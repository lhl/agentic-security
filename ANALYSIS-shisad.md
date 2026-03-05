# shisad Security Analysis (Design → agentic-security taxonomy)

*Inputs:* `shisad/` security architecture bundle (exported 2026-03-05; source commit `a61a0d8`) and repo-wide `ANALYSIS.md`.

This document is a **design- and wiring-focused gap analysis**, not an external security audit. It answers:
- What are shisad’s **high-level security goals** and **core primitives**?
- How does shisad map onto the threat/defense structure in `ANALYSIS.md`?
- What are the **current gaps** called out by shisad’s own design/audit notes?
- What can we **adopt quickly** vs what likely needs **new design work**?

## 1) High-level goals (what “secure” means for shisad)

These are the governing “north stars” across the shisad docs.

1. **Intent preservation (fidelity):** do what the user actually asked for, and prevent untrusted inputs from steering actions. The core question is provenance: **“Who asked for this?”** (`shisad/docs/DESIGN-PHILOSOPHY.md`, `shisad/docs/ADR-command-task-architecture.md`).
2. **Security enables functionality (not feature removal):** avoid “safe by disabling.” Prefer per-call enforcement + confirmations over lockdowns and blanket denials (`shisad/docs/DESIGN-PHILOSOPHY.md`, `shisad/docs/PLAN-security.md`).
3. **Defense-in-depth:** assume prompt injection sometimes succeeds; constrain damage even if the model is fully compromised (`shisad/docs/PLAN-security.md`).
4. **Default-grant capabilities, enforce per-call:** capabilities exist so the product is usable; enforcement happens at execution time via the PEP and resource policies (`shisad/docs/DESIGN-PHILOSOPHY.md`, `shisad/docs/PLAN-security.md`).
5. **Graduated response ladder:** **auto-approve (clear user-goal)** → confirm (ambiguous provenance/risk) → deny (specific action) → lockdown (multi-signal anomaly). Avoid “deny the assistant” cascades (`shisad/docs/DESIGN-PHILOSOPHY.md`, `shisad/docs/PLAN-security.md`).
6. **Control-plane integrity is non-negotiable:** data-plane inputs must not mutate policy/skills/guardrails except via an explicit privileged workflow (`shisad/docs/PLAN-security.md`, `shisad/docs/v0.4/ANALYSIS-admin-self-modification.md`).
7. **Auditability and operational recovery:** incidents must be explainable, containable, and reversible with runbooks, logs, and rollback paths (`shisad/docs/runbooks/*`, `shisad/docs/PLAN-tracing.md`).

## 2) Core security primitives (what shisad is building with)

This section lists the **architectural primitives** that show up repeatedly in the shisad design docs. Think of these as the “security vocabulary” we can map onto `ANALYSIS.md`.

### 2.1 Instruction/data boundary + provenance

- **Control plane vs data plane:** control plane (policy, tool schemas, skills, identity, enforcement code) must be protected from data-plane influence (untrusted messages/content/tool outputs/memory) (`shisad/docs/PLAN-security.md`, `shisad/docs/ANALYSIS-security-casestudies.md`).
- **Trust levels + context tiers:** TRUSTED vs SEMI_TRUSTED vs UNTRUSTED, with strict prompt placement rules (Trusted/Internal/Untrusted tiers) (`shisad/docs/PLAN-multiturn-taint.md`, `shisad/docs/PLAN-context-scaffold.md`).
- **Spotlighting / boundary marking:** keep user goal/instructions visually and structurally separated from untrusted evidence so the model (and tooling around it) can’t silently treat data as instruction (`shisad/docs/PLAN-security.md`, `shisad/docs/PLAN-context-scaffold.md`).
- **Taint labels + provenance annotation:** derived content carries immutable lineage; summaries don’t “clean” taint, they remain provenance-annotated (`shisad/docs/PLAN-multiturn-taint.md`).

### 2.2 Stateless context as a safety primitive

shisad explicitly treats “LLMs have no state between calls” as an *enabler*:
- **Checkpoint rollback / quarantine** (future turns can be rebuilt without tainted entries).
- **Context forking** for different privilege modes or tasks.
- **Clean-room sessions** for privileged workflows.
- **Differential execution** (compare plans with/without suspected taint) (`shisad/docs/PLAN-security.md`).

### 2.3 Privilege separation: COMMAND vs TASK agents

