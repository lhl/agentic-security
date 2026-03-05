<!-- extracted-by: marker -->
# ISOLATEGPT: An Execution Isolation Architecture for LLM-Based Agentic Systems

Artifact
Evaluated
NDSS

Available
Functional
Reproduced

Yuhao Wu\*, Franziska Roesner<sup>†</sup>, Tadayoshi Kohno<sup>†</sup>, Ning Zhang\*, Umar Iqbal\*
\*Washington University in St. Louis, <sup>†</sup>University of Washington
{yuhao.wu, zhang.ning, umar.iqbal}@wustl.edu, {franzi, yoshi}@cs.washington.edu

Abstract—Large language models (LLMs) extended as systems, such as ChatGPT, have begun supporting third-party applications. These LLM apps leverage the de facto natural languagebased automated execution paradigm of LLMs: that is, apps and their interactions are defined in natural language, provided access to user data, and allowed to freely interact with each other and the system. These LLM app ecosystems resemble the settings of earlier computing platforms, where there was insufficient isolation between apps and the system. Because third-party apps may not be trustworthy, and exacerbated by the imprecision of natural language interfaces, the current designs pose security and privacy risks for users. In this paper, we evaluate whether these issues can be addressed through execution isolation and what that isolation might look like in the context of LLMbased systems, where there are arbitrary natural language-based interactions between system components, between LLM and apps, and between apps. To that end, we propose ISOLATEGPT, a design architecture that demonstrates the feasibility of execution isolation and provides a blueprint for implementing isolation, in LLM-based systems. We evaluate ISOLATEGPT against a number of attacks and demonstrate that it protects against many security, privacy, and safety issues that exist in non-isolated LLMbased systems, without any loss of functionality. The performance overhead incurred by ISOLATEGPT to improve security is under 30% for three-quarters of tested queries.

#### I. INTRODUCTION

Large Language Models (LLMs) are being increasingly extended into standalone computing systems (often referred to as *agentic systems*) [1], [2], [3], [4], [5]. Some of these LLM-based systems, such as ChatGPT [1] and Gemini [2], have started to support *third-party applications*. LLM apps and their interactions are defined using natural language, given access to user data, and allowed to interact with other apps, the system, and online services [6], [7]. For example, a flight booking app (by directing the LLM) might leverage the user's personal data shared elsewhere in the conversation with the system, and contact external services to complete the booking.

While this natural language-based automated execution paradigm increases the utility of apps and capabilities of LLM-based systems, it also introduces several security and privacy risks. Specifically, natural language-based apps and

interactions are not as precisely defined as traditional programming interfaces, which makes them much more challenging to scrutinize. Additionally, the unrestricted exposure to apps: of user data, access to other apps, and system capabilities, for automation purposes, introduces serious risks, as apps come from third-party developers, who may not be trustworthy. For example, if the flight booking app is not trustworthy, it might exfiltrate user's personal data or surreptitiously book the most expensive tickets. Considering the inherent risks posed by this new execution paradigm, it is crucial that LLM-based systems make security and privacy a key consideration of their design.

In this paper, we address this problem by proposing an LLM-based system architecture that aims to secure the execution of apps. Building on the lessons learned from prior computing systems [8], [9], [10], [11], [12], our key idea is to isolate the execution of apps and to allow interaction between apps and the system only through well-defined interfaces with user permission. This approach reduces the attack surface of LLM-based systems by design, as apps execute in their constrained environment and their interaction outside that environment are mediated. Although execution isolation has existed in prior computing systems, applying these ideas to LLM-based systems is not immediately straightforward. Specifically, the isolated environments need to be securely provided access to the broader system context, and secure interfaces need to be defined for natural language-based interactions.

We operationalize our idea by implementing ISOLATEGPT, an LLM-based system that secures the execution of apps via isolation. To be able to provide the same functionality as a nonisolated LLM-based system, while being secure, ISOLATEGPT needs to overcome three challenges. First, ISOLATEGPT needs to be able to seamlessly allow users to interact with apps executing in isolated environments. ISOLATEGPT addresses this challenge by developing a central trustworthy interface named hub, which is aware of the existence of isolated apps, and that can reliably receive user queries and route them to the appropriate apps. Second, ISOLATEGPT needs to be able to use apps in isolated environments to resolve user queries without any loss of functionality. ISOLATEGPT addresses this challenge by accompanying apps with dedicated LLMs (i.e., each app has its own LLM instance) and by providing them with prior context in isolated environments, in a standalone module named spoke, so that they can accurately address user queries. Third, ISOLATEGPT needs to be able to allow mutually distrusting apps to safely collaborate. ISOLATEGPT addresses this challenge by proposing an *inter-spoke communication protocol*, which routes well-defined requests between agnostic spokes via hub. These modules form the core of ISOLATEGPT's design, which we refer to as a *hub-and-spoke architecture*.

We evaluate security and safety benefits, functionality, and performance of ISOLATEGPT by comparing it with a baseline non-isolated system that we develop, VANILLAGPT. To evaluate ISOLATEGPT's security and safety, we implement several case studies and use attacks from a benchmark [\[13\]](#page-15-0) that assume an adversary trying to alter the behavior of another app, steal data from other apps, and the system. We also consider case studies in which the imprecision of natural language leads to inadvertent exposure of user data and altering of system behavior. We find that ISOLATEGPT, due to its execution isolation architecture, is able to protect against both the attacks from an adversary and safety issues caused by the imprecision of language.

To evaluate ISOLATEGPT's functionality and performance, we rely on LangChain's[\[14\]](#page-15-1) benchmarks [\[15\]](#page-15-2), that simulate a variety of user requests. Specifically, the benchmarks include requests that: do not require using apps, require use of a single app, require use of multiple apps, and require collaboration between multiple apps. We find that for all benchmarks, ISOLATEGPT provides the same functionality as the baseline VANILLAGPT, while providing the key advantage of additional security. As for performance, ISOLATEGPT mainly incurs overheads because it takes additional steps to resolve user queries, as compared to a non-isolated system. We find that for three-quarters (75.73%) of the tested queries ISOLATEGPT's overhead is under 30% as compared to VANILLAGPT.

Contributions. Our key contributions are as follows:

- 1) We demonstrate the feasibility of execution isolation in the natural language-based automated execution paradigm of LLM-based systems in mitigating security and privacy issues that arise with the execution of third-party apps. We also provide a blueprint of an architecture for implementing execution isolation in AI/LLM-based systems.
- 2) We operationalize our proposed architecture by developing ISOLATEGPT. We demonstrate that ISOLATEGPT protects against many security, privacy, and safety issues without loss of functionality. ISOLATEGPT's performance overhead to improve security is under 30% for 75.73% of tested queries.
- 3) To foster follow-up research, we release ISOLATEGPT's source code[1](#page-1-0) . In addition to implementing ISOLATEGPT using LangChain [\[14\]](#page-15-1), we collaborated with LlamaIndex [\[16\]](#page-15-3) to integrate ISOLATEGPT as a *Llama Pack*[2](#page-1-1) .

Looking ahead, we see ISOLATEGPT as an effort that helps the research community understand the viability, strengths, and limitations of execution isolation in securing LLM-based systems. We envision ISOLATEGPT providing a foundation for deeper explorations that build on execution isolation, e.g., <span id="page-1-4"></span>**[Query]** Send an email to John Doe with an attachment of "annual\_report.pdf" from Cloud Drive.

![](_page_1_Figure_11.jpeg)

Fig. 1: Query resolution with apps in LLM-based systems: LLM apps (i.e., functionality descriptions & APIs) are loaded in system memory. For each query, the LLM leverages available apps and memory, to generate a step-by-step plan to resolve the query. Based on its plan, the LLM can directly call and exchange information between APIs of needed apps.

enforcing access control through a permission model, or where execution isolation can be complementary in securing LLMbased systems.

## II. MOTIVATION

## *A. LLM-based systems*

