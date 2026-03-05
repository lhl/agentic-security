https://claude.ai/chat/3e4ccc67-3e69-43b6-accd-119aaf7201b8

# CaMeL: Defeating Prompt Injections by Design — Comprehensive Review

**Paper:** Debenedetti, E., Shumailov, I., Fan, T., Hayes, J., Carlini, N., Fabian, D., Kern, C., Shi, C., Terzis, A., & Tramèr, F. (2025). *Defeating Prompt Injections by Design.* arXiv:2503.18813. Google DeepMind / ETH Zurich.

**Commentary:** Willison, S. (2025). *CaMeL offers a promising new direction for mitigating prompt injection attacks.* simonwillison.net, April 11, 2025.

---

## 1. Executive Summary

CaMeL (CApabilities for MachinE Learning) is the first prompt injection defense that claims **strong security guarantees** without modifying the underlying LLM. Rather than training models to resist injection or layering probabilistic AI detectors, CaMeL applies classical software security principles — control flow integrity, capability-based access control, and information flow control — as an architectural wrapper around untrusted LLM components.

The core insight: treat the LLM as an inherently untrusted component (like user input in web security) and enforce security at the system design level. This is a paradigm shift from the dominant approach of trying to make models themselves robust.

## 2. Architecture

CaMeL extends Simon Willison's 2023 Dual LLM pattern with four components operating in concert:

### 2.1 Privileged LLM (P-LLM)
- Sees **only** the trusted user query, never raw tool outputs or untrusted data
- Generates a plan as restricted Python code (leveraging LLMs' strong Python capabilities)
- Acts as the planner/orchestrator — analogous to a project manager who never touches raw materials

### 2.2 Quarantined LLM (Q-LLM)
- Processes untrusted data (emails, documents, web content) with **no tool access**
- Extracts structured data from unstructured inputs via constrained output schemas (Pydantic BaseModel)
- Can signal insufficient information via a `have_enough_information` boolean field, but **cannot communicate back to the P-LLM what information it needs** (preventing injection via error messages)
- Can be a smaller/cheaper/local model — enabling a privacy architecture where sensitive data never leaves the user's device

### 2.3 Custom Python Interpreter
- Executes the P-LLM's plan while maintaining a **data flow graph** tracking provenance of every variable
- Propagates capabilities (metadata tags) through operations: if `c = a + b`, then `c` inherits the capabilities of both `a` and `b`
- Two modes: **NORMAL** (tracks direct dependencies) and **STRICT** (adds control flow dependencies — variables assigned inside if/for blocks depend on the conditional/iterable)
- STRICT mode blocks side-channel attacks where private data leaks through loop iteration counts or conditional branching

### 2.4 Security Policies
- Expressed as Python functions (not a custom DSL — enabling arbitrary logic)
- Evaluated before each tool call, checking capabilities of the arguments
- Example: `send_email` policy requires the `recipient` parameter to be trusted (from user input or a known-safe source); untrusted recipients trigger user confirmation
- Can be per-tool, per-data-type, or global

### Capability System
Capabilities are metadata tags on every value, tracking:
- **Provenance:** Where the data came from (User literal, specific tool, CaMeL transformation)
- **Readers:** Who is authorized to see this data (specific email addresses, Public, etc.)

Inspired by: libcap (POSIX capabilities), Capsicum (FreeBSD capability mode), CHERI (hardware capability architecture).

## 3. What CaMeL Fixes Over Dual LLM

Willison's original Dual LLM pattern (April 2023) protects the **control flow** — the attacker can't make the agent call different tools or change the sequence of operations. But CaMeL identifies a residual vulnerability: the **data flow** can still be manipulated.

The attack scenario: user asks to "send Bob the document from our meeting notes." The P-LLM correctly plans: find notes → extract email → extract doc name → fetch doc → send email. But the notes contain a prompt injection targeting the Q-LLM, causing it to return the attacker's email address instead of Bob's. The tool sequence is correct; the arguments are poisoned.

CaMeL's capability system catches this: the email address extracted by the Q-LLM from meeting notes is tagged as originating from an untrusted source. When the `send_email` tool is called, the security policy checks if the recipient is trusted. It isn't (it came from the Q-LLM processing untrusted notes), so execution is blocked and the user is prompted for confirmation.

## 4. Results (AgentDojo Benchmark)

### Utility
- CaMeL achieves **77%** task completion with provable security vs. **84%** for an undefended system (v2, with newer models like Claude 4 Sonnet, Gemini 2.5 Pro, o3)
- The utility gap is narrowing as models improve: Claude went from 25% → 55% → 75% utility on the Travel suite across model generations, with zero changes to CaMeL
- Using a cheaper Q-LLM (e.g., Claude 3.5 Haiku with Claude 4 Sonnet as P-LLM) causes only ~1% utility drop for ~12% cost reduction

### Security
- **0 successful prompt injection attacks** across all models when policies are enforced
- The only "successful" attacks in AgentDojo are explicitly outside CaMeL's threat model (text-to-text attacks with no data flow impact, and one case where raw reviews are printed — not a prompt injection)
- Contrast: Claude 3.5 Sonnet with native tool calling is vulnerable to 300+ attacks; GPT-4o Mini with instruction hierarchy defense: 276 attacks

### Overhead
- 2.82× more input tokens, 2.73× more output tokens (median task) — a reasonable cost for provable security
- Expected to decrease as models improve at following the restricted Python dialect

## 5. Acknowledged Limitations

### 5.1 Side Channels
The paper is refreshingly honest about three classes of side-channel attacks:

1. **Indirect inference via external resources:** A loop `for i in range(private_variable)` leaks the variable's value through the number of HTTP requests an attacker's server observes. STRICT mode mitigates this by adding the loop iterable as a dependency of all statements inside the loop.

2. **Exception-based bit leaking:** The Q-LLM can be injected to throw an exception conditional on private data. Whether execution continues (and reaches an attacker-observable tool call) reveals one bit. Mitigated by STRICT mode's dependency propagation.

3. **Timing side channels:** Time-dependent operations could theoretically leak private data. CaMeL's interpreter doesn't expose the `time` module, but other timing channels may exist.

The paper draws an explicit analogy to CFI vs. ROP attacks in traditional security — CaMeL represents CFI-level protection, and ROP-style attacks (chaining individually-allowed operations into a malicious sequence) may emerge.

### 5.2 User Fatigue / Policy Burden
- Users must define and maintain security policies
- Frequent confirmation prompts risk "click-yes-to-everything" desensitization
- AWS IAM-level policy complexity is a real concern (as Willison notes: "I have enough trouble thinking through those myself")

### 5.3 Ecosystem Adoption
- Capability-based systems require participation from the entire tool ecosystem
- Third-party tools that don't support capabilities degrade the security model
- CHERI hardware capabilities are a cautionary tale — adoption required redesigning the full software-hardware stack

### 5.4 Data-Requires-Action Problem
- When actions depend on untrusted data content (e.g., "do whatever the email says"), CaMeL fundamentally cannot help — this is inherent to the Dual LLM pattern
- Potential mitigation: nested P-LLM instances with strict policies

### 5.5 Text-to-Text Attacks
- CaMeL cannot prevent an injected prompt from causing the Q-LLM to produce a misleading summary, as long as the summary doesn't affect the data flow
- However, CaMeL's data flow graph can annotate the UI with provenance information to help users identify untrusted content

## 6. Willison's Key Observations

Willison's commentary is valuable not just as accessible explanation but for several analytical contributions:

1. **"99% is a failing grade"** — The fundamental argument for architectural (deterministic) over probabilistic (AI-based) defenses. SQL injection and XSS would be catastrophic if defenses failed 1% of the time. The same standard should apply to prompt injection.

2. **Privacy architecture** — The P-LLM/Q-LLM split enables a deployment where the cloud-hosted P-LLM (which needs to be powerful) never sees private data, while the Q-LLM (which can be weaker) runs locally on the user's device.

3. **Honest self-assessment** — Willison highlights that CaMeL's own section 8.3 is titled "So, are prompt injections solved now?" with the answer "No." This intellectual honesty from security researchers is noted as a positive signal.

4. **The real challenge is UX** — Willison's hope is for "robustly selected defaults with a clear user interface design" — the gap between CaMeL's security engineering and a shippable product.

## 7. Historical Context: The Prompt Injection Problem Space

CaMeL sits at a pivotal moment in a timeline that has seen essentially zero progress on robust defenses since the problem was identified:

- **September 2022:** Willison coins "prompt injection" by analogy to SQL injection
- **2022–2024:** All proposed defenses are probabilistic (training-based, detection-based, prompting-based) and provide no guarantees
- **April 2023:** Willison proposes the Dual LLM pattern — the first architectural approach, but theoretical
- **March 2025:** CaMeL paper — first concrete implementation of architectural defense with provable guarantees
- **October 2025:** "The Attacker Moves Second" (Nasr et al.) demonstrates that 12 published probabilistic defenses are bypassed at >90% ASR by adaptive attacks, reinforcing CaMeL's architectural philosophy
- **February 2026:** Ten months after CaMeL, real-world adoption remains limited (NeuralTrust analysis)

---

## 8. Annotated Reference List: Essential Prior Work, Concurrent Work, and Follow-ups

### 8.1 Foundational: The Prompt Injection Problem

| Ref | Notes |
|-----|-------|
| **Goodside, R. (2022).** *Exploiting GPT-3 prompts with malicious inputs.* | First public demonstration of prompt injection |
| **Perez, F. & Ribeiro, I. (2022).** *Ignore previous prompt: Attack techniques for language models.* arXiv:2211.09527 | First systematic taxonomy of prompt injection attack techniques |
| **Greshake, K. et al. (2023).** *Not What You've Signed Up For: Compromising Real-World LLM-Integrated Applications with Indirect Prompt Injection.* ACM AISec Workshop | Seminal paper on **indirect** prompt injection — attacks via third-party content (emails, web pages) rather than direct user input. Foundational threat model for CaMeL |
| **Willison, S. (2023).** *The Dual LLM pattern for building AI assistants that can resist prompt injection.* simonwillison.net | Theoretical proposal for P-LLM/Q-LLM isolation. Direct precursor to CaMeL — the paper explicitly builds on and extends this |
| **Willison, S. (2022).** *You can't solve AI security problems with more AI.* simonwillison.net | Argument that probabilistic AI-based defenses are fundamentally insufficient for security (99% ≠ 100%). Core philosophical motivation for CaMeL's deterministic approach |
| **Pasquini, D., Strohmeier, M., & Troncoso, C. (2024).** *Neural Exec: Learning (and Learning from) Execution Triggers for Prompt Injection Attacks.* arXiv:2403.03792 | Advanced prompt injection attacks that learn optimal triggers — demonstrates the arms race that architectural defenses like CaMeL aim to sidestep |
| **Rehberger, J. (2024).** *Embrace The Red Blog.* | Extensive practical demonstrations of prompt injection in production systems (Bing Chat, Copilot, etc.) |

### 8.2 Foundational: Software Security Concepts Applied

| Ref | Notes |
|-----|-------|
| **Abadi, M. et al. (2009).** *Control-flow integrity principles, implementations, and applications.* ACM TISSEC | CFI: ensures program execution follows a pre-defined control flow graph. Direct inspiration for CaMeL's control flow extraction |
| **Denning, D.E. & Denning, P.J. (1977).** *Certification of programs for secure information flow.* CACM | Foundational information flow control theory. CaMeL's data flow tracking and capability propagation are a modern instantiation |
| **Denning, D.E. (1976).** *A lattice model of secure information flow.* CACM | Formal lattice model for information flow security — the theoretical basis for CaMeL's capability hierarchy |
| **Myers, A.C. & Liskov, B. (1997).** *A decentralized model for information flow control.* SOSP | Decentralized labels for tracking information flow — ancestor of CaMeL's per-value capability tags |
| **Watson, R.N.M. et al. (2010).** *Capsicum: Practical Capabilities for UNIX.* USENIX Security | Capability mode for FreeBSD — practical OS-level capability system. CaMeL's capability design draws from this |
| **Watson, R.N.M. et al. (2015).** *CHERI: A hybrid capability-system architecture for scalable software compartmentalization.* IEEE S&P | Hardware capability architecture. CaMeL cites CHERI's adoption challenges (full stack redesign required) as a cautionary parallel |
| **Woodruff, J. et al. (2014).** *The CHERI capability model: Revisiting RISC in an age of risk.* ACM SIGARCH | CHERI capability model — hardware-enforced memory safety via capabilities |
| **Anderson, R.J. (2010).** *Security Engineering* (2nd ed.) | Comprehensive security engineering textbook; CaMeL's access control and policy framework draws from Chapter 6 |
| **Anderson, R., Stajano, F., & Lee, J.H. (2002).** *Security policies.* Advances in Computers | Formal definition of security policies. CaMeL's policy language and de-classification challenges reference this directly |
| **Carlini, N. & Wagner, D. (2014).** *ROP is still dangerous: Breaking modern defenses.* USENIX Security | Return-oriented programming bypasses CFI. CaMeL paper explicitly draws the analogy: ROP-style attacks may eventually emerge against CaMeL's control flow protection |
| **Sabelfeld, A. & Myers, A.C. (2003).** *Language-based information-flow security.* IEEE JSAC | Survey of language-level IFC mechanisms. Theoretical grounding for CaMeL's interpreter-level enforcement |
| **Aleph One (1996).** *Smashing The Stack For Fun And Profit.* Phrack | Classic buffer overflow paper. CaMeL draws the parallel between buffer overflows violating control flow and prompt injections corrupting LLM execution |
| **Shacham, H. (2007).** *The geometry of innocent flesh on the bone: return-into-libc without function calls.* ACM CCS | Original ROP paper. CaMeL warns that analogous "gadget-chaining" attacks may target their system |

### 8.3 Heuristic/Probabilistic Defenses (That CaMeL Outperforms)

| Ref | Notes |
|-----|-------|
| **Hines, K. et al. (2024).** *Defending Against Indirect Prompt Injection with Spotlighting.* arXiv:2403.14720 | Delimiting untrusted content with special characters. CaMeL benchmarks against this — it uses 1.06× input tokens but provides zero security guarantees |
| **Learn Prompting (2024).** *Sandwich Defense / Prompt Sandwiching.* | Repeating original task instructions after each tool output. Evaluated in AgentDojo — significantly less effective than CaMeL |
| **Wallace, E. et al. (2024).** *The instruction hierarchy: Training LLMs to prioritize privileged instructions.* arXiv:2404.13208 | OpenAI's instruction hierarchy (deployed in GPT-4o Mini). CaMeL paper shows GPT-4o Mini with instruction hierarchy still fails 276 attacks in AgentDojo vs. 0 with CaMeL |
| **Chen, S. et al. (2024).** *StruQ: Defending against prompt injection with structured queries.* arXiv:2402.06363 | Training models to accept structured queries. Training-based approach that CaMeL's architectural approach supersedes |
| **Wu, F., Cecchetti, E., & Xiao, C. (2024).** *System-Level Defense against Indirect Prompt Injection Attacks: An Information Flow Control Perspective.* arXiv:2409.19091 | Closest precursor to CaMeL's IFC approach. Uses IFC to track trusted/untrusted data but with coarser granularity than CaMeL's per-value capabilities |
| **ProtectAI (2024).** *Fine-Tuned DeBERTa-v3-base for Prompt Injection Detection.* | BERT-based prompt injection detector. "The Attacker Moves Second" showed >90% bypass rate with adaptive attacks |
| **Sharma, R.K., Gupta, V., & Grossman, D. (2024).** *SPML: A DSL for Defending Language Models Against Prompt Attacks.* arXiv:2402.11755 | Formal language for defining model tasks and detecting deviations. DSL-based approach that CaMeL's Python-based policies generalize |
| **Wu, T. et al. (2024).** *Instructional Segment Embedding: Improving LLM Safety with Instruction Hierarchy.* arXiv:2410.09102 | Embedding-level instruction hierarchy. Training-based approach — no guarantees against adaptive attacks |

### 8.4 Benchmarks and Evaluation

| Ref | Notes |
|-----|-------|
| **Debenedetti, E. et al. (2024b).** *AgentDojo: A Dynamic Environment to Evaluate Attacks and Defenses for LLM Agents.* NeurIPS 2024 Datasets & Benchmarks | The primary evaluation benchmark for CaMeL. By the same first author. Realistic agentic security tasks across Workspace, Banking, Travel, and Slack domains |
| **Debenedetti, E. et al. (2024a).** *Dataset and Lessons Learned from the 2024 SaTML LLM Capture-the-Flag Competition.* NeurIPS 2024 | Practical prompt injection competition — empirical evidence of the difficulty of defending against adaptive human attackers |
| **US-AISI (2025).** *Technical Blog: Strengthening AI Agent Hijacking Evaluations.* | US AI Safety Institute showing that Claude 3.5 Sonnet's robustness drops drastically under adaptive prompts — supporting CaMeL's argument that model-level robustness is insufficient |

### 8.5 Concurrent and Follow-up Work (Post-CaMeL)

| Ref | Notes |
|-----|-------|
| **Nasr, M. et al. (2025).** *The Attacker Moves Second: Stronger Adaptive Attacks Bypass Defenses Against LLM Jailbreaks and Prompt Injections.* arXiv:2510.09023 | **Critical validation of CaMeL's thesis.** Joint OpenAI/Anthropic/DeepMind team (including several CaMeL co-authors) bypasses 12 published defenses at >90% ASR. Strongly reinforces that probabilistic defenses are insufficient and architectural approaches like CaMeL are necessary. Note: several authors overlap with the CaMeL paper |
| **Shi, T. et al. (2025).** *Progent: Programmable Privilege Control for LLM Agents.* arXiv:2504.11703 | Concurrent work using a JSON-based DSL (vs. CaMeL's Python) for policy enforcement. Claims 0% ASR on AgentDojo. Key difference: Progent uses LLMs to auto-generate policies (addressing CaMeL's policy burden limitation), but this introduces a probabilistic element. CaMeL cites this as a potential integration path for policy automation |
| **Costa, M. et al. (2025).** *Securing AI Agents with Information-Flow Control.* arXiv:2505.23643 | Microsoft Research paper on IFC for AI agents. Part of the same intellectual lineage as CaMeL |
| **Kim, J., Choi, W., & Lee, B. (2025).** *Prompt flow integrity to prevent privilege escalation in LLM agents.* arXiv:2503.15547 | Applies program analysis techniques to prevent privilege escalation in LLM agents |
| **Li, E. et al. (2025).** *ACE: A Security Architecture for LLM-Integrated App Systems.* arXiv:2504.20984 | Security architecture for LLM-integrated applications |
| **Wu, Y. et al. (2025).** *IsolateGPT: An Execution Isolation Architecture for LLM-Based Agentic Systems.* NDSS | Isolation-based defense similar to Dual LLM, requiring explicit user approval for cross-tool data sharing. Prone to user fatigue (as CaMeL's capability system aims to reduce) |
| **Zhong, P.Y. et al. (2025).** *RTBAS: Defending LLM Agents Against Prompt Injection and Privacy Leakage.* arXiv:2502.08966 | Uses integrity/confidentiality labels but with coarser granularity (only private/public, trusted/untrusted) and classifier-based dependency detection (vs. CaMeL's explicit tracking) |
| **Abdelnabi, S. et al. (2025).** *Firewalls to Secure Dynamic LLM Agentic Networks.* arXiv:2502.01822 | Firewall approach for agent-to-agent communications |
| **Zverev, E. et al. (2025).** *ASIDE: Architectural Separation of Instructions and Data in Language Models.* arXiv:2503.10566 | Architectural-level separation using different input embeddings for instructions vs. data. Complementary approach that could be combined with CaMeL |
| **Bagdasaryan, E. et al. (2024).** *Air Gap: Protecting Privacy-Conscious Conversational Agents.* arXiv:2405.05175 | Contextual integrity framework for privacy. CaMeL suggests integration with AirGap for automated policy derivation |
| **Ghalebikesabi, S. et al. (2024).** *Operationalizing contextual integrity in privacy-conscious assistants.* arXiv:2408.02373 | Contextual integrity for LLM assistants — potential complement to CaMeL's capability system |
| **Nestaas, F., Debenedetti, E., & Tramèr, F. (2025).** *Adversarial Search Engine Optimization for Large Language Models.* ICLR 2025 | Demonstrates that adversaries can manipulate which tools agents choose via SEO-style attacks. Relevant to CaMeL's Scenario 2 (spy tool) |
| **Schneier, B. & Raghavan, B. (2026).** *Why AI Keeps Falling for Prompt Injection Attacks.* IEEE Spectrum | High-level analysis of the fundamental architectural reasons prompt injection persists |
| **NCSC UK (2025).** *Formal assessment characterising LLMs as "inherently confusable deputies."* | UK's National Cyber Security Centre formally declares LLMs are "inherently confusable deputies" — institutional validation of the premise underlying CaMeL |
| **Abdelnabi, S. et al. (2024).** *Are you still on track!? Catching LLM Task Drift with Activations.* arXiv:2406.00799 | Internal activation monitoring to detect task drift. Probabilistic approach that CaMeL's deterministic tracking supersedes |

### 8.6 Willison's Broader Prompt Injection Series (Context)

| Post | Notes |
|------|-------|
| **MCP has prompt injection security problems** (Apr 9, 2025) | Published 2 days before the CaMeL commentary. MCP's tool-use paradigm amplifies the attack surface CaMeL addresses |
| **Design Patterns for Securing LLM Agents against Prompt Injections** (Jun 13, 2025) | Follow-up synthesis of design patterns emerging from CaMeL and related work |
| **An Introduction to Google's Approach to AI Agent Security** (Jun 15, 2025) | Coverage of Google's broader agent security strategy, of which CaMeL is a component |
| **The lethal trifecta for AI agents** (Jun 16, 2025) | Willison's framework: private data + untrusted content + external communication = vulnerability. CaMeL addresses exactly this trifecta |
| **New prompt injection papers: Agents Rule of Two and The Attacker Moves Second** (Nov 2, 2025) | Coverage of Meta's "Rule of Two" heuristic and the Nasr et al. adaptive attacks paper. Notes that the adaptive attacks paper reinforces CaMeL's architectural philosophy |

### 8.7 Agentic Systems Background

| Ref | Notes |
|-----|-------|
| **Schick, T. et al. (2023).** *ToolFormer: Language Models Can Teach Themselves to Use Tools.* NeurIPS | Foundational tool-use paper — the paradigm CaMeL aims to secure |
| **Yao, S. et al. (2022).** *ReAct: Synergizing reasoning and acting in language models.* arXiv:2210.03629 | ReAct framework — the reasoning-then-acting loop that CaMeL's P-LLM plan generation extends |
| **Gao, L. et al. (2023).** *PAL: Program-aided language models.* ICML | Program-aided LMs — generating code to solve tasks. CaMeL's P-LLM generating Python plans is directly in this lineage |
| **Carlini, N. et al. (2023).** *Are aligned neural networks adversarially aligned?* NeurIPS | Shows alignment training doesn't provide adversarial robustness — further motivation for architectural defenses |

---

## 9. Assessment

### What Makes CaMeL Important

1. **Paradigm shift:** From "make the model robust" to "make the system robust around an untrusted model." This is the SQL parameterized query equivalent for LLMs — you don't try to sanitize input, you change the architecture so injection is structurally impossible for the protected threat model.

2. **Provable guarantees:** CaMeL is the first defense to claim provable security properties (within its threat model), not just empirical robustness against a benchmark.

3. **Honest threat modeling:** The paper explicitly defines what it does and doesn't protect against, acknowledges side channels, and draws parallels to known limitations in traditional security (CFI vs. ROP).

4. **Practical overhead:** ~3× token cost with narrowing utility gap is far more deployable than many proposed defenses.

### Open Questions

1. **Policy authoring at scale:** Who writes the policies for a general-purpose agent? CaMeL acknowledges this but doesn't solve it. Progent's LLM-generated policies are one path, but re-introduce a probabilistic element.

2. **Ecosystem buy-in:** Every tool needs to emit proper capability metadata. This is the CHERI adoption problem all over again.

3. **The data-requires-action gap:** When the user's intent is "do what the email says," no amount of control/data flow separation helps. This covers a non-trivial fraction of real-world agent use cases.

4. **ROP-style composition attacks:** The paper flags but doesn't fully address the risk of chaining individually-allowed operations (each passing policy checks) into a malicious composite action.

5. **Real-world adoption:** As of early 2026 (~10 months post-publication), production adoption remains limited. The gap between academic demonstration and shippable product is significant.

### Bottom Line

CaMeL is the most important contribution to prompt injection defense since the problem was identified. It doesn't solve prompt injection completely — and is honest about that — but it establishes the correct paradigm: deterministic, architectural security guarantees rather than probabilistic model-level robustness. The concurrent "Attacker Moves Second" paper (from an overlapping author team) serves as the devastating empirical counterpart, proving that every probabilistic defense tested can be bypassed at >90% by adaptive attackers.

The practical question is whether the industry will adopt this architectural complexity or continue shipping agents with probabilistic "good enough" defenses until a sufficiently embarrassing breach forces the issue.
