# shisad v0.6.0 Security Analysis (Source Code Review)

**Repository:** https://github.com/shisa-ai/shisad
**Version:** v0.6.0 (released 2026-04-03)
**Point-in-time:** 2026-04-04
**Language:** Python
**Category:** Security-focused
**Prior analyses:** ANALYSIS-shisad.md (docs-only, 2026-03-05, commit a61a0d8), ANALYSIS-shisad-v0.5.md (source code review, 2026-03-31, commit 016b39b)

## 1. Overview

shisad is a persistent AI agent daemon -- a long-running service that manages conversations, executes tool calls, and takes actions on behalf of a user across multiple channels (CLI, Discord, Slack, Telegram, Matrix). The core thesis is that the LLM proposes actions but the runtime decides what executes, enforced through a multi-layered security architecture.

v0.6.0 is described as the "orchestration-foundation release" -- it converts the previously flat session model into a formal two-tier COMMAND/TASK runtime with explicit trust boundaries, hardens the supply chain from source to PyPI, and expands the tool surface to include browser automation under the same enforcement model as core tools.

**Codebase size (v0.6.0):** ~51,500 lines of Python source across `src/shisad/`, ~51,900 lines of tests across `tests/`. 1,368 test functions (84 adversarial, 169 integration, 1,115 unit). 367 Python files. Test/source ratio: 1.01x.

**Delta from v0.5:** 58 commits, 192 files touched, 16,742 insertions, 2,895 deletions. Six milestone deliveries (G0, M1-M6) plus supply chain hardening.

**What changed (executive summary):**

| Area | v0.5 Status | v0.6 Status |
|------|-------------|-------------|
| COMMAND/TASK separation | Conceptual; session primitives only | First-class runtime: `SessionRole` enum, immutable `TaskEnvelope`, mandatory summary-firewall checkpoint |
| Evidence system | `EvidenceStore` with plaintext blobs | Structured `ArtifactLedger` with lifecycle states, endorsement tracking, HMAC metadata MAC, restart-stable refs |
| Credential scoping | Session-level capability set | Per-task-envelope credential refs with `enforce_explicit_credential_refs` |
| Approval provenance | Nonce-based confirmation | Session/task/timestamp-bound provenance; non-portable across boundaries |
| Typed validation | Schema validation only | Semantic atom validators for URLs, command_tokens, workspace_paths, credential_refs |
| Browser tools | Not implemented | 6-tool browser surface with confirmation-gated writes and element-binding hash |
| Supply chain | Ed25519 skill signatures + pinned deps | + OIDC trusted publishing + SBOM + attestations + pip-audit + pinned CI actions + zizmor + adapter lockdown |
| Web tools | Not implemented | `web.search` + evidence-wrapped `web.fetch` |
| Test coverage | ~100+ unit, ~20+ integration, ~14 adversarial files | 1,368 test functions (84 adversarial); ~4,000+ new test lines |

## 2. Security Architecture

### 2.1 Design Philosophy

Unchanged from v0.5 -- "security enables functionality." The default policy grants all capabilities and sets `default_deny: false`. Security enforcement happens at execution time through the PEP pipeline, control-plane consensus, and sandbox isolation. v0.6.0 adds a new principle: **architectural trust boundaries are more reliable than runtime checks alone**. The COMMAND/TASK split encodes trust separation into the session model itself rather than relying solely on per-call enforcement.

### 2.2 Core Security Primitives (v0.6.0 State)

**Taint tracking** (`security/taint.py`): Unchanged from v0.5. Six `TaintLabel` values (`UNTRUSTED`, `SENSITIVE_EMAIL`, `SENSITIVE_FILE`, `SENSITIVE_CALENDAR`, `USER_CREDENTIALS`, `USER_REVIEWED`). Worst-case union propagation. The key property holds: `evidence.promote` produces `USER_REVIEWED`, not `TRUSTED` -- endorsement does not launder provenance.

