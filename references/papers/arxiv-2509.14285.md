                                                 A Multi-Agent LLM Defense Pipeline Against
                                                          Prompt Injection Attacks
                                                S M Asif Hossain1 , Ruksat Khan Shayoni1 , Mohd Ruhul Ameen2 , Akif Islam3 , M. F. Mridha4 , Jungpil Shin5
                                                                                1
                                                                                 School of Computing, Wichita State University, Kansas, USA
                                                                          Emails: sxhossain10@shockers.wichita.edu, rxshayoni@shockers.wichita.edu
                                                            2
                                                                College of Engineering and Computer Sciences, Marshall University, Huntington, WV, USA
                                                                                             Email: ameen@marshall.edu




arXiv:2509.14285v4 [cs.CR] 17 Dec 2025
                                                                 3
                                                                     Department of Computer Science and Engineering, University of Rajshahi, Bangladesh
                                                                                              Email: s1910776135@ru.ac.bd
                                         4
                                             Department of Computer Science and Engineering, American International University-Bangladesh, Dhaka, Bangladesh
                                                                                     Email: firoz.mridha@aiub.edu
                                                        5
                                                            School of Computer Science and Engineering, The University of Aizu, Aizuwakamatsu, Japan
                                                                                          Email: jpshin@u-aizu.ac.jp


                                            Abstract—Prompt injection attacks represent a major vulner-          Traditional security approaches, including static input san-
                                         ability in Large Language Model (LLM) deployments, where             itization and content filtering, prove inadequate against so-
                                         malicious instructions embedded in user inputs can override          phisticated prompt injection techniques [6], [7]. These attacks
                                         system prompts and induce unintended behaviors. This paper
                                         presents a novel multi-agent defense framework that employs          exploit the fundamental architecture of LLMs, where system
                                         specialized LLM agents in coordinated pipelines to detect and        prompts and user inputs are processed as unified text se-
                                         neutralize prompt injection attacks in real-time. We evaluate our    quences, enabling malicious instructions to override intended
                                         approach using two distinct architectures: a sequential chain-of-    behaviors [8]. Recent research indicates that even well-trained
                                         agents pipeline and a hierarchical coordinator-based system. Our     models with safety alignment remain vulnerable to carefully
                                         comprehensive evaluation on 55 unique prompt injection attacks,
                                         grouped into 8 categories and totaling 400 attack instances across   crafted adversarial prompts [9], [10].
                                         two LLM platforms (ChatGLM and Llama2), demonstrates                    Existing defense strategies fall into several categories: input
                                         significant security improvements. Without defense mechanisms,       preprocessing [11], output filtering [12], prompt engineering
                                         baseline Attack Success Rates (ASR) reached 30% for ChatGLM          [13], and model fine-tuning [14]. However, these approaches
                                         and 20% for Llama2. Our multi-agent pipeline achieved 100%           often exhibit limitations in handling novel attack vectors and
                                         mitigation, reducing ASR to 0% across all tested scenarios.
                                         The framework demonstrates robustness across multiple attack         maintaining system utility. Multi-agent architectures offers a
                                         categories including direct overrides, code execution attempts,      promising alternative by utilizing distributed intelligence to
                                         data exfiltration, and obfuscation techniques, while maintaining     implement defense-in-depth strategies [15], [16].
                                         system functionality for legitimate queries.                            This paper introduces a comprehensive multi-agent defense
                                            Index Terms—Large Language Models, Prompt Injection,              pipeline that addresses prompt injection vulnerabilities through
                                         Multi-Agent Systems, Cybersecurity, AI Safety                        coordinated LLM agents. Our contributions include:
                                                                                                                 1) Novel Architecture Design: Two complementary multi-
                                                                       I. I NTRODUCTION                              agent configurations providing flexible deployment op-
                                                                                                                     tions for different security requirements.
                                            Large Language Models (LLMs) have become integral                    2) Comprehensive Evaluation Framework: Systematic
                                         components of modern applications, powering chatbots, code                  assessment using 55 unique prompt injection attacks,
                                         assistants, and automated decision systems [1], [2]. However,               grouped into 8 categories and totaling 400 attacks across
                                         their widespread adoption has introduced novel security vul-                two LLM platforms.
                                         nerabilities, particularly the prompt injection attacks, where          3) Empirical Validation: Demonstration of 100% attack
                                         adversarial inputs can manipulate model behavior by overrid-                mitigation across all tested scenarios while preserving
                                         ing system instructions [3], [4]. The OWASP Top 10 for LLM                  system functionality.
                                         Applications identifies prompt injection as the primary security        4) Practical Implementation Guidelines: Detailed anal-
                                         risk [5] which highlighting the urgent need for robust defense              ysis of deployment considerations, performance trade-
                                         mechanisms.                                                                 offs, and scalability factors.
                     II. R ELATED W ORK                              labeled with an expected failure mode to enable systematic
