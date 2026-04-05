# Production Agent Framework Security Comparison

**6 frameworks | 4 security-focused + 2 baseline | Point-in-time: 2026-04-06**

*Cross-cutting synthesis of individual framework analyses against the ANALYSIS.md defense taxonomy (79 papers, 7 defense categories). Updated to reflect shisad v0.6.1 (process-isolated control plane, PromptGuard 2 ML injection classifier, Tool Dependency Graph verification, phantom action detection).*

---

## Executive Summary

We analyzed six production agent frameworks -- four marketed as security-focused and two as general-purpose "baselines" -- by reading their documentation AND source code. The goal: understand how real production systems compare to the academic defense landscape surveyed in ANALYSIS.md.

**Five findings define the current state of production agent security:**

1. **The "baseline" vs "security-focused" distinction is blurrier than expected.** Both baselines (openclaw, hermes-agent) implement substantial security infrastructure: dangerous command detection, SSRF protection, DM pairing, sandbox validation, supply chain auditing. The gap between baselines and security-focused frameworks is narrower than the gap between any of these frameworks and the academic state-of-the-art (CaMeL, Fides, AgentArmor).

2. **Execution-layer security is solved; intent-layer security is not.** All six frameworks can enforce policies on what actions an agent takes (command blocking, sandboxing, network filtering). None of them can reliably determine whether a policy-allowed action was requested by the user or injected by an attacker. This is the fundamental gap between current production systems and the CaMeL/IFC research paradigm.

