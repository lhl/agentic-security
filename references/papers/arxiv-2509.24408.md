                                                         FuncPoison: Poisoning Function Library to Hijack Multi-agent
                                                                         Autonomous Driving Systems

                                                                         Yuzhen Long                                        Songze Li
                                                                      Southeast University                             Southeast University
                                                                    213221738@seu.edu.cn                               songzeli@seu.edu.cn




arXiv:2509.24408v2 [cs.CR] 29 Dec 2025
                                         Abstract—Autonomous driving systems increasingly rely on          multi-agent systems often rely on externally provided or pre-
                                         multi-agent architectures powered by large language mod-          designed Function Libraries—including perception APIs,
                                         els (LLMs), where specialized agents collaborate to perceive,     mapping modules, and vendor toolkits [8]–[11]—maintained
                                         reason, and plan. A key component of these systems is the         and updated by third-party providers. This design improves
                                         shared function library, a collection of software tools that      modularity and efficiency but simultaneously exposes a new
                                         agents use to process sensor data and navigate complex driving    supply-chain attack surface. [12] A compromised or mali-
                                         environments. Many functions in the library are provided and      cious provider can inject poisoned functions during distri-
                                         updated by third parties, which introduces under-explored         bution or version updates, as seen in real-world incidents
                                         upstream vulnerabilities. In this paper, we introduce FuncPoi-    such as the event-stream backdoor and the coa/rc [13], [14]
                                         son, a novel poisoning attack targeting the function library,     compromises in the npm ecosystem, as well as malicious or
                                         which manipulates the behavior of LLM-driven multi-agent          typosquatting packages [15] discovered in PyPI [16] and
                                         autonomous driving systems. FuncPoison exploits two key           unverified module updates in ROS-based robotic frame-
                                         weaknesses in how agents access the function library: (1)         works [17], [18]. These libraries and updates are inher-
                                         agents rely on text-based instructions to select tools; and (2)   ently trusted by downstream agents, so poisoned entries are
                                         these tools are activated using standardized command formats      seamlessly integrated and executed during normal operation.
                                         that attackers can replicate. By injecting malicious tools with   Consequently, even without local privilege or prompt ma-
                                         deceptive instructions, FuncPoison manipulates one agent’s
                                                                                                           nipulation, an attacker can influence the system’s runtime
                                                                                                           behavior through supply-side poisoning of the Function
                                         decisions—such as misinterpreting road conditions—triggering
                                                                                                           Library.
                                         cascading errors that mislead other agents in the system.
                                                                                                                While supply-chain compromises highlight the feasi-
                                         We experimentally evaluate FuncPoison on two representative
                                                                                                           bility of function-level manipulation, the security implica-
                                         multi-agent autonomous driving systems, demonstrating its
                                                                                                           tions of this dependency remain largely unexplored.Existing
                                         ability to significantly degrade trajectory accuracy, flexibly
                                                                                                           poisoning attacks have focused on training data, retrieval
                                         target specific agents to induce coordinated misbehaviors, and
                                                                                                           modules, and memory bases, they suffer from several key
                                         evade various defense mechanisms. Our results reveal that the     limitations in real-world autonomous driving applications:
                                         function library, often considered a simple toolset, can serve    (1) they often lack stealth [19], [20], as anomalous inputs
                                         as a critical attack surface in LLM-based autonomous driving      [21]or memory traces can trigger detection mechanisms;
                                         systems, raising elevated concerns on their reliability.          (2) their effects are frequently localized, impacting only
                                                                                                           specific components without propagating across agents; and
                                         1. Introduction                                                   (3) they are vulnerable to defenses such as filtering, memory
                                         Large language model (LLM)-based agents have shown                sanitization, or retraining. In contrast, the function-calling
                                         strong potential in autonomous driving systems [1]–[5],           mechanism operates outside the core reasoning loop, yet
                                         where they interpret complex environments and coordi-             directly affects runtime decisions—making it a unique and
                                         nate decisions through structured interactions with func-         powerful attack surface [22]. Despite this, it has received
                                         tion libraries and perception modules [6]. To manage the          little security scrutiny.
                                         growing complexity of driving tasks, recent systems have               As illustrated in Fig. 1, prior poisoning methods target
                                         adopted multi-agent frameworks where LLM agents collab-           static knowledge (e.g., memory, database, or retrieval aug-
                                         orate through structured pipelines. A central mechanism in        mentation), aiming to bias the internal reasoning process of
                                         these pipelines is the function call, where agents invoke pre-    LLM agents [23]. These methods often degrade under real-
                                         defined functions from a shared Function Library to perform       time constraints or are blocked by robust instruction tun-
                                         sensor queries, trajectory planning, and other environment-       ing [24]. In contrast, poisoning the Function Library—the
                                         aware tasks [7].                                                  execution layer of the agent system—offers a stealthier and
                                             In practice, these Function Libraries are not monolithic      more persistent vector of attack. This raises the central
                                         or internally built components. Modern autonomous and             question of our work: Can we control multi-agent systems by
                                                                  2. Related Works
                                                                  2.1. Safety in Multi-Agent Systems
                                                                  As LLM-based multi-agent systems (MAS) gain promi-
                                                                  nence in real-world applications, ensuring their safety and
                                                                  robustness has become increasingly critical. Recent studies
                                                                  have begun to examine the vulnerabilities of MAS under
                                                                  adversarial conditions. Evil Geniuses [23] introduces an au-
      Figure 1: Existing vs. Our New Attack Surfaces.             tomated evaluation framework for analyzing the robustness
                                                                  of LLM-based multi-agent decision-making. Flooding [33]
subtly manipulating the function execution layer rather than      investigates the impact of injecting manipulated knowledge
the reasoning core? More critically, how far can a poisoned       into agents to degrade coordination performance, while
function propagate in a collaborative multi-agent setting?        PsySafe [24] explores psychologically-inspired attacks to
                                                                  induce adversarial behaviors within agents.
    To this end, we propose FuncPoison, a novel poisoning
                                                                      While these works highlight the security risks associ-
attack that targets the function-calling process in LLM-
                                                                  ated with inter-agent communication, knowledge contami-
based autonomous driving systems. By injecting malicious
                                                                  nation, and behavioral manipulation, they largely overlook
prompts into the function descriptions, FuncPoison exploits
                                                                  a critical component of MAS architectures: the function-
the templated nature of function calls to hijack agent ex-
                                                                  calling or function library. Despite its central role in agent-
ecution without modifying the model weights [25], [26]
                                                                  environment interaction and decision execution, the security
or prompt instructions [21], [27]. This enables (1) direct
                                                                  of this component has remained underexplored. Our work
manipulation of the victim agent’s outputs and (2) indirect
                                                                  addresses this overlooked threat by focusing on attacks
propagation of corrupted data to downstream agents in the
                                                                  targeting the function library, exposing a previously unrec-
decision pipeline.
                                                                  ognized yet highly impactful vulnerability in multi-agent
    Compared to existing poisoning attacks that primarily         autonomous driving systems.
target training data, memory, or retrieval components [28]–
[32], FuncPoison exhibits several critical advantages. First,     2.2. Poisoning Attacks
it achieves significantly higher attack success rates without     Poisoning attacks aim to manipulate model behavior by
relying on model retraining [27] or prompt overwriting.           injecting malicious content into training data [34]–[36],
Second, unlike prompt-injection-based methods which are           memory [37]–[39], or external resources [35], [40]–[43]. In
often easily detected or neutralized by defensive prompting       the context of large language models (LLMs), such attacks
or sanitization techniques, FuncPoison embeds its payload         have been developed across different system layers, each
in the function description field—a channel rarely inspected      targeting a distinct component of the LLM-based pipeline.
by conventional defenses. Third, our attack is highly con-            Input-layer poisoning is explored by methods like
trollable: it allows precise selection of injection points and    GCG [44]and AUTO DAN [45], which manipulate prompt
propagation routes (e.g., direct to Planning or via intermedi-    tokens or wrappers to inject adversarial content. However,
ate Memory and Reasoning agents), enabling both stealthy          their modifications are often semantically visible and vulner-
and persistent manipulation of multi-agent behavior.              able to prompt-level filtering or human inspection, especially
    We evaluate FuncPoison on two representative multi-           in safety-critical applications.
agent systems—AgentDriver and AgentThink—and demon-                   Model-level poisoning is exemplified by CPA [35],
strate attack success rates (ASR) exceeding 86%, even under       [46], which alters training samples to influence model
strong defense strategies such as instruction-level constraints   weights. While effective in controlled settings, such corpus-
and boundary awareness. Our findings reveal a previously          level attacks are typically detectable through data audits
overlooked attack surface in LLM-based systems and call for       or robust training techniques, limiting their applicability in
urgent re-valuation of trust assumptions around function-call     real-world systems.
infrastructure in safety-critical domains.                            Reasoning-layer poisoning [19], [47]–[49]is targeted
    Our contributions are as follows:                             by methods such as BAD C HAIN [50], which inject mis-
                                                                  leading prompts into intermediate reasoning steps or train-
  • We propose the first poisoning attack that targets the        of-thought chains. Yet these perturbations are often syntac-
    function-calling mechanism of LLM agents by manip-            tically or structurally abnormal—e.g., strange keywords or
    ulating only the function library.                            unnatural logic steps—making them detectable by simple
  • We demonstrate that manipulating the function calls of        reasoning sanitization or consistency checks.
    a single agent enables stealthy and precise control over          Memory-base poisoning is employed by AGENT P OI -
    downstream agents in a multi-agent system.                    SON [28], which contaminates the retrieved memory to intro-
  • We empirically evaluate our attack on two representa-         duce long-term behavioral drift. Nonetheless, these attacks
    tive autonomous driving systems, achieving over 86%           usually require planting large quantities of specific entries
    ASR and exposing critical security risks in real-world        into the memory base, making them costly and more prone
    settings.                                                     to being filtered by retrieval or ranking mechanisms.
     Supply-chain poisoning. Beyond traditional data and          sues a similar goal—subtle behavioral manipulation through
