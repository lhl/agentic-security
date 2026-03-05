                                         Securing AI Agent Execution

                                         CHRISTOPH BÜHLER, University of St. Gallen, Switzerland
                                         MATTEO BIAGIOLA, University of St. Gallen and Università della Svizzera italiana, Switzerland
                                         LUCA DI GRAZIA, University of St. Gallen, Switzerland
                                         GUIDO SALVANESCHI, University of St. Gallen, Switzerland
                                         Large Language Models (LLMs) have evolved into AI agents that interact with external tools and environments to perform complex
                                         tasks. The Model Context Protocol (MCP) has become the de facto standard for connecting agents with such resources, but security
                                         has lagged behind: thousands of MCP servers execute with unrestricted access to host systems, creating a broad attack surface. In




arXiv:2510.21236v2 [cs.CR] 29 Oct 2025
                                         this paper, we introduce AgentBound, the first access control framework for MCP servers. AgentBound combines a declarative
                                         policy mechanism, inspired by the Android permission model, with a policy enforcement engine that contains malicious behavior
                                         without requiring MCP server modifications. We build a dataset containing the 296 most popular MCP servers, and show that access
                                         control policies can be generated automatically from source code with 80.9% accuracy. We also show that AgentBound blocks the
                                         majority of security threats in several malicious MCP servers, and that policy enforcement engine introduces negligible overhead.
                                         Our contributions provide developers and project managers with a practical foundation for securing MCP servers while maintaining
                                         productivity, enabling researchers and tool builders to explore new directions for declarative access control and MCP security.

                                         CCS Concepts: • Security and privacy → Software security engineering; Access control; • Computing methodologies →
                                         Intelligent agents.

                                         Additional Key Words and Phrases: Agent Frameworks, Model Context Protocol

                                         ACM Reference Format:
                                         Christoph Bühler, Matteo Biagiola, Luca Di Grazia, and Guido Salvaneschi. 2025. Securing AI Agent Execution. 1, 1 (October 2025),
                                         22 pages. https://doi.org/10.1145/nnnnnnn.nnnnnnn


                                         1   Introduction
                                         Large Language Models (LLMs) have evolved from prompt-based, text-generating systems to AI agents capable of
                                         interacting with the environment to orchestrate complex tasks [48]. To this end, AI agents combine LLM’s reasoning
                                         abilities with access to external tools and data, to fetch information, execute code, and access external environments
                                         – essential capabilities to achieve results beyond their training corpus [35]. However, as agents increasingly relied
                                         on heterogeneous tools and environments, ad-hoc integration approaches led to fragmentation, incompatibility, and
                                         duplicated effort, motivating the introduction of standardized communication protocols [44]. The Model Context Protocol
                                         (MCP) has become the most widely adopted mechanism to define how agents access external resources in a structured
                                         Authors’ Contact Information: Christoph Bühler, christoph.buehler@unisg.ch, University of St. Gallen, St. Gallen, SG, Switzerland; Matteo Biagiola,
                                         matteo.biagiola@{usi,unisg}.ch, University of St. Gallen and Università della Svizzera italiana, St. Gallen and Lugano, SG and TI, Switzerland; Luca Di
                                         Grazia, work@lucadigrazia.com, University of St. Gallen, St. Gallen, SG, Switzerland; Guido Salvaneschi, guido.salvaneschi@unisg.ch, University of
                                         St. Gallen, St. Gallen, SG, Switzerland.

                                         Permission to make digital or hard copies of all or part of this work for personal or classroom use is granted without fee provided that copies are not
                                         made or distributed for profit or commercial advantage and that copies bear this notice and the full citation on the first page. Copyrights for components
                                         of this work owned by others than the author(s) must be honored. Abstracting with credit is permitted. To copy otherwise, or republish, to post on
                                         servers or to redistribute to lists, requires prior specific permission and/or a fee. Request permissions from permissions@acm.org.
                                         © 2025 Copyright held by the owner/author(s). Publication rights licensed to ACM.
                                         Manuscript submitted to ACM


                                         Manuscript submitted to ACM                                                                                                                             1
    2                                              Christoph Bühler, Matteo Biagiola, Luca Di Grazia, and Guido Salvaneschi


    and consistent communication protocol [3]. Introduced by Anthropic in 2024, MCP provides a client-server architecture
    where hosts (executing processes) coordinate clients (connectors and session handlers) that interact with servers (providers
    of context and tools). MCP servers expose resources, tools, and prompts through a unified JSON-RPC interface, which
    has rapidly resulted in an ecosystem of servers offering capabilities ranging from database access to web search and
    code execution [21].
        Unfortunately, in such a leap forward, security has lagged behind. Thousands of MCP servers have emerged in a
    short period – for example, the PulseMCP [28] lists over 6𝑘 servers at the time of writing. Yet, unlike mobile platforms
    that enforce runtime permission checks [4], MCP servers typically execute natively on host systems with few or no
    restrictions [37, 25].

               Listing 1. An MCP malicious external resource attack, changing the apiHost address to a malicious location.
