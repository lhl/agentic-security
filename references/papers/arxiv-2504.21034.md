                                                 SAGA: A Security Architecture for Governing
                                                           AI Agentic Systems
                                                              Georgios Syros                                   Anshuman Suri                              Jacob Ginesin
                                                         Northeastern University                          Northeastern University                    Northeastern University
                                                        syros.g@northeastern.edu                         ans.suri@northeastern.edu                  ginesin.j@northeastern.edu

                                                                            Cristina Nita-Rotaru                                                Alina Oprea
                                                                           Northeastern University                                         Northeastern University
                                                                        c.nitarotaru@northeastern.edu                                     a.oprea@northeastern.edu




arXiv:2504.21034v2 [cs.CR] 29 Aug 2025
                                            Abstract—Large Language Model (LLM)-based agents in-                             presents several challenges, as highlighted in a recent OpenAI
                                         creasingly interact, collaborate, and delegate tasks to one another                 white paper [9]. Several key requirements include defining
                                         autonomously with minimal human interaction. Industry guide-                        unique identities for AI agents, authenticating these agents,
                                         lines for agentic system governance emphasize the need for users
                                         to maintain comprehensive control over their agents, mitigat-                       and providing secure mechanisms for agent discovery and
                                         ing potential damage from malicious agents. Several proposed                        communication. These requirements must remain effective
                                         agentic system designs address agent identity, authorization,                       even under adversarial conditions, as malicious actors may
                                         and delegation, but remain purely theoretical, without concrete                     attempt to impersonate agents, intercept communications, or
                                         implementation and evaluation. Most importantly, they do not                        manipulate agent behavior to extract sensitive information
                                         provide user-controlled agent management.
                                            To address this gap, we propose SAGA, a scalable Security                        or subvert intended functionality. Significantly, the OpenAI
                                         Architecture for Governing Agentic systems, that offers user                        white paper emphasizes the necessity of maintaining user
                                         oversight over their agents’ lifecycle. In our design, users register               control and supervision throughout all operational phases and
                                         their agents with a central entity, the Provider, that maintains                    throughout the entire lifecycle of LLM agents to safeguard
                                         agent contact information, user-defined access control policies,                    against potential harm from malicious agents.
                                         and helps agents enforce these policies on inter-agent commu-
                                         nication. We introduce a cryptographic mechanism for deriving                          Although various AI agentic system designs have been
                                         access control tokens, that offers fine-grained control over an                     proposed that incorporate agent identities [10], attribution [11],
                                         agent’s interaction with other agents, providing formal security                    authorization mechanisms and delegation capabilities [12],
                                         guarantees. We evaluate SAGA on several agentic tasks, using                        these designs largely remain theoretical without implemen-
                                         agents in different geolocations, and multiple on-device and cloud                  tation or evaluation. Most critically, they fail to adequately
                                         LLMs, demonstrating minimal performance overhead with no
                                         impact on underlying task utility in a wide range of conditions.                    address the essential component of user-controlled agent man-
                                         Our architecture enables secure and trustworthy deployment of                       agement. Recently, Google’s A2A protocol [13] introduces
                                         autonomous agents, accelerating the responsible adoption of this                    a decentralized identity framework where agents advertise
                                         technology in sensitive environments.1                                              public metadata and initiate direct, encrypted communica-
                                                                    I. I NTRODUCTION                                         tion using web-based authentication. While A2A promotes
                                                                                                                             interoperability and supports verifiable identifiers, it lacks
                                            AI agents with increased levels of autonomy are being                            policy enforcement mechanisms and runtime mediation of
                                         deployed in safety-critical applications, such as healthcare [1],                   agent interactions, and does not provide mitigation against
                                         [2], finance [3]–[5], and cybersecurity [6]–[8]. These agents,                      adversarial agents.
                                         built on top of Large Language Models (LLMs), excel at                                 In this paper, we propose SAGA, a framework for governing
                                         automating complex tasks traditionally performed by humans.                         LLM agent deployment, designed to enhance security while
                                         Agents powered by LLMs have sophisticated reasoning ca-                             offering user oversight on their agents’ lifecycle (see Figure 1
                                         pabilities and the ability to understand and generate natural                       for an overview). In SAGA users register themselves and
                                         language. They also leverage access to tools installed on user                      their agents with a Provider service that maintains user
                                         devices, external resources, and the ability to interact with                       and agent metadata and facilitates controlled communication
                                         other AI agents autonomously.                                                       establishment between agents. SAGA enables users to control
                                            The increasing autonomy and functionality of AI agents                           access to their agents through an Access Contact Policy that
                                         expand the attack surface of agentic systems, introducing                           users define for their agents. The enforcement of the policy
                                         numerous security risks. As AI agents become more in-                               is done through cryptographic access control tokens, derived
                                         tegrated into critical applications, securing these systems                         from agent one-time keys stored at the Provider. Inter-
                                           1 This is the full version of the paper accepted for publication at the Network   agent communication over secure TLS channels does not
                                         and Distributed System Security Symposium (NDSS) 2026.                              involve the Provider for scalability, while utilizing access
                                                                                 Provider                                                  Legend
                          (1) User Registration
                                                                                                                                 LLM       User           Agent
                                                                                                                                 Agent     Information    Information
                             Confirmation

          User                                                                                                                   Contact   Certificate
                                                                                                                                                          Access
                                                                                                                                                          Control
                                                                                                                                 Policy
                                                                                                                                                          Token
                                                                                                                                 Access
                                                                                                                                           Agent          One-time
                                                                                                                                 Control
                     (2) Agent Registration                                                                                      Key
                                                                                                                                           Conversation   Keys



                                                          User-Registry                      Agent-Registry




                              Confirmation                                                                          (3a) Agent
                                                                                                                      Lookup

                                                                          (3b) Get Access Control Token




                                                                          (3c) Agent Communication



             Agent                                Agent                                                                  Agent                    Agent



                               User                                                                                                User
Fig. 1: System overview of SAGA. (1) A user registers with the Provider. (2) A registered user registers their agent and
receives a confirmation from the Provider. (3a) An initiating agent requests a One-time Key (OTK) and the receiving agent’s
information from the Provider. (3b) The initiating agent contacts the receiving agent with the OTK, after which the agents
derive a shared key and the receiving agent encrypts an access control token under the shared key. (3c) The initiating agent
attaches this token to subsequent communication over TLS. When token expires or reaches limit, a new OTK is retrieved from
the Provider and a new token is obtained from the receiving agent.


control tokens to ensure compliance with user-defined policies.                                   the Provider fault-tolerant using RAFT introduces
The granularity of access control tokens provides a tradeoff                                      negligible throughput degradation across key operations.
between potential windows of vulnerability and performance                                        They also demonstrate that scaling the Provider using
overhead. The architecture aligns with best practices for secur-                                  sharding results in linear throughput increase.
ing agentic AI systems and meets key requirements outlined                                   The code of our protocol and the formal verification is
in emerging AI governance frameworks.                                                        available at https://github.com/gsiros/saga.
Contributions. We highlight our main contributions:
                                                                                                          II. BACKGROUND AND P ROBLEM S TATEMENT
  • We present SAGA, a Security Architecture for Governing                                     We provide background on agentic systems, their security
    Agentic systems, that enables users control and oversight                                requirements, and define our problem statement.
    of their LLM-enabled agents.
  • We propose a cryptographic mechanism based on access                                     A. Agentic AI Systems
    control tokens encrypted under shared agent keys that al-
                                                                                                Agentic AI systems represent an advancement in au-
    lows fine-grained control over inter-agent communication
                                                                                             tonomous systems, enabled by generative AI. These agents
    to balance security and performance considerations.
                                                                                             independently devise execution plans for tasks, leveraging
  • We use PROVERIF to formalize the secrecy of the SAGA
                                                                                             their underlying models for strategic planning and reasoning.
    token, authentication of communication between agents
                                                                                             As part of the planned steps for completing the assigned tasks,
    and the Provider, and authentication of communica-
                                                                                             agents might need to leverage additional tools installed on user
    tion between any two agents. We automatically prove
                                                                                             devices, interact with cloud services, or communicate with
    these properties with respect to an attacker that can
                                                                                             external agents running on other devices. LLM agents can
    observe, intercept, modify, replay, reorder, and synthesize
                                                                                             automate both professional tasks like scheduling and personal
    arbitrary messages on the network.
                                                                                             activities such as trip planning. For example, Alice’s calendar
  • We evaluate our system across several agentic tasks
                                                                                             agent might contact Bob’s calendar agent to arrange a meeting,
    (scheduling meetings, submitting expense reports, and
                                                                                             then use an email tool to send confirmations. We formulate the
    collaborative writing), multiple on-device and cloud LLM
                                                                                             following definitions and terminology that we use in the rest
    models, and agents placed in diverse geolocations to
                                                                                             of the paper.
    demonstrate the scalability of our design.
  • We discuss and evaluate the fault-tolerance and scalability                              Definition 1. A User owns one or more agents and is
    of the Provider. Our results demonstrate that making                                     responsible for assigning them tasks. A user has only one agent



                                                                                         2
instance running on each device (e.g., only one Calendar agent             We first address the fundamental requirement of creating
running on a particular device).                                        and managing agent identities while providing effective mech-
                                                                        anisms for agent discovery within the ecosystem. We design
Definition 2. An Agent is an autonomous software entity
                                                                        secure inter-agent communication protocols, which represents
using LLMs for decision making. Upon receiving a user query,
                                                                        a critical functionality of any agentic system, and address the
agents use LLMs for planning, store information in memory,
                                                                        challenge of how to limit the influence of adversarial agents on
and execute plans to complete assigned tasks. Agents can
                                                                        benign ones. We also aim to enable user control on an agent’s
access tools installed on user machines. Each agent operates
                                                                        entire lifecycle, including agent registration in the system,
under a specific user’s authority and may interact with other
                                                                        managing agent’s contacts, and agent’s deactivation at any
agents to fulfill complex objectives. Agents can be ”initiating”
                                                                        time, according to the user’s preferences and policies.
(starting communication) or ”receiving” (accepting communi-
                                                                           With the rapid evolution of agentic systems and emerging
cation) with other agents.
                                                                        regulations, our goal is to design a modular, extensible frame-
Definition 3. A task is defined as a sequence of actions that           work that can support new security properties with minimal
an Agent must plan and execute to achieve a User-defined                changes to core components.
goal. Actions might involve interacting with an LLM, invoking
other tools, or communicating with other agents.                                        III. S YSTEM A RCHITECTURE
                                                                           We begin by outlining the desirable goals for a secure
B. Requirements and Challenges for Secure Agentic Systems               agentic system (Section III-A), followed by an overview of our
   An OpenAI white paper [9] outlines several guidelines                proposed architecture SAGA (Section III-B). We also discuss
and open problems in designing secure agentic systems. Key              the system assumptions (Section III-C) and the considered
requirements include defining unique identities for AI agents           threat model (Section III-D).
with verification capabilities, providing secure mechanisms for
agents to discover and communicate with each other, and                 A. System Goals
enabling agents to make informed decisions about resource                  Although the requirements for secure agentic systems are
access and collaboration with other agents. Agentic systems             still evolving, we outline several desirable goals:
must also implement protections against adversarial or rogue            Agent lifecycle managed by users. An agent’s lifecycle
agents to limit their influence and prevent harm to benign              should be established by a user. The user installs the agent on
agents. Crucially, [9] advocates for users’ control and oversight       their device, registers it in the system, and retains the authority
throughout the lifecycle of LLM agents.                                 to terminate the agent at any time. Termination is performed
   Challenges: An agent management system must address                  by deactivating the agent and preventing other agents from
three key challenges: (1) discovery—how agents discover each            locating it in the ecosystem.
other; (2) secure communication—how agents communicate
with each other; and (3) remote access control—which agents             Agent access controlled by user policies. While LLM agents
are allowed to interact with a specific agent, for what tasks,          can autonomously decide to contact other agents to perform
and for how long. While inter-agent communication should be             user-assigned tasks, communication between agents should be
performed automatically by agents, access control and agent             controlled by user-defined access control policies.
discovery should remain under the user’s control for better se-         Limited trust. Agents should have limited trust in other
curity. Existing solutions address only one of these challenges         third-parties in the system, including any centralized service
and are not specifically designed for agents. For example,              provider or other agents.
secure messaging protocols like Signal or Matrix provide peer           Scalability. Design the system to efficiently manage a large
discovery and secure communication, but lack fine-grained               number of agents with minimal performance overhead.
access control; protocols like TLS or QUIC enable secure
                                                                        Limited influence on other agents. An agent can control
communication, but offer no agent discovery or fine-grained
                                                                        only its own participation in the system and cannot arbitrarily
access control; and systems like Kerberos provide high-
                                                                        remove other agents from the ecosystem.
granularity access control, but lack secure communication
capabilities. The recent A2A protocol [13] is the only agent-           Limited vulnerability window. It is crucial to limit the
specific work we are aware of that ensures communication                vulnerability window when compromised agents are still active
between agents, but provides no security guarantees or access           in the system. The length of this window can be controlled by
control functionality.                                                  cryptographic mechanisms and depends on factors such as the
                                                                        agent’s communication patterns, the nature of the task, and the
C. Problem Statement                                                    sensitivity of the exchanged data.
  Our goal is to design a system that addresses all the                 Maintain system utility. We aim to preserve the utility of
