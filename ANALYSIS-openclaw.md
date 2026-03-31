# openclaw Security Analysis (Baseline)

**Repository:** https://github.com/openclaw/openclaw
**Commit:** dbe6663c34a4721af47520cb11d6b86c277466d8
**Point-in-time:** 2026-03-31
**Language:** TypeScript
**Category:** Baseline (non-security-focused)

## 1. Overview

OpenClaw is a personal AI assistant designed to run on the operator's own devices and bridge across messaging channels the operator already uses. The project describes itself as "Your own personal AI assistant. Any OS. Any Platform. The lobster way." It connects to over 20 messaging platforms (WhatsApp, Telegram, Slack, Discord, Signal, iMessage, IRC, Microsoft Teams, Matrix, and more) and routes conversations through a central Gateway control plane to AI model backends.

### High-Level Architecture

The system is organized around these core components:

- **Gateway** (`src/gateway/`): A WebSocket + HTTP control plane that runs locally (default `ws://127.0.0.1:18789`). It handles session management, channel routing, authentication, tool invocation, cron jobs, and webhooks. The Gateway is the single hub through which all interactions pass.

- **Pi Agent Runtime** (`src/agents/`): The agent execution engine that manages AI model inference, tool execution, session state, and prompt construction. It operates in RPC mode with tool streaming and block streaming.

- **Channels** (`src/channels/`, `extensions/`): Messaging channel integrations (Telegram, Discord, Slack, WhatsApp, etc.) that bridge between external messaging APIs and the Gateway. Each channel is either a core integration or a bundled plugin.

- **Plugin System** (`src/plugins/`, `src/plugin-sdk/`, `extensions/`): An extensive plugin architecture with ~80+ bundled plugins covering model providers (Anthropic, OpenAI, Google, etc.), channels, tools, media understanding, and more. Plugins are loaded in-process.

- **Sandbox** (`src/agents/sandbox/`): Docker-based container isolation for tool execution, with SSH backend support.

- **ACP Bridge** (`src/acp/`): An Agent Client Protocol implementation for IDE integration via stdio/NDJSON.

- **CLI** (`src/cli/`, `src/commands/`): A comprehensive CLI surface for gateway management, messaging, agent interaction, onboarding, and diagnostics.

- **Companion Apps** (`apps/`): Native macOS, iOS, and Android applications that connect to the Gateway.

The codebase is large and mature: approximately 3,050 non-test TypeScript source files in `src/`, plus 2,941 files in `extensions/`, with 3,313 test files. The monorepo uses pnpm workspaces.

## 2. Security Architecture

### 2.1 Design Philosophy

OpenClaw has a deliberately articulated security philosophy that is unusually comprehensive for what is nominally a "personal assistant" project. From `VISION.md`:

> "Security in OpenClaw is a deliberate tradeoff: strong defaults without killing capability. The goal is to stay powerful for real work while making risky paths explicit and operator-controlled."

The project's priority list explicitly places "Security and safe defaults" first. The project maintains a 300-line `SECURITY.md` with a detailed vulnerability disclosure policy, an explicit operator trust model, and a dedicated Security & Trust lead.

The fundamental trust model is **single trusted operator**: one user per gateway instance, with all authenticated callers treated as trusted operators. This is explicitly not a multi-tenant system. The project states: "OpenClaw's security model is 'personal assistant' (one trusted operator, potentially many agents), not 'shared multi-tenant bus.'"

A key design principle is that the AI model/agent is **not** a trusted principal. From `SECURITY.md`: "The model/agent is not a trusted principal. Assume prompt/content injection can manipulate behavior. Security boundaries come from host/config trust, auth, tool policy, sandboxing, and exec approvals."

### 2.2 Security Primitives Present

OpenClaw implements a remarkable number of security primitives for a personal assistant framework:

1. **Gateway Authentication** (`src/gateway/auth.ts`): Multiple auth modes including token-based, password-based, Tailscale whois-based, device-token, bootstrap-token, and trusted-proxy authentication. Timing-safe secret comparison via `crypto.timingSafeEqual` (with SHA-256 hashing to normalize lengths) in `src/security/secret-equal.ts`.

