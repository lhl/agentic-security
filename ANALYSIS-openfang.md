# openfang Security Analysis

**Repository:** https://github.com/RightNow-AI/openfang
**Commit:** a78299ed3d59c45f694365334f8d69811c65c522
**Point-in-time:** 2026-03-31
**Language:** Rust
**Category:** Security-focused

## 1. Overview

OpenFang is an open-source "Agent Operating System" written in Rust. It is not merely a chatbot framework; it provides a full daemon-based runtime for autonomous agents ("Hands") that can run on schedules, interact with 40+ messaging platforms, execute tools, and coordinate via a peer-to-peer wire protocol.

### Architecture

The system compiles to a single ~32MB binary organized as a Cargo workspace of 14 crates:

| Crate | Role |
|-------|------|
| `openfang-kernel` | Orchestration, workflows, RBAC, scheduling, budget tracking, agent approval |
| `openfang-runtime` | Agent loop, 3 LLM drivers (Anthropic/Gemini/OpenAI-compat), 53+ tools, WASM sandbox, MCP, A2A |
| `openfang-api` | 140+ REST/WS/SSE endpoints, OpenAI-compatible API, web dashboard |
| `openfang-channels` | 40 messaging adapters (Telegram, Discord, Slack, WhatsApp, etc.) |
| `openfang-memory` | SQLite persistence, vector embeddings, session compaction |
| `openfang-types` | Core types, taint tracking, Ed25519 manifest signing, capability system |
| `openfang-skills` | 60 bundled skills, SKILL.md parser, marketplace integration, prompt injection scanner |
| `openfang-hands` | 7 autonomous Hands (Researcher, Lead, Collector, Predictor, etc.) |
| `openfang-extensions` | 25 MCP templates, AES-256-GCM credential vault, OAuth2 PKCE |
| `openfang-wire` | OFP peer-to-peer protocol with HMAC-SHA256 mutual authentication |
| `openfang-cli` | CLI with daemon management, TUI dashboard, MCP server mode |
| `openfang-desktop` | Tauri 2.0 native app |
| `openfang-migrate` | OpenClaw/LangChain/AutoGPT migration engine |
| `xtask` | Build automation |

The system reports ~177K lines of Rust code across the workspace, with 1,767+ tests (including ~4K lines in dedicated test files in `/tests/` directories, plus extensive in-module `#[cfg(test)]` blocks).

### Core Execution Flow

1. User or scheduled trigger sends a message to an agent
2. Kernel identifies the agent, performs RBAC check, and routes to the agent loop
3. Agent loop (`agent_loop.rs`) retrieves memories, builds prompt, calls LLM driver
4. LLM response may include tool calls; each tool call is checked against the tool policy and loop guard
5. Tools requiring approval go through the approval manager
6. Tool execution happens either natively (file I/O, web fetch, shell) or via WASM sandbox or MCP
7. Results feed back to the LLM for the next iteration (up to 50 iterations per loop)
8. All actions are recorded to the Merkle hash-chain audit trail

## 2. Security Architecture

### 2.1 Design Philosophy

OpenFang's security philosophy is explicitly **defense-in-depth**: 16 independent security systems form overlapping layers so that failure in any single layer is caught by others. The README and docs consistently emphasize this.

Key design principles observed in the code:

- **Deny by default**: The WASM sandbox, capability system, and tool policy all default to denying access unless explicitly granted.
- **Least privilege**: Agents declare required capabilities in manifests; the kernel enforces them. Child agents cannot exceed parent capabilities.
- **Independent layers**: Each security system (taint tracking, capability checks, SSRF protection, path traversal prevention) operates independently. A bypass of one layer does not compromise the others.
- **Cryptographic integrity**: The audit trail uses Merkle hash chains, agent manifests use Ed25519 signing, secrets use AES-256-GCM with Argon2 KDF, and the wire protocol uses HMAC-SHA256 with constant-time comparison.

### 2.2 Core Security Primitives

1. **Capability-based access control** (`openfang-types/src/capability.rs`, `openfang-kernel/src/capabilities.rs`): Fine-grained, typed `Capability` enum covering file I/O, network, tools, LLM, agent interaction, memory, shell, wire protocol, and economic operations. Pattern matching supports glob wildcards. Capability inheritance validation prevents privilege escalation during agent spawning.

