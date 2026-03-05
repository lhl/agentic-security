<!-- extracted-by: marker -->
# MCP-Guard: A Multi-Stage Defense-in-Depth Framework for Securing Model Context Protocol in Agentic AI

Wenpeng Xing1,2,\*, Zhonghao Qi3,\*, Yupeng Qin<sup>2</sup> , Yilin Li<sup>2</sup> , Caini Chang<sup>2</sup> , Jiahui Yu<sup>2</sup> , Changting Lin2,5 , Zhenzhen Xie<sup>4</sup> , Meng Han1,2,5,†

<sup>1</sup>Zhejiang University <sup>2</sup>Binjiang Institute of Zhejiang University <sup>3</sup>The Chinese University of Hong Kong <sup>4</sup>Shandong University <sup>5</sup>GenTel.io

### Abstract

While Large Language Models (LLMs) have achieved remarkable performance, they remain vulnerable to jailbreak. The integration of Large Language Models (LLMs) with external tools via protocols such as the Model Context Protocol (MCP) introduces critical security vulnerabilities, including prompt injection, data exfiltration, and other threats. To counter these challenges, we propose MCP-GUARD, a robust, layered defense architecture designed for LLM–tool interactions. MCP-GUARD employs a three-stage detection pipeline that balances efficiency with accuracy: it progresses from lightweight static scanning for overt threats and a deep neural detector for semantic attacks, to our fine-tuned E5-based model achieves 96.01% accuracy in identifying adversarial prompts. Finally, an LLM arbitrator synthesizes these signals to deliver the final decision. To enable rigorous training and evaluation, we introduce MCP-ATTACKBENCH, a comprehensive benchmark comprising 70,448 samples augmented by GPT-4. This benchmark simulates diverse real-world attack vectors that circumvent conventional defenses in the MCP paradigm, thereby laying a solid foundation for future research on securing LLM-tool ecosystems.

### 1 Introduction

