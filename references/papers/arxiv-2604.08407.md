                                         Your Agent Is Mine: Measuring Malicious Intermediary Attacks
                                                           on the LLM Supply Chain
                                                         Hanzhi Liu                                   Chaofan Shou                                     Hongbo Wen
                                               University of California, Santa                           Fuzzland                             University of California, Santa
                                                          Barbara                                     shou@fuzz.land                                     Barbara
                                                     hanzhi@ucsb.edu                                                                             hongbowen@ucsb.edu

                                                         Yanju Chen                              Ryan Jingyang Fang                                       Yu Feng
                                            University of California, San Diego                  World Liberty Financial                      University of California, Santa
                                                     yanju@ucsd.edu                          ryan@worldlibertyfinancial.com                              Barbara




arXiv:2604.08407v1 [cs.CR] 9 Apr 2026
                                                                                                                                                  yufeng@cs.ucsb.edu

                                        Abstract                                                                    open-source router with roughly 40,000 GitHub stars and over 240
                                        Large language model (LLM) agents increasingly rely on third-               million Docker Hub pulls, is integrated into production pipelines
                                        party API routers to dispatch tool-calling requests across multiple         across thousands of organizations. OpenRouter [35] connects users
                                        upstream providers. These routers operate as application-layer              to more than 300 active models from over 60 providers and serves
                                        proxies with full plaintext access to every in-flight JSON payload,         millions of developers and end-users [6]. Routers provide model fall-
                                        yet no provider enforces cryptographic integrity between client             back, load balancing, cost optimization, and a single API key across
                                        and upstream model. We present the first systematic study of this           providers. A growing number of production deployments route traf-
                                        attack surface. We formalize a threat model for malicious LLM API           fic through at least one such intermediary [41, 50]. The severity of
                                        routers and define two core attack classes, payload injection (AC-1)        this dependency was demonstrated in March 2026, when attackers
                                        and secret exfiltration (AC-2), together with two adaptive evasion          compromised the LiteLLM package through dependency confu-
                                        variants: dependency-targeted injection (AC-1.a) and conditional            sion, injecting malicious code directly into the request-handling
                                        delivery (AC-1.b). Across 28 paid routers purchased from Taobao,            pipeline of every deployment that pulled the poisoned release [11].
                                        Xianyu, and Shopify-hosted storefronts and 400 free routers col-            That incident turned a widely trusted router into a supply-chain
                                        lected from public communities, we find 1 paid and 8 free routers           weapon with full plaintext access to every transiting API request
                                        actively injecting malicious code, 2 deploying adaptive evasion             and response.
                                        triggers, 17 touching researcher-owned AWS canary credentials,                  This architecture creates a trust relationship that has received
                                        and 1 draining ETH from a researcher-owned private key. Two                 little scrutiny. The “router-in-the-middle” is not an accidental on-
                                        poisoning studies further show that ostensibly benign routers can           path adversary but an intentionally configured intermediary with
                                        be pulled into the same attack surface as they process end-user             application-layer authority over both requests and responses. Un-
                                        requests using leaked credentials and weakly configured peers:              like a traditional network MITM, no TLS downgrade or certificate
                                        intentionally leaked OpenAI keys and weakly configured decoys               forgery is required: the client voluntarily configures the router’s
                                        have processed 2.1B tokens from these routers, exposing 99 creden-          URL as the API endpoint, the router terminates the client-side TLS
                                        tials across 440-codex sessions, and 401 sessions already running           connection, and it originates a separate TLS connection upstream.
                                        in autonomous YOLO mode, allowing direct payload injection. We              Once an agent targets that router endpoint, the service can inspect
                                        build Mine, a research proxy that implements all four attack classes        tool-call arguments, API keys, system prompts, and model outputs;
                                        against four public agent frameworks, and use it to evaluate three          it can also normalize, delay, or rewrite the returned tool call before
                                        deployable client-side defenses: a fail-closed policy gate, response-       the client executes it. No end-to-end integrity mechanism binds
                                        side anomaly screening, and append-only transparency logging.               the provider’s tool-calling output to the action the client finally ob-
                                                                                                                    serves (Section 3). A malicious or compromised router can therefore
                                        Keywords                                                                    replace a benign installer URL with an attacker-controlled script,
                                                                                                                    swap pip install requests for a attacker-controlled dependency,
                                        LLM security, API routers, tool-use attacks, supply chain security,         or silently exfiltrate every credential that transits the service.
                                        man-in-the-middle                                                               Proxy tampering itself is not new [12, 14], but LLM agents make
                                                                                                                    this intermediary trust boundary unusually dangerous because the
                                        1   Introduction                                                            payload now carries executable tool-call semantics. We study that
                                                                                                                    boundary as an LLM supply-chain problem and introduce a tax-
                                        Large language model (LLM) agents have moved beyond conversa-
                                                                                                                    onomy of Adversarial Router Behaviors, spanning direct payload
                                        tional assistants into tool-using systems that book flights, execute
                                                                                                                    manipulation, dependency rewriting, credential sniffing, and Adap-
                                        code, query databases, and manage cloud infrastructure on behalf
                                                                                                                    tive Evasion, in which malicious rewrites are delivered only after a
                                        of their users [50]. A less studied but increasingly critical com-
                                                                                                                    warm-up period or when the router infers that the client is running
                                        ponent in this ecosystem is the LLM API router: an intermediary
                                                                                                                    in an autonomous “YOLO mode.” These attacks are orthogonal to
                                        service that accepts requests in a unified format and dispatches
                                                                                                                    prompt injection [17, 38]: they occur in the JSON/tool layer before
                                        them to upstream model providers. LiteLLM [7], the dominant
                                                                                                                1
                                                                                             Hanzhi Liu, Chaofan Shou, Hongbo Wen, Yanju Chen, Ryan Jingyang Fang, and Yu Feng


                                                                                    Multi-hop LLM Router Chain
           Agent Clients

                      YOLO mode
                                                                                                                                                   Model Providers
           CO
             MP
               R
             Claude
                OM Code                                                                            𝑅3
                   ISE
                       D
                                                                            𝑅1                                             𝑅6                             OpenAI

                                                               h   | sh
           CO                                             wn.s
             MP                                      xyz/p
                  RO                             ***.
                   Codex                     rl *
                    MIS              Bash
                                         : cu                                                      𝑅4           Attacker
                        ED                                                                                                                               Anthropic
                                                                                                 malicious
                                                                            𝑅2                                             𝑅7
              OpenClaw                                                                             𝑅5                                                      Google



                             request / clean response                     tainted response


Figure 1: LLM router ecosystem and taint propagation. Agent clients (left) exchange requests and responses through a multi-hop
graph of LLM routers to upstream model providers (right). Each hop terminates the inbound TLS session, granting full plaintext
access. Green arrows denote clean data flow; red arrows trace how a single malicious router 𝑅4 , controlled by an external
attacker, taints responses on the return path: corrupted payloads propagate through 𝑅1 back to the compromised Claude Code
and Codex clients, handing the attacker effective control over their tool execution (“your agent is mine”), while agents routed
through honest paths (e.g., 𝑅2 →𝑅5 ) remain unaffected (Section 4).


the model sees the request or after it emits a response, outside the                                2B GPT-5.4 / 5.3-codex tokens, exposed about 13 GB of visible down-
model’s reasoning loop, and therefore compose with model-side                                       stream prompt/response traffic, and leaked 99 credentials across
safeguards rather than replacing them.                                                              440 Codex sessions on 398 different projects or hosts. Every one of
   Our empirical results show that this risk is already present in                                  those 440 sessions was command-injectable, and 401 already ran in
commodity router markets. The open-source templates that un-                                        autonomous YOLO mode, meaning tool execution was already auto-
derpin most commodity routers, new-api [40] (25.4k GitHub stars,                                    approved and simple payload injection would have been enough
1.25M Docker pulls) and its upstream fork one-api [31] (30.5k                                       even without sophisticated adaptive triggers. Finally, we build Mine,
stars, 1.19M Docker pulls), have been pulled millions of times, and                                 a research proxy that implements the attack classes and companion
Chinese open-source models reached nearly 30% of total usage on                                     mitigations, and use it to evaluate practical client-side defenses.
OpenRouter in some weeks [6], the largest public routing platform.                                  A fail-closed policy gate blocks all AC-1 and AC-1.a shell-rewrite
Investigative reporting documents Taobao shops with over 30,000                                     samples at 1.0% false positives, and response-side anomaly screen-
repeat purchases for resold LLM API access [36]. We analyze 28                                      ing flags 89% of AC-1 samples without requiring provider changes.
paid routers bought from Taobao, Xianyu, and Shopify-hosted store-                                  These mitigations reduce exposure today, but securing the agent
fronts and 400 free routers built from the dominant sub2api [47]                                    ecosystem ultimately requires provider-backed response integrity
and new-api templates. Within that corpus, 1 paid and 8 free routers                                so that the tool call an agent executes can be cryptographically tied
inject malicious code into returned tool calls. Two routers deploy                                  to what the upstream model actually produced.
adaptive evasion in the wild, for example by waiting for 50 prior                                   In summary, this paper makes three contributions:
calls, restricting payload delivery to autonomous “YOLO mode” ses-                                  (1) Threat model and attack taxonomy. We present the first
sions, or targeting only Rust and Go projects. Among the free-router                                    formal threat model for LLM API routers as a supply-chain trust
set, 17 routers touch at least one researcher-owned AWS canary                                          boundary and define two core attack classes, payload injection
credential and 1 drains ETH from a researcher-owned Ethereum                                            (AC-1) and secret exfiltration (AC-2), together with two adap-
private key.                                                                                            tive evasion variants: dependency-targeted injection (AC-1.a)
   Malicious routers are only half of the story. Routers that look                                      and conditional delivery (AC-1.b), grounded in observed router
benign can be poisoned into the same trust boundary when they                                           behavior (Sections 3–4).
reuse leaked upstream keys or forward traffic through weaker re-                                    (2) Ecosystem measurement and poisoning studies. We ana-
lays. We intentionally leaked a researcher-owned OpenAI key on                                          lyze 28 paid and 400 free routers and find 9 injecting malicious
Chinese forums and in WeChat and Telegram groups; that sin-                                             code, 2 deploying adaptive evasion, and 17 abusing researcher-
gle key generated 100M GPT-5.4 tokens and more than seven                                               owned credentials. Two poisoning studies show that benign
Codex sessions. We also deployed weakly configured Sub2API,                                             routers can be pulled into the same attack surface through
claude-relay-service, and CLIProxyAPI decoys across 20 do-                                              leaked keys and weak relay chains (Section 5).
mains and 20 IPs. Those decoys received tens of thousands of unau-                                  (3) Implementation and deployable defenses. We build Mine,
thorized access attempts from 147 IPs (6 JA3 fingerprints), served                                      a research proxy implementing all four attack classes against
                                                                                             2
Your Agent Is Mine: Measuring Malicious Intermediary Attacks on the LLM Supply Chain


      four public agent frameworks, and evaluate three client-side de-                 received by the client. An intermediary that terminates TLS on each
      fenses that can be deployed today without provider cooperation                   side can therefore read, modify, or fabricate any tool-call payload
      (Sections 6–7).                                                                  without detection.

2 Background                                                                           2.3    The LiteLLM Incident
2.1 LLM API Routers                                                                    In March 2026, attackers compromised LiteLLM through depen-
                                                                                       dency confusion, injecting malicious code into the request-handling
