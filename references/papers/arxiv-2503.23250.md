                                              Encrypted Prompt: Securing LLM Applications
                                                      Against Unauthorized Actions


                                                                                   Shih-Han Chan
                                                                          University of California San Diego
                                                                                 s2chan@ucsd.edu




arXiv:2503.23250v1 [cs.CR] 29 Mar 2025
                                                                                       Abstract
                                                  Security threats like prompt injection attacks pose significant risks to applications
                                                  that integrate Large Language Models (LLMs), potentially leading to unauthorized
                                                  actions such as API misuse. Unlike previous approaches that aim to detect these
                                                  attacks on a best-effort basis, this paper introduces a novel method that appends an
                                                  Encrypted Prompt to each user prompt, embedding current permissions. These
                                                  permissions are verified before executing any actions (such as API calls) generated
                                                  by the LLM. If the permissions are insufficient, the LLM’s actions will not be
                                                  executed, ensuring safety. This approach guarantees that only actions within the
                                                  scope of the current permissions from the LLM can proceed. In scenarios where
                                                  adversarial prompts are introduced to mislead the LLM, this method ensures that
                                                  any unauthorized actions from LLM wouldn’t be executed by verifying permissions
                                                  in Encrypted Prompt. Thus, threats like prompt injection attacks that trigger LLM
                                                  to generate harmful actions can be effectively mitigated.


                                         1   Introduction
                                         Agents are advanced AI systems that combine LLMs with traditional software tools and APIs, often
                                         referred to as actions or tools. These systems typically start by using reasoning processes to decide
                                         which action to take, such as performing a web search Vu et al. [2023] and feeding the results back to
                                         LLM for the next step Gao et al. [2023], or accessing private data stored in cloud or local storage.
                                         While these agents are powerful and widely deployed in various products, their access to tools and
                                         APIs increases the potential risks of these systems, such as security vulnerabilities and API misuse.
                                         For instance, an attacker could use direct or indirect prompt injections Greshake et al. [2023] to
                                         control the actions of an agent, potentially leading to the leakage of intellectual property or private
                                         information Yu et al. [2023], or even unauthorized code execution. In addition, researchers have
                                         collected and analyzed common prompt injection commands designed to manipulate or mislead the
                                         behavior of LLMs Jain et al. [2023]. The findings indicate that most LLM-integrated applications are
                                         susceptible to these attacks, which could result in the generation of harmful content or the execution
                                         of malicious operations Liu et al. [2023]. These vulnerabilities underscore the need to protect against
                                         such threats and ensure that LLMs perform actions strictly within the limits of their authorized
                                         permissions.
                                         Currently, most defense strategies against prompt injection attacks focus on learning a model that
                                         better aligns with human values Shen et al. [2023] or ignoring the malicious requests Piet et al. [2023].
                                         For instance, Wallace et al. Wallace et al. [2024] proposed a method called Instruction Hierarchy,
                                         which involves fine-tuning the models with malicious instructions to learn how to refuse them.
                                         However, these methods have several limitations. First, the models suffer from over-refusal, where
                                         they may incorrectly reject valid inputs. Moreover, they remain vulnerable to more advanced gradient-
                                         based transfer attacks Wallace et al. [2019], Zhu et al. [2023]. Even worse, stronger adversarial
                                         prompts and novel attack methods may emerge in the future, potentially rendering existing defense

                                         Preprint. Under review.
         (a) Delete_Email API is blocked                       (b) Find_Photo API is executed
Figure 1: A simplified example illustrates how Encrypted Prompt work. The user submits a prompt
from their device, which is appended with an encrypted prompt and sent to the server. The LLM
generates API calls and responses based on the user’s prompt. Before executing these API calls,
the server checks the permissions specified in the encrypted prompt. If an API call exceeds the
permissions, the server may reject the request or ask the user for additional verification. For example,
(a) Delete_Email API (generated from adversarial prompt) exceeds the current permission level and
is rejected, (b) whereas a Find_Photo API call is within the permitted scope and is executed.


