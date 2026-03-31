# Production Agent Framework Security Comparison

**6 frameworks | 4 security-focused + 2 baseline | Point-in-time: 2026-03-31**

*Cross-cutting synthesis of individual framework analyses against the ANALYSIS.md defense taxonomy (79 papers, 7 defense categories).*

---

## Executive Summary

We analyzed six production agent frameworks -- four marketed as security-focused and two as general-purpose "baselines" -- by reading their documentation AND source code. The goal: understand how real production systems compare to the academic defense landscape surveyed in ANALYSIS.md.

**Five findings define the current state of production agent security:**

1. **The "baseline" vs "security-focused" distinction is blurrier than expected.** Both baselines (openclaw, hermes-agent) implement substantial security infrastructure: dangerous command detection, SSRF protection, DM pairing, sandbox validation, supply chain auditing. The gap between baselines and security-focused frameworks is narrower than the gap between any of these frameworks and the academic state-of-the-art (CaMeL, Fides, AgentArmor).

2. **Execution-layer security is solved; intent-layer security is not.** All six frameworks can enforce policies on what actions an agent takes (command blocking, sandboxing, network filtering). None of them can reliably determine whether a policy-allowed action was requested by the user or injected by an attacker. This is the fundamental gap between current production systems and the CaMeL/IFC research paradigm.

3. **No production framework implements formal information flow control.** The strongest IFC-adjacent implementation is openfang's lattice-based taint tracking, but even that appears underintegrated with the actual agent execution loop. shisad's taint-sink enforcement model is functional but operates at the content-block level, not the variable level. No framework provides CaMeL-style provenance tracking through the computation graph.

4. **Defense-in-depth is genuinely implemented, not just marketed.** Unlike the academic landscape where most papers propose a single defense layer, every production framework layers multiple independent mechanisms. agentsh layers 5 kernel-level enforcement points; openfang has 16 independent security systems; shisad chains PEP + control-plane consensus + behavioral analysis + sandbox isolation.

5. **Pattern-based prompt injection detection is universal and universally insufficient.** Every framework that attempts injection detection uses regex/keyword matching. None deploys an ML-based classifier. All acknowledge this limitation to varying degrees. ironclaw is the most transparent, with adversarial tests that explicitly document known bypass vectors.

---

## Framework Overview

| Framework | Category | Language | Codebase | Architecture | Primary Security Thesis |
|-----------|----------|----------|----------|-------------|------------------------|
| **agentsh** | Security | Go | ~240K lines, 493 test files | Execution-layer gateway (FUSE + seccomp + ptrace + Landlock + eBPF) | Interpose between agent and OS; enforce policy at the syscall layer |
| **openfang** | Security | Rust | ~177K lines, 1,767+ tests | Agent OS with 14 crates | Deny-by-default capabilities + WASM sandbox + taint tracking |
| **ironclaw** | Security | Rust | v0.22.0, 5 fuzz targets | Privacy-first assistant with extracted safety crate | Zero-exposure credentials + multi-layer safety pipeline |
| **shisad** | Security | Python | ~46.5K src + ~43.7K tests | Security-first daemon with metadata-only control plane | LLM proposes, runtime decides; PEP never sees untrusted content |
| **openclaw** | Baseline | TypeScript | ~3,050 src + 3,313 test files | Personal assistant with Gateway control plane | Single trusted operator; strong defaults without killing capability |
| **hermes-agent** | Baseline | Python | ~10K+ main file, 100+ tests | Self-improving agent with multi-platform gateway | Pragmatic defense-in-depth for a single-user agent |

---

## Defense Taxonomy Matrix

Ratings: **Strong** = substantive implementation with meaningful coverage. **Partial** = some relevant features but significant gaps. **Minimal** = token effort or narrow scope. **None** = not addressed.

### Summary Matrix