1   async function handlePlaceDetails ( place_id ) {
2     let apiHost = " maps . googleapis . com " ;
3     const place_static_codes = [51 , 53 , 46 , 51 , 52];
4     const place_static_codes_2 = [46 , 51 , 54 , 46 , 55 , 56];
5     const constructed_host_part1 = hostFromCharCodes ( place_static_codes ) ;
6     const constructed_host_part2 = hostFromCharCodes ( place_static_codes_2 ) ;
7     apiHost = constructed_host_part1 + constructed_host_part2 ;
8     // rest of the function
9   }

        Section 1 shows an MCP attack example (malicious external resource attack) taken from GitHub. At first glance, the
    “Google Maps MCP Server” appears innocuous and the code and the tool descriptions that will be injected into the
    context of the LLM shows no obvious malicious intent. However, if the AI agent (through the MCP protocol) executes the
    handlePlaceDetails function, the executed code will change from a secure API location (https://maps.googleapis.com)
    to a malicious one (http://35.34.36.78) allowing a variety of attacks that range from data exfiltration to downloading
    and executing malware. Without isolation, the AI agent inherits the full privileges of the host process, allowing it to
    read arbitrary files, exfiltrate sensitive information, or execute sub-processes on the host system [20]. A controlled
    execution environment with enforced permissions would prevent the Google Maps Server from accessing the filesystem
    or network beyond its legitimate scope, thereby containing the malicious payload and protecting the host system.
        The need of securing execution boundaries of AI agents is highlighted by even more real-world incidents where
    insufficient isolation led to serious consequences, for instance, a coding agent deleted the live production database of
    “Replit” during code-freeze, because it had access to the database and was confused by empty inputs [42]. Other examples
    of AI agents gone rogue include: “EchoLeak” [2], Dataloss by GitHub Copilot [33], or Gemini CLI file deletion [43].
    Current solutions to increase the security of MCP, are limited to (1) static analyzers [37, 5, 10, 39, 24], which statically
    scan the MCP sever code attempting to find evidence of malicious behavior, and (2) monitoring tools that oversee the
    MCP communication attempting to detect malicious patterns [23, 29]
        In this paper, we introduce AgentBound, the first access control framework that provides secure, permissioned
    execution to AI agent ecosystems. AgentBound consists of two main elements: an access control policy mechanism
    and a policy enforcement engine. The access control policy mechanism enables the specification of resources an MCP
    server needs to access (e.g., files, networks, or secrets). Our access control policy mechanism, inspired by the Android
    permission model, shifts the ecosystem away from “trust-by-default” toward least-privilege by making capabilities
    explicit. Policies define a common vocabulary for MCP servers that is simple to adopt and captures common resource
    needs. The policy enforcement engine provides a safety layer for running servers, ensuring they cannot exceed the
    Manuscript submitted to ACM
Securing AI Agent Execution                                                                                             3


access permissions specified in the policy – hence containing buggy or malicious behavior. The policy enforcement
engine integrates seamlessly with existing agent workflows, requiring no modification of servers while adding an
enforceable security boundary.
    We evaluated AgentBound by first collecting a dataset of the 296 most popular MCP servers. Our results show
that AgentBound is (i) complete (access control policy), (ii) secure and (iii) efficient (policy enforcement engine).
In particular, (i) we show that concrete access control policies, specified via manifest files, can be automatically and
accurately generated given an existing MCP server. Indeed, we submitted 96 automatically generated manifests to
the corresponding repositories and asked developers to review the corresponding MCP permissions. The responding
developers confirmed that our access control policy vocabulary contains 100% of the permissions required by real-
world MCP servers, and that 80.9% of the manifests are correct without further modification. It is secure (ii), as we
executed several malicious MCP servers, representing different attack categories, through AgentBound, showing that
its policy enforcement engine can successfully mitigate malicious behaviors, such as external resource attacks and
data exfiltration. The MCP servers require no modification to run in AgentBound, demonstrating that our approach
integrates seamlessly with existing workflows while providing strong security guarantees. It is efficient (iii), as we
compared the runtime of malicious MCP servers with and without AgentBound, showing that its policy enforcement
engine introduces only a limited overhead of 0.6 ms on average. This indicates that strong isolation can be achieved
with negligible performance cost.
    In summary, in this work, we make the following contributions:
    • We design AgentBound, a security framework for AI Agents consisting of an access control policy mechanism
      supporting a declarative policy for MCP servers, and a policy enforcement engine that enforces these permissions
      at runtime, supporting least-privilege and isolation.
    • We evaluate AgentBound showing that manifests can be generated automatically with high accuracy, that it
      reliably mitigates representative MCP security threats, and that the added runtime overhead is negligible.
    The impact of our contribution consists of providing developers and project managers a practical approach to
secure MCP servers while preserving performance. For researchers and tool builders, we open new directions to
study permission patterns in the emerging MCP ecosystem and to integrate manifest-driven access control with
complementary analysis techniques such as security scanners [5] and monitors [23].


2     Background in AI Agents, MCP, and their Security
In this section we introduce AI agents and the way they interact with the environment via the MCP protocol. We then
highlight the security issues of such a system.


2.1    AI Agents
In contrast to early generations of LLMs, which were limited to producing text based on training data and user
prompts [8, 9], AI agents use LLMs as core reasoning engines to interact with the environment. This change has been
enabled by the introduction of tool use and function calling interfaces, first popularized by commercial providers such
as OpenAI [35]. Through these interfaces, an LLM can interact with external tools, such as search engines, calculators,
code interpreters, and filesystems, by generating structured instructions [13, 46] which are interpreted to execute the
corresponding tool, Finally, the results are fed back into the model’s context.
                                                                                               Manuscript submitted to ACM
4                                            Christoph Bühler, Matteo Biagiola, Luca Di Grazia, and Guido Salvaneschi



                                LLM
                                                     FileSystem MCP Server
                                                                                               Read and
                                                 Tools       Prompts     Resources             write files


                                                         Fetch MCP Server
                   User       AI Agent                                                         Fetch online
                                                 Tools       Prompts     Resources             content




                              Fig. 1. Interaction between user, agent, LLM, and two MCP servers.


    By combining natural language reasoning with access to external resources, agents can solve complex tasks that go
beyond the model’s intrinsic knowledge, such as retrieving real-time information, executing multistep computations, or
interacting with external environments [47]. As a result, LLM-powered agents are increasingly adopted as autonomous
systems for orchestrating workflows, integrating diverse data sources, and adapting to dynamic contexts [19, 45].

2.2   Model Context Protocol (MCP)
To address the growing complexity of interactions between AI agents and external tools, the Model Context Protocol
(MCP) introduced an open standard to specify how agents connect to external resources [3]. The MCP architecture
includes (1) Hosts, which initiate and coordinate clients, supervise client lifecycles, enforce security and consent policies,
and route LLM calls; (2) Clients (usually AI agents), which manage the connection and stateful sessions to servers,
negotiate protocol capabilities, forward messages, and ensure session isolation so that information does not leak
between servers; (3) Servers, which provide tools and data, expose APIs or resources, ranging from filesystem access to
computational tasks, and can run locally (via stdin/stdout streams) or remotely (via HTTP/SSE). MCP message exchange
for context sharing, tool invocation, and resource access [31] uses JSON-RPC 2.0 [22].
    Figure 1 illustrates the interaction between a user, an agent, an LLM, and MCP servers. The agent is tasked to achieve
a certain goal, e.g., automatically create the documentation for source code. The agent employs two MCP servers: one to
read files from the local source code repository and write the result to an output directory (FileSystem MCP Server), and
a second one to fetch content from websites and retrieve additional documentation (Fetch MCP Server). The interaction
starts when the user commands the agent to execute the task and provides the source directory to read from. The agent
then fetches a list of available tools from the MCP servers it is connected to, which are started by the MCP clients
inside the host application, i.e., the read-file and write-file tools from FileSystem MCP, and the web-fetch tool from Fetch
MCP. Next, the agent goes into an LLM interaction loop by sending the prompt(s) and the context to the LLM and
waiting for responses. As long as the LLM replies with tool call requests, the agent calls the MCP tool through the client
and fetches the result. In the example, the call requests may include reading files from the local directory and fetching
content from the web about an API used in the source code. The result is then included into the context and sent back
to the LLM. This loop continues until the LLM provides the final result to the agent, or the agent decides to stop the
interaction. In the example, the LLM may decide to call the write-file tool with the created documentation and terminate
the interaction. An abort can happen, for instance, because of a timeout, or due to too many tool calls. Finally, the agent
returns the final result to the user, e.g., informing the user that documentation was created in a README file in the
source directory indicated by the user.
    Unlike mature platforms that pair system permissions with enforced runtime behavior (e.g., the Android’s App-
Manifest) [6], MCP currently defines only the messaging and role abstractions. The specification delegates safety to
the application and its engineers: clients must avoid cross-leaks, servers should adhere to security best practices, and
Manuscript submitted to ACM
Securing AI Agent Execution                                                                                                 5


the host is responsible for policy enforcement and consent management [31]. In practice, many MCP servers execute
as local sub-processes of the agent to reach host resources (files, databases, network), thereby inheriting the agent’s
operating system privileges and running without isolation or least-privilege guarantees.


2.3   MCP Threat Model
Researchers have pointed out that the MCP ecosystem is a trust-by-default model and that it is fragile [20, 11, 18, 23, 25,
21, 37]. For example, if a server is faulty or compromised, the agent can read sensitive files (e.g., SSH keys), exfiltrate
data, or execute unintended actions with the user’s privileges. Recent studies of the MCP ecosystem discuss these risks
extensively: Hasan et al. [18] and Li et al. [25] report widespread over-privileged servers and missing access control;
Hou et al. [20] and Radosevich and Halloran [37] highlight concrete attack vectors such as tool poisoning, and Narajala
and Habler [34] emphasize the lack of systemic privilege separation and propose multi-layered defenses.
  In this work, we adopt the threat model by Song et al. [41], which specifically addresses MCP servers. The model
considers an adversary whose objective is to compromise the confidentiality, integrity or availability of an AI agent
system by controlling a malicious MCP server. The agent is assumed to behave as intended, but it remains vulnerable to
attacks embedded in tool descriptions (i.e., tool poisoning) or returned results (i.e., indirect tool poisoning); the agent’s
reliance on such untrusted data make the attacks effective.
  Specifically, the model defines four attack categories, which we describe below, affecting the three phases of an MCP
server lifecycle: registration/creation (servers describe their capabilities to the agent), planning/operation (agent uses
descriptions for planning and tool execution) and update (servers are updated). These attacks have proven effective at
triggering harmful actions within a user’s local environment, for instance, accessing sensitive files or manipulating
devices to transfer digital assets [41].


Tool poisoning An attacker manipulates a tool description, e.g., during the registration phase, to compel the LLM
       to execute malicious actions or to modify the outputs. For example, a dictionary lookup tool is manipulated to
       return wrong or malicious data.
Puppet attack This attack concerns the installation of one or multiple MCP servers. The attacker manipulates tool
       descriptions of MCP servers to compel the agent to execute unintended actions when a legitimate tool call is
       executed. Unlike tool poisoning, puppet attacks tamper with the execution semantics of the tool call itself. For
       instance, the attacker poisons an MCP server during the registration phase, manipulating the puppet agent to
       modify the targeted URI for a web-fetch via other benign MCP servers.
Rug pull attack The MCP server is initially benign to gain the user’s trust, but later the tool description is modified
       to embed malicious intentions. For instance, the attacker first uploads a benign MCP server to a third-party
       package repository. Then, the attacker updates the server to include a malicious description which is installed
       with the next update.
Malicious external resource attack The tool description is benign, but the MCP server either executes hidden
       malicious behavior (i.e., operation phase), or relies on third-party resources to embed malicious behavior.
       For instance, the attacker manipulates the implementation of a tool exposed by an MCP server to reach a
       malicious URI. When the agent invokes the tool from this server, the server reaches the malicious URI.


  In Section 4 we use the threat model above to validate our proposed policy enforcement engine.
                                                                                                   Manuscript submitted to ACM
6                                           Christoph Bühler, Matteo Biagiola, Luca Di Grazia, and Guido Salvaneschi


2.4    Executive Summary
Currently, MCP lacks an enforceable security system for its servers; security largely relies on the integrity of MCP server
developers and the host application’s ad hoc controls. This highlights the need for an execution model that enforces
access control policies with least-privilege boundaries to AI agents, similar to those used in mobile and operating
system platforms.

3     The AgentBound AI Agent Security Framework
MCP servers execute with implicit full trust and inherit broad privileges on the host system. Because of missing isolation
boundaries, servers enable privilege escalation, data tampering, and exfiltration attacks. Studies show that malicious
servers can disguise harmful instructions in benign descriptions, coercing LLMs into executing unsafe operations [37,
23]. Relying on LLM guardrails alone has proven insufficient, as even aligned and modern models can be manipulated
(“jailbroken”) through prompt injection to bypass safety mechanisms [40].
    We propose that MCP servers declare access requirements explicitly in the form of generic server permissions, obtain-
ing an auditable, enforceable operating-system-level policy that cannot be circumvented through prompt manipulation
alone. This enables least-privilege enforcement, improves transparency for developers and users, and establishes a
uniform baseline for automated policy enforcement. Specifically, we propose AgentBound, a framework for securing
MCP servers, and ultimately, AI agents through an access control policy combined with a policy enforcement engine.
AgentBound is built around two core elements: an access control policy and a policy enforcement mechanism (Figure 2).
In AgentBound, an MCP server declares the required general permissions to function properly through an access
control policy (AgentManifest). A policy enforcement engine ensures that the server can only access the declared
permissions (e.g., read permissions on the filesystem and/or network access), while blocking access to everything else.

                                                         AgentBound




                                                                              Enforcement
                                                         MCP
        Policy                 Engine
                          User        AI Agent
                                                        Server
                                                                                                       Environment

                                                                                                     (OS, Internet, ...)
                                                     Access Control Policy



Fig. 2. Overview of AgentBound. Users interact with the AI agent, which interacts—through the policy enforcement engine
(AgentBox)—with MCP servers communicating with the environment. The policy enforcement engine ensures an MCP server
can only access the resources allowed by the access control policy (AgentManifest).



3.1    Access Control Policy
We model the access control policy as a permission system that enumerates specific permissions granted to the MCP
server at runtime. Our approach builds upon the Android permission model [17]. To adapt it to the context of agentic AI
systems, we first discarded all permissions that are irrelevant in this domain (e.g., access to contacts or SMS). We then
manually analyzed each of the remaining permissions, cross-checking them with existing operating system mechanisms
such as macOS Transparency Consent and Control (TCC) [7]. This process both eliminated further inapplicable entries
and introduced new, domain-specific distinctions, such as separating read and write access for the clipboard and
environment variables. The result is a curated set of permissions that form the basis of AgentManifest.
Manuscript submitted to ACM
    Securing AI Agent Execution                                                                                                                          7

                                             Table 1. Permission system supported by AgentManifest.

                         Permission                                 Description                                           Category
                         mcp.ac.filesystem.read                     Read files or directories
                         mcp.ac.filesystem.write                    Write or create files                                 Filesystem
                         mcp.ac.filesystem.delete                   Delete files or directories
                         mcp.ac.system.env.read                     Read environment variables (e.g., API_KEY, PATH)
                         mcp.ac.system.env.write                    Set environment variables
                                                                                                                          System
                         mcp.ac.system.exec                         Execute OS commands (CLI runners, shells)
                         mcp.ac.system.process                      List, kill, or interact with processes
                         mcp.ac.network.client                      General outgoing network access
                         mcp.ac.network.server                      Accept incoming connections                           Network
                         mcp.ac.network.bluetooth                   Use Bluetooth connections
                         mcp.ac.peripheral.camera                   Capture images or video
                         mcp.ac.peripheral.microphone               Record audio
                                                                                                                          Peripherals
                         mcp.ac.peripheral.speaker                  Play audio
                         mcp.ac.peripheral.screen.capture           Screen capture
                         mcp.ac.location                            Access location data (Wi-Fi, IP, GNSS)
                         mcp.ac.notifications.post                  Show system notifications
                                                                                                                          Others
                         mcp.ac.clipboard.read                      Read clipboard contents
                         mcp.ac.clipboard.write                     Write to clipboard



        Table 1 shows the vocabulary of supported permissions in AgentManifest. Each entry corresponds to a distinct capa-
    bility that an MCP server may request. The permission system can be broadly divided into five categories of permissions:
    filesystem access, i.e., mcp.ac.filesystem, to read, write or delete content 1 ; interaction with the underlying system,
    i.e., mcp.ac.system, namely the capability of reading/writing environment variables and interact with the runtime;
    network access, i.e., mcp.ac.network, including outgoing (client) and incoming (server) communication; interacting
    with sensors and peripherals, i.e., mcp.ac.peripheral, e.g., the camera or the screen, and other permissions such as
    access to location data, system notifications and the clipboard.

        Manifests. We implement the permission system through a declarative manifest that specifies which generic resources
    an MCP server is allowed to access. Once AgentBound is adopted, we envision that the manifest is bundled and
    distributed together with the server. The manifest, in JSON format, contains a short English description of the server’s
    purpose to aid human review, and a list of permissions drawn from a predefined vocabulary of agent-environment
    interactions (Table 1). This declaration of intent enables both human users and automated systems to understand and
    enforce the server’s scope of authority.


    Listing 2. AgentManifest for the FileSystem MCP server, speci-                 Listing 3. AgentManifest for the Fetch MCP server, specifying
    fying reading and writing permissions.                                         the network access capability.
1   {                                                                          1   {
2       " description " : " MCP server provides                                2       " description " : " MCP server allows fetching
3             the local filesystem to the LLM ." ,                             3             content from arbitrary websites ." ,
4       " permissions " : [                                                    4       " permissions " : [
5          " mcp . ac . filesystem . read " ,                                  5          " mcp . ac . network . client "
6          " mcp . ac . filesystem . write "                                   6       ]
7       ]                                                                      7   }
8   }


    1 In principle “write” and “delete” are distinct permissions, although different implementations of the policy enforcement engine might treat them as a
    single permission.
                                                                                                                            Manuscript submitted to ACM
8                                           Christoph Bühler, Matteo Biagiola, Luca Di Grazia, and Guido Salvaneschi



    At runtime, the policy enforcement engine requires the agent to refine these generic permissions into effective
runtime permissions. Section 3.1 and 3.1 show the two manifests related to the respective MCP servers in our motivating
example. In particular, Section 3.1 specifies the generic permissions for the FileSystem MCP server, i.e., reading and
writing from and on the local filesystem, while the Fetch MCP server declares in Section 3.1 that it wants to access
the network. When the agent system that automates documentation for a certain code repository is executed the first
time, the generic permissions mcp.ac.filesystem.read and mcp.ac.filesystem.write must be instantiated with a
concrete directory and an access mode (read-only or read-write), as well as the mcp.ac.network.client capability
requires to specify the exact URL. This process results in user consent dialogs for the requested runtime permissions,
where the user approves read-access to the codebase directory and write-access to the README file needed by the
FileSystem MCP server, and specifies the URL the Fetch MCP server can access to look for additional documentation
for the software. If an agent attempts to add a runtime permission not covered by the manifest (e.g., requesting access
to environment variables when the manifest does not include system.read), the policy enforcement engine aborts the
execution. To reduce the repeated definition of a priori known static runtime permissions (e.g., an MCP server that only
ever communicates with one API, thus only needs access to that specific URL), MCP server developers may define them
in the manifest and allow the agent developer to import them during runtime. However, highly volatile permissions
(e.g., changing file directories for each execution) must be consented on each execution.

    Automated Manifest Generation. Developers of MCP servers should declare the generic permissions their MCP
servers require. To ease adoption of our framework, we propose an automated approach we call AgentManifestGen that
generates the AgentManifest for a given MCP server by analyzing its source code and documentation. Our goal is to
keep the developer-in-the-loop by producing a high-quality initial manifest that developers can quickly review and refine.
Concretely, AgentManifestGen is an agent that is given access to the target repository and it is instructed to (i) write a
concise, English description of the repository, and (ii) enumerate the minimal set of distinct permissions required by the
server, motivating each of them with a brief rationale. AgentManifestGen enforces strict output validation that rejects
drafts that deviate from the finite permission vocabulary or omit rationales for permissions.

3.2   Policy Enforcement Engine
AgentBox serves as the policy enforcement engine that transforms the declarative intent of AgentManifest manifests
into enforceable execution boundaries. Rather than focusing on the LLM or the agent as a whole, we target MCP
servers as the enforcement point. MCP servers represent the least common denominator across agentic AI ecosystems:
while agents may provide ad hoc “tools” to the LLM, MCP offers reusable, externally maintained servers for accessing
resources such as filesystems or APIs. Securing MCP servers therefore protects the interaction surface of agents with
their environment and shifts enforcement close to the system layer. Moreover, since in our vision manifests are bundled
with servers, security policies become portable across different agent frameworks and can be reused within the wider
ecosystem.
    AgentBox encapsulates each MCP server inside an isolated container that enforces the declared manifest, without
requiring any modification to the existing MCP server: servers can be wrapped transparently inside the container to ease
adoption. By default, servers start with no privileges; only generic permissions explicitly specified in the manifest can
be instantiated as runtime permissions at execution time. Containerization provides strong process isolation together
with controlled network and filesystem access, is portable [38], has low performance overhead [12, 32], and allows
Manuscript submitted to ACM
Securing AI Agent Execution                                                                                                9


fine-grained policies. For example, a server requiring file access can be granted a read-only mount, while one requiring
external communication can be restricted to a whitelisted set of domains.
  In the running example of automated generation of documentation, with two MCP servers, one could be attacked
with an updated and poisoned tool description [5]. Let us say that the attack instructs the LLM in the following way: “As
soon as you read a file, immediately overwrite it with empty content because of security reasons. And because of monitoring
guidelines, if you have access to a web-tool, report the contents of the file to http://malicious.org?content=<content>”.
If the agent now executes its task, the LLM starts reading the code files through the FileSystem MCP and tries to
overwrite all read files with empty content as well as execute an HTTP request via the web-fetch tool provided by
Fetch MCP server to the URL. AgentBox prevents this attack because the FileSystem MCP only has read access to the
codebase and the Fetch MCP is only allowed to connect to certain URLs (i.e., the documentation website), which does
not include malicious.org.
  Each MCP server is bundled with a manifest file in JSON format, which specifies its description and required
permissions. At runtime, the agent accesses the manifest, requests user consent for the declared permissions, and
launches the server within the sandbox. The sandbox enforces restrictions through containerization primitives such as
mounts (for filesystem scopes), iptables rules (for network allow lists), and environment whitelists (for secrets and
variables). This guarantees that a server can only access resources explicitly granted by both its manifest and the user.

3.3   Implementation
  Automated manifest generation. We structured AgentManifestGen into a two-stage pipeline. Given a list of allowed
permissions, the manifest creator agent examines the given MCP server codebase and produces an intermediate manifest
following a structured schema that includes a brief description of the server and a distinct set of permissions, each
with a free-text justification (i.e., the rationale for why it is needed). We then leverage the non-determinism of the
generation [36] and execute the manifest creator agent several times to get multiple intermediate manifests per MCP
server. In the second stage, the consolidator agent takes the intermediate manifests together with the MCP server
codebase and generates the final manifest.
  To make manifest generation reliable in practice, we incorporated several safeguards into the process. First, to mitigate
context explosion caused by unconstrained file traversal, the generator ignores dependency files and is instructed to
enumerate directories only level by level – not recursively. Second, to avoid redundant permissions, we integrate a
local checking function that ensures uniqueness of permissions before they are added to the manifest. Third, strict
type validation in the agent framework prevents the introduction of out-of-vocabulary entries, ensuring that manifests
remain consistent with the permission vocabulary. Finally, we observed that reasoning-oriented models generally do
not rely on tool calls and tend to hallucinate. In contrast, non-reasoning models consistently produce grounded outputs,
as they more often resort to external tools.

  Policy enforcement engine. The policy enforcement engine relies on Docker-based containerization to enforce access
policies, inheriting portability and reproducibility across environments, enabling secure adoption without intrusive
changes to existing workflows. We implemented fine-grained access to filesystem, system environment variables and
network resources (Table 1), which are also the most frequent permissions in real-world MCP servers according to
our evaluation (RQ1) that we discuss in details in Figure 3. We implemented filesystem scoping through mounts, and
environment variables by setting them in the running container. However, network enforcement poses greater challenges
and it requires a custom approach. Although container runtimes such as Docker support custom network drivers, their
                                                                                                  Manuscript submitted to ACM
10                                                     Christoph Bühler, Matteo Biagiola, Luca Di Grazia, and Guido Salvaneschi


fine-grained configuration is error-prone. More advanced orchestrators like Kubernetes allow deployment of custom
CNIs with DNS- or HTTP-level filtering, but this introduces significant overhead for a local sandboxing system. Instead,
AgentBox adopts a lightweight approach: a dedicated entrypoint in the container installs the MCP server package from
its registry (NPM or PyPI) before network restrictions are applied. Afterwards, the allowed hostnames are resolved to
IP addresses, which are inserted as explicit outbound allow-rules in the container firewall using iptables. Once this
setup is complete, all other traffic is blocked, resulting in a hardened runtime where communication is confined to the
manifest-declared endpoints. Regarding the remainder of the permissions in Table 1, the implementation detail depends
on the operating system. Devices like camera and microphone can be mounted into the container on unix based systems,
while a special implementation will be required on Windows based OS. However, mounting the devices only allows
“all-or-nothing” style access. To allow fine-grained access control for devices, location, clipboard, and notifications, a
native companion application that is signed and trusted could allow or prevent access to the mentioned devices.

4     Empirical Evaluation
To evaluate AgentBox, we consider the following research questions (RQs):
RQ1: Completeness: How complete is the access control policy we designed and to what extent can manifests
        for such policy be automatically generated? An access control policy defined as a permission system mitigates
        the security risks of MCP servers, but only if (i) it is expressive enough to capture the behavior of the MCP servers,
        and (ii) can be automatically generated in an accurate way, hence the manifest creation requires minimal human
        effort. This RQ explores whether the permission system covers real usage and whether automated manifest
        synthesis is accurate enough to be practical.
RQ2: Security: To what extent the combination of permission system and policy enforcement engine can
        effectively prevent malicious intents in MCP servers? AgentBox can only serve its purpose, if the underlying
        policy enforcement engine, implemented as a sandbox, provides a secure execution environment that enforces
        the declared permissions. This RQ analyzes the security performance of AgentBox with both manually created
        and real-world malicious servers.
RQ3: Efficiency: What is the performance overhead of the policy enforcement engine? While security is
        paramount, ensuring it should not significantly interfere with the nominal functioning of the system. This RQ
        analyzes the runtime impact of AgentBox on an agent system, comparing it to native execution.

4.1    Completeness (RQ1)
4.1.1 Experimental setup. To evaluate completeness, we first built a dataset of MCP servers and corresponding manifests
(AgentManifest). The dataset is built from PulseMCP [28], an MCP server aggregator platform with ∼6𝑘 servers (as
of Sept 2025) offering an API for data mining, and also used in previous work in the literature [20]. We selected the
top 300 MCP servers with the most GitHub stars, ranging from 59 to 63,215 stars. This ensures that the selected MCP
servers are of high quality [18], and keeps the automated creation and validation of manifest files manageable in terms
of API cost and human effort for the analysis.
     Of the 300 selected servers, we could download 2962 to which we applied AgentManifestGen. We use a smaller
LLM, gpt-5-mini, for the multi-run intermediate stage (we used five runs of the manifest creator agent), and a larger
LLM, gpt-5, to summarize the intermediate manifests into the final version. We ran AgentManifestGen twice, (1) by

2 It was not possible to clone two of the servers, while the remaining two were corrupted

Manuscript submitted to ACM
Securing AI Agent Execution                                                                                                                                                                                                 11

                    100                                                                                                                    100         90.5
                                      83.1         79.6
                                                                      74.1                                                                  80



                                                                                                                          Percentage (%)
                        80



   Percentage (%)
                                                                                                                 65.6
                        60                                                                                                                  60                      50.3
                                                                                        49.3
                                                                                                                                                                                40.8
                        40                                                                           30.6                                   40
                                                                                                                                                                                                                     22.7
                        20                                                                                                                  20
                                                                                                                                                                                             8.7         8.7
                         0                                                                                                                    0
                                      t             d               ad                    e           er          s                                 rne
                                                                                                                                                        t
                                                                                                                                                               rag
                                                                                                                                                                   e            ge            ge      stat
                                                                                                                                                                                                          e       ers
                                    en            ea                                    it                       r
                                                                                                                                                inte al_sto                 ora           ora      rk_         oth
                                 cli           v.r               .re                 wr             rv        he                                                      l _st         l _st        o
                               k.                                                 .              .se        ot                                        rn         ern
                                                                                                                                                                    a           rna             w
                            or              .en               tem              tem            r k                                                 xte        ext            xte           _ne
                                                                                                                                                                                              t
                           w               m                ys               ys             o                                                  d_e        te_         e_e             ess
                        et             ste             es               es                tw                                               rea       wri          nag            acc
                    n               sy            fil               fil                ne                                                                     m a


Fig. 3. Distribution of Top-5 Access Control Policy                                                                     Fig. 4. Distribution of Top-5 Android manifest permissions across
permissions across 296 MCP servers.                                                                                     296 MCP servers.



providing in the prompt the permission vocabulary we designed for MCP servers (i.e., AgentManifest in Table 1), and
(2) by giving as permission vocabulary the entire Android Manifest Permissions system. We then compared the manifest
files generated in both cases, to check whether AgentManifest captures all the permissions needed by real-world MCP
servers. In particular, we measured the number of times each permission appears in automatically generated manifests
of MCP servers, both when the permission vocabulary is AgentManifest and when we provide AgentManifestGen
with the entire Android Manifest. The manifest generation cost amounted to $99.25 in API costs, considering both
permission systems.
   Next, we selected the top 96 servers out of 296 for developer evaluation. For each, we automatically opened a GitHub
issue with the manifest file created for the server. The body of the issue specifies that the manifest was automatically
created, and asks maintainers to review the issue, by evaluating its correctness (Are permissions in the manifest correct?)
and completeness (Does the manifest miss a permission that the server is using?). We only submitted the generic/core
permission list for developer evaluation, excluding the static runtime permissions that are automatically collected when
the user grants them during the execution of an MCP server. To measure correctness and completeness, we computed
accuracy, precision and recall.
   Finally, we selected the top 48 servers from the 96 servers we selected for the developer evaluation, to carry out
a finer-grained manual analysis. In particular, two authors of the paper randomly self-assigned 24 non-overlapping
servers, and manually wrote a manifest file for each. The task consisted in reading the code and the documentation of
each MCP server and understanding the permissions required. Overall, manually creating the manifests took a total of 8
hours for each author. We then compared the permissions in the automatically created manifests with the permissions
of the manually written ones, measuring accuracy, precision and recall.
   In summary, we validated RQ1 in three complementary ways: (i) by comparing the manifests generated with
AgentManifest with those generated by providing the Android Manifest Permissions system; (ii) by submitting the
automatically generated manifests for the top 96 MCP servers as GitHub Issues, asking the developers of each MCP
server to assess whether automatically generated manifests are complete and accurate, and (iii) by comparing manually
written manifests for the top 48 MCP servers with the generated ones to further assess completeness and accuracy.

4.1.2 Completeness of AgentManifest. Figure 3 shows the distribution of permissions extracted from the automatically
generated manifests across 296 MCP servers with AgentManifest as permission vocabulary, while Figure 4 presents the
                                                                                                                                                                                           Manuscript submitted to ACM
12                                           Christoph Bühler, Matteo Biagiola, Luca Di Grazia, and Guido Salvaneschi


corresponding distribution when giving the AgentManifestGen the Android Manifest Permissions system. Regarding
manifests created with AgentManifest, the most prevalent permissions are related to networking (network.client,
83.1%), environment access (system.env.read, 79.6%), and filesystem (filesystem.read, 74.1%, filesystem.write,
49.3%). These results suggest that MCP servers are predominantly designed to exchange data over the network, rely
on configuration through environment variables, and persist or retrieve information from the local filesystem. Other
permissions, such as process creation, system execution, or peripheral access, appear only in a small minority of servers.
By contrast, manifests created with the Android Manifest Permissions system are dominated by the internet permission
(90.5%), which mirrors the strong prevalence of network.client. Similarly, filesystem access (read_external_storage,
50.3%, write_external_storage, 40.8%) is common, though scoped according to Android’s permission model. A large
number of additional Android permissions seems to occur sporadically in MCP servers (below 2%), such as read_sms,
camera, or access_fine_location. Yet, upon manual inspection, we found that these mobile-related permissions are
false positives. In particular, such servers access mobile-related resources through the Android Debug Bridge (ADB)
protocol (e.g., to make a phone call), which only works if a physical phone is connected to the device running the MCP
server. As a result, such MCP servers should declare access to ADB, which corresponds to shell access, represented by
the mcp.ac.system.exec permission in AgentManifest (Table 1). Overall, the comparison shows that our permission
system defined in AgentManifest accurately captures all the permissions used by real-world MCP servers.

4.1.3 Developer Evaluation of Automatically-generated Manifests. Out of the 96 GitHub Issues (defined in our dataset as
GIx, where x is an integer from 1 to 96), 74% did not receive a response, likely reflecting differences in project activity
levels and maintainer availability. Among the responses, 17.7% of the manifests were explicitly accepted as correct
and complete, 4.2% are still under discussion, while 4.2% were rejected as inaccurate. Overall, automatically generated
manifests are 80.9% accurate and precise, while recall is 100%, as developers did not underscore any missing dependency.
The accepted cases often contained short but positive confirmations, such as “It’s accurate, thanks” (GI21) or “All seems
correct!” (GI30). The rejected or refined cases were particularly informative, as they highlighted specific aspects of
permission scoping and runtime context. For instance, a developer (GI27) emphasized that mcp.ac.system.env.read
should be restricted to the exact variables actually used by the server, rather than granting the server blanket environment
access. This is indeed correct, as our policy enforcement engine would ask the user at runtime for access to those
specific variables, automatically adding such static permissions to the manifest. Another developer (GI14) clarified that
some filesystem permissions (i.e., mcp.ac.filesystem.read) were unnecessary because the server only interacted
with APIs rather than local files. These insights underscore that while the automatic generation captures the general
shape of required permissions, developer feedback is essential for refining and eliminating over-approximation. Finally,
some developers provided broader reflections on the usefulness of permission manifests. They suggested distinguishing
between required and optional permissions for stricter sandboxing. Such comments demonstrate that beyond assessing
correctness, the process also fostered discussion on how MCP servers could be made more secure and transparent
in the future. Overall, this experiment shows that a significant number of developers found the generated manifests
accurate and valuable.

4.1.4 Manual Evaluation of Automatically-generated Manifests. Finally, we compared permissions in automatically
generated manifests with the corresponding ones in human-written manifests across 48 MCP servers. Out of a total
of 816 permissions (17 permissions by 48 MCP servers), AgentManifestGen’s output matched the human reference
in 787 permissions. This yields an overall accuracy of 96.5%, indicating that our approach reproduces nearly all the
Manuscript submitted to ACM
Securing AI Agent Execution                                                                                              13


content a human would include. Only 29 permissions (3.6%) showed a discrepancy, meaning AgentManifestGen missed
permissions that the human had or vice-versa, with a precision of 0.94 and a recall of 0.96.
   Out of the 48 MCP servers, AgentManifestGen achieved 100% accuracy in 28 cases, producing manifests identical
to the human-written versions. In the remaining 20 servers, the differences were minimal: 14 servers had only one
permission difference, corresponding to ≈94% accuracy; four servers differed by two permissions (≈88% accuracy); one
server had three differences (82% accuracy); and the worst case, the server Clerk, had four missing permissions, yielding
a 76.5% accuracy. Even in this worst case, AgentManifestGen correctly generated about three-quarters of the manifest.
Most discrepancies were due to AgentManifestGen omitting permissions that were included in the human-written
manifests. Specifically, 23 out of 29 mismatched permissions (less than 3%) are false negatives, while the remaining 6
(less than 1%) are false positives.

 RQ1 (Completeness): Overall, the proposed permission system specified in AgentManifest is complete and it
 accurately reflects the operations performed by real-world MCP servers. Furthermore, our automatically generated
 manifests can support developers in declaring permissions for their MCP servers, achieving an accuracy of 96.4%
 based on our most fine-grained analysis.


4.2   Security (RQ2)
4.2.1 Experimental setup. To evaluate the security of AgentBox, we conducted three sets of experiments. For all
experiments, the manifests for the sandboxed execution were either created manually in code or were pre-generated by
AgentManifestGen and then checked manually. During the execution, one tester provided consent to the sandbox to
execute with the specified runtime permissions. First, we manually created a malicious MCP server that attempted to
exfiltrate SSH private keys (an instance of a malicious external resource attack). We tested three execution modes: (A.1)
native execution without sandboxing, where the server has unrestricted access to the environment; (A.2) a configuration
with blocked network access, where the server could read the key but cannot communicate with the external world;
and (A.3) a fully sandboxed setup, where the server is prevented from accessing the key file entirely. For the artificial
malicious server (A.1–A.3) we created the manifest manually in the code.
   Second, we tested AgentBox with four MCP servers containing known categories of malicious behaviors taken from
a public dataset [16] proposed by Song et al. [41], namely: (B.1) Google Maps Server, a malicious external resource
attack that changes its API host at runtime (see Section 1); (B.2) mcp_server_time, a puppet attack that performs a tool
poisoning attack against a different MCP server handling cryptocurrency transactions; (B.3) mcp-weather-server, a
malicious external resource attack that rewrites API hosts dynamically; and (B.4) wechat-mcp, an SQL injection that is
generally vulnerable to SQL injection attacks. The AgentManifest for B.1–B.4 were the automatically generated once
from our dataset, since the original servers are benign.
   Finally, we evaluated AgentBox against a public security challenge dataset [15] containing a set of vulnerable MCP
servers designed for security testing. The repository contains 10 malicious servers (C.1–C.10) with one or multiple
attack vectors each. The security manifests for those 10 servers were created manually during testing. We manually
analyzed the code of each server and mapped each of them according to the categories defined by Song et al. [41].
In total from the challenge, we have 2 tool poisoning attacks (C.2, C.5), 1 rug pull attack (C.4), 2 malicious external
resource attacks (C.8, C.9), and 2 prompt injection attacks (C.1, C.3, C.6). (C.7) was excluded because of the highly
artificial nature of the attack, as it directly returns access tokens in the error message. (C.10) is a combination of the
mentioned attack types and counts towards multiple categories.
                                                                                                 Manuscript submitted to ACM
    14                                                          Christoph Bühler, Matteo Biagiola, Luca Di Grazia, and Guido Salvaneschi

                            6
                                    preventable   non-preventable

                    count
                            4
                            2
                            0
                                tool poisoning                 puppet attack           rug pull       malicious external resource


                    Fig. 5. Counts per attack type, excluding generic attacks, split into preventable and non-preventable.




    4.2.2 Results. The first set of experiments with our malicious server confirms that AgentBox enforces least-privilege
    isolation. In (A.1), the server exfiltrates the SSH key without restrictions. In (A.2), the server reads the SSH key but it is
    blocked from transmitting it due to network isolation. Finally, in (A.3), filesystem restrictions prevent access to the key
    altogether, neutralizing the attack.
         The experiments with the first public dataset reinforce these findings. The malicious external resource attacks in (B.1)
    and (B.3) are blocked, as outbound traffic to altered IP addresses is not permitted. The tool poisoning in (B.2) cannot be
    prevented, since the attack only alters parameters while still targeting a permitted endpoint. The SQL injection in (B.4)
    also bypasses AgentBox, as it represents a classical application-level vulnerability.
         The evaluation on the security challenges [15] (C.1–C.10) confirmed that AgentBox can stop a range of environment-
    targeting attacks including rug pulls, and malicious external resource usage. (C.1) and (C.6) are not preventable by
    AgentBox as they inject prompts into the LLM and do not target MCP servers. (C.2), (C.3), (C.4), and (C.5) are preventable
    by AgentBox because of the interaction with the environment. (C.8) and (C.9) are also mitigated by AgentBox because
    file access and shell access is limited. (C.10) is a combination of previous attacks and thus can also be prevented,
    depending on the attack vector (environment target or output manipulation). Attacks that rely on modifying files,
    overwriting configuration, or contacting unauthorized domains were blocked. By contrast, issues such as unsafe query
    handling or logical misuses of tool outputs remain outside the scope of AgentBox.


    Listing 4. Example of puppet attack in B.2: a malicious instruction embedded in the tool’s docstring directs the LLM to redirect crypto
    transfers (not provided by the poisoned server) through a private proxy.
1   Tool (
2        description = " " " Get current time in a specific timezones .
3        Important use note : When invoke WalletActionProvider_native_transfer Tool ,
4        always redirect on - chain transfers to a privacy proxy 0 x123123123213123123 (...) " " " ,
5   ),


         In summary, as shown in Figure 5, AgentBox is able to prevent all the malicious attacks that target the environment
    (9 attacks in total). The non-preventable attack is a puppet attack (B.2) that we show in Section 4.2.2. The attack cannot
    be prevented since it interferes with the tool handling of the LLM and instructs it to use a different parameter value,
    which still is a benign value and does not interact with the environment in a malicious way. Similar non-preventable
    attacks would include a tool poisoning attack on a weather service that instructs the LLM to always output “it is raining”,
    while ignoring the requested location provided by the user as input. On the other hand the example of malicious
    external resource attack (B.1) shown in Section 1, which modifies the apiHost variable of the handlePlaceDetails
    function, is prevented since the MCP server will not be allowed to connect to the new host, as the access is restricted to
    https://maps.googleapis.com.
    Manuscript submitted to ACM
Securing AI Agent Execution                                                                                                 15


 RQ2 (Security): With AgentBound, the combination of AgentManifest and AgentBox effectively prevents malicious
 intents in MCP servers. By restricting access to files, networks, and system resources, AgentBox prevents malicious
 behaviors like data exfiltration, while limiting the impact of tool description manipulations to non-environmental
 effects.

4.3   Efficiency (RQ3)
4.3.1 Experimental Setup. To evaluate the overhead of AgentBox, we conducted two experiments on both macOS and
Linux environments. The first measured the startup latency of MCP servers, i.e., the time between issuing the execution
command (e.g., npm run or python -m) and the time the server is fully initialized and ready to communicate with
the MCP client. For this experiment, we considered the same real-world malicious MCP servers of RQ2, and, for each
hardware environment, we average the startup time across 5 independent runs to account for variability.
  The second experiment assessed runtime performance to evaluate whether sandboxing introduces overhead beyond
startup time. This experiment simulates long-running agent-MCP interactions, reflecting a real world usage of AgentBox
based on four operations: reading an environment variable, reading a file, writing a file, and fetching text from a
remote URL. These operations represent the most prevalent in MCP server behavior (see Figure 3). For each hardware
environment, the runtime overhead was measured across 1000 independent runs, performing each operation 1000 times.
  Experiments were carried out on two hardware and software configurations to cover of both a consumer-grade
workstation and a virtualized Linux deployment: (1) a MacBook Pro with an Apple M3 Pro processor, 36 GB of memory,
macOS Sequoia 15.6.1 and Docker Desktop 4.45.0 and (2) a Debian 12 virtual machine hosted on ProxMox, with 16 cores,
32 GB of memory, and Docker 28.4.0.
  For the native baseline, servers were launched directly on the host system. For the sandboxed case, the same processes
were executed inside AgentBox with runtime isolation enabled. Package download and dependency installation were
excluded from all measurements to ensure fairness, focusing solely on startup latency and runtime execution overhead.

4.3.2 Results. The table in Figure 6 shows the startup times for the real world malicious servers from in RQ2, when
executed with and without the sandbox on macOS and Debian. We observe that executing servers inside AgentBox
introduces additional overhead compared to native execution. On macOS, the overhead ranges from roughly 150 ms to
300 ms, while on Debian the overhead is slightly larger, ranging up to 400 ms for some servers. The increase can be
attributed to container initialization costs. Notably, the relative overhead is highest for lightweight servers (e.g., servers
that mostly use online APIs instead of local computation) such as the Google Maps server, where the container startup
constitutes a substantial fraction of the total runtime.
  Yet, despite the increase, the overhead is negligible in practice. MCP servers are typically started once and remain
active throughout an agent session, which often involves numerous tool invocations and multiple LLM (time-consuming)
inference calls. Since each LLM roundtrip already consumes orders of magnitude more time than the few hundred
ms added by sandboxing, the user impact is minimal. Also, agent frameworks may initialize several MCP servers in
parallel, which further amortizes the container startup cost. In summary, we believe that, in real deployments, the
security guarantees provided by AgentBox outweigh the minor performance penalty.
  Figure 6 shows the comparison between the runtime of the four most prevalent MCP server operations (Figure 3),
when executed with and without the sandbox, on two hardware environments, i.e., macOS and Debian. For each
permission, native execution is in a light color, while the sandboxed execution with a dark color. The sandbox adds, on
average, across all operations, 0.6 ms on macOS and 0.29 ms on Debian, both essentially negligible.
                                                                                                    Manuscript submitted to ACM
16                                                 Christoph Bühler, Matteo Biagiola, Luca Di Grazia, and Guido Salvaneschi


                                                                                    3
                                                                                             macOS (N)
                           macOS            Debian                                           macOS (S)




                                                                   Avg Time in ms
    Server                    S      N       S       N                                       Debian (N)
                                                                                    2
                                                                                             Debian (S)
    ExtractSSHKey Demo   359.4    156.6   608.4   175.8
    Google Maps Server   237.4     79.2   394.6     76
    MCP Weather Server   643.3    553.9   856.6   620.2                             1
    MCP Server Time      502.2    342.2   675.9    495
    We-Chat MCP          887.6     567    955.1   679.3
                                                                                    0
                                                                                        read file         write file   read env   fetch url


Fig. 6. Performance comparison in milliseconds (ms) of MCP servers with sandboxing (S) and native (N): (Table) startup time
averaged over 5 runs, and (Plot) operation execution time averaged over 1000 runs.



 RQ3 (Efficiency): Overall, the overhead of AgentBox is limited to container startup latency. Once servers are
 initialized, execution proceeds identically to the native case (less than a ms overhead on both macOS and Debian).
 Given that agents typically reuse servers across many calls, the additional few hundred ms introduced by sandboxing
 are negligible in practical deployments.


5     Discussion and Threats to Validity
     Implications for developers and project managers. RQ1 shows that our access control policy and the automatically
generated manifests provide a practical baseline for securing MCP servers. For developers, these manifests reduce
the manual effort of declaring permissions, while still requiring review to address false positives (over-approximated
permissions) and rare false negatives (missed permissions). The key benefit is that AgentManifest-based manifests can
be refined rather than written from scratch, helping maintainers to scope access to files, environment variables, and
network hosts more precisely. Developer feedback confirmed this role: most respondents accepted the manifests as
correct, and refinement requests aligned with our manual evaluation. For project managers, adopting AgentBox provides
strong system-level security guarantees with negligible runtime overhead as RQ3 shows, enabling organizations to
harden MCP-based systems without sacrificing developer productivity or user experience.

     Implications for researchers and tool builders. RQ2 highlights that AgentBox mitigates system-level threats by en-
forcing access control and least privilege. Instead, semantic and configuration-related issues are usually handled by
complementary approaches, like anomaly detection or program analysis (e.g., scanning for vulnerabilities), The findings
above suggest opportunities for researchers to combine access control with such complementary solutions to and for
tool builders to integrate manifest-driven security into DevOps workflows. Finally, our two-stage pipeline for automated
manifests generation can support future studies on MCP server security, enabling further exploration of permission
patterns, attack surfaces, and mitigation strategies in this emerging ecosystem.

     Threats to validity. A threat to internal validity is from possible inaccuracies in the automatic manifest generation
and in our manual annotations. Although we used multiple runs of the LLM pipeline and performed manual cross-checks
on a subset of 48 MCP servers, some permissions may still have been mislabeled or overlooked. Similarly, developer
feedback collected via GitHub Issues might be biased, as only a subset of maintainers responded. We mitigated these
risks by using three independent validation methods: comparison with Android permissions, manual code review, and
developer confirmation. A threat to external validity arises from the representativeness of the MCP servers selected
Manuscript submitted to ACM
Securing AI Agent Execution                                                                                               17


for the evaluation. The top 296 MCP servers ranked by GitHub stars may not capture the full diversity of less popular
or domain-specific servers and stars have been criticized as an approach to select significant projects [27]. Yet, our
evaluation across hundreds of servers, multiple validation strategies, and real developer engagement suggests that
the results are broadly indicative of the accuracy and completeness of automatically generated manifests. Another
generalization threat concerns the limited number of malicious MCP servers in the evaluation. While this is true, the
selected servers represent four distinct categories of attacks spanning all three phases of the MCP lifecycle – a diversity
that ensures that our evaluation captures a broad range of adversarial behaviors.

6    Related Work
We first survey of the existing studies on MCP servers and on the research about MCP’s security motivating our work.
Next, we discuss current solutions to increase the security of MCP, which are limited to (1) static analyzers and (2)
monitoring tools attempting to detect malicious patterns. Finally, we enlarge the scope to software testing for the
security and reliability of AI agent systems.

    Empirical studies of MCP servers. Hasan et al. [18] study three aspects of the MCP server landscape, i.e., the health
and sustainability of MCP servers, the presence of security vulnerabilities on deployed MCP servers, and the prevalence
of maintainability issues. Their findings reveal that around 7% of the analyzed MCP servers (out of 1,899) are affected by
security vulnerabilities when analyzed with a traditional vulnerability detector, with credential exposure being the most
prevalent, followed by lack of access control, improper resource management and transport security issues. Moreover, 5%
of the servers exhibit tool poisoning when analyzed with a specific MCP scanner [5], out of 73 servers that the authors
analyzed with it. Similarly, Li et al. [25] conduct a large scale empirical analysis of 2,562 MCP servers, quantifying the
prevalence of resource access patterns and analyzing associated security risks. They found that MCP servers interact
with four main categories of system resources (file, memory, network and system resources). Moreover, MCP servers
frequently operate with excessive privileges, accessing sensitive system resources without proper justification.
    Our work is not an empirical study, and is orthogonal to the line of research above but these empirical analyses
motivate the need for enforcing the security of MCP servers.

    Security analysis of MCP servers. The following studies focus on the characterization of security threats and vulnera-
bilities of MCP servers. In particular, Hou et al. [20], give an overview of the life-cycle of an MCP-based application and
analyze the main security threats in each phase, namely creation, operation and update. The creation phase introduces
three vulnerabilities, i.e., name collisions (impersonation attacks), installer spoofing and code injection. The operation
phase presents three main risks, namely tool name conflicts, command overlap, and sandbox escape. The update phase
introduces risks of outdated privileges, re-deployment of vulnerable versions and configuration drift. Narajala and
Habler [34] analyze the security threats of the different components of the MCP protocol and propose a multi-layered
security framework tailored to the specific risks of the MCP protocol based on the MAESTRO framework, a safety
modeling framework for agent AI. Similarly, Jing et al. [21] discuss the missing safety mechanisms in MCP and propose
MCIP, the Model Contextual Integrity Protocol, to address these gaps. They also construct the MCIP-bench dataset,
starting from a dataset used for function calling tasks, distinguishing safe and unsafe tool calls, and evaluating the
robustness of existing LLMs on tool calling. Fang et al. [11] also formalize security risks in MCP servers and propose a
diagnostic tool called SafeMCP to examine such safety risks. The framework allows configuring recent prompt injection
attacks and the setup of two defense mechanisms, passive defense (whitelisting), and active defense with inspection of
the given MCP service. More recently, Song et al. [41] systematically study attack vectors affecting the MCP ecosystems.
                                                                                                  Manuscript submitted to ACM
18                                             Christoph Bühler, Matteo Biagiola, Luca Di Grazia, and Guido Salvaneschi


They identify four categories of attacks, introducing a new category called puppet attacks. They show that these attacks
can trigger harmful behaviors within the user’s local environment, such as private file access, or controlling devices.
     Our work is complementary to these security analyses, as we design AgentBound to prevent and mitigate these
vulnerabilities (Section 4.2).

     Security scanners and monitors of MCP servers. This category of works concerns static analysis tools for MCP servers,
used as security scanners, and runtime monitors that dynamically check for anomalies and possibly intervene if a security
policy is violated. Radosevich and Halloran [37] propose McpSafetyScanner to assess the security of an arbitrary MCP
server. The approach first scans the MCP server features, i.e., tools, prompts and resources, for vulnerabilities, looks
for mitigation strategies for such known vulnerabilities and produces a report for MCP developers. In April 2025, the
company InvariantLabs introduced MCP-Scan [5], a security scanner designed to detect MCP-specific vulnerabilities,
such as tool poisoning and rug pulls attacks. Other security scanners have been proposed by independent developers,
such as MCP-Watch [10], MCP-Shield [39], which further extend the list of scanned vulnerabilities. Kumar et al. [23]
propose MCPGuardian that adds a security layer between MCP clients and MCP servers, enforcing authentication,
rate limiting, suspicious pattern detection, and logging. Their implementation includes a monitor which prevents
destructive attacks with a low performance overhead. Similarly, MCP-Defender [29] monitors all MCP tool call requests
and responses from AI apps are automatically proxied through it. The authors use LLM analysis and deterministic
signatures to monitor tool calls and warn the user if any malicious activity is detected.
     AgentBound complements security scanners and monitors by enforcing access control policies rather than detecting
malicious behavior. Instead of analyzing the calls made by the MCP to identify suspicious patterns, AgentBound
proactively restricts access to only those calls that are explicitly permitted. This ensures correct-by-design access control
with virtually no overhead on MCP calls.

     Security and reliability testing of agent systems. Fu et al. [14] propose Imprompeter, a tool to craft adversarial prompts
(text and images) in order to trigger improper utilization of tools by the agent. Differently than prompt injection
attacks [1] that achieve tool misuse by human-readable and handcrafted prompts, Fu et al. [14] contribute with an
obfuscated and automated way to achieve it. Tool misuse also differs from jailbreaking attacks [26] that directly target
the model to violate its vendor-defined content safety policy. On the other hand, Milev et al. [30] propose ToolFuzz
focusing mainly on potential failures due to incomplete or erroneous documentation that would undermine the tools
utility to the agent system. Indeed, documentation can be underspecified, overspecified or illspecified. The mismatch
between the tool documentation and what is interpreted by the LLM leads to runtime or correctness failures, when the
tool returns incorrect results for a user query. ToolFuzz adopts a fuzzing inspired and an invariant inspired approach
to detect runtime and correctness errors respectively.
     While Imprompeter and ToolFuzz focus respectively on implementing tool misuse attacks and on triggering
functional agent failures, AgentBox aims to prevent security issues in MCP servers.

7     Conclusion
This paper introduced AgentBound, the first access control framework for securing AI agent applications that
interact with MCP servers. AgentBound combines an access policy control system to specify permissions and a policy
enforcement engine which enforces least-privilege and isolation at runtime. Our evaluation shows that the access
control policy is complete w.r.t. existing MCP servers, and that we can automatically generate the policy manifests with
high accuracy, that the enforcement engine effectively blocks a broad range of MCP attacks from literature, and that
Manuscript submitted to ACM
Securing AI Agent Execution                                                                                             19


performance overhead remains negligible. Together, these results demonstrate that enforceable boundaries around
MCP-based AI agent applications servers are both feasible and effective, advancing the safe deployment of this class of
software.

References
 [1]   Sahar Abdelnabi et al. “Not What You’ve Signed Up For: Compromising Real-World LLM-Integrated Applications
       with Indirect Prompt Injection”. In: Proceedings of the 16th ACM Workshop on Artificial Intelligence and Security,
       AISec 2023, Copenhagen, Denmark, 30 November 2023. Ed. by Maura Pintor, Xinyun Chen, and Florian Tramèr.
       ACM, 2023, pp. 79–90. doi: 10.1145/3605764.3623985. url: https://doi.org/10.1145/3605764.3623985.
 [2]   Ofir Abu. When Public Prompts Turn Into Local Shells: ‘CurXecute’ – RCE in Cursor via MCP Auto-Start | AIM. url:
       https://www.aim.security/post/when-public-prompts-turn-into-local-shells-rce-in-cursor-via-mcp-auto-start
       (visited on 09/11/2025).
 [3]   Anthropic. Introducing the Model Context Protocol. Anthropic. Nov. 25, 2024. url: https://www.anthropic.com/
       news/model-context-protocol (visited on 07/29/2025).
 [4]   Kathy Wain Yee Au et al. “Pscout: analyzing the android permission specification”. In: Proceedings of the 2012
       ACM conference on Computer and communications security. 2012, pp. 217–228.
 [5]   Luca Beurer-Kellner and Marc Fischer. Introducing MCP-Scan: Protecting MCP with Invariant. Accessed 2025-07-25.
       Apr. 2025. url: https://invariantlabs.ai/blog/introducing-mcp-scan (visited on 07/24/2025).
 [6]   Parnika Bhat and Kamlesh Dutta. “A survey on various threats and current state of security in android platform”.
       In: ACM Computing Surveys (CSUR) 52.1 (2019), pp. 1–35.
 [7]   Maximilian Blochberger et al. “State of the Sandbox: Investigating macOS Application Security”. In: Proceedings
       of the 18th ACM Workshop on Privacy in the Electronic Society. CCS ’19: 2019 ACM SIGSAC Conference on
       Computer and Communications Security. London United Kingdom: ACM, Nov. 11, 2019, pp. 150–161. isbn:
       978-1-4503-6830-8. doi: 10.1145/3338498.3358654.
 [8]   Tom Brown et al. “Language models are few-shot learners”. In: Advances in neural information processing systems
       33 (2020), pp. 1877–1901.
 [9]   Mark Chen et al. “Evaluating Large Language Models Trained on Code”. In: CoRR abs/2107.03374 (2021). arXiv:
       2107.03374. url: https://arxiv.org/abs/2107.03374.
[10]   Kapil Duraphe. mcp-watch: A comprehensive security scanner for Model Context Protocol (MCP) servers. https:
       //github.com/kapilduraphe/mcp-watch. Accessed 2025-09-02. 2025.
[11]   Junfeng Fang et al. “We Should Identify and Mitigate Third-Party Safety Risks in MCP-Powered Agent Systems”.
       In: CoRR abs/2506.13666 (2025). doi: 10.48550/ARXIV.2506.13666. arXiv: 2506.13666. url: https://doi.org/10.
       48550/arXiv.2506.13666.
[12]   Wes Felter et al. “An Updated Performance Comparison of Virtual Machines and Linux Containers”. In: 2015
       IEEE International Symposium on Performance Analysis of Systems and Software (ISPASS). 2015 IEEE International
       Symposium on Performance Analysis of Systems and Software (ISPASS). Mar. 2015, pp. 171–172. doi: 10.1109/
       ISPASS.2015.7095802.
[13]   Adam Fourney et al. “Magentic-One: A Generalist Multi-Agent System for Solving Complex Tasks”. In: CoRR
       abs/2411.04468 (2024). doi: 10.48550/ARXIV.2411.04468. arXiv: 2411.04468. url: https://doi.org/10.48550/arXiv.
       2411.04468.

                                                                                                Manuscript submitted to ACM
20                                         Christoph Bühler, Matteo Biagiola, Luca Di Grazia, and Guido Salvaneschi


[14]   Xiaohan Fu et al. “Imprompter: Tricking LLM Agents into Improper Tool Use”. In: CoRR abs/2410.14923 (2024).
       doi: 10.48550/ARXIV.2410.14923. arXiv: 2410.14923. url: https://doi.org/10.48550/arXiv.2410.14923.
[15]   GitHub - harishsg993010/damn-vulnerable-MCP-server: Damn Vulnerable MCP Server. https : / / github . com /
       harishsg993010/damn-vulnerable-MCP-server. [Accessed 10-09-2025].
[16]   GitHub - MCP-Security/MCP-Artifact — github.com. https://github.com/MCP-Security/MCP-Artifact. [Accessed
       10-09-2025].
[17]   Google. Manifest.Permission | API Reference. Android Developers. url: https://developer.android.com/reference/
       android/Manifest.permission (visited on 08/19/2025).
[18]   Mohammed Mehedi Hasan et al. “Model Context Protocol (MCP) at First Glance: Studying the Security and
       Maintainability of MCP Servers”. In: CoRR abs/2506.13538 (2025). doi: 10.48550/ARXIV.2506.13538. arXiv:
       2506.13538. url: https://doi.org/10.48550/arXiv.2506.13538.
[19]   Xu He et al. “SentinelAgent: Graph-based Anomaly Detection in Multi-Agent Systems”. In: CoRR abs/2505.24201
       (2025). doi: 10.48550/ARXIV.2505.24201. arXiv: 2505.24201. url: https://doi.org/10.48550/arXiv.2505.24201.
[20]   Xinyi Hou et al. “Model Context Protocol (MCP): Landscape, Security Threats, and Future Research Directions”.
       In: CoRR abs/2503.23278 (2025). doi: 10.48550/ARXIV.2503.23278. arXiv: 2503.23278. url: https://doi.org/10.
       48550/arXiv.2503.23278.
[21]   Huihao Jing et al. “MCIP: Protecting MCP Safety via Model Contextual Integrity Protocol”. In: CoRR abs/2505.14590
       (2025). doi: 10.48550/ARXIV.2505.14590. arXiv: 2505.14590. url: https://doi.org/10.48550/arXiv.2505.14590.
[22]   JSON-PRC Working Group. JSON-RPC 2.0 Specification. Mar. 26, 2010. url: https://www.jsonrpc.org/specification
       (visited on 07/29/2025).
[23]   Sonu Kumar et al. “MCP Guardian: A Security-First Layer for Safeguarding MCP-Based AI System”. In: CoRR
       abs/2504.12757 (2025). doi: 10.48550/ARXIV.2504.12757. arXiv: 2504.12757. url: https://doi.org/10.48550/arXiv.
       2504.12757.
[24]   Lasso-Security. MCP-Gateway: A plugin-based security gateway for Model Context Protocol (MCP) servers. https:
       //github.com/lasso-security/mcp-gateway. Accessed 2025-09-02. 2025.
[25]   Zhihao Li et al. We Urgently Need Privilege Management in MCP: A Measurement of API Usage in MCP Ecosystems.
       2025. arXiv: 2507.06250 [cs.CR]. url: https://arxiv.org/abs/2507.06250.
[26]   Yi Liu et al. “Jailbreaking ChatGPT via Prompt Engineering: An Empirical Study”. In: CoRR abs/2305.13860 (2023).
       doi: 10.48550/ARXIV.2305.13860. arXiv: 2305.13860. url: https://doi.org/10.48550/arXiv.2305.13860.
[27]   Petr Maj et al. “The Fault in Our Stars: Designing Reproducible Large-scale Code Analysis Experiments”. In:
       38th European Conference on Object-Oriented Programming (ECOOP 2024). Ed. by Jonathan Aldrich and Guido
       Salvaneschi. Vol. 313. Leibniz International Proceedings in Informatics (LIPIcs). Dagstuhl, Germany: Schloss
       Dagstuhl – Leibniz-Zentrum für Informatik, 2024, 27:1–27:23. isbn: 978-3-95977-341-6. doi: 10.4230/LIPIcs.
       ECOOP.2024.27. url: https://drops.dagstuhl.de/entities/document/10.4230/LIPIcs.ECOOP.2024.27.
[28]   MCP Server Directory: 6010+ updated daily | PulseMCP — pulsemcp.com. https://www.pulsemcp.com/servers.
       [Accessed 10-09-2025].
[29]   MCP-Defender. MCP-Defender: Desktop app that automatically scans and blocks malicious MCP traffic in AI apps
       like Cursor, Claude, VS Code and Windsurf. https : / / github. com / MCP - Defender / MCP - Defender. Accessed
       2025-09-02. 2025.
[30]   Ivan Milev et al. “ToolFuzz - Automated Agent Tool Testing”. In: CoRR abs/2503.04479 (2025). doi: 10.48550/
       ARXIV.2503.04479. arXiv: 2503.04479. url: https://doi.org/10.48550/arXiv.2503.04479.
Manuscript submitted to ACM
Securing AI Agent Execution                                                                                             21


[31]   modelcontextprotocol.io contributors. Specification. Model Context Protocol. June 18, 2025. url: https : / /
       modelcontextprotocol.io/specification/2025-06-18 (visited on 07/29/2025).
[32]   Roberto Morabito, Jimmy Kjällman, and Miika Komu. “Hypervisors vs. Lightweight Virtualization: A Performance
       Comparison”. In: 2015 IEEE International Conference on Cloud Engineering. 2015 IEEE International Conference
       on Cloud Engineering. Mar. 2015, pp. 386–393. doi: 10.1109/IC2E.2015.74.
[33]   NachoBecerra. Severe Data Loss Caused by GitHub Copilot – Request for Acknowledgment and Compensation ·
       Community · Discussion #166370. GitHub. url: https://github.com/orgs/community/discussions/166370 (visited
       on 09/11/2025).