**PEP** (`security/pep.py`): The 8-check pipeline from v0.5 is preserved and extended. New in v0.6.0:
- **Credential scope enforcement** (line 600-612): When `context.enforce_explicit_credential_refs` is true (always true for SUBAGENT sessions), every credential_ref in a tool call is checked against the task envelope's allowed set. Out-of-scope refs are rejected.
- **Typed semantic validation**: Tool arguments tagged with semantic types (`url`, `command_token`, `workspace_path`, `credential_ref`, `evidence_ref`) are validated by `is_valid_semantic_value()` in `core/tools/registry.py` (lines 71-107). Prose-bearing URLs, whitespace-bearing command tokens, and instructional content in structured fields are rejected before reaching the PEP's policy checks.

**Context scaffold** (`core/context.py`, `security/spotlight.py`): Unchanged from v0.5. Three-tier prompt construction with cryptographically random delimiters.

**Control plane engine** (`security/control_plane/engine.py`): Unchanged from v0.5. Five independent voters on metadata-only payloads.

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

### 2.3 Threat Model

v0.6.0 extends the v0.5 threat model with three new threat categories:

- **Cross-boundary taint laundering**: A compromised TASK agent could attempt to smuggle tainted content back to the orchestrator through the return boundary. Addressed by the mandatory summary-firewall checkpoint and the ArtifactLedger's taint-preserving endorsement model.
- **Approval replay attacks**: An attacker could attempt to replay a legitimate approval in a different task/session context. Addressed by approval provenance binding (session + task + nonce + timestamp).
- **Browser DOM-drift attacks**: Attacker-controlled pages could change between approval and execution. Addressed by element-binding hash verification and source URL binding.

The threat model also now explicitly covers supply chain attacks referencing real-world incidents: LiteLLM compromise (2026-03-24), ClawdHub skill poisoning, and Cline malware distribution.

### 2.4 Design-to-Implementation Gap (v0.6.0 Assessment)

**Gaps closed from v0.5:**

| v0.5 Gap | v0.6 Status | Component |
|----------|-------------|-----------|
| COMMAND/TASK agent separation conceptual only | **Closed**: First-class `SessionRole` + `TaskEnvelope` with immutable envelopes | `core/types.py`, `scheduler/schema.py`, `daemon/handlers/_impl_session.py` |
| ArtifactLedger proposed but not implemented | **Closed**: Structured ledger with lifecycle, endorsement, metadata MAC | `core/evidence.py:240-781` |
| Summary barrier not a mandatory checkpoint | **Closed**: `_build_task_summary_firewall_checkpoint()` is mandatory | `daemon/handlers/_impl_session.py:171` |
| No typed argument validation beyond schema | **Closed**: Semantic atom validators for 7 field types | `core/tools/registry.py:71-107` |
| Credential scoping session-level only | **Closed**: Per-task-envelope credential refs | `security/pep.py:600-612` |
| No approval provenance binding | **Closed**: Session/task/nonce/timestamp-bound provenance | `daemon/handlers/_impl_confirmation.py` |

**Remaining gaps:**

- **Variable-level provenance tracking**: Still operates at content-block level, not CaMeL's per-variable level.
- **Evidence encryption at rest**: Metadata MAC provides tamper detection but blobs remain unencrypted. Encryption hook point exists; KMS/HSM integration deferred to v0.6.2.
- **In-process control plane**: Metadata boundary between control plane and agent runtime is coding convention, not OS-level process isolation. Planned for v0.6.1.
- **Scoped approval tokens with TTL**: Still per-action confirmation only; no pre-approval tokens (e.g., "approve all fetches to reuters.com for 30 minutes").
- **Differential execution**: Lightweight wrapper exists, not the full three-tier system.
- **No MCP/A2A access control**: Planned for v0.6.3.
- **No ML-based injection classifier**: PromptGuard 2 integration planned for v0.6.1.
- **No formal noninterference proof**: Taint system follows IFC principles but has no machine-checked proofs.

