 https://claude.ai/chat/80225b77-2528-4a7f-b43c-7769b21390b9 

**Securing AI Agents:**

**A Comprehensive Research Review**

Defense-in-Depth Strategies and Secure Architectures

for LLM-Based Agent Systems

33 Papers | 2024–2026 | Organized by Defense Taxonomy

Compiled March 2026

# **Table of Contents**

# **Executive Summary**

This document reviews 33 research papers published between 2024 and 2026 addressing the security of LLM-based AI agents. As agents increasingly operate with real-world tool access, processing untrusted inputs from emails, web pages, and databases, the attack surface grows dramatically beyond traditional LLM safety concerns. Prompt injection, the most critical vulnerability, allows adversaries to hijack agent behavior through malicious content embedded in otherwise benign data sources.

The research landscape reveals a maturing field coalescing around several key defense paradigms. Architectural approaches like the Dual LLM pattern and CaMeL offer the strongest theoretical guarantees by separating trusted planning from untrusted data processing. Information flow control and formal verification methods provide mathematical foundations for reasoning about agent security. Meanwhile, practical runtime defenses including guardrail frameworks, access control systems, and detection mechanisms offer deployable layers for real-world systems.

No single defense is sufficient. The consensus across the literature points toward defense-in-depth strategies combining architectural isolation, privilege separation, runtime monitoring, and formal guarantees. This review organizes the research into seven defense categories to provide a complete picture of what is available, what is being developed, and where critical gaps remain.

# **Threat Landscape Overview**

Before examining defenses, it is important to understand the attack surface these papers collectively address. LLM agents face threats at every layer of their architecture.

## **Core Attack Vectors**

**Indirect Prompt Injection (IPI):** The most critical and widely studied threat. Malicious instructions are embedded in data the agent processes (emails, web pages, documents), causing the agent to execute unintended actions. Unlike direct jailbreaks, the user is the victim, not the attacker.

**Privilege Escalation:** Agents perform actions exceeding the least privilege required for the user’s task. This includes the confused deputy problem in multi-agent systems, where one agent tricks another into performing unauthorized actions on its behalf.

**Data Exfiltration:** Adversaries use prompt injection to redirect sensitive data to attacker-controlled endpoints through unauthorized tool calls, side channels in outputs, or chained tool invocations.

**Tool Abuse:** Over-privileged tool access enables attackers to invoke destructive operations (file deletion, financial transactions, code execution) via compromised agent reasoning.

**Multi-Agent Trust Boundary Violations:** In multi-agent systems, agents that correctly reject malicious direct instructions may accept those same instructions when propagated by a peer agent, creating novel trust boundary issues.

# **Defense Taxonomy**

The following taxonomy organizes the 33 papers into seven categories based on primary defense mechanism. Many papers span multiple categories; they are placed where their primary contribution lies, with cross-references noted.

| Defense Category | \# | Representative Approaches |
| :---- | :---- | :---- |
| Architectural / Control-Data Separation | 6 | Dual LLM, CaMeL, type-directed separation, data flow isolation |
| Access Control & Privilege Separation | 7 | MAC/ABAC frameworks, permission models, policy DSLs, governance architectures |
| Runtime Monitoring & Guardrails | 5 | Guard agents, runtime spec enforcement, verify-before-commit, defense-in-depth pipelines |
| Prompt-Level Defenses | 6 | Cryptographic signing, encrypted permissions, fencing, token sanitization, spotlighting, representation editing |
| Detection & Filtering | 4 | Unified attack detection, program analysis, tool dependency graphs, test-time filtering |
| Formal Methods & Verification | 3 | Information flow control, lambda calculus semantics, noninterference proofs |
| Benchmarks & Evaluation | 2 | Deployable detection benchmarks, tool invocation safety evaluation |

# **Category 1: Architectural and Control-Data Separation**

These papers propose fundamental architectural changes to how agents process information, separating trusted control flow from untrusted data to prevent prompt injection from influencing agent behavior. This category represents the strongest defense paradigm, offering provable or near-provable security guarantees.

## **1.1 Foundational Architecture**

