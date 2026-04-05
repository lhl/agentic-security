# shisad v0.6.1 Security Analysis (Source Code Review)

**Repository:** https://github.com/shisa-ai/shisad
**Version:** v0.6.1 (released 2026-04-05)
**Point-in-time:** 2026-04-06
**Language:** Python
**Category:** Security-focused
**Prior analyses:** ANALYSIS-shisad.md (docs-only, 2026-03-05, commit a61a0d8), ANALYSIS-shisad-v0.5.md (source code review, 2026-03-31, commit 016b39b)

## 1. Overview

shisad is a persistent AI agent daemon -- a long-running service that manages conversations, executes tool calls, and takes actions on behalf of a user across multiple channels (CLI, Discord, Slack, Telegram, Matrix). The core thesis is that the LLM proposes actions but the runtime decides what executes, enforced through a multi-layered security architecture.

v0.6.0 was the "orchestration-foundation release" -- converting the flat session model into a formal two-tier COMMAND/TASK runtime with explicit trust boundaries, hardening the supply chain, and expanding the tool surface to browser automation. v0.6.1 is a security-hardening follow-up that closes three gaps identified in the v0.6.0 analysis: control-plane process isolation, ML-based injection classification (PromptGuard 2), and Tool Dependency Graph verification with phantom action detection.

**Codebase size (v0.6.1):** ~55,000 lines of Python source across `src/shisad/`, ~55,000 lines of tests across `tests/`. 1,522 test functions (86 adversarial, 182 integration, 1,182 unit, 70 behavioral). 374 Python files. Test/source ratio: 1.0x.

**Delta from v0.6.0:** 29 commits, 92 files touched, 8,805 insertions, 299 deletions. Five security hardening deliveries (H1-H5) plus YARA compile fix and delegated task count hardening.

**Delta from v0.5:** 87 commits, 284 files touched, 25,547 insertions, 3,194 deletions. Six milestone deliveries (G0, M1-M6), supply chain hardening, and five security hardening deliveries (H1-H5).

**What changed (executive summary):**