## 3. Mapping to Defense Taxonomy

### 3.1 Secure Architectures by Construction

**Rating: Strong** (upgraded basis from v0.5)

v0.5 already had the metadata-only PEP and three-tier context scaffold. v0.6.0 adds the COMMAND/TASK dual-agent architecture as a first-class runtime concept:

- `SessionRole` enum (`ORCHESTRATOR`/`SUBAGENT`) is immutable at session creation (`core/types.py:130`).
- `TaskEnvelope` carries frozen capability snapshots and credential refs that cannot be widened post-creation (`scheduler/schema.py:38`).
- TASK→COMMAND handoffs must pass a mandatory summary-firewall checkpoint (`daemon/handlers/_impl_session.py:171`).
- The structured `ArtifactLedger` (`core/evidence.py:240`) tracks artifact lifecycle and endorsement state with HMAC-bound metadata. Endorsement does not strip taint.
- TASK close-gate self-check: Before handoff completion, the TASK agent inspects the original task description to detect injection-driven drift.

This is the first production implementation of the CaMeL-inspired dual-agent architecture with explicit trust boundaries. The gap vs. CaMeL: provenance is tracked at the content-block level, not per-variable; and the control plane is in-process, not OS-isolated.

### 3.2 Access Control and Governance

**Rating: Strong** (strengthened from v0.5)

v0.5 had session capability sets, most-restrictive-wins policy merge, per-tool allowlists, and argument DLP. v0.6.0 adds:

- **Typed semantic atom validation** (`core/tools/registry.py:71-107`): Seven field types with specific validation rules. URLs must have scheme+hostname and no whitespace. Command tokens reject whitespace and instructional patterns. Workspace paths reject `..` traversal and instructional text. Credential refs, evidence refs, and thread IDs must match `^[A-Za-z0-9][A-Za-z0-9._:-]{0,127}$`.
- **Task-envelope credential scoping** (`security/pep.py:600-612`): SUBAGENT sessions have `enforce_explicit_credential_refs=True`. Every credential_ref is checked against the task envelope's allowed set. Missing or out-of-scope refs fail closed.
- **Resource-scope enforcement** (`daemon/handlers/_task_scope.py:11-37`): Task resource scopes (e.g., `thread-id:12345`) prevent cross-scope tool access even when credentials are valid.
- **Approval provenance binding**: Approvals are non-portable across task/session boundaries.
- **Untrusted-trigger policy**: Background tasks triggered by tainted event payloads either require confirmation or are rejected outright, controlled by `untrusted_payload_action` in the task envelope.

### 3.3 Runtime Verification and Policy Enforcement

**Rating: Strong** (strengthened from v0.5)

v0.5 had the PEP 8-check pipeline, 5-voter consensus, behavioral sequence analysis, plan commitment verification, rate limiting, and lockdown escalation. v0.6.0 adds:

- **Browser element-binding hash** (`executors/browser.py:968-990`): SHA256 hash of element properties (kind, label, selector, href, form_action, form_method, destination). Verified at execution time to prevent TOCTOU attacks where DOM changes between approval and execution.
- **Source/destination URL binding**: Browser write confirmations carry the approved source URL. Navigation between approval and execution invalidates the confirmation.
- **Tool-schema-hash drift detection** (`core/tools/registry.py:122-145`): Skill-declared tools register with expected schema hashes. Hash mismatch blocks re-registration (fail-closed), detecting skill tampering between install and runtime.
- **TASK close-gate self-check**: Before delegated handoff completes, the TASK agent inspects the original task description against its output to detect injection-driven drift.
- **Approval provenance**: Every approval carries session ID, task envelope ID, timestamp, and one-time nonce. Replay across boundaries fails.

### 3.4 Detection, Filtering, and Firewalls

**Rating: Strong** (strengthened from v0.5)

