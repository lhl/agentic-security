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

## PDF text extraction

### Default: `pdftotext` snapshots (fast)

`python scripts/sync_refs.py --extract` (or `--all`) generates one `*.md` per PDF using `pdftotext -layout`, alongside each PDF:

- `references/papers/*.md`
- `references/vendor/*.md`

These files are primarily for grep/search and quick LLM ingestion.

### Higher-quality extraction with marker-pdf

[marker-pdf](https://github.com/VikParuchuri/marker) converts PDFs to structured Markdown with proper headings, tables, and layout — much better for LLM ingestion than `pdftotext`.

#### Setup

Create a `marker` conda/mamba environment with PyTorch, then install marker-pdf:

```bash
mamba create -n marker --clone therock   # or any env with torch
mamba activate marker
pip install marker-pdf
```

marker-pdf depends on PyTorch (CPU or GPU). For GPU acceleration, use a torch build matching your hardware (CUDA, ROCm, etc.).

#### Usage

Single file:

```bash
mamba run -n marker marker_single references/papers/arxiv-XXXX.XXXXX.pdf \
  --output_dir references/papers/ --disable_image_extraction
```

Batch (all PDFs):

```bash
mamba run -n marker marker references/papers/ \
  --output_dir references/papers/ --disable_image_extraction --skip_existing
```

Output is one `*.md` per PDF alongside the original.

#### marker-pdf vs pdftotext

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