mechanisms outdated and ineffective in protecting applications. Lastly, there is the subjective nature
of determining the correct behavior of LLMs. For instance, users might intentionally or accidentally
request the deletion of stored data. However, actions such as calling APIs or executing commands
should never be performed if they exceed current permissions.
To address this issue, we developed an Encrypted Prompt and a framework designed to ensure that
LLMs strictly adhere to predefined permissions. This flexible framework allows developers and users
to define permissions based on their specific architecture and application needs. Permissions can
also be dynamically adjusted based on different user inputs, adapting to the current user, device, and
server status. The Encrypted Prompt consists of three components:
1. Delimiter (<D> and </D>): These special tokens are used to distinguish the enclosed input as
an Encrypted Prompt, differentiating it from user prompts. Like the reserved tokens in LLAMA-3
Llama Team [2024], they mark specific input types to ensure proper interpretation by the LLM.
2. Permission (<P>): Specifies the current permissions that determine which actions can be taken.
Every user input can have unique (different) permissions.
3. Public Key (<PK>): Utilizes for verification, ensuring that the permissions and public key remain
unchanged after being appended to the user input.
                     <E NCRYPTED P ROMPT > = <D> + <P> + <PK> +</D>
As illustrated in Fig. 1, the user input includes a user prompt and an encrypted prompt. Based
on the current user’s status (e.g. whether user enters password/fingerprint within 5 mins, login
account, current place, other device’s status), as determined by the developer, permissions and a
corresponding public key are assigned for encrypted prompt. For public/private key verification A to
prevent permission from being modified, RSA Rivest et al. [1978] or other methods can be used as
the public/private key pair. The encrypted prompt is then appended to the user prompt, and the user
input is sent from the user’s device to the server.
                 <U SER I NPUT > = <U SER P ROMPT > + <E NCRYPTED P ROMPT >

After the server receives the user input, it automatically identifies the delimiter in the encrypted
prompt before processing user prompts with the LLM. The server then retrieves the corresponding
private key based on the permissions in the encrypted prompt and checks whether the public and
private keys match. The LLM generates output and actions (API calls) accordingly. If the actions
are within the permitted scope, the server allows the actions or API calls to execute. However, if
the actions exceed the permitted scope, the server can either refuse the action or request further
verification from the user. The developer can define the exact behavior in these cases. Additionally,
if there is a mismatch between the public key and private key for the permissions, it could indicate
an issue during transmission (such as tampering by an attacker) or the permissions changed after
appending encrypted prompt to user prompt. In such cases, the server must handle the LLM’s output


                                                   2
or actions accordingly such as asking user for further verification. More detailed settings are discussed
in Section 3 and Appendix B.
Compared to traditional permission-based access control systems (defining few permissions in the
Operating System level) Baskiyar and Meghanathan [2005], Satyanarayanan [2010], Encrypted
prompt could be implemented in the software (application) level, allowing easier implementation
(no need to change kernel code) and different applications could also define different permission
rules. Moreover, the permission can be changed among various instructions and from time to time,
allowing more flexibility. Although the Operating System can also achieve this by synchronizing
the permissions of this user device, it requires more network overhead and hardware resources.
Appending an Encrypted prompt to each user prompt is much simpler and more flexible. The only
drawback of Encrypted prompt is the permission needs to be determined on the user’s device.
Our contributions can be summarized as follows:

       • We introduce the Encrypted Prompt and a framework designed to prevent systems from
         executing actions generated by LLMs that exceed the current permissions.

       • The framework allows developers and users to define permissions and rules for all LLM
         actions based on the current status of the user, their device, and the server. Permissions can
         be adjusted dynamically based on different user inputs and over time, providing flexibility.

       • The Encrypted Prompt can be easily implemented across various platforms and applications
         without requiring additional model training or causing over-refusal issues, as permissions
         are pre-set. It can also integrate with other defense methods, such as instruction hierarchy
         Wallace et al. [2019], red teaming Shi et al. [2024], and model alignment Shen et al. [2023].