memory poisoning, a growing class of attacks compromise           crafted inputs. Here, the manipulation is embedded in the
the software distribution process itself—injecting malicious      function descriptions of the Function Library, which agents
content into external packages, dependencies, or libraries        later parse and execute. The resulting poisoned outputs act as
before they are integrated into target systems. Such supply-      implicit prompts for downstream agents, acting as an inter-
chain poisoning [12] has been repeatedly observed in real-        nalized form of prompt injection. Hence, our method can be
world ecosystems: the event-stream backdoor [51], [52] and        viewed as a covert and persistent variant of prompt injection,
the coa/rc compromises in the npm registry [13], [14], as         leveraging trusted function-call interfaces to bypass prompt-
well as typosquatting and credential-stealing packages [15]       level defenses and propagate across agents.
discovered in PyPI [16], have demonstrated how adversaries
can modify trusted modules during update or distribution          3. Preliminaries
phases. These attacks exploit the implicit trust between
developers and third-party package maintainers—once a             3.1. Function Call
malicious update is published, it propagates downstream au-       Function calling has emerged as a critical mechanism in
tomatically and executes under legitimate privileges. Recent      modern large language models (LLMs), enabling them to
reports on unverified module updates in ROS-based robotic         interface with external systems and perform real-world op-
frameworks [17], [18] further highlight that even safety-         erations. Traditional LLMs are limited to generating text
critical domains are vulnerable to such supply-chain com-         and reasoning over token sequences; they lack the ca-
promises. Inspired by these observations, our work treats         pacity to perform dynamic tasks like querying sensors or
the Function Library in multi-agent autonomous driving            executing motion commands. To overcome this limitation,
systems as a realistic supply-chain entry point: by inject-       recent frameworks such as OpenAI Function Calling [59],
ing poisoned function descriptions, adversaries can hijack        Toolformer [60], and ReAct [61] have introduced structured
function-call logic and manipulate agent behavior without         function call protocols.
touching model weights or prompts.                                    Fig. 2 illustrates function calling in LLM-based agent
     While these methods target different layers of the sys-      systems typically involves a two-stage interaction process:
tem—including data, reasoning, memory, and even the soft-             The LLM agent first receives a guiding prompt, such as:
ware supply chain—they all suffer from practical limi-
tations—some are detached from real-world deployment                Do you need to perform detections from the driving
scenarios, while others are less effective under defensive          scenario?
conditions. Each approach faces its own weaknesses, making
them insufficient for attacking robust, multi-agent systems.          Upon replying “YES”, the system provides a list of
     To address these limitations, we propose FuncPoison, a       available functions with their descriptions:
novel attack operating at the function-calling layer. Instead
of modifying prompts or training data, we inject malicious          get leading object detection()
content directly into the shared function descriptions in           # Get the detection of the leading
the system’s Function Library. These poisoned definitions           object
mimic legitimate function call formats, hijacking the func-         get future trajectories for specific objects()
tion selection logic and misleading agents into executing           # Get future trajectories
attacker-specified behaviors. This approach bypasses tradi-
tional semantic defenses and exploits the template-driven             Based on the presented descriptions, the agent generates
execution pipeline of LLM-based multi-agent systems, en-          a structured call output:
abling stealthy and cross-agent manipulation.
2.3. Prompt Injection Attacks                                       {
Instruction-following language models have been shown to                "function_call":
be vulnerable to prompt injection attacks [53]–[57], where              "name":"get_future_trajectories_for
malicious inputs are crafted to manipulate the model’s be-              _specific _objects",
havior [21], [27]. Such attacks can influence downstream                "arguments": {"object_ids": [2, 3]}
reasoning or decision-making without altering the model             }
weights themselves. Recent studies have further extended
prompt injection to LLM-driven applications, including in-            This output is interpreted and executed by a backend
teractive agents and embodied systems [58].                       system. The returned result (e.g., future trajectories) is fed
    However, most prompt injections depend on visible             back to the LLM’s context for further reasoning. This loop
wrapper prompts that are increasingly detectable by filters.      enables LLMs to act as controllers in dynamic environments.
They also act only at the initial input stage and thus have           As systems scale, these functions are typically organized
limited influence in structured multi-agent pipelines that rely   into a centralized Function Library—a structured repository
heavily on intermediate tool outputs.                             of callable routines for maintainability and reuse. For in-
    Our attack does not alter prompts directly, but pur-          stance:
Figure 2: Function Call pipeline: (1) Function Choose, where the agent selects a tool from the Function Library based on
prompt intent; (2) Function Output, where the agent executes the selected function in a structured template and receives
results.


  -get around object detection()                                and Planning—that communicate via structured outputs to
  #Get the detection of around objects                          complete the decision-making pipeline.
  -get leading object detection()                                   As shown in Fig. 3, the Perception Agent initiates each
  #Get the detection of the leading                             cycle by issuing a Function Call to a centralized Function
  objects                                                       Library, retrieving environment data through sensor func-
  -get future trajectories()#......                             tions. The resulting Perception Result is propagated along
                                                                two paths: one to the Planning Agent for fast response, and
    This shift from scattered individual calls to a consol-     the other to the Memory Agent, which processes it into a
idated library reflects practical needs for organizing and      Memory Result using historical or rule-based context.
scaling agent capabilities. The Function Library streamlines        The Reasoning Agent then integrates both outputs to
how agents access callable routines but does not introduce      generate a Reasoning Result, which is finally passed to the
new modular interfaces or shared abstraction layers across      Planning Agent to produce the final Planning Result.
agents. However, since function selection is based on nat-          This modular pipeline enables decomposed reasoning
ural language descriptions, attackers can exploit this by       but also creates a critical vulnerability: all downstream
injecting adversarially-crafted functions that mimic template   decisions depend on the correctness of the initial Function
formats—deceiving agents into selecting malicious calls.        Call. A single malicious function in the library can compro-
This vulnerability underpins the attack mechanism proposed      mise the Perception Result, mislead Memory and Reasoning
in FuncPoison.                                                  Agents, and ultimately hijack the system’s driving decision.
3.2. Multi-Agent System for Autonomous Driving                  3.2.2. AgentThink
                                                                AgentThink is another representative multi-agent system
Recent advances in Large Language Models (LLMs) have
                                                                for autonomous driving, originally proposed as a vision-
enabled the construction of modular multi-agent systems for
                                                                language model (VLM) framework. In our work, we mod-
autonomous driving, where each agent—instantiated from
                                                                ularize its architecture into alternating Thinking Agents and
an LLM—handles a specific subtask (e.g., perception, rea-
                                                                Function Agents, each instantiated by an LLM and paired
soning, planning). These agents communicate via structured
                                                                for reasoning and execution.
prompts and outputs, and often rely on a centralized Func-
                                                                    As shown in Fig. 3, the system processes surrounding
tion Library to invoke external tools through standardized
                                                                information through a chain of reasoning–calling–response
Function Calls. This design supports flexible task decompo-
                                                                loops: each Thinking Agent performs semantic reasoning
sition and interpretable decision-making, but also introduces
                                                                and instructs its paired Function Agent to execute specific
a new attack surface: any tampering of function definitions
                                                                operations via Function Calls from a shared Function
or invocation patterns can affect downstream agents through
                                                                Library. The Function Agent executes the call and returns
the inter-agent communication chain.
                                                                the result to the Thinking Agent for the next stage of
     In the following subsections, we introduce two rep-
                                                                reasoning. This loop continues across multiple stages until
resentative instantiations of such LLM-based multi-agent
                                                                the final Thinking Agent outputs the Planning Result for
systems for autonomous driving: AgentDriver [8], which
                                                                vehicle control.
emphasizes information propagation and inter-agent coordi-
                                                                    While this architecture supports modularity and inter-
nation; and AgentThink [11], which structures the pipeline
                                                                pretability, it also places critical trust in the integrity of each
as alternating chains of reasoning and execution agents.
                                                                Function Call. Any malicious or misleading function in-
3.2.1. AgentDriver                                              jected into the Function Library can manipulate intermediate
AgentDriver is a representative LLM-based multi-agent           outputs and propagate errors throughout the entire reasoning
architecture for autonomous driving. The system consists        chain. This makes AgentThink particularly susceptible to
of four specialized agents—Perception, Memory, Reasoning,       stealthy attacks that exploit function-level vulnerabilities.
Figure 3: Architecture of two representative Autonomous Driving Multi-Agent Systems: AgentDriver is composed of
four specialized agents—Perception, Memory, Reasoning, and Planning—that collaborate through a sequential information
pipeline. In contrast, AgentThink adopts an alternating chain of Thinking and Function agents to accomplish decision-making
in a chain-of-thought (CoT) manner.


3.3. Attack Scenario and Threat Model                            4. FuncPoison
In multi-agent autonomous driving systems, LLM-based             Before introducing the full attack pipeline of FuncPoison,
agents interact with external tools via structured function      we first dissect the underlying causes that make LLM-based
calls to a shared Function Library. These libraries typi-        multi-agent systems vulnerable to function-level poisoning.
cally aggregate perception utilities, mapping services, and      These insights are not only foundational for our attack
planning routines that are described in natural language         design, but also highlight a broader class of risks introduced
and invoked through templated prompts. While this mod-           by function-call-based interactions.
ular design improves flexibility and reuse, it also creates          Specifically, we identify three critical factors that enable
a trusted execution layer that downstream agents rely on         successful hijacking of agent behavior: structural vulner-
during runtime.                                                  abilities in function call selection, template-constrained
    We consider an adversary who compromises the Func-           invocation behavior at the functional level, and model-
