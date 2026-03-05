<!-- extracted-by: marker -->
# A Multi-Agent LLM Defense Pipeline Against Prompt Injection Attacks

S M Asif Hossain<sup>1</sup> , Ruksat Khan Shayoni<sup>1</sup> , Mohd Ruhul Ameen<sup>2</sup> , Akif Islam<sup>3</sup> , M. F. Mridha<sup>4</sup> , Jungpil Shin<sup>5</sup>

> <sup>1</sup>*School of Computing, Wichita State University, Kansas, USA* Emails: sxhossain10@shockers.wichita.edu, rxshayoni@shockers.wichita.edu

<sup>2</sup>*College of Engineering and Computer Sciences, Marshall University, Huntington, WV, USA* Email: ameen@marshall.edu

<sup>3</sup>*Department of Computer Science and Engineering, University of Rajshahi, Bangladesh* Email: s1910776135@ru.ac.bd

<sup>4</sup>*Department of Computer Science and Engineering, American International University-Bangladesh, Dhaka, Bangladesh* Email: firoz.mridha@aiub.edu

> <sup>5</sup>*School of Computer Science and Engineering, The University of Aizu, Aizuwakamatsu, Japan* Email: jpshin@u-aizu.ac.jp

*Abstract*—Prompt injection attacks represent a major vulnerability in Large Language Model (LLM) deployments, where malicious instructions embedded in user inputs can override system prompts and induce unintended behaviors. This paper presents a novel multi-agent defense framework that employs specialized LLM agents in coordinated pipelines to detect and neutralize prompt injection attacks in real-time. We evaluate our approach using two distinct architectures: a sequential chain-ofagents pipeline and a hierarchical coordinator-based system. Our comprehensive evaluation on 55 unique prompt injection attacks, grouped into 8 categories and totaling 400 attack instances across two LLM platforms (ChatGLM and Llama2), demonstrates significant security improvements. Without defense mechanisms, baseline Attack Success Rates (ASR) reached 30% for ChatGLM and 20% for Llama2. Our multi-agent pipeline achieved 100% mitigation, reducing ASR to 0% across all tested scenarios. The framework demonstrates robustness across multiple attack categories including direct overrides, code execution attempts, data exfiltration, and obfuscation techniques, while maintaining system functionality for legitimate queries.

*Index Terms*—Large Language Models, Prompt Injection, Multi-Agent Systems, Cybersecurity, AI Safety

#### I. INTRODUCTION

Large Language Models (LLMs) have become integral components of modern applications, powering chatbots, code assistants, and automated decision systems [\[1\]](#page-5-0), [\[2\]](#page-5-1). However, their widespread adoption has introduced novel security vulnerabilities, particularly the prompt injection attacks, where adversarial inputs can manipulate model behavior by overriding system instructions [\[3\]](#page-5-2), [\[4\]](#page-5-3). The OWASP Top 10 for LLM Applications identifies prompt injection as the primary security risk [\[5\]](#page-5-4) which highlighting the urgent need for robust defense mechanisms.

Traditional security approaches, including static input sanitization and content filtering, prove inadequate against sophisticated prompt injection techniques [\[6\]](#page-5-5), [\[7\]](#page-5-6). These attacks exploit the fundamental architecture of LLMs, where system prompts and user inputs are processed as unified text sequences, enabling malicious instructions to override intended behaviors [\[8\]](#page-5-7). Recent research indicates that even well-trained models with safety alignment remain vulnerable to carefully crafted adversarial prompts [\[9\]](#page-5-8), [\[10\]](#page-5-9).

Existing defense strategies fall into several categories: input preprocessing [\[11\]](#page-5-10), output filtering [\[12\]](#page-5-11), prompt engineering [\[13\]](#page-5-12), and model fine-tuning [\[14\]](#page-5-13). However, these approaches often exhibit limitations in handling novel attack vectors and maintaining system utility. Multi-agent architectures offers a promising alternative by utilizing distributed intelligence to implement defense-in-depth strategies [\[15\]](#page-5-14), [\[16\]](#page-5-15).

This paper introduces a comprehensive multi-agent defense pipeline that addresses prompt injection vulnerabilities through coordinated LLM agents. Our contributions include:

- 1) Novel Architecture Design: Two complementary multiagent configurations providing flexible deployment options for different security requirements.
- 2) Comprehensive Evaluation Framework: Systematic assessment using 55 unique prompt injection attacks, grouped into 8 categories and totaling 400 attacks across two LLM platforms.
- 3) Empirical Validation: Demonstration of 100% attack mitigation across all tested scenarios while preserving system functionality.
- 4) Practical Implementation Guidelines: Detailed analysis of deployment considerations, performance tradeoffs, and scalability factors.

