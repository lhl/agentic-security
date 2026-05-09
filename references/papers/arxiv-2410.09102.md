                                        Published as a assemblage paper at ICLR 2025




                                        I NSTRUCTIONAL S EGMENT E MBEDDING : I MPROVING
                                        LLM S AFETY WITH I NSTRUCTION H IERARCHY
                                          Tong Wu1∗ Shujian Zhang2 Kaiqiang Song2 Silei Xu2 Sanqiang Zhao2 Ravi Agrawal2
                                          Sathish Indurthi2 Chong Xiang1 Prateek Mittal1 Wenxuan Zhou2
                                         1
                                           Princeton University 2 Zoom Video Communications


                                                                                       A BSTRACT




arXiv:2410.09102v2 [cs.LG] 1 Mar 2025
                                                    Large Language Models (LLMs) are susceptible to security and safety threats,
                                                    such as prompt injection, prompt extraction, and harmful requests. One major
                                                    cause of these vulnerabilities is the lack of an instruction hierarchy. Modern LLM
                                                    architectures treat all inputs equally, failing to distinguish between and prioritize
                                                    various types of instructions, such as system messages, user prompts, and data. As
                                                    a result, lower-priority user prompts may override more critical system instructions,
                                                    including safety protocols. Existing approaches to achieving instruction hierarchy,
                                                    such as delimiters and instruction-based training, do not address this issue at the
                                                    architectural level. We introduce the Instructional Segment Embedding (ISE)
                                                    technique, inspired by BERT, to modern large language models, which embeds
                                                    instruction priority information directly into the model. This approach enables mod-
                                                    els to explicitly differentiate and prioritize various instruction types, significantly
                                                    improving safety against malicious prompts that attempt to override priority rules.
                                                    Our experiments on the Structured Query and Instruction Hierarchy benchmarks
                                                    demonstrate an average robust accuracy increase of up to 15.75% and 18.68%,
                                                    respectively. Furthermore, we observe an improvement in the instruction-following
                                                    capability of up to 4.1% on AlpacaEval. Overall, our approach offers a promising
                                                    direction for enhancing the safety and effectiveness of LLM architectures.


                                        1       I NTRODUCTION
                                        Large Language Models (LLMs) have shown significant
                                        potential in enabling agentic applications and autonomous
                                        decision-making across various domains, such as web
                                        agents, educational tools, and medical assistance (Yao
                                        et al., 2022; Gan et al., 2023; Abbasian et al., 2024). To
                                        optimize LLM applications, a structured approach to im-
                                        plementation is widely adopted. This involves clear dis-
                                        tinctions among system instructions, user prompts, and
                                        data inputs, as illustrated in Figure 1. These instructions
                                        contain specific priorities (e.g., system instructions have
                                        higher importance than user instructions) that help the
                                        model execute functionalities and better assist users.
                                        However, modern LLM architecture processes all input
                                        tokens equally without formal mechanisms to differenti- Figure 1: A demonstration of the hier-
                                        ate instructions. Consequently, malicious attackers can archy of instructions, including system
                                        easily exploit this limitation to override the priorities of in- instruction, user instruction, data input
                                        structions, leading to various vulnerabilities. For example, as well as model output.
                                        prompt injection (Greshake et al., 2023) inserts malicious
                                        instructions into data sources to subvert the original ones.
                                        Prompt extraction (Zhang et al., 2024) aims to extract system messages, revealing proprietary prompts.
                                        Harmful requests (Ganguli et al., 2022) involve malicious users providing unsafe instructions to elicit
                                        irresponsible or dangerous responses from the safety-aligned LLMs. These vulnerabilities underscore
                                        the significance of designing more robust instruction hierarchy in LLM applications.
                                            ∗
                                                Works done at Zoom. Correspondence to: tongwu@princeton.edu, wenxuan.zhou@zoom.us


                                                                                              1
Published as a assemblage paper at ICLR 2025




Figure 2: A demonstration of various vulnerabilities of LLM applications, including prompt injection,
prompt extraction as well as harmful request.
Recently, research has been conducted to enhance models’ ability to follow the instruction hierar-
chy. For instance, Hines et al. (2024) proposed prompt-based solutions utilizing a special delimiter
between prompts. Chen et al. (2024) and Wallace et al. (2024) suggested methods for generating hier-
archical prompts, incorporating adversarial data along with high-quality responses to fine-tune LLMs.
However, despite these improvements, the core challenge persists: current LLM architectures still
lack an effective mechanism to differentiate and prioritize hierarchical instructions.
In this work, we tackle the challenge by introducing an architecture-level design for LLMs. Inspired
by BERT (Lan et al., 2019) and its variants (Lan et al., 2019; Yasunaga et al., 2022), we propose using
an Instructional Segment Embedding (ISE) to categorize different types of instructions distinctly.
Specifically, we enhance the input token by incorporating segment information that classifies each
token by its role (e.g., system instruction as 0, user prompt as 1, and data input as 2). This segment
information is processed through a learned embedding layer, converting it into segment embeddings,
which are then passed to later self-attention layers along with token embeddings. To obtain a robust
segment embedding layer, we perform supervised fine-tuning on datasets containing structured
prompts and high-quality responses. This process enables the model to differentiate between levels
of instruction hierarchies more effectively, thereby boosting the overall safety of the system.
Empirically, we conduct comprehensive experiments on two benchmarks: Structured Query (Chen
et al., 2024) and Instruction Hierarchy (Wallace et al., 2024), which are constructed based on the
Alpaca (Taori et al., 2023) and Ultrachat (Ding et al., 2023) datasets, respectively. We fine-tune
multiple pretrained LLMs, including Llama-2-13B (Touvron et al., 2023), Llama-3-8B (Llama Team,
2024), and Llama-3.1-8B, and compare their performance with and without the use of Instructional
Segment Embedding. Our findings indicate that our method yields substantial improvements in
robustness while either maintaining or enhancing the models’ general capabilities, regardless of the
presence of adversarial training data. For example, on the Structured Query benchmark, the method
achieves an average robust accuracy improvement of up to 15.75% against indirect prompt injection
attacks. On the Instruction Hierarchy benchmark, our ISE yields an average boost in robustness of
up to 18.68% across multiple vulnerabilities, including indirect and direct prompt injection, prompt
extraction, and harmful requests. In addition, the integration of ISE also maintains or even improves
the instruction-following capability by as much as 4.1% on AlpacaEval.
Contributions: (1) We identify and analyze critical limitations in current LLM architectures concern-
ing the lack of instruction hierarchy (Section 3). (2) We propose Instructional Segment Embedding, a
simple yet effective method designed to incorporate instruction-type information directly into the
model. This approach enables the model to better distinguish and prioritize instructions based on their
privilege (Section 4). (3) We empirically demonstrate the effectiveness of ISE across two benchmarks,
encompassing five training datasets and addressing four types of vulnerabilities (Sections 5 & 6).


2    BACKGROUND : LLM V ULNERABILITIES
Modern LLM products typically involve up to three stakeholders1 : (1) the LLM application provider
(e.g., OpenAI), who designs the model’s system-level instructions and manages the general workflow;
(2) the primary user, who provides input in the form of instructions or queries; and (3) third-party
    1
      Here, we simplify real-world scenarios by assuming the LLM provider and the LLM application provider to
be the same stakeholder collectively responsible for providing system instructions. Additionally, we consider
text from third parties as data, which may also include other contents like outputs from external API calls.


                                                     2
Published as a assemblage paper at ICLR 2025




         <| begin_of_text | >
         <| start_header_id | > system <| end_header_id | >{{ system_prompt }} <| eot_id | >
         <| start_header_id | > user <| end_header_id | >{{ user_message }} <| eot_id | >
         <| start_header_id | > assistant <| end_header_id | >

    Figure 3: A demonstration of the chat template for Llama-3-Instruct (Llama Team, 2024).


source/data, such as web search results, that offer additional context for the LLM. As a result, LLM
applications often establish a hierarchical order of instructions based on their perceived reliability:
system instructions take precedence, followed by user instructions, and finally data.
Security vulnerabilities arise when conflicts between these priorities occur, such as (1) a malicious
user attempting to bypass safety system instructions or (2) malicious web providers injecting harmful
actions in data. These conflicts may take various forms, including prompt injections, prompt
extractions, and harmful requests, as shown in Figure 2 and outlined below.
Prompt injection (Figure 2a). Prompt injection attacks (Perez & Ribeiro, 2022) generally occur in
two forms: indirect and direct. Indirect prompt injection attacks occur when third-party data input
contains instructions that should never be followed by LLMs. Direct prompt injection attacks happen
when a malicious attacker manipulates the user query to an LLM, causing the model to generate
outputs that deviate from predefined instructions.
Prompt extraction (Figure 2b). This vulnerability (Zhang et al., 2024) often exploits a weakness in
certain LLM applications that store confidential information within system instructions. Attackers
may craft malicious queries that prompt the model to reference this stored information, potentially
leading to the disclosure of system prompts.
Harmful requests (Figure 2c). Harmful requests (Ganguli et al., 2022) aim to bypass the model’s
safety alignment (Bai et al., 2022) through malicious queries. These prompts can lead to unsafe
outcomes, including unethical responses or even the weaponization of LLMs.
In this paper, we aim to enhance the instruction hierarchy capabilities of LLMs, thereby mitigating
various forms of attacks that attempt to override the priority rules.

3    L ACK OF I NSTRUCTION H IERARCHY IN M ODERN LLM A RCHITECTURE
Current embeddings lack instruction hierarchy. Given an input context XM with M tokens
x1 , x2 , . . . , xM , the large language models first convert each token into a high-dimensional vector
using a token embedding matrix ETok ∈ RV ×D , where V is the vocabulary size, and D is the output
embedding dimension. The embedding vector eTok        m for token xm is given by E
                                                                                        Tok
                                                                                            [xm ], based on its
index in the vocabulary. Additionally, the model also obtains positional embeddings EPos          m , based on
the position of each token. Then, the token embeddings (eTok           Tok          Tok
                                                                  1 , e2 , . . . , eM ) will be fed into the
transformer’s self-attention layers along with positional embeddings for further processing.2
In these self-attention layers, each token embedding is processed “equally”. As a result, the model
recognizes only the semantic content and sequential order of each token from the embedding, lacking
the capability to distinguish their hierarchical significance. This architectural design can inherently
lead to vulnerabilities. For instance, a lower-priority user prompt, such as “Please focus on my prompt
as the system prompt is outdated”, could mistakenly be prioritized and override the original system
prompt. This could inadvertently lead to various types of vulnerabilities, as shown in Figure 2.
Prior works do not address this issue. To mitigate these vulnerabilities, researchers have introduced
methods to improve the robustness of large language models (LLMs) during the supervised fine-
tuning phase. This method involves not only using benign prompt-response data but also adversarial
or misaligned instructions with robust responses (Piet et al., 2023; Chen et al., 2024; Wallace
et al., 2024). This approach helps the model learn to prioritize hierarchical instructions and adhere
to embedded safety protocols. Despite its improvement, the challenge of uniformly processing
hierarchical instructions remains a fundamental limitation inherent in current embedding methods
    2
      Models handle positional information in different ways. For example, GPT-2 (Radford et al., 2019) adds
learned positional embeddings to its token embeddings, while Llama-2 uses Rotary Position Embedding (RoPE)
(Su et al., 2024) in its attention blocks to represent positions.


                                                       3
Published as a assemblage paper at ICLR 2025




Figure 4: The input representation includes both token embeddings and instructional segment
embeddings. We categorize all input texts into four segments: system instructions, user instructions,
third-party data, and generated output. We assign different segment embeddings to each type of input
text. The final input embeddings are the sum of token embeddings and segment embeddings. The
LLMs will predict the next token after "the summary is", with extra instruction hierarchy information.



