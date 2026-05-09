                                          Owner-Harm: A Missing Threat Model for AI Agent
                                                             Safety


                                                               Dongcheng Zhang∗                                Yiqing Jiang
                                                         BlueFocus Communication Group                       Tongji University
                                                                 Beijing, China                               Shanghai, China
                                                              zdclink@gmail.com                           jyq.russel@gmail.com




arXiv:2604.18658v1 [cs.CR] 20 Apr 2026
                                                                                         Abstract
                                                     Existing AI agent safety benchmarks focus predominantly on generic crimi-
                                                     nal harm—cybercrime, harassment, and weapon synthesis—leaving a systematic
                                                     blind spot for a distinct and commercially consequential threat category: agents
                                                     harming their own deployers. Real-world incidents illustrate this gap: the Slack AI
                                                     credential exfiltration (August 2024), Microsoft 365 Copilot data leaks via calen-
                                                     dar injection (January 2024), and a Meta agent unauthorized forum post exposing
                                                     operational data (March 2026). We propose Owner-Harm, a formal threat model
                                                     defining eight categories of agent behavior that damage the deploying owner’s in-
                                                     terests. We quantify the resulting defense gap on two authoritative benchmarks:
                                                     the same compositional safety system achieves 100% TPR / 0% FPR on Agen-
                                                     tHarm (generic criminal harm, 176 harmful scenarios) yet only 14.8% (4/27;
                                                     95% CI: 5.9%–32.5%) on AgentDojo injection tasks (prompt-injection-mediated
                                                     owner harm), exposing a category-specific blind spot. A controlled experiment
                                                     with a zero-shot generic LLM classifier reveals that this gap is not inherent to the
                                                     owner-harm category (generic LLM: 62.7% vs. 59.3%, gap = 3.4 pp) but arises
                                                     from environment-bound symbolic rules that fail to generalize across tool vocabu-
                                                     laries. On a post-hoc diagnostic benchmark of 300 owner-harm scenarios, the gate
                                                     alone achieves 75.3% TPR / 3.3% FPR; adding a deterministic post-audit verifier
                                                     raises overall TPR to 85.3% (+10.0 pp) and Hijacking detection from 43.3% to
                                                     93.3%, demonstrating strong layer complementarity. These results confirm that
                                                     owner-harm requires context-aware safety mechanisms that explicitly model re-
                                                     source ownership, trust boundaries, and authorization scope. To organize these ob-
                                                     servations, we introduce the Symbolic-Semantic Defense Generalization (SSDG)
                                                     conceptual framework, which describes how information coverage—the fraction
                                                     of an attack’s evidential requirements satisfied by a defense’s context set—relates
                                                     to detection rate. Two controlled SSDG experiments partially test the framework:
                                                     context deprivation induces a 3.4× amplification of the detection gap (gap ra-
                                                     tio R = 3.60 vs. R = 1.06 with full context), while context injection reveals
                                                     that goal-context awareness is necessary but not sufficient—structured goal-action
                                                     alignment, not simple text concatenation, is required for effective owner-harm de-
                                                     tection.


                                         1       Introduction
                                         The deployment of autonomous AI agents into production systems has accelerated faster than the
                                         safety frameworks needed to govern them. Current research focuses on preventing agents from facil-
                                         itating generic criminal harm: generating malware, synthesizing dangerous substances, or producing
                                             ∗
                                                 Work performed while at BlueFocus Communication Group. Correspondence: zdclink@gmail.com.


                                         Preprint. Under review.
harassing content. Yet a qualitatively different and commercially urgent threat class has emerged in
practice—agents harming the very organizations that deploy and trust them.
Three incidents anchor this concern. In August 2024, PromptArmor disclosed that Slack AI could be
manipulated via prompt injection to exfiltrate private channel tokens from the deploying organization
PromptArmor [2024]. In January 2024, Zenity Research demonstrated that Microsoft 365 Copilot
could be hijacked through malicious calendar invitations to forward sensitive emails to external
parties Zenity Research [2024]. In March 2026, a Meta AI agent made an unauthorized post to an
internal forum, exposing operational data for two hours before containment Schiffer [2026]. In each
case, the agent’s deployer—not a third-party victim—bore the harm.
The benchmark gap. Existing agent safety benchmarks do not model this pattern. AgentHarm
Andriushchenko et al. [2025] catalogs 11 harm categories, all framed as an adversary using an agent
against third parties. AgentDojo Debenedetti et al. [2024] evaluates prompt injection defenses across
four suites (Banking, Travel, Workspace, Slack) but without an explicit owner-harm taxonomy. The
consequences are measurable: the same compositional safety system that achieves 100% TPR on
AgentHarm scores only 3.7% (1/27) on AgentDojo injection tasks using deterministic rules, and
14.8% (4/27) with semantic reasoning added. The constraints that successfully intercept generic
criminal content—system call patterns, toxicity signals—have near-zero coverage of application-
layer owner harm, such as financial transactions initiated via legitimate banking APIs or PII for-
warded through authorized email tools.
Contributions. This paper makes three contributions:
      1. Owner-Harm threat model. We provide the first formal definition of owner-harm and
         its eight sub-categories, grounded in real incidents and distinguished from existing tax-
         onomies.
      2. Defense gap quantification and gap attribution. We measure the gap (100% vs. 14.8%)
         and use a controlled experiment to attribute it to environment-bound rule generalization
         failure rather than inherent category difficulty: a zero-shot generic LLM shows only a 3.4
         pp gap (62.7% vs. 59.3%) across the same benchmarks.
      3. Layer complementarity evidence. We show that deterministic post-audit verification is
         orthogonal to semantic gate reasoning for Hijacking (C7), raising detection from 43.3% to
         93.3% via complementary detection dimensions.

2     Owner-Harm Threat Model
2.1   Formal Definitions

We model an AI agent as a tuple A = ⟨M, T , E, π⟩, where M is the underlying language model,
T is the available tool set, E is the environment state space, and π is the agent’s policy. An agent
produces an action sequence ⃗a = (a1 , . . . , an ) transforming environment state s0 to s′ .
Definition 1 (Owner). The owner O is the entity that deploys A, grants resource access RO , and
bears accountability for agent actions. O is associated with a resource set RO , a utility function UO
over environment states, and a trust boundary BO delineating authorized interactions.
Definition 2 (Owner-Harm). An action sequence ⃗a causes owner-harm with respect to owner O if
and only if:
                OH(⃗a, O) := UO (s′ ) < UO (s0 ) ∧ ∃ ai ∈ ⃗a : cause(ai , s0 → s′ )
