# ironclaw Security Analysis

**Repository:** https://github.com/nearai/ironclaw
**Commit:** 27fa292b3354e88a12bd4193c1132f9cc35a8ae2
**Point-in-time:** 2026-03-31
**Language:** Rust
**Category:** Security-focused

## 1. Overview

IronClaw is a self-hosted, open-source personal AI assistant built in Rust, inspired by OpenClaw (a TypeScript predecessor). It is developed by NEAR AI and positions itself as a privacy-first alternative to cloud-hosted AI assistants. The core thesis is "your AI assistant should work for you, not against you" -- all data stays local, encrypted, with no telemetry.

**Architecture components:**

- **Agent Loop** (`src/agent/`): Main message handling, job coordination, session management, intent routing, and scheduling of parallel jobs.
- **Channels** (`src/channels/`): Multi-channel input via REPL, HTTP webhooks, WASM-based channels (Telegram, Slack, Discord, WhatsApp, Feishu), and a web gateway with SSE/WebSocket streaming.
- **Tool System** (`src/tools/`): Extensible tool registry with built-in tools (shell, HTTP, file, memory, etc.), WASM-sandboxed tools (via wasmtime), MCP protocol client, and a dynamic tool builder.
- **Safety Layer** (`crates/ironclaw_safety/`): Extracted crate for prompt injection defense, content sanitization, policy enforcement, and secret leak detection.
- **Secrets Management** (`src/secrets/`): AES-256-GCM encrypted secret storage with OS keychain integration for master key, per-secret key derivation via HKDF-SHA256.
- **Docker Sandbox** (`src/sandbox/`): Container-based execution with tiered policies (ReadOnly/WorkspaceWrite/FullAccess), network proxying with domain allowlists, and credential injection at the proxy boundary.
- **WASM Sandbox** (`src/tools/wasm/`): wasmtime-based execution with capability-based permissions, endpoint allowlisting, fuel metering, memory limits, credential injection, and leak detection.
- **Workspace/Memory** (`src/workspace/`): Persistent memory with hybrid search (FTS + vector via RRF), PostgreSQL or libSQL backends.
- **Orchestrator** (`src/orchestrator/`): Internal HTTP API for sandbox containers with per-job bearer token authentication.
- **LLM Integration** (`src/llm/`): Multi-provider support (NEAR AI, Anthropic, OpenAI, Gemini, Ollama, AWS Bedrock, etc.) with smart routing, failover, and circuit breaking.

The system is designed as a single Rust binary (v0.22.0, Rust 2024 edition, MSRV 1.92) with PostgreSQL 15+ and pgvector for persistence, or libSQL/Turso as a lighter alternative.

## 2. Security Architecture

### 2.1 Design Philosophy

IronClaw's security philosophy centers on several explicit principles:

1. **Data sovereignty**: All data is stored locally in the user's own database, encrypted at rest. No telemetry, analytics, or data sharing.
2. **Defense in depth**: Multiple security layers (sanitization, validation, policy, leak detection) applied at different points in the data flow.
3. **Zero-exposure credential model**: Secrets are stored encrypted and injected at transit boundaries. WASM tools and Docker containers never see raw credential values.
4. **Capability-based least privilege**: WASM tools start with no permissions and must be explicitly granted capabilities (HTTP, workspace read, tool invocation, secret existence checks).
5. **Untrusted by default**: Docker containers, external services, and WASM modules are treated as untrusted. The orchestrator validates all interactions.

### 2.2 Core Security Primitives

**WASM Sandbox (wasmtime):**
- Capability-based permission system (`src/tools/wasm/capabilities.rs`) -- tools get `Capabilities::none()` by default; HTTP, workspace read, tool invoke, and secrets must be explicitly granted.
- Fuel metering: 10M instruction default limit (`src/tools/wasm/limits.rs`, lines 13-14).
- Memory limiting: 10 MB default via `WasmResourceLimiter` implementing wasmtime's `ResourceLimiter` trait.
- Execution timeout: 60-second wall-clock default.
- Endpoint allowlisting with path traversal protection (`src/tools/wasm/allowlist.rs`): normalizes paths, rejects encoded separators, rejects userinfo in URLs.
- Credential injection at host boundary (`src/tools/wasm/credential_injector.rs`): WASM never sees secret values; credentials are decrypted and injected into HTTP requests by the host runtime.
- Per-tool rate limiting (`src/tools/wasm/rate_limiter.rs`).

