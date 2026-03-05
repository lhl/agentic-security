                                             Secure and Efficient Access Control Framework for
                                                  Computer-Use Agents via Context Space
                                                                         Haochen Gong, Chenxiao Li, Rui Chang, Wenbo Shen
                                                                                                Zhejiang University
                                                                                             Hangzhou, Zhejiang, China

                                         Abstract                                                                79], violating the principle of least privilege. Consequently,
                                         Large language model (LLM)-based computer-use agents                    agents may execute unintended, irreversible actions, such
                                         represent a convergence of AI and OS capabilities, enabling             as deleting data, transferring funds, or unlocking devices,
                                         natural language to control system- and application-level               resulting in severe financial loss or physical harm.
                                                                                                                    As it is impractical to address these issues through model




arXiv:2509.22256v4 [cs.CR] 14 Jan 2026
                                         functions. However, due to LLMs’ inherent uncertainty is-
                                         sues, granting agents control over computers poses signif-              training alone [14, 65, 68, 76], commercial agents usually
                                         icant security risks. When agent actions deviate from user              rely on external safeguards to mitigate risks. For example,
                                         intentions, they can cause irreversible consequences. Exist-            many agents [2, 8, 41] require user confirmations before per-
                                         ing mitigation approaches, such as user confirmation and                forming actions. However, this approach burdens the user
                                         LLM-based dynamic action validation, still suffer from limita-          experience, reduces task efficiency, and thus diminishes over-
                                         tions in usability, security, and performance. To address these         all agent usability. This calls for a more seamless protection
                                         challenges, we propose CSAgent, a system-level, static policy-          mechanism. Inspired by operating systems (OSes), an intu-
                                         based access control framework for computer-use agents. To              itive approach is to enforce policy-based access control to
                                         bridge the gap between static policy and dynamic context and            constrain agent behavior. Drawing from the Contextual In-
                                         user intent, CSAgent introduces intent- and context-aware               tegrity (CI) framework [40, 50, 67] and Mandatory Access
                                         policies, and provides an automated toolchain to assist devel-          Control (MAC) principles [52, 58, 69], we can ensure that
                                         opers in constructing and refining them. CSAgent enforces               security-critical actions are performed only when contextual
                                         these policies through an optimized OS service, ensuring                conditions are satisfied. Recent studies have explored this
                                         that agent actions can only be executed under specific user             approach [4, 7, 27, 55, 60, 73, 77], and some propose dynamic
                                         intents and contexts. CSAgent supports protecting agents                security policy generation, which enhances security while
                                         that control computers through diverse interfaces, including            preserving automation. However, these approaches still suf-
                                         API, CLI, and GUI. We implement and evaluate CSAgent,                   fer from fundamental limitations as they rely on LLM-based
                                         which successfully defends against all attacks in the bench-            dynamic policy generation at agent runtime: unreliable LLMs
                                         marks while introducing only 1.99% performance overhead                 can produce flawed or incomplete rules, and the inference
                                         and 5.42% utility decrease.                                             process incurs significant performance and cost overhead.
                                                                                                                    In this paper, we introduce CSAgent, a secure and effi-
                                                                                                                 cient static policy-based agent access control framework
                                         1   Introduction
                                                                                                                 that addresses these limitations. CSAgent supports CUAs of
                                         Recent advances in large language models (LLMs) have paved              multiple interaction modalities (GUI, API, and CLI-based) by
                                         the way for a new paradigm in human-computer interaction:               uniformly abstracting their operations into functions. Fol-
                                         the computer-use agent (CUA) [51]. These agents are capa-               lowing the principle of CI, CSAgent first defines a formal
                                         ble of autonomously controlling personal computing devices              specification for context-aware access control policies that
                                         via application programming interfaces (APIs) [3, 15, 75],              determines the structure and format for security rules. Each
                                         command-line interfaces (CLIs) [1, 25, 43], or graphical user           policy specifies the contexts (such as user intents and system
                                         interfaces (GUIs) [2, 20, 41, 48, 59, 62, 66], assisting users in       states) under which a function may be safely executed. We
                                         daily tasks. Such agents are already being deployed in diverse          introduce a CSAgent OS service to enforce these policies
                                         domains, including PC, smartphones, and in-vehicle systems.             during agent runtime. Similar to SELinux, system adminis-
                                         By interpreting natural language instructions and orches-               trators and application developers can author access control
                                         trating multi-step workflows across multiple apps, agents               policies based on this specification during the development
                                         significantly enhance user experience and productivity.                 phase. To facilitate this process, we provide an automated
                                            However, these agents significantly expand the attack sur-           policy generation tool that assists developers in creating
                                         face, introducing risks primarily stemming from two factors.            more complete and systematic policies. By shifting policy
                                         First, LLMs are inherently vulnerable to attacks like prompt            construction to the development phase, CSAgent eliminates
                                         injection and jailbreaks [10, 18, 36, 53, 54, 65, 78], and suffer       the runtime overhead of dynamic policy generation while
                                         from unpredictability due to hallucinations [22, 57]. Second,
                                         agents often possess user-level permissions [31, 51, 56, 64,
                                                                                                             1
Preprint                                                                                                                     Gong et al.


providing a more controllable security framework. To make                while requesting the service to extract intents, effectively
this practical, we address three key challenges.                         hiding inference latency. Moreover, the manager categorizes
   First, static policies face difficulties when the security con-       contexts by update frequency to minimize unnecessary data
straints for a function depend on dynamic user intent. For               gathering and uses a cache to reduce context space loading
example, file deletion may require path validation for                   overhead during app switching.
targeted removal but backup verification for cleanup opera-                 We implement a CSAgent prototype and conduct exten-
tions. Moreover, users may explicitly specify constraints (e.g.,         sive evaluation across three benchmarks: AgentBench [35],
amount limits) in their requests, which also determine how               AgentDojo [9], and AndroidWorld [49], which respectively
the rules should be defined. Approaches [27, 55, 60] that gen-           evaluate CLI-based, API-based, and GUI-based agents. Our
erate policies at runtime can easily handle such variations,             experimental results demonstrate that CSAgent achieves
but they require user instructions, which are not observable             a near-perfect defense rate (blocking 100% of attacks with
at development time. To address this, we propose intent-                 policy evolution) while introducing only 1.99% average addi-
aware context space, a per-application hierarchical structure            tional latency and 5.42% utility decrease, significantly out-
that defines and organizes context- and intent-aware policies            performing existing methods. Additionally, our LLM-based
(§4.2). Context space uses function and intent to index poli-            context analyzer identifies 1.93× to 4.12× more GUI elements
cies, improving the expressiveness to cover a wider range                compared to existing approaches during GUI app analysis,
of scenarios. Additionally, we propose an intent prediction              providing a substantially richer semantic knowledge base
method that employs LLMs to predict potential user intents               for automated policy generation.
during the policy generation phase.                                         In summary, our key contributions are:
   Second, automatically generating policies in a controllable
                                                                             1. We analyze the limitations of existing CUA protection
manner for applications across different interaction modali-
                                                                                methods, identify three new challenges, and propose
ties is challenging. We introduce an LLM-based context ana-
                                                                                CSAgent, a system-level, static policy-based access
lyzer that employs systematic reasoning to generate context
                                                                                control framework to secure agent behaviors. By in-
spaces for apps (§4.3). For API and CLI apps, well-defined
                                                                                troducing the intent-aware context space, we enhance
specifications provide sufficient semantic information for
                                                                                the capability and flexibility of static policies.
policy generation. However, GUI apps lack these proper-
                                                                             2. We present the first toolchain that enables automated
ties. Our insight is that event handlers triggered by GUI
                                                                                policy generation across diverse agent interaction modal-
interactions define the actual functions and provide precise
                                                                                ities. By employing stronger models and our policy
semantic information. To extract such information, we use
                                                                                evolution framework, CSAgent enables controllable
LLMs to identify GUI elements and establish associations
                                                                                LLM-based policy generation and refinement.
with their handlers, then employ static analysis to construct
                                                                             3. We implement a CSAgent prototype and integrate it
call graphs of them, thereby building a semantic knowledge
                                                                                with three agent benchmarks, demonstrating excellent
base that enables policy generation. Another problem is that
                                                                                usability and compatibility. We will open-source the
using LLMs for static policy generation still suffers from
                                                                                CSAgent prototype to facilitate broader adoption.
uncertainty issues (e.g., incorrect or missed generation). Ben-
                                                                             4. We conduct a comprehensive evaluation of CSAgent,
efiting from the consistency of static policies, we introduce
                                                                                showing stronger protection and significantly better
a policy evolution framework that helps developers continu-
                                                                                performance, which validates the effectiveness and
ously improve context spaces based on app feature updates
                                                                                flexibility of our approach.
or runtime feedback from agents (§4.5).
   Third, extracting user intents at runtime via LLM and man-
aging context spaces for complex apps create performance bot-            2    Background
tlenecks. During an agent’s runtime, the agent establishes               LLM-based agents are AI systems that use LLMs as their core
a connection with the CSAgent service, the service loads                 reasoning engine to perceive environments, make plans, and
context spaces, and enforces policy validation before func-              take actions to accomplish goals [31, 72]. A key enabler of
tion execution. To retrieve policies, we first use an LLM to             this paradigm is the function calling capability of LLMs,
extract user intents from user requests, which introduces                which allows agents to interface with external systems and
extra overhead. Additionally, context management faces chal-             perform concrete actions through tools [11, 12, 42, 47]. A
lenges from frequent context updates in complex apps with                tool typically refers to a semantic abstraction that encapsu-
extensive context spaces and costly loading overhead when                lates one or more functions. Computer-use agents (CUAs),
switching between multiple context spaces in multi-app sce-              as shown in Figure 1, represent a specialized class of LLM
narios. To address this, we propose an optimized context                 agents designed to control computers like humans. Based on
manager in the service that employs parallel processing and              how they interface with computers, CUAs can be categorized
systematic management (§4.4). When agents receive user                   into three primary approaches: API-based control, CLI-based
requests, they concurrently initiate task-related reasoning              control, and GUI-based control.
                                                                     2
Secure and Efficient Access Control Framework for Computer-Use Agents via Context Space                                            Preprint


            External         Computer-Use         “Help me send            with any GUI app. This greatly enhances the agent’s adapt-
            Data                Agent              [content] via           ability, especially for tasks involving legacy apps that lack
                                   Memory             email to
                                                    [recipient].”          API or CLI support. However, this approach still faces sev-
                                   Planning
                                                User
                                                                           eral limitations. For example, GUI agents often exhibit low
               Tools                LLM         Instruction                task completion rates due to challenges in GUI comprehen-
                                                                           sion and the complexity of multi-step interactions [49, 74].
                               User Device
                                                                           Moreover, they also suffer from poor performance since ev-
              Computer Control            Agent Actions
                                                                           ery action requires LLM inference, resulting in substantial
                                       Write a draft
              GUI
              GUI      API
                       API   CLI
                             CLI                                           latency and degraded user experience [64, 79].
                                       Read private data

                                       Transfer money
                                                                           3     Motivation and Threat Model
                                                                           3.1    Security-usability Trade-offs in CUAs
         Figure 1. Overview of computer-use agent.
                                                                           While CUAs bring convenience to users, they also expand
                                                                           the attack surface of personal devices and introduce security
                                                                           risks. Specifically, due to the inherent uncertainty of LLMs, as
API-based control. One category of tools provides access                   well as their susceptibility to attacks such as prompt injection
to the APIs of systems or applications on user devices [3,                 and jailbreaking, agents may perform unexpected actions
15, 24, 37]. This enables agents to perform high-level ac-                 that deviate from user intentions [31, 51, 64], as shown in
tions like document processing, ticket booking, and route                  Figure 1. Many of these actions are irreversible and can cause
planning. API-based control offers significant advantages                  severe consequences that impact the real world, such as data
in reliability and efficiency. Specifically, well-defined APIs             loss, financial damage, or physical harm.
provide clear interfaces with predictable behavior, enabling                  Although some tools attempt to constrain agents’ capabil-
agents to accomplish complex tasks through systematic tool                 ities through filtering mechanisms and sandboxing [1, 25, 43,
orchestration and deterministic code execution. However,                   45], these approaches cannot fundamentally solve the prob-
this approach is limited by the predefined tools—agents can                lem. Such methods typically either permit or deny specific
only perform actions supported by available APIs. This con-                operations unconditionally, lacking the flexibility to account
straint requires explicit tool development to support new                  for the specific context. This creates an inherent dilemma:
functionalities, limiting the agent’s adaptability to novel user           agents must retain the ability to perform actions to maintain
needs and emerging ecosystems.                                             their functionality, yet many of these actions are inherently
CLI-based control. Another category of tools leverages                     risky. Prohibiting dangerous operations would limit agent
command-line interfaces (CLIs) to enable agents to interact                capabilities, while unrestricted access poses unacceptable se-
with OSes through text commands, providing direct access                   curity risks. This tension between security and functionality
to system functions and utilities [1, 25, 43]. CLI-based con-              is a core challenge in agent design.
trol offers broader functionality compared to API-based ap-                   A straightforward and widely adopted solution is to re-
proaches, as the extensive ecosystem of CLI tools provides                 quest user confirmation before each sensitive action [2, 8, 41].
rich functionality without requiring extra API development.                However, this approach introduces considerable usability
However, this flexibility comes with security risks, as com-               and performance trade-offs. From a usability perspective, fre-
mand injection vulnerabilities can lead to code execution,                 quent confirmation prompts can disrupt the user experience
privilege escalation, and system compromise [34]. To miti-                 and lead to fatigue, causing users to approve actions without
gate these risks, tool providers typically require mechanisms              careful consideration [60]. From a performance standpoint,
like sandboxing and command filtering [1, 25, 43].                         the confirmation process introduces non-negligible latency,
GUI-based control. A third category of tools enables agents                as each task requires multiple rounds of user interaction and
to interact with apps via graphical user interfaces (GUIs)                 LLM inference cycles. This undermines the primary value
[2, 41, 66]. GUI is designed only for human users, requiring               proposition of autonomous agents: their ability to complete
agents to perceive the screen and manipulate UI elements                   tasks efficiently without constant human oversight.
as a human would. This typically involves capturing screen-
shots [20, 48] or extracting a structured GUI tree [59, 66],               3.2    Rule-based Context Validation for CUAs
allowing the agent to understand the current screen, iden-                 Ideally, the execution of a function should be determined
tify actionable elements (such as buttons and input fields),               based on specific contexts rather than applying uncondi-
and reason about which actions to take. Finally, the agent                 tional restrictions, aligning with the principles of Contextual
performs these actions by calling tools that simulate user                 Integrity (CI) [40, 50, 67]. Specifically, in our scenario, con-
interactions, such as clicking or scrolling. GUI-based con-                text refers to the collection of information that characterizes
trol offers broad compatibility, allowing agents to interact               the current execution environment, including user intents,
                                                                       3
Preprint                                                                                                                    Gong et al.


 Table 1. Policy consistency across multiple generations.               framework and user instructions are benign, but the un-
                                                                        derlying LLM may produce untrustworthy outputs when
                   Banking   Slack   Travel   Workspace   GMean         processing untrusted inputs from external sources like web-
        Mean         0.79    0.75     0.68       0.83      0.76         sites or making security-critical decisions. We assume that
         Std         0.13    0.11     0.13       0.12      0.12         the software with which the agent interacts (i.e., the OS and
      Structural     0.94    0.93     0.85       0.94      0.91         legitimate apps) is trustworthy and functions as intended.
      Semantic       0.64    0.56     0.52       0.71      0.60         We trust the agent’s execution framework, tool invocation,
                                                                        and prompt construction operate correctly, and the agent
                                                                        can communicate with our OS service securely. Moreover,
                                                                        context values extracted from these trusted components are
system states, and application-specific parameters. The key             also trusted. Our approach does not address attacks targeting
insight is that the same action may be safe under certain               LLM training processes or model deployment infrastructure,
contextual conditions but dangerous in others. For example,             nor does it cover content safety issues.
file deletion is safe when the user explicitly specifies the
target, but risky without authorization or when targeting
critical files. This motivates validation systems that evaluate         4     CSAgent Design
the appropriateness of agent actions within a given context.            4.1   Design Goals and Overview
Such validation can be performed before (pre-execution) or              CSAgent is a static policy-based access control framework
after (post-execution) each action. While post-execution vali-          that secures computer-use agents while preserving their au-
dation enables more precise anomaly detection by analyzing              tonomy and efficiency. The system assists developers in cre-
outcomes, it cannot prevent irreversible harm. Thus, recent             ating context-aware security policies guided by CI principles
studies focus on pre-execution validation. Early work like              during development. These policies are enforced at runtime
AirGapAgent [4] applied CI principles, using a separate LLM             through lightweight validation, eliminating risky and costly
for data access decisions, but lacked explicit policies, limiting       runtime policy generation and frequent user confirmations.
explainability and auditability. GuardAgent [73] advanced               To achieve effective agent protection while maintaining prac-
this by introducing code generation to convert safety guard             tical deployability, CSAgent targets four design goals:
requests into executable code, offering more structured and                G1: Security. CSAgent must effectively mitigate risks
deterministic validation than direct LLM decisions.                     from unreliable agent behavior while minimizing security
   More recent works have developed policy frameworks that              risks introduced by our own LLM usage.
support conditional rules [21, 27, 55, 60]. However, these ap-             G2: Efficiency. CSAgent should introduce minimal over-
proaches still face the limitation of requiring LLM inference           head to agent execution, preserving task efficiency and user
at agent runtime for policy generation, creating the security           experience. It must avoid frequent runtime LLM calls and
and efficiency challenges we aim to address. Additionally,              maintain responsive behavior.
policies dynamically generated at different times or devices               G3: Automation. CSAgent should achieve high automa-
are likely to vary, hindering policy consistency and prevent-           tion in policy construction and evolution while supporting
ing the unified improvement of policies through iterative               effective human-AI collaboration. The generated policies
refinement. As shown in Table 1, we analyzed the similarity             should be easily reviewable and refinable by developers.
of policies generated by LLMs multiple times for the same                  G4: Compatibility. CSAgent must support diverse agent
function using apps from AgentDojo [9]. We calculate the                interaction modalities (API, CLI, GUI) and work across dif-
policy similarity from both structural and semantic perspec-            ferent agent models. It should provide a modular design for
tives. Even with a temperature of 0, the overall similarity             seamless integration with existing agent systems.
is only around 0.76, highlighting the uncertainty in policy             System overview. As shown in Figure 2, CSAgent uniformly
generation, especially from the semantic perspective.                   abstracts API-, CLI-, and GUI-based agent operations as func-
                                                                        tions to support diverse agent types. This unified abstraction
3.3     Threat Model and Assumptions                                    enables consistent policy enforcement and provides a coher-
We focus on the risks posed by unreliable LLMs within CUAs.             ent framework for security analysis, policy organization, and
Drawing from the OWASP project [44], we target the Exces-               management. The CSAgent workflow operates in two dis-
sive Agency problem, where agents are granted too much                  tinct phases: the development phase and the runtime phase,
autonomy and perform unintended actions, and Sensitive In-              where the former serves as a toolchain for assisted policy
formation Disclosure, such as inadvertent leakage of private            construction and evolution, and the latter works as a stan-
data. These risks can manifest due to various underlying                dalone OS security service for agent runtime protection.
factors, including prompt injection attacks, insecure output               During the development phase, developers can manually
handling, and the inherently uncertain nature of current                write policies or utilize our context analyzer (§4.3) to gen-
LLMs, such as hallucinations. We assume that the agent                  erate policies automatically. We introduce the intent-aware
                                                                    4
Secure and Efficient Access Control Framework for Computer-Use Agents via Context Space                                                                           Preprint


Context Analyzer    CSAgent Service                   Intent                                      domain. By tailoring policies to the specific security charac-
      (§4.3)                                            A              Context Policy
                      Intent Extractor       Func
          LLM                                 A       Intent
                                                                                                  teristics of each application and maintaining clear boundaries
                                                        B         Ctx Rule 0 ... Ctx Rule N
                        Feedback             Func                                                 between them, this approach provides more granular and
 Function                                     ...                           ...
 Description                                          Intent
                      Context Manager                   ...         Context Space (§4.2)          systematic management, while avoiding the bloat of a single,
        GUI                   (§4.4)
      Analyzer                                   Retrieval
         Static          Policy Verifier                          C0   C1 Ctx Vector Cn           large context space. Additionally, the context space defines
        Analysis                                    Update
                                                                                                  the policy format for CSAgent, offering a formal specification
                                       RPC                     Context Values
          LLM
                                                                                                  for developers or LLM-based tools to write policies.
                     Policy        Agent Framework                                                Challenges in static policy. The intent-aware design of
                    Evolution                                             Function Call
  Source Code      Framework             User instruction
  / Documents        (§4.5)
                                                                                                  the context space aims to address a fundamental challenge in
                                        LLM Agent                      GUI / API / CLI.           static policy: the same function may require different secu-
                                                                          User Device             rity policies depending on the user’s intent, as the examples
                                                                                                  in Figure 3. Unlike dynamic policy generation approaches
                   Figure 2. CSAgent architecture.                                                that can adapt to specific user instructions at runtime, static
                                                                                                  policies must anticipate and accommodate these intent vari-
                                                                                                  ations during development. Our intent-aware structure ad-
                                                                                                  dresses this limitation by organizing policies according to
context space (§4.2), a per-application hierarchical structure,                                   predicted user intents, enabling static policies to achieve
to organize all contextual policies for an application. This                                      flexibility comparable to dynamic approaches.
structure also defines CSAgent’s policy format, enabling de-                                      Our solution. A context space organizes policies in a hier-
velopers to understand, write, and audit policies. When using                                     archical structure with the indexing pattern: (class) →
our analyzer, it generates policies by systematically reason-                                     function → intent → policy, where the class level is
ing through the documentation or code of each function                                            optional and used only for large-scale apps with well-defined
in the app. This static policy approach enables the use of                                        classes, such as GUI apps with distinct UI widget classes. To
more powerful reasoning models to generate higher-quality                                         precisely characterize this structure, we formally define the
policies and iterative refinement to improve them continu-                                        context space and its constituent elements as follows. A con-
ously (§4.5), making policy generation more controllable. In                                      text space 𝐶𝑆 for application 𝐴 is defined as:
contrast, performing such optimizations at runtime would                                                           (
incur significant performance overhead.                                                                              {𝐶 1, 𝐶 2, . . . , 𝐶𝑛 } if |𝐶𝑙𝑎𝑠𝑠𝑒𝑠𝐴 | > 0
                                                                                                            𝐶𝑆𝐴 =                                               (1)
   During the runtime phase, the agent framework estab-                                                              {𝐹 1, 𝐹 2, . . . , 𝐹𝑚 } if |𝐶𝑙𝑎𝑠𝑠𝑒𝑠𝐴 | = 0
lishes a remote procedure call (RPC) connection with the
                                                                                                  where each 𝐶𝑖 represents a class containing multiple func-
CSAgent service. When the agent accesses a new applica-
                                                                                                  tions, and each 𝐹 𝑗 represents a function that agents can exe-
tion, it registers the corresponding context space with the
                                                                                                  cute within the app, such as performing a control or changing
service, which then loads the context space. Our optimized
                                                                                                  a setting. For API/CLI agents, a function corresponds to a tool
manager extracts contexts efficiently from user devices and
                                                                                                  function or CLI command. For GUI agents, it corresponds
instructions using parallel processing, updating context val-
                                                                                                  to an interaction with a GUI element. A function entry 𝐹
ues based on freshness to minimize unnecessary extractions.
                                                                                                  describes such a function and is defined as a tuple:
Before each function execution, the agent requests policy
validation from the service via RPC. A function can only                                                               𝐹 = ⟨𝑑𝑒𝑠𝑐, 𝑠𝑒𝑐_𝑙𝑒𝑣𝑒𝑙, 𝐼, 𝑃⟩                     (2)
execute when all its dependent contexts satisfy the speci-                                        where 𝑑𝑒𝑠𝑐 is the natural language description of the func-
fied rules in the corresponding policy. If validation fails, the                                  tion’s purpose and behavior, providing human-readable doc-
system provides two fallback mechanisms to maintain task                                          umentation for policy developers and maintainers. 𝑠𝑒𝑐_𝑙𝑒𝑣𝑒𝑙 ∈
efficiency: it can either prompt the user for a decision or                                       {𝑛𝑜𝑟𝑚𝑎𝑙, 𝑐𝑜𝑛𝑑𝑖𝑡𝑖𝑜𝑛𝑎𝑙, 𝑑𝑎𝑛𝑔𝑒𝑟𝑜𝑢𝑠} categorizes functions based
offer contextual guidance to the agent, allowing continued                                        on their risk potential: normal functions are completely
execution with security guarantees.                                                               harmless (e.g., reading system time); conditional functions
                                                                                                  are safe under specific conditions but may cause harm if ex-
4.2     Intent-aware Context Space                                                                ecuted inappropriately (e.g., sending an email); dangerous
CSAgent introduces the concept of intent-aware context space,                                     functions require special handling like mandatory user con-
a structured data abstraction used to maintain access control                                     firmation (e.g., resetting the system). 𝐼 = {𝑖 1, . . . , 𝑖𝑘 , 𝑓 𝑎𝑙𝑙𝑏𝑎𝑐𝑘 }
policies for securing agent actions across different user in-                                     is the set of possible user intents, where each intent captures
tents and contexts. Each context space is application-specific,                                   the underlying motivation behind user requests rather than
accompanying the development and deployment of an ap-                                             surface-level commands, and 𝑓 𝑎𝑙𝑙𝑏𝑎𝑐𝑘 serves as a default
plication, such as a GUI app or tool. This design follows a                                       when no specific intent matches. Intents also serve as implicit
principle similar to OSes’ per-process address spaces, where                                      constraints: functions can only be executed when the user’s
each application operates within its own isolated security                                        request corresponds to a defined intent. 𝑃 : 𝐼 → 𝑃𝑜𝑙𝑖𝑐𝑦 maps
                                                                                              5
Preprint                                                                                                                                                                 Gong et al.


  Function: send_email                                      Function: delete_file                                               Function: control_door_lock

  Possible User Intents:                                    Possible User Intents:                                              Possible User Intents:
  • compose_send: compose and send a new email              • cleanup_temp: clean up temporary or cache files                   • remote_unlock: unlock door remotely
  • send_draft: send a previously composed draft            • remove_specific: delete a specific file they explicitly           • auto_lock/unlock: automatic unlock based on
  • auto_reply: automatically reply to an incoming email      mentioned                                                           arrival or departure
                                                            • batch_organize: organize files by removing dupli-                 • scheduled_access: sets up time-based access for
  Intent-Specific Policy: compose_send                        cates or outdated versions                                          regular visitors
  • Recipients must be explicitly provided
  • Email content must be finalized                         Intent-Specific Policy: cleanup_temp                                Intent-Specific Policy: remote_unlock
                                                            • File must be in designated temporary directories                  • User identity must be verified
  Intent-Specific Policy: send_draft                        • File must be sufficiently old
  • Recipients must be explicitly provided                                                                                      Intent-Specific Policy: auto_lock/unlock
  • A valid draft must be selected                                                                                              • User must be moving toward/away from the door
                                                            Intent-Specific Policy: remove_specific
                                                            • File must be explicitly mentioned in user request                 • All security systems must be operational
  Intent-Specific Policy: auto_reply                        • File is not system-critical
  • Original email must warrant an automatic reply (e.g.,
     not in the spam list)                                                                                                      Intent-Specific Policy: scheduled_access
  • Auto-generated content must not contain sensitive       Intent-Specific Policy: batch_organize                              • Scheduled access must be time-bounded
     information                                            • Files must be verified duplicates or outdated                     • Access must match pre-defined schedule
  • Should align with expected response times               • Recent backup must exist before mass operations                   • Expected visitor must be detected at the door


           (a) Example: send an email                                (b) Example: delete a file                                      (c) Example: control door lock

Figure 3. Examples of intent-aware policies showing context constraints for the same function under different user intents.

intents to the related policies, enabling fine-grained access                               current state is represented by a context vector 𝐶𝑉 :
control based on user purpose. A context policy 𝑝𝑜𝑙𝑖𝑐𝑦𝑖 for                                                             𝐶𝑉 = {𝑐𝑡𝑥 1, 𝑐𝑡𝑥 2, . . . , 𝑐𝑡𝑥𝑛 }                          (5)
intent 𝑖 is defined as:
                                                                                            where 𝑐𝑡𝑥 =< 𝑐𝑡𝑥_𝑖𝑑, 𝑣𝑎𝑙, 𝑚𝑒𝑡𝑎𝑑𝑎𝑡𝑎 > stores the informa-
                  𝑝𝑜𝑙𝑖𝑐𝑦𝑖 = {𝑟𝑢𝑙𝑒 1, 𝑟𝑢𝑙𝑒 2, . . . , 𝑟𝑢𝑙𝑒𝑛 },                  (3)          tion of a context. 𝑐𝑡𝑥_𝑖𝑑 is the context’s identifier, and 𝑣𝑎𝑙
                                                                                            is the current context value. For context acquisition and
where each 𝑟𝑢𝑙𝑒 𝑗 corresponds to a specific context and spec-
                                                                                            management, each context is associated with 𝑚𝑒𝑡𝑎𝑑𝑎𝑡𝑎 that
ifies the constraint that this context must satisfy for safe
                                                                                            specifies: 𝑡𝑦𝑝𝑒 - the data type of the context value (e.g., string,
function execution under the given intent. Specifically, a
                                                                                            boolean, integer, float). 𝑠𝑟𝑐 ∈ {𝑢𝑠𝑒𝑟 _𝑟𝑒𝑞𝑢𝑒𝑠𝑡, 𝑠𝑦𝑠𝑡𝑒𝑚_𝑎𝑝𝑖,
context rule 𝑟𝑢𝑙𝑒 is defined as a tuple:
                                                                                            𝑠𝑦𝑠𝑡𝑒𝑚_𝑐𝑙𝑖, 𝑓 𝑢𝑛𝑐_𝑝𝑎𝑟𝑎𝑚𝑠, 𝑎𝑔𝑒𝑛𝑡_ℎ𝑖𝑠𝑡𝑜𝑟𝑦} - where the con-
                𝑟𝑢𝑙𝑒 = ⟨𝑐𝑡𝑥_𝑖𝑑, 𝑐𝑜𝑛𝑠𝑡𝑟𝑎𝑖𝑛𝑡, 𝑔𝑢𝑖𝑑𝑎𝑛𝑐𝑒⟩                          (4)          text value can be acquired at runtime. 𝑡𝑒𝑚𝑝𝑟 - the update
                                                                                            frequency of the context value (see §4.4 for details).
where 𝑐𝑡𝑥_𝑖𝑑 is the unique identifier of the context. 𝑐𝑜𝑛𝑠𝑡𝑟𝑎𝑖𝑛𝑡                               For a function 𝐹 performed under intent 𝑖, the security
is a logical expression that must evaluate to true against the                              validation succeeds if and only if all context rules in the
corresponding context value for safe execution. Constraints                                 corresponding policy are satisfied:
are constructed using atomic predicates combined with logi-
cal connectives (e.g., ∧, ∨, ¬). An atomic predicate typically                                   ∀𝑟𝑢𝑙𝑒 ∈ 𝑃 (𝑖) : 𝑣𝑎𝑙𝑖𝑑𝑎𝑡𝑒 (𝑟𝑢𝑙𝑒.𝑐𝑜𝑛𝑠𝑡𝑟𝑎𝑖𝑛𝑡, 𝐶𝑉 ) = 𝑡𝑟𝑢𝑒                             (6)
takes the form val1 operator val2, where val1 refers to                                     where 𝑣𝑎𝑙𝑖𝑑𝑎𝑡𝑒 (𝑟𝑢𝑙𝑒.𝑐𝑜𝑛𝑠𝑡𝑟𝑎𝑖𝑛𝑡, 𝐶𝑉 ) returns true if the con-
the current context value, and val2 represents a reference                                  straint condition is satisfied by the corresponding context
target. Crucially, val2 supports flexible assignment: it can                                value in the current context vector 𝐶𝑉 . This validation logic
be a pre-defined constant, a user-specified configuration,                                  enforces a default-deny security model: any sensitive func-
or a dynamic value derived from another context, ensuring                                   tion execution is blocked unless explicitly authorized by a
that security policies adapt to individual usage patterns. The                              matching policy and satisfied context constraints. While the
operator includes relational symbols (e.g., =, <, ≠) and set                                policy enforces the conjunction (AND) of rules, disjunctive
operations (e.g., ∈, ⊂). This flexible definition allows poli-                              scenarios (OR) are supported through flexible constraints or
cies to express complex logic, such as ensuring a user role                                 distinct user intents for mutually exclusive contexts. This de-
belongs to a permitted set (𝑟𝑜𝑙𝑒 ∈ {𝑎𝑑𝑚𝑖𝑛, 𝑜𝑤𝑛𝑒𝑟 }) or val-                                 sign flattens complex branching into linear paths, ensuring
idating value ranges (10 < 𝑎𝑚𝑜𝑢𝑛𝑡 < 500). 𝑔𝑢𝑖𝑑𝑎𝑛𝑐𝑒 pro-                                     security (via default-deny) without sacrificing expressive-
vides human-readable hints when constraint validation fails,                                ness.
helping users understand why the function was blocked. To
centrally manage all contexts within a context space and                                    4.3      LLM-based Context Analyzer
facilitate policy validation at runtime, we introduce the con-                              To assist developers in constructing intent-aware context
cept of context vector. The vector serves as a unified data                                 spaces for diverse applications, we introduce an LLM-based
structure that maintains the current runtime values of all                                  context analyzer that leverages the semantic comprehension
relevant contexts defined in the policies. At runtime, the                                  capabilities of LLMs to generate security policies. Concretely,
                                                                                      6
Secure and Efficient Access Control Framework for Computer-Use Agents via Context Space                                                                                         Preprint

                                                                                                                                                API/CLI Doc
as shown in Figure 4 (blue arrows), our approach utilizes in-                                        App
                                                                                                                   LLM Context Window           Update Info     1. Statistics

context learning by providing the LLM with carefully crafted                                         Source      CSAgent methodology                            2. Deduplication
                                                                                                     Code
                                                                                                                 Example context policies                       3. Analysis
prompts that include method descriptions, exemplary poli-                                                        Context space data structure                   Developer
cies, and explicit data structure definitions for context spaces.                  ➀          LLM
                                                                                                                                                                         ➁           LLM
                                                                                                                 Function descriptions

Through a structured reasoning process, the analyzer guides                       GUI Event Handlers                      ➂                     ➂ Suggestions       Policy Evolution
                                                                             GUI ID0 => onClick(...) {...}          Security level?                                   Framework
the LLM to generate context spaces progressively in mul-                     GUI ID1 => onLongClick(...) {...}      Possible user intents?
                                                                                                                                                Context
                                                                                                                                                                              User
                                                                                                                                                Space
tiple stages. First, it analyzes each function’s purpose and                 GUI ID2 => onKey(...) {...}
                                                                                                                    Dependent contexts?
                                                                             GUI ID3 => onXXX(...) {...}
assesses its security risk level. For functions classified as                               ...
                                                                                                                    Contexts’ metadata?
                                                                                                                                                                          ➀      Agent

conditional, the analyzer generates corresponding poli-                         Call Graph     Analysis ➁           Security constraints?

                                                                                                                                                                   CSAgent Service
                                                                             Code Knowledge Base
cies through a two-step process: it begins with intent predic-                                                                  LLM



tion based on function semantics to identify possible user
intents that may trigger the function or affect how this func-                               Figure 4. Policy generation and evolution.
tion works (e.g., intents on parameters), followed by policy
analysis for each intent. During policy analysis, the system
identifies dependent contexts, specifies constraints for each,
and generates the necessary context metadata. Upon com-
pletion, the context space is stored in a file, which can then
be deployed with the application to the device and used by                 through GUI event handlers. These handlers precisely rep-
CSAgent for runtime policy enforcement.                                    resent the functions that agents can trigger through GUI
Challenges in GUI analysis. For API- and CLI-based apps,                   interactions. Therefore, our approach centers on identifying
policy generation is straightforward due to the availability of            GUI event handlers within an app and constructing their call
well-defined function specifications. Specifically, API tools              graphs to build a granular and thorough knowledge base of
usually provide detailed documentation on purpose, parame-                 app functionality for subsequent policy generation.
ters, and behavior [26, 47], while CLIs usually offer manuals                 The first challenge lies in systematically identifying GUI
specifying command functionality and usage [23, 38], which                 event handlers, as they may not follow standardized nam-
enables LLMs to generate high-quality context spaces with                  ing conventions across different apps. For instance, while
sufficient semantic information on function behavior. How-                 Android apps may use standard callbacks like onClick, de-
ever, GUI agents present greater challenges. Concretely, GUI               velopers sometimes implement custom handler methods
agents interact with apps through generic interaction prim-                with varied naming schemes that are subsequently assigned
itives (such as screen capture, clicking, scrolling, and text              to these callbacks. To address this variability, we leverage
input) rather than explicit functional interfaces. Even worse,             the semantic understanding capabilities of LLMs to identify
GUI apps typically lack functional documentation. While                    GUI-related code segments. We prompt the LLM to analyze
human users understand app usage through interaction, this                 source code files and identify GUI event handlers and extract
knowledge is rarely formalized in machine-readable specifi-                their code, regardless of their specific naming patterns or
cations, making it difficult to identify the security-sensitive            implementation approaches. Additionally, the LLM extracts
functions that require protection. As a result, no existing                the corresponding GUI element identifiers (such as Android
agent protection approach has demonstrated automated end-                  view classes and resource IDs) associated with each handler.
to-end policy generation for GUI apps. Existing approaches                 These identifiers enable our runtime validation system to
for GUI functionality discovery include static program anal-               map agent GUI actions, which typically involve coordinate-
ysis and GUI exploration tools. However, our experiments                   based clicks rather than direct function calls, to the specific
(§7.2) reveal limitations in both approaches: static analysis              functions and their security policies (§5).
often fails to capture the complete scope of GUI functional-                  Once event handlers are identified, we employ static analy-
ities due to dynamic binding and complex UI frameworks,                    sis techniques to construct call graphs for them, mapping the
while GUI exploration tools suffer from scalability issues                 complete execution flow triggered by user interactions. This
and frequently encounter infinite loops or state explosion                 process is well-supported for source code analysis, where
problems that prevent comprehensive coverage.                              mature tools can accurately trace function invocations and
Our solution. To address the challenge, we propose a hybrid                data dependencies to provide comprehensive coverage of
approach that combines LLM-based code comprehension                        handler functionality. The combination of identified handlers
with static analysis. Our key insight is that in the absence of            and their call graphs provides a source-code-level knowledge
explicit documentation, source code represents the most au-                base that captures the complete functional semantics of the
thoritative and comprehensive description of app functionality.            application. This knowledge base can then be processed by
GUI apps typically follow an event-driven programming par-                 our context analyzer using the same reasoning approach
adigm where all user-facing functionalities are implemented                applied to API and CLI tools, enabling the generation of
                                                                           high-quality context spaces for GUI apps.
                                                                       7
Preprint                                                                                                                                                     Gong et al.


                                          User Instruction               Cold/Warm/Hot Ctx             Our solution. Figure 5 shows how we address these chal-
                                                                                                       lenges by adopting thorough optimizations through parallel
            Intent Extractor                                              Agent                        processing and systematic context management. To mitigate
           LLM        Intent selecting ...                         LLM         Task planning ...       LLM inference overhead, we employ a concurrent approach
                                                                                                       for extracting user intents and related contexts from user
   { Intent | Ctx}               { Full Intent Set }
                                                                                                       instructions. When users send requests, the instruction is
      Policies                                         Suspended                 User Device           simultaneously dispatched to both the agent and a dedicated
                                                 Ctx Space                           App #0            LLM-based intent extractor in the CSAgent service. To im-
                     ...                  Switch     #1              LRU             Context           prove accuracy and efficiency, we employ a coarse-to-fine
                           ...                            ...                        Space
                                                                                      File
                                                                                                       retrieval strategy before invoking the LLM. Specifically, the
           Context Vector
                                                       Ctx Space         Ctx                           manager first uses cosine similarity to efficiently filter rele-
      Active Ctx Space #0                                 #M
                                                                                     App #1            vant intent candidates from the context space based on the
                 Context Space Cache                                                   ...             user instruction. These filtered candidates, along with param-
                      Context Manager                                               App #N             eter contexts, are then passed to the extractor. The extractor
                                                                                                       analyzes the user instruction to identify the valid intent and
Figure 5. Optimized context manager that employs parallel                                              extract contexts that correspond to the current request. For
processing and systematic context management.                                                          function intents, we also prompt the LLM to infer reasonable
                                                                                                       execution sequences to prevent out-of-sequence errors. To
                                                                                                       address potential ambiguities where the LLM identifies mul-
4.4    Optimized Context Manager                                                                       tiple intents for a single function, we select the intent with
The context manager serves as the core component of the                                                the highest similarity score to ensure precise policy retrieval.
CSAgent service, responsible for managing context spaces,                                              When the agent determines the next function, we use this
maintaining context vectors, and enforcing security policies.                                          finalized intent to retrieve the policy.
When an agent first interacts with an app, the context man-                                               To address the computational overhead from extensive
ager loads the app’s context space file, and establishes the                                           context updates, we categorize contexts into three tempera-
corresponding context vector. The manager then continu-                                                ture levels based on their update frequency: cold, warm, and
ously updates context values in the vector based on their                                              hot. Cold contexts represent the least frequently updated
metadata specifications, extracting data from user instruc-                                            data, like system settings that remain stable over long peri-
tions, device systems, and agent frameworks. When the agent                                            ods, which are updated only during context space loading
determines the function to execute, the embedded policy ver-                                           or switching. Warm contexts represent moderately updated
ifier retrieves the corresponding policy from the context                                              data, such as user instruction-related contexts, which are
space and validates it against the current context values in                                           updated when users send new instructions. Hot contexts
the vector. CSAgent leverages LLMs to extract user intents                                             represent frequently changing data, such as sensor informa-
and related contexts from user instructions. Specifically, we                                          tion, precise timestamps, agent action history, and function
need to identify two types of user intent information: func-                                           parameters that the agent determined, which are updated be-
tion intent that is used for policy retrieval, and parameter                                           fore each policy validation. These temperature classifications
contexts that provide specific context values required by rules                                        are automatically determined by the context analyzer during
(e.g., recipient for message sending).                                                                 the development phase based on each context’s attributes.
Challenges in performance. The context manager faces                                                      To support multi-application scenarios and reduce fre-
two primary performance challenges. First, LLM-based con-                                              quent context space loading overhead during application
text extraction from user instructions introduces additional                                           switching, CSAgent’s context manager introduces a caching
inference latency. One simple approach is to request the LLM                                           mechanism that stores recently used context spaces. When-
to analyze the relevant intent and extract context values after                                        ever a new context space is loaded, it is inserted into the
the agent determines the function to perform, which would                                              cache. When the cache reaches its capacity, the system em-
introduce inference latency for every agent action, severely                                           ploys a Least Recently Used (LRU) replacement policy to
degrading performance [27, 55]. Second, context management                                             manage space allocation efficiently. For any given agent,
for complex apps creates substantial computational overhead.                                           only one context space remains active at a time, as the agent
Large-scale apps, particularly GUI apps, often have exten-                                             can interact with only one application at once. Other con-
sive context spaces involving numerous contexts. Frequent                                              text spaces are suspended and awaiting activation. When
acquisition and updates of all context values incur unneces-                                           the application switches, the active context space is updated
sary computational costs, increased resource consumption,                                              accordingly. If the target context space is already present in
and additional energy drain. Moreover, loading these con-                                              the cache, no loading overhead is incurred.
text spaces is time-consuming, especially when switching
between multiple apps, resulting in a poor user experience.
                                                                                                   8
Secure and Efficient Access Control Framework for Computer-Use Agents via Context Space                                              Preprint


4.5   Policy Evolution Framework                                           reporting mechanisms, with similar user privacy controls
Challenges in policy reliability. We acknowledge that                      allowing opt-out from logging and data collection. To com-
LLMs’ uncertainty makes it difficult to guarantee policy cor-              plement offline refinement, we support online parameter
rectness and completeness. CSAgent relies on LLMs to gen-                  adaptation for user-customizable values. These parameters
erate context space (intents, contexts and policies), analyze              (e.g., threshold or recipient whitelists) are initialized with
GUI event handlers, and select intent during policy retrieval.             strict defaults (e.g., empty sets) to ensure safety. When a legit-
Inaccuracies and omissions in their content can compromise                 imate action is blocked due to these conservative constraints,
access control effectiveness. Since writing completely correct             the system prompts the user for verification. Upon approval,
and comprehensive policies is impractical (akin to bug-free                the specific context value is dynamically incorporated into
software), the only viable mitigation is continuous policy re-             the trusted set, relaxing the policy for future execution.
finement. Manual policy review is labor-intensive, requiring               Scalable policy testing foundation. PEF’s design also pro-
domain experts with deep knowledge of both app features                    vides infrastructure for large-scale policy validation. For
and security.                                                              instance, we can use LLMs to generate diverse task scenarios
Our solution. We treat policy engineering as analogous                     and agent action sequences to fuzz context spaces and detect
to software engineering: initial LLM-generated policies are                anomalies, analyzing policy completeness and accuracy for
"beta code" that must undergo rigorous testing and iterative               further refinement. Systematic policy testing is an important
refinement. Static policy offers a key advantage of consis-                direction for our future work.
tency across deployments: all users operate under identical
policies, enabling centralized quality assurance. Building
                                                                           5     Implementation
on this, we propose the Policy Evolution Framework (PEF),
a comprehensive toolchain that ensures policy reliability                  We implement CSAgent in Python as a two-component sys-
through generation-time validation, app update synchro-                    tem: a toolchain for context space generation and evolu-
nization, and runtime feedback-based evolution, as shown                   tion, and an OS service for agent runtime protection. The
in Figure 4 (orange arrows). When a new context space is                   toolchain includes the context analyzer and policy evolution
generated, PEF performs initial validation: it verifies the for-           framework, while the service consists of the context manager
mat correctness, then checks function coverage for API/CLI                 and policy verification logic, offering a lightweight interface
apps or validates the existence and consistency of UI element              that integrates easily with existing agent frameworks with
classes, identifiers, and event handlers. When an app under-               minimal modification. Context spaces are stored in JSON
goes feature changes, developers provide update information                format for ease of review and evolution.
(e.g., patches or changelogs) to PEF, which automatically up-              Automatic policy generation and evolution. As outlined
dates the context space. For new functions, PEF uses the                   in §4.3, we use LLMs (DeepSeek-R1 [19]) for policy gen-
context analyzer to generate fresh policies. For modified or               eration and refinement. For API and CLI agents, the LLM
removed functions, PEF locates the corresponding policies                  analyzes function documentation to generate policies. For
and either regenerates or removes them accordingly.                        GUI agents, we target Android apps since Android is widely
    For runtime feedback analysis, the CSAgent service logs                used and open-source. For a given app’s source code, our
the full execution trace: user request, extracted intent, con-             context analyzer first uses text matching to identify files
text evaluation process, and validation result. Policy anom-               related to GUI operations, then provides these files to the
alies are identified through two mechanisms. During policy                 LLM for analysis of event handlers. The LLM outputs results
retrieval, the service logs cases where target functions or                in JSON format, including GUI element details like class
intents cannot be located, capturing user instructions and                 and resource ID, and methods invoked by the corresponding
missing elements. During policy validation, when validation                handlers. We then use static analysis tools (CodeQL [13]) to
fails, the system requests user confirmation before blocking;              construct call graphs. For policy evolution, we implement a
if users indicate the function should proceed, this suggests               runtime logging system that captures task information, vali-
potential policy deficiencies. Conversely, when validation                 dation events, user feedback, and execution traces. During
succeeds but users believe the function should be blocked,                 refinement, the LLM analyzes the logs alongside the existing
they can actively report anomalies. The CSAgent service                    context space and update history to identify potential utility
filters anomalous logs during idle periods and uploads them                and security issues, then systematically updates policies to
to PEF for analysis. PEF then identifies the root cause by                 address these deficiencies.
prompting the LLM with the runtime error log, the target                   Policy retrieval. Upon receiving a request, we first retrieve
function’s specification or code, and the failed policy, subse-            a set of relevant (Function,Intent) candidates from the
quently generating improvement suggestions for developers,                 context space using cosine similarity. Next, we feed the re-
who can directly adopt these suggestions or manually in-                   quest, these candidates, and policy-defined contexts to the
tervene as needed. This approach mirrors existing OS crash                 intent extractor LLM, which then identifies the valid intent
                                                                           and extracts specific context values, returning them in a list.
                                                                       9
Preprint                                                                                                                           Gong et al.


        Table 2. Notation for Formal Security Analysis                  A system state at time 𝑡 is 𝑠𝑡 = ⟨𝑐𝑣𝑡 , 𝑒𝑛𝑣𝑡 ⟩ where 𝑐𝑣𝑡 is the
                                                                      current context vector and 𝑒𝑛𝑣𝑡 ∈ E.
Symbol      Definition                                                Agent Behavior Model. An agent A maps user instructions
                                                                      and environmental states to function executions:
    F       Set of all functions that agents can execute
    C       Set of all possible contexts                                                        A : U × E → F∗                            (7)
    U       Set of all possible user instructions
                                                                        Due to LLM unreliability, we model agent decisions as
    E       Set of environmental states that agents have access
                                                                      potentially erroneous:
            (e.g., system status, sensor data, external data)
 F𝑛𝑜𝑟𝑚      Functions that are always safe to execute                         A𝑢𝑛𝑟𝑒𝑙 (𝑢, 𝑒𝑛𝑣) = A𝑖𝑑𝑒𝑎𝑙 (𝑢, 𝑒𝑛𝑣) ⊕ A𝑒𝑟𝑟𝑜𝑟 (𝑢, 𝑒𝑛𝑣)         (8)
 F𝑐𝑜𝑛𝑑      Functions that are safe under specific contexts
 F𝑑𝑛𝑔𝑟𝑠     Functions that require explicit user authorization        where ⊕ denotes probabilistic combination of ideal and erro-
   A        Agent behavior model                                      neous behaviors and 𝑢 ∈ U.
 A𝑖𝑑𝑒𝑎𝑙     Intended agent behavior                                   Safety Classification. We partition functions by security
 A𝑒𝑟𝑟𝑜𝑟     Erroneous agent behavior due to LLM defects               risk:
 A𝑢𝑛𝑟𝑒𝑙     Combination of ideal and erroneous behaviors                             F = F𝑛𝑜𝑟𝑚 ∪ F𝑐𝑜𝑛𝑑 ∪ F𝑑𝑛𝑔𝑟𝑠                (9)
 𝑃 𝑓 (𝑖)    Policy for function 𝑓 under intent 𝑖
  𝑟𝑢𝑙𝑒      A context rule within a policy                            6.2     Security Properties
                                                                      Property 1 (Context-Dependent Safety). For any function
                                                                      𝑓 ∈ F𝑐𝑜𝑛𝑑 executed under user intent 𝑖:
Subsequently, before each agent action, the CSAgent service
retrieves the corresponding policy via function and intent              Safe(𝑓 , 𝑖, 𝑐𝑣𝑡 ) ⇐⇒
indexing. For API/CLI agents, the mapping is direct, with               ∀𝑟𝑢𝑙𝑒 ∈ 𝑃 𝑓 (𝑖) : validate(𝑟𝑢𝑙𝑒.𝑐𝑜𝑛𝑠𝑡𝑟𝑎𝑖𝑛𝑡, 𝑐𝑣𝑡 ) = true (10)
each tool call or CLI command corresponding to a function
                                                                      Property 2 (Policy Completeness). Every security-sensitive
entry. GUI agents present a more complex scenario, as their
                                                                      function has a corresponding policy that captures all neces-
actions consist of GUI controls rather than function calls.
                                                                      sary safety conditions:
To address this, CSAgent captures the screen’s GUI tree and
uses the agent’s target coordinates to identify the intended            ∀𝑓 ∈ F𝑐𝑜𝑛𝑑 : ∃𝑃 𝑓 such that Safe(𝑓 , 𝑖, 𝑐𝑣𝑡 ) ≡
GUI element, extracting its package, class, and resource ID
                                                                                                              PolicySat(𝑃 𝑓 (𝑖), 𝑐𝑣𝑡 )   (11)
attributes to map to the corresponding function.
Context acquisition and policy validation. Context val-               Property 3 (Unauthorized Prevention). No conditional
ues come from user instructions, systems, and agent oper-             or dangerous function executes without satisfying security
ations. During intent selection, the intent extractor LLM             requirements:
parses user requests and environmental data (e.g., configura-
tions) to obtain contexts. Agent-related contexts are captured          ∀𝑓 ∈ F𝑐𝑜𝑛𝑑 ∪ F𝑑𝑛𝑔𝑟𝑠 : Execute(𝑓 ) ⇒ Authorized(𝑓 ) (12)
in two ways: parameter contexts are obtained when inter-
                                                                      6.3     Main Security Theorems
cepting agent actions, while history contexts are updated
after action completion. For system state contexts, values            Theorem 1 (Safety Preservation). CSAgent ensures no
are acquired through CLI (e.g., shell or ADB [16]) or APIs            unsafe operations are executed:
accessible to the agent. Another approach is implementing                    ∀𝑡, 𝑓 : Execute(𝑓 , 𝑡) ⇒ Safe(𝑓 , intent(𝑢𝑡 ), 𝑐𝑣𝑡 )        (13)
dedicated system services to provide unified interfaces for
context acquisition, which requires platform vendor partici-          Proof. We prove by contradiction. Assume ∃𝑡, 𝑓 such that
pation in the ecosystem.                                              Execute(𝑓 , 𝑡) = true but Safe(𝑓 , intent(𝑢𝑡 ), 𝑐𝑣𝑡 ) = false.
                                                                         For execution to occur, 𝑓 must pass CSAgent’s valida-
6     Security Analysis                                               tion. If 𝑓 ∈ F𝑛𝑜𝑟𝑚 , then Safe(𝑓 , intent(𝑢𝑡 ), 𝑐𝑣𝑡 ) = true by
In this section, we provide a formal security analysis of             definition. If 𝑓 ∈ F𝑑𝑛𝑔𝑟𝑠 , then explicit user authorization
CSAgent to demonstrate its effectiveness in protecting CUAs           is required, which implies safety. If 𝑓 ∈ F𝑐𝑜𝑛𝑑 , then execu-
from executing unintended and unsafe actions. We estab-               tion requires both intent matching and policy satisfaction,
lish formal models for the system behavior and prove key              which by Property 1 implies safety. All these cases lead to
security properties.                                                  contradictions, thus proving the assumption is false.          □

6.1     Formal Model                                                  Theorem 2 (Utility Preservation). CSAgent does not pre-
                                                                      vent legitimate operations:
System Model. We model the system as a tuple S = ⟨F , C,
U, E⟩ where the notation is defined in Table 2.                             ∀𝑓 , 𝑖, 𝑐𝑣𝑡 : Safe(𝑓 , 𝑖, 𝑐𝑣𝑡 ) ⇒ CanExecute(𝑓 , 𝑖, 𝑐𝑣𝑡 )    (14)
                                                                 10
Secure and Efficient Access Control Framework for Computer-Use Agents via Context Space                                           Preprint


Proof. For any safe operation: if 𝑓 ∈ F𝑛𝑜𝑟𝑚 , CSAgent always                Policy reliability. The security improvement provided by
permits execution. If 𝑓 ∈ F𝑐𝑜𝑛𝑑 and Safe(𝑓 , 𝑖, 𝑐𝑣𝑡 ) = true,               CSAgent largely depends on the correctness and complete-
then by Property 1, all constraints are satisfied and policy                ness of the policies. While generating fully correct and com-
validation succeeds.                                       □                plete policies is unrealistic, CSAgent mitigates this issue
                                                                            by leveraging more powerful reasoning models to generate
6.4   Threat Analysis                                                       higher-quality policies and iteratively improve them through
We analyze potential threats to CSAgent’s security guaran-                  the PEF. Additionally, we have fallback mechanisms to ad-
tees, examining scenarios where our approach might fail to                  dress situations where policies are incomplete (e.g., missing
prevent unsafe agent operations.                                            intents or functions). In such cases, the system requests user
Prompt Injection Attacks. Consider an attacker who in-                      intervention or prompts the agent to re-plan, ensuring that
jects malicious instructions through external data sources                  uncertain actions are blocked.
(e.g., web pages) that are processed by the agent. Let
𝑒𝑛𝑣𝑚𝑎𝑙𝑖𝑐𝑖𝑜𝑢𝑠 ∈ E represent the compromised environmental                    7     Evaluation
state containing injected content. The attack aims to manip-                In this section, we conduct a comprehensive evaluation of
ulate the agent’s reasoning process to execute unintended                   our CSAgent prototype by answering four key research ques-
functions. However, for any function 𝑓 to be executed, it                   tions that align with our design goals:
must still satisfy:                                                            RQ1: How well does CSAgent integrate with existing
                                                                            agent frameworks and support diverse interaction modes?
   ∃𝑓 ∈ F𝑐𝑜𝑛𝑑 : PolicySat(𝑃 𝑓 (intent(𝑢𝑡 )), 𝑐𝑣𝑡 ) = true       (15)
                                                                               RQ2: How effective is the context analyzer at identifying
                                                                            GUI event handlers used for context space generation?
where both the user instruction 𝑢𝑡 and the context vector
                                                                               RQ3: How accurately can CSAgent identify and prevent
𝑐𝑣𝑡 remain trustworthy, as they are derived from legitimate
                                                                            unexpected behaviors of computer-use agents?
user inputs and authoritative system APIs. Since the policy
                                                                               RQ4: How much performance and cost overhead does
validation process relies exclusively on these trusted data
                                                                            CSAgent introduce compared to vanilla agent execution?
sources, prompt injection attacks cannot manipulate the
                                                                               RQ5: How effectively does the Policy Evolution Frame-
validation outcome, effectively mitigating this attack vector.
                                                                            work refine context spaces to optimize the trade-off between
Hallucination and Non-determinism. LLM hallucina-
                                                                            security, utility, and performance?
tions may cause the agent to deviate from ideal behavior,
potentially selecting incorrect functions. This can be formal-
ized as:                                                                    7.1   Experimental Setup and Benchmarks (RQ1)
                                                                            To evaluate CSAgent across diverse interaction modalities,
              A𝑢𝑛𝑟𝑒𝑙 (𝑢𝑡 , 𝑒𝑛𝑣𝑡 ) ≠ A𝑖𝑑𝑒𝑎𝑙 (𝑢𝑡 , 𝑒𝑛𝑣𝑡 )         (16)
                                                                            we employ three benchmarks: AgentBench [35] (CLI), Agent-
  However, our safety guarantee from Theorem 1 still holds                  Dojo [9] (API), and AndroidWorld [49] (GUI). We use DeepSeek-
because any function execution 𝑓 must satisfy:                              V3 [33] and Seed1.6 [5] as the runtime text and multimodal
                                                                            models, respectively. The integration mirrors real-world de-
                 Safe(𝑓 , intent(𝑢𝑡 ), 𝑐𝑣𝑡 ) = true             (17)        ployment in two steps: first, we generate context spaces
                                                                            for target tools/apps using our analyzer; second, we adapt
   Even if hallucination causes the agent to select an un-                  agent frameworks to the CSAgent service via minimal RPC
intended function 𝑓 ′ , the execution will be blocked unless                hooks for intent extraction, validation, and context updates.
𝑓 ′ ∈ F𝑛𝑜𝑟𝑚 or all contextual constraints in 𝑃 𝑓 ′ (intent(𝑢𝑡 ))            This successful integration demonstrates CSAgent’s strong
are satisfied. The multi-layered validation reduces the prob-               compatibility (G4).
ability that a hallucinated decision satisfies all required con-               Our evaluation methodology encompasses three primary
straints simultaneously.                                                    dimensions across all benchmarks: utility, security, and over-
Intent Extraction Errors. A potential threat lies in the LLM-               head. Utility measures the agent’s task completion capability
based intent extraction process. If the intent extraction pro-              under CSAgent protection, security evaluates CSAgent’s abil-
duces incorrect results such that intent(𝑢𝑡 ) ≠ intent𝑡𝑟𝑢𝑒 (𝑢𝑡 ),           ity to block unintended behaviors, and overhead quantifies
this could lead to policy selection errors. However, our de-                the latency and token consumption introduced by CSAgent.
sign mitigates this risk by constraining the intent extraction              For AndroidWorld specifically, we also conduct an analy-
to a limited set of legitimate intents, reducing the decision               sis of CSAgent’s code identification capabilities for context
space compared to open-ended generation. Additionally, we                   space generation. We compare it against UI-CTX [29] and
use cosine similarity to verify that the selected intent is truly           AutoDroid [66], representing state-of-the-art approaches in
relevant to the user instruction. Incorrect intent selection                static analysis and GUI exploration, respectively. For secu-
typically results in policy validation failure rather than un-              rity evaluation, all the context policies are generated by the
safe execution, maintaining the safety property.                            context analyzer (satisfying G3). While AgentDojo provides
                                                                       11
Preprint                                                                                                                           Gong et al.


                                                                                      Table 3. Overall defense capability.
               5.9%                                17.6% 5.3%
                      30.2%                                                  Agent          AgentDojo      AgentBench AndroidWorld
                              Common
                              Only in CSAgent                                Type        ASR      UUA           ASR              ASR
                              Only in other
           63.9%                                                            Vanilla  46.61%      54.26%            -                -
                                                          77.0%
                                                                           PVAgent    4.14%      33.03%         1.00%            5.09%
                                                                           CSAgent     0%        41.61%         0.11%            1.21%
      CSAgent vs AutoDroid                      CSAgent vs UI-CTX         CSAgent-RF    0%       54.23%           0%               0%

Figure 6. Comparison of GUI element extraction methods.
                                                                          Table 4. Detailed results of AgentDojo injection attacks.

built-in adversarial tests, we construct additional security
                                                                           Agent      Banking           Slack           Travel   Workspace
test cases for AgentBench and AndroidWorld. These test                     Type      ASR,% UUA,% ASR,% UUA,% ASR,% UUA,% ASR,% UUA,%
cases consist of mismatched user requests and agent actions
(i.e., simulating agent actions that violate the user intent),             Vanilla  45.14    59.72 85.71 64.76 49.17 29.17       6.43    63.39
                                                                          PVAgent    0.00    36.81 0.00 4.76 15.83 40.00         0.71    50.54
creating a series of pairs that serve as input to evaluate ca-            CSAgent    0.00    40.97 0.00 18.10 0.00 40.83         0.00    50.71
pability to detect anomalous agent behaviors that deviate                CSAgent-RF 0.00     56.25 0.00 38.10 0.00 54.17         0.00    68.39
from user intentions. Notably, the policies we test are gen-
erated solely based on the apps themselves, and the policy
generation process has no access to the test set.                        attacks against agents. Additionally, AgentDojo includes
    To emphasize effectiveness, we design our experiments                the Utility Under Attacks (UUA) metric, which evaluates
around CSAgent and two other agent configurations. First,                an agent’s ability to complete original tasks under injec-
we evaluate a Vanilla Agent that operates without any se-                tion attacks. For the AgentDojo travel task, we exclude one
curity protection mechanisms, serving as our analysis base-              out-of-scope attack that targets LLM output content rather
line. Second, we implement a Pre-execution Validation Agent              than agent behavior. The results demonstrate that CSAgent
(PVAgent) that employs dynamic policy generation and vali-               achieves average ASR of only 0.44%, successfully defend-
dation before executing each action (similar to [55, 60]). Fi-           ing against approximately 99.56% of attacks (satisfying G1).
nally, we evaluate CSAgent-RF, a refined variant of CSAgent              In comparison, PVAgent defends against 96.59% of attacks.
that leverages PEF, to further demonstrate its effectiveness.            Table 4 provides detailed results for AgentDojo’s prompt
                                                                         injection attack tests. CSAgent achieves 100% successful de-
7.2    Capability of GUI Analysis (RQ2)                                  fense across all scenarios. For AgentBench and Android-
Figure 6 demonstrates CSAgent’s capability in extracting                 World, CSAgent did not defend against all attacks. This is
GUI elements and event handlers from open-source apps                    due to the context analyzer generating policies that were
and AOSP system apps used by AndroidWorld. UI-CTX was                    not sufficiently comprehensive in a single analysis. After a
configured with default settings, while AutoDroid employed               round of iteration through the PEF, CSAgent was able to
the deep learning-based strategy Humanoid [32]. The re-                  defend against all attacks. CSAgent outperforms PVAgent
sults show that CSAgent extracts 0.93× more GUI element                  mainly due to the nature of static policies, allowing us to
information (including handlers) than AutoDroid and 3.12×                use stronger reasoning models to generate and iteratively
more than UI-CTX (satisfying G3). While some GUI elements                improve policies with low impact on runtime performance.
are identified by these two baseline methods but missed                     The observed UUA drop is due to the high complexity
by CSAgent, most do not produce actual control effects                   of AgentDojo tasks and the information gap during initial
(e.g., merely opening menus rather than clicking specific                policy generation. Specifically, many tasks in AgentDojo are
options). We prompt our context analyzer to ignore these                 derived from environmental contexts (e.g., billing files or to-
non-functional elements to optimize token consumption. We                do lists) or depend on implicit intermediate actions, rather
did not compare to source code-based analysis primarily due              than direct user instructions. Furthermore, some tasks rely
to the lack of available tools. Our approach differs by using            on untrusted data sources, from which CSAgent restricts con-
LLMs to identify GUI-related code, offering better general-              text extraction to ensure security. In our setup, local context
ization capabilities. Importantly, CSAgent can complement                sources (e.g., file systems) are configured as trusted, while
other methods to achieve more comprehensive coverage.                    online sources (e.g., web and email) are treated as untrusted.
                                                                         Since our context analyzer generates policies based solely
7.3    Effectiveness of CSAgent Access Control (RQ3)                     on tool code without access to specific task scenarios, the
Table 3 presents CSAgent’s comprehensive attack defense                  LLM cannot comprehensively reason about such complex
capabilities. The primary evaluation metric is Attack Success            execution patterns or diverse user intents in a single analysis,
Rate (ASR), which measures the success rate of simulated                 leading to runtime failure. However, as shown in §7.5, the
                                                                    12
 Secure and Efficient Access Control Framework for Computer-Use Agents via Context Space                                                                                                                                                                                     Preprint


                       1.00               1.00                 1.00                                                                                                  1.05                                                                1.79
                                                                                                                                                        1.00 1.04
                                                                                                                                                                                                                                                         Vanilla             CSAgent
                1.0           0.94 0.96                 0.93                 0.95   1.0     1.00          1.02   1.00 1.02 0.99                                                   1.75                                                                   PVAgent             CSAgent-RF
                                                                                                   0.94                                                                                             1.59




Normalized Result
                0.8                                                                                                                                                               1.50
                                                                                    0.8                                                                                                                                                                                     1.34
                                                                      0.70                                                                                                        1.25
                0.6                                                                                                                                                                          1.00            1.02                 1.00           1.01              1.00            1.04
                                                                                    0.6                                                                                           1.00
                                                 0.45
                0.4                                                                 0.4                                                                                           0.75
                                                                                                                                                                                  0.50
                0.2                                                                 0.2
                                                                                                                                                                                  0.25
                0.0                                                                 0.0                                                                                           0.00
                       AgentBench          AgentDojo           AndroidWorld                 AgentBench            AgentDojo                             AndroidWorld                          AgentBench                            AgentDojo                      AndroidWorld
                               (a) Normalized utility.                                    (b) Normalized task completion steps.                                                                    (c) Normalized task latency.

                                                               Figure 7. Utility drops and performance overhead of CSAgent.

                                                                                                                                                         Square Root: y=52.08 x+-85.4 (R²=0.791)
 PEF effectively addresses this limitation through iterative                                                                                                                                                               1.4                                                      1.428s
                                                                                                                                              800
 refinement based on runtime feedback.



                                                                                                                         Context Policies Count
                                                                                                                                                                                                                           1.2




                                                                                                                                                                                                           Latency (seconds)
                                                                                                                                              600                                                                          1.0
                                                                                                                                                                                                                           0.8                                                    0.684s
 7.4                  Performance and Cost Overhead (RQ4)                                                                                     400                                                                          0.6
                                                                                                                                                                                                                                                                            0.384s
                                                                                                                                                                                                                           0.4
 Figure 7 illustrates the utility drop and extra latency intro-                                                                               200                                                                                                                  0.207s
                                                                                                                                                                                                                           0.2 0.064s 0.076s         0.100s
 duced by CSAgent. On all three benchmarks, latency over-
                                                                                                                                                  0 0     50    100 150 200 250 300 350                                    0.0    20            40            60             80            100
 head introduced by CSAgent is less than 5%, compared to
 PVAgent’s overhead of 58.57%, 34.28%, and 103.98% on Agent-                                                             (a) Policy count vs app size (MB). (b) Loading latency distribution.
 Bench, AndroidWorld, and AgentDojo, respectively. Addi-
 tionally, we found that 80.08% of contexts are classified as                                                                                                    Figure 8. Context space complexity.
 cold or warm temperature levels. These results demonstrate
 that our optimized context manager efficiently performs user
                                                                                                                                                        Table 5. Average token consumption per task.
 intent extraction, context updates and policy verification (sat-
 isfying G2). For utility, CSAgent causes a 15.58% decrease on
                                                                                                                                                                            AgentBench                AgentDojo                          AndroidWorld
 average, significantly outperforming PVAgent. The degra-
                                                                                                                                                         Vanilla                 2980.36                   13000.99                             109296.92
 dation on AgentBench and AndroidWorld is less than 5%,
                                                                                                                                                        CSAgent                  5961.70                    4364.93                              7161.50
 but that on AgentDojo is more pronounced, primarily due to                                                                                             Overhead                 200.03%                    33.57%                                6.55%
 task complexity and insufficient policy quality, as discussed                                                                                           Prompt                   96.44%                    95.39%                               97.42%
 earlier. Notably, upon a policy validation failure during eval-
 uation, the agent is prompted to either explore alternative
 execution paths or terminate the task. In real deployments,                                                             size. As shown in Figure 8a, the policy count grows at a dimin-
 user intervention or agent reflection could resume such tasks,                                                          ishing rate as app size increases. This is mainly because we
 further reducing the impact. To explore this potential, we                                                              generate policies only for security-critical functions, which
 evaluate a variant incorporating agent reflection upon val-                                                             are typically limited in number. Figure 8b shows the load-
 idation failures. On AgentDojo, this approach reduces the                                                               ing latency distribution, revealing that 96.00% of context
 utility drop to 9.93% and improves UUA to 51.79%. However,                                                              spaces can be loaded within one second. Loading latency
 it incurs a 21.04% latency overhead and increases ASR to                                                                correlates directly with context space size and I/O latency.
 0.455%, as additional LLM requests introduce both compu-                                                                When context spaces are cached, retrieval latency becomes
 tational costs and increased uncertainty. We also evaluated                                                             negligible. Therefore, beyond our LRU replacement policy,
 CSAgent’s impact on task completion steps. Overall, the im-                                                             larger context spaces (such as that for the settings app) can be
 pact is minimal, indicating that CSAgent’s decisions to allow                                                           permanently fixed in cache to further optimize performance.
 or block agent actions are relatively accurate.                                                                            Table 5 presents CSAgent’s per task token consumption
    We further evaluated the complexity of context spaces and                                                            compared to the vanilla agent. The geometric mean of con-
 their loading latency. Across the three benchmarks (Agent-                                                              sumption overhead is 35.30%, with over 96.41% consisting
 Bench, AgentDojo, and AndroidWorld), the average number                                                                 of prompt tokens, which are less expensive than completion
 of policies per application, which is also the number of pre-                                                           tokens. Generally, more complex tasks have proportionally
 dicted user intents, is 120, 13.25, and 150.4, respectively, with                                                       lower overhead. For instance, AgentBench tasks have low
 average context counts of 187.0, 25.75, and 238.65. We also                                                             average token consumption, so the large context space re-
 analyzed real-world complex apps from AndroidWorld to                                                                   sults in higher overhead. Conversely, AndroidWorld tasks are
 explore the relationship between app size and context space                                                             highly complex, requiring multimodal capabilities for screen
                                                                                                                   13
Preprint                                                                                                                     Gong et al.


recognition, leading to very high task token consumption               applied to website scenarios. Our evaluation included apps
and lower overhead. In comparison, runtime policy genera-              written in TypeScript, showing the method’s compatibility.
tion methods introduce 1.61× additional token consumption              However, web environments are more fragmented and often
on AgentDojo [55]. CSAgent’s low token consumption re-                 face more content security issues, limiting the effectiveness
sults from development-phase policy generation that applies            of access control. Generating policies for GUI apps through
across all devices and users without regeneration, and from            source code analysis remains a potential hurdle for further
requiring only one additional LLM inference per task regard-           adoption of this approach. Nevertheless, we provide a com-
less of complexity (satisfying G2).                                    prehensive automated toolchain that assists developers in
                                                                       constructing and maintaining policies. We argue that, simi-
7.5   Efficacy of Policy Evolution (RQ5)                               lar to traditional security models, agent security requires an
                                                                       ecosystem-wide effort to enhance the quality of protections
To validate the PEF’s effectiveness, we focus on AgentDojo,
                                                                       and foster stronger collaboration in policy creation.
where CSAgent exhibits the most significant utility degrada-
tion, and iteratively refine the corresponding context spaces.
Specifically, we consolidate logs from both utility and se-            9   Related Work
curity tests, enabling the LLM to simultaneously consider
utility and security trade-offs during refinement. PEF itera-          Access control and contextual integrity. Traditional ac-
                                                                       cess control mechanisms in OS include discretionary access
tively tests and upgrades each context space until either no
further improvements are identified or sufficiently high eval-         control (DAC) and mandatory access control (MAC) [52].
uation scores are achieved. In our experiments, convergence            SELinux [58, 69] exemplifies MAC principles by defining
requires an average of 7.25 iterations per context space.              fine-grained policies that govern process interactions and
   As shown in Table 4, CSAgent-RF maintains 0% ASR while              resource access based on security contexts. The theory of
improving UUA to 54.23%, demonstrating enhanced utility                contextual integrity (CI) [39, 40], proposed in more recent
                                                                       years, has been explored by researchers for its applications
preservation without compromising security guarantees. Fig-
ure 7 shows the performance improvements: CSAgent-RF                   in existing operating systems [50, 67], driving the evolution
reduces utility drop to 6.76% and latency overhead to 0.53%.           of permission management and access control toward more
Across all benchmarks, the overall utility decrease is reduced         user-transparent, secure, and flexible approaches.
to 5.42%, with an average latency overhead of only 1.99%.              Access control for LLM agents. For agents, access con-
                                                                       trol focuses on constraining tool calls through pre-execution
Notably, the reduced latency overhead primarily stems from
                                                                       validation. Most approaches use contextual information to
a decrease in the average number of completion steps for
some complex tasks. More precise policies enable the agent             make authorization decisions, following the CI principle.
to execute tasks more efficiently by eliminating unneces-              AirGapAgent [4] employs a separate LLM to directly make
sary validation failures and re-planning cycles. Our analysis          decisions about data access permissions. GuardAgent [73]
reveals three primary categories of improvements in the re-            employs LLMs to generate guardrail code that validates pre-
                                                                       defined rules before executing actions. VeriSafe Agent [27]
fined context spaces. First, PEF generates more explicit and
                                                                       describes rules through Horn clauses and verifies agent be-
fine-grained intent definitions. Second, PEF produces more
precise constraint conditions and validation logic. Third, PEF         havior based on logic-based reasoning. ShieldAgent [7] en-
relaxes overly conservative security constraints that unnec-           forces explicit policy compliance by constructing action-
essarily block benign operations. As a result, CSAgent-RF              based probabilistic rule circuits for formal verification. Quad-
achieves more accurate runtime intent extraction and policy            Sentinel [77] employs a multi-agent guard team to enforce
                                                                       safety through machine-checkable sequent logic rules de-
retrieval, performs more precise validation, and maintains
                                                                       rived from natural language policies. Conseca [60] and Pro-
an effective balance between blocking dangerous operations
and permitting legitimate actions.                                     gent [55] achieve dynamic security policy generation, en-
                                                                       abling more autonomous responses to diverse task scenarios.
                                                                       AgentSentinel [21] extends context extraction to the OS,
8     Discussion                                                       providing real-time protection for CUAs by combining rule-
CSAgent supports automated policy generation and iterative             based and LLM-based auditing. These approaches rely on
improvement through the PEF based on runtime feedback.                 runtime LLM-based security decision-making, suffering from
However, an automated testing tool is still needed to cover a          security or performance limitations. AgentSpec [63] employs
broader range of agent actions and attacks, allowing for large-        predefined static policies, but adopts a risk-blocking para-
scale testing of policy completeness and further refinement.           digm that struggles with unknown threats and lacks user
Currently, CSAgent focuses on protecting single-agent sce-             intent differentiation, limiting policy flexibility.
narios. However, multi-agent collaboration introduces more             Other system-level LLM agent protection. Beyond access
complex challenges, such as cross-agent context transfer,              control, some other forms of system-level protection have
which we plan to explore in future work. CSAgent can be                been proposed for agents. The Instruction Hierarchy [61]
                                                                  14
Secure and Efficient Access Control Framework for Computer-Use Agents via Context Space                                                                 Preprint


and StruQ [6] implement privilege and type separation for                                Proceedings of the Network and Distributed System Security Symposium
LLM inputs to mitigate interference between different in-                                (NDSS’24).
put sources. f -secure LLM system [70], RTBAS [80], and                             [11] Yu Du, Fangyun Wei, and Hongyang Zhang. 2024. Anytool: Self-
                                                                                         reflective, hierarchical agents for large-scale api calls. arXiv preprint
SAFEFLOW [30] introduce information flow control into                                    arXiv:2402.04253 (2024).
LLM agents to prevent prompt injection and privacy leakage.                         [12] Hugging Face. 2025. Function Calling. https://huggingface.co/docs/
GoEX [46] implements post-facto validation of agent actions                              hugs/guides/function-calling.
and isolates dangerous operations through sandboxing. Iso-                          [13] Inc. GitHub. 2021. CodeQL. https://codeql.github.com.
lateGPT [71] employs isolation for multi-LLM application                            [14] Yichen Gong, Delong Ran, Xinlei He, Tianshuo Cong, Anyu Wang,
                                                                                         and Xiaoyun Wang. 2025. Safety misalignment against large language
scenarios to prevent interference between LLMs and differ-                               models. In Proceedings 2025 Network and Distributed System Security
ent applications. ACE [28] decouples agent planning into                                 Symposium (NDSS’25).
two phases to defend against untrusted third-party apps.                            [15] Google. 2025. AI Edge Function Calling guide. https://ai.google.dev/
These approaches and CSAgent can collectively form part of                               edge/mediapipe/solutions/genai/function_calling.
a defense-in-depth strategy [17], working in conjunction to                         [16] Google. 2025. Android Debug Bridge (adb). https://developer.android.
                                                                                         com/tools/adb.
achieve more comprehensive protection.                                              [17] Google. 2025. Google’s Approach for Secure AI Agents: An Intro-
                                                                                         duction. https://storage.googleapis.com/gweb-research2023-media/
10     Conclusion                                                                        pubtools/1018686.pdf.
                                                                                    [18] Kai Greshake, Sahar Abdelnabi, Shailesh Mishra, Christoph Endres,
We present CSAgent, a secure, efficient, and flexible access                             Thorsten Holz, and Mario Fritz. 2023. Not what you’ve signed up for:
control framework to protect computer-use agents. CSAgent                                Compromising real-world llm-integrated applications with indirect
introduces a novel context space design that enforces con-                               prompt injection. In Proceedings of the 16th ACM Workshop on Artificial
textual and intent-aware policies to validate agent actions.                             Intelligence and Security. 79–90.
                                                                                    [19] Daya Guo, Dejian Yang, Haowei Zhang, Junxiao Song, Ruoyu Zhang,
Evaluation shows that CSAgent provides strong security
                                                                                         Runxin Xu, Qihao Zhu, Shirong Ma, Peiyi Wang, Xiao Bi, et al. 2025.
guarantees while incurring acceptable overhead.                                          Deepseek-r1: Incentivizing reasoning capability in llms via reinforce-
                                                                                         ment learning. arXiv preprint arXiv:2501.12948 (2025).
References                                                                          [20] Wenyi Hong, Weihan Wang, Qingsong Lv, Jiazheng Xu, Wenmeng Yu,
                                                                                         Junhui Ji, Yan Wang, Zihan Wang, Yuxiao Dong, Ming Ding, et al. 2024.
 [1] Anthropic. 2025. Bash tool. https://docs.anthropic.com/en/docs/                     Cogagent: A visual language model for gui agents. In Proceedings of
     agents-and-tools/tool-use/bash-tool.                                                the IEEE/CVF Conference on Computer Vision and Pattern Recognition.
 [2] Anthropic. 2025. Computer use tool. https://docs.anthropic.com/en/                  14281–14290.
     docs/agents-and-tools/tool-use/computer-use-tool.                              [21] Haitao Hu, Peng Chen, Yanpeng Zhao, and Yuqi Chen. 2025. AgentSen-
 [3] Apple. 2025.       Integrating actions with Siri and Apple Intel-                   tinel: An End-to-End and Real-Time Security Defense Framework for
     ligence.     https://developer.apple.com/documentation/appintents/                  Computer-Use Agents. arXiv:2509.07764 [cs.CR] https://arxiv.org/abs/
     integrating-actions-with-siri-and-apple-intelligence.                               2509.07764
 [4] Eugene Bagdasarian, Ren Yi, Sahra Ghalebikesabi, Peter Kairouz,                [22] Lei Huang, Weijiang Yu, Weitao Ma, Weihong Zhong, Zhangyin Feng,
     Marco Gruteser, Sewoong Oh, Borja Balle, and Daniel Ramage. 2024.                   Haotian Wang, Qianglong Chen, Weihua Peng, Xiaocheng Feng, Bing
     AirGapAgent: Protecting privacy-conscious conversational agents. In                 Qin, et al. 2025. A survey on hallucination in large language models:
     Proceedings of the 2024 on ACM SIGSAC Conference on Computer and                    Principles, taxonomy, challenges, and open questions. ACM Transac-
     Communications Security. 3868–3882.                                                 tions on Information Systems 43, 2 (2025), 1–55.
 [5] ByteDance. 2025. Introduction to Techniques Used in Seed1.6. https:
                                                                                    [23] Michael Kerrisk. 2025. Linux man pages online. https://man7.org/
     //seed.bytedance.com/en/seed1_6.                                                    linux/man-pages/.
 [6] Sizhe Chen, Julien Piet, Chawin Sitawarin, and David Wagner. 2024.             [24] LangChain. 2025. File System Tool. https://python.langchain.com/
     Struq: Defending against prompt injection with structured queries.                  docs/integrations/tools/filesystem/.
     arXiv preprint arXiv:2402.06363 (2024).                                        [25] LangChain. 2025. Shell (Bash) Tool. https://python.langchain.com/
 [7] Zhaorun Chen, Mintong Kang, and Bo Li. 2025. ShieldAgent: Shielding                 docs/integrations/tools/bash/.
     Agents via Verifiable Safety Policy Reasoning. In Forty-second Interna-        [26] LangChain. 2025.        Tools.    https://python.langchain.com/docs/
     tional Conference on Machine Learning. https://openreview.net/forum?                integrations/tools/.
     id=DkRYImuQA9                                                                  [27] Jungjae Lee, Dongjae Lee, Chihun Choi, Youngmin Im, Jaeyoung Wi,
 [8] Visual Studio Code. 2025. Use agent mode in VS Code. https://code.                  Kihong Heo, Sangeun Oh, Sunjae Lee, and Insik Shin. 2025. Safeguard-
     visualstudio.com/docs/copilot/chat/chat-agent-mode.                                 ing mobile gui agent via logic-based action verification. arXiv preprint
 [9] Edoardo Debenedetti, Jie Zhang, Mislav Balunovic, Luca Beurer-                      arXiv:2503.18492 (2025).
     Kellner, Marc Fischer, and Florian Tramèr. 2024. AgentDojo: A                  [28] Evan Li, Tushin Mallick, Evan Rose, William Robertson, Alina Oprea,
     Dynamic Environment to Evaluate Prompt Injection Attacks and                        and Cristina Nita-Rotaru. 2025. ACE: A Security Architecture for
     Defenses for LLM Agents. In Advances in Neural Information                          LLM-Integrated App Systems. arXiv:2504.20984 [cs.CR] https://arxiv.
     Processing Systems, A. Globerson, L. Mackey, D. Belgrave, A. Fan,                   org/abs/2504.20984
     U. Paquet, J. Tomczak, and C. Zhang (Eds.), Vol. 37. Curran Asso-              [29] Jiawei Li, Jiahao Liu, Jian Mao, Jun Zeng, and Zhenkai Liang. 2025.
     ciates, Inc., 82895–82920.      https://proceedings.neurips.cc/paper_               UI-CTX: Understanding UI Behaviors with Code Contexts for Mobile
     files/paper/2024/file/97091a5177d8dc64b1da8bf3e1f6fb54-Paper-                       Applications. In NDSS.
     Datasets_and_Benchmarks_Track.pdf                                              [30] Peiran Li, Xinkai Zou, Zhuohang Wu, Ruifeng Li, Shuo Xing, Han-
[10] Gelei Deng, Yi Liu, Yuekang Li, Kailong Wang, Ying Zhang, Zefeng                    wen Zheng, Zhikai Hu, Yuping Wang, Haoxi Li, Qin Yuan, Yingmo
     Li, Haoyu Wang, Tianwei Zhang, and Yang Liu. 2024. Masterkey:
     Automated jailbreak across multiple large language model chatbots. In
                                                                               15
Preprint                                                                                                                                                Gong et al.


     Zhang, and Zhengzhong Tu. 2025. SAFEFLOW: A Principled Proto-                          arXiv preprint arXiv:2501.12326 (2025).
     col for Trustworthy and Transactional Autonomous Agent Systems.                   [49] Christopher Rawles, Sarah Clinckemaillie, Yifan Chang, Jonathan
     arXiv:2506.07564 [cs.AI] https://arxiv.org/abs/2506.07564                              Waltz, Gabrielle Lau, Marybeth Fair, Alice Li, William Bishop, Wei
[31] Yuanchun Li, Hao Wen, Weijun Wang, Xiangyu Li, Yizhen Yuan, Guo-                       Li, Folawiyo Campbell-Ajala, et al. 2024. Androidworld: A dynamic
     hong Liu, Jiacheng Liu, Wenxing Xu, Xiang Wang, Yi Sun, et al. 2024.                   benchmarking environment for autonomous agents. arXiv preprint
     Personal llm agents: Insights and survey about the capability, efficiency              arXiv:2405.14573 (2024).
     and security. arXiv preprint arXiv:2401.05459 (2024).                             [50] Franziska Roesner, Tadayoshi Kohno, Alexander Moshchuk, Bryan
[32] Yuanchun Li, Ziyue Yang, Yao Guo, and Xiangqun Chen. 2019. Hu-                         Parno, Helen J Wang, and Crispin Cowan. 2012. User-driven access
     manoid: A Deep Learning-Based Approach to Automated Black-box                          control: Rethinking permission granting in modern operating systems.
     Android App Testing. In 2019 34th IEEE/ACM International Conference                    In 2012 IEEE Symposium on Security and Privacy. IEEE, 224–238.
     on Automated Software Engineering (ASE). 1070–1073. doi:10.1109/ASE.              [51] Pascal J Sager, Benjamin Meyer, Peng Yan, Rebekka von Wartburg-
     2019.00104                                                                             Kottler, Layan Etaiwi, Aref Enayati, Gabriel Nobel, Ahmed Abdulkadir,
[33] Aixin Liu, Bei Feng, Bing Xue, Bingxuan Wang, Bochao Wu, Chengda                       Benjamin F Grewe, and Thilo Stadelmann. 2025. AI Agents for Com-
     Lu, Chenggang Zhao, Chengqi Deng, Chenyu Zhang, Chong Ruan, et al.                     puter Use: A Review of Instruction-based Computer Control, GUI
     2024. Deepseek-v3 technical report. arXiv preprint arXiv:2412.19437                    Automation, and Operator Assistants. arXiv preprint arXiv:2501.16150
     (2024).                                                                                (2025).
[34] Tong Liu, Zizhuang Deng, Guozhu Meng, Yuekang Li, and Kai Chen.                   [52] Ravi Sandhu and Pierangela Samarati. 1996. Authentication, access
     2024. Demystifying rce vulnerabilities in llm-integrated apps. In Pro-                 control, and audit. ACM Computing Surveys (CSUR) 28, 1 (1996), 241–
     ceedings of the 2024 on ACM SIGSAC Conference on Computer and                          243.
     Communications Security. 1716–1730.                                               [53] Xinyue Shen, Zeyuan Chen, Michael Backes, Yun Shen, and Yang
[35] Xiao Liu, Hao Yu, Hanchen Zhang, Yifan Xu, Xuanyu Lei, Hanyu                           Zhang. 2024. " do anything now": Characterizing and evaluating in-
     Lai, Yu Gu, Hangliang Ding, Kaiwen Men, Kejuan Yang, Shudan                            the-wild jailbreak prompts on large language models. In Proceedings of
     Zhang, Xiang Deng, Aohan Zeng, Zhengxiao Du, Chenhui Zhang,                            the 2024 on ACM SIGSAC Conference on Computer and Communications
     Sheng Shen, Tianjun Zhang, Yu Su, Huan Sun, Minlie Huang, Yuxiao                       Security. 1671–1685.
     Dong, and Jie Tang. 2023. AgentBench: Evaluating LLMs as Agents.                  [54] Jiawen Shi, Zenghui Yuan, Yinuo Liu, Yue Huang, Pan Zhou, Lichao
     arXiv:2308.03688 [cs.AI] https://arxiv.org/abs/2308.03688                              Sun, and Neil Zhenqiang Gong. 2024. Optimization-based prompt
[36] Yupei Liu, Yuqi Jia, Runpeng Geng, Jinyuan Jia, and Neil Zhenqiang                     injection attack to llm-as-a-judge. In Proceedings of the 2024 on ACM
     Gong. 2024. Formalizing and benchmarking prompt injection attacks                      SIGSAC Conference on Computer and Communications Security. 660–
     and defenses. In 33rd USENIX Security Symposium (USENIX Security                       674.
     24). 1831–1847.                                                                   [55] Tianneng Shi, Jingxuan He, Zhun Wang, Linyu Wu, Hongwei Li,
[37] Microsoft. 2025.        Microsoft 365 Copilot overview.             https:             Wenbo Guo, and Dawn Song. 2025. Progent: Programmable privi-
     //learn.microsoft.com/en-us/copilot/microsoft-365/microsoft-                           lege control for LLM agents. arXiv preprint arXiv:2504.11703 (2025).
     365-copilot-overview.                                                             [56] Yucheng Shi, Wenhao Yu, Wenlin Yao, Wenhu Chen, and Ning-
[38] Microsoft. 2025. PowerShell Documentation. https://learn.microsoft.                    hao Liu. 2025. Towards Trustworthy GUI Agents: A Survey.
     com/en-us/powershell/.                                                                 arXiv:2503.23434 [cs.LG] https://arxiv.org/abs/2503.23434
[39] Helen Nissenbaum. 2004. Privacy as contextual integrity. Wash. L. Rev.            [57] Varin Sikka and Vishal Sikka. 2025. Hallucination Stations: On Some
     79 (2004), 119.                                                                        Basic Limitations of Transformer-Based Language Models. arXiv
[40] Helen Nissenbaum. 2009. Privacy in context: Technology, policy, and                    preprint arXiv:2507.07505 (2025).
     the integrity of social life. In Privacy in context. Stanford University          [58] Stephen Smalley and Robert Craig. 2013. Security enhanced (se) an-
     Press.                                                                                 droid: bringing flexible mac to android.. In Proceedings of the Network
[41] OpenAI. 2025. Computer-Using Agent. https://openai.com/index/                          and Distributed System Security Symposium (NDSS’13).
     computer-using-agent/.                                                            [59] Hongjin Su, Ruoxi Sun, Jinsung Yoon, Pengcheng Yin, Tao Yu, and
[42] OpenAI. 2025. Function Calling. https://platform.openai.com/docs/                      Sercan Ö Arık. 2025. Learn-by-interact: A Data-Centric Framework
     guides/function-calling?api-mode=chat.                                                 for Self-Adaptive Agents in Realistic Environments. arXiv preprint
[43] OpenAI. 2025. Local Shell Tool. https://platform.openai.com/docs/                      arXiv:2501.10893 (2025).
     guides/tools-local-shell.                                                         [60] Lillian Tsai and Eugene Bagdasarian. 2025. Contextual Agent Secu-
[44] OWASP. 2024. OWASP Top 10 for LLM Applications 2025. https://                          rity: A Policy for Every Purpose. In Proceedings of the 2025 Workshop
     genai.owasp.org/resource/owasp-top-10-for-llm-applications-2025/.                      on Hot Topics in Operating Systems (Banff, AB, Canada) (HotOS ’25).
[45] Shishir G. Patil, Tianjun Zhang, Vivian Fang, Noppapon C., Roy Huang,                  Association for Computing Machinery, New York, NY, USA, 8–17.
     Aaron Hao, Martin Casado, Joseph E. Gonzalez, Raluca Ada Popa,                         doi:10.1145/3713082.3730378
     and Ion Stoica. 2024. GoEX: Perspectives and Designs Towards a                    [61] Eric Wallace, Kai Xiao, Reimar Leike, Lilian Weng, Johannes Heidecke,
     Runtime for Autonomous LLM Applications. arXiv:2404.06921 [cs.CL]                      and Alex Beutel. 2024. The instruction hierarchy: Training llms to pri-
     https://arxiv.org/abs/2404.06921                                                       oritize privileged instructions. arXiv preprint arXiv:2404.13208 (2024).
[46] Shishir G Patil, Tianjun Zhang, Vivian Fang, Roy Huang, Aaron Hao,                [62] Bryan Wang, Gang Li, and Yang Li. 2023. Enabling conversational
     Martin Casado, Joseph E Gonzalez, Raluca Ada Popa, Ion Stoica, et al.                  interaction with mobile ui using large language models. In Proceedings
     2024. GoEX: Perspectives and Designs Towards a Runtime for Au-                         of the 2023 CHI Conference on Human Factors in Computing Systems.
     tonomous LLM Applications. CoRR (2024).                                                1–17.
[47] Yujia Qin, Shihao Liang, Yining Ye, Kunlun Zhu, Lan Yan, Yaxi Lu,                 [63] Haoyu Wang, Christopher M. Poskitt, and Jun Sun. 2025. AgentSpec:
     Yankai Lin, Xin Cong, Xiangru Tang, Bill Qian, et al. 2023. Toolllm:                   Customizable Runtime Enforcement for Safe and Reliable LLM Agents.
     Facilitating large language models to master 16000+ real-world apis.                   arXiv:2503.18666 [cs.AI] https://arxiv.org/abs/2503.18666
     arXiv preprint arXiv:2307.16789 (2023).                                           [64] Shuai Wang, Weiwen Liu, Jingxuan Chen, Yuqi Zhou, Weinan Gan,
[48] Yujia Qin, Yining Ye, Junjie Fang, Haoming Wang, Shihao Liang, Shizuo                  Xingshan Zeng, Yuhan Che, Shuai Yu, Xinlong Hao, Kun Shao, Bin
     Tian, Junda Zhang, Jiahao Li, Yunxin Li, Shijue Huang, et al. 2025. UI-                Wang, Chuhan Wu, Yasheng Wang, Ruiming Tang, and Jianye Hao.
     TARS: Pioneering Automated GUI Interaction with Native Agents.                         2025. GUI Agents with Foundation Models: A Comprehensive Survey.

                                                                                  16
Secure and Efficient Access Control Framework for Computer-Use Agents via Context Space                                                          Preprint


     arXiv:2411.04890 [cs.AI] https://arxiv.org/abs/2411.04890                           2411.18279
[65] Alexander Wei, Nika Haghtalab, and Jacob Steinhardt. 2023. Jailbroken:         [80] Peter Yong Zhong, Siyuan Chen, Ruiqi Wang, McKenna McCall, Ben L.
     How does llm safety training fail? Advances in Neural Information                   Titzer, Heather Miller, and Phillip B. Gibbons. 2025. RTBAS: De-
     Processing Systems 36 (2023), 80079–80110.                                          fending LLM Agents Against Prompt Injection and Privacy Leakage.
[66] Hao Wen, Yuanchun Li, Guohong Liu, Shanhui Zhao, Tao Yu, Toby                       arXiv:2502.08966 [cs.CR] https://arxiv.org/abs/2502.08966
     Jia-Jun Li, Shiqi Jiang, Yunhao Liu, Yaqin Zhang, and Yunxin Liu. 2024.
     Autodroid: Llm-powered task automation in android. In Proceedings
     of the 30th Annual International Conference on Mobile Computing and
     Networking. 543–557.
[67] Primal Wijesekera, Arjun Baokar, Ashkan Hosseini, Serge Egelman,
     David Wagner, and Konstantin Beznosov. 2015. Android permissions
     remystified: A field study on contextual integrity. In 24th USENIX
     Security Symposium (USENIX Security 15). 499–514.
[68] Yotam Wolf, Noam Wies, Oshri Avnery, Yoav Levine, and Amnon
     Shashua. 2023. Fundamental limitations of alignment in large language
     models. arXiv preprint arXiv:2304.11082 (2023).
[69] Chris Wright, Crispin Cowan, Stephen Smalley, James Morris, and
     Greg Kroah-Hartman. 2002. Linux security modules: General secu-
     rity support for the linux kernel. In 11th USENIX security symposium
     (USENIX Security 02).
[70] Fangzhou Wu, Ethan Cecchetti, and Chaowei Xiao. 2024. System-Level
     Defense against Indirect Prompt Injection Attacks: An Information
     Flow Control Perspective. arXiv:2409.19091 [cs.CR] https://arxiv.org/
     abs/2409.19091
[71] Yuhao Wu, Franziska Roesner, Tadayoshi Kohno, Ning Zhang, and
     Umar Iqbal. 2025. IsolateGPT: An Execution Isolation Architecture for
     LLM-Based Agentic Systems. In NDSS.
[72] Zhiheng Xi, Wenxiang Chen, Xin Guo, Wei He, Yiwen Ding, Boyang
     Hong, Ming Zhang, Junzhe Wang, Senjie Jin, Enyu Zhou, et al. 2025.
     The rise and potential of large language model based agents: A survey.
     Science China Information Sciences 68, 2 (2025), 121101.
[73] Zhen Xiang, Linzhi Zheng, Yanjie Li, Junyuan Hong, Qinbin Li, Han
     Xie, Jiawei Zhang, Zidi Xiong, Chulin Xie, Carl Yang, et al. 2024.
     Guardagent: Safeguard llm agents by a guard agent via knowledge-
     enabled reasoning. arXiv preprint arXiv:2406.09187 (2024).
[74] Tianbao Xie, Danyang Zhang, Jixuan Chen, Xiaochuan Li, Siheng
     Zhao, Ruisheng Cao, Toh Jing Hua, Zhoujun Cheng, Dongchan
     Shin, Fangyu Lei, Yitao Liu, Yiheng Xu, Shuyan Zhou, Silvio
     Savarese, Caiming Xiong, Victor Zhong, and Tao Yu. 2024. OS-
     World: Benchmarking Multimodal Agents for Open-Ended Tasks in
     Real Computer Environments. In Advances in Neural Information
     Processing Systems, A. Globerson, L. Mackey, D. Belgrave, A. Fan,
     U. Paquet, J. Tomczak, and C. Zhang (Eds.), Vol. 37. Curran Asso-
     ciates, Inc., 52040–52094.      https://proceedings.neurips.cc/paper_
     files/paper/2024/file/5d413e48f84dc61244b6be550f1cd8f5-Paper-
     Datasets_and_Benchmarks_Track.pdf
[75] Jiaming Xu, Kaibin Guo, Wuxuan Gong, and Runyu Shi. 2024. OS-
     Agent: Copiloting Operating System with LLM-based Agent. In 2024
     International Joint Conference on Neural Networks (IJCNN). IEEE, 1–9.
[76] Ziwei Xu, Sanjay Jain, and Mohan Kankanhalli. 2024. Hallucination
     is inevitable: An innate limitation of large language models. arXiv
     preprint arXiv:2401.11817 (2024).
[77] Yiliu Yang, Yilei Jiang, Qunzhong Wang, Yingshui Tan, Xiaoyong Zhu,
     Sherman S. M. Chow, Bo Zheng, and Xiangyu Yue. 2025. QuadSentinel:
     Sequent Safety for Machine-Checkable Control in Multi-agent Systems.
     arXiv:2512.16279 [cs.AI] https://arxiv.org/abs/2512.16279
[78] Zhiyuan Yu, Xiaogeng Liu, Shunning Liang, Zach Cameron, Chaowei
     Xiao, and Ning Zhang. 2024. Don’t listen to me: understanding and
     exploring jailbreak prompts of large language models. In 33rd USENIX
     Security Symposium (USENIX Security 24). 4675–4692.
[79] Chaoyun Zhang, Shilin He, Jiaxu Qian, Bowen Li, Liqun Li, Si Qin,
     Yu Kang, Minghua Ma, Guyue Liu, Qingwei Lin, Saravan Rajmohan,
     Dongmei Zhang, and Qi Zhang. 2025. Large Language Model-Brained
     GUI Agents: A Survey. arXiv:2411.18279 [cs.AI] https://arxiv.org/abs/

                                                                               17