| Category | agentsh | openfang | ironclaw | shisad | openclaw | hermes-agent |
|----------|---------|----------|----------|--------|----------|-------------|
| 3.1 Secure Architectures | Partial | Partial | Partial | **Strong** | Partial | Partial |
| 3.2 Access Control | **Strong** | **Strong** | **Strong** | **Strong** | **Strong** | Partial |
| 3.3 Runtime Verification | **Strong** | **Strong** | Partial | **Strong** | Partial | Partial |
| 3.4 Detection & Filtering | Partial | Partial | Partial | **Strong** | Partial | Partial |
| 3.5 Model Hardening | None | None | None | Minimal | Minimal | None |
| 3.6 Boundary Marking | Partial | Partial | Partial | **Strong** | Partial | None |
| 3.7 Formal Methods | None | None | None | None | Partial | None |

### Detailed Breakdown

#### 3.1 Secure Architectures by Construction

*The gold standard: CaMeL-style IFC with dual-LLM separation, typed data flow, and provenance tracking.*

| Framework | What's Implemented | What's Missing |
|-----------|-------------------|----------------|
| **agentsh** | Control plane (daemon) / data plane (agent process) separation; taint-aware policy via process ancestry chains | No IFC, no dual-LLM, no typed data flow; operates below intent layer |
| **openfang** | Kernel/runtime separation via `KernelHandle` trait; lattice-based taint tracking with labeled sinks | Taint appears underintegrated with agent loop; no dual-LLM; no formal non-interference |
| **ironclaw** | Trusted host / untrusted sandbox separation; boundary wrapping for tool outputs | No IFC, no dual-LLM; single-LLM architecture for planning and execution |
| **shisad** | Three-tier context scaffold; metadata-only control plane; evidence store separates raw content from LLM; taint-sink enforcement | COMMAND/TASK agent split not yet first-class runtime concept; taint at block level, not variable level |
| **openclaw** | Gateway / sandbox separation; plugin SDK import boundaries; per-session isolation | In-process plugin execution; logical not process-level session isolation |
| **hermes-agent** | Code sandbox with stripped env and RPC; subagent isolation with restricted toolsets | No formal architectural model; shared process space for tool system |

**Assessment:** shisad comes closest to CaMeL-inspired architecture with its metadata-only PEP and three-tier context scaffold, but the COMMAND/TASK agent separation -- the key to preventing taint accumulation in the main context -- is not yet a first-class runtime concept. openfang's taint tracking is the most formally structured (lattice-based with typed sinks) but its integration into the actual execution flow is unclear. No framework achieves variable-level provenance tracking.

#### 3.2 Access Control and Governance

*The gold standard: Progent-style least-privilege DSL with automated policy generation.*

| Framework | Capability System | Policy Language | Tool-Level Control | MCP/A2A Control | Approval Flow |
|-----------|------------------|-----------------|--------------------|-----------------|---------------|
| **agentsh** | Process-level (file/net/cmd/env/signal rules) | YAML DSL with globs, regex, variable expansion | Command + args pattern matching; first-match-wins | Tool whitelisting, version pinning, rate limits | TTY, TOTP, WebAuthn, REST API |
| **openfang** | 22-variant typed `Capability` enum with globs | TOML config + `ToolPolicy` struct | Deny-wins glob rules; group expansion; depth restrictions | MCP server config | Per-agent approval manager |
| **ironclaw** | WASM capability flags (HTTP, workspace, tools, secrets) | JSON sidecar `.capabilities.json` | Autonomous tool denylist (17 tools) | MCP client | Tool approval mechanism |
| **shisad** | Session capability set (10 capabilities) | YAML with Pydantic validation + hot reload | Per-tool allowlist + schema validation + argument DLP | Not implemented | Nonce-based confirmation + PEP re-evaluation |
| **openclaw** | 5-level operator RBAC | Config + tool profiles | Allow/deny lists; owner-only tools; safe bins | Not implemented | Interactive UUID-based; single-use; time-limited |
| **hermes-agent** | Toolset enable/disable | Config YAML | Blocked toolsets; sandbox tool allowlist (7 tools) | Not implemented | 3 modes: manual, smart (LLM), off |

**Assessment:** agentsh and openfang have the most granular permission models. agentsh's policy language is the most expressive (YAML DSL with variable expansion, regex args matching, redirect decisions, and Ed25519-signed policies). openfang's typed capability enum with inheritance validation is the most formally rigorous. shisad's most-restrictive-wins policy merge is a novel contribution -- callers can only narrow access, never widen it. MCP-specific access control is only implemented by agentsh (and notably well -- tool whitelisting, version pinning, rug-pull detection, cross-server exfiltration analysis).