tion Library at supply side—before its integration into the      level biases rooted in instruction tuning. We analyze these
target system—by injecting new poisoned functions or sub-        issues below to motivate the core design choices of our
tly modifying the description fields of existing functions.      attack.
Such manipulations occur only at the supply stage (e.g.,
within third-party packages, vendor toolkits, or repository      4.1. Security Vulnerabilities
updates) and are fixed once the system is deployed, en-          The Function Call mechanism in LLM-based Multi-Agent
suring that the library content remains immutable at run-        Systems presents two major vulnerabilities, both of which
time. Because poisoned entries preserve legitimate names,        are exploited by FuncPoison. In addition, when Function
signatures, and input/output schemas, they are likely to be      Call interacts with instruction-tuned LLMs, it introduces
accepted as valid and executed under normal trust assump-        a further model-level weakness: a systematic bias toward
tions.                                                           template-conforming descriptions. Together, these three vul-
Attacker’s goal. The attacker aims to induce covert and          nerabilities form the functional and behavioral basis that
controllable misbehavior in the multi-agent pipeline—e.g.,       allows FuncPoison to hijack system execution in a reliable
trajectory deviations, omitted obstacle detections, or reason-   and persistent manner.
ing biases—while maintaining surface-level plausibility so           (1) Function Selection Dependency on Descriptions:
that outputs appear benign to simple monitors or human           When an agent is prompted to select a function, it relies
supervisors. The intent is to manipulate runtime execution       entirely on the textual descriptions provided in the function
without altering model parameters, prompts, system archi-        library. If these descriptions are poisoned—i.e., contain tem-
tecture, and without accessing the function library during       plated examples that resemble legitimate function calls—the
runtime.                                                         LLM may misinterpret them as in-context demonstrations.
Attacker’s capabilities. The adversary can (1) modify            This implicit injection can cause the agent to prefer the
Function Library artifacts at supply side by injecting or        malicious function, bypassing semantic reasoning. Impor-
replacing function entries and/or their description fields;      tantly, since this injection originates from internal function
(2) craft poisoned entries preserving interface compatibility    metadata, it evades standard prompt injection defenses.
(names, argument schemas, return formats) to avoid immedi-           (2) Template-Constrained Invocation Behavior: Once
ate integration failures; and (3) embed template-conforming      a function is selected, the agent typically generates a tem-
invocation examples or semantically misleading descriptions      plated function-call output. If the poisoned description in-
to bias function selection and templated invocation behavior.    cludes a similar format, it can bias the LLM into replicating
Crucially, the adversary does not possess access to model        that template, reinforcing the malicious selection and call.
weights, system prompts, or runtime privileges.                  This templated behavior lowers robustness, as the agent
Figure 4: Overview of FuncPoison: Our attack injects forged function calls into the prompt and manipulates specific functions
in the function library, enabling control over downstream agents.


is incentivized to repeat observed structures rather than          pering with the shared Function Library. The core idea is
perform true inference.                                            to embed adversarial prompt patterns, particularly function-
     (3) Model-Level Behavioral Biases: FuncPoison also            call templates, into the textual descriptions of malicious
exploits behavioral biases that arise from instruction tuning      functions. When an agent consults the function library to
and in-context learning. Instruction-tuned LLMs tend to pre-       choose which function to invoke, these carefully crafted
fer inputs that conform to familiar structural patterns, partic-   descriptions act as misleading in-context examples, guiding
ularly in templated or tool-augmented settings. Concretely,        the LLM to mistakenly select and invoke the poisoned
when presented with a list of candidate functions, agents          function. Once invoked, the function produces controlled
often favor descriptions that resemble invocation templates        outputs that alter the agent’s behavior. The attack unfolds
even when those entries are semantically less relevant. This       in three coordinated stages: Poisoning and Hijacking: The
inductive bias directly reinforces vulnerability (2): embed-       attacker injects malicious functions into the function library
ding templated call patterns into function descriptions aligns     by embedding imitation-style prompts in the function de-
with the model’s learned expectations and nudges the agent         scriptions. These templates mimic common Function Call
to select the option that “looks like” a valid invocation.         patterns to mislead the LLM into favoring the malicious
In effect, the poisoned function serves as a suggested in-         function during function selection. Function Call and Ma-
context example, and the model’s preference for format             nipulating: Once hijacked, the agent invokes the poisoned
over semantics makes the system especially susceptible to          function, whose output is crafted to manipulate the agent’s
maliciously structured metadata.                                   reasoning and final response. Spread and Affect Other
     In summary, the first two issues constitute the functional    Agents: The manipulated output propagates to downstream
foundation of FuncPoison, enabling it to hijack the function       agents via structured inter-agent communication. This cross-
selection and invocation pipeline, while the third issue am-       agent propagation leads to systemic misbehavior, even if
plifies this risk at the model level, ensuring template-injected   only one agent is compromised. As we will demonstrate,
functions are consistently favored and the attack remains          FuncPoison introduces cross-agent destructiveness while
both effective and persistent.                                     maintaining stealth and specificity. The following sections
4.2. Attack Overview                                               analyze the detail of the methodology of our attack pipeline.
We propose FuncPoison, the first function-level poison-            4.3. Attack Pipeline
ing attack targeting LLM-based Multi-Agent Systems for             Stage 1: Poisoning and Hijacking. The first stage of
Autonomous Driving. Unlike traditional data poisoning or           our attack targets the function selection mechanism within
prompt injection techniques, FuncPoison exploits the core          the agent system. Existing multi-agent autonomous driving
architectural component of these systems—the Function              systems often assume that function selection is based on
Call mechanism—and manipulates agent behavior by tam-              the semantic relevance of function descriptions and the
agent’s reasoning capabilities. This process implicitly trusts     proceeds to invoke the poisoned function that we injected
the integrity of the function library.                             into the Function Library. This malicious function is not a
     FuncPoison breaks this assumption by injecting ma-            genuine tool utility, but a payload crafted by the attacker. It
licious function definitions into the centralized Function         mimics legitimate functions in interface and format but is
Library. These poisoned functions are carefully crafted            engineered to return adversarially controlled outputs.
such that their description fields not only explain their              This function call manipulates the agent’s output
utility, but also embed templated function call prompts            at its root. Instead of producing an honest interpretation
that mimic the system’s own invocation format.                     of environmental information, the agent’s behavior is now
                                                                   dictated by the poisoned function’s response. As shown
  malicious get object()                                           below, the function call may appear structurally normal:
  #To get object location, call:
    {                                                                {
       "name": "malicious_get_object",                                   "function_call": {
       "arguments": { "id": 5 }                                            "name": "malicious_get_object",
    }                                                                      "arguments": {"id": 5}
                                                                           }
    When the agent scans available functions, this descrip-          }
tion prompt acts as a behavioral trigger. It imitates
legitimate function call patterns and exploits the templated            However, because the function is malicious by design,
nature of the agent’s function selection logic. As a result,       its output is also adversarial. This leads the agent to generate
the agent may be unintentionally “hijacked” into selecting         misleading or harmful conclusions—such as claiming no
and invoking the malicious function, without realizing the         obstacles are present when they actually are.
abnormality.                                                       Manipulating outputs enables control over agents. In
    As illustrated in Fig. 4, this stage contains two critical     LLM-based multi-agent systems, each agent’s reasoning is
substeps: poisoning the library with maliciously crafted           built upon its own outputs and the outputs of prior agents.
functions, and hijacking the agent’s function selection pro-       When an agent is deceived into calling a poisoned function,
cess via prompt mimicry embedded within the function               its entire reasoning process is effectively hijacked. Since its
descriptions.                                                      final output is directly shaped by the function’s return, the
    This allows the attacker to achieve initial foothold, ef-      agent itself becomes a vehicle for adversarial influence.
fectively redirecting the agent’s behavior by corrupting the       From Local Control to Systemic Spread. This manipu-
seemingly benign function library..                                lated output is not confined to the attacked agent alone. It
    This stage of the attack works due to two fundamental          becomes the input to downstream agents—Memory, Reason-
vulnerabilities identified in the function call pipeline:          ing, Planning—each of which treats the received information
   • V1 – Description Injection: The agent relies solely           as trusted and grounded. Consequently, a single poisoned
      on the Function Library to display available func-           function call can alter the trajectory of the entire system.
      tion options. Thus, any injected content within the               Fig. 4 illuatrates this chain reaction reveals the structural
      description field will be rendered to the agent              amplification effect: controlling one function enables the
      during function selection. This allows the attacker to       attacker to dominate an entire agent pipeline’s behavior.
      control what the agent sees and how it interprets func-      Stage 3: Spread and Affect Other Agents. Once an
      tion’s purpose.                                              agent has been hijacked and manipulated by a poisoned
   • V2 – Template Exploitation: Function invocation in            function, the consequences do not remain localized—they
      many systems follows a rigid, templated format (e.g.,        propagate structurally throughout the system. In multi-agent
      {"name": ..., "arguments": ...}). By em-                     architectures, where each agent’s output serves as the input
      bedding this format directly into the function descrip-      to subsequent agents, even a single malicious output can
      tion, the attacker exploits the agent’s tendency to repli-   cascade through the entire decision pipeline, triggering long-
      cate observed call patterns, turning static metadata into    range effects.
      executable influence.                                             As shown in Fig. 4, the contaminated output becomes
    By combining these two vulnerabilities, the attacker           part of the system’s internal context, feeding future rea-
