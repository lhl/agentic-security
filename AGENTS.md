# agentic-security — Agent Guide

See `README.md` for repo layout, tooling, and workflows.

## Concurrent work

Multiple agents and the human lead may be working in this repo simultaneously. Check `git status -sb` before starting. Stage and commit only your own files. Do not touch unrelated changes.

## Generated artifacts (don't hand-edit)

- `references/papers/*.md` and `references/vendor/*.md` — text snapshots (regenerate via `scripts/sync_refs.py` or marker-pdf)
- `references/bib/*.bib` — BibTeX output (regenerate via `scripts/sync_refs.py`)

## Writing ANALYSIS documents

These are public-facing technical reviews intended for security-literate developers who have **not** read the source code or internal architecture of the projects being analyzed.

### Terminology and naming
- Use each framework's own names for its components and mechanisms — precision matters.
- When a term is not a standard security/CS term of art (or its meaning is not obvious from context), explain it on first use. A parenthetical or one-sentence gloss is enough.
- Expand all acronyms on first occurrence, even project-specific ones (e.g., "Tool Dependency Graph (TDG)").
- Map project-specific concepts to well-known primitives where possible (e.g., "control-plane sidecar — a separate OS process that…").

### Formatting and readability
- Do not collapse distinct items into comma-separated run-on lists. Each distinct mechanism, gap, or finding gets its own bullet point or table row.
- Keep line items scannable — a reader should be able to skim a bulleted list and understand each point independently.

### Audience assumptions
- The reader understands security concepts, threat models, and software architecture.
- The reader has **not** examined the project's code, internal docs, or commit history.
- All claims should be traceable to observable behavior, public docs, or code-level evidence cited in the analysis — but the reader should not need to verify them to follow the argument.

## Commits

- No bylines, co-author footers, or AI attribution in commit messages.
- Never use `git add .`, `git add -A`, or `git commit -a`.
- Stage only specific files with `git add <file>`.
