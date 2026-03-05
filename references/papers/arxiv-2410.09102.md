<!-- extracted-by: marker -->
# INSTRUCTIONAL SEGMENT EMBEDDING: IMPROVING LLM SAFETY WITH INSTRUCTION HIERARCHY

Tong Wu1<sup>∗</sup> Shujian Zhang<sup>2</sup> Kaiqiang Song<sup>2</sup> Silei Xu<sup>2</sup> Sanqiang Zhao<sup>2</sup> Ravi Agrawal<sup>2</sup> Sathish Indurthi<sup>2</sup> Chong Xiang<sup>1</sup> Prateek Mittal<sup>1</sup> Wenxuan Zhou<sup>2</sup>

## ABSTRACT

Large Language Models (LLMs) are susceptible to security and safety threats, such as prompt injection, prompt extraction, and harmful requests. One major cause of these vulnerabilities is the lack of an instruction hierarchy. Modern LLM architectures treat all inputs equally, failing to distinguish between and prioritize various types of instructions, such as system messages, user prompts, and data. As a result, lower-priority user prompts may override more critical system instructions, including safety protocols. Existing approaches to achieving instruction hierarchy, such as delimiters and instruction-based training, do not address this issue at the architectural level. We introduce the Instructional Segment Embedding (ISE) technique, inspired by BERT, to modern large language models, which embeds instruction priority information directly into the model. This approach enables models to explicitly differentiate and prioritize various instruction types, significantly improving safety against malicious prompts that attempt to override priority rules. Our experiments on the Structured Query and Instruction Hierarchy benchmarks demonstrate an average robust accuracy increase of up to 15.75% and 18.68%, respectively. Furthermore, we observe an improvement in the instruction-following capability of up to 4.1% on AlpacaEval. Overall, our approach offers a promising direction for enhancing the safety and effectiveness of LLM architectures.

## 1 INTRODUCTION