2. **Auth Rate Limiting** (`src/gateway/auth-rate-limit.ts`): In-memory sliding-window rate limiter for failed auth attempts, with per-IP tracking, configurable lockout periods (default 10 attempts / 1 minute window / 5 minute lockout), and loopback exemption.

3. **Operator Scope System** (`src/gateway/method-scopes.ts`): Fine-grained RBAC with five operator scopes: `operator.admin`, `operator.read`, `operator.write`, `operator.approvals`, `operator.pairing`. Every Gateway method is classified into exactly one scope, and unclassified methods default to `ADMIN_SCOPE`.

4. **DM Pairing & Allowlists** (`src/security/dm-policy-shared.ts`, `src/pairing/`): A pairing-code-based access control system for inbound DMs across messaging channels. Unknown senders receive a short pairing code; the operator must approve them. Explicit opt-in required for open public DMs.

5. **Exec Approval System** (`src/gateway/exec-approval-manager.ts`, `src/infra/exec-approvals*.ts`): An interactive human-in-the-loop approval workflow for command execution. Approval records are tokenized with UUIDs, time-limited, and single-use (for `allow-once` decisions). The system includes obfuscation detection (`src/infra/exec-obfuscation-detect.ts`) that checks for base64-encoded commands, hex-encoded strings, invisible Unicode code points, and other evasion techniques.

6. **Docker Sandbox** (`src/agents/sandbox/`, `Dockerfile.sandbox`): Full container-based isolation for tool execution. The sandbox validator (`src/agents/sandbox/validate-sandbox-security.ts`) blocks dangerous bind mounts (system directories, Docker socket, SSH keys, cloud credentials), enforces seccomp and AppArmor profiles, blocks `host` network mode, and performs symlink escape hardening via existing-ancestor path resolution.

7. **SSRF Protection** (`src/infra/net/ssrf.ts`): DNS-rebinding-safe SSRF protection that blocks private network addresses, loopback, link-local, cloud metadata endpoints (e.g., `metadata.google.internal`), legacy IPv4 literal encodings, and IPv4-mapped IPv6 addresses. Uses a custom DNS lookup interceptor.

8. **External Content Wrapping** (`src/security/external-content.ts`): Untrusted external content (emails, webhooks, web fetches) is wrapped in randomized XML boundary markers with security warnings, designed to resist prompt injection. Suspicious injection patterns are detected and logged.

9. **Tool Policy System** (`src/agents/tool-policy.ts`, `src/agents/tool-policy-pipeline.ts`): Configurable allow/deny lists for tools, tool profiles (e.g., `messaging` for restricted tool sets), owner-only tool restrictions, and plugin-scoped tool groups.

10. **Security Audit CLI** (`src/security/audit.ts` -- 1,504 lines, plus `audit-extra.sync.ts` at 48,752 characters and `audit-extra.async.ts` at 47,874 characters): A comprehensive `openclaw security audit` command that inspects configuration for insecure settings, exposed gateways, missing auth, dangerous config flags, filesystem permissions, channel security, browser control auth, and more. Supports `--deep` mode with live gateway probing and `--fix` for automated remediation.

11. **CSP Headers** (`src/gateway/control-ui-csp.ts`): Content Security Policy headers for the web control UI, including `frame-ancestors 'none'`, inline script hash allowlisting, and restricted `connect-src`.

12. **Browser Origin Checking** (`src/gateway/origin-check.ts`): Origin validation for browser requests with an allowlist mechanism and loopback fallback for local development.

13. **Skill Scanner** (`src/security/skill-scanner.ts`): Static analysis of skill/plugin code for dangerous patterns before installation.

14. **Secrets Detection** (`.detect-secrets.cfg`, `.secrets.baseline`): Automated secret scanning via `detect-secrets` with a 433KB baseline file and custom exclusion patterns.

15. **Dangerous Config Flags** (`src/security/dangerous-config-flags.ts`): Explicit tracking and auditing of all `dangerously*` config flags, surfaced in `openclaw doctor` and the security audit.

### 2.3 Implicit Threat Model

OpenClaw has an **explicit** threat model documented in `docs/security/THREAT-MODEL-ATLAS.md`, mapped to the MITRE ATLAS framework. The model identifies five trust boundaries:

1. **Channel Access**: Untrusted zone (messaging platforms) -> Gateway via pairing, allowlists, and authentication.
2. **Session Isolation**: Gateway -> Agent sessions via session keys and per-agent tool policies.
3. **Tool Execution**: Agent -> Execution sandbox via Docker isolation or host exec-approvals.
4. **External Content**: Agent -> Fetched URLs/emails/webhooks via content wrapping and SSRF blocking.
5. **Supply Chain**: ClawHub skill marketplace -> Agent via moderation and scanning.

Key threats explicitly modeled include: gateway endpoint discovery, pairing code interception, AllowFrom spoofing, prompt injection via messaging channels, tool execution abuse, SSRF, skill supply chain attacks, and session data exfiltration.

## 3. Mapping to Defense Taxonomy

### 3.1 Secure Architectures by Construction

**Partially addressed.** OpenClaw's architecture separates the control plane (Gateway) from execution (sandbox/host), but both remain within the same operator trust boundary. The Gateway is designed as a local-first loopback-bound service, which is a secure default. The plugin system enforces import boundaries (plugins must use `openclaw/plugin-sdk/*`, not import core internals), enforced by architecture tests (`test/extension-plugin-sdk-boundary.test.ts`, `test/plugin-extension-import-boundary.test.ts`). The session model provides per-channel, per-peer isolation. However, the system is fundamentally single-process (plugins run in-process with the Gateway), and session isolation is logical rather than process-level.

### 3.2 Access Control and Governance

**Substantially addressed.** OpenClaw implements a layered access control system:

- **Gateway auth**: Token/password/Tailscale/trusted-proxy authentication with rate limiting.
- **Operator scopes**: Five-level RBAC (admin, read, write, approvals, pairing) applied to every Gateway method.
- **DM pairing**: Code-based access control for messaging channel access with per-channel allowlists.
- **Owner-only tools**: Certain tools (WhatsApp login, cron, gateway, nodes) are restricted to the owner sender.
- **Tool policies**: Allow/deny lists with profile-based presets, per-agent configuration.
- **Exec approvals**: Interactive human-in-the-loop approval for command execution, with allowlist/always-allow/ask modes.

### 3.3 Runtime Verification and Policy Enforcement

**Substantially addressed.** The exec approval system provides runtime verification of tool execution requests. The ACP approval classifier (`src/acp/approval-classifier.ts`) categorizes tool calls into classes (readonly_scoped, readonly_search, mutating, exec_capable, control_plane, interactive, other, unknown) and auto-approves only narrow readonly operations (file reads scoped to cwd, search). Exec-capable and control-plane tool calls always require explicit approval. The sandbox security validator runs at container creation time, blocking dangerous Docker configurations. The SSRF protector performs DNS resolution interception at runtime.

### 3.4 Detection, Filtering, and Firewalls

**Substantially addressed.** Multiple detection layers:

- **External content injection detection**: Regex-based detection of prompt injection patterns (`src/security/external-content.ts`) with logging and monitoring.
- **Command obfuscation detection**: Detection of base64/hex encoding, invisible Unicode, and other evasion techniques in exec commands (`src/infra/exec-obfuscation-detect.ts`).
- **SSRF blocking**: DNS-rebinding-safe IP and hostname filtering with cloud metadata endpoint blocking.
- **Skill scanner**: Static code analysis for dangerous patterns in skills before installation.
- **Security audit**: A comprehensive runtime audit tool (`openclaw security audit --deep`) that probes for misconfigurations.
- **Safe regex validation**: ReDoS protection via `src/security/safe-regex.ts` for user-supplied regex patterns.

### 3.5 Model-Level Hardening

**Partially addressed.** OpenClaw does not modify or fine-tune models, but it does implement prompt-level hardening. External content is wrapped with security notices instructing the model to ignore injected instructions. The README notes: "for the best experience and lower prompt-injection risk use the strongest latest-generation model available to you." The `SECURITY.md` explicitly warns that "Weak model tiers are generally easier to prompt-inject" and recommends strong model tiers for tool-enabled agents. However, there is no structured output enforcement, no model output validation, and no systematic defense against indirect prompt injection beyond the content wrapping.

### 3.6 Boundary Marking and Cryptographic Provenance

