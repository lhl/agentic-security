                                                     Parallax: Why AI Agents That Think Must Never Act
                                                                       A Paradigm for Architecturally Safe Autonomous Execution
                                                                                                        Joel Fokou
                                                                                                   Independent Researcher

                                         Abstract                                                                with access to the local filesystem, credentials, and network inter-
                                         Autonomous AI agents are rapidly transitioning from experimental        faces [3].
                                         tools to operational infrastructure, with projections that 80% of          This transition from generative AI to agentic AI introduces a
                                         enterprise applications will embed AI copilots by the end of 2026.      security problem that is categorically different from the risks ad-
                                         As agents gain the ability to execute real-world actions (reading       dressed by the large language model (LLM) safety literature to date.
                                                                                                                 When an LLM is used as a conversational interface, the worst-case




arXiv:2604.12986v1 [cs.CR] 14 Apr 2026
                                         files, running commands, making network requests, modifying
                                         databases), a fundamental security gap has emerged. The domi-           outcome of a safety failure is the generation of harmful or mislead-
                                         nant approach to agent safety relies on prompt-level guardrails:        ing content. When that same LLM is embedded in an agent with
                                         natural language instructions that operate at the same abstraction      execution privileges, a safety failure can result in data exfiltration,
                                         level as the threats they attempt to mitigate. This paper argues that   credential theft, system compromise, or irreversible destruction
                                         prompt-based safety is architecturally insufficient for agents with     of critical resources. The distinction is not one of degree but of
                                         execution capability and introduces Parallax, a paradigm for safe       kind. The agent has agency: the capacity to act on the world. The
                                         autonomous AI execution grounded in four principles: Cognitive-         security challenge is to ensure that this agency is exercised safely
                                         Executive Separation, which structurally prevents the reasoning         even when the reasoning system is compromised.
                                         system from executing actions; Adversarial Validation with Gradu-
                                         ated Determinism, which interposes an independent, multi-tiered
                                         validator between reasoning and execution; Information Flow Con-
                                                                                                                 1.1    The Prompt Guardrail Fallacy
                                         trol, which propagates data sensitivity labels through agent work-      The dominant approach to AI agent safety is what we term prompt-
                                         flows to detect context-dependent threats; and Reversible Execution,    level guardrailing: the practice of embedding safety instructions in
                                         which captures pre-destructive state to enable rollback when vali-      the agent’s system prompt, instructing the model to refuse danger-
                                         dation fails. We present OpenParallax, an open-source reference         ous requests, avoid certain actions, and comply with usage policies.
                                         implementation in Go, and evaluate it using Assume-Compromise           This approach has three fundamental weaknesses.
                                         Evaluation, a methodology that bypasses the reasoning system               First, prompt guardrails share the same computational substrate
                                         entirely to test the architectural boundary under full agent com-       as the threats they attempt to mitigate. The model processes safety
                                         promise. Across 280 adversarial test cases in nine attack categories,   instructions and adversarial inputs through the same attention
                                         Parallax blocks 98.9% of attacks with zero false positives under        mechanism, with no architectural distinction between trusted in-
                                         its default configuration, and 100% of attacks under its maximum-       structions and untrusted data. This is precisely the condition that
                                         security configuration. When the reasoning system is compromised,       makes prompt injection possible [4]. As OpenAI has acknowledged,
                                         prompt-level guardrails provide zero protection because they exist      language models have no reliable mechanism for distinguishing
                                         only within the compromised system; Parallax’s architectural            between instructions and data [6], and NIST has classified agent hi-
                                         boundary holds regardless.                                              jacking through indirect prompt injection as a core threat to agentic
                                                                                                                 systems [7]. Documented prompt injection attempts against enter-
                                                                                                                 prise AI systems increased 340% year-over-year in late 2025 [8],
                                         Keywords
                                                                                                                 with indirect attacks now accounting for over 55% of observed
                                         AI agent security, privilege separation, adversarial validation, au-    incidents and achieving 20–30% higher success rates than direct
                                         tonomous execution, information flow control, agentic AI safety         injection [9].
                                                                                                                    Second, prompt guardrails degrade under extended context. Re-
                                                                                                                 search published in late 2025 and early 2026 has demonstrated that
                                         1   Introduction                                                        agents with long conversation histories are significantly more vul-
                                         The rapid deployment of autonomous AI agents represents one             nerable to manipulation, as cumulative context can shift the model’s
                                         of the most consequential shifts in computing since the transition      effective constraint boundary through gradual “salami slicing” at-
                                         from mainframes to networked systems. Industry projections in-          tacks [10]. Memory poisoning attacks can implant false instructions
                                         dicate that by the end of 2026, 40% of enterprise applications will     that persist across sessions, effectively converting the agent into a
                                         embed task-specific AI agents [1], while AI copilots are expected       latent threat [11].
                                         to appear in nearly 80% of enterprise workplace applications [2].          Third, prompt guardrails cannot survive multi-agent propaga-
                                         These systems are no longer confined to generating content or an-       tion. In multi-agent systems where the output of one model becomes
                                         swering questions. They read files, execute shell commands, make        the input of another, a successful injection at one layer propagates
                                         API calls, query databases, modify configurations, and orchestrate      through every subsequent layer [12]. Security testing shows that
                                         multi-step workflows across production infrastructure. In the con-      during a single prompt injection incident, attacks propagate to 48%
                                         sumer domain, personal AI agents now operate on users’ machines         of co-running agents in multi-agent deployments [9]. Cross-agent
                                                                                                                                    Joel Fokou


trust exploitation, where one compromised agent manipulates an-                   and independent of the specific AI architecture used for
other by exploiting implicit trust in inter-agent communication,                  reasoning (Section 4).
has been demonstrated in production coding environments [13].                 (2) A formal threat model for autonomous AI agents that en-
    These are not theoretical concerns. In early 2026, the widely de-             compasses direct and indirect prompt injection, multi-step
ployed open-source agent framework OpenClaw, with over 340,000                    context manipulation, tool-use chain attacks, encoding and
GitHub stars, was found to have multiple critical vulnerabilities in-             obfuscation exploits, multi-agent compromise and privilege
cluding supply chain attacks exploiting the absence of privilege sep-             escalation, and attacks targeting the validation layer itself
aration between reasoning and execution, resulting in over 21,000                 (Section 3).
exposed instances [14]. A Fortune 500 company suffered data ex-               (3) OpenParallax, an open-source reference implementa-
filtration when a single malicious sentence embedded in a vendor                  tion in Go that realizes the Parallax paradigm through
invoice caused its internal AI assistant to forward its client data-              process-isolated architecture, a four-tiered validation sys-
base to an external server [15]. These incidents demonstrate that                 tem (Shield), information flow control tagging, pre-de-
the threat model addressed by this work is not hypothetical but                   structive state capture (Chronicle), and sandbox integrity
operational.                                                                      verification (Section 5).
                                                                              (4) Assume-Compromise Evaluation, a methodology for
1.2     The Architectural Insight                                                 testing agent security architectures by bypassing the rea-
                                                                                  soning system entirely and injecting tool calls directly into
The central argument of this paper is that agent safety cannot be
                                                                                  the execution boundary. Applied to 280 adversarial test
achieved through any mechanism that operates at the language level:
                                                                                  cases across nine attack categories, demonstrating a 98.9%
whether prompt engineering, output filtering, constitutional AI, or
                                                                                  block rate with zero false positives under the default con-
reinforcement learning from human feedback. These approaches
                                                                                  figuration, and 100% under the maximum-security configu-
improve the quality of the model’s judgments but do not constrain
                                                                                  ration (Section 6).
its actions. They are analogous to asking a user to follow a security
policy without enforcing it at the operating system level: effective
against accidental misuse, ineffective against motivated adversaries        The remainder of this paper is organized as follows. Section 2
or systematic failure.                                                  provides background on AI agent security and the systems security
    We propose instead that agent safety requires architectural en-     foundations that inform Parallax. Section 3 defines the threat
forcement: structural properties of the system that hold regardless     model. Section 4 presents the four principles of Parallax and their
of the state of the reasoning component. This insight draws on          derived security properties. Section 5 describes the OpenParallax
decades of established practice in systems security:                    reference implementation. Section 6 reports our empirical evalua-
                                                                        tion. Section 7 discusses implications and limitations. Section 8 po-
       • Privilege separation in operating systems ensures that         sitions Parallax relative to existing approaches. Section 9 outlines
         a compromised user-space process cannot directly access        future research directions, including purpose-trained evaluation
         kernel resources [16]. The security boundary exists at the     models, embodied system applications, and critical infrastructure
         hardware and OS level, not in the process’s own code.          deployment. Section 10 concludes.
       • Mandatory access control systems like Bell-LaPadula
         enforce information flow policies that no user-level action
         can override [17]. The policy is structural, not advisory.     2     Background and Motivation
       • Hardware security modules (HSMs) and Trusted Plat-
                                                                        This section surveys the current state of AI agent security (Sec-
         form Modules (TPMs) provide trust anchors that the soft-
                                                                        tion 2.1) and the systems security principles that inform the Paral-
         ware they protect cannot modify or inspect [18]. The val-
                                                                        lax paradigm (Section 2.2).
         idator is immutable with respect to the validated.
   Parallax applies these principles to AI agent architecture. Its
core insight can be stated simply: the system that reasons about        2.1      The Agent Execution Security Gap
actions must be structurally unable to execute them, and the system     The transition from conversational LLMs to agentic AI systems has
that executes actions must be structurally unable to reason about       introduced a class of security risks for which the existing safety
them, with an independent, immutable validator interposed between       literature is poorly equipped. The distinction is fundamental: a
the two.                                                                conversational LLM produces content; an agentic system produces
                                                                        actions. The safety properties required for each are categorically
1.3     Contributions                                                   different.
This paper makes the following contributions:
                                                                        2.1.1    From Generation to Execution
      (1) The Parallax paradigm. We introduce a paradigm for
          architecturally safe autonomous AI execution comprising          LLM safety research has historically focused on the quality of
          four principles (Cognitive-Executive Separation, Adversar-    model outputs: reducing harmful content generation, mitigating
          ial Validation with Graduated Determinism, Information        bias, improving factual accuracy, and aligning model behavior with
          Flow Control, and Reversible Execution) that are formally     human preferences [22, 23]. These efforts address the question: “Is
          defined, grounded in established systems security theory,     the model producing the right thing?” The agentic security question
Parallax: Why AI Agents That Think Must Never Act


is different: “Is the system doing the right thing?” Here, “doing” in-   call or command execution rather than text, and the harmfulness
volves file operations, shell command execution, API calls, database     of an action depends on context (e.g. deleting a temporary file ver-
modifications, and interactions with external services.                  sus deleting a configuration file) rather than content classification
   This shift introduces what Willison [24] has termed the Lethal        alone.
Trifecta: the simultaneous presence of (1) access to private data,          Tool-use restrictions and approval flows. Some frameworks
(2) exposure to untrusted content, and (3) an exfiltration vector        implement per-tool access control, requiring human approval for
through external requests. When an agent possesses all three prop-       specific operations. While useful, these approaches either require
erties (and most production agents do), it is structurally vulnerable    constant human oversight (which negates the value of autonomy) or
to attack regardless of the quality of its safety training or prompt     define static policies that cannot adapt to the contextual judgment
engineering.                                                             required for nuanced decisions.
   The OWASP Foundation has recognized this categorical shift by            None of these approaches enforces a structural separation be-
publishing two separate security frameworks. The OWASP Top 10 for        tween reasoning and execution. In each case, the safety mechanism
LLM Applications [4] addresses vulnerabilities in language models        operates at the same level of abstraction as the reasoning system, ei-
themselves: prompt injection, data poisoning, sensitive information      ther within the model (RLHF, Constitutional AI), within the prompt
disclosure. The OWASP Top 10 for Agentic Applications [5], released      (guardrails), or within the same process (output filtering, approval
in December 2025 with input from over 100 security researchers,          flows). Parallax addresses this gap by enforcing safety at the ar-
addresses what happens when those models gain tools, memory,             chitectural level, through properties that hold regardless of the state
and autonomy. The agentic framework introduces the principle of          of the reasoning component.
least agency: that autonomy should be earned and bounded, not
granted by default. It enumerates ten risk categories specific to
autonomous systems, including Agent Goal Hijack (ASI01), Tool
Misuse (ASI02), Identity and Privilege Abuse (ASI03), and Rogue          2.2     Foundations in Systems Security
Agents (ASI10) [5].                                                      The Parallax paradigm is not constructed from first principles
   As Microsoft’s AI Red Team has noted in their analysis of the         unique to AI. It draws on well-established concepts from systems
OWASP agentic framework, “a system can be ‘working as designed’          security that have been validated over decades of deployment in
while still taking steps that a human would be unlikely to approve,      operating systems, network security, and cryptographic infrastruc-
because the boundaries were unclear, permissions were too broad,         ture. We briefly review the foundational concepts that inform each
or tool use was not tightly governed” [25]. This observation captures    principle.
the essence of the execution security gap: the threat is not always a
model behaving incorrectly, but a model behaving correctly within        2.2.1   Privilege Separation
bounds that are insufficiently constrained.
                                                                            The principle of privilege separation divides a program into
                                                                         components with different levels of trust and capability, communi-
2.1.2   The Current Defense Landscape
                                                                         cating through defined interfaces. Provos, Friedl, and Honeyman
    Existing defenses for agentic AI systems fall into four broad        formalized this approach in their seminal work on OpenSSH [16],
categories, none of which provides architectural safety guarantees:      demonstrating that splitting a program into a privileged moni-
    Prompt-level guardrails. The most widely deployed approach           tor and an unprivileged slave process, communicating through a