| Area | v0.5 Status | v0.6.0 Status | v0.6.1 Status |
|------|-------------|---------------|---------------|
| COMMAND/TASK separation | Conceptual; session primitives only | First-class runtime: `SessionRole` enum, immutable `TaskEnvelope`, mandatory summary-firewall checkpoint | Unchanged from v0.6.0 |
| Control plane isolation | In-process, coding convention | In-process, coding convention | **Process-isolated sidecar**: the policy-decision engine runs in a separate OS process, communicating via Unix socket JSON-RPC with peer credential authorization |
| ML injection classification | Not implemented | Not implemented; `SemanticClassifier` protocol hook only | **PromptGuard 2** (Meta's neural injection classifier): local ONNX inference, signed model-packs, three postures (off/best_effort/required), three-tier thresholds |
| Tool Dependency Graph (TDG) | Not implemented | Not implemented | **TDG verification**: every tool action must trace back to the user's stated goal through a chain of dependency paths; ungrounded reads → confirmation; ungrounded writes → block |
| Phantom action detection | Not implemented | Not implemented | **Three phantom deny rules**: alerts when repeated denied actions suggest an attacker probing for capability boundaries, testing egress paths, or attempting taint bypasses; configurable threshold + window |
| Skill drift observability | Silent drop on schema mismatch | Silent drop on schema mismatch | **Structured audit events** when a skill plugin's tool schema changes after review (schema drift); events flushed to event bus at startup |
| Evidence system | `EvidenceStore` with plaintext blobs | Structured `ArtifactLedger` with lifecycle states, endorsement tracking, HMAC metadata MAC, restart-stable refs | Unchanged from v0.6.0 |
| Credential scoping | Session-level capability set | Per-task-envelope credential refs with `enforce_explicit_credential_refs` | Unchanged from v0.6.0 |
| Approval provenance | Nonce-based confirmation | Session/task/timestamp-bound provenance; non-portable across boundaries | Unchanged from v0.6.0 |
| Typed validation | Schema validation only | Semantic atom validators for URLs, command_tokens, workspace_paths, credential_refs | Unchanged from v0.6.0 |
| Browser tools | Not implemented | 6-tool browser surface with confirmation-gated writes and element-binding hash | Unchanged from v0.6.0 |
| Supply chain | Ed25519 skill signatures + pinned deps | + OIDC trusted publishing + SBOM + attestations + pip-audit + pinned CI actions + zizmor + adapter lockdown | + signed PromptGuard model-packs |
| Web tools | Not implemented | `web.search` + evidence-wrapped `web.fetch` | Unchanged from v0.6.0 |
| Test coverage | ~100+ unit, ~20+ integration, ~14 adversarial files | 1,368 test functions (84 adversarial); ~4,000+ new test lines | 1,522 test functions (86 adversarial, 70 behavioral); ~3,100+ new test lines from v0.6.0 |

## 2. Security Architecture

### 2.1 Design Philosophy

Unchanged from v0.5 -- "security enables functionality." The default policy grants all capabilities and sets `default_deny: false`. Security enforcement happens at execution time through the PEP pipeline, control-plane consensus, and sandbox isolation. v0.6.0 adds a new principle: **architectural trust boundaries are more reliable than runtime checks alone**. The COMMAND/TASK split encodes trust separation into the session model itself rather than relying solely on per-call enforcement.

### 2.2 Core Security Primitives (v0.6.0 State)

**Taint tracking** (`security/taint.py`): Unchanged from v0.5. Six `TaintLabel` values (`UNTRUSTED`, `SENSITIVE_EMAIL`, `SENSITIVE_FILE`, `SENSITIVE_CALENDAR`, `USER_CREDENTIALS`, `USER_REVIEWED`). Worst-case union propagation. The key property holds: `evidence.promote` produces `USER_REVIEWED`, not `TRUSTED` -- endorsement does not launder provenance.

**PEP** (`security/pep.py`): The 8-check pipeline from v0.5 is preserved and extended. New in v0.6.0:
- **Credential scope enforcement** (line 600-612): When `context.enforce_explicit_credential_refs` is true (always true for SUBAGENT sessions), every credential_ref in a tool call is checked against the task envelope's allowed set. Out-of-scope refs are rejected.
- **Typed semantic validation**: Tool arguments tagged with semantic types (`url`, `command_token`, `workspace_path`, `credential_ref`, `evidence_ref`) are validated by `is_valid_semantic_value()` in `core/tools/registry.py` (lines 71-107). Prose-bearing URLs, whitespace-bearing command tokens, and instructional content in structured fields are rejected before reaching the PEP's policy checks.

**Context scaffold** (`core/context.py`, `security/spotlight.py`): Unchanged from v0.5. Three-tier prompt construction with cryptographically random delimiters.

**[CHANGED v0.6.1] Control plane engine** (`security/control_plane/engine.py`, `security/control_plane/sidecar.py`): The five independent voters on metadata-only payloads are preserved, but the engine now runs in a separate process behind a Unix socket JSON-RPC boundary (see new sidecar section below).

**[NEW] SessionRole and TaskEnvelope** (`core/types.py:130-135`, `scheduler/schema.py:38-83`):

`SessionRole` is a `StrEnum` with two values: `ORCHESTRATOR` and `SUBAGENT`. The role is immutable after session creation. `create_subagent_session()` in `daemon/handlers/_impl_session.py` (line 164) enforces the boundary -- SUBAGENT sessions inherit restrictions from the orchestrator but cannot widen them.

`TaskEnvelope` is a frozen (immutable post-creation) Pydantic model carrying:
- `envelope_id`: UUID
- `capability_snapshot`: `frozenset[Capability]` -- frozen at task creation
- `parent_session_id`: reference to orchestrator
- `credential_refs`: `tuple[str, ...]` -- scoped credential allowlist
- `resource_scope_ids` / `resource_scope_prefixes`: resource boundary enforcement
- `untrusted_payload_action`: `"require_confirmation"` or `"reject"` -- controls what happens when a background task is triggered by tainted input
- `policy_snapshot_ref`, `audit_trail_ref`, `orchestrator_provenance`, `lockdown_state_inheritance`

The envelope is created by the orchestrator and cannot be modified by the subagent. Capability snapshots are frozen at creation time. Credential refs are the only credentials the TASK session can use. Resource scope IDs prevent cross-scope tool access.

**[NEW] ArtifactLedger** (`core/evidence.py:240-781`):

Replaces the v0.5 `EvidenceStore` with a structured artifact management system. Key components:

- **Lifecycle states** (`ArtifactLifecycleState`, line 39): `ACTIVE`, `QUARANTINED`. Artifacts can be quarantined on security anomaly and are excluded from normal queries.
- **Endorsement states** (`ArtifactEndorsementState`, line 44): `UNENDORSED`, `USER_ENDORSED`, `SYSTEM_ENDORSED`. Endorsement is audit metadata, not a trust upgrade -- `USER_ENDORSED` artifacts still carry their original taint labels.
- **Metadata MAC** (`_make_metadata_mac()`, line 499): HMAC-SHA256 over the canonical sorted JSON of all ref fields (artifact_kind, byte_size, content_hash, endorsement_state, lifecycle_state, ref_id, session_key, taint_labels, etc.) using a per-instance salt. Refs with missing or invalid MACs are dropped on load (fail-closed, no legacy migration).
- **Summary-firewall checkpoint** (`daemon/handlers/_impl_session.py:171`): `_build_task_summary_firewall_checkpoint()` validates every TASK summary for injection before the handoff completes. Firewall exceptions trigger a fail-closed path (`_TASK_SUMMARY_CHECKPOINT_FAILURE_REASON`). This is the mandatory architectural checkpoint at the TASK→COMMAND boundary.
- **Approval provenance binding**: Every `ToolApproved`/`ToolRejected`/`ToolExecuted` audit event carries session ID, task envelope ID, timestamp, and one-time nonce. Approvals are non-portable across task/session boundaries.

**[NEW] Browser toolkit** (`executors/browser.py`):

Six tools: `browser.navigate`, `browser.read_page`, `browser.screenshot`, `browser.click`, `browser.type_text`, `browser.end_session`.

- **Read-mostly actions** (navigate, read_page, screenshot) proceed without confirmation on authorized domains.
- **Write actions** (click, type_text) are confirmation-gated with element-binding hash verification.
- **Element-binding hash** (line 968-990): SHA256 hash of element properties (kind, label, selector, href, form_action, form_method, destination). Computed at approval time and verified at execution time. If the DOM changed between approval and execution (TOCTOU attack), execution fails with `browser_confirmation_context_changed`.
- **Source/destination URL binding**: Confirmation carries the approved source URL. If the page navigated between approval and execution, confirmation is invalid.
- **Hardened isolation** (`require_hardened_isolation`, line 248): When enabled (default: `SHISAD_BROWSER_REQUIRE_HARDENED_ISOLATION=1`), wildcard domain scope is rejected and `DegradedModePolicy.FAIL_CLOSED` applies.

**[NEW] Credential broker scoping** (`security/pep.py:600-612`, `daemon/handlers/_task_scope.py`):

v0.5's credential broker operated at the session level -- any credential in the store was usable. v0.6.0 adds per-task-envelope scoping:
- Tool grants do NOT implicitly grant credentials.
- TASK sessions have `enforce_explicit_credential_refs=True` in their `PolicyContext`.
- The PEP validates every credential_ref against the envelope's allowed set.
- `task_resource_authorizer()` in `_task_scope.py` (lines 11-37) prevents out-of-envelope resource access even when credentials are technically valid.

**[NEW v0.6.1] Control-plane sidecar** (`security/control_plane/sidecar.py`, 833 lines):

The control plane is the metadata-only policy-decision engine that evaluates proposed actions without ever seeing untrusted content (it receives only action types, resource identifiers, and timing metadata). In v0.6.0 it ran in the same process as the daemon. In v0.6.1, it runs in a separate OS process, spawned as a subprocess by the daemon. Communication is via JSON-RPC over a Unix domain socket (`control_plane/sidecar.sock`). Key security properties:

- **Peer credential authorization** (`_is_authorized_sidecar_peer()`, line 797): Every RPC call validates that the connecting peer has the same UID as the sidecar process and that the peer's PID matches the expected parent daemon PID. This prevents other processes from issuing control-plane commands.
- **Fail-closed on unavailability**: `ControlPlaneUnavailableError` is raised when the sidecar is unreachable. The daemon cannot proceed without the control plane.
- **Parent-death watchdog** (`_watch_parent()`, line 697): The sidecar monitors its parent PID and exits automatically if the daemon disappears. Prevents orphaned sidecar processes.
- **`ControlPlaneGateway` protocol** (line 68): A typed Protocol interface consumed by daemon handlers. Both the in-process engine and the sidecar client implement the same interface, maintaining behavioral compatibility.
- **Typed Pydantic RPC models**: Every RPC method has explicit request/response Pydantic models. No unstructured data crosses the process boundary.

This closes the v0.6.0 gap where the control plane was in-process and the boundary was coding convention only. The sidecar provides OS-level process isolation: a compromised agent runtime cannot directly access control plane internals because they live in a separate address space. The Unix socket peer credential check prevents other local processes from injecting commands.

**[NEW v0.6.1] PromptGuard 2 ML classifier** (`security/firewall/classifier.py`, `security/firewall/promptguard_pack.py`):

The `SemanticClassifier` protocol hook from v0.6.0 is now backed by a production implementation: PromptGuard 2 running as a local ONNX model.

- **`OnnxPromptGuardBackend`** (classifier.py, line 153): Local-only inference using Transformers tokenizer + ONNX Runtime CPU provider. Supports sliding-window tokenization (`max_length=512`, `stride=64`) with batched inference for long inputs (`max_segments=8`). No remote model loading -- `local_files_only=True` and `trust_remote_code=False` are hardcoded.
- **`PromptGuardSemanticClassifier`** (classifier.py, line 331): Wraps the backend behind the `SemanticClassifier` protocol. Takes the max maliciousness score across all segments, maps it through three-tier thresholds (medium=0.35, high=0.7, critical=0.9) to `SemanticRiskTier` values.
- **Three postures** (`PromptGuardSettings.posture`): `off` (disabled), `best_effort` (degrades gracefully on error), `required` (fails closed on any error).
- **Signed model-packs** (`promptguard_pack.py`): Model artifacts are distributed as signed packs with `manifest.json` containing SHA256 hashes of all files. Signature verification uses `ssh-keygen -Y verify` against an `allowed_signers` trust store. Invalid signatures, missing files, hash mismatches, or unsafe relative paths all fail closed. Build provenance is recorded in the manifest (`source_model_id`, `builder_id`, `signer_principal`).
- **Integration path**: `ContentFirewall.__init__()` now accepts a `semantic_classifier` parameter. `PatternInjectionClassifier.classify()` calls the semantic classifier and takes the max of pattern-based and ML-based scores. The `FirewallResult` now carries `semantic_risk_score`, `semantic_risk_tier`, and `semantic_classifier_id`.
- **Policy-configurable**: `content_firewall.semantic_classifier` section in policy YAML controls posture, model path, and thresholds.

This closes the v0.6.0 gap about pattern-based classification being the only detection mechanism. The ML classifier operates alongside (not replacing) pattern + YARA rules -- scores are merged via max(), so the classifier can only escalate, never suppress pattern findings.

**[NEW v0.6.1] Tool Dependency Graph (TDG) verification** (`security/control_plane/trace.py`, 620 lines):

The TDG verifier ensures that every tool action the agent performs can be traced back to the user's stated goal through a chain of dependency paths. For example, if the user asks "summarize README.md," the agent can read README.md (it traces to the goal) but cannot read /etc/passwd (ungrounded -- no path from the goal to that file). If the agent reads README.md and finds a link to changelog.md, reading changelog.md is grounded (it's reachable from a prior legitimate action). Key mechanisms:

- **`ExecutionTraceVerifier`** (trace.py, line 159): Commits structural plans before untrusted content is seen, then verifies each action against the plan.
- **Plan stages**: `STAGE1_PRECONTENT` (before any untrusted content has been fetched; only reads/lists/memory reads allowed) and `STAGE2_POSTEVIDENCE` (after the user has reviewed fetched content and approved expanding the plan; writes and egress can now be allowed).
- **Goal resource extraction** (`_goal_resource_patterns()`, line 444): Extracts file paths, hosts, and workspace roots from the user's goal text. These become dependency roots.
- **Declared resource roots**: COMMAND session can declare resource roots (filesystem paths, hostnames) that become first-class TDG roots, allowing TASK agents to access them without extra confirmation.
- **Reachability tracking** (`record_dependency_path()`, line 324): After successful execution, the action's resource IDs are added to `reachable_resources`. Subsequent actions to resources reachable from prior outputs are grounded.
- **TDG enforcement** (`_tdg_reason()`, line 450): For enforced action kinds (FS_READ, FS_LIST, FS_WRITE, EGRESS, BROWSER_READ, BROWSER_WRITE), if the target resource is not grounded in any dependency root, the action is either routed to confirmation (read-like) or blocked (write-like/side-effect).
- **Plan amendment** (`amend()`, line 347): User approval via `approve_stage2` can widen the plan to allow additional action kinds and resources. The amendment carries the prior plan hash for audit chaining.
- **`PlanVerificationResult`** carries `reason_code` and `risk_tier` for downstream enforcement.

This is a significant new defense layer: even if an injection successfully proposes an action that passes all other checks, the TDG verifier will block it unless the target resource traces back to the user's stated goal or to outputs of prior legitimate actions.

**[NEW v0.6.1] Phantom action detection** (`security/control_plane/sequence.py`, `security/control_plane/engine.py`):

"Phantom actions" are tool calls that the agent keeps attempting despite being denied by the policy enforcement pipeline (PEP) -- a pattern that suggests an attacker is probing for capability boundaries or testing ways around security controls. Repeated denied actions now trigger structured warnings:

- **`PhantomDenyRule`** (sequence.py, line 31): Configurable rule with reason codes to watch, threshold count, time window, and risk tier.
- **Three default rules** (engine.py, lines 140-172): `phantom_capability_probe` (repeated `pep:missing_capabilities`, `pep:tool_not_permitted`, `pep:resource_authorization_failed`), `phantom_unattributed_egress` (repeated `pep:destination_unattributed`, `pep:ip_literal_not_allowlisted`, `pep:local_destination_not_allowlisted`), `phantom_taint_bypass_attempt` (repeated `pep:taint_sink_block`).
- **Detection flow**: `observe_denied_action()` on the engine (line 344) records the denial in the history store, runs `analyze_denied_action()` on the sequence analyzer, and emits `phantom_action_detected` audit events with evidence arrays.
- **Threshold-based alerting**: Findings fire only when the count crosses the threshold (default 3 within 120 seconds), preventing duplicate alerts.

This converts previously silent deny-and-continue behavior into observable compromise signals. An attacker probing for capability boundaries or attempting repeated taint bypasses now generates structured metadata-only alerts.

**[NEW v0.6.1] Skill drift observability** (`skills/manager.py`):

Skills are third-party plugins that declare tool interfaces. After a skill is reviewed and approved, its tool schemas are recorded as SHA256 hashes. "Skill drift" occurs when a skill's tool schema changes after review -- potentially indicating tampering or unauthorized modification.

- `SkillManager._record_registration_drop()` (line 434): When a reviewed skill tool's schema hash doesn't match the expected hash, the tool is still dropped (fail-closed, same as v0.6.0), but now a structured `SkillToolRegistrationDropped` audit event is emitted with skill name, version, tool name, reason code, and hash prefixes (first 12 chars of expected vs. actual).
- Events are buffered during initialization and flushed to the event bus at daemon startup.
- Operators can now see *why* a skill tool was dropped rather than discovering the absence silently.

### 2.3 Threat Model

v0.6.0 extends the v0.5 threat model with three new threat categories:

- **Cross-boundary taint laundering**: A compromised TASK agent could attempt to smuggle tainted content back to the orchestrator through the return boundary. Addressed by the mandatory summary-firewall checkpoint and the ArtifactLedger's taint-preserving endorsement model.
- **Approval replay attacks**: An attacker could attempt to replay a legitimate approval in a different task/session context. Addressed by approval provenance binding (session + task + nonce + timestamp).
- **Browser DOM-drift attacks**: Attacker-controlled pages could change between approval and execution. Addressed by element-binding hash verification and source URL binding.

The threat model also now explicitly covers supply chain attacks referencing real-world incidents: LiteLLM compromise (2026-03-24), ClawdHub skill poisoning, and Cline malware distribution.

### 2.4 Design-to-Implementation Gap (v0.6.1 Assessment)

**Gaps closed from v0.5 (in v0.6.0):**

| v0.5 Gap | v0.6.0 Status | Component |
|----------|---------------|-----------|
| COMMAND/TASK agent separation conceptual only | **Closed**: First-class `SessionRole` + `TaskEnvelope` with immutable envelopes | `core/types.py`, `scheduler/schema.py`, `daemon/handlers/_impl_session.py` |
| ArtifactLedger proposed but not implemented | **Closed**: Structured ledger with lifecycle, endorsement, metadata MAC | `core/evidence.py:240-781` |
| Summary barrier not a mandatory checkpoint | **Closed**: `_build_task_summary_firewall_checkpoint()` is mandatory | `daemon/handlers/_impl_session.py:171` |
| No typed argument validation beyond schema | **Closed**: Semantic atom validators for 7 field types | `core/tools/registry.py:71-107` |
| Credential scoping session-level only | **Closed**: Per-task-envelope credential refs | `security/pep.py:600-612` |
| No approval provenance binding | **Closed**: Session/task/nonce/timestamp-bound provenance | `daemon/handlers/_impl_confirmation.py` |

**Gaps closed from v0.6.0 (in v0.6.1):**

| v0.6.0 Gap | v0.6.1 Status | Component |
|------------|---------------|-----------|
| In-process control plane (coding convention) | **Closed**: OS-level process isolation via Unix socket sidecar with peer credential authorization | `security/control_plane/sidecar.py` |
| No ML-based injection classifier | **Closed**: PromptGuard 2 local ONNX inference with signed model-packs, three postures, three-tier thresholds | `security/firewall/classifier.py`, `security/firewall/promptguard_pack.py` |
| No tool dependency graph verification | **Closed**: TDG verification traces actions to committed intent; ungrounded reads → confirmation, ungrounded writes → block | `security/control_plane/trace.py` |
| Schema-hash inventory registration-time only (silent drops) | **Closed**: Structured `SkillToolRegistrationDropped` audit events on drift with hash prefixes | `skills/manager.py`, `core/events.py` |