transforms a descriptive field—intended solely for clari-          soning steps and impacting downstream function selection.
fication—into a behavioral trigger that biases the agent’s         At each stage, the misinformed agent generates its own
decision-making process. In effect, the agent sees the poi-        structured output, which is then trusted by other agents.
soned function not just as a viable option, but as an already-     These outputs are not discarded; they persist, accumulate,
recommended or frequently-used function. This subtle yet           and shape subsequent decisions, compounding the effect of
powerful manipulation is what enables hijacking during the         the original malicious function call.
function selection stage, even without access to the agent’s            This architectural behavior forms a powerful amplifica-
internal logic or explicit control over its reasoning path.        tion loop: the longer the poisoned output remains in the
Stage 2: Function Call and Manipulating. After suc-                system, the more distorted the overall decision becomes. In
cessfully hijacking the function selection process, the agent      particular, this differs significantly from traditional prompt
injection attacks, which typically affect a model’s interpre-        FuncPoison leverages three unique properties that render
tation of external user inputs. In contrast, our attack poi-    traditional defenses ineffective:
sons the system-generated outputs—namely, the responses            • Internal Attack Surface: The poisoned content resides
of internal agents—causing the system to attack itself from           within the trusted function library, bypassing external
within. The malicious signal is no longer limited to a single         input filters.
point of entry; it is continuously regenerated by internal         • Invisible Propagation: The attack moves through in-
components, making it highly persistent and difficult to              termediate outputs and agent memory, rarely surfacing
detect or remove.                                                     as anomalous behavior.
    Spread in AgentDriver. The AgentDriver framework               • Infectious Chaining: Each compromised agent propa-
features a sequential chain of agents—Perception, Memory,             gates tainted outputs to downstream agents, amplifying
Reasoning, and Planning. Once the Perception Agent is                 the impact system-wide.
compromised via a poisoned function (e.g., misleading sen-           We now analyze why three major defense
sor output), its result is immediately propagated to the Mem-   categories—prompt-based, agent-based, and model-
ory Agent and the Planning Agent. The Memory Agent,             based—fail to stop FuncPoison, each in light of these three
unaware of the corruption, generates a Memory Result that       attack characteristics.
is based on already-tampered inputs. These outputs are                   Prompt Injection Defenses: Designed for External
then forwarded to the Reasoning Agent, which generates          Threats. Prompt-level defenses such as input sanitization,
a high-level reasoning output. Finally, the Planning Agent      paraphrasing, or instruction wrapping are primarily designed
consumes all prior outputs to compute the driving action.       under the assumption that malicious content originates from
    This linear propagation structure ensures that each stage   user-facing inputs. However, FuncPoison embeds malicious
multiplies the distortion from the previous stage. A mali-      payloads directly within the system’s own Function Li-
cious output at the start of the pipeline will affect every     brary—specifically in the description fields of func-
subsequent decision, culminating in a severely distorted        tions—which are automatically surfaced to agents during
or unsafe Planning Result. The fact that each agent trusts      function selection.
prior outputs makes this structure particularly vulnerable to        Since these poisoned descriptions are not part of any
cascading failures.                                             external prompt, they bypass all input sanitizers and seman-
    Spread in AgentThink. The AgentThink framework              tic filters. The system, in effect, is attacking itself using
uses a looped architecture of alternating Thinking Agents       internally trusted components. Moreover, because the entire
and Function Agents. At each stage, a Thinking Agent issues     function selection and execution process is often invisible
a function call, receives the result, and produces a new        to users, logs, or monitoring tools, the root cause remains
structured output that feeds into the next stage’s Thinking     deeply buried. The only visible symptom might be a benign-
Agent. Once a poisoned function is invoked by any Function      looking output—such as a misclassified object—from a
Agent, the resulting output is returned to the Thinking         downstream agent, making diagnosis nearly impossible.
Agent, which integrates it into its semantic reasoning. This             Agent Chain Defenses: Misled by Apparent Normal-
new output then influences the next function call.              ity. Multi-agent systems sometimes use behavioral consis-
                                                                tency checks—verifying reasoning paths or flagging con-
    Function Agents operate under the assumption that prior     tradictory outputs. These mechanisms are effective when an
outputs are trustworthy, this looping mechanism creates a re-   agent acts abnormally such as deviating from a logical chain
cursive propagation path. The adversarial signal is embedded    of thought.
deeper into the decision chain with every loop, amplifying           However, FuncPoison does not cause agents to break
its effect while maintaining structural legitimacy.             logical structure. The poisoned function is selected through
    In both systems, this multi-stage propagation showcases     the normal process, its output is syntactically correct, and
a systemic vulnerability: the attack not only affects a         each downstream agent behaves as expected—except that
single component but induces an auto-propagating error path     its input has been subtly corrupted. The manipulation lies
throughout the entire architecture. It turns each agent into    not in the agent’s reasoning logic but in its trusted inputs.
an unwilling amplifier of adversarial behavior, rendering       Because all components behave formally correctly, chain-
conventional input-level defenses ineffective.                  level validators and reasoning monitors remain silent—even
                                                                as the entire pipeline drifts from its original intention.
4.4. Why Existing Defenses Fail
                                                                         Model-Level Defenses: Focused on Output, Blind to
FuncPoison remains effective against various defense strate-    Context. Some defenses align LLM outputs via fine-tuning,
gies proposed for LLM-based systems—including prompt            decoding constraints, or safety filters. While useful in con-
sanitization, agent verification, and model alignment. The      trolling open-ended generations, these defenses assume the
root cause is a fundamental mismatch between these de-          model’s behavior is shaped purely by its decoding process.
fenses assumptions and our attack nature. While traditional          In contrast, agents in multi-agent systems are heav-
defenses focus on guarding against external threats—such as     ily conditioned on structured prompts, tool templates, and
user-input prompt injection or agent outputs—FuncPoison         function outputs. Since FuncPoison manipulates the very
operates entirely internally, propagates invisibly, and         structure of these contextual inputs—embedding templated
spreads through trusted communication channels.                 payloads in function descriptions—the model simply follows
its learned behavior and selects the poisoned function. Even       6,000 for validation, covering diverse urban conditions. Each
a well-aligned LLM, misleading internal context, will faith-       scene includes a 3-second future trajectory as the ground
fully execute unsafe calls. These structural manipulations lie     truth, paired with a surrounding environment data. These
beyond the scope of most LLM-alignment techniques.                 inputs are used to guide function calls and inform trajectory
     In summary, traditional defenses fail not due to a lack       planning.
of coverage, but due to misaligned assumptions about where         Metrics. To evaluate our attack, we adopt two widely used
threats originate. FuncPoison redefines the threat model: it       metrics from autonomous driving systems—L2 Distance and
weaponizes trusted system components, disguises its propa-         Collision Rate—as well as a new metric we develop to
gation within legitimate agent interactions, and compromises       quantify attack effectiveness: Attack Success Rate (ASR).
behavior without violating logic. This underscores the need            L2 Distance measures the deviation between the pre-
for new defense paradigms that scrutinize internal function        dicted trajectory and the human reference trajectory. For
calls, not just surface prompts or final outputs.                  each timestep t, the distance is computed as:
                                                                                        p
5. Experiments                                                                   L2t = (x̂t − xt )2 + (ŷt − yt )2 ,         (1)
5.1. Setup                                                         where x̂t and xt denote the predicted and reference posi-
Systems. Existing LLM-driven multi-agent systems for au-           tions, respectively. We report the average L2 values over
tonomous driving predominantly adopt sequential, pipeline-         1s, 2s, and 3s time horizons. Lower values indicate better
style architectures in which module outputs are consumed           alignment with human-like driving, which is considered the
by downstream components; this pattern is widely ob-               standard for safe autonomous behavior.
served in recent literature and surveys of LLM-based driving           Collision Rate (abbreviated as Coll.) measures the
agents [9], [62]. To evaluate our attack, we adopt two rep-        safety of the predicted trajectories by computing the pro-
resentative systems: AgentDriver and AgentThink. Both              portion of cases where the predicted path intersects with
systems utilize function-call-based interactions and exhibit       any surrounding object:
complex inter-agent communication, making them ideal tar-
gets to study cross-agent propagation of poisoned outputs.                               #collided trajectories
                                                                                  CR =                          ,             (2)
    AgentDriver is a modular multi-agent system composed                                  #total trajectories
of four specialized agents: a Perception Agent, a Memory           which reflects the system’s ability to avoid unsafe decisions
Agent, a Reasoning Agent, and a Planning Agent. These              in complex environments.
agents are fine-tuned from GPT-3.5 using task-specific                 Attack Success Rate (ASR) quantifies the effectiveness
prompts and training data derived from expert-labeled tra-         of adversarial attacks. For each scenario i, an attack is con-
jectories in the nuScenes dataset. The Perception Agent is         sidered successful if it either causes a collision or induces
solely responsible for interacting with a shared Function Li-      a deviation exceeding a threshold δ :
brary, issuing queries to perception-related tools (e.g., detec-                      h                              i
tion and trajectory prediction). Other agents only consume                                       (i)
                                                                          ASRi = 1 max L2t > δ ∨ collision(i) ,               (3)
intermediate results through a lightweight publish–subscribe                              t
flow and do not access the Function Library directly. This         and the overall ASR across N scenarios is computed as:
design makes AgentDriver particularly vulnerable to our
                                                                                                   N