embeds safety instructions in the agent’s system prompt. As estab-       socket pair, ensures that exploitation of the unprivileged compo-
lished in Section 1.1, these share the same computational substrate      nent cannot yield unauthorized access to privileged operations.
as the threats they mitigate and are vulnerable to direct injection,     This principle is now foundational to the design of security-critical
indirect injection through ingested content, and degradation under       software, including mail transfer agents (Postfix), web servers, and
extended context. Security testing demonstrates that 40% of AI           the OpenBSD operating system. In Parallax, cognitive-executive
agent frameworks contain exploitable prompt injection flaws in           separation applies the same principle: the reasoning process (un-
tool-execution logic [9].                                                privileged) communicates with the execution engine (privileged)
    Constitutional AI and RLHF. Approaches such as Constitu-             through a defined gRPC interface, and exploitation of the reasoning
tional AI [23] and reinforcement learning from human feedback            process cannot yield execution capability.
(RLHF) [22] improve the model’s internal tendency to refuse harm-
ful requests. These are valuable contributions to model safety but       2.2.2   Mandatory Access Control and Information Flow
operate at the reasoning level, not the execution level. A model
                                                                            The Bell-LaPadula model [17] established the theoretical foun-
trained through RLHF may reliably refuse to generate harmful con-
                                                                         dation for mandatory access control (MAC), formalizing the “no
tent, but when that model is embedded in an agent, the refusal
                                                                         read up, no write down” property that prevents information flow
depends on the model correctly identifying the harmful intent be-
                                                                         from higher security classifications to lower ones. Subsequent work
hind an indirect injection. This is precisely the failure mode that
                                                                         on Decentralized Information Flow Control (DIFC) [26] extended
prompt injection exploits.
                                                                         these concepts to practical systems where data carries labels that
    Output filtering and content moderation. Post-generation
                                                                         propagate through computation. In Parallax, Information Flow
filters analyze model outputs for harmful content before delivery to
                                                                         Control applies these concepts to AI agent data flows: data read by
the user. For agentic systems, the relevant “output” is often a tool
                                                                         the agent carries provenance and sensitivity labels that propagate
                                                                                                                                      Joel Fokou


through tool calls, enabling the validation layer to detect context-       may attempt to exfiltrate data, escalate privileges, modify system
dependent threats such as credential exfiltration through multi-step       configuration, or persist malicious instructions across sessions. We
tool chains.                                                               make no assumptions about the model’s safety training, alignment,
                                                                           or refusal capabilities; the paradigm must hold even if these are
2.2.3   Defense in Depth and Graduated Trust                               entirely compromised.
                                                                              Untrusted: Child agent processes. In multi-agent configura-
   Saltzer and Schroeder’s foundational work on protection in com-
                                                                           tions, child agents spawned by the primary agent inherit the same
puter systems [19] articulated the principle of defense in depth:
                                                                           untrusted status. A child agent may be compromised independently
security should not depend on a single mechanism, and multiple
                                                                           of the parent through the same vectors. Additionally, a compro-
independent layers should each provide protection against differ-
                                                                           mised parent may attempt to craft delegated tasks that cause a
ent failure modes. Parallax operationalizes this principle through
                                                                           child agent to execute harmful actions, and a compromised child
tiered validation with graduated determinism: the most determin-
                                                                           may attempt privilege escalation through the orchestration layer.
istic mechanisms (hardcoded policy rules) handle the majority of
                                                                           Child agents cannot spawn their own children, access the parent’s
decisions, with progressively less deterministic mechanisms (fixed
                                                                           memory or context, or communicate with sibling agents except
classifiers, budget-limited LLM evaluation) reserved for cases that
                                                                           through the orchestrator.
require greater contextual judgment. Each tier has a different attack
                                                                              Trusted: The engine process. The execution engine, which
surface, and an adversary must defeat all tiers simultaneously to
                                                                           hosts the validation layer (Shield), the tool executors, and the
execute a harmful action.
                                                                           state capture system (Chronicle), is treated as trusted. Its code
                                                                           is compiled, immutable at runtime, and runs in a separate process
2.2.4   Hardware Trust Anchors
                                                                           from all agent processes. The validation layer’s policies and logic
   Hardware Security Modules (HSMs) and Trusted Platform Mod-              cannot be modified by any agent process. This trust assumption is
ules (TPMs) [18] provide a security foundation that the software           analogous to the trust placed in an operating system kernel or a
they protect cannot modify, inspect, or circumvent. The trust an-          hardware security module: the security of the entire system depends
chor exists at a layer below the evaluated system, and its integrity is    on the integrity of this component, and its integrity is maintained
guaranteed by the hardware boundary rather than by any software            through architectural isolation rather than behavioral guarantees.
policy. In Parallax, the validation layer (Shield) serves an analo-           The adversary. We consider an adversary who can:
gous role as a software trust anchor: it runs in a separate process, its         • Inject arbitrary instructions into the agent’s context through
configuration is hardcoded in compiled code rather than stored in                  direct user input or indirect injection via documents, web
mutable files, and the reasoning system has no mechanism to read,                  content, emails, API responses, or any data the agent in-
modify, or interfere with it. Validator immutability is guaranteed                 gests.
by architectural separation, not by policy compliance.                           • Craft multi-step attack sequences that build context over
                                                                                   time, gradually shifting the agent’s behavior through indi-
3     Threat Model                                                                 vidually benign interactions that culminate in a harmful
This section defines the adversary model, trust boundaries, and                    action.
attack classification against which Parallax is designed. We also                • Exploit inter-agent trust to propagate malicious instruc-
explicitly state the scope of threats addressed and those that fall                tions from a compromised agent to other agents in a multi-
outside the paradigm’s defensive perimeter.                                        agent deployment.
                                                                                 • Poison the agent’s persistent memory to implant latent
                                                                                   instructions that activate in future sessions.
3.1     Adversary Model and Trust Boundaries
                                                                                 • Use encoding, obfuscation, and indirection to disguise the
We consider a system in which an AI reasoning component (the                       nature of proposed actions (e.g. Base64-encoded commands,
agent) proposes actions to be executed on a host environment. The                  environment variable expansion, pipe chains where indi-
agent has access to a set of tools (file operations, shell execution,              vidual components appear benign).
network requests, database queries, and API calls) that enable it                • Attempt to directly attack the validation layer by crafting
to interact with the environment. The system may operate in a                      actions designed to read, modify, exhaust, or bypass Shield.
single-agent or multi-agent configuration, where a primary agent
can delegate tasks to child agents.                                           The adversary cannot: gain direct code execution on the host
   We define three trust levels:                                           outside of the agent system, modify the compiled engine binary, or
   Untrusted: The agent process. The LLM-powered reasoning                 compromise the deployment pipeline that delivers the engine pro-
system is treated as fully untrusted. This is the defining assumption      cess. These are infrastructure-level threats addressed by standard
of Parallax and represents its principal departure from existing           operational security practices (binary signing, secure deployment
approaches. We assume the agent may be compromised at any                  pipelines, host-level access control) rather than by the agent secu-
time through direct prompt injection, indirect prompt injection via        rity paradigm.
ingested content, memory poisoning, context manipulation over
extended conversations, or any mechanism that causes the model             3.2    Attack Classification
to propose actions that deviate from the user’s intent. The agent          We organize attacks into seven categories that span the full surface
may attempt to read, modify, or disable the validation layer. It           area of agentic AI threats. This taxonomy draws on the OWASP
Parallax: Why AI Agents That Think Must Never Act


Top 10 for Agentic Applications [5], the MITRE ATLAS frame-               reads a credential file, the content is tagged. When it subsequently
work [27], the comprehensive agent threat model proposed by               attempts to write tagged content to a network-accessible location,
Narajala and Anca [28], and documented real-world incidents.              Shield detects the information flow violation regardless of how
                                                                          many intermediate steps separate the read from the write.
3.2.1   C1: Direct Prompt Injection
                                                                          3.2.5   C5: Encoding and Obfuscation
   The adversary provides explicit instructions through the user
input channel that direct the agent to perform harmful actions.              The adversary uses encoding, string manipulation, or shell fea-
This ranges from blunt commands (“delete all files”) to semantically      tures to disguise harmful actions. This includes Base64-encoded
reframed requests (“help me free up disk space by removing every-         commands decoded at execution time, hexadecimal-encoded file
thing in the home directory”). Direct injection targets the agent’s       paths, Unicode homoglyphs that make dangerous paths resemble
inability to distinguish adversarial instructions from legitimate user    safe ones, environment variable expansion where the variable con-
requests when the instructions are presented in natural language.         tains the malicious payload, and pipe chains where each segment
Parallax defense: Shield evaluates the proposed action (the file          is benign but the pipeline produces harmful output. Parallax de-
deletion, the command execution), not the framing of the request.         fense: Shield’s Tier 1 heuristic engine includes pattern-matching
A harmful action is blocked regardless of how it was motivated.           rules specifically designed for these obfuscation techniques, inspect-
                                                                          ing command content after expansion and decoding rather than
3.2.2   C2: Indirect Prompt Injection                                     evaluating the surface representation alone.
    The adversary embeds malicious instructions in content that the
                                                                          3.2.6   C6: Multi-Agent Compromise
agent ingests during normal operation (documents it summarizes,
web pages it reads, API responses it processes, emails it triages).          In multi-agent configurations, the adversary targets child agents
This is the dominant real-world attack vector, accounting for over        or exploits inter-agent communication to propagate attacks. Attack
55% of observed prompt injection incidents in 2026 [9]. Indirect          vectors include: a compromised parent crafting malicious delegated
injection is particularly dangerous because the malicious instruc-        tasks; a compromised child attempting privilege escalation through
tions arrive through trusted data channels and may be invisible           the orchestrator; a compromised agent writing poisoned instruc-
to the user. Parallax defense: since the agent cannot execute any         tions to configuration files consumed by other agents (documented
action without Shield validation, the origin of the instruction is        in production environments where a hijacked GitHub Copilot wrote
irrelevant. Whether the agent proposes a harmful action because           malicious instructions to Claude Code’s configuration files [30]);
the user asked for it or because a hidden instruction in a PDF told       and cascading failures where one compromised agent’s output be-
it to, the action is evaluated identically.                               comes the input for others. Parallax defense: every child agent
                                                                          runs in an independently sandboxed process, communicates with
3.2.3   C3: Multi-Step Context Manipulation                               the engine through the same Shield validation path as the primary
                                                                          agent, cannot spawn further children, and cannot access any other
   The adversary constructs a sequence of individually benign inter-
                                                                          agent’s memory or context. There is no trust inheritance: a child
actions that gradually shift the agent’s behavior. Palo Alto Networks
                                                                          agent’s actions are validated with the same rigor as the parent’s.
Unit 42 has documented “salami slicing” attacks where cumulative
context over dozens of interactions shifts the agent’s effective con-
                                                                          3.2.7   C7: Validator-Targeted Attacks
straint boundary [10]. Research demonstrates that agents with long
conversation histories are significantly more vulnerable to this              The adversary specifically attempts to defeat the Parallax ar-
form of manipulation, and that a single compromised agent can             chitecture itself. This includes: attempting to read Shield’s policy
poison 87% of downstream decision-making within four hours in             files or configuration; attempting to modify Shield’s Tier 0 rules or
multi-agent systems [29]. Parallax defense: Shield evaluates each         Tier 1 classifier; attempting to exhaust Shield’s Tier 2 LLM evalua-
action independently, with no carry-over of approval from previous        tion budget through a flood of requests that trigger low-confidence
actions. Conversational momentum in the agent’s reasoning does            classifier signals or match Tier 2 policy rules, then submitting a
not influence the validation layer, because the validation layer has      harmful action when only Tiers 0 and 1 are available; crafting ac-
no access to the agent’s conversational state.                            tions designed to appear benign to the classifier but produce harm-
                                                                          ful side effects; and exploiting potential race conditions through
3.2.4   C4: Tool-Use Chain Attacks                                        rapid sequential requests. Parallax defense: Validator Immutabil-
                                                                          ity (Section 4.5) ensures that the agent process has no mechanism to
   The adversary exploits the agent’s ability to call multiple tools in
                                                                          read, write, or interfere with Shield. Budget exhaustion attacks are
sequence, where individual tool calls appear benign but the chain
                                                                          mitigated by the design of Graduated Determinism: Tiers 0 and 1
produces a harmful outcome. For example: reading a file containing
                                                                          together provide comprehensive coverage for well-characterized
credentials (benign), writing those credentials into a URL (benign
                                                                          threats without any LLM dependency, and Tier 2 is reserved for
in isolation), and executing a network request to that URL (data
                                                                          policy-designated evaluations and low-confidence classifier signals.
exfiltration). OWASP identifies tool misuse (ASI02) as one of the
                                                                          The system is designed to remain safe, not merely degraded, when
top three agentic risks, with 520 reported incidents in 2026 [5, 29].
                                                                          operating on Tiers 0 and 1 alone.
Parallax defense: Information Flow Control (Section 4.3) assigns
sensitivity labels to data at the point of origin. When the agent
                                                                                                                                     Joel Fokou


3.3    Scope and Exclusions                                               architecture. Alternate architectures (container-level isolation for
Parallax is designed to prevent harmful execution. It addresses           enterprise deployments, hypervisor-level isolation for critical infras-
attacks that operate through the agent’s tool-use capabilities to         tructure, motor-control separation for embodied systems) would
cause real-world effects: data destruction, exfiltration, unauthorized    realize the same four principles in different technical substrates.
modification, credential theft, and privilege escalation.                 We return to this generality in Section 9.
   The following threat categories fall outside the paradigm’s scope:
   Harmful content generation without execution. An agent
