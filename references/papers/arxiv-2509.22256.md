<!-- extracted-by: marker -->
# Secure and Efficient Access Control Framework for Computer-Use Agents via Context Space

Haochen Gong, Chenxiao Li, Rui Chang, Wenbo Shen Zhejiang University Hangzhou, Zhejiang, China

# Abstract

Large language model (LLM)-based computer-use agents represent a convergence of AI and OS capabilities, enabling natural language to control system- and application-level functions. However, due to LLMs' inherent uncertainty issues, granting agents control over computers poses significant security risks. When agent actions deviate from user intentions, they can cause irreversible consequences. Existing mitigation approaches, such as user confirmation and LLM-based dynamic action validation, still suffer from limitations in usability, security, and performance. To address these challenges, we propose CSAgent, a system-level, static policybased access control framework for computer-use agents. To bridge the gap between static policy and dynamic context and user intent, CSAgent introduces intent- and context-aware policies, and provides an automated toolchain to assist developers in constructing and refining them. CSAgent enforces these policies through an optimized OS service, ensuring that agent actions can only be executed under specific user intents and contexts. CSAgent supports protecting agents that control computers through diverse interfaces, including API, CLI, and GUI. We implement and evaluate CSAgent, which successfully defends against all attacks in the benchmarks while introducing only 1.99% performance overhead and 5.42% utility decrease.

# 1 Introduction

