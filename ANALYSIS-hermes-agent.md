# hermes-agent Security Analysis (Baseline)

**Repository:** https://github.com/NousResearch/hermes-agent
**Commit:** 344239c2dbfe6c03c9020a4faa9552c8769be20a
**Point-in-time:** 2026-03-31
**Language:** Python
**Category:** Baseline (non-security-focused)

## 1. Overview

Hermes Agent is a self-improving AI agent framework built by Nous Research. It is a substantial, production-oriented system (the main `run_agent.py` alone is ~427KB / ~10,000+ lines) with the tagline "the agent that grows with you." It supports 200+ LLM models via multiple providers (OpenRouter, Nous Portal, OpenAI, Anthropic, z.ai/GLM, Kimi/Moonshot, MiniMax, Hugging Face, and custom OpenAI-compatible endpoints).

### Architecture

The framework consists of several major subsystems:

- **Agent Loop** (`run_agent.py`, `agent/` package): The core conversational agent with tool-calling loop, context compression, prompt caching, model metadata, and usage tracking. The `AIAgent` class manages the conversation lifecycle.

- **Tool System** (`tools/`, `model_tools.py`, `toolsets.py`): A registry-based tool system with 40+ tools organized into named toolsets. Tools self-register via `tools/registry.py`. Toolsets can be composed, enabled, or disabled per session.

- **CLI** (`cli.py`, `hermes_cli/`): A full terminal UI built on prompt_toolkit with slash-command autocomplete, session management, multiline editing, and streaming output.

- **Gateway** (`gateway/`): A multi-platform messaging bridge supporting Telegram, Discord, Slack, WhatsApp, Signal, Matrix, DingTalk, Feishu, WeCom, SMS, Email, and Home Assistant. All platforms share one gateway process.

- **Skills System** (`skills/`, `tools/skills_tool.py`): Procedural memory — the agent creates, edits, and uses markdown skill documents. Integrates with an external Skills Hub (agentskills.io).

- **Environments** (`environments/`): Terminal backends — local, Docker, SSH, Singularity, Modal (serverless), and Daytona. Also includes RL training environments for Tinker/Atropos.

- **State Management** (`hermes_state.py`): SQLite-backed session store with FTS5 full-text search, WAL mode for concurrent access, and thread-safe write retry logic.

- **ACP Adapter** (`acp_adapter/`): Agent Communication Protocol integration for editor integrations (VS Code, Zed, JetBrains).

- **Cron Scheduler** (`cron/`): Built-in cron scheduling with delivery to any connected messaging platform.

- **Code Execution Sandbox** (`tools/code_execution_tool.py`): Programmatic tool calling (PTC) — the LLM writes Python scripts that call Hermes tools via RPC over Unix domain sockets.

- **Subagent Delegation** (`tools/delegate_tool.py`): Spawns child `AIAgent` instances with isolated context, restricted toolsets, and independent terminal sessions.

## 2. Security Architecture

### 2.1 Design Philosophy