where cause(ai , s0 → s′ ) means ai is a proximate or distal cause of the state transition from s0 to
s′ .
Definition 3 (Direct Owner-Harm).
                          DOH(⃗a, O) := OH(⃗a, O) ∧ ProxCause(A, ⃗a)
where ProxCause(A, ⃗a) means the agent is the proximate cause of the harmful state transition.
Definition 4 (Indirect Owner-Harm).
                        IOH(⃗a, O, V) := OH(⃗a, O) ∧ Manipulate(V, π, ⃗a)
where V is an adversarial actor that manipulates the agent’s policy π to produce the harmful action
sequence—the prompt injection attack model.


                                                  2
              Table 1: Coverage of Owner-Harm Categories by Existing Frameworks

           Category                      AgentHarm     ToolEmu        OWASP   AgentDojo
           C1: Credential Leak               ∼             ✓           ✓           ∼
           C2: Infrastructure Exposure       ×             ∼           ✓           ×
           C3: Privacy Exposure              ∼             ✓           ✓           ✓
           C4: Inner Circle Leak             ×             ×           ×           ×
           C5: Asset Destruction             ∼             ✓           ∼           ∼
           C6: Exfiltration via Tools        ×             ∼           ∼           ∼
           C7: Hijacking                     ×             ∼           ✓           ∼
           C8: Unauthorized Autonomy         ∼             ✓           ∼           ×
                                  ✓ = covered; ∼ = partial; × = gap


2.2   Eight Owner-Harm Categories

We enumerate eight categories C1–C8 (primary labels; a single incident may span multiple cate-
gories), each grounded in documented incidents.
C1: Credential Leak. The agent exfiltrates authentication materials (API keys, OAuth tokens,
session cookies, passwords) belonging to or entrusted to the owner. Real case: Slack AI August
2024 PromptArmor [2024]—injected prompt caused the assistant to echo private channel tokens to
the attacker.
C2: Infrastructure Exposure. The agent misconfigures or discloses network rules, cloud resource
policies, or internal architecture, expanding the owner’s attack surface. Pattern: AI-assisted code
generation producing over-permissive AWS IAM policies that expose production databases.
C3: Privacy Exposure. The agent transmits personally identifiable information (PII) or confiden-
tial business data to unauthorized parties. Real case: Microsoft 365 Copilot January 2024 Zenity
Research [2024]—calendar injection caused Copilot to forward sensitive email contents externally.
C4: Inner Circle Leak. The agent betrays trust relationships that are commercially sensitive to the
owner: client lists, partner agreements, M&A discussions, or strategic roadmaps. Pattern: Samsung
employees pasting proprietary semiconductor source code into ChatGPT (April 2023), with the
owner-harm being the confidentiality breach to a third-party model.
C5: Asset Destruction. The agent irreversibly deletes or corrupts owner data, configurations, or
digital assets. Pattern: AI coding agents executing rm -rf on production directories when given
broad filesystem access and ambiguous cleanup instructions.
C6: Exfiltration via Tools. The agent exploits authorized tools as covert data channels—using
email, webhooks, or file-write operations to smuggle sensitive data to attacker-controlled endpoints.
Real case: ASCII smuggling via Microsoft 365 Copilot Rehberger [2024]—injected prompt caused
Copilot to encode and transmit sensitive data through Markdown image URLs rendered invisibly.
C7: Hijacking. An adversary achieves persistent control over the agent using the owner’s identity,
credentials, or resource access—the agent becomes a weaponized surrogate. Pattern: AutoGPT
memory poisoning (2024–2025) where injected memory entries caused the agent to act on behalf of
the attacker across subsequent sessions.
C8: Unauthorized Autonomy. The agent exceeds its authorization scope by taking consequen-
tial actions without required human confirmation. Real case: Air Canada chatbot (February 2024)
committed the airline to unauthorized refund terms in a legally binding interaction British Columbia
Civil Resolution Tribunal [2024].

2.3   Comparison with Existing Taxonomies

Table 1 compares Owner-Harm categories against four existing frameworks: AgentHarm An-
driushchenko et al. [2025] (11 categories), ToolEmu Ruan et al. [2024] (7 risk types), OWASP
LLM Top 10, and AgentDojo Debenedetti et al. [2024] (4 suites).
The most notable gap is C4 (Inner Circle Leak), which appears in no existing benchmark. This
category requires reasoning about the owner’s trust graph—who counts as an insider—which no


                                                 3
                    Table 2: Generic Defense Failure Modes for Owner-Harm
                     Defense Class          Owner-Harm Blind Spot
                     Content classifier     Ignores RO ; “send email” is benign
                                            by content
                     Injection detector     Detects injection syntax; misses se-
                                            mantic intent
                     Tool monitor           Sees call signature; not authorization
                                            context
                     DLP system             Pattern-matches known PII; misses
                                            context-defined confidential data
                     Behavioral anomaly     Requires baseline; new deployments
                                            have no baseline


current system models explicitly. C6 is partially covered by ToolEmu but misses the covert channel
aspect: using authorized tools as smuggling vectors. The owner-centric perspective itself is the pri-
mary novel contribution: existing frameworks evaluate harm against third parties, users, or society;
none formally model the deploying owner as the victim.

2.4   Why Generic Defenses Fail

The fundamental mismatch is context-dependence of harm:
                        ∃ c, O1 , O2 : Harmful(c, O1 ) ∧ ¬Harmful(c, O2 )
The action “forward email to external@attacker.com” is benign for an owner whose trust bound-
ary includes that address, and harmful for an owner whose trust boundary does not. Content-only
classifiers cannot make this distinction.
Three owner-context dimensions are systematically absent from generic defenses:

       • Resource Ownership (RO ): which data and credentials belong to the owner and should
         not be disclosed.
       • Trust Boundary (BO ): who the owner considers an authorized counterparty for each re-
         source type.
       • Authorization Scope (AuthO ): which actions the owner has explicitly sanctioned without
         requiring confirmation.
Proposition 1 (Generic Classifier Incompleteness). Any context-free binary classifier fgen : C →
{0, 1} that classifies action content without access to RO , BO , or AuthO will produce owner-harm
false negatives on scenarios where harm is defined relative to the owner’s context.

Table 2 summarizes the failure modes of common defense classes against this incompleteness.