**Remaining gaps:**

- **Variable-level provenance tracking**: Still operates at content-block level, not CaMeL's per-variable level.
- **Evidence encryption at rest**: Metadata MAC provides tamper detection but blobs remain unencrypted. Encryption hook point exists; KMS/HSM integration deferred to v0.6.2.
- **Scoped approval tokens with TTL**: Still per-action confirmation only; no pre-approval tokens (e.g., "approve all fetches to reuters.com for 30 minutes").
- **Differential execution**: Lightweight wrapper exists, not the full three-tier system.
- **No MCP/A2A access control**: Planned for v0.6.3.
- **No formal noninterference proof**: Taint system follows IFC principles but has no machine-checked proofs.

## 3. Mapping to Defense Taxonomy

### 3.1 Secure Architectures by Construction

**Rating: Strong** (further strengthened from v0.6.0)

v0.5 already had the metadata-only PEP and three-tier context scaffold. v0.6.0 added the COMMAND/TASK dual-agent architecture as a first-class runtime concept. v0.6.1 closes the control-plane isolation gap:

- `SessionRole` enum (`ORCHESTRATOR`/`SUBAGENT`) is immutable at session creation (`core/types.py:130`).
- `TaskEnvelope` carries frozen capability snapshots and credential refs that cannot be widened post-creation (`scheduler/schema.py:38`).
- TASK→COMMAND handoffs must pass a mandatory summary-firewall checkpoint (`daemon/handlers/_impl_session.py:171`).
- The structured `ArtifactLedger` (`core/evidence.py:240`) tracks artifact lifecycle and endorsement state with HMAC-bound metadata. Endorsement does not strip taint.
- TASK close-gate self-check: Before handoff completion, the TASK agent inspects the original task description to detect injection-driven drift.
- **[NEW v0.6.1]** The control plane now runs in a separate OS process (`security/control_plane/sidecar.py`), communicating via JSON-RPC over a Unix domain socket with peer credential authorization. The metadata boundary between control plane and agent runtime is now an OS-level process boundary, not coding convention.

This is the first production implementation of the CaMeL-inspired dual-agent architecture with explicit trust boundaries. The remaining gap vs. CaMeL: provenance is tracked at the content-block level, not per-variable. The control-plane isolation gap from v0.6.0 is now closed.

### 3.2 Access Control and Governance

**Rating: Strong** (strengthened from v0.5)

v0.5 had session capability sets, most-restrictive-wins policy merge, per-tool allowlists, and argument DLP. v0.6.0 adds:

- **Typed semantic atom validation** (`core/tools/registry.py:71-107`): Seven field types with specific validation rules. URLs must have scheme+hostname and no whitespace. Command tokens reject whitespace and instructional patterns. Workspace paths reject `..` traversal and instructional text. Credential refs, evidence refs, and thread IDs must match `^[A-Za-z0-9][A-Za-z0-9._:-]{0,127}$`.
- **Task-envelope credential scoping** (`security/pep.py:600-612`): SUBAGENT sessions have `enforce_explicit_credential_refs=True`. Every credential_ref is checked against the task envelope's allowed set. Missing or out-of-scope refs fail closed.
- **Resource-scope enforcement** (`daemon/handlers/_task_scope.py:11-37`): Task resource scopes (e.g., `thread-id:12345`) prevent cross-scope tool access even when credentials are valid.
- **Approval provenance binding**: Approvals are non-portable across task/session boundaries.
- **Untrusted-trigger policy**: Background tasks triggered by tainted event payloads either require confirmation or are rejected outright, controlled by `untrusted_payload_action` in the task envelope.

### 3.3 Runtime Verification and Policy Enforcement

**Rating: Strong** (further strengthened from v0.6.0)

v0.5 had the PEP 8-check pipeline, 5-voter consensus, behavioral sequence analysis, plan commitment verification, rate limiting, and lockdown escalation. v0.6.0 added browser element-binding hash, tool-schema-hash drift detection, TASK close-gate self-check, and approval provenance binding. v0.6.1 adds:

- **[NEW v0.6.1] Tool Dependency Graph verification** (`security/control_plane/trace.py`): Actions must trace to committed user intent through dependency paths. Plans are committed before untrusted content is seen (stage 1: reads only). After evidence review, plans can be amended to allow writes/egress (stage 2). Ungrounded read-like actions route to confirmation; ungrounded write-like actions are blocked. Reachable resources expand as actions succeed, building a dynamic dependency graph.
- **[NEW v0.6.1] Phantom action detection** (`security/control_plane/sequence.py`, `engine.py`): Repeated denied actions (capability probes, unattributed egress attempts, taint bypass attempts) crossing a configurable threshold (default: 3 within 120 seconds) trigger structured `phantom_action_detected` audit events. Converts silent deny-and-continue into observable compromise signals.
- **[NEW v0.6.1] Declared resource roots**: COMMAND sessions can declare workspace roots and resource roots that become first-class TDG dependency sources, allowing TASK agents to access them without unnecessary confirmation (addresses the trusted-scope inheritance gap).
- **Browser element-binding hash** (`executors/browser.py:968-990`): SHA256 hash of element properties. Verified at execution time to prevent TOCTOU attacks.
- **Source/destination URL binding**: Browser write confirmations carry the approved source URL. Navigation between approval and execution invalidates the confirmation.
- **Tool-schema-hash drift detection** (`core/tools/registry.py:122-145`): Skill-declared tools register with expected schema hashes. Hash mismatch blocks re-registration (fail-closed). **[v0.6.1]** Now emits structured `SkillToolRegistrationDropped` audit events on drift.
- **TASK close-gate self-check**: Before delegated handoff completes, the TASK agent inspects the original task description against its output to detect injection-driven drift.
- **Approval provenance**: Every approval carries session ID, task envelope ID, timestamp, and one-time nonce. Replay across boundaries fails.

### 3.4 Detection, Filtering, and Firewalls

**Rating: Strong** (further strengthened from v0.6.0)

v0.5 had the content firewall (pattern + YARA), multi-layer base64 decoding, secret/PII detection, and output firewall. v0.6.0 added terminal control-sequence sanitization, browser DOM-drift detection, and supply chain detection layers (detailed below). v0.6.1 adds:

- **[NEW v0.6.1] PromptGuard 2 ML classifier** (`security/firewall/classifier.py`): Local ONNX-based neural classifier for prompt injection detection. Operates alongside (not replacing) pattern + YARA rules. Scores are merged via `max()` -- the classifier can only escalate, never suppress pattern findings. Three-tier thresholds: medium (0.35), high (0.7), critical (0.9). Three postures: `off`, `best_effort` (degrades gracefully), `required` (fails closed). Signed model-packs prevent model tampering.
- **[NEW v0.6.1] Fixed YARA unicode steganography rule**: The shipped unicode-steganography detection rule now compiles correctly at runtime, closing a v0.6.0 bug where the rule depended on a broken compile path.
- **Terminal control-sequence sanitization**: Strips ANSI CSI, OSC, DCS/APC/PM/SOS sequences, stray ESC, and C0/C1 control characters from evidence rendering. Prevents terminal escape injection.
- **Browser DOM-drift detection**: Element-binding hash mechanism detects when attacker-controlled pages modify DOM between approval and execution.
- **Supply chain detection layers**:
  - `pip-audit --require-hashes` in publish workflow for known-vulnerability detection
  - `dependency-review` GitHub Action on PRs for supply chain scanning
  - `zizmor` workflow linting for CI/CD security issues
  - `uv lock --check` lockfile drift guard
  - Tool-schema-hash inventory for skill drift detection (**[v0.6.1]** now with structured audit events on drift)
  - `SHISAD_REQUIRE_LOCAL_ADAPTERS` flag to prevent runtime npx remote fetches