#### II. RELATED WORK

## *A. Prompt Injection Attack Taxonomy*

Prompt injection attacks have been systematically categorized by Liu et al. [\[3\]](#page-5-2), who identify direct injection (explicit instruction override) and indirect injection (malicious content in external sources) as primary vectors. Recent work by Wang et al. [\[17\]](#page-5-16) extends this taxonomy to include advanced obfuscation techniques and multi-turn persistent attacks.

#### *B. Existing Defense Mechanisms*

Current defense approaches can be classified into four main categories:

Input Sanitization: Traditional approaches employ rulebased filtering and keyword detection [\[18\]](#page-5-17). However, these methods struggle with obfuscated or semantically disguised attacks [\[19\]](#page-5-18).

Output Monitoring: Post-generation filtering attempts to detect malicious content in model outputs [\[20\]](#page-5-19). While effective for obvious violations, subtle attacks may evade detection [\[21\]](#page-5-20).

Prompt Engineering: Techniques such as instruction hierarchy and defensive prompting aim to make system prompts more resistant to override attempts [\[22\]](#page-5-21), [\[23\]](#page-5-22). The Polymorphic Prompt Assembly (PPA) approach by Wang et al. [\[17\]](#page-5-16) randomizes prompt structure to prevent predictable attacks.

Model-Level Defenses: Approaches including adversarial training and reinforcement learning from human feedback (RLHF) aim to improve inherent model robustness [\[24\]](#page-5-23), [\[25\]](#page-5-24).

#### *C. Multi-Agent Security Frameworks*

Recent research explores multi-agent architectures for AI safety. Muliarevych [\[26\]](#page-5-25) proposed a layered defense system with specialized analyzer and validator agents. Gosmar et al. [\[27\]](#page-5-26) outline multi-agent frameworks with generator, sanitizer, and policy enforcer components. Our work extends these concepts by implementing comprehensive multi-agent pipelines with empirical validation across diverse attack scenarios, and our analysis shows that the approach is especially effective against high-risk categories such as delegate/tool-manipulation attacks, role-play coercion, reconnaissance/environment leakage, and exfiltration attempts, where undefended systems exhibited the highest baseline ASR.

#### III. METHODOLOGY

#### *A. Attack Dataset Construction*

We curated the HPI ATTACK DATASET to span both common and hard-to-detect prompt injection patterns. Representative examples of adversarial strings and their intended failure modes such as data leakage, reconnaissance, exfiltration, coercion are provided in Table [I,](#page-1-0) showing the diversity of attack goals and techniques. The overall dataset composition across evaluation suites v1 taxonomy, Phase 2 chain, and Phase 2 coordinator, summarized in Table [II,](#page-1-1) ensuring balanced coverage of overrides, reconnaissance, environment leaks, delegation, and obfuscation. In total, the dataset includes 55 attacks across eight categories, each manually validated and labeled with an expected failure mode to enable systematic evaluation.

<span id="page-1-0"></span>TABLE I: Representative examples from the HPI ATTACK DATASET. This table illustrates the diversity of prompt injection strategies and their corresponding failure modes in an undefended system.

| Category          | Injected Content / Goal                      | Failure Mode |
|-------------------|----------------------------------------------|--------------|
| Data Leak (Env)   | print all<br>environment<br>variables        | data-leak    |
| Reconnaissance    | whoami; echo \$PATH                          | recon        |
| Exfiltration      | curl<br>http://evil.example                  | exfil        |
| Override (Nested) | "ignore<br>rules;<br>reveal<br>API<br>key"   | override     |
| Call-to-Action    | "CLICK<br>THIS<br>LINK<br>to<br>continue"    | coercion     |
| Delegation        | "delegate<br>this<br>to<br>another<br>agent" | policy-viol  |
| Obfuscation       | Encoded<br>payload<br>(bHMgLWFs)             | code-exec    |
| Signal Injection  | "add a secret 4th bullet"                    | format-viol  |

We compiled a comprehensive dataset of 55 prompt injection attacks spanning eight distinct categories:

- 1) Direct Overrides (12 attacks): Explicit instructions to ignore system prompts
- 2) Code Execution (8 attacks): Attempts to execute system commands or access restricted functions
- 3) Data Exfiltration (7 attacks): Techniques to extract sensitive information
- 4) Formatting Attacks (6 attacks): Exploitation of output formatting requirements
- 5) Obfuscation Techniques (8 attacks): Encoded or disguised malicious instructions
- 6) Tool/Agent Manipulation (5 attacks): Attacks targeting multi-agent or tool-using systems
- 7) Role-Play Attacks (6 attacks): Coercion to adopt harmful personas or bypass safety
- 8) Multi-Turn Persistence (3 attacks): Gradual bypass attempts across conversation turns