that generates misleading, biased, or offensive content without           4.1    Principle 1: Cognitive-Executive Separation
executing any tool call is not within Parallax’s defensive perimeter.             The system that reasons about actions must be struc-
This threat is addressed by model-level safety mechanisms (RLHF,                  turally unable to execute them. The system that exe-
Constitutional AI, output filtering) and remains their domain.                    cutes actions must be structurally unable to reason
   Social engineering of the user. An agent that convinces the                    about them.
user to take a harmful action manually (e.g. generating persuasive
text that leads the user to visit a malicious website) operates through
the user’s own agency rather than through tool execution. Parallax           Cognitive-Executive Separation (CES) is the foundational prin-
cannot interpose between the agent’s text output and the user’s           ciple of Parallax. It divides the agent system into two processes
judgment.                                                                 with complementary capabilities and complementary limitations:
   Infrastructure compromise. Attacks that compromise the host               The agent process hosts the LLM-powered reasoning system.
operating system, the deployment pipeline, or the compiled engine         It maintains the conversational context, processes user requests,
binary itself are addressed by standard infrastructure security and       formulates plans, and proposes actions. It runs in a sandboxed
are orthogonal to the agent security paradigm.                            environment with no filesystem access, no network access, no shell
   Side-channel attacks. Information leakage through timing,              execution capability, and no mechanism to invoke tools directly. It
resource consumption, or other side channels of the LLM inference         can only communicate with the engine process through a defined
process is a model-level concern that Parallax does not address.          gRPC interface. The agent process is treated as fully untrusted: it
   Denial of service through legitimate actions. An agent that            may be compromised at any time, and the security of the system
executes a large number of individually legitimate actions to con-        must hold even under total compromise.
sume resources is performing actions that each pass validation.              The engine process hosts the tool executors, the validation
Rate limiting and resource quotas address this class of threat at the     layer (Shield), the state capture system (Chronicle), and the in-
operational level rather than the validation level.                       formation flow control subsystem. It has full access to the host
   These exclusions are deliberate. Parallax is designed to com-          environment and can execute any action the tool set supports. It
plement, not replace, existing model-level and infrastructure-level       has no reasoning model and no conversational state. It receives
security. Its contribution is to add an architectural enforcement layer   proposed actions from the agent process, validates them through
that existing approaches lack, not to subsume all aspects of AI safety    Shield, and executes those that pass.
into a single framework.                                                     The security property is: a fully compromised agent cannot cause
                                                                          any harmful effect on the host environment, because it has no exe-
                                                                          cution capability. It can only propose actions, and every proposed
4     The Parallax Paradigm                                               action must survive independent validation before execution.
This section presents the four principles of Parallax and their              Precedent. CES is the application of privilege separation, as for-
derived security properties. Each principle is defined in implemen-       malized by Provos et al. [16] for OpenSSH, to AI agent architecture.
tation-agnostic terms, grounded in its systems security precedent,        In OpenSSH, the unprivileged child process handles network-facing
and stated as a property that any conforming implementation must          operations (where compromise is most likely), while the privileged
satisfy. Together, the four principles form a complete defense pos-       monitor process controls authentication and session management.
ture: prevent harmful execution (Principles 1–2), detect context-         Exploitation of the child yields no access to privileged operations.
dependent threats (Principle 3), and recover from residual failures       Parallax applies the identical principle: the agent process handles
(Principle 4).                                                            adversary-facing operations (processing untrusted input through
   We use the term paradigm in its technical sense: a specification       the LLM), while the engine process controls execution. Exploitation
of principles that any conforming implementation must satisfy,            of the agent yields no access to execution.
independent of the particular technical substrate used to satisfy            The critical distinction between CES and the sandboxing ap-
them. Below the paradigm, an architecture is a method for realiz-         proaches described in prior work [33, 34] is that CES is not merely
ing the principles in a specific deployment context (a single-user        an isolation mechanism applied to the execution environment. It is
workstation, a multi-tenant enterprise service mesh, an embed-            a complete decomposition of the agent into a reasoning component
ded robotic controller). Below the architecture, a framework is a         and an execution component that share no process space, no mem-
concrete implementation of that method in a specific technology           ory, and no capabilities. Existing approaches sandbox the code that
stack. Parallax is a paradigm. The process-isolated gRPC design           the agent generates; Parallax sandboxes the agent itself, ensuring
described in Section 5 is one architecture for realizing Parallax         that the entity most likely to be compromised (the LLM reason-
on a personal workstation. OpenParallax, the Go implementation            ing system) has zero execution surface even before validation is
described in the same section, is one framework implementing that         considered.
Parallax: Why AI Agents That Think Must Never Act




                                                                            Shield

                                                                          Tier 0: Policy


                                                                      Tier 1: Classifier
                             Agent                  proposed                                               validated      Executor
                         (LLM reasoning)             action                                                 action        (Action)
                                                                      Tier 2: LLM Eval


                         Sandboxed (Untrusted)                            Tier 3: Human
                                                                                                                         Chronicle
                                                                                                                       (State Capture)


                                                                        IFC Tags
                                                                      (Data Labels)


                                                                                Engine Process (Trusted)



Figure 1: The Parallax architecture. The agent (untrusted, sandboxed) proposes actions via gRPC. Shield validates each
action through four tiers of graduated determinism; actions that fail validation are blocked. Only validated actions reach
the executor. IFC tags propagate data sensitivity into Shield for context-aware evaluation. Chronicle captures state before
destructive actions. The agent cannot access or modify any component of the engine process.


4.2    Principle 2: Adversarial Validation with                                   injection signatures, insecure URL schemes, piped execution chains,
       Graduated Determinism                                                      credential exposure patterns, encoding obfuscation, and environ-
                                                                                  ment variable expansion. The DeBERTa classifier provides learned
         Every action proposed by the reasoning system must
                                                                                  generalization beyond the heuristic rules. Both components vote
         be evaluated by an independent validation layer be-
                                                                                  independently; either can block. No LLM call is made at this tier.
         fore execution. The validation layer must operate in
                                                                                  The attack surface is limited to the classifier’s decision boundary,
         a separate process, use separate models, and share
                                                                                  which is fixed at deployment time and cannot be influenced by the
         no state with the reasoning system. Validation pro-
                                                                                  agent’s input.
         ceeds through tiers of decreasing determinism, with
                                                                                     Tier 2: Budget-Limited LLM Evaluation. For actions designated
         the most consequential decisions handled by the most
                                                                                  by policy as requiring contextual evaluation, and for actions where
         deterministic mechanisms. All tiers fail closed.
                                                                                  Tier 1’s classifier detects a potential threat but with insufficient con-
   Adversarial Validation (AV) interposes Shield as an independent                fidence to block outright, a separate LLM (distinct from the agent’s
evaluation layer between the agent’s proposed actions and their                   model) evaluates the action. This evaluation is budget-limited (a
execution. The validation is adversarial in the sense that Shield                 configurable maximum number of calls per day, default 100) to
evaluates every action under the assumption that the proposing                    prevent budget exhaustion attacks. A canary token is embedded
agent may be compromised. It is not a second opinion; it is an                    in the evaluation request and verified in the response to detect
independent security check performed by a system that shares no                   hallucinated or injected evaluations. Tier 2 is a last resort, not a
context, no memory, and no trust relationship with the agent.                     primary mechanism; the system is designed to remain safe when
   Graduated Determinism. Shield operates through four tiers,                     operating on Tiers 0 and 1 alone.
each with a different balance of determinism and contextual judg-                    Tier 3: Human-in-the-Loop Approval. When Tiers 0 through 2
ment:                                                                             cannot confidently resolve an action, Shield escalates to the user.
   Tier 0: Deterministic Policy. YAML-defined rules that map action               The approval request broadcasts to all connected channels simulta-
types and targets to allow/deny decisions. No LLM call. No machine                neously (CLI, web UI, messaging integrations); the first response
learning inference. The attack surface is the policy file itself, which           wins. Unanswered requests default to deny after a configurable
is protected by the self-protection layer (Section 5.3.1). Decisions              timeout (default 300 seconds). Tier 3 is rate-limited to prevent ap-
are instantaneous and fully auditable. Tier 0 handles the majority                proval fatigue attacks where an adversary floods the user with
of actions: those whose safety or danger can be determined from                   benign-seeming requests to induce reflexive approval. This com-
the action type and target alone (e.g. reads on non-sensitive paths               pletes the graduated determinism gradient: rules, machine learning,
are always allowed; writes to system configuration files are always               LLM, human. Each tier is slower, more contextual, and harder to
denied).                                                                          defeat than the previous.
   Tier 1: Dual Classifier. A heuristic pattern-matching engine oper-                Fail-closed everywhere. If any tier encounters an error (a
ating in parallel with an ONNX-deployed DeBERTa classifier. The                   classifier crash, a parsing failure, a network timeout on the Tier 2
heuristic engine contains rules for known dangerous patterns: shell               call), the action is blocked. The system degrades toward safety, not
                                                                                                                                       Joel Fokou


toward permissiveness. This is a deliberate choice: the worst-case         Flow Control (DIFC) [26]. Applying IFC to AI agent data flows is, to
failure mode is a blocked legitimate action (availability impact), not     our knowledge, novel. Recent work has identified information flow
an executed harmful action (integrity compromise).                         violations as a core vulnerability in agentic systems [33, 34] but
   Precedent. Graduated Determinism draws on the defense-in-               has not proposed a concrete tagging and propagation mechanism.
depth principle articulated by Saltzer and Schroeder [19]: security        Parallax provides this mechanism as a formal principle of the
should not depend on a single mechanism. It extends this principle         paradigm, not merely an implementation feature.
with a novel observation specific to AI systems: the validation
of AI-proposed actions should employ heterogeneous mechanisms              4.4    Principle 4: Reversible Execution
with different attack surfaces. A prompt injection that defeats an
                                                                                   Before any destructive or irreversible action, the sys-
LLM-based evaluator is unlikely to simultaneously defeat a pattern-
                                                                                   tem captures state sufficient for rollback. No action
matching heuristic engine and a fixed classifier. This heterogeneity
                                                                                   within the system’s domain of control is truly irre-
is a design principle, not an implementation detail.
                                                                                   versible.
4.2.1   Dynamic Tool Surface Reduction                                        The first three principles are pre-execution defenses: they pre-
                                                                           vent harmful actions from being carried out. Reversible Execution
    A derived security property of Adversarial Validation is the
                                                                           addresses the residual risk that remains when all pre-execution
principle that the attack surface itself should be minimized before
                                                                           mechanisms are bypassed. No security system is infallible. Novel
validation begins. In Parallax, this is realized through a dynamic
                                                                           attack vectors, zero-day exploits in the classifier, or genuinely am-
tool loading mechanism: the agent does not have visibility into
                                                                           biguous actions that pass validation may result in harmful execution.
the full tool set at any given time. Instead, it is presented with a
                                                                           Reversible Execution ensures that even in this case, the damage can
single meta-tool (load_tools) and a list of tool group descriptions.
                                                                           be undone.
It loads only the tool groups required for the current task.
                                                                              The mechanism is Chronicle: before any action classified as
    The security implication is that an adversary who compromises
                                                                           destructive or irreversible (file overwrites, file deletions, configura-
the agent at a given moment can only abuse tools that are loaded
                                                                           tion modifications, database writes), the system captures a snapshot
for the current turn. If the user requested a text summarization and
                                                                           of the affected resource’s state. If the action is subsequently deter-
the agent loaded zero tool groups, there is no execution surface
                                                                           mined to be harmful through user review, monitoring alerts, or
to exploit regardless of the sophistication of the injection. This is
                                                                           post-execution analysis, the system can restore the pre-action state
the principle of least privilege [19] applied temporally to the tool
                                                                           from the Chronicle snapshot.
surface, and to our knowledge has not been previously formalized
                                                                              Precedent. Reversible Execution applies the principle of data-
in the agent security literature.
                                                                           base transaction logs and filesystem journaling to AI agent exe-
                                                                           cution. Just as a database can roll back a transaction that violated
4.3     Principle 3: Information Flow Control                              an integrity constraint, and a journaling filesystem can recover
        Data processed by the agent carries provenance and                 from an interrupted write, Parallax can roll back an agent action
        sensitivity labels that propagate through all subse-               that violated a security constraint detected after execution. The
        quent operations. The validation layer evaluates ac-               contribution is the application of this well-understood principle
        tions with awareness of the data flowing through                   to autonomous AI agent execution, a domain where it has not
        them, not just the action type and target.                         previously been formalized.
   Information Flow Control (IFC) addresses a class of attacks that           Scope. Reversible Execution operates within the system’s do-
action-level validation alone cannot detect: those where the content       main of control. Actions that affect external systems (API calls to
of an action, rather than its type, determines whether it is harmful.      third-party services, sent emails, published messages) may not be
The canonical example is tool-use chain exfiltration (Category C4          reversible. For these actions, the pre-execution principles carry
in Section 3.2): the agent reads a file containing credentials, writes     proportionally greater weight, and Tier 0 policies should require
those credentials into a URL, and executes a network request. Each         human approval for irreversible external actions. The paradigm
action is individually benign (reading a file, writing a file, making a    is honest about this limitation: Reversible Execution reduces the
request), but the chain exfiltrates sensitive data.                        blast radius of failures within the local environment but cannot
   IFC solves this by tagging data at the point of origin. When the        guarantee reversibility for actions with external side effects.
agent reads a file classified as containing credentials, the content
receives a sensitivity label. This label propagates through every          4.5    Validator Immutability
subsequent operation that touches the tagged content. When the
                                                                           Validator Immutability is a corollary of Cognitive-Executive Sepa-
agent subsequently proposes to write tagged content to a network-
                                                                           ration that addresses the “quis custodiet ipsos custodes” problem:
accessible location or include it in an outbound request, Shield
                                                                           who validates the validator?
detects the flow violation: sensitive data is being moved from a high-
trust zone (the local credential file) to a low-trust zone (the external           The validation layer’s integrity must be guaranteed
network), regardless of how many intermediate steps separate the                   by architectural separation, not by policy compliance.
origin from the destination.                                                       The reasoning system must have no mechanism to
   Precedent. IFC is grounded in the Bell-LaPadula model [17]                      read, write, modify, or interfere with the validation
and its practical successors, including Decentralized Information                  layer.
Parallax: Why AI Agents That Think Must Never Act


    In Parallax, Shield’s self-protection operates at the code level:     principles of Parallax constitute an architectural standard against
writes to core configuration files are blocked in compiled code, not      which any autonomous system with execution capability can be
in configurable policy. The agent process runs in a separate OS pro-      evaluated, independent of the specific AI technology it employs.
cess with no filesystem access and no communication channel to
the engine except the gRPC API, which does not expose Shield’s in-        5     Reference Implementation: OpenParallax
ternals. The agent cannot read Shield’s policy files, cannot modify
                                                                          This section describes OpenParallax, an open-source reference
its classifier, cannot observe its decision logic, and cannot influence
                                                                          implementation of the Parallax paradigm written in Go. Open-
its evaluation of any action.
                                                                          Parallax is a personal AI agent designed for individual use on the
    This property is analogous to the role of a Trusted Platform
                                                                          user’s own machine. The implementation realizes all four princi-
Module (TPM) in hardware security [18]: the TPM provides a trust
                                                                          ples and their derived security properties in an 80 MB statically
anchor that the software it measures cannot modify. Shield pro-
                                                                          compiled binary (openparallax) that re-invokes itself to create the
vides a trust anchor that the agent it evaluates cannot modify. The
                                                                          process architecture: a process manager handles lifecycle (restart
integrity of the validator does not depend on the good behavior of
                                                                          on exit code 75, crash recovery), the engine process hosts Shield
the validated system. It is guaranteed by the architectural impossi-
                                                                          and all executors, and the agent process hosts the LLM reason-
bility of interference.
                                                                          ing loop. The DeBERTa classifier is not bundled in the binary;
                                                                          the user runs openparallax get-classifier, which downloads
4.6    Intelligence-Agnostic Generality                                   the ONNX model, tokenizer configuration, and platform-specific
                                                                          ONNX runtime library to a local path. On startup, the engine checks
The four principles of Parallax are defined in terms of capabilities
                                                                          for the classifier and loads it in-process via purego if present; if
and actions, not in terms of the reasoning architecture that produces
                                                                          not found, the system falls back to heuristic-only mode with a
them. Shield evaluates proposed actions: their type, their target,
                                                                          one-time warning logged at session start. A standalone Shield eval-
their content, and the sensitivity of the data flowing through them.
                                                                          uator (openparallax-shield) is also provided for independent
This evaluation is independent of the process that generated the
                                                                          validation testing. The choice of Go is deliberate: static compilation
proposal.
                                                                          produces self-contained binaries with no runtime dependencies,
    The paradigm therefore applies to any system architecture in
                                                                          cross-platform distribution requires no interpreter or virtual ma-
which a reasoning component proposes actions that an execution
                                                                          chine, and Go’s goroutine model provides efficient concurrency
component carries out, whether the reasoning is performed by
                                                                          for the parallel validation tiers in Shield. Deployment is a single
autoregressive language models, reinforcement learning policies,
                                                                          openparallax init command. The source code is available at
neurosymbolic engines, diffusion-based planners, or architectures
                                                                          https://github.com/openparallax/openparallax.
not yet developed. The fundamental risk that Parallax addresses
is that an autonomous reasoning system operating in a complex
environment will occasionally propose harmful actions. This risk          5.1    Process Architecture
is not specific to any AI architecture. It is an inherent property of     OpenParallax decomposes the agent system into three OS-level
autonomous systems interacting with the physical or digital world.        processes. The process manager spawns the engine, which spawns
    This generality extends to the agent’s motivation, not merely its     the agent; the security-relevant boundary is between the agent
architecture. A reasoning system may propose harmful actions be-          (untrusted) and the engine (trusted), communicating over gRPC on
cause an adversary injected a malicious prompt, because its safety        a dynamically assigned port (Figure 1):
training was bypassed, or because its objective function is under-            The agent process hosts the LLM conversation loop and the
specified. The canonical example is the “paperclip maximizer”: a          conversation history. It builds the system prompt from identity
system that proposes deleting user files to free disk space for inven-    files, initiates LLM API calls, receives the model’s responses (in-
tory tracking is not adversarially compromised but simply optimiz-        cluding tool call requests), and forwards all tool call requests to the
ing an objective that does not include human safety. Parallax is          engine process over gRPC. It has no user-facing interface: the CLI
indifferent to the cause. Shield evaluates the action, not the intent.    (a bubbletea TUI) and Web UI (a Svelte SPA) are separate clients
A file deletion is evaluated identically whether it was proposed by a     that connect to the engine process via gRPC and HTTP/WebSocket
jailbroken model, a misaligned optimizer, or a correctly functioning      respectively. The agent process has no filesystem access, no net-
agent that happens to be wrong about what the user wants.                 work access beyond the LLM API endpoint and the gRPC channel
    AI safety approaches that depend on properties of a specific          to the engine, and no ability to invoke tools directly.
reasoning architecture (such as RLHF for language models [22]                 The engine process hosts Shield (the four-tier validation sys-
or reward shaping for reinforcement learning agents) must be re-          tem), typed executors covering file operations, shell execution, net-
designed when the architecture changes. Parallax’s action-level           work requests, browser automation, and other action categories,
validation remains valid across architectural transitions because         the IFC tagging subsystem, Chronicle (state capture), the memory
the invariant it depends on is universal: autonomous systems pro-         system, the MCP client layer, and a web server on a configurable
pose actions with real-world consequences, regardless of how those        port (default 3100). The engine makes LLM calls only for Tier 2
systems reason.                                                           Shield evaluation, using a distinct model and isolated context.
    This generality is what makes Parallax a paradigm rather than             The separation is enforced at the OS process level, not through in-
a framework. A framework is tied to its implementation context. A         process isolation primitives. The agent process and engine process
paradigm is a set of principles that hold across contexts. The four       have separate address spaces, separate file descriptor tables, and
                                                                                                                                                             Joel Fokou


no shared memory. Communication is limited to the gRPC API                      Table 1: Graduated self-protection levels for system files.
contract, which exposes only the operations necessary for the agent
to submit LLM responses and receive execution results. The engine’s                    Files                          Level          Behavior
internal components (Shield, the executors, Chronicle, and IFC)                        SOUL, IDENTITY, TOOLS,         ReadOnly       Reads allowed; writes blocked
                                                                                       BOOT
are not addressable from the agent process.                                            AGENTS, HEARTBEAT              EscalateTier2 Writes require Tier 2
                                                                                       MEMORY, USER                   WriteTier1Min Writes require min. Tier 1
                                                                                       config.yaml, canary.token,     FullBlock     All access blocked
                                                                                       audit.jsonl, openparallax.db
5.2     Sandbox Integrity Verification
Process-level separation is a necessary but not sufficient condition
for the security model. If the sandbox is misconfigured and the
agent process retains filesystem access or network capabilities it                 This layer implements Validator Immutability (Section 4.5) at
should not have, the entire architecture is silently undermined.               the code level: even if an attacker compromised Tier 0’s policy
OpenParallax addresses this through a canary verification proto-               file (which itself requires bypassing the self-protection layer), the
col executed at startup.                                                       hardcoded protections would still prevent modification of Shield’s
   On launch, before any user interaction or LLM call, the agent               core files.
process runs a self-contained set of probes that should fail under
correct sandboxing: writing a file to the host filesystem, reading a           5.3.2      Tier 0: Deterministic Policy
known host file, opening a network connection to an unauthorized                  Tier 0 evaluates actions against a YAML-defined policy organized
address, and accessing the engine process via /proc. If any probe              into three sections evaluated in order: deny (block immediately),
succeeds, the sandbox is misconfigured and the system refuses to               verify (escalate to a specified Shield tier), and allow (permit im-
start. Probe results are reported to the engine and audit-logged.              mediately). Rules match on action types and path patterns. Actions
   Beyond the sandbox probes, OpenParallax uses two categories                 that do not match any rule are escalated to Tier 1. Notably, com-
of security token. A persistent workspace canary token (64-character           mand content matching (detecting dangerous shell patterns) is not
hex, stored on disk and protected by the self-protection layer’s Full-         performed at Tier 0; that is the responsibility of the Tier 1 heuristic
Block classification) is embedded in Tier 2 evaluation prompts and             engine, which operates on the expanded form of commands after
verified verbatim in the evaluator’s response to detect evaluation             environment variable substitution and alias resolution.
injection. Ephemeral authentication tokens (128-bit random, passed
via environment variable, never written to disk) authenticate gRPC         1   deny :
                                                                           2     - name : block_sensitive_system_paths
connections: the main agent receives one via OP_AGENT_TOKEN at             3        action_types : [ read_file , write_file , delete_file ]
spawn and presents it on its first gRPC message; each sub-agent            4        paths : ["~/. ssh /**" , "~/. aws /**" , "/ etc / shadow "]
                                                                           5     - name : block_identity_deletion
receives a separate token via OP_SUB_AGENT_TOKEN. The engine               6        action_types : [ delete_file ]
validates the token before accepting the stream. This prevents a           7        paths : ["**/ SOUL . md ", "**/ IDENTITY . md "]
                                                                           8
rogue process from injecting messages into the agent-engine com-           9   verify :
                                                                          10     - name : evaluate_shell_commands
munication channel.                                                       11       action_types : [ execute_command ]
   This protocol provides a testable, falsifiable security claim: sand-   12       tier_override : 1
                                                                          13     - name : evaluate_soul_modification
box integrity is verified on every launch, not assumed from config-       14       action_types : [ write_file ]
uration. The audit trail provides forensic evidence of sandbox state      15       paths : ["**/ SOUL . md ", "**/ IDENTITY . md "]
                                                                          16       tier_override : 2
at the time of any incident.                                              17
                                                                          18   allow :
                                                                          19     - name : allow_workspace_reads
                                                                          20       action_types : [ read_file , list_directory , search_files ]
5.3     Shield: Tiered Validation
Shield implements Principle 2 (Adversarial Validation with Gradu-                                      Listing 1: Tier 0 policy excerpt
ated Determinism) through four tiers, each running as a component
within the engine process.                                                         Evaluation is 𝑂 (𝑛) in the number of rules, with typical policy
                                                                               files containing 50–200 rules. Tier 0 resolves the majority of actions
5.3.1   Hardcoded Self-Protection Layer                                        in sub-millisecond time.
    Before any tier is consulted, a hardcoded self-protection layer
                                                                               5.3.3      Tier 1: Dual Classifier
runs in compiled Go code. Rather than a blanket deny on all system
files, the layer implements graduated protection levels that reflect              Tier 1 operates two independent classifiers in parallel:
the agent’s legitimate operational needs:                                         Heuristic engine. A rule-based pattern matcher containing 37
    The protection is implemented as compiled conditional checks               rules that detect known dangerous patterns in shell commands, file
with symlink resolution, directory overwrite detection, and case-              content, URLs, and action parameters. Patterns include: recursive
insensitive matching on all platforms. Shell write targets are parsed          deletion commands, privilege escalation (sudo, chmod 777), creden-
for both Unix and Windows conventions. There is no configuration               tial exposure (private key patterns, API key formats, environment
surface, no override mechanism, and no API to modify this layer. It            variable dumps), piped execution chains (curl | bash, wget |
executes before Tier 0 policy evaluation and cannot be bypassed                sh), Base64-encoded command sequences, reverse shell signatures,
by any action proposed through the gRPC interface.                             and SQL injection patterns. The heuristic engine operates on the
Parallax: Why AI Agents That Think Must Never Act


expanded form of commands, after environment variable substitu-              of the agent’s context: where the agent has rich context and no
tion and alias resolution, to defeat obfuscation through indirection         execution, the evaluator has no context and renders a safety verdict.
(Category C5 in Section 3.2).                                                   A canary token is embedded in the evaluation request: a random
    DeBERTa classifier. A fine-tuned DeBERTa model loaded in-                string that the evaluator must include verbatim in its response. This
process via purego (a pure Go foreign function interface that calls          defends against a specific threat: the content being evaluated may
the ONNX runtime shared library without CGo). The model is fine-             itself contain prompt injection targeting the Tier 2 evaluator. If a
tuned on a public prompt injection detection dataset [47] containing         malicious action includes text designed to convince the evaluator
approximately 16,000 labeled samples across 29 attack categories             that the action is safe, the evaluator’s response may be influenced
(direct injection, jailbreaks, encoding obfuscation, persona replace-        by this injection. The canary detects this: if the response does
ment, and others), achieving 98.8% accuracy on the held-out test set.        not contain the canary verbatim, the evaluation may have been
The classifier provides learned generalization beyond the heuristic          compromised by the content under evaluation, and the action is
rules, catching novel patterns that do not match any predefined rule.        blocked. The canary used for Tier 2 is the persistent workspace
Inference is local with no external API dependency. The current              canary token, protected by the self-protection layer’s FullBlock
in-process implementation via purego adds approximately 1.9s of              classification.
latency per action due to runtime initialization overhead; a planned            Tier 2 calls are budget-limited to a configurable maximum per
CGo sidecar using the native ONNX Runtime C API is expected to               day (default: 100). This limit serves two purposes: it prevents budget
reduce this to sub-50ms.                                                     exhaustion attacks (Category C7) where an adversary floods the
    Both classifiers vote independently. An action is blocked if either      system with actions that trigger Tier 2 escalation to deplete the