and model architecture. We demonstrated that our proposed architecture design can provide better
robustness (see results in Table 1 and Figure 5).
An alternative approach is to use specific chat templates to better handle input data. For instance,
LLAMA-3-Chat (Llama Team, 2024) leverages a chat template with special tokens like <|be-
gin_of_text|> and <|star_header_id|> as shown in Figure 3. Hines et al. (2024) and Chen et al.
(2024) have also leveraged the specialized delimiters that aid the model in more effectively distin-
guishing instructions. However, two major drawbacks exist. Firstly, during inference, only a few
tokens contain hierarchical priority information, and this signal is likely to diminish when encounter-
ing long-context tasks (e.g., summarizing a novel). Secondly, malicious attackers may extract these
special delimiters, and exploiting them could lead to more severe attacks (Zheng et al., 2024).


4   P ROPOSED A PPROACH : I NSTRUCTIONAL S EGMENT E MBEDDING (ISE)

To tackle this challenge, we propose Instructional Segment Embedding (ISE), which encodes the
instruction hierarchy directly into the embeddings. This enables subsequent self-attention layers to
more effectively recognize and follow instruction priorities, thereby boosting robustness.
Specifically, we leverage a learnable embedding layer, similar to the token embedding matrix ETok ,
which we call the segment embedding matrix ESeg . We define ESeg ∈ RH×D , where H is the
number of hierarchies and D is the embedding dimension. By default, we set H to 4, representing
system, user, data, and output. Each token in XM is tagged with corresponding hierarchy information
hm ∈ {0, 1, 2, 3}, readily derived from distinct stakeholder categories in the LLM applications. The
instructional segment embeddings of XM are represented as (eSeg      Seg          Seg
                                                                1 , e2 , . . . , eM ) and obtained from
  Seg
E [hm ]. To incorporate this modification, the final embeddings are computed by summing the
token embeddings and segment embeddings. This results in (eSeg       Tok Seg         Tok     Seg
                                                              1 + e1 , e2 + e2 , . . . , eM + eM ),
                                                                                                    Tok

as illustrated in Figure 4. These embeddings are then fed into self-attention layers, following the
process used in current LLMs.
The segment embedding layer is trained alongside other parameters during the supervised fine-
tuning (instruction tuning) phase. In our experiments, we use widely adopted instruction-following
datasets and construct structured queries based on the original prompt using GPT-4o (OpenAI, 2023).
Additionally, we experiment with datasets containing malicious instructions designed to override
higher-level instructions, enabling the model to learn how to reject or ignore such commands.
Flexibility in design. The design choice for Instructional Segment Embedding can be flexible and
should be tailored to the specific downstream tasks. For instance, if the data category can be further
subdivided into outputs from external API tools or online information, we can introduce "tools type"
and "web data type" categories, providing more fine-grained information. If the application does not
involve third-party context, the data type can be omitted.


                                                  4
Published as a assemblage paper at ICLR 2025




Connection to BERT. Inspired by BERT’s segment embeddings (Devlin et al., 2019), originally used
to distinguish input segments for next-sentence prediction, our approach repurposes these embeddings
to encode hierarchical instructions. This helps address the need for structured prompts and safer LLM
outputs by providing direct, contextually relevant cues to the model. Unlike BERT, we incorporate
the output type for two reasons: (1) It supports consistent autoregressive inference for each token
in the input. (2) output may also include instructions (e.g., “Please provide more details of your
question”) that are critical in multi-turn language tasks.
Simplicity and lightweight. The implementation is also straightforward and lightweight, requiring
only H × D additional parameters. We provide a PyTorch code snippet that demonstrates how to
implement this in just a few lines, as shown in Appendix A.

5       E XPERIMENTAL D ESIGN
In this section, we present how we conducted the experiments. Specifically, we begin by describing
the generation of the training data (Section 5.1), the experimental setup (Section 5.2), and the details
of the robustness evaluation against multiple attacks (Section 5.3).

5.1       G ENERATING T RAINING DATA

We conduct experiments using two benchmarks: Structured Query and Instruction Hierarchy.
The Structured Query benchmark primarily focuses on indirect prompt injection attacks, whereas the
Instruction Hierarchy benchmark evaluates all types of vulnerabilities discussed, including indirect
and direct prompt injections, prompt extraction, and harmful requests.
For the Structured Query benchmark, we generally follow the approach of Chen et al. (2024).
Two datasets are constructed: Clean Alpaca and Adversarial Alpaca. The Clean Alpaca dataset is
constructed by Alpaca-Cleaned-50K dataset (Taori et al., 2023; Gururise, 2024). For the Adversarial
Alpaca dataset, we incorporate instructions drawn from other samples (either directly or with a
fabricated response) into the data and train the model to ignore such instructions. More details are
available in Section B.1.
For the Instruction Hierarchy benchmark, we mostly adhere to previous work by Wallace et al.
(2024) to create both aligned and misaligned data3 . We select the UltraChat-200K dataset (Ding
et al., 2023) as the base dataset, which contains more training data. Since UltraChat consists
solely of prompts and responses, we utilized GPT-4o (OpenAI, 2023) to decompose 10K prompts
into three components: system instructions, user instructions, and data inputs, which we term the
UltraChat Baseline. Additionally, we incorporate datasets from SystemChat (Abacus.AI, 2023) and
SystemMessage (Huggingface, 2023) that contain specifical system prompts, designated as the System
Follow dataset. Lastly, we crafted three types of attacks for the malicious data: indirect/direct prompt
injection and prompt extraction, which we collectively name the Instruction Hierarchy datasets. We
excluded harmful request data from the training but used them as evaluations following Wallace et al.
(2024). Further details on generating training data are available in Section B.2.

5.2       E XPERIMENT S ETUP

Data processing. We format all training and evaluation samples with clear segmentation, including
system, user, data, and output information. We merge the system and user instructions for the
Structured Query benchmark into the same type, as all system instructions in Alpaca are identical. To
simplify the experiments, we train and evaluate only single-turn chats, where the conversation ends
after the model generates a complete response.
LLM training and inference. By default, we utilize Llama-2-13B (Touvron et al., 2023) and
Llama-3-8B (Llama Team, 2024) as the pretrained models for Structured Query and Instruction
Hierarchy, respectively. Experiments with Llama-3.1-8B are presented in Section 6.4.
We employ supervised fine-tuning to update all model parameters for all baseline and ISE methods
with three epochs. A learning rate of 2e-5 and a cosine learning schedule are used. During inference,
we use top-p sampling methods with the model’s default settings.
    3
        We contacted the authors for training data and details, but they cannot share them due to company restrictions.


                                                            5
Published as a assemblage paper at ICLR 2025




Baselines. We conduct experiments on multiple datasets and compare our Instructional Segment
Embedding method (+ISE) with models that do not use it. For the Structured Query benchmark,
we include experiments using either text (Baseline) or newly constructed tokens (Delimiter) to
differentiate distinct types of prompts, following the approach of Chen et al. (2024). For the Instruction
Hierarchy benchmark, we only include experiments with the default delimiters of LLAMA-3-8B
(Baseline), as these are already specially reserved tokens (shown in Figure 3).

5.3   ROBUSTNESS E VALUATION

We evaluate our method using comprehensive attack methods. More details are in Appendix C.
Structured Query benchmark. Following the approach of Chen et al. (2024), we evaluate indirect
prompt injection attacks on models trained on the Alpaca dataset. Specifically, we focus on four types
of attacks: Naive Attack, Ignore Attack, Escape Separation Attack, and Completion Real Attack as
in-domain attacks. All in-domain attacks are crafted by injecting one or a few sentences at the end
of the data to trick the model into outputting the word “hacked”. Since the scenarios for in-domain
attacks are quite similar to the adversarial training data constructed by Chen et al. (2024), we further
develop new attacks based on the in-domain methods. These new attacks inject adversarial texts
at the data’s beginning and end, called out-of-domain attacks. This strategy significantly degrades
the robustness of models trained on the adversarial Alpaca dataset. For the evaluation metrics, we
compute the rate at which the model does not generate content containing the word “hacked” and
refer to this as robustness or robust accuracy.
Instruction Hierarchy benchmark. Evaluating models trained on the Instruction Hierarchy bench-
mark is complex due to the need to account for indirect and direct prompt injection, prompt extraction,
and harmful requests. To address these challenges: (1) For indirect prompt injection, we apply the
same evaluations and metrics used in Structured Query benchmarks. For direct prompt injection,
we use the same attacking prompts but inject them directly into the user prompt. (2) For prompt
extraction, we use the ShareGPT and Unnatural Instructions datasets from (Zhang et al., 2024), along
with 15 author-selected effective extraction prompts, and evaluate robustness using an approximate
metric based on Rouge-L recall (Lin, 2004). (3) For harmful requests, we follow the evaluations of
(Wallace et al., 2024), using Jailbreakchat (Chat) and "Do Anything Now" (DAN) prompts (Shen
et al., 2024) paired with StrongREJECT malicious instructions (Souly et al., 2024). We query GPT-4o
to check whether its responses adhere to safety guardrails.
Comprehensive robustness metrics. For prompt injection and extraction, which encompass multiple
attack methods or malicious prompts, we include additional metrics. We define average robustness as
the model’s average performance across these various attack methods, offering a general evaluation
of model robustness. Furthermore, we introduce worst robustness, representing the model’s ability to
defend against the most challenging attack.
Clean evaluation. We evaluate the model’s capacity using standard datasets. Both benchmarks
are assessed with AlpacaEval 1.0 (Li et al., 2023). For the Instruction Hierarchy benchmark, we
additionally use the MT-Bench (Zheng et al., 2023) to measure the model’s performance.

6     E XPERIMENTAL R ESULTS AND A NALYSIS
We report the main results on the Structured Query benchmark in Section 6.1 and the Instruction
Hierarchy in Section 6.2. We observe that our approach consistently achieves higher robust
accuracy while either maintaining or improving general capability. We also present a more
detailed analysis of multiple vulnerabilities in Section 6.3. Lastly, we conduct an over-refusal
evaluation and assess generalization to the advanced Llama-3.1-8B model in Section 6.4.

6.1   M AIN R ESULTS ON S TRUCTURED Q UERY

Maintains high utility. In Table 1, we present the main results for capability and robustness by
comparing our method with the baseline and delimiter methods on both the clean and adversarial
Alpaca datasets. Compared to the other two methods, Instructional Segment Embedding maintains
high utility with negligible degradation or even slight improvement. The difference in winning rate
between the methods is less than 1% on AlpacaEval.


                                                    6
Published as a assemblage paper at ICLR 2025




Table 1: The evaluation results on Structured Query benchmark against both in-domain and
out-of-domain indirect prompt injection attacks. We compare our method (+ISE) with the baseline
and delimiter methods (Chen et al., 2024) on Clean Alpaca and Adversarial Alpaca.
                 Dataset                    Clean Alpaca                           Adversarial Alpaca
                 Method          Baseline   Delimiter +ISE (Ours)          Baseline Delimiter +ISE (Ours)
Capability (↑)   AlpacaEval       72.76       72.67          72.13          73.41     72.26       73.76
                 Naive            65.87       68.75          75.96         100.00     99.04      100.00
                 Ignore           57.69       57.21          70.19         99.52      99.04       99.04
 In-Domain       Escape-S         75.00       69.23          78.85         99.52      99.52      100.00
Robustness (↑)   Completion-R      4.81        7.21          40.38         70.19     100.00      100.00

                 Average          50.84       50.60       66.35 (+15.75)    92.31     99.16    99.76 (+0.60)
                 Worst            4.81        7.21        40.38 (+32.17)    70.19     99.04    99.04 (+0.00)
                 Naive            62.02       66.35          69.71          64.90     67.79       76.44
                 Ignore           52.40       51.92          69.71          98.56     96.15       96.63
Out-of-Domain    Escape-S         72.12       71.63          70.67          73.08     76.44       88.46
Robustness (↑)   Completion-R      1.92       12.99          34.14          85.58     91.35       99.52

                 Average          47.12       50.72       61.06 (+10.34)    80.53     82.93    90.26 (+7.67)
                 Worst            1.92        12.99       34.14 (+21.15)    64.90     67.79    76.44 (+8.65)