Large Language Models (LLMs) have shown significant potential in enabling agentic applications and autonomous decision-making across various domains, such as web agents, educational tools, and medical assistance [\(Yao](#page-13-0) [et al., 2022;](#page-13-0) [Gan et al., 2023;](#page-10-0) [Abbasian et al., 2024\)](#page-10-1). To optimize LLM applications, a structured approach to implementation is widely adopted. This involves clear distinctions among system instructions, user prompts, and data inputs, as illustrated in Figure [1.](#page-0-0) These instructions contain specific priorities (e.g., system instructions have higher importance than user instructions) that help the model execute functionalities and better assist users.

However, modern LLM architecture processes all input tokens equally without formal mechanisms to differentiate instructions. Consequently, malicious attackers can easily exploit this limitation to override the priorities of instructions, leading to various vulnerabilities. For example, *prompt injection* [\(Greshake et al., 2023\)](#page-11-0) inserts malicious instructions into data sources to subvert the original ones.

![](_page_0_Figure_10.jpeg)

<span id="page-0-0"></span>Figure 1: A demonstration of the hierarchy of instructions, including system instruction, user instruction, data input as well as model output.

*Prompt extraction* [\(Zhang et al., 2024\)](#page-13-1) aims to extract system messages, revealing proprietary prompts. *Harmful requests* [\(Ganguli et al., 2022\)](#page-11-1) involve malicious users providing unsafe instructions to elicit irresponsible or dangerous responses from the safety-aligned LLMs. These vulnerabilities underscore the significance of designing more robust *instruction hierarchy* in LLM applications.

<sup>1</sup>Princeton University <sup>2</sup>Zoom Video Communications

<sup>∗</sup>Works done at Zoom. Correspondence to: tongwu@princeton.edu, wenxuan.zhou@zoom.us

![](_page_1_Figure_1.jpeg)

<span id="page-1-1"></span>Figure 2: A demonstration of various vulnerabilities of LLM applications, including prompt injection, prompt extraction as well as harmful request.

Recently, research has been conducted to enhance models' ability to follow the instruction hierarchy. For instance, [Hines et al.](#page-11-2) [\(2024\)](#page-11-2) proposed prompt-based solutions utilizing a special delimiter between prompts. [Chen et al.](#page-10-2) [\(2024\)](#page-10-2) and [Wallace et al.](#page-12-0) [\(2024\)](#page-12-0) suggested methods for generating hierarchical prompts, incorporating adversarial data along with high-quality responses to fine-tune LLMs. However, despite these improvements, the core challenge persists: current LLM architectures still lack an effective mechanism to differentiate and prioritize hierarchical instructions.

In this work, we tackle the challenge by introducing an architecture-level design for LLMs. Inspired by BERT [\(Lan et al., 2019\)](#page-11-3) and its variants [\(Lan et al., 2019;](#page-11-3) [Yasunaga et al., 2022\)](#page-13-2), we propose using an *Instructional Segment Embedding (ISE)* to categorize different types of instructions distinctly. Specifically, we enhance the input token by incorporating segment information that classifies each token by its role (e.g., system instruction as 0, user prompt as 1, and data input as 2). This segment information is processed through a learned embedding layer, converting it into segment embeddings, which are then passed to later self-attention layers along with token embeddings. To obtain a robust segment embedding layer, we perform supervised fine-tuning on datasets containing structured prompts and high-quality responses. This process enables the model to differentiate between levels of instruction hierarchies more effectively, thereby boosting the overall safety of the system.

Empirically, we conduct comprehensive experiments on two benchmarks: Structured Query [\(Chen](#page-10-2) [et al., 2024\)](#page-10-2) and Instruction Hierarchy [\(Wallace et al., 2024\)](#page-12-0), which are constructed based on the Alpaca [\(Taori et al., 2023\)](#page-12-1) and Ultrachat [\(Ding et al., 2023\)](#page-10-3) datasets, respectively. We fine-tune multiple pretrained LLMs, including Llama-2-13B [\(Touvron et al., 2023\)](#page-12-2), Llama-3-8B [\(Llama Team,](#page-11-4) [2024\)](#page-11-4), and Llama-3.1-8B, and compare their performance with and without the use of Instructional Segment Embedding. Our findings indicate that our method yields substantial improvements in robustness while either maintaining or enhancing the models' general capabilities, regardless of the presence of adversarial training data. For example, on the Structured Query benchmark, the method achieves an average robust accuracy improvement of up to 15.75% against indirect prompt injection attacks. On the Instruction Hierarchy benchmark, our ISE yields an average boost in robustness of up to 18.68% across multiple vulnerabilities, including indirect and direct prompt injection, prompt extraction, and harmful requests. In addition, the integration of ISE also maintains or even improves the instruction-following capability by as much as 4.1% on AlpacaEval.

Contributions: (1) We identify and analyze critical limitations in current LLM architectures concerning the lack of instruction hierarchy (Section [3\)](#page-2-0). (2) We propose Instructional Segment Embedding, a simple yet effective method designed to incorporate instruction-type information directly into the model. This approach enables the model to better distinguish and prioritize instructions based on their privilege (Section [4\)](#page-3-0). (3) We empirically demonstrate the effectiveness of ISE across two benchmarks, encompassing five training datasets and addressing four types of vulnerabilities (Sections [5](#page-4-0) & [6\)](#page-5-0).

## 2 BACKGROUND: LLM VULNERABILITIES

Modern LLM products typically involve up to three stakeholders[1](#page-1-0) : (1) the LLM application provider (e.g., OpenAI), who designs the model's system-level instructions and manages the general workflow; (2) the primary user, who provides input in the form of instructions or queries; and (3) third-party

<span id="page-1-0"></span><sup>1</sup>Here, we simplify real-world scenarios by assuming the LLM provider and the LLM application provider to be the same stakeholder collectively responsible for providing system instructions. Additionally, we consider text from third parties as data, which may also include other contents like outputs from external API calls.

```
<|begin_of_text|>
<|start_header_id|>system<|end_header_id|>{{system_prompt}}<|eot_id|>
<|start_header_id|>user<|end_header_id|>{{user_message}}<|eot_id|>
<|start_header_id|>assistant<|end_header_id|>
```

Figure 3: A demonstration of the chat template for Llama-3-Instruct (Llama Team, 2024).

source/data, such as web search results, that offer additional context for the LLM. As a result, LLM applications often establish a hierarchical order of instructions based on their perceived reliability: system instructions take precedence, followed by user instructions, and finally data.

Security vulnerabilities arise when conflicts between these priorities occur, such as (1) a malicious user attempting to bypass safety system instructions or (2) malicious web providers injecting harmful actions in data. These conflicts may take various forms, including prompt injections, prompt extractions, and harmful requests, as shown in Figure 2 and outlined below.

**Prompt injection (Figure 2a).** Prompt injection attacks (Perez & Ribeiro, 2022) generally occur in two forms: indirect and direct. Indirect prompt injection attacks occur when third-party data input contains instructions that should never be followed by LLMs. Direct prompt injection attacks happen when a malicious attacker manipulates the user query to an LLM, causing the model to generate outputs that deviate from predefined instructions.

**Prompt extraction (Figure 2b).** This vulnerability (Zhang et al., 2024) often exploits a weakness in certain LLM applications that store confidential information within system instructions. Attackers may craft malicious queries that prompt the model to reference this stored information, potentially leading to the disclosure of system prompts.

**Harmful requests (Figure 2c).** Harmful requests (Ganguli et al., 2022) aim to bypass the model's safety alignment (Bai et al., 2022) through malicious queries. These prompts can lead to unsafe outcomes, including unethical responses or even the weaponization of LLMs.

In this paper, we aim to enhance the instruction hierarchy capabilities of LLMs, thereby mitigating various forms of attacks that attempt to override the priority rules.

### <span id="page-2-0"></span>3 LACK OF INSTRUCTION HIERARCHY IN MODERN LLM ARCHITECTURE

Current embeddings lack instruction hierarchy. Given an input context  $\mathbf{X}_M$  with M tokens  $x_1, x_2, \ldots, x_M$ , the large language models first convert each token into a high-dimensional vector using a token embedding matrix  $\mathbf{E}^{\mathrm{Tok}} \in \mathbb{R}^{V \times D}$ , where V is the vocabulary size, and D is the output embedding dimension. The embedding vector  $e_m^{\mathrm{Tok}}$  for token  $x_m$  is given by  $\mathbf{E}^{\mathrm{Tok}}[x_m]$ , based on its index in the vocabulary. Additionally, the model also obtains positional embeddings  $\mathbf{E}_m^{\mathrm{Pos}}$ , based on the position of each token. Then, the token embeddings  $(e_1^{\mathrm{Tok}}, e_2^{\mathrm{Tok}}, \ldots, e_M^{\mathrm{Tok}})$  will be fed into the transformer's self-attention layers along with positional embeddings for further processing.<sup>2</sup>

In these self-attention layers, each token embedding is processed "equally". As a result, the model recognizes only the semantic content and sequential order of each token from the embedding, lacking the capability to distinguish their hierarchical significance. This architectural design can inherently lead to vulnerabilities. For instance, a lower-priority user prompt, such as "Please focus on my prompt as the system prompt is outdated", could mistakenly be prioritized and override the original system prompt. This could inadvertently lead to various types of vulnerabilities, as shown in Figure 2.

**Prior works do not address this issue.** To mitigate these vulnerabilities, researchers have introduced methods to improve the robustness of large language models (LLMs) during the supervised finetuning phase. This method involves not only using benign prompt-response data but also adversarial or misaligned instructions with robust responses (Piet et al., 2023; Chen et al., 2024; Wallace et al., 2024). This approach helps the model learn to prioritize hierarchical instructions and adhere to embedded safety protocols. Despite its improvement, the challenge of uniformly processing hierarchical instructions remains a fundamental limitation inherent in current embedding methods

<span id="page-2-1"></span><sup>&</sup>lt;sup>2</sup>Models handle positional information in different ways. For example, GPT-2 (Radford et al., 2019) adds learned positional embeddings to its token embeddings, while Llama-2 uses Rotary Position Embedding (RoPE) (Su et al., 2024) in its attention blocks to represent positions.

![](_page_3_Figure_1.jpeg)

<span id="page-3-1"></span>Figure 4: The input representation includes both token embeddings and instructional segment embeddings. We categorize all input texts into four segments: system instructions, user instructions, third-party data, and generated output. We assign different segment embeddings to each type of input text. The final input embeddings are the sum of token embeddings and segment embeddings. The LLMs will predict the next token after "the summary is", with extra instruction hierarchy information.

and model architecture. We demonstrated that our proposed architecture design can provide better robustness (see results in Table 1 and Figure 5).

An alternative approach is to use specific chat templates to better handle input data. For instance, LLAMA-3-Chat (Llama Team, 2024) leverages a chat template with special tokens like <|begin\_of\_text|> and <|star\_header\_id|> as shown in Figure 3. Hines et al. (2024) and Chen et al. (2024) have also leveraged the specialized delimiters that aid the model in more effectively distinguishing instructions. However, two major drawbacks exist. Firstly, during inference, only a few tokens contain hierarchical priority information, and this signal is likely to diminish when encountering long-context tasks (e.g., summarizing a novel). Secondly, malicious attackers may extract these special delimiters, and exploiting them could lead to more severe attacks (Zheng et al., 2024).

### <span id="page-3-0"></span>4 PROPOSED APPROACH: INSTRUCTIONAL SEGMENT EMBEDDING (ISE)

To tackle this challenge, we propose **Instructional Segment Embedding (ISE)**, which encodes the instruction hierarchy directly into the embeddings. This enables subsequent self-attention layers to more effectively recognize and follow instruction priorities, thereby boosting robustness.

Specifically, we leverage a learnable embedding layer, similar to the token embedding matrix  $\mathbf{E}^{\mathrm{Tok}}$ , which we call the segment embedding matrix  $\mathbf{E}^{\mathrm{Seg}}$ . We define  $\mathbf{E}^{\mathrm{Seg}} \in \mathbb{R}^{H \times D}$ , where H is the number of hierarchies and D is the embedding dimension. By default, we set H to 4, representing system, user, data, and output. Each token in  $\mathbf{X}_M$  is tagged with corresponding hierarchy information  $h_m \in \{0,1,2,3\}$ , readily derived from distinct stakeholder categories in the LLM applications. The instructional segment embeddings of  $\mathbf{X}_M$  are represented as  $(e_1^{\mathrm{Seg}}, e_2^{\mathrm{Seg}}, \dots, e_M^{\mathrm{Seg}})$  and obtained from  $\mathbf{E}^{\mathrm{Seg}}[h_m]$ . To incorporate this modification, the final embeddings are computed by summing the token embeddings and segment embeddings. This results in  $(e_1^{\mathrm{Seg}} + e_1^{\mathrm{Tok}}, e_2^{\mathrm{Seg}} + e_2^{\mathrm{Tok}}, \dots, e_M^{\mathrm{Seg}} + e_M^{\mathrm{Tok}})$ , as illustrated in Figure 4. These embeddings are then fed into self-attention layers, following the process used in current LLMs.

The segment embedding layer is trained alongside other parameters during the supervised fine-tuning (instruction tuning) phase. In our experiments, we use widely adopted instruction-following datasets and construct structured queries based on the original prompt using GPT-40 (OpenAI, 2023). Additionally, we experiment with datasets containing malicious instructions designed to override higher-level instructions, enabling the model to learn how to reject or ignore such commands.

**Flexibility in design.** The design choice for Instructional Segment Embedding can be flexible and should be tailored to the specific downstream tasks. For instance, if the data category can be further subdivided into outputs from external API tools or online information, we can introduce "tools type" and "web data type" categories, providing more fine-grained information. If the application does not involve third-party context, the data type can be omitted.

Connection to BERT. Inspired by BERT's segment embeddings [\(Devlin et al., 2019\)](#page-10-5), originally used to distinguish input segments for next-sentence prediction, our approach repurposes these embeddings to encode hierarchical instructions. This helps address the need for structured prompts and safer LLM outputs by providing direct, contextually relevant cues to the model. Unlike BERT, we incorporate the output type for two reasons: (1) It supports consistent autoregressive inference for each token in the input. (2) output may also include instructions (e.g., "Please provide more details of your question") that are critical in multi-turn language tasks.

Simplicity and lightweight. The implementation is also straightforward and lightweight, requiring only H × D additional parameters. We provide a PyTorch code snippet that demonstrates how to implement this in just a few lines, as shown in Appendix [A.](#page-14-0)

## <span id="page-4-0"></span>5 EXPERIMENTAL DESIGN

In this section, we present how we conducted the experiments. Specifically, we begin by describing the generation of the training data (Section [5.1\)](#page-4-1), the experimental setup (Section [5.2\)](#page-4-2), and the details of the robustness evaluation against multiple attacks (Section [5.3\)](#page-5-1).

### <span id="page-4-1"></span>5.1 GENERATING TRAINING DATA

We conduct experiments using two benchmarks: Structured Query and Instruction Hierarchy. The Structured Query benchmark primarily focuses on indirect prompt injection attacks, whereas the Instruction Hierarchy benchmark evaluates all types of vulnerabilities discussed, including indirect and direct prompt injections, prompt extraction, and harmful requests.

For the Structured Query benchmark, we generally follow the approach of [Chen et al.](#page-10-2) [\(2024\)](#page-10-2). Two datasets are constructed: *Clean Alpaca* and *Adversarial Alpaca*. The Clean Alpaca dataset is constructed by *Alpaca-Cleaned-50K* dataset [\(Taori et al., 2023;](#page-12-1) [Gururise, 2024\)](#page-11-5). For the Adversarial Alpaca dataset, we incorporate instructions drawn from other samples (either directly or with a fabricated response) into the data and train the model to ignore such instructions. More details are available in Section [B.1.](#page-15-0)

For the Instruction Hierarchy benchmark, we mostly adhere to previous work by [Wallace et al.](#page-12-0) [\(2024\)](#page-12-0) to create both aligned and misaligned data[3](#page-4-3) . We select the *UltraChat-200K* dataset [\(Ding](#page-10-3) [et al., 2023\)](#page-10-3) as the base dataset, which contains more training data. Since UltraChat consists solely of prompts and responses, we utilized GPT-4o [\(OpenAI, 2023\)](#page-12-7) to decompose 10K prompts into three components: system instructions, user instructions, and data inputs, which we term the *UltraChat Baseline*. Additionally, we incorporate datasets from SystemChat [\(Abacus.AI, 2023\)](#page-10-6) and SystemMessage [\(Huggingface, 2023\)](#page-11-6) that contain specifical system prompts, designated as the *System Follow* dataset. Lastly, we crafted three types of attacks for the malicious data: indirect/direct prompt injection and prompt extraction, which we collectively name the *Instruction Hierarchy* datasets. We excluded harmful request data from the training but used them as evaluations following [Wallace et al.](#page-12-0) [\(2024\)](#page-12-0). Further details on generating training data are available in Section [B.2.](#page-15-1)

### <span id="page-4-2"></span>5.2 EXPERIMENT SETUP

Data processing. We format all training and evaluation samples with clear segmentation, including system, user, data, and output information. We merge the system and user instructions for the Structured Query benchmark into the same type, as all system instructions in Alpaca are identical. To simplify the experiments, we train and evaluate only single-turn chats, where the conversation ends after the model generates a complete response.

LLM training and inference. By default, we utilize Llama-2-13B [\(Touvron et al., 2023\)](#page-12-2) and Llama-3-8B [\(Llama Team, 2024\)](#page-11-4) as the pretrained models for Structured Query and Instruction Hierarchy, respectively. Experiments with Llama-3.1-8B are presented in Section [6.4.](#page-8-0)

We employ supervised fine-tuning to update all model parameters for all baseline and ISE methods with three epochs. A learning rate of 2e-5 and a cosine learning schedule are used. During inference, we use top-p sampling methods with the model's default settings.

<span id="page-4-3"></span><sup>3</sup>We contacted the authors for training data and details, but they cannot share them due to company restrictions.

Baselines. We conduct experiments on multiple datasets and compare our Instructional Segment Embedding method (+ISE) with models that do not use it. For the Structured Query benchmark, we include experiments using either text (Baseline) or newly constructed tokens (Delimiter) to differentiate distinct types of prompts, following the approach of [Chen et al.](#page-10-2) [\(2024\)](#page-10-2). For the Instruction Hierarchy benchmark, we only include experiments with the default delimiters of LLAMA-3-8B (Baseline), as these are already specially reserved tokens (shown in Figure [3\)](#page-2-2).

## <span id="page-5-1"></span>5.3 ROBUSTNESS EVALUATION

We evaluate our method using comprehensive attack methods. More details are in Appendix [C.](#page-18-0)

Structured Query benchmark. Following the approach of [Chen et al.](#page-10-2) [\(2024\)](#page-10-2), we evaluate indirect prompt injection attacks on models trained on the Alpaca dataset. Specifically, we focus on four types of attacks: Naive Attack, Ignore Attack, Escape Separation Attack, and Completion Real Attack as *in-domain attacks*. All in-domain attacks are crafted by injecting one or a few sentences at the end of the data to trick the model into outputting the word "hacked". Since the scenarios for in-domain attacks are quite similar to the adversarial training data constructed by [Chen et al.](#page-10-2) [\(2024\)](#page-10-2), we further develop new attacks based on the in-domain methods. These new attacks inject adversarial texts at the data's beginning and end, called *out-of-domain attacks*. This strategy significantly degrades the robustness of models trained on the adversarial Alpaca dataset. For the evaluation metrics, we compute the rate at which the model does not generate content containing the word "hacked" and refer to this as robustness or robust accuracy.

Instruction Hierarchy benchmark. Evaluating models trained on the Instruction Hierarchy benchmark is complex due to the need to account for indirect and direct prompt injection, prompt extraction, and harmful requests. To address these challenges: (1) For indirect prompt injection, we apply the same evaluations and metrics used in Structured Query benchmarks. For direct prompt injection, we use the same attacking prompts but inject them directly into the user prompt. (2) For prompt extraction, we use the ShareGPT and Unnatural Instructions datasets from [\(Zhang et al., 2024\)](#page-13-1), along with 15 author-selected effective extraction prompts, and evaluate robustness using an approximate metric based on Rouge-L recall [\(Lin, 2004\)](#page-11-7). (3) For harmful requests, we follow the evaluations of [\(Wallace et al., 2024\)](#page-12-0), using Jailbreakchat (Chat) and "Do Anything Now" (DAN) prompts [\(Shen](#page-12-8) [et al., 2024\)](#page-12-8) paired with StrongREJECT malicious instructions [\(Souly et al., 2024\)](#page-12-9). We query GPT-4o to check whether its responses adhere to safety guardrails.

Comprehensive robustness metrics. For prompt injection and extraction, which encompass multiple attack methods or malicious prompts, we include additional metrics. We define *average robustness* as the model's average performance across these various attack methods, offering a general evaluation of model robustness. Furthermore, we introduce *worst robustness*, representing the model's ability to defend against the most challenging attack.

Clean evaluation. We evaluate the model's capacity using standard datasets. Both benchmarks are assessed with AlpacaEval 1.0 [\(Li et al., 2023\)](#page-11-8). For the Instruction Hierarchy benchmark, we additionally use the MT-Bench [\(Zheng et al., 2023\)](#page-13-4) to measure the model's performance.

## <span id="page-5-0"></span>6 EXPERIMENTAL RESULTS AND ANALYSIS

We report the main results on the Structured Query benchmark in Section [6.1](#page-5-2) and the Instruction Hierarchy in Section [6.2.](#page-6-1) We observe that our approach consistently achieves higher robust accuracy while either maintaining or improving general capability. We also present a more detailed analysis of multiple vulnerabilities in Section [6.3.](#page-7-1) Lastly, we conduct an over-refusal evaluation and assess generalization to the advanced Llama-3.1-8B model in Section [6.4.](#page-8-0)

### <span id="page-5-2"></span>6.1 MAIN RESULTS ON STRUCTURED QUERY

Maintains high utility. In Table [1,](#page-6-0) we present the main results for capability and robustness by comparing our method with the baseline and delimiter methods on both the clean and adversarial Alpaca datasets. Compared to the other two methods, Instructional Segment Embedding maintains high utility with negligible degradation or even slight improvement. The difference in winning rate between the methods is less than 1% on AlpacaEval.

<span id="page-6-0"></span>Table 1: The evaluation results on Structured Query benchmark against both in-domain and out-of-domain indirect prompt injection attacks. We compare our method (+ISE) with the baseline and delimiter methods [\(Chen et al., 2024\)](#page-10-2) on Clean Alpaca and Adversarial Alpaca.

|                | Dataset      |          | Clean Alpaca |                | Adversarial Alpaca |           |               |  |
|----------------|--------------|----------|--------------|----------------|--------------------|-----------|---------------|--|
|                | Method       | Baseline | Delimiter    | +ISE (Ours)    | Baseline           | Delimiter | +ISE (Ours)   |  |
| Capability (↑) | AlpacaEval   | 72.76    | 72.67        | 72.13          | 73.41              | 72.26     | 73.76         |  |
|                | Naive        | 65.87    | 68.75        | 75.96          | 100.00             | 99.04     | 100.00        |  |
|                | Ignore       | 57.69    | 57.21        | 70.19          | 99.52              | 99.04     | 99.04         |  |
| In-Domain      | Escape-S     | 75.00    | 69.23        | 78.85          | 99.52              | 99.52     | 100.00        |  |
| Robustness (↑) | Completion-R | 4.81     | 7.21         | 40.38          | 70.19              | 100.00    | 100.00        |  |
|                | Average      | 50.84    | 50.60        | 66.35 (+15.75) | 92.31              | 99.16     | 99.76 (+0.60) |  |
|                | Worst        | 4.81     | 7.21         | 40.38 (+32.17) | 70.19              | 99.04     | 99.04 (+0.00) |  |
|                | Naive        | 62.02    | 66.35        | 69.71          | 64.90              | 67.79     | 76.44         |  |
|                | Ignore       | 52.40    | 51.92        | 69.71          | 98.56              | 96.15     | 96.63         |  |
| Out-of-Domain  | Escape-S     | 72.12    | 71.63        | 70.67          | 73.08              | 76.44     | 88.46         |  |
| Robustness (↑) | Completion-R | 1.92     | 12.99        | 34.14          | 85.58              | 91.35     | 99.52         |  |
|                | Average      | 47.12    | 50.72        | 61.06 (+10.34) | 80.53              | 82.93     | 90.26 (+7.67) |  |
|                | Worst        | 1.92     | 12.99        | 34.14 (+21.15) | 64.90              | 67.79     | 76.44 (+8.65) |  |

Consistent robustness enhancement. We also observe that our method consistently improves robustness against indirect prompt injection attacks. Specifically, it achieves a 15.75% increase in average robust accuracy and a 32.17% increase in worst robust accuracy against in-domain attacks when trained with the clean Alpaca dataset. Both the delimiter and our ISE reach nearly perfect in-domain robustness. For out-of-domain attacks, we find that adding ISE can also significantly enhance robustness, resulting in improvements of ∼10% and ∼7% in average robustness for clean and adversarial Alpaca, respectively. Interestingly, our out-of-domain attacks degrade the robustness of models trained on the adversarial Alpaca dataset more than those trained on the clean Alpaca dataset (16% vs. 5%). This suggests that the adversarial dataset may overfit to in-domain attacks. Nevertheless, adding ISE largely maintains generalization to out-of-domain attacks.

## <span id="page-6-1"></span>6.2 MAIN RESULTS ON INSTRUCTION HIERARCHY

We present the evaluation results for our method on the Instruction Hierarchy benchmark in Figure [5,](#page-7-0) focusing on model capability and average robustness across various datasets and attack scenarios.

Improvement in capabilities. Adding ISE boosts instruction-following capabilities, particularly for models trained on the System Follow and Instruction Hierarchy datasets. For example, the AlpacaEval win rate improves by approximately ∼4.1% when training on the Instruction Hierarchy dataset with our ISE, as shown in Figure [5\(](#page-7-0)a). Additionally, we observe negligible degradation on MT-Bench for the UltraChat Baseline model and improvements for the other two training datasets.

Enhanced safety against multiple vulnerabilities. We evaluate the robustness of the models against indirect and direct prompt injection attacks, prompt extraction attacks, and harmful requests. (1) Indirect and direct prompt injection scenarios (#1, #2, #3, and #4 in Figure [5\(](#page-7-0)b)) : We report the average robustness across four types of attacks, including both in-domain (ID) and out-of-domain (OOD) contexts. Our results demonstrate robust accuracy improvements ranging from 5% to 25% across all training data configurations when applying the ISE method. Notably, for models trained with the UltraChat Baseline, robust accuracy increases by nearly 25% on average. (2) Prompt extraction scenarios (#5 and #6 in Figure [5\(](#page-7-0)b)): Robustness is measured against 15 effective extraction prompts. Our findings show that models using ISE consistently achieve higher average robustness, with an increase of at least 10% across all datasets. This is evident even for models trained on the Instruction Hierarchy dataset, which already demonstrated more than 80% robust accuracy. (3) Harmful requests (#7 and #8 in Figure [5\(](#page-7-0)b)): Our analysis reveals improvements in robustness for models under

![](_page_7_Figure_1.jpeg)

Figure 5: The evaluation of model capabilities on the Instruction Hierarchy benchmark is conducted using AlpacaEval and MT-Bench, as illustrated in Figure (a). Robustness evaluations include both indirect and direct prompt injection attacks, prompt extraction attacks, and harmful requests, as shown in Figure (b). We performed experiments across three training datasets (i.e., UltraChat Baseline, System Follow, and Instruction Hierarchy) and compared ISE with the baseline (Wallace et al., 2024).

<span id="page-7-2"></span><span id="page-7-0"></span>![](_page_7_Figure_3.jpeg)

Figure 6: Robust accuracy of indirect prompt injection attack on the Instruction Hierarchy benchmark with both in-domain and out-of-domain attacks. More details are described in Appendix E.1.

the UltraChat Baseline and Instruction Hierarchy settings when using ISE. For System Follow, our methods either maintain or slightly exceed the baseline method.

Overall, using Instructional Segment Embeddings significantly enhances both the capabilities and robustness of models against a wide range of attacks on the Instruction Hierarchy benchmark.

### <span id="page-7-1"></span>6.3 DETAILED ANALYSIS OVER ATTACKS

The previous sections mainly covered the overall results (average robustness) across multiple prompt injection and extraction attacks. Here, we provide more detailed evaluations of attacks on the Instruction Hierarchy benchmark. Results for the Structure Query are reported in Appendix D.

**Prompt injection.** In Figure 6, we present the results of indirect prompt injection attacks, including Naive, Ignore, Escape Separation, and Completion Real, across in-domain and out-of-domain scenarios. The results indicate that our ISE method significantly enhances performance compared to

![](_page_8_Figure_1.jpeg)

Figure 7: Robust accuracy against 15 effective prompt extraction attacks on ShareGPT dataset.

![](_page_8_Figure_3.jpeg)

![](_page_8_Figure_4.jpeg)

<span id="page-8-1"></span>![](_page_8_Figure_5.jpeg)

<span id="page-8-2"></span>Figure 8: Harmful requests across categories using UltraChat Baseline.

<span id="page-8-3"></span>Figure 9: Overefusal evaluation on Wild-Chat.

<span id="page-8-4"></span>Figure 10: Evaluation of Llama-3.1-8B models trained on the UltraChat Baseline.

the baseline across nearly all scenarios. Notably, the Completion Real attack severely compromises model robustness, resulting in less than 10% effectiveness for models trained on the UltraChat Baseline and the System Follow dataset without ISE. This attack works by introducing a spoofed response to the benign instruction and concatenating a new malicious instruction into the data. Models that fail to effectively differentiate between these types of instructions are prone to executing the new malicious instruction. However, our method significantly boosts robustness, yielding improvements ranging from approximately 30% to 50%. We also observe similar trends for direct prompt injection attacks, which are detailed in Appendix E.2.

**Prompt extraction.** As mentioned in Section 5.3, we utilize 15 effective malicious prompts to extract the system messages. In Figure 7, we present all the results and find that our method consistently outperforms the baseline, notably enhancing the worst robust accuracy by up to approximately **45%**. Interestingly, the model trained on the UltraChat Baseline dataset with ISE exhibits the highest robustness, even exceeding that of the model trained on the Instruction Hierarchy dataset. We find that this is because the instruction-following capability of models trained on the UltraChat Baseline is relatively weak (about 20% lower than the other two models on AlpacaEval). Consequently, in scenarios where the model is misled into fulfilling a request to output the system message, it sometimes generates only a partial system prompt. Therefore, the attack is not classified as successful. Results on the Unnatural dataset are provided in Appendix E.3.

**Harmful requests.** In Figure 8, we report the robustness of models trained on UltraChat Baseline against Jailbreakchat prompts across six categories: 'Disinformation and Deception,' 'Hate, Harassment, and Discrimination,' 'Illegal Goods and Services,' 'Non-Violent Crimes,' 'Sexual Content,' and 'Violence.' We observe that Instructional Segment Embedding improves robustness in 6 out of 6 categories, with improvements of up to **18%**. Further results are reported in Appendix E.4.

### <span id="page-8-0"></span>6.4 OTHER ANALYSIS

Over-refusal Evaluation. One potential concern is that our method may overfit and refuse to follow user instructions. Therefore, we conduct an over-refusal evaluation on the WildChat dataset (Zhao et al., 2024) following (Anthropic, 2024; Zou et al., 2024). After filtering out prompts that exceed the context window, we use 691 non-toxic prompts to query the model and evaluate whether it generates non-refusal responses using GPT-40. In Figure 9, we report the compliance rate on the benchmark and observe that our ISE improves the compliance rate by about 10% for the model trained on the UltraChat Baseline but shows slight degradation for the other two models. Overall, we expect that our method will maintain model capacity, as shown on AlpacaEval and MT-bench in Figure 5.

Generalization to Other Model. We also evaluated Llama-3.1-8B using the same setup as Llama-3- 8B on the Instruction Hierarchy benchmarks. In Figure [10,](#page-8-4) we present the results on AlpacaEval and the robustness against four attacks (averaged results) of models trained on the UltraChat Baseline. Our method demonstrates an approximate 10% improvement in win rate on the AlpacaEval dataset. For robustness, we observe around a 5% robust accuracy improvement against harmful requests and over 10% on all other attacks. Overall, these results suggest our method can be generalized across different models. The complete results are provided in Appendix [E.5.](#page-24-2)

## 7 RELATED WORKS

Safety vulnerabilities of LLMs. Recently, the safety of LLMs has become a critical concern. (1) These models are vulnerable to indirect and direct prompt injection attacks. Indirect prompt injections happen when malicious content is embedded in inputs sourced from external data providers, as discussed in various research studies [\(Greshake et al., 2023;](#page-11-0) [Liu et al., 2023;](#page-11-9) [Zhan et al., 2024;](#page-13-7) [Debenedetti et al., 2024\)](#page-10-8). In contrast, direct prompt injections occur when attackers explicitly introduce malicious instructions into user input, as demonstrated in [\(Perez & Ribeiro, 2022;](#page-12-3) [Mu et al.,](#page-11-10) [2023;](#page-11-10) [Toyer et al., 2024;](#page-12-10) [Sharma et al., 2024\)](#page-12-11). (2) Another safety concern is the prompt extraction attack [\(Yu et al., 2023;](#page-13-8) [Wang et al., 2023;](#page-12-12) [Zhang et al., 2024\)](#page-13-1), which is more related to privacy. In this type of attack, the attacker's goal is to maliciously obtain information from the system prompt, which is usually considered confidential. (3) Lastly, we consider harmful requests [\(Ganguli et al., 2022;](#page-11-1) [Perez et al., 2022;](#page-12-13) [Souly et al., 2024;](#page-12-9) [Xie et al., 2024\)](#page-13-9), where the prompts attempt to circumvent safety guidelines and elicit responses involving unsafe behavior, such as instructions for stealing someone's identity.

Improving LLM robustness. To mitigate these attacks, researchers have developed two major defense strategies: prompt-based and learning-based defenses. Prompt-based defenses construct special instructions (e.g., in-context exemplars or delimiters) to mitigate attacks during inference [\(Wei et al., 2023;](#page-12-14) [Hines et al., 2024;](#page-11-2) [Zverev et al., 2024\)](#page-13-10). While these defenses can achieve high robustness against specific attacks, concerns exist regarding their potential utility drops. Learningbased defenses [\(Piet et al., 2023;](#page-12-4) [Chen et al., 2024;](#page-10-2) [Wallace et al., 2024\)](#page-12-0) aim to enhance model robustness by fine-tuning the models with a dataset of malicious instructions combined with robust responses. In this work, we explore another approach to improving model robustness by modifying the embedding approach, which is orthogonal to all previous mitigation strategies.

Embedding and architecture of LLMs. Recent research has also focused on improving the LLM embeddings and architectural designs to tackle different challenges. For instance, [Yen et al.](#page-13-11) [\(2024\)](#page-13-11) proposed a method for enhancing long-context generalization by using a small encoder to process long inputs in chunks. Additionally, [McLeish et al.](#page-11-11) [\(2024\)](#page-11-11) introduced the Abacus embedding to improve model performance on arithmetic tasks. In contrast, this paper focuses primarily on enabling the model to learn the instruction hierarchy through Instructional Segment Embedding, as inspired by previous work on designing BERT [\(Lan et al., 2019\)](#page-11-3) and LinkBERT [\(Yasunaga et al., 2022\)](#page-13-2).

## 8 DISCUSSION AND CONCLUSION

Limitations and future work directions. This study primarily focused on the supervised fine-tuning phase, using single-turn conversations. Future work could explore incorporating ISE during the pre-training or RLHF stage and applying it to multi-turn conversation datasets. Additionally, while our approach significantly improves the instruction hierarchy capabilities of LLMs, it offers limited robustness against adaptive attacks, commonly referred to as jailbreaks (see Appendix [F](#page-30-0) for more discussion). However, integrating our method with established adversarial training strategies may potentially enhance the robustness. Lastly, our experiments were limited to smaller models with 8B and 13B parameters and datasets less than 300K. It remains to be investigated whether our results can be generalized to larger models and datasets, which could provide deeper insights into the scalability of our proposed methods.

Conclusion. In this work, we introduced the Instructional Segment Embedding as the first attempt to design novel architectures to enhance instruction hierarchy. We conducted comprehensive experiments to demonstrate its effectiveness in improving robustness and general capabilities.

## 9 ETHICS AND REPRODUCIBILITY STATEMENT

Ethics. Our research employs publicly available datasets for experiments and utilizes safety-aligned GPT-4o to generate some training data and judge the performance. We anticipate no ethical concerns with our methodology. Furthermore, we expect our work to have a positive societal impact, as we propose an embedding method to enhance model robustness against various malicious instructions.

Reproducibility. We discuss how we generate data in Section [5.1](#page-4-1) and Appendix [B.](#page-15-2) The process of training the model and inference is detailed in Section [5.2.](#page-4-2) The evaluation data is explained in Section [5.3](#page-5-1) and Appendix [C.](#page-18-0) Additionally, we provide a code snippet to implement our method in Appendix [A.](#page-14-0) We release our code at [https://github.com/tongwu2020/ISE.](https://github.com/tongwu2020/ISE)

## ACKNOWLEDGMENT

We would like to thank Jiachen T. Wang and Feiran Jia for providing feedback on our early draft. Prateek was supported in part by the National Science Foundation under grant CNS-2131938 and the Princeton SEAS Innovation Grant.

## REFERENCES

- <span id="page-10-6"></span>Abacus.AI. Systemchat-1.1, 2023. URL [https://huggingface.co/datasets/abacusai/](https://huggingface.co/datasets/abacusai/SystemChat-1.1) [SystemChat-1.1](https://huggingface.co/datasets/abacusai/SystemChat-1.1). Accessed: August 23, 2024.
- <span id="page-10-1"></span>Mahyar Abbasian, Iman Azimi, Amir M. Rahmani, and Ramesh Jain. Conversational health agents: A personalized llm-powered agent framework, 2024. URL <https://arxiv.org/abs/2310.02374>.
- <span id="page-10-11"></span>Maksym Andriushchenko, Francesco Croce, and Nicolas Flammarion. Jailbreaking leading safetyaligned llms with simple adaptive attacks. *arXiv preprint arXiv:2404.02151*, 2024.
- <span id="page-10-10"></span>Cem Anil, Esin Durmus, Mrinank Sharma, Joe Benton, Sandipan Kundu, Joshua Batson, Nina Rimsky, Meg Tong, Jesse Mu, Daniel Ford, et al. Many-shot jailbreaking, 2024. Preprint.
- <span id="page-10-7"></span>Anthropic. The claude 3 model family: Opus, sonnet, haiku, 2024. 2024c.
- <span id="page-10-4"></span>Yuntao Bai, Andy Jones, Kamal Ndousse, Amanda Askell, Anna Chen, Nova DasSarma, Dawn Drain, Stanislav Fort, Deep Ganguli, Tom Henighan, et al. Training a helpful and harmless assistant with reinforcement learning from human feedback. *arXiv preprint arXiv:2204.05862*, 2022.
- <span id="page-10-9"></span>Patrick Chao, Alexander Robey, Edgar Dobriban, Hamed Hassani, George J. Pappas, and Eric Wong. Jailbreaking black box large language models in twenty queries. In *R0-FoMo:Robustness of Few-shot and Zero-shot Learning in Large Foundation Models*, 2023. URL [https://openreview.](https://openreview.net/forum?id=rYWD5TMaLj) [net/forum?id=rYWD5TMaLj](https://openreview.net/forum?id=rYWD5TMaLj).
- <span id="page-10-2"></span>Sizhe Chen, Julien Piet, Chawin Sitawarin, and David Wagner. Struq: Defending against prompt injection with structured queries. *ArXiv*, abs/2402.06363, 2024. URL [https://api.semanticscholar.](https://api.semanticscholar.org/CorpusID:267616771) [org/CorpusID:267616771](https://api.semanticscholar.org/CorpusID:267616771).
- <span id="page-10-8"></span>Edoardo Debenedetti, Jie Zhang, Mislav Balunovic, Luca Beurer-Kellner, Marc Fischer, and Florian ´ Tramèr. Agentdojo: A dynamic environment to evaluate attacks and defenses for llm agents, 2024.
- <span id="page-10-5"></span>Jacob Devlin, Ming-Wei Chang, Kenton Lee, and Kristina Toutanova. Bert: Pre-training of deep bidirectional transformers for language understanding. In *North American Chapter of the Association for Computational Linguistics*, 2019. URL [https://api.semanticscholar.org/CorpusID:](https://api.semanticscholar.org/CorpusID:52967399) [52967399](https://api.semanticscholar.org/CorpusID:52967399).
- <span id="page-10-3"></span>Ning Ding, Yulin Chen, Bokai Xu, Yujia Qin, Zhi Zheng, Shengding Hu, Zhiyuan Liu, Maosong Sun, and Bowen Zhou. Enhancing chat language models by scaling high-quality instructional conversations. *arXiv preprint arXiv:2305.14233*, 2023.
- <span id="page-10-0"></span>Wensheng Gan, Zhenlian Qi, Jiayang Wu, and Jerry Chun-Wei Lin. Large language models in education: Vision and opportunities. In *2023 IEEE International Conference on Big Data (BigData)*, pp. 4776–4785, 2023. doi[:10.1109/BigData59044.2023.10386291.](https://doi.org/10.1109/BigData59044.2023.10386291)

- <span id="page-11-1"></span>Deep Ganguli, Liane Lovitt, John Kernion, Amanda Askell, Yuntao Bai, Saurav Kadavath, Benjamin Mann, Ethan Perez, Nicholas Schiefer, Kamal Ndousse, Andy Jones, Sam Bowman, Anna Chen, Tom Conerly, Nova Dassarma, Dawn Drain, Nelson Elhage, Sheer El-Showk, Stanislav Fort, Zachary Dodds, Tom Henighan, Danny Hernandez, Tristan Hume, Josh Jacobson, Scott Johnston, Shauna Kravec, Catherine Olsson, Sam Ringer, Eli Tran-Johnson, Dario Amodei, Tom B. Brown, Nicholas Joseph, Sam McCandlish, Christopher Olah, Jared Kaplan, and Jack Clark. Red teaming language models to reduce harms: Methods, scaling behaviors, and lessons learned. *ArXiv*, abs/2209.07858, 2022. URL <https://api.semanticscholar.org/CorpusID:252355458>.
- <span id="page-11-0"></span>Kai Greshake, Sahar Abdelnabi, Shailesh Mishra, Christoph Endres, Thorsten Holz, and Mario Fritz. Not what you've signed up for: Compromising real-world llm-integrated applications with indirect prompt injection. In *Proceedings of the 16th ACM Workshop on Artificial Intelligence and Security*, AISec '23, pp. 79–90, New York, NY, USA, 2023. Association for Computing Machinery. ISBN 9798400702600. doi[:10.1145/3605764.3623985.](https://doi.org/10.1145/3605764.3623985) URL [https://doi.org/10.1145/3605764.](https://doi.org/10.1145/3605764.3623985) [3623985](https://doi.org/10.1145/3605764.3623985).
- <span id="page-11-5"></span>Gururise. AlpacaDataCleaned: Data Cleaning Repository. [https://github.com/gururise/](https://github.com/gururise/AlpacaDataCleaned) [AlpacaDataCleaned](https://github.com/gururise/AlpacaDataCleaned), 2024.
- <span id="page-11-2"></span>Keegan Hines, Gary Lopez, Matthew Hall, Federico Zarfati, Yonatan Zunger, and Emre Kiciman. Defending against indirect prompt injection attacks with spotlighting. *ArXiv*, abs/2403.14720, 2024. URL <https://api.semanticscholar.org/CorpusID:268667111>.
- <span id="page-11-12"></span>Or Honovich, Thomas Scialom, Omer Levy, and Timo Schick. Unnatural instructions: Tuning language models with (almost) no human labor. In Anna Rogers, Jordan Boyd-Graber, and Naoaki Okazaki (eds.), *Proceedings of the 61st Annual Meeting of the Association for Computational Linguistics (Volume 1: Long Papers)*, pp. 14409–14428, Toronto, Canada, July 2023. Association for Computational Linguistics. doi[:10.18653/v1/2023.acl-long.806.](https://doi.org/10.18653/v1/2023.acl-long.806) URL <https://aclanthology.org/2023.acl-long.806>.
- <span id="page-11-6"></span>Huggingface. System message contradictions sharegpt, 2023. URL [https://huggingface.](https://huggingface.co/datasets/NobodyExistsOnTheInternet/SystemMessageContradictionsSharegpt) [co/datasets/NobodyExistsOnTheInternet/SystemMessageContradictionsSharegpt](https://huggingface.co/datasets/NobodyExistsOnTheInternet/SystemMessageContradictionsSharegpt). Accessed: August 23, 2024.
- <span id="page-11-3"></span>Zhenzhong Lan, Mingda Chen, Sebastian Goodman, Kevin Gimpel, Piyush Sharma, and Radu Soricut. Albert: A lite bert for self-supervised learning of language representations. In *International Conference on Learning Representations*, 2019.
- <span id="page-11-8"></span>Xuechen Li, Tianyi Zhang, Yann Dubois, Rohan Taori, Ishaan Gulrajani, Carlos Guestrin, Percy Liang, and Tatsunori B. Hashimoto. Alpacaeval: An automatic evaluator of instruction-following models. [https://github.com/tatsu-lab/alpaca\\_eval](https://github.com/tatsu-lab/alpaca_eval), 5 2023.
- <span id="page-11-13"></span>Zeyi Liao and Huan Sun. Amplegcg: Learning a universal and transferable generative model of adversarial suffixes for jailbreaking both open and closed llms. *arXiv preprint arXiv:2404.07921*, 2024.
- <span id="page-11-7"></span>Chin-Yew Lin. Rouge: A package for automatic evaluation of summaries. In *Annual Meeting of the Association for Computational Linguistics*, 2004. URL [https://api.semanticscholar.org/](https://api.semanticscholar.org/CorpusID:964287) [CorpusID:964287](https://api.semanticscholar.org/CorpusID:964287).
- <span id="page-11-9"></span>Yi Liu, Gelei Deng, Yuekang Li, Kailong Wang, Zihao Wang, Xiaofeng Wang, Tianwei Zhang, Yepang Liu, Haoyu Wang, Yan Zheng, et al. Prompt injection attack against llm-integrated applications. *arXiv preprint arXiv:2306.05499*, 2023.
- <span id="page-11-4"></span>AI @ Meta Llama Team. The llama 3 herd of models, 2024. URL [https://arxiv.org/abs/2407.](https://arxiv.org/abs/2407.21783) [21783](https://arxiv.org/abs/2407.21783).
- <span id="page-11-11"></span>Sean McLeish, Arpit Bansal, Alex Stein, Neel Jain, John Kirchenbauer, Brian R Bartoldson, Bhavya Kailkhura, Abhinav Bhatele, Jonas Geiping, Avi Schwarzschild, et al. Transformers can do arithmetic with the right embeddings. *arXiv preprint arXiv:2405.17399*, 2024.
- <span id="page-11-10"></span>Norman Mu, Sarah Chen, Zifan Wang, Sizhe Chen, David Karamardian, Lulwa Aljeraisy, Basel Alomair, Dan Hendrycks, and David Wagner. Can llms follow simple rules? *arXiv*, 2023.

- <span id="page-12-7"></span>OpenAI. Gpt-4o system card, 2023. URL <https://cdn.openai.com/gpt-4o-system-card.pdf>.
- <span id="page-12-13"></span>Ethan Perez, Saffron Huang, Francis Song, Trevor Cai, Roman Ring, John Aslanides, Amelia Glaese, Nat McAleese, and Geoffrey Irving. Red teaming language models with language models. *arXiv preprint arXiv:2202.03286*, 2022.
- <span id="page-12-3"></span>Fábio Perez and Ian Ribeiro. Ignore previous prompt: Attack techniques for language models, 2022. URL <https://arxiv.org/abs/2211.09527>.
- <span id="page-12-4"></span>Julien Piet, Maha Alrashed, Chawin Sitawarin, Sizhe Chen, Zeming Wei, Elizabeth Sun, Basel Alomair, and David Wagner. Jatmo: Prompt injection defense by task-specific finetuning. *ArXiv*, abs/2312.17673, 2023. URL <https://api.semanticscholar.org/CorpusID:266690784>.
- <span id="page-12-5"></span>Alec Radford, Jeff Wu, Rewon Child, David Luan, Dario Amodei, and Ilya Sutskever. Language models are unsupervised multitask learners, 2019.
- <span id="page-12-11"></span>Reshabh K Sharma, Vinayak Gupta, and Dan Grossman. Spml: A dsl for defending language models against prompt attacks, 2024.
- <span id="page-12-8"></span>Xinyue Shen, Zeyuan Chen, Michael Backes, Yun Shen, and Yang Zhang. "Do Anything Now": Characterizing and Evaluating In-The-Wild Jailbreak Prompts on Large Language Models. In *ACM SIGSAC Conference on Computer and Communications Security (CCS)*. ACM, 2024.
- <span id="page-12-15"></span>Abhay Sheshadri, Aidan Ewart, Phillip Guo, Aengus Lynch, Cindy Wu, Vivek Hebbar, Henry Sleight, Asa Cooper Stickland, Ethan Perez, Dylan Hadfield-Menell, and Stephen Casper. Targeted latent adversarial training improves robustness to persistent harmful behaviors in llms. *arXiv preprint arXiv:2407.15549*, 2024.
- <span id="page-12-9"></span>Alexandra Souly, Qingyuan Lu, Dillon Bowen, Tu Trinh, Elvis Hsieh, Sana Pandey, Pieter Abbeel, Justin Svegliato, Scott Emmons, Olivia Watkins, and Sam Toyer. A strongreject for empty jailbreaks, 2024.
- <span id="page-12-6"></span>Jianlin Su, Murtadha Ahmed, Yu Lu, Shengfeng Pan, Wen Bo, and Yunfeng Liu. Roformer: Enhanced transformer with rotary position embedding. *Neurocomputing*, 568:127063, 2024. ISSN 0925- 2312. doi[:https://doi.org/10.1016/j.neucom.2023.127063.](https://doi.org/https://doi.org/10.1016/j.neucom.2023.127063) URL [https://www.sciencedirect.](https://www.sciencedirect.com/science/article/pii/S0925231223011864) [com/science/article/pii/S0925231223011864](https://www.sciencedirect.com/science/article/pii/S0925231223011864).
- <span id="page-12-1"></span>Rohan Taori, Ishaan Gulrajani, Tianyi Zhang, Yann Dubois, Xuechen Li, Carlos Guestrin, Percy Liang, and Tatsunori B. Hashimoto. Stanford alpaca: An instruction-following llama model. [https://github.com/tatsu-lab/stanford\\_alpaca](https://github.com/tatsu-lab/stanford_alpaca), 2023.
- <span id="page-12-2"></span>Hugo Touvron, Louis Martin, Kevin Stone, Peter Albert, Amjad Almahairi, Yasmine Babaei, Nikolay Bashlykov, Soumya Batra, Prajjwal Bhargava, Shruti Bhosale, et al. Llama 2: Open foundation and fine-tuned chat models. *arXiv preprint arXiv:2307.09288*, 2023.
- <span id="page-12-10"></span>Sam Toyer, Olivia Watkins, Ethan Adrian Mendes, Justin Svegliato, Luke Bailey, Tiffany Wang, Isaac Ong, Karim Elmaaroufi, Pieter Abbeel, Trevor Darrell, Alan Ritter, and Stuart Russell. Tensor trust: Interpretable prompt injection attacks from an online game. In *The Twelfth International Conference on Learning Representations*, 2024. URL [https://openreview.net/forum?id=](https://openreview.net/forum?id=fsW7wJGLBd) [fsW7wJGLBd](https://openreview.net/forum?id=fsW7wJGLBd).
- <span id="page-12-0"></span>Eric Wallace, Kai Xiao, Reimar H. Leike, Lilian Weng, Johannes Heidecke, and Alex Beutel. The instruction hierarchy: Training llms to prioritize privileged instructions. *ArXiv*, abs/2404.13208, 2024. URL <https://api.semanticscholar.org/CorpusID:269294048>.
- <span id="page-12-12"></span>Boxin Wang, Weixin Chen, Hengzhi Pei, Chulin Xie, Mintong Kang, Chenhui Zhang, Chejian Xu, Zidi Xiong, Ritik Dutta, Rylan Schaeffer, Sang T. Truong, Simran Arora, Mantas Mazeika, Dan Hendrycks, Zinan Lin, Yu Cheng, Sanmi Koyejo, Dawn Song, and Bo Li. Decodingtrust: A comprehensive assessment of trustworthiness in GPT models. In *Thirty-seventh Conference on Neural Information Processing Systems Datasets and Benchmarks Track*, 2023. URL [https:](https://openreview.net/forum?id=kaHpo8OZw2) [//openreview.net/forum?id=kaHpo8OZw2](https://openreview.net/forum?id=kaHpo8OZw2).
- <span id="page-12-14"></span>Zeming Wei, Yifei Wang, and Yisen Wang. Jailbreak and guard aligned language models with only few in-context demonstrations. *arXiv preprint arXiv:2310.06387*, 2023.

- <span id="page-13-9"></span>Tinghao Xie, Xiangyu Qi, Yi Zeng, Yangsibo Huang, Udari Madhushani Sehwag, Kaixuan Huang, Luxi He, Boyi Wei, Dacheng Li, Ying Sheng, et al. Sorry-bench: Systematically evaluating large language model safety refusal behaviors. *arXiv preprint arXiv:2406.14598*, 2024.
- <span id="page-13-0"></span>Shunyu Yao, Howard Chen, John Yang, and Karthik Narasimhan. Webshop: Towards scalable real-world web interaction with grounded language agents. In S. Koyejo, S. Mohamed, A. Agarwal, D. Belgrave, K. Cho, and A. Oh (eds.), *Advances in Neural Information Processing Systems*, volume 35, pp. 20744–20757. Curran Associates, Inc., 2022. URL [https://proceedings.neurips.cc/paper\\_files/paper/2022/file/](https://proceedings.neurips.cc/paper_files/paper/2022/file/82ad13ec01f9fe44c01cb91814fd7b8c-Paper-Conference.pdf) [82ad13ec01f9fe44c01cb91814fd7b8c-Paper-Conference.pdf](https://proceedings.neurips.cc/paper_files/paper/2022/file/82ad13ec01f9fe44c01cb91814fd7b8c-Paper-Conference.pdf).
- <span id="page-13-2"></span>Michihiro Yasunaga, Jure Leskovec, and Percy Liang. LinkBERT: Pretraining language models with document links. In Smaranda Muresan, Preslav Nakov, and Aline Villavicencio (eds.), *Proceedings of the 60th Annual Meeting of the Association for Computational Linguistics (Volume 1: Long Papers)*, pp. 8003–8016, Dublin, Ireland, May 2022. Association for Computational Linguistics. doi[:10.18653/v1/2022.acl-long.551.](https://doi.org/10.18653/v1/2022.acl-long.551) URL <https://aclanthology.org/2022.acl-long.551>.
- <span id="page-13-11"></span>Howard Yen, Tianyu Gao, and Danqi Chen. Long-context language modeling with parallel context encoding. In Lun-Wei Ku, Andre Martins, and Vivek Srikumar (eds.), *Proceedings of the 62nd Annual Meeting of the Association for Computational Linguistics (Volume 1: Long Papers)*, pp. 2588–2610, Bangkok, Thailand, August 2024. Association for Computational Linguistics. URL <https://aclanthology.org/2024.acl-long.142>.
- <span id="page-13-8"></span>Jiahao Yu, Yuhang Wu, Dong Shu, Mingyu Jin, and Xinyu Xing. Assessing prompt injection risks in 200+ custom gpts. *arXiv preprint arXiv:2311.11538*, 2023.
- <span id="page-13-7"></span>Qiusi Zhan, Zhixiang Liang, Zifan Ying, and Daniel Kang. Injecagent: Benchmarking indirect prompt injections in tool-integrated large language model agents. In *Annual Meeting of the Association for Computational Linguistics*, 2024. URL [https://api.semanticscholar.org/CorpusID:](https://api.semanticscholar.org/CorpusID:268248325) [268248325](https://api.semanticscholar.org/CorpusID:268248325).
- <span id="page-13-1"></span>Yiming Zhang, Nicholas Carlini, and Daphne Ippolito. Effective prompt extraction from language models. In *First Conference on Language Modeling*, 2024. URL [https://openreview.net/](https://openreview.net/forum?id=0o95CVdNuz) [forum?id=0o95CVdNuz](https://openreview.net/forum?id=0o95CVdNuz).
- <span id="page-13-5"></span>Wenting Zhao, Xiang Ren, Jack Hessel, Claire Cardie, Yejin Choi, and Yuntian Deng. Wildchat: 1m chatGPT interaction logs in the wild. In *The Twelfth International Conference on Learning Representations*, 2024. URL <https://openreview.net/forum?id=Bl8u7ZRlbM>.
- <span id="page-13-4"></span>Lianmin Zheng, Wei-Lin Chiang, Ying Sheng, Siyuan Zhuang, Zhanghao Wu, Yonghao Zhuang, Zi Lin, Zhuohan Li, Dacheng Li, Eric Xing, Hao Zhang, Joseph E Gonzalez, and Ion Stoica. Judging llm-as-a-judge with mt-bench and chatbot arena. In A. Oh, T. Naumann, A. Globerson, K. Saenko, M. Hardt, and S. Levine (eds.), *Advances in Neural Information Processing Systems*, volume 36, pp. 46595–46623. Curran Associates, Inc., 2023. URL [https://proceedings.neurips.cc/paper\\_files/paper/2023/file/](https://proceedings.neurips.cc/paper_files/paper/2023/file/91f18a1287b398d378ef22505bf41832-Paper-Datasets_and_Benchmarks.pdf) [91f18a1287b398d378ef22505bf41832-Paper-Datasets\\_and\\_Benchmarks.pdf](https://proceedings.neurips.cc/paper_files/paper/2023/file/91f18a1287b398d378ef22505bf41832-Paper-Datasets_and_Benchmarks.pdf).
- <span id="page-13-3"></span>Xiaosen Zheng, Tianyu Pang, Chao Du, Qian Liu, Jing Jiang, and Min Lin. Improved few-shot jailbreaking can circumvent aligned language models and their defenses, 2024. URL [https:](https://arxiv.org/abs/2406.01288) [//arxiv.org/abs/2406.01288](https://arxiv.org/abs/2406.01288).
- <span id="page-13-12"></span>Andy Zou, Zifan Wang, Nicholas Carlini, Milad Nasr, J Zico Kolter, and Matt Fredrikson. Universal and transferable adversarial attacks on aligned language models. *arXiv preprint arXiv:2307.15043*, 2023.
- <span id="page-13-6"></span>Andy Zou, Long Phan, Justin Wang, Derek Duenas, Maxwell Lin, Maksym Andriushchenko, Rowan Wang, Zico Kolter, Matt Fredrikson, and Dan Hendrycks. Improving alignment and robustness with circuit breakers. *ArXiv*, abs/2406.04313, 2024. URL [https://api.semanticscholar.org/](https://api.semanticscholar.org/CorpusID:270286008) [CorpusID:270286008](https://api.semanticscholar.org/CorpusID:270286008).
- <span id="page-13-10"></span>Egor Zverev, Sahar Abdelnabi, Mario Fritz, and Christoph H Lampert. Can llms separate instructions from data? and what do we even mean by that? *arXiv preprint arXiv:2403.06833*, 2024.

## <span id="page-14-0"></span>A DETAILS OF IMPLEMENTING INSTRUCTIONAL SEGMENT EMBEDDING

Here's an example of implementing Instructional Segment Embedding with a few lines of Python/Pytorch code. The additional code is highlighted in bold blue.

In the init function, we initialize embedding layers, including the token embedding layer, ISE embedding layer, and positional embedding layer. The inputs to the function include the embedding dimension (embed\_size), vocabulary size (vocab\_size), and ISE dimension (ISE\_size, which defaults to 4).

During inference (the forward function), we compute the token embeddings and ISE embeddings, then sum them for further processing. The input x is a list containing the input IDs of each token in the sentence, and the input seg is a list containing the segment IDs (e.g., system as 0, user as 1, data as 2, output as 3) for each token, with the same size as x.

### Instructional

```
1 import torch
4 class Transformer ( nn . Module ) :
5 def __init__ ( self , embed_size , vocab_size , ISE_size ) :
6 super ( Transformer , self ) . __init__ ()
7 self . token_embedding = nn . Embedding ( vocab_size , embed_size )
8 # Token embedding layer
9 self . ISE_embedding = nn. Embedding ( ISE_size , embed_size )
10 # Instructional segment embedding layer
12 self . positional_embedding = ...
13 self . layers = ...
14
16 def forward ( self , x , seg) :
17 token_embed = self . token_embedding ( x )
18 # Convert token indices to token embeddings
19 ISE_embed = self . ISE_embedding (seg)
20 # Convert instructional segments to Instructional Segment
     Embeddings
22 embedding = token_embed + ISE_embed
24 x = self . positional_encoding ( embedding )
26 for layer in self . layers :
27 x = layer ( x )
28
29 return x
```

## <span id="page-15-2"></span>B DETAILS OF TRAINING DATA

In this section, we provide details on how we construct the data, including both the clean and adversarial datasets, to conduct experiments on Structured Query and Instruction Hierarchy benchmarks.

### <span id="page-15-0"></span>B.1 STRUCTURED QUERY BENCHMARK.

For the Clean Alpaca dataset, we use the *Alpaca-Cleaned-50K* dataset [\(Taori et al., 2023;](#page-12-1) [Gururise,](#page-11-5) [2024\)](#page-11-5) to fine-tune the model. There are 32,603 samples that contain data input, and 19,157 samples do not contain any data input. All of them contain user input. Since the dataset shares the same system instructions (i.e., "Below is an instruction that describes a task, paired with an input that provides further context. Write a response that appropriately completes the request."), we combine the types of system and user instructions into a single instruction type.

For the Adversarial Alpaca dataset, we follow the approach outlined in [Chen et al.](#page-10-2) [\(2024\)](#page-10-2) to construct the dataset. We keep the samples without data input unchanged. Then, the remaining data includes both clean samples (50%), derived from the Clean Alpaca dataset, and attacked samples (50%), which involve indirect prompt injection attacks within the data. These attacked samples contain two types of attacks: the Naive Attack and the Completion-Other Attack. In the Naive Attack, the instruction from other samples is injected into the data. In the Completion-Other Attack, a fabricated response is injected first, followed by another set of instructions. The desired output for these adversarial samples should address only the original user instruction so the output remains the same. We provide a demonstration in Figure [11.](#page-15-3)

More details can be found in this [StruQ repository.](https://github.com/Sizhe-Chen/StruQ/tree/main)

<span id="page-15-3"></span>Figure 11: A demonstration of how the Adversiaral Alpaca dataset is constructed.

### <span id="page-15-1"></span>B.2 INSTRUCTION HIERARCHY BENCHMARK.

We use three different datasets to train models: UltraChat Baseline, System Follow, and Instruction Hierarchy.

For the UltraChat Baseline dataset, we use the *UltraChat-200K* dataset [\(Ding et al., 2023\)](#page-10-3) and employ GPT-4o to decompose 10K prompts into three components: system instructions, user instructions, and data inputs. We provided the detailed prompts in Figure [12](#page-16-0) and an example of decomposing data

in Figure [13.](#page-16-1) This results in approximately 190K plain UltraChat samples and 10K samples with structured queries. For samples without system instructions, we use the default prompt shown in Figure [14.](#page-16-2)

<span id="page-16-0"></span>Figure 12: The prompt of decomposing compositional prompts to structured prompts.

<span id="page-16-1"></span>Figure 13: An example of prompts before and after decomposing using GPT-4o.

<span id="page-16-2"></span>Figure 14: The default system prompt of Instruction Hierarchy benchmark.

For the System Follow dataset, we combine the UltraChat Baseline dataset with two additional datasets: SystemChat [\(Abacus.AI, 2023\)](#page-10-6) and SystemMessage [\(Huggingface, 2023\)](#page-11-6). We use 5K samples from each of these datasets. All of them do not contain the data part. Additionally, we observe that the quality of the original responses in SystemChat is relatively low; therefore, we use GPT-4o to generate high-quality output.

For the Instruction Hierarchy dataset, we include three different types of misaligned data following [Wallace et al.](#page-12-0) [\(2024\)](#page-12-0): indirect prompt injection, direct prompt injection, and prompt extraction. (1) Indirect prompt injection: We use 2K samples from UltraChat and inject instructions from other samples into the data. The output remains unchanged. (2) Direct prompt injection: We use 2K SystemChat samples and inject malicious user instructions that attempt to change the original system instructions. Additionally, we include 200 samples that directly conflict with the system instructions. The outputs for both parts are generated by GPT-4o. We provide a demonstration of how to prompt the GPT-4o model to ensure it follows the desired behavior in Figure [15.](#page-17-0) Additionally, we manually review a portion of the outputs to verify this. (3) Prompt extraction: We use 200 SystemMessage samples and inject malicious user instructions that attempt to extract the system message. We also included 2K samples that used aligned questions, which asked for general information about the system messages. Again, GPT-4o is used to generate the outputs. For direct prompt injection and prompt extraction, all injected user instructions are also generated by prompting GPT-4o.

<span id="page-17-0"></span>Figure 15: The prompt of generating desired responses from GPT-4o.

## <span id="page-18-0"></span>C DETAILS OF EVALUATION

In this section, we provide full details on constructing various attacks to evaluate LLM models. Specifically, we consider the Structured Query benchmark (Appendix [C.1\)](#page-18-1) and the Instruction Hierarchy benchmark (Appendix [C.2\)](#page-19-0). We also explain how we evaluate the model's instructionfollowing capabilities in Appendix [C.3.](#page-20-0)

### <span id="page-18-1"></span>C.1 EVALUATIONS ON STRUCTURED QUERY BENCHMARK

As we discussed in Section [5.3,](#page-5-1) we leverage the same evaluation methods from [\(Chen et al., 2024\)](#page-10-2), including Naive Attack, Ignore Attack, Escape Separation Attack, and Completion Real Attack, as shown in Figure [16.](#page-18-2) We use the test set from AlpacaEval, but only include samples containing valid data inputs to evaluate the model, resulting in a total of 208 test samples.

These attacks are designed to trick the model into outputting the specific word "hacked". The Naive Attack directly requests the model to print "hacked". The Ignore Attack prompts the model to disregard all previous instructions and output "hacked" [\(Perez & Ribeiro, 2022\)](#page-12-3). The Escape Separation Attack injects special characters to simulate a separation of the previous text, tricking the model into ignoring prior instructions. Finally, the Completion Real Attack appends a fake response to the prompt, leading the model to believe the task is complete, after which malicious instructions are injected for the model to follow.

We also evaluate out-of-domain indirect prompt injection attacks. The key idea is to inject the adversarial text at the beginning and end of the data input sequence. We present a demonstration in Figure [17.](#page-19-1)

For both in-domain and out-of-domain attacks, we evaluate the models using robust accuracy, defined as the ratio of samples that do not output "hacked".

Figure 16: A demonstration of in-domain indirect prompt injection attacks on the Alpaca dataset, including Naive Attack, Ignore Attack, Escape Separation Attack, and Completion Real Attack.

Figure 17: A demonstration of out-of-domain indirect prompt injection attacks on the Alpaca dataset, including Naive Attack, Ignore Attack, Escape Separation Attack, and Completion Real Attack.

### <span id="page-19-0"></span>C.2 EVALUATIONS ON THE INSTRUCTION HIERARCHY BENCHMARK

We evaluate our models on Instruction Hierarchy using four types of attacks: indirect prompt injection, direct prompt injection, prompt extraction, and harmful requests.

Indirect prompt injection. We use the same evaluations and metrics as those applied in the Structured Query benchmarks.

Direct prompt injection. We use the same attacking prompts as indirect prompt injection but inject them directly into the user prompt. Additionally, we use the test set from AlpacaEval without any data input, which consists of 597 test samples. The evaluation metric remains the same: we calculate the ratio of samples that do not output "hacked", and denote this as robustness.

Prompt extraction. We use the ShareGPT and Unnatural Instructions datasets [\(Honovich et al.,](#page-11-12) [2023\)](#page-11-12), each consisting of 500 prompts, as described in [\(Zhang et al., 2024\)](#page-13-1), to serve as the secret system messages. To perform prompt extraction, we utilize 15 effective prompts selected by the authors. These prompts are illustrated in Figure [18.](#page-20-1)

For evaluation metrics, we adopt the approach of [Zhang et al.](#page-13-1) [\(2024\)](#page-13-1), utilizing an approximate metric based on ROUGE-L recall [\(Lin, 2004\)](#page-11-7). This metric computes the length of the longest common subsequence (LCS) between the extracted system message (e) and the ground truth (t). The resulting score is the ratio of the LCS length to the length of the ground truth. An attack is considered successful if this score exceeds 0.9, as presented in Equation [1.](#page-19-2)

<span id="page-19-2"></span>
$$Metric(e, t) = 1 \left[ \frac{|LCS(tokens(t), tokens(e))|}{|tokens(t)|} \ge 0.9 \right]$$
 (1)

Robustness is then evaluated by the proportion of samples that successfully defend against the attack.

Harmful requests. We follow the evaluation approach of [Wallace et al.](#page-12-0) [\(2024\)](#page-12-0), utilizing prompts from Jailbreakchat (Chat) and "Do Anything Now" (DAN). These prompts are concatenated with malicious requests from StrongREJECT [\(Souly et al., 2024\)](#page-12-9) to create the final harmful prompts.

<span id="page-20-1"></span>Figure 18: A demonstration of attacking prompts used in prompt extraction.

<span id="page-20-2"></span>Figure 19: A demonstration of evaluation prompts for harmful requests.

The full dataset includes 79 effective attacking prompts from Jailbreakchat (Chat) and 225 from "Do Anything Now" (DAN), all of which are publicly available. Both Jailbreakchat (Chat) and "Do Anything Now" (DAN) can be accessed in the [repository,](https://github.com/verazuo/jailbreak_llms/tree/main/data/prompts) sourced from jailbreakchat.com and ChatGPTJailbreak. Additionally, there are 313 malicious instructions from StrongREJECT. For each sample, we randomly select one attacking prompt to concatenate with the instruction, resulting in a dataset of 313 evaluation samples.

For evaluation metrics, we query GPT-4o to determine whether the response adheres to safety guardrails (i.e., whether the response provides sufficient details to answer malicious requests). The detailed evaluation prompt is presented in Figure [19,](#page-20-2) which is similar to that used in [\(Xie et al., 2024\)](#page-13-9). Robust accuracy is then computed as the ratio of cases where the model either rejects or does not provide sufficient detail in response to malicious questions.

## <span id="page-20-0"></span>C.3 INSTRUCTION-FOLLOWING EVALUATION

We also evaluate our models using two instruction-following benchmarks: AlpacaEval 1.0 [\(Li et al.,](#page-11-8) [2023\)](#page-11-8) and MT-Bench [\(Zheng et al., 2023\)](#page-13-4). Specifically, we follow the steps of AlpacaEval 1.0 to assess model performance. For MT-Bench, we evaluate only 1-turn conversations, as our model is trained for single-turn interactions.

<span id="page-21-0"></span>Figure 20: A demonstration of prompts for over-refusal evaluation.

### C.4 OVER-REFUSAL EVALUATION

For over-refusal evaluation, we query GPT-4o to assess whether the response provides sufficient details to address benign requests. The detailed evaluation prompt is shown in Figure [20,](#page-21-0) which is similar to the prompts used for evaluating harmful request tasks.

## <span id="page-22-0"></span>D MORE EXPERIMENTAL RESULTS ON STRUCTURED QUERY

In this section, we provide a detailed evaluation of additional indirect prompt injection attacks as constructed by [\(Chen et al., 2024\)](#page-10-2). Specifically, we evaluate the "Escape deletion" attack, which injects multiple instances of \b or \r to mimic the deletion of previous characters. We also study 12 other types of completion attacks that attempt to obfuscate the prompt roles using unusual characters, and further details are in [\(Chen et al., 2024\)](#page-10-2) and [StruQ repository.](https://github.com/Sizhe-Chen/StruQ/tree/main) Additionally, we include the results of our instructional segment embedding with text delimiters.

As shown in Figures [2](#page-22-1) and [3,](#page-22-2) our ISE with special delimiters consistently outperforms all other methods in almost all cases. Interestingly, we found that directly using Instructional Segment Embedding does not improve performance on the Clean Alpaca dataset but generally increases robustness on the Adversarial Alpaca dataset by up to 4.6% on average and up to 14% for the in-domain worst robust accuracy compared to the baseline. Therefore, ISE should be used with special token delimiters to achieve the best performance.

<span id="page-22-1"></span>Table 2: Full evaluation results of the LLM on LLAMA-2-13B using in-domain indirect prompt injection attacks.

| Dataset                  |          |             | Clean Alpaca |             | Adversarial Alpaca |             |           |             |  |
|--------------------------|----------|-------------|--------------|-------------|--------------------|-------------|-----------|-------------|--|
| Method                   | Baseline | +ISE (Ours) | Delimiter    | +ISE (Ours) | Baseline           | +ISE (Ours) | Delimiter | +ISE (Ours) |  |
| AlpacaEval (↑)           | 72.76    | 72.13       | 72.67        | 72.13       | 73.41              | 73.35       | 72.26     | 73.76       |  |
| Naive                    | 65.87    | 67.31       | 68.75        | 75.96       | 100.00             | 100.00      | 99.04     | 100.00      |  |
| Ignore                   | 57.69    | 61.06       | 57.21        | 70.19       | 99.52              | 98.08       | 99.04     | 99.04       |  |
| Escape-deletion          | 86.54    | 80.77       | 83.17        | 79.81       | 99.04              | 99.52       | 99.04     | 98.56       |  |
| Escape-separation        | 75.00    | 72.60       | 69.23        | 78.85       | 99.52              | 100.00      | 99.52     | 100.00      |  |
| Completion-other         | 10.10    | 21.15       | 9.62         | 43.75       | 100.00             | 100.00      | 100.00    | 100.00      |  |
| Completion-othercmb      | 31.25    | 30.29       | 33.65        | 60.58       | 100.00             | 100.00      | 100.00    | 100.00      |  |
| Completion-real          | 4.81     | 5.29        | 7.21         | 40.38       | 70.19              | 81.73       | 100.00    | 100.00      |  |
| Completion-realcmb       | 26.92    | 25.96       | 17.31        | 48.56       | 98.08              | 95.67       | 100.00    | 100.00      |  |
| Completion-close-2hash   | 5.29     | 5.29        | 10.10        | 45.67       | 97.60              | 98.56       | 100.00    | 100.00      |  |
| Completion-close-1hash   | 9.62     | 6.25        | 7.69         | 36.54       | 65.38              | 79.81       | 100.00    | 100.00      |  |
| Completion-close-0hash   | 11.06    | 5.77        | 9.13         | 47.12       | 93.27              | 97.12       | 100.00    | 100.00      |  |
| Completion-close-upper   | 5.29     | 6.25        | 7.21         | 38.46       | 93.27              | 96.15       | 100.00    | 100.00      |  |
| Completion-close-title   | 5.77     | 5.77        | 7.21         | 27.40       | 70.19              | 87.98       | 99.52     | 100.00      |  |
| Completion-close-nospace | 6.25     | 5.77        | 6.25         | 38.46       | 82.69              | 89.90       | 100.00    | 100.00      |  |
| Completion-close-nocolon | 6.25     | 5.77        | 8.65         | 38.46       | 71.63              | 89.42       | 100.00    | 100.00      |  |
| Completion-close-typo    | 7.21     | 6.25        | 10.10        | 50.96       | 97.12              | 99.52       | 99.52     | 100.00      |  |
| Completion-close-similar | 5.77     | 5.29        | 8.65         | 45.19       | 91.83              | 93.75       | 99.52     | 99.52       |  |
| Average                  | 24.75    | 24.52       | 24.77        | 50.96       | 89.96              | 94.60       | 99.66     | 99.83       |  |
| Worst                    | 4.81     | 5.29        | 6.25         | 27.40       | 65.38              | 79.81       | 98.08     | 98.56       |  |

<span id="page-22-2"></span>Table 3: Full evaluation results of the LLM on LLAMA-2-13B using out-of-domain indirect prompt injection attacks.

| Dataset           |          |             | Clean Alpaca |             | Adversarial Alpaca |             |           |             |  |  |
|-------------------|----------|-------------|--------------|-------------|--------------------|-------------|-----------|-------------|--|--|
| Method            | Baseline | +ISE (Ours) | Delimiter    | +ISE (Ours) | Baseline           | +ISE (Ours) | Delimiter | +ISE (Ours) |  |  |
| AlpacaEval (↑)    | 73.32    | 72.13       | 72.67        | 71.21       | 73.41              | 73.35       | 72.26     | 72.60       |  |  |
| Naive             | 62.02    | 63.46       | 66.35        | 69.71       | 64.90              | 65.87       | 67.79     | 76.44       |  |  |
| Ignore            | 52.40    | 66.83       | 51.92        | 69.71       | 98.56              | 96.63       | 96.15     | 96.63       |  |  |
| Escape-separation | 72.12    | 63.46       | 71.63        | 70.67       | 73.08              | 74.52       | 76.44     | 88.46       |  |  |
| Completion-real   | 1.92     | 1.92        | 12.99        | 34.14       | 85.58              | 96.64       | 91.35     | 99.52       |  |  |
| Average           | 47.12    | 48.92       | 50.72        | 61.06       | 80.53              | 83.41       | 82.93     | 90.26       |  |  |
| Worst             | 1.92     | 1.92        | 12.99        | 34.14       | 64.90              | 65.87       | 67.79     | 76.44       |  |  |

### E MORE EXPERIMENTAL RESULTS ON INSTRUCTION HIERARCHY

In this section, we provide additional experimental results on the Instruction Hierarchy benchmark, covering indirect prompt injection (Appendix E.1), direct prompt injection (Appendix E.2), prompt extraction (Appendix E.3), and harmful requests (Appendix E.4). Furthermore, we present the results for Llama-3.1-8B in Appendix E.5.

### <span id="page-23-0"></span>E.1 DETAILED ANALYSIS OF INDIRECT PROMPT INJECTION

In Figure 6, we present the results of both in-domain and out-of-domain attacks. Similar to the Structured Query benchmark, we evaluate additional in-domain attacks designed by (Chen et al., 2024), which are shown in Figure 21. Due to space constraints, we use Att to represent different attacks.

Specifically, Att1 to Att18 correspond to the following list of attacks: Att1:Naive, Att2:Ignore, Att3:Escape\_deletion, Att4:Escape\_separation, Att5:Completion\_other, Att6:Completion\_othercmb, Att7:Completion\_real, Att8:Completion\_realcmb, Att9:Completion\_close\_2hash, Att10:Completion\_close\_1hash, Att11:Completion\_close\_0hash, Att12:Completion\_close\_upper, Att13:Completion\_close\_title, Att14:Completion\_close\_nospace, Att15:Completion\_close\_nocolon, Att16:Completion\_close\_typo, and Att17:Completion\_close\_similar.

Again, we observe that our ISE method significantly enhances robustness against almost all attacks. The average robust accuracy gains range from approximately 15% to 45%, with the worst robust accuracy gains reaching up to nearly 50%.

![](_page_23_Figure_7.jpeg)

<span id="page-23-2"></span>Figure 21: Full results of in-domain indirect prompt injection attack we evaluated on the Instruction Hierarchy benchmark.

### <span id="page-23-1"></span>E.2 Detailed Analysis of Direct Prompt Injection

In Figure 22, we report the robust accuracy against both in-domain and out-of-domain direct prompt injection attacks. We observe performance gains for our ISE method across various attack scenarios. For instance, the average robust accuracy against in-domain attacks improves from **47.3**% to **69.9**% for the model trained on the UltraChat Baseline dataset.

Additionally, similar to indirect prompt injection attacks, we also include the full results of in-domain attacks in Figure 23. The attacking prompts are exactly the same as described in Appendix E.1. These results further validate the effectiveness of our method, improving the average robust accuracy by over 10% and the worst robust accuracy by over 20%.

<span id="page-23-3"></span>![](_page_23_Figure_12.jpeg)

Figure 22: Results of direct prompt injection attack we evaluated on the Instruction Hierarchy benchmark.

![](_page_24_Figure_1.jpeg)

<span id="page-24-3"></span>Figure 23: Full results of in-domain direct prompt injection attack we evaluated on the Instruction Hierarchy benchmark.

### <span id="page-24-0"></span>E.3 DETAILED ANALYSIS OF PROMPT EXTRACTION

Following Section 6.3, we also present the full results of the prompt extraction on the Unnatural Instructions dataset. We observe similar trends where adding ISE makes the model more robust against extraction attacks, potentially enhancing privacy. Notably, the robustness (i.e., the ratio of cases where the attack fails to extract a significant number of original prompts) improves by over 20% on both average and worst scenarios for the models trained on the UltraChat Baseline.

![](_page_24_Figure_5.jpeg)

Figure 24: Full results of prompt extraction we evaluated on Unnatural Instructions.

### <span id="page-24-1"></span>E.4 DETAILED ANALYSIS OF HARMFUL REQUESTS

We present the full results from Figure 8 with two more models trained on the System Follow and Instruction Hierarchy dataset in Figure 25. We continue to observe average robustness improvements across different categories, especially for the UltraChat Baseline and Instruction Hierarchy datasets. Note that the model was trained without any data specifically designed to bypass the safety guidelines.

<span id="page-24-4"></span>![](_page_24_Figure_9.jpeg)

Figure 25: Full results of the harmful request evaluation on JailbreakChat prompts using StrongRE-JECT malicious instructions.

### <span id="page-24-2"></span>E.5 DETAILED ANALYSIS OF LLAMA 3.1 MODEL

We then provide a more detailed evaluation of the Llama-3.1-8B model on Instruction Hierarchy in Figure 26. We continue to observe improved model capability and enhanced robustness across various attacks, indicating that our method generalizes well to different models. For instance, ISE consistently improves the winning rate on AlpacaEval and either maintains or improves the score on

MT-Bench. In terms of robustness, our method also improves performance, even for models trained on Instruction Hierarchy, which already achieve high robustness.

![](_page_25_Figure_2.jpeg)

<span id="page-25-0"></span>Figure 26: Evaluations on Llama-3.1-8B. The evaluation of model capabilities on the Instruction Hierarchy benchmark is conducted using AlpacaEval and MT-Bench (Figure a). Robustness evaluations include indirect and direct prompt injection attacks, prompt extraction attacks, and harmful requests (Figure b). We performed experiments across three training datasets and compared our Instructional Segment Embedding (ISE) method against the baseline.

## E.6 INVESTIGATION OF INSTRUCTIONAL SEGMENT EMBEDDING

In this appendix, we examine the behavior of our ISE embeddings across different scenarios. Specifically, we analyze three settings: omitting the system prompt, using the system prompt with user embedding, and using the data part with user embedding.

Capability Evaluation. First, we present the results on AlpacaEval as the clean performance in Table [4](#page-26-0) with these three settings.

In general, we observe a slight performance degradation (< 5%) when system prompts are omitted, particularly for models trained on the Instruction Hierarchy. However, our method largely preserves instruction-following capability compared to baseline methods. This highlights that the system prompt plays a more significant role in the ISE models than in the baseline methods.

Next, we assess the performance of system prompts using user embeddings. In this setting, we observe a noticeable performance degradation (∼15%), which is even greater than when system prompts are omitted. We attribute this to the system prompts (i.e., *Below is an instruction that describes a task, paired with an input that provides further context. Write a response that appropriately completes the request.*) being mixed with the original user prompts. This makes it challenging for the model to accurately interpret and follow the intended user prompt, leading to lower-quality responses.

Interestingly, we find that performance remains high when the data part uses user embeddings. The degradation is less than 2%. We think that this is because some of the training data does not separate the user and data parts.

<span id="page-26-0"></span>Table 4: AlpacaEval evaluation of various configurations with and without Instruction Segment Embedding (ISE).

| Training Data               |          | UltraChat Baseline |          | Instruction Follow |          | Instruction Hierarchy |
|-----------------------------|----------|--------------------|----------|--------------------|----------|-----------------------|
|                             | Baseline | +ISE (Ours)        | Baseline | +ISE (Ours)        | Baseline | +ISE (Ours)           |
| With system prompt          | 63.18%   | 64.65%             | 77.24%   | 81.82%             | 79.25%   | 83.35%                |
| Without system prompt       | 61.39%   | 63.50%             | 75.16%   | 76.60%             | 79.47%   | 78.57%                |
| System using user embedding | —        | 50.93%             | —        | 66.42%             | —        | 70.90%                |
| Data using user embedding   | —        | 63.34%             | —        | 80.77%             | —        | 83.08%                |

Robustness Evaluation. We then conduct experiments against indirect prompt injection attacks (Naive attack) under the same three settings. We present the results in Table [5.](#page-26-1)

Firstly, we observe that the robustness against indirect prompt injection attacks remains roughly unchanged when the system prompt is omitted. Our ISE method still demonstrates higher robustness (10% to 20%) compared to the baseline. Secondly, we evaluate the use of system prompts with user embeddings and observe a slight performance degradation (<6%). Lastly, we assess the use of data prompts with user embeddings and find a more noticeable performance degradation (up to 10%). This result is expected, as adversarial texts (injected into the data part) are more prioritized.

<span id="page-26-1"></span>Table 5: Performance of various configurations with and without Instruction Segment Embedding (ISE) against indirect prompt injection attacks.

| Training Data               |          | UltraChat Baseline |          | Instruction Follow | Instruction Hierarchy |             |
|-----------------------------|----------|--------------------|----------|--------------------|-----------------------|-------------|
|                             | Baseline | +ISE (Ours)        | Baseline | +ISE (Ours)        | Baseline              | +ISE (Ours) |
| With system prompt          | 64.42%   | 82.21%             | 61.54%   | 77.88%             | 83.65%                | 87.02%      |
| Without system prompt       | 62.50%   | 82.69%             | 64.90%   | 78.37%             | 80.77%                | 88.94%      |
| System using user embedding | —        | 76.92%             | —        | 75.48%             | —                     | 85.58%      |
| Data using user embedding   | —        | 76.44%             | —        | 71.63%             | —                     | 76.92%      |

### E.7 EVALUATION ON AUTOMATIC ATTACKS.

We also conduct experiments to evaluate the effectiveness of our method against indirect prompt injection attacks using automatically optimized prompts. Specifically, we follow the methodology outlined in [\(Chao et al., 2023\)](#page-10-9), which iteratively refines and improves the attacking prompts using GPT-4o. The goal of these prompts is to mislead the model into generating the word "hacked." The results are presented in Table [6.](#page-27-0)

We observe that our ISE methods consistently demonstrate higher robustness (up to 20%) against this automatic attack. The improvement is particularly noticeable when the model is trained on the UltraChat Baseline and Instruction Following datasets. These results align with our findings on other types of attacks.

<span id="page-27-0"></span>Table 6: Performance of the Instructional Segment Embedding on multi-turn MT-Bench.

| Training Data     | UltraChat Baseline |             |          | Instruction Follow | Instruction Hierarchy |             |  |
|-------------------|--------------------|-------------|----------|--------------------|-----------------------|-------------|--|
|                   | Baseline           | +ISE (Ours) | Baseline | +ISE (Ours)        | Baseline              | +ISE (Ours) |  |
| Automatic attacks | 39.90%             | 57.21%      | 13.46%   | 34.62%             | 65.38%                | 69.71%      |  |

### E.8 EVALUATION ON MULTI-TURN CONVERSATION.

Although all the training data are single-turn conversations, we observe that our ISE method is capable of handling multi-turn conversations. Specifically, we conduct experiments on MT-Bench with multi-turn scenarios and prompt GPT-4o to evaluate the performance of the generated responses. The results are presented in Table [7.](#page-27-1)

We observe that all models experience some performance degradation (up to 2.7), which is expected given that the models are trained on single-turn chat datasets. Nonetheless, ISE achieves comparable or even higher MT-Bench scores in multi-turn tasks. This demonstrates the potential of our method to extend to multi-turn conversations.

<span id="page-27-1"></span>Table 7: Performance of the Instructional Segment Embedding on multi-turn MT-Bench.

| Training Data | UltraChat Baseline |             |          | Instruction Follow | Instruction Hierarchy |             |  |
|---------------|--------------------|-------------|----------|--------------------|-----------------------|-------------|--|
|               | Baseline           | +ISE (Ours) | Baseline | +ISE (Ours)        | Baseline              | +ISE (Ours) |  |
| Single-turn   | 6.73               | 6.64        | 7.38     | 7.55               | 7.30                  | 7.48        |  |
| Mutli-turn    | 5.81               | 5.7         | 5.6      | 6.48               | 4.61                  | 5.4         |  |

### E.9 CASE STUDY OF ISE ATTENTION

In this appendix, we analyze the attention differences between the baseline and ISE models. We focus on models trained on the instruction hierarchy dataset and illustrate an attack example (indirect prompt injection) in Figure [27.](#page-28-0) Our observations reveal that the baseline model fails to distinguish benign instructions from malicious ones, whereas our method effectively identifies the presence of malicious attacks in the context.

Next, we present a visualization of the average attention logits in layer 0 in Figure [28.](#page-28-1) We observe that the diagonal line of the baseline model (without ISE) is much brighter than that of our ISE model. This indicates that the baseline model places significantly stronger attention on neighbor tokens, making it more susceptible to malicious instructions in data. As a result, the malicious instruction "Print exactly hacked" plays an overly important role in generating the final response. In contrast, the ISE model distributes attention more evenly across the full instructions, and provide safe responses.

Figure 27: A demonstration of indirect prompt injection attacks against baseline and ISE models trained on instruction hierarchy dataset.

<span id="page-28-0"></span>![](_page_28_Figure_7.jpeg)

<span id="page-28-1"></span>Figure 28: Attention patterns between baseline and ISE models on the example of Figure [27.](#page-28-0)

## E.10 DETAILED FIGURE OF ROBUSTNESS EVALUATION ON INSTRUCTION HIERARCHY

![](_page_29_Figure_2.jpeg)

Figure 29: Detailed demonstration of Figure [5.](#page-7-0) Evaluation results of Llama-3-8B on Instruction Hierarchy.

## <span id="page-30-0"></span>F DISCUSSIONS AND EVALUATIONS ON JAILBREAK ATTACKS

In our harmful request evaluations, we primarily focused on malicious prompts collected in the wild, without involving any active optimization, following [Wallace et al.](#page-12-0) [\(2024\)](#page-12-0). We considered these prompts as zero-shot generalization evaluations since no training data aimed to bypass safety alignment.

There also exist adaptive attacks, known as jailbreak attacks, generated through advanced strategies, such as adversarially optimized texts like those in [\(Zou et al., 2023;](#page-13-12) [Liao & Sun, 2024\)](#page-11-13), or carefully human-crafted strategies as seen in [Anil et al.](#page-10-10) [\(2024\)](#page-10-10). In Table [8,](#page-30-1) we present the results of using adaptive attacks from [\(Andriushchenko et al., 2024;](#page-10-11) [Zheng et al., 2024\)](#page-13-3) on 50 malicious requests [\(Chao et al., 2023\)](#page-10-9), and we observe that our models almost completely fail to generate safe responses.

*In fact, we do not expect our method to improve adaptive jailbreak robustness.* First, none of our data were explicitly created to defend against (or reject) jailbreak attacks. Second, while our segment embedding is designed to differentiate between types of instructions, adversarial texts may directly target the model. Our method is orthogonal to many robust training methods, such as LAT [\(Sheshadri](#page-12-15) [et al., 2024\)](#page-12-15) and circuit breakers [\(Zou et al., 2024\)](#page-13-6). We leave further exploration of this issue for future research.

<span id="page-30-1"></span>Table 8: Robust accuracy against adaptive attacks on Instruction Hierarchy benchmark.

|                       | UltraChat | +ISE   | System | +ISE   | Instruction | +ISE   |
|-----------------------|-----------|--------|--------|--------|-------------|--------|
|                       | Baseline  | (Ours) | Follow | (Ours) | Hierarchy   | (Ours) |
| Jailbreak attacks (%) | 2.0       | 2.0    | 0.0    | 2.0    | 2.0         | 4.0    |