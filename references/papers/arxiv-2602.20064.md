                                                         The LLMbda Calculus:
                                             AI Agents, Conversations, and Information Flow
                                                                                                        Zac Garby
                                                                                             University of Nottingham, UK
                                                                                                  Andrew D. Gordon
                                                                                              University of Edinburgh, UK
                                                                                                      David Sands
                                                                  Chalmers University of Technology and The University of Gothenburg, Sweden


                                         Abstract—A conversation with a large language model (LLM)              By iterating generation itself, we can build up a chat or




arXiv:2602.20064v1 [cs.PL] 23 Feb 2026
                                         is a sequence of prompts and responses, with each response             dialogue from an alternating sequence of prompts and re-
                                         generated from the preceding conversation. AI agents build such        sponses. Let a prompt-response conversation, c, be a sequence
                                         conversations automatically: given an initial human prompt, a
                                         planner loop interleaves LLM calls with tool invocations and           [(p1 , r1 ), . . . , (pn , rn )], where each ri+1 is generated from the
                                         code execution. This tight coupling creates a new and poorly           concatenation p1 + r1 + · · · + pi + ri + pi+1 .
                                         understood attack surface. A malicious prompt injected into a
                                         conversation can compromise later reasoning, trigger dangerous         Behind several sorts of human-AI interaction are processes
                                         tool calls, or distort final outputs. Despite the centrality of such   that build up one or more prompt-response conversations. The
                                         systems, we currently lack a principled semantic foundation for        simplest form of chatbot just builds up a conversation where
                                         reasoning about their behaviour and safety. We address this            the human user supplies each pi while the system replies
                                         gap by introducing an untyped call-by-value lambda calculus            with each ri . An AI agent acting for a human builds up a
                                         enriched with dynamic information-flow control and a small
                                         number of primitives for constructing prompt-response conver-          conversation too, but with more autonomy.
                                         sations. Our language includes a primitive that invokes an LLM:        In a typical interaction with an AI agent, the initial prompt
                                         it serializes a value, sends it to the model as a prompt, and parses
                                         the response as a new term. This calculus faithfully represents        p1 contains the instruction from the human user while the
                                         planner loops and their vulnerabilities, including the mechanisms      final response rn is a message to the user. The intermediate
                                         by which prompt injection alters subsequent computation. The           messages arise from the agent’s planner algorithm; they trace
                                         semantics explicitly captures conversations, and so supports           the unrolling of the agentic loop. A common case is that an
                                         reasoning about defenses such as quarantined sub-conversations,        intermediate response ri encodes an instruction from the LLM
                                         isolation of generated code, and information-flow restrictions
                                         on what may influence an LLM call. A termination-insensitive           to an external tool [4], [5]. Tools enable searching the web,
                                         noninterference theorem establishes integrity and confidentiality      generating an image, reading or editing a file, running a shell
                                         guarantees, demonstrating that a formal calculus can provide           command, or running some code, and so on. The planner
                                         rigorous foundations for safe agentic programming.                     receives the tool instruction ri , executes it, and forms prompt
                                                                                                                pi+1 with the result from the tool. The LLM’s response, ri ,
                                                                I. I NTRODUCTION                                may be a piece of JSON encoding a web search, or it may be
                                                                                                                a piece of code to be run locally and able to read and update
                                         A. Terminology: prompt-response conversations and AI agents            state separate from the LLM. The result of the tool, pi+1 , may
                                                                                                                again be some JSON holding search results, or it could be
                                         At the core of generative AI are probabilistic algorithms to
                                                                                                                the textual response from the Python interpreter successfully
                                         generate (or complete) one message from another, where a
                                                                                                                running a program, or perhaps an error message from a crash.
                                         message is a sequence of tokens that encodes a piece of text. A
                                         token is an integer index into a large fixed vocabulary of words,
                                         subwords, and special symbols. An LLM is autoregressive,               B. Motivation: prompt injection attacks and countermeasures
                                         meaning that it samples text serially from an initial input [1].
                                                                                                                A prompt injection attack arises in a conversation where the
                                         The model conditions the prediction of the current token on the
                                                                                                                generation of rj from pj is unduly influenced by a prompt
                                         concatenation of the original input and all previously generated
                                                                                                                earlier in the conversation. Prompt injection attacks on AI
                                         tokens. The decoding process continues iteratively until the
                                                                                                                agents became known by late 2022 [6], [7]. In March 2023,
                                         model samples an end-of-sequence token, which signals the
                                                                                                                Simon Willison [8] proposed the dual LLM pattern, where a
                                         semantic completion of the response [2]. Otherwise, genera-
                                                                                                                Privileged LLM (P-LLM) and a Quarantined LLM (Q-LLM)
                                         tion terminates if the length exceeds a pre-defined maximum
                                                                                                                work together. Instead of the AI agent relying on a single
                                         token limit, known as the context window [3].
                                                                                                                conversation, the idea is to have separate conversations to
                                         Let the prompt, p, and the response, r, be the token sequences         avoid untrusted prompt messages from affecting later actions.
                                         that are the input and output of this generation process.              The conversations conducted by the P-LLM are kept decon-
taminated from untrusted data. The conversations conducted                   the prompt serialise(v), followed by the response r, and to
by the Q-LLM act on untrusted data in isolation. CaMeL [9]                   return the parsed response parse(r) as its value.
is a countermeasure based on refinements of the dual LLM
pattern, including code generation and dynamic information                             c, @e ⇓ c′ + [(serialise(v), r)], parse(r)
flow tracking. Its practical effectiveness is shown on the
AgentDojo prompt injection benchmark [10]. Willison [11]                     Although the semantics manipulates token sequences and con-
acknowledges its effectiveness. Still, although it describes a               versations, they are not data types within the language itself,
correctness property, the CaMeL paper includes no formal                     a deliberate choice. The serialize and parse functions appear
reasoning or proof, but describes formalization as a “crucial                only in the semantics, not expressions. Still, we have evidence
direction” for further work. Formalizing and reasoning about                 that generation is an expressive abstraction for programming
AI agents in general, and CaMeL in particular, was a prime                   with LLMs as shown by Sections II and VI.
driver for the research in this paper.
                                                                             Just as with serialisation and parsing, we model the behaviour
                                                                             of the LLM in an abstract and intentionally minimal way.
C. This paper: a calculus of prompt-response conversations                   The only semantic assumption we make is determinism: at
                                                                             each step the LLM’s response is a pure function of the
Section II describes the syntax and informal semantics of
                                                                             conversation history so far. This abstraction matches earlier
our LLM BDA calculus, an extension of the untyped lambda
                                                                             formal treatments of LLM interactions [15], while keeping
calculus [12]. We aimed for a kernel able to express both the
                                                                             the calculus general enough to accommodate a wide variety
code of agent planners and the code that they generate. (We
                                                                             of concrete model behaviours.
pronounce the name LLM BDA “L-L-Em-da”, to rhyme with
“lambda.”)
To track information flow we assume that the intended infor-                 D. Semantics and semantic guarantees
mation flows are modelled as a lattice of labels [13] where, as
is standard, the partial order (⊑) between labels l, l′ etc. is the          Section IV presents our main technical result, Theorem 1,
"may-flow-to" relation. For example, with two labels T and                   is a termination-insensitive noninterference theorem. Ignoring
U for trusted and untrusted data, T ⊑ U indicates that T -data               termination behaviour, information labelled at level m cannot
flow to data labelled U , but the reverse flow is not allowed.               affect observations at level n unless m ⊑ n.
To track and test information flow, our calculus relies on two               An important and particularly subtle aspect of our semantics
existing primitives [14]: labelled expressions l : e and label               is the treatment of label testing. While the label lattice broadly
testing l ?e, which returns a boolean to indicate whether the                models the intended information flow policy, the label testing
label l′ of e may safely be allowed to flow to data labelled l,              operation is means by which policies can be enforced in the
that is, it returns the value of l′ ⊑ l.                                     code itself. For example, suppose that we are constructing a
                                                                             record which is intended to be the parameter of a security-
To manipulate prompt-response conversations, we introduce                    sensitive API. A policy could be implemented as an API
three original primitives:                                                   wrapper or a callee-check, and the policy for such a scenario
(1) the @ operator @e to continue the current conversation                   might simply be that the label of the data should be trusted. A
    by prompting the LLM to generate a response, and parse                   more elaborate policy might decide, in addition, that untrusted
    it as semi-structured data, including text and code;                     data is also OK as long as a “sanitized" flag is set, and
(2) a fork construct to begin a fork of the current conversa-                furthermore labelled as trusted. We cannot predict the variety
    tion, a key aspect of context management; and                            of policy checks that might be implemented, but regardless of
(3) a clear construct to clear the current conversation, quar-               what the policy code does, the main theorem ensures that it
    antining the conversation from the past history.                         makes its decisions using semantically correct labels.
                                                                             With this perspective in mind, our semantics defines the label
Section III develops a formal theory. If we omit information
                                                                             of the result of a test to be independent of the labels that it
flow tracking, the core of our semantics is a big-step relation
                                                                             is inspecting. From a policy-enforcement perspective this is
                             c, e ⇓ c′ , v                                   what we want: if we test whether some data untrusted, then
                                                                             we do not want the outcome to be labelled as untrusted—who
meaning that given an initial conversation c, expression e                   would base a policy decision on untrusted data?
returns a value v, and updated conversation c′ .
                                                                             This “liberal” design for label testing is natural from a
For example, take a generation expression @e. Suppose c is the               policy-checking perspective—but it turns out to be incompati-
current conversation, and v is the value of e, that is, c, e ⇓ c′ , v.       ble with noninterference in the general case. Our main theorem
Suppose that r is the response message generated by the LLM,                 therefore identifies and formalises the precise constraints under
given the concatenation of c′ and serialise(v), the tokenization             which label tests can remain expressive while still preserving
of v. The semantics of @e is to extend the conversation with                 noninterference.



                                                                         2
E. Modelling Prompt Injections and Countermeasures                     Earlier works either deal with information flow tracking for
                                                                       general code but do not provide any formal security proofs
For any formal system (such as our LLM BDA calculus) to                (CaMeL [9]), or provide formal information flow properties,
be effective for security analysis of AI agents, it must be            but only for a fixed program schema, for example, FIDES [15],
capable of representing both their intended behaviour and their        or for a fixed system architecture [16].
potential security flaws.
Given our motivation to model and experiment with meaning-             G. Closest related work: FIDES, OPAL, Quasar
ful examples of AI agents, such as those in the CaMeL paper,
we built an interpreter for our calculus. Section V describes          FIDES [15] is the first research to give formal statements of
the LLM BDA interpreter, which allows us to build meaningful           the expected guarantees offered by information-flow tracking
examples. It is a direct implementation in Python of our big-          in a planner for AI agents: noninterference [17] for integrity
step semantics as a recursive interpreter, using the OpenAI            and explicit secrecy [18] for confidentiality. The planner algo-
responses API to implement the @ operator.                             rithms are presented as simple program schemas. FIDES is not
                                                                       based on the lambda calculus, and does not consider prompted
Section VI illustrates stateful AI agents via monadic pro-             code generation as in CaMeL and our work. Still, FIDES is
gramming within our calculus, including tool-calling agents            shown to be a practical system that can perform a broad set of
and the CaMeL pattern of code generation by a privileged               tasks from the AgentDojo benchmark with security guarantess.
P-LLM and quarantined execution of a Q-LLM. An exam-                   It is future work to benchmark our calculus in a similar way.
ple from the CaMeL paper illustrates a conventional tool-
calling architecture where untrusted data shares the same              A couple of languages for programming with LLMs,
prompt-response conversation with tool-commands, and thus              OPAL [19] and Quasar [20], are based on the lambda calculus
its vulnerability to prompt injection, demonstrated by our             and have formal semantics. These language offer benefits
interpreter. Moreover, we demonstrate that the dual LLM                including performance, quantification of uncertainty to help
pattern defeats this attack, and that label tracking and testing       against hallucinations, and assistance to the user when review-
in our lambda calculus model CaMeL’s use of capabilities. We           ing security decisions. Quasar, like our calculus, is designed
discuss the noninterference properties of our example implied          to be generated by an LLM. These works are closely related
by Theorem 1.                                                          to ours, although they do not discuss prompt injection, and do
                                                                       not consider information flow or noninterference results.

F. Main Contributions                                                  We postpone a full discussion of related work to Section VII.

