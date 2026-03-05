# Papers (Archived PDFs + Text Snapshots)

This directory contains **archived papers** referenced by our analyses.

Conventions:
- PDFs: `arxiv-<id>.pdf`, `openreview-<id>.pdf`, `iclrYYYY-<hash>...pdf`, etc.
- Text snapshots: same stem, `.md` (generated via `pdftotext -layout` for grep/LLM ingestion)

Automation:
- Use `python scripts/sync_refs.py --all` to fetch missing papers and refresh snapshots/BibTeX.

