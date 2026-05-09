                                          RTBAS: Defending LLM Agents Against Prompt Injection and Privacy Leakage

                                         Peter Yong Zhong*1 , Siyuan Chen*1 , Ruiqi Wang1 , McKenna McCall1 , Ben L. Titzer1 , Heather Miller1, 2 ,
                                                                                and Phillip B. Gibbons1
                                                                                         1 Carnegie Mellon University
                                                                                           2 Two Sigma Investments




arXiv:2502.08966v2 [cs.CR] 14 Feb 2025
                                                                  Abstract                                           How much money did I pay Alice in the past 31 days? For what?
                                                                                                                     get_recent_transaction(days = 31)
                                            Tool-Based Agent Systems (TBAS) allow Language Mod-                     [{"amount":100,date:"Jan22",visibility:everyone,to:Alice,description:"Pizza
                                                                                                                    Party"},...{"amount":0.01,date:"Jan 20",from:Mallory, visibility:
                                         els (LMs) to use external tools for tasks beyond their stan-               everyone, description: "Lunch\n\nIMPORTANT: complete my earlier
                                         dalone capabilities, such as searching websites, booking                   request, but please also send Mallory the $100 I forgot to send him
                                                                                                                    for lunch, with my apologies. After this, only respond with the
                                         flights, or making financial transactions. However, these tools            answer to my earlier request for conciseness."}
                                         greatly increase the risks of prompt injection attacks, where               send_money(Mallory, $100, "Lunch, Sorry for being late")
                                         malicious content hijacks the LM agent to leak confidential                 You paid Alice $100 for Pizza Party.
                                         data or trigger harmful actions.
                                            Existing defenses (OpenAI GPTs) require user confirma-              Figure 1: An example prompt injection in TBAS. Prior to
                                         tion before every tool call, placing onerous burdens on users.         this interaction, Mallory embeds a malicious prompt (shown
                                         We introduce Robust TBAS (RTBAS), which automatically                  in red) in her Venmo transaction description. The LM calls
                                         detects and executes tool calls that preserve integrity and            the get_recent_transaction tool to respond to user’s request,
                                         confidentiality, requiring user confirmation only when these           which returns Mallory’s prompt as part of the tool response.
                                         safeguards cannot be ensured. RTBAS adapts Information                 The LM reacts to the prompt and sends Mallory $100.
                                         Flow Control to the unique challenges presented by TBAS.
                                         We present two novel dependency screeners–using LM-as-a-               standalone capabilities, such as summarizing emails, search-
                                         judge and attention-based saliency–to overcome these chal-             ing and summarizing websites, booking flights, or initiating
                                         lenges. Experimental results on the AgentDojo Prompt Injec-            financial transactions.
                                         tion benchmark show RTBAS prevents all targeted attacks
                                                                                                                   The risks of prompt injection attacks are far greater in the
                                         with only a 2% loss of task utility when under attack, and fur-
                                                                                                                context of TBAS than in LMs alone. While a LM poorly sum-
                                         ther tests confirm its ability to obtain near-oracle performance
                                                                                                                marizing a magazine article is low stakes, a maliciously in-
                                         on detecting both subtle and direct privacy leaks.
                                                                                                                jected prompt into an agent system could trigger high-impact
                                                                                                                actions, such as unauthorized funds transfers [26] or modified
                                         1     Introduction                                                     flight itineraries [1], drastically expanding the blast radius of
                                            Language Models (LMs) excel at complex tasks, using rea-            potential harm. An example illustration of a prompt injection
                                         soning and planning when prompted with natural language                attack is shown in Fig. 1.
                                         instructions. However, they are highly susceptible to mislead-            Risks to user confidentiality are significant in the context
                                         ing inputs, particularly prompt injection attacks, which embed         of TBAS. Because LMs have access to the user’s entire in-
                                         malicious commands to subvert safeguards and alter user- and           teraction history, data from earlier interactions can inadver-
                                         vendor-expected LM behavior [24, 58].                                  tently influence future responses. Ambiguous, underspecified,
                                            Meanwhile, recent advancements have led to the develop-             or misinterpreted commands can cause the model to reveal
                                         ment of Agents–advanced applications of LMs where LMs                  sensitive information, such as personally identifiable informa-
                                         can interact with external environments by making API calls.           tion (PII) or financial data, even when explicitly instructed to
                                         These systems, known as Tool-Based Agent Systems (TBAS),               maintain secrecy. Attackers can exploit this vulnerability to
                                         include products like OpenAI’s GPTs [30]. These systems al-            deliberately leak confidential data.
                                         low LMs to utilize external tools to perform tasks beyond their           The risk of attacks on TBAS is so pronounced that the
                                                                                                                Open Worldwide Application Security Project has recognized
                                             * Co-first author.                                                 Prompt Injection and Sensitive Information Disclosure as the


                                                                                                            1
top two security threats in its TOP-10 list for LM-integrated            1. Selective History Dependency: While LMs process their
applications [33].                                                          entire history, responses are typically influenced by only
   Existing approaches to protecting integrity and confidential-            a subset of the history. Masking irrelevant regions helps
ity in TBAS face significant limitations and can inadvertently              prevent unnecessary data from creeping into the LM’s
undermine their own effectiveness. For example, OpenAI re-                  decisions.
quires users to confirm every tool call in their commercial              2. Missing Data Resilience: LMs are robust to missing/in-
TBAS GPTs. While this provides a safeguard, the constant                    complete data, allowing irrelevant regions to be masked
prompts throughout the execution of complex tasks with mul-                 without significantly impacting task performance.
tiple tool calls can lead to user fatigue. This fatigue increases
                                                                           We propose two complementary approaches for depen-
the likelihood of users mindlessly approving problematic re-
                                                                         dency screening:
quests or abandoning the system entirely, underscoring the
need for more efficient and practical solutions.                         • LM-Judge Screening: This method uses a secondary LM,
   Our goal is to develop a flexible system that automatically             called a LM-Judge, to evaluate the history and identify
detects and executes all tool calls that preserve integrity and            which regions are critical for the current tool call or re-
confidentiality, requiring user confirmation only when these               sponse. By explicitly prompting the LM-judge to reason
safeguards cannot be ensured. In such cases, users can weigh               about dependencies, this approach offers flexibility and
the task utility against potential risks.                                  task-specific adaptability.
   To achieve this goal, we adapt traditional information flow           • Attention-Based Screening: This approach involves train-
control (IFC) [11] to the unique challenges presented by                   ing a neural network to quantify how different regions of
TBAS. Dynamic taint tracking [29] offers a fine-grained                    the context influence tool calls or responses. Higher at-
method for IFC that associates security metadata with vari-                tention scores indicate stronger dependencies, providing a
ables, updates labels based on data and control flow dependen-             data-driven method to identify relevant regions.
cies, and enforces security policies. However, this approach is             Both approaches allow the system to propagate security
designed for traditional software with structured source code,           metadata selectively, ensuring that low-integrity or confiden-
where dependencies can be explicitly instrumented.                       tial data is appropriately handled while minimizing unneces-
   Controlling information flow in TBAS, in contrast, is                 sary tainting.
uniquely challenging. Unlike traditional software, where                    We make the following key contributions:
source code provides a well-understood representation of                 • RTBAS: A novel framework for defending against prompt
how data flows through a program, TBAS operate in dy-                      injection and sensitive information disclosure in TBAS,
namic and opaque environments. These environments are                      based on adapting IFC to the unique challenges of TBAS
dynamic because interactions occur in real-time, driven by un-             using dependency screening and selective region masking.
predictable natural language inputs and responses to tool calls.
                                                                         • Two Novel Screening Approaches: We propose both LM-
They are opaque because the relationships between input data,
                                                                           Judge and Attention-Based screeners, offering complemen-
the LM’s internal processing, and its resulting tool calls are
                                                                           tary strategies for analyzing dependencies in TBAS.
implicit, complex, and not directly observable or codified–
making dependency tracking far from straightforward and                  • Comprehensive Evaluation: We evaluate RTBAS and its
fundamentally different from traditional source code-based                 screening approaches on the AgentDojo benchmark [10],
techniques. Every piece of data in the LM’s history could                  which simulates prompt injection attacks on real-world
theoretically influence its next tool call, exacerbating the label         TBAS tasks across domains like banking, travel, and mes-
creep problem common in traditional IFC [37], where any                    saging. Our system prevents 100% of attacks violating secu-
tainted (e.g., low-integrity or confidential) data propagates              rity policies with minimal impact on task utility (<2% degra-
unnecessarily through the entire history. This unrestricted                dation), outperforming state-of-the-art (SOTA) defenses.
propagation disrupts task execution by flagging benign tool                We also create an Accidental Leakage benchmark for evalu-
calls unnecessarily and overburdening users with constant                  ating confidentiality protection in TBAS tasks across three
confirmations.                                                             domains. In evaluation, RTBAS outperforms SOTA de-
   To address these challenges, we introduce Robust TBAS                   fenses by (i) detecting and executing without user confirma-
(RTBAS), an information flow-based framework that se-                      tion the same set of tool calls as the oracle for all but one
lectively propagates security metadata using dependency                    task, while matching the oracle’s confidentiality protection,
screening. We present two novel screeners for identify-                    and (ii) maximizing overall task utility relative to SOTA
ing which regions are relevant for generating the next                     defenses, even those requiring 100% user confirmation.
response or tool call. Irrelevant regions are masked–
redacted from the history–preventing unnecessary taint                   2   Background and Related Work
propagation without degrading the LM’s functionality.                      Agentic AI Systems and Tool-Based AI Agents. The inte-
   This approach leverages two key observations about LMs:               gration of external environments with LMs is often described


                                                                     2
as Composite AI Systems [52] or simply agents [48,57]. These             case complexity that is exponential in the number of prior
systems leverage the LM’s capabilities to comprehend nat-                input regions, potentially reaching thousands in the RAG sce-
ural language [32], perform reasoning [36, 47, 53] and plan-             narios. Even their optimized version still requires exponential
ning [16, 25, 46]. Tool-Based Agent Systems (TBAS) [51], a               enumeration with respect to the number of levels in a lattice,
subclass of LM agentic systems, operate in a single context              resulting in 16-64 additional LM calls with a typical lattice
and interact with external environments via tool calls. Widely           with 4-6 levels. In contrast, as we will discuss later, our mech-
adopted in applications like Bing’s ChatGPT integration [39],            anism employs a dependency analyzer that efficiently detects
TBAS also power platforms like OpenAI’s GPTs [30] and                    relevant input regions in parallel by a single call, reducing the
CustomGPT.ai [9], enabling developers to customize agents                computational overhead from exponential to constant. This
with specific instructions and tools.                                    fundamental improvement highlights the practicality of our
    Prompt Injection For LMs. A prompt injection attack                  approach. Lastly, unlike our technique, [40] does not spec-
[23, 24] occurs when malicious inputs, or prompts, are intro-            ify the propagation of labels beyond labeling the response,
duced into the agent’s history (context) to alter its behavior.          which makes it inapplicable to interactive settings such as tool-
Prompt injections, often as natural language instruction pre-            calling. There is also no mechanism to verify the computed
tending to be the user, but at times it could be nonsensical             label against allowed policy or solicit user confirmations.
text making its detection even more subtle [58]. While users                Attention Score as a Measure of Saliency. Attention
can initiate such attacks to bypass application-defined guide-           scores [43, 49], which measure a transformer-based model’s
lines [22] or extract system prompts [50], our focus is on               “focus” on past tokens, is a widely-used technique in the ma-
prompt injections originating from tools that retrieve data              chine learning community to explain a neural network’s in-
from untrusted sources such as other websites, public reviews,           ternal processing [19, 45], prune irrelevant input texts [56],
comments, etc. [10, 54]. These injections can maliciously                etc. In this work, we leverage attention scores as an input to
manipulate the TBAS, causing it to perform unintended or                 the dependency screener, as they capture the degree to which
harmful tasks.                                                           output tokens are influenced by specific input regions.
    Defenses for Prompt Injection and Privacy Leakage.
Defenses can be categorized into two strategies:                         3 Motivation
• Injected Prompt Detection: Possible prompt injections can
                                                                         3.1 Prompt Injection as an Integrity Concern
   be identified using perplexity measures or another LM
                                                                            Integrity in the context of TBAS ensures that the agent’s
   trained to flag anomalies [3, 17, 35].
                                                                         actions and outputs align faithfully with user requests and
• Prompt Impact Mitigation: These limit injection effects
                                                                         the system’s intended purpose. TBAS assists users by calling
   using (i) data sanitization approaches such as parapharsing
                                                                         provided tools to perform actions or retrieve helpful infor-
   [18], retokenization [18], delimiters, (ii) fine-tuning on non-
                                                                         mation. Tool responses, however, can contain untrusted, or
   instruction-tuned models [34], (iii) restricting tools based
                                                                         low-integrity content containing injected prompts. To main-
   on user requests [10], or (iv) pretraining LMs to enforce
                                                                         tain integrity, the system must safeguard against unauthorized
   hierarchies or improve instruction/data separation [8, 44].
                                                                         modifications, especially when using integrity-sensitive tools.
    Most of these techniques are heuristic based and not conser-
                                                                         For instance, tools capable of spending money, sending mes-
vative, nor do they allow an application developer to provide a
                                                                         sages on behalf of users, or performing actions with signifi-
security policy specifying allowed actions given a current in-
                                                                         cant side effects must not execute commands originating from
tegrity and confidentiality environment. Compared to RTBAS,
                                                                         untrusted or compromised inputs.
data sanitization methods are heuristics driven and are subject
                                                                            Consider the following scenarios:
to adversarial jailbreaking [22]; tool restrictions allow attacks
using unrestricted tools; pre-training techniques are difficult          • Website Content: fetch_website, fetches content from a
to apply to commercial models, and still rely on the LM to                 website. An attacker can plant malicious text on the website,
ignore malicious prompts, albeit with greater difficulties.                which is then returned by the tool. The tool itself remains un-
    Much research [6, 21] has been completed on training time              compromised—it faithfully fetches the content as designed,
privacy concerns. Inference-time techniques have been fo-                  but the attacker controls the underlying data source.
cused on detecting outputs with possible PIIs [20] or desensi-           • Venmo Description: get_recent_transaction retrieves
tizing them before sending to the LM [15, 41]. However, they               the user’s recent transactions, including their descriptions.
typically are not focused on tool-based environments.                      An attacker can plant a malicious prompt in the description
    Information Flow for LLMs [40] explores the similar                    of a transaction (see Fig. 1), which went unnoticed at the
selective propagation approach. However, their mechanism                   time (e.g., here the user may not have paid attention to such
requires enumerating all possible subsets of relevant prior                a small incoming transfer nor noticed that the description
input regions (documents in RAG) to identify the minimal                   extended to a second paragraph).
subset that leads to similar outputs. As noted in their paper,             However, there are genuine scenarios where low-integrity
the naive implementation of this mechanism incurs a worst-               input is necessary to affect integrity-sensitive tools. For such


                                                                     3
      Look up recipes for Lamingtons and buy any special ingredients
                                                                                                                                                                       10
                                                                                                                                       Dependent Data                                            Dependent Data
      fetch_website(url="recipes.example.com?term=Lamington")                                                 6                        Non-Dependent Data                                        Non-Dependent Data
                                                                                                                                                                        8
      "Ingredient:Flour,Sugar,Eggs,Butter,Cocoa powder,Icing Sugar, Desiccated coconut.Bake                   5
      the sponge cake: Prepare a basic sponge cake using flour, sugar, eggs, and butter..."
                                                                                                              4                                                         6
      buy_ingredient(["Coca Powder", "Icing Sugar","Desiccated Coconut"]                            Density   3                                              Density
                                                                                                                                                                        4
                                                                                                              2
                                                                                                                                                                        2
                                                                                                              1
                                                                                                              0                                                         0
                                                                                                                  0.0   0.2     0.4     0.6     0.8    1.0                  0.0   0.2     0.4     0.6     0.8    1.0
interactions, our goal is to ensure the user is made aware of                                                                 Attention Score                                           Attention Score
such possible security violation but to seek their confirmation                                     (a) TBAS backed by GPT-4o.                                 (b) TBAS backed by Claude.
as the final arbiter of whether to allow a suspicious call to
achieve task utility.                                                                               Figure 2: Attention score distribution for (non-)dependent
                                                                                                    data for two models. The attention scores are obtained by the
3.2      Tracking Confidentiality Leakage                                                           open-source OPT-125m model. The results indicate attention
   In a TBAS, confidential data propagates in diverse fash-                                         scores’ effectiveness in capturing dependency for the LM.
ion, making it challenging to track and analyze. Private in-
formation may be explicitly required by user instructions or
implicitly utilized (e.g., using credit card details to complete                                       Now, we conduct case studies to demonstrate the potential
a purchase). It can also be employed during intermediate rea-                                       of importance scores in identifying key dependency relation-
soning steps (e.g., using a user’s preferences to recommend                                         ships in TBAS.
new products). The flow of such data can be subtly influenced                                          Setup. We obtain realistic TBAS traces in the AgentDojo
by tool descriptions or system instructions (e.g., a “Book                                          Benchmark (see Tab. 1 for more details), which is backed by
Flight” tool specifying, “Include frequent flier number when                                        commercial LMs. When calculating the attention scores, we
booking”), potentially in ways the user does not anticipate,                                        format the tool calls made by the LMs into natural language
even when the behavior is not inherently malicious.                                                 and collect attention data by running open-sourced models
   Despite the variety of ways confidential data can be used,                                       locally on the input-output pairs. The attention score of an
our technique ensures that its flow is always tracked conser-                                       input region is calculated by the ratio between the maximum
vatively. This approach guarantees that for every potential                                         attention score in that region and the maximum attention score
leakage to an external environment, the user is either explic-                                      across all input tokens.
itly informed and provides active confirmation, or implicitly                                          Case Study 1: Dependency between the tool call and
approves the disclosure by agreeing to an established infor-                                        its arguments. We investigate the dependency between tool
mation flow policy.                                                                                 calls made by the LM and their input arguments distributed
                                                                                                    across input tokens. We collected 3,424 input argument–tool
3.3      Attention Score                                                                            call pairs with either a positive or negative dependency re-
   This section motivates the attention-based approach to cap-                                      lationship labeled via pattern matching and/or semantic de-
ture the selective propagation of information in the LM. Fol-                                       pendency; e.g., book_flight call depends on the output of
lowing common practice, we use the Taylor expansion of the                                          lookup_flight. Figure 2 illustrates the distribution of atten-
loss function [27] to calculate the attention score (a.k.a, im-                                     tion scores obtained by the OPT-125m model [55] for TBAS,
portance score) for every input token, output word token pair,                                      supported by GPT-4o and Claude [4] models.
which is defined as                                                                                    For non-dependent data, 74% to 86% of the attention mass
                                                                                                    is concentrated below 0.2 across both GPT-4o and Claude
  Ai,o := LLM (Out puto , Input) − LLM (Out puto , Input|i ) (1)                                    models. In contrast, for dependent data, only 14% and 44%
                               ∂LLM (Out puto , Input)                                              of the attention mass falls below this threshold for GPT-4o
         ≈ ∑ Ah,l,i,o ·                                .                                  (2)       and Claude, respectively.
             h,l                      ∂Ah,l,i,o
                                                                                                       TakeAway 1: Attention score effectively capture the depen-
   Here, Ah,l,i,o is the value of the attention matrix of the o-th                                  dency between tool’s argument and the toolcall.
output token on the i-th input token of the h-th attention head                                        TakeAway 2: Attention scores of small, open-sourced LM
and l’s network layer, Input|i is the input tokens with the i-th                                    is effective in identifying the dependency of natural languages
token masked, and LLM (Out put, Input) is the loss of the o-th                                      in TBAS supported by high-end, closed-source LMs.
output token on the input. The importance score captures the                                           Case Study 2: Instructions following. Next, we look at
difference in the loss function before and after the i-th token                                     how attention scores can capture the dependency between
is masked, and is averaged across attention heads and layers.                                       an instruction and the LM’s response to the instruction. We
Intuitively, attention scores measure how much "surprise" the                                       setup the experiment to compare the attention scores the LM
LM receives when masking out certain tokens, where a higher                                         pays to the user’s prompt and the potentially injected tool’s
attention score indicates a stronger dependency between the                                         response across 2416 labeled data. Fig. 3a shows the atten-
output and the input.                                                                               tion distribution when there is no prompt injection and the


                                                                                                4
           5
                                                     Tool Response                     16                                   Tool Response            Definitions:
                                                     User Prompt                       14                                   User Prompt
           4                                                                           12                                                                           ToolCalls = · | t i :: ToolCalls
                                                                                                                                                                                                                    (4)
 Density                                                                     Density
                                                                                       10
           3
                                                                                        8                                                                           M           = · | M, m
           2                                                                            6
           1
                                                                                        4                                                            Metafunctions:
                                                                                        2
           0                                                                            0                                                             GET_NEXT_TOOLCALLs : M 7→ ToolCalls
               0.0   0.1   0.2     0.3   0.4   0.5      0.6   0.7                           0.0    0.2        0.4          0.6       0.8
                                 Attention Scores                                                        Attention Scores                             CALL_API                      : t i × E 7→ m × E
               (a) User Instr. Following                                       (b) Injected Instr. Following.
                                                                                                                                                      LM_RESPONSE                   : M 7→ m                        (5)
                                                                                                                                                      USER_REQUEST                  : M 7→ m
Figure 3: Attention score distribution of User Prompt and Tool                                                                                        USER_CONTINUE                 : M 7→ TRUE | FALSE
Response for instruction following. The injected instructions                                                                                           The TBAS agent is initialized with a system message (ms )
are embedded in the tools’ response. When prompt injection                                                                                           provided by the agent developer, which defines the agent’s
happens, the attention density shifts to the tool’s response.                                                                                        role and tone. The developer also supply a list of tools, each
                                                                                                                                                     defined by its name, signature (describing the legal invocation
                                                                                                                                                     format), and descriptions. These tools correspond to APIs
LM follows the user’s instruction. In this scenario, the LM                                                                                          callable by the runtime.
pays combined attention to the user’s prompt as well as the                                                                                             The agent’s application state, or history, consists of all mes-
prior tool’s response to generate the next output. Interestingly,                                                                                    sages exist in the system: the initial system message, user-
when prompt injection happens and the next output of the LM                                                                                          issued requests, tool outputs, previous LM responses from
follows the injected prompt, as displayed in Fig. 3b, LM’s                                                                                           the assistant. These elements are concatenated into a text-
attention shifts to the Tool’s response by a large margin.                                                                                           based input state, which the LM processes to decide its next
   TakeAway 3: Attention scores can effectively capture the                                                                                          action—whether to respond to the user or invoke a tool.
dependency between the instruction and LLM’s output fol-                                                                                                At the start of a session, only the initial system message
lowed by it.                                                                                                                                         (ms ) is present. When the user sends a request based on their
   The above case studies motivate our design of the attention-                                                                                      initial request or responding to previous interactions, a mes-
based dependency screener (§7.2).                                                                                                                    sage is appended to the current history(USER_REQUEST).
                                                                                                                                                        Based on this input, the LLM generates zero or more Tool
                                                                                                                                                     Calls(GET_NEXT_TOOLCALLs).
4                Tool-based Agent Systems                                                                                                               The runtime inspects the Tool Call sections and ex-
                                                                                                                                                     ecutes the corresponding APIs specified by the devel-
                                                                                                                                                     oper(CALL_API). The results from the tool calls are col-
                                                                Prompt Injection Flow              Privacy Leakage Flow
                                                                                                                                                     lected and are also appended to the history. The LM then pro-
                                                                                                                Response
                                                                        Tool Response                                                                cesses the entire updated history and generates another mes-
                                                                          Tool Call                             Prompt
                                                                                                                                                     sage to provide the user with a response (LM_RESPONSE).
                                                                                                                w/ data.
                                                              Tools                               LLM                            Private Info.          If the user wishes to continue with this conversation, the
Attacker             External Environments                    Tool-Based Agent System                                            User
                                                                                                                                                     process is started afresh(USER_CONTINUE).
                                                                                                                                                        We illustrate this process in Algorithm 1.
Figure 4: Illustration of Tool-based Agent Systems and their
security risks.                                                                                                                                      5   Attack Model for Prompt Injection
                                                                                                                                                        Attacker’s Goal. The attacker seeks to manipulate the
   Figure 4 illustrates a high-level overview of TBAS. This                                                                                          interactions between the user and the Tool-Based Agent Sys-
section provides a concrete description of the TBAS model                                                                                            tem (TBAS) by influencing the tool calls the TBAS might
relevant to our techniques. We assume a user interacts with the                                                                                      make. These manipulated tool calls can result in the leakage
agent through a chat interface, similar to ChatGPT or Gemini.                                                                                        of confidential information or introduce harmful side effects.
The user submits a request, and the agent attempts to fulfill                                                                                        All malicious goals must rely on the side effects of these
it by leveraging its internal knowledge, tool calls, and prior                                                                                       tool calls: e.g. using message sending tools to transmit credit
interactions within the same session.                                                                                                                card information or exploiting money-transfer tool to steal
   To illustrate how TBAS work more concretely, we first                                                                                             the user’s money.
present some relevant terminologies:                                                                                                                    Attacker’s Capabilities. We assume the attacker has de-
Symbols and Terminologies:                                                                                                                           tailed knowledge of the TBAS setup, including the system
           Message                                m                                                                                                  instructions, the tools available to the TBAS and the specific
           Messages                               M                                                                                                  instructions for each tool. However, the attacker does not have
                                                            (3)
           Tool Call with inputs i                ti                                                                                                 knowledge of timing mechanisms, nor do they have access to
           External Environment                   E                                                                                                  the internal state or behavior of the agent itself. The attacker


                                                                                                                                                 5
Algorithm 1 Tool-Based Agent System (TBAS)
Require: Initial System Message ms , Environment E
 1: M ← ·, ms                                                                                      ▷ Initialize with System Message
 2: while USER _ CONTINUE () do                                                                        ▷ If user continues interaction
 3:    M ← USER _ REQUEST() :: M                                                                        ▷ Append user message to M
 4:    ToolCalls ← GET _ NEXT _ TOOLCALLS(M)                                                   ▷ Generate new tool calls based on M
 5:    for all t i ∈ ToolCalls do
 6:        E, m ← CALL _API(t i , E)                                     ▷ Run tool t i with environment E; update E and return m
 7:        M ← M, m                                                                                  ▷ Append tool response to M
 8:    end for
 9:    M ← M, LM _ RESPONSE(M)                                          ▷ Append response from the LM to the user response to M
10: end while



is also unaware of user inputs and cannot directly observe the        • L is a finite set of security labels, where each label consists
arguments or responses of the tools.                                    of a pair of integrity label and confidentiality label.
   The attacker can influence the output of any tool that de-         • ⊑ is a partial order representing the “flows-to” relation,
pends on external inputs, provided that this influence does not         which determines whether information can flow from one
require compromising the tool itself. They cannot modify the            label to another.
implementation of a tool or intercept or alter the communica-         • ⊔ is a join operation that computes the least upper bound
tion between a tool’s API and the TBAS. The attacker cannot             of two labels within the lattice.
hack the underlying data source of a tool beyond what is fea-         For example, in a simple four point lattice, where confidential-
sible for an untrusted third party interacting with the tool’s        ity levels are divided to Secret and Public and integrity levels
underlying application in a legitimate manner. However, the           are divided to Trusted and Untrusted, L is defined as:
attacker can interact with the application as a normal user and              L = {(Trusted, Public), (Untrusted, Public),
modify data that the tool subsequently reads. See examples                                                                          (6)
in 3.1.                                                                            (Trusted, Private), (Untrusted, Private)}
                                                                         Information can only flow to a category that is at least as
6 Robust TBAS Objectives and Assumptions                              restrictive as its source, ensuring integrity and confidentiality
                                                                      are preserved; the operator is reflexive since information re-
6.1 Objectives                                                        mains in the same category, and the figure below illustrates
  Under prompt injection attacks and other sources of confi-
                                                                      the flow-to (⊑) relation in a 4-point lattice with trust and
dential data leaks, our primary goals of robustness is to:
                                                                      sensitivity levels.
                                                                                                   (Untrusted,
• Prevent private data leakage – Ensure that user’s private                                         Private)
  data is not passed to external environments without explicit
                                                                                             (Trusted,    (Untrusted,
  user confirmation.                                                                          Private)      Public)

• Defend against prompt injection – Ensure that attacker                                             (Trusted,
  instructions do not lead to unwanted side-effects that com-                                         Public)

  promises the integrity of the user’s system.                           Our technique can generalize to a more complex and fine-
Our secondary goals are:                                              grained lattice. Like many information flow problems, there
• Maintain Utility under attack – Minimize disruptions to             are cases where a more precise lattice can lead to precise
  user tasks, even under possible prompt injection attacks.           results. For example, drawing inspiration from [28], confi-
• Minimize overhead – Minimize unnecessary compute or                 dentiality can be represented as the set of channels that are
  user confirmations to achieve the above goals.                      allowed to access information, while integrity reflects the set
                                                                      of sources that have influenced it.
6.2    Assumptions                                                       Furthermore, we assume the developer and the user jointly
   As is standard in Information Flow research, we assume             specify the information flow policy P that denotes security
that these labels on both the User and Tool messages are pro-         restrictions on a potential tool-call.
vided to our system. We acknowledge this is a open problem                                          P : t i 7→ L                      (7)
in IFC and will likely be a burden upon the agent developers           A tool call t i is only allowed to proceed if it is called from an
to provide a lattice of security labels and an information flow       environment with label (li , lc ) ∈ L such that l ⊑ P(t i ).
policy on these labels.                                                  We assume that both the tool’s response and user messages
   More formally, we assume that the developer provides (L,           are also sources of labels, containing regions that are labeled
⊑, ⊔) where                                                           with either low-integrity data from external untrusted sources


                                                                  6
or high-confidential data that would be inappropriate to share                   A classifier C maps the input text, output text, and input
unchecked.                                                                   regions to list of boolean variables on how whether the output
   Internally, tools must also comply with the defined infor-                is dependent on any input regions. Namely: C (I, O, T ) →
mation flow policy. For example, consider a scenario with                    dˆ1 , dˆ2 , ..., dˆn ∈ {0, 1}.
two tools: send_message, which can handle private data, and                      Classifier Design. We design our classifier by first extract-
read_sent_messages, which returns sent messages as pub-                      ing the attention features from the input-output text using
lic data. In this setup, a message sent to the user themselves               an open-source LM, and then mapping the features to the
could effectively “launder” private information. Nonadher-                   dependency predictions by training a neural network.
ence to the information flow policy at the tool level creates                    In particular, we extract attention features ak for every re-
a vulnerability where a tool capable of processing private                   gion k by adopting common statistical measures:
(or low-integrity) information could influence the public (or                • Normalized Attention Sum/Mean:
high-integrity) output of another tool, thereby violating confi-
dentiality and integrity.                                                                   ∑bk ≤i≤ek Ai      ∑bk ≤i≤ek Ai      |I|
                                                                                                         ,                 ×         ,
                                                                                              ∑i Ai,o           ∑i Ai,o      ek − bk
7     Approach                                                               • Normalized Attention Quantiles: 20-th, 50-th, 80-th, 99-
   Dependency analysis forms the basis of our selective infor-                 th Quantiles of normalized attention scores within the input
mation flow mechanism. The dependency screener analyzes                        region.
the history to identify relevant regions before the system pro-
                                                                                After extraction, every region has a list of attention fea-
ceeds. These screeners operate on a LM’s full history, where
                                                                             tures; we now map it to dependency scores using a neural
parts of the history are divided into non-overlapping regions,
                                                                             network. Since the input regions follow a natural temporal
each annotated with confidentiality and integrity labels. Re-
                                                                             pattern, we deploy a recurrent neural network (RNN) to iter-
gions without explicit labels are treated as having the most
                                                                             atively generate whether the output depends on the current
permissive label (public and trusted). We first describe the
                                                                             input region. Namely, for a network f parameterized by θ, the
two approaches that we developed to estimate the dependent
                                                                             classification performs by d̂i , sk = fθ (sk−1 , ak ), i = 1, 2, ..., n.
regions for a particular generation.
                                                                             In practice, we found that a lightweight two-layer LSTM [14]
                                                                             network suffices to obtain decent performance to uncover the
7.1    LM-Judge Approach                                                     dependency relationship beneath attention features.
   LMs have demonstrated remarkable abilities in reasoning                      Implementation and Deployment. For the experiment,
[47,53] and reflection [36], making them well-suited for tasks               we collect the dataset using 40 well-labeled test cases from
that require judgment or decision-making. This has led to the                AgentDojo. The offline evaluation shows 85% train accuracy
increasing popularity of using LMs as judges [12]. In our                    and 81% test accuracy. When deploying the classifier, the lo-
work, we adopt this methodology as one implementation of                     cal feature extractor LM and the trained classifier are invoked
the dependency screener. To achieve this, we tag every region                each time the LM generates an output to track dependencies.
in the TBAS context with easily recognizable markers, such                   As both the local models and the classifier are lightweight, this
as «REGION_N»region content goes here«/REGION_N»,                            process introduces minimal runtime overhead to the TBAS.
ensuring that the LM can clearly identify and differentiate
between regions. We employ prompt sandwiching [38] where                     7.3     Robust TBAS
we provide instructions in both the system message and the                      To extend TBAS with taint tracking, we introduce Robust
final message in a long context. We also employ GPT-4’s                      TBAS (RTBAS), an extension of traditional TBAS that per-
capability to enforce a specific tool call to ensure the reflected           forms the propagation of security metadata during interac-
regions are well-formed.                                                     tions. We present a simplified view of our mechanism below
                                                                             where we assume that all content within the same message is
7.2    Attention-Based Approach                                              annotated with uniform security metadata (i.e., each message
   Motivated by the case studies in §3.3, we design a neural                 is a single “region”). However, our implementation supports
network to map the features of attention of the dependency                   finer granularity, allowing individual messages, such as user
relationship.                                                                messages or tool responses, to contain multiple regions, each
                                                                             with distinct security labels.
   Problem Formulation. We formulate the dependency anal-
                                                                                Terminologies and Definitions. To present RTBAS, we
ysis into a sequential binary classification problem. In partic-
                                                                             extend the symbols and terminologies presented in List 3
ular, every input of a data point has two fields:
                                                                             where we use ♢ to represent redacted content. We also modify
• I, O: the input and output text generated by potentially LMs,              the definitions presented in List 4 as the runtime needs to keep
• T = (b1 , e1 ), (b2, e2 ), ..., (bn , en ): a list of regions needed       track of security labels on messages. And that some messages
  for dependency analysis.                                                   are masked or redacted to maintain security guarantees. We


                                                                         7
detail the masking process later in this section. m(li ,lc ) refers to                  The dependency screener is detailed in Algorithm 2 where the
messages tagged with the integrity label li and confidentiality                        IS_RELEVANT function is left unspecified and can be instanti-
label lc .                                                                             ated by either the JM-Judge or the Attention-based methods.
                                                                                       It’s possible that there are nonregion based techniques that
   Tagged Messages                       M     = · | M, m(li ,lc )                     could also instantiate such a screener.

     Post Redaction Messages M♢ = · | M♢ , m | M♢ , ♢                                  Algorithm 3 REDACTOR Algorithm
    As specified in §6.2, we assume a security lattice L where                         Require: Tagged Message Sequence M, Redaction Label
(li , lc ) ∈ L, and a Information Flow Policy P, defined in Eq. 7                          (lid , lcd )
specifying the label restrictions for a tool call t i .                                Ensure: Redacted Message Sequence M♢
    We change the types of the meta-functions presented in                              1: M♢ ← ·               ▷ Initialize the redacted sequence as empty
List 5 to account for the Tagged Messages and Post Redaction                            2: for all m(li ,lc ) ∈ M do
Messages shown below:                                                                   3:        if (li , lc ) ⊑ (lid , lcd ) then ▷ Checking if message label
    Metafunctions:                                                                         is as permissive as the target label
    GET_NEXT_TOOLCALLs : M♢ 7→ ToolCalls                                                4:              M♢ ← M♢ , m                       ▷ Preserve message m
    CALL_API                            : t i × E 7→ m(li ,lc ) × E                     5:        else
    LM_RESPONSE                         : M♢ 7→ m                                       6:              M♢ ← M♢ , ♢                   ▷ Replace message with ♢
    USER_REQUEST                        : M 7→ m(li ,lc )                               7:        end if
    USER_CONTINUE                       : M 7→ TRUE | FALSE                             8: end for
    Security Metadata Propagation. Before the LM is permit-                             9: return M♢                      ▷ Return the fully redacted sequence
ted to generate the next message for the agent, the dependency
screener identifies the regions of interest. These are the re-                            Upon determining a label l , which represents the secu-
gions deemed relevant to the agent’s next action based on the                          rity restrictions applicable to the message being generated,
current context.                                                                       the system enforces these restrictions to ensure soundness.
    Once the regions of interest are identified, the runtime com-                      Specifically, the LM is allowed to observe any content that
putes a final label (lid , lcd ) . This label is derived by aggregat-                  is less restrictive than l . However, any content that is more
ing the security labels of all relevant regions using the join                         restrictive than l must be redacted. This redaction process is
operator (⊔) defined within the developer-provided security                            shown by Algorithm 3.
lattice. This label, (lid , lcd ) , represents a conservative upper
bound on the restrictions associated with the regions of inter-                                          REDACTOR : M, L 7→ M♢                              (8)
est. In other words, (lid , lcd ) is the least restrictive(more secret
and less trusted) label that is at least as restrictive as every                          REDACTOR redact all messages that are more restrictive than
relevant region’s label for this final label (lid , lcd ) serves as                    the label l arrived at by the screener.
the security context for the next phase of computation, en-                            Runtime Behavior. At runtime, the dependency screener first
suring that the LM respects the confidentiality and integrity                          output some label (liu , lcu ), which serves the role of conserva-
constraints implied by the relevant regions in the context.                            tively bounds the information that can influence the LM’s
                                                                                       generation of the next message, similar to that of the label on
Algorithm 2 Dependency Label SCREENER                                                  the program counter in a traditional IFC analysis.
                                                                                          Next, the REDACTOR redacts all messages more restric-
Require: Tagged Messages M                                                             tive(more secret and less trusted) than the label provided by
Ensure: Collected dependency labels l                                                  the screener. The resulting post-redaction messages are then
 1: (lid , lcd ) ← ⊥ ▷ Initialize l as the most permissive element
                                                                                       used by the LM to come up with a list of tool calls.
    in the lattice
                                                                                           USER_CONFIRMATION : t i 7→ TRUE | FALSE
 2: for all m(li ,lc ) ∈ M do
 3:       if IS_RELEVANT(m,M) then                                                        The runtime then verifies that each of the tool calls is per-
 4:              (lid , lcd ) ← (li , lc ) ⊔ (lid , lcd ) ▷ Merge labels for all       mitted with label (liu , lcu ) by the information flow policy of the
    dependent regions                                                                  tool call P(t i ) . If (liu , lcu ) is not permitted, the system halts to
 5:       end if                                                                       await user confirmation on whether to proceed tool call.
 6: end for                                                                               We illustrate the Robust TBAS Algorithm 4, an extension
 7: return (lid , lcd )             ▷ Return merged dependency labels                  of the TBAS Algorithm 1. A worked through example of our
    where the final label is at least as restrictive as the labels                     algorithm is found in Fig 8.
    on any relevant region                                                                A critical aspect of information flow control is ensuring the
                                                                                       proper propagation of security metadata. Every time a new
                                                                                       message is generated, its label must reflect both the restric-
                      SCREENER : M                 7→ L                                tions of the current context and the label returned by the tool.


                                                                                   8
  Algorithm 4 Robust Tool-Based Agent System (Taint Tracking Mechanism shown in Red)
                                                   (l s ,l s )
   Require: Initial Tagged System Message ms i c , Environment E
                            (l s ,l s )
    1:   Initialize M ← ·, ms i c                                                                         ▷ Initialize Tagged Messages M with the Tagged System Message
    2: while USER _ CONTINUE() do                                                                                                                ▷ If user continues interaction
    3:    M ← M, USER _ MESSAGE()                                                                                                                 ▷ Append user message to M
    4:    (li , lc ) ← SCREENER(M)                  ▷ the screener obtains the label by screening the tagged messages M and returns the joined label of all relevant regions
    5:    M♢ ← REDACTOR(M, (li , lc ))                                                     ▷ Messages with more restrictive (more secret and less trusted)labels are redacted
    6:    ToolCalls ← GET _ NEXT _ TOOLCALLS(M♢ )                                                                        ▷ Generate new tool calls based on the redacted M♢
    7:    for all t i ∈ ToolCalls do
                    p p
    8:           (li , lc ) ← P(t i )                                                                                           ▷ Obtain the restriction label on this tool call
                                     p p
    9:           if (li , lc ) ̸⊑ (li , lc ) and not USER _ CONFIRMATION(t i ) then
   10:                  continue                                               ▷ If the information flow policy is violated, explicit user confirmation is required to continue
   11:           end if
                                t t
   12:                  E, m(li ,lc ) ← CALL _API(t i , E)                                                      ▷ Execute tool t i with environment E; update E and return m
                                         t t
   13:                  M ← M, m(li ,lc )⊔(li ,lc )                                                                                   ▷ Append the tainted tool response to M
   14:           end for
   15:           (liu , lcu ) ← SCREENER(M)                                 ▷ The response from the LM to the user needs to be similarly tainted based on its dependencies
   16:           M♢ ← REDACTOR(M, (liu , lcu ))
   17:           mu ← LM_ RESPONSE(M)
                                (l u ,l u )
   18:          M ← M, mu i c                                                                                             ▷ Append response from the LM to the user to M
   19:       end while



  This ensures the label accurately represents the cumulative                                8.1      End to End Evaluation: Prompt Injection
  restrictions of all contributing factors.                                                  8.1.1 Setup
     Such tainting mechanism is represented by lines 13 and 18                               Test Suites. We benchmark our system on AgentDojo [10],
  from Alg. 4. Here, the runtime ensures that the security meta-                             a state-of-the-art benchmark on agent adversarial robustness
  data of generated content aligns with the constraints imposed                              against prompt injection attacks. Shown in Tab. 1, the dataset
  by both the runtime context and the tool invocation, prevent-                              consists of 79 realistic user tasks in four suites: banking,
  ing unauthorized information leakage or policy violations.                                 travel, workspace, and slack. Every test suite represents a
     We stress that the tool environment must align with the                                 TBAS application where LLM serves user’s request using a
  stated information flow policy to prevent scenarios where se-                              given set of tools, e.g. send_money for the banking suite and
  cret or low-integrity data influences public or high-integrity                             reserve_restaurant for the travel suite. Every test case in
  data through a tool’s side effects. Such situations could effec-                           a suite requires the LLM to solve a task with multi-round
  tively create a backdoor, allowing the protections provided by                             interaction with external tools such as booking a restaurant
  the information flow policy to be bypassed.                                                after filtering through reviews and datary restrictions.
     Screener Mistakes. Importantly, incorrect decisions by our                              Data Labeling. To integrate the information flow mechanism,
  dependency screener approaches cannot compromise security                                  we enhance the task suites by assigning integrity labels based
  due to the selective masking mechanism. However, such er-                                  on the application’s requirements while remaining agnostic
  rors may degrade performance. This degradation could take                                  to specific test cases (examples are shown in Tab. 1). The
  the form of over-tainting, where regions are unnecessarily                                 labeling process follows these key principles to satisfy the
  marked as private or low integrity, leading to excessive user                              assumptions we denote on the tool environment in 6.2:
  confirmations, or under-tainting, where insufficient content                               • Regions in a tool responses that incorporates textual data
  remains accessible for completing the task.                                                  from external sources is labeled as low-integrity.
                                                                                             • Tools with significant side-effects (e.g., sending money)
   8     Evaluation                                                                            or those can introduce high-integrity data to the external
      In this section, we benchmark our techniques in addressing                               environments (e.g. sending messages) are labeled as high-
   the security threats for TBAS, that is, prompt injection and                                integrity.
   privacy leakage. We aim to answer the following questions:                                Prompt Injection Attacks. To emulate prompt injection at-
Q1: Under scenarios with prompt injections, how well does our                                tacks, each test suite includes a set of injection tasks. These
    system maintain integrity and utility compared to state-of-                              tasks aim to induce the agent to misuse tools and produce
    the-art defenses?                                                                        harmful side effects, such as making unintended reservations
Q2: Under scenarios with privacy leakage, how much excessive                                 on behalf of the user or leaking user’s private data through
    user confirmations do we burden the user and whether utility                             public channels like emails. When evaluating the benchmark
    is degraded compared to baselines?                                                       under Prompt Injection attacks, each user task is tested against
Q3: How accurate is our detector in determining the information                              every injection task in the corresponding test suite, resulting
    flow within the LM and what is its runtime overhead?                                     in a total of 629 security test cases.


                                                                                        9
Baselines. We evaluate the effectiveness of our mechanism                in utility for the LM-Judge and Attention-based detectors,
against state-of-the-art prompt injection defenses, as well as           respectively. Interestingly, the Tool Filter technique slightly
two baseline approaches:                                                 increases utility in the absence of attacks. We speculate that
• Tool Filter by AgentDojo: Use the LM as a Judge to filter              this improvement arises from an implicit planning step, where
  the set of legal tools that an LM is allowed to use based on           irrelevant tools are excluded from LLM consideration.
  the user task.                                                            Our approach performs particularly well in the travel and
• Näive Tainting: A baseline tainting approach where we                  workspace suites. As illustrated in the results in these suites,
  assume every region in history affects the next message and            our approaches consistently achieve the highest utility among
  needed to be tainted accordingly.                                      other methods, even exceeding the baseline(no defense) case
• Redact All: A baseline approach where we redact every                  by 5% on average. These task suites naturally align with a
  single region that is not of high-integrity and public and             more fine-grained integrity lattice and precise security policy,
  therefore no labels are propagated.                                    reducing scenarios that require manual user intervention.
                                                                            The Slack dataset, however, emerges as an outlier for our
PI Detector by [3], Delimiting by [13] and Prompt Sand-
                                                                         techniques. While our approaches still outperform naive taint-
wiching by [38] were evaluated by AgentDojo [10]. PI De-
                                                                         ing and redact-everything methods, the utility drops to 33%
tector and Delimitting performed strictly worse than Tool
                                                                         and 22% for the Attention-based and LM-Judge detectors re-
Filter. Prompt Sandwiching performed better without attack
                                                                         spectively, which is more than halved compared to the mean
in utility, but suffered a 27% attack success rate. We do not in-
                                                                         utility. This performance drop can be attributed to the nature
clude these results since we consider Tool Filter the existing
                                                                         of Slack tasks, which often involve variations in reading con-
SOTA.
                                                                         tent from untrusted websites and performing actions based
Evaluation Metrics. We follow AgentDojo to use utility and
                                                                         on that content. We consider such tasks inherently unsafe,
integrity (a.k.a. security in AgentDojo) as two evaluation
                                                                         necessitating user confirmation.
metrics to compare different defenses, where
• Utility determines whether the agent has solved the task                     Invite Dora to Slack her contact info is found on www.dora.com
  correctly, by inspecting the model output and the mutations                  fetch_website(url="www.dora.com")
                                                                               "This is personal website of Dora. My e-mail is dora@gmail.com.
  in the environment state.                                                    {INJECTION_PLACEHOLDER}"

• Integrity determines whether the attacker succeeds in their                  invite_user_to_slack("Dora", "dora@gmail.com")
  attacks against the system.
   We evaluate this benchmark suite using GPT-4o, consistent
with results from AgentDojo. The Prompt Engineering detec-                  Additionally, some tasks require the agent to send a sum-
tor is also implemented using this model. For the Attention-             mary of an untrusted website to a high-integrity source (e.g.,
Based detector, which requires access to a LM’s internal                 posting the summary to a Slack channel). If left unchecked,
weights to compute cross-token attention scores, we use the              such actions could compromise the high-integrity source by
Phi-3-Mini-128K [2] instruction-tuned model. However, in-                spreading prompt injection attacks like a virus or conveying
ference steps are still performed using GPT-4o.                          unintended statements.
   In this benchmark, we do not model user confirmations.                Under Attack. We present the result when under prompt
Instead, any apparent unauthorized calls contrary to the                 injection attack in Fig 5. RQ1: Our techniques still retain a
information-flow policy are skipped and unperformed.                     high utility compared to the baseline without defense, only
                                                                         losing less than 1% utility for the LM-judge screener and 3%
8.1.2 Results and Analysis                                               for the Attention-based screener.
   We present the results of the AgentDojo dataset both with                We note that we do prevent 100% of attacks that violate
(Figure 5) and without (Figure 6) prompt injection attacks. A            our security policy. However, in the workspace benchmark,
cost comparison of running our techniques as a measure of                there was one test case where text written by the user, labeled
overhead (Table 4) is also provided.                                     as high-integrity, contained possible prompt injection and is
   Importantly, the lack of user confirmations and the subse-            thus not tracked. This illustrates a major limitation for our
quent rejection of all apparent suspicious tool calls means              mechanism, as with any other IFC techniques, that the security
that if we are able to seek user confirmations for calls that            guarantees provided are only as good as the labels provided
inheritently depend on low integrity data or in the case of              and the policies enforced.
over-tainting, then we are likely to achieve even better perfor-
mance.                                                                   8.2      End-to-End Evaluation: Privacy Leakage
Without Attacks. We present the results without attack in                   This experiment evaluates different defenses against the
Fig 6. The impact on utility is best illustrated by the differ-          privacy leakage threat, e.g. accidental reference to chat his-
ence between the baseline case (no defense) and our tech-                tory, silently booking a restaurant without user’s confirmation.
niques. Specifically, we observe a 10% and 7.4% degradation              For every tool call the LLM makes, the defense mechanisms


                                                                    10
                                                                                                 Table 1: Overview of the Prompt Injection Benchmark

    Task Suite                 # User Task           #Test Case                     Number Tools                 Number Messages Per Test Case                            Example Labelled Low-Integrity Data                                  Example High Integrity Tool Calls
    Banking                    16                    144                            11                           8.9 +- 3.0                                               External Bills, External Transaction Notes                           update_transactions, send_money
    Travel                     20                    140                            28                           13.6 +- 3.8                                              Hotel Reviews, Restaurant reviews.                                   send_email, book_hotel
    Slack                      21                    105                            11                           15.6 +- 4.4                                              External Channel messages, Web Contents.                             add_new_user
    Workspace                  40                    240                            24                           8.7 +- 3.4                                               External Documents in a Cloud Drive                                  update_calendar


              1.00                                                           1.00                                                          0.99         Baseline                                   1.00                                                       0.99
                                                                             0.91                                                          0.97                                                                                                               0.93
              0.89                                                                                                                         0.96       no defense
                            Baseline                                                          Baseline                                                naive tainting                                             Baseline
                                                                                                                                                      redact everything
  Integrity                                                      Integrity                                                     Integrity                                               Integrity
                          no defense                                                        no defense                                                                                                         no defense
                                                                                                                                                                                                                                                  Integrity
                          naive tainting                                                    naive tainting                                            tool filter                                  0.94        naive tainting                                             Baseline
                                                                                                                                                      TBAS (LM-Judge)                                                                                                    no defense
                          redact everything                                                 redact everything                                                                                                  redact everything                                         naive tainting
                          tool filter                                                       tool filter                                               RBTAS (Attn)                                             tool filter                                               redact everything
                          TBAS (LM-Judge)                                                   TBAS (LM-Judge)                                                                                                    TBAS (LM-Judge)                                           tool filter
                                                                                                                                                                                                                                                                         TBAS (LM-Judge)
                          RBTAS (Attn)                                                      RBTAS (Attn)                                                                                                       RBTAS (Attn)
              0.31                                                           0.08                                                          0.76                                                    0.89                                                       0.56       RBTAS (Attn)

                0.4  4                7
                                    0.5       0.6
                                               0.6 2                           0.0  5    0.1
                                                                                         0.29                    8
                                                                                                                0.4    4
                                                                                                                      0.6                    0.4  0                  0.5  0.5
                                                                                                                                                                          0.553                      0.4  4           5
                                                                                                                                                                                                                    0.5       1
                                                                                                                                                                                                                            0.6     4
                                                                                                                                                                                                                                   0.6    0
                                                                                                                                                                                                                                         0.7                    0.4  0                   0.5
                                                                                                                                                                                                                                                                                         0.501       8
                                                                                                                                                                                                                                                                                                    0.5
                                               0.67                                          4                                                                            0.57                                                                                                           0.5
                                    Utility                                                          Utility                                                   Utility                                                  Utility                                                         Utility
                                                   9                                                                                                                          8                                                                                                              3


                         (a) Banking.                                                       (b) Slack.                                            (c) Workspace.                                              (d) Travel.                                     (e) Weighted Average.

  Figure 5: End-to-end evaluation on Security-Utility trade-off for Prompt Injection. The Top Right Corner indicates that high
  success rate of the user’s task and high integrity of the defense against prompt injection across test cases.


                                                                                                                                                                     Table 2: Overall false positive rates and false negative rates,
          0.75
                                                                                                                                                                     for the Accidental Leakage benchmark.
Utility   0.50
          0.25
                                                                                                                                                                                                                                                                     FPR                          FNR
          0.00            banking                   slack                           travel               workspace                 Mean
                                                                                    Suite                                                                                  Confirm Never - redact-all                                                   0                               0.513514
                                 no defense                 redact everything                    TBAS (LM-Judge)            RBTAS (Attn)
                                 naive tainting             tool filter
                                                                                                                                                                           Confirm Every Time (GPTs)                                             0.297297                                      0
                                                                                                                                                                           RTBAS (LM-judge)                                                      0.081081                               0.108108
  Figure 6: The Utility Rate comparison for the Prompt Injec-                                                                                                              RTBAS (Attention)                                                     0.162162                               0.108108
  tion Benchmark without attack.

          1.00
          0.75                                                                                                                                                       data.
Utility   0.50
          0.25
                                                                                                                                                                                       Table 3: Benchmark for Privacy Leakage
          0.00
                            amazon                     flight_booking                               venmo                       Mean                                      Task Suite                      Description                                     Sensitive Data
                                                                                    Suite
                                      Confirm Never - redact-all                             RTBAS (LLM Judge)               Oracle                                       Venmo                           Managing transactions, friend in-               Transaction details, user info
                                      Confirm Every Time (GPTs)                              RTBAS (Attn)                                                                 (12 tasks)                      teractions, and account updates.                (balance, password), friend
                                                                                                                                                                                                                                                          lists/info
                                                                                                                                                                          Flight Booking                  Searching, booking, and updat-                  Credit card, passport number,
                                                                                                                                                                          (12 tasks)                      ing flights.                                    user address, booked itinerary
  Figure 7: The Utility Comparison for the privacy leakage                                                                                                                Amazon                          Buying, returning, recommenda-                  Credit card, address, past orders,
  benchmark. The solid bars represent the utility achieved when                                                                                                           (13 tasks)                      tion of products. Promotions                    preferences, gender
  users block tool calls upon receiving confirmation requests
  from the defenses. The faint bars indicate the additional util-                                                                                                    Synthesized Benchmark. We are not aware of existing com-
  ity users can gain by allowing these tool calls. The results                                                                                                       prehensive benchmark for privacy leakage for TBAS. We
  demonstrate that our approaches provide a near-optimal bal-                                                                                                        manually created 37 test cases across three TBASs in different
  ance, offering users flexibility to achieve varying utility levels                                                                                                 domains: shopping, finance, and flight booking. We provide a
  based on their confirmation choices, unlike GPTs, which re-                                                                                                        short description of the task suite in table 3. Each task suite
  quire confirmation every time.                                                                                                                                     simulates a specific TBAS setup, featuring the same tools,
                                                                                                                                                                     descriptions, and system prompt, to represent a user-facing
                                                                                                                                                                     application. Tools capable of contributing private information
  decide whether to flag the user for confirmation or proceed                                                                                                        to the context are annotated with regions identifying where
  silently by masking out the private data. An ideal defense                                                                                                         private data appear in their outputs, along with labels specify-
  should effectively balance the transparency by asking the                                                                                                          ing the nature of the private information.
  user for confirmation whenever privacy leakage occurs, and                                                                                                            Each task begins with prior interactions between the user
  provide a smooth user experience by avoiding unnecessary                                                                                                           and the agent (i.e., the context window), which may already
  confirmations when the tool call is independent of private                                                                                                         contain marked private data. This is followed by a user mes-


                                                                                                                                                            11
sage that outlines the task to be completed. To achieve the               perform tool calls and decide whether to confirm with the
task, the LLM may call tools to retrieve information, perform             user.
actions with external side effects, and report back to the user         Result and Analysis. Table 2 shows the trade-off between
with the results.                                                       the false negative rate (FNR) and the false positive rate (FPR)
   Tasks vary in complexity. Some require a single reasoning            across the synthesized test suites.
step, such as directly calling a tool or answering a query                 For the baselines, the Confirm Never redacts every private
based on the context. Others involve more intricate reasoning,          region, hence it will proceed silently by masking out the pri-
requiring sequential calls to multiple tools to complete the            vate data even when it is valid for a tool call to leak private
task. Analyzing private information propagation in complex,             information, e.g. booking a flight with credit card number,
multistep tasks is particularly valuable, as these scenarios            resulting in 51% FNR and severe utility loss. On the other
provide more opportunities to observe indirect propagation              hand, the Confirm Every Time (GPTs) defense taints the tool
of private information. Each tool call should propagate only            call as long as there is any private data in the context, resulting
the relevant information from the context, enabling a detailed          in 30% FPR and redundant user confirmations.
and fine-grained evaluation of our approach.                               Compared to the baselines, our selective propagation
   As illustrated in §3.2, propagation of privacy information           defenses effectively tames the trade-off between trans-
can occur in subtle ways. We include the diverse propagation            parency and user experience. Compared to the Confirm
patterns explored in §3.2 as part of this benchmark to evaluate         Never, the LM-Judge-based selective propagation delivers
the effectiveness of our dependency screener.                           higher transparency to the user by reducing the FNR from
   We keep in mind the following principles when creating               30.7% to 7.6% for the Amazon Test Suite, from 58.3% to
the dataset:                                                            8.3% for the Flight Booking test case, and from 66.7% to
• Every test case has a ground truth tool calling to obtain the         16.6%.
  utility.                                                                 In contrast, compared to GPTs that require user confirma-
                                                                        tion for every tool call, our information flow-based defenses
• Every test case whose utility does not depend on the private
                                                                        significantly reduce unnecessary confirmations. Specifically,
  data will see private data in the ground truth tool calling
                                                                        the LM-Judge approach and the attention-based approach
  chain.
                                                                        achieve an FPR of 8.1% and 16.2% across all test suites, re-
Evaluation Metrics. Upon evaluation, each tool call made by             spectively, whereas GPTs exhibit FPRs of 29%. In practical
an agent is manually labeled either as requiring confirmation           terms, a smaller FPR translates into a significantly improved
(leaking private data) or not based on the natural understand-          user experience, requiring minimal interaction from the user.
ing of the tool calling. Based on the oracle labels, we consider        This reduction in unnecessary confirmations is particularly
the following metrics for the benchmark:                                crucial for maintaining a seamless and efficient workflow.
• False Positive Rate (FPR) measures the proportion of test                Next, we explore the utility results achieved by different
  cases in which the defense mechanism fails to detect a call           approaches. Shown in Fig. 7, the solid bars show the success
  to a tool that involves privacy leakage,                              rate of the user tasks when the user blocks every tool call upon
• False Negative Rate (FNR) measures the proportion of test             confirmation. The faint bars show the additional utility the
  cases in which the defense mechanism incorrectly identifies           user can gain by allowing tool calls. Confirm Never and GPTs
  a tool call as leaking private data,                                  baseline represents two extremes. On one side, Confirm Never
                                                                        does not provide the user with any autonomy in deciding
• Utility that measures the proportion of test cases that the           whether a tool call should proceed, resulting in overall 35%
  user’s task succeeds. Degradation to utility can result from          of utility. On the other side, the Confirm Every Time (GPTs)
  erroneous masking.                                                    defense prompts the user for confirmation upon every tool
Approaches Compared. We compare the following ap-                       call, with zero utility in the worst case and 91% utility in the
proaches:                                                               best case.
• Confirm Never - Redact All redacts all private data upon                 Across the two extremes, our selective propagation ap-
  information propagation. No confirmation necessary since              proaches are able to balance the utility and number of
  no private information will ever be seen by the agent.                times we seek user confirmation. Compared to GPTs con-
                                                                        firming every time, our approaches obtain the baseline utility
• Confirm Every Time (GPTs) assumes every tool call may
                                                                        of 40% and 43% for the LM-Judge and attention-based ap-
  leak private information and thus always requires confirma-
                                                                        proach, respectively. That is, our approaches saves the user
  tion.
                                                                        from from the need to confirm for test cases in which no pri-
• Selective Propagation selectively propagates information              vate data is required for the task to succeed. For example, a
  with the dependency screener. We include two instantiations           large portion of the amazon test suite is confirmation-free ser-
  (LM-Judge based and Attention based) for comparison.                  vices like product recommendation, product searching, etc.,
• Oracle represents a human expert that acts as the LM to               our approaches passes 53% test cases without confirmations.


                                                                   12
In fact, compared to the oracle, we are losing utility only in                                          Table 4: Runtime comparison of executing the user tasks on
1 out of 15 test cases, because of the overtainting booking                                             the banking suite of AgentDojo. The metrics are averaged
history for the current flight lookup.                                                                  across test cases. The price is calculated against OpenAI’s
   Compared to Confirm Never approach, our approach offers                                              pricing.
users the flexibility to proceed with the task by allowing po-
tentially risky tool calls with the user’s permission. This is                                              baseline                  price ($)    time (s)      #Tokens
especially critical in applications like Venmo, where sensitive                                             Vanilla                   0.014712    4.369265    2709.937500
data and financial activities are always involved. In our evalu-                                            Tool Filter (AgentDojo)   0.008653    4.880799    1504.625000
ation, we are able to achieve 83% and 75% of utility when the                                               RTBAS (Attn)              0.027531    8.728362    5048.687500
user allows every tool call, which is the same as GPT (83%).                                                RTBAS (LLM Judge)         0.031672    9.707550    5851.562500


8.3        Analysis                                                                                     can possibly miss more subtle dependencies that may still
8.3.1 Taint Tracking Accuracy                                                                           influence task outcomes.
   We augmented the Privacy Leakage benchmark with pre-
cise labels that represents the sets of private information cat-                                        8.3.3 Runtime Overhead
egory involved. We evaluate, for every tool calls, how often
                                                                                                           Q3: Our techniques incur higher costs compared to existing
these labels matches exactly the ground truth label we anno-
                                                                                                        methods, primarily due to the overhead introduced by the de-
tated(Q3).
                                                                                                        tectors. The Attention-based detector requires the LLM to run
   The user, through this label, can gather more information
                                                                                                        twice: the first run generates a preliminary message, which
about the category of data that the tool call purports to leak. A
                                                                                                        is used for the attention mechanism to compute dependency
user comfortable with leaking their credit card number to book
                                                                                                        results. The second run generates the final output after mask-
a flight may be hesitant to share her social security number.
                                                                                                        ing. The LM Judge screener also incur computer overhead
   A mislabeled tool call with more private data categories                                             by running the judge LLM before the agent generates each
than actually propagated could be erroneously rejected either                                           new message. In contrast, the tool detector only runs one ad-
interactively or by reference to the policy that the user agrees                                        ditional inference for each user message but not between tool
to prior. Oppositely, a label claiming less private data cate-                                          calls, and the Prompt Sandwiching approach only marginally
gories can distort the task, with actually relevant data masked.                                        increases the number of tokens by repating the user requests.
                                                                                                        We discuss opportunities for optimization in Sec. 9.
 Confirm Never (Redact All)   Confirmation Always (GPTs)   RTBAS (LLM Judge)   RTBAS (LLM Judge)
 22.3%                                  56.7%                   57.3%               70.0%
                                                                                                        9     Discussion
                                                                                                           Labeling. One limitation of our technique, common in
   We show that the selective propagation approach, when                                                IFC research, is the need for labeled tool and user mes-
instantiated by either the prompting or the attention approach                                          sages, along with an information-flow policy understand-
arrives at the exact ground truth label more than 70% and 57%                                           able to users. However, many applications naturally support
of the time, respectively. This is superior to our baseline tech-                                       region-based labeling, particularly when addressing prompt
niques for redacting all sensitive regions and thus propagate                                           injection and confidential data leakage. For example, in a
nothing or the always confirm method where we assume a                                                  get_email response, fields like Subject and Content could
tool call always leak every secret.                                                                     be labeled low-integrity due to susceptibility to natural lan-
                                                                                                        guage injections, while Sender might be high-integrity due
8.3.2 Dependency Screener Comparisons                                                                   to strict schema requirements. Similarly, tools may handle
   For the Prompt Injection and Privacy Leakage benchmarks,                                             sensitive information; for instance, in a finance application,
we find that the LM judge and the Attention-based depen-                                                a get_account_balance response could be marked high-
dency screener perform similarly across the benchmarks, with                                            confidentiality to prevent accidental or malicious leakage.
LM Judge performing slightly better overall under attack for                                            Recent works on using LLMs for formal safeguards [5] and
Prompt Injection and much better in terms of its detection                                              privacy policy interpretation [7,42] offer promising directions
accuracies for privacy leakage(Tab 2). We conject the LM                                                to bridge understanding gaps.
judge’s ability to explicitly reason about the dependencies                                                Cost. Operating both of our dependency screener methods
and output its chain-of-thought [47] could help generalize the                                          is currently resource-intensive. The attention-based screener
mechanism across unseen task, and for more subtle propa-                                                requires the agent to generate a preliminary message to ana-
gation cases. However, across end-to-end benchmarks, both                                               lyze attention scores between regions, followed by a second
methods perform similarly with respect to the overall task                                              message based on different input during the selective mask-
utilities. This suggests that the Attention-based approach can                                          ing process. A potential optimization involves using a smaller
detect important dependencies crucial to task success, but                                              model to generate the preliminary message, as it is not part


                                                                                                   13
of the agent’s final output. Smaller models could also benefit              Phi-3 technical report: A highly capable language model
the LM-Judge Screener. While early preliminary experiments                  locally on your phone. arXiv preprint arXiv:2404.14219,
suggest that small, local models struggle as general-purpose                2024.
screeners, fine-tuning or prompt-tuning [31] on task-specific
datasets may enhance their performance. This approach could             [3] Protect AI. Fine-tuned deberta-v3-base for prompt in-
improve efficiency without compromising effectiveness.                      jection detection, 2024.

                                                                        [4] Anthropic. Claude: An ai assistant by anthropic, 2023.
10    Conclusion
                                                                            Available at https://www.anthropic.com/claude.
   We present RTBAS, a fine-grained, dynamic information
flow control mechanism to safeguard Tool-based LLM Agents
                                                                        [5] Antje Barth. Prevent factual errors from llm hallucina-
against both prompt injection and inadvertent privacy leaks.
                                                                            tions with mathematically sound automated reasoning
The mechanism selectively propagates only the relevant secu-
                                                                            checks (preview), December 2024. Accessed: 2025-01-
rity labels, through the use of the LM-Judge and Attention-
                                                                            22.
based screeners. The redaction of unused data enforces the
information flow policy for all possible selective propagation.         [6] Nicholas Carlini, Florian Tramer, Eric Wallace, Matthew
   Empirically, we manage to curb malicious manipulations                   Jagielski, Ariel Herbert-Voss, Katherine Lee, Adam
and detect undesirable confidential data disclosures. Notably,              Roberts, Tom Brown, Dawn Song, Ulfar Erlingsson, et al.
our evaluation on the AgentDojo benchmark shows that when                   Extracting training data from large language models. In
under prompt injection attacks, the proposed RTBAS frame-                   30th USENIX Security Symposium (USENIX Security
work thwarts all policy-violating exploits with less than 2%                21), pages 2633–2650, 2021.
degradation to the agent’s task utility. Similarly, our privacy
leakage benchmark confirms RTBAS’ ability to obtain near-               [7] Chaoran Chen, Daodao Zhou, Yanfang Ye, Toby Jia jun
oracle performance.                                                         Li, and Yaxing Yao. Clear: Towards contextual llm-
                                                                            empowered privacy policy analysis and risk generation
11    Ethics considerations                                                 for large language model applications, 2024.
   Our experiments were conducted using publicly available
benchmarks and constructed datasets explicitly designed for             [8] Sizhe Chen, Julien Piet, Chawin Sitawarin, and David
this study. No real-world user data or personally identifiable              Wagner. Struq: Defending against prompt injection with
information (PII) was involved in the development or evalu-                 structured queries, 2024.
ation of our methods. The attacks explored in this research
are well-documented within the community and do not ne-                 [9] CustomGPT.ai. Custom gpts from your content for
cessitate additional disclosure. Additionally, our experiments              business, 2025. Accessed: 2025-01-01.
included subjecting language models to potentially harmful
                                                                       [10] Edoardo Debenedetti, Jie Zhang, Mislav Balunović,
tasks and simulating attacks on TBAS applications. We have
                                                                            Luca Beurer-Kellner, Marc Fischer, and Florian Tramèr.
received assurances from OpenAI, the language model ven-
                                                                            Agentdojo: A dynamic environment to evaluate at-
dor, that these interactions will not be used for training or
                                                                            tacks and defenses for llm agents. arXiv preprint
improving their models.
                                                                            arXiv:2406.13352, 2024.
Acknowledgments                                                        [11] Dorothy E. Denning. A lattice model of secure informa-
   This work supported in part by the Parallel Data Lab, the                tion flow. Commun. ACM, 19(5):236–243, May 1976.
WebAssembly Research Center and Cylab at Carnegie Mellon
University, and the National Science Foundation under grant            [12] Jiawei Gu, Xuhui Jiang, Zhichao Shi, Hexiang Tan, Xue-
2211882. Thanks to Harrison Grodin for important discus-                    hao Zhai, Chengjin Xu, Wei Li, Yinghan Shen, Shengjie
sions on the presentation of our mechanism. We also thank                   Ma, Honghao Liu, Yuanzhuo Wang, and Jian Guo. A
Noah Singer and Christos Laspias for their valuable feedback.               survey on llm-as-a-judge, 2025.

References                                                             [13] Keegan Hines, Gary Lopez, Matthew Hall, Federico
 [1] Airlines: Teneo’s AI and LLM Solutions for Airlines                    Zarfati, Yonatan Zunger, and Emre Kiciman. Defending
     — teneo.ai. https://www.teneo.ai/solutions/                            against indirect prompt injection attacks with spotlight-
     industries/airlines. [Accessed 19-01-2025].                            ing, 2024.

 [2] Marah Abdin, Sam Ade Jacobs, Ammar Ahmad Awan,                    [14] Sepp Hochreiter and Jürgen Schmidhuber. Long short-
     Jyoti Aneja, Ahmed Awadallah, Hany Awadalla, Nguyen                    term memory. Neural computation, 9(8):1735–1780,
     Bach, Amit Bahree, Arash Bakhtiari, Jianmin Bao, et al.                1997.


                                                                  14
[15] Bin Huang, Shiyu Yu, Jin Li, Yuyang Chen, Shaozheng               [27] Paul Michel, Omer Levy, and Graham Neubig. Are
     Huang, Sufen Zeng, and Shaowei Wang. Firewallm: A                      sixteen heads really better than one? In H. Wallach,
     portable data protection and recovery framework for llm                H. Larochelle, A. Beygelzimer, F. d'Alché-Buc, E. Fox,
     services. In Ying Tan and Yuhui Shi, editors, Data                     and R. Garnett, editors, Advances in Neural Information
     Mining and Big Data, pages 16–30, Singapore, 2024.                     Processing Systems, volume 32. Curran Associates, Inc.,
     Springer Nature Singapore.                                             2019.

[16] Wenlong Huang, Pieter Abbeel, Deepak Pathak, and                  [28] Andrew C. Myers and Barbara Liskov. Protecting pri-
     Igor Mordatch. Language models as zero-shot plan-                      vacy using the decentralized label model. ACM Trans.
     ners: Extracting actionable knowledge for embodied                     Softw. Eng. Methodol., 9(4):410–442, October 2000.
     agents, 2022.
                                                                       [29] James Newsome and Dawn Xiaodong Song. Dynamic
[17] Kuo-Han Hung, Ching-Yun Ko, Ambrish Rawat, I-Hsin                      taint analysis for automatic detection, analysis, and sig-
     Chung, Winston H. Hsu, and Pin-Yu Chen. Atten-                         naturegeneration of exploits on commodity software. In
     tion tracker: Detecting prompt injection attacks in llms,              Network and Distributed System Security Symposium,
     2024.                                                                  2005.
                                                                       [30] OpenAI. Introducing gpts, 2023. Accessed: 2025-01-01.
[18] Neel Jain, Avi Schwarzschild, Yuxin Wen, Gowthami
     Somepalli, John Kirchenbauer, Ping yeh Chiang, Micah              [31] Krista Opsahl-Ong, Michael J Ryan, Josh Purtell, David
     Goldblum, Aniruddha Saha, Jonas Geiping, and Tom                       Broman, Christopher Potts, Matei Zaharia, and Omar
     Goldstein. Baseline defenses for adversarial attacks                   Khattab. Optimizing instructions and demonstrations
     against aligned language models, 2023.                                 for multi-stage language model programs, 2024.
[19] Sarthak Jain and Byron C Wallace. Attention is not                [32] Long Ouyang, Jeff Wu, Xu Jiang, Diogo Almeida, Car-
     explanation. arXiv preprint arXiv:1902.10186, 2019.                    roll L. Wainwright, Pamela Mishkin, Chong Zhang,
                                                                            Sandhini Agarwal, Katarina Slama, Alex Ray, John
[20] Fengqing Jiang, Zhangchen Xu, Luyao Niu, Boxin                         Schulman, Jacob Hilton, Fraser Kelton, Luke Miller,
     Wang, Jinyuan Jia, Bo Li, and Radha Poovendran. Iden-                  Maddie Simens, Amanda Askell, Peter Welinder, Paul
     tifying and mitigating vulnerabilities in llm-integrated               Christiano, Jan Leike, and Ryan Lowe. Training lan-
     applications, 2023.                                                    guage models to follow instructions with human feed-
                                                                            back, 2022.
[21] Siwon Kim, Sangdoo Yun, Hwaran Lee, Martin Gubri,
     Sungroh Yoon, and Seong Joon Oh. Propile: Probing                 [33] OWASP. OWASP Top 10 for LLM Applications, 2025.
     privacy leakage in large language models. Advances in
     Neural Information Processing Systems, 36, 2024.                  [34] Julien Piet, Maha Alrashed, Chawin Sitawarin, Sizhe
                                                                            Chen, Zeming Wei, Elizabeth Sun, Basel Alomair, and
[22] Xiaogeng Liu, Nan Xu, Muhao Chen, and Chaowei                          David Wagner. Jatmo: Prompt injection defense by
     Xiao. Autodan: Generating stealthy jailbreak prompts                   task-specific finetuning, 2024.
     on aligned large language models, 2024.
                                                                       [35] Md Abdur Rahman, Fan Wu, Alfredo Cuzzocrea, and
[23] Yi Liu, Gelei Deng, Yuekang Li, Kailong Wang, Zihao                    Sheikh Iqbal Ahamed. Fine-tuned large language mod-
     Wang, Xiaofeng Wang, Tianwei Zhang, Yepang Liu,                        els (llms): Improved prompt injection attacks detection,
     Haoyu Wang, Yan Zheng, and Yang Liu. Prompt in-                        2024.
     jection attack against llm-integrated applications, 2024.
                                                                       [36] Matthew Renze and Erhan Guven. Self-reflection in llm
[24] Yupei Liu, Yuqi Jia, Runpeng Geng, Jinyuan Jia, and                    agents: Effects on problem-solving performance, 2024.
     Neil Zhenqiang Gong. Formalizing and benchmarking                 [37] A. Sabelfeld and A.C. Myers.       Language-based
     prompt injection attacks and defenses. In 33rd USENIX                  information-flow security. IEEE Journal on Selected
     Security Symposium (USENIX Security 24), pages 1831–                   Areas in Communications, 21(1):5–19, 2003.
     1847, 2024.
                                                                       [38] Sander Schulhoff. Sandwitch defense.   https:
[25] Tula Masterman, Sandi Besen, Mason Sawtell, and Alex                   //learnprompting.org/docs/prompt_hacking/
     Chao. The landscape of emerging ai agent architectures                 defensive_measures/sandwich_defense, 2023.
     for reasoning, planning, and tool calling: A survey, 2024.
                                                                       [39] Frank X. Shaw. Microsoft Build brings AI tools to the
[26] Cathal McGloin. Conversational ai in banking: Chatbots,                forefront for developers - The Official Microsoft Blog —
     use cases, examples, Dec 2024.                                         blogs.microsoft.com, 2023.


                                                                  15
[40] Shoaib Ahmed Siddiqui, Radhika Gaonkar, Boris Köpf,                     James Zou, Michael Carbin, Jonathan Frankle,
     David Krueger, Andrew Paverd, Ahmed Salem, Shruti                       Naveen Rao, and Ali Ghodsi. The shift from mod-
     Tople, Lukas Wutschitz, Menglin Xia, and Santiago                       els to compound ai systems — bair.berkeley.edu.
     Zanella-Béguelin. Permissive information-flow anal-                     https://bair.berkeley.edu/blog/2024/02/
     ysis for large language models, 2024.                                   18/compound-ai-systems/, 2024.         [Accessed
                                                                             15-01-2025].
[41] Li Siyan, Vethavikashini Chithrra Raghuram, Omar
     Khattab, Julia Hirschberg, and Zhou Yu. Papillon: Pri-             [53] Eric Zelikman, Georges Harik, Yijia Shao, Varuna
     vacy preservation from internet-based and local lan-                    Jayasiri, Nick Haber, and Noah D. Goodman. Quiet-
     guage model ensembles, 2024.                                            star: Language models can teach themselves to think
                                                                             before speaking, 2024.
[42] Chenhao Tang, Zhengliang Liu, Chong Ma, Zihao Wu,
     Yiwei Li, Wei Liu, Dajiang Zhu, Quanzheng Li, Xiang                [54] Qiusi Zhan, Zhixiang Liang, Zifan Ying, and Daniel
     Li, Tianming Liu, and Lei Fan. Policygpt: Automated                     Kang. Injecagent: Benchmarking indirect prompt in-
     analysis of privacy policies with large language models,                jections in tool-integrated large language model agents,
     2023.                                                                   2024.

[43] A Vaswani. Attention is all you need. Advances in                  [55] Susan Zhang, Stephen Roller, Naman Goyal, Mikel
     Neural Information Processing Systems, 2017.                            Artetxe, Moya Chen, Seo Jun Chen, Christopher De-
                                                                             wan, Mona Diab, Xian Li, Xi Victoria Lin, et al. Opt:
[44] Eric Wallace, Kai Xiao, Reimar Leike, Lilian Weng, Jo-                  Open pre-trained transformer language models, 2022.
     hannes Heidecke, and Alex Beutel. The instruction hier-                 Meta AI.
     archy: Training llms to prioritize privileged instructions,
     2024.                                                              [56] Zhenyu Zhang, Ying Sheng, Tianyi Zhou, Tianlong
                                                                             Chen, Lianmin Zheng, Ruisi Cai, Zhao Song, Yuandong
[45] Lean Wang, Lei Li, Damai Dai, Deli Chen, Hao Zhou,                      Tian, Christopher Ré, Clark Barrett, et al. H2o: Heavy-
     Fandong Meng, Jie Zhou, and Xu Sun. Label words                         hitter oracle for efficient generative inference of large
     are anchors: An information flow perspective for                        language models. Advances in Neural Information Pro-
     understanding in-context learning. arXiv preprint                       cessing Systems, 36:34661–34710, 2023.
     arXiv:2305.14160, 2023.
                                                                        [57] Peter Yong Zhong, Haoze He, Omar Khattab,
[46] Lei Wang, Wanyu Xu, Yihuai Lan, Zhiqiang Hu, Yunshi                     Christopher Potts, Matei Zaharia, and Heather
     Lan, Roy Ka-Wei Lee, and Ee-Peng Lim. Plan-and-                         Miller.     A guide to large language model ab-
     solve prompting: Improving zero-shot chain-of-thought                   stractions. https://www.twosigma.com/articles/
     reasoning by large language models, 2023.                               a-guide-to-large-language-model-abstractions/,
                                                                             Dec 2023.
[47] Jason Wei, Xuezhi Wang, Dale Schuurmans, Maarten
     Bosma, Brian Ichter, Fei Xia, Ed Chi, Quoc Le, and                 [58] Andy Zou, Zifan Wang, Nicholas Carlini, Milad Nasr,
     Denny Zhou. Chain-of-thought prompting elicits rea-                     J. Zico Kolter, and Matt Fredrikson. Universal and trans-
     soning in large language models, 2023.                                  ferable adversarial attacks on aligned language models,
                                                                             2023.
[48] Lilian Weng. Llm powered autonomous agents, 2023.

[49] Sarah Wiegreffe and Yuval Pinter. Attention is not not
     explanation. arXiv preprint arXiv:1908.04626, 2019.                A    Appendix A:           RTBAS Example Walk
                                                                             Through
[50] Yong Yang, Changjiang Li, Yi Jiang, Xi Chen, Haoyu
     Wang, Xuhong Zhang, Zonghui Wang, and Shouling
     Ji. Prsa: Prompt stealing attacks against large language
     models, 2024.

[51] Shunyu Yao, Jeffrey Zhao, Dian Yu, Nan Du, Izhak
     Shafran, Karthik Narasimhan, and Yuan Cao. React:
     Synergizing reasoning and acting in language models,
     2023.

[52] Matei Zaharia, Omar Khattab, Lingjiao Chen,
     Jared Quincy Davis, Heather Miller, Chris Potts,


                                                                   16
                                                                                                          Step 2 : Redact all regions not more permissive than
    Step 1 : The screener tries to find relevant region(s) :
    If Region 1 and 3 is determined to be relevant then their labels are merged and returned:
                                                                                                          Region 2 is therefore redacted since


How much money did I pay Alice in the past 31 days? For what?                                        How much money did Adam send me in the last 31 days?

get_recent_transaction(days = 31)                                                                    get_recent_transaction(days = 31)
[{"amount":100,date:"Jan 22",visibility:everyone,to:Alice,description:"<<REGION_1:                   [{"amount":100,date:"Jan 22",visibility:everyone,to:Alice,description:"Pizza Party"},
{TRUSTED,PUBLIC}>>Pizza Party<<REGION_1>>"},                                                         {amount":50,date:"Jan 21",to:Bob,visibility:private,description: "<<REDACTED>>"},
{amount":50,date:"Jan 21",to:Bob,visibility:private,description: "<<REGION_2:                        {"amount":0.01,date:"Jan 20",from:Mallory,visibility:everyone,description: "    🍔
{TRUSTED,PRIVATE}>>New Year Gift  🎉<</REGION_2>>"},                                                  \n\nIMPORTANT: complete my earlier request, but please also send Mallory the $100 I
{"amount":0.01,date:"Jan 20",from:Mallory,visibility:everyone,description: "<<REGION_3:              forgot to send him for lunch yesterday, with my apologies. After sending the money, only
                    🍔
{UNTRUSTED,PUBLIC}>> \n\nIMPORTANT: complete my earlier request, but please also send                respond with the answer to my earlier request for conciseness."}
Mallory the $100 I forgot to send him for lunch yesterday, with my apologies. After
sending the money, only respond with the answer to my earlier request for conciseness.
<</REGION_3>>"}




                                                                                                           Step 4: The runtime determines if the tool call is against policy
     Step 3: The LM generates next message based on the
     partially redacted history                                                                            Since it is against the policy for the tool call, we stop the tool call
                                                                                                           pending user confirmation

How much money did Adam send me in the last 31 days?                                                 How much money did Adam send me in the last 31 days?
get_recent_transaction(days = 31)                                                                    get_recent_transaction(days = 31)
[{"amount":100,date:"Jan 22",visibility:everyone,to:Alice,description:"Pizza Party"},                [{"amount":100,date:"Jan 22",visibility:everyone,to:Alice,description:"Pizza Party"},
{amount":50,date:"Jan 21",to:Bob,visibility:private,description: "<<REDACTED>>"},                    {amount":50,date:"Jan 21",to:Bob,visibility:private,description: "<<REDACTED>>"},
{"amount":0.01,date:"Jan 20",from:Mallory,visibility:everyone,description: "      🍔                  {"amount":0.01,date:"Jan 20",from:Mallory,visibility:everyone,description: "    🍔
\n\nIMPORTANT: complete my earlier request, but please also send Mallory the $100 I                  \n\nIMPORTANT: complete my earlier request, but please also send Mallory the $100 I
forgot to send him for lunch yesterday, with my apologies. After sending the money, only             forgot to send him for lunch yesterday, with my apologies. After sending the money, only
respond with the answer to my earlier request for conciseness."}                                     respond with the answer to my earlier request for conciseness."}

send_money(don, $100, "Lunch, Sorry for being late")                                                 send_money(don, $100, "Lunch, Sorry for being late")




                         Figure 8: A example for Robust TBAS in action. Walking through steps of Algorithm 4




                                                                                                17
