# agentsh Security Analysis

**Repository:** https://github.com/canyonroad/agentsh
**Commit:** 6491d2e0e5b48e977079e440b548f0ec44d06487
**Point-in-time:** 2026-03-31
**Language:** Go
**Category:** Security-focused

## 1. Overview

agentsh is an execution-layer security (ELS) gateway for AI agents. It interposes between an AI agent (or any tool-use framework) and the host system, intercepting file, network, process, signal, and environment operations at runtime, enforcing declarative YAML policies, and emitting structured audit events. It is not a container or VM -- it is a policy-enforcement and audit layer that can run inside or alongside containers.

### High-Level Architecture

The system is composed of several major subsystems:

- **Server daemon** (`internal/api/`, `internal/server/`): An HTTP/gRPC server that manages sessions and dispatches command execution. Each session is bound to a workspace and a named policy.
- **Policy engine** (`internal/policy/`): A first-match-wins rule evaluator supporting file, network, command, environment, Unix socket, Windows registry, signal, DNS redirect, and connect redirect rules. Rules are compiled into glob/regex matchers at load time.
- **FUSE filesystem** (`internal/fsmonitor/`): A loopback FUSE mount (via `go-fuse/v2`) over the workspace that intercepts every file operation (open, read, write, create, delete, rename, chmod, etc.) and checks policy before allowing the underlying syscall.
- **Network monitor** (`internal/netmonitor/`): eBPF-based cgroup network filtering on Linux; pf-based on macOS; WinDivert/WFP on Windows. Filters DNS and TCP connections against network policy rules.
- **Seccomp/ptrace enforcement** (`internal/seccomp/`, `internal/ptrace/`, `cmd/agentsh-unixwrap/`): On Linux, a `seccomp-bpf` user-notify filter traps syscalls (Unix socket, signal, file, execve) and a ptrace tracer intercepts execve/execveat for process-tree-wide enforcement.
- **Landlock** (`internal/landlock/`): Linux Landlock LSM integration providing kernel-enforced filesystem access restrictions as defense-in-depth.
- **LLM proxy** (`internal/llmproxy/`): An embedded HTTP proxy that intercepts all LLM API requests, applies DLP (Data Loss Prevention) redaction, logs usage/tokens, and enforces MCP tool policies.
- **MCP inspection** (`internal/mcpinspect/`): Tool whitelisting, version pinning ("rug pull" detection), cross-server exfiltration detection, rate limiting, and suspicious pattern detection for Model Context Protocol tool calls.
- **Audit system** (`internal/audit/`): HMAC-chained integrity logging with external KMS support (AWS KMS, Azure Key Vault, HashiCorp Vault, GCP Cloud KMS).
- **Policy signing** (`internal/policy/signing/`): Ed25519 policy signatures with trust store verification.
- **Shell shim** (`cmd/agentsh-shell-shim/`): Replaces `/bin/sh` and `/bin/bash` so all shell invocations inside a container route through agentsh.
- **Approval workflows** (`internal/approvals/`): Human-in-the-loop approval for risky operations via local TTY, TOTP, WebAuthn, or REST API.
- **Platform abstraction** (`internal/platform/`): Cross-platform support for Linux, macOS (FUSE-T, ESF+NE, sandbox-exec), and Windows (minifilter, WinFsp, AppContainer, WinDivert).

The codebase is approximately 240,000 lines of Go across 1,089 source files (493 test files, 596 non-test).

## 2. Security Architecture

### 2.1 Design Philosophy

agentsh's design philosophy centers on **runtime interposition with defense in depth**. Rather than relying on a single enforcement mechanism, it layers multiple independent enforcement points:

1. **Policy check before execution** (command rules evaluated pre-exec)
2. **Kernel-level syscall interception** (seccomp user-notify, ptrace, Landlock)
3. **Filesystem interposition** (FUSE loopback mount with per-operation policy checks)
4. **Network filtering** (eBPF cgroup attachment before process resumes)
5. **LLM request interception** (embedded proxy with DLP)

