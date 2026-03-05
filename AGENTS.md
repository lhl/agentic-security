# agentic-security — minimal agent guide

Source of truth for repo organization + workflows: `README.md`.

## References workflow

- Papers/vendor docs live under `references/`:
  - `references/papers/` (academic papers)
  - `references/vendor/` (system cards, vendor PDFs, etc.)
  - `references/web/` (saved HTML pages)
  - `references/bib/` (BibTeX)
- Do not add new PDFs under the deprecated `papers/` directory.
- Prefer automation over manual downloads:
  - After adding new arXiv/OpenReview IDs or PDF links to `analysis/`, `datasets/`, or `shisad/docs/`, run:
    - `python scripts/sync_refs.py --all`

## Generated artifacts (don’t hand-edit)

- `references/papers/*.md` and `references/vendor/*.md` are generated text snapshots.
- `references/bib/*.bib` is generated BibTeX output.

Regenerate via `python scripts/sync_refs.py` instead of editing these by hand.

## Commits

- Do **not** run `git commit` unless the user explicitly asks.
- If asked to commit: keep commits small and scoped; prefer `docs:`, `chore:`, `feat:`, `fix:` style prefixes.