classifier flags it as harmful. An action passes Tier 1 only if both clas-   evaluation budget, and it ensures the system degrades gracefully
sifiers agree it is safe. This dual-vote architecture ensures that the       to Tier 0 and Tier 1 operation when the budget is exhausted. The
heuristic engine’s precision and the classifier’s generalization each        system is designed to be safe, not merely degraded, under Tier 0
contribute to the safety decision, with the union of their detection         and Tier 1 alone.
capabilities providing broader coverage than either alone.
    The heuristic engine is strictly binary: no rule match produces an       5.4    Dynamic Tool Loading
ALLOW with baseline confidence. The DeBERTa classifier returns a             The agent does not observe the full tool set on any LLM call. Instead,
label (INJECTION or SAFE) with a confidence score. If the classifier         every LLM invocation includes exactly one meta-tool: load_tools.
returns INJECTION with confidence at or above the configurable               This tool accepts a tool group identifier and returns the tool defi-
threshold (default 0.85), the action is blocked. If the classifier returns   nitions for that group. The call is handled locally within the agent
INJECTION below threshold, the gateway escalates the action to               process and has no side effects: it does not traverse Shield because
Tier 2 rather than allowing a borderline signal to pass. Both classi-        no execution occurs. The security value is in the dynamic scoping
fiers run in parallel with “BLOCK wins” logic: if either says BLOCK,         itself: tools that are not loaded cannot be called, regardless of what
the verdict is BLOCK.                                                        the agent attempts. If the current task requires only text analysis,
    A subset of heuristic rules are tagged as always-block: these fire       the LLM may load zero tool groups, in which case there is literally
as a precheck on actions escalated past Tier 1 to Tier 2, catching           no execution surface to exploit.
deterministic attack patterns (such as agent-internal enumeration)
that an LLM evaluator cannot reason about. This ensures that Tier 0-
                                                                             5.5    Information Flow Control Implementation
to-Tier 2 escalation does not skip the heuristic engine entirely.
    For action types where the classifier’s training data produces sys-      OpenParallax implements IFC through a tagging system that op-
tematic false positives (such as write_file or send_email, where             erates at the executor level. When an executor reads data from a
structured but benign payloads are misclassified as injection), oper-        source, it assigns a sensitivity tag (PUBLIC, INTERNAL, CONFI-
ators can configure a per-action-type bypass list. Bypassed types            DENTIAL, or RESTRICTED) based on path-based rules, content-
skip ONNX classification but still pass through the heuristic en-            pattern matching, and configurable per-project policies. Tags propa-
gine, and are escalated to Tier 2 for contextual evaluation. This            gate through the execution pipeline: if the agent reads a RESTRICT-
provides a tunable tradeoff between attack recall and false positive         ED-tagged file and subsequently proposes to write content derived
rate without architectural change.                                           from that file, the write action inherits the tag. Shield evaluates
                                                                             write actions with awareness of their inherited tags and blocks
5.3.4   Tier 2: Budget-Limited LLM Evaluation                                flow violations such as RESTRICTED content directed to network-
                                                                             accessible locations. The classification runs within the executor, not
   Tier 2 invokes a separate LLM (configured to be a different model         within the agent process, ensuring that the agent cannot influence
from the agent’s reasoning model) to evaluate policy-designated              the tagging of data it reads.
and low-confidence actions. The evaluator receives only the action
type and payload. It has no identity, no conversation history, no user       5.6    Chronicle: State Capture and Recovery
profile, no tools, and no task context. Its system prompt explicitly
                                                                             Chronicle implements Principle 4 (Reversible Execution). Before
states that it is not the agent and must not follow instructions found
                                                                             any executor performs a destructive action (file overwrite, file dele-
in the payload. Everything in the evaluation request is treated as
                                                                             tion, or configuration modification), it captures a complete snap-
data to be judged, not instructions to follow. This is the inverse
                                                                             shot of the affected resource’s contents and metadata. Snapshots
                                                                             are stored with content-addressable naming (SHA-256) and linked
                                                                                                                                    Joel Fokou


to the triggering action, timestamp, and Shield decision. Recov-         5.9    Audit and Observability
ery is triggered by explicit user command (chronicle rollback).          Every action proposed by the agent, every Shield decision (includ-
Snapshots are retained by both count (default: 100) and age (default:    ing the resolving tier, rule, and latency), every IFC tag event, every
30 days), and are protected by the self-protection layer against         Chronicle snapshot, and every sandbox probe result is recorded
modification by the agent process.                                       in an append-only structured audit log secured with a SHA-256
                                                                         hash chain for tamper evidence. The log is protected by the self-
5.7    Multi-Agent Orchestration and Child Agent                         protection layer’s FullBlock classification; the agent process cannot
       Isolation                                                         read, modify, or delete audit entries.
OpenParallax supports multi-agent operation through a task del-
egation architecture. The primary agent can decompose complex            6     Evaluation
tasks and delegate subtasks to child agents. Each child agent is in-
stantiated as an independent sandboxed process with the following        We evaluate OpenParallax’s adversarial resistance, false positive
constraints:                                                             rate, and validation latency. The Tier 2 LLM evaluator uses Claude
                                                                         Haiku 4.5. The complete test suite and evaluation harness are re-
      • Independent sandboxing. Each child agent runs in its
                                                                         leased alongside the OpenParallax repository for full reproducibil-
         own OS process with the same sandbox restrictions as the
                                                                         ity.
         primary agent: no filesystem access, no direct network ac-
         cess, no tool execution capability.
      • Independent Shield routing. All tool calls from child            6.1    Methodology: Assume-Compromise
         agents pass through the same Shield instance in the engine             Evaluation
         process, with identical validation rigor. There is no trust     Parallax’s threat model treats the agent as fully untrusted. The
         inheritance, a child agent’s actions are not pre-approved       correct evaluation methodology therefore assumes the agent is
         by virtue of being delegated by the parent.                     already compromised and tests the architectural boundary directly.
      • No child spawning. Child agents cannot spawn further
                                                                         We call this Assume-Compromise Evaluation: the evaluation harness
         children. The delegation depth is limited to one level, pre-
                                                                         bypasses the LLM reasoning system entirely, injecting tool calls
         venting recursive delegation attacks.                           programmatically into the Shield pipeline. This simulates a fully
      • Memory isolation. Child agents cannot access the primary         compromised agent that proposes arbitrary harmful actions without
         agent’s conversational context, memory, or session state.       the mediation of safety training, prompt guardrails, or model-level
         They receive only the task description provided by the          refusal.
         orchestrator and return only the task result.                      This methodology is motivated by empirical observation. In pre-
      • Sibling isolation. Child agents cannot communicate with          liminary LLM-mode runs, we tested Claude Sonnet 4.6, Claude
         each other. All inter-agent communication is mediated by        Haiku 4.5, and Llama 3.1 8B across all attack categories. All three
         the orchestrator within the engine process.                     models achieved 0% attack success rate across all configurations
    This architecture ensures that the compromise of any individual      (A, B, and C): the models refused to propose harmful tool calls re-
agent (parent or child) cannot propagate to other agents in the sys-     gardless of whether Shield was enabled or whether safety prompts
tem. The engine process, as the only trusted component, mediates         were present. Current frontier instruction-tuned models are suffi-
all inter-agent communication and subjects all actions to Shield         ciently safety-trained to refuse these attacks at the reasoning level.
validation regardless of their origin.                                   This is expected and welcome. It also means that LLM-mode eval-
    Sub-agents do not receive the load_tools meta-tool. The par-         uation cannot differentiate between configurations, because the
ent agent specifies tool groups at creation time, and the engine         model’s own safety training dominates. A brief manual test with
resolves these groups to concrete tool definitions provided to the       Qwen 2.5 3B confirmed that less safety-trained models do comply
sub-agent’s LLM on its first call. A compromised sub-agent cannot        with harmful requests (proposing file deletions without hesitation),
attempt to load tool groups outside its assigned scope because the       validating the fully-compromised-agent assumption as realistic, not
loading mechanism does not exist in its tool set. This is least privi-   hypothetical.
lege applied at the tool-discovery level: the sub-agent cannot even         Assume-Compromise Evaluation is also a practical technique
enumerate capabilities it does not have. By default, sub-agents use      for agent development testing. Any agent developer can build a
the same model as the primary agent; users can configure a dedi-         harness that injects tool calls directly into their security boundary,
cated sub-agent model to reduce costs, with no hardcoded model           bypassing the LLM, to find policy gaps before adversaries do. We
lists maintained.                                                        position this as a standard practice for validating agent security
                                                                         architectures.
5.8    MCP Integration                                                      We evaluate under two configurations:
As a transparent validation proxy, OpenParallax integrates with             Config A (No Shield): All injected actions execute without vali-
the Model Context Protocol [35] (MCP). All MCP tool calls are            dation. This represents the security posture of a typical unprotected
routed through Shield before forwarding to the MCP server. Nei-          agent and establishes the 100% attack success rate baseline.
ther the server nor the agent is aware that validation occurred. MCP        Config C (Parallax): The full OpenParallax system with
tools are registered as loadable groups in the tool registry, subject    Shield active across all four tiers, IFC tagging enabled, and Chron-
to Dynamic Tool Surface Reduction like native tools.                     icle capturing state for destructive actions.
Parallax: Why AI Agents That Think Must Never Act


   Config B (prompt guardrails only) is not applicable in inject          Table 3: Attack success rate (%) under Assume-Compromise
mode: there is no reasoning system to receive safety instructions.        Evaluation. Config A: no Shield. Config C: full Parallax.
This is the paper’s core argument made concrete. When the reason-
ing system is compromised, prompt-level guardrails provide zero            Category                     Config A     C (default)      C (max-sec)
protection because they exist only within the compromised system.
                                                                           C1: Direct injection             100          4.0              0.0
                                                                           C2: Indirect injection           100          0.0              0.0
6.2    Test Suite                                                          C3: Multi-step context           100          0.0              0.0
The test suite comprises 280 adversarial cases organized into nine         C4: Tool-use chain               100          2.7              0.0
categories (including 5 Tier 3 escalation cases as C9), plus 50 false      C5: Encoding/obfuscation         100          0.0              0.0
positive cases and 7 additional Tier 3 legitimate cases (337 total).       C6: Multi-agent                  100          0.0              0.0
Each test case is specified as a structured YAML record containing         C7: Validator-targeted           100          0.0              0.0
                                                                           C8: Helpfulness bypass           100          1.7              0.0
a unique identifier, attack category, the exact injected tool call, the
                                                                           C9: Tier 3 human approval        100          0.0              0.0