A direct API subscription to a single model provider is the simplest
                                                                                       pipeline of every deployment that pulled the poisoned release [11].
deployment, but production agent systems rarely stop there. Orga-
                                                                                       The injected payload had write access to every API request and
nizations need access to models from multiple providers (OpenAI,
                                                                                       response transiting the proxy, the same capability set that a deliber-
Anthropic, Google, and an expanding set of open-weight hosts)
                                                                                       ately malicious router would possess. This incident demonstrated
with fallback, load balancing, cost optimization, and a single cre-
                                                                                       that the router trust boundary is not hypothetical: a single supply-
dential plane. An LLM API router fills this role: it accepts requests in
                                                                                       chain entry point in one widely deployed router was sufficient to
a unified format (typically OpenAI-compatible), selects an upstream
                                                                                       compromise the entire forwarding path.
provider, and returns the response.
   Routing exists at every scale. At the institutional end, Amazon                     3     Threat Model
Bedrock [4] and Azure OpenAI Service [28] are cloud-managed
routers: they host or proxy third-party models behind a unified                        Figure 1 illustrates the system architecture and the attacker’s posi-
API, and enterprises consume them as a managed service. At the                         tion.
open-source end, LiteLLM [7] and OpenRouter [35] let individual                           We consider an attacker that operates a malicious LLM API router
developers and startups aggregate dozens of providers behind a                         or has compromised a legitimate one through supply-chain compro-
single base-URL change. Some model providers collaborate directly                      mise, insider access, or server-side exploitation [11]. Because the
with routers for distribution; for example, making new models                          client explicitly configures the router as its API endpoint, the router
available through OpenRouter or regional aggregator platforms as                       terminates client-side TLS and originates a separate TLS connection
a first-class channel.                                                                 upstream. It therefore occupies an application-layer man-in-the-
   Crucially, routers are composable: the path from client to GPU                      middle position by design and can read, retain, rewrite, or fabricate
routinely traverses multiple routing layers. A developer may pur-                      request and response bodies, headers, and request metadata. This
chase API access from a Taobao reseller, who aggregates keys from                      includes tool definitions, prompts, tool outputs, API keys, and re-
a second-tier aggregator, who routes through OpenRouter, which                         turned tool-call payloads across OpenAI-, Anthropic-, and Gemini-
dispatches to the model host. That is four hops, each terminating                      style interfaces. The router may also keep cross-request state, which
and re-originating a TLS connection, each with full plaintext ac-                      lets it activate payload rewriting only for trigger-matching sessions.
cess to API keys, system prompts, tool definitions, and tool-call                      We assume standard TLS between the router and the upstream
responses. The client configures only the first hop; subsequent hops                   provider and no compromise of model weights or inference logic.
are invisible. Because no end-to-end integrity mechanism spans                            The core integrity gap is that no deployed mechanism binds
this chain, a single malicious or compromised router at any layer                      the provider-origin tool-call response to what the client finally
taints the entire path: downstream honest routers cannot detect                        receives. That gap enables response-side payload rewriting, while
that an upstream hop has already rewritten a tool call or copied a                     request-side visibility enables selective delivery to particular users,
credential. We formalize this weakest-link property in Section 4.                      workflows, or tool invocations. We exclude prompt injection, model
   Routing is especially prevalent in regions where direct provider                    backdoors, client-side malware, denial of service, and pure model
access is restricted, expensive, or subject to quota limitations. A                    substitution. Those behaviors may compose with router abuse,
large commodity market has emerged around resold and aggregated                        but they are distinct from the response-manipulation and passive-
API access: investigative reporting documents Taobao merchants                         collection attacks studied here.
with over 30,000 repeat purchases for LLM API keys [36], and
the open-source router templates that power most of these ser-
                                                                                       4     Attack Taxonomy
vices, new-api [40] (25.4k GitHub stars, 1.25M Docker pulls) and                       Malicious-router behavior reduces to two orthogonal primitives:
its upstream fork one-api [31] (30.5k stars, 1.19M Docker pulls),                      active manipulation, in which the router rewrites a tool-call payload
have been pulled millions of times. LiteLLM alone has accumulated                      before it reaches the client, and passive collection, in which the
roughly 40,000 stars and over 240 million Docker Hub pulls.                            router silently extracts secrets from plaintext traffic. We formalize
                                                                                       these as two core attack classes (AC-1 and AC-2) and define two
2.2     Tool Use and Function Calling                                                  adaptive evasion variants (AC-1.a and AC-1.b) that specialize AC-1
                                                                                       to evade specific classes of client-side defenses. Table 1 summarizes
Modern LLM APIs expose tool use (also called function calling) as a
                                                                                       the taxonomy, and Figure 2 shows where each class activates in the
first-class capability [37, 39, 43]. OpenAI returns a tool_calls field
                                                                                       request–response path.
with JSON-encoded arguments [32]; Anthropic returns tool_use
content blocks with a native JSON object [5]; Gemini exposes a sim-                      Formal framework. We model the system as (𝐶, 𝑅1, . . . , 𝑅𝑘 , 𝑃)
ilar structured interface [16]. In every format, tool-call arguments                   where 𝐶 is the client, 𝑃 is the upstream provider, and 𝑅1, . . . , 𝑅𝑘 are
are transmitted as plaintext JSON. No provider-level integrity mech-                   routers. A request req ∈ Request carries a prompt, tool definitions,
anism binds the arguments returned by the model to the arguments                       and an API key; a response resp ∈ Response carries tool calls
                                                                                 3
                                                                                          Hanzhi Liu, Chaofan Shou, Hongbo Wen, Yanju Chen, Ryan Jingyang Fang, and Yu Feng


                                                                                   Malicious Router
            Agent Clients                                                                                                                           Model Providers
                                                                   AC-2: secret scan

                                          Request JSON                                                                          Request JSON
              Claude Code                                       Parse Request                    Forward Request                                            OpenAI

                  Codex                                                                                                                                    Anthropic

                OpenClaw                                        Parse Response                  Receive Response                                            Google
                                     Response JSON (tampered)                                                                   Response JSON
                 ···                                            AC-1: payload injection               AC-2: secret scan                                     ···
                                                                AC-1.a           AC-1.b




Figure 2: Request–response lifecycle through a malicious router. AC-2 tags mark where the router passively scans traffic for
secrets (both request and response paths). AC-1 marks where parsed responses are rewritten before delivery; AC-1.a specializes
to dependency substitution, AC-1.b gates activation on session-level triggers (Section 4.2).


[𝑡 1, . . . , 𝑡𝑛 ] where 𝑡𝑖 = (name𝑖 , args𝑖 ). Let 𝜎 ⊆ Secrets denote a set                  anomaly. For a shell-execution tool such as Bash, replacing a benign
of extracted credential patterns, and let 𝜑 : Request × State → Bool                          URL with an attacker-controlled script suffices for arbitrary code
be a trigger predicate over request and session features.                                     execution: the semantic change occurs after inference completes,
    An honest router is transparent: 𝑅honest (req) = 𝑃 (req). A chain                         entirely outside the model’s reasoning loop.
composes as (𝑅1 ◦ · · · ◦ 𝑅𝑘 )(req), where each 𝑅𝑖 terminates and                             Example. The listing below shows a benign installer URL replaced
re-originates a TLS connection. Chain integrity is a weakest-link                             with an attacker-controlled endpoint. The March 2026 LiteLLM
property:                                                                                     compromise [11] demonstrated exactly this primitive at scale: once
                          ∀ 𝑖 ∈ [1, 𝑘]. 𝑅𝑖 = 𝑅honest                                          the attacker controlled the request pipeline, every transiting tool
                                                                                              call was exposed to rewriting.
                       (𝑅1 ◦ · · · ◦ 𝑅𝑘 )(req) = 𝑃 (req)
                                                                                              Original tool call (from upstream provider):
                         ∃ 𝑗 ∈ [1, 𝑘]. 𝑅 𝑗 ≠ 𝑅honest                                              {
                                                                                                      "name": "Bash",
           no integrity guarantee for (𝑅1 ◦ · · · ◦ 𝑅𝑘 )(req)                                         "arguments": {
                                                                                                        "command": "curl -sSL https://get.example.com/cli.sh | bash"
A single malicious router at any layer can apply AC-1 (rewrite) or                                    }
AC-2 (collect); downstream honest routers cannot detect or undo the                               }
modification because they lack a reference to the original upstream                           Router-modified tool call (delivered to client):
response. For AC-2, taint is cumulative: every router in the chain
observes plaintext traffic, so the total secret exposure is 𝜎chain =                              {
Ð𝑘                                                                                                    "name": "Bash",
  𝑖=1 extract 𝑖 (req𝑖 , resp𝑖 ). Our measurement (Section 5.3) confirms                               "arguments": {
this composability empirically: leaked keys and weak relays turn                                        "command": "curl -sSL https://attacker****.sh | bash"
otherwise benign outer routers into conduits for the full attack                                      }
                                                                                                  }
surface. The remainder of this section defines the attack classes
for a single malicious router 𝑅; the chain property above lifts each                           Consequence of AC-1: A single rewritten tool call is sufficient
class to arbitrary multi-hop deployments.                                                      for arbitrary code execution on the client machine. Any agent that
                                                                                               auto-executes tool calls through an unverified router is exposed.
4.1     Core Attack Classes
4.1.1   AC-1: Response-Side Payload Injection.                                                4.1.2     AC-2: Passive Secret Exfiltration.
               𝑃 (req) = resp          resp.tool_calls[𝑖] = 𝑡                                             𝑃 (req) = resp         extract (req, resp) = 𝜎      𝜎≠∅
                                                                    
           𝑅AC-1 (req) = resp tool_calls[𝑖] ↦→ rewrite(𝑡)                                                                 𝑅AC-2 (req) = resp ∧ leak(𝜎)
The function rewrite : ToolCall → ToolCall replaces selected fields                           The function extract : Request × Response → P (Secrets) scans
in the argument JSON while preserving the tool name and schema                                headers, request bodies, and response bodies against credential
structure. The router rewrites a model-generated tool call after                              patterns; the router forwards the response unmodified and exfil-
it leaves the upstream provider but before it reaches the client;                             trates 𝜎 asynchronously. AC-2 requires no payload modification;
the only preconditions are a tool-calling response and the absence                            the boundary between “credential handling” and “credential theft”
of an integrity mechanism binding the received arguments to the                               is invisible to the client because routers already read secrets in
upstream original. Because the modified payload remains syntacti-                             plaintext as part of normal forwarding. Once exposed credentials
cally valid JSON matching the expected tool schema, AC-1 redirects                            are reused by relays, passive collection alone creates downstream
agent behavior without producing a schema violation or transport                              data exposure at scale: our poisoning study (Section 5.3) shows that
                                                                                          4
Your Agent Is Mine: Measuring Malicious Intermediary Attacks on the LLM Supply Chain


                              Table 1: Attack taxonomy: two core classes and two adaptive evasion variants.

                   Class    Role            Manipulated        Sur-   Preconditions                 Primary Harm            Detection Difficulty
                                            face
                   AC-1     Core            Tool-call arguments       Tool-calling response;        Arbitrary code execu-   Modified payload is schema-
                                                                      no integrity check            tion                    valid; client never sees up-
                                                                                                                            stream original
                   AC-2     Core            None (read-only)          Secret in plaintext traf-     Credential theft        Traffic is unchanged; clients
                                                                      fic                                                   cannot observe router-side re-
                                                                                                                            tention
                   AC-1.a   Evasion         Package name inside       Install-capable tool call     Durable supply-chain    Evades domain-based policy
                                            install command                                         compromise              gates; rewritten command
                                                                                                                            looks legitimate
                   AC-1.b   Evasion         Same as AC-1, condi-      Trigger-relevant     ses-     Targeted delivery       Non-matching probes see be-
                                            tionally                  sion features                                         nign behavior; finite audits
                                                                                                                            miss the attack