### 3.5 Model-Level Hardening

**Rating: Partial** (upgraded from Minimal in v0.6.0)

The action monitor still uses simple heuristics. The LLM is explicitly treated as untrusted (correct design for multi-provider frameworks). However, v0.6.1 now deploys PromptGuard 2 as a content-seeing detection layer. While PromptGuard is not model-level hardening in the SecAlign sense (it doesn't change the model's behavior), it provides ML-based input classification that is architecturally adjacent -- it screens untrusted content before it reaches the LLM context, reducing the model's exposure to injection payloads. This is the first ML-based classifier deployed in any open-source production agent framework.

### 3.6 Boundary Marking and Cryptographic Provenance

**Rating: Strong** (further strengthened from v0.6.0)

v0.5 had spotlighting with random delimiters, three-tier context placement, policy integrity (SHA256 + SIGHUP), skill Ed25519 signatures, and the credential broker. v0.6.0 added:

- **Mandatory TASK→COMMAND summary-firewall checkpoint**: Architectural boundary enforcement, not just content filtering. TASK output cannot reach orchestrator context without passing the checkpoint.
- **ArtifactLedger metadata MAC** (`core/evidence.py:499`): HMAC-SHA256 over all ref fields using per-instance salt. Tampered or stripped MACs cause refs to be dropped on load.
- **Approval provenance binding**: Session/task/nonce/timestamp attached to every approval event. Non-portable across boundaries.
- **OIDC trusted publishing** (`.github/workflows/publish.yml`): Eliminates long-lived PyPI credentials. Uses GitHub's OpenID Connect for identity verification.
- **SBOM generation**: Anchore SBOM action produces SPDX 3.0 JSON attached to GitHub Release.
- **Build provenance attestations**: GitHub Actions `attest-build-provenance` creates attestations for wheel artifacts, verifiable by consumers.
- **Tool-schema-hash inventory**: Persisted schema hashes detect skill tool tampering.

v0.6.1 adds:

- **[NEW v0.6.1] Process-level control-plane boundary**: Unix domain socket with peer credential authorization enforces OS-level separation between the control plane and agent runtime.
- **[NEW v0.6.1] Signed PromptGuard model-packs**: Ed25519-signed manifests with SHA256 file hashes, verified via `ssh-keygen -Y verify` against an `allowed_signers` trust store. Prevents model tampering in the ML classifier supply chain.
- **[NEW v0.6.1] Structured skill drift audit events**: `SkillToolRegistrationDropped` events with hash prefixes provide tamper-evident observability for skill tool integrity.

### 3.7 Formal Methods and Semantics

**Rating: None** (unchanged from v0.5)

The taint tracking system follows IFC principles but has no machine-checked proofs. The COMMAND/TASK separation creates a real architectural boundary but is not formally verified. Writing a consistency checker for taint-sink rules against the label lattice remains the highest-leverage formal methods opportunity.

## 4. Source Code Analysis

### 4.1 New Security-Critical Code Paths

**COMMAND/TASK orchestration flow:**

1. **Orchestrator creates task envelope** (`scheduler/schema.py:38-83`): Frozen `TaskEnvelope` with capability snapshot, credential refs, resource scopes.
2. **Subagent session created** (`daemon/handlers/_impl_session.py:164`): `create_subagent_session()` sets `SessionRole.SUBAGENT` (immutable). Policy context inherits `enforce_explicit_credential_refs=True`.
3. **Task execution**: Tool calls go through standard PEP pipeline with additional credential scope enforcement (`security/pep.py:600-612`) and resource scope enforcement (`daemon/handlers/_task_scope.py:11-37`).
4. **Task close-gate self-check**: Before handoff, TASK inspects original description vs output.
5. **Summary-firewall checkpoint** (`daemon/handlers/_impl_session.py:171,5115`): `_build_task_summary_firewall_checkpoint()` runs content firewall on every summary sentence. Injection-bearing content triggers `_TASK_SUMMARY_CHECKPOINT_FAILURE_REASON` and blocks the handoff.
6. **Approval provenance recording**: `ToolApproved`/`ToolRejected`/`ToolExecuted` events carry session ID, envelope ID, timestamp, nonce.

**Browser tool execution flow:**

1. **Domain scope validation** (`executors/browser.py:557-558`): Wildcard domains rejected under hardened isolation.
2. **Navigation** (line 274): URL validated against approved domains.
3. **Element snapshot**: Before click/type, element properties captured and hashed (line 968-990).
4. **Confirmation request**: Hash and source URL included in confirmation context.
5. **Post-approval validation** (`_validate_prepared_binding()`, line 368): Live element binding hash compared to approved hash. Source URL compared. Mismatch → `browser_confirmation_context_changed`.
6. **Execution**: Only after binding validation passes.

### 4.2 New v0.6.1 Security-Critical Code Paths

**Control-plane sidecar flow:**

1. **Daemon startup** (`daemon/services.py`): `start_control_plane_sidecar()` spawns a subprocess running `shisad.security.control_plane.sidecar` with `--socket-path`, `--data-dir`, `--policy-path`, `--parent-pid`, and `--assistant-fs-root` arguments.
2. **Sidecar initialization** (`sidecar.py:708`): `_run_sidecar()` builds a `ControlPlaneEngine` instance (same as previously in-process), creates a `ControlServer` on the Unix socket, registers 9 JSON-RPC methods, installs signal handlers, and starts a parent-PID watchdog.
3. **Peer authorization** (`sidecar.py:797`): Every RPC call validates UID match and PID match against the expected parent. Unauthorized peers are rejected.
4. **Daemon communication**: All daemon handler code now calls `control_plane.evaluate_action()`, `control_plane.record_execution()`, etc. through the `ControlPlaneGateway` protocol, which dispatches via `ControlPlaneSidecarClient` over the Unix socket.
5. **Fail-closed**: `ControlPlaneUnavailableError` on socket errors, timeouts, or validation failures prevents the daemon from proceeding without the control plane.

**PromptGuard classification flow:**

1. **Daemon startup** (`daemon/services.py`): `build_promptguard_classifier()` loads the configured model from a local path, optionally verifying the signed model-pack. The classifier is injected into `ContentFirewall`.
2. **Content inspection** (`firewall/__init__.py`): `ContentFirewall.inspect()` calls `PatternInjectionClassifier.classify()`, which runs both pattern matching and (if available) `PromptGuardSemanticClassifier.classify()`.
3. **PromptGuard scoring** (`classifier.py:224`): `OnnxPromptGuardBackend.score_text()` tokenizes with sliding window, runs batched ONNX inference, extracts maliciousness probability via softmax, returns per-segment scores.
4. **Score merging** (`classifier.py:688-695`): Pattern score and semantic score are merged via `max()` -- the ML classifier can only escalate, never suppress. Semantic risk tier and classifier ID are propagated to the `FirewallResult`.
5. **Degradation handling**: On inference failure, `best_effort` posture logs a warning and returns zero-score (detection continues without ML). `required` posture raises an error (fail-closed).

**TDG verification flow:**

1. **Plan commitment** (`trace.py:179`): `begin_precontent_plan()` extracts goal resource patterns (file paths, hosts, workspace roots), freezes stage-1 allowed actions (reads/lists/memory reads + capability-granted actions), and persists the plan.
2. **Action verification** (`trace.py:227`): `verify_action()` checks: forbidden actions → reject; action kind not in plan → stage-2 upgrade required (if write/egress in stage 1); resource not in allowed set → reject; TDG check → ungrounded reads need confirmation, ungrounded writes blocked; action count limit → reject.
3. **Dependency tracking** (`trace.py:324`): `record_dependency_path()` after successful execution adds the action's resource IDs to `reachable_resources`, expanding the grounding set.
4. **Plan amendment** (`trace.py:347`): User approval via `approve_stage2` widens allowed actions/resources, transitions plan to stage 2, and chains to the prior plan hash.