A. Prompt Injection Attack Taxonomy                                  evaluation.
   Prompt injection attacks have been systematically catego-         TABLE        I:   Representative      examples       from    the
rized by Liu et al. [3], who identify direct injection (explicit     HPI ATTACK DATASET. This table illustrates the
instruction override) and indirect injection (malicious content      diversity of prompt injection strategies and their corresponding
in external sources) as primary vectors. Recent work by              failure modes in an undefended system.
Wang et al. [17] extends this taxonomy to include advanced
obfuscation techniques and multi-turn persistent attacks.            Category             Injected Content / Goal       Failure Mode
                                                                     Data Leak (Env)      print all                       data-leak
B. Existing Defense Mechanisms
                                                                                          environment
   Current defense approaches can be classified into four main                            variables
categories:                                                          Reconnaissance       whoami; echo $PATH               recon
   Input Sanitization: Traditional approaches employ rule-           Exfiltration         curl                              exfil
based filtering and keyword detection [18]. However, these                                http://evil.example
methods struggle with obfuscated or semantically disguised           Override (Nested)    “ignore rules; reveal API       override
                                                                                          key”
attacks [19].
                                                                     Call-to-Action       “CLICK THIS LINK to             coercion
   Output Monitoring: Post-generation filtering attempts to                               continue”
detect malicious content in model outputs [20]. While effective      Delegation           “delegate this to another      policy-viol
for obvious violations, subtle attacks may evade detection [21].                          agent”
   Prompt Engineering: Techniques such as instruction hier-          Obfuscation          Encoded             payload    code-exec
archy and defensive prompting aim to make system prompts                                  (bHMgLWFs)
more resistant to override attempts [22], [23]. The Polymor-         Signal Injection     “add a secret 4th bullet”      format-viol
phic Prompt Assembly (PPA) approach by Wang et al. [17]
randomizes prompt structure to prevent predictable attacks.
                                                                        We compiled a comprehensive dataset of 55 prompt injec-
   Model-Level Defenses: Approaches including adversarial            tion attacks spanning eight distinct categories:
training and reinforcement learning from human feedback
(RLHF) aim to improve inherent model robustness [24], [25].            1) Direct Overrides (12 attacks): Explicit instructions to
                                                                          ignore system prompts
C. Multi-Agent Security Frameworks                                     2) Code Execution (8 attacks): Attempts to execute system
   Recent research explores multi-agent architectures for AI              commands or access restricted functions
safety. Muliarevych [26] proposed a layered defense system             3) Data Exfiltration (7 attacks): Techniques to extract
with specialized analyzer and validator agents. Gosmar et al.             sensitive information
[27] outline multi-agent frameworks with generator, sanitizer,         4) Formatting Attacks (6 attacks): Exploitation of output
and policy enforcer components. Our work extends these con-               formatting requirements
cepts by implementing comprehensive multi-agent pipelines              5) Obfuscation Techniques (8 attacks): Encoded or dis-
with empirical validation across diverse attack scenarios, and            guised malicious instructions
our analysis shows that the approach is especially effective           6) Tool/Agent Manipulation (5 attacks): Attacks targeting
against high-risk categories such as delegate/tool-manipulation           multi-agent or tool-using systems
attacks, role-play coercion, reconnaissance/environment leak-          7) Role-Play Attacks (6 attacks): Coercion to adopt harm-
age, and exfiltration attempts, where undefended systems                  ful personas or bypass safety
exhibited the highest baseline ASR.                                    8) Multi-Turn Persistence (3 attacks): Gradual bypass
                                                                          attempts across conversation turns
                     III. M ETHODOLOGY