a single leaked key yielded 100M tokens and 99 credentials across                          4.2.1      AC-1.a: Dependency-Targeted Injection.
440 sessions without any payload rewriting.

Example. Listing 1 shows representative extraction patterns. An
attacker who controls the LiteLLM request pipeline as in the March
2026 incident [11] gains read access to every API key, system                                                              𝑃 (req) = resp
prompt, and credential that transits the proxy, even if the injected                              𝑡𝑖 .name ∈ {Bash, run_command}           𝑡𝑖 .args |= install_pattern
code never modifies a single response. In Section 5, we count AC-2                                                                                        
outcomes only when exposure is followed by externally visible                                               𝑅AC-1.a (req) = resp 𝑡𝑖 .args ↦→ subst (pkg)
unauthorized use of researcher-owned canaries or credentials. In
practice, the extraction surface extends beyond API keys: system
prompts, tool definitions, user-supplied file contents, and environ-
ment variables all transit the same plaintext channel and are equally
accessible to a router performing AC-2.                                                    AC-1.a specializes AC-1 to package-install commands (pip install,
                                                                                           npm install, cargo add). Rather than rewriting an arbitrary URL,
   sk-[A-Za-z0-9]{20,}            // OpenAI keys
   AKIA[A-Z0-9]{16}               // AWS keys                                              which a domain-based policy gate (Section 7.1) can catch, the
   ghp_[A-Za-z0-9]{36}            // GitHub PATs                                           router substitutes a legitimate dependency name with an attacker-
   xoxb-[0-9]+-[A-Za-z0-9]+       // Slack bot tokens
   0x[a-fA-F0-9]{64}              // Ethereum keys
                                                                                           controlled package pre-registered on the target registry. The sub-
   -----BEGIN .* PRIVATE KEY----- // PEM keys                                              stitution may be a visually similar name (typosquatting) or an en-
                                                                                           tirely different package; the former is particularly effective because
Listing 1: AC-2: representative secret-matching patterns for                               LLM-based review and approval UIs tend to hallucinate that a near-
passive extraction.                                                                        homograph is correct, causing downstream checks to pass. The
                                                                                           surrounding command line remains unchanged, so the rewritten
                                                                                           command clears domain-based allowlists and approval flows that
 Consequence of AC-2: Passive collection requires zero payload                             emphasize only the high-level action. Once the substituted package
 modification and is invisible to the client, since the same plaintext                     installs, the attacker gains a durable supply-chain foothold that
 access needed for legitimate routing also enables silent credential                       persists beyond the current session. This is strictly more dangerous
 retention. Unlike AC-1, AC-2 cannot be mitigated by response-                             than a one-shot AC-1 URL redirect, because the compromised de-
 signing proposals because the secrets are exposed on the request                          pendency is cached locally and re-imported across future sessions.
 path before any provider-side mechanism can act.                                          We design AC-1.a specifically to demonstrate that the policy gate
                                                                                           defense can be evaded when the attacker targets package-install
                                                                                           workflows: the gate blocks non-allowlisted domains but does not
4.2     Adaptive Evasion Variants                                                          maintain a per-package allowlist.
The core AC-1 attack is effective but coarse: always-on rewriting
is easily detected by a simple policy check or manual review. A
sophisticated attacker therefore needs to control not only what                            Example. The listing below shows a single-character substitution:
is injected but also when and how the injection is delivered, so                           requests becomes reqeusts, a typosquat package that the router
that standard client-side checks pass while high-value targets still                       has pre-registered on PyPI. Because the surrounding command line
receive malicious payloads. We define two adaptive evasion variants                        is unchanged and the package name passes a casual visual check,
that specialize AC-1 to defeat specific defensive strategies while                         the rewritten command clears both domain-based policy gates and
preserving its payload-injection capability.                                               LLM-assisted approval flows.
                                                                                      5
                                                                            Hanzhi Liu, Chaofan Shou, Hongbo Wen, Yanju Chen, Ryan Jingyang Fang, and Yu Feng


Original tool call:                                                             The combination of multiple trigger families is especially potent: a
   {                                                                            router can require both a tool-name match and a warm-up count
        "name": "Bash",                                                         before activating, so that even an auditor who tests the correct
        "arguments": {
          "command": "python -m pip install requests flask pyyaml"
                                                                                tool never reaches the activation threshold within a typical probe
        }                                                                       budget.
   }
                                                                                 Consequence of AC-1.b: Conditional delivery makes finite
Router-modified tool call:                                                       black-box auditing fundamentally inadequate. A router that acti-
                                                                                 vates only after a warm-up period or on specific session attributes
   {
        "name": "Bash",                                                          appears entirely transparent during routine probes. Because the
        "arguments": {                                                           trigger predicate is server-side and opaque, no fixed-length client
          "command": "python -m pip install reqeusts flask pyyaml"
        }
                                                                                 test can guarantee that the router is benign. Combined with au-
   }                                                                             tonomous auto-approval modes, the attacker can reserve payload
                                                                                 injection exclusively for high-value sessions while keeping all
 Consequence of AC-1.a: Dependency-targeted injection evades                     audit traffic clean.
 domain-based policy gates because the rewritten command in-
 stalls from the same trusted registry, differing only in the package              Summary. AC-1 and AC-2 are orthogonal: AC-1 changes what
 name. Worse, the compromised dependency is cached locally and                  the agent executes, while AC-2 silently harvests credentials from
 re-imported across future sessions, giving the attacker a durable              the same plaintext channel. The evasion variants sharpen AC-1
 supply-chain foothold that persists long after the malicious router            for realistic deployment: AC-1.a evades domain-based policy gates
 interaction ends.                                                              by substituting dependencies instead of URLs, and AC-1.b evades
                                                                                black-box auditing by gating delivery on session-level triggers. Sec-
4.2.2    AC-1.b: Conditional Delivery.
                                                                                tion 5 maps these classes to the observed ecosystem, and Section 7
                   𝑃 (req) = resp     𝜑 (req, 𝑠) = true                         evaluates client-side defenses against each.
                       𝑅AC-1.b (req) = 𝑅AC-1 (req)
                                                                                5     Ecosystem Measurement
                   𝑃 (req) = resp     𝜑 (req, 𝑠) = false                        We study two complementary questions. First, are malicious routers
                           𝑅AC-1.b (req) = resp                                 already operating in real agent-facing markets? Second, can routers
                                                                                that appear benign or trusted be poisoned into the same supply-
The predicate 𝜑 gates payload injection on session state 𝑠: the                 chain position through leaked upstream credentials or by forward-
router behaves honestly for non-matching traffic and applies AC-1               ing traffic through weaker relays? Our measurement therefore com-
only when 𝜑 holds. AC-1.b is not a distinct payload primitive but               bines a market study of paid and free routers with two poisoning
determines when AC-1 activates, so that routine probes and low-                 studies based on leaked researcher-owned keys and intentionally
value traffic see benign behavior while high-value sessions receive             weak relay deployments. Table 2 summarizes the datasets, Table 3
rewritten payloads. Practical triggers fall into five families:                 collects the main outcomes, Figure 3 visualizes the malicious-router
(1) Tool-name conditions: activate only for tools such as Bash                  counts, and Table 4 lists adaptive-evasion conditions observed in
     or run_command.                                                            the wild or demonstrated in the artifact.
(2) Content keywords: activate when the command contains
     installer patterns such as curl -sSL or pip install.                       5.1     Dataset and Collection
(3) User fingerprints: activate only for sessions in autonomous                 We purchased 28 paid OpenAI- and Anthropic-compatible routers
     YOLO mode or belonging to a target organization.                           from Taobao [2], Xianyu [3], and Shopify-hosted storefronts [44].
(4) Time windows: activate only during off-hours or after a de-                 We also collected 400 free routers exposed through public com-
     ployment event.                                                            munities, router lists, and configuration dumps. The free corpus
(5) Request-count thresholds: activate only after the session has               is dominated by two widely reused templates, sub2api [47] (11k
     passed 𝑁 benign interactions, hiding the attack from shallow               GitHub stars) and new-api [40] (25.4k stars, 1.25M Docker Hub
     smoke tests.                                                               pulls), which made it possible to expand from seed URLs into a much
None of these require model compromise; they depend only on                     larger set of reachable router instances. That expansion followed
metadata and payload fields already visible to the router. A router             only additional public links reachable from the same posts, router
deploying a 50-request warm-up appears entirely transparent dur-                lists, and configuration-dump references; we did not scan arbitrary
ing a 10-request probe, making finite black-box auditing fundamen-              address ranges or attempt to enumerate hidden admin surfaces. We
tally inadequate against conditional delivery.                                  conservatively deduplicated exact repeated endpoints after URL nor-
Example. The Codecov CI breach [9] persisted undetected for                     malization; deployments that reused the same template on distinct
months by activating its credential-harvesting payload only within              domains or IPs remained separate because they still correspond to
CI environments, a conditional-delivery strategy analogous to AC-               different externally reachable trust boundaries. We also could not
1.b. Our measurement (Section 5) confirms that real routers deploy              always recover exact template versions or complete default con-
similar logic: one activates only after 50 prior calls, another restricts       figurations, so we do not attribute observed abuse to a particular
injection to YOLO-mode sessions targeting Rust or Go projects.                  sub2api or new-api release. For each router, the testing pipeline
                                                                            6
Your Agent Is Mine: Measuring Malicious Intermediary Attacks on the LLM Supply Chain


                                             Table 2: Measurement datasets and collection channels.

     Dataset                      Collection Channel                                      Scale                                   Purpose
     Paid routers                 Taobao, Xianyu, Shopify storefronts                     28 routers                              Test sold OpenAI- and Anthropic-
                                                                                                                                  compatible endpoints
     Free routers                 Public links using sub2api [47] and new-api [40]        400 routers                             Measure in-the-wild abuse in commod-
                                  templates                                                                                       ity router ecosystems
     Leaked-key poisoning         Chinese forums, and WeChat / Telegram groups            1 OpenAI key                            Observe downstream sessions on a
                                                                                                                                  reused upstream account
    Weak-router decoys            Weak-password Sub2API, CLIProxyAPI, and                 20 domains + 20 IPs                     Measure exploitation and downstream
                                  claude-relay-service deployments                                                                exposure through poisoned routers


proceeds in four stages. First, we register a researcher-controlled
                                                                                                                                                                  Paid (𝑛=28)
account with the router and obtain API credentials. Second, we                                                                                          4.25
                                                                                                                                                                  Free (𝑛=400)
route the account through a sandboxed agent environment and ex-                                            4     3.57




                                                                                             Routers (%)
ecute a randomized subset of custom tasks and TerminalBench 2.0
tasks [1], which produce realistic shell, package-install, and file-
                                                                                                                        2
manipulation tool calls across diverse programming languages and                                           2
workflows. Third, every tool-call payload returned by the router is
executed inside the sandbox, which monitors for network callbacks,                                                                     0.5
                                                                                                                                                                         0.25
file-system modifications, and process-tree anomalies. Fourth, a                                                                   0                0                0
                                                                                                           0