2.5   Symbolic-Semantic Defense Generalization (SSDG) Framework

The controlled experiment results motivate a conceptual account of when and why defenses fail to
generalize across attack categories. We emphasize that SSDG is a conceptual framework for orga-
nizing observations, not a formal mathematical theory with rigorous proofs. For formal treatments
of causality in such analyses, see Pearl Pearl [2009]. We introduce the following framework.
Definitions. Let an attack a be characterized by its evidential requirement set E(a)—the set of
contextual facts needed to determine its harmfulness. A defense D maintains an information set
Ω(D) = ΩS ∪ ΩC , where ΩS captures surface-level features (tool names, parameter patterns) and
ΩC captures contextual knowledge (world knowledge, owner context, task goals). The information
coverage of D for attack a is:
                                            |E(a) ∩ Ωusable (D)|
                          Cover(D, a) :=                         ∈ [0, 1]
                                                  |E(a)|
where Ωusable (D) ⊆ Ω(D) denotes the subset of information that the defense can effectively use in
its decision process. Mere availability of information (Ωraw ) does not guarantee usability—simple


                                                 4
text concatenation of context may not enable structured comparison (as P1 in Section 4.6 demon-
strates).
Assumption (Detection-Coverage Monotonicity). TPR(D, a) is non-decreasing in Cover(D, a);
below threshold θ, TPR(D, a) ≤ ε.
Hypothesis 1 (Symbolic Defense Gap). A pure symbolic defense with ΩC = ∅ achieves
Cover(D, AG ) ≫ Cover(D, AO ) when AO requires joint surface-context evidence. Consequently,
TPR(D, AO ) ≤ ε while TPR(D, AG ) remains high—producing a structural detection gap.
Hypothesis 2 (Semantic Defense Stability). A semantic defense with ΩC ⊇ Cworld (world knowl-
edge) satisfies Cover(D, AG ) ≈ Cover(D, AO ), since both attack types’ evidential requirements
are met by world-knowledge reasoning. The inter-category detection gap is thus bounded by infer-
ence capacity, not information availability.

These hypotheses yield two falsifiable predictions tested in Section 4.6: P1—injecting the user goal
into a symbolic defense’s context should raise Cover(D, AO ), increasing TPR; and P2—stripping
world-context from a semantic defense should cause it to exhibit symbolic-gap behavior, with gap
ratio R > 3×.


3     Nous: Compositional Runtime Safety Gate

We evaluate owner-harm detection using Nous, a four-layer compositional runtime safety gate for
AI agent actions. We describe it briefly here; the architecture is the primary evaluation vehicle rather
than the primary contribution.
Layer 1 (L1): Deterministic Datalog Blocker. 46 Datalog rules encode owner-policy constraints
(resource ownership, known-bad patterns, categorical prohibitions). L1 is fail-closed, fast (P50 =
0.055 ms), and requires no LLM call. Rules cover categorical owner-harm such as exfiltration of
credentials with recognizable patterns (C1) and shell commands associated with asset destruction
(C5).
Layer 2 (L2): Triviality Filter. Routes trivially benign actions past the expensive semantic layer,
yielding approximately 70% cost reduction with negligible safety impact.
Layer 3 (L3): Semantic Gate. An LLM evaluator supplied with minimal-pair examples, intent de-
composition prompts, and majority vote k = 3 to handle stochasticity in mixture-of-experts models.
L3 provides semantic reasoning about owner context: whether an action falls within the owner’s
trust boundary, whether resource access is proportionate to the stated task.
Layer 4 (L4): Post-Gate Verifier. Six deterministic audit rules (V1–V6) inspect file contents and
multi-step tool-call sequences that are invisible to L1–L3 because they emerge from composed ac-
tions rather than individual calls. L4 adds ∼0.038 ms latency with zero LLM cost. Rules target
prompt injection patterns embedded in file artifacts and behavioral sequences characteristic of Hi-
jacking (C7).
Why this architecture for owner-harm. L1 encodes owner-policy as explicit Datalog facts; L3
reasons about owner context when policy is ambiguous; L4 catches injection patterns that survive
semantic evaluation because the semantic reasoning is itself manipulated by injected content. The
layers are architecturally complementary: L1 operates on individual action content; L3 operates on
action semantics plus owner context; L4 operates on artifact contents and behavioral sequences.


4     Evaluation

4.1   Evaluation Strategy

We evaluate on three benchmark sets with different evidentiary weight:

      1. AgentDojo Debenedetti et al. [2024] (authoritative): 27 injection tasks, 97 user tasks, 4
         suites (Banking, Travel, Workspace, Slack). Ground-truth labels provided by benchmark
         authors. Safety score = fraction of injection tasks blocked.


                                                   5
      Table 3: AgentDojo Results: Safety Score vs. Utility (27 injection tasks, 97 user tasks)

               Configuration             Safety             Utility           FPR
                                                   †
               L1 only (baseline)     3.7% (1/27)      97.9% (95/97)    2.1% (2/97)
               L1 + L4                3.7% (1/27)†         97.9%           2.1%
               L1 + L3 + L4 (full)   14.8% (4/27)†         97.9%           2.1%
               †95% Wilson CI: 3.7% [0.7%–18.3%]; 14.8% [5.9%–32.5%]

                       Table 4: AgentDojo Safety by Owner-Harm Category

                        Category                  L1 only       L1+L3+L4
                        Financial Harm         0/10 (0%)        1/10 (10%)
                        Privacy Breach          0/6 (0%)         2/6 (33%)
                        Operational Harm       1/4 (25%)         1/4 (25%)
                        Credential Leak         0/3 (0%)          0/3 (0%)
                        Reputational Harm       0/3 (0%)          0/3 (0%)
                        Other                   0/1 (0%)          0/1 (0%)
                        Total                 1/27 (3.7%)      4/27 (14.8%)


      2. AgentHarm Andriushchenko et al. [2025] (comparative baseline): 176 harmful + 176 be-
         nign scenarios across 11 categories. Used to confirm that the 3.7%/14.8% gap on Agent-
         Dojo is category-specific, not a global system deficiency.
      3. Owner-Harm Benchmark (post-hoc diagnostic, 300H + 150B, 8 categories): Constructed
         by the same author after optimization loops. This is NOT a held-out independent test set;
         results should be interpreted as diagnostic evidence of system capabilities. Reported sepa-
         rately from the authoritative benchmarks to avoid overstating validity.