**CaMeL: Defeating Prompt Injections by Design**

*arXiv: 2503.18813 | Debenedetti, Shumailov, Fan, Hayes, Carlini, Fabian, Kern, Shi, Terzis, Tramèr (Google DeepMind)*

The landmark paper in architectural defense. CaMeL (CApabilities for MachinE Learning) creates a protective system layer around the LLM, explicitly separating control flow from data flow. A Privileged LLM (P-LLM) converts user queries into a restricted Python-like program, while a Quarantined LLM (Q-LLM) processes untrusted data without tool access. A custom interpreter tracks data provenance through capability tokens, ensuring untrusted data can never influence program control flow or be exfiltrated via unauthorized channels. Solves 77% of tasks with provable security on AgentDojo (vs. 84% undefended).

**Key contributions:** Capability-based security model for LLM agents; custom Python interpreter with provenance tracking; formal separation of control and data planes; addresses the flaw in the Dual LLM pattern where Q-LLM outputs could still be weaponized as tool arguments.

**Operationalizing CaMeL: Strengthening LLM Defenses for Enterprise Deployment**

*arXiv: 2505.22852 | Tallam, Miller (SentinelAI)*

A response paper identifying practical gaps in CaMeL for enterprise deployment: the assumption of trusted user prompts, omission of side-channel concerns, and performance overhead from dual-LLM invocation. Proposes four engineering improvements: prompt screening for initial inputs, output auditing to detect instruction leakage, a tiered-risk access model balancing usability and control, and a formally verified intermediate language replacing the restricted Python subset.

**Key contributions:** Identifies CaMeL’s enterprise deployment gaps; proposes plan-template caching to reduce latency; introduces policy-as-code framework for managing tool policies at scale; advocates verified intermediate language for static guarantees.

**Better Privilege Separation for Agents by Restricting Data Types**

*arXiv: 2509.25926 | Authors from multiple institutions*

Addresses a critical shortcoming of the Dual LLM pattern: the prohibition on data flowing from Q-LLM to P-LLM restricts functionality. Proposes type-directed privilege separation, allowing data to flow between the quarantined and privileged LLMs only when it belongs to carefully selected data types (integers, booleans, enums) that cannot carry instruction payloads. This enables applications that the original Dual LLM pattern could not protect while maintaining injection resistance.

**Key contributions:** Type system as security boundary; data types chosen to be non-instruction-bearing; extends Dual LLM pattern’s applicability to broader class of agents; demonstrated on bug-fixing agent scenarios.

**AirGapAgent: Protecting Privacy-Conscious Conversational Agents**

*arXiv: 2405.05175 | Multiple authors*

Proposes data isolation between agent components through air-gapped architecture. The agent processes sensitive user data in isolated compartments that cannot leak to untrusted contexts. Draws from the Contextual Integrity framework and Mandatory Access Control principles to ensure security-critical actions are performed only when contextual conditions are met.

**Key contributions:** Privacy-by-design architecture for agents; contextual integrity-based data flow restrictions; compartmentalized processing of sensitive information.

## **1.2 Design Patterns**

**Design Patterns for Securing LLM Agents against Prompt Injections**

*arXiv: 2506.08837 | Multiple authors*

A systematic catalog of security design patterns for LLM agents, analogous to the Gang of Four design patterns for object-oriented software. Identifies recurring architectural solutions across the literature and organizes them into a reusable pattern language. Covers input sanitization patterns, output validation patterns, privilege separation patterns, and monitoring patterns. Provides practitioners with a structured approach to composing defenses.

**Key contributions:** First systematic pattern catalog for LLM agent security; pattern composition guidance; bridges academic research and practical implementation; reusable across agent frameworks.

**Prompt Flow Integrity: Preventing Privilege Escalation in LLM Agents**

*arXiv: 2503.15547 | Multiple authors*

Introduces the concept of prompt flow integrity, drawing an analogy to control flow integrity in systems security. The framework tags prompts with integrity labels and ensures that data from untrusted sources (plugin outputs, retrieved documents) cannot influence the control flow of the agent. Prevents privilege escalation by ensuring that the LLM’s planning decisions are based only on trusted prompt components.