The stated goal is to govern "semi-trusted AI agents" -- agents that may attempt policy violations but are not actively adversarial at the kernel level. The system explicitly acknowledges it does not protect against kernel exploits, root-level attacks, or hardware side-channels.

A distinctive design choice is the **redirect** decision type: rather than just allow/deny, agentsh can transparently redirect commands, file writes, and network connections, "steering" the agent toward approved paths without producing an error. This reduces wasted agent retries.

### 2.2 Core Security Primitives

- **FUSE filesystem interception**: Every file operation on the workspace is intercepted at the VFS layer (`internal/fsmonitor/fuse.go`). The FUSE node checks policy before calling through to the underlying loopback filesystem. Symlink escape is prevented by `filepath.EvalSymlinks` + boundary checks (`internal/fsmonitor/path.go`).

- **Seccomp user-notify**: On Linux, `SECCOMP_RET_USER_NOTIF` traps Unix socket, signal, execve, and file-related syscalls. The agentsh daemon receives each trapped syscall, evaluates policy, and either allows or denies it (`cmd/agentsh-unixwrap/`).

- **Ptrace-based execve interception**: Uses `PTRACE_SEIZE` to attach to the process tree. Intercepts `execve` and `execveat` at entry, reads filename/argv from `/proc/<tid>/mem`, evaluates policy, and denies by setting the syscall number to -1 (`internal/ptrace/`). Auto-attaches to all descendants via `PTRACE_O_TRACECLONE`/`TRACEFORK`/`TRACEVFORK`.

- **Landlock LSM**: Kernel-enforced filesystem access restrictions using Linux Landlock ABI v1-v4. Derives allowed paths from the loaded policy (`internal/landlock/ruleset.go`). Provides a backstop even if FUSE is bypassed.

- **eBPF network filtering**: Attaches to the process cgroup before the process is resumed. Filters by domain, CIDR, and port. Race condition mitigated by starting processes in ptrace-stopped state (`SECURITY.md` lines 126-127).

- **Policy engine**: First-match-wins evaluation with compiled glob patterns (via `gobwas/glob`) and regex-based args matching. Supports variable expansion (`${PROJECT_ROOT}`, `${HOME}`), per-command environment allow/deny lists, and transparent command unwrapping (`internal/policy/engine.go`).

- **HMAC integrity chain**: Audit entries form a tamper-evident chain where each entry's hash depends on the previous entry's hash, using HMAC-SHA256 or HMAC-SHA512 (`internal/audit/integrity.go`). Key material can be sourced from external KMS.

- **Ed25519 policy signatures**: Policies can be signed with Ed25519 keys and verified against a trust store before loading (`internal/policy/signing/`).

- **DLP redaction**: Regex-based PII detection (email, phone, credit card, SSN, API keys) with configurable redaction or tokenization before LLM requests leave the proxy (`internal/llmproxy/dlp.go`).

### 2.3 Threat Model

**Explicitly addressed threats:**
- Arbitrary file access outside the workspace (FUSE + Landlock + policy)
- Credential theft via files (deny rules for `.ssh/`, `.aws/`, `.env`)
- Credential theft via environment variables (deny list for secrets + `LD_PRELOAD`/`DYLD_INSERT_LIBRARIES`/etc.)
- Unauthorized network access (eBPF + policy-based filtering, CIDR blocks for metadata services)
- Dangerous command execution (command allowlists, args pattern matching, seccomp/ptrace enforcement)
- Resource exhaustion (cgroups v2 for memory, CPU, PIDs)
- Destructive operations (approval workflows, soft-delete, checkpoint/rollback)
- PII leakage to LLM providers (embedded proxy with DLP)
- MCP tool abuse (tool whitelisting, version pinning, cross-server exfiltration detection)
- Signal-based process attacks (signal interception via seccomp on Linux)
- Audit tampering (HMAC integrity chains, external KMS)
- Policy tampering (Ed25519 policy signatures)

**Explicitly out of scope:**
- Kernel exploits (runs in userspace)
- Root-level attacks (assumes unprivileged user)
- Hardware side-channels (Spectre/Meltdown)
- Compromised agentsh binary
- Pre-existing malware
- Social engineering (content the agent outputs)
- Full denial of service to host (resource limits help but do not fully prevent)