The design intent is a long-lived, intent-authoritative **COMMAND/orchestrator** that stays clean by default, plus scoped, ephemeral **TASK/subagents** that consume untrusted content and return structured results (`shisad/docs/PLAN-multiturn-taint.md`, `shisad/docs/ADR-command-task-architecture.md`).

Key primitives:
- **Scoped task envelopes** (minimal inputs/capabilities).
- **Structured return boundary**: deterministic metadata in Trusted, firewall’d SEMI_TRUSTED summaries in Internal, raw evidence stored out-of-band as UNTRUSTED.
- **ArtifactLedger (proposed)**: store raw artifacts encrypted at rest; track endorsement separately from provenance (`shisad/docs/ADR-command-task-architecture.md`).

### 2.4 Deterministic per-call enforcement: the PEP

The **Policy Enforcement Point (PEP)** is the “security kernel”: the model can only propose actions; the PEP decides. PEP checks include schema/tool allowlists, capability checks, object-level authorization, taint/sink rules, argument DLP (no raw credentials), provenance-aware egress controls, risk scoring → confirmation, and rate limits (`shisad/docs/PLAN-security.md`).

### 2.5 Policy authority and monotonicity (no widening via caller)

For external tool-exec paths, shisad’s policy model is explicitly **server-side floor + caller patch**, merged so the result is always at least as restrictive as server policy (“most restrictive wins”) (`shisad/docs/ADR-policy-source-authority.md`).

### 2.6 Credential proxying / “LLM never sees secrets”

shisad’s baseline credential model is:
- **No raw secrets in prompts or tool args**.
- Tools resolve credentials internally via references (`credential_ref`), with host binding and auditing (`shisad/docs/PLAN-security.md`).

Future hardening path (explicitly called out): move to **proxy-level secret injection** when threat model expands to compromised executors/computer-use (`shisad/docs/PLAN-security.md`).

### 2.7 Supply chain hardening for skills

Skills are treated as an attack surface requiring:
- explicit capability declarations
- vetting/scanning before install/enable
- signatures/trust anchors + revocation
- sandboxing and PEP mediation (“no bypass”) (`shisad/docs/v0.1/SECURITY-ANALYSIS.md`, `shisad/docs/ANALYSIS-skill-scanner.md`).

### 2.8 Observability, audit, and recovery

- **Append-only, tamper-evident audit logs** (hash-chained) and control-plane metadata-only logging (`shisad/docs/v0.1/SECURITY-ANALYSIS.md`).
- **Training-ready trace recorder** (planner messages + decision chain) with aggressive secret/PII redaction (`shisad/docs/PLAN-tracing.md`).
- **Operational runbooks**: incident response, rollback, key rotation, skill revocation (`shisad/docs/runbooks/*`).

## 3) Applying `ANALYSIS.md` to shisad (mapping + “what matters”)

This section mirrors the structure in `ANALYSIS.md` and annotates it with: (a) shisad primitives that already cover the area, (b) gaps called out in shisad docs, and (c) “likely-relevant” research clusters from `ANALYSIS.md`.

### 3.1 Threat landscape (Section 2 in `ANALYSIS.md`)

shisad’s threat model aligns with the standard “agent lethal trifecta” (private data + untrusted content + privileged actions) and explicitly includes:
- Indirect prompt injection (untrusted web/email/tool output)
- Memory poisoning / persistence mechanisms
- Tool/skill supply chain attacks
- Confused deputy and privilege escalation via tool misuse
- Data exfiltration via network and outbound messaging sinks (`shisad/docs/PLAN-security.md`, `shisad/docs/ANALYSIS-security-casestudies.md`).

What matters most for shisad:
- Anything that collapses the instruction/data boundary (IPI, taint laundering via summaries, “tool-tag spoofing”).
- Anything that bypasses per-call enforcement (scheduled tasks, external exec APIs, skill tool wiring).
- Anything that silently expands authority (self-modification workflows, skill installs, policy widening).

### 3.2 Defense taxonomy (Section 3 in `ANALYSIS.md`)

#### 3.2.1 Secure architectures by construction (3.1)

shisad already centers “secure-by-construction” primitives:
- control plane vs data plane separation
- COMMAND/TASK privilege separation + context forking
- PEP as a capability/authorization kernel
- stateless context rollback/quarantine patterns (`shisad/docs/PLAN-security.md`, `shisad/docs/PLAN-multiturn-taint.md`, `shisad/docs/ADR-command-task-architecture.md`).

