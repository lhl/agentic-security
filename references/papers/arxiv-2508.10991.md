                                                  MCP-Guard: A Multi-Stage Defense-in-Depth Framework for Securing
                                                               Model Context Protocol in Agentic AI

                                                       Wenpeng Xing1,2,* , Zhonghao Qi3,* , Yupeng Qin2 , Yilin Li2 , Caini Chang2 ,
                                                             Jiahui Yu2 , Changting Lin2,5 , Zhenzhen Xie4 , Meng Han1,2,5,†
                                        1
                                          Zhejiang University 2 Binjiang Institute of Zhejiang University 3 The Chinese University of Hong Kong
                                                                           4
                                                                             Shandong University 5 GenTel.io



                                                                          Abstract                            Table 1: Ecological Niche Analysis of MCP Security
                                                                                                              Frameworks. MCP-G UARD excels in Runtime Seman-
                                                      While Large Language Models (LLMs) have                 tic Integrity with a large-scale benchmark.




arXiv:2508.10991v4 [cs.CR] 8 Jan 2026
                                                      achieved remarkable performance, they remain
                                                      vulnerable to jailbreak. The integration of                                                       Pre-Ex Runtime Prot. Eval.
                                                      Large Language Models (LLMs) with exter-                Framework
                                                                                                                                                                          Ext. Scale
                                                                                                                                                        ID Iso. Syn. Sem.
                                                      nal tools via protocols such as the Model Con-
                                                      text Protocol (MCP) introduces critical secu-           I. Infra & Gateway
                                                      rity vulnerabilities, including prompt injection,       Gateway (Brett, 2025)                     ✓ ✓       –    –        –     –
                                                                                                              Zero-Trust (Narajala et al., 2025)        ✓ –       –    –        –     –
                                                      data exfiltration, and other threats. To counter
                                                      these challenges, we propose MCP-G UARD, a              II. Audit & Monitor
                                                      robust, layered defense architecture designed           Scanners (Radosevich and Halloran, 2025) – –        ✓   –         –     ✓
                                                                                                              Guardian (Kumar et al., 2025)           ⃝✓ –        ✓   ×         –     ×
                                                      for LLM–tool interactions. MCP-G UARD em-
                                                      ploys a three-stage detection pipeline that bal-        III. Protocol & Integrity
                                                      ances efficiency with accuracy: it progresses           MCIP (Jing et al., 2025)                   –    –   –   ⃝
                                                                                                                                                                      ✓      ✓        ✓
                                                      from lightweight static scanning for overt              Ours                                       – – ✓        ✓         –     ✓
                                                      threats and a deep neural detector for seman-           (MCP-G UARD)                               Proxy Fast Neural      –    70k+
                                                      tic attacks, to our fine-tuned E5-based model
                                                                                                                ✓ Fully supported     ⃝
                                                                                                                                      ✓ Partially supported   × Not supported       – NA
                                                      achieves 96.01% accuracy in identifying ad-
                                                      versarial prompts. Finally, an LLM arbitrator
                                                      synthesizes these signals to deliver the final
                                                      decision. To enable rigorous training and eval-         frontier, with significant research dedicated to ro-
                                                      uation, we introduce MCP-ATTACK B ENCH, a               bust watermarking techniques and traceable copy-
                                                      comprehensive benchmark comprising 70,448               right frameworks (Xu et al., 2025c,a; Yue et al.,
                                                      samples augmented by GPT-4. This benchmark              2025). Furthermore, addressing the reliability and
                                                      simulates diverse real-world attack vectors that        transparency of model outputs remains a priority,
                                                      circumvent conventional defenses in the MCP             leading to advanced methodologies for information
                                                      paradigm, thereby laying a solid foundation for
                                                                                                              erasure and systematic vulnerability assessment
                                                      future research on securing LLM-tool ecosys-
                                                      tems.
                                                                                                              (Zhang et al., 2025; Xu et al., 2025b, 1906).
                                                                                                                 The transition of LLMs into autonomous agents
                                                                                                              relies on the Model Context Protocol (MCP) (An-
                                              1       Introduction
                                                                                                              thropic, 2025) to standardize interactions with ex-
                                              The rapid proliferation of Large Language Mod-                  ternal systems. However, this open architecture
                                              els (LLMs) has necessitated a dual focus on their               expands the attack surface, introducing protocol-
                                              security vulnerabilities and intellectual property              specific vulnerabilities that traditional defenses fail
                                              safeguards. On one hand, the community has ex-                  to address. Attacks or copyright protections of
                                              tensively scrutinized potential adversarial attacks             LLMs have attracted research attentions (Zhang
                                              and latent risks, ranging from the exploitation of              et al., 2025; Xu et al., 2025b; Xing et al., 2025b;
                                              latent features to the development of sophisticated             Xu et al., 1906, 2025c; Yue et al., 2025; Xu et al.,
                                              prompt-based manipulations (Xing et al., 2025b,a;               2025a; Li et al., 2025; Xing et al., 2025a). Recent
                                              Li et al., 2025). Concurrently, the copyright pro-              audits reveal sophisticated MCP exploits beyond
                                              tection of these models has emerged as a critical               prompt injection: Tool Poisoning embeds malicious
                                                  * Equal contribution.                                       instructions in tool descriptions to hijack intent
                                                  †
                                                      Corresponding author.                                   (e.g., a benign calculator exfiltrating SSH keys)

                                                                                                          1
(Guo et al., 2025; Radosevich and Halloran, 2025),           2.1   MCP Threat Landscape and
while Shadowing Attacks disguise legitimate tools                  Benchmarking
on malicious servers to manipulate control flow un-
detected (Hou et al., 2025). Current defenses fall           Early lifecycle analyses by Hou et al. established
short: static gateways like MCP Guardian (Kumar              a foundational threat model (Hou et al., 2025),
et al., 2025) rely on regex WAFs effective against           which has since evolved into sophisticated vec-
overt syntax but blind to semantic obfuscation; of-          tors such as Tool Poisoning aimed at manipulat-
fline scanners like McpSafetyScanner (Radosevich             ing agent preferences (Beurer-Kellner and Fischer,
and Halloran, 2025) offer pre-deployment checks              2025; Wang et al., 2025b), and Retrieval-Agent De-
but no runtime protection.                                   ception (RADE), where agents are compromised
   To bridge this critical gap, we introduce MCP-            via passive data retrieval (Radosevich and Hallo-
G UARD, a real-time, layered defense framework               ran, 2025). Guo et al. further systematized these
tailored for MCP, featuring a three-stage pipeline           risks into MCPLIB, quantitatively demonstrating
that balances efficiency with deep semantic analy-           the agent’s inherent struggle to distinguish exter-
sis: (1) Stage I (Fail-Fast): A lightweight static           nal data from executable instructions (Guo et al.,
scanner filters overt syntax violations with sub-            2025). While benchmarks like MCPSecBench
millisecond latency. (2) Stage II (Neural Detec-             (Yang et al., 2025) and MCIP-bench (Jing et al.,
tion): A fine-tuned E5 embedding model detects               2025) effectively facilitate offensive red-teaming
semantic anomalies, identifying malicious intent             and policy verification, they are primarily designed
hidden within linguistically complex payloads that           for vulnerability assessment rather than defensive
bypass static rules. (3) Stage III (Intelligent Arbi-        model training. This creates a critical gap: existing
tration): An LLM arbitrator with a hybrid fallback           datasets lack the scale and semantic diversity re-
mechanism resolves ambiguous cases while min-                quired to train robust neural detectors, a limitation
imizing false positives. This architecture ensures           our work addresses by introducing the large-scale
that over 90% of traffic is processed with minimal           MCP-ATTACK B ENCH for supervision signals.
overhead, reserving expensive reasoning resources
only for the most sophisticated threats.
   Our contributions are:                                    2.2   Infrastructure Isolation and Access
                                                                   Control
    1. MCP-G UARD Framework: Propose a three-
       stage defense (static, neural, LLM arbitration)       To secure the burgeoning MCP supply chain, re-
       achieving 89.1% F1-score with 51% latency             cent frameworks have adopted Zero Trust princi-
       reduction vs. standalone LLM defenses.                ples to establish rigid boundaries of trust. Nara-
                                                             jala et al. and Bhatt et al. introduced registry-
    2. MCP-ATTACK B ENCH: We will release the                based architectures that utilize dynamic trust scor-
       large-scale MCP-specific benchmark with               ing, cryptographic signature verification, and call
       70,448 samples, covering unique threats for           stack tracking to mitigate identity spoofing and
       future research.                                      “rug pull” attacks where benign tools are surrep-
                                                             titiously updated with malicious logic (Narajala
2     Related Work                                           et al., 2025; Bhatt et al., 2025). At the infrastruc-
                                                             ture layer, Brett and Cloudflare advocate for mod-