2. **WASM dual-metered sandbox** (`openfang-runtime/src/sandbox.rs`): Wasmtime-based sandbox with fuel metering (deterministic instruction counting) and epoch interruption (wall-clock timeout via watchdog thread). Deny-by-default capability checks on every host call. No WASI -- no implicit filesystem or network access.

3. **Information flow taint tracking** (`openfang-types/src/taint.rs`): Lattice-based taint propagation with five labels (ExternalNetwork, UserInput, Pii, Secret, UntrustedAgent). Predefined sinks (shell_exec, net_fetch, agent_message) block specific label types. Explicit declassification required.

4. **Merkle hash-chain audit trail** (`openfang-runtime/src/audit.rs`): Append-only log where each entry includes SHA-256(content + prev_hash). SQLite-backed persistence. Integrity verification on boot and on-demand.

5. **Ed25519 manifest signing** (`openfang-types/src/manifest_signing.rs`): Cryptographic signing of agent TOML manifests via `ed25519-dalek`. Two-phase verification: hash check + signature check.

6. **SSRF protection** (`openfang-runtime/src/host_functions.rs`): Scheme validation (http/https only), hostname blocklist (localhost, cloud metadata endpoints), DNS resolution check (all resolved IPs checked against private ranges to defeat DNS rebinding).

7. **Secret zeroization**: `Zeroizing<String>` from the `zeroize` crate used on all API key fields across LLM drivers, channel adapters, embedding client, and web search modules.

8. **AES-256-GCM credential vault** (`openfang-extensions/src/vault.rs`): Encrypted at-rest storage with Argon2id KDF, OS keyring or environment variable master key, zeroizing containers throughout.

9. **HMAC-SHA256 mutual authentication** (`openfang-wire/src/peer.rs`): Nonce-based mutual authentication for the OFP wire protocol with constant-time comparison, 5-minute replay window nonce tracking, and mandatory pre-shared secret.

10. **Shell metacharacter blocking** (`openfang-runtime/src/subprocess_sandbox.rs`): Comprehensive check for backticks, `$()`, `${}`, pipes, semicolons, redirects, braces, newlines, null bytes, and ampersands before any allowlist-mode command execution.

### 2.3 Threat Model

**Explicitly addressed threats** (from `docs/security.md` and `SECURITY.md`):

- Unauthorized actions by agents (capability system)
- Privilege escalation via child agents (capability inheritance)
- CPU DoS via runaway WASM (dual metering)
- Tampered audit logs (Merkle chain)
- Prompt injection via external data (taint tracking)
- Data exfiltration via LLM tool use (taint sinks)
- Supply chain attacks via tampered manifests (Ed25519 signing)
- SSRF to cloud metadata (multi-layer IP blocking)
- API key recovery from memory dumps (zeroization)
- Unauthorized peer connections (HMAC mutual auth)
- XSS/clickjacking (security headers + CSP)
- API abuse/DoS (GCRA rate limiting)
- Directory traversal (canonicalization + `..` component rejection)
- Secret leakage to child processes (env_clear + allowlist)
- Malicious skills from marketplace (prompt injection scanner + SHA256 checksum)
- Agent stuck in tool loops (loop guard with circuit breaker)
- Corrupted LLM session history (7-phase session repair)
- Shell injection (Command::new without shell, metacharacter blocking)
- DNS rebinding for SSRF bypass (resolved IP check)
- Timing attacks on auth (constant-time comparison)

**In-scope for vulnerability reports** (`SECURITY.md`): Auth bypass, RCE, path traversal, SSRF, privilege escalation, information disclosure, resource exhaustion DoS, supply chain attacks, WASM sandbox escapes.

**Implicitly out of scope or not addressed**:
- Adversarial model inputs (model-level attacks, not just prompt injection)
- Multi-tenant isolation (the system is single-owner with RBAC, not multi-tenant)
- Side-channel attacks beyond timing (e.g., power analysis, cache timing)
- Physical access scenarios

## 3. Mapping to Defense Taxonomy

### 3.1 Secure Architectures by Construction

**Partially addressed.** OpenFang has a clear architectural separation between the kernel (trusted orchestration layer) and the runtime (less-trusted agent execution layer), with the `KernelHandle` trait providing a narrow interface between them.