v0.5 had the content firewall (pattern + YARA), multi-layer base64 decoding, secret/PII detection, and output firewall. v0.6.0 adds:

- **Terminal control-sequence sanitization**: Strips ANSI CSI, OSC, DCS/APC/PM/SOS sequences, stray ESC, and C0/C1 control characters from evidence rendering. Prevents terminal escape injection.
- **Browser DOM-drift detection**: Element-binding hash mechanism detects when attacker-controlled pages modify DOM between approval and execution.
- **Supply chain detection layers**:
  - `pip-audit --require-hashes` in publish workflow for known-vulnerability detection
  - `dependency-review` GitHub Action on PRs for supply chain scanning
  - `zizmor` workflow linting for CI/CD security issues
  - `uv lock --check` lockfile drift guard
  - Tool-schema-hash inventory for skill drift detection
  - `SHISAD_REQUIRE_LOCAL_ADAPTERS` flag to prevent runtime npx remote fetches

### 3.5 Model-Level Hardening

**Rating: Minimal** (unchanged from v0.5)

The action monitor still uses simple heuristics. The LLM is explicitly treated as untrusted. PromptGuard 2 integration planned for v0.6.1.

### 3.6 Boundary Marking and Cryptographic Provenance

**Rating: Strong** (strengthened from v0.5)

v0.5 had spotlighting with random delimiters, three-tier context placement, policy integrity (SHA256 + SIGHUP), skill Ed25519 signatures, and the credential broker. v0.6.0 adds:

- **Mandatory TASK→COMMAND summary-firewall checkpoint**: Architectural boundary enforcement, not just content filtering. TASK output cannot reach orchestrator context without passing the checkpoint.
- **ArtifactLedger metadata MAC** (`core/evidence.py:499`): HMAC-SHA256 over all ref fields using per-instance salt. Tampered or stripped MACs cause refs to be dropped on load.
- **Approval provenance binding**: Session/task/nonce/timestamp attached to every approval event. Non-portable across boundaries.
- **OIDC trusted publishing** (`.github/workflows/publish.yml`): Eliminates long-lived PyPI credentials. Uses GitHub's OpenID Connect for identity verification.
- **SBOM generation**: Anchore SBOM action produces SPDX 3.0 JSON attached to GitHub Release.
- **Build provenance attestations**: GitHub Actions `attest-build-provenance` creates attestations for wheel artifacts, verifiable by consumers.
- **Tool-schema-hash inventory**: Persisted schema hashes detect skill tool tampering.

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

### 4.2 Supply Chain Hardening (`.github/workflows/`)

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

### 4.4 Dependency Changes

| Package | v0.5 Version | v0.6 Version | Reason |
|---------|-------------|-------------|--------|
| cryptography | 45.0.7 | 46.0.6 | CVE-2026-34073, CVE-2026-26007 |
| aiohttp | 3.13.3 | 3.13.5 | Security patches |
| Pygments | 2.19.2 | 2.20.0 | Maintenance |

All direct + transitive dependencies resolved via `uv.lock` with SHA256 integrity hashes. CI install uses `--frozen` + `--exclude-newer P7D`.

## 5. Production Readiness

### 5.1 Maturity Level

**v0.5 → v0.6 progression indicators:**

- Source code grew from ~46.5K to ~51.5K lines (11% increase).
- Test code grew from ~43.7K to ~51.9K lines (19% increase). Test/source ratio crossed 1.0x.
- Test functions: 1,368 total (84 adversarial, 169 integration, 1,115 unit).
- CI pipeline expanded from basic lint+test to 7 jobs covering security runtime, adversarial gating, dependency review, and workflow linting.
- Supply chain: from pinned deps + Ed25519 skill signatures to full OIDC trusted publishing with SBOM, attestations, and hash-verified auditing.
- First PyPI publication using trusted publishing workflow (v0.6.0).

### 5.2 Test Coverage (v0.6.0)

**New test files:**