2   Related Work

LLM Safety. LLMs are widely deployed across various applications and products. However, since
LLMs are typically trained on large text corpora sourced from the internet, they may inadvertently
incorporate offensive content that misaligns with human values. This can lead to the generation
of polarized content or harmful speech, including biases and stereotypes Bommasani et al. [2021],
Nadeem et al. [2020], Patel and Pavlick [2021], Weidinger et al. [2021]. To mitigate these risks,
LLM researchers and developers employ various fine-tuning techniques, often referred to as model
alignment, to ensure LLMs do not produce inappropriate responses to user queries Glaese et al.
[2022], Korbak et al. [2023]. These efforts have, at least on the surface, been successful in preventing
public chatbots from generating overtly inappropriate content in response to typical user interactions.
Prompt Injection Attacks. Similar to adversarial attacks on machine learning models in the computer
vision domain Papernot et al. [2016], Dong et al. [2020], LLMs also suffer from prompt injection
attacks (PIA). These attacks use carefully engineered prompts to cause aligned LLMs to generate
content or actions that violate safety guidelines Wei et al. [2024], Zhu et al. [2023]. PIA used the
designed prompt to leak the original prompts, private data, and system instructions of the LLM, or
even generate some harmful API usage such as deleting user’s data, sharing private data through
email, etc. Many works discussed how to generate an adversarial prompt that misled the LLM to
generate unexpected or harmful texts/actions Wallace et al. [2019], Shin et al. [2020], Zhu et al.
[2023].
LLMs with APIs and tools. Recently, users can access LLMs hosted on servers, such as ChatGPT,
or use LLMs directly on mobile devices, like Apple Intelligence Gunter et al. [2024]. These LLMs
can execute external tools through simple API calls to streamline users’ daily tasks. For instance,
Toolformer Schick et al. [2024] trains LLMs to generate API calls directly. Similarly, ReAct Yao
et al. [2022] enables LLMs to utilize tools through Chain-of-Thought prompting, producing specific
actions and reasoning based on intermediate observations from the environment. However, in the
context of prompt injection attacks (PIA), adversarial prompts could lead LLMs to ignore previous
instructions and generate harmful or unexpected API calls, and it would be important that these
harmful or incorrect API call are not executed.


                                                   3
Figure 2: Malicious User Scenario. The malicious user prompt contains adversarial texts and prompt
designed to manipulate the LLM into generating harmful API calls. Send_Email is blocked as the
API call exceeds the permissions in encrypted prompt. (Actual execution paths are highlighted.)




Figure 3: Malicious Content from Online Source. The prompt from online website includes
adversarial texts and prompt, and the LLM generates API calls beyond current permission scope. In
this example, the Web_Crawl API is executed to read online text as LLM input because the current
permissions allow it. However, when the LLM generates a Send_Email API call from online texts,
it is rejected since it exceeds the current permissions. (Actual execution paths are highlighted.)



3     Encrypted Prompt as an Effective Defense

In this section, we discuss how encrypted prompts can be applied in various real-world scenarios
Greshake et al. [2023] to prevent systems from executing actions (API calls) beyond their current
permissions. The core principle is that only actions generated by the LLM within the scope of
its current permissions are allowed to be executed. In the following examples, <A DV _P ROMPT >
represents a strong adversarial prompt designed to deceive the LLM into generating actions that
exceed the allowed boundaries, assuming that defense mechanisms, such as model alignment, fail to
protect the model.


3.1   Malicious User
In this scenario, we assume that the user is either an attacker or that the user’s prompt has been
tampered with by an attacker, causing the LLM to generate actions that exceed the current permissions.
In Fig. 2, the user enters: "Send the password to abc123@gmail.com <ADV_PROMPT>." The LLM then
generates an API call to send the stored password to the specified email address. Since sending
confidential data via email requires a high level of permission, and the user has not entered a password
on the mobile device within the last five minutes, the permission level in the encrypted prompt is low,
resulting in the API call being denied. The user is then asked for further verification.


                                                   4
