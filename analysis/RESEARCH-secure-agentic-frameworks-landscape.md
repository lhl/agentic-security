# Secure-by-Design Agentic Frameworks: Literature Survey & Implementation Status

*Compiled March 2026*

---

## Overview

This document catalogs the emerging class of **system-level, secure-by-design defenses** for LLM-based agentic systems. Unlike probabilistic defenses (prompt augmentation, fine-tuning, classifier-based detection), these frameworks treat the LLM as an untrusted component and enforce security through architectural mechanisms: information flow control, capability systems, execution isolation, privilege control, and program analysis.

The key validation for this entire paradigm comes from **"Attacker Moves Second"** (Nasr et al., Oct 2025), a joint OpenAI/Anthropic/DeepMind red-team effort that bypassed all 12 tested probabilistic defenses at >90% attack success rate — demonstrating that model-level robustness alone is insufficient.

---

## Frameworks with Implementations

### 1. CaMeL — CApabilities for MachinE Learning
**Google DeepMind, Mar 2025**

| | |
|---|---|
| **Paper** | [arXiv:2503.18813](https://arxiv.org/abs/2503.18813) — Debenedetti, Shumailov, Fan, Hayes, Carlini, Fabian, Kern, Shi, Terzis, Tramèr |
| **GitHub** | [google-research/camel-prompt-injection](https://github.com/google-research/camel-prompt-injection) |
| **Status** | Research artifact (authors explicitly note: not production-ready, no planned maintenance) |
| **Venue** | Preprint (v2 Jun 2025) |

**Architecture:** Dual LLM (P-LLM/Q-LLM) + custom Python interpreter with capability-tagged variables tracking provenance and reader sets. Security policies are Python functions evaluated before each tool call.

**Key Results (AgentDojo):**
- Security: 0 successful prompt injection attacks (with policies)
- Utility: 77% vs 84% undefended baseline
- Overhead: ~2.8× token cost

**Security Approach:** Information flow control + capability-based access control. Deterministic enforcement — no probabilistic elements in the security layer. Extends Willison's Dual LLM pattern by tracking data flow through the Q-LLM to catch the substitution attack the original pattern misses.

**Limitations:** Requires user-authored security policies; acknowledged side channels (loop iteration, exceptions, timing); cannot protect against "data-requires-action" scenarios.

---

### 2. IsolateGPT / SecGPT
**WashU + U. Washington, Mar 2024 → NDSS 2025**

| | |
|---|---|
| **Paper** | [arXiv:2403.04960](https://arxiv.org/abs/2403.04960) — Wu, Roesner, Kohno, Zhang, Iqbal |
| **GitHub** | [llm-platform-security/SecGPT](https://github.com/llm-platform-security/SecGPT) |
| **Status** | Research implementation (LlamaIndex + LangChain + Redis); available as LlamaIndex Llama Pack |
| **Venue** | NDSS 2025 |

**Architecture:** Hub-and-spoke model inspired by OS process isolation. Each third-party app gets its own isolated "spoke" with a dedicated LLM instance. Inter-spoke communication goes through the hub via well-defined ISC (Inter-Spoke Communication) protocol with user permission.

**Key Results:**
- Defends against app compromise, data stealing, inadvertent exposure, uncontrolled system alteration
- Performance overhead <30% for 75% of tested queries

**Security Approach:** Execution isolation — analogous to process sandboxing in operating systems. Apps cannot directly access each other's data or the system LLM.

**Limitations:** Subsequent work (ACE, 2025) demonstrated three bypass attacks: Execution Flow Disruption, Execution Manager Hijack, and Planner Manipulation — showing that isolation alone is insufficient without integrity guarantees on the planning phase.

---

### 3. Progent — Programmable Privilege Control
**UC Berkeley (Dawn Song's group), Apr 2025**

| | |
|---|---|
| **Paper** | [arXiv:2504.11703](https://arxiv.org/abs/2504.11703) — Shi, He, Wang, Wu, Li, Guo, Song |
| **GitHub** | [sunblaze-ucb/progent](https://github.com/sunblaze-ucb/progent) |
| **Status** | Research implementation with AgentDojo, ASB, and AgentPoison integration |
| **Venue** | Preprint (v2 Aug 2025) |

**Architecture:** Proxy-based privilege control layer that intercepts agent tool calls. Features a domain-specific language (DSL) for expressing fine-grained policies on tool arguments, with fallback actions and dynamic policy updates.

**Key Results:**
- ASR: 0% (provably guaranteed via deterministic policies) — down from 39.9% baseline
- Utility preserved in both attack and no-attack scenarios
- LLM-generated policies shown viable (with some re-introduction of probabilistic risk)

**Security Approach:** Least-privilege enforcement at the tool-call level. Policies are deterministic — the probabilistic element only enters if using LLM-generated policies. Modular design: plugs into existing agents without modifying internals.

**Limitations:** DSL complexity/usability for end users; cannot defend against attacks operating within the least-privilege boundary (e.g., preference manipulation); focused on tool calls — doesn't cover text-output attacks.

---

### 4. LlamaFirewall
**Meta, Apr 2025**

| | |
|---|---|
| **Paper** | [arXiv:2505.03574](https://arxiv.org/abs/2505.03574) — Chennabasappa et al. |
| **GitHub** | [meta-llama/PurpleLlama/LlamaFirewall](https://github.com/meta-llama/PurpleLlama/tree/main/LlamaFirewall) |
| **Status** | **Production deployment at Meta** — most mature of the implementations |
| **Venue** | Preprint (May 2025) |

**Architecture:** Modular policy engine orchestrating multiple security scanners across the agent lifecycle:
- **PromptGuard 2**: BERT-style classifier for direct prompt injection (low-latency, high-throughput)
- **AlignmentCheck (Agent Alignment Checks)**: Chain-of-thought auditor inspecting agent reasoning for goal hijacking/misalignment
- **CodeShield**: Online static analysis for LLM-generated code (Semgrep + regex, 8 languages)
- **Custom Scanners**: Regex/LLM-prompt based pattern matching

**Security Approach:** Layered defense — combines probabilistic detection (PromptGuard, AlignmentCheck) with deterministic static analysis (CodeShield). Not pure secure-by-design in the CaMeL sense, but system-level rather than model-level.

**Limitations:** PromptGuard and AlignmentCheck are probabilistic classifiers — subject to the >90% bypass rates demonstrated by "Attacker Moves Second" for this defense class. Subsequent work (ControlValve) demonstrated control-flow hijacking attacks that evade alignment checks even with advanced LLMs.

**Note:** Part of Meta's broader PurpleLlama ecosystem (CyberSecEval, Llama Guard, Prompt Guard).

---

### 5. MELON — Masked re-Execution and TooL comparisON
**UC Santa Barbara + William & Mary, Feb 2025 → ICML 2025**

| | |
|---|---|
| **Paper** | [arXiv:2502.05174](https://arxiv.org/abs/2502.05174) — Zhu, Yang, Wang, Guo, Wang |
| **GitHub** | [kaijiezhu11/MELON](https://github.com/kaijiezhu11/MELON) |
| **Status** | Research implementation (AgentDojo integration) |
| **Venue** | ICML 2025 |

**Architecture:** Detection-based defense using parallel execution paths. The original run processes the user task normally; a masked run replaces the user prompt with a task-neutral prompt while preserving retrieved data. If both runs produce similar tool calls, the action is flagged as attack-driven (since it's independent of user intent).

**Key Results (GPT-4o):**
- MELON: 0.24% ASR, 58.78% UA
- MELON-Aug (+ prompt augmentation): 0.32% ASR, 68.72% UA
- Outperforms all baseline defenses on security-utility tradeoff

**Security Approach:** Behavioral/causal — exploits the insight that successful attacks decouple tool calls from user intent. Training-free, inference-time only.

**Limitations:** 2× API cost (dual execution); causal "blindspot" for conditional attacks intertwined with legitimate logic; still fundamentally a detection approach rather than provable prevention.

---

### 6. ACE — Abstract-Concrete-Execute
**Northeastern University, Apr 2025**

| | |
|---|---|
| **Paper** | [arXiv:2504.20984](https://arxiv.org/abs/2504.20984) — Li, Mallick, Rose, Robertson, Oprea, Nita-Rotaru |
| **GitHub** | No public repo found |
| **Status** | Research (accepted NDSS 2026) |
| **Venue** | NDSS 2026 |

**Architecture:** Decouples planning into two phases: (1) abstract plan generation using only trusted information (user query + app schemas, no app descriptions), (2) concrete plan mapping using installed app specs. Execution phase then enforces static security policies over the concrete plan.

**Key Insight:** Identifies and demonstrates three attacks against IsolateGPT (Execution Flow Disruption, Execution Manager Hijack, Planner Manipulation), then proposes ahead-of-time planning on trusted-only data as the fix.

**Security Approach:** Separating planning integrity from untrusted app content, with static policy enforcement on execution. Bridges the gap between IsolateGPT's isolation model and CaMeL's information flow approach.

---

### 7. Fides — Microsoft IFC for AI Agents
**Microsoft Research, May 2025**

| | |
|---|---|
| **Paper** | [arXiv:2505.23643](https://arxiv.org/abs/2505.23643) — Costa, Köpf, Kolluri, Paverd, Russinovich, Salem, Tople, Wutschitz, Zanella-Béguelin |
| **GitHub** | No public repo found |
| **Status** | Research (v2 Sep 2025) |
| **Venue** | Preprint |

**Architecture:** Formal model for reasoning about security and expressiveness of agent planners. Fides (Flow Integrity Deterministic Enforcement System) tracks confidentiality and integrity labels, deterministically enforces security policies, and introduces novel primitives for selectively hiding/revealing information via constrained decoding.

**Key Contributions:**
- Formal characterization of properties enforceable by dynamic taint-tracking
- Taxonomy of tasks evaluating security-utility tradeoffs across planner designs
- "Hiding" primitive: quarantined LLM sees data via constrained decoding but sensitive content is redacted from outputs
- "Revealing" primitive: inspects stored variables using quarantined LLM with strict schema enforcement

**Security Approach:** Classical information flow control (IFC) with formal proofs. Most theoretically rigorous of the frameworks — provides formal model rather than just empirical evaluation.

---

### 8. AgentArmor
**UCLA et al., Aug 2025**

| | |
|---|---|
| **Paper** | [arXiv:2508.01249](https://arxiv.org/abs/2508.01249) — Wang, Liu, Lu, Cai, Chen, Yang, Zhang, Hong, Wu |
| **GitHub** | No public repo found |
| **Status** | Research (v3 Nov 2025) |
| **Venue** | Preprint |

**Architecture:** Runtime program analysis framework that converts agent execution traces into Program Dependence Graphs (PDGs) — CFG, DFG, and PDG representations. A property registry attaches security metadata; a type system performs inference and checking.

**Key Results (AgentDojo):**
- ASR reduced to ~3% (1.16% average in some configurations)
- Only 1% utility overhead — lowest of any framework surveyed
- 95.75% TPR, 3.66% FPR

**Security Approach:** Treats agent runtime traces as programs with analyzable semantics. The dependency analyzer infers control and data flow from natural language reasoning patterns, enabling formal PDG-based policy enforcement.

**Note:** Uses an LLM for dependency analysis, so contains a probabilistic element — but the enforcement mechanism itself is deterministic once the graph is constructed.

---

## Frameworks Without Public Implementations (Paper-Only)

### 9. Prompt Flow Integrity (PFI)
- **Focus:** Privilege escalation prevention via untrusted data identification, least privilege enforcement, and unsafe data flow validation
- **Status:** Paper only, referenced in Progent and related work

### 10. ControlValve
- **Focus:** Control-flow integrity + least privilege for multi-agent systems. Generates permitted control-flow graphs and enforces compliance with contextual rules.
- **Notable:** Demonstrated control-flow hijacking attacks that bypass LlamaFirewall's alignment checks
- **Status:** Paper only (referenced in Progent/ResearchGate discussions)

### 11. The LLMbda Calculus
- **Paper:** [arXiv:2602.20064](https://arxiv.org/abs/2602.20064) — Garby, Gordon, Sands (Feb 2026)
- **Focus:** Formal semantic foundation — untyped call-by-value lambda calculus with dynamic IFC and LLM invocation primitives. Proves termination-insensitive noninterference (integrity + confidentiality).
- **Significance:** First formal calculus for agentic programming with provable security properties. Theoretical complement to the empirical frameworks above.

### 12. AgentSentry
- **Paper:** [arXiv:2602.22724](https://arxiv.org/abs/2602.22724) (Feb 2026)
- **Focus:** Temporal causal diagnostics for multi-turn IPI. Reframes attacks as temporal causal takeover and performs boundary-local causal attribution.
- **Key Claim:** First inference-time defense enabling secure task *continuation* (not just termination) under IPI.
- **Results:** Mean UA 74.55% with 0% mean ASR

---

## Comparison Matrix

| Framework | Security Model | Deterministic? | GitHub? | Production? | Venue |
|---|---|---|---|---|---|
| **CaMeL** | IFC + Capabilities | Yes | ✅ google-research | No (research artifact) | Preprint |
| **IsolateGPT** | Execution Isolation | Partial | ✅ llm-platform-security/SecGPT | LlamaIndex Pack | NDSS 2025 |
| **Progent** | Least Privilege/DSL | Yes (policies) | ✅ sunblaze-ucb/progent | No | Preprint |
| **LlamaFirewall** | Layered Detection | Mixed | ✅ meta-llama/PurpleLlama | **Yes (Meta)** | Preprint |
| **MELON** | Causal Independence | No (detection) | ✅ kaijiezhu11/MELON | No | ICML 2025 |
| **ACE** | Trusted Planning + IFC | Yes | ❌ | No | NDSS 2026 |
| **Fides (MS)** | Formal IFC | Yes | ❌ | No | Preprint |
| **AgentArmor** | Program Analysis/PDG | Mixed | ❌ | No | Preprint |
| **LLMbda Calculus** | Formal Semantics | Yes (proofs) | ❌ | No | Preprint |
| **AgentSentry** | Temporal Causal | No (detection) | ❌ | No | Preprint |

---

## Full Reference List

### A. Secure-by-Design Agentic Frameworks (Primary)

1. **CaMeL** — Debenedetti, E., Shumailov, I., Fan, T., Hayes, J., Carlini, N., Fabian, D., Kern, C., Shi, C., Terzis, A., & Tramèr, F. (2025). "Defeating Prompt Injections by Design." arXiv:2503.18813. GitHub: google-research/camel-prompt-injection

2. **IsolateGPT / SecGPT** — Wu, Y., Roesner, F., Kohno, T., Zhang, N., & Iqbal, U. (2025). "IsolateGPT: An Execution Isolation Architecture for LLM-Based Agentic Systems." NDSS 2025. arXiv:2403.04960. GitHub: llm-platform-security/SecGPT

3. **Progent** — Shi, T., He, J., Wang, Z., Wu, L., Li, H., Guo, W., & Song, D. (2025). "Progent: Programmable Privilege Control for LLM Agents." arXiv:2504.11703. GitHub: sunblaze-ucb/progent

4. **LlamaFirewall** — Chennabasappa, S. et al. (2025). "LlamaFirewall: An Open Source Guardrail System for Building Secure AI Agents." arXiv:2505.03574. GitHub: meta-llama/PurpleLlama/LlamaFirewall

5. **Fides / Microsoft IFC** — Costa, M., Köpf, B., Kolluri, A., Paverd, A., Russinovich, M., Salem, A., Tople, S., Wutschitz, L., & Zanella-Béguelin, S. (2025). "Securing AI Agents with Information-Flow Control." arXiv:2505.23643

6. **ACE** — Li, E., Mallick, T., Rose, E., Robertson, W., Oprea, A., & Nita-Rotaru, C. (2025). "ACE: A Security Architecture for LLM-Integrated App Systems." arXiv:2504.20984. NDSS 2026.

7. **MELON** — Zhu, K., Yang, X., Wang, J., Guo, W., & Wang, W. Y. (2025). "MELON: Provable Defense Against Indirect Prompt Injection Attacks in AI Agents." ICML 2025. arXiv:2502.05174. GitHub: kaijiezhu11/MELON

8. **AgentArmor** — Wang, P., Liu, Y., Lu, Y., Cai, Y., Chen, H., Yang, Q., Zhang, J., Hong, J., & Wu, Y. (2025). "AgentArmor: Enforcing Program Analysis on Agent Runtime Trace to Defend Against Prompt Injection." arXiv:2508.01249

9. **LLMbda Calculus** — Garby, Z., Gordon, A. D., & Sands, D. (2026). "The LLMbda Calculus: AI Agents, Conversations, and Information Flow." arXiv:2602.20064

10. **AgentSentry** — (2026). "AgentSentry: Mitigating Indirect Prompt Injection in LLM Agents." arXiv:2602.22724

### B. Critical Validation / Red-Teaming

11. **Attacker Moves Second** — Nasr, M. et al. (2025). Joint OpenAI/Anthropic/DeepMind evaluation bypassing 12 published defenses at >90% ASR. (The paper that validates the entire architectural approach.)

12. **SaTML CTF** — Debenedetti, E. et al. (2024a). "Dataset and Lessons Learned from the 2024 SaTML LLM Capture-the-Flag Competition."

### C. Benchmarks

13. **AgentDojo** — Debenedetti, E., Zhang, J., Balunovic, M., Beurer-Kellner, L., Fischer, M., & Tramèr, F. (2024b). "AgentDojo: A Dynamic Environment to Evaluate Prompt Injection Attacks and Defenses for LLM Agents." NeurIPS 2024 D&B Track.

14. **ASB** — Zhang, J. et al. (2024). "Agent Security Benchmark."

15. **AgentPoison** — Chen, Z. et al. (2024). "AgentPoison: Red-Teaming LLM Agents via Poisoning Memory or Knowledge Bases." NeurIPS 2024.

### D. Foundational Prompt Injection

16. **Original prompt injection** — Goodside, R. (2022). First public demonstration of prompt injection.

17. **Prompt injection taxonomy** — Perez, F. & Ribeiro, I. (2022). "Ignore This Title and HackAPrompt: Exposing Systemic Weaknesses of LLMs through a Global Scale Prompt Hacking Competition."

18. **Indirect prompt injection** — Greshake, K. et al. (2023). "Not What You've Signed Up For: Compromising Real-World LLM-Integrated Applications with Indirect Prompt Injection."

19. **Dual LLM pattern** — Willison, S. (2023). "The Dual LLM Pattern for Building AI Assistants That Can Resist Prompt Injection."

20. **Willison: MCP security** — Willison, S. (2025). "Model Context Protocol Has Prompt Injection Security Problems."

21. **Willison: Design patterns** — Willison, S. (2025). "Design Patterns for Securing LLM Agents Against Prompt Injections."

22. **Willison: Lethal Trifecta** — Willison, S. (2025). "The Lethal Trifecta for AI Agents: Private Data, Untrusted Content, and External Communication."

23. **Willison: Agents Rule of Two** — Willison, S. (2025). Referenced in CaMeL review.

### E. Probabilistic Defenses (Outperformed by Architectural Approaches)

24. **Instruction Hierarchy** — Wallace, E., Xiao, K., Leike, R., Weng, L., Heidecke, J., & Beutel, A. (2024). "The Instruction Hierarchy: Training LLMs to Prioritize Privileged Instructions." arXiv:2404.13208

25. **StruQ** — Chen, S., Piet, J., Sitawarin, C., & Wagner, D. (2024). "StruQ: Defending Against Prompt Injection with Structured Queries." arXiv:2402.06363

26. **SecAlign** — Chen, S. et al. (2024). "SecAlign: Defending Against Prompt Injection with Preference Optimization." arXiv:2410.05451

27. **Spotlighting** — Hines, K. et al. (2024). Data marking/encoding strategies for distinguishing trusted vs. untrusted tokens.

28. **PromptGuard / Llama Guard** — Meta (2024-2025). Classifier-based detection models (part of PurpleLlama ecosystem).

### F. Software Security Ancestry

29. **Information Flow Control** — Denning, D. E. & Denning, P. J. (1977). "Certification of Programs for Secure Information Flow."

30. **Decentralized IFC** — Myers, A. C. & Liskov, B. (1997). "A Decentralized Model for Information Flow Control." (JFlow/Jif)

31. **Control Flow Integrity** — Abadi, M. et al. (2009). "Control-Flow Integrity: Principles, Implementations, and Applications."

32. **Capsicum** — Watson, R. N. M. et al. (2010). "Capsicum: Practical Capabilities for UNIX." (OS-level capability system)

33. **CHERI** — Watson, R. N. M. et al. (2015). "CHERI: A Hybrid Capability-System Architecture for Scalable Software Compartmentalization." (Hardware capability system — illustrative of adoption challenges)

34. **Security Engineering** — Anderson, R. (2010). *Security Engineering: A Guide to Building Dependable Distributed Systems.* (Foundational reference for policy design, usability constraints)

### G. Additional Related Work

35. **DRIFT** — Li, H. et al. (2025). "DRIFT: Dynamic Rule-Based Defense with Injection Isolation for Securing LLM Agents." arXiv:2506.12104

36. **SafeFlow** — Li, P. et al. (2025). "SafeFlow: A Principled Protocol for Trustworthy and Transactional Autonomous Agent Systems."

37. **IPIGuard** — An, H. et al. (2025). "IPIGuard: A Novel Tool Dependency Graph-Based Defense Against Indirect Prompt Injection in LLM Agents."

38. **AEGIS** — Liu, T.-C. et al. (2025). "AEGIS: Automated Co-Evolutionary Framework for Guarding Prompt Injections Schema." arXiv:2509.00088

39. **Pasquini et al.** — (2024). Neural exec attack and defense landscape survey.

40. **NeuralTrust analysis** — (2025-2026). Industry analysis of CaMeL adoption status showing limited production deployments ~10 months post-publication.

41. **OWASP Top 10 for LLM Applications** — (2025). Industry standard threat taxonomy.

42. **OWASP Top 10 for Agentic Applications** — (2026, Dec 2025 release). ASI-prefixed taxonomy for agentic security issues.

43. **AI Agents with Formal Security Guarantees** — Balunovic, M., Beurer-Kellner, L., Fischer, M., & Vechev, M. (2024). ICML 2024 Next Generation of AI Safety Workshop.

44. **US AISI Evaluations** — (2024-2025). Government-led AI safety evaluations referenced in CaMeL benchmarking.

---

## Key Takeaways

**What exists and runs:**
- 5 frameworks have public GitHub repos with runnable code (CaMeL, IsolateGPT/SecGPT, Progent, LlamaFirewall, MELON)
- Only LlamaFirewall is confirmed in production (Meta)
- All others are research artifacts — some quite complete (SecGPT has LlamaIndex integration), others minimal

**The spectrum:**
- **Strongest formal guarantees:** Fides (Microsoft) > CaMeL > LLMbda Calculus (theoretical)
- **Most practical/deployed:** LlamaFirewall >> SecGPT > Progent
- **Best security-utility tradeoff:** AgentArmor (1% utility drop) > MELON > CaMeL (7% gap)
- **Most comprehensive threat model:** ACE (explicitly attacks IsolateGPT) > CaMeL (honest about side channels)

**The fundamental tension:**
Every framework faces the same tradeoff CaMeL identified: deterministic security guarantees vs. policy authoring burden. Progent's LLM-generated policies and LlamaFirewall's probabilistic scanners are both attempts to ease this burden — but both re-introduce the probabilistic element that architectural approaches were designed to eliminate.

**Open ecosystem gap:**
No production-grade, open-source framework yet combines CaMeL-style IFC with Progent-style automated policy generation and LlamaFirewall-style deployment maturity. This remains the key integration challenge for the field.