**Docker Sandbox:**
- Three-tier policy system: ReadOnly (ro workspace, proxied network), WorkspaceWrite (rw workspace, proxied network), FullAccess (full host, explicit double opt-in required).
- Network proxy with domain allowlist (`src/sandbox/proxy/`): intercepts all container network requests, enforces allowlist, injects credentials.
- Per-job bearer token auth (`src/orchestrator/auth.rs`): cryptographically random 32-byte tokens, constant-time comparison via `subtle::ConstantTimeEq`, job-scoped, ephemeral (in-memory only).

**Safety Layer (`crates/ironclaw_safety/`):**
- `Sanitizer`: Aho-Corasick multi-pattern matching for 18+ injection patterns (instruction override, role manipulation, system message injection, special tokens, code injection markers) plus regex patterns (base64 payloads, eval/exec, null bytes). Case-insensitive detection.
- `Validator`: Input length limits (100KB default), null byte detection, forbidden pattern matching, excessive whitespace/repetition warnings, recursive JSON parameter validation with depth cap (32).
- `Policy`: Regex-based rules with four severity levels (Critical/High/Medium/Low) and four actions (Block/Warn/Review/Sanitize). Default rules cover system file access, crypto private keys, SQL patterns, shell injection, encoded exploits, and obfuscation.
- `LeakDetector`: 16 patterns for API key/token/credential detection (OpenAI, Anthropic, AWS, GitHub, Stripe, NEAR AI, PEM/SSH keys, Google, Slack, Twilio, SendGrid, Bearer tokens, auth headers, high-entropy hex). Scanning at two points: before outbound requests (URL, headers, body) and after responses/outputs. Actions: Block, Redact, or Warn.
- `wrap_for_llm()` / `wrap_external_content()`: XML-boundary wrapping with delimiter escape (zero-width space injection) to prevent boundary injection attacks.

**Cryptography:**
- AES-256-GCM authenticated encryption for secrets at rest (`src/secrets/crypto.rs`).
- HKDF-SHA256 per-secret key derivation from a master key.
- Random 32-byte salts per secret (so identical plaintexts produce different ciphertexts).
- Master key stored in OS keychain (macOS Keychain, Linux GNOME Keyring/KWallet).
- Ed25519 signature verification for webhook authentication (`ed25519-dalek`).
- HMAC-SHA256 for Slack-style webhook signing.
- BLAKE3 hashing available.
- `secrecy` crate for sensitive value handling (zeroize on drop).
- `jsonwebtoken` for JWT operations.

**Credential Detection:**
- `credential_detect.rs`: Heuristic detection of manually-provided credentials in HTTP request parameters (header names, header value prefixes, URL query parameters, URL userinfo).

### 2.3 Threat Model

**Explicitly addressed threats:**