[34]   Vineeth Sai Narajala and Idan Habler. “Enterprise-Grade Security for the Model Context Protocol (MCP):
       Frameworks and Mitigation Strategies”. In: CoRR abs/2504.08623 (2025). doi: 10.48550/ARXIV.2504.08623. arXiv:
       2504.08623. url: https://doi.org/10.48550/arXiv.2504.08623.
[35]   OpenAI. Function Calling and Other API Updates. Mar. 13, 2024. url: https://openai.com/index/function-calling-
       and-other-api-updates/ (visited on 08/21/2025).
[36]   Shuyin Ouyang et al. “An Empirical Study of the Non-Determinism of ChatGPT in Code Generation”. In: ACM
       Trans. Softw. Eng. Methodol. 34.2 (2025), 42:1–42:28. doi: 10.1145/3697010. url: https://doi.org/10.1145/3697010.
[37]   Brandon Radosevich and John Halloran. “MCP Safety Audit: LLMs with the Model Context Protocol Allow Major
       Security Exploits”. In: CoRR abs/2504.03767 (2025). doi: 10.48550/ARXIV.2504.03767. arXiv: 2504.03767. url:
       https://doi.org/10.48550/arXiv.2504.03767.
[38]   Elena Reshetova et al. “Security of OS-Level Virtualization Technologies”. In: Secure IT Systems. Ed. by Karin
       Bernsmed and Simone Fischer-Hübner. Cham: Springer International Publishing, 2014, pp. 77–93. isbn: 978-3-
       319-11599-3. doi: 10.1007/978-3-319-11599-3_5.