**Key contributions:** Prompt flow integrity as first-class security property; integrity labeling for prompt components; prevents privilege escalation via tainted data influence on planning.

# **Category 2: Access Control and Privilege Separation**

These papers apply established access control paradigms from systems security (MAC, ABAC, RBAC) to the LLM agent domain, enforcing least-privilege principles on tool invocations and inter-agent communication.

**SEAgent: Taming Privilege Escalation in LLM Agent Systems via Mandatory Access Control**

*arXiv: 2601.11893 | Multiple authors*

Applies mandatory access control (MAC) built on attribute-based access control (ABAC) to LLM agent systems. Identifies novel privilege escalation scenarios in multi-agent systems, including a variant of the confused deputy problem where one agent tricks another into exceeding its authority. SEAgent monitors agent-tool interactions via an information flow graph and enforces customizable security policies based on entity attributes.

**Key contributions:** First formal identification of confused deputy problem in multi-agent LLM systems; information flow graph for runtime monitoring; ABAC-based policy enforcement; handles both single and multi-agent privilege escalation.

**CSAgent: Context-Aware Access Control for Computer-Use Agents**

*arXiv: 2509.22256 | Multiple authors*

A system-level, static policy-based access control framework for computer-use agents. Introduces intent-aware context spaces, per-application hierarchical structures that organize policies by function and predicted user intent. Uses LLM-based context analysis to generate policies automatically from application specifications, and employs static analysis for GUI applications to build semantic knowledge bases linking interface elements to their handlers.

**Key contributions:** Intent prediction for dynamic policy selection; automated policy generation from app specifications and GUI analysis; static rather than LLM-dependent runtime enforcement; addresses gap between static policy and dynamic context.

**Progent: Programmable Privilege Control for LLM Agents**

*arXiv: 2504.11703 | Shi, He, Wang, Li, Wu, Guo, Song*

The first privilege control framework that enforces security at the tool level. Features a domain-specific language for expressing fine-grained policies controlling tool privileges, with flexible fallback actions when calls are blocked and dynamic policy updates. Addresses the root cause enabling most attacks: over-privileged tool access.

**Key contributions:** DSL for tool privilege policies; dynamic policy updates; fallback action mechanisms; addresses over-privilege as root cause of agent exploitation.

**AgentBound: Securing AI Agent Execution**

*arXiv: 2510.21236 | Bühler, Biagiola, Di Grazia, Salvaneschi*

The first access control framework specifically for MCP (Model Context Protocol) servers. Combines a declarative policy mechanism inspired by the Android permission model with a policy enforcement engine that contains malicious behavior without requiring MCP server modifications. Built a dataset of 296 popular MCP servers and demonstrated 80.9% accuracy in automatic policy generation from source code.

**Key contributions:** First MCP-specific access control; Android permission model adaptation; automatic policy generation from source code; no MCP server modification required; addresses the rapid proliferation of unvetted MCP servers.

**SAGA: A Security Architecture for Governing AI Agentic Systems**

*arXiv: 2504.21034 | Syros et al. (Northeastern University)*

A scalable security architecture for governing multi-agent systems with user oversight. Users register agents with a central Provider entity that maintains contact information, access control policies, and helps agents enforce policies on inter-agent communication. Unlike purely theoretical proposals, SAGA provides concrete implementation and evaluation of agent identity, authorization, and delegation mechanisms.

**Key contributions:** User-controlled agent lifecycle management; central Provider for policy enforcement; concrete implementation (not just theoretical); inter-agent authorization and delegation.

**Encrypted Prompt: Securing LLM Applications Against Unauthorized Actions**

*arXiv: 2503.23250 | Multiple authors*

Appends an encrypted prompt to each user request, embedding current permissions as cryptographic tokens. Permissions are verified before executing any LLM-generated actions (API calls, tool invocations). If permissions are insufficient, actions are blocked regardless of what the LLM generates. Provides deterministic guarantee: only actions within scope of current permissions can proceed.

