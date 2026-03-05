<!-- extracted-by: marker -->
# The LLMbda Calculus:

# AI Agents, Conversations, and Information Flow

Zac Garby University of Nottingham, UK Andrew D. Gordon University of Edinburgh, UK David Sands

Chalmers University of Technology and The University of Gothenburg, Sweden

*Abstract*—A conversation with a large language model (LLM) is a sequence of prompts and responses, with each response generated from the preceding conversation. AI agents build such conversations automatically: given an initial human prompt, a planner loop interleaves LLM calls with tool invocations and code execution. This tight coupling creates a new and poorly understood attack surface. A malicious prompt injected into a conversation can compromise later reasoning, trigger dangerous tool calls, or distort final outputs. Despite the centrality of such systems, we currently lack a principled semantic foundation for reasoning about their behaviour and safety. We address this gap by introducing an untyped call-by-value lambda calculus enriched with dynamic information-flow control and a small number of primitives for constructing prompt-response conversations. Our language includes a primitive that invokes an LLM: it serializes a value, sends it to the model as a prompt, and parses the response as a new term. This calculus faithfully represents planner loops and their vulnerabilities, including the mechanisms by which prompt injection alters subsequent computation. The semantics explicitly captures conversations, and so supports reasoning about defenses such as quarantined sub-conversations, isolation of generated code, and information-flow restrictions on what may influence an LLM call. A termination-insensitive noninterference theorem establishes integrity and confidentiality guarantees, demonstrating that a formal calculus can provide rigorous foundations for safe agentic programming.

#### I. INTRODUCTION

#### <span id="page-0-0"></span>*A. Terminology: prompt-response conversations and AI agents*

