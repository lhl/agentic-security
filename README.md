# Agentic Security Research

Research collection on LLM agent security: prompt injection defenses, privilege separation, control planes, runtime verification, and model hardening.

## Citation

If you reference this repo's summaries/analyses in academic or professional work, please cite:

```bibtex
@misc{lin_agentic_security_2026,
  author       = {Leonard Lin},
  title        = {agentic-security: LLM Agent Security Research Collection (Summaries and Analyses)},
  year         = {2026},
  howpublished = {GitHub repository},
  url          = {https://github.com/shisa-ai/agentic-security},
}
```

## Layout

```
agentic-security/
├── analysis/          # Cross-cutting synthesis and research notes (*.md)
├── datasets/          # Structured indices (CSV/XLSX)
├── references/        # Archived source material + derived artifacts
│   ├── papers/        # Paper PDFs + extracted text snapshots (*.md)
│   ├── bib/           # Generated BibTeX (*.bib)
│   ├── web/           # Saved HTML articles/pages
│   └── vendor/        # Vendor reports/system cards
├── scripts/           # Automation (sync downloads, extract text, generate BibTeX)
└── shisad/            # Project-specific implementation docs
```

## Sync

Download missing PDFs and generate BibTeX:

```bash
python scripts/sync_refs.py --all
```

This scans `analysis/`, `datasets/`, and `shisad/docs/` for arXiv/OpenReview/PDF links, downloads missing PDFs into `references/papers/` (and vendor PDFs into `references/vendor/`), generates `references/papers/*.md` text snapshots, and writes BibTeX under `references/bib/`.

## Reference index

Generate a topic-organized Markdown index of all local references (papers/vendor/web), with title + short summary:

```bash
python scripts/build_reference_index.py
```

Output: `references/REFERENCE_INDEX.md`

## PDF text extraction

`scripts/extract_pdf.py` converts PDFs to Markdown. Both `sync_refs.py --extract` and direct invocation use this script.

```bash
# Via sync (also downloads + generates bibtex):
python scripts/sync_refs.py --all

# Standalone — auto-detects best available backend:
python scripts/extract_pdf.py references/papers/

# Force a specific backend:
python scripts/extract_pdf.py --backend marker references/papers/
python scripts/extract_pdf.py --backend pdftotext references/papers/

# Single file, overwrite existing:
python scripts/extract_pdf.py --force references/papers/arxiv-2401.07612.pdf

# Debug mode (show marker/pdftotext backend logs and framework warnings):
python scripts/extract_pdf.py --debug references/papers/
```

Backend priority (auto mode): **marker-pdf** if `marker_single` is on PATH, else **pdftotext**, else error.

### marker-pdf setup

[marker-pdf](https://github.com/VikParuchuri/marker) produces structured Markdown (headings, tables, figures) — much better for LLM ingestion than pdftotext. It depends on PyTorch (CPU or GPU).

```bash
mamba create -n marker --clone therock   # or any env with torch
mamba activate marker
pip install marker-pdf
```

For GPU acceleration, use a torch build matching your hardware (CUDA, ROCm, etc.). To use marker from the conda env with the standalone script:

```bash
mamba run --no-capture-output -n marker python scripts/extract_pdf.py references/papers/
```

`mamba run` captures stdout/stderr by default, so progress output may not appear until the process exits unless `--no-capture-output` (alias `--live-stream`) is set.

### marker-pdf vs pdftotext

Tested on a 7-page academic paper (arxiv-2401.07612, "Signed-Prompt"):

| Tool | Time | Output |
|---|---|---|
| `pdftotext -layout` | 0.08s | Plain text. Broken multi-column layout, no heading hierarchy, tables mangled, wasted whitespace. |
| `marker-pdf` (GPU, warm) | 7.5s | Clean Markdown. Proper `#` headings, structured paragraphs, tables as Markdown pipes, figure captions preserved. |
| `marker-pdf` (GPU, cold start) | ~7min | Same quality. First-run overhead from MIOpen kernel JIT compilation (ROCm/AMD). |

marker is ~100x slower but produces structured Markdown that LLMs can parse semantically. For a batch of ~80 papers at ~7.5s each, total extraction is under 10 minutes.

System tested: AMD Ryzen AI MAX+ 395 w/ Radeon 8060S (ROCm 7.12), PyTorch 2.9.1, marker-pdf 1.10.2.

## Large files

PDFs are tracked with Git LFS via `.gitattributes`.
