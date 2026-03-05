Yes. I grouped your seed list, filled in a few missing anchors, and the picture is pretty clear now:

**The center of gravity has moved away from “detect bad prompts” and toward “make it impossible for untrusted text to directly exercise privilege.”** The most important papers are the ones that separate trusted intent from untrusted data, enforce least privilege outside the model, and treat tools, memory, MCP servers, and inter-agent communication as control-plane problems rather than prompt-engineering problems. ([arXiv][1])

## The literature map

### 1) Threat model and benchmark papers

This starts with the foundational indirect prompt-injection papers showing that once an LLM consumes retrieved content, the line between **data** and **instructions** collapses. From there the benchmark line evolves through BIPIA, InjecAgent, AgentDojo, ASB, and then AgentDyn, which is important because it argues many earlier defenses look good partly because the benchmarks were too static or too weak. In parallel, the threat model expands beyond text-only prompt injection into **memory poisoning**, **function/tool supply-chain poisoning**, and **visual prompt injection** against computer-use agents. ([arXiv][2])

### 2) Architecture-by-construction papers

This is the highest-signal cluster for secure design. **IsolateGPT** is the early execution-isolation blueprint. **AirGapAgent** pushes a privacy-first/data-minimization design grounded in contextual integrity. **CaMeL** is the standout paper from your list: it explicitly separates control flow from data flow and uses capabilities to restrict exfiltration and tool use. **PFI** reframes the problem as privilege escalation and adds isolation plus guardrails. **Progent** turns least privilege into a deterministic tool-policy system. **Better Privilege Separation by Restricting Data Types** takes the strongest systems-security position of all: don’t let privileged models consume raw untrusted strings when a typed extract will do. ([arXiv][3])

A good fast on-ramp into this cluster is Simon Willison’s CaMeL write-up, because it explains why “dual-LLM isolation” alone is not enough unless the privileged side also has an explicit capability and data-flow story. ([Simon Willison’s Weblog][4])

### 3) Control planes, governance, MCP, and computer-use security

For the “secure architecture / control plane” part of your question, this is the bucket to prioritize. **SAGA** proposes a provider-mediated governance layer with identity, policy, and cryptographic tokens for inter-agent communication. **AgentBound** is the clearest MCP-security/control-plane paper: it adds declarative permissions and a policy enforcement engine around MCP servers. **CSAgent** pushes authorization into an OS-level service for computer-use agents and makes it context-aware. **SEAgent** brings MAC/ABAC-style information-flow enforcement to agent-tool interactions. **MCP-Guard** is worth reading too, but it is more of a layered protocol-edge detector than a true authorization/control plane. ([arXiv][5])

### 4) Runtime verification and policy-enforcement systems

These papers monitor or verify execution as the agent runs. **Task Shield** checks whether each action still serves the user’s task. **AgentArmor** treats runtime traces as structured programs and applies CFG/DFG/PDG-style analysis. **IPIGuard** constrains execution through a preplanned tool-dependency graph. **ShieldAgent**, **AgentSpec**, **DRIFT**, **VIGIL**, and **ToolSafe** are all variations on the same theme: dynamic validation, verify-before-commit, or explicit policy reasoning around tool calls and action trajectories. This line is promising, but I would still treat it as an inner guard layer, not the root of trust. ([arXiv][6])

### 5) Model-level hardening

This category is much stronger in 2025–2026 than it was in early 2024. **StruQ** introduces explicit instruction/data channels. **SecAlign** uses preference optimization so the model learns to prefer the legitimate instruction over the injected one. **Meta SecAlign** turns that into an open secure foundation model with a broad security/utility evaluation. **DRIP** goes after the representation itself, editing instruction-like semantics out of data tokens while reinforcing the intended instruction. These are especially compelling when you control the model stack, but adaptive-attack papers are a reminder not to mistake model hardening for complete system security. ([arXiv][7])

### 6) Detection, sanitization, and firewalls

This is the most deployable defense-in-depth layer. **PromptShield** is a useful deployable-detector paper because it explicitly optimizes for low false positive rates. **Tool Result Parsing**, **DataFilter**, and **CommandSans** all try to sanitize or transform untrusted tool outputs before the privileged model consumes them. **LlamaFirewall** packages several practical guardrails into an open-source stack. There is also a strong “firewall” line now: a tool-input minimizer plus tool-output sanitizer can perform extremely well on current public benchmarks. The catch is that recent meta-evaluation work shows benchmark saturation is not the same thing as robustness under stronger tasks or adaptive attackers. ([arXiv][8])

### 7) Boundary-marking / provenance ideas

Your seed list also contains a smaller family of “authenticated boundary” papers: **Signed-Prompt**, **FATH**, **Encrypted Prompt**, and **Prompt Fencing**. I think these are intellectually interesting because they try to give the model a cryptographic or authenticated notion of trusted vs. untrusted text. But today they feel less fundamental than capability systems and external policy engines, because the model still has to semantically honor the boundary marker; even Prompt Fencing explicitly notes that current models are not natively fence-aware. ([arXiv][9])