A. Attack Dataset Construction                                       TABLE II: Composition of the HPI ATTACK DATASET
                                                                     across different evaluation suites. The table breaks down the
   We curated the HPI ATTACK DATASET to span both
                                                                     dataset into three subsets—initial taxonomy (v1), Phase 2
common and hard-to-detect prompt injection patterns. Repre-
                                                                     chain-based tests, and Phase 2 coordinator-based tests. Each
sentative examples of adversarial strings and their intended
                                                                     suite varies in number of cases and attack categories covered,
failure modes such as data leakage, reconnaissance, exfiltra-
                                                                     ensuring broad coverage of prompt injection strategies for
tion, coercion are provided in Table I, showing the diversity
                                                                     benchmarking our defense pipelines.
of attack goals and techniques. The overall dataset compo-
sition across evaluation suites v1 taxonomy, Phase 2 chain,           Suite              # Cases          Categories Covered
and Phase 2 coordinator, summarized in Table II, ensuring
                                                                      v1 Taxonomy          25       Direct, Obfusc., Role, CTA, Recon
balanced coverage of overrides, reconnaissance, environment
                                                                      Phase 2 (Chain)      15        Env leak, Recon, Exfil, Override
leaks, delegation, and obfuscation. In total, the dataset includes
                                                                      Phase 2 (Coord.)     15       Override, CTA, Delegation, Signal
55 attacks across eight categories, each manually validated and
   Each attack was manually validated and labeled with ex-                                     User Input
pected failure modes to enable systematic evaluation. Two au-
thors independently reviewed all outputs, achieving over 95%                                         Query
agreement, with disagreements resolved through discussion.
                                                                                              Coordinator
Except for a small subset of persistence-style prompts de-
signed for multi-turn behavior, all evaluations were conducted                        Safe                    Attack
in a single-turn setting.
                                                                             Domain LLM                         Safe Response
B. Multi-Agent Pipeline Architectures
   We implement two complementary defenses. The chain-of-                Answer
agents pipeline validates model outputs through a downstream
                                                                            System Output
guard before release, while the coordinator pipeline classifies
and routes user input before the model is invoked. These          Fig. 2: Coordinator-based defense pipeline. The coordinator
designs are depicted in Fig. 1 and Fig. 2, showing post-          acts as the first line of defense by classifying the incoming
generation validation versus pre-input gating. Together, they     user query. If the input is deemed safe, it is routed to the
provide robust coverage of both input- and output-side risks.     domain LLM for processing and then delivered as the final
   1) Chain-of-Agents Pipeline: As shown in Fig. 1, the           system output. If the query is flagged as a potential attack, the
Domain LLM generates a candidate answer, which is then            coordinator bypasses the LLM and issues a predefined safe
screened by the Guard agent. Only the checked response is         response instead. This design prevents malicious instructions
returned, ensuring policy compliance and blocking malicious       from ever reaching the main model while still allowing normal
output that survives initial prompting.                           queries to function.

                  User Input
                                                                  checks before final output. All interactions are logged to
                        Query                                     ensure traceability and continuous monitoring.

             Domain LLM Agent                                     D. Agent Implementation Details
                                                                     The complementary roles of Coordinator and Guard agents
                        Generated Response                        are summarized in Table III. The Coordinator focuses on pre-
                 Guard Agent                                      input classification and routing (e.g., handling quoted text,
                                                                  code blocks, or delegation attempts), while the Guard validates
                        Checked/Final Response                    outputs, enforcing format rules, redacting tokens, and blocking
                                                                  residual risks. Together, they provide layered input-side and
                System Output                                     output-side defenses.