1. **Prompt injection via tool output**: Multi-layer defense (sanitizer + policy + boundary wrapping). Tool outputs are wrapped in `<tool_output>` XML with delimiter escape before reaching the LLM.
2. **Secret exfiltration by WASM tools**: Leak detection scans outbound HTTP requests (URL, headers, body) and tool outputs. Secrets are never exposed to WASM code; injected at host boundary.
3. **Unauthorized API access by sandboxed code**: Endpoint allowlisting (host + path prefix + method) in both WASM and Docker sandboxes.
4. **Resource exhaustion by untrusted code**: Fuel metering, memory limits, execution timeouts in WASM; memory limits, CPU shares, timeouts in Docker.
5. **Path traversal attacks**: URL path normalization with percent-encoding validation, `..` resolution, encoded separator rejection.
6. **Host confusion/redirect attacks**: Userinfo (`user:pass@host`) rejection in URL parsing to prevent allowlist bypass.
7. **Data exfiltration via secrets in user input**: Inbound secret scanning prevents users from accidentally sending credentials to the LLM.
8. **Autonomous agent abuse**: Explicit tool denylist for autonomous jobs/routines (`src/tools/autonomy.rs`) -- blocks routine/job creation, tool install, secret management, restart.
9. **Container escape / cross-job access**: Per-job bearer tokens scoped to specific job IDs, ephemeral in-memory storage, constant-time comparison.
10. **External content injection**: `wrap_external_content()` wraps untrusted data (emails, webhooks, web pages) with security notices instructing the LLM to treat content as data, not instructions.

**Implicitly addressed threats:**

- Memory safety: Rust's ownership system prevents buffer overflows, use-after-free, etc.
- Supply chain: `deny.toml` for cargo-deny license/advisory checking.
- Regex DoS: Adversarial tests verify all regex patterns complete within 100-500ms on 100KB inputs.

**Out of scope / not addressed:**

- Trusted Execution Environments (TEE): Despite the description mentioning "privacy and security," there is no TEE/enclave support (no SGX, TDX, SEV, or similar).
- End-to-end encryption of LLM communication: Relies on HTTPS/TLS to LLM providers; no additional encryption layer.
- Formal verification of security properties.
- Multi-tenant isolation at the database level (single-user design, though multi-tenant web gateway support exists).
- Model-level hardening (no instruction hierarchy, preference optimization, or representation editing).

## 3. Mapping to Defense Taxonomy

### 3.1 Secure Architectures by Construction

IronClaw implements a partial separation of trusted and untrusted components:

- **Trusted host / untrusted sandbox**: The Rust host process is trusted; WASM tools and Docker containers are untrusted. The host mediates all external access (HTTP, secrets, tool invocation) through capability checks.
- **Control plane / data plane separation**: The orchestrator (`src/orchestrator/`) acts as a control plane for Docker sandbox containers, providing LLM proxying, event APIs, and per-job auth. Workers communicate only through the orchestrator's API endpoints.
- **No CaMeL-style IFC or dual-LLM patterns**: The agent loop uses a single LLM for both planning and execution. There is no formal information flow control between trusted and untrusted data paths.
- **Boundary wrapping**: Tool outputs and external content are structurally delimited (`<tool_output>`, `--- BEGIN EXTERNAL CONTENT ---`) before reaching the LLM, creating a data/instruction boundary.

### 3.2 Access Control and Governance

This is one of IronClaw's strongest areas:

- **Capability-based permissions for WASM tools** (`src/tools/wasm/capabilities.rs`): Default-deny; each capability (HTTP, workspace read, tool invoke, secrets) must be explicitly granted via `.capabilities.json` sidecar files. HTTP capability includes specific endpoint allowlists, credential mappings, rate limits, body size limits, and timeouts.
- **Endpoint allowlisting** (`src/tools/wasm/allowlist.rs`): Host + path prefix + HTTP method matching with wildcard support. HTTPS required by default.
- **Per-job bearer token auth** (`src/orchestrator/auth.rs`): Cryptographic tokens scoped to individual jobs, with constant-time validation and ephemeral storage.
- **Secret access control**: `SecretsStore::is_accessible()` checks glob-pattern-based access lists before returning credentials. WASM secrets capability only allows existence checks, never value reads.
- **Tool approval flow**: The agent has tool approval mechanisms (referenced in AGENTS.md as "special paths").
- **Autonomous tool denylist** (`src/tools/autonomy.rs`): 17 sensitive tools (routine management, job creation, tool install, secret management, restart) are blocked for autonomous/background execution.
- **Skills trust model**: Two tiers -- Trusted (user-placed, full tool access) vs Installed (registry, read-only tools) with attenuation (`src/skills/attenuation.rs`).
- **Webhook authentication** (`src/channels/wasm/signature.rs`): Ed25519 and HMAC-SHA256 signature verification for incoming webhooks.

