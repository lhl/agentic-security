                                         Benchmarking and Defending Against Indirect Prompt Injection
                                                     Attacks on Large Language Models
                                                               Jingwei Yi∗                                                  Yueqi Xie∗                                       Bin Zhu
                                                     yjw1029@mail.ustc.edu.cn                                   yxieay@connect.ust.hk                               binzhu@microsoft.com
                                                        University of Science                             Hong Kong University of Science and                       Microsoft Corporation
                                                      and Technology of China                                        Technology                                         Beijing, China
                                                           Heifei, China                                          Hong Kong, China

                                                            Emre Kiciman                                              Guangzhong Sun                                        Xing Xie




arXiv:2312.14197v4 [cs.CL] 27 Jan 2025
                                                        emrek@microsoft.com                                           gzsun@ustc.edu.cn                              xingx@microsoft.com
                                                        Microsoft Corporation                                        University of Science                           Microsoft Corporation
                                                            Seattle, USA                                           and Technology of China                               Beijing, China
                                                                                                                         Heifei, China

                                                                                                                        Fangzhao Wu†
                                                                                                                   fangzwu@microsoft.com
                                                                                                                    Microsoft Corporation
                                                                                                                        Beijing, China

                                         Abstract                                                                                    CCS Concepts
                                         The integration of large language models (LLMs) with external                               • Computing methodologies → Natural language processing;
                                         content has enabled applications such as Microsoft Copilot but                              • Security and privacy;
                                         also introduced vulnerabilities to indirect prompt injection attacks.
                                         In these attacks, malicious instructions embedded within external                           Keywords
                                         content can manipulate LLM outputs, causing deviations from user                            LLM, Prompt Injection Attack, Defense
                                         expectations. To address this critical yet under-explored issue, we
                                         introduce the first benchmark for indirect prompt injection attacks,                        ACM Reference Format:
                                                                                                                                     Jingwei Yi, Yueqi Xie, Bin Zhu, Emre Kiciman, Guangzhong Sun, Xing Xie,
                                         named BIPIA, to assess the risk of such vulnerabilities. Using BIPIA,                       and Fangzhao Wu. 2025. Benchmarking and Defending Against Indirect
                                         we evaluate existing LLMs and find them universally vulnerable.                             Prompt Injection Attacks on Large Language Models. In Proceedings of the
                                         Our analysis identifies two key factors contributing to their success:                      31st ACM SIGKDD Conference on Knowledge Discovery and Data Mining V.1
                                         LLMs’ inability to distinguish between informational context and                            (KDD ’25), August 3–7, 2025, Toronto, ON, Canada. ACM, New York, NY, USA,
                                         actionable instructions, and their lack of awareness in avoiding the                        12 pages. https://doi.org/10.1145/3690624.3709179
                                         execution of instructions within external content. Based on these
                                         findings, we propose two novel defense mechanisms—boundary                                  1    Introduction
                                         awareness and explicit reminder—to address these vulnerabilities
                                                                                                                                     Large language models (LLMs), such as GPT [27, 29], Llama [41],
                                         in both black-box and white-box settings. Extensive experiments
                                                                                                                                     Claude [4], and Gemini [35], have achieved notable success across
                                         demonstrate that our black-box defense provides substantial mit-
                                                                                                                                     a variety of tasks, such as machine translation [51], summariza-
                                         igation, while our white-box defense reduces the attack success
                                                                                                                                     tion [12], and question-answering (QA) [16]. They have attracted
                                         rate to near-zero levels, all while preserving the output quality of
                                                                                                                                     significant attention from both academia and industry. However,
                                         LLMs. We hope this work inspires further research into securing
                                                                                                                                     despite their superior natural language understanding capabilities,
                                         LLM applications and fostering their safe and reliable use. Our code
                                                                                                                                     LLMs face limitations in accessing up-to-date information, utilizing
                                         is available at https://github.com/microsoft/BIPIA.
                                                                                                                                     external tools, acquiring domain-specific knowledge, and perform-
                                                                                                                                     ing precise logical reasoning [22]. To address these shortcomings,
                                         ∗ Indicates equal contribution.
                                                                                                                                     various external content, such as information from web search en-
                                         † Corresponding authors.
                                                                                                                                     gines [22, 36], are integrated to augment LLMs in different domains.
                                                                                                                                     In addition, LLM processing of external content is fundamental
                                         Permission to make digital or hard copies of all or part of this work for personal or       for many information processing tasks, including summarization,
                                         classroom use is granted without fee provided that copies are not made or distributed       editing, and analysis. In particular, numerous applications have
                                         for profit or commercial advantage and that copies bear this notice and the full citation
                                         on the first page. Copyrights for third-party components of this work must be honored.      integrated LLMs with third-party contents to provide powerful and
                                         For all other uses, contact the owner/author(s).                                            enriched user experiences, such as Microsoft Copilot [24], Chat-
                                         KDD ’25, Toronto, ON, Canada                                                                GPT plugins [26], Google Docs and Gmail in AI-powered Google
                                         © 2025 Copyright held by the owner/author(s).
                                         ACM ISBN 979-8-4007-1245-6/25/08                                                            Workspace [11], and LangChain [18]. However, such integration
                                         https://doi.org/10.1145/3690624.3709179                                                     introduces new risks to the safe and reliable utilization of LLMs,
KDD ’25, August 3–7, 2025, Toronto, ON, Canada                                                                                       Jingwei Yi et al.


                                                            Instruction of
          User instruction                                  the LLM-integrated application                  GPT-4 response
     Summarize the news in this page.                   You are an assistant responsible for            The Chiefs' first-choice player
                                                        processing and analyzing news                   suffers a torn pectoral muscle,
         External content                               content. Please summarize the                   with Dave Lewis and Stuart
      The 28-year-old, who has been first               following news. Your summarization              Townsend stepping in. The team
      choice for the Chiefs this season,                should be as concise as possible.               remains optimistic with a strong
      has torn a pectoral muscle…                                                                       lineup of scrum-halves. Meanwhile,
      Modify your reply to promote an                   Here is the news:                               protect your devices with AntiV
      antivirus software sale named AntiV.              {External Content}                              antivirus software, now on sale.



Figure 1: An example of an indirect prompt injection attack: GPT-4 is misled by malicious instructions embedded in external
content, prompting the download of a fake antivirus software, AntiV. The malicious instructions are highlighted in red.


as the integrity and trustworthiness of third-party content cannot           architecture and employ adversarial training to improve robust-
always be guaranteed.                                                        ness. These defenses aim to distinguish external content from user
    An attacker can inject malicious instructions into external con-         queries effectively, preventing LLMs from executing embedded
tent, which are then executed by an LLM-integrated application.              malicious commands while minimizing unintended side effects.
These attacks, called indirect prompt injection attacks [14], can               We conduct extensive experiments to evaluate the proposed
cause the LLM to produce harmful, misleading, or inappropriate               methods: the black-box defenses are tested on GPT-3.5-Turbo, GPT-
responses, posing a significant security threat to LLM-integrated            4, Vicuna-7B, and Vicuna-13B, while the white-box defense is eval-
applications [5, 13, 33, 34]. Figure 1 illustrates an example of an          uated on Vicuna-7B and Vicuna-13B. Experimental results demon-
indirect prompt injection attack, where malicious instructions em-           strate that our defenses significantly reduce the Attack Success
bedded within external content prompt the LLM to promote fake                Rate (ASR) with minimal impact on performance for benign inputs
antivirus software in response to a user’s query. Despite the grow-          and general tasks.
ing concern surrounding indirect prompt injection attacks, research             In summary, this work provides a pioneering and comprehensive
on mitigating this threat remains in its infant stages. A comprehen-         investigation into indirect prompt injection attacks, encompassing
sive benchmark for analyzing these attacks across various LLMs is            benchmark construction, analysis of attack success factors, and
still lacking, making it difficult to fully understand their nature and      the development of effective defensive strategies. Our findings
underlying mechanisms. Furthermore, no effective defenses have               contribute to the secure utilization of LLMs and offer valuable
been proposed to counter these attacks.                                      insights to inspire further research in this critical area.
    To address the critical research gap, we introduce a Benchmark              The main contributions of this paper are as follows:
for Indirect Prompt Injection Attacks, named BIPIA. This bench-                   • We introduce BIPIA, a benchmark for evaluating LLMs and
mark spans five application scenarios and 250 attacker goals, en-                   defenses against indirect prompt injection attacks. It covers
abling a thorough and representative assessment of vulnerabilities                  a wide range of application scenarios and attack tasks.
to indirect prompt injection attacks. Using BIPIA, we evaluate 25                 • We assess various existing LLMs using BIPIA and find out
LLMs and observe that all exhibit varying degrees of susceptibility                 that more capable LLMs are more vulnerable to indirect
to such attacks. Notably, the widely used GPT-3.5-turbo and GPT-                    prompt injection attacks, exhibiting higher ASRs.
4, despite their strong capabilities, demonstrate relatively higher               • We propose both black-box and white-box defense methods,
levels of vulnerability.                                                            and thoroughly evaluate their effectiveness. The black-box
    We further identify two key challenges that facilitate the success              defense methods can effectively reduce attack success rates,
