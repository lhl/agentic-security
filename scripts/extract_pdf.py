#!/usr/bin/env python3
"""Extract text from PDFs to Markdown.

Uses marker-pdf (preferred) or pdftotext (fallback). Fails if neither is available.

Usage:
    # Auto-detect backend, extract all PDFs in a directory:
    python scripts/extract_pdf.py references/papers/

    # Single file:
    python scripts/extract_pdf.py references/papers/arxiv-2401.07612.pdf

    # Force pdftotext backend:
    python scripts/extract_pdf.py --backend pdftotext references/papers/

    # Overwrite existing .md files:
    python scripts/extract_pdf.py --force references/papers/
"""

from __future__ import annotations

import argparse
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path


def has_marker() -> bool:
    return shutil.which("marker_single") is not None


def has_pdftotext() -> bool:
    return shutil.which("pdftotext") is not None


def detect_backend() -> str:
    if has_marker():
        return "marker"
    if has_pdftotext():
        return "pdftotext"
    print("error: neither marker_single nor pdftotext found on PATH", file=sys.stderr)
    print("install marker-pdf (pip install marker-pdf) or pdftotext (poppler-utils)", file=sys.stderr)
    sys.exit(1)


def extract_marker(pdf: Path, out_md: Path) -> None:
    with tempfile.TemporaryDirectory() as tmp:
        subprocess.run(
            ["marker_single", str(pdf), "--output_dir", tmp, "--disable_image_extraction"],
            check=True,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
        # marker writes to <tmpdir>/<stem>/<stem>.md
        result = Path(tmp) / pdf.stem / f"{pdf.stem}.md"
        if not result.exists():
            # Some marker versions write directly
            candidates = list(Path(tmp).rglob("*.md"))
            if not candidates:
                raise RuntimeError(f"marker produced no output for {pdf}")
            result = candidates[0]
        out_md.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(result, out_md)


def extract_pdftotext(pdf: Path, out_md: Path) -> None:
    out_md.parent.mkdir(parents=True, exist_ok=True)
    subprocess.run(
        ["pdftotext", "-layout", "-enc", "UTF-8", str(pdf), str(out_md)],
        check=True,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )


def extract_one(pdf: Path, out_md: Path, backend: str) -> None:
    if backend == "marker":
        extract_marker(pdf, out_md)
    elif backend == "pdftotext":
        extract_pdftotext(pdf, out_md)
    else:
        raise ValueError(f"unknown backend: {backend}")


def collect_pdfs(paths: list[Path]) -> list[Path]:
    pdfs: list[Path] = []
    for p in paths:
        if p.is_file() and p.suffix.lower() == ".pdf":
            pdfs.append(p)
        elif p.is_dir():
            pdfs.extend(sorted(p.glob("*.pdf")))
    return pdfs


def main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(description="Extract text from PDFs to Markdown.")
    parser.add_argument("paths", nargs="+", type=Path, help="PDF files or directories containing PDFs.")
    parser.add_argument(
        "--backend",
        choices=["auto", "marker", "pdftotext"],
        default="auto",
        help="Extraction backend (default: auto = marker if available, else pdftotext).",
    )
    parser.add_argument("--force", action="store_true", help="Overwrite existing .md files.")

    args = parser.parse_args(argv)

    if args.backend == "auto":
        backend = detect_backend()
    else:
        backend = args.backend
        if backend == "marker" and not has_marker():
            print("error: marker_single not found on PATH", file=sys.stderr)
            return 1
        if backend == "pdftotext" and not has_pdftotext():
            print("error: pdftotext not found on PATH", file=sys.stderr)
            return 1

    pdfs = collect_pdfs(args.paths)
    if not pdfs:
        print("no PDFs found", file=sys.stderr)
        return 1

    print(f"[{backend}] {len(pdfs)} PDF(s)")

    for pdf in pdfs:
        out_md = pdf.with_suffix(".md")
        if out_md.exists() and not args.force:
            continue
        print(f"  {pdf.name}")
        try:
            extract_one(pdf, out_md, backend)
        except Exception as e:
            print(f"  ERROR: {e}", file=sys.stderr)

    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