## The papers I would read first

If the goal is **defense in depth + secure architecture design**, my reading order would be:

1. **Not what you’ve signed up for** — foundational indirect prompt injection. ([arXiv][2])
2. **AgentDojo** — baseline benchmark vocabulary for the whole field. ([arXiv][10])
3. **ASB** — broad benchmark including memory/tool/backdoor perspectives. ([arXiv][11])
4. **IsolateGPT** — execution isolation as the base systems idea. ([arXiv][3])
5. **AirGapAgent** — privacy-conscious data minimization. ([arXiv][12])
6. **CaMeL** — strongest “by design” secure execution paper in the set. ([arXiv][1])
7. **PFI** — privilege-escalation framing for LLM agents. ([arXiv][13])
8. **Progent** — deterministic least-privilege tool control. ([arXiv][14])
9. **SAGA + AgentBound + CSAgent + SEAgent** — the control-plane/governance line. ([arXiv][5])
10. **StruQ + SecAlign + Meta SecAlign** — the model-hardening line. ([arXiv][7])
11. **AgentDyn + The Attacker Moves Second** — reality check on benchmark quality and adaptive attacks. ([arXiv][15])

## What this means for a secure agent architecture

My synthesis from the strongest papers is that a production-grade secure agent should look like this:

* **Separate intent from observations.** The privileged planner should reason over the user’s goal and typed summaries, not raw untrusted web/email/tool output.
* **Convert untrusted content into typed data early.** Treat raw strings as toxic until parsed, minimized, or sanitized.
* **Put authorization in a control plane, not in prompts.** Tool calls, MCP actions, file/network access, and inter-agent delegation should go through explicit policy enforcement.
* **Use least privilege with provenance.** Every datum and every action should carry trust/provenance and be checked against policy.
* **Split memory into trust zones.** Ephemeral task memory, long-term memory, and imported knowledge should not share a flat trust domain.
* **Sandbox tools and MCP servers.** Deny by default; grant scoped credentials and bounded capabilities.
* **Keep dynamic guardrails as a second line, not the first.** Verify-before-commit, sanitizers, and detectors are valuable, but they should sit on top of isolation and access control. ([arXiv][3])

## Where research still looks thin

The biggest gaps are: **persistent memory poisoning**, **tool/function-library supply chain attacks**, **visual/rendered prompt injection in computer-use agents**, and **evaluation under strong adaptive attacks**. The field is improving quickly, but AgentDyn and “The Attacker Moves Second” are both warning signs that many current claims still do not survive stronger threat models. ([arXiv][16])

I also put the paper map into a workbook and CSV:

* [AI agent security paper map (.xlsx)](sandbox:/mnt/data/ai_agent_security_paper_map.xlsx)
* [AI agent security paper matrix (.csv)](sandbox:/mnt/data/ai_agent_security_paper_matrix.csv)

Next useful step: either collapse this into a **10-paper reading plan by week**, or turn it into a **reference secure-agent architecture memo** with concrete design choices for data isolation, MCP control planes, memory zoning, and approval boundaries.

[1]: https://arxiv.org/abs/2503.18813 "https://arxiv.org/abs/2503.18813"
[2]: https://arxiv.org/abs/2302.12173 "https://arxiv.org/abs/2302.12173"
[3]: https://arxiv.org/abs/2403.04960 "https://arxiv.org/abs/2403.04960"
[4]: https://simonwillison.net/2025/Apr/11/camel/ "https://simonwillison.net/2025/Apr/11/camel/"
[5]: https://arxiv.org/abs/2504.21034 "https://arxiv.org/abs/2504.21034"
[6]: https://arxiv.org/abs/2412.16682 "https://arxiv.org/abs/2412.16682"
[7]: https://arxiv.org/abs/2402.06363 "https://arxiv.org/abs/2402.06363"
[8]: https://arxiv.org/abs/2501.15145 "https://arxiv.org/abs/2501.15145"
[9]: https://arxiv.org/abs/2401.07612 "https://arxiv.org/abs/2401.07612"
[10]: https://arxiv.org/abs/2406.13352 "https://arxiv.org/abs/2406.13352"
[11]: https://arxiv.org/abs/2410.02644 "https://arxiv.org/abs/2410.02644"
[12]: https://arxiv.org/abs/2405.05175 "https://arxiv.org/abs/2405.05175"
[13]: https://arxiv.org/abs/2503.15547 "https://arxiv.org/abs/2503.15547"
[14]: https://arxiv.org/abs/2504.11703 "https://arxiv.org/abs/2504.11703"
[15]: https://arxiv.org/abs/2602.03117 "https://arxiv.org/abs/2602.03117"
[16]: https://arxiv.org/abs/2407.12784 "https://arxiv.org/abs/2407.12784"