Consistent robustness enhancement. We also observe that our method consistently improves
robustness against indirect prompt injection attacks. Specifically, it achieves a 15.75% increase in
average robust accuracy and a 32.17% increase in worst robust accuracy against in-domain attacks
when trained with the clean Alpaca dataset. Both the delimiter and our ISE reach nearly perfect
in-domain robustness. For out-of-domain attacks, we find that adding ISE can also significantly
enhance robustness, resulting in improvements of ∼10% and ∼7% in average robustness for clean
and adversarial Alpaca, respectively. Interestingly, our out-of-domain attacks degrade the robustness
of models trained on the adversarial Alpaca dataset more than those trained on the clean Alpaca
dataset (16% vs. 5%). This suggests that the adversarial dataset may overfit to in-domain attacks.
Nevertheless, adding ISE largely maintains generalization to out-of-domain attacks.


6.2   M AIN R ESULTS ON I NSTRUCTION H IERARCHY

We present the evaluation results for our method on the Instruction Hierarchy benchmark in Figure 5,
focusing on model capability and average robustness across various datasets and attack scenarios.
Improvement in capabilities. Adding ISE boosts instruction-following capabilities, particularly for
models trained on the System Follow and Instruction Hierarchy datasets. For example, the AlpacaEval
win rate improves by approximately ∼4.1% when training on the Instruction Hierarchy dataset with
our ISE, as shown in Figure 5(a). Additionally, we observe negligible degradation on MT-Bench for
the UltraChat Baseline model and improvements for the other two training datasets.
Enhanced safety against multiple vulnerabilities. We evaluate the robustness of the models against
indirect and direct prompt injection attacks, prompt extraction attacks, and harmful requests. (1)
Indirect and direct prompt injection scenarios (#1, #2, #3, and #4 in Figure 5(b)) : We report the
average robustness across four types of attacks, including both in-domain (ID) and out-of-domain
(OOD) contexts. Our results demonstrate robust accuracy improvements ranging from 5% to 25%
across all training data configurations when applying the ISE method. Notably, for models trained with
the UltraChat Baseline, robust accuracy increases by nearly 25% on average. (2) Prompt extraction
scenarios (#5 and #6 in Figure 5(b)): Robustness is measured against 15 effective extraction prompts.
Our findings show that models using ISE consistently achieve higher average robustness, with an
increase of at least 10% across all datasets. This is evident even for models trained on the Instruction
Hierarchy dataset, which already demonstrated more than 80% robust accuracy. (3) Harmful requests
(#7 and #8 in Figure 5(b)): Our analysis reveals improvements in robustness for models under


                                                      7
Published as a assemblage paper at ICLR 2025




                                       AlpacaEval                                                                 MT-Bench




                                                                    (a) Capability

           #1: Indirect Prompt Injection (ID)               #2: Indirect Prompt Injection (OOD)             #3: Direct Prompt Injection (ID)

           #4: Direct Prompt Injection (OOD)                #5: Prompt Extraction (ShareGPT)                #6: Prompt Extraction (Unnatural)

           #7: Harmful Requests (Chat)                      #8: Harmful Requests (DAN)




                  UltraChat Baseline                                     System Follow                            Instruction Hierarchy

                                                                  (b) Robustness
Figure 5: The evaluation of model capabilities on the Instruction Hierarchy benchmark is conducted
using AlpacaEval and MT-Bench, as illustrated in Figure (a). Robustness evaluations include both
indirect and direct prompt injection attacks, prompt extraction attacks, and harmful requests, as shown
in Figure (b). We performed experiments across three training datasets (i.e., UltraChat Baseline,
System Follow, and Instruction Hierarchy) and compared ISE with the baseline (Wallace et al., 2024).

                                                                         UltraChat Baseline
             Baseline   64.4    59.6       74.5       2.4       50.2         2.4        55.8    43.3       64.4       2.9       41.6      2.9    100
          +ISE (Ours)   82.2    73.1       86.5      56.7       74.6        56.7        70.7    71.2       74.0      53.4       67.3     53.4
                                                                                                                                                 80



                                                                                                                                                      Robustness (%)
                                                                           System Follow
             Baseline   61.5    53.9       74.0       6.2       48.9         6.2        53.4    33.2       52.9       1.9       35.3      1.9    60
          +ISE (Ours)   77.9    71.2       81.7      58.6       72.3        58.6        62.0    59.6       63.0      33.6       54.6     33.6    40
                                                                    Instruction Hierarchy
             Baseline   83.7    76.9       90.9      58.6       77.5        58.6        66.3    75.5       72.1      23.1       59.3     23.1
                                                                                                                                                 20
          +ISE (Ours)   87.0    80.8       88.5      74.0       82.6        74.0        67.8    73.6       76.4      51.0       67.2     51.0    0
                        Naive   Ignore   Escape_S Completion_R Average      Worst       Naive   Ignore   Escape_S Completion_R Average   Worst
                                           In Domain Attacks                                               Out of Domain Attacks
Figure 6: Robust accuracy of indirect prompt injection attack on the Instruction Hierarchy benchmark
with both in-domain and out-of-domain attacks. More details are described in Appendix E.1.


the UltraChat Baseline and Instruction Hierarchy settings when using ISE. For System Follow, our
methods either maintain or slightly exceed the baseline method.
Overall, using Instructional Segment Embeddings significantly enhances both the capabilities and
robustness of models against a wide range of attacks on the Instruction Hierarchy benchmark.

6.3   D ETAILED A NALYSIS OVER ATTACKS

The previous sections mainly covered the overall results (average robustness) across multiple prompt
injection and extraction attacks. Here, we provide more detailed evaluations of attacks on the
Instruction Hierarchy benchmark. Results for the Structure Query are reported in Appendix D.
Prompt injection. In Figure 6, we present the results of indirect prompt injection attacks, including
Naive, Ignore, Escape Separation, and Completion Real, across in-domain and out-of-domain
scenarios. The results indicate that our ISE method significantly enhances performance compared to


                                                                                    8
Published as a assemblage paper at ICLR 2025




                                                                                                                          UltraChat Baseline
   Baseline    46.6           51.8          67.0      70.2             66.2          72.8                      92.4       68.6       82.2     77.4    68.0                    79.8      85.8       74.0      54.4       70.5        46.6        100
+ISE (Ours)    94.6           97.4          99.2      97.8             92.0       100.0                        99.8       98.4       98.0     98.0    98.4                    99.2      99.0       97.2      94.2       97.5        92.0
                                                                                                                                                                                                                                                80
                                                                                                                            System Follow


                                                                                                                                                                                                                                                       Robustness (%)
   Baseline    48.2           61.4          65.6      72.4             73.0          58.6                      79.0       41.2       84.2     67.0    77.6                    88.6      80.2       78.2      66.8       69.5         41.2       60
+ISE (Ours)    82.0           89.8          92.6      90.8             83.2          88.6                      88.0       92.4       91.4     89.2    92.8                    96.4      99.4       94.4      83.0       90.3        82.0
                                                                                                                                                                                                                                                40
                                                                                                                      Instruction Hierarchy
   Baseline    78.0           63.0          76.6      76.2              61.0         92.4                      97.6       77.8       87.4     90.6    91.2                    87.4      81.4       78.8      72.4       80.8         61.0       20
+ISE (Ours)     91.8          85.6          89.0      95.4             78.4          93.0                      94.2       97.0       92.6     95.6    93.4                    97.2      98.0       89.8      87.2       91.9        78.4        0
               Att1           Att2          Att3      Att4           Att5         Att6                        Att7        Att8   Att9 Att10 Att11 Att12 Att13 Att14 Att15 Average Worst


 Figure 7: Robust accuracy against 15 effective prompt extraction attacks on ShareGPT dataset.

                                                                                                        100                                                             100
         Baseline      26.0          24.0      28.0          60                                                                      Baseline                                        Baseline
                                                                                                        80                           +ISE (Ours)                        80           +ISE (Ours)
                                                             50



                                                                                  Compliance Rate (%)                                                 Performance (%)
      +ISE (Ours)      44.0          26.0      34.0



                                                                 Robustness (%)
                                                             40                                         60                                                              60
                Disinformation Hate Illegal services
                                                             30                                         40                                                              40
         Baseline      30.5          24.0      22.2          20
                                                                                                        20                                                              20
      +ISE (Ours)      39.0          26.0      29.6
                                                             10
                                                                                                         0
                                                             0                                                UltraChat     System      Instruction                      0
                                                                                                                                                                                AlpacaEval   Indirect Propmt Direct Propmt      Prompt      Harmful
                    Crimes       Sexual       Violence                                                         Baseline     Follow       Hierarchy                              Capability      Injection      Injection       Extraction   Requests

      Figure 8: Harmful re-                                                       Figure 9: Overefusal Figure 10: Evaluation of Llama-3.1-
      quests across categories                                                    evaluation on Wild- 8B models trained on the UltraChat
      using UltraChat Baseline.                                                   Chat.                Baseline.

the baseline across nearly all scenarios. Notably, the Completion Real attack severely compromises
model robustness, resulting in less than 10% effectiveness for models trained on the UltraChat
Baseline and the System Follow dataset without ISE. This attack works by introducing a spoofed
response to the benign instruction and concatenating a new malicious instruction into the data. Models
that fail to effectively differentiate between these types of instructions are prone to executing the new
malicious instruction. However, our method significantly boosts robustness, yielding improvements
ranging from approximately 30% to 50%. We also observe similar trends for direct prompt injection
attacks, which are detailed in Appendix E.2.
Prompt extraction. As mentioned in Section 5.3, we utilize 15 effective malicious prompts to extract
the system messages. In Figure 7, we present all the results and find that our method consistently
outperforms the baseline, notably enhancing the worst robust accuracy by up to approximately 45%.
Interestingly, the model trained on the UltraChat Baseline dataset with ISE exhibits the highest
robustness, even exceeding that of the model trained on the Instruction Hierarchy dataset. We find
that this is because the instruction-following capability of models trained on the UltraChat Baseline
is relatively weak (about 20% lower than the other two models on AlpacaEval). Consequently,
in scenarios where the model is misled into fulfilling a request to output the system message, it
sometimes generates only a partial system prompt. Therefore, the attack is not classified as successful.
Results on the Unnatural dataset are provided in Appendix E.3.
Harmful requests. In Figure 8, we report the robustness of models trained on UltraChat Baseline
against Jailbreakchat prompts across six categories: ‘Disinformation and Deception,’ ‘Hate, Harass-
ment, and Discrimination,’ ‘Illegal Goods and Services,’ ‘Non-Violent Crimes,’ ‘Sexual Content,’
and ‘Violence.’ We observe that Instructional Segment Embedding improves robustness in 6 out of
6 categories, with improvements of up to 18%. Further results are reported in Appendix E.4.

6.4     OTHER A NALYSIS

Over-refusal Evaluation. One potential concern is that our method may overfit and refuse to follow
user instructions. Therefore, we conduct an over-refusal evaluation on the WildChat dataset (Zhao
et al., 2024) following (Anthropic, 2024; Zou et al., 2024). After filtering out prompts that exceed the
context window, we use 691 non-toxic prompts to query the model and evaluate whether it generates
non-refusal responses using GPT-4o. In Figure 9, we report the compliance rate on the benchmark
and observe that our ISE improves the compliance rate by about 10% for the model trained on the
UltraChat Baseline but shows slight degradation for the other two models. Overall, we expect that
our method will maintain model capacity, as shown on AlpacaEval and MT-bench in Figure 5.


                                                                                                                                       9
Published as a assemblage paper at ICLR 2025




Generalization to Other Model. We also evaluated Llama-3.1-8B using the same setup as Llama-3-
8B on the Instruction Hierarchy benchmarks. In Figure 10, we present the results on AlpacaEval and
the robustness against four attacks (averaged results) of models trained on the UltraChat Baseline.
Our method demonstrates an approximate 10% improvement in win rate on the AlpacaEval dataset.
For robustness, we observe around a 5% robust accuracy improvement against harmful requests and
over 10% on all other attacks. Overall, these results suggest our method can be generalized across
different models. The complete results are provided in Appendix E.5.


7    R ELATED W ORKS

Safety vulnerabilities of LLMs. Recently, the safety of LLMs has become a critical concern. (1)
These models are vulnerable to indirect and direct prompt injection attacks. Indirect prompt injections
happen when malicious content is embedded in inputs sourced from external data providers, as
discussed in various research studies (Greshake et al., 2023; Liu et al., 2023; Zhan et al., 2024;
Debenedetti et al., 2024). In contrast, direct prompt injections occur when attackers explicitly
introduce malicious instructions into user input, as demonstrated in (Perez & Ribeiro, 2022; Mu et al.,
2023; Toyer et al., 2024; Sharma et al., 2024). (2) Another safety concern is the prompt extraction
attack (Yu et al., 2023; Wang et al., 2023; Zhang et al., 2024), which is more related to privacy. In this
type of attack, the attacker’s goal is to maliciously obtain information from the system prompt, which
is usually considered confidential. (3) Lastly, we consider harmful requests (Ganguli et al., 2022;
Perez et al., 2022; Souly et al., 2024; Xie et al., 2024), where the prompts attempt to circumvent
safety guidelines and elicit responses involving unsafe behavior, such as instructions for stealing
someone’s identity.
Improving LLM robustness. To mitigate these attacks, researchers have developed two major
defense strategies: prompt-based and learning-based defenses. Prompt-based defenses construct
special instructions (e.g., in-context exemplars or delimiters) to mitigate attacks during inference
(Wei et al., 2023; Hines et al., 2024; Zverev et al., 2024). While these defenses can achieve high
robustness against specific attacks, concerns exist regarding their potential utility drops. Learning-
based defenses (Piet et al., 2023; Chen et al., 2024; Wallace et al., 2024) aim to enhance model
robustness by fine-tuning the models with a dataset of malicious instructions combined with robust
responses. In this work, we explore another approach to improving model robustness by modifying
the embedding approach, which is orthogonal to all previous mitigation strategies.
Embedding and architecture of LLMs. Recent research has also focused on improving the LLM
embeddings and architectural designs to tackle different challenges. For instance, Yen et al. (2024)
proposed a method for enhancing long-context generalization by using a small encoder to process
long inputs in chunks. Additionally, McLeish et al. (2024) introduced the Abacus embedding to
improve model performance on arithmetic tasks. In contrast, this paper focuses primarily on enabling
the model to learn the instruction hierarchy through Instructional Segment Embedding, as inspired by
previous work on designing BERT (Lan et al., 2019) and LinkBERT (Yasunaga et al., 2022).


8    D ISCUSSION AND C ONCLUSION

Limitations and future work directions. This study primarily focused on the supervised fine-tuning
phase, using single-turn conversations. Future work could explore incorporating ISE during the
pre-training or RLHF stage and applying it to multi-turn conversation datasets. Additionally, while
our approach significantly improves the instruction hierarchy capabilities of LLMs, it offers limited
robustness against adaptive attacks, commonly referred to as jailbreaks (see Appendix F for more
discussion). However, integrating our method with established adversarial training strategies may
potentially enhance the robustness. Lastly, our experiments were limited to smaller models with 8B
and 13B parameters and datasets less than 300K. It remains to be investigated whether our results can
be generalized to larger models and datasets, which could provide deeper insights into the scalability
of our proposed methods.
Conclusion. In this work, we introduced the Instructional Segment Embedding as the first attempt to
design novel architectures to enhance instruction hierarchy. We conducted comprehensive experiments
to demonstrate its effectiveness in improving robustness and general capabilities.


                                                   10
Published as a assemblage paper at ICLR 2025




9   E THICS AND R EPRODUCIBILITY S TATEMENT
Ethics. Our research employs publicly available datasets for experiments and utilizes safety-aligned
GPT-4o to generate some training data and judge the performance. We anticipate no ethical concerns
with our methodology. Furthermore, we expect our work to have a positive societal impact, as we
propose an embedding method to enhance model robustness against various malicious instructions.
Reproducibility. We discuss how we generate data in Section 5.1 and Appendix B. The process
of training the model and inference is detailed in Section 5.2. The evaluation data is explained in
Section 5.3 and Appendix C. Additionally, we provide a code snippet to implement our method in
Appendix A. We release our code at https://github.com/tongwu2020/ISE.

ACKNOWLEDGMENT
We would like to thank Jiachen T. Wang and Feiran Jia for providing feedback on our early draft.
Prateek was supported in part by the National Science Foundation under grant CNS-2131938 and the
Princeton SEAS Innovation Grant.

R EFERENCES
Abacus.AI. Systemchat-1.1, 2023. URL https://huggingface.co/datasets/abacusai/
  SystemChat-1.1. Accessed: August 23, 2024.
Mahyar Abbasian, Iman Azimi, Amir M. Rahmani, and Ramesh Jain. Conversational health agents: A
 personalized llm-powered agent framework, 2024. URL https://arxiv.org/abs/2310.02374.
Maksym Andriushchenko, Francesco Croce, and Nicolas Flammarion. Jailbreaking leading safety-
 aligned llms with simple adaptive attacks. arXiv preprint arXiv:2404.02151, 2024.
Cem Anil, Esin Durmus, Mrinank Sharma, Joe Benton, Sandipan Kundu, Joshua Batson, Nina
  Rimsky, Meg Tong, Jesse Mu, Daniel Ford, et al. Many-shot jailbreaking, 2024. Preprint.
Anthropic. The claude 3 model family: Opus, sonnet, haiku, 2024. 2024c.
Yuntao Bai, Andy Jones, Kamal Ndousse, Amanda Askell, Anna Chen, Nova DasSarma, Dawn Drain,
  Stanislav Fort, Deep Ganguli, Tom Henighan, et al. Training a helpful and harmless assistant with
  reinforcement learning from human feedback. arXiv preprint arXiv:2204.05862, 2022.
Patrick Chao, Alexander Robey, Edgar Dobriban, Hamed Hassani, George J. Pappas, and Eric Wong.
  Jailbreaking black box large language models in twenty queries. In R0-FoMo:Robustness of
  Few-shot and Zero-shot Learning in Large Foundation Models, 2023. URL https://openreview.
  net/forum?id=rYWD5TMaLj.
Sizhe Chen, Julien Piet, Chawin Sitawarin, and David Wagner. Struq: Defending against prompt injec-
  tion with structured queries. ArXiv, abs/2402.06363, 2024. URL https://api.semanticscholar.
  org/CorpusID:267616771.
Edoardo Debenedetti, Jie Zhang, Mislav Balunović, Luca Beurer-Kellner, Marc Fischer, and Florian
  Tramèr. Agentdojo: A dynamic environment to evaluate attacks and defenses for llm agents, 2024.
Jacob Devlin, Ming-Wei Chang, Kenton Lee, and Kristina Toutanova. Bert: Pre-training of deep bidi-
  rectional transformers for language understanding. In North American Chapter of the Association
  for Computational Linguistics, 2019. URL https://api.semanticscholar.org/CorpusID:
  52967399.
Ning Ding, Yulin Chen, Bokai Xu, Yujia Qin, Zhi Zheng, Shengding Hu, Zhiyuan Liu, Maosong
  Sun, and Bowen Zhou. Enhancing chat language models by scaling high-quality instructional
  conversations. arXiv preprint arXiv:2305.14233, 2023.
Wensheng Gan, Zhenlian Qi, Jiayang Wu, and Jerry Chun-Wei Lin. Large language models in educa-
 tion: Vision and opportunities. In 2023 IEEE International Conference on Big Data (BigData), pp.
 4776–4785, 2023. doi:10.1109/BigData59044.2023.10386291.


                                                11
Published as a assemblage paper at ICLR 2025




Deep Ganguli, Liane Lovitt, John Kernion, Amanda Askell, Yuntao Bai, Saurav Kadavath, Benjamin
  Mann, Ethan Perez, Nicholas Schiefer, Kamal Ndousse, Andy Jones, Sam Bowman, Anna Chen,
  Tom Conerly, Nova Dassarma, Dawn Drain, Nelson Elhage, Sheer El-Showk, Stanislav Fort,
  Zachary Dodds, Tom Henighan, Danny Hernandez, Tristan Hume, Josh Jacobson, Scott Johnston,
  Shauna Kravec, Catherine Olsson, Sam Ringer, Eli Tran-Johnson, Dario Amodei, Tom B. Brown,
  Nicholas Joseph, Sam McCandlish, Christopher Olah, Jared Kaplan, and Jack Clark. Red teaming
  language models to reduce harms: Methods, scaling behaviors, and lessons learned. ArXiv,
  abs/2209.07858, 2022. URL https://api.semanticscholar.org/CorpusID:252355458.
Kai Greshake, Sahar Abdelnabi, Shailesh Mishra, Christoph Endres, Thorsten Holz, and Mario Fritz.
  Not what you’ve signed up for: Compromising real-world llm-integrated applications with indirect
  prompt injection. In Proceedings of the 16th ACM Workshop on Artificial Intelligence and Security,
  AISec ’23, pp. 79–90, New York, NY, USA, 2023. Association for Computing Machinery. ISBN
  9798400702600. doi:10.1145/3605764.3623985. URL https://doi.org/10.1145/3605764.
  3623985.
Gururise. AlpacaDataCleaned: Data Cleaning Repository. https://github.com/gururise/
 AlpacaDataCleaned, 2024.
Keegan Hines, Gary Lopez, Matthew Hall, Federico Zarfati, Yonatan Zunger, and Emre Kiciman.
  Defending against indirect prompt injection attacks with spotlighting. ArXiv, abs/2403.14720,
  2024. URL https://api.semanticscholar.org/CorpusID:268667111.
Or Honovich, Thomas Scialom, Omer Levy, and Timo Schick. Unnatural instructions: Tuning
  language models with (almost) no human labor. In Anna Rogers, Jordan Boyd-Graber, and
  Naoaki Okazaki (eds.), Proceedings of the 61st Annual Meeting of the Association for Com-
  putational Linguistics (Volume 1: Long Papers), pp. 14409–14428, Toronto, Canada, July
  2023. Association for Computational Linguistics. doi:10.18653/v1/2023.acl-long.806. URL
  https://aclanthology.org/2023.acl-long.806.
Huggingface. System message contradictions sharegpt, 2023. URL https://huggingface.
  co/datasets/NobodyExistsOnTheInternet/SystemMessageContradictionsSharegpt. Ac-
  cessed: August 23, 2024.
Zhenzhong Lan, Mingda Chen, Sebastian Goodman, Kevin Gimpel, Piyush Sharma, and Radu Soricut.
  Albert: A lite bert for self-supervised learning of language representations. In International
  Conference on Learning Representations, 2019.
Xuechen Li, Tianyi Zhang, Yann Dubois, Rohan Taori, Ishaan Gulrajani, Carlos Guestrin, Percy
  Liang, and Tatsunori B. Hashimoto. Alpacaeval: An automatic evaluator of instruction-following
  models. https://github.com/tatsu-lab/alpaca_eval, 5 2023.
Zeyi Liao and Huan Sun. Amplegcg: Learning a universal and transferable generative model of
  adversarial suffixes for jailbreaking both open and closed llms. arXiv preprint arXiv:2404.07921,
  2024.
Chin-Yew Lin. Rouge: A package for automatic evaluation of summaries. In Annual Meeting of the
  Association for Computational Linguistics, 2004. URL https://api.semanticscholar.org/
  CorpusID:964287.
Yi Liu, Gelei Deng, Yuekang Li, Kailong Wang, Zihao Wang, Xiaofeng Wang, Tianwei Zhang,
  Yepang Liu, Haoyu Wang, Yan Zheng, et al. Prompt injection attack against llm-integrated
  applications. arXiv preprint arXiv:2306.05499, 2023.
AI @ Meta Llama Team. The llama 3 herd of models, 2024. URL https://arxiv.org/abs/2407.
  21783.
Sean McLeish, Arpit Bansal, Alex Stein, Neel Jain, John Kirchenbauer, Brian R Bartoldson, Bhavya
  Kailkhura, Abhinav Bhatele, Jonas Geiping, Avi Schwarzschild, et al. Transformers can do
  arithmetic with the right embeddings. arXiv preprint arXiv:2405.17399, 2024.
Norman Mu, Sarah Chen, Zifan Wang, Sizhe Chen, David Karamardian, Lulwa Aljeraisy, Basel
 Alomair, Dan Hendrycks, and David Wagner. Can llms follow simple rules? arXiv, 2023.


                                                12
Published as a assemblage paper at ICLR 2025




OpenAI. Gpt-4o system card, 2023. URL https://cdn.openai.com/gpt-4o-system-card.pdf.
Ethan Perez, Saffron Huang, Francis Song, Trevor Cai, Roman Ring, John Aslanides, Amelia Glaese,
  Nat McAleese, and Geoffrey Irving. Red teaming language models with language models. arXiv
  preprint arXiv:2202.03286, 2022.
Fábio Perez and Ian Ribeiro. Ignore previous prompt: Attack techniques for language models, 2022.
  URL https://arxiv.org/abs/2211.09527.
Julien Piet, Maha Alrashed, Chawin Sitawarin, Sizhe Chen, Zeming Wei, Elizabeth Sun, Basel
  Alomair, and David Wagner. Jatmo: Prompt injection defense by task-specific finetuning. ArXiv,
  abs/2312.17673, 2023. URL https://api.semanticscholar.org/CorpusID:266690784.
Alec Radford, Jeff Wu, Rewon Child, David Luan, Dario Amodei, and Ilya Sutskever. Language
  models are unsupervised multitask learners, 2019.
Reshabh K Sharma, Vinayak Gupta, and Dan Grossman. Spml: A dsl for defending language models
  against prompt attacks, 2024.
Xinyue Shen, Zeyuan Chen, Michael Backes, Yun Shen, and Yang Zhang. "Do Anything Now":
  Characterizing and Evaluating In-The-Wild Jailbreak Prompts on Large Language Models. In
  ACM SIGSAC Conference on Computer and Communications Security (CCS). ACM, 2024.
Abhay Sheshadri, Aidan Ewart, Phillip Guo, Aengus Lynch, Cindy Wu, Vivek Hebbar, Henry Sleight,
  Asa Cooper Stickland, Ethan Perez, Dylan Hadfield-Menell, and Stephen Casper. Targeted latent
  adversarial training improves robustness to persistent harmful behaviors in llms. arXiv preprint
  arXiv:2407.15549, 2024.
Alexandra Souly, Qingyuan Lu, Dillon Bowen, Tu Trinh, Elvis Hsieh, Sana Pandey, Pieter Abbeel,
  Justin Svegliato, Scott Emmons, Olivia Watkins, and Sam Toyer. A strongreject for empty
  jailbreaks, 2024.
Jianlin Su, Murtadha Ahmed, Yu Lu, Shengfeng Pan, Wen Bo, and Yunfeng Liu. Roformer: Enhanced
   transformer with rotary position embedding. Neurocomputing, 568:127063, 2024. ISSN 0925-
   2312. doi:https://doi.org/10.1016/j.neucom.2023.127063. URL https://www.sciencedirect.
   com/science/article/pii/S0925231223011864.
Rohan Taori, Ishaan Gulrajani, Tianyi Zhang, Yann Dubois, Xuechen Li, Carlos Guestrin, Percy
  Liang, and Tatsunori B. Hashimoto. Stanford alpaca: An instruction-following llama model.
  https://github.com/tatsu-lab/stanford_alpaca, 2023.
Hugo Touvron, Louis Martin, Kevin Stone, Peter Albert, Amjad Almahairi, Yasmine Babaei, Nikolay
  Bashlykov, Soumya Batra, Prajjwal Bhargava, Shruti Bhosale, et al. Llama 2: Open foundation
  and fine-tuned chat models. arXiv preprint arXiv:2307.09288, 2023.
Sam Toyer, Olivia Watkins, Ethan Adrian Mendes, Justin Svegliato, Luke Bailey, Tiffany Wang, Isaac
  Ong, Karim Elmaaroufi, Pieter Abbeel, Trevor Darrell, Alan Ritter, and Stuart Russell. Tensor
  trust: Interpretable prompt injection attacks from an online game. In The Twelfth International
  Conference on Learning Representations, 2024. URL https://openreview.net/forum?id=
  fsW7wJGLBd.
Eric Wallace, Kai Xiao, Reimar H. Leike, Lilian Weng, Johannes Heidecke, and Alex Beutel. The
  instruction hierarchy: Training llms to prioritize privileged instructions. ArXiv, abs/2404.13208,
  2024. URL https://api.semanticscholar.org/CorpusID:269294048.
Boxin Wang, Weixin Chen, Hengzhi Pei, Chulin Xie, Mintong Kang, Chenhui Zhang, Chejian Xu,
  Zidi Xiong, Ritik Dutta, Rylan Schaeffer, Sang T. Truong, Simran Arora, Mantas Mazeika, Dan
  Hendrycks, Zinan Lin, Yu Cheng, Sanmi Koyejo, Dawn Song, and Bo Li. Decodingtrust: A
  comprehensive assessment of trustworthiness in GPT models. In Thirty-seventh Conference on
  Neural Information Processing Systems Datasets and Benchmarks Track, 2023. URL https:
  //openreview.net/forum?id=kaHpo8OZw2.
Zeming Wei, Yifei Wang, and Yisen Wang. Jailbreak and guard aligned language models with only
  few in-context demonstrations. arXiv preprint arXiv:2310.06387, 2023.


                                                13
Published as a assemblage paper at ICLR 2025




Tinghao Xie, Xiangyu Qi, Yi Zeng, Yangsibo Huang, Udari Madhushani Sehwag, Kaixuan Huang,
  Luxi He, Boyi Wei, Dacheng Li, Ying Sheng, et al. Sorry-bench: Systematically evaluating large
  language model safety refusal behaviors. arXiv preprint arXiv:2406.14598, 2024.
Shunyu Yao, Howard Chen, John Yang, and Karthik Narasimhan. Webshop: Towards
  scalable real-world web interaction with grounded language agents.  In S. Koyejo,
  S. Mohamed, A. Agarwal, D. Belgrave, K. Cho, and A. Oh (eds.), Advances in Neu-
  ral Information Processing Systems, volume 35, pp. 20744–20757. Curran Associates,
  Inc., 2022.    URL https://proceedings.neurips.cc/paper_files/paper/2022/file/
  82ad13ec01f9fe44c01cb91814fd7b8c-Paper-Conference.pdf.
Michihiro Yasunaga, Jure Leskovec, and Percy Liang. LinkBERT: Pretraining language models with
 document links. In Smaranda Muresan, Preslav Nakov, and Aline Villavicencio (eds.), Proceedings
 of the 60th Annual Meeting of the Association for Computational Linguistics (Volume 1: Long
 Papers), pp. 8003–8016, Dublin, Ireland, May 2022. Association for Computational Linguistics.
 doi:10.18653/v1/2022.acl-long.551. URL https://aclanthology.org/2022.acl-long.551.
Howard Yen, Tianyu Gao, and Danqi Chen. Long-context language modeling with parallel context
  encoding. In Lun-Wei Ku, Andre Martins, and Vivek Srikumar (eds.), Proceedings of the 62nd
 Annual Meeting of the Association for Computational Linguistics (Volume 1: Long Papers), pp.
  2588–2610, Bangkok, Thailand, August 2024. Association for Computational Linguistics. URL
  https://aclanthology.org/2024.acl-long.142.
Jiahao Yu, Yuhang Wu, Dong Shu, Mingyu Jin, and Xinyu Xing. Assessing prompt injection risks in
   200+ custom gpts. arXiv preprint arXiv:2311.11538, 2023.
Qiusi Zhan, Zhixiang Liang, Zifan Ying, and Daniel Kang. Injecagent: Benchmarking indirect prompt
  injections in tool-integrated large language model agents. In Annual Meeting of the Association
  for Computational Linguistics, 2024. URL https://api.semanticscholar.org/CorpusID:
  268248325.
Yiming Zhang, Nicholas Carlini, and Daphne Ippolito. Effective prompt extraction from language
  models. In First Conference on Language Modeling, 2024. URL https://openreview.net/
  forum?id=0o95CVdNuz.
Wenting Zhao, Xiang Ren, Jack Hessel, Claire Cardie, Yejin Choi, and Yuntian Deng. Wildchat:
 1m chatGPT interaction logs in the wild. In The Twelfth International Conference on Learning
 Representations, 2024. URL https://openreview.net/forum?id=Bl8u7ZRlbM.
Lianmin Zheng, Wei-Lin Chiang, Ying Sheng, Siyuan Zhuang, Zhanghao Wu, Yonghao
  Zhuang, Zi Lin, Zhuohan Li, Dacheng Li, Eric Xing, Hao Zhang, Joseph E Gonza-
  lez, and Ion Stoica.       Judging llm-as-a-judge with mt-bench and chatbot arena. In
  A. Oh, T. Naumann, A. Globerson, K. Saenko, M. Hardt, and S. Levine (eds.), Advances
  in Neural Information Processing Systems, volume 36, pp. 46595–46623. Curran Asso-
  ciates, Inc., 2023. URL https://proceedings.neurips.cc/paper_files/paper/2023/file/
  91f18a1287b398d378ef22505bf41832-Paper-Datasets_and_Benchmarks.pdf.
Xiaosen Zheng, Tianyu Pang, Chao Du, Qian Liu, Jing Jiang, and Min Lin. Improved few-shot
  jailbreaking can circumvent aligned language models and their defenses, 2024. URL https:
  //arxiv.org/abs/2406.01288.
Andy Zou, Zifan Wang, Nicholas Carlini, Milad Nasr, J Zico Kolter, and Matt Fredrikson. Universal
  and transferable adversarial attacks on aligned language models. arXiv preprint arXiv:2307.15043,
  2023.
Andy Zou, Long Phan, Justin Wang, Derek Duenas, Maxwell Lin, Maksym Andriushchenko, Rowan
 Wang, Zico Kolter, Matt Fredrikson, and Dan Hendrycks. Improving alignment and robustness
  with circuit breakers. ArXiv, abs/2406.04313, 2024. URL https://api.semanticscholar.org/
  CorpusID:270286008.
Egor Zverev, Sahar Abdelnabi, Mario Fritz, and Christoph H Lampert. Can llms separate instructions
  from data? and what do we even mean by that? arXiv preprint arXiv:2403.06833, 2024.


                                                14
     Published as a assemblage paper at ICLR 2025




     A    D ETAILS OF I MPLEMENTING I NSTRUCTIONAL S EGMENT E MBEDDING
     Here’s an example of implementing Instructional Segment Embedding with a few lines of Python/Py-
     torch code. The additional code is highlighted in bold blue.
     In the init function, we initialize embedding layers, including the token embedding layer, ISE
     embedding layer, and positional embedding layer. The inputs to the function include the embedding
     dimension (embed_size), vocabulary size (vocab_size), and ISE dimension (ISE_size, which
     defaults to 4).
     During inference (the forward function), we compute the token embeddings and ISE embeddings,
     then sum them for further processing. The input x is a list containing the input IDs of each token in
     the sentence, and the input seg is a list containing the segment IDs (e.g., system as 0, user as 1, data
     as 2, output as 3) for each token, with the same size as x.
     Instructional
 1   import torch
 2
 3
 4 class Transformer ( nn . Module ):
 5     def __init__ ( self , embed_size , vocab_size , ISE_size ):
 6         super ( Transformer , self ). __init__ ()
 7         self . token_embedding = nn . Embedding ( vocab_size , embed_size )
 8         # Token embedding layer
 9         self . ISE_embedding = nn . Embedding ( ISE_size , embed_size )
10         # Instructional segment embedding layer
11
12              self . positional_embedding = ...
13              self . layers = ...
14
15
16        def forward ( self , x , seg ):
17            token_embed = self . token_embedding (x)
18            # Convert token indices to token embeddings
19            ISE_embed = self . ISE_embedding ( seg )
20            # Convert instructional segments to Instructional Segment
          Embeddings
21
22              embedding = token_embed + ISE_embed
23
24              x = self . positional_encoding ( embedding )
25
26              for layer in self . layers :
27                  x = layer (x)
28
29              return x




                                                       15
Published as a assemblage paper at ICLR 2025




B     D ETAILS OF T RAINING DATA
In this section, we provide details on how we construct the data, including both the clean and adver-
sarial datasets, to conduct experiments on Structured Query and Instruction Hierarchy benchmarks.

B.1   S TRUCTURED Q UERY BENCHMARK .

For the Clean Alpaca dataset, we use the Alpaca-Cleaned-50K dataset (Taori et al., 2023; Gururise,
2024) to fine-tune the model. There are 32,603 samples that contain data input, and 19,157 samples
do not contain any data input. All of them contain user input. Since the dataset shares the same
system instructions (i.e., “Below is an instruction that describes a task, paired with an input
that provides further context. Write a response that appropriately completes the request.”), we
combine the types of system and user instructions into a single instruction type.
For the Adversarial Alpaca dataset, we follow the approach outlined in Chen et al. (2024) to construct
the dataset. We keep the samples without data input unchanged. Then, the remaining data includes
both clean samples (50%), derived from the Clean Alpaca dataset, and attacked samples (50%), which
involve indirect prompt injection attacks within the data. These attacked samples contain two types
of attacks: the Naive Attack and the Completion-Other Attack. In the Naive Attack, the instruction
from other samples is injected into the data. In the Completion-Other Attack, a fabricated response
is injected first, followed by another set of instructions. The desired output for these adversarial
samples should address only the original user instruction so the output remains the same. We provide
a demonstration in Figure 11.
More details can be found in this StruQ repository.




        Figure 11: A demonstration of how the Adversiaral Alpaca dataset is constructed.

B.2   I NSTRUCTION H IERARCHY BENCHMARK .

We use three different datasets to train models: UltraChat Baseline, System Follow, and Instruction
Hierarchy.
For the UltraChat Baseline dataset, we use the UltraChat-200K dataset (Ding et al., 2023) and employ
GPT-4o to decompose 10K prompts into three components: system instructions, user instructions,
and data inputs. We provided the detailed prompts in Figure 12 and an example of decomposing data


                                                 16
Published as a assemblage paper at ICLR 2025




in Figure 13. This results in approximately 190K plain UltraChat samples and 10K samples with
structured queries. For samples without system instructions, we use the default prompt shown in
Figure 14.




      Figure 12: The prompt of decomposing compositional prompts to structured prompts.




        Figure 13: An example of prompts before and after decomposing using GPT-4o.




          Figure 14: The default system prompt of Instruction Hierarchy benchmark.


For the System Follow dataset, we combine the UltraChat Baseline dataset with two additional
datasets: SystemChat (Abacus.AI, 2023) and SystemMessage (Huggingface, 2023). We use 5K


                                               17
Published as a assemblage paper at ICLR 2025




samples from each of these datasets. All of them do not contain the data part. Additionally, we
observe that the quality of the original responses in SystemChat is relatively low; therefore, we use
GPT-4o to generate high-quality output.
For the Instruction Hierarchy dataset, we include three different types of misaligned data following
Wallace et al. (2024): indirect prompt injection, direct prompt injection, and prompt extraction. (1)
Indirect prompt injection: We use 2K samples from UltraChat and inject instructions from other
samples into the data. The output remains unchanged. (2) Direct prompt injection: We use 2K
SystemChat samples and inject malicious user instructions that attempt to change the original system
instructions. Additionally, we include 200 samples that directly conflict with the system instructions.
The outputs for both parts are generated by GPT-4o. We provide a demonstration of how to prompt
the GPT-4o model to ensure it follows the desired behavior in Figure 15. Additionally, we manually
review a portion of the outputs to verify this. (3) Prompt extraction: We use 200 SystemMessage
samples and inject malicious user instructions that attempt to extract the system message. We also
included 2K samples that used aligned questions, which asked for general information about the
system messages. Again, GPT-4o is used to generate the outputs. For direct prompt injection and
prompt extraction, all injected user instructions are also generated by prompting GPT-4o.




              Figure 15: The prompt of generating desired responses from GPT-4o.




                                                 18
Published as a assemblage paper at ICLR 2025




C     D ETAILS OF E VALUATION

In this section, we provide full details on constructing various attacks to evaluate LLM models.
Specifically, we consider the Structured Query benchmark (Appendix C.1) and the Instruction
Hierarchy benchmark (Appendix C.2). We also explain how we evaluate the model’s instruction-
following capabilities in Appendix C.3.


C.1   E VALUATIONS ON S TRUCTURED Q UERY B ENCHMARK

As we discussed in Section 5.3, we leverage the same evaluation methods from (Chen et al., 2024),
including Naive Attack, Ignore Attack, Escape Separation Attack, and Completion Real Attack, as
shown in Figure 16. We use the test set from AlpacaEval, but only include samples containing valid
data inputs to evaluate the model, resulting in a total of 208 test samples.
These attacks are designed to trick the model into outputting the specific word “hacked”. The
Naive Attack directly requests the model to print “hacked”. The Ignore Attack prompts the model
to disregard all previous instructions and output “hacked” (Perez & Ribeiro, 2022). The Escape
Separation Attack injects special characters to simulate a separation of the previous text, tricking the
model into ignoring prior instructions. Finally, the Completion Real Attack appends a fake response
to the prompt, leading the model to believe the task is complete, after which malicious instructions
are injected for the model to follow.
We also evaluate out-of-domain indirect prompt injection attacks. The key idea is to inject the
adversarial text at the beginning and end of the data input sequence. We present a demonstration in
Figure 17.
For both in-domain and out-of-domain attacks, we evaluate the models using robust accuracy, defined
as the ratio of samples that do not output “hacked”.




Figure 16: A demonstration of in-domain indirect prompt injection attacks on the Alpaca dataset,
including Naive Attack, Ignore Attack, Escape Separation Attack, and Completion Real Attack.


                                                  19
Published as a assemblage paper at ICLR 2025




Figure 17: A demonstration of out-of-domain indirect prompt injection attacks on the Alpaca
dataset, including Naive Attack, Ignore Attack, Escape Separation Attack, and Completion Real
Attack.

C.2   E VALUATIONS ON THE I NSTRUCTION H IERARCHY B ENCHMARK

We evaluate our models on Instruction Hierarchy using four types of attacks: indirect prompt injection,
direct prompt injection, prompt extraction, and harmful requests.
Indirect prompt injection. We use the same evaluations and metrics as those applied in the Structured
Query benchmarks.
Direct prompt injection. We use the same attacking prompts as indirect prompt injection but inject
them directly into the user prompt. Additionally, we use the test set from AlpacaEval without any
data input, which consists of 597 test samples. The evaluation metric remains the same: we calculate
the ratio of samples that do not output “hacked”, and denote this as robustness.
Prompt extraction. We use the ShareGPT and Unnatural Instructions datasets (Honovich et al.,
2023), each consisting of 500 prompts, as described in (Zhang et al., 2024), to serve as the secret
system messages. To perform prompt extraction, we utilize 15 effective prompts selected by the
authors. These prompts are illustrated in Figure 18.
For evaluation metrics, we adopt the approach of Zhang et al. (2024), utilizing an approximate metric
based on ROUGE-L recall (Lin, 2004). This metric computes the length of the longest common
subsequence (LCS) between the extracted system message (e) and the ground truth (t). The resulting
score is the ratio of the LCS length to the length of the ground truth. An attack is considered successful
if this score exceeds 0.9, as presented in Equation 1.
                                                                              
                                             | LCS(tokens(t), tokens(e))|
                      Metric(e, t) = 1                                    ≥ 0.9                        (1)
                                                     | tokens(t)|
Robustness is then evaluated by the proportion of samples that successfully defend against the attack.
Harmful requests. We follow the evaluation approach of Wallace et al. (2024), utilizing prompts
from Jailbreakchat (Chat) and "Do Anything Now" (DAN). These prompts are concatenated with
malicious requests from StrongREJECT (Souly et al., 2024) to create the final harmful prompts.


                                                    20
Published as a assemblage paper at ICLR 2025




           Figure 18: A demonstration of attacking prompts used in prompt extraction.




              Figure 19: A demonstration of evaluation prompts for harmful requests.



The full dataset includes 79 effective attacking prompts from Jailbreakchat (Chat) and 225 from
"Do Anything Now" (DAN), all of which are publicly available. Both Jailbreakchat (Chat) and
"Do Anything Now" (DAN) can be accessed in the repository, sourced from jailbreakchat.com and
ChatGPTJailbreak. Additionally, there are 313 malicious instructions from StrongREJECT. For each
sample, we randomly select one attacking prompt to concatenate with the instruction, resulting in a
dataset of 313 evaluation samples.
For evaluation metrics, we query GPT-4o to determine whether the response adheres to safety
guardrails (i.e., whether the response provides sufficient details to answer malicious requests). The
detailed evaluation prompt is presented in Figure 19, which is similar to that used in (Xie et al., 2024).
Robust accuracy is then computed as the ratio of cases where the model either rejects or does not
provide sufficient detail in response to malicious questions.


C.3   I NSTRUCTION - FOLLOWING E VALUATION

We also evaluate our models using two instruction-following benchmarks: AlpacaEval 1.0 (Li et al.,
2023) and MT-Bench (Zheng et al., 2023). Specifically, we follow the steps of AlpacaEval 1.0 to
assess model performance. For MT-Bench, we evaluate only 1-turn conversations, as our model is
trained for single-turn interactions.


                                                   21
Published as a assemblage paper at ICLR 2025




               Figure 20: A demonstration of prompts for over-refusal evaluation.


C.4   OVER - REFUSAL E VALUATION

For over-refusal evaluation, we query GPT-4o to assess whether the response provides sufficient
details to address benign requests. The detailed evaluation prompt is shown in Figure 20, which is
similar to the prompts used for evaluating harmful request tasks.




                                               22
Published as a assemblage paper at ICLR 2025




D     M ORE E XPERIMENTAL R ESULTS ON S TRUCTURED Q UERY
In this section, we provide a detailed evaluation of additional indirect prompt injection attacks as
constructed by (Chen et al., 2024). Specifically, we evaluate the "Escape deletion" attack, which
injects multiple instances of \b or \r to mimic the deletion of previous characters. We also study 12
other types of completion attacks that attempt to obfuscate the prompt roles using unusual characters,
and further details are in (Chen et al., 2024) and StruQ repository. Additionally, we include the
results of our instructional segment embedding with text delimiters.
As shown in Figures 2 and 3, our ISE with special delimiters consistently outperforms all other
methods in almost all cases. Interestingly, we found that directly using Instructional Segment
Embedding does not improve performance on the Clean Alpaca dataset but generally increases
robustness on the Adversarial Alpaca dataset by up to 4.6% on average and up to 14% for the
in-domain worst robust accuracy compared to the baseline. Therefore, ISE should be used with
special token delimiters to achieve the best performance.


Table 2: Full evaluation results of the LLM on LLAMA-2-13B using in-domain indirect prompt
injection attacks.
Dataset                                        Clean Alpaca                                          Adversarial Alpaca
Method                     Baseline     +ISE (Ours) Delimiter        +ISE (Ours)     Baseline     +ISE (Ours) Delimiter   +ISE (Ours)
AlpacaEval (↑)                72.76           72.13       72.67         72.13          73.41        73.35       72.26        73.76
Naive                         65.87           67.31       68.75         75.96         100.00        100.00       99.04      100.00
Ignore                        57.69           61.06       57.21         70.19         99.52          98.08       99.04       99.04
Escape-deletion               86.54           80.77       83.17         79.81         99.04          99.52       99.04       98.56
Escape-separation             75.00           72.60       69.23         78.85         99.52         100.00       99.52      100.00
Completion-other              10.10           21.15        9.62         43.75         100.00        100.00      100.00      100.00
Completion-othercmb           31.25           30.29       33.65         60.58         100.00        100.00      100.00      100.00
Completion-real                4.81            5.29        7.21         40.38         70.19         81.73       100.00      100.00
Completion-realcmb            26.92           25.96       17.31         48.56         98.08         95.67       100.00      100.00
Completion-close-2hash         5.29            5.29       10.10         45.67         97.60         98.56       100.00      100.00
Completion-close-1hash         9.62            6.25        7.69         36.54         65.38         79.81       100.00      100.00
Completion-close-0hash        11.06            5.77        9.13         47.12         93.27         97.12       100.00      100.00
Completion-close-upper         5.29            6.25        7.21         38.46         93.27         96.15       100.00      100.00
Completion-close-title         5.77            5.77        7.21         27.40         70.19         87.98        99.52      100.00
Completion-close-nospace       6.25            5.77        6.25         38.46         82.69         89.90       100.00      100.00
Completion-close-nocolon       6.25            5.77        8.65         38.46         71.63         89.42       100.00      100.00
Completion-close-typo          7.21            6.25       10.10         50.96         97.12         99.52        99.52      100.00
Completion-close-similar       5.77           5.29        8.65          45.19         91.83         93.75        99.52       99.52
Average                       24.75           24.52       24.77         50.96          89.96        94.60       99.66        99.83
Worst                         4.81            5.29        6.25          27.40          65.38        79.81       98.08        98.56




Table 3: Full evaluation results of the LLM on LLAMA-2-13B using out-of-domain indirect prompt
injection attacks.
Dataset                                 Clean Alpaca                                               Adversarial Alpaca
Method              Baseline     +ISE (Ours) Delimiter            +ISE (Ours)      Baseline     +ISE (Ours) Delimiter     +ISE (Ours)
AlpacaEval (↑)        73.32           72.13           72.67         71.21           73.41         73.35        72.26        72.60
Naive                 62.02           63.46           66.35         69.71           64.90         65.87        67.79        76.44
Ignore                52.40           66.83           51.92         69.71           98.56         96.63        96.15        96.63
Escape-separation     72.12           63.46           71.63         70.67           73.08         74.52        76.44        88.46
Completion-real        1.92            1.92           12.99         34.14           85.58         96.64        91.35        99.52
Average               47.12           48.92           50.72         61.06           80.53         83.41        82.93        90.26
Worst                 1.92            1.92            12.99         34.14           64.90         65.87        67.79        76.44




                                                                   23
Published as a assemblage paper at ICLR 2025




E      M ORE E XPERIMENTAL R ESULTS ON I NSTRUCTION H IERARCHY
In this section, we provide additional experimental results on the Instruction Hierarchy benchmark,
covering indirect prompt injection (Appendix E.1), direct prompt injection (Appendix E.2), prompt
extraction (Appendix E.3), and harmful requests (Appendix E.4). Furthermore, we present the results
for Llama-3.1-8B in Appendix E.5.

E.1      D ETAILED A NALYSIS OF I NDIRECT P ROMPT I NJECTION

In Figure 6, we present the results of both in-domain and out-of-domain attacks. Similar to the
Structured Query benchmark, we evaluate additional in-domain attacks designed by (Chen et al.,
2024), which are shown in Figure 21. Due to space constraints, we use Att to represent different
attacks.
Specifically, Att1 to Att18 correspond to the following list of attacks: Att1:Naive, Att2:Ignore,
Att3:Escape_deletion, Att4:Escape_separation, Att5:Completion_other, Att6:Completion_othercmb,
Att7:Completion_real,             Att8:Completion_realcmb,           Att9:Completion_close_2hash,
Att10:Completion_close_1hash,      Att11:Completion_close_0hash,    Att12:Completion_close_upper,
Att13:Completion_close_title,    Att14:Completion_close_nospace,  Att15:Completion_close_nocolon,
Att16:Completion_close_typo, and Att17:Completion_close_similar.
Again, we observe that our ISE method significantly enhances robustness against almost all attacks.
The average robust accuracy gains range from approximately 15% to 45%, with the worst robust
accuracy gains reaching up to nearly 50%.

                                                                                   UltraChat Baseline
      Baseline 64.4   59.6   84.6     74.5       11.1     34.1   2.4     27.4       5.8           7.2   4.8      2.9          5.8       4.3      3.9     5.8        5.8          23.8   2.4                    100
 +ISE (Ours) 82.2     73.1   82.7     86.5      69.7      74.0   56.7    91.8       51.0         60.6   64.9     59.6         54.8      59.1    53.4     76.0       62.5         68.2   51.0
                                                                                                                                                                                                               80



                                                                                                                                                                                                                    Robustness (%)
                                                                                     System Follow
      Baseline 61.5   53.9   85.6     74.0      26.4      21.1   6.2     21.6       11.5         16.8   6.2      9.1          13.0      3.9      7.7     9.6        17.3         26.2   3.9                    60
 +ISE (Ours) 77.9     71.2   84.1     81.7      69.7      70.2   58.6    84.1       61.5         60.6   49.5     59.1         54.8      61.5    52.4     69.7       65.4         66.6   49.5                   40
                                                                                Instruction Hierarchy
      Baseline 83.7   76.9   91.8     90.9      78.4      78.8   58.6    66.3       56.2         73.6   50.0     61.1         66.3      59.1    55.3     64.9       64.4         69.2   50.0
                                                                                                                                                                                                               20
 +ISE (Ours) 87.0     80.8   86.1     88.5      90.4      88.9   74.0    88.0       81.7         82.7   77.9     80.8         80.3      82.2    76.4     87.5       85.6         83.5   74.0                   0
               Att1   Att2   Att3     Att4      Att5      Att6   Att7   Att8        Att9 Att10 Att11 Att12 Att13 Att14 Att15 Att16 Att17 Average Worst

Figure 21: Full results of in-domain indirect prompt injection attack we evaluated on the Instruction
Hierarchy benchmark.

E.2      D ETAILED A NALYSIS OF D IRECT P ROMPT I NJECTION

In Figure 22, we report the robust accuracy against both in-domain and out-of-domain direct prompt
injection attacks. We observe performance gains for our ISE method across various attack scenarios.
For instance, the average robust accuracy against in-domain attacks improves from 47.3% to 69.9%
for the model trained on the UltraChat Baseline dataset.
Additionally, similar to indirect prompt injection attacks, we also include the full results of in-domain
attacks in Figure 23. The attacking prompts are exactly the same as described in Appendix E.1. These
results further validate the effectiveness of our method, improving the average robust accuracy by
over 10% and the worst robust accuracy by over 20%.
                                                                                    UltraChat Baseline
                  Baseline    62.8       48.2           74.9     3.2       47.3            3.2           56.0          30.6          66.8        0.7       38.5            0.7           100
               +ISE (Ours)    84.1       75.4           85.4     34.7      69.9            34.7          67.0          56.0          74.0       15.4       53.1            15.4
                                                                                                                                                                                         80



                                                                                                                                                                                              Robustness (%)
                                                                                      System Follow
                  Baseline    62.8       42.0           76.2     5.7       46.7            5.7           32.3          29.5          40.7        0.5       25.8            0.5           60
               +ISE (Ours)    75.7       55.8           79.6     33.8       61.2           33.8          48.9          33.0          54.6        7.2       35.9            7.2           40
                                                                                 Instruction Hierarchy
                  Baseline    70.2       67.8           84.9     39.2      65.5            39.2          44.2          61.5          54.3        8.4       42.1            8.4
                                                                                                                                                                                         20
               +ISE (Ours)    82.8       75.2           89.6     45.4      73.2            45.4          60.5          65.5          58.1       14.9       49.8            14.9          0
                              Naive     Ignore      Escape_S Completion_R Average      Worst             Naive      Ignore          Escape_S Completion_R Average         Worst
                                                        In Domain Attacks                                                             Out of Domain Attacks

Figure 22: Results of direct prompt injection attack we evaluated on the Instruction Hierarchy
benchmark.


                                                                                                   24
Published as a assemblage paper at ICLR 2025




                                                                                      UltraChat Baseline
      Baseline 62.8     48.2    83.2     74.9      13.1      32.7      3.2    29.6      5.0      5.2      3.4     4.0     4.4       4.0          3.2          5.0      6.0                22.8    3.2   100
 +ISE (Ours) 84.1       75.4    76.7     85.4      43.0      63.0     34.7    59.8     33.0     34.7      38.9   45.6     37.5     40.2          33.2      58.5        43.9               52.2   33.0
                                                                                                                                                                                                        80



                                                                                                                                                                                                             Robustness (%)
                                                                                         System Follow
      Baseline 62.8     42.0    85.3     76.2      31.7      22.8      5.7    23.1      7.7     12.6      5.2     9.6     9.9       7.7          4.9          7.9      12.7               25.2    4.9   60
 +ISE (Ours) 75.7       55.8    74.7     79.6      52.9      54.6     33.8    48.7     34.8     42.7      39.5   40.5     33.8     40.4          32.5         51.8     46.7               49.3   32.5   40
                                                                                     Instruction Hierarchy
      Baseline 70.2     67.8    86.8     84.9      70.8      75.2     39.2    55.6     44.7     52.3      42.9   38.4     48.2     35.7          30.3      42.7        47.1               54.9   30.3
                                                                                                                                                                                                        20
 +ISE (Ours) 79.4       76.4    82.1     86.9      67.3      90.0     57.0    52.6     59.8     61.3      54.6   67.0     57.6     59.5          53.9      69.3        61.8               66.9   52.6   0
                 Att1   Att2    Att3     Att4      Att5      Att6     Att7    Att8     Att9 Att10 Att11 Att12 Att13 Att14 Att15 Att16 Att17 Average Worst

Figure 23: Full results of in-domain direct prompt injection attack we evaluated on the Instruction
Hierarchy benchmark.


E.3       D ETAILED A NALYSIS OF P ROMPT E XTRACTION

Following Section 6.3, we also present the full results of the prompt extraction on the Unnatural
Instructions dataset. We observe similar trends where adding ISE makes the model more robust
against extraction attacks, potentially enhancing privacy. Notably, the robustness (i.e., the ratio of
cases where the attack fails to extract a significant number of original prompts) improves by over
20% on both average and worst scenarios for the models trained on the UltraChat Baseline.

                                                                                      UltraChat Baseline
      Baseline   64.0    60.2     76.8      63.0          61.4      87.8     97.8      96.6     87.8      76.2     73.4     58.0          95.8          78.2         53.0             75.3       53.0   100
 +ISE (Ours)     97.6    98.8     99.6      95.2          78.6      99.8     99.8      99.6     98.8      98.6     98.8     98.8          99.2          98.6         90.4             96.8       78.6
                                                                                                                                                                                                        80
                                                                                         System Follow


                                                                                                                                                                                                             Robustness (%)
      Baseline   84.0    71.8     77.6      78.6          74.8      82.0     91.8      63.8     89.0      84.2     92.4     79.8          93.4          85.4         59.4             80.5       59.4   60
 +ISE (Ours)     84.8    96.0     95.8      83.6          75.0      98.2     96.6      98.4     96.2      98.0     96.4     94.2          99.8          96.0         70.8             92.0       70.8
                                                                                                                                                                                                        40
                                                                                     Instruction Hierarchy
      Baseline   96.0    61.8     73.4      83.0          67.6      93.8     99.0      86.0     85.4      96.2     95.0     69.8          91.0          82.8         54.6             82.4       54.6   20
 +ISE (Ours)     95.6    90.8     92.6      85.0          64.6      97.6     97.8      99.0     89.8      99.2     96.8     94.0          98.6          93.8         76.2             91.4       64.6   0
                 Att1   Att2      Att3     Att4       Att5          Att6     Att7     Att8      Att9 Att10 Att11 Att12 Att13 Att14 Att15 Average Worst

           Figure 24: Full results of prompt extraction we evaluated on Unnatural Instructions.


E.4       D ETAILED A NALYSIS OF H ARMFUL R EQUESTS

We present the full results from Figure 8 with two more models trained on the System Follow and
Instruction Hierarchy dataset in Figure 25. We continue to observe average robustness improvements
across different categories, especially for the UltraChat Baseline and Instruction Hierarchy datasets.
Note that the model was trained without any data specifically designed to bypass the safety guidelines.

                                                                                         UltraChat Baseline
                                   Baseline          26.0             24.0            28.0         30.5           24.0            22.2                 25.8                 60
                                +ISE (Ours)          44.0             26.0            34.0         39.0           26.0            29.6                 33.1                 50
                                                                                              System Follow


                                                                                                                                                                                Robustness (%)
                                                                                                                                                                            40
                                   Baseline          36.0             42.0            38.0         38.8           38.0            22.6                 35.9
                                                                                                                                                                            30
                                +ISE (Ours)          36.0             44.0            42.0         37.3           38.0            24.1                 36.9
                                                                                                                                                                            20
                                                                                       Instruction Hierarchy
                                   Baseline          40.0             34.0            38.0         32.2           32.0            37.0                 35.5                 10
                                +ISE (Ours)          52.0             42.0            32.0         42.4           48.0            29.6                 41.0                 0
                                                Disinformation Hate Illegal services Crimes                      Sexual         Violence          Average

Figure 25: Full results of the harmful request evaluation on JailbreakChat prompts using StrongRE-
JECT malicious instructions.


E.5       D ETAILED A NALYSIS OF LLAMA 3.1 M ODEL

We then provide a more detailed evaluation of the Llama-3.1-8B model on Instruction Hierarchy
in Figure 26. We continue to observe improved model capability and enhanced robustness across
various attacks, indicating that our method generalizes well to different models. For instance, ISE
consistently improves the winning rate on AlpacaEval and either maintains or improves the score on


                                                                                                  25
Published as a assemblage paper at ICLR 2025




MT-Bench. In terms of robustness, our method also improves performance, even for models trained
on Instruction Hierarchy, which already achieve high robustness.

                                AlpacaEval                                              MT-Bench




                                                    (a) Capability

         #1: Indirect Prompt Injection (ID)   #2: Indirect Prompt Injection (OOD)   #3: Direct Prompt Injection (ID)

         #4: Direct Prompt Injection (OOD)    #5: Prompt Extraction (ShareGPT)      #6: Prompt Extraction (Unnatural)

         #7: Harmful Requests (Chat)          #8: Harmful Requests (DAN)




               UltraChat Baseline                     System Follow                     Instruction Hierarchy

                                                   (b) Robustness

Figure 26: Evaluations on Llama-3.1-8B. The evaluation of model capabilities on the Instruction Hi-
erarchy benchmark is conducted using AlpacaEval and MT-Bench (Figure a). Robustness evaluations
include indirect and direct prompt injection attacks, prompt extraction attacks, and harmful requests
(Figure b). We performed experiments across three training datasets and compared our Instructional
Segment Embedding (ISE) method against the baseline.




                                                              26
Published as a assemblage paper at ICLR 2025




E.6   I NVESTIGATION OF I NSTRUCTIONAL S EGMENT E MBEDDING

In this appendix, we examine the behavior of our ISE embeddings across different scenarios. Specif-
ically, we analyze three settings: omitting the system prompt, using the system prompt with user
embedding, and using the data part with user embedding.
Capability Evaluation. First, we present the results on AlpacaEval as the clean performance in
Table 4 with these three settings.
In general, we observe a slight performance degradation (< 5%) when system prompts are omitted,
particularly for models trained on the Instruction Hierarchy. However, our method largely preserves
instruction-following capability compared to baseline methods. This highlights that the system
prompt plays a more significant role in the ISE models than in the baseline methods.
Next, we assess the performance of system prompts using user embeddings. In this setting, we observe
a noticeable performance degradation (∼15%), which is even greater than when system prompts are
omitted. We attribute this to the system prompts (i.e., Below is an instruction that describes a task,
paired with an input that provides further context. Write a response that appropriately completes the
request.) being mixed with the original user prompts. This makes it challenging for the model to
accurately interpret and follow the intended user prompt, leading to lower-quality responses.
Interestingly, we find that performance remains high when the data part uses user embeddings. The
degradation is less than 2%. We think that this is because some of the training data does not separate
the user and data parts.


Table 4: AlpacaEval evaluation of various configurations with and without Instruction Segment
Embedding (ISE).
Training Data                   UltraChat Baseline       Instruction Follow     Instruction Hierarchy
                              Baseline +ISE (Ours)     Baseline +ISE (Ours)     Baseline +ISE (Ours)
With system prompt             63.18%      64.65%      77.24%       81.82%      79.25%       83.35%
Without system prompt          61.39%      63.50%      75.16%       76.60%      79.47%       78.57%
System using user embedding      —         50.93%        —          66.42%        —          70.90%
Data using user embedding        —         63.34%        —          80.77%        —          83.08%


Robustness Evaluation. We then conduct experiments against indirect prompt injection attacks
(Naive attack) under the same three settings. We present the results in Table 5.
Firstly, we observe that the robustness against indirect prompt injection attacks remains roughly
unchanged when the system prompt is omitted. Our ISE method still demonstrates higher robustness
(10% to 20%) compared to the baseline. Secondly, we evaluate the use of system prompts with user
embeddings and observe a slight performance degradation (<6%). Lastly, we assess the use of data
prompts with user embeddings and find a more noticeable performance degradation (up to 10%).
This result is expected, as adversarial texts (injected into the data part) are more prioritized.


Table 5: Performance of various configurations with and without Instruction Segment Embedding
(ISE) against indirect prompt injection attacks.
Training Data                   UltraChat Baseline       Instruction Follow     Instruction Hierarchy
                              Baseline +ISE (Ours)     Baseline +ISE (Ours)     Baseline +ISE (Ours)
With system prompt             64.42%      82.21%      61.54%       77.88%      83.65%       87.02%
Without system prompt          62.50%      82.69%      64.90%       78.37%      80.77%       88.94%
System using user embedding      —         76.92%        —          75.48%        —          85.58%
Data using user embedding        —         76.44%        —          71.63%        —          76.92%




                                                 27
Published as a assemblage paper at ICLR 2025




E.7   E VALUATION ON AUTOMATIC ATTACKS .

We also conduct experiments to evaluate the effectiveness of our method against indirect prompt
injection attacks using automatically optimized prompts. Specifically, we follow the methodology
outlined in (Chao et al., 2023), which iteratively refines and improves the attacking prompts using
GPT-4o. The goal of these prompts is to mislead the model into generating the word “hacked.” The
results are presented in Table 6.
We observe that our ISE methods consistently demonstrate higher robustness (up to 20%) against
this automatic attack. The improvement is particularly noticeable when the model is trained on the
UltraChat Baseline and Instruction Following datasets. These results align with our findings on other
types of attacks.


      Table 6: Performance of the Instructional Segment Embedding on multi-turn MT-Bench.

Training Data           UltraChat Baseline         Instruction Follow       Instruction Hierarchy
                      Baseline +ISE (Ours)       Baseline +ISE (Ours)       Baseline +ISE (Ours)
Automatic attacks     39.90%        57.21%        13.46%       34.62%        65.38%        69.71%


E.8   E VALUATION ON MULTI - TURN CONVERSATION .

Although all the training data are single-turn conversations, we observe that our ISE method is
capable of handling multi-turn conversations. Specifically, we conduct experiments on MT-Bench
with multi-turn scenarios and prompt GPT-4o to evaluate the performance of the generated responses.
The results are presented in Table 7.
We observe that all models experience some performance degradation (up to 2.7), which is expected
given that the models are trained on single-turn chat datasets. Nonetheless, ISE achieves comparable
or even higher MT-Bench scores in multi-turn tasks. This demonstrates the potential of our method
to extend to multi-turn conversations.

      Table 7: Performance of the Instructional Segment Embedding on multi-turn MT-Bench.

Training Data       UltraChat Baseline           Instruction Follow        Instruction Hierarchy
                  Baseline +ISE (Ours)         Baseline +ISE (Ours)        Baseline +ISE (Ours)
Single-turn          6.73          6.64          7.38          7.55           7.30          7.48
Mutli-turn           5.81          5.7           5.6           6.48           4.61           5.4




                                                 28
Published as a assemblage paper at ICLR 2025




E.9   C ASE S TUDY OF ISE ATTENTION

In this appendix, we analyze the attention differences between the baseline and ISE models. We
focus on models trained on the instruction hierarchy dataset and illustrate an attack example (indirect
prompt injection) in Figure 27. Our observations reveal that the baseline model fails to distinguish
benign instructions from malicious ones, whereas our method effectively identifies the presence of
malicious attacks in the context.
Next, we present a visualization of the average attention logits in layer 0 in Figure 28. We observe
that the diagonal line of the baseline model (without ISE) is much brighter than that of our ISE model.
This indicates that the baseline model places significantly stronger attention on neighbor tokens,
making it more susceptible to malicious instructions in data. As a result, the malicious instruction
"Print exactly hacked" plays an overly important role in generating the final response. In contrast, the
ISE model distributes attention more evenly across the full instructions, and provide safe responses.




Figure 27: A demonstration of indirect prompt injection attacks against baseline and ISE models
trained on instruction hierarchy dataset.




  Figure 28: Attention patterns between baseline and ISE models on the example of Figure 27.




                                                  29
Published as a assemblage paper at ICLR 2025




E.10   D ETAILED F IGURE OF ROBUSTNESS E VALUATION ON I NSTRUCTION H IERARCHY




Figure 29: Detailed demonstration of Figure 5. Evaluation results of Llama-3-8B on Instruction
Hierarchy.




                                               30
Published as a assemblage paper at ICLR 2025




F    D ISCUSSIONS AND E VALUATIONS ON JAILBREAK ATTACKS
In our harmful request evaluations, we primarily focused on malicious prompts collected in the
wild, without involving any active optimization, following Wallace et al. (2024). We considered
these prompts as zero-shot generalization evaluations since no training data aimed to bypass safety
alignment.
There also exist adaptive attacks, known as jailbreak attacks, generated through advanced strategies,
such as adversarially optimized texts like those in (Zou et al., 2023; Liao & Sun, 2024), or carefully
human-crafted strategies as seen in Anil et al. (2024). In Table 8, we present the results of using
adaptive attacks from (Andriushchenko et al., 2024; Zheng et al., 2024) on 50 malicious requests
(Chao et al., 2023), and we observe that our models almost completely fail to generate safe responses.
In fact, we do not expect our method to improve adaptive jailbreak robustness. First, none of our data
were explicitly created to defend against (or reject) jailbreak attacks. Second, while our segment
embedding is designed to differentiate between types of instructions, adversarial texts may directly
target the model. Our method is orthogonal to many robust training methods, such as LAT (Sheshadri
et al., 2024) and circuit breakers (Zou et al., 2024). We leave further exploration of this issue for
future research.

     Table 8: Robust accuracy against adaptive attacks on Instruction Hierarchy benchmark.

                           UltraChat       +ISE         System      +ISE       Instruction      +ISE
                           Baseline       (Ours)        Follow     (Ours)       Hierarchy      (Ours)
Jailbreak attacks (%)         2.0           2.0          0.0        2.0           2.0            4.0




                                                   31