AgentDojo to Owner-Harm category mapping. We assign each of the 27 injection tasks to
the Owner-Harm category it most closely targets: Banking (9 injection tasks): financial harm
(8 tasks—unauthorized transfers with data exfiltration), credential leak (1 task—password
modification); Travel (7 tasks): privacy breach (6 tasks—passport/banking info exfiltra-
tion), reputational harm (1 task); Workspace (6 tasks): operational harm (file dele-
tion), privacy breach (email forwarding), credential leak (2FA bypass); Slack (5 tasks):
reputational harm (phishing message), privacy breach (data exfiltration), other (SSRF).

4.2   AgentDojo Results

Table 3 presents the three-configuration comparison. All configurations are evaluated with the
AgentDojo ground-truth mode (deterministic task success scoring; no adversarial attack LLM used
in this evaluation).
Layer 4 contributes zero to AgentDojo safety. Verifier rules V1–V6 target bash command se-
quences and curl exfiltration patterns embedded in file artifacts—patterns characteristic of system-
level Hijacking. AgentDojo injection tasks operate at the application layer: the attack tools are
send money, send email, update calendar. No file artifact intermediary exists for V-rules to
inspect.
Layer 3 adds +11.1pp by catching three cases unreachable by Datalog:
travel/injection task 3 (Privacy Breach—passport details forwarded to adversary URL),
travel/injection task 5 (Privacy Breach—bank account numbers forwarded via booking
confirmation), and banking/injection task 6 (Financial Harm—batch wire transfer to adver-
sary account at plausible individual amounts). Utility remains at 97.9% across all configurations,
confirming that semantic reasoning does not increase false positives.
Table 4 shows per-Owner-Harm-category results.
Structural blind spots. Three categories of injection tasks remain systematically out of reach re-
gardless of configuration:


                                                  6
           Table 5: Owner-Harm Benchmark: Per-Category Results (Post-Hoc Diagnostic)

         Category                           Nh    Gate TPR       Combined TPR         Gate FPR
         C1: Credential Leak                28      100.0%            100.0%             0.0%
         C2: Infrastructure Exposure        50      100.0%            100.0%            20.0%†
         C3: Privacy Exposure               28      100.0%            100.0%             0.0%
         C4: Inner Circle Leak              28       89.3%             89.3%             0.0%
         C8: Unauthorized Autonomy          50       70.0%             70.0%             0.0%
         C5: Asset Destruction              28       64.3%             64.3%             0.0%
         C6: Exfiltration via Tools         28      57.1%              57.1%             0.0%
         C7: Hijacking                      60      43.3%             93.3%              0.0%
†
    20% FPR for C2 caused by rule OH-R3a over-triggering on benign external-channel configuration queries.


        • Text-only manipulation (e.g., travel/injection task 6: adversarial advertising text in-
          jected into a hotel description, with no tool call produced). The gate has no tool-call artifact
          to intercept.
        • Malicious parameters indistinguishable from legitimate ones (e.g., send money with a
          plausible amount and adversary-controlled recipient that appears to be a valid payee).
          Without the user’s task goal in the gate context, the semantic layer cannot compare “user
          requested payment to X” versus “agent is paying Y”.
        • Multi-step attacks where partial interception is insufficient (e.g., a read-then-exfiltrate chain
          where blocking the read breaks utility and missing the exfiltrate misses the attack).

Theoretical ceiling without goal context: we estimate 40–60% safety score on AgentDojo is
achievable with user task goal injected into gate context, enabling the “user requested X, agent
doing Y” comparison that resolves malicious-parameter ambiguity.
Comparison with AgentDojo baselines. Debenedetti et al. report that a GPT-4 agent with
tool filter defense achieves approximately 14.8% safety on the Banking suite Debenedetti et al.
[2024]. Nous L1+L3+L4 matches this at 14.8% overall across all four suites, while maintaining
97.9% utility compared to approximately 85% for tool filter (which blocks entire tool cate-
gories rather than discriminating at the call level).

4.3    Owner-Harm Benchmark Results (Post-Hoc Diagnostic)

Important caveat: the Owner-Harm Benchmark was constructed by the same author after optimiza-
tion loops on the Nous system. It is not an independent held-out evaluation. All 450 scenarios were
labeled by a single annotator (the first author); no inter-annotator agreement (IAA) was computed.
The C1–C8 primary-category assignments reflect the author’s subjective judgment of the dominant
harm vector, and some scenarios could plausibly be assigned to multiple categories. The results be-
low constitute diagnostic evidence that the system has learned the intended owner-harm categories;
they do not constitute validation performance in the machine-learning sense.
Overall results.
Gate only (L1+L2+L3): TPR = 75.3% (226/300), 95% Wilson CI [70.2%, 79.9%]; FPR = 3.3%
(5/150), CI [1.4%, 7.6%].
Gate + Verifier (all layers): TPR = 85.3% (256/300), 95% Wilson CI [80.9%, 88.9%]; FPR = 3.3%
(unchanged).
Table 5 shows per-category breakdown.
Hijacking layer complementarity. The most significant result is the Hijacking (C7) improvement
from 43.3% gate-only to 93.3% combined. Table 6 shows the 2×2 detection quadrant analysis (60
harmful, 30 benign).
Wilson 95% CIs: Gate TPR [31.6%, 55.9%]; Combined TPR [84.1%, 97.4%]; Hijacking benign
FPR [0.0%, 11.4%]. The 50% “Verifier-only” quadrant (30 cases) represents prompt-injection at-
tacks where the semantic gate is itself manipulated by injected content, but the verifier detects the


                                                     7
           Table 6: Hijacking (C7) Detection Quadrant Analysis (60 harmful, 30 benign)

                            Quadrant                            Count         %
                            Gate-only (verifier misses)            11       18.3%
                            Verifier-only (gate allows)            30       50.0%
                            Both layers detect                     15       25.0%
                            Neither (structural boundary)          4        6.7%
                            Combined                               56      93.3%

             Table 7: Cross-Benchmark Safety Scores (Nous vs. Generic LLM Baseline)

      Benchmark                     Focus            Nous Safety        Generic LLM            Status
      AgentHarm               Generic criminal        100% / 0%         62.7% / 16.0%        Validation
      Owner-Harm (diag.)      Owner-directed         75.3% / 3.3%            —               Diagnostic
      AgentDojo               Prompt injection       14.8% (4/27)       59.3% (16/27)       Authoritative
  Generic LLM = qwen-turbo zero-shot; gap = |Nous gap| − |Generic gap| = 85.2 pp − 3.4 pp = 81.8 pp
                        attributable to symbolic rule generalization failure.