**Key contributions:** Cryptographic permission embedding; deterministic action authorization; immune to prompt injection affecting authorization decisions; shifts security check outside the LLM.

**FATH: Authentication-Based Defense for LLM Agents**

*arXiv: 2410.21492 | Multiple authors*

Proposes an authentication-based framework where tool calls must include valid authentication tokens that are generated based on the original user intent. The system verifies that each tool invocation aligns with the authenticated task before execution, preventing hijacked agents from performing unauthorized operations.

**Key contributions:** Token-based tool call authentication; intent verification before execution; defense independent of LLM robustness to injection.

# **Category 3: Runtime Monitoring and Guardrails**

These papers provide runtime safety layers that monitor agent behavior and intervene when violations are detected. They function as an outer defense perimeter, complementing architectural defenses.

**ShieldAgent: Shielding Agents via Verifiable Safety Policy Reasoning**

*arXiv: 2503.22738 | Multiple authors*

The first guardrail agent designed to enforce explicit safety policy compliance on the action trajectories of other protected agents. Constructs a safety policy model by extracting verifiable rules from policy documents and structuring them into action-based probabilistic rule circuits. Given a protected agent’s action trajectory, ShieldAgent retrieves relevant circuits and generates a shielding plan using its tool library and executable code for formal verification.

**Key contributions:** Guardrail-as-agent paradigm; probabilistic rule circuits from policy documents; formal verification of action trajectories; tool library for automated policy checking.

**AgentSpec: Customizable Runtime Enforcement for Safe and Reliable LLM Agents**

*arXiv: 2503.18666 | Wang, Poskitt, Sun*

A lightweight domain-specific language for specifying and enforcing runtime constraints on LLM agents. AgentSpec rules combine triggers, predicates, and enforcement mechanisms, ensuring agents operate within predefined safety boundaries. Implemented across code execution, embodied agents, and autonomous driving domains, demonstrating cross-domain adaptability.

**Key contributions:** DSL for runtime safety constraints; trigger-predicate-enforcement rule structure; cross-domain applicability (code, robotics, driving); addresses gap between pre-execution risk assessment and runtime enforcement.

**VIGIL: Verify-Before-Commit Protocol for LLM Agents**

*arXiv: 2601.05755 | Multiple authors*

Implements a verification protocol requiring agents to validate planned actions against safety policies before committing to execution. The protocol operates as a checkpoint mechanism in the agent loop, catching potentially harmful actions that slip past other defenses. Designed to be composable with architectural and detection-based defenses.

**Key contributions:** Pre-commit verification checkpoint; composable with other defense layers; catches actions that bypass detection.

**MCP-Guard: A Multi-Stage Defense-in-Depth Framework for MCP Security**

*arXiv: 2508.10991 | Multiple authors*

A multi-stage defense-in-depth framework specifically targeting Model Context Protocol (MCP) security. Implements layered defenses across the MCP communication pipeline, including input validation, tool invocation monitoring, and output verification. Designed to address the rapid growth of MCP servers (6,000+ in PulseMCP registry) operating without security controls.

**Key contributions:** Multi-stage pipeline defense for MCP; addresses MCP-specific attack vectors; defense-in-depth across input/execution/output stages; designed for the MCP ecosystem’s rapid growth.

**LlamaFirewall: An Open Source Guardrail System for Building Secure AI Agents**

*arXiv: 2505.03574 | Meta*

An open-source, security-focused guardrail framework designed as a final layer of defense for AI agents. Unlike chatbot-focused guardrails, LlamaFirewall is specifically designed for the higher-stakes agentic setting where agents edit production code, orchestrate workflows, and take actions based on untrusted inputs. Supports system-level, use-case-specific safety policy definition and enforcement as a real-time monitor.

**Key contributions:** Open-source agent-specific guardrail framework; real-time monitoring as final defense layer; designed for production agentic deployments; supports custom safety policies.

# **Category 4: Prompt-Level Defenses**

These papers operate directly on the prompt and token level, modifying how inputs are processed to distinguish trusted instructions from untrusted data. They range from cryptographic approaches to representation-level interventions.