The taint tracking system (`taint.rs`) implements a form of information flow control (IFC) that labels data by provenance and blocks tainted values from reaching sensitive sinks. This is conceptually related to the CaMeL IFC pattern but is not a full CaMeL implementation -- it tracks labels at the value level rather than at the instruction/program level, and does not provide formal non-interference guarantees.

The capability inheritance check (`validate_capability_inheritance`) ensures a control plane / data plane separation where child agents (data plane) cannot exceed parent capabilities (control plane). The tool policy system (`tool_policy.rs`) adds deny-wins glob-based rules with agent-level overriding global rules, plus depth-based restrictions that strip admin tools from subagents.

There is no dual-LLM pattern (separate trusted planner vs. untrusted executor), though the approval manager (`approval.rs`) provides human-in-the-loop gating for dangerous operations.

### 3.2 Access Control and Governance

**Strongly addressed.** This is one of OpenFang's strengths.

- **Capability-based permissions**: 22 typed `Capability` variants with glob pattern matching. Every host call from WASM is checked via `check_capability()` before execution (`host_functions.rs`, line 57-67).
- **RBAC**: Four-tier role hierarchy (Viewer < User < Admin < Owner) with per-action minimum role requirements. Channel binding maps platform identities to OpenFang users (`auth.rs`).
- **Tool-level policy**: `ToolPolicy` struct with agent-level and global rules, deny-wins semantics, group expansion (e.g., `@web_tools`), subagent depth restrictions, and leaf-node spawn prevention (`tool_policy.rs`).
- **Capability inheritance**: `validate_capability_inheritance()` in `capability.rs` (line 171-187) ensures child capabilities are a subset of parent capabilities.
- **Inter-agent authorization**: `AgentMessage(pattern)` and `AgentKill(pattern)` capabilities restrict which agents can communicate with or terminate others.
- **MCP integration**: MCP servers are configured in `config.toml` with explicit command/args pairs.
- **Approval gates**: The `ApprovalManager` (`approval.rs`) blocks dangerous tool calls pending human approval, with per-agent limits and timeout handling.

### 3.3 Runtime Verification and Policy Enforcement

**Strongly addressed.**

- **Loop guard** (`loop_guard.rs`): SHA-256-based tool call loop detection with graduated response (Allow -> Warn -> Block -> CircuitBreak). Enhanced with outcome-aware detection, ping-pong pattern detection (A-B-A-B and A-B-C-A-B-C), poll tool handling with backoff, and warning bucket limits. Global circuit breaker at 30 total calls.
- **Verify-before-commit**: The capability check runs before every tool execution (both in WASM host calls and in the agent loop). The tool policy is checked before the tool runner is invoked.
- **Trace analysis**: The Merkle hash-chain audit trail records every security-critical action (tool invocations, capability checks, agent spawns/kills, network access, shell execution, auth attempts, wire connections, config changes) with SHA-256-linked entries.
- **Goal-hijacking detection**: The `phantom_action_detected()` function in `agent_loop.rs` detects when the LLM claims to have performed actions (sent, posted, emailed) without actually calling any tools, preventing hallucinated completions.
- **Session repair** (`session_repair.rs`): 7-phase validation and repair of message history before LLM submission, preventing corrupted state from propagating.

### 3.4 Detection, Filtering, and Firewalls

**Moderately addressed.**

- **Prompt injection scanning**: `SkillVerifier::scan_prompt_content()` in `verify.rs` (line 109-179) detects 10 prompt override patterns, 9 data exfiltration patterns, and 3 shell command patterns. This is explicitly noted as catching patterns from "341 malicious skills discovered on ClawHub (Feb 2026)."
- **Input sanitization**: Path traversal prevention via `safe_resolve_path()` and `safe_resolve_parent()` with two-phase validation (component check + canonicalization). Shell metacharacter blocking with `contains_shell_metacharacters()` checking 10+ metacharacter categories.
- **Shell bleed detection** (`shell_bleed.rs`): Scans script files referenced in commands for environment variable references that may leak secrets (supports shell `$VAR`, Python `os.environ`, Node.js `process.env` patterns).
- **SSRF firewall**: Multi-layer SSRF protection blocking private IPs, cloud metadata endpoints, non-HTTP schemes, and DNS rebinding.

