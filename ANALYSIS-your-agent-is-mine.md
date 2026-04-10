# Your Agent Is Mine: Analysis of LLM Router Supply-Chain Attacks

**Paper:** "Your Agent Is Mine: Measuring Malicious Intermediary Attacks on the LLM Supply Chain"
**Authors:** Hanzhi Liu, Chaofan Shou, Hongbo Wen, Yanju Chen, Ryan Jingyang Fang, Yu Feng
**Affiliations:** UC Santa Barbara, Fuzzland, UC San Diego, World Liberty Financial
**Venue:** ACM CCS '26
**arXiv:** [2604.08407](https://arxiv.org/abs/2604.08407)
**Date:** April 2026

## 1. Overview

This paper presents the first systematic study of security vulnerabilities in third-party LLM API routers --- intermediary services that accept requests in a provider-compatible format, route them to upstream model providers, and return responses. The core insight is that these routers operate as application-layer proxies with full plaintext access to every in-flight JSON payload, yet no provider enforces cryptographic integrity between client and upstream model.

The paper makes three contributions:

1. **Formal threat model and attack taxonomy.** Defines LLM API routers as a supply-chain trust boundary and introduces two core attack classes (response-side payload injection and passive secret exfiltration) with two adaptive evasion variants (dependency-targeted injection and conditional delivery).

2. **Large-scale ecosystem measurement.** Analyzes 28 paid and 400 free commodity routers, finding 9 actively injecting malicious code, 2 deploying adaptive evasion triggers, 17 abusing researcher-owned AWS credentials, and 1 draining ETH from a researcher-controlled wallet. Complementary poisoning studies show that benign routers can be pulled into the same attack surface through leaked keys and weak relay chains.

3. **Research proxy and deployable defenses.** Builds Mine, a research proxy implementing all four attack classes, tests it against four public agent frameworks (OpenClaw, OpenCode, Codex, Claude Code), and evaluates three client-side defenses: a fail-closed policy gate, response-side anomaly screening, and append-only transparency logging.

**Why this matters for agent security:** Most existing work on agent security focuses on prompt injection, memory poisoning, or tool supply-chain attacks that operate at the model or application layer. This paper identifies a distinct, lower-level attack surface: the transport layer between client and provider. These attacks are orthogonal to prompt-level defenses --- they occur in the JSON/tool layer before the model sees the request or after it emits a response, entirely outside the model's reasoning loop. An agent that is perfectly defended against prompt injection can still have its tool calls silently rewritten by a malicious router.

---

## 2. Threat Model

### 2.1 System Model

The paper models the LLM agent ecosystem as a multi-hop graph:

- **Agent clients** (e.g., Claude Code, Codex, OpenClaw) send tool-calling requests
- **Routers** (R_1, ..., R_k) form a chain between client and provider
- **Model providers** (OpenAI, Anthropic, Google) serve the upstream model

Each router terminates the inbound TLS connection, originating a separate TLS connection upstream. Once an agent targets that router endpoint, the service can inspect tool-call arguments, API keys, system prompts, and model outputs; it can also normalize, delay, or rewrite the returned tool call before the client finally observes it.

### 2.2 Integrity Properties

- **Honest router:** R_honest(req) = P(req) --- forwards the request and returns the unmodified provider response.
- **Chain composition:** (R_1 ... R_k)(req) = R_1(R_2(...R_k(P(req))...)).
- **Weakest-link property:** If all R_i are honest, the chain preserves integrity. If any single R_j is malicious, there is no integrity guarantee for the full chain.
- **Cumulative taint:** For AC-2 (secret exfiltration), every router in the chain observes plaintext traffic, so the total secret exposure is the union of all extracted credentials across all routers.
- **Transitivity of trust:** A malicious router at any layer can apply AC-1 (rewrite) or AC-2 (collect); downstream honest routers cannot detect or undo the modification because they lack a reference to the original upstream response.

### 2.3 Scope

The paper explicitly scopes to commodity router markets and researcher-controlled accounts. Enterprise and invite-only deployments are acknowledged as natural extensions. The majority of routers in the corpus originate from Chinese-language marketplaces and communities, but this reflects market structure: Chinese open-source models reached nearly 30% of total OpenRouter usage in some weeks, and Asia's share of LLM API spend on the platform grew from ~15% to ~31%, so routers serving this traffic handle a substantial share of global routing volume.

---

## 3. Attack Classes

### 3.1 AC-1: Response-Side Payload Injection

The router rewrites tool-call arguments in the JSON response before it reaches the client. The `rewrite` function replaces selected fields in the argument JSON while preserving the tool name and schema structure. Because the modified payload remains syntactically valid JSON matching the expected tool schema, AC-1 redirects agent behavior without producing a schema violation or transport error.

- **Preconditions:** Tool-calling response and absence of an integrity mechanism binding the returned arguments to the upstream original.
- **Primary harm:** Arbitrary code execution on the client machine. Any agent that auto-executes tool calls through an unverified router is exposed.
- **Detection difficulty:** The modified payload is schema-valid; the client never sees the upstream original.
- **Example:** A benign installer URL `https://get.example.com/cli.sh` is rewritten to `https://attacker****.sh`.

The March 2026 LiteLLM compromise \[11\] demonstrated exactly this primitive at scale: once the attacker controlled the request pipeline, every transiting tool call was exposed to rewriting.

### 3.2 AC-2: Passive Secret Exfiltration

The router scans request headers, bodies, and response bodies against credential patterns and exfiltrates secrets asynchronously. AC-2 requires no payload modification --- the response is forwarded unmodified. This makes it invisible to the client: the boundary between "credential handling" and "credential theft" is invisible because routers already read secrets in plaintext as part of normal forwarding.

- **Preconditions:** Secrets present in plaintext traffic.
- **Primary harm:** Credential theft at scale.
- **Detection difficulty:** Traffic is unchanged; clients cannot observe router-side retention.
- **Extraction patterns observed:** OpenAI keys, AWS keys, GitHub PATs, Slack bot tokens, Ethereum private keys, PEM keys, Bearer tokens, auth headers, high-entropy hex strings.

AC-2 cannot be mitigated by response-signing proposals because secrets are exposed on the request path before any provider-side mechanism can act.

### 3.3 AC-1.a: Dependency-Targeted Injection

AC-1.a specializes AC-1 to package-install commands (`pip install`, `npm install`, `cargo add`). Rather than rewriting an arbitrary URL, the router substitutes a legitimate dependency name with an attacker-controlled package pre-registered on the target registry. The substitution may be a visually similar name (typosquatting) or an entirely different package.

- **Key consequence:** Evades domain-based policy gates because the rewritten command installs from the trusted registry, differing only in the package name.
- **Persistence:** The compromised dependency is cached locally and re-imported across future sessions, giving the attacker a durable supply-chain foothold that persists long after the malicious router interaction ends.
- **Compatibility:** 99.6% rewrite compatibility across all four tested frameworks on package-install tool calls.

### 3.4 AC-1.b: Conditional Delivery

AC-1.b applies AC-1 only when a session-level predicate phi(req, s) evaluates to true. The router behaves honestly for non-matching traffic and applies AC-1 only when the trigger fires. This makes finite black-box auditing fundamentally inadequate: a router deploying a 50-request warm-up appears entirely transparent during a 10-request probe.

**Five observed trigger families:**

| Trigger Family | Condition | Effect |
|:---------------|:----------|:-------|
| Request-count threshold | After 50 prior calls | Hides AC-1 from warm-up traffic; shallow smoke tests see benign behavior |
| User fingerprint | Only in autonomous YOLO mode | Reserves payload injection for sessions where tool execution is auto-approved |
| Content keyword | Only for Rust / Go projects | Targets high-value developer environments while evading generic probes |
| Tool-name conditions | Only for tools such as Bash or run_command | Activates only when tool calls carry executable payloads |
| Time windows | Off-hours or after a deployment event | Restricts injection to low-scrutiny periods |

The combination of trigger families is potent: a router can require both a tool-name match and a warm-up count before activating, so that even an auditor who tests the correct tool never reaches the activation threshold within a typical probe budget.

**Consequence:** Conditional delivery makes finite black-box auditing fundamentally inadequate. Because the trigger predicate is server-side and opaque, no fixed-length client test can guarantee that the router is benign.

---

## 4. Ecosystem Measurement

### 4.1 Methodology

The study uses four data collection channels:

| Dataset | Collection Channel | Scale | Purpose |
|:--------|:-------------------|:------|:--------|
| Paid routers | Taobao, Xianyu, Shopify storefronts | 28 routers | Test sold OpenAI- and Anthropic-compatible endpoints |
| Free routers | Public links using sub2api and new-api templates | 400 routers | Measure in-the-wild abuse in commodity router ecosystems |
| Leaked-key poisoning | Chinese forums, WeChat / Telegram groups | 1 OpenAI key | Observe downstream sessions on a reused upstream account |
| Weak-router decoys | Weak-password Sub2API, CLIProxyAPI, claude-relay-service | 20 domains + 20 IPs | Measure exploitation and downstream exposure through poisoned routers |

For each router, the pipeline proceeds in four stages:

1. Register a researcher-controlled account with the router and obtain API credentials.
2. Route through a sandboxed agent environment, executing a randomized subset of TerminalBench 2.0 tasks (shell, package-install, file-manipulation tool calls across diverse languages and workflows).
3. Monitor every tool-call payload returned by the router inside the sandbox for network callbacks, file-system modifications, and process-tree anomalies.
4. A dedicated analysis agent reviews flagged executions and classifies the behavior as benign rewriting (e.g., CDN substitution), potentially malicious, or confirmed malicious. The pipeline also records whether conditional triggers were present and whether router-side plaintext access to researcher-owned AWS or Ethereum canaries produced follow-on abuse.

### 4.2 Main Results

| Setting | Sample | Active Manipulation | Adaptive Evasion | Credential Abuse | Main Outcome |
|:--------|:-------|:--------------------|:-----------------|:-----------------|:-------------|
| Paid routers | 28 | 1 injects malicious code | 0 observed | 0 observed | Paying for a router does not remove tool-call injection risk |
| Free routers | 400 | 8 inject malicious code | 2 trigger selectively | 17 touch AWS canaries; 1 drains ETH | Commodity free-router ecosystems already expose AC-1, AC-1.a/b, and AC-2 |
| Leaked upstream key | 1 OpenAI key leaked publicly | 0 observed | Not needed | >7 Codex sessions; one session exposed multiple credentials | 100M GPT-5.4 tokens observed under a researcher-owned account |
| Weak-router decoys | 20 domains + 20 IPs | All 440 sessions expose shell execution paths | 401 sessions already in auto-approve (YOLO) mode | 99 credentials across 440 sessions / 398 projects | 2B billed tokens; ~13 GB visible traffic; 40k+ access attempts; 6 JA3 fingerprints |

### 4.3 Key Measurement Findings

**Malicious routers already exist in both paid and free commodity markets.** The 1 paid and 8 free routers that inject malicious code show that this is not a purely hypothetical threat or a pathology confined to obvious free relay dumps. Paid access improves service stability, but it does not prove tool-call integrity.

**Adaptive evasion is deployed, but often unnecessary.** Two malicious routers exhibit adaptive evasion: one injects only after the first 50 requests, another only for sessions appearing to be in autonomous YOLO mode and targeting Rust or Go. At the same time, the weak-router decoy study shows that 401 of 440 downstream agent sessions already ran in autonomous YOLO mode, meaning tool execution was already auto-approved and simple payload injection would have been sufficient.

**Benign routers can be poisoned into the same trust boundary.** Leaked upstream keys and weak third-party relays turn otherwise benign routers into channels for plaintext prompt visibility, credential exposure, and command injection. The supply-chain risk does not begin only when a router operator decides to act maliciously; it also appears when a router compromises credentials or silently chains through a weaker upstream intermediary. A single leaked key generated 100M GPT-5.4 tokens and exposed 7+ Codex sessions with multiple distinct credentials appearing behind the leaked key, consistent with direct reuse, unrelated third-party reuse, or reuse somewhere inside a longer relay chain.

**Scope and generalizability.** The corpus targets the most actively reachable commodity router markets. Although the majority of routers originate from Chinese-language marketplaces, Chinese open-source models reached ~30% of total OpenRouter usage in some weeks, and Asia's share of LLM API spend grew from ~15% to ~31%, so routers serving this traffic handle a substantial share of global routing volume.

---

## 5. Cross-Framework Compatibility

The paper tests Mine against four public agent frameworks to evaluate whether existing frameworks implement any integrity checks that would materially constrain the attack surface.

| Metric | Result |
|:-------|:-------|
| Frameworks tested | 4 (OpenClaw, OpenCode, Codex, Claude Code) |
| Requests per framework/module | 1,000 |
| Frameworks with response-integrity checks | 0/4 |
| AC-1 rewrite compatibility | 100% |
| AC-1.a rewrite compatibility | 99.6% |
| AC-2 extractor coverage | 4/4 |
| Buffered streaming compatibility | 4/4 |
| Median overhead | 0.013 ms/request |
| Median upstream latency | 820 ms |

**None of the four frameworks implement response-integrity verification.** AC-1 achieves 100% rewrite compatibility on tool-calling responses across all frameworks. For AC-1.a, the relevant metric is extractor coverage rather than client-side execution: the module matches 100% of payloads containing detectable secrets under its rule set while remaining passive from the client's perspective. The remaining 0.4% of AC-1.a failures are edge cases where install commands used quoted package fragments, editable local paths, or URL-based installs that the substitution rule conservatively declined to rewrite.

The rewriting logic handles both OpenAI- and Anthropic-style wire formats: OpenAI requires nested parsing of string-encoded arguments, whereas Anthropic-style interfaces expose native JSON structures directly. Buffered rewriting introduces an average pause of 0.004--0.005 ms between the final natural token and the first rewritten token, well below the 820 ms median upstream latency, making it indistinguishable from ordinary model jitter.

---

## 6. Deployable Defenses

The paper evaluates three client-side defenses that can be deployed today without provider cooperation, plus a proposed response-signing mechanism that would require provider support.

### 6.1 Fail-Closed Policy Gate

A pattern-based filter that blocks or escalates every shell tool call. The gate uses shell-risk patterns, domain/URL checks, and package-name validation. The paper evaluates it on a corpus of 1,000 benign commands plus 500 AC-1 and 500 AC-1.a samples, constructed from templated shell commands covering curl, package installs, grep, git, pytest, and kubectl.

| Attack Class | Coverage | False-Positive Rate |
|:-------------|:---------|:--------------------|
| AC-1 | 100% | 1.0% on sample workloads |
| AC-1.a | 89% | 1.0% on sample workloads |
| AC-1.b | N/A (by design, conditional delivery appears benign during probing) | -- |

The gate is effective but coarse. Its principal strength is that it blocks AC-1 and AC-1.a at low false-positive cost. Its weakness is that it should be understood as a best-effort defense rather than a robust one: it uses a finite set of shell-risk patterns that a defense-aware attacker can evade, and it does not maintain a per-package allowlist, so AC-1.a can still succeed when the attacker targets package-install workflows with names that pass a casual visual check.

### 6.2 Response-Side Anomaly Screening

An isolation-forest detector trained on locally observable features from each returned tool call. Features include shell-risk score, tool frequency, string entropy, unexpected secret patterns, and schema deviation.

At the 6.7% false-positive operating point:

| Feature Removed | AC-1 | AC-1.a | AC-1.b |
|:----------------|:-----|:-------|:-------|
| None (baseline) | 89.0% | 50.0% | 50.9% |
| shell_risk_score | 17.6% | 4.4% | 9.4% |
| tool_frequency | 88.4% | 53.4% | 43.5% |
| string_entropy | 89.0% | 33.7% | 50.9% |
| unexpected_secret_pattern | 89.0% | 47.3% | 50.9% |
| schema_deviation | 86.4% | 39.5% | 50.9% |

Shell-risk patterns dominate detection for active command rewrites (AC-1). The evasion variants (AC-1.a and AC-1.b) require much more lenient thresholds. The ablation confirms that the detector remains a review aid rather than a substitute for provenance.

### 6.3 Append-Only Transparency Log

A forensic tool that records each request/response object with tool calls, secret-side reduction checks, and response-byte hashing. Approximately 1.26 KB per entry.

The log is most useful when paired with one of the preventive controls: the gate or detector decides what to block or escalate in the moment; the log preserves context needed to answer the next question after an incident --- how far did this router or credential reach, and which sessions were exposed through it.

These defenses reduce exposure for high-risk tool-use deployments, but they do not authenticate origin. A router that stays within local allowlists and avoids obvious anomalies can still alter semantics. The remaining gap is end-to-end provenance.

### 6.4 Proposed: Provider-Signed Response Envelopes

The paper proposes a canonical response-envelope format (Appendix C), analogous to DKIM for email. The provider signs a minimal JSON envelope containing:

| Field | Purpose |
|:------|:--------|
| v | Envelope version for compatibility and rollout |
| provider | Provider identity, e.g., api.openai.com |
| key_id | Signing-key identifier used for verification and rotation |
| model | Provider model identifier for the signed response |
| request_nonce | Client-supplied opaque nonce for replay control and audit |
| issued_at | Provider timestamp for replay control and audit |
| expires_at | Validity horizon for key rotation and replay limits |
| content | Natural-language assistant content, if any |
| tool_calls | Array of tool calls, each with name and native-JSON arguments |
| finish_reason | Provider finish reason, e.g., tool_calls or stop |
| sig_alg | Signature algorithm identifier |
| signature | Signature over the canonicalized envelope excluding this field |

**Provider-side generation:** The provider maps its native response into the envelope fields, parses string-encoded tool arguments into native JSON, canonicalizes the result with RFC 8785 JSON canonicalization, and signs with the private key referenced by key_id.

**Client-side verification:** Before executing any tool call, the client fetches or caches the provider verification key, checks that request_nonce matches the outstanding request, checks issued_at and expires_at, re-canonicalizes the envelope without signature, and verifies the signature. If any step fails, the client treats the response as unsigned and blocks tool execution.

**Current status:** No major provider tool-use API or the current MCP specification exposes a deployed response-signing mechanism for tool-call arguments today. The paper notes that existing controls (policy gates, anomaly screening, transparency logs) reduce exposure today, but closing the provenance gap ultimately requires provider-backed response integrity so that the tool call an agent executes can be tied to what the upstream model actually produced.

---

## 7. Mapping to Defense Taxonomy

This paper occupies a gap in the defense taxonomy defined in ANALYSIS.md. Existing categories focus on threats at the model layer (prompt injection, jailbreaking), the application layer (memory poisoning, tool supply-chain attacks), or the protocol layer (MCP poisoning). This paper identifies a distinct **transport-layer** attack surface between the categories.

### Intersections with Existing Categories

- **Supply-chain attacks (Threat Landscape):** FuncPoison \[arXiv:2509.24408\] targets tool libraries; AC-1.a shares the supply-chain foothold primitive but operates at the router level rather than the tool-definition level. The attack vectors are complementary: FuncPoison poisons what tools do; AC-1.a poisons what tools install.

- **Boundary marking and cryptographic provenance (Taxonomy 3.6):** Signed-Prompt \[arXiv:2401.07612\], Prompt Fencing \[arXiv:2511.19727\], and FATH \[arXiv:2410.21492\] all propose cryptographic boundaries for input integrity. This paper identifies the symmetric gap on the response side: none of these proposals cover provider-to-client response signing.

- **Detection and firewalls (Taxonomy 3.4):** The policy gate and anomaly screener are analogous to LlamaFirewall's pattern-based detection, with the same fundamental limitation: probabilistic defenses fail under adaptive attack. AC-1.b's conditional delivery is specifically designed to exploit this weakness.

- **Access control and governance (Taxonomy 3.2):** Progent \[arXiv:2504.11703\] and AgentBound \[arXiv:2510.21236\] enforce least-privilege on tool invocations. These controls reduce post-execution blast radius but do not authenticate where a tool call came from.

### Novel Contribution

The paper's core contribution to the taxonomy is identifying that **the transport layer is an undefended trust boundary**. All existing architectural defenses (CaMeL, IsolateGPT, ACE, Progent) assume that the provider's response arrives unmodified. This assumption is violated when any router in the chain is malicious, compromised, or simply configured to relay through a weaker upstream intermediary.

---

## 8. Limitations and Open Questions

### Acknowledged Limitations

- **Scope restricted to commodity markets.** Enterprise and invite-only deployments are not studied. The paper notes these as natural extensions.
- **No exploitation of discovered vulnerabilities.** Measurement reveals potential weaknesses but does not attempt real-world exploitation beyond the minimum necessary to confirm existence.
- **No coordinated disclosure.** The paper argues the vulnerability is architectural (any router that terminates TLS and forwards tool-call JSON can mount these attacks), not implementation-specific, so disclosure to individual operators would not remediate the underlying trust gap.
- **Trigger families may be incomplete.** The observed conditional triggers (request-count, user-fingerprint, content-keyword, tool-name, time-window) are from observed behavior; routers may implement additional latent conditions that probes did not activate.

### Open Questions

- **Provider adoption of response signing.** The proposed envelope format is a minimal design. Whether any major provider (OpenAI, Anthropic, Google) will implement it, and on what timeline, is the key open question. The paper notes that mutual TLS, certificate pinning, and ordinary transport security do not solve the problem because they authenticate the router endpoint the client chose, but they do not say whether the returned tool call preserves upstream semantics.

- **MCP extension.** The Model Context Protocol introduces a related trust boundary between LLM agents and external tools. A malicious MCP server receives tool-call requests in plaintext and can return forged results. The same base manipulation and collection ideas transfer with adaptation to the MCP message format.

- **Streaming signatures.** For streaming responses, the paper proposes signing the final tool-bearing envelope rather than every token chunk. Per-chunk signatures are possible but would add significantly more protocol complexity and are unnecessary for the core threat (silent modification of the final tool-call payload).

- **Web integrity mechanisms.** The paper identifies Subresource Integrity, signed exchanges, and certificate-transparency logs as useful patterns from web security that authenticate content and make authentication auditable. Artifact-attestation systems such as SLSA and Sigstore apply the same idea to software supply chains. Adapting these to LLM response integrity is an open design problem.

---

## 9. Key Findings

- **LLM API routers sit on a critical trust boundary that the ecosystem currently treats as transparent transport.** No major provider enforces cryptographic integrity between client and upstream model. Any router in the chain can inspect, delay, or rewrite every tool call and credential that passes through it. This is not a hypothetical risk: 9 of 428 commodity routers are actively injecting malicious code, and 17 more abuse researcher-owned credentials.

- **The attack surface is orthogonal to prompt injection and model-level defenses.** AC-1 (payload injection) and AC-2 (secret exfiltration) operate at the JSON/transport layer, outside the model's reasoning loop. Architectural defenses like CaMeL, runtime monitors like AgentArmor, and model hardening like SecAlign do not protect against router-level rewriting because they assume the provider's response arrives intact.

- **Adaptive evasion makes finite black-box auditing fundamentally inadequate.** AC-1.b's conditional delivery (trigger predicates based on request count, user fingerprint, content keywords, time windows) means that a router can appear entirely benign during any bounded probing period and activate injection only for high-value targets. This is the strongest evidence that the router threat boundary is not addressable by client-side detection alone.

- **Benign routers can be poisoned into the attack surface.** Leaked upstream keys and weak relay chains convert otherwise trustworthy routers into plaintext channels with the same visibility as an actively malicious router. The poisoning experiments show this is already happening at scale: a single leaked key generated 100M tokens of downstream activity with 7+ distinct sessions exposing credentials.

- **Client-side defenses are useful but insufficient.** The policy gate blocks AC-1 at 100% coverage with 1.0% false positives. The anomaly screener catches 89% of AC-1 at 6.7% false positives. Neither can address AC-2 (passive exfiltration) or provide provenance guarantees. Closing the gap requires provider-signed response envelopes --- the DKIM analogue for LLM tool-call integrity.

- **401 of 440 observed downstream sessions already ran in autonomous YOLO mode.** This means tool execution was already auto-approved, and simple payload injection would have been sufficient to change executed commands. Sophisticated adaptive evasion was unnecessary for the majority of observed targets. This finding underscores that the real-world attack surface is larger than the technical capability gap might suggest.