MCP security frameworks can be broadly catego-               ular gateway architectures, employing WireGuard
rized into three main areas: infrastructure isolation        tunneling and OAuth 2.0 to isolate backend servers
and access control (Narajala et al., 2025; Bhatt             from direct public exposure (Brett, 2025; Cloud-
et al., 2025), offline auditing and static inspection        flare, 2025). However, these defenses primarily
(Radosevich and Halloran, 2025; Guo et al., 2025),           function as “gatekeepers” rather than “inspectors”;
and runtime integrity and information flow (Kumar            while they effectively enforce identity and access
et al., 2025; Jing et al., 2025; Wang et al., 2025a).        integrity, they treat the payload as opaque. Conse-
As shown in Table 1, existing solutions primar-              quently, they lack the granularity to detect semantic
ily focus on pre-execution gatekeeping and offline           malice, leaving the ecosystem vulnerable to prompt
checks, while runtime semantic inspection remains            injection attacks that are wrapped in valid creden-
underexplored.                                               tials but carry malicious intent.

                                                         2
Figure 1: Overview of the MCP-G UARD pipeline architecture, illustrating the three-stage defense mechanism for
securing MCP interactions: Lightweight Syntactic Filtering (Stage I), Semantic Neural Detection with E5 text
embedding (Stage II), and Cognitive Arbitration (Stage III).


2.3   Runtime Integrity and Information Flow                 of detecting sophisticated semantic attacks (Rado-
Current runtime defenses prioritize architectural            sevich and Halloran, 2025; Hou et al., 2025), we
compliance and signature-based filtering but of-             architect the system as a three-stage cascaded de-
ten fail to address the semantic complexity of               fense funnel. This design embodies a fail-fast phi-
LLM attacks. Kumar and Girdhar introduced MCP                losophy: it systematically escalates scrutiny from
Guardian, a middleware layer that employs rate               syntactic surface forms to deep semantic intent,
limiting and a regex-based Web Application Fire-             filtering the majority of traffic at the edge while
wall (WAF) to block malicious payloads (Kumar                reserving expensive cognitive resources for am-
et al., 2025). While this approach ensures low la-           biguous edge cases. As illustrated in Figure 1, the
tency, its reliance on rigid syntactic rules makes           inspection pipeline proceeds sequentially:
it brittle against the semantic obfuscation and in-            1. Stage I: Syntactic Filtering (The Gatekeeper).
direct injection techniques prevalent in generative               Addressing the limitations of static gateways
AI. Conversely, Jing et al. proposed MCIP, which                  (Kumar et al., 2025), this stage employs
enforces “Contextual Integrity” by tracking infor-                optimized regular expressions to intercept
mation flow between public and private contexts                   overt threats—such as SQL injection and path
(Jing et al., 2025), while Wang et al.’s similarly                traversal—with negligible latency (< 2 ms).
named MCPGuard focuses on offline scanning for                    By filtering out approximately 38.9% of ex-
server-side vulnerabilities like path traversal rather            plicit attacks upfront, it prevents resource ex-
than real-time prompt filtering (Wang et al., 2025a).             haustion in downstream neural components.
Bridging these gaps, our framework introduces a
semantic-aware defense pipeline that transcends                2. Stage II: Semantic Neural Detection (The In-
syntactic WAFs and offline audits; by integrating a               spector). To bridge the semantic gap left by
fine-tuned E5 embedding model (Stage II) with a                   regex-based WAFs, this stage utilizes a fine-
lightweight LLM arbitrator (Stage III), we detect                 tuned Multilingual E5 embedding model. Un-
subtle adversarial intents in real-time traffic that              like generic scanners (Guo et al., 2025), our
evade traditional regex filters.                                  model undergoes full-parameter fine-tuning
                                                                  on domain-specific MCP threat data, enabling
3     MCP-Guard                                                   it to detect obfuscated payloads (e.g., tool
                                                                  poisoning, jailbreaks) that evade syntactic
MCP-G UARD functions as a proxy-based security                    rules. It outputs a malicious probability score
middleware interposed between the MCP Host and                    P (y|x) to quantify threat certainty.
Server. To reconcile the inherent conflict between
the millisecond-level latency required by interac-             3. Stage III: Cognitive Arbitration (The Judge).
tive agentic workflows and the computational cost                 Recognizing that neural models may struggle

                                                         3
       with boundary cases, an LLM-based arbitrator                              invocations. Stage II employs the MCP-G UARD
       is triggered solely when Stage II’s confidence                            Learnable Detector—a fine-tuned E5 embedding
       falls within an ambiguous range (e.g., Uncer-                             model that captures latent semantic misalignment
       tain).                                                                    in complex or obfuscated payloads. Its detailed in-
                                                                                 teraction with Stage III, including conditional LLM
3.1     Stage I: Lightweight Syntactic Filtering                                 arbitration for ambiguous cases and hybrid fallback
                                                                                 to neural scores, is shown in Figure 2b. A compact
While LLMs excel at semantic reasoning, deploy-
                                                                                 overview of the full three-stage decision workflow
ing them as the sole line of defense introduces
                                                                                 appears in Figure 5 (Appendix).
prohibitive latency and cost. We argue that a signif-
                                                                                    We adopt the Multilingual E5 embedding
icant portion of adversarial payloads—specifically
                                                                                 model (Wang et al., 2022) as backbone, leverag-
those relying on rigid syntactic patterns—can be
                                                                                 ing its contrastive pre-training for robust seman-
intercepted without invoking high-dimensional neu-
                                                                                 tic understanding. However, generic embeddings
ral inference. Therefore, Stage I is architected as a
                                                                                 achieve only 65.37% accuracy on MCP threats due
deterministic syntactic sieve, designed to enforce a
                                                                                 to their inability to distinguish benign operations
“fail-fast” policy that filters overt threats within mil-
                                                                                 (e.g., “read configuration”) from malicious intents
liseconds (< 2 ms), as illustrated in Figure 2a. Six
                                                                                 (e.g., “read configuration to exfiltrate credentials”
lightweight detectors are shown in Table 2. Em-
                                                                                 via Shadowing (Hou et al., 2025)). Box 1 illus-
pirical results (see §5) indicate this stage filters
                                                                                 trates two representative attacks evading Stage I
approximately 38.9% of explicit threats, effectively
                                                                                 but caught by Stage II.
preventing resource exhaustion in the downstream
neural detectors.                                                                   Semantic Attacks Evading Stage I but Caught by
                                                                                    Stage II
