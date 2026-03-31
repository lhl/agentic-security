# shisad Security Analysis (Source Code Review)

**Repository:** https://github.com/shisa-ai/shisad
**Commit:** 016b39bce31559c37a31efc39823e0502ebdb3b4
**Point-in-time:** 2026-03-31
**Language:** Python
**Category:** Security-focused
**Prior analysis:** ANALYSIS-shisad.md (docs-only review from 2026-03-05, commit a61a0d8)

## 1. Overview

shisad is a persistent AI agent daemon -- a long-running service that manages conversations, executes tool calls, and takes actions on behalf of a user across multiple channels (CLI, Discord, Slack, Telegram, Matrix). The core thesis is that the LLM proposes actions but the runtime decides what executes, enforced through a multi-layered security architecture.

**Codebase size:** ~46,500 lines of Python source across `src/shisad/`, with ~43,700 lines of tests across `tests/`. The security-specific code (`src/shisad/security/`) comprises ~7,300 lines. There are ~2,200 lines of adversarial tests.

**Actual runtime components (from source):**

- **Daemon** (`daemon/`): The main server process. Hosts handler implementations for all RPC endpoints -- session management, tool execution, confirmation flows, memory, skills, tasks, and admin operations. Built on a Unix socket transport with JSON-RPC.
- **Security subsystem** (`security/`): PEP (Policy Enforcement Point), taint tracking, content firewall (pattern + YARA-based injection classifier), spotlight context builder, credential broker, rate limiter, lockdown manager, risk scorer, provenance verification, and a full control-plane engine with consensus voting.
- **Control plane** (`security/control_plane/`): A metadata-only decision engine with five voters (NetworkVoter, SequenceVoter, ResourceVoter, TraceVoter, ActionMonitorVoter), behavioral sequence analysis, plan commitment/verification, network intelligence monitoring, and append-only audit logging.
- **Executors** (`executors/`): Sandbox orchestrator supporting multiple backends (bwrap, nsjail, container), egress proxy with credential injection, filesystem mount management, and connect-path network isolation.
- **Governance** (`governance/`): Policy merge primitives implementing most-restrictive-wins semantics between server floors and caller requests.
- **Skills** (`skills/`): Plugin system with manifest parsing, multi-engine analysis (YARA + AST + LLM semantic), Ed25519 signature verification with key rotation/revocation, and runtime sandbox governance.
- **Self-modification** (`selfmod/`): Signed artifact lifecycle manager with propose/apply/rollback workflow, integrity verification, and incident recording.
- **Scheduler** (`scheduler/`): Task scheduling with cron, interval, and event triggers, capability snapshots, and confirmation queuing.
- **Memory** (`memory/`): Structured storage with schema-based ingestion, semantic search via embeddings, and taint-aware summarization.
- **Core** (`core/`): Planner (LLM interaction), session management with checkpoints, tool registry with schema validation, evidence store for out-of-band tainted content, context scaffold, transcript tracking, and event bus.
- **Channels** (`channels/`): Multi-channel ingress (Discord, Slack, Telegram, Matrix) with per-channel identity resolution and trust-level assignment.

## 2. Security Architecture

### 2.1 Design Philosophy