Recent advances in large language models (LLMs) have paved the way for a new paradigm in human-computer interaction: the computer-use agent (CUA) [\[51\]](#page-15-0). These agents are capable of autonomously controlling personal computing devices via application programming interfaces (APIs) [\[3,](#page-14-0) [15,](#page-14-1) [75\]](#page-16-0), command-line interfaces (CLIs) [\[1,](#page-14-2) [25,](#page-14-3) [43\]](#page-15-1), or graphical user interfaces (GUIs) [\[2,](#page-14-4) [20,](#page-14-5) [41,](#page-15-2) [48,](#page-15-3) [59,](#page-15-4) [62,](#page-15-5) [66\]](#page-16-1), assisting users in daily tasks. Such agents are already being deployed in diverse domains, including PC, smartphones, and in-vehicle systems. By interpreting natural language instructions and orchestrating multi-step workflows across multiple apps, agents significantly enhance user experience and productivity.

However, these agents significantly expand the attack surface, introducing risks primarily stemming from two factors. First, LLMs are inherently vulnerable to attacks like prompt injection and jailbreaks [\[10,](#page-14-6) [18,](#page-14-7) [36,](#page-15-6) [53,](#page-15-7) [54,](#page-15-8) [65,](#page-16-2) [78\]](#page-16-3), and suffer from unpredictability due to hallucinations [\[22,](#page-14-8) [57\]](#page-15-9). Second, agents often possess user-level permissions [\[31,](#page-15-10) [51,](#page-15-0) [56,](#page-15-11) [64,](#page-15-12) [79\]](#page-16-4), violating the principle of least privilege. Consequently, agents may execute unintended, irreversible actions, such as deleting data, transferring funds, or unlocking devices, resulting in severe financial loss or physical harm.

As it is impractical to address these issues through model training alone [\[14,](#page-14-9) [65,](#page-16-2) [68,](#page-16-5) [76\]](#page-16-6), commercial agents usually rely on external safeguards to mitigate risks. For example, many agents [\[2,](#page-14-4) [8,](#page-14-10) [41\]](#page-15-2) require user confirmations before performing actions. However, this approach burdens the user experience, reduces task efficiency, and thus diminishes overall agent usability. This calls for a more seamless protection mechanism. Inspired by operating systems (OSes), an intuitive approach is to enforce policy-based access control to constrain agent behavior. Drawing from the Contextual Integrity (CI) framework [\[40,](#page-15-13) [50,](#page-15-14) [67\]](#page-16-7) and Mandatory Access Control (MAC) principles [\[52,](#page-15-15) [58,](#page-15-16) [69\]](#page-16-8), we can ensure that security-critical actions are performed only when contextual conditions are satisfied. Recent studies have explored this approach [\[4,](#page-14-11) [7,](#page-14-12) [27,](#page-14-13) [55,](#page-15-17) [60,](#page-15-18) [73,](#page-16-9) [77\]](#page-16-10), and some propose dynamic security policy generation, which enhances security while preserving automation. However, these approaches still suffer from fundamental limitations as they rely on LLM-based dynamic policy generation at agent runtime: unreliable LLMs can produce flawed or incomplete rules, and the inference process incurs significant performance and cost overhead.

In this paper, we introduce CSAgent, a secure and efficient static policy-based agent access control framework that addresses these limitations. CSAgent supports CUAs of multiple interaction modalities (GUI, API, and CLI-based) by uniformly abstracting their operations into functions. Following the principle of CI, CSAgent first defines a formal specification for context-aware access control policies that determines the structure and format for security rules. Each policy specifies the contexts (such as user intents and system states) under which a function may be safely executed. We introduce a CSAgent OS service to enforce these policies during agent runtime. Similar to SELinux, system administrators and application developers can author access control policies based on this specification during the development phase. To facilitate this process, we provide an automated policy generation tool that assists developers in creating more complete and systematic policies. By shifting policy construction to the development phase, CSAgent eliminates the runtime overhead of dynamic policy generation while

1

providing a more controllable security framework. To make this practical, we address three key challenges.

First, static policies face difficulties when the security constraints for a function depend on dynamic user intent. For example, file deletion may require path validation for targeted removal but backup verification for cleanup operations. Moreover, users may explicitly specify constraints (e.g., amount limits) in their requests, which also determine how the rules should be defined. Approaches [\[27,](#page-14-13) [55,](#page-15-17) [60\]](#page-15-18) that generate policies at runtime can easily handle such variations, but they require user instructions, which are not observable at development time. To address this, we propose intentaware context space, a per-application hierarchical structure that defines and organizes context- and intent-aware policies ([§4.2\)](#page-4-0). Context space uses function and intent to index policies, improving the expressiveness to cover a wider range of scenarios. Additionally, we propose an intent prediction method that employs LLMs to predict potential user intents during the policy generation phase.

Second, automatically generating policies in a controllable manner for applications across different interaction modalities is challenging. We introduce an LLM-based context analyzer that employs systematic reasoning to generate context spaces for apps ([§4.3\)](#page-5-0). For API and CLI apps, well-defined specifications provide sufficient semantic information for policy generation. However, GUI apps lack these properties. Our insight is that event handlers triggered by GUI interactions define the actual functions and provide precise semantic information. To extract such information, we use LLMs to identify GUI elements and establish associations with their handlers, then employ static analysis to construct call graphs of them, thereby building a semantic knowledge base that enables policy generation. Another problem is that using LLMs for static policy generation still suffers from uncertainty issues (e.g., incorrect or missed generation). Benefiting from the consistency of static policies, we introduce a policy evolution framework that helps developers continuously improve context spaces based on app feature updates or runtime feedback from agents ([§4.5\)](#page-8-0).

Third, extracting user intents at runtime via LLM and managing context spaces for complex apps create performance bottlenecks. During an agent's runtime, the agent establishes a connection with the CSAgent service, the service loads context spaces, and enforces policy validation before function execution. To retrieve policies, we first use an LLM to extract user intents from user requests, which introduces extra overhead. Additionally, context management faces challenges from frequent context updates in complex apps with extensive context spaces and costly loading overhead when switching between multiple context spaces in multi-app scenarios. To address this, we propose an optimized context manager in the service that employs parallel processing and systematic management ([§4.4\)](#page-7-0). When agents receive user requests, they concurrently initiate task-related reasoning

while requesting the service to extract intents, effectively hiding inference latency. Moreover, the manager categorizes contexts by update frequency to minimize unnecessary data gathering and uses a cache to reduce context space loading overhead during app switching.

We implement a CSAgent prototype and conduct extensive evaluation across three benchmarks: AgentBench [\[35\]](#page-15-19), AgentDojo [\[9\]](#page-14-14), and AndroidWorld [\[49\]](#page-15-20), which respectively evaluate CLI-based, API-based, and GUI-based agents. Our experimental results demonstrate that CSAgent achieves a near-perfect defense rate (blocking 100% of attacks with policy evolution) while introducing only 1.99% average additional latency and 5.42% utility decrease, significantly outperforming existing methods. Additionally, our LLM-based context analyzer identifies 1.93× to 4.12× more GUI elements compared to existing approaches during GUI app analysis, providing a substantially richer semantic knowledge base for automated policy generation.

In summary, our key contributions are:

- 1. We analyze the limitations of existing CUA protection methods, identify three new challenges, and propose CSAgent, a system-level, static policy-based access control framework to secure agent behaviors. By introducing the intent-aware context space, we enhance the capability and flexibility of static policies.
- 2. We present the first toolchain that enables automated policy generation across diverse agent interaction modalities. By employing stronger models and our policy evolution framework, CSAgent enables controllable LLM-based policy generation and refinement.
- 3. We implement a CSAgent prototype and integrate it with three agent benchmarks, demonstrating excellent usability and compatibility. We will open-source the CSAgent prototype to facilitate broader adoption.
- 4. We conduct a comprehensive evaluation of CSAgent, showing stronger protection and significantly better performance, which validates the effectiveness and flexibility of our approach.

# 2 Background

LLM-based agents are AI systems that use LLMs as their core reasoning engine to perceive environments, make plans, and take actions to accomplish goals [\[31,](#page-15-10) [72\]](#page-16-11). A key enabler of this paradigm is the function calling capability of LLMs, which allows agents to interface with external systems and perform concrete actions through tools [\[11,](#page-14-15) [12,](#page-14-16) [42,](#page-15-21) [47\]](#page-15-22). A tool typically refers to a semantic abstraction that encapsulates one or more functions. Computer-use agents (CUAs), as shown in Figure [1,](#page-2-0) represent a specialized class of LLM agents designed to control computers like humans. Based on how they interface with computers, CUAs can be categorized into three primary approaches: API-based control, CLI-based control, and GUI-based control.

<span id="page-2-0"></span>![](_page_2_Figure_2.jpeg)

**Figure 1.** Overview of computer-use agent.

API-based control. One category of tools provides access to the APIs of systems or applications on user devices [3, 15, 24, 37]. This enables agents to perform high-level actions like document processing, ticket booking, and route planning. API-based control offers significant advantages in reliability and efficiency. Specifically, well-defined APIs provide clear interfaces with predictable behavior, enabling agents to accomplish complex tasks through systematic tool orchestration and deterministic code execution. However, this approach is limited by the predefined tools—agents can only perform actions supported by available APIs. This constraint requires explicit tool development to support new functionalities, limiting the agent's adaptability to novel user needs and emerging ecosystems.

CLI-based control. Another category of tools leverages command-line interfaces (CLIs) to enable agents to interact with OSes through text commands, providing direct access to system functions and utilities [1, 25, 43]. CLI-based control offers broader functionality compared to API-based approaches, as the extensive ecosystem of CLI tools provides rich functionality without requiring extra API development. However, this flexibility comes with security risks, as command injection vulnerabilities can lead to code execution, privilege escalation, and system compromise [34]. To mitigate these risks, tool providers typically require mechanisms like sandboxing and command filtering [1, 25, 43].

GUI-based control. A third category of tools enables agents to interact with apps via graphical user interfaces (GUIs) [2, 41, 66]. GUI is designed only for human users, requiring agents to perceive the screen and manipulate UI elements as a human would. This typically involves capturing screenshots [20, 48] or extracting a structured GUI tree [59, 66], allowing the agent to understand the current screen, identify actionable elements (such as buttons and input fields), and reason about which actions to take. Finally, the agent performs these actions by calling tools that simulate user interactions, such as clicking or scrolling. GUI-based control offers broad compatibility, allowing agents to interact

with any GUI app. This greatly enhances the agent's adaptability, especially for tasks involving legacy apps that lack API or CLI support. However, this approach still faces several limitations. For example, GUI agents often exhibit low task completion rates due to challenges in GUI comprehension and the complexity of multi-step interactions [49, 74]. Moreover, they also suffer from poor performance since every action requires LLM inference, resulting in substantial latency and degraded user experience [64, 79].

# 3 Motivation and Threat Model

### 3.1 Security-usability Trade-offs in CUAs

While CUAs bring convenience to users, they also expand the attack surface of personal devices and introduce security risks. Specifically, due to the inherent uncertainty of LLMs, as well as their susceptibility to attacks such as prompt injection and jailbreaking, agents may perform unexpected actions that deviate from user intentions [31, 51, 64], as shown in Figure 1. Many of these actions are irreversible and can cause severe consequences that impact the real world, such as data loss, financial damage, or physical harm.

Although some tools attempt to constrain agents' capabilities through filtering mechanisms and sandboxing [1, 25, 43, 45], these approaches cannot fundamentally solve the problem. Such methods typically either permit or deny specific operations unconditionally, lacking the flexibility to account for the specific context. This creates an inherent dilemma: agents must retain the ability to perform actions to maintain their functionality, yet many of these actions are inherently risky. Prohibiting dangerous operations would limit agent capabilities, while unrestricted access poses unacceptable security risks. This tension between security and functionality is a core challenge in agent design.

A straightforward and widely adopted solution is to request user confirmation before each sensitive action [2, 8, 41]. However, this approach introduces considerable usability and performance trade-offs. From a usability perspective, frequent confirmation prompts can disrupt the user experience and lead to fatigue, causing users to approve actions without careful consideration [60]. From a performance standpoint, the confirmation process introduces non-negligible latency, as each task requires multiple rounds of user interaction and LLM inference cycles. This undermines the primary value proposition of autonomous agents: their ability to complete tasks efficiently without constant human oversight.

### 3.2 Rule-based Context Validation for CUAs

Ideally, the execution of a function should be determined based on specific contexts rather than applying unconditional restrictions, aligning with the principles of Contextual Integrity (CI) [40, 50, 67]. Specifically, in our scenario, *context* refers to the collection of information that characterizes the current execution environment, including user intents,

<span id="page-3-0"></span>Table 1. Policy consistency across multiple generations.

|            | Banking | Slack | Travel | Workspace | GMean |
|------------|---------|-------|--------|-----------|-------|
| Mean       | 0.79    | 0.75  | 0.68   | 0.83      | 0.76  |
| Std        | 0.13    | 0.11  | 0.13   | 0.12      | 0.12  |
| Structural | 0.94    | 0.93  | 0.85   | 0.94      | 0.91  |
| Semantic   | 0.64    | 0.56  | 0.52   | 0.71      | 0.60  |

system states, and application-specific parameters. The key insight is that the same action may be safe under certain contextual conditions but dangerous in others. For example, file deletion is safe when the user explicitly specifies the target, but risky without authorization or when targeting critical files. This motivates validation systems that evaluate the appropriateness of agent actions within a given context. Such validation can be performed before (pre-execution) or after (post-execution) each action. While post-execution validation enables more precise anomaly detection by analyzing outcomes, it cannot prevent irreversible harm. Thus, recent studies focus on pre-execution validation. Early work like AirGapAgent [\[4\]](#page-14-11) applied CI principles, using a separate LLM for data access decisions, but lacked explicit policies, limiting explainability and auditability. GuardAgent [\[73\]](#page-16-9) advanced this by introducing code generation to convert safety guard requests into executable code, offering more structured and deterministic validation than direct LLM decisions.

More recent works have developed policy frameworks that support conditional rules [\[21,](#page-14-18) [27,](#page-14-13) [55,](#page-15-17) [60\]](#page-15-18). However, these approaches still face the limitation of requiring LLM inference at agent runtime for policy generation, creating the security and efficiency challenges we aim to address. Additionally, policies dynamically generated at different times or devices are likely to vary, hindering policy consistency and preventing the unified improvement of policies through iterative refinement. As shown in Table [1,](#page-3-0) we analyzed the similarity of policies generated by LLMs multiple times for the same function using apps from AgentDojo [\[9\]](#page-14-14). We calculate the policy similarity from both structural and semantic perspectives. Even with a temperature of 0, the overall similarity is only around 0.76, highlighting the uncertainty in policy generation, especially from the semantic perspective.

# 3.3 Threat Model and Assumptions

We focus on the risks posed by unreliable LLMs within CUAs. Drawing from the OWASP project [\[44\]](#page-15-26), we target the Excessive Agency problem, where agents are granted too much autonomy and perform unintended actions, and Sensitive Information Disclosure, such as inadvertent leakage of private data. These risks can manifest due to various underlying factors, including prompt injection attacks, insecure output handling, and the inherently uncertain nature of current LLMs, such as hallucinations. We assume that the agent

framework and user instructions are benign, but the underlying LLM may produce untrustworthy outputs when processing untrusted inputs from external sources like websites or making security-critical decisions. We assume that the software with which the agent interacts (i.e., the OS and legitimate apps) is trustworthy and functions as intended. We trust the agent's execution framework, tool invocation, and prompt construction operate correctly, and the agent can communicate with our OS service securely. Moreover, context values extracted from these trusted components are also trusted. Our approach does not address attacks targeting LLM training processes or model deployment infrastructure, nor does it cover content safety issues.

# 4 CSAgent Design

# 4.1 Design Goals and Overview

CSAgent is a static policy-based access control framework that secures computer-use agents while preserving their autonomy and efficiency. The system assists developers in creating context-aware security policies guided by CI principles during development. These policies are enforced at runtime through lightweight validation, eliminating risky and costly runtime policy generation and frequent user confirmations. To achieve effective agent protection while maintaining practical deployability, CSAgent targets four design goals:

G1: Security. CSAgent must effectively mitigate risks from unreliable agent behavior while minimizing security risks introduced by our own LLM usage.

G2: Efficiency. CSAgent should introduce minimal overhead to agent execution, preserving task efficiency and user experience. It must avoid frequent runtime LLM calls and maintain responsive behavior.

G3: Automation. CSAgent should achieve high automation in policy construction and evolution while supporting effective human-AI collaboration. The generated policies should be easily reviewable and refinable by developers.

G4: Compatibility. CSAgent must support diverse agent interaction modalities (API, CLI, GUI) and work across different agent models. It should provide a modular design for seamless integration with existing agent systems.

System overview. As shown in Figure [2,](#page-4-1) CSAgent uniformly abstracts API-, CLI-, and GUI-based agent operations as functions to support diverse agent types. This unified abstraction enables consistent policy enforcement and provides a coherent framework for security analysis, policy organization, and management. The CSAgent workflow operates in two distinct phases: the development phase and the runtime phase, where the former serves as a toolchain for assisted policy construction and evolution, and the latter works as a standalone OS security service for agent runtime protection.

During the development phase, developers can manually write policies or utilize our context analyzer ([§4.3\)](#page-5-0) to generate policies automatically. We introduce the intent-aware

<span id="page-4-1"></span>![](_page_4_Figure_2.jpeg)

Figure 2. CSAgent architecture.

context space (§4.2), a per-application hierarchical structure, to organize all contextual policies for an application. This structure also defines CSAgent's policy format, enabling developers to understand, write, and audit policies. When using our analyzer, it generates policies by systematically reasoning through the documentation or code of each function in the app. This static policy approach enables the use of more powerful reasoning models to generate higher-quality policies and iterative refinement to improve them continuously (§4.5), making policy generation more controllable. In contrast, performing such optimizations at runtime would incur significant performance overhead.

During the runtime phase, the agent framework establishes a remote procedure call (RPC) connection with the CSAgent service. When the agent accesses a new application, it registers the corresponding context space with the service, which then loads the context space. Our optimized manager extracts contexts efficiently from user devices and instructions using parallel processing, updating context values based on freshness to minimize unnecessary extractions. Before each function execution, the agent requests policy validation from the service via RPC. A function can only execute when all its dependent contexts satisfy the specified rules in the corresponding policy. If validation fails, the system provides two fallback mechanisms to maintain task efficiency: it can either prompt the user for a decision or offer contextual guidance to the agent, allowing continued execution with security guarantees.

# <span id="page-4-0"></span>4.2 Intent-aware Context Space

CSAgent introduces the concept of *intent-aware context space*, a structured data abstraction used to maintain access control policies for securing agent actions across different user intents and contexts. Each context space is application-specific, accompanying the development and deployment of an application, such as a GUI app or tool. This design follows a principle similar to OSes' per-process address spaces, where each application operates within its own isolated security

domain. By tailoring policies to the specific security characteristics of each application and maintaining clear boundaries between them, this approach provides more granular and systematic management, while avoiding the bloat of a single, large context space. Additionally, the context space defines the policy format for CSAgent, offering a formal specification for developers or LLM-based tools to write policies.

Challenges in static policy. The intent-aware design of the context space aims to address a fundamental challenge in static policy: the same function may require different security policies depending on the user's intent, as the examples in Figure 3. Unlike dynamic policy generation approaches that can adapt to specific user instructions at runtime, static policies must anticipate and accommodate these intent variations during development. Our intent-aware structure addresses this limitation by organizing policies according to predicted user intents, enabling static policies to achieve flexibility comparable to dynamic approaches.

**Our solution.** A context space organizes policies in a hierarchical structure with the indexing pattern: (class)  $\rightarrow$  function  $\rightarrow$  intent  $\rightarrow$  policy, where the class level is optional and used only for large-scale apps with well-defined classes, such as GUI apps with distinct UI widget classes. To precisely characterize this structure, we formally define the context space and its constituent elements as follows. A context space CS for application A is defined as:

$$CS_A = \begin{cases} \{C_1, C_2, \dots, C_n\} & \text{if } |Classes_A| > 0\\ \{F_1, F_2, \dots, F_m\} & \text{if } |Classes_A| = 0 \end{cases}$$
 (1)

where each  $C_i$  represents a class containing multiple functions, and each  $F_j$  represents a function that agents can execute within the app, such as performing a control or changing a setting. For API/CLI agents, a function corresponds to a tool function or CLI command. For GUI agents, it corresponds to an interaction with a GUI element. A function entry F describes such a function and is defined as a tuple:

$$F = \langle desc, sec\_level, I, P \rangle \tag{2}$$

where desc is the natural language description of the function's purpose and behavior, providing human-readable documentation for policy developers and maintainers. sec  $level \in$ {normal, conditional, dangerous} categorizes functions based on their risk potential: normal functions are completely harmless (e.g., reading system time); conditional functions are safe under specific conditions but may cause harm if executed inappropriately (e.g., sending an email); dangerous functions require special handling like mandatory user confirmation (e.g., resetting the system).  $I = \{i_1, \dots, i_k, fallback\}$ is the set of possible user intents, where each intent captures the underlying motivation behind user requests rather than surface-level commands, and fallback serves as a default when no specific intent matches. Intents also serve as *implicit* constraints: functions can only be executed when the user's request corresponds to a defined intent.  $P: I \rightarrow Policy$  maps

#### <span id="page-5-1"></span>Function: send email

#### Possible User Intents

- compose send: compose and send a new email
- send draft; send a previously composed draft auto reply: automatically reply to an incoming email

#### Intent-Specific Policy: compose\_send

- · Recipients must be explicitly provided Email content must be finalized

#### Intent-Specific Policy: send\_draft

- Recipients must be explicitly provided
- · A valid draft must be selected

#### Intent-Specific Policy: auto\_reply

- Original email must warrant an automatic reply (e.g. not in the spam list)
- Auto-generated content must not contain sensitive information
- Should align with expected response times
  - (a) Example: send an email

#### Function: delete file

#### Possible User Intents:

- cleanup temp; clean up temporary or cache files remove specific: delete a specific file they explicitly
- batch\_organize: organize files by removing duplicates or outdated versions

#### Intent-Specific Policy: cleanup\_temp

- File must be in designated temporary directories
- File must be sufficiently old

### Intent-Specific Policy: remove\_specific

- File must be explicitly mentioned in user request
- File is not system-critical

#### Intent-Specific Policy: batch\_organize

- Files must be verified duplicates or outdated
- Recent backup must exist before mass operations
  - (b) Example: delete a file

#### Function: control door lock

#### Possible User Intents

- remote\_unlock: unlock door remotely
- auto lock/unlock: automatic unlock based on arrival or departure
- scheduled\_access: sets up time-based access for regular visitors

### Intent-Specific Policy: remote\_unlock

· User identity must be verified

#### Intent-Specific Policy: auto\_lock/unlock

- User must be moving toward/away from the door
- All security systems must be operational

### Intent-Specific Policy: scheduled\_access

- Scheduled access must be time-bounded
- Access must match pre-defined schedule
- Expected visitor must be detected at the door
  - (c) Example: control door lock

Figure 3. Examples of intent-aware policies showing context constraints for the same function under different user intents.

intents to the related policies, enabling fine-grained access control based on user purpose. A context policy  $policy_i$  for intent *i* is defined as:

$$policy_i = \{rule_1, rule_2, \dots, rule_n\},$$
(3)

where each rule; corresponds to a specific context and specifies the constraint that this context must satisfy for safe function execution under the given intent. Specifically, a context rule *rule* is defined as a tuple:

$$rule = \langle ctx\_id, constraint, quidance \rangle \tag{4}$$

where *ctx* id is the unique identifier of the context. *constraint* is a logical expression that must evaluate to true against the corresponding context value for safe execution. Constraints are constructed using atomic predicates combined with logical connectives (e.g.,  $\land$ ,  $\lor$ ,  $\neg$ ). An atomic predicate typically takes the form val1 operator val2, where val1 refers to the current context value, and val2 represents a reference target. Crucially, val2 supports flexible assignment: it can be a pre-defined constant, a user-specified configuration, or a dynamic value derived from another context, ensuring that security policies adapt to individual usage patterns. The operator includes relational symbols (e.g., =, <,  $\neq$ ) and set operations (e.g.,  $\in$ ,  $\subset$ ). This flexible definition allows policies to express complex logic, such as ensuring a user role belongs to a permitted set ( $role \in \{admin, owner\}$ ) or validating value ranges (10 < amount < 500). quidance provides human-readable hints when constraint validation fails, helping users understand why the function was blocked. To centrally manage all contexts within a context space and facilitate policy validation at runtime, we introduce the concept of context vector. The vector serves as a unified data structure that maintains the current runtime values of all relevant contexts defined in the policies. At runtime, the

current state is represented by a context vector CV:

$$CV = \{ctx_1, ctx_2, \dots, ctx_n\}$$
 (5)

where  $ctx = \langle ctx\_id, val, metadata \rangle$  stores the information of a context. ctx id is the context's identifier, and val is the current context value. For context acquisition and management, each context is associated with metadata that specifies: type - the data type of the context value (e.g., string, boolean, integer, float).  $src \in \{user\_request, system\_api, \}$ system\_cli, func\_params, agent\_history} - where the context value can be acquired at runtime. tempr - the update frequency of the context value (see §4.4 for details).

For a function F performed under intent i, the security validation succeeds if and only if all context rules in the corresponding policy are satisfied:

$$\forall rule \in P(i) : validate(rule.constraint, CV) = true$$
 (6)

where *validate*(*rule.constraint*, *CV*) returns true if the constraint condition is satisfied by the corresponding context value in the current context vector CV. This validation logic enforces a default-deny security model: any sensitive function execution is blocked unless explicitly authorized by a matching policy and satisfied context constraints. While the policy enforces the conjunction (AND) of rules, disjunctive scenarios (OR) are supported through flexible constraints or distinct user intents for mutually exclusive contexts. This design flattens complex branching into linear paths, ensuring security (via default-deny) without sacrificing expressiveness.

### <span id="page-5-0"></span>4.3 LLM-based Context Analyzer

To assist developers in constructing intent-aware context spaces for diverse applications, we introduce an LLM-based context analyzer that leverages the semantic comprehension capabilities of LLMs to generate security policies. Concretely, as shown in Figure 4 (blue arrows), our approach utilizes incontext learning by providing the LLM with carefully crafted prompts that include method descriptions, exemplary policies, and explicit data structure definitions for context spaces. Through a structured reasoning process, the analyzer guides the LLM to generate context spaces progressively in multiple stages. First, it analyzes each function's purpose and assesses its security risk level. For functions classified as conditional, the analyzer generates corresponding policies through a two-step process: it begins with intent prediction based on function semantics to identify possible user intents that may trigger the function or affect how this function works (e.g., intents on parameters), followed by policy analysis for each intent. During policy analysis, the system identifies dependent contexts, specifies constraints for each, and generates the necessary context metadata. Upon completion, the context space is stored in a file, which can then be deployed with the application to the device and used by CSAgent for runtime policy enforcement.

**Challenges in GUI analysis.** For API- and CLI-based apps, policy generation is straightforward due to the availability of well-defined function specifications. Specifically, API tools usually provide detailed documentation on purpose, parameters, and behavior [26, 47], while CLIs usually offer manuals specifying command functionality and usage [23, 38], which enables LLMs to generate high-quality context spaces with sufficient semantic information on function behavior. However, GUI agents present greater challenges. Concretely, GUI agents interact with apps through generic interaction primitives (such as screen capture, clicking, scrolling, and text input) rather than explicit functional interfaces. Even worse, GUI apps typically lack functional documentation. While human users understand app usage through interaction, this knowledge is rarely formalized in machine-readable specifications, making it difficult to identify the security-sensitive functions that require protection. As a result, no existing agent protection approach has demonstrated automated endto-end policy generation for GUI apps. Existing approaches for GUI functionality discovery include static program analysis and GUI exploration tools. However, our experiments (§7.2) reveal limitations in both approaches: static analysis often fails to capture the complete scope of GUI functionalities due to dynamic binding and complex UI frameworks, while GUI exploration tools suffer from scalability issues and frequently encounter infinite loops or state explosion problems that prevent comprehensive coverage.

Our solution. To address the challenge, we propose a hybrid approach that combines LLM-based code comprehension with static analysis. Our key insight is that in the absence of explicit documentation, source code represents the most authoritative and comprehensive description of app functionality. GUI apps typically follow an event-driven programming paradigm where all user-facing functionalities are implemented

<span id="page-6-0"></span>![](_page_6_Figure_5.jpeg)

Figure 4. Policy generation and evolution.

through GUI event handlers. These handlers precisely represent the functions that agents can trigger through GUI interactions. Therefore, our approach centers on identifying GUI event handlers within an app and constructing their call graphs to build a granular and thorough knowledge base of app functionality for subsequent policy generation.

The first challenge lies in systematically identifying GUI event handlers, as they may not follow standardized naming conventions across different apps. For instance, while Android apps may use standard callbacks like onClick, developers sometimes implement custom handler methods with varied naming schemes that are subsequently assigned to these callbacks. To address this variability, we leverage the semantic understanding capabilities of LLMs to identify GUI-related code segments. We prompt the LLM to analyze source code files and identify GUI event handlers and extract their code, regardless of their specific naming patterns or implementation approaches. Additionally, the LLM extracts the corresponding GUI element identifiers (such as Android view classes and resource IDs) associated with each handler. These identifiers enable our runtime validation system to map agent GUI actions, which typically involve coordinatebased clicks rather than direct function calls, to the specific functions and their security policies (§5).

Once event handlers are identified, we employ static analysis techniques to construct call graphs for them, mapping the complete execution flow triggered by user interactions. This process is well-supported for source code analysis, where mature tools can accurately trace function invocations and data dependencies to provide comprehensive coverage of handler functionality. The combination of identified handlers and their call graphs provides a source-code-level knowledge base that captures the complete functional semantics of the application. This knowledge base can then be processed by our context analyzer using the same reasoning approach applied to API and CLI tools, enabling the generation of high-quality context spaces for GUI apps.

<span id="page-7-1"></span>![](_page_7_Figure_1.jpeg)

**Figure 5.** Optimized context manager that employs parallel processing and systematic context management.

### <span id="page-7-0"></span>4.4 Optimized Context Manager

The *context manager* serves as the core component of the CSAgent service, responsible for managing context spaces, maintaining context vectors, and enforcing security policies. When an agent first interacts with an app, the context manager loads the app's context space file, and establishes the corresponding context vector. The manager then continuously updates context values in the vector based on their metadata specifications, extracting data from user instructions, device systems, and agent frameworks. When the agent determines the function to execute, the embedded policy verifier retrieves the corresponding policy from the context space and validates it against the current context values in the vector. CSAgent leverages LLMs to extract user intents and related contexts from user instructions. Specifically, we need to identify two types of user intent information: function intent that is used for policy retrieval, and parameter contexts that provide specific context values required by rules (e.g., recipient for message sending).

**Challenges in performance.** The context manager faces two primary performance challenges. First, LLM-based context extraction from user instructions introduces additional inference latency. One simple approach is to request the LLM to analyze the relevant intent and extract context values after the agent determines the function to perform, which would introduce inference latency for every agent action, severely degrading performance [27, 55]. Second, context management for complex apps creates substantial computational overhead. Large-scale apps, particularly GUI apps, often have extensive context spaces involving numerous contexts. Frequent acquisition and updates of all context values incur unnecessary computational costs, increased resource consumption, and additional energy drain. Moreover, loading these context spaces is time-consuming, especially when switching between multiple apps, resulting in a poor user experience.

**Our solution.** Figure 5 shows how we address these challenges by adopting thorough optimizations through parallel processing and systematic context management. To mitigate LLM inference overhead, we employ a concurrent approach for extracting user intents and related contexts from user instructions. When users send requests, the instruction is simultaneously dispatched to both the agent and a dedicated LLM-based *intent extractor* in the CSAgent service. To improve accuracy and efficiency, we employ a coarse-to-fine retrieval strategy before invoking the LLM. Specifically, the manager first uses cosine similarity to efficiently filter relevant intent candidates from the context space based on the user instruction. These filtered candidates, along with parameter contexts, are then passed to the extractor. The extractor analyzes the user instruction to identify the valid intent and extract contexts that correspond to the current request. For function intents, we also prompt the LLM to infer reasonable execution sequences to prevent out-of-sequence errors. To address potential ambiguities where the LLM identifies multiple intents for a single function, we select the intent with the highest similarity score to ensure precise policy retrieval. When the agent determines the next function, we use this finalized intent to retrieve the policy.

To address the computational overhead from extensive context updates, we categorize contexts into three temperature levels based on their update frequency: cold, warm, and hot. *Cold* contexts represent the least frequently updated data, like system settings that remain stable over long periods, which are updated only during context space loading or switching. *Warm* contexts represent moderately updated data, such as user instruction-related contexts, which are updated when users send new instructions. *Hot* contexts represent frequently changing data, such as sensor information, precise timestamps, agent action history, and function parameters that the agent determined, which are updated before each policy validation. These temperature classifications are automatically determined by the context analyzer during the development phase based on each context's attributes.

To support multi-application scenarios and reduce frequent context space loading overhead during application switching, CSAgent's context manager introduces a caching mechanism that stores recently used context spaces. Whenever a new context space is loaded, it is inserted into the cache. When the cache reaches its capacity, the system employs a Least Recently Used (LRU) replacement policy to manage space allocation efficiently. For any given agent, only one context space remains active at a time, as the agent can interact with only one application at once. Other context spaces are suspended and awaiting activation. When the application switches, the active context space is updated accordingly. If the target context space is already present in the cache, no loading overhead is incurred.

# <span id="page-8-0"></span>4.5 Policy Evolution Framework

Challenges in policy reliability. We acknowledge that LLMs' uncertainty makes it difficult to guarantee policy correctness and completeness. CSAgent relies on LLMs to generate context space (intents, contexts and policies), analyze GUI event handlers, and select intent during policy retrieval. Inaccuracies and omissions in their content can compromise access control effectiveness. Since writing completely correct and comprehensive policies is impractical (akin to bug-free software), the only viable mitigation is continuous policy refinement. Manual policy review is labor-intensive, requiring domain experts with deep knowledge of both app features and security.

Our solution. We treat policy engineering as analogous to software engineering: initial LLM-generated policies are "beta code" that must undergo rigorous testing and iterative refinement. Static policy offers a key advantage of consistency across deployments: all users operate under identical policies, enabling centralized quality assurance. Building on this, we propose the Policy Evolution Framework (PEF), a comprehensive toolchain that ensures policy reliability through generation-time validation, app update synchronization, and runtime feedback-based evolution, as shown in Figure [4](#page-6-0) (orange arrows). When a new context space is generated, PEF performs initial validation: it verifies the format correctness, then checks function coverage for API/CLI apps or validates the existence and consistency of UI element classes, identifiers, and event handlers. When an app undergoes feature changes, developers provide update information (e.g., patches or changelogs) to PEF, which automatically updates the context space. For new functions, PEF uses the context analyzer to generate fresh policies. For modified or removed functions, PEF locates the corresponding policies and either regenerates or removes them accordingly.

For runtime feedback analysis, the CSAgent service logs the full execution trace: user request, extracted intent, context evaluation process, and validation result. Policy anomalies are identified through two mechanisms. During policy retrieval, the service logs cases where target functions or intents cannot be located, capturing user instructions and missing elements. During policy validation, when validation fails, the system requests user confirmation before blocking; if users indicate the function should proceed, this suggests potential policy deficiencies. Conversely, when validation succeeds but users believe the function should be blocked, they can actively report anomalies. The CSAgent service filters anomalous logs during idle periods and uploads them to PEF for analysis. PEF then identifies the root cause by prompting the LLM with the runtime error log, the target function's specification or code, and the failed policy, subsequently generating improvement suggestions for developers, who can directly adopt these suggestions or manually intervene as needed. This approach mirrors existing OS crash

reporting mechanisms, with similar user privacy controls allowing opt-out from logging and data collection. To complement offline refinement, we support online parameter adaptation for user-customizable values. These parameters (e.g., threshold or recipient whitelists) are initialized with strict defaults (e.g., empty sets) to ensure safety. When a legitimate action is blocked due to these conservative constraints, the system prompts the user for verification. Upon approval, the specific context value is dynamically incorporated into the trusted set, relaxing the policy for future execution.

Scalable policy testing foundation. PEF's design also provides infrastructure for large-scale policy validation. For instance, we can use LLMs to generate diverse task scenarios and agent action sequences to fuzz context spaces and detect anomalies, analyzing policy completeness and accuracy for further refinement. Systematic policy testing is an important direction for our future work.

# <span id="page-8-1"></span>5 Implementation

We implement CSAgent in Python as a two-component system: a toolchain for context space generation and evolution, and an OS service for agent runtime protection. The toolchain includes the context analyzer and policy evolution framework, while the service consists of the context manager and policy verification logic, offering a lightweight interface that integrates easily with existing agent frameworks with minimal modification. Context spaces are stored in JSON format for ease of review and evolution.

Automatic policy generation and evolution. As outlined in [§4.3,](#page-5-0) we use LLMs (DeepSeek-R1 [\[19\]](#page-14-21)) for policy generation and refinement. For API and CLI agents, the LLM analyzes function documentation to generate policies. For GUI agents, we target Android apps since Android is widely used and open-source. For a given app's source code, our context analyzer first uses text matching to identify files related to GUI operations, then provides these files to the LLM for analysis of event handlers. The LLM outputs results in JSON format, including GUI element details like class and resource ID, and methods invoked by the corresponding handlers. We then use static analysis tools (CodeQL [\[13\]](#page-14-22)) to construct call graphs. For policy evolution, we implement a runtime logging system that captures task information, validation events, user feedback, and execution traces. During refinement, the LLM analyzes the logs alongside the existing context space and update history to identify potential utility and security issues, then systematically updates policies to address these deficiencies.

Policy retrieval. Upon receiving a request, we first retrieve a set of relevant (Function,Intent) candidates from the context space using cosine similarity. Next, we feed the request, these candidates, and policy-defined contexts to the intent extractor LLM, which then identifies the valid intent and extracts specific context values, returning them in a list.

<span id="page-9-0"></span>Table 2. Notation for Formal Security Analysis

| Symbol                   | Definition                                          |
|--------------------------|-----------------------------------------------------|
| $\mathcal{F}$            | Set of all functions that agents can execute        |
| C                        | Set of all possible contexts                        |
| $\mathcal{U}$            | Set of all possible user instructions               |
| 3                        | Set of environmental states that agents have access |
|                          | (e.g., system status, sensor data, external data)   |
| $\mathcal{F}_{norm}$     | Functions that are always safe to execute           |
| $\mathcal{F}_{cond}$     | Functions that are safe under specific contexts     |
| $\mathcal{F}_{dngrs}$    | Functions that require explicit user authorization  |
| $\mathring{\mathcal{A}}$ | Agent behavior model                                |
| $\mathcal{A}_{ideal}$    | Intended agent behavior                             |
| $\mathcal{A}_{error}$    | Erroneous agent behavior due to LLM defects         |
| $\mathcal{A}_{unrel}$    | Combination of ideal and erroneous behaviors        |
| $P_f(i)$                 | Policy for function <i>f</i> under intent <i>i</i>  |
| rule                     | A context rule within a policy                      |

Subsequently, before each agent action, the CSAgent service retrieves the corresponding policy via function and intent indexing. For API/CLI agents, the mapping is direct, with each tool call or CLI command corresponding to a function entry. GUI agents present a more complex scenario, as their actions consist of GUI controls rather than function calls. To address this, CSAgent captures the screen's GUI tree and uses the agent's target coordinates to identify the intended GUI element, extracting its package, class, and resource ID attributes to map to the corresponding function.

Context acquisition and policy validation. Context values come from user instructions, systems, and agent operations. During intent selection, the intent extractor LLM parses user requests and environmental data (e.g., configurations) to obtain contexts. Agent-related contexts are captured in two ways: parameter contexts are obtained when intercepting agent actions, while history contexts are updated after action completion. For system state contexts, values are acquired through CLI (e.g., shell or ADB [16]) or APIs accessible to the agent. Another approach is implementing dedicated system services to provide unified interfaces for context acquisition, which requires platform vendor participation in the ecosystem.

# 6 Security Analysis

In this section, we provide a formal security analysis of CSAgent to demonstrate its effectiveness in protecting CUAs from executing unintended and unsafe actions. We establish formal models for the system behavior and prove key security properties.

### 6.1 Formal Model

**System Model.** We model the system as a tuple  $S = \langle \mathcal{F}, C, \mathcal{U}, \mathcal{E} \rangle$  where the notation is defined in Table 2.

A system state at time t is  $s_t = \langle cv_t, env_t \rangle$  where  $cv_t$  is the current context vector and  $env_t \in \mathcal{E}$ .

**Agent Behavior Model.** An agent  $\mathcal{A}$  maps user instructions and environmental states to function executions:

$$\mathcal{A}: \mathcal{U} \times \mathcal{E} \to \mathcal{F}^* \tag{7}$$

Due to LLM unreliability, we model agent decisions as potentially erroneous:

$$\mathcal{A}_{unrel}(u, env) = \mathcal{A}_{ideal}(u, env) \oplus \mathcal{A}_{error}(u, env)$$
 (8)

where  $\oplus$  denotes probabilistic combination of ideal and erroneous behaviors and  $u \in \mathcal{U}$ .

**Safety Classification.** We partition functions by security risk:

$$\mathcal{F} = \mathcal{F}_{norm} \cup \mathcal{F}_{cond} \cup \mathcal{F}_{dngrs} \tag{9}$$

# **6.2 Security Properties**

**Property 1 (Context-Dependent Safety).** For any function  $f \in \mathcal{F}_{cond}$  executed under user intent i:

Safe
$$(f, i, cv_t) \iff$$
  
 $\forall rule \in P_f(i) : validate(rule.constraint, cv_t) = true$  (10)

**Property 2 (Policy Completeness).** Every security-sensitive function has a corresponding policy that captures all necessary safety conditions:

$$\forall f \in \mathcal{F}_{cond} : \exists P_f \text{ such that Safe}(f, i, cv_t) \equiv \text{PolicySat}(P_f(i), cv_t) \quad (11)$$

**Property 3 (Unauthorized Prevention).** No conditional or dangerous function executes without satisfying security requirements:

$$\forall f \in \mathcal{F}_{cond} \cup \mathcal{F}_{dngrs} : \text{Execute}(f) \Rightarrow \text{Authorized}(f)$$
 (12)

### 6.3 Main Security Theorems

**Theorem 1 (Safety Preservation).** CSAgent ensures no unsafe operations are executed:

$$\forall t, f : \text{Execute}(f, t) \Rightarrow \text{Safe}(f, \text{intent}(u_t), cv_t)$$
 (13)

*Proof.* We prove by contradiction. Assume  $\exists t, f$  such that  $\text{Execute}(f, t) = \text{true but Safe}(f, \text{intent}(u_t), cv_t) = \text{false}$ .

For execution to occur, f must pass CSAgent's validation. If  $f \in \mathcal{F}_{norm}$ , then  $\mathrm{Safe}(f,\mathrm{intent}(u_t),cv_t)=$  true by definition. If  $f \in \mathcal{F}_{dngrs}$ , then explicit user authorization is required, which implies safety. If  $f \in \mathcal{F}_{cond}$ , then execution requires both intent matching and policy satisfaction, which by Property 1 implies safety. All these cases lead to contradictions, thus proving the assumption is false.  $\Box$ 

**Theorem 2 (Utility Preservation).** CSAgent does not prevent legitimate operations:

$$\forall f, i, cv_t : \text{Safe}(f, i, cv_t) \Rightarrow \text{CanExecute}(f, i, cv_t)$$
 (14)

*Proof.* For any safe operation: if  $f \in \mathcal{F}_{norm}$ , CSAgent always permits execution. If  $f \in \mathcal{F}_{cond}$  and Safe $(f, i, cv_t) = \text{true}$ , then by Property 1, all constraints are satisfied and policy validation succeeds.

### 6.4 Threat Analysis

We analyze potential threats to CSAgent's security guarantees, examining scenarios where our approach might fail to prevent unsafe agent operations.

**Prompt Injection Attacks.** Consider an attacker who injects malicious instructions through external data sources (e.g., web pages) that are processed by the agent. Let  $env_{malicious} \in \mathcal{E}$  represent the compromised environmental state containing injected content. The attack aims to manipulate the agent's reasoning process to execute unintended functions. However, for any function f to be executed, it must still satisfy:

$$\exists f \in \mathcal{F}_{cond} : \text{PolicySat}(P_f(\text{intent}(u_t)), cv_t) = \text{true}$$
 (15)

where both the user instruction  $u_t$  and the context vector  $cv_t$  remain trustworthy, as they are derived from legitimate user inputs and authoritative system APIs. Since the policy validation process relies exclusively on these trusted data sources, prompt injection attacks cannot manipulate the validation outcome, effectively mitigating this attack vector. Hallucination and Non-determinism. LLM hallucinations may cause the agent to deviate from ideal behavior, potentially selecting incorrect functions. This can be formalized as:

$$\mathcal{A}_{unrel}(u_t, env_t) \neq \mathcal{A}_{ideal}(u_t, env_t)$$
 (16)

However, our safety guarantee from Theorem 1 still holds because any function execution *f* must satisfy:

$$Safe(f, intent(u_t), cv_t) = true$$
 (17)

Even if hallucination causes the agent to select an unintended function f', the execution will be blocked unless  $f' \in \mathcal{F}_{norm}$  or all contextual constraints in  $P_{f'}(\text{intent}(u_t))$  are satisfied. The multi-layered validation reduces the probability that a hallucinated decision satisfies all required constraints simultaneously.

**Intent Extraction Errors.** A potential threat lies in the LLM-based intent extraction process. If the intent extraction produces incorrect results such that  $intent(u_t) \neq intent_{true}(u_t)$ , this could lead to policy selection errors. However, our design mitigates this risk by constraining the intent extraction to a limited set of legitimate intents, reducing the decision space compared to open-ended generation. Additionally, we use cosine similarity to verify that the selected intent is truly relevant to the user instruction. Incorrect intent selection typically results in policy validation failure rather than unsafe execution, maintaining the safety property.

Policy reliability. The security improvement provided by CSAgent largely depends on the correctness and completeness of the policies. While generating fully correct and complete policies is unrealistic, CSAgent mitigates this issue by leveraging more powerful reasoning models to generate higher-quality policies and iteratively improve them through the PEF. Additionally, we have fallback mechanisms to address situations where policies are incomplete (e.g., missing intents or functions). In such cases, the system requests user intervention or prompts the agent to re-plan, ensuring that uncertain actions are blocked.

# 7 Evaluation

In this section, we conduct a comprehensive evaluation of our CSAgent prototype by answering four key research questions that align with our design goals:

**RQ1:** How well does CSAgent integrate with existing agent frameworks and support diverse interaction modes?

**RQ2:** How effective is the context analyzer at identifying GUI event handlers used for context space generation?

**RQ3:** How accurately can CSAgent identify and prevent unexpected behaviors of computer-use agents?

**RQ4:** How much performance and cost overhead does CSAgent introduce compared to vanilla agent execution?

**RQ5:** How effectively does the Policy Evolution Framework refine context spaces to optimize the trade-off between security, utility, and performance?

# 7.1 Experimental Setup and Benchmarks (RQ1)

To evaluate CSAgent across diverse interaction modalities, we employ three benchmarks: AgentBench [35] (CLI), Agent-Dojo [9] (API), and AndroidWorld [49] (GUI). We use DeepSeek-V3 [33] and Seed1.6 [5] as the runtime text and multimodal models, respectively. The integration mirrors real-world deployment in two steps: first, we generate context spaces for target tools/apps using our analyzer; second, we adapt agent frameworks to the CSAgent service via minimal RPC hooks for intent extraction, validation, and context updates. This successful integration demonstrates CSAgent's strong compatibility (G4).

Our evaluation methodology encompasses three primary dimensions across all benchmarks: utility, security, and overhead. Utility measures the agent's task completion capability under CSAgent protection, security evaluates CSAgent's ability to block unintended behaviors, and overhead quantifies the latency and token consumption introduced by CSAgent. For AndroidWorld specifically, we also conduct an analysis of CSAgent's code identification capabilities for context space generation. We compare it against UI-CTX [29] and AutoDroid [66], representing state-of-the-art approaches in static analysis and GUI exploration, respectively. For security evaluation, all the context policies are generated by the context analyzer (satisfying G3). While AgentDojo provides

<span id="page-11-1"></span>![](_page_11_Figure_1.jpeg)

Figure 6. Comparison of GUI element extraction methods.

built-in adversarial tests, we construct additional security test cases for AgentBench and AndroidWorld. These test cases consist of mismatched user requests and agent actions (i.e., simulating agent actions that violate the user intent), creating a series of pairs that serve as input to evaluate capability to detect anomalous agent behaviors that deviate from user intentions. Notably, the policies we test are generated solely based on the apps themselves, and the policy generation process has no access to the test set.

To emphasize effectiveness, we design our experiments around CSAgent and two other agent configurations. First, we evaluate a *Vanilla Agent* that operates without any security protection mechanisms, serving as our analysis baseline. Second, we implement a *Pre-execution Validation Agent* (PVAgent) that employs dynamic policy generation and validation before executing each action (similar to [55, 60]). Finally, we evaluate CSAgent-RF, a refined variant of CSAgent that leverages PEF, to further demonstrate its effectiveness.

# <span id="page-11-0"></span>7.2 Capability of GUI Analysis (RQ2)

Figure 6 demonstrates CSAgent's capability in extracting GUI elements and event handlers from open-source apps and AOSP system apps used by AndroidWorld. UI-CTX was configured with default settings, while AutoDroid employed the deep learning-based strategy Humanoid [32]. The results show that CSAgent extracts 0.93× more GUI element information (including handlers) than AutoDroid and 3.12× more than UI-CTX (satisfying G3). While some GUI elements are identified by these two baseline methods but missed by CSAgent, most do not produce actual control effects (e.g., merely opening menus rather than clicking specific options). We prompt our context analyzer to ignore these non-functional elements to optimize token consumption. We did not compare to source code-based analysis primarily due to the lack of available tools. Our approach differs by using LLMs to identify GUI-related code, offering better generalization capabilities. Importantly, CSAgent can complement other methods to achieve more comprehensive coverage.

# 7.3 Effectiveness of CSAgent Access Control (RQ3)

Table 3 presents CSAgent's comprehensive attack defense capabilities. The primary evaluation metric is Attack Success Rate (ASR), which measures the success rate of simulated

Table 3. Overall defense capability.

<span id="page-11-2"></span>

| Agent      | AgentDojo |        | AgentBench | AndroidWorld |  |
|------------|-----------|--------|------------|--------------|--|
| Type       | ASR       | UUA    | ASR        | ASR          |  |
| Vanilla    | 46.61%    | 54.26% | -          | -            |  |
| PVAgent    | 4.14%     | 33.03% | 1.00%      | 5.09%        |  |
| CSAgent    | 0%        | 41.61% | 0.11%      | 1.21%        |  |
| CSAgent-RF | 0%        | 54.23% | 0%         | 0%           |  |

<span id="page-11-3"></span>Table 4. Detailed results of AgentDojo injection attacks.

| Agent      | Banking |       | Slack |       | Travel |       | Workspace |       |
|------------|---------|-------|-------|-------|--------|-------|-----------|-------|
| Type       | ASR,%   | UUA,% | ASR,% | UUA,% | ASR,%  | UUA,% | ASR,%     | UUA,% |
| Vanilla    | 45.14   | 59.72 | 85.71 | 64.76 | 49.17  | 29.17 | 6.43      | 63.39 |
| PVAgent    | 0.00    | 36.81 | 0.00  | 4.76  | 15.83  | 40.00 | 0.71      | 50.54 |
| CSAgent    | 0.00    | 40.97 | 0.00  | 18.10 | 0.00   | 40.83 | 0.00      | 50.71 |
| CSAgent-RF | 0.00    | 56.25 | 0.00  | 38.10 | 0.00   | 54.17 | 0.00      | 68.39 |

attacks against agents. Additionally, AgentDojo includes the Utility Under Attacks (UUA) metric, which evaluates an agent's ability to complete original tasks under injection attacks. For the AgentDojo travel task, we exclude one out-of-scope attack that targets LLM output content rather than agent behavior. The results demonstrate that CSAgent achieves average ASR of only 0.44%, successfully defending against approximately 99.56% of attacks (satisfying G1). In comparison, PVAgent defends against 96.59% of attacks. Table 4 provides detailed results for AgentDojo's prompt injection attack tests. CSAgent achieves 100% successful defense across all scenarios. For AgentBench and Android-World, CSAgent did not defend against all attacks. This is due to the context analyzer generating policies that were not sufficiently comprehensive in a single analysis. After a round of iteration through the PEF, CSAgent was able to defend against all attacks. CSAgent outperforms PVAgent mainly due to the nature of static policies, allowing us to use stronger reasoning models to generate and iteratively improve policies with low impact on runtime performance.

The observed UUA drop is due to the high complexity of AgentDojo tasks and the information gap during initial policy generation. Specifically, many tasks in AgentDojo are derived from environmental contexts (e.g., billing files or todo lists) or depend on implicit intermediate actions, rather than direct user instructions. Furthermore, some tasks rely on untrusted data sources, from which CSAgent restricts context extraction to ensure security. In our setup, local context sources (e.g., file systems) are configured as trusted, while online sources (e.g., web and email) are treated as untrusted. Since our context analyzer generates policies based solely on tool code without access to specific task scenarios, the LLM cannot comprehensively reason about such complex execution patterns or diverse user intents in a single analysis, leading to runtime failure. However, as shown in §7.5, the

<span id="page-12-0"></span>![](_page_12_Figure_2.jpeg)

Figure 7. Utility drops and performance overhead of CSAgent.

PEF effectively addresses this limitation through iterative refinement based on runtime feedback.

### 7.4 Performance and Cost Overhead (RQ4)

Figure 7 illustrates the utility drop and extra latency introduced by CSAgent. On all three benchmarks, latency overhead introduced by CSAgent is less than 5%, compared to PVAgent's overhead of 58.57%, 34.28%, and 103.98% on Agent-Bench, AndroidWorld, and AgentDojo, respectively. Additionally, we found that 80.08% of contexts are classified as cold or warm temperature levels. These results demonstrate that our optimized context manager efficiently performs user intent extraction, context updates and policy verification (satisfying G2). For utility, CSAgent causes a 15.58% decrease on average, significantly outperforming PVAgent. The degradation on AgentBench and AndroidWorld is less than 5%, but that on AgentDojo is more pronounced, primarily due to task complexity and insufficient policy quality, as discussed earlier. Notably, upon a policy validation failure during evaluation, the agent is prompted to either explore alternative execution paths or terminate the task. In real deployments, user intervention or agent reflection could resume such tasks, further reducing the impact. To explore this potential, we evaluate a variant incorporating agent reflection upon validation failures. On AgentDojo, this approach reduces the utility drop to 9.93% and improves UUA to 51.79%. However, it incurs a 21.04% latency overhead and increases ASR to 0.455%, as additional LLM requests introduce both computational costs and increased uncertainty. We also evaluated CSAgent's impact on task completion steps. Overall, the impact is minimal, indicating that CSAgent's decisions to allow or block agent actions are relatively accurate.

We further evaluated the complexity of context spaces and their loading latency. Across the three benchmarks (Agent-Bench, AgentDojo, and AndroidWorld), the average number of policies per application, which is also the number of predicted user intents, is 120, 13.25, and 150.4, respectively, with average context counts of 187.0, 25.75, and 238.65. We also analyzed real-world complex apps from AndroidWorld to explore the relationship between app size and context space

<span id="page-12-1"></span>![](_page_12_Figure_8.jpeg)

(a) Policy count vs app size (MB). (b) Loading latency distribution.

**Figure 8.** Context space complexity.

<span id="page-12-2"></span>**Table 5.** Average token consumption per task.

|          | AgentBench | AgentDojo | ${\bf Android World}$ |
|----------|------------|-----------|-----------------------|
| Vanilla  | 2980.36    | 13000.99  | 109296.92             |
| CSAgent  | 5961.70    | 4364.93   | 7161.50               |
| Overhead | 200.03%    | 33.57%    | 6.55%                 |
| Prompt   | 96.44%     | 95.39%    | 97.42%                |

size. As shown in Figure 8a, the policy count grows at a diminishing rate as app size increases. This is mainly because we generate policies only for security-critical functions, which are typically limited in number. Figure 8b shows the loading latency distribution, revealing that 96.00% of context spaces can be loaded within one second. Loading latency correlates directly with context space size and I/O latency. When context spaces are cached, retrieval latency becomes negligible. Therefore, beyond our LRU replacement policy, larger context spaces (such as that for the settings app) can be permanently fixed in cache to further optimize performance.

Table 5 presents CSAgent's per task token consumption compared to the vanilla agent. The geometric mean of consumption overhead is 35.30%, with over 96.41% consisting of prompt tokens, which are less expensive than completion tokens. Generally, more complex tasks have proportionally lower overhead. For instance, AgentBench tasks have low average token consumption, so the large context space results in higher overhead. Conversely, AndroidWorld tasks are highly complex, requiring multimodal capabilities for screen

recognition, leading to very high task token consumption and lower overhead. In comparison, runtime policy generation methods introduce 1.61× additional token consumption on AgentDojo [\[55\]](#page-15-17). CSAgent's low token consumption results from development-phase policy generation that applies across all devices and users without regeneration, and from requiring only one additional LLM inference per task regardless of complexity (satisfying G2).

# <span id="page-13-0"></span>7.5 Efficacy of Policy Evolution (RQ5)

To validate the PEF's effectiveness, we focus on AgentDojo, where CSAgent exhibits the most significant utility degradation, and iteratively refine the corresponding context spaces. Specifically, we consolidate logs from both utility and security tests, enabling the LLM to simultaneously consider utility and security trade-offs during refinement. PEF iteratively tests and upgrades each context space until either no further improvements are identified or sufficiently high evaluation scores are achieved. In our experiments, convergence requires an average of 7.25 iterations per context space.

As shown in Table [4,](#page-11-3) CSAgent-RF maintains 0% ASR while improving UUA to 54.23%, demonstrating enhanced utility preservation without compromising security guarantees. Figure [7](#page-12-0) shows the performance improvements: CSAgent-RF reduces utility drop to 6.76% and latency overhead to 0.53%. Across all benchmarks, the overall utility decrease is reduced to 5.42%, with an average latency overhead of only 1.99%. Notably, the reduced latency overhead primarily stems from a decrease in the average number of completion steps for some complex tasks. More precise policies enable the agent to execute tasks more efficiently by eliminating unnecessary validation failures and re-planning cycles. Our analysis reveals three primary categories of improvements in the refined context spaces. First, PEF generates more explicit and fine-grained intent definitions. Second, PEF produces more precise constraint conditions and validation logic. Third, PEF relaxes overly conservative security constraints that unnecessarily block benign operations. As a result, CSAgent-RF achieves more accurate runtime intent extraction and policy retrieval, performs more precise validation, and maintains an effective balance between blocking dangerous operations and permitting legitimate actions.

# 8 Discussion

CSAgent supports automated policy generation and iterative improvement through the PEF based on runtime feedback. However, an automated testing tool is still needed to cover a broader range of agent actions and attacks, allowing for largescale testing of policy completeness and further refinement. Currently, CSAgent focuses on protecting single-agent scenarios. However, multi-agent collaboration introduces more complex challenges, such as cross-agent context transfer, which we plan to explore in future work. CSAgent can be

applied to website scenarios. Our evaluation included apps written in TypeScript, showing the method's compatibility. However, web environments are more fragmented and often face more content security issues, limiting the effectiveness of access control. Generating policies for GUI apps through source code analysis remains a potential hurdle for further adoption of this approach. Nevertheless, we provide a comprehensive automated toolchain that assists developers in constructing and maintaining policies. We argue that, similar to traditional security models, agent security requires an ecosystem-wide effort to enhance the quality of protections and foster stronger collaboration in policy creation.

# 9 Related Work

Access control and contextual integrity. Traditional access control mechanisms in OS include discretionary access control (DAC) and mandatory access control (MAC) [\[52\]](#page-15-15). SELinux [\[58,](#page-15-16) [69\]](#page-16-8) exemplifies MAC principles by defining fine-grained policies that govern process interactions and resource access based on security contexts. The theory of contextual integrity (CI) [\[39,](#page-15-30) [40\]](#page-15-13), proposed in more recent years, has been explored by researchers for its applications in existing operating systems [\[50,](#page-15-14) [67\]](#page-16-7), driving the evolution of permission management and access control toward more user-transparent, secure, and flexible approaches.

Access control for LLM agents. For agents, access control focuses on constraining tool calls through pre-execution validation. Most approaches use contextual information to make authorization decisions, following the CI principle. AirGapAgent [\[4\]](#page-14-11) employs a separate LLM to directly make decisions about data access permissions. GuardAgent [\[73\]](#page-16-9) employs LLMs to generate guardrail code that validates predefined rules before executing actions. VeriSafe Agent [\[27\]](#page-14-13) describes rules through Horn clauses and verifies agent behavior based on logic-based reasoning. ShieldAgent [\[7\]](#page-14-12) enforces explicit policy compliance by constructing actionbased probabilistic rule circuits for formal verification. Quad-Sentinel [\[77\]](#page-16-10) employs a multi-agent guard team to enforce safety through machine-checkable sequent logic rules derived from natural language policies. Conseca [\[60\]](#page-15-18) and Progent [\[55\]](#page-15-17) achieve dynamic security policy generation, enabling more autonomous responses to diverse task scenarios. AgentSentinel [\[21\]](#page-14-18) extends context extraction to the OS, providing real-time protection for CUAs by combining rulebased and LLM-based auditing. These approaches rely on runtime LLM-based security decision-making, suffering from security or performance limitations. AgentSpec [\[63\]](#page-15-31) employs predefined static policies, but adopts a risk-blocking paradigm that struggles with unknown threats and lacks user intent differentiation, limiting policy flexibility.

Other system-level LLM agent protection. Beyond access control, some other forms of system-level protection have been proposed for agents. The Instruction Hierarchy [\[61\]](#page-15-32)

and StruQ [\[6\]](#page-14-26) implement privilege and type separation for LLM inputs to mitigate interference between different input sources. f -secure LLM system [\[70\]](#page-16-13), RTBAS [\[80\]](#page-16-14), and SAFEFLOW [\[30\]](#page-14-27) introduce information flow control into LLM agents to prevent prompt injection and privacy leakage. GoEX [\[46\]](#page-15-33) implements post-facto validation of agent actions and isolates dangerous operations through sandboxing. IsolateGPT [\[71\]](#page-16-15) employs isolation for multi-LLM application scenarios to prevent interference between LLMs and different applications. ACE [\[28\]](#page-14-28) decouples agent planning into two phases to defend against untrusted third-party apps. These approaches and CSAgent can collectively form part of a defense-in-depth strategy [\[17\]](#page-14-29), working in conjunction to achieve more comprehensive protection.

# 10 Conclusion

We present CSAgent, a secure, efficient, and flexible access control framework to protect computer-use agents. CSAgent introduces a novel context space design that enforces contextual and intent-aware policies to validate agent actions. Evaluation shows that CSAgent provides strong security guarantees while incurring acceptable overhead.

# References

- <span id="page-14-2"></span>[1] Anthropic. 2025. Bash tool. [https://docs.anthropic.com/en/docs/](https://docs.anthropic.com/en/docs/agents-and-tools/tool-use/bash-tool) [agents-and-tools/tool-use/bash-tool](https://docs.anthropic.com/en/docs/agents-and-tools/tool-use/bash-tool).
- <span id="page-14-4"></span>[2] Anthropic. 2025. Computer use tool. [https://docs.anthropic.com/en/](https://docs.anthropic.com/en/docs/agents-and-tools/tool-use/computer-use-tool) [docs/agents-and-tools/tool-use/computer-use-tool](https://docs.anthropic.com/en/docs/agents-and-tools/tool-use/computer-use-tool).
- <span id="page-14-0"></span>[3] Apple. 2025. Integrating actions with Siri and Apple Intelligence. [https://developer.apple.com/documentation/appintents/](https://developer.apple.com/documentation/appintents/integrating-actions-with-siri-and-apple-intelligence) [integrating-actions-with-siri-and-apple-intelligence](https://developer.apple.com/documentation/appintents/integrating-actions-with-siri-and-apple-intelligence).
- <span id="page-14-11"></span>[4] Eugene Bagdasarian, Ren Yi, Sahra Ghalebikesabi, Peter Kairouz, Marco Gruteser, Sewoong Oh, Borja Balle, and Daniel Ramage. 2024. AirGapAgent: Protecting privacy-conscious conversational agents. In Proceedings of the 2024 on ACM SIGSAC Conference on Computer and Communications Security. 3868–3882.
- <span id="page-14-24"></span>[5] ByteDance. 2025. Introduction to Techniques Used in Seed1.6. [https:](https://seed.bytedance.com/en/seed1_6) [//seed.bytedance.com/en/seed1\\_6](https://seed.bytedance.com/en/seed1_6).
- <span id="page-14-26"></span>[6] Sizhe Chen, Julien Piet, Chawin Sitawarin, and David Wagner. 2024. Struq: Defending against prompt injection with structured queries. arXiv preprint arXiv:2402.06363 (2024).
- <span id="page-14-12"></span>[7] Zhaorun Chen, Mintong Kang, and Bo Li. 2025. ShieldAgent: Shielding Agents via Verifiable Safety Policy Reasoning. In Forty-second International Conference on Machine Learning. [https://openreview.net/forum?](https://openreview.net/forum?id=DkRYImuQA9) [id=DkRYImuQA9](https://openreview.net/forum?id=DkRYImuQA9)
- <span id="page-14-10"></span>[8] Visual Studio Code. 2025. Use agent mode in VS Code. [https://code.](https://code.visualstudio.com/docs/copilot/chat/chat-agent-mode) [visualstudio.com/docs/copilot/chat/chat-agent-mode](https://code.visualstudio.com/docs/copilot/chat/chat-agent-mode).
- <span id="page-14-14"></span>[9] Edoardo Debenedetti, Jie Zhang, Mislav Balunovic, Luca Beurer-Kellner, Marc Fischer, and Florian Tramèr. 2024. AgentDojo: A Dynamic Environment to Evaluate Prompt Injection Attacks and Defenses for LLM Agents. In Advances in Neural Information Processing Systems, A. Globerson, L. Mackey, D. Belgrave, A. Fan, U. Paquet, J. Tomczak, and C. Zhang (Eds.), Vol. 37. Curran Associates, Inc., 82895–82920. [https://proceedings.neurips.cc/paper\\_](https://proceedings.neurips.cc/paper_files/paper/2024/file/97091a5177d8dc64b1da8bf3e1f6fb54-Paper-Datasets_and_Benchmarks_Track.pdf) [files/paper/2024/file/97091a5177d8dc64b1da8bf3e1f6fb54-Paper-](https://proceedings.neurips.cc/paper_files/paper/2024/file/97091a5177d8dc64b1da8bf3e1f6fb54-Paper-Datasets_and_Benchmarks_Track.pdf)[Datasets\\_and\\_Benchmarks\\_Track.pdf](https://proceedings.neurips.cc/paper_files/paper/2024/file/97091a5177d8dc64b1da8bf3e1f6fb54-Paper-Datasets_and_Benchmarks_Track.pdf)
- <span id="page-14-6"></span>[10] Gelei Deng, Yi Liu, Yuekang Li, Kailong Wang, Ying Zhang, Zefeng Li, Haoyu Wang, Tianwei Zhang, and Yang Liu. 2024. Masterkey: Automated jailbreak across multiple large language model chatbots. In

- Proceedings of the Network and Distributed System Security Symposium (NDSS'24).
- <span id="page-14-15"></span>[11] Yu Du, Fangyun Wei, and Hongyang Zhang. 2024. Anytool: Selfreflective, hierarchical agents for large-scale api calls. arXiv preprint arXiv:2402.04253 (2024).
- <span id="page-14-16"></span>[12] Hugging Face. 2025. Function Calling. [https://huggingface.co/docs/](https://huggingface.co/docs/hugs/guides/function-calling) [hugs/guides/function-calling](https://huggingface.co/docs/hugs/guides/function-calling).
- <span id="page-14-22"></span>[13] Inc. GitHub. 2021. CodeQL. <https://codeql.github.com>.
- <span id="page-14-9"></span>[14] Yichen Gong, Delong Ran, Xinlei He, Tianshuo Cong, Anyu Wang, and Xiaoyun Wang. 2025. Safety misalignment against large language models. In Proceedings 2025 Network and Distributed System Security Symposium (NDSS'25).
- <span id="page-14-1"></span>[15] Google. 2025. AI Edge Function Calling guide. [https://ai.google.dev/](https://ai.google.dev/edge/mediapipe/solutions/genai/function_calling) [edge/mediapipe/solutions/genai/function\\_calling](https://ai.google.dev/edge/mediapipe/solutions/genai/function_calling).
- <span id="page-14-23"></span>[16] Google. 2025. Android Debug Bridge (adb). [https://developer.android.](https://developer.android.com/tools/adb) [com/tools/adb](https://developer.android.com/tools/adb).
- <span id="page-14-29"></span>[17] Google. 2025. Google's Approach for Secure AI Agents: An Introduction. [https://storage.googleapis.com/gweb-research2023-media/](https://storage.googleapis.com/gweb-research2023-media/pubtools/1018686.pdf) [pubtools/1018686.pdf](https://storage.googleapis.com/gweb-research2023-media/pubtools/1018686.pdf).
- <span id="page-14-7"></span>[18] Kai Greshake, Sahar Abdelnabi, Shailesh Mishra, Christoph Endres, Thorsten Holz, and Mario Fritz. 2023. Not what you've signed up for: Compromising real-world llm-integrated applications with indirect prompt injection. In Proceedings of the 16th ACM Workshop on Artificial Intelligence and Security. 79–90.
- <span id="page-14-21"></span>[19] Daya Guo, Dejian Yang, Haowei Zhang, Junxiao Song, Ruoyu Zhang, Runxin Xu, Qihao Zhu, Shirong Ma, Peiyi Wang, Xiao Bi, et al. 2025. Deepseek-r1: Incentivizing reasoning capability in llms via reinforcement learning. arXiv preprint arXiv:2501.12948 (2025).
- <span id="page-14-5"></span>[20] Wenyi Hong, Weihan Wang, Qingsong Lv, Jiazheng Xu, Wenmeng Yu, Junhui Ji, Yan Wang, Zihan Wang, Yuxiao Dong, Ming Ding, et al. 2024. Cogagent: A visual language model for gui agents. In Proceedings of the IEEE/CVF Conference on Computer Vision and Pattern Recognition. 14281–14290.
- <span id="page-14-18"></span>[21] Haitao Hu, Peng Chen, Yanpeng Zhao, and Yuqi Chen. 2025. AgentSentinel: An End-to-End and Real-Time Security Defense Framework for Computer-Use Agents. arXiv[:2509.07764](https://arxiv.org/abs/2509.07764) [cs.CR] [https://arxiv.org/abs/](https://arxiv.org/abs/2509.07764) [2509.07764](https://arxiv.org/abs/2509.07764)
- <span id="page-14-8"></span>[22] Lei Huang, Weijiang Yu, Weitao Ma, Weihong Zhong, Zhangyin Feng, Haotian Wang, Qianglong Chen, Weihua Peng, Xiaocheng Feng, Bing Qin, et al. 2025. A survey on hallucination in large language models: Principles, taxonomy, challenges, and open questions. ACM Transactions on Information Systems 43, 2 (2025), 1–55.
- <span id="page-14-20"></span>[23] Michael Kerrisk. 2025. Linux man pages online. [https://man7.org/](https://man7.org/linux/man-pages/) [linux/man-pages/](https://man7.org/linux/man-pages/).
- <span id="page-14-17"></span>[24] LangChain. 2025. File System Tool. [https://python.langchain.com/](https://python.langchain.com/docs/integrations/tools/filesystem/) [docs/integrations/tools/filesystem/](https://python.langchain.com/docs/integrations/tools/filesystem/).
- <span id="page-14-3"></span>[25] LangChain. 2025. Shell (Bash) Tool. [https://python.langchain.com/](https://python.langchain.com/docs/integrations/tools/bash/) [docs/integrations/tools/bash/](https://python.langchain.com/docs/integrations/tools/bash/).
- <span id="page-14-19"></span>[26] LangChain. 2025. Tools. [https://python.langchain.com/docs/](https://python.langchain.com/docs/integrations/tools/) [integrations/tools/](https://python.langchain.com/docs/integrations/tools/).
- <span id="page-14-13"></span>[27] Jungjae Lee, Dongjae Lee, Chihun Choi, Youngmin Im, Jaeyoung Wi, Kihong Heo, Sangeun Oh, Sunjae Lee, and Insik Shin. 2025. Safeguarding mobile gui agent via logic-based action verification. arXiv preprint arXiv:2503.18492 (2025).
- <span id="page-14-28"></span>[28] Evan Li, Tushin Mallick, Evan Rose, William Robertson, Alina Oprea, and Cristina Nita-Rotaru. 2025. ACE: A Security Architecture for LLM-Integrated App Systems. arXiv[:2504.20984](https://arxiv.org/abs/2504.20984) [cs.CR] [https://arxiv.](https://arxiv.org/abs/2504.20984) [org/abs/2504.20984](https://arxiv.org/abs/2504.20984)
- <span id="page-14-25"></span>[29] Jiawei Li, Jiahao Liu, Jian Mao, Jun Zeng, and Zhenkai Liang. 2025. UI-CTX: Understanding UI Behaviors with Code Contexts for Mobile Applications. In NDSS.
- <span id="page-14-27"></span>[30] Peiran Li, Xinkai Zou, Zhuohang Wu, Ruifeng Li, Shuo Xing, Hanwen Zheng, Zhikai Hu, Yuping Wang, Haoxi Li, Qin Yuan, Yingmo

- Zhang, and Zhengzhong Tu. 2025. SAFEFLOW: A Principled Protocol for Trustworthy and Transactional Autonomous Agent Systems. arXiv[:2506.07564](https://arxiv.org/abs/2506.07564) [cs.AI] <https://arxiv.org/abs/2506.07564>
- <span id="page-15-10"></span>[31] Yuanchun Li, Hao Wen, Weijun Wang, Xiangyu Li, Yizhen Yuan, Guohong Liu, Jiacheng Liu, Wenxing Xu, Xiang Wang, Yi Sun, et al. 2024. Personal llm agents: Insights and survey about the capability, efficiency and security. arXiv preprint arXiv:2401.05459 (2024).
- <span id="page-15-29"></span>[32] Yuanchun Li, Ziyue Yang, Yao Guo, and Xiangqun Chen. 2019. Humanoid: A Deep Learning-Based Approach to Automated Black-box Android App Testing. In 2019 34th IEEE/ACM International Conference on Automated Software Engineering (ASE). 1070–1073. doi:[10.1109/ASE.](https://doi.org/10.1109/ASE.2019.00104) [2019.00104](https://doi.org/10.1109/ASE.2019.00104)
- <span id="page-15-28"></span>[33] Aixin Liu, Bei Feng, Bing Xue, Bingxuan Wang, Bochao Wu, Chengda Lu, Chenggang Zhao, Chengqi Deng, Chenyu Zhang, Chong Ruan, et al. 2024. Deepseek-v3 technical report. arXiv preprint arXiv:2412.19437 (2024).
- <span id="page-15-24"></span>[34] Tong Liu, Zizhuang Deng, Guozhu Meng, Yuekang Li, and Kai Chen. 2024. Demystifying rce vulnerabilities in llm-integrated apps. In Proceedings of the 2024 on ACM SIGSAC Conference on Computer and Communications Security. 1716–1730.
- <span id="page-15-19"></span>[35] Xiao Liu, Hao Yu, Hanchen Zhang, Yifan Xu, Xuanyu Lei, Hanyu Lai, Yu Gu, Hangliang Ding, Kaiwen Men, Kejuan Yang, Shudan Zhang, Xiang Deng, Aohan Zeng, Zhengxiao Du, Chenhui Zhang, Sheng Shen, Tianjun Zhang, Yu Su, Huan Sun, Minlie Huang, Yuxiao Dong, and Jie Tang. 2023. AgentBench: Evaluating LLMs as Agents. arXiv[:2308.03688](https://arxiv.org/abs/2308.03688) [cs.AI] <https://arxiv.org/abs/2308.03688>
- <span id="page-15-6"></span>[36] Yupei Liu, Yuqi Jia, Runpeng Geng, Jinyuan Jia, and Neil Zhenqiang Gong. 2024. Formalizing and benchmarking prompt injection attacks and defenses. In 33rd USENIX Security Symposium (USENIX Security 24). 1831–1847.
- <span id="page-15-23"></span>[37] Microsoft. 2025. Microsoft 365 Copilot overview. [https:](https://learn.microsoft.com/en-us/copilot/microsoft-365/microsoft-365-copilot-overview) [//learn.microsoft.com/en-us/copilot/microsoft-365/microsoft-](https://learn.microsoft.com/en-us/copilot/microsoft-365/microsoft-365-copilot-overview)[365-copilot-overview](https://learn.microsoft.com/en-us/copilot/microsoft-365/microsoft-365-copilot-overview).
- <span id="page-15-27"></span>[38] Microsoft. 2025. PowerShell Documentation. [https://learn.microsoft.](https://learn.microsoft.com/en-us/powershell/) [com/en-us/powershell/](https://learn.microsoft.com/en-us/powershell/).
- <span id="page-15-30"></span>[39] Helen Nissenbaum. 2004. Privacy as contextual integrity. Wash. L. Rev. 79 (2004), 119.
- <span id="page-15-13"></span>[40] Helen Nissenbaum. 2009. Privacy in context: Technology, policy, and the integrity of social life. In Privacy in context. Stanford University Press.
- <span id="page-15-2"></span>[41] OpenAI. 2025. Computer-Using Agent. [https://openai.com/index/](https://openai.com/index/computer-using-agent/) [computer-using-agent/](https://openai.com/index/computer-using-agent/).
- <span id="page-15-21"></span>[42] OpenAI. 2025. Function Calling. [https://platform.openai.com/docs/](https://platform.openai.com/docs/guides/function-calling?api-mode=chat) [guides/function-calling?api-mode=chat](https://platform.openai.com/docs/guides/function-calling?api-mode=chat).
- <span id="page-15-1"></span>[43] OpenAI. 2025. Local Shell Tool. [https://platform.openai.com/docs/](https://platform.openai.com/docs/guides/tools-local-shell) [guides/tools-local-shell](https://platform.openai.com/docs/guides/tools-local-shell).
- <span id="page-15-26"></span>[44] OWASP. 2024. OWASP Top 10 for LLM Applications 2025. [https://](https://genai.owasp.org/resource/owasp-top-10-for-llm-applications-2025/) [genai.owasp.org/resource/owasp-top-10-for-llm-applications-2025/](https://genai.owasp.org/resource/owasp-top-10-for-llm-applications-2025/).
- <span id="page-15-25"></span>[45] Shishir G. Patil, Tianjun Zhang, Vivian Fang, Noppapon C., Roy Huang, Aaron Hao, Martin Casado, Joseph E. Gonzalez, Raluca Ada Popa, and Ion Stoica. 2024. GoEX: Perspectives and Designs Towards a Runtime for Autonomous LLM Applications. arXiv[:2404.06921](https://arxiv.org/abs/2404.06921) [cs.CL] <https://arxiv.org/abs/2404.06921>
- <span id="page-15-33"></span>[46] Shishir G Patil, Tianjun Zhang, Vivian Fang, Roy Huang, Aaron Hao, Martin Casado, Joseph E Gonzalez, Raluca Ada Popa, Ion Stoica, et al. 2024. GoEX: Perspectives and Designs Towards a Runtime for Autonomous LLM Applications. CoRR (2024).
- <span id="page-15-22"></span>[47] Yujia Qin, Shihao Liang, Yining Ye, Kunlun Zhu, Lan Yan, Yaxi Lu, Yankai Lin, Xin Cong, Xiangru Tang, Bill Qian, et al. 2023. Toolllm: Facilitating large language models to master 16000+ real-world apis. arXiv preprint arXiv:2307.16789 (2023).
- <span id="page-15-3"></span>[48] Yujia Qin, Yining Ye, Junjie Fang, Haoming Wang, Shihao Liang, Shizuo Tian, Junda Zhang, Jiahao Li, Yunxin Li, Shijue Huang, et al. 2025. UI-TARS: Pioneering Automated GUI Interaction with Native Agents.

- arXiv preprint arXiv:2501.12326 (2025).
- <span id="page-15-20"></span>[49] Christopher Rawles, Sarah Clinckemaillie, Yifan Chang, Jonathan Waltz, Gabrielle Lau, Marybeth Fair, Alice Li, William Bishop, Wei Li, Folawiyo Campbell-Ajala, et al. 2024. Androidworld: A dynamic benchmarking environment for autonomous agents. arXiv preprint arXiv:2405.14573 (2024).
- <span id="page-15-14"></span>[50] Franziska Roesner, Tadayoshi Kohno, Alexander Moshchuk, Bryan Parno, Helen J Wang, and Crispin Cowan. 2012. User-driven access control: Rethinking permission granting in modern operating systems. In 2012 IEEE Symposium on Security and Privacy. IEEE, 224–238.
- <span id="page-15-0"></span>[51] Pascal J Sager, Benjamin Meyer, Peng Yan, Rebekka von Wartburg-Kottler, Layan Etaiwi, Aref Enayati, Gabriel Nobel, Ahmed Abdulkadir, Benjamin F Grewe, and Thilo Stadelmann. 2025. AI Agents for Computer Use: A Review of Instruction-based Computer Control, GUI Automation, and Operator Assistants. arXiv preprint arXiv:2501.16150 (2025).
- <span id="page-15-15"></span>[52] Ravi Sandhu and Pierangela Samarati. 1996. Authentication, access control, and audit. ACM Computing Surveys (CSUR) 28, 1 (1996), 241– 243.
- <span id="page-15-7"></span>[53] Xinyue Shen, Zeyuan Chen, Michael Backes, Yun Shen, and Yang Zhang. 2024. " do anything now": Characterizing and evaluating inthe-wild jailbreak prompts on large language models. In Proceedings of the 2024 on ACM SIGSAC Conference on Computer and Communications Security. 1671–1685.
- <span id="page-15-8"></span>[54] Jiawen Shi, Zenghui Yuan, Yinuo Liu, Yue Huang, Pan Zhou, Lichao Sun, and Neil Zhenqiang Gong. 2024. Optimization-based prompt injection attack to llm-as-a-judge. In Proceedings of the 2024 on ACM SIGSAC Conference on Computer and Communications Security. 660– 674.
- <span id="page-15-17"></span>[55] Tianneng Shi, Jingxuan He, Zhun Wang, Linyu Wu, Hongwei Li, Wenbo Guo, and Dawn Song. 2025. Progent: Programmable privilege control for LLM agents. arXiv preprint arXiv:2504.11703 (2025).
- <span id="page-15-11"></span>[56] Yucheng Shi, Wenhao Yu, Wenlin Yao, Wenhu Chen, and Ninghao Liu. 2025. Towards Trustworthy GUI Agents: A Survey. arXiv[:2503.23434](https://arxiv.org/abs/2503.23434) [cs.LG] <https://arxiv.org/abs/2503.23434>
- <span id="page-15-9"></span>[57] Varin Sikka and Vishal Sikka. 2025. Hallucination Stations: On Some Basic Limitations of Transformer-Based Language Models. arXiv preprint arXiv:2507.07505 (2025).
- <span id="page-15-16"></span>[58] Stephen Smalley and Robert Craig. 2013. Security enhanced (se) android: bringing flexible mac to android.. In Proceedings of the Network and Distributed System Security Symposium (NDSS'13).
- <span id="page-15-4"></span>[59] Hongjin Su, Ruoxi Sun, Jinsung Yoon, Pengcheng Yin, Tao Yu, and Sercan Ö Arık. 2025. Learn-by-interact: A Data-Centric Framework for Self-Adaptive Agents in Realistic Environments. arXiv preprint arXiv:2501.10893 (2025).
- <span id="page-15-18"></span>[60] Lillian Tsai and Eugene Bagdasarian. 2025. Contextual Agent Security: A Policy for Every Purpose. In Proceedings of the 2025 Workshop on Hot Topics in Operating Systems (Banff, AB, Canada) (HotOS '25). Association for Computing Machinery, New York, NY, USA, 8–17. doi:[10.1145/3713082.3730378](https://doi.org/10.1145/3713082.3730378)
- <span id="page-15-32"></span>[61] Eric Wallace, Kai Xiao, Reimar Leike, Lilian Weng, Johannes Heidecke, and Alex Beutel. 2024. The instruction hierarchy: Training llms to prioritize privileged instructions. arXiv preprint arXiv:2404.13208 (2024).
- <span id="page-15-5"></span>[62] Bryan Wang, Gang Li, and Yang Li. 2023. Enabling conversational interaction with mobile ui using large language models. In Proceedings of the 2023 CHI Conference on Human Factors in Computing Systems. 1–17.
- <span id="page-15-31"></span>[63] Haoyu Wang, Christopher M. Poskitt, and Jun Sun. 2025. AgentSpec: Customizable Runtime Enforcement for Safe and Reliable LLM Agents. arXiv[:2503.18666](https://arxiv.org/abs/2503.18666) [cs.AI] <https://arxiv.org/abs/2503.18666>
- <span id="page-15-12"></span>[64] Shuai Wang, Weiwen Liu, Jingxuan Chen, Yuqi Zhou, Weinan Gan, Xingshan Zeng, Yuhan Che, Shuai Yu, Xinlong Hao, Kun Shao, Bin Wang, Chuhan Wu, Yasheng Wang, Ruiming Tang, and Jianye Hao. 2025. GUI Agents with Foundation Models: A Comprehensive Survey.

- arXiv[:2411.04890](https://arxiv.org/abs/2411.04890) [cs.AI] <https://arxiv.org/abs/2411.04890>
- <span id="page-16-2"></span>[65] Alexander Wei, Nika Haghtalab, and Jacob Steinhardt. 2023. Jailbroken: How does llm safety training fail? Advances in Neural Information Processing Systems 36 (2023), 80079–80110.
- <span id="page-16-1"></span>[66] Hao Wen, Yuanchun Li, Guohong Liu, Shanhui Zhao, Tao Yu, Toby Jia-Jun Li, Shiqi Jiang, Yunhao Liu, Yaqin Zhang, and Yunxin Liu. 2024. Autodroid: Llm-powered task automation in android. In Proceedings of the 30th Annual International Conference on Mobile Computing and Networking. 543–557.
- <span id="page-16-7"></span>[67] Primal Wijesekera, Arjun Baokar, Ashkan Hosseini, Serge Egelman, David Wagner, and Konstantin Beznosov. 2015. Android permissions remystified: A field study on contextual integrity. In 24th USENIX Security Symposium (USENIX Security 15). 499–514.
- <span id="page-16-5"></span>[68] Yotam Wolf, Noam Wies, Oshri Avnery, Yoav Levine, and Amnon Shashua. 2023. Fundamental limitations of alignment in large language models. arXiv preprint arXiv:2304.11082 (2023).
- <span id="page-16-8"></span>[69] Chris Wright, Crispin Cowan, Stephen Smalley, James Morris, and Greg Kroah-Hartman. 2002. Linux security modules: General security support for the linux kernel. In 11th USENIX security symposium (USENIX Security 02).
- <span id="page-16-13"></span>[70] Fangzhou Wu, Ethan Cecchetti, and Chaowei Xiao. 2024. System-Level Defense against Indirect Prompt Injection Attacks: An Information Flow Control Perspective. arXiv[:2409.19091](https://arxiv.org/abs/2409.19091) [cs.CR] [https://arxiv.org/](https://arxiv.org/abs/2409.19091) [abs/2409.19091](https://arxiv.org/abs/2409.19091)
- <span id="page-16-15"></span>[71] Yuhao Wu, Franziska Roesner, Tadayoshi Kohno, Ning Zhang, and Umar Iqbal. 2025. IsolateGPT: An Execution Isolation Architecture for LLM-Based Agentic Systems. In NDSS.
- <span id="page-16-11"></span>[72] Zhiheng Xi, Wenxiang Chen, Xin Guo, Wei He, Yiwen Ding, Boyang Hong, Ming Zhang, Junzhe Wang, Senjie Jin, Enyu Zhou, et al. 2025. The rise and potential of large language model based agents: A survey. Science China Information Sciences 68, 2 (2025), 121101.
- <span id="page-16-9"></span>[73] Zhen Xiang, Linzhi Zheng, Yanjie Li, Junyuan Hong, Qinbin Li, Han Xie, Jiawei Zhang, Zidi Xiong, Chulin Xie, Carl Yang, et al. 2024. Guardagent: Safeguard llm agents by a guard agent via knowledgeenabled reasoning. arXiv preprint arXiv:2406.09187 (2024).
- <span id="page-16-12"></span>[74] Tianbao Xie, Danyang Zhang, Jixuan Chen, Xiaochuan Li, Siheng Zhao, Ruisheng Cao, Toh Jing Hua, Zhoujun Cheng, Dongchan Shin, Fangyu Lei, Yitao Liu, Yiheng Xu, Shuyan Zhou, Silvio Savarese, Caiming Xiong, Victor Zhong, and Tao Yu. 2024. OS-World: Benchmarking Multimodal Agents for Open-Ended Tasks in Real Computer Environments. In Advances in Neural Information Processing Systems, A. Globerson, L. Mackey, D. Belgrave, A. Fan, U. Paquet, J. Tomczak, and C. Zhang (Eds.), Vol. 37. Curran Associates, Inc., 52040–52094. [https://proceedings.neurips.cc/paper\\_](https://proceedings.neurips.cc/paper_files/paper/2024/file/5d413e48f84dc61244b6be550f1cd8f5-Paper-Datasets_and_Benchmarks_Track.pdf) [files/paper/2024/file/5d413e48f84dc61244b6be550f1cd8f5-Paper-](https://proceedings.neurips.cc/paper_files/paper/2024/file/5d413e48f84dc61244b6be550f1cd8f5-Paper-Datasets_and_Benchmarks_Track.pdf)[Datasets\\_and\\_Benchmarks\\_Track.pdf](https://proceedings.neurips.cc/paper_files/paper/2024/file/5d413e48f84dc61244b6be550f1cd8f5-Paper-Datasets_and_Benchmarks_Track.pdf)
- <span id="page-16-0"></span>[75] Jiaming Xu, Kaibin Guo, Wuxuan Gong, and Runyu Shi. 2024. OS-Agent: Copiloting Operating System with LLM-based Agent. In 2024 International Joint Conference on Neural Networks (IJCNN). IEEE, 1–9.
- <span id="page-16-6"></span>[76] Ziwei Xu, Sanjay Jain, and Mohan Kankanhalli. 2024. Hallucination is inevitable: An innate limitation of large language models. arXiv preprint arXiv:2401.11817 (2024).
- <span id="page-16-10"></span>[77] Yiliu Yang, Yilei Jiang, Qunzhong Wang, Yingshui Tan, Xiaoyong Zhu, Sherman S. M. Chow, Bo Zheng, and Xiangyu Yue. 2025. QuadSentinel: Sequent Safety for Machine-Checkable Control in Multi-agent Systems. arXiv[:2512.16279](https://arxiv.org/abs/2512.16279) [cs.AI] <https://arxiv.org/abs/2512.16279>
- <span id="page-16-3"></span>[78] Zhiyuan Yu, Xiaogeng Liu, Shunning Liang, Zach Cameron, Chaowei Xiao, and Ning Zhang. 2024. Don't listen to me: understanding and exploring jailbreak prompts of large language models. In 33rd USENIX Security Symposium (USENIX Security 24). 4675–4692.
- <span id="page-16-4"></span>[79] Chaoyun Zhang, Shilin He, Jiaxu Qian, Bowen Li, Liqun Li, Si Qin, Yu Kang, Minghua Ma, Guyue Liu, Qingwei Lin, Saravan Rajmohan, Dongmei Zhang, and Qi Zhang. 2025. Large Language Model-Brained GUI Agents: A Survey. arXiv[:2411.18279](https://arxiv.org/abs/2411.18279) [cs.AI] [https://arxiv.org/abs/](https://arxiv.org/abs/2411.18279)

[2411.18279](https://arxiv.org/abs/2411.18279)

<span id="page-16-14"></span>[80] Peter Yong Zhong, Siyuan Chen, Ruiqi Wang, McKenna McCall, Ben L. Titzer, Heather Miller, and Phillip B. Gibbons. 2025. RTBAS: Defending LLM Agents Against Prompt Injection and Privacy Leakage. arXiv[:2502.08966](https://arxiv.org/abs/2502.08966) [cs.CR] <https://arxiv.org/abs/2502.08966>