#### 3.3 Runtime Verification and Policy Enforcement

*The gold standard: AgentArmor-style trace analysis with CFG/DFG/PDG over execution traces.*

| Framework | Pre-Execution Check | During-Execution Enforcement | Behavioral Analysis | Loop/Drift Detection | Graduated Response |
|-----------|--------------------|-----------------------------|---------------------|---------------------|-------------------|
| **agentsh** | Command policy eval | FUSE + seccomp + ptrace + Landlock + eBPF | MCP cross-server exfiltration patterns | Not explicit | Allow/deny/approve/redirect |
| **openfang** | Capability + tool policy + approval | WASM fuel + epoch metering | Phantom action detection (hallucinated tool use) | Loop guard with circuit breaker; ping-pong detection | Allow -> Warn -> Block -> CircuitBreak |
| **ironclaw** | Sanitizer + validator + policy | WASM fuel + memory limits + timeout | Not implemented | Not implemented | Block/Warn/Review/Sanitize |
| **shisad** | PEP 8-check pipeline + control-plane consensus | Sandbox with network isolation | 5 behavioral sequence patterns; plan commitment verification | Rate limiting; lockdown escalation | Auto-approve -> Confirm -> Deny -> Lockdown (4 levels) |
| **openclaw** | Tool policy + ACP approval classifier | Docker sandbox validation | Not implemented | Not implemented | Auto-approve/ask/deny; allow-once/always |
| **hermes-agent** | Dangerous command patterns + tirith scanner | Container isolation (when used) | Not implemented | Read-loop detection | Manual/smart/off approval |

**Assessment:** shisad has the most sophisticated runtime verification with its 5-voter consensus system, behavioral sequence analysis, and 4-level lockdown escalation. agentsh has the deepest kernel-level enforcement with 5 independent OS-level interception points. openfang's loop guard with ping-pong pattern detection and circuit breaker is a pragmatic feature other frameworks lack. No framework implements the trace-level program analysis (CFG/DFG/PDG) seen in AgentArmor or the causal independence testing of MELON.

#### 3.4 Detection, Filtering, and Firewalls

*The gold standard: LlamaFirewall's modular policy engine or MELON's causal independence detection.*

| Framework | Injection Detection | Secret/PII Detection | Network Filtering | Supply Chain | Encoding Evasion Handling |
|-----------|--------------------|--------------------|------------------|-------------|--------------------------|
| **agentsh** | MCP suspicious pattern scanning | DLP regex (email, phone, CC, SSN, API keys) | eBPF + threat feed integration | Package install checking | Not documented |
| **openfang** | 10 keyword patterns + 9 exfil patterns + 3 shell patterns | Secret zeroization; env stripping | SSRF (multi-layer IP blocking + DNS rebinding defense) | Ed25519 manifest signing + SHA256 skill checksums | Shell bleed detection |
| **ironclaw** | 18+ Aho-Corasick literals + 4 regex patterns | 16 API key patterns + credential detection | SSRF + endpoint allowlisting | cargo-deny; Ed25519 webhooks | Unicode bypass vectors documented but unfixed |
| **shisad** | Pattern + YARA (13 rule files) + multi-layer base64 decoding | Secret detection + PII redaction + argument DLP | Egress allowlisting with provenance-aware routing | Ed25519 skill signatures + dependency chain verification + multi-engine analysis | Recursive encoding unwrapping (2 layers) |
| **openclaw** | External content wrapping with injection pattern logging | detect-secrets CI (433KB baseline) | SSRF with DNS rebinding defense | Skill scanner | Exec obfuscation detection (base64, hex, Unicode) |
| **hermes-agent** | Cron prompt injection scanning only | 20+ API key prefix patterns + PII redaction | SSRF (browser tool only) | CI supply chain audit + tirith binary verification | ANSI stripping + Unicode NFKC normalization |

**Assessment:** shisad's content firewall is the most comprehensive with YARA rules covering 13 attack categories and recursive encoding detection. agentsh's MCP-specific detection (cross-server exfiltration, rug-pull, shadow tool replacement) addresses threats no other framework detects. ironclaw's adversarial testing methodology -- explicitly documenting known bypass vectors -- is exemplary. All detection is pattern-based; no framework deploys an ML classifier. The gap between these systems and LlamaFirewall (production at Meta with PromptGuard 2 neural classifier) is significant.