The stated philosophy (from `docs/DESIGN-PHILOSOPHY.md` and the codebase's `AGENTS.md`) is "security enables functionality" -- a secure system that cannot do what the user asks is a broken product, not a secure one. The code substantially matches this philosophy:

- The default policy (`runner/policy.default.yaml`) grants all capabilities (`file.read`, `file.write`, `http.request`, `memory.read`, `memory.write`, `message.send`, `shell.exec`) and sets `default_deny: false`, `default_require_confirmation: false`. Security enforcement happens at execution time, not at configuration time.
- The PEP (`security/pep.py`) implements an 8-check pipeline that routes actions to ALLOW, REQUIRE_CONFIRMATION, or REJECT -- it does not simply block everything with taint.
- The lockdown system (`security/lockdown.py`) has four levels (NORMAL, CAUTION, QUARANTINE, FULL_LOCKDOWN) with explicit recovery paths. The code supports `resume()` to return to NORMAL, implementing the "graduated response" design.
- Behavioral tests (`tests/behavioral/`) are treated as a hard gate: "If a security change breaks functionality, the security change is wrong."

**Code-design alignment assessment:** The code genuinely implements the stated philosophy. This is not marketing -- the default-grant approach is evident in the codebase, and the PEP's multi-outcome decision model (not binary allow/deny) is a real implementation, not a stub.

### 2.2 Core Security Primitives

**Taint tracking** (`security/taint.py`): Implemented with concrete `TaintLabel` enum values: `UNTRUSTED`, `SENSITIVE_EMAIL`, `SENSITIVE_FILE`, `SENSITIVE_CALENDAR`, `USER_CREDENTIALS`, `USER_REVIEWED`. Propagation uses worst-case union semantics (`propagate_taint()` at line 104). Ingress labeling (`label_ingress()`) automatically adds `UNTRUSTED` and scans for credential patterns. Tool output labeling (`label_tool_output()`) distinguishes internal tools (clean output) from external tools (UNTRUSTED output). The `evidence.promote` tool returns `USER_REVIEWED` taint, not `TRUSTED` -- this implements the endorsement/taint separation described in docs.

**PEP** (`security/pep.py`): The central enforcement point. The `evaluate()` method (line 134) runs 8 checks in sequence:
1. Tool registry lookup (unknown tools rejected)
2. Per-session/policy tool allowlist
3. Schema validation via `ToolRegistry.validate_call()`
4. Capability check (missing capabilities rejected)
5. Argument DLP scan (regex patterns for API keys, AWS keys, GitHub tokens, Google OAuth)
6. Object-level resource authorization (via `resource_authorizer` callback)
7. Egress enforcement with provenance-aware 5-tier decision: tool-declared -> allowlisted -> user-requested -> untrusted-suggested (confirm) -> unattributed (block)
8. Taint-sink enforcement and risk scoring

**Context scaffold** (`core/context.py`, `security/spotlight.py`): Three-tier prompt construction. `ContextScaffoldEntry` carries `trust_level`, `provenance`, and `source_taint_labels`. The spotlight builder (`build_planner_input_v2()`) places content into TRUSTED (system instructions), INTERNAL/SEMI_TRUSTED (session context with provenance annotations), and UNTRUSTED (data evidence with random delimiters and datamarking). Random delimiters are generated cryptographically (`secrets.token_hex(12)`).

**Control plane engine** (`security/control_plane/engine.py`): Coordinates five independent voters via a consensus voting system. Each voter operates on metadata only -- the engine normalizes voter payloads to strip freeform text (`_normalize_voter_text` truncates to 256 chars). The engine manages plan commitment lifecycle (begin, amend, cancel) and records all decisions to an append-only audit log.

**Evidence store** (`core/evidence.py`): Out-of-band blob storage for tainted content. Evidence is stored with HMAC-based reference IDs (using a 32-byte random salt), session-scoped access validation, automatic TTL-based eviction, and restrictive file permissions (0o700/0o600). Summaries are generated extractively (not by LLM) and passed through the content firewall before inclusion.

**Credential broker** (`security/credentials.py`): Implements the "LLM never sees secrets" pattern. Credentials are replaced with deterministic placeholders (`SHISAD_SECRET_PLACEHOLDER_` + SHA256 hash). Resolution happens at the egress proxy level only, with host-scoped binding. The agent process only ever sees placeholder strings.

### 2.3 Threat Model

Based on code analysis, the implemented threat model covers:

- **Indirect prompt injection (IPI):** Content firewall with pattern + YARA detection, spotlight/datamarking, taint tracking, and PEP enforcement that does not see raw content. 13 YARA rule files in `security/rules/yara/` cover: prompt injection (direct, indirect, unicode/steganography), data exfiltration, credential harvesting, command injection, code execution, tool spoofing, tool chaining abuse, masquerading authority, capability inflation, system manipulation, and autonomy abuse.
- **Data exfiltration:** Egress allowlisting with provenance-aware routing, credential DLP scanning in arguments, taint-sink blocking for write tools with untrusted data, and behavioral sequence detection (exfil_after_read pattern).
- **Tool/skill supply chain:** Ed25519 signature verification, key rotation/revocation, dependency chain verification (source allowlist, pinned versions, digest validation), multi-engine analysis, and runtime sandbox governance.
- **Privilege escalation:** Most-restrictive-wins policy merge (`governance/merge.py`), capability snapshots for scheduled tasks, tool allowlists, and policy-driven sandbox type floors.
- **Persistence attacks:** Behavioral sequence detection for `persistence_attempt` pattern (fs_write + shell_exec targeting .rc/cron/autostart files), lockdown escalation, and sandbox escape detection.
- **Confused deputy:** Provenance-aware egress decisions distinguish user-requested from untrusted-suggested destinations.

**Explicit non-claims:** The PEP is described as "injection-proof" in its docstring, but this applies only to the control-plane -- the PEP itself never processes raw untrusted content. The LLM is explicitly treated as untrusted; spotlighting is an inner layer, not a boundary.

### 2.4 Design-to-Implementation Gap

The prior docs-only analysis identified several "proposed but not implemented" items. Source code review reveals the following status:

**Implemented (closing gaps from prior analysis):**
- The evidence store (described as "ArtifactLedger proposed" in docs) is implemented as `EvidenceStore` in `core/evidence.py` -- functional with session-scoped access, HMAC validation, TTL eviction, and firewall-filtered summaries. It is not the full encrypted "ArtifactLedger" with endorsement tracking from the design docs, but it is a working evidence reference system.
- Plan commitment and trace verification are implemented in `security/control_plane/trace.py`. The `ExecutionTraceVerifier` supports stage1 (pre-content) and stage2 (post-evidence) plans, action counting, TTL expiry, and amendment.
- Consensus voting is implemented with five concrete voters in `security/control_plane/consensus.py`.
- Behavioral sequence analysis is implemented in `security/control_plane/sequence.py` with five default patterns (exfil_after_read, env_then_egress, mass_enum, persistence_attempt, rapid_fire).
- Self-modification safety loop is implemented in `selfmod/manager.py` with propose/apply/rollback, re-inspection before apply, artifact-changed detection, and incident recording.
- Skill signature verification is implemented using Ed25519 in `skills/signatures.py` with keyring management, key rotation/revocation, and dependency chain verification.
- Sandbox orchestration is implemented in `executors/sandbox/` with multiple backends, degraded mode handling, filesystem validation, network boundary enforcement, and escape detection.

**Still gaps (from design docs but not fully in code):**
- **Differential execution** (three-tier comparison with clean evaluator): The `security/control_plane/differential.py` file exists but is a lightweight wrapper, not the full three-tier system described in the design docs.
- **COMMAND/TASK agent separation:** The codebase has session isolation primitives (`core/session.py`), clean-room session support, and task session helpers, but there is no explicit "COMMAND agent" and "TASK agent" as distinct runtime entities with separate contexts. The architectural pattern is approximated through session modes and the evidence store, but the formal two-tier agent split is not a first-class runtime concept.
- **ArtifactLedger with encrypted storage and endorsement tracking:** The evidence store (`core/evidence.py`) stores blobs in plaintext files (not encrypted at rest) and does not implement the mutable endorsement semantics described in the design docs. Evidence references carry taint labels but not endorsement status.
- **Summary barrier as a formal firewall pass:** The content firewall exists and is used for evidence summary generation (`_generate_safe_summary` in `core/evidence.py`), but there is no explicit "second firewall pass" wired into the TASK-to-COMMAND boundary as a mandatory architectural checkpoint.
- **Scoped approval tokens with TTL:** The confirmation system (`daemon/handlers/confirmation.py`) implements per-action confirmation with nonce-based decisions, but does not implement time-scoped, scope-limited pre-approval tokens (e.g., "approve all web fetches to reuters.com for 30 minutes").
- **Process isolation for control plane:** The control plane runs in the same Python process as the agent runtime, separated by a coding convention (metadata-only payloads), not by OS-level process isolation.

## 3. Mapping to Defense Taxonomy

### 3.1 Secure Architectures by Construction

**What shisad does:**

The architecture implements structural separation between the security enforcement layer and the LLM:

- **Control plane / data plane separation:** The PEP (`security/pep.py`) operates entirely on metadata -- tool names, argument schemas, taint labels, capability sets. It never receives raw untrusted content. The `PolicyContext` (line 70) carries only `capabilities`, `taint_labels`, `user_goal_host_patterns`, `untrusted_host_patterns`, `session_id`, `workspace_id`, `user_id`, `action_count`, and `trust_level`. The control-plane engine (`security/control_plane/engine.py`) further normalizes voter payloads with `sanitize_metadata_payload()` and truncates freeform text to 256 characters (`_normalize_voter_text`).
- **Stateless context as safety primitive:** Sessions (`core/session.py`) are isolated execution contexts with checkpoint support (`CheckpointStore`). Clean-room sessions for privileged operations are supported through `SessionMode`.
- **Three-tier context scaffold:** `ContextScaffold` (`core/context.py`, line 69) explicitly separates `trusted_frontmatter`, `internal_entries` (SEMI_TRUSTED with provenance), and `untrusted_entries`, with the spotlight builder enforcing placement rules.

**Not fully implemented:** Formal COMMAND/TASK agent separation as distinct runtime processes. The pattern exists conceptually through session isolation and evidence references, but not as a first-class runtime split with separate LLM contexts.

### 3.2 Access Control and Governance

**What shisad does:**

- **Tool-level permissions:** Each tool in the registry declares `capabilities_required`. The PEP checks these against session capabilities at line 172. Tool policies support `require_confirmation`, `allowed_args` constraints, and per-tool allowlists.
- **Capability-based session model:** Sessions carry a `capabilities: set[Capability]` field. Default capabilities are loaded from policy (`default_capabilities`). Capabilities include `FILE_READ`, `FILE_WRITE`, `HTTP_REQUEST`, `MEMORY_READ`, `MEMORY_WRITE`, `MESSAGE_SEND`, `SHELL_EXEC`, `CALENDAR_WRITE`, `EMAIL_SEND`, `EMAIL_WRITE`.
- **Policy monotonicity:** `governance/merge.py` implements most-restrictive-wins merging. `PolicyMerge.merge()` (line 97) ensures callers can only narrow access, never widen it. For sandbox types, a strict rank ordering (host < container < nsjail < vm) is enforced. For network domains, caller wildcards cannot widen server floors. `is_at_least_as_restrictive()` provides a formal check.
- **Object-level resource authorization:** The PEP's `_check_resource_authorization()` (line 546) inspects arguments ending with `_id` and delegates to a `resource_authorizer` callback for workspace/user-scoped validation. Evidence reference validation uses HMAC-based ref IDs with session-scoped checking (`EvidenceStore.validate_ref_id()`).
- **Declarative YAML policy:** Policy bundles (`security/policy.py`) are Pydantic-validated YAML with typed schema for tools, egress rules, filesystem rules, risk thresholds, rate limits, control-plane settings, sandbox configuration, and skill install policy. The `PolicyLoader` supports SIGHUP-based hot reload (line 375) where only the daemon process can trigger reloads -- the agent cannot reload policy from the data plane.
- **Egress host validation:** `EgressRule` (line 38) validates host patterns and rejects overly broad wildcards (`*` alone is rejected; `*.example.com` requires at least two domain labels).
- **Skill runtime governance:** `skills/sandbox.py` defines `SkillExecutionRequest` with declared network hosts, filesystem paths, shell commands, and environment variables. Runtime authorization checks these against the skill's declared capabilities.

### 3.3 Runtime Verification and Policy Enforcement

**What shisad does:**

- **PEP gating every tool call:** The 8-check PEP pipeline described in 2.2 is the primary enforcement mechanism. Tool calls that pass PEP evaluation then go through the control-plane engine for consensus evaluation.
- **Plan commitment and trace verification:** `ExecutionTraceVerifier` (`security/control_plane/trace.py`) implements pre-content plan commitment. Plans specify allowed action kinds, maximum actions, TTL, and forbidden actions. Each subsequent action is verified against the committed plan. Stage2 amendment requires explicit approval.
- **Consensus voting:** Five voters independently evaluate each action. The `ConsensusVotingSystem` aggregates votes according to configurable thresholds (e.g., 1 approval for LOW risk, 5 approvals for CRITICAL risk). A single BLOCK vote from any voter at HIGH/CRITICAL risk tiers vetoes the action (when `veto_for_high_and_critical` is true, which is the default).
- **Behavioral sequence analysis:** `BehavioralSequenceAnalyzer` (`security/control_plane/sequence.py`) detects suspicious patterns in session action history. Five default patterns are defined: exfil_after_read (fs_read followed by egress within 5 actions), env_then_egress (environment access followed by egress within 3 actions), mass_enum (4+ fs_list operations within 10 actions), persistence_attempt (fs_write + shell_exec targeting .rc/cron/autostart), and rapid_fire (5+ actions within 1 second).
- **Rate limiting:** `RateLimiter` (`security/ratelimit.py`) implements sliding-window limits per-tool, per-user, per-session, and burst detection. Approaching limits triggers confirmation; exceeding limits blocks.
- **Lockdown escalation:** `LockdownManager` (`security/lockdown.py`) implements a 4-level state machine. CAUTION strips side-effect capabilities (email, file write, HTTP, shell, message send). QUARANTINE and FULL_LOCKDOWN block all actions. The escalation is monotonic (only escalates, never auto-de-escalates) unless manually resumed.
- **Graduated response:** The system implements a full graduated response ladder: auto-approve (low risk, clean provenance) -> confirm (medium risk, untrusted provenance, approaching limits) -> deny (high risk, policy violation, unattributed destinations) -> lockdown (genuine multi-signal anomalies).

### 3.4 Detection, Filtering, and Firewalls

**What shisad does:**

- **Content firewall** (`security/firewall/__init__.py`): Normalizes text (Unicode normalization, encoding layer unwrapping), classifies with pattern matching + YARA rules (13 rule files covering injection, exfiltration, credential harvesting, tool spoofing, etc.), and rewrites suspicious fragments. The classifier supports three modes: YARA (when yara-python is available), fallback regex (extracted from YARA files), and base patterns only.
- **Multi-layer encoding detection:** The classifier (`security/firewall/classifier.py`) detects base64-encoded payloads (both direct and split across whitespace/separators) and recursively decodes up to 2 layers, checking for suspicious tokens in the decoded content. This addresses encoding-based injection evasion.
- **Secret detection and redaction:** `security/firewall/secrets.py` and `security/firewall/pii.py` detect and redact secrets (API keys, tokens) and PII in both ingress content and tool arguments. The PEP's `_check_argument_dlp()` (line 511) scans for raw secrets in tool call arguments.
- **Output firewall:** `security/firewall/output.py` provides egress-side filtering.
- **Evidence summary firewall:** `_generate_safe_summary()` in `core/evidence.py` (line 134) runs each candidate summary sentence through the content firewall and falls back to a generic summary if the risk score exceeds the threshold (0.25). This is a form of the "second firewall pass" at the evidence boundary, though not wired as a mandatory TASK-to-COMMAND architectural checkpoint.

### 3.5 Model-Level Hardening

**What shisad does:**

- **Action monitor** (`security/monitor.py`): A deterministic guardrail layer that evaluates proposed actions against the user's goal. High-risk tools used without goal alignment are rejected. Suspicious argument content (containing tokens like "evil.com", "exfiltrate", "bypass", "steal") triggers rejection.
- **Monitor-PEP combination:** `combine_monitor_with_policy()` (line 115) implements the M2 rule set: PEP reject always wins, monitor reject always wins, high risk always requires confirmation, medium risk requires both PEP and monitor agreement.
- **Strict tool-calling contract:** Tools are registered with JSON schemas, capability requirements, and destination declarations. Schema validation happens before any security check.

**Not addressed:** Instruction hierarchy tuning, preference optimization, or representation editing. The LLM is explicitly treated as untrusted -- model-level hardening is not a security boundary.

### 3.6 Boundary Marking and Cryptographic Provenance

**What shisad does:**

- **Spotlighting with random delimiters:** `security/spotlight.py` generates cryptographically random delimiter tokens (`secrets.token_hex(12)`) for each prompt construction. Untrusted content is datamarked (character-level marker insertion) and framed with explicit labels ("DATA EVIDENCE (UNTRUSTED)"). Deterministic mode (for testing) uses SHA256-based delimiters from a seed.
- **Three-tier context placement:** Content is placed in TRUSTED (system instructions area), INTERNAL/SEMI_TRUSTED (session context with provenance annotations), or UNTRUSTED (fenced evidence area) based on trust level. Provenance annotations include source taint labels and provenance chains.
- **Security asset provenance:** `security/provenance.py` implements manifest-based integrity verification for security assets (YARA rules, etc.) with SHA256 hashes and drift detection.
- **Policy integrity:** `PolicyLoader` computes SHA256 hashes of policy files at load time and provides `verify_integrity()` to detect on-disk tampering.
- **Skill signature verification:** Ed25519 signatures on skill manifests with a keyring supporting trust levels ("org", "registry"), key rotation, and revocation. The canonical signature payload is deterministic (sorted JSON).

### 3.7 Formal Methods and Semantics

**Not addressed** in the current implementation. The taint tracking system follows IFC principles (label propagation via union, processing does not clean labels), and the trust levels (UNTRUSTED > SEMI_TRUSTED > TRUSTED) form a lattice, but there is no formal proof of noninterference. As noted in the prior analysis, writing a consistency checker (~200 lines) that verifies all taint-sink rules against the lattice would be relatively low-effort.

## 4. Source Code Analysis

### 4.1 Security-Critical Code Paths

**Tool execution flow (from `daemon/handlers/_impl_tool_execution.py`):**

1. **Session lookup:** Verify session exists and is active.
2. **Tool registry check:** Canonical tool name resolution, tool definition lookup.
3. **Argument merging:** Reserved execution keys are protected from collision.
4. **Skill runtime authorization:** If the tool belongs to a skill, `SkillManager.authorize_runtime()` checks declared capabilities against the skill manifest.
5. **Policy merge:** Server floor merged with caller request via `PolicyMerge.merge()` (most-restrictive-wins).
6. **Egress wildcard enforcement:** Wildcard domains blocked during enforce phase.
7. **Plan commitment:** `ControlPlaneEngine.begin_precontent_plan()` commits a plan before execution.
8. **Control-plane evaluation:** `evaluate_action()` runs all five voters, produces a consensus decision.
9. **Decision routing:** BLOCK -> reject. REQUIRE_CONFIRMATION -> queue pending action with confirmation ID and nonce. ALLOW -> proceed to execution.
10. **Sandbox execution:** For shell tools, the `SandboxOrchestrator` selects backend, validates filesystem access, authorizes network requests, injects credentials, checks for escape signals, optionally creates pre-execution checkpoints, runs the process in isolation, and reports results.

**Confirmation flow (from `daemon/handlers/_impl_confirmation.py`):**

Pending actions are stored with a `decision_nonce` (anti-replay). Confirmation requires matching the nonce. Approved actions are re-evaluated through PEP before execution (no stale approval bypass). Stage2 plan amendment is recorded in the trace verifier.

### 4.2 Input Validation and Sanitization

- **Policy validation:** All policy schemas use Pydantic with strict validators. Egress rules reject empty hosts and overly broad wildcards (`security/policy.py` lines 45-63). Tool names are canonicalized at load time.
- **Content firewall:** Normalizes Unicode, unwraps encoding layers, classifies injection patterns, and rewrites suspicious content. The `decode_text_layers()` function handles recursive base64 decoding.
- **Evidence summary generation:** Extractive (not generative) summaries with per-sentence firewall inspection. HTML content is parsed with a custom parser that skips nav/header/footer/script/style tags and cookie-related elements.
- **Scheduler input validation:** Cron expressions are validated field-by-field with range checks. Interval expressions are parsed with strict format matching. Event filter keys are restricted to alphanumeric tokens.
- **Self-modification input validation:** Artifact names and versions are validated against strict regex patterns. Proposal and change IDs must match `^[a-f0-9]{32}$`. File paths in manifests are validated to prevent path traversal (no absolute paths, no `..` components).

### 4.3 Tool Execution and Sandboxing

The sandbox system (`executors/sandbox/`) is a multi-layered isolation system:

- **Backend selection:** `SandboxPolicyEvaluator` selects from bwrap, nsjail, or container backends based on tool requirements and policy.
- **Filesystem enforcement:** `MountManager` validates read/write paths against the filesystem policy's mount rules and denylist. Path traversal via symlinks or `..` is checked.
- **Network enforcement:** `SandboxNetworkManager` authorizes network requests against the network policy. Allowed domains, private range blocking, IP literal blocking, and credential injection are all handled before process execution. A `revalidate_requests()` pass runs after credential injection to catch any policy violations introduced during resolution.
- **Environment sanitization:** Environment variables are filtered against an allowlist, denied prefixes are stripped, and total key count and byte size limits are enforced.
- **Escape detection:** `_escape_signal_reason()` checks commands for known sandbox escape patterns.
- **Connect-path network isolation:** When available (requires CAP_NET_ADMIN), iptables-based per-process network filtering restricts the sandbox process to only the pre-resolved IP addresses of approved destinations.
- **Resource limits:** CPU shares, memory, timeout, output bytes, and PID limits are applied via process-level controls.
- **Degraded mode handling:** If the selected backend cannot enforce required controls, the system either blocks execution (fail-closed for security-critical tools) or proceeds with degraded enforcement auditing (fail-open for non-critical tools).
- **Pre-execution checkpoints:** For destructive commands, the `SandboxCheckpointManager` captures filesystem snapshots before execution.

### 4.4 Taint Tracking Implementation

**Data structures:** Taint is represented as `set[TaintLabel]` using a `StrEnum` with values: `UNTRUSTED`, `SENSITIVE_EMAIL`, `SENSITIVE_FILE`, `SENSITIVE_CALENDAR`, `USER_CREDENTIALS`, `USER_REVIEWED`.

**Propagation rules (`security/taint.py`):**
- `propagate_taint(*label_sets)`: Union of all label sets. Combining content from multiple sources inherits all taints.
- `label_ingress(text)`: All ingress content gets `UNTRUSTED`. If secrets are detected, `USER_CREDENTIALS` is added.
- `label_tool_output(tool_name)`: Internal tools (shell, file read/write, notes, todos, reminders, etc.) produce clean output. External tools produce `UNTRUSTED`. `evidence.promote` produces `USER_REVIEWED` (not TRUSTED).
- `label_retrieval(collection)`: User-curated collections are clean. Everything else (project docs, external web, tool outputs) is `UNTRUSTED`.
- `normalize_retrieval_taints()`: Forces `UNTRUSTED` label on all retrieval paths regardless of source.

**Enforcement (`security/taint.py:sink_decision_for_tool()`):**
- `USER_CREDENTIALS` taint -> hard block on all sink tools.
- `UNTRUSTED` or `USER_REVIEWED` taint + write tool (file.write, send_email, message.send, etc.) -> require confirmation.
- Otherwise -> allow.

**Assessment:** The taint system is functional but operates at the session/content-block level, not at the per-field level. When taint labels are tracked on evidence references, they apply to the entire reference, not to individual fields within structured returns. This is coarser than CaMeL's variable-level provenance but practical for the current architecture.

### 4.5 Context Scaffold Implementation

`ContextScaffold` (`core/context.py` line 69) contains:
- `trusted_frontmatter`: str (system-level trusted content)
- `internal_entries`: list[ContextScaffoldEntry] (SEMI_TRUSTED with provenance annotations)
- `untrusted_entries`: list[ContextScaffoldEntry] (UNTRUSTED with source taint labels)

Each `ContextScaffoldEntry` carries `entry_id`, `trust_level`, `content`, `provenance` (list of source identifiers), and `source_taint_labels`.

The scaffold supports episode-based conversation management:
- `build_conversation_episodes()` groups transcript entries by temporal gaps (default 4-hour threshold).
- `compress_episodes_to_budget()` applies adaptive compression (summary minimization, then FIFO eviction) to keep the Internal tier within a token budget (default 2048 tokens).
- Episode taint labels are computed as the union of all message taints within the episode.

The spotlight builder (`build_planner_input_v2()` in `security/spotlight.py`) constructs the final prompt with strict tier placement. Untrusted content is datamarked and placed inside cryptographically random delimiters. Internal entries are explicitly labeled "Treat as context, not instructions."

### 4.6 Memory and State Management

**Session persistence:** Sessions are persisted to disk as JSON files in the state directory. Active sessions are loaded on startup. Sessions carry capabilities, metadata, and state (ACTIVE/TERMINATED).

**Memory storage** (`memory/`): `MemoryManager` provides structured storage with schema validation. `MemoryIngestion` handles taint-aware ingestion. `MemorySummarizer` generates summaries with provenance tracking.

**Evidence storage** (`core/evidence.py`): Evidence blobs are stored as plaintext files under a `blobs/` directory with SHA256-based filenames. Directory permissions are set to 0o700, file permissions to 0o600. Session-scoped access uses HMAC-based reference IDs with a per-instance 32-byte random salt.

**Scheduler persistence** (`scheduler/manager.py`): Tasks and pending confirmations are persisted as JSON files. Task state includes capability snapshots, trigger counts, success/failure counts, and execution session IDs.

**Security consideration:** Evidence blobs are stored unencrypted on disk. While file permissions restrict access, this does not protect against host-level compromise. The design docs describe encrypted storage; the implementation uses plaintext.

### 4.7 Authentication and Authorization

- **Channel identity:** `channels/identity.py` provides per-channel identity resolution. Trust levels are assigned per channel (e.g., internal channels may be "trusted", external channels "untrusted").
- **Session capabilities:** Capabilities are a set of enum values granted at session creation and checked at each tool call. The lockdown manager can restrict capabilities dynamically.
- **Resource authorization:** The PEP supports a `resource_authorizer` callback for object-level authorization (checking whether a specific resource ID is accessible in the current workspace/user scope).
- **Credential binding:** Credentials are host-scoped. The PEP's credential check (`_check_credential_refs()` at line 566) verifies: (a) the credential exists, (b) the destination host is in the credential's allowed hosts, and (c) the destination is declared in the tool's destinations. Credential usage is audited.
- **Policy authority:** Policy files are loaded from trusted paths only, with SHA256 integrity verification. Hot reload is SIGHUP-based (signal from daemon process, not from agent). The `register_reload_signal()` method (line 375) documents: "The reload is signal-based, not agent-triggered, to prevent control-plane tampering via the data plane."

## 5. Production Readiness

### 5.1 Maturity Level

**Code quality indicators:**
- Consistent use of Pydantic models for all data structures with strict validation.
- Type annotations throughout (the project runs `mypy src/shisad/`).
- Comprehensive logging with structured metadata (tool names, session IDs, reason codes) but never raw content in security-critical paths.
- Atomic file operations in self-modification (`_write_text_atomic()`).
- Deterministic hashing and canonicalization for signatures.
- Systematic error handling with explicit failure modes (never silent failures in security paths).

**Stability indicators:**
- The `pyproject.toml` and `uv.lock` (342KB) pin all dependencies with SHA256 integrity hashes.
- The codebase includes migration validators (e.g., `_migrate_legacy_tool_overrides` in policy schema) indicating iterative evolution.
- Operational harness (`runner/harness.sh`) and default policy demonstrate deployment-readiness.

**Versioning:** The policy schema uses `version: "1"` and control-plane components reference milestone numbers (M2, M4, M5) indicating iterative development.

### 5.2 Test Coverage

The test suite is substantial:
- **Unit tests** (~100+ test files): Cover PEP, taint, policy, firewall, spotlight, credentials, rate limiting, lockdown, sandbox, governance, skills, self-modification, scheduler, sessions, evidence, and more.
- **Integration tests** (~20+ files): Cover control-plane integration, security loop defense, scheduler execution gates, skill runtime governance, task session isolation, sandbox loops, clean-room workflows, and daemon runtime flows.
- **Adversarial tests** (~14 files, ~2,200 lines): Cover adversarial channels, clean-room attack scenarios, context taint manipulation, control-plane evasion, defense bypass attempts, firewall evasion, hardening verification, sandbox escape attempts, skill attack vectors, content-tool injection, evidence reference manipulation, native tool spoofing, and artifact parser attacks.
- **Behavioral tests** (~5 files): Verify that authorized user operations work correctly -- the "security change must not break functionality" contract.

**Security-specific test patterns observed:**
- Prompt injection payloads in adversarial tests (role impersonation, instruction override, tool spoofing).
- Egress provenance tests verifying user-goal vs untrusted-suggested vs unattributed destination handling.
- Taint propagation verification through multi-step flows.
- Policy merge monotonicity tests (caller cannot widen server floor).
- Sandbox escape detection tests.
- Credential host-scoping tests.

### 5.3 Documentation Quality

The `docs/` directory contains architectural decision records, design philosophy, roadmap, environment variable documentation, tool status tracking, and operational runbooks. The `AGENTS.md` (24,600 bytes) is an unusually thorough contributor guide covering security-first development practices, validation matrices, claim integrity requirements, and definition of done for security features.

### 5.4 Deployment Model

shisad runs as a Unix socket-based daemon. The `runner/` directory provides:
- Default policy (`policy.default.yaml`)
- Environment example (`.env.example`)
- Startup harness (`harness.sh`)
- Operational runbook (`RUNBOOK.md`)

The daemon supports multiple channels (CLI, Discord, Slack, Telegram, Matrix) and can be managed via a control API over the Unix socket.

## 6. Strengths

1. **Genuine defense-in-depth implementation.** Unlike many frameworks that describe layered defense but implement a single check, shisad has independently functional layers: content firewall, PEP with 8 checks, control-plane consensus with 5 voters, behavioral sequence analysis, plan commitment verification, rate limiting, lockdown escalation, and sandbox isolation. Each layer operates on different signals and fails independently.

2. **Metadata-only control plane.** The control-plane engine never sees raw untrusted content. Voter payloads are sanitized and truncated. This is a structurally sound design that prevents prompt injection from reaching the enforcement layer -- not by filtering injection out of content, but by never exposing the enforcement layer to content.

3. **Provenance-aware egress.** The PEP's 5-tier egress decision model (tool-declared / allowlisted / user-requested / untrusted-suggested / unattributed) is more nuanced than any published system. It enables the agent to do what the user asked while blocking injection-driven exfiltration, without blanket-blocking all untrusted-derived actions.

4. **Most-restrictive-wins policy merge.** The `governance/merge.py` implementation is thorough: sandbox type ranking, domain intersection, mount overlap checking, environment key intersection, resource limit minimization. The formal `is_at_least_as_restrictive()` check enables policy audit.

5. **Evidence store with firewall-filtered summaries.** Evidence references keep raw tainted content out of the LLM's context while allowing the agent to reference it. Summaries are generated extractively (not by LLM) and individually inspected by the content firewall before inclusion.

6. **Credential broker with proxy-level injection.** The LLM never sees raw secrets. Credentials are host-scoped and injected only at the egress boundary for pre-approved destinations. This is not just a design pattern -- it is fully implemented with placeholder generation, host-scoped resolution, and PEP-enforced credential binding.

7. **Comprehensive adversarial test suite.** The ~2,200 lines of adversarial tests go beyond typical "does the filter catch this string" testing to cover multi-step attack scenarios, control-plane evasion attempts, and sandbox escape detection.

8. **Self-modification safety loop.** The propose/apply/rollback workflow with re-inspection before apply, artifact-changed detection, signed manifests, and incident recording is a thorough implementation that addresses the "skill as persistence mechanism" threat.

## 7. Gaps and Weaknesses

### Taxonomy Category 3.1 (Secure Architectures)
- **COMMAND/TASK agent separation not a first-class runtime concept.** The design docs describe a formal two-tier agent split with separate contexts and a controlled return boundary. The code has session isolation primitives that could support this pattern, but there is no explicit orchestrator/worker architecture with separate LLM contexts. This is the most significant design-to-implementation gap.

### Taxonomy Category 3.2 (Access Control)
- **`resource_authorizer` callback is optional.** The PEP supports object-level authorization (`_check_resource_authorization()` at line 546) but the callback is optional (`resource_authorizer: Callable[...] | None = None`). If not provided, no object-level authorization is performed. It is unclear from the daemon wiring code whether this callback is typically configured.
- **No MCP/A2A access control.** The codebase does not implement Model Context Protocol or agent-to-agent authorization controls.

### Taxonomy Category 3.3 (Runtime Verification)
- **Plan commitment does not build a dependency graph.** The trace verifier checks action kinds and counts against the committed plan, but does not construct a tool dependency graph (TDG) or verify that each action has a justification path back to the user's goal. An injected action that matches the plan's allowed action kinds would pass verification.
- **No verify-before-commit for irreversible actions.** The system does not run speculative planning or VIGIL-style pre-execution verification. High-risk actions are routed to confirmation (human in the loop) rather than automated pre-execution analysis.

### Taxonomy Category 3.4 (Detection and Filtering)
- **Pattern-based classifier has inherent limitations.** The injection classifier uses regex patterns and YARA rules. While the multi-encoding detection and base64 decoding are thorough, adaptive attackers can craft payloads that evade pattern matching. The `SemanticClassifier` protocol hook exists but no production semantic classifier is included.
- **YARA dependency is optional.** When `yara-python` is not installed, the system falls back to regex patterns extracted from YARA files. The fallback patterns are less precise than compiled YARA rules.

### Taxonomy Category 3.5 (Model-Level Hardening)
- **Action monitor uses simple heuristics.** The `ActionMonitor.evaluate()` method checks for suspicious tokens in arguments and goal-alignment for high-risk tools, but uses simple string matching. The `_SUSPICIOUS_ARG_TOKENS` set is small and easily evaded.

### Taxonomy Category 3.6 (Boundary Marking)
- **Evidence blobs stored unencrypted.** The evidence store writes content as plaintext files. While file permissions are restrictive (0o600), this does not protect against host-level compromise.

### Taxonomy Category 3.7 (Formal Methods)
- **No formal verification.** The taint tracking system follows IFC principles but has no machine-checked proofs.

### Cross-cutting
- **Scheduler PEP integration gap.** The `SchedulerManager.trigger_due()` and `trigger_event()` methods produce `TaskRunRequest` objects with `plan_commitment` and `payload_taint` fields, but the code that consumes these requests (`daemon/handlers/_impl_tasks.py`) needs to be verified for full PEP enforcement of scheduled executions. The capability snapshot mechanism (`can_execute_with_capabilities()`) is implemented, but the end-to-end path from trigger to PEP-gated execution needs validation.
- **In-process control plane.** The metadata boundary between the control plane and agent runtime is enforced by coding convention, not by OS-level process isolation. A sufficiently compromised Python process could theoretically bypass the convention.

## 8. Delta from Prior Analysis

The prior analysis (2026-03-05, commit a61a0d8) was a docs-only review. Source code review at commit 016b39b (2026-03-31) reveals:

### Now implemented (was "gap" or "proposed" in prior analysis)

| Prior Status | Current Status | Component |
|---|---|---|
| "ArtifactLedger proposed" | EvidenceStore implemented (without encryption/endorsement) | `core/evidence.py` |
| "Plan commitment principle-level" | ExecutionTraceVerifier with stage1/stage2 plans | `security/control_plane/trace.py` |
| "Consensus voting designed" | Five-voter ConsensusVotingSystem operational | `security/control_plane/consensus.py` |
| "Behavioral sequence analysis concept" | BehavioralSequenceAnalyzer with 5 default patterns | `security/control_plane/sequence.py` |
| "Self-modification safety loop v0.4 proposal" | SelfModificationManager with propose/apply/rollback | `selfmod/manager.py` |
| "Skill signatures designed" | Ed25519 verification with keyring/rotation/revocation | `skills/signatures.py` |
| "Sandbox planned" | Multi-backend SandboxOrchestrator with network isolation | `executors/sandbox/` |
| "Credential broker concept" | InMemoryCredentialStore with host-scoped proxy injection | `security/credentials.py` |
| "Monitor model concept" | ActionMonitor with deterministic M2 decision rules | `security/monitor.py` |
| "Lockdown concept" | LockdownManager with 4-level state machine | `security/lockdown.py` |

### Significantly more mature than docs suggested

- **PEP implementation** is richer than the docs described: credential reference binding (host-scoped, with tool destination matching), evidence reference validation (HMAC-based), and IP literal / local destination blocking were not prominent in the design docs.
- **Content firewall** includes multi-layer encoding detection (recursive base64 decoding with signal token scanning) that goes beyond what the docs described.
- **Policy system** is a full Pydantic-validated YAML schema with per-tool overrides, sandbox configuration, skill policy, rate limits, control-plane tuning, and hot-reload -- more elaborate than the docs conveyed.
- **Governance merge** is formally specified with `is_at_least_as_restrictive()` audit check, path overlap analysis for filesystem mounts, and domain intersection logic.

### Still gaps from prior analysis

- COMMAND/TASK agent separation remains conceptual, not a first-class runtime split.
- Differential execution is not fully implemented (lightweight wrapper exists, not the three-tier system).
- Evidence encryption at rest is not implemented.
- Scoped approval tokens with TTL are not implemented.
- Process isolation for control plane is not implemented.
- Variable-level provenance tracking is not implemented (block-level only).
- No external benchmark evaluation (AgentDojo, ASB).
- No formal noninterference proof for taint system.

### New findings from source code review

- The consensus voting system is more sophisticated than the docs suggested, with configurable approval thresholds per risk tier, veto semantics, voter timeouts, and an `ActionMonitorVoter` that can integrate LLM-based intent analysis.
- The sandbox orchestrator includes connect-path network isolation (iptables-based per-process filtering) which was not described in the docs.
- The self-modification manager includes incident recording, re-inspection before apply (catches artifact tampering between propose and apply), and atomic staged copies with backup/restore.
- The evidence store implements HTML-aware extractive summarization with cookie/nav/script filtering, per-sentence firewall inspection of summaries, and content-hash deduplication.

## 9. Key Findings

1. **shisad is a real, working security-first agent framework, not vaporware.** The 46,500 lines of source code and 43,700 lines of tests implement the security architecture described in the design docs to a substantial degree. The metadata-only control plane, provenance-aware PEP, taint tracking, evidence store, sandbox orchestration, and self-modification safety loop are all functional, tested code.

2. **The most important remaining gap is the COMMAND/TASK agent separation.** The design docs describe this as the primary architectural defense against taint propagation in multi-step workflows. The code has the building blocks (session isolation, evidence references, context scaffolding) but has not assembled them into a formal two-tier agent runtime. This is the single highest-leverage improvement remaining.

3. **The PEP + control-plane + sandbox stack provides genuine defense-in-depth.** The PEP operates on metadata and cannot be influenced by prompt injection. The control plane runs five independent voters on sanitized metadata. The sandbox provides OS-level isolation for shell execution. These three layers are structurally independent -- compromising one does not compromise the others.

4. **The credential broker implementation is production-ready and noteworthy.** The pattern of placeholder generation, host-scoped proxy injection, and PEP-enforced credential binding is both well-designed and fully implemented. The LLM genuinely never sees raw secrets, and credentials cannot be used for unapproved destinations.

5. **The taint-sink enforcement model correctly separates endorsement from taint.** The `evidence.promote` tool produces `USER_REVIEWED` taint, not `TRUSTED`. Write tools with `USER_REVIEWED` data still require confirmation. This means user approval does not upgrade trust -- the security model holds even when users routinely approve everything. This is a novel contribution not found in published systems.