### 4.3 Supply Chain Hardening (`.github/workflows/`)

**Publish workflow** (`.github/workflows/publish.yml`):

1. **Pre-gates**: Version/tag match verification, lockfile check (`uv lock --check`), linting (ruff), full test suite (unit + behavioral), package metadata verification (twine), dependency audit (`pip-audit --require-hashes --no-emit-project`).
2. **Build**: Produces wheel + sdist artifacts.
3. **SBOM**: Anchore `sbom-action` generates SPDX 3.0 JSON (excluded from dist, attached to release).
4. **Attestations**: `actions/attest-build-provenance@v4.1.0` for wheel artifacts.
5. **Publish**: PyPA trusted publishing via OIDC (no stored credentials). Protected `pypi-publish` environment requires approval.

**CI hardening**:

- All GitHub Actions pinned to immutable commit SHAs (checkout, setup-uv, upload-artifact, dependency-review, attest-build-provenance, sbom-action).
- Top-level `permissions: contents: read` with elevated scopes only where needed (`id-token: write`, `attestations: write` for publish job only).
- 7-day update exclusion window (`--exclude-newer P7D`) on dev installs prevents surprise transitive updates.
- `SHISAD_REQUIRE_LOCAL_ADAPTERS=1` prevents runtime `npx` fetches.

**CI job structure** (7 jobs):

| Job | Trigger | Purpose |
|-----|---------|---------|
| lint-and-test | push/PR | Lockfile check, linting, unit tests (Python 3.12, 3.13) |
| security-runtime | push/PR | Full deps with yara-python, coverage enforcement (80% critical, 60% general) |
| privileged-connect-path | optional | CAP_NET_ADMIN network tests |
| adversarial-pr-core | PR | 13 deterministic core adversarial tests gating PRs |
| adversarial-nightly-full | schedule/manual | Full adversarial suite with metrics/regression gating |
| dependency-review | PR | GitHub native supply chain scanner |
| zizmor | push/PR | Workflow security linting |

### 4.3 Semantic Atom Validation

`is_valid_semantic_value()` in `core/tools/registry.py` (lines 71-107) validates tool arguments tagged with semantic types:

| Type | Validation Rules | Rejects |
|------|-----------------|---------|
| `url` | No whitespace, http/https scheme, hostname present | Prose-bearing URLs, data: URIs, relative paths |
| `workspace_path` | No `..`, trimmed segments, no instructional text | Path traversal, embedded instructions |
| `command_token` | No whitespace, no instructional patterns | Multi-token injection, embedded instructions |
| `credential_ref` | `^[A-Za-z0-9][A-Za-z0-9._:-]{0,127}$` | Injection via credential names |
| `evidence_ref` | Same pattern as credential_ref | Injection via evidence ref names |
| `thread_id` | Same pattern | Cross-scope targeting |
| `email_address` | `[^@\s]+@[^@\s]+\.[^@\s]+` | Malformed addresses |

All types also reject non-string inputs and control characters (null, newline, CR, tab).

### 4.5 Dependency Changes

| Package | v0.5 Version | v0.6.0 Version | Reason |
|---------|-------------|----------------|--------|
| cryptography | 45.0.7 | 46.0.6 | CVE-2026-34073, CVE-2026-26007 |
| aiohttp | 3.13.3 | 3.13.5 | Security patches |
| Pygments | 2.19.2 | 2.20.0 | Maintenance |

**New in v0.6.1:** `onnxruntime`, `transformers`, and `numpy` are added as optional dependencies for the PromptGuard 2 classifier. These are only loaded when PromptGuard is configured (posture != `off`).

All direct + transitive dependencies resolved via `uv.lock` with SHA256 integrity hashes. CI install uses `--frozen` + `--exclude-newer P7D`.

## 5. Production Readiness

### 5.1 Maturity Level

**v0.5 → v0.6.0 → v0.6.1 progression indicators:**

- Source code grew from ~46.5K to ~51.5K (v0.6.0) to ~55K lines (v0.6.1) (18% total increase from v0.5).
- Test code grew from ~43.7K to ~51.9K (v0.6.0) to ~55K lines (v0.6.1) (26% total increase from v0.5). Test/source ratio: 1.0x.
- Test functions: 1,522 total (86 adversarial, 182 integration, 1,182 unit, 70 behavioral). Up from 1,368 in v0.6.0.
- **New test category in v0.6.1:** Behavioral tests (70 functions) covering tool access UX and behavioral contract verification.
- CI pipeline: 7 jobs covering security runtime, adversarial gating, dependency review, and workflow linting.
- Supply chain: full OIDC trusted publishing with SBOM, attestations, and hash-verified auditing (v0.6.0). Signed model-packs for PromptGuard artifacts (v0.6.1).

### 5.2 Test Coverage

**New test files in v0.6.0:**

| File | Lines | Coverage |
|------|-------|---------|
| `tests/adversarial/test_adversarial_task_handoffs.py` | 259 | Cross-session taint laundering, orchestrator context leakage, capability-snapshot immutability |
| `tests/integration/test_task_session_isolation.py` | 2,001 | TASK/ORCHESTRATOR role separation, session boundaries, policy inheritance |
| `tests/integration/test_task_ledger_scaffold.py` | 472 | ArtifactLedger persistence, metadata MAC validation, endorsement lifecycle |
| `tests/unit/test_browser_toolkit.py` | 795 | Element binding hash, confirmation context, URL validation, hardened isolation |
| `tests/unit/test_skill_tool_registration.py` | 496 | Tool schema hash verification, registry integrity, drift detection |

**New test files in v0.6.1:**

| File | Coverage |
|------|---------|
| `tests/unit/test_control_plane_sidecar.py` | Sidecar lifecycle, peer authorization, fail-closed behavior, parent-death watchdog |
| `tests/unit/test_promptguard_classifier.py` | ONNX backend scoring, threshold tiering, posture degradation, model-pack verification, score merging |
| `tests/unit/test_denied_action_observation.py` | Phantom deny rule matching, threshold crossing, window expiry |
| `tests/unit/test_handler_confirmation.py` | Pending PEP context snapshots, capability elevation, approval provenance |
| `tests/integration/test_control_plane_integration.py` | TDG plan commitment, stage transitions, resource grounding, dependency path expansion |
| `tests/adversarial/test_adversarial_hardening.py` | Control-plane sidecar under adversarial conditions |
| `tests/behavioral/test_behavioral_contract.py` | Behavioral contract verification for new security primitives |
| `tests/behavioral/test_tool_access_ux.py` | Tool access UX under TDG enforcement, declared resource roots |

**Coverage enforcement** (CI):
- 80% minimum on critical security modules.
- 60% minimum on general modules.
- Coverage trend tracking across releases.

### 5.3 Deployment Model

Unchanged from v0.5 -- Unix socket daemon with multi-channel ingress. New environment variables:

| Variable | Default | Purpose |
|----------|---------|---------|
| `SHISAD_BROWSER_ENABLED` | 0 | Enable browser tools |
| `SHISAD_BROWSER_COMMAND` | -- | Playwright CLI path |
| `SHISAD_BROWSER_ALLOWED_DOMAINS` | -- | Auto-approve scope |
| `SHISAD_BROWSER_TIMEOUT_SECONDS` | -- | Timeout |
| `SHISAD_BROWSER_REQUIRE_HARDENED_ISOLATION` | 1 | Fail-closed on wildcards |
| `SHISAD_BROWSER_MAX_READ_BYTES` | -- | Read limit |
| `SHISAD_REQUIRE_LOCAL_ADAPTERS` | 1 | Block runtime npx fetches |