#### 3.5 Model-Level Hardening

*The gold standard: SecAlign/Meta SecAlign preference optimization or instruction hierarchy.*

**No framework implements model-level hardening.** All six are model-agnostic and explicitly treat the LLM as an untrusted component. shisad's action monitor uses simple heuristics (suspicious keyword matching in arguments) which is minimal. openclaw recommends "strongest latest-generation models" to reduce injection risk.

This is the correct design choice for multi-provider frameworks, but it means that instruction hierarchy and preference optimization -- which research shows provide meaningful (if insufficient) baseline resistance -- are entirely absent from the production stack.

#### 3.6 Boundary Marking and Cryptographic Provenance

*The gold standard: Signed-Prompt or Encrypted Prompt with cryptographic permission tokens.*

| Framework | Prompt Boundary Marking | Audit Integrity | Policy Integrity | Credential Protection |
|-----------|------------------------|-----------------|-----------------|----------------------|
| **agentsh** | None | HMAC chain + external KMS (AWS/Azure/GCP/Vault) | Ed25519 policy signatures | DLP redaction in LLM proxy |
| **openfang** | None | Merkle SHA-256 hash chain | Ed25519 manifest signing | AES-256-GCM vault + Argon2 KDF + zeroization |
| **ironclaw** | XML boundary wrapping + delimiter escape | None | Ed25519 webhook verification | AES-256-GCM + HKDF-SHA256 per-secret keys + OS keychain |
| **shisad** | Random cryptographic delimiters + datamarking + three-tier placement | Append-only audit log | SHA256 policy integrity + SIGHUP-only reload | Credential broker with placeholders + proxy-level injection |
| **openclaw** | Randomized XML boundary markers with security notices | None | None | Environment variable sanitization in sandbox |
| **hermes-agent** | None | None | None | Env var filtering in code sandbox |

**Assessment:** shisad's approach is the most comprehensive -- cryptographically random delimiters, character-level datamarking, three-tier context placement, and provenance annotations. agentsh has the strongest audit integrity (HMAC chains with external KMS from four major cloud providers). For credential protection, ironclaw's zero-exposure model (WASM tools never see secrets, injection at host boundary, leak detection at both request and response boundaries) and shisad's credential broker (placeholder substitution at egress proxy only) are the strongest implementations. No framework implements the Signed-Prompt or Encrypted Prompt patterns from the academic literature.

#### 3.7 Formal Methods and Semantics

*The gold standard: Fides/LLMbda Calculus noninterference proofs.*

**Surprisingly, the closest to formal methods is the "baseline" openclaw**, which maintains TLA+ models for its highest-risk paths (gateway exposure, exec pipeline, pairing store). No security-focused framework provides formal verification. openfang's taint tracking uses lattice-based semantics but has no proof. shisad's taint system follows IFC principles but lacks a consistency checker. ironclaw has fuzz targets but no formal models.

---

## Architectural Comparison

### Where Security Lives

Each framework places its primary security enforcement at a different layer:

```
                    Academic ideal (CaMeL/Fides)
                    ┌─────────────────────────────────┐
                    │ Formal IFC + provenance tracking │  ← No production framework
                    │ through computation graph        │
                    └─────────────────────────────────┘
                                    │
      ┌─────────────────────────────┼─────────────────────────────┐
      │                             │                             │
  Intent Layer              Policy Layer                  Execution Layer
  (shisad)                 (openfang, ironclaw)          (agentsh)
  ┌───────────────┐        ┌───────────────┐            ┌───────────────┐
  │ Metadata-only │        │ Capability    │            │ FUSE + seccomp│
  │ PEP; context  │        │ checks before │            │ + ptrace +    │
  │ scaffold;     │        │ tool dispatch;│            │ Landlock +    │
  │ consensus     │        │ WASM sandbox; │            │ eBPF          │
  │ voting        │        │ taint sinks   │            │               │
  └───────────────┘        └───────────────┘            └───────────────┘
                                    │
                    ┌───────────────┴───────────────┐
                    │        Baselines               │
                    │ (openclaw: approval + sandbox) │
                    │ (hermes: approval + patterns)  │
                    └────────────────────────────────┘
```