above challenges by providing agent discovery, secure agent             the system, as measured by task completion, without compro-
communication, and fine-grained access control to the services          mising system security. Additionally, the framework should be
provided by an agent, while allowing users to retain control            agnostic to various agent implementations and LLM models
over the management of their agents.                                    that serve as the backbone.



                                                                    3
B. Architecture Overview                                                maintains the secret part. We then use the Diffie-Hellman key
                                                                        exchange protocol, in which the initiating agent contributes
   We provide an overview of our SAGA system architecture               the access control key, and the receiving agent the OTKs as
in Figure 1. A critical consideration in designing a secure             public keys. The receiving agent encrypts the Access Control
agentic framework is the mechanism for agent discovery. The             Token under the derived shared key. The token includes an
implementation of an agent registry facilitates this discovery          expiration timestamp and a limit on the number of permitted
process, with architectural options ranging from centralized            requests. The token is reused for inter-agent communication,
to distributed registry models. In our design, we choose to             without involving the Provider. When the token expires, a
use a centralized registry, maintained by an entity called              new one is created after the initiating agent obtains another
Provider. The Provider manages agent and user identi-                   OTK from the Provider. This design balances the security
ties, ensures authentication, and facilitates controlled commu-         and performance overhead in the system, by allowing users
nication establishment between agents.                                  to tune access to their agents through the number of keys
   To ensure user oversight over an agent’s lifecycle, we del-          they register and the lifetime of Access Control Tokens. Note
egate the agent registration process to users themselves, with          that the protocol is asymmetric, as access control is enforced
the Provider maintaining the agent information. Users must              for receiving agents, according to user-specified policies for
be registered in the system and authenticate before registering         initiating agents.
any agents and retain the ability to deactivate their agents, for          Below, we outline the main components of our system;
example as a protective measure when abuse is detected. Each            protocol details are provided in Section IV.
agent is assigned a unique identifier, linked to the user and
                                                                        User Registration (Section IV-B). Users must register with
the device it is installed on. The Provider thus maintains
                                                                        the Provider using a persistent identity mechanism, such
the User Registry (DU ) holding user identity records,
                                                                        as OpenID Connect [14]. Upon successful registration, users
and the Agent Registry (DA ) storing agent metadata,
                                                                        authenticate to the Provider and provision agents for par-
cryptographic credentials, endpoint information, and agent
                                                                        ticipation in the SAGA ecosystem.
communication policies.
   While communication between agents can be implemented                Agent Registration (Section IV-C). A user registers its
using standard secure protocols such as TLS, we would like              agents with the Provider. During registration, the user
the ability to enforce limits on agent access, controlled by            generates cryptographic keys for its agents, including TLS
users. Governed by the same principle of users managing                 certificates and access control keys. The user also signs the
access to their agents, each user can specify an Access                 agent metadata, such as hostname, port, and device identifiers,
Contact Policy for each agent defining which agents are                 to bind it to its identity and specific device. Additionally, the
permitted to initiate contact. To enable fine-grained access            Provider signs the agent’s metadata.
control and limit the vulnerability window, access to agents            Agent Management (Section IV-D). The Provider enables
needs to be cryptographically bounded. For scalability and              users to define and update an Agent Contact Policy for each
reduced reliance on the Provider, once an agent obtains the             of their agents, which governs the policy for permissible
necessary connection details for another agent, all subsequent          incoming communication. This policy allows users to restrict
communication should proceed directly, without Provider                 which other agents can initiate contact with their agent, and to
involvement.                                                            impose access control constraints. The Provider enforces
   An important design consideration is how to manage agent             these policies during initial contact requests, ensuring that
access control in a fine-grained manner while reducing the              agent interactions are governed by user-defined rules. Users
burden on the Provider. Towards this goal, each agent                   can deactivate their own agents at any time, but cannot
registers a number of public one-time keys (OTKs) with                  deactivate agents owned by others.
different quotas for each initiating agent (and locally stores          Agent Communication (Section IV-E). To initiate contact
the corresponding secret information linked to these OTKs).             with another agent, the initiating agent queries the Provider
In principle, an OTK could be used only once for an inter-              with the receiving agent’s identifier. The Provider responds
agent interaction, but that would require generating and storing        with metadata, including the receiving agent’s device, IP
a large number of OTKs, presenting significant operational              address, and a one-time key (OTK) for access control. Sub-
overhead. We extend the lifetime of these one-time keys                 sequently, the initiating agent establishes a shared key with
by the receiving agent generating an Access Control Token               the receiving agent using the Diffie-Hellman protocol. The
that is encrypted using a dynamically derived shared key                receiving agent generates an access control token, encrypted
between the agents. The shared key must be unique to each               under the shared key, which is included in any communication
initiating–receiving agent pair and derivable only by those             by the initiating agent. When a token expires or reaches its
two agents. To support the shared key computation, each                 request limit, the initiating agent obtains a new OTK from
agent maintains a long-term Access Control Key, which serves            the Provider. Note that the Provider does not mediate
as the basis for deriving the shared key and binding it to              inter-agent communication, but it is critical in enforcing each
the specific agent pair. The public component of the access             receiving agent’s Access Control Policy by distributing OTKs
control key is stored in the Agent Registry, while each agent           to initiating agents.



                                                                    4
C. System Assumptions                                                   C3: Adversaries may instruct an agent to self-replicate on the
   The correctness and security guarantees of SAGA rely on              same device or on another user’s device without registering the
a set of clearly defined system assumptions, outlned below.             child agent with the Provider. Prior work has demonstrated
                                                                        such self-replication of agents [15]. The parent agent can share
Secure User Authentication and Human Verification. We                   TLS keys, access control keys, and existing access control
assume that the Provider implements a robust user authen-               tokens with the child agent.
tication mechanism (e.g., OpenID Connect) and that user cre-
                                                                        C4: An adversarial agent may share its TLS public keys,
dentials are not compromised. Crucially, we assume that agent
                                                                        access control keys, and access control tokens with another
registration is restricted to authenticated human users, enforced
                                                                        adversary-controlled agent, enabling communication with a
through human verification during user account creation. This
                                                                        benign victim agent.
verification process is delegated to a trusted external identity
                                                                        C5: An adversary could attempt to mount a Sybil attack, by
service, which certifies the user’s human status on behalf of
                                                                        creating agents with multiple identities.
the Provider.
                                                                        C6: An adversary may overhear, intercept, and synthesize any
Agent Identity Control. We assume that attackers can create             message, and is only limited by the computational hardness
and register agents under their own identities but cannot imper-        constraints of the employed cryptographic primitives.
sonate other users. That is, while adversaries may instantiate
and operate malicious agents, they cannot register agents under                    IV. SAGA P ROTOCOL S PECIFICATION
the identity of a benign user.
                                                                           In this section, we begin with a description of the cryp-
Public IP Addressing. All agents and providers are assumed              tographic primitives involved in our protocol, followed by a
to operate under globally routable, public IP addresses. This           description of the key protocols involved in SAGA: user regis-
design avoids NAT traversal and local discovery, assuming that          tration (Section IV-B), agent registration (Section IV-C), agent
agents are reachable at their registered endpoints.                     management (Section IV-D), and inter-agent communication
Cryptographic Soundness. We assume that all cryptographic               (Section IV-E).
primitives used by the system—signature schemes, key ex-
change protocols, encryption schemes, and key derivation                A. Cryptographic Primitives and Notation
functions—are secure. Secret keys are assumed to remain                   We leverage the following cryptographic primitives:
confidential and outside adversarial control.
                                                                        Signature schemes. A signature scheme consists of three
Secure Channels. All communication, both between agents
                                                                        algorithms: KeyGen() – a key generation function that outputs
and between agents and the Provider, is protected by
                                                                        a (public, private) signing key pair (PK, SK),
TLS. We assume that TLS provides confidentiality, integrity,
                                                                           SignSK (m) – a signing algorithm that outputs a signature σ
and authenticity against network-level adversaries performing
                                                                        on message m using SK, and VerifyPK (m, σ) – an algorithm
message tampering, eavesdropping, and replay.
                                                                        that verifies if the signature σ on message m is correct. We
Network Protections. We assume that the network infras-                 assume that the signature scheme is Existential Unforgeable
tructure enforces basic protections against denial-of-service           under Chosen Message Attack [16], such as ECDSA [17] and
attacks and packet flooding.                                            Ed25519 [18]. A certificate generation function GenCertX (m)
                                                                        involves entity X creating a certificate for content m as:
D. Threat Model
                                                                        GenCertX (m) = ⟨m, SignSKX (m)⟩
   The Provider is expected to adhere to the SAGA protocol
                                                                        Hash function. We use a collision-resistant hash function H(·),
logic, including enforcing contact policies, issuing keys, and
                                                                        such as SHA-256 or SHA-3 [19].
performing registry operations. However, it may be honest-
but-curious: capable of observing agent metadata and traffic            Diffie-Hellman Key Exchange. The Diffie-Hellman Key Ex-
patterns without actively attempting to subvert the protocol.           change protocol [16] is a cryptographic method that allows two
The user and agent registries are assumed to be securely stored         parties to establish a shared secret key. Each party generates
and not vulnerable to adversarial control or tampering. We              a (secret, public) key pair, and exchanges with the other
consider several adversarial capabilities:                              party the public component. We denote by DH the function
C1: Adversaries might create agents and register them with the          that takes as input the secret key of one party and public
Provider. These adversarial agents could deviate from the               key of the other party and computes the shared secret key
protocol when communicating with other agents. They could               DH(x, g y ) = DH(y, g x ) = g xy mod p. The security of
also add themselves to the contact policy of benign agents by           Diffie-Hellman is based on the Computational Diffie-Hellman
performing social engineering on users.                                 (CDH) assumption.
C2: A legitimate agent registered with the Provider could               Key Derivation Function. A Key Derivation Function (KDF) is
be compromised by an adversary. This attack could occur                 a cryptographic algorithm that derives one or more secret keys
when agents interact with external resources, such as websites,         from a master secret. We use the HMAC-based Extract-and-
or tools installed on user devices, which might trigger a               Expand Key Derivation Function (HKDF) [20] with SHA-256
compromise.                                                             as the underlying hash function.



                                                                    5
Notation. We introduce formal notation throughout the proto-                 C. Agent Registration by User
col specification. For convenience, Table I provides a summary                  The agent registration process ensures that each agent is
of all symbols used.                                                         cryptographically bound to its user and a specific user’s device.
                                                                             The cryptographic information generated by a user for its
     Symbol              Description
                                                                             agents is stored by the Provider and subsequently used
     PK, SK              Public/private signing keys                         to establish secure agent communication mediated by the
     Cert                Certificate issued by CA
                                                                             Provider. The following protocol is executed by user U
     uidU                User identifier                                     to register their agent A (shown in Figure 8, Appendix).
     aidA                Agent A identifier
     EDA                 Agent A endpoint descriptor                         1) Generating agent information. The user selects an iden-
     (PKA , SKA )        Agent A public/private TLS credentials                  tifier nameA for the agent, forming a unique agent ID in
     (PACA , SACA )      Agent A public/private access control keys
     (OTKiA , SOTKiA )   Agent A one-time public/private keys
                                                                                 combination with their username: aidA = uidU :nameA .
     CPA                 Contact policy of agent A                               The user specifies the agent’s device name deviceA and
     token               Access control token                                    networking details IPA and portA . These comprise the
      Y
     σX                  Entity Y-issued signature regarding entity X.           agent’s “endpoint descriptor”:
     DU                  Provider’s user registry                                             EDA = ⟨deviceA , IPA , portA ⟩
     DA                  Provider’s agent registry
       TABLE I: Notation used in the SAGA protocol.                          2) Generating cryptographic keys. The user generates the
                                                                                following keys for the agent:
                                                                                • TLS credentials (PKA , SKA ) to establish secure com-
B. User Registration                                                               munication channels with other agents and a signed
   The first step for any user seeking to deploy agents is to                      certificate by the CA:
register with the Provider. This process establishes the
user’s identity and enables them to link future agents to                                    CertA = GenCertSKCA (⟨aidA , PKA ⟩)
their identity and manage them securely. The user obtains a                     • A public-private key pair: (PACA , SACA ) for access
certificate signed by an external certificate authority CA on                     control. These long-term keys are used for the receiving
their public key, sent to the Provider. We assume that the                        agent to derive a shared key with the initiating agent
user can establish a TLS connection with the Provider and                         for encrypting the access control token in inter-agent
that the provider can verify the user’s identity with the help                    communication (Section IV-E).
of an external service such as OpenIDConnect. The protocol                      • A batch of N one-time public and secret key pairs
follows these steps (also shown in Figure 7):                                     (OTK1A , SOTK1A ), . . . , (OTKNA , SOTKNA ), used for deriving
1) User Account Setup. The user selects a public                                  tokens for controlling access to the agent. Each public
    identifier uidU corresponding to their email address,                         one-time key is signed by the user:
    e.g., uidU = ‘alice@domain.com’, and a secret                                              U
                                                                                                                      ⟨aidA , OTKiA ⟩
                                                                                                                                      
                                                                                              σOTK  i = SignSK
    passphrase passwd to authenticate to the Provider.                                                            U

2) User signature key generation: The user generates a sig-                     The user also signs the agent’s device and networking
    nature key pair (PKU , SKU ) for signing agent information.                 information, along with its long-term keys:
    The user contacts CA to generate its certificate
    CertU = GenCertSKCA (⟨uidU , PKU ⟩), and shares it                               σAU = SignSKU (⟨aidA , EDA , PKA , PACA , PKProv ⟩)
    with the Provider.                                                          The inclusion of PKProv in the signature indicates that the