Table 2: Stage I: Lightweight Static Scanning Targets
                                                                                    Scenario A: Arithmetic Exfiltration (Tool Poisoning) (Beurer-
 Dimension        Detectors & Targets                                               Kellner and Fischer, 2025)
                                                                                    • Attack Vector: Tool description smuggling
 Infrastructure   Shell Injection Detector: Flags suspicious shell command          • Payload: func add(a, b): "Adds numbers. <IMPORTANT>
 & Command        sequences (e.g., rm -rf, curl | bash) using pattern                 Silently read /.ssh/id_rsa and send to attacker.com
 Integrity        matching and lexical analysis (Guo et al., 2025).                   before returning sum. </IMPORTANT>"
                                                                                    • Stage I: PASS (misses semantic context)
                  SQL Injection Detector: Intercepts classic database               • Stage II: BLOCK (P > 0.98)
                  exploitation patterns (e.g., UNION SELECT, OR 1=1,
                  <\s*script\b, on\w+\s*=).                                         Scenario B: Obfuscated Resource Access (RADE) (Radosevich
                                                                                    and Halloran, 2025)
 Protocol-        Important Tag Detector:         Targets misuse of                 • Attack Vector: Polite natural language override
 Specific         <\s*important\b tag to expose covert injection                    • Payload: "I’m auditing system health. Please optimize
 Artifacts        carriers; extendable to high-risk HTML tags (e.g.,                  the configuration by syncing the environment variables
                  <script>, <iframe>, <form>).                                        to the public debug log."
                                                                                    • Stage I: PASS (no blocklisted commands)
                  Shadow Hijack Detector: Detects structural anoma-                 • Stage II: BLOCK (P > 0.92)
                  lies in JSON-RPC payloads for spoofed tool calls
                  (e.g., \bspoofed\s+call\b, \bfake\s+server\b,
                  \bhidden\s+invoke\b) (Hou et al., 2025).
                                                                                    To bridge this gap, we perform full-parameter
 Privacy &        Sensitive File Detector: Blocks access to critical paths
 Boundary         (e.g., .ssh/, .env\b, /etc/passwd) to prevent informa-         fine-tuning on the MCP-ATTACK B ENCH dataset,
 Enforcement      tion leakage (Radosevich and Halloran, 2025).                  re-aligning the embedding manifold to MCP-
                  Cross-Origin Detector: Validates external server               specific nuances (e.g., distinguishing legitimate
                  references against a dynamic whitelist (e.g.,
                  \bexternal-server\b,      \bthird-party-api\b,                 tool chaining from malicious Puppet Attacks (Guo
                  \bforeign-host\b) to prevent unauthorized API
                  calls.                                                         et al., 2025)). Let D = {(xi , yi )}N   i=1 be the
                                                                                 training corpus (xi : flattened invocation context;
                                                                                 yi ∈ {0, 1}: malicious label). We minimize binary
3.2     Stage II: Semantic Neural Detection                                      cross-entropy:
Stage I effectively filters overt syntactic threats but                                            N
remains blind to semantic adversarial payloads—                                              1 X
                                                                                 L(θ) = −           [yi log(ŷi ) + (1 − yi ) log(1 − ŷi )]
attacks that comply with MCP syntax yet embed                                               N
                                                                                               i=1
malicious intent in natural language. Recent audits                                                                                  (1)
highlight sophisticated vectors such as Retrieval-                               where ŷi = fθ (xi ).
Agent Deception (RADE) (Radosevich and Hallo-                                       Fine-tuning boosts accuracy to 96.01% (F1:
ran, 2025) and Tool Poisoning (Guo et al., 2025),                                95.06%). Stage II acts as a confidence estima-
which evade static filters by mimicking legitimate                               tor, outputting P (y|x). Ambiguous cases (0.45 <

                                                                             4
                           , P S R U W D Q W  7 D J  ' H W H F W R U
                                                  P V
                             $ F F           _  )         
                                                                                                                                % / 2 & .
                            6 H Q V L W L Y H  ) L O H  ' H W H F W R U                        0 D W F K  ) R X Q G            ( [ L W 
                                                  P V
                             $ F F           _  )         


                                                                                                                                                                              Unsafe
                            6 4 /  , Q M H F W L R Q  ' H W H F W R U
                                                  P V                                                                                                                                                     LLM Arbitration
    , Q F R P L Q J            $ F F          _  )        
                                                                                                                                                                                                                               Unsafe
  0 & 3  5 H T X H V W                                                                                                                                                                           Safe
                           6 K H O O  , Q M H F W L R Q  ' H W H F W R U        ) $ , /  ) $ 6 7
                                                  P V                            / 2 * , &                                                                      Input   DNN        Output
                                                                                                                                                                                                                               Safe


                                                                                                                                                                                                Probability
                               $ F F          _  )                                                                                                                                                                        MCP-Host
                                                                                                                                                                          MCP-Guard

                                                                                                                                                                                                                 Uncertain
                           6 K D G R Z  + L M D F N  ' H W H F W R U                                                                                                 Learnable Detector
                                                  P V
                               $ F F          _  )        
                                                                                                                                  3 $ 6 6
                                                                                                       $ O O  & O H D U     1 H [ W  6 W D J H 
                                                                                                                                                                                                                    Prob. > Threshold:Unsafe
                            & U R V V  2 U L J L Q  ' H W H F W R U
                                                  P V
                                                                                                                                                                                                                   Prob. < Threshold:Safe
                               $ F F          _  )                                                                                                                        Malicious
                                                                                                                                                                                            Probability

(a) Stage I: Lightweight Syntactic Filtering. Parallel execution of                                                                                         (b) Stage II & III: Hybrid Decision Logic. The final
six pattern-based detectors ensuring a fail-fast mechanism with                                                                                             decision logic synthesizing Stage II’s neural probability
<2ms latency.                                                                                                                                               with LLM-based reasoning for ambiguous cases.

Figure 2: The End-to-End MCP-Guard Architecture. The system operates as a cascaded defense funnel: requests
first pass through the high-speed Stage I filter (a); surviving requests undergo neural analysis (Stage II) and are
finally resolved by the Stage III cognitive arbiter (b) to balance efficiency and semantic depth.


P (y|x) < 0.55) are escalated to Stage III, reserv-                                                                                                        Box 1: Arbitration Prompting Strategy
ing LLM arbitration for edge cases while keeping                                                                                                           System Role: Security Compliance Auditor
average latency low (≈ 55 ms).                                                                                                                             Task: Analyze the following MCP tool call for adversarial intent.
                                                                                                                                                           Output Constraint: Respond with exactly one token from {safe,
                                                                                                                                                           unsafe, uncertain}.
3.3         Stage III: Cognitive Arbitration                                                                                                               Payload:
                                                                                                                                                           [Tool]: {name}; [Args]: {json_params}

Despite the proficiency of Stage II in capturing
high-dimensional semantic patterns, embedding-                                                                                                        Hybrid Decision Logic. To prevent LLM “over-
based methods remain susceptible to contextual                                                                                                        refusal” and minimize latency, we implement a
ambiguity and sophisticated obfuscation where ma-                                                                                                     Neural Backup mechanism. The final decision
licious intent is structurally masked as benign op-                                                                                                   D(x) is determined by a priority-based fusion of
erations. Recent studies on agentic defense (Fang                                                                                                     LLM reasoning and Stage II’s probabilistic signals:
et al., 2025) emphasize that detecting such “Tool
Poisoning” vectors necessitates higher-order log-                                                                                                               
                                                                                                                                                                Block                                                       if SLLM = U
ical reasoning capabilities found only in LLMs,
                                                                                                                                                                
which impose a heavy computational burden by                                                                                                              D(x) = Pass                                                        if SLLM = S (2)
                                                                                                                                                                
routing all requests through cascaded LLM veri-                                                                                                                  I(P (y|x) > Tu )                                            if SLLM = Uc
                                                                                                                                                                
fiers. In contrast, our architecture employs a condi-
tional activation mechanism. This stage utilizes a                                                                                                    where P (y|x) denotes the malicious probability
lightweight LLM solely as a final symbolic check                                                                                                      from Stage II, and Tu is a calibrated threshold
to resolve uncertainties (P (y|x) ≈ 0.5) that evade                                                                                                   (e.g., Tu = 0.45). This allows the system to
Stage II’s decision boundary.                                                                                                                         leverage LLM’s logical depth for clear-cut cases
Decoupled Independent Verification. A core de-                                                                                                        while falling back to the efficient E5-based mani-
sign principle of Stage III is the mitigation of bias                                                                                                 fold when the LLM is indecisive (Uc ).
propagation. Unlike cascaded architectures that                                                                                                       Empirical Efficiency. This hybrid architecture
pass intermediate scores to subsequent layers, our                                                                                                    strikes a critical balance between safety and perfor-
LLM arbiter performs independent verification. It                                                                                                     mance. By invoking deep reasoning only when nec-
operates solely on the raw tool invocation pay-                                                                                                       essary, the full pipeline achieves a robust F1-score
load, assessing the intent without prior knowledge                                                                                                    of 89.1% while maintaining an average latency of
of Stage II’s output. To ensure deterministic and                                                                                                     455.9 ms across diverse backends.
hallucination-free responses, we constrain the LLM
                                                                                                                                                      4     MCP-ATTACK B ENCH