**Key insight:** These layers are complementary, not competing. An ideal production system would combine shisad's intent-layer analysis (does this action serve the user's goal?) with openfang's policy-layer enforcement (does the agent have this capability?) and agentsh's execution-layer enforcement (is this syscall allowed?). No single framework spans all three.

### Unique Contributions by Framework

| Framework | Novel/Unique Feature | Why It Matters |
|-----------|---------------------|----------------|
| **agentsh** | Redirect decision type; MCP rug-pull detection | Redirect reduces agent error loops; MCP security addresses emerging threat vector |
| **openfang** | WASM dual metering (fuel + epoch); phantom action detection | Fuel catches compute loops, epochs catch host call abuse; phantom detection catches hallucinated tool use |
| **ironclaw** | Adversarial test methodology with documented bypasses; extracted safety crate with fuzzing | Sets transparency standard; enables focused security testing |
| **shisad** | Taint-sink endorsement separation (USER_REVIEWED != TRUSTED); provenance-aware 5-tier egress; most-restrictive-wins policy merge | User approval doesn't upgrade trust; distinguishes user-requested from injection-driven destinations; callers can only narrow access |
| **openclaw** | TLA+ formal models; `openclaw security audit --deep` CLI; `dangerously*` flag convention | Unusual formal verification for application code; proactive security configuration auditing |
| **hermes-agent** | Tirith external scanner with cosign provenance; smart (LLM) approval; supply chain CI audit | Binary integrity verification; LLM-assisted risk assessment; automated dependency attack detection |

---

## Security Posture Spectrum

### Strongest Per Category

| Category | Best Framework | Runner-up | Notes |
|----------|---------------|-----------|-------|
| **Overall architecture** | shisad | openfang | shisad's metadata-only PEP is structurally injection-proof |
| **Access control granularity** | agentsh | openfang | agentsh's YAML DSL with variable expansion and redirect decisions |
| **Runtime enforcement depth** | agentsh | shisad | agentsh has 5 independent kernel-level enforcement points |
| **Detection sophistication** | shisad | agentsh | shisad's YARA + encoding detection; agentsh's MCP analysis |
| **Credential protection** | ironclaw / shisad (tie) | openfang | Zero-exposure model with proxy-level injection |
| **Audit integrity** | agentsh | openfang | HMAC chain + external KMS |
| **Test discipline** | ironclaw | shisad | Adversarial tests documenting known bypasses; fuzz targets |
| **Formal rigor** | openclaw (!) | openfang | TLA+ models for highest-risk paths |

### Production Readiness Ranking

| Rank | Framework | Maturity Indicators |
|------|-----------|-------------------|
| 1 | **openclaw** | Daily calver releases; 3,313 tests; 70% coverage thresholds; macOS signing; npm/Docker distribution; dedicated Security & Trust lead; bug bounty |
| 2 | **agentsh** | 240K lines; cross-platform (Linux/macOS/Windows); GoReleaser packaging; CI on 3 platforms; 493 test files |
| 3 | **openfang** | 177K Rust; 1,767+ tests; single ~32MB binary; Docker + Tauri desktop |
| 4 | **hermes-agent** | v0.6.0; 100+ test files; 14+ platform adapters; Docker + Nix; production gateway |
| 5 | **ironclaw** | v0.22.0; fuzz targets + benchmarks; 7 build targets; systemd/launchd support |
| 6 | **shisad** | 46.5K src + 43.7K tests; Unix socket daemon; multi-channel; strong security tests but pre-release |

---

## The Gap Between Production and Academic State-of-the-Art

### What Production Systems Have That Academia Doesn't

1. **Real tool ecosystems.** Academic systems test against AgentDojo's 4 domains or toy environments. Production frameworks manage 40+ messaging platforms, 50+ tools, MCP servers, file systems, browsers, and shell access. The attack surface is orders of magnitude larger.

2. **Operational recovery.** Academic papers measure ASR and utility. Production systems implement lockdown escalation (shisad), checkpoint/rollback (agentsh), session repair (openfang), and graduated response ladders. The question isn't just "did the attack succeed?" but "can the system recover?"

