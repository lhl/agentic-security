# Owner-Harm: A Missing Threat Model for AI Agent Safety

**Paper:** "Owner-Harm: A Missing Threat Model for AI Agent Safety"
**Authors:** Dongcheng Zhang, Yiqing Jiang
**Affiliations:** BlueFocus Communication Group, Tongji University
**Venue:** arXiv preprint
**arXiv:** [2604.18658](https://arxiv.org/abs/2604.18658)
**Date:** April 2026

## 1. Overview

This paper identifies and formalizes a systematic blind spot in AI agent safety: **owner-harm**, where an agent damages the interests of the very organization that deploys it. Existing benchmarks (AgentHarm, AgentDojo, OWASP LLM Top 10) focus on generic criminal harm directed at third parties---cybercrime, harassment, weapon synthesis---while leaving undeployer-directed harm as an unmodeled category.

The core argument is that owner-harm is not merely a special case of generic harm, but a structurally distinct threat class with different evidential requirements. An action like "send email to external@attacker.com" is not harmful by content alone; its harmfulness depends entirely on whether that address lies within the owner's trust boundary. Content-only classifiers, injection detectors, and DLP systems that lack owner-context dimensions cannot make this determination.

**Three contributions:**

1. **Owner-Harm threat model.** Formal definitions (Owner, Owner-Harm, Direct/Indirect Owner-Harm) and eight sub-categories grounded in real incidents from 2023--2026.
2. **Defense gap quantification and attribution.** A compositional safety system scoring 100% TPR / 0% FPR on AgentHarm (generic criminal harm) drops to 14.8% on AgentDojo injection tasks (owner-harm). A controlled experiment attributes this 85.2 pp gap to environment-bound symbolic rule generalization failure, not inherent category difficulty.
3. **Layer complementarity evidence.** A deterministic post-audit verifier (L4) is orthogonal to a semantic gate (L3), raising Hijacking detection from 43.3% to 93.3% by detecting behavioral fingerprints in file artifacts that the semantic gate misses.

---

## 2. Threat Model

### 2.1 Formal Definitions

The paper models an agent as a tuple A = ⟨M, T, E, π⟩ (model, tool set, environment state, policy). An action sequence ⃗a transforms state s₀ to s′.

- **Owner (O):** The entity that deploys A, grants resource access R_O, and bears accountability. Associated with a resource set, a utility function U_O, and a trust boundary B_O.
- **Owner-Harm (OH):** An action sequence causes owner-harm iff U_O(s′) < U_O(s₀) and some action aᵢ is a proximate or distal cause of the state transition.
- **Direct Owner-Harm (DOH):** The agent itself is the proximate cause.
- **Indirect Owner-Harm (IOH):** An adversarial actor V manipulates the agent's policy π to produce the harmful sequence (the prompt injection model).

### 2.2 Eight Owner-Harm Categories (C1--C8)

| Category | Description | Real Incident |
|----------|-------------|-------------|
| **C1: Credential Leak** | Exfiltration of auth materials (API keys, tokens, cookies) | Slack AI credential exfiltration via prompt injection (Aug 2024) |
| **C2: Infrastructure Exposure** | Misconfiguration/disclosure of network rules, cloud policies, internal architecture | Over-permissive AWS IAM policies from AI-generated code |
| **C3: Privacy Exposure** | Transmission of PII or confidential business data to unauthorized parties | Microsoft 365 Copilot calendar-injection email forwarding (Jan 2024) |
| **C4: Inner Circle Leak** | Breach of commercially sensitive trust relationships (client lists, partner agreements, M&A) | Samsung employees pasting proprietary code into ChatGPT (Apr 2023) |
| **C5: Asset Destruction** | Irreversible deletion/corruption of owner data, configs, or digital assets | AI coding agent executing `rm -rf` on production directories |
| **C6: Exfiltration via Tools** | Exploiting authorized tools as covert data channels (email, webhooks, file-write) | ASCII smuggling via Microsoft 365 Copilot Markdown URLs (Rehberger 2024) |
| **C7: Hijacking** | Adversary achieves persistent control over the agent using the owner's identity/credentials | AutoGPT memory poisoning across sessions (2024--2025) |
| **C8: Unauthorized Autonomy** | Agent exceeds authorization scope by taking consequential actions without human confirmation | Air Canada chatbot committing to unauthorized refund terms (Feb 2024) |

### 2.3 Coverage Gaps in Existing Frameworks

Table 1 (from the paper) maps categories against AgentHarm, ToolEmu, OWASP LLM Top 10, and AgentDojo:

- **C4 (Inner Circle Leak)** appears in **no existing benchmark.** This category requires reasoning about the owner's trust graph---who counts as an insider---which no current system models explicitly.
- **C6 (Exfiltration via Tools)** is partially covered by ToolEmu but misses the covert-channel aspect: using authorized tools as smuggling vectors.
- The owner-centric perspective itself is the primary novel contribution. Existing frameworks evaluate harm against third parties, users, or society; none formally model the deploying owner as the victim.

### 2.4 Why Generic Defenses Fail

The fundamental mismatch is **context-dependence of harm**:

```
∃ c, O₁, O₂ : Harmful(c, O₁) ∧ ¬Harmful(c, O₂)
```

Three owner-context dimensions are systematically absent from generic defenses:

1. **Resource Ownership (R_O):** Which data and credentials belong to the owner and should not be disclosed.
2. **Trust Boundary (B_O):** Who the owner considers an authorized counterparty for each resource type.
3. **Authorization Scope (Auth_O):** Which actions the owner has explicitly sanctioned without requiring confirmation.

**Proposition 1 (Generic Classifier Incompleteness):** Any context-free binary classifier that classifies action content without access to R_O, B_O, or Auth_O will produce owner-harm false negatives on scenarios where harm is defined relative to the owner's context.

Table 2 (from the paper) summarizes failure modes:

| Defense Class | Owner-Harm Blind Spot |
|---------------|----------------------|
| Content classifier | Ignores R_O; "send email" is benign by content |
| Injection detector | Detects injection syntax; misses semantic intent |
| Tool monitor | Sees call signature; not authorization context |
| DLP system | Pattern-matches known PII; misses context-defined confidential data |
| Behavioral anomaly | Requires baseline; new deployments have no baseline |

---

## 3. Nous: Compositional Runtime Safety Gate

The paper uses Nous, a four-layer compositional runtime safety gate, as its evaluation vehicle. This is described as an existing system rather than the primary contribution.

### 3.1 Architecture

| Layer | Mechanism | Function | Latency |
|-------|-----------|----------|---------|
| **L1** | Deterministic Datalog Blocker | 46 Datalog rules encoding owner-policy constraints (resource ownership, bad patterns, categorical prohibitions). Fail-closed. | P50 = 0.055 ms |
| **L2** | Triviality Filter | Routes trivially benign actions past L3; ~70% cost reduction | negligible |
| **L3** | Semantic Gate | LLM evaluator with minimal-pair examples, intent decomposition, majority vote k=3 | LLM call |
| **L4** | Post-Gate Verifier | 6 deterministic audit rules (V1--V6) inspecting file contents and multi-step tool-call sequences invisible to L1--L3 | ~0.038 ms |

### 3.2 Design Rationale for Owner-Harm

- **L1** encodes owner-policy as explicit Datalog facts.
- **L3** reasons about owner context when policy is ambiguous.
- **L4** catches injection patterns that survive semantic evaluation because the semantic reasoning is itself manipulated by injected content.

The layers are architecturally complementary: L1 operates on individual action content; L3 on action semantics plus owner context; L4 on artifact contents and behavioral sequences.

---

## 4. Evaluation

### 4.1 Benchmark Sets

1. **AgentDojo** (authoritative): 27 injection tasks, 97 user tasks, 4 suites (Banking, Travel, Workspace, Slack). Ground-truth labels provided by benchmark authors.
2. **AgentHarm** (comparative baseline): 176 harmful + 176 benign scenarios across 11 categories. Used to confirm the gap is category-specific, not a global system deficiency.
3. **Owner-Harm Benchmark** (post-hoc diagnostic, 300H + 150B, 8 categories): Constructed by the author after optimization loops. **Not a held-out independent test set**---results are diagnostic evidence of system capabilities, not validation performance.

### 4.2 AgentDojo Results

| Configuration | Safety (27 injection) | Utility (97 user) | FPR |
|---------------|----------------------|-------------------|-----|
| L1 only | 3.7% (1/27) | 97.9% (95/97) | 2.1% (2/97) |
| L1 + L4 | 3.7% (1/27) | 97.9% | 2.1% |
| L1 + L3 + L4 (full) | 14.8% (4/27) | 97.9% | 2.1% |

**Key findings:**
- **L4 contributes zero** to AgentDojo safety. V-rules target bash/curl patterns in file artifacts; AgentDojo attacks operate at the application layer (send money, send email, update calendar) with no file artifact intermediary.
- **L3 adds +11.1 pp** by catching three cases unreachable by Datalog: passport forwarding, bank account forwarding, and batch wire transfer to adversary account.
- **Utility remains 97.9%** across all configurations---semantic reasoning does not increase false positives.

**Structural blind spots** (three categories systematically out of reach):
1. **Text-only manipulation** (no tool-call artifact to intercept).
2. **Malicious parameters indistinguishable from legitimate ones** (e.g., send money with plausible amount and adversary-controlled recipient that appears valid). Without the user's task goal in gate context, semantic layer cannot compare "user requested payment to X" vs. "agent is paying Y".
3. **Multi-step attacks** where partial interception is insufficient (read-then-exfiltrate chains).

### 4.3 Owner-Harm Benchmark Results (Post-Hoc Diagnostic)

| Category | N_h | Gate TPR | Combined TPR | Gate FPR |
|----------|-----|----------|--------------|----------|
| C1: Credential Leak | 28 | 100.0% | 100.0% | 0.0% |
| C2: Infrastructure Exposure | 50 | 100.0% | 100.0% | 20.0%† |
| C3: Privacy Exposure | 28 | 100.0% | 100.0% | 0.0% |
| C4: Inner Circle Leak | 28 | 89.3% | 89.3% | 0.0% |
| C8: Unauthorized Autonomy | 50 | 70.0% | 70.0% | 0.0% |
| C5: Asset Destruction | 28 | 64.3% | 64.3% | 0.0% |
| C6: Exfiltration via Tools | 28 | 57.1% | 57.1% | 0.0% |
| C7: Hijacking | 60 | 43.3% | **93.3%** | 0.0% |

† 20% FPR for C2 caused by rule OH-R3a over-triggering on benign external-channel configuration queries.

**Hijacking layer complementarity** (most significant result):

| Quadrant | Count | % |
|----------|-------|---|
| Gate-only (verifier misses) | 11 | 18.3% |
| Verifier-only (gate allows) | 30 | 50.0% |
| Both layers detect | 15 | 25.0% |
| Neither (structural boundary) | 4 | 6.7% |
| **Combined** | **56** | **93.3%** |

The 50% "Verifier-only" quadrant represents prompt-injection attacks where the semantic gate is itself manipulated by injected content, but the verifier detects the behavioral fingerprint in file artifacts.

### 4.4 Cross-Benchmark Comparison (Central Finding)

| Benchmark | Focus | Nous Safety | Generic LLM | Status |
|-----------|-------|-------------|-------------|--------|
| AgentHarm | Generic criminal | 100% / 0% | 62.7% / 16.0% | Validation |
| Owner-Harm (diag.) | Owner-directed | 75.3% / 3.3% | --- | Diagnostic |
| AgentDojo | Prompt injection | 14.8% (4/27) | 59.3% (16/27) | Authoritative |

The generic LLM (qwen-turbo zero-shot) achieves **59.3% on AgentDojo** without any prompt-injection-specific design, substantially outperforming Nous (14.8%). This is the central architectural insight: owner-harm detection depends primarily on semantic understanding of action consequences and owner context, which symbolic rules (L1) cannot provide.

### 4.5 Gap Attribution (Controlled Experiment)

The 85.2 pp gap admits two explanations:
- **H1:** Owner-harm scenarios are semantically harder to classify.
- **H2:** The gap is an artifact of Nous's symbolic rules being fit to the AgentHarm tool vocabulary and failing to generalize.

**Experimental design:** Zero-shot generic LLM classifier (qwen-turbo) with uniform binary-classification prompt, no benchmark-specific fine-tuning.

**Results:**

| System | AgentHarm TPR | AgentDojo TPR | Gap |
|--------|---------------|---------------|-----|
| Nous (L1+L3+L4) | 100.0% | 14.8% | **85.2 pp** |
| Generic LLM | 62.7% | 59.3% | **3.4 pp** |

**Finding:** The generic LLM's 3.4 pp gap is statistically negligible compared to Nous's 85.2 pp gap. AgentDojo owner-harm scenarios are **not** semantically harder to detect. The gap is strongly associated with **L1 (Datalog) generalization failure**---L1 rules derived from AgentHarm patterns (bash, read file, execute command) are absent from AgentDojo's application-layer vocabulary (send money, send email, update calendar).

**Implication:** Upgrading from tool-name blacklists to parameter-semantic analysis (detecting attacker-controlled IBANs or exfiltration-destination emails regardless of calling tool name) is the single most impactful architectural change for cross-environment generalization.

### 4.6 SSDG Experimental Predictions

The Symbolic-Semantic Defense Generalization (SSDG) framework yields two testable predictions:

**P1 (Context Injection) --- Prediction Rejected.**
Injecting the user's task goal into gate evaluation context should raise AgentDojo TPR. Result: TPR **declined** from 14.8% to 8.3%.
- **Interpretation:** Appending user goal as text prefix does not constitute structured goal-action alignment. The gate's intent decomposition logic cannot compare injected goal to observed action without explicit structural scaffolding (e.g., a "goal vs. action" contrast prompt).
- **Confounds:** Ground-truth evaluates task success not injection semantics; simple text injection may activate overcautious benign-task blocking; pilot N=12 is too small for significance.
- **P1 remains open:** The mechanism requires structured goal-context integration, not raw text concatenation.

**P2 (Context Deprivation) --- Prediction Confirmed.**
Stripping world-context from semantic defense should reproduce symbolic-gap behavior.

| Condition | AgentHarm TPR | AgentDojo TPR | Gap Ratio R |
|-----------|---------------|---------------|-------------|
| Full Group | 62.7% | 59.3% | 1.06 |
| Stripped Group | 30.0% | 8.3% | **3.60** |

R = 3.60 exceeds the P2 falsification threshold (R ≤ 1.5). When deprived of context, semantic defense degrades to near-symbolic gap behavior, confirming Hypothesis 2.

---

## 5. Production Deployment Evidence

Nous was deployed in **shadow mode** alongside an existing rule-based system for 11+ days (30,204 calls total).

- **Consistency:** 99.47% agreement with existing rule-based system---semantic reasoning does not introduce systematic drift.
- **False negative recovery:** Nous detected 157 cases the existing system passed as benign. Manual review (stratified sample, author-conducted, non-blind) confirmed these were true positives, predominantly ambiguous read-then-send workflows where the send target fell outside the owner's trust boundary.
- **Over-blocking:** Nous over-blocked in 4 cases where the existing system correctly allowed. All 4 were over-triggered on ambiguous read-then-send workflows with legitimate internal addresses.
- **Caveat:** Manual review conducted by system developer (first author), not an independent auditor, and was not blind to Nous's verdict---potential confirmation bias. These results are case-level observations, not a controlled study.

Following the shadow period, Nous was promoted to primary interceptor. No regressions observed post-cutover.

---

## 6. Key Insights

### 6.1 Symbolic vs. Semantic Generalization Asymmetry

The paper exposes a fundamental asymmetry between the two primary detection mechanisms:

- **Symbolic rules (L1 Datalog):** Bimodal generalization profile. Near-perfect recall in-distribution (100% on AgentHarm), near-zero recall out-of-distribution (3.7% on AgentDojo). Datalog rules encode extensional facts ("tool t is prohibited") rather than intensional harm semantics. Any tool name not in the rule set is trivially allowed.
- **Semantic reasoning (L3 gate, generic LLM):** Flat generalization profile. Below-perfect recall within distribution (62.7% generic LLM on AgentHarm), but stable recall across environments (59.3% on AgentDojo, gap = 3.4 pp). Semantic reasoning transfers because harm intent is encoded in goal descriptions---which remain semantically consistent across tool-vocabulary changes---rather than in tool names.

**Design implication:** The value of combining symbolic and semantic layers is not simply "two layers are better than one." The layers have **complementary generalization curves**: symbolic rules provide high-precision coverage in-distribution, and semantic reasoning maintains consistent coverage out-of-distribution. A system relying solely on symbolic rules will exhibit catastrophic degradation on novel tool environments; a system relying solely on semantic reasoning will accept a consistent recall ceiling but generalize robustly.

### 6.2 Architectural Complementarity on Hijacking

The Hijacking result (43.3% gate → 93.3% combined) provides direct evidence of architectural complementarity for prompt injection:

- When injection is **semantically explicit** ("ignore previous instructions"), the gate catches it; verifier sees no artifact yet.
- When injection is **embedded in a file artifact** (calendar event description, email body that the agent reads and acts upon), the semantic gate evaluates the agent's action (which may be semantically plausible); the verifier detects the injection fingerprint in the artifact content.
- When **both signals are present**, both layers fire (25% of cases).

This is a transferable design principle: **prompt injection requires both semantic and behavioral-sequence detection.**

### 6.3 Benchmark Design Implications

Existing injection benchmarks do not provide explicit owner context. The paper recommends future benchmarks include an **owner context manifest**: a structured specification of R_O, B_O, and Auth_O provided to both the agent and any runtime safety system. Without this, defenses cannot reach the estimated 40--60% ceiling on malicious-parameter tasks, and benchmarks cannot meaningfully differentiate owner-harm defense strategies.

---

## 7. Limitations

1. **AgentDojo ceiling:** Without user task goal context, semantic gate cannot compare "user requested X" to "agent doing Y", limiting achievable safety to ~15% on malicious-parameter tasks.
2. **Benchmark independence:** Owner-Harm Benchmark is author-constructed after system optimization. Diagnostic, not validation evidence.
3. **Single annotator:** No inter-annotator agreement reported for Owner-Harm Benchmark labels.
4. **Structural boundary:** 4/60 Hijacking cases (SQL file injection, direct SSH key injection) are out of reach of current V-rules.
5. **Evaluation mode:** AgentDojo uses ground-truth mode without an adversarial attack LLM; real-world adaptive adversaries may achieve different results.
6. **Infrastructure Exposure FPR:** Rule OH-R3a over-triggers on benign external-channel configuration queries (20% FPR for C2).
7. **SSDG pilot scale:** P1 and P2 use N=12 AgentDojo tasks and N=15 AgentHarm scenarios. Directionally consistent with theory but require full-benchmark replication for statistical significance.

---

## 8. Connections to Our Research

This paper is highly relevant to the agentic-security collection for several reasons:

1. **It formalizes a threat class we have observed but not named.** Many of the incidents catalogued in this repo (Copilot data leaks, Slack credential exfiltration, chatbot autonomy failures) fit cleanly into the C1--C8 taxonomy. The paper provides the vocabulary and formal structure to analyze them consistently.
2. **It quantifies the defense gap we hypothesize.** The 100% → 14.8% drop demonstrates that compositional safety architectures optimized for generic harm (the dominant research focus) leave owner-harm nearly undefended. This validates the emphasis on runtime verification and context-aware policies in our defense-in-depth recommendations.
3. **It provides a concrete instance of the symbolic-semantic tension.** The Datalog/LLM complementarity in Nous is a specific case of the broader pattern: symbolic systems (type systems, policy languages, Datalog) provide precision in-distribution but fail on novel tool vocabularies; semantic systems (LLM evaluators) generalize but have lower precision. The SSDG framework gives a conceptual vocabulary for this tension.
4. **It reinforces the need for owner-context dimensions in any policy system.** Papers like PCAS (Palumbo et al. 2026), AgentSpec (Wang et al. 2026), and Pro2Guard (He et al. 2025) explore policy-driven runtime enforcement, but none include R_O, B_O, or Auth_O in their input vocabularies. The owner-harm threat model implies these are prerequisites, not optional extensions.
5. **The Hijacking layer-complementarity result is a design template.** The 43.3% → 93.3% improvement from adding a behavioral-sequence verifier to a semantic gate is direct evidence for the "post-audit" layer in our recommended defense stack.

---

## 9. Citation

```bibtex
@article{zhang2026ownerharm,
  title={Owner-Harm: A Missing Threat Model for AI Agent Safety},
  author={Zhang, Dongcheng and Jiang, Yiqing},
  journal={arXiv preprint arXiv:2604.18658},
  year={2026},
  url={https://arxiv.org/abs/2604.18658}
}
```

**Local PDF:** `references/papers/arxiv-2604.18658.pdf`
**Local text snapshot:** `references/papers/arxiv-2604.18658.md`