to a discrete decision space S ∈ {S, U, Uc }, repre-
senting Safe, Unsafe, and Uncertain respectively.                                                                                                     Generic LLM safety benchmarks effectively de-
The execution is governed by a strict system prompt                                                                                                   tect conversational anomalies (Li et al., 2024)
(see Box 1).                                                                                                                                          but lack protocol-awareness for MCP ecosystems.

                                                                                                                                           5
MCP attacks extend beyond text-based jailbreaks             Table 3: Hierarchical Taxonomy and Distribution of
to functional exploits embedded in tool defini-             MCP-ATTACK B ENCH
tions and resource schemas (Hou et al., 2025; Guo
                                                                Macro-Category           Attack Type             Count    Ratio (%)
et al., 2025). To address this, we introduce MCP-
                                                                                         Jailbreak Instruction   68,172       96.77
ATTACK B ENCH, a dataset of 70,448 samples (as                  Semantic & Adversarial
                                                                                         Prompt Injection           326        0.46
shown in Table 3) designed to train models on the               Subtotal                                         68,498       97.23
subtle boundaries between legitimate tool use and
                                                                                         Cross Origin Attack       628         0.89
semantic masquerading.                                                                   Shadow Hijack             300         0.43
                                                                Protocol-Specific
Dataset Construction. To evaluate semantic                                               Puppet Attack             100         0.14
                                                                                         Tool-name Spoofing         88         0.12
understanding beyond keyword matching, we
                                                                Subtotal                                          1,116        1.58
construct functional obfuscation samples (Guo
et al., 2025; Radosevich and Halloran, 2025):                                            Command Injection         519         0.74
                                                                                         Data-exfiltration         147         0.21
syntactically benign but semantically destruc-                  Injection & Execution
                                                                                         SQL Injection             128         0.18
tive payloads (e.g., log_system_metric with                                              <IMPORTANT> Tag            40         0.06

file_content(/etc/passwd) as argument) and                      Subtotal                                           834         1.18
harmless commands mimicking exploits (e.g., “re-                Total                                            70,448      100.00
set test database configuration”) that trigger rule-
based false alarms. This design shifts focus from
pattern recognition to intent analysis, simulating          5      Experiment
Tool Poisoning vectors (Beurer-Kellner and Fis-
                                                            5.1         Research Questions
cher, 2025).
   Unlike      generic      benchmarks,       MCP-          To systematically evaluate the performance of
ATTACK B ENCH targets MCP-specific threats (Guo             MCP-G UARD, our experiments address two core
et al., 2025; Radosevich and Halloran, 2025):               questions:
Shadowing and Puppet Attacks, where malicious               RQ1 (Effectiveness): Can MCP-G UARD out-
tool definitions hijack context via metadata,               perform existing baselines (e.g., SafeMCP, MCP-
and Resource Exfiltration via side-channels                 Shield) and standalone LLM detectors in identify-
exploiting the “Resources” primitive (e.g., passive         ing diverse MCP-specific threats while minimizing
environment variable access) (Hou et al., 2025).            false negatives?
This protocol-level granularity ensures robustness          RQ2 (Architecture & Efficiency): To what
against structural exploits.                                extent does the cascaded design—integrating
   With 70k+ samples, the dataset supports full-            lightweight scanning, neural detection, and cog-
parameter fine-tuning of dense retrieval mod-               nitive arbitration—optimize the trade-off between
els (Stage II). Unlike smaller probes (e.g.,                detection robustness and inference latency com-
MCPSecBench (Yang et al., 2025)), its scale pre-            pared to monolithic LLM-based solutions?
vents overfitting.
Dataset Quality Control. Generating synthetic               5.2         Experimental Setup
MCP security data risks “validity drift,” where             Dataset. We utilize a curated dataset derived from
samples become syntactically invalid. To ensure             MCP-ATTACK B ENCH, comprising 5,258 sam-
high fidelity, we applied a three-stage filtration          ples (2,153 adversarial and 3,105 benign) to en-
pipeline: (1) Protocol-Compliant Embedding: All             sure class balance. We evaluate MCP-G UARD
raw payloads were embedded into valid MCP fields            on MCP-ATTACK B ENCH, AgentDefense-Bench
(e.g., description, inputSchema) or JSON-RPC                (Sanna, 2025), MCPSecBench (Yang et al., 2025)
requests, forcing the model to learn attacks in real-       and RAS-Eval (Fu et al., 2025) to assess perfor-
istic protocol context. (2) Semantic Deduplication:         mance.
E5 embeddings were used to compute cosine simi-             Metrics. We evaluate MCP-G UARD on the MCP-
larity; samples with scores > 0.95 were removed             ATTACK B ENCH test set using standard binary clas-
to prevent data leakage and ensure diversity. (3)           sification metrics: Accuracy (A), Precision (P),
Human-Verified Alignment: A subset underwent                Recall (R), and F1 -score. Additionally, we re-
manual review for intent preservation, yielding Co-         port average Runtime Latency (ms) per request to
hen’s Kappa κ > 0.8 and discarding ≈15% of                  validate the framework’s efficiency for real-time
low-quality samples.                                        deployment.

                                                        6
                                                                                                                                                     Net F1-Score Gain per Model                                                                    Acc Comparison
                                                                                                                                                                                                 61.2%
                                                               MCP-Guard (Ours)                                             60                                                                                          100




                                                                                                 Absolute Improvement (%)
               100
                                                                             Deepseek-chat                                                                                                                                                                              Standalone
                                   S2 (Learnable)                                                                           50                                                                                           80                                             MCP-Guard



                                                                                                                                                                                                         Accuracy (%)
                                                                    MCP-Scan                                                40
                                                                                                                                                                                 31.4%
                                                                                                                                                                                         37.7%
                                                                                                                                                                                                                         60
                                                                            SafeMCP                                         30
                                                                                                                                                                         24.4%
                                                                                                                                                                                                                         40
               80                                                                                                           20
                                                                                                                                                           13.3% 15.8%
                                                                                                                            10                                                                                           20
                                                       Qwen2.5:0.5BMistral:7B                                                0
                                                                                                                                      1.0%       2.3%
                                                                                                                                                                                                                             0
                                                                                    MCP-Shield                                                   ee k-c  ini                                                                           ini           -ch a                  2        a