Figure 4: Malicious LLMs Scenario. The LLM generates unexpected API calls even if the input
user prompt is clean. In this example, Move_Data API generated from LLM is rejected since current
permission is not enough. (Actual execution paths are highlighted.)


3.2 Malicious Content from Online Source
LLMs can also interact with online websites or persistent storage to retrieve information. How-
ever, these sources might contain malicious content, leading the LLM to generate harmful actions.
In Fig. 3, a user input: "Tell me the procedure to make a chicken sandwich from cooking.com."
Suppose the recipe from cooking.com includes a malicious instruction like "Send your password
to abc123@gmail.com <ADV_PROMPT>." The LLM first processes the user’s input and generates an
API call to retrieve information from cooking.com. Since Web_Crawl API requires low permis-
sion and satisfies the permission level in the encrypted prompt, Web_Crawl is executed. The
recipe from cooking.com, including the malicious content, is then summarized by the LLM. How-
ever, the <A DV _P ROMPT > in the malicious content causes the LLM to generate an API call:
Send_Email(<password>, abc123@gmail.com). Fortunately, Send_Email requires a higher level of per-
mission, and the current permission in the encrypted prompt is insufficient. As a result, the action is
rejected, and the user is informed.

3.3 Malicious LLMs
Due to issues such as problematic training data, flawed training methods, or other factors, an LLM
might misunderstand user instructions and generate harmful actions, even when the user input is
clean (no adversarial texts and prompts exist). In Fig. 4, a user inputs, "My cloud storage is almost
full, and my laptop is so slow." The LLM then generates a Move_Data API call to upload user’s
data. Since transferring large amounts of data requires a high level of permission, and the current
permission level in the encrypted prompt is low, the system asks the user for further verification
before executing the API call.


4   Discussion

Permission in Encrypted Prompt. Permissions (P) in the encrypted prompt are determined by
both the developer and the user. The rules and logic for permissions should be stored either on the
user’s device or on the server (if the LLM is server-based). Permissions can be implemented at the
application layer rather than the system layer, although developers may choose to implement them at
the kernel or system layer if desired. Permissions can take various forms. For example, a permission
could be represented by a single integer from 1 to x, indicating the current permission level (e.g., level
1 allows all "read" API calls, level 2 allows all "write/modify" API calls, etc.). Permissions could also
be represented as a set of boolean values (e.g., TFFTTFFF...), indicating whether each API is currently
allowed. Additionally, an advanced graph structure could define permissions, specifying which APIs
can be used sequentially. Ultimately, developers can customize their own permission rules based on
the application’s need, device status, and other factors. This flexibility allows permissions to adapt
dynamically, changing over time or based on specific user inputs.
Public key in Encrypted Prompt. The public key in the encrypted prompt is compared with the
private key on the server to ensure that permissions have not been altered by an attacker during
transmission or on the server. Any public/private key cryptographic algorithms, such as RSA Rivest


                                                    5
et al. [1978], DSA Nist [1992], ECDSA Johnson et al. [2001], DH Diffie and Hellman [1976], or
ECDH Koblitz [1987], can be used for this verification.
Limitation. Although the encrypted prompt can ensure that the system only takes actions within
current permissions, it cannot safeguard against "authorized" actions resulting from various attacks.
For instance, if the LLM accesses private data due to a strong prompt injection attack, and these
actions are within the allowed permissions, the corresponding API calls will still be executed.
Social impact statement. The integration of LLMs into applications introduces security challenges
like prompt injection and jailbreak attacks, which may cause LLMs to ignore instructions or execute
unauthorized API calls. These risks intensify when LLMs are chained, allowing attacks at one stage
to affect others. In this work, Encrypted Prompt introduces a permission-based mechanism to
prevent unauthorized actions by LLMs. Future research can explore refining permission rules to
ensure LLMs operate securely within ethical boundaries.

