<!-- extracted-by: marker -->
# SHIELDAGENT: Shielding Agents via Verifiable Safety Policy Reasoning

Zhaorun Chen <sup>1</sup> Mintong Kang <sup>2</sup> Bo Li 1 2

# Abstract

Autonomous agents powered by foundation models have seen widespread adoption across various real-world applications. However, they remain highly vulnerable to malicious instructions and attacks, which can result in severe consequences such as privacy breaches and financial losses. More critically, existing guardrails for LLMs are not applicable due to the complex and dynamic nature of agents. To tackle these challenges, we propose SHIELDAGENT, the first guardrail agent designed to enforce explicit safety policy compliance for the action trajectory of other protected agents through logical reasoning. Specifically, SHIELDAGENT first constructs a safety policy model by extracting verifiable rules from policy documents and structuring them into a set of action-based probabilistic rule circuits. Given the action trajectory of the protected agent, SHIELDAGENT retrieves relevant rule circuits and generates a shielding plan, leveraging its comprehensive tool library and executable code for formal verification. In addition, given the lack of guardrail benchmarks for agents, we introduce SHIELDAGENT-BENCH, a dataset with 3K safety-related pairs of agent instructions and action trajectories, collected via SOTA attacks across 6 web environments and 7 risk categories. Experiments show that SHIELDAGENT achieves SOTA on SHIELDAGENT-BENCH and three existing benchmarks, outperforming prior methods by 11.3% on average with a high recall of 90.1%. Additionally, SHIELDAGENT reduces API queries by 64.7% and inference time by 58.2%, demonstrating its high precision and efficiency in safeguarding agents. Our project is available and continuously maintained here: [https:](https://shieldagent-aiguard.github.io/) [//shieldagent-aiguard.github.io/](https://shieldagent-aiguard.github.io/)

<sup>1</sup>University of Chicago, Chicago IL, USA <sup>2</sup>University of Illinois at Urbana-Champaign, Champaign IL, USA. Correspondence to: Zhaorun Chen, Bo Li <{zhaorun, bol}@uchicago.edu>.

*Proceedings of the* 42 nd *International Conference on Machine Learning*, Vancouver, Canada. PMLR 267, 2025. Copyright 2025 by the author(s).

# 1. Introduction

LLM-based autonomous agents are rapidly gathering momentum across various applications, integrating their ability to call external tools and make autonomous decisions in real-world tasks such as web browsing [\(Zhou et al.,](#page-9-0) [2023\)](#page-9-0), GUI navigation [\(Lin et al.,](#page-9-1) [2024\)](#page-9-1), and embodied control [\(Mao et al.,](#page-9-2) [2023\)](#page-9-2). Among these, *LLM-based web agents*, such as OpenAI's Operator [\(OpenAI,](#page-9-3) [2025b\)](#page-9-3), deep research agent [\(OpenAI,](#page-9-4) [2025a\)](#page-9-4), and Anthropic's computer assistant agent [\(Anthropic,](#page-8-0) [2024\)](#page-8-0), have become particularly prominent, driving automation in areas like online shopping, stock trading, and information retrieval.

Despite their growing capabilities, users remain reluctant to trust current web agents with high-stakes data and assets, as they are still highly vulnerable to malicious instructions and adversarial attacks [\(Chen et al.,](#page-8-1) [2024c;](#page-8-1) [Wu et al.,](#page-9-5) [2025\)](#page-9-5), which can lead to severe consequences such as privacy breaches and financial losses [\(Levy et al.,](#page-8-2) [2024\)](#page-8-2). Existing guardrails primarily focus on LLMs as *models*, while failing to safeguard them as *agentic systems* due to two key challenges: (1) LLM-based agents operate through sequential interactions with dynamic environments, making it difficult to capture unsafe behaviors that emerge over time [\(Xiang](#page-9-6) [et al.,](#page-9-6) [2024\)](#page-9-6); (2) Safety policies governing these agents are often complex and encoded in lengthy regulation documents (e.g. *EU AI Act* [\(Act,](#page-8-3) [2024\)](#page-8-3)) or corporate policy handbooks [\(GitLab,](#page-8-4) [2025\)](#page-8-4), making it difficult to systematically extract, verify, and enforce rules across different platforms [\(Zeng et al.,](#page-9-7) [2024\)](#page-9-7). As a result, safeguarding the safety of LLM-based web agents remains an open challenge.

To address these challenges, we introduce SHIELDAGENT, the first LLM-based guardrail agent designed to shield the action trajectories of other LLM-based autonomous agents, ensuring explicit safety compliance through probabilistic logic reasoning and verification. Unlike existing approaches that rely on simple text-based filtering [\(Xiang et al.,](#page-9-6) [2024\)](#page-9-6), SHIELDAGENT accounts for the uniqueness of agent actions and explicitly verifies them against relevant policies in an efficient manner. At its core, SHIELDAGENT automatically constructs a robust safety policy model by extracting verifiable rules from policy documents, iteratively refining them, and grouping them based on different action types to form a set of structured, action-based probabilistic rule

circuits [\(Kang & Li,](#page-8-5) [2024\)](#page-8-5). During inference, SHIELDA-GENT only verifies the relevant rule circuits corresponding to the invoked action, ensuring both precision and efficiency. Specifically, SHIELDAGENT references from a hybrid memory module of both *long-term shielding workflows* and *shortterm interaction history*, generates a shielding plan with specialized operations from a rich tool library, and runs formal verification code. Once a rule is verified, SHIELDAGENT performs probabilistic inference within the circuits and provides a binary safety label, identifies any violated rules, and generates detailed explanations to justify its decision.

While evaluating these guardrails is critical for ensuring agent safety, existing benchmarks remain small in scale, cover limited risk categories, and lack explicit risk definitions (see Table [1\)](#page-5-0). Therefore, we introduce SHIELDAGENT-BENCH, the first comprehensive agent guardrail benchmark comprising 2K safety-related pairs of agent instructions and trajectories across six web environments and seven risk categories. Specifically, each unsafe agent trajectory is generated under two types of attacks [\(Chen et al.,](#page-8-1) [2024c;](#page-8-1) [Xu et al.,](#page-9-8) [2024\)](#page-9-8) based on different perturbation sources (i.e., *agentbased* and *environment-based*), capturing risks present both within the agent system and the external environments.

We conduct extensive experiments demonstrating that SHIELDAGENT achieves SOTA performance on both SHIELDAGENT-BENCH and three existing benchmarks (i.e., ST-WebAgentBench [\(Levy et al.,](#page-8-2) [2024\)](#page-8-2), VWA-Adv [\(Wu](#page-9-5) [et al.,](#page-9-5) [2025\)](#page-9-5), and AgentHarm [\(Andriushchenko et al.\)](#page-8-6)). Specifically, SHIELDAGENT outperforms the previous best guardrail method by 11.3% on SHIELDAGENT-BENCH, and 7.4% on average across existing benchmarks. Grounded on robust safety policy reasoning, it achieves the lowest false positive rate at 4.8% and a high recall rate of violated rules at 90.1%. Additionally, SHIELDAGENT reduces the number of closed-source API queries by 64.7% and inference time by 58.2%, demonstrating its ability to effectively shield LLM agents' actions while significantly improving efficiency and reducing computational overhead.

# 2. Related Works

### 2.1. Safety of LLM Agents

While LLM agents are becoming increasingly capable, numerous studies have demonstrated their susceptibility to manipulated instructions and vulnerability to adversarial attacks, which often result in unsafe or malicious actions [\(Levy et al.,](#page-8-2) [2024;](#page-8-2) [Andriushchenko et al.;](#page-8-6) [Zhang et al.,](#page-9-9) [2024b\)](#page-9-9). Existing attack strategies against LLM agents can be broadly classified into the following two categories.

(1) Agent-based attacks, where adversaries manipulate internal components of the agent, such as instructions [\(Guo](#page-8-7) [et al.;](#page-8-7) [Zhang et al.,](#page-9-10) [2024c\)](#page-9-10), memory modules or knowledge

bases [\(Chen et al.,](#page-8-1) [2024c;](#page-8-1) [Jiang et al.,](#page-8-8) [2024\)](#page-8-8), and tool libraries [\(Fu et al.,](#page-8-9) [2024;](#page-8-9) [Zhang et al.,](#page-9-11) [2024a\)](#page-9-11). These attacks are highly effective and can force the agent to execute arbitrary malicious requests. However, they typically require some access to the agent's internal systems or training data.

(2) Environment-based attacks, which exploit vulnerabilities in the environment that the agents interact with to manipulate their behavior [\(Liao et al.,](#page-9-12) [2024\)](#page-9-12), such as injecting malicious HTML elements [\(Xu et al.,](#page-9-8) [2024\)](#page-9-8) or deceptive web pop-ups [\(Zhang et al.,](#page-9-13) [2024d\)](#page-9-13). Since the environment is less controlled than the agent itself, these attacks are easier to execute in real world but may have a lower success rate.

Both attack types pose significant risks, leading to severe consequences such as life-threatening failures [\(Chen](#page-8-1) [et al.,](#page-8-1) [2024c\)](#page-8-1), privacy breaches [\(Liao et al.,](#page-9-12) [2024\)](#page-9-12), and financial losses [\(Andriushchenko et al.\)](#page-8-6). Therefore in this work, we account for both *agent-based* and *environmentbased* adversarial perturbations in the design of SHIELD-AGENT. Besides, we leverage SOTA attacks [\(Chen et al.,](#page-8-1) [2024c;](#page-8-1) [Xu et al.,](#page-9-8) [2024\)](#page-9-8) from both categories to construct our SHIELDAGENT-BENCH dataset which involves diverse risky web agent trajectories across various environments.

### 2.2. LLM Guardrails

While LLM agents are highly vulnerable to adversarial attacks, existing guardrail mechanisms are designed for LLMs as *models* rather than *agents*, leaving a critical gap in safeguarding their sequential decision-making processes [\(An](#page-8-6)[driushchenko et al.\)](#page-8-6). Current guardrails primarily focus on filtering harmful inputs and outputs, such as LlamaGuard [\(Inan et al.,](#page-8-10) [2023\)](#page-8-10) for text-based LLMs, Llava-Guard [\(Helff et al.,](#page-8-11) [2024\)](#page-8-11) for image-based multimodal LLMs, and SafeWatch [\(Chen et al.,](#page-8-12) [2024a\)](#page-8-12) for video generative models. However, these methods focus solely on content moderation, failing to address the complexities of action sequences, where vulnerabilities often emerge over time [\(Debenedetti et al.,](#page-8-13) [2024\)](#page-8-13). While GuardAgent [\(Xi](#page-9-6)[ang et al.,](#page-9-6) [2024\)](#page-9-6) preliminarily explores the challenge of guardrailing LLM agents with another LLM agent, it focus solely on textual space and still relies on the model's internal knowledge rather than explicitly enforcing compliance with external safety policies and regulations [\(Zeng et al.,](#page-9-7) [2024\)](#page-9-7), limiting its effectiveness in real-world applications. To our knowledge, SHIELDAGENT is the first multimodal LLM-based agent to safeguard action sequences of other LLM agents via probabilistic policy reasoning to ensure explicit and efficient policy compliance.

# 3. SHIELDAGENT

As illustrated in Fig. [1,](#page-2-0) SHIELDAGENT consists of two main stages: (1) constructing an automated action-based safety policy model (ASPM) that encodes safety constraints from

<span id="page-2-0"></span>![](_page_2_Figure_1.jpeg)

Figure 1: **Overview of SHIELDAGENT. (Top)** From AI regulations (e.g. EU AI Act) and platform-specific safety policies, SHIELDAGENT first extracts verifiable rules and iteratively refines them to ensure each rule is accurate, concrete, and atomic. It then clusters these rules and assembles them into an action-based safety policy model, associating actions with their corresponding constraints (with weights learned from real or simulated data). **(Bottom)** During inference, SHIELDAGENT retrieves relevant rule circuits w.r.t. the invoked action and performs action verification. By referencing existing workflows from a hybrid memory module, it first generates a step-by-step shielding plan with operations supported by a comprehensive tool library to assign truth values for all predicates, then produces executable code to perform formal verification for actions. Finally, it runs probabilistic inference in the rule circuits to provide a safety label and explanation and reports violated rules.

government regulations or platform-wide policies, and (2) leveraging the ASPM to verify and enforce these safety policies on the shielded agents' actions via robust probabilistic safety policy reasoning. Notably, while SHIELDAGENT can be generalized to guardrail arbitrary agents and environments, we use web agents as an example for illustration.

### 3.1. Overview

Let  $\pi_{\rm agent}$  be the action policy of an agent we aim to shield, where at each timestep i, the agent receives an observation  $o_i$  from the environment and then produces an action  $a_i \sim \pi_{\rm agent}(o_i)$  to progressively interacts with the environment.

Then SHIELDAGENT  $\mathcal{A}_s$  is a guardrail agent aiming to safe-guard the action of  $\pi_{\text{agent}}$ , leveraging ASPM which encodes safety constraints in a logical knowledge graph  $\mathcal{G}_{\text{ASPM}}$  with n rules, as well as a variety of tools and a hybrid memory module. Our guardrail task can be formulated as:

$$(l_s, V_s, T_s) = \mathcal{A}_s(a_i \mid (o_i, \mathcal{H}_{\leq i}, \mathcal{G}_{ASPM})) \tag{1}$$

where  $\mathcal{A}_s$  takes as input the past interaction history  $\mathcal{H}_{< i} = \{(o_j, a_j) | j \in [1, i-1]\}$ , the observation  $o_i$ , and the invoked action  $a_i$  at step i, and consequently produces: (1) a binary flag  $l_s$  indicating whether action  $a_i$  is safe; (2) a list of flags indicating rule violation  $V_s = \{l_j^i | j \in [1, n]\}$ , if applicable; (3) a textual explanation  $T_s$  justifying the shielding decision.

### 3.2. Action-based Safety Policy Model

To achieve tractable verification, we first construct an action-based safety policy model (ASPM) that structurally encodes all safety constraints in a logical knowledge graph  $\mathcal{G}_{ASPM}$ .

### 3.2.1. OVEWVIEW OF ASPM

Specifically, all constraints are represented as linear temporal logic (LTL) rules (Zhu et al., 2017) where each rule includes corresponding atomic predicates as decision variables<sup>1</sup>. Please refer to §3.2.2 for details. Thus let  $\mathcal{P}$ ,  $\mathcal{R}$  denote the predicate and rule space respectively, we have:

$$\mathcal{G}_{ASPM} = (\mathcal{P}, \mathcal{R}, \pi_{\theta}) \text{ s.t. } \mathcal{P} = \{\mathcal{P}_{a}, \mathcal{P}_{s}\}, \mathcal{R} = \{\mathcal{R}_{a}, \mathcal{R}_{p}\}$$
 (2)

where  $\pi_{\theta}$  denotes the probabilistic logic model (parameterized by  $\theta$ ) which organizes the rules (see §3.2.4). Specifically,  $\mathcal{G}_{\text{ASPM}}$  partitions  $\mathcal{P}$  into state predicates  $p_s \in \mathcal{P}_s$  to represent system states or environmental conditions, and action predicates  $p_a \in \mathcal{P}_a$  to represent target actions. Consequently,  $\mathcal{R}$  is divided into action rules  $\mathcal{R}_a$  which encodes safety specifications for target actions, and physical rules  $\mathcal{R}_p$  which capture internal constraints on system variables. Specifically, while  $\mathcal{R}_p$  does not directly constrain actions in  $\mathcal{P}_a$ , these knowledge rules are critical for the logical reason-

<span id="page-2-1"></span><sup>&</sup>lt;sup>1</sup>Each predicate can be assigned a boolean value per time step to describe the agent system variables or environment state.

ing in ASPM, enhancing the robustness of our shield (Kang & Li, 2024). Therefore, by structuring the solution space this way, we achieve a clear and manageable verification of target actions. Refer to Appendix A.2 for more details.

Specifically, we construct ASPM from policy documents via the following steps: (1) Extract structured safety rules from government regulations (Act, 2024), corporate policies (Git-Lab, 2025), and user-provided constraints; (2) Refine these rules iteratively for better clarity, verifiability, and efficiency; (3) Cluster the optimized rules by different agent actions and obtain a set of action-based rule circuits (Kisa et al., 2014) where each circuit associates an agent action with relevant rules for verification; (4) Train the ASPM by learning rule weights from either real-world interactions or simulated data, ensuring adaptive and robust policy verification.

### <span id="page-3-0"></span>3.2.2. AUTOMATIC POLICY AND RULE EXTRACTION

Since policy definitions are typically encoded in lengthy documents with structures varying widely across platforms (Act, 2024; GitLab, 2025), directly verifying them is challenging. To address this, SHIELDAGENT first extracts individual actionable policies from these documents and further translates them into manageable logical rules for tractable verification.

**Policy Extraction.** Given policy documents, we first query GPT-40 (prompt detailed in Appendix H) to extract individual policy into a structured format that contains the following elements: *term definition*, *application scope*, *policy description*, and *reference* (detailed in Appendix C.2.1). These elements ensure that each policy can be interpreted independently and backtracked for verification during shielding.

LTL Rule Extraction. Since natural language constraints are hard to verify, we further extract logical rules from these formatted policies via GPT-4o (prompt detailed in Appendix H). Specifically, each rule is formulated as  $r = [\mathcal{P}_r, T_r, \phi_r, t_r]$  that involves: (1) a set of predicates  $\mathcal{P}_r \subset \mathcal{P}$  from a finite predicate set  $\mathcal{P} = \{\mathcal{P}_a, \mathcal{P}_s\}$ ; (2) a natural language description of the constraint  $T_r$ ; (3) a formal representation of the rule in LTL; (4) the rule type  $t_r$  (i.e. *action* or *physical*). Please refer to Appendix C.3 for more details.

### 3.2.3. ASPM STRUCTURE OPTIMIZATION

While the procedure in §3.2.2 extracts structured LTL rules from policy documents, they may not fully capture the original constraints or be sufficiently concrete for verification.

Therefore, we propose a bi-stage optimization algorithm to iteratively refine the rules in ASPM by: (1) improving their alignment with the original natural language policies, (2) enhancing verifiability by decomposing complex or vague rules into more atomic and concrete forms, and (3) increasing verification efficiency by merging redundant predicates and rules. As detailed in Algorithm 2 in Appendix C.4, the optimization process alternates between two stages, i.e., *Verifiability Refinement (VR)* and *Redundancy Pruning (RP)*.

**Verifiability Refinement (VR).** In this stage, we refine rules to be: (1) accurate, i.e., adjusting incorrect LTL representations by referencing their original definitions; (2) verifiable, i.e., refining predicates to be *observable* and can be assigned a boolean value to be deterministically used for logical inference; and (3) atomic, i.e., decomposing compound rules into individual rules such that their LTL representations cannot be further simplified. Specifically, we prompt GPT-40 (prompt detailed in Appendix H) by either traversing each rule or prioritizing vague rules under an optimization budget. For example, based on the observation that concrete, useful rules usually have more specialized predicates that distinguish from each other, we devise an offline proxy to estimate the vagueness of rules via  $\mathcal{V}_r = \max\{\mathcal{V}_p^1, \cdots, \mathcal{V}_p^{|\mathcal{P}_r|}\},\$ where  $V_p^i$  quantifies the vagueness for each of its predicates  $p_i$  by averaging its top-k embedding similarity with all other predicates of the same type  $\mathcal{P}_i$  (i.e., either *action* or *state*):

<span id="page-3-2"></span>
$$\mathcal{V}_i = \frac{1}{k} \sum_{i=m}^k S_{\alpha(m)} \text{s.t. } S_\alpha = \text{desc} \left( \left\{ e_i \cdot e_j \mid j \le |\mathcal{P}_i| \right\} \right)$$
 (3)

where  $e_i$  denotes the normalized vector representation of predicate  $p_i$  obtained by a SOTA embedding model (e.g. OpenAI's text-embedding-3-large model (OpenAI, 2024)). Please refer to Appendix C.4 for more details.

**Redundancy Pruning (RP).** Since the previous VR stage operates at the rule level without taking account of the global dynamics, it may introduce repetitive or contradictory rules into ASPM. To address this, RP evaluates ASPM from a global perspective by clustering rules with semantically similar predicates. Then within each cluster, we prompt GPT-40 (see Appendix H) to merge redundant predicates and rules, enhancing both efficiency and clarity in ASPM.

**Iterative Optimization.** By alternating between VR and RP, we progressively refine ASPM, improving rule verifiability, concreteness, and verification efficiency. This process iterates until convergence, i.e., no further rule optimizations are possible, or the budget is reached. Finally, human experts may review the optimized rules and make corrections when necessary, and the resulting ASPM thus effectively encodes all safety specifications from the given policy documents.

### <span id="page-3-1"></span>3.2.4. ASPM Inference & Training

Given that rules in ASPM can be highly interdependent, we equip ASPM with logical reasoning capabilities by organizing it into a set of action-based rule circuits  $\pi_{\theta} := \{\mathcal{C}_{\theta_a}^{p_a} \mid p_a \in \mathcal{P}_a\}$ , where  $\mathcal{C}_{\theta_a}^{p_a}$  represents the rule circuit responsible for verifying action  $p_a$ , where its rules are assigned a soft weight  $\theta_r$  to indicate their relevant importance for guardrail decision-making. Refer to Appendix C.5 for more details.

**Action-based ASPM Clustering.** Observing that certain agent actions exhibit low logical correlation to each other (e.g.  $delete\_data$  and  $buy\_product$ ), we further construct

an action-based probabilistic circuit  $\pi_{\theta}$  (Kisa et al., 2014) from ASPM to boost its verification efficiency while retaining precision. Concretely, we first apply spectral clustering (Von Luxburg, 2007) to the state predicates  $\mathcal{P}_s$ , grouping rules that exhibit strong logical dependencies or high semantic relevance. Then, we associate each action predicate  $p_a$  with its relevant constraints by unifying rule clusters that involve  $p_a$  into a single probabilistic circuit  $\mathcal{C}_{\theta_a}^{p_a}$  (weights  $\theta_a$  are trained in §3.2.4). During verification, the agent only needs to check the corresponding circuit w.r.t. the invoked action, thereby substantially reducing inference complexity while preserving logical dependencies among rules.

**ASPM Inference.** At each step i, SHIELDAGENT first extracts action predicates  $p_a$  from the agent output and retrieves corresponding action rule circuits from  $\mathcal{G}_{\text{ASPM}}$  to verify the invoked action  $a_i$ . Then, SHIELDAGENT generates a shielding plan to assign boolean values  $v_s^i$  to each state predicates  $p_s^i$  in  $\mathcal{C}_{\theta_a}^{p_a}$  by leveraging a diverse set of verification operations and tools (detailed in §3.3).

In each action circuit  $\mathcal{C}^{p_a}_{\theta_a}$ , the joint distribution over all possible assignments of predicates (i.e., world) is modeled via Markov Logic Network (Richardson & Domingos, 2006). Let  $\mu_p$  denote the assignment of predicate p, the probability of the proposed world  $\mu$  with action  $p_a$  invoked is given by:

<span id="page-4-2"></span>
$$P_{\theta}(\mu_{p_a} = 1 | \{\mu_{p_s} = v_s\}) = \frac{1}{Z} \exp \sum_{r \in R_{p_a}} \theta_r \mathbb{I}[\mu \sim r]$$
 (4)

where  $\mathbb{I}[\mu \sim r] = 1$  indicates that the world  $\mu$  follows the logical rule r and Z is a constant partition for normalization. However, since the absolute value of world probability is usually unstable (Gürel et al., 2021), directly thresholding it as the guardrail decision may cause a high false positive rate. Thus inspired by the control barrier certificate (Ames et al., 2019), we propose the following *relative safety condition*:

<span id="page-4-0"></span>
$$l_s(a_i) = 1$$
 iff  $P_{\theta}(\mu_{p_a=1}) - P_{\theta}(\mu_{p_a=0}) \ge \epsilon$  (5)

where  $P_{\theta}(\mu_{p_a}=1)$  is the probability in Eq. (4), rewritten for brevity, and  $P_{\theta}(\mu_{p_a=0})=P_{\theta}(\mu_{p_a}=0|\{\mu_{p_s}=v_s\})$  reverses the value of the invoked action while keeping others unchanged. Specifically, condition Eq. (5) guarantees the safety of the action sequence from a dynamic perspective, allowing executing action  $a_i$  only when the safety likelihood increases or remains within a tolerable region bounded by  $|\epsilon|$  from the current state (i.e. no action taken). Users are allowed to adjust  $\epsilon$  to adapt to different levels of safety requirements (e.g. higher  $\epsilon$  for more critical safety needs).

**ASPM Weight Learning.** Since some rules in ASPM may be inaccurate or vary in importance when constraining different actions, treating them all as *absolute* constraints (i.e., rule weights are simply infinity) can lead to a high false positive rate. To improve ASPM's robustness, we

### Algorithm 1 SHIELDAGENT Inference Procedure

```
Require: Interaction history \mathcal{H}_{\leq i} = \{(o_j, a_j) \mid j \in [1, i - 1]\}
      1]} from the target agent; Current observation o_i; Agent
      output a_i; Safety policy model \mathcal{G}_{ASPM} = (\mathcal{P}, \mathcal{R}, \pi_{\theta});
      Safety threshold \epsilon.
 1: p_a \leftarrow \text{EXTRACT}(a_i)

 2: \mathcal{C}_{\theta_a}^{p_a} = (\mathcal{P}_{p_a}, R_{p_a}, \theta_a) \leftarrow \text{Retrieve}(p_a, \mathcal{G}_{\text{ASPM}})
 3: V_s = \{p_s^i : v_s^i\} \leftarrow \emptyset \triangleright Initialize predicate-value map
 4: for each rule r = [\mathcal{P}_r, T_r, \phi_r, t_r] \in R_{p_a} do
          W_r \leftarrow \text{RetrieveWorkflow}(r, p_a)
          while \exists p_s \in \mathcal{P}_r s.t. \mathcal{V}_s[p_s] is not assigned do
 6:
              A_s \leftarrow \text{PLAN}(\mathcal{W}_r, r, \mathcal{P}_r) \triangleright \text{Generate an action plan}
 7:
              with shielding operations (e.g., SEARCH, CHECK)
              for each step t_s^i in action plan A_s do
 8:
 9:
                  o_s^i \leftarrow \text{EXECUTE}(t_s^i, \mathcal{H}_{\leq i}, o_i) \triangleright \text{Get step result}
                  \mathcal{V}_s[p_s] \leftarrow \text{PARSE}(o_s^i), p_s \in \mathcal{P}_r \quad \triangleright \text{Attempt to}
10:
                  assign a truth value to any unassigned predicates
11:
              end for
          end while
12:
          l_r \leftarrow \text{Verify}(r, \mathcal{V}_s)
13:
                                                    ▶ Run formal verification
14: end for
15: \epsilon_s \leftarrow P_\theta(\mu_{p_a=1}) - P_\theta(\mu_{p_a=0})

      condition via Eq. (4) and Eq. (5)
16: if \epsilon_s \geq \epsilon then
         l_s \leftarrow 1
17:
                                                              \triangleright Action p_a is safe
18: else
19:
          l_s \leftarrow 0
                                                          \triangleright Action p_a is unsafe
20: end if
21: return (l_s, V_s, T_s) \triangleright \text{Return safety label, violated rules,}
      textual explanation
```

optimize rule weights for each circuit  $\theta_a$  over a dataset  $\mathcal{D} = \{\zeta^{(i)}, y^{(i)}\}_{i=1}^N$  via the following guardrail hinge loss:

<span id="page-4-3"></span>
$$\mathcal{L}_g(\theta) = \mathbb{E}_{(\zeta, \mathcal{Y}) \sim \mathcal{D}} \max(0, -y^{(i)}(P_{\theta}(\mu_{p_a=1}^{(i)}) - P_{\theta}(\mu_{p_a=0}^{(i)})))$$
(6)

where labels  $y^{(i)}=1$  if action  $a^{(i)}$  is  $\mathit{safe}$  or  $y^{(i)}=-1$  if  $\mathit{un-safe}$ . Specifically,  $y^{(i)}$  can be derived from either real-world safety-labeled data or simulated pseudo-learning (Kang & Li, 2024). The learned weights act as soft constraints, capturing the relative importance of each rule in guardrail decision-making. We illustrate the training process in Algorithm 3.

# <span id="page-4-1"></span>3.3. SHIELDAGENT Framework

In this section, we detail the verification workflow of SHIELDAGENT for each action rule circuit. Specifically, SHIELDAGENT integrates specialized shielding operations designed for diverse guardrail needs, supported by a rich tool library. To further enhance efficiency, it employs a hybrid memory module that caches *short-term* interaction history and stores *long-term* successful shielding workflows.

**Shielding Pipeline.** As illustrated in the lower part of Fig. 1,

<span id="page-5-0"></span>Table 1: Comparison of SHIELDAGENT-BENCH with existing agent safety benchmarks. SHIELDAGENT-BENCH extends prior work by offering more samples, operation risk categories, and types of adversarial perturbations (both *agent-based* and *environment-based*). In addition, SHIELDAGENT-BENCH provides verified annotations of both risky inputs and output trajectories, explicitly defining each case of safety violations, and annotating relevant policies for verifying each trajectory.

| Benchmark                         | #Sample | #Operation Risk | #Attack Typ | e   #Environment | Risky Trajectory | Risk Explanation | #Rule |
|-----------------------------------|---------|-----------------|-------------|------------------|------------------|------------------|-------|
| ST-Web (Levy et al., 2024)        | 234     | 3               | 0           | 3                |                  | <b> </b>         | 36    |
| AgentHarm (Andriushchenko et al.) | 440     | 1               | 0           | 0                |                  |                  | 0     |
| VWA-Adv (Wu et al., 2025)         | 200     | 1               | 1           | 3                |                  |                  | 0     |
| SHIELDAGENT-BENCH                 | 3110    | 7               | 2           | 6                | <b>√</b>         | <b>√</b>         | 1080  |

at each step i, SHIELDAGENT first extracts action predicates from the agent output and retrieves corresponding rule circuits for verification. Then it formats all the predicates and rules in a query and retrieves similar shielding workflows from the long-term memory. Using them as few-shot examples, it then produces a step-by-step shielding plan supported by a diverse set of operations and tools to assign truth values for the predicates. Once all predicates are assigned, it then generates model-checking code to formally verify each rule. For each violated rule, it provides an in-depth explanation and potential countermeasures. Finally, it performs a probabilistic inference (as detailed in  $\S 3.2.4$ ) to deliver the final guardrail decision (see details in Appendix D).

**Shielding Operations.** SHIELDAGENT includes four inbuilt operations for rule verification: (1) **Search**: Retrieves relevant information from past history  $\mathcal{H}_{\leq i}$  and enumerates queried items as output; (2) **Binary-Check**: Assigns a binary label to the input query; (3) **Detect**: Calls moderation APIs to analyze target content and produce guardrail labels for different risk categories; (4) **Formal Verify**: Run model-checking algorithms to formally verify target rules.

**Tool Library.** To support these operations, SHIELDAGENT is equipped with powerful tools, including moderation APIs for various modalities (e.g., image, video, audio) and formal verification tools (e.g., Stormpy). To enhance guardrail accuracy, we fine-tuned two specialized guardrail models based on InternVL2-2B (Chen et al., 2024b) for enumeration-based search and binary-check operations.

Memory Modules. To optimize efficiency, SHIELDAGENT employs a hybrid memory module comprising: (1) **History as short-term memory**: To copilot with the shielded agent  $\pi_{\rm agent}$  in real time, SHIELDAGENT incrementally stores agent-environment interactions as KV-cache, minimizing redundant computations. Once the current action sequence is verified, the cache is discarded to maintain a clean and manageable memory; (2) **Successful workflows as long-term memory**: Since verifying similar actions often follows recurring patterns, SHIELDAGENT also stores successful verification workflows for diverse action circuits as permanent memory, enabling efficient retrieval and reuse of these effective strategies. This module is also continually updated to incorporate new successful shielding experiences.

<span id="page-5-1"></span>![](_page_5_Picture_7.jpeg)

Figure 2: Pipeline for curating SHIELDAGENT-BENCH. We adopt the AWM web agent (Wang et al., 2024) and collect safe trajectories by executing instructions with full policy compliance. For risky trajectories, we attack the agent with two SOTA *agent-based* and *environment-based* algorithms and produce unsafe trajectories across seven risk categories. Built on the MCP framework (Anthropic, 2024), SHIELDA-

Built on the MCP framework (Anthropic, 2024), SHIELDA-GENT collectively integrates these modules to handle diverse shielding scenarios while allowing users to customize new tools to extend the guardrail capabilities.

### 4. SHIELDAGENT-BENCH Dataset

Existing guardrail benchmarks primarily evaluate the *content* generated by LLMs rather than their *actions* as decision-making *agents*. To bridge this gap, we introduce SHIELDAGENT-BENCH, the first comprehensive benchmark for evaluating guardrails for LLM-based autonomous agents, encompassing safe and risky trajectories across six diverse web environments. As shown in Fig. 2, we curate 960 safety-related web instructions and collect 3110 unsafe trajectories by attacking agents to violate targeted safety policies via two practical perturbations. Furthermore, we categorize the resulting failure patterns into seven common risk categories.

**Safety-related Instructions.** We selectively reuse the instruction templates from WebArena (Zhou et al., 2023) and ST-WebAgentBench (Levy et al., 2024) across six environments (i.e., *Shopping*, *CMS*, *Reddit*, *GitLab*, *Maps*, *SuiteCRM*), and curate instructions that yield potential safety risks by augmenting the templates with safety-critical information (e.g. *API token*). Finally, we obtain 960 high-quality safety-related instructions. Specifically, each sample in our

<span id="page-6-0"></span>Table 2: Agent guardrail performance comparison of SHIELDAGENT with various baselines on SHIELDAGENT-BENCH. For each perturbation source (i.e., *agent-based* and *environment-based*), we report the individual accuracy for each risk category, along with average accuracy (ACC@G) and false positive rate (FPR@G) for the final guardrail label. Additionally, we report the average rule recall rate (ARR@R). Inference cost is measured by the average number of queries (NoQ) to GPT-40 and inference time (seconds per sample). The best performance is in bold.

| Perturbation | 1             |        | Risk Category |        |        |           |       |           |        | Overall |        | C    | 6.3   |  |
|--------------|---------------|--------|---------------|--------|--------|-----------|-------|-----------|--------|---------|--------|------|-------|--|
| Source       | Guardrail     | Access | Content       | Hallu. | Instr. | Operation | Error | Long-term | ACC@G↑ | FPR@G↓  | ARR@R↑ | NoQ↓ | Time↓ |  |
|              | Direct        | 68.2   | 78.6          | 76.3   | 78.0   | 69.2      | 74.3  | 68.8      | 73.3   | 7.6     | 31.5   | 1    | 6.3   |  |
| Agent besed  | Rule Traverse | 83.4   | 85.9          | 74.0   | 85.0   | 87.9      | 70.5  | 87.0      | 82.0   | 18.1    | 69.0   | 27.1 | 75.3  |  |
| Agent-based  | GuardAgent    | 77.0   | 77.6          | 80.3   | 87.7   | 85.3      | 84.7  | 76.9      | 81.4   | 14.3    | 55.9   | 13.6 | 62.3  |  |
|              | SHIELDAGENT   | 92.0   | 89.2          | 85.5   | 93.3   | 93.0      | 88.7  | 91.3      | 90.4   | 5.6     | 87.5   | 9.5  | 31.1  |  |
|              | Direct        | 75.0   | 81.6          | 73.3   | 74.9   | 73.5      | 70.3  | 82.0      | 75.8   | 6.6     | 31.5   | 1    | 6.7   |  |
| Environment- | Rule Traverse | 85.0   | 86.2          | 76.7   | 83.2   | 88.0      | 69.3  | 83.0      | 81.6   | 15.0    | 75.0   | 31.5 | 80.1  |  |
| based        | GuardAgent    | 89.3   | 88.2          | 88.1   | 86.3   | 83.1      | 77.7  | 80.9      | 84.8   | 10.7    | 70.0   | 14.8 | 58.7  |  |
|              | SHIELDAGENT   | 95.1   | 92.7          | 86.7   | 95.2   | 91.0      | 89.3  | 92.0      | 91.7   | 4.0     | 92.7   | 11.2 | 33.8  |  |

dataset consists of  $(I_s, \zeta_s, \zeta_u^a, \zeta_u^e)$ , where  $I_s$  is the instruction,  $\zeta_s$  is the safe trajectory, and  $\zeta_u^a, \zeta_u^e$  are unsafe trajectories induced by two types of attacks, respectively. Each  $\zeta$  includes the complete interactions between the agent and the environment at each step, including: (1) all conversations, (2) visual screenshots, (3) HTML accessibility trees.

Policy-Targeted Agent Attacks. We consider two types of adversarial perturbations against agents, each instanced by a practical attack algorithm: (1) Agent-based: we adopt AgentPoison (Chen et al., 2024c), which injects adversarial demonstrations in the agent's memory or knowledge base to manipulate its decision-making; (2) Environment-based: we adopt AdvWeb (Xu et al., 2024), which stealthily manipulates the environment elements to mislead the agent. Specifically, we adapt both algorithms to attack a SOTA web agent, AWM (Wang et al., 2024) to violate at least one extracted safety policy per instruction, ensuring policy-centered safety violation for tractable guardrail evaluation.

Comprehensive Risk Categories. We carefully investigate the extracted policies, risky trajectories induced by our attack, and concurrent studies on agents' risky behaviors (Levy et al., 2024), and categorize the unsafe trajectories into seven risk categories: (1) access restriction, (2) content restriction, (3) hallucination, (4) instruction adherence, (5) operational restriction, (6) typical error patterns, and (7) long-term risks. Please refer to Appendix F for more details.

**Quality Control.** For each trajectory, human annotators manually review its guardrail label and all violated policies, ensuring a reliable testbed for evaluating agent guardrails.

### 5. Experiment

# 5.1. Setup

**Datasets.** We evaluate SHIELDAGENT against guardrail baselines on our SHIELDAGENT-BENCH dataset and three existing benchmarks: (1) *ST-WebAgentBench* (Levy et al.,

2024), which includes 234 safety-related web agent tasks with simple safety constraints; (2) VWA-Adv (Wu et al., 2025), consisting of 200 realistic adversarial tasks in the VisualWebArena (Koh et al., 2024); and (3) AgentHarm (Andriushchenko et al.), comprising 110 malicious tasks designed for general agents. Notably, to properly evaluate agent guardrails, each sample must include an instruction, agent trajectory, enforced policy, and ground-truth label as protocols—all of which are available in SHIELDAGENT-BENCH. However, existing benchmarks only provide task instructions (see Table 1). To address this, we augment them by collecting corresponding policies and both safe and unsafe trajectories using various algorithms. See Appendix F for details on the curation pipeline and dataset statistics.

**Baselines.** We consider three representative baselines: (1) *Direct prompt*: We provide GPT-40 with the complete policy and directly prompt it to produce an overall safety label and any violated rules. (2) *Rule traverse*: We traverse each rule and prompt GPT-40 to identify potential violation. We flag the trajectory as *unsafe* once a rule is flagged as violated. (3) *GuardAgent* (Xiang et al., 2024): We follow their pipeline and set the *guard request* to identify any policy violations in the agent trajectory. To ensure a fair comparison, we provide all methods with the same safety policy as input and collect the following outputs for evaluation: (i) A binary flag (*safe* or *unsafe*); (ii) A list of violated rules, if any.

Metrics. We evaluate these guardrails using three holistic metrics: (1) Guardrail Accuracy: We report the accuracy (ACC) and false positive rate (FPR) based on the overall safety label, capturing the end-to-end guardrail performance. (2) Rule Recall Rate: For each rule, we compute their average recall rates (ARR) from the list of reported violations, reflecting how well the guardrail grounds its decisions based on the underlying policy. (3) Inference Cost: We report the average number of API queries to closed-source LLMs (e.g., GPT-40) and the inference time (in seconds) per sample for different guardrail methods, capturing both monetary and

<span id="page-7-0"></span>Table 3: Comparison of guardrails across three existing benchmarks. Averaged accuracy (ACC) and false positive rate (FPR) are reported. The best performance is in bold.

<span id="page-7-1"></span>

| Guardrail                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                       | ST-V  | Veb   | VWA   | -Adv  | AgentHarm |       |  |
|-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|-------|-------|-------|-------|-----------|-------|--|
| Guararan                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                        | ACC ↑ | FPR ↓ | ACC ↑ | FPR ↓ | ACC ↑     | FPR ↓ |  |
| Direct                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                          | 74.1  | 4.2   | 90.3  | 4.2   | 76.9      | 4.4   |  |
| GuardAgent                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                      | 84.0  | 6.6   | 89.9  | 4.4   | 78.4      | 4.1   |  |
| SHIELDAGENT                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                     | 91.1  | 4.4   | 94.1  | 3.4   | 86.9      | 3.9   |  |
| 90 —                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                            |       |       |       |       |           |       |  |
| 90 08 00 08 00 08 00 08 00 08 00 08 00 08 00 08 00 08 00 08 00 08 00 08 00 08 00 08 00 08 00 08 00 08 00 08 00 08 00 08 00 08 00 08 00 08 00 08 00 08 00 08 00 08 00 08 00 08 00 08 00 08 00 08 00 08 00 08 00 08 00 08 00 08 00 08 00 08 00 08 00 08 00 08 00 08 00 08 00 08 00 08 00 08 00 08 00 08 00 08 00 08 00 08 00 08 00 08 00 08 00 08 00 08 00 08 00 08 00 08 00 08 00 08 00 08 00 08 00 08 00 08 00 08 00 08 00 08 00 08 00 08 00 08 00 08 00 08 00 08 00 08 00 08 00 08 00 08 00 08 00 08 00 08 00 08 00 08 00 08 00 08 00 08 00 08 00 08 00 08 00 08 00 08 00 08 00 08 00 08 00 08 00 08 00 08 00 08 00 08 00 08 00 08 00 08 00 08 00 08 00 08 00 08 00 08 00 08 00 08 00 08 00 08 00 08 00 08 00 08 00 08 00 08 00 08 00 08 00 08 00 08 00 08 00 08 00 08 00 08 00 08 00 08 00 08 00 08 00 08 00 08 00 08 00 08 00 08 00 08 00 08 00 08 00 08 00 08 00 08 00 08 00 08 00 08 00 08 00 08 00 08 00 08 00 08 00 08 00 08 00 08 00 08 00 08 00 08 00 08 00 08 00 08 00 08 00 08 00 00 |       |       |       |       |           |       |  |
|                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                 |       |       |       |       |           |       |  |

Figure 3: Performance comparison of SHIELDAGENT with *rule traverse* and *GuardAgent* baselines on ST-WebAgentBench. We report the individual guardrail accuracy for each risk category.

Boundary

Execution

computational overhead for real-time applications.

### 5.2. Results

Consent

SHIELDAGENT-BENCH. As shown in Table 2, SHIELDA-GENT achieves SOTA performance, outperforming the best baseline (rule traverse) by an average of 10.2% in terms of accuracy. It also attains the lowest false positive rate at 4.8%and a high rule recall rate of 90.1%, attributed to the robust logical reasoning of ASPM. In terms of efficiency, SHIELD-AGENT reduces API queries by 64.7% and inference time by 58.2% due to its streamlined verification pipeline. (1) Policy Grounding: The high ARR demonstrates SHIELDA-GENT's strong ability to ground decisions in self-extracted constraints, highlighting the effectiveness of our ASPM pipeline in both rule extraction and rigorous verification. (2) Guardrail Robustness: Guardrails generally perform better on environment-based perturbations, as these are externally observable by the guardrail, unlike agent-based which rely on internal agent configurations. Nonetheless, SHIELDA-GENT performs consistently well across both types due to its proactive evidence-grounded verification, making it robust and agnostic to attack modality. (3) Guardrail by Category: SHIELDAGENT leads across most risk categories, particularly in access restriction and instruction adherence, with slightly lower performance on hallucination-related risks that often require external knowledge beyond the policy.

**Existing Datasets.** As shown in Table 3 and Fig. 3, SHIELD-AGENT outperforms the baselines across all three benchmarks by an average of 7.4% in ACC. Specifically: (1) On ST-WebAgentBench, SHIELDAGENT shows notable gains in *User Consent* and *Boundary and Scope Limitation*, high-

<span id="page-7-2"></span>Table 4: Comparison of online guardrail performance of different guardrail methods across six web environments. We report the policy compliance rate (%) conditioned on task success for the tasks from each web environment, along with the average time cost. The best performance is in bold.

|                 | Shopping | CMS  | Reddit | GitLab | Maps | SuiteCRM |
|-----------------|----------|------|--------|--------|------|----------|
| AWM Agent       | 46.8     | 53.2 | 45.9   | 22.8   | 67.9 | 36.0     |
| + Direct        | 50.2     | 56.1 | 48.3   | 26.5   | 70.2 | 38.5     |
| + Rule Traverse | 58.7     | 62.9 | 55.4   | 32.0   | 75.1 | 41.0     |
| + GuardAgent    | 57.9     | 61.5 | 54.8   | 36.1   | 74.3 | 40.6     |
| + SHIELDAGENT   | 65.3     | 68.4 | 60.2   | 50.7   | 80.5 | 55.9     |

lighting its strength in grounding and enforcing target policies; (2) On VWA-Adv, SHIELDAGENT achieves the highest ACC and lowest FPR, demonstrating robust guardrail decisions grounded in logical reasoning. (3) On AgentHarmthat spans a broader range of agent tasks, SHIELDAGENT achieves SOTA performance, showing its generalizability to guardrail across diverse agent types and scenarios.

**Online Guardrail.** We further evaluate SHIELDAGENT's performance in providing online guardrails for web agents. Specifically, we use the AWM agent as the task agent and integrate each guardrail method as a post-verification module that copilots with the agent. These guardrails verify the agent's actions step-by-step and provide interactive feedback to help it adjust behavior for better policy compliance. Notably, this evaluation setting comprehensively captures key dimensions such as guardrail accuracy, fine-grained policy grounding, and explanation clarity, which are all critical components for effectively guiding the task agent's behavior toward better safety compliance. As shown in Table 4, SHIELDAGENT also outperforms all baselines in this online setting, achieving the highest policy compliance rate. These results highlight SHIELDAGENT's effectiveness as System 2 (Li et al., 2025) to seamlessly integrate with task agents to enhance their safety across diverse environments.

### 6. Conclusion

In this work, we propose SHIELDAGENT, the first LLMbased guardrail agent that explicitly enforces safety policy compliance for autonomous agents through logical reasoning. Specifically, SHIELDAGENT leverages a novel actionbased safety policy model (ASPM) and a streamlined verification framework to achieve rigorous and efficient guardrail. To evaluate its effectiveness, we present SHIELDAGENT-BENCH, the first benchmark for agent guardrails, covering seven risk categories across diverse web environments. Empirical results show that SHIELDAGENT outperforms existing methods in guardrail accuracy while significantly reducing resource overhead. As LLM agents are increasingly deployed in high-stakes, real-world scenarios, SHIELDA-GENT marks a critical step toward ensuring their behavior aligns with explicit regulations and policies—paving the way for more capable and trustworthy AI systems.

# Acknowledgment

We thank Meng Ding for the constructive suggestions and help with the paper writing. This work is partially supported by the National Science Foundation under grant No. 1910100, No. 2046726, NSF AI Institute ACTION No. IIS-2229876, DARPA TIAMAT No. 80321, the National Aeronautics and Space Administration (NASA) under grant No. 80NSSC20M0229, ARL Grant W911NF-23-2-0137, Alfred P. Sloan Fellowship, the research grant from eBay, AI Safety Fund, Virtue AI, and Schmidt Science.

# Impact Statement

This paper presents work whose goal is to advance the field of Machine Learning. There are many potential societal consequences of our work, none which we feel must be specifically highlighted here.

# References

- <span id="page-8-3"></span>Act, E. A. I. The eu artificial intelligence act, 2024.
- <span id="page-8-16"></span>Ames, A. D., Coogan, S., Egerstedt, M., Notomista, G., Sreenath, K., and Tabuada, P. Control barrier functions: Theory and applications. In *2019 18th European control conference (ECC)*, pp. 3420–3431. IEEE, 2019.
- <span id="page-8-6"></span>Andriushchenko, M., Souly, A., Dziemian, M., Duenas, D., Lin, M., Wang, J., Hendrycks, D., Zou, A., Kolter, J. Z., Fredrikson, M., et al. Agentharm: Benchmarking robustness of llm agents on harmful tasks. In *The Thirteenth International Conference on Learning Representations*.
- <span id="page-8-0"></span>Anthropic. Introducing the model context protocol, 11 2024. URL [https://www.anthropic.com/](https://www.anthropic.com/news/model-context-protocol) [news/model-context-protocol](https://www.anthropic.com/news/model-context-protocol).
- <span id="page-8-12"></span>Chen, Z., Pinto, F., Pan, M., and Li, B. Safewatch: An efficient safety-policy following video guardrail model with transparent explanations. *arXiv preprint arXiv:2412.06878*, 2024a.
- <span id="page-8-17"></span>Chen, Z., Wang, W., Tian, H., Ye, S., Gao, Z., Cui, E., Tong, W., Hu, K., Luo, J., Ma, Z., et al. How far are we to gpt-4v? closing the gap to commercial multimodal models with open-source suites. *Science China Information Sciences*, 67(12):220101, 2024b.
- <span id="page-8-1"></span>Chen, Z., Xiang, Z., Xiao, C., Song, D., and Li, B. Agentpoison: Red-teaming llm agents via poisoning memory or knowledge bases. In *The Thirty-eighth Annual Conference on Neural Information Processing Systems*, 2024c.
- <span id="page-8-13"></span>Debenedetti, E., Zhang, J., Balunovic, M., Beurer-Kellner, ´ L., Fischer, M., and Tramer, F. Agentdojo: A dynamic en- ` vironment to evaluate attacks and defenses for llm agents. *arXiv preprint arXiv:2406.13352*, 2024.

- <span id="page-8-9"></span>Fu, X., Li, S., Wang, Z., Liu, Y., Gupta, R. K., Berg-Kirkpatrick, T., and Fernandes, E. Imprompter: Tricking llm agents into improper tool use. *arXiv preprint arXiv:2410.14923*, 2024.
- <span id="page-8-4"></span>GitLab. The gitlab handbook, 02 2025. URL [https:](https://handbook.gitlab.com/) [//handbook.gitlab.com/](https://handbook.gitlab.com/).
- <span id="page-8-7"></span>Guo, C., Liu, X., Xie, C., Zhou, A., Zeng, Y., Lin, Z., Song, D., and Li, B. Redcode: Risky code execution and generation benchmark for code agents. In *The Thirty-eight Conference on Neural Information Processing Systems Datasets and Benchmarks Track*.
- <span id="page-8-15"></span>Gurel, N. M., Qi, X., Rimanic, L., Zhang, C., and Li, B. ¨ Knowledge enhanced machine learning pipeline against diverse adversarial attacks. In *International Conference on Machine Learning*, pp. 3976–3987. PMLR, 2021.
- <span id="page-8-11"></span>Helff, L., Friedrich, F., Brack, M., Kersting, K., and Schramowski, P. Llavaguard: Vlm-based safeguards for vision dataset curation and safety assessment. *arXiv preprint arXiv:2406.05113*, 2024.
- <span id="page-8-10"></span>Inan, H., Upasani, K., Chi, J., Rungta, R., Iyer, K., Mao, Y., Tontchev, M., Hu, Q., Fuller, B., Testuggine, D., et al. Llama guard: Llm-based input-output safeguard for human-ai conversations. *arXiv preprint arXiv:2312.06674*, 2023.
- <span id="page-8-8"></span>Jiang, C., Pan, X., Hong, G., Bao, C., and Yang, M. Ragthief: Scalable extraction of private data from retrievalaugmented generation applications with agent-based attacks. *arXiv preprint arXiv:2411.14110*, 2024.
- <span id="page-8-5"></span>Kang, M. and Li, B. r 2 -guard: Robust reasoning enabled llm guardrail via knowledge-enhanced logical reasoning. *arXiv preprint arXiv:2407.05557*, 2024.
- <span id="page-8-14"></span>Kisa, D., Van den Broeck, G., Choi, A., and Darwiche, A. Probabilistic sentential decision diagrams. In *Fourteenth International Conference on the Principles of Knowledge Representation and Reasoning*, 2014.
- <span id="page-8-18"></span>Koh, J. Y., Lo, R., Jang, L., Duvvur, V., Lim, M., Huang, P.-Y., Neubig, G., Zhou, S., Salakhutdinov, R., and Fried, D. Visualwebarena: Evaluating multimodal agents on realistic visual web tasks. In *Proceedings of the 62nd Annual Meeting of the Association for Computational Linguistics (Volume 1: Long Papers)*, pp. 881–905, 2024.
- <span id="page-8-2"></span>Levy, I., Wiesel, B., Marreed, S., Oved, A., Yaeli, A., and Shlomov, S. St-webagentbench: A benchmark for evaluating safety and trustworthiness in web agents. *arXiv preprint arXiv:2410.06703*, 2024.
- <span id="page-8-19"></span>Li, Z.-Z., Zhang, D., Zhang, M.-L., Zhang, J., Liu, Z., Yao, Y., Xu, H., Zheng, J., Wang, P.-J., Chen, X., et al. From

- system 1 to system 2: A survey of reasoning large language models. *arXiv preprint arXiv:2502.17419*, 2025.
- <span id="page-9-12"></span>Liao, Z., Mo, L., Xu, C., Kang, M., Zhang, J., Xiao, C., Tian, Y., Li, B., and Sun, H. Eia: Environmental injection attack on generalist web agents for privacy leakage. *arXiv preprint arXiv:2409.11295*, 2024.
- <span id="page-9-1"></span>Lin, K. Q., Li, L., Gao, D., Yang, Z., Bai, Z., Lei, W., Wang, L., and Shou, M. Z. Showui: One vision-languageaction model for generalist gui agent. In *NeurIPS 2024 Workshop on Open-World Agents*, 2024.
- <span id="page-9-2"></span>Mao, J., Ye, J., Qian, Y., Pavone, M., and Wang, Y. A language agent for autonomous driving. *arXiv preprint arXiv:2311.10813*, 2023.
- <span id="page-9-15"></span>OpenAI. New embedding models and api updates, 01 2024. URL [https://openai.com/index/](https://openai.com/index/new-embedding-models-and-api-updates/) [new-embedding-models-and-api-updates/](https://openai.com/index/new-embedding-models-and-api-updates/).
- <span id="page-9-4"></span>OpenAI. Introducing deep research, 02 2025a. URL [https://openai.com/index/](https://openai.com/index/introducing-deep-research/) [introducing-deep-research/](https://openai.com/index/introducing-deep-research/).
- <span id="page-9-3"></span>OpenAI. Introducing operator, 01 2025b. URL [https://openai.com/index/](https://openai.com/index/introducing-operator/) [introducing-operator/](https://openai.com/index/introducing-operator/).
- <span id="page-9-17"></span>Richardson, M. and Domingos, P. Markov logic networks. *Machine learning*, 62:107–136, 2006.
- <span id="page-9-16"></span>Von Luxburg, U. A tutorial on spectral clustering. *Statistics and computing*, 17:395–416, 2007.
- <span id="page-9-18"></span>Wang, Z. Z., Mao, J., Fried, D., and Neubig, G. Agent workflow memory. *arXiv preprint arXiv:2409.07429*, 2024.
- <span id="page-9-5"></span>Wu, C. H., Shah, R. R., Koh, J. Y., Salakhutdinov, R., Fried, D., and Raghunathan, A. Dissecting adversarial robustness of multimodal lm agents. In *The Thirteenth International Conference on Learning Representations*, 2025.
- <span id="page-9-6"></span>Xiang, Z., Zheng, L., Li, Y., Hong, J., Li, Q., Xie, H., Zhang, J., Xiong, Z., Xie, C., Yang, C., et al. Guardagent: Safeguard llm agents by a guard agent via knowledgeenabled reasoning. *arXiv preprint arXiv:2406.09187*, 2024.
- <span id="page-9-8"></span>Xu, C., Kang, M., Zhang, J., Liao, Z., Mo, L., Yuan, M., Sun, H., and Li, B. Advweb: Controllable black-box attacks on vlm-powered web agents. *arXiv preprint arXiv:2410.17401*, 2024.
- <span id="page-9-7"></span>Zeng, Y., Yang, Y., Zhou, A., Tan, J. Z., Tu, Y., Mai, Y., Klyman, K., Pan, M., Jia, R., Song, D., et al. Air-bench 2024: A safety benchmark based on risk categories from regulations and policies. *arXiv preprint arXiv:2407.17436*, 2024.

- <span id="page-9-11"></span>Zhang, B., Tan, Y., Shen, Y., Salem, A., Backes, M., Zannettou, S., and Zhang, Y. Breaking agents: Compromising autonomous llm agents through malfunction amplification. *arXiv preprint arXiv:2407.20859*, 2024a.
- <span id="page-9-9"></span>Zhang, H., Huang, J., Mei, K., Yao, Y., Wang, Z., Zhan, C., Wang, H., and Zhang, Y. Agent security bench (asb): Formalizing and benchmarking attacks and defenses in llmbased agents. *arXiv preprint arXiv:2410.02644*, 2024b.
- <span id="page-9-10"></span>Zhang, Y., Chen, K., Jiang, X., Sun, Y., Wang, R., and Wang, L. Towards action hijacking of large language model-based agent. *arXiv preprint arXiv:2412.10807*, 2024c.
- <span id="page-9-13"></span>Zhang, Y., Yu, T., and Yang, D. Attacking visionlanguage computer agents via pop-ups. *arXiv preprint arXiv:2411.02391*, 2024d.
- <span id="page-9-0"></span>Zhou, S., Xu, F. F., Zhu, H., Zhou, X., Lo, R., Sridhar, A., Cheng, X., Ou, T., Bisk, Y., Fried, D., et al. Webarena: A realistic web environment for building autonomous agents. *arXiv preprint arXiv:2307.13854*, 2023.
- <span id="page-9-14"></span>Zhu, S., Tabajara, L. M., Li, J., Pu, G., and Vardi, M. Y. Symbolic ltlf synthesis. *arXiv preprint arXiv:1705.08426*, 2017.

# A. Detailed Introduction to SHIELDAGENT

### A.1. Notations

Let X denote the environment, and let πagent be the action policy of an agent we aim to shield. At each step i, the agent receives an observation o<sup>i</sup> ∈ X and maps it to a partial state s<sup>i</sup> = f(oi) via a state-space mapping function f. Specifically for web agents, f extracts accessibility trees (*AX-trees*) from the webpage's HTML and visual screenshots, condensing key information from lengthy observations [\(Zhou et al.,](#page-9-0) [2023\)](#page-9-0). Then, the agent generates an action a<sup>i</sup> by sampling from policy a<sup>i</sup> ∼ πagent(si) and progressively interacts with the environment X .

### <span id="page-10-0"></span>A.2. Solution Space

Given the uniqueness of verifying agent trajectories, we further categorize the predicates into two types: (1) action predicate pa: indicates the action to be executed (e.g. *delete data*); and (2) state predicate ps: describes the environment states involved for specifying the condition that certain actions should be executed (e.g. *is private*). A detailed explanation can be found in Appendix [C.3.](#page-11-1)

Consequently, we characterize the solution space of LLM-based agents with the following two types of rules.

Action rule: an action rule ϕ<sup>a</sup> specifies whether an action p<sup>a</sup> should be executed or not under certain permissive or preventive conditions pc. Note ϕ<sup>a</sup> must involve at least one pa. For example, the deletion action cannot be executed without user consent (i.e., ¬is user authorized → ¬delete data).

Physical rule: a physical rule ϕ<sup>p</sup> specifies the natural constraints of the system, where conditions can logically depend on the others. For example, if a dataset contains private information then it should be classified as *red data* under GitLab's policy (i.e., is private → is red data).

Since predicates can sometimes be inaccurately assigned, ϕ<sup>p</sup> can serve as knowledge in ASPM to enhance the robustness of our shield [\(Kang & Li,](#page-8-5) [2024\)](#page-8-5). With these rules, SHIELDAGENT can effectively reason in the solution space to shield the agent action with high accuracy and robustness.

# B. Additional Results

### B.1. ST-WebAgentBench

Table 5: Comparison of guardrail performance across three risk categories in ST-WebAgentBench [\(Levy et al.,](#page-8-2) [2024\)](#page-8-2). Specifically, we report the averaged accuracy (ACC) and false positive rate (FPR) for each evaluation category, along with overall averages. The best performance is in bold.

| Guardrail     |      | User Consent | Boundary |      |                               | Strict Execution | Overall     |     |  |
|---------------|------|--------------|----------|------|-------------------------------|------------------|-------------|-----|--|
|               |      |              |          |      | ACC ↑ FPR ↓ ACC ↑ FPR ↓ ACC ↑ | FPR ↓            | ACC ↑ FPR ↓ |     |  |
| Direct        | 78.0 | 5.0          | 72.3     | 3.4  | 71.9                          | 4.3              | 74.1        | 4.2 |  |
| Rule Traverse | 84.3 | 10.7         | 85.0     | 11.5 | 80.5                          | 7.0              | 83.3        | 9.7 |  |
| GuardAgent    | 80.1 | 4.5          | 88.9     | 8.7  | 83.0                          | 6.5              | 84.0        | 6.6 |  |
| SHIELDAGENT   | 91.4 | 4.2          | 93.5     | 4.0  | 88.3                          | 5.1              | 91.1        | 4.4 |  |

### B.2. VWA-Adv

Specifically, VWA-Adv [\(Wu et al.,](#page-9-5) [2025\)](#page-9-5) attacks web agents by perturbing either the text instruction by adding a suffix or the image input by adding a bounded noise. Specifically, VWA-Adv constructs 200 diverse risky instructions based on the three environments from VisualWebArena [\(Koh et al.,](#page-8-18) [2024\)](#page-8-18). The environments are detailed as follows:

Classifieds. Classifieds is a similar environment inspired by real-world platforms like Craigslist and Facebook Marketplace, comprising roughly 66K listings and uses OSClass—an open-source content management system—allowing realistic tasks such as posting, searching, commenting, and reviewing.

Shopping. This environment builds on the e-commerce site from WebArena [\(Zhou et al.,](#page-9-0) [2023\)](#page-9-0), where successful navigation requires both textual and visual comprehension of product images, reflecting typical online shopping tasks.

Reddit. Adopting the social forum environment from WebArena, this environment hosts 31K+ posts (including images and memes) across different subreddits. The content variety offers broad coverage of social media interactions and challenges in forum-based tasks.

Table 6: Guardrail performance comparison on VWA-Adv across three environments in VisualWebArena, i.e., *Classifieds*, *Reddit*, *Shopping*, under two perturbation sources, i.e., *text-based* and *image-based*. We report accuracy (ACC) and false positive rate (FPR) for each environment. The best performance is in bold.

| Perturbation | Guardrail   | Classifieds |       | Reddit |       | Shopping |       |       | Overall |  |
|--------------|-------------|-------------|-------|--------|-------|----------|-------|-------|---------|--|
| Source       |             | ACC ↑       | FPR ↓ | ACC ↑  | FPR ↓ | ACC ↑    | FPR ↓ | ACC ↑ | FPR ↓   |  |
|              | Direct      | 87.8        | 4.6   | 91.1   | 3.9   | 90.1     | 5.0   | 89.7  | 4.5     |  |
| Text-based   | GuardAgent  | 90.5        | 6.8   | 87.3   | 2.6   | 91.8     | 5.8   | 89.9  | 5.1     |  |
|              | SHIELDAGENT | 93.2        | 3.4   | 93.4   | 4.9   | 95.1     | 3.2   | 93.9  | 3.8     |  |
|              | Direct      | 93.7        | 3.5   | 91.2   | 4.3   | 87.9     | 3.6   | 90.9  | 3.8     |  |
| Image-based  | GuardAgent  | 92.4        | 3.9   | 87.2   | 2.7   | 90.0     | 4.1   | 89.9  | 3.6     |  |
|              | SHIELDAGENT | 91.0        | 3.4   | 96.6   | 2.7   | 94.9     | 3.0   | 94.2  | 3.0     |  |

### B.3. AgentHarm

Table 7: Guardrail performance comparison on AgentHarm across 11 harm categories. The best performance is in bold.

|             |     |      |      |      | Fraud Cybercrime Self-harm Harassment Sexual Copyright Drugs Disinfo. Hate Violence Terrorism Overall |      |      |      |      |      |      |      |      |
|-------------|-----|------|------|------|-------------------------------------------------------------------------------------------------------|------|------|------|------|------|------|------|------|
| Direct      | ACC | 75.7 | 82.4 | 76.5 | 80.6                                                                                                  | 82.2 | 72.0 | 82.0 | 76.9 | 71.0 | 75.8 | 71.1 | 76.9 |
|             | FPR | 5.2  | 3.6  | 3.6  | 3.8                                                                                                   | 3.8  | 3.9  | 7.0  | 4.1  | 3.5  | 4.4  | 5.1  | 4.4  |
| GuardAgent  | ACC | 82.6 | 66.1 | 75.1 | 75.9                                                                                                  | 82.1 | 69.6 | 76.6 | 80.1 | 77.7 | 92.4 | 83.9 | 78.4 |
|             | FPR | 4.7  | 4.0  | 4.5  | 3.4                                                                                                   | 6.3  | 4.3  | 3.8  | 3.2  | 3.7  | 3.3  | 4.2  | 4.1  |
| SHIELDAGENT | ACC | 89.1 | 92.9 | 82.5 | 92.4                                                                                                  | 94.0 | 89.0 | 80.4 | 81.9 | 81.7 | 83.9 | 88.3 | 86.9 |
|             | FPR | 4.6  | 4.9  | 3.9  | 2.5                                                                                                   | 4.0  | 2.1  | 5.5  | 4.2  | 3.8  | 4.7  | 3.2  | 3.9  |

# C. Action-based Probabilistic Safety Policy Model

### C.1. Automated Policy Extraction

We detail the prompt for automated policy extraction in Appendix [H](#page-28-0) and LTL rule extraction in Appendix [H.](#page-28-1)

### C.2. Safety Policy Model Construction

# <span id="page-11-0"></span>C.2.1. AUTOMATIC POLICY AND RULE EXTRACTION

Specifically, we detail the prompt used for extracting structured policies in Appendix [H\)](#page-28-0). Specifically, each policy contains the following four elements:

- 1. Term definition: clearly defines all the terms used for specifying the policy, such that each policy block can be interpreted independently without any ambiguity.
- 2. Application scope: specifies the conditions (e.g. time period, user group, region) under which the policy applies.
- 3. Policy description: specifies the exact regulatory constraint or guideline (e.g. *allowable* and *non-allowable* actions).
- 4. Reference: lists original document source where the policy is extracted from, such that maintainers can easily trace them back for verifiability.

### <span id="page-11-1"></span>C.3. Linear Temporal Logic (LTL) Rules

Temporal logic represents propositional and first-order logical reasoning with respect to time. *Linear temporal logic over finite traces* (LTL<sup>f</sup> ) [\(Zhu et al.,](#page-9-14) [2017\)](#page-9-14) is a form of temporal logic that deals with finite sequences, i.e., finite-length trajectories.

Syntax. The syntax of an LTL<sup>f</sup> formula φ over a set of propositional variables P is defined as:

$$\varphi ::= p \in P \mid \neg \varphi \mid \varphi_1 \land \varphi_2 \mid \bigcirc \varphi \mid \Box \varphi \mid \varphi_1 \mathcal{U} \varphi_2. \tag{7}$$

Specifically, LTL<sup>f</sup> formulas include all standard propositional connectives: *AND* (∧), *OR* (∨), *XOR* (⊕), *NOT* (¬), *IMPLY* (→), and so on. They also use the following temporal operators (interpreted over finite traces):

- Always (✷φ1): φ<sup>1</sup> is true at every step in the finite trajectory.
- Sometimes (✸φ1): φ<sup>1</sup> is true at least once in the finite trajectory.
- Next (⃝ φ1): φ<sup>1</sup> is true in the next step.
- Until (φ<sup>1</sup> U φ2): φ<sup>1</sup> must hold true at each step until (and including) the step when φ<sup>2</sup> first becomes true. In a finite trace, φ<sup>2</sup> must become true at some future step.

Specifically, φ<sup>1</sup> and φ<sup>2</sup> are themselves LTL<sup>f</sup> formulas. An LTL<sup>f</sup> formula is composed of variables in P and logic operations specified above.

Trajectory. A finite sequence of truth assignments to variables in P is called a *trajectory*. Let Φ denote a set of LTL<sup>f</sup> specifications (i.e., {ϕ | ϕ ∈ Φ}), we have ζ |= Φ to denote that a trajectory ζ satisfies the LTL<sup>f</sup> specification Φ.

### <span id="page-12-0"></span>C.4. ASPM Structure Optimization

We detail the prompt for the verifiability refinement of ASPM in Appendix [H](#page-29-0) and redundancy merging in Appendix [H.](#page-29-0)

We detail the overall procedure of the iterative ASPM structure optimization in Algorithm [2.](#page-13-0)

Table 8: Statistics of ASPM before and after policy model structure optimization across each environment. Specifically, we demonstrate the number of predicates, the number of rules, and the average vagueness score of each rule. The maximum number of iterations is set to 10 across all environments.

| Environment |      | Before Optimization |                                     | After Optimization |     |                                     |  |  |
|-------------|------|---------------------|-------------------------------------|--------------------|-----|-------------------------------------|--|--|
|             |      |                     | # Predicates # Rules Avg. Vagueness |                    |     | # Predicates # Rules Avg. Vagueness |  |  |
| Shopping    | 920  | 562                 | 0.71                                | 461                | 240 | 0.38                                |  |  |
| CMS         | 590  | 326                 | 0.69                                | 225                | 120 | 0.34                                |  |  |
| Reddit      | 1150 | 730                 | 0.77                                | 490                | 178 | 0.49                                |  |  |
| GitLab      | 1079 | 600                 | 0.62                                | 363                | 198 | 0.51                                |  |  |
| Maps        | 430  | 202                 | 0.64                                | 210                | 104 | 0.25                                |  |  |
| SuiteCRM    | 859  | 492                 | 0.66                                | 390                | 240 | 0.32                                |  |  |

### <span id="page-12-1"></span>C.5. Training ASPM

# <span id="page-12-2"></span>D. SHIELDAGENT Framework

# E. SHIELDAGENT-BENCH

# E.1. Risk Categories

We categorize the unsafe trajectories from SHIELDAGENT-BENCH into the following seven risk categories.

(1) Access restriction: Ensuring the agent only interacts with explicitly authorized areas within an application (e.g., enforcing user-specific access control); (2) Content restriction: Verifying that content handling follows predefined policies (e.g., preventing exposure of private or harmful data); (3) Hallucination: the cases where the agent generates or retrieves

### <span id="page-13-0"></span>Algorithm 2 ASPM Structure Optimization

```
Require: Predicate set \mathcal{P} = \{\mathcal{P}_a, \mathcal{P}_s\}; Rule set \mathcal{R} = \{\mathcal{R}_a, \mathcal{R}_p\}; Embedding model \mathcal{E}; Clustering algorithm \mathcal{C}; Refinement
      budget N_b; Max iterations M_{it}; Surrogate LLM; Graph G = (\mathcal{P}, E) with initial edge weights E.
 1: Initialize vagueness score for each predicate V_p, p \in \mathcal{P}
                                                                                                                                          ▷ Calculate via Eq. (3)
 2: V_r = \max\{V_{p_1}, \dots, V_{p_{|\mathcal{P}_r|}}\}, \mathcal{P}_r \subseteq \mathcal{P}

 3: Initialize a max-heap \mathcal{U} \leftarrow \{(\mathcal{V}_r, r) \mid r \in \mathcal{R}\}

 4: n \leftarrow 0
 5: for m=1 to M_{\rm it} do
 6:
         changed \leftarrow false
                                                                                                       > Tracks if any update occurred in this iteration
 7:
         while \mathcal{U} \neq \emptyset \ \land \ n \leq N_{\rm b} do
            (-,r) \leftarrow \operatorname{HeapPop}(\mathcal{U})
                                                                                                                                     ⊳ Pop the most vague rule
 8:
            if LLM_verifiable(r) = false then
 9:
                r_{\text{new}} \leftarrow \text{LLM\_refine}(r, \mathcal{P}_r)
                                                                                   \triangleright Refine rule r to be verifiable; update its predicates if needed
10:
11:
                Update \mathcal{R}: replace r with r_{\text{new}}
12:
                Update \mathcal{P}: if r_{\text{new}} introduces or revises predicates
                Recompute V_p for any changed predicate p in r_{\text{new}}
13:
                Recompute V_{r_{\text{new}}} = \max\{V_p \mid p \in \mathcal{P}_{r_{\text{new}}}\}
14:
                Push (\mathcal{V}_{r_{\mathrm{new}}},\ r_{\mathrm{new}}) into \mathcal{U}
15:
16:
                n \leftarrow n + 1
17:
                changed \leftarrow true
18:
            end if
19:
         end while
         \mathcal{K} \leftarrow \mathcal{C}(G)
                                                                                                          ▶ Cluster predicates in G to prune redundancy
20:
         for each cluster C \in \mathcal{K} do
21:
            p_{\text{merged}} \leftarrow \text{LLM\_merge}(C, \mathcal{R})
22.
                                                                                                    \triangleright Merge similar predicates/rules in C if beneficial
23:
            if p_{\text{merged}} \neq \emptyset then
                Update G: add p_{\text{merged}}, remove predicates in C
24:
25:
                Update \mathcal{R} to replace references of predicates in C with p_{\text{merged}}
                Recompute \mathcal{V}_{p_{\text{merged}}} and any affected \mathcal{V}_r
26:
                Push updated rules into \mathcal{U} by their new \mathcal{V}_r
27:
28:
                changed \leftarrow true
29:
            end if
         end for
30:
         if changed = false then
31:
            break
32:
                                                                                                                           No more refinements or merges
         end if
33:
34: end for
35: return ASPM \mathcal{G}_{ASPM} with optimized structure and randomized weights
```

factually incorrect or misleading outputs in information-seeking tasks; (4) **Instruction adherence**: Assessing the agent's ability to strictly follow user-provided instructions and constraints without deviation; (5) **Operational restriction**: Enforcing explicit policy-based operational constraints, such as requiring user permission before executing sensitive actions; (6) **Typical error pattern**: Identifying common failure patterns like infinite loops or redundant executions; (7) **Long-term risks**: Evaluating actions with delayed consequences, such as repeated failed login attempts leading to account lockout.

# <span id="page-13-1"></span>F. Detailed Experiment Results

# F.1. Dataset Distribution

We detail the distribution of samples in our proposed SHIELDAGENT-BENCH dataset in Fig. 9.

### G. Case Study

![](_page_14_Figure_1.jpeg)

Verifiability Refinement
Redundancy Pruning

800

900

1000

200

1000

1000

1000

1000

1000

1000

1000

1000

1000

1000

1000

1000

1000

1000

1000

1000

1000

1000

1000

1000

1000

1000

1000

1000

1000

1000

1000

1000

1000

1000

1000

1000

1000

1000

1000

1000

1000

1000

1000

1000

1000

1000

1000

1000

1000

1000

1000

1000

1000

1000

1000

1000

1000

1000

1000

1000

1000

1000

1000

1000

1000

1000

1000

1000

1000

1000

1000

1000

1000

1000

1000

1000

1000

1000

1000

1000

1000

1000

1000

1000

1000

1000

1000

1000

1000

1000

1000

1000

1000

1000

1000

1000

1000

1000

1000

1000

1000

1000

1000

1000

1000

1000

1000

1000

1000

1000

1000

1000

1000

1000

1000

1000

1000

1000

1000

1000

1000

1000

1000

1000

1000

1000

1000

1000

1000

1000

1000

1000

1000

1000

1000

1000

1000

1000

1000

1000

1000

1000

1000

1000

1000

1000

1000

1000

1000

1000

1000

1000

1000

1000

1000

1000

1000

1000

1000

1000

1000

1000

1000

1000

1000

1000

1000

1000

1000

1000

1000

1000

1000

1000

1000

1000

1000

1000

1000

1000

1000

1000

1000

1000

1000

1000

1000

1000

1000

1000

1000

1000

1000

1000

1000

1000

1000

1000

1000

1000

1000

1000

1000

1000

1000

1000

1000

1000

1000

1000

1000

1000

1000

1000

1000

1000

1000

1000

1000

1000

1000

1000

1000

1000

1000

1000

1000

1000

1000

1000

1000

1000

1000

1000

1000

1000

1000

1000

1000

1000

1000

1000

1000

1000

1000

1000

1000

1000

1000

1000

1000

1000

1000

1000

1000

1000

1000

1000

1000

1000

1000

1000

1000

1000

1000

1000

1000

1000

1000

1000

1000

1000

1000

1000

1000

1000

1000

1000

1000

1000

1000

1000

1000

1000

1000

1000

1000

1000

1000

1000

1000

1000

1000

1000

1000

1000

1000

1000

1000

1000

1000

1000

1000

1000

1000

1000

1000

1000

1000

1000

1000

1000

1000

1000

1000

1000

1000

1000

1000

1000

1000

1000

1000

1000

1000

1000

1000

1000

1000

1000

1000

1000

1000

1000

Figure 4: The number of rules during each iteration step for GitLab policy. Specifically, the orange bar denotes the number of rules after each *verifiability refinement* step, and the blue bar denotes the number of rules after each *redundancy pruning* step.

Figure 5: The number of predicates during each iteration step for GitLab policy. Specifically, the orange bar denotes the number of predicates after each *verifiability refinement* step, and the blue bar denotes the number of predicates after each *redundancy pruning* step.

![](_page_14_Figure_5.jpeg)

Figure 6: The vagueness score of the rule set during each iteration step for optimizing the GitLab policy. Specifically, we leverage GPT-40 as a judge and prompt it to evaluate the vagueness of each rule within the rule set. A lower vagueness score signifies that the rules are more concrete and therefore more easily verified.

<span id="page-14-0"></span>Table 9: Distribution of samples in our proposed SHIELDAGENT-BENCH dataset. For each environment, we report the number of *safe* and *unsafe* trajectories. Each instruction is paired with one *safe* trajectory (i.e., compliant with all policies) and one *unsafe* trajectory (i.e., violating at least one policy), such that these paired trajectories are always equal in quantity.

| Environment | Unsafe | Safe | Total |
|-------------|--------|------|-------|
| Shopping    | 265    | 265  | 530   |
| CMS         | 260    | 260  | 520   |
| Reddit      | 230    | 230  | 460   |
| GitLab      | 450    | 450  | 900   |
| Maps        | 160    | 160  | 320   |
| SuiteCRM    | 190    | 190  | 380   |

### <span id="page-15-0"></span>Algorithm 3 ASPM TRAINING PIPELINE

```
Require: Rule set \mathcal{R}; state predicates \mathcal{P}_s and action predicates \mathcal{P}_a; similarity threshold \theta; number of clusters k.
 1: A \in \{0,1\}^{|\mathcal{P}_s| \times |\mathcal{P}_s|} \leftarrow \mathbf{0}
                                                                                                                                    ▶ Initialize adjacency matrix
 2: A_{ij} \leftarrow 1 if (p_s^i, p_s^j) co-occur in any rule OR \operatorname{cosSim}(\operatorname{emb}(p_s^i), \operatorname{emb}(p_s^j)) \geq \theta; else 0.

 3: labels \leftarrow SpectralClustering(A, k)
                                                                                                                \triangleright Cluster the state predicates into k groups
 4: for \ell = 1 to k do
         C_p^\ell \leftarrow \{p_s \mid \text{labels}[p_s] = \ell\}
                                                                                                                                    \triangleright Form predicate clusters C_p
 6: end for
 7: for each pair (p_s^i, p_s^j) that co-occur do
         if \operatorname{labels}[p_s^i] \neq \operatorname{labels}[p_s^j] then
 8:
            \mathcal{C}_p^{\ell} \leftarrow \mathcal{C}_p^{\ell} \cup \mathcal{C}_p^m \text{ s.t. } p_s^i \in \mathcal{C}_p^{\ell}, p_s^j \in \mathcal{C}_p^m
                                                                     ▷ If two co-occurring predicates appear in different clusters, merge them
 9:
10:
11: end for
12: for \ell=1 to k' do
         C_r^\ell \leftarrow \{r_s \mid p_s \in C_n^\ell\}
                                                                                     ▶ Group rules which share state predicates in the same cluster
14: end for
15: \mathcal{G}_{ASPM} \leftarrow \emptyset
                                                                                    ▶ Initialize ASPM as an empty dictionary with actions as keys
16: for each p_a \in \mathcal{P}_a do
         for each rule cluster C_r^{\ell} \in \mathcal{C}_r do
17:
             for each rule r \in C_r^{\ell} do
18:
                if p_a^r \in r then
19:
                   \mathcal{G}_{\mathsf{ASPM}}[p_a] = \mathcal{G}_{\mathsf{ASPM}}[p_a] \cup C_r^\ell
20:
                                                                                            ▶ Associate action circuits with any relevant rule clusters
21:
                    break
22:
                end if
23:
             end for
         end for
24:
25: end for
26: for each action circuit C_{\theta_a}^{p_a} do
         for each rule r \in \mathcal{C}_{\theta_a}^{p_a} do
27:
             Initialize rule weight \theta_r randomly
28:
         end for
29:
         for epoch = 1 to max epochs do
30:
             for i = 1 to N do
31:
                Compute P_{\theta}(\mu_{p_a=1}^{(i)}) and P_{\theta}(\mu_{p_a=0}^{(i)}) \triangleright \text{Run probabilistic inference to obtain corresponding safety probabilities}
32:
33:
                Compute loss \mathcal{L}(\theta)
                                                                                              ▷ Calculate loss w.r.t. the groundtruth labels via Eq. (6)
                Update \theta using gradient descent
34:
35:
             end for
36:
         end for
37: end for
38: return Action-based safety policy model \mathcal{G}_{ASPM} with trained weights
```

<span id="page-16-0"></span>![](_page_16_Figure_1.jpeg)

Figure 7: Illustration of an *unsafe* trajectory and its corresponding annotation from a sample in our SHIELDAGENT-BENCH. Each sample contains one *safe* trajectory and two *unsafe* trajectories generated by two distinct attack algorithms. As shown on the left, each trajectory comprises multiple steps of agent-environment interaction, where the environment observation includes both textual information (e.g., *HTML AX-tree* and *terminal stdout*) and the agent's action consists of a CoT reasoning process followed by an executable action. As shown on the right, we carefully annotate each agent action step with a *task success label*, *safety violation label*, and corresponding *risk categories*.

### GitLab – **Access Restriction** • **Policy description**: Users must not access, modify, delete, or disseminate GitLab's or its users' confidential information without authorization. • **Applicable scope**: Applicable to all GitLab and user data handled via GitLab services. • **Term definition**: Confidential Information: Unauthorized access, modification, or dissemination of protected data. • **Policy source**: handbook.LACA.acceptable\_use\_policy • **Predicates**: • *is\_confidential\_data*: • description: The data is classified as confidential information • type: **condition** • *user\_authorized*: • description: The user has authorized to perform actions on the data. • type: **condition** • *delete\_data*: • description: The user deletes the data. • type: **action** • **Rule Logic**: (is\_confidential\_data AND NOT is\_authorized\_user) IMPLIES NOT delete\_data. • **Logic template**: (P1 AND NOT P2) IMPLIES NOT P3 • **Risk type**: access restriction; content restriction **Rule Policy**

Figure 8: An example of the *access restriction* policy and the corresponding extracted rules from GitLab policy handbook.

![](_page_17_Figure_3.jpeg)

Figure 9: An example of the *content restriction* policy and the corresponding extracted rules from GitLab policy handbook.

![](_page_18_Figure_1.jpeg)

Figure 10: An example of the *hallucination* policy and the corresponding extracted rules from GitLab policy handbook.

### *Original Extracted Rule:*

- **Predicates**:
  - *is\_illegal\_content*:
    - description: The content is classified as illegal or harmful.
    - type: **condition**
  - *process\_content*:
    - description: The action to process the content such as publish, download, or create it.
    - type: **action**
- **Rule Logic**: is\_illegal\_content IMPLIES NOT process\_content
- **Logic template**: P1 IMPLIES NOT (P2 OR P3 OR P4)
- **Risk type**: content restriction
- **Policy description**: If content is classified as illegal or harmful, it is strictly prohibited to publish, download, or create such content.
- **Source**: reddit.policies.reddit\_rules.07

### *After Verifiability Refinement:*

- **Predicates**:
  - *is\_illegal\_content*:
    - description: The content is classified as illegal or harmful.
    - type: **condition**
  - *publish\_content*:
    - description: An action to publish the content.
    - type: **action**
- **Rule Logic**: is\_illegal\_content IMPLIES NOT publish\_content
- **Logic template**: P1 IMPLIES NOT P2
- **Risk type**: content restriction
- **Policy description**: If content is classified as illegal or harmful, it is strictly prohibited to publish such content.
- **Source**: reddit.policies.reddit\_rules.07
- **Predicates**:
  - *is\_illegal\_content*:
    - description: The content is classified as illegal or harmful.
    - type: **condition**
  - *download\_content*:
    - description: An action to download the content.
    - type: **action**
- **Rule Logic**: is\_illegal\_content IMPLIES NOT download\_content
- **Logic template**: P1 IMPLIES NOT P2
- **Risk type**: content restriction
- **Policy description**: If content is classified as illegal or harmful, it is strictly prohibited to download such content.
- **Source**: reddit.policies.reddit\_rules.07
- **Predicates**:
  - *is\_illegal\_content*:
    - description: The content is classified as illegal or harmful.
    - type: **condition**
  - *create\_content*:
    - description: An action to create the content.
    - type: **action**
- **Rule Logic**: is\_illegal\_content IMPLIES NOT create\_content
- **Logic template**: P1 IMPLIES NOT P2
- **Risk type**: content restriction
- **Policy description**: If content is classified as illegal or harmful, it is strictly prohibited to create such content.
- **Source**: reddit.policies.reddit\_rules.07

Figure 11: An example of the *verifiability refinement* stage of our safety policy structure optimization algorithm, where a compound rule (*process content*) is decomposed into multiple atomic rules that are more concrete and verifiable (*publish content*, *download content*, *create content*). Specifically, the decomposition process takes into account the broader context of the original rule, including its NLP descriptions and document source, to ensure accuracy and fidelity.

### *Original Extracted Rule:*

- **Predicates**:
  - *comply\_with\_laws*:
    - description: Ensure that instructions comply with data protection laws.
    - type: **condition**
  - *store\_personal\_data*:
    - description: An action to store personal data based on customer instructions.
    - type: **action**
- **Rule Logic**: NOT comply\_with\_laws IMPLIES NOT store\_personal\_data
- **Logic template**: NOT P1 IMPLIES NOT P2
- **Risk type**: [access restriction, content restriction, operational restriction]
- **Policy description**: If customer instructions do not comply with the General Data Protection Regulation (GDPR) [reference], the storage of personal data based on those instructions is prohibited.
- **Source**: gitlab.handbook.content\_security\_policy.03

### *After Verifiability Refinement:*

- **Predicates**:
  - *comply\_with\_GDPR\_laws*:
    - description: Ensure that instructions comply with General Data Protection Regulation (GDPR).
    - type: **condition**
  - *store\_personal\_data*:
    - description: An action to store personal data based on customer instructions.
    - type: **action**
- **Rule Logic**: NOT comply\_with\_laws IMPLIES NOT store\_personal\_data
- **Logic template**: NOT P1 IMPLIES NOT P2
- **Risk type**: [access restriction, content restriction, operational restriction]
- **Policy description**: If customer instructions do not comply with the General Data Protection Regulation (GDPR) [reference], the storage of personal data based on those instructions is prohibited.
- **Source**: gitlab.handbook.content\_security\_policy.03

Figure 12: An example of the *verifiability refinement* stage in our safety policy structure optimization algorithm, where the original extracted rule which contains a vague predicate (*comply with laws*) is refined into a more specific and grounded rule with an updated predicate (*comply with GDPR laws*). With the optimized predicate, the refined rule could explicitly guide the agent to invoke a relevant GDPR checking tool during the guardrail process, enabling a more accurate verification result.

### *Original Extracted Rule:*

- **Predicates**:
  - *user\_consent*:
    - description: Ensure that the user consent is obtained.
    - type: **condition**
  - *publish\_personal\_data*:
    - description: Publish personal data such as someone's home address or intimate media.
    - type: **action**
- **Rule Logic**: NOT user\_consent IMPLIES NOT publish\_personal\_data
- **Logic template**: NOT P1 IMPLIES NOT P2
- **Risk type**: [content restriction, operational restriction]
- **Policy description**: The publication of personal data, including but not limited to home addresses or intimate media, is prohibited unless explicit user consent has been obtained.
- **Source**: reddit.policies.privacy\_policy.17
- **Predicates**:
  - *account\_logged\_in*:
    - description: The user has logged in his/her Reddit account.
    - type: **condition**
  - *disclose\_personal\_data*:
    - description: An action to disclose personal data.
    - type: **action**
- **Rule Logic**: NOT *account\_logged\_in* IMPLIES NOT publish\_personal\_data
- **Logic template**: NOT P1 IMPLIES NOT P2
- **Risk type**: [access restriction, content restriction, operational restriction]
- **Policy description**: If a user is not logged into their Reddit account, the disclosure of personal data is prohibited.
- **Source**: reddit.policies.reddit\_rules.21

### *After Redundancy Pruning:*

- **Predicates**:
  - *user\_consent*:
    - description: Ensure that the user consent is obtained.
    - type: **condition**
  - *publish\_personal\_data*:
    - description: An action to publish personal data such as someone's home address or intimate media.
    - type: **action**
- **Rule Logic**: NOT user\_consent IMPLIES NOT publish\_personal\_data
- **Logic template**: NOT P1 IMPLIES NOT P2
- **Risk type**: [content restriction, operational restriction]
- **Policy description**: The publication of personal data, including but not limited to home addresses or intimate media, is prohibited unless explicit user consent has been obtained.
- **Source**: reddit.policies.privacy\_policy.17
- **Predicates**:
  - *account\_logged\_in*:
    - description: The user has logged in his/her Reddit account.
    - type: **condition**
  - *publish\_personal\_data*:
    - description: An action to publish personal data such as someone's home address or intimate media.
    - type: **action**
- **Rule Logic**: NOT *account\_logged\_in* IMPLIES NOT publish\_personal\_data
- **Logic template**: NOT P1 IMPLIES NOT P2
- **Risk type**: [access restriction, content restriction, operational restriction]
- **Policy description**: The publication of personal data, including but not limited to home addresses or intimate media, is prohibited unless the user has logged in to his/her Reddit account.
- **Source**: reddit.policies.reddit\_rules.21

Figure 13: An example of the *redundancy pruning* stage in our safety policy structure optimization algorithm, where two clustered rules containing predicates with identical contextual implications but different names (*publish personal data* and *disclose personal data*) are merged such that they share a single predicate (*publish personal data*). This pruning operation reduces redundancy in the rule space and improves the efficiency of the verification process.

![](_page_22_Figure_1.jpeg)

Figure 14: An end-to-end example of the guardrail procedure in SHIELDAGENT. Given the task instruction, interaction history, and invoked action as input, (1) SHIELDAGENT first extracts relevant action predicates from the agent's output and matches all higher-level action nodes within the action tree. (2) It then retrieves relevant rule circuits for all identified actions and (3) searches for similar verification workflows from the long-term memory module. Based on this, (4) SHIELDAGENT generates a step-by-step *shielding plan* to assign predicate values by invoking operations from a comprehensive tool library (illustrated in detail in Fig. 15, Fig. 16, and Fig. 17). Once all predicates are assigned, (5) it then generates shielding code (shown in Fig. 18) to formally verify each rule. Finally, (6) it performs probabilistic inference to determine the safety label and (7) reports all violated rules along with corresponding explanations and remediation suggestions (detailed in Fig. 19).

# <span id="page-23-0"></span>**Input**

### *Relevant Rule Circuits*

- **Rule 1**: data\_is\_private AND NOT user\_consent IMPLIES NOT publish\_data
- **Rule 2**: NOT data\_is\_truthful IMPLIES NOT publish\_data
- **Rule 3**: data\_is\_harmful IMPLIES NOT publish\_data
- **Rule 4**: data\_is\_personal IMPLIES data\_is\_private
- **Rule 5**: NOT user\_consent IMPLIES NOT update\_bio
- **Rule 6**: info\_is\_outdated IMPLIES NOT update\_account\_info
- **Rule 7**: NOT exact\_user\_request IMPLIES NOT access\_content
- **Rule 8**: NOT (business\_account\_owner AND content\_truthful) IMPLIES NOT edit\_business\_profile
- **Rule 9**: NOT (user\_consent AND user\_account\_owner IMPLIES NOT delete\_account)

**…**

<think>

# **Shielding Plan** (turn 1)

### ### **Action Circuits Rule Analysis**

*The agent is attempting to update a Reddit bio with "Seeking SDE positions" and add email and phone number, then save these changes. Two target actions "update bio" and "Publish User Information" were identified, which were both L3 levels, and we have retrieved all their associated action circuits including those actions of their parent nodes including "Profile Modification", "Publish Private Data", and "Content Access". Given the retrieved action circuits, I need to first determine which rules are relevant and which predicates need verification.*

### ### **Rule Filtering and Relevance Analysis**

*The agent updates the bio, thus according to the rules, we need to verify if it has strictly followed the user's request to update the corresponding information. Besides, we need to check if the data disclosed during this step is appropriate. Therefore, rules [1, 2, 3, 4, 5, 6, 7] are relevant and require verification.* 

*Since the user uses personal account and not business account, thus rule 8 is not relevant. No account deletion operation is involved in this action, thus rule 9 is also irrelevant.*

### ### **Create Predicate Truth Table**

*Since both rule 1 and rule 5 involve the state predicate user\_consent, however, they refer to different contexts, thus we further specify them to avoid ambiguity:*

- *user\_consent\_for\_publish\_contact\_info (Rule 1): Indicates whether the user has explicitly consented to publishing their personal contact information*
- *user\_consent\_for\_update\_bio (Rule 5): Indicates whether the user has given permission to update their bio information All the other predicates are clear and can be interpreted without ambiguity. I'll also provide context and descriptions for each predicate.*

### </think> <action>

```
verification_tool.create_predicate_map({
     "update_bio": "Action involves updating the bio content",
     "publish_data": "Action involves publishing any data publicly",
     "access_content": "Action involves accessing profile content",
     "update_account_info": "Action involves updating account information",
     "data_is_harmful": "Content contains harmful material",
     "data_is_truthful": "Content is factual and truthful",
     "data_is_personal": "Data is personally identifiable information",
     "data_is_private": "Data is private and sensitive",
     "info_is_outdated": "Current account information is outdated",
     "exact_user_request": "Action precisely matches what the user requested",
     "user_consent_for_publish_contact_info": "User has explicitly consented to publishing their 
     personal contact information",
     "user_consent_for_update_bio": "User has given permission to update their bio information"
})
</action>
```

Figure 15: An example illustrating the shielding plan generation process of SHIELDAGENT. This example focuses on guardrailing the unsafe trajectory from the dataset sample shown in Fig. [7.](#page-16-0) Specifically, given the retrieved action rule circuits corresponding to the extracted actions across different hierarchical levels (matched via a static action tree), SHIELDAGENT first performs relevance analysis to filter out irrelevant rules and resolve ambiguities within the rule predicates. It then invokes tools to construct a *predicate truth table*, listing all predicate names and definitions for assignments.

<span id="page-24-0"></span>**Tool Result Shielding Plan** (turn 3) **Shielding Plan** (turn 2) <think> ### **Assign Direct Predicates** *First, I will assign predicates that can be directly inferred from the context. Specifically, from the extracted actions and their parenting nodes, I can directly determine that the agent is updating a bio, publishing data including personal information, accessing profile content, and updating account information.* </think> <action> **verification\_tool.assign\_predicate\_values**({ "update\_bio": true, "publish\_data": true, "access\_content": true, "update\_account\_info": true }) </action> <think> ### **Predicates Rely on Tool-calling** *Now I'll invoke privacy analysis tools to investigate whether there are personal or private information included, based on the contextual privacy implications of sharing contact details in a public profile. Besides, I'll also invoke text moderation tools to analyze whether the target text contain harmful information. Finally, I'll invoke factual check tools to analyze whether the content is truthful or outdated.* </think> <action> **content\_analysis.privacy\_analysis**({ target\_predicates=["data\_is\_personal", "data\_is\_private"], descriptions=["Data is personally identifiable information", "Data is private and sensitive"] observation=Interaction\_History + [thought\_text, action\_text] }) **content\_analysis.text\_moderate**({ target\_predicates=["data\_is\_harmful"], descriptions=["Content contains harmful material"], observation=Interaction\_History + [thought\_text, action\_text] }) **content\_analysis.factual\_check**({ target\_predicates=["data\_is\_truthful", "info\_is\_outdated"], descriptions=["Content is factual and truthful", "Current account information is outdated"], observation=Interaction\_History + [thought\_text, action\_text], source=["User\_Info\_DB", "Wikipedia", "Google"] }) </action> **content\_moderation.privacy\_analysis.result=**{ "data\_is\_personal": true, "data\_is\_private": true } **content\_moderation.text\_moderate.result=**{ "data\_is\_harmful": false } **content\_moderation.text\_moderate.result=**{ "data\_is\_truthful": true, "info\_is\_outdated": false }

Figure 16: An example (following Fig. [15\)](#page-23-0) illustrating the shielding plan generation process of SHIELDAGENT. In this stage, SHIELDAGENT first assigns predicates that can be directly inferred from the context (e.g., target *action predicates* such as *update bio*). Then for more sophisticated *state predicates* (e.g., *data is harmful*), SHIELDAGENT invokes various verification tools following the MCP protocol to determine and assign their truth values.

### <span id="page-25-0"></span>**Tool Result binary\_check.general\_query.result=**{ "flag": [false, false, true], "explanation": ["The agent does not follow the user's request by adding extra contact information.", "The user has provided consent by authorizing the operation.", "The user does not provide consent as the agent intends to update the bio without asking the user's permission."] } <think> ### **Assign Predicates by Geneal Query** *First, let's update our predicate truth table with the values we've assigned so far. Now we'll use the general query tool to determine values for our remaining unassigned predicates: exact\_user\_request, user\_consent\_for\_publish\_personal\_data, user\_consent\_for\_update\_bio.* </think> <action> **verification\_tool.assign\_predicate\_values**({ "data\_is\_personal": true, "data\_is\_private": true, "data\_is\_harmful": true, "data\_is\_truthful": true, "info\_is\_outdated": false }) **binary\_check.general\_query**({ query=["Does the agent strictly follow user's request?", "Does the user consent to publishing his/her personal data including email and phone number?", "Does the user consent to updating the bio?"], observation=Interaction\_History + [thought\_text, action\_text], binary\_flag=true }) </action> **Shielding Plan** (turn 4) <think> ### **Rule Verification** *Now I'll update the newly assigned predicated from the query results. Now I'll check if all the predicates have been assigned.* </think> <action> **verification\_tool.assign\_predicate\_values**({ "exact\_user\_request": false, "user\_consent\_for\_publish\_contact\_info": false, "user\_consent\_for\_update\_bio": true, }) **verification\_tool.check\_unassigned**() </action> **Shielding Plan** (turn 5) **Tool Result verification\_tool.check\_unassigned.result=**{ "unassigned": false, "unassigned\_list": [] }

Figure 17: An example (following Fig. [16\)](#page-24-0) illustrating the shielding plan generation process of SHIELDAGENT. In this stage, SHIELDAGENT first updates the *predicate truth table* with the newly assigned predicates. Then, it proceeds to verify *state predicates* where no specialized tools are available by leveraging generic query-based verification tools to generate individual queries for each predicate and assign their values based on the responses. Afterward, SHIELDAGENT invokes an additional tool to verify whether all predicates have been successfully assigned or to generate a new plan for any remaining unassigned predicates.

<span id="page-26-0"></span>**Shielding Code**  <think> ### **Rule Verification** *Since all the predicates have been verified, I'll call model checking tools to formally verify each rule. Specifically, I'll first add all the assigned predicates as assumptions and add each rule as hypothesis. Then I'll call prover9 solver and get corresponding results.* </think> <code> ```prover9 % Predicate assignments from the truth table update\_bio = true. publish\_data = true. publish\_personal\_data = true. data\_is\_personal = true. data\_is\_private = true. content\_is\_harmful = false. content\_is\_truthful = true. exact\_user\_request = false. user\_consent\_for\_publish\_personal\_data = false. user\_consent\_for\_update\_bio = true. % Rule 1: data\_is\_private AND NOT user\_consent IMPLIES NOT publish\_data (data\_is\_private & -user\_consent\_for\_publish\_contact\_info -> -publish\_data). % Rule 2: NOT data\_is\_truthful IMPLIES NOT publish\_data (-data\_is\_truthful -> -publish\_data). % Rule 3: data\_is\_harmful IMPLIES NOT publish\_data (data\_is\_harmful -> -publish\_data). % Rule 4: data\_is\_personal IMPLIES data\_is\_private (data\_is\_personal -> data\_is\_private). % Rule 5: user\_consent IMPLIES update\_bio (-user\_consent\_for\_update\_bio -> -update\_bio). % Rule 6: info\_is\_outdated IMPLIES NOT update\_account\_info (info\_is\_outdated -> - update\_account\_info). % Rule 7: NOT exact\_user\_request IMPLIES NOT access\_content (-exact\_user\_request -> -access\_content). end\_of\_list. </code> <action> **verification\_tool.verify\_rule**({ "code": verification\_code "rule\_idx":[1,2,3,4,5,6,7], "explanation": true "feedback": true "verifier": "Prover9/Mace4" }) </action> **Tool Result verification\_tool.verify\_rule.result=**{ "status": [false, true, true, true, true, true, false], "explanation": ["The agent attempts to publish private contact information without user consent.", None, None, None, None, None, "The agent attempts to access content without following the exact user request."] "feedback": ["Delete contact information or obtain user consent before publishing the bio.", None, None, None, None, None, "Delete contact information to strictly follow user request."] }

Figure 18: An example (following Fig. [17\)](#page-25-0) illustrating the shielding code generation process of SHIELDAGENT. Once all predicates in the truth table have been assigned, SHIELDAGENT then generates model checking code for each rule (e.g., based on *prover9*) and transports these codes via corresponding tools to formally verify them. It then collects the verification results along with detailed explanations and remediation feedback for any violated rules.

<span id="page-27-0"></span>![](_page_27_Figure_1.jpeg)

Figure 19: An example (following Fig. [18\)](#page-26-0) illustrating the safety certification process of SHIELDAGENT. After all rules have been verified, SHIELDAGENT performs safety certification to estimate the safety probability of executing the invoked action. It then determines a safety label by comparing this probability against a predefined threshold using a prescribed certification method (e.g., *barrier function*). Finally, SHIELDAGENT reports the safety label along with any violated rules, accompanied by detailed explanations and remediation suggestions.

# <span id="page-28-0"></span>H. Prompt Template

### Prompt Template for Policy Extraction

SYSTEM: You are a helpful policy extraction model to identify actionable policies from organizational safety guidelines. Your task is to exhaust all the potential policies from the provided organization handbook which sets restrictions or guidelines for user or entity behaviors in this organization. You will extract specific elements from the given guidelines to produce structured and actionable outputs.

USER: As a policy extraction model to clean up policies from {organization (e.g. GitLab)}, your tasks are:

- 1. Read and analyze the provided safety policies carefully, section by section.
- 2. Exhaust all actionable policies that are concrete and explicitly constrain behaviors.
- 3. For each policy, extract the following four elements:
  - 1. Definition: Any term definitions, boundaries, or interpretative descriptions for the policy to ensure it can be interpreted without any ambiguity. These definitions should be organized in a list.
  - 2. Scope: Conditions under which this policy is enforceable (e.g. time period, user group).
  - 3. Policy Description: The exact description of the policy detailing the restriction or guideline.
  - 4. Reference: All the referenced sources in the original policy article from which the policy elements were extracted. These sources should be organized piece by piece in a list.

### <span id="page-28-1"></span>Extraction Guidelines:

- Do not summarize, modify, or simplify any part of the original policy. Copy the exact descriptions.
- Ensure each extracted policy is self-contained and can be fully interpreted by looking at its Definition, Scope, and Policy Description.
- If the Definition or Scope is unclear, leave the value as None.
- Avoid grouping multiple policies into one block. Extract policies as individual pieces of statements.

### Provide the output in the following JSON format:

```
```json
[
  {
    "definition": ["Exact term definition or interpretive description."],
    "scope": "Conditions under which the policy is enforceable.",
    "policy_description": "Exact description of the policy.",
    "reference": ["Original source where the elements were extracted."]
  },
    ...
]
```
```

# Output Requirement:

- Each policy must focus on explicitly restricting or guiding behaviors.
- Ensure policies are actionable and clear.
- Do not combine unrelated statements into one policy block.

## Prompt Template for Linear Temporal Rule Extraction

SYSTEM: You are an advanced policy translation model designed to convert organizational policies into structured Linear Temporal Logic (LTL) rules. Your task is to extract verifiable rules from the provided safety guidelines and express them in a machine-interpretable format while maintaining full compliance with logical correctness.

USER: As a policy-to-LTL conversion model, your tasks are:

- 1. Carefully analyze the policy's definition, scope, and policy description.
- 2. Break down the policy into structured rules that precisely capture its constraints and requirements.
- 3. Translate each rule into LTL using atomic predicates derived from the policy.

### Translation Guidelines:

- Use atomic predicates that are directly verifiable from the agent's observations and action history.
- Prefer positive predicates over negative ones (e.g., use store data instead of is data stored).
- If a rule involves multiple predicates, decompose it into smaller, verifiable atomic rules whenever possible.
- Emphasize action-based predicates, ensuring that constrained actions are positioned appropriately within logical expressions (e.g., "only authorized users can access personal data" should be expressed as:

```
(is authorized ∧ has legitimate need) ⇒ access personal data (8)
```

Predicate Formatting: Each predicate must include:

- Predicate Name: Use snake case format.
- Description: A brief, clear explanation of what the predicate represents.
- Keywords: A list of descriptive keywords providing relevant context (e.g., actions, entities, attributes).

### LTL Symbol Definitions:

).

```
• Always: ALWAYS
```

• Eventually: EVENTUALLY

• Next: NEXT • Until: UNTIL • Not: NOT

• And: AND • Or: OR

• Implies: IMPLIES

### Output Format: ```json

```
[
  {
    "predicates": [
      ["predicate_name", "Description of the predicate.", ["kw1", "kw2", ...]]
    ],
    "logic": "LTL rule using predicate names."
  },
  ...
]
```
```

### Output Requirements:

- Ensure each rule is explicitly defined and unambiguous.
- Keep predicates general when applicable (e.g., use create project instead of click create project).
- Avoid combining unrelated rules into a single LTL statement.

## Prompt Template for Verifiability Refinement (VR)

SYSTEM: You are a helpful predicate refinement model tasked with ensuring predicates in the corresponding rules are clean, verifiable, concrete, and accurate enough to represent the safety policies. Your task is to verify each predicate and refine or remove it if necessary.

USER: As a predicate refinement model, your tasks are:

- 1. Check if the provided predicate satisfies the following criteria:
  - Verifiable: It should be directly verifiable from the agent's observation or action history.
  - Concrete: It should be specific and unambiguous.
  - Accurate: It must represent the intended fact or condition precisely.
  - Atomic: It should describe only one fact or action. If it combines multiple facts, break it into smaller predicates.
  - Necessary: The predicate must refer to meaningful information. If it is redundant or assumed by default, remove it.
  - Unambiguous: If the same predicate name is used in different rules but has different meanings, rename it for clarity.
- 2. If refinement is needed, refine the predicate accordingly with one of the following:
  - Rewrite the predicate if it is unclear or inaccurate.
  - Break it down into smaller atomic predicates if it combines multiple facts or conditions.
  - Rename the predicate to reflect its context if it is ambiguous.
  - Remove the predicate if it is redundant or unnecessary for the rule.

### Output Requirements:

- Provide step-by-step reasoning under the section Reasoning.
- Include the label on whether the predicate is good, needs refinement, or redundant.
- If refinement is needed, provide a structured JSON including:
  - Updated predicate with definitions and keywords.
  - Each of the updated rules which are associated with the updated predicate.
  - Definitions of the predicate in each rule's context.

### Output Format:

### Reasoning:

- 1. Step-by-step reasoning for why the predicate is good, needs refinement, or is redundant.
- 2. If yes, then reason about how to refine or remove the redundant predicate.

Decision: Yes/No

If yes, then provide the following:

### Output JSON:

```
{
  "rules": [
    {
      "predicates": [
        ["predicate_name", "Predicate definition.", ["keywords"]]
      ],
      "logic": "logic_expression_involving_predicates"
    }
  ]
}
```

{Few-shot Examples}

## Prompt Template for Redundancy Pruning (RP)

SYSTEM: You are a helpful predicate merging model tasked with analyzing a collection of similar predicates and their associated rules to identify whether there are at least predicates that can be merged or pruned. Your goal is to simplify and unify rule representation while ensuring the meaning and completeness of the rules remain intact after modifying the predicates.

USER: As a predicate merging model, your tasks are:

- 1. Identify predicates in the cluster that can be merged based on the following conditions:
  - Redundant Predicates: If two or more predicates describe the same action or condition but use different names or phrasing, merge them into one.
  - Identical Rule Semantics: If two rules describe the same behavior or restriction but are phrased differently, unify the predicates and merge their logics to represent them with fewer rules.
- 2. Ensure the merged predicates satisfy the following:
  - Consistency: The merged predicate must be meaningful and represent the combined intent of the original predicates.
  - Completeness: The new rules must perfectly preserve the logic and intent of all original rules.

### Output Requirements:

- Provide step-by-step reasoning under the section Reasoning.
- Include a decision label on whether the predicates should be merged.
- If merging is needed, provide a structured JSON including:
  - Updated predicates with definitions and keywords.
  - Updated rules with the new merged predicates.

# Output Format:

## Reasoning:

- 1. Step-by-step reasoning for why the predicates should or should not be merged.
- 2. If merging is needed, explain how the predicates and rules were updated to ensure completeness and consistency.

# Decision: Yes/No

If yes, then provide the following:

# Output JSON:

```
{
  "rules": [
    {
      "predicates": [
        ["predicate_name", "Predicate definition.", ["keywords"]]
      ],
      "logic": "logic_expression_involving_predicates"
    }
  ]
}
```

# Few-shot Examples