### 3.3 Runtime Verification and Policy Enforcement

- **Policy engine** (`crates/ironclaw_safety/src/policy.rs`): Regex-based rules with Block/Warn/Review/Sanitize actions. Default policy includes 7 rules covering system file access, crypto private keys, SQL patterns, shell injection, encoded exploits, excessive URLs, and obfuscation detection.
- **Sanitization pipeline** (`crates/ironclaw_safety/src/sanitizer.rs`): All tool output passes through `SafetyLayer::sanitize_tool_output()` which runs leak detection, policy checking, and content sanitization in sequence. Critical-severity matches trigger content escaping.
- **Input validation** (`crates/ironclaw_safety/src/validator.rs`): Validates length, encoding, forbidden patterns, whitespace ratio, and character repetition. Recursive JSON validation with depth cap.
- **Inbound secret scanning**: `SafetyLayer::scan_inbound_for_secrets()` rejects user messages that contain detected API keys/tokens before they reach the LLM.
- **Tool output truncation**: Outputs exceeding `max_output_length` are truncated at safe character boundaries (multi-byte aware).
- **No explicit goal-hijacking detection or trace-level analysis**: The system detects individual injection patterns but does not analyze conversation-level behavioral deviation.

### 3.4 Detection, Filtering, and Firewalls

- **Prompt injection detection**: Aho-Corasick multi-pattern matching for 18+ literal patterns (case-insensitive) plus 4 regex patterns. Covers instruction override, role manipulation, system message injection, special token injection, code block injection.
- **Secret leak detection** (`crates/ironclaw_safety/src/leak_detector.rs`): 16 regex patterns covering major API key formats (OpenAI, Anthropic, AWS, GitHub, Stripe, Slack, Google, etc.) plus generic patterns (Bearer tokens, auth headers, high-entropy hex).
- **Credential detection in HTTP parameters** (`crates/ironclaw_safety/src/credential_detect.rs`): Detects auth headers, Bearer/Basic prefixes, credential query parameters, and URL userinfo.
- **Boundary delimiter escaping**: Zero-width space injection to prevent `</tool_output>` and `--- END EXTERNAL CONTENT ---` boundary escape attacks.
- **Known bypass documentation**: Tests explicitly document known bypasses (ZWSP/ZWJ/ZWNJ in literal patterns, percent-encoding in URL scanning) -- a commendable transparency practice.
- **No ML-based classifier**: All detection is pattern-based (regex + Aho-Corasick). No neural prompt injection classifier or fine-tuned model.

### 3.5 Model-Level Hardening

Not addressed. IronClaw operates at the application layer and does not modify or fine-tune the underlying LLM. There is no instruction hierarchy enforcement, preference optimization, or representation editing. The framework is model-agnostic and supports 10+ LLM providers.

### 3.6 Boundary Marking and Cryptographic Provenance

- **Structural boundary marking**: `wrap_for_llm()` wraps tool output in `<tool_output name="...">` XML tags. `wrap_external_content()` wraps external data with `SECURITY NOTICE` header and `--- BEGIN/END EXTERNAL CONTENT ---` delimiters.
- **Delimiter injection prevention**: Both wrapping functions escape closing delimiters in content (zero-width space insertion) to prevent boundary escape attacks. Tests verify round-trip integrity.
- **Webhook signature verification**: Ed25519 (`ed25519-dalek`) and HMAC-SHA256 for authenticating incoming webhooks.
- **No signed prompts or hash-based prompt authentication**: The boundary marking is structural (XML/text delimiters), not cryptographic. There is no cryptographic signing of system prompts or tool outputs.

### 3.7 Formal Methods and Semantics

Not addressed. There is no formal verification, type-level security guarantees, or information flow control proofs. However, the codebase has several properties that support correctness:

- **Rust's type system**: Strong typing, ownership model, and absence of `unwrap()`/`expect()` in production code (enforced by clippy rules).
- **Fuzz testing** (`crates/ironclaw_safety/fuzz/`): 5 fuzz targets covering safety sanitizer, validator, leak detector, credential detection, and config environment parsing with seed corpora.
- **Adversarial test suites**: Extensive adversarial tests for Unicode edge cases (ZWSP, ZWJ, ZWNJ, RTL override, combining diacriticals, BOM), control characters, regex backtracking performance, and multi-byte boundary handling.

## 4. Source Code Analysis

### 4.1 Security-Critical Code Paths

**Tool output flow:**
1. Tool executes and returns `ToolOutput` (`src/tools/tool.rs`).
2. If `requires_sanitization()` returns true, output passes through `SafetyLayer::sanitize_tool_output()` (`crates/ironclaw_safety/src/lib.rs`, lines 54-135):
   a. Length check and truncation (multi-byte aware, lines 57-81).
   b. Leak detection via `LeakDetector::scan_and_clean()` (lines 88-101).
   c. Policy check -- Block action blocks entire output (lines 106-115), Sanitize action forces sanitization (lines 116-121).
   d. If injection check enabled or policy requires: `Sanitizer::sanitize()` (lines 124-127).
3. Output wrapped in `<tool_output>` XML via `wrap_for_llm()` (lines 169-175).
4. Wrapped output injected into LLM conversation context.

**WASM HTTP request flow:**
1. WASM calls HTTP host function.
2. Allowlist validation (`AllowlistValidator::validate()`) -- checks HTTPS requirement, parses URL, normalizes path, matches against endpoint patterns.
3. Leak scan on request (`LeakDetector::scan_http_request()`) -- scans URL, headers, and body.
4. Credential injection (`CredentialInjector::inject()`) -- decrypts secret from store, injects into headers/query params based on `CredentialLocation`.
5. HTTP request executed.
6. Leak scan on response.
7. Response returned to WASM.

**Docker sandbox execution flow:**
1. Job dispatched to orchestrator (`src/orchestrator/job_manager.rs`).
2. Per-job bearer token generated (`TokenStore::create_token()`).
3. Container created with resource limits and network proxy.
4. All container HTTP traffic routed through proxy (`src/sandbox/proxy/`).
5. Proxy evaluates domain allowlist, injects credentials for matching hosts.
6. Worker communicates with orchestrator via authenticated API.
7. On completion: token revoked, credential grants cleared, container cleaned up.

### 4.2 Input Validation and Sanitization

- **Validator** (`crates/ironclaw_safety/src/validator.rs`): 100KB max input by default, null byte rejection, forbidden pattern matching, whitespace ratio warning (>90% over 100 chars), character repetition warning (>20 consecutive identical chars).
- **Tool parameter validation**: Recursive JSON traversal with 32-level depth cap to prevent stack overflow (`validator.rs`, lines 197-245).
- **URL validation** (`src/tools/wasm/allowlist.rs`): Scheme validation (http/https only), userinfo rejection, percent-encoding validation, path normalization with `..` resolution, encoded separator rejection.
- **Shell environment scrubbing**: The shell tool scrubs sensitive environment variables before executing commands (referenced in `.claude/rules/safety-and-sandbox.md`).

### 4.3 Tool Execution and Sandboxing

**WASM sandbox** (wasmtime Component Model):
- Module compilation and caching (`src/tools/wasm/runtime.rs`).
- `WasmResourceLimiter` enforces memory limits (10MB default) via wasmtime's `ResourceLimiter` trait (`src/tools/wasm/limits.rs`, lines 63-158).
- Fuel metering enabled by default (10M instructions) via `FuelConfig` (`src/tools/wasm/limits.rs`, lines 162-194).
- Host functions provide controlled access to logging, time, and workspace (`src/tools/wasm/host.rs`).
- Capabilities are all-or-nothing per type; no partial grants within a capability type.
- WASM binary validation via `wasmparser` crate.