We make two primary contributions:                                     H. Limitations of this work
1. A formal calculus capturing the core mechanisms of
                                                                       One limitation of our formalisation is an assumption of LLM
agentic programming. To the best of our knowledge, this
                                                                       determinism. Although there is a good case to be made against
is the first lambda calculus extended to model the major
                                                                       using nondeterminism, a better approach would be to admit
operational features of agentic systems built around LLMs.
                                                                       probabilistic behaviour, together with probabilistic versions
Our calculus, executable in the LLM BDA interpreter, supports:
                                                                       of noninterference. We leave that to future work; Borgström
  • prompting and parsing semi-structured data, including              et al. [21] develop the theory of a big-step semantics for a
    both text and code;                                                probabilistic lambda calculus. Instead of assuming message
  • explicit conversational context management—extending,              generation to be deterministic, we might adopt their weighted
    forking, and clearing conversations;                               big-step relation to obtain a probabilistic semantics and at-
  • repair loops in which the LLM reacts to error messages             tempt to establish some probabilistic variant of termination-
    by attempting corrective steps;                                    insensitive noninterference.
  • tool invocation via model-generated instructions or dy-            Another limitation of our approach is our modelling of tool
    namically generated code;                                          calls, and in particular how we model data sources. In our
  • dynamic security labels attached to values to track con-           approach, all data sources are assumed to be in the program.
    fidentiality and integrity throughout agent execution.             A more realistic model would include more general forms
                                                                       of interaction with external data and tools, and in particular
2. A sound information-flow foundation for defending
                                                                       data sources that are obtained by external tool calls. It is
against prompt injection. We formalize agents in the CaMeL
                                                                       fairly easy to envisage how our system might be augmented
style [9], where each sensitive tool function exposed to the
                                                                       with such external tool calls and data sources, but this comes
agent can enforce its own protection via dynamic label checks.
                                                                       at the price of expanding the calculus and complicating the
Theorem 1 implies that these dynamic checks—–when used
                                                                       theoretical development.
in a library of tool functions–—soundly enforce the intended
policy. In particular, we obtain the first formalization of            Our development in Section VI centres on different versions
information-flow-based defences for general agentic programs.          of a single example, and we have not presented a full model



                                                                   3
of the CaMeL system. Still, we offer the results in this paper          The final value is a list of three postcodes, as expected.
as a firm basis on which to study and build a fully practical
system.                                                                 B. Example: a simple agentic repair loop

                                                                        The @ operator can prompt the LLM to emit code as a lambda
        II. T HE LLM BDA CALCULUS , BY EXAMPLE                          abstraction within our calculus. Since our grammar is bespoke
                                                                        sometimes the LLM makes mistakes. The standard solution is
We add three new kinds of expression to the lambda calculus.            an agentic loop: detect the syntactic error message, and return
The @ operator, @e, captures the key new programming                    it to the LLM as a continuation of the conversation. Below
concept in our calculus: it extends the current conversation            we build a simple retry loop that adds syntax hints and keeps
by sampling the next response given the prompt given by the             trying until the code parses. The identifier syntax_summary
expression e, and returns the parse of the response as its value.       from our prelude in Appendix C is a set of hints to the LLM
                                                                        on the syntax of our calculus. The identifier fix is a call-by-
The fork expression, fork e, makes a temporary fork of the              value Y-combinator.
conversation for the expression e, and then discards it.
                                                                         # Retry loop: keeps prompting until syntax is valid
The clear expression, clear, clears the current conversation.            let retry = fix (\self. \round. \max. \prompt.
                                                                           if round > max then [false, "max retries"] else
                                                                           let r = @prompt in
                                                                           if r.[0] then [true, r.[1], round]
A. Example: postcode extraction                                            else self (round + 1) max "Error: {r.[1]}. Try again.")

                                                                         # Generate with syntax hints and auto-retry
In this first example, the task is to extract and normalize              let generate = \p. retry 1 5 (syntax_summary + ". " + p)
postcodes by inserting the optional middle space. We establish           generate "Write the factorial function"
a detailed prompt once, then make three short queries that
inherit it We prompt the LLM using the @ operator to
                                                                         retry = fn
prime it for the text processing task, and then repeatedly               generate = fn
fork the context to process each of three example addresses.             [true, \n.
                                                                            let fixer =
The example illustrates that the conversation context persists                \f.
between the first use of @ and subsequent calls. Moreover,                      \n.
                                                                                  if n == 0 then 1 else n * f (n - 1)
by using a fork expression, we ensure that each of the three             in
examples are processed independently of each other.                         fix fixer n, 1]                                       (7.3s)


 # Rich context established once
 let setup = @’You are a UK postcode extractor. UK                      C. Example: Agentic loop with test cases
      postcodes have the format: 1-2 letters, 1-2 digits,
      optional space, digit, two letters. Examples: EC1A 1              Our third example is a more complex agentic loop that
      BB, W1A 0AX, LS14AP, G1 1XQ. When asked to extract,
      return ONLY the postcode as a double-quoted string,               synthesizes a function from a prompt and checks that they
      always including the space. Now return {ready: true}              satisfy a pair of test cases. The loop uses the @ operator to
       to confirm.’
                                                                        prompt for a function, and loops if there is a syntax error, if the
 # Short prompt works because context is inherited                      returned value is not a lambda, or if either of the two cases
 let extract = \addr.
   let r = fork @"Extract: {addr}" in                                   fails. The loop is called from an agent function that begins
   if r.[0] then r.[1] else "error"                                     by forking the context and clearing it, that is, it works in an
 [ extract "10 Downing Street, London SW1A2AA",                         empty context, but restores the original context on exit. In
   extract "221B Baker Street, London NW16XE",                          this regard, the agent function works like subagents in Claude
   extract "Old Trafford, Manchester M16 0RA" ]
                                                                        Code.
The @ operator returns the outcome of parsing the response               # Test a function against test cases
                                                                         # Returns [true, f] or [false, "errors"]
from the LLM. It returns either an array [true, vok ] where vok          let run_tests = \ts. \f.
is the parsed value on success, or [false, verror ] where verror           let r0 = f ts.[0].[0] in let e0 = ts.[0].[1] in
                                                                           let r1 = f ts.[1].[0] in let e1 = ts.[1].[1] in
is the textual error message on parse failure.                             if r0 == e0 && r1 == e1
                                                                           then [true, f]