**Not addressed**: No token-level filtering, no dedicated prompt injection classifier (pattern-matching only), no LLM firewall/proxy layer.

### 3.5 Model-Level Hardening

**Not addressed.** OpenFang is model-agnostic (supports 27 providers) and does not implement instruction hierarchy, preference optimization, representation editing, or any model-internal hardening. The system prompt is constructed by `prompt_builder.rs` but there is no special delimiter or instruction hierarchy enforcement beyond standard system/user message roles.

### 3.6 Boundary Marking and Cryptographic Provenance

**Partially addressed.**

- **Ed25519 signed agent manifests** (`manifest_signing.rs`): Agent identity and capability sets are cryptographically signed. Two-phase verification detects both content tampering and key substitution.
- **Merkle hash-chain audit trail**: Provides cryptographic provenance for all agent actions. Each entry is SHA-256-linked to the previous one.
- **SHA-256 skill checksums**: Skills installed from ClawHub have content verified against known hashes.
- **HMAC-SHA256 wire protocol authentication**: Nonce-based signatures on handshake messages with replay protection.

**Not addressed**: No signed prompts or cryptographic delimiters between system/user/tool content in LLM messages. No hash-based authentication of individual tool call results.

### 3.7 Formal Methods and Semantics

**Not addressed.** The taint tracking system (`taint.rs`) is inspired by information flow control lattice theory but does not include formal proofs of non-interference. There is no formal verification, no type-system-based security guarantees, and no model checking. The Rust type system provides memory safety guarantees, but this is a language property rather than an application-level formal method.

## 4. Source Code Analysis

### 4.1 Security-Critical Code Paths

**Tool execution flow** (traced through source):

1. `agent_loop.rs`: LLM returns `ToolCall` -> check `tool_policy::resolve_tool_access()` -> check `loop_guard.check()` -> check `approval_manager.requires_approval()` -> if approval needed, block on `request_approval()` -> call `tool_runner::execute()`
2. `tool_runner.rs`: Routes to the appropriate tool handler (native, WASM sandbox, MCP, etc.)
3. For WASM tools: `sandbox.rs::execute()` -> spawns blocking thread -> compiles WASM module -> creates Store with GuestState (capabilities, kernel handle) -> sets fuel + epoch -> links host functions -> calls guest `execute()`
4. Host function calls from WASM: `host_functions.rs::dispatch()` -> `check_capability()` -> SSRF check (for net_fetch) -> path traversal check (for fs_read/write) -> actual operation
5. For shell tools: `subprocess_sandbox.rs::sandbox_command()` (env_clear + allowlist) -> `shell_bleed::scan_script_for_shell_bleed()` -> `contains_shell_metacharacters()` check -> `validate_command_allowlist()` -> execution
6. Result goes through `loop_guard.record_outcome()` -> back to agent loop

**Authentication flow** (API requests):

1. `middleware.rs::auth()`: Check if path is public (GET-only for most endpoints) -> check if API key configured -> extract Bearer token or X-API-Key header or query parameter -> constant-time comparison via `subtle::ConstantTimeEq` -> check session cookie for dashboard auth -> return 401 if no valid credential

### 4.2 Input Validation and Sanitization

Validation is applied at multiple layers:

- **Path inputs**: `safe_resolve_path()` rejects `..` components, then canonicalizes. `safe_resolve_parent()` adds belt-and-suspenders filename check (`host_functions.rs`, lines 75-117).
- **URL inputs**: Scheme validation (http/https only), hostname blocklist, DNS-resolved IP check against private ranges (`host_functions.rs`, lines 125-176).
- **Shell commands**: `contains_shell_metacharacters()` blocks 10+ metacharacter categories. `validate_command_allowlist()` enforces a binary allowlist in Allowlist mode. CJK/multi-byte safety is explicitly tested (issue #490) (`subprocess_sandbox.rs`, lines 96-241).
- **Executable paths**: `validate_executable_path()` rejects `..` components (`subprocess_sandbox.rs`, lines 71-82).
- **Skill prompts**: Pattern matching against 10 injection patterns, 9 exfiltration patterns, 3 shell patterns (`verify.rs`, lines 109-179).
- **Wire protocol messages**: Maximum message size of 16MB (`peer.rs`, line 108). Protocol version checking.
- **API rate limiting**: Per-IP GCRA with cost-aware token budgets (`rate_limiter.rs`).

### 4.3 Tool Execution and Sandboxing

**WASM Sandbox** (`sandbox.rs`):
- Uses Wasmtime with no WASI (deny-by-default, no implicit OS access)
- Fuel metering: default 1M instructions, configurable
- Epoch interruption: watchdog thread kills after 30s (configurable)
- Guest ABI: `alloc(i32)->i32` and `execute(i32,i32)->i64`, packed pointer results
- Host functions: capability-checked dispatch via `host_functions::dispatch()`
- Tests verify: echo module, fuel exhaustion, capability denial, unknown method rejection

**Subprocess Sandbox** (`subprocess_sandbox.rs`):
- `env_clear()` strips all inherited environment variables
- Safe allowlist re-adds only PATH, HOME, TMPDIR, etc.
- Process tree kill with graceful SIGTERM -> wait -> force SIGKILL
- Dual timeout: absolute + no-output idle detection

**Shell Execution** (`subprocess_sandbox.rs`, `host_functions.rs`):
- Three exec modes: Deny, Allowlist (default), Full
- In WASM host calls: `Command::new(command).args(&args)` -- no shell invocation, preventing shell injection
- In runtime: metacharacter blocking before allowlist checking, preventing injection via arguments to allowed binaries

### 4.4 Memory and State Management

- **SQLite persistence** (`openfang-memory`): Conversations, memories, knowledge base, and usage data stored in `~/.openfang/data/openfang.db` with schema migrations (`migration.rs`).
- **Session management**: Sessions track conversation history per agent. Session repair validates message structure before LLM submission. Session compaction (LLM-based summarization) prevents unbounded context growth.
- **Credential vault** (`vault.rs`): AES-256-GCM encrypted with Argon2id-derived keys. Vault entries use `Zeroizing<String>`. `Drop` implementation clears all entries and cached keys. Vault file format includes magic bytes (`OFV1`) for versioning.
- **Audit trail persistence**: Audit entries written to `audit_entries` SQLite table. Chain integrity verified on daemon boot.
- **Memory decay**: Configurable confidence decay rate for memory entries.
- **Secret handling**: `Zeroizing<String>` on all API key fields. Subprocess sandbox strips secrets from child process environments.

### 4.5 Authentication and Authorization

**API Authentication** (`middleware.rs`):
- Bearer token authentication with constant-time comparison (`subtle::ConstantTimeEq`)
- Supports `Authorization: Bearer`, `X-API-Key` header, and `?token=` query parameter (for SSE clients)
- Session cookie support for dashboard login
- Public endpoints are explicitly listed and GET-only (POST/PUT/DELETE always require auth)
- Loopback bypass only for `/api/shutdown` (with explicit loopback IP check, default-deny)

**RBAC** (`auth.rs`):
- Four roles: Viewer (read-only), User (chat), Admin (spawn/kill/install), Owner (config/users)
- Channel bindings map platform identities (e.g., `telegram:123456`) to OpenFang users
- `authorize(user_id, action)` checks role hierarchy

**Wire Protocol** (`peer.rs`):
- HMAC-SHA256 with nonce-based mutual authentication
- Replay protection via `NonceTracker` with 5-minute window and garbage collection
- Mandatory `shared_secret` -- OFP refuses to start without it
- Constant-time HMAC comparison via `subtle::ConstantTimeEq`

## 5. Production Readiness

### 5.1 Maturity Level

- **Version**: v0.3.30 (README) / v0.5.5 (Cargo.toml workspace.package.version) -- pre-1.0, breaking changes expected
- **Code quality**: Zero clippy warnings enforced. Consistent code style with `rustfmt`. Comprehensive doc comments on all public items. Thorough error handling with `thiserror` and `anyhow`.
- **Binary size**: ~32MB single binary (release profile with LTO, stripped)
- **Performance**: Claims <200ms cold start, 40MB idle memory
- **Stability**: README warns to "pin to a specific commit for production deployments until v1.0"
- **Language**: Rust -- memory safety, thread safety via ownership system

### 5.2 Test Coverage

- **1,767+ tests** claimed, consistent with the extensive `#[cfg(test)]` blocks observed across all crates
- **Security-specific tests** are extensive:
  - Taint tracking: injection blocking, exfiltration blocking, declassification, clean pass-through (`taint.rs`)
  - Capability matching: exact, wildcard, glob, numeric bounds, inheritance validation, escalation denial (`capability.rs`)
  - WASM sandbox: echo module, fuel exhaustion, host call capability denial, unknown method (`sandbox.rs`)
  - Audit trail: chain integrity, tamper detection, tip changes, DB persistence + restart (`audit.rs`)
  - Manifest signing: sign-verify round-trip, tamper detection, wrong key detection (`manifest_signing.rs`)
  - SSRF: private IP blocking, public IP allowing, scheme validation (`host_functions.rs`)
  - Shell injection: metacharacter blocking (12+ test cases), allowlist enforcement, CJK safety (`subprocess_sandbox.rs`)
  - Loop guard: threshold behavior, circuit breaker, ping-pong detection, outcome awareness, poll handling (`loop_guard.rs`)
  - Prompt injection: clean content pass, injection detection, exfiltration pattern detection (`verify.rs`)
  - Vault: init/roundtrip, wrong key failure, magic header, legacy compat (`vault.rs`)
  - Auth: role hierarchy, channel binding, owner full access, viewer read-only, unknown user denial (`auth.rs`)
  - Tool policy: deny-wins, agent overrides global, group expansion, depth restriction, implicit deny (`tool_policy.rs`)
- **Integration tests**: Separate test files for API integration, daemon lifecycle, load testing, multi-agent scenarios, WASM agent integration, workflow integration, bridge integration, and migration
- **No dedicated fuzzing** observed in the repository

### 5.3 Documentation Quality

- **README.md**: Comprehensive (510 lines), covers architecture, features, benchmarks, quick start
- **docs/security.md**: Extensive (1,492 lines) technical security reference with code excerpts, threat model summary, and configuration reference. Documents all 16 security systems with code-level detail.
- **SECURITY.md**: Responsible disclosure policy with clear scope
- **CLAUDE.md**: Developer guide for build/test/integration workflows
- **docs/** directory: 18 documentation files covering architecture, API reference, CLI reference, configuration, providers, workflows, channel adapters, MCP/A2A, production checklist, etc.
- **Code comments**: Thorough module-level doc comments on all source files, with `//! ...` module documentation explaining purpose and design

### 5.4 Deployment Model

- Single binary deployment (no Docker required, though Dockerfile provided)
- Daemon mode with `openfang start`, managed by CLI
- Local-only by default (binds to `127.0.0.1:4200`); explicit configuration needed for remote access
- SQLite for all persistence (no external database dependency)
- Cross-platform: Linux, macOS, Windows (CI builds for all three)
- Desktop app via Tauri 2.0 (system tray, notifications, global shortcuts)
- Docker Compose file for containerized deployment

## 6. Strengths

1. **Comprehensive defense-in-depth**: 16 independently testable security systems is an unusually thorough approach for an agent framework. Each system addresses a specific threat class and operates independently. The WASM sandbox with dual metering (fuel + epoch) is particularly well-designed -- fuel catches compute loops while epochs catch host call abuse.

2. **Capability-based security with typed enforcement**: The `Capability` enum with 22 variants and glob pattern matching is more granular than most agent frameworks. The capability inheritance check that prevents child agents from exceeding parent capabilities is a strong defense against privilege escalation.

3. **Information flow taint tracking**: The lattice-based taint propagation model is a notable feature. While not a formal IFC implementation, the predefined sinks (shell_exec blocks ExternalNetwork/UntrustedAgent, net_fetch blocks Secret/PII, agent_message blocks Secret) address real attack vectors.

4. **Cryptographic integrity throughout**: Merkle hash-chain audit trail, Ed25519 manifest signing, AES-256-GCM credential vault with Argon2id KDF, HMAC-SHA256 wire protocol with constant-time comparison, and secret zeroization. The use of `subtle::ConstantTimeEq` consistently across auth and HMAC verification is good practice.

5. **Rust language benefits**: Memory safety without GC eliminates entire classes of vulnerabilities (buffer overflows, use-after-free, data races). The type system enforces invariants at compile time. The ownership model prevents accidental secret sharing.

6. **Excellent security test coverage**: Nearly every security system has dedicated tests that verify both positive (allow) and negative (deny) cases. The shell metacharacter tests are particularly thorough, including CJK/multi-byte safety tests.

7. **Multi-layer shell execution protection**: The combination of env_clear, allowlist/metacharacter blocking, path traversal prevention, shell bleed scanning, and direct process execution (no shell invocation) provides strong defense against command injection.

## 7. Gaps and Weaknesses

1. **Taint tracking appears underintegrated** (Category 3.1 -- Secure Architectures): The taint tracking system in `taint.rs` is well-designed as a library but its integration into the actual agent execution flow is unclear from the source. The `TaintedValue` struct and `TaintSink` definitions exist in `openfang-types`, but the agent loop and tool runner don't show explicit taint label application to incoming data or taint checks before tool execution. The taint system may be aspirational infrastructure rather than actively enforced at every data boundary.

2. **No model-level hardening** (Category 3.5): The system relies entirely on external-to-model defenses. There is no instruction hierarchy enforcement, no special delimiter handling to prevent prompt injection at the model input level, and no fine-tuning for instruction-following robustness. This is understandable given the multi-provider design (27 providers, 123+ models), but it means the system cannot leverage provider-specific hardening features.

3. **Pattern-based prompt injection detection** (Category 3.4): The prompt injection scanner uses keyword matching against 10 fixed patterns. This will miss obfuscated, multilingual, or novel injection attempts. There is no ML-based classifier, no perplexity-based detection, and no LLM-as-a-judge verification.

4. **Ed25519 signing is infrastructure without trust chain**: The manifest signing module provides the cryptographic primitives (sign/verify), but there is no observed trust store, key distribution mechanism, or policy for which public keys are trusted. Without a PKI or trust anchor, the signing provides integrity but not authentic provenance -- an attacker who can modify the manifest can also provide their own key.

5. **No formal verification** (Category 3.7): The taint tracking system claims lattice-based semantics but has no formal proof. The capability system's glob matching (`glob_matches`) has no proof of completeness or correctness beyond tests. For a system that handles such sensitive operations, formal methods could strengthen confidence.

6. **RBAC disabled when unconfigured**: When no users are configured, `AuthManager::is_enabled()` returns false and the auth middleware passes all requests when no `api_key` is set. The system defaults to open-access on localhost, which is reasonable for development but risky if accidentally deployed without configuration.

7. **Vault keyring fallback is weak**: The file-based keyring fallback (`store_keyring_key`) uses XOR obfuscation with a SHA-256 hash of username + hostname. This is explicitly acknowledged as a fallback but provides only obfuscation, not real protection, against an attacker with filesystem access.

8. **No network-level isolation for agents**: While the WASM sandbox provides process-level isolation and the capability system restricts operations, there is no network namespace isolation, container isolation, or seccomp-BPF filtering for native tool execution. The subprocess sandbox clears environment variables but does not restrict syscalls or network access at the OS level.

## 8. Key Findings

- **OpenFang has the most comprehensive security architecture of any open-source agent framework reviewed.** With 16 independently testable security systems spanning capabilities, sandboxing, cryptography, information flow, and runtime verification, it goes significantly beyond the typical allowlist-only approach.

- **The WASM dual-metered sandbox with capability-checked host functions is well-engineered.** Fuel metering + epoch interruption + deny-by-default capabilities form a strong isolation boundary. The code quality and test coverage for this component are high.

- **The taint tracking system is architecturally sound but may be underintegrated.** The types and sink definitions exist, but evidence of active enforcement at every data flow boundary in the agent loop is not clearly visible. If fully wired in, this would be one of the strongest prompt injection defenses in any agent framework.

- **Pattern-based prompt injection detection is a known weak point.** The 10-pattern keyword scanner will miss sophisticated attacks. This is the most likely entry point for adversarial inputs, and the gap is partially mitigated by the capability system and taint tracking (which limit what a hijacked agent can do even if injection succeeds).

- **Production deployment requires careful configuration.** The system defaults to open-access on localhost with no RBAC. Security depends on the operator setting `api_key`, `shared_secret`, capability manifests, and tool policies. The documentation is thorough about what needs to be configured, but the secure-by-default posture could be stronger.
