                                         Multimodal Needle in a Haystack: Benchmarking Long-Context Capability
                                                        of Multimodal Large Language Models
                                                 Hengyi Wang1 * , Haizhou Shi1 , Shiwei Tan1 , Weiyi Qin1 , Wenyuan Wang1 ,
                                                        Tunyu Zhang1 , Akshay Nambi2 , Tanuja Ganu2 , Hao Wang1
                                                                         1
                                                                             Rutgers University, 2 Microsoft Research
                                                                                   https://mmneedle.github.io

                                                               Abstract                               Ying et al., 2024). To evaluate the capabilities and
                                             Multimodal Large Language Models (MLLMs)                 limitations of MLLMs, various benchmarks have
                                             have shown significant promise in various ap-            been proposed, focusing on challenges such as rea-




arXiv:2406.11230v2 [cs.LG] 11 Feb 2025
                                             plications, leading to broad interest from re-           soning (Yue et al., 2023; Padlewski et al., 2024; Lu
                                             searchers and practitioners alike. However, a            et al., 2023), perception (Fu et al., 2024b; Yu et al.,
                                             comprehensive evaluation of their long-context           2023), and hallucination (Guan et al., 2023).
                                             capabilities remains underexplored. To ad-                  Despite significant progress, the evaluation of
                                             dress these gaps, we introduce the MultiModal
                                                                                                      MLLMs for long-context understanding has been
                                             Needle-in-a-haystack (MMNeedle) benchmark,
                                             specifically designed to assess the long-context         lagging. Current evaluation methods and bench-
                                             capabilities of MLLMs. Besides multi-image               marks (Yue et al., 2023; Ying et al., 2024; Liu et al.,
                                             input, we employ image stitching to further in-          2023; Padlewski et al., 2024; Fu et al., 2024b; Yu
                                             crease the input context length, and develop a           et al., 2023; Chen et al., 2024; Fu et al., 2024a;
                                             protocol to automatically generate labels for            Lu et al., 2023; Reid et al., 2024) either (1) as-
                                             sub-image level retrieval. Essentially, MM-              sume the use of single or limited images as inputs,
                                             Needle evaluates MLLMs by stress-testing
                                                                                                      failing to stress-test MLLMs’ long-context capa-
                                             their capability to locate a target sub-image
                                             (needle) within a set of images (haystack)
                                                                                                      bilities or (2) only contain a limited numbers of
                                             based on textual instructions and descriptions           data points (referred to as “samples” in this paper),
                                             of image contents. This setup necessitates               lacking in statistical significance and therefore of-
                                             an advanced understanding of extensive vi-               ten rendering the evaluation inconclusive. These
                                             sual contexts and effective information re-              gaps limit the development of MLLMs capable of
                                             trieval within long-context image inputs. With           effectively handling long-context hybrid-modality
                                             this benchmark, we evaluate state-of-the-art             inputs, which is crucial for broader applications.
                                             MLLMs, encompassing both API-based and
                                                                                                         To bridge this gap, we introduce the MultiModal
                                             open-source models. The findings reveal that
                                             GPT-4o consistently surpasses other models               Needle-in-a-haystack (MMNeedle) benchmark to
                                             in long-context scenarios, but suffers from              comprehensively evaluate the long-context capa-
                                             hallucination problems in negative samples,              bilities of MLLMs. Fig. 1 shows a simple exam-
                                             i.e., when needles are not in the haystacks.             ple: The MLLMs are presented with a haystack
                                             Our comprehensive long-context evaluation of             of images, consisting of M = 10 images, each
                                             MLLMs also sheds lights on the considerable              containing N × N = 2 × 2 = 4 sub-images (see
                                             performance gap between API-based and open-
                                                                                                      Figure 1(b)). Additionally, a caption is provided for
                                             source models. All the code, data, and instruc-
                                             tions required to reproduce the main results
                                                                                                      one of the sub-images in the haystack, as shown in
                                             are available at https://github.com/Wang-ML-             green text in Figure 1(c). The goal of the MLLMs
                                             Lab/multimodal-needle-in-a-haystack.                     is to identify the needle, namely the sub-image
                                                                                                      highlighted in the green box in Figure 1(a), which
                                         1   Introduction                                             corresponds to the caption.
                                         Recent breakthroughs in multimodal large lan-                   By using advanced techniques, such as image
                                         guage models (MLLMs) have enabled a wide range               stitching to increase input context length, we assess
                                         of applications, spanning from visual question an-           MLLMs’ ability to locate a target sub-image (nee-
                                         swering to cross-modal retrieval (Yue et al., 2023;          dle) within a large set of images (haystack) based
                                            * Correspondence     to:            Hengyi     Wang       on textual instructions, i.e., instructions with the
                                         <hengyi.wang@rutgers.edu>                                    target caption in Fig. 1(c). The highlights of our

                                                                                                  1
 (a) Needle Sub-Image              (b) Haystack Image Inputs                                (c) Text Inputs                        (d) LLM Outputs
                         Image 1            Image 5            Image 10                                                   Claude 3 Opus: 9, 2, 2 ❌
                                                                                  Given 10 images indexed from 1 to 10,
                        Sub-Images        Sub-Images          Sub-Images          each divided into 2*2 sub-images,       Gemini Pro 1.0: 10, 2, 4 ❌
                         1, 2, 3, 4       17,18,19, 20       37, 38, 39, 40       identify the sub-image that best        Gemini Pro 1.5: 5, 2, 1 ❌
                                                                                  matches the provided caption.           GPT-4V: 6, 2, 2 ❌
                                                                                  Respond with "index, row, column"       GPT-4o: 5, 2, 2
                                                                                  and nothing else …                      Fuyu-8B: Index:1. Row:2. Column: 3. ❌
                                      …                  …                                                                mPLUG-Owl-v2: -4, 6 ❌
                                                                                  Caption: A woman walking across a       IDEFICS2-8B: \n\n\n\n\n ❌
                                                                                  sandy beach holding a little kite.      LLaVA-Llama-3: \n===== ❌


Figure 1: MMNeedle evaluation overview. Correct answers are marked with checkmark (✓), while the incorrect
answers are marked with cross (×). Our evaluation setup involves the following key components: (a) Needle
Sub-Image: The needle sub-image to be retrieved based on the given caption. (b) Haystack Image Inputs:
The long-context visual inputs consist of M images, each stitched from N × N sub-images. (c) Text Inputs
(Instructions and Caption): Detailed instructions to MLLMs, followed by a caption describing the needle, i.e.,
sub-image 20. See Sec. A for MMNeedle’s complete instructions. (d) LLM Outputs: The answers from different
MLLMs, indicating their ability to accurately locate the needle in the haystack based on the given caption. The
expected output is composed of the model’s identification of the index, row, and column of the matching sub-image.
The results showcase the comparative performance of various models: GPT-4o correctly predicts the exact location
of the needle; Gemini Pro 1.5 only correctly predicts the image index of the needle; other API models predict
incorrect locations; open-source models often output with wrong formats.

MMNeedle benchmark include:                                                       best model, GPT-4o, whose accuracy drops from
  • Comprehensive Dataset. Our dataset ensures                                    97.00% for M = 10 images without sub-images
    sufficient samples for each setting, with a total                             (i.e., equivalent to 10 images in the haystack) to
    number of 40,000 images, 560,000 captions,                                    26.90% for M = 10 images with N ×N = 4×4 =
    and 280,000 needle-haystack pairs.                                            16 sub-images for each image (equivalent to 160
  • Diverse Settings. Our benchmark covers di-                                    images in the haystack). See Fig. 2 and more re-
    verse settings with varying context lengths, sin-                             sults in Sec. 4.
    gle and multiple needles, as well as positive
    and negative samples, among others (details
    in Sec. 3).                                                                   2      Related Work
  • Coarse-to-Fine Evaluation Metrics. We es-
    tablish a set of evaluation metrics, includ-                                  Existing benchmarks for MLLMs mainly focus on
    ing “existence accuracy”, “index accuracy”,                                   limited image inputs, such as reasoning (Yue et al.,
    and “exact accuracy”, to holistically evaluate                                2023; Padlewski et al., 2024; Lu et al., 2023; Song
    MLLM at the sequence-, image-, and sub-                                       et al., 2024), perception (Fu et al., 2024b; Yu et al.,
    image- levels (details in Sec. 3.4).                                          2023), hallucination (Guan et al., 2023), where the
  • Wide Coverage. Our evaluation covers both                                     answers are based on either single or only a hand-
    state-of-the-art API-based and state-of-the-art                               ful of images. They are therefore not suitable for
    open-source MLLMs, shedding light on their                                    evaluating MLLMs’ long-context capability for vi-
    long-context capabilities.                                                    sual inputs. Recent work (Fu et al., 2024c; Kuratov
   Our findings underscore a considerable perfor-                                 et al., 2024; Levy et al., 2024; Zhao et al., 2024) on
mance gap between models and reveal the hal-                                      LLMs employs the needle-in-a-haystack test (Kam-
lucination problem in state-of-the-art MLLMs                                      radt, 2023) to evaluate the long-context capability
through negative samples. For example, we find                                    of large language models (LLMs), where the LLM
that (1) there is still a large performance gap be-                               is expected to answer the question by finding the
tween state-of-the-art API-based and state-of-the-                                corresponding information among a long irrele-
art open-source models, (2) accuracy drops signifi-                               vant corpus as context. However, these datasets
cantly with more images in the haystacks, even                                    and benchmarks are not applicable for the mul-
for state-of-the-art API-based MLLMs such as                                      timodal setting. Google’s technical report (Reid
Claude 3 Opus and Gemini 1.0 Pro, and (3) all                                     et al., 2024) has showcased Gemini 1.5 Pro’s ca-
models (including Claude 3 Opus, Gemini 1.5 Pro,                                  pability of finding the needle in an audio or video
and GPT-4V) perform poorly in MMNeedle set-                                       haystack. However, its evaluation (1) involves only
tings with sub-images (e.g., N × N = 2 × 2 = 4                                    one single sample rather than a complete dataset,
sub-images in Fig. 1); this is true even for the                                  obviously lacking statistical significance and there-

                                                                              2
fore rendering the evaluation inconclusive 1 , and                 Table 1: Maximum numbers of images per request
(2) does not involve a large set of unrelated images,              for Azure GPT-4V/o , OpenAI GPT-4V/o, Claude, and
which is the focus of MMNeedle. There is also                      Gemini. "*" indicates that the OpenAI GPT-4V/o API
work on the retrieval capability of small objects in               supports at most 10 images with high quality. Other
                                                                   numbers are hard limits. See Appendix A for details.
a single large image (Pawlowski et al., 2019) or re-
trieval from large external image datasets (Brogan                   Model    GPT-4 (Az.)   GPT-4 (Op.)    Claude   Gemini
et al., 2019), but none of them are concerned with                   Limit         10           10∗          20       16
in-context image retrieval, particularly for long-
context multimodal evaluation.                                     et al., 2024) to output the location of the sub-image
   In contrast to existing benchmarks, our MMNee-                  (needle) in the correct format.
dle benchmark includes a dataset of 40,000 images,
                                                                   3.2   MMNeedle Dataset