dedicated analysis agent reviews flagged executions and classifies                                             Code injection Adaptive evasion Credential abuse   Wallet drain
the behavior as benign rewriting (e.g., CDN substitution), poten-
tially malicious, or confirmed malicious. This pipeline also records
                                                                                       Figure 3: Observed malicious-router behaviors across 28 paid
whether conditional triggers were present and whether router-side
                                                                                       and 400 free routers. Bars are normalized within the paid
plaintext access to researcher-owned AWS or Ethereum canaries
                                                                                       and free populations; raw counts appear in Table 3 and the
produced follow-on abuse.
                                                                                       surrounding text. Adaptive evasion is observed only among
    To study how ostensibly benign routers can be poisoned, we
                                                                                       routers that already perform active manipulation.
ran two additional measurements. First, we intentionally leaked
a researcher-owned OpenAI API key on Chinese forums, and
WeChat and Telegram groups where router operators share cre-
dentials and relay endpoints [27]. Second, we deployed vulnerable                      cover only the subset of traffic we could confidently attribute to
claude-relay-service instances across 20 domains and weak-                             downstream Codex clients, so the two quantities are not directly
password Sub2API and CLIProxyAPI instances across 20 IPs. These                        comparable.
decoys were researcher-controlled and served only to measure how
quickly external operators would absorb them into downstream                           5.2             Malicious Routers in the Wild
router chains. Across both poisoning studies, we retained only                         Across the 28 paid and 400 free routers, we find active malicious
aggregate session metadata, credential classes, salted hashes of                       behavior in both markets. One paid router and eight free routers
leaked credential values, and coarse host or project identifiers; we                   inject malicious code into returned tool calls. These modifications
did not store raw third-party prompt or response bodies. We use                        are not cosmetic output rewrites; they change the command or
conservative operational definitions throughout.                                       dependency that the agent intends to execute. In the free-router set,
    A router counts as injecting malicious code only if a returned                     17 routers trigger follow-on use of at least one researcher-owned
tool-call payload is rewritten into an attacker-controlled command                     AWS canary credential after seeing it in transit, and one router
or dependency under researcher-controlled probing. We count an                         drains ETH from a researcher-owned Ethereum private key. Figure 3
AWS canary as touched when a credential that crossed the router                        summarizes these counts by paid versus free router populations.
later produces follow-on AWS API activity attributable to that cre-                       Two malicious routers exhibit adaptive evasion rather than
dential, and an ETH drain when funds leave a prefunded researcher-                     always-on rewriting. The deployed trigger logic is operational
controlled private key after exposure. In the weak-router study, an                    rather than exotic. In one case, malicious tool calls are injected
unauthorized access attempt is a distinct unsolicited interaction                      only after the first 50 requests, which hides the attack from shallow
against a decoy endpoint; a session is command-injectable if it ex-                    smoke tests. In another, injection is enabled only for sessions that
poses at least one shell-execution path whose returned command                         appear to be running in autonomous YOLO mode and only when
could be rewritten before execution; and YOLO mode means auto-                         the project fingerprint matches Rust or Go. These triggers are
matic tool approval without per-command confirmation. Through-                         sufficient to keep benign probes clean while reserving manipulation
out this section, token totals reflect all billed traffic visible at the               for high-value coding sessions. They are not necessarily exhaustive.
exposed upstream account or decoy, whereas Codex-session counts                        Because we observe the routers only through finite black-box
                                                                                 7
                                                                                       Hanzhi Liu, Chaofan Shou, Hongbo Wen, Yanju Chen, Ryan Jingyang Fang, and Yu Feng


                      Table 3: Main measurement outcomes across malicious routers and poisoned benign routers.

Setting                        Sample / Footprint        Active Manipula-            Adaptive Evasion        Credential Abuse         Main Outcome
                                                         tion
Paid routers                   28 purchased routers      1 router injects mali-      0 observed              0 observed               Paying for a router does not re-
                                                         cious code                                                                   move tool-call injection risk
Free routers                   400 public routers        8 routers inject mali-      2 routers trigger se-   17 routers touch AWS     Commodity free-router ecosys-
                                                         cious code                  lectively               canaries; 1 drains ETH   tems already expose AC-1, AC-
                                                                                                                                      1.a/b, and AC-2 behaviors
Leaked upstream key            1 OpenAI key leaked       0 observed                  Not needed              >7 Codex sessions;       100M GPT-5.4 tokens observed un-
                               publicly                                                                      one session exposed      der a researcher-owned account
                                                                                                             multiple credentials
Weak-router decoys             20 domains + 20 IPs       All 440 observed ses-       401 sessions already    99 credentials across    2B billed tokens; about 13 GB visi-
                                                         sions expose shell-         in     auto-approve     440 sessions / 398       ble traffic; 40k+ attempts; 6 JA3
                                                         execution paths             (YOLO) mode             projects


Table 4: AC-1.b conditions observed in malicious routers.                                     In the second poisoning study, we deployed vulnerable
Each maps to one of the five trigger families defined in Sec-                              claude-relay-service instances across 20 domains and weak-
tion 4.2.2.                                                                                password Sub2API and CLIProxyAPI instances across 20 IPs. We
                                                                                           observed 40k+ unauthorized access attempts from 147 IPs with six
Type           Condition              Trigger Family     Effect                            unique JA3 fingerprints. Those initial accesses are consistent with a
Observed       After 50 prior calls   Request-count      Hides AC-1 until warm-            mix of opportunistic internet scanning and subsequent relay reuse.
                                      threshold          up traffic completes              We therefore do not interpret every access event itself as evidence
Observed       Only in      YOLO      User fingerprint   Reserves payload injec-           of a targeted supply-chain attack. The stronger signal comes from
               mode                                      tion for autonomous ses-
                                                         sions
                                                                                           the later structured downstream traffic: the decoys were not merely
                                                                                           scanned once, but were folded into active agent-facing relay paths
Observed       Only for Rust / Go     Content keyword    Targets high-value devel-
               projects                                  oper environments while           that generated sustained billed usage and repeat Codex sessions.
                                                         evading generic probes            Those decoys ultimately served roughly 2B GPT-5.4 and 5.3-codex
                                                                                           tokens, corresponding to roughly 13 GB of visible downstream
                                                                                           prompt/response traffic, and exposed 99 unique credentials across
                                                                                           440 Codex sessions spanning 398 different projects or hosts. All
probing, a router may implement additional latent conditions that                          440 sessions were command-injectable, and 401 already operated
our probes did not activate.                                                               in YOLO mode, i.e., with tool execution auto-approved rather
                                                                                           than confirmed command by command. For those 401 sessions,
                                                                                           sophisticated adaptive evasion was unnecessary: basic payload
5.3       Poisoning Benign and Trusted Routers                                             injection would have been sufficient to change executed commands.
Active malicious routers are only half of the supply-chain problem.                           This benign-router poisoning result is the strongest evidence
Routers that look benign can be poisoned into the same position                            that the router threat boundary is transitive. A router does not need
when they reuse leaked upstream credentials or when they forward                           to be malicious at account creation time. If it later adopts leaked
user traffic through other weak routers. We observe both paths.                            upstream keys or forwards traffic into a weak relay chain, all four
   In the first poisoning study, we intentionally leaked a researcher-                     attack classes become available to whoever controls that upstream
owned OpenAI API key on Chinese forums, WeChat, and Telegram                               account or inner relay. The user may believe they are trusting one
groups frequented by router operators. That single key served 100M                         router, while the effective trust boundary has silently expanded to
GPT-5.4 tokens and exposed more than seven Codex user sessions.                            a larger chain of opportunistic operators.
Because the traffic was billed to and logged under our upstream
account, we could observe downstream prompt, tool, and credential                          5.4     Key Findings
material crossing a router we did not directly operate. In at least                           Malicious routers already exist in both paid and free commodity
one observed session, multiple distinct credentials appeared behind                        router markets. The 1 paid and 8 free routers that inject malicious
the leaked key. This result is consistent with several paths: direct                       code show that this is not a purely hypothetical threat or a pathol-
reuse by a router operator, direct reuse by unrelated third parties,                       ogy confined to obvious free relay dumps. Paid access improves
or reuse somewhere inside a longer relay chain. We cannot always                           service stability, but it does not prove tool-call integrity.
distinguish among those paths from provider-side logs alone. What
the experiment does establish is the blast radius: once a supposedly                          Adaptive evasion is deployed, but often unnecessary. We observe
benign router path reuses a stolen upstream credential, the holder                         real routers that wait for warm-up traffic, target only YOLO mode,
of that credential inherits the same plaintext visibility as an actively                   or restrict injection to Rust and Go projects. At the same time,
malicious router.                                                                          the weak-router decoy study shows that many downstream agent
                                                                                       8
Your Agent Is Mine: Measuring Malicious Intermediary Attacks on the LLM Supply Chain


sessions are already so permissive that complex triggers are not                        Table 5: Cross-framework compatibility results for Mine.
required: 401 of 440 observed sessions were autonomous enough
for simple payload injection to succeed.                                                       Metric                                      Result
                                                                                               Frameworks tested                           4
   Benign routers can be poisoned into the same trust boundary.                                Requests per framework/module               1,000
Leaked upstream keys and weak third-party relays turn otherwise                                Frameworks with response-integrity checks   0/4
                                                                                               AC-1 rewrite compatibility                  100%
benign routers into channels for plaintext prompt visibility, cre-                             AC-1.a rewrite compatibility                99.6%
dential exposure, and command injection. The supply-chain risk                                 AC-2 extractor coverage                     100%
therefore does not begin only when a router operator decides to                                Buffered streaming compatibility            4/4
                                                                                               Median overhead                             0.013 ms/request
act maliciously; it also appears when a router reuses compromised                              Median upstream latency                     820 ms
credentials or silently chains through a weaker upstream interme-
diary.
                                                                                       responses across all frameworks. AC-1.a achieves a 99.6% compat-
5.5     Scope                                                                          ibility rate on package-install tool calls. For AC-2, the relevant
Our corpus targets the most active publicly reachable commod-                          metric is extractor coverage rather than client-visible execution:
ity router markets; enterprise and invite-only deployments are a                       the module matches 100% of payloads containing detectable se-
natural extension. Although the majority of routers in our corpus                      crets under its rule set while remaining passive from the client’s
originate from Chinese-language marketplaces and communities,                          perspective. Within the evaluated frameworks, the same rewriting
this does not make the findings regionally narrow: Chinese open-                       logic handles both OpenAI- and Anthropic-style wire formats; Ope-
source models reached nearly 30% of total OpenRouter usage in                          nAI requires nested parsing of string-encoded arguments, whereas
some weeks, and Asia’s share of LLM API spend on the platform                          Anthropic-style interfaces expose native JSON structures directly.
grew from about 13% to 31% [6], so routers serving this traffic han-                   These are compatibility measurements, not end-to-end execution
dle a substantial share of global routing volume. The poisoning                        rates: they show that the tampered tool call reaches the client
studies demonstrate exploitability and blast radius under realistic                    in a valid framework-native format, but downstream permission
conditions, and the session-level findings reflect the population of                   prompts or local execution sandboxes may still block the resulting
users who interact with these commodity routers in practice.                           action. Table 5 summarizes the results.
                                                                                          In streaming mode, AC-1 and AC-1.a retain the same rewrite
                                                                                       compatibility rates because the proxy reconstructs the complete