Potentially adoptable from `ANALYSIS.md`:
- Explicit capability-security patterns (CaMeL-like separation) as a validation lens: ensure enforcement decisions are made without seeing untrusted content.
- Clear design for “instruction/data separation” representations (typed prompts, structured evidence blocks) to reduce ambiguity at boundaries.

#### 3.2.2 Access control and governance (3.2)

shisad maps strongly to this category:
- capability sets + resource policies
- provenance-aware egress authorization (“who asked for it?”)
- server-authoritative policy floors and monotonic merges (`shisad/docs/DESIGN-PHILOSOPHY.md`, `shisad/docs/ADR-policy-source-authority.md`).

Potentially adoptable from `ANALYSIS.md`:
- Formalized delegation models for multi-agent/task delegation (especially if/when MCP/A2A integration becomes a goal).
- More explicit object-level authorization models for “IDs as untrusted inputs” (message IDs, file handles, memory IDs).

#### 3.2.3 Runtime verification and policy enforcement (3.3)

shisad’s core runtime enforcement stack is:
- PEP gating + taint/sink rules
- plan commitment / trace verification concepts
- monitoring + rate limiting + lockdown as a last resort (`shisad/docs/PLAN-security.md`, `shisad/docs/v0.1/SECURITY-ANALYSIS.md`).

Potentially adoptable from `ANALYSIS.md`:
- Trace-as-program verification ideas (CFG/DFG/PDG-style checks) as a way to tighten plan-commitment and detect unjustified tool calls.
- “Verify-before-commit” patterns for irreversible actions (send/write/transfer): speculative planning + deterministic checks before side effects.

#### 3.2.4 Detection, filtering, and firewalls (3.4)

shisad already invests here, but treats it as *outer layers*, not a core boundary:
- ingress Content Firewall (normalize/classify/sanitize)
- TASK→COMMAND “summary barrier” firewall to prevent taint laundering
- output firewall/DLP/redaction (`shisad/docs/PLAN-security.md`, `shisad/docs/PLAN-context-scaffold.md`, `shisad/docs/ADR-command-task-architecture.md`).

Quick adoption candidate (already analyzed in shisad docs):
- Use an enterprise-grade skill scanner (YARA + AST/dataflow + LLM semantic analysis) as a drop-in for the skill vetting pipeline (`shisad/docs/ANALYSIS-skill-scanner.md`).

#### 3.2.5 Model-level hardening (3.5)

shisad explicitly does **not** treat the planner as a security boundary, but it does treat model tuning as important for reliability and reducing “unsafe proposals”:
- strict tool-calling contract + validation gates (`shisad/docs/SHISAD-MODEL.md`)
- monitor model can raise risk/confirmation but shouldn’t hard-block user-goal actions (`shisad/docs/PLAN-security.md`).

#### 3.2.6 Boundary marking and cryptographic provenance (3.6)

shisad’s boundary marking is primarily structural (spotlighting + trust tiers), plus operational integrity primitives:
- tamper-evident audit logs
- signed artifacts (skills/behavior packs) and trust stores as a control-plane integrity mechanism (`shisad/docs/v0.4/ANALYSIS-signatures-and-integrity.md`).

What to design next:
- How “signed + verified” artifacts interact with hot reload, rollback, and incident response (v0.4 goals).

#### 3.2.7 Formal methods and semantics (3.7)

shisad borrows many semantics-adjacent ideas (IFC-like taint/sink rules; capability systems), but mostly via pragmatic enforcement rather than formal proofs.

Low-effort, high-leverage direction:
- Make taint/sink policy rules *explicitly spec-derived* (from the “assets & sensitivity classes” section) and machine-checked for internal consistency (`shisad/docs/PLAN-security.md`).

### 3.3 Benchmarks and evaluation (Section 4 in `ANALYSIS.md`)

What shisad already has (per docs):
- adversarial/security test corpus and YARA assets (`shisad/docs/v0.1/M2-HANDOFF-security-corpus.md`)
- decision-chain tracing for offline analysis and training (`shisad/docs/PLAN-tracing.md`)

Gap relative to `ANALYSIS.md`:
- standardized, externally-comparable ASR/utility numbers against common agent benchmarks (requires adapters/harnesses).

### 3.4 Production readiness (Section 5 in `ANALYSIS.md`)

Strong signals in shisad docs:
- explicit runbooks for incident response, rollback, key rotation, skill revocation (`shisad/docs/runbooks/*`)
- policy authority semantics designed for future-proofing non-local transports (`shisad/docs/ADR-policy-source-authority.md`)