attack: once a poisoned function is invoked, its manipulated                                1 X
outputs propagate through the chain and affect the final                              ASR =       ASRi ,                      (4)
                                                                                            N i=1
planning outcome.
    AgentThink is a chain-of-thought style autonomous              capturing both trajectory divergence and safety violations,
driving framework built upon a VLM. For our experiments,           and providing a comprehensive assessment of the adversarial
we refactor this architecture into a multi-agent system by         impact on system performance.
decomposing its monolithic logic into alternating Function         Baseline Attacks. To evaluate the effectiveness of our
Agents and Thought Agents. Function Agent select and               approach, we compare it against five representative base-
execute external functions, while Thought Agent interprets         lines, each exploiting different vulnerabilities in LLM-based
the result and determines the next step in the reasoning           systems. Several of these methods are also categorized as
process. This iterative reasoning structure forms a function-      poisoning attacks, but differ in their targets and delivery
thought-function chain that resembles high-level cognitive         mechanisms.
planning. Because function selection relies entirely on nat-           Greedy Coordinate Gradient (GCG) [44] is a black-
ural language, AgentThink becomes especially susceptible           box jailbreak technique that constructs adversarial suffixes
to template-style hijacking in poisoned function definitions.      via greedy token optimization. It targets the model’s prompt
Datasets. We conduct experiments on the nuScenes dataset,          alignment behavior without requiring model weights or gra-
a widely used benchmark for urban autonomous driving.              dients. Although not a poisoning method in the traditional
It consists of 1,000 driving scenes collected in Boston and        sense, it effectively manipulates model outputs at runtime.
Singapore, each lasting 20 seconds and captured using six              AutoDAN (Automatic Discrete Adversarial Prompts)
cameras, five radars, one LIDAR, GPS, and IMU. From                uses reinforcement learning to learn prompt wrappers that
this dataset, we select over 28,000 scenes for training and        lead to undesired completions. While it operates during
      TABLE 1: Attacks on AgentDriver.                                                TABLE 2: Attacks on AgentThink.
 Method         L2     Coll.   ASR@L2=3     ASR@L2=6
                                                                                  Method        L2    Coll.   ASR@3     ASR@6
 no attack     1.46    0.25       15.5           2.5
                                                                                  no attack    1.57   0.31     16.3      2.37
 GCG           1.85    0.35       18.5           5.6
                                                                                  GCG          2.32   0.43     22.8      8.00
 AutoDan       3.21    1.73       55.6          17.3
                                                                                  AutoDan      2.88   0.78     45.4      13.6
 CPA           3.35    1.70       56.8          20.7
                                                                                  CPA          3.63   1.95     60.7      26.9
 Bad Chain     2.77    0.83       43.2          23.4
                                                                                  Bad Chain    3.17   1.53     50.3      24.1
 AgentPoison   8.47    3.56       80.6          50.6
                                                                                  FuncPoison   9.86   3.57     84.2      79.5
 FuncPoison    10.52   4.58       86.3          82.3




Figure 5: Attack performance on AgentDriver (L2                            Figure 6: Attack performance on AgentThink (L2
threshold=3).                                                              threshold=3).


          TABLE 3: Comparison of attack methods                    TABLE 4: Injection Strategy Design: Function Description
 Attack Method         Poisoning Target         System Layer       Types
 GCG                   Prompt Tokens            Input Layer                  Description                         Call
                                                                    Category                   Example                   ASR@L2=3
 AutoDAN               Prompt Wrapper           Input Layer                  Strategy                            Rate
                                                                             Normal            Get future
 CPA                   Training Samples         Model Weights       Baseline description,      trajectories     18.3%     15.5%
 Bad Chain             Chain-of-Thought Steps   Reasoning Layer              no injection      of objects.
 Agent Poison          Memory / Tool Outputs    Memory Base                  Insert            Get future
                                                                   Semantic
 FuncPoison (Ours)     Function Descriptions    Function Library             misleading        trajectories
                                                                   Manipula-
                                                                             semantic          assuming no
                                                                                                                34.5%     32.8%
                                                                      tion
                                                                             statements        obstacles.
inference, its effect mimics a form of prompt-level poisoning                                  To get
by persistently altering model behavior across tasks.                           Embed          trajectories,
                                                                    Template
    Corpus Poisoning Attack (CPA) embeds malicious ex-              Injection
                                                                                function-      call:
                                                                                                                 98%      86.3%
amples into pretraining/fine-tuning corpora to implant model                    call-style     {"name":
                                                                     (Ours)
                                                                                templates      "...",
biases/backdoors, targeting the training pipeline with wide-                                   "args": ...}
ranging downstream effects.
    Bad Chain targets the model’s reasoning process via            compromised, with poisoned entries achieving very high call
Chain-of-Thought (CoT) manipulation. By inserting flawed           rates and ASR. Building on this mechanism-level evidence,
logical steps into intermediate prompts, it “poisons” the          we then evaluate the end-to-end impact of FuncPoison com-
reasoning trajectory and drives the model toward incorrect         pared to baseline attacks.
outputs, even when final prompts appear well-formed.               Mechanism-level validation experiment: template bias in
    AgentPoison poisons the system’s memory base by in-            function selection
serting optimized trigger–target pairs, increasing the chance
                                                                   As discussed in methodology, our attack leverages a
of retrieving malicious entries and inducing long-term be-
                                                                   model-level behavioral bias observed in instruction-tuned
havioral bias in downstream agents.
                                                                   LLMs—agents tend to prefer function descriptions that
5.2. Attack Effectiveness: Comparison with Baseline At-            conform to structured invocation templates. To empirically
tacks                                                              validate this hypothesis, we conduct a mechanism-level val-
We begin by presenting a preliminary experiment on                 idation experiment within the AgentDriver system, where
function-call selection bias, designed to validate that            we modify its Function Library to include three types of
template-style descriptions inserted into the Function Li-         function descriptions. We evaluate each description style in
brary can reliably control which function the agent chooses.       terms of its function call rate and attack success rate (ASR),
This front-loaded test demonstrates that, under our template-      as shown in Table 4.
injection setting, the function selection step itself becomes          This mechanism-level validation confirms template-style
descriptions are selected far more frequently and yield            5.3. Attack Robustness: ASR under different seeds,
substantially higher attack success rates than both base-          Model-cores and L2 Thresholds
line and semantic-only modifications. In other words,              5.3.1. ASR under different seeds
the function-selection step effectively hijacked under our
                                                                   To evaluate whether FuncPoison depends on specific
template-injection setting: poisoned function entries behave
                                                                   function-insertion locations, we repeat the attack under five
like in-context examples and are systematically favored
                                                                   random seeds. Each seed corresponds to a distinct placement
by the agent during invocation. These results validate the
                                                                   of poisoned functions within the Function Library, while
Template-Constrained Invocation Behavior hypothesized in
                                                                   keeping all other experimental factors identical: same sce-
the methodology and provide a causal explanation for why
                                                                   narios, same number of poisoned functions, same prompts
template-based poisoning yields stronger downstream ef-
                                                                   and temperatures, and the same evaluation protocol.
fects.
                                                                       Across the five seeds, FuncPoison achieves a consis-
                                                                   tently high level of attack success, with an average ASR of
    Building on the mechanism-level finding above, we eval-
                                                                   86.3% ± 3.0%. The small variance across different inser-
uate the end-to-end impact of these attacks on system perfor-
                                                                   tion placements indicates that the attack does not rely on any
mance. Specifically, we compare our proposed FuncPoison
                                                                   particular position in the Function Library, demonstrating
against five representative baselines across two systems:
                                                                   strong robustness.
AgentDriver and AgentThink.
                                                                       Across five independent insertion seeds, FuncPoison
    All attacks are applied under identical input conditions       yields ASR = 86.3% ± 3.0% while AgentPoison yields
and evaluated using three complementary metrics: L2 Dis-           ASR = 80.5% ± 2.0%. A two-sided Welch t-test on
tance (3s average), Collision Rate(Coll.), and Attack Success      per-seed ASR values shows the difference is statistically
Rate (ASR) under thresholds of 3 m and 6 m. These ASR              significant (t = 3.52, df = 6.9, p = 0.009), indicating the
thresholds capture both fine-grained (3 m) and moderate (6         improvement is unlikely due to random seed variation.
m) deviations, which roughly correspond to crossing one            5.3.2. ASR under different Model-cores
or two full traffic lanes in real urban environments—an            To evaluate model-core generalization, we replace the LLM
intuitive proxy for safety-critical violations. This enables a     backbone used by each agent while keeping the rest of the
nuanced analysis of the system’s vulnerability. The results        pipeline identical. This isolates the effect of the model core
are summarized in Tables 1–2 and Fig. 5–6.                         on attack success. We report results for three representa-
                                                                   tive cores: GPT-3.5 (baseline), GPT-4.0 (higher-capability
    FuncPoison consistently achieves the highest impact            model), and LLaMA 3 (open-source backbone).