**Signed-Prompt: A New Approach to Prevent Prompt Injection**

*arXiv: 2401.07612 | Multiple authors*

Applies cryptographic signing to distinguish trusted system prompts from potentially malicious user inputs. System prompts carry digital signatures that the LLM framework verifies, ensuring that the model can distinguish between authenticated instructions and injected content. The approach is model-agnostic and works as a wrapper around existing LLM deployments.

**Key contributions:** Cryptographic prompt authentication; model-agnostic defense; digital signature verification for instruction provenance; wrapper-based deployment.

**Prompt Fencing: Cryptographic Boundaries for Prompt Injection Defense**

*arXiv: 2511.19727 | Multiple authors*

Establishes cryptographic boundaries between trusted and untrusted regions within prompts. Uses unique, unpredictable delimiter tokens as fences that an attacker cannot guess or reproduce. The LLM is trained or prompted to recognize these boundaries and refuse to follow instructions that appear in untrusted regions.

**Key contributions:** Cryptographic delimiter tokens; unpredictable boundary markers; trained boundary recognition; prevents instruction following from untrusted prompt regions.

**CommandSans: Token-Level Sanitization for Prompt Injection Defense**

*arXiv: 2510.08829 | Multiple authors*

Operates at the token level to sanitize inputs, removing or neutralizing tokens that could function as instructions when they appear in data regions. The sanitization process is designed to preserve the semantic content of the data while stripping its ability to influence the LLM’s instruction-following behavior.

**Key contributions:** Token-level input sanitization; preserves data semantics while removing instruction potential; operates at the embedding/token boundary.

**Spotlighting: Input Transformation Techniques for LLM Security**

*arXiv: 2403.04960 | Multiple authors*

Introduces input transformation techniques that make it easier for the LLM to distinguish between system instructions and external data. Methods include adding special delimiters, encoding transformations, and structural markers that highlight the boundary between trusted and untrusted content. A practical, easy-to-deploy defense that improves robustness without model modification.

**Key contributions:** Input transformation for instruction-data separation; delimiter-based marking; encoding transformations; practical deployment without model changes.

**DRIP: Defending Prompt Injection via Token-wise Representation Editing**

*arXiv: 2511.00447 | Multiple authors*

A representation-level defense that precisely removes instruction semantics from tokens in the data section while preserving their data semantics. DRIP introduces a lightweight representation-editing module that modifies embeddings of instruction-like tokens in the data region, preventing them from activating the LLM’s instruction-following pathways. Additionally uses residual instruction fusion to robustly preserve the effect of intended instructions under adversarial content.

**Key contributions:** Representation-level defense; de-instructionalization of data tokens; residual instruction fusion for robustness; balances utility and security at the embedding level.

**Defense Against Indirect Prompt Injection via Tool Result Parsing**

*arXiv: 2601.04795 | Multiple authors*

Focuses specifically on the tool result vector: when agents process results from tool calls (web searches, API responses, database queries), those results may contain injected instructions. The paper proposes structured parsing of tool results that strips potential instruction content while preserving the informational payload.

**Key contributions:** Tool result-specific defense; structured parsing of untrusted tool outputs; targets the tool-to-agent data flow vector.

# **Category 5: Detection and Filtering**

These papers focus on identifying attacks in progress or filtering malicious content before it reaches the agent’s reasoning engine. They serve as an alerting and interception layer.

**UniGuardian: A Unified Defense for Detecting Prompt Injection, Backdoor Attacks, and Adversarial Attacks**

*arXiv: 2502.13141 | Multiple authors*

A unified detection framework that identifies multiple attack types through a single system: prompt injection, backdoor attacks, and adversarial examples. Rather than requiring separate detectors for each attack class, UniGuardian uses shared detection features across attack types, reducing overhead while maintaining accuracy.

**Key contributions:** Unified multi-attack detection; shared detection features across attack types; reduced deployment overhead vs. separate detectors.

**AgentArmor: Enforcing Program Analysis on Agent Runtime Traces**

*arXiv: 2508.01249 | Multiple authors*