**Partially addressed.** External content boundary markers use randomized 16-byte hex IDs to prevent marker spoofing (`src/security/external-content.ts`). Gateway authentication uses timing-safe comparison via SHA-256 hashing. Exec approval records are identified by cryptographic UUIDs. However, there is no cryptographic signing of tool outputs, no provenance chains for agent actions, and no tamper-evident logging of agent decisions.

### 3.7 Formal Methods and Semantics

**Partially addressed -- and notably so for a personal assistant project.** OpenClaw maintains TLA+ formal models in a separate repository (`vignesh07/openclaw-formal-models`) covering:

- Gateway exposure and open gateway misconfiguration
- Node exec pipeline (highest-risk capability)
- Pairing store (DM gating)

Each claim has a runnable model check plus a negative model that produces expected counterexamples. The `docs/security/formal-verification.md` page documents the models, their scope, and their limitations ("These are models, not the full TypeScript implementation. Drift between model and code is possible."). This is unusual for any application-level project.

## 4. Source Code Analysis

### 4.1 Tool Execution Model

Tool execution flows through a multi-layered pipeline:

1. **Tool Registration**: Tools are registered via the plugin SDK and the agent tool catalog (`src/agents/tool-catalog.ts`). Each tool has metadata including `ownerOnly` flags and names.

2. **Tool Policy Filtering** (`src/agents/tool-policy.ts`, `src/agents/tool-policy-pipeline.ts`): Before tools are presented to the model, they are filtered through allow/deny lists, tool profiles, and owner-only restrictions. Non-owner senders have owner-only tools removed entirely.

3. **ACP Approval Classification** (`src/acp/approval-classifier.ts`): When a tool call is requested, it is classified into an approval class. Auto-approval is limited to `readonly_scoped` (file reads within cwd) and `readonly_search` (search/web_search/memory_search). All exec-capable, control-plane, mutating, and interactive tools require explicit approval.

4. **Exec Approval Flow** (`src/gateway/exec-approval-manager.ts`, `src/infra/exec-approvals.ts`): For commands requiring approval, a request is registered with a UUID, a timeout, and caller metadata (connection ID, device ID, client ID). The operator is presented with the command details and must approve (allow-once, allow-always) or deny. Allow-once approvals are consumed atomically to prevent replay.

5. **Execution Host Resolution** (`src/infra/exec-host.ts`): The execution host is determined (gateway host, sandbox container, or remote node). The default is `auto`, which uses sandbox when available, otherwise gateway host.

6. **Sandbox Execution** (`src/agents/sandbox/`): If sandboxed, commands execute in a Docker container with validated bind mounts, seccomp/AppArmor enforcement, network mode restrictions, and environment variable sanitization (`src/agents/sandbox/sanitize-env-vars.ts`).

7. **Command Safety Checks**: Executable values are validated for shell metacharacters, control characters, null bytes, and suspicious patterns (`src/infra/exec-safety.ts`). Obfuscation detection runs in parallel.

### 4.2 Input Handling

User input from messaging channels is treated as untrusted. Key handling points:

- **DM Policy Enforcement** (`src/security/dm-policy-shared.ts`): Inbound messages from unknown senders are intercepted by the pairing system. Only approved senders proceed.

- **Chat Sanitization** (`src/gateway/chat-sanitize.ts`): Input sanitization for chat messages entering the gateway.

- **Terminal Safe Text** (`src/terminal/safe-text.ts`): Terminal output is sanitized to prevent terminal escape sequence injection.

- **External Content Wrapping** (`src/security/external-content.ts`): Content from webhooks, emails, and web fetches is wrapped with randomized boundary markers and security notices before being passed to the agent.

- **Config Validation**: Configuration inputs use Zod schemas at external boundaries (config files, webhook payloads, CLI/JSON output) as noted in the coding style guidelines.

### 4.3 Sandboxing and Isolation

OpenClaw provides Docker-based sandboxing as an opt-in feature (`agents.defaults.sandbox.mode`):

- **Container Configuration** (`src/agents/sandbox/config.ts`, `src/agents/sandbox/types.ts`): Configurable sandbox settings including image, workspace mounts, bind mounts, network mode, and prune policies. Default image is a minimal Debian bookworm with basic tools (`Dockerfile.sandbox`).

