                                                     Remember Me, Refine Me: A Dynamic Procedural Memory
                                                        Framework for Experience-Driven Agent Evolution
                                                               Zouying Cao1,3, * , Jiaji Deng2 , Li Yu2 , Weikang Zhou2 ,
                                                                      Zhaoyang Liu2,† , Bolin Ding2 , Hai Zhao1,3,†
                                                     1
                                                       AGI Institute, School of Computer Science, Shanghai Jiao Tong University,
                                                                              2
                                                                                Tongyi Lab, Alibaba Group,
                                                   3
                                                     Key Laboratory of Shanghai Education Commission for Intelligent Interaction
                                                              and Cognitive Engineering, Shanghai Jiao Tong University
                                                     zouyingcao@sjtu.edu.cn, {dengjiaji.djj, jinli.yl, zhouweikang.zwk,
                                                       jingmu.lzy, bolin.ding}@alibaba-inc.com, zhaohai@cs.sjtu.edu.cn




arXiv:2512.10696v2 [cs.AI] 15 Apr 2026
                                                                Abstract                               dynamic tasks through iterative reasoning and tool
                                                                                                       use (Tao et al., 2024; Gao et al., 2025; Fang et al.,
                                             Procedural memory enables large language
                                                                                                       2025). To facilitate continuous improvement with-
                                             model (LLM) agents to internalize “how-to”
                                             knowledge and thus reduce redundant trial-and-            out model retraining, procedural memory, which
                                             error. However, existing frameworks predom-               internalizes “how-to” knowledge from past interac-
                                             inantly suffer from a “passive accumulation”              tions, has emerged as a critical substrate for agent
                                             paradigm, treating memory as a static append-             evolution (Zhang et al., 2025b; Xu et al., 2025).
                                             only archive. To bridge the gap between static            By accumulating high-quality problem-solving ex-
                                             storage and dynamic reasoning, we propose                 periences, agents can leverage prior successes and
                                             ReMe (Remember Me, Refine Me), a compre-
                                                                                                       lessons to navigate novel scenarios, theoretically re-
                                             hensive framework for experience-driven agent
                                             evolution. ReMe manages the memory lifecy-                ducing redundant trial-and-error and avoiding local
                                             cle via three mechanisms: 1) multi-faceted dis-           optima (Wang and Chen, 2025; Chen et al., 2025).
                                             tillation, which extracts fine-grained experi-            Figure 1 contrasts how an agent completes one
                                             ences by recognizing success patterns, analyz-            stock trading task with and without experiences.
                                             ing failure triggers and generating comparative              To bridge the gap between static storage and
                                             insights; 2) context-adaptive reuse, which tai-           dynamic reasoning, an ideal procedural memory
                                             lors historical insights to new contexts through          system must function not merely as a database, but
                                             scenario-aware indexing; and 3) utility-based
                                                                                                       as an evolving cognitive substrate satisfying three
                                             refinement, which automatically adds validated
                                             memories and prunes outdated ones to maintain             core criteria: 1) High-quality Extraction: The sys-
                                             a compact, high-quality experience pool. Ex-              tem should distill generalized, reusable knowledge
                                             periments on BFCL-V3 and AppWorld demon-                  from noisy execution trajectories, rather than raw,
                                             strate that ReMe establishes a new state-of-the-          problem-specific observations. 2) Task-grounded
                                             art in agent memory system. Crucially, we                 Utilization: Retrieved memories should be dynam-
                                             observe a significant memory-scaling effect:              ically adapted to the specific requirements of the
                                             Qwen3-8B equipped with ReMe outperforms
                                                                                                       current task, maximizing their utility in novel sce-
                                             larger, memoryless Qwen3-14B, indicating that
                                             self-evolving memory provides a computation-              narios. 3) Progressive Optimization: The memory
                                             efficient path for lifelong learning.1                    pool should maintain its vitality through continu-
                                                                                                       ous updates, autonomously reinforcing effective
                                         1   Introduction                                              entries while removing outdated ones to prevent
                                                                                                       degradation over time.
                                         The transition from static language models to au-
                                                                                                          However, current frameworks often fall short
                                         tonomous agents marks a pivotal shift in artificial
                                                                                                       of these criteria, largely constrained by a “passive
                                         intelligence, enabling systems to handle complex,
                                                                                                       accumulation” paradigm. Prevailing approaches
                                             * This work was done during Zouying Cao’s internship at
                                                                                                       typically treat memory as inert, static storage, built
                                         Tongyi Lab, Alibaba Group.
                                             †
                                               Corresponding authors. This research was supported by   on either raw trajectories as experiences (Zheng
                                         the Shanghai Jiao Tong University 2030 Initiative and The     et al., 2024; Hu et al., 2024) or summarized work-
                                         Major Program of Chinese National Foundation of Social Sci-   flows corresponding to entire trajectories (Tang
                                         ences under Grant ‘The Challenge and Governance of Smart
                                         Media on News Authenticity’ [No. 23&ZD213].                   et al., 2025; Liu et al., 2025b). This introduces sev-
                                             1
                                               https://github.com/agentscope-ai/ReMe                   eral fundamental limitations. First, coarse-grained
                                          Past Trajectory                                                                                Experience
 Turn 1:
   User: I'm reviewing my account, and I'd like you to confirm the current balance and provide ...                   when to use: When a user wants to place an order
                                                                                                                     for a stock but specifies 'current market price'
  Assistant: [get_account_info()] … …
                                                                                                                     without providing a specific price.
 Turn 2:
   User: Subsequently, initiate a purchase order for 150 shares of TSLA at the prevailing market price ...           content: The assistant demonstrated a methodical
  Assistant: [get_stock_info(symbol='TSLA’)]                                                                         approach by first retrieving the current stock price
  Tool: {'price': 667.92, 'percent_change': -0.12, 'volume': 1.654, … }                                              using get_stock_info before placing an order.
  Assistant: place_order(order_type='Buy', symbol='TSLA', amount=150, price=250.0)]                                  This ensured that the user's request was
 Turn 3: … …                                                                                                         executed with precise, real-time data … ...


                                                                           LLM Agents
                                w/o experience                                                                         w/ experience
  Turn 1:                                                                                Turn 1:
    User: I know the stock market updates its status at different points ...               User: I know the stock market updates ...➕ Related Experience
    Assistant: [get_current_time()] … ...                                                Turn 2:
  Turn 2:                                                                                  User: ... 100 shares of the company with symbol AAPL at the prevailing price …
    User: I'm on the lookout for a stock ... 100 shares of the company with               Assistant: [get_stock_info(symbol='AAPL')]
  symbol AAPL at the prevailing market price? …                                           Tool: {'price': 227.16 , 'percent_change': 0.17, 'volume': 2.552, … }
    Assistant: [place_order(order_type='Buy',symbol='AAPL',price=190.50, … )] …           Assistant: [place_order(order_type='Buy',symbol='AAPL',price=227.16,…)] …
  Turn 3:                                                                                Turn 3:
    User: Once you've set up the order, …                   The price of AAPL              User: Once you've set up the order, …
    …                                                       is fabricated!                  …
  Turn N:                                                                                Turn N:
    User: I‘ve decided to back off from this particular order …                            User: I‘ve decided to back off from this particular order …



         Figure 1: Example of how agents complete one stock trading task with and without past experience.


trajectory-level experiences may introduce irrele-                                           Through extensive experiments on BFCL-V3
vant information that can prevent the agent from                                          and AppWorld benchmarks, ReMe achieves state-
grasping the core logic. Second, fetched experi-                                          of-the-art performance, demonstrating its effective-
ences are applied without adaptation, leading to                                          ness for memory-augmented agents. Most notably,
failures in slightly shifted scenarios. Crucially, lack                                   results reveal that memory quality can substitute
of timely update strategies causes the experience                                         for model scale: ReMe enables Qwen3-8B to outper-
pool to degrade into a mixture of valid insights and                                      form larger Qwen3-14B (without memory), achiev-
toxic noise (Xiong et al., 2025).                                                         ing average gains of 8.83% in Avg@4 and 7.29%
   To address these challenges, we propose ReMe                                           in Pass@4. These findings suggest that a self-
(Remember Me, Refine Me), a dynamic procedu-                                              evolving memory mechanism paves the way for
ral memory framework that shifts the paradigm                                             resource-efficient lifelong learning in LLM agents.
from passive storage to feedback-driven evolution.                                           In summary, our contributions are as follows:
We introduce coordinated innovations across the                                            • We propose ReMe, a comprehensive framework
memory lifecycle to meet the criteria of an ideal                                            for agent evolution that integrates multi-faceted
system. First, ReMe employs a multi-faceted distil-                                          experience distillation, context-adaptive reuse,
lation strategy for high-quality extraction. Through                                         and utility-based refinement. This achieves the
success pattern recognition, failure analysis and                                            closed loop of procedural memory, resolving the
comparative insight generation, the system distills                                          “passive accumulation” dilemma by enabling
key steps from past execution trajectories into struc-                                       agents to autonomously distill, adapt, and main-
tured, reusable experiences. Second, we design a                                             tain high-quality reasoning patterns.
comprehensive reuse pipeline for task-grounded
                                                                                           • We release reme.library, a fine-grained proce-
utilization. ReMe employs usage scenario index-
                                                                                             dural memory dataset constructed from diverse
ing strategy for retrieval, supplemented by rerank-
                                                                                             agentic tasks, with structured success patterns
ing and adaptive rewriting, aligning historical in-
                                                                                             and failure lessons to serve as a valuable com-
sights with the specific constraints of new tasks.
                                                                                             munity resource for studying procedure memory
Finally, ReMe implements a utility-based refine-
                                                                                             and optimizing memory-augmented agents.
ment mechanism for progressive optimization. The
memory pool grows as new successful trajectories                                           • Extensive experiments show that ReMe signif-
contribute reliable experiences and failure attempts                                         icantly enhances agent performance across di-
trigger self-reflection to explore viable solutions                                          verse benchmarks. Crucially, we demonstrate
for potential insights. Concurrently, our framework                                          a memory-scaling effect, where smaller mod-
tracks the utility of each experience during reuse,                                          els equipped with ReMe surpass larger baselines,
periodically pruning low-utility entries to maintain                                         validating our framework as a computationally
a compact and highly effective memory state.                                                 efficient pathway for lifelong agent learning.
2   Related Works                                      relevant knowledge in new tasks. These methods
                                                       neglect strategic experience removal mechanism,
Memory-enhanced LLM Agents. LLM-based                  since harmful experiences inevitably exist even
agents excel at handling complex tasks and in-         with human validation and initial helpful ones can
teractions, fueling their integration into diverse     also degrade over time (Xiong et al., 2025).
fields, such as finance (Ding et al., 2024), edu-
cation (Wang et al., 2024) and personalized as-        3     Methodology
sistant applications (Abbasian et al., 2023). Con-
temporary LLM agents employ memory systems             3.1    Overview of ReMe
that store explored information and reuse these ex-    Our framework, ReMe, as illustrated in Figure 2,
periences, to enhance their reasoning capabilities     operates through three interconnected phases: ex-
and training efficiency (Mei et al., 2025). In gen-    perience acquisition, reuse, and refinement. In the
eral, memory-enhanced agents often leverage two        experience acquisition phase, a summarizer ana-
forms of memory: parametric memory and non-            lyzes agent generated trajectories (both successful
parametric memory (Zhang et al., 2024). Paramet-       and failed) and distills actionable knowledge into
ric memory refers to encoding long-term knowl-         a structured experience pool. During experience
edge within model weights, while non-parametric        reuse, given a novel task, a retriever recalls rele-
memory utilizes external resources like knowledge      vant experiences from the experience pool. These
bases and databases to enrich task contexts without    experiences then augment the agent’s context, en-
modifying model parameters. WKM (Qiao et al.,          hancing their reasoning and task-solving perfor-
2024) incorporates a parametric world-knowledge        mance. Finally, the experience refinement phase
model to facilitate agent planning. AWM (Wang          continuously optimizes the experience pool by in-
et al., 2025) enables agents to automatically induce   corporating new solid experiences and discarding
and use task workflows from past experiences, im-      outdated ones, ensuring long-term relevance and
proving their performance on web navigation tasks.     adaptability to shifting task demands.
MARK (Ganguli et al., 2025) constructs user pref-
erence memory to deliver personalized responses        3.2    Experience Acquisition
in conversational AI systems.                          We begin by defining agentic experiences E as
Experience Learning Strategies. Recent studies         structured, generalizable representations of agent
show LLMs can improve their decision-making            execution insights. Each individual experience
abilities through gathering experiences and recall-    E ∈ E is denoted as E = ⟨ω, e, κ, c, τ ⟩, where
ing relevant knowledge (Zhao et al., 2024; Tan         ω states the scenario when to use the experience,
et al., 2025). The core of experience learning in-     e represents the core experience content, κ =
volves extracting usable information to selectively    {κ1 , κ2 , ..., κm } is a set of relevant keywords for
update the experience pool and retrieving effective    categorization, c ∈ [0, 1] quantifies the confidence
experiences to help generate responses. Early ap-      score, and τ enumerates the tools utilized.
proaches, such as Synapse (Zheng et al., 2024) and        To construct the initial experience pool, the ex-
HiAgent (Hu et al., 2024), store complete trajec-      ecution agent LLMexecute interacts with the envi-
tories as experiences for retrieval. However, col-     ronment over time and across the training tasks,
lecting raw and long interaction histories is hard     incrementally accumulating informative trajecto-
to manage, and the lack of abstraction limits task     ries. For each task query q, we sample trajectories
generalization. Current works (Wang et al., 2025;      N times aiming to capture diverse execution paths
Chen et al., 2025) focus on summarizing structured     and thereby increase the likelihood of obtaining
knowledge from prior trajectories and implement-       valuable success/failure pairs for comparisons dur-
ing a context-aware retrieval system to reuse ex-      ing experience acquisition.
periences for task guidance. For instance, Agent          After collecting a set of exploration trajectories,
KB (Tang et al., 2025) captures generalizable expe-    a summarizer LLMsumm is instructed to transform
rience units and introduces a teacher-student dual-    them into structured, reusable experiences through
phase retrieval mechanism that enables complex         three complementary analyses: First, the summa-
agentic problem solving. CER (Liu et al., 2025b)       rizer engages in success pattern recognition, identi-
distills fine-grained skills and environment dynam-    fying effective strategies and distilling the underly-
ics, allowing agents to augment themselves with        ing principles from succeeded trajectories. Concur-
                   Experience Acquisition                                                    Experience Reuse

                                                                                                                 Task Query
                        Prior Tasks                  AI Agents                                Indexing
                                                                                              Strategies          LLM-generated Field
     Trajectory
                                                                                                                  (e.g., when to use)
     Collection
                                             Execution
                                            Trajectories                    Recall              Retrieval
                                                                                               Frequency
                                                                                                               Task / Turn / Step Level


     Extraction       Trajectory-level            Keypoint-level
     Granularity
                                                                                                                      +
     Extraction       From Success
                                              From                        Rerank        Rewrite             Experience-driven Inference
     Strategies        From Failure        comparison



                          LLM As              Score
                                                                   ReMe
     Validation                                                                           Experience Refinement
                        Evaluator          Validation

                                                                             Selective Addition

    Deduplication          Similarity-based Filtering
                                                                                Failure-aware
                                                                                  Reflection

                        Task Experience
     task query     generalized query     experience content              Experience Record                     Utility-based Deletion
                                                                            freq += 1                            freq >= α &&
     query keywords      when to use      score       tool used             if task success: utility += 1        utility / freq < β




Figure 2: The ReMe framework comprises three alternating phases: build an experience pool from the agent’s past
trajectories, recall and adapt relevant experiences for new tasks, then refine the pool by selectively adding new
insights and removing outdated ones after each task execution.


rently, LLMsumm conducts failure analysis, scru-                         All retained experiences are indexed by the em-
tinizing unsuccessful attempts to derive valuable                     bedding vector of usage scenario ω and then stored
lessons. These preventive insights discuss common                     in a vector database, which we refer to as the expe-
pitfalls, ineffective approaches, and critical errors                 rience pool. The multi-faceted experience pool es-
that can be used to avoid repeating them in future                    tablishes a foundation for efficient retrieval and ap-
tasks. Additionally, LLMsumm performs compara-                        plication of relevant knowledge in future problem-
tive analysis by jointly examining successful and                     solving scenarios, promoting the agent evolution
failed trajectories, identifying critical differences                 from trial-and-error to strategic reasoning.
that distinguish effective from ineffective attempts.
                                                                      3.3      Experience Reuse
   Following the summarization, a validation step
leveraging LLM-as-a-Judge (Zheng et al., 2023) is                     Equipped with the experience pool, we can retrieve
further applied to assess whether the extracted ex-                   top-K relevant experiences based on task similar-
periences are actionable, accurate, and valuable for                  ity, which serve as a candidate set of in-context
future agent executions. The designed prompt tem-                     learning demonstrations to guide LLMexecute . To
plate is presented in Appendix Table 13. Moreover,                    be specific, the retriever utilizes advanced embed-
to keep the experience pool compact, validated ex-                    ding models (e.g., Qwen3-Embedding (Zhang et al.,
periences undergo similarity-based deduplication.                     2025a)) to encode the current task query and com-
Specifically, each new experience is encoded into                     putes cosine similarity scores to rank prior expe-
a vector embedding and compared against exist-                        riences. More retrieval details can be found in
ing ones via cosine similarity, and any candidate                     Appendix B.4.2. Upon fetching the top-K ex-
exceeding a predefined similarity threshold is dis-                   periences, we optionally employ a context-aware
carded as redundant. This helps maintain the effi-                    reranker LLMrerank to further refine the selection.
ciency of the subsequent experience reuse phase                       This involves a nuanced evaluation of experience
and preserve the diversity of retrieved experiences.                  relevance in light of the current task’s specific con-
text, constraints, and objectives, thus ensuring the    aware reflection mechanism that encourages agents
most pertinent experiences are brought to the fore-     to explore alternative strategies when encounter-
front. Table 14 shows the prompt template.              ing new task failures. Specifically, LLMsumm an-
   To better adapt the experiences to new task re-      alyzes this unsuccessful attempt, extracts key in-
quirements, we introduce the rewriting module to        sights about potential areas for improvement, and
reorganize the original context (containing multi-      then LLMexecute starts a new trial based on these
ple experiences) into a cohesive, task-specific guid-   lessons. When such trial succeeds, the correspond-
ance that is more directly applicable. See Table 15     ing lessons are incorporated into memory; other-
for the example prompt. Since past experiences          wise, they are discarded without cluttering the ex-
may not always perfectly align with new situations,     perience pool. To avoid falling into an endless loop
this intelligent adaptation mechanism not only in-      caused by inherent model limitations, we limit the
creases the immediate utility of the retrieved expe-    maximum number of self-reflections to 3.
riences but also empowers the agent to make more           Second, to prevent the accumulation of outdated
flexible and context-aware decisions.                   or ineffective experiences, we employ a utility-
   The experience reuse phase extends beyond            based deletion strategy that removes any experi-
mere experience retrieval, acting as a cognitive        ence whose average utility across all its past recalls
bridge that dynamically connects past knowledge         falls below a predefined threshold β. Specifically,
with present challenges. By combining retrieval,        ReMe continuously records the status of existing
reranking and rewriting, it not only leverages prior    experiences, including the total retrievals f and the
wisdom but also encourages novel thinking when          historical utility u which increments by 1 each time
past experiences fall short, thereby achieving a bal-   its recall contributes to a successful task comple-
ance between exploitation and exploration.              tion. An experience E ∈ E is considered to be
                                                        removed when it is frequently retrieved yet fails to
3.4   Experience Refinement                             improve new task performance:
However, a static experience pool cannot adapt                             ( h u(E)      i
to shifts in task distributions or improvements in                           1 f (E) ≤ β , if f (E) ≥ α,
                                                         ϕremove (E) =
model capability, making retrieved experiences in-                           0,               otherwise.
creasingly irrelevant. To address this, we introduce                                                       (1)
an experience refinement mechanism that dynam-          Note that we only consider an experience for re-
ically updates the experience pool via selective        moval after it has been retrieved at least α times.
addition and utility-based deletion.                       By integrating these components, ReMe facili-
   First, we carefully compare two distinct strate-     tates a self-evolving experience pool that retains
gies for adding new experiences to the pool: 1) full    high-quality experiences capable of shaping long-
addition, which incorporates experiences summa-         term agent behavior while adapting to new task
rized from all new trajectories regardless of out-      demands.
come; 2) selective addition, where only trajectories
that lead to success are distilled into experiences     4     Experiments
and stored. The empirical evidence indicates that       4.1    Experimental Settings
full addition often underperforms selective addi-
                                                        Datasets. We conduct experiments on two tool-