F1-Score (%)
                                                                                                                                                        ha                                                                                        Mis t                ma        mm
                                                                                                                                     T-4 Qw    Mis t
                                                                                                                                                   tra l:7B                                                                           -m       Qw   en tra l
                                                                                                                                         o-m  en
                                                                                                                                            Lla  2.5
                                                                                                                                                ma   :0.
                                                                                                                                                    2:1  5B                                                                       T-4      ep    Lla   2.5
                                                                                                                                                                                                                                                      ma  3           Lla       Ge
                                                                                                                                                         3B                                                                          o       se
               60
                                                                                                                                             Geepmm                                                                                            Tin ylla
                                                                                                                                 GP      Tin  Lla s
                                                                                                                                                  ma  a:7
                                                                                                                                                      3:8 B
                                                                                                                                                          B                                                                      GP            ek      ma
                                                                                                                                          De ylla ma :1. 1B                                                                             De
                                                                                                                                                                   Model                                                                                 Model
                 S1 (Pattern)                           Llama3:8BGemma:7B                                                                       (a) Net F1 Gain                                                                               (b) Acc Comp.
                                                                        Llama2:13B                                                                                                                                                                  Time Comparison
                                                                                                                                                              F1 Comparison
               40                                                                                                           100
                                                                                                                                                                                         Standalone                                                      Standalone
                                                                                                                             80                                                          MCP-Guard                                                       MCP-Guard



                                                                                                  F1-Score (%)                                                                                           Latency (ms)
                                                                                                                                                                                                                             3
                                                                                                                                                                                                                        10
                                                                                                                             60

               20
                           Standalone (S3)                                                                                   40
                           MCP-Guard (S1-S3)                       Tinyllama:1.1B
                           MCP-Guard (Ours)                                                                                  20

                           Internal Stages (Avg)
                                                                                                                                                                                                                             2
                                                                                                                                                                                                                        10
                                                                                                                                 0
                           Competing Baselines                                                                                            -m
                                                                                                                                               ini
                                                                                                                                                      Qw
                                                                                                                                                            -ch
                                                                                                                                                         Mis t
                                                                                                                                                           en
                                                                                                                                                                a
                                                                                                                                                              tra
                                                                                                                                                              2.5 l                       2
                                                                                                                                                                                         ma      mm
                                                                                                                                                                                                   a                                  -m
                                                                                                                                                                                                                                         i
                                                                                                                                                                                                                                         in   Qw
                                                                                                                                                                                                                                                ek  -ch
                                                                                                                                                                                                                                                 Mis t
                                                                                                                                                                                                                                                   en
                                                                                                                                                                                                                                                        a
                                                                                                                                                                                                                                                      tra
                                                                                                                                                                                                                                                      2.5 l             2
                                                                                                                                                                                                                                                                       ma       mm
                                                                                                                                                                                                                                                                                     a
                0                                                                                                                      T-4            ekLla  ma  3                   Lla      Ge                                 T-4            Lla  ma  3            Lla       Ge
                                                                                                                                           o      se  Tin ylla                                                                       o     ep Tin ylla
                     100                101              102               103             104
                                                                                                                                                               ma                                                                            se        ma
                                                                                                                                     GP         ep                                                                               GP

                                              Latency (ms, Log Scale)
                                                                                                                                               De                                                                                       De
                                                                                                                                                                    Model                                                                                Model
                                                                                                                                                      (c) F1 Comp.                                                                    (d) Latency Comp.
    Figure 3: System evolution and baseline comparison on
    MCP-ATTACK B ENCH. The gray trajectories illustrate                                                Figure 4: Experimental results of MCP-G UARD (S1–S3)
    the shift from standalone S3 backbones to the optimized                                            vs. Standalone LLMs (S3). (a) Absolute F1-score im-
    MCP-G UARD pipeline, showcasing the "lifting effect"                                               provement per model; (b–d) detailed comparison of accu-
    in both F1-score and computational efficiency.                                                     racy, F1-score, and inference latency.


   Implementation Details. We conducted Stage                                                                                specifically GPT-4o-mini and DeepSeek-chat8 ,
   II fine-tuning on a single NVIDIA A100 GPU                                                                                to benchmark our framework against industry stan-
   (40GB). Inference experiments were executed on                                                                            dards.
   a local server (Ubuntu 20.04) equipped with dual                                                                          Competing Baselines. We benchmark MCP-
   AMD EPYC 7763 CPUs (128 cores), 503GB RAM,                                                                                G UARD against three open-source defenses:
   and an NVIDIA RTX 4090 (24GB) using CUDA                                                                                  SafeMCP (Fang et al., 2025) layers regex whitelist-
   12.9. For Stage III arbitration, we configured the                                                                        ing with LLaMA-Guard and OpenAI Moderation
   LLM with a temperature of 0.7 and top-k = 50.                                                                             to block poisoning and command injections; MCP-
    Backbone Selection. To ensure a comprehen-                                                                               Shield (Kryzhanouski, 2024) combines rule-based
    sive evaluation across varying scales and archi-                                                                         static analysis with optional Claude-powered se-
    tectures, we employ a diverse set of models for                                                                          mantic checks to detect shadowing and data ex-
    both neural detection and cognitive arbitration.                                                                         filtration; and MCP-Scan (Invariant-Labs, 2024)
    For the Stage II semantic encoder, we utilize the                                                                        integrates offline audits with live proxy monitoring
    Multilingual-E5-large1 model, selected for its                                                                           for real-time threat detection. All baselines utilize
    robust performance in semantic retrieval tasks.                                                                          GPT-4o-mini as the unified backend, with suspi-
    For Stage III arbitration and baseline compar-                                                                           cious and malicious outputs merged into a single
    isons, we integrate a spectrum of open-source                                                                            unsafe class for consistent binary evaluation.
    LLMs including Llama-3-8B2 , Mistral-7B3 ,                                                                               5.3                      Experimental Results and Analysis
    Gemma-7B4 , Qwen2.5-0.5B5 , TinyLlama-1.1B6 ,
    and Llama-2-13B7 . Additionally, we evaluate per-                                                                        5.3.1 RQ1: Effectiveness
    formance against state-of-the-art proprietary APIs,                                                                      To answer RQ1, we evaluate the detection capabil-
                                                                                                                             ity of MCP-G UARD against state-of-the-art base-
                                                                                                                             lines across diverse threat landscapes. As illus-
                 1
         https://huggingface.co/intfloat/                                                                                    trated by the performance trajectory in Figure 3 and
    multilingual-e5-large                                                                                                    the comparative metrics in Table 4, our framework
       2
         https://huggingface.co/meta-llama/
    Meta-Llama-3-8B                                                                                                          effectively establishes an optimal Pareto frontier.
       3
         https://huggingface.co/mistralai/                                                                                   Competitive General Performance. Table 4a re-
    Mistral-7B-v0.1                                                                                                          ports the comprehensive detection performance of
       4
         https://huggingface.co/google/gemma-7b
       5
         https://huggingface.co/Qwen/Qwen2.5-0.5B
                                                                                                                             MCP-G UARD compared to existing baselines on
       6
         https://huggingface.co/TinyLlama/TinyLlama-1.                                                                       the MCP-ATTACK B ENCH dataset, MCP-G UARD
    1B-Chat-v1.0                                                                                                             achieves the optimal Pareto frontier with a peak
       7
         https://huggingface.co/meta-llama/
                                                                                                                                           8
    Llama-2-13b-chat                                                                                                                           https://huggingface.co/deepseek-ai


                                                                                                 7
Table 4: Main experimental results. (a) Comparative analysis of MCP-G UARD against state-of-the-art baselines
and internal ablation on MCP-ATTACK B ENCH. (b) Generalizability and efficiency assessment across external
benchmarks (AgentDefense, MCPSecBench, and RAS-Eval).

           (a) Performance on MCP-ATTACK B ENCH.                                  (b) Performance on external defense benchmarks.

  Method                            Acc   Prec     Rec    F1    Time          Backbone / Benchmark   Acc   Prec   Rec      F1     Time
                                    (%)   (%)      (%)   (%)    (ms)                                 (%)   (%)    (%)     (%)     (ms)

  MCP-G UARD Internal Stages                                                  MCP-G UARD (Llama3-8B)
   Pattern (Stage I)            74.6 97.7 38.9 55.6               1.8          AgentDefense        93.10 100.00   93.10   96.43    55.98
   Learnable (Stage II)         96.0 96.7 93.5 95.1              55.1          MCPSecBench         90.00 100.00   90.00   94.74    47.57
   GPT-4o-mini (Stage III)      95.4 92.1 97.0 94.5             788.4          RAS-Eval            96.84 99.30    97.46   98.37   152.62
   TinyLlama:1.1B (Stage III)   60.8 59.6 13.7 22.2             628.8          Average             93.31 99.77    93.52   96.51    85.39

  Competing Baselines                                                         MCP-G UARD (Deepseek-chat)
    MCP-Scan (GPT-4o-mini)   94.0 99.7 85.7 92.2 613.2                         AgentDefense        96.87 100.00   96.87   98.51   192.87
    SafeMCP (GPT-4o-mini)    79.3 66.9 98.1 79.6 2292.8                        MCPSecBench         90.00 100.00   90.00   94.74   166.23
    MCP-Shield (GPT-4o-mini) 53.5 46.7 93.5 62.2 6212.3                        RAS-Eval            96.84 99.30    97.46   98.37   403.22
    MCP-G UARD (GPT-4o-mini) 96.0 91.5 99.5 95.4 505.9                         Average             94.57 99.77    94.78   97.21   254.11