3. **Supply chain defenses.** Academic work focuses on prompt injection. Production frameworks defend against poisoned skills (openfang, ironclaw, shisad), tampered tool definitions (agentsh MCP version pinning), malicious dependencies (hermes-agent CI audit), and corrupted agent manifests (openfang Ed25519 signing).

4. **Credential protection infrastructure.** No academic paper we surveyed addresses the practical problem of keeping API keys and secrets away from the LLM. Three production frameworks (ironclaw, shisad, agentsh) implement proxy-level credential injection where the LLM never sees raw secrets.

5. **Cross-platform enforcement.** agentsh implements full enforcement stacks for Linux (5 layers), macOS (4 layers), and Windows (4 layers). Academic prototypes are single-platform.

### What Academia Has That Production Doesn't

1. **Variable-level provenance tracking.** CaMeL tracks data provenance through the computation graph at the variable level. No production framework achieves this -- shisad tracks at the content-block level, openfang at the value level (but underintegrated).

2. **Formal non-interference guarantees.** Fides and LLMbda Calculus prove that untrusted data cannot influence trusted decisions. No production system has formal proofs.

3. **Causal independence detection.** MELON's dual-execution approach (testing whether an action would occur regardless of user intent) is not implemented in any production framework.

4. **ML-based prompt injection classification.** LlamaFirewall's PromptGuard 2 is a production-deployed neural classifier. No open-source agent framework includes one.

5. **Structured plan verification.** CaMeL generates restricted Python plans that can be statically analyzed. AgentArmor applies CFG/DFG/PDG analysis to execution traces. Production frameworks verify actions individually, not as execution graphs.

---

## Cross-Cutting Observations

### The Taint Tracking Gap

Three frameworks implement taint tracking (openfang, shisad, and partially ironclaw via boundary wrapping), but none achieves the CaMeL standard:

| Framework | Taint Granularity | Taint Propagation | Taint Enforcement | Formal Basis |
|-----------|-------------------|-------------------|-------------------|-------------|
| CaMeL (reference) | Variable-level | Through computation graph | Capability tokens gate tool access | IFC with proofs |
| openfang | Value-level (5 labels) | Union semantics | Predefined sinks block specific labels | Lattice-inspired; no proof |
| shisad | Content-block-level (6 labels) | Worst-case union | PEP taint-sink rules; confirmation for writes | IFC-inspired; no proof |
| ironclaw | Content-level | Not propagated; boundary-marked | Policy rules per severity | None |

The gap is clear: academic IFC tracks provenance through the computation; production systems label content blobs. This means production taint tracking can't detect when clean-looking output was derived from tainted input through a sequence of processing steps.

### The MCP Security Gap

MCP (Model Context Protocol) is rapidly becoming the standard for agent-tool integration, but only **agentsh** implements MCP-specific security (tool whitelisting, version pinning, rug-pull detection, cross-server exfiltration analysis, rate limiting, suspicious pattern scanning). This is a significant gap -- MCP servers are a growing attack surface (6,000+ in PulseMCP), and the academic AgentBound paper identifies the need for Android-style MCP permissions.

### The Approval Fatigue Problem

Five of six frameworks implement human-in-the-loop approval for risky actions. All face the same problem: approval fatigue. Only shisad addresses this systematically with graduated response (auto-approve for low-risk, confirm for medium, deny for high, lockdown for anomalies) and rate-limiting that triggers confirmation as limits approach. agentsh's SECURITY.md acknowledges the fatigue attack vector. This is an unsolved UX problem that directly impacts security effectiveness.

### Languages and Safety

The language choice has security implications:

| Language | Frameworks | Memory Safety | Type Safety for Security |
|----------|-----------|--------------|------------------------|
| **Rust** | openfang, ironclaw | Yes (ownership) | Strong (typed capabilities, no unwrap in prod) |
| **Go** | agentsh | Yes (GC) | Moderate (interfaces, but no generics for security types) |
| **Python** | shisad, hermes-agent | No | Pydantic validation; mypy |
| **TypeScript** | openclaw | No | Zod schemas at boundaries |