tion, which may be attributed to the quality of
                                                        augmented benchmarks: BFCL-V3 (Patil et al.,
failure-based experiences. During initial experi-
                                                        2025), AppWorld (Trivedi et al., 2024). For BFCL-
ence pool construction, multiple failed trajectories
                                                        V3, we randomly select 50 tasks from the base
can be collectively analyzed to extract meaningful
                                                        multi-turn category to construct the initial experi-
insights. However, in real-time task execution, a
                                                        ence pool since the default dataset does not provide
single failed trajectory often provides insufficient
                                                        training split. The remaining 150 tasks serve as the
context for accurate failure analysis, potentially
                                                        evaluation set. For AppWorld, we use 90 training
leading to misguided experiences. In contrast, suc-
                                                        tasks for the initial experience acquisition stage and
cessful trajectories consistently yield more reliable
                                                        evaluate agents on 168 test-normal tasks. Detailed
and actionable insights, thereby making selective
                                                        information of the datasets are in Appendix B.1.
addition effective.
   Additionally, we recognize the potential value       Metrics. We report both Avg@4 and Pass@4
of learning from failures and introduce a failure-      results: the average task success rate across four
                                           BFCL-V3                    AppWorld                    Avg
  Model          Methods
                                       Avg@4    Pass@4             Avg@4   Pass@4            Avg@4 Pass@4
                 No Memory           40.33±0.94    59.55±0.83     14.97±0.24   32.85±2.11     27.65      46.20
                 A-Mem               41.22±0.61    62.00±2.37     12.95±0.37   29.76±2.80     27.09      45.88
  Qwen3-8B       LangMem             44.11±0.28    65.55±1.13     11.46±0.53   26.79±0.84     27.79      46.17
                 ReMe (fixed)        44.50±0.85    65.77±0.63     17.06±0.25   36.31±1.29     30.78      51.04
                 ReMe (dynamic)      45.17±0.36    68.00±0.55     24.70±1.04   42.06±0.74     34.94      55.03
                 No Memory           48.66±1.51    68.22±0.63     22.57±0.19   41.07±0.84     35.62      54.65
                 A-Mem               47.44±0.44    69.77±0.63     18.95±0.31   37.70±0.57     33.20      53.74
  Qwen3-14B      LangMem             49.17±0.33    71.33±1.33     21.88±1.37   41.67±1.68     35.53      56.50
                 ReMe (fixed)        51.89±0.34    72.44±0.63     25.35±0.91   46.82±0.74     38.62      59.63
                 ReMe (dynamic)      55.00±0.72    74.44±0.83     34.32±0.81   52.98±1.29     44.66      63.71
                 No Memory           54.55±0.63    72.44±0.83     27.23±0.92   50.59±1.68     40.89      61.52
                 A-Mem               54.50±1.09    72.66±0.54     28.13±0.75   51.19±0.97     41.32      61.93
  Qwen3-32B      LangMem             52.27±1.13    72.22±1.91     24.55±0.57   47.02±1.56     38.41      59.62
                 ReMe (fixed)        56.05±1.26    74.89±0.63     31.50±0.67   58.13±1.40     43.78      66.51
                 ReMe (dynamic)      56.17±0.24    76.44±1.13     42.02±0.51   63.49±0.28     49.10      69.97