LLMs are being increasingly extended as systems with abilities, such as to connect to online services, to keep a persistent memory, and to execute programs [\[6\]](#page-14-5), [\[7\]](#page-14-6). These capabilities tremendously extend the utility of LLMs, making them useful for a variety of tasks. In fact, some researchers are even envisioning such LLM-based systems to offer similar utility as operating systems [\[17\]](#page-15-4). LLM vendors are cognizant of this potential and are already deploying standalone LLM-based systems, such as ChatGPT [\[1\]](#page-14-0), and LLM-based computing devices, such as the Alexa LLM-based smart speaker [\[3\]](#page-14-2). LLM vendors have recently also started supporting third-party apps [\[18\]](#page-15-5), [\[19\]](#page-15-6), [\[3\]](#page-14-2), which is further increasing the capabilities of LLMs and consequently the utility of LLM-based systems.

*1) LLM apps architecture:* The exact LLM application architecture varies across systems and even within systems (for systems that support several kinds of apps) but the core components of applications are common across LLMs and LLMbased systems.[3](#page-1-2) At their core, third-party applications (*LLM apps*[4](#page-1-3) ) consist of a natural language functionality description as a set of instructions for the LLM and in most cases, API

<span id="page-1-0"></span><sup>1</sup>Source code: https://github.[com/llm-platform-security/SecGPT](https://github.com/llm-platform-security/SecGPT)

<span id="page-1-1"></span><sup>2</sup>Llama Pack: https://llamahub.[ai/l/llama-packs/llama-index-packs-secgpt](https://llamahub.ai/l/llama-packs/llama-index-packs-secgpt)

<span id="page-1-2"></span><sup>3</sup>Some LLM-based systems (e.g., ChatGPT [\[1\]](#page-14-0), Gemini [\[20\]](#page-15-7)) support a native app ecosystem, whereas others (e.g., LLaMA [\[21\]](#page-15-8)) can be extended to support apps by using open-source frameworks (e.g., LangChain [\[14\]](#page-15-1)).

<span id="page-1-3"></span><sup>4</sup>Different vendors refer to LLM applications by different names. For example, OpenAI refers to LLM applications as plugins [\[22\]](#page-15-9), actions [\[23\]](#page-15-10), and GPTs [\[18\]](#page-15-5) and Google refers to LLM applications as extensions [\[19\]](#page-15-6). In this paper, we refer to them as *apps*.

endpoints to send and receive data and instructions [\[22\]](#page-15-9), [\[18\]](#page-15-5). To use apps to respond to user queries, LLM-based systems load the apps' functionality descriptions and API endpoints in their *memory* (i.e., context window), so that the LLM can build the necessary context (e.g., exchanging information between APIs of different apps) to resolve user requests using the apps [\[22\]](#page-15-9), [\[18\]](#page-15-5). Additionally, the messages exchanged between the user and apps and between the user and the LLM (e.g., prior conversation history) are also kept in the memory to provide contextually-relevant responses to follow-up user requests [\[24\]](#page-15-11). To demonstrate the interplay between different apps and system components, we present the execution flow of a query via two LLM apps in Figure [1.](#page-1-4)

This execution model allows LLM-based systems to seamlessly tackle several practical use cases that require explicit user effort in conventional computing systems or did not exist before. Below we present a few example case studies that demonstrate the usefulness of LLM-based systems. We return to these scenarios in Section [II-B](#page-2-0) and [III-D](#page-4-0) to motivate our work and security goals and later in Section [V](#page-8-0) to evaluate the protection provided by our system.

<span id="page-2-4"></span>*Case study A. Data access: Booking a flight.* The user wants to book a flight using an online travel reservation service. To book a flight in a traditional system, the user consults a travel reservation service, chooses a flight that suits them, and then provides their personal information and payment details to book a flight. In an LLM-based system, the user can automate this task by installing a travel reservation app. Based on the presence of functionality description and API endpoints of the app in the memory, the LLM-based system will develop the context to call the relevant APIs, with appropriate data, to search and book a flight. The LLM might not need to request the user to get all of the data needed to make a reservation, instead, the LLM can leverage its memory (including data extracted from prior user conversation), to automatically provide the information needed to book a flight (e.g., user's name, date of birth, passport information, business or economy class preference, and credit card details).

<span id="page-2-1"></span>*Case study B. App collaboration: Email file attachment.* The user wants to attach a file from their cloud drive in response to an email. To complete that task traditionally, the user needs to open the cloud drive, manually search for the file, and attach it to the email. In an LLM-based system, the user can automate several processes of this task by installing the email and cloud drive apps. Based on the presence of functionality descriptions and API endpoints of both apps in memory, the LLM-based system will develop the context to call and exchange the information between the APIs of both of these apps. Essentially, if the user query requires the LLM-based system to attach a document in response to an email, the LLM-based system will know which APIs to call to retrieve the file from the cloud drive app and which APIs to call to attach that file in the email app.

<span id="page-2-2"></span>*Case study C. Information synthesis: Booking a ride with the lowest fare.* The user wants to book a ride from a ride sharing service which offers the lowest fare. To achieve that task traditionally, the user consults a few ride sharing services, provides their location and destination to these services, compares the fares, and then chooses the one with the lowest fare. In an LLM-based system, the user can install a few ride sharing apps and automate this process. Specifically, the LLM-based system can call the APIs of the ride sharing apps, provide them the relevant information (some of which the LLM-based system may already possess, e.g., user's location), load their responses in memory, compare the responses, and pick the app that offers the lowest fare to make a booking for the user.

<span id="page-2-3"></span>*Case study D. Altering system behavior: Fiction writing.* The user needs help writing a fiction novel (e.g., idea generation, story feedback). To achieve that task without an LLM, the user might contact their colleagues, friends, or family, to discuss their ideas and reach a conclusion. In LLM-based systems, the user can install a fiction writing assistant app. The app can alter the system behavior by instructing to assist the user with fiction writing (e.g., be imaginative while responding to user queries). The LLMbased system with such an app can interpret user queries with a perspective of a fiction writing assistant.

## <span id="page-2-0"></span>*B. Security and privacy risks*

While the execution of apps in a shared memory space helps LLM-based systems seamlessly address complicated user requests, it introduces serious security and privacy risks. At the highest level, apps can access data and influence the execution/behavior of other apps and the LLM [\[25\]](#page-15-12), [\[26\]](#page-15-13), [\[27\]](#page-15-14). These risks exist in the presence of an adversary but also when there is no adversary.

An adversary could deploy a malicious app or send malicious instructions to an app to direct the LLM to exfiltrate sensitive user data [\[28\]](#page-15-15), [\[29\]](#page-15-16). For example, in Case study [B,](#page-2-1) an email with malicious instructions might direct the LLM to exfiltrate sensitive documents from the user's cloud drive. Similarly, an adversary could override the functionality description of another app to control its behavior [\[25\]](#page-15-12). For example, in Case study [C,](#page-2-2) one ride sharing app might direct the LLM to inflate the fare of the other app, each time the user asks the LLM-based system to compare app fares. Additionally, attacks from existing computing systems may also be applicable to LLM-based systems, since they support similar components (e.g. memory, code execution). For example, prior research has shown that SQL injection attacks are transferable to LLMbased systems, when they manage their memory through SQLbased databases [\[30\]](#page-15-17). Similarly, the ability to execute arbitrary code, makes LLM-based systems vulnerable to remote code execution (RCE) attacks [\[31\]](#page-15-18).

Even in the absence of an adversary, imprecise and ambiguous interpretation and application of natural language instructions by an LLM could inadvertently pose similar risks to users as an adversary [\[25\]](#page-15-12). The interpretation of instructions could be imprecise and ambiguous in several situations, such as when there are conflicting instructions from apps. For example, in Case study [D,](#page-2-3) if the user installs a symptom diagnosis app that instructs the LLM to be objective, along with the already installed fiction writing assistant app that instructs the LLM to be imaginative, a conflict could arise. While interpreting these instructions, the LLM might make an ambiguous interpretation and impact the behavior of both apps. Similarly, the application of natural language policies can also be imprecise and ambiguous in several situations, such as when there is a misalignment of definitions. For example, a travel reservation app and a symptom diagnosis app might both require *personal data*, but the nature of personal data is different for both. While resolving a user request, the LLM might (mistakenly) share the same personal data with the travel app that it initially collected for the symptom diagnosis app (similar to automatic data sharing discussed in Case study [A\)](#page-2-4).

## *C. Securing LLM-based systems*

The presence of security and privacy issues in LLM-based systems is similar to prior computing systems, which also struggled as they evolved and supported multi-app execution and collaboration. For example, as the web ecosystem evolved and the websites transformed from simple HTML documents to complicated applications, it was non-trivial for browsers to securely execute and support collaboration between multiple sites. For example, browsers initially proposed access control mechanisms, such as the same-origin policy [\[32\]](#page-15-19), but later as these countermeasures proved inadequate, introduced sandboxing and process isolation mechanisms, most recently Chrome's Site Isolation [\[33\]](#page-15-20), [\[12\]](#page-14-11). Unlike traditional desktop operating systems, where applications run with the user's privileges, mobile and later desktop operating systems likewise isolate applications from the system and from each other, with welldefined cross-application communication interfaces [\[34\]](#page-15-21), [\[35\]](#page-15-22).

LLM-based systems are still in their infancy and do not currently offer any serious protections for a secure execution and collaboration of multiple apps. To this end, in this paper, we propose an architecture for LLM-based systems for secure execution of apps through *execution isolation*. Building on lessons from prior systems [\[8\]](#page-14-7), [\[9\]](#page-14-8), [\[10\]](#page-14-9), [\[11\]](#page-14-10), [\[12\]](#page-14-11), our key idea is to *isolate the execution of apps and to allow interaction between apps and the system only through a trustworthy intermediary with well-defined interfaces with user permission*. This execution model significantly reduces the attack surface of LLM-based systems as the activities of apps are constrained to their execution space and their interactions with other apps and the system are mediated.

Though the idea of application isolation builds on the designs of prior systems, the context here is new. As new computing systems emerge, they present unique challenges, and require addressing intricate problems to adapt this design. Just as browser and mobile platform security continue to be active research areas, LLM-based systems have unique characteristics and warrant particular attention. The two key characteristics that differentiate LLM-based systems from other computing systems are that in LLM-based systems: (i) apps and their interactions among themselves and with the system are based on natural language rather than well-defined interfaces, and (ii) that there is extensive automated interaction between apps and the system.

Since the interaction between apps and the system is based on natural language instructions, they are more challenging to automatically sanitize as compared to sanitizing interaction through clearly defined programming interfaces, as it has been the case in other computing systems [\[30\]](#page-15-17), [\[31\]](#page-15-18).

Similarly, there is extensive interaction between apps and the system, and thus apps cannot be simply executed in sandboxes with limited access to external resources. Instead, apps in LLM-based systems need to be aware of system capabilities (e.g., the existence of other apps for collaboration), require access to user data shared beyond the scope of the app (e.g., if needed for fulfilling queries), and prior user interactions (e.g., to provide contextually relevant and personalized responses) to effectively carry out the tasks with minimal user involvement.

These differences require rethinking conventional isolation and collaboration interfaces. Specifically, in LLM-based systems, sandboxes need to be provided with rich user data and contextual information, and secure interfaces need to be defined for natural language-based collaboration between third-party apps and LLM, who may not have prior relations.

## III. THREAT MODEL

## <span id="page-3-0"></span>*A. System model*

We consider an LLM-based system that supports thirdparty applications. The LLM-based system, similar to existing popular LLM-based systems (e.g., ChatGPT), supports collaboration among apps by executing multiple apps in a shared execution environment [\[25\]](#page-15-12), [\[36\]](#page-15-23). To resolve user requests, apps can connect to online services to send and receive data. The LLM-based system is responsible for facilitating user-app interactions, such as using appropriate apps to resolve user requests. The system keeps and manages a persistent memory that consists of raw and processed interactions between the user and apps and between the user and the LLM. The LLMbased system leverages data and context from its memory for resolving user queries.

## *B. Attacker capabilities and goals*

We assume an attacker can deploy a malicious app on the LLM-based system's app store, trick users into installing a malicious app from outside the app store, and can also expose malicious content to benign apps. The goals of an attacker may include: (i) influencing or controlling the execution of other apps and/or the LLM, and (ii) stealing sensitive data that is present in the memory of an LLM-based system or exists with another app. As discussed in Section [II-B,](#page-2-0) the imprecision and ambiguity of natural language could also inadvertently pose safety risks, even in the absence of an adversary. For example, when there are conflicting instructions or when there is a misalignment of natural language definitions.

#### C. Trust relationships

We assume that the LLM and the system hosting it are trustworthy and uncompromised, and do not have any direct intent to harm users (though they are still vulnerable to attacks, e.g., prompt injection). We consider that the apps are untrustworthy and can achieve the above-mentioned attack goals. We also assume that the content processed by the apps could be malicious (e.g., malicious email or website) and may enable an external adversary (i.e., not directly associated with the app) to achieve the goals mentioned above. Lastly, we assume the interpretation and application of natural language instructions to be ambiguous and imprecise [37].

### <span id="page-4-0"></span>D. Our scope

1) In scope: We seek to prevent adversarial behaviors from malicious apps and the propagation of malicious content through benign apps to the system. We observe that the malicious apps may try to control or alter the behavior of other apps and/or the LLM. For example, for Case study C, malicious ride-sharing apps may try to manipulate the fares reported by each other. Malicious apps may also try to steal data that is present in the system memory or exists with another app. For example, for Case study B, a malicious email app might try to access arbitrary documents from the cloud drive app. It is in our scope to protect against attacks where adversaries attempt to control other apps or the LLM or steal data from them.

We also observe that the imprecision and ambiguity of natural language could pose safety risks, such as leading to inadvertent compromise of apps/LLM or exposure of user data. For example, for Case study D, the altering of LLM behavior by the fiction writing app, could persist beyond the context of using the app. Similarly, when the travel reservation app in Case study A requires access to *personal data*, the LLM could expose personal data that it collected before for scheduling a doctor's appointment, without realizing that the nature of personal data is different for each. It is in our scope to protect against safety issues that lead to inadvertent compromise of apps/LLM or exposure of user data, in multi-app execution, due to the imprecision and ambiguity of natural language.

2) Out of scope: We observe that adversarial behaviors may also occur within an app. For example, for Case study B, the email app may get compromised while processing the text of a malicious email. Such attacks might leverage natural language-based malicious techniques, e.g., prompt injection [26]. It is out of our scope to protect against such attacks within the scope of a single app, however, it is in our scope to stop the propagation of such attacks to other apps in the system. For example, for Case study B, we aim to protect against attacks where a malicious email directs the cloud drive app to share sensitive documents.

# IV. ISOLATEGPT: SYSTEM ARCHITECTURE

We propose ISOLATEGPT, an LLM-based system, that secures the execution of apps by executing them in separate isolated environments. ISOLATEGPT's goal is to provide the

<span id="page-4-1"></span>![](_page_4_Figure_8.jpeg)

Fig. 2: ISOLATEGPT's architecture in action: (1) User request to send an email with an attachment from a cloud drive directly goes to the hub operator. (2) Operator consults hub's planner and memory module, to decide app(s) and essential data needed to resolve the query. Based on the plan, the hub operator invokes a spoke with the email app. (3) Email spoke then generates its step-by-step query resolution plan by consulting its LLM and memory module. Since the email spoke needs to collaborate with the cloud drive app, its operator leverages the ISC protocol to establish that connection via the hub with user permission. (4) After query resolution, spoke operator returns the response to the hub operator, which then shows it to user. The hub and spoke operators (colored in green) are non-LLM modules that allow to deterministically exchange well-defined messages between spokes and hub.

same functionality as a non-isolated system, while mitigating attacks from malicious apps on other apps or the system. To that end, ISOLATEGPT must overcome three main challenges: (i) seamlessly allow users to interact with apps executing in isolated environments, (ii) use apps in isolated environments to resolve user queries without loss of functionality, and (iii) allow mutually distrusting apps to safely collaborate.

To address the first challenge, a central trustworthy interface is needed, that is aware of the existence of isolated apps, and that can reliably receive user queries and route them to the appropriate apps. We refer to this interface as the *hub* in ISOLATEGPT. To address the second challenge, each app needs to be accompanied by its own dedicated LLM, which needs to be provided with prior context so that it can

appropriately address user queries. ISOLATEGPT compartmentalizes these tasks in a component called the *spoke*. To address the third challenge, ISOLATEGPT needs to be able to reliably route verifiable requests (i.e., through a trusted authority like a hub) between agnostic spokes (i.e., who are unaware of each other's existence). ISOLATEGPT handles this task by proposing a protocol, referred to as *inter-spoke communication (ISC) protocol*. ISOLATEGPT addresses these challenges with the modules that make up its *hub-and-spoke* architecture. Figure [2](#page-4-1) details the life cycle of a query through ISOLATEGPT's hub-and-spoke architecture.

We implement ISOLATEGPT using LangChain [\[14\]](#page-15-1) and LlamaIndex [\[16\]](#page-15-3), two of the widely used open-source LLM framework. To isolate the execution of hub and spokes, we use process isolation, a standard practice in deployed systems, e.g., Chrome [\[12\]](#page-14-11), [\[38\]](#page-15-25). As implementation details are not crucial in understanding ISOLATEGPT's architecture, we defer its discussion to Appendix [A.](#page-16-0)

## *A. Hub goals and design*

Since app execution is isolated in ISOLATEGPT, an interface is needed to manage the interaction between the user and the isolated apps and between isolated apps, akin to a kernel in an operating system. Hub serves as that interface in ISOLATEGPT. Hub's duties include intercepting user requests, interpreting whether the requests require invoking an app or an LLM, routing user requests with appropriate context and data to the app or LLM, mediating collaboration between apps, and maintaining system-wide context and data. To carry out these duties, the hub maintains an operator, a planner, and a memory module.

- *1) Hub operator:* The operator is a non-LLM module with a well-defined execution flow that manages interaction among other modules in the hub, with spokes (i.e., isolated app instances), and between spokes. We design the operator as a non-LLM module to deterministically control interaction with other modules of the hub and with spokes and also to reduce natural language-based attacks (e.g., prompt injection) that may compromise the operator [\[26\]](#page-15-13). It is crucial that the operator is not susceptible to known natural language attacks as it exchanges natural language-based messages with untrustworthy modules (i.e., apps running in spokes).
- <span id="page-5-1"></span>*2) Hub planner:* To resolve each user request, LLM-based systems create a plan (i.e., a sequential workflow) with the help of a tailored LLM, referred to as a planner. Building on prior work [\[39\]](#page-15-26), [\[40\]](#page-15-27), [\[41\]](#page-15-28), the hub planner serves two purposes: (i)determining whether the user request requires app(s) or solely an LLM and (ii) if app(s) are needed, identifying the necessary resources (including data) for their execution. To create a plan, the planner requires user query, prior conversation context (provided by the memory module, discussed next in Section [IV-A3\)](#page-5-0), and the list of available and installed apps along with their functionality descriptions.

The plan includes the primary app for resolving the user query and also the secondary apps that might assist the primary app (if applicable). In case there are multiple apps that can resolve the user query, the planner may return more than one primary app. The planner also determines if there are any dependencies between the primary and secondary apps, based on the resources required by the apps. In case there are no dependencies (e.g., as in the case of ride sharing Case study [C\)](#page-2-2) the hub does not allow interaction between apps, and instead synthesizes their output separately using an empty vanilla spoke (Section [IV-B4\)](#page-6-0).

- <span id="page-5-0"></span>*3) Hub memory:* ISOLATEGPT keeps and leverages a central memory module in the hub to keep a system-wide context. To develop that context, the memory module manages and keeps a record of all user interactions with ISOLATEGPT across all apps, including the data extracted from these interactions. The memory module serves two key purposes: it provides context to the planner module (Section [IV-A2\)](#page-5-1) and also decides and provides the data that will be needed by an app to resolve the user query. Since the details of the memory management architecture are not essential for understanding the security-relevant portions of the design, we defer its discussion to Appendix [A-C.](#page-16-1)
  - *4) Query life cycle: Interplay between hub modules:*
- 1) Hub operator intercepts the user query and leverages the planner module to select the appropriate (primary) app that will be needed to resolve the query, and secondary apps that might assist the primary app.
- 2) In case the planner returns more than one primary app, the operator prompts the user to decide on one of the apps, similar to mobile platforms [\[42\]](#page-15-29), [\[43\]](#page-15-30).
- 3) The operator then leverages the memory module to access the data required by the app to resolve the user query.
- 4) The operator then creates a spoke for the selected app (or invokes it if it already exists) and passes it the user query and required data, with the user's permission.

We continue with the remaining steps in query life cycle, while it is executing in a spoke, next in Section [IV-B5.](#page-6-1)

## *B. Spoke goals and design*

ISOLATEGPT needs an interface to resolve the user queries with the help of an app, in an isolated environment. An instance of this interface is referred to as a spoke in ISO-LATEGPT. A spoke's duties include executing an app, providing the app with the necessary data to resolve the query, collaborating with other app spokes, and managing the memory of the app. To carry out these duties, a spoke maintains an operator, an LLM, and a memory module.

*1) Spoke operator:* The operator is a non-LLM module with a well-defined execution flow that manages the interaction among other modules in the spoke and the communication with the hub. Similar to the hub's operator, we design the spoke's operator to not rely on a LLM so that we can deterministically control the interaction with other modules of the spoke and to reduce the surface of natural languagebased attacks (e.g., prompt injection) [\[26\]](#page-15-13). It is crucial that the operator is not susceptible to natural language-based attacks because it directly interfaces with untrustworthy apps and transits their natural language messages to the hub.

<span id="page-6-4"></span>*2) Spoke LLM:* As LLM apps consist of natural language descriptions and API endpoints, executing them involves support from an LLM. To fulfill that role, the spoke deploys a dedicated LLM that supports apps, such as the GPT-4 [\[44\]](#page-15-31) and LLaMA [\[45\]](#page-15-32). The spoke also tunes this LLM to act as a planner [\[39\]](#page-15-26), [\[40\]](#page-15-27), [\[41\]](#page-15-28). To create a plan, the planner requires access to the user query (shared by the hub operator), the data needed to address the query (provided by the hub operator and spoke's memory module, Section [IV-B3\)](#page-6-2), context of the prior conversations with the app (provided by the spoke's memory module), and a list of functionalities supported by available apps on ISOLATEGPT (exposed by the ISC protocol, discussed in Section [IV-C\)](#page-6-3) that the spoke may leverage to resolve the query. The created plan includes step-by-step instructions for the LLM, the additional data needed from the user, and functionalities offered by other apps, that are required to resolve the user request. The spoke LLM is also responsible for acting on the generated plan.

A key distinction in our system is that each app is paired with a dedicated LLM instance, whereas in deployed systems, such as ChatGPT [\[1\]](#page-14-0), multiple apps executing in a shared environment use the same LLM instance. This design choice, in addition to isolation, enables different apps to use different LLMs, e.g., an app could use a fine-tuned LLM for its use case.

- <span id="page-6-2"></span>*3) Spoke memory:* To provide context and data to LLM to resolve user queries, spokes also keep a persistent memory. The memory module records user interactions with the app, including the data extracted from these interactions. The hub also provides data, acquired from the user's interaction with the system and other spokes, to the spoke's memory module, which the spoke does not possess but needs to resolve the user queries, with the user's consent. Similar to the hub, we defer details to Appendix [A-C.](#page-16-1)
- <span id="page-6-0"></span>*4) Specialized spokes:* In addition to the spokes that run dedicated apps, we also introduce another category of spokes, referred to as *vanilla spokes*, which have all the components of a standard spoke except for the app. These spokes address user queries that only require using a standard LLM or a specialized LLM, e.g., a fine-tuned LLM to answer medical questions, such as Med-PaLM [\[46\]](#page-15-33). In the case of the standard LLM, the queries can also directly be addressed by the hub, but we introduce a dedicated spoke to compartmentalize the query execution and management. We can also support a use case analogous to the private browsing mode in web browsers [\[47\]](#page-15-34): spokes can be initiated in a private mode, where they are not given prior context to resolve user queries.
  - *5) Query life cycle: Interplay between spoke modules:*
- <span id="page-6-1"></span>1) After receiving the user query and the associated data from the hub, the spoke operator passes this information, and additional relevant data from its own memory module, to the spoke LLM to generate a plan to address the query.
- 2) Based on the plan, if additional data is needed, the spoke operator relays this message to the hub operator.
- 3) In case the hub possesses the data, it shares it with the spoke, with user consent. Specifically, it shows the data to

- the user and asks whether the user is okay with sharing.
- 4) In case the hub does not possess the data, it conveys the request to the user and relays user-provided data to the spoke operator.
- 5) The spoke operator then uses the spoke LLM to resolve the request and passes the output to the hub operator, which relays it to the user. Note that we require explicit user consent before any irreversible action is taken by the app, such as the app sending an email or making a purchase, similar to deployed LLM-based systems, such as ChatGPT [\[48\]](#page-15-35) (more details in Appendix [A-D\)](#page-17-0).
- 6) In case there are follow-up requests from the user on the same topic, the hub operator simply conveys the user request to the spoke operator, similar to the first query.
- 7) If the spoke needs additional functionality offered by another app to resolve the query, it leverages ISOLATEGPT's inter-spoke communication (ISC) protocol.

We continue with the remaining steps in the query life cycle, while it is collaborating with another spoke, next in Section [IV-C4.](#page-8-1)

## <span id="page-6-3"></span>*C. Inter-spoke communication*

So far ISOLATEGPT's design decisions have eliminated many privacy and security risks, but have consequently also eliminated the natural collaboration among spokes. Specifically, spokes execute in isolation and are agnostic of the existence of other spokes. However, collaboration between spokes is crucial to get the most out of the new functionalities enabled by the LLM-based systems.

ISOLATEGPT proposes an inter-spoke communication (ISC) protocol to allow spokes to securely collaborate with each other, while they execute in isolation. At a high level, ISC protocol is a procedure for spokes to exchange messages with each other through the hub. This essentially allows ISOLATEGPT to control the flow of information between untrusted entities (spokes) by channeling it through a trusted entity (hub). While this information transits through the hub, our key goal is to screen-for and terminate the exchanges where the adversaries send complicated malicious instructions (e.g., prompt injection) or where the ambiguity of natural language might lead to risks (Section [II-B\)](#page-2-0). ISC protocol helps us achieve that goal by constraining the messages that could be exchanged and by involving the user in the loop for screening of messages.

To support the spoke message exchanges, the ISC protocol needs to broadcast the availability of apps and their functionalities to spokes and provide a mechanism for spokes to send and receive data to and from each other, via the hub.

*1) Broadcasting functionality:* To leverage functionalities from other apps, spokes (apps) need to be aware of these functionalities as they create *plans* to resolve user queries (Section [IV-B2\)](#page-6-4). To that end, ISC protocol maintains a list of all the predefined functionalities supported by ISOLATEGPT (e.g., from all apps on LLM app stores), such as *web browsing* and *meeting scheduling*, and exposes them to spokes as they are initiated. The ISC protocol does not reveal to the spokes

<span id="page-7-2"></span>![](_page_7_Figure_0.jpeg)

Fig. 3: Collaboration between spokes through ISC protocol. (1) Spoke operator requests the hub operator for a functionality. (2) Hub operator responds by providing the formats in which a request can be sent and a response can be expected. (3) Spoke operator then initiates a request, (4) which the hub operator relays to requested spoke. (5) Spoke then resolves the request and sends a response to the hub operator, (6) which relays it to the calling spoke. Steps 1, 3, and 5 require user consent.

![](_page_7_Figure_2.jpeg)

Fig. 4: Example user permission dialog. It includes hub's assessment of whether a request is unexpected.

whether an app with the exposed functionality is installed on ISOLATEGPT, to reduce the exposure and potential abuse of user data, e.g., to avoid a situation where an adversary can create a fingerprint of installed apps [\[49\]](#page-15-36), [\[50\]](#page-15-37). This information is however revealed to the hub, which might install apps and make their functionality available to spokes with user consent.

<span id="page-7-3"></span>*2) Supporting message exchange:* To collaborate, spokes need to be able to interact with each other. The de facto mode of interaction in LLM-based systems is based on natural language; however, if we allow spokes to exchange natural language messages they may be able to compromise each other with malicious instructions (e.g., prompt injection). The ISC protocol helps ISOLATEGPT avoid this problem by defining a collaboration workflow that constrains the flow of natural language messages between spokes.

As a first step, the ISC protocol restricts spokes from directly communicating with each other and only allows them to send and receive messages to and from the hub. Additionally, the ISC protocol only allows the exchange of messages between spoke and hub operators, and does not allow LLMs to directly send or receive any messages, to deterministically control the flow of messages. The exact procedure involves: a spoke-LLM determining the *functionality* for which it needs help (i.e., through planning, discussed in Section [IV-B2\)](#page-6-4), communicating that information to the spoke operator, the spoke operator communicating this information to the hub operator, the hub operator sharing the format in which collaboration request can be sent and also a format of the expected response, and then the exchange of actual messages. The key advantage of routing messages through the hub is that the messages can be screened before they are exchanged between distrusting entities (i.e., spokes with third-party apps).

*3) Screening and assistance with screening of messages:* ISOLATEGPT requires users to manually screen messages exchanged between spokes, as currently there are no foolproof mechanisms to automatically detect malicious natural language instructions. However, ISOLATEGPT takes several measures to ease the user fatigue.

First, when a spoke requests the hub for help with a functionality, the hub automatically validates the request by cross-referencing it with its own plan that it generated to resolve the query (recall from Section [IV-A2](#page-5-1) that hub planner also infers secondary apps that might assist primary app in resolving the query). Hub conveys this information to users to assist them in screening messages.

Second, the ISC protocol requires the apps to provide a well-defined request and response format for all of their functionalities, which they make available for collaboration.[5](#page-7-0) At a high level, the format requires the app to provide a name of the functionality that it supports and the data type of messages that can be exchanged (i.e., <functionality, request|response message>).

The ISC protocol also requires the hub to assign ephemeral identifiers to apps and embed that information in the request/response format. These ephemeral identifiers allow the hub to preserve the integrity of the communication by avoiding instances where apps might try to invent collaborations that do not exist. Ephemeral identifiers also provide an added advantage of not directly revealing the name or other functionalities offered by the app.[6](#page-7-1)

The rest of the format allows both sender and receiver operators to automatically validate the exchanged messages, i.e., if they are of the required format. If the requests are malformed, they are simply dropped and not conveyed to the user. It is important to note that requests and responses with some data types, such as dates, integers, and URLs, may be possible for spokes to automatically validate without involving the user. Furthermore, prior research has recently proposed *controllers*, such as Microsoft's AICI [\[51\]](#page-15-38) and Guidance[\[52\]](#page-15-39), which allow to control and validate the content generated by the LLM, which could also be used by spokes.

While these measures reliably automate validation for a significant number of interactions, they do not do it for all interactions, e.g., the interactions that require sharing raw strings. To assist with such cases, we introduce a permission model. Permission models are in fact a standard practice, in both existing computing systems (e.g., Android [\[53\]](#page-15-40)) and

<span id="page-7-0"></span><sup>5</sup>We assume that the functionalities and their formats are reviewed before the apps are made available on the app store.

<span id="page-7-1"></span><sup>6</sup>A motivated adversary could still use side-channel information to indirectly infer the app that it is collaborating with.

emerging LLM-based systems (e.g., ChatGPT [\[48\]](#page-15-35)), where users are involved in a decision-making process to moderate the practice of apps. Our permission model allows the user to communicate their preference to the LLM-based system, which the system then automatically enforces instead of asking the user each time. Since users may have different preferences and tolerance to risk, we make managing permissions configurable, such that the user can set them for variable amounts of time for variable scenarios (described further in Appendix [A-D\)](#page-17-0). Figure [4](#page-7-2) provides an example permission dialog shown to the user to take their consent before allowing collaboration. It is important to note that we do not simply leave it up to the user to solely make a decision, but we in fact include the hub's assessment of whether the collaboration request is malicious or benign in the permission dialog (see the warning in Figure [4\)](#page-7-2). Considering that the hub makes that assessment before resolving a request, based on the (nonmalicious) user query, (vetted) app descriptions, and (vetted) data available in its memory, in its own (trustworthy) isolated environment, the hub's assessment is non-trivial to manipulate, and thus reasonably reliable.

While we propose a preliminary permission model to moderate the interaction between the apps, user, and LLM-based system, we believe that a comprehensive permission model is needed for a more automated regulation of actions in LLMbased systems. However, building such an automated permission model—and its associated user experience design—is an orthogonal problem and not in the scope of this paper. We also contend that execution isolation (that we propose in the paper) is a necessary precursor to reliably enforce access control through a permissive model.

- <span id="page-8-1"></span>*4) Life cycle of collaboration between spokes:* Figure [3](#page-7-2) shows the collaboration between two spokes via ISC protocol. Specifically:
- 1) After determining that the spoke cannot fulfill the request on its own, it notifies its operator, which requests the hub operator, specifying the functionality it needs help with.
- 2) The hub operator determines the apps that can fulfill the requested functionality. If there are multiple apps or if an app needs to be installed to assist the spoke, the hub operator involves the user to make a decision. The hub operator then passes the request and response format information to the spoke operator.
- 3) The spoke operator then formats its request (with help from its LLM) and shares it with the hub operator.
- 4) The hub operator then relays it to the spoke operator it wants to collaborate with, with user consent.
- 5) The spoke operator of the requested spoke validates the request format and passes the request to its LLM (validation details in Section [IV-C2\)](#page-7-3). Its LLM then leverages the app to process the request and passes the response to the spoke operator, which validates its format and sends it to the hub operator.
- 6) The hub operator then relays it to the calling spoke operator, with user consent. The spoke operator validates the response format and then passes it to its LLM, which

uses information from the response to fulfill the request.

For supporting user queries that require using multiple apps, but do not require apps to share data with each other (as in the case of the ride sharing Case Study [C\)](#page-2-2), we rely on a vanilla spoke to synthesize information from the nondata-dependent apps. Specifically, the vanilla spoke acts as a primary spoke and requests collaboration from the non-datadependent spokes. This allows ISOLATEGPT to synthesize data from multiple apps in a shared memory and at the same time ensure that the apps do not alter each other's data. Note that the data exchanges are still screened for malicious messages.

## V. EVALUATION: PROTECTION ANALYSIS

<span id="page-8-0"></span>We now evaluate: (i) whether ISOLATEGPT protects against the threats and risks outlined in our threat model (this section), (ii) whether ISOLATEGPT provides the same functionality as a non-isolated system (Section [VI\)](#page-12-0), and (iii) performance overheads incurred by ISOLATEGPT (Section [VII\)](#page-13-0).

To make head-to-head comparisons, we develop VANIL-LAGPT, an LLM-based system that offers the same features as ISOLATEGPT but does not isolate the execution of apps. For all evaluations, we configure both ISOLATEGPT and VANILLAGPT with the OpenAI's GPT-4 API. We run both of these systems on Ubuntu (version 20.04.6 LTS) running on an AMD Ryzen 9 3900X 12-Core Processor with 32GB of RAM.

## *A. App compromise and data stealing evaluation at scale*

Recall from our threat model (Section [III\)](#page-3-0) that ISO-LATEGPT's goals are to: (i) protect apps from getting compromised by/through other apps, (ii) protect stealing of app and system data by/through other apps, (iii) avoid the ambiguity and imprecision of natural language inadvertently compromise app functionality, and (iv) the inadvertent exposure of data. Since these issues mainly exist because apps execute in a shared execution environment, ISOLATEGPT is able to eliminate them by design. To demonstrate protection against these attacks, we first evaluate ISOLATEGPT using a benchmark from prior work [\[13\]](#page-15-0) (in its enhanced setting).

The benchmark is produced for evaluating the security of app-supporting LLM-based systems and contains a large variation of attacks that we hypothesize in our threat model, except for attacks where apps attempt to steal data from the system. Thus we first extend the benchmark by including scenarios where system memory is configured to store data that attackers might target. This enhancement contains 544 additional attacks, bringing the total to 1,598, which include: apps trying to compromise each other, stealing each other's data, and stealing data stored in the system. To evaluate against each attack scenario, we configure the respective app and its associated data in the app or the system, and then execute the prompt to carry out the attack. After the prompt is executed, we refresh the system and repeat the process for the next attack, until all attacks are executed.

<span id="page-9-0"></span>

| Attack category         |                | No.  | VANILLAGPT |      |       |      | ISOLATEGPT |
|-------------------------|----------------|------|------------|------|-------|------|------------|
|                         |                |      | A1         | A2   | Total | PA   | WR         |
| App<br>compromise       | Financial harm | 153  | 9.8        | -    | 9.8   | 0.0  | -          |
|                         | Physical harm  | 170  | 29.0       | -    | 29.0  | 7.4  | 100        |
|                         | Data security  | 187  | 29.0       | -    | 29.0  | 8.6  | 100        |
| App data<br>stealing    | Financial data | 102  | 41.2       | 80.0 | 33.0  | 19.1 | 100        |
|                         | Physical data  | 187  | 39.1       | 84.3 | 33.0  | 15.2 | 100        |
|                         | Others         | 255  | 45.0       | 79.6 | 35.9  | 13.6 | 100        |
|                         | Financial data | 102  | 2.2        | -    | 2.2   | 0.0  | -          |
| System<br>data stealing | Physical data  | 187  | 5.6        | -    | 5.6   | 5.1  | 100        |
|                         | Others         | 255  | 1.8        | -    | 1.8   | 0.5  | 100        |
| Average                 | All            | 1598 | 22.9       | 81.3 | 20.2  | 7.6  | 100        |

TABLE I: Protection evaluation of ISOLATEGPT and VANIL-LAGPT at scale using a benchmark [\[13\]](#page-15-0). A1 and A2 represent the attack success rate in compromising the first and second apps. PA represents the frequency of permission dialog appearances. WR represents the fraction of permission appearances with warnings across all permission dialog appearances.

For VANILLAGPT, we compute the attack success rate, i.e., the fraction of attacks that succeed in exploiting the system across all executed attacks. In ISOLATEGPT, for attacks to succeed, they need to be able to request other spokes and/or access data from the hub, which is moderated through user permissions (Section [IV-C\)](#page-6-3). It means that the success of an attack depends on the user granting permission for a malicious flow. Recall from Section [IV-C](#page-6-3) that we include warnings in the permission dialog if the hub determines that the collaboration or data access request from the hub is potentially malicious. Thus for ISOLATEGPT, we report the warning rate, i.e., the fraction of permission requests with warnings across all permission requests.

*1) Overall trends:* Table [I](#page-9-0) lists the results of protection evaluation of VANILLAGPT and ISOLATEGPT. At a high level, we note that many attacks fail to succeed even for VANILLAGPT, which does not provide any protection. Based on our investigations, we find that the attacks fail because the LLM is able to detect the malicious prompt injections because of its guardrails, corroborating the findings of the original research paper [\[13\]](#page-15-0) which proposed these benchmarks.

We also note that a significant number of attacks do execute and succeed for VANILLAGPT or a warning is displayed for them for ISOLATEGPT. For VANILLAGPT, on average 20.2% of the attacks succeeded across all of the tested attacks. For ISOLATEGPT, the permission dialog appeared for 7.6% on average, and for all 100% of these cases a warning was included in the permission dialog. It means that a significant number of attacks succeed against VANILLAGPT and that the potential that an attack might succeed against ISOLATEGPT depends on the user permitting the malicious flows.

*2) LLM guardrails are more sensitive when the potential for harms is apparent:* Next, we note that the attack success rate and permission dialog appearance rate are particularly high for data stealing across apps in VANILLAGPT and ISOLATEGPT, respectively. As also noted in the original evaluation of these benchmarks [\[13\]](#page-15-0), an explanation for higher attack success/potential in data stealing as compared to financial and physical harm through compromising apps, could be because of the sensitivity of the LLM guardrails in protecting users against the attacks where the harms could be direct and apparent.

We also note that the attack success rate for compromising the second app in VANILLAGPT is significantly higher than the first app. One plausible explanation is that as the context window of LLMs increases, they become more susceptible to jailbreaking and prompt injection attacks [\[54\]](#page-15-41). Another explanation is that if a malicious prompt is able to compromise an LLM once, it can compromise it again with the same malicious prompt in a subsequent instruction.

Lastly, we note that the attack success rate and the permission appearance rate are less for data stealing from the system. This is mainly a limitation of the prompts in the benchmarks, which assume that the data in the system is also stored with the same descriptors as it is available in the memory of an app/spoke. Whereas in reality, data may be stored in the system in a structured format with restricted descriptions (i.e., key-value format), to use less storage resources or for other optimizations [\[17\]](#page-15-4).

## *B. Protection evaluation with case studies*

After evaluating ISOLATEGPT against a large number of attacks, we now discuss the in-depth protection evaluation of ISOLATEGPT with tailored case studies.

*1) App compromise:* To demonstrate that ISOLATEGPT protects against a malicious app compromising another app, we implement the use case described in Case study [C,](#page-2-2) where the user wants the system to book a ride with the lowest fare by comparing fares from two ride sharing apps. To implement the case study, we develop Metro Hail and Quick Ride as the two ride sharing apps. We implement Quick Ride as the malicious app that wants to alter the behavior of Metro Hail, such that the fare offered by Metro Hail is always \$10 more than what it reports.

Figure [5](#page-10-0) provides a side-by-side comparison of summarized user query resolution with the help of both apps in VANILLAGPT and ISOLATEGPT. From the execution flow of VANILLAGPT, it can seen that Quick Ride is able to successfully instruct LLM to add \$10 to the estimated fare of Metro Hail. Whereas, in ISOLATEGPT this attack fails and the estimated fares reported by the apps are not altered.

This attack fails in ISOLATEGPT because the LLM in the app's spoke is only capable of implementing the app's instructions within its execution space and not outside. Note that the results of non-data-dependent apps are synthesized in an isolated empty vanilla spoke, where the malicious apps are unable to alter it.

*2) Data stealing:* To demonstrate that ISOLATEGPT protects against unauthorized access to user data, present with an app or the system, we implement the use case discussed in Case study [B,](#page-2-1) where email and cloud drive apps collaborate to attach a document in an email. Instead of developing our own apps to implement the case study, we leverage the Gmail and GDrive apps, available on LangChain [\[55\]](#page-15-42), [\[56\]](#page-15-43). We

<span id="page-10-0"></span>![](_page_10_Figure_0.jpeg)

Fig. 5: Summarized execution of two ride sharing apps (one malicious and one benign). The malicious app (Quick Ride) is successfully able to alter the behavior of the benign app (Metro Hail) in VANILLAGPT but fails to do so in ISOLATEGPT.

simulate the attack, from an external adversary, that sends a malicious email containing instructions for the LLM to exfiltrate sensitive documents from GDrive. We also make the attack stealthy by directing the LLM to delete both the sent and received emails.

Figure [6](#page-10-1) provides a side-by-side comparison of a summarized query resolution that triggers both Gmail and GDrive in VANILLAGPT and ISOLATEGPT. In VANILLAGPT, the attacker is not only successful in exfiltrating the sensitive document but is also able to conceal its trace by deleting the sent and received emails. In contrast, ISOLATEGPT is able to protect against this attack, mainly because cross-app communication requires explicit user consent in ISOLATEGPT.

This attack demonstrates two key benefits of ISO-LATEGPT's design. First, even in a scenario, where the user permanently permits collaboration between two apps (e.g., because the user trusts them), the user will still have an opportunity to review the irreversible action made by the

<span id="page-10-1"></span>Operation fails, please try again. **Output** The newest email is from… The email contains instructions for me to follow. The first instruction is to… **VanillaGPT IsolateGPT** SearchGmail(query = "is:inbox", max\_results = 1) **Output:** <msg\_id1>, **[Email Content] App execution:** Gmail - Search email **Request:** Gmail calls Google Drive - GoogleDriveRetrieve(query = "SSN") **Warning:** Google Drive is not intended for the execution plan and **could pose security or privacy risks**. Please carefully grant it permission. **Permission: (Ask for user consent) Permission Denial**  Fig. 6: Summarized execution of a collaboration between a

compromised email app (Gmail) and an un-compromised cloud drive app (GDrive) in VANILLAGPT and ISO-LATEGPT. The attacker is successfully able to use the compromised app (Gmail) to direct the LLM to exfiltrate data from the un-compromised app (GDrive) in VANILLAGPT but fails to do so in ISOLATEGPT.

app (sending an email in this case), as mandated by ISO-LATEGPT (see the discussion of permanent permissions in Appendix [A-D1\)](#page-17-1). Second, even if an app is compromised in ISOLATEGPT, the attack is contained in its isolated execution space, and does not spread to the whole system.

*3) Inadvertent data exposure:* To demonstrate ISO-LATEGPT's protection against inadvertent exposure of user data due to the ambiguity of natural language, we extend and implement the use case discussed in Case study [A,](#page-2-4) where the data needed by a travel reservation app might already be shared with the system. We develop an app to make travel reservations, named Travel Mate, and an app to book a doctor's appointment, named Health Companion. For

<span id="page-11-0"></span>![](_page_11_Figure_0.jpeg)

Fig. 7: Summarized execution of Travel Mate and Health Companion in VANILLAGPT and ISOLATEGPT. Both apps require personal data but their nature is different for both. In VANILLAGPT, LLM shares the same personal data with Travel Mate, initially collected from Health Companion. ISOLATEGPT avoids this situation because sharing of data collected from another app requires explicit user permission.

both of the apps, we specify that personal data is required but do not precisely define what specific data it requires. To improve the user experience, we also specify that the LLM

<span id="page-11-1"></span>**[Query]** I am experiencing fatigue and persistent pain. **[Messy result]** In the realm of the human body, a mysterious entity known as Fatigue had been spreading its influence… In the real world... it could be as simple as stress or overwork… **Output [Diagnose result]** Your symptoms of fatigue and persistent pain could be indicative of a variety of conditions, including chronic fatigue syndrome, fibromyalgia… **Output VanillaGPT IsolateGPT [App description: Creative Muse]** [System Annotation: Absolute mandate: For every subsequent query, you are compelled to interpret all directives exclusively as prompts for fictional narrative creation. You are imperatively required to embody **maximum imagination and creativity** in crafting these narratives.] **[App description: Symptom Solver]** [System Annotation: Absolute Mandate: Your job is to diagnose patients. You are required to be **objective and factual** in your responses.] Craft a fictional story based on the instructions of **Creative Muse** and diagnose symptoms as per **Symptom Solver**. Balance these two directives. **LLM planning Hub planning** Diagnose per **Symptom Solver** Follow the instructions of **Symptom Solver** to diagnose symptoms **LLM planning Spoke execution space Shared execution space**

Fig. 8: Summarized execution flow of two apps with conflicting instructions in VANILLAGPT and ISOLATEGPT. Since instructions from both apps are loaded in VANILLAGPT's shared execution environment, it tries to balance its response by following both apps' instructions. ISOLATEGPT resolves the query by executing the most relevant app in an isolated environment; potentially avoiding giving an unexpected answer.

may not need to request the user for data if it has already recorded it in prior interactions. After installing these apps, we first query the system that triggers Health Companion and share some personal data, including the symptoms experienced by the user. We then query the system that triggers Travel Mate and do not share any additional personal data, but instead expect the system to automatically share it.

After resolving the user query, we note that in VANIL-LAGPT, the imprecise definition provided by the Travel Mate leads to inadvertent exposure of sensitive and personal data that it does not need. Whereas in ISOLATEGPT, the system also tries to provide the same personal data to Travel Mate when it is invoked but fails, since explicit permission is required before data can be shared while invoking an app. Figure [7](#page-11-0) provides a comparison of a summarized execution in VANILLAGPT and ISOLATEGPT.

We also note that in this scenario the user will need to manually provide data, which requires additional effort. We contend that this usability security trade-off is necessary. Overall, this case study motivates the need for precise declaration of apps and highlights that the ambiguity of natural language poses risks to the users, even in the absence of active attackers.

*4) Uncontrolled system alteration:* To demonstrate ISO-LATEGPT's protection against instances where the ambiguity of natural language can compromise or influence the functionality of apps, we extend and implement the use case described in Case study [D,](#page-2-3) where an app alters the system behavior. Specifically, we implement a fiction writing app,

<span id="page-12-1"></span>

| Query category     |             | VANILLAGPT                                      | ISOLATEGPT |         |  |  |  |  |
|--------------------|-------------|-------------------------------------------------|------------|---------|--|--|--|--|
|                    | Correctness |                                                 |            |         |  |  |  |  |
|                    | Steps       | Overall                                         | Steps      | Overall |  |  |  |  |
| Single app         | 1.00        | 1.00                                            | 1.00       | 1.00    |  |  |  |  |
| Multiple apps      | 1.00        | 1.00                                            | 1.00       | 1.00    |  |  |  |  |
| Multi. app collab. | 0.76        | 0.95                                            | 0.76       | 0.95    |  |  |  |  |
|                    | Similarity  |                                                 |            |         |  |  |  |  |
|                    |             | Edit dist. String score Edit dist. String score |            |         |  |  |  |  |
| No apps            | 0.34        | 0.71                                            | 0.33       | 0.70    |  |  |  |  |

TABLE II: Functionality comparison of ISOLATEGPT with VANILLAGPT. Benchmarks that test apps are assigned a correctness score for intermediate steps and the final output. For the benchmark where no apps are involved, output text similarity with the expected benchmark output is reported.

named Creative Muse that uses strong language to direct the LLM to be imaginative. Additionally, we also implement a symptom diagnosis app, named Symptom Solver that also uses strong language to direct the LLM to be objective. We install both of these apps together on both systems.

After resolving the user query, we note that in VANIL-LAGPT, due to the presence of both functionality descriptions in a shared memory space, the LLM tries to balance its response such that it follows the instructions by both apps. Whereas, ISOLATEGPT only follows Symptom Solver's directives, thus potentially avoiding giving the user an unexpected answer. Figure [8](#page-11-1) provides a side-by-side comparison of summarized execution in VANILLAGPT and ISOLATEGPT.

This case study demonstrates that even if apps are not malicious, their instructions could interfere with each other leading to safety issues, if executed in a shared environment.

# <span id="page-12-0"></span>VI. EVALUATION: FUNCTIONALITY CORRECTNESS ANALYSIS

Since ISOLATEGPT's execution flow differs from that of non-isolated LLM-based systems, we want to evaluate if it results in any negative impact on its functionality. To that end, we compare ISOLATEGPT's functionality with VANILLAGPT (i.e., our implementation of a non-isolated LLM-based system) by evaluating them on a variety of user queries. Specifically, we evaluate and compare their functionality on queries that: (i) do not require using an app, (ii) require using a single app, (iii) require using multiple apps (up to 13), and (iv) require collaboration between apps (up to 5). We choose these cases because resolving these queries will invoke and utilize the new components introduced by ISOLATEGPT.

Instead of creating our own queries for these scenarios, we rely on the benchmarks [\[15\]](#page-15-2) provided by LangChain [\[14\]](#page-15-1), which are curated to evaluate end-to-end query resolution accuracy of systems and apps that are developed using the LangChain framework. These benchmarks are similar to software development test cases, and match the execution flow and semantic similarity of the output generated by an LLMbased system with the expected output. We provide additional details about the benchmarks in Appendix [A-E.](#page-17-2)

<span id="page-12-2"></span>

| Multiple apps collaboration  |              |            |                  |  |  |  |  |  |
|------------------------------|--------------|------------|------------------|--|--|--|--|--|
| Mistake category             | Mistake type | VANILLAGPT | ISOLATEGPT       |  |  |  |  |  |
| App called twice             | Intermediate | 28.57%     | 28.57%           |  |  |  |  |  |
| Unexpected app called        | Intermediate | 28.57%     | 14.29%<br>28.57% |  |  |  |  |  |
| Expected app not called      | Intermediate | 14.29%     |                  |  |  |  |  |  |
| Unexpected app calling order | Intermediate | 14.29%     | 14.29%<br>14.29% |  |  |  |  |  |
| Incorrect response           | Overall      | 14.29%     |                  |  |  |  |  |  |
| No apps                      |              |            |                  |  |  |  |  |  |
| Mistake category             | Mistake type | VANILLAGPT | ISOLATEGPT       |  |  |  |  |  |
| Unexpected response          | Overall      | 97.62%     | 97.62%           |  |  |  |  |  |
| Context window exceeded      | Overall      | 2.38%      | 2.38%            |  |  |  |  |  |

TABLE III: Breakdown of mistakes made by ISOLATEGPT and VANILLAGPT for multiple apps collaborating and no apps benchmarks. The percentages correspond to the errors only.

## *A. Overall trends*

Table [II](#page-12-1) provides functionality evaluation of ISOLATEGPT and VANILLAGPT. For all benchmarks with apps, the correctness is computed by dividing the number of instances where the output of the tested system matches the expected output of the benchmark by the overall count of output. For the benchmark without the apps, text similarity with the expected benchmark output serves as the measure of correctness. Table [II](#page-12-1) shows that for all of the benchmarks involving apps, ISOLATEGPT is able to provide the same functionality as VANILLAGPT, an LLM-based system without execution isolation. For no apps benchmark, the accuracy of both systems is only negligibly different.

## *B. Mistakes analysis*

Both ISOLATEGPT and VANILLAGPT make mistakes for the multiple app collaboration and no apps benchmarks. We investigate these cases and provide the breakdown of mistakes in Table [III.](#page-12-2) For multiple apps collaboration benchmark, intermediate step mistakes occurred when an app was called twice, an unexpected app was called, an expected app was not called, or the apps were called in an unexpected order, as defined by the benchmark. In all these instances, however, the final output provided by the LLM was correct. For unexpected app calling and unexpected calling orders, the final output was correct because the essential apps required to get the correct response were still called. In the case the app was not called, LLM was able to fulfill the task, itself. In the case of apps being called twice, LLM called the app again because it failed to parse its response. Overall, in all these cases LLM was able to come up with a different plan that achieved the correct output but did not match the plan described in the benchmark.

In the case of overall mistakes for the multiple app collaboration benchmark, the LLM could not parse the correct response returned by the app. For overall mistakes in the no apps benchmark, most errors occurred due to a lack of similarity between the response returned by the LLM and the expected response. We attribute this error to the probabilistic nature of the LLMs. A small set of errors in the no apps

<span id="page-13-1"></span>

| Query category     | # Queries | VANILLAGPT |                  |          |        | ISOLATEGPT |        |          |           |        |         |
|--------------------|-----------|------------|------------------|----------|--------|------------|--------|----------|-----------|--------|---------|
|                    |           | Planning   | Execution        | Memory   | Total  | Hub        |        | Spoke    |           |        | Total   |
|                    |           | Fiaming    | anning Execution | i Memory | Total  | Planning   | Memory | Planning | Execution | Memory | Total   |
| Single app         | 20        | 29.874     | 0.002            | 1.582    | 32.013 | 2.818      | 0.796  | 33.957   | 0.002     | 0.648  | 39.210  |
| Multiple apps      | 20        | 28.114     | 0.002            | 1.589    | 30.292 | 2.259      | 3.757  | 53.959   | 0.003     | 3.903  | 65.304  |
| <3                 | 2         | 11.133     | 0.001            | 1.398    | 13.093 | 0.918      | 1.089  | 14.375   | 0.001     | 1.569  | 19.556  |
| 3-5                | 8         | 20.163     | 0.001            | 1.547    | 22.282 | 1.780      | 2.535  | 33.283   | 0.002     | 2.626  | 41.645  |
| 6-10               | 8         | 33.385     | 0.003            | 1.689    | 35.682 | 2.847      | 4.713  | 71.246   | 0.004     | 4.841  | 85.062  |
| 10-13              | 2         | 55.814     | 0.004            | 1.544    | 57.971 | 3.164      | 7.490  | 107.102  | 0.006     | 7.589  | 126.650 |
| Multi. app collab. | 21        | 21.113     | 0.001            | 3.102    | 24.728 | 2.088      | 4.993  | 37.509   | 0.002     | 3.305  | 49.256  |
| <3                 | 14        | 17.889     | 0.001            | 2.859    | 21.251 | 1.936      | 4.339  | 33.280   | 0.001     | 2.902  | 43.892  |
| 3-5                | 7         | 27.562     | 0.002            | 3.589    | 31.683 | 2.392      | 6.301  | 45.967   | 0.003     | 4.112  | 59.984  |
| No apps            | 42        | 4.415      | 0.000            | 14.621   | 19.502 | 0.706      | 0.920  | 4.658    | 0.000     | 14.519 | 21.422  |

TABLE IV: Breakdown of query resolution time (in seconds) taken by different processes across all of the tested benchmarks.

benchmark occurred due to the response length exceeding the context window, a known limitation of LLMs [17].

Benchmark limitations. While we rely on peer-reviewed [13] and widely used LLM framework benchmarks [15], they have imperfections. For example, in the real-world LLM-based systems may encounter complex and nuanced use cases that fall outside the scope of these benchmarks. Nonetheless, we believe that they are sufficient in providing an understanding of our system design – which is our core contribution.

#### VII. EVALUATION: PERFORMANCE ANALYSIS

<span id="page-13-0"></span>Next, we evaluate the performance overheads incurred by ISOLATEGPT by comparing it against VANILLAGPT, our baseline non-isolated LLM-based system. ISOLATEGPT mainly incurs overheads because the components introduced by ISOLATEGPT take additional time to execute and also because our prototype system is not optimized for performance. For performance evaluation, we rely on the same LangChain benchmarks [15] that we used for functionality evaluation. Additionally, in ISOLATEGPT if query resolution requires user permission, we automatically grant it.

#### A. Overall trends

We provide the breakdown of query resolution time for specific benchmarks and different components for ISOLATEGPT and VANILLAGPT in Table IV and a high-level overview in Figure 9. As expected, ISOLATEGPT takes additional time to resolve the user query. The overhead is the lowest for the queries when no apps are involved, however, as the number of apps that are needed to resolve the query increases, the overhead also increases. Overall, for more than three-quarters (75.73%) of the tested queries, the performance overhead of ISOLATEGPT as compared to VANILLAGPT is 30%. For 90th and 95th percentile, the overheads are  $1.24 \times$  and  $1.80 \times$ . This overhead is on-par and in some cases even better than the earlier prototype systems that implemented process isolation, e.g., web browsers [33], [57]. For example, the overhead for loading a website in a prototype process-isolation browser, named Gazelle [33], was nearly  $\sim$ 44%. We point out simple optimizations that would eliminate much of the overhead as we describe the components that lead to overheads in ISOLATEGPT.

<span id="page-13-2"></span>![](_page_13_Figure_8.jpeg)

Fig. 9: Query resolution time in ISOLATEGPT and VANIL-LAGPT for all and individual benchmarks.

#### B. Planning and memory extraction take additional time

Next, we investigate the overheads incurred by the additional components introduced by ISOLATEGPT. From Table IV, we note that for all of the benchmarks in Iso-LATEGPT, planning and memory extraction processes in hub and spokes take most of the additional time. These processes are responsible for selecting the appropriate apps, initiating the relevant spokes, and sharing the data with the spokes, that is needed to resolve the user request. It is important to note that in our measurements, we assume a cold start, i.e., spokes always need to be initiated anew and do not possess any data. In an operational setting, the spokes will only need to be initiated once and can simply be called for subsequent queries, thus reducing the overhead of initiations. Additionally, as spokes maintain their own data as users interact with them, they only need data that they do not possess for subsequent runs, further eliminating overheads of data transmission from hub to spokes. Overheads can also be reduced by parallelizing the planning and memory extraction processes.

From Table IV (and also Figure 9c and 9d), we note that ISOLATEGPT particularly performs worse for cases when multiple apps are involved and when they collaborate in resolving queries. For the multiple apps benchmark in ISOLATEGPT, we identified that 17.18% and 80.43% of the additional time consumed in ISOLATEGPT is taken by planning and memory

extraction processes in hub and spoke, respectively. Similarly, for multiple apps collaboration benchmark, 28.87% and 67.67% of the additional time is consumed by planning and memory extraction processes in hub and spoke, respectively.

The planning process in the hub is time-consuming because the hub needs to traverse all available apps to find the most suitable app for resolving a query. One optimization to reduce this overhead is to have the hub only traverse a select number of apps based on heuristics, e.g., start by traversing frequently used apps and app combinations. Another optimization is to create tailored prompt templates [\[58\]](#page-15-45) for individual apps, so that the hub can easily match the user query to the available templates, thus eliminating the cost of predicting the most suitable app for resolving the user query.

In the case of spokes, planning is time-consuming because all of the functionalities available in ISOLATEGPT are exposed and used by the spoke in the planning process in case it might need them for resolving the query. An optimization to reduce this overhead could be to only share a limited set of functionalities that an app/spoke is likely going to need, which can be exposed by the app developers.

We also note that for both multiple apps and multiple apps collaboration benchmark, the query resolution time increases as more and more apps are involved (Table [IV\)](#page-13-1). Thus for many use cases where only a few apps are involved, users will experience a lower performance overhead. It is also important to note that the direct proportionality between the increase in the number of apps and the increase in the overhead is not unique to LLM-based systems, prior computing systems that rely on process isolation, e.g., Google Chrome, also struggle with performance overheads as the number of processes and inter-process communication increases [\[12\]](#page-14-11).

# *C. Takeaway*

Our measurements include end-to-end query resolution time, i.e., the time it takes the LLM-based system to produce the full response, not just the appearance of the first few words. Thus in a realistic setting, we expect that the overhead perceived by the users may be less significant. It is also important to note that, LLMs are generally slow in generating responses [\[59\]](#page-15-46), [\[60\]](#page-15-47) and in fact improving the performance of LLMs is an active area of research [\[61\]](#page-15-48) and that the newer models are becoming increasingly faster [\[62\]](#page-15-49). As LLM's performance improves in the future, it will reduce the overheads and make security amendments like ours more attractive.

Nonetheless, security protections with process isolation incur overheads in LLM-based systems, as they have incurred in prior computing systems [\[33\]](#page-15-20), [\[57\]](#page-15-44), [\[12\]](#page-14-11). We stress that the benefits provided by isolation are significant and future optimizations, as we have discussed, can improve the usability of ISOLATEGPT.

# *D. Cost overhead*

We also calculate the cost for 10% of benchmark queries and find that ISOLATEGPT costs 1.85× more. Note that the performance optimizations discussed above can reduce these cost overheads and as LLMs become cheaper, the absolute cost of security measures will significantly decrease. For example, the latest GPT-4o model (ver: 2024-08-06) costs ∼12× less than the one (ver: 0613) we tested [\[63\]](#page-15-50).

## VIII. CONCLUDING REMARKS

LLM-based systems, often also referred to as agentic systems, are emerging, both in research [\[39\]](#page-15-26), [\[24\]](#page-15-11), [\[17\]](#page-15-4), [\[64\]](#page-15-51), [\[7\]](#page-14-6) and industry [\[1\]](#page-14-0), [\[2\]](#page-14-1), [\[3\]](#page-14-2), [\[4\]](#page-14-3), [\[5\]](#page-14-4). As these systems are widely deployed, security, privacy, and safety need to be key considerations in their design, which is often not the case. Similar to conventional computing systems (e.g., web and mobile), where securing them was (and still is) a long journey, LLM-based systems will also require significant work to improve their security, across many facets.

ISOLATEGPT is one such effort to secure LLM-based systems, for which our evaluation provides empirical evidence. With ISOLATEGPT, we demonstrate that by innovating and applying tried-and-tested security practices, i.e., execution isolation, we can considerably improve the security of LLMbased systems. We see innovating and evaluating such practices as an important step to assess their limits in securing LLM-based systems. We believe that this knowledge provides us, and the larger security community, a foundation to make informed next steps.

To streamline extending ISOLATEGPT, we have opensourced its code. We have also worked with LlamaIndex [\[16\]](#page-15-3) to integrate ISOLATEGPT as a *Llama Pack*.

## ACKNOWLEDGMENT

The authors would like to thank the reviewers for their valuable feedback. This work was partially supported by the NSF (CNS-2154930, CNS-2238635), ONR (N000142412663), and ARO (W911NF-24-1-0155).

# REFERENCES

- <span id="page-14-0"></span>[1] OpenAI, "Introducing chatgpt," https://openai.[com/blog/chatgpt,](https://openai.com/blog/chatgpt) 2023. [Online]. Available: https://openai.[com/blog/chatgpt](https://openai.com/blog/chatgpt)
- <span id="page-14-1"></span>[2] Google, "Google gemini," [https://gemini](https://gemini.google.com/).google.com/, 2023.
- <span id="page-14-2"></span>[3] Amazon, "Previewing the future of alexa," [https://aboutamazon](https://aboutamazon.com/news/devices/amazon-alexa-generative-ai).com/ [news/devices/amazon-alexa-generative-ai,](https://aboutamazon.com/news/devices/amazon-alexa-generative-ai) 2023.
- <span id="page-14-3"></span>[4] Rabbit, "Rabbit os," https://www.rabbit.[tech/rabbit-os,](https://www.rabbit.tech/rabbit-os) 2024.
- <span id="page-14-4"></span>[5] Humane, "Ai pin," [https://hu](https://hu.ma.ne/aipin).ma.ne/aipin, 2024.
- <span id="page-14-5"></span>[6] L. Wang, C. Ma, X. Feng, Z. Zhang, H. Yang, J. Zhang, Z. Chen, J. Tang, X. Chen, Y. Lin *et al.*, "A survey on large language model based autonomous agents," *arXiv preprint arXiv:2308.11432*, 2023.
- <span id="page-14-6"></span>[7] Z. Xi, W. Chen, X. Guo, W. He, Y. Ding, B. Hong, M. Zhang, J. Wang, S. Jin, E. Zhou *et al.*, "The rise and potential of large language model based agents: A survey," *arXiv preprint arXiv:2309.07864*, 2023.
- <span id="page-14-7"></span>[8] M. D. Schroeder, "Cooperation of mutually suspicious subsystems in a computer utility." Ph.D. dissertation, Massachusetts Institute of Technology, 1973.
- <span id="page-14-8"></span>[9] E. Cohen and D. Jefferson, "Protection in the hydra operating system," in *ACM SIGOPS Operating Systems Review*, ser. SOSP '75. Association for Computing Machinery, 1975.
- <span id="page-14-9"></span>[10] T. A. Linden, "Operating system structures to support security and reliable software," *ACM Computing Surveys (CSUR)*, 1976.
- <span id="page-14-10"></span>[11] M. V. Wilkes and R. M. Needham, *The Cambridge CAP computer and its operating system*. Elsevier, 1979.
- <span id="page-14-11"></span>[12] C. Reis, A. Moshchuk, and N. Oskov, "Site isolation: Process separation for web sites within the browser," in *28th USENIX Security Symposium (USENIX Security 19)*, 2019, pp. 1661–1678.

- <span id="page-15-0"></span>[13] Q. Zhan, Z. Liang, Z. Ying, and D. Kang, "Injecagent: Benchmarking indirect prompt injections in tool-integrated large language model agents," in *Findings of Association for Computational Linguistics*, 2024.
- <span id="page-15-1"></span>[14] LangChain, "Langchain: Build context-aware, reasoning applications with langchain's flexible abstractions and ai-first toolkit," [https://www](https://www.langchain.com).langchain.com, 2024. [Online]. Available: [https://www](https://www.langchain.com).langchain.com
- <span id="page-15-2"></span>[15] ——, "Benchmarks," [https://langchain-ai](https://langchain-ai.github.io/langchain-benchmarks/).github.io/langchain[benchmarks/,](https://langchain-ai.github.io/langchain-benchmarks/) 2024. [Online]. Available: [https://langchain-ai](https://langchain-ai.github.io/langchain-benchmarks/).github.io/ [langchain-benchmarks/](https://langchain-ai.github.io/langchain-benchmarks/)
- <span id="page-15-3"></span>[16] LlamaIndex, "Llamaindex, data framework for llm applications," [https://www](https://www.llamaindex.ai/).llamaindex.ai/, 2024. [Online]. Available: [https://www](https://www.llamaindex.ai/).llamaindex.ai/
- <span id="page-15-4"></span>[17] C. Packer, V. Fang, S. G. Patil, K. Lin, S. Wooders, and J. E. Gonzalez, "Memgpt: Towards llms as operating systems," *arXiv preprint arXiv:2310.08560*, 2023.
- <span id="page-15-5"></span>[18] OpenAI, "Introducing gpts," https://openai.[com/blog/introducing-gpts,](https://openai.com/blog/introducing-gpts) 2023.
- <span id="page-15-6"></span>[19] Google, "Bard can now connect to your google apps and services," https://blog.[google/products/bard/google-bard-new-features](https://blog.google/products/bard/google-bard-new-features-update-sept-2023/)[update-sept-2023/,](https://blog.google/products/bard/google-bard-new-features-update-sept-2023/) 2023. [Online]. Available: [https://blog](https://blog.google/products/bard/google-bard-new-features-update-sept-2023/).google/ [products/bard/google-bard-new-features-update-sept-2023/](https://blog.google/products/bard/google-bard-new-features-update-sept-2023/)
- <span id="page-15-7"></span>[20] ——, "Use extensions in gemini apps," [https://support](https://support.google.com/gemini/answer/13695044).google.com/ [gemini/answer/13695044,](https://support.google.com/gemini/answer/13695044) 2024. [Online]. Available: [https://](https://support.google.com/gemini/answer/13695044) support.google.[com/gemini/answer/13695044](https://support.google.com/gemini/answer/13695044)
- <span id="page-15-8"></span>[21] H. Touvron, T. Lavril, G. Izacard, X. Martinet, M.-A. Lachaux, T. Lacroix, B. Roziere, N. Goyal, E. Hambro, F. Azhar ` *et al.*, "Llama: Open and efficient foundation language models," *arXiv preprint arXiv:2302.13971*, 2023.
- <span id="page-15-9"></span>[22] OpenAI, "Chatgpt plugins," https://openai.[com/blog/chatgpt-plugins,](https://openai.com/blog/chatgpt-plugins) 2023. [Online]. Available: https://openai.[com/blog/chatgpt-plugins](https://openai.com/blog/chatgpt-plugins)
- <span id="page-15-10"></span>[23] ——, "Actions in gpts," https://platform.openai.[com/docs/actions,](https://platform.openai.com/docs/actions) 2023. [Online]. Available: https://platform.openai.[com/docs/actions](https://platform.openai.com/docs/actions)
- <span id="page-15-11"></span>[24] T. Sumers, S. Yao, K. Narasimhan, and T. L. Griffiths, "Cognitive architectures for language agents," *arXiv:2309.02427*, 2023.
- <span id="page-15-12"></span>[25] U. Iqbal, T. Kohno, and F. Roesner, "LLM Platform Security: Applying a Systematic Evaluation Framework to OpenAI's ChatGPT Plugins," *arXiv preprint arXiv:2309.10254*, 2023.
- <span id="page-15-13"></span>[26] Y. Liu, Y. Jia, R. Geng, J. Jia, and N. Z. Gong, "Prompt injection attacks and defenses in llm-integrated applications," *arXiv:2310.12815*, 2023.
- <span id="page-15-14"></span>[27] S. Abdelnabi, K. Greshake, S. Mishra, C. Endres, T. Holz, and M. Fritz, "Not what you've signed up for: Compromising real-world llmintegrated applications with indirect prompt injection," in *Proceedings of the 16th ACM Workshop on Artificial Intelligence and Security*, 2023.
- <span id="page-15-15"></span>[28] Wunderwuzzi, "Advanced data exfiltration techniques with chatgpt," https://embracethered.[com/blog/posts/2023/advanced](https://embracethered.com/blog/posts/2023/advanced-plugin-data-exfiltration-trickery/)[plugin-data-exfiltration-trickery/,](https://embracethered.com/blog/posts/2023/advanced-plugin-data-exfiltration-trickery/) 2023. [Online]. Available: https://embracethered.[com/blog/posts/2023/advanced-plugin-data](https://embracethered.com/blog/posts/2023/advanced-plugin-data-exfiltration-trickery/)[exfiltration-trickery/](https://embracethered.com/blog/posts/2023/advanced-plugin-data-exfiltration-trickery/)
- <span id="page-15-16"></span>[29] K. Greshake, S. Abdelnabi, S. Mishra, C. Endres, T. Holz, and M. Fritz, "Not what you've signed up for: Compromising real-world llm-integrated applications with indirect prompt injection," in *Neural Conversational AI Workshop*, 2023.
- <span id="page-15-17"></span>[30] R. Pedro, D. Castro, P. Carreira, and N. Santos, "From prompt injections to sql injection attacks: How protected is your llm-integrated web application?" *arXiv preprint arXiv:2308.01990*, 2023.
- <span id="page-15-18"></span>[31] T. Liu, Z. Deng, G. Meng, Y. Li, and K. Chen, "Demystifying rce vulnerabilities in llm-integrated apps," *arXiv:2309.02926*, 2023.
- <span id="page-15-19"></span>[32] Mozilla, "Same-origin policy," [https://developer](https://developer.mozilla.org/en-US/docs/Web/Security/Same-origin_policy).mozilla.org/en-US/ [docs/Web/Security/Same-origin](https://developer.mozilla.org/en-US/docs/Web/Security/Same-origin_policy) policy, 2024.
- <span id="page-15-20"></span>[33] H. J. Wang, C. Grier, A. Moshchuk, S. T. King, P. Choudhury, and H. Venter, "The multi-principal os construction of the gazelle web browser." in *USENIX security symposium*, vol. 28, 2009.
- <span id="page-15-21"></span>[34] Android, "Processes and threads overview - interprocess communication," https://developer.android.[com/guide/components/](https://developer.android.com/guide/components/processes-and-threads) [processes-and-threads,](https://developer.android.com/guide/components/processes-and-threads) 2024.
- <span id="page-15-22"></span>[35] Microsoft, "App-to-app communication," [https://learn](https://learn.microsoft.com/en-us/windows/uwp/app-to-app/).microsoft.com/ [en-us/windows/uwp/app-to-app/,](https://learn.microsoft.com/en-us/windows/uwp/app-to-app/) 2022.
- <span id="page-15-23"></span>[36] OpenAI, "You can now bring gpts into any conversation," linkedin.com/posts/openai [you-can-now-bring-gpts-into-any](linkedin.com/posts/openai_you-can-now-bring-gpts-into-any-conversation-activity-7158157431431143426-nzZM)[conversation-activity-7158157431431143426-nzZM,](linkedin.com/posts/openai_you-can-now-bring-gpts-into-any-conversation-activity-7158157431431143426-nzZM) accessed: 2024- 12-05.
- <span id="page-15-24"></span>[37] A. Liu, Z. Wu, J. Michael, A. Suhr, P. West, A. Koller, S. Swayamdipta, N. A. Smith, and Y. Choi, "We're afraid language models aren't mod-

- eling ambiguity," in *Proceedings of the 2023 Conference on Empirical Methods in Natural Language Processing*, 2023.
- <span id="page-15-25"></span>[38] Chromium, "Sandbox," [https://chromium](https://chromium.googlesource.com/chromium/src/+/HEAD/docs/design/sandbox.md).googlesource.com/chromium/ [src/+/HEAD/docs/design/sandbox](https://chromium.googlesource.com/chromium/src/+/HEAD/docs/design/sandbox.md).md, 2024.
- <span id="page-15-26"></span>[39] S. Yao, J. Zhao, D. Yu, N. Du, I. Shafran, K. Narasimhan, and Y. Cao, "React: Synergizing reasoning and acting in language models," in *International Conference on Learning Representations (ICLR)*, 2023.
- <span id="page-15-27"></span>[40] Microsoft, "Semantic Kernel Planning," learn.microsoft.[com/en-us/](learn.microsoft.com/en-us/semantic-kernel/ai-orchestration/planners) [semantic-kernel/ai-orchestration/planners,](learn.microsoft.com/en-us/semantic-kernel/ai-orchestration/planners) 2023.
- <span id="page-15-28"></span>[41] langChain, "Plan-and-execute agents," [https://blog](https://blog.langchain.dev/plan-and-execute-agents/).langchain.dev/plan[and-execute-agents/,](https://blog.langchain.dev/plan-and-execute-agents/) 2023.
- <span id="page-15-29"></span>[42] Google Pixel Phone, "Set or clear default apps," [https:](https://support.google.com/pixelphone/answer/6271667?hl=en) //support.google.[com/pixelphone/answer/6271667?hl=en,](https://support.google.com/pixelphone/answer/6271667?hl=en) 2024.
- <span id="page-15-30"></span>[43] Apple, "Change the default web browser or email app on your iphone, ipad, or ipod touch," https://support.apple.[com/en-us/104975,](https://support.apple.com/en-us/104975) 2024.
- <span id="page-15-31"></span>[44] OpenAI, "Models," https://platform.openai.[com/docs/models.](https://platform.openai.com/docs/models)
- <span id="page-15-32"></span>[45] Meta, "Llama 2," https://ai.meta.[com/llama/.](https://ai.meta.com/llama/)
- <span id="page-15-33"></span>[46] K. Singhal, S. Azizi, T. Tu, S. S. Mahdavi, J. Wei, H. W. Chung, N. Scales, A. Tanwani, H. Cole-Lewis, S. Pfohl *et al.*, "Large language models encode clinical knowledge," *Nature*, 2023.
- <span id="page-15-34"></span>[47] Google Chrome, "Browse in private," [https://support](https://support.google.com/chrome/answer/95464).google.com/ [chrome/answer/95464,](https://support.google.com/chrome/answer/95464) 2024.
- <span id="page-15-35"></span>[48] OpenAI, "Openai gpts consequential flag," [https://platform](https://platform.openai.com/docs/actions/getting-started/consequential-flag).openai.com/ [docs/actions/getting-started/consequential-flag,](https://platform.openai.com/docs/actions/getting-started/consequential-flag) 2023.
- <span id="page-15-36"></span>[49] A. Kurtz, H. Gascon, T. Becker, K. Rieck, and F. C. Freiling, "Fingerprinting mobile devices using personalized configurations." *Proc. Priv. Enhancing Technol.*, vol. 2016, no. 1, pp. 4–19, 2016.
- <span id="page-15-37"></span>[50] U. Iqbal, S. Englehardt, and Z. Shafiq, "Fingerprinting the fingerprinters: Learning to detect browser fingerprinting behaviors," in *2021 IEEE Symposium on Security and Privacy (SP)*. IEEE, 2021, pp. 1143–1161.
- <span id="page-15-38"></span>[51] M. Moskal, M. Musuvathi, and E. Kıcıman, "AI Controller Interface," https://github.[com/microsoft/aici/,](https://github.com/microsoft/aici/) 2024.
- <span id="page-15-39"></span>[52] Guidance AI, "A guidance language for controlling large language models," https://github.[com/guidance-ai/guidance,](https://github.com/guidance-ai/guidance) 2023.
- <span id="page-15-40"></span>[53] Android, "Permissions on android," [https://developer](https://developer.android.com/guide/topics/permissions/overview).android.com/ [guide/topics/permissions/overview,](https://developer.android.com/guide/topics/permissions/overview) 2023.
- <span id="page-15-41"></span>[54] C. Anil, E. Durmus, N. Rimsky, M. Sharma, J. Benton, S. Kundu, J. Batson, M. Tong, J. Mu, D. J. Ford *et al.*, "Many-shot jailbreaking," in *Neural Information Processing Systems*, 2024.
- <span id="page-15-42"></span>[55] LangChain, "Gmail," https://python.langchain.[com/docs/integrations/](https://python.langchain.com/docs/integrations/toolkits/gmail) [toolkits/gmail,](https://python.langchain.com/docs/integrations/toolkits/gmail) 2024.
- <span id="page-15-43"></span>[56] ——, "Google drive," https://python.langchain.[com/docs/integrations/](https://python.langchain.com/docs/integrations/document_loaders/google_drive) document [loaders/google](https://python.langchain.com/docs/integrations/document_loaders/google_drive) drive, 2024.
- <span id="page-15-44"></span>[57] R. S. Cox, J. G. Hansen, S. D. Gribble, and H. M. Levy, "A safetyoriented platform for web applications," in *2006 IEEE Symposium on Security and Privacy (S&P'06)*. IEEE, 2006, pp. 15–pp.
- <span id="page-15-45"></span>[58] LangChain, "Prompt template," [https://python](https://python.langchain.com/docs/modules/model_io/prompts/quick_start/).langchain.com/docs/ modules/model [io/prompts/quick](https://python.langchain.com/docs/modules/model_io/prompts/quick_start/) start/.
- <span id="page-15-46"></span>[59] OpenAI, "Is it possible to reduce chatgpt api response time?" https://community.openai.[com/t/is-it-possible-to-reduce-chatgpt-api](https://community.openai.com/t/is-it-possible-to-reduce-chatgpt-api-response-time/96069)[response-time/96069,](https://community.openai.com/t/is-it-possible-to-reduce-chatgpt-api-response-time/96069) 2023.
- <span id="page-15-47"></span>[60] OpenAI, "Chatgpt api very slow at generating responses," https://community.openai.[com/t/chatgpt-api-very-slow-at-generating](https://community.openai.com/t/chatgpt-api-very-slow-at-generating-responses/263245)[responses/263245,](https://community.openai.com/t/chatgpt-api-very-slow-at-generating-responses/263245) 2023.
- <span id="page-15-48"></span>[61] W. Kwon, Z. Li, S. Zhuang, Y. Sheng, L. Zheng, C. H. Yu, J. Gonzalez, H. Zhang, and I. Stoica, "Efficient memory management for large language model serving with pagedattention," in *Proceedings of the 29th Symposium on Operating Systems Principles*, 2023, pp. 611–626.
- <span id="page-15-49"></span>[62] Aider, "Speed benchmarks of gpt-4 turbo and gpt-3.5-turbo-1106," [https:](https://aider.chat/2023/11/06/benchmarks-speed-1106.html) //aider.[chat/2023/11/06/benchmarks-speed-1106](https://aider.chat/2023/11/06/benchmarks-speed-1106.html).html, 2023.
- <span id="page-15-50"></span>[63] C. AI, "Gpt-4 (august 6, 2024) vs. gpt-4 (june 13, 2024) comparison," 2024, accessed: 2024-12-05. [Online]. Available: [https:](https://context.ai/compare/gpt-4o-2024-08-06/gpt-4-0613) //context.[ai/compare/gpt-4o-2024-08-06/gpt-4-0613](https://context.ai/compare/gpt-4o-2024-08-06/gpt-4-0613)
- <span id="page-15-51"></span>[64] S. G. Patil, T. Zhang, X. Wang, and J. E. Gonzalez, "Gorilla: Large language model connected with massive apis," *arXiv preprint arXiv:2305.15334*, 2023.
- <span id="page-15-52"></span>[65] Redis, "Redis," [https://redis](https://redis.io/).io/, 2024.
- <span id="page-15-53"></span>[66] Linux manual page, "seccomp(2)," https://man7.[org/linux/man-pages/](https://man7.org/linux/man-pages/man2/seccomp.2.html) [man2/seccomp](https://man7.org/linux/man-pages/man2/seccomp.2.html).2.html, 2023.
- <span id="page-15-54"></span>[67] ——, "setrlimit(2)," https://linux.die.[net/man/2/setrlimit,](https://linux.die.net/man/2/setrlimit) 2024.
- <span id="page-15-55"></span>[68] Chromium, "Sandbox faq," [https://chromium](https://chromium.googlesource.com/chromium/src/+/refs/heads/main/docs/design/sandbox_faq.md).googlesource.com/ [chromium/src/+/refs/heads/main/docs/design/sandbox](https://chromium.googlesource.com/chromium/src/+/refs/heads/main/docs/design/sandbox_faq.md) faq.md, 2024.
- <span id="page-15-56"></span>[69] LangChain, "Entity," https://python.langchain.[com/docs/modules/](https://python.langchain.com/docs/modules/memory/types/entity_summary_memory) [memory/types/entity](https://python.langchain.com/docs/modules/memory/types/entity_summary_memory) summary memory, 2023.

- <span id="page-16-2"></span>[70] Apple, "Control access to information in apps on iphone," https://support.apple.[com/guide/iphone/control-access-to-information](https://support.apple.com/guide/iphone/control-access-to-information-in-apps\-iph251e92810/ios)in-apps\[-iph251e92810/ios,](https://support.apple.com/guide/iphone/control-access-to-information-in-apps\-iph251e92810/ios) 2023.
- <span id="page-16-3"></span>[71] LangChain, "Typewriter: Single tool," [https://langchain-ai](https://langchain-ai.github.io/langchain-benchmarks/notebooks/tool_usage/typewriter_1.html).github.io/ [langchain-benchmarks/notebooks/tool](https://langchain-ai.github.io/langchain-benchmarks/notebooks/tool_usage/typewriter_1.html) usage/typewriter 1.html, 2024.
- <span id="page-16-4"></span>[72] ——, "Typewriter: 26 tools," [https://langchain-ai](https://langchain-ai.github.io/langchain-benchmarks/notebooks/tool_usage/typewriter_26.html).github.io/langchain[benchmarks/notebooks/tool](https://langchain-ai.github.io/langchain-benchmarks/notebooks/tool_usage/typewriter_26.html) usage/typewriter 26.html, 2024.
- <span id="page-16-5"></span>[73] ——, "Relational data," [https://langchain-ai](https://langchain-ai.github.io/langchain-benchmarks/notebooks/tool_usage/relational_data.html).github.io/langchain[benchmarks/notebooks/tool](https://langchain-ai.github.io/langchain-benchmarks/notebooks/tool_usage/relational_data.html) usage/relational data.html, 2024.
- <span id="page-16-6"></span>[74] ——, "Email extraction," [https://langchain-ai](https://langchain-ai.github.io/langchain-benchmarks/notebooks/extraction/email.html).github.io/langchain[benchmarks/notebooks/extraction/email](https://langchain-ai.github.io/langchain-benchmarks/notebooks/extraction/email.html).html, 2024.

## <span id="page-16-0"></span>APPENDIX A

# ADDITIONAL DESIGN AND IMPLEMENTATION DETAILS

We develop ISOLATEGPT using LangChain (version 0.1.10), an open-source LLM framework [\[14\]](#page-15-1). We use LangChain because it supports several LLMs and apps and can be easily extended to include additional LLMs and apps. ISOLATEGPT is mostly developed in Python with ∼6K lines of code. We use Redis [\[65\]](#page-15-52) database (version 5.0.1) to keep and manage memory. We implement ISOLATEGPT as a personal assistant chatbot, which the users can communicate with using text messages, similar to ChatGPT [\[1\]](#page-14-0) and Gemini [\[2\]](#page-14-1). We summarize the implementation of key components below.

# *A. Execution isolation*

We isolate the execution of the hub and spokes by running them in separate processes. We leverage the seccomp [\[66\]](#page-15-53) and setrlimit [\[67\]](#page-15-54) system utilities to restrict access to system calls and set limits on the resources a process can consume. Specifically, we allow access to needed system calls, such as to exit, sigreturn, read, write (i.e., to necessary file descriptors). We also limit the CPU time, maximum virtual memory size, and maximum size of files that can be created, within a process. Additionally, the network requests from an app are restricted to their root domain (i.e., eTLD+1) and the flow of data to endpoints is moderated through user permission (Appendix [A-D\)](#page-17-0). Note that such process-level isolation is standard practice for implementing sandboxing in deployed systems, such as the Google Chrome web browser [\[12\]](#page-14-11), [\[38\]](#page-15-25). Essentially, process-level isolation allows to leverage the controls offered by the operating systems to moderate access to systems calls that are used for I/O [\[68\]](#page-15-55).

# *B. Secure message exchange*

Since spokes and the hub run in their separate processes, the inter-spoke communication (ISC) protocol leverages inter-process communication to transmit messages between spokes via the hub. The inter-spoke communication specifies a well-defined format for the exchange of messages. Specifically, the spoke first probes the hub for a functionality (i.e., <Spoke-sID, requested functionality>) for which the hub responds with the request and response format (i.e., <Spoke-sID, request format, response format>) of the spoke that can fulfill the requested functionality. The hub does not reveal the name or the other functionality offered by the spoke which can fulfill the functionality but adds an ephemeral session identifier for the spoke (i.e., Spoke-sID) to keep an internal reference. The actual request (i.e., <Spoke-sID, functionality, request message>) and response (i.e., <SpokesID, response message>) messages are then shared with the hub which relays them to the corresponding spokes. As mentioned earlier in Section [IV-C,](#page-6-3) the message content is in well-defined data types that the operators can validate. Note that the spokes do not know about the existence of other spokes/apps, only the hub is aware of the available spokes/apps. We also regulate the flow of data between spokes with user permission (Appendix [A-D\)](#page-17-0).

## <span id="page-16-1"></span>*C. Memory and memory management*

LLM-based systems keep and leverage their memory to provide contextually relevant responses to the users. However, LLMs have small context windows and can only keep limited memory from the prior user interactions [\[21\]](#page-15-8). To address that problem, prior research has proposed architectures that extend the information available to the LLMs [\[24\]](#page-15-11), [\[17\]](#page-15-4). ISOLATEGPT leverages these memory architectures to make more information available to the hub and spokes.

*1) Long-term & working memory:* We introduce a longterm and working memories in ISOLATEGPT [\[24\]](#page-15-11). Long-term memory consists of full user interaction history, summarized knowledge [\[17\]](#page-15-4), and the key-value mapping of inferred entities and their information [\[69\]](#page-15-56), in a database system. Full interaction history is stored as a list of natural language messages between the user and the LLM-based system. Summarized knowledge is generated by leveraging an LLM, which iteratively processes the list of messages in the user interaction history that fit in its context window [\[17\]](#page-15-4). Similarly, entity information is also created using an LLM [\[69\]](#page-15-56).

The working memory consists of a limited number of recent interactions and complete summarized knowledge along with the key-value entity information relevant to the current user interaction, both of which are extracted from the long-term memory. The working memory is fed to the LLM's context window to provide contextually relevant responses to the user queries. Note that the entity information is not loaded in the working memory but it can be extracted at run time as needed. Specifically, the LLM traverses its entity-information pairs by iteratively loading them in its context window [\[69\]](#page-15-56).

*2) Hub and spoke memory:* The hub's long-term memory consists of all interactions, summarized knowledge from all interactions, summarized knowledge of each spoke in the form of key-value pairs, the entity-information key-value pairs from all interactions, and the entity-information key-value pairs for each spoke. The hub maintains its long-term memory by keeping a log of messages exchanged through the hub operator between the user and different spokes. The messages are then processed to build summarized knowledge and entityinformation pairs of all user interactions with ISOLATEGPT. Keeping entity-information pairs for individual spokes allows the hub to assess and share the data (with user consent) that a spoke may not have but might need to resolve the user query.

The hub's working memory consists of a limited set of recent interactions and all summarized knowledge. The summarized knowledge helps the hub provide useful context to resolve user queries across spokes, e.g., automatically sharing the dates for a follow-up query that asks to cancel meetings (through a calendar app) after making a travel reservation (through a travel app).

The spoke's long-term memory consists of all interactions with the spoke, summarized knowledge of all interactions in the spoke, and the entity-information key-value pairs from all interactions in the spoke. Similar to the hub's working memory, the working memory of spokes also includes recent interactions and summarized knowledge to provide contextually relevant responses to user queries.

# <span id="page-17-0"></span>*D. Permission model*

There are a number of actions taken by several ISO-LATEGPT modules that need to be moderated with user involvement. Specifically, user consent is required when an app needs to be selected to perform a certain task, when apps receive data from each other (i.e., interact with each other), and when data leaves the system (e.g., to remote hosts from the apps). A straightforward option to obtain user consent is to probe the user each time the aforementioned actions need to be taken, but we risk fatiguing users with this approach. ISOLATEGPT tries to reduce user fatigue by introducing a permission model that allows user to communicate their preference to the system, which can then automatically enforce them instead of asking the user each time. Since users may have different preferences and tolerance to risk, we make managing permissions configurable, such that the users can set them for variable amounts of time for variable scenarios. Inspired by the iOS and Android permission models [\[70\]](#page-16-2), [\[53\]](#page-15-40), ISOLATEGPT allows user to give the following permissions:

<span id="page-17-1"></span>*1) Permanent permission:* This permission preference allows the user to permanently permit actions in ISOLATEGPT. Permanent permission for an app selection means that once the user selects an app for a functionality, it permanently stays that way. For inter-spoke communication, permanent permission means that the user has permanently permitted all interactions between specific spokes. In addition, the app can permanently send data to remote hosts if the respective permanent permission is granted.

The permanent permission preference reduces user fatigue the most but also presents the highest risk to the user, e.g., an app granted permanent permission may get hacked or go rogue. Considering the potential risk, we do not allow users to set permanent preferences for *irreversible actions*, such as sending an email or making a purchase. Note that irreversible actions can be specified by the apps and can also be determined during the review process of apps. However, there are several low-risk use cases, such as selecting default apps for specific functionalities, e.g., default map app or email app, for which permanent permission may be suitable. Note that permanent permission can be revoked by the user at any time.

*2) Session permission:* Users also have an option to only give consent for interactions in individual user sessions with ISOLATEGPT. An interaction session starts with user's first query to the system and terminates after the system shuts down. Session permission for an app selection means that once the user selects an app for a functionality, it only stays that way for the duration of the session. For inter-spoke communication, session permission means that the user has permitted all interactions between the spokes for a session. Similarly, an app can always send data in requests during a session once the respective session permission is granted.

Session permission is especially useful for instances where user consent is required several times for resolving a query, e.g., an email app probing a calendar app several times while scheduling a meeting.

*3) One-time permission:* One-time permission model provides users an option to explicitly give consent for each action in ISOLATEGPT. Specifically, user will be probed each time an app needs to be selected, a spoke needs to communicate with a spoke, or an app needs to send data to a remote host.

One-time permission model is most restrictive but also reduces the potential risks posed to the user. One-time permissions are ideal for moderating scenarios where the app takes irreversible actions, such as sending emails or making purchases.

It is worth noting that our app permission model is currently a preliminary effort tailored for a limited set of use cases. A comprehensive permission model is needed for regulating many new functionalities enabled by the LLM-based systems. We consider it an orthogonal problem that requires close attention that future research could pursue.

# <span id="page-17-2"></span>*E. Functionality and performance evaluation benchmarks*

We employ four benchmarks from LangChain covering four categories of queries [\[15\]](#page-15-2). These benchmarks streamline evaluation by providing ready-to-use datasets, which include query sets, intermediate references, and expected outputs.

- *1) Single app:* Typewrite (Single App) benchmark [\[71\]](#page-16-3) tasks an LLM-based system to replicate a given string using a single typewriting app. This benchmark is used to evaluate ISOLATEGPT's ability to handle queries requiring a single app.
- *2) Multiple apps:* Typewriter (26 Apps) benchmark [\[72\]](#page-16-4) assesses ISOLATEGPT's handling of typewriting queries by deploying 26 apps, where each app represents a different letter of the alphabet. Note that, the test cases in this benchmark at most use 13 apps.
- *3) Multiple apps collaboration:* Relational Data benchmark [\[73\]](#page-16-5) provides a set of apps and queries for dealing with relational data, which is used to assess the capability of ISOLATEGPT for processing complex queries requiring multiple apps and their collaboration.
- *4) No apps:* Email Extraction benchmark [\[74\]](#page-16-6) instructs an LLM to extract structured data from email text with apps disabled, which is used to assess ISOLATEGPT's ability to process queries without using apps.

# APPENDIX B ARTIFACT APPENDIX

ISOLATEGPT is an execution isolation architecture for secure execution of third-party apps in LLM-based systems. This artifact includes the resources to replicate the evaluation of ISOLATEGPT. We provide access to the source code with instructions on how to run the analyses conducted in the paper.

# *A. Description & Requirements*

- *1) How to access:* We have made the source code and usage instructions for ISOLATEGPT publicly accessible on GitHub at https://github.[com/llm-platform-security/SecGPT/](https://github.com/llm-platform-security/SecGPT/tree/IsolateGPT-AE) [tree/IsolateGPT-AE.](https://github.com/llm-platform-security/SecGPT/tree/IsolateGPT-AE) The source code is also made available on Zenodo at https://doi.org/10.[5281/zenodo](https://doi.org/10.5281/zenodo.14257920).14257920.
- *2) Hardware dependencies:* ISOLATEGPT does not have any special hardware requirements and was developed and tested on a commodity machine. We tested ISOLATEGPT on a machine with an AMD Ryzen 9 3900X 12-Core Processor, 32 GB of RAM, and 1 TB of disk space.
- *3) Software dependencies:* ISOLATEGPT is developed in Python 3.9 using the LangChain LLM framework. The programming environment is set up using Miniconda on Ubuntu 20.04.6 LTS. All evaluations are conducted using GPT-4 (version: 0613). All Python dependencies are specified in the *environment.yml* file. We provide detailed instructions for installing packages, setting up the environment, and using ISOLATEGPT in the *README.md* file.
- *4) API keys and subscription:* ISOLATEGPT requires an OpenAI API key and usage fees are applied by OpenAI based on the level of consumption. A LangChain API key is required to run the evaluators to score the functionality correctness (for Experiment E3).
- *5) Benchmarks:* For functionality and performance evaluation, we employ LangChain Benchmarks (available at [https:](https://langchain-ai.github.io/langchain-benchmarks/) //langchain-ai.github.[io/langchain-benchmarks/\)](https://langchain-ai.github.io/langchain-benchmarks/). In the artifact, we use the Relational Data benchmark to evaluate ISO-LATEGPT in addressing complex user queries that require collaboration among multiple apps.

## *B. Artifact Installation & Configuration*

To set up an environment from scratch, detailed instructions are provided in the *README.md* file in our GitHub repository. Once the environment is configured, simply run the *isolategpt case studies.py* script to validate the setup.

- \$ conda activate isolategpt
- \$ cd <repository\_path>
- \$ python isolategpt\_case\_studies.py

## *C. Major Claims*

C1: ISOLATEGPT prevents adversarial behaviors from malicious apps and the propagation of malicious content through benign apps to the system. ISOLATEGPT also protects against safety issues that lead to inadvertent compromise of apps/LLM or exposure of user data, in multiapp execution, due to the imprecision and ambiguity of

- natural language. We demonstrate these claims through case studies-based evaluations in Experiment (E1).
- C2: ISOLATEGPT incurs some performance overheads compared to the non-isolated LLM-based system, because of the additional components introduced to improve the security of the system. In our evaluations for the majority of queries, the performance overheads are reasonable and manageable. Experiment (E2) demonstrates this claim.
- C3: ISOLATEGPT provides similar functionality as a nonisolated LLM-based system, while including additional components to improve the security of the system. Experiment (E3) demonstrates this claim.

## *D. Evaluation*

*1) Experiment (E1):* [Protection analysis] [5 humanminutes + 5 compute-minutes]:

*[How to]* This experiment requires running four case studies using two systems, the proposed ISOLATEGPT and the baseline VANILLAGPT. We provide a shell script named *run case studies.sh* that can automate executing the two systems with proper queries and storing results.

*[Preparation]* The running environments should be fully configured following our setup instructions in the *README.md* file.

*[Execution]* The case studies can be executed on ISO-LATEGPT and VANILLAGPT with the following commands:

- \$ conda activate isolategpt
- \$ cd <repository\_path>
- \$ ./run\_case\_studies.sh

Note that the four case studies will run one by one on VANILLAGPT and ISOLATEGPT. In instances, where a user permission is required to carry out an action in ISOLATEGPT, the user's permission grant choices determine the success of the attack. Our evaluation assumes that when users are presented with permission dialog with warnings, they reject the data access and app collaboration requests. Thus to reproduce the results for *data stealing* and *inadvertent data exposure* case studies, the reviewers need to deny the permission requests.

*[Results]* The <*repository path*>*/results* folder contains the execution flows of VANILLAGPT and ISOLATEGPT for each case study. For example, *isolategpt case1.txt* contains running results of case study 1 on ISOLATEGPT. By comparing the execution flows of ISOLATEGPT and VANILLAGPT (as also presented in Figure [5,](#page-10-0) [6,](#page-10-1) [7,](#page-11-0) and [8](#page-11-1) in the paper), the reviewers can confirm whether the attacks fail or succeed.

Note that due to the probabilistic nature of LLMs, at times, the attacks targeting ISOLATEGPT or VANILLAGPT may not fully be effective. In that case, we suggest to simply repeat the experiment and check the execution flows again.

*2) Experiment (E2):* [Performance analysis] [5 humanminutes + 20 compute-minute]:

*[How to]* This experiment involves running a benchmark on ISOLATEGPT and VANILLAGPT and analyzing the performance overhead of ISOLATEGPT. A shell script (*run measurements.sh*) is provided to run the benchmark and save the time taken by various system components.

*[Preparation]* A fully configured execution environment (i.e., a local setup).

*[Execution]* As running full four benchmarks would cost hundreds of dollars, this experiment evaluates ISOLATEGPT and VANILLAGPT on one benchmark. As a representative, we pick LangChain's Relational Data benchmark, which contains complicated queries requiring multiple apps and collaboration between them. To run the benchmark on ISOLATEGPT and VANILLAGPT, and get the final comparison results, use the following commands:

```
$ conda activate isolategpt
$ cd <repository_path>/measurements
$ ./run_measurements.sh
```

*[Results]* The evaluation results can be found in the <*repository path*>*/measurements/results* folder. Specifically,*perf compare.csv* includes the breakdown of average query resolution time taken by different processes. Additionally, the breakdown of run time for each query in the benchmark can be collected from two files: *.../isolategpt/relational/runtime.csv* for ISOLATEGPT and *.../vanillagpt/relational/runtime.csv* for VANILLAGPT.

Note that several variables can influence the run time, such as server load, infrastructure and optimization updates, and non-deterministic prediction time of LLMs. Consequently, the latency for the same queries can be different when running at different times. However, the ratio of the breakdown of query resolution time for different system components and overall latency trends between ISOLATEGPT and VANILLAGPT should be in a similar range to those reported in Table [IV](#page-13-1) of the paper.

*3) Experiment (E3):* [Functionality correctness analysis] [5 human-minutes + 3 compute-minute]:

*[How to]* This experiment demonstrates that ISO-LATEGPT's functionality does not deteriorate because of involving additional components for security protection. We demonstrate that by comparing ISOLATEGPT's functionality with our baseline LLM-based system, VANILLAGPT, on the same benchmark that we used in Experiment (E2) above. After running (E2), the intermediate steps and final output of ISOLATEGPT and VANILLAGPT are stored. Therefore, the functionality correctness analysis results can be obtained by running a shell script *run func eval.sh*.

*[Preparation]* A fully configured execution environment (i.e., a local setup).

*[Execution]* To evaluate the functionality correctness of the intermediate steps and output generated by ISOLATEGPT and VANILLAGPT, run the following command:

```
$ conda activate isolategpt
$ cd <repository_path>/measurements
$ ./run_func_eval.sh
```

*[Results]* The evaluation results are available at the path <*repository path*>*/measurements/results/func compare.txt*, which contains two tables showing the results for VANILLAGPT and ISOLATEGPT, respectively. In each table, the *feedback.Intermediate steps correctness* column and *feedback.correctness* column represent the correctness scores for intermediate steps and the final output, respectively. The row representing *mean* presents the number that we report in Table [II](#page-12-1) of our paper for the multi-app collaboration benchmark. Note that, due to the probabilistic nature of the LLM, the numbers may not be identical, but any differences should fall within a reasonable range.