across all metrics and both systems. On AgentDriver,                   The results show minimal differences across models:
FuncPoison reaches an average L2 distance of 10.52, sig-           ASR remains 86.3% ± 3.0% using GPT-3.5, 85.6% ±
nificantly surpassing AgentPoison (8.47), and increases the        5.0% using GPT-4.0, and 90.0% ± 2.0% using LLaMA
collision rate to 4.58%. Similarly, on AgentThink, FuncPoi-        3. These results indicate that FuncPoison remains highly
son yields an L2 of 9.86 and a collision rate of 3.57              effective regardless of the LLM core, demonstrating strong
In terms of attack success rate, FuncPoison achieves an            model-level robustness.
ASR@3 of 86.3% and ASR@6 of 82.3% on AgentDriver,
as shown in Fig. 5. This reflects a notable improvement            5.3.3. ASR under increasing L2 thresholds
over AgentPoison (80.6%) and prompt-level attacks like             To evaluate robustness under varying safety criteria, we
AutoDan (55.6%). On AgentThink, FuncPoison similarly               increase the L2 distance threshold from 1 to 20 meters and
dominates with ASR@3 of 84.2% and ASR@6 of 79.5%,                  measure the ASR. Higher thresholds permit larger deviations
as visualized in Fig. 6.                                           between predicted and reference trajectories before an attack
                                                                   is considered successful. All other inputs, model states, and
    Compared to prompt-based attacks (GCG, AutoDan),               attack prompts are held constant. We focus on the direct
FuncPoison benefits from deeper integration into the sys-          attack setting, where poisoned function outputs immediately
tem’s functional infrastructure, subverting behavior more          influence the final Planning Agent. As the L2 threshold
persistently. Unlike CPA or Bad Chain, which rely on               increases, the system tolerates larger deviation, improving
training-time or reasoning-level manipulation, FuncPoison          benign accuracy and reducing ASR.This provides a baseline
injects adversarial behavior directly into the function call in-   for understanding FuncPoison-induced deviations’ persis-
terface. This misleads early-stage perception modules (e.g.,       tence under relaxed constraints.
via poisoned detection tools), while maintaining legitimate            Fig. 7 shows the accuracy rapidly improves as the system
agent communication patterns—making it more effective              becomes more tolerant to deviation, reaching over 95% once
and stealthy.                                                      the threshold exceeds 6 meters. This reflects the inherent
                                                                   resilience of the driving system to small prediction errors.
    Overall, results demonstrate that function-level poison-           Fig. 8 shows that, unlike benign accuracy, which steadily
ing via FuncPoison achieves stronger behavioral divergence,        improves, FuncPoison maintains high ASR across a broad
higher safety risk, and more consistent attack success across      range of thresholds: above 80% up to around 8 meters and
modular and reasoning-centric autonomous driving systems.          declining gradually beyond 10 meters. This indicates that
      Figure 7: System accuracy under varying L2                     Figure 8: Direct Attack: ASR under varying L2
      thresholds.                                                    thresholds.


the attack induces trajectory shifts exceeding both strict and    5.5. Attack Stealth and Persistence: Bypassing Prompt-
moderately relaxed safety margins.                                level and Agent-level Defenses
    Even under relaxed thresholds, the attack continues to        To evaluate the stealth and persistence of FuncPoison, we
produce non-trivial deviations, confirming its persistence.       deploy it under two propagation styles (direct and indirect)
                                                                  within the AgentDriver system and measure its success
    Overall, FuncPoison remains effective across broad
                                                                  rate when combined with representative defenses. For each
safety tolerances, showing robustness and illustrating relax-
                                                                  setup, the function descriptions are poisoned using the same
ing evaluation criteria alone is insufficient for mitigation.
                                                                  malicious template, while system inputs, driving scenarios,
                                                                  and agent configurations remain fixed. We consider both
5.4. Attack Propagating Styles: Direct vs. Indirect
                                                                  prompt-level and agent-level defenses, and evaluate the
To investigate how attack effects propagate across agents, we     attack using ASR under a 3-meter L2 threshold, as well
implement three variants of FuncPoison in the AgentDriver         as dynamic ASR values over a range of L2 thresholds to
system. All variants use the same poisoned function descrip-      understand defense robustness under relaxed conditions.
tions and system inputs, but differ in where the malicious            Defense Overview. We group defenses into two primary
output is introduced. In the Direct Attack, the output from       categories based on their application scope:
the Perception Agent is passed directly to the Planning              • Prompt-level Defenses including Paraphrasing, De-
Agent. In the Memory Attack, the poisoned output is routed              limiters, Sandwich Prevention, and Boundary Aware-
through the Memory Agent, and in the Reasoning Attack, it               ness, aim to mitigate injection risks.
passes through both Memory and Reasoning agents before               • Multi-agent Defenses, including Safety Instruction and
reaching Planning. This setup allows us to compare the                  Memory Vaccines, target the system’s internal reason-
attack effectiveness of different propagation depths under              ing chain and memory interfaces, injecting explicit
a unified threat model.                                                 behavior constraints or semantic safeguards.
     Fig. 9 presents ASR values under varying L2 thresholds       We focus on two widely adopted and conceptually distinct
for all three attack paths. Interestingly, indirect propagation   defenses: Boundary Awareness (Defense 1)—a prompt-
results in more stable and persistent attack effects. While the   level strategy that marks tool outputs to prevent misinterpre-
Direct Attack achieves higher ASR in low-threshold settings,      tation, and Safety Instruction (Defense 2)—an agent-level
its effectiveness sharply drops beyond 10 meters. In contrast,    defense that inserts reasoning constraints into downstream
both Memory and Reasoning Attacks maintain moderate               prompts. We also evaluate a combined version, referred to
ASR (around 30%–40%) even as thresholds exceed 20                 as Binary Defense, where both methods are applied.
meters, indicating stronger long-range influence.                     We first test these defenses in a direct propagation
                                                                  setting, where the Perception Agent’s poisoned function
     We hypothesize this persistence stems from poisoned          output is passed directly to the Planning Agent. Table 5
outputs being compounded or semantically reinterpreted by         shows ASR@L2=3 results across eight defenses. Even the
intermediate agents, reinforcing their impact in a distributed    strongest—Boundary Awareness—only reduces ASR from
and less detectable way. FuncPoison not only misleads             86.3% to 84.3%, while others like Memory Vaccines
the initial agent but also leverages reasoning dynamics to        and Paraphrasing show almost no reduction. These results
amplify impact.                                                   demonstrate function-level poisoning remains highly effec-
     These findings demonstrate indirect propagation chan-        tive despite surface-level sanitization or behavior guidance.
nels more effective than direct manipulation, especially              We then assess the same defenses under an indirect
under relaxed safety conditions. Leveraging intermediate          propagation path—poisoned outputs pass through Memory
agents (Memory and Reasoning), FuncPoison gains en-               and Reasoning agents before reaching the Planning Agent.
hanced stealth and durability, making detection and miti-         Fig. 10 shows ASR across L2 thresholds. vs. direct attacks,
gation harder in multi-agent autonomous driving systems.          ASR drops more gradually with higher thresholds; even
      Figure 9: Indirect Attack: ASR of indirect attack                        Figure 10: Defense: ASR after applying different
      under varying L2 thresholds.                                             defense methods.

                      TABLE 5: Evaluation of Defense Methods Against FuncPoison (ASR @ L2=3)
              Category     Method                     Description                                                    ASR@L2=3
              –            Without Defense            No protection mechanism is applied. Baseline for comparison.     86.3%
              Direct       Paraphrasing               Rewriting prompts to avoid trigger patterns.                     86.3%
              Prompt       Delimiters                 Adding clear markers to separate prompt content.                 85.8%
              Injection    Sandwich Prevention        Wrapping user input with trusted instructions.                   86.0%
              Indirect     Instructional Prevention   Guiding language to restrict model behavior.                     78.7%
              Prompt       Boundary Awareness         Marking tool outputs to avoid confusion.                         84.3%
              Injection    Explicit Reminder          Providing injection warning examples.                            81.0%
              Defense in   Safety Instruction         Embedding constraints in agent prompts.                          79.0%
              MAS          Memory Vaccines            Pre-inserting safe memory entries.                               85.2%



with Defense 1/2 applied, the attack remains effective. For                   (2) Semantic Inspection Layer. An LLM reviewer
example, Binary Defense keeps ASR more than 50% up                        analyzes function intent and instruction-likeness, identifying
to L2=15m, indicating long-lasting behavioral divergence.                 covert template hijacking patterns bypassing lexical checks.
Defense 1 outperforms Defense 2 slightly, as prompt-based                 Suspicious descriptions are sanitized or flagged for review.
annotation slows but does not stop propagation.                               These two layers act as a publish-time gatekeeper for
     These results expose fundamental weaknesses in existing              Function Libraries, allowing normal updates to pass unhin-
defenses. Prompt-level defenses fail because FuncPoison                   dered while intercepting anomalous behaviors at the source.
embeds malicious triggers within structured function de-                      We evaluate this defense under the same experimen-
scriptions, often assumed trusted and are not subject to                  tal conditions as in our attack effectiveness studies, en-
prompt sanitization. Agent-level defenses struggle because                suring changes in Attack Success Rate (ASR) directly
the poisoned outputs often remain semantically plausible                  reflects defensive impact. After applying the inspection
and pass through intermediate reasoning agents undetected.                pipeline—without modifying system prompts, models, or
The use of indirect propagation further obscures attribution,             communication architecture—ASR decreases from 86.3%
allowing the malicious effect to accumulate over time.                    ± 3.0% to 80.1% ± 3.2%. This moderate reduction indi-
     FuncPoison maintains strong persistence and stealth un-              cates pre-deployment auditing blocks part of the poisoned
der direct and indirect propagation. It bypasses prompt-                  entries, but template-conforming poisoning still evades de-
and agent-level defenses by exploiting trusted function-call              tection when malicious content closely resembles legitimate
execution and inter-agent reasoning flow, demonstrating ex-               tool usage.
isting defenses’ limitation against function-level poisoning.                 Overall, these results reveal that while library-level in-
                                                                          spection is a practical first defense against supply-chain
