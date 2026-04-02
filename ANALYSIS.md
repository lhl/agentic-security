# Securing AI Agents: A Comprehensive Analysis

**80 papers and reports | 2022--2026 | Defense-in-depth for LLM-based agent systems**

*Compiled March 2026*

---

## Executive Summary

LLM-based agents---systems that combine language models with tool access, memory, and multi-step reasoning---are the fastest-growing deployment pattern in production AI. They are also the most vulnerable. The core problem is **prompt injection**: when an agent processes untrusted data (emails, web pages, API responses), an adversary can embed instructions that hijack the agent's behavior, exfiltrate data, or escalate privileges.

Three findings define the current state of the field:

1. **Probabilistic defenses fail under adaptive attack.** A joint OpenAI/Anthropic/DeepMind red-team effort ("The Attacker Moves Second," Oct 2025) bypassed 12 recent model-level and detection-based defenses; adaptive attacks reached >90% attack success rate in most cases. This is the single most important empirical result in the field. \[arXiv:2510.09023\]

2. **Architectural defenses work but aren't deployed.** CaMeL (Google DeepMind, arXiv Mar 2025) is not vulnerable to AgentDojo's prompt injection attacks by separating control flow from untrusted data through capability-based security. As of Feb 2026, production adoption remains limited. \[arXiv:2503.18813\]

3. **Defense-in-depth is the only viable strategy.** No single layer is sufficient. The research consensus points to layered defenses: architectural isolation at the core, access control and privilege separation as enforcement, runtime verification as monitoring, and detection/filtering as outer perimeter.

**Key terms (used throughout):**

- **IPI (Indirect Prompt Injection):** Attacker instructions embedded in untrusted data an agent reads (webpages, emails, tool outputs).
- **ASR (Attack Success Rate):** Fraction of attacks that achieve the attacker's objective, as defined by each paper/benchmark.
- **Utility:** Task success rate (often reported both benign and under attack).
- **IFC (Information Flow Control):** Track/restrict how labeled data (trusted/untrusted, public/private) can influence decisions and tool calls.
- **MCP (Model Context Protocol):** A protocol for connecting agents to tool servers.
- **RAG (Retrieval-Augmented Generation):** Retrieve external context (often from a vector store) and feed it into the model.
- **MAC/ABAC:** Mandatory / attribute-based access control policy models.
- **PDG:** Program dependence graph (data/control dependencies), used for trace-based analyses.

**For practitioners:** Start with Section 5 (Production Readiness) and Section 6 (Recommended Defense Stack). For researchers: the full taxonomy begins at Section 3.

---

## Table of Contents