| File | Lines | Coverage |
|------|-------|---------|
| `tests/adversarial/test_adversarial_task_handoffs.py` | 259 | Cross-session taint laundering, orchestrator context leakage, capability-snapshot immutability |
| `tests/integration/test_task_session_isolation.py` | 2,001 | TASK/ORCHESTRATOR role separation, session boundaries, policy inheritance |
| `tests/integration/test_task_ledger_scaffold.py` | 472 | ArtifactLedger persistence, metadata MAC validation, endorsement lifecycle |
| `tests/unit/test_browser_toolkit.py` | 795 | Element binding hash, confirmation context, URL validation, hardened isolation |
| `tests/unit/test_skill_tool_registration.py` | 496 | Tool schema hash verification, registry integrity, drift detection |

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

## 7. Gaps and Weaknesses

### Taxonomy Category 3.1 (Secure Architectures)
- **Variable-level provenance tracking not implemented.** Taint operates at the content-block level, not CaMeL's per-variable level. The ArtifactLedger tracks endorsement per artifact, not per field within structured returns.
- **Control plane in-process.** The metadata boundary between control plane and agent runtime is enforced by coding convention, not OS-level process isolation. Planned for v0.6.1.

### Taxonomy Category 3.2 (Access Control)
- **No MCP/A2A access control.** The codebase does not implement Model Context Protocol or agent-to-agent authorization. Planned for v0.6.3.
- **No scoped approval tokens with TTL.** Per-action confirmation only; no pre-approval scopes.

### Taxonomy Category 3.3 (Runtime Verification)
- **No tool dependency graph verification.** Plan commitment checks action kinds and counts but does not construct a TDG. An injected action matching the plan's allowed kinds would pass.
- **No verify-before-commit for irreversible actions.** High-risk actions route to confirmation (human in the loop) rather than automated pre-execution analysis (VIGIL-style).

### Taxonomy Category 3.4 (Detection and Filtering)
- **Pattern-based classifier has inherent limitations.** Adaptive attackers can craft payloads that evade regex + YARA. The `SemanticClassifier` protocol hook exists but no ML classifier is included. PromptGuard 2 integration planned for v0.6.1.
- **YARA dependency optional.** Fallback regex patterns are less precise than compiled YARA rules.

### Taxonomy Category 3.5 (Model-Level Hardening)
- **Action monitor uses simple heuristics.** String matching on a small token set is easily evaded.

### Taxonomy Category 3.6 (Boundary Marking)
- **Evidence blobs stored unencrypted.** Metadata MAC provides tamper detection but not confidentiality. Encryption hook point exists; KMS/HSM integration deferred to v0.6.2.

### Taxonomy Category 3.7 (Formal Methods)
- **No formal verification.** No machine-checked proofs for taint system, COMMAND/TASK boundary, or policy merge monotonicity.

### Cross-cutting
- **No external benchmark evaluation.** No ASR/utility numbers against AgentDojo or ASB. Security claims cannot be directly compared against published academic systems.

## 8. Delta from v0.5 Analysis

### Gaps closed

| v0.5 Gap | v0.6 Resolution | Impact |
|----------|----------------|--------|
| COMMAND/TASK not first-class runtime concept | `SessionRole` enum + `TaskEnvelope` with immutable frozen envelopes | **High**: Establishes architectural trust boundary that is more reliable than per-call enforcement |
| `EvidenceStore` without endorsement tracking | `ArtifactLedger` with lifecycle states, endorsement states, metadata MAC | **High**: Evidence refs survive restarts, tampering is detectable, endorsement is auditable |
| Summary barrier not mandatory | `_build_task_summary_firewall_checkpoint()` as architectural requirement | **High**: TASK output cannot reach orchestrator without firewall pass |
| Credential scoping session-level only | Per-task-envelope `credential_refs` with `enforce_explicit_credential_refs` | **High**: Least-privilege credentials per task |
| No approval provenance | Session/task/nonce/timestamp binding | **Medium**: Prevents approval replay across contexts |
| No typed argument validation | Semantic atom validators for 7 types | **Medium**: Structural defense against argument injection |
| No browser tools | 6-tool browser surface with TOCTOU prevention | **Medium**: High-risk surface with proper enforcement model |
| Supply chain limited to skill signatures + pinned deps | Full OIDC + SBOM + attestations + pip-audit + pinned CI + zizmor + adapter lockdown | **High**: End-to-end tamper-evident supply chain |