**Docker sandbox:**
- Container lifecycle managed via `bollard` Docker API (`src/sandbox/container.rs`).
- Three-tier policy with double opt-in for FullAccess (`SandboxConfig::allow_full_access` must be explicitly set, `src/sandbox/config.rs`, lines 17-19).
- Network proxy intercepts all traffic, enforcing domain allowlist with default entries for common package registries, documentation sites, version control, and LLM APIs (lines 151-177).
- Default credential mappings for OpenAI, Anthropic, and NEAR AI APIs (lines 180-188).
- Reaper task (`src/orchestrator/reaper.rs`) cleans up orphaned containers.

### 4.4 Memory and State Management

- **Session state**: Managed via `SessionManager` (`src/agent/session_manager.rs`) with job context isolation (`src/context/`).
- **Database persistence**: Dual-backend (PostgreSQL + libSQL/Turso) with SQL migrations (`migrations/`). Both backends implement the same `Database` trait.
- **Secrets persistence**: Encrypted at rest in the database. Master key stored in OS keychain (macOS: `security-framework`, Linux: `secret-service` via D-Bus/zbus).
- **In-memory token store**: Per-job bearer tokens are ephemeral, never persisted to disk (`src/orchestrator/auth.rs`).
- **Workspace privacy**: `src/workspace/privacy.rs` exists (not read in detail but present in the codebase).
- **Sensitive data in logs**: The project enforces redaction of tool parameters and outputs before logging or broadcasting via SSE/WebSocket (`src/tools/redaction.rs`). The `SecretsCrypto` Debug implementation shows `[REDACTED]` for the master key.

### 4.5 Authentication and Authorization

- **NEAR AI OAuth**: Browser-based OAuth flow for NEAR AI authentication (configured during onboarding wizard).
- **Per-job bearer tokens**: 32-byte cryptographically random tokens, hex-encoded (64 chars), validated with constant-time comparison (`subtle::ConstantTimeEq`), scoped to individual job UUIDs.
- **Webhook authentication**: Multiple mechanisms -- shared-secret header validation, Ed25519 signature verification (Discord-style), HMAC-SHA256 signing (Slack-style with optional timestamp headers).
- **Web gateway auth**: `src/channels/web/auth.rs` handles authentication for the browser-facing API.
- **Secret access control**: Glob-pattern-based access lists (`is_accessible()` in `SecretsStore`). WASM tools can only check secret existence, never read values.
- **User isolation**: Secrets are scoped to user IDs (`user_id` in all `SecretsStore` operations). Tests verify cross-user isolation (`test_user_isolation` in `src/secrets/store.rs`).
- **Tenant support**: `src/tenant.rs` and multi-tenant integration tests (`tests/multi_tenant_integration.rs`, `tests/multi_tenant_system_prompt.rs`) indicate multi-tenant capability.

## 5. Production Readiness

### 5.1 Maturity Level

- **Version**: 0.22.0 (pre-1.0, but substantial feature set).
- **Language**: Rust 2024 edition, MSRV 1.92, with `strip = true` for release builds and thin LTO for distribution.
- **Code quality**: Strict clippy rules (zero warnings enforced), no `.unwrap()`/`.expect()` in production code, `thiserror` for error types, strong typing throughout.
- **Dependencies**: Well-chosen ecosystem crates (tokio, axum, wasmtime, serde, aes-gcm, hkdf). `deny.toml` for supply chain checks.
- **Multi-platform**: Builds for 7 targets (macOS arm64/x86_64, Linux arm64/x86_64/musl, Windows x86_64). Windows MSI installer, Homebrew, shell/PowerShell scripts.
- **Safety crate extraction**: Security-critical code extracted to `crates/ironclaw_safety/` with its own Cargo.toml, enabling independent testing and fuzzing.

### 5.2 Test Coverage

Extensive testing at multiple tiers:

- **Unit tests**: Every security-critical module has comprehensive `mod tests {}` blocks with both normal and adversarial cases. The `ironclaw_safety` crate alone has ~100+ test functions.
- **Adversarial tests**: Dedicated `adversarial` submodules in sanitizer, policy, validator, leak detector, and credential detect testing Unicode edge cases (ZWSP, ZWJ, ZWNJ, RTL override, combining diacriticals, BOM), control characters, regex backtracking performance (100KB near-miss inputs with 100-500ms thresholds), and multi-byte boundary handling.
- **Fuzz testing**: 5 fuzz targets in `crates/ironclaw_safety/fuzz/` (sanitizer, validator, leak detector, credential detect, config env) plus 1 in `fuzz/` (tool params), with seed corpora.
- **Integration tests**: ~60+ test files in `tests/` covering workspace, heartbeat, gateway, pairing, tool approval, safety layer, multi-tenant, import, and more.
- **E2E tests**: `tests/e2e/` with Python/Playwright scenarios.
- **Benchmarks**: `benches/safety_check.rs` and `benches/safety_pipeline.rs` for performance regression tracking.
- **CI**: GitHub Actions workflows for code style, testing, coverage, e2e, and release.

### 5.3 Documentation Quality

- **README**: Comprehensive with philosophy, features, security section, architecture diagram, and installation instructions.
- **CLAUDE.md**: Detailed development guide with project structure, module specs, and coding conventions.
- **AGENTS.md**: Agent-oriented quick-start contract.
- **Module specs**: `CLAUDE.md` files within `src/agent/`, `src/channels/web/`, `src/db/`, `src/llm/`, and README files in `src/setup/`, `src/tools/`, `src/workspace/`.
- **Inline documentation**: Security-relevant modules have extensive doc comments with ASCII diagrams of data flows.
- **FEATURE_PARITY.md**: Tracking matrix against OpenClaw reference implementation.
- **COVERAGE_PLAN.md**: Detailed test coverage plan.
- **CONTRIBUTING.md**: Contributor guidelines.
- **Multi-language READMEs**: English, Chinese, Russian, Japanese.

### 5.4 Deployment Model

- **Single binary**: Compiles to a single Rust binary.
- **Docker support**: `Dockerfile`, `Dockerfile.test`, `Dockerfile.worker`, `docker-compose.yml`, `docker/sandbox.Dockerfile`.
- **System service**: `src/service.rs` supports launchd (macOS) and systemd (Linux) daemon installation.
- **Deploy directory**: `deploy/` with systemd service files, Cloud SQL Proxy integration, and setup scripts.
- **Tunnel support**: Cloudflare, ngrok, Tailscale, and custom tunnel providers for public internet exposure (`src/tunnel/`).

## 6. Strengths

1. **Comprehensive credential protection model**: The zero-exposure design where WASM tools never see raw secrets, combined with leak detection at both request and response boundaries, is notably thorough. Credential injection at the host boundary is well-implemented with support for Bearer, Basic, custom header, and query parameter locations.

2. **WASM sandbox with capability-based permissions**: Default-deny capabilities with explicit opt-in for HTTP (with endpoint allowlists), workspace read, tool invoke, and secrets (existence-only) is a strong least-privilege implementation. The combination of fuel metering, memory limits, and execution timeouts provides resource protection.

3. **Well-engineered URL/path validation**: The allowlist validator's handling of path traversal (percent-encoding normalization, `..` resolution, encoded separator rejection, userinfo rejection) demonstrates security-aware URL handling that prevents common bypass techniques.

4. **Adversarial testing discipline**: The explicit testing of Unicode bypass vectors (ZWSP, ZWJ, ZWNJ, RTL override, combining diacriticals) and regex performance on near-miss inputs, with tests that document known limitations rather than hiding them, is an exemplary practice.

5. **Defense-in-depth layering**: Multiple independent security mechanisms (sanitizer, validator, policy, leak detector, allowlist, capability system, credential injector, boundary wrapping) provide redundancy -- no single component failure compromises the entire system.