3) Connection establishment. The user obtains the                               agent is registered with the specified Provider.
    Provider’s certificate and public key PKProv from                        3) Specifying the contact policy: The user specifies the
    the CA and verifies them. A TLS session is established                      agent’s contact policy CPA (discussed in Section IV-D).
    between the user and the Provider.                                       4) User authentication to Provider. The user establishes
4) Sending user information. The user submits                                   a secure TLS connection with the Provider, and au-
    (uidU , passwd) and CertU to the Provider.                                  thenticates by providing credentials ⟨uidU , passwd⟩. The
5) User identity verification. The Provider verifies the                        Provider verifies the credentials and proceeds if suc-
    user’s identity using an external service S (see Sec-                       cessful.
    tion III-C). If verification is successful and the account               5) Registration submission. The user submits to the
    does not exist, the Provider finalizes the registration.                    Provider: the agent’s information (aidA , EDA , CPA ),
6) User        account      storage      and     confirmation:                  the TLS certificate CertA , the public access control and
    The      Provider        updates    the    user     registry:               one-time keys PACA , {OTK1A , ..., OTKNA }, and signatures
    DU [uidU ] = ⟨H(passwd), CertU ⟩ and sends a                                σAU , σOTK
                                                                                         U
                                                                                           i   for i ∈ [1, N ].
    confirmation to the user.                                                   The agent stores locally all the private keys corresponding
After the user registration is completed successfully, the user                 to the public keys submitted to the provider: (SKA , SACA ,
can proceed to register its agents with the Provider.                           {SOTK1A , ..., SOTKNA }).



                                                                         6
6) Provider verification. The Provider processes the reg-                // Agent C's Contact Policy
   istration request by checking that aidA and EDA are                   [
                                                                           {
   globally unique, and verifying CertA and signatures:                       "agents": "alice@company.com:calendar_agent",
                                                                              "budget": 15
         VerifyPKU (⟨aidA , EDA , PKA , PACA , PKProv ⟩, σAU )             },
                                                                           {
                 VerifyPKU (⟨aidA , OTKiA ⟩, σOTK
                                              U
                                                  i)
                                                                              "agents": "*@company.com:calendar_agent",
                                                                              "budget": 10
                                                                           },
7) Completion. Upon successful verification, the Provider                  {
   stores in the agent registry the agent’s metadata MA , the                 "agents": "bob@mail.com:*",
                                                                              "budget": 100
   contact policy CPA , the agent’s signatures σAU and σOTK
                                                        U
                                                            i,             }
   along with uidU to associate the agent A with user U:                 ]

          MA = {EDA , CertA , PACA , OTKiA , i ∈ [1, N ]}                Listing 1: Example contact policy for an agent. More specific
          DA [aidA ] = ⟨uidU , MA , CPA , σAU , σOTK
                                                 U
                                                     i⟩
                                                                         patterns take precedence over general ones.
   The Provider then signs the agent A’s information
      σAP rov = SignSKProv ⟨aidA , CertA , EDA , PACA , σA
                                                         U
                                                                         where r∗ is the most specific rule among all rules R in CPA
                                                                 
                                                           ⟩
                                                                         that match aidB , and B(r∗ ) corresponds to the budget for rule
  and returns it as confirmation to the user. The user stores
                                                                         r∗ indicated in CPA . The distinction for R = ∅ helps the user
  this signature, which it uses when initiating agent commu-
                                                                         distinguish between no match in policy and an expired OTK
  nication (Section IV-E).
                                                                         budget.
The agent A is now officially registered and can securely
                                                                            2) One-Time Key Generation: To control communication
communicate within the ecosystem.
                                                                         to registered agents, the Provider facilitates the distribution
D. Agent Management                                                      of OTKs: one-time keys generated and uploaded by each user
   Agent management in SAGA involves managing access                     for their agents. Each OTK is consumed when an initiating
control polices, policy updates, and cryptographic key man-              agent contacts the Provider to obtain information for a
agement.                                                                 receiving agent. OTKs are defined for receiving agents, as
                                                                         the protocol is asymmetric. Additionally, the Provider
Access control management. There are two fundamental
                                                                         maintains the number of OTKs remaining for a particular agent
capabilities in SAGA for managing access control: (1) specifi-
                                                                         communicating with another agent. While it might be possible
cation and enforcement of the Agent Contact Policy (CP), and
                                                                         for the initiating agent to receive multiple OTKs from the
(2) provisioning of fresh One-Time Keys (OTK) to facilitate
                                                                         Provider, thereby reducing the number of times the agent
user-controlled communication.
                                                                         must contact the Provider, we chose a more conservative
   1) Agent Contact Policy: In SAGA, each agent is associated
                                                                         design. In our approach, the agent receives only one OTK per
with a contact policy CP that specifies which initiating agents
                                                                         request to limit the vulnerability window in case the agent is
are authorized to establish contact. This policy is defined by
                                                                         compromised.
the user when registering their agent, and is enforced by the
Provider during contact resolution. CP consists of a set of                 When an initiating agent B queries the Provider to
declarative rules, along with the number of OTKs that should             contact a recipient agent A, the Provider first verifies that
be allotted to an agent that matches that rule. These rules may          the initiating agent satisfies A’s Agent Contact Policy (CPA ),
use pattern matching over agent identifiers to allow flexible yet        as detailed above. If this is the first time B is contacting A,
controlled specification of acceptable contacts. For instance,           the Provider creates a counter CounterOTK [aidA ][aidB ] to
the rule ("*@company.com:email_agent", 10) per-                          keep track of the number of remaining OTKs, and initializes
mits any email-handling agent from a specified domain to                 it with BudgetOTK (aidA , aidB ).
initiate contact and be allotted at most 10 OTKs.                           If the policy check succeeds and a valid OTK is available
   If multiple rules match, the one with the highest                     (indicated by a positive value for CounterOTK [aidA ][aidB ]),
specificity is selected. For instance, in Listing 1, agent               the Provider returns an OTK to the initiating agent (along
alice@company.com:calendar_agent attempts to                             with the recipient’s metadata and its signature, discussed in
contact another agent. The agent’s identifier matches the top            Section IV-E) and decreases the counter by one.
three patterns, but the first rule is the most specific and                 Obtaining an OTK at this stage may fail due to: (a) exhaus-
therefore determines the OTK budget, resulting in 15 OTKs.               tion of aidA ’s overall OTK pool, or (b) depletion of aidB ’s
   Formally, for a receiving agent A with contact policy CPA             OTK quota as defined by CPA . The user of agent A can update
and an initiating agent B with identifier aidB , the number of           the contact policy and refresh the OTKs at any time.
OTKs issued is defined as:                                               Policy Updates and Revocation. Users can dynamically
                                                                         update their agents’ contact policies via the Provider in-
                                    (
                                      −1       if R = ∅
        BudgetOTK (aidA , aidB ) =                       ,               terface. Updates may include adding rules (e.g., to onboard
                                      B(r∗ ) if R ̸= ∅                   collaborators) or removing them (e.g., to revoke access),



                                                                     7
allowing policies to adapt as trust relationships shift or threats          key PKU1 . B also verifies the signatures on agent’s A
emerge.                                                                     information and the received OTK as follows:
   It is important to allow users to block contact from specific
agents, as they might detect abusive behavior. To block specific                 VerifyPKU1 (⟨aidA , EDA , PKA , PACA , PKProv ⟩, σAU )
agents, a receiving agent can update its contact policy with
a rule that assigns a B(·) score of −1. The modified CP is                               VerifyPKU1 (⟨aidA , OTKiA , ⟩, σOTK
                                                                                                                         U
                                                                                                                             i)

then pushed to the Provider. Alternatively, to completely                4) Establishing a TLS connection between agents: B initi-
disable incoming contact, a user can request the Provider                   ates a TLS connection with A, and both agents verify each
to deactivate their agent at any time. This functionality is                other’s certificates (CertA , CertB ).
motivated by our design goal of giving the user full control             5) Token request sent: B sends A its information and a
over their agent’s entire lifecycle. Crucially, we do not allow             signature σBP rov from the Provider (generated during
users the ability to deactivate agents registered by other users,           agent registration: step 7), along with one-time key OTKiA ,
as they should control only their own agents.                               requesting access.
Cryptographic key management. Cryptographic keys for                     6) Token request received: A verifies U2’s certificate, as well
agents should be managed by users according to best prac-                   as σBP rov :
tice principles for key management and key rotation [21].
In particular, users should periodically rotate their agents’                  VerifyPKProv (⟨aidB , CertB , EDB , PACB , σBU2 ⟩, σBP rov )
TLS key and access control keys. Best practices should also                 If OTKiA is valid, both agents perform a Diffie-Hellman
be followed by the Provider for user authentication and                     (DH) key exchange protocol to derive a shared key:
password management [22].
                                                                             DHA = DH(SOTKiA , PACB ),         DHB = DH(SACB , OTKiA )
E. Inter-Agent Communication
   We describe how two registered agents can communicate                               SDHK = KDF (DHA ) = KDF (DHB )
with each other securely, while respecting the Access Contact
                                                                         7) Token generation: A creates the access token with a
Policy defined by users for their agents.                                                                    $
   When an agent B (initiating agent) wants to contact agent A              randomly generated nonce (N ←   − R), issue (Tissued ) and
(receiving agent), it first queries the Provider to verify A’s              expiration (Texpire ) timestamps, the maximum number of
registration. If permitted by A’s contact policy, B receives A’s            requests linked to this token (Qmax ), and B’s access control
metadata and a one-time key (OTK) from the Provider. This                   key (PACB ):
OTK is used by both agents to derive a shared key, which the                  token = EncSDHK (⟨N, Tissued , Texpire , Qmax , PACB ⟩).
receiving agent A will use to encrypt an access control token
(ACT) for B. The ACT is scoped to a specific task, but the                  A stores the token and sends it to B.
granularity of tokens can be adjusted further if desired. The            8) Inter-Agent communication: B receives the token and
token will have limited validity, as well as a limit on the total           initiates the conversation to complete its task. For each sub-
number of requests.                                                         sequent request to A, B attaches the token. Upon receiving
   The following steps outline the agent communication pro-                 a request, A verifies that the token was issued for B (not for
tocol involving initiating agent B contacting receiving agent A             another agent), has not expired, and has not exceeded its
to obtain an access control token (shown in Figure 9). This                 usage quota. Once a task is deemed completed, the token
protocol runs either the first time B contacts A, or when tokens            is discarded by both parties.
have expired or exceeded their usage limits.                             Token reuse. Once an Agent obtains a token, it can reuse
1) Establishing a TLS connection with the Provider:                      it as long as it remains valid and hasn’t exceeded its request
    This step follows a standard TLS session establishment               limit. If B holds a valid token for A, it can skip ahead to step 8
    between B and the Provider.                                          to initiate secure communication. If the agents’ existing TLS
2) Receiving agent information retrieval: B requests per-                session is reset, the agents will establish a new TLS session
    mission to contact A by specifying their identity (aidB )            (step 1) and proceed directly to agent communication (step
    and the identity of the receiving agent (aidA ). The                 8). The expiration time and request limit in the token offer
    Provider verifies that B is in A’s contact policy                    a balance between security and performance considerations.
    and has sufficient OTKs allotted to it (by making sure               A larger number of requests Qmax reduces the overhead of
    CounterOTK [aidA ][aidB ] > 0). It returns A’s access in-            contacting the Provider to obtain OTKs, but increases the
    formation: user’s certificate CertU1 , agent’s device and            potential exposure in case an agent is compromised.
    network information (aidA , EDA ), agent’s TLS and access
    control keys (CertA , PACA ) and a signed one-time key               F. Formal Protocol Analysis
    OTKiA , σOTK
             U1
                 i . Subsequently, the Provider decrements the             We formalized SAGA using the state-of-the-art symbolic
    counter CounterOTK [aidA ][aidB ] by one.                            cryptographic analysis tool, P ROV ERIF, to reason about cryp-
3) Receiving agent information verification: B first verifies            tographic attackers [23]. Our P ROV ERIF model precisely
    A’s user’s certificate CertU1 including the user’s public            captures the SAGA protocol description, using standard



                                                                     8
P ROV ERIF protocol modeling techniques and assumptions.                 design, a quorum of servers is required to participate in each
Within our P ROV ERIF model of SAGA, we encoded formal                   operation ensuring that a majority of honest servers make the
properties specifying the secrecy of the SAGA token, authen-             decision. Such a system can tolerate f compromised servers
tication of communication between agents and the provider,               out of 3f + 1 participating servers. An alternative, more
and authentication of communication between any two agents.              lightweight design is using fault-tolerant algorithms (RAFT
Using P ROV ERIF’s automated reasoning capabilities, we au-              or Paxos), augmented with proactive auditing mechanisms to
tomatically proved each of the afformentioned properties with            detect server compromises.
respect to an attacker that can observe, intercept, modify,                 Scalability. Finally, the scalability of the system can
replay, reorder, and synthesize arbitrary messages on the                be elastically increased by using a standard technique in
network. This directly corresponds to the Dolev-Yao symbolic             databases [28]–[30] called sharding [31], [32]. In this approach
cryptographic protocol model [23]. For details on formal                 the agent registry is partitioned across several entities called
verification, see Appendix D.                                            sharders, and we can partition based on the space of agent
                                                                         ID. Each sharder can be made fault-tolerant with a RAFT
      V. E XTENSIONS TO THE SAGA ARCHITECTURE
                                                                         cluster, and a set of load-balancers forwarding the requests
   We discuss several extensions to SAGA to enable fault                 for different agent entries to the corresponding sharder. We