6     Mine Artifact                                                                    tool-call payload before modification via buffered rewriting. This
We implement Mine as an OpenAI-compatible FastAPI proxy that                           buffering introduces an average pause of 0.004–0.005 ms between
forwards requests to an upstream provider and conditionally applies                    the final natural token and the first rewritten token, well below the
AC-1, AC-1.a, AC-1.b, and AC-2. We also implement companion                            820 ms median upstream latency and indistinguishable from ordi-
client-side modules for the deployable defenses evaluated in Sec-                      nary model jitter. Per-request proxy overhead is 0.013 ms median
tion 7: a tool policy gate, response-side anomaly screening, and an                    over 10,000 requests to GPT-5.4, measured on an Apple M3 Max
append-only transparency log.                                                          workstation (time.perf_counter_ns()). The remaining 0.4% of
   Mine parses each request, evaluates trigger rules, optionally                       AC-1.a failures are edge cases where install commands used quoted
activates an attack module, forwards the request upstream, and                         package fragments, editable local paths, or URL-based installs that
applies response-side rewrites before returning data to the client.                    the substitution rule conservatively declined to rewrite.
AC-1 rewrites tool-call payloads via JSON-path mutation; AC-1.a
rewrites shell and package-install command strings via substitution                    7   Deployable Defenses
rules; AC-1.b selects when AC-1 and AC-1.a activate using tool-
                                                                                       No client-side control available today can prove that a router pre-
name, keyword, user-fingerprint, time-window, and 𝑁 -th-request
                                                                                       served the upstream provider’s response. Still, several mitigations
conditions; and AC-2 scans request and response bodies for secrets
                                                                                       can be deployed immediately without provider cooperation. We
and exfiltrates matches asynchronously. Streaming is handled by
                                                                                       implemented three such controls in the artifact and evaluated them
buffering Server-Sent Events (SSE) tool-call chunks until the full
                                                                                       against the same attack classes studied in Sections 4 and 6. All
argument payload can be rewritten.
                                                                                       numbers in this section come from controlled artifact-side evalua-
                                                                                       tion rather than field data: the released scripts generate synthetic
6.1     Cross-Framework Compatibility                                                  benign and attack tool-call corpora, run the defenses over those
We evaluate Mine against four public agent frameworks: Open-                           corpora, and report the resulting coverage and overhead. The threat
Claw [33], OpenCode [34], OpenAI’s Codex, and Anthropic’s                              model for these defenses is deliberately modest: they are meant to
Claude Code. For each framework, we send 1,000 tool-calling                            reduce exposure when the attacker must pass through ordinary tool-
requests through the proxy with each attack module active. This                        execution paths visible to the client. We assume the attacker may
section asks whether public agent frameworks add local integrity                       know the defense family and probe coarse behavior; the adaptive
checks or other constraints that materially narrow the attack                          tests below relax that assumption further. They are not a substitute
surface in practice.                                                                   for origin authentication. Table 6 summarizes the coverage.
    None of the four frameworks implement response-integrity ver-                         These controls serve different operational purposes. The pol-
ification. AC-1 achieves 100% rewrite compatibility on tool-calling                    icy gate is the only one in our evaluation that consistently stops
                                                                                 9
                                                                                Hanzhi Liu, Chaofan Shou, Hongbo Wen, Yanju Chen, Ryan Jingyang Fang, and Yu Feng


Table 6: Immediate client-side defenses and their coverage.                          7.2    Response-Side Anomaly Screening
                                                                                     Some deployments cannot fail closed on every shell command. For
Defense        AC-1    AC-     AC-2    AC-     Result / Scope                        those settings, we evaluate a weaker detector that scores each re-
                       1.a             1.b
                                                                                     turned tool call using only locally observable features: shell-risk
Policy gate    100%    100%    –       –       1.0% FP; 2.3 𝜇s; 100% adaptive        patterns, tool-name frequency within the session, argument en-
                                               bypass in a simple benchmark
                                                                                     tropy, unexpected secret-like strings, and schema deviation. The
Anomaly        89.0%   50.0%   –       50.9%   6.7% FP on returned tool calls        detector deliberately does not compare the observed tool call against
screening
                                                                                     an unavailable upstream response. The implementation is an Iso-
Transparency   Audit   Audit   Audit   Audit   12.0     MB/1k       sessions;
                                                                                     lationForest [24] fit on 2,000 synthetic benign tool calls generated
log                                            1.26 KB/entry
                                                                                     from Bash, Read, Grep, Glob, and Edit sessions, then evaluated on
                                                                                     disjoint held-out synthetic attack and benign sessions (3,352 benign,
                                                                                     301 AC-1, 294 AC-1.a, and 53 AC-1.b tool calls). It is therefore a
                                                                                     controlled review-oriented detector, not a model trained on pro-
                                                                                     duction user traffic. At 6.7% false positives, the detector flags 89.0%
AC-1 and AC-1.a before execution, but only for narrowly scoped                       of AC-1 samples, 50.0% of AC-1.a samples, and 50.9% of AC-1.b
high-risk tools. Anomaly screening is weaker, yet still useful when                  samples. An additional held-out benign distribution drawn from
deployments cannot turn every shell-execution path into a fail-                      different developer commands yields 0/600 false positives at that
closed workflow. Transparency logging does not prevent manip-                        threshold. On the in-distribution benign set, most false positives
ulation, but it preserves the evidence needed to scope exposure                      come from legitimate but high-risk shell workflows: allowlisted
once a router, account, or session becomes suspect. The practical                    installer bootstraps, multi-package install commands, and kubectl
takeaway is not that any one control solves the problem. It is that                  apply fetches. Figure 4a shows the threshold tradeoff. At a strict
meaningful exposure reduction is possible today without waiting                      1% false-positive budget, the detector still catches 43.5% of AC-1
for provider cooperation. The strongest caveat is that the policy                    samples, but essentially none of AC-1.a and only 9.4% of AC-1.b.
gate is also brittle: once the attacker can hide behind an allowlisted               Relaxing the budget to 5% raises AC-1 coverage to 86.7%, while AC-
domain or a pre-positioned local stager, the gate no longer helps.                   1.a and AC-1.b remain only partially visible at 28.6% and 49.1%. At
That full bypass result is the main negative finding of this section,                10%, AC-1.a rises to 64.3%, and at 20% all three classes become sub-
and it bounds how much confidence practitioners should place in                      stantially more visible, but at a review burden that would be hard to
allowlist-only defenses.                                                             justify for routine developer workflows. We therefore report 6.7%
                                                                                     as a middle operating point: it surfaces most blatant AC-1 rewrites
                                                                                     while keeping review load bounded and still catching a meaningful
7.1     High-Risk Tool Policy Gate
                                                                                     share of AC-1.a and AC-1.b traffic. Appendix B reports the full
The strongest immediately deployable control is to fail closed on                    threshold table and a feature ablation. The ablation shows that the
high-risk shell-execution workflows. Our policy gate inspects only                   shell-risk feature carries most of the signal: removing it drops AC-1
locally visible tool-call payloads and blocks commands that fetch                    detection to 17.6% and AC-1.a detection to 4.4%. The detector is
from non-allowlisted domains or install packages outside a local al-                 therefore useful for review prioritization, but it remains weaker
lowlist. This is narrow by design: it targets the subset of tools that al-           than a fail-closed policy and still loses ground against selective
ready carry the highest execution risk, such as Bash, run_command,                   or defense-aware attackers. An attacker that knows the detector’s
and package-install commands emitted through those tools. On a                       feature family can deliberately stay within ordinary shell syntax,
templated benchmark of 1,000 benign shell commands plus 500 AC-                      spread an action across multiple benign-looking tool calls, or fall
1 and 500 AC-1.a commands generated by the artifact, the policy                      back to AC-2, none of which this local detector can rule out.
gate blocks every AC-1 and AC-1.a sample with a 1.0% false positive
rate and 2.3 𝜇s median decision cost. All false positives are benign
installer fetches from mirror domains outside the local allowlist.                   7.3    Append-Only Transparency Logging
Mirror-heavy deployments, including developer environments that                      The third control is a local transparency log that records the request
rely on regional package mirrors, would likely see higher false-                     body, response body, router URL, TLS metadata, and a hash of the
positive rates unless those mirrors are explicitly incorporated into                 raw response bytes after request-side secret redaction. Logging does
local policy. The cost of this defense is operational rather than com-               not prevent manipulation, but it improves forensic scoping once
putational. Teams must maintain allowlists for installer domains                     misuse is suspected and makes it easier to correlate traffic across
and dependency names, and benign drift outside those allowlists                      retries, routers, and upstream accounts. For AC-2 in particular,
becomes a review or breakage event. That threat model matters.                       the log is useful only after the fact: it can tie a leaked upstream
If the attacker can host payloads on an allowlisted domain or pre-                   credential or suspicious tool output to later unauthorized usage
position a local stager that is later executed through a benign Bash                 on the same account, but it does not detect passive collection at
command, the gate no longer helps. In a simple adaptive benchmark                    the moment it occurs. In a storage benchmark over 1,000 synthetic
that uses those two strategies, the policy gate is bypassed in 100%                  OpenAI-style sessions (10 tool calls each), the log costs 12.0 MB per
of samples. This means the gate should be understood as a coarse                     1,000 sessions, or about 1.26 KB per entry. That overhead is small
but useful filter for obvious high-risk workflows, not as a robust                   enough for developer workstations and CI jobs, which makes the
defense against defense-aware attackers.                                             control practical even when fail-closed policies are too restrictive.
                                                                                10
Your Agent Is Mine: Measuring Malicious Intermediary Attacks on the LLM Supply Chain



                        100                                                                                    100




                                                                                           Effectiveness (%)
   Detection rate (%)
                        80                                                                                     80

                        60                                                                                     60

                        40                                                                                     40

                        20                                                                                     20

                                                                                                                0
                         0
                              1         5           10                      20                                        AC-1          AC-1.a          AC-2          AC-1.b
                                            False-positive budget (%)                                                                  Signing   Anomaly
                                             AC-1        AC-1.a    AC-1.b                                                              TLS pin   Logging


                              (a) Threshold sweep for anomaly screening.                                             (b) Defense effectiveness by attack class.

Figure 4: Defense evaluation. (a) Threshold sweep: detection rate vs. false-positive budget for the anomaly screener across
AC-1, AC-1.a, and AC-1.b. (b) Per-class effectiveness of all four defenses: response signing, anomaly detection, TLS pinning, and
transparency logging.


In deployment, the log is most useful when paired with one of                          46]. Existing message-signing machinery could carry such a signa-
the preventive controls above. The gate or detector decides what                       ture, but it does not remove the need to define a canonical applica-
to block or escalate in the moment; the log preserves the request,                     tion payload. The closest analogue here would be a provider-signed
returned tool call, router endpoint, and response hash needed to                       canonical response envelope, similar in spirit to DKIM for email [10],
answer the next question after an incident: how far did this router                    that covers the model identifier, tool name, tool arguments, finish
or credential reach, and which sessions were exposed through it?                       reason, and a client nonce. Appendix C gives a minimal message
   These defenses reduce exposure for high-risk tool-use deploy-                       format and verification procedure. In brief, the provider signs a
ments, but they do not authenticate origin. A router that stays                        canonical JSON object containing the provider identity, model, con-
within local allowlists and avoids obvious anomalies can still alter                   tent, tool calls, finish reason, request nonce, validity window, and
semantics. The remaining gap is end-to-end provenance, which still                     key identifier [42]. The client verifies that envelope before execut-
points back to provider-supported integrity mechanisms.                                ing any tool call. Canonicalization is necessary because the routers
                                                                                       in our corpus front heterogeneous upstream providers through