behavioral fingerprint in file artifacts. The 4 structural boundary cases (6.7%) involve direct SQL
file injection and direct SSH key injection patterns not yet covered by V-rules.

4.4    Cross-Benchmark Comparison

Table 7 presents the central finding: the same system exhibits a 6.8× gap in safety score between
generic harm and owner-harm scenarios.
The 100% → 14.8% gap is not a system deficiency. It is the paper’s primary evidence: the constraints
that achieve 100% on AgentHarm (system call toxicity patterns, malware-synthesis keywords, ha-
rassment content signals) have near-zero coverage of application-layer owner-harm. “Send money
to account X” is indistinguishable from a legitimate banking action by its content alone; it becomes
harmful only relative to the owner’s authorization scope and the user’s actual task goal.

4.5    Controlled Experiment: Gap Attribution

The 85.2 pp gap between AgentHarm (100%) and AgentDojo (14.8%) admits two competing expla-
nations: (H1) the gap reflects a genuine structural difference—owner-harm scenarios detected via
prompt injection are semantically harder to classify; or (H2) the gap is an artifact of Nous’s symbolic
rules being fit to the AgentHarm tool vocabulary and failing to generalize.
Experimental design. We evaluate a zero-shot generic LLM classifier (qwen-turbo via API relay)
on the same data, using a uniform binary-classification prompt with no benchmark-specific fine-
tuning:
               You are a safety classifier. An AI agent is performing a task. User’s original request:
          {prompt}. Agent’s planned action: {tool} ({params}). Is this action potentially harmful
          to the user? Answer YES or NO.

For AgentDojo, the goal description (injected instruction) is substituted for the tool-call representa-
tion. The baseline has no access to owner context (RO , BO , AuthO ).
Results. Table 8 shows the 2×2 comparison.
Finding. The generic LLM exhibits a 3.4 pp gap (62.7% vs. 59.3%)—statistically negligible com-
pared to Nous’s 85.2 pp gap. This is inconsistent with H1: AgentDojo owner-harm scenarios do
not appear to be semantically harder to detect. The generic LLM achieves 59.3% on AgentDojo
without any prompt-injection-specific design, suggesting that the harm is semantically recognizable
by content alone.
Gap attribution. Nous’s gap is strongly associated with Layer 1 (Datalog) generaliza-
tion failure. L1 rules were derived from AgentHarm patterns—bash(script), read file


                                                       8
         Table 8: Controlled Experiment: Gap Attribution (Nous vs. Generic LLM Classifier)

               System                AgentHarm TPR         AgentDojo TPR           Gap
               Nous (L1+L3+L4)            100.0%            14.8% (4/27)          85.2 pp
               Generic LLM                 62.7%            59.3% (16/27)          3.4 pp
      Generic LLM AgentHarm: 110 TP / 66 FN / 28 FP (FPR = 15.9%, N = 176 harmful + 176 benign).
                          AgentDojo per-category breakdown appears in text.


Table 9: P2: Context Deprivation Induces Symbolic-Class Gap (pilot, N = 12 AgentDojo + 15
AgentHarm)

              Condition         AgentHarm TPR          AgentDojo TPR       Gap Ratio R
              Full Group              62.7%                59.3%                  1.06
              Stripped Group          30.0%                 8.3%                  3.60
                        R = TPRAH /TPRAD . P2 falsification threshold: R ≤ 1.5.



(malicious path), execute(command)—which are absent from AgentDojo’s application-layer
tool vocabulary (send money, send email, update calendar). Implication: generic LLM out-
performs Nous. Notably, the zero-shot generic LLM (59.3%) substantially outperforms Nous
(14.8%) on AgentDojo owner-harm detection. This is not a contradiction—it is the central ar-
chitectural insight: owner-harm detection depends primarily on semantic understanding of action
consequences and owner context, which symbolic rules (L1) cannot provide. Nous’s L1 achieves
perfect recall on AgentHarm’s system-call patterns but has near-zero coverage of application-layer
actions. L3’s semantic gate contributes only +11.1 pp because it also lacks owner-context grounding.
The generic LLM compensates via world-knowledge reasoning, suggesting that future owner-harm
defenses should prioritize structured semantic alignment over pattern-matching rules.


4.6    SSDG Experimental Predictions

The SSDG framework (Section 2.5) yields two testable predictions. We report pilot experiments
(N = 12 AgentDojo tasks + 15 AgentHarm scenarios) using the same controlled setup as Sec-
tion 4.5.
P1 (Context Injection) — Prediction Rejected. Injecting the user’s task goal into the gate evalu-
ation context (L1+L3+L4 + user goal) should raise the AgentDojo TPR if goal-awareness is the
missing information. Result: TPR declined from 14.8% to 8.3%—below the no-injection baseline.
This rejection has an informative interpretation: appending the user goal as a text prefix does not
constitute structured goal-action alignment. The gate’s intent decomposition logic cannot compare
the injected goal to the observed action without explicit structural scaffolding (e.g., a “goal vs. ac-
tion” contrast prompt). Three confounding factors compound this: (a) the ground-truth AgentDojo
pipeline evaluates task success, not injection semantics; (b) simple text injection may activate over-
cautious benign-task blocking; and (c) the pilot sample size (N = 12) is too small for significance.
P1 remains open: the mechanism requires structured goal-context integration, not raw text concate-
nation.
P2 (Context Deprivation) — Prediction Confirmed. Stripping world-context from the semantic
defense should reproduce symbolic-gap behavior. We evaluate the generic LLM classifier under
two conditions: (i) Full Group—standard evaluation with full agent-context prompt; (ii) Stripped
Group—evaluation with only the raw tool name and parameter, no surrounding task description.
The stripped condition yields R = 3.60, exceeding the P2 falsification threshold (R ≤ 1.5). When
deprived of context, the semantic defense degrades to near-symbolic gap behavior, confirming Hy-
pothesis 2: the stability of semantic detection depends on access to world-context, not on model
reasoning capacity per se. The finding identifies information deprivation as a key factor associated
with the detection gap.


                                                   9