The rapid proliferation of Large Language Models (LLMs) has necessitated a dual focus on their security vulnerabilities and intellectual property safeguards. On one hand, the community has extensively scrutinized potential adversarial attacks and latent risks, ranging from the exploitation of latent features to the development of sophisticated prompt-based manipulations [\(Xing et al.,](#page-9-0) [2025b](#page-9-0)[,a;](#page-9-1) [Li et al.,](#page-9-2) [2025\)](#page-9-2). Concurrently, the copyright protection of these models has emerged as a critical

<span id="page-0-0"></span>Table 1: Ecological Niche Analysis of MCP Security Frameworks. MCP-GUARD excels in Runtime Semantic Integrity with a large-scale benchmark.

|   |                                            | Runtime               |    |                   | Eval. |
|---|--------------------------------------------|-----------------------|----|-------------------|-------|
|   |                                            |                       |    | Ext.              | Scale |
|   |                                            |                       |    |                   |       |
|   |                                            | –                     | –  | –                 | –     |
| ✓ | –                                          | –                     | –  | –                 | –     |
|   |                                            |                       |    |                   |       |
|   | –                                          | ✓                     | –  | –                 | ✓     |
|   |                                            | ✓                     | ×  | –                 | ×     |
|   |                                            |                       |    |                   |       |
| – | –                                          | –                     | ⃝✓ | ✓                 | ✓     |
| – | –                                          | ✓                     | ✓  | –                 | ✓     |
|   |                                            | Proxy Fast Neural     |    | –                 | 70k+  |
|   | Scanners (Radosevich and Halloran, 2025) – | Pre-Ex<br>✓ ✓<br>⃝✓ – |    | ID Iso. Syn. Sem. | Prot. |

frontier, with significant research dedicated to robust watermarking techniques and traceable copyright frameworks [\(Xu et al.,](#page-9-7) [2025c,](#page-9-7)[a;](#page-9-8) [Yue et al.,](#page-9-9) [2025\)](#page-9-9). Furthermore, addressing the reliability and transparency of model outputs remains a priority, leading to advanced methodologies for information erasure and systematic vulnerability assessment [\(Zhang et al.,](#page-9-10) [2025;](#page-9-10) [Xu et al.,](#page-9-11) [2025b,](#page-9-11) [1906\)](#page-9-12).

The transition of LLMs into autonomous agents relies on the Model Context Protocol (MCP) [\(An](#page-8-1)[thropic,](#page-8-1) [2025\)](#page-8-1) to standardize interactions with external systems. However, this open architecture expands the attack surface, introducing protocolspecific vulnerabilities that traditional defenses fail to address. Attacks or copyright protections of LLMs have attracted research attentions [\(Zhang](#page-9-10) [et al.,](#page-9-10) [2025;](#page-9-10) [Xu et al.,](#page-9-11) [2025b;](#page-9-11) [Xing et al.,](#page-9-0) [2025b;](#page-9-0) [Xu et al.,](#page-9-12) [1906,](#page-9-12) [2025c;](#page-9-7) [Yue et al.,](#page-9-9) [2025;](#page-9-9) [Xu et al.,](#page-9-8) [2025a;](#page-9-8) [Li et al.,](#page-9-2) [2025;](#page-9-2) [Xing et al.,](#page-9-1) [2025a\)](#page-9-1). Recent audits reveal sophisticated MCP exploits beyond prompt injection: *Tool Poisoning* embeds malicious instructions in tool descriptions to hijack intent (e.g., a benign calculator exfiltrating SSH keys)

<sup>\*</sup>Equal contribution.

<sup>†</sup>Corresponding author.

[\(Guo et al.,](#page-8-2) [2025;](#page-8-2) [Radosevich and Halloran,](#page-9-4) [2025\)](#page-9-4), while *Shadowing Attacks* disguise legitimate tools on malicious servers to manipulate control flow undetected [\(Hou et al.,](#page-9-13) [2025\)](#page-9-13). Current defenses fall short: static gateways like MCP Guardian [\(Kumar](#page-9-5) [et al.,](#page-9-5) [2025\)](#page-9-5) rely on regex WAFs effective against overt syntax but blind to semantic obfuscation; offline scanners like McpSafetyScanner [\(Radosevich](#page-9-4) [and Halloran,](#page-9-4) [2025\)](#page-9-4) offer pre-deployment checks but no runtime protection.

To bridge this critical gap, we introduce MCP-GUARD, a real-time, layered defense framework tailored for MCP, featuring a three-stage pipeline that balances efficiency with deep semantic analysis: (1) Stage I (Fail-Fast): A lightweight static scanner filters overt syntax violations with submillisecond latency. (2) Stage II (Neural Detection): A fine-tuned E5 embedding model detects semantic anomalies, identifying malicious intent hidden within linguistically complex payloads that bypass static rules. (3) Stage III (Intelligent Arbitration): An LLM arbitrator with a hybrid fallback mechanism resolves ambiguous cases while minimizing false positives. This architecture ensures that over 90% of traffic is processed with minimal overhead, reserving expensive reasoning resources only for the most sophisticated threats.

Our contributions are:

- 1. MCP-GUARD Framework: Propose a threestage defense (static, neural, LLM arbitration) achieving 89.1% F1-score with 51% latency reduction vs. standalone LLM defenses.
- 2. MCP-ATTACKBENCH: We will release the large-scale MCP-specific benchmark with 70,448 samples, covering unique threats for future research.

### 2 Related Work

MCP security frameworks can be broadly categorized into three main areas: infrastructure isolation and access control [\(Narajala et al.,](#page-9-3) [2025;](#page-9-3) [Bhatt](#page-8-3) [et al.,](#page-8-3) [2025\)](#page-8-3), offline auditing and static inspection [\(Radosevich and Halloran,](#page-9-4) [2025;](#page-9-4) [Guo et al.,](#page-8-2) [2025\)](#page-8-2), and runtime integrity and information flow [\(Kumar](#page-9-5) [et al.,](#page-9-5) [2025;](#page-9-5) [Jing et al.,](#page-9-6) [2025;](#page-9-6) [Wang et al.,](#page-9-14) [2025a\)](#page-9-14). As shown in Table [1,](#page-0-0) existing solutions primarily focus on pre-execution gatekeeping and offline checks, while runtime semantic inspection remains underexplored.

## 2.1 MCP Threat Landscape and Benchmarking

Early lifecycle analyses by Hou et al. established a foundational threat model [\(Hou et al.,](#page-9-13) [2025\)](#page-9-13), which has since evolved into sophisticated vectors such as *Tool Poisoning* aimed at manipulating agent preferences [\(Beurer-Kellner and Fischer,](#page-8-4) [2025;](#page-8-4) [Wang et al.,](#page-9-15) [2025b\)](#page-9-15), and *Retrieval-Agent Deception* (RADE), where agents are compromised via passive data retrieval [\(Radosevich and Hallo](#page-9-4)[ran,](#page-9-4) [2025\)](#page-9-4). Guo et al. further systematized these risks into *MCPLIB*, quantitatively demonstrating the agent's inherent struggle to distinguish external data from executable instructions [\(Guo et al.,](#page-8-2) [2025\)](#page-8-2). While benchmarks like *MCPSecBench* [\(Yang et al.,](#page-9-16) [2025\)](#page-9-16) and *MCIP-bench* [\(Jing et al.,](#page-9-6) [2025\)](#page-9-6) effectively facilitate offensive red-teaming and policy verification, they are primarily designed for vulnerability assessment rather than defensive model training. This creates a critical gap: existing datasets lack the scale and semantic diversity required to train robust neural detectors, a limitation our work addresses by introducing the large-scale MCP-ATTACKBENCH for supervision signals.

## 2.2 Infrastructure Isolation and Access Control

To secure the burgeoning MCP supply chain, recent frameworks have adopted Zero Trust principles to establish rigid boundaries of trust. Narajala et al. and Bhatt et al. introduced registrybased architectures that utilize dynamic trust scoring, cryptographic signature verification, and call stack tracking to mitigate identity spoofing and "rug pull" attacks where benign tools are surreptitiously updated with malicious logic [\(Narajala](#page-9-3) [et al.,](#page-9-3) [2025;](#page-9-3) [Bhatt et al.,](#page-8-3) [2025\)](#page-8-3). At the infrastructure layer, Brett and Cloudflare advocate for modular gateway architectures, employing WireGuard tunneling and OAuth 2.0 to isolate backend servers from direct public exposure [\(Brett,](#page-8-0) [2025;](#page-8-0) [Cloud](#page-8-5)[flare,](#page-8-5) [2025\)](#page-8-5). However, these defenses primarily function as "gatekeepers" rather than "inspectors"; while they effectively enforce identity and access integrity, they treat the payload as opaque. Consequently, they lack the granularity to detect semantic malice, leaving the ecosystem vulnerable to prompt injection attacks that are wrapped in valid credentials but carry malicious intent.

<span id="page-2-0"></span>![](_page_2_Figure_0.jpeg)

Figure 1: Overview of the MCP-GUARD pipeline architecture, illustrating the three-stage defense mechanism for securing MCP interactions: Lightweight Syntactic Filtering (Stage I), Semantic Neural Detection with E5 text embedding (Stage II), and Cognitive Arbitration (Stage III).

#### 2.3 Runtime Integrity and Information Flow

Current runtime defenses prioritize architectural compliance and signature-based filtering but often fail to address the semantic complexity of LLM attacks. Kumar and Girdhar introduced *MCP Guardian*, a middleware layer that employs rate limiting and a regex-based Web Application Firewall (WAF) to block malicious payloads [\(Kumar](#page-9-5) [et al.,](#page-9-5) [2025\)](#page-9-5). While this approach ensures low latency, its reliance on rigid syntactic rules makes it brittle against the semantic obfuscation and indirect injection techniques prevalent in generative AI. Conversely, Jing et al. proposed *MCIP*, which enforces "Contextual Integrity" by tracking information flow between public and private contexts [\(Jing et al.,](#page-9-6) [2025\)](#page-9-6), while Wang et al.'s similarly named *MCPGuard* focuses on offline scanning for server-side vulnerabilities like path traversal rather than real-time prompt filtering [\(Wang et al.,](#page-9-14) [2025a\)](#page-9-14). Bridging these gaps, our framework introduces a semantic-aware defense pipeline that transcends syntactic WAFs and offline audits; by integrating a fine-tuned E5 embedding model (Stage II) with a lightweight LLM arbitrator (Stage III), we detect subtle adversarial intents in real-time traffic that evade traditional regex filters.

## 3 MCP-Guard

MCP-GUARD functions as a proxy-based security middleware interposed between the MCP Host and Server. To reconcile the inherent conflict between the millisecond-level latency required by interactive agentic workflows and the computational cost

of detecting sophisticated semantic attacks [\(Rado](#page-9-4)[sevich and Halloran,](#page-9-4) [2025;](#page-9-4) [Hou et al.,](#page-9-13) [2025\)](#page-9-13), we architect the system as a three-stage cascaded defense funnel. This design embodies a *fail-fast* philosophy: it systematically escalates scrutiny from syntactic surface forms to deep semantic intent, filtering the majority of traffic at the edge while reserving expensive cognitive resources for ambiguous edge cases. As illustrated in Figure [1,](#page-2-0) the inspection pipeline proceeds sequentially:

- 1. Stage I: Syntactic Filtering (The Gatekeeper). Addressing the limitations of static gateways [\(Kumar et al.,](#page-9-5) [2025\)](#page-9-5), this stage employs optimized regular expressions to intercept overt threats—such as SQL injection and path traversal—with negligible latency (< 2 ms). By filtering out approximately 38.9% of explicit attacks upfront, it prevents resource exhaustion in downstream neural components.
- 2. Stage II: Semantic Neural Detection (The Inspector). To bridge the semantic gap left by regex-based WAFs, this stage utilizes a finetuned Multilingual E5 embedding model. Unlike generic scanners [\(Guo et al.,](#page-8-2) [2025\)](#page-8-2), our model undergoes full-parameter fine-tuning on domain-specific MCP threat data, enabling it to detect obfuscated payloads (e.g., tool poisoning, jailbreaks) that evade syntactic rules. It outputs a malicious probability score P(y|x) to quantify threat certainty.
- 3. Stage III: Cognitive Arbitration (The Judge). Recognizing that neural models may struggle

with boundary cases, an LLM-based arbitrator is triggered solely when Stage II's confidence falls within an ambiguous range (e.g., *Uncertain*).

#### 3.1 Stage I: Lightweight Syntactic Filtering

While LLMs excel at semantic reasoning, deploying them as the sole line of defense introduces prohibitive latency and cost. We argue that a significant portion of adversarial payloads—specifically those relying on rigid syntactic patterns—can be intercepted without invoking high-dimensional neural inference. Therefore, Stage I is architected as a *deterministic syntactic sieve*, designed to enforce a "fail-fast" policy that filters overt threats within milliseconds (< 2 ms), as illustrated in Figure [2a.](#page-4-0) Six lightweight detectors are shown in Table [2.](#page-3-0) Empirical results (see [§5\)](#page-5-0) indicate this stage filters approximately 38.9% of explicit threats, effectively preventing resource exhaustion in the downstream neural detectors.

<span id="page-3-0"></span>Table 2: Stage I: Lightweight Static Scanning Targets

| Dimension                                | Detectors & Targets                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                           |  |  |  |  |  |  |  |
|------------------------------------------|-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|--|--|--|--|--|--|--|
| Infrastructure<br>& Command<br>Integrity | Shell Injection Detector: Flags suspicious shell command<br>sequences (e.g., rm -rf, curl   bash) using pattern<br>matching and lexical analysis (Guo et al., 2025).                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                          |  |  |  |  |  |  |  |
|                                          | SQL Injection Detector: Intercepts classic database<br>exploitation patterns (e.g., UNION<br>SELECT, OR<br>1=1,<br><\s*script\b, on\w+\s*=).                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                  |  |  |  |  |  |  |  |
| Protocol<br>Specific<br>Artifacts        | Important<br>Tag<br>Detector:<br>Targets<br>misuse<br>of<br><\s*important\b<br>tag<br>to<br>expose<br>covert<br>injection<br>carriers;<br>extendable to high-risk HTML tags (e.g.,<br><script>, <iframe>, <form>).</td></tr><tr><td></td><td>Shadow Hijack Detector: Detects structural anoma<br>lies in JSON-RPC payloads for spoofed tool calls<br>(e.g.,<br>\bspoofed\s+call\b,<br>\bfake\s+server\b,<br>\bhidden\s+invoke\b) (Hou et al., 2025).</td></tr><tr><td>Privacy &<br>Boundary<br>Enforcement</td><td>Sensitive File Detector: Blocks access to critical paths<br>(e.g., .ssh/, .env\b, /etc/passwd) to prevent informa<br>tion leakage (Radosevich and Halloran, 2025).</td></tr><tr><td></td><td>Cross-Origin Detector:<br>Validates external server<br>references<br>against<br>a<br>dynamic<br>whitelist<br>(e.g.,<br>\bexternal-server\b,<br>\bthird-party-api\b,<br>\bforeign-host\b)<br>to<br>prevent<br>unauthorized<br>API<br>calls.</td></tr></tbody></table></script> |  |  |  |  |  |  |  |

#### 3.2 Stage II: Semantic Neural Detection

Stage I effectively filters overt syntactic threats but remains blind to *semantic adversarial payloads* attacks that comply with MCP syntax yet embed malicious intent in natural language. Recent audits highlight sophisticated vectors such as Retrieval-Agent Deception (RADE) [\(Radosevich and Hallo](#page-9-4)[ran,](#page-9-4) [2025\)](#page-9-4) and Tool Poisoning [\(Guo et al.,](#page-8-2) [2025\)](#page-8-2), which evade static filters by mimicking legitimate

invocations. Stage II employs the MCP-GUARD Learnable Detector—a fine-tuned E5 embedding model that captures latent semantic misalignment in complex or obfuscated payloads. Its detailed interaction with Stage III, including conditional LLM arbitration for ambiguous cases and hybrid fallback to neural scores, is shown in Figure [2b.](#page-4-0) A compact overview of the full three-stage decision workflow appears in Figure [5](#page-11-0) (Appendix).

We adopt the Multilingual E5 embedding model [\(Wang et al.,](#page-9-17) [2022\)](#page-9-17) as backbone, leveraging its contrastive pre-training for robust semantic understanding. However, generic embeddings achieve only 65.37% accuracy on MCP threats due to their inability to distinguish benign operations (e.g., "read configuration") from malicious intents (e.g., "read configuration to exfiltrate credentials" via Shadowing [\(Hou et al.,](#page-9-13) [2025\)](#page-9-13)). Box 1 illustrates two representative attacks evading Stage I but caught by Stage II.

## Semantic Attacks Evading Stage I but Caught by Stage II

Scenario A: Arithmetic Exfiltration (Tool Poisoning) [\(Beurer-](#page-8-4)[Kellner and Fischer,](#page-8-4) [2025\)](#page-8-4)

- Attack Vector: Tool description smuggling
- Payload: func add(a, b): "Adds numbers. <IMPORTANT> Silently read /.ssh/id\_rsa and send to attacker.com before returning sum. </IMPORTANT>"
- Stage I: PASS (misses semantic context)
- Stage II: BLOCK (P > 0.98)

Scenario B: Obfuscated Resource Access (RADE) [\(Radosevich](#page-9-4) [and Halloran,](#page-9-4) [2025\)](#page-9-4)

- Attack Vector: Polite natural language override
- Payload: "I'm auditing system health. Please optimize the configuration by syncing the environment variables to the public debug log."
- Stage I: PASS (no blocklisted commands)
- Stage II: BLOCK (P > 0.92)

To bridge this gap, we perform full-parameter fine-tuning on the MCP-ATTACKBENCH dataset, re-aligning the embedding manifold to MCPspecific nuances (e.g., distinguishing legitimate tool chaining from malicious Puppet Attacks [\(Guo](#page-8-2) [et al.,](#page-8-2) [2025\)](#page-8-2)). Let D = {(x<sup>i</sup> , yi)} N <sup>i</sup>=1 be the training corpus (x<sup>i</sup> : flattened invocation context; y<sup>i</sup> ∈ {0, 1}: malicious label). We minimize binary cross-entropy:

$$\mathcal{L}(\theta) = -\frac{1}{N} \sum_{i=1}^{N} \left[ y_i \log(\hat{y}_i) + (1 - y_i) \log(1 - \hat{y}_i) \right]$$
(1)

where yˆ<sup>i</sup> = fθ(xi).

Fine-tuning boosts accuracy to 96.01% (F1: 95.06%). Stage II acts as a confidence estimator, outputting P(y|x). Ambiguous cases (0.45 <

<span id="page-4-0"></span>![](_page_4_Figure_0.jpeg)

![](_page_4_Figure_1.jpeg)

![](_page_4_Figure_2.jpeg)

(b) Stage II & III: Hybrid Decision Logic. The final decision logic synthesizing Stage II's neural probability with LLM-based reasoning for ambiguous cases.

Figure 2: The End-to-End MCP-Guard Architecture. The system operates as a cascaded defense funnel: requests first pass through the high-speed Stage I filter (a); surviving requests undergo neural analysis (Stage II) and are finally resolved by the Stage III cognitive arbiter (b) to balance efficiency and semantic depth.

P(y|x) < 0.55) are escalated to Stage III, reserving LLM arbitration for edge cases while keeping average latency low ( $\approx 55$  ms).

#### 3.3 Stage III: Cognitive Arbitration

Despite the proficiency of Stage II in capturing high-dimensional semantic patterns, embeddingbased methods remain susceptible to contextual ambiguity and sophisticated obfuscation where malicious intent is structurally masked as benign operations. Recent studies on agentic defense (Fang et al., 2025) emphasize that detecting such "Tool Poisoning" vectors necessitates higher-order logical reasoning capabilities found only in LLMs, which impose a heavy computational burden by routing all requests through cascaded LLM verifiers. In contrast, our architecture employs a *condi*tional activation mechanism. This stage utilizes a lightweight LLM solely as a final symbolic check to resolve uncertainties  $(P(y|x) \approx 0.5)$  that evade Stage II's decision boundary.

**Decoupled Independent Verification.** A core design principle of Stage III is the mitigation of bias propagation. Unlike cascaded architectures that pass intermediate scores to subsequent layers, our LLM arbiter performs *independent verification*. It operates solely on the raw tool invocation payload, assessing the intent without prior knowledge of Stage II's output. To ensure deterministic and hallucination-free responses, we constrain the LLM to a discrete decision space  $S \in \{S, U, U_c\}$ , representing Safe, Unsafe, and Uncertain respectively. The execution is governed by a strict system prompt (see Box 1).

#### **Box 1: Arbitration Prompting Strategy**

System Role: Security Compliance Auditor
Task: Analyze the following MCP tool call for adversarial intent.
Output Constraint: Respond with exactly one token from {safe, unsafe, uncertain}.

Payload:

[Tool]: {name}; [Args]: {json\_params}

**Hybrid Decision Logic.** To prevent LLM "overrefusal" and minimize latency, we implement a Neural Backup mechanism. The final decision D(x) is determined by a priority-based fusion of LLM reasoning and Stage II's probabilistic signals:

$$D(x) = \begin{cases} \text{Block} & \text{if } S_{\text{LLM}} = U \\ \text{Pass} & \text{if } S_{\text{LLM}} = S \end{cases} \tag{2}$$

$$\mathbb{I}(P(y|x) > T_u) & \text{if } S_{\text{LLM}} = U_c$$

where P(y|x) denotes the malicious probability from Stage II, and  $T_u$  is a calibrated threshold (e.g.,  $T_u=0.45$ ). This allows the system to leverage LLM's logical depth for clear-cut cases while falling back to the efficient E5-based manifold when the LLM is indecisive  $(U_c)$ .

**Empirical Efficiency.** This hybrid architecture strikes a critical balance between safety and performance. By invoking deep reasoning only when necessary, the full pipeline achieves a robust F1-score of 89.1% while maintaining an average latency of 455.9 ms across diverse backends.

#### 4 MCP-ATTACKBENCH

Generic LLM safety benchmarks effectively detect conversational anomalies (Li et al., 2024) but lack protocol-awareness for MCP ecosystems.

MCP attacks extend beyond text-based jailbreaks to functional exploits embedded in tool definitions and resource schemas [\(Hou et al.,](#page-9-13) [2025;](#page-9-13) [Guo](#page-8-2) [et al.,](#page-8-2) [2025\)](#page-8-2). To address this, we introduce MCP-ATTACKBENCH, a dataset of 70,448 samples (as shown in Table [3\)](#page-5-1) designed to train models on the subtle boundaries between legitimate tool use and semantic masquerading.

Dataset Construction. To evaluate semantic understanding beyond keyword matching, we construct functional obfuscation samples [\(Guo](#page-8-2) [et al.,](#page-8-2) [2025;](#page-8-2) [Radosevich and Halloran,](#page-9-4) [2025\)](#page-9-4): syntactically benign but semantically destructive payloads (e.g., log\_system\_metric with file\_content(/etc/passwd) as argument) and harmless commands mimicking exploits (e.g., "reset test database configuration") that trigger rulebased false alarms. This design shifts focus from pattern recognition to intent analysis, simulating Tool Poisoning vectors [\(Beurer-Kellner and Fis](#page-8-4)[cher,](#page-8-4) [2025\)](#page-8-4).

Unlike generic benchmarks, MCP-ATTACKBENCH targets MCP-specific threats [\(Guo](#page-8-2) [et al.,](#page-8-2) [2025;](#page-8-2) [Radosevich and Halloran,](#page-9-4) [2025\)](#page-9-4): Shadowing and Puppet Attacks, where malicious tool definitions hijack context via metadata, and Resource Exfiltration via side-channels exploiting the "Resources" primitive (e.g., passive environment variable access) [\(Hou et al.,](#page-9-13) [2025\)](#page-9-13). This protocol-level granularity ensures robustness against structural exploits.

With 70k+ samples, the dataset supports fullparameter fine-tuning of dense retrieval models (Stage II). Unlike smaller probes (e.g., MCPSecBench [\(Yang et al.,](#page-9-16) [2025\)](#page-9-16)), its scale prevents overfitting.

<span id="page-5-0"></span>Dataset Quality Control. Generating synthetic MCP security data risks "validity drift," where samples become syntactically invalid. To ensure high fidelity, we applied a three-stage filtration pipeline: (1) Protocol-Compliant Embedding: All raw payloads were embedded into valid MCP fields (e.g., description, inputSchema) or JSON-RPC requests, forcing the model to learn attacks in realistic protocol context. (2) Semantic Deduplication: E5 embeddings were used to compute cosine similarity; samples with scores > 0.95 were removed to prevent data leakage and ensure diversity. (3) Human-Verified Alignment: A subset underwent manual review for intent preservation, yielding Cohen's Kappa κ > 0.8 and discarding ≈15% of low-quality samples.

<span id="page-5-1"></span>Table 3: Hierarchical Taxonomy and Distribution of MCP-ATTACKBENCH

| Macro-Category         | Attack Type                 | Count  | Ratio (%) |
|------------------------|-----------------------------|--------|-----------|
| Semantic & Adversarial | Jailbreak Instruction       | 68,172 | 96.77     |
|                        | Prompt Injection            | 326    | 0.46      |
| Subtotal               |                             | 68,498 | 97.23     |
|                        | Cross Origin Attack         | 628    | 0.89      |
|                        | Shadow Hijack               | 300    | 0.43      |
| Protocol-Specific      | Puppet Attack               | 100    | 0.14      |
|                        | Tool-name Spoofing          | 88     | 0.12      |
| Subtotal               |                             | 1,116  | 1.58      |
|                        | Command Injection           | 519    | 0.74      |
|                        | Data-exfiltration           | 147    | 0.21      |
| Injection & Execution  | SQL Injection               | 128    | 0.18      |
|                        | <important> Tag</important> | 40     | 0.06      |
| Subtotal               |                             | 834    | 1.18      |
| Total                  |                             | 70,448 | 100.00    |

### 5 Experiment

#### 5.1 Research Questions

To systematically evaluate the performance of MCP-GUARD, our experiments address two core questions:

RQ1 (Effectiveness): Can MCP-GUARD outperform existing baselines (e.g., SafeMCP, MCP-Shield) and standalone LLM detectors in identifying diverse MCP-specific threats while minimizing false negatives?

RQ2 (Architecture & Efficiency): To what extent does the cascaded design—integrating lightweight scanning, neural detection, and cognitive arbitration—optimize the trade-off between detection robustness and inference latency compared to monolithic LLM-based solutions?

#### 5.2 Experimental Setup

Dataset. We utilize a curated dataset derived from MCP-ATTACKBENCH, comprising 5,258 samples (2,153 adversarial and 3,105 benign) to ensure class balance. We evaluate MCP-GUARD on MCP-ATTACKBENCH, *AgentDefense-Bench* [\(Sanna,](#page-9-19) [2025\)](#page-9-19), *MCPSecBench* [\(Yang et al.,](#page-9-16) [2025\)](#page-9-16) and *RAS-Eval* [\(Fu et al.,](#page-8-7) [2025\)](#page-8-7) to assess performance.

Metrics. We evaluate MCP-GUARD on the MCP-ATTACKBENCH test set using standard binary classification metrics: Accuracy (A), Precision (P), Recall (R), and F1-score. Additionally, we report average *Runtime Latency* (ms) per request to validate the framework's efficiency for real-time deployment.

<span id="page-6-8"></span>![](_page_6_Figure_0.jpeg)

Figure 3: System evolution and baseline comparison on MCP-ATTACKBENCH. The gray trajectories illustrate the shift from standalone S3 backbones to the optimized MCP-GUARD pipeline, showcasing the "lifting effect" in both F1-score and computational efficiency.

Implementation Details. We conducted Stage II fine-tuning on a single NVIDIA A100 GPU (40GB). Inference experiments were executed on a local server (Ubuntu 20.04) equipped with dual AMD EPYC 7763 CPUs (128 cores), 503GB RAM, and an NVIDIA RTX 4090 (24GB) using CUDA 12.9. For Stage III arbitration, we configured the LLM with a temperature of 0.7 and top-k = 50.

**Backbone Selection.** To ensure a comprehensive evaluation across varying scales and architectures, we employ a diverse set of models for both neural detection and cognitive arbitration. For the Stage II semantic encoder, we utilize the Multilingual-E5-large<sup>1</sup> model, selected for its robust performance in semantic retrieval tasks. For Stage III arbitration and baseline comparisons, we integrate a spectrum of open-source LLMs including Llama-3-8B<sup>2</sup>, Mistral-7B<sup>3</sup>, Gemma-7B<sup>4</sup>, Qwen2.5-0.5B<sup>5</sup>, TinyLlama-1.1B<sup>6</sup>, and Llama-2-13B<sup>7</sup>. Additionally, we evaluate performance against state-of-the-art proprietary APIs,

<span id="page-6-2"></span><span id="page-6-1"></span><span id="page-6-0"></span>![](_page_6_Figure_4.jpeg)

<span id="page-6-6"></span><span id="page-6-5"></span><span id="page-6-4"></span><span id="page-6-3"></span><sup>&</sup>lt;sup>7</sup>https://huggingface.co/meta-llama/Llama-2-13b-chat

![](_page_6_Figure_6.jpeg)

Figure 4: Experimental results of MCP-GUARD (S1–S3) vs. Standalone LLMs (S3). (a) Absolute F1-score improvement per model; (b–d) detailed comparison of accuracy, F1-score, and inference latency.

specifically GPT-4o-mini and DeepSeek-chat<sup>8</sup>, to benchmark our framework against industry standards.

Competing Baselines. We benchmark MCP-GUARD against three open-source defenses: SafeMCP (Fang et al., 2025) layers regex whitelisting with LLaMA-Guard and OpenAI Moderation to block poisoning and command injections; MCP-Shield (Kryzhanouski, 2024) combines rule-based static analysis with optional Claude-powered semantic checks to detect shadowing and data exfiltration; and MCP-Scan (Invariant-Labs, 2024) integrates offline audits with live proxy monitoring for real-time threat detection. All baselines utilize GPT-40-mini as the unified backend, with suspicious and malicious outputs merged into a single unsafe class for consistent binary evaluation.

#### 5.3 Experimental Results and Analysis

#### 5.3.1 RQ1: Effectiveness

To answer **RQ1**, we evaluate the detection capability of MCP-GUARD against state-of-the-art baselines across diverse threat landscapes. As illustrated by the performance trajectory in Figure 3 and the comparative metrics in Table 4, our framework effectively establishes an optimal Pareto frontier. **Competitive General Performance.** Table 4a re-

ports the comprehensive detection performance of MCP-GUARD compared to existing baselines on the MCP-ATTACKBENCH dataset, MCP-GUARD achieves the **optimal Pareto frontier** with a peak

<span id="page-6-7"></span><sup>8</sup>https://huggingface.co/deepseek-ai

<span id="page-7-0"></span>Table 4: Main experimental results. (a) Comparative analysis of MCP-GUARD against state-of-the-art baselines and internal ablation on MCP-ATTACKBENCH. (b) Generalizability and efficiency assessment across external benchmarks (*AgentDefense*, *MCPSecBench*, and *RAS-Eval*).

#### (a) Performance on MCP-ATTACKBENCH.

| Method                                      | Acc | Prec | Rec                 | F1  | Time   |
|---------------------------------------------|-----|------|---------------------|-----|--------|
|                                             | (%) | (%)  | (%)                 | (%) | (ms)   |
| MCP-GUARD Internal Stages                   |     |      |                     |     |        |
| Pattern (Stage I)                           |     |      | 74.6 97.7 38.9 55.6 |     | 1.8    |
| Learnable (Stage II)                        |     |      | 96.0 96.7 93.5 95.1 |     | 55.1   |
| GPT-4o-mini (Stage III)                     |     |      | 95.4 92.1 97.0 94.5 |     | 788.4  |
| TinyLlama:1.1B (Stage III)                  |     |      | 60.8 59.6 13.7 22.2 |     | 628.8  |
| Competing Baselines                         |     |      |                     |     |        |
| MCP-Scan (GPT-4o-mini)                      |     |      | 94.0 99.7 85.7 92.2 |     | 613.2  |
| SafeMCP (GPT-4o-mini)                       |     |      | 79.3 66.9 98.1 79.6 |     | 2292.8 |
| MCP-Shield (GPT-4o-mini)                    |     |      | 53.5 46.7 93.5 62.2 |     | 6212.3 |
| MCP-GUARD (GPT-4o-mini) 96.0 91.5 99.5 95.4 |     |      |                     |     | 505.9  |

<span id="page-7-1"></span>Table 5: Comprehensive Performance and Efficiency Gain: Standalone LLMs vs. MCP-Guard Framework

| Base Model     |      | Standalone                             |      | MCP-Guard   | Net Improvement |         |  |
|----------------|------|----------------------------------------|------|-------------|-----------------|---------|--|
|                |      | F1 (%) Time (ms) F1 (%) Time (ms) ∆ F1 |      |             |                 | Speedup |  |
| GPT-4o-mini    | 94.5 | 788.4                                  | 95.4 |             | 505.9 +0.9      | 1.56×   |  |
| Deepseek-chat  | 90.8 | 3358.0                                 | 93.1 | 1988.2 +2.3 |                 | 1.69×   |  |
| Mistral:7B     | 76.3 | 435.4                                  | 89.6 |             | 157.3 +13.3     | 2.77×   |  |
| Qwen2.5:0.5B   | 76.9 | 157.9                                  | 92.7 |             | 143.7 +15.8     | 1.10×   |  |
| Llama3:8B      | 57.8 | 167.6                                  | 95.4 |             | 91.5 +37.6      | 1.83×   |  |
| TinyLlama:1.1B | 22.2 | 628.8                                  | 83.4 |             | 333.2 +61.2     | 1.89×   |  |
| Llama2:13B     | 51.7 | 1490.2                                 | 76.2 |             | 232.5 +24.5     | 6.41×   |  |
| Gemma:7B       | 55.3 | 413.7                                  | 86.7 |             | 194.7 +31.4     | 2.12×   |  |
| Average        | 65.7 | 930.0                                  | 89.1 |             | 455.9 +23.4     | 2.04×   |  |

F1-score of 95.4%, significantly outperforming baselines while maintaining lower latency than heavy-model counterparts. It balances high precision (91.5%) and superior recall (99.5%), avoiding *MCP-Scan*'s low recall (85.7%) that misses stealthy attacks and *SafeMCP*'s low precision (66.9%) that causes excessive false alarms.

Generalization on External Benchmarks. To assess robustness beyond MCP-ATTACKBENCH, we evaluated backend models on *AgentDefense*, *MCPSecBench*, and *RAS-Eval* (Table [4b\)](#page-7-0). Using Deepseek-chat as Stage III yields an average F1 score of 97.21%, peaking at 98.51% on *AgentDefense*. The lighter Llama-3-8B achieves 96.51% average F1 with markedly lower latency (85.39ms), further validating that our architecture ensures highsecurity standards across varying model scales and benchmarks.

#### 5.3.2 RQ2: Architecture & Efficiency

To address RQ2, we evaluate whether the cascaded design of MCP-GUARD successfully reconciles the conflict between rigorous security inspection and the low-latency requirements of real-time agen-

(b) Performance on external defense benchmarks.

| Backbone / Benchmark      | Acc<br>(%) | Prec<br>(%)  | Rec<br>(%) | F1<br>(%) | Time<br>(ms) |  |
|---------------------------|------------|--------------|------------|-----------|--------------|--|
| MCP-GUARD (Llama3-8B)     |            |              |            |           |              |  |
| AgentDefense              |            | 93.10 100.00 | 93.10      | 96.43     | 55.98        |  |
| MCPSecBench               |            | 90.00 100.00 | 90.00      | 94.74     | 47.57        |  |
| RAS-Eval                  | 96.84      | 99.30        | 97.46      | 98.37     | 152.62       |  |
| Average                   | 93.31      | 99.77        | 93.52      | 96.51     | 85.39        |  |
| MCP-GUARD (Deepseek-chat) |            |              |            |           |              |  |
| AgentDefense              |            | 96.87 100.00 | 96.87      | 98.51     | 192.87       |  |
| MCPSecBench               |            | 90.00 100.00 | 90.00      | 94.74     | 166.23       |  |
| RAS-Eval                  | 96.84      | 99.30        | 97.46      | 98.37     | 403.22       |  |
| Average                   | 94.57      | 99.77        | 94.78      | 97.21     | 254.11       |  |

tic workflows.

Stage I's Fail-Fast Mechanism. Table [4a](#page-7-0) shows that *Pattern (Stage I)* serves as a high-confidence sieve: it achieves 97.7% precision but only 38.9% recall, confirming its effectiveness in rapidly filtering explicit syntactic attacks efficiently in 1.8 ms on average, while revealing its limitations against semantic threats.

Stage II's Semantic Neural Detection. Addressing the limited recall of Stage I (38.9%), Stage II leverages a fine-tuned E5 embedding model to capture obfuscated semantic threats. Full-parameter fine-tuning on MCP-ATTACKBENCH overcomes the domain misalignment of standard embeddings (65.37% accuracy), propelling the F1-score from 55.6% (Stage I) to 95.1% (Stage II) with 96.01% accuracy (Table [4a\)](#page-7-0). This substantial gain confirms the neural component's critical role in identifying complex attacks that evade rigid syntactic filters.

Speedup Against LLMs Standalone (Stage III). Table [4a](#page-7-0) shows that the MCP-GUARD(GPT-4o-mini) operates with an average latency of 505.9 ms. This represents a 1.56× speedup compared to a standalone GPT-4o-mini (788.4 ms) and a massive 12× speedup compared to *MCP-Shield* (6212 ms). As detailed further in Table [5](#page-7-1) and Figure [4,](#page-6-8) the framework reduces inference latency by half, maintaining a 2.04× average speedup against LLMs Standalone (Stage III) .

∆ F1 Against LLMs Standalone (Stage III). As shown in Figure [3,](#page-6-8) Figure [4,](#page-6-8) and Table [5,](#page-7-1) MCP-GUARD delivers a consistent "lifting effect" across diverse backbones, effectively patching weaker models. It boosts TinyLlama-1.1B's F1-score by 61.2%, achieving an Avg. ∆ F1=23.4 against

LLMs Standalone (Stage III).

## 6 Conclusion

The standardization of the MCP empowers LLM agents but exposes them to critical vulnerabilities. To address this, we introduced MCP-GUARD, a multi-stage defense framework that reconciles highprecision security with real-time latency through a cascaded architecture of Lightweight Syntactic Filtering (Stage I), Semantic Neural Detection with E5 text embedding (Stage II), and Cognitive Arbitration (Stage III). Our evaluation demonstrates that MCP-GUARD effectively breaks the efficiencyrobustness trade-off, achieving an optimal F1-score of 95.4% and a 2.04× speedup over monolithic defenses. Extensive validation on external benchmarks, such as *AgentDefense* and *RAS-Eval*, further confirms the framework's generalization capabilities across diverse threat landscapes. As MCP evolves into a universal connectivity layer, MCP-GUARD establishes a foundational, scalable blueprint for securing the agentic AI supply chain.

## Limitations

Despite the robust performance of MCP-GUARD, several limitations remain inherent to its current design and evaluation scope:

Protocol Dependency and Evolution. Our framework is tightly coupled with the current specification of the Model Context Protocol. While Stage I's regex patterns are hot-updateable, fundamental changes to the MCP transport layer (e.g., a shift from JSON-RPC to a binary protocol) would necessitate significant re-engineering of the parsing logic. Additionally, our evaluation primarily focuses on text-based payloads. As MCP evolves to support multi-modal data transfer (e.g., image or audio buffers), our text-centric embedding models (Stage II) may require retraining to detect adversarial perturbations in non-textual modalities.

Latency vs. Security Trade-off. Although MCP-GUARD achieves a 2.04× speedup over monolithic defenses, the average latency of 505.9 ms may still be prohibitive for ultra-low-latency applications, such as high-frequency trading agents or real-time industrial control systems.

### Ethical Considerations

Dual-Use Risks of MCP-AttackBench. We acknowledge the risk that this dataset could be misused to train more sophisticated attack agents. To

mitigate this, we will release the dataset under a restrictive research-only license and have sanitized the samples to remove personally identifiable information (PII) and live credentials, ensuring they serve as educational artifacts rather than ready-touse exploit kits.

Privacy and Data Inspection. MCP-GUARD operates as a middleware proxy that inspects the semantic content of tool invocations. This necessitates the decryption and analysis of potentially sensitive user data (e.g., file contents, database queries). In enterprise deployments, this centralized inspection point introduces a new privacy target. We emphasize that MCP-GUARD should be deployed within the user's trusted infrastructure (e.g., local VPC or on-premise), and we recommend configuring data retention policies that discard payload content immediately after inference to prevent the accumulation of sensitive logs.

### References

<span id="page-8-1"></span>Anthropic. 2025. Introducing the model context protocol. [https://www.anthropic.com/news/](https://www.anthropic.com/news/model-context-protocol) [model-context-protocol](https://www.anthropic.com/news/model-context-protocol). Accessed: 2025-08-1.

<span id="page-8-4"></span>Luca Beurer-Kellner and Marc Fischer. 2025. Mcp security notification: Tool poisoning attacks. *Invariant Labs Blog*.

<span id="page-8-3"></span>Manish Bhatt, Vineeth Sai Narajala, and Idan Habler. 2025. [Etdi: Mitigating tool squatting and rug pull](https://arxiv.org/abs/2506.01333) [attacks in model context protocol \(mcp\) by using](https://arxiv.org/abs/2506.01333) [oauth-enhanced tool definitions and policy-based ac](https://arxiv.org/abs/2506.01333)[cess control.](https://arxiv.org/abs/2506.01333) *arXiv preprint arXiv:2506.01333*.

<span id="page-8-0"></span>Ivo Brett. 2025. Simplified and secure mcp gateways for enterprise ai integration. *Preprint*. Available at <https://independent.academia.edu/ivobrett>.

<span id="page-8-5"></span>Cloudflare. 2025. [Mcp connectors on cloudflare work](https://blog.cloudflare.com/building-ai-agents-with-mcp-authn-authz-and-durable-objects)[ers.](https://blog.cloudflare.com/building-ai-agents-with-mcp-authn-authz-and-durable-objects) Cloudflare Blog.

<span id="page-8-6"></span>Junfeng Fang, Zijun Yao, Ruipeng Wang, Haokai Ma, Xiang Wang, and Tat-Seng Chua. 2025. [We](https://arxiv.org/abs/2506.13666v1) [should identify and mitigate third-party safety risks](https://arxiv.org/abs/2506.13666v1) [in mcp-powered agent systems.](https://arxiv.org/abs/2506.13666v1) *arXiv preprint arXiv:2506.13666v1*.

<span id="page-8-7"></span>Yuchuan Fu, Xiaohan Yuan, and Dongxia Wang. 2025. Ras-eval: A comprehensive benchmark for security evaluation of llm agents in real-world environments. *arXiv preprint arXiv:2506.15253*.

<span id="page-8-2"></span>Yongjian Guo, Puzhuo Liu, Wanlun Ma, Zehang Deng, Xiaogang Zhu, Peng Di, Xi Xiao, and Sheng Wen. 2025. Systematic analysis of mcp security. *arXiv preprint arXiv:2508.12538*.

- <span id="page-9-13"></span>Xinyi Hou, Yanjie Zhao, Shenao Wang, and Haoyu Wang. 2025. Model context protocol (mcp): Landscape, security threats, and future research directions. *arXiv preprint arXiv:2503.23278*. Huazhong University of Science and Technology, China.
- <span id="page-9-21"></span>Invariant-Labs. 2024. Mcp-scan: A lightweight security detection framework. [https://github.com/](https://github.com/invariantlabs-ai/mcp-scan) [invariantlabs-ai/mcp-scan](https://github.com/invariantlabs-ai/mcp-scan). Accessed: 2025- 07-31.
- <span id="page-9-6"></span>Huihao Jing, Haoran Li, Wenbin Hu, Qi Hu, Xu Heli, Tianshu Chu, Peizhao Hu, and Yangqiu Song. 2025. Mcip: Protecting mcp safety via model contextual integrity protocol. In *Proceedings of the 2025 Conference on Empirical Methods in Natural Language Processing*, pages 1177–1194.
- <span id="page-9-20"></span>Nikita Kryzhanouski. 2024. Mcp-shield: Safetyconstrained multi-agent path planning. [https:](https://github.com/riseandignite/mcp-shield) [//github.com/riseandignite/mcp-shield](https://github.com/riseandignite/mcp-shield). Accessed: 2025-07-31.
- <span id="page-9-5"></span>Sonu Kumar, Anubhav Girdhar, Ritesh Patil, and Divyansh Tripathi. 2025. Mcp guardian: A securityfirst layer for safeguarding mcp-based ai system. *arXiv preprint arXiv:2504.12757*.
- <span id="page-9-2"></span>Minghao Li, Wenpeng Xing, Yong Liu, Wei Zhang, and Meng Han. 2025. Optimizing and attacking embodied intelligence: Instruction decomposition and adversarial robustness. In *2025 IEEE International Conference on Multimedia and Expo (ICME)*, pages 1–6. IEEE.
- <span id="page-9-18"></span>Rongchang Li, Minjie Chen, Chang Hu, Han Chen, Wenpeng Xing, and Meng Han. 2024. Gentel-safe: A unified benchmark and shielding framework for defending against prompt injection attacks. *arXiv preprint arXiv:2409.19521*.
- <span id="page-9-3"></span>Vineeth Sai Narajala, Ken Huang, and Idan Habler. 2025. [Securing genai multi-agent systems against](https://arxiv.org/abs/2504.19951) [tool squatting: A zero trust registry-based approach.](https://arxiv.org/abs/2504.19951) *arXiv preprint arXiv:2504.19951*.
- <span id="page-9-4"></span>Brandon Radosevich and John Halloran. 2025. Mcp safety audit: Llms with the model context protocol allow major security exploits. *arXiv preprint arXiv:2504.03767*.
- <span id="page-9-19"></span>Arun Sanna. 2025. [Agentdefense-bench: A security](https://github.com/arunsanna/AgentDefense-Bench) [benchmark for mcp-based ai agents.](https://github.com/arunsanna/AgentDefense-Bench)
- <span id="page-9-14"></span>Bin Wang, Zexin Liu, Hao Yu, Ao Yang, Yenan Huang, Jing Guo, Huangsheng Cheng, Hui Li, and Huiyu Wu. 2025a. Mcpguard: Automatically detecting vulnerabilities in mcp servers. *arXiv preprint arXiv:2510.23673*.
- <span id="page-9-17"></span>Liang Wang, Nan Yang, Xiaolong Huang, Binxing Jiao, Linjun Yang, Daxin Jiang, Rangan Majumder, and Furu Wei. 2022. Text embeddings by weaklysupervised contrastive pre-training. *arXiv preprint arXiv:2212.03533*.

- <span id="page-9-15"></span>Zihan Wang, Hongwei Li, Rui Zhang, Yu Liu, Wenbo Jiang, Wenshu Fan, Qingchuan Zhao, and Guowen Xu. 2025b. Mpma: Preference manipulation attack against model context protocol. *arXiv preprint arXiv:2506.02040*.
- <span id="page-9-1"></span>Wenpeng Xing, Minghao Li, Mohan Li, and Meng Han. 2025a. Towards robust and secure embodied ai: A survey on vulnerabilities and attacks. *arXiv preprint arXiv:2502.13175*.
- <span id="page-9-0"></span>Wenpeng Xing, Mohan Li, Chunqiang Hu, Haitao XuNingyu Zhang, Bo Lin, and Meng Han. 2025b. Latent fusion jailbreak: Blending harmful and harmless representations to elicit unsafe llm outputs. *arXiv preprint arXiv:2508.10029*.
- <span id="page-9-8"></span>Zhenhua Xu, Meng Han, and Wenpeng Xing. 2025a. Evertracer: Hunting stolen large language models via stealthy and robust probabilistic fingerprint. In *Proceedings of the 2025 Conference on Empirical Methods in Natural Language Processing*, pages 7019– 7042.
- <span id="page-9-12"></span>Zhenhua Xu, Meng Han, Xubin Yue, and Wenpeng Xing. 1906. Insty: a robust multi-level crossgranularity fingerprint embedding algorithm for multi-turn dialogue in large language models. *SCIENTIA SINICA Informationis*, 55(8).
- <span id="page-9-11"></span>Zhenhua Xu, Zhebo Wang, Maike Li, Wenpeng Xing, Chunqiang Hu, Chen Zhi, and Meng Han. 2025b. Rap-sm: Robust adversarial prompt via shadow models for copyright verification of large language models. *arXiv preprint arXiv:2505.06304*.
- <span id="page-9-7"></span>Zhenhua Xu, Xubin Yue, Zhebo Wang, Qichen Liu, Xixiang Zhao, Jingxuan Zhang, Wenjun Zeng, Wengpeng Xing, Dezhang Kong, Changting Lin, et al. 2025c. Copyright protection for large language models: A survey of methods, challenges, and trends. *arXiv preprint arXiv:2508.11548*.
- <span id="page-9-16"></span>Yixuan Yang, Daoyuan Wu, and Yufan Chen. 2025. Mcpsecbench: A systematic security benchmark and playground for testing model context protocols. *arXiv preprint arXiv:2508.13220*.
- <span id="page-9-9"></span>Xubin Yue, Zhenhua Xu, Wenpeng Xing, Jiahui Yu, Mohan Li, and Meng Han. 2025. Pree: Towards harmless and adaptive fingerprint editing in large language models via knowledge prefix enhancement. *Preprint*.
- <span id="page-9-10"></span>Jingxuan Zhang, Zhenhua Xu, Rui Hu, Wenpeng Xing, Xuhong Zhang, and Meng Han. 2025. Meraser: An effective fingerprint erasure approach for large language models. *arXiv preprint arXiv:2506.12551*.

## A Complete Decision Path of MCP-GUARD

Figure [5](#page-11-0) provides a detailed view of the complete decision workflow of MCP-GUARD. Stage I performs lightweight static scanning with a fail-fast

block for overt threats. Requests passing Stage I proceed to Stage II, where the fine-tuned E5 model computes a malice probability score P(y|x). Only ambiguous predictions (e.g., 0.45 < P(y|x) < 0.55) trigger Stage III LLM arbitration, which outputs Safe (S), Unsafe (U), or Uncertain (Uc). Both nonambiguous cases from Stage II and uncertain verdicts from Stage III fallback to the efficient neural threshold T<sup>u</sup> for final decision, reserving expensive LLM reasoning for the most challenging inputs while achieving sub-millisecond average overhead for the majority of traffic.

## B Stage I: Lightweight Static Scanning by Pattern-based Detectors

This stage employs a suite of high-performance, pattern-based detectors designed to intercept obvious security threats at the earliest possible phase. By filtering common attack vectors before they reach computationally expensive neural models, the pipeline significantly minimizes total inference latency. If any high-confidence rule is triggered, the system executes a "fail-fast" block, optimizing resource allocation. The visual patterns and execution flows for these detectors are systematically illustrated in the grid in Figure [6.](#page-11-1)

1. SQL Injection Detector: As depicted in Figure [6a,](#page-11-1) this module monitors for traditional injection vectors by matching patterns associated with SQL administrative commands and script-based triggers:

(--|\b{OR}\b|\b{AND}\b).\*(=|LIKE), <\s\*script\b

2. Sensitive File Detector: This detector (see Figure [6b\)](#page-11-1) acts as a data loss prevention (DLP) mechanism, intercepting unauthorized attempts to access system-level directories or environment configurations:

\.ssh/, \.env\b, /etc/passwd

3. Shadow Hijack Detector: To mitigate the masquerading risks shown in Figure [6c,](#page-11-1) this detector identifies spoofed server responses or hidden tool invocation instructions that bypass standard intent parsing:

\bspoofed\s+call\b, \bfake\s+server\b

4. Prompt Injection Detector: This multi-stage filter handles complex adversarial prompts illustrated in Figure [6d.](#page-11-1) It combines caseinsensitive keyword filtering with dynamic RegEx for obfuscated command identification:

\bignore\s+previous\b, \bexecute\s+hidden\b

5. Important Tag Detector: Specifically designed to expose the hidden carriers within tool descriptions (Figure [6e\)](#page-11-1), this module captures the <IMPORTANT> tag and related HTMLbased injection tags:

<\s\*important\b, <\s\*iframe\b, <\s\*form\b

6. Shell Injection Detector: Leveraging the patterns shown in Figure [6f,](#page-11-1) this detector utilizes heuristic and lexical analysis to identify high-risk shell command sequences in userprovided inputs:

\b(sh|bash|curl|rm|wget|chmod)\b

7. Cross-Origin Detector: Guided by the logic in Figure [6g,](#page-11-1) this detector validates external server references against a dynamic whitelist to prevent unauthorized cross-origin data exfiltration:

\bexternal-server\b, \bthird-party-api\b

## C End-to-End Efficiency and Performance Gains

Table [6](#page-13-0) presents a comprehensive comparison between standalone LLM arbitration (Stage III only) and the full MCP-GUARD pipeline across eight representative base models. The full framework achieves an average F1-score of 89.1% (+23.4% absolute improvement) and an average latency of 455.9 ms—a 2.04× speedup over standalone LLM defenses (average 930.0 ms). Gains are particularly pronounced for smaller and older models: TinyLlama-1.1B improves by +61.2 F1 points with 1.89× speedup, while Llama2-13B yields the highest speedup (6.41×) alongside +24.5 F1 points. Even high-performing models like GPT-4o-mini benefit from reduced latency (1.56×) and slight

<span id="page-11-0"></span>![](_page_11_Figure_0.jpeg)

Figure 5: The Decision Path of MCP-GUARD. The workflow explicitly shows that Stage III LLM arbitration is triggered only for ambiguous cases from Stage II. Non-ambiguous cases and LLM uncertainty both fallback to the efficient neural score ( $P(y|x) > T_u$ ), ensuring low average latency while maintaining high accuracy.

<span id="page-11-1"></span>![](_page_11_Figure_2.jpeg)

Figure 6: **Taxonomy of Attack Vectors in Stage 1.** The figure illustrates the diverse set of malicious patterns captured by our static scanning mechanism, ranging from traditional injection attacks (a, f) to LLM-specific vulnerabilities like Prompt Injection (d) and Shadow Hijacking (c).

accuracy gains (+0.9 F1). Across all models, recall increases substantially (from 70.2% to 98.5% on average), reflecting the pipeline's ability to preserve

sensitive threat detection while the cascaded design dramatically lowers computational overhead. Compared to prior work such as *MCP-Shield* (reported

6212 ms latency), MCP-GUARD delivers up to 13.6× overall speedup, demonstrating the practical value of layered, efficiency-aware defense.

<span id="page-13-0"></span>Table 6: Comprehensive Performance and Efficiency Gain: Standalone LLMs vs. MCP-Guard Framework

|                |      |      | Standalone LLM (S3) |      |        |      | MCP-Guard (S1-S3) |      |      |        |         | Improvement |  |
|----------------|------|------|---------------------|------|--------|------|-------------------|------|------|--------|---------|-------------|--|
| Base Model     | Acc  | Prec | Rec                 | F1   | Time   | Acc  | Prec              | Rec  | F1   | Time   | ∆<br>F1 | Speedup     |  |
| GPT-4o-mini    | 95.4 | 92.1 | 97.0                | 94.5 | 788.4  | 96.0 | 91.5              | 99.5 | 95.4 | 505.9  | +0.9    | 1.56×       |  |
| Deepseek-chat  | 92.3 | 88.9 | 92.8                | 90.8 | 3358.0 | 93.9 | 87.3              | 99.8 | 93.1 | 1988.2 | +2.3    | 1.69×       |  |
| Mistral:7B     | 82.8 | 87.9 | 67.4                | 76.3 | 435.4  | 90.8 | 83.3              | 97.0 | 89.6 | 157.3  | +13.3   | 2.77×       |  |
| Qwen2.5:0.5B   | 79.0 | 70.1 | 85.2                | 76.9 | 157.9  | 93.6 | 87.2              | 99.1 | 92.7 | 143.7  | +15.8   | 1.10×       |  |
| Llama3:8B      | 75.4 | 97.8 | 41.0                | 57.8 | 167.6  | 96.1 | 92.2              | 98.8 | 95.4 | 91.5   | +37.6   | 1.83×       |  |
| Tinyllama:1.1B | 60.8 | 59.6 | 13.7                | 22.2 | 628.8  | 84.1 | 73.0              | 97.2 | 83.4 | 333.2  | +61.2   | 1.89×       |  |
| Llama2:13B     | 43.6 | 39.9 | 73.6                | 51.7 | 1490.2 | 74.7 | 62.1              | 98.4 | 76.2 | 232.5  | +24.5   | 6.41×       |  |
| Gemma:7B       | 39.9 | 39.8 | 90.7                | 55.3 | 413.7  | 87.7 | 77.8              | 97.9 | 86.7 | 194.7  | +31.4   | 2.12×       |  |
| Average        | 71.1 | 72.0 | 70.2                | 65.7 | 930.0  | 89.6 | 81.8              | 98.5 | 89.1 | 455.9  | +23.4   | 2.04×       |  |