Table 1: Performance comparison (%) between ReMe and the baselines on BFCL-V3, AppWorld benchmarks. Bold
indicate the best results of each model. All results are computed as the average over three independent runs, with
the superscript showing the standard deviation.


independent trials, and the probability that at least      employ text-embedding-v4 2 with its default em-
one out of four independent task trials is successful.     bedding dimension of 1024. The prompts used in
Unless otherwise specified, all results are averaged       this phase and more details can be found in Ap-
over three independent runs and reported as mean           pendix B.4.1. In the experience reuse phase, we
with standard deviation.                                   use top-K=5, retrieving the five most relevant expe-
                                                           riences for each task. The configuration difference
Baselines. To evaluate the effectiveness of ReMe,          between ReMe (fixed) and ReMe (dynamic) lies
we compare it against three baselines: (1) No Mem-         in whether the experience pool is dynamically up-
ory, and two popular baseline memory systems (2)           dated during agent execution. In the experience re-
A-Mem (Xu et al., 2025), an agentic memory sys-            finement phase, utility-based deletion is controlled
tem that enables LLM agents to dynamically orga-           by the retrieval threshold α=5 and the utility thresh-
nize their memories for future action guidance, and        old β=0.5, where the threshold selection follows
(3) LangMem (LangChain, 2025), LangChain’s                 the prior work (Xiong et al., 2025). Selecting 3
long-term memory module that provides tooling to           for the maximum number of self-reflections is also
extract important information from previous con-           proper since the agent’s performance immediately
versations and optimize agent behavior through             improves between the first two trials (Shinn et al.,
prompt refinement. For fair comparison, all meth-          2023). Additionally, the maximum number of it-
ods perform experience retrieval only once at the          erations is limited to 30, after which the agent ter-
beginning of each task. Additionally, the mem-             minates regardless of task success or failure. To
ory addition operation for these systems is trig-          ensure fair comparison, we maintain these settings
gered only upon the collection of successful tra-          consistently across all experiments unless other-
jectories. Further implementation details of the           wise specified for ablation studies.
baseline methods are provided in Appendix B.2.
                                                           4.2    Main Results
Implementation Details. We use the Qwen3 se-
ries instruct models (Team, 2025b) as LLMexecute           Table 1 presents the main results of ReMe across
and set LLMsumm = LLMexecute for experience-               Qwen3 family models on BFCL-V3 and AppWorld
driven self-evolution. In the experience acquisi-          benchmarks. Overall, ReMe achieves the highest av-
tion phase, we set N =8 and temperature=0.9 for               2
                                                              https://bailian.console.aliyun.com/?tab=model#/model-
trajectory sampling. For experience indexing, we           market/detail/text-embedding-v4
                                     BFCL-V3
                                                                           Full   Selective                       BFCL-V3
         GPT-4.1                                    No Memory Baseline                      Reflection Deletion
         o4-mini                                    + ReMe (fixed)       Addition Addition                      Avg@4 Pass@4
                                                    + ReMe (dynamic)
     Qwen3-Max
Kimi-K2-Thinking                                                               ✓        –            –          –     40.83%    62.00%
 DeepSeek-V3.2                                                                 –        ✓            –          –     44.33%    64.66%
        GLM-4.7                                                                –        ✓            ✓          –     45.00%    64.66%
                40    45   50   55      60     65    70      75     80         –        ✓            ✓          ✓     45.17%    68.00%
                                     Avg@4 (%)

Figure 3: Performance improvements (%) for multiple                      Table 3: Ablation on key components. We compare the
LLMs enhanced with ReMe.                                                 full addition and selective addition and assess the impact
                                                                         of failure-aware reflection and utility-based deletion. A
                                                                         checkmark (✓) indicates the component is used.
                         Qwen3-8B           Qwen3-14B
 Granularity
                     Avg@4(%) Pass@4(%) Avg@4(%) Pass@4(%)
 Trajectory-level 43.00+2.67 60.00+0.45 49.66+1.00 69.33+1.11                                                          BFCL-V3
                                                                           Qwen3-8B         Rerank       Rrewrite
 Keypoint-level 44.50+4.17 65.77+6.22 51.89+4.23 72.44+4.22                                                         Avg@4 Pass@4
                                                                          No Memory           –             –       24.41%     28.50%