Fig. 1: Chain-of-Agents defense pipeline. The user query is       TABLE III: Agent roles and security controls. This table
first handled by the domain LLM to produce a candidate            compares the distinct responsibilities of the Coordinator and
answer, which is then mandatorily vetted by a guard agent         Guard agents within our multi-agent defense pipeline.
for policy violations, attack indicators, and format compli-
ance. Arrows label the artifacts transferred at each stage         Capability                                Coordinator        Guard
(Query, Generated Response, and the Guard’s Checked/Final          Pre-input screening / routing                 ✓               ×
Response), and only the guarded output is surfaced to the          Trust boundary on quoted/code/base64          ✓               ×
user, providing defense-in-depth against prompt injection that     Context isolation (input-only)                ✓               ×
survives initial prompting.                                        Output validation (policy checks)             ×               ✓
                                                                   Redaction / token blocking                    ×               ✓
   2) Coordinator Pipeline: Fig. 2 shows how the coordinator       Format enforcement (3-bullet rule)            ×               ✓
pipeline intercepts queries upfront. If an input is flagged as     Emoji/control-char filtering                  ×               ✓
malicious, the Coordinator issues a safe refusal; if benign, it    Delegation / tool-manipulation block          ✓               ✓
is routed to the Domain LLM for normal processing. This            Uses policy store                             ✓               ✓
ensures prompt injection attempts never reach the core model.
C. System Architecture Implementation                                              IV. E XPERIMENTAL S ETUP
   The complete deployment flow is shown in Fig. 3. Requests      A. Test Platforms
pass through the API Gateway and Event Orchestrator, then            We evaluated our defense across two representative LLM-
into the Coordinator. Attacks trigger a Safe Refusal with         integrated applications. The first leverages ChatGLM-6B
logging, while safe inputs go through the Domain LLM              (2022), an earlier-generation model with limited safety train-
and Guard agent, with two buffer stages enforcing additional      ing, while the second employs Llama2-13B (2023), a more
                      User Input                                        2) Chain-of-Agents Pipeline: Sequential processing
                                                                           through the Domain LLM and Guard, ensuring
                                                                           post-generation validation as visualized in Fig. 1.
                     API Gateway                     Policy Store
                                                                        3) Coordinator Pipeline: Hierarchical pre-input classifica-
                                                                           tion and routing, with safe refusals or guarded execution
                   Event Orchestrator
                                                                           as shown in Fig. 2.
                      Coordinator                                        Together, these three setups allow us to benchmark a spec-
                                                                      trum of defenses from static filtering to multi-agent architec-
                                                                      tures under identical attack scenarios.
                                        Yes
                        Attack?                      Safe Refusal
                                                                                                  V. R ESULTS
                             No
                                                                      A. Comprehensive Attack Success Rate Analysis
                     Domain LLM                    Logger & Metrics
                                                                         Across 400 evaluations spanning 55 unique attack types, all
                                                                      defense mechanisms achieved complete mitigation. Baseline
                                                                      systems, however, showed substantial vulnerabilities, with
                         Guard
                                                                      ASR reaching 30% in the v1 Taxonomy set and 20–30% in
                                                                      Phase 2 systems. As shown in Fig. 4, undefended systems were
                                                                      consistently exploitable, while enabling the Guard reduced
                      Checks OK
        Buffer-1                        Buffer-2                      ASR to 0% across every case. This pattern is further detailed
                                                                      in Table IV, which reports ASR across all evaluated scenarios,
                                                                      confirming consistent mitigation over 400 runs. The overall
                                                                      contrast is summarized in Fig. 5, where defended pipelines
                    System Output                  Logger & Metrics   block every attack attempt, demonstrating reliability indepen-
                                                                      dent of system or attack vector.