560,000 captions, and 280,000 needle-haystack
pairs (more details in Sec. 3), rather than only one               Constructing Long Context. To evaluate the long-
(or a handful of) needle-haystack pair(s) (Kamradt,                context capability of MLLMs, we extend the con-
2023; Reid et al., 2024). MMNeedle also includes                   text length of visual inputs in the following two
a diverse set of metrics and evaluation protocols,                 aspects:
covering different numbers of needle sub-images                      • More Images: We increase the number of im-
and needle sub-images. These differences set MM-                        ages in the inputs for MLLMs to extend the
Needle apart from existing benchmarks and are                           visual context length. Specifically, we use two
essential to evaluate MLLMs’ long-context capa-                         different numbers of images M in the prompt,
bility comprehensively.                                                 i.e., M = 1 or M = 10. Note that we choose
                                                                        M = 10 because it is the largest number
3     MultiModal Needle in a Haystack                                   of input images that GPT-4V/GPT-4o can
      (MMNeedle)                                                        support (see Table 1 and Appendix A).
In this section, we introduce our MultiModal                         • Image Stitching: We stitch small images into
Needle-in-a-haystack (MMNeedle) benchmark.                              a single large image as the input. Specifically,
                                                                        we use N × N sub-images (N ∈ {1, 2, 4, 8})
3.1    Overview                                                         to compose a stitched image with N rows and
Problem Setting. Fig. 1 provides an overview                            N columns, each combination of row and col-
of our evaluation setup with a randomly selected                        umn indices (r,c) corresponding to a sub-image.
example from our MMNeedle dataset (details                              Fig. 1(b) shows an example of 2 × 2 stitching,
in Sec. 3.2). The MLLM is given (1) an image                            with 4 sub-images in 1 stitched image.
haystack, i.e., a sequence of M images, (M = 10                       Purpose of Image Stitching. The purpose of im-
in Fig. 1), with each image containing N × N sub-                  age stitching is to: (1) Extend the effective context
images (N = 2 in Fig. 1), and (2) a caption for one                length. For example, stitching M = 10 images,
of the sub-images, shown as green text in Fig. 1(c).               each with N × N = 8 × 8 sub-images, results
The MLLM’s goal is then prompted to find the nee-                  in a long context of 640 sub-images. This setup
dle, i.e., the sub-image which the caption describes.              tests MLLMs’ long-context capabilities. (2) Test
Note that our evaluation setup can be naturally ap-                MLLMs’ localization capability by requiring them
plied for video-based inputs by extracting images                  to pinpoint sub-images within a large image based
from individual frames, which would be interesting                 on specific captions. For details, see Appendix A.
future work.                                                          Combining both dimensions provides compre-
   Evaluation Goals. As illustrated in Fig. 1, our                 hensive settings for our evaluation: (M, N ) =