Table 2: Ablation study on extraction granularity levels
                                                                                              –             –       27.17%   34.66%
in the experience acquisition stage. The experimental                                         ✓             –       28.91%   36.67%
setting is ReMe (fixed), with subscript showing the                            +ReMe
                                                                                              –             ✓       28.67%   37.33%
performance gap compared with No Memory baseline.                                             ✓             ✓       29.00%   40.67%

                                                                         Table 4: Ablation on the reranking and rewriting module.
erage task success rate across three model sizes,                        A checkmark (✓) indicates the component is used.
consistently outperforming No Memory baseline
and competitive baseline memory systems. Specifi-
cally, Qwen3-8B with ReMe surpasses the No Mem-                          deviation in performance across runs, particularly
ory baseline by an improvement of 7.29% Pass@4                           for larger models. This suggests that ReMe not only
and 8.83% Avg@4 on average. The gains observed                           improves overall performance but also enhances
in Pass@4 indicate that retrieved experiences are ef-                    the robustness and reliability of model outputs.
fective at broadening the exploration space, increas-                       To demonstrate the generalizability of ReMe
ing the likelihood of finding at least one successful                    across different backbones, we evaluate on six ad-
solution among multiple attempts. Besides, the                           ditional LLMs as shown in Figure 3. ReMe delivers
performance stability of our ReMe is particularly ev-                    consistent gains in Avg@4 across all models, with
ident when compared to the baseline methods. For                         the dynamic variant yielding further improvements.
instance, while LangMem performs well on BFCL-                           4.3       Ablation Studies
V3, its performance drops significantly on App-
World, especially for smaller models. Instead, ReMe                      Granularity Ablations. We compare two granu-
(dynamic) shows remarkable consistency across                            larity levels for experience acquisition: trajectory-
both BFCL-V3 and AppWorld benchmarks.                                    level and keypoint-level. In Appendix C, we
                                                                         present two experience examples illustrating the
   Notably, smaller models equipped with ReMe can
                                                                         structural and content differences between these
be comparable to, or even surpass, larger models
                                                                         granularity settings. As shown in Table 2, although
without memory. For example, the average Pass@4
                                                                         the incorporation of trajectory-level experiences
score for Qwen3-8B + ReMe (dynamic) exceeds
                                                                         exhibits minor progress over No Memory base-
that of vanilla Qwen3-14B (55.03% vs. 54.65%).
                                                                         line, the performance gains brought by keypoint-
Similarly, Qwen3-14B + ReMe (dynamic) exceeds
                                                                         level experiences are substantially higher. This
the overall performance of Qwen3-32B without
                                                                         underscores that summarizing experiences at a fine-
memory (Avg@4: 44.66% vs. 40.89%; Pass@4:
                                                                         grained level enables more effective knowledge
63.71% vs. 61.52%). This underscores that an
                                                                         transfer, leading to superior agent performance
effective memory mechanism can significantly nar-
                                                                         across different tasks and model scales.
row the performance gap across model scales.
   Moreover, ReMe (dynamic) consistently outper-                         Component Ablations. Taking Qwen3-8B as an
forms ReMe (fixed) across all model sizes and                            example, Table 3 presents an ablation study on key
benchmarks. This underscores the importance of                           components of our ReMe framework. Firstly, replac-
adaptive experience refinement during task execu-                        ing full addition with selective addition leads to
tion. In addition, ReMe tends to reduce the standard                     substantial performance improvements, with gains
                                task query                           query keywords                                                             Model: Qwen3-8B Dataset: BFCL-V3
                                generalized query                    usage scenario                                                                              65.77 65.33                  65.33
                                                                                                                               66                                            64.66 64.66
            57                                                  75                                                                              64.0        64.0                         64.0
                                                                                                                               64         63.33       63.33
            54                                                  72

Avg@4 (%)                                          Pass@4 (%)
            51                                                  69                                                             62
            48                                                                                                                 60 59.55




                                                                                                       Agent Performance (%)
                                                                66
            45                                                                                                                                                 Pass@4            Avg@4
                                                                63                                                             58
            42                                                                                                                 45                                       44.5
                         B        3-14B wen3-32B                             B        3-14B wen3-32B
                 Qwen3-8     Qwen      Q                             Qwen3-8     Qwen      Q
                                                                                                                                                                44.16          44.0 44.16 44.16 44.0
                                                                                                                               44                       43.5                                           43.66
                                                                                                                               43
  Figure 4: Ablation on retrieval keys. The experiments                                                                                         42.0
                                                                                                                               42
  are evaluated on BFCL-V3 in ReMe (fixed) setting.
                                                                                                                               41 40.33 40.33
                                                                                                                               40    0      1    2       3      4     5     6     7        8     9      10
                                                     BFCL-V3
      LLMexecute LLMsumm                                                                                                                             Number of Experience Retrieved
                                             Avg@4 (%)     Pass@4 (%)
                         Qwen3-8B        44.50                                    65.77                    Figure 5: Effect of retrieved experience number on agent
      Qwen3-8B           Qwen3-14B 46.33 △ = 1.83 ↑                         66.00 △ = 0.23 ↑
                                                                                                           performance (%) in ReMe (fixed) setting.
                         Qwen3-32B 47.83 △ = 3.33 ↑                         68.00 △ = 2.23 ↑


 Table 5: Performance of different LLMsumm capabili-                                                                                Model              Setting                 Latency (seconds)
 ties with fixed LLMexecute in ReMe (fixed) setting.                                                                                                   No Memory                      21.42
                                                                                                                                    Qwen3-8B
                                                                                                                                                       + ReMe                      23.96 +2.54

 of 3.50% Avg@4 and 2.66% Pass@4 on BFCL-
                                                                                                           Table 6: The average inference latency per task for ReMe
 V3. This highlights the importance of experience                                                          versus the No Memory baseline.
 quality over quantity in experience-driven agent
 evolution. Moreover, the introduction of the failure-
 aware reflection module enhances the average task                                                      tigate whether the agent gains more as LLMsumm
 success rate, demonstrating the value of learning                                                      capability increases, we scale the summarization
 from unsuccessful attempts. Notably, incorporating                                                     model from Qwen3-8B to Qwen3-32B with the
 the utility-based deletion yields further improve-                                                     fixed LLMexecute = Qwen3-8B. It can be observed
 ments, indicating that regularly discarding outdated                                                   from Table 5 that stronger summarization capabil-
 experiences is critical for agents to adapt to non-                                                    ity yields clear performance improvements in both
 stationary environments. Further, we supplement                                                        Avg@4 and Pass@4 metrics (Avg@4: +1.83% →
 the ablation studies on the reranking and rewriting                                                    +3.33%; Pass@4: +0.23% → +2.23%). These
 module. All tests use the Qwen3-8B model with                                                          findings emphasize the critical role of high-quality
 thinking mode disabled in ReMe(fixed) setting,                                                         experience summarization in overall agent perfor-
 with BFCL-V3 results summarized in Table 4.                                                            mance, highlighting the potential for further gains
                                                                                                        through advanced summarization techniques.
  Retrieval Key Ablations. Regarding the index-
  ing strategy, we explore four different retrieval keys                                                   Effect of Retrieved Experience Number. To
  to assess their impact on the performance of ReMe.                                                       evaluate the relationship between retrieved experi-
  From Figure 4, it can be seen that using the raw                                                         ence number and performance, we vary the value
  task description or their extracted keywords to in-                                                      K from 0 to 10. Figure 5 illustrates increasing the
  dex experiences underperforms the LLM-generated                                                          number of in-context experiences achieves steady
  fields (generalized query and usage scenario). The                                                       performance gains that rise and then saturate. Be-
  usage scenario indexing strategy, which likely cap-                                                      yond the saturation point, retrieving more may de-
  tures both the task context and potential application                                                    grade performance, primarily due to the higher
  areas, proves to be the most effective in retrieving                                                     chance of incorporating noisy experiences. This is
  relevant experiences from the database. For com-                                                         why we select K = 5 in the main experiments.
  prehensive results, please refer to Appendix D.3.
                                                                                                           Computational Overheads. To demonstrate
  4.4             More Analysis                                                                            ReMe offers a favorable trade-off between inference
  Agent Gains More with Stronger LLMsumm .                                                                 cost and performance enhancement, taking App-
  Our main experiments demonstrate an agent can                                                            world as an example, we report the average infer-
  learn effectively through experience-driven self-                                                        ence latency per task for ReMe versus the No Mem-
  evolution, i.e., LLMsumm =LLMexecute . To inves-                                                         ory baseline in Table 6. It can be seen that the com-
    Model: Qwen3-8B        22                                          Limitations
    Dataset: BFCL-V3                 19                    Baseline
                                          16               ReMe
                                14                                     This paper focuses on procedural memory manage-
                                               13 13
                                                                       ment for agent self-evolution. Despite its promis-
                                                                       ing performance, there are several limitations that
                                                       4       4
                                                           2       2   could be addressed in future work. First, ReMe
                                                                       currently employs a fixed retrieval strategy, where
                                                                       experiences are retrieved once at the beginning of
              (a)                              (b)                     each task. Implementing a more flexible, context-
                                                                       aware retrieval mechanism could potentially im-