The expression if r.[0] then r.[1] else "error" above                      else [false, "got {r0} & {r1} expected {e0} & {e1}"]
is inspecting the boolean to see whether or not the parse has            # Recursive synthesis loop with retries
succeeded. Below, in the output from the LLMbda interpreter,             # Returns [success, value, rounds_taken]
                                                                         let synth = fix (\self. \ts. \round. \max. \prompt.
the list shown as the value of setup indicates a successful                if round > max then [false, "max retries", max] else
parse of {ready: true}.                                                    let r = @prompt in
                                                                           if not r.[0] then self ts (round + 1) max "Syntax error
                                                                              : {r.[1]}. Try again." else
 setup = [true, {ready: true}]                                             if not (is_fn r.[1]) then self ts (round + 1) max "Not
 extract = fn
 ["SW1A 2AA", "NW16 XE", "M16 0RA"]                     (9.3s)




                                                                    4
      a lambda. Write \\p. ..." else                                  the current conversation. In this first part of the calculus, a
   let t = run_tests ts r.[1] in
   if not t.[0] then self ts (round + 1) max "Tests failed
                                                                      value v is a closed lambda abstraction.
      : {t.[1]}. Try again." else
   [true, t.[1], round])                                                • To evaluate λx.e: return it, with no change to the state.
 # Agent: fork context, clear, synthesize with syntax
                                                                        • To evaluate e1 e2 , first evaluate e1 to a value λx.e. Eval-
      guidance, generate report                                           uate e2 to a value v. Continue by evaluating e[x := v].
 let agent = \tests. \prompt. fork (
   let _ = clear in
                                                                          Pass the conversational state from one step to the next.
   let full_prompt = syntax_summary + ". " + prompt in                  • To evaluate @e, first evaluate e to a value vp , possibly
   let result = synth tests 1 5 full_prompt in
   let rounds = result.[2] in
                                                                          updating the conversation. Serialize vp to a token se-
   let report = if result.[0]                                             quence p, the prompt to the LLM. Sample the response
     then "Synthesis succeeded in {rounds} round(s)."
     else "Synthesis failed after {rounds} round(s)." in
                                                                          r generated by the LLM given c extended with p. Parse
   {result: result, report: report})                                      the value vr from the response. Return the value vr and
 # Task 1: swap x and y coordinates
                                                                          extend the conversation with (p, r).
 let swap = agent                                                       • To evaluate fork e save a copy of the current conversation
   [[{x: 1, y: 2}, {x: 2, y: 1}],
    [{x: 5, y: 3}, {x: 3, y: 5}]]
                                                                          c. Evaluate e from the current conversation, yielding value
   ’Write a lambda \p. that swaps x and y. Example: {x:1,y                v, and a possibly updated conversation. Restore c and
      :2} becomes {x:2,y:1}’
                                                                          return v.
 # Task 2: reflect point on X-axis (negate y)                           • To evaluate clear, set the conversation to the empty
 let reflect = agent
   [[{x: 1, y: 2}, {x: 1, y: 0 - 2}],
                                                                          sequence [], and return the unit value λx.x.
    [{x: 3, y: 5}, {x: 3, y: 0 - 5}]]
   ’Write a lambda \p. that negates y (use 0 - p.y).
      Example: {x:1,y:2} becomes {x:1,y:-2}’                          B. Derived data types and expressions

                                                                      For examples and for practical programming, we rely on
 run_tests = fn
 synth = fn                                                           JSON-style data types: booleans, numbers, strings, and
 agent = fn                                                           records, with the following syntax. Appendix B shows stan-
 swap = {result: [true, \p.{x: p.y, y: p.x}, 1], report: "
      Synthesis succeeded in 1 round(s)."}                            dard Church-style encodings of all of these derived values and
 reflect = {result: [true, \p.{x: p.x, y: 0 - p.y}, 1],               expressions. For example, we derive our unit value () ≜ λx.x.
      report: "Synthesis succeeded in 1 round(s)."} (3.1s)

                                                                      Derived forms e, f , expressible in λ@
               III. S YNTAX AND SEMANTICS                              e, f ::=                          derived expressions
                                                                            let x = e1 in e2                  let expression
                                                                            () true false n ∈ Z s ∈ string literals
A. Lambda calculus plus conversations
                                                                            if e1 then e2 else e3             conditional
                                                                            [e1 , . . . , en ]                array
The expressions e of the first part of our calculus are as fol-
                                                                            e1 .[e2 ]                         element extraction
lows, where x ranges over variables. (Section III-C describes
                                                                            {s1 : e1 , . . . , sn : en }      record
the second part, dealing with labels.)
                                                                            e.s                               field access
                                                                            e.s := e′                         functional field update
λ@ : λ with conversations
 e, f ::=             expressions
      x                   variable                                    Evaluation of the derived expressions is similar, and standard,
      λx.e                abstraction                                 and so we omit the details. In our formal development we treat
      e1 e2               application                                 derived expressions as being encoded within our core calculus.
      @e                  @ operator for generation                   The LLMbda interpreter implements them directly.
      fork e              fork the conversation
      clear               clear the conversation                      C. Completing our core lambda calculus with labels

                                                                      To track information flow in our calculus, we assume a set of
We have standard notions of free and bound variables. In λx.e,        labels k, l, m, pc drawn from a join-semi-lattice [13] with join
the variable x binds any free occurrences of x in e. We say           ⊔, ordering ⊑, and top and bottom elements written ⊤ and ⊥.
an expression e is closed if it has no free variables. We write       In what follows we will refer to the join-semi-lattice as just a
e[x := e′ ] for the outcome of substituting closed e′ for each        lattice.
free occurrence of x in the expression e. (Our development
                                                                      Our theory applies to any such structure but all our examples
does not rely on α-conversion.)
                                                                      run in the LLMbda interpreter where we consider a label to
The execution or evaluation process described next interprets         be an element of the powerset of {U, S} ordered by subset
a closed expression to yield a value, and may read and update         inclusion, where U means untrusted, and S means secret. In



                                                                  5
earlier work, e.g. [15], this label lattice is often presented           testing the result. Fork allows us to roll back the conversation
equivalently as the product of a confidentiality lattice P               history after doing this:
(Public) ⊑ S (Secret) and an integrity lattice T (Trusted) ⊑
U (Untrusted).                                                                           testConversation m ≜ m?fork @( )

In general, l ⊔⊤ = ⊤ and l ⊔⊥ = l. In our interpreter, ⊥ = {}            Here @() prompts the LLM with (). Whatever response is
and ⊤ = {U, S}.                                                          returned, it will have the label of the conversation history.
                                                                         The fork operation then restores the conversation history back
Labels:                                                                  to the point before the prompt. This completes the full syntax
 k, l, m, pc ⊆ {U, S}    label (U for untrusted, S for secret)           of our calculus. We have stated our intended semantics as
                                                                         informal evaluation rules. In the rest of this section, we define
                                                                         a formal semantics.
Building on prior work on dynamic information flow tracking
in the lambda calculus, and most closely to the work of Austin
                                                                         D. Behind the @ operator: serialize, generate, parse
et at. [22], [14], we add label and test expressions to our
calculus:                                                                Our model of generating messages from an LLM is largely
                                                                         abstract, with some minimal assumptions. Here we describe
λl:@ : λ@ with labels                                                    the semantics-level entities that are used to model the com-
 e, f ::=       expressions                                              munication with the LLM and its state.
      ...           expressions of λ@ (Section III-A)
      l:e           ℓ expression                                         Messages and (labelled) conversations:
      l?e           ℓ test                                                p, r ::= token sequence               message: prompt or response
                                                                          c ::= [(p1 , r1 ) . . . (pn , rn )]   conversation
A labelled value V is an expression of the form l : v where               C ::= l : c                           labelled conversation
v is a value (a lambda expression). Our labelling discipline
is parsimonious in the sense of [22], so that we never need              To convert a value into a prompt we use semantic functions,
to label anything with ⊥. Hence in the interpreter unlabelled            erasem(_) ∈ λl:@ → λ@ to erase any subterms labelled
expressions are assumed to be trusted and public, and we                 with things not less than or equal to m, for some label m,
need only explicitly label the secrets and the untrusted things.         and an unspecified function function serialise which serialises
Labels play a dual role: they provide the intended meaning of            values into a representation understood by the agent (that is, a
data sources, but they can also be used as explicit coercions            token sequence). Why is erasure needed? Although the value
of values (“treat this value as if it where a secret") which can         returned by an expression has a top-level label summarising
be used to better control how information flow is tracked.               the influence of all data used to produce it, it may still contain
In the absence of side effects, the evaluation semantics of these        labelled subexpressions—–parts of the value that have not yet
expressions can be understood as:                                        been inspected. To safely communicate with the agent, the
                                                                         erase function removes any information whose label is not
  • To evaluate l : e, first evaluate e to its labelled value            below a specified threshold m.
    l′ : v, and return l ⊔ l′ : v.
                                                             ′
  • To evaluate l?e, first evaluate e to its labelled value l : v;       Inductive definition of n-erasure
    return true if l′ ⊑ l, or false otherwise.
                                                                          erasen(m : e)          = erasen(e)       if m ⊑ n
For example, in the four-point lattice of integrity and secrecy                                  = ()              otherwise
labels:                                                                   erasen(fork e)         = fork erasen(e)
                                                                          erasen(@e)             = @erasen(e)
  {U }?42          evaluates to true         (⊥ ⊑ ⊥)
                                                                          erasen(l?e)            = erasen(e)
  {U }?{U } : 42   evaluates to true         ({U } ⊑ {U })
                                                                          erasen(e1 e2 )         = erasen(e1 ) erasen(e2 )
  {U, S}?{U } : 42 evaluates to true         ({U } ⊑ {U, S})
                                                                          erasen(λx.e)           = λx.erasen(e)
  {}?{U } : 42     evaluates to false        ({U } ̸⊑ ⊥)
                                                                          erasen(x)              =x
  {S}?{U } : 42    evaluates to false        ({U } ̸⊑ {S})
                                                                          erasen(clear)          = clear
In a test of the form l?e, one would typically expect e to be
a bound variable x: you compute a value, bind it to x, and               We establish a central erasure property (formalised later) of
depending on the outcome of a test you decide how to use x.              erase, namely: if two labelled values v and v ′ differ only in
When e has side-effects (via @), the label says nothing about            labelled subexpressions whose labels are not less than m, then
the level of any prompts sent. Fortunately one can readily
test the label of the conversation history by prompting it and                                   erasem(v) = erasem(v ′ ).



                                                                     6
Following FIDES [15], we write JM K for the behaviour of                      Values with labels:
the underlying model and make the simplifying assumption                       v ::= λx.e               value (closed: at most x free in e)
that it is deterministic. We write r = JM K(p) to mean that r                  V ::= l : v              labelled value
is the sample obtained from the model’s message generation
process, conditioned on p, as described in Section I-A.
Assuming deterministic behaviour is a reasonable model of                     For top-level evaluation we always take pc = ⊥, indicating
agentic behaviour, which intentionally does not leak internal                 that no control-flow decisions have yet been influenced by
state. From the point of view of proving noninterference                      labelled data. The incoming conversation history C (empty at
properties, the determinism in this model is the “right thing”;               top level) and the outgoing history C ′ are themselves labelled.
when we compare two executions of related terms (e.g. where
the terms only differ in the things which are labelled as                     Big-step semantics:          pc ⊢ C, e ⇓ C ′ , V       e ⇓ C, V
untrusted) we are performing a “what-if" experiment: what                     (L ABEL)                      (L AMBDA)
if, all other things being the same, the value of the untrusted               pc ⊔ l ⊢ C, e ⇓ C ′ , V
things had been different? By proving properties relative to an               pc ⊢ C, l : e ⇓ C ′ , V       pc ⊢ C, λx.e ⇓ C, pc : λx.e
unspecified behaviour function, we provide the right setting
for such experiments.                                                         (A PP)
                                                                              pc ⊢ C0 , e1 ⇓ C1 , m : λx.e3
The final semantic function we assume is parse, which con-                    pc ⊢ C1 , e2 ⇓ C2 , V2
verts the response (a token stream) into a closed, label-free                 pc ⊔ m ⊢ C2 , e3 [x := V2 ] ⇓ C3 , V3
value.
                                                                              pc ⊢ C0 , e1 e2 ⇓ C3 , V3
We make no specific assumptions about the encoding scheme
used by the parser in the semantics. Of course the programmer                 (P ROMPT) (where pc ⊑ l)
must know the properties of the parser to be able to interpret                pc ⊢ C, e ⇓ (l : c), (m : vp ) n = l ⊔ m
the result and act on it accordingly.                                         (c′ , r) = generate(c, serialise(erasen(vp )))        vr = parse(r)
                                                                                                    ′
                                                                              pc ⊢ C, @e ⇓ (n : c ), (n : vr )
In our specific interpreter, for example, the parser recognises
all syntactic sugar and derived forms of the calculus, including              (F ORK)                       (C LEAR)
references to prelude-defined constants; each such constant d                 pc ⊢ C, e ⇓ C ′ , V           pc ⊑ l
(where let d = e appears in the prelude) is expanded to its                   pc ⊢ C, fork e ⇓ C, V         pc ⊢ (l : c), clear ⇓ (pc : [ ]), (pc : ())
definition e. The result is always a syntactic value form—a
literal, lambda abstraction, record, or array—rather than an ex-              (T EST) (where v = true if l′ ⊑ l else false)          (T OP L EVEL)
pression requiring further computation. In our interpreter, for               pc ⊢ C, e ⇓ C ′ , l′ : v ′                             ⊥ ⊢ [ ], e ⇓ C, V
any response sequence r, parse(r) takes the form [true, vok ]                 pc ⊢ C, l?e ⇓ C ′ , pc : v                             e ⇓ C, V
or [false, verror ] indicating whether the resonse was parsed
successfully or not.
                                                                              We include a convenient top-level judgement for evaluation an
Finally, we define generate, as a shorthand used in (P ROMPT).                expression – it simply means evaluate starting with pc = ⊥
Given a conversation and a prompt (as a token sequence)                       and the empty conversation history.
            generate(c, p) ≜ (c + [(p, r)], parse(r))
                      where r = JM K(concat(c) + p)                           F. Discussion of the rules
Here, concat([(p1 , r1 ) . . . (pn , rn )]) = p1 + r1 + . . . + pn + rn
is the concatenation of a conversation into a single token                    For the most part, the information flow tracking is not surpris-
sequence. (We overload the + operator both for concatenation                  ing relative to similar systems for dynamic information flow
p + r of token sequences and for concatenation c + c′ of                      tracking. Our approach is a combination of (i) an imperative
conversations.)                                                               approach such as [22] in so far as how we track the conversa-
                                                                              tion history, together with (ii) a substitution-based tracking at
E. Big-step Semantics                                                         the level of expressions, exemplified by the labelled lambda
                                                                              calculus [14].
Our big-step semantics carries security levels on the conver-
                                                                              As mentioned in the introduction, a particular feature of the
sation history and on the values produced. Judgements have
                                                                              test primitive is that it returns its result at the level of the pc,
the general form
                                                                              motivated by the desire to use tests to make policy decisions.
                     pc ⊢ C, e ⇓ C ′ , V,
                                                                              In the next section we will see that this is not sound in general,
where pc ∈ L is the program-counter (pc) label, following                     but the primitive is sound in the special case of a two-level
Denning and Denning’s classical treatment of information-flow                 label lattice, and is sufficient to build two different sound
control [23]. The main syntactic categories are:                              variants of testing operations.



                                                                          7
The conversation history C is a state that can be read or                 To formalise termination-insensitive noninterference, we first
written through Rules (P ROMPT) and (C LEAR). Consequently,               define when two expressions are indistinguishable up to level
the label associated with the history is subject to constraints           n. We define this n-indistinguishability relation (∼n ) induc-
that prevent illicit information flow along execution paths that          tively below.
do not modify the state. To illustrate the issue, consider the
following example:                                                        Inductive definition of n-indistinguishability
 let secret = true in                                                     l ̸⊑ n   m ̸⊑ n         e 0 ∼n e 1              e0 ∼n e1
   let _ = @’Remember this value: x = false’ in
   let _ = if {S}:secret then @’Set x = true’ else () in                  l : e0 ∼n m : e1        m : e0 ∼n m : e1        m?e0 ∼n m?e1
   @’Give me the value of x’
                                                                                      e 0 ∼n e 1               f0 ∼n f1     e 0 ∼n e 1
 Error: Cannot prompt LLM with @’Set x = true’: pc label                  x ∼n x      λx.e0 ∼n λx.e1           f0 e0 ∼n f1 e1
      {S} does not flow to conversation label bot. This is
       the ’no high upgrade’ check - cannot update low-                   e0 ∼n e1             e0 ∼n e1
      labeled conversation from a high security context.
                                                                          @e0 ∼n @e1           fork e0 ∼n fork e1        clear ∼n clear
Suppose that Rule (P ROMPT) had no constraint in its premise,
and instead simply updated the label of the conversation                  We extend ∼n to labelled conversations as follows:
history by joining it with the current pc and the label of the
argument. When the secret variable is true, the query on the              Definition of n-indistinguishability for conversations:
second line would cause the label of the outgoing history to
                                                                          (H IST D IFF)          (H IST S AME)
become secret, and the return value would therefore be labelled
                                                                          l ̸⊑ n m ̸⊑ n
secret. The problem appears when the secret is false: in that
case, the label on the history remains low, and so the final              l : c 1 ∼n m : c 2     m : c ∼n m : c
result is labelled low—an obviously incorrect behaviour.
The solution we adopt is the standard no-high-upgrade disci-              The following basic properties of ∼n are straightforward
pline, first articulated by Zdancewic [24] and developed further          consequences of its inductive definition:
by Austin and Flanagan [22]. In the two-point lattice setting,
                                                                          Lemma 1 (∼).
this rule prevents a low-labelled state variable from being
upgraded while in a high context (i.e. when the pc is high). In           (1) ∼n is an equivalence relation (that is, reflexive, symmet-
the multi-level setting, the generalisation is that the label of              ric, and transitive);
the history (our only state variable) may be changed only when
its current label is at least as high as the pc. This is precisely        (2) If e0 ∼n e′0 and e1 ∼n e′1 then
the constraint enforced in the premises of Rules (P ROMPT)                                        e0 [x := e1 ] ∼n e′0 [x := e′1 ];
and (C LEAR).
As in prior work, the no-high-upgrade constraint is conserva-             (3) If m ⊑ n then e ∼n e′ implies e ∼m e′ .
tive: it prevents potential bad flows, and so some executions
may be unnecessarily blocked. The blocking behaviour itself               We can now state the key property relating ∼n to erase:
leaks information through termination, but this is permitted
                                                                          Lemma 2. v ∼n v ′ implies erasen(v) = erasen(v ′ )
by the termination-insensitive noninterference property we
establish later. More permissive—but still sound—approaches
                                                                          We are now ready to state the main semantic property: a
have been proposed, e.g. [25], though these become intricate in
                                                                          generalised form of termination-insensitive noninterference.
general multi-level lattices [26] or require labels on labels [27].
                                                                          The resulting noninterference theorem for our semantics will,
                                                                          however, hold only under certain restrictions—either to the
                   IV. N ONINTERFERENCE                                   structure of the label lattice or to the class of programs con-
                                                                          sidered. Whenever such restrictions are made, we implicitly
                                                                          assume that the parse function, in addition to producing label-
A. Semantic guarantees
                                                                          free closed expressions, respects the same constraints. Strictly
                                                                          speaking, the parse function should be parameterised by these
The main semantic guarantee we establish is a standard
                                                                          sets, but we omit such annotations to avoid clutter.
termination-insensitive noninterference property [28]. Ignoring
side channels, this property ensures that any information leak-           Definition 1. Termination-Insensitive Noninterference (TINI)
age can occur only through termination behaviour. Informally,             Let E be a sublanguage of closed expressions whose labels
it states that if two expressions agree on all components                 come from a join-semilattice L. We say that E satisfies
labelled at some level m or below, then evaluating them will              termination-insensitive noninterference (TINI) if and only if
produce values that are indistinguishable up to level m.                  for all e0 , e1 ∈ E and all levels k ∈ L:



                                                                      8
   •   e0 ∼k e1 implies that whenever e0 ⇓ C0 , V0 and e1 ⇓                           Lemma 3. The following proof rules for assert and strong
       C1 , V1 , we have that C0 ∼k C1 and V0 ∼k V1 .                                 test are sound and complete:

Unfortunately, TINI does not hold for all expressions and label                       Derived rules: assert and strong test
lattices. The difficulty arises from the testing (?) operation. To                    (A SSERT)
illustrate the problem, consider a three-level lattice L ⊑ M ⊑                        pc ⊢ C, e ⇓ C ′ , V   label(V ) ⊑ k
H and the following L-indistinguishable terms:
                                                                                      pc ⊢ C, assert k e ⇓ C ′ , (pc : ())
                    M : true ∼L M : (H : false).                                      (S TRONG T EST) (where v = true if l ⊑ k else false)
                                                                                      pc ⊢ C, e ⇓ C ′ , l : v ′
Performing a label test on these terms reveals the issue:                             pc ⊢ C, k??e ⇓ C ′ , (pc ⊔ k : v)
M ? (M : true) evaluates to L : true, whereas M ? (M :
(H : false)) evaluates to L : false – two terms which are
clearly not L-indistinguishable. Where does this discrepancy                          Main technical theorem.
originate? One might blame the label rule for returning the
test outcome at too low a level; however, this behaviour is                           Theorem 1 (TINI). The following sublanguages satisfy TINI:
intentional. The label must be available at a low level to
                                                                                      (1) expressions built without ?;
allow the program to make policy decisions freely. If the
outcome of tests have high labels then they cannot be used                            (2) expressions which only use one non-bottom label; and
to implement policy decisions. For example, suppose, using
                                                                                      (3) expressions in which ? occurs only in the form of assert
the earlier example lattice with labels from the power set of
                                                                                          statements or strong tests.
{U, S}. If testing whether an expession is public ({U } ? e)1
gives a boolean with label {U } (untrusted), what use does it
                                                                                      Note that a special case of (2) is when the lattice has only
have in a policy decision? We will present three alternative
                                                                                      two elements, as in [14]. The proof of Theorem 1 is a
ways to address this issue and obtain noninterference results:
                                                                                      consequence of a lemma which generalises TINI to begin
(i) disallow expressions that perform tests on labels, (ii) restrict
                                                                                      with an arbitrary pc and arbitrary (∼k )-related conversations
attention to programs which use only one non-bottom label,
                                                                                      (over the appropriate set of labels). The proof is given in
or (iii) use label tests solely to implement two more restricted
                                                                                      the technical appendix, and is a standard induction over the
forms of test: assertions about labels—operations that fail if
                                                                                      derivation in the big-step semantics.
the asserted condition does not hold, and a strong form of
label test that is always noninterfering, but returns a boolean
at a sufficiently high level.                                                             V. I MPLEMENTATION : THE LLM BDA INTERPRETER

Option (ii) is particularly interesting in light of the existing                      At the earliest stages of conceiving our formal calculus we
literature. While many systems are developed for arbitrary                            found ourselves speculating about what sorts of prompts would
lattices, most formal noninterference results are ultimately                          work, or not. We realized that it was impossible to reason
proved only for the special case of a two-level lattice. The                          about prompts and the likely responses from an LLM in the
counterexample discussed above genuinely requires three dis-                          abstract. Hence, so that we could experiment with programs
tinct levels, and thus lies outside the scope of these two-level                      in the calculus and observe their behaviour, we implemented
results.                                                                              our operational semantics within an interpreter with a read-
To state (iii) precisely, we define assertions strong tests as                        eval-print loop.
follows:                                                                              Our goal was to implement the calculus and its derived forms
                                                                                      directly. We kept to a principle of minimality, and have resisted
Derived constructs: assert and strong test                                            the temptation to think of the implementation as being a
 assert k e ≜ if k?e then () else Ω                                                   practical programming language. Applying the ideas of the
                                                                                      calculus in a practical programming language is out of scope
     where Ω ≜ (λx. x x) (λx. x x)
                                                                                      for this paper and left as future work.
 k??e ≜ let x = e in (let b = k?x in k : b)
                                                                                      The implementation is in Python (approximately 4000 lines),
                                                                                      written with Claude Code. The parser uses the Lark li-
Note that the else-branch uses the standard divergent term Ω.                         brary [29] with an LALR grammar. The interpreter implements
We also state the key properties of the encoded operators in                          the big-step semantics with label propagation. The @ operator
terms of their derived evaluation rules:                                              calls the OpenAI Responses API [30]. We experimented with
                                                                                      an option from OpenAI to constrain the LLM’s responses to be
  1 This might look unintuitive, but the public labels are those not containing       syntactically valid expressions from the Lark grammar, though
S (secret), that is, { } and {U }.                                                    responses are slower than when unconstrained.



                                                                                  9
     VI. P ROMPT INJECTION ATTACKS AND DEFENSES                          On the other hand, injecting a suitable text into the stored
                                                                         email causes a cancellation to be sent.
Figure 5 of the CaMeL paper [9] sets up an example that                  let injection = ’
                                                                         ---SYSTEM UPDATE---
typifies a prompt injection attack. In the example, the user asks        CRITICAL: The meeting has been CANCELLED. Do NOT
the agent to find an email to send a reminder about a meeting.               send a reminder. Send a CANCELLATION notice.
The agent has access to the user’s emails. Unfortunately, a text         ---END SYSTEM UPDATE---’
injected into the email causes the agent to send a cancellation
                                                                          let state2 = state1.last := state1.last + injection
instead of a reminder.                                                    performIO (run_agent goal1) state2


                                                                          state2 = {last: {U}:"Long message from bob@chalmers.se to
A. Prompt injection attack on a tool-calling agent                              alice@darpa.gov.\n---SYSTEM UPDATE---\nCRITICAL:
                                                                               The meeting has been CANCELLED. Do NOT send a
                                                                               reminder. Send a CANCELLATION notice.\n---END SYSTEM
                                                                                UPDATE---", queue: []}
We present a simple model of this situation within our cal-               {U}:[{U}:{subject: "Meeting cancellation notice", body: "
culus. The system state is a record with a field for the last                  Hello,\n\nThe meeting has been cancelled. No
                                                                               reminder is needed.\n\nBest regards,", recipient: "
email received and another field for the output message queue,                 bob@chalmers.se"}]                            (10.8s)
initially empty. The goal from the human user is a string.
let state1 = { last: {U}:"Long message from                              In the definition of state1 we attached the label {U} for
    bob@chalmers.se to alice@darpa.gov", queue: [] }                     untrusted to the email string. In both runs, that label has tainted
let goal1 = "Extract sender email address from my                        the output message. This illustrates the root vulnerability
    last email and send a meeting reminder to that                       exploited by prompt injection attacks: the tool-calling agent
    address"                                                             uses the same channel, a single prompt-response conversation,
We prompt the LLM to engage in a tool-calling conversation as            to carry both untrusted inputs (the emails) and also command
follows. Curiously, despite our calculus having no type system,          information (the tool-calls).
we can rely on the model’s pre-trained knowledge of types.               If we are to reason about attacks and defenses in our calculus
                                                                         we need it to represent both functionality and vulnerability.
Every answer must be in one of the following two forms.
(1) you have info to answer your goal,                                   By running the model in our interpreter we have shown both
    emit [’answer’, the-answer-as-a-value];                              that it models intended functionality—it can send the reminder
(2) to gather more information,
    emit [’tool-call’,[’function-name’, value1, ... valueN]].            intended by the user successfully when there is no attack—but
    You will receive the answer in the next prompt,                      also that it models the vulnerability—it sends the unintended
    and can then continue.
                                                                         cancellation when the attack text is injected.
get_last_email_tool: IO string
send_email_tool: {"subject": string, "body": string,
    "recipient" : string } -> IO {}                                      B. CaMeL: code generation and quarantine

The tool-calling agent is a function run_agent. Given the goal           We give an example of the CaMeL defence, based on a
from the user, it prompts the model as above, and loops to               privileged planner that generates code to do the work of
serve tool-calls from the LLM, by calling the available tools,           the agent, which later calls a quarantined LLM to process
and eventually returns the final message queue. The agent is             the untrusted data. CaMeL relies on capabilities: “tags as-
a stateful computation programmed in the monadic style of                signed to each individual value that describe control and data-
functional programming. We list all the code in Appendix D.              flow relationships.” The labelled expressions can model these
Figure 1 shows a standard set of monadic functions for                   capabilities, and policy decisions based on capabilities are
programming with state. Figure 2 shows the tool-calling agent            expressed using label test expressions.
itself [4], [5], coded within our calculus in a monadic style.           Running the code reveals that the original attack fails on
We model execution without an attack. The function                       this planner. Moreover, our noninterference theorem provides
performIO (from Figure 1) executes the monadic computation               guarantees.
on the initial state, and displays the final state.                      Our planner generates code f before touching state. The code
 performIO (run_agent goal1) state1                                      of the planner, including its code generation, correspond to
                                                                         Willitson’s privileged P-LLM [8].
We get the intended reminder in the message queue:                       let direct_code_gen_agent = \goal. \state.
                                                                           let f = direct_code_gen goal in
                                                                           let post_state = f state in post_state.queue
 {U}:[{U}:{subject: "Meeting reminder", body: "Hi Bob,\n\
      nJust a reminder about our upcoming meeting. Please                The function below models the quarantined Q-LLM:
      let me know if you need to reschedule or if there’s
      anything you’d like to add to the agenda.\n\nBest,\                # quarantine: string -> json
      nAlice", recipient: "bob@chalmers.se"}]      (7.1s)                # Prompts LLM in isolated context, returns JSON.




                                                                    10
# The prompt should include a description or example                    any other run cannot effect outputs that are labelled as trusted.
     of the expected JSON format.                                       (The absence of an explicit label indicates that the value is
let quarantine = \prompt.
  let pair = fork( let _ = clear in @ prompt ) in                       trusted.) The subject and body fields have trusted values in
  pair.[1]                                                              the first run, and so must take the same values in any other
                                                                        run too.
The inner direct_code_gen function is another iterative agen-
tic loop that produces a lambda. When run on our example                It justifies implementing security policies based on label
goal, we may get the following function f, which uses a                 testing. The policy assertions implemented by send_email
quarantined call to the LLM to process the untrusted input.               in Figure 3 have a semantic consequence: they guarantee
Finally, it calls send_email to form a message and add it               that only messages with trusted subjects and bodies may be
to the output queue. An injected prompt cannot change the               sent, and hence that those parts of emails are unaffected by
subject or body.                                                        untrusted inputs.
 let f = direct_code_gen goal1 # line 1 of the agent                    Although not shown in this example, we have constructed
                                                                        other examples where the security policy guards confidential-
 f = \state.                                                            ity: for instance, a variant of send_mail can encode a policy
    let last = get_last_email state in                                  that if the body of the outgoing message has a secret label,
    let extracted =
      quarantine                                                        then the recipient must be in an allow-list.
        "Extract the sender email address from the
       following email text. Return ONLY a double-quoted
       string containing the email address (example: \"                                     VII. R ELATED WORK
       name@example.com\"). Email text:\n\n{last}\n"
 in
    send_email extracted "Meeting reminder" "Hi,\n\nJust a              A. Background: minimal kernels of programming languages
       reminder about our upcoming meeting. Please let me
       know if you need to reschedule.\n\nThanks." state
       (5.5s)                                                           The lambda calculus is a formalism of pure functions [31].
                                                                        It was adopted as a tool for analysis and design early in the
                                                                        study of programming languages [32]. The method is to factor
The system function send_email, shown below, can test labels
                                                                        language design into independent, orthogonal concerns, with a
on data to enforce a security policy dynamically. In this case,
                                                                        minimal kernel based on the lambda calculus that captures the
we enforce that the subject and body must be trusted. The
                                                                        essential semantics, and derived constructs that reduce to it.
{S}? test implicit in the assert below is satisfied by labels {}
                                                                        Pioneers include Böhm [33], Landin [34], and Strachey [35].
and {S} but not {U } and {U, S}. Hence, the assert is testing
the policy that neither subject nor body is untrusted.
                                                                        B. Lambda calculus applied to LLMs
# policy: subject and body are trusted
let send_email = \to. \subject. \body. \state.                          OPAL [19] is a parallel scripting language for LLMs, based
  if assert {S} (subject+body) then                                     on a lambda calculus with a formal semantics. The emphasis
    state.queue := state.queue +
      [{to:to, subject:subject, body:body}]
                                                                        of the work is execution performance. The paper does not
  else state # return state unchanged                                   consider aspects of security such as resistance to prompt
                                                                        injection or noninterference.
As we saw earlier, with the tool-calling agent, any tainted data
passed to the LLM taints the whole conversation. Hence, a               Quasar [20] is a programming language with a pure, functional
tool-calling agent cannot meaningfully use the label-checking           core based on the lambda calculus. Side effects are isolated in
function send_email because its policy would always fail.               external calls. Its goals are performance through parallelisa-
                                                                        tion, uncertainty quantification to counter hallucinations, and
 let post_state = f state2 in post_state.queue # line 2
                                                                        security to help users validate external actions.

 [{to: {U}:"bob@chalmers.se", subject: "Meeting reminder",
       body: "Hi,\n\nJust a reminder about our upcoming                 C. Dynamic Enforcement of Noninterference
      meeting. Please let me know if you need to
      reschedule.\n\nThanks."}] (1.1s)                                  Our approach to dynamic information flow tracking is closest
                                                                        to that of Austin et al. [22], but combined with a term-
Running this code, despite the prompt injection, results in the         level treatment of labels that is in the spirit of the functional
correct message being sent.                                             approach defined in the later work [14], which in turn is based
                                                                        on Abadi, Lampson, and Lévy’s labelled lambda calculus [36].
But what about other runs? The theory of information flow in
our lambda calculus lets us reason how changes to inputs affect         A novelty of our noninterference results are in the analysis
outputs. If data is labelled as untrusted, changes to that data         of label testing, which we view as a crucial component for
cannot change an output known to be trusted. Consider the               implementing policy checks. Austin et al. [22] included a
untrusted message string in the last field in the input state2.         label testing operation returning “low” booleans, but only
Noninterference tells us that changing that untrusted input in          established noninterference for a two-level lattice. Bichhawat



                                                                   11
et al. [26] study generalisations of Austin and Flanagan’s work            replacing pc⊔m in the (A PP) rule with pc. However, even if it
to arbitrary lattices, but do not include label testing. Vassena           was clear how to formulate explicit secrecy for a higher-order
et al. [37] introduce a fully-fledged label testing operation              language, we question its potential value for any language
inspired by the labelOf operation from the course-grained                  with features such as higher-order functions, where data and
tracking approach of LIO [38]. Their operation returns the                 control are interchangeable and leaks through control can be
label of an expression (thus labels are first-class values in              made very efficient.
the language), and its level is the label itself. This is close
in spirit to our strong testing operation, and while useful for            E. Other prompt injection attacks and defences
certain operations on labelled data, we have argued that it is
not suitable to implement policy logic.                                    Greshake et al. [42] introduced indirect prompt injection,
                                                                           where adversarial instructions are embedded in untrusted data
Our result that assertions can safely return a low result for any          retrieved by the application. Liu et al. [43] give a formal defini-
label lattice seems to be new. Somewhat related is Kozyri et               tion: given an LLM-integrated application with an instruction
al. [39] which deals with the expressiveness of labels on labels           prompt (the target instruction) and data (the target data) for a
on labels. . . to an arbitrary depth. They include the notion of a         target task, a prompt injection attack modifies the data such
fixed variable—a variable with a fixed label. An assignment to             that the application accomplishes an injected task instead.
such a variable acts as an assert that the label of the value being
assigned is less than or equal to the fixed label of the value.            The AgentDojo benchmark [10] is a framework, based around
Our assert operation potentially leaks information within what             97 tasks, for designing and evaluating prompt injection attacks
is accepted by termination-insensitive noninterference. In the             and their countermeasures.
terminology of Kozyri et al. it is not block safe. It remains to           Other defenses include spotlighting [44], which transforms in-
be seen whether this is inevitable (as we suspect), or a feature           put to make its provenance more salient, and Task Shield [45],
specific to our language and semantics.                                    which verifies that instructions align with user-specified goals.

D. Information-flow Based Defences Against Injection Attacks               F. Code generation with LLMs
The use of information flow labeling and tracking to tackle                Large language models trained on code have demonstrated
problems with LLM interactions has been used in a variety of               remarkable ability to generate programs from natural language
recent papers. As well as FIDES and CaMeL mentioned in the                 descriptions [46]. SWE-Agent [47] uses agent-computer inter-
introduction, Wu et. al [16] describe the use of information               faces to enable LLMs to autonomously fix bugs and implement
flow labels in a system level defence and prove that their                 features in real software repositories. In future work, we would
(fixed) architecture satisfies a form of noninterference. Other            like to benchmark agents in the LLMbda interpreter against
papers using information flow, and the dynamic tracking of                 SWE-Bench and indeed AgentDojo.
untrusted data sources in particular, include Kim et al.[40]. Li
et al [41] adopt a form of static information flow analysis for a          G. Session types
very simple language of dynamically generated output plans.
Regarding the formal security guarantees, the CaMeL work                   Session types [48], [49] are type systems for structured
acknowledges the lack of such, and the potential difficulties              communication protocols. There may be a connection be-
in providing such in the context of languages like Python.                 tween our conversations—alternating sequences of prompts
The FIDES work, by contrast, provides formal statements of                 and responses—and session types. Exploring session types as
the intended security properties and proves that one specific              a foundation for typing LLM interactions is left as future work.
planning loop satisfies these properties. Their system makes
careful pragmatic choices as to when to not track control-flow                                   VIII. C ONCLUSION
dependencies – i.e., to perform what is commonly called “taint
                                                                           Famously, impressed by the prompt-based programming he
tracking". The choice as to where to weaken the dependency
                                                                           was seeing in AI labs, Andrej Karpathy quipped that the
tracking depends on the labels (e.g. secrets) and the size of the
                                                                           “hottest new programming language is English” [50]. We
data domains. Taint tracking gives rather weak guarantees, but
                                                                           agree, but observe that an LLM cannot execute English on
these can be formalised in a semantic way using a property
                                                                           its own. Instead, given an initial prompt from a human, the
called explicit secrecy [18]. This is the property stated by
                                                                           planner loop of an AI agent builds prompt-response conversa-
the FIDES system for the confidentiality tracking part of the
                                                                           tions by serving tool-calls and running code for the LLM.
system; for integrity noninterference is used. Explicit secrecy
requires a semantic model which splits the behaviour into data             Our lambda calculus represents the code of agentic planners,
and control parts. The idea is to give a semantic condition                and code generated and run during their conversations with
which captures a correct information flow analysis which                   LLMs. The examples run within our interpreter demonstrate
ignores leaks through control flow. Modifying our system                   the expressiveness of our calculus. The theory of noninterfer-
to ignore control flow dependencies is simply a matter of                  ence puts the propagation of labels in our lambda calculus on



                                                                      12
a firm foundation (despite the novel features of our language).                       [16] F. Wu, E. Cecchetti, and C. Xiao, “System-level defense against indirect
Noninterference implies security properties of policies imple-                             prompt injection attacks: An information flow control perspective,”
                                                                                           2024. [Online]. Available: https://arxiv.org/abs/2409.19091
mented with label testing.                                                            [17] J. A. Goguen and J. Meseguer, “Security policies and security models,”
                                                                                           in IEEE Symposium on Security and Privacy. IEEE, 1982, pp. 11–20.
There is a long tradition of analysing and improving the hottest                           [Online]. Available: https://www.cs.purdue.edu/homes/ninghui/readings/
new programming languages by study within the lambda                                       AccessControl/goguen_meseguer_82.pdf
calculus. We hope to have helped renew the tradition.                                 [18] D. Schoepe, M. Balliu, B. C. Pierce, and A. Sabelfeld, “Explicit secrecy:
                                                                                           A policy for taint tracking,” in IEEE European Symposium on Security
                                                                                           and Privacy (EuroS&P). IEEE, 2016, pp. 15–30.
                                                                                      [19] S. Mell, K. Kallas, S. Zdancewic, and O. Bastani, “Opportunistically
                              R EFERENCES                                                  parallel lambda calculus,” Proc. ACM Program. Lang., vol. 9, no.
                                                                                           OOPSLA2, Oct. 2025. [Online]. Available: https://doi.org/10.1145/
 [1] Y. Bengio, R. Ducharme, P. Vincent, and C. Jauvin, “A neural proba-                   3763143
     bilistic language model,” Journal of Machine Learning Research, vol. 3,          [20] S. Mell, B. Zhang, D. Mell, S. Li, R. Ramalingam, N. Yu, S. Zdancewic,
     no. Feb, pp. 1137–1155, 2003.                                                         and O. Bastani, “A fast, reliable, and secure programming language
 [2] I. Sutskever, O. Vinyals, and Q. V. Le, “Sequence to sequence                         for llm agents with code actions,” 2025. [Online]. Available:
     learning with neural networks,” in Advances in Neural Information                     https://arxiv.org/abs/2506.12202
     Processing Systems, vol. 27, 2014, pp. 3104–3112. [Online]. Available:           [21] J. Borgström, U. Dal Lago, A. D. Gordon, and M. Szymczak, “A
     https://arxiv.org/abs/1409.3215                                                       lambda-calculus foundation for universal probabilistic programming,”
 [3] A. Vaswani, N. Shazeer, N. Parmar, J. Uszkoreit, L. Jones, A. N.                      in Proceedings of the 21st ACM SIGPLAN International Conference on
     Gomez, Ł. Kaiser, and I. Polosukhin, “Attention is all you need,” in                  Functional Programming (ICFP). ACM, 2016, pp. 33–46. [Online].
     Advances in Neural Information Processing Systems, vol. 30, 2017.                     Available: https://dl.acm.org/doi/10.1145/2951913.2951942
     [Online]. Available: https://arxiv.org/abs/1706.03762                            [22] T. H. Austin and C. Flanagan, “Efficient purely-dynamic information
 [4] S. Yao, J. Zhao, D. Yu, N. Du, I. Shafran, K. Narasimhan, and Y. Cao,                 flow analysis (abstract only),” SIGPLAN Not., vol. 44, no. 8, p. 6, Dec.
     “React: Synergizing reasoning and acting in language models,” in                      2009. [Online]. Available: https://doi.org/10.1145/1667209.1667220
     International Conference on Learning Representations (ICLR), 2023.               [23] D. E. Denning and P. J. Denning, “Certification of Programs for Secure
     [Online]. Available: https://par.nsf.gov/servlets/purl/10451467                       Information Flow,” Comm. of the ACM, vol. 20, no. 7, pp. 504–513, Jul.
 [5] T. Schick, J. Dwivedi-Yu, R. Dessì, R. Raileanu, M. Lomeli,                           1977.
     L. Zettlemoyer, N. Cancedda, and T. Scialom, “Toolformer: Language               [24] S. Zdancewic, “Programming languages for information security,” Ph.D.
     models can teach themselves to use tools,” in Advances in Neural                      dissertation, Cornell University, August 2002. [Online]. Available:
     Information Processing Systems, vol. 36, 2023. [Online]. Available:                   https://www.cis.upenn.edu/~stevez/papers/Zda02.pdf
     https://arxiv.org/abs/2302.04761                                                 [25] T. H. Austin and C. Flanagan, “Permissive dynamic information
 [6] S. Willison, “Prompt injection attacks against GPT-3,” Sep. 2022. [On-                flow analysis,” in Proceedings of the 5th ACM SIGPLAN Workshop
     line]. Available: https://simonwillison.net/2022/Sep/12/prompt-injection/             on Programming Languages and Analysis for Security, 2010, pp.
 [7] A. Hern, “Why AI systems might never be secure,” The                                  1–12. [Online]. Available: https://users.soe.ucsc.edu/~cormac/papers/
     Economist, Sep. 2025, “The gullibility of LLMs had been                               plas10.pdf
     spotted before ChatGPT was even made public. In the                              [26] A. Bichhawat, V. Rajani, D. Garg, and C. Hammer, “Generalizing
     summer of 2022, Willison and others independently coined the                          permissive-upgrade in dynamic information flow analysis,” in
     term ‘prompt injection’ to describe the behaviour.”. [Online].                        Proceedings of the Ninth Workshop on Programming Languages
     Available: https://www.economist.com/science-and-technology/2025/                     and Analysis for Security, ser. PLAS’14. New York, NY, USA:
     09/23/why-ai-systems-might-never-be-secure                                            Association for Computing Machinery, 2014, p. 15–24. [Online].
 [8] S. Willison, “The dual LLM pattern for building AI assistants                         Available: https://doi.org/10.1145/2637113.2637116
     that can resist prompt injection,” Apr. 2023. [Online]. Available:               [27] P. Buiras, D. Stefan, and A. Russo, “ On Dynamic Flow-
     https://simonwillison.net/2023/Apr/25/dual-llm-pattern/                               Sensitive Floating-Label Systems ,” in 2014 IEEE 27th Computer
 [9] E. Debenedetti, I. Shumailov, T. Fan, J. Hayes, N. Carlini,                           Security Foundations Symposium (CSF). Los Alamitos, CA, USA:
     D. Fabian, C. Kern, C. Shi, A. Terzis, and F. Tramèr, “Defeating                      IEEE Computer Society, Jul. 2014, pp. 65–79. [Online]. Available:
     prompt injections by design,” in IEEE Conference on Secure and                        https://doi.ieeecomputersociety.org/10.1109/CSF.2014.13
     Trustworthy Machine Learning (SaTML), 2026. [Online]. Available:                 [28] A. Askarov, S. Hunt, A. Sabelfeld, and D. Sands, “Termination
     https://arxiv.org/abs/2503.18813                                                      insensitive noninterference leaks more than just a bit,” in Proc.
[10] E. Debenedetti, J. Zhang, M. Balunovic, L. Beurer-Kellner, M. Fischer,                European Symp. on Research in Computer Security, 2008. [Online].
     and F. Tramèr, “Agentdojo: A dynamic environment to evaluate prompt                   Available: https://doi.org/10.1007/978-3-540-88313-5_22
     injection attacks and defenses for llm agents,” Advances in Neural               [29] E. Shinan, “Lark: A parsing toolkit for Python,” 2017. [Online].
     Information Processing Systems, vol. 37, pp. 82 895–82 920, 2024.                     Available: https://github.com/lark-parser/lark
[11] S. Willison, “CaMeL offers a promising new direction for mitigating              [30] OpenAI, “Responses API reference,” OpenAI Platform Documentation,
     prompt injection attacks,” Apr. 2025. [Online]. Available: https:                     2025, accessed: 2026-01-24. [Online]. Available: https://platform.
     //simonwillison.net/2025/Apr/11/camel/                                                openai.com/docs/api-reference/responses
[12] G. D. Plotkin, “Call-by-name, call-by-value and the λ-calculus,”                 [31] A. Church, The Calculi of Lambda Conversion, ser. Annals of
     Theoretical Computer Science, vol. 1, no. 2, pp. 125–159, 1975.                       Mathematics Studies. Princeton, NJ: Princeton University Press, 1941,
     [Online]. Available: https://www.sciencedirect.com/science/article/pii/               no. 6. [Online]. Available: https://www.jstor.org/stable/j.ctt1b9x12d
     0304397575900171                                                                 [32] F. Cardone and J. R. Hindley, “History of lambda-calculus and
[13] D. E. Denning, “A lattice model of secure information flow,”                          combinatory logic,” in Logic from Russell to Church (Handbook
     Communications of the ACM, vol. 19, no. 5, pp. 236–243, 1976.                         of the History of Logic, Volume 5), D. M. Gabbay and
     [Online]. Available: https://dl.acm.org/doi/10.1145/360051.360056                     J. Woods, Eds. Amsterdam: Elsevier, 2006, pp. 723–817. [Online].
[14] T. H. Austin, C. Flanagan, and M. Abadi, “A functional view                           Available: http://www.users.waitrose.com/~hindley/SomePapers_PDFs/
     of imperative information flow,” in Programming Languages and                         2006CarHin,HistlamRp.pdf
     Systems. Berlin, Heidelberg: Springer Berlin Heidelberg, 2012, pp.               [33] C. Böhm and W. Gross, “Introduction to the CUCH,” in Automata
     34–49. [Online]. Available: https://link.springer.com/chapter/10.1007/                Theory, E. R. Caianiello, Ed. New York: Academic Press, 1966, pp.
     978-3-642-35182-2_4                                                                   35–65.
[15] M. Costa, B. Köpf, A. Kolluri, A. Paverd, M. Russinovich, A. Salem,              [34] P. J. Landin, “A correspondence between ALGOL 60 and Church’s
     S. Tople, L. Wutschitz, and S. Zanella-Béguelin, “Securing AI agents                  lambda-notation,” Communications of the ACM, vol. 8, no. 2–3,
     with information-flow control,” arXiv preprint arXiv:2505.23643, 2025.                pp. 89–101, 158–165, feb–mar 1965. [Online]. Available: https:
     [Online]. Available: https://arxiv.org/abs/2505.23643                                 //dl.acm.org/doi/10.1145/363744.363749




                                                                                 13
[35] C. Strachey, “Fundamental concepts in programming languages,”
     Higher-Order and Symbolic Computation, vol. 13, pp. 11–49, 2000,
     lecture notes from 1967, first formally published in 2000. [Online].
     Available: https://link.springer.com/article/10.1023/A:1010000313106
[36] M. Abadi, B. W. Lampson, and J.-J. Lévy, “Analysis and caching of
     dependencies,” in Proceedings of the First ACM SIGPLAN International
     Conference on Functional Programming, ser. ICFP ’96. New York,
     NY, USA: Association for Computing Machinery, 1996, pp. 83–91.
     [Online]. Available: https://doi.org/10.1145/232627.232638
[37] M. Vassena, A. Russo, D. Garg, V. Rajani, and D. Stefan, “From fine-
     to coarse-grained dynamic information flow control and back,” Proc.
     ACM Program. Lang., vol. 3, no. POPL, Jan. 2019. [Online]. Available:
     https://doi.org/10.1145/3290389
[38] D. Stefan, A. Russo, J. C. Mitchell, and D. Mazières, “Flexible
     dynamic information flow control in haskell,” in Proceedings of the 4th
     ACM Symposium on Haskell, ser. Haskell ’11. New York, NY, USA:
     Association for Computing Machinery, 2011, p. 95–106. [Online].
     Available: https://doi.org/10.1145/2034675.2034688
[39] E. Kozyri, F. B. Schneider, A. Bedford, J. Desharnais, and
     N. Tawbi, “Beyond labels: Permissiveness for dynamic information
     flow enforcement,” in 2019 IEEE 32nd Computer Security Foundations
     Symposium (CSF), 2019, pp. 351–35 115. [Online]. Available: https:
     //ieeexplore.ieee.org/document/8823779
[40] J. Kim, W. Choi, and B. Lee, “Prompt flow integrity to prevent
     privilege escalation in llm agents,” 2025. [Online]. Available:
     https://arxiv.org/abs/2503.15547
[41] E. Li, T. Mallick, E. Rose, W. Robertson, A. Oprea, and C. Nita-Rotaru,
     “Ace: A security architecture for llm-integrated app systems,” 2025.
     [Online]. Available: https://arxiv.org/abs/2504.20984
[42] K. Greshake, S. Abdelnabi, S. Mishra, C. Endres, T. Holz, and M. Fritz,
     “Not what you’ve signed up for: Compromising real-world LLM-
     integrated applications with indirect prompt injection,” in Proceedings of
     the 16th ACM Workshop on Artificial Intelligence and Security (AISec),
     2023, pp. 79–90. [Online]. Available: https://arxiv.org/abs/2302.12173
[43] Y. Liu, Y. Jia, R. Geng, J. Jia, and N. Z. Gong, “Formalizing and
     benchmarking prompt injection attacks and defenses,” in 33rd USENIX
     Security Symposium (USENIX Security 24), 2024, pp. 2607–2624.
     [Online]. Available: https://arxiv.org/abs/2310.12815
[44] K. Hines, G. Lopez, M. Hall, F. Zarfati, Y. Zunger, and E. Kiciman,
     “Defending against indirect prompt injection attacks with spotlighting,”
     in Proceedings of the Conference on Applied Machine Learning in
     Information Security (CAMLIS), 2024, pp. 48–62. [Online]. Available:
     https://arxiv.org/abs/2403.14720
[45] F. Jia, T. Wu, X. Qin, and A. Squicciarini, “The task shield:
     Enforcing task alignment to defend against indirect prompt injection
     in LLM agents,” in Proceedings of the 63rd Annual Meeting of
     the Association for Computational Linguistics (ACL), 2025. [Online].
     Available: https://arxiv.org/abs/2412.16682
[46] M. Chen, J. Tworek, H. Jun, Q. Yuan, H. P. d. O. Pinto, J. Kaplan,
     H. Edwards, Y. Burda, N. Joseph, G. Brockman et al., “Evaluating large
     language models trained on code,” arXiv preprint arXiv:2107.03374,
     2021. [Online]. Available: https://arxiv.org/abs/2107.03374
[47] J. Yang, C. E. Jimenez, A. Wettig, K. Lieret, S. Yao, K. Narasimhan,
     and O. Press, “SWE-Agent: Agent-computer interfaces enable automated
     software engineering,” Advances in Neural Information Processing Sys-
     tems, vol. 37, pp. 50 528–50 652, 2024.
[48] K. Honda, “Types for dyadic interaction,” in CONCUR’93, ser. Lecture
     Notes in Computer Science, vol. 715. Springer, 1993, pp. 509–523.
     [Online]. Available: https://doi.org/10.1007/3-540-57208-2_35
[49] K. Honda, V. T. Vasconcelos, and M. Kubo, “Language primitives and
     type discipline for structured communication-based programming,” in
     Programming Languages and Systems (ESOP’98), ser. Lecture Notes in
     Computer Science, vol. 1381. Springer, 1998, pp. 122–138. [Online].
     Available: https://doi.org/10.1007/BFb0053567
[50] A. Karpathy, “The hottest new programming language is English,”
     Jan. 2023, post on X (formerly Twitter). [Online]. Available:
     https://x.com/karpathy/status/1617979122625712128
[51] D. Volpano, C. Irvine, and G. Smith, “A sound type system for
     secure flow analysis,” in Journal of Computer Security, vol. 4,
     no. 2-3. IOS Press, 1996, pp. 167–187. [Online]. Available:
     https://users.cs.fiu.edu/~smithg/papers/jcs96.pdf




                                                                                  14
                      A PPENDIX

Contents:

 A. Proof of the Main Theorem (Theorem 1)
 B. Encoding of derived expressions
 C. Prelude
 D. Code listings omitted from Section VI




                                            15
A. Proof of the Main Theorem (Theorem 1)                                   Restatement of Theorem 1                The following sublanguages
                                                                           satisfy TINI:
The proof makes use of some basic properties of the system–
—often referred to as confinement properties (following Vol-               (1) expressions built without ?;
pano, Irvine, and Smith [51]):                                             (2) expressions which use only one non-bottom label, and
Lemma 4. If pc ⊢ C, e ⇓ C ′ , V , then:                                    (3) expressions in which ? occurs only in the form of assert
(1) pc ⊑ label(V );                                                            statements or strong tests.

(2) C ̸= C ′ implies pc ⊑ label(C) and pc ⊑ label(C ′ ).
                                                                           Proof. For a set of expressions E, define label(E) to be the
                                                                           set of all labels appearing as labels or tests in E.
Proof. (Sketch) (1) By a straightforward induction on the
derivation. In the axioms, the value label equals the current              We prove the theorem by generalising the property proved for
pc; in the remaining rules, the premise pc is the same as or               each of the three sublanguages E, to show that if e0 , e1 ∈ E,
higher than the conclusion’s pc, and the conclusion’s value                and the labels of pc, C0 and C1 are in labels found in E, then
label is at least that of one of the premises.                               •   pc ⊢ C0 , e0 ⇓ C0′ , V0 ,   pc ⊢ C1 , e1 ⇓ C1′ , V1 ,
(2) Also by induction on the derivation. The only rules that                 •   C0 ∼k C1 , and       e0 ∼k e1 .
explicitly change the history are (T EST) and (C LEAR), and
each has explicit side conditions ensuring the stated invariant.           Then C0′ ∼k C1′ and V0 ∼k V1 , V0 , V1 ∈ E, and
                                                                           label(C0′ ), label(C1′ ) ∈ label(E).
                                                                           The theorem then follows by taking pc = ⊥, and from the
In what follows we consider the special case when pc ̸⊑ k.                 fact that ∼k is reflexive and hence [ ] ∼k [ ].
The condition pc ̸⊑ k may be read as: information currently
influencing the program counter is not permitted to flow to                All three parts can be proved in the same manner, by strong
level k. In the special case of a two-level confidentiality lattice        induction on the derivation of the pair of judgements, and
with pc = High and k = Low, this is commonly expressed as                  by cases according to the last derivation rule applied. All the
“the pc is high”, or “the context is high". In the following we            cases, with the exception of test, strong test, and assert, are
sometimes say that “the pc is high" to mean pc ̸⊑ k when a                 common to all three proofs, so we roll the three proofs into
specific k is clear from the context.                                      one; the reasoning in the three parts of the theorem only differs
                                                                           at the case for (T EST) (where we need to assume that the
Lemma 5. If pc ⊢ C, e ⇓ C ′ , V and pc ̸⊑ k, then C ∼k C ′ .               lattice has only two elements) and (A SSERT) and (S TRONG
                                                                           T EST) (for the case of the general lattice). A key observation is
Proof. If C = C ′ , the result is immediate by reflexivity of              that the sublanguage with assert and strong test is closed under
∼k . Otherwise, by Lemma 4(2) we have pc ⊑ label(C) and                    substitution. The parts about the labels of the sublanguages
pc ⊑ label(C ′ ). Since pc ̸⊑ k, it follows that label(C) ̸⊑ k             (V0 , V1 ∈ E, and label(C0′ ), label(C1′ ) ∈ label(E)) are trivial
and label(C ′ ) ̸⊑ k, hence C ∼k C ′ by the definition of ∼k               except for part (iii), where it follows easily by the facts that
on histories.                                                              the set of labels of the expressions are closed under join, the
                                                                           set of expressions is closed under substitution, and that the
This yields a core ingredient for the main noninterference                 labels in the resulting terms must always be the join of labels
proof:                                                                     from the set of expressions.

Lemma 6 (High NI). Suppose that pc ̸⊑ k,                                   We proceed by strong induction on the derivation of pc ⊢
                                                                           C0 , e0 ⇓ C0′ , V0 . The goal is to show that whenever C0 ∼k C1
  •   pc ⊢ C0 , e0 ⇓ C0′ , V0 ,   pc ⊢ C1 , e1 ⇓ C1′ , V1 ,                and e0 ∼k e1 , and
  •   C0 ∼k C1 , and       e 0 ∼k e 1 .                                                           pc ⊢ C1 , e1 ⇓ C1′ , V1 ,
Then C0′ ∼k C1′ and V0 ∼k V1 .                                             then C0′ ∼k C1′ and V0 ∼k V1 . Strong induction is needed
                                                                           because in the derivations for the derived rules (A SSERT)
Proof. By Lemma 5, Ci ∼k Ci′ for i ∈ {0, 1}. Using C0 ∼k                   and (S TRONG T EST), the immediate subderivations correspond
C1 and symmetry/transitivity of ∼k ,                                       to non-immediate subderivations in the actual operational
                                                                           semantics.
                     C0′ ∼k C0 ∼k C1 ∼k C1′ ,
                                                                           We begin with a top-level case-analysis: if pc ̸⊑ k, the results
hence C0′ ∼k C1′ . Moreover, Lemma 4(1) gives pc ⊑                         follow immediately from Lemma 6. Thus, for the remainder
label(Vi ); since pc ̸⊑ k, we have label(Vi ) ̸⊑ k for i ∈ {0, 1}.         of the proof we assume pc ⊑ k and analyse the final rule used
By the definition of ∼k on values, V0 ∼k V1 .                              in the derivation of pc ⊢ C0 , e0 ⇓ C0′ , V0 .



                                                                      16
Case: (F ORK)      e0 = fork e ∼k fork e′ = e1 , so e ∼k e′ .           to obtain C0′ ∼k C1′ and V0 ∼k V1 .
We apply the induction hypothesis (IH) to the subderivations
                                                                          Subcase: l0 ⊑ k        Since pc ⊑ k, we have pc ⊔ l0 ⊑ k.
        pc ⊢ C0 , e ⇓ C0′ , V0         pc ⊢ C1 , e′ ⇓ C1′ , V1          By definition of ∼k , e1 = l0 : e′ for some e′ with e ∼k e′ .
                                                                        Thus we have
to obtain V0 ∼k V1 . Since in the fork rule C0′ = C0 and
C1′ = C1 , we have C0′ ∼k C1′ by the premise of the theorem.                                pc ⊔ l0 ⊢ C1 , e′ ⇓ C1′ , V ′
Case: (L AMBDA)        Immediate: the Ci unchanged and                  and applying the induction hypothesis yields C0′ ∼k C1′ and
e0 = λx.e ∼k λx.e′ = e1 implies pc : λx.e ∼k pc : λx.e′ .               V ∼k V ′ as required. Case: (P ROMPT)        Let e0 = @f0
                                                                        and e1 = @f1 for some expressions f0 ∼k f1 .
Case: (C LEAR)          e1 = clear, so the two rule instances
are identical. Result follows from reflexivity of ∼k .                  We have derivations for i ∈ {0, 1} of the form:
Case: (A PP)      Let e0 = ef ea and e1 = e′f e′a with ef ∼k                       pc ⊢ Ci , fi ⇓ (li : ci ), (mi : vi )
 ′            ′
ef and ea ∼k ea .                                                                  pc ⊢ Ci , @fi ⇓ ni : ci + [(pi , ri )], ni : ri
We have subderivations:
                                                                                      where     pi = serialise(eraseni(vi ))
         (a) pc ⊢ C0 , ef ⇓ C1 , m : λx.e3
         (b) pc ⊢ C1 , ea ⇓ C2 , V2                                                             ni = li ⊔ mi
         (c) pc ⊔ m ⊢ C2 , e3 [x := V2 ] ⇓ C0′ , V                                              ri = generate(ci , pi )
and
                                                                        The definition of ∼k ensures f0 ∼k f1 , so from the induction
          (a’) pc ⊢ C0 , e′f ⇓ C1′ , m′ : λx.e′3                        hypothesis applied to the subderivations of f0 and f1 , we
          (b’) pc ⊢ C1′ , e′a ⇓ C2′ , V2′                               obtain l0 : c0 ∼k l1 : c1 and m0 : v0 ∼k m1 : v1 . It remains
          (c’) pc ⊔ m′ ⊢ C2′ , e′3 [x := V2′ ] ⇓ C0′′ , V ′             to show:

By the induction hypothesis applied to (a) and (a’), we obtain                     n0 : c0 + [p0 , r0 ] ∼k n1 : c1 + [(p1 , r1 )]         (*)
                                                                                                n0 : r0 ∼k n1 : r1
      C1 ∼k C1′        and       m : λx.e3 ∼k m′ : λx.e′3 .
Similarly, applying the IH to (b) and (b’) gives                        We proceed by cases on the labels li and mi which, by the
                                                                        induction hypothesis and definition of ∼k , are exhaustive:
              C2 ∼k C2′          and        V2 ∼k V2′ .
                                                                          Subcase: Both li ⊑ k and mi ⊑ k         By this assumption
We now proceed by case analysis on m and m′ .                           we have ni ⊑ k. By definition of ∼k , we have l0 = l1 and
                                                                        m0 = m1 and hence C0 = C1 and v0 ∼k v1 . From this
  Subcase: m = m′ ⊑ k                     Then e3 ∼k e′3 and, by
                                                                        we see that n0 = n1 . By the serialisation assumption, since
substitutivity,
                                                                        ni ⊑ k, v0 ∼k v1 implies p0 = p1 . Hence by determinism of
                  e3 [x := V2 ] ∼k e′3 [x := V2′ ].                     generate, r0 = r1 and . Thus C0 + [p0 , r0 ] = C1 + [p1 , r1 ]
                                                                        and r0 = r1 , so (*) holds.
Applying the IH to (c) and (c’) yields
                                                                           Subcase: Either li ̸⊑ k or mi ̸⊑ k for some i              From
               C0′ ∼k C0′′       and        V ∼k V ′ .                  this assumption is follows that the outgoing label ni = li ⊔
                                                                        mi ̸⊑ k for i = 0, 1. Thus from the definition of ∼k , n0 :
  Subcase: m ̸⊑ k, m′ ̸⊑ k         Then pc ⊔ m ̸⊑ k and                 c0 + [p0 , r0 ] ∼k n1 : c1 + [p1 , r1 ] and n0 : r0 ∼k n1 : r1 .
pc ⊔ m′ ̸⊑ k, so by Lemma 6 applied to (c) and (c’),
                                                                        This completes the proof of part (1) of the Theorem. The
               C0′ ∼k C0′′       and        V ∼k V ′ .                  remaining two proof cases complete the proof for parts (2)
                                                                        and (3) respectively:
Case: (L ABEL)           Let e0 = l0 : e for some e, with rule
instance                                                                Case: (T EST) (two-point lattice)             In this case ei = e′i ?l
                    pc ⊔ l0 ⊢ C0 , e ⇓ C0′ , V0                         for i = 0, 1, with e′0 ∼k e′1 .
                    pc ⊢ C0 , l0 : e ⇓ C0′ , V0                                            pc ⊢ Ci , e′i ⇓ Ci′ , li : vi
                                                                                           pc ⊢ Ci , l?e′i ⇓ Ci′ , pc : bi
We proceed by cases according to the relation between l0 and
k:                                                                      where                      (
                                                           ′
                                                                                                       true    if li ⊑ l
   Subcase: l0 ̸⊑ k        Here we have e1 = l1 : e for some                                bi =
                                                                                                       false   otherwise.
l1 ̸⊑ k and e′ . Since both pc ⊔ l0 and pc ⊔ l1 are not below k,
we apply Lemma 6 to the subderivations                                  By the IH we have
                     pc ⊔ li ⊢ Ci , e ⇓ Ci′ , Vi                                   C0′ ∼k C1′       and         l0 : v0 ∼k l1 : v1 .



                                                                   17
It remains to show that pc : b0 ∼k pc : b1 . Since we are                  B. Encoding of derived expressions
assuming that pc ⊑ k (the top level case analysis in the
induction proof) this amounts to showing that b0 = b1 .                    We use _ as a variable with the convention that _ only ever
                                                                           appears in the abstraction of a lambda and never in the body
We proceed by cases according to how l0 : v0 ∼k l1 : v1 :
                                                                           or elsewhere.
   Subcase: l0 = l1 ⊑ k and v0 ∼k v1                   In this case
b0 = b1 follows directly.                                                  Derived expressions:
  Subcase: l0 ̸⊑ k and l1 ̸⊑ k    To have b0 = b1 we                        true ≜ λx.λy.x
require                                                                     false ≜ λx.λy.y
                  l0 ∈ L ⇐⇒ l1 ∈ L.                                         () ≜ λx.x
In general this need not hold, but in a two-point lattice there is          if e1 then e2 else e3 ≜ e1 (λ_.e2 ) (λ_.e3 ) ()
only one way to satisfy the assumption of this subcase, namely              let x = e1 in e2 ≜ (λx.e2 ) e1
that k = ⊥ and l0 = l1 = ⊤. From equivalence of l0 and l1                   e1 ; e2 ≜ let _ = e1 in e2
it follows that b0 = b1 .                                                   (e1 , e2 ) ≜ pair e1 e2
                                                                            pair ≜ λx.λy.λs. s x y
Case: (A SSERT)         The behaviour of assert is captured by
                                                                            fst p ≜ p true
a derived rule, so for i ∈ {0, 1} we have derivations
                                                                            snd p ≜ p false
                    pc ⊢ Ci , e ⇓ Ci′ , Vi                                  [ ] ≜ λc. λn. n
                    pc ⊢ Ci , assert l e ⇓ Ci′                              e1 :: e2 ≜ cons e1 e2
Since assert l e ∼k assert l e and assert is not defined using              cons ≜ λh.λt.λc. λn. c h (t c n)
any labelling, it follows from the definition of ∼k that                    [e1 , e2 , . . . , en ] ≜ e1 :: e2 :: · · · :: en :: [ ]
                    assert l e ∼k assert l e.
Since pc ⊢ Ci , e ⇓ Ci′ , Vi is a subderivation of the expansion of        Note that (), the empty tuple, is just the identity function in the
the definition of assert, we can apply the induction hypothesis            standard Church encoding of tuples. We encode numbers as
to obtain                                                                  lists, characters as numbers, and strings as lists of characters.
                             C0′ ∼k C1′ .                                  An object is a list of field-value pairs. Hence, all the the JSON
                                                                           notations supported by our interpreter can be encoded in our
(The other part of the induction hypothesis is not relevant here)          core calculus.
Since both computations return the same labelled value, this
concludes the proof.
                                                                           C. Prelude
Case: (S TRONG T EST)                In this case we suppose e =
m??e0 ∼k e′ , and C0 ∼k C1 , Since we assume e′ is in the                  The following definitions are automatically loaded before user
same sublanguage where test only occurs in the form of an                  code. They provide common utilities including the Y combi-
assert or a strong test, e′ must have the form m??e1 and thus              nator for recursion, array operations, and a syntax summary
we have two derivations of the form                                        for LLM prompts.
               pc ⊢ Ci , ei ⇓ Ci′ , li : vi′
                                                                           # Syntax summary for LLM prompts
              pc ⊢ Ci , m??ei ⇓ Ci′ , (pc ⊔ m : vi )                       let syntax_summary =
                                                                           ’Grammar:
The induction hypothesis gives us C0′ ∼k C1′ and l0 : v0′ ∼k               e ::= x | \x.e | e1 e2 | let x=e1 in e2 | if e1 then
l1 : v1′ , so it remains to show that pc ⊔ m : v0 ∼k pc ⊔ m : v1                e2 else e3
                                                                               | {l1:e1, ..., ln:en} | e.l | e.l:=e | [e1, e2,
where vi is the result of the comparison li ⊑ m, i = 0, 1. We                  ...] | e.[i]
proceed by cases according to the way by which l0 : v0′ ∼k                     | e1+e2 | e1-e2 | e1*e2 | e1/e2 | e1%e2
l1 : v1′ :                                                                     | e1==e2 | e1!=e2 | e1<e2 | e1>e2 | e1<=e2 | e1
                                                                               >=e2
   Subcase: l0 = l1 ⊑ k       If follows that the outcome of                   | e1&&e2 | e1||e2 | not e | n | true | false |
                                                                               "...{e}..."
the test is the same in both cases, i.e. v0 = v1 and we are
done.                                                                      Examples:
                                                                           - Lambda: \x.x + 1 (backslash, param, dot, body)
   Subcase: li ̸⊑ k, i = 1, 2            We reason by cases                - Curried: \a.\b.a + b (nested lambdas)
according to whether the predicate l0 ⊑ m is equivalent to                 - Application: (\x.x + 1) 5
                                                                           - Let: let x = 5 in x + 1
l1 ⊑ m; if they are, then v0 = v1 and we are done. Otherwise,              - If: if x == 0 then 1 else 0
suppose wlog that l0 ⊑ m and l1 ̸⊑ m (and hence v0 and v1                  - Record: {x: 1, y: 2}, field access: r.x, update: r
are different). Since by assumption l0 ̸⊑ k, we have m ̸⊑ k,                   .x := 5
                                                                           - Array: [1, 2, 3], index: arr.[0]
and thus pc⊔m ̸⊑ k, it follows that pc⊔m : v0 ∼k pc⊔m : v1                 - String: "hello {name}" (double-quote interpolates)
as required.                                                                   , single-quote is raw/JSON




                                                                      18
- Recursive function f: \x. let fixer = (\f.\x. ...f
    (...)...) in fix fixer x
(fix is a predefined Y-combinator)
- IMPORTANT: for any recursive function you MUST use
     fix combinator as above.

LAMBDA RULES - backslash ONLY starts lambdas, never
    in variable names:
- Variables are bare names: x, foo, myVar (no
    backslash!)
- In lambda body, reference params by bare name: \x.
    x + 1
- WRONG: \x.\x + 1 (backslash starts new lambda, not
     variable x)
- RIGHT: \x.x + 1 (bare x refers to the parameter)

CRITICAL STRING RULES:
- Double quotes "...": {x} is interpolation.
    Apostrophes OK. Braces NOT OK.
- Single quotes: for JSON/braces ONLY. NO
    apostrophes (they end the string!)

INVALID - do not generate:
- Top-level bindings: let x = 5 (missing "in")
- Multi-param lambda: \x y.body (use \x.\y.body)
- Arrow syntax: \x -> body (use \x.body)
- null keyword: use "null" string or false instead’

# Y combinator for recursion
let fix = \f. (\x. f (\v. x x v)) (\x. f (\v. x x v)
    )

# Check if a value is a function
let is_fn = \x. (shape x).type == "function"

# Check if a value is an array
let is_array = \x. (shape x).type == "array"


D. Code listings omitted from Section VI

Figure 1 shows imperative programming in the monadic style
used to program the tool-calling examples.
Figure 2 shows a tool-calling agent for Fig 5 of the CaMeL
paper [9], programmed within our calculus in a monadic style.
Figure 3 shows how a trusted conversation can generate
code that uses a quarantined conversation to avoid a prompt
injection vulnerability [9].




                                                                19
let monadic_api =
’
The monadic type IO t represents stateful computation with simple exception handling.
An expression of type IO t is a top level program expected to return an answer of type t.

The (lower case) state type is an abstract record type.

The (lower case) type value is the top-type of all values in the calculus.

Use the following functions to assemble monadic computations:

return : (x:a) -> IO a
failwith : (error_msg: string) -> IO A
bind : (m:IO a) -> (f:a -> IO b) -> IO b
get_state : IO state
set_state : (new_state:state) -> IO state
prompt_llm : (prompt:value) -> IO value
performIO : (m:IO a) -> (initial_state:state) -> a | string

Example: bind (return 23) (\x. bind (return 10) (\y. prompt_llm "add {x} and {y}"))
Example: performIO (return 42) {} returns 42
Example: performIO (failwith "oops") {} returns "Error: oops"
’

let return = \x. \state. [[true, x], state]
let failwith = \e. \state. [[false, e], state]
let get_state = \state. [[true, state], state]
let set_state = \state_1. \state_0. [[true, {}], state_1]
let bind = \m. \f.
  \state_0.
  let union_state = m state_0 in
  let union = union_state.[0] in
  let state_1 = union_state.[1] in
  let normal = union.[0] in
  if normal then
    (let x=union.[1] in f x state_1)
  else
    (let e=union.[1] in failwith e state_1)

let prompt_llm = \p.
  let union = @ p in
  let ok = union.[0] in
  if ok then
    (let v=union.[1] in return v)
  else
    (let msg=union.[1] in failwith msg)

# performIO : IO a -> state -> a | string
# Executes a monadic computation on a state, returning value on success or "Error: ..." on failure
let performIO = \m. \state.
  let result = (m state).[0] in
  if result.[0] then result.[1] else "Error: {result.[1]}"

                                   Fig. 1. Imperative programming in the monadic style.




                                                           20
let system_prompt =
  "{tool_api}.
    You are a versatile agent, but you only emit literal JSON values, not lambda calculus.

    A tool call must take the form: [’function-name’, value1, ... valueN]
    where function-name is the name of one of the provided functions
    and each value is a literal (not an expression).
    Do not include the initial state argument, which will be provided automatically.

    Every answer in this session must be in one of the following two forms.
    (1) you have info to answer your goal, emit [’answer’, the-answer-as-a-value];
    (2) to gather more information, emit [’tool-call’,[’function-name’, value1, ... valueN]].
    You will receive the answer in the next prompt, and can then continue.
    Only return a literal array in format (1) or (2), never any other expression such as a let or lambda.
    Remember, every answer must be in one of these two forms.
    Your first answer should be [’answer’, 42]."

# Response format helpers
let is_answer = \r. let s = shape r in s.type == "array" && s.length == 2 && r.[0] == ’answer’
let dest_answer = \r. r.[1]
let is_tool_call = \r. let s = shape r in s.type == "array" && s.length == 2 && r.[0] == ’tool-call’
let dest_tool_call = \r. r.[1]

# tool_agent: int -> string -> IO value
# Recursive agent loop: runs until [’answer’, v], feeds errors back to LLM for retry
# Counts down rounds from initial budget to 0
let tool_agent = fix (\self. \rounds. \p.
  if rounds == 0 then failwith "Max rounds exceeded" else
  let r = @ p in
  if not r.[0] then
    self (rounds - 1) "Error: {r.[1]}. Try again. Reply with [’answer’, value] or [’tool-call’, [...]]."
  else
    let response = r.[1] in
    if is_answer response then
       return (dest_answer response)
    else if is_tool_call response then
       let call = dest_tool_call response in
       bind (exec_tool_call call) (\result.
         self (rounds - 1) "Tool {call} returned: {result}. Reply with [’answer’, value] or [’tool-call’,
             [...]].")
    else
       self (rounds - 1) "Expected [’answer’, v] or [’tool-call’, [...]]. Got: {response}"
)

# run_agent: string -> IO queue
# Initializes the conversation, runs the looping agent, and returns the message queue
let run_agent = \goal.
  let _ = clear in
  bind (prompt_llm system_prompt) (\_.
  bind (tool_agent 5 "Your goal: {goal}. Issue tool calls until you can answer directly.") (\_.
  bind (get_state) (\state.
  return state.queue)))

                                Fig. 2. Tool-calling agent for Fig 5 of the CaMeL paper [9].




                                                            21
let direct_api =
"{syntax_summary}

You have access to functions with the following types:

get_last_email: state -> string
send_email: (to:string) -> (subject:string) -> (body:string) -> state -> state
quarantine: (prompt:string) -> json   # prompt an LLM, returns JSON

The quarantine function prompts an LLM and returns true, false, number, double quoted string, or JSON.
The prompt should describe the result format or give an example.
Example: quarantine ’Add 1 and 2. Return a number.’
"

let direct_code_gen_prompt = \goal.
  "{direct_api}.
   Write a state-passing function in the form (\\state.body) where body returns an updated state.
   REMINDER: Use double quotes for text (apostrophes OK), single quotes ONLY for JSON with braces.
   The function should accomplish this goal: {goal}."

# codegen_agent: int -> string -> string -> value
# Recursive code generation loop: prompts LLM, feeds errors back for retry
let codegen_agent = fix (\self. \retries. \base_prompt. \prompt.
  if retries > 5 then "Error: max retries exceeded" else
  let r = @ prompt in
  if not r.[0] then
    self (retries + 1) base_prompt "Error: {r.[1]}. Fix your code and try again. {base_prompt}"
  else
    r.[1]
)

# direct_code_gen: string -> (state -> state)
let direct_code_gen = \goal.
  let _ = clear in
  let base_prompt = direct_code_gen_prompt goal in
  codegen_agent 0 base_prompt base_prompt

                                           Fig. 3. Direct code generation




                                                        22