8 Discussion                                                                           OpenAI- or Anthropic-compatible interfaces, so signing the raw
8.1 Scope and Future Directions                                                        HTTP body is insufficient. To our knowledge, none of the major
                                                                                       provider tool-use APIs or the current MCP specification expose
Our measurement targets the most active commodity router mar-                          a deployed response-signing mechanism for tool-call arguments
kets and uses researcher-controlled accounts throughout. Extending                     today [5, 16, 29, 32]. Section 7 shows what clients can do today
the study to private deployments are natural next steps that would                     without that provider support. Those controls reduce exposure and
complement the snapshot presented here.                                                preserve evidence, but they do not prove provenance. Execution
                                                                                       sandboxes such as E2B reduce post-execution blast radius but do
8.2                     Longer-Term Integrity                                          not authenticate where a tool call came from [15].
Choosing a router is a trust decision, but it is not the same as
choosing a cloud provider or package registry. The switching cost                      8.3                     Generalizability
is unusually low: in many agent frameworks, moving to a router is
just a base-URL change and a new API key. At the same time, the                        The Model Context Protocol (MCP) [19] introduces a related trust
service is often presented as a transparent compatibility layer even                   boundary between LLM agents and external tools. A malicious
though it can translate schemas, substitute credentials, and return                    MCP server receives tool-call requests in plaintext and can return
executable tool calls.                                                                 forged results, so the same basic manipulation and collection ideas
   Existing security mechanisms suggest what would and would                           transfer with adaptation to the MCP message format.