Figure 6: Statistics of failed tasks with and without
                                                                       prove system performance, since dynamic experi-
ReMe. (a) Left: shows overlapping and unique failure
cases; (b) Right: displays the number of task failures
                                                                       ence incorporation promotes adaptive knowledge
across different error categories.                                     utilization. Secondly, although the existing ex-
                                                                       perience validation process effectively filters out
                                                                       low-quality experiences, relying primarily on an
putational cost of our ReMe is acceptable, which                       LLM-as-judge approach may overlook nuanced as-
will not limit its applicability in long-running or                    pects of experience quality and relevance. In the
resource-constrained settings.                                         future, we can explore more sophisticated valida-
                                                                       tion techniques for more precise experience eval-
Error Analysis. We conduct an analysis of the                          uation. Furthermore, a larger-scale summarizer
error patterns with and without ReMe for Qwen3-                        brings greater performance gains in agent reason-
8B on BFCL-V3. The Venn diagram (Figure 6a)                            ing, as shown in Section 4.4, which can be at-
reveals a reduction in the total number of failure                     tributed to its stronger summarization capability.
cases from 62 (No Memory Baseline) to 47 (ReMe).                       This indicates that designing advanced summariza-
Notably, ReMe corrects 17 baseline-specific errors                     tion strategies with small models can further boost
while introduces only 2 new ones. Further, we man-                     agent self-evolution.
ually review and categorize each failure case to ex-
amine the impact of ReMe on different error types
(Figure 6b). A substantial decrease in Reasoning                       References
Error (22 → 14) indicates ReMe effectively lever-                      Mahyar Abbasian, Iman Azimi, Amir M Rahmani, and
ages past experiences to strengthen its multi-step                      Ramesh Jain. 2023. Conversational health agents: A
reasoning capabilities, reducing propagation of ear-                    personalized llm-powered agent framework. arXiv
lier mistakes. ReMe also yields a moderate but                          preprint arXiv:2310.02374.
meaningful reduction in Action Omission errors,                        Silin Chen, Shaoxin Lin, Xiaodong Gu, Yuling Shi,
which helps the agent recognize missing steps in                          Heng Lian, Longfei Yun, Dong Chen, Weiguo Sun,
multi-turn tasks, especially those requiring sequen-                      Lin Cao, and Qianxiang Wang. 2025. Swe-exp:
tial tool interactions or state tracking.                                 Experience-driven software issue resolution. arXiv
                                                                          preprint arXiv:2507.23361.
5     Conclusion                                                       Han Ding, Yinheng Li, Junhao Wang, and Hang Chen.
                                                                         2024. Large language model agent in financial trad-
We introduce ReMe, a dynamic procedural memory                           ing: A survey. arXiv preprint arXiv:2408.06361.
framework that evolves agent reasoning from blind
                                                                       Jinyuan Fang, Yanwen Peng, Xi Zhang, Yingxu Wang,
trial-and-error to strategic experience reuse. By
                                                                          Xinhao Yi, Guibin Zhang, Yi Xu, Bin Wu, Siwei
distilling structured knowledge from prior trajec-                        Liu, Zihao Li, and 1 others. 2025. A comprehensive
tories at a fine-grained level, ReMe enables agents                       survey of self-evolving ai agents: A new paradigm
to leverage critical insights, thus avoiding poten-                       bridging foundation models and lifelong agentic sys-
tial experience interference in coarse-grained ap-                        tems. arXiv preprint arXiv:2508.07407.
proaches. Equipped with effective experience re-                       Anish Ganguli, Prabal Deb, and Debleena Banerjee.
finement, ReMe maintains a high-quality experience                       2025. Mark: Memory augmented refinement of
pool for agent evolution. Extensive experiments                          knowledge. arXiv preprint arXiv:2505.05177.
validate that ReMe significantly outperforms several                   Huan-ang Gao, Jiayi Geng, Wenyue Hua, Mengkang Hu,
baselines, with ablation studies highlighting the                        Xinzhe Juan, Hongzhang Liu, Shilong Liu, Jiahao
value of each core component in ReMe.                                    Qiu, Xuan Qi, Yiran Wu, and 1 others. 2025. A
  survey of self-evolving agents: On path to artificial   Xiangru Tang, Tianrui Qin, Tianhao Peng, Ziyang Zhou,
  super intelligence. arXiv preprint arXiv:2507.21046.      Daniel Shao, Tingting Du, Xinming Wei, Peng Xia,
                                                            Fang Wu, He Zhu, and 1 others. 2025. Agent kb:
Mengkang Hu, Tianxing Chen, Qiguang Chen, Yao Mu,           Leveraging cross-domain experience for agentic prob-
 Wenqi Shao, and Ping Luo. 2024. Hiagent: Hier-             lem solving. arXiv preprint arXiv:2507.06229.
  archical working memory management for solving
  long-horizon agent tasks with large language model.     Zhengwei Tao, Ting-En Lin, Xiancai Chen, Hangyu
  arXiv preprint arXiv:2408.09559.                          Li, Yuchuan Wu, Yongbin Li, Zhi Jin, Fei Huang,
                                                            Dacheng Tao, and Jingren Zhou. 2024. A survey
LangChain. 2025.      Langmem: Modular mem-                 on self-evolution of large language models. arXiv
  ory for agentic systems. https://github.com/              preprint arXiv:2404.14387.
  langchain-ai/langmem. Accessed: 2025-10-13.
                                                          Qwen Team. 2025a. Qwen3-max: Just scale it.
Aixin Liu, Aoxue Mei, Bangcai Lin, Bing Xue, Bingx-
  uan Wang, Bingzheng Xu, Bochao Wu, Bowei Zhang,
                                                          Qwen Team. 2025b. Qwen3 technical report. Preprint,
  Chaofan Lin, Chen Dong, and 1 others. 2025a.
                                                            arXiv:2505.09388.
  Deepseek-v3. 2: Pushing the frontier of open large
  language models. arXiv preprint arXiv:2512.02556.
                                                          Harsh Trivedi, Tushar Khot, Mareike Hartmann, Ruskin
Yitao Liu, Chenglei Si, Karthik R Narasimhan, and           Manku, Vinty Dong, Edward Li, Shashank Gupta,
  Shunyu Yao. 2025b. Contextual experience replay           Ashish Sabharwal, and Niranjan Balasubramanian.
  for self-improvement of language agents. In Proceed-      2024. Appworld: A controllable world of apps and
  ings of the 63rd Annual Meeting of the Association        people for benchmarking interactive coding agents.
  for Computational Linguistics (Volume 1: Long Pa-         In Proceedings of the 62nd Annual Meeting of the
  pers), pages 14179–14198.                                 Association for Computational Linguistics (Volume
                                                            1: Long Papers), pages 16022–16076.
Lingrui Mei, Jiayu Yao, Yuyao Ge, Yiwei Wang, Bao-
  long Bi, Yujun Cai, Jiazhi Liu, Mingyu Li, Zhong-Zhi    Shen Wang, Tianlong Xu, Hang Li, Chaoli Zhang,
  Li, Duzhen Zhang, and 1 others. 2025. A survey of         Joleen Liang, Jiliang Tang, Philip S Yu, and Qing-
  context engineering for large language models. arXiv      song Wen. 2024. Large language models for ed-
  preprint arXiv:2507.13334.                                ucation: A survey and outlook. arXiv preprint
                                                            arXiv:2403.18105.
MoonshotAI. 2025. Introducing kimi k2 thinking.
                                                          Yu Wang and Xi Chen. 2025. Mirix: Multi-agent mem-
OpenAI. 2025a. Introducing gpt-4.1 in the api.              ory system for llm-based agents. arXiv preprint
                                                            arXiv:2507.07957.
OpenAI. 2025b. Introducing openai o3 and o4-mini.
                                                          Zora Zhiruo Wang, Jiayuan Mao, Daniel Fried, and
Shishir G Patil, Huanzhi Mao, Fanjia Yan, Charlie
                                                            Graham Neubig. 2025. Agent workflow memory. In
  Cheng-Jie Ji, Vishnu Suresh, Ion Stoica, and Joseph E
                                                            Forty-second International Conference on Machine
  Gonzalez. 2025. The berkeley function calling leader-
                                                            Learning.
  board (bfcl): From tool use to agentic evaluation of
  large language models. In Forty-second International
                                                          Zidi Xiong, Yuping Lin, Wenya Xie, Pengfei He, Jil-
  Conference on Machine Learning.
                                                            iang Tang, Himabindu Lakkaraju, and Zhen Xiang.
Shuofei Qiao, Runnan Fang, Ningyu Zhang, Yuqi Zhu,          2025. How memory management impacts llm agents:
  Xiang Chen, Shumin Deng, Yong Jiang, Pengjun Xie,         An empirical study of experience-following behavior.
  Fei Huang, and Huajun Chen. 2024. Agent planning          arXiv preprint arXiv:2505.16067.
  with world knowledge model. Advances in Neural
  Information Processing Systems, 37:114843–114871.       Wujiang Xu, Kai Mei, Hang Gao, Juntao Tan, Zu-
                                                           jie Liang, and Yongfeng Zhang. 2025. A-mem:
Noah Shinn, Federico Cassano, Ashwin Gopinath,             Agentic memory for llm agents. arXiv preprint
  Karthik R Narasimhan, and Shunyu Yao. 2023. Re-          arXiv:2502.12110.
  flexion: language agents with verbal reinforcement
  learning. In Thirty-seventh Conference on Neural        Yanzhao Zhang, Mingxin Li, Dingkun Long, Xin Zhang,
  Information Processing Systems.                           Huan Lin, Baosong Yang, Pengjun Xie, An Yang,
                                                            Dayiheng Liu, Junyang Lin, Fei Huang, and Jingren
Zhen Tan, Jun Yan, I-Hung Hsu, Rujun Han, Zifeng            Zhou. 2025a. Qwen3 embedding: Advancing text
  Wang, Long Le, Yiwen Song, Yanfei Chen, Hamid             embedding and reranking through foundation models.
  Palangi, George Lee, Anand Rajan Iyer, Tianlong           arXiv preprint arXiv:2506.05176.
  Chen, Huan Liu, Chen-Yu Lee, and Tomas Pfister.
  2025. In prospect and retrospect: Reflective mem-       Zeyu Zhang, Quanyu Dai, Xiaohe Bo, Chen Ma, Rui Li,
  ory management for long-term personalized dialogue        Xu Chen, Jieming Zhu, Zhenhua Dong, and Ji-Rong
  agents. In Proceedings of the 63rd Annual Meet-           Wen. 2024. A survey on the memory mechanism of
  ing of the Association for Computational Linguistics      large language model based agents. ACM Transac-
  (Volume 1: Long Papers), pages 8416–8439.                 tions on Information Systems.
    Zeyu Zhang, Quanyu Dai, Xiaohe Bo, Chen Ma, Rui Li,
when toXuuse:   When
             Chen,      a user wants
                     Jieming           to place an
                                Zhu, Zhenhua        order and
                                                 Dong,     for Ji-Rong       task query: Access and retrieve the details of my
a stockWen.
         but without   providing  a on
                                     specific                                most recent order, as I've misplaced the ID but need
               2025b. A     survey       the price.
                                              memory mechanism of
experience content: The assistant demonstrated a                             the latest transaction.
        large language model-based agents. ACM Transac-
methodical approach by first retrieving the current                          query keywords: ["order retrieval", "ambiguous
stock price
        tionsusing  get_stock_info
               on Information         and then43(6):1–47.
                                   Systems,     using that                   requests", "efficiency", "user experience"]
price in the place_order function. This two-step                             generalized query: Retrieve recent order details
process
    Andrewensures  compliance
                Zhao,    Daniel with  the required
                                  Huang,      Quentin Xu, Matthieu           when order ID is unavailable.
parameters
        Lin, of the
              Yong-Jinplace_order
                            Liu, andfunction
                                        Gao while
                                              Huang.aligning
                                                        2024. Expel:         when to use: When users need order details without
with theLlmuser's intent
              agents   arefor a market-price-based
                            experiential              order.
                                           learners. In   Proceedings        explicit order IDs.
        of the AAAI Conference on Artificial Intelligence,                   experience content: The higher-scoring approach
                                                                             automatically retrieved and displayed the most recent
        volume 38, pages 19632–19642.                                        order details (ID 12446) after fetching the history,
                                                                             while the lower-scoring response only listed order IDs
when to    use: When
     Lianmin    Zheng, interacting
                          Wei-Linwith     APIs that
                                     Chiang,     Yingrequire
                                                       Sheng, Siyuan         without immediate detail retrieval. This demonstrates
preciseZhuang,
         authentication   parameters
                    Zhanghao      Wu,and    data extraction.
                                         Yonghao     Zhuang, Zi Lin,         efficiency in handling ambiguous user requests by
experience    content:
        Zhuohan     Li, The  higher-scoring
                         Dacheng      Li, Ericapproach
                                                 Xing, and 1 others.         combining history lookup with direct detail fetching.
prioritized
        2023.API Judging
                 specification  validation before
                             llm-as-a-judge         execution
                                                 with   mt-bench and
(e.g., confirming phone login requires phone number as
        chatbot   arena.   Advances      in neural
username), implemented robust error handling for
                                                     information   pro-
        cessingfailures,
authentication    systems,   36:46595–46623.
                           and used   precise data extraction             Figure 7: Different indexing examples for the same
techniques (search_notes with tags/query filters). The                    BFCL-V3 task experience.
lower-scoring   approach made
     Longtao Zheng,        Rundongrepeated
                                         Wang,authentication
                                                  Xinrun Wang, and
errors, Bo
         included  explanatory text
              An. 2024.       Synapse: in code blocks  causing
                                            Trajectory-as-exemplar
syntax failures,
        prompting and with
                       used memory
                             inefficient for
                                          string parsing that
                                               computer    control. In
retained   metadata  instead  of clean titles.                            In our experiments, a task is deemed successful
        The   Twelfth   International      Conference on Learning
        Representations.                                                  when the agent makes the necessary function calls
                                                                          correctly and yields the expected outputs.
    ZhipuAI. 2025. Glm-4.7: Advancing the coding capa-
      bility.                                                             AppWorld AppWorld (Trivedi et al., 2024) is a
                                                                          benchmark designed to evaluate function calling
    A     Use of AI Assistants                                            and interactive coding agents. It simulates a world
   During the writing process of this paper, we utilized                  of 9 day-to-day applications (e.g., email, Spotify,
   AI assistants for language refinement, including                       Venmo) through 457 APIs and is populated with the
   tasks such as grammar checking, sentence restruc-                      digital activities of approximately 100 simulated
   turing, and phrasing. All AI-suggested changes                         users. A key feature of AppWorld is its robust eval-
   were thoroughly reviewed and approved by the                           uation framework, which uses state-based unit tests
   authors to ensure the final content of this paper                      to assess task completion and provides two metrics
   represents the authors’ original ideas.                                to measure performance: 1) Task Goal Completion
                                                                          (TGC) measures percentage of tasks for which the
    B     Experimental Details                                            agent passes all evaluation tests; 2) Scenario Goal
                                                                          Completion (SGC) is the percentage of scenarios
    In this section, we detail our experimental setup, in-
                                                                          where the agent passes all the unit tests for all tasks
    cluding the benchmark datasets, evaluation metrics,
                                                                          from that scenario. In our experiments, we report
    and baseline methods compared. We also describe
                                                                          Task Goal Completion metric, which naturally re-
    the implementation details of ReMe crucial for re-
                                                                          flects task success rate.
    producing our results.

    B.1     Datasets and Evaluation Metrics                               B.2    Baseline Details

   BFCL-V3 Berkeley Function Calling Leader-                              LangMem LangMem (LangChain, 2025) is
   board V3 (BFCL-V3) (Patil et al., 2025) is a bench-                    Langchain’s long-term memory module that ex-
   mark which assesses the function calling and tool-                     tracts and stores key information from conversa-
   using capabilities of LLMs, particularly in multi-                     tions for future retrieval. It provides both functional
   turn and multi-step scenarios. It provides over                        primitives compatible with any storage system and
   1,800 test tasks that require models to generate                       native integration with LangGraph’s storage layer,
   precise API calls, handle various programming                          enabling agents to continuously improve. In our ex-
   languages (Python, Java, JavaScript), and manage                       periments, we adopt LangMem’s implementation
   complex interactions like parallel function calls.                     of episodic memory3 , which helps the agent learn
   The evaluation employs both Abstract Syntax Tree                       from experience.
   (AST) matching to check syntactic correctness and                         3
                                                                              https://langchain-ai.github.io/langmem/guides/extract_
   executable testing to verify functional outcomes.                      episodic_memories/
                                                                 Model              No Memory ReMe (fixed) ReMe (dynamic)
   when to use: When a user wants to place an order for
   a stock but without providing a specific price.               GPT-4.1              48.25%   53.33%+5.08%   54.67%+6.42%
   experience
   when   to use:content:
                   When aThe
                           userassistant
                                 wants todemonstrated  a for
                                           place an order
                                                                 o4-mini              54.67%   57.78%+3.11%   60.00%+5.33%
   methodical  approach   by first retrieving the
   a stock but without providing a specific price.current        Qwen3-Max            59.00%   61.83%+2.83%   64.00%+5.00%
   stock price using get_stock_info and then using that
   experience content: The assistant demonstrated a              Kimi-K2-Thinking     57.17%   62.17%+5.00%   66.00%+8.83%
   price in theapproach
   methodical    place_order  function.
                          by first      This two-step
                                   retrieving the current        DeepSeek-V3.2        53.06%   56.00%+2.94%   57.33%+4.27%
   process ensures compliance with the required
   stock price using get_stock_info and then using that
   parameters of the place_order function while aligning         GLM-4.7              68.00%   70.00%+2.00%   73.83%+5.83%
   price in the place_order function. This two-step
   with the user's intent for a market-price-based order.
   process ensures compliance with the required
   parameters of the place_order function while aligning         Table 7: Performance comparison of more LLMs with
   with the user's intent for a market-price-based order.        and without ReMe on BFCL-V3 (Avg@4 %).
      Figure 8: Experience example on BFCL-V3.
   when to use: When interacting with APIs that require
   precise authentication parameters and data extraction.
   content: The higher-scoring approach prioritized API
                                                                 Kimi-K2-Thinking are in the thinking mode, and
   when to use: When interacting with APIs that require
   specification validation before execution (e.g., confirming   the others are in the non-thinking mode.
   precise authentication parameters and data extraction.
   phone login requires phone number as username),
   experience content: The higher-scoring approach
   implemented robust error handling for authentication
   prioritized API specification validation before execution     B.4     Implementation Details
   failures, and used precise data extraction techniques
   (e.g., confirming phone login requires phone number as
   (search_notes with tags/query filters). The lower-scoring
   username), implemented robust error handling for              B.4.1 For Experience Acquisition
   approach made repeated authentication errors, included
   authentication failures, and used precise data extraction
   explanatory text in code blocks causing syntax failures,      First, we sample trajectories N = 8 times for each
   techniques (search_notes with tags/query filters). The
   and used inefficient string parsing that retained
   lower-scoring approach made repeated authentication           task query to obtain a diverse set of potential solu-
   metadata instead of clean titles.
   errors, included explanatory text in code blocks causing
   syntax failures, and used inefficient string parsing that     tions including both high-reward and low-reward
   retained metadata instead of clean titles.                    results. Next, within each group corresponding
                                                                 to the same task, all trajectories are sorted by
      Figure 9: Experience example on AppWorld.                  their rewards and only the lowest-scoring and
                                                                 highest-scoring examples are selected to the fol-
                                                                 lowing experience acquisition.