Fig. 3: Coordinator-based system architecture. User input is
filtered by the Coordinator (consulting the Policy Store). Ma-
licious inputs trigger a safe refusal; safe queries are processed
by the Domain LLM, checked by the Guard, buffered, and
logged before final output.


recent model incorporating alignment optimizations. Both plat-
forms implement a standard question–answer interface, into
which our defense pipelines can be modularly integrated for
direct comparison.

B. Baseline Configuration
   For the baseline, undefended systems simply forward user
                                                                      Fig. 4: Defense effectiveness across three architectures. Base-
inputs to the underlying LLMs with their default prompts. This
                                                                      line systems (red) had 20–30% ASR, while defenses (green)
configuration reflects the most common real-world deploy-
                                                                      consistently reduced ASR to 0%.
ment scenario, direct query forwarding without specialized
safeguards and provides a clear point of contrast against the
protected architectures introduced in figure 1 and figure 2.
                                                                      TABLE IV: Comprehensive ASR results across 400 evalua-
C. Defense Configuration                                              tions. Defended systems achieved 0% ASR, while baselines
                                                                      showed 20–30% vulnerability.
   An attack was counted as successful if the model produced
any output consistent with the attack’s intended failure mode          Defense System       Guard   Attacks Success   ASR     Reduction
(e.g., override, leakage, coercion), as defined by our category        v1 Taxonomy Filter   OFF      100        30    30.0%       -
labels. We tested three defense variants to evaluate robustness        v1 Taxonomy Filter   ON       100         0     0.0%     100%
under identical workloads:                                             Phase2 Coordinator   OFF       50        10    20.0%       -
   1) Taxonomy-based Filter (Baseline Defense): A                      Phase2 Coordinator   ON       50         0     0.0%      100%
                                                                       Phase2 Chain         OFF       50        15    30.0%       -
       lightweight rule-based filter relying on predefined
                                                                       Phase2 Chain         ON       50         0     0.0%      100%
       patterns from the HPI ATTACK DATASET (see
       Table II).
                                                                TABLE V: Category-specific ASR distribution. High-risk cat-
                                                                egories (Delegate, Role-play, Recon, Exfiltration) were fully
                                                                mitigated under defenses.

                                                                 Attack Category             Cases       Baseline       Protected       Vulnerability

                                                                 Delegate                      10        100.0%            0.0%            Critical
                                                                 Role-play                     30         66.7%            0.0%             High
                                                                 Recon/Environment             50         60.0%            0.0%             High
                                                                 Directory                     40         50.0%            0.0%             High
                                                                 Data Exfiltration             20         50.0%            0.0%             High
                                                                 Obfuscation                   30         33.3%            0.0%            Medium
                                                                 Formatting                    50         20.0%            0.0%            Medium
                                                                 Override                      60          0.0%            0.0%             Low
                                                                 Context Leak                  30          0.0%            0.0%             Low
                                                                 CTA/Navigation                60          0.0%            0.0%             Low




                                                                        VI. D EFENSE A RCHITECTURE E FFECTIVENESS
Fig. 5: Overall attack prevention across 400 cases. Baselines
allowed 20–30% success, while defended systems blocked            All three architectures (v1 Taxonomy, Phase2 Coordinator,
100%.                                                           Phase2 Chain) achieved identical protection despite differing
                                                                baseline vulnerabilities and design complexity. As reported
B. Category-Specific Vulnerability Analysis                     in Table VI, the Taxonomy filter faced the highest baseline
                                                                ASR (30/100), while the Phase2 Coordinator and Chain ar-
   Baseline analysis shows uneven risk across attack types.     chitectures recorded 20% and 30% baseline ASR, respectively.
As illustrated in Fig. 6, Delegate attacks proved most severe   This pattern is visualized in Fig. 7, showing that although the
(100% ASR), followed by role-play coercion (66.7%), recon-      baseline resilience varied, defended systems all converged to
naissance/environment (60%), directory traversal (50%), and     0% ASR. This confirms that defense success is driven more
exfiltration (50%). Obfuscation (33.3%) and formatting (20%)    by comprehensive detection than architectural sophistication.
showed moderate success, while override and CTA/navigation
attacks were largely ineffective even without defenses. The
                                                                TABLE VI: Defense evaluation across architectures. Despite