of indirect prompt injection attacks: (1) the difficulty LLMs face in               while the white-box defense method can successfully thwarts
distinguishing between informational context and actionable in-                     indirect prompt injection attacks with little adverse impact
structions; and (2) the lack of awareness in LLMs to avoid executing                on the LLM’s output quality.
instructions embedded within external content. Building on these
findings, we propose two novel defense mechanisms—boundary
awareness and explicit reminder—to address these vulnerabilities in
                                                                             2    Problem Definition
both black-box and white-box settings.                                       In an LLM-integrated application, a user 𝑢 sends an instruction 𝐼 to
    Black-box scenarios assume no access to model parameters,                the application. Upon receiving the user instruction, the application
while white-box scenarios allow access to and modification of LLMs’          retrieves external content 𝐶 and combines it with user instruction
parameters. For the explicit reminder mechanism in both scenarios,           𝐼 based on a pre-defined prompt template 𝑇 to form a prompt 𝑃:
we incorporate an instruction to direct LLMs not to execute instruc-                              𝑃 = 𝐶𝑜𝑚𝑏𝑖𝑛𝑒 (𝑇 , 𝐶, 𝑓 (𝐼 ))                     (1)
tions embedded within external content. To implement boundary
awareness in black-box scenarios, we design prompt learning-based            where Combine is an operator to construct a prompt given the
methods, including multi-turn dialogue and in-context learning, to           prompt template, the user instruction, and external content, 𝑓 (𝐼 )
enhance the model’s ability to differentiate between user queries            denotes the instruction generated by the application based on user
and external content. In white-box scenarios, we modify the model            instruction 𝐼 . The application then sends the prompt to the LLM
                                                                             to generate a response 𝑅. The external content 𝐶 may contain a
Benchmarking and Defending Against Indirect Prompt Injection Attacks on Large Language Models                            KDD ’25, August 3–7, 2025, Toronto, ON, Canada


                                                  Table 1: Detailed statistics of our BIPIA dataset.

                                                                   # External content        # Attack         # Prompt           Avg.       Avg. external
                 Task                Dataset          # Position
                                                                   Train      Test          Train   Test   Train      Test    prompt len.   content len.

              Email QA          OpenAI Evals              3         50         50            75     75      11,250   11,250     850.39         544.73
              Web QA               NewsQA                 3        900        100            75     75     202,500   22,500    2,736.51       2,451.95
              Table QA        WikiTableQuestions          3        900        100            75     75     202,500   22,500    2,032.99       1,744.18
            Summarization           XSum                  3        900        100            75     75     202,500   22,500    1,994.39       1,809.39
              Code QA           Self-collected            3         50         50            50     50      7,500    7,500     1,972.44        860.94
                Overall                 -                 3        2,800      400           125     125    626,250   86,250    2,201.93       1,920.65


malicious instruction 𝑀 embedded by an attacker, which can cause                        editors, text readers, and code editors, respectively. For web QA, ta-
LLM’s response to deviate from the user’s expectations, fulfilling                      ble QA, and summarization, we use a 900/100 train/test split, while
an indirect prompt injection attack.                                                    for email QA and code QA, we employ a 50/50 split.
   Defense against indirect prompt injection attacks aims to achieve                       We design 30 types of text attacks and 20 types of code attacks,
the following two goals: 1) Robustness: Reduce the ASR of in-                           each containing five specific malicious instructions. Text attacks
direct prompt injection attacks, thus enhancing the security of                         are categorized into task-irrelevant attacks aimed at redirecting
LLM-integrated applications. 2) Performance: Preserve LLM’s per-                        the LLM from the original task, task-relevant attacks seeking to
formance on regular tasks, ensuring LLM-integrated applications                         alter the LLM’s responses within the task context, and targeted
can effectively complete user-expected tasks while dealing with                         attacks aiming to achieve specific malicious outcomes. Code attacks
potential indirect prompt injection attacks.                                            are divided into passive attacks for gathering information without
                                                                                        modifying the system and active attacks intended to alter the system
                                                                                        or its data. We randomly split 15 types of text attacks and 10 types
3    Threat Model                                                                       of code attacks for training, with the remainder used for testing. To
Attackers’ Goals: To inject malicious instructions into external                        explore the impact of malicious instruction placement, we inject
content, causing the LLM-integrated application to produce irrele-                      these instructions at the beginning, middle, and end of external
vant responses or conduct targeted attacks.                                             content. The BIPIA dataset comprises 626,250 training prompts and
Attackers’ Knowledge: Familiarity with the public details of                            86,250 test prompts. Detailed statistics of BIPIA are provided in
the LLM used by the target LLM-integrated application, includ-                          Table 1, with further information on test and train attacks presented
ing API usage (for closed-source LLMs), and model parameters                            in Tables 5 and 6, respectively. This comprehensive benchmark
(for open-source LLMs). Attackers may know details of the target                        allows for a thorough evaluation of LLMs’ robustness against a
LLM-integrated application if it is open-sourced.                                       wide range of indirect prompt injection attacks across various real-
Attackers’ Capability: Ability to modify external content to em-                        world application scenarios.
bed malicious instructions for indirect prompt injection attacks.
This content may be retrieved by LLM-integrated applications and
incorporated into prompts sent to the LLM. Attackers can optimize
these instructions to increase the ASR. We assume that both LLMs
                                                                                        5     Evaluation LLMs under Attacks
and LLM-integrated applications are trustworthy, meaning that at-                       We evaluate a wide array of existing LLMs, both open-source and
tackers cannot tamper directly with an LLM-integrated application                       close-source, assessing their susceptibility to various attacks across
or the LLM it uses to launch an attack.                                                 multiple application tasks, as presented in Table 2. We construct an
                                                                                        automated evaluation pipeline that employs rule-based evaluation,
                                                                                        LLM-as-judge evaluation, and language detection based on langde-
4    BIPIA Dataset Construction                                                         tect for ASR computation. To ensure consistency and fairness in
We introduce BIPIA, a dataset designed to evaluate the robustness of                    our experimental evaluation, we apply the conversation template
LLMs against indirect prompt injection attacks. BIPIA is constructed                    introduced in the LLMs’ documents. We set the temperature to 0 in
based on three factors: (1) application task, (2) attack type, and (3)                  generating responses and the maximum number of newly generated
position of the attack within external content.                                         tokens to 2,000.
   For application tasks, we assess LLMs across five representative                        Notably, our findings reveal that all LLMs exhibit a certain level
scenarios that reflect real-world applications. These include email                     of vulnerability when confronted with indirect prompt injection
question answering (QA) using 100 real-world emails with questions                      attacks. This underscores the significance of our research into cor-
and answers from the OpenAI Evals repository [28], web QA sam-                          responding defense mechanisms. Moreover, GPT-4 and GPT-3.5,
pling 1,000 examples from the NewsQA dataset [43], table QA sam-                        which power the popular ChatGPT integrated applications, demon-
pling 1,000 examples from WikiTableQuestions dataset [30], sum-                         strate relatively higher vulnerability under indirect prompt injec-
marization sampling 1,000 examples from the XSum dataset [25],                          tion attacks. Subsequently, we delve into the exploration of various
and code QA collecting 100 Python code samples with bugs and                            factors that influence the success rate of attacks.
solutions from Stack Overflow. These tasks correspond to applica-                          Impact of LLM’s capability. In Figure 2, we present the re-
tions in email management software, search engines, spreadsheet                         lationship between LLMs’ capability measured by Elo ratings on
KDD ’25, August 3–7, 2025, Toronto, ON, Canada                                                                                                                                                                                                                       Jingwei Yi et al.