Design gap to watch:
- clean-room privileged workflows and self-modification need complete “apply + validate + rollback + signature” closure to avoid becoming the persistence substrate shisad is trying to avoid (`shisad/docs/v0.4/ANALYSIS-admin-self-modification.md`).

### 3.5 Recommended defense stack (Section 6 in `ANALYSIS.md`, shisad-specific)

Interpreting `ANALYSIS.md`’s “recommended defense stack” through shisad’s primitives:

- **Layer 1 — Architecture (non-negotiable):**
  - control/data plane separation + strict prompt tiers
  - COMMAND/TASK separation with artifact-based handoffs (needs closure on ArtifactLedger + orchestration wiring)
- **Layer 2 — Access control (non-negotiable):**
  - PEP as kernel + policy monotonicity (server floor) + object-level authorization
  - scheduler tasks must be routed through the same PEP path (gap called out)
- **Layer 3 — Model hardening (helpful, not a boundary):**
  - tool-calling protocol tuning + strong schema validation at inference (`shisad/docs/SHISAD-MODEL.md`)
- **Layer 4 — Runtime monitoring:**
  - plan commitment / trace verification + metadata-only control-plane veto paths
  - rate limiting + graduated response ladder (confirm/deny/lockdown)
- **Layer 5 — Detection/filtering (outer perimeter):**
  - content firewall + output firewall
  - skill vetting/scanners as supply-chain perimeter
- **Cross-cutting — Memory trust zones:**
  - gated writes + provenance retention + reversible updates (explicitly framed as invariants in shisad docs)

### 3.6 Open problems / research gaps (Section 7 in `ANALYSIS.md`, shisad lens)

The shisad bundle already names most of the hard parts; the `ANALYSIS.md` research gaps that look most relevant to shisad’s near-term roadmap are:
- **Secure proactivity** (background tasks) without turning confirmations into spam or allowing drift/exfil (ties to scheduler→PEP and scoped approvals).
- **Multi-agent scalability** without “taint laundering” (ties to ArtifactLedger and strict handoff contracts).
- **Standard evaluation** (comparable ASR/utility reporting) to validate the stack against adaptive attackers.

## 4) Current security gaps (from shisad’s own docs)

These items are explicitly called out as gaps/risks in the shisad bundle (or follow directly from stated non-claims).

### 4.1 Enforcement bypass risks (must close)

1. **Scheduler → PEP integration missing**: scheduled task execution is described as bypassing PEP evaluation in the architecture maturity audit; scheduled/triggered tasks are a persistence surface and must be PEP-gated (`shisad/docs/ANALYSIS-architecture-maturity.md`, `shisad/docs/PLAN-security.md` §4.4).
2. **Skill → ToolRegistry wiring unclear**: if skill-defined tools aren’t registered into the planner-visible tool surface in a well-defined way, you risk both (a) missing enforcement hooks and (b) “shadow tools” (planner can’t reason about what exists) (`shisad/docs/ANALYSIS-architecture-maturity.md`).
3. **Tool-level test template gap**: the architecture maturity audit calls out missing reusable tests for new tools (argument validation, output parsing, capability escalation), which is a reliability and security regression risk as the tool surface grows (`shisad/docs/ANALYSIS-architecture-maturity.md`).

### 4.2 Control-plane integrity gaps (design closure needed)

4. **Process isolation for control plane**: early implementation notes explicitly say control plane is “in-process” with a strict metadata boundary, while the longer-term plan prefers stronger isolation (separate process/container). This is a gap between “current enforced boundary” and “desired boundary” (`shisad/docs/v0.1/SECURITY-ANALYSIS.md`, `shisad/docs/PLAN-security.md`).
5. **Self-modification closure**: v0.4 proposes a safe self-mod workflow (proposal-only LLM + deterministic validators + signatures + rollback), but the security risk is that any missing piece becomes a wormable persistence substrate (`shisad/docs/v0.4/ANALYSIS-admin-self-modification.md`, `shisad/docs/v0.4/ANALYSIS-signatures-and-integrity.md`).

### 4.3 Multi-turn and multi-agent gaps (architecture closure needed)