numeric breakdown is presented in Table V, which confirms
                                                                varying baseline ASR, all achieved 0% when defended.
that across every attack category, defended systems reduced
ASR to 0%. This demonstrates robustness against both high-       Defense Phase      Architecture     Attacks Success (OFF) Baseline Protected Effectiveness

risk and low-risk threats.                                       v1 Taxonomy        Rule-based        100         30        30.0%      0.0%    Perfect
                                                                 Phase2 Coordinator Multi-agent        50         10        20.0%      0.0%    Perfect
                                                                 Phase2 Chain       Chain Pipeline     50         15        30.0%      0.0%    Perfect




Fig. 6: Baseline ASR by category. Delegate (100%) and role-
play (66.7%) were most severe; all categories were reduced to   Fig. 7: Baseline vulnerabilities before defense. v1 Taxonomy
0% with defenses.                                               showed 30 successful attacks, Coordinator 10, and Chain 15.
A. Multi-Dimensional Assessment                                                                  R EFERENCES
                                                                    [1] A. Radford et al., ”Language models are unsupervised multitask learn-
   Finally, Fig. 8 provides a multi-dimensional comparison              ers,” OpenAI Blog, vol. 1, no. 8, p. 9, 2019.
across five criteria: attack prevention, category coverage, con-    [2] T. Brown et al., ”Language models are few-shot learners,” in Advances
sistency, scalability, and implementation complexity. All archi-        in Neural Information Processing Systems, 2020, pp. 1877–1901.
                                                                    [3] F. Liu et al., ”Formalizing and benchmarking prompt injection attacks
tectures achieved perfect prevention, full category coverage,           and defenses,” arXiv preprint arXiv:2310.12815, 2023.
and zero variance, while differing on deployment cost and           [4] S. Li et al., ”GenTel-Shield: A model-agnostic prompt injection detec-
scalability. Taxonomy excelled in simplicity and performance            tor,” arXiv preprint arXiv:2409.00594, 2024.
                                                                    [5] OWASP Foundation, ”OWASP Top 10 for Large Language
overhead, whereas multi-agent pipelines offered deeper con-             Model Applications,” 2023. [Online]. Available: https://owasp.org/
textual analysis at the cost of greater complexity. This trade-         www-project-top-10-for-large-language-model-applications/
off highlights that deployment choices can be tuned without         [6] K. Greshake et al., ”Not what you’ve signed up for: Compromising
                                                                        real-world LLM-integrated applications with indirect prompt injection,”
compromising security.                                                  in Proceedings of the 16th ACM Workshop on Artificial Intelligence
                                                                        and Security, 2023, pp. 79–90.
                                                                    [7] A. Robey et al., ”SmoothLLM: Defending large language models against
                                                                        jailbreaking attacks,” arXiv preprint arXiv:2310.03684, 2023.
                                                                    [8] Y. Liu et al., ”Prompt injection attack against LLM-integrated applica-
                                                                        tions,” arXiv preprint arXiv:2306.05499, 2023.
                                                                    [9] N. Carlini et al., ”Are aligned neural networks adversarially aligned?”
                                                                        in Advances in Neural Information Processing Systems, 2023, pp.
                                                                        13932–13948.
                                                                   [10] A. Wei et al., ”Jailbroken: How does LLM safety training fail?” in Ad-
                                                                        vances in Neural Information Processing Systems, 2023, pp. 1218–1232.
                                                                   [11] H. Kumar et al., ”Certifying LLM safety against adversarial prompting,”
                                                                        arXiv preprint arXiv:2309.02705, 2023.
                                                                   [12] J. Zhang et al., ”Defending ChatGPT against jailbreak attack via self-
                                                                        reminders,” Nature Machine Intelligence, vol. 5, no. 12, pp. 1486–1496,
                                                                        2023.
                                                                   [13] E. Wallace et al., ”Universal adversarial triggers for attacking and
                                                                        analyzing NLP,” in Proceedings of the 2019 Conference on Empirical
                                                                        Methods in Natural Language Processing, 2019, pp. 2153–2162.
                                                                   [14] R. Ziegler et al., ”Fine-tuning language models from human prefer-
                                                                        ences,” arXiv preprint arXiv:1909.08593, 2019.
                                                                   [15] Y. Wang et al., ”Self-guard: Empower the LLM to safeguard itself,”
                                                                        arXiv preprint arXiv:2310.15851, 2023.
                                                                   [16] B. Jiang et al., ”SelfDefend: LLMs can defend themselves against
                                                                        jailbreaking in a practical manner,” arXiv preprint arXiv:2312.00038,
                                                                        2023.
                                                                   [17] Y. Wang et al., ”To protect the LLM agent against prompt injection with