1. [Executive Summary](#executive-summary)
2. [Threat Landscape](#2-threat-landscape)
3. [Defense Taxonomy](#3-defense-taxonomy)
   - 3.1 [Secure Architectures by Construction](#31-secure-architectures-by-construction)
   - 3.2 [Access Control and Governance](#32-access-control-and-governance)
   - 3.3 [Runtime Verification and Policy Enforcement](#33-runtime-verification-and-policy-enforcement)
   - 3.4 [Detection, Filtering, and Firewalls](#34-detection-filtering-and-firewalls)
   - 3.5 [Model-Level Hardening](#35-model-level-hardening)
   - 3.6 [Boundary Marking and Cryptographic Provenance](#36-boundary-marking-and-cryptographic-provenance)
   - 3.7 [Formal Methods and Semantics](#37-formal-methods-and-semantics)
4. [Benchmarks and Evaluation](#4-benchmarks-and-evaluation)
5. [Production Readiness](#5-production-readiness)
6. [Recommended Defense Stack](#6-recommended-defense-stack)
7. [Open Problems and Research Gaps](#7-open-problems-and-research-gaps)
8. [Complete Reference Index](#8-complete-reference-index)

---

## 2. Threat Landscape

### The Core Problem

LLM agents face a fundamental architectural vulnerability: **they cannot distinguish instructions from data**. When an agent reads an email, fetches a web page, or processes an API response, any text in that content can be interpreted as an instruction. This is **indirect prompt injection** (IPI)---the attacker targets the user, not the model directly.

### Key Attack Vectors

- **Indirect prompt injection (IPI):** Malicious instructions embedded in data the agent processes. The most critical and widely studied threat. The user is the victim. \[arXiv:2302.12173, arXiv:2306.05499\]
- **Memory poisoning:** Persistent compromise via poisoned entries in long-term memory or RAG stores. Attacks persist across sessions. \[arXiv:2407.12784, arXiv:2503.03704, arXiv:2512.16962\]
- **Tool/function supply-chain attacks:** Poisoned tool libraries or MCP servers that hijack agent behavior at the integration layer. \[arXiv:2509.24408\]
- **Privilege escalation and confused deputy:** Agents perform actions exceeding least privilege; in multi-agent systems, one agent tricks another into unauthorized operations. \[arXiv:2601.11893, arXiv:2503.15547\]
- **Data exfiltration:** Hijacked tool calls (or malicious tools) can route sensitive data to attacker-controlled endpoints; side channels can leak information even when direct exfil is blocked. \[arXiv:2302.12173, arXiv:2306.05499, arXiv:2509.10540\]
- **Visual/rendered prompt injection:** Attacks embedded in rendered UI elements targeting computer-use agents. \[arXiv:2506.02456, arXiv:2505.21936\]
- **Browser-specific attacks:** Prompt injection tailored to web-browsing agents. \[arXiv:2511.20597\]

### The Validation That Changed the Field

**"The Attacker Moves Second"** (Nasr et al., Oct 2025) is a joint red-team effort by researchers from OpenAI, Anthropic, and Google DeepMind. They applied adaptive attacks---iteratively refined based on defense behavior---against 12 published defenses across prompt injection and jailbreak domains. Across most defenses, adaptive attacks reached >90% attack success rate; none of the 12 defenses was robust. This paper is the empirical foundation for the architectural defense paradigm: if adaptive adversaries can bypass model-level robustness, security must be enforced outside the model. \[arXiv:2510.09023\]

Concurrent work reinforces this: **AgentDyn** (Feb 2026) shows many defenses that appear effective on static benchmarks are overfit and fail on open-ended, dynamic tasks. \[arXiv:2602.03117\]

### Empirical Validation in Deployed Agents

**"Agents of Chaos"** (Shapira et al., Feb 2026) is the first controlled red-team study of autonomous LLM agents deployed with persistent memory, email, shell access, file systems, and Discord in a live environment. Six agents (Kimi K2.5 and Claude Opus 4.6) operated for two weeks while 20 researchers probed for vulnerabilities. The study documents 10 security failures and 6 emergent safety behaviors across 16 case studies.

Key vulnerability findings: (1) **non-owner compliance**---agents followed unauthorized data requests, exposing 124+ email records without owner approval; (2) **disproportionate response**---an agent destroyed an entire mail server as a "protective" measure; (3) **semantic reframing bypasses**---an agent refused to "share" PII but complied when asked to "forward" it; (4) **identity hijacking**---agents accepted spoofed owner identity and executed full system compromise; (5) **cross-agent propagation**---a malicious "holiday" instruction injected via GitHub Gist caused one agent to attempt shutdowns and compromise other agents; (6) **infinite loops and resource exhaustion**---mutual agent relay loops and storage DoS with no recovery mechanisms.

The study identifies the **social coherence problem**: agents lack stable models of social hierarchy and treat authority as conversationally constructed, making them vulnerable to whoever demonstrates sufficient confidence or persistence. Multi-agent deployments amplify this---"failures that require a single social engineering step may propagate automatically to connected agents." Notably, agents also demonstrated positive safety behaviors: rejecting 14+ prompt injection variants, refusing email spoofing, and spontaneously coordinating shared safety policies without instruction. \[arXiv:2602.20021\]

### Systematic Taxonomy of Environmental Attacks

**"AI Agent Traps"** (Franklin et al., Google DeepMind, 2026) introduces the first systematic framework for classifying adversarial content embedded in the information environment---web pages, emails, APIs, and databases---engineered to exploit visiting AI agents. Unlike prior work that focuses on specific attack types, this paper taxonomizes environmental attacks by the agent functional component they target, identifying six categories with 22 subcategories:

1. **Content Injection Traps** (perception): Exploit the gap between human-visible rendering and machine-parsed data. Subcategories: *web-standard obfuscation* (CSS/HTML hidden text), *dynamic cloaking* (fingerprinting agent visitors to serve tailored payloads), *steganographic payloads* (adversarial instructions in image pixel arrays), *syntactic masking* (exploiting Markdown/LaTeX parsing to hide payloads).

2. **Semantic Manipulation Traps** (reasoning): Corrupt the agent's reasoning without overt commands. Subcategories: *biased phrasing, framing & contextual priming* (skewing output via sentiment-laden or authoritative language), *oversight & critic evasion* (wrapping malicious instructions in educational/hypothetical framing to bypass safety filters), *persona hyperstition* (seeding circulating narratives about a model's identity that feed back via retrieval, stabilizing attacker-chosen behavior).

3. **Cognitive State Traps** (memory & learning): Target long-term memory, knowledge bases, and learned policies. Subcategories: *RAG knowledge poisoning* (fabricated documents in retrieval corpora), *latent memory poisoning* (innocuous data that activates as malicious in specific future contexts), *contextual learning traps* (corrupted few-shot demonstrations or reward signals that steer in-context learning).

4. **Behavioural Control Traps** (action): Hijack the agent's instruction-following capabilities. Subcategories: *embedded jailbreak sequences* (dormant adversarial prompts in external resources), *data exfiltration traps* (confused deputy attacks inducing the agent to leak privileged data), *sub-agent spawning traps* (coercing orchestrators to instantiate attacker-controlled sub-agents within the trusted control flow).

5. **Systemic Traps** (multi-agent dynamics): Trigger macro-level failures through correlated agent behavior. Subcategories: *congestion traps* (synchronizing agents into exhaustive resource competition), *interdependence cascades* (self-reinforcing failure spirals analogous to financial flash crashes), *tacit collusion* (environmental signals as correlation devices for anti-competitive behavior without direct communication), *compositional fragment traps* (partitioning a payload across multiple data sources that reconstitutes upon multi-agent aggregation), *Sybil attacks* (fabricated agent identities to manipulate collective decision-making).

6. **Human-in-the-Loop Traps** (human overseer): Commandeer the agent to attack the human user. Includes approval fatigue (generating benign-looking outputs that overwhelm human reviewers), social engineering via agent (inducing users to click malicious links), and exploiting automation bias.

The key insight is that the attack surface is **combinatorial**: traps from different categories can be chained, stacked, or spread across multi-agent systems. Content injection may deliver a behavioural control payload, while systemic traps exploit the interaction dynamics to amplify single-agent compromises into ecosystem-wide failures. The Systemic Traps and Human-in-the-Loop Traps categories are largely novel---they represent a theoretical but increasingly plausible attack surface as agent economies scale. The paper's mitigation discussion identifies three strategic challenges: detection at web scale, attribution (tracing a compromised output to the specific trap), and the continuous adaptation arms race. \[SSRN:6372438\]

### Threat Landscape References

| Paper | Year | Key Contribution |
|:------|:-----|:-----------------|
| Greshake et al., "Not What You've Signed Up For" \[arXiv:2302.12173\] | 2023 | Foundational paper on indirect prompt injection taxonomy |
| Perez & Ribeiro, "Ignore Previous Prompt" \[arXiv:2211.09527\] | 2022 | First systematic prompt injection attack taxonomy |
| Liu et al., HouYi \[arXiv:2306.05499\] | 2025 | Empirical prompt injection on commercial apps; black-box attack framework |
| Pasquini et al., Neural Exec \[arXiv:2403.03792\] | 2024 | Learned execution triggers that sidestep handcrafted-string detectors |
| Chen et al., AgentPoison \[arXiv:2407.12784\] | 2024 | Foundational attack on agent memory/RAG stores |
| Yang et al., MINJA \[arXiv:2503.03704\] | 2026 | Practical query-only persistent memory injection |
| Wang et al., MemoryGraft \[arXiv:2512.16962\] | 2025 | Persistent compromise via poisoned successful experiences |
| Guo et al., FuncPoison \[arXiv:2509.24408\] | 2025 | Tool/function library as attack surface in multi-agent systems |
| Liu et al., Visual PI for CUAs \[arXiv:2506.02456\] | 2026 | Prompt injection in rendered UI/pixel layer |
| Peng et al., RedTeamCUA \[arXiv:2505.21936\] | 2026 | Realistic adversarial testing in hybrid web-OS environments |
| Lee et al., BrowseSafe \[arXiv:2511.20597\] | 2025 | Browser-agent-specific prompt injection threats and defenses |
| Yi et al., EchoLeak \[arXiv:2509.10540\] | 2025 | First real-world zero-click prompt injection exploit in production |
| Nasr et al., "The Attacker Moves Second" \[arXiv:2510.09023\] | 2025 | Meta-evaluation: adaptive attacks bypass 12 defenses; >90% ASR in most cases |
| He et al., AgentDyn \[arXiv:2602.03117\] | 2026 | Dynamic benchmark showing static-benchmark overfitting |
| Shapira et al., "Agents of Chaos" \[arXiv:2602.20021\] | 2026 | Red-team study: 10 vulnerabilities in deployed autonomous agents over 2 weeks |
| Franklin et al., "AI Agent Traps" \[SSRN:6372438\] | 2026 | First systematic taxonomy of environmental attacks on agents; 6 categories, 22 subcategories |

---

## 3. Defense Taxonomy

The field has converged on seven defense categories. No single category is sufficient---they compose into a defense-in-depth stack (see Section 6).

| Category | Approach | Guarantee | Maturity |
|:---------|:---------|:----------|:---------|
| Secure Architectures | Control/data separation, capability systems | Deterministic (within threat model) | Research prototypes |
| Access Control & Governance | MAC/ABAC, policy DSLs, MCP permissions | Deterministic (policy-dependent) | Early frameworks |
| Runtime Verification | Guardrail agents, verify-before-commit, trace analysis | Mixed (depends on analyzer) | Research + some OSS |
| Detection & Firewalls | Classifiers, sanitizers, token-level filtering | Probabilistic | Most deployed today |
| Model-Level Hardening | Instruction hierarchy, preference optimization, representation editing | Probabilistic (improves with scale) | Deployed in some foundation models |
| Boundary Marking | Cryptographic signing, prompt fencing, encrypted permissions | Depends on model compliance | Conceptual / early research |
| Formal Methods | Information flow control, lambda calculus semantics | Provable (simplified models) | Theoretical |

---

### 3.1 Secure Architectures by Construction

**The key insight:** Treat the LLM as an untrusted component---like user input in web security---and enforce security at the system level. This is the SQL parameterized query equivalent for LLM agents.

**Why it matters:** This category offers the strongest security guarantees. Rather than trying to make models robust to injection (which "The Attacker Moves Second" showed fails), these approaches make injection structurally impossible for the protected threat model.

**Synthesis:**

- **CaMeL** is the landmark paper. A Privileged LLM (P-LLM) generates plans as restricted Python; a Quarantined LLM (Q-LLM) processes untrusted data with no tool access. A custom interpreter tracks data provenance through capability tokens. Result: 0 successful prompt injection attacks on AgentDojo's attack suite; solves 77% of AgentDojo tasks with provable security (vs. 84% undefended). Cost: ~2.8x token overhead. \[arXiv:2503.18813\]
- **IsolateGPT/SecGPT** pioneered hub-and-spoke execution isolation, but **ACE** (NDSS 2026) later demonstrated three bypass attacks against it, showing isolation alone is insufficient without planning integrity guarantees. \[arXiv:2403.04960, arXiv:2504.20984\]
- **Type-directed privilege separation** extends the Dual LLM pattern by allowing data flow between P-LLM and Q-LLM only for non-instruction-bearing types (integers, booleans, enums). This recovers functionality the original pattern sacrificed. \[arXiv:2509.25926\]
- **AirGapAgent** applies contextual integrity and data minimization---the agent only accesses task-necessary data. Strong privacy architecture. \[arXiv:2405.05175\]
- **Design Patterns for Securing LLM Agents** is the field's first systematic pattern catalog---the GoF patterns equivalent for agent security. Best entry point for system designers. \[arXiv:2506.08837\]
- **Operationalizing CaMeL** identifies enterprise deployment gaps (trusted user prompts assumption, side channels, performance) and proposes practical mitigations including plan-template caching and policy-as-code. \[arXiv:2505.22852\]

| Paper | Year | Venue | Code | Key Contribution |
|:------|:-----|:------|:-----|:-----------------|
| CaMeL \[arXiv:2503.18813\] | 2025 | Preprint | [github](https://github.com/google-research/camel-prompt-injection) | IFC + capabilities; eliminates AgentDojo prompt injection attacks; 77% tasks solved w/ provable security |
| IsolateGPT/SecGPT \[arXiv:2403.04960\] | 2025 | NDSS 2025 | [github](https://github.com/llm-platform-security/SecGPT) | Hub-and-spoke execution isolation; LlamaIndex pack |
| ACE \[arXiv:2504.20984\] | 2025 | NDSS 2026 | -- | Breaks IsolateGPT; trusted-planning fix |
| Type-Directed Separation \[arXiv:2509.25926\] | 2025 | Preprint | -- | Type system as security boundary for Dual LLM |
| AirGapAgent \[arXiv:2405.05175\] | 2024 | Preprint | -- | Privacy-by-design; contextual integrity |
| Design Patterns \[arXiv:2506.08837\] | 2025 | Preprint | -- | First systematic security pattern catalog for agents |
| Operationalizing CaMeL \[arXiv:2505.22852\] | 2025 | Preprint | -- | Enterprise deployment gaps and mitigations |
| ASIDE \[arXiv:2503.10566\] | 2026 | Preprint | -- | Architectural instruction/data separation at embedding level |

---

### 3.2 Access Control and Governance

**The key insight:** Even if an attacker compromises the agent's reasoning, access control limits what actions can be taken. Put authorization in a control plane, not in prompts.

**Why it matters:** Over-privileged tool access is the root cause enabling most attacks. These frameworks enforce least-privilege on tool invocations, inter-agent communication, and MCP server access.

**Synthesis:**

- **Progent** is the most practical: a proxy-based privilege control layer with a DSL for fine-grained tool policies, fallback actions, and dynamic updates. 0% ASR with preserved utility. LLM-generated policies are viable but re-introduce probabilistic risk. \[arXiv:2504.11703\]
- **SEAgent** formally identifies the **confused deputy problem** in multi-agent systems and applies MAC/ABAC with information flow graphs. \[arXiv:2601.11893\]
- **AgentBound** is the first access control framework for **MCP servers**, adapting the Android permission model. Auto-generates policies from source code with 80.9% accuracy across 296 MCP servers. Critical as MCP adoption accelerates (6,000+ servers in PulseMCP). \[arXiv:2510.21236\]
- **SAGA** provides centralized governance for multi-agent systems: identity, authorization, delegation, and cryptographic tokens for inter-agent communication. \[arXiv:2504.21034\]
- **CSAgent** pushes authorization to the OS level for computer-use agents with intent-aware context spaces and automated policy generation from app specifications. \[arXiv:2509.22256\]
- **Prompt Flow Integrity (PFI)** reframes prompt injection as privilege escalation, applying integrity labels to prompt components. \[arXiv:2503.15547\]
- **RTBAS** addresses the user-fatigue problem with coarser-grained trust labels (private/public, trusted/untrusted) and classifier-based dependency detection. \[arXiv:2502.08966\]

| Paper | Year | Venue | Code | Key Contribution |
|:------|:-----|:------|:-----|:-----------------|
| Progent \[arXiv:2504.11703\] | 2025 | Preprint | [github](https://github.com/sunblaze-ucb/progent) | DSL for tool-level least-privilege; 0% ASR |
| SEAgent \[arXiv:2601.11893\] | 2026 | Preprint | -- | MAC/ABAC + confused deputy identification |
| AgentBound \[arXiv:2510.21236\] | 2025 | Preprint | -- | First MCP access control; Android-style permissions |
| SAGA \[arXiv:2504.21034\] | 2025 | Preprint | -- | Centralized governance with delegation |
| CSAgent \[arXiv:2509.22256\] | 2026 | Preprint | -- | OS-level AC for computer-use agents |
| PFI \[arXiv:2503.15547\] | 2025 | Preprint | -- | Privilege escalation framing; integrity labels |
| RTBAS \[arXiv:2502.08966\] | 2025 | Preprint | -- | Coarse-grained trust labels; reduced user fatigue |
| Encrypted Prompt \[arXiv:2503.23250\] | 2025 | Preprint | -- | Cryptographic permission embedding in prompts |
| FATH \[arXiv:2410.21492\] | 2024 | Preprint | -- | Token-based tool call authentication |
| Contextual Integrity \[arXiv:2408.02373\] | 2024 | Preprint | -- | CI framework for privacy-conscious assistants |

---

### 3.3 Runtime Verification and Policy Enforcement

**The key insight:** Monitor agent behavior as it executes, intervening when policy violations are detected. These are the guardrails that catch what slips past architectural and access control layers.

**Why it matters:** Even with architectural defenses, novel attack patterns can emerge. Runtime verification provides an observability and interception layer.

**Synthesis:**

- **AgentArmor** treats runtime traces as programs, applying CFG/DFG/PDG analysis with a type system. Best security-utility tradeoff of any framework surveyed: ASR reduced to ~3% with only 1% utility overhead. \[arXiv:2508.01249\]
- **ShieldAgent** is a guardrail-as-agent: extracts verifiable rules from policy documents into probabilistic rule circuits, then formally verifies action trajectories. \[arXiv:2503.22738\]
- **IPIGuard** constructs tool dependency graphs from execution plans and detects deviations---unjustified tool calls that have no dependency justification. \[arXiv:2508.15310\]
- **VIGIL** implements verify-before-commit: speculative reasoning + intent-grounded verification before tool execution. \[arXiv:2601.05755\]
- **Task Shield** checks whether each action still serves the user's original task, detecting goal hijacking/task drift. \[arXiv:2412.16682\]
- **DRIFT** combines a secure planner, dynamic validator, and memory-stream injection isolator. \[arXiv:2506.12104\]
- **AgentSpec** provides a DSL for runtime safety constraints across domains (code execution, robotics, driving). \[arXiv:2503.18666\]
- **AgentSentry** (Feb 2026) reframes IPI as temporal causal takeover, enabling secure task *continuation* (not just termination) under attack. Claims 0% mean ASR with 74.55% mean utility. \[arXiv:2602.22724\]

| Paper | Year | Venue | Code | Key Contribution |
|:------|:-----|:------|:-----|:-----------------|
| AgentArmor \[arXiv:2508.01249\] | 2025 | Preprint | -- | Program analysis over traces; 1% utility overhead |
| ShieldAgent \[arXiv:2503.22738\] | 2025 | Preprint | -- | Guardrail agent with formal policy verification |
| IPIGuard \[arXiv:2508.15310\] | 2025 | Preprint | -- | Tool dependency graph deviation detection |
| VIGIL \[arXiv:2601.05755\] | 2026 | Preprint | -- | Verify-before-commit protocol |
| Task Shield \[arXiv:2412.16682\] | 2024 | Preprint | -- | Task alignment enforcement; goal hijacking detection |
| DRIFT \[arXiv:2506.12104\] | 2025 | Preprint | -- | Dynamic rule-based isolation with memory protection |
| AgentSpec \[arXiv:2503.18666\] | 2025 | Preprint | -- | Cross-domain runtime constraint DSL |
| AgentSentry \[arXiv:2602.22724\] | 2026 | Preprint | -- | Temporal causal diagnostics; secure continuation |
| ToolSafe \[arXiv:2601.10156\] | 2026 | Preprint | -- | Step-level tool safety guardrail + benchmark |
| Task Drift Detection \[arXiv:2406.00799\] | 2025 | Preprint | -- | Activation-based task drift monitoring |

---

### 3.4 Detection, Filtering, and Firewalls

**The key insight:** Intercept and evaluate data flowing into the agent. These are the most deployable defenses today, functioning as an outer perimeter.

**Why it matters:** While insufficient alone (see "The Attacker Moves Second"), detection and filtering layers add meaningful friction for attackers and handle the long tail of unsophisticated injection attempts. They are also the only category with production deployments.

**Synthesis:**

- **LlamaFirewall** (Meta) is the most mature deployed system. Modular policy engine with PromptGuard 2 (BERT-style classifier), AlignmentCheck (CoT auditor), and CodeShield (static analysis). Production-deployed at Meta. However, its probabilistic components are subject to the >90% adaptive bypass rates. \[arXiv:2505.03574\]
- **MELON** uses dual execution paths (original + masked run) to detect attacks by causal independence: if the same tool call appears regardless of user intent, it's attack-driven. 0.24% ASR but 2x API cost. ICML 2025. \[arXiv:2502.05174\]
- **Spotlighting** is a prompt-only defense that can saturate static benchmarks but remains brittle under adaptive attack (e.g., >95% ASR under adaptive evaluation). \[arXiv:2403.14720, arXiv:2510.09023\]
- **CommandSans** performs token-level instruction removal from data---non-blocking sanitization with strong empirical results across benchmarks. \[arXiv:2510.08829\]
- **DataFilter** strips malicious instructions from retrieved data while preserving utility. Model-agnostic. \[arXiv:2510.19207\]
- **Tool Result Parsing** targets specifically the tool-to-agent data flow vector. \[arXiv:2601.04795\]
- **Firewalls for Agentic Networks** mirrors early internet security: agent-to-agent communication needs the same perimeter controls that network traffic got. \[arXiv:2502.01822\]
- **PISanitizer** addresses prompt injection specifically in long-context LLMs. \[arXiv:2511.10720\]
- A critical meta-finding: **simple firewalls saturate weak benchmarks** but fail on stronger evaluation. \[arXiv:2510.05244\]

| Paper | Year | Venue | Code | Key Contribution |
|:------|:-----|:------|:-----|:-----------------|
| LlamaFirewall \[arXiv:2505.03574\] | 2025 | Preprint | [github](https://github.com/meta-llama/PurpleLlama/tree/main/LlamaFirewall) | **Production at Meta**; modular guardrail suite |
| MELON \[arXiv:2502.05174\] | 2025 | ICML 2025 | [github](https://github.com/kaijiezhu11/MELON) | Causal independence detection via dual execution |
| CommandSans \[arXiv:2510.08829\] | 2025 | Preprint | -- | Token-level instruction sanitization |
| DataFilter \[arXiv:2510.19207\] | 2026 | Preprint | -- | Model-agnostic data filtering |
| Tool Result Parsing \[arXiv:2601.04795\] | 2026 | Preprint | -- | Structured parsing of tool outputs |
| Firewalls for Agentic Networks \[arXiv:2502.01822\] | 2026 | Preprint | -- | Agent-to-agent firewall paradigm |
| MCP-Guard \[arXiv:2508.10991\] | 2026 | Preprint | -- | Multi-stage MCP defense pipeline |
| PromptShield \[arXiv:2501.15145\] | 2025 | Preprint | -- | Deployable low-FPR detection benchmark |
| UniGuardian \[arXiv:2502.13141\] | 2025 | Preprint | -- | Unified multi-attack detector |
| PISanitizer \[arXiv:2511.10720\] | 2025 | Preprint | -- | Long-context prompt injection sanitization |
| AEGIS \[arXiv:2509.00088\] | 2025 | Preprint | -- | Co-evolutionary attack/defense framework |
| Multi-Agent Defense Pipeline \[arXiv:2509.14285\] | 2025 | Preprint | -- | Multi-agent layered defense |
| Firewalls Benchmark \[arXiv:2510.05244\] | 2025 | Preprint | -- | Shows firewall saturation on weak benchmarks |

---

### 3.5 Model-Level Hardening

**The key insight:** Train the model itself to distinguish instructions from data and resist injection. Complementary to---but never a substitute for---architectural defenses.

**Why it matters:** When you control the model stack, hardening reduces the baseline attack surface. The StruQ -> SecAlign -> Meta SecAlign progression shows meaningful improvement. But "The Attacker Moves Second" is a constant reminder: model-level robustness alone is insufficient.

**Synthesis:**

- **StruQ** introduced explicit instruction/data channels via special formatting + fine-tuning. The foundational model-level approach. \[arXiv:2402.06363\]
- **SecAlign** uses preference optimization: the model learns to prefer the legitimate instruction over injected content. Strong training-time defense. \[arXiv:2410.05451\]
- **Meta SecAlign** builds on SecAlign to produce an open secure foundation model with broad security/utility evaluation across benchmarks. The most practical model-hardening result to date. \[arXiv:2507.02735\]
- **DRIP** operates at the representation level: editing instruction-like semantics out of data tokens while reinforcing intended instructions via residual instruction fusion. \[arXiv:2511.00447\]
- **Instruction Hierarchy** trains models to prioritize privileged instructions when instructions conflict. CaMeL reports that GPT-4o Mini's native tool-calling stack (which implements instruction hierarchy) remains vulnerable in AgentDojo, while GPT-4o Mini with CaMeL is not. \[arXiv:2404.13208, arXiv:2503.18813\]
- **Instructional Segment Embedding** improves safety via embedding-level hierarchy. \[arXiv:2410.09102\]

| Paper | Year | Venue | Code | Key Contribution |
|:------|:-----|:------|:-----|:-----------------|
| Meta SecAlign \[arXiv:2507.02735\] | 2026 | Preprint | -- | Open secure foundation model |
| SecAlign \[arXiv:2410.05451\] | 2025 | Preprint | -- | Preference optimization for injection resistance |
| StruQ \[arXiv:2402.06363\] | 2024 | Preprint | -- | Structured instruction/data separation |
| DRIP \[arXiv:2511.00447\] | 2025 | Preprint | -- | Representation-level de-instructionalization |
| Instruction Hierarchy \[arXiv:2404.13208\] | 2024 | Preprint | -- | Privilege ordering via hierarchical instruction following |
| ISE \[arXiv:2410.09102\] | 2025 | Preprint | -- | Embedding-level instruction hierarchy |

---

### 3.6 Boundary Marking and Cryptographic Provenance

**The key insight:** Give the model a cryptographic or authenticated notion of trusted vs. untrusted text.

**Why it matters:** Intellectually interesting, but today these are less fundamental than capability systems and external policy engines, because the model still has to semantically honor the boundary marker. Current models are not natively fence-aware.

**Synthesis:**

- **Signed-Prompt** applies digital signatures to distinguish trusted system prompts from user inputs. Model-agnostic wrapper. \[arXiv:2401.07612\]
- **Prompt Fencing** uses unpredictable cryptographic delimiter tokens as boundaries. Requires the model to recognize and respect fences---the current limitation. \[arXiv:2511.19727\]
- **Encrypted Prompt** embeds current permissions as cryptographic tokens, verified before action execution. Deterministic guarantee: actions outside scope are blocked regardless of LLM output. \[arXiv:2503.23250\]
- **FATH** uses hash-based tags to authenticate and select user-intended tool call responses. \[arXiv:2410.21492\]

| Paper | Year | Venue | Key Contribution |
|:------|:-----|:------|:-----------------|
| Signed-Prompt \[arXiv:2401.07612\] | 2024 | Preprint | Cryptographic prompt authentication |
| Prompt Fencing \[arXiv:2511.19727\] | 2025 | Preprint | Cryptographic delimiter boundaries |
| Encrypted Prompt \[arXiv:2503.23250\] | 2025 | Preprint | Permission embedding + deterministic authorization |
| FATH \[arXiv:2410.21492\] | 2024 | Preprint | Hash-based tool call authentication |

---

### 3.7 Formal Methods and Semantics

**The key insight:** Provide mathematical foundations for proving that composed defense stacks actually achieve their security goals.

**Why it matters:** Formal methods give defenders confidence beyond empirical testing. The noninterference theorems established here can verify that architectural defenses prevent untrusted data from influencing trusted decisions. This category is the most nascent but the most important for long-term trust.

**Synthesis:**

- **Fides** (Microsoft Research) is the most theoretically rigorous framework: formal IFC model, taxonomy of security-utility tradeoffs, and novel "hiding"/"revealing" primitives via constrained decoding. Directly formalizes CaMeL-style defenses. \[arXiv:2505.23643\]
- **The LLMbda Calculus** introduces a formal calculus extending lambda calculus with dynamic IFC and an @ operator for LLM invocation. Proves termination-insensitive noninterference for integrity and confidentiality. The first formal semantics for prompt-response conversations. \[arXiv:2602.20064\]

| Paper | Year | Venue | Key Contribution |
|:------|:-----|:------|:-----------------|
| Fides / MS IFC \[arXiv:2505.23643\] | 2025 | Preprint | Formal IFC model; hiding/revealing primitives; noninterference proofs |
| LLMbda Calculus \[arXiv:2602.20064\] | 2026 | Preprint | Formal calculus for agentic systems; @ operator; noninterference theorem |

---

## 4. Benchmarks and Evaluation

The field's evaluation infrastructure has grown rapidly but still has significant gaps. Key finding: **many defenses that appear effective on static benchmarks fail under adaptive attack or stronger evaluation**.

| Benchmark | Year | Venue | Focus |
|:----------|:-----|:------|:------|
| **AgentDojo** \[arXiv:2406.13352\] | 2024 | NeurIPS 2024 D&B | Dynamic agentic security tasks (Workspace, Banking, Travel, Slack); most common evaluation point |
| **ASB** \[arXiv:2410.02644\] | 2025 | ICLR 2025 | Broad benchmark including memory, tool, and backdoor perspectives |
| **InjecAgent** \[arXiv:2403.02691\] | 2024 | Preprint | Early agent-specific IPI benchmark across tools |
| **BIPIA** \[arXiv:2312.14197\] | 2025 | Preprint | First systematic IPI benchmark |
| **AgentDyn** \[arXiv:2602.03117\] | 2026 | Preprint | Dynamic open-ended benchmark; shows static-benchmark overfitting |
| **ToolSafe** \[arXiv:2601.10156\] | 2026 | Preprint | Tool invocation safety evaluation + step-level guardrail |
| **PromptShield** \[arXiv:2501.15145\] | 2025 | Preprint | Deployable detection benchmark with low-FPR framing |
| **"The Attacker Moves Second"** \[arXiv:2510.09023\] | 2025 | Preprint | Meta-evaluation: adaptive attacks vs. 12 defenses |
| **SaTML CTF** | 2024 | NeurIPS 2024 | Practical prompt injection competition |
| **SPML** \[arXiv:2402.11755\] | 2024 | Preprint | DSL-based task deviation detection benchmark |

Note: prompt-only defenses such as **Spotlighting** can appear effective on static evaluations, but break under adaptive attack. \[arXiv:2403.14720, arXiv:2510.09023\]

---

## 5. Production Readiness

**The reality check:** Of 78 papers surveyed, exactly one framework explicitly reports production deployment.

### Framework Comparison Matrix

| Framework | Security Model | Deterministic? | Open Source | Reported Production? | Venue |
|:----------|:---------------|:---------------|:------------|:------------|:------|
| **LlamaFirewall** | Layered detection | Mixed | Yes ([PurpleLlama](https://github.com/meta-llama/PurpleLlama/tree/main/LlamaFirewall)) | **Yes (Meta)** | Preprint |
| **CaMeL** | IFC + Capabilities | Yes | Yes ([google-research](https://github.com/google-research/camel-prompt-injection)) | No (research artifact) | Preprint |
| **IsolateGPT/SecGPT** | Execution isolation | Partial | Yes ([SecGPT](https://github.com/llm-platform-security/SecGPT)) | No (LlamaIndex pack) | NDSS 2025 |
| **Progent** | Least privilege DSL | Yes (policies) | Yes ([sunblaze-ucb](https://github.com/sunblaze-ucb/progent)) | No | Preprint |
| **MELON** | Causal independence | No (detection) | Yes ([MELON](https://github.com/kaijiezhu11/MELON)) | No | ICML 2025 |
| **ACE** | Trusted planning + IFC | Yes | No | No | NDSS 2026 |
| **Fides** | Formal IFC | Yes | No | No | Preprint |
| **AgentArmor** | Program analysis/PDG | Mixed | No | No | Preprint |
| **AgentSentry** | Temporal causal | No (detection) | No | No | Preprint |
| **LLMbda Calculus** | Formal semantics | Yes (proofs) | No | No | Preprint |

### The Spectrum

- **Strongest formal guarantees:** Fides > CaMeL > LLMbda Calculus (theoretical)
- **Most practical/deployed:** LlamaFirewall >> SecGPT > Progent
- **Best security-utility tradeoff:** AgentArmor (1% utility drop) > MELON > CaMeL (7% gap)
- **Most comprehensive threat model:** ACE (explicitly breaks IsolateGPT) > CaMeL (honest about side channels)

### The Fundamental Tension

Every framework faces the same tradeoff: **deterministic security guarantees vs. policy authoring burden**. Progent's LLM-generated policies and LlamaFirewall's probabilistic scanners both attempt to ease this burden---but both re-introduce the probabilistic element that architectural approaches were designed to eliminate.

### The Open Ecosystem Gap

No production-grade, open-source framework yet combines CaMeL-style IFC with Progent-style automated policy generation and LlamaFirewall-style deployment maturity. This is the key integration challenge for the field.

---

## 6. Recommended Defense Stack

Based on the surveyed research, a production agent system should implement as many layers as constraints allow, starting from Layer 1 as the non-negotiable foundation.

### Layer 1 -- Architecture (Non-Negotiable)

**Separate trusted planning from untrusted data processing.**

- The privileged planner reasons over the user's goal and typed summaries, never raw untrusted content
- Convert untrusted content into typed data early; treat raw strings as toxic until parsed
- Reference implementations: CaMeL \[arXiv:2503.18813\], Type-Directed Separation \[arXiv:2509.25926\]
- Design guidance: Design Patterns \[arXiv:2506.08837\], Operationalizing CaMeL \[arXiv:2505.22852\]

### Layer 2 -- Access Control (Non-Negotiable)

**Put authorization in a control plane, not in prompts.**

- Tool calls, MCP actions, file/network access, and inter-agent delegation go through explicit policy enforcement
- Deny by default; grant scoped credentials and bounded capabilities
- Reference implementations: Progent \[arXiv:2504.11703\], AgentBound \[arXiv:2510.21236\], SEAgent \[arXiv:2601.11893\]

### Layer 3 -- Model Hardening (When You Control the Stack)

**Train or select models with built-in instruction-data separation.**

- Use SecAlign/Meta SecAlign-hardened models when available
- Apply instruction hierarchy and structured query formatting
- References: Meta SecAlign \[arXiv:2507.02735\], SecAlign \[arXiv:2410.05451\], StruQ \[arXiv:2402.06363\]

### Layer 4 -- Runtime Monitoring

**Verify-before-commit on every tool call; detect task drift.**

- Runtime trace analysis catches novel attack patterns not anticipated by static policies
- Guardrail agents provide policy verification
- References: AgentArmor \[arXiv:2508.01249\], ShieldAgent \[arXiv:2503.22738\], VIGIL \[arXiv:2601.05755\]

### Layer 5 -- Detection and Filtering (Outer Perimeter)

**Sanitize inputs; detect and flag injection attempts.**

- Token-level sanitization, tool result parsing, firewall classifiers
- Handles the long tail of unsophisticated attacks; buys time against sophisticated ones
- References: LlamaFirewall \[arXiv:2505.03574\], CommandSans \[arXiv:2510.08829\], DataFilter \[arXiv:2510.19207\]

### Cross-Cutting: Memory Trust Zones

**Split memory into trust zones.** Ephemeral task memory, long-term memory, and imported knowledge should not share a flat trust domain. "AI Agent Traps" \[SSRN:6372438\] systematizes these threats as "cognitive state traps"---including latent memory poisoning (innocuous data that activates maliciously in future contexts) and contextual learning traps (corrupted demonstrations steering in-context learning). \[arXiv:2407.12784, arXiv:2503.03704, arXiv:2512.16962, SSRN:6372438\]

---

## 7. Open Problems and Research Gaps

### Critical Gaps

- **Multi-agent trust boundaries:** The confused deputy problem is identified \[arXiv:2601.11893\] but securing networks of interacting agents with delegation chains remains open. "Agents of Chaos" \[arXiv:2602.20021\] empirically demonstrates cross-agent propagation of compromised states in deployed systems. SAGA \[arXiv:2504.21034\] and Firewalls for Agentic Networks \[arXiv:2502.01822\] are early steps.

- **Persistent memory poisoning:** Memory injection \[arXiv:2503.03704\], experience poisoning \[arXiv:2512.16962\], and RAG store attacks \[arXiv:2407.12784\] are demonstrated but no defense specifically addresses temporal persistence. Most current defenses assume stateless single-turn interactions.

- **Tool/function supply-chain attacks:** FuncPoison \[arXiv:2509.24408\] shows the attack surface; MCP's rapid growth (6,000+ servers, largely unvetted) makes this increasingly urgent. AgentBound \[arXiv:2510.21236\] is a start.

- **Visual and computer-use agent attacks:** As agents operate through GUIs and rendered content, prompt injection extends to the pixel layer \[arXiv:2506.02456, arXiv:2505.21936\]. No architectural defense addresses this yet.

- **Evaluation under adaptive attack:** AgentDyn \[arXiv:2602.03117\] and "The Attacker Moves Second" \[arXiv:2510.09023\] show that most current claims don't survive stronger threat models. The field needs adversarial evaluation as standard practice.

- **Social hierarchy and authority management:** "Agents of Chaos" \[arXiv:2602.20021\] reveals a fundamental gap: agents treat authority as conversationally constructed rather than cryptographically or architecturally enforced. Semantic reframing bypasses, spoofed identity acceptance, and non-owner compliance are not addressed by any current defense framework. This intersects with but is distinct from the confused deputy problem---it is about who the agent believes it should obey, not just what it is allowed to do.

- **Systemic and human-in-the-loop attacks:** "AI Agent Traps" \[SSRN:6372438\] identifies two largely novel attack surfaces: systemic traps (congestion, cascades, tacit collusion, compositional fragments, Sybil attacks targeting multi-agent dynamics) and human-in-the-loop traps (exploiting the agent to attack the human overseer via approval fatigue or social engineering). No defense framework addresses either category. Systemic traps draw on game theory and financial contagion models; benchmarking them requires multi-agent simulation environments that do not yet exist.

- **Combinatorial trap chaining:** Individual attack vectors can be composed---a content injection trap delivering a behavioural control payload, or compositional fragments that reconstitute only upon multi-agent aggregation. Current defenses evaluate attack categories in isolation. The combinatorial attack surface identified by \[SSRN:6372438\] needs evaluation methodology.

- **Accountability Gap for compromised agents:** When a compromised agent commits a financial crime or privacy violation, liability allocation between agent operator, model provider, and malicious domain owner remains an open legal question \[SSRN:6372438\]. No technical framework addresses forensic attribution from agent output back to the specific environmental trap that caused the compromise.

### Structural Challenges

- **Side-channel attacks:** Most defenses focus on direct data flow but neglect timing, token count, loop iteration, and response structure side channels. CaMeL's STRICT mode is one of the few concrete mitigations proposed so far. \[arXiv:2503.18813\]

- **Performance and cost:** Dual-LLM architectures impose ~2.8x token overhead. Plan-template caching \[arXiv:2505.22852\] is promising but unproven at scale.

- **Policy authoring at scale:** Who writes the security policies for a general-purpose agent? The CaMeL/AWS-IAM complexity problem. Progent's LLM-generated policies \[arXiv:2504.11703\] are one path, but re-introduce probabilistic risk.

- **Formal verification at scale:** Proofs exist for simplified agent models \[arXiv:2505.23643, arXiv:2602.20064\]. Scaling to real-world agents with hundreds of tools is open.

- **Standardization:** No standardized security interfaces for agent frameworks exist. MCP is emerging for tool integration, but no equivalent exists for security policy enforcement.

- **ROP-style composition attacks:** Chaining individually-allowed operations into malicious composites---the agent equivalent of return-oriented programming. CaMeL flags but doesn't solve this. \[arXiv:2503.18813\]

---

## 8. Complete Reference Index

All papers and resources referenced in this analysis, organized by category. Importance ratings: **A** = Must-read, **B** = Important, **C** = Supplementary.

Year reflects the year field in `references/bib/*.bib` (typically the latest arXiv version or publication year captured in this repo).

### Threat Model and Benchmarks

| ID | Title | Year | Importance |
|:---|:------|:-----|:-----------|
| arXiv:2302.12173 | Not What You've Signed Up For (Indirect PI) | 2023 | **A** |
| arXiv:2211.09527 | Ignore Previous Prompt (PI taxonomy) | 2022 | **A** |
| arXiv:2510.09023 | The Attacker Moves Second | 2025 | **A** |
| arXiv:2406.13352 | AgentDojo | 2024 | **A** |
| arXiv:2410.02644 | Agent Security Bench (ASB) | 2025 | **A** |
| arXiv:2602.03117 | AgentDyn | 2026 | **A** |
| arXiv:2602.20021 | Agents of Chaos (deployed agent red-team) | 2026 | **A** |
| SSRN:6372438 | AI Agent Traps (environmental attack taxonomy) | 2026 | **A** |
| arXiv:2306.05499 | HouYi (PI against commercial apps) | 2025 | **B** |
| arXiv:2403.03792 | Neural Exec (learned triggers) | 2024 | **B** |
| arXiv:2407.12784 | AgentPoison (memory/RAG attacks) | 2024 | **B** |
| arXiv:2403.02691 | InjecAgent (agent-specific PI benchmark) | 2024 | **B** |
| arXiv:2312.14197 | BIPIA (first IPI benchmark) | 2025 | **B** |
| arXiv:2503.03704 | MINJA (memory injection) | 2026 | **B** |
| arXiv:2512.16962 | MemoryGraft (experience poisoning) | 2025 | **B** |
| arXiv:2509.24408 | FuncPoison (tool supply chain) | 2025 | **B** |
| arXiv:2506.02456 | Visual PI for Computer-Use Agents | 2026 | **B** |
| arXiv:2505.21936 | RedTeamCUA | 2026 | **B** |
| arXiv:2511.20597 | BrowseSafe | 2025 | **B** |
| arXiv:2509.10540 | EchoLeak (zero-click exploit) | 2025 | **B** |
| arXiv:2510.05244 | Firewall benchmark saturation | 2025 | **B** |
| arXiv:2403.14720 | Spotlighting | 2024 | **C** |
| arXiv:2402.11755 | SPML (DSL for task deviation) | 2024 | **C** |

### Secure Architectures by Construction

| ID | Title | Year | Importance |
|:---|:------|:-----|:-----------|
| arXiv:2503.18813 | CaMeL | 2025 | **A** |
| arXiv:2403.04960 | IsolateGPT / SecGPT | 2025 | **A** |
| arXiv:2504.20984 | ACE | 2025 | **A** |
| arXiv:2509.25926 | Type-Directed Privilege Separation | 2025 | **A** |
| arXiv:2506.08837 | Design Patterns for Agent Security | 2025 | **A** |
| arXiv:2405.05175 | AirGapAgent | 2024 | **A** |
| arXiv:2505.22852 | Operationalizing CaMeL | 2025 | **B** |
| arXiv:2503.10566 | ASIDE | 2026 | **B** |

### Access Control and Governance

| ID | Title | Year | Importance |
|:---|:------|:-----|:-----------|
| arXiv:2504.11703 | Progent | 2025 | **A** |
| arXiv:2601.11893 | SEAgent (MAC/ABAC) | 2026 | **A** |
| arXiv:2510.21236 | AgentBound (MCP AC) | 2025 | **A** |
| arXiv:2504.21034 | SAGA (governance) | 2025 | **B** |
| arXiv:2509.22256 | CSAgent (computer-use AC) | 2026 | **B** |
| arXiv:2503.15547 | Prompt Flow Integrity | 2025 | **B** |
| arXiv:2502.08966 | RTBAS | 2025 | **B** |
| arXiv:2503.23250 | Encrypted Prompt | 2025 | **B** |
| arXiv:2410.21492 | FATH | 2024 | **B** |
| arXiv:2408.02373 | Contextual Integrity | 2024 | **C** |

### Runtime Verification and Policy Enforcement

| ID | Title | Year | Importance |
|:---|:------|:-----|:-----------|
| arXiv:2508.01249 | AgentArmor | 2025 | **A** |
| arXiv:2503.22738 | ShieldAgent | 2025 | **A** |
| arXiv:2508.15310 | IPIGuard | 2025 | **A** |
| arXiv:2601.05755 | VIGIL | 2026 | **A** |
| arXiv:2412.16682 | Task Shield | 2024 | **A** |
| arXiv:2506.12104 | DRIFT | 2025 | **A** |
| arXiv:2602.22724 | AgentSentry | 2026 | **B** |
| arXiv:2503.18666 | AgentSpec | 2025 | **B** |
| arXiv:2601.10156 | ToolSafe | 2026 | **B** |
| arXiv:2406.00799 | Task Drift Detection | 2025 | **C** |

### Detection, Filtering, and Firewalls

| ID | Title | Year | Importance |
|:---|:------|:-----|:-----------|
| arXiv:2505.03574 | LlamaFirewall | 2025 | **A** |
| arXiv:2502.05174 | MELON | 2025 | **A** |
| arXiv:2510.08829 | CommandSans | 2025 | **A** |
| arXiv:2510.19207 | DataFilter | 2026 | **A** |
| arXiv:2601.04795 | Tool Result Parsing | 2026 | **B** |
| arXiv:2502.01822 | Firewalls for Agentic Networks | 2026 | **B** |
| arXiv:2508.10991 | MCP-Guard | 2026 | **B** |
| arXiv:2501.15145 | PromptShield | 2025 | **B** |
| arXiv:2502.13141 | UniGuardian | 2025 | **B** |
| arXiv:2511.10720 | PISanitizer | 2025 | **B** |
| arXiv:2509.00088 | AEGIS | 2025 | **C** |
| arXiv:2509.14285 | Multi-Agent Defense Pipeline | 2025 | **C** |

### Model-Level Hardening

| ID | Title | Year | Importance |
|:---|:------|:-----|:-----------|
| arXiv:2507.02735 | Meta SecAlign | 2026 | **A** |
| arXiv:2410.05451 | SecAlign | 2025 | **A** |
| arXiv:2402.06363 | StruQ | 2024 | **A** |
| arXiv:2511.00447 | DRIP | 2025 | **B** |
| arXiv:2404.13208 | Instruction Hierarchy | 2024 | **B** |
| arXiv:2410.09102 | Instructional Segment Embedding | 2025 | **C** |

### Boundary Marking and Cryptographic Provenance

| ID | Title | Year | Importance |
|:---|:------|:-----|:-----------|
| arXiv:2401.07612 | Signed-Prompt | 2024 | **B** |
| arXiv:2511.19727 | Prompt Fencing | 2025 | **B** |
| arXiv:2503.23250 | Encrypted Prompt | 2025 | **B** |
| arXiv:2410.21492 | FATH | 2024 | **B** |

### Formal Methods and Semantics

| ID | Title | Year | Importance |
|:---|:------|:-----|:-----------|
| arXiv:2505.23643 | Fides / MS IFC | 2025 | **A** |
| arXiv:2602.20064 | LLMbda Calculus | 2026 | **A** |

### Foundations and Related Work

| ID | Title | Year | Importance |
|:---|:------|:-----|:-----------|
| arXiv:2210.03629 | ReAct | 2023 | **A** |
| arXiv:2409.19091 | System-Level Defense (IFC perspective) | 2024 | **B** |
| arXiv:2510.27246 | Long-Term Memory Benchmarking | 2026 | **C** |
| arXiv:2410.10813 | LongMemEval | 2025 | **C** |
| arXiv:2406.11230 | Multimodal Needle in a Haystack | 2025 | **C** |

### Vendor System Cards and Industry Sources

| Source | Key Contribution |
|:-------|:-----------------|
| Anthropic, Claude Opus 4.6 System Card | Frontier model safety and agentic capability assessment |
| OWASP Top 10 for LLM Applications (2025) | Industry standard threat taxonomy |
| OWASP Top 10 for Agentic Applications (Dec 2025) | ASI-prefixed taxonomy for agentic security |
| NCSC UK (2025) | Formal assessment: LLMs are "inherently confusable deputies" |
| Willison, S. -- CaMeL write-up (Apr 2025) | Accessible synthesis of architectural defense paradigm |
| Willison, S. -- Dual LLM Pattern (Apr 2023) | Foundational architectural proposal; direct precursor to CaMeL |
| Willison, S. -- MCP security (Apr 2025) | MCP tool-use paradigm amplifies attack surface |
| Willison, S. -- Lethal Trifecta (Jun 2025) | Private data + untrusted content + external communication = vulnerability |
| NeuralTrust analysis (2025--2026) | CaMeL adoption status: limited ~10 months post-publication |

---

*This analysis synthesizes and supersedes the individual RESEARCH files in `analysis/`. For deep dives on specific topics, those files remain available as detailed supplements.*