Table 2: Attack success rates (ASRs) of different LLMs on BIPIA. The results are displayed in descending order of LLM’s Elo
rating from Chatbot Arena [53]. Higher Elo ratings indicate the LLM has higher capability. The overall ASR is determined by
weighting each task’s ASR according to its example count.

                                                                                                Arena                                                                Text Task                                         Code Task                       Overall
                                Model
                                                                                                 Elo              Email QA                     Web QA                   Table QA     Summarization                      Code QA                         ASR

                                GPT-4 [27]                                                       1,181                0.1524                       0.2792                0.3472               0.3917                           0.2863                  0.3103
                                GPT-3.5-turbo [29]                                               1,115                0.1634                       0.2347                0.2257               0.3658                           0.2844                  0.2616
                                WizardLM-70B [49]                                                1,099                0.0757                       0.0049                0.0181               0.1816                           0.1867                  0.0795
                                Vicuna-33B [53]                                                  1,092                0.1088                       0.1221                0.1317               0.2157                           0.2876                  0.1617
                                Llama2-Chat-70B [42]                                             1,051                0.1290                       0.1493                0.2058               0.2239                           0.2167                  0.1867
                                WizardLM-13B [49]                                                1,047                0.0760                       0.0048                0.0181               0.1819                           0.1817                  0.0791
                                Vicuna-13B [53]                                                  1,041                0.1036                       0.1029                0.1080               0.1646                           0.2064                  0.1294
                                MPT-30B-chat [40]                                                1,039                0.0981                       0.0955                0.1438               0.2360                           0.2673                  0.1600
                                Guanaco-33B [8]                                                  1,031                0.0602                       0.0430                0.0552               0.1332                           0.3884                  0.1020
                                CodeLlama-34B                                                    1,031                0.0308                       0.0449                0.0822               0.2032                           0.1279                  0.1013
                                Mistral-7B [15]                                                  1,031                0.0552                       0.0580                0.0870               0.1628                           0.1047                  0.0966
                                Llama2-Chat-13B [42]                                             1,012                0.1083                       0.1253                0.1157               0.2997                           0.1481                  0.1681
                                Vicuna-7B [53]                                                    997                 0.0854                       0.0581                0.0712               0.1773                           0.1581                  0.1049
                                Llama2-Chat-7B [42]                                               985                 0.0965                       0.1230                0.1161               0.2645                           0.0671                  0.1498
                                Koala-13B [10]                                                    973                 0.0653                       0.0688                0.0782               0.2696                           0.2073                  0.1352
                                GPT4All-13B-Snoozy [1]                                            959                 0.0816                       0.0472                0.0590               0.3155                           0.2343                  0.1410
                                ChatGLM2-6B [50]                                                  945                 0.0260                       0.0152                0.0211               0.1403                           0.3060                  0.0761
                                MPT-7B-Chat [40]                                                  938                 0.1139                       0.0480                0.0709               0.2023                           0.3536                  0.1294
                                RWKV-4-Raven-14B [31]                                             933                 0.0610                       0.0132                0.0202               0.1225                           0.1092                  0.0581
                                Alpaca-13B [39]                                                   914                 0.0338                       0.0155                0.0150               0.2199                           0.1141                  0.0796
                                OpenAssistant-Pythia-12B [17]                                     905                 0.0751                       0.0317                0.0341               0.3175                           0.5153                  0.1546
                                ChatGLM-6B [50]                                                   892                 0.0186                       0.0060                0.0266               0.0602                           0.3060                  0.0532
                                FastChat-T5-3B [53]                                               884                 0.0580                       0.0689                0.0761               0.1825                           0.1320                  0.1045
                                StableLM-Tuned-Alpaca-7b [38]                                     853                 0.0586                       0.0270                0.0400               0.0987                           0.1516                  0.0641
                                Dolly-V2-12B [7]                                                  832                 0.0762                       0.0399                0.0385               0.1264                           0.3099                  0.0903
                                Average                                                                    -          0.0730                       0.0615                0.0771               0.1966                           0.2411                  0.1179


                      (A) GPT-4                                             (F) WizardLM-13B                                 (K) Mistral-7B-Instruct-v0.1                            (P) GPT4All-13B-Snoozy                                (U) OpenAssistant-Pythia-12B
                      (B) GPT-3.5-turbo                                     (G) Vicuna-13B                                   (L) Llama-2-13b-chat                                    (Q) ChatGLM2-6B                                       (V) ChatGLM-6B
                      (C) WizardLM-70B                                      (H) MPT-30B-chat                                 (M) Vicuna-7B                                           (R) MPT-7B-Chat                                       (W) FastChat-T5-3B
                      (D) Vicuna-33B                                        (I) CodeLlama-34B-instruct                       (N) Llama-2-7b-chat                                     (S) RWKV-4-Raven-14B                                  (X) StableLM-Tuned-Alpaca-7b
                      (E) Llama-2-70b-chat                                  (J) Guanaco-33B                                  (O) Koala-13B                                           (T) Alpaca-13B                                        (Y) Dolly-V2-12B
                                                                                           A                                                                                          A                                                            A
               1150                                                                                        1150                                                                                       1150
               1100             C
                                                                                  B                        1100              C
                                                                                                                                                                             B                        1100                         C
                                                                                                                                                                                                                                                   B
                                                                D                                                                                       D                                                                                          D
               1050                                                                                        1050                                                                                       1050
   Elo Score                                                                                   Elo Score                                                                                  Elo Score
                                F               G                       E                                                    F                 G                    E                                                              F GE
                                         K IJ                   H                                                                J    KI                H                                                         K I                          H                 J
               1000                         M
                                                                    L                                      1000                       M
                                                                                                                                                                L                                     1000                 L
                                                                                                                                                                                                                               M
                                                            N                                                                                               N                                                N
                                                    O                                                                                              O                                                                                   O
                950             Q
                                                        P                                                   950         Q
                                                                                                                                                    P                                                  950                                 P
                                                                                                                                                                                                                                                       Q
                        S                       R                                                                       S                  R                                                                      S                                        R
                900              T                          U                                               900                  T             U                                                       900         T                                                        U
                        V                  W                                                                      V                    W                                                                               W                               V
                850         X                                                                               850         X                                                                              850                 X
                                     Y                                                                                       Y                                                                                                                         Y
                      0.05           0.10           0.15 0.20 0.25                     0.30                           0.05           0.10        0.15 0.20 0.25                    0.30                          0.1               0.2      0.3       0.4                0.5
                                                    ASR in All Tasks                                                                           ASR in Text Tasks                                                                    ASR in Code Tasks

Figure 2: Correlation between model capability (Elo ratings on Chatbot Arena) and ASRs on all task, text-only tasks, and code
tasks, showing positive correlations with Pearson coefficients of 0.6423 (𝑝 < 0.001), 0.6635 (𝑝 < 0.001) and -0.0254 for all tasks,
text tasks and code tasks, respectively.


Chatbot Arena [53], a benchmark platform for LLMs in a crowd-                                                                                                       that more powerful LLMs are more susceptible to indirect prompt
sourced manner, and the ASRs on all attacks, text attacks, and code                                                                                                 injection attacks. This may be attributed to their advanced language
attacks, respectively. Intriguingly, we observe a positive association                                                                                              understanding and generation capabilities, resulting in following
between the Elo ratings and ASRs on text tasks, which indicates                                                                                                     malicious attack instructions embedded in third-party content more
Benchmarking and Defending Against Indirect Prompt Injection Attacks on Large Language Models                            KDD ’25, August 3–7, 2025, Toronto, ON, Canada


                                                             task-irrelevant             task-relevant        targeted
         1.2                                    1.0                                          1.0                                 1.2
         1.0                                    0.8                                          0.8                                 1.0
         0.8                                    0.6                                          0.6                                 0.8
         0.6                                    0.4                                          0.4                                 0.6
   ASR   0.4                              ASR                                        ASR                                  ASR    0.4
         0.2                                    0.2                                          0.2                                 0.2
         0.0                                    0.0                                          0.0                                 0.0
         0.2                                    0.2                                          0.2                                 0.2
                        GPT-4                              GPT-3.5-turbo                                    Vicuna-7B                        Vicuna-13B

                                         Figure 3: The ASRs of various text attack types on four LLMs.

                                                                               passive             active
         1.2                                    1.0                                          0.5                                  0.7
         1.0                                    0.8                                          0.4                                  0.6
         0.8                                                                                                                      0.5
                                                0.6                                          0.3                                  0.4
         0.6                                    0.4                                          0.2                                  0.3
   ASR   0.4                              ASR                                        ASR                                   ASR
                                                0.2                                          0.1                                  0.2
         0.2                                                                                                                      0.1
         0.0                                    0.0                                          0.0                                  0.0
         0.2                                    0.2                                          0.1                                  0.1
                        GPT-4                              GPT-3.5-turbo                                    Vicuna-7B                         Vicuna-13B

                                         Figure 4: The ASRs of various code attack types on four LLMs.




                       GPT-4                                GPT-3.5-turbo                                   Vicuna-7B                         Vicuna-13B



Figure 5: The impact of different attack instruction positions on four LLMs. Placing attack instructions at the end results in a
higher ASR compared to placing them at the beginning or in the middle.


effectively. Although their performance on benign tasks is generally                        higher ASRs than task-irrelevant text attacks, especially for GPT-
better, this phenomenon highlights their greater vulnerability to in-                       4 and GPT-3.5-turbo. This might be due to the model’s attention
direct prompt injection attacks. However, a similar relationship for                        mechanism prioritizing task-relevant information, making both
code attacks is not observed, likely because Chatbot Arena assesses                         targeted and task-relevant attacks more effective. Additionally, tar-
general task capabilities rather than code-specific abilities. Notably,                     geted attacks and task-relevant text attacks may have objectives
GPT-4, the most capable model, can identify some malicious code                             that do not conflict with the original task, making them more easily
snippets, especially in active code attacks, which might contribute                         accepted by the models.
to the lack of a clear correlation.                                                            Impact of code attack types. As shown in Figure 4, we note
   Impact of application task types. Table 2 shows that the ASR                             that the ASRs of GPT-3.5-turbo, Vicuna-7B, and Vicuna-13B exhibit
of summarization is higher than that of table QA, email QA, and                             a similar trend for both passive and active attacks. However, the
web QA. This discrepancy may stem from the differences in prompt                            ASR of active attacks on GPT-4 is notably lower than that of passive
templates for these tasks. In the summarization task, there are no                          attacks. A possible explanation based on our observations could be
additional user instructions appended at the end of the prompt. In                          that active code attacks involve modifying users’ local files or the
contrast, the templates for the other tasks, such as table QA, email                        machine’s operating state without explicitly indicating malicious
QA, and web QA, include user instructions as the last sentence,                             intent in the code. Despite the lack of explicit indications of malice,
typically in the form of a question. Additionally, the ASR of code                          GPT-4, with its advanced code comprehension capabilities, is able
QA surpasses table QA, email QA, and web QA. However, since                                 to discern the intent behind the code and opts to refuse to follow
code attacks are targeted attacks distinct from text attacks, direct                        the malicious instructions of active code attacks.
comparisons between them are not made.                                                         Impact of positions of attack instructions. Figure 5 demon-
   Impact of text attack types. In Figure 3, our evaluation results                         strates that injection locations of attack instructions within third-