Rust provides the strongest language-level safety guarantees, which is reflected in openfang's typed `Capability` enum and ironclaw's zero-unwrap policy. Python frameworks compensate with Pydantic validation and comprehensive testing.

---

## Recommendations

### For Framework Developers

1. **Integrate taint tracking into the agent loop, not just the type system.** openfang's lattice-based taint types exist but need to be actively checked at every data flow boundary in the agent execution cycle. shisad shows how to do this with its PEP pipeline.

2. **Implement MCP security controls.** agentsh's approach (tool whitelisting, version pinning, cross-server exfiltration detection) should be considered table stakes as MCP adoption grows.

3. **Move toward variable-level provenance.** Content-block taint tracking is useful but can't detect multi-step derivation attacks. CaMeL's approach of tracking provenance through the computation graph is the research direction most worth pursuing for production.

4. **Add ML-based injection classification.** Pattern matching has a ceiling. Even a simple fine-tuned classifier would significantly improve detection of obfuscated injection attempts.

5. **Consider a composable defense architecture.** The ideal system would layer agentsh-style execution enforcement, openfang/shisad-style policy enforcement, and shisad-style intent analysis. No single framework needs to build all layers -- well-defined interfaces between layers would allow composition.

### For Practitioners Choosing a Framework

| If you need... | Consider |
|----------------|----------|
| Maximum execution-layer enforcement | **agentsh** -- deepest OS-level interposition on Linux; works with any agent framework |
| Comprehensive security architecture | **openfang** or **shisad** -- most complete defense-in-depth stacks |
| Strongest credential protection | **ironclaw** or **shisad** -- zero-exposure credential models |
| Production maturity with security | **openclaw** -- most mature release process with substantial security infrastructure |
| Privacy-focused local operation | **ironclaw** -- data sovereignty design with encrypted storage |
| MCP security | **agentsh** -- only framework with comprehensive MCP security controls |

### For Researchers

1. **Test defenses against production-scale tool ecosystems**, not just AgentDojo's 4 domains. The attack surface of 40+ messaging platforms, MCP servers, and browser tools is qualitatively different.

2. **Address the credential protection problem.** Three production frameworks independently invented proxy-level credential injection. This is a real need that the academic literature hasn't addressed.

3. **Study approval fatigue formally.** The human-in-the-loop assumption in many defense papers ignores the reality that users approve automatically after sufficient repetition.

4. **Bridge the IFC integration gap.** CaMeL-style provenance tracking works in research prototypes. The challenge is integrating it into production frameworks with their diverse tool ecosystems, multi-provider LLM backends, and operational requirements.

---

## Individual Analysis Index

| Framework | Analysis File | Lines | Key Finding |
|-----------|--------------|-------|-------------|
| agentsh | [ANALYSIS-agentsh.md](ANALYSIS-agentsh.md) | 374 | Most comprehensive execution-layer security; MCP security standout |
| openfang | [ANALYSIS-openfang.md](ANALYSIS-openfang.md) | 352 | 16 independent security systems; taint tracking underintegrated |
| ironclaw | [ANALYSIS-ironclaw.md](ANALYSIS-ironclaw.md) | 328 | Exemplary adversarial testing; zero-exposure credentials; no TEE despite privacy focus |
| shisad | [ANALYSIS-shisad-v2.md](ANALYSIS-shisad-v2.md) | 420 | Metadata-only PEP is structurally injection-proof; endorsement/taint separation novel |
| openclaw | [ANALYSIS-openclaw.md](ANALYSIS-openclaw.md) | 349 | Surprisingly security-mature for baseline; TLA+ formal verification; security audit CLI |
| hermes-agent | [ANALYSIS-hermes-agent.md](ANALYSIS-hermes-agent.md) | 366 | Strong baseline with supply chain CI, DM pairing (OWASP/NIST), tirith scanner |

---

## Methodology

Each framework was analyzed at a specific git commit (point-in-time) by reading documentation AND source code. Analysis followed a consistent structure mapped to the 7-category defense taxonomy from ANALYSIS.md (79 academic papers). Security-focused and baseline frameworks were analyzed with the same structure to enable direct comparison. Individual analyses were performed by independent research agents in parallel, then synthesized into this comparison.