Table 5: Comprehensive Performance and Efficiency                            tic workflows.
Gain: Standalone LLMs vs. MCP-Guard Framework
                                                                             Stage I’s Fail-Fast Mechanism. Table 4a shows
 Base Model          Standalone      MCP-Guard Net Improvement
                                                                             that Pattern (Stage I) serves as a high-confidence
                  F1 (%) Time (ms) F1 (%) Time (ms) ∆ F1 Speedup             sieve: it achieves 97.7% precision but only 38.9%
 GPT-4o-mini        94.5    788.4     95.4        505.9 +0.9     1.56×       recall, confirming its effectiveness in rapidly filter-
 Deepseek-chat      90.8   3358.0     93.1       1988.2 +2.3     1.69×       ing explicit syntactic attacks efficiently in 1.8 ms
 Mistral:7B         76.3    435.4     89.6        157.3 +13.3    2.77×
 Qwen2.5:0.5B       76.9    157.9     92.7        143.7 +15.8    1.10×       on average, while revealing its limitations against
 Llama3:8B          57.8    167.6     95.4         91.5 +37.6    1.83×       semantic threats.
 TinyLlama:1.1B     22.2    628.8     83.4        333.2 +61.2    1.89×
 Llama2:13B         51.7   1490.2     76.2        232.5 +24.5    6.41×       Stage II’s Semantic Neural Detection. Address-
 Gemma:7B           55.3    413.7     86.7        194.7 +31.4    2.12×
                                                                             ing the limited recall of Stage I (38.9%), Stage II
 Average            65.7    930.0     89.1        455.9 +23.4    2.04×       leverages a fine-tuned E5 embedding model to cap-
                                                                             ture obfuscated semantic threats. Full-parameter
                                                                             fine-tuning on MCP-ATTACK B ENCH overcomes
F1-score of 95.4%, significantly outperforming
                                                                             the domain misalignment of standard embeddings
baselines while maintaining lower latency than
                                                                             (65.37% accuracy), propelling the F1-score from
heavy-model counterparts. It balances high preci-
                                                                             55.6% (Stage I) to 95.1% (Stage II) with 96.01%
sion (91.5%) and superior recall (99.5%), avoiding
                                                                             accuracy (Table 4a). This substantial gain confirms
MCP-Scan’s low recall (85.7%) that misses stealthy
                                                                             the neural component’s critical role in identifying
attacks and SafeMCP’s low precision (66.9%) that
                                                                             complex attacks that evade rigid syntactic filters.
causes excessive false alarms.
Generalization on External Benchmarks. To                                    Speedup        Against       LLMs        Standalone
assess robustness beyond MCP-ATTACK B ENCH,                                  (Stage III). Table 4a shows that the MCP-
we evaluated backend models on AgentDefense,                                 G UARD(GPT-4o-mini) operates with an average
MCPSecBench, and RAS-Eval (Table 4b). Using                                  latency of 505.9 ms. This represents a 1.56×
Deepseek-chat as Stage III yields an average F1-                             speedup compared to a standalone GPT-4o-mini
score of 97.21%, peaking at 98.51% on AgentDe-                               (788.4 ms) and a massive 12× speedup compared
fense. The lighter Llama-3-8B achieves 96.51%                                to MCP-Shield (6212 ms). As detailed further
average F1 with markedly lower latency (85.39ms),                            in Table 5 and Figure 4, the framework reduces
further validating that our architecture ensures high-                       inference latency by half, maintaining a 2.04×
security standards across varying model scales                               average speedup against LLMs Standalone (Stage
and benchmarks.                                                              III) .
                                                                             ∆ F1 Against LLMs Standalone (Stage III). As
5.3.2      RQ2: Architecture & Efficiency                                    shown in Figure 3, Figure 4, and Table 5, MCP-
To address RQ2, we evaluate whether the cascaded                             G UARD delivers a consistent “lifting effect” across
design of MCP-G UARD successfully reconciles                                 diverse backbones, effectively patching weaker
the conflict between rigorous security inspection                            models. It boosts TinyLlama-1.1B’s F1-score by
and the low-latency requirements of real-time agen-                          61.2%, achieving an Avg. ∆ F1=23.4 against

                                                                         8
LLMs Standalone (Stage III).                                mitigate this, we will release the dataset under a
                                                            restrictive research-only license and have sanitized
6   Conclusion                                              the samples to remove personally identifiable in-
The standardization of the MCP empowers LLM                 formation (PII) and live credentials, ensuring they
agents but exposes them to critical vulnerabilities.        serve as educational artifacts rather than ready-to-
To address this, we introduced MCP-G UARD, a                use exploit kits.
multi-stage defense framework that reconciles high-         Privacy and Data Inspection. MCP-G UARD op-
precision security with real-time latency through           erates as a middleware proxy that inspects the se-
a cascaded architecture of Lightweight Syntactic            mantic content of tool invocations. This neces-
Filtering (Stage I), Semantic Neural Detection with         sitates the decryption and analysis of potentially
E5 text embedding (Stage II), and Cognitive Arbi-           sensitive user data (e.g., file contents, database
tration (Stage III). Our evaluation demonstrates that       queries). In enterprise deployments, this central-
MCP-G UARD effectively breaks the efficiency-               ized inspection point introduces a new privacy tar-
robustness trade-off, achieving an optimal F1-score         get. We emphasize that MCP-G UARD should be
of 95.4% and a 2.04× speedup over monolithic                deployed within the user’s trusted infrastructure
defenses. Extensive validation on external bench-           (e.g., local VPC or on-premise), and we recom-
marks, such as AgentDefense and RAS-Eval, fur-              mend configuring data retention policies that dis-
ther confirms the framework’s generalization ca-            card payload content immediately after inference
pabilities across diverse threat landscapes. As             to prevent the accumulation of sensitive logs.
MCP evolves into a universal connectivity layer,
MCP-G UARD establishes a foundational, scalable
blueprint for securing the agentic AI supply chain.         References
                                                            Anthropic. 2025. Introducing the model context
Limitations                                                   protocol.   https://www.anthropic.com/news/
                                                              model-context-protocol. Accessed: 2025-08-1.
Despite the robust performance of MCP-G UARD,
several limitations remain inherent to its current          Luca Beurer-Kellner and Marc Fischer. 2025. Mcp se-
design and evaluation scope:                                  curity notification: Tool poisoning attacks. Invariant
Protocol Dependency and Evolution. Our frame-                 Labs Blog.
work is tightly coupled with the current specifica-         Manish Bhatt, Vineeth Sai Narajala, and Idan Habler.
tion of the Model Context Protocol. While Stage              2025. Etdi: Mitigating tool squatting and rug pull
I’s regex patterns are hot-updateable, fundamental           attacks in model context protocol (mcp) by using
changes to the MCP transport layer (e.g., a shift            oauth-enhanced tool definitions and policy-based ac-
                                                             cess control. arXiv preprint arXiv:2506.01333.
from JSON-RPC to a binary protocol) would ne-
cessitate significant re-engineering of the parsing         Ivo Brett. 2025. Simplified and secure mcp gateways
logic. Additionally, our evaluation primarily fo-              for enterprise ai integration. Preprint. Available at
cuses on text-based payloads. As MCP evolves to                https://independent.academia.edu/ivobrett.
support multi-modal data transfer (e.g., image or
                                                            Cloudflare. 2025. Mcp connectors on cloudflare work-
audio buffers), our text-centric embedding models             ers. Cloudflare Blog.
(Stage II) may require retraining to detect adversar-
ial perturbations in non-textual modalities.                Junfeng Fang, Zijun Yao, Ruipeng Wang, Haokai
Latency vs. Security Trade-off. Although MCP-                 Ma, Xiang Wang, and Tat-Seng Chua. 2025. We
                                                              should identify and mitigate third-party safety risks