Applies program analysis techniques to agent runtime traces, treating the sequence of agent actions as a program to be analyzed for security violations. Detects patterns indicative of prompt injection, privilege escalation, or data exfiltration by analyzing the structural properties of action sequences rather than their natural language content.

**Key contributions:** Program analysis applied to agent traces; structural pattern detection; content-agnostic analysis; detects attack patterns in action sequences.

**IPIGuard: Defending Against Indirect Prompt Injection via Tool Dependency Graphs**

*arXiv: 2508.15310 | Multiple authors*

Constructs tool dependency graphs that model the expected data flow between tools in an agent’s execution plan. Detects indirect prompt injection by identifying deviations from expected dependency patterns—when data flows through unexpected channels or tool calls appear that have no dependency justification in the original plan.

**Key contributions:** Tool dependency graph analysis; deviation detection from expected data flow; identifies unjustified tool invocations; structural rather than content-based detection.

**DataFilter: Test-Time Filtering for LLM Agent Security**

*arXiv: 2510.19207 | Multiple authors*

A test-time filtering approach that intercepts and evaluates data flowing into the agent during execution. Filters are applied to tool results, retrieved documents, and other external inputs before they enter the agent’s context, removing or flagging content that exhibits injection characteristics.

**Key contributions:** Test-time data filtering; pre-context injection detection; applied to all external data flows; lightweight runtime overhead.

# **Category 6: Formal Methods and Verification**

These papers provide mathematical foundations for reasoning about agent security, enabling provable guarantees about information flow, integrity, and confidentiality in agentic systems. This category represents the most rigorous but also the most nascent defense paradigm.

**Securing AI Agents with Information-Flow Control**

*arXiv: 2505.23643 | Costa, Köpf, Kolluri, Paverd, Russinovich, Salem, Tople, Wutschitz, Zanella-Béguelin (Microsoft Research)*

Applies information-flow control (IFC) to provide formal security guarantees for AI agents. Presents a formal model of the agent loop decomposed into planning and execution components, with security labels on data tracking its provenance (trusted vs. untrusted). Defines integrity and confidentiality properties and proves that properly labeled agents satisfy noninterference—untrusted data cannot influence trusted control decisions. The formalization covers the full agent lifecycle including tool calls and their side effects through a global datastore model.

**Key contributions:** First comprehensive IFC formalization for AI agents; planning/execution decomposition; noninterference proofs for integrity and confidentiality; datastore model for tool side effects; directly formalizes CaMeL-style defenses.

**The LLMbda Calculus: AI Agents, Conversations, and Information Flow**

*arXiv: 2602.20064 | Garby, Gordon, Sands*

Introduces a formal calculus (pronounced “L-L-Em-da”) for reasoning about AI agent security. Extends the untyped lambda calculus with dynamic information-flow control and primitives for LLM interaction (the @ operator for prompt-response generation). Provides the first formal semantics for prompt-response conversations, enabling rigorous reasoning about defenses including quarantined sub-conversations, code isolation, and information-flow restrictions. Proves a termination-insensitive noninterference theorem establishing integrity and confidentiality guarantees.

**Key contributions:** Formal calculus for agentic systems; @ operator for LLM invocation; dynamic information-flow control; noninterference theorem; formalizes CaMeL and Dual LLM pattern; models prompt injection as information flow violation.

**DRIFT: Dynamic Rule-Based Isolation for LLM Agent Security**

*arXiv: 2506.12104 | Multiple authors*

Applies dynamic isolation rules derived from formal specifications to partition agent execution contexts. Rules define boundaries between trusted and untrusted execution environments and are enforced at runtime, creating formally-grounded dynamic sandboxes for agent operations.

**Key contributions:** Formally-grounded dynamic sandboxing; runtime isolation rule enforcement; bridges formal methods and practical deployment.

# **Category 7: Benchmarks and Evaluation**

These papers provide evaluation infrastructure for measuring the effectiveness of agent security defenses.

**PromptShield: Deployable Detection Benchmark for Prompt Injection**

*arXiv: 2501.15145 | Multiple authors*