A-Mem A-Mem (Xu et al., 2025) is a system de-                    • Success Pattern Recognition: Successful tra-
signed to provide LLM agents with agentic mem-                     jectories are defined as those exceeding a pre-
ory, allowing them to autonomously manage their                    defined score threshold (empirically set to 1.0).
own long-term knowledge. It constructs a memory-                   Then, we prompt LLMsumm to identify the key
centric knowledge graph for agents, actively decid-                point that contributes to the task success.
ing what information to store, recall, and update
                                                                 • Failure Analysis: Conversely, failed trajectories
based on their goals and interaction. In our experi-
                                                                   trigger failure analysis by prompting LLMsumm
ments, we reproduce A-Mem using its open-source
                                                                   to determine the earliest key step that leads to
code, with slight prompt modifications to extract
                                                                   suboptimal outcomes.
procedural memories.
                                                                 • Comparative Insight Generation: When the
B.3    Model Configuration                                         reward gap exists between the chosen two tra-
We select Qwen3 series for backbone models in our                  jectories, we prompt LLMsumm to articulate
main experiments. By using Qwen3-Instruct mod-                     which specific decision or action distinguishes
els of different sizes, including 8B, 14B, and 32B,                higher-scoring from lower-scoring attempts.
we can explore whether memory-enhanced agent                        Three example prompts for experience acquisi-
performance improves as model size increases. For                tion are shown in Table 10, 11 and 12. To filter out
high-quality experience acquisition, Qwen3 think-                the generated invalid experiences, we employ the
ing mode is activated for BFCL-V3 tasks and dis-                 LLM-as-a-Judge prompt in Table 13 for validation.
abled for AppWorld tasks.
                                                                 B.4.2 For Experience Retrieval
   To validate the generalizability of our sys-
tem, we also evaluate other LLMs with and                        When a new task is received, LLMexecute retrieves
without ReMe on BFCL-V3 tasks, including                         relevant experiences Er by matching the current
GPT-4.1-2025-04-14 (OpenAI, 2025a), o4-mini-                     task’s query qnew against the usage scenario field
2025-04-16 (OpenAI, 2025b), Qwen3-Max-                           w of stored experiences:
Preview (Team, 2025a), Kimi-K2-Thinking (Moon-                            Er = arg topk [simcos (Ei , qnew )] .         (2)
shotAI, 2025), DeepSeek-V3.2 (Liu et al.,
2025a), and GLM-4.7 (ZhipuAI, 2025), where                       Here, simcos stands for the computation of co-
Qwen3-Max-Preview, DeepSeek-V3.2, and                            sine similarity between embeddings. In our exper-
                              Trajectory-level Experience                                                           Keypoint-level Experience
 when to use: When a user needs to assess the current market status and make informed                  when to use: When a user wants to place an order for a
 trading decisions, such as buying or canceling an order.                                              stock but without providing a specific price.
 experience content:                                                                                   experience content: The assistant demonstrated a methodical
 1. Retrieve the current time using `get_current_time`.                                                approach by first retrieving the current stock price using
 2. Use the retrieved time to update and obtain the market status via `update_market_status`.          get_stock_info and then using that price in the place_order
 3. If the market is open and the user decides to trade, use `place_order` to execute the trade.       function. This two-step process ensures compliance with the
 4. If the user requests cancellation, call `cancel_order` with the appropriate order ID.              required parameters of the place_order function while
 5. Provide updates on account details through `get_account_info` if requested by the user.            aligning with the user's intent for a market-price-based order.



                     Figure 10: Comparison of trajectory-level and keypoint-level experience granularity.

    BFCL-V3                   Trajectory-level
                        Overall (750)          Experience Miss Param (200)
                                           Base (150)                                                          Keypoint-level
                                                                                                         Miss Func (200) Long Experience
                                                                                                                                   Context (200)
                                                                                                           when to use: When a user wants to place an order
     when to use: When a user needs to assess the current market status and make informed                  for a stock but without providing a specific price.
    Qwen3-8B                37.78%                     59.55%
     trading decisions, such as buying or canceling an order.
                                                                                   31.00%                       19.00%                           47.00%
                                                                                                           content: The assistant demonstrated a methodical
     content:
     +ReMe             43.02%+5.24%               65.77%+6.22%                38.50%+7.50%                 21.50%
                                                                                                           approach by first
                                                                                                                       +2.50%               52.00%
                                                                                                                              retrieving the current stock price
                                                                                                                                                       +5.00%
     1. Retrieve the current time using `get_current_time`.                                                using get_stock_info and then using that price in
     2. Use the retrieved time to update and obtain the market status via `update_market_status`.
                                                                                                           the place_order function. This two-step process
     3. If the market is open and the user decides to trade, use `place_order` to execute the trade.       ensures compliance with the required parameters of
                               Table 8: Evaluation results on complete BFCL V3 Multi-Turn category.
     4. If the user requests cancellation, call `cancel_order` with the appropriate order ID.
                                                                                                           the place_order function while aligning with the
     5. Provide updates on account details through `get_account_info` if requested by the user.            user's intent for a market-price-based order.


 Model                 Retrieval Key               Avg@4          Pass@4             we contrast the structural and content character-
                       task query                  44.00%         63.33%             istics of the two granularity levels, showing how
                       generalized query           42.50%         63.77%             trajectory-level captures exhaustive procedural de-
 Qwen3-8B
                       query keywords              44.22%         65.33%             tails, while keypoint-level emphasizes critical ac-
                       usage scenario              44.50%         65.77%             tions and omits less relevant steps.
                       task query                  50.11%         71.77%
 Qwen3-14B
                       generalized query           50.49%         72.22%             D       Detailed Experimental Results
                       query keywords              51.16%         71.11%
                       usage scenario              51.89%         72.44%             D.1       Generalizability across Different Models
                       task query                  56.22%         72.22%             To examine the generalizability of ReMe, we con-
                       generalized query           55.33%         73.33%             duct experiments with different backbone mod-
 Qwen3-32B
                       query keywords              56.89%         74.44%
                                                                                     els, including GPT-4.1, o4-mini, Qwen3-Max,
                       usage scenario              56.05%         74.89%
                                                                                     Kimi-K2, DeepSeek-V3.2, and GLM-4.7. The
           Table 9: Ablation study of retrieve keys.                                 stacked analysis in Figure 3 and detailed results
                                                                                     in Table 7 show that ReMe consistently outperforms
                                                                                     No Memory baseline across various backbones,
iments, past experiences are indexed using vector                                    confirming the model-agnostic advantage of our
representations of the usage scenario field ϕ(w),                                    novel procedural memory system.
obtained from Qwen3-Embedding model ϕ(·). Our
selected vector database is Elasticsearch.                                           D.2       Results on Larger-scale Benchmark
                                                                                     To further show the superiority of ReMe, we supple-
                           ϕ(w) · ϕ(qnew )
      simcos (E, qnew ) =                                                  (3)       ment the experiments on the Missing Parameters,
                          ∥ϕ(w)∥ ∥ϕ(qnew )∥                                          Missing Functions, and Long Context category of
                                                                                     BFCL-V3 benchmark with total 600 tasks. Us-
   In Section 4.3, we also explore more indexing
                                                                                     ing the experience pool constructed from 50 tasks
strategies for experience storage. The example in
                                                                                     in base multi-turn category, the evaluation results
Figure 7 illustrates the differences among these
                                                                                     (Pass@4 as metric) are shown in Table 8. It can
retrieval keys.
                                                                                     be observed that our ReMe still performs well when
C       Experience Examples                                                          evaluated on a larger-size benchmark.

ReMe focuses on extracting keypoint-level expe-                                      D.3       Retrieval Key Analysis
riences from historical trajectories, with exam-                                     Table 9 compares four retrieval key strategies
ples for BFCL-V3 and AppWorld illustrated in                                         (task query, generalized query, query keywords,
Figure 8 and 9, respectively. To further investi-                                    and usage scenario) across three model scales
gate the impact of experience granularity, we com-                                   (Qwen3–8B, Qwen3–14B, and Qwen3–32B) on
pare trajectory-level and keypoint-level acquisi-                                    the BFCL-V3 benchmark under the ReMe(fixed)
tion, as described in Section 4.3. In Figure 10,                                     setting. Consistent with the trends observed in
Figure 4, simple indexing methods such as raw
task query and query keywords generally yield
lower performance. In contrast, LLM-generated
retrieval keys, particularly the usage scenario field,
exhibit consistently strong results across all mod-
els, achieving the highest or near-highest Avg@4
and Pass@4 scores.