tolerance, scalability and resilience to server compromise               present scalability results in Section VI-D.
in Section V-A, and describe the integration with the A2A                   Federation. The Provider service can be further decen-
protocol in Section V-B.                                                 tralized by using federation, where several organizations each
                                                                         managing their own provider, participate in the protocol. Sim-
A. Provider Architecture Design
                                                                         ilar to cross-realm Kerberos [33], multiple providers establish
   In our proposed architecture, the Provider is trusted, a              trust relationships via shared cryptographic keys or certificates,
model similar to that in existing systems as Active Directory            enabling cross-domain agent authentication where agents from
 [24] (based on Kerberos). We discuss below how the design               one provider can securely communicate with agents from other
can be augmented to enable fault-tolerance, resilience to                providers. This model allows organizations to maintain control
attacks and server compromises, and scalability.                         over their agent registries and policies while enabling inter-
   Fault-tolerance. The centralized Provider design we                   organizational communication, with each provider validating
propose can be made fault-tolerant by using standard dis-                its local agents during cross-boundary interactions.
tributed systems techniques. Specifically, the Provider
functionality can be implemented as a RAFT [25] or
                                                                         B. Integration with the A2A Protocol
Paxos [26] cluster, where the agent registry is replicated across
the RAFT nodes. Operations such as agent registration, policy               We discuss the integration of SAGA with Google’s
update, and OTK retrieval are submitted to the leader of the             Agent2Agent (A2A) protocol [13]. A2A defines an agentic
RAFT cluster. Such systems are provisioned to tolerate a                 framework where AI agents advertise public metadata and
certain number of failures, for example typical deployments              establish secure communication with other agents. While
consist of 5 servers tolerating 2 faulty servers. We present             A2A defines a unified interface for structured task exchange
fault tolerance results in Section VI-D.                                 via “agent cards”, it lacks support for authentication, access
   Protection against denial-of-service (DoS). Additionally,             control, and agent governance. Our integration bridges this gap
protection against DoS can be achieved by using rate limiters            by protecting agent cards with SAGA access control policies
that control the volume and frequency of incoming requests,              and by encapsulating A2A messages within SAGA’s secure
preventing attackers from overwhelming server resources with             communication layer. We highlight below the changes that
excessive traffic. Advanced rate limiters can detect abnormal            enable integration with SAGA.
traffic patterns, adapt their restrictions based on current server          The Provider stores agent cards in the agent registry as
load, and implement tiered responses like introducing delays             part of each agent’s metadata entry as per Step 7 of Agent
rather than complete blocking. While particularly effective              Registration in Section IV-C.
against single-source attacks, rate limiters serve as a crucial
first line of defense that maintains system availability during              DA [aidA ] = ⟨uidU , MA , CPA , A2ACardA , σAU , σOTK
                                                                                                                               U
                                                                                                                                   i⟩
attacks, though they work best when combined with other pro-
tective measures like firewalls and DDoS protection services             Unlike A2A’s recommended deployment via public URLs,
for comprehensive security against sophisticated distributed             SAGA protects these cards under user-specified access control
attacks.                                                                 policies. This ensures that only authorized agents may retrieve
   Resilience to compromised servers. A compromised                      the agent cards. Additionally, the integrity of the agent cards
Provider might refuse agent registration, refuse to forward              are protected with user signatures (Step 2, Section IV-C).
agent metadata, register malicious agents, or not follow agent
policies. The Provider can be made resilient to these                      σAU = SignSKU (⟨aidA , EDA , PKA , PACA , PKProv , A2ACardA ⟩)
types of attacks by implementing it as a Byzantine-resilient
service using existing protocols such as PBFT [27]. In this              For inter-agent communication, the standard message in the



                                                                     9
msg field is wrapped into an A2A Request during Step 8                   Key Management Overhead. SAGA relies on three classes
of Section IV-E.                                                         of cryptographic keys, each with distinct lifetimes and ro-
                                                                         tation patterns: short-term one-time keys (OTK), medium-
     ⟨token, msg⟩ → ⟨token, A2ARequest(msg)⟩                             term access control keys (PAC, SAC), and long-term identity
In addition to the message content, A2A Requests include                 keys (PK, SK). OTKs are ephemeral and rotated frequently
internal metadata such as task and message IDs, and the                  once consumed for the derivation of access control tokens.
content type (e.g., text, image). Before forwarding the request          On the other hand, access control keys are medium-term,
to the agent’s A2A stack, the SAGA stack verifies the token              typically rotated on a weekly or biweekly basis to balance
for authenticity, freshness, and contact authorization as per            security with operational stability. Long-term identity keys are
Step 8 of Section IV-E. If any check fails, the message                  rotated infrequently, commonly every 30 to 90 days, following
is discarded and never reaches the A2A layer, effectively                established key management guidelines [21].
preventing unauthorized task execution.
                                                                                                        10
   SAGA integrates with A2A through minimal changes that




                                                                         Computational Overhead (sec)
                                                                                                                                                           Number of OTKs
preserve the protocol’s functionality, while augmenting its                                              8                                                         10
security. The integration remains agnostic to agent design and                                                                                                     100
                                                                                                         6                                                         1000
task semantics, enabling secure, interoperable agent commu-
nication controlled by user policies.                                                                    4

                      VI. E VALUATION                                                                    2

   To evaluate SAGA, we implement the full protocol (VI-A),                                              0
                                                                                                         every 5 min   10 min       15 min    30 min       1 hr       8 hrs
measure its overhead in VI-B, and evaluate it on three agentic                                                                  OTK Generation Frequency
tasks in VI-C. We measure the cost of fault tolerance and
                                                                         Fig. 2: Computational overhead of OTK generation for the user,
protocol scalability in VI-D. In Appendix E we implement 8
                                                                         as a function of frequency and key-chain length. Even with
attackers within the capabilities defined in the threat model
                                                                         frequent generation (every 5 minutes) and long key-chains
(III-D) and evaluate SAGA’s resilience.
                                                                         (1000 OTKs), the total cost remains low.
A. Implementation
                                                                            Figure 2 measures the overhead for OTK generation at
   The Provider is implemented as an HTTPS service. Inter-               the user, showing that even under frequent generation (1000
agent communication is conducted over TLS configured with                OTKs every 5 minutes over an 8-hour period) the total com-
mutual authentication, with protocol-level authentication and            putational cost remains under 10 seconds for a single user.
encryption enforced via ephemeral session keys. Our frame-               The computational cost at the Provider (validation and
work is agnostic to the underlying LLM-agent implementation.             storage of the OTKs) does not exceed 0.5 seconds under the
This design enables seamless integration with arbitrary agent            same conditions (1000 OTKs/5min). In contrast, both access
implementations. We also implemented the integration of                  control and identity key pairs require only 0.11 milliseconds to
SAGA with A2A, described in V-B.                                         generate on commodity hardware, and due to their infrequent
   All cryptographic operations in the protocol are built on             rotation, their cost is effectively amortized.
Curve25519 [34]. Both long-term and ephemeral keys are                      Figure 3 reports the total cost of deriving access control
generated using the X25519 elliptic-curve Diffie-Hellman                 tokens with different configurable lifetimes (L) from OTKs
(ECDH) [35] scheme, using 256-bit shared secrets. Certificates           for a single initiating agent with 1, 10 and 100 receiving
adhere to the X.509 PKI standard [36] and are issued by                  agents. The process includes a Diffie-Hellman handshake,
an internal certificate authority (CA) deployed as part of the           the encryption and decryption (validation) of the token as
provider. All digital signatures and key derivation steps utilize        described in Section IV-E. Even for very short lifetimes (1
the SHA256 hash function [19].                                           minute), the total cost of derivation of 144K tokens is just
   For LLM agents, we experimented with a local Qwen-2.5                 below 400 seconds over the span of 1 day for a single agent.
[37] 72B model running on NVIDIA H100, as well as two                       We conclude that a longer lifetime reduces reliance on the
OpenAI models hosted in the cloud and accessed via API.                  Provider but increases the window for compromised agents
                                                                         to operate without interruption. Shorter lifetimes mitigate secu-
B. Overhead Evaluation                                                   rity risks by requiring more frequent cryptographic validation,
Cryptographic Overhead. We begin with measuring the                      at the expense of additional overhead.
cryptographic overhead of core protocol operations at the                   Importantly, all aforementioned overheads are very small
user, Provider, and agents. These costs cover cryptographic              compared to the total task execution times (Section VI-C),
primitives such as hashing, key generation, signing, verifica-           which typically last at least a few minutes, depending on task
tion, and Diffie-Hellman key exchange. As shown in Table III             complexity and LLM backend latency.
(Appendix B) most operations are lightweight, on the order of            Protocol Overhead. We measure the overhead introduced by
several ms.                                                              SAGA’s access control and provider coordination mechanisms



                                                                    10
                                 400




Computational Overhead (sec)
                                                                                                       Receiving Agents                                       175
                                                                                                                                                                                                          Agent Location
                                 300                                                                             1
                                                                                                                                                              150                                               US-West




                                                                                                                                    Amortized Overhead (ms)
                                                                                                                 10
                                 200                                                                                                                                                                            US-East
                                                                                                                 100                                          125                                               EU
                                 100                                                                                                                                                                            Asia
                                                                                                                                                              100
                                                  0
                                                          1 min     3 min    6 min   12 min    1 hr      8 hrs       1 day                                     75
                                                                               Token Lifetime (L)
                                                                                                                                                               50
Fig. 3: Computational overhead of access control token deriva-
tion between one initiating agent and 1, 10 and 100 receiving                                                                                                  25

agents, varying by token lifetime (L). Even for short lifetimes                                                                                                 0
(1 minute), the total cost remains low.                                                                                                                             1              10               20                30
                                                                                                                                                                        Maximum number of requests per token (Qmax)

(Section VI-B). Specifically, we analyze the overhead incurred                                                                    Fig. 5: Amortized protocol overhead per request c̄proto (m) as a
by an initiating agent B issuing m requests to a receiving                                                                        function of maximum number of requests token is reused. We
agent A. This includes a network component for establishing                                                                       measure the overhead for several geographic locations for the
secure communication, and a cryptographic component tcrypto                                                                       initiating agent, where the Provider is fixed in US-West.
for certificate validation, signature verification, Diffie-Hellman                                                                The shaded region captures variability under sampled network
key exchange, key derivation, token encoding, and symmetric                                                                       conditions.
encryption. The total protocol overhead is modeled as:
                                                      
                                                   m                                                                              AWS [39], and use these to approximate protocol overhead.
           cproto (m) = (RTTB,P + tcrypto ) ·            ,      (1)
                                                  Qmax                                                                            Figure 4 shows the amortized protocol setup overhead:
where P is the Provider, and RTTB,P is the round-trip                                                                                                                cproto (m)
                                                                                                                                                                               c̄proto (m) =
time for agent B contacting the Provider and receiving a                                                                                                                 m
response. Each authorization cycle involves agent B retrieving                                                                    as a function of token quota Qmax , using m = 100 requests,
metadata and a one-time key for agent A from the Provider.                                                                        where the measured cryptographic overhead tcrypto = 7 ms.
This round-trip, along with local cryptographic operations,                                                                       As shown, the protocol overhead decreases sharply with in-
must be performed once every Qmax requests, as the token                                                                          creasing token quota Qmax , demonstrating how it can be effec-
quota is exhausted.                                                                                                               tively amortized across inter-agent interactions. Moreover, the
                                                                                                                                  overhead is low for all Provider geolocations, with slightly
                                                                                                                                  higher overhead for Europe and Asia.
                                                         250                                          Provider Location              We also evaluate the effect of geolocation on protocol
                                                                                                              US-West




                               Amortized Overhead (ms)
                                                                                                              US-East
                                                                                                                                  overhead by varying the placement of the initiating agent
                                                         200
                                                                                                              EU                  under a fixed Provider location (US-West). The overhead
                                                                                                              Asia                is very low—under 25ms when agents interact for at least 4–5
                                                         150
                                                                                                                                  requests (Figure 5). This effect is even more pronounced when
                                                                                                                                  the agent and Provider are geographically close.
                                                         100

                                                                                                                                  C. Task Completion
                                                          50
                                                                                                                                     SAGA operates as a protocol layer above the underlying
                                                           0                                                                      LLM agents, whose communications are not impacted by the
                                                               1              10               20                    30
                                                                                                                                  protocol. To illustrate SAGA in realistic agent interactions,
                                                                   Maximum number of requests per token (Qmax)                    we deploy three types of agents: (a) Calendar agents that
                                                                                                                                  determine a mutually available time and schedule a meeting,
Fig. 4: Amortized protocol overhead per request c̄proto (m) as a                                                                  (b) Email agents that extract relevant expense-related emails
function of maximum number of requests token is reused. We                                                                        and collaborate to submit an expense report, and (c) Writing
measure the overhead for several geographic locations for the                                                                     agents with different expertise areas collaborating to write a
Provider. The shaded region reflects variability for agents                                                                       blogpost. As expected, all agents successfully complete their
position worldwide.                                                                                                               tasks. See Appendix C for more details.
                                                                                                                                     We measure the standard task completion cost i.e., the
  We sample round-trip times (RTTB,P ) from empirical                                                                             time taken by the LLM to generate responses, and the net-