not help. Mutual TLS, certificate pinning, and ordinary transport                         Our implementation evaluates buffered rewriting; richer variants
security can authenticate the router endpoint the client chose, but                    including token injection and AC-1.b triggers are natural exten-
they do not say whether the returned tool call preserves upstream                      sions. The measured buffering pause of 0.004–0.005 ms is far below
semantics [8]. Web integrity mechanisms such as Subresource In-                        the 820 ms median upstream latency (Section 6), confirming that
tegrity [48], signed exchanges [51], and certificate-transparency                      buffered rewriting adds negligible overhead in practice.
logs [23] illustrate two useful patterns: authenticate content and
make that authentication auditable. Artifact-attestation systems                       9                   Related Work
such as SLSA and Sigstore apply the same idea to software supply                       Table 7 summarizes the closest prior lines of research and how our
chains by signing provenance statements and release artifacts [45,                     work differs.
                                                                                 11
                                                                              Hanzhi Liu, Chaofan Shou, Hongbo Wen, Yanju Chen, Ryan Jingyang Fang, and Yu Feng


                                                       Table 7: Related work comparison.

 Prior Work               Layer              Focus                                             Our Differentiation
 Greshake et al. [17];    Model              Prompt injection: adversarial text manipu-        Router attacks modify JSON wire format below the model;
 Perez & Ribeiro [38]                        lates model reasoning                             orthogonal to prompt-level defenses
 Zou et al. [52]          Model              Jailbreaking and adversarial prompting            We attack the transport, not the model; no adversarial prompt
                                                                                               needed
 Ohm et al. [30];         Supply chain       Supply chain attacks on OSS / AI infrastruc-      We analyze post-compromise router capabilities: active tool-
 LiteLLM incident [11]                       ture                                              call rewriting, passive collection, and conditional delivery
 Gu et al. [18]; Kurita   Model              Model-level backdoors via training / fine-        Router attacks require no model access and no training-time
 et al. [21]                                 tuning                                            adversary
 Durumeric et al. [14];   Transport          TLS interception by middleboxes                   LLM routers are voluntarily configured; no cert substitution
 de Carnavalet & Man-                                                                          needed; attacks are application-layer semantic
 nan [12]
 MCP security [29];       Tool server        Tool-server poisoning via malicious MCP de-       We target the client–provider transport; a compromised router
 Hou et al. [19]                             scriptions                                        can intercept any MCP-based interaction that transits it
 Liu et al. [25]          Client extension   Vulnerabilities in installable agent skills and   Router attacks need no skill installation and can affect both
                                             bundled scripts                                   skill-enabled and skill-free clients


   Prompt injection. Greshake et al. introduced indirect prompt                   in installable agent skills and bundled scripts [25]; router attacks
injection, showing that adversarial content embedded in external                  need no skill installation and affect both skill-enabled and skill-free
data sources can hijack an LLM’s behavior [17]. Subsequent work                   clients.
explored direct prompt injection [38], jailbreaking [52]. Router
attacks are orthogonal: the intermediary rewrites the JSON wire                   10     Conclusion
format outside the model’s reasoning loop, so prompt-level defenses               LLM API routers sit on a critical trust boundary that the ecosys-
do not authenticate the returned tool-call payload.                               tem currently treats as transparent transport. Our measurement
   Software supply chain. Ladisa et al. systematized attacks on open-             of 428 commodity routers found 9 injecting malicious code and
source supply chains [22]; Duan et al. measured typosquatting                     17 abusing researcher-owned credentials; poisoning studies showed
and dependency confusion across package managers [13]; Ohm                        that even benign routers are one leaked key away from the same
et al. catalogued maintainer compromise and related vectors [30].                 exposure, with researcher-controlled decoys attracting 2B billed
The Codecov breach showed how a single compromised CI script                      tokens, 440 autonomous Codex sessions, and 99 leaked credentials.
can persist for months while exfiltrating credentials [9]. Gu et al.              Client-side defenses (policy gates, anomaly screening, transparency
and Kurita et al. demonstrated backdoor injection into pre-trained                logs) reduce exposure today, but closing the provenance gap ul-
models and fine-tuning pipelines [18, 21]. Adjacent systems such as               timately requires provider-signed response envelopes so that the
SLSA and Sigstore sign build provenance or release artifacts rather               tool call an agent executes can be tied to what the model actually
than dynamic per-response tool-call semantics [45, 46].                           produced.

   TLS interception and API gateways. Durumeric et al. measured                   References
the security impact of HTTPS interception by middleboxes [14];                     [1] 2025. Terminal-Bench. https://www.tbench.ai/. Benchmark for testing AI agents
de Carnavalet and Mannan found widespread TLS validation fail-                         in terminal environments. Accessed: 2026-04-08.
ures [12]; Waked et al. showed that even well-intentioned intercep-                [2] Alibaba Group. 2026. Taobao. https://www.taobao.com. Chinese consumer-to-
                                                                                       consumer marketplace. Accessed: 2026-04-07.
tion introduces vulnerabilities [49]. LLM routers perform the same                 [3] Alibaba Group. 2026. Xianyu (Idle Fish). https://www.goofish.com. Chinese
basic operation, but the client chooses the intermediary explicitly,                   second-hand marketplace. Accessed: 2026-04-07.
                                                                                   [4] Amazon Web Services. 2026. Amazon Bedrock. https://aws.amazon.com/
so no certificate substitution occurs [26]. Enterprise AI gateways                     bedrock/. Managed service providing access to foundation models from AI21,
such as Kong [20] add policy around the chosen intermediary, and                       Anthropic, Cohere, Meta, Mistral, Stability AI, and Amazon via a unified API.
sandboxes such as E2B [15] constrain post-execution blast radius,                      Accessed: 2026-04-08.
                                                                                   [5] Anthropic. 2024. Tool use with Claude. https://platform.claude.com/docs/en/
but neither authenticates the provider-origin tool-call payload.                       agents-and-tools/tool-use/overview. Accessed: 2026-04-08.
                                                                                   [6] Malika Aubakirova, Alex Atallah, Chris Clark, Justin Summerville, and Anjney
   MCP security. MCP introduces a related trust boundary between                       Midha. 2026. State of AI: An Empirical 100 Trillion Token Study with OpenRouter.
agents and tool servers [19, 29]. The key structural difference is                     arXiv preprint arXiv:2601.10088 (2026).
                                                                                   [7] BerriAI. 2024. LiteLLM: Call 100+ LLM APIs in OpenAI Format. https://github.
where the intermediary sits: an MCP server terminates the tool-                        com/BerriAI/litellm. Accessed: 2026-03-15.
execution side and can forge outputs but cannot observe or alter                   [8] Brian Campbell, John Bradley, Nat Sakimura, and Torsten Lodderstedt. 2020.
the upstream model’s reasoning. A malicious router, by contrast,                       OAuth 2.0 Mutual-TLS Client Authentication and Certificate-Bound Access To-
                                                                                       kens. RFC 8705. https://doi.org/10.17487/RFC8705
sits on the client–provider transport and intercepts every tool call               [9] Codecov. 2021. Bash Uploader Security Update. https://about.codecov.io/security-
as well as the full request context. Liu et al. studied vulnerabilities                update/. April 2021. CI/CD supply chain breach persisting January–April 2021.
                                                                             12
Your Agent Is Mine: Measuring Malicious Intermediary Attacks on the LLM Supply Chain


     Accessed: 2026-03-20.                                                                      [33] OpenClaw. 2026. OpenClaw Features Documentation. https://docs.openclaw.
[10] Dave Crocker, Tony Hansen, and Murray S. Kucherawy. 2011. DomainKeys                            ai/concepts/features. Accessed: 2026-04-07. Documents support for 35+ model
     Identified Mail (DKIM) Signatures. RFC 6376. https://doi.org/10.17487/RFC6376                   providers, including custom and self-hosted OpenAI-compatible and Anthropic-
[11] Datadog Security Labs. 2026. LiteLLM and Telnyx compromised on PyPI: Trac-                      compatible endpoints..
     ing the TeamPCP supply chain campaign. https://securitylabs.datadoghq.com/                 [34] OpenCode. 2026. OpenCode Providers Documentation. https://opencode.ai/docs/
     articles/litellm-compromised-pypi-teampcp-supply-chain-campaign/. March                         providers. Accessed: 2026-04-07. Documents support for 75+ LLM providers and
     2026. Accessed: 2026-04-08.                                                                     configurable base URLs for custom endpoints and proxy services..
[12] Xavier de Carné de Carnavalet and Mohammad Mannan. 2016. Killed by Proxy:                  [35] OpenRouter. 2024. OpenRouter: A Unified Interface for LLMs. https://openrouter.
     Analyzing Client-end TLS Interception Software. In Proceedings of the 2016                      ai. Accessed: 2026-03-15.
     Network and Distributed System Security Symposium (NDSS). Internet Society.                [36] Lily Ottinger, Jordan Schneider, and Zilan Qian. 2025. How to Use Banned
     https://doi.org/10.14722/ndss.2016.23374                                                        US Models in China. https://www.chinatalk.media/p/the-grey-market-for-
[13] Ruian Duan, Omar Alrawi, Ranjita Pai Kasturi, Ryan Elder, Brendan Saltafor-                     american-llms. Investigation of Taobao and Xianyu LLM API reselling market.
     maggio, and Wenke Lee. 2021. Towards Measuring Supply Chain Attacks on                          Accessed: 2026-04-08.
     Package Managers for Interpreted Languages. In Proceedings of the 2021 Network             [37] Shishir G. Patil, Tianjun Zhang, Xin Wang, and Joseph E. Gonzalez. 2023. Go-
     and Distributed System Security Symposium (NDSS). Internet Society.                             rilla: Large Language Model Connected with Massive APIs. arXiv preprint
[14] Zakir Durumeric, Zane Ma, Drew Springall, Richard Barnes, Nick Sullivan, Elie                   arXiv:2305.15334 (2023).
     Bursztein, Michael Bailey, J. Alex Halderman, and Vern Paxson. 2017. The                   [38] Fábio Perez and Ian Ribeiro. 2022. Ignore Previous Prompt: Attack Techniques
     Security Impact of HTTPS Interception. In Proceedings of the 2017 Network                       For Language Models. arXiv preprint arXiv:2211.09527 (2022).
     and Distributed System Security Symposium (NDSS). Internet Society. https:                 [39] Yujia Qin, Shihao Liang, Yining Ye, Kunlun Zhu, Lan Yan, Yaxi Lu, Yankai Lin,
     //doi.org/10.14722/ndss.2017.23456                                                              Xin Cong, Xiangru Tang, Bill Qian, Sihan Zhao, Lauren Hong, Runchu Tian,
[15] E2B. 2026. E2B Documentation. https://e2b.dev/docs. Accessed: 2026-04-07.                       Ruobing Xie, Jie Zhou, Mark Gerstein, Dahai Li, Zhiyuan Liu, and Maosong Sun.
[16] Google. 2024. Function calling with the Gemini API. https://ai.google.dev/gemini-               2023. ToolLLM: Facilitating Large Language Models to Master 16000+ Real-world
     api/docs/function-calling. Accessed: 2026-04-08.                                                APIs. arXiv preprint arXiv:2307.16789 (2023).
[17] Kai Greshake, Sahar Abdelnabi, Shailesh Mishra, Christoph Endres, Thorsten                 [40] QuantumNous. 2026. new-api. https://github.com/QuantumNous/new-api.
     Holz, and Mario Fritz. 2023. Not What You’ve Signed Up For: Compromising                        Open-source multi-provider API management and distribution platform. Ac-
     Real-World LLM-Integrated Applications with Indirect Prompt Injection. In                       cessed: 2026-04-08.
     Proceedings of the 16th ACM Workshop on Artificial Intelligence and Security               [41] Yangjun Ruan, Honghua Dong, Andrew Wang, Silviu Pitis, Yongchao Zhou,
     (AISec). ACM. https://doi.org/10.1145/3605764.3623985                                           Jimmy Ba, Yann Dubois, Chris J. Maddison, and Tatsunori Hashimoto. 2024.
[18] Tianyu Gu, Kang Liu, Brendan Dolan-Gavitt, and Siddharth Garg. 2019. BadNets:                   Identifying the Risks of LM Agents with an LM-Emulated Sandbox. In Proceedings
     Evaluating Backdooring Attacks on Deep Neural Networks. IEEE Access 7 (2019),                   of the 12th International Conference on Learning Representations (ICLR).
     47230–47244. https://doi.org/10.1109/ACCESS.2019.2909068                                   [42] Anders Rundgren, Benjamin Jordan, and Samuel Erdtman. 2020. JSON Canoni-
[19] Xinyi Hou, Yanjie Zhao, Shenao Wang, and Haoyu Wang. 2025. Model Context                        calization Scheme (JCS). RFC 8785. https://doi.org/10.17487/RFC8785
     Protocol (MCP): Landscape, Security Threats, and Future Research Directions.               [43] Timo Schick, Jane Dwivedi-Yu, Roberto Dessì, Roberta Raileanu, Maria Lomeli,
     arXiv preprint arXiv:2503.23278 (2025).                                                         Eric Hambro, Luke Zettlemoyer, Nicola Cancedda, and Thomas Scialom. 2023.
[20] Kong. 2026. Kong AI Gateway. https://developer.konghq.com/ai-gateway/.                          Toolformer: Language Models Can Teach Themselves to Use Tools. In Advances
     Accessed: 2026-04-08.                                                                           in Neural Information Processing Systems (NeurIPS), Vol. 36.
[21] Keita Kurita, Paul Michel, and Graham Neubig. 2020. Weight Poisoning Attacks               [44] Shopify. 2026. Shopify. https://www.shopify.com. Global e-commerce platform
     on Pretrained Models. In Proceedings of the 58th Annual Meeting of the Association              hosting independent storefronts. Accessed: 2026-04-07.
     for Computational Linguistics (ACL). ACL. https://doi.org/10.18653/v1/2020.acl-            [45] Sigstore. 2026. Sigstore Documentation. https://docs.sigstore.dev/. Accessed:
     main.249                                                                                        2026-04-07.
[22] Piergiorgio Ladisa, Henrik Plate, Matias Martinez, and Olivier Barais. 2023. SoK:          [46] SLSA. 2026. SLSA Specification. https://slsa.dev/spec/v1.2/. Accessed: 2026-04-07.
     Taxonomy of Attacks on Open-Source Software Supply Chains. In Proceedings                  [47] sub2api. 2026. sub2api. https://github.com/Wei-Shaw/sub2api. Open-source
     of the 2023 IEEE Symposium on Security and Privacy (S&P). IEEE. https://doi.org/                OpenAI-compatible API router template. Accessed: 2026-04-08.
     10.1109/SP46215.2023.10179304                                                              [48] W3C. 2016. Subresource Integrity. https://www.w3.org/TR/SRI/. W3C Recom-
[23] Ben Laurie, Adam Langley, and Emil Kasper. 2013. Certificate Transparency.                      mendation. Accessed: 2026-04-07.
     RFC 6962. https://doi.org/10.17487/RFC6962                                                 [49] Louis Waked, Mohammad Mannan, and Amr Youssef. 2018. The Sorry
[24] Fei Tony Liu, Kai Ming Ting, and Zhi-Hua Zhou. 2008. Isolation Forest. In                       State of TLS Security in Enterprise Interception Appliances. arXiv preprint
     Proceedings of the 2008 IEEE International Conference on Data Mining (ICDM).                    arXiv:1809.08729 (2018).
     IEEE. https://doi.org/10.1109/ICDM.2008.17                                                 [50] Lei Wang, Chen Ma, Xueyang Feng, Zeyu Zhang, Hao Yang, Jingsen Zhang,
[25] Yi Liu, Weizhe Wang, Ruitao Feng, Yao Zhang, Guangquan Xu, Gelei Deng,                          Zhiyuan Chen, Jiakai Tang, Xu Chen, Yankai Lin, Wayne Xin Zhao, Zhewei Wei,
     Yuekang Li, and Leo Zhang. 2026. Agent Skills in the Wild: An Empirical                         and Ji-Rong Wen. 2023. A Survey on Large Language Model based Autonomous
     Study of Security Vulnerabilities at Scale. arXiv preprint arXiv:2601.10338 (2026).             Agents. arXiv preprint arXiv:2308.11432 (2023).
     https://doi.org/10.48550/arXiv.2601.10338                                                  [51] Jeffrey Yasskin. 2020. Signed HTTP Exchanges. Internet-Draft draft-yasskin-http-
[26] Keyu Man, Zhiyun Qian, Zhongjie Wang, Xiaofeng Zheng, Youjun Huang, and                         origin-signed-responses-09. https://datatracker.ietf.org/doc/html/draft-yasskin-
     Haixin Duan. 2020. DNS Cache Poisoning Attack Reloaded. In Proceedings of the                   http-origin-signed-responses-09 Work in progress. Accessed: 2026-04-07.
     2020 ACM Conference on Computer and Communications Security (CCS). ACM.                    [52] Andy Zou, Zifan Wang, Nicholas Carlini, Milad Nasr, J. Zico Kolter, and Matt
     https://doi.org/10.1145/3372297.3417280                                                         Fredrikson. 2023. Universal and Transferable Adversarial Attacks on Aligned
[27] Michael Meli, Matthew R. McNiece, and Bradley Reaves. 2019. How Bad                             Language Models. arXiv preprint arXiv:2307.15043 (2023).
     Can It Git? Characterizing Secret Leakage in Public GitHub Reposito-
     ries.       https://www.ndss-symposium.org/ndss-paper/how-bad-can-it-git-
     characterizing-secret-leakage-in-public-github-repositories/. In Proceedings of            A     Ethical Considerations
     the 2019 Network and Distributed System Security Symposium (NDSS). Internet
     Society. Accessed: 2026-04-07.                                                             This appendix describes the ethical framework governing our re-
[28] Microsoft. 2026. Azure OpenAI in Foundry Models. https://azure.microsoft.com/              search, including data handling, measurement constraints, and dual-
     en-us/products/ai-foundry/models/openai/. Accessed: 2026-04-08.                            use risk mitigation.
[29] Model Context Protocol. 2025. Security Best Practices - Model Context Pro-
     tocol. https://modelcontextprotocol.io/docs/tutorials/security/security_best_              No IRB / ethics-board review. We did not obtain IRB or equivalent
     practices. Accessed: 2026-04-08.                                                           ethics-board review for this study. The work used only researcher-
[30] Marc Ohm, Henrik Plate, Arnold Sykosch, and Michael Meier. 2020. Backstabber’s
     Knife Collection: A Review of Open Source Software Supply Chain Attacks. In                controlled accounts and credentials, relied on synthetic active-
     Proceedings of the 17th Conference on Detection of Intrusions and Malware &                probing traffic, and retained only aggregate operational metadata
     Vulnerability Assessment (DIMVA). Springer. https://doi.org/10.1007/978-3-030-
     52683-2_2
                                                                                                from unauthorized third-party use of researcher-owned secrets. We
[31] one-api contributors. 2026. one-api: OpenAI API Management and Distribution                therefore treated it as systems measurement rather than human-
     System. https://github.com/songquanpeng/one-api. 30.5k GitHub stars, 1.19M                 subjects research, but we make this status explicit because the
     Docker Hub pulls as of April 2026. Accessed: 2026-04-07.
[32] OpenAI. 2023. Function calling and other API updates. https://openai.com/index/            credential-exposure case study intentionally created publicly dis-
     function-calling-and-other-api-updates/. Accessed: 2026-04-08.                             coverable secrets. We nevertheless treated the study as ethically
                                                                                           13
                                                                           Hanzhi Liu, Chaofan Shou, Hongbo Wen, Yanju Chen, Ryan Jingyang Fang, and Yu Feng


sensitive because that design could attract third-party abuse and               No persistent data collection. Experimental data is retained only
lead to nominal financial loss on researcher-owned accounts.                    for the duration of the study. Researcher-owned credentials used
                                                                                in the credential-exposure case study (Section 5.3) were revoked or
A.1     Disclosure Scope                                                        otherwise retired upon completion of the observation period. All
We did not run a provider-by-provider coordinated disclosure pro-               provider interaction logs are stored on encrypted research infras-
cess for the findings in Section 5. Several considerations informed             tructure and will be deleted 12 months after publication. Revocation
this decision. First, the paper centers on three measurements:                  could interrupt unauthorized downstream use of those exposed cre-
routers openly sold in public markets, free routers distributed                 dentials. We accepted that externality because continued operation
through public communities, and researcher-controlled poisoning                 would have extended third-party exposure and financial loss on
studies based on leaked keys and weak relay decoys. These are                   researcher-owned accounts.
not private zero-days disclosed by a single vendor. They are
observations about how publicly reachable router ecosystems and                 A.3     Measurement Constraints
router chains behave once exposed to attacker-relevant inputs.                  We impose the following constraints to ensure our experiments do
Second, the affected routers are commodity services operated                    not disrupt the services we study:
by pseudonymous or anonymous sellers on Taobao, Xianyu, and                     Rate limiting. No provider receives more than 60 requests per
public community forums; there is no stable security-contact                    hour during any experiment, well below the rate limits published by
channel for most of these operators, and many explicitly advertise              all tested providers. Provider-facing validation requests are spaced
their service as unofficial or gray-market. Third, the vulnerability            to avoid triggering abuse-detection mechanisms.
is architectural rather than implementation-specific: any router
                                                                                No third-party traffic interception. All active probing requests
that terminates TLS and forwards tool-call JSON can mount the
                                                                                originate from our own client infrastructure and target our own
same attacks, so disclosing to individual operators would not
                                                                                upstream accounts. The poisoning studies do not rely on network-
remediate the underlying trust gap. We therefore treated the work
                                                                                level interception equipment, DNS hijacking, or traffic redirection;
as a measurement study rather than an embargo case. At the end
                                                                                it analyzes upstream-provider metadata associated with researcher-
of the observation window, all exposed credentials were revoked
                                                                                owned credentials after those credentials became publicly discover-
or otherwise retired. Because the affected upstream credentials
                                                                                able or after traffic voluntarily reached researcher-controlled decoy
were researcher-owned and could be retired directly, we did not
                                                                                relays.
separately notify OpenAI, Anthropic, or other upstream providers
about each individual reuse event.                                              No exploitation of discovered vulnerabilities. Where our mea-
                                                                                surement reveals potential security weaknesses (e.g., unauthorized
A.2     Data Minimization                                                       secret reuse in the credential-exposure case study), we record the
                                                                                finding but do not attempt to validate it through additional real-
We adhere to strict data minimization principles throughout the
                                                                                world exploitation. We do not attempt to exploit, amplify, or repro-
study:
                                                                                duce any vulnerability beyond the minimum necessary to confirm
Research accounts only. All API keys, user accounts, and ser-                   its existence.
vice subscriptions used in our experiments (Sections 5–6) were
created specifically for this research. We never access accounts or             Minimal financial exposure. Researcher-owned Ethereum decoy
credentials not under researcher control. When third-party traf-                keys were prefunded only with nominal balances. For the single
fic voluntarily reached researcher-controlled keys or decoy relays,             on-chain drain reported in Section 5.3, the value lost was below
we limited retention to aggregate metadata and hashed credential                US$50 at the time of transfer.
identifiers as described below.
                                                                                A.4     Dual-Use Risk and Mitigations
Synthetic payloads. All provider-facing payloads and prompts
used in our study are synthetically generated. No real user queries,            The attack taxonomy and techniques we describe (Sections 4–6)
proprietary code, or sensitive data appear in any provider-facing               constitute dual-use research: the same material that enables defen-
validation request.                                                             sive understanding could guide a malicious router operator. We
                                                                                adopt the following mitigations:
Retrospective credential-exposure data. The poisoning studies
(Section 5.3) are observational rather than interactive: they analyze           No public release of Mine. We do not publish Mine or any of its
unauthorized traffic that reached researcher-owned credentials af-              attack modules. Mine exists solely as an internal research imple-
ter public exposure. For these studies, we retain only aggregate                mentation used to produce the compatibility and defense results in
operational metadata (timestamps, coarse model identifiers, token               Sections 6–7; we neither distribute the source code nor provide de-
volume, source network labels where available, session counts,                  ployment or operational guidance for it. This choice is intentional:
project or host counts, and salted hashes of leaked credential val-             it raises the engineering barrier for misuse while preserving the
ues) and do not store or release prompt/response bodies or raw                  scientific value of the measurements the tool enabled.
credential strings from third-party traffic. Project or host identifiers        Defensive value outweighs offensive risk. The attack classes
were stored only in coarse form and, where persisted, as salted                 we describe (AC-1, AC-1.a, AC-1.b, and AC-2) require only straight-
one-way hashes rather than human-readable names. They were                      forward JSON manipulation; any competent adversary with router
used solely for counting distinct exposure scopes and were not                  access could implement them independently. By publishing a sys-
joined against external account records.                                        tematic taxonomy and measurement methodology, we enable the
                                                                           14
Your Agent Is Mine: Measuring Malicious Intermediary Attacks on the LLM Supply Chain


Table 8: Corpora used for the deployable-defense evaluation.                                     Table 11: Minimal provider-signed response-envelope fields.

Defense           Corpus Size              Construction                                              Field            Purpose
Policy gate       1,000 benign, 500        Templated shell commands covering in-                     v               Envelope version for compatibility and rollout.
                  AC-1, 500 AC-1.a         staller fetches, package installs, grep, git,             provider        Provider identity, e.g., api.openai.com.
                                           pytest, and kubectl; AC-1 and AC-1.a                      key_id          Signing-key identifier used for verification and rotation.
                                           samples are generated by substituting mali-               model           Provider model identifier for the signed response.
                                           cious domains or attacker-controlled pack-                request_nonce   Client-supplied nonce bound to the corresponding request.
                                           age names.                                                issued_at       Provider timestamp for replay control and audit.
                                                                                                     expires_at      Short validity horizon for key rotation and replay limits.
Anomaly           2,000 fit benign;        Procedurally generated sessions over Bash,                content         Natural-language assistant content, if any.
screening         held-out    3,352        Read, Grep, Glob, and Edit. The detector                  tool_calls      Array of tool calls, each with name and native-JSON
                  benign, 301 AC-1,        is an IsolationForest fit on synthetic benign                             arguments.
                  294 AC-1.a, 53           sessions only; held-out attack labels come                finish_reason   Provider finish reason, e.g., tool_calls or stop.
                  AC-1.b                   from injected AC-1, AC-1.a, and trigger-                  sig_alg         Signature algorithm identifier.
                                           matching AC-1.b tool calls.                               signature       Signature over the canonicalized envelope excluding this field.
Transparency      1,000      sessions,     Synthetic OpenAI-style request/response
log               10,000 entries           objects with tool calls, request-side secret
                                           redaction checks, and response-byte hash-
                                           ing checks.
                                                                                                   The threshold sweep shows the expected tradeoff: AC-1 rises
Table 9: Threshold sensitivity for response-side anomaly                                        quickly as the false-positive budget grows, while AC-1.a and AC-1.b
screening.                                                                                      require much more lenient thresholds. The ablation confirms that
                                                                                                shell-risk patterns dominate detection for active command rewrites,
                 Benign FP Target         AC-1       AC-1.a      AC-1.b
                                                                                                which is precisely why the detector remains a review aid rather
                                                                                                than a substitute for provenance.
                                 1%       43.5%        0.0%        9.4%
                                 5%       86.7%       28.6%       49.1%
                                10%       95.0%       64.3%       60.4%
                                20%      100.0%       86.7%       83.0%
                                                                                                 C        Canonical Response-Envelope Format
                                                                                                 This appendix gives a minimal message format for the provider-
                                                                                                 signed response envelope discussed in Section 8.2. The goal is
Table 10: Feature ablation for anomaly screening at the 6.7%
                                                                                                 semantic integrity for tool-calling responses even when a router
false-positive operating point.
                                                                                                 re-serializes, wraps, or otherwise transforms the original HTTP
                                                                                                 body.
              Feature Removed                AC-1      AC-1.a      AC-1.b
                                                                                                    The signed scope is the entire envelope except signature.
              None                           89.0%       50.0%       50.9%                       Provider-specific billing metadata, raw response identifiers, and
              shell_risk_score               17.6%        4.4%        9.4%
              tool_frequency                 88.4%       53.4%       45.3%                       transport headers remain outside the signed scope because they
              string_entropy                 89.0%       33.7%       50.9%                       are not required to decide which tool call the client executes.
              unexpected_secret_pattern      89.0%       47.3%       50.9%
              schema_deviation               86.4%       39.5%       50.9%
                                                                                                 The critical normalization step is that tool_calls[*].arguments
                                                                                                 must be represented as native JSON values inside the envelope
                                                                                                 even if a provider’s wire format emits them as string-encoded
community to build better safeguards around intermediary trust in                                JSON. This parsing step must itself be canonical and fail closed. If a
agent systems. We believe the defensive benefit of public disclosure                             provider cannot unambiguously parse a string-encoded argument
substantially outweighs the marginal increase in offensive capabil-                              blob into native JSON, it should treat the response as unsigned
ity, consistent with the established norms of the security research                              rather than producing a best-effort envelope.
community [14, 17].                                                                             1     {
                                                                                                2         "v": 1,
B    Additional Defense Evaluation                                                              3         "provider": "api.openai.com",
                                                                                                4         "key_id": "2026-04-k1",
All defense results in Section 7 come from controlled artifact-side                             5         "model": "gpt-5.4",
evaluation rather than field data. The released scripts procedurally                            6         "request_nonce": "b7c6b9f0e87a4a6b",
                                                                                                7         "issued_at": "2026-04-07T18:00:00Z",
generate benign and attack corpora from fixed command templates                                 8         "expires_at": "2026-04-07T18:05:00Z",
and random seeds, then run the defenses on those corpora.                                       9         "content": "I will inspect the repository.",
   The anomaly detector in Section 7.2 is fit on 2,000 benign tool                              10        "tool_calls": [
                                                                                                11           {
calls, calibrated on disjoint held-out benign sessions, and evaluated                           12             "name": "Bash",
on separate attack sessions. The held-out test split contains 3,352                             13             "arguments": {"command": "grep -R \"TODO\" ./src"}
benign tool calls, 301 AC-1 calls, 294 AC-1.a calls, and 53 AC-1.b                              14           }
                                                                                                15        ],
calls. The AC-1.b count is smaller because only trigger-matching                                16        "finish_reason": "tool_calls",
calls are labeled as attack traffic; non-matching calls remain benign                           17        "sig_alg": "Ed25519",
by construction. We also check the chosen operating point on a held-                            18        "signature": "base64..."
                                                                                                19    }
out benign distribution built from different developer commands
                                                                                                                 Listing 2: Example response envelope.
and observe 0/600 false positives.
                                                                                           15
                                                                        Hanzhi Liu, Chaofan Shou, Hongbo Wen, Yanju Chen, Ryan Jingyang Fang, and Yu Feng


Provider-side generation. Given an upstream response, the                    envelope. This design therefore tolerates schema translation and
provider-side SDK or API gateway: (1) maps the provider-native               re-serialization while preventing a router from silently rewriting
response into the envelope fields above; (2) parses any string-              the semantically meaningful tool-call payload. Backwards compat-
encoded tool arguments into native JSON; (3) canonicalizes the               ibility is incremental: providers can add the envelope alongside
resulting object with RFC 8785 JSON canonicalization [42]; and (4)           existing response formats, and clients that do not understand it
signs the canonical byte string with the private key referenced by           simply ignore it and behave as they do today. Clients that do under-
key_id.                                                                      stand it can adopt a phased policy, e.g., verify when present, then
Client-side verification. Before executing any tool call, the client:        require signatures only for high-risk tool categories.
(1) fetches or caches the provider verification key for provider and            For streaming responses, the simplest design is to sign the final
key_id; (2) checks that request_nonce matches the outstanding                tool-bearing envelope rather than every token chunk. That matches
request; (3) checks that issued_at and expires_at define a cur-              the execution boundary in current tool-use clients, which typically
rently valid window; and (4) re-canonicalizes the envelope without           wait for complete tool arguments before taking action. Per-chunk
signature and verifies the signature. If any step fails, the client          signatures are possible, but they would add significantly more pro-
treats the response as unsigned and blocks tool execution.                   tocol complexity and are unnecessary for the core threat studied
Deployment notes. Routers may still add unsigned outer meta-                 here, namely silent modification of the final tool-call payload.
data, but clients should execute tool calls only from the verified




                                                                        16