## 6. Strengths

### Retained from v0.5

1. **Metadata-only control plane.** PEP and consensus voters never see raw untrusted content.
2. **Provenance-aware 5-tier egress.** Tool-declared / allowlisted / user-requested / untrusted-suggested / unattributed.
3. **Most-restrictive-wins policy merge.** Callers can only narrow access, never widen it.
4. **Credential broker with proxy-level injection.** LLM never sees raw secrets.
5. **Defense-in-depth.** Multiple independently-functional layers fail independently.

### New in v0.6.0

6. **First production COMMAND/TASK dual-agent architecture.** `SessionRole` is immutable at creation, `TaskEnvelope` carries frozen capabilities/credentials, TASK→COMMAND handoffs pass mandatory summary-firewall checkpoint. This is the closest production implementation of CaMeL-inspired privilege separation. The architectural boundary is more reliable than per-call checks alone because it doesn't depend on individual enforcement rules being correct -- the subagent structurally cannot access credentials or resources outside its envelope.

7. **Endorsement-aware ArtifactLedger with tamper detection.** Metadata MAC (HMAC-SHA256) provides tamper detection for persisted evidence refs. Lifecycle states (active/quarantined) and endorsement states (unendorsed/user_endorsed/system_endorsed) are tracked separately from taint. Stripped or invalid MACs cause refs to be dropped on load (fail-closed). The critical property: endorsement does not launder provenance. `USER_ENDORSED` artifacts still carry their original taint labels.

8. **Approval provenance binding.** Every approval carries session ID, task envelope ID, timestamp, and one-time nonce. Approvals are non-portable across task/session boundaries. This prevents replay attacks where a legitimate approval in one context is exploited in another.

9. **Browser tool surface with TOCTOU prevention.** Element-binding hash (SHA256 of element properties) prevents DOM-drift attacks. Source URL binding prevents cross-page approval replay. Hardened isolation mode (default on) rejects wildcard domain scope and applies fail-closed degraded mode policy.

10. **End-to-end supply chain hardening.** OIDC trusted publishing eliminates long-lived credentials. SBOM + build attestations provide tamper-evident provenance from source to PyPI. Pinned CI actions (immutable SHAs) prevent upstream workflow poisoning. `pip-audit --require-hashes` catches known vulnerabilities. `zizmor` catches CI/CD security issues. Adapter runtime lockdown prevents dynamic fetches. Tool-schema-hash inventory detects skill tampering. This is the most comprehensive supply chain posture in the production agent framework landscape.

11. **Typed semantic atom validation.** Rejects prose-bearing URLs, whitespace-bearing command tokens, instructional content in structured fields, and control characters in all typed arguments. This is a structural defense against injection through tool arguments -- the validator operates on the argument shape, not its content, so it cannot be bypassed by encoding tricks.

### New in v0.6.1

12. **Process-isolated control plane.** The control plane engine now runs in a separate OS process (`security/control_plane/sidecar.py`), communicating via JSON-RPC over a Unix domain socket. Peer credential authorization (UID + PID match) prevents unauthorized processes from issuing control-plane commands. Parent-death watchdog prevents orphaned sidecar processes. Fail-closed on unavailability. This closes the largest remaining architectural gap from v0.6.0 -- the metadata boundary between control plane and agent runtime is now an OS-level process boundary, not coding convention.

13. **PromptGuard 2 ML injection classifier.** First ML-based prompt injection classifier deployed in an open-source production agent framework. Local ONNX inference (no remote model loading), signed model-packs with SHA256 file hashes and Ed25519 manifest signatures, three postures (off/best_effort/required), three-tier thresholds (medium 0.35 / high 0.7 / critical 0.9). Operates alongside pattern + YARA rules via `max()` score merging -- can only escalate, never suppress. The `best_effort` posture degrades gracefully on inference failure; `required` fails closed. This closes the gap between shisad and LlamaFirewall's PromptGuard 2 deployment at Meta -- same underlying model, now available in the open-source agent framework landscape.

14. **Tool Dependency Graph verification.** Actions must trace back to committed user intent through dependency paths. Plans are committed before untrusted content is seen (stage 1: reads/lists only). After evidence review, plans can be amended to allow writes/egress (stage 2). Ungrounded read-like actions route to confirmation; ungrounded write-like actions are blocked. Reachable resources expand dynamically as prior actions succeed, building a dependency graph. This is a significant new defense layer against injection: even if an injected action passes all other checks, the TDG verifier blocks it unless the target resource traces to the user's stated goal or to outputs of prior legitimate actions.

15. **Phantom action detection.** Repeated denied actions (capability probes, unattributed egress attempts, taint bypass attempts) crossing configurable thresholds (default: 3 within 120 seconds) trigger structured `phantom_action_detected` audit events. This converts previously silent deny-and-continue behavior into observable compromise signals, enabling operator alerting on probing patterns.

16. **Skill drift is observable, not silent.** Schema-hash mismatches on reviewed skill tools still fail closed (same as v0.6.0), but now emit structured `SkillToolRegistrationDropped` audit events with skill name, version, tool name, and hash prefixes. Operators can distinguish between "skill tool not loaded because it was never registered" and "skill tool dropped because its schema changed after review."

## 7. Gaps and Weaknesses

### Taxonomy Category 3.1 (Secure Architectures)
- **Variable-level provenance tracking not implemented.** Taint operates at the content-block level, not CaMeL's per-variable level. The ArtifactLedger tracks endorsement per artifact, not per field within structured returns.

### Taxonomy Category 3.2 (Access Control)
- **No MCP/A2A access control.** The codebase does not implement Model Context Protocol or agent-to-agent authorization. Planned for v0.6.3.
- **No scoped approval tokens with TTL.** Per-action confirmation only; no pre-approval scopes.