E   Case Study
To gain deeper insights into how experience reuse
influences agent reasoning, we compare two agent
trajectories on the same BFCL-V3 task, one guided
by retrieved experiences and one without. As il-
lustrated in Figure 1, without past experience, the
agent encounters a failure when purchasing Ap-
ple shares since it fabricates the current market
price instead of fetching real-time data. With ReMe,
past experience guides the agent to correctly obtain
real-time pricing before placing an order, success-
fully completing the stock trading task. This case
demonstrates how experience-driven reasoning pre-
vents agents from repeating earlier mistakes and
improves robustness across similar scenarios.
Example Prompt for Success Pattern Recognition

You are an expert AI analyst reviewing successful step sequences from an AI agent execution.

Your task is to extract reusable, actionable step-level experiences that can guide future agent
executions.
Focus on identifying specific patterns, techniques, and decision points that contributed to success.

ANALYSIS FRAMEWORK:
• STEP PATTERN ANALYSIS: Identify the specific sequence of actions that led to success
• DECISION POINTS: Highlight critical decisions made during these steps
• TECHNIQUE EFFECTIVENESS: Analyze why specific approaches worked well
• REUSABILITY: Extract patterns that can be applied to similar scenarios

EXTRACTION PRINCIPLES:
• Focus on TRANSFERABLE TECHNIQUES and decision frameworks
• Frame insights as actionable guidelines and best practices

# Original Query
{query}

# Step Sequence Analysis
{step_sequence}

# Context Information
{context}

# Outcome
This step sequence was part of a successful trajectory.

OUTPUT FORMAT:
Generate 1-3 step-level success insights as JSON objects:
```json
[
  {{
   “when_to_use” : “Specific conditions when this success insight should be applied”,
   “task_query” : “Identify the specific task query from the original trajectory that this success
experience is most closely related to. Extract the exact query text.”,
   “generalized_query” : “Abstract the specific task query to create a more generalized task
representation.”,
   “experience” : “Detailed description of the successful step pattern and why it works”,
   “tags” : [“relevant", “keywords", “from", “the", “task", “query"],
   “confidence” : 0.8,
   “tools_used” : [“list", “of", “tools"]
  }}
]
```

                    Table 10: Example prompt for success pattern recognition.
Example Prompt for Failure Analysis

You are an expert AI analyst reviewing failed step sequences from an AI agent execution.

Your task is to extract learning experiences from failures to prevent similar mistakes in future
executions.
Focus on identifying error patterns, missed opportunities, and alternative approaches.

ANALYSIS FRAMEWORK:
• FAILURE POINT IDENTIFICATION: Pinpoint where and why the steps went wrong
• ERROR PATTERN ANALYSIS: Identify recurring mistakes or problematic approaches
• ALTERNATIVE APPROACHES: Suggest what could have been done differently
• PREVENTION STRATEGIES: Extract actionable insights to avoid similar failures

EXTRACTION PRINCIPLES:
• Extract GENERAL PRINCIPLES as well as SPECIFIC INSTRUCTIONS
• Focus on PATTERNS and RULES as well as particular instances

# Original Query
{query}

# Step Sequence Analysis
{step_sequence}

# Context Information
{context}

# Outcome
This step sequence was part of a failed trajectory.

OUTPUT FORMAT:
Generate 1-3 step-level failure prevention insights as JSON objects:
```json
[
  {{
   “when_to_use” : “Specific situations where this lesson should be remembered”,
   “task_query” : “Identify the specific task query from the original trajectory that this lesson is
most closely related to. Extract the exact query text.”,
   “generalized_query” : “Abstract the specific task query to create a more generalized task
representation.”,
   “experience” : “Universal principle or rule extracted from the failure pattern”,
   “tags” : [“relevant", “keywords", “from", “the", “task", “query"],
   “confidence” : 0.8,
   “tools_used” : [“list", “of", “tools"]
  }}
]
```

                          Table 11: Example prompt for failure analysis.
Example Prompt for Comparative Insights Generation

You are an expert AI analyst comparing higher-scoring and lower-scoring step sequences to extract
performance insights.

Your task is to identify the key differences between higher and lower performing approaches at the
step level.
Focus on what made the higher-scoring approach more effective, even when both approaches may
have had partial success.

SOFT COMPARATIVE ANALYSIS FRAMEWORK:
• PERFORMANCE FACTORS: Identify what specifically contributed to the higher score
• APPROACH DIFFERENCES: Compare methodologies and execution strategies
• EFFICIENCY ANALYSIS: Analyze why one approach was more efficient or effective
• OPTIMIZATION INSIGHTS: Extract lessons for improving performance

EXTRACTION PRINCIPLES:
• Focus on INCREMENTAL IMPROVEMENTS and performance optimization
• Extract QUALITY INDICATORS that differentiate better vs good approaches
• Identify REFINEMENT STRATEGIES that lead to higher scores
• Frame insights as PERFORMANCE ENHANCEMENT guidelines

# Higher-Scoring Step Sequence (Score: {higher_score})
{higher_steps}

# Lower-Scoring Step Sequence (Score: {lower_score})
{lower_steps}

OUTPUT FORMAT:
Generate 1-2 performance improvement insights as JSON objects:
```json
[
  {{
   “when_to_use” : “Specific scenarios where this performance insight applies”,
   “task_query” : “Identify the specific task query from the original trajectory that this
performance insight is most closely related to. Extract the exact query text.”,
   “generalized_query” : “Abstract the specific task query to create a more generalized task
representation.”,
   “experience” : “Detailed analysis of what made the higher-scoring approach more effective”,
   “tags” : [“relevant", “keywords", “from", “the", “task", “query"],
   “confidence” : 0.8,
   “tools_used” : [“list", “of", “tools"]
  }}
]
```

                  Table 12: Example prompt for comparative insights generation.
Example Prompt for Experience Validation

You are an expert AI analyst tasked with validating the quality and usefulness of extracted
step-level experiences.

Your task is to assess whether the extracted experience is actionable, accurate, and valuable for
future agent executions.

VALIDATION CRITERIA:
• ACTIONABILITY: Is the experience specific enough to guide future actions?
• ACCURACY: Does the experience correctly reflect the patterns observed?
• RELEVANCE: Is the experience applicable to similar future scenarios?
• CLARITY: Is the experience clearly articulated and understandable?
• UNIQUENESS: Does the experience provide novel insights or common knowledge?

# Experience to Validate
Condition: condition
Experience Content: experience_content

OUTPUT FORMAT:
Provide validation assessment:
```json
{{
 “is_valid” : true/false,
 “score” : 0.8,
 “feedback” : “Detailed explanation of validation decision”,
 “recommendations” : “Suggestions for improvement if applicable”
}}
```
Score should be between 0.0 (poor quality) and 1.0 (excellent quality).
Mark as invalid if score is below 0.3 or if there are fundamental issues with the experience.



                       Table 13: Example prompt for experience validation.
Example Prompt for Experience Reranking

You are an expert AI analyst tasked with reranking retrieved experiences based on their relevance
to a specific query.

Your task is to analyze the candidates and rank them by relevance, considering:
• DIRECT RELEVANCE: How directly applicable the experience is to the current query
• SITUATION SIMILARITY: How similar the experience context is to the current situation
• ACTIONABILITY: How actionable and specific the experience is
• QUALITY: The overall quality and clarity of the experience

# Current Query
query

# Candidate Experiences (Total: num_candidates)
candidates

OUTPUT FORMAT:
Provide a ranked list of candidate indices (0-based) from most relevant to least relevant:
```json
{{
 “ranked_indices” : [2, 0, 4, 1, 3],
 “reasoning” : “Brief explanation of ranking rationale”
}}
```

Note: Include ALL candidate indices in the ranking, even if some are less relevant.



                       Table 14: Example prompt for experience reranking.
Example Prompt for Experience Rewriting

You are an expert AI assistant tasked with rewriting and reorganizing context content to make it
more relevant and actionable for the current task.

Your task is to take the original context (containing multiple experiences) and rewrite it as a
cohesive, task-specific guidance that directly addresses the current situation.

REWRITING GUIDELINES:
• RELEVANCE FOCUS: Emphasize the most relevant aspects of each experience. Prioritize the
most relevant experiences. Use clear, direct language.
• ACTIONABLE INSIGHTS: Extract specific, actionable guidance. Make the context immediately
actionable
• COHERENT NARRATIVE: Create a flowing narrative rather than disconnected tips
• SITUATIONAL AWARENESS: Adapt the guidance to the current situation

# Current Task/Query
current_query

# Current Trajectory
current_context
# Original Context Content (Multiple Experiences)
original_context

OUTPUT FORMAT:
Provide the rewritten context:
```json
{{
 “rewritten_context” : “A cohesive, task-specific context message that reorganizes and adapts the
 original experiences for the current task. This should be written as a unified guidance rather than
 separate experience items.”,
}}
```

Guidelines:
- Rewrite as a unified, flowing guidance
- Adapt terminology and examples to match the current task domain
- Consolidate overlapping insights into coherent recommendations
- Prioritize experiences most relevant to the current situation
- Make the guidance feel custom-written for this specific task



                       Table 15: Example prompt for experience rewrting.