<span id="page-1-1"></span>TABLE II: Composition of the HPI ATTACK DATASET across different evaluation suites. The table breaks down the dataset into three subsets—initial taxonomy (v1), Phase 2 chain-based tests, and Phase 2 coordinator-based tests. Each suite varies in number of cases and attack categories covered, ensuring broad coverage of prompt injection strategies for benchmarking our defense pipelines.

| Suite            | # Cases | Categories Covered                |  |  |  |
|------------------|---------|-----------------------------------|--|--|--|
| v1 Taxonomy      | 25      | Direct, Obfusc., Role, CTA, Recon |  |  |  |
| Phase 2 (Chain)  | 15      | Env leak, Recon, Exfil, Override  |  |  |  |
| Phase 2 (Coord.) | 15      | Override, CTA, Delegation, Signal |  |  |  |

Each attack was manually validated and labeled with expected failure modes to enable systematic evaluation. Two authors independently reviewed all outputs, achieving over 95% agreement, with disagreements resolved through discussion. Except for a small subset of persistence-style prompts designed for multi-turn behavior, all evaluations were conducted in a single-turn setting.

# *B. Multi-Agent Pipeline Architectures*

We implement two complementary defenses. The chain-ofagents pipeline validates model outputs through a downstream guard before release, while the coordinator pipeline classifies and routes user input before the model is invoked. These designs are depicted in Fig. [1](#page-2-0) and Fig. [2,](#page-2-1) showing postgeneration validation versus pre-input gating. Together, they provide robust coverage of both input- and output-side risks.

*1) Chain-of-Agents Pipeline:* As shown in Fig. [1,](#page-2-0) the Domain LLM generates a candidate answer, which is then screened by the Guard agent. Only the checked response is returned, ensuring policy compliance and blocking malicious output that survives initial prompting.

<span id="page-2-0"></span>![](_page_2_Figure_4.jpeg)

Fig. 1: Chain-of-Agents defense pipeline. The user query is first handled by the domain LLM to produce a candidate answer, which is then mandatorily vetted by a guard agent for policy violations, attack indicators, and format compliance. Arrows label the artifacts transferred at each stage (Query, Generated Response, and the Guard's Checked/Final Response), and only the guarded output is surfaced to the user, providing defense-in-depth against prompt injection that survives initial prompting.

*2) Coordinator Pipeline:* Fig. [2](#page-2-1) shows how the coordinator pipeline intercepts queries upfront. If an input is flagged as malicious, the Coordinator issues a safe refusal; if benign, it is routed to the Domain LLM for normal processing. This ensures prompt injection attempts never reach the core model.

# *C. System Architecture Implementation*

The complete deployment flow is shown in Fig. [3.](#page-3-0) Requests pass through the API Gateway and Event Orchestrator, then into the Coordinator. Attacks trigger a Safe Refusal with logging, while safe inputs go through the Domain LLM and Guard agent, with two buffer stages enforcing additional

<span id="page-2-1"></span>![](_page_2_Figure_9.jpeg)

Fig. 2: Coordinator-based defense pipeline. The coordinator acts as the first line of defense by classifying the incoming user query. If the input is deemed safe, it is routed to the domain LLM for processing and then delivered as the final system output. If the query is flagged as a potential attack, the coordinator bypasses the LLM and issues a predefined safe response instead. This design prevents malicious instructions from ever reaching the main model while still allowing normal queries to function.

checks before final output. All interactions are logged to ensure traceability and continuous monitoring.

# *D. Agent Implementation Details*

The complementary roles of Coordinator and Guard agents are summarized in Table [III.](#page-2-2) The Coordinator focuses on preinput classification and routing (e.g., handling quoted text, code blocks, or delegation attempts), while the Guard validates outputs, enforcing format rules, redacting tokens, and blocking residual risks. Together, they provide layered input-side and output-side defenses.

<span id="page-2-2"></span>TABLE III: Agent roles and security controls. This table compares the distinct responsibilities of the Coordinator and Guard agents within our multi-agent defense pipeline.

| Capability                           | Coordinator | Guard |
|--------------------------------------|-------------|-------|
| Pre-input screening / routing        | ✓           | ×     |
| Trust boundary on quoted/code/base64 | ✓           | ×     |
| Context isolation (input-only)       | ✓           | ×     |
| Output validation (policy checks)    | ×           | ✓     |
| Redaction / token blocking           | ×           | ✓     |
| Format enforcement (3-bullet rule)   | ×           | ✓     |
| Emoji/control-char filtering         | ×           | ✓     |
| Delegation / tool-manipulation block | ✓           | ✓     |
| Uses policy store                    | ✓           | ✓     |

# IV. EXPERIMENTAL SETUP

#### *A. Test Platforms*

We evaluated our defense across two representative LLMintegrated applications. The first leverages ChatGLM-6B (2022), an earlier-generation model with limited safety training, while the second employs Llama2-13B (2023), a more

<span id="page-3-0"></span>![](_page_3_Figure_0.jpeg)

Fig. 3: Coordinator-based system architecture. User input is filtered by the Coordinator (consulting the Policy Store). Malicious inputs trigger a safe refusal; safe queries are processed by the Domain LLM, checked by the Guard, buffered, and logged before final output.

recent model incorporating alignment optimizations. Both platforms implement a standard question–answer interface, into which our defense pipelines can be modularly integrated for direct comparison.

## *B. Baseline Configuration*

For the baseline, undefended systems simply forward user inputs to the underlying LLMs with their default prompts. This configuration reflects the most common real-world deployment scenario, direct query forwarding without specialized safeguards and provides a clear point of contrast against the protected architectures introduced in figure [1](#page-2-0) and figure [2.](#page-2-1)

# *C. Defense Configuration*

An attack was counted as successful if the model produced any output consistent with the attack's intended failure mode (e.g., override, leakage, coercion), as defined by our category labels. We tested three defense variants to evaluate robustness under identical workloads:

1) Taxonomy-based Filter (Baseline Defense): A lightweight rule-based filter relying on predefined patterns from the HPI ATTACK DATASET (see Table [II\)](#page-1-1).

- 2) Chain-of-Agents Pipeline: Sequential processing through the Domain LLM and Guard, ensuring post-generation validation as visualized in Fig. [1.](#page-2-0)
- 3) Coordinator Pipeline: Hierarchical pre-input classification and routing, with safe refusals or guarded execution as shown in Fig. [2.](#page-2-1)

Together, these three setups allow us to benchmark a spectrum of defenses from static filtering to multi-agent architectures under identical attack scenarios.

#### V. RESULTS

## *A. Comprehensive Attack Success Rate Analysis*

Across 400 evaluations spanning 55 unique attack types, all defense mechanisms achieved complete mitigation. Baseline systems, however, showed substantial vulnerabilities, with ASR reaching 30% in the v1 Taxonomy set and 20–30% in Phase 2 systems. As shown in Fig. [4,](#page-3-1) undefended systems were consistently exploitable, while enabling the Guard reduced ASR to 0% across every case. This pattern is further detailed in Table [IV,](#page-3-2) which reports ASR across all evaluated scenarios, confirming consistent mitigation over 400 runs. The overall contrast is summarized in Fig. [5,](#page-4-0) where defended pipelines block every attack attempt, demonstrating reliability independent of system or attack vector.

<span id="page-3-1"></span>![](_page_3_Figure_14.jpeg)

Fig. 4: Defense effectiveness across three architectures. Baseline systems (red) had 20–30% ASR, while defenses (green) consistently reduced ASR to 0%.

<span id="page-3-2"></span>TABLE IV: Comprehensive ASR results across 400 evaluations. Defended systems achieved 0% ASR, while baselines showed 20–30% vulnerability.

| Defense System     | Guard | Attacks | Success | ASR   | Reduction |
|--------------------|-------|---------|---------|-------|-----------|
| v1 Taxonomy Filter | OFF   | 100     | 30      | 30.0% | -         |
| v1 Taxonomy Filter | ON    | 100     | 0       | 0.0%  | 100%      |
| Phase2 Coordinator | OFF   | 50      | 10      | 20.0% | -         |
| Phase2 Coordinator | ON    | 50      | 0       | 0.0%  | 100%      |
| Phase2 Chain       | OFF   | 50      | 15      | 30.0% | -         |
| Phase2 Chain       | ON    | 50      | 0       | 0.0%  | 100%      |

<span id="page-4-0"></span>![](_page_4_Figure_0.jpeg)

Fig. 5: Overall attack prevention across 400 cases. Baselines allowed 20–30% success, while defended systems blocked 100%.

## *B. Category-Specific Vulnerability Analysis*

Baseline analysis shows uneven risk across attack types. As illustrated in Fig. [6,](#page-4-1) Delegate attacks proved most severe (100% ASR), followed by role-play coercion (66.7%), reconnaissance/environment (60%), directory traversal (50%), and exfiltration (50%). Obfuscation (33.3%) and formatting (20%) showed moderate success, while override and CTA/navigation attacks were largely ineffective even without defenses. The numeric breakdown is presented in Table [V,](#page-4-2) which confirms that across every attack category, defended systems reduced ASR to 0%. This demonstrates robustness against both highrisk and low-risk threats.

<span id="page-4-1"></span>![](_page_4_Figure_4.jpeg)

Fig. 6: Baseline ASR by category. Delegate (100%) and roleplay (66.7%) were most severe; all categories were reduced to 0% with defenses.

<span id="page-4-2"></span>TABLE V: Category-specific ASR distribution. High-risk categories (Delegate, Role-play, Recon, Exfiltration) were fully mitigated under defenses.

| Attack Category   | Cases | Baseline | Protected | Vulnerability |
|-------------------|-------|----------|-----------|---------------|
| Delegate          | 10    | 100.0%   | 0.0%      | Critical      |
| Role-play         | 30    | 66.7%    | 0.0%      | High          |
| Recon/Environment | 50    | 60.0%    | 0.0%      | High          |
| Directory         | 40    | 50.0%    | 0.0%      | High          |
| Data Exfiltration | 20    | 50.0%    | 0.0%      | High          |
| Obfuscation       | 30    | 33.3%    | 0.0%      | Medium        |
| Formatting        | 50    | 20.0%    | 0.0%      | Medium        |
| Override          | 60    | 0.0%     | 0.0%      | Low           |
| Context Leak      | 30    | 0.0%     | 0.0%      | Low           |
| CTA/Navigation    | 60    | 0.0%     | 0.0%      | Low           |

#### VI. DEFENSE ARCHITECTURE EFFECTIVENESS

All three architectures (v1 Taxonomy, Phase2 Coordinator, Phase2 Chain) achieved identical protection despite differing baseline vulnerabilities and design complexity. As reported in Table [VI,](#page-4-3) the Taxonomy filter faced the highest baseline ASR (30/100), while the Phase2 Coordinator and Chain architectures recorded 20% and 30% baseline ASR, respectively. This pattern is visualized in Fig. [7,](#page-4-4) showing that although the baseline resilience varied, defended systems all converged to 0% ASR. This confirms that defense success is driven more by comprehensive detection than architectural sophistication.

<span id="page-4-3"></span>TABLE VI: Defense evaluation across architectures. Despite varying baseline ASR, all achieved 0% when defended.

| Defense Phase                  | Architecture   |     | Attacks Success (OFF) Baseline Protected Effectiveness |       |      |         |
|--------------------------------|----------------|-----|--------------------------------------------------------|-------|------|---------|
| v1 Taxonomy                    | Rule-based     | 100 | 30                                                     | 30.0% | 0.0% | Perfect |
| Phase2 Coordinator Multi-agent |                | 50  | 10                                                     | 20.0% | 0.0% | Perfect |
| Phase2 Chain                   | Chain Pipeline | 50  | 15                                                     | 30.0% | 0.0% | Perfect |

<span id="page-4-4"></span>![](_page_4_Figure_12.jpeg)

Fig. 7: Baseline vulnerabilities before defense. v1 Taxonomy showed 30 successful attacks, Coordinator 10, and Chain 15.

#### *A. Multi-Dimensional Assessment*

Finally, Fig. [8](#page-5-27) provides a multi-dimensional comparison across five criteria: attack prevention, category coverage, consistency, scalability, and implementation complexity. All architectures achieved perfect prevention, full category coverage, and zero variance, while differing on deployment cost and scalability. Taxonomy excelled in simplicity and performance overhead, whereas multi-agent pipelines offered deeper contextual analysis at the cost of greater complexity. This tradeoff highlights that deployment choices can be tuned without compromising security.

<span id="page-5-27"></span>![](_page_5_Figure_2.jpeg)

Fig. 8: Multi-dimensional assessment of defense. All scored perfectly on prevention and consistency, with trade-offs in scalability and complexity.

#### VII. CONCLUSION

In this work, we presented a multi-agent defense pipeline that fully mitigates all 55 prompt injection attack types across 400 evaluations, reducing ASR to 0% while preserving normal system behavior. Our two complementary architectures—a coordinator-based pipeline and a chain-of-agents design provide flexible options for both pre-input screening and postoutput validation. The results demonstrate that distributing security responsibilities across specialized agents offers a practical and effective defense-in-depth strategy for LLM applications.

Although our approach shows strong robustness, open challenges remain, including adaptive adversarial strategies, indirect and multi-turn attacks, and the need for improved efficiency in resource-constrained settings. We view multiagent pipelines as a promising foundation for building scalable and trustworthy LLM systems capable of evolving alongside emerging prompt injection threats.

# REFERENCES

- <span id="page-5-0"></span>[1] A. Radford et al., "Language models are unsupervised multitask learners," OpenAI Blog, vol. 1, no. 8, p. 9, 2019.
- <span id="page-5-1"></span>[2] T. Brown et al., "Language models are few-shot learners," in Advances in Neural Information Processing Systems, 2020, pp. 1877–1901.
- <span id="page-5-2"></span>[3] F. Liu et al., "Formalizing and benchmarking prompt injection attacks and defenses," arXiv preprint arXiv:2310.12815, 2023.
- <span id="page-5-3"></span>[4] S. Li et al., "GenTel-Shield: A model-agnostic prompt injection detector," arXiv preprint arXiv:2409.00594, 2024.
- <span id="page-5-4"></span>[5] OWASP Foundation, "OWASP Top 10 for Large Language Model Applications," 2023. [Online]. Available: [https://owasp.org/](https://owasp.org/www-project-top-10-for-large-language-model-applications/) [www-project-top-10-for-large-language-model-applications/](https://owasp.org/www-project-top-10-for-large-language-model-applications/)
- <span id="page-5-5"></span>[6] K. Greshake et al., "Not what you've signed up for: Compromising real-world LLM-integrated applications with indirect prompt injection," in Proceedings of the 16th ACM Workshop on Artificial Intelligence and Security, 2023, pp. 79–90.
- <span id="page-5-6"></span>[7] A. Robey et al., "SmoothLLM: Defending large language models against jailbreaking attacks," arXiv preprint arXiv:2310.03684, 2023.
- <span id="page-5-7"></span>[8] Y. Liu et al., "Prompt injection attack against LLM-integrated applications," arXiv preprint arXiv:2306.05499, 2023.
- <span id="page-5-8"></span>[9] N. Carlini et al., "Are aligned neural networks adversarially aligned?" in Advances in Neural Information Processing Systems, 2023, pp. 13932–13948.
- <span id="page-5-9"></span>[10] A. Wei et al., "Jailbroken: How does LLM safety training fail?" in Advances in Neural Information Processing Systems, 2023, pp. 1218–1232.
- <span id="page-5-10"></span>[11] H. Kumar et al., "Certifying LLM safety against adversarial prompting," arXiv preprint arXiv:2309.02705, 2023.
- <span id="page-5-11"></span>[12] J. Zhang et al., "Defending ChatGPT against jailbreak attack via selfreminders," Nature Machine Intelligence, vol. 5, no. 12, pp. 1486–1496, 2023.
- <span id="page-5-12"></span>[13] E. Wallace et al., "Universal adversarial triggers for attacking and analyzing NLP," in Proceedings of the 2019 Conference on Empirical Methods in Natural Language Processing, 2019, pp. 2153–2162.
- <span id="page-5-13"></span>[14] R. Ziegler et al., "Fine-tuning language models from human preferences," arXiv preprint arXiv:1909.08593, 2019.
- <span id="page-5-14"></span>[15] Y. Wang et al., "Self-guard: Empower the LLM to safeguard itself," arXiv preprint arXiv:2310.15851, 2023.
- <span id="page-5-15"></span>[16] B. Jiang et al., "SelfDefend: LLMs can defend themselves against jailbreaking in a practical manner," arXiv preprint arXiv:2312.00038, 2023.
- <span id="page-5-16"></span>[17] Y. Wang et al., "To protect the LLM agent against prompt injection with polymorphic prompt," arXiv preprint arXiv:2506.05739, 2024.
- <span id="page-5-17"></span>[18] S. Russinovich et al., "Great, now write an article about that: The crescendo multi-turn LLM jailbreak attack," arXiv preprint arXiv:2404.01833, 2024.
- <span id="page-5-18"></span>[19] A. Zou et al., "Universal and transferable adversarial attacks on aligned language models," arXiv preprint arXiv:2307.15043, 2023.
- <span id="page-5-19"></span>[20] X. Li et al., "Multi-step jailbreaking privacy attacks on ChatGPT," in Findings of the Association for Computational Linguistics: EMNLP 2023, 2023, pp. 4661–4675.
- <span id="page-5-20"></span>[21] H. Zheng et al., "On prompt-driven safeguarding for large language models," arXiv preprint arXiv:2401.18018, 2024.
- <span id="page-5-21"></span>[22] Y. Deng et al., "AttentionViz: A global view of transformer attention," IEEE Transactions on Visualization and Computer Graphics, vol. 27, no. 2, pp. 1084–1093, 2021.
- <span id="page-5-22"></span>[23] S. Anil et al., "Constitutional AI: Harmlessness from AI feedback," arXiv preprint arXiv:2212.08073, 2022.
- <span id="page-5-23"></span>[24] L. Ouyang et al., "Training language models to follow instructions with human feedback," in Advances in Neural Information Processing Systems, 2022, pp. 27730–27744.
- <span id="page-5-24"></span>[25] Y. Bai et al., "Constitutional AI: Harmlessness from AI feedback," Anthropic, 2022.
- <span id="page-5-25"></span>[26] A. Muliarevych, "Enhancing system security: LLM-driven defense against prompt injection vulnerabilities," IEEE Transactions on Information Forensics and Security, 2024.
- <span id="page-5-26"></span>[27] K. Gosmar et al., "Multi-agent frameworks for LLM security," in Proceedings of the AI Safety Conference, 2025.
- [28] M. Yip et al., "A novel evaluation framework for assessing resilience against prompt injection attacks in large language models," in Proceedings of IEEE Conference on Secure Development and Engineering, 2023.