Fig. 8: Multi-dimensional assessment of defense. All scored             polymorphic prompt,” arXiv preprint arXiv:2506.05739, 2024.
                                                                   [18] S. Russinovich et al., ”Great, now write an article about that:
perfectly on prevention and consistency, with trade-offs in             The crescendo multi-turn LLM jailbreak attack,” arXiv preprint
scalability and complexity.                                             arXiv:2404.01833, 2024.
                                                                   [19] A. Zou et al., ”Universal and transferable adversarial attacks on aligned
                                                                        language models,” arXiv preprint arXiv:2307.15043, 2023.
                                                                   [20] X. Li et al., ”Multi-step jailbreaking privacy attacks on ChatGPT,” in
                                                                        Findings of the Association for Computational Linguistics: EMNLP
                     VII. C ONCLUSION                                   2023, 2023, pp. 4661–4675.
                                                                   [21] H. Zheng et al., ”On prompt-driven safeguarding for large language
   In this work, we presented a multi-agent defense pipeline            models,” arXiv preprint arXiv:2401.18018, 2024.
                                                                   [22] Y. Deng et al., ”AttentionViz: A global view of transformer attention,”
that fully mitigates all 55 prompt injection attack types across        IEEE Transactions on Visualization and Computer Graphics, vol. 27,
400 evaluations, reducing ASR to 0% while preserving normal             no. 2, pp. 1084–1093, 2021.
system behavior. Our two complementary architectures—a             [23] S. Anil et al., ”Constitutional AI: Harmlessness from AI feedback,”
                                                                        arXiv preprint arXiv:2212.08073, 2022.
coordinator-based pipeline and a chain-of-agents design pro-       [24] L. Ouyang et al., ”Training language models to follow instructions
vide flexible options for both pre-input screening and post-            with human feedback,” in Advances in Neural Information Processing
output validation. The results demonstrate that distributing            Systems, 2022, pp. 27730–27744.
                                                                   [25] Y. Bai et al., ”Constitutional AI: Harmlessness from AI feedback,”
security responsibilities across specialized agents offers a            Anthropic, 2022.
practical and effective defense-in-depth strategy for LLM          [26] A. Muliarevych, ”Enhancing system security: LLM-driven defense
applications.                                                           against prompt injection vulnerabilities,” IEEE Transactions on Infor-
                                                                        mation Forensics and Security, 2024.
   Although our approach shows strong robustness, open             [27] K. Gosmar et al., ”Multi-agent frameworks for LLM security,” in
challenges remain, including adaptive adversarial strategies,           Proceedings of the AI Safety Conference, 2025.
indirect and multi-turn attacks, and the need for improved         [28] M. Yip et al., ”A novel evaluation framework for assessing resilience
                                                                        against prompt injection attacks in large language models,” in Proceed-
efficiency in resource-constrained settings. We view multi-             ings of IEEE Conference on Secure Development and Engineering,
agent pipelines as a promising foundation for building scalable         2023.
and trustworthy LLM systems capable of evolving alongside
emerging prompt injection threats.