- **Security Validation** (`src/agents/sandbox/validate-sandbox-security.ts`): At container creation time, comprehensive validation blocks:
  - Bind mounts to system directories (`/etc`, `/proc`, `/sys`, `/dev`, `/root`, `/boot`, `/run`, Docker socket paths)
  - Bind mounts to sensitive home subdirectories (`.aws`, `.config`, `.kube`, `.openclaw`, `.ssh`)
  - Mounting the filesystem root (`/`)
  - Non-absolute source paths
  - `host` network mode (bypasses isolation)
  - `unconfined` seccomp or AppArmor profiles
  - Symlink escape attacks (resolved via existing-ancestor path canonicalization)

- **Filesystem Bridge** (`src/agents/sandbox/fs-bridge.ts`, `fs-bridge-path-safety.ts`): Controlled file transfer between host and sandbox with path safety validation.

- **Environment Sanitization** (`src/agents/sandbox/sanitize-env-vars.ts`): Provider API keys and sensitive environment variables are stripped before passing to sandbox containers.

- **SSH Backend** (`src/agents/sandbox/ssh-backend.ts`, `ssh.ts`): An alternative sandbox backend that executes commands over SSH, enabling remote sandbox hosts.

- **Default Off**: Sandbox mode defaults to `off`. The `SECURITY.md` notes: "Exec behavior is host-first by default: `agents.defaults.sandbox.mode` defaults to `off`."

### 4.4 State Management

Session state is managed hierarchically:

- **Session Keys** (`src/gateway/server-session-key.ts`, `src/routing/session-key.ts`): Sessions are keyed as `agent:channel:peer`, providing per-agent, per-channel, per-peer isolation. A `main` session is used for direct chats.

- **Session Storage** (`src/gateway/session-utils.fs.ts`): Sessions are persisted as JSONL files under `~/.openclaw/agents/<agentId>/sessions/`. The base directory is not configurable.

- **Session Lifecycle** (`src/gateway/session-lifecycle-state.ts`): State machine managing session creation, activation, pruning, and archival.

- **Config State** (`src/config/`): Configuration is loaded from `~/.openclaw/openclaw.json` with environment variable overlay. Hot-reloading is supported (`src/gateway/config-reload.ts`).

- **Credential Storage** (`src/secrets/`, `src/gateway/credentials.ts`): Credentials are stored at `~/.openclaw/credentials/` with SecretRef semantics for configuration references. Provider API keys can be sourced from environment variables, config files, or OAuth flows.

### 4.5 Network and Data Flow

Data flows through the system as follows:

1. **Inbound**: External messaging platforms -> Channel integrations -> Gateway (WebSocket/HTTP) -> Session routing -> Agent runtime.

2. **Outbound**: Agent responses -> Gateway -> Channel routing -> External messaging platforms.

3. **Tool Execution**: Agent -> Tool invocation -> Exec approval check -> Sandbox/host execution -> Result return.

4. **External Fetch**: Agent -> Web fetch tool -> SSRF check (DNS interception + IP blocking) -> External HTTP request -> Content wrapping -> Agent.

Network access controls:
- Gateway binds to loopback by default (`gateway.bind="loopback"`).
- SSRF protection intercepts DNS resolution and blocks private IPs, loopback, link-local, and cloud metadata endpoints.
- Docker sandbox can restrict network mode (`bridge`, `none`, or custom; `host` mode blocked).
- Tailscale integration provides encrypted tunnel access with identity-based auth.

### 4.6 Permission Model

The operator has extensive control over agent capabilities:

- **Tool Profiles** (`tools.profile`): Preset tool sets like `messaging` (restricted) or broader profiles.
- **Tool Allow/Deny** (`tools.allow`, `tools.deny`): Fine-grained per-tool control.
- **Exec Approvals** (`tools.exec.approval`): `ask` (interactive), `allowlist`, or `auto` modes for command execution approval.
- **Safe Bins** (`tools.exec.safeBins`): Curated list of binaries that bypass interactive approval.
- **Sandbox Mode** (`agents.defaults.sandbox.mode`): `off`, `non-main`, or `all` to control which sessions get sandboxed.
- **Owner-Only Tools**: Some tools require owner sender status.
- **Workspace-Only FS**: Optional restriction of file operations to the workspace directory.
- **DM Policy**: Per-channel control over who can message the agent (`pairing`, `open`, `disabled`).
- **Dangerous Flags**: Explicit `dangerously*` prefixed config keys for break-glass capabilities that weaken defaults.