A benchmark for evaluating deployable prompt injection detection systems. Provides standardized test cases across injection types, attack sophistication levels, and application contexts. Enables apples-to-apples comparison of detection approaches.

**Key contributions:** Standardized prompt injection detection benchmark; multi-sophistication test cases; deployable system evaluation.

**ToolSafe: Enhancing Tool Invocation Safety via Proactive Step-Level Guardrail and Feedback**

*arXiv: 2601.10156 | Multiple authors*

Evaluates and enhances the safety of tool invocations in LLM agents through proactive step-level guardrails. Provides both a benchmark for measuring tool safety and a defense mechanism that operates at each step of tool invocation, offering feedback to the agent when potentially unsafe tool calls are detected.

**Key contributions:** Tool invocation safety benchmark; step-level guardrail evaluation; proactive safety feedback to agents during execution.

**Task Shield: Enforcing Task Alignment to Defend Against Indirect Prompt Injection**

*arXiv: 2412.16682 | Multiple authors*

Enforces task alignment by verifying that agent actions remain consistent with the original user task. Detects when indirect prompt injection causes task drift—the agent begins pursuing goals injected through untrusted data rather than the user’s original intent. Serves both as a defense and as an evaluation framework for measuring task alignment under adversarial conditions.

**Key contributions:** Task alignment enforcement; task drift detection; evaluation framework for measuring alignment under attack; defends against goal hijacking.

# **Defense-in-Depth: Composing Defenses**

No single defense category is sufficient to secure AI agents against the full spectrum of attacks. The research literature converges on a defense-in-depth strategy combining multiple layers.

## **Recommended Defense Stack**

Based on the surveyed research, a comprehensive defense posture combines five layers:

**Layer 1 – Architecture (CaMeL, Type-Directed Separation):** Separate trusted planning from untrusted data processing. This is the foundational layer providing the strongest guarantees. The P-LLM/Q-LLM split with capability tracking prevents the majority of prompt injection attacks by design.

**Layer 2 – Access Control (Progent, SEAgent, AgentBound):** Enforce least-privilege on tool access. Even if an attacker compromises the agent’s reasoning, access control limits what actions can be taken. Policy DSLs enable fine-grained, context-aware restrictions.

**Layer 3 – Prompt Hardening (Signed-Prompt, Prompt Fencing, DRIP):** Cryptographic and representation-level protections that make it harder for injected content to be interpreted as instructions. These reduce the attack success rate even against sophisticated payloads.

**Layer 4 – Runtime Monitoring (ShieldAgent, LlamaFirewall, AgentSpec):** Guardrail systems that observe agent behavior in real-time and intervene when policy violations are detected. This catches attacks that bypass lower layers.

**Layer 5 – Detection and Verification (UniGuardian, AgentArmor, VIGIL):** Detection systems that analyze action traces and verify actions before commitment. Provides logging and forensic capabilities alongside active defense.

## **Formal Foundations**

The IFC and LLMbda Calculus papers provide the mathematical foundations needed to reason about whether a composed defense stack actually achieves its security goals. The noninterference theorems established in these works can be used to verify that properly-implemented architectural defenses prevent untrusted data from influencing trusted decisions, giving defenders confidence beyond empirical testing alone.

# **Research Gaps and Open Problems**

## **Identified Gaps**

**Multi-Agent Security:** While SEAgent identifies the confused deputy problem in multi-agent systems, the broader challenge of securing networks of interacting agents remains under-explored. Trust boundary management across agent delegation chains is an open problem.

**Side-Channel Attacks:** Most defenses focus on direct data flow but neglect side channels: timing, token count, response structure, and other observable properties that can leak information. The Operationalizing CaMeL paper flags this explicitly.

**Performance and Usability:** Dual-LLM architectures double inference costs. Enterprise adoption requires solutions that balance security with latency and cost constraints. Plan-template caching and batched validation are promising but unproven at scale.

**Memory and State Attacks:** Agents with persistent memory introduce attack vectors through poisoned memory entries that influence future sessions. This temporal persistence threat is not addressed by most current defenses.