6. **ArtifactLedger + endorsement semantics are still proposed**: without a first-class artifact store and endorsement-scoped approvals, multi-turn “read → decide → act” workflows risk either taint leakage (if you inline evidence) or usability collapse (if you can’t reference evidence safely) (`shisad/docs/ADR-command-task-architecture.md`, `shisad/docs/PLAN-multiturn-taint.md`).
7. **Decision fatigue mitigation needs concrete UX + policy shape**: scoped approval tokens are a proposed mitigation; needs precise semantics to avoid becoming blanket privilege escalation (`shisad/docs/ADR-command-task-architecture.md`).

### 4.4 Evaluation/ops gaps (needed for credibility)

8. **Manual verification for trace capture** is explicitly left open as a final step (`shisad/docs/IMPLEMENTATION-tracing.md`).
9. **Externally comparable security evaluation** (benchmarks, red-team harnesses, ASR/utility reporting) is not yet pinned to a standard suite in this bundle (see `ANALYSIS.md` Section 4 for what “good” looks like).

## 5) Easy adoptions (low design cost, high leverage)

These are “fast follow” items that match shisad’s existing architecture and appear implementable without redesigning the core.

1. **Skill scanner integration (YARA + AST/dataflow + LLM semantic) as a vetting gate**: shisad already analyzed the ecosystem options; adopting the Apache-licensed enterprise scanner (or its YARA subset) would quickly harden the skill supply chain (`shisad/docs/ANALYSIS-skill-scanner.md`).
2. **Standard benchmark harnessing**: wrap shisad scenarios into one or more standard agent-security benchmarks so we can report ASR/utility consistently with `ANALYSIS.md` (requires adapters, not new primitives).
3. **Deterministic “action justification” checks**: implement trace/plan-based dependency checks (tool call must be justified by a dependency on user goal + approved evidence) to tighten runtime verification without relying on probabilistic detectors (fits PEP + metadata-only control plane model).

## 6) Design work to consider (likely needs new primitives or deeper decisions)

1. **Control-plane isolation level**: decide whether the metadata boundary is the long-term “enough” boundary, or whether a separate control-plane process/container is a release-gating requirement (tradeoff: complexity vs assurance).
2. **ArtifactLedger finalization**: settle schemas for artifacts, summaries, provenance, and endorsement; define what is encrypt-at-rest vs prompt-visible vs audit-visible.
3. **Credential broker upgrade path**: define when tool-level credential resolution becomes insufficient (executor compromise, computer-use), and how proxy-level injection would integrate with PEP egress decisions.
4. **Policy semantics for background autonomy**: how scheduled tasks get “pre-approved scope” that is expressive enough to be useful but tight enough to prevent drift/exfil (ties directly to the scheduler→PEP gap).

## 7) Actionable checklist (gap analysis → next steps)

**Legend**
- `- [x]` = documented as present in the shisad bundle (keep it green with regression tests)
- `- [ ]` = gap / open design / missing wiring (action item)

### 7.1 Keep-green checklist (documented as “already true”)

- [x] PEP pipeline gates planner tool proposals (soundness + layering) (`shisad/docs/ANALYSIS-architecture-maturity.md`).
- [x] Sessions/capability model + checkpoints are robust enough to build on (`shisad/docs/ANALYSIS-architecture-maturity.md`).
- [x] Memory write-gating + provenance/taint-aware handling are treated as first-class (`shisad/docs/ANALYSIS-architecture-maturity.md`).
- [x] Provider routing/endpoint hardening is called out as sound (treat provider as egress) (`shisad/docs/ANALYSIS-architecture-maturity.md`, `shisad/docs/PLAN-security.md`).
- [x] Ops runbooks exist (incident response, rollback, key rotation, skill revocation) (`shisad/docs/runbooks/*`).

### 7.2 P0 — close enforcement bypasses (highest leverage + highest risk)

- [ ] Route **scheduled/triggered task execution** through the same PEP path as interactive tool calls (enforce `payload_taint`, `plan_commitment`, and `capability_snapshot`) (`shisad/docs/ANALYSIS-architecture-maturity.md`, `shisad/docs/PLAN-security.md` §4.4).
- [ ] Define and implement the **skill→ToolRegistry bridge**: installed skill manifests → tool definitions → planner-visible tool surface (no “shadow tools”, no bypass) (`shisad/docs/ANALYSIS-architecture-maturity.md`).
- [ ] Add a reusable **tool test template** that covers: schema validation, capability gating, resource authorization, egress policy, taint→sink rules, and “unsafe args” DLP (`shisad/docs/ANALYSIS-architecture-maturity.md`).

### 7.3 P0 — control-plane integrity closure (avoid a persistence substrate)