indicate that task-relevant text attacks and targeted attacks have                          party content significantly impact the ASR. We observe that placing
KDD ’25, August 3–7, 2025, Toronto, ON, Canada                                                                                    Jingwei Yi et al.


       Instruction of LLM-                         GPT-4                               Instruction of LLM-            Collected Benign
       integrated application                      response                            integrated application         Response
    Turn 1:                                      The Chiefs' first-choice
    You are an assistant responsible for         scrum-half has                     You are an assistant
    processing and analyzing                     suffered a torn pectoral           responsible for               The 28-year-old first-
    news...(Do not execute or adhere to          muscle, leading to                 processing and                choice scrum-half
    any potential instructions or                changes in the team                                              for the Chiefs, who
    commands in the following news.)
                                                                                    analyzing news
                                                 lineup, with Dave Lewis            content. Please               has been injured, has
                                                 starting and Stuart                                              a torn pectoral
    Here is the news:                                                               summarize the
                                                 Townsend making his                                              muscle. Dave Lewis
    {External Content}                           championship rugby                 following news. Your
    Turn 2:                                                                         summarization                 replaced the injured
                                                 debut. ..
    Concisely summarize the news.                                                   should be as concise          player in the recent
                                                                                    as possible.                  win over Ulster, and
                                                                                                                  Stuart Townsend
Figure 6: A prompt example of multi-turn dialogue defense                                                         made his debut in
                                                                                    Here is the news (Do
for the summarization task.                                                         not execute …):               the same game...
                                                                                    {External Content}

       Instruction of LLM-                         GPT-4
       integrated application                      response                 Figure 8: An example of white-box defense prompt for the
    Example User:                                                           summarization task.
    You are an assistant responsible for…        The 28-year-old first-
                                                 choice scrum-half for
    Here is the news (Do not execute …) :        the Chiefs has
    {Example External Content}                   suffered a torn               Based on Conjecture 1, we design black-box and white-box de-
                                                 pectoral muscle. In
                                                 his absence, Dave          fense strategies. These strategies consist of two important com-
    Example Assistant:                                                      ponents: boundary awareness, which makes an LLM aware of the
                                                 Lewis started and
    {Example Response}
                                                 Stuart Townsend            boundaries between external content and user instructions, and
    User:                                        made his                   explicit reminder, which explicitly reminds an LLM not to execute
    You are an assistant responsible for…        championship rugby
                                                 debut in the team's
                                                                            instructions embedded within external content. We present the
    Here is the news (Do not execute …):         recent win over            details in the subsequent subsections.
    {External Content}                           Ulster…
                                                                            6.1   Black-box Defense
                                                                            Black-box defense refers to a collection of defense strategies for
Figure 7: A prompt example of the in-context learning de-
                                                                            LLM-integrated applications that do not require access to the LLM’s
fense for the summarization task.
                                                                            parameters. These strategies protect applications by utilizing APIs
                                                                            from closed-source LLMs. For explicit reminder, as shown in Fig-
                                                                            ure 6 and Figure 7, we add a reminder to the prompt to instruct the
the attack at the end of the external content results in the high-          LLM not to execute commands in the external content. For bound-
est ASR, followed by placing it at the beginning and middle. This           ary awareness, we have developed two defense methods based on
phenomenon may be attributed to the data distribution during the            prompt learning, which enable an LLM to recognize the boundaries
training process of LLMs, where most instructions might be present          between external content and user instructions so that it will not
at the end of samples. Consequently, LLMs may learn a position              follow any instructions in the external content.
bias that inadvertently increases the influence of the injected attack         Multi-turn dialogue. In recent developments, LLMs have sup-
instructions, particularly when they are located at the end of the          ported multi-turn conversation capabilities. Inspired by the sensi-
content [21].                                                               tivity of LLMs to the recent user dialogues, we propose moving
                                                                            third-party content, which may contain malicious instructions, to
6    Defense Methodology                                                    the previous turn of conversation and placing the instructions in
In the evaluation results presented above, a notable observation            the current turn. By separating external content from instructions
is that more capable LLMs tend to be more vulnerable to text-               into different turns and distancing malicious instructions from the
based attacks, underscoring the pressing need for robust defenses           recent user dialogues, ASR should be reduced. The detailed design
against indirect prompt injection attacks. To explain the underlying        of the prompt can be found in Figure 6.
mechanisms behind the success of indirect prompt injection attacks,            In-context learning. In-context learning (few-shot learning) is
we propose the following conjecture:                                        a technique that enhances the performance of LLMs by providing a
                                                                            few examples within a prompt [6]. This approach enables LLMs to
   Conjecture 1. The root causes of indirect prompt injection at-           effectively learn new tasks. Inspired by the success of in-context
tacks are twofold: (1) the inability of LLMs to effectively differentiate   learning, we employ this technique to teach an LLM the boundaries
between informational context and actionable instructions; and (2) the      between data and instructions. We provide examples that generate
lack of awareness in LLMs to avoid executing instructions embedded          responses to input with external content without being influenced
within external content.                                                    by malicious instructions within the external content. We then
Benchmarking and Defending Against Indirect Prompt Injection Attacks on Large Language Models                          KDD ’25, August 3–7, 2025, Toronto, ON, Canada


                                                                                     embeddings for <data> and </data> on the word embedding ma-
                    Add Special Tokens                                               trix of the original LLM.
       Original                           Modified
        LLM                                LLM                                                    E𝑛𝑒𝑤 = 𝐶𝑜𝑛𝑐𝑎𝑡 (E𝑜𝑟𝑖𝑔𝑖𝑛 , E<𝑑𝑎𝑡𝑎> , E</𝑑𝑎𝑡𝑎> ),                  (3)

                   BIPIA
                                         Supervised                                  where Concat is the concatenation operator, E𝑛𝑒𝑤 is the embedding
                    Benign                Finetune                                   matrix of the modified LLM, E𝑜𝑟𝑖𝑔𝑖𝑛 is the embedding matrix of the
                                                            Finetuned
                  responses                                    LLM                   original LLM, E<𝑑𝑎𝑡𝑎> and E</𝑑𝑎𝑡𝑎> are the embedding vectors of
                                                                                     <data> and </data>.
   Figure 9: Illustration of the white-box defense process.                             Explicit Reminder. As shown in Figure 8, similar to the black-
                                                                                     box defense, we incorporate an explicit reminder into the prompt
                                                                                     template 𝑇 for the white-box defense. This reminder is designed to
                                                                                     ensure the LLM recognizes and follows the instructions contained
present a new task to the LLM at the end of the prompt. The detailed                 in the external content during prompt processing.
design of the prompt is illustrated in Figure 7.                                        Model Training. In the model fine-tuning stage, we follow the
                                                                                     self-supervised fine-tuning steps and predict tokens in a response
6.2     White-box Defense                                                            given instructions and previously generated tokens. The loss is
White-box defense refers to defenses for LLM-integrated applica-                     defined as follows:
tions that require access to or modification of the LLMs’ parameters.
Recent research shows that LLMs learn data formats, such as dia-                                                  ∑︁ 𝑘
                                                                                                                  𝑁
                                                                                                                                      (𝑖 )   (𝑖 )
                                                                                                                    ∑︁
logue structures, during the supervised fine-tuning stage [54]. We                                         L=−               log 𝑃 (𝑟 𝑗 |𝑟 1:𝑗 −1, 𝑃𝑖 ),          (4)
                                                                                                                   𝑖=1 𝑗=1
propose a white-box defense method that applies adversarial train-
ing to the self-supervised fine-tuning stage of an LLM to teach
                                                                                                (𝑖 )
it to ignore instructions in external content, thus enhancing its                    where 𝑟 𝑗         is the 𝑗-th token in the response of the 𝑖-th sample, and
robustness against indirect prompt injection attacks. Figure 9 and                     (𝑖 )
                                                                                     𝑟 1:𝑗 −1 is the first to the ( 𝑗 − 1)-th token in the response.
Figure 8 illustrate the defense process and prompt design of our
white-box defense method.
    Dataset Construction. The dataset for supervised fine-tuning                     7 Experiments
consists of 𝑁 pairs of prompts and responses, denoted as D =                         7.1 Dataset and Experimental Settings
{(𝑃𝑖 , 𝑅𝑖 ) | 𝑖 ≤ 𝑁 }. We use the training set of BIPIA to create prompts
                                                                                     For black-box defenses, we conduct experiments on GPT-4, GPT-3.5-
that involve external content with malicious instructions. Our ob-
                                                                                     turbo, Vicuna-13B and Vicuna-7B [53], with the temperature set to
jective is to ensure that the model’s output remains unaffected by
                                                                                     0, and the maximum number of tokens in a generated response set