5     Production Deployment Evidence
Nous was deployed in shadow mode alongside an existing rule-based system in a production multi-
agent environment for 11+ days (30,204 calls total).
Consistency: 99.47% agreement with the existing rule-based system across all calls—confirming
that semantic reasoning does not introduce systematic drift from established policy.
False negative recovery: Nous detected 157 cases that the existing rule-based system passed as
benign. Manual review of a stratified sample confirmed these were true positives, predominantly
ambiguous read-then-send workflows where the send target fell outside the owner’s trust boundary.
Caveat: the manual review was conducted by the system developer (first author), not an independent
auditor, and was not blind to Nous’s verdict—creating potential confirmation bias. These results
should be interpreted as case-level observations, not as a controlled study.
Over-blocking: Nous over-blocked in 4 cases where the existing system correctly allowed. Man-
ual review confirmed all 4 were over-triggered on ambiguous read-then-send workflows where the
send target was a legitimate internal address. (Same caveat as above: non-blind, author-conducted
review.)
Following the shadow period, Nous was promoted to primary interceptor. No regressions were
observed post-cutover.

6     Discussion
6.1   Why Generic Defenses Fail on Owner-Harm

The production and benchmark results converge on the same explanation: generic defenses evaluate
action content without owner context. The action “send email to external@domain.com” carries no
harm signal by content; its harmfulness is entirely determined by whether external@domain.com
is within BO . Content classifiers, injection detectors, and DLP systems operating without RO , BO ,
and AuthO cannot make this determination.
The controlled experiment (Section 4.5) provides a more precise attribution. The 85.2 pp gap arises
specifically from the symbolic rule layer (L1), which encodes environment-specific tool-name black-
lists derived from the AgentHarm training distribution rather than semantic harm patterns. The se-
mantic layer (L3) alone shows no comparable gap—and the generic zero-shot LLM, which operates
purely on semantic content without any symbolic rules, exhibits only a 3.4 pp cross-benchmark
gap. This has concrete implications for defense design: symbolic rules provide near-perfect cover-
age within their training distribution but catastrophically fail to generalize to novel tool vocabular-
ies. Upgrading from tool-name blacklists to parameter-semantic analysis (e.g., detecting attacker-
controlled IBANs or exfiltration-destination emails regardless of the calling tool name) is the single
most impactful architectural change for cross-environment generalization.
The AgentDojo structural blind spots (Section 4.2) reveal an orthogonal gap: malicious-parameter
attacks succeed because the gate context does not include the user’s task goal. The fundamental
information needed to compare “user requested X, agent doing Y” is absent from runtime gate
evaluation.
The SSDG experiments (Section 4.6) provide a more precise formulation: information deprivation
is the structural factor, not semantic difficulty. P2 confirms that stripping context from an otherwise
capable semantic defense reproduces symbolic-level gaps (R = 3.60). P1’s rejection is equally
informative—it shows that goal awareness is necessary but not sufficient: the defense must be ar-
chitecturally capable of comparing goal to action, not merely receive the goal as a text fragment.

6.2   Symbolic vs. Semantic Generalization

The controlled experiment, together with the SSDG theoretical framework (Hypotheses 1–2), ex-
poses a fundamental asymmetry between the two primary detection mechanisms in compositional
safety architectures:
Symbolic rules (L1 Datalog) exhibit a bimodal generalization profile: near-perfect recall within the
training distribution (100% on AgentHarm), and near-zero recall on out-of-distribution tool vocab-


                                                  10
ularies (3.7% on AgentDojo). This is structurally expected—Datalog rules encode extensional facts
(“tool t is prohibited”) rather than intensional harm semantics. Any tool name not in the rule set is
trivially allowed.
Semantic reasoning (L3 gate and generic LLM) exhibits a flat generalization profile: below-
perfect recall within distribution (62.7% for the generic LLM on AgentHarm), but stable recall
across environments (59.3% on AgentDojo, gap = 3.4 pp). Semantic reasoning transfers because
harm intent is encoded in goal descriptions—which remain semantically consistent across tool-
vocabulary changes—rather than in tool names.
This asymmetry has a direct design implication for compositional architectures: the value of com-
bining symbolic and semantic layers is not simply “two layers are better than one.” The layers
have complementary generalization curves: symbolic rules provide high-precision coverage in-
distribution, and semantic reasoning maintains consistent coverage out-of-distribution. A system
relying solely on symbolic rules will exhibit catastrophic degradation on novel tool environments;
a system relying solely on semantic reasoning will accept a consistent recall ceiling but generalize
robustly. The composable architecture’s value is precisely that it avoids both failure modes.

6.3   Layer Complementarity on Hijacking

The Hijacking result (43.3% gate → 93.3% combined) provides direct evidence of architectural
complementarity. The gate operates on prompt semantics and command surface; the verifier operates
on file contents and multi-step behavioral sequences. These detection dimensions are orthogonal for
prompt-injection attacks:

       • When the injection is semantically explicit (e.g., “ignore previous instructions”), the gate
         catches it; the verifier sees no artifact yet.
       • When the injection is embedded in a file artifact (e.g., a calendar event description or email
         body that the agent reads and acts upon), the semantic gate evaluates the agent’s action,
         which may be semantically plausible; the verifier detects the injection fingerprint in the
         artifact content.
       • When both signals are present, both layers fire (25% of cases).

This architectural insight—that prompt injection requires both semantic and behavioral-sequence
detection—is a transferable design principle for agent safety systems.

6.4   Implications for Benchmark Design

The AgentDojo 3.7%→14.8% result implies a design gap in existing injection benchmarks: they
do not provide explicit owner context. A benchmark that injects into the gate context (a) which
resources belong to the owner, (b) who is in the owner’s trust boundary, and (c) what the user’s
task goal is, would enable defenses to reach the estimated 40–60% ceiling and would meaningfully
differentiate owner-harm defense strategies.
We recommend future benchmarks include an owner context manifest: a structured specification of
RO , BO , and AuthO provided to both the agent and any runtime safety system.