- [ ] Decide the target **control-plane isolation level** (in-process metadata boundary vs separate process/container), and write the explicit “non-claims” either way (`shisad/docs/v0.1/SECURITY-ANALYSIS.md`, `shisad/docs/PLAN-security.md`).
- [ ] Close the v0.4 **self-modification safety loop** end-to-end: propose → deterministic validate → capability diff/warn → operator apply → audit → rollback (`shisad/docs/v0.4/ANALYSIS-admin-self-modification.md`).
- [ ] Implement the v0.4 **artifact integrity contract** for self-modifiable control-plane artifacts (hash manifests + signatures + trust store + fail-closed behavior) (`shisad/docs/v0.4/ANALYSIS-signatures-and-integrity.md`).

### 7.4 P1 — multi-turn fidelity primitives (make “who asked?” robust over time)

- [ ] Finalize/implement the **ArtifactLedger** (or equivalent) as the primary “evidence store”: encrypted raw artifacts + firewall’d summaries + immutable provenance + mutable endorsement (`shisad/docs/ADR-command-task-architecture.md`).
- [ ] Implement the **TASK→COMMAND summary barrier** as a hard rule (firewall on summaries; provenance annotation; URLs in summaries treated as untrusted provenance) (`shisad/docs/ADR-command-task-architecture.md`, `shisad/docs/PLAN-context-scaffold.md`).
- [ ] Specify and enforce **scoped approval tokens** (TTL + narrow scope + revocation) to reduce confirmation fatigue without blanket privilege escalation (`shisad/docs/ADR-command-task-architecture.md`).

### 7.5 P1 — supply-chain hardening quick wins

- [ ] Integrate a multi-engine **skill scanner** (YARA + AST/dataflow + semantic analysis) into the skill vetting pipeline and CI gates (`shisad/docs/ANALYSIS-skill-scanner.md`).
- [ ] Document and enforce **remote tool discovery / MCP assumptions**: treat tool servers as untrusted, require explicit approval/vetting, and default-deny ambient filesystem/network (`shisad/docs/PLAN-security.md`).

### 7.6 P1 — evaluation + credibility

- [ ] Run the remaining **manual trace verification** (`SHISAD_TRACE_ENABLED=true`) and confirm redaction + permissions in real flows (`shisad/docs/IMPLEMENTATION-tracing.md`).
- [ ] Choose at least one **external benchmark harness** (ASR/utility) and add a “regression suite” that runs in CI (aligned to `ANALYSIS.md` Section 4).
- [ ] Add a small set of **end-to-end adversarial scenarios** that specifically target shisad’s stated invariants: (a) IPI → exfil attempt, (b) memory poisoning attempt, (c) scheduled-task drift, (d) skill supply-chain install attempt (`shisad/docs/ANALYSIS-security-casestudies.md`).

### 7.7 P2 — longer-term hardening decisions (defer unless threat model expands)

- [ ] Define the cutover point for upgrading from tool-level credential resolution to **proxy-level secret injection** (executor compromise, computer-use, arbitrary HTTP) (`shisad/docs/PLAN-security.md`).
- [ ] If multi-tenant or cross-channel consolidation becomes a goal, write the explicit isolation model (identity, workspace boundaries, memory zones) before shipping cross-channel context (`shisad/docs/PLAN-context-scaffold.md`).

## Appendix: Key shisad docs referenced

- Philosophy and core security model:
  - `shisad/docs/DESIGN-PHILOSOPHY.md`
  - `shisad/docs/PLAN-security.md`
- Multi-turn / orchestration:
  - `shisad/docs/PLAN-context-scaffold.md`
  - `shisad/docs/PLAN-multiturn-taint.md`
  - `shisad/docs/ADR-command-task-architecture.md`
- Governance / policy authority:
  - `shisad/docs/ADR-policy-source-authority.md`
- Case studies and maturity/gap audits:
  - `shisad/docs/ANALYSIS-security-casestudies.md`
  - `shisad/docs/ANALYSIS-architecture-maturity.md`
  - `shisad/docs/ANALYSIS-skill-scanner.md`
- Ops + observability:
  - `shisad/docs/runbooks/*`
  - `shisad/docs/PLAN-tracing.md`
  - `shisad/docs/IMPLEMENTATION-tracing.md`
- Self-modification and integrity (v0.4):
  - `shisad/docs/v0.4/ANALYSIS-admin-self-modification.md`
  - `shisad/docs/v0.4/ANALYSIS-signatures-and-integrity.md`