measurement distributions using monitors in US-East, US-                                                                          work latency (Table II, under Standard Cost). The LLM
West, Europe and Asia, made available by CAIDA [38] and                                                                           response time depends on both model execution speed and



                                                                                                                             11
                                 Standard Cost       SAGA              Fault Tolerance. Figures 6a, 6b, and 10 demonstrate that
  Task       LLM Backend
                               LLM     Networking   Overhead
                                                                       making the Provider fault-tolerant (3, 5 RAFT nodes)
  Calendar   GPT-4.1-mini      50.001     0.791       0.165            introduces negligible throughput degradation across key op-
  Email      GPT-4.1           26.862     1.319       0.165
  Writing    Qwen-2.5         363.563     1.319       0.165            erations. For example, for OTK Requests (Figure 6a), the
                                                                       No-RAFT (1-node) setup achieves 242K requests per minute,
TABLE II: Task execution time (in seconds). A, B, and
                                                                       compared to 212K for 3-node and 204K for 5-node RAFT
the Provider are located in Asia, Europe, and US-West,
                                                                       configurations, which translates to a throughput decrease of
respectively, and the token quota is 10. Standard Cost is
                                                                       12-15%. In Figure 6b, the cost of replication for OTK refresh
the minimum runtime for two agents communicating directly
                                                                       is lower, dropping from 173K (No-RAFT) to 153K (3-node
without SAGA, including LLM cost and network latency.
                                                                       RAFT), a difference of just 20K requests per minute (∼11%).
                                                                       For more I/O-intensive operations such as refreshing large key-
                                                                       chains (1000 OTKs), the tradeoff shrinks further to only 2K
task complexity. For example, using a local Qwen-2.5 model             requests per minute. Agent registration performance remains
instead of the cloud-based GPT-4.1 model for the Email task            largely stable even under 5-node replication, regardless of
increases the runtime from 26.862 to 43.730 seconds, as the            the number of OTKs provisioned per agent achieving 511K
Qwen-2.5 (72B) model is slower than the highly optimized               requests per minute. Similarly, OTK request and refresh incur
models served by OpenAI. Tasks like blog post writing require          minimal overhead.
substantially more input and output tokens and result in longer
runtimes, as observed for the Writing task. Since most of              Scalability. As expected, throughput scales linearly with the
the task completion time is spent by LLM-agents during                 number of sharders. As shown in Figures 6a, 10 and 11 adding
intermediate planning [40], and tool calls [41], the amortized         just 10 sharders increases OTK throughput nearly tenfold,
overhead of our protocol is significantly lower in comparison.         indicating no early saturation and achieving 178K to 511K
For example, even when agents and the Provider are                     requests per minute depending on the operation. We omit the
geographically distant, the protocol overhead accounts for less        latency of forwarding the request to the right sharder, as within
than 0.6% of the end-to-end cost of completing the fastest             the same datacenter this would be very small. Experiments on
calendar task.                                                         AWS including the cloud latency show a similar trend (see
                                                                       Appendix G). We expect that in production, Provider can
                                                                       scale to hundreds of sharders.
D. Fault Tolerance and Scalability
                                                                       Agent Capacity. We seek to answer the question: How many
   We evaluate SAGA’s scalability and fault tolerance under            active agents can the system support at any given time?
varying deployment configurations. Specifically, we measure            We define this as the number of agents a Provider can
the throughput of the Provider for core operations; agent              continuously serve with OTKs. Let L = Texpire − Tissue
registration, OTK request (i.e., issuance of one-time keys to          denote the token lifetime. Each agent needs to contact the
agents), and OTK refresh (i.e., generation of new OTKs by the          Provider only once per L to obtain an OTK, which it
user). We vary system parameters such as replication factor            then uses to generate a token and communicate with another
(RAFT nodes), number of sharding workers NS , OTK key-                 agent throughout the interval. Hence, the provider’s total
chain length, and access control token lifetime. Our findings          supported population is: C = T (NS ) · L where T (NS ) is
show that SAGA maintains high throughput under replication,            the Provider ’s OTK issuance throughput with NS sharder
scales linearly with added compute, and supports large agent           nodes. As shown in Figure 6c, with 10 sharders and 24-hour
populations through configurable token lifetimes.                      tokens, the system can support up to 300 million agents. These
Setup. We deploy a Provider backed by a replicated                     results demonstrate SAGA’s ability to operate under realistic,
RethinkDB cluster. RethinkDB [42] is a distributed, open-              large-scale deployment scenarios.
source database using the RAFT consensus algorithm for                 Sensitivity to the OTK Key-Chain Length. We analyze the
strong consistency and fault tolerance. For replication cost           effect of increasing the OTK key-chain length (number of
evaluation, we consider typical cluster configurations with 3          OTKs submitted to the Provider) on the throughput for
and 5 RAFT nodes (supporting 1 and 2 crash faults), and as             agent registration and OTK refresh. We omit OTK request,
baseline a configuration with only 1 node (no fault tolerance).        as each request consumes exactly one OTK by design. As
For scalability evaluation, we vary the number of sharders             expected, Figures 10 and 6b show a gradual throughput
and observe throughput assuming that each sharder (consisting          decrease as the number of submitted OTKs increases. This
of a RAFT cluster) runs on a separate machine and requests             is due to the increased payload size and the cost of writing
are routed by a proxy to the right sharder. To analyze the             more state to the replicated agent registry.
system’s sensitivity to storage-related operations, we vary               While longer OTK key-chains incur higher cost, SAGA
the number of submitted OTKs between 10, 100, and 1000                 maintains high throughput across practical configurations. For
keys. Experiments are conducted on a workstation with a 16-            example, agent registration with 1000 OTKs still exceeds 40K
core AMD Threadripper PRO 5955WX CPU and Samsung’s                     requests per minute with 10 sharders (Figure 10c), and OTK
MZ1L21T9HCLS-00A07 SSD.                                                refresh remains comparably efficient across RAFT configu-



                                                                  12
                                                                                                                                                                                   300M




 Throughput (reqs/min)                                                          Throughput (reqs/min)
                                      Replicas                                                                                                Replicas                                     Sharders (NS )




                                                                                                                                                                Total Agents (C)
                         200K        No-RAFT (1-node)                                                   150K                                 No-RAFT (1-node)                                       1
                                     RAFT (3-node)                                                                                           RAFT (3-node)                         200M             5
                                     RAFT (5-node)                                                      100K                                 RAFT (5-node)                                          10
                         100K                                                                                                                                                      100M
                                                                                                        50K

                                                                                                                                                                                    20K
                          0K                                                                             0K
                                 1        2          3         4    5    10                                        10            100               1000                                   1 min         1 hr          6 hr          12 hr   24 hr
                                                        Sharders                                                        One-Time Keys (OTKs)                                                                   Token Lifetime (L)


                                (a) OTK Request Throughput                                                     (b) OTK Refresh Throughput                                           (c) Total Capacity C of the system.
                                                               Fig. 6: SAGA’s Throughput and Capacity for different protocol operations.


rations (Figure 6b). Despite processing the same number of                                                                       short of enabling secure cross-organizational communication.
OTKs, registration outperforms OTK refresh due to differences                                                                    While frameworks like LangChain’s Agent Protocol3 provide
in storage operations: registration involves appending to the                                                                    specifications for interactions, they do not address critical
registry whereas OTK refresh updates existing entries. These                                                                     aspects like authentication or access control mechanisms.
results confirm that users can pre-provision large key batches                                                                   Commercial platforms like Amazon Bedrock [47] enable
with small performance penalties, enhancing resilience under                                                                     agent orchestration but assume all agents belong to the same
intermittent connectivity.                                                                                                       restricted environment. Packages like AutoGen [44] support
                                                                                                                                 multi-agent interactions, but only when agents are all running
                                                     VII. R ELATED W ORK                                                         locally. AACP [48] introduces a cryptographic foundation
   This section reviews existing frameworks for secure agent                                                                     using verifiable credentials but adopts a fully peer-to-peer
interactions and current implementation landscapes, highlight-                                                                   architecture without mediation layers to govern agent inter-
ing the gaps our work addresses. We also explore existing                                                                        actions.
multi-agent attacks, highlighting their limited scope.
                                                                                                                                 Key Pre-Distribution and Trust Models. Users of Signal
High-Level Designs for Inter-Agent Interaction. Several                                                                          and Matrix provide a server with signed one-time keys and
frameworks and protocols have been proposed to govern AI                                                                         ephemeral keys in-advance to allow offline shared key estab-
agent interactions securely. South et al. [12] introduce a                                                                       lishment; users either choose to trust the central server, or
framework for authenticated delegation using OAuth 2.0 de-                                                                       verify identity keys off-band in the case server compromise
sign patterns, where users register their agents with providers                                                                  is a concern. [49], [50]. SAGA employs a similar technique,
and issue delegation tokens. Chan et al. [11] outline agent                                                                      allowing users to register their agents and provide one-time
infrastructure protocols defining interaction standards, focused                                                                 keys with a Provider to enable fine access control to agents,
on three core functions: attribution, interaction, and response,                                                                 in the spirit of Kerberos [33]. Similar to Signal, users who do
Chan et al. [10] propose a system for agent identification                                                                       not trust the identity service (third party in SAGA) must verify
that tracks AI systems along with their context windows and                                                                      identity keys off-band. Additionally, the Provider can be
initial users. Shavit et al. [9] discuss governance practices for                                                                made resilient to compromise, as discussed in Section V-A.
agentic systems, highlighting unique agent identification and
interruptibility as critical features. None of these designs are                                                                 Attacks on Multi-Agent Systems. Several works examine
actually implemented and evaluated in a real system.                                                                             adversarial propagation in multi-agent communication [51]–
LLM Agent Development Frameworks. LangChain [43],                                                                                [55], where rogue agents can propagate malicious outputs via
AutoGen [44], and smolagents [45] are development libraries                                                                      interactions with other agents. Other works consider fixed
that help build LLM agents, but do not address gover-                                                                            communication patterns with slightly different goals, such
nance—how users control their agents or how agents securely                                                                      as multi-agent debate [53] and question-answer collaboration
discover and communicate with each other. We used smola-                                                                         [56]. In orchestrated multi-agent systems, Triedman et al.
gents in our experiments, but SAGA is compatible with any                                                                        [57] describe attacks against orchestrator agents using ad-
other agent development framework. SAGA provides user-                                                                           versarial content via metadata. Khan et al. [58] introduce
level control of agent interaction with other agents and secure                                                                  an attack approach for pragmatic multi-agent LLM systems
agent communication.                                                                                                             operating under real-world constraints like token bandwidth
                                                                                                                                 limits and message latency. SAGA provides protection against
Inter-Agent Protocol Implementations. Recent surveys [46]                                                                        such attacks through its token-driven system, which explicitly
reveal that implementations typically assume pre-established                                                                     limits the number of interactions between agents. Additionally,
connections between agents with static communication pat-                                                                        benign agents can easily update their contact policies to block
terns. Smyth OS2 offers a portal for agent creation and                                                                          malicious agents, preventing any widespread “outbreak.”
integration limited within an particular organization. Current
software implementations for agent interactions generally fall
       2 https://smythos.com/                                                                                                          3 https://github.com/langchain-ai/agent-protocol




                                                                                                                            13
                         VIII. C ONCLUSION                                            [19] M. J. Dworkin et al., “SHA-3 standard: Permutation-based hash and
                                                                                           extendable-output functions,” 2015.
   SAGA establishes a scalable framework for secure inter-                            [20] H. Krawczyk and P. Eronen, “HMAC-based Extract-and-Expand Key
agent communication that balances security, autonomy, and                                  Derivation Function (HKDF),” RFC 5869, May 2010, https://datatracker.
governance through a Provider-mediated architecture en-                                    ietf.org/doc/html/rfc5869.
                                                                                      [21] E. Barker, “Recommendation for Key Management, Part 1: General
forcing user policies. Unlike prior works that only offer                                  (Revision 5),” National Institute of Standards and Technology, NIST
conceptual designs or high-level architectures for agent gov-                              Special Publication 800-57 Part 1 Rev. 5, May 2020, provides
ernance [9]–[12], SAGA provides the first concrete protocol                                foundational guidance on cryptographic key lifecycle management,
                                                                                           including cryptoperiod determination and key rotation practices.
specification with strong formal security guarantees and a                                 [Online]. Available: https://doi.org/10.6028/NIST.SP.800-57pt1r5
reference implementation. SAGA is compatible with existing                            [22] P. A. Grassi, M. E. Garcia, and J. L. Fenton, “Digital identity guidelines,”
agent protocols, such as A2A and Model Context Protocol [59]                               NIST special publication, vol. 800, pp. 63–3, 2017.
                                                                                      [23] B. Blanchet, B. Smyth, V. Cheval, and M. Sylvestre, “Proverif 2.00:
for standardized tool-use and it can be integrated with defenses                           automatic cryptographic protocol verifier, user manual and tutorial,”
against prompt-injection attacks [60], and privacy-preserving                              Version from, vol. 16, pp. 05–16, 2018.
data minimization techniques [61].                                                    [24] B. Desmond, J. Richards, R. Allen, and A. G. Lowe-Norris, Active
                                                                                           Directory: Designing, Deploying, and Running Active Directory. ”
                              R EFERENCES                                                  O’Reilly Media, Inc.”, 2008.
                                                                                      [25] D. Ongaro and J. Ousterhout, “In search of an understandable consensus
 [1] N. Mehandru, B. Y. Miao, E. R. Almaraz, M. Sushil, A. J. Butte, and                   algorithm,” in 2014 USENIX Annual Technical Conference (USENIX
     A. Alaa, “Evaluating large language models as agents in the clinic,” NPJ              ATC 14). Philadelphia, PA: USENIX Association, Jun. 2014, pp.
     digital medicine, vol. 7, no. 1, p. 84, 2024.                                         305–319. [Online]. Available: https://www.usenix.org/conference/atc14/
 [2] W. Wang, Z. Ma, Z. Wang, C. Wu, W. Chen, X. Li, and Y. Yuan, “A                       technical-sessions/presentation/ongaro
     survey of llm-based agents in medicine: How far are we from baymax?”             [26] L. Lamport, “The part-time parliament,” ACM Trans. Comput.
     arXiv preprint arXiv:2502.11211, 2025.                                                Syst., vol. 16, no. 2, p. 133–169, May 1998. [Online]. Available:
 [3] S. Wu, O. Irsoy, S. Lu, V. Dabravolski, M. Dredze, S. Gehrmann,                       https://doi.org/10.1145/279227.279229
     P. Kambadur, D. Rosenberg, and G. Mann, “BloombergGPT: A large                   [27] M. Castro and B. Liskov, “Practical byzantine fault tolerance,” in
     language model for finance,” arXiv preprint arXiv:2303.17564, 2023.                   3rd Symposium on Operating Systems Design and Implementation
 [4] Y. Nie, Y. Kong, X. Dong, J. M. Mulvey, H. V. Poor, Q. Wen, and                       (OSDI 99).        New Orleans, LA: USENIX Association, Feb.
     S. Zohren, “A survey of large language models for financial applications:             1999. [Online]. Available: https://www.usenix.org/conference/osdi-99/
     Progress, prospects and challenges,” arXiv preprint arXiv:2406.11903,                 practical-byzantine-fault-tolerance
     2024.                                                                            [28] F. Chang, J. Dean, S. Ghemawat, W. C. Hsieh, D. A. Wallach,
 [5] T. Zhou, P. Wang, Y. Wu, and H. Yang, “Finrobot: Ai agent for equity                  M. Burrows, T. Chandra, A. Fikes, and R. E. Gruber, “Bigtable:
     research and valuation with large language models,” arXiv preprint                    A distributed storage system for structured data,” ACM Trans.
     arXiv:2411.08804, 2024.                                                               Comput. Syst., vol. 26, no. 2, Jun. 2008. [Online]. Available:
 [6] J. Zhang, H. Bu, H. Wen, Y. Liu, H. Fei, R. Xi, L. Li, Y. Yang, H. Zhu,               https://doi.org/10.1145/1365815.1365816
     and D. Meng, “When llms meet cybersecurity: A systematic literature              [29] J. C. Corbett, J. Dean, M. Epstein, A. Fikes, C. Frost, J. Furman,
     review,” Cybersecurity, vol. 8, no. 1, pp. 1–41, 2025.                                S. Ghemawat, A. Gubarev, C. Heiser, P. Hochschild, W. Hsieh,
 [7] M. Rigaki, C. Catania, and S. Garcia, “Hackphyr: A local fine-                        S. Kanthak, E. Kogan, H. Li, A. Lloyd, S. Melnik, D. Mwaura,
     tuned llm agent for network security environments,” arXiv preprint                    D. Nagle, S. Quinlan, R. Rao, L. Rolig, Y. Saito, M. Szymaniak,
     arXiv:2409.11276, 2024.                                                               C. Taylor, R. Wang, and D. Woodford, “Spanner: Google’s Globally-
 [8] M. Kobayashi, M. Fuchi, A. Zanashir, T. Yoneda, and T. Takagi,                        Distributed database,” in 10th USENIX Symposium on Operating Systems
     “Construction and evaluation of llm-based agents for semi-autonomous                  Design and Implementation (OSDI 12). Hollywood, CA: USENIX
     penetration testing,” arXiv preprint arXiv:2502.15506, 2025.                          Association, Oct. 2012, pp. 261–264. [Online]. Available: https://www.
 [9] Y. Shavit, S. Agarwal, M. Brundage, S. Adler, C. O’Keefe, R. Campbell,                usenix.org/conference/osdi12/technical-sessions/presentation/corbett
     T. Lee, P. Mishkin, T. Eloundou, A. Hickey et al., “Practices for                [30] J. Baker, C. Bond, J. C. Corbett, J. Furman, A. Khorlin,
     governing agentic AI systems,” Research Paper, OpenAI, 2023.                          J. Larson, J.-M. Leon, Y. Li, A. Lloyd, and V. Yushprakh,
[10] A. Chan, N. Kolt, P. Wills, U. Anwar, C. S. de Witt, N. Rajkumar,                     “Megastore: Providing scalable, highly available storage for interactive
     L. Hammond, D. Krueger, L. Heim, and M. Anderljung, “IDs for AI                       services,” in Proceedings of the Conference on Innovative Data
     systems,” arXiv preprint arXiv:2406.12137, 2024.                                      system Research (CIDR), 2011, pp. 223–234. [Online]. Available:
[11] A. Chan, K. Wei, S. Huang, N. Rajkumar, E. Perrier, S. Lazar, G. K.                   http://www.cidrdb.org/cidr2011/Papers/CIDR11 Paper32.pdf
     Hadfield, and M. Anderljung, “Infrastructure for ai agents,” arXiv               [31] A. Silberschatz, H. F. Korth, and S. Sudarshan, “Database system
     preprint arXiv:2501.10114, 2025.                                                      concepts,” 2011.
[12] T. South, S. Marro, T. Hardjono, R. Mahari, C. D. Whitney, D. Green-             [32] S. Solat, “Sharding distributed databases: A critical review,” arXiv
     wood, A. Chan, and A. Pentland, “Authenticated delegation and autho-                  preprint arXiv:2404.04384, 2024.
     rized AI agents,” arXiv preprint arXiv:2501.09674, 2025.                         [33] C. Neuman, S. Hartman, K. Raeburn, and T. Yu, “The kerberos network
[13] R. Surapaneni, M. Jha, M. Vakoc, and T. Segal, “Announcing                            authentication service (v5),” RFC 4120, 2005. [Online]. Available:
     the agent2agent protocol (A2A),” Google Developers Blog, April                        https://www.rfc-editor.org/info/rfc4120
     2025, accessed: 2025-04-10. [Online]. Available: https://developers.             [34] D. J. Bernstein, “Curve25519: New diffie-hellman speed records,” in
     googleblog.com/en/a2a-a-new-era-of-agent-interoperability/                            Public Key Cryptography - PKC 2006, M. Yung, Y. Dodis, A. Kiayias,
[14] N. Natarajan, J. Bradley, N. Sakimura, M. B. Jones, and E. Jay, “Openid               and T. Malkin, Eds. Berlin, Heidelberg: Springer Berlin Heidelberg,
     connect core 1.0 incorporating errata set 1,” https://openid.net/specs/               2006, pp. 207–228.
     openid-connect-core-1 0.html, 2014, openID Foundation.                           [35] A. Langley, M. Hamburg, and S. Turner, “Elliptic Curves for Security,”
[15] S. Cohen, R. Bitton, and B. Nassi, “Here comes the AI worm: Unleash-                  RFC 7748, Jan. 2016. [Online]. Available: https://www.rfc-editor.org/
     ing zero-click worms that target GenAI-powered applications,” arXiv                   info/rfc7748
     preprint arXiv:2403.02817, 2024.                                                 [36] S. Boeyen, S. Santesson, T. Polk, R. Housley, S. Farrell, and D. Cooper,
[16] J. Katz and Y. Lindell, Introduction to Modern Cryptography, Second                   “Internet X.509 Public Key Infrastructure Certificate and Certificate
     Edition, 2nd ed. Chapman & Hall/CRC, 2014.                                            Revocation List (CRL) Profile,” RFC 5280, May 2008. [Online].
[17] D. Johnson, A. Menezes, and S. Vanstone, “The elliptic curve digital sig-             Available: https://www.rfc-editor.org/info/rfc5280
     nature algorithm (ecdsa),” International journal of information security,        [37] A. Yang, B. Yang, B. Zhang, B. Hui, B. Zheng, B. Yu, C. Li, D. Liu,
     vol. 1, pp. 36–63, 2001.                                                              F. Huang, H. Wei, H. Lin, J. Yang, J. Tu, J. Zhang, J. Yang, J. Yang,
[18] B. Harris and L. Velvindron, “RFC 8709: Ed25519 and ed448 public                      J. Zhou, J. Lin, K. Dang, K. Lu, K. Bao, K. Yang, L. Yu, M. Li, M. Xue,
     key algorithms for the secure shell (SSH) protocol,” USA, 2020.                       P. Zhang, Q. Zhu, R. Men, R. Lin, T. Li, T. Xia, X. Ren, X. Ren, Y. Fan,




                                                                                 14
     Y. Su, Y. Zhang, Y. Wan, Y. Liu, Z. Cui, Z. Zhang, and Z. Qiu, “Qwen2.5                                 User                    Provider
     technical report,” arXiv preprint arXiv:2412.15115, 2024.
[38] CAIDA, “The CAIDA archipelago monitor statistics,” https://www.
     caida.org/projects/ark/statistics/, accessed April 2025.
[39] M. Adorjan, “cloudping.co: Aws inter-region latency monitoring,” 2025,                 Generate uidU , passwd
     accessed: 2025-04-18. [Online]. Available: https://github.com/mda590/                  Generate SKU , PKU
     cloudping.co                                                                           Get CertU = GenCertSKCA (uidU , PKU )
[40] S. Yao, J. Zhao, D. Yu, N. Du, I. Shafran, K. Narasimhan, and Y. Cao,                  Get Provider certificate and PKProv
     “React: Synergizing reasoning and acting in language models,” in
     International Conference on Learning Representations, 2023.
[41] T. Schick, J. Dwivedi-Yu, R. Dessı̀, R. Raileanu, M. Lomeli, E. Hambro,
                                                                                                                 Establish TLS connection
     L. Zettlemoyer, N. Cancedda, and T. Scialom, “Toolformer: Language
     models can teach themselves to use tools,” Advances in Neural Infor-
     mation Processing Systems, 2023.                                                                            uidU , passwd, CertU
[42] L. Walsh, V. Akhmechet, and M. Glukhovsky, “Rethinkdb-rethinking
     database storage,” Hexagram 49, Inc, p. 85, 2009.
[43] “Agent Protocol — langchain-ai.github.io,” https://langchain-ai.github.
     io/agent-protocol/api.html, 2024, [Accessed 26-03-2025].                                                              Verify user identity using service S
[44] Q. Wu, G. Bansal, J. Zhang, Y. Wu, B. Li, E. Zhu, L. Jiang, X. Zhang,                                                 DU [uidU ]=⟨H(passwd), CertU ⟩
     S. Zhang, J. Liu et al., “Autogen: Enabling next-gen llm applications
     via multi-agent conversations,” in Conference on Language Modeling                                                Confirmation
     (COLM), 2024.
[45] A. Roucher, A. V. del Moral, T. Wolf, L. von Werra, and E. Kau-
     nismäki, “smolagents: a smol library to build great agentic systems.”
     https://github.com/huggingface/smolagents, 2025.                                           Fig. 7: User Registration protocol for user U.
[46] K.-T. Tran, D. Dao, M.-D. Nguyen, Q.-V. Pham, B. O’Sullivan, and
     H. D. Nguyen, “Multi-agent collaboration mechanisms: A survey of
     llms,” arXiv preprint arXiv:2501.06322, 2025.
[47] A. Sempf, J. Toth, and S. v. d. Moosdijk, “Creating asynchronous                  [61] E. Bagdasarian, R. Yi, S. Ghalebikesabi, P. Kairouz, M. Gruteser, S. Oh,
     AI agents with Amazon Bedrock — Amazon Web Services —                                  B. Balle, and D. Ramage, “Airgapagent: Protecting privacy-conscious
     aws.amazon.com,”         https://aws.amazon.com/blogs/machine-learning/                conversational agents,” in Proceedings of the 2024 on ACM SIGSAC
     creating-asynchronous-ai-agents-with-amazon-bedrock/,                2025,             Conference on Computer and Communications Security, ser. CCS ’24.
     [Accessed 21-04-2025].                                                                 Association for Computing Machinery, 2024, p. 3868–3882.
[48] K.      Royce,      “AI       agent-to-agent       communications     pro-        [62] S. Abdelnabi, A. Gomaa, E. Bagdasarian, P. O. Kristensson, and
     tocol,”      kossisoroyce.com,         2025,        accessed:    2025-04-              R. Shokri, “Firewalls to secure dynamic llm agentic networks,” arXiv
     10.     [Online].    Available:       https://kossisoroyce.com/2025/03/28/             preprint arXiv:2502.01822, 2025.
     ai-agent-to-agent-communications-protocol/
[49] M. R. Albrecht, B. Dowling, and D. Jones, “Device-oriented group                                                 A PPENDIX
     messaging: a formal cryptographic analysis of matrix’core,” in 2024
     IEEE Symposium on Security and Privacy (SP). IEEE, 2024, pp. 2666–                A. Protocol Figures
     1685.                                                                                Here we provide detailed protocol diagrams for user regis-
[50] E. Kret and R. Schmidt, “The pqxdh key agreement protocol,” 2024.
     [Online]. Available: https://signal.org/docs/specifications/pqxdh                 tration (Section IV-B), agent registration (Section IV-C) and
[51] X. Gu, X. Zheng, T. Pang, C. Du, Q. Liu, Y. Wang, J. Jiang, and M. Lin,           agent communication (Section IV-E), under Figure 7, Figure 8
     “Agent smith: A single image can jailbreak one million multimodal                 and Figure 9 respectively.
     llm agents exponentially fast,” in International Conference on Machine
     Learning, 2024.                                                                   B. More Cryptographic Overhead Results