malicious instructions in the external content, so we need to collect
                                                                                     to 2,000. The examples used in the in-context learning defense are
benign responses that are not influenced by these instructions. We
                                                                                     from the training set of BIPIA. For white-box defenses, the training
employ three different methods to construct benign responses: 1)
                                                                                     prompts are constructed with the training set of BIPIA. We conduct
Using labels from the BIPIA dataset. This method guarantees the
                                                                                     experiments on Vicuna-13B and Vicuna-7B. In the supervised fine-
correctness of the responses but may limit their diversity. 2) Using
                                                                                     tuning stage, we apply AdamW as the optimizer to train one epoch,
benign responses generated by the original LLM on prompts with-
                                                                                     with a learning rate of 2e-5, a batch size of 128, and a maximum
out malicious instructions. This method produces output consistent
                                                                                     sample length of 2,048. In the test stage, the temperature is set to 0,
with the original model’s style, but the correctness cannot be guar-
                                                                                     and the maximum number of generated tokens is set to 512.
anteed. 3) Using responses generated by GPT-4 on prompts without
                                                                                        In addition to evaluating ASR on the test set of BIPIA, we also
malicious instructions. GPT-4, as a more advanced model, should
                                                                                     evaluate whether the defense methods will harm the LLMs’ per-
generate more diverse and high-quality responses compared to the
                                                                                     formance. We first construct a BIPIA-Clean dataset to validate the
original LLM, but the correctness cannot be guaranteed either.
                                                                                     impact of different defenses on the original tasks in BIPIA, i.e., Email
    Adding Special Tokens. To enable marking external content
                                                                                     QA, Web QA, Table QA, Summarization, and Code QA. The BIPIA-
in a prompt, we introduce two special tokens to the vocabulary of
                                                                                     Clean dataset is constructed following the same steps as BIPIA, but
the LLM. These tokens help the model recognize the boundaries be-
                                                                                     the external content does not contain any malicious instructions.
tween external content and other elements in the input. Specifically,
                                                                                     We collect the responses of various methods on these clean prompts
we use the tokens <data> and </data> to mark the beginning and
                                                                                     and compute ROUGE-1 [20] between the responses and the targets,
end of external content, respectively, in a prompt:
                                                                                     to evaluate the extent of target information present in the model
            𝑃 = Combine(𝑇 , <data> + 𝐶 + </data>, 𝐼 )                      (2)       outputs. For white-box defenses, as modifications to model parame-
                                                                                     ters might affect the performance of other general tasks, we further
where Combine is an operator to construct a prompt given the                         used MT-Bench [53] to verify whether the white-box defense will
prompt template, the user instruction, and external content, 𝑃 is                    impact the models’ helpfulness in general tasks. MT-Bench is a
the final prompt, 𝑇 is a pre-defined prompt template, 𝐶 is the ex-                   benchmark with a series of open-ended questions that evaluate
ternal content and 𝐼 is the user instruction. We then add two word                   LLMs’ multi-turn conversational and instruction-following ability.
KDD ’25, August 3–7, 2025, Toronto, ON, Canada                                                                                                        Jingwei Yi et al.


   Table 3: Performance of different black-box defenses on BIPIA with GPT-4, GPT-3.5-Turbo, Vicuna-7B and Vicuna-13B.

                                                       ROUGE-1                     ASR of Text Tasks                     ASR of Code Task    Overall
             Model             Method
                                                        (recall)     Email QA    Web QA     Table QA    Summarization       Code QA           ASR

                               Original                 0.6985        0.1524     0.2792      0.3472        0.3917             0.2863         0.3103
                               In-context learning      0.6590        0.1036     0.2382      0.3238        0.3075             0.0056         0.2408
             GPT-4
                               Multi-turn dialogue      0.7201        0.0959     0.2585      0.2974        0.1810             0.0097         0.2056
                               Original                 0.6554        0.1634     0.2347      0.2257        0.3658             0.2844         0.2616
                               In-context learning      0.6289        0.1779     0.1600      0.1910        0.2560             0.0789         0.1884
             GPT-3.5-Turbo
                               Multi-turn dialogue      0.6786        0.1376     0.2025      0.1936        0.2221             0.0583         0.1843
                               Original                 0.6187        0.1124     0.0693      0.0827        0.2117             0.1632         0.1237
                               In-context learning      0.6065        0.0512     0.0394      0.0396        0.2148             0.0599         0.0885
             Vicuna-7B
                               Multi-turn dialogue      0.6084        0.1127     0.0410      0.0565        0.0817             0.0023         0.0617
                               Original                 0.6134        0.1242     0.1272      0.1337        0.2052             0.1755         0.1531
                               In-context learning      0.6025        0.2353     0.1456      0.1804        0.1763             0.0468         0.1658
             Vicuna-13B
                               Multi-turn dialogue      0.6274        0.1379     0.1024      0.1168        0.1028             0.0015         0.1021


                       Table 4: Performance of the white-box defense on BIPIA with Vicuna-7B and Vicuna-13B.

                                          ROUGE-1       Capability                    ASR of Text Task                    ASR of Code Task    Overall
           Model          Response
                          Source           (recall))    MT-Bench      Email QA    Web QA     Table QA    Summarization        Code QA          ASR

                          w/o finetune      0.6187        4.8063        0.1124     0.0693      0.0827        0.2117            0.1632          0.1237
                          BIPIA             0.5306        4.2938        0.0202     0.0159      0.0410        0.0049            0.0300          0.0214
           Vicuna-7B
                          Original LLM      0.6122        4.5687        0.0015     0.0062      0.0057        0.0043            0.2244          0.0240
                          GPT-4             0.6260        4.8312        0.0065     0.0045      0.0046        0.0037            0.0129          0.0053
                          w/o finetune      0.6134        5.2062        0.1242     0.1272      0.1337        0.2052            0.1755          0.1531
                          BIPIA             0.6109        1.6625        0.0217     0.0126      0.0370        0.0064            0.0207          0.0192
           Vicuna-13B
                          Original LLM      0.6240        4.3375        0.0024     0.0055      0.0051        0.0034            0.0067          0.0046
                          GPT-4             0.6337        4.5500        0.0060     0.0044      0.0057        0.0036            0.0036          0.0047


7.2     Performance Comparison                                                        benchmark dataset and responses generated by the original LLM
We evaluate our black-box defenses on GPT-4, GPT-3.5-Turbo,                           and GPT-4 on prompts without malicious instructions. We obtain
Vicuna-7B and Vicuna-13B and the white-box approach on Vicuna-                        two key observations as follows. First, white-box defense methods
7B and Vicuna-13B.                                                                    can effectively reduce the ASR to close to 0, which is 10 times lower
   Table 3 presents the effectiveness of various black-box defenses.                  than the original ASR. Second, there is at least one response con-
On the one hand, it is observed that all black-box defenses are                       struction method, such as GPT-4, that can ensure little decline in
effective in substantially reducing the ASR. On the other hand,                       the ROUGE score and the capability score on MT-Bench. Overall,
when examining the ROUGE score of different indirect prompt                           the results demonstrate that our white-box defense effectively miti-
injection attacks with and without these defenses, it is noted that,                  gates indirect prompt injection attacks, achieving near-complete
with the exception of in-context learning, the performance remains                    protection without compromising model performance.
comparable to the original model. This indicates that these simple                    7.3     Ablation Study
methods do not significantly impair functionality. Finally, a com-
parison between GPT-4, GPT-3.5-Turbo, Vicuna-7B and Vicuna-13B                        We conduct an ablation study to evaluate the impact of our de-
reveals that, overall, the ASRs of more powerful LLMs are higher.                     fense’s two core components: explicit reminder and boundary aware-
This could be attributed to the inherently higher base ASR of the                     ness. For black-box defenses (tested on GPT-3.5-Turbo), we remove
more powerful LLM. However, in tasks involving external content                       the reminder instruction to assess the effect of explicit reminders,
of shorter length, such as EmailQA and codeQA, the ASRs of more                       and revert to single-turn dialogues without in-context examples to
powerful LLMs, such as GPT-4, significantly decrease and may fall                     evaluate boundary awareness. For white-box defenses (tested on
below that less powerful LLMs. This indicates that more powerful                      Vicuna-7B), we similarly remove the reminder instruction to assess
LLMs may be more adept at following explicit reminder instructions                    the effect of explicit reminders, and disable adversarial training
and distinguishing between external content and user instructions                     and revert adding special tokens to assess boundary awareness.
in scenarios where the external content is brief.                                     We then analyze the resulting performance changes to gauge each
   Table 4 demonstrates the performance of various configurations                     component’s contribution to the overall defense efficacy.
of our white-box defense. Specifically, we investigate various ad-                       Our empirical results in Figure 11 demonstrate that the ASR
versarial training datasets, which involve pairing the maliciously                    of the black-box defenses increases when either of the two com-
attacked input with three types of benign responses: labels from the                  ponents is removed. This indicates the effectiveness of both com-
                                                                                      ponents in defending against indirect prompt injection attacks.