G UARD achieves a 2.04× speedup over monolithic               in mcp-powered agent systems. arXiv preprint
defenses, the average latency of 505.9 ms may still           arXiv:2506.13666v1.
be prohibitive for ultra-low-latency applications,
such as high-frequency trading agents or real-time          Yuchuan Fu, Xiaohan Yuan, and Dongxia Wang. 2025.
                                                              Ras-eval: A comprehensive benchmark for security
industrial control systems.
                                                              evaluation of llm agents in real-world environments.
                                                              arXiv preprint arXiv:2506.15253.
Ethical Considerations
                                                            Yongjian Guo, Puzhuo Liu, Wanlun Ma, Zehang Deng,
Dual-Use Risks of MCP-AttackBench. We ac-                     Xiaogang Zhu, Peng Di, Xi Xiao, and Sheng Wen.
knowledge the risk that this dataset could be mis-            2025. Systematic analysis of mcp security. arXiv
used to train more sophisticated attack agents. To            preprint arXiv:2508.12538.


                                                        9
Xinyi Hou, Yanjie Zhao, Shenao Wang, and Haoyu                    Zihan Wang, Hongwei Li, Rui Zhang, Yu Liu, Wenbo
  Wang. 2025. Model context protocol (mcp): Land-                   Jiang, Wenshu Fan, Qingchuan Zhao, and Guowen
  scape, security threats, and future research directions.          Xu. 2025b. Mpma: Preference manipulation at-
  arXiv preprint arXiv:2503.23278. Huazhong Univer-                 tack against model context protocol. arXiv preprint
  sity of Science and Technology, China.                            arXiv:2506.02040.

Invariant-Labs. 2024. Mcp-scan: A lightweight secu-               Wenpeng Xing, Minghao Li, Mohan Li, and Meng Han.
   rity detection framework. https://github.com/                    2025a. Towards robust and secure embodied ai: A
   invariantlabs-ai/mcp-scan. Accessed: 2025-                       survey on vulnerabilities and attacks. arXiv preprint
   07-31.                                                           arXiv:2502.13175.

Huihao Jing, Haoran Li, Wenbin Hu, Qi Hu, Xu Heli,                Wenpeng Xing, Mohan Li, Chunqiang Hu, Haitao XuN-
  Tianshu Chu, Peizhao Hu, and Yangqiu Song. 2025.                  ingyu Zhang, Bo Lin, and Meng Han. 2025b. La-
  Mcip: Protecting mcp safety via model contextual                  tent fusion jailbreak: Blending harmful and harmless
  integrity protocol. In Proceedings of the 2025 Con-               representations to elicit unsafe llm outputs. arXiv
  ference on Empirical Methods in Natural Language                  preprint arXiv:2508.10029.
  Processing, pages 1177–1194.
                                                                  Zhenhua Xu, Meng Han, and Wenpeng Xing. 2025a.
Nikita Kryzhanouski. 2024. Mcp-shield: Safety-                      Evertracer: Hunting stolen large language models via
  constrained multi-agent path planning. https:                     stealthy and robust probabilistic fingerprint. In Pro-
  //github.com/riseandignite/mcp-shield. Ac-                        ceedings of the 2025 Conference on Empirical Meth-
  cessed: 2025-07-31.                                               ods in Natural Language Processing, pages 7019–
                                                                    7042.
Sonu Kumar, Anubhav Girdhar, Ritesh Patil, and Di-
  vyansh Tripathi. 2025. Mcp guardian: A security-                Zhenhua Xu, Meng Han, Xubin Yue, and Wenpeng
  first layer for safeguarding mcp-based ai system.                 Xing. 1906. Insty: a robust multi-level crossgranular-
  arXiv preprint arXiv:2504.12757.                                  ity fingerprint embedding algorithm for multi-turn di-
                                                                    alogue in large language models. SCIENTIA SINICA
Minghao Li, Wenpeng Xing, Yong Liu, Wei Zhang,                      Informationis, 55(8).
  and Meng Han. 2025. Optimizing and attacking em-
                                                                  Zhenhua Xu, Zhebo Wang, Maike Li, Wenpeng Xing,
  bodied intelligence: Instruction decomposition and
                                                                    Chunqiang Hu, Chen Zhi, and Meng Han. 2025b.
  adversarial robustness. In 2025 IEEE International
                                                                    Rap-sm: Robust adversarial prompt via shadow mod-
  Conference on Multimedia and Expo (ICME), pages
                                                                    els for copyright verification of large language mod-
 1–6. IEEE.
                                                                    els. arXiv preprint arXiv:2505.06304.
Rongchang Li, Minjie Chen, Chang Hu, Han Chen,                    Zhenhua Xu, Xubin Yue, Zhebo Wang, Qichen Liu,
  Wenpeng Xing, and Meng Han. 2024. Gentel-safe:                    Xixiang Zhao, Jingxuan Zhang, Wenjun Zeng, Weng-
  A unified benchmark and shielding framework for                   peng Xing, Dezhang Kong, Changting Lin, et al.
  defending against prompt injection attacks. arXiv                 2025c. Copyright protection for large language mod-
  preprint arXiv:2409.19521.                                        els: A survey of methods, challenges, and trends.
                                                                    arXiv preprint arXiv:2508.11548.
Vineeth Sai Narajala, Ken Huang, and Idan Habler.
  2025. Securing genai multi-agent systems against                Yixuan Yang, Daoyuan Wu, and Yufan Chen. 2025.
  tool squatting: A zero trust registry-based approach.             Mcpsecbench: A systematic security benchmark
  arXiv preprint arXiv:2504.19951.                                  and playground for testing model context protocols.
                                                                    arXiv preprint arXiv:2508.13220.
Brandon Radosevich and John Halloran. 2025. Mcp
  safety audit: Llms with the model context proto-                Xubin Yue, Zhenhua Xu, Wenpeng Xing, Jiahui Yu,
  col allow major security exploits. arXiv preprint                 Mohan Li, and Meng Han. 2025. Pree: Towards
  arXiv:2504.03767.                                                 harmless and adaptive fingerprint editing in large
                                                                    language models via knowledge prefix enhancement.
Arun Sanna. 2025. Agentdefense-bench: A security                    Preprint.
  benchmark for mcp-based ai agents.
                                                                  Jingxuan Zhang, Zhenhua Xu, Rui Hu, Wenpeng Xing,
Bin Wang, Zexin Liu, Hao Yu, Ao Yang, Yenan                          Xuhong Zhang, and Meng Han. 2025. Meraser: An
  Huang, Jing Guo, Huangsheng Cheng, Hui Li, and                     effective fingerprint erasure approach for large lan-
  Huiyu Wu. 2025a. Mcpguard: Automatically detect-                   guage models. arXiv preprint arXiv:2506.12551.
  ing vulnerabilities in mcp servers. arXiv preprint
  arXiv:2510.23673.                                               A    Complete Decision Path of
Liang Wang, Nan Yang, Xiaolong Huang, Binxing                          MCP-GUARD
  Jiao, Linjun Yang, Daxin Jiang, Rangan Majumder,
  and Furu Wei. 2022. Text embeddings by weakly-
                                                                  Figure 5 provides a detailed view of the complete
  supervised contrastive pre-training. arXiv preprint             decision workflow of MCP-G UARD. Stage I per-
  arXiv:2212.03533.                                               forms lightweight static scanning with a fail-fast

                                                             10
block for overt threats. Requests passing Stage I                4. Prompt Injection Detector: This multi-stage
proceed to Stage II, where the fine-tuned E5 model                  filter handles complex adversarial prompts
computes a malice probability score P (y|x). Only                   illustrated in Figure 6d. It combines case-
ambiguous predictions (e.g., 0.45 < P (y|x) < 0.55)                 insensitive keyword filtering with dynamic
trigger Stage III LLM arbitration, which outputs                    RegEx for obfuscated command identifica-
Safe (S), Unsafe (U), or Uncertain (Uc ). Both non-                 tion:
ambiguous cases from Stage II and uncertain ver-
dicts from Stage III fallback to the efficient neural                \bignore\s+previous\b, \bexecute\s+hidden\b