3. **One production framework now implements practical information flow control.** shisad v0.6.0 ships a formal COMMAND/TASK agent separation with immutable task envelopes, taint-safe handoffs, mandatory summary-firewall checkpoints at the TASK-to-COMMAND boundary, and a structured ArtifactLedger with endorsement tracking and metadata MAC integrity. This is the first production implementation of the CaMeL-inspired dual-agent architecture with explicit trust boundaries. It still operates at the content-block level (not CaMeL's variable level), but the provenance gap between production and academic IFC has narrowed significantly. openfang's lattice-based taint tracking remains underintegrated with its execution loop.

4. **Defense-in-depth is genuinely implemented, not just marketed.** Unlike the academic landscape where most papers propose a single defense layer, every production framework layers multiple independent mechanisms. agentsh layers 5 kernel-level enforcement points; openfang has 16 independent security systems; shisad chains PEP + control-plane consensus + behavioral analysis + sandbox isolation.

5. **Pattern-based prompt injection detection is nearly universal and universally insufficient on its own.** Every framework that attempts injection detection includes regex/keyword matching. shisad v0.6.1 is now the first to also deploy an ML-based classifier (PromptGuard 2, local ONNX inference with signed model-packs) alongside its pattern + YARA layers. All other frameworks remain pattern-only. ironclaw is the most transparent about limitations, with adversarial tests that explicitly document known bypass vectors.

---

## Framework Overview

| Framework | Category | Language | Codebase | Architecture | Primary Security Thesis |
|-----------|----------|----------|----------|-------------|------------------------|
| **agentsh** | Security | Go | ~240K lines, 493 test files | Execution-layer gateway (FUSE + seccomp + ptrace + Landlock + eBPF) | Interpose between agent and OS; enforce policy at the syscall layer |
| **openfang** | Security | Rust | ~177K lines, 1,767+ tests | Agent OS with 14 crates | Deny-by-default capabilities + WASM sandbox + taint tracking |
| **ironclaw** | Security | Rust | v0.22.0, 5 fuzz targets | Privacy-first assistant with extracted safety crate | Zero-exposure credentials + multi-layer safety pipeline |
| **shisad** | Security | Python | v0.6.1; ~114K lines (src+tests+scripts); 1,522 test functions | Security-first daemon with COMMAND/TASK orchestration + process-isolated control plane + PromptGuard 2 | LLM proposes, runtime decides; formal orchestrator/subagent split with taint-safe handoffs |
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
| 3.5 Model Hardening | None | None | None | Partial | Minimal | None |
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
| **shisad** | Three-tier context scaffold; metadata-only control plane in process-isolated sidecar (Unix socket + peer credential auth); formal COMMAND/TASK orchestrator/subagent split with immutable task envelopes; structured ArtifactLedger with endorsement tracking and metadata MAC; mandatory summary-firewall checkpoint at TASK→COMMAND boundary; taint-sink enforcement; approval provenance binding; Tool Dependency Graph verification | Taint at content-block level, not variable level |
| **openclaw** | Gateway / sandbox separation; plugin SDK import boundaries; per-session isolation | In-process plugin execution; logical not process-level session isolation |
| **hermes-agent** | Code sandbox with stripped env and RPC; subagent isolation with restricted toolsets | No formal architectural model; shared process space for tool system |

**Assessment:** shisad v0.6.1 implements the CaMeL-inspired dual-agent architecture as a first-class runtime concept with process-isolated enforcement: `SessionRole` enum (ORCHESTRATOR/SUBAGENT) is immutable at session creation, task envelopes carry frozen capability snapshots and credential refs, TASK→COMMAND handoffs must pass a mandatory summary-firewall checkpoint, the structured ArtifactLedger tracks artifact lifecycle and endorsement state with HMAC-bound metadata, and the control plane now runs in a separate OS process (Unix socket sidecar with UID+PID peer credential authorization). v0.6.1 also adds Tool Dependency Graph verification -- actions must trace back to committed user intent through dependency paths. openfang's taint tracking is the most formally structured (lattice-based with typed sinks) but its integration into the actual execution flow is unclear. No framework achieves variable-level provenance tracking.

#### 3.2 Access Control and Governance

*The gold standard: Progent-style least-privilege DSL with automated policy generation.*

| Framework | Capability System | Policy Language | Tool-Level Control | MCP/A2A Control | Approval Flow |
|-----------|------------------|-----------------|--------------------|-----------------|---------------|
| **agentsh** | Process-level (file/net/cmd/env/signal rules) | YAML DSL with globs, regex, variable expansion | Command + args pattern matching; first-match-wins | Tool whitelisting, version pinning, rate limits | TTY, TOTP, WebAuthn, REST API |
| **openfang** | 22-variant typed `Capability` enum with globs | TOML config + `ToolPolicy` struct | Deny-wins glob rules; group expansion; depth restrictions | MCP server config | Per-agent approval manager |
| **ironclaw** | WASM capability flags (HTTP, workspace, tools, secrets) | JSON sidecar `.capabilities.json` | Autonomous tool denylist (17 tools) | MCP client | Tool approval mechanism |
| **shisad** | Session capability set (10 capabilities) + task-envelope credential scoping + Tool Dependency Graph (TDG) resource grounding | YAML with Pydantic validation + hot reload + typed semantic atom validation | Per-tool allowlist + schema validation + argument DLP + resource-scope enforcement + TDG dependency path verification | Not implemented (v0.6.3 planned) | Nonce-based confirmation + PEP re-evaluation + approval provenance binding + capability elevation |
| **openclaw** | 5-level operator RBAC | Config + tool profiles | Allow/deny lists; owner-only tools; safe bins | Not implemented | Interactive UUID-based; single-use; time-limited |
| **hermes-agent** | Toolset enable/disable | Config YAML | Blocked toolsets; sandbox tool allowlist (7 tools) | Not implemented | 3 modes: manual, smart (LLM), off |

**Assessment:** agentsh and openfang have the most granular permission models. agentsh's policy language is the most expressive (YAML DSL with variable expansion, regex args matching, redirect decisions, and Ed25519-signed policies). openfang's typed capability enum with inheritance validation is the most formally rigorous. shisad v0.6.0 adds typed semantic atom validation (rejecting prose-bearing URLs, whitespace-bearing command tokens, and instructional content in structured fields) and task-envelope credential scoping (tool grants do not implicitly grant credentials; TASK sessions cannot use send-capable credentials). Its most-restrictive-wins policy merge remains a novel contribution. MCP-specific access control is only implemented by agentsh (and notably well -- tool whitelisting, version pinning, rug-pull detection, cross-server exfiltration analysis).

#### 3.3 Runtime Verification and Policy Enforcement

*The gold standard: AgentArmor-style trace analysis with CFG/DFG/PDG over execution traces.*

| Framework | Pre-Execution Check | During-Execution Enforcement | Behavioral Analysis | Loop/Drift Detection | Graduated Response |
|-----------|--------------------|-----------------------------|---------------------|---------------------|-------------------|
| **agentsh** | Command policy eval | FUSE + seccomp + ptrace + Landlock + eBPF | MCP cross-server exfiltration patterns | Not explicit | Allow/deny/approve/redirect |
| **openfang** | Capability + tool policy + approval | WASM fuel + epoch metering | Phantom action detection (hallucinated tool use) | Loop guard with circuit breaker; ping-pong detection | Allow -> Warn -> Block -> CircuitBreak |
| **ironclaw** | Sanitizer + validator + policy | WASM fuel + memory limits + timeout | Not implemented | Not implemented | Block/Warn/Review/Sanitize |
| **shisad** | PEP 8-check pipeline + control-plane consensus + typed semantic validation + Tool Dependency Graph (TDG) verification | Sandbox with network isolation + browser element-binding hash verification | 5 behavioral sequence patterns; plan commitment verification; TASK close-gate self-check; phantom action detection (3 deny rules) | Rate limiting; lockdown escalation; tool-schema-hash drift detection (with audit events); TDG plan stage transitions | Auto-approve -> Confirm -> Deny -> Lockdown (4 levels) + approval provenance binding (session/nonce/timestamp) + capability elevation |
| **openclaw** | Tool policy + ACP approval classifier | Docker sandbox validation | Not implemented | Not implemented | Auto-approve/ask/deny; allow-once/always |
| **hermes-agent** | Dangerous command patterns + tirith scanner | Container isolation (when used) | Not implemented | Read-loop detection | Manual/smart/off approval |

**Assessment:** shisad v0.6.1 has the most sophisticated runtime verification with its 5-voter consensus system, behavioral sequence analysis, 4-level lockdown escalation, approval provenance binding, and new Tool Dependency Graph verification (actions must trace to committed user intent through dependency paths; ungrounded reads → confirmation, ungrounded writes → block). v0.6.1 also adds phantom action detection (repeated denied actions trigger structured audit events for operator alerting). agentsh has the deepest kernel-level enforcement with 5 independent OS-level interception points. openfang's loop guard with ping-pong pattern detection and circuit breaker is a pragmatic feature other frameworks lack. No framework implements the trace-level program analysis (CFG/DFG/PDG) seen in AgentArmor or the causal independence testing of MELON, though shisad's TDG verification is the closest production approximation of structured plan verification.

#### 3.4 Detection, Filtering, and Firewalls

*The gold standard: LlamaFirewall's modular policy engine or MELON's causal independence detection.*

| Framework | Injection Detection | Secret/PII Detection | Network Filtering | Supply Chain | Encoding Evasion Handling |
|-----------|--------------------|--------------------|------------------|-------------|--------------------------|
| **agentsh** | MCP suspicious pattern scanning | DLP regex (email, phone, CC, SSN, API keys) | eBPF + threat feed integration | Package install checking | Not documented |
| **openfang** | 10 keyword patterns + 9 exfil patterns + 3 shell patterns | Secret zeroization; env stripping | SSRF (multi-layer IP blocking + DNS rebinding defense) | Ed25519 manifest signing + SHA256 skill checksums | Shell bleed detection |
| **ironclaw** | 18+ Aho-Corasick literals + 4 regex patterns | 16 API key patterns + credential detection | SSRF + endpoint allowlisting | cargo-deny; Ed25519 webhooks | Unicode bypass vectors documented but unfixed |
| **shisad** | Pattern + YARA (13 rule files) + **PromptGuard 2 ML classifier** (local ONNX, signed model-packs) + multi-layer base64 decoding + browser DOM-drift detection | Secret detection + PII redaction + argument DLP + terminal control-sequence sanitization | Egress allowlisting with provenance-aware routing + browser domain scope enforcement | Ed25519 skill signatures + dependency chain verification + multi-engine analysis + tool-schema-hash inventory (with audit events) + OIDC trusted publishing + SBOM + build attestations + pip-audit + pinned CI actions + signed PromptGuard model-packs | Recursive encoding unwrapping (2 layers) |
| **openclaw** | External content wrapping with injection pattern logging | detect-secrets CI (433KB baseline) | SSRF with DNS rebinding defense | Skill scanner | Exec obfuscation detection (base64, hex, Unicode) |
| **hermes-agent** | Cron prompt injection scanning only | 20+ API key prefix patterns + PII redaction | SSRF (browser tool only) | CI supply chain audit + tirith binary verification | ANSI stripping + Unicode NFKC normalization |

**Assessment:** shisad v0.6.1's content firewall is now the most comprehensive with YARA rules covering 13 attack categories, PromptGuard 2 ML classifier (local ONNX inference with signed model-packs), recursive encoding detection, terminal control-sequence sanitization (ANSI CSI, OSC, DCS/APC/PM/SOS, stray ESC, C0/C1), and browser-surface DOM-drift detection via element-binding hashes. The ML classifier operates alongside pattern + YARA via `max()` score merging -- it can only escalate, never suppress pattern findings. Three postures (off/best_effort/required) allow operators to control the failure mode. Its supply chain hardening remains the most thorough: OIDC trusted publishing, SBOM generation, build provenance attestations, pip-audit with hash verification, pinned CI actions (immutable SHAs), dependency-review gates, zizmor workflow linting, lockfile drift guards, adapter runtime lockdown, tool-schema-hash inventory (now with structured audit events on drift), and signed PromptGuard model-packs. agentsh's MCP-specific detection (cross-server exfiltration, rug-pull, shadow tool replacement) addresses threats no other framework detects. ironclaw's adversarial testing methodology -- explicitly documenting known bypass vectors -- is exemplary. shisad is now the first open-source agent framework to deploy an ML-based injection classifier. The gap between these systems and LlamaFirewall (production at Meta) has narrowed significantly -- same underlying PromptGuard 2 model, now available in the open-source landscape.

#### 3.5 Model-Level Hardening

*The gold standard: SecAlign/Meta SecAlign preference optimization or instruction hierarchy.*

**No framework implements model-level hardening in the SecAlign sense** (preference optimization or instruction hierarchy). All six are model-agnostic and explicitly treat the LLM as an untrusted component. shisad v0.6.1 now deploys PromptGuard 2 as a content-seeing detection layer -- while this is not model-level hardening (it doesn't change the model's behavior), it provides ML-based input classification that screens untrusted content before it reaches the LLM context, reducing exposure to injection payloads. openclaw recommends "strongest latest-generation models" to reduce injection risk.

This is the correct design choice for multi-provider frameworks, but it means that instruction hierarchy and preference optimization -- which research shows provide meaningful (if insufficient) baseline resistance -- are entirely absent from the production stack. PromptGuard 2 as an input filter is the closest any open-source framework comes to ML-based defense.

#### 3.6 Boundary Marking and Cryptographic Provenance

*The gold standard: Signed-Prompt or Encrypted Prompt with cryptographic permission tokens.*

| Framework | Prompt Boundary Marking | Audit Integrity | Policy Integrity | Credential Protection |
|-----------|------------------------|-----------------|-----------------|----------------------|
| **agentsh** | None | HMAC chain + external KMS (AWS/Azure/GCP/Vault) | Ed25519 policy signatures | DLP redaction in LLM proxy |
| **openfang** | None | Merkle SHA-256 hash chain | Ed25519 manifest signing | AES-256-GCM vault + Argon2 KDF + zeroization |
| **ironclaw** | XML boundary wrapping + delimiter escape | None | Ed25519 webhook verification | AES-256-GCM + HKDF-SHA256 per-secret keys + OS keychain |
| **shisad** | Random cryptographic delimiters + datamarking + three-tier placement + mandatory TASK→COMMAND summary-firewall checkpoint + process-isolated control plane (Unix socket + peer cred auth) | Append-only audit log + ArtifactLedger with HMAC-bound metadata MAC + approval provenance (session/nonce/timestamp) + phantom action audit events | SHA256 policy integrity + SIGHUP-only reload + tool-schema-hash inventory (with drift audit events) + OIDC trusted publishing + SBOM + build attestations + signed PromptGuard model-packs | Credential broker with placeholders + proxy-level injection + task-envelope-scoped credential refs |
| **openclaw** | Randomized XML boundary markers with security notices | None | None | Environment variable sanitization in sandbox |
| **hermes-agent** | None | None | None | Env var filtering in code sandbox |

**Assessment:** shisad v0.6.1's approach is the most comprehensive -- cryptographically random delimiters, character-level datamarking, three-tier context placement, provenance annotations, mandatory summary-firewall checkpoint at the TASK→COMMAND boundary, and now process-isolated control plane (Unix socket sidecar with peer credential authorization). The structured ArtifactLedger with HMAC-bound metadata MAC provides tamper detection for persisted evidence refs. v0.6.1 adds signed PromptGuard model-packs (Ed25519 manifests + SHA256 file hashes) extending supply chain integrity to ML artifacts. agentsh has the strongest audit integrity (HMAC chains with external KMS from four major cloud providers). For credential protection, ironclaw's zero-exposure model (WASM tools never see secrets, injection at host boundary, leak detection at both request and response boundaries) and shisad's credential broker (placeholder substitution at egress proxy only, with per-task-envelope credential scoping) are the strongest implementations. No framework implements the Signed-Prompt or Encrypted Prompt patterns from the academic literature.

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
  │ PEP; COMMAND/ │        │ checks before │            │ + ptrace +    │
  │ TASK split;   │        │ tool dispatch;│            │ Landlock +    │
  │ ArtifactLedger│        │ WASM sandbox; │            │ eBPF          │
  │ consensus     │        │ taint sinks   │            │               │
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
| **shisad** | First production COMMAND/TASK dual-agent architecture with immutable task envelopes and process-isolated control plane; taint-sink endorsement separation (USER_REVIEWED != TRUSTED); ArtifactLedger with endorsement lifecycle + metadata MAC; approval provenance binding (non-portable across task/session boundaries); typed semantic atom validation; browser element-binding hash verification; OIDC trusted publishing with SBOM + attestations; **first ML-based injection classifier** (PromptGuard 2, local ONNX, signed model-packs) in open-source agent framework; **Tool Dependency Graph verification** (actions must trace to committed intent); **phantom action detection** (structured alerts on probing patterns) | Closest production implementation of CaMeL-inspired privilege separation; user approval doesn't upgrade trust; task envelopes carry frozen credentials/capabilities that cannot be widened; approval replay attacks blocked; supply chain is auditable from source to PyPI; ML classifier merges with pattern+YARA via max(); TDG blocks injected actions even when they pass other checks |
| **openclaw** | TLA+ formal models; `openclaw security audit --deep` CLI; `dangerously*` flag convention | Unusual formal verification for application code; proactive security configuration auditing |
| **hermes-agent** | Tirith external scanner with cosign provenance; smart (LLM) approval; supply chain CI audit | Binary integrity verification; LLM-assisted risk assessment; automated dependency attack detection |

---

## Security Posture Spectrum

### Strongest Per Category

| Category | Best Framework | Runner-up | Notes |
|----------|---------------|-----------|-------|
| **Overall architecture** | shisad | openfang | shisad's COMMAND/TASK split + metadata-only PEP is the closest production system to CaMeL |
| **Access control granularity** | agentsh | shisad | agentsh's YAML DSL; shisad's typed semantic validation + task-envelope credential scoping |
| **Runtime enforcement depth** | agentsh | shisad | agentsh has 5 kernel-level points; shisad has 10 defense layers + browser element binding |
| **Detection sophistication** | shisad | agentsh | shisad's YARA + encoding + DOM-drift detection; agentsh's MCP analysis |
| **Credential protection** | shisad | ironclaw | shisad's per-task-envelope credential scoping + proxy injection; ironclaw's zero-exposure WASM model |
| **Supply chain hardening** | shisad | hermes-agent | shisad's OIDC publishing + SBOM + attestations + pip-audit + pinned actions; hermes-agent's tirith + cosign |
| **Audit integrity** | agentsh | shisad | agentsh's HMAC chain + external KMS; shisad's ArtifactLedger with metadata MAC + approval provenance |
| **Test discipline** | ironclaw | shisad | ironclaw's adversarial tests + fuzz; shisad's 84 adversarial + 1,368 total test functions |
| **Formal rigor** | openclaw (!) | openfang | TLA+ models for highest-risk paths |

### Production Readiness Ranking

| Rank | Framework | Maturity Indicators |
|------|-----------|-------------------|
| 1 | **openclaw** | Daily calver releases; 3,313 tests; 70% coverage thresholds; macOS signing; npm/Docker distribution; dedicated Security & Trust lead; bug bounty |
| 2 | **agentsh** | 240K lines; cross-platform (Linux/macOS/Windows); GoReleaser packaging; CI on 3 platforms; 493 test files |
| 3 | **openfang** | 177K Rust; 1,767+ tests; single ~32MB binary; Docker + Tauri desktop |
| 4 | **hermes-agent** | v0.6.0; 100+ test files; 14+ platform adapters; Docker + Nix; production gateway |
| 5 | **ironclaw** | v0.22.0; fuzz targets + benchmarks; 7 build targets; systemd/launchd support |
| 6 | **shisad** | v0.6.1; 114K lines (src+tests+scripts); 1,522 test functions (86 adversarial, 70 behavioral); OIDC trusted publishing + SBOM + attestations; process-isolated control plane; PromptGuard 2; Unix socket daemon; multi-channel; 7 CI jobs |

---

## The Gap Between Production and Academic State-of-the-Art

### What Production Systems Have That Academia Doesn't

1. **Real tool ecosystems.** Academic systems test against AgentDojo's 4 domains or toy environments. Production frameworks manage 40+ messaging platforms, 50+ tools, MCP servers, file systems, browsers, and shell access. The attack surface is orders of magnitude larger.

2. **Operational recovery.** Academic papers measure ASR and utility. Production systems implement lockdown escalation (shisad), checkpoint/rollback (agentsh), session repair (openfang), and graduated response ladders. The question isn't just "did the attack succeed?" but "can the system recover?"

3. **Supply chain defenses.** Academic work focuses on prompt injection. Production frameworks defend against poisoned skills (openfang, ironclaw, shisad), tampered tool definitions (agentsh MCP version pinning, shisad tool-schema-hash inventory), malicious dependencies (hermes-agent CI audit, shisad pip-audit + dependency-review gates), and corrupted agent manifests (openfang Ed25519 signing). shisad v0.6.0's end-to-end supply chain is the most comprehensive: OIDC trusted publishing eliminates long-lived credentials, SBOM + build attestations provide tamper-evident provenance, pinned CI actions (immutable SHAs) prevent upstream workflow poisoning, and runtime adapter lockdown prevents dynamic fetches.

4. **Credential protection infrastructure.** No academic paper we surveyed addresses the practical problem of keeping API keys and secrets away from the LLM. Three production frameworks (ironclaw, shisad, agentsh) implement proxy-level credential injection where the LLM never sees raw secrets.

5. **Cross-platform enforcement.** agentsh implements full enforcement stacks for Linux (5 layers), macOS (4 layers), and Windows (4 layers). Academic prototypes are single-platform.

### What Academia Has That Production Doesn't

1. **Variable-level provenance tracking.** CaMeL tracks data provenance through the computation graph at the variable level. shisad v0.6.1's COMMAND/TASK split with ArtifactLedger and TDG verification is the closest production implementation of CaMeL-inspired architecture, but still tracks at the content-block level, not per-variable. openfang tracks at the value level but remains underintegrated with its execution loop.

2. **Formal non-interference guarantees.** Fides and LLMbda Calculus prove that untrusted data cannot influence trusted decisions. No production system has formal proofs.

3. **Causal independence detection.** MELON's dual-execution approach (testing whether an action would occur regardless of user intent) is not implemented in any production framework.

4. **ML-based prompt injection classification at scale.** LlamaFirewall's PromptGuard 2 is deployed at Meta's production scale. shisad v0.6.1 now includes the same PromptGuard 2 model as a local ONNX classifier with signed model-packs -- the first open-source agent framework to deploy an ML-based injection classifier. The gap here has narrowed from "not present" to "present but single-model."

5. **Structured plan verification.** CaMeL generates restricted Python plans that can be statically analyzed. AgentArmor applies CFG/DFG/PDG analysis to execution traces. shisad v0.6.1's TDG verification is the closest production approximation -- it verifies that actions trace to committed intent through dependency paths with dynamic reachability tracking -- but does not construct full CFG/DFG/PDG or require the model to generate restricted programs.

---

## Cross-Cutting Observations

### The Taint Tracking Gap

Three frameworks implement taint tracking (openfang, shisad, and partially ironclaw via boundary wrapping), but none fully achieves the CaMeL standard:

| Framework | Taint Granularity | Taint Propagation | Taint Enforcement | Formal Basis |
|-----------|-------------------|-------------------|-------------------|-------------|
| CaMeL (reference) | Variable-level | Through computation graph | Capability tokens gate tool access | IFC with proofs |
| openfang | Value-level (5 labels) | Union semantics | Predefined sinks block specific labels | Lattice-inspired; no proof |
| shisad (v0.6.1) | Content-block-level (6 labels) | Worst-case union + TASK→COMMAND mandatory firewall checkpoint + TDG dependency path verification | PEP taint-sink rules; ArtifactLedger endorsement lifecycle; approval provenance binding; credential scoping per task envelope; TDG blocks ungrounded actions; PromptGuard 2 ML screening at ingress | IFC-inspired; COMMAND/TASK architectural separation with process-isolated control plane; no formal proof |
| ironclaw | Content-level | Not propagated; boundary-marked | Policy rules per severity | None |

The gap has narrowed further: shisad v0.6.1's COMMAND/TASK separation enforces an architectural boundary where tainted content from TASK agents must pass through a mandatory summary-firewall checkpoint before reaching the orchestrator's context, with the control plane now in a separate OS process. The ArtifactLedger tracks endorsement state separately from taint (USER_ENDORSED does not strip UNTRUSTED taint), approval provenance is bound to specific task/session boundaries (preventing replay), and the new TDG verifier ensures actions trace to committed user intent through dependency paths. v0.6.1 also adds PromptGuard 2 ML screening at the content ingress boundary, providing neural-classifier detection alongside pattern + YARA rules. However, academic IFC still tracks provenance through the computation graph at the variable level, which production systems cannot match -- they label content blocks, not individual values within structured returns.

### The MCP Security Gap

MCP (Model Context Protocol) is rapidly becoming the standard for agent-tool integration, but only **agentsh** implements MCP-specific security (tool whitelisting, version pinning, rug-pull detection, cross-server exfiltration analysis, rate limiting, suspicious pattern scanning). This is a significant gap -- MCP servers are a growing attack surface (6,000+ in PulseMCP), and the academic AgentBound paper identifies the need for Android-style MCP permissions.

### The Approval Fatigue Problem

Five of six frameworks implement human-in-the-loop approval for risky actions. All face the same problem: approval fatigue. shisad v0.6.1 addresses this most systematically with graduated response (auto-approve for low-risk, confirm for medium, deny for high, lockdown for anomalies), rate-limiting that triggers confirmation as limits approach, approval provenance binding (approvals are non-portable across task/session boundaries), TDG verification (reduces unnecessary confirmations by grounding actions against the user's stated goal and declared resource roots), and capability elevation (per-action capability grants avoid all-or-nothing confirmation). The browser tool surface adds source/destination URL binding and element-binding hash verification so that even within a single confirmation flow, DOM drift between approval and execution fails closed. agentsh's SECURITY.md acknowledges the fatigue attack vector. This remains an unsolved UX problem that directly impacts security effectiveness.

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

1. **Integrate taint tracking into the agent loop, not just the type system.** openfang's lattice-based taint types exist but need to be actively checked at every data flow boundary in the agent execution cycle. shisad v0.6.0's COMMAND/TASK split with mandatory summary-firewall checkpoints is the current best example of taint-aware architectural enforcement.

2. **Implement MCP security controls.** agentsh's approach (tool whitelisting, version pinning, cross-server exfiltration detection) should be considered table stakes as MCP adoption grows. shisad plans MCP/A2A access control for v0.6.3.

3. **Move toward variable-level provenance.** Content-block taint tracking is useful but can't detect multi-step derivation attacks. CaMeL's approach of tracking provenance through the computation graph is the research direction most worth pursuing for production. shisad's ArtifactLedger with endorsement lifecycle and TDG verification are steps in this direction but still operate at the block level, not per-variable.

4. **Add ML-based injection classification.** Pattern matching has a ceiling. Even a simple fine-tuned classifier would significantly improve detection of obfuscated injection attempts. shisad v0.6.1 now deploys PromptGuard 2 as a local ONNX classifier with signed model-packs -- other frameworks should consider similar integration.

5. **Harden the supply chain end-to-end, including ML artifacts.** shisad v0.6.1 extends the standard set in v0.6.0 (OIDC trusted publishing, SBOM, build attestations, pip-audit, pinned CI actions, adapter runtime lockdown) with signed model-packs for PromptGuard artifacts. Other frameworks should adopt comparable measures, especially as real-world supply chain attacks against AI tooling escalate (LiteLLM compromise, ClawdHub skill poisoning). ML model supply chains are an emerging attack surface that most frameworks have not yet addressed.

6. **Consider a composable defense architecture.** The ideal system would layer agentsh-style execution enforcement, openfang/shisad-style policy enforcement, shisad-style intent analysis with COMMAND/TASK separation, and ML-based detection (PromptGuard 2 or similar). No single framework needs to build all layers -- well-defined interfaces between layers would allow composition.

### For Practitioners Choosing a Framework

| If you need... | Consider |
|----------------|----------|
| Maximum execution-layer enforcement | **agentsh** -- deepest OS-level interposition on Linux; works with any agent framework |
| Comprehensive security architecture | **shisad** -- most complete defense-in-depth with COMMAND/TASK separation, process-isolated control plane, PromptGuard 2 ML classifier, TDG verification, 10+ defense layers, and end-to-end supply chain |
| Strongest credential protection | **shisad** -- per-task-envelope credential scoping + proxy injection; or **ironclaw** -- zero-exposure WASM model |
| Production maturity with security | **openclaw** -- most mature release process with substantial security infrastructure |
| Privacy-focused local operation | **ironclaw** -- data sovereignty design with encrypted storage |
| MCP security | **agentsh** -- only framework with comprehensive MCP security controls |
| Supply chain hardening | **shisad** -- OIDC trusted publishing, SBOM, attestations, pip-audit, pinned CI actions, adapter lockdown, signed ML model-packs |

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
| shisad (v0.5) | [ANALYSIS-shisad-v0.5.md](ANALYSIS-shisad-v0.5.md) | 420 | Metadata-only PEP is structurally injection-proof; endorsement/taint separation novel |
| shisad (v0.6.1) | [ANALYSIS-shisad-v0.6.md](ANALYSIS-shisad-v0.6.md) | ~600 | COMMAND/TASK first-class; process-isolated control plane; PromptGuard 2 ML classifier; TDG verification; phantom action detection; supply chain hardened |
| openclaw | [ANALYSIS-openclaw.md](ANALYSIS-openclaw.md) | 349 | Surprisingly security-mature for baseline; TLA+ formal verification; security audit CLI |
| hermes-agent | [ANALYSIS-hermes-agent.md](ANALYSIS-hermes-agent.md) | 366 | Strong baseline with supply chain CI, DM pairing (OWASP/NIST), tirith scanner |

---

## Methodology

Each framework was analyzed at a specific git commit (point-in-time) by reading documentation AND source code. Analysis followed a consistent structure mapped to the 7-category defense taxonomy from ANALYSIS.md (79 academic papers). Security-focused and baseline frameworks were analyzed with the same structure to enable direct comparison. Individual analyses were performed by independent research agents in parallel, then synthesized into this comparison.

**Update 2026-04-04:** shisad entries updated to reflect v0.6.0 (released 2026-04-03). Changes based on source code review of shisad repo (58 commits since v0.5 analysis) and development planning/review records from shisad-dev. Other frameworks not re-analyzed -- their entries remain at the 2026-03-31 point-in-time.

**Update 2026-04-06:** shisad entries updated to reflect v0.6.1 (released 2026-04-05). Changes based on source code review of shisad repo (29 commits since v0.6.0, 92 files changed, 8,805 insertions). Key additions: control-plane process isolation via Unix socket sidecar, PromptGuard 2 ML injection classifier with signed model-packs, Tool Dependency Graph verification, phantom action detection, and skill drift observability. Other frameworks not re-analyzed.