### Taxonomy Category 3.3 (Runtime Verification)
- **No verify-before-commit for irreversible actions.** High-risk actions route to confirmation (human in the loop) rather than automated pre-execution analysis (VIGIL-style).
- **TDG resource grounding is heuristic.** Goal resource extraction uses regex patterns on user text to identify file paths and hosts. Adversarial goal phrasing could manipulate the initial grounding set (though this requires the attacker to control the user's goal text, which is a high bar).

### Taxonomy Category 3.4 (Detection and Filtering)
- **ML classifier is one model.** PromptGuard 2 is a single model with known limitations (training distribution, adversarial robustness). Pattern + YARA + ML is significantly better than pattern alone, but adaptive attackers will find bypasses.
- **YARA dependency optional.** Fallback regex patterns are less precise than compiled YARA rules.

### Taxonomy Category 3.5 (Model-Level Hardening)
- **Action monitor uses simple heuristics.** String matching on a small token set is easily evaded.
- **PromptGuard is input classification, not model hardening.** The model itself is not fine-tuned for injection resistance (SecAlign-style). PromptGuard screens inputs before they reach the model but cannot prevent the model from being influenced by payloads that pass the classifier.

### Taxonomy Category 3.6 (Boundary Marking)
- **Evidence blobs stored unencrypted.** Metadata MAC provides tamper detection but not confidentiality. Encryption hook point exists; KMS/HSM integration deferred to v0.6.2.

### Taxonomy Category 3.7 (Formal Methods)
- **No formal verification.** No machine-checked proofs for taint system, COMMAND/TASK boundary, or policy merge monotonicity.

### Cross-cutting
- **No external benchmark evaluation.** No ASR/utility numbers against AgentDojo or ASB. Security claims cannot be directly compared against published academic systems.

## 8. Delta from v0.5 Analysis

### Gaps closed in v0.6.0

| v0.5 Gap | v0.6.0 Resolution | Impact |
|----------|-------------------|--------|
| COMMAND/TASK not first-class runtime concept | `SessionRole` enum + `TaskEnvelope` with immutable frozen envelopes | **High**: Establishes architectural trust boundary that is more reliable than per-call enforcement |
| `EvidenceStore` without endorsement tracking | `ArtifactLedger` with lifecycle states, endorsement states, metadata MAC | **High**: Evidence refs survive restarts, tampering is detectable, endorsement is auditable |
| Summary barrier not mandatory | `_build_task_summary_firewall_checkpoint()` as architectural requirement | **High**: TASK output cannot reach orchestrator without firewall pass |
| Credential scoping session-level only | Per-task-envelope `credential_refs` with `enforce_explicit_credential_refs` | **High**: Least-privilege credentials per task |
| No approval provenance | Session/task/nonce/timestamp binding | **Medium**: Prevents approval replay across contexts |
| No typed argument validation | Semantic atom validators for 7 types | **Medium**: Structural defense against argument injection |
| No browser tools | 6-tool browser surface with TOCTOU prevention | **Medium**: High-risk surface with proper enforcement model |
| Supply chain limited to skill signatures + pinned deps | Full OIDC + SBOM + attestations + pip-audit + pinned CI + zizmor + adapter lockdown | **High**: End-to-end tamper-evident supply chain |

### Gaps closed in v0.6.1

| v0.6.0 Gap | v0.6.1 Resolution | Impact |
|------------|-------------------|--------|
| Control plane in-process (coding convention only) | OS-level process isolation via Unix socket sidecar with UID+PID peer authorization | **High**: Compromised agent runtime cannot directly access control plane internals |
| No ML-based injection classifier | PromptGuard 2 local ONNX inference with signed model-packs, three postures, three-tier thresholds | **High**: First ML classifier in open-source agent framework; merges with pattern+YARA via max() |
| No tool dependency graph verification | TDG verification traces actions to committed intent; ungrounded reads → confirmation, ungrounded writes → block | **High**: Blocks injected actions even when they pass all other checks if target doesn't trace to user goal |
| Schema-hash drift was silent | Structured `SkillToolRegistrationDropped` audit events on drift | **Medium**: Operators can now detect and investigate skill tampering |
| YARA unicode steganography rule broken at compile time | Fixed compile path for the shipped rule | **Low**: Restores detection of unicode steganography injection vectors |

### Gaps remaining from v0.5

| Gap | Status | Planned |
|-----|--------|---------|
| Variable-level provenance | Still content-block level | No timeline |
| Evidence encryption at rest | Hook point exists, not implemented | v0.6.2 |
| Scoped approval tokens with TTL | Not implemented | No timeline |
| Differential execution | Lightweight wrapper only | No timeline |
| External benchmark evaluation | Not implemented | No timeline |
| Formal noninterference proof | Not implemented | No timeline |

### New gaps identified in v0.6.0 review (status in v0.6.1)

- **Browser tool surface expands attack surface.** Attacker-controlled web pages are now directly processed by the agent. While the confirmation + binding-hash model is sound, browser automation is inherently high-risk. *Status: unchanged in v0.6.1.*
- **Schema-hash inventory is registration-time only.** Tool schemas are verified at registration but not continuously monitored at runtime for hot-swap attacks. *Status: v0.6.1 adds audit events on drift but does not add continuous runtime monitoring.*
- **Untrusted-trigger policy is binary.** Background tasks triggered by tainted payloads either require confirmation or are rejected; there is no intermediate policy (e.g., "allow read-only tools, require confirmation for writes"). *Status: unchanged in v0.6.1.*

### New gaps identified in v0.6.1 review

- **TDG resource grounding depends on goal text parsing.** The `ExecutionTraceVerifier` extracts file paths and hosts from the user's goal text via regex. Adversarial goal phrasing could manipulate the initial grounding set, though this requires the attacker to control the user's message (a high bar).
- **PromptGuard model is a single point of ML detection.** One model (PromptGuard 2) with known training distribution limitations. Not a replacement for defense-in-depth, but a significant addition to the detection stack.
- **Sidecar peer authorization is UID+PID only.** The Unix socket peer credential check validates the connecting process's UID and PID but does not use additional kernel security mechanisms (e.g., SELinux labels, seccomp). Sufficient for the current threat model (same-user compromise boundary), but not a hard isolation primitive against a root-level attacker.

## 9. Key Findings

1. **v0.6.1 closes three of the four gaps identified in the v0.6.0 analysis.** Control-plane process isolation, ML-based injection classification, and tool dependency graph verification were all identified as planned-for-v0.6.1 in the v0.6.0 review. All three are now implemented and tested. The only v0.6.0-planned item not yet delivered is differential execution (post-v0.6.1).

2. **The control-plane isolation gap is now closed.** The v0.6.0 analysis identified in-process control plane as the most significant remaining architectural weakness. v0.6.1's Unix socket sidecar with peer credential authorization provides OS-level process isolation. A compromised agent runtime cannot directly access control plane internals because they live in a separate address space. This makes shisad's CaMeL-inspired architecture materially closer to the academic ideal of separated trust domains.

3. **shisad is now the first open-source agent framework to deploy an ML-based injection classifier.** PromptGuard 2 running as local ONNX inference with signed model-packs closes the gap between production open-source frameworks and Meta's LlamaFirewall deployment. The three-posture system (off/best_effort/required) with `max()` score merging means the ML classifier can only escalate findings from the pattern+YARA layers, preserving defense-in-depth. The signed model-pack supply chain prevents model tampering.

4. **Tool Dependency Graph verification is a novel production defense.** No other production framework verifies that tool actions trace back to committed user intent through a dependency graph. The two-stage plan model (precontent reads → postevidence writes) with dynamic reachability tracking is a practical approximation of CaMeL's structured plan verification without requiring the model to generate restricted programs. This blocks a class of attacks where injected actions match the plan's allowed kinds but target unrelated resources.

5. **Supply chain hardening is now best-in-class and extends to ML artifacts.** Beyond the v0.6.0 OIDC + SBOM + attestation pipeline, v0.6.1 adds signed model-packs for PromptGuard artifacts. The ML model supply chain -- often overlooked -- is now subject to the same integrity verification as code artifacts.

6. **The endorsement/taint separation continues to hold.** The ArtifactLedger's endorsement lifecycle (unendorsed → user_endorsed → system_endorsed) is tracked separately from taint labels. `USER_ENDORSED` does not strip `UNTRUSTED`. This means the security model holds even when users routinely approve everything -- a critical property that no other production framework implements.

7. **The production/academic gap has narrowed further.** v0.6.1 closes three gaps that previously separated production from academic systems: process isolation for the control plane (CaMeL-like trust domain separation), ML-based injection classification (LlamaFirewall-like neural detection), and tool dependency graph verification (CaMeL-like plan verification). The remaining gaps vs. academic state-of-the-art are: variable-level provenance tracking, formal noninterference proofs, causal independence detection (MELON), and capability-token-gated tool access.

8. **The review process continues as a security feature.** v0.6.1's five hardening deliveries (H1-H5) each went through reviewer remediation rounds, with security findings traced to fix commits. H1-H5 collectively address the three planned items and add two additional improvements (phantom detection, skill drift observability) identified during the hardening process.