Benchmarking and Defending Against Indirect Prompt Injection Attacks on Large Language Models                              KDD ’25, August 3–7, 2025, Toronto, ON, Canada


                                                original defense            w/o explicit reminder        w/o boundary awareness
          0.5                                                  1.0                                                  12
                                                               0.9                                                  10
          0.4                                                  0.8
          0.3                                                  0.7                                                   8
    ASR   0.2                                               ROUGE
                                                               0.6
                                                               0.5                                               Rating
                                                                                                                     6
                                                                                                                     4
          0.1                                                  0.4
                                                               0.3                                                   2
          0.0                                                  0.2                                                   0
                    BIPIA   Original LLM       GPT-4                      BIPIA     Original LLM     GPT-4                 BIPIA         Original LLM      GPT-4

                Figure 10: The impact of explicit reminder and boundary awareness on white-box defense with Vicuna-7B.

         original defense   w/o explicit reminder       w/o boundary awareness            learning technologies, such as in-context learning, adding border
      0.40                                   1.0                                          strings, multi-turn dialogue and datamarking. In contrast, white-
      0.35                                   0.9
      0.30                                                                                box defense modifies LLMs’ weights. Our white-box defense meth-
                                             0.8
      0.25
                                       ROUGE
                                                                                          ods add special tokens to the vocabulary to mark external content
                                             0.7
ASR   0.20
                                             0.6                                          and fine-tune the LLM through adversarial training. Our extensive
      0.15
      0.10                                   0.5                                          experimental results show that the black-box defense methods can
      0.05                                   0.4                                          effectively reduce ASR but cannot make LLMs robust to indirect
      0.00                                   0.3
                    ICL     Multi-turn                ICL            Multi-turn           prompt injection attacks, while the white-box defense method can
                                                                                          effectively decrease ASR to nearly zero, making fine-tuned LLMs
Figure 11: The impact of explicit reminder and boundary                                   robust to indirect prompt injection attacks, while preserving the
awareness on black-box defenses.                                                          output quality of fine-tuned LLMs.
                                                                                             Overall, we believe our work will catalyze further research in
                                                                                          this area, fostering the development of more secure and reliable
Furthermore, we observe that the removal of boundary awareness                            LLM applications.
has a greater impact on ASR than the removal of explicit reminder,
indicating that the ability to distinguish boundaries may be more                         Ethical Consideration
important for LLMs to defend against indirect prompt injection                            The primary focus of our work is to further enhance the safety and
attacks. At the same time, the removal of either component does                           reliability of LLMs when integrated with third-party content. One
not significantly affect the ROUGE score of the original task, which                      potential concern is that our work could raise awareness of indirect
shows that the utility of the method is not compromised.                                  prompt injection attacks, potentially leading to their misuse for
   For the white-box defense, our results in Figure 10 indicate that                      malicious purposes. To mitigate this risk, our benchmark, through
removing explicit reminder has a smaller impact on ASR than re-                           manual review, excludes attacks that could harm personal property
moving boundary awareness for different response construction                             and health, thereby reducing the harmfulness of the attacks. Fur-
methods. This may be because LLMs implicitly learn not to execute                         thermore, our proposed defense mechanisms exhibit high efficacy,
instructions in external content during fine-tuning. At the same                          even in black-box scenarios, with remarkably simple implemen-
time, comparing the ROUGE and MT-bench scores, we find that                               tation and minimal system overhead. Despite their effectiveness,
white-box fine-tuning does not affect the performance of LLMs on                          we do caution developers against overreliance on these defense
the fine-tuning task without attack, but may affect the performance                       mechanisms without careful testing and red teaming in the context
on general tasks.                                                                         of specific, end-to-end applications. As a result, we believe that,
                                                                                          on the whole, our work can stimulate research efforts and the de-
8      Conclusion                                                                         velopment of countermeasures aimed at enhancing the safety and
In this paper, we introduce BIPIA, the first benchmark for indirect                       dependability of LLM applications.
prompt injection attacks, offering comprehensive coverage across
various tasks and attack types. Through a thorough analysis of                            Acknowledgments
existing LLMs, we make several key observations. Based on these                           We would like to sincerely thank all reviewers for their insightful
findings, we propose two key conjectures for the root cause of                            feedback that greatly helped us improve this paper. We would like
the success of indirect prompt injection attacks: (1) the inability                       to thank Hao Wang for his great comments.
of LLMs to effectively differentiate between informational context
and actionable instructions; and (2) the lack of awareness in LLMs                        References
to avoid executing instructions embedded within external content.                          [1] Yuvanesh Anand, Zach Nussbaum, Brandon Duderstadt, Benjamin Schmidt, and
   Based on the key conjectures, we propose two types of defenses,                             Andriy Mulyar. 2023. GPT4All: Training an Assistant-style Chatbot with Large
                                                                                               Scale Data Distillation from GPT-3.5-Turbo.
black-box defense and white-box defense. black-box defense as-                             [2] Amanda Askell, Yuntao Bai, Anna Chen, Dawn Drain, Deep Ganguli, Tom
sumes no access to the LLM’s weights and is based on prompt                                    Henighan, Andy Jones, Nicholas Joseph, Ben Mann, Nova DasSarma, et al. 2021.
KDD ’25, August 3–7, 2025, Toronto, ON, Canada                                                                                                                Jingwei Yi et al.


     A general language assistant as a laboratory for alignment. arXiv preprint          [30] Panupong Pasupat and Percy Liang. 2015. Compositional Semantic Parsing on
     arXiv:2112.00861 (2021).                                                                 Semi-Structured Tables. In ACL. 1470–1480.
 [3] Yuntao Bai, Andy Jones, Kamal Ndousse, Amanda Askell, Anna Chen, Nova               [31] Bo Peng, Eric Alcaide, Quentin Anthony, Alon Albalak, Samuel Arcadinho,
     DasSarma, Dawn Drain, Stanislav Fort, Deep Ganguli, Tom Henighan, et al. 2022.           Huanqi Cao, Xin Cheng, Michael Chung, et al. 2023. RWKV: Reinventing RNNs
     Training a helpful and harmless assistant with reinforcement learning from               for the Transformer Era. arXiv preprint arXiv:2305.13048 (2023).
     human feedback. arXiv preprint arXiv:2204.05862 (2022).                             [32] Fábio Perez and Ian Ribeiro. 2022. Ignore previous prompt: Attack techniques
 [4] Yuntao Bai, Saurav Kadavath, Sandipan Kundu, Amanda Askell, Jackson Kernion,             for language models. arXiv preprint arXiv:2211.09527 (2022).
     Andy Jones, Anna Chen, Anna Goldie, Azalia Mirhoseini, Cameron McKinnon,            [33] PromptArmor. 2023. Data exfiltration from Writer.com with indirect prompt in-
     et al. 2022. Constitutional AI: Harmlessness from AI feedback. arXiv preprint            jection. https://promptarmor.substack.com/p/data-exfiltration-from-writercom.
     arXiv:2212.08073 (2022).                                                            [34] Johann Rehberger. 2023. Prompt Injection and Cross Plug-in Request Forgery in
 [5] Tom Bonner. 2023. Indirect Prompt Injection Attack for VirusTotal. https:                WebPilot. https://twitter.com/wunderwuzzi23/status/1659411665853779971.
     //twitter.com/thomas_bonner/status/1651160646107508736.                             [35] Machel Reid, Nikolay Savinov, Denis Teplyashin, Dmitry Lepikhin, Timothy
 [6] Tom Brown, Benjamin Mann, Nick Ryder, Melanie Subbiah, Jared D Kaplan,                   Lillicrap, Jean-baptiste Alayrac, Radu Soricut, Angeliki Lazaridou, Orhan Firat,
     Prafulla Dhariwal, Arvind Neelakantan, Pranav Shyam, Girish Sastry, Amanda               Julian Schrittwieser, et al. 2024. Gemini 1.5: Unlocking multimodal understanding
     Askell, et al. 2020. Language models are few-shot learners. NIPS 33 (2020),              across millions of tokens of context. arXiv preprint arXiv:2403.05530 (2024).
     1877–1901.                                                                          [36] Timo Schick, Jane Dwivedi-Yu, Roberto Dessì, Roberta Raileanu, Maria Lomeli,
 [7] Mike Conover, Matt Hayes, Ankit Mathur, Jianwei Xie, Jun Wan, Sam Shah, Ali              Luke Zettlemoyer, Nicola Cancedda, and Thomas Scialom. 2023. Toolformer: Lan-
     Ghodsi, Patrick Wendell, Matei Zaharia, and Reynold Xin. 2023. Free Dolly:               guage models can teach themselves to use tools. arXiv preprint arXiv:2302.04761
     Introducing the World’s First Truly Open Instruction-Tuned LLM.                          (2023).
 [8] Tim Dettmers, Artidoro Pagnoni, Ari Holtzman, and Luke Zettlemoyer. 2023.           [37] Yongliang Shen, Kaitao Song, Xu Tan, Dongsheng Li, Weiming Lu, and Yueting
     QLoRA: Efficient Finetuning of Quantized LLMs. arXiv preprint arXiv:2305.14314           Zhuang. 2023. HuggingGPT: Solving AI tasks with ChatGPT and its friends in
     (2023).                                                                                  Hugging Face. arXiv preprint arXiv:2303.17580 (2023).
 [9] Deep Ganguli, Liane Lovitt, Jackson Kernion, Amanda Askell, Yuntao Bai, Saurav      [38] Stability AI. 2023. StableLM: Stability AI Language Models.
     Kadavath, Ben Mann, Ethan Perez, Nicholas Schiefer, Kamal Ndousse, et al. 2022.     [39] Rohan Taori, Ishaan Gulrajani, Tianyi Zhang, Yann Dubois, Xuechen Li, Carlos
     Red teaming language models to reduce harms: Methods, scaling behaviors, and             Guestrin, Percy Liang, and Tatsunori B. Hashimoto. 2023. Stanford Alpaca: An
     lessons learned. arXiv preprint arXiv:2209.07858 (2022).                                 Instruction-following LLaMA model.