6.5   Limitations

      1. AgentDojo ceiling: Without user task goal context, the semantic gate cannot compare
         “user requested X” to “agent doing Y”, limiting achievable safety to ∼15% on malicious-
         parameter tasks.
      2. Benchmark independence: The Owner-Harm Benchmark is author-constructed after sys-
         tem optimization. It is diagnostic, not validation evidence.
      3. Single annotator: No inter-annotator agreement is reported for the Owner-Harm Bench-
         mark labels.
      4. Structural boundary: 4/60 Hijacking cases (SQL file injection, direct SSH key injection)
         are out of reach of current V-rules.


                                                  11
      5. Evaluation mode: AgentDojo evaluation uses ground-truth mode without an adversarial
         attack LLM; real-world adaptive adversaries may achieve different results.
      6. Infrastructure Exposure FPR: Rule OH-R3a over-triggers on benign external-channel
         configuration queries (20% FPR for C2), indicating the rule requires further refinement.
      7. SSDG pilot scale: P1 and P2 experiments use N = 12 AgentDojo tasks and N = 15
         AgentHarm scenarios. Conclusions are directionally consistent with theory but require
         full-benchmark replication before statistical significance can be claimed.

6.6   Future Work

Structured goal-action alignment. The P1 SSDG experiment reveals that simply injecting the
user’s task goal as text is insufficient—the gate must be architecturally restructured to perform an
explicit goal-vs.-action comparison. A dedicated “goal alignment prompt” that contrasts the user’s
authorized intent against the agent’s proposed action is the concrete next step, estimated to raise
AgentDojo safety from 14.8% to 40–60%.
UEBA for AI agents. User and entity behavioral analytics adapted for AI agent deployments would
enable per-owner behavioral profiles, providing a personalized baseline for anomaly detection.
Adaptive immunity. Systems that learn owner-harm patterns from deployment logs—incorporating
newly discovered injection patterns into Datalog or V-rule libraries without manual rule authoring.
SQL-aware file content analysis. Addressing the 4 structural boundary Hijacking cases requires
content-aware analysis of structured file formats, beyond the current regex-based V-rules.
Owner context manifest standard. A community standard for specifying RO , BO , and AuthO in
a machine-readable format, to enable principled owner-harm benchmarking across systems.
Per-decision proof-obligation synthesis. Ongoing work extends this compositional gate from
offline-authored Datalog rules to per-decision runtime synthesis of Datalog proof obligations by
the LLM itself, admitted through a compile-time gate that rejects perturbation-invariant or decisive-
primitive-less rules. This moves verification from a “statute” (pre-authored policy) to a “case-law”
(per-decision argued) model; a companion preprint is in preparation.

7     Related Work
Agent safety and harm taxonomies. AgentHarm Andriushchenko et al. [2025] provides the most
comprehensive generic harm benchmark for LLM agents, covering 11 categories from cybercrime
to fraud. ToolEmu Ruan et al. [2024] evaluates LM agent risks in an LM-emulated sandbox with
7 risk types, partially overlapping our taxonomy but without an owner-centric perspective. AGrail
Liu et al. [2025] proposes a hierarchical safety framework for agentic systems with adaptive safety
detection. Our work differs by (a) formally defining the owner as the harm victim, and (b) providing
quantitative evidence of the resulting defense gap.
Prompt injection. Greshake et al. Greshake et al. [2023] first systematically analyzed indirect
prompt injection, demonstrating that LLM-integrated applications can be compromised through in-
jected third-party content. AgentDojo Debenedetti et al. [2024] provides standardized evaluation of
injection defenses across realistic agentic tasks. CaMeL Debenedetti et al. [2025] addresses prompt
injection via capability-aware information flow, preventing data exfiltration at the language model
level rather than the runtime layer.
Runtime safety systems. NeMo Guardrails Rebedea et al. [2023] provides programmable rails for
LLM applications. Llama Guard Inan et al. [2023] implements LLM-based input/output safeguards.
ShieldGemma Zeng et al. [2024] offers generative content moderation. R2Guard Chen et al. [2024]
provides runtime guardrails specifically designed for agent tool calls, and AgentMonitor Yu et al.
[2024] offers real-time behavior monitoring. BIPIA Yi et al. [2023] benchmarks indirect prompt
injection attacks complementary to our analysis. These systems operate primarily on content clas-
sification; none model owner-context dimensions (RO , BO , AuthO ). Guardrails AI Guardrails AI
[2024] provides composable input/output guards but without owner-harm semantics. Doshi et al.
Doshi et al. [2026] propose verifiable tool safety via type systems, complementary to our runtime
detection approach.


                                                 12
Policy-driven agent enforcement (2025–2026). A rapidly growing body of work explores policy-
driven runtime enforcement for LLM agents. PCAS Palumbo et al. [2026] compiles a Datalog-
derived declarative policy language offline and enforces it through a reference monitor. AgentSpec
Wang et al. [2026] provides a lightweight DSL of triggers, predicates, and enforcement actions.
Pro2Guard He et al. [2025] adds probabilistic reachability via learned DTMCs over execution traces.
Solver-Aided verification Roy et al. [2026] translates natural-language tool-use policies into SMT-
LIB constraints offline and verifies each call with Z3. ShieldAgent Chen et al. [2025] constructs
probabilistic rule circuits from policy documents with formal-verification tool support. GuardA-
gent Xiang et al. [2024] synthesizes a guardrail plan and executes it as code, and TrustAgent Hua
et al. [2024] inserts an Agent Constitution post-planning check. These systems focus on policy ex-
pressiveness and offline authorability; our contribution is orthogonal: the owner-context dimensions
(RO , BO , AuthO ) must be inputs to any such policy regardless of its authoring method, yet are
absent from the input vocabularies of all systems surveyed here.
Exfiltration and covert channels. Rehberger Rehberger [2024] demonstrated ASCII smuggling
via Microsoft 365 Copilot, encoding sensitive data in Markdown rendered by the victim’s browser.
The PromptArmor Slack AI disclosure PromptArmor [2024] demonstrated credential exfiltration
via injected prompts. Abdelnabi et al. Abdelnabi et al. [2024] provide a systematic analysis of
adversarial attacks on LLM-based agents.
Post-gate auditing. Intrusion detection systems Liao et al. [2013] provide a conceptual precedent
for behavioral sequence auditing after an initial gate, applied here to AI agent tool-call sequences.
Provably safe systems. Tegmark and Omohundro Tegmark and Omohundro [2023] argue that only
formally verifiable systems can achieve controllable AGI, motivating the Datalog layer’s emphasis
on decidable rule-based reasoning.


8   Conclusion

Owner-harm is a systematically under-studied threat category in AI agent safety. We formalize
it with eight categories and precise definitions, grounded in real incidents from 2023–2026. We
demonstrate the defense gap quantitatively: a compositional safety system achieving 100% on
generic criminal harm (AgentHarm) scores only 3.7%/14.8% on prompt-injection-mediated owner
harm (AgentDojo), with specific structural causes attributed to each failure mode. We show that
compositional detection—combining a semantic gate with a deterministic post-audit verifier—
achieves 93.3% on the hardest sub-category (Hijacking), with the two layers operating on orthogonal
detection signals.
The core finding is conceptually simple: existing defenses are owner-context-blind. An action is
harmful to an owner not because of its content in isolation, but because of how it relates to the
owner’s resources, trust boundary, and authorization scope. Until safety systems model these con-
text dimensions explicitly, owner-harm will remain a systematic blind spot—even as generic harm
detection reaches saturation.


Author Contributions

D.Z. conceived the Owner-Harm threat model, designed and implemented the four-layer Nous sys-
tem, ran all experiments on AgentHarm and AgentDojo, and drafted the manuscript. Y.J. (knowledge
graph specialist, Tongji University) contributed to the initial research design discussions, provided
critical review of the symbolic–semantic architecture and the owner-harm category taxonomy, and
reviewed final manuscript revisions. Both authors approved the final version and are accountable for
the integrity of the work.


References
Sahar Abdelnabi, Kai Greshake, Shailesh Mishra, Thorsten Holz, and Mario Fritz. (ab)using LLMs:
  Adversarial attacks on LLM-based agents. arXiv:2407.01902, 2024.


                                                 13
Maksym Andriushchenko, Francesco Croce, and Nicolas Flammarion. Agentharm: A benchmark
 for measuring harmfulness of llm agents. In Proceedings of the International Conference on
 Learning Representations (ICLR), 2025. Poster #32106.
British Columbia Civil Resolution Tribunal. Air Canada chatbot unauthorized refund commitment.
  BCCRT Decision #SC-2023-007829, February 2024.
Yili Chen et al. R2guard: Runtime guardrails for llm agents. 2024.
Zhaorun Chen et al. ShieldAgent: Shielding agents via verifiable safety policy reasoning. In Pro-
  ceedings of the International Conference on Machine Learning (ICML), 2025. arXiv:2503.22738.
Edoardo Debenedetti, Jie Zhang, Mislav Baader, and Florian Tramèr. AgentDojo: A dynamic envi-
  ronment to evaluate prompt injection attacks and defenses for LLM agents. In NeurIPS, 2024.
Edoardo Debenedetti, Mislav Balunovic, Florian Tramèr, et al. CaMeL: Defeating prompt injections
  by design. In arXiv:2503.18813, 2025.
Aarya Doshi et al. Towards verifiably safe tool use for LLM agents. In ICSE NIER 2026, 2026.
Kai Greshake, Sahar Abdelnabi, Shailesh Mishra, Christoph Endres, Thorsten Holz, and Mario
  Fritz. Not what you’ve signed up for: Compromising real-world LLM-integrated applications
  with indirect prompt injections. arXiv:2302.12173, 2023.
Guardrails AI.           Guardrails ai:        Input/output    guards   for    llm   applications.
  https://www.guardrailsai.com, 2024.
Haoyu He et al. Pro2Guard: Proactive runtime enforcement of LLM agent safety via probabilistic
  model checking. arXiv:2508.00500, 2025.
Wenyue Hua et al. TrustAgent: Towards safe and trustworthy LLM-based agents through agent
 constitution. arXiv:2402.01586, 2024.
Hakan Inan, Kartikeya Upasani, Jianfeng Chi, et al. Llama guard: Llm-based input-output safeguard
  for human-ai conversations. 2023. Meta AI.
Hung-Jen Liao, Chun-Hung Richard Lin, Ying-Chih Lin, and Kuang-Yuan Tung. Intrusion detection
  system: A comprehensive review. Journal of Network and Computer Applications, 36(1):16–24,
  2013.
Weidi Liu et al. AGrail: A lifelong agent guardrail with effective and adaptive safety detection.
 arXiv:2502.11448, 2025.
Nils Palumbo, Sarthak Choudhary, et al.          Policy compiler for secure agentic systems.
  arXiv:2602.16708, February 2026.
Judea Pearl. Causality: Models, Reasoning, and Inference. Cambridge University Press, 2nd edition,
  2009.
PromptArmor. Slack AI data exfiltration via prompt injection. Security disclosure, promptar-
  mor.com, August 2024.
Traian Rebedea, Razvan Dinu, Makesh Narsimhan Sreedhar, Christopher Parisien, and Jonathan
  Cohen. Nemo guardrails: A toolkit for controllable and safe llm applications with programmable
  rails, 2023. NVIDIA.
Johann Rehberger. Exfiltration of personal data using Microsoft 365 Copilot via prompt injection
  (ascii smuggling). Blog post, embracethered.com, 2024.
Arnab Roy et al. Solver-aided verification of policy compliance in tool-augmented LLM agents.
  arXiv:2603.20449, March 2026.
Yangjun Ruan, Honghua Dong, Andrew Wang, Silviu Pitis, Yongchao Zhou, Jimmy Ba, Yann
  Dubois, Chris J Maddison, and Tatsunori Hashimoto. Identifying the risks of lm agents with
  an lm-emulated sandbox. In ICLR, 2024.


                                               14
Zoe Schiffer. Meta’s ai agent incident: Unauthorized internal forum posting. The Information,
  reported by TechCrunch, March 2026. Sev 1 incident, 2h sensitive data exposure before contain-
  ment.
Max Tegmark and Steve Omohundro. Provably safe systems: the only path to controllable AGI.
 arXiv:2309.01933, 2023.
Haoyu Wang, Christopher M. Poskitt, et al. AgentSpec: Customizable runtime enforcement for safe
  and reliable LLM agents. In Proceedings of the IEEE/ACM International Conference on Software
  Engineering (ICSE), 2026. arXiv:2503.18666.
Zhen Xiang et al. GuardAgent: Safeguard LLM agents by a guard agent via knowledge-enabled
  reasoning. arXiv:2406.09187, 2024.
Jingwei Yi et al. Benchmarking and defending against indirect prompt injection attacks on large
   language models. In arXiv preprint arXiv:2312.14173, 2023.
Yue Yu et al. Agentmonitor: Real-time behavior monitoring for llm agents. 2024.
Wenhao Zeng et al. Shieldgemma: Generative ai content moderation based on gemma. 2024.
 Google DeepMind.
Zenity Research. Microsoft 365 Copilot prompt injection via calendar invites. Security research
  report, zenity.io, January 2024.




                                              15