## 5. Production Readiness

### 5.1 Maturity Level

OpenClaw is a mature, actively developed project with a large contributor base, daily releases (calver `vYYYY.M.D`), and a formal release process. The project has:

- A 923KB `CHANGELOG.md` indicating extensive release history
- Automated CI/CD via GitHub Actions
- Multiple release channels (stable, beta, dev)
- macOS app signing and notarization
- npm package distribution
- Docker images with health checks
- A dedicated Security & Trust lead
- Bug bounty disclosure (though no monetary bounty)
- A private maintainer release runbook
- GHSA advisory handling workflow

### 5.2 Test Coverage

Testing is extensive:

- **3,313 test files** covering unit, integration, e2e, and live tests
- **Vitest** framework with V8 coverage thresholds (70% lines/branches/functions/statements)
- **Colocated tests** (`*.test.ts`) alongside source files
- **Security-specific tests**: `src/security/audit.test.ts` (127,273 bytes), `src/security/dm-policy-shared.test.ts`, `src/security/external-content.test.ts`, `src/security/skill-scanner.test.ts`, `src/security/safe-regex.test.ts`, `src/security/temp-path-guard.test.ts`, `src/security/windows-acl.test.ts`
- **Sandbox security tests**: `src/agents/sandbox/validate-sandbox-security.test.ts`, `src/agents/sandbox/fs-bridge.boundary.test.ts`
- **Auth tests**: `src/gateway/auth.test.ts` (28,355 bytes), `src/gateway/auth-rate-limit.test.ts`, extensive server auth test suites
- **Architecture boundary tests**: `test/extension-plugin-sdk-boundary.test.ts`, `test/plugin-extension-import-boundary.test.ts`
- **Pre-commit hooks** enforcing `pnpm check` (format + lint + type check)
- **detect-secrets** in CI for automated secret detection
- **Docker e2e tests** for containerized workflows

### 5.3 Documentation Quality

Documentation is extensive and well-structured:

- **Hosted docs site** (docs.openclaw.ai) via Mintlify with i18n support (zh-CN)
- **Security documentation**: `SECURITY.md` (300 lines), `docs/security/THREAT-MODEL-ATLAS.md` (MITRE ATLAS mapping), `docs/security/formal-verification.md`, `docs/security/CONTRIBUTING-THREAT-MODEL.md`
- **Gateway security docs**: `docs/gateway/security/`, `docs/gateway/sandboxing.md`, `docs/gateway/authentication.md`, `docs/gateway/trusted-proxy-auth.md`
- **Plugin SDK docs**: Building plugins, SDK overview, SDK entrypoints, channel plugins, provider plugins
- **Comprehensive AGENTS.md** (35,263 bytes) serving as the contributor guide with detailed architecture boundaries, testing guidelines, and security tips
- **VISION.md** articulating project direction and security philosophy

### 5.4 Deployment Model

OpenClaw supports multiple deployment models:

- **Local install** (`npm install -g openclaw@latest`) with daemon mode (launchd/systemd user service)
- **Docker** (`Dockerfile`, `docker-compose.yml`) with non-root user, capability dropping (`cap_drop: NET_RAW, NET_ADMIN`), and `no-new-privileges`
- **Nix** for declarative configuration
- **macOS app** (menu bar) with Sparkle auto-update
- **iOS/Android companion apps** for mobile access
- **Remote gateway** via Tailscale Serve/Funnel or SSH tunnels

The recommended deployment is loopback-only on a single-user machine with Tailscale for remote access. Docker Compose drops capabilities and sets `no-new-privileges`.

## 6. What Works Well

1. **Explicit trust model**: The documented single-operator trust model is clear and consistently enforced throughout the codebase. The `SECURITY.md` is remarkably thorough about what is and is not in scope.

2. **Defense in depth for tool execution**: The layered approach of tool policy filtering, approval classification, interactive human-in-the-loop approval, command obfuscation detection, sandbox validation, and SSRF protection creates meaningful barriers against agent misuse.