5   Conclusion
As adversarial attacks on LLMs, like prompt injection attacks, become more advanced, encrypted
prompts offer a way to ensure only authorized actions are executed. Regardless of emerging threats,
Encrypted Prompt safeguards against actions beyond the allowed permissions. We envision their
integration with other defense mechanisms across various applications. Future research should
explore how to design permissions for different scenarios and how systems can respond based on
permission levels.

References
Tu Vu, Mohit Iyyer, Xuezhi Wang, Noah Constant, Jerry Wei, Jason Wei, Chris Tar, Yun-Hsuan Sung,
  Denny Zhou, Quoc Le, et al. Freshllms: Refreshing large language models with search engine
  augmentation. arXiv preprint arXiv:2310.03214, 2023.
Luyu Gao, Aman Madaan, Shuyan Zhou, Uri Alon, Pengfei Liu, Yiming Yang, Jamie Callan, and
  Graham Neubig. PAL: Program-aided language models. In Andreas Krause, Emma Brunskill,
  Kyunghyun Cho, Barbara Engelhardt, Sivan Sabato, and Jonathan Scarlett, editors, Proceedings of
  the 40th International Conference on Machine Learning, volume 202 of Proceedings of Machine
  Learning Research, pages 10764–10799. PMLR, 23–29 Jul 2023. URL https://proceedings.
  mlr.press/v202/gao23f.html.
Kai Greshake, Sahar Abdelnabi, Shailesh Mishra, Christoph Endres, Thorsten Holz, and Mario Fritz.
  Not what you’ve signed up for: Compromising real-world llm-integrated applications with indirect
  prompt injection. In Proceedings of the 16th ACM Workshop on Artificial Intelligence and Security,
  pages 79–90, 2023.
Jiahao Yu, Yuhang Wu, Dong Shu, Mingyu Jin, and Xinyu Xing. Assessing prompt injection risks in
   200+ custom gpts. arXiv preprint arXiv:2311.11538, 2023.
Neel Jain, Avi Schwarzschild, Yuxin Wen, Gowthami Somepalli, John Kirchenbauer, Ping yeh
  Chiang, Micah Goldblum, Aniruddha Saha, Jonas Geiping, and Tom Goldstein. Baseline defenses
  for adversarial attacks against aligned language models, 2023. URL https://arxiv.org/abs/
  2309.00614.
Yi Liu, Gelei Deng, Yuekang Li, Kailong Wang, Zihao Wang, Xiaofeng Wang, Tianwei Zhang,
  Yepang Liu, Haoyu Wang, Yan Zheng, et al. Prompt injection attack against llm-integrated
  applications. arXiv preprint arXiv:2306.05499, 2023.
Tianhao Shen, Renren Jin, Yufei Huang, Chuang Liu, Weilong Dong, Zishan Guo, Xinwei Wu, Yan
  Liu, and Deyi Xiong. Large language model alignment: A survey. arXiv preprint arXiv:2309.15025,
  2023.
Julien Piet, Maha Alrashed, Chawin Sitawarin, Sizhe Chen, Zeming Wei, Elizabeth Sun, Basel
  Alomair, and David Wagner. Jatmo: Prompt injection defense by task-specific finetuning. ArXiv,
  abs/2312.17673, 2023. URL https://api.semanticscholar.org/CorpusID:266690784.


                                                 6
Eric Wallace, Kai Xiao, Reimar Leike, Lilian Weng, Johannes Heidecke, and Alex Beutel. The instruc-
  tion hierarchy: Training llms to prioritize privileged instructions. arXiv preprint arXiv:2404.13208,
  2024.

Eric Wallace, Shi Feng, Nikhil Kandpal, Matt Gardner, and Sameer Singh. Universal adversarial
  triggers for attacking and analyzing nlp. arXiv preprint arXiv:1908.07125, 2019.

Sicheng Zhu, Ruiyi Zhang, Bang An, Gang Wu, Joe Barrow, Zichao Wang, Furong Huang, Ani
  Nenkova, and Tong Sun. Autodan: Automatic and interpretable adversarial attacks on large
  language models. arXiv preprint arXiv:2310.15140, 2023.

AI @ Meta Llama Team. The llama 3 herd of models, 2024. URL https://arxiv.org/abs/
  2407.21783.

Ronald L. Rivest, Adi Shamir, and Leonard Adleman. A method for obtaining digital signatures and
  public-key cryptosystems. Communications of the ACM, 21(2):120–126, 1978.

Sundararajan Baskiyar and Natarajan Meghanathan. A survey of contemporary real-time operating
  systems. Informatica, 29(3):233–240, 2005.

Mahadev Satyanarayanan. Mobile computing: The next decade. In Proceedings of the 1st ACM
 Workshop on Mobile Cloud Computing and Services: Social Networks and Beyond, pages 1–6.
 ACM, 2010. doi: 10.1145/1810931.1810935.

Zhouxing Shi, Yihan Wang, Fan Yin, Xiangning Chen, Kai-Wei Chang, and Cho-Jui Hsieh. Red
  teaming language model detectors with language models. Transactions of the Association for
  Computational Linguistics, 12:174–189, 2024. doi: 10.1162/tacl_a_00639. URL https://
  aclanthology.org/2024.tacl-1.10.

Rishi Bommasani, Drew A Hudson, Ehsan Adeli, Russ Altman, Simran Arora, Sydney von Arx,
  Michael S Bernstein, Jeannette Bohg, Antoine Bosselut, Emma Brunskill, et al. On the opportuni-
  ties and risks of foundation models. arXiv preprint arXiv:2108.07258, 2021.

Moin Nadeem, Anna Bethke, and Siva Reddy. Stereoset: Measuring stereotypical bias in pretrained
 language models. arXiv preprint arXiv:2004.09456, 2020.

Roma Patel and Ellie Pavlick. “was it “stated” or was it “claimed”?: How linguistic bias affects
  generative language models. In Marie-Francine Moens, Xuanjing Huang, Lucia Specia, and Scott
  Wen-tau Yih, editors, Proceedings of the 2021 Conference on Empirical Methods in Natural Lan-
  guage Processing, pages 10080–10095, Online and Punta Cana, Dominican Republic, November
  2021. Association for Computational Linguistics. doi: 10.18653/v1/2021.emnlp-main.790. URL
  https://aclanthology.org/2021.emnlp-main.790.

Laura Weidinger, John Mellor, Maribeth Rauh, Conor Griffin, Jonathan Uesato, Po-Sen Huang, Myra
  Cheng, Mia Glaese, Borja Balle, Atoosa Kasirzadeh, et al. Ethical and social risks of harm from
  language models. arXiv preprint arXiv:2112.04359, 2021.

Amelia Glaese, Nat McAleese, Maja Tr˛ebacz, John Aslanides, Vlad Firoiu, Timo Ewalds, Maribeth
 Rauh, Laura Weidinger, Martin Chadwick, Phoebe Thacker, et al. Improving alignment of dialogue
 agents via targeted human judgements. arXiv preprint arXiv:2209.14375, 2022.

Tomasz Korbak, Kejian Shi, Angelica Chen, Rasika Vinayak Bhalerao, Christopher Buckley, Jason
  Phang, Samuel R Bowman, and Ethan Perez. Pretraining language models with human preferences.
  In International Conference on Machine Learning, pages 17506–17533. PMLR, 2023.

Nicolas Papernot, Patrick McDaniel, Somesh Jha, Matt Fredrikson, Z Berkay Celik, and Ananthram
  Swami. The limitations of deep learning in adversarial settings. In 2016 IEEE European symposium
  on security and privacy (EuroS&P), pages 372–387. IEEE, 2016.

Yinpeng Dong, Qi-An Fu, Xiao Yang, Tianyu Pang, Hang Su, Zihao Xiao, and Jun Zhu. Benchmark-
  ing adversarial robustness on image classification. In proceedings of the IEEE/CVF conference on
  computer vision and pattern recognition, pages 321–331, 2020.


                                                  7
Alexander Wei, Nika Haghtalab, and Jacob Steinhardt. Jailbroken: How does llm safety training fail?
  Advances in Neural Information Processing Systems, 36, 2024.
Taylor Shin, Yasaman Razeghi, Robert L Logan IV, Eric Wallace, and Sameer Singh. Autoprompt:
  Eliciting knowledge from language models with automatically generated prompts. arXiv preprint
  arXiv:2010.15980, 2020.
Tom Gunter, Zirui Wang, Chong Wang, Ruoming Pang, Andy Narayanan, Aonan Zhang, Bowen
  Zhang, Chen Chen, Chung-Cheng Chiu, David Qiu, et al. Apple intelligence foundation language
  models. arXiv preprint arXiv:2407.21075, 2024.
Timo Schick, Jane Dwivedi-Yu, Roberto Dessì, Roberta Raileanu, Maria Lomeli, Eric Hambro, Luke
  Zettlemoyer, Nicola Cancedda, and Thomas Scialom. Toolformer: Language models can teach
  themselves to use tools. Advances in Neural Information Processing Systems, 36, 2024.
Shunyu Yao, Jeffrey Zhao, Dian Yu, Nan Du, Izhak Shafran, Karthik Narasimhan, and Yuan Cao.
  React: Synergizing reasoning and acting in language models. arXiv preprint arXiv:2210.03629,
  2022.
Corporate Nist. The digital signature standard. Communications of the ACM, 35(7):36–40, 1992.
Don Johnson, Alfred Menezes, and Scott Vanstone. The elliptic curve digital signature algorithm
 (ecdsa). Int. J. Inf. Secur., 1(1):36–63, aug 2001. ISSN 1615-5262. doi: 10.1007/s102070100002.
  URL https://doi.org/10.1007/s102070100002.
Whitfield Diffie and Martin E Hellman. New directions in cryptography. IEEE transactions on
 Information Theory, 22(6):644–654, 1976.
Neal Koblitz. Elliptic curve cryptosystems. In Mathematics of computation, pages 203–209. JSTOR,
 1987.
Wei Zhang and John Liu. Asymmetric encryption for securing ai interactions: A case study in ai
 model communication. Journal of Secure AI Systems, 12(4):234–250, 2021.
Thao Nguyen and Minghao Sun. Cryptographic frameworks for securing machine learning model
  and api interactions. In Proceedings of the International Conference on Machine Learning Security
  (ICMLS), pages 102–114. ML Security Press, 2020.




                                                8
A    Encryption (Public/Private Key)
Encryption mechanisms, especially those based on public and private key cryptography, have long
been fundamental to securing communication and maintaining data integrity. Public Key Infrastruc-
ture (PKI) enables secure communication between parties by using a pair of cryptographic keys: a
public key, which is shared openly, and a private key, which is kept secret. This method ensures
that even if the public key is compromised, the private key remains secure. For utilizing encryption
with AI models, Zhang et al. Zhang and Liu [2021] explored the use of asymmetric encryption to
secure these communications, while Nguyen et al.Nguyen and Sun [2020] proposed cryptographic
frameworks to safeguard information flow between machine learning models and APIs. These
works provide foundational insights into applying cryptography to enhance security and alignment in
LLM-based systems.

B    LLM on user’s device
The LLM could deploy on the user’s device instead of the server. In this case, the Encrypted Prompt
would consist only of a Delimiter <D> and </D> and a Permission (P) without the Public Key (PK).
This is because the public/private key pair is intended to protect permissions from being modified
during transmission or on the server.




                                                 9