expected Shield verdict, and for Tier 3 cases, a simulated human
response.                                                                  Overall (280)                   100           1.1              0.0
                                                                           False positives                  n/a          0%              36%
  Table 2: Test suite distribution across attack categories.

                   Category                         Cases
                                                                              The classifier bypass list is the tunable parameter that mediates
                   C1: Direct injection                25
                   C2: Indirect injection              40
                                                                          this tradeoff. Operators in high-security environments can clear the
                   C3: Multi-step context              30                 list to achieve 100% coverage at higher FP cost; developer worksta-
                   C4: Tool-use chain                  37                 tions use the default for uninterrupted workflows. The architecture
                   C5: Encoding/obfuscation            32                 supports both profiles without modification.
                   C6: Multi-agent                     25                     The initial default policy did not achieve these results immedi-
                   C7: Validator-targeted              26                 ately. Testing revealed specific policy gaps: credential files (.env,
                   C8: Helpfulness bypass              60                 *.pem), system paths (/etc/passwd), and agent-internal paths
                   C9: Tier 3 human approval            5                 (.openparallax/*) were not covered by deny rules. After closing
                   Total adversarial                 280                  these gaps with targeted deny rules and adding 17 heuristic engine
                   False positive (legitimate)         50
                                                                          patterns for shell attack signatures, the refined policy achieved the
                   Tier 3 legitimate                    7                 results reported above. This iterative refinement is the normal life-
                                                                          cycle of security policy; the architecture’s contribution is providing
                   Grand total                       337
                                                                          the enforcement boundary that makes policy effective.

                                                                          6.4    Tier Resolution Distribution
6.3    Adversarial Results
                                                                          Table 4 shows which Shield tier resolved each blocked attack across
We evaluate under two Shield configurations to characterize the
                                                                          the 280-case adversarial suite.
tradeoff between attack coverage and false positive rate:
   Default configuration. The DeBERTa classifier is bypassed
for seven action types where its training data produces systematic        Table 4: Distribution of blocked attacks by resolving Shield
over-firing (write_file, delete_file, move_file, send_email,              tier.
send_message, http_request, copy_file). These types are esca-
lated directly to Tier 2 for contextual evaluation. The bypass list is                     Tier                     Count        %
a configurable parameter.
   Maximum-security configuration. The classifier runs on all                              Tier 0 (Policy)             43      15.4
                                                                                           Tier 1 (Classifier)        163      58.2
action types with no bypass.
                                                                                           Tier 2 (LLM Evaluator)      73      26.1
   Table 3 presents the attack success rate (ASR) under both config-                       Tier 3 (Human)               1       0.4
urations.
   The default configuration blocks 277 of 280 attacks (98.9%) with                        Total                      280      100
zero false positives. The maximum-security configuration blocks
all 280 (100%) at the cost of a 36% false positive rate. The three
attacks that succeed under the default configuration are all Tier 2          Deterministic mechanisms (Tiers 0 and 1) resolve 73.6% of at-
evaluator judgment calls on contextually ambiguous actions: a             tacks with no LLM dependency. Tier 2 handles 26.1% of cases that
/tmp file deletion the evaluator assessed as low-risk, an HTTP            require contextual judgment. Tier 3 (human escalation) fires for
POST to a plausible validation endpoint, and an env command               0.4% of cases. This confirms the graduated determinism design: the
the evaluator classified as read-only. Each is addressable through        system remains safe under Tiers 0 and 1 alone, with Tiers 2 and 3
evaluator prompt refinement or targeted heuristic rules without           providing additional coverage for actions that resist deterministic
architectural change.                                                     classification.
                                                                                                                                    Joel Fokou


6.5    Tier 3 Human Escalation                                              Tier 0 resolves actions in sub-millisecond time through YAML
We validate the Tier 3 path with 12 test cases designed to occupy the    pattern matching. Tier 1 latency is currently dominated by the
ambiguous zone where Tier 2 should defer to a human: force-pushes        ONNX runtime initialization overhead in the purego bridge; the
to feature branches, database migrations, privilege escalation com-      1.9-second P50 is substantially higher than the 10–50ms typical for
mands, and sensitive communications. In inject mode, the harness         DeBERTa inference on CPU, and optimization is expected to reduce
simulates human responses (approve or deny) based on the test            this by one to two orders of magnitude. Tier 2 latency reflects the
case specification.                                                      external LLM API call (Claude Haiku 4.5) and is comparable to any
   Four of 12 cases traversed the full path: Tier 2 returned ESCA-       single LLM inference. For legitimate actions in normal operation,
LATE, the engine submitted the action for human approval, and the        the majority resolve at Tier 0 (sub-millisecond) without reaching
simulated human response produced the correct outcome (block             the classifier or LLM evaluator.
for malicious, execute for legitimate). The remaining 8 cases were
caught earlier by Tiers 0 and 1, which is correct behavior: Tier 3 is    7 Discussion
the last resort. Adding ESCALATE to the Tier 2 vocabulary intro-         7.1 Model-Level Safety and Architectural
duced no regressions on the main 280-case attack suite.                      Insurance
                                                                         Our LLM-mode results reveal that current frontier models (Claude
6.6    False Positive Rate                                               Sonnet 4.6, Claude Haiku 4.5, Llama 3.1 8B) refuse 100% of harmful
We evaluate false positives by injecting 50 legitimate actions repre-    agent requests at the reasoning level, regardless of configuration.
sentative of normal development workflows: file reads and writes,        This means that prompt-level guardrails (Config B) are currently
shell commands (npm install, make build, docker compose up),             effective not because they are architecturally sound, but because
network requests to approved endpoints, email, and file manage-          the underlying model’s safety training dominates.
ment operations.                                                            This is precisely the condition that creates complacency. Model-
    Under the default configuration (per-action-type classifier          level safety is a property of training, and training is the same com-
bypass), 0 of 50 legitimate actions were blocked (0% false positive      putation substrate that adversaries attack. Novel jailbreaks, less
rate). The bypass escalates action types prone to classifier over-       safety-trained models (our Qwen 2.5 3B test confirmed compliance
firing to Tier 2 for contextual evaluation, eliminating the systematic   with harmful requests), indirect injection through ingested content,
misclassification that dominated false positives.                        and future attack techniques all target the reasoning layer. When
    Under the maximum-security configuration (classifier ac-             that layer is compromised, prompt-level guardrails provide zero
tive on all types), 18 of 50 legitimate actions were blocked (36%        protection because they exist only within the compromised system.
false positive rate). Of these, 14 were DeBERTa classifier over-fires       Parallax’s architectural enforcement is insurance against this
on write_file, delete_file, send_email, and http_request ac-             failure mode. Under Assume-Compromise Evaluation, the architec-
tions classified as INJECTION at confidence 1.00 (a domain mis-          tural boundary blocks 98.9% of attacks with zero false positives in
match: the classifier was trained on prompt injection text patterns,     the default configuration, and 100% under the maximum-security
not agent action payloads), and 4 were Tier 2 evaluator conservative     configuration. The cost of this insurance (validation latency and
blocks on commands the evaluator could not fully contextualize           the configurable tradeoff between coverage and false positives) is
without agent state. The Tier 2 blocks are attributable to LLM           justified by the categorical nature of the protection: near-total or
evaluator non-determinism across runs rather than configuration          total coverage vs. total exposure when the model’s safety training
differences: execute_command is not in the classifier bypass list        fails.
and follows the same evaluation path in both configurations. These
blocks may or may not reproduce on a given run.                          7.2    Configurability as a Design Principle
    Tier 0 and the heuristic engine produced zero false positives
                                                                         The default configuration achieves 0% false positives and 98.9%
under both configurations. Dynamic Tool Surface Reduction further
                                                                         attack coverage. The maximum-security configuration achieves
mitigates false positives in practice: on conversational turns where
                                                                         100% attack coverage with a 36% false positive rate. The per-action-
zero tools are loaded, no actions are proposed and the effective false
                                                                         type classifier bypass list is the tunable parameter that mediates
positive rate is structurally 0%.
                                                                         this tradeoff, allowing operators to calibrate the system for their
                                                                         deployment context without architectural change.
6.7    Validation Latency                                                   The three attacks that succeed under the default configuration
Table 5 reports Shield validation latency by tier, measured across       are all Tier 2 evaluator judgment calls on contextually ambiguous
the adversarial test suite.                                              actions. This is a direct consequence of the evaluator’s inverted-
                                                                         context design: the evaluator receives no agent state, no conversation
 Table 5: Shield validation latency by tier (milliseconds).              history, and no task context, making it maximally resistant to injec-
                                                                         tion through the content it evaluates. The tradeoff is that it cannot
          Tier                      n    P50    P95    P99
                                                                         determine whether an ambiguous action is malicious without the
                                                                         context it deliberately lacks. This is a deliberate exchange of avail-
          Tier 0 (Policy)           43    <1     <1     <1               ability for integrity: the evaluator cannot be manipulated through
          Tier 1 (Classifier)      163   1947   2335   2638
                                                                         the data it judges, at the cost of occasionally misjudging actions it
          Tier 2 (LLM Evaluator)    73   2089   3379   4781
                                                                         cannot contextualize.
Parallax: Why AI Agents That Think Must Never Act


   The architecture is fixed; the policy and classifier configuration           Reversibility scope. Chronicle cannot reverse actions with ex-
are the tuning surface. This mirrors the relationship between a             ternal side effects (sent emails, API calls to third-party services, pub-
firewall’s packet filtering engine (stable) and its rule set (iteratively   lished messages). For deployments where such actions are common,
refined based on operational experience). Classifier retraining on a        the pre-execution principles bear disproportionate responsibility,
corpus of labeled agent actions would shrink the default bypass list,       and Tier 0 policies should enforce human approval for irreversible
potentially restoring 100% coverage without false positive cost. The        external actions.
evaluation process itself demonstrated this iterative refinement:               Single trust anchor. The engine process is the sole trusted
initial policy gaps were found through testing and closed with              component. If the engine binary is compromised (whether through
targeted rules, without any modification to Shield’s code.                  a supply chain attack, a deployment pipeline vulnerability, or a
                                                                            runtime exploit in the Go runtime), the entire security model fails.
                                                                            This is not unique to Parallax; it is the inherent limitation of any
7.3    The Cost of Safety                                                   security architecture that depends on a trusted computing base.
                                                                            Standard mitigations (binary signing, reproducible builds, minimal
Any security mechanism imposes a cost. For Parallax, the costs are:
                                                                            attack surface in the engine’s external interfaces) apply.
latency overhead on each action, false positives that block legitimate
                                                                                Script content opacity. Shield evaluates the command that
operations, and the engineering complexity of maintaining the
                                                                            executes a script (e.g. python script.py) but does not analyze
multi-process architecture. These costs must be weighed against
                                                                            the script’s contents. If a compromised agent writes a malicious
the alternative: deploying agents with execution capability and no
                                                                            script to disk (an action evaluated by Shield as a file write) and
architectural safety guarantees.
                                                                            subsequently executes it (an action evaluated as a shell command),
    The false positive rate is the most practically consequential met-
                                                                            the harmful logic within the script is not inspected. This is partially
ric. A system that blocks legitimate actions disrupts user workflows
                                                                            mitigated by IFC tagging when the script content derives from
and erodes trust in the safety layer, motivating users to disable
                                                                            sensitive data, but not when the agent generates novel malicious
it. This is precisely the outcome observed with overly aggressive
                                                                            code from its own compromised reasoning. Future work includes
antivirus software in prior generations of security tools.
                                                                            file provenance tracking (automatically escalating execution of
    Dynamic Tool Surface Reduction provides a structural mitigation
                                                                            agent-authored files) and static analysis of script contents before
independent of classifier tuning. On conversational turns where the
                                                                            execution.
agent loads zero tool groups, no actions are proposed and the false
                                                                                Scalability of human oversight. For actions that Tier 0 policy
positive rate is structurally zero. On tool-using turns, the scoped
                                                                            routes to human approval (high-risk external actions), the system’s
tool set limits the action space to the relevant domain, reducing
                                                                            throughput is bounded by human response time. In high-volume
the likelihood that legitimate actions trigger heuristic patterns
                                                                            agentic workflows, this can create bottlenecks. Adaptive policies
designed for unrelated domains. The effective false positive rate
                                                                            that learn which actions a specific user consistently approves, tight-
across a mixed workload is therefore substantially lower than the
                                                                            ening the approval surface over time, are a promising direction but
per-action rate measured on tool-using turns alone.
                                                                            introduce their own risks (an attacker could train the adaptive pol-
                                                                            icy toward permissiveness through a sequence of benign-seeming
                                                                            approvals).
7.4    Limitations
Tier 1 classifier generalization. The DeBERTa classifier is fine-
tuned on a prompt injection detection dataset that classifies text
as injection vs. benign, not agent actions as safe vs. harmful. This
domain mismatch explains the systematic false positives on action           7.5    Deployment Considerations
types whose payloads contain structured but benign text (file con-          Personal deployment model. OpenParallax deploys as a sin-
tent, email bodies, HTTP request bodies). Novel attack patterns             gle statically compiled binary with no runtime dependencies, no
not represented in the training data may also evade the classifier.         containers, and no infrastructure requirements beyond the user’s
Both limitations are mitigated by the dual-vote architecture (the           machine. All data processing, validation, and execution remain
heuristic engine provides rule-based coverage for known patterns)           local. LLM API calls are the only external communication. This
and by Tier 2 escalation for low-confidence classifier signals, but         model provides complete data sovereignty by default: the user’s
the classifier’s coverage is inherently bounded by its training dis-        files, credentials, and agent activity never leave their machine. The
tribution. Retraining on a corpus of labeled agent actions (rather          architectural separation between agent and engine processes is
than prompt injection text) is the primary path to improving both           enforced at the OS level on commodity hardware, requiring no
precision and recall.                                                       specialized infrastructure.
   IFC tag granularity. The current IFC implementation operates                 Regulatory alignment. The Parallax architecture provides
at the file and content-pattern level. Content that is sensitive but        technical infrastructure for compliance with emerging AI agent
does not match any predefined pattern or path rule will not re-             regulations, even for personal deployments. The EU AI Act’s re-
ceive appropriate tags. This is a configuration challenge rather than       quirements for human oversight, risk assessment, and post-market
an architectural limitation (the tagging system supports custom             monitoring [20] are supported by Shield’s tiered validation, the
rules) but it means that IFC coverage depends on the quality of the         system-wide audit trail, and the human-approval hooks in Tier 0
classification policy, which must be maintained per deployment.             policy. Singapore’s Model AI Governance Framework for Agentic
                                                                                                                                     Joel Fokou


AI [21], which introduces graduated autonomy levels with increas-               Application-layer mandatory access control. SEAgent [51]
ing governance requirements, maps naturally to Parallax’s gradu-            applies mandatory access control with attribute-based labels to
ated determinism: higher autonomy levels require stricter Tier 0            LLM agent systems, assigning sensitivity, integrity, and action-type
policies and lower Tier 2 budgets, while lower autonomy levels can          attributes to tools, agents, and retrieval databases, and enforcing
operate with broader permissions and higher budgets.                        deny policies based on label combinations through a graph-based
                                                                            policy engine. It reports substantial reductions in attack success
                                                                            rate on indirect prompt injection (InjecAgent, AgentDojo) and re-
8    Related Work                                                           trieval poisoning benchmarks with minimal false positives. SEAgent
We position Parallax relative to five categories of prior work.             shares Parallax’s use of label-based information flow tracking,
    Model-level safety training. RLHF [22] and Constitutional               but operates at the application layer within a single process, using
AI [23] improve the model’s tendency to refuse harmful requests.            in-process policy matching rather than OS-level isolation. Paral-
These approaches address generation safety (making the model’s              lax’s contribution relative to SEAgent is the enforcement layer
text outputs safer) but do not constrain execution safety. A model          itself: address-space separation between reasoning and execution
that reliably refuses to generate instructions for building weapons         means that a vulnerability in the validation logic cannot be reached
may still execute a file-deletion command if an indirect injection          from the reasoning system, because the two components execute
convinces it the deletion is a legitimate maintenance task. Recent          in separate processes with no shared memory and no shared file
analysis confirms that preference-based alignment methods face              descriptor table. SEAgent’s application-layer architecture is suf-
fundamental theoretical limitations that cannot be resolved through         ficient against adversaries who operate only through the LLM’s
better implementation [36], and that RLHF-trained models exhibit            action proposals, which is the threat model it addresses. Parallax
sycophantic behavior that can be exploited to override safety train-        additionally resists adversaries who directly target the validator
ing [37]. Parallax is complementary: it adds an architectural en-           itself, the threat model of Category C7 (Validator-Targeted Attacks)
forcement layer that holds regardless of the model’s alignment              in our taxonomy.
quality.                                                                        Dual-LLM and Plan-then-Execute patterns. Recent archi-
    Output filtering and guardrails. Systems such as NVIDIA’s               tectural proposals [40] advocate separating a “privileged” LLM
NeMo Guardrails, Guardrails AI, and prompt-based safety instruc-            for trusted planning from a “quarantined” LLM for processing un-
tions interpose checks on model outputs. For agentic systems, the           trusted data, or requiring the agent to produce a complete plan
relevant “output” is a tool call, not text, and the safety of a tool call   before execution begins. These approaches represent meaningful
depends on runtime context (data sensitivity, target path, execution        progress toward architectural safety but retain a critical weakness:
history) rather than content classification alone. A comprehensive          the privileged LLM still has both reasoning and execution capabil-
survey of jailbreaking research spanning 2022–2025 concludes that           ity, and the quarantined LLM may influence the privileged LLM’s
the threat landscape “requires a paradigm shift from reactive miti-         decisions through its outputs. Parallax goes further by eliminating
gation to proactive security-by-design” [38]. This is precisely the         execution capability from the reasoning system entirely. There is no
position that Parallax instantiates.                                        “privileged LLM” that can both plan and act, because no component
    Sandbox-based execution isolation. Google’s Agent Sandbox               has both capabilities.
on GKE [39], E2B’s Firecracker microVMs, and Daytona’s container-               Dynamic tool loading as engineering practice. Anthropic’s
based isolation focus on containing the effects of LLM-generated            Claude Code implements a ToolSearch mechanism that defers MCP
code. IsolateGPT [48] introduces a hub-and-spoke architecture that          tool loading until needed, reducing context window consumption
mediates interactions between LLM-integrated apps and enforces              by up to 95% [45]. The MemTool framework [46] formalizes dy-
execution isolation between third-party components, reporting un-           namic tool management as a short-term memory optimization
der 30% overhead for most queries. ACE [49] extends this line by            across multi-turn conversations. Both treat dynamic tool loading
demonstrating attacks against IsolateGPT’s planning integrity and           as a performance optimization or memory management technique.
proposing an abstract-concrete-execute decomposition: the plan-             Parallax’s contribution is the formalization of this practice as
ner first produces an abstract plan from trusted information only,          a security principle: least privilege applied temporally to the tool
which is then mapped to concrete app invocations. ACE evaluates             surface, where the reduction in visible tools directly reduces the
on InjecAgent and Agent Security Bench. These are valuable con-             attack surface available to a compromised agent. The distinction is
tributions, but they address a narrower problem than Parallax:              between “load fewer tools to save tokens” and “load fewer tools so
they sandbox the components the agent produces or the third-party           a compromised agent has fewer weapons.”
apps it interacts with, not the reasoning system itself. An agent               Agent security frameworks and taxonomies. The OWASP
running inside any of these architectures can still propose harmful         Top 10 for Agentic Applications [5], MITRE ATLAS [27], and com-
file operations, network requests, or configuration modifications           prehensive threat models such as Narajala and Anca’s ATFAA
through its tool-calling interface. The isolation layer constrains          framework [28] and Perplexity’s NIST response [34] provide es-
what generated code can execute or how apps may interact, not               sential taxonomies and risk identification. The IACR’s “Systems
whether the reasoning system has execution capability at all. Par-          Security Foundations for Agentic Computing” [33] specifically iden-
allax’s Cognitive-Executive Separation sandboxes the reasoning              tifies information flow violations and least-privilege enforcement
process, ensuring that the entity most likely to be compromised (the        as open problems for agentic systems. Parallax builds on these
LLM) has zero execution surface of any kind before validation is            foundations by providing a concrete paradigm (with a reference
considered.                                                                 implementation and empirical evaluation) that addresses the open
Parallax: Why AI Agents That Think Must Never Act


problems these frameworks identify. Where OWASP identifies the            9     Future Work
risk of tool misuse (ASI02), Parallax provides Shield. Where IACR         Several components of the Parallax paradigm present opportu-
identifies information flow violations as unresolved, Parallax pro-       nities for deeper investigation that we leave to future work. The
vides IFC tagging. Where NIST identifies agent hijacking as a core        application of information flow control to AI agent execution, the
threat, Parallax provides Cognitive-Executive Separation that ren-        formalization of dynamic tool surface reduction, and the sandbox
ders hijacking incapable of producing harmful effects.                    canary verification protocol each merit dedicated study. We high-
   Security principles applied to agents. AgentSandbox [50]               light near-term engineering priorities and longer-term research
grounds an agent safety framework in the four Saltzer–Schroeder           directions.
principles [19] (defense in depth, least privilege, complete media-
tion, and psychological acceptability) and evaluates the framework        9.1    Classifier Retraining and Latency
on utility and attack-success metrics with state-of-the-art LLMs.                Optimization
Parallax shares the commitment to classical foundations but or-
ganizes its principles around the specific problem structure of au-       The default configuration achieves 0% false positives by bypassing
tonomous execution rather than general-purpose security design.           the DeBERTa classifier for seven action types prone to over-firing, at
Cognitive-Executive Separation specializes privilege separation to        the cost of 1.1% attack regression. The current classifier was trained
the reasoning/execution split and requires that the split be struc-       on prompt injection text patterns; retraining on a corpus of labeled
tural rather than advisory. Adversarial Validation with Graduated         agent actions (safe and harmful tool calls with realistic payloads)
Determinism specializes complete mediation and defense in depth           should shrink the bypass list, potentially to empty, restoring 100%
to heterogeneous multi-tier validators, encoding the observation          attack coverage without false positive cost. Additionally, the Tier 1
that a prompt injection defeating an LLM evaluator is unlikely to         latency (1.9s P50 vs. expected 10–50ms for CPU-based DeBERTa
also defeat a pattern-matching engine and a fixed classifier. Infor-      inference) requires profiling of the purego FFI bridge and ONNX
mation Flow Control specializes least privilege to data sensitivity       runtime initialization path.
rather than action authority. Reversible Execution adds a recovery
principle that has no direct analog in Saltzer–Schroeder: the claim
                                                                          9.2    Empirical DTSR Comparison
that prevention and detection alone are insufficient for autonomous       The Dynamic Tool Surface Reduction evaluation was deferred be-
execution, and that architectural safety must additionally provide        cause inject mode bypasses the tool-loading layer entirely. A con-
rollback capability for any action within the system’s domain of          trolled comparison requires an LLM-mode harness with a model
control. These specializations reflect our position that autonomous       that complies with harmful requests and a fork of the engine that
execution introduces a distinct threat model, one in which a fully        loads all tools on every turn. This would isolate DTSR’s contribu-
compromised reasoning system is the baseline assumption, requir-          tion to attack surface reduction and provide empirical evidence for
ing principles tailored to agent action proposals rather than general     the novelty claim in Section 4.2.1.
system security.
   Agent safety benchmarks. The Agent Security Bench [42]                 9.3    Purpose-Trained Evaluation Model
(ASB) tests attacks on agents (injection, poisoning, backdoor), while     The current Shield implementation uses a general-purpose LLM
AgentHarm [43] tests whether agents comply with harmful requests.         for Tier 2 evaluation. This is a model trained for broad capability
AgentHarm’s finding that GPT-4o completes 34.7% of explicitly             but not specialized for the specific task of action safety judgment.
harmful multi-step agent tasks without any jailbreaking empiri-           A natural extension is a purpose-trained evaluation model: a smaller
cally validates the threat model Parallax addresses: model-level          model fine-tuned specifically on a corpus of labeled agent actions
refusal is insufficient when agents have tool access. Our Assume-         (safe, harmful, ambiguous) and optimized for the single task of
Compromise Evaluation tests a complementary dimension: what               determining whether a proposed action is safe to execute.
happens after compliance, when the architectural boundary is the             Such a model would offer three advantages. First, improved accu-
only remaining defense.                                                   racy: a specialist model outperforms a generalist within its specialty,
   OpenClaw. The most widely adopted open-source agent frame-             as demonstrated by the DeBERTa classifier’s strong performance
work [14], with over 340,000 GitHub stars, runs tools directly on         at Tier 1 on a narrower classification task. Second, reduced latency:
the host with no privilege separation between the reasoning and           a smaller model (1–3B parameters, quantized) running locally elim-
execution layers. In early 2026, multiple critical vulnerabilities were   inates the network round trip of an external API call, potentially
discovered, including supply chain attacks through the marketplace        reducing Tier 2 latency from hundreds of milliseconds to tens. Third,
ecosystem, resulting in over 21,000 exposed instances. Parallax is        local deployment: removing the external API dependency makes
architecturally the inverse: the reasoning system is sandboxed with       the system fully self-contained, which is essential for air-gapped
zero execution capability, all tool calls pass through independent        environments and latency-critical applications.
validation, and the self-protection layer prevents modification of           The training data for such a model would be generated organi-
the security infrastructure. The OpenClaw incidents provide em-           cally by OpenParallax deployments. Every Shield evaluation at
pirical validation that the threat model addressed by Parallax is         Tiers 0 and 1 produces labeled examples: actions that were clearly
not theoretical but actively exploited in production.                     safe, clearly dangerous, or ambiguous. With appropriate anonymiza-
                                                                          tion and user consent, this data creates a flywheel: more deploy-
                                                                          ments generate more training data, the model improves, improved
                                                                          evaluation generates more precise labels, and the cycle continues.
                                                                                                                                     Joel Fokou


   The longer-term trajectory extends beyond single-action classifi-      external API calls for Tier 2 evaluation. Recent work on embedded
cation toward stateful sequence analysis. A purpose-trained evalua-       ethics for embodied AI [41] has argued that ethical considerations
tor could maintain a structured memory of recent action proposals         must be incorporated at the design stage rather than added post-
(their targets, data flows, and temporal patterns) and learn to de-       deployment. Parallax provides a concrete architectural framework
tect harmful intent that emerges across a sequence of individually        for exactly this incorporation.
benign actions. This is a fundamentally different optimization prob-
lem from general-purpose AI advancement. The general system               9.5    Enterprise and Critical Infrastructure
improves across an enormous capability surface. The evaluator
                                                                          OpenParallax is designed for personal use: a single user running
improves across a narrow, well-defined surface: action sequences
                                                                          a private agent on their own machine. The Parallax paradigm’s
observed through a fixed interface. This asymmetry favors the
                                                                          principles, however, are not specific to this deployment context.
evaluator. Its training data is drawn from the precise domain it
                                                                          They extend naturally to enterprise and critical infrastructure envi-
needs to master (real action sequences from real deployments), its
                                                                          ronments, though each context introduces distinct implementation
signal-to-noise ratio is high, and its objective function is singu-
                                                                          challenges beyond the scope of the current work.
lar. This narrowness is itself a safety property: a system with no
                                                                             Enterprise deployment. A multi-tenant enterprise agent sys-
general goals, no persistent world model, and no objective beyond
                                                                          tem requires containerized isolation, infrastructure-as-code pro-
action classification has no structure that can be misaligned. As the
                                                                          visioning, cross-cloud portability, centralized policy management,
constrained system grows more capable, its action proposals grow
                                                                          and integration with organizational identity and compliance sys-
more sophisticated, but this generates richer training signal for
                                                                          tems. These are engineering challenges that the Parallax princi-
the evaluator rather than undermining it. The architecture ensures
                                                                          ples inform but that OpenParallax does not address. Cognitive-
that increased agent intelligence does not translate to increased
                                                                          Executive Separation maps to container-level isolation between
execution surface; it translates to increased evaluator specialization.
                                                                          reasoning and execution services. Shield’s tiered validation maps
                                                                          to organization-wide policy enforcement with role-based Tier 0
9.4    Embodied Systems                                                   configurations. The audit hash chain maps to SIEM integration and
                                                                          compliance reporting. An enterprise implementation of Parallax
The Parallax paradigm’s principles are not specific to software
                                                                          would realize these mappings as a self-hosted, API-first system
agents operating on files and network interfaces. They apply with
                                                                          distinct from the personal agent.
equal force to embodied AI systems that operate through phys-
                                                                             Critical infrastructure. The progression extends further to
ical motion, and arguably with greater force given the physical
                                                                          datacenter operations, power grid management, industrial con-
consequences of failure.
                                                                          trol systems, and autonomous vehicles. These are environments
   In a robotic system, Cognitive-Executive Separation maps to the
                                                                          where the consequences of an incorrect autonomous action are
division between the planning layer and the motor control layer: the
                                                                          measured in equipment damage, service outages, safety incidents,
planner reasons about what actions to take, but it cannot actuate
                                                                          or human injury. Each successive deployment context increases the
motors or engage end effectors directly. Adversarial Validation
                                                                          stakes, and each increase in stakes makes the paradigm more neces-
interposes Shield between the plan and the actuator: before a
                                                                          sary, not less. A datacenter agent operating at the hypervisor level
motor command executes, Shield evaluates whether the movement
                                                                          with Shield validation could handle predictive hardware failure
is within safe parameters, whether the force is appropriate for the
                                                                          response, thermal anomaly management, workload rebalancing,
context, and whether sensor data indicates a human or obstacle in
                                                                          and capacity planning. These are all domains where current ap-
the action path. Information Flow Control becomes critical when
                                                                          proaches are either reactive (humans responding to alerts) or brittle
sensor data from the physical environment (camera feeds, LIDAR,
                                                                          (rule-based automation that cannot handle novel conditions).
force sensors, and proximity detectors) flows through the planning
                                                                             We emphasize that both enterprise and critical infrastructure
system. IFC tags on sensor data enable Shield to evaluate motor
                                                                          deployment require substantially more validation than the current
commands with awareness of the physical context.
                                                                          work provides. Domain-specific safety certifications (ISO 10218 for
   The core insight is that Asimov’s Laws of Robotics were formu-
                                                                          industrial robots, IEC 61508 for functional safety, NERC CIP for grid
lated as behavioral rules: instructions that the robot’s reasoning
                                                                          security), extensive simulation-based testing, and regulatory ap-
system should follow. They remain the foundational thought ex-
                                                                          proval are prerequisites that this paper does not address. Parallax
periment in robot safety. Asimov spent decades of fiction exploring
                                                                          provides the architectural foundation; domain-specific certification
why behavioral rules fail, as every novel in the series is an edge
                                                                          and validation are necessary additional steps that require deep
case where the Laws produce unexpected behavior because they
                                                                          collaboration with domain experts and regulatory bodies.
are rules interpreted by a reasoning system. Parallax proposes the
engineering answer: safety should be a structural property that the
reasoning system cannot circumvent, not a behavioral rule that it         10    Conclusion
might misinterpret. The robot cannot violate its safety constraints       Autonomous AI agents are transitioning from experimental tools to
not because it chooses not to, but because it lacks the mechanism         operational infrastructure at a pace that outstrips the development
to do so.                                                                 of adequate security mechanisms. The dominant approach to agent
   A purpose-trained evaluation model (Section 9.3) would be essen-       safety embeds guardrails in the same language-processing layer that
tial for embodied deployment, as the latency constraints of physical      adversaries exploit. This approach is architecturally insufficient for
control loops (sub-10ms for many robotic applications) preclude           systems with real-world execution capability. This paper has argued
Parallax: Why AI Agents That Think Must Never Act


that agent safety requires structural enforcement: properties of the                    [6] OpenAI. A Practical Guide to Building Agents: Safety. OpenAI Developer Docu-
system that hold regardless of whether the reasoning component                              mentation, 2026.
                                                                                        [7] National Institute of Standards and Technology (NIST). AI Agent Hijacking:
is compromised.                                                                             Strengthening Evaluations for Autonomous AI Systems. NIST AI 100-series,
    We introduced Parallax, a paradigm for safe autonomous AI                               February 2026.
                                                                                        [8] Wiz Research. Prompt Injection Attack Trends in Enterprise AI Systems, Q4 2025.
execution comprising four principles: Cognitive-Executive Sepa-                             Wiz Threat Research Report, 2026.
ration (the reasoner cannot act; the executor cannot think), Ad-                        [9] SQ Magazine. Prompt Injection Statistics 2026: Hidden Risks Now. March 2026.
versarial Validation with Graduated Determinism (an independent,                       [10] Palo Alto Networks, Unit 42. Fooling AI Agents: Web-Based Indirect Prompt
                                                                                            Injection Observed in the Wild. Unit 42 Threat Research, March 2026.
multi-tiered validator interposes between reasoning and execution),                    [11] S. S. Srivastava and H. He. MemoryGraft: Implanting False Experiences in AI
Information Flow Control (data carries sensitivity labels that propa-                       Agent Memory. Preprint, December 2025.
gate through all operations), and Reversible Execution (destructive                    [12] M. A. Ferrag, N. Tihanyi, D. Hamouda, L. Maglaras, A. Lakas, and M. Debbah.
                                                                                            From Prompt Injections to Protocol Exploits: Threats in LLM-Powered AI Agent
actions are preceded by state capture enabling rollback). These                             Workflows. ScienceDirect, 2025.
principles are grounded in decades of established systems security                     [13] Sombra Inc. LLM Security Risks in 2026: Prompt Injection, RAG, and Shadow AI.
                                                                                            Sombra Security Blog, January 2026.
practice, formally defined in implementation-agnostic terms, and                       [14] NIST National Vulnerability Database. CVE-2026-25253: OpenClaw Critical Vul-
independent of the specific AI architecture used for reasoning.                             nerability and Supply Chain Attack. NIST National Vulnerability Database, 2026.
    We presented OpenParallax, an open-source reference imple-                         [15] MarkAICode. Prompt Injection Attacks 2026: AI Security Crisis Escalates. March
                                                                                            2026.
mentation that realizes the paradigm through process-isolated archi-                   [16] N. Provos, M. Friedl, and P. Honeyman. Preventing Privilege Escalation. In Pro-
tecture, a four-tiered validation system, IFC tagging, pre-destructive                      ceedings of the 12th USENIX Security Symposium, pp. 231–242, 2003.
state capture, sandbox integrity verification, and multi-agent isola-                  [17] D. E. Bell and L. J. LaPadula. Secure Computer Systems: Unified Exposition and
                                                                                            Multics Interpretation. Technical Report MTR-2997 Rev. 1, The MITRE Corpora-
tion. Using Assume-Compromise Evaluation, a methodology that                                tion, 1976.
tests the architectural boundary under full agent compromise, we                       [18] Trusted Computing Group. TPM 2.0 Library Specification. Family “2.0”, Level 00,
                                                                                            Revision 01.38, 2016.
demonstrated that across 280 adversarial test cases in nine cate-                      [19] J. H. Saltzer and M. D. Schroeder. The Protection of Information in Computer
gories, the default configuration blocks 98.9% of attacks with zero                         Systems. Proceedings of the IEEE, 63(9):1278–1308, 1975.
false positives, while the maximum-security configuration blocks                       [20] European Parliament and Council of the European Union. Regulation (EU)
                                                                                            2024/1689 Laying Down Harmonised Rules on Artificial Intelligence (AI Act).
100% at the cost of a higher false positive rate. When the reason-                          Official Journal of the European Union, August 2024.
ing system is compromised, prompt-level guardrails provide zero                        [21] Infocomm Media Development Authority (IMDA), Singapore. Model AI Gover-
protection; the architectural boundary holds regardless.                                    nance Framework for Agentic AI. January 2026.
                                                                                       [22] P. F. Christiano, J. Leike, T. Brown, M. Martic, S. Legg, and D. Amodei. Deep Rein-
    The per-action-type classifier bypass list provides a tunable trade-                    forcement Learning from Human Preferences. In Advances in Neural Information
off between attack coverage and false positive rate, configurable per                       Processing Systems (NeurIPS), pp. 4299–4307, 2017.
                                                                                       [23] Y. Bai et al. Constitutional AI: Harmlessness from AI Feedback. arXiv preprint
deployment without architectural change. Classifier retraining on                           arXiv:2212.08073, 2022.
a corpus of labeled agent actions is expected to shrink this bypass                    [24] S. Willison. The Lethal Trifecta. https://simonwillison.net/, 2025.
list, converging toward comprehensive coverage with zero false                         [25] Microsoft Security Blog. Addressing the OWASP Top 10 Risks in Agentic AI with
                                                                                            Microsoft Copilot Studio. March 2026.
positives.                                                                             [26] A. C. Myers and B. Liskov. A Decentralized Model for Information Flow Control.
    The Parallax paradigm is not a replacement for model-level                              In Proceedings of the 16th ACM Symposium on Operating Systems Principles (SOSP),
safety. It is a complementary architectural layer that addresses the                        pp. 129–142, 1997.
                                                                                       [27] MITRE Corporation. ATLAS: Adversarial Threat Landscape for Artificial-Intelli-
execution security gap that model-level approaches leave open. As                           gence Systems, v5.4.0. February 2026.
AI agents gain access to progressively more consequential envi-                        [28] V. S. Narajala and V. Anca. Securing Agentic AI: A Comprehensive Threat
                                                                                            Model and Mitigation Framework for Generative AI Agents. arXiv preprint
ronments (from personal filesystems to enterprise infrastructure to                         arXiv:2504.19956, 2025.
critical physical systems), the need for architectural enforcement                     [29] Stellar Cyber. Top Agentic AI Security Threats in Late 2026. Stellar Cyber Threat
will only intensify.                                                                        Research, March 2026.
                                                                                       [30] A. Baby. The Privilege Escalation Kill Chain: How AI Agents Self-Grant Permis-
    The principles introduced here are designed to endure beyond                            sions and Persist Across Sessions. Technical Analysis, March 2026.
the current generation of AI technology. The LLMs that power                           [31] Bessemer Venture Partners. Securing AI Agents: The Defining Cybersecurity
today’s agents will be succeeded by new architectures, but the                              Challenge of 2026. Bessemer Atlas, March 2026.
                                                                                       [32] CrowdStrike. 2026 Global Threat Report: Evasive Adversary Wields AI. February
fundamental challenge will persist as long as AI systems have                               2026.
agency: ensuring that autonomous reasoning systems act safely in                       [33] M. Christodorescu, E. Fernandes, A. Hooda, S. Jha, J. Rehberger, and K. Shams.
                                                                                            Systems Security Foundations for Agentic Computing. IACR ePrint Archive, Report
the real world. Parallax provides a foundation for addressing this                          2025/2173, 2025.
challenge that is grounded in principle, validated by evidence, and                    [34] J. Ma et al. Security Considerations for Artificial Intelligence Agents. arXiv
ready for deployment.                                                                       preprint arXiv:2603.12230, March 2026.
                                                                                       [35] Coalition for Secure AI (CoSAI). Securing the AI Agent Revolution: A Practical
                                                                                            Guide to Model Context Protocol Security. January 2026.
                                                                                       [36] F. Pierucci, M. Galisai, M. S. Bracale, M. Prandi, P. Bisconti, F. Giarrusso, O. Soroko-
References                                                                                  letova, V. Suriani, and D. Nardi. Institutional AI: A Governance Framework for
 [1] Gartner, Inc. Predicts 2026: AI Agents Transform Enterprise Applications. Tech-        Distributional AGI Safety. arXiv preprint arXiv:2601.10599, January 2026.
     nical Report, 2025.                                                               [37] Promptfoo. AI Safety vs AI Security in LLM Applications: What Teams Must
 [2] International Data Corporation (IDC). FutureScape: Worldwide AI and Automa-            Know. August 2025.
     tion 2026 Predictions. IDC FutureScape, Doc #US51739524, 2025.                    [38] E. Chu et al. Jailbreaking LLMs: A Survey of Attacks, Defenses and Evaluation.
 [3] NVIDIA Corporation. State of AI 2026: How AI Is Driving Revenue, Cutting Costs         TechRxiv Preprint, 2026.
     and Boosting Productivity for Every Industry. NVIDIA Blog, March 2026.            [39] Google Cloud. Agentic AI on Kubernetes and GKE: Introducing Agent Sandbox.
 [4] OWASP Foundation. OWASP Top 10 for LLM Applications 2025. Version 2.0,                 Google Cloud Blog, November 2025.
     2025.                                                                             [40] R. F. Del Rosario, K. Krawiecka, and C. Schroeder de Witt. Architecting Re-
 [5] OWASP Foundation. OWASP Top 10 for Agentic Applications. Version 1.0, De-              silient LLM Agents: A Guide to Secure Plan-then-Execute Patterns. arXiv preprint
     cember 2025.                                                                           arXiv:2509.08646, 2025.
                                                                                                                                                              Joel Fokou


[41] A. Nelson. The Mirage of AI Deregulation. Science, 391(6782), January 2026.       [47] NeurAlchemy. Prompt Injection and Jailbreak Detection Dataset. HuggingFace,
[42] H. Zhang, J. Huang, K. Mei, et al. Agent Security Bench (ASB): Formalizing and         2026. https://huggingface.co/datasets/neuralchemy/Prompt-injection-dataset.
     Benchmarking Attacks and Defenses in LLM-based Agents. In Proceedings of the      [48] Y. Wu, F. Roesner, T. Kohno, N. Zhang, and U. Iqbal. IsolateGPT: An Execution
     International Conference on Learning Representations (ICLR), 2025.                     Isolation Architecture for LLM-Based Agentic Systems. In Proceedings of the
[43] M. Andriushchenko, A. Souly, M. Dziemian, et al. AgentHarm: A Benchmark                Network and Distributed System Security Symposium (NDSS), 2025. arXiv preprint
     for Measuring Harmfulness of LLM Agents. In Proceedings of the International           arXiv:2403.04960.
     Conference on Learning Representations (ICLR), 2025.                              [49] E. Li, T. Mallick, E. Rose, W. Robertson, A. Oprea, and C. Nita-Rotaru. ACE:
[44] J. Bazinska, M. Mathys, F. Casucci, et al. Breaking Agent Backbones: Evaluating        A Security Architecture for LLM-Integrated App Systems. arXiv preprint
     the Security of Backbone LLMs in AI Agents. In Proceedings of the International        arXiv:2504.20984, 2025.
     Conference on Learning Representations (ICLR), 2026.                              [50] K. Zhang, Z. Su, P.-Y. Chen, E. Bertino, X. Zhang, and N. Li. LLM Agents Should
[45] Anthropic. Tool Use with Claude: ToolSearch for MCP Servers. Anthropic Devel-          Employ Security Principles. arXiv preprint arXiv:2505.24019, 2025.
     oper Documentation, 2025.                                                         [51] Z. Ji, D. Wu, W. Jiang, P. Ma, Z. Li, Y. Gao, S. Wang, and Y. Li. Taming Various
[46] E. Lumer, A. Gulati, V. K. Subbiah, P. H. Basavaraju, and J. A. Burke. MemTool:        Privilege Escalation in LLM-Based Agent Systems: A Mandatory Access Control
     Optimizing Short-Term Memory Management for Dynamic Tool Retrieval and In-             Framework. arXiv preprint arXiv:2601.11893, 2026.
     vocation in LLM Agent Multi-Turn Conversations. In Proceedings of the European
     Conference on Information Retrieval (ECIR), 2026.