### Gaps remaining from v0.5

| Gap | Status | Planned |
|-----|--------|---------|
| Variable-level provenance | Still content-block level | No timeline |
| Evidence encryption at rest | Hook point exists, not implemented | v0.6.2 |
| Process isolation for control plane | In-process, coding convention | v0.6.1 |
| Scoped approval tokens with TTL | Not implemented | No timeline |
| Differential execution | Lightweight wrapper only | No timeline |
| External benchmark evaluation | Not implemented | No timeline |
| Formal noninterference proof | Not implemented | No timeline |

### New gaps identified in v0.6 review

- **Browser tool surface expands attack surface.** Attacker-controlled web pages are now directly processed by the agent. While the confirmation + binding-hash model is sound, browser automation is inherently high-risk.
- **Schema-hash inventory is registration-time only.** Tool schemas are verified at registration but not continuously monitored at runtime for hot-swap attacks.
- **Untrusted-trigger policy is binary.** Background tasks triggered by tainted payloads either require confirmation or are rejected; there is no intermediate policy (e.g., "allow read-only tools, require confirmation for writes").

## 9. Key Findings

1. **v0.6.0 closes the single largest gap from v0.5.** The COMMAND/TASK agent separation was identified as the #1 remaining improvement in the v0.5 analysis. It is now a first-class runtime concept with `SessionRole`, `TaskEnvelope`, mandatory summary-firewall checkpoint, and approval provenance binding. This makes shisad the first production framework to implement CaMeL-inspired dual-agent architecture with explicit trust boundaries.

2. **Supply chain hardening is now best-in-class across the production agent framework landscape.** OIDC trusted publishing, SBOM, build attestations, pip-audit, pinned CI actions, dependency-review gates, zizmor workflow linting, lockfile drift guards, adapter runtime lockdown, and tool-schema-hash inventory collectively create the most comprehensive supply chain posture among the six frameworks compared in ANALYSIS-frameworks-comparison.md.

3. **The endorsement/taint separation holds through the new architecture.** The ArtifactLedger's endorsement lifecycle (unendorsed → user_endorsed → system_endorsed) is tracked separately from taint labels. `USER_ENDORSED` does not strip `UNTRUSTED`. This means the security model holds even when users routinely approve everything -- a critical property that no other production framework implements.

4. **Browser tool surface is the highest-risk new addition, and the enforcement model is proportionate.** Confirmation-gated writes, element-binding hash, source URL binding, hardened isolation defaults, and fail-closed degraded mode policy represent a careful approach to expanding into attacker-controlled content (web pages). The TOCTOU prevention via binding hashes is novel among production frameworks.

5. **The production/academic gap has narrowed but remains significant.** v0.6.0's COMMAND/TASK split with ArtifactLedger is the closest production approximation of CaMeL's architecture. But CaMeL's variable-level provenance tracking, formal noninterference guarantees, and capability-token-gated tool access remain beyond current production capabilities. The planned v0.6.1 additions (PromptGuard 2, control-plane process isolation) would further close this gap.

6. **The review process itself is a security feature.** The shisad-dev records show that M4 through M6 each went through 4-7 reviewer remediation rounds, with specific security findings traced to fix commits. M6 alone had 4 remediation passes (M6.R, M6.RR, M6.RRR, M6.RRRR). This level of review discipline -- documented with evidence -- is itself a production-readiness indicator.