**Known limitations documented:**
- TOCTOU between FUSE open and subsequent reads/writes
- DNS rebinding (recommends CIDR rules for critical blocks)
- Process tree escape window between fork and ptrace auto-attach
- Transparent command unwrap heuristic edge cases
- Approval bypass via repeated retries (fatigue attack)

## 3. Mapping to Defense Taxonomy

### 3.1 Secure Architectures by Construction

agentsh does not implement a CaMeL-style information flow control architecture or dual-LLM pattern. However, it does implement a clear **control plane / data plane separation**:

- The **control plane** (agentsh daemon, policy engine, approval manager) runs with full host access and is trusted.
- The **data plane** (the agent's commands, running inside FUSE mount with seccomp/ptrace/Landlock restrictions) is untrusted and governed by policy.

The `ContextEngine` (`internal/policy/context_eval.go`) provides **taint-aware policy evaluation** using process ancestry chains and identity matching. This allows different policies to apply based on which process in the ancestry chain initiated the operation -- a form of context-sensitive access control.

The architecture is not "secure by construction" in the formal IFC sense, but it provides meaningful separation between the trusted orchestration layer and the untrusted execution environment.

### 3.2 Access Control and Governance

This is agentsh's strongest area. Specific mechanisms:

- **Tool-level permissions**: Command rules with basename, full-path, and glob matching plus regex-based args patterns (`internal/policy/engine.go` lines 184-236). Commands like `rm -rf` can be denied while allowing `rm` for single files.
- **Least privilege**: Default-deny for files, network, and commands. The default policy (`configs/policies/default.yaml`) explicitly denies all write operations outside the workspace and all network connections not on the allowlist.
- **Policy DSL**: YAML-based policy language supporting file rules, network rules, command rules, Unix socket rules, registry rules (Windows), signal rules, DNS redirect rules, and connect redirect rules (`internal/policy/model.go`).
- **Per-operation decisions**: `allow`, `deny`, `approve` (human-in-the-loop), `redirect`, `audit`, `soft_delete`.
- **Variable expansion**: `${PROJECT_ROOT}`, `${HOME}`, `${GIT_ROOT}` in policy paths (`internal/policy/vars.go`).
- **Policy allowlisting**: Server config restricts which policies can be selected; env-based selection validated against allowlist (`configs/server-config.yaml`).
- **Policy signing**: Ed25519 signatures with trust store verification (`internal/policy/signing/`).
- **Policy integrity manifest**: Optional SHA256 manifest for policy file verification at load time.
- **Role-based API access**: Agent, approver, and admin roles with API key and OIDC authentication (`internal/auth/`).
- **MCP access control**: Tool whitelisting (allowlist/denylist), per-server rate limits, version pinning (`internal/mcpinspect/policy.go`).
- **Environment variable control**: Per-command `env_allow`/`env_deny` with max_bytes/max_keys limits. Built-in deny list for secrets and code injection vectors like `LD_PRELOAD`, `DYLD_INSERT_LIBRARIES`, `PYTHONPATH`, `NODE_OPTIONS`, `BASH_ENV` (`internal/policy/env_policy.go`).
- **Parent-conditional policies**: Process context rules that vary policy based on the calling process identity and ancestry chain (`internal/policy/context_eval.go`).

### 3.3 Runtime Verification and Policy Enforcement

- **Pre-execution policy check**: Every command is evaluated against command rules before execution (`internal/api/core.go`). Denied commands never start.
- **Runtime FUSE enforcement**: Every file operation is checked at the FUSE layer during execution, not just at command start (`internal/fsmonitor/fuse.go`).
- **Kernel-level enforcement**: Seccomp user-notify, ptrace execve interception, and Landlock provide kernel-level backstops that the agent process cannot bypass without kernel exploits (`internal/ptrace/`, `internal/seccomp/`, `internal/landlock/`).
- **Process tree tracking**: All child processes are tracked and governed. Ptrace auto-attaches to fork/clone/vfork children. eBPF attaches to the process cgroup.
- **Approval workflows**: Risky operations can require human approval via TTY, TOTP, WebAuthn, or REST API. Timeout defaults to deny (`internal/approvals/`).
- **Checkpoint/rollback**: Workspace snapshots before destructive operations with SHA-256 verification on rollback (`SECURITY.md` lines 256-322).
- **Transparent command unwrapping**: Wrapper commands (`env`, `sudo`, `nice`, `ld-linux`) are unwrapped to find the real payload; both wrapper and payload are evaluated with the most restrictive decision winning (`SECURITY.md` lines 137-138).
- **Fail-closed ptrace**: When the ptrace tracer exits unexpectedly, `ptraceFailed` is set to true and subsequent command execution is blocked (`internal/api/app.go` line 75).

### 3.4 Detection, Filtering, and Firewalls

- **DLP/PII filtering**: Regex-based detection of email, phone, credit card, SSN, and API keys in LLM request bodies. Matches are redacted or tokenized before forwarding (`internal/llmproxy/dlp.go`). Custom patterns configurable.
- **MCP suspicious pattern detection**: The `Detector` in `internal/mcpinspect/detector.go` scans MCP tool definitions for suspicious patterns (prompt injection indicators, data exfiltration patterns, etc.) using compiled regex patterns.
- **Cross-server exfiltration detection**: The `SessionAnalyzer` (`internal/mcpinspect/session_analyzer.go`) detects multi-step attack patterns across MCP servers: shadow tool replacement, burst activity, read-then-send sequences, and cross-server data flows. Uses a bounded sliding window (max 1000 entries) to prevent memory exhaustion.
- **Threat feed integration**: Domain-level threat feed lookups during network policy evaluation. Can block or audit connections to known-malicious domains (`internal/threatfeed/`, `internal/policy/engine.go` lines 456-469).
- **MCP version pinning**: Detects tool definition changes ("rug pull") by hashing tool schemas and comparing against pinned versions (`internal/mcpinspect/pins.go`).
- **Package install checking**: Optional verification of package installs against rules (`internal/pkgcheck/`).
- **No prompt injection classifier**: agentsh does not include a dedicated prompt injection detection model or classifier. It operates at the execution layer, not the prompt layer.

### 3.5 Model-Level Hardening

Not addressed. agentsh operates below the model layer. It does not modify LLM behavior through instruction hierarchy, preference optimization, or representation editing. It is model-agnostic -- it intercepts actions the agent takes, regardless of what model produced those actions.

### 3.6 Boundary Marking and Cryptographic Provenance

- **Ed25519 policy signatures**: Policies can be cryptographically signed and verified against a trust store (`internal/policy/signing/sign.go`, `verify.go`). The `SigFile` format includes version, algorithm, key ID, signer identity, timestamp, and signature. Key IDs are SHA-256 hashes of Ed25519 public keys.
- **HMAC audit integrity chains**: Each audit entry's hash depends on the previous entry, forming a tamper-evident chain. Supports HMAC-SHA256 and HMAC-SHA512 with minimum 32-byte keys (`internal/audit/integrity.go`).
- **External KMS for audit keys**: HMAC keys can be sourced from AWS KMS (envelope encryption), Azure Key Vault, HashiCorp Vault, or GCP Cloud KMS (`internal/audit/kms/`).
- **SHA-256 checkpoint verification**: Workspace checkpoint restores are verified with SHA-256 hashes.
- **No signed prompts or cryptographic delimiters**: agentsh does not implement signed prompt boundaries or hash-based authentication for agent communications. The trust boundary is at the policy/config layer (files not writable by the agent).

### 3.7 Formal Methods and Semantics

Not addressed. There is no formal verification, no type system for information flow control, no IFC proofs. The policy engine uses first-match-wins evaluation with compiled patterns, which is straightforward to reason about but not formally verified.

The `ContextEngine` with taint-aware ancestry tracking (`internal/policy/context_eval.go`) approaches information flow control concepts but is implemented as a runtime heuristic, not a formally verified system.

## 4. Source Code Analysis

### 4.1 Security-Critical Code Paths

**Command execution flow** (`internal/api/core.go` -> `internal/api/exec.go`):

1. **API request received**: The `App.handleExec` method receives an `ExecRequest`.
2. **Auth check**: API key or OIDC token validated, role checked.
3. **Command policy check**: `Engine.CheckCommand()` evaluates the command+args against command rules. If denied, returns immediately.
4. **Environment building**: `buildPolicyEnv()` applies env allow/deny rules, limits, and operator injections (`exec.go` lines 167-212).
5. **Seccomp wrapper setup**: `setupSeccompWrapper()` configures the `agentsh-unixwrap` wrapper with seccomp-bpf, Landlock, signal filtering, and file monitoring (`core.go` lines 107-313).
6. **Process start**: Command starts either stopped (for cgroup/eBPF attachment) or under ptrace.
7. **Hook execution**: eBPF/cgroup hooks run before the process is resumed (`exec.go` lines 285-347).
8. **Ptrace attachment**: In hybrid mode, ptrace attaches after wrapper completes seccomp setup, then sends GO byte (`exec.go` lines 289-340).
9. **Runtime enforcement**: During execution, FUSE intercepts file ops, seccomp intercepts syscalls, eBPF filters network, ptrace intercepts execve.
10. **Audit emission**: Events are emitted to the store and broker throughout.

**FUSE file operation path** (`internal/fsmonitor/fuse.go`):

Each FUSE node method (Open, Create, Unlink, Mkdir, Rename, etc.) follows the same pattern:
1. Compute virtual path
2. Call `n.check()` -> `Engine.CheckFile()` for policy evaluation
3. If decision is `approve`, call `n.maybeApprove()` for human approval
4. If denied, return `syscall.EACCES`
5. If allowed, call the underlying `LoopbackNode` method
6. Emit audit event

**Symlink escape prevention** (`internal/fsmonitor/path.go` lines 16-64):
- Virtual path validated to be under virtualRoot
- Real path computed with `filepath.EvalSymlinks` on root
- `filepath.Clean` applied to prevent `..` escape
- Both parent directory and final path checked against root boundary
- Separate handling for `mustExist` (full resolution) vs new paths (parent resolution only)

### 4.2 Input Validation and Sanitization

- **Policy paths**: Glob patterns compiled at engine construction time with error checking (`internal/policy/engine.go` lines 134-316). Invalid patterns cause engine construction to fail.
- **CIDR parsing**: Network CIDRs parsed with `net.ParseCIDR` at compile time (`engine.go` lines 174-180).
- **Args patterns**: Compiled as `regexp.Regexp` at engine construction (`engine.go` lines 229-235).
- **Environment variables**: Filtered through allow/deny lists with max_bytes and max_keys limits. Built-in deny list for injection vectors (`internal/policy/env_policy.go`).
- **Path canonicalization**: `filepath.EvalSymlinks` resolves symlinks before policy evaluation for both file and command paths. For `execveat` calls, relative paths and fd-based paths are resolved to absolute paths (`SECURITY.md` lines 136-137).
- **Command unwrapping**: Wrapper commands (env, sudo, nice, ld-linux) are automatically unwrapped. Both wrapper and inner command are evaluated; the most restrictive decision wins (`SECURITY.md` lines 137-138).
- **DLP patterns**: Regex-based with built-in patterns for common PII types. Custom patterns configurable via YAML (`internal/llmproxy/dlp.go` lines 71-86).

### 4.3 Tool Execution and Sandboxing

**Linux (full enforcement):**
- FUSE filesystem mount for file interception
- Seccomp user-notify for syscall trapping (Unix sockets, signals, execve, file ops)
- Ptrace for execve/execveat interception with auto-attachment to all descendants
- Landlock LSM for kernel-enforced filesystem restrictions
- eBPF for cgroup-based network filtering
- cgroups v2 for resource limits (memory, CPU, PIDs)
- Process started in stopped state; all enforcement attached before resumption

**macOS (tiered enforcement):**
- FUSE-T for file interception (requires CGO)
- ESF (Endpoint Security Framework) for file/process events (requires Apple entitlements)
- Network Extension for DNS/network policy (standard capability)
- sandbox-exec with SBPL profiles for process sandboxing (deprecated but functional)
- XPC/Mach IPC control for sandboxed processes
- No seccomp, no cgroups, no namespaces

**Windows (native enforcement):**
- Minifilter driver for file create/write/delete/rename
- WinFsp (FUSE-style) as alternative filesystem interception
- WinDivert for TCP/DNS interception
- WFP (Windows Filtering Platform) as network fallback
- CmRegisterCallbackEx for registry monitoring
- AppContainer for process isolation
- Job Objects for resource limits

### 4.4 Memory and State Management

- **Session state**: Sessions are managed by `session.Manager` (`internal/session/`), each with a unique ID, workspace path, policy engine reference, process registry, command history, and optional checkpoint store.
- **Event storage**: Events stored in SQLite (`internal/store/`) with JSONL audit logs. LLM proxy logs stored separately per session.
- **Retention**: Configurable retention policies for audit logs, LLM logs, and checkpoints. Automatic cleanup of old sessions (`internal/llmproxy/retention.go`).
- **MCP session window**: Bounded to 1000 entries maximum (`internal/mcpinspect/session_analyzer.go` line 13) to prevent memory exhaustion.
- **Token store for DLP**: In-memory forward/reverse mapping for tokenized PII (`internal/llmproxy/dlp.go` lines 28-68).
- **Policy caching**: Compiled policies cached in the engine; no re-compilation per operation.

### 4.5 Authentication and Authorization

- **API key auth** (`internal/auth/apikey.go`): Static keys loaded from a YAML file. Each key maps to a role (agent, approver, admin). Simple header-based authentication (`X-API-Key`).
- **OIDC auth** (`internal/auth/oidc.go`): JWT validation with JWKS auto-discovery. Group-based role mapping. Token caching with secure hashing.
- **WebAuthn** (`internal/auth/webauthn.go`): Hardware security key (YubiKey) support for approval workflows. Provides cryptographic proof of human presence.
- **Role separation**: Agent role can execute commands but cannot approve. Approver role can resolve approval requests. Admin role has full access.
- **Approval credential separation**: Agents cannot self-approve; approval requires a different authentication method/credential.

## 5. Production Readiness

### 5.1 Maturity Level

The codebase shows significant engineering investment. Key indicators:

- **Multi-platform support**: Dedicated implementations for Linux, macOS, and Windows, each with platform-appropriate enforcement mechanisms.
- **Multiple enforcement layers**: FUSE + seccomp + ptrace + Landlock + eBPF on Linux; not just a single mechanism.
- **Error handling**: Consistent error propagation. Fail-closed on ptrace failure (`ptraceFailed` atomic flag blocks execution).
- **Configuration depth**: Extensive YAML configuration covering every subsystem with sensible defaults.
- **Versioned policy format**: `version: 1` field for future schema evolution.
- **GoReleaser config** (`.goreleaser.yml`): Automated release packaging for multiple platforms.
- **CI/CD** (`.github/workflows/ci.yml`): Tests on Linux, macOS, and Windows. Cross-compilation verification.

However, the repository URL in README references `erans/agentsh` while the module path is `github.com/agentsh/agentsh`, and the documented repo reference on the README title page is `canyonroad/agentsh` -- this inconsistency suggests the project may be in early public release or transitioning ownership.

### 5.2 Test Coverage

**Quantitative:**
- 493 test files out of 1,089 total Go files (45% of files are tests)
- Approximately 110,000 lines of test code
- Tests span all major subsystems: policy engine, FUSE operations, DLP, LLM proxy, MCP inspection, audit integrity, seccomp, ptrace, landlock, auth, signal handling

**Notable test suites:**
- `internal/policy/agent_policies_test.go` (29,425 lines): Extensive policy evaluation tests
- `internal/llmproxy/proxy_test.go` (62,104 lines): Comprehensive proxy testing
- `internal/llmproxy/mcp_intercept_test.go` (58,535 lines): MCP interception testing
- `internal/llmproxy/sse_intercept_test.go` (72,468 lines): SSE streaming interception
- `internal/mcpinspect/session_analyzer_test.go` (23,260 lines): Cross-server detection testing
- `internal/policy/redirect_test.go` (28,368 lines): Redirect policy testing

**Security-specific tests:**
- Symlink escape tests (`internal/fsmonitor/path_test.go`)
- Cross-mount FUSE tests (`internal/fsmonitor/fuse_cross_mount_test.go`)
- Policy variable expansion tests (`internal/policy/engine_vars_test.go`)
- Threat feed tests (`internal/policy/engine_threat_test.go`)
- HMAC integrity chain tests (`internal/audit/integrity_test.go`, `crypto_test.go`)
- Policy signing/verification tests (`internal/policy/signing/*_test.go`)
- DLP pattern tests (`internal/llmproxy/dlp_test.go`)
- Landlock integration tests (`internal/landlock/integration_test.go`)
- Seccomp integration tests (`internal/seccomp/integration_test.go`)
- Ptrace benchmark and correctness tests (`internal/ptrace/benchmark_test.go`)

**Docker-based integration tests:** Multiple Dockerfiles for platform-specific testing:
- `Dockerfile.test` (Debian), `Dockerfile.test.alpine`, `Dockerfile.test.arch`, `Dockerfile.test.rpm`, `Dockerfile.test.ubuntu`
- `Dockerfile.policy-test`, `Dockerfile.dns-test`, `Dockerfile.ptrace-test`
- `test_policy.py`: Python-based policy integration tests

### 5.3 Documentation Quality

Documentation is extensive:

- **README.md** (680 lines): Comprehensive overview with quick start, policy model, examples, and feature documentation.
- **SECURITY.md** (999 lines): Detailed threat model, security mechanisms, platform-specific limitations, known limitations, and operator checklist.
- **docs/** directory: 15+ documentation files covering approval auth, CI/CD integration, eBPF, cross-platform support, MCP security, LLM proxy, macOS builds, and platform comparison.
- **docs/plans/** directory: 70+ design documents and implementation plans spanning December 2025 to February 2026.
- **Inline comments**: Security-relevant code paths have explanatory comments (e.g., race condition mitigations, symlink escape prevention, trust boundary descriptions).
- **Policy examples**: 15+ policy files in `configs/policies/` covering dev-safe, CI-strict, agent-sandbox, observe-only, and platform-specific variants.

### 5.4 Deployment Model

- **Standalone daemon**: `agentsh server` runs as a daemon with HTTP/gRPC API.
- **Autostart**: First `agentsh exec` auto-launches the server if not running.
- **Container sidecar**: Recommended pattern is agentsh as a sidecar with shared workspace volume.
- **Shell shim**: `agentsh-shell-shim` replaces `/bin/sh`/`/bin/bash` inside containers for transparent interposition.
- **Linux packaging**: `.deb`, `.rpm`, `.apk` packages via GoReleaser.
- **Docker integration**: `Dockerfile.example` demonstrates container deployment.
- **AWS Fargate**: `Dockerfile.fargate-workload` and specific ptrace fallback for restricted environments.
- **Kubernetes**: `pkg/k8s/` package for Kubernetes integration.

## 6. Strengths

1. **Defense in depth on Linux**: The layering of FUSE + seccomp + ptrace + Landlock + eBPF + cgroups provides multiple independent enforcement points. If one layer is bypassed (e.g., FUSE via direct syscall), Landlock and seccomp provide backstops.

2. **MCP security is notably comprehensive**: Tool whitelisting, version pinning (rug-pull detection), cross-server exfiltration detection with pattern analysis (shadow tool, burst, read-then-send), rate limiting, and suspicious pattern scanning. This addresses a real emerging threat vector that most frameworks ignore entirely.

3. **Redirect as a first-class decision type**: The ability to redirect commands, file writes, and network connections rather than just denying them is a pragmatic innovation for agent workflows. It reduces error loops and keeps agents productive within policy bounds.

4. **LLM proxy with DLP**: Intercepting all LLM API traffic for PII redaction, usage tracking, and audit is a meaningful production concern. The proxy is transparent to the agent via environment variable overrides.

5. **Cryptographic audit integrity**: HMAC-chained audit logs with external KMS support provide tamper-evident logging suitable for compliance and forensics. Ed25519 policy signatures prevent policy tampering.

6. **Process tree tracking**: Auto-attachment to all descendant processes via ptrace and cgroup inheritance means subprocess trees cannot escape governance, which is critical for real-world agent workflows that spawn build tools, package managers, etc.

7. **Thoughtful known-limitations documentation**: The SECURITY.md honestly documents TOCTOU windows, DNS rebinding, process tree race conditions, and approval fatigue, with mitigations for each.

## 7. Gaps and Weaknesses

1. **No prompt injection detection** (Category 3.4): agentsh operates at the execution layer, not the prompt layer. It cannot detect or prevent prompt injection attacks that manipulate the LLM's intent. If a prompt injection causes the agent to request allowed actions with malicious intent (e.g., exfiltrating data through an allowed API endpoint in a legitimate-looking request), agentsh will allow it.

2. **No model-level hardening** (Category 3.5): There is no instruction hierarchy enforcement, no preference optimization for safety, no representation-level interventions. agentsh is entirely model-agnostic, which is both a strength (works with any model) and a gap (cannot influence model behavior).

3. **No formal verification** (Category 3.7): The policy engine and enforcement mechanisms are not formally verified. The first-match-wins evaluation is simple enough to reason about informally, but complex policy configurations could have unexpected interactions (e.g., ordering mistakes causing overly permissive results).

4. **macOS enforcement significantly weaker**: As documented, macOS without Apple ESF entitlements provides at most 75% of Linux's security score. The pf-based network filtering is loopback-only, sandbox-exec is deprecated, and there are no resource limits, no seccomp, no namespaces. Organizations requiring strong enforcement on macOS face a real gap.

5. **DLP is regex-based only** (Category 3.4): The DLP system uses regex patterns for PII detection, which will miss obfuscated, encoded, or semantically-equivalent sensitive data. There is no ML-based classification or context-aware detection.

6. **Approval fatigue attack surface**: The SECURITY.md acknowledges that a patient attacker could retry operations until a human mistakenly approves. The mitigation is audit logging, but there is no adaptive rate limiting on approval requests or escalating friction for repeated denials of the same operation pattern.

7. **FUSE TOCTOU window**: Between FUSE open and subsequent reads/writes, the underlying file could change via hard links from outside the sandbox. While mitigated by the fact that the agent cannot create hard links outside `/workspace`, this is an inherent limitation of userspace filesystem interception.

8. **No information flow tracking between tool calls** (Category 3.1): While the MCP session analyzer detects cross-server patterns, there is no general taint tracking for data flowing through the agent. Data read from a sensitive source (within allowed policy) can be exfiltrated through allowed network endpoints without detection, as long as the individual operations are each permitted.

## 8. Key Findings

- **agentsh is the most comprehensive execution-layer security framework examined in this survey.** With 240K lines of Go, 493 test files, and implementations spanning Linux (FUSE + seccomp + ptrace + Landlock + eBPF), macOS (FUSE-T, ESF, sandbox-exec), and Windows (minifilter, AppContainer, WinDivert), it provides unusually deep and layered enforcement.

- **MCP security is a standout feature.** The combination of tool whitelisting, version pinning, cross-server exfiltration detection, and rate limiting addresses real emerging attack vectors (tool shadowing, rug pulls, data exfiltration via MCP) that virtually no other framework addresses.

- **The "redirect" decision type is a pragmatic innovation.** Rather than just blocking, agentsh can steer agents toward approved paths, reducing error loops. This reflects real operational experience with AI agent workflows.

- **The primary limitation is that agentsh operates below the intent layer.** It cannot distinguish between a legitimate agent request and a prompt-injection-induced request if both result in the same system-level operations. Defense against prompt injection must come from layers above agentsh.

- **Cryptographic provenance for audit and policy is well-implemented.** HMAC integrity chains with external KMS for audit logs and Ed25519 policy signatures provide meaningful tamper resistance suitable for compliance use cases. This is more mature than most frameworks' approach to audit integrity.