MMNeedle aims to evaluate the MLLMs’ three                         (1, 2), (1, 4), (1, 8), (10, 1), (10, 2), (10, 4), (10, 8).
key capabilities within one forward pass: (1) un-                  Note that (M, N ) = (1, 1) is excluded, as finding
derstanding the semantics of both visual and tex-                  an image within a single image is trivial. Note
tual inputs, (2) retrieving the sub-image (needle)                 that MMNeedle covers typical, real-world MLLM
from long-context images (haystack), and (3) un-                   use-cases. Specifically, single, complete images
derstanding and following the instructions (Xia                    correspond to our setting with the number of
   1
                                                                   images M = 10 and the stitch size N × N = 1 × 1.
     Our MMNeedle results show that Gemini 1.5 Pro’s per-
formance does drop a lot with long contexts, especially with          Single-Needle Setting, Multi-Needle Setting,
multiple sub-images in the same image.                             and the Number of Needles K. We also extend

                                                               3
the single-needle setting above, i.e., the number of             tute the haystacks for stitching size N in the
needles (and associated captions) per query K = 1,               M = 1 setting.
to a multi-needle setting, where there are K > 1               • Step 2: Sampling Multi-Image Haystacks.
needles.                                                         For each stitch size N ∈ {1, 2, 4, 8} in the
   Image Data. In this paper, we use the MS                      M = 10 setting, we sample 10 different im-
COCO 2014 validation set (Lin et al., 2014) as                   ages as a haystack from the 10,000 stitched im-
our source dataset for constructing our MMNeedle                 ages constructed in Step 1. We sample 10,000
dataset. Note that our data construction approach                such haystacks for stitching size N (ensuring
is agnostic to the dataset and can be applied to                 each haystack has no repetitive stitched im-
any dataset containing images with paired captions               ages).
that describe the content of the images. We re-                • Step 3: Generating Positive Samples. We
size each original image from the MS COCO 2014                   sample a sub-image as a needle from a unique
validation set to 256 × 256 pixels before stitching              haystack (i.e., M ×N ×N sub-images) in Step
them into a larger image. The image resolution                   1 or Step 2, obtain its associated caption MS
of 256 pixels is chosen to ensure sufficient image               COCO annotations, and use this caption as the
quality; our preliminary studies show that humans                query in our MMNeedle evaluation (see Fig. 1).
(and MLLMs) cannot effectively recognize MS                      We repeat this process for K times in multi-
COCO images with resolution lower than 256 (see                  needle settings, where K = 2 or K = 5 (ensur-
examples in Fig. 1 and more in Appendix A). We                   ing each needle is a unique sub-image). This
then stitch these sub-images using stitching sizes               process ensures that the needles are inside the
of 1 × 1, 2 × 2, 4 × 4, and 8 × 8, leading to larger             haystack.
images with resolutions of 256 × 256, 512 × 512,               • Step 4: Generating Negative Samples. From
1024 × 1024, and 2048 × 2048, respectively. Given                the MS COCO 2014 validation set, we sample
that Claude 3 supports a maximum resolution of                   an image outside the haystack in Step 1 or Step
1092 × 1092 pixels and GPT-4 (including GPT-4V                   2 and use the image as the needle for a negative
and GPT-4o) supports a maximum resolution of                     sample. We also obtain the needle’s associated
2000 pixels for the long side of an image, we have               caption from MS COCO annotations and use
chosen 2048 pixels as the maximum resolution for                 it as the query in our MMNeedle evaluation.
our stitched images. Note that these models will re-             We repeat this process for K times in multi-
size images that exceed their respective size limits.            needle settings, where K = 2 or K = 5 (ensur-
                                                                 ing each needle refers to a unique sub-image).
3.3   Dataset Construction: Automated                            This ensures that the needles are outside the
      Sampling                                                   haystack.
Positive and Negative Samples. Our dataset is di-              With the process above, we construct 5,000 pos-
vided into (1) positive samples, where a sub-image          itive and 5,000 negative samples for each setting
(needle) exists in the context (haystack) to match          (M, N, K), where M ∈ {1, 10}, N ∈ {1, 2, 4, 8},
the given caption, and (2) negative samples, where          and K ∈ {1, 2, 5}.
no sub-image (needle) exists in the context that can
match the given caption. To construct the dataset           3.4   Evaluation Metrics
with balanced data distribution, we generate 5000           As mentioned in the previous sections, there are
samples each for positive and negative samples for          two “axes” for different settings in our MMNeedle
each (M, N, K) combination, leading to 280,000              evaluation: (1) the number of input images M ,
needle-haystack pairs in total.                             which indicates how many images are passed as
   Sampling Process. Specifically, we construct             inputs to an MLLM, and (2) the stitching size N ,
our dataset with the following sampling process:            where N is the number of total columns/rows of
  • Step 1: Sampling Single-Image Haystacks.                sub-images (where N = 1 means that each input
    For each stitch size N ∈ {1, 2, 4, 8}, we               image is the original image from the MS COCO
    first construct 10,000 stitched images, with            2014 validation set, otherwise, it is N × N images
    each sub-image randomly sampled from the                stitched as one). Increasing each of these axes adds
    MS COCO validation dataset (ensuring each               difficulty to MLLMs due to the increased context
    stitched image has no repetitive sub-images).           length, i.e., the haystack size. We propose and use
    These 10,000 stitched images directly consti-           the following evaluation metrics:

                                                        4
   Single Needle. For the single-needle setting, we                the ground truth m. For multi-needle settings,
define three different metrics to evaluate as follows:             predictions are considered correct only if the
  • Existence Accuracy is the proportion of sam-                   MLLM predicts the correct m for all needles.
     ples in which the model correctly predicts                    Note that even for the M = 1 settings, the
     whether the needle exists in the input image                  index accuracy may not be perfect (100%), be-
     sequence.                                                     cause the model can fail to output the only
  • Index Accuracy is the proportion of samples                    image index “1”. Therefore, we also evaluate
     where the model correctly predicts the index                  the index accuracy of different models in the
     m ∈ {1, . . . , M } of the stitched image con-                M = 1 settings (see Sec. 4.3 for details).
     taining the needle (e.g., m = 5 in Fig. 1).                 • Exact Accuracy is measured by whether the
  • Exact Accuracy (success rate of the needle                     tuple (m̂, r̂, ĉ) predicted by MLLM matches
     retrieval (Reid et al., 2024)) is the proportion              the ground truth (m, r, c). For multi-needle
     of samples where the model correctly predicts                 test, predictions are considered correct only if
     the needle sub-image’s location, i.e., index m,               the MLLM predicts the correct (m, r, c) for all
     row r and column c.                                           needles.
   Multiple Needles. We use similar metrics for
the multi-needle setting (details in Appendix B).            4     Experiments
   Coarse-to-Fine Evaluation. From the def-
                                                             In this section, we describe the evaluation results
initions, we can see that these accuracies
                                                             of various MLLMs on our MMNeedle dataset.
satisfy the relation “Existence Accuracy” ≥
“Index Accuracy” ≥ “Exact Accuracy” for a given              4.1    Evaluated MLLMs
model and evaluation setting (M, N, K). This indi-
cates a coarse-to-fine evaluation using our devised          We conduct MMNeedle evaluation for both API-
metrics.                                                     based models and open-source models:
   Automated Evaluation Protocol. We design an                 • API-Based Models. We evaluate state-of-the-
automated evaluation protocol for the defined three              art API-based MLLMs, including Claude 3
metrics as follows:                                              Opus (Feb 2024) (ant, 2023), Gemini Pro 1.0
  • Ground Truth Format. (1) For each positive                   (Feb 2024) (Team et al., 2023), Gemini Pro
     sample, i.e., the needle sub-image is in the con-           1.5 (May 2024) (Reid et al., 2024), GPT-4V
     text, the ground-truth output is “m, r, c” that             (March 2024) (Achiam et al., 2023), and GPT-
     describes the location of the needle, where m               4o (May 2024) (ope, 2024).
     is the image index (m ∈ 1, ..., M ), and r, c are         • Open-Source Models. We evaluate top
     the row and column of the sub-image (needle)                open-source multimodal LLMs, including
     in image m, respectively (r, c ∈ 1, ..., N ). (2)           CogVLM (CogVLM-17B/CogVLM2-Llama-
     For each negative sample, i.e., no needle sub-              3) (Wang et al., 2023), Fuyu-8B (Bavishi
     image is in the context, the ground-truth output            et al., 2023), mPLUG-Owl-v2 (Ye et al.,
     is “-1”, indicating the needle does not exist.              2023), InstructBLIP (InstructBLIP-Vicuna-
     The multi-needle setting uses a similar format              13B/InstructBLIP-Flan-T5-XXL) (Dai et al.,
     (details in Appendix B).                                    2024), IDEFICS2 (Laurençon et al., 2024),
  • Existence Accuracy is measured by whether                    and LLaVA-Llama-3 (Li et al., 2024). Note
     the MLLM outputs “-1” (in multi-needle set-                 that CogVLM and InstructBLIP do not support
     tings, we match “-1” for all the needles, sep-              multi-image inputs; therefore, we do not test
     arated by “;”, or alternatively just one “-1”).             them for our multi-image (M = 10) settings.
     Specifically, for positive samples (targets ex-           See Appendix C for more details on evaluated
     ist), the existence accuracy is the proportion          MLLMs.
     of samples where the MLLM does not predict
     “-1”, and for negative samples (targets do not          4.2    Overview of MMNeedle Evaluation
     exist), the existence accuracy is the proportion               Results
     of of samples where the MLLM predicts “-1”              Fig. 2 shows an intuitive comparison of the ex-
     (see Sec. 4.3 for details).                             act accuracy (defined in Sec. 3.4) across advanced
  • Index Accuracy is measured by whether the                MLLMs in various single-needle (K = 1) settings,
     image index m̂ predicted by MLLM matches                including Claude 3 Opus, Gemini Pro 1.0, Gemini

                                                         5
              Claude-3 Gemini-1.0 Gemini-1.5                          GPT-4V      GPT-4o LLaVA-Llama-3
                                                                                                                   100
M=1, N=2
                  52.25            29.53            90.34              86.09         94.60           43.80


M=1, N=4                                                                                                           80

                  12.30            24.78            39.85              54.72         83.00           17.50


M=1, N=8
                                                                                                                   60
                   1.60             2.11            29.81               7.30         19.00           3.30

M=10, N=1
                  66.93            16.25            89.94              72.36         97.00           0.00
                                                                                                                   40
M=10, N=2
                   4.60             4.82            45.21              34.24         81.80           0.00


M=10, N=4
                                                                                                                   20
                   0.40             0.40            6.09                7.58         26.90           0.00


M=10, N=8
                                                                                                                   0
                   0.00             0.00            0.62                0.00         1.00            0.00

Figure 2: MMNeedle evaluation performance comparison (Claude-3 refers to Claude 3 Opus, and Gemini-1.0/1.5
refers to Gemini Pro 1.0/1.5). The x-axis shows the results of different models, and the y-axis shows the results
on various input image number M and stitching size N . For each row, i.e., setting (M, N ), we show the average
accuracy (%) of each model. For each stitched image, the color of row r, the column c indicates the accuracy of
predicting the exact position for samples with the “needle” sub-image in position (r, c) of the stitched image. For the
M = 10 setting, we show the average accuracy of each location (r, c) over 10 images. A redder cell indicates lower
accuracy, while a greener cell indicates higher accuracy. The best result for each row is marked with underlining.

Pro 1.5, GPT-4V, GPT-4o, and LLaVA-Llama-3.                         ples, where Gemini Pro 1.5 reaches the best
Each heatmap is divided into N × N cells, where                     performance and GPT-4o is the second-best.
the cell at row r, column c is marked in a color                  • Capability of the Open-Source Models:
that indicates the average accuracy of the model                    LLaVA-Llama-3, as a top open-source model,
predicting the exact location for needle sub-images                 enjoys comparable performance with frontier
at (m, r, c) (m is the image index of the needle).                  API-based models such as Claude 3 Opus and
We highlight the following observations:                            Gemini Pro 1.0 for M = 1 samples, while
                                                                    lagging behind in M = 10 samples.
  • Impact of Stitching Size N and Input Im-
                                                                We also analyze the error patterns. As illustrated
    age Number M : For an MLLM (one column
                                                                in Fig. 2, the models demonstrate higher accuracy
    in Fig. 2), if we fix the number of input images
                                                                when the needles are positioned in the corners of
    M , the accuracy drops quickly when increas-
                                                                the image compared to when they are located in
    ing the stitching size N . This drop is more
                                                                the center. This trend is particularly pronounced
    significant for M = 10 than for M = 1, where
                                                                in Gemini-1.5 and LLaVA-Llama-3, in contrast to
    the accuracy drops to near zero for all models
                                                                GPT-4o. See Sec. 4.3 below for details and more
    on samples with M = 10, N = 8.
                                                                evaluation results.
  • Capability of the API-Based Models: For
    a fixed (M, N ) pair (one row in Fig. 2), the
                                                                4.3    Detailed Results of the Three Defined
    performance varies significantly for different
                                                                       Metrics
    MLLMs, particularly for samples with low
    stitching size N . GPT-4o achieves the high-                In this section, we discuss the results of the MM-
    est accuracy except for M = 1, N = 8 sam-                   Needle evaluation in various settings of (M, N, K)

                                                            6
Table 2: Accuracy (%) for the M = 1 setting. We mark the best results with bold face. Note that the existence
accuracy is measured by whether the model outputs “-1”. The index accuracy is not always 100% because the
model can fail to output the only image index “1”.

                        Stitching                                      2×2                              4×4                                 8×8
                        Metrics                            Existence    Index      Exact    Existence     Index       Exact   Existence       Index    Exact
                        Claude 3 Opus                         75.38     74.77      52.25      58.70       58.00       12.30      56.36        54.85    1.60
                        Gemini Pro 1.0                        97.10     85.09      29.53      88.42       82.88       24.78      55.62        45.18    2.11
 API-Based Models       Gemini Pro 1.5                        99.59     99.38      90.34      98.85       98.44       39.85      96.65        96.65    29.81
                        GPT-4V                                92.64     92.64      86.09      97.29       97.19       54.72      98.20        98.20    7.30
                        GPT-4o                                99.00     99.00      94.60      99.50       99.50       83.00      99.60        99.60    19.00
                        CogVLM-17B                             99.90      0.80      0.00     97.50        3.30         0.10       96.90       22.90    0.30
                        CogVLM2-Llama-3                        69.10     24.60      7.30     69.90       16.40         0.90       55.90        5.30    0.10
                        Fuyu-8B                               100.00     0.50       0.00     100.00       0.00        0.00       100.00        0.00    0.00
                        mPLUG-Owl-v2                           96.60     48.60      1.90     90.70       34.30         0.30       86.30       36.90    0.70
 Open-Source Models
                        InstructBLIP-Vicuna-13B               100.00     6.90       0.00     100.00      11.70        0.00       100.00       32.00    0.00
                        InstructBLIP-Flan-T5-XXL              100.00    100.00      3.80     100.00      100.00       6.20       100.00       93.00    2.20
                        IDEFICS2-8B                            75.80     69.30     18.90     95.80       86.00         7.80       39.60       24.50    0.90
                        LLaVA-Llama-3                         100.00    93.70      43.80      97.20       93.00       17.50      95.40        95.30    3.30


Table 3: Accuracy (%) for the M = 10 setting. We mark the best results with bold face. Note that the existence
accuracy is measured by whether the model outputs “-1”.
                      Stitching                      1×1                           2×2                          4×4                           8×8
                      Metrics            Existence    Index    Exact   Existence    Index   Exact   Existence    Index   Exact    Existence    Index    Exact
                      Claude 3 Opus       83.77       67.23    66.93    66.60        9.90    4.60     64.78       6.46   0.40       54.13       5.93    0.00
                      Gemini Pro 1.0      83.66       33.90    16.25    81.63       10.74    4.82     58.92       4.81   0.40       18.11       1.61    0.00
 API-Based Models     Gemini Pro 1.5      97.08       90.04    89.94    98.84       53.42   45.21     96.17      17.26   6.09       89.02       9.86    0.62
                      GPT-4V              95.11       75.59    72.36    98.32       52.10   34.24     99.80      24.87   7.58       99.50      10.57    0.00
                      GPT-4o              99.00       97.00    97.00    99.60       87.20   81.80     100.00     45.00   26.90      99.80      17.80    1.00
                      Fuyu-8B             100.00      0.00      0.00    100.00      0.00    0.00      100.00      0.00    0.00     100.00       0.00    0.00
                      mPLUG-Owl-v2         15.90      5.60      0.40    70.10       5.20    0.10       88.50      8.10    0.00      86.10       6.30    0.00
 Open-Source Models
                      IDEFICS2-8B          71.10      0.30      0.00    93.80       0.70    0.00       99.60      6.40    0.00      96.60       2.40    0.00
                      LLaVA-Llama-3       100.00      0.20      0.00    100.00      0.10    0.00      100.00      0.00    0.00     100.00       0.00    0.00



across three metrics: Existence, Index, and Exact                                models’ exact accuracy by at least 7.06%, 36.59%,
Accuracy, as defined in Sec. 3.4. More results are                               19.32%, and 0.38% on 1 × 1, 2 × 2, 4 × 4, and
available in Appendix D.                                                         8 × 8 stitching, respectively. These results indi-
   Results on Single-Image Samples (M = 1).                                      cate stronger long-context capability of GPT-4o for
Table 2 shows the accuracy on samples in the                                     multi-image samples compared to other state-of-
M = 1 setting, with three different stitching scenar-                            the-art models, such as GPT-4V and Claude 3 Opus.
ios (i.e., N × N as 2 × 2, 4 × 4, and 8 × 8). GPT-4o                             In contrast, open-source models only achieve near-
achieves the highest exact accuracy 94.60% and                                   zero exact accuracy in all stitching sizes. Note that
83.00% for the 2 × 2 and 4 × 4 stitching, respec-                                from 1 × 1 to 4 × 4 stitching, GPT-4o’s exact accu-
tively, while Gemini Pro 1.5 achieves the highest                                racy drops rapidly from 97.00% to 26.90%, while
exact accuracy, 29.81%, for the 8 × 8 stitching.                                 its index accuracy drops from 97.00% to 45.00%;
Among open-source models, LLaVA-Llama-3 per-                                     this shows that even the best performing MLLM
forms well in simpler stitching settings, outper-                                struggles in long-context needle test, verifying the
forming Gemini Pro 1.0 by 14.27% on 2 × 2 stitch-                                effectiveness of both our coarse-to-fine metrics and
ing, and Claude 3 Opus by 5.20% on 4×4 stitching.                                MMNeedle’s dataset in stress-testing MLLMs.
The results highlight that while open-source models                                 Results on Multi-Needle Samples (K > 1). Ta-
can match or exceed API-based models in simpler                                  ble 4 shows the results of different models on multi-
contexts or metrics, they generally lag behind in                                needle samples, i.e., the number of needles K = 2.
more complex stitching scenarios.                                                Gemini Pro 1.5 achieves the highest exact accuracy
   Results on Multi-Image Samples (M > 1).                                       87.88% on 2 × 2 samples, and GPT-4o achieves
Table 3 extends our evaluation to multi-image sam-                               the highest exact accuracy 57.00% on 4 × 4 sam-
ples, i.e., M = 10. It shows that GPT-4o con-                                    ples. In contrast, the exact accuracy of open-source
sistently performs best in terms of index/exact ac-                              models is close to zero for all stitching sizes. These
curacy for all stitching sizes, outperforming other                              results indicate a large gap between the API-based

                                                                           7
Table 4: Accuracy (%) for samples with M = 1 in the 2-needle setting. We mark the best results with bold face.
Existence accuracy is measured by whether the model outputs “-1” for all the needles. Index accuracy is not always
100% because models can fail to output the only image index “1”.

                               Stitching                                              2×2                              4×4                          8×8
                               Metrics                                   Existence         Index   Exact   Existence    Index   Exact   Existence    Index   Exact
                               Claude 3 Opus                              100.00           66.00   32.00     97.00      31.00    1.00     98.00      25.00   0.00
                               Gemini Pro 1.0                             100.00           79.80    9.09     95.00      50.00    2.00     68.00      11.00   0.00
 API-Based Models              Gemini Pro 1.5                             100.00           94.95   87.88    100.00      84.00   22.00     98.00      80.00   6.00
                               GPT-4V                                     100.00           90.72   71.13    100.00      95.00   34.00    100.00      93.41   1.10
                               GPT-4o                                     100.00           84.00   76.00    100.00      84.00   57.00    100.00      78.00   2.00
                               CogVLM-17B                                 100.00           0.00    0.00     100.00      0.00    0.00     100.00      0.00    0.00
                               CogVLM2-Llama-3                            100.00           0.00    0.00     100.00      0.00    0.00     100.00      0.00    0.00
                               Fuyu-8B                                    100.00           0.00    0.00     100.00      0.00    0.00     100.00      0.00    0.00
                               mPLUG-Owl-v2                                98.00            0.00   0.00     94.00       2.00    0.00      96.00       3.00   0.00
 Open-Source Models
                               InstructBLIP-Vicuna-13B                    100.00           0.00    0.00     100.00      0.00    0.00     100.00      0.00    0.00
                               InstructBLIP-Flan-T5-XXL                   100.00           17.00   1.00     100.00      0.00    0.00     100.00      0.00    0.00
                               IDEFICS2-8B                                100.00           0.00    0.00     100.00      0.00    0.00     100.00      0.00    0.00
                               LLaVA-Llama-3                              100.00           0.00    0.00     100.00      2.00    0.00     100.00      12.00   0.00


Table 5: Existence Accuracy (%) for the negative sam-                                           significantly, with some generally underperforming
ples (the ground truth is “-1”). We mark the best results                                       compared to API-based models (e.g., CogVLM-
with bold face. Note that the existence accuracy is mea-
                                                                                                17B, Fuyu-8B, InstructBLIP and LLaVA-Llama-
sured by whether the model outputs “-1”. “-” means
that the models do not support multi-image inputs.                                              3), while others demonstrate high existence accu-
                                                                                                racy (e.g., CogVLM2-Llama-3, mPLUG-Owl-v2,
Stitching                   1×1          2×2               4×4               8×8
Context                    10 imgs   1 img   10 imgs   1 img   10 imgs   1 img   10 imgs
                                                                                                IDEFICS2-8B). Notably, IDEFICS2-8B achieves
API-Based Models                                                                                the highest accuracy of 62.00% on M = 1, N = 8
Claude 3 Opus
Gemini Pro 1.0
                            81.78
                            90.60
                                     77.88
                                     89.67
                                              54.10
                                              67.14
                                                       67.03
                                                       64.73
                                                                38.38
                                                                56.00
                                                                         51.10
                                                                         57.27
                                                                                  53.38
                                                                                  87.13
                                                                                                samples, indicating a low level of hallucination in
Gemini Pro 1.5
GPT-4V
                            92.23
                            90.57
                                     87.70
                                     92.98
                                              54.56
                                              36.01
                                                       65.88
                                                       52.70
                                                                18.77
                                                                 0.71
                                                                         33.75
                                                                          3.40
                                                                                  17.50
                                                                                  0.10
                                                                                                this setting.
GPT-4o                      89.40    91.90    34.80    61.60     1.30     3.10    0.20
Open-Source Models
                                                                                                   Summary. These results show that our exis-
CogVLM-17B                     -      3.80       -      3.50       -      2.50       -          tence, index, and exact accuracy are designed to
CogVLM2-Llama-3                -     90.30       -     65.50       -     52.70       -
Fuyu-8B                      0.00     0.00     0.00    0.00      0.00     0.00     0.00         differentiate the model capabilities across various
mPLUG-Owl-v2                91.70    36.00    35.60    16.20    12.70    12.70    13.40
InstructBLIP-Vicuna-13B        -      0.00       -      0.00       -      0.00       -          settings while also facilitating a transition from
InstructBLIP-Flan-T5-XXL       -      0.00       -      0.00       -      0.00       -
IDEFICS2-8B                 30.80    89.40     6.90    55.70     0.60    62.00     3.10         easier to more challenging tasks.
LLaVA-Llama-3                0.00    11.10     0.00    7.40      0.00     5.90     0.00
                                                                                                   For example, we demonstrate that various met-
and the open-source models. See Appendix D for                                                  rics highlight the long-context capabilities of mod-
more results and analysis on multi-needle samples                                               els under different settings:
(K = 2 or K = 5).
                                                                                                   • Exact Accuracy: In Table 2, where the number
   Results on Negative Samples. Table 5 shows                                                        of input images M = 1, we focus on evaluat-
the existence accuracy (defined in Sec. 3.4) for                                                     ing exact accuracy, which measures whether
negative samples (defined in Sec. 3.3). For API-                                                     the model correctly predicts both the row and
based models, Claude 3 Opus and Gemini Pro                                                           column of the needle.
1.0 perform well across different configurations,                                                  • Index Accuracy: In Table 3, where the num-
suggesting robustness in handling varied context-                                                    ber of input images M = 10, we emphasize
length for the negative samples. On the other hand,                                                  index accuracy, assessing whether the model
GPT-4V and GPT-4o achieve inferior accuracy on                                                       correctly identifies the image index within the
more complex settings, including multi-image in-                                                     image haystack. Together with Exact Accuracy,
puts (M = 10) and/or large stitching size (N = 4                                                     it is crucial for evaluating whether an MLLM
or N = 8). These results reveal that: (1) Even top                                                   can understand images and sub-images in the
API-based models severely suffer from hallucina-                                                     long-context scenario.
tion; they incorrectly believe the needle exists in                                                • Existence Accuracy: In Table 4, where negative
the haystack when it does not. (2) API-based mod-                                                    samples are introduced, we evaluate existence
els with stronger needle-retrieval performance, e.g.,                                                accuracy, which reflects whether the model cor-
GPT-4o, tend to suffer more from hallucination.                                                      rectly determines that the needle is not present
   The performance of open-source models varies                                                      in the haystack. This is particularly relevant

                                                                                            8
      for benchmarking hallucination in MLLMs.               not infringe on personal privacy. We ensure that
  These analyses underscore the different use cases          MMNeedle dataset does not contain any personally
  and the necessity of our coarse-to-fine metrics.           identifiable information or offensive content. We
                   Mean and Standard Error
                                                             bear all responsibility in case of violation of rights
                                                             and confirm that we use the CC BY 4.0 data license.
                                                                Despite these precautions, there remains a risk
                                                             that the benchmark’s capabilities could be misused,

Exact Accuracy
                                                             particularly in scenarios where models are pushed
                                                             to handle extensive visual contexts that may lead to
                                                             unintended inferences or biases. Additionally, the
                                                             risk of hallucination in negative samples, where the
                                                             model incorrectly identifies a nonexistent target,
                     Number of Samples                       highlights the importance of responsible use and
  Figure 3: Exact Accuracy of Models on Varying Sample       the need for thorough evaluation before deploying
  Sizes in the M = 1, N = 2 Setting.                         these models in high-stakes applications.
  4.4             Statistical Significance
                                                             7   Limitations
 Fig. 3 shows the results of our hypothesis test of
 exact accuracy (success rate) over varying sample           Our MMNeedle Benchmark assumes that the eval-
 sizes, i.e., from 100 to 1000 samples. The solid            uated MLLM can understand and follow both vi-
 lines indicate the exact accuracy, while the shaded         sual and textual instructions, and that the model
 areas indicate the standard error. The results show         can process multiple images as input in a single
 that for all models, (1) the accuracy stabilizes af-        query. While this is not general, we note that these
 ter 500 samples, and (2) the standard error drops           assumptions (and capabilities) are necessary for
 significantly as sample sizes increase from 100 to          modern, state-of-the-art MLLMs. Adding textual
 1000 samples. This demonstrates (1) the necessity           or visual index labels next to each image or sub-
 of using larger sample size and (2) the sufficiency         image could potentially enhance the performance
 of using a sample size of 1000, to achieve reliable         of models. However, we leave this exploration
 evaluation (see Appendix D for details and more             for future work for the following reasons: (1) Our
 experiments on statistical significance).                   MMNeedle’s goal is to measure MLLM’s long-
                                                             context capability on natural images. Accuracy of
  5              Conclusion                                  predicting sub-image indices serves as one way of
 We propose MMNeedle, a benchmark to evalu-                  measuring such capabilitiy, but the accuracy itself
 ate MLLMs’ long-context capabilities. MMNee-                is not the final goal. (2) This approach alters the
 dle includes a comprehensive dataset and estab-             original image content. MMNeedle is also limited
 lishes diverse settings as well as a systematic set         by the supported number M and stitching size N of
 of coarse-to-fine evaluation metrics. We reveal that        image inputs in MLLMs. However, our framework
 while API-based models, such as GPT-4o, outper-             can seamlessly accommodate larger M and N once
 form open-source models in long-context scenar-             open-source and API models (e.g., GPT-4o) begin
 ios, they still struggle with hallucination issues in       to support them.
 negative samples and challenges in large stitch-
 ing size/multi-needle retrieval. A limitation of our        8   Acknowledgements
 MMNeedle evaluation is the assumption that the              We sincerely appreciate the generous support from
 MLLM takes both images and texts as inputs and              the Microsoft Research AI & Society Fellowship,
 supports multiple-image inputs. However, we ar-             NSF Grant IIS-2127918, NSF CAREER Award
 gue that these are necessary requirements for an            IIS-2340125, NIH Grant 1R01CA297832, and the
 ideal MLLM.                                                 Amazon Faculty Research Award. This research is
                                                             also supported by NSF National Artificial Intelli-
  6              Ethical Considerations
                                                             gence Research Resource (NAIRR) Pilot and the
  Our MMNeedle dataset, created from MS COCO                 Frontera supercomputer, funded by the National
  images, adheres to ethical guidelines and ensures          Science Foundation (award NSF-OAC 1818253)
  that the usage of images is respectful and does            and hosted at the Texas Advanced Computing Cen-

                                                         9
ter (TACC) at The University of Texas at Austin.                 Furong Huang, Yaser Yacoob, et al. 2023. Hallu-
Finally, we extend our gratitude to the Center for               sionbench: An advanced diagnostic suite for en-
                                                                 tangled language hallucination & visual illusion
AI Safety (CAIS) for providing the essential com-
                                                                 in large vision-language models. arXiv preprint
puting resources that made this work possible.                   arXiv:2310.14566.

                                                               G. Kamradt. 2023. Needle in a haystack - pressure
References                                                       testing llms.  https://github.com/gkamradt/
                                                                 LLMTest_NeedleInAHaystack.
2023. Model card and evaluations for claude models,
  july 2023.                                                   Yuri Kuratov, Aydar Bulatov, Petr Anokhin, Dmitry
                                                                 Sorokin, Artyom Sorokin, and Mikhail Burtsev. 2024.
2024. Introducing gpt-4o: our fastest and most afford-           In search of needles in a 10m haystack: Recur-
  able flagship model.                                           rent memory finds what llms miss. arXiv preprint
                                                                 arXiv:2402.10790.
Josh Achiam, Steven Adler, Sandhini Agarwal, Lama
  Ahmad, Ilge Akkaya, Florencia Leoni Aleman,                  Hugo Laurençon, Léo Tronchon, Matthieu Cord, and
  Diogo Almeida, Janko Altenschmidt, Sam Altman,                 Victor Sanh. 2024. What matters when build-
  Shyamal Anadkat, et al. 2023. Gpt-4 technical report.          ing vision-language models?     arXiv preprint
  arXiv preprint arXiv:2303.08774.                               arXiv:2405.02246.

Rohan Bavishi, Erich Elsen, Curtis Hawthorne,                  Mosh Levy, Alon Jacoby, and Yoav Goldberg. 2024.
  Maxwell Nye, Augustus Odena, Arushi Somani, and               Same task, more tokens: the impact of input length on
  Saugnak Taşırlar. 2023. Introducing our multimodal           the reasoning performance of large language models.
  models.                                                       arXiv preprint arXiv:2402.14848.

Joel Brogan, Aparna Bharati, Daniel Moreira, Kevin             Bo Li, Kaichen Zhang, Hao Zhang, Dong Guo, Ren-
  Bowyer, Patrick Flynn, Anderson Rocha, and                     rui Zhang, Feng Li, Yuanhan Zhang, Ziwei Liu, and
  W Scheirer. 2019. Needle in a haystack: A frame-               Chunyuan Li. 2024. Llava-next: Stronger llms super-
  work for seeking small objects in big datasets. arXiv          charge multimodal capabilities in the wild.
  preprint arXiv:1903.10019.
                                                               Tsung-Yi Lin, Michael Maire, Serge Belongie, James
Lin Chen, Jinsong Li, Xiaoyi Dong, Pan Zhang, Yuhang             Hays, Pietro Perona, Deva Ramanan, Piotr Dollár,
  Zang, Zehui Chen, Haodong Duan, Jiaqi Wang,                    and C Lawrence Zitnick. 2014. Microsoft coco:
  Yu Qiao, Dahua Lin, et al. 2024. Are we on the                 Common objects in context. In Computer Vision–
  right way for evaluating large vision-language mod-            ECCV 2014: 13th European Conference, Zurich,
  els? arXiv preprint arXiv:2403.20330.                          Switzerland, September 6-12, 2014, Proceedings,
                                                                 Part V 13, pages 740–755. Springer.
Wenliang Dai, Junnan Li, Dongxu Li, Anthony
 Meng Huat Tiong, Junqi Zhao, Weisheng Wang,                   Haotian Liu, Chunyuan Li, Qingyang Wu, and Yong Jae
 Boyang Li, Pascale N Fung, and Steven Hoi.                      Lee. 2024. Visual instruction tuning. Advances in
 2024. Instructblip: Towards general-purpose vision-             neural information processing systems, 36.
 language models with instruction tuning. Advances
 in Neural Information Processing Systems, 36.                 Yuan Liu, Haodong Duan, Yuanhan Zhang, Bo Li,
                                                                 Songyang Zhang, Wangbo Zhao, Yike Yuan, Jiaqi
Chaoyou Fu, Peixian Chen, Yunhang Shen, Yulei                    Wang, Conghui He, Ziwei Liu, et al. 2023. Mm-
  Qin, Mengdan Zhang, Xu Lin, Jinrui Yang, Xiawu                 bench: Is your multi-modal model an all-around
  Zheng, Ke Li, Xing Sun, Yunsheng Wu, and Ron-                  player? arXiv preprint arXiv:2307.06281.
  grong Ji. 2024a. Mme: A comprehensive evaluation
  benchmark for multimodal large language models.              Pan Lu, Hritik Bansal, Tony Xia, Jiacheng Liu, Chun-
  Preprint, arXiv:2306.13394.                                    yuan Li, Hannaneh Hajishirzi, Hao Cheng, Kai-
                                                                 Wei Chang, Michel Galley, and Jianfeng Gao. 2023.
Xingyu Fu, Yushi Hu, Bangzheng Li, Yu Feng, Haoyu                Mathvista: Evaluating mathematical reasoning of
  Wang, Xudong Lin, Dan Roth, Noah A Smith, Wei-                 foundation models in visual contexts. arXiv preprint
  Chiu Ma, and Ranjay Krishna. 2024b. Blink: Multi-              arXiv:2310.02255.
  modal large language models can see but not perceive.
  arXiv preprint arXiv:2404.12390.                             Piotr Padlewski, Max Bain, Matthew Henderson,
                                                                 Zhongkai Zhu, Nishant Relan, Hai Pham, Donovan
Yao Fu, Rameswar Panda, Xinyao Niu, Xiang Yue, Han-              Ong, Kaloyan Aleksiev, Aitor Ormazabal, Samuel
  naneh Hajishirzi, Yoon Kim, and Hao Peng. 2024c.               Phua, et al. 2024. Vibe-eval: A hard evaluation suite
  Data engineering for scaling language models to 128k           for measuring progress of multimodal language mod-
  context. arXiv preprint arXiv:2402.10171.                      els. arXiv preprint arXiv:2405.02287.

Tianrui Guan, Fuxiao Liu, Xiyang Wu, Ruiqi Xian,               Nick Pawlowski, Suvrat Bhooshan, Nicolas Bal-
  Zongxia Li, Xiaoyu Liu, Xijun Wang, Lichang Chen,              las, Francesco Ciompi, Ben Glocker, and Michal


                                                          10
  Drozdzal. 2019. Needles in haystacks: On classi-                  Longagent: Scaling language models to 128k context
  fying tiny objects in large images. arXiv preprint                through multi-agent collaboration. arXiv preprint
  arXiv:1908.06037.                                                 arXiv:2402.11550.
Machel Reid, Nikolay Savinov, Denis Teplyashin,                 A     Details of the MMNeedle Dataset
 Dmitry Lepikhin, Timothy Lillicrap, Jean-baptiste
 Alayrac, Radu Soricut, Angeliki Lazaridou, Orhan Fi-           We include all the images, captions, prompts, and
 rat, Julian Schrittwieser, et al. 2024. Gemini 1.5: Un-        needle-haystack pairs of our MMNeedle Dataset
 locking multimodal understanding across millions of
 tokens of context. arXiv preprint arXiv:2403.05530.            at https://github.com/Wang-ML-Lab/multimodal-
                                                                needle-in-a-haystack.
Dingjie Song, Shunian Chen, Guiming Hardy Chen, Fei                Limits on the Image Numbers. We set the
  Yu, Xiang Wan, and Benyou Wang. 2024. Milebench:
                                                                maximum number of complete images to M = 10
  Benchmarking mllms in long context. arXiv preprint
  arXiv:2404.18532.                                             because this is the largest number of input images
                                                                that GPT-4V/4o can support. Note that our frame-
Gemini Team, Rohan Anil, Sebastian Borgeaud,                    work can easily handle larger N and M once open-
  Yonghui Wu, Jean-Baptiste Alayrac, Jiahui Yu,
  Radu Soricut, Johan Schalkwyk, Andrew M Dai,                  source and API models (e.g., GPT-4o) start to sup-
  Anja Hauth, et al. 2023. Gemini: a family of                  port them. Table 6 below summarizes each API-
  highly capable multimodal models. arXiv preprint              based model’s limit for the number of images.
  arXiv:2312.11805.
                                                                Table 6: Maximum number of images per request. "*"
Weihan Wang, Qingsong Lv, Wenmeng Yu, Wenyi                     indicates that the OpenAI GPT-4V/4o API also supports
 Hong, Ji Qi, Yan Wang, Junhui Ji, Zhuoyi Yang, Lei
                                                                a maximum of 10 images with high quality. Other num-
 Zhao, Xixuan Song, et al. 2023. Cogvlm: Visual ex-
 pert for pretrained language models. arXiv preprint            bers are hard limits.
 arXiv:2311.03079.
                                                                            API-Based Model         Limit
Congying Xia, Chen Xing, Jiangshu Du, Xinyi Yang,
  Yihao Feng, Ran Xu, Wenpeng Yin, and Caim-                                Azure GPT-4V/4o         10
  ing Xiong. 2024. Fofo: A benchmark to eval-                               OpenAI GPT-4V/4o        10∗
  uate llms’ format-following capability. Preprint,                         Claude 3 Opus           20
  arXiv:2402.18667.
                                                                            Gemini 1.0 Pro          16
Qinghao Ye, Haiyang Xu, Jiabo Ye, Ming Yan, Haowei
  Liu, Qi Qian, Ji Zhang, Fei Huang, and Jingren Zhou.              It is worth noting that:
  2023. mplug-owl2: Revolutionizing multi-modal                     • Azure OpenAI API only supports 10 images
  large language model with modality collaboration.                   for GPT-4V/4o. For example, an Azure doc-
  arXiv preprint arXiv:2311.04257.
                                                                      ument states that “When uploading images,
Kaining Ying, Fanqing Meng, Jin Wang, Zhiqian Li,                     there is a limit of 10 images per chat request.”
  Han Lin, Yue Yang, Hao Zhang, Wenbo Zhang, Yuqi                     Another Azure document states that “GPT-4o
  Lin, Shuo Liu, Jiayi Lei, Quanfeng Lu, Runjian Chen,                max images per request” is 10.
  Peng Xu, Renrui Zhang, Haozhe Zhang, Peng Gao,
  Yali Wang, Yu Qiao, Ping Luo, Kaipeng Zhang, and                  • Regular OpenAI API also supports a maximum
  Wenqi Shao. 2024. Mmt-bench: A comprehensive                        of 10 images with high quality. Specifically, an
  multimodal benchmark for evaluating large vision-                   OpenAI document states that “the token cost of
  language models towards multitask agi. Preprint,                    a given image is determined by two factors: its
  arXiv:2404.16006.
                                                                      size, and the detail option on each image_url
Weihao Yu, Zhengyuan Yang, Linjie Li, Jianfeng Wang,                  block”. Therefore, to ensure sufficient qual-
  Kevin Lin, Zicheng Liu, Xinchao Wang, and Lijuan                    ity/resolution of image inputs, we cannot up-
 Wang. 2023. Mm-vet: Evaluating large multimodal
                                                                      load more than 10 images to GPT-4V/4o in the
  models for integrated capabilities. arXiv preprint
  arXiv:2308.02490.                                                   MMNeedle benchmark.
                                                                    • Other models also have a limit on the number
Xiang Yue, Yuansheng Ni, Kai Zhang, Tianyu Zheng,                     of input images (e.g., 20 for Claude and 16
  Ruoqi Liu, Ge Zhang, Samuel Stevens, Dongfu Jiang,
  Weiming Ren, Yuxuan Sun, et al. 2023. Mmmu:                         for Gemini). Specifically, the Claude 3 Opus
  A massive multi-discipline multimodal understand-                   document states that “You can include multiple
  ing and reasoning benchmark for expert agi. arXiv                   images in a single request (up to 5 for claude.ai
  preprint arXiv:2311.16502.                                          and 20 for API requests)”, and the Gemini 1.0
Jun Zhao, Can Zu, Hao Xu, Yi Lu, Wei He, Yiwen                        Pro Vision supports up to “16 images” as “Max-
  Ding, Tao Gui, Qi Zhang, and Xuanjing Huang. 2024.                  imum number of images per request”.

                                                           11
               Figure 4: Random samples of 8 × 8 stitched images in the MMNeedle dataset.

  Therefore, to ensure a fair comparison, we con-           • Image stitching enables us to conduct addi-
ducted all multi-image experiments on the M = 10              tional evaluation on MLLMs’ capability in lo-
images setting.                                               calization and retrieval of sub-images within
                                                              the complete input images, which is another
   Purpose of Image Stitching. The reason we
                                                              important aspect of long-context problems.
introduce stitching with N × N > 1 × 1 is as
follows:
                                                          Resolution of Sub-Images.             As discussed
  • API-based models, such as GPT-4V/4o, can              in Sec. 3.2 of the main paper, we find that humans
    support at most 10 images as inputs, which is         and LLMs cannot effectively recognize MS COCO
    surprisingly small. To further evaluate long          images with a resolution lower than 256. Fig. 4
    contexts with more images, we decided to in-          shows 4 random samples with 8 × 8 stitching from
    troduce image stitching. As a result, when            our MMNeedle dataset. As demonstrated in these
    M = 10, N × N = 8 × 8, there are equiva-              images, our 256 × 256 resolution ensures a rea-
    lently 640 sub-images in the context, which is        sonable balance of input tokens and image quality.
    sufficiently large compared to the API limits         Consequently, for a stitch size of N ×N , the overall
    of a few images.                                      resolution becomes 256N × 256N , resulting in a

                                                     12
longer input context length that scales linearly with           negative samples in our dataset, respectively. Due
the stitch size N . This approach ensures that we do            to time and rate limits, as well as the high cost of
not downsample the sub-images in the stitched im-               testing API models, we are able to test 2000 sam-
age, while still maintaining high image quality for             ples for each single-needle setting and 200 samples
the model’s comprehension. The Azure OpenAI                     for each multi-needle setting. However, our test
document states that: “If an image is ambiguous                 easily scale to more samples, such as other sam-
or unclear, the model will do its best to interpret             ples in our 10,000-sample dataset. We also show
it. However, the results might be less accurate. A              that the accuracy stabilizes when the test number
good rule of thumb is that if an average human                  reaches 1000 in Sec. 4.4 of the main paper and Ap-
can’t see the info in an image at the resolutions               pendix D.
used in low/high res mode, then the model can’t                    Prompt Design For single-needle evaluation, we
either.” The Anthropic document also states that                use the following prompt for the evaluated LLM:
“Ensure your images are clear and not too blurry
or pixelated. Claude may struggle to accurately                     Input = [Images] + Instructions + "\n"
interpret unclear or low-quality images.” Indeed,                           + "Caption: " + Caption
our stitched images demonstrate sufficiently high
resolution to be recognized by both humans and                    where the instructions to MLLMs is as follows:
MLLMs, and there is very little content loss or
                                                                    Given M images indexed from 1 to M , each
noise introduced.
                                                                    divided into N ×N sub-images, identify the
    Data Source. The asset we use in our paper,
                                                                    sub-image that best matches the provided
i,e, MS COCO 2014 dataset, is licensed under a
                                                                    caption. Respond with “index, row, column”
Creative Commons Attribution 4.0 License. This li-
                                                                    and nothing else. For example, “1, 2, 3”
cense permits the copying, redistribution, remixing,
                                                                    indicates the sub-image in the first image,
transforming, and building upon the material for
                                                                    second row, and third column. If no match
any purpose, including commercial use, provided
                                                                    is found, respond only with “-1”.
appropriate credit is given, and any changes made
are indicated. As a user of the MS COCO dataset,
                                                                   We use a similar prompt for the multi-needle
we acknowledge and comply with the requirements
                                                                setting. Specifically, for K-needle (K > 1) evalua-
of the CC BY 4.0 license.
                                                                tion, we use the following prompt for the evaluated
    Evaluation Metrics for Multiple Needles. As
                                                                MLLM:
mentioned in Sec. 3.4 of the main paper, we use
similar metrics for the multi-needle setting:                       Input = [Images] + Instructions + "\n"
   • Existence Accuracy is the proportion of sam-                      + "Caption 1: " + Caption_1 + "\n"+ "Caption 2: " + Caption_2
                                                                        + "\n" + ... + "Caption K: " + Caption_K,
      ples in which the model correctly predicts
      whether any needle exists, i.e., at least one tar-          where the instructions to MLLMs is as follows:
      get caption matches a sub-image in the input
      image sequence.                                              Given M images indexed from 1 to M ,
   • Index Accuracy is the proportion of samples                   each divided into N × N sub-images, iden-
      where the model correctly predicts the index                 tify the sub-images that best match the pro-
      m ∈ {1, ..., M } of the stitched image contain-              vided K captions. Respond in the format:
      ing the needle for all the needles.                          “index_1, row_1, column_1; ...; index_K,
   • Exact Accuracy is the proportion of samples                   row_K, column_K.” Only provide this in-
      where the model correctly predicts the needle                formation. For example, “1, 2, 3” indicates
      sub-image’s location, i.e., index m, row r and               the sub-image in the first image, second row,
      column c for all the needles.                                and third column. If no sub-image matches
    In this paper, we evaluate MLLMs with the num-                 a caption, respond with “-1” for that cap-
ber of needles K ∈ {1, 2, 5}. Our primary eval-                    tion.
uation involves testing on the first 1000 positive
and the first 1000 negative samples in our dataset                 Note that for both single-needle and multi-needle
using a single needle. As complementary experi-                 settings, when M = 1 or N = 1, we remove the
ments, we also test multi-needle settings with 2 and            “s” in “images” or “sub-images” in our prompt for
5 needles on the first 100 positive and the first 100           coherent description, respectively.

                                                           13
B    Details of Evaluation Process                                   by the MLLM matches the ground truth
                                                                     (m, r, c) in multi-needle samples, where pre-
Automated Evaluation Protocol. As discussed                          dictions are considered correct only if the
in Sec. 3.4 of the main paper, we design an au-                      MLLM predicts the correct (m, r, c) for each
tomated evaluation protocol for the three defined                    individual needle.
metrics as follows:
  • Ground Truth Format. For each caption in a                      This automated evaluation protocol can be seam-
    test sample, (1) if it is positive, i.e., the needle         lessly integrated with prompt design, where our
    sub-image is in the context, the ground-truth                prompts ask the MLLM to output in the format
    output is “m, r, c” that describes the location              of the ground truth. As discussed in Sec. 3.1 of
    of the needle, where m is the image index                    the main paper, the model can successfully pro-
    (m ∈ {1, ..., M }), and r, c are the row and                 duce a correct answer only if it understands our
    column of the sub-image (needle) in image m,                 instructions, recognizes where there are needles in
    respectively (r, c ∈ {1, ..., N }); (2) if it is neg-        the haystack that match the given text query (tar-
    ative, meaning no needle sub-image is in the                 get captions), and outputs in the correct format.
    context, the ground truth output is “-1”, indicat-           Otherwise, the MLLM may produce answers with
    ing the needle does not exist. For multi-needle              incorrect formats or meanings, resulting in failed
    settings, the ground truth is a concatenation of             cases.
    the ground-truth answer for each needle in the
    order of input captions, separated by “;”. For                  Our multimodal evaluation benefits from canon-
    example, for a 2-needle test with M = 10 and                 ical ground-truth answers and is therefore not af-
    N = 8, a positive answer can be “1, 2, 8; 10,                fected by the similarity of the needles to test and
    3, 5” and a negative answer should be “-1; -1”.              data points in the training set in terms of output
  • Existence Accuracy is measured by whether                    tokens.
    the MLLM outputs “-1” (in multi-needle set-
    tings, we match “-1” for all the needles, sep-               (1) Compared to other open-ended evaluations,
    arated by “;”, or alternatively just one “-1”).                  since we ask the MLLMs to output the loca-
    Specifically, for positive samples (targets ex-                  tions of the target sub-images, the model has no
    ist), the existence accuracy is the proportion                   back-doors to output a “seemingly” correct an-
    of samples where the MLLM does not predict                       swer as in other open-ended generation. These
    “-1”, and for negative samples (targets do not                   back-doors include learning the next token dis-
    exist), the existence accuracy is the proportion                 tribution from the training set and responding
    of of samples where the MLLM predicts “-1”.                      with the contents of other images.
  • Index Accuracy is measured by whether                        (2) Compared to multiple-choice questions, the
    the image index m̂ predicted by the MLLM                         chance that the model outputs coincidentally
    matches the ground truth m. For multi-needle                     match the correct answer is also much lower.
    settings, predictions are considered correct                     For example, the accuracy of a random guess in
    only if the MLLM predicts the correct m for all                  4-choice problems is always 25%, while even
    needles. Note that even for the M = 1 settings,                  in our easiest settings (1 image, 2 × 2 stitching;
    the index accuracy may not be perfect (100%),                    10 images, 1×1 stitching), the accuracy is 25%
    because the model can fail to output the correct                 and 10%, respectively.
    image index “1”. Therefore, we also evaluate
    the index accuracy of different models in the                   Post-Processing. In Table 3 of the main paper,
    M = 1 settings.                                              IDEFICS2-8B M = 1, N = 4 results on negative
  • Exact Accuracy is measured by whether the tu-                samples are as low as 20.20% due to its failure to
    ple (m̂, r̂, ĉ) predicted by the MLLM matches               follow instructions on the output format, particu-
    the ground truth (m, r, c). For multi-needle set-            larly affected by the “Answer: ” prefix in responses.
    tings, predictions are considered correct only               Therefore, we include additional parsing for this
    if the MLLM predicts the correct (m, r, c) for               case, resulting in an accuracy of 55.70% in the
    all needles.                                                 same setting. Specifically, we use additional filter-
  • (Multi-Needle) Individual Accuracy is mea-                   ing of the prefix “Answer:” for IDEFICS2-8B in
    sured by whether the tuple (m̂, r̂, ĉ) predicted            M = 1, N = 4 negative samples.

                                                            14
                                                                                     Claude 3 Opus        Gemini Pro 1.0           GPT-4V
C    Implementation Details                                                    0%                                                                 100




All the code, data, and instructions required to re-                          50%
                                                                                                                                                  80




                                                            Depth of Needle
produce the main experimental results are provided
in the supplementary materials (“Software” and                                100%
                                                                                                                                                  60



“Data”).                                                                             LLaVA-Llama-3        Gemini Pro 1.5           GPT-4o
                                                                               0%
                                                                                                                                                  40
   Compute and Resources. For the API-based
models, we used the corresponding API credits                                 50%                                                                 20

to conduct our experiments: Anthropic API for
Claude 3 Opus, Google Cloud API for Gemini Pro                                100%                                                                0
                                                                                     10   40   160 640    10   40   160 640   10   40   160 640
1.0 and Gemini Pro 1.5, and Azure OpenAI API                                                             Context Length
service for GPT-4V and GPT-4o. For the open-                  Figure 5: Accuracy (%) under different needle depths
source models, we used 2 Nvidia A100 GPUs for                 and context lengths on M = 10 samples. A redder cell
our evaluation. Each model required a few hours to            indicates lower accuracy, while a greener cell indicates
a few days to complete the evaluation, depending              higher accuracy.
on the API rate limit or GPU memory limit.
   Model Details. As discussed in Sec. 4.1 of the                    – Fuyu-8B (Bavishi et al., 2023) is a state-
main paper, we conduct MMNeedle evaluation for                         of-the-art, 8-billion-parameter model that
both API-based models and open-source models:                          excels in multimodal tasks compared to
  • API-based models are state-of-the-art multi-                       other models of similar size.
    modal LLMs with API calling access:                              – mPLUG-Owl-v2 (Ye et al., 2023) is an
      – Claude 3 Opus (ant, 2023) is the strongest                     updated version of mPLUG-Owl and also
         MLLM developed by Anthropic. We                               a state-of-the-art MLLM.
         use the model version claude-3-opus-                        – InstructBLIP (Dai et al., 2024) is an-
         20240229.                                                     other state-of-the-art MLLM for single-
      – Gemini Pro 1.0 (Team et al., 2023) is an                       image inputs. We evaluate InstructBLIP-
         advanced version of Google Gemini, offer-                     Vicuna-13B and InstructBLIP-Flan-T5-
         ing enhanced performance in multimodal                        XXL, which are its two strongest variants.
         tasks. We use the model version gemini-                     – IDEFICS2 (Laurençon et al., 2024) is the
        1.0-pro-vision-latest.                                         latest version of IDEFICS and also a state-
      – Gemini Pro 1.5 (Reid et al., 2024) is built                    of-the-art MLLM.
         upon Gemini Pro 1.0 with further optimiza-                  – LLaVA-Llama-3 (Li et al., 2024) is the
         tions in multimodal capability, serving as                    latest and strongest version of LLaVA (Liu
         the strongest model version of Google                         et al., 2024) and also a state-of-the-art
         Gemini. We use the model version gemini-                      MLLM.
        1.5-pro-latest.                                          Samples Skipped by API-based Models. Due
      – GPT-4V (Achiam et al., 2023) is an exten-             to the built-in filters for the API-based models, they
         sion of OpenAI’s GPT-4, equipped with                may refuse to answer questions for a small number
         vision capabilities for multimodal tasks.            of samples in our dataset. However, the number of
         We use Azure OpenAI API with the model               refused questions is limited to dozens out of 2,000
         version 2024-03-01-preview.                          samples in each setting. Therefore, excluding these
      – GPT-4o (ope, 2024) is the latest and                  vacant samples in the results does not affect any
         strongest variant of OpenAI’s GPT-4. We              of our conclusions. See the statistical significance
         use Azure OpenAI API with the model                  discussion in Appendix D, as well as Sec. 4.4 of
         version 2024-05-01-preview.                          the main paper.
  • Open-source models are state-of-the-art meth-
                                                              D                     More Experimental Results
    ods with open access to their weights:
      – CogVLM (Wang et al., 2023) is a state-                Effect of Needle Depth. We investigated the effect
         of-the-art MLLM for single-image in-                 of needle depth on the accuracy of MLLMs. Specif-
         puts. We evaluate CogVLM-17B-base                    ically, we tested different needle depths ranging
         and CogVLM2-Llama-3 (the latest and                  from 1 to 10 for M = 10 images in a single-needle
         strongest version).                                  setting. We calculated the accuracy for each depth,

                                                       15
Table 7: Exact Accuracy ± Standard Error (%) of GPT-4V for the 1-needle samples with different instruction
structures. We mark the best results with bold face.

  Stitching             1×1                  2×2                                          4×4                           8×8
  Instructions         10 imgs       1 img         10 imgs                        1 img         10 imgs         1 img      10 imgs
  Prompt + Caption   74.49±4.36    85.71±3.50   30.21±4.59                      45.00±4.97     8.16±2.74      8.00±2.71   0.00±0.00
  Caption + Prompt   74.49±4.36    80.61±3.95   33.33±4.71                      49.00±5.00     5.10±2.20      9.00±2.86   0.00±0.00
                                                                                    Mean and Standard Error
analyzing how well the models could identify the
correct needle image across various depths. Fig. 5
shows the accuracy of models on different needle


                                                               Exact Accuracy
depths and context lengths. The results show that
for all models, accuracy drops significantly with
increasing context lengths, while the accuracy of
different needle depths shows little variation for the
same model and context length.
   Statistical Significance. To ensure the robust-
                                                                                      Number of Samples
ness of our evaluation, we conducted hypothesis
                                                                 Figure 6: Exact Accuracy and Standard Error of Dif-
tests for the exact accuracy (mean of binary value
                                                                 ferent Models on M = 10, N = 1 Samples. The accu-
for each sample) of different models under the bi-               racies of all open-source models on these samples are
nomial distribution Binomial(1, p), where p is the               very close to 0%.
probability of success on an individual trial. The
standard error (SE) of this test is calculated as fol-           the M = 1, K = 5 setting, with three different
lows:                                                            stitching scenarios (i.e., N × N as 2 × 2, 4 × 4, and
                       r                                         8×8). GPT-4V achieves the highest exact accuracy
                          p(1 − p)
                 SE =               ,              (1)           34.41% and 8.16% for the 2×2 and 4×4 stitching,
                              s                                  respectively, with accuracy dropping significantly
where s is the number of trials (samples). Fig. 6                to 0.00% for the 8 × 8 stitching. All open-source
shows the mean and standard error of exact accu-                 models show zero exact accuracy across all settings,
racy for different models in the M = 1, N = 10                   falling behind in more needles (K = 5) scenarios.
setting. Note that InstructBLIP and CogVLM mod-                     Results on Multi-Needle Multi-Image Sam-
els do not support multi-image inputs; therefore                 ples. Table 9 shows the accuracy on samples in
we exclude them in the figure. The results indicate              the M = 10, K = 2 setting, with four different
that the accuracy stabilizes after approximately 500             stitching scenarios (i.e., N × N as 1 × 1, 2 × 2,
samples, and the standard error decreases signif-                4×4, and 8×8). GPT-4o achieves the highest exact
icantly as the sample size increases from 100 to                 accuracy of 88.00% and 53.00% for the 1 × 1 and
1000. This highlights the importance of utilizing                2 × 2 stitching, respectively, with accuracy drop-
larger sample sizes to ensure reliable evaluation                ping significantly to 5.00% for the 4 × 4 stitching.
results, as discussed in Sec. 4.4 of the main paper.                Table 10 shows the accuracy on samples in the
   Effect of the Instruction Order. Table 7 shows                M = 10, K = 5 setting, with four different stitch-
the exact accuracy of the GPT-4V model in each                   ing scenarios (i.e., N × N as 1 × 1, 2 × 2, 4 × 4,
different M, N setting on 100 random positive                    and 8 × 8). GPT-4o achieves the highest exact ac-
samples. “Prompt+Caption (default)” means our                    curacy of 69.00% for the 1 × 1 stitching, while its
prompt is followed by a caption in the instructions,             accuracy drops significantly to 8.00% for the 2 × 2
and “Caption+Prompt (alternative)” means a cap-                  stitching.
tion is followed by our prompt in the instructions.                 All open-source models show zero exact accu-
The results indicate that these two different ordered            racy across all settings, falling behind in more com-
instructions are not statistically significantly better          plex (M = 10) scenarios. These results indicate
than each other for any setting.                                 the difficulty of our multi-needle multi-image eval-
   Results on Multi-Needle Single-Image Sam-                     uation.
ples. In additional to Sec. 4.3 of the main pa-                     Results on Multi-Needle Negative Samples.
per, Table 8 shows the accuracy on samples in                    Table 11 and Table 12 show the existence accu-

                                                          16
Table 8: Accuracy (%) in the three metrics for the 5-needle, M = 1 samples. We mark the best results with bold
face. Note that the existence accuracy is measured by whether the model outputs “-1” for all the needles. The index
accuracy is not always 100 % because the model can fail to output the correct image index “1”.


 Stitching                                     2×2                                   4×4                               8×8
 Metrics                           Existence       Index      Exact      Existence     Index     Exact     Existence       Index      Exact
 API-based models
 Claude 3 Opus                       100.00        22.00       2.00       100.00       37.00      0.00       100.00        29.00      0.00
 Gemini Pro 1.0                      100.00        32.00       1.00       100.00       6.00       0.00       100.00        0.00       0.00
 Gemini Pro 1.5                      100.00        91.00      24.00       100.00       91.00      1.00       100.00        81.00      0.00
 GPT-4V                              100.00        55.91      34.41       100.00       68.37      8.16       100.00        61.62      0.00
 GPT-4o                              100.00        28.00      24.00       100.00       24.00      6.00       100.00        22.00      0.00
 Open-source models
 CogVLM-17B                          100.00        0.00       0.00        100.00       0.00       0.00       100.00          0.00     0.00
 CogVLM2-LLaMA-3                     100.00        0.00       0.00        100.00       1.00       0.00       100.00          0.00     0.00
 Fuyu-8B                             100.00        0.00       0.00        100.00       0.00       0.00       100.00          0.00     0.00
 mPLUG-Owl-v2                         98.00        0.00       0.00        98.00        2.00       0.00        98.00          0.00     0.00
 InstructBLIP-Vicuna-13B             100.00        0.00       0.00        100.00       0.00       0.00       100.00          0.00     0.00
 InstructBLIP-Flan-T5-XXL            100.00        0.00       0.00        100.00       0.00       0.00       100.00          0.00     0.00
 IDEFICS2-8B                         100.00        0.00       0.00        100.00       0.00       0.00       100.00          0.00     0.00
 LLaVA-LLaMA-3                       100.00        3.00       0.00        100.00       2.00       0.00       100.00          2.00     0.00
Table 9: Accuracy (%) in the three metrics for the 2-needle, M = 10 samples. We mark the best results with bold
face. Note that the existence accuracy is measured by whether the model outputs “-1” for all the needles.

 Stitching                        1×1                           2×2                            4×4                           8×8
 Metrics              Existence    Index   Exact    Existence    Index    Exact    Existence    Index    Exact   Existence    Index   Exact
 API-based models
 Claude 3 Opus         100.00      46.00   46.00     100.00       1.12    0.00        98.00      0.00    0.00     96.91        1.03    0.00
 Gemini Pro 1.0         92.93       3.03    0.00     98.00        1.00     0.00      100.00      0.00    0.00      99.00       0.00    0.00
 Gemini Pro 1.5        100.00      86.73   85.71     100.00      34.00    25.00      100.00      2.08    0.00      85.86       0.00    0.00
 GPT-4V                100.00      52.17   48.91     100.00      25.58     6.98      100.00      3.45    0.00     100.00       1.19    0.00
 GPT-4o                100.00      88.00   88.00     100.00      71.00    53.00      100.00     13.00    5.00     100.00       3.00    0.00
 Open-source models
 Fuyu-8B               100.00      0.00    0.00      100.00      0.00      0.00      100.00     0.00     0.00     100.00       0.00    0.00
 mPLUG-Owl-v2           66.00      0.00    0.00      90.00       0.00      0.00       97.00     0.00     0.00      96.00       0.00    0.00
 IDEFICS2-8B            59.00      0.00    0.00      94.00       0.00      0.00      100.00     0.00     0.00      99.00       0.00    0.00
 LLaVA-LLaMA-3         100.00      0.00    0.00      100.00      0.00      0.00      100.00     0.00     0.00     100.00       0.00    0.00

Table 10: Accuracy (%) in terms of the three metrics for the 5-needle, M = 10 samples. We mark the best results
with bold face. Note that the existence accuracy is measured by whether the model outputs “-1” for all the needles.

 Stitching                        1×1                           2×2                            4×4                           8×8
 Metrics              Existence    Index   Exact    Existence    Index    Exact    Existence    Index    Exact   Existence    Index   Exact
 API-based models
 Claude 3 Opus         100.00      32.32   32.32     100.00       0.00     0.00      100.00     0.00     0.00     100.00       0.00    0.00
 Gemini Pro 1.0        100.00       0.00    0.00     100.00       0.00     0.00      100.00     0.00     0.00     100.00       0.00    0.00
 Gemini Pro 1.5        100.00      82.83   13.13     100.00       7.00     0.00      100.00     0.00     0.00     100.00       0.00    0.00
 GPT-4V                100.00      28.12   25.00     100.00       1.14     0.00      100.00     0.00     0.00     100.00       0.00    0.00
 GPT-4o                100.00      73.00   69.00     100.00      37.00     8.00      100.00     0.00     0.00     100.00       0.00    0.00
 Open-source models
 Fuyu-8B               100.00      0.00    0.00      100.00      0.00      0.00      100.00     0.00     0.00     100.00       0.00    0.00
 mPLUG-Owl-v2           82.00      0.00    0.00      93.00       0.00      0.00       97.00     0.00     0.00     100.00       0.00    0.00
 IDEFICS2-8B            69.00      0.00    0.00      91.00       0.00      0.00       98.00     0.00     0.00      99.00       0.00    0.00
 LLaVA-LLaMA-3         100.00      0.00    0.00      100.00      0.00      0.00      100.00     0.00     0.00     100.00       0.00    0.00




                                                                  17
Table 11: Existence Accuracy (%) for the 2-needle negative samples (the ground truth is “-1; -1”). We mark the best
results with bold face. Note that the existence accuracy is measured by whether the model outputs “-1” for all the
needles. “-” means that the models do not support multi-image inputs.


             Stitching                    1×1             2×2                   4×4               8×8
             Context                     10 imgs   1 img       10 imgs   1 img   10 imgs   1 img   10 imgs
             API-based models
             Claude 3 Opus                45.00    14.00         0.00     5.00    1.00     4.00     8.33
             Gemini Pro 1.0               54.64    85.86        18.00    50.00    0.00     34.00    0.00
             Gemini Pro 1.5               79.59    71.00        31.00    50.00    7.37     22.00    17.00
             GPT-4V                       74.75    77.00        13.40    33.00    3.00     0.00     0.00
             GPT-4o                       80.00    67.00        25.00    51.00    3.00     2.00      0.00
             Open-source models
             CogVLM-17B                      -     0.00           -      0.00       -      0.00       -
             CogVLM2-LLaMA-3                 -     0.00           -      0.00       -      0.00       -
             Fuyu-8B                       0.00    0.00         0.00     0.00     0.00     0.00     0.00
             mPLUG-Owl-v2                 36.00    7.00         7.00     9.00     2.00     7.00     6.00
             InstructBLIP-Vicuna-13B         -     0.00           -      0.00       -      0.00       -
             InstructBLIP-Flan-T5-XXL        -     0.00           -      1.00       -      0.00       -
             IDEFICS2-8B                  39.00    0.00         7.00     0.00     0.00     0.00     1.00
             LLaVA-LLaMA-3                 0.00    0.00         0.00     0.00     0.00     0.00     0.00



racy for negative samples in multi-needle settings
(K = 2 or K = 5). In Table 11, representing the
K = 2 setting, Gemini Pro 1.5 achieves the highest
existence accuracy in the M = 10, N ∈ {2, 4, 8}
scenarios, indicating a low level of hallucination
for long-context samples. In contrast, in Table 12,
representing the K = 5 setting, GPT-4o achieves
the best existence accuracy of 25.00% and 37.00%
for M = 10, N = 2 and M = 1, N = 4 samples,
respectively.
   The performance of open-source models fall
behind in multi-needle negative samples, with
mPLUG-Owl-v2 and IDEFICS2-8B performing
better than others in both K = 2 and K = 5 set-
tings.
   Results on Multi-Needle Individual Samples.
Table 13, Table 14, Table 15, and Table 16 show
the individual accuracy for multi-needle samples
defined in Appendix B. Gemini Pro 1.5 achieves
the highest exact accuracy for N = 2 and N = 8
samples in both Table 13 and Table 14 (single-
image inputs), while GPT-4o achieves the highest
exact accuracy in both Table 15 and Table 16 (multi-
image inputs).




                                                          18
Table 12: Existence Accuracy (%) for the 5-needle negative samples (the ground truth is “-1; -1; -1; -1; -1”). We
mark the best results with bold face. Note that the existence accuracy is measured by whether the model outputs
“-1” for all the needles. “-” means that the models do not support multi-image inputs.


             Stitching                    1×1             2×2                     4×4                8×8
             Context                    10 imgs   1 img        10 imgs    1 img    10 imgs   1 img    10 imgs
             API-based models
             Claude 3 Opus               14.14     2.00          0.00      0.00     0.00      0.00     0.00
             Gemini Pro 1.0               1.00    32.00          0.00      1.01     1.00      0.00     0.00
             Gemini Pro 1.5              56.57    60.00          4.00     15.15     0.00      1.00     0.00
             GPT-4V                      73.63    65.96          8.99     17.00     0.00      0.00     0.00
             GPT-4o                      58.00    67.00         25.00     37.00     0.00      2.00     0.00
             Open-source models
             CogVLM-17B                     -      0.00            -       0.00       -       0.00       -
             CogVLM2-LLaMA-3                -      0.00            -       0.00       -       0.00       -
             Fuyu-8B                      0.00     0.00          0.00      0.00     0.00      0.00     0.00
             mPLUG-Owl-v2                40.00     5.00         2.00       5.00     3.00      2.00     3.00
             InstructBLIP-Vicuna-13B        -      0.00            -       0.00       -       0.00       -
             InstructBLIP-Flan-T5-XXL       -      0.00            -       0.00       -       0.00       -
             IDEFICS2-8B                 29.00     0.00         12.00      0.00     0.00      0.00     0.00
             LLaVA-LLaMA-3                0.00     0.00          0.00      0.00     0.00      0.00     0.00




Table 13: Individual Accuracy (%) in the three metrics for the 2-needle M = 1 samples. We mark the best results
with bold face. The index accuracy is not always 100 % because the model can fail to output the correct image
index “1”.

             Stitching                             2×2                      4×4                  8×8
             Metrics                          Index       Exact          Index     Exact     Index     Exact
             API-based models
             Claude 3 Opus                    82.01       49.74          55.62     10.00     49.67      2.61
             Gemini Pro 1.0                   89.34       30.96          67.25      9.36     25.38      1.54
             Gemini Pro 1.5                   97.47       93.43          92.00     42.50     89.00     26.00
             GPT-4V                           94.85       79.90          97.00     56.00     96.70      5.49
             GPT-4o                           96.28       86.17          96.81     74.47     89.69     12.37
             Open-source models
             CogVLM-17B                        0.00       0.00            0.00     0.00       0.00     0.00
             CogVLM2-LLaMA-3                   0.00       0.00            0.00     0.00       0.00     0.00
             Fuyu-8B                          79.00       0.00           35.00     0.00      13.86     0.00
             mPLUG-Owl-v2                     41.77       1.27           14.75     0.00      16.03     0.00
             InstructBLIP-Vicuna-13B           0.00       0.00            0.00     0.00       4.00     0.00
             InstructBLIP-Flan-T5-XXL         98.32       24.37         100.00     4.00      75.00     4.00
             IDEFICS2-8B                      23.08       0.96           84.40     0.00      14.00     0.00
             LLaVA-LLaMA-3                     0.00       0.00           13.00     1.50      25.50     0.50




                                                          19
Table 14: Individual Accuracy (%) in terms of the three metrics for the 5-needle M = 1 samples. We mark the best
results with bold face. The index accuracy is not always 100 % because the model can fail to output the correct
image index “1”.


             Stitching                              2×2              4×4                 8×8
             Metrics                          Index    Exact     Index      Exact     Index    Exact
             API-based models
             Claude 3 Opus                    80.20    46.40     84.16      14.20     80.87     1.74
             Gemini Pro 1.0                   58.60    15.60     28.80       5.40     10.80     0.20
             Gemini Pro 1.5                   98.20    76.55     98.40      27.80     95.40    25.00
             GPT-4V                           86.45    70.11     92.45      45.10     91.31     6.26
             GPT-4o                           88.34    71.72     94.83      50.43     92.18    14.81
             Open-source models
             CogVLM-17B                        0.00     0.00     0.00       0.00      2.55     0.00
             CogVLM2-LLaMA-3                   2.42     0.81     7.72       0.00      6.17     0.00
             Fuyu-8B                          80.00     0.00     26.00      0.00      10.00    0.00
             mPLUG-Owl-v2                     30.53     0.76     32.88      0.00      18.18    0.00
             InstructBLIP-Vicuna-13B           2.00     0.00     5.56       0.00      5.77     0.00
             InstructBLIP-Flan-T5-XXL         88.89     0.00     60.48      0.00      62.50    0.00
             IDEFICS2-8B                      26.42     4.88     51.85      1.85      82.00    0.00
             LLaVA-LLaMA-3                    30.00     8.00     30.00      1.60      54.60    1.40




Table 15: Individual Accuracy (%) in terms of the three metrics for the 2-needle M = 10 samples. We mark the
best results with bold face.


             Stitching                  1×1             2×2              4×4              8×8
             Metrics               Index    Exact   Index   Exact   Index     Exact    Index   Exact
             API-based models
             Claude 3 Opus         69.95    66.12    7.28    2.65    3.82      0.64     3.64    0.00
             Gemini Pro 1.0        17.68     7.32   10.06    5.33    2.19      0.00     4.96    0.83
             Gemini Pro 1.5        90.82    90.31   57.00   48.50   18.32      8.38     2.53    0.00
             GPT-4V                71.58    68.85   50.00   28.82   22.42      6.06    11.18    0.00
             GPT-4o                94.82    93.26   88.89   72.49   40.59     18.82    19.21    1.69
             Open-source models
             Fuyu-8B                4.00    0.00    11.00    0.00    4.81     0.00     2.00     0.00
             mPLUG-Owl-v2           1.68    0.84    1.64     0.00    7.69     0.00     4.55     0.00
             IDEFICS2-8B            3.00    0.00    4.95     0.00    0.00     0.00     3.00     0.00
             LLaVA-LLaMA-3          0.00    0.00    1.00     0.00    0.00     0.00     0.00     0.00




                                                      20
Table 16: Individual Accuracy (%) in terms of the three metrics for the 5-needle M = 10 samples. We mark the
best results with bold face.


            Stitching                 1×1             2×2             4×4             8×8
            Metrics               Index   Exact   Index   Exact   Index   Exact   Index   Exact
            API-based models
            Claude 3 Opus         72.18   71.97    9.16    2.65   10.30    0.21    6.11   0.00
            Gemini Pro 1.0        21.20   12.00   12.40    3.00   11.16    0.44    7.44   0.00
            Gemini Pro 1.5        94.75   78.79   58.40   35.20   20.59    7.86   10.61   0.41
            GPT-4V                70.83   68.33   43.86   25.23   19.10    4.94    9.98   0.42
            GPT-4o                95.13   91.81   86.47   56.14   42.71   19.89   15.09   0.26
            Open-source models
            Fuyu-8B               14.00    0.00    9.00   0.00    13.00   0.00    8.00    0.00
            mPLUG-Owl-v2          4.40     0.00    7.47   0.57    8.15    0.00    5.42    0.00
            IDEFICS2-8B           0.00     0.00    0.83   0.00    0.00    0.00    0.00    0.00
            LLaVA-LLaMA-3         0.00     0.00    0.00   0.00    0.00    0.00    0.00    0.00




                                                    21