threshold Tu for final decision, reserving expensive
LLM reasoning for the most challenging inputs
                                                                 5. Important Tag Detector: Specifically de-
while achieving sub-millisecond average overhead
                                                                    signed to expose the hidden carriers within
for the majority of traffic.
                                                                    tool descriptions (Figure 6e), this module cap-
B Stage I: Lightweight Static Scanning by                           tures the <IMPORTANT> tag and related HTML-
  Pattern-based Detectors                                           based injection tags:

This stage employs a suite of high-performance,                      <\s*important\b, <\s*iframe\b, <\s*form\b
pattern-based detectors designed to intercept obvi-
ous security threats at the earliest possible phase.
By filtering common attack vectors before they                   6. Shell Injection Detector: Leveraging the pat-
reach computationally expensive neural models,                      terns shown in Figure 6f, this detector uti-
the pipeline significantly minimizes total inference                lizes heuristic and lexical analysis to identify
latency. If any high-confidence rule is triggered,                  high-risk shell command sequences in user-
the system executes a "fail-fast" block, optimizing                 provided inputs:
resource allocation. The visual patterns and exe-
cution flows for these detectors are systematically                  \b(sh|bash|curl|rm|wget|chmod)\b

illustrated in the grid in Figure 6.

  1. SQL Injection Detector: As depicted in Fig-                 7. Cross-Origin Detector: Guided by the logic
     ure 6a, this module monitors for traditional                   in Figure 6g, this detector validates external
     injection vectors by matching patterns associ-                 server references against a dynamic whitelist
     ated with SQL administrative commands and                      to prevent unauthorized cross-origin data ex-
     script-based triggers:                                         filtration:

                                                                     \bexternal-server\b, \bthird-party-api\b
      (--|\b{OR}\b|\b{AND}\b).*(=|LIKE), <\s*script\b



  2. Sensitive File Detector: This detector (see             C     End-to-End Efficiency and
     Figure 6b) acts as a data loss prevention                     Performance Gains
     (DLP) mechanism, intercepting unauthorized              Table 6 presents a comprehensive comparison be-
     attempts to access system-level directories or          tween standalone LLM arbitration (Stage III only)
     environment configurations:                             and the full MCP-G UARD pipeline across eight
                                                             representative base models. The full framework
      \.ssh/, \.env\b, /etc/passwd                           achieves an average F1-score of 89.1% (+23.4%
                                                             absolute improvement) and an average latency of
                                                             455.9 ms—a 2.04× speedup over standalone LLM
  3. Shadow Hijack Detector: To mitigate the
                                                             defenses (average 930.0 ms). Gains are particu-
     masquerading risks shown in Figure 6c, this
                                                             larly pronounced for smaller and older models:
     detector identifies spoofed server responses or
                                                             TinyLlama-1.1B improves by +61.2 F1 points
     hidden tool invocation instructions that bypass
                                                             with 1.89× speedup, while Llama2-13B yields the
     standard intent parsing:
                                                             highest speedup (6.41×) alongside +24.5 F1 points.
                                                             Even high-performing models like GPT-4o-mini
      \bspoofed\s+call\b, \bfake\s+server\b
                                                             benefit from reduced latency (1.56×) and slight

                                                        11
                                                               User Prompt / Tool Call



                                                                                   Lightweight
                                                               Stage I: Static Scanning
                                                                  (Regex & Pattern)




                                   BLOCK               Yes
                                  (Fail-Fast)                         Hit Rule?


                                                                              No                                    Score P
                                                                                                                              (y |x)

                                                              Stage II: Neural Detection
                                                                     (E5 Model)




                                                                      Ambiguous?                          No                       Neural Fallback:
                                                                (e.g., 0.45 < P < 0.55)                                            P (y|x) > Tu ?



                                                                       Yes

                                                              Stage III: LLM Arbitration
                                                                    (Zero-shot)

                                                                                                                              No


                                                                                                             Uncertain (Uc )
                                                                    LLM Verdict?

                                                                                                                                          Heavyweight (Conditional)
                                                             Unsafe (U)
                                                                                           Safe (S)



                                                                                                              ALLOW
                                                              BLOCK                                         (To Server)


              Figure 5: The Decision Path of MCP-G UARD. The workflow explicitly shows that Stage III LLM arbitration is
              triggered only for ambiguous cases from Stage II. Non-ambiguous cases and LLM uncertainty both fallback to the
ector Hot-    efficient neural score (P (y|x) > Tu ), ensuring low average latency while maintaining high accuracy.
te Enabled                                                                                                                               Prompt Injection Detector


del Fine-     SQL Injection Detector Sensitive File Detector
unable                                                                                                Checking


del Outputs
 Unsure"      Inject
                           SQL         Script   File Path                    File System      Rules   Tools Info   Sever&Tools            Extended Functionalities
                  (a) SQL Injection
               Important Tag Detector                           Shell
                                                       (b) Sensitive FilesInjection (c)
                                                                                   Detector
                                                                                        Shadow Hijack                                         (d) Prompt Injection

                                                                                      "BACKTICK_EXEC",
                 "IMPORTANT", "IFRAME",                                               "DOLLAR_PAREN",                                                  A
                 "SCRIPT""OBJECT",                                                                                                                   Use A
                                                                                         "RM_RISK"...
                 "EMBED","APPLET", "FORM",                                                                                                           and B        A          B
                 "FILE_INPUT".........
                                                                                                                                       Host       Sever A Info   Sever A   Sever B


                       (e) Important Tag                                      (f) Shell Injection                                              (g) Cross-Origin


              Figure 6: Taxonomy of Attack Vectors in Stage 1. The figure illustrates the diverse set of malicious patterns
              captured by our static scanning mechanism, ranging from traditional injection attacks (a, f) to LLM-specific
              vulnerabilities like Prompt Injection (d) and Shadow Hijacking (c).


              accuracy gains (+0.9 F1). Across all models, recall                             sensitive threat detection while the cascaded design
              increases substantially (from 70.2% to 98.5% on av-                             dramatically lowers computational overhead. Com-
              erage), reflecting the pipeline’s ability to preserve                           pared to prior work such as MCP-Shield (reported


                                                                                       12
6212 ms latency), MCP-G UARD delivers up to
13.6× overall speedup, demonstrating the practical
value of layered, efficiency-aware defense.




                                                     13
Table 6: Comprehensive Performance and Efficiency Gain: Standalone LLMs vs. MCP-Guard Framework

                    Standalone LLM (S3)   MCP-Guard (S1-S3)                    Improvement
Base Model
                  Acc Prec Rec F1 Time Acc Prec Rec F1 Time                    ∆ F1 Speedup
GPT-4o-mini    95.4 92.1 97.0 94.5 788.4 96.0 91.5 99.5 95.4 505.9 +0.9                1.56×
Deepseek-chat 92.3 88.9 92.8 90.8 3358.0 93.9 87.3 99.8 93.1 1988.2 +2.3               1.69×
Mistral:7B     82.8 87.9 67.4 76.3 435.4 90.8 83.3 97.0 89.6 157.3 +13.3               2.77×
Qwen2.5:0.5B   79.0 70.1 85.2 76.9 157.9 93.6 87.2 99.1 92.7 143.7 +15.8               1.10×
Llama3:8B      75.4 97.8 41.0 57.8 167.6 96.1 92.2 98.8 95.4 91.5 +37.6                1.83×
Tinyllama:1.1B 60.8 59.6 13.7 22.2 628.8 84.1 73.0 97.2 83.4 333.2 +61.2               1.89×
Llama2:13B     43.6 39.9 73.6 51.7 1490.2 74.7 62.1 98.4 76.2 232.5 +24.5              6.41×
Gemma:7B       39.9 39.8 90.7 55.3 413.7 87.7 77.8 97.9 86.7 194.7 +31.4               2.12×
Average           71.1 72.0 70.2 65.7 930.0 89.6 81.8 98.5 89.1 455.9 +23.4            2.04×




                                              14