6. **Extracted safety crate with fuzzing**: Moving security-critical code to an independent crate with its own fuzz targets enables focused security testing and makes the security boundary explicit.

## 7. Gaps and Weaknesses

1. **No TEE/enclave support** (Taxonomy 3.1): Despite being described as "focused on privacy and security," IronClaw has no Trusted Execution Environment integration. Data is encrypted at rest and in transit (HTTPS), but there is no hardware-backed confidential computing. The master key is stored in the OS keychain, which is adequate for personal use but not for adversarial environments.

2. **Pattern-based detection only** (Taxonomy 3.4): All prompt injection detection relies on regex and literal string matching. There is no ML-based classifier, embedding-similarity detection, or perplexity-based analysis. The tests explicitly document known bypasses (zero-width characters breaking literal matches, percent-encoding bypassing URL scanning). A sophisticated attacker can evade these patterns.

3. **No model-level hardening** (Taxonomy 3.5): IronClaw is entirely model-agnostic and applies no model-level defenses. It cannot enforce instruction hierarchy, apply preference optimization against jailbreaks, or use representation editing. Defense depends entirely on application-layer filtering.

4. **No formal verification** (Taxonomy 3.7): While Rust's type system provides memory safety, there are no formal proofs of security properties like information flow control, capability confinement, or policy completeness.

5. **Single-LLM architecture** (Taxonomy 3.1): The agent loop uses one LLM for both reasoning and action. There is no trusted planner / untrusted executor separation, no dual-LLM verification, and no independent safety checker.

6. **FullAccess sandbox policy bypasses all protection** (Taxonomy 3.2): The `FullAccess` policy executes commands directly on the host with `sh -c` and the agent process's full privileges. While it requires double opt-in (`SANDBOX_ALLOW_FULL_ACCESS=true`), it creates a complete security bypass. The code documents the "BLAST RADIUS" explicitly (`src/sandbox/config.rs`, lines 76-87).

7. **Known Unicode bypass vectors** (Taxonomy 3.4): Zero-width space, zero-width joiner, and zero-width non-joiner characters can break both Aho-Corasick literal matching and regex-based detection. While documented in tests, these are exploitable by knowledgeable attackers.

8. **No conversation-level behavioral analysis** (Taxonomy 3.3): Detection operates at the individual content level (per-output, per-input). There is no trace-level analysis for goal hijacking, multi-turn manipulation, or gradual prompt injection.

## 8. Key Findings

- **IronClaw has one of the most thorough credential protection architectures among open-source AI agent frameworks.** The zero-exposure model (WASM tools never see secrets, credential injection at host boundary, leak detection at request and response boundaries, inbound secret scanning) is well-designed and well-implemented. The capability-based WASM sandbox with default-deny permissions is a strong security primitive.

- **The defense-in-depth approach is genuine, not superficial.** Multiple independent security layers (sanitizer, validator, policy engine, leak detector, allowlist, capability system, boundary wrapping) are each substantive, well-tested, and have clear separation of concerns. The extraction of safety logic into a dedicated crate with fuzzing is a mature engineering practice.

- **Detection is purely pattern-based, which creates a ceiling on effectiveness.** All prompt injection and leak detection relies on regex and literal string matching. Known bypasses via zero-width Unicode characters and percent-encoding are documented but unfixed (they may be fundamentally difficult to address with pattern matching). No ML-based classification is used.

- **Despite the "privacy and security" marketing, there is no TEE/confidential computing support.** IronClaw provides strong application-level security (encryption at rest, capability-based sandboxing, credential protection) but does not extend to hardware-backed security guarantees. For personal use this is appropriate; for high-assurance environments it falls short.

- **The adversarial testing methodology is exemplary and rare in this space.** The practice of writing tests that explicitly document known bypasses (with comments explaining why they exist) rather than hiding limitations, combined with Unicode edge case testing, regex performance testing on adversarial inputs, and fuzz testing with seed corpora, sets a high bar that most frameworks do not meet.