3. **Security audit tooling**: The built-in `openclaw security audit --deep` command is a proactive approach to helping operators identify misconfigurations, distinguishing between `info`, `warn`, and `critical` severity findings with actionable remediation guidance.

4. **Formal verification effort**: TLA+ models for highest-risk paths (gateway exposure, node exec pipeline, pairing store) is unusual and commendable for an application-level project.

5. **Channel pairing system**: The DM pairing mechanism provides a practical zero-trust-by-default approach to inbound messaging, requiring explicit operator approval before processing messages from unknown senders.

6. **Dangerous flag convention**: The consistent `dangerously*` prefix for break-glass config options makes it easy to audit which security defaults have been weakened, and these are surfaced in both `openclaw doctor` and the security audit.

7. **Extensive testing**: The 3,313 test files with 70% coverage thresholds and dedicated security test suites demonstrate serious investment in correctness.

## 7. Security Gaps (Relative to Defense Taxonomy)

1. **Sandbox off by default**: The Docker sandbox defaults to `off` (`agents.defaults.sandbox.mode=off`). While this is documented and fits the single-operator trust model, it means most users run tool execution directly on the host without isolation. The SECURITY.md acknowledges this: "Exec behavior is host-first by default."

2. **In-process plugin execution**: Plugins run in the same Node.js process as the Gateway with full host privileges. The `SECURITY.md` states: "Installing or enabling a plugin grants it the same trust level as local code running on that gateway host." There is no process-level plugin isolation.

3. **No structured output validation**: Agent responses are not validated against expected schemas or filtered for unsafe content patterns before being forwarded to messaging channels or used in tool invocations. The prompt injection defense relies primarily on content wrapping and model compliance.

4. **No cryptographic provenance for agent actions**: There is no signing or tamper-evident logging of tool invocations, agent decisions, or approval chains. Exec approvals use UUIDs but not cryptographic binding.

5. **Session isolation is logical, not process-level**: Sessions share the same Gateway process. A compromised agent session could theoretically access other session data in memory, though this would require escaping the application-level isolation.

6. **Prompt injection defense relies on model compliance**: The external content wrapping (`<<<EXTERNAL_UNTRUSTED_CONTENT>>>`) relies on the model respecting the security notice. The system detects suspicious patterns for logging but does not block injected content -- it is still passed to the model. The SECURITY.md explicitly places prompt injection out of scope for security reports.

7. **TLA+ model drift**: The formal models are maintained in a separate repository and could drift from the TypeScript implementation. There is no automated verification that the code matches the model.

8. **No output filtering to channels**: While input from channels is filtered through allowlists and pairing, agent responses sent back to channels do not appear to undergo systematic filtering for sensitive data leakage (API keys, file contents, etc.).

## 8. Key Findings

- **OpenClaw is remarkably security-conscious for a personal assistant framework.** It has a documented threat model (MITRE ATLAS), formal TLA+ verification models, a comprehensive security audit CLI, timing-safe auth, SSRF protection, exec obfuscation detection, Docker sandbox validation with symlink escape hardening, and a dedicated Security & Trust lead. This is well above what would be expected for a "baseline" non-security-focused framework.

- **The explicit single-operator trust model is both a strength and a limitation.** It enables powerful local capabilities (host exec, file access, browser control) while being honest about what it does and does not protect against. Multi-tenant scenarios are explicitly out of scope, which is appropriate for the use case but means the system has no concept of least-privilege per-agent or per-user isolation.

- **Defense in depth for tool execution is the strongest security surface.** The chain of tool policy -> approval classification -> interactive approval -> obfuscation detection -> sandbox validation -> SSRF blocking provides multiple independent barriers. However, sandbox mode being off by default significantly reduces the effective defense for most users.

- **Prompt injection is acknowledged but architecturally unresolved.** The project explicitly places prompt injection out of scope for vulnerability reports and relies on model-level compliance with security notices. This is a reasonable position given current LLM limitations, but it means the system's security guarantees degrade proportionally to model susceptibility to injection.

- **The project has invested heavily in making security auditable and operator-visible.** The `openclaw security audit`, `openclaw doctor`, dangerous flag tracking, and explicit `dangerously*` configuration prefix convention demonstrate a philosophy of transparency over obscurity. This is a mature approach that treats the operator as a responsible party rather than trying to hide security complexity.