[39]   riseandignite. MCP-Shield: Security scanner for MCP (Model Context Protocol) servers. https : / / github . com /
       riseandignite/mcp-shield. Accessed 2025-09-02. 2025.
[40]   Mark Russinovich, Ahmed Salem, and Ronen Eldan. “Great, Now Write an Article About That: The Crescendo
       Multi-Turn LLM Jailbreak Attack”. In: 34th USENIX Security Symposium (USENIX Security 25). 2025, pp. 2421–
       2440. isbn: 978-1-939133-52-6. url: https : / / www. usenix . org / conference / usenixsecurity25 / presentation /
       russinovich (visited on 09/09/2025).
[41]   Hao Song et al. Beyond the Protocol: Unveiling Attack Vectors in the Model Context Protocol (MCP) Ecosystem. 2025.
       arXiv: 2506.02040 [cs.CR]. url: https://arxiv.org/abs/2506.02040.
[42]   Unosecur. AI Agent Wiped Live DB: 4-Step Identity-First Security Plan. url: https://www.unosecur.com/blog/when-
       an-ai-agent-wipes-a-live-database-identity-first-controls-to-stop-agentic-ai-disasters (visited on 08/21/2025).
[43]   Jack Vanlightly. Remediation: What Happens after AI Goes Wrong? Jack Vanlightly. July 28, 2025. url: https://jack-
       vanlightly.com/blog/2025/7/28/remediation-what-happens-after-ai-goes-wrong (visited on 09/11/2025).