[52] D. Lee and M. Tiwari, “Prompt infection: Llm-to-llm prompt injection
     within multi-agent systems,” arXiv preprint arXiv:2410.07283, 2024.                 We provide details about the cryptographic cost of key
[53] A. Amayuelas, X. Yang, A. Antoniades, W. Hua, L. Pan, and W. Y.                   operations in the SAGA protocol in Table III.
     Wang, “Multiagent collaboration attack: Investigating adversarial attacks
     in large language model collaborations via debate,” in Findings of the            C. Agent-Interaction Task Details
     Association for Computational Linguistics: EMNLP 2024, 2024, pp.
     6929–6948.                                                                           We implement our LLM-agent using the smolagents library
[54] P. He, Y. Lin, S. Dong, H. Xu, Y. Xing, and H. Liu, “Red-teaming                  [45], specifically leveraging the CodeAgent class. This class
     llm multi-agent systems via communication attacks,” arXiv preprint
     arXiv:2502.14847, 2025.                                                           enables agents to write and execute Python code during
[55] W. Yu, K. Hu, T. Pang, C. Du, M. Lin, and M. Fredrikson, “Infecting               their reasoning process, significantly reducing the number of
     llm agents via generalizable adversarial attack,” in Red Teaming GenAI:           interactions required with the user—which, in our setup, is
     What Can We Learn from Adversaries?, 2024.
[56] T. Ju, Y. Wang, X. Ma, P. Cheng, H. Zhao, Y. Wang, L. Liu, J. Xie,                another agent. To support autonomous agent-to-agent com-
     Z. Zhang, and G. Liu, “Flooding spread of manipulated knowledge in                munication, we modify the system prompts provided to each
     llm-based multi-agent communities,” arXiv preprint arXiv:2407.07791,              agent, tailoring the instructions slightly based on whether the
     2024.
[57] H. Triedman, R. Jha, and V. Shmatikov, “Multi-agent systems execute               agent is in the initiating or receiving role.
     arbitrary malicious code,” arXiv preprint arXiv:2503.12188, 2025.                    To emulate realistic tool usage, we implement database-
[58] R. M. S. Khan, Z. Tan, S. Yun, C. Flemming, and T. Chen, “Agents Un-              backed services for email, calendar, and document read/write
     der Siege: Breaking pragmatic multi-agent llm systems with optimized
     prompt attacks,” arXiv preprint arXiv:2504.00218, 2025.                           operations. For the email and calendar tools, we implement
[59] “Model context protocol,” https://modelcontextprotocol.io/, 2025, [Ac-            end-to-end functionality: sending an email or calendar invite
     cessed 26-03-2025].                                                               causes the content to actually appear in the recipient’s inbox or
[60] E. Debenedetti, I. Shumailov, T. Fan, J. Hayes, N. Carlini, D. Fabian,
     C. Kern, C. Shi, A. Terzis, and F. Tramèr, “Defeating prompt injections          calendar. This stands in contrast to recent agent-agent interac-
     by design,” arXiv preprint arXiv:2503.18813, 2025.                                tion work, which typically simulates tool use via another LLM



                                                                                  15
                             User                                                                                     Provider

      Generate aidA , EDA , CPA
      Generate (PKA , SKA ) and (PACA , SACA )
      Get CertA = GenCertSKCA (⟨aidA , PKA ⟩)
      Generate (OTK1A , SOTK1A ), . . . , (OTKNA , SOTKNA )
      σAU = SignSKU (⟨aidA , ED A , PKA , PACA , PKProv ⟩)
      σ U i = SignSKU OTKiA
       OTKA


                                                                     Establish TLS connection


                                                                       (uidU , passwd)


                                                                                                                  Verify user credentials.

                                         (aidA , EDA , CPA ), PKU , CertA , PACA , OTKiA , σOTK
                                                                                            U
                                                                                                i , i ∈ [1, N ]




                                                                                                 Check uniqueness of aidA and EDA
                                                                                                 Verify CertA and signatures σAU , σOTK
                                                                                                                                    U
                                                                                                                                        i , i ∈ [1, N ]

                                                                                                 Compute MA = {EDA , CertA , PACA , OTKiA , i ∈ [1, N ]}
                                                                                                 Store DA [aidA ] = ⟨uidU , MA , CPA , σAU , σOTK
                                                                                                                                              U
                                                                                                                                                 i⟩

                                                                                                 σAP rov = SignSKProv (⟨CertU , EDA , PACA , σAU ⟩)
                                                                             σAP rov



                                         Fig. 8: Agent Registration protocol for agent A by user U.


              Protocol Component                 Overhead (ms)                         between them. This ensures a clean isolation layer between
                             User Registration                                         tasks, without introducing any additional overhead.
              User Registration (User)                     2.34                        Calendar. In this task, one agent contacts another to schedule
              User Registration (Provider)               194.09
                                                                                       a meeting on a specific date. Both agents inspect their respec-
                             Agent Registration                                        tive calendars to determine availability, negotiate a mutually
              Agent Registration (User)                   15.09                        agreeable time, and then create a calendar event. Task success
              Agent Registration (Provider)              212.85                        is defined by the following criteria:
                           Agent Communication                                          1) the calendar invite appears in both agents’ calendars for
              Contact Resolution (Provider)                   1.46                         the correct duration, listing both as attendees,
              Setup Phase (Initiator)                         2.14
              Setup Phase (Receiver)                          1.83
                                                                                        2) there are no scheduling conflicts with pre-existing events,
                                                                                           and
                           Access Control Tokens
                                                                                        3) the meeting is scheduled for a future date and time.
              Token Generation (Initiator)                    1.03
              Token Decryption (Receiver)                     1.20                     We use GPT-4.1-mini as the LLM backbone for this task. The
              Token Validation (Initiator)                    0.24                     full interaction trace is shown in Figure 13.
              Token Validation (Receiver)                     0.26
                                                                                       Email. In this task, one agent reaches out to another for
   TABLE III: Computational overhead of key operations.                                help compiling information to submit an expense report. Both
                                                                                       agents search their respective inboxes for expenses related to
                                                                                       a shared event. The receiving agent extracts relevant entries
rather than through explicit, stateful updates. We initialize                          and sends them to the initiator, who combines the results and
each user profile (and corresponding agent) with synthetic data                        submits a final report using a tool-call. We evaluate success
adapted from Abdelnabi et al. [62], extending it as needed to                          based on:
suit the scope of our tasks.                                                            1) whether the total amount submitted matches the expected
   Each task (such as one agent requesting another to find                                 value (as all data is synthetic and fully known),
a common meeting time) spawns a fresh instance of the                                   2) whether both users are listed as participants in the ex-
agent class. While the underlying LLM remains the same                                     pense report, and
across tasks, no prior context or conversation history is shared                        3) whether no extraneous users are included.



                                                                                 16
                                    A                                                B                                         Provider

                                                                                                 Establish TLS connection


                                                                                                Request to contact aidA


                                                                                                                     Check BudgetOTK (aidA , aidB ) > 0
                                                                                                                     Check CounterOTK [aidA ][aidB ] > 0
                                                                                                                     CounterOTK [aidA ][aidB ]− = 1

                                                                                         CertU1 , (aidA , EDA ), (CertA , PACA ),
                                                                                                    OTKiA , σOTK
                                                                                                             U1       U1
                                                                                                                 i , σA




                                                          Verify CertU1                                          
                                                          VerifyPKU1 ⟨aidA , EDA , PKA , PACA , PKProv ⟩, σAU1
                                                                                       U1
                                                          VerifyPKU1 ⟨aidA , OTKiA ⟩, σOTKi




                                               Establish TLS connection


                                                                       DHB = DH(SACB , OTKiA )
                                                                       SDHK = KDF (DHB )

                                          ⟨aidB , CertB , EDB , PACB , σBU2 ⟩,
                                                    OTKiA , σBP rov


        VerifyPKProv (⟨aidB , CertB , EDB , PACB , σBU2 ⟩, σBP rov )
        Verify OTKiA −→ SOTKiA exists in storage
        DHA = DH(SOTKiA , PACB )
        SDHK = KDF (DHA )
        Delete OTKiA → SOTKiA



                            $
       Generate nonce N ←
                        −R
       token = EncSDHK (⟨N, Tissued , Texpire , Qmax , PACB ⟩)
       Store token

                                                         token


                                                     Communication



Fig. 9: Agent Communication protocol between initiating agent B and receiving agent A to obtain an Access Control Token
with the Provider mediation if first communication between agents or the previous token expired.


We use GPT-4.1 as the LLM backbone for this task. The                                interaction rounds. Once the final blog post is agreed upon,
complete interaction is provided in Figure 14.                                       one of the agents uses a tool-call to save the document under
                                                                                     a specified filename. Success is measured by whether the blog
Writing. In this task, two agents collaborate on writing a blog                      post is saved correctly with the expected filename. We use
post about the privacy implications of AI. Each agent repre-                         Qwen2.5-72B-Instruct [37] as the LLM backbone. Due to the
sents a user with expertise in either law or machine learning.                       length of messages involved (often exceeding 2000 words),
They begin by reading existing blog posts associated with                            we omit the full example here.
their respective users and then engage in a multi-step writing
process to produce a unified article. Agents are encouraged
to both internally reflect and externally revise across multiple



                                                                                17
// required types                                                        •  EndAgentAuthA and EndAgentAuthB, which trig-
type key [data].                                                            ger once agents A and B complete communication with
type skey [data].
type pkey [data].                                                           each other.
fun pk(skey): pkey.
                                                                          To specify authentication queries using these events, we
// DH formalized as a symmetric equation                               employ the general pattern of proving that received content
fun dh(pkey, skey): key.
equation forall a: skey, b: skey;                                      must have been sent in exactly the same form. That is, Peer
    dh(pk(a), b) = dh(pk(b), a).                                       A receives a token X, Peer B must have sent exactly the
// key signing                                                         token X. To formulate this in P ROV ERIF, we employ the
fun sign(skey, bitstring): bitstring.                                  implies primitive as such. For example, agent A as shown
reduc forall m: bitstring, sk: skey;
    checksign(pk(sk), m, sign(sk, m)) = m.                             in Figure 8 is authenticated against the provider with the
                                                                       following P ROV ERIF query:
// symmetric encryption
fun senc(key, bitstring): bitstring.
reduc forall m: bitstring, k: key;
                                                                       query x: bitstring, k:pkey; inj-event(EndAuthA(x, k))
    sdec(k, senc(k,m)) = m.
                                                                           ==> inj-event(EndProviderAuthA(x, k)).
// hashing/key derivation
// (recall, proverif functions are uni-directional
// unless [data] is specified
fun hash(bitstring): bitstring
fun kdf(bitstring): key                                                   And, to specify reachability, we simply query P ROV ERIF to
                                                                       check if each specified event occurs.
Listing 2: Cryptographic primitives for SAGA modeled in
                                                                          Finally, our P ROV ERIF models are open source, and our
P ROV ERIF.
                                                                       testing environment is fully declared and reproducible using
                                                                       a nix flake. Using a 6th-generation i7 laptop with 16 GB of
                                                                       RAM, P ROV ERIF terminates in approximately 10 minutes.
D. Verification Details
   To formally verify the SAGA protocol, we employ                     E. Attacker Evaluation
P ROV ERIF, an automated cryptographic protocol verifier in               We evaluate SAGA’s resilience against adversarial behavior
the symbolic Dolev-Yao model. In the Dolev-Yao model,                  as defined in the threat model in Section III-D. We consider
attackers are assumed to be capable of arbitrarily observing,          8 adversarial agents that attempt to bypass authentication,
intercepting, replaying, and synthesizing on-network mes-              secrecy, or access control, including authenticated connec-
sages. We construct two models: one model for reasoning                tions, token misuse, contact policy violations, or message-
about the authentication of agent registration, and another for        level manipulation by a network-level adversary. As noted in
reasoning about both the authentication and secrecy of agent           Section III-C, we assume the adversary cannot compromise
communication.                                                         the TLS layer, break standard cryptographic primitives (e.g.,
   We model the required cryptographic primitives for SAGA             signature forgery or DH key extraction), or bypass human
in P ROV ERIF, including Diffie-Hellman, key signing, sym-             verification during user registration. To verify that SAGA does
metric encryption, hashing, and key derivation, as shown in            indeed work in defending against such threats, we imple-
Listing 2.                                                             mented these attacker models in our evaluation.
   To formally model SAGA, we precisely replicated the                    We denote the adversarial agent as M and the victim agent
cryptographic operations of the agent registration and agent           as A. Table IV summarizes the attack models, the required
communication handshakes as described in Figure 8 and                  adversarial capabilities, and the specific protocol step at which
Figure 9 respectively. Within P ROV ERIF, we specified secrecy,        each attack is detected. The following attack models represent
authentication, and reachability queries for SAGA.                     distinct ways in which the protocol may be misused or
Secrecy. To specify secrecy, we simply employ P ROV ERIF’s             subverted by an adversarial agent:
attacker primitive, which soundly determines whether a                   A1: M attempts to contact A without presenting valid TLS
Dolev-Yao attacker can obtain any given term. In this case,              credentials.
we specify the attacker to check whether it can obtain the
                                                                       In this case, the TLS handshake fails since M cannot authen-
token term.
                                                                       ticate to A. The connection is rejected before any application-