Hermes Agent is explicitly not a security-focused framework, but it has accumulated a notable number of security-conscious features organically. The README links to a [Security documentation page](https://hermes-agent.nousresearch.com/docs/user-guide/security) covering command approval, DM pairing, and container isolation — indicating that the developers are aware of the security implications of giving an AI agent system-level access.

The overall philosophy can be characterized as **defense-in-depth for a single-user personal agent**: the system assumes a trusted operator who configures what the agent can access, with guardrails to prevent accidental damage from the LLM making dangerous choices. There is no formal threat model document, but the code reveals pragmatic security thinking.

Key stated security values (from `.env.example` comments and code):
- SSH backend is explicitly described as providing "SECURITY BENEFITS" by isolating the agent from its own `.env` file and source code.
- Container backends (Docker, Singularity, Modal, Daytona) implicitly provide isolation.
- The dangerous command approval system exists explicitly to prevent destructive operations.

### 2.2 Security Primitives Present

Hermes Agent contains a surprising number of security-relevant features for a framework not marketed as security-focused:

1. **Dangerous Command Approval System** (`tools/approval.py`): A pattern-matching system that detects 30+ dangerous shell patterns (recursive delete, disk format, fork bombs, SQL DROP, etc.) and prompts for user approval. Supports session-scoped, permanent, and "smart" (LLM-assisted) approval modes.

2. **Tirith Pre-Exec Security Scanner** (`tools/tirith_security.py`): Integration with an external Rust binary for content-level threat scanning (homograph URLs, pipe-to-interpreter, terminal injection). Auto-installs with SHA-256 checksum verification and optional cosign provenance verification.

3. **Secret Redaction** (`agent/redact.py`): Regex-based redaction of API keys, tokens, credentials, private keys, database connection strings, and phone numbers from logs and tool output. Covers 20+ known API key prefixes and common credential patterns.

4. **Code Execution Sandbox** (`tools/code_execution_tool.py`): LLM-generated scripts run in a child process with a deliberately stripped environment — API keys and tokens are excluded from `child_env` by filtering environment variables containing "KEY", "TOKEN", "SECRET", "PASSWORD", "CREDENTIAL", "PASSWD", "AUTH". The sandbox communicates with the parent via Unix domain sockets, not direct API access.

5. **DM Pairing System** (`gateway/pairing.py`): Code-based user authorization for messaging platforms. Uses cryptographically random 8-character codes (via `secrets.choice()`), 1-hour expiry, rate limiting (1 request per user per 10 minutes), lockout after 5 failed attempts, and `chmod 0600` on all data files. Explicitly references OWASP and NIST SP 800-63-4 guidance.

6. **File Permission Hardening**: Config files, cron data, pairing data, and the `~/.hermes` home directory use restrictive UNIX permissions (0600 for files, 0700 for directories). Dedicated tests verify this (`tests/test_file_permissions.py`).

7. **SSRF Protection** (`tools/browser_tool.py`): Browser navigation blocks private/internal URLs by default, with both pre-navigation and post-redirect checks. Configurable via `browser.allow_private_urls`.

8. **Path Traversal Prevention**: Skill viewing (`tools/skills_tool.py`) blocks `..` traversal attempts. Worktree setup blocks parent directory traversal and symlinks resolving outside the repository root.

9. **SQL Injection Mitigation**: Parameterized queries in `hermes_state.py` and `agent/insights.py`, with dedicated tests (`tests/test_sql_injection.py`) verifying that query templates use `?` placeholders rather than string interpolation.

10. **PII Redaction in Gateway Context**: Session context prompts can hash user IDs and chat IDs using SHA-256 deterministic hashing before sending them to the LLM, configurable per platform.

11. **Supply Chain Audit CI** (`.github/workflows/supply-chain-audit.yml`): A GitHub Actions workflow that scans PRs for supply chain attack patterns — `.pth` file injection, base64+exec combos (the litellm attack pattern), obfuscated subprocess calls, and suspicious network exfiltration. Blocks PRs with critical findings.

12. **Dependency Pinning** (`pyproject.toml`): Dependencies are pinned to known-good version ranges with explicit comments about supply chain attack surface. CVE references appear in version constraints (e.g., `requests>=2.33.0,<3` noting CVE-2026-25645).

13. **ANSI Escape Stripping** (`tools/ansi_strip.py`): Terminal output is stripped of ANSI escape sequences before being returned to the model, preventing terminal injection attacks.

14. **Unicode Normalization for Command Detection**: The dangerous command detector normalizes Unicode (NFKC) and strips null bytes before pattern matching, preventing fullwidth character obfuscation bypasses.

15. **Prompt Injection Scanning for Cron**: The cron job system (`tools/cronjob_tools.py`) scans scheduled prompts for injection patterns like "ignore previous instructions."

### 2.3 Implicit Threat Model

Based on the code, Hermes Agent implicitly handles or partially handles these threats:

**Handled:**
- **LLM executing destructive commands** (approval system, dangerous pattern detection)
- **Credential leakage in logs/output** (redaction system)
- **Credential leakage to LLM-generated scripts** (sandbox env filtering)
- **Unauthorized messaging platform access** (DM pairing, user allowlists)
- **SSRF via browser tool** (private URL blocking)
- **Path traversal in file/skill operations** (traversal checks)
- **SQL injection** (parameterized queries)
- **Supply chain attacks in dependencies** (CI audit, pinned deps)
- **Terminal injection via ANSI escapes** (escape stripping)
- **Command detection bypass via Unicode obfuscation** (NFKC normalization)
- **Cron prompt injection** (prompt scanning)

**Partially handled:**
- **LLM prompt injection via untrusted content** (only cron prompts are scanned; general prompt injection from web content, file contents, or user messages is not addressed)
- **Credential storage security** (file permissions but no encryption at rest)
- **Network-level isolation** (optional via container backends, but not enforced)

**Not handled:**
- **Multi-tenant security** (designed as single-user)
- **Data exfiltration by the LLM** (no outbound network controls)
- **Formal verification of tool call correctness**
- **Cryptographic provenance of tool outputs**
- **Human-in-the-loop for all consequential actions** (only "dangerous" patterns trigger approval)

## 3. Mapping to Defense Taxonomy

### 3.1 Secure Architectures by Construction

**Partially addressed.** The architecture has several isolation boundaries:

- The code execution sandbox (`tools/code_execution_tool.py`) creates a child process with a stripped environment and communicates via RPC over Unix domain sockets. Only 7 tools are allowed in the sandbox (`SANDBOX_ALLOWED_TOOLS`). API keys are deliberately excluded from the child environment (lines 434-455).
- Subagent delegation (`tools/delegate_tool.py`) creates isolated child agents with restricted toolsets (`DELEGATE_BLOCKED_TOOLS` prevents recursive delegation, user interaction, shared memory writes, and cross-platform messaging). Depth is capped at 2 levels (`MAX_DEPTH = 2`).
- Container backends (Docker, Singularity, Modal, SSH) provide OS-level isolation. The SSH backend is explicitly documented as isolating the agent from its own `.env` file.
- Subagents cannot gain tools that the parent lacks — toolset inheritance is intersected with the parent's enabled toolsets (line 179-180 in `delegate_tool.py`).

However, the overall architecture is not designed around a formal security model. The tool system, state management, and configuration all operate in a shared process space with no capability-based access control between components.

### 3.2 Access Control and Governance

**Partially addressed.**

- **Toolset system**: Users can enable/disable toolsets via `hermes tools`, and the configuration persists in `config.yaml`. A "safe" toolset is defined that excludes terminal access. However, this is operator-configured, not policy-enforced.
- **Messaging platform access control**: The gateway supports per-platform user allowlists (`TELEGRAM_ALLOWED_USERS`, `SLACK_ALLOWED_USERS`, etc.) and a DM pairing system for dynamic user authorization. `GATEWAY_ALLOW_ALL_USERS` defaults to false.
- **Iteration budgets** (`IterationBudget` in `run_agent.py`): Thread-safe iteration counters cap the number of tool-calling turns per agent (90 for parent, 50 for subagents).
- **No RBAC or role-based permissions**: All authorized users have the same access level.

### 3.3 Runtime Verification and Policy Enforcement

**Partially addressed.**

- **Dangerous command detection** (`tools/approval.py`): 30+ regex patterns checked before every terminal command execution. Normalized with Unicode NFKC and ANSI stripping to resist obfuscation. Three approval modes: manual (default), smart (LLM-assisted), and off.
- **Tirith pre-exec scanning** (`tools/tirith_security.py`): External binary scans commands for content-level threats. Configurable fail-open/fail-closed behavior. Combined with dangerous command detection in a single guard (`check_all_command_guards`).
- **Container bypass**: Dangerous command checks are explicitly skipped for container backends (Docker, Singularity, Modal, Daytona) on the assumption that containers provide sufficient isolation (line 433-434 in `approval.py`).
- **YOLO mode**: Setting `HERMES_YOLO_MODE` bypasses all approval prompts — an explicit escape hatch.
- **Code execution limits**: The sandbox enforces a 5-minute timeout, 50KB stdout cap, and max 50 tool calls per script. Terminal parameters `background`, `check_interval`, and `pty` are stripped from sandbox terminal calls.
- **Read loop detection**: The file tools track consecutive read/search operations to detect potential infinite loops.
- **No runtime monitoring**: There is no ongoing verification that tool outputs match expected patterns, no anomaly detection, and no kill switch beyond user interrupts.

### 3.4 Detection, Filtering, and Firewalls

**Partially addressed.**

- **Secret redaction** (`agent/redact.py`): Applied to log output via `RedactingFormatter`. Covers API keys (20+ prefix patterns), environment variable assignments, JSON fields, Authorization headers, Telegram bot tokens, private key blocks, database connection strings, and phone numbers.
- **SSRF detection** (`tools/browser_tool.py`): Both pre-navigation and post-redirect checks against private/internal IP addresses.
- **Prompt injection scanning** (`tools/cronjob_tools.py`): Pattern-based detection of injection attempts in scheduled task prompts.
- **Command obfuscation detection**: ANSI stripping, null byte removal, and Unicode NFKC normalization before dangerous command pattern matching.
- **Supply chain audit in CI** (`.github/workflows/supply-chain-audit.yml`): Scans for `.pth` files, base64+exec combos, obfuscated subprocess calls, and suspicious network requests.
- **No LLM output filtering**: The framework does not filter or validate LLM responses for safety before displaying them to users or executing tool calls.

### 3.5 Model-Level Hardening

**Not addressed.** Hermes Agent is model-agnostic and delegates all model-level safety to the upstream provider. It supports 200+ models via OpenRouter and direct provider APIs. There is no model-level fine-tuning for safety, no classifier-based tool call validation, and no constitutional AI mechanisms.

The "smart approval" feature (`_smart_approve` in `approval.py`) uses an auxiliary LLM to assess command risk, but this is a heuristic check, not model-level hardening.

### 3.6 Boundary Marking and Cryptographic Provenance

**Not addressed.** There is no mechanism for marking or authenticating the boundaries between system prompts, user inputs, tool outputs, or external data. Tool results are passed to the LLM as plain text without any integrity verification. Session transcripts are stored in SQLite and JSONL without digital signatures.

The tirith auto-install system does verify binary integrity via SHA-256 checksums and optionally cosign provenance, but this applies only to the tirith binary itself, not to tool outputs or session data.

### 3.7 Formal Methods and Semantics

**Not addressed.** There are no formal specifications, contracts, or machine-verifiable properties in the codebase. The dangerous command patterns are regex-based heuristics, not formally verified grammars. The toolset system uses runtime validation but no static type-checked policy enforcement.

## 4. Source Code Analysis

### 4.1 Tool Execution Model

Tools are registered via `tools/registry.py` using a `registry.register()` call with a name, toolset, JSON schema, handler function, optional `check_fn` (availability gate), and emoji. The `model_tools.py` module discovers tools by importing all tool modules, which triggers their self-registration calls.

Tool execution flows through `handle_function_call()` in `model_tools.py` (lines 368-443), which:
1. Notifies the read-loop tracker for non-read tools
2. Checks if the tool requires agent-loop handling (todo, memory, session_search, delegate_task)
3. Invokes plugin `pre_tool_call` hooks
4. Dispatches through `registry.dispatch()` (or handles `execute_code` specially with sandbox-enabled tool list)
5. Invokes plugin `post_tool_call` hooks

Terminal commands pass through a consolidated guard (`check_all_command_guards` in `tools/approval.py`) before execution, which runs both tirith scanning and dangerous pattern detection, then either auto-approves (container backends), prompts the user (CLI/gateway), or applies smart approval (LLM risk assessment).

### 4.2 Input Handling

User input enters through two main paths:
- **CLI** (`cli.py`): Direct terminal input via prompt_toolkit
- **Gateway** (`gateway/`): Messages from 14+ messaging platforms, each with its own platform adapter

Input is not systematically sanitized or validated before being passed to the LLM. The framework relies on the LLM to interpret user intent and generate appropriate tool calls, with guardrails applied at the tool execution layer rather than the input layer.

For the cron system, scheduled prompts are scanned for injection patterns (`_scan_cron_prompt` in `tools/cronjob_tools.py`), which is the only input-level filtering observed.

External data (web content, file contents, tool outputs) is passed to the LLM as-is without boundary marking or content sanitization, making the system susceptible to indirect prompt injection.

### 4.3 Sandboxing and Isolation

Multiple isolation layers exist:

1. **Code execution sandbox** (`tools/code_execution_tool.py`): Child process with stripped environment variables, limited to 7 tools, communicating via UDS RPC. API keys excluded from child env. Process group isolation via `os.setsid()` and `os.killpg()` for cleanup. Timeout enforcement with SIGTERM escalation to SIGKILL.

2. **Container backends** (`tools/terminal_tool.py`): Docker, Singularity, Modal, and Daytona backends provide OS-level isolation. Dangerous command checks are bypassed for these backends.

3. **SSH backend**: Remote command execution — agent code stays on the local machine, commands execute remotely. `.env.example` documents this as providing API key protection and code modification prevention.

4. **Subagent isolation** (`tools/delegate_tool.py`): Fresh conversation context, own task_id, own terminal session, restricted toolset. Blocked tools: delegate_task, clarify, memory, send_message, execute_code.

5. **No filesystem sandboxing for local backend**: When using the local terminal backend, the agent has full access to the host filesystem and can execute arbitrary commands (subject to the approval system).

### 4.4 State Management

Session state is managed by `SessionDB` in `hermes_state.py`:
- **SQLite with WAL mode** for concurrent readers and a single writer
- **FTS5 virtual table** for full-text search across all session messages
- **Thread-safe write retries** with random jitter (15 retries, 20-150ms backoff) to handle multi-process contention
- **Schema versioning** (currently at version 6) with migration support
- **Parameterized queries** (verified by `tests/test_sql_injection.py`)

Persistent memory is stored in `~/.hermes/memories/` as markdown files. User profiles are maintained via Honcho integration (optional external service) or local memory tools.

Credential state is managed by `CredentialPool` in `agent/credential_pool.py`, supporting multiple credentials per provider with failover, rotation strategies (fill_first, round_robin, random, least_used), and OAuth token refresh for Anthropic, OpenAI Codex, and Nous Portal.

Auth data is stored in `~/.hermes/auth.json` with `0600` file permissions.

### 4.5 Network and Data Flow

Data flows through the system as follows:

1. User message enters via CLI or gateway platform adapter
2. System prompt is assembled from soul file, context files, skills, memory, and session context
3. Message history + system prompt sent to LLM provider via OpenAI-compatible API or Anthropic API
4. LLM response is parsed for tool calls (with model-specific parsers in `environments/tool_call_parsers/`)
5. Tool calls are dispatched through `handle_function_call()`
6. Tool results are appended to conversation history and sent back to the LLM
7. Final response is delivered to the user via the original platform

There are no network-level access controls on outbound connections. The agent can make HTTP requests via web tools, browser tools, and terminal commands without restrictions (beyond the browser SSRF check for private URLs).

The credential pool system manages API key rotation and failover across providers, with cooldown periods for exhausted credentials (1 hour for 429s, 24 hours for other failures).

### 4.6 Permission Model

The permission model is operator-configured:

- **Toolsets** can be enabled/disabled in `config.yaml` or via `hermes tools`
- **Terminal backends** determine the level of system isolation
- **Gateway user allowlists** control who can interact with the agent
- **DM pairing** allows dynamic user authorization with code-based verification
- **Dangerous command approval** is configurable: manual (default), smart (LLM-assisted), or off
- **Command allowlist** persists permanent approvals in `config.yaml`
- **YOLO mode** (`HERMES_YOLO_MODE` env var) disables all approval prompts

There is no fine-grained per-tool permission system, no capability-based security, and no distinction between different user roles. The system assumes a single trusted operator.

## 5. Production Readiness

### 5.1 Maturity Level

**Medium-high.** Hermes Agent is at version 0.6.0 with detailed release notes for each minor version (0.2.0 through 0.6.0). The codebase is substantial — over 50 Python source files, 100+ test files, and comprehensive documentation. It supports 14+ messaging platforms and 6 terminal backends, indicating significant real-world deployment.

The code shows signs of iterative hardening — security features like the approval system, redaction, pairing, and SSRF protection were clearly added in response to real usage scenarios. Comments reference specific issue numbers (e.g., "#560-discord", "#860", "#220").

### 5.2 Test Coverage

**Extensive.** The `tests/` directory contains ~100+ test files covering:

- Agent guardrails (`test_agent_guardrails.py` — orphaned tool pair repair, subagent concurrency limits, duplicate call deduplication)
- Credential pool management (`test_credential_pool.py` — 31KB of tests)
- Provider resolution and parity (`test_runtime_provider_resolution.py`, `test_provider_parity.py`)
- Gateway session management (`tests/gateway/`)
- Tool-specific tests (`tests/tools/` — 80+ files) including security-focused tests:
  - `test_approval.py` — dangerous command detection
  - `test_command_guards.py` — combined tirith + approval guards
  - `test_browser_ssrf_local.py` — SSRF protection
  - `test_cron_prompt_injection.py` — prompt injection scanning
  - `test_skill_view_traversal.py` — path traversal prevention
  - `test_code_execution.py` — sandbox behavior
  - `test_yolo_mode.py` — YOLO mode bypass
  - `test_credential_files.py` — credential file handling
  - `test_write_deny.py` — write operation restrictions
  - `test_force_dangerous_override.py` — force-approval bypass testing
  - `test_local_env_blocklist.py` — environment variable filtering
  - `test_url_safety.py` — URL safety checks
  - `test_website_policy.py` — website access control
- SQL injection mitigation (`test_sql_injection.py`)
- File permission hardening (`test_file_permissions.py`)
- Worktree security (`test_worktree_security.py` — path traversal, symlink escape)

Tests run with pytest-xdist for parallel execution, with integration tests marked separately and excluded from default runs.

### 5.3 Documentation Quality

**Good.** Documentation is available at a dedicated site (hermes-agent.nousresearch.com/docs) with sections covering quickstart, CLI usage, configuration, messaging gateway, security, tools, skills, memory, MCP integration, cron scheduling, context files, architecture, and contributing. The `.env.example` file (350 lines) serves as comprehensive inline documentation for all configuration options.

The `AGENTS.md` file (20KB) provides detailed guidance for AI coding agents working in the repository. The `CONTRIBUTING.md` (27KB) covers development setup, code style, and PR process.

### 5.4 Deployment Model

Hermes Agent supports multiple deployment models:

- **Local CLI**: Single-user desktop/laptop usage
- **Docker container**: Via `Dockerfile` — Debian-based with all dependencies
- **Cloud serverless**: Modal and Daytona backends with serverless persistence
- **Remote SSH**: Agent runs locally, commands execute remotely
- **VPS/systemd**: Gateway as a systemd service with messaging platform connections
- **Nix**: Flake-based reproducible builds

The gateway process can run as a long-lived daemon connecting to multiple messaging platforms simultaneously.

## 6. What Works Well

- **Breadth of integration**: 14+ messaging platforms, 6 terminal backends, 200+ LLM models, MCP integration, ACP integration, Skills Hub. The framework is genuinely useful as a personal agent.

- **Pragmatic security layering**: The dangerous command approval system, secret redaction, code execution sandbox, and DM pairing system represent thoughtful, practical security measures that protect against the most likely real-world failure modes.

- **Extensive test suite**: Over 100 test files with dedicated security-focused tests covering path traversal, SSRF, prompt injection, SQL injection, file permissions, and credential handling.

- **Supply chain awareness**: The CI supply chain audit workflow, pinned dependency ranges with CVE references, and tirith binary integrity verification show awareness of software supply chain risks.

- **Self-improving architecture**: The skills system, memory, session search, and Honcho user modeling create a genuinely learning agent — the stated differentiator is real.

- **Operator configuration flexibility**: The toolset system, multiple terminal backends, approval modes, and per-platform gateway configuration give operators meaningful control over the agent's capabilities.

## 7. Security Gaps (Relative to Defense Taxonomy)

These gaps are expected for a baseline non-security-focused framework. They serve as reference points for comparison with security-focused frameworks.

1. **No prompt injection defense for general content**: While cron prompts are scanned for injection patterns, external content (web pages, files, tool outputs) enters the LLM context without any boundary marking, content sanitization, or injection detection. This is the standard in the industry but a known gap.

2. **No outbound network controls**: The agent can make arbitrary HTTP requests via web tools, browser tools, and terminal commands. There is no network firewall, egress filtering, or data exfiltration prevention beyond the browser SSRF check.

3. **No formal tool call validation**: Tool calls are parsed from LLM output and dispatched directly. There is no schema validation beyond what the OpenAI API provides, no contract enforcement, and no formal verification of tool call correctness.

4. **No cryptographic integrity for session data**: Session transcripts, memory files, and configuration are stored without digital signatures. An attacker with file system access could tamper with the agent's memory and history.

5. **No multi-tenant security**: The framework is designed for single-user operation. All authorized gateway users have identical permissions and share the same agent context (modulo per-chat session isolation).

6. **Local backend has no filesystem isolation**: When running with the local terminal backend (the default), the agent has the same filesystem and network access as the user who launched it. Container backends provide isolation but are opt-in.

7. **Approval system is bypassable**: The `HERMES_YOLO_MODE` environment variable and the `approvals.mode: off` config setting disable all approval prompts. The dangerous command patterns are regex-based heuristics that sophisticated adversarial commands could potentially evade (though Unicode normalization and ANSI stripping make simple obfuscation harder).

8. **No model output safety filtering**: LLM responses are not checked for harmful content, instructions to bypass safety controls, or attempts to manipulate the user. The framework trusts the upstream model's safety alignment.

9. **Smart approval uses an LLM to judge another LLM's requests**: The `_smart_approve` function asks an auxiliary model to assess command risk, which creates a recursive trust dependency. If the adversary controls the content that influences the primary LLM, they may also influence the auxiliary model.

10. **Credential storage is not encrypted**: While file permissions (0600) restrict access, API keys and OAuth tokens in `auth.json` and `.env` are stored in plaintext. There is no at-rest encryption, no keychain integration, and no hardware security module support.

## 8. Key Findings

- **Hermes Agent has substantially more security infrastructure than a typical non-security-focused agent framework.** The dangerous command approval system, secret redaction, code execution sandbox, DM pairing with OWASP/NIST-informed design, SSRF protection, path traversal prevention, file permission hardening, supply chain CI audit, and tirith security scanner integration collectively represent a pragmatic defense-in-depth approach. This makes it a strong baseline — it sets the bar higher than "no security at all."

- **The security features are reactive and heuristic, not architectural.** Security measures are applied at the tool execution layer (command approval, SSRF checks) rather than being baked into the system architecture. There is no capability-based access control, no formal policy language, and no runtime security monitor. This is typical of baseline frameworks and contrasts with security-focused frameworks that design around a threat model.

- **The code execution sandbox is the most security-conscious component.** It deliberately strips credentials from the child environment, limits available tools to 7, communicates via RPC rather than shared state, enforces resource limits, and runs in a separate process group. This demonstrates that the developers understand isolation principles and apply them where the risk is highest (running LLM-generated code).

- **The test suite includes dedicated security regression tests**, including for path traversal (#220), prompt injection bypass in cron scheduling, SSRF, SQL injection, file permissions, command approval, and worktree escapes. This indicates a security-conscious development culture even in a framework not marketed as security-focused.

- **The primary unaddressed risks are indirect prompt injection and data exfiltration** — the same gaps present in virtually all production agent frameworks today. External content enters the LLM context without boundary marking, and the agent can make arbitrary outbound network requests. These are the hardest problems in agentic security and are not expected to be solved in a baseline framework.