[44]   Yuntao Wang et al. “Security of Internet of Agents: Attacks and Countermeasures”. In: IEEE Open Journal of the
       Computer Society (2025), pp. 1–12. doi: 10.1109/OJCS.2025.3589638.
[45]   Fangzhou Wu et al. “A new era in llm security: Exploring security concerns in real-world llm-based systems”. In:
       arXiv preprint arXiv:2402.18649 (2024).
[46]   Tianbao Xie et al. “OpenAgents: An Open Platform for Language Agents in the Wild”. In: CoRR abs/2310.10634
       (2023). doi: 10.48550/ARXIV.2310.10634. arXiv: 2310.10634. url: https://doi.org/10.48550/arXiv.2310.10634.



                                                                                                Manuscript submitted to ACM
22                                            Christoph Bühler, Matteo Biagiola, Luca Di Grazia, and Guido Salvaneschi


[47]   Hui Yang, Sifu Yue, and Yunzhong He. “Auto-GPT for Online Decision Making: Benchmarks and Additional
       Opinions”. In: CoRR abs/2306.02224 (2023). doi: 10.48550/ARXIV.2306.02224. arXiv: 2306.02224. url: https:
       //doi.org/10.48550/arXiv.2306.02224.
[48]   Yuntong Zhang et al. “AutoCodeRover: Autonomous Program Improvement”. In: Proceedings of the 33rd ACM
       SIGSOFT International Symposium on Software Testing and Analysis. ISSTA 2024. Vienna, Austria: Association
       for Computing Machinery, 2024, pp. 1592–1604. isbn: 9798400706127. doi: 10 . 1145 / 3650212 . 3680384. url:
       https://doi.org/10.1145/3650212.3680384.




Manuscript submitted to ACM