At the core of generative AI are probabilistic algorithms to generate (or complete) one message from another, where a *message* is a sequence of tokens that encodes a piece of text. A *token* is an integer index into a large fixed vocabulary of words, subwords, and special symbols. An LLM is *autoregressive*, meaning that it samples text serially from an initial input [\[1\]](#page-12-0). The model conditions the prediction of the current token on the concatenation of the original input and all previously generated tokens. The decoding process continues iteratively until the model samples an end-of-sequence token, which signals the semantic completion of the response [\[2\]](#page-12-1). Otherwise, generation terminates if the length exceeds a pre-defined maximum token limit, known as the context window [\[3\]](#page-12-2).

Let the *prompt*, p, and the *response*, r, be the token sequences that are the input and output of this generation process.

By iterating generation itself, we can build up a chat or dialogue from an alternating sequence of prompts and responses. Let a *prompt-response conversation*, c, be a sequence [(p1, r1), . . . ,(pn, rn)], where each ri+1 is generated from the concatenation p<sup>1</sup> + r<sup>1</sup> + · · · + p<sup>i</sup> + r<sup>i</sup> + pi+1.

Behind several sorts of human-AI interaction are processes that build up one or more prompt-response conversations. The simplest form of chatbot just builds up a conversation where the human user supplies each p<sup>i</sup> while the system replies with each r<sup>i</sup> . An AI agent acting for a human builds up a conversation too, but with more autonomy.

In a typical interaction with an AI agent, the initial prompt p<sup>1</sup> contains the instruction from the human user while the final response r<sup>n</sup> is a message to the user. The intermediate messages arise from the agent's planner algorithm; they trace the unrolling of the agentic loop. A common case is that an intermediate response r<sup>i</sup> encodes an instruction from the LLM to an external tool [\[4\]](#page-12-3), [\[5\]](#page-12-4). Tools enable searching the web, generating an image, reading or editing a file, running a shell command, or running some code, and so on. The planner receives the tool instruction r<sup>i</sup> , executes it, and forms prompt pi+1 with the result from the tool. The LLM's response, r<sup>i</sup> , may be a piece of JSON encoding a web search, or it may be a piece of code to be run locally and able to read and update state separate from the LLM. The result of the tool, pi+1, may again be some JSON holding search results, or it could be the textual response from the Python interpreter successfully running a program, or perhaps an error message from a crash.

# *B. Motivation: prompt injection attacks and countermeasures*

A *prompt injection attack* arises in a conversation where the generation of r<sup>j</sup> from p<sup>j</sup> is unduly influenced by a prompt earlier in the conversation. Prompt injection attacks on AI agents became known by late 2022 [\[6\]](#page-12-5), [\[7\]](#page-12-6). In March 2023, Simon Willison [\[8\]](#page-12-7) proposed the *dual LLM pattern*, where a *Privileged LLM* (P-LLM) and a *Quarantined LLM* (Q-LLM) work together. Instead of the AI agent relying on a single conversation, the idea is to have separate conversations to avoid untrusted prompt messages from affecting later actions. The conversations conducted by the P-LLM are kept decontaminated from untrusted data. The conversations conducted by the Q-LLM act on untrusted data in isolation. CaMeL [\[9\]](#page-12-8) is a countermeasure based on refinements of the dual LLM pattern, including code generation and dynamic information flow tracking. Its practical effectiveness is shown on the AgentDojo prompt injection benchmark [\[10\]](#page-12-9). Willison [\[11\]](#page-12-10) acknowledges its effectiveness. Still, although it describes a correctness property, the CaMeL paper includes no formal reasoning or proof, but describes formalization as a "crucial direction" for further work. Formalizing and reasoning about AI agents in general, and CaMeL in particular, was a prime driver for the research in this paper.

#### *C. This paper: a calculus of prompt-response conversations*

Section [II](#page-3-0) describes the syntax and informal semantics of our LLMBDA calculus, an extension of the untyped lambda calculus [\[12\]](#page-12-11). We aimed for a kernel able to express both the code of agent planners and the code that they generate. (We pronounce the name LLMBDA "L-L-Em-da", to rhyme with "lambda.")

To track information flow we assume that the intended information flows are modelled as a lattice of labels [\[13\]](#page-12-12) where, as is standard, the partial order (⊑) between labels l, l ′ etc. is the "may-flow-to" relation. For example, with two labels T and U for trusted and untrusted data, T ⊑ U indicates that T-data flow to data labelled U, but the reverse flow is not allowed.

To track and test information flow, our calculus relies on two existing primitives [\[14\]](#page-12-13): *labelled expressions* l : e and *label testing* l?e, which returns a boolean to indicate whether the label l ′ of e may safely be allowed to flow to data labelled l, that is, it returns the value of l ′ ⊑ l.

To manipulate prompt-response conversations, we introduce three original primitives:

- (1) the @ operator @e to continue the current conversation by prompting the LLM to generate a response, and parse it as semi-structured data, including text and code;
- (2) a fork construct to begin a fork of the current conversation, a key aspect of context management; and
- (3) a clear construct to clear the current conversation, quarantining the conversation from the past history.

Section [III](#page-4-0) develops a formal theory. If we omit information flow tracking, the core of our semantics is a big-step relation

$$c, e \downarrow c', v$$

meaning that given an initial conversation c, expression e returns a value v, and updated conversation c ′ .

For example, take a generation expression @e. Suppose c is the current conversation, and v is the value of e, that is, c, e ⇓ c ′ , v. Suppose that r is the response message generated by the LLM, given the concatenation of c ′ and serialise(v), the tokenization of v. The semantics of @e is to extend the conversation with the prompt serialise(v), followed by the response r, and to return the parsed response parse(r) as its value.

$$c, @e \Downarrow c' + [(serialise(v), r)], parse(r)$$

Although the semantics manipulates token sequences and conversations, they are not data types within the language itself, a deliberate choice. The serialize and parse functions appear only in the semantics, not expressions. Still, we have evidence that generation is an expressive abstraction for programming with LLMs as shown by Sections [II](#page-3-0) and [VI.](#page-9-0)

Just as with serialisation and parsing, we model the behaviour of the LLM in an abstract and intentionally minimal way. The only semantic assumption we make is determinism: at each step the LLM's response is a pure function of the conversation history so far. This abstraction matches earlier formal treatments of LLM interactions [\[15\]](#page-12-14), while keeping the calculus general enough to accommodate a wide variety of concrete model behaviours.

#### *D. Semantics and semantic guarantees*

Section [IV](#page-7-0) presents our main technical result, Theorem [1,](#page-8-0) is a termination-insensitive noninterference theorem. Ignoring termination behaviour, information labelled at level m cannot affect observations at level n unless m ⊑ n.

An important and particularly subtle aspect of our semantics is the treatment of label testing. While the label lattice broadly models the intended information flow policy, the label testing operation is means by which policies can be enforced in the code itself. For example, suppose that we are constructing a record which is intended to be the parameter of a securitysensitive API. A policy could be implemented as an API wrapper or a callee-check, and the policy for such a scenario might simply be that the label of the data should be trusted. A more elaborate policy might decide, in addition, that untrusted data is also OK as long as a "sanitized" flag is set, and furthermore labelled as trusted. We cannot predict the variety of policy checks that might be implemented, but regardless of what the policy code does, the main theorem ensures that it makes its decisions using semantically correct labels.

With this perspective in mind, our semantics defines the label of the result of a test to be *independent* of the labels that it is inspecting. From a policy-enforcement perspective this is what we want: if we test whether some data untrusted, then we do not want the outcome to be labelled as untrusted—who would base a policy decision on untrusted data?

This "liberal" design for label testing is natural from a policy-checking perspective—but it turns out to be incompatible with noninterference in the general case. Our main theorem therefore identifies and formalises the precise constraints under which label tests can remain expressive while still preserving noninterference.

#### *E. Modelling Prompt Injections and Countermeasures*

For any formal system (such as our LLMBDA calculus) to be effective for security analysis of AI agents, it must be capable of representing both their intended behaviour and their potential security flaws.

Given our motivation to model and experiment with meaningful examples of AI agents, such as those in the CaMeL paper, we built an interpreter for our calculus. Section [V](#page-8-1) describes the LLMBDA interpreter, which allows us to build meaningful examples. It is a direct implementation in Python of our bigstep semantics as a recursive interpreter, using the OpenAI responses API to implement the @ operator.

Section [VI](#page-9-0) illustrates stateful AI agents via monadic programming within our calculus, including tool-calling agents and the CaMeL pattern of code generation by a privileged P-LLM and quarantined execution of a Q-LLM. An example from the CaMeL paper illustrates a conventional toolcalling architecture where untrusted data shares the same prompt-response conversation with tool-commands, and thus its vulnerability to prompt injection, demonstrated by our interpreter. Moreover, we demonstrate that the dual LLM pattern defeats this attack, and that label tracking and testing in our lambda calculus model CaMeL's use of capabilities. We discuss the noninterference properties of our example implied by Theorem [1.](#page-8-0)

#### *F. Main Contributions*

We make two primary contributions:

- 1. A formal calculus capturing the core mechanisms of agentic programming. To the best of our knowledge, this is the first lambda calculus extended to model the major operational features of agentic systems built around LLMs. Our calculus, executable in the LLMBDA interpreter, supports:
  - prompting and parsing semi-structured data, including both text and code;
  - explicit conversational context management—extending, forking, and clearing conversations;
  - repair loops in which the LLM reacts to error messages by attempting corrective steps;
  - tool invocation via model-generated instructions or dynamically generated code;
  - dynamic security labels attached to values to track confidentiality and integrity throughout agent execution.
- 2. A sound information-flow foundation for defending against prompt injection. We formalize agents in the CaMeL style [\[9\]](#page-12-8), where each sensitive tool function exposed to the agent can enforce its own protection via dynamic label checks. Theorem [1](#page-8-0) implies that these dynamic checks—–when used in a library of tool functions–—soundly enforce the intended policy. In particular, we obtain the first formalization of information-flow-based defences for general agentic programs.

Earlier works either deal with information flow tracking for general code but do not provide any formal security proofs (CaMeL [\[9\]](#page-12-8)), or provide formal information flow properties, but only for a fixed program schema, for example, FIDES [\[15\]](#page-12-14), or for a fixed system architecture [\[16\]](#page-12-15).

#### *G. Closest related work: FIDES, OPAL, Quasar*

FIDES [\[15\]](#page-12-14) is the first research to give formal statements of the expected guarantees offered by information-flow tracking in a planner for AI agents: noninterference [\[17\]](#page-12-16) for integrity and explicit secrecy [\[18\]](#page-12-17) for confidentiality. The planner algorithms are presented as simple program schemas. FIDES is not based on the lambda calculus, and does not consider prompted code generation as in CaMeL and our work. Still, FIDES is shown to be a practical system that can perform a broad set of tasks from the AgentDojo benchmark with security guarantess. It is future work to benchmark our calculus in a similar way.

A couple of languages for programming with LLMs, OPAL [\[19\]](#page-12-18) and Quasar [\[20\]](#page-12-19), are based on the lambda calculus and have formal semantics. These language offer benefits including performance, quantification of uncertainty to help against hallucinations, and assistance to the user when reviewing security decisions. Quasar, like our calculus, is designed to be generated by an LLM. These works are closely related to ours, although they do not discuss prompt injection, and do not consider information flow or noninterference results.

We postpone a full discussion of related work to Section [VII.](#page-10-0)

#### *H. Limitations of this work*

One limitation of our formalisation is an assumption of LLM determinism. Although there is a good case to be made against using nondeterminism, a better approach would be to admit probabilistic behaviour, together with probabilistic versions of noninterference. We leave that to future work; Borgström et al. [\[21\]](#page-12-20) develop the theory of a big-step semantics for a probabilistic lambda calculus. Instead of assuming message generation to be deterministic, we might adopt their weighted big-step relation to obtain a probabilistic semantics and attempt to establish some probabilistic variant of terminationinsensitive noninterference.

Another limitation of our approach is our modelling of tool calls, and in particular how we model data sources. In our approach, all data sources are assumed to be in the program. A more realistic model would include more general forms of interaction with external data and tools, and in particular data sources that are obtained by external tool calls. It is fairly easy to envisage how our system might be augmented with such external tool calls and data sources, but this comes at the price of expanding the calculus and complicating the theoretical development.

Our development in Section [VI](#page-9-0) centres on different versions of a single example, and we have not presented a full model of the CaMeL system. Still, we offer the results in this paper as a firm basis on which to study and build a fully practical system.

#### II. THE LLMBDA CALCULUS, BY EXAMPLE

<span id="page-3-0"></span>We add three new kinds of expression to the lambda calculus.

The @ *operator*, @e, captures the key new programming concept in our calculus: it extends the current conversation by sampling the next response given the prompt given by the expression e, and returns the parse of the response as its value.

The *fork expression*, fork e, makes a temporary fork of the conversation for the expression e, and then discards it.

The *clear expression*, clear, clears the current conversation.

#### *A. Example: postcode extraction*

In this first example, the task is to extract and normalize postcodes by inserting the optional middle space. We establish a detailed prompt once, then make three short queries that inherit it We prompt the LLM using the @ operator to prime it for the text processing task, and then repeatedly fork the context to process each of three example addresses. The example illustrates that the conversation context persists between the first use of @ and subsequent calls. Moreover, by using a fork expression, we ensure that each of the three examples are processed independently of each other.

```
# Rich context established once
let setup = @'You are a UK postcode extractor. UK
    postcodes have the format: 1-2 letters, 1-2 digits,
    optional space, digit, two letters. Examples: EC1A 1
    BB, W1A 0AX, LS14AP, G1 1XQ. When asked to extract,
    return ONLY the postcode as a double-quoted string,
    always including the space. Now return {ready: true}
     to confirm.'
# Short prompt works because context is inherited
let extract = \addr.
  let r = fork @"Extract: {addr}" in
  if r.[0] then r.[1] else "error"
[ extract "10 Downing Street, London SW1A2AA",
  extract "221B Baker Street, London NW16XE",
  extract "Old Trafford, Manchester M16 0RA" ]
```

The @ operator returns the outcome of parsing the response from the LLM. It returns either an array [true, vok] where vok is the parsed value on success, or [false, verror] where verror is the textual error message on parse failure.

The expression **if** r.[0] **then** r.[1] **else** "error" above is inspecting the boolean to see whether or not the parse has succeeded. Below, in the output from the LLMbda interpreter, the list shown as the value of setup indicates a successful parse of {ready: **true**}.

```
setup = [true, {ready: true}]
extract = fn
["SW1A 2AA", "NW16 XE", "M16 0RA"] (9.3s)
```

The final value is a list of three postcodes, as expected.

#### *B. Example: a simple agentic repair loop*

The @ operator can prompt the LLM to emit code as a lambda abstraction within our calculus. Since our grammar is bespoke sometimes the LLM makes mistakes. The standard solution is an agentic loop: detect the syntactic error message, and return it to the LLM as a continuation of the conversation. Below we build a simple retry loop that adds syntax hints and keeps trying until the code parses. The identifier syntax\_summary from our prelude in Appendix [C](#page-17-0) is a set of hints to the LLM on the syntax of our calculus. The identifier fix is a call-byvalue Y-combinator.

```
# Retry loop: keeps prompting until syntax is valid
let retry = fix (\self. \round. \max. \prompt.
  if round > max then [false, "max retries"] else
  let r = @prompt in
  if r.[0] then [true, r.[1], round]
  else self (round + 1) max "Error: {r.[1]}. Try again.")
# Generate with syntax hints and auto-retry
let generate = \p. retry 1 5 (syntax_summary + ". " + p)
generate "Write the factorial function"
```

```
retry = fn
generate = fn
[true, \n.
 let fixer =
   \f.
    \n.
      if n == 0 then 1 else n * f (n - 1)
in
 fix fixer n, 1] (7.3s)
```

# *C. Example: Agentic loop with test cases*

Our third example is a more complex agentic loop that synthesizes a function from a prompt and checks that they satisfy a pair of test cases. The loop uses the @ operator to prompt for a function, and loops if there is a syntax error, if the returned value is not a lambda, or if either of the two cases fails. The loop is called from an agent function that begins by forking the context and clearing it, that is, it works in an empty context, but restores the original context on exit. In this regard, the agent function works like subagents in Claude Code.

```
# Test a function against test cases
# Returns [true, f] or [false, "errors"]
let run_tests = \ts. \f.
  let r0 = f ts.[0].[0] in let e0 = ts.[0].[1] in
  let r1 = f ts.[1].[0] in let e1 = ts.[1].[1] in
  if r0 == e0 && r1 == e1
  then [true, f]
  else [false, "got {r0} & {r1} expected {e0} & {e1}"]
# Recursive synthesis loop with retries
# Returns [success, value, rounds_taken]
let synth = fix (\self. \ts. \round. \max. \prompt.
  if round > max then [false, "max retries", max] else
  let r = @prompt in
  if not r.[0] then self ts (round + 1) max "Syntax error
    : {r.[1]}. Try again." else
  if not (is_fn r.[1]) then self ts (round + 1) max "Not
```

```
a lambda. Write \\p. ..." else
  let t = run_tests ts r.[1] in
  if not t.[0] then self ts (round + 1) max "Tests failed
    : {t.[1]}. Try again." else
  [true, t.[1], round])
# Agent: fork context, clear, synthesize with syntax
    guidance, generate report
let agent = \tests. \prompt. fork (
  let _ = clear in
  let full_prompt = syntax_summary + ". " + prompt in
  let result = synth tests 1 5 full_prompt in
  let rounds = result.[2] in
  let report = if result.[0]
    then "Synthesis succeeded in {rounds} round(s)."
    else "Synthesis failed after {rounds} round(s)." in
  {result: result, report: report})
# Task 1: swap x and y coordinates
let swap = agent
  [[{x: 1, y: 2}, {x: 2, y: 1}],
   [{x: 5, y: 3}, {x: 3, y: 5}]]
  'Write a lambda \p. that swaps x and y. Example: {x:1,y
    :2} becomes {x:2,y:1}'
# Task 2: reflect point on X-axis (negate y)
let reflect = agent
  [[{x: 1, y: 2}, {x: 1, y: 0 - 2}],
   [{x: 3, y: 5}, {x: 3, y: 0 - 5}]]
  'Write a lambda \p. that negates y (use 0 - p.y).
    Example: {x:1,y:2} becomes {x:1,y:-2}'
```

```
run_tests = fn
synth = fn
agent = fn
swap = {result: [true, \p.{x: p.y, y: p.x}, 1], report: "
    Synthesis succeeded in 1 round(s)."}
reflect = {result: [true, \p.{x: p.x, y: 0 - p.y}, 1],
    report: "Synthesis succeeded in 1 round(s)."} (3.1s)
```

# III. SYNTAX AND SEMANTICS

# <span id="page-4-2"></span><span id="page-4-0"></span>*A. Lambda calculus plus conversations*

The expressions e of the first part of our calculus are as follows, where x ranges over variables. (Section [III-C](#page-4-1) describes the second part, dealing with labels.)

λ @: λ with conversations

| e, f ::= | expressions               |
|----------|---------------------------|
| x        | variable                  |
| λx.e     | abstraction               |
| e1<br>e2 | application               |
| @e       | @ operator for generation |
| fork e   | fork the conversation     |
| clear    | clear the conversation    |
|          |                           |

We have standard notions of free and bound variables. In λx.e, the variable x binds any free occurrences of x in e. We say an expression e is *closed* if it has no free variables. We write e[x := e ′ ] for the outcome of substituting closed e ′ for each free occurrence of x in the expression e. (Our development does not rely on α-conversion.)

The execution or *evaluation* process described next interprets a closed expression to yield a value, and may read and update the current conversation. In this first part of the calculus, a value v is a closed lambda abstraction.

- To evaluate λx.e: return it, with no change to the state.
- To evaluate e<sup>1</sup> e2, first evaluate e<sup>1</sup> to a value λx.e. Evaluate e<sup>2</sup> to a value v. Continue by evaluating e[x := v]. Pass the conversational state from one step to the next.
- To evaluate @e, first evaluate e to a value vp, possibly updating the conversation. Serialize v<sup>p</sup> to a token sequence p, the prompt to the LLM. Sample the response r generated by the LLM given c extended with p. Parse the value v<sup>r</sup> from the response. Return the value v<sup>r</sup> and extend the conversation with (p, r).
- To evaluate fork e save a copy of the current conversation c. Evaluate e from the current conversation, yielding value v, and a possibly updated conversation. Restore c and return v.
- To evaluate clear, set the conversation to the empty sequence [], and return the unit value λx.x.

#### *B. Derived data types and expressions*

For examples and for practical programming, we rely on JSON-style data types: booleans, numbers, strings, and records, with the following syntax. Appendix [B](#page-17-1) shows standard Church-style encodings of all of these derived values and expressions. For example, we derive our unit value () ≜ λx.x.

#### Derived forms e, f, expressible in λ @

```
e, f ::= derived expressions
   let x = e1 in e2 let expression
   () true false n ∈ Z s ∈ string literals
   if e1 then e2 else e3 conditional
   [e1, . . . , en] array
   e1.[e2] element extraction
   {s1 : e1, . . . , sn : en} record
   e.s field access
   e.s := e
        ′
                          functional field update
```

Evaluation of the derived expressions is similar, and standard, and so we omit the details. In our formal development we treat derived expressions as being encoded within our core calculus. The LLMbda interpreter implements them directly.

#### <span id="page-4-1"></span>*C. Completing our core lambda calculus with labels*

To track information flow in our calculus, we assume a set of labels k, l, m, pc drawn from a join-semi-lattice [\[13\]](#page-12-12) with join ⊔, ordering ⊑, and top and bottom elements written ⊤ and ⊥. In what follows we will refer to the join-semi-lattice as just a lattice.

Our theory applies to any such structure but all our examples run in the LLMbda interpreter where we consider a label to be an element of the powerset of {U, S} ordered by subset inclusion, where U means untrusted, and S means secret. In earlier work, e.g. [\[15\]](#page-12-14), this label lattice is often presented equivalently as the product of a confidentiality lattice P (Public) ⊑ S (Secret) and an integrity lattice T (Trusted) ⊑ U (Untrusted).

In general, l⊔⊤ = ⊤ and l⊔⊥ = l. In our interpreter, ⊥ = {} and ⊤ = {U, S}.

# Labels:

```
k, l, m, pc ⊆ {U, S} label (U for untrusted, S for secret)
```

Building on prior work on dynamic information flow tracking in the lambda calculus, and most closely to the work of Austin et at. [\[22\]](#page-12-21), [\[14\]](#page-12-13), we add label and test expressions to our calculus:

λ <sup>l</sup>:@: λ @ with labels

| e, f ::= | expressions                              |
|----------|------------------------------------------|
|          | @ (Section<br>expressions of λ<br>III-A) |
| l : e    | ℓ expression                             |
| l?e      | ℓ test                                   |
|          |                                          |

A *labelled value* V is an expression of the form l : v where v is a value (a lambda expression). Our labelling discipline is *parsimonious* in the sense of [\[22\]](#page-12-21), so that we never need to label anything with ⊥. Hence in the interpreter unlabelled expressions are assumed to be trusted and public, and we need only explicitly label the secrets and the untrusted things. Labels play a dual role: they provide the intended meaning of data sources, but they can also be used as explicit coercions of values ("treat this value as if it where a secret") which can be used to better control how information flow is tracked.

In the absence of side effects, the evaluation semantics of these expressions can be understood as:

- To evaluate l : e, first evaluate e to its labelled value l ′ : v, and return l ⊔ l ′ : v.
- To evaluate l?e, first evaluate e to its labelled value l ′ : v; return true if l ′ ⊑ l, or false otherwise.

For example, in the four-point lattice of integrity and secrecy labels:

```
{U}?42 evaluates to true (⊥ ⊑ ⊥)
{U}?{U} : 42 evaluates to true ({U} ⊑ {U})
{U, S}?{U} : 42 evaluates to true ({U} ⊑ {U, S})
{}?{U} : 42 evaluates to false ({U} ̸⊑ ⊥)
{S}?{U} : 42 evaluates to false ({U} ̸⊑ {S})
```

In a test of the form l?e, one would typically expect e to be a bound variable x: you compute a value, bind it to x, and depending on the outcome of a test you decide how to use x. When e has side-effects (via @), the label says nothing about the level of any prompts sent. Fortunately one can readily test the label of the conversation history by prompting it and testing the result. Fork allows us to roll back the conversation history after doing this:

```
testConversation m ≜ m?fork @( )
```

Here @() prompts the LLM with (). Whatever response is returned, it will have the label of the conversation history. The fork operation then restores the conversation history back to the point before the prompt. This completes the full syntax of our calculus. We have stated our intended semantics as informal evaluation rules. In the rest of this section, we define a formal semantics.

#### *D. Behind the @ operator: serialize, generate, parse*

Our model of generating messages from an LLM is largely abstract, with some minimal assumptions. Here we describe the semantics-level entities that are used to model the communication with the LLM and its state.

#### Messages and (labelled) conversations:

```
p, r ::= token sequence message: prompt or response
c ::= [(p1, r1). . .(pn, rn)] conversation
C ::= l : c labelled conversation
```

To convert a value into a prompt we use semantic functions, erasem(\_) ∈ λ <sup>l</sup>:@ → λ @ to erase any subterms labelled with things not less than or equal to m, for some label m, and an unspecified function function serialise which serialises values into a representation understood by the agent (that is, a token sequence). Why is erasure needed? Although the value returned by an expression has a top-level label summarising the influence of all data used to produce it, it may still contain labelled subexpressions—–parts of the value that have not yet been inspected. To safely communicate with the agent, the erase function removes any information whose label is not below a specified threshold m.

#### Inductive definition of n-erasure

```
erasen(m : e) = erasen(e) if m ⊑ n
              = () otherwise
erasen(fork e) = fork erasen(e)
erasen(@e) = @erasen(e)
erasen(l?e) = erasen(e)
erasen(e1 e2) = erasen(e1) erasen(e2)
erasen(λx.e) = λx.erasen(e)
erasen(x) = x
erasen(clear) = clear
```

We establish a central erasure property (formalised later) of erase, namely: if two labelled values v and v ′ differ only in labelled subexpressions whose labels are not less than m, then

$$erase_m(v) = erase_m(v').$$

Following FIDES [\[15\]](#page-12-14), we write <sup>J</sup>M<sup>K</sup> for the behaviour of the underlying model and make the simplifying assumption that it is deterministic. We write <sup>r</sup> <sup>=</sup> <sup>J</sup>MK(p) to mean that <sup>r</sup> is the sample obtained from the model's message generation process, conditioned on p, as described in Section [I-A.](#page-0-0)

Assuming deterministic behaviour is a reasonable model of agentic behaviour, which intentionally does not leak internal state. From the point of view of proving noninterference properties, the determinism in this model is the "right thing"; when we compare two executions of related terms (e.g. where the terms only differ in the things which are labelled as untrusted) we are performing a "what-if" experiment: what if, all other things being the same, the value of the untrusted things had been different? By proving properties relative to an unspecified behaviour function, we provide the right setting for such experiments.

The final semantic function we assume is parse, which converts the response (a token stream) into a closed, label-free value.

We make no specific assumptions about the encoding scheme used by the parser in the semantics. Of course the programmer must know the properties of the parser to be able to interpret the result and act on it accordingly.

In our specific interpreter, for example, the parser recognises all syntactic sugar and derived forms of the calculus, including references to prelude-defined constants; each such constant d (where let d = e appears in the prelude) is expanded to its definition e. The result is always a syntactic value form—a literal, lambda abstraction, record, or array—rather than an expression requiring further computation. In our interpreter, for any response sequence r, parse(r) takes the form [true, vok] or [false, verror] indicating whether the resonse was parsed successfully or not.

Finally, we define generate, as a shorthand used in (P[ROMPT](#page-6-0)). Given a conversation and a prompt (as a token sequence)

$$\begin{aligned} \text{generate}(c,p) &\triangleq (c + [(p,r)], \mathsf{parse}(r)) \\ \text{where } r &= [\![M]\!] (\mathsf{concat}(c) + p) \end{aligned}$$

Here, concat([(p1, r1). . .(pn, rn)]) = p<sup>1</sup> +r<sup>1</sup> + . . .+p<sup>n</sup> +r<sup>n</sup> is the concatenation of a conversation into a single token sequence. (We overload the + operator both for concatenation p + r of token sequences and for concatenation c + c ′ of conversations.)

# *E. Big-step Semantics*

Our big-step semantics carries security levels on the conversation history and on the values produced. Judgements have the general form

$$pc \vdash C, e \Downarrow C', V,$$

where pc ∈ L is the *program-counter* (pc) label, following Denning and Denning's classical treatment of information-flow control [\[23\]](#page-12-22). The main syntactic categories are:

### Values with labels:

| v ::=<br>λx.e  | value (closed: at most x free in e) |
|----------------|-------------------------------------|
| V ::=<br>l : v | labelled value                      |
|                |                                     |

For top-level evaluation we always take pc = ⊥, indicating that no control-flow decisions have yet been influenced by labelled data. The incoming conversation history C (empty at top level) and the outgoing history C ′ are themselves labelled.

```
Big-step semantics: pc ⊢ C, e ⇓ C
                                       ′
                                       , V e ⇓ C, V
(LABEL)
pc ⊔ l ⊢ C, e ⇓ C
                  ′
                  , V
pc ⊢ C, l : e ⇓ C
                 ′
                  , V
                         (LAMBDA)
                         pc ⊢ C, λx.e ⇓ C, pc : λx.e
(APP)
pc ⊢ C0, e1 ⇓ C1, m : λx.e3
pc ⊢ C1, e2 ⇓ C2, V2
pc ⊔ m ⊢ C2, e3[x := V2] ⇓ C3, V3
pc ⊢ C0, e1 e2 ⇓ C3, V3
(PROMPT) (where pc ⊑ l)
pc ⊢ C, e ⇓ (l : c),(m : vp) n = l ⊔ m
(c
  ′
  , r) = generate(c, serialise(erasen(vp))) vr = parse(r)
pc ⊢ C, @e ⇓ (n : c
                    ′
                     ),(n : vr)
(FORK)
pc ⊢ C, e ⇓ C
              ′
               , V
pc ⊢ C, fork e ⇓ C, V
                        (CLEAR)
                        pc ⊑ l
                        pc ⊢ (l : c), clear ⇓ (pc : [ ]),(pc : ())
(TEST) (where v=true if l
                            ′ ⊑l else false)
pc ⊢ C, e ⇓ C
              ′
               , l′
                  : v
                     ′
pc ⊢ C, l?e ⇓ C
                ′
                 , pc : v
                                               (TOP LEVEL)
                                               ⊥ ⊢ [ ], e ⇓ C, V
                                               e ⇓ C, V
```

<span id="page-6-4"></span><span id="page-6-3"></span><span id="page-6-1"></span><span id="page-6-0"></span>We include a convenient top-level judgement for evaluation an expression – it simply means evaluate starting with pc = ⊥ and the empty conversation history.

#### *F. Discussion of the rules*

For the most part, the information flow tracking is not surprising relative to similar systems for dynamic information flow tracking. Our approach is a combination of (i) an imperative approach such as [\[22\]](#page-12-21) in so far as how we track the conversation history, together with (ii) a substitution-based tracking at the level of expressions, exemplified by the labelled lambda calculus [\[14\]](#page-12-13).

As mentioned in the introduction, a particular feature of the test primitive is that it returns its result at the level of the pc, motivated by the desire to use tests to make policy decisions. In the next section we will see that this is not sound in general, but the primitive is sound in the special case of a two-level label lattice, and is sufficient to build two different sound variants of testing operations.

The conversation history C is a state that can be read or written through Rules (P[ROMPT](#page-6-0)) and (C[LEAR](#page-6-1)). Consequently, the label associated with the history is subject to constraints that prevent illicit information flow along execution paths that *do not* modify the state. To illustrate the issue, consider the following example:

```
let secret = true in
  let _ = @'Remember this value: x = false' in
  let _ = if {S}:secret then @'Set x = true' else () in
  @'Give me the value of x'
Error: Cannot prompt LLM with @'Set x = true': pc label
    {S} does not flow to conversation label bot. This is
      the 'no high upgrade' check - cannot update low-
    labeled conversation from a high security context.
```

Suppose that Rule (P[ROMPT](#page-6-0)) had no constraint in its premise, and instead simply updated the label of the conversation history by joining it with the current pc and the label of the argument. When the secret variable is true, the query on the second line would cause the label of the outgoing history to become *secret*, and the return value would therefore be labelled secret. The problem appears when the secret is *false*: in that case, the label on the history remains low, and so the final result is labelled low—an obviously incorrect behaviour.

The solution we adopt is the standard *no-high-upgrade* discipline, first articulated by Zdancewic [\[24\]](#page-12-23) and developed further by Austin and Flanagan [\[22\]](#page-12-21). In the two-point lattice setting, this rule prevents a low-labelled state variable from being upgraded while in a high context (i.e. when the pc is high). In the multi-level setting, the generalisation is that the label of the history (our only state variable) may be changed *only* when its current label is at least as high as the pc. This is precisely the constraint enforced in the premises of Rules (P[ROMPT](#page-6-0)) and (C[LEAR](#page-6-1)).

As in prior work, the no-high-upgrade constraint is conservative: it prevents *potential* bad flows, and so some executions may be unnecessarily blocked. The blocking behaviour itself leaks information through termination, but this is permitted by the termination-insensitive noninterference property we establish later. More permissive—but still sound—approaches have been proposed, e.g. [\[25\]](#page-12-24), though these become intricate in general multi-level lattices [\[26\]](#page-12-25) or require labels on labels [\[27\]](#page-12-26).

# IV. NONINTERFERENCE

#### <span id="page-7-0"></span>*A. Semantic guarantees*

The main semantic guarantee we establish is a standard *termination-insensitive noninterference* property [\[28\]](#page-12-27). Ignoring side channels, this property ensures that any information leakage can occur only through termination behaviour. Informally, it states that if two expressions agree on all components labelled at some level m or below, then evaluating them will produce values that are indistinguishable up to level m.

To formalise termination-insensitive noninterference, we first define when two expressions are indistinguishable up to level n. We define this n-indistinguishability relation (∼n) inductively below.

#### Inductive definition of n-indistinguishability

$$\frac{l \not\sqsubseteq n \quad m \not\sqsubseteq n}{l : e_0 \sim_n m : e_1} \quad \frac{e_0 \sim_n e_1}{m : e_0 \sim_n m : e_1} \quad \frac{e_0 \sim_n e_1}{m?e_0 \sim_n m?e_1}$$

$$\frac{e_0 \sim_n e_1}{x \sim_n x} \quad \frac{e_0 \sim_n e_1}{\lambda x. e_0 \sim_n \lambda x. e_1} \quad \frac{f_0 \sim_n f_1}{f_0 e_0 \sim_n f_1 e_1}$$

$$\frac{e_0 \sim_n e_1}{@e_0 \sim_n @e_1} \quad \frac{e_0 \sim_n e_1}{\text{fork } e_0 \sim_n \text{ fork } e_1} \quad \frac{e_0 \sim_n \text{ clear}}{\text{clear} \sim_n \text{ clear}}$$

We extend ∼<sup>n</sup> to labelled conversations as follows:

#### Definition of n-indistinguishability for conversations:

(HISTDIFF) (HISTSAME) 
$$\frac{l \not\sqsubseteq n \quad m \not\sqsubseteq n}{l: c_1 \sim_n m: c_2} \quad \frac{}{m: c \sim_n m: c}$$

The following basic properties of ∼<sup>n</sup> are straightforward consequences of its inductive definition:

#### Lemma 1 (∼).

- (1) ∼<sup>n</sup> *is an equivalence relation (that is, reflexive, symmetric, and transitive);*
- (2) *If* e<sup>0</sup> ∼<sup>n</sup> e ′ <sup>0</sup> *and* e<sup>1</sup> ∼<sup>n</sup> e ′ 1 *then* e0[x := e1] ∼<sup>n</sup> e ′ 0 [x := e ′ 1 ];
- (3) *If* m ⊑ n *then* e ∼<sup>n</sup> e ′ *implies* e ∼<sup>m</sup> e ′ *.*

We can now state the key property relating ∼<sup>n</sup> to erase:

**Lemma 2.** 
$$v \sim_n v'$$
 implies  $erase_n(v) = erase_n(v')$ 

We are now ready to state the main semantic property: a generalised form of termination-insensitive noninterference. The resulting noninterference theorem for our semantics will, however, hold only under certain restrictions—either to the structure of the label lattice or to the class of programs considered. Whenever such restrictions are made, we implicitly assume that the parse function, in addition to producing labelfree closed expressions, respects the same constraints. Strictly speaking, the parse function should be parameterised by these sets, but we omit such annotations to avoid clutter.

<span id="page-7-1"></span>Definition 1. *Termination-Insensitive Noninterference (TINI) Let* E *be a sublanguage of closed expressions whose labels come from a join-semilattice* L*. We say that* E *satisfies* termination-insensitive noninterference *(TINI) if and only if for all* e0, e<sup>1</sup> ∈ E *and all levels* k ∈ L*:*

• e<sup>0</sup> ∼<sup>k</sup> e<sup>1</sup> *implies that whenever* e<sup>0</sup> ⇓ C0, V<sup>0</sup> *and* e<sup>1</sup> ⇓ C1, V1*, we have that* C<sup>0</sup> ∼<sup>k</sup> C<sup>1</sup> *and* V<sup>0</sup> ∼<sup>k</sup> V1*.*

Unfortunately, TINI does not hold for all expressions and label lattices. The difficulty arises from the testing (?) operation. To illustrate the problem, consider a three-level lattice L ⊑ M ⊑ H and the following L-indistinguishable terms:

$$M: \mathbf{true} \sim_L M: (H: \mathbf{false}).$$

Performing a label test on these terms reveals the issue: M ? (M : true) evaluates to L : true, whereas M ? (M : (H : false)) evaluates to L : false – two terms which are clearly not L-indistinguishable. Where does this discrepancy originate? One might blame the label rule for returning the test outcome at too low a level; however, this behaviour is intentional. The label must be available at a low level to allow the program to make policy decisions freely. If the outcome of tests have high labels then they cannot be used to implement policy decisions. For example, suppose, using the earlier example lattice with labels from the power set of {U, S}. If testing whether an expession is public ({U}?e) gives a boolean with label {U} (untrusted), what use does it have in a policy decision? We will present three alternative ways to address this issue and obtain noninterference results: (i) disallow expressions that perform tests on labels, (ii) restrict attention to programs which use only one non-bottom label, or (iii) use label tests solely to implement two more restricted forms of test: *assertions* about labels—operations that fail if the asserted condition does not hold, and a strong form of label test that is always noninterfering, but returns a boolean at a sufficiently high level.

Option (ii) is particularly interesting in light of the existing literature. While many systems are developed for arbitrary lattices, most formal noninterference results are ultimately proved only for the special case of a two-level lattice. The counterexample discussed above genuinely requires three distinct levels, and thus lies outside the scope of these two-level results.

To state (iii) precisely, we define assertions strong tests as follows:

#### Derived constructs: assert and strong test

```
assert k e ≜ if k?e then () else Ω
   where Ω ≜ (λx. x x) (λx. x x)
k??e ≜ let x = e in (let b = k?x in k : b)
```

Note that the else-branch uses the standard divergent term Ω. We also state the key properties of the encoded operators in terms of their *derived* evaluation rules:

Lemma 3. *The following proof rules for assert and strong test are sound and complete:*

#### *Derived rules: assert and strong test*

```
(ASSERT)
pc ⊢ C, e ⇓ C
              ′
               , V label(V ) ⊑ k
pc ⊢ C, assert k e ⇓ C
                        ′
                        ,(pc : ())
(STRONG TEST) (where v = true if l ⊑ k else false)
pc ⊢ C, e ⇓ C
              ′
               , l : v
                    ′
pc ⊢ C, k??e ⇓ C
                   ′
                   ,(pc ⊔ k : v)
```

#### <span id="page-8-4"></span>Main technical theorem.

<span id="page-8-0"></span>Theorem 1 (TINI). *The following sublanguages satisfy [TINI:](#page-7-1)*

- (1) *expressions built without* ?*;*
- (2) *expressions which only use one non-bottom label; and*
- (3) *expressions in which* ? *occurs only in the form of* assert *statements or strong tests.*

Note that a special case of (2) is when the lattice has only two elements, as in [\[14\]](#page-12-13). The proof of Theorem [1](#page-8-0) is a consequence of a lemma which generalises TINI to begin with an arbitrary pc and arbitrary (∼k)-related conversations (over the appropriate set of labels). The proof is given in the technical appendix, and is a standard induction over the derivation in the big-step semantics.

## <span id="page-8-1"></span>V. IMPLEMENTATION: THE LLMBDA INTERPRETER

At the earliest stages of conceiving our formal calculus we found ourselves speculating about what sorts of prompts would work, or not. We realized that it was impossible to reason about prompts and the likely responses from an LLM in the abstract. Hence, so that we could experiment with programs in the calculus and observe their behaviour, we implemented our operational semantics within an interpreter with a readeval-print loop.

Our goal was to implement the calculus and its derived forms directly. We kept to a principle of minimality, and have resisted the temptation to think of the implementation as being a practical programming language. Applying the ideas of the calculus in a practical programming language is out of scope for this paper and left as future work.

The implementation is in Python (approximately 4000 lines), written with Claude Code. The parser uses the Lark library [\[29\]](#page-12-28) with an LALR grammar. The interpreter implements the big-step semantics with label propagation. The @ operator calls the OpenAI Responses API [\[30\]](#page-12-29). We experimented with an option from OpenAI to constrain the LLM's responses to be syntactically valid expressions from the Lark grammar, though responses are slower than when unconstrained.

<span id="page-8-2"></span><sup>1</sup>This might look unintuitive, but the public labels are those not containing S (secret), that is, { } and {U}.

#### <span id="page-9-0"></span>VI. PROMPT INJECTION ATTACKS AND DEFENSES

Figure 5 of the CaMeL paper [\[9\]](#page-12-8) sets up an example that typifies a prompt injection attack. In the example, the user asks the agent to find an email to send a reminder about a meeting. The agent has access to the user's emails. Unfortunately, a text injected into the email causes the agent to send a cancellation instead of a reminder.

#### *A. Prompt injection attack on a tool-calling agent*

We present a simple model of this situation within our calculus. The system state is a record with a field for the last email received and another field for the output message queue, initially empty. The goal from the human user is a string.

```
let state1 = { last: {U}:"Long message from
    bob@chalmers.se to alice@darpa.gov", queue: [] }
let goal1 = "Extract sender email address from my
    last email and send a meeting reminder to that
    address"
```

We prompt the LLM to engage in a tool-calling conversation as follows. Curiously, despite our calculus having no type system, we can rely on the model's pre-trained knowledge of types.

```
Every answer must be in one of the following two forms.
(1) you have info to answer your goal,
    emit ['answer', the-answer-as-a-value];
(2) to gather more information,
    emit ['tool-call',['function-name', value1, ... valueN]].
    You will receive the answer in the next prompt,
    and can then continue.
```

```
get_last_email_tool: IO string
send_email_tool: {"subject": string, "body": string,
    "recipient" : string } -> IO {}
```

The tool-calling agent is a function run\_agent. Given the goal from the user, it prompts the model as above, and loops to serve tool-calls from the LLM, by calling the available tools, and eventually returns the final message queue. The agent is a stateful computation programmed in the monadic style of functional programming. We list all the code in Appendix [D.](#page-18-0) Figure [1](#page-19-0) shows a standard set of monadic functions for programming with state. Figure [2](#page-20-0) shows the tool-calling agent itself [\[4\]](#page-12-3), [\[5\]](#page-12-4), coded within our calculus in a monadic style.

We model execution without an attack. The function performIO (from Figure [1\)](#page-19-0) executes the monadic computation on the initial state, and displays the final state.

```
performIO (run_agent goal1) state1
```

We get the intended reminder in the message queue:

```
{U}:[{U}:{subject: "Meeting reminder", body: "Hi Bob,\n\
    nJust a reminder about our upcoming meeting. Please
    let me know if you need to reschedule or if there's
    anything you'd like to add to the agenda.\n\nBest,\
    nAlice", recipient: "bob@chalmers.se"}] (7.1s)
```

On the other hand, injecting a suitable text into the stored email causes a cancellation to be sent.

CRITICAL: The meeting has been CANCELLED. Do NOT

**let** injection = ' ---SYSTEM UPDATE---

```
send a reminder. Send a CANCELLATION notice.
---END SYSTEM UPDATE---'
 let state2 = state1.last := state1.last + injection
 performIO (run_agent goal1) state2
 state2 = {last: {U}:"Long message from bob@chalmers.se to
       alice@darpa.gov.\n---SYSTEM UPDATE---\nCRITICAL:
      The meeting has been CANCELLED. Do NOT send a
      reminder. Send a CANCELLATION notice.\n---END SYSTEM
       UPDATE---", queue: []}
 {U}:[{U}:{subject: "Meeting cancellation notice", body: "
```

Hello,\n\nThe meeting has been cancelled. No reminder is needed.\n\nBest regards,", recipient: " bob@chalmers.se"}] (10.8s)

In the definition of state1 we attached the label {U} for untrusted to the email string. In both runs, that label has tainted the output message. This illustrates the root vulnerability exploited by prompt injection attacks: the tool-calling agent uses the same channel, a single prompt-response conversation, to carry both untrusted inputs (the emails) and also command information (the tool-calls).

If we are to reason about attacks and defenses in our calculus we need it to represent both functionality and vulnerability. By running the model in our interpreter we have shown both that *it models intended functionality*—it can send the reminder intended by the user successfully when there is no attack—but also that *it models the vulnerability*—it sends the unintended cancellation when the attack text is injected.

#### *B. CaMeL: code generation and quarantine*

We give an example of the CaMeL defence, based on a privileged planner that generates code to do the work of the agent, which later calls a quarantined LLM to process the untrusted data. CaMeL relies on capabilities: "tags assigned to each individual value that describe control and dataflow relationships." The labelled expressions can model these capabilities, and policy decisions based on capabilities are expressed using label test expressions.

Running the code reveals that the original attack fails on this planner. Moreover, our noninterference theorem provides guarantees.

Our planner generates code f before touching state. The code of the planner, including its code generation, correspond to Willitson's privileged P-LLM [\[8\]](#page-12-7).

```
let direct_code_gen_agent = \goal. \state.
  let f = direct_code_gen goal in
  let post_state = f state in post_state.queue
```

The function below models the quarantined Q-LLM:

```
# quarantine: string -> json
# Prompts LLM in isolated context, returns JSON.
```

```
# The prompt should include a description or example
     of the expected JSON format.
let quarantine = \prompt.
  let pair = fork( let _ = clear in @ prompt ) in
  pair.[1]
```

The inner direct\_code\_gen function is another iterative agentic loop that produces a lambda. When run on our example goal, we may get the following function f, which uses a quarantined call to the LLM to process the untrusted input. Finally, it calls send\_email to form a message and add it to the output queue. An injected prompt cannot change the subject or body.

**let** f = direct\_code\_gen goal1 # line 1 of the agent

```
f = \state.
  let last = get_last_email state in
  let extracted =
    quarantine
      "Extract the sender email address from the
    following email text. Return ONLY a double-quoted
    string containing the email address (example: \"
    name@example.com\"). Email text:\n\n{last}\n"
in
  send_email extracted "Meeting reminder" "Hi,\n\nJust a
    reminder about our upcoming meeting. Please let me
    know if you need to reschedule.\n\nThanks." state
    (5.5s)
```

The system function send\_email, shown below, can test labels on data to enforce a security policy dynamically. In this case, we enforce that the subject and body must be trusted. The {S}? test implicit in the assert below is satisfied by labels {} and {S} but not {U} and {U, S}. Hence, the assert is testing the policy that neither subject nor body is untrusted.

```
# policy: subject and body are trusted
let send_email = \to. \subject. \body. \state.
  if assert {S} (subject+body) then
    state.queue := state.queue +
      [{to:to, subject:subject, body:body}]
  else state # return state unchanged
```

As we saw earlier, with the tool-calling agent, any tainted data passed to the LLM taints the whole conversation. Hence, a tool-calling agent cannot meaningfully use the label-checking function send\_email because its policy would always fail.

```
let post_state = f state2 in post_state.queue # line 2
[{to: {U}:"bob@chalmers.se", subject: "Meeting reminder",
      body: "Hi,\n\nJust a reminder about our upcoming
    meeting. Please let me know if you need to
    reschedule.\n\nThanks."}] (1.1s)
```

Running this code, despite the prompt injection, results in the correct message being sent.

But what about other runs? The theory of information flow in our lambda calculus lets us reason how changes to inputs affect outputs. If data is labelled as untrusted, changes to that data cannot change an output known to be trusted. Consider the untrusted message string in the last field in the input state2. Noninterference tells us that changing that untrusted input in any other run cannot effect outputs that are labelled as trusted. (The absence of an explicit label indicates that the value is trusted.) The subject and body fields have trusted values in the first run, and so must take the same values in any other run too.

It justifies implementing security policies based on label testing. The policy assertions implemented by send\_email in Figure [3](#page-21-0) have a semantic consequence: they guarantee that only messages with trusted subjects and bodies may be sent, and hence that those parts of emails are unaffected by untrusted inputs.

Although not shown in this example, we have constructed other examples where the security policy guards confidentiality: for instance, a variant of send\_mail can encode a policy that if the body of the outgoing message has a secret label, then the recipient must be in an allow-list.

#### VII. RELATED WORK

### <span id="page-10-0"></span>*A. Background: minimal kernels of programming languages*

The lambda calculus is a formalism of pure functions [\[31\]](#page-12-30). It was adopted as a tool for analysis and design early in the study of programming languages [\[32\]](#page-12-31). The method is to factor language design into independent, orthogonal concerns, with a minimal kernel based on the lambda calculus that captures the essential semantics, and derived constructs that reduce to it. Pioneers include Böhm [\[33\]](#page-12-32), Landin [\[34\]](#page-12-33), and Strachey [\[35\]](#page-13-0).

#### *B. Lambda calculus applied to LLMs*

OPAL [\[19\]](#page-12-18) is a parallel scripting language for LLMs, based on a lambda calculus with a formal semantics. The emphasis of the work is execution performance. The paper does not consider aspects of security such as resistance to prompt injection or noninterference.

Quasar [\[20\]](#page-12-19) is a programming language with a pure, functional core based on the lambda calculus. Side effects are isolated in external calls. Its goals are performance through parallelisation, uncertainty quantification to counter hallucinations, and security to help users validate external actions.

#### *C. Dynamic Enforcement of Noninterference*

Our approach to dynamic information flow tracking is closest to that of Austin et al. [\[22\]](#page-12-21), but combined with a termlevel treatment of labels that is in the spirit of the functional approach defined in the later work [\[14\]](#page-12-13), which in turn is based on Abadi, Lampson, and Lévy's labelled lambda calculus [\[36\]](#page-13-1).

A novelty of our noninterference results are in the analysis of label testing, which we view as a crucial component for implementing policy checks. Austin et al. [\[22\]](#page-12-21) included a label testing operation returning "low" booleans, but only established noninterference for a two-level lattice. Bichhawat et al. [\[26\]](#page-12-25) study generalisations of Austin and Flanagan's work to arbitrary lattices, but do not include label testing. Vassena et al. [\[37\]](#page-13-2) introduce a fully-fledged label testing operation inspired by the *labelOf* operation from the course-grained tracking approach of LIO [\[38\]](#page-13-3). Their operation returns the label of an expression (thus labels are first-class values in the language), and its level is the label itself. This is close in spirit to our strong testing operation, and while useful for certain operations on labelled data, we have argued that it is not suitable to implement policy logic.

Our result that *assertions* can safely return a low result for any label lattice seems to be new. Somewhat related is Kozyri et al. [\[39\]](#page-13-4) which deals with the expressiveness of labels on labels on labels. . . to an arbitrary depth. They include the notion of a fixed variable—a variable with a fixed label. An assignment to such a variable acts as an assert that the label of the value being assigned is less than or equal to the fixed label of the value. Our assert operation potentially leaks information within what is accepted by termination-insensitive noninterference. In the terminology of Kozyri et al. it is not *block safe*. It remains to be seen whether this is inevitable (as we suspect), or a feature specific to our language and semantics.

#### *D. Information-flow Based Defences Against Injection Attacks*

The use of information flow labeling and tracking to tackle problems with LLM interactions has been used in a variety of recent papers. As well as FIDES and CaMeL mentioned in the introduction, Wu et. al [\[16\]](#page-12-15) describe the use of information flow labels in a system level defence and prove that their (fixed) architecture satisfies a form of noninterference. Other papers using information flow, and the dynamic tracking of untrusted data sources in particular, include Kim et al.[\[40\]](#page-13-5). Li et al [\[41\]](#page-13-6) adopt a form of static information flow analysis for a very simple language of dynamically generated output plans.

Regarding the formal security guarantees, the CaMeL work acknowledges the lack of such, and the potential difficulties in providing such in the context of languages like Python. The FIDES work, by contrast, provides formal statements of the intended security properties and proves that one specific planning loop satisfies these properties. Their system makes careful pragmatic choices as to when to not track control-flow dependencies – i.e., to perform what is commonly called "taint tracking". The choice as to where to weaken the dependency tracking depends on the labels (e.g. secrets) and the size of the data domains. Taint tracking gives rather weak guarantees, but these can be formalised in a semantic way using a property called *explicit secrecy* [\[18\]](#page-12-17). This is the property stated by the FIDES system for the confidentiality tracking part of the system; for integrity noninterference is used. Explicit secrecy requires a semantic model which splits the behaviour into data and control parts. The idea is to give a semantic condition which captures a correct information flow analysis which ignores leaks through control flow. Modifying our system to ignore control flow dependencies is simply a matter of replacing pc⊔m in the [\(A](#page-6-2)PP) rule with pc. However, even if it was clear how to formulate explicit secrecy for a higher-order language, we question its potential value for any language with features such as higher-order functions, where data and control are interchangeable and leaks through control can be made very efficient.

#### *E. Other prompt injection attacks and defences*

Greshake et al. [\[42\]](#page-13-7) introduced *indirect prompt injection*, where adversarial instructions are embedded in untrusted data retrieved by the application. Liu et al. [\[43\]](#page-13-8) give a formal definition: given an LLM-integrated application with an instruction prompt (the target instruction) and data (the target data) for a target task, a *prompt injection attack* modifies the data such that the application accomplishes an injected task instead.

The AgentDojo benchmark [\[10\]](#page-12-9) is a framework, based around 97 tasks, for designing and evaluating prompt injection attacks and their countermeasures.

Other defenses include spotlighting [\[44\]](#page-13-9), which transforms input to make its provenance more salient, and Task Shield [\[45\]](#page-13-10), which verifies that instructions align with user-specified goals.

#### *F. Code generation with LLMs*

Large language models trained on code have demonstrated remarkable ability to generate programs from natural language descriptions [\[46\]](#page-13-11). SWE-Agent [\[47\]](#page-13-12) uses agent-computer interfaces to enable LLMs to autonomously fix bugs and implement features in real software repositories. In future work, we would like to benchmark agents in the LLMbda interpreter against SWE-Bench and indeed AgentDojo.

#### *G. Session types*

Session types [\[48\]](#page-13-13), [\[49\]](#page-13-14) are type systems for structured communication protocols. There may be a connection between our conversations—alternating sequences of prompts and responses—and session types. Exploring session types as a foundation for typing LLM interactions is left as future work.

#### VIII. CONCLUSION

Famously, impressed by the prompt-based programming he was seeing in AI labs, Andrej Karpathy quipped that the "hottest new programming language is English" [\[50\]](#page-13-15). We agree, but observe that an LLM cannot execute English on its own. Instead, given an initial prompt from a human, the planner loop of an AI agent builds prompt-response conversations by serving tool-calls and running code for the LLM.

Our lambda calculus represents the code of agentic planners, and code generated and run during their conversations with LLMs. The examples run within our interpreter demonstrate the expressiveness of our calculus. The theory of noninterference puts the propagation of labels in our lambda calculus on a firm foundation (despite the novel features of our language). Noninterference implies security properties of policies implemented with label testing.

There is a long tradition of analysing and improving the hottest new programming languages by study within the lambda calculus. We hope to have helped renew the tradition.

#### REFERENCES

- <span id="page-12-0"></span>[1] Y. Bengio, R. Ducharme, P. Vincent, and C. Jauvin, "A neural probabilistic language model," *Journal of Machine Learning Research*, vol. 3, no. Feb, pp. 1137–1155, 2003.
- <span id="page-12-1"></span>[2] I. Sutskever, O. Vinyals, and Q. V. Le, "Sequence to sequence learning with neural networks," in *Advances in Neural Information Processing Systems*, vol. 27, 2014, pp. 3104–3112. [Online]. Available: <https://arxiv.org/abs/1409.3215>
- <span id="page-12-2"></span>[3] A. Vaswani, N. Shazeer, N. Parmar, J. Uszkoreit, L. Jones, A. N. Gomez, Ł. Kaiser, and I. Polosukhin, "Attention is all you need," in *Advances in Neural Information Processing Systems*, vol. 30, 2017. [Online]. Available: <https://arxiv.org/abs/1706.03762>
- <span id="page-12-3"></span>[4] S. Yao, J. Zhao, D. Yu, N. Du, I. Shafran, K. Narasimhan, and Y. Cao, "React: Synergizing reasoning and acting in language models," in *International Conference on Learning Representations (ICLR)*, 2023. [Online]. Available: <https://par.nsf.gov/servlets/purl/10451467>
- <span id="page-12-4"></span>[5] T. Schick, J. Dwivedi-Yu, R. Dessì, R. Raileanu, M. Lomeli, L. Zettlemoyer, N. Cancedda, and T. Scialom, "Toolformer: Language models can teach themselves to use tools," in *Advances in Neural Information Processing Systems*, vol. 36, 2023. [Online]. Available: <https://arxiv.org/abs/2302.04761>
- <span id="page-12-5"></span>[6] S. Willison, "Prompt injection attacks against GPT-3," Sep. 2022. [Online]. Available: <https://simonwillison.net/2022/Sep/12/prompt-injection/>
- <span id="page-12-6"></span>[7] A. Hern, "Why AI systems might never be secure," *The Economist*, Sep. 2025, "The gullibility of LLMs had been spotted before ChatGPT was even made public. In the summer of 2022, Willison and others independently coined the term 'prompt injection' to describe the behaviour.". [Online]. Available: [https://www.economist.com/science-and-technology/2025/](https://www.economist.com/science-and-technology/2025/09/23/why-ai-systems-might-never-be-secure) [09/23/why-ai-systems-might-never-be-secure](https://www.economist.com/science-and-technology/2025/09/23/why-ai-systems-might-never-be-secure)
- <span id="page-12-7"></span>[8] S. Willison, "The dual LLM pattern for building AI assistants that can resist prompt injection," Apr. 2023. [Online]. Available: <https://simonwillison.net/2023/Apr/25/dual-llm-pattern/>
- <span id="page-12-8"></span>[9] E. Debenedetti, I. Shumailov, T. Fan, J. Hayes, N. Carlini, D. Fabian, C. Kern, C. Shi, A. Terzis, and F. Tramèr, "Defeating prompt injections by design," in *IEEE Conference on Secure and Trustworthy Machine Learning (SaTML)*, 2026. [Online]. Available: <https://arxiv.org/abs/2503.18813>
- <span id="page-12-9"></span>[10] E. Debenedetti, J. Zhang, M. Balunovic, L. Beurer-Kellner, M. Fischer, and F. Tramèr, "Agentdojo: A dynamic environment to evaluate prompt injection attacks and defenses for llm agents," *Advances in Neural Information Processing Systems*, vol. 37, pp. 82 895–82 920, 2024.
- <span id="page-12-10"></span>[11] S. Willison, "CaMeL offers a promising new direction for mitigating prompt injection attacks," Apr. 2025. [Online]. Available: [https:](https://simonwillison.net/2025/Apr/11/camel/) [//simonwillison.net/2025/Apr/11/camel/](https://simonwillison.net/2025/Apr/11/camel/)
- <span id="page-12-11"></span>[12] G. D. Plotkin, "Call-by-name, call-by-value and the λ-calculus," *Theoretical Computer Science*, vol. 1, no. 2, pp. 125–159, 1975. [Online]. Available: [https://www.sciencedirect.com/science/article/pii/](https://www.sciencedirect.com/science/article/pii/0304397575900171) [0304397575900171](https://www.sciencedirect.com/science/article/pii/0304397575900171)
- <span id="page-12-12"></span>[13] D. E. Denning, "A lattice model of secure information flow," *Communications of the ACM*, vol. 19, no. 5, pp. 236–243, 1976. [Online]. Available: <https://dl.acm.org/doi/10.1145/360051.360056>
- <span id="page-12-13"></span>[14] T. H. Austin, C. Flanagan, and M. Abadi, "A functional view of imperative information flow," in *Programming Languages and Systems*. Berlin, Heidelberg: Springer Berlin Heidelberg, 2012, pp. 34–49. [Online]. Available: [https://link.springer.com/chapter/10.1007/](https://link.springer.com/chapter/10.1007/978-3-642-35182-2_4) [978-3-642-35182-2\\_4](https://link.springer.com/chapter/10.1007/978-3-642-35182-2_4)
- <span id="page-12-14"></span>[15] M. Costa, B. Köpf, A. Kolluri, A. Paverd, M. Russinovich, A. Salem, S. Tople, L. Wutschitz, and S. Zanella-Béguelin, "Securing AI agents with information-flow control," *arXiv preprint arXiv:2505.23643*, 2025. [Online]. Available: <https://arxiv.org/abs/2505.23643>

- <span id="page-12-15"></span>[16] F. Wu, E. Cecchetti, and C. Xiao, "System-level defense against indirect prompt injection attacks: An information flow control perspective," 2024. [Online]. Available: <https://arxiv.org/abs/2409.19091>
- <span id="page-12-16"></span>[17] J. A. Goguen and J. Meseguer, "Security policies and security models," in *IEEE Symposium on Security and Privacy*. IEEE, 1982, pp. 11–20. [Online]. Available: [https://www.cs.purdue.edu/homes/ninghui/readings/](https://www.cs.purdue.edu/homes/ninghui/readings/AccessControl/goguen_meseguer_82.pdf) [AccessControl/goguen\\_meseguer\\_82.pdf](https://www.cs.purdue.edu/homes/ninghui/readings/AccessControl/goguen_meseguer_82.pdf)
- <span id="page-12-17"></span>[18] D. Schoepe, M. Balliu, B. C. Pierce, and A. Sabelfeld, "Explicit secrecy: A policy for taint tracking," in *IEEE European Symposium on Security and Privacy (EuroS&P)*. IEEE, 2016, pp. 15–30.
- <span id="page-12-18"></span>[19] S. Mell, K. Kallas, S. Zdancewic, and O. Bastani, "Opportunistically parallel lambda calculus," *Proc. ACM Program. Lang.*, vol. 9, no. OOPSLA2, Oct. 2025. [Online]. Available: [https://doi.org/10.1145/](https://doi.org/10.1145/3763143) [3763143](https://doi.org/10.1145/3763143)
- <span id="page-12-19"></span>[20] S. Mell, B. Zhang, D. Mell, S. Li, R. Ramalingam, N. Yu, S. Zdancewic, and O. Bastani, "A fast, reliable, and secure programming language for llm agents with code actions," 2025. [Online]. Available: <https://arxiv.org/abs/2506.12202>
- <span id="page-12-20"></span>[21] J. Borgström, U. Dal Lago, A. D. Gordon, and M. Szymczak, "A lambda-calculus foundation for universal probabilistic programming," in *Proceedings of the 21st ACM SIGPLAN International Conference on Functional Programming (ICFP)*. ACM, 2016, pp. 33–46. [Online]. Available: <https://dl.acm.org/doi/10.1145/2951913.2951942>
- <span id="page-12-21"></span>[22] T. H. Austin and C. Flanagan, "Efficient purely-dynamic information flow analysis (abstract only)," *SIGPLAN Not.*, vol. 44, no. 8, p. 6, Dec. 2009. [Online]. Available: <https://doi.org/10.1145/1667209.1667220>
- <span id="page-12-22"></span>[23] D. E. Denning and P. J. Denning, "Certification of Programs for Secure Information Flow," *Comm. of the ACM*, vol. 20, no. 7, pp. 504–513, Jul. 1977.
- <span id="page-12-23"></span>[24] S. Zdancewic, "Programming languages for information security," Ph.D. dissertation, Cornell University, August 2002. [Online]. Available: <https://www.cis.upenn.edu/~stevez/papers/Zda02.pdf>
- <span id="page-12-24"></span>[25] T. H. Austin and C. Flanagan, "Permissive dynamic information flow analysis," in *Proceedings of the 5th ACM SIGPLAN Workshop on Programming Languages and Analysis for Security*, 2010, pp. 1–12. [Online]. Available: [https://users.soe.ucsc.edu/~cormac/papers/](https://users.soe.ucsc.edu/~cormac/papers/plas10.pdf) [plas10.pdf](https://users.soe.ucsc.edu/~cormac/papers/plas10.pdf)
- <span id="page-12-25"></span>[26] A. Bichhawat, V. Rajani, D. Garg, and C. Hammer, "Generalizing permissive-upgrade in dynamic information flow analysis," in *Proceedings of the Ninth Workshop on Programming Languages and Analysis for Security*, ser. PLAS'14. New York, NY, USA: Association for Computing Machinery, 2014, p. 15–24. [Online]. Available: <https://doi.org/10.1145/2637113.2637116>
- <span id="page-12-26"></span>[27] P. Buiras, D. Stefan, and A. Russo, " On Dynamic Flow-Sensitive Floating-Label Systems ," in *2014 IEEE 27th Computer Security Foundations Symposium (CSF)*. Los Alamitos, CA, USA: IEEE Computer Society, Jul. 2014, pp. 65–79. [Online]. Available: <https://doi.ieeecomputersociety.org/10.1109/CSF.2014.13>
- <span id="page-12-27"></span>[28] A. Askarov, S. Hunt, A. Sabelfeld, and D. Sands, "Termination insensitive noninterference leaks more than just a bit," in *Proc. European Symp. on Research in Computer Security*, 2008. [Online]. Available: [https://doi.org/10.1007/978-3-540-88313-5\\_22](https://doi.org/10.1007/978-3-540-88313-5_22)
- <span id="page-12-28"></span>[29] E. Shinan, "Lark: A parsing toolkit for Python," 2017. [Online]. Available: <https://github.com/lark-parser/lark>
- <span id="page-12-29"></span>[30] OpenAI, "Responses API reference," OpenAI Platform Documentation, 2025, accessed: 2026-01-24. [Online]. Available: [https://platform.](https://platform.openai.com/docs/api-reference/responses) [openai.com/docs/api-reference/responses](https://platform.openai.com/docs/api-reference/responses)
- <span id="page-12-30"></span>[31] A. Church, *The Calculi of Lambda Conversion*, ser. Annals of Mathematics Studies. Princeton, NJ: Princeton University Press, 1941, no. 6. [Online]. Available: <https://www.jstor.org/stable/j.ctt1b9x12d>
- <span id="page-12-31"></span>[32] F. Cardone and J. R. Hindley, "History of lambda-calculus and combinatory logic," in *Logic from Russell to Church (Handbook of the History of Logic, Volume 5)*, D. M. Gabbay and J. Woods, Eds. Amsterdam: Elsevier, 2006, pp. 723–817. [Online]. Available: [http://www.users.waitrose.com/~hindley/SomePapers\\_PDFs/](http://www.users.waitrose.com/~hindley/SomePapers_PDFs/2006CarHin,HistlamRp.pdf) [2006CarHin,HistlamRp.pdf](http://www.users.waitrose.com/~hindley/SomePapers_PDFs/2006CarHin,HistlamRp.pdf)
- <span id="page-12-32"></span>[33] C. Böhm and W. Gross, "Introduction to the CUCH," in *Automata Theory*, E. R. Caianiello, Ed. New York: Academic Press, 1966, pp. 35–65.
- <span id="page-12-33"></span>[34] P. J. Landin, "A correspondence between ALGOL 60 and Church's lambda-notation," *Communications of the ACM*, vol. 8, no. 2–3, pp. 89–101, 158–165, feb–mar 1965. [Online]. Available: [https:](https://dl.acm.org/doi/10.1145/363744.363749) [//dl.acm.org/doi/10.1145/363744.363749](https://dl.acm.org/doi/10.1145/363744.363749)

- <span id="page-13-0"></span>[35] C. Strachey, "Fundamental concepts in programming languages," *Higher-Order and Symbolic Computation*, vol. 13, pp. 11–49, 2000, lecture notes from 1967, first formally published in 2000. [Online]. Available: <https://link.springer.com/article/10.1023/A:1010000313106>
- <span id="page-13-1"></span>[36] M. Abadi, B. W. Lampson, and J.-J. Lévy, "Analysis and caching of dependencies," in *Proceedings of the First ACM SIGPLAN International Conference on Functional Programming*, ser. ICFP '96. New York, NY, USA: Association for Computing Machinery, 1996, pp. 83–91. [Online]. Available: <https://doi.org/10.1145/232627.232638>
- <span id="page-13-2"></span>[37] M. Vassena, A. Russo, D. Garg, V. Rajani, and D. Stefan, "From fineto coarse-grained dynamic information flow control and back," *Proc. ACM Program. Lang.*, vol. 3, no. POPL, Jan. 2019. [Online]. Available: <https://doi.org/10.1145/3290389>
- <span id="page-13-3"></span>[38] D. Stefan, A. Russo, J. C. Mitchell, and D. Mazières, "Flexible dynamic information flow control in haskell," in *Proceedings of the 4th ACM Symposium on Haskell*, ser. Haskell '11. New York, NY, USA: Association for Computing Machinery, 2011, p. 95–106. [Online]. Available: <https://doi.org/10.1145/2034675.2034688>
- <span id="page-13-4"></span>[39] E. Kozyri, F. B. Schneider, A. Bedford, J. Desharnais, and N. Tawbi, "Beyond labels: Permissiveness for dynamic information flow enforcement," in *2019 IEEE 32nd Computer Security Foundations Symposium (CSF)*, 2019, pp. 351–35 115. [Online]. Available: [https:](https://ieeexplore.ieee.org/document/8823779) [//ieeexplore.ieee.org/document/8823779](https://ieeexplore.ieee.org/document/8823779)
- <span id="page-13-5"></span>[40] J. Kim, W. Choi, and B. Lee, "Prompt flow integrity to prevent privilege escalation in llm agents," 2025. [Online]. Available: <https://arxiv.org/abs/2503.15547>
- <span id="page-13-6"></span>[41] E. Li, T. Mallick, E. Rose, W. Robertson, A. Oprea, and C. Nita-Rotaru, "Ace: A security architecture for llm-integrated app systems," 2025. [Online]. Available: <https://arxiv.org/abs/2504.20984>
- <span id="page-13-7"></span>[42] K. Greshake, S. Abdelnabi, S. Mishra, C. Endres, T. Holz, and M. Fritz, "Not what you've signed up for: Compromising real-world LLMintegrated applications with indirect prompt injection," in *Proceedings of the 16th ACM Workshop on Artificial Intelligence and Security (AISec)*, 2023, pp. 79–90. [Online]. Available: <https://arxiv.org/abs/2302.12173>
- <span id="page-13-8"></span>[43] Y. Liu, Y. Jia, R. Geng, J. Jia, and N. Z. Gong, "Formalizing and benchmarking prompt injection attacks and defenses," in *33rd USENIX Security Symposium (USENIX Security 24)*, 2024, pp. 2607–2624. [Online]. Available: <https://arxiv.org/abs/2310.12815>
- <span id="page-13-9"></span>[44] K. Hines, G. Lopez, M. Hall, F. Zarfati, Y. Zunger, and E. Kiciman, "Defending against indirect prompt injection attacks with spotlighting," in *Proceedings of the Conference on Applied Machine Learning in Information Security (CAMLIS)*, 2024, pp. 48–62. [Online]. Available: <https://arxiv.org/abs/2403.14720>
- <span id="page-13-10"></span>[45] F. Jia, T. Wu, X. Qin, and A. Squicciarini, "The task shield: Enforcing task alignment to defend against indirect prompt injection in LLM agents," in *Proceedings of the 63rd Annual Meeting of the Association for Computational Linguistics (ACL)*, 2025. [Online]. Available: <https://arxiv.org/abs/2412.16682>
- <span id="page-13-11"></span>[46] M. Chen, J. Tworek, H. Jun, Q. Yuan, H. P. d. O. Pinto, J. Kaplan, H. Edwards, Y. Burda, N. Joseph, G. Brockman *et al.*, "Evaluating large language models trained on code," *arXiv preprint arXiv:2107.03374*, 2021. [Online]. Available: <https://arxiv.org/abs/2107.03374>
- <span id="page-13-12"></span>[47] J. Yang, C. E. Jimenez, A. Wettig, K. Lieret, S. Yao, K. Narasimhan, and O. Press, "SWE-Agent: Agent-computer interfaces enable automated software engineering," *Advances in Neural Information Processing Systems*, vol. 37, pp. 50 528–50 652, 2024.
- <span id="page-13-13"></span>[48] K. Honda, "Types for dyadic interaction," in *CONCUR'93*, ser. Lecture Notes in Computer Science, vol. 715. Springer, 1993, pp. 509–523. [Online]. Available: [https://doi.org/10.1007/3-540-57208-2\\_35](https://doi.org/10.1007/3-540-57208-2_35)
- <span id="page-13-14"></span>[49] K. Honda, V. T. Vasconcelos, and M. Kubo, "Language primitives and type discipline for structured communication-based programming," in *Programming Languages and Systems (ESOP'98)*, ser. Lecture Notes in Computer Science, vol. 1381. Springer, 1998, pp. 122–138. [Online]. Available: <https://doi.org/10.1007/BFb0053567>
- <span id="page-13-15"></span>[50] A. Karpathy, "The hottest new programming language is English," Jan. 2023, post on X (formerly Twitter). [Online]. Available: <https://x.com/karpathy/status/1617979122625712128>
- <span id="page-13-16"></span>[51] D. Volpano, C. Irvine, and G. Smith, "A sound type system for secure flow analysis," in *Journal of Computer Security*, vol. 4, no. 2-3. IOS Press, 1996, pp. 167–187. [Online]. Available: <https://users.cs.fiu.edu/~smithg/papers/jcs96.pdf>

#### APPENDIX

#### *Contents:*

- [A.](#page-15-0) Proof of the Main Theorem (Theorem [1\)](#page-8-0)
- [B.](#page-17-1) Encoding of derived expressions
- [C.](#page-17-0) Prelude
- [D.](#page-18-0) Code listings omitted from Section [VI](#page-9-0)

<span id="page-15-0"></span>A. Proof of the Main Theorem (Theorem 1)

The proof makes use of some basic properties of the system—often referred to as *confinement* properties (following Volpano, Irvine, and Smith [51]):

<span id="page-15-1"></span>**Lemma 4.** If  $pc \vdash C, e \Downarrow C', V$ , then:

- (1)  $pc \sqsubseteq label(V)$ ;
- (2)  $C \neq C'$  implies  $pc \sqsubseteq label(C)$  and  $pc \sqsubseteq label(C')$ .

*Proof.* (Sketch) (1) By a straightforward induction on the derivation. In the axioms, the value label equals the current pc; in the remaining rules, the premise pc is the same as or higher than the conclusion's pc, and the conclusion's value label is at least that of one of the premises.

(2) Also by induction on the derivation. The only rules that explicitly change the history are (TEST) and (CLEAR), and each has explicit side conditions ensuring the stated invariant.

In what follows we consider the special case when  $pc \not\sqsubseteq k$ . The condition  $pc \not\sqsubseteq k$  may be read as: information currently influencing the program counter is not permitted to flow to level k. In the special case of a two-level confidentiality lattice with pc = High and k = Low, this is commonly expressed as "the pc is high", or "the context is high". In the following we sometimes say that "the pc is high" to mean  $pc \not\sqsubseteq k$  when a specific k is clear from the context.

<span id="page-15-2"></span>**Lemma 5.** If  $pc \vdash C, e \Downarrow C', V$  and  $pc \not\sqsubseteq k$ , then  $C \sim_k C'$ .

*Proof.* If C = C', the result is immediate by reflexivity of  $\sim_k$ . Otherwise, by Lemma 4(2) we have  $pc \sqsubseteq \mathsf{label}(C)$  and  $pc \sqsubseteq \mathsf{label}(C')$ . Since  $pc \not\sqsubseteq k$ , it follows that  $\mathsf{label}(C) \not\sqsubseteq k$  and  $\mathsf{label}(C') \not\sqsubseteq k$ , hence  $C \sim_k C'$  by the definition of  $\sim_k$  on histories.

This yields a core ingredient for the main noninterference proof:

<span id="page-15-3"></span>**Lemma 6** (High NI). Suppose that  $pc \not\sqsubseteq k$ ,

- $pc \vdash C_0, e_0 \Downarrow C'_0, V_0, \quad pc \vdash C_1, e_1 \Downarrow C'_1, V_1,$
- $C_0 \sim_k C_1$ , and  $e_0 \sim_k e_1$ .

Then  $C_0' \sim_k C_1'$  and  $V_0 \sim_k V_1$ .

*Proof.* By Lemma 5,  $C_i \sim_k C_i'$  for  $i \in \{0, 1\}$ . Using  $C_0 \sim_k C_1$  and symmetry/transitivity of  $\sim_k$ ,

$$C_0' \sim_k C_0 \sim_k C_1 \sim_k C_1'$$

hence  $C_0' \sim_k C_1'$ . Moreover, Lemma 4(1) gives  $pc \sqsubseteq \mathsf{label}(V_i)$ ; since  $pc \not\sqsubseteq k$ , we have  $\mathsf{label}(V_i) \not\sqsubseteq k$  for  $i \in \{0,1\}$ . By the definition of  $\sim_k$  on values,  $V_0 \sim_k V_1$ .

**Restatement of Theorem 1** The following sublanguages satisfy TINI:

- (1) expressions built without ?;
- (2) expressions which use only one non-bottom label, and
- (3) expressions in which? occurs only in the form of assert statements or strong tests.

*Proof.* For a set of expressions E, define label(E) to be the set of all labels appearing as labels or tests in E.

We prove the theorem by generalising the property proved for each of the three sublanguages E, to show that if  $e_0, e_1 \in E$ , and the labels of pc,  $C_0$  and  $C_1$  are in labels found in E, then

- $pc \vdash C_0, e_0 \Downarrow C'_0, V_0, \quad pc \vdash C_1, e_1 \Downarrow C'_1, V_1,$
- $C_0 \sim_k C_1$ , and  $e_0 \sim_k e_1$ .

Then  $C_0'\sim_k C_1'$  and  $V_0\sim_k V_1,\ V_0,V_1\in E,$  and  $\mathrm{label}(C_0'),\mathrm{label}(C_1')\in\mathrm{label}(E).$ 

The theorem then follows by taking  $pc = \bot$ , and from the fact that  $\sim_k$  is reflexive and hence  $[] \sim_k []$ .

All three parts can be proved in the same manner, by strong induction on the derivation of the pair of judgements, and by cases according to the last derivation rule applied. All the cases, with the exception of test, strong test, and assert, are common to all three proofs, so we roll the three proofs into one; the reasoning in the three parts of the theorem only differs at the case for (TEST) (where we need to assume that the lattice has only two elements) and (ASSERT) and (STRONG TEST) (for the case of the general lattice). A key observation is that the sublanguage with assert and strong test is closed under substitution. The parts about the labels of the sublanguages  $(V_0, V_1 \in E, \text{ and } \mathsf{label}(C_0'), \mathsf{label}(C_1') \in \mathsf{label}(E))$  are trivial except for part (iii), where it follows easily by the facts that the set of labels of the expressions are closed under join, the set of expressions is closed under substitution, and that the labels in the resulting terms must always be the join of labels from the set of expressions.

We proceed by strong induction on the derivation of  $pc \vdash C_0, e_0 \Downarrow C'_0, V_0$ . The goal is to show that whenever  $C_0 \sim_k C_1$  and  $e_0 \sim_k e_1$ , and

$$pc \vdash C_1, e_1 \Downarrow C'_1, V_1,$$

then  $C_0' \sim_k C_1'$  and  $V_0 \sim_k V_1$ . Strong induction is needed because in the derivations for the derived rules (ASSERT) and (STRONG TEST), the immediate subderivations correspond to non-immediate subderivations in the actual operational semantics.

We begin with a top-level case-analysis: if  $pc \not\sqsubseteq k$ , the results follow immediately from Lemma 6. Thus, for the remainder of the proof we assume  $pc \sqsubseteq k$  and analyse the final rule used in the derivation of  $pc \vdash C_0, e_0 \Downarrow C'_0, V_0$ .

Case: (FORK)  $e_0 =$ fork  $e \sim_k$ fork  $e' = e_1$ , so  $e \sim_k e'$ . We apply the induction hypothesis (IH) to the subderivations

$$pc \vdash C_0, e \Downarrow C'_0, V_0 \qquad pc \vdash C_1, e' \Downarrow C'_1, V_1$$

to obtain  $V_0 \sim_k V_1$ . Since in the fork rule  $C_0' = C_0$  and  $C_1' = C_1$ , we have  $C_0' \sim_k C_1'$  by the premise of the theorem.

Case: (LAMBDA) Immediate: the  $C_i$  unchanged and  $e_0 = \lambda x.e \sim_k \lambda x.e' = e_1 \text{ implies } pc: \lambda x.e \sim_k pc: \lambda x.e'.$ 

Case: (CLEAR)  $e_1 =$ clear, so the two rule instances are identical. Result follows from reflexivity of  $\sim_k$ .

Let  $e_0 = e_f e_a$  and  $e_1 = e_f' e_a'$  with  $e_f \sim_k$ Case: (APP)  $e'_f$  and  $e_a \sim_k e'_a$ .

We have subderivations:

- (a)  $pc \vdash C_0, e_f \Downarrow C_1, m : \lambda x.e_3$
- (b)  $pc \vdash C_1, e_a \Downarrow C_2, V_2$
- (c)  $pc \sqcup m \vdash C_2, e_3[x := V_2] \Downarrow C'_0, V$

and

- $\begin{array}{ll} \text{(a')} & pc \vdash C_0, e'_f \Downarrow C'_1, \ m' : \lambda x. e'_3 \\ \text{(b')} & pc \vdash C'_1, e'_a \Downarrow C'_2, \ V'_2 \\ \text{(c')} & pc \sqcup m' \vdash C'_2, e'_3[x := V'_2] \Downarrow C''_0, \ V' \end{array}$

By the induction hypothesis applied to (a) and (a'), we obtain

$$C_1 \sim_k C_1'$$
 and  $m: \lambda x.e_3 \sim_k m': \lambda x.e_3'$ .

Similarly, applying the IH to (b) and (b') gives

$$C_2 \sim_k C_2'$$
 and  $V_2 \sim_k V_2'$ .

We now proceed by case analysis on m and m'.

**Subcase:**  $m = m' \sqsubseteq k$ Then  $e_3 \sim_k e_3'$  and, by substitutivity,

$$e_3[x := V_2] \sim_k e_3'[x := V_2'].$$

Applying the IH to (c) and (c') yields

$$C_0' \sim_k C_0''$$
 and  $V \sim_k V'$ .

**Subcase:**  $m \not\sqsubseteq k$ ,  $m' \not\sqsubseteq k$ Then  $pc \sqcup m \not\sqsubseteq k$  and  $pc \sqcup m' \not\sqsubseteq k$ , so by Lemma 6 applied to (c) and (c'),

$$C_0' \sim_k C_0''$$
 and  $V \sim_k V'$ .

Let  $e_0 = l_0 : e$  for some e, with rule Case: (LABEL) instance

$$\frac{pc \sqcup l_0 \vdash C_0, e \Downarrow C'_0, V_0}{pc \vdash C_0, l_0 : e \Downarrow C'_0, V_0}$$

We proceed by cases according to the relation between  $l_0$  and k:

**Subcase:**  $l_0 \not\sqsubseteq k$ Here we have  $e_1 = l_1 : e'$  for some  $l_1 \not\sqsubseteq k$  and e'. Since both  $pc \sqcup l_0$  and  $pc \sqcup l_1$  are not below k, we apply Lemma 6 to the subderivations

$$pc \sqcup l_i \vdash C_i, e \Downarrow C'_i, V_i$$

to obtain  $C_0' \sim_k C_1'$  and  $V_0 \sim_k V_1$ .

**Subcase:**  $l_0 \sqsubseteq k$  Since  $pc \sqsubseteq k$ , we have  $pc \sqcup l_0 \sqsubseteq k$ . By definition of  $\sim_k$ ,  $e_1 = l_0 : e'$  for some e' with  $e \sim_k e'$ . Thus we have

$$pc \sqcup l_0 \vdash C_1, e' \Downarrow C'_1, V'$$

and applying the induction hypothesis yields  $C_0' \sim_k C_1'$  and  $V \sim_k V'$  as required. Case: (PROMPT) and  $e_1 = @f_1$  for some expressions  $f_0 \sim_k f_1$ .

We have derivations for  $i \in \{0, 1\}$  of the form:

$$\frac{pc \vdash C_i, f_i \Downarrow (l_i : c_i), (m_i : v_i)}{pc \vdash C_i, @f_i \Downarrow n_i : c_i + [(p_i, r_i)], n_i : r_i}$$

$$\begin{aligned} \text{where} \quad p_i &= \text{serialise}(\text{erase}_{n_i}(v_i)) \\ n_i &= l_i \sqcup m_i \\ r_i &= \text{generate}(c_i, p_i) \end{aligned}$$

The definition of  $\sim_k$  ensures  $f_0 \sim_k f_1$ , so from the induction hypothesis applied to the subderivations of  $f_0$  and  $f_1$ , we obtain  $l_0: c_0 \sim_k l_1: c_1$  and  $m_0: v_0 \sim_k m_1: v_1$ . It remains to show:

$$n_0: c_0 + [p_0, r_0] \sim_k n_1: c_1 + [(p_1, r_1)]$$
 (\*)  
 $n_0: r_0 \sim_k n_1: r_1$ 

We proceed by cases on the labels  $l_i$  and  $m_i$  which, by the induction hypothesis and definition of  $\sim_k$ , are exhaustive:

**Subcase:** Both  $l_i \sqsubseteq k$  and  $m_i \sqsubseteq k$ By this assumption we have  $n_i \sqsubseteq k$ . By definition of  $\sim_k$ , we have  $l_0 = l_1$  and  $m_0 = m_1$  and hence  $C_0 = C_1$  and  $v_0 \sim_k v_1$ . From this we see that  $n_0 = n_1$ . By the serialisation assumption, since  $n_i \sqsubseteq k, v_0 \sim_k v_1$  implies  $p_0 = p_1$ . Hence by determinism of generate,  $r_0 = r_1$  and . Thus  $C_0 + [p_0, r_0] = C_1 + [p_1, r_1]$ and  $r_0 = r_1$ , so (\*) holds.

**Subcase:** Either  $l_i \not\subseteq k$  or  $m_i \not\subseteq k$  for some ithis assumption is follows that the outgoing label  $n_i = l_i \sqcup$  $m_i \not\sqsubseteq k$  for i=0,1. Thus from the definition of  $\sim_k$ ,  $n_0$ :  $c_0 + [p_0, r_0] \sim_k n_1 : c_1 + [p_1, r_1] \text{ and } n_0 : r_0 \sim_k n_1 : r_1.$ 

This completes the proof of part (1) of the Theorem. The remaining two proof cases complete the proof for parts (2) and (3) respectively:

Case: (TEST) (two-point lattice) In this case  $e_i = e_i' ? l$ for i = 0, 1, with  $e'_0 \sim_k e'_1$ .

$$\frac{pc \vdash C_i, e'_i \Downarrow C'_i, l_i : v_i}{pc \vdash C_i, l?e'_i \Downarrow C'_i, pc : b_i}$$

where

$$b_i = \begin{cases} \mathbf{true} & \text{if } l_i \sqsubseteq l \\ \mathbf{false} & \text{otherwise.} \end{cases}$$

By the IH we have

$$C_0' \sim_k C_1'$$
 and  $l_0: v_0 \sim_k l_1: v_1.$ 

It remains to show that  $pc: b_0 \sim_k pc: b_1$ . Since we are assuming that  $pc \sqsubseteq k$  (the top level case analysis in the induction proof) this amounts to showing that  $b_0 = b_1$ .

We proceed by cases according to how  $l_0: v_0 \sim_k l_1: v_1$ :

**Subcase:**  $l_0 = l_1 \sqsubseteq k$  and  $v_0 \sim_k v_1$  In this case  $b_0 = b_1$  follows directly.

**Subcase:**  $l_0 \not\sqsubseteq k$  and  $l_1 \not\sqsubseteq k$  To have  $b_0 = b_1$  we require

$$l_0 \in L \iff l_1 \in L$$
.

In general this need not hold, but in a two-point lattice there is only one way to satisfy the assumption of this subcase, namely that  $k = \bot$  and  $l_0 = l_1 = \top$ . From equivalence of  $l_0$  and  $l_1$  it follows that  $b_0 = b_1$ .

Case: (ASSERT) The behaviour of assert is captured by a derived rule, so for  $i \in \{0, 1\}$  we have derivations

$$\frac{pc \vdash C_i, e \Downarrow C'_i, V_i}{pc \vdash C_i, \mathbf{assert} \ l \ e \Downarrow C'_i}$$

Since assert l  $e \sim_k$  assert l e and assert is not defined using any labelling, it follows from the definition of  $\sim_k$  that

assert 
$$l$$
  $e \sim_k$  assert  $l$   $e$ .

Since  $pc \vdash C_i, e \Downarrow C'_i, V_i$  is a subderivation of the expansion of the definition of assert, we can apply the induction hypothesis to obtain

$$C_0' \sim_k C_1'$$
.

(The other part of the induction hypothesis is not relevant here) Since both computations return the same labelled value, this concludes the proof.

**Case:** (STRONG TEST) In this case we suppose  $e = m??e_0 \sim_k e'$ , and  $C_0 \sim_k C_1$ , Since we assume e' is in the same sublanguage where test only occurs in the form of an assert or a strong test, e' must have the form  $m??e_1$  and thus we have two derivations of the form

$$\frac{pc \vdash C_i, e_i \Downarrow C_i', l_i : v_i'}{pc \vdash C_i, m??e_i \Downarrow C_i', (pc \sqcup m : v_i)}$$

The induction hypothesis gives us  $C_0' \sim_k C_1'$  and  $l_0: v_0' \sim_k l_1: v_1'$ , so it remains to show that  $pc \sqcup m: v_0 \sim_k pc \sqcup m: v_1$  where  $v_i$  is the result of the comparison  $l_i \sqsubseteq m, i = 0, 1$ . We proceed by cases according to the way by which  $l_0: v_0' \sim_k l_1: v_1'$ :

**Subcase:**  $l_0 = l_1 \sqsubseteq k$  If follows that the outcome of the test is the same in both cases, i.e.  $v_0 = v_1$  and we are done

**Subcase:**  $l_i \not\sqsubseteq k, \ i=1,2$  We reason by cases according to whether the predicate  $l_0 \sqsubseteq m$  is equivalent to  $l_1 \sqsubseteq m$ ; if they are, then  $v_0 = v_1$  and we are done. Otherwise, suppose wlog that  $l_0 \sqsubseteq m$  and  $l_1 \not\sqsubseteq m$  (and hence  $v_0$  and  $v_1$  are different). Since by assumption  $l_0 \not\sqsubseteq k$ , we have  $m \not\sqsubseteq k$ , and thus  $pc \sqcup m \not\sqsubseteq k$ , it follows that  $pc \sqcup m : v_0 \sim_k pc \sqcup m : v_1$  as required.

#### <span id="page-17-1"></span>B. Encoding of derived expressions

We use \_ as a variable with the convention that \_ only ever appears in the abstraction of a lambda and never in the body or elsewhere.

#### **Derived expressions:**

```
true \triangleq \lambda x.\lambda y.x

false \triangleq \lambda x.\lambda y.y

() \triangleq \lambda x.x
\nif e_1 then e_2 else e_3 \triangleq e_1 (\lambda_-.e_2) (\lambda_-.e_3) ()

let x = e_1 in e_2 \triangleq (\lambda x.e_2) e_1

e_1; e_2 \triangleq \text{let } \_= e_1 in e_2

(e_1, e_2) \triangleq \text{pair } e_1 e_2

pair \triangleq \lambda x.\lambda y.\lambda s. s. x.y

fst p \triangleq p true

snd p \triangleq p false

[] \triangleq \lambda c.\lambda n. n

e_1 :: e_2 \triangleq \text{cons } e_1 e_2

cons \triangleq \lambda h.\lambda t.\lambda c.\lambda n. c.h (t.c.n)

[e_1, e_2, \ldots, e_n] \triangleq e_1 :: e_2 :: \cdots :: e_n :: []
```

Note that (), the empty tuple, is just the identity function in the standard Church encoding of tuples. We encode numbers as lists, characters as numbers, and strings as lists of characters. An object is a list of field-value pairs. Hence, all the the JSON notations supported by our interpreter can be encoded in our core calculus.

#### <span id="page-17-0"></span>C. Prelude

The following definitions are automatically loaded before user code. They provide common utilities including the Y combinator for recursion, array operations, and a syntax summary for LLM prompts.

# Syntax summary for LLM prompts

```
let syntax_summary =
    'Grammar:\ne ::= x | \x.e | e1 e2 | let x=e1 in e2 | if e1 then
        e2 else e3
        | {11:e1, ..., ln:en} | e.l | e.l:=e | [e1, e2,
```

```
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
- null keyword: use "null" string or false instead'
# Y combinator for recursion
let fix = \f. (\x. f (\v. x x v)) (\x. f (\v. x x v)
    )
# Check if a value is a function
let is_fn = \x. (shape x).type == "function"
# Check if a value is an array
let is_array = \x. (shape x).type == "array"
```

### <span id="page-18-0"></span>*D. Code listings omitted from Section [VI](#page-9-0)*

Figure [1](#page-19-0) shows imperative programming in the monadic style used to program the tool-calling examples.

Figure [2](#page-20-0) shows a tool-calling agent for Fig 5 of the CaMeL paper [\[9\]](#page-12-8), programmed within our calculus in a monadic style.

Figure [3](#page-21-0) shows how a trusted conversation can generate code that uses a quarantined conversation to avoid a prompt injection vulnerability [\[9\]](#page-12-8).

```
let monadic_api =
'
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
'
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
```

<span id="page-19-0"></span>Fig. 1. Imperative programming in the monadic style.

```
let system_prompt =
  "{tool_api}.
    You are a versatile agent, but you only emit literal JSON values, not lambda calculus.
    A tool call must take the form: ['function-name', value1, ... valueN]
    where function-name is the name of one of the provided functions
    and each value is a literal (not an expression).
    Do not include the initial state argument, which will be provided automatically.
    Every answer in this session must be in one of the following two forms.
    (1) you have info to answer your goal, emit ['answer', the-answer-as-a-value];
    (2) to gather more information, emit ['tool-call',['function-name', value1, ... valueN]].
    You will receive the answer in the next prompt, and can then continue.
    Only return a literal array in format (1) or (2), never any other expression such as a let or lambda.
    Remember, every answer must be in one of these two forms.
    Your first answer should be ['answer', 42]."
# Response format helpers
let is_answer = \r. let s = shape r in s.type == "array" && s.length == 2 && r.[0] == 'answer'
let dest_answer = \r. r.[1]
let is_tool_call = \r. let s = shape r in s.type == "array" && s.length == 2 && r.[0] == 'tool-call'
let dest_tool_call = \r. r.[1]
# tool_agent: int -> string -> IO value
# Recursive agent loop: runs until ['answer', v], feeds errors back to LLM for retry
# Counts down rounds from initial budget to 0
let tool_agent = fix (\self. \rounds. \p.
  if rounds == 0 then failwith "Max rounds exceeded" else
  let r = @ p in
  if not r.[0] then
    self (rounds - 1) "Error: {r.[1]}. Try again. Reply with ['answer', value] or ['tool-call', [...]]."
  else
    let response = r.[1] in
    if is_answer response then
      return (dest_answer response)
    else if is_tool_call response then
      let call = dest_tool_call response in
      bind (exec_tool_call call) (\result.
        self (rounds - 1) "Tool {call} returned: {result}. Reply with ['answer', value] or ['tool-call',
            [...]].")
    else
      self (rounds - 1) "Expected ['answer', v] or ['tool-call', [...]]. Got: {response}"
)
# run_agent: string -> IO queue
# Initializes the conversation, runs the looping agent, and returns the message queue
let run_agent = \goal.
  let _ = clear in
  bind (prompt_llm system_prompt) (\_.
  bind (tool_agent 5 "Your goal: {goal}. Issue tool calls until you can answer directly.") (\_.
  bind (get_state) (\state.
  return state.queue)))
```

<span id="page-20-0"></span>Fig. 2. Tool-calling agent for Fig 5 of the CaMeL paper [\[9\]](#page-12-8).

```
let direct_api =
"{syntax_summary}
You have access to functions with the following types:
get_last_email: state -> string
send_email: (to:string) -> (subject:string) -> (body:string) -> state -> state
quarantine: (prompt:string) -> json # prompt an LLM, returns JSON
The quarantine function prompts an LLM and returns true, false, number, double quoted string, or JSON.
The prompt should describe the result format or give an example.
Example: quarantine 'Add 1 and 2. Return a number.'
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
```

<span id="page-21-0"></span>Fig. 3. Direct code generation