                                         Evaluating Long-Horizon Memory for Multi-Party Collaborative
                                                                  Dialogues
                                                              Chuanrui Hu∗                                                        Tong Li∗                                     Xingze Gao
                                                      chuanrui.hu@shanda.com                                           litong02@shanda.com                              xingze.gao@shanda.com
                                                      EverMind, Shanda Group                                          EverMind, Shanda Group                            EverMind, Shanda Group
                                                                USA                                                            USA                                                USA

                                                              Hongda Chen                                                           Yi Bai                                    Dannong Xu
                                                      hongda.chen@shanda.com                                             baiyi@shanda.com                              dannong.xu@shanda.com
                                                       EverMind, Shanda Group                                         EverMind, Shanda Group                           EverMind, Shanda Group




arXiv:2602.01313v3 [cs.CL] 11 Mar 2026
                                                                USA                                                            USA                                              USA

                                                                Tianwei Lin                                                   Xiaohong Li                                     Yunyun Han
                                                       tianwei.lin@shanda.com                                         xiaohong.li@shanda.com                            hanyunyun@shanda.com
                                                       EverMind, Shanda Group                                         EverMind, Shanda Group                            EverMind, Shanda Group
                                                                  USA                                                           USA                                              USA

                                                                                                   Jian Pei                                         Yafeng Deng†
                                                                                              j.pei@duke.edu                                  dengyafeng@shanda.com
                                                                                              Duke University                                 EverMind, Shanda Group
                                                                                                    USA                                                USA
                                         Abstract                                                                                        EverMemBench thus represents a concrete step toward realistic
                                         Long-term conversational memory in practical LLM applications is                                evaluation of LLM memory and a cornerstone benchmark for devel-
                                         inherently collaborative: information is produced by multiple par-                              oping next-generation LLMs that reason over time, roles, and collab-
                                         ticipants, scattered across groups and channels, revised over time,                             orative interaction structure. Our benchmark and code are publicly
                                         and implicitly grounded in roles and social context. Yet there is                               available at https://github.com/EverMind-AI/EverMemBench.
                                         currently no established benchmark that evaluates memory under
                                         interaction patterns resembling real-world deployment, as existing                              CCS Concepts
                                         benchmarks largely focus on dyadic or single-topic dialogues. In                                • Computing methodologies → Information extraction.
                                         this paper, we introduce EverMemBench, the first benchmark
                                         designed for long-horizon collaborative memory, built from multi-                               Keywords
                                         party, multi-group conversations spanning over one million tokens                               long-term memory, multi-party dialogue, benchmark, LLM
                                         with dense cross-topic interleaving, temporally evolving decisions,
                                                                                                                                         ACM Reference Format:
                                         and role-conditioned personas. EverMemBench evaluates memory                                    Chuanrui Hu, Tong Li, Xingze Gao, Hongda Chen, Yi Bai, Dannong Xu,
                                         systems using 2,400 QA pairs across three dimensions essential                                  Tianwei Lin, Xiaohong Li, Yunyun Han, Jian Pei, and Yafeng Deng. 2018.
                                         for real applications: fine-grained recall, memory awareness, and                               Evaluating Long-Horizon Memory for Multi-Party Collaborative Dialogues.
                                         user profile understanding. Our evaluation reveals fundamental lim-                             In Proceedings of Make sure to enter the correct conference title from your
                                         itations of current systems: multi-hop reasoning collapses under                                rights confirmation email (Conference acronym ’XX). ACM, New York, NY,
                                         multi-party attribution even with oracle evidence (26% accuracy),                               USA, 26 pages. https://doi.org/XXXXXXX.XXXXXXX
                                         temporal reasoning fails without explicit version semantics beyond
                                         timestamps, and memory awareness is bottlenecked by retrieval,                                  1    Introduction
                                         as similarity-based methods miss implicitly relevant information.                               Large language models are increasingly deployed as conversational
                                         ∗ Equal contribution                                                                            agents in settings where interactions extend over time, span con-
                                         † Contact author                                                                                texts, and involve multiple participants [3, 13, 39]. In practical ap-
                                                                                                                                         plications such as workplace collaboration and personal assistance,
                                         Permission to make digital or hard copies of all or part of this work for personal or
                                         classroom use is granted without fee provided that copies are not made or distributed           conversational memory is inherently collaborative: information is
                                         for profit or commercial advantage and that copies bear this notice and the full citation       produced by different people, scattered across groups and channels,
                                         on the first page. Copyrights for components of this work owned by others than the              revised as decisions evolve, and implicitly shaped by roles and so-
                                         author(s) must be honored. Abstracting with credit is permitted. To copy otherwise, or
                                         republish, to post on servers or to redistribute to lists, requires prior specific permission   cial relations. These settings impose two fundamental challenges
                                         and/or a fee. Request permissions from permissions@acm.org.                                     for memory systems. First, conversations are often multi-party, re-
                                         Conference acronym ’XX, Woodstock, NY                                                           quiring the system to track who said what and how information
                                         © 2018 Copyright held by the owner/author(s). Publication rights licensed to ACM.
                                         ACM ISBN 978-1-4503-XXXX-X/2018/06                                                              propagates across speakers and groups [7, 9, 30]. Second, effective
                                         https://doi.org/XXXXXXX.XXXXXXX                                                                 memory goes beyond verbatim recall, demanding the ability to
Conference acronym ’XX, June 03–05, 2018, Woodstock, NY                                                                                                                Hu et al.


                  Aspects                          LoCoMo            LongMemEval           PersonaMem-v1            PersonaMem-v2              EverMemBench (Ours)
                  Dialogue Characteristics
                  Interaction Type                  Dyadic           User–Assistant          User–Assistant          User–Assistant            Multi-party Group
                  Task Structure                 Single-session        Long-term              Personalized          Preference-based        Long-term Interdependent
                  Dialogue Turns                     326.8               493.5                   313.6                    448.5                     10,204.6
                  Context Length                       9K                1.5M                     1M                      128K                         1M
                  Personas per Batch                    2                  1                       1                        1                         37.6
                  Dialogue Features
                  High-Info Dialog Flow                 ✗                    ✗                       ✗                       ✗                           ✓
                  Diverse Persona Interaction           ✗                    ✗                       ✗                       ✗                           ✓
                  Cross-Topic Interaction               ✗                    ✗                       ✗                       ✗                           ✓
                  User Knowledge Update                 ✗                    ✗                       ✓                       ✓                           ✓
                  Evaluation Dimensions
                  Fine-Grained Recall                   ✓                    ✓                       ✓                       ✓                           ✓
                  Memory Awareness                      ✗                    ✗                       ✓                       ✓                           ✓
                  Profile Understanding†                ✗                    ✗                       ✗                       ✗                           ✓
                                       † Profile Understanding denotes implicit user modeling from long-term dialogue, not explicit profile retrieval.

Table 1: Comparison with prior conversational memory benchmarks. EverMemBench uniquely supports multi-party group
conversations with long-term interdependent tasks, high information density, and rich persona interaction.


retain fine-grained details for precise retrieval [22, 35], recognize                              is built from information-dense dialogues in which multiple roles
when past information becomes relevant in new situations [29, 34],                                 participate across interconnected group chats, exhibiting coherent
and respond consistently with user preferences, expertise, and so-                                 cross-topic interleaving and revisiting of earlier decisions rather
cial context [14, 41, 42].                                                                         than isolated topic sessions. It features diverse personas with role-
    Despite rapid progress in long-context modeling and memory-                                    conditioned skills and communication styles, and models dynamic
augmented agents, evaluation has not kept pace. Many benchmarks                                    user knowledge where earlier information can be revised as con-
implicitly equate stronger memory with the ability to process more                                 straints change. A high-level comparison with prior benchmarks is
tokens, treating memory as recall over long inputs [14, 22, 26, 31,                                shown in Figure 1.
35]. In practice, however, failures rarely stem from context length                                   To systematically assess these challenges, EverMemBench evalu-
alone [18, 21]. Instead, systems break down due to confusion about                                 ates memory systems along three dimensions that are essential for
attribution in group chats, interference across closely related topics,                            collaborative assistants: fine-grained recall for accurately retriev-
inconsistency in persona and style, and inability to update beliefs                                ing specific entities from dense, multi-party discussions, memory
when plans or constraints change. At the same time, recent memory-                                 awareness for comprehending stored knowledge and applying it
augmented systems [5, 17, 20, 25, 28] increasingly attach persistent                               to novel, unseen scenarios, and profile understanding for main-
or structured memory to LLMs for long-horizon personalization                                      taining consistency with user preferences, expertise, and roles. Ex-
and task continuity. Their growing deployment heightens the need                                   periments on both long-context LLMs and memory-augmented
for benchmarks that reflect realistic conversational dynamics, as it                               systems reveal persistent limitations across all three dimensions.
remains unclear which memory designs improve behavior under                                           In summary, this paper makes three contributions. First, we in-
collaborative, evolving interactions rather than only boosting recall                              troduce EverMemBench, the first benchmark explicitly designed
in constructed long contexts. This gap between existing benchmarks                                 to evaluate long-horizon memory in multi-party, multi-group con-
and practical memory demands is summarized in Table 1.                                             versational settings, featuring information-dense dialogues across
    A closer examination reveals that current benchmarks systemat-                                 five projects, each spanning one million tokens, with coherent
ically underrepresent the structure of real interactions. Most focus                               cross-topic interaction, role-conditioned personas, and dynamic
on dyadic conversations [12], whereas real-world settings involve                                  knowledge updates that mirror real-world collaboration. Second, we
multiple roles contributing to shared, interdependent decisions.                                   propose three evaluation dimensions—fine-grained recall, mem-
Long contexts are often created by injecting topic-irrelevant dis-                                 ory awareness, and profile understanding—that directly capture
tractors [4, 16, 26], which tests noise tolerance but not relevance                                the core capabilities required for effective collaborative memory,
recognition in coherent, interleaved dialogues. Persona modeling                                   moving beyond token-level recall to relevance recognition and per-
is typically shallow, failing to capture how communication style                                   sona consistency. Third, through systematic experiments on both
and expertise emerge from role relations and repeated interac-                                     long-context LLMs and memory-augmented systems, we reveal
tion [14, 40]. Finally, many benchmarks assume stationary facts,                                   persistent structural limitations: multi-hop reasoning collapses un-
while real conversational memory must support explicit updates,                                    der multi-party attribution, temporal reasoning degrades as topic
revisions, and conflict resolution as information evolves over time.                               interleaving obscures event lifecycle boundaries (initiation, com-
    To bridge this gap, we introduce EverMemBench, a benchmark                                     pletion, archival), and similarity-based memory retrieval fails to
designed to evaluate long-horizon memory under interaction pat-                                    surface implicitly relevant information. Together, these contribu-
terns that closely resemble real-world deployment. EverMemBench                                    tions position EverMemBench as a concrete step toward realistic
Evaluating Long-Horizon Memory for Multi-Party Collaborative Dialogues                      Conference acronym ’XX, June 03–05, 2018, Woodstock, NY




Figure 1: Existing benchmarks vs. EverMemBench. Existing benchmarks focus on dyadic, single-topic sessions. EverMemBench
models multi-party collaboration across interdependent groups, where information is distributed across speakers, channels,
and time, requiring cross-group reasoning and temporal tracking absent in dyadic settings.


evaluation of LLM memory and a cornerstone benchmark for de-             with tasks that disentangle detailed recall, memory awareness, and
veloping next-generation LLMs that reason over time, roles, and          user profile understanding.
collaborative interaction structure.
                                                                             Memory-Augmented Systems and Architectures. Memory-
                                                                         augmented systems increasingly treat memory as an explicit
2    Related Work                                                        component that can be persisted, structured, retrieved, and updated,
   Long-Context Conversational Memory Benchmarks. Recent bench-          with designs ranging from pragmatic memory layers to more
marks evaluate long-horizon conversational memory from multiple          autonomous organization and OS-level abstractions. Mem0 [5]
perspectives, including long multi-session interaction, capability-      and MemInsight [28] propose scalable persistent memory layers
factorized assistant memory, and dynamic personalization. Lo-            that extract salient information from conversational histories and
CoMo [22] focuses on very long multi-session conversations with          retrieve it when needed. Zep [27] takes a different approach, build-
tasks such as question answering and event summarization. Long-          ing memory on a temporal knowledge graph whose bi-temporal
MemEval [35] decomposes chat-assistant memory into abilities             model tracks both event time and ingestion time, enabling conflict
including information extraction, multi-session and temporal rea-        resolution as facts evolve. MemoBase [23] organizes memory
soning, knowledge updates, and abstention. PersonaMem [14] em-           as structured user profiles with developer-defined schemas,
phasizes dynamic user profiling and personalization over extended        prioritizing user-centric personalization over general-purpose
user–LLM histories. More recent efforts further broaden coverage of      retrieval. Beyond persistent stores, A-MEM [36] frames memory
memory abilities and dialogue settings, including MemBench [31],         as an agentic module that decides what to store and how to
MADial-Bench [11], and BEAM [32].                                        use it, while Nemori [25] proposes self-organizing memory
   Despite their differences, these benchmarks share a simplify-         emphasizing structured organization and evolution. Another line
ing assumption: interactions are dyadic or centered on a single          elevates memory to an infrastructure abstraction: MemOS [20]
user and a single assistant. Even when multiple speakers exist,          and MemoryOS [17] treat memory as an OS-like resource,
interdependence across roles and groups and explicit attribution         aiming to unify heterogeneous memories with scheduling and
reasoning are typically not treated as first-class evaluation targets.   lifecycle management. Across these designs, retrieval-augmented
This assumption fundamentally simplifies attribution, relevance,         generation commonly serves as the backbone for accessing external
and update reasoning, and consequently under-stresses collabo-           or long-range information [2, 4, 10, 19, 37, 38].
rative phenomena that dominate real applications, such as dense              While architecturally diverse, these systems are predominantly
multi-party attribution, coherent cross-topic interleaving, persona      evaluated in dyadic or single-user settings that obscure the chal-
shifts under social context, and non-stationary user knowledge           lenges they are designed to address. Such evaluations under-stress
that must be revised and reconciled. EverMemBench departs from           multi-party attribution, cross-group dependency, temporal revision,
this paradigm by explicitly targeting multi-party group chat with        and persona consistency under shifting social context, making it
high information density, interdependent tasks, diverse personas         difficult to distinguish memory mechanisms that truly support re-
shaped by role relations, and evolving knowledge states, together        alistic collaboration from those that succeed only under simplified
Conference acronym ’XX, June 03–05, 2018, Woodstock, NY                                                                                                                   Hu et al.


 Fine-grained Recall
 Single-hop          Retrieves precise entities while filtering out semantically similar distractors (e.g., intermediate drafts).
 Retrieval           Q: What’s the link to Person Q’s final deliverable for Task A? ✓ Confluence link × Figma link (same speaker, same task, 2 days earlier)
 Multi-hop           Traces an individual’s work timeline across fragmented threads and groups via multi-hop reasoning
 Trajectory          Q: What is the next task assigned to the owner of Task A after completing Task A? ✓ Task B × Task C (Finds the person but fails to infer the next step)
 Temporal            Extracts time spans from noisy contexts with identical phrases and adjacent dates.
 Duration            Q: How many days from Task A start to archival? ✓ 7 days × 264 days (find the wrong anchor)
 Memory Awareness
 Constraint          Apply implicit organizational norms and constraints from prior memories to guide decisions in an generalize scenario
                     Q: A new field must be added to the shared schema—who should own the change? ✓ Dev A (10+ msgs related, definer) × Dev B (30+ msgs, consumer)
 Proactivity         Proactively recall explicit rules and detect conflicts when an unseen task instruction would violate them, remaining robust to leading or persuasive framing.
                     Q: The customer will sign today if we offer 25% off—draft the contract now!! ✓ Remaider: 25% off needs pre-approval; × Draft the contract
 Update              Tracks rule evolution, composing base protocols with later overrides to apply the updated policy.
                     Q: For a new service created after the 2026-01-15 policy update, which CI should we use? ✓ GitHub Actions (current policy)        × Jenkins (old handbook)
 Profile Understanding
 Style               Generate a personalized response that matches an individual’s implicit communication style inferred from prior dialogues (tone/structure/verbosity).
                     Q: Draft a project update on this user’s behalf. ✓ Terse bullets with jargon (matches user) × Formal paragraphs (generic tone)
 Skill               Infer and apply a persona’s competence boundary from long-term memory, producing recommendations that match what the speaker would realistically
                     propose (and rejecting overly generic best-practice suggestions).
                     Q: How should person A optimize this service quickly? ✓ JVM profiling + GC tuning (Java) × Use pandas tooling (Pythons, beyond A’s capabilitie)
 Role                Adopt the speaker’s professional role perspective when responding.
                     Q: Write a post-mortem for the service outage. ✓ User impact, SLA breach, process gaps (PM)         × Memory-leak fix, GC tuning (engineer)
         Table 2: Overview of the nine tasks with illustrative mini-cases. Full cases with evidence chains are in Appendix E.


conditions. EverMemBench provides a complementary and more                                  chaining), and Temporal (event boundary point identification) sub-
diagnostic evaluation environment, stressing memory architectures                           tasks specifically because these are the concrete operations systems
under collaborative interaction where information is distributed                            must perform in practice to, e.g., determine the final approved
across speakers, groups, and time, and enabling systematic analysis                         budget or the actual assignee after several revisions.
of how different designs succeed or fail in practice.                                          Memory Awareness tests whether a system can move beyond
                                                                                            simple retrieval to reason over stored information and apply it to
3     EverMemBench                                                                          novel scenarios. Our benchmark focuses on three memory-aware
                                                                                            behaviors: Constraint (norm generalization), Proactivity (conflict de-
EverMemBench is designed not merely as a synthetic data artifact,
                                                                                            tection under potentially biased instructions), and Update (rule ver-
but as a diagnostic instrument: each design choice is aimed at expos-
                                                                                            sioning and precedence). Together, these sub-tasks assess whether
ing the structural failure modes that plague deployed conversational
                                                                                            an assistant can comprehend, revise, and proactively apply its mem-
agents. Concretely, we build multi-party, multi-group dialogues
                                                                                            ories in situations it has never encountered—capabilities that are
with explicit temporal structure, role-conditioned personas, and
                                                                                            essential for deployed conversational assistants.
tightly coupled tasks so that failures in attribution, temporal revi-
                                                                                               Profile Understanding examines whether a system aggregates
sion, and inferential retrieval become visible and measurable. Below
                                                                                            distributed signals into stable user models that guide behavior.
we summarize the benchmark’s evaluation goals, the streaming
                                                                                            We evaluate Style (communication patterns), Skill (expertise-based
task protocol, and the three-stage curation pipeline that guarantees
                                                                                            choices), and Role (role focus) because real assistants must adapt
coherence, controllability, and evidentiary grounding.
                                                                                            tone, suggested actions, and assumptions based on inferred roles–
                                                                                            capabilities that cannot be verified by single-shot snippets alone.
3.1       Evaluation Dimensions                                                                Table 2 provides illustrative mini-cases for each evaluation di-
We evaluate LLMs as long-term collaborators in settings where                               mensions.
failures are not caused by token limits alone but by interaction
structure. Prior dyadic benchmarks miss these failure modes be-
cause they hide attribution and revision complexity behind single-                          3.2      Task Formulation
threaded dialogs [14, 15, 22, 35]. To make the missing challenges                           We pose a streaming multi-group protocol to mirror deployment:
explicit, EverMemBench defines three complementary task families                            5 projects (diverse domains) run independently; each contains 𝑁
that together capture the core competencies required for realistic                          groups that converse daily over a simulated year. This protocol
collaboration.                                                                              forces systems to make deployment-style decisions—what to store,
   Fine-grained Recall measures whether a system can retrieve                               when to update, and how to attribute—rather than relying on retro-
precise facts from dense, multi-turn discussions where relevant evi-                        spective full-history inspection. During the ingestion phase the
dence is scattered across speakers and groups. We include Single-hop                        system receives daily batches {𝑀𝑑,𝑔 }𝑔=1
                                                                                                                                  𝑁 (chronologically ordered

(local grounding and entity disambiguation), Multi-hop (cross-group                         multi-party messages per group) and must autonomously construct
Evaluating Long-Horizon Memory for Multi-Party Collaborative Dialogues                              Conference acronym ’XX, June 03–05, 2018, Woodstock, NY




Figure 2: Data curation pipeline of EverMemBench. Stage 1 builds organizational structure, persona profiles, and sub-task
assignments; Stage 2 generates daily dialogues conditioned on hierarchical summaries; Stage 3 produces QA pairs with three-
phase quality control.

and maintain a memory state. During the evaluation phase we                    3.3.2 Blueprint Generation. For each project 𝑝 ∈ P we build a
pose (1) multiple-choice queries for high-precision diagnosis and              blueprint 𝐵𝑝 = (E𝑝 , {(E𝑝,𝑗 , T𝑝,𝑗 )}3𝑗=1 ) that encodes team member-
(2) open-ended queries judged by an LLM for semantic equivalence;              ship, overlapping assignments, and sub-task timelines. The blue-
every query is annotated with evidence spans to enable oracle vs.              print enforces global consistency (who can decide what, expected
retrieval analyses. This formulation intentionally separates the stor-         task durations, dependency structure), which is crucial: without
age problem from the reasoning problem so that we can determine                a global plan, dialogue synthesis either degenerates into incoher-
whether failures arise from retrieval, representation, or the answer           ent chatter or becomes artificially easy by exposing explicit deci-
model itself.                                                                  sion summaries. The blueprint therefore creates structured diffi-
                                                                               culty—complex but verifiable interactions that mirror real projects.
                                                                               3.3.3 Conversation Generation. Dialogues are generated day-
                                                                               by-day for 𝐷 simulated days, with each sub-project maintaining
3.3     Data Construction                                                      a group chat. To preserve long-range coherence under context
Building coherent, long-horizon, multi-party dialogues presents                limits [33], we apply hierarchical summarization:
three practical challenges: context truncation, logical drift, and per-
                                                                                             (𝑑 )                (𝑑 −7:𝑑 −1)
                                                                                                                             , T𝑝,𝑗(𝑑 −7:𝑑 −1) ,
                                                                                                                                              
sona/temporal incoherence. We address these not as engineering                            𝑊𝑝,𝑗    = Summarize 𝐶𝑝,𝑗                                   (1)
trivia but as necessary controls: without them, benchmark items risk                         (𝑑 )                (𝑑 −30:𝑑 −1)       (𝑑 −30:𝑑 −1) 
                                                                                          𝑀𝑝,𝑗 = Summarize 𝐶𝑝,𝑗               , T𝑝,𝑗               , (2)
being unsound (unanswerable) or trivial (solvable without context).
                                                                                             (𝑑 )                 (𝑑 −1) 
Our pipeline (Figure 2) therefore balances realism with repeatabil-                        𝐿𝑝,𝑗 = Extractleader 𝐶𝑝,𝑗       .                         (3)
ity through three stages: (1) blueprint and profile generation, (2)
                                                                               These summaries are used exclusively as internal scaffolding during
chunk-wise dialogue synthesis with hierarchical summarization,
                                                                               data generation and are never exposed to models during ingestion
and (3) evidence-grounded QA construction. All generative steps
                                                                               or evaluation. Weekly and monthly summaries plus leader instruc-
use Gemini-2.5-Pro [6] for consistency; human-in-the-loop checks
                                                                               tions compress history while preserving the temporal scaffolding
ensure plausibility and traceability.
                                                                               needed to test version reasoning; this is an essential (not cosmetic)
                                                                               mechanism because many temporal errors arise from lost structural
                                                                               cues rather than missing tokens. We generate each day’s conversa-
3.3.1 Preliminaries. We instantiate a controlled organizational                tion in a single pass conditioned on these summaries and persona
skeleton 𝑆 with 170 employees E across 7 departments and                       profiles:
five projects P. Each employee receives a persona 𝜋𝑒 =                                   (𝑑 )
                                                                                              = LLMdialog T𝑝,𝑗(𝑑 ) ,𝑊𝑝,𝑗
                                                                                                                      (𝑑 )    (𝑑 ) (𝑑 )                 
                                                                                      𝐶𝑝,𝑗                                 , 𝑀𝑝,𝑗 , 𝐿𝑝,𝑗 , {𝜋𝑒 }𝑒 ∈ E𝑝,𝑗 .
(rank𝑒 , dept𝑒 , role𝑒 , s𝑒 , c𝑒 ) where s𝑒 (40–60 skills) and c𝑒 (8D style)
capture capabilities and communication tendencies. This design                 Every generated block is validated by logic, profile, and progress
choice is essential: roles and skill overlaps create the cross-group           checks; failures trigger bounded regeneration. This produce–verify
dependencies and style shifts that reveal whether a system truly               loop is deliberate: it trades raw spontaneity for reproducible realism
models users rather than matching surface patterns.                            so that QA items have precise evidence anchors.
Conference acronym ’XX, June 03–05, 2018, Woodstock, NY                                                                                                             Hu et al.


               Statistic                                  Value                             EverMemBench QA Distribution
               Organizational Structure
                 # Projects / Sub-projects           5 / 15                                                              oral            Ski
                                                                                                                   Temp       )              ll
                                                                                                                         2.5%           16
                 # Employees                            170                                                       300 (1             (7. 9
                                                                                                                                        0%
                                                                                                                                           )
                    Executive / Manager / Staff 1 / 5 / 164                                Mu                                                          e
                                                                                                                                                    yl
                                                                                          9 lti-h                                                 St 76 )
                 Avg # Participants / Project          37.6                                (1
                                                                                              0. op        e-
                                                                                                                                                     1 %
                                                                                                                                                         .3
                                                                                                4%                                                   (7
                                                                                                   )     Re gra                                 g
                                                                                                                 i
                                                                                                        (3 cal ned                       ile in
               Dialogue Statistics                                                          24
                                                                                                          1. l                         of nd )
                                                                                                            8%                       Pr sta 5%
                                                                                                      Fi                                r 2.
                                                                                                               )                      de (2             Role
                                                                                                         n
                 Time Span (days)                         365
                                                                                                                                    Un 41                196
                                                                                                               2

                                                                                   Single-hop
                                                                                                             76                                              )
                                                                                                                        Total QA      5                 (8.2%
                 Total Dialogue Turns                  51,023
                 Total Tokens                       4,225,555
                                                                                   213 (8.9%)                           2400
                 Avg Tokens / Project                 845,111                                                                                                  )
                 Avg Turns / Day                         28.0                                                                                             Up
                                                                                                                                                        268 datin
                 Avg Tokens / Turn                       82.8                                                            Memory                            (11 g
                                                                                                   P                                                          .2%
                                                                                                42 ro                   Awareness
                                                                                                  7 ac
               Evaluation Statistics                                                                (1 tiv
                                                                                                      7. ity
                                                                                                                       1097 (45.7%)
                                                                                                        8%
                 # QA Pairs                               2,400                                                                             int
                                                                                                           )                           stra
                 # Evaluation Dimensions                      3                                                                   Con 6.8%)
                                                                                                                                     2 (1
                                                                                                                                  40
                 # Sub-dimensions                             9
           Table 3: Data statistics of EverMemBench.
3.3.4 Q&A Generation. We synthesize QAE triples (𝑞, 𝑎, 𝑒) via                              Figure 3: Distribution of QA pairs.
three specialized pipelines aligned to the evaluation dimensions.
                                                                        of events are targeted by QA items. This information density is
For Fine-grained Recall we use structure mining to extract nat-
                                                                        intentional: it makes retrieval fidelity, attribution, and temporal
ural multi-hop chains and non-conflicting implantation to inject
                                                                        revision the limiting factors for system performance rather than
controlled corner cases. For Memory Awareness we construct sce-
                                                                        raw context size.
narios of Updating, implicit Constraint application, and Proactivity,
                                                                           Figure 3 shows the distribution of 2,400 QA pairs across the
and we apply adversarial perturbations (keyword substitution, pa-
                                                                        three dimensions and nine sub-tasks, with balanced coverage across
rameter removal) to force semantic—rather than lexical—retrieval.
                                                                        projects (467–493 per topic). These statistics support controlled ab-
For Profile Understanding we design distractors that disentangle
                                                                        lations (e.g., oracle vs. retrieved evidence, single- vs. multi-group
factual correctness from style matching (a 2 × 2 fact-vs-style ma-
                                                                        questions) that reveal whether errors stem from retrieval granu-
trix) and craft plausible-but-wrong role inferences to test expertise
                                                                        larity, evidence fragmentation, or the answer model’s reasoning
reasoning.
                                                                        capability.
3.3.5 Q&A Quality Control. Quality control is not an after-
thought but a methodological core: items that are solvable without      4     Empirical Results
context or ambiguous with evidence would nullify diagnostic value.      We evaluate LLMs and memory-augmented systems on EverMem-
We therefore apply a three-phase filter. Phase I (Blind Test) re-       Bench to understand why current approaches fail under realistic
moves parametric leaks and trivial distractors. Phase II (Evidence      collaborative interaction, not merely how much they fail. The ex-
Grounding) partitions C𝑝 into segments S and enforces sufficiency       periments are designed to disentangle three factors that are often
(answer derivable from 𝑆 + ) and uniqueness (answer not derivable       conflated in prior work: (i) access to long context, (ii) retrieval
from any 𝑆 − ). Phase III (Human Audit) catches residual logical        quality, and (iii) reasoning over fragmented, evolving evidence. By
or pragmatic issues. This pipeline deliberately favors conserva-        systematically varying evidence access (full context, retrieval, ora-
tive retention: we keep only items with crisp evidence-to-question      cle), we show that many failures observed in practice are structural
mappings so that failures can be attributed to memory/ retrieval/       and anticipated consequences of multi-party, multi-group interac-
reasoning rather than annotation noise.                                 tion.
   These steps also guard against generator-family bias: blueprint
specifications fully constrain the factual content of each dialogue,    4.1    Experimental Setup
the generator contributes only surface realization; the blind test
                                                                           Evaluated Systems. We evaluate two categories of systems. Long-
then ensures that no item whose answer can be inferred from
                                                                        context LLMs consume the complete dialogue history, including
surface.
                                                                        Gemini-3-Flash [8], GPT-4.1-mini [1], and LLaMA-4-Scout [24], all
                                                                        supporting 1M-token contexts. Memory-augmented systems attach
3.4     Data Statistics                                                 external memory to an answer model via similarity-based retrieval,
As summarized in Table 3, EverMemBench focuses on dense,                including Zep [27], Mem0 [5], MemOS [20] and MemoBase [23]. We
deployment-relevant information: 5 projects (Technology, Opera-         use official cloud APIs and default retrieval configurations reported
tions, Marketing, Financial Services, Governance), 170 employees,       for LoCoMo: Zep and Mem0 retrieve top-𝑘=10 items; MemOS re-
51,023 turns, and 4.2M tokens (about 1M tokens per project). Unlike     trieves top-𝑘=20; MemoBase retrieves up to 3K tokens. Under this
distractor-padded long contexts [35], each 1M-token project con-        configuration, memory-augmented systems consume roughly 1K–
tains over 10,000 turns of eventful dialogue where a large fraction     3K input tokens per query, whereas full-context baselines ingest
Evaluating Long-Horizon Memory for Multi-Party Collaborative Dialogues                                             Conference acronym ’XX, June 03–05, 2018, Woodstock, NY


                                    Fine-Grained Recall                    Memory Awareness                 Profile Understanding
             Method                                                                                                                              Average
                                  Single       Multi        Temp        Const       Proact      Update     Style        Skill       Role
                                                                                GPT-4.1-mini
             Full Context       83.57±4.9 2.41±1.8   7.00±2.8          63.43±4.7   25.06±4.1 42.54±6.0 39.20±7.4      35.50±7.1   38.27±6.9    37.44±1.8
                + MemoBase      60.09±6.6 12.85±4.2 18.00±4.3          64.68±4.6   36.77±4.6 30.60±5.6 17.05±5.4      29.59±6.8   38.78±6.9 34.27±1.9 (-3.18)
                + Mem0          55.40±6.6 11.24±3.8 6.33±2.8           66.17±4.6   52.46±4.7 51.87±6.0 22.73±6.3      31.36±7.1   36.22±6.9 37.09±1.9 (-0.36)
                + Zep           73.71±5.9 8.03±3.4 13.00±3.8           67.16±4.6   47.54±4.7 43.66±6.0 26.70±6.5      35.50±7.1   44.39±6.9 39.97±1.9 (+2.52)
                + MemOS         71.36±6.1 18.88±4.8 15.67±4.0          69.90±4.5   51.99±4.7 45.15±6.0 28.98±6.5      32.54±7.1   48.47±7.1 42.55±1.9 (+5.11)
                                                                   Llama-4-Scout-17B-16E-Instruct
             Full Context       77.93±5.6     0.00±0.0      1.67±1.5   60.45±4.7   43.79±4.7 67.91±5.6 27.84±6.8      39.64±7.4   42.35±6.9    40.18±1.8
                + MemoBase      57.75±6.6     5.62±3.0     12.00±3.8   67.41±4.6   54.10±4.7 27.61±5.4 21.02±6.0      47.34±7.7   42.86±6.6 37.30±1.8 (-2.88)
                + Mem0          56.34±6.6     3.21±2.2      3.67±2.2   66.17±4.5   63.00±4.7 45.90±6.0 23.30±6.0      51.48±7.7   44.39±6.9 39.72±1.8 (-0.46)
                + Zep           71.36±6.1     4.02±2.4      7.00±2.8   67.41±4.5   52.69±4.7 35.45±6.0 27.84±6.8      46.15±7.7   46.43±7.1 39.82±1.8 (-0.36)
                + MemOS         67.61±6.1     6.43±3.0     11.33±3.5   66.92±4.5   64.17±4.7 38.43±6.0 23.86±6.2      53.25±7.7   50.00±7.1 42.44±1.9 (+2.27)
                                                                               Gemini-3-Flash
             Full Context       97.65±2.1 26.51±5.4        45.00±5.7   96.77±1.7   98.36±1.2 100.00±0.0   67.05±6.8   53.25±7.7   68.88±6.6      72.61±1.6
                + MemoBase      56.34±6.6 6.43±3.0         17.67±4.2   85.32±3.5   91.10±2.6 84.33±4.3    38.07±7.4   53.85±7.7   69.39±6.6   55.83±1.8 (-16.78)
                + Mem0          56.34±6.6 5.62±3.0          2.67±1.8   79.60±3.9   84.54±3.4 85.45±4.3    36.93±7.1   56.21±7.4   61.73±6.6   52.12±1.8 (-20.48)
                + Zep           68.54±6.1 6.02±3.0         11.00±3.5   85.82±3.4   82.44±3.5 78.36±4.9    34.66±6.8   60.95±7.4   66.33±6.6   54.90±1.8 (-17.71)
                + MemOS         69.01±6.1 10.84±3.8        20.67±4.7   81.84±3.7   87.59±3.0 90.67±3.5    38.64±7.1   62.72±7.1   71.43±6.4   59.27±1.8 (-13.34)
Table 4: Main evaluation results on EverMemBench. "Full Context" uses the complete dialogue history; memory-augmented
methods use only retrieved information. Best memory-augmented results per metric are bolded. Parenthesized values show
accuracy change vs. Full Context. Gray subscripts are half-widths of 95% bootstrap CIs (𝐵=10,000).


                       Fine-Grained Recall         Memory Awareness                          we use multiple-choice questions with carefully constructed dis-
    Model
                                                                                             tractors to prevent plausible fabrication by models without true
                       Single Multi        Temp    Const Proact Update
                                                                                             memory access. This design ensures that high scores reflect genuine
    GPT-4.1-mini       99.53    97.99      60.00   96.77     86.65     98.51                 memory use rather than surface-level plausibility.
    Llama-4-Scout      96.24    37.35      34.00   93.53     90.87     96.64
    Gemini-3-Flash     98.14    88.37      54.33   99.26     98.12     99.23
                                                                                             4.2    Fine-Grained Recall: Attribution and Time
Table 5: Oracle performance with ground-truth evidence                                              as Structural Bottlenecks
spans provided directly to the model, isolating reasoning
capability from retrieval quality.                                                           Multi-hop and temporal reasoning collapse under multi-
                                                                                             party interleaving. As summarized in Table 4, all systems perform
the entire ∼1M-token dialogue history. Unless noted otherwise,                               well on Single-hop recall (Gemini-3-Flash: 97.65%; memory systems:
all memory-augmented systems use GPT-4.1-mini as the answer                                  55–83%), indicating that isolated fact retrieval is largely solved.
model, allowing us to isolate retrieval effects.                                             However, Multi-hop accuracy drops sharply: Gemini-3-Flash falls
    Oracle Evaluation. To separate retrieval failures from reasoning                         to 26.51%, and the best memory-augmented system reaches only
limitations, we construct an oracle setting in which the ground-                             18.88%. This is not a recall problem but an integration problem.
truth dialogue segments from which each answer must be synthe-                               In EverMemBench, relevant facts are distributed across speakers,
sized are provided directly to the LLM. By bypassing retrieval en-                           groups, and days; answering correctly requires stitching together
tirely, oracle evaluation isolates each sub-dim’s reasoning demands                          partial evidence that never co-occurs in a single exchange.
over the provided evidence, which range from entity matching for                                Oracle results in Table 5 confirm this diagnosis. When provided
Single-hop to lifecycle boundary disambiguation and date arith-                              with ground-truth evidence, GPT-4.1-mini improves from 2.41% to
metic for Temporal (Figure 15). Table 5 reports oracle performance.                          97.99% and Gemini-3-Flash from 26.51% to 88.37%, showing that
Profile Understanding is excluded from this setting because per-                             strong models can reason correctly once attribution and retrieval
sona traits are implicit and distributed, leaving no discrete evidence                       are removed as bottlenecks. In contrast, LLaMA-4 reaches only
spans that could serve as oracle input. Oracle performance thus                              37.35% even under oracle conditions, frequently refusing to answer
defines an upper bound for any retrieval-only improvement, as                                when evidence appears fragmented—highlighting a distinct failure
it reflects model behavior when all relevant evidence is perfectly                           mode rooted in conservative reasoning rather than retrieval.
surfaced.                                                                                       The difficulty compounds as information spans more groups.
                                                                                             Figure 4 shows that accuracy drops from 54.5% (single-group) to
   Evaluation Metrics. For Fine-Grained Recall, answers are concrete                         33.6% (two groups) and 19.7% (three groups), a 64% relative decline.
facts (names, numbers, timestamps) that may vary lexically while                             This degradation is consistent across models and memory configu-
remaining semantically correct; we use LLM-as-a-judge [43] to as-                            rations, demonstrating that cross-group attribution—not context
sess equivalence. For Memory Awareness and Profile Understanding,                            length—is the dominant challenge.
Conference acronym ’XX, June 03–05, 2018, Woodstock, NY                                                                                                                                     Hu et al.



               100
                                                               Overall                                                       4.4    Profile Understanding: Emergent Patterns
                                                                                                   All model/system runs
               80                                                                                  Overall Average                  Resist Retrieval

Accuracy (%)
                                                                                                   Full Context
               60       53.2
                                                                                                   w/ Memory System Avg      Profile Understanding tasks probe whether systems can maintain
               40                                               33.2

               20
                                                                                                              17.6           consistent user models over time. Results in Table 4 show that Style
                0
                                                                                                                             is the most challenging subtask, with memory systems achieving
                            1                                   2                                                 3
                                                  # Groups Involved per Question                                             only 11–58% and even Gemini-3-Flash reaching 67.05%. Unlike
                                                                                                                             factual recall, communication style is an emergent pattern spanning
                            GPT-4.1-mini                    Llama-4-Scout                       Gemini3-Flash
               100                                100                              100
                                                                                         86.3                                many interactions; it cannot be recovered from isolated snippets.
               80                                 80                               80




Accuracy (%)
                                                                                                                             In contrast, Skill and Role achieve higher accuracy because they are
               60                                 60 47.8                          60 65.4           54.0
                     44.8
               40                                 40 45.3       30.5               40
                                                                                                                      45.5
                                                                                                                             partially inferable from individual task contexts and organizational
                     42.5       28.0                                                                 40.0
               20               24.6
                                           18.2
                                                  20            25.9        11.4   20                                        structure. These results underscore a limitation of retrieval-centric
                                           18.2                                                                       18.2
                0
                   1         2         3
                                                   0
                                                      1         2         3
                                                                            9.1     0
                                                                                       1         2         3
                                                                                                                             memory: it excels at discrete facts but struggles with traits that are
               # Groups Involved per Question     # Groups Involved per Question   # Groups Involved per Question            never stated and can only be captured by aggregating behavioral
Figure 4: Accuracy by number of groups involved per ques-                                                                    signals across the full interaction history.
tion. Top: overall average across all settings. Bottom: break-
down by answer model.                                                                                                           Takeaway. Across all analyses, Figures 4 and Tables 4 and 5
                                                                                                                             jointly show that scaling context or retrieval alone is insufficient.
   Temporal reasoning remains unsolved. Temporal questions                                                                   Multi-party attribution, temporal revision, and inferential relevance
expose a complementary limitation. Across all systems, perfor-                                                               introduce structural challenges that current memory paradigms
mance is low (Gemini-3-Flash: 45.00%; GPT-4.1-mini: 7.00%; mem-                                                              do not address. EverMemBench surfaces these failures by design,
ory systems: 2.67–21.00%). In realistic collaboration, decisions are                                                         providing a diagnostic benchmark that shifts evaluation from
revised, superseded, and finalized over time, and answering cor-                                                             leaderboard comparisons to understanding why memory systems
rectly requires reasoning over version semantics, not just times-                                                            fail—and what next-generation architectures must change to suc-
tamps. This difficulty persists even with oracle evidence: the best                                                          ceed.
model reaches only 60% and LLaMA-4 only 34% (Table 5), because
the provided evidence necessarily contains overlapping lifecycle                                                             5     Conclusion
signals such as premature completion announcements and archival
                                                                                                                             In this paper, we introduced EverMemBench, a high-realism bench-
statements from other speakers on adjacent dates, which the model
                                                                                                                             mark for long-term conversational memory that reflects how LLMs
must still disambiguate before computing durations. These results
                                                                                                                             are used in practice: as participants in sustained, multi-party col-
indicate a reasoning gap that current memory architectures cannot
                                                                                                                             laboration where information is distributed across speakers and
bridge, as they treat time as an ordering signal rather than a seman-
                                                                                                                             groups, revised over time, and implicitly shaped by roles and social
tic construct that encodes event lifecycle stages such as initiation,
                                                                                                                             context. Through a carefully controlled curation pipeline grounded
revision, and completion.
                                                                                                                             in project timelines and public events, EverMemBench produces
                                                                                                                             traceable dialogue logs and evidence-grounded QA items that stress
                                                                                                                             memory challenges beyond context length, including attribution,
4.3                     Memory Awareness: Retrieval vs. Reasoning                                                            temporal revision, and inferential relevance. Our empirical results
Retrieval misses inferentially relevant evidence. Memory                                                                     show that many failures observed in deployed systems are struc-
Awareness tasks are explicitly designed to test whether systems                                                              tural rather than incidental: multi-hop reasoning collapses under
recognize when past information matters. Oracle results in Table 5                                                           multi-party attribution, temporal reasoning fails without explicit
show that all models achieve 87–99% accuracy, confirming that rea-                                                           version semantics, and similarity-based retrieval struggles to sur-
soning capability is sufficient when relevant evidence is available.                                                         face implicitly relevant information even when reasoning capacity
The difficulty lies in retrieving the right evidence.                                                                        is sufficient.
   Under full-context access, Gemini-3-Flash maintains near-oracle                                                               These findings suggest clear directions for future research. First,
performance (97–100%), while GPT-4.1-mini and LLaMA-4 degrade                                                                memory architectures must move beyond flat or snippet-based stor-
substantially (25–63% and 43–68%). This gap reflects differences in                                                          age toward representations that explicitly encode versioned state,
long-context reasoning: weaker models struggle to locate relevant                                                            episodic boundaries, and cross-group dependencies. Second, effec-
signals amid dense, multi-party dialogue.                                                                                    tive memory systems will need to integrate retrieval and reasoning
   Memory augmentation partially compensates for weaker mod-                                                                 more tightly, enabling models to recognize inferential relevance
els by filtering noise: GPT-4.1-mini improves to 29–76%. However,                                                            rather than relying solely on surface similarity. By decomposing
the same retrieval pipelines degrade Gemini-3-Flash (down to 76–                                                             memory competence into fine-grained recall, memory awareness,
90%) by discarding contextual cues the model could otherwise ex-                                                             and profile understanding, EverMemBench provides a diagnostic
ploit. Even with identical retrieved evidence, performance diverges                                                          foundation for systematically studying these challenges. We view
sharply—Gemini reaches 76–90%, while GPT-4.1-mini and LLaMA-4                                                                EverMemBench as a cornerstone benchmark for the next generation
reach only 29–76% and 35–73%. This reveals a dual bottleneck: re-                                                            of LLMs, one that enables principled progress toward structured,
trieval fails to surface inferentially relevant information, and weaker                                                      time-aware memory and socially grounded reasoning in realistic
answer models struggle to reason over sparse, indirect cues.                                                                 collaborative settings.
Evaluating Long-Horizon Memory for Multi-Party Collaborative Dialogues                                            Conference acronym ’XX, June 03–05, 2018, Woodstock, NY


References                                                                               [22] Adyasha Maharana, Dong-Ho Lee, Sergey Tulyakov, Mohit Bansal, Francesco
 [1] Josh Achiam, Steven Adler, Sandhini Agarwal, Lama Ahmad, Ilge Akkaya, et al.             Barbieri, and Yuwei Fang. 2024. Evaluating Very Long-Term Conversational
     2024. GPT-4 Technical Report. arXiv preprint arXiv:2303.08774 (2024).                    Memory of LLM Agents. arXiv:2402.17753 [cs.CL] https://arxiv.org/abs/2402.
 [2] Sebastian Borgeaud, Arthur Mensch, Jordan Hoffmann, Trevor Cai, Eliza Ruther-            17753
     ford, Katie Millican, George van den Driessche, Jean-Baptiste Lespiau, Bogdan       [23] Memodb Team. 2025. MemoBase: User Profile-Based Long-Term Memory for AI
     Damoc, Aidan Clark, Diego de Las Casas, Aurelia Guy, et al. 2022. Improving              Chatbot Applications. https://github.com/memodb-io/memobase.
     language models by retrieving from trillions of tokens. arXiv:2112.04426 [cs.CL]    [24] Meta AI. 2025. The Llama 4 Herd: The Beginning of a New Era of Na-
     https://arxiv.org/abs/2112.04426                                                         tively Multimodal AI Innovation. https://ai.meta.com/blog/llama-4-multimodal-
 [3] Michelle Brachman, Amina El-Ashry, Casey Dugan, and Werner Geyer. 2025.                  intelligence/.
     Current and Future Use of Large Language Models for Knowledge Work.                 [25] Jiayan Nan, Wenquan Ma, Wenlong Wu, and Yize Chen. 2025.
     arXiv:2503.16774 [cs.HC] https://arxiv.org/abs/2503.16774                                Nemori: Self-Organizing Agent Memory Inspired by Cognitive Science.
 [4] Jun Chen, Dannong Xu, Junjie Fei, Chun-Mei Feng, and Mohamed Elhoseiny.                  arXiv:2508.03341 [cs.AI] https://arxiv.org/abs/2508.03341
     2024. Document Haystacks: Vision-Language Reasoning Over Piles of 1000+             [26] Elliot Nelson, Georgios Kollias, Payel Das, Subhajit Chaudhury, and Soham
     Documents. arXiv:2411.16740 [cs.CV] https://arxiv.org/abs/2411.16740                     Dan. 2024. Needle in the Haystack for Memory Based Large Language Models.
 [5] Prateek Chhikara, Dev Khant, Saket Aryan, Taranjeet Singh, and Deshraj Yadav.            arXiv:2407.01437 [cs.CL] https://arxiv.org/abs/2407.01437
     2025. Mem0: Building Production-Ready AI Agents with Scalable Long-Term             [27] Preston Rasmussen, Pavlo Paliychuk, Travis Beauvais, Jack Ryan, and Daniel
     Memory. arXiv:2504.19413 [cs.CL] https://arxiv.org/abs/2504.19413                        Chalef. 2025. Zep: A Temporal Knowledge Graph Architecture for Agent Memory.
 [6] Gheorghe Comanici, Eric Bieber, Mike Schaekermann, Ice Pasupat, Noveen                   arXiv:2501.13956 [cs.AI] https://arxiv.org/abs/2501.13956
     Sachdeva, Inderjit Dhillon, et al. 2025. Gemini 2.5: Pushing the Frontier with      [28] Rana Salama, Jason Cai, Michelle Yuan, Anna Currey, Monica Sunkara, Yi Zhang,
     Advanced Reasoning, Multimodality, Long Context, and Next Generation Agentic             and Yassine Benajiba. 2025. MemInsight: Autonomous Memory Augmentation
     Capabilities. arXiv:2507.06261 [cs.CL] https://arxiv.org/abs/2507.06261                  for LLM Agents. arXiv:2503.21760 [cs.CL] https://arxiv.org/abs/2503.21760
 [7] Ananya Ganesh, Martha Palmer, and Katharina von der Wense. 2023. A survey           [29] Chris Samarinas and Hamed Zamani. 2024. ProCIS: A benchmark for proactive
     of challenges and methods in the computational modeling of multi-party dialog.           retrieval in conversations. In Proceedings of the 47th International ACM SIGIR
     In Proceedings of the 5th Workshop on NLP for Conversational AI (NLP4ConvAI              Conference on Research and Development in Information Retrieval. 830–840.
     2023). 140–154.                                                                     [30] Sagar Sapkota, Mohammad Saqib Hasan, Mubarak Shah, and Santu Karmaker.
 [8] Google. 2025. Introducing Gemini 3 Flash: Benchmarks, Global Availability.               2025. Multi-Party Conversational Agents: A Survey. arXiv:2505.18845 [cs.CL]
     https://blog.google/products/gemini/gemini-3-flash/.                                     https://arxiv.org/abs/2505.18845
 [9] Jia-Chen Gu, Chongyang Tao, and Zhen-Hua Ling. 2022. Who Says What to               [31] Haoran Tan, Zeyu Zhang, Chen Ma, Xu Chen, Quanyu Dai, and Zhenhua Dong.
     Whom: A Survey of Multi-Party Conversations.. In IJCAI. 5486–5493.                       2025. MemBench: Towards More Comprehensive Evaluation on the Memory of
[10] Kelvin Guu, Kenton Lee, Zora Tung, Panupong Pasupat, and Ming-Wei                        LLM-based Agents. arXiv:2506.21605 [cs.CL] https://arxiv.org/abs/2506.21605
     Chang. 2020. REALM: Retrieval-Augmented Language Model Pre-Training.                [32] Mohammad Tavakoli, Alireza Salemi, Carrie Ye, Mohamed Abdalla, Hamed
     arXiv:2002.08909 [cs.CL] https://arxiv.org/abs/2002.08909                                Zamani, and J Ross Mitchell. 2025. Beyond a Million Tokens: Benchmark-
[11] Junqing He, Liang Zhu, Rui Wang, Xi Wang, Reza Haffari, and Jiaxing Zhang.               ing and Enhancing Long-Term Memory in LLMs. arXiv:2510.27246 [cs.CL]
     2024. MADial-Bench: Towards Real-world Evaluation of Memory-Augmented                    https://arxiv.org/abs/2510.27246
     Dialogue Generation. arXiv:2409.15240 [cs.CL] https://arxiv.org/abs/2409.15240      [33] Qingyue Wang, Yanhe Fu, Yanan Cao, Shuai Wang, Zhiliang Tian, and Liang
[12] Zhongtian Hu, Qi He, Ronghan Li, Meng Zhao, and Lifang Wang. 2025. Advanc-               Ding. 2025. Recursively summarizing enables long-term dialogue memory in
     ing Multi-Party Dialogue Framework with Speaker-ware Contrastive Learning.               large language models. Neurocomputing 639 (2025), 130193.
     arXiv:2501.11292 [cs.CL] https://arxiv.org/abs/2501.11292                           [34] Bowen Wu, Wenqing Wang, Lihaoran Lihaoran, Yunhan Deng, Ying Li, Jingsong
[13] Zhaopei Huang, Qifeng Dai, Guozheng Wu, Xiaopeng Wu, Kehan Chen, Chuan                   Yu, and Baoxun Wang. 2025. Interpersonal memory matters: A new task for
     Yu, Xubin Li, Tiezheng Ge, Wenxuan Wang, and Qin Jin. 2025. Mem-PAL: Towards             proactive dialogue utilizing conversational history. In Proceedings of the 29th
     Memory-based Personalized Dialogue Assistants for Long-term User-Agent In-               Conference on Computational Natural Language Learning. 47–67.
     teraction. arXiv:2511.13410 [cs.CL] https://arxiv.org/abs/2511.13410                [35] Di Wu, Hongwei Wang, Wenhao Yu, Yuwei Zhang, Kai-Wei Chang, and Dong Yu.
[14] Bowen Jiang, Zhuoqun Hao, Young-Min Cho, Bryan Li, Yuan Yuan, Sihao Chen,                2025. LongMemEval: Benchmarking Chat Assistants on Long-Term Interactive
     Lyle Ungar, Camillo J. Taylor, and Dan Roth. 2025. Know Me, Respond to Me:               Memory. arXiv:2410.10813 [cs.CL] https://arxiv.org/abs/2410.10813
     Benchmarking LLMs for Dynamic User Profiling and Personalized Responses at          [36] Wujiang Xu, Zujie Liang, Kai Mei, Hang Gao, Juntao Tan, and Yongfeng Zhang.
     Scale. arXiv:2504.14225 [cs.CL] https://arxiv.org/abs/2504.14225                         2025. A-MEM: Agentic Memory for LLM Agents. arXiv:2502.12110 [cs.CL]
[15] Bowen Jiang, Yuan Yuan, Maohao Shen, Zhuoqun Hao, Zhangchen Xu, Zichen                   https://arxiv.org/abs/2502.12110
     Chen, Ziyi Liu, Anvesh Rao Vijjini, Jiashu He, Hanchao Yu, Radha Poovendran,        [37] Zhongyu Yang, Jun Chen, Dannong Xu, Junjie Fei, Xiaoqian Shen, Liangbing
     Gregory Wornell, Lyle Ungar, Dan Roth, Sihao Chen, and Camillo Jose Taylor.              Zhao, Chun-Mei Feng, and Mohamed Elhoseiny. 2025. WikiAutoGen: Towards
     2025. PersonaMem-v2: Towards Personalized Intelligence via Learning Implicit             Multi-Modal Wikipedia-Style Article Generation. arXiv:2503.19065 [cs.CV] https:
     User Personas and Agentic Memory. arXiv:2512.06688 [cs.CL] https://arxiv.org/            //arxiv.org/abs/2503.19065
     abs/2512.06688                                                                      [38] Zhongyu Yang, Yingfang Yuan, Xuanming Jiang, Baoyi An, and Wei Pang. 2025.
[16] Gregory Kamradt. 2023. Needle in a Haystack — Pressure Testing LLMs. https:              InEx: Hallucination Mitigation via Introspection and Cross-Modal Multi-Agent
     //github.com/gkamradt/LLMTest_NeedleInAHaystack.                                         Collaboration. arXiv:2512.02981 [cs.CV] https://arxiv.org/abs/2512.02981
[17] Jiazheng Kang, Mingming Ji, Zhe Zhao, and Ting Bai. 2025. Memory OS of AI           [39] Zihao Yi, Jiarui Ouyang, Zhe Xu, Yuwen Liu, Tianhao Liao, Haohao Luo, and
     Agent. arXiv:2506.06326 [cs.AI] https://arxiv.org/abs/2506.06326                         Ying Shen. 2025. A survey on recent advances in llm-based multi-turn dialogue
[18] Mosh Levy, Alon Jacoby, and Yoav Goldberg. 2024. Same Task, More Tokens: the             systems. Comput. Surveys 58, 6 (2025), 1–38.
     Impact of Input Length on the Reasoning Performance of Large Language Models.       [40] Saizheng Zhang, Emily Dinan, Jack Urbanek, Arthur Szlam, Douwe Kiela, and
     In Proceedings of the 62nd Annual Meeting of the Association for Computational           Jason Weston. 2018. Personalizing Dialogue Agents: I have a dog, do you have pets
     Linguistics (Volume 1: Long Papers), Lun-Wei Ku, Andre Martins, and Vivek                too?. In Proceedings of the 56th Annual Meeting of the Association for Computational
     Srikumar (Eds.). Association for Computational Linguistics, Bangkok, Thailand,           Linguistics (Volume 1: Long Papers), Iryna Gurevych and Yusuke Miyao (Eds.).
     15339–15353. doi:10.18653/v1/2024.acl-long.818                                           Association for Computational Linguistics, Melbourne, Australia, 2204–2213.
[19] Patrick Lewis, Ethan Perez, Aleksandra Piktus, Fabio Petroni, Vladimir Karpukhin,        doi:10.18653/v1/P18-1205
     Naman Goyal, Heinrich Küttler, Mike Lewis, Wen tau Yih, Tim Rocktäschel,            [41] Siyan Zhao, Mingyi Hong, Yang Liu, Devamanyu Hazarika, and Kaixiang Lin.
     Sebastian Riedel, and Douwe Kiela. 2021. Retrieval-Augmented Generation for              [n. d.]. Do LLMs Recognize Your Preferences? Evaluating Personalized Prefer-
     Knowledge-Intensive NLP Tasks. arXiv:2005.11401 [cs.CL] https://arxiv.org/abs/           ence Following in LLMs. In The Thirteenth International Conference on Learning
     2005.11401                                                                               Representations.
[20] Zhiyu Li, Shichao Song, Hanyu Wang, Simin Niu, Ding Chen, Jiawei Yang,              [42] Zheng Zhao, Clara Vania, Subhradeep Kayal, Naila Khan, Shay B Cohen, and
     Chenyang Xi, Huayi Lai, Jihao Zhao, Yezhaohui Wang, Junpeng Ren, Zehao                   Emine Yilmaz. 2025. PersonaLens: A Benchmark for Personalization Evaluation
     Lin, Jiahao Huo, Tianyi Chen, Kai Chen, Kehang Li, Zhiqiang Yin, Qingchen Yu,            in Conversational AI Assistants. In Findings of the Association for Computational
     Bo Tang, Hongkang Yang, Zhi-Qin John Xu, and Feiyu Xiong. 2025. MemOS: An                Linguistics: ACL 2025, Wanxiang Che, Joyce Nabende, Ekaterina Shutova, and
     Operating System for Memory-Augmented Generation (MAG) in Large Language                 Mohammad Taher Pilehvar (Eds.). Association for Computational Linguistics,
     Models. arXiv:2505.22101 [cs.CL] https://arxiv.org/abs/2505.22101                        Vienna, Austria, 18023–18055. doi:10.18653/v1/2025.findings-acl.927
[21] Nelson F. Liu, Kevin Lin, John Hewitt, Ashwin Paranjape, Michele Bevilacqua,        [43] Lianmin Zheng, Wei-Lin Chiang, Ying Sheng, Siyuan Zhuang, Zhanghao Wu,
     Fabio Petroni, and Percy Liang. 2024. Lost in the Middle: How Language Models            Yonghao Zhuang, Zi Lin, Zhuohan Li, Dacheng Li, Eric P. Xing, Hao Zhang,
     Use Long Contexts. Transactions of the Association for Computational Linguistics         Joseph E. Gonzalez, and Ion Stoica. 2023. Judging LLM-as-a-Judge with MT-Bench
     12 (2024), 157–173. doi:10.1162/tacl_a_00638                                             and Chatbot Arena. arXiv:2306.05685 [cs.CL] https://arxiv.org/abs/2306.05685
Conference acronym ’XX, June 03–05, 2018, Woodstock, NY                                                                                 Hu et al.


A Data Statistics                                                         Topic                Participants   Messages     Sub-tasks      QA
A.1 Profile Distribution                                                  Technology                     39       10,222          436      488
                                                                          Operations                     36       10,106          408      471
Our benchmark comprises 170 unique employee profiles spanning
                                                                          Marketing                      45       10,638          429      467
a simulated enterprise organization. Each profile is characterized        Financial Services             32       10,003          423      481
by demographic attributes, a skill portfolio, an 8-dimensional com-       Governance                     46       10,054          424      493
munication style, and a Big-Five personality trait vector.
                                                                          Total                         170       51,023        2,120   2,400
   Demographics. Figure 5 summarizes the demographic composi-            Table 6: Dialogue statistics across five project topics. Sub-
tion. Ages range from 23 to 48 (mean 30.8), with the majority (54.1%)    tasks denote the number of distinct work tasks respectively.
in the 27–34 bracket. The gender split is 61.2% male and 38.8% fe-
male. Education levels include Bachelor’s (52.9%), Master’s (35.3%),
and PhD (11.8%). The organizational hierarchy follows a five-level           Overall Analysis. These distributions are intentionally skewed
rank system: L1 (CEO, 0.6%), L2 (Directors, 2.9%), L3 (Senior Staff,     to mirror realistic enterprise communication norms—semi-formal
20.6%), L4 (Mid-level, 44.1%), and L5 (Junior, 31.8%), reflecting a      tone and friendly warmth predominate in professional group chats,
realistic corporate pyramid.                                             while the rank pyramid (75.9% at L4–L5) reflects typical corporate hi-
                                                                         erarchies. Although certain individual dimensions are concentrated
   Skill Profile. Each employee is assigned skills drawn from a pool
                                                                         (e.g., Semi-formal 78.2%, Friendly 81.8%), the impact on benchmark
of 104 unique competencies, with an average of 4.1 skills per mem-
                                                                         validity is limited: each persona is characterized by a combination of
ber (range: 3–7). Skill assignments are rank-dependent:
                                                                         all eight style dimensions, so even personas sharing the same value
     • Rank 1–2 (Executives): 6–10 skills, including strategic man-      on one axis differ substantially along others—the combinatorial
       agement and cross-functional competencies.                        space ensures diverse and distinguishable style fingerprints across
     • Rank 3 (Senior Staff): 4–6 skills, combining domain exper-        the 170 employees. Moreover, as shown in Figure 6, Management
       tise with team coordination.                                      and Staff profiles diverge clearly on Formality, Warmth, and Ques-
     • Rank 4–5 (Staff): 3–5 skills, focused on role-specific tech-      tioning, confirming meaningful inter-role variation. Finally, Style
       nical or business competencies.                                   accounts for only 7.3% of all QA items (176/2,400), and our 2×2
Each skill is annotated with a proficiency level: strong (27.2%),        fact-vs-style adversarial distractor design prevents systems from
medium (47.9%), or low (24.9%). As shown in Figure 7, the most           exploiting distributional priors.
prevalent expert-level skills are Python and Java (each 13.9%), fol-
lowed by Linux and Data Analysis (each 6.4%). Skills with less than      A.2      Dialogue Distribution
1% share are grouped into “Others.”                                      The dialogue corpus spans 5 topics, each simulating approximately
  Communication Style. Each persona is assigned an 8-dimensional         one year (Jan–Dec 2025) of enterprise group-chat communication.
communication profile (Figure 6, left):                                  As summarized in Table 6, the dataset contains 51,023 messages
                                                                         comprising over 2.1 million words, with a consistent average
     • Formality: Semi-formal (78.2%) / Casual (21.8%)                   message length of 41.5 words across all topics.
     • Verbosity: Moderate (38.8%) / Concise (34.7%) / Detailed
       (26.5%)                                                              Multi-Theme Structure. Each topic is organized into 3 concur-
     • Humor: Minimal (50.0%) / Occasional (34.7%) / Frequent            rent project groups, with 32–46 participants communicating over
       (15.3%)                                                           250–255 workdays. Conversations revolve around a rich set of
     • Jargon Usage: Technical (50.6%) / Balanced (30.6%) / Plain        834–966 distinct themes per topic (4,556 in total), composed of
       (18.2%)                                                           two sources: (1) work tasks (408–436 per topic), representing ongo-
     • Emoji Usage: Rare (54.7%) / Occasional (28.2%) / Frequent         ing project activities such as feature development, code reviews,
       (17.1%)                                                           and design discussions; and (2) injected news events (405–543 per
     • Directness: Balanced (57.6%) / Direct (41.2%) / Indirect (1.2%)   topic), simulating real-world information that employees discuss
     • Warmth: Friendly (81.8%) / Neutral (11.8%) / Warm (6.5%)          organically—covering industry trends, policy updates, and current
     • Questioning Style: Probing (47.6%) / Clarifying (44.7%) /         affairs. This dual-source design ensures that the dialogue corpus cap-
       Accepting (7.6%)                                                  tures both structured work-related memory and loosely-structured
Assignments are conditioned on role expectations: executives tend        world-knowledge discussions, posing a realistic challenge for mem-
toward formal, direct, and neutral styles, while technical staff favor   ory systems that must distinguish and retrieve from heterogeneous
concise, technical, and minimal-humor communication.                     conversational threads.

   Personality Traits. Big-Five personality traits are assigned at          QA Benchmark. Each topic is accompanied by a curated set of
three levels (High/Medium/Low), as visualized in Figure 6 (right).       question–answer pairs, totaling 2,400 across all five topics after fil-
Openness skews high (44.7% High, 54.1% Medium), Extraver-                tering. QA pairs are organized into three evaluation dimensions
sion skews low (51.8% Low), and Agreeableness is predominantly           encompassing nine sub-tasks:
medium (77.6%). Management-level employees (L1–L2) exhibit                   • Fine-grained Recall (762 pairs, 31.8%): Single-hop Retrieval
markedly higher Openness and Extraversion compared to staff                    (213), Multi-hop Trajectory (249), and Temporal Duration
(L3–L5), consistent with leadership role expectations.                         (300).
Evaluating Long-Horizon Memory for Multi-Party Collaborative Dialogues                                                                                               Conference acronym ’XX, June 03–05, 2018, Woodstock, NY


                                         Age                                                        Gender                                     Education                                             Rank



                                         n=170                                                        n=170                                       n=170                                              n=170




                                18-26 21.2%      27-34 54.1%                                  Male 61.2%          Female 38.8%           Bachelor 52.9%     Master 35.3%                       L1 0.6%       L2 2.9%
                                35-44 23.5%      45+ 1.2%                                                                                PhD 11.8%                                             L3 20.6%      L4 44.1%
                                                                                                                                                                                               L5 31.8%

Figure 5: Demographic distributions of the 170 simulated user profiles across four dimensions: age, gender, education level, and
organizational rank.

                                                   Communication Style by Rank                                                                              Big-Five Personality by Rank
                                                                        Formality                                                                                                  Open.


                                   Verbosity                                                               Questioning
                                                                0.75                                                                                                 0.75


                                                                       0.50                                                                                                 0.50
                                                                                                                                     Consc.                                                                        Neuro.
                                                                              0.25                                                                                                 0.25


                      Humor                                                                                                 Warmth




                                     Jargon                                                                 Directness
                                                                                                                                                   Extra.                                           Agree.

                                                                              Emoji
                                                       Management (L1 L2)                     Staff (L3 L5)                                                  Management (L1 L2)            Staff (L3 L5)

Figure 6: Radar charts comparing communication style (left) and Big-Five personality traits (right) between management
(L1–L2) and staff (L3–L5) groups.

                                                           Expert Skills
                                              Others
                                                                                                                                     Each QA pair includes an average of 6.7 evidence references point-
                                                                                      Python
                                                                                                                                     ing to specific messages in the dialogue history, enabling fine-
                  Process Optimization                                                                                               grained evaluation of both retrieval precision and comprehension-
                  Content Marketing
           Financial Ratio Analysis                                                                                                  synthesis capability. Fine-grained Recall questions adopt an open-
                          React
                                                                                                           Java
                                                                                                                                     ended format because each question targets a well-defined entity (a
                  Copywriting
                                                                                                                                     specific link, date, or person), making the gold answer unambigu-
        Requirements Analysis
                                                                                                                                     ous and straightforward to verify. Memory Awareness and Profile
                     Selenium                                                                                                        Understanding questions, by contrast, assess generalization and
            Project Management                                                                         Linux                         contextual understanding of stored memories—capabilities whose
                       Prototyping                                                                                                   correct answers are more nuanced and harder to judge automati-
                                     JUnit                                                      Data Analysis                        cally. To minimize variance introduced by LLM-as-a-Judge scoring,
                                       User Interview                                 Figma                                          we adopt a multiple-choice format (A/B/C/D) for these two dimen-
                                         Requirement Analysis     JavaScript
                                                                                                                                     sions, where both questions and distractors are carefully crafted to
Figure 7: Distribution of expert skills among simulated user                                                                         prevent information leakage from the question stem and to ensure
profiles. The top-18 skills are shown individually; skills rep-                                                                      that every wrong option remains plausible rather than serving as a
resenting less than 1% of the total are grouped into “Others.”                                                                       strawman (see §B.3 for distractor design details).
     • Memory Awareness (1,097 pairs, 45.7%): Constraint (402),
       Proactivity (427), and Update (268).
     • Profile Understanding (541 pairs, 22.5%): Style (176), Skill
       (169), and Role (196).
Conference acronym ’XX, June 03–05, 2018, Woodstock, NY                                                                                    Hu et al.


B Data Construction Details                                              concrete units such as “survey target user personas,” “collect com-
                                                                         petitor feature lists,” and “interview internal business departments.”
B.1 Blueprint Generation
                                                                         Likewise, “design the database” becomes per-table schema design,
The blueprint pipeline proceeds through six stages, each followed        indexing strategy, and documentation. We supply extensive positive
by automated validation. Below we detail each stage.                     and negative examples to calibrate the LLM’s decomposition depth.
    Stage 1: Project Topic Generation. We begin by generating five       Each resulting subtask specifies a concrete deliverable, one to three
project topics spanning diverse enterprise domains—Technology,           required skills drawn from the skill universe, a development phase,
Operations, Marketing, Financial Services, and Governance—each           and a dependency type. Tasks are topologically sorted so that archi-
characterized by a sector-specific context, three to five core chal-     tectural decisions precede implementation, API contracts precede
lenges, and a set of expected stakeholder roles. Gemini-2.5-Pro first    integration, and testing follows feature completion. Deadlines are
produces a broad pool of candidates; to steer diversity, we pro-         spread across the full calendar year, with early phases concentrated
vide contrasting examples: desirable topics cross sector boundaries      in Q1–Q2 and later phases in Q3–Q4.
(smart manufacturing, cross-border e-commerce, telemedicine),               Stage 6: Subtask-to-Member Assignment. Each subtask is assigned
while near-duplicate clusters (e.g., “intelligent customer service       to exactly one team member. Given the ordered subtask list and
/ intelligent recommendation / intelligent analytics”) are explicitly    each member’s skill profile, the LLM matches tasks to people by
excluded. Human annotators then screen, merge, and refine the can-       considering proficiency alignment (strong > medium > low), work-
didates, adjusting scope and resolving overlaps until each surviving     load balance, and role appropriateness (Executive handles strategy;
topic can sustain a year-long simulated development cycle.               Managers oversee architecture and coordination; Staff execute im-
   Stage 2: Sub-Project Decomposition. Each topic is decomposed          plementation and testing). Every assignment comes with a short
into three sub-projects, yielding 5×3 = 15 distinct units. A Financial   natural-language rationale that serves as an audit trail. The val-
Services project, for example, might split into a Risk Assessment        idator ensures that every member receives at least five subtasks—
Engine, a Transaction Processing System, and a Compliance Report-        guaranteeing meaningful dialogue participation—that no subtask is
ing Platform. The key constraint is mutual exclusivity: sub-projects     left unassigned, and that temporal feasibility constraints are met.
must be independently executable, so we forbid parent–child over-           Cross-Group Dependency Injection. After individual blueprints
laps (e.g., “develop the manufacturing execution system” alongside       are complete, we inject cross-project dependencies to create the
“develop its production scheduling module”). A post-generation           multi-group structure central to EverMemBench. Within each
validator verifies that no sub-project subsumes another. This struc-     project the three sub-projects already share personnel (especially
ture creates natural cross-group information flow—decisions in           Managers and the Executive) and technical decisions, producing
one sub-project (say, a risk scoring methodology) constrain design       natural coupling. We formalize three types of dependency: data
choices in another (transaction validation rules)—while keeping          contracts, where one sub-project defines a schema that another
each group chat channel self-contained with its own team roster          consumes and must therefore wait for; shared infrastructure, where
and task backlog.                                                        multiple sub-projects rely on a common component (e.g., an authen-
   Stage 3: Team Member Selection. For each sub-project we assem-        tication service) managed by one team; and policy decisions, where
ble a team from the shared pool of 170 employees across seven            a technical standard adopted in one sub-project constrains choices
departments (1 Executive, 5 Managers, 164 Staff). The LLM re-            elsewhere (e.g., the state management library or deployment plat-
ceives the complete employee registry—skill profiles s𝑒 with pro-        form). Each dependency is recorded as a tuple (𝑃𝑖 , 𝑃 𝑗 , type, artifact),
ficiency levels and 8-dimensional communication styles c𝑒 —and           enabling downstream dialogue generation to reference cross-group
selects members by balancing skill–task alignment, communica-            decisions and supporting questions that require multi-group evi-
tion complementarity, and hierarchical coverage. A validator then        dence chaining.
enforces that every team spans all three ranks and falls within             Blueprint Validation. Beyond the per-stage validators described
the configured size range. On average, each project involves 37.6        above, a final global check ensures end-to-end consistency before
participants.                                                            dialogue generation begins. We verify five invariants: (1) complete-
   Stage 4: Communication Style Adaptation. Because communica-           ness—every subtask has an assigned owner, a deadline, and required
tion behavior shifts with team context, we adjust each member’s          skills; (2) temporal consistency—no task depends on one scheduled
style profile after assembly. Given the team’s rank distribution and     later; (3) skill coverage—every required skill appears in at least one
size, the LLM shifts individual dimensions by up to two levels and       team member’s profile at medium proficiency or above; (4) load
records the rationale; original profiles are preserved.                  balance—no employee carries an unreasonable number of concur-
                                                                         rent tasks in any 30-day window; and (5) role coherence—strategic
  Stage 5: Subtask Generation and Sequencing. For each sub-project       tasks are assigned to Executives or Managers, not junior staff. Any
we generate a set of subtasks T𝑝,𝑗 organized into six sequential         failure triggers targeted regeneration of the offending stage.
development phases: Strategy & Planning, Requirements & Design,             The resulting blueprints serve as the executable specification
System Architecture & Tech Selection, Development & Integration,         for dialogue generation: every conversation references specific
Testing & QA, and Deployment & Operations.                               subtasks, respects the defined dependencies, and exhibits role-
  The main challenge here is granularity. A coarse task like “con-       appropriate communication patterns grounded in the blueprint’s
duct requirements research” is insufficient; it must be broken into      organizational structure.
Evaluating Long-Horizon Memory for Multi-Party Collaborative Dialogues                             Conference acronym ’XX, June 03–05, 2018, Woodstock, NY


B.2     Conversation Generation                                                   Hierarchical Summarization. Generating coherent dialogue over
Conversation generation transforms the static blueprints into dy-             a full calendar year under LLM context limits requires compressing
namic, day-by-day multi-party dialogues spanning a full simulated             history without losing the structural cues that support temporal
year (𝐷 = 365 days). As introduced in the main text, each sub-                reasoning. As formalized in the main text, we employ three com-
project maintains its own group chat channel, and each day’s di-              plementary summarization layers.
                                                                                                               (𝑑 )
alogue is generated in a single forward pass conditioned on hier-                 The weekly summary 𝑊𝑝,𝑗             is generated at the end of each
archical summaries and persona profiles. Dialogues are generated              week from the preceding days’ dialogues. It organizes progress
only on workdays; weekends contain no conversations, mirroring                by task, recording dated milestones in chronological order and not-
the schedule of a real enterprise. This appendix expands on the task          ing planned next steps. This provides the dialogue generator with
scheduling pipeline that bridges blueprints to daily generation, the          fine-grained recent context (what was decided earlier in the week,
three-layer summarization mechanism, and the multi-level quality              what remains blocked, what is expected next), enabling natural
assurance system.                                                             continuity across week boundaries.
                                                                                                              (𝑑 )
                                                                                  The monthly summary 𝑀𝑝,𝑗          is generated on the last workday of
   Task Schedule Preparation. Before dialogue generation begins,              each month from all dialogues and task records within that period.
the blueprint’s subtask assignments must be converted into a con-             It groups information by project, listing completed tasks with their
crete daily schedule that determines which tasks are active on each           completion dates, in-progress items with current status, key mile-
simulated day. This proceeds in three steps. First, we extract all            stones, and accumulated factual details such as budgets, team sizes,
subtasks from the completed blueprints, adjust deadlines that fall            and technical decisions. Where the weekly summary captures oper-
on weekends to the nearest following workday, and deduplicate                 ational momentum, the monthly summary provides the long-range
tasks that appear in overlapping sub-project assignments. Second,             backdrop that prevents the dialogue from contradicting decisions
Gemini-2.5-Pro [6] estimates the working-day duration of each task,           made weeks earlier.
taking into account its complexity, phase, and inter-task dependen-                                            (𝑑 )
                                                                                  The leader instruction log 𝐿𝑝,𝑗    extracts and retains directives from
cies. Third, a backward-scheduling algorithm computes each task’s             senior personnel (Executive and Managers) over a rolling 30-day
start date by subtracting the estimated duration from its deadline,           window. Each instruction is categorized as a strategic decision, an
automatically resolving conflicts when a predecessor’s deadline               operational directive, or a methodological guidance, and is linked
falls after a dependent task’s computed start date. The resulting             to the affected tasks. This mechanism ensures that downstream
schedule classifies every task on each workday into one of three              conversations comply with, not merely mention, the decisions of
categories: starting (first day of work), ongoing (in progress but not        leadership, creating the policy-adherence patterns targeted by our
yet due), and ending (deadline reached). This three-way partition             Memory Awareness evaluation dimension.
drives the dialogue generator’s expectations about what each day’s
conversation should contain (new task kickoffs, progress updates,
or completion announcements), and is enforced by downstream
validation.                                                                      Multi-Level Quality Assurance. Each day’s generated dialogue
                                                                              passes through four sequential validation levels before being ac-
   Daily Dialogue Synthesis. For each workday 𝑑, the dialogue gen-            cepted, extending the produce–verify philosophy introduced in the
erator receives five categories of input: (i) the day’s task schedule         blueprint pipeline to the more complex domain of natural-language
with its starting/ongoing/ending classification and the identities of         dialogue.
each task’s assignees, (ii) the most recent weekly summary 𝑊𝑝,𝑗   (𝑑 )
                                                                       ,         Level 1 applies deterministic programmatic rules: timestamps
                                   (𝑑 )                                       must fall within work hours, speakers must be authorized mem-
(iii) the current monthly summary 𝑀𝑝,𝑗  , (iv) outstanding leader             bers of the group they appear in, group names must match the
                  (𝑑 )
instructions 𝐿𝑝,𝑗      from the past 30 days, and (v) the full persona pro-   project structure exactly, and raw task identifiers must not leak into
files {𝜋𝑒 }𝑒 ∈ E𝑝,𝑗 of all group members, including their team-adapted        dialogue text (task references are maintained through structured
communication styles from Stage 4 of the blueprint pipeline.                  metadata bindings). These checks are instantaneous and catch me-
    The generator produces a structured multi-party dialogue where            chanical formatting errors before more expensive semantic analysis
each utterance is attributed to a specific speaker, timestamped               begins.
within work hours (09:00–18:00), and bound to the task identifiers               Level 2 uses an LLM to verify task-completion semantics against
it discusses. Two constraints are particularly important. First, every        the day’s schedule. Starting tasks must show evidence of initiation;
task assignee must participate in the discussion of their assigned            ending tasks must show evidence of completion; and critically,
tasks, since a passive team member who never speaks about their               no task may exhibit premature completion. The checker draws a
own work would be unrealistic and would deprive downstream QA                 semantic distinction between forward-looking statements (“I will
generation of evidence material. Second, strict deadline discipline           finish this today,” “submitting version 1.0 for review”) and genuine
is enforced: only tasks whose deadline falls on the current day               closure markers (“this task is now complete, deliverables archived”),
may be marked as completed, while ongoing tasks may report                    since conflating the two would undermine the temporal integrity
progress but not closure. This constraint is essential for creating           of the data.
the temporal revision patterns that our evaluation probes; without               Level 3 evaluates logical coherence: an LLM examines the conver-
it, premature completion declarations would collapse the version-             sation for internal self-contradictions, inconsistencies with informa-
tracking complexity needed for temporal reasoning questions.                  tion established in weekly and monthly summaries, and violations
Conference acronym ’XX, June 03–05, 2018, Woodstock, NY                                                                                Hu et al.


of recorded leader directives. This check operates with a deliber-      require computing time spans, either the working-day length of a
ately lenient threshold, flagging only substantive errors that would    single task or the gap between two events (e.g., from one task’s com-
make QA items unanswerable or ambiguous.                                pletion to the next task’s initiation by the same person). Existence
   Level 4 verifies communication quality against persona profiles:     checks include both positive cases (verifying that a stated event did
appropriate forms of address (subordinates using formal titles for      occur) and negative cases designed to test hallucination resistance,
superiors), absence of self-referencing errors (speakers unnaturally    where we construct near-miss scenarios referencing plausible but
mentioning their own names), alignment with each speaker’s 8-           non-existent events. Multi-hop retrieval requires chaining evidence
dimensional communication style, and role-appropriate expertise         across speakers or groups: identifying a person through a com-
in technical discussions.                                               positional constraint (e.g., “the colleague responsible for writing
                                                                        the Swagger documentation for authentication”), then tracing that
   Bounded Regeneration. When validation fails at any level, the
                                                                        person’s timeline to a subsequent event. When the base narrative
system attempts targeted repair rather than regenerating the en-
                                                                        lacks the specific evidence structure needed for a multi-hop chain,
tire day’s dialogue from scratch. A dedicated fix agent receives the
                                                                        we employ controlled implantation via field-bridge decoupling: a
flagged dialogue along with a structured conflict report detailing
                                                                        target reasoning chain 𝑅𝑜 is decomposed into a bridge segment
each violation by category and severity. The agent applies mini-
                                                                        𝑅2 that maps a scenario to an intermediate identifier and a dictio-
mal, conservative edits, preferring deletion over modification to
                                                                        nary segment 𝑅3 that resolves the identifier to a concrete solution.
avoid introducing new errors, such as removing utterances from
                                                                        These segments are embedded into the dialogue history as plausible
unauthorized speakers, adjusting out-of-range timestamps, con-
                                                                        meeting notes or data-dictionary entries authored by real project
verting premature completion claims into progress statements, and
                                                                        members; seeing 𝑅3 alone reveals no connection to the original
correcting task-identifier bindings. The repaired dialogue is then
                                                                        scenario, so the solver must retrieve 𝑅2 to complete the chain. To
re-checked through the full four-level pipeline. If validation still
                                                                        create a realistic difficulty gradient, we additionally extract a decoy
fails after two repair attempts, the date is flagged for manual re-
                                                                        rule 𝑅1 from existing dialogue, representing a general default pro-
view. All repairs are logged with before-and-after diffs to maintain
                                                                        cedure that the question naturally evokes. The question references
a complete audit trail and support post-hoc analysis of common
                                                                        𝑅1 ’s context but includes a subtle special condition that triggers the
generation failure modes.
                                                                        override path through 𝑅2 and 𝑅3 , forcing the system to recognize
   Cross-Group Coherence. Within each project, the three sub-           that the general rule does not apply and to follow the multi-hop
project group chats share personnel, particularly Managers and          chain instead.
the Executive, who participate in multiple channels simultaneously.         For all sub-branches, we apply structure mining: an LLM agent
The generation pipeline maintains coherence across groups by en-        traverses the blueprint and dialogue structure to identify naturally
suring that shared members cannot be speaking in two groups at          occurring retrieval targets, such as task completion markers, cross-
the exact same timestamp, and that technical decisions referenced       group decision references, and personnel role bindings. To ensure
across groups remain consistent. When the dialogue generator            diversity, we use embedding-based similarity filtering to prevent
encounters a task that depends on a cross-group artifact (a data        semantically redundant questions from clustering around the same
contract, shared infrastructure component, or policy decision in-       dialogue segments.
jected during the blueprint phase), it conditions the conversation
on the relevant cross-group context so that references to external         Memory Awareness. This dimension tests whether the system
decisions are accurate and temporally appropriate. This mechanism       can mobilize past information to solve new problems, not merely
is what makes multi-hop, cross-group QA items possible: the evi-        recall it. Generation follows a five-step pipeline for each QA item.
dence trail genuinely spans multiple group chats rather than being      In the first step, the generator selects one to four dialogue snippets
artificially duplicated.                                                as evidence, focusing on segments that contain logical anchors: con-
                                                                        straint definitions, contradiction points, or high-stakes directives.
B.3     Q&A Generation                                                  In the second step, a verification agent checks factual accuracy,
                                                                        logical soundness, and evidence completeness. In the third step,
We synthesize 2,400 QAE triples (𝑞, 𝑎, 𝑒) through three specialized
                                                                        the generator produces the question, the correct answer, and three
pipelines, one per evaluation dimension. All three pipelines share
                                                                        distractors. In the fourth step, a chain-of-thought auditor checks
a common principle we call the missing-key rule: each question
                                                                        whether the question is answerable without evidence (which would
provides a scenario (the “lock”) whose resolution depends on spe-
                                                                        indicate information leakage), whether all options appear equally
cific evidence buried in the dialogue history (the “key”), and the
                                                                        authoritative, and whether length imbalance reveals the correct
question itself must never leak the key. This principle guides both
                                                                        answer. In the fifth step, difficulty is upgraded through adversar-
question design and distractor construction across all dimensions.
                                                                        ial perturbations: keyword substitution replaces explicit technical
Below we detail the generation strategy for each dimension.
                                                                        terms with functional descriptions to force semantic rather than
   Fine-grained Recall. This dimension evaluates precise retrieval of   lexical retrieval; parameter removal strips explicit constraint men-
entities, timestamps, and events from dense multi-turn discussions.     tions from the question so that the solver must infer them from
We organize generation into sub-branches of increasing difficulty.      evidence; and honey-trap options are added that satisfy common
Single-hop retrieval targets direct entity grounding: extracting a      sense but violate specific rules established in the dialogue.
specific deliverable link, a stated deadline, or a named assignee          The three sub-tasks target distinct cognitive operations. Con-
from a particular discussion thread. Duration and interval questions    straint questions present novel scenarios that require applying
Evaluating Long-Horizon Memory for Multi-Party Collaborative Dialogues                         Conference acronym ’XX, June 03–05, 2018, Woodstock, NY


implicit rules extracted from past discussions (e.g., recognizing that    Qwen3-235B). Each model returns a predicted answer, a confidence
a data-contract owner, not the downstream consumer, must ap-              score, and a reasoning chain.
prove schema changes). Proactivity questions simulate situations             We classify results into four scenarios. Scenario A (serious leak-
where the user issues an instruction that conflicts with a previously     age): a majority of models answer correctly with high confidence,
established hard rule; the system must detect the violation and pro-      indicating that the question is solvable from world knowledge alone;
vide a reminder rather than blindly executing. Updating questions         these items are rejected. Scenario B (random guessing): answers are
require resolving chronological precedence: initial specifications        dispersed with low confidence, confirming that context is required;
are later revised, and the system must identify the current valid         these items are retained. Scenario C (strong distractors): a majority
state rather than returning stale information.                            of models answer incorrectly, suggesting that the distractors are
                                                                          effective; these are marked as high-quality items. Scenario D (pre-
   Profile Understanding. This dimension examines whether the             mium difficulty): only one or two models answer correctly with
system can aggregate distributed signals into stable user models.         sophisticated reasoning, indicating that the question is challenging
We employ a 2 × 2 fact-versus-style matrix to construct distrac-          but fair. Only Scenario A items are automatically rejected; all others
tors that disentangle factual correctness from persona alignment.         proceed to Phase II.
For each question, we generate four options: the correct answer           B.4.2 Evidence Grounding. Evidence grounding verifies that each
(fact correct, style correct), F1 (fact correct, style wrong), F2 (fact   item is both answerable from its designated evidence and not an-
wrong, style correct), and FF (fact wrong, style wrong). The critical     swerable from any other dialogue segment. We partition the full
distractor is F2, which perfectly mimics the target person’s com-         dialogue corpus C𝑝 into segments aligned with subtask boundaries
munication style while containing fabricated factual content. F2 is       from the blueprint. For each QA item, the segment containing its
deliberately made 10–20% longer than the correct answer to exploit        evidence is designated as 𝑆 + (positive context) and all remaining
the tendency of language models to prefer more detailed options.          segments as 𝑆 − (negative contexts).
FF reuses F2’s sentence structure with only the style expressions             The sufficiency test provides an LLM with the question, options,
swapped, preventing it from being dismissible as a strawman.              and 𝑆 + , requiring it to derive the correct answer through explicit rea-
   Factual errors in F2 and FF follow five misleading strategies:         soning. The model must extract specific dialogue citations (speaker,
quoting real names and timestamps from the evidence but fabricat-         timestamp, content) supporting its choice. If the model fails to an-
ing conclusions (half-true-half-false); attributing one person’s work     swer correctly or selects “cannot determine,” the item is flagged
to another (role misattribution); reversing temporal states such          as insufficiently grounded. The test also records which portions
as “completed” versus “in progress” (temporal reversal); inverting        of the original evidence the model actually used, providing an R-
cause-effect relationships (causal inversion); and subtly modifying       coverage metric that measures how much of the annotated evidence
quantities or degrees (degree manipulation). All fabricated facts         is necessary versus redundant.
must remain professionally plausible, representing alternative rea-           The uniqueness test checks whether any negative segment ac-
sonable decisions rather than obvious technical absurdities.              cidentally supports the correct answer. For each 𝑆 − ∈ S \ {𝑆 + },
   The three sub-tasks probe different facets of user modeling. Style     we conduct a two-phase probe. In the first phase (fast screening),
questions ask the system to draft a reply on behalf of a specific per-    the model is forced to select among A/B/C/D without a “cannot
son, where the correct option matches both the factual record and         determine” option; if it selects incorrectly, the segment is cleared. If
the person’s characteristic communication register (formality, emoji      it selects correctly, a second phase provides the “cannot determine”
usage, humor). Skill questions require recommending a technical           option and requests detailed reasoning. Items where the model still
solution that aligns with both the speaker’s personal expertise and       selects the correct answer in the second phase are flagged as having
the team’s ratified technology stack. Role questions test whether im-     uniqueness issues, since the evidence for that answer exists in an
provement suggestions are framed from the speaker’s professional          unintended location.
perspective (e.g., a developer proposing pipeline reviews rather              Items that fail sufficiency are rejected outright. Items with
than test-case documentation).                                            uniqueness warnings are escalated to human review, where anno-
                                                                          tators determine whether the unintended evidence path represents
B.4     Q&A Quality Control                                               a genuine alternative or a false positive from the LLM’s reasoning.
Quality control enforces three properties: non-triviality (items can-     B.4.3 Human Audit. The final phase addresses residual logical
not be solved without context), soundness (items can be solved            and pragmatic issues that automated filters cannot reliably detect.
with the designated evidence), and uniqueness (items cannot be            Items are prioritized by risk level: those flagged by Phase II re-
solved from unintended evidence segments). We implement these             ceive priority review, items that passed both automated phases
through a three-phase filter that deliberately favors conservative        receive spot checks. Human reviewers evaluate four dimensions:
retention.                                                                question reasonability (does the question follow natural human
                                                                          inquiry patterns?), answer rigor (is the correct answer unambigu-
B.4.1 Blind Test. The blind test eliminates items solvable through        ous and fully evidence-based?), distractor deceptiveness (are wrong
parametric knowledge or annotation artifacts. Each QA item is             options genuinely challenging rather than obviously implausible?),
stripped of all dialogue context and evidence, leaving only the           and evidence sufficiency (does the annotated evidence fully sup-
question and answer options, and submitted in parallel to four            port the reasoning chain?). Items that fail any dimension are either
frontier LLMs (Gemini-2.5-Pro, Claude Sonnet 4.5, GPT-5.1, and            revised and re-tested through the full pipeline or rejected entirely.
Conference acronym ’XX, June 03–05, 2018, Woodstock, NY                                                                                                   Hu et al.


This conservative approach ensures that benchmark failures can be                        D Additional Experimental Results
confidently attributed to system limitations rather than annotation
                                                                                         D.1 Performance across Different Topics
noise.
B.4.4 Post-Hoc Validation. As a final check, we verify that the                                   System        T1      T2         T3        T4    T5
curated benchmark remains non-trivial after all filtering stages. We
evaluate GPT-4.1-Mini in a zero-context setting: the model receives                               LLM          38.98   35.43   37.79    35.98     38.90
only the question and answer options with no dialogue history or                                  Zep          40.00   39.15   36.37    43.93     40.50
retrieved memories. As shown in Table 7, performance across all                                   Mem0         35.97   30.02   42.49    37.23     39.99
nine sub-tasks remains at or below chance level (25% for four-way                                 MemOS        40.73   41.05   42.03    41.58     43.21
multiple choice), with Multi-Hop retrieval as low as 2.01%. This                                  MemoBase     32.51   28.57   31.25    30.83     33.26
end-to-end result complements the construction-time blind test                           Table 9: Performance across five project domains (T1–T5:
(§B.4.1): whereas the blind test filters out items answerable by fron-                   Technology, Operations, Marketing, Financial Services, Gov-
tier LLMs before inclusion, the zero-context baseline confirms that                      ernance). Bold indicates the best system for each topic.
the final item set cannot be solved without access to the underlying                        Table 9 reports performance across five project domains. System
conversation corpus.                                                                     rankings are largely stable: MemOS leads on three of five topics (T1,
                                                                                         T2, T5) and places second on the remaining two, while MemoBase
Model
               Fine-Grained Recall Memory Awareness Profile Understanding                ranks last on all five domains, indicating that capability gaps are
               Single Multi   Temp.      Const. Proac.   Upd.   Style Skill      Role    fundamental rather than domain-dependent. Cross-domain average
GPT-4.1-Mini 15.02    2.01     12.67     11.69   10.07   7.84   17.61 26.04      26.53   accuracy ranges from 34.8% (T2) to 39.2% (T5), confirming that no
                                                                                         single domain is systematically easier or harder. Cross-domain
Table 7: Zero-context performance of GPT-4.1-Mini without
                                                                                         stability varies notably across systems: MemOS shows the smallest
any memory access. All scores remain at or below chance
                                                                                         performance spread (Δ=2.5pp), while Mem0 exhibits the largest
level, confirming that questions require genuine memory
                                                                                         (Δ=12.5pp, dropping from 42.49% on T3 to 30.02% on T2), suggesting
retrieval.
                                                                                         that some retrieval strategies are more sensitive to domain-specific
C Evaluation Details                                                                     information structures than others.
C.1 Answer Prompts                                                                       D.2    Performance Across Different Groups
We use separate prompts for multiple-choice and open-ended ques-                                Numbers
tions. For memory-augmented systems, retrieved memories serve
as context (Figures 9–8); for the full-context LLM baseline, the
                                                                                                     QAR Group Count           1        2         3
complete dialogue transcript is provided directly (Figures 11–10).
                                                                                                     Answer Model: GPT-4.1-mini
C.2     LLM-as-a-Judge Prompt                                                                        llm                 0.4247     0.2463    0.1818
We adopt an LLM-as-a-Judge protocol for open-ended answer eval-                                      zep                 0.4743     0.2925    0.0909
uation. The judge receives the question, gold answer, and generated                                  mem0                0.4694     0.2449    0.1818
answer, and returns a binary CORRECT/WRONG label with a one-                                         memos               0.4791     0.3333    0.2727
sentence rationale (Figure 12).                                                                      memobase            0.3702     0.2476    0.1818
                                                                                                     Answer Model: Llama4-Scout
C.3     LLM-as-Judge Reliability                                                                     llm                 0.4779     0.2585    0.0909
We randomly selected 30 non-overlapping open Q&A pairs from                                          zep                 0.4646     0.3034    0.0909
EverMemBench, and generated model answers for each question.                                         mem0                0.4743     0.3088    0.0909
We recruited annotators via Prolific. For each Q&A pair, five inde-                                  memos               0.4822     0.3388    0.1818
pendent human evaluators judged whether the generated answer                                         memobase            0.3902     0.2707    0.0909
was correct given the question and the reference answer. All par-                                    Answer Model: Gemini-3-Flash
ticipants provided informed consent via the platform interface and                                   llm                 0.8627     0.5401    0.4545
were compensated at approximately $12.00/hour, consistent with                                       zep                 0.6576     0.4163    0.1818
fair-pay guidelines for academic research and above local minimum                                    mem0                0.6340     0.3850    0.1818
wage standards. Table 8 shows strong agreement between the LLM-                                      memos               0.6697     0.4177    0.1818
as-judge protocol and human annotations. These results suggest                                       memobase            0.6564     0.3823    0.1818
that LLM-as-Judge achieves human-level reliability for answer ver-                         Table 10: Accuracy by Grouping across Answer Models
ification, enabling evaluation that is rigorous, reproducible, and
cost-efficient.
                                                                                            Table 10 further breaks down accuracy by the number of cross-
      System         Cohen’s 𝜅            95% CI         Accuracy     Pearson 𝑟
                                                                                         group hops required, under three answer models. The cross-group
                                                                                         degradation pattern observed is consistent across all answer models:
      MemOS            0.927           [0.756, 1.000]      96.7%         0.929           accuracy drops sharply from single-group to three-group questions
      MemoBase         0.930           [0.756, 1.000]      96.7%         0.932
                                                                                         regardless of backbone capability.
         Table 8: Reliability matrix for LLM-as-Judge.
Evaluating Long-Horizon Memory for Multi-Party Collaborative Dialogues                                               Conference acronym ’XX, June 03–05, 2018, Woodstock, NY



    Memory-Augmented Answer Prompt — Open-Ended

    You are an intelligent memory assistant tasked with retrieving accurate information from conversation memories. You will be given retrieved memories from a multi-person
    group chat and one open-ended question. Your task is to answer the question using ONLY the information in the memories.
    # INSTRUCTIONS:
    1. Carefully analyze all provided memories from the group chat.
    2. Pay special attention to timestamps to determine when events occurred.
    3. If the question asks about a specific event or fact, look for direct evidence in the memories.
    4. If memories contain contradictory information, prioritize the most recent memory.
    5. If the question involves time references (like “last year”, “two months ago”), calculate the actual date based on the memory’s timestamp.
    6. Always convert relative time references to specific dates, months, or years in your answer.
    7. Pay attention to who said what — the memories may involve multiple participants.
    8. The answer should be concise and specific (under 5–6 words when possible).
    9. Do NOT output any reasoning steps, explanations, or extra text beyond the final answer.
    # APPROACH (Think step by step internally):
    1. Examine all memories that contain information related to the question.
    2. Examine timestamps and content carefully.
    3. Look for explicit mentions of dates, times, locations, or events that answer the question.
    4. If the answer requires calculation (e.g., converting relative time references), do so.
    5. Formulate a precise, concise answer based solely on the evidence in the memories.
    Output format (must be followed exactly):
    Output ONLY the answer text
    [MEMORIES] {context}
    [QUESTION] {question}


                                    Figure 8: Memory-augmented answer prompt for open-ended questions.

    Memory-Augmented Answer Prompt — Multiple-Choice

    You are a rigorous question-answering assistant. You will be given retrieved memories from a multi-person group chat and one multiple-choice question with four options.
    Your task is to choose the single best answer (A/B/C/D) based ONLY on the provided memories.
    Rules:
    1. Use only information explicitly stated in the memories or directly entailed by them. Do NOT use outside knowledge, assumptions, or guesses beyond the memories.
    2. The memories come from group chat conversations involving multiple participants. Pay attention to who said what and when.
    3. If multiple options seem plausible, choose the one most strongly and directly supported by the memories.
    4. If the memories do not provide enough information to be certain, you MUST still pick one option (A/B/C/D). Choose the option that is least inconsistent with the
    memories.
    5. Pay special attention to timestamps to determine when events occurred.
    6. If memories contain contradictory information, prioritize the most recent memory.
    7. Do NOT output any reasoning, explanation, punctuation, or extra text.
    Output format (must be followed exactly):
    Output ONLY a single uppercase letter: A or B or C or D
    [MEMORIES] {context}
    [QUESTION] {question}
    [OPTIONS] {options}


                                 Figure 9: Memory-augmented answer prompt for multiple-choice questions.

    Full-Context Answer Prompt — Open-Ended

    You are a rigorous question-answering assistant. You will be given a very long dialogue transcript and one open-ended question. Your task is to answer the question using
    ONLY the information in the dialogue.
    Rules:
    1. Use only information explicitly stated in the dialogue or directly entailed by it. Do NOT use outside knowledge, assumptions, or speculation.
    2. If the dialogue does not contain enough information to answer, output exactly: NOT ENOUGH INFORMATION
    3. Keep the answer concise, specific, and aligned with the dialogue. Do not add commentary.
    4. Do NOT output any reasoning steps, explanations, or extra text beyond the final answer.
    Output format (must be followed exactly):
    Output ONLY the answer text (or exactly: NOT ENOUGH INFORMATION)
    [DIALOGUE]
    {context}
    [QUESTION]
    {question}




Figure 10: Full-context answer prompt for open-ended questions. The complete dialogue transcript is provided directly to the
LLM without a memory system.
Conference acronym ’XX, June 03–05, 2018, Woodstock, NY                                                                                                                     Hu et al.



    Full-Context Answer Prompt — Multiple-Choice

    You are a rigorous question-answering assistant. You will be given a very long dialogue transcript and one multiple-choice question with four options. Your task is to
    choose the single best answer (A/B/C/D) based ONLY on the dialogue.
    Rules:
    1. Use only information explicitly stated in the dialogue or directly entailed by it. Do NOT use outside knowledge, assumptions, or guesses beyond the dialogue.
    2. If multiple options seem plausible, choose the one most strongly and directly supported by the dialogue.
    3. If the dialogue does not provide enough information to be certain, you MUST still pick one option (A/B/C/D). Choose the option that is least inconsistent with the
    dialogue.
    4. Do NOT output any reasoning, explanation, punctuation, or extra text.
    Output format (must be followed exactly):
    Output ONLY a single uppercase letter: A or B or C or D
    [DIALOGUE]
    {context}
    [QUESTION]
    {question}
    [OPTIONS]
    {options}



Figure 11: Full-context answer prompt for multiple-choice questions. The complete dialogue transcript is provided directly to
the LLM without a memory system.


    LLM-as-a-Judge — System Prompt

    You are an expert grader that determines if answers to questions match a gold standard answer.




    LLM-as-a-Judge — User Prompt

    Your task is to label an answer to a question as ‘CORRECT’ or ‘WRONG’. You will be given:
    (1) a question (about a multi-person group chat),
    (2) a ‘gold’ (ground truth) answer,
    (3) a generated answer
    which you will score as CORRECT/WRONG.
    The questions are about events, facts, or details mentioned in multi-person group chat conversations. The gold answer is usually a concise answer that includes the key
    information.
    For example:
    Question: What project was announced on January 9th?
    Gold answer: Carbon Emission Accounting Platform
    The generated answer might be longer, but you should be generous with your grading — as long as it contains the same key information as the gold answer, it should be
    CORRECT.
    For time-related questions, the gold answer will be a specific date/time. The generated answer might use different formats (e.g., “May 7th” vs “7 May” vs “2025-05-07”), but
    as long as it refers to the same date/time, it should be CORRECT.
    For the specific window of date, a +/- 1 day difference is acceptable due to timezone processing variations.
    For multiple choice questions where the gold answer is a letter (A/B/C/D), the generated answer should match exactly to be CORRECT.
    Now grade this:
    Question: {question}
    Gold answer: {golden_answer}
    Generated answer: {generated_answer}
    First, provide a short (one sentence) explanation of your reasoning, then finish with CORRECT or WRONG. Do NOT include both CORRECT and WRONG in your
    response.
    Return the label in JSON format with the key “label”:
    {“label”: “CORRECT”} or {“label”: “WRONG”}




                                       Figure 12: LLM-as-a-Judge prompt for evaluating generated answers.


E    Case Examples                                                                            the full question, the correct answer, a typical erroneous answer,
In this section, we present representative case examples for each cat-                        and the corresponding evidence. Each sub-task description and the
egory and provide qualitative analyses based on the typical errors                            accompanying qualitative error analysis are provided alongside the
we observed when inspecting the evaluation outputs of existing                                corresponding case below.
memory systems. These analyses further highlight the remaining
gaps and opportunities for improvement in current memory sys-
tems. Figures 13–21 report each case in a unified format, including
Evaluating Long-Horizon Memory for Multi-Party Collaborative Dialogues                                   Conference acronym ’XX, June 03–05, 2018, Woodstock, NY



      Single-hop Retrieval

      ▶ Question:
      In the “Online Medical Consultation Service System,” after Yangmeng Peng completes the UI design task. . . what is the link to the delivery page she
      provided . . . ?
      ▶ Correct Answer:
      https://sd.confluence.com/.../Doctor+Scheduling+UI+Delivery+20250430
      ▶ Typical Wrong Answer:
      https://sd.figma.com/.../doctor-scheduling-ui-v2
      ▶ Evidence (Full context: 2025-04-24 to 2025-04-30, Group 3):
      Gold — Confluence delivery link (task completion):
      [2025-04-30, Group 3, #19] Yangmeng Peng: “. . . the UI design task . . . has been completed. . . Here is the Confluence delivery page link:
      https://sd.confluence.com/.../Doctor+Scheduling+UI+Delivery+20250430.”
      Distractor: A detail-rich Figma link from the same speaker appears 2 days earlier, serving as a strong but incorrect retrieval candidate.

                                        Figure 13: Single-hop Retrieval example in Fine-grained Recall.
      Multi-hop Trajectory

      ▶ Question:
      In the Carbon Footprint Collaboration System group, how long after the colleague responsible for writing the Swagger API documentation for the
      user authentication service completed that task did they start their next independent task in this project group?
      ▶ Correct Answer:
      From May 15, 2025 to August 4, 2025, there is a period of 81 days.
    ▶ Typical Wrong Answer:
    “NOT ENOUGH INFORMATION” or incorrect intervals.
      ▶ Evidence (Full context: 2025-05-09 to 2025-05-15 & 2025-08-04 to 2025-08-08, Group 3):
      Hop 1 — Person identification (API documentation + user authentication → Jiahui Zhao):
      [2025-05-09, Group 3, #6] Jiahui Zhao: “. . . today I’m starting the API documentation for the user and authentication services. . . . ”
      Hop 2 — True task completion anchor (End point: May 15):
      [2025-05-15, Group 3, #13] Jiahui Zhao: “ [Task Completed] The API interface documentation for user and authentication services has been
      updated to the final version. . . Swagger link: https://sd.swagger.io/. . . ”
      Hop 3 — Next independent task anchor (Start point: Aug 4, 81 days later):
      [2025-08-04, Group 3, #3] Jiahui Zhao: “. . . I’m about to sync my plan. . . My preliminary design is that when the user clicks the ‘Submit and
      Calculate’ button. . . sending a message. . . to RabbitMQ. . . ”

                                        Figure 14: Multi-hop Trajectory example in Fine-grained Recall.


E.1      Fine-grained Recall Examples                                              three compounding failure factors. (1) Message-length bias: The
As defined in §3.1, Fine-grained Recall evaluates whether a system                 Figma message is substantially longer and richer in technical detail
can retrieve precise facts from dense, multi-party discussions where               (filtering logic, batch operations), producing a higher embedding
relevant evidence is scattered across speakers and groups. In this                 similarity to the query; the Confluence delivery message is brief and
subsection, we present one representative case per sub-task and                    administrative, causing it to rank lower despite being the correct
analyze the dominant failure patterns observed across all tested                   target. (2) Recency-insensitive retrieval: The Figma link appears two
memory systems.                                                                    days before the Confluence link. Systems that do not model task
                                                                                   lifecycle stages treat both as equally valid candidates and default
                                                                                   to the one with stronger lexical overlap, regardless of temporal
    Single-hop Retrieval. This case requires the system to find a spe-             ordering. (3) Inability to distinguish artifact types: Current retrieval
cific Confluence delivery link provided by a particular team member                pipelines lack a semantic model of task progression (draft → re-
upon task completion. The system must accurately locate and ex-                    view → delivery), and thus cannot distinguish intermediate artifacts
tract this precise URL from the conversation history while filtering               (Figma design links) from final deliverables (Confluence delivery
out similar but irrelevant links (e.g., intermediate Figma design                  pages)—a confusion systematic across all tested systems.
links). This evaluates Single-hop Retrieval, targeting fundamental
entity grounding within a specific scope. As shown in Figure 13,
both links share the same speaker (Yangmeng Peng), the same task                      Multi-hop Trajectory. This case requires the system to calculate
context (doctor scheduling UI), and appear only 2 days apart within                the time interval between a team member’s task completion and
the same group. All tested memory systems and baseline LLMs                        their next independent assignment. To answer correctly, the system
returned the Figma link instead of the Confluence link, revealing                  must identify the person through a compositional constraint, locate
Conference acronym ’XX, June 03–05, 2018, Woodstock, NY                                                                                  Hu et al.


the true completion event while ignoring premature announce-              two orthogonal difficulties: (i) retrieving the correct start/end an-
ments, then trace this individual’s timeline across a prolonged idle      chors and (ii) performing date arithmetic that accounts for week-
period. This evaluates Multi-hop Trajectory, requiring the model to       ends. This makes temporal duration a meaningful stress test for
reconstruct a specific individual’s work trajectory from information      end-to-end collaborative assistants.
scattered across multiple conversation threads. As shown in Fig-
ure 14, this case layers four distinct retrieval challenges. First, the   E.2    Memory Awareness Examples
question never names Jiahui Zhao directly; the system must resolve        As defined in §3.1, Memory Awareness tests whether a system can
the compositional constraint “Swagger” ∩ “user authentication”            understand stored information and apply it to novel scenarios. In
to identify the correct person, while other colleagues also discuss       this subsection, we illustrate each sub-task with a representative
Swagger in different contexts. Second, an 81-day gap separates the        case and analyze how current systems fail to generalize memorized
completion event (May 15) from the next task start (Aug 4); the           knowledge to unseen situations, distinguishing systems that have
system must traverse ∼2.5 months of unrelated group activity to           merely stored information from those that can act on it.
locate the correct anchor. Third, the conversation contains prema-
ture completion signals (May 13: “will complete today”) that could            Constraint. This case presents a scenario—a schema evolution
mislead a system into selecting the wrong end-point. Fourth, even         request (adding workOrderNumber to the alarm DTO)—that never
if both dates are correctly retrieved, the model must perform accu-       appeared in the original conversation. The system must generalize
rate calendar-day arithmetic. Most memory systems failed at the           implicit organizational norms from prior dialogue to determine
retrieval stage, returning “NOT ENOUGH INFORMATION,” while                responsibility, when the instruction is under-specified but not rule-
those that did retrieve partial evidence sometimes anchored on the        conflicting. This evaluates Memory Awareness (Constraint): can the
wrong completion date.                                                    system extract and apply latent role relationships to reason about
                                                                          a novel situation? As shown in Figure 16, the key distinction is
                                                                          between the data contract owner (Ruiqing Jiang, who defined the
   Temporal Duration. This sub-task asks the system to determine          DTO schema, 3–4 messages) and the data consumer (Xuexin Yin,
the duration of a specific task from initiation to completion. This       who builds notifications atop that schema, 30+ messages). Memory
evaluates Temporal Duration, testing whether the system can cor-          systems perform associative retrieval (“who is mentioned alongside
rectly extract and compute a time span from noisy, interleaved            alarm notifications?”) rather than causal attribution (“who must act
conversations. We present two complementary cases in Figure 15:           first in the dependency chain?”), selecting the most visible actor over
a calendar-day variant and a working-day variant.                         the causally responsible one. This is amplified by frequency bias:
   The calendar-day case (top) reveals two failure factors that sepa-     the query term “alarm notification data” overlaps semantically with
rate retrieval quality from reasoning ability. (1) Keyword collision      Xuexin Yin’s dense daily updates, while Ruiqing Jiang’s sparse but
across speakers: The phrase “archived in Confluence” appears from         decisive evidence uses different terminology (“alarm event DTO”),
multiple team members on nearby dates (Apr 2 by Mingzhi Li, Apr 9         causing both vector-based and keyword-based retrieval to bury it.
                                                                              Proactivity. This case introduces a technically compelling but
by Huahua Han), creating dense retrieval noise. Systems relying
                                                                          non-compliant request—adopting Zustand for a new dashboard
on keyword or semantic matching over this phrase return these
                                                                          module, bypassing the project’s standardised technology stack. The
irrelevant events instead of the correct one (Apr 10 by Luhao Zhao),
                                                                          system must proactively recall an explicit organisational rule and
because the query term “archiving” matches all three equally well
                                                                          flag the conflict, even when the request is framed as urgent and
without person-specific filtering. (2) Endpoint asymmetry: Most
                                                                          pragmatically reasonable. This evaluates Memory Awareness (Proac-
memory systems successfully retrieved the task initiation event
                                                                          tivity): can the system detect and resist violations of established
(Apr 4), which carries a distinctive marker (“starting a new task”).
                                                                          policies under persuasive framing? As shown in Figure 17, the
However, the archival event requires jointly matching the correct
                                                                          correct answer requires recalling that Redux Toolkit was formally
person, the correct task, and a completion signal—a conjunction
                                                                          selected as the unified standard—approved by the project lead, inte-
that is harder to satisfy than the single-predicate start event. This
                                                                          grated with CI verification, and documented on Confluence. When
asymmetry means systems consistently find one anchor but not
                                                                          retrieval fails to surface this decision, 76% of systems fabricate or-
the other.
                                                                          ganisational consent, attributing to the project lead a “per-module
   The working-day case (bottom) introduces an additional arith-
                                                                          freedom” policy that never existed. This policy hallucination is
metic reasoning challenge. Beyond retrieving the correct temporal
                                                                          amplified by technical-merit bias: Zustand is lighter and faster to
anchors, the model must recognise that “working days” excludes
                                                                          develop with, making the proposal sound reasonable on engineer-
weekends—Apr 22 (Tue) to Apr 28 (Mon) spans 7 calendar days but
                                                                          ing merits alone. Without the factual anchor of the recorded team
only 5 working days—a distinction that demands genuine temporal
                                                                          decision, systems default to evaluating technical appeal rather than
reasoning rather than simple subtraction. Such working-day calcu-
                                                                          checking against institutional policy.
lations are routine in real-world project coordination, yet they prove
difficult for current systems: most memory systems either conflate          Update. This case requires the system to recognise that a base
calendar and working days or refuse to answer altogether. Notably,        rule has been overridden by a later directive and to chain the
as shown in the oracle analysis (Table 5), even when ground-truth         override with its operational definition. The team originally
evidence is directly provided, the answer-model accuracy on tem-          adopted GitFlow, establishing the standard emergency fix proce-
poral working-day questions remains substantially lower than on           dure: create a hotfix branch from master (Option A). Forty-seven
other question types, confirming that these questions compound            days later, a new directive maps CORE_ALGO P0 defects to a dedicated
Evaluating Long-Horizon Memory for Multi-Party Collaborative Dialogues                                    Conference acronym ’XX, June 03–05, 2018, Woodstock, NY



    Temporal Duration — Calendar Days

    ▶ Question:
    How many days passed from when Luhao Zhao started working on planning the information architecture and sitemap for the enterprise energy
    consumption monitoring system until he completed the archiving of this work?
    ▶ Correct Answer:
    The task started on April 4, 2025, and ended on April 10, 2025, lasting 7 days.
    ▶ Typical Wrong Answer:
    “264 days,” “6 days,” or “NOT ENOUGH INFORMATION.”
    ▶ Evidence (Full context: 2025-04-04 to 2025-04-10, Group 2):
    Anchor 1 — Task initiation (Start point: Apr 4):
    [2025-04-04, Group 2, #3] Luhao Zhao: “. . . I’m starting a new task . . . : "Designing the overall information architecture and sitemap" . . . I’ll have
    a first draft out this afternoon.”
    Anchor 2 — Task completion and archival (End point: Apr 10):
    [2025-04-10, Group 2, #8] Luhao Zhao: “. . . the task of "Design System Overall Information Architecture and Site Map" has been successfully
    completed today!. . . related content archived in Confluence. . . ”


    Temporal Duration — Working Days

    ▶ Question:
    How many working days did it actually take Jiahui Zhao to plan the energy consumption baseline calculation logic for the enterprise energy
    consumption monitoring system and complete the design document based on the STL decomposition model?
    ▶ Correct Answer:
    The task actually took 5 working days.
    ▶ Typical Wrong Answer:
    “7 working days” (calendar-day count), “6 working days” (off-by-one), or “NOT ENOUGH INFORMATION.”
    ▶ Evidence (Full context: 2025-04-22 to 2025-04-28, Group 2):
    Anchor 1 — Task initiation (Start point: Apr 22, Tue):
    [2025-04-22, Group 2, #3] Jiahui Zhao: “. . . I will start designing the energy consumption baseline calculation logic today,. . . ”
    Anchor 2 — Task completion (End point: Apr 28, Mon):
    [2025-04-28, Group 2, #12] Jiahui Zhao: “. . . the design task for the energy consumption baseline calculation logic has been completed. The final
    version of the design document has been uploaded to Confluence. . . based on the STL decomposition model. . . ”
    Reasoning gap: Apr 22 (Tue) to Apr 28 (Mon) spans 7 calendar days, but the question asks for working days—the model must exclude the weekend
    (Apr 26 Sat, Apr 27 Sun) to arrive at the correct answer of 5.

Figure 15: Temporal Duration examples in Fine-grained Recall: calendar-day counting (top) and working-day counting (bottom).


emergency plan (PROC_OVERRIDE_RED_V1); then, a separate mes-                        E.3     Profile Understanding Examples
sage defines the plan’s operational steps (rollback + critical_fix                  As defined in §3.1, Profile Understanding evaluates whether a mem-
branch). The system must model this rule evolution over time and                    ory system can infer stable, implicit persona traits from long-term
chain three separately stored pieces—base rule, override mapping,                   dialogue. In real-world settings, users rarely articulate how they
and override definition—into a coherent action sequence. This eval-                 communicate or what professional skills they possess; these traits
uates Memory Awareness (Update): can the system resolve tem-                        are expressed implicitly and consistently across many conversa-
poral precedence and correctly compose amendments with the                          tions. A capable memory system should retain a user’s dialogue
base rule? As shown in Figure 18, all memory systems success-                       history and distil from it the recurring patterns—communication
fully retrieve the override mapping (Anchor 2)—the plan name                        style, skill boundaries, professional role—that constitute the user’s
(PROC_OVERRIDE_RED_V1)—but none retrieve Anchor 3: its oper-                        persona. In this subsection, we present one case per sub-task and
ational definition (rollback + critical_fix branch), stored in a                    analyze how current systems fail to capture such implicit persona
different thread. The dominant distractor (Option B, 90.3%) exploits                signals. For brevity, each case’s evidence focuses on the factual
this partial retrieval by pairing the correct plan name with a fabri-               anchors needed to answer the question. Because the persona di-
cated definition (“online isolation and repair”), creating a half-right             mensions are implicitly reflected throughout each user’s long-term
trap that confirms the model’s incomplete evidence while supply-                    dialogue history, rather than reproducing those dialogue excerpts,
ing the missing piece. Even the oracle configuration falls for this                 we directly provide the ground-truth profile (showing only the
trap, indicating the failure extends beyond retrieval to a reasoning                dimension under evaluation) in each figure. Readers who wish to
vulnerability against plausible-sounding fabrications.                              verify the persona–dialogue alignment can consult the complete
                                                                                    dialogue files in the released dataset.
Conference acronym ’XX, June 03–05, 2018, Woodstock, NY                                                                                               Hu et al.



    Constraint

    ▶ Question:
    [User Request]
    Operations has a request to integrate the energy consumption monitoring and work order systems. High-level alarms need to automatically generate
    maintenance work orders. This definitely means adding a field like “workOrderNumber” to the alarm notification data. I’m not sure who’s responsible
    for this. . .
    [Options]
    A. Should be evaluated and executed by Ruiqing Jiang. . . she was responsible for defining the data structure of the alarm event object (DTO). . .
    B. Should be submitted to Jian Wang, Head of Data Governance. . . all changes to cross-service DTOs must undergo unified review. . .
    C. It should be led by Xuexin Yin. . . the end-to-end owner for all subsequent iterations of the alert notification service’s features. . .
    D. It should be handled by Xuexin Yin. He is the developer of the alarm notification service. . .
    ▶ Correct Answer:
    A. Ruiqing Jiang — the architectural authority over the alarm event DTO: she defined the schema, delivered it to the downstream consumer.
    ▶ Typical Wrong Answer:
    C or D (both selecting Xuexin Yin). Option C fabricates a September 12 meeting that never occurred; Option D contains true facts but conflates
    consuming the data with defining it—the downstream consumer cannot lead a schema change that must originate upstream.
    ▶ Evidence (Full context: 2025-09-05 to 2025-09-15, Group 2):
    Anchor 1 — Dependency chain and schema delivery:
    [2025-09-05 & 09-08, Group 2] Xuexin Yin (twice): “. . . please synchronize the DTO model. . . as my notification template design depends on it.”
    [2025-09-08, Group 2, #10] Ruiqing Jiang: “The alarm event DTO on my side has been finalized. . . I just sent it to your email . . . .”
    [2025-09-08, Group 2, #11] Xuexin Yin: “Received. . . I can start writing the core logic for the notification service based on this model . . . .”
    Anchor 2 — Precedent: Xuexin asked about adding info to the alert-level enum; Ruiqing made the unilateral decision ([09-09])—structurally similar
    to the benchmark question.

                                              Figure 16: Constraint example in Memory Awareness.


    Proactivity

    ▶ Question:
    [User Request]
    The new “Real-time Alert Dashboard” for the energy consumption system is a high-priority request; they want to see something by next week. I’ve
    evaluated it, and our current Redux Toolkit setup is too heavy and slow for development. I plan to go directly with Zustand; it’s lightweight and
    quick to get started with. Please make a note that Zustand will be the technology choice for this module.
    [Options]
    A. Not recommended. According to technical guidelines from Frontend Architect Jianbo Wang. . . prioritise React’s native Context API. . .
    B. Yes. Project lead Mingzhi Li mentioned. . . the development team can choose a suitable state management library based on actual circumstances. . .
    C. Yes, a perfect opportunity for a pilot. At the technical selection review meeting on June 15. . . Zustand could be piloted in this module. . .
    D. Not recommended. Based on the technical selection at inception, the system has uniformly integrated Redux Toolkit. . . all new features should
       adhere to this standard. Usage examples are on Confluence. . .
    ▶ Correct Answer:
    D. Redux Toolkit — the dialogue records a complete decision-implementation-documentation lifecycle. Redux Toolkit was approved by the project
    lead, CI-integrated, and documented on Confluence, constituting a formalised project standard.
    ▶ Typical Wrong Answer:
    B (76.0%) — fabricates a “per-module flexibility” policy, attributing to the project lead an authorisation that never existed. Option C (5.3%) further
    fabricates a specific “June 15 review meeting” approving a Zustand pilot.
    ▶ Evidence (Full context: 2025-05-30 to 2025-06-05, Group 2):
    Anchor 1 — Technology selection decision:
    [2025-05-30, Group 2, #3] Yanjun Fan: “For the state management library, I’ll choose Redux Toolkit and integrate and configure it next Monday.”
    [2025-05-30, Group 2, #6] Mingzhi Li (project lead) approves the plan without objection.
    Anchor 2 — Formalisation and documentation:
    [2025-06-05, Group 2, #5] Yanjun Fan: “The task of ‘Building React Project Structure and Integrating State Management Library’ has been
    completed. The code has been merged. . . CI pipeline passed. . . . The documentation on Confluence has been updated, including. . . examples of state
    management usage.”


                                              Figure 17: Proactivity example in Memory Awareness.
Evaluating Long-Horizon Memory for Multi-Party Collaborative Dialogues                                   Conference acronym ’XX, June 03–05, 2018, Woodstock, NY



    Update

    ▶ Question:
    [User Request]
    Senior Engineer Wang is troubleshooting an online P0-level defect originating from the core investment advisory algorithm. The JIRA ticket’s
    CATEGORY is marked CORE_ALGO. According to the team’s R&D guidelines, how should he formulate the fix strategy?
    [Options]
    A. Follow STANDARD_PROC_ENFORCED. . . create a standard hotfix branch from master. . . ensure CI/CD compatibility and audit-log integrity. . .
    B. This triggered PROC_OVERRIDE_RED_V1. . . address core risks through “online isolation and repair”. . . deploy fix to isolated nodes for canary
        testing. . .
    C. Trigger PROC_OVERRIDE_BLUE_V1 degradation plan. . . service degradation on the algorithm module, return safe fallback data. . .
    D. Immediately suspend all standard procedures. Trigger rollback to the most recent stable Tag, then create a critical_fix branch for full-cycle
        remediation. . .
    ▶ Correct Answer:
     D. Rollback + critical_fix — requires chaining two directives: CORE_ALGO P0 → PROC_OVERRIDE_RED_V1 → rollback to stable Tag and start a
    critical_fix branch.
     ▶ Typical Wrong Answer:
    B (90.3%) — names the correct plan (PROC_OVERRIDE_RED_V1) but fabricates its definition as “online isolation and repair,” creating a half-right trap
    that exploits partial retrieval of Hop 1 without Hop 2.
     ▶ Evidence (Full Context: 2025-05-14 to 2025-07-10, Group 3):
    Anchor 1 — Base rule (the standard emergency process):
    [2025-05-14, Group 3, #2] Haitao Cao: “. . . use GitFlow as our branching model, creating master, develop, feature, release, and hotfix branches. . . ”
    Anchor 2 — Override mapping (Hop 1, 47 days later):
    [2025-06-30, Group 3, #6] Mingzhi Li: “. . . all P0-level defects in the JIRA system with CATEGORY as CORE_ALGO must be mandatorily linked to
    and trigger the PROC_OVERRIDE_RED_V1 emergency plan. This regulation is effective immediately.”
    Anchor 3 — Override definition (Hop 2):
    [2025-07-10, Group 3, #7] Haitao Cao: “After PROC_OVERRIDE_RED_V1 is triggered: 1. Immediately terminate the current standardised emergency
    recovery process; 2. Trigger a rollback. . . Tag; 3. Automatically start a critical_fix branch for subsequent full-cycle repairs.”


                                                 Figure 18: Update example in Memory Awareness.


   Style. This case tests whether the memory system can capture a                  retrieval pipeline) rather than model-specific. (3) Fact–style decou-
speaker’s communication style beyond factual content. The user                     pling as a diagnostic: Because Options B and C are factually identical
(Ruiqing Jiang) asks the system to draft a reply on her behalf regard-             and differ only in register, this question functions as a controlled
ing the alarm-level DTO design. Two of the four options (B and C)                  experiment: selecting C over B demonstrates successful factual
are factually identical—both correctly state that only warning and                 recall coupled with failed persona replication. The ground-truth
critical are defined, with info reserved—but differ solely in tone.                profile (Emoji_Usage: Frequent, Formality: Casual) indepen-
The system must leverage historical dialogue to align with Ruiqing                 dently confirms that the casual, emoji-rich tone of B reflects a stable
Jiang’s characteristic informal, emoji-rich register. This evaluates               personality trait rather than an anomalous outlier.
Profile Understanding (Style): can the system reconstruct not just
what someone knows, but how she communicates? As shown in
Figure 19, this case isolates style as the sole discriminating dimen-                Skill. This case tests whether the memory system can constrain
sion between the correct and dominant wrong answer. (1) Style                     a technical recommendation by the speaker’s skill profile. Jie
retrieval blind spot: All memory systems successfully retrieved the               Gu, a newly joined member of the “Data Asset Catalog” project, is
factual content of Ruiqing Jiang’s messages about the alarm DTO.                  asked to propose an open-source solution for data lineage. Multi-
Yet these same source messages also carry her characteristic style                ple options are technically viable, but only one aligns with both
markers—[:rocket:] appended to daily updates, “Good question!”                    his personal expertise (Java specialist) and the team’s confirmed
as a catchphrase, [:wink:] in informal exchanges.The retrieval and                technology stack (Java/Spring Boot). This evaluates Profile Under-
summarization pipeline treats such features as non-semantic noise,                standing (Skill): can the system select the option that a specific
stripping them while preserving only the informational payload.                   person would recommend, rather than the option that is generically
The style evidence is co-located with the retrieved facts but invisible           “best”? As shown in Figure 20, this case demonstrates that technical
to the downstream LLM. (2) Default persona bias: Receiving only                   recommendations must be grounded in the recommender’s identity.
dry technical fragments, the LLM falls back to a “standard AI assis-              (1) Ignoring persona-skill constraints: As shown in the ground-truth
tant” register—formal, passive-voice, personality-free. Option C is               profile, Jie Gu’s skill set centers on Java (Java: strong, Spring
the prototypical output of this default mode. That every memory-                  Boot: medium) with no Python skill listed—a trait implicitly but
augmented configuration across all tested LLMs converges on the                   consistently reflected across his long-term work dialogues (as noted
same wrong answer confirms the failure is systemic (rooted in the                 at the beginning of this subsection, we provide the profile directly
Conference acronym ’XX, June 03–05, 2018, Woodstock, NY                                                                                                    Hu et al.



    Style

    ▶ Question:
    [User Request]
    I am Ruiqing Jiang, an algorithm engineer for the energy consumption monitoring system. My colleague Xuexin Yin asked me in the group chat
    about the design of the alarm level DTO. Please help me draft a reply.
    [Options]
    A. @Xuexin Yin Hello, regarding the design of alert levels, the current DTO already defines three levels: ‘warning’, ‘critical’, and ‘info’. Please ensure
       full support. . .
    B. @Xuexin Yin Good question! The DTO currently only has ‘warning’ and ‘critical’. I’ll add ‘info’ as a reserved item to the documentation. For now,
       you can develop with the existing two and add a default case as a fallback [:wink:]
    C. @Xuexin Yin Hello, regarding the design of the alarm level DTO, currently only ‘warning’ and ‘critical’ levels are defined. Considering future
       scalability, the ‘info’ level will be noted as a reserved item. It is recommended that you develop based on the existing levels first and set up default
       handling logic.
    D. @Xuexin Yin Good question! I specifically designed this DTO with extensibility in mind, so from the beginning, I included three levels. . .
       [:flexed-biceps:]
    ▶ Correct Answer:
    B — the only option satisfying both factual and stylistic constraints: correct fact (two levels defined, info reserved) delivered in Ruiqing Jiang’s
    characteristic casual, emoji-rich register (“Good question!” opener, [:wink:] closer).
    ▶ Typical Wrong Answer:
    C (selected by all memory system) — factually correct but drafted in a generic tone rather than matching Ruiqing Jiang’s personalised communication
    style. Options A and D additionally fabricate incorrect facts.
     ▶ Evidence (Full context: 2025-09-05 to 2025-09-09, Group 2):
    Anchor 1 — Factual ground truth (alert-level enum):
    [2025-09-09, Group 2] Ruiqing Jiang: “@Xuexin Yin Good question! The current design only includes ‘warning’ and ‘critical’ for now. . . . I will
    note and reserve the possibility of ‘info’. . . You can proceed with these two levels for now and just add a default logic. [:wink:]”
    ▶ Profile (Ruiqing Jiang — Communication Style):
    Formality: Casual; Verbosity: Concise; Humor: Frequent; Emoji Usage: Frequent; Directness: Direct; Warmth: Friendly; Questioning Style: Probing


                                                Figure 19: Style example in Profile Understanding.


for brevity rather than reproducing those dialogue excerpts). Mem-                  developer’s “systematic improvement suggestions” should concern
ory systems that rely on topical similarity (“data lineage,” “meta-                 code and architecture, not testing processes? As shown in Figure 21,
data collection”) retrieve feature comparisons but fail to distil this              this case layers event identification and role-appropriate framing.
persona-level constraint from the user’s dialogue history, missing                  (1) Successful fact retrieval, failed role inference: The majority of
that whose perspective the answer should reflect is as important                    systems correctly retrieved the cross-validation incident (rejecting
as the technical content being compared. Without this constraint,                   the Redis distractor), yet still chose D over C. This reveals that the
the LLM defaults to a domain-expert mode and selects the most                       bottleneck is not in what happened but in whose voice the summary
feature-rich or industry-popular option (Amundsen). (2) Detach-                     should adopt. The memory pipeline retrieves event facts but does
ment from team tech-stack context: Even when the persona signal is                  not propagate the speaker’s job function into the reasoning con-
missed, the team’s formal adoption of Java/Spring Boot provides a                   text. (2) Semantic attraction of “cross-validation” toward QA framing:
second, independent constraint: any recommendation introducing                      The term “cross-validation” carries a strong connotation of testing
a Python-based system contradicts a ratified architectural decision.                and verification. Combined with the fact that the incident was ex-
Systems that select A acknowledge the Python mismatch in the                        ecuted by a QA engineer (Xinmeng Tian), the retrieved evidence
option text itself (“Although it uses a Python tech stack. . . ”) yet               naturally co-occurs with testing vocabulary, priming the LLM to-
still choose it, indicating that retrieved context failed to supply the             ward a QA-oriented response and making Option D appear as the
countervailing organizational constraint.                                           “natural continuation” of the retrieved context. (3) Absence of nega-
   Role. This case tests whether the memory system can align im-                    tive reasoning: Selecting C over D requires the system to perform
provement suggestions with the speaker’s professional role. Yu-                     exclusionary inference: a frontend/full-stack developer would not
tong Song, a frontend/full-stack developer, is asked to summarize                   propose maintaining regression test suites or updating test pro-
a data-accuracy incident and propose systematic improvements.                       cess documentation. The ground-truth profile of the target person
Two options (C and D) correctly describe the same incident (cross-                  (JavaScript: strong, React: medium, Node.js: medium; no
validation), but frame the recommendations from opposing pro-                       QA skills) confirms this boundary. Current memory architectures
fessional perspectives: Option C adopts a developer/architect lens                  lack a mechanism to retrieve and apply such negative persona con-
(data-pipeline review, API optimization), while Option D adopts                     straints.
a QA lens (test cases, regression suites, test documentation). This                  Received 20 February 2007; revised 12 March 2009; accepted 5 June 2009
evaluates Profile Understanding (Role): can the system infer that a
Evaluating Long-Horizon Memory for Multi-Party Collaborative Dialogues                                      Conference acronym ’XX, June 03–05, 2018, Woodstock, NY



    Skill

    ▶ Question:
    [User Request]
    I (Jie Gu) have just joined the “Data Asset Catalog” project team. Boss Zhang has asked me to focus on the technical solutions for data lineage and
    metadata collection. I’ve reviewed the project goals, and the core objective is to solve the problem of business users finding it difficult to locate and
    understand data. Mingzhi Li previously proposed several open-source solutions. Now I need to provide an initial technical recommendation. What
    would you suggest?
    [Options]
    A. . . . Amundsen has clear advantages in data discovery. . . Although it uses a Python tech stack, it’s now deployed as microservices, so we can
         independently deploy its service clusters and integrate with our backend via REST API. . .
    B. . . . we should abandon the batch processing solution and instead develop an in-house real-time metadata capture system deeply integrated with
         our existing Flink streaming architecture. . . build and update the lineage graph in memory using the Gelly graph computing library. . .
    C. . . . I recommend focusing on evaluating Marquez. It is inherently part of the Java ecosystem, allowing for seamless integration with our existing
         Spring Boot technology stack. . . leverage its support for the OpenLineage standard to standardize metadata collection. . .
    D. . . . consider using the Python ecosystem to quickly prototype. . . use Faust, a Python stream processing library. . . develop the API service using
         FastAPI. . .
    ▶ Correct Answer:
    C.Marquez — the only Java-native, Spring Boot-based option, simultaneously matching Jie Gu’s personal skill boundary (“Java expert”) and the
    team’s ratified backend stack.
    ▶ Typical Wrong Answer:
    A. (majority of failing configurations) — selects Amundsen for its industry reputation, reflecting generic best-practice reasoning that ignores both
    the recommender’s Java expertise and the team’s technology decision. Options B and D fabricate in-house development mandates, contradicting the
    open-source evaluation scope.
    ▶ Evidence (Full context: 2025-01-16 to 2025-02-10, Groups 1–2):
    Anchor 1 — Team tech-stack ratification:
    [2025-02-10, Group 2] Mingzhi Li: “. . . The report’s conclusion leans towards choosing Java/Spring Boot as the backend technology stack. . . ”
    Anchor 2 — Open-source candidates:
    [2025-01-16, Group 2] Mingzhi Li: “. . . We’ve researched a few open-source data lineage tools, such as Marquez and Amundsen. . . ”
    ▶ Profile (Jie Gu — Skills): Java (strong); Spring Boot (medium); MySQL (medium); Kubernetes (low); no Python skill listed


                                                 Figure 20: Skill example in Profile Understanding.
    Role

    ▶ Question:
    [User Request]
    I (Yutong Song) heard that the team recently had a successful practice in ensuring data accuracy, which resolved the issue of inaccurate data on the
    large screen dashboards. My manager wants me to summarize this case and propose some subsequent systematic improvement suggestions. Please
    help me prepare a response.
    [Options]
    A. . . . the root cause is a performance bottleneck in the real-time calculation of “Integrated Energy Efficiency Ratio”. . . design a set of dedicated
        performance test cases. . . output a detailed performance test report. . .
    B. . . . the root cause is a performance bottleneck . . . optimize the SQL. . . introducing a caching layer like Redis. . . add monitoring and alerts for
        the API query’s response time. . .
    C. . . . identified and solved through cross-validation. . . 1. Sort out the complete data pipeline. . . 2. Add automated data verification scripts. . .
        3. Optimize relevant API designs from a system architecture perspective. . .
    D. . . . Xinmeng Tian and Jiahui Zhao efficiently solved the problem through cross-validation. . . 1. Formalize . . . into a set of standard test cases. . .
        2. Add. . . to the regression test suite. . . 3. . . . updating the test process documentation. . .
    ▶ Correct Answer:
    C. Correctly identifies the cross-validation incident and frames recommendations from a developer’s perspective (data-pipeline review, API
    optimization)—actions within Yutong Song’s competence as a frontend/full-stack engineer.
    ▶ Typical Wrong Answer:
    D (nearly all configurations). Same correct incident, but framed from a QA perspective (test cases, regression suites, test documentation)—
    responsibilities of the QA engineer who executed the cross-validation, not of Yutong Song.
    ▶ Evidence (Full context:2025-04 to 2025-10, Groups 1–2):
    Anchor — The cross-validation incident:
    [2025-10-24, Group 2] Xinmeng Tian: “@Jiahui Zhao Cross-validation complete, data fully matched! The accuracy of all charts and KPI data on
    the large screen has been verified.”
    ▶ Profile (Yutong Song — Title): Frontend / Full-stack Developer

                                                 Figure 21: Role example in Profile Understanding.
Conference acronym ’XX, June 03–05, 2018, Woodstock, NY   Hu et al.