6. Countermeasures                                                        poisoning, FuncPoison retains strong stealth and persistence.
Given the supply-side nature of FuncPoison, a practical                   Tool-augmented autonomous driving systems must therefore
defense should intervene when functions are published or                  combine static inspection with additional supply-chain safe-
updated rather than during runtime. We therefore design a                 guards to mitigate this overlooked attack surface.
lightweight library-level inspection pipeline that automati-
cally scrutinizes function descriptions before distribution.              7. Conclusion
    Our defense includes two detection layers:                            We present FuncPoison, a novel function-level poisoning
    (1) Lexical Filter Layer. A lightweight scanner per-                  attack against LLM-based multi-agent autonomous driv-
forms pattern-based inspection to detect imperative phrases               ing systems. Unlike traditional prompt or data poisoning,
and command-like text structures. The filter assigns a risk               FuncPoison targets the trusted function call interface, in-
score and automatically blocks entries exceeding a thresh-                jecting adversarial patterns into shared Function Libraries to
old, forwarding borderline cases for deeper analysis.                     trigger template-compliant malicious calls. Our experiments
show that FuncPoison achieves high success rates, strong                    [6]   C. Cui, Z. Yang, Y. Zhou, Y. Ma, J. Lu, L. Li, Y. Chen,
stealth, and persistent impact across propagation paths and                       J. Panchal, and Z. Wang, “Personalized autonomous driving with
                                                                                  large language models: Field experiments,” 2024. [Online]. Available:
model cores, even under advanced defenses. These find-                            https://arxiv.org/abs/2312.09397
ings reveal a critical underexplored vulnerability in LLM-
                                                                            [7]   W. Huang, F. Xia, T. Xiao, H. Chan, J. Liang, P. Florence, A. Zeng,
driven systems—the trusted interfaces linking reasoning and                       J. Tompson, I. Mordatch, Y. Chebotar, P. Sermanet, N. Brown,
real-world actions. We call for future defenses verify the                        T. Jackson, L. Luu, S. Levine, K. Hausman, and B. Ichter, “Inner
trustworthiness and provenance of internal function calls to                      monologue: Embodied reasoning through planning with language
ensure the safety of LLM-based autonomous systems.                                models,” 2022. [Online]. Available: https://arxiv.org/abs/2207.05608
                                                                            [8]   J. Mao, J. Ye, Y. Qian, M. Pavone, and Y. Wang, “A
Ethics Considerations                                                             language agent for autonomous driving,” 2024. [Online]. Available:
In this paper, we present FuncPoison, a security analysis                         https://arxiv.org/abs/2311.10813
of function-level poisoning attacks in large language model                 [9]   X. Hou, W. Wang, L. Yang, H. Lin, J. Feng, H. Min, and
(LLM)-based multi-agent autonomous driving systems. All                           X. Zhao, “Driveagent: Multi-agent structured reasoning with llm and
                                                                                  multimodal sensor fusion for autonomous driving,” 2025. [Online].
experiments were conducted in a strictly controlled research                      Available: https://arxiv.org/abs/2505.02123
environment using simulated agents and sandboxed func-                      [10] K. Jiang, X. Cai, Z. Cui, A. Li, Y. Ren, H. Yu, H. Yang,
tion libraries, ensuring that no real autonomous vehicles,                       D. Fu, L. Wen, and P. Cai, “Koma: Knowledge-driven multi-agent
vendors, or external systems were affected. Our purpose is                       framework for autonomous driving with large language models,”
not to attack or disrupt real-world systems, but to reveal a                     2024. [Online]. Available: https://arxiv.org/abs/2407.14239
previously overlooked structural vulnerability—namely, the                  [11] K. Qian, S. Jiang, Y. Zhong, Z. Luo, Z. Huang, T. Zhu, K. Jiang,
critical yet fragile role of the Function Library within multi-                  M. Yang, Z. Fu, J. Miao, Y. Shi, H. Z. Lim, L. Liu, T. Zhou, H. Yu,
                                                                                 Y. Hu, G. Li, G. Chen, H. Ye, L. Sun, and D. Yang, “Agentthink:
agent architectures. Through this work, we aim to raise                          A unified framework for tool-augmented chain-of-thought reasoning
awareness of Function Library security as a foundational                         in vision-language models for autonomous driving,” 2025. [Online].
aspect of LLM-based system safety and to encourage the                           Available: https://arxiv.org/abs/2505.15298
community to integrate such considerations into future sys-                 [12] H. Siadati, S. Jafarikhah, E. Sahin, T. B. Hernandez, E. L. Tripp,
tem design. The entire study adheres to the ethical principles                   D. Khryashchev, and A. Kharraz, “Devphish: Exploring social
of responsible security research and disclosure.                                 engineering in software supply chain attacks on developers,” 2024.
                                                                                 [Online]. Available: https://arxiv.org/abs/2402.18401
LLM Usage Considerations                                                    [13] Google Cloud Threat Intelligence, “Supply chain compromises
Throughout this research, large language models (LLMs)                           through node.js packages,” https://cloud.google.com/blog/topics/
                                                                                 threat-intelligence/supply-chain-node-js/, 2021.
were used solely for grammar checking and language
refinement during paper writing. All research ideas, system                 [14] Sonatype Blog, “Npm ’coa’ and ’rc’ packages taken
                                                                                 over to spread malware,” https://www.sonatype.com/blog/
designs, attack implementations, and analysis results were                       npm-hijackers-at-it-again-popular-coa-and-rc-open-source-libraries,
created independently by the authors. No generative model                        2021.
was used to produce technical content or experimental data.                 [15] S. Liu, X. Hu, X. Xia, D. Lo, and X. Yang, “An empirical study
The authors ensured that all use of LLMs complied with                           of vulnerable package dependencies in llm repositories,” 2025.
academic ethics and avoided plagiarism or scientific miscon-                     [Online]. Available: https://arxiv.org/abs/2508.21417
duct. The authors take full responsibility for the originality              [16] U. . T. Intelligence, “Malicious python packages in pypi tar-
and integrity of the manuscript.                                                 geting developer credentials,” https://unit42.paloaltonetworks.com/
                                                                                 malicious-packages-in-pypi/, 2023.
References                                                                  [17] A. White et al., “Security on ros: analyzing and exploiting vulnera-
[1]   C. Cui, Y. Ma, Z. Yang, Y. Zhou, P. Liu, J. Lu, L. Li, Y. Chen,            bilities of ros-based systems,” arXiv preprint, 2020.
      J. H. Panchal, A. Abdelraouf, R. Gupta, K. Han, and Z. Wang,          [18] M. Ohm et al., “A review of open source software supply chain
      “Large language models for autonomous driving (llm4ad): Concept,           attacks,” Journal / PMC, 2020.
      benchmark, experiments, and challenges,” 2025. [Online]. Available:
      https://arxiv.org/abs/2410.15281                                      [19] J. Guo and H. Cai, “System prompt poisoning: Persistent attacks
                                                                                 on large language models beyond user injection,” 2025. [Online].
[2]   H. Sha, Y. Mu, Y. Jiang, L. Chen, C. Xu, P. Luo, S. E. Li,                 Available: https://arxiv.org/abs/2505.06493
      M. Tomizuka, W. Zhan, and M. Ding, “Languagempc: Large
      language models as decision makers for autonomous driving,” 2025.     [20] T. Fu, M. Sharma, P. Torr, S. B. Cohen, D. Krueger, and F. Barez,
      [Online]. Available: https://arxiv.org/abs/2310.03026                      “Poisonbench: Assessing large language model vulnerability to data
                                                                                 poisoning,” 2025. [Online]. Available: https://arxiv.org/abs/2410.
[3]   Z. Xu, Y. Zhang, E. Xie, Z. Zhao, Y. Guo, K.-Y. K. Wong, Z. Li,            08811
      and H. Zhao, “Drivegpt4: Interpretable end-to-end autonomous
      driving via large language model,” 2024. [Online]. Available:         [21] F. Perez and I. Ribeiro, “Ignore previous prompt: Attack
      https://arxiv.org/abs/2310.01412                                           techniques for language models,” 2022. [Online]. Available:
                                                                                 https://arxiv.org/abs/2211.09527
[4]   Z. Yang, X. Jia, H. Li, and J. Yan, “Llm4drive: A survey of large
      language models for autonomous driving,” 2024. [Online]. Available:   [22] C. H. Song, J. Wu, C. Washington, B. M. Sadler, W.-L. Chao,
      https://arxiv.org/abs/2311.01043                                           and Y. Su, “Llm-planner: Few-shot grounded planning for embodied
                                                                                 agents with large language models,” 2023. [Online]. Available:
[5]   W. Wang, J. Xie, C. Hu, H. Zou, J. Fan, W. Tong, Y. Wen, S. Wu,
                                                                                 https://arxiv.org/abs/2212.04088
      H. Deng, Z. Li, H. Tian, L. Lu, X. Zhu, X. Wang, Y. Qiao, and
      J. Dai, “Drivemlm: Aligning multi-modal large language models         [23] Y. Tian, X. Yang, J. Zhang, Y. Dong, and H. Su, “Evil geniuses:
      with behavioral planning states for autonomous driving,” 2023.             Delving into the safety of llm-based agents,” 2024. [Online].
      [Online]. Available: https://arxiv.org/abs/2312.09245                      Available: https://arxiv.org/abs/2311.11855