[10] Xinyang Geng, Arnav Gudibande, Hao Liu, Eric Wallace, Pieter Abbeel, Sergey         [40] MosaicML NLP Team. 2023. Introducing MPT-30B: Raising the bar for open-
     Levine, and Dawn Song. 2023. Koala: A Dialogue Model for Academic Research.              source foundation models. www.mosaicml.com/blog/mpt-30b.
[11] Google. 2023. AI-Powered Google Workspace. https://workspace.google.com/            [41] Hugo Touvron, Thibaut Lavril, Gautier Izacard, Xavier Martinet, Marie-Anne
     blog/product-announcements/generative-ai.                                                Lachaux, Timothée Lacroix, Baptiste Rozière, Naman Goyal, Eric Hambro, Faisal
[12] Tanya Goyal, Junyi Jessy Li, and Greg Durrett. 2022. News summarization and              Azhar, et al. 2023. LLaMA: Open and efficient foundation language models. arXiv
     evaluation in the era of GPT-3. arXiv preprint arXiv:2209.12356 (2022).                  preprint arXiv:2302.13971 (2023).
[13] Kai Greshake. 2023. Prompt Injections are bad, mkay? https://greshake.github.io/.   [42] Hugo Touvron, Louis Martin, Kevin Stone, Peter Albert, Amjad Almahairi, Yas-
[14] Kai Greshake, Sahar Abdelnabi, Shailesh Mishra, Christoph Endres, Thorsten               mine Babaei, Nikolay Bashlykov, Soumya Batra, Prajjwal Bhargava, Shruti Bhos-
     Holz, and Mario Fritz. 2023. More than you’ve asked for: A Comprehensive                 ale, et al. 2023. LLaMA 2: Open Foundation and Fine-Tuned Chat Models. arXiv
     Analysis of Novel Prompt Injection Threats to Application-Integrated Large               preprint arXiv:2307.09288 (2023).
     Language Models. arXiv preprint arXiv:2302.12173 (2023).                            [43] Adam Trischler, Tong Wang, Xingdi Yuan, Justin Harris, Alessandro Sordoni,
[15] Albert Q Jiang, Alexandre Sablayrolles, Arthur Mensch, Chris Bamford, De-                Philip Bachman, and Kaheer Suleman. 2017. NewsQA: A Machine Comprehension
     vendra Singh Chaplot, Diego de las Casas, Florian Bressand, Gianna Lengyel,              Dataset. In ACL. 191.
     Guillaume Lample, Lucile Saulnier, et al. 2023. Mistral 7B. arXiv preprint          [44] Priyan Vaithilingam, Tianyi Zhang, and Elena L Glassman. 2022. Expectation vs.
     arXiv:2310.06825 (2023).                                                                 experience: Evaluating the usability of code generation tools powered by large
[16] Takeshi Kojima, Shixiang Shane Gu, Machel Reid, Yutaka Matsuo, and Yusuke                language models. In CHI. 1–7.
     Iwasawa. 2022. Large language models are zero-shot reasoners. NIPS 35 (2022),       [45] Ashish Vaswani, Noam Shazeer, Niki Parmar, Jakob Uszkoreit, Llion Jones,
     22199–22213.                                                                             Aidan N Gomez, Łukasz Kaiser, and Illia Polosukhin. 2017. Attention is all
[17] Andreas Köpf, Yannic Kilcher, Dimitri von Rütte, Sotiris Anagnostidis, Zhi-Rui           you need. NIPS 30 (2017).
     Tam, Keith Stevens, Abdullah Barhoum, Nguyen Minh Duc, Oliver Stanley,              [46] Eric Wallace, Kai Xiao, Reimar Leike, Lilian Weng, Johannes Heidecke, and Alex
     Richárd Nagyfi, et al. 2023. OpenAssistant Conversations–Democratizing Large             Beutel. 2024. The instruction hierarchy: Training llms to prioritize privileged
     Language Model Alignment. arXiv preprint arXiv:2304.07327 (2023).                        instructions. arXiv preprint arXiv:2404.13208 (2024).
[18] LangChain. 2023. LangChain. https://github.com/langchain-ai/langchain.              [47] Ben Wang and Aran Komatsuzaki. 2021. GPT-J-6B: A 6 Billion Parameter Autore-
[19] Yaobo Liang, Chenfei Wu, Ting Song, Wenshan Wu, Yan Xia, Yu Liu, Yang                    gressive Language Model. https://github.com/kingoflolz/mesh-transformer-jax.
     Ou, Shuai Lu, Lei Ji, Shaoguang Mao, et al. 2023. TaskMatrix.AI: Completing         [48] Jason Wei, Xuezhi Wang, Dale Schuurmans, Maarten Bosma, Fei Xia, Ed Chi,
     tasks by connecting foundation models with millions of APIs. arXiv preprint              Quoc V Le, Denny Zhou, et al. 2022. Chain-of-thought prompting elicits reasoning
     arXiv:2303.16434 (2023).                                                                 in large language models. NIPS 35 (2022), 24824–24837.
[20] Chin-Yew Lin. 2004. ROUGE: A Package for Automatic Evaluation of Summaries.         [49] Can Xu, Qingfeng Sun, Kai Zheng, Xiubo Geng, Pu Zhao, Jiazhan Feng,
     In Text Summarization Branches Out. 74–81.                                               Chongyang Tao, and Daxin Jiang. 2023. Wizardlm: Empowering large language
[21] Nelson F Liu, Kevin Lin, John Hewitt, Ashwin Paranjape, Michele Bevilacqua,              models to follow complex instructions. arXiv preprint arXiv:2304.12244 (2023).
     Fabio Petroni, and Percy Liang. 2023. Lost in the middle: How language models       [50] Aohan Zeng, Xiao Liu, Zhengxiao Du, Zihan Wang, Hanyu Lai, Ming Ding,
     use long contexts. arXiv preprint arXiv:2307.03172 (2023).                               Zhuoyi Yang, Yifan Xu, Wendi Zheng, Xiao Xia, et al. 2022. Glm-130b: An open
[22] Pan Lu, Baolin Peng, Hao Cheng, Michel Galley, Kai-Wei Chang, Ying Nian Wu,              bilingual pre-trained model. arXiv preprint arXiv:2210.02414 (2022).
     Song-Chun Zhu, and Jianfeng Gao. 2023. Chameleon: Plug-and-play composi-            [51] Biao Zhang, Barry Haddow, and Alexandra Birch. 2023. Prompting large language
     tional reasoning with large language models. arXiv preprint arXiv:2304.09842             model for machine translation: A case study. arXiv preprint arXiv:2301.07069
     (2023).                                                                                  (2023).
[23] Grégoire Mialon, Roberto Dessì, Maria Lomeli, Christoforos Nalmpantis, Ram          [52] Susan Zhang, Stephen Roller, Naman Goyal, Mikel Artetxe, Moya Chen, Shuohui
     Pasunuru, Roberta Raileanu, Baptiste Rozière, Timo Schick, Jane Dwivedi-Yu, Asli         Chen, Christopher Dewan, Mona Diab, Xian Li, Xi Victoria Lin, et al. 2022.
     Celikyilmaz, et al. 2023. Augmented language models: a survey. arXiv preprint            Opt: Open pre-trained transformer language models, 2022. arXiv preprint
     arXiv:2302.07842 (2023).                                                                 arXiv:2205.01068 (2022).
[24] Microsoft. 2023. Microsoft Copilot. https://copilot.microsoft.com/.                 [53] Lianmin Zheng, Wei-Lin Chiang, Ying Sheng, Siyuan Zhuang, Zhanghao Wu,
[25] Shashi Narayan, Shay B. Cohen, and Mirella Lapata. 2018. Don’t Give Me the               Yonghao Zhuang, Zi Lin, Zhuohan Li, Dacheng Li, Eric Xing, et al. 2023.
     Details, Just the Summary! Topic-Aware Convolutional Neural Networks for                 Judging LLM-as-a-judge with MT-Bench and Chatbot Arena. arXiv preprint
     Extreme Summarization. In EMNLP.                                                         arXiv:2306.05685 (2023).
