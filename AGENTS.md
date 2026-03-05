# agentic-security — Agent Guide

See `README.md` for repo layout, tooling, and workflows.

## Concurrent work

Multiple agents and the human lead may be working in this repo simultaneously. Check `git status -sb` before starting. Stage and commit only your own files. Do not touch unrelated changes.

## Generated artifacts (don't hand-edit)

- `references/papers/*.md` and `references/vendor/*.md` — text snapshots (regenerate via `scripts/sync_refs.py` or marker-pdf)
- `references/bib/*.bib` — BibTeX output (regenerate via `scripts/sync_refs.py`)

## Commits

- No bylines, co-author footers, or AI attribution in commit messages.
- Never use `git add .`, `git add -A`, or `git commit -a`.
- Stage only specific files with `git add <file>`.