[24] Z. Zhang, Y. Zhang, L. Li, H. Gao, L. Wang, H. Lu,                        [43] N. Fendley, E. W. Staley, J. Carney, W. Redman, M. Chau,
     F. Zhao, Y. Qiao, and J. Shao, “Psysafe: A comprehensive                       and N. Drenkow, “A systematic review of poisoning attacks
     framework for psychological-based attack, defense, and evaluation              against large language models,” 2025. [Online]. Available: https:
     of multi-agent system safety,” 2024. [Online]. Available: https:               //arxiv.org/abs/2506.06518
     //arxiv.org/abs/2401.11880
                                                                               [44] A. Zou, Z. Wang, N. Carlini, M. Nasr, J. Z. Kolter, and M. Fredrikson,
[25] P. Lu, B. Peng, H. Cheng, M. Galley, K.-W. Chang, Y. N. Wu,                    “Universal and transferable adversarial attacks on aligned language
     S.-C. Zhu, and J. Gao, “Chameleon: Plug-and-play compositional                 models,” arXiv preprint arXiv:2307.15043, 2023.
     reasoning with large language models,” 2023. [Online]. Available:
     https://arxiv.org/abs/2304.09842                                          [45] X. Liu, N. Xu, M. Chen, and C. Xiao, “Autodan: Generating
                                                                                    stealthy jailbreak prompts on aligned large language models,” 2024.
[26] E. Bagdasaryan and V. Shmatikov, “Blind backdoors in deep learning             [Online]. Available: https://arxiv.org/abs/2310.04451
     models,” 2021. [Online]. Available: https://arxiv.org/abs/2005.03823
                                                                               [46] S. Jiang, S. R. Kadhe, Y. Zhou, L. Cai, and N. Baracaldo, “Forcing
[27] Y. Liu, Y. Jia, R. Geng, J. Jia, and N. Z. Gong, “Formalizing                  generative models to degenerate ones: The power of data poisoning
     and benchmarking prompt injection attacks and defenses,” 2024.                 attacks,” 2023. [Online]. Available: https://arxiv.org/abs/2312.04748
     [Online]. Available: https://arxiv.org/abs/2310.12815
                                                                               [47] H. Song, Y. an Liu, R. Zhang, J. Guo, and Y. Fan, “Chain-of-thought
[28] Z. Chen, Z. Xiang, C. Xiao, D. Song, and B. Li, “Agentpoison:                  poisoning attacks against r1-based retrieval-augmented generation
     Red-teaming llm agents via poisoning memory or knowledge bases,”               systems,” 2025. [Online]. Available: https://arxiv.org/abs/2505.16367
     2024. [Online]. Available: https://arxiv.org/abs/2407.12784
                                                                               [48] G. Zhao, H. Wu, X. Zhang, and A. V. Vasilakos, “Shadowcot:
[29] B. Zhang, H. Xin, J. Li, D. Zhang, M. Fang, Z. Liu,                            Cognitive hijacking for stealthy reasoning backdoors in llms,” 2025.
     L. Nie, and Z. Liu, “Benchmarking poisoning attacks against                    [Online]. Available: https://arxiv.org/abs/2504.05605
     retrieval-augmented generation,” 2025. [Online]. Available: https:
     //arxiv.org/abs/2505.18543                                                [49] J. Su, “Enhancing adversarial attacks through chain of thought,”
                                                                                    2024. [Online]. Available: https://arxiv.org/abs/2410.21791
[30] X. Tan, H. Luan, M. Luo, X. Sun, P. Chen, and J. Dai,
     “Revprag: Revealing poisoning attacks in retrieval-augmented              [50] Z. Xiang, F. Jiang, Z. Xiong, B. Ramasubramanian, R. Poovendran,
     generation through llm activation analysis,” 2025. [Online]. Available:        and B. Li, “Badchain: Backdoor chain-of-thought prompting
     https://arxiv.org/abs/2411.18948                                               for large language models,” 2024. [Online]. Available: https:
                                                                                    //arxiv.org/abs/2401.12242
[31] H. Hao, J. Han, C. Li, Y.-F. Li, and X. Yue, “Rap: Retrieval-
     augmented personalization for multimodal large language models,”          [51] Snyk     Threat   Research,     “Malicious   code      found     in
     2025. [Online]. Available: https://arxiv.org/abs/2410.13360                    npm        package        event-stream,”      https://snyk.io/blog/
                                                                                    malicious-code-found-in-npm-package-event-stream/, 2018.
[32] F. Nazary, Y. Deldjoo, T. D. Noia, and E. D. Sciascio, “Stealthy
     llm-driven data poisoning attacks against embedding-based retrieval-      [52] npm      Blog,     “Details     about     the     event-stream   in-
     augmented recommender systems,” 2025. [Online]. Available:                     cident,”                   https://blog.npmjs.org/post/180565383195/
     https://arxiv.org/abs/2505.05196                                               details-about-the-event-stream-incident, 2018.
[33] T. Ju, Y. Wang, X. Ma, P. Cheng, H. Zhao, Y. Wang, L. Liu, J. Xie,        [53] Z. Shao, H. Liu, J. Mu, and N. Z. Gong, “Enhancing prompt
     Z. Zhang, and G. Liu, “Flooding spread of manipulated knowledge                injection attacks to llms via poisoning alignment,” 2025. [Online].
     in llm-based multi-agent communities,” 2024. [Online]. Available:              Available: https://arxiv.org/abs/2410.14827
     https://arxiv.org/abs/2407.07791
                                                                               [54] J. Wang, P. Gupta, I. Habernal, and E. Hüllermeier, “Is your prompt
[34] E. Wallace, T. Z. Zhao, S. Feng, and S. Singh, “Concealed                      safe? investigating prompt injection attacks against open-source
     data poisoning attacks on nlp models,” 2021. [Online]. Available:              llms,” 2025. [Online]. Available: https://arxiv.org/abs/2505.14368
     https://arxiv.org/abs/2010.12563
                                                                               [55] C. Zhang, M. Jin, Q. Yu, C. Liu, H. Xue, and X. Jin, “Goal-guided
[35] Y. Zhang, J. Rando, I. Evtimov, J. Chi, E. M. Smith, N. Carlini,               generative prompt injection attack on large language models,” 2024.
     F. Tramèr, and D. Ippolito, “Persistent pre-training poisoning of             [Online]. Available: https://arxiv.org/abs/2404.07234
     llms,” 2024. [Online]. Available: https://arxiv.org/abs/2410.13722
                                                                               [56] X. Liu, Z. Yu, Y. Zhang, N. Zhang, and C. Xiao, “Automatic and
[36] M. Shu, J. Wang, C. Zhu, J. Geiping, C. Xiao, and T. Goldstein, “On            universal prompt injection attacks against large language models,”
     the exploitability of instruction tuning,” 2023. [Online]. Available:          2024. [Online]. Available: https://arxiv.org/abs/2403.04957
     https://arxiv.org/abs/2306.17194
                                                                               [57] Y. Liu, G. Deng, Y. Li, K. Wang, Z. Wang, X. Wang, T. Zhang,
[37] M. Cole, “Engineer-friendly primer: Memory injection attacks on                Y. Liu, H. Wang, Y. Zheng, and Y. Liu, “Prompt injection
     llms,” https://murraycole.com/posts/llm-memory-injection-attacks,              attack against llm-integrated applications,” 2024. [Online]. Available:
     2024, accessed August 2025.                                                    https://arxiv.org/abs/2306.05499
[38] L. S. Database, “Llm memory poisoning attack,” On-                        [58] W. Zhang, X. Kong, C. Dewitt, T. Braunl, and J. B. Hong, “A study
     line,  2024,      https://www.promptfoo.dev/lm-security-db/vuln/               on prompt injection attack against llm-integrated mobile robotic
     llm-memory-poisoning-attack-01ba0c8d.                                          systems,” 2024. [Online]. Available: https://arxiv.org/abs/2408.03515
[39] S. Dong, S. Xu, P. He, Y. Li, J. Tang, T. Liu, H. Liu, and Z. Xiang,      [59] OpenAI, “Function calling and code interpreter,” https://platform.
     “A practical memory injection attack against llm agents,” 2025.                openai.com/docs/guides/function-calling, 2023, accessed: 2025-07-
     [Online]. Available: https://arxiv.org/abs/2503.03704                          28.
[40] P.   Yang,     “Awesome     data     poisoning      and    back-
                                                                               [60] T. Schick and H. Schütze, “Toolformer: Language models can teach
     door          attacks,”         https://github.com/penghui-yang/
                                                                                    themselves to use tools,” arXiv preprint arXiv:2302.04761, 2023.
     awesome-data-poisoning-and-backdoor-attacks, 2025, accessed:
     August 2025.                                                              [61] S. Yao, J. Yang, N. Yu, D. Jiang, D. Wang, and M. Tang, “React:
                                                                                    Synergizing reasoning and acting in language models,” arXiv preprint
[41] M. Alber, D. Mack, A. Ondrus et al., “Medical large language models
                                                                                    arXiv:2210.03629, 2022.
     are vulnerable to data-poisoning attacks,” Nature Medicine, vol. 30,
     no. 6, pp. 1355–1358, 2024.                                               [62] Y. Wu, D. Li, Y. Chen, R. Jiang, H. P. Zou, W.-C. Huang, Y. Li,
[42] P. Zhao, W. Zhu, P. Jiao, D. Gao, and O. Wu, “Data                             L. Fang, Z. Wang, and P. S. Yu, “Multi-agent autonomous driving
     poisoning in deep learning: A survey,” 2025. [Online]. Available:              systems with large language models: A survey of recent advances,”
     https://arxiv.org/abs/2503.22759                                               2025. [Online]. Available: https://arxiv.org/abs/2502.16804