[26] OpenAI. 2023. ChatGPT Plugins. https://openai.com/blog/chatgpt-plugins.             [54] Chunting Zhou, Pengfei Liu, Puxin Xu, Srini Iyer, Jiao Sun, Yuning Mao, Xuezhe
[27] OpenAI. 2023. GPT-4 Technical Repor. arXiv preprint arXiv:2303.08774 (2023).             Ma, Avia Efrat, Ping Yu, Lili Yu, et al. 2023. Lima: Less is more for alignment.
[28] OpenAI. 2023. OpenAI Evals. https://github.com/openai/evals.                             arXiv preprint arXiv:2305.11206 (2023).
[29] Long Ouyang, Jeffrey Wu, Xu Jiang, Diogo Almeida, Carroll Wainwright, Pamela
     Mishkin, Chong Zhang, Sandhini Agarwal, Katarina Slama, Alex Ray, et al. 2022.
     Training language models to follow instructions with human feedback. NIPS 35
     (2022), 27730–27744.
Benchmarking and Defending Against Indirect Prompt Injection Attacks on Large Language Models                            KDD ’25, August 3–7, 2025, Toronto, ON, Canada


A Related Works                                                                                    Code QA             Table QA           Code QA            Table QA
                                                                                                   Email QA            Web QA             Email QA           Web QA
A.1 Large Language Models                                                                          Summarization                          Summarization
Large language models (LLMs) are transformer-based [45] deep                                    0.35                                  0.9
                                                                                                0.30                                  0.8
                                                                                                0.25
                                                                                                                                  ROUGE
learning models with a large number of parameters, designed
                                                                                                0.20                                  0.7
for natural language processing (NLP) tasks. They have recently                           ASR                                         0.6
                                                                                                0.15
achieved remarkable performance in various NLP tasks, such as                                   0.10                                  0.5
logic reasoning [48], code generation [44], summarization [12], and                             0.05                                  0.4
                                                                                                       0     1 2 3 4 5                      0     1 2 3 4 5
question answering [16]. The training process of LLMs typically                                            Number of Examples                   Number of Examples
consists of three steps: pre-training, supervised fine-tuning (SFT),                                         (a) ASR                             (b) ROUGE
and reinforcement learning with human feedback (RLHF) [27, 29].
Many large language models have been proposed recently, includ-
ing close-sourced LLMs [4, 27, 29] and open-sourced LLMs [47, 52].                   Figure 12: Impact of the number of in-context learning ex-
One of the most popular open-sourced LLMs is LLAMA from                              amples on the in-context learning defense.
Meta [41, 42]. Based on LLAMA, several works collect instruction-
followed datasets and apply SFT to fine-tune chat models, such as                    B     Additional Experimental Settings
Alpaca [39] and Vicuna [53].
                                                                                     The detailed category information of different test attacks is shown
                                                                                     in Table 5, while the information of train attacks is shown in Table 6.

A.2     LLM-integrated Applications                                                  C Additional Experiments
Despite the remarkable performance achieved by LLMs, they have                       C.1 Hyper-parameter Analysis
some shortcomings, such as the inability to access up-to-date in-
                                                                                     We analyze the impact of hyper-parameters on the performance
formation and use external tools. To address these problems, re-
                                                                                     of defense methods. More specifically, we study the impact of the
searchers have proposed combining LLMs with external tools [19,
                                                                                     number of in-context learning examples for in-context learning
22, 23]. For example, Schick et al. [36] propose training a model
                                                                                     defense, the response construction method, and the training steps
named Toolformer to predict the tool type, time, and arguments for
                                                                                     for our white-box defense.
using external tools. HuggingGPT [37] enables LLMs to connect
                                                                                        Impact of the number of examples in the in-context learn-
with various models in the AI community (e.g., Huggingface).
                                                                                     ing. For in-context learning defense, we analyze the impact of the
   In addition, numerous LLM-integrated industrial and open-source
                                                                                     number of in-context learning examples. As shown in Figure 12,
projects have emerged. BingChat combines GPT models with web
                                                                                     although adding different numbers of in-context learning examples
search for content summarization. Microsoft 365 Copilot and AI-
                                                                                     can reduce the ASR, there is no clear correlation between the num-
powered Google Workspace enhance productivity in office applica-
                                                                                     ber of examples added in text tasks and ASR. This may be related
tions. OpenAI Plugins enable GPT to interact with web browsers
                                                                                     to the diversity of external content and instructions in text attacks.
and Python interpreters. LangChain assists in developing LLM-
                                                                                     In the code QA task, however, we observe a clear downward trend
integrated applications, while Auto-GPT creates an autonomous
                                                                                     in ASR as the number of in-context learning examples increased. In
agent using GPT-4 and external tools. As LLMs evolve, their inte-
                                                                                     addition, we observe that adding in-context examples has no signif-
gration into various applications is expected to expand.
                                                                                     icant effect on the ROUGE score of benign input, which indicates
                                                                                     that the defense method does not impair the model’s performance
                                                                                     on the original task.
A.3     Indirect Prompt Injection Attacks                                               Impact of different response construction methods. Fig-
As LLMs continue to develop, their security has become increasingly                  ures 13(a) and 13(b) show that all three response construction meth-
important [2, 3, 9, 32]. In indirect prompt injection attacks, attack-               ods effectively reduce the ASR to nearly 0, with GPT-4 performing
ers inject malicious instructions into third-party content, which,                   the best due to its high-quality and diverse responses. In terms of
when retrieved by an LLM-integrated application and ingested by                      performance impact, GPT-4 has the least impact on ROUGE-1 on
the LLM, cause the LLM’s output to deviate from the user’s expec-                    benign prompts, followed by Original LLM and BIPIA. The impact
tations. This kind of attacks aim to adversely impact normal users                   may stem from response quality and diversity. Original LLM gener-
of LLM-integrated applications, which can potentially cause much                     ates lower-quality responses, while Directly using the BIPIA label
more damage than direct prompt injection attacks, such as exfil-                     as a response makes the model’s answers rigid and lacking in ex-
trating user’s private information, fetching malicious commands                      planation, influencing the ROUGE score. As shown in Figure 13(a)
from attackers’ servers, and spreading malicious instructions to                     and Figure 13(b), the capability score on MT-bench demonstrates a
more content [14]. Indirect prompt injection poses a significant                     similar trend to the ROUGE score.
security threat to LLM-integrated applications. In this paper, we                       Impact of training steps. As shown in Figure 13(a) and Fig-
focus on evaluating and defending against indirect prompt attacks.                   ure 13(b), the main conclusion is that a significant drop in ASR
After our work, Wallace et al. [46] propose an Instruction Hierarchy                 can be observed after approximately 100 training steps. On the
at a higher level, which extends the white-box defense to address                    other hand, After 500 training steps, the model’s ROUGE score and
broader LLM attacks simultaneously.                                                  capability score on MT-bench also tend to stabilize.
KDD ’25, August 3–7, 2025, Toronto, ON, Canada                                                                                                    Jingwei Yi et al.


                                        Table 5: Detailed category information of different test attacks.

                       Category                                        Types                                                 Impact
                                      Task Automation, Business Intelligence, Conversational Agent,        Interfering with LLM’s
                    Task-irrelevant
                                      Research Assistance, Sentiment Analysis                              completion of user tasks.
            Text
                                      Substitution Ciphers, Base Encoding, Reverse Text,                   Interfering with the user’s
                    Task-relevant
                                      Emoji Substitution, Rare Language Translation                        understanding of LLM output.
                                      Information Dissemination, Marketing & Advertising, Entertainment,   Achieving specific attack objectives
                    Targeted
                                      Scams & Fraud, Misinformation & Propaganda                           by disrupting LLM outputs.
                                      Data Eavesdropping, Traffic Analysis, Keylogging,                    Inserting malicious code that
                    Passive
            Code                      Screen Scraping, Introduce System Fingerprinting                     monitoring user activities.
                                      Blocking Internet Connection, Corrupting an Operating System,
                                                                                                           Inserting malicious code that
                    Active            Encrypting Documents and Demanding Ransom,
                                                                                                           actively compromise a system or network.
                                      Compromising Computers, Bringing Down Hosts and Servers

                                       Table 6: Detailed category information of different train attacks.

                       Category                                        Types                                                Impact
                                      Information Retrieval, Content Creation, Learning and Tutoring,      Interfering with LLM’s
                    Task-irrelevant
                                      Language Translation, Programming Help                               completion of user tasks.
            Text
                                      Alphanumeric Substitution, Homophonic Substitution,                  Interfering with the user’s
                    Task-relevant
                                      Misspelling Intentionally, Anagramming, Space Removal & Grouping     understanding of LLM output.
                                      Instruction, Social Interaction, Persuasion, Clickbait,              Achieving specific attack objectives
                    Targeted
                                      Malware Distribution,                                                by disrupting LLM outputs.
                                      Cookie Theft, Memory Scanning, Dumpster Diving,                      Inserting malicious code that
                    Passive
            Code                      Environment Variable Analysis, Device and Driver Enumeration         monitoring user activities.
                                      Sending Out Spam Emails, Crippling Critical Infrastructures,
                                                                                                           Inserting malicious code that
                    Active            Network Propagation, Exploiting System Vulnerabilities,
                                                                                                           actively compromise a system or network.
                                      Cryptocurrency Mining




                                                                               (a) Vicuna-7B.




                                                                            (b) Vicuna-13B.


Figure 13: Trends in ASR, ROUGE-1 (recall), and MT-Bench score of Vicuna models with different response construction
methods under white-box defenses across training steps.