Authentication and Reachability. To specify authentication             layer interaction takes place.
and reachability, we employ P ROV ERIF’s event functional-
ity. We construct six events in our model:                               A2: M contacts A without a one-time access key or token.
  • EndAuthA and EndAuthB, which trigger once agents                   Here, M completes the TLS handshake and is authenticated,
    A and B complete authentication with the provider.                 but fails to provide either a valid OTKiA or a previously issued
  • EndProviderAuthA          and EndProviderAuthB,                    access token. A terminates the session without issuing a token.
    which trigger once the provider completes authenticating
                                                                         A3: M contacts A with an invalid token.
    A and B respectively.



                                                                  18
     Attack Model    Capabilities     Protocol Step Detected   Details
     A1              C1, C2           IV-E, Step 4             The receiving agent rejects the TLS connection attempt, as a valid certificate
                                                               is required to establish communication.
     A2              C1, C2           IV-E, Step 6             The receiving agent terminates the session due to the absence of a valid access
                                                               control credential (either an OTK or token).
     A3              C1, C2           IV-E, Step 8             The receiving agent detects that the token presented is either expired or has
                                                               exceeded its usage quota, and aborts the connection.
     A4              C1, C2           IV-E, Step 6             The provider-issued signature on the initiating agent’s metadata fails verifica-
                                                               tion, as the metadata does not match the registered information.
     A5              C1, C2, C3, C4   IV-E, Step 8             The token presented by the initiating agent was issued to a different agent,
                                                               and the mismatch is detected by the receiving agent during token validation,
                                                               leading to connection termination.
     A6              C1, C2, C3, C4   IV-E, Step 2             The Provider denies issuance of an OTK since the initiating agent is not
                                                               permitted under the receiving agent’s contact policy.
     A7              C3               IV-B, Step 5             User registration requires human verification. As only users can register agents
                                                               in SAGA, the adversarial agent fails to satisfy the verification requirements and
                                                               is denied registration.
     A8              C1, C2, C3, C4   IV-E, Token reuse        The malicious initiating agent proceeds with establishing a secure connection
                                                               with the receiving agent. However, there’s a limited amount of communication
                                                               between the two parties dictated by the token quota or the expiry date.


TABLE IV: Different attack models with corresponding required adversarial capabilities, and the specific SAGA protocol step
at which each attack is detected.


The connection is established and the token is received by                 A8: M contacts A with a valid token.
A, but the token is invalid, either because its timestamp has
                                                                         This represents a short-lived window of vulnerability. The
passed or it has exceeded its limit. Upon detecting this token
                                                                         protocol accepts the connection, but the token’s expiration
replay, A immediately closes the connection.
                                                                         and communication quota strictly bound the scope of abuse.
  A4: M attempts to impersonate benign agent A by providing              Once either limit is reached, the token becomes invalid and
  its Provider-issued signature and public information                   further requests are rejected. If malicious activity is detected,
  upon contact with other agents.                                        A’s user may blocklist M, thereby preventing it from obtaining
                                                                         new OTKs.
M uses A’s public information and the provider-issued signature
(σMP rov ← σAP rov ) when contacting other agents. Receiving             F. Additional Fault Tolerance & Scalability Results
agents verify the signature using M’s information (Step 6,
                                                                            Figure 10 and Figure 11 provide extended throughput results
Section IV-E), and the verification fails.
                                                                         for two core SAGA operations: agent registration and OTK
  A5: M contacts A and reuses a valid token issued by A to               refresh, across varying key-chain lengths and fault-tolerant
  a different agent.                                                     configurations.
In this scenario, A has issued a valid token to some other                  Figure 10 shows that agent registration throughput remains
agent, which is later intercepted or exfiltrated by M. When M            high and scales linearly with the number of sharders, even as
attempts to use it, A detects the mismatch between the token’s           the number of provisioned OTKs increases from 10 to 1000.
intended recipient and the initiating party’s identity (PACM ).          Although higher key-chain lengths reduce throughput due to
The connection is immediately aborted.                                   larger payload sizes and increased registry writes, the system
                                                                         still achieves over 40K registrations per minute with 1000
  A6: M attempts to contact A despite not being authorized               OTKs and 10 sharders. Additionally, the impact of RAFT-
  under A’s contact policy.                                              based replication remains marginal across all configurations.
The Provider enforces contact policies on behalf of receiv-              This confirms that the append-only nature of agent registration
ing agents. When M attempts to query or initiate a connection            enables efficient write performance.
with A, the Provider denies the request based on A’s contact                Figure 11 reports OTK refresh throughput under the same
policy.                                                                  settings. As expected, throughput decreases with larger key-
                                                                         chains due to the more I/O-intensive update operations. How-
  A7: M attempts to register copies of itself or other agents            ever, even with 1000 OTKs, the system sustains nearly 20K
  with the Provider.                                                     refreshes per minute at 10 sharders, even with 5 RAFT repli-
M attempts to register new identities, either by self-replication        cas. This demonstrates that agents can efficiently pre-provision
or creating agent variants. However, the Provider requires               large key bundles under realistic deployment conditions.
human-in-the-loop verification during user registration (see
                                                                         G. Experiments on Amazon Web Services
Section IV-B), enforced through integration with trusted iden-
tity services.                                                             This section presents additional experiments evaluating the
                                                                         system’s Agent Capacity (C) under realistic cloud deployment



                                                                    19
  Throughput (reqs/min)                                                                Throughput (reqs/min)
                                       Replicas                                                                                 Replicas
                                      No-RAFT (1-node)                                                         150K            No-RAFT (1-node)
                          400K
                                      RAFT (3-node)                                                                            RAFT (3-node)
                                      RAFT (5-node)                                                            100K            RAFT (5-node)
                          200K
                                                                                                               50K


                           0K                                                                                   0K
                                 1         2            3          4   5   10                                            1           2             3           4       5    10
                                                          Sharders                                                                                    Sharders

                                                (a) 10 OTKs                                                                                    (a) 10 OTKs




  Throughput (reqs/min)                                                                Throughput (reqs/min)
                          200K         Replicas                                                                100K             Replicas
                                      No-RAFT (1-node)                                                                         No-RAFT (1-node)
                          150K        RAFT (3-node)                                                            75K             RAFT (3-node)
                                      RAFT (5-node)                                                                            RAFT (5-node)
                          100K                                                                                 50K

                          50K                                                                                  25K

                           0K                                                                                   0K
                                 1         2            3          4   5   10                                            1           2             3           4       5    10
                                                          Sharders                                                                                    Sharders

                                               (b) 100 OTKs                                                                                (b) 100 OTKs

                          40K




  Throughput (reqs/min)                                                                Throughput (reqs/min)
                                                                                                               20K
                                      Replicas                                                                                 Replicas
                                     No-RAFT (1-node)                                                                         No-RAFT (1-node)
                          30K                                                                                  15K
                                     RAFT (3-node)                                                                            RAFT (3-node)
                          20K        RAFT (5-node)                                                             10K            RAFT (5-node)


                          10K                                                                                  5K

                          0K                                                                                   0K
                                 1         2          3            4   5   10                                           1           2             3            4      5     10
                                                        Sharders                                                                                   Sharders

                                               (c) 1000 OTKs                                                                               (c) 1000 OTKs
Fig. 10: Agent Registration Throughput for varying OTK key-                          Fig. 11: OTK Refresh Throughput for varying OTK key-chain
chain sizes.                                                                         sizes.


conditions. Recall that Agent Capacity is defined as the total                                                 300M
number of active agents that the system can support concur-                                                    250M    Sharders (NS )




                                                                                       Total Agents (C)
rently.                                                                                                                          1
                                                                                                               200M
   We deploy the Provider registry service on Amazon                                                                             3
                                                                                                               150M              5
Web Services (AWS)4 . The deployment consists of a single
                                                                                                               100M              7
proxy node and up to seven sharder nodes, each hosted on a
dedicated EC2 instance in the US-East region. The proxy node                                                   50M
routes incoming requests to the appropriate sharder to ensure                                                   31K
balanced workload distribution across the cluster. Sharders                                                           1 min             1 hr            6 hr        12 hr    24 hr
                                                                                                                                               Token Lifetime (L)
are configured to run RAFT with 5-node replication for fault
tolerance.                                                                           Fig. 12: Total Capacity C of the system for various numbers
   The proxy instance uses a virtual machine of type                                 of sharders on AWS. Each sharder is running RAFT with 5
c7i.xlarge (4 vCPUs) optimized for compute, while the                                nodes.
sharder instances use i4i.xlarge (4 vCPUs) for storage-
intensive workloads. Due to AWS account limits, we were
 4 https://aws.amazon.com/                                                           constrained to 8 total EC2 instances, 32 vCPUs, and ap-



                                                                                20
proximately 100K IOPS in total (4 vCPUs/12GB of attached
storage per instance). Within these limits, we selected the
best available configuration for high-throughput, fault-tolerant
deployment. The proxy is configured with 128 threads to max-
imize request concurrency and dispatches 80,000 requests per
experiment. These parameters were tuned to avoid triggering
AWS rate limits during evaluation.
   Figure 12 reports the system’s agent capacity for varying
token lifetimes (L) and number of sharders (NS ). Results
confirm the scalability trends shown in Figure 6c, reinforcing
the validity of our analysis. With 7 sharders and a 24-hour
token lifetime, the system supports up to 260 million agents.
We note that as expected, the absolute values for C are
slightly lower than those reported in Figure 6c, due to practical
constraints: our AWS experiments were limited to 7 sharders
(versus 10), and despite co-locating all instances in the same
geographic region, we cannot guarantee placement within
the same physical datacenter, introducing additional network
latency. Nevertheless, the observed trends align closely with
our previous analysis. Increasing the number of sharders
or extending the token lifetime yields a predictable, nearly
multiplicative increase in supported agent population. This em-
pirical validation confirms that SAGA remains performant and
scalable under realistic cloud-based infrastructure conditions.




                                                                    21
                    Agent B
                    Let’s find some time to discuss our NDSS submission. Are you available on Tuesday for a 30-minute
                    meeting? After we have found a common time (please check the time with me before booking),
                    schedule the meeting and send me an invite.


    Agent A
    I am available for a 30-minute meeting on Tuesday, April 22, 2025, from 9:00 AM to 9:30 AM.
    Does this time work for you? Please confirm before I schedule the meeting.


                    Agent B
                    I am not available at 9:00 AM to 9:30 AM on Tuesday, April 22, 2025. However, I am available
                    from 12:00 PM to 12:30 PM on the same day. Does this time work for you?


    Agent A
    I am not available at 12:00 PM to 12:30 PM on Tuesday, April 22, 2025. However, I am available
    from 2:00 PM to 2:30 PM on the same day. Does this time work for you? Please confirm before I
    schedule the meeting.


                    Agent B
                    I am available from 2:00 PM to 2:30 PM on Tuesday, April 22, 2025. Please confirm if this time
                    works for you and provide your email address so I can schedule the meeting.


    Agent A
    Yes, I am available for the meeting on Tuesday, April 22, 2025, from 2:00 PM to 2:30 PM. Please
    go ahead and schedule the meeting and send the invite.


                    Agent B
                    Please provide your email address so I can add you as a participant and send the meeting invite for
                    the NDSS submission discussion on Tuesday, April 22, 2025, from 2:00 PM to 2:30 PM.


    Agent A
    My email address is <REDACTED>. Please use it to add me as a participant and send the meeting
    invite for the NDSS submission discussion on Tuesday, April 22, 2025, from 2:00 PM to 2:30 PM.


                    Agent B
                    The meeting for the NDSS submission discussion has been scheduled on Tuesday, April 22, 2025,
                    from 2:00 PM to 2:30 PM. You have been added as a participant, and the invite has been sent to
                    <REDACTED>.

    Agent A
    <TASK_FINISHED>

Fig.    13:    Example dialog between agents for   the    calendar-scheduling   task,   using     GPT-4.1-mini
(gpt-4.1-mini-2025-04-14) as the backend LLM. Contact information mentioned during interactions is redacted for
visualization.


                                                           22
                    Agent B
                    Can you please check your emails for any expenses for our recent trip for NerurIPS to New Orleans
                    from 03-01 to 03-03 Tell me what your expenses were (including hotel, travel, food, etc.) and your
                    email ID. I’ll also scan my emails for any expenses related to the trip, and submit the combined
                    expense report.


    Agent A
    Here are my expenses for the NeurIPS trip to New Orleans (03-01 to 03-03):
    - Hotel: $500 (Hilton, 2 nights: 03-01 to 03-03)
    - Food: $20 (Breakfast at Dumbo Gumbo, 03-01)
    - Food: $50 (Dinner at Dumbo Gumbo, 03-01)
    - Conference Registration: $1000 (NeurIPS workshop)
    My email ID is: <REDACTED>


                    Agent B
                    The expense report for the NeurIPS trip to New Orleans (03-01 to 03-03) has been submitted
                    successfully. The report includes your provided expenses as well as additional receipts found in
                    my inbox (flight, extra meals, and a WH Smith purchase). The total submitted amount is $2,140,
                    and you (<REDACTED>) are listed as involved. If you need a detailed breakdown or a copy of the
                    report, let me know.


    Agent A
    Thank you for letting me know! I appreciate the update. If I need a detailed breakdown or a copy
    of the report, I’ll reach out.


                    Agent B
                    <TASK_FINISHED>

Fig. 14: Example dialog between agents for the expense-report task, using GPT-4.1 (gpt-4.1-2025-04-14) as the backend
LLM. Contact information mentioned during interactions is redacted for visualization.




                                                           23