**Adaptive Adversaries:** Most evaluations use static attack sets. Defense robustness against adaptive adversaries who modify their approach based on observed defenses is understudied.

**Standardization:** The absence of standardized security interfaces for agent frameworks means each defense is implemented bespoke. MCP is emerging as a standard for tool integration, but no equivalent exists for security policy enforcement.

**Formal Verification at Scale:** The formal methods papers prove properties for simplified agent models. Scaling these proofs to real-world agents with hundreds of tools and complex interaction patterns remains a challenge.

# **Conclusions**

The AI agent security research landscape has matured rapidly from 2024 to 2026, moving from problem identification to concrete defense mechanisms. The field is converging on several key principles: that prompt injection must be addressed architecturally rather than through model robustness alone; that traditional security concepts like access control, information flow control, and formal verification are directly applicable to agent systems; and that defense-in-depth is essential because no single mechanism is sufficient.

The CaMeL architecture from Google DeepMind represents the current state-of-the-art in architectural defense, with formal methods papers from Microsoft Research and academic groups providing the mathematical foundations. Open-source frameworks like LlamaFirewall and community-driven tools like AgentBound for MCP security are making these defenses more accessible. The research trajectory suggests that within the next one to two years, production agent frameworks will incorporate multi-layered security as a standard feature rather than an afterthought.

For practitioners building agent systems today, the recommended approach is to implement as many defense layers as performance constraints allow, starting with architectural separation (Layer 1\) and access control (Layer 2\) as non-negotiable foundations, then adding prompt hardening, runtime monitoring, and detection capabilities based on the specific threat model.

# **Appendix: Complete Paper Index**

All 33 papers reviewed in this document, listed by arXiv identifier.

| arXiv ID | Title | Primary Category |
| :---- | :---- | :---- |
| 2503.18813 | CaMeL: Defeating Prompt Injections by Design | Architectural |
| 2505.22852 | Operationalizing CaMeL | Architectural |
| 2509.25926 | Better Privilege Separation (Type-Directed) | Architectural |
| 2405.05175 | AirGapAgent | Architectural |
| 2506.08837 | Design Patterns for Securing LLM Agents | Architectural |
| 2503.15547 | Prompt Flow Integrity | Architectural |
| 2601.11893 | SEAgent (MAC Framework) | Access Control |
| 2509.22256 | CSAgent (Context-Aware AC) | Access Control |
| 2504.11703 | Progent (Programmable Privilege) | Access Control |
| 2510.21236 | AgentBound (MCP AC) | Access Control |
| 2504.21034 | SAGA (Governance Architecture) | Access Control |
| 2503.23250 | Encrypted Prompt | Access Control |
| 2410.21492 | FATH (Authentication) | Access Control |
| 2503.22738 | ShieldAgent | Runtime Monitoring |
| 2503.18666 | AgentSpec | Runtime Monitoring |
| 2601.05755 | VIGIL | Runtime Monitoring |
| 2508.10991 | MCP-Guard | Runtime Monitoring |
| 2505.03574 | LlamaFirewall | Runtime Monitoring |
| 2401.07612 | Signed-Prompt | Prompt-Level |
| 2511.19727 | Prompt Fencing | Prompt-Level |
| 2510.08829 | CommandSans | Prompt-Level |
| 2403.04960 | Spotlighting | Prompt-Level |
| 2511.00447 | DRIP | Prompt-Level |
| 2601.04795 | Tool Result Parsing Defense | Prompt-Level |
| 2502.13141 | UniGuardian | Detection |
| 2508.01249 | AgentArmor | Detection |
| 2508.15310 | IPIGuard | Detection |
| 2510.19207 | DataFilter | Detection |
| 2505.23643 | IFC for AI Agents | Formal Methods |
| 2602.20064 | LLMbda Calculus | Formal Methods |
| 2506.12104 | DRIFT | Formal Methods |
| 2501.15145 | PromptShield | Benchmarks |
| 2601.10156 | ToolSafe | Benchmarks |
| 2412.16682 | Task Shield | Benchmarks |

