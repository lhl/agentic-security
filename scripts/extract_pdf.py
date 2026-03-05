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

    # Quiet mode (for scripting / sync_refs.py integration):
    python scripts/extract_pdf.py --quiet --force references/papers/

    # Debug mode (show backend/framework logs and warnings):
    python scripts/extract_pdf.py --debug references/papers/

    # From a conda/mamba env with live logs:
    mamba run --no-capture-output -n marker python scripts/extract_pdf.py references/papers/
"""

from __future__ import annotations

import argparse
import os
import shutil
import subprocess
import sys
import time
import warnings
from pathlib import Path

_DEBUG = "--debug" in sys.argv[1:] or os.environ.get("AGENTIC_SECURITY_PDF_DEBUG") == "1"

# Suppress noisy GPU/framework warnings unless debug mode is enabled.
if not _DEBUG:
    os.environ.setdefault("GRPC_VERBOSITY", "ERROR")
    os.environ.setdefault("GLOG_minloglevel", "2")
    os.environ.setdefault("PYTORCH_ENABLE_MPS_FALLBACK", "1")
    os.environ.setdefault("TRANSFORMERS_NO_ADVISORY_WARNINGS", "1")
    warnings.filterwarnings("ignore", message=".*Mem Efficient.*")
    warnings.filterwarnings("ignore", message=".*experimental.*")

# Force line-buffered stdout/stderr for normal pipes/terminals. Note: conda/mamba run may
# still capture output unless --no-capture-output/--live-stream is used.
if not os.environ.get("PYTHONUNBUFFERED"):
    sys.stdout = os.fdopen(sys.stdout.fileno(), "w", buffering=1, closefd=False)
    sys.stderr = os.fdopen(sys.stderr.fileno(), "w", buffering=1, closefd=False)


def _strip_user_site_packages() -> None:
    """Prevent ~/.local packages from shadowing active conda/venv dependencies."""
    if os.environ.get("AGENTIC_SECURITY_ALLOW_USER_SITE") == "1":
        return
    in_managed_env = bool(os.environ.get("CONDA_PREFIX")) or (
        sys.prefix != getattr(sys, "base_prefix", sys.prefix)
    )
    if not in_managed_env:
        return

    try:
        import site

        user_site = site.getusersitepackages()
    except Exception:
        return
    if not user_site:
        return

    normalized_user_site = os.path.normcase(os.path.abspath(user_site))
    new_path: list[str] = []
    removed = False
    for entry in sys.path:
        if entry and os.path.normcase(os.path.abspath(entry)) == normalized_user_site:
            removed = True
            continue
        new_path.append(entry)

    if removed:
        sys.path[:] = new_path
        os.environ.setdefault("PYTHONNOUSERSITE", "1")


# Must run before marker/surya imports to avoid pulling incompatible ~/.local deps.
_strip_user_site_packages()


def _fmt_duration(seconds: float) -> str:
    if seconds < 60:
        return f"{seconds:.1f}s"
    m, s = divmod(int(seconds), 60)
    return f"{m}m{s:02d}s"


def has_marker() -> bool:
    try:
        import marker  # noqa: F401
        return True
    except ImportError:
        return shutil.which("marker_single") is not None


def has_pdftotext() -> bool:
    return shutil.which("pdftotext") is not None


def detect_backend() -> str:
    if has_marker():
        return "marker"
    if has_pdftotext():
        return "pdftotext"
    print("error: neither marker nor pdftotext found", file=sys.stderr)
    print("install marker-pdf (pip install marker-pdf) or pdftotext (poppler-utils)", file=sys.stderr)
    sys.exit(1)


def _create_marker_converter():
    """Load marker models and create a reusable converter. Called once."""
    # Suppress internal tqdm progress bars from surya/marker unless debug is enabled.
    if not _DEBUG:
        os.environ["TQDM_DISABLE"] = "1"

    from marker.converters.pdf import PdfConverter
    from marker.models import create_model_dict

    models = create_model_dict()
    converter = PdfConverter(
        artifact_dict=models,
        config={"disable_image_extraction": True},
    )
    return converter


def _suppress_native_stderr():
    """Redirect fd 2 to /dev/null to silence C++ library noise (MIOpen, etc.)."""
    import contextlib

    if _DEBUG:
        return contextlib.nullcontext()

    @contextlib.contextmanager
    def _ctx():
        fd = 2
        old = os.dup(fd)
        devnull = os.open(os.devnull, os.O_WRONLY)
        os.dup2(devnull, fd)
        os.close(devnull)
        try:
            yield
        finally:
            os.dup2(old, fd)
            os.close(old)

    return _ctx()


def extract_marker(pdf: Path, out_md: Path, converter) -> None:
    with _suppress_native_stderr():
        rendered = converter(str(pdf))
    out_md.parent.mkdir(parents=True, exist_ok=True)
    # rendered is a RenderedOutput with .markdown attribute (or similar)
    if hasattr(rendered, "markdown"):
        text = rendered.markdown
    elif hasattr(rendered, "text"):
        text = rendered.text
    elif isinstance(rendered, str):
        text = rendered
    else:
        # Some versions return (text, images, metadata) tuple
        text = rendered[0] if isinstance(rendered, (list, tuple)) else str(rendered)
    out_md.write_text(f"<!-- extracted-by: marker -->\n{text}", encoding="utf-8")


def extract_pdftotext(pdf: Path, out_md: Path) -> None:
    out_md.parent.mkdir(parents=True, exist_ok=True)
    stdout_target = None if _DEBUG else subprocess.DEVNULL
    stderr_target = None if _DEBUG else subprocess.DEVNULL
    subprocess.run(
        ["pdftotext", "-layout", "-enc", "UTF-8", str(pdf), str(out_md)],
        check=True,
        stdout=stdout_target,
        stderr=stderr_target,
    )


_MARKER_STAMP = "<!-- extracted-by: marker -->"


def _was_extracted_by(md_path: Path, backend: str) -> bool:
    """Check if an existing .md was produced by a given backend."""
    try:
        head = md_path.read_text(encoding="utf-8", errors="ignore")[:256]
    except OSError:
        return False
    if backend == "marker":
        return _MARKER_STAMP in head
    # No stamp → assume pdftotext (or unknown)
    return _MARKER_STAMP not in head


def collect_pdfs(paths: list[Path]) -> list[Path]:
    pdfs: list[Path] = []
    for p in paths:
        if p.is_file() and p.suffix.lower() == ".pdf":
            pdfs.append(p)
        elif p.is_dir():
            pdfs.extend(sorted(p.glob("*.pdf")))
    return pdfs


def _run_quiet(pdfs: list[Path], backend: str, force: bool) -> int:
    """Quiet mode: one line per extracted file + summary. For scripting."""
    total = len(pdfs)
    extracted = skipped = failed = 0

    converter = None
    if backend == "marker":
        converter = _create_marker_converter()

    t_start = time.monotonic()
    for pdf in pdfs:
        out_md = pdf.with_suffix(".md")
        if out_md.exists() and not force and _was_extracted_by(out_md, backend):
            skipped += 1
            continue
        t0 = time.monotonic()
        try:
            if backend == "marker":
                extract_marker(pdf, out_md, converter)
            else:
                extract_pdftotext(pdf, out_md)
            dt = time.monotonic() - t0
            print(f"  {pdf.name} ({_fmt_duration(dt)})", flush=True)
            extracted += 1
        except Exception as e:
            dt = time.monotonic() - t0
            print(f"  ERROR {pdf.name} ({_fmt_duration(dt)}): {e}", file=sys.stderr, flush=True)
            failed += 1

    elapsed = time.monotonic() - t_start
    parts = [f"{extracted} extracted"]
    if skipped:
        parts.append(f"{skipped} skipped")
    if failed:
        parts.append(f"{failed} failed")
    print(f"[{backend}] {', '.join(parts)} of {total} — {_fmt_duration(elapsed)}")
    return 1 if (failed and not extracted) else 0


def _run_rich(pdfs: list[Path], backend: str, force: bool) -> int:
    """Interactive mode: rich progress bar + log panel."""
    from rich.console import Console
    from rich.progress import BarColumn, MofNCompleteColumn, Progress, TextColumn, TimeElapsedColumn, TimeRemainingColumn

    console = Console(stderr=True)
    extracted = skipped = failed = 0
    total = len(pdfs)

    # Pre-count skips so the progress bar reflects actual work
    to_extract: list[tuple[Path, Path]] = []
    for pdf in pdfs:
        out_md = pdf.with_suffix(".md")
        if out_md.exists() and not force and _was_extracted_by(out_md, backend):
            skipped += 1
        else:
            to_extract.append((pdf, out_md))

    if not to_extract:
        console.print(f"[bold][{backend}][/bold] {total} PDF(s), all already extracted (use --force to re-extract)")
        return 0

    console.print(f"[bold][{backend}][/bold] {len(to_extract)} to extract, {skipped} already done, {total} total")

    # Load models once (this is the slow part for marker)
    converter = None
    if backend == "marker":
        console.print("[dim]Loading marker models…[/dim]")
        t_load = time.monotonic()
        converter = _create_marker_converter()
        console.print(f"[dim]Models loaded in {_fmt_duration(time.monotonic() - t_load)}[/dim]")

    t_start = time.monotonic()
    with Progress(
        TextColumn("[progress.description]{task.description}"),
        BarColumn(),
        MofNCompleteColumn(),
        TimeElapsedColumn(),
        TextColumn("/"),
        TimeRemainingColumn(),
        console=console,
    ) as progress:
        task = progress.add_task("Extracting", total=len(to_extract))
        for pdf, out_md in to_extract:
            progress.update(task, description=f"[cyan]{pdf.name}[/cyan]")
            t0 = time.monotonic()
            try:
                if backend == "marker":
                    extract_marker(pdf, out_md, converter)
                else:
                    extract_pdftotext(pdf, out_md)
                dt = time.monotonic() - t0
                progress.console.print(f"  [green]OK[/green] {pdf.name} [dim]({_fmt_duration(dt)})[/dim]")
                extracted += 1
            except Exception as e:
                dt = time.monotonic() - t0
                progress.console.print(f"  [red]FAIL[/red] {pdf.name} [dim]({_fmt_duration(dt)})[/dim]: {e}")
                failed += 1
            progress.advance(task)

    elapsed = time.monotonic() - t_start
    parts = [f"[green]{extracted} extracted[/green]"]
    if skipped:
        parts.append(f"[dim]{skipped} skipped[/dim]")
    if failed:
        parts.append(f"[red]{failed} failed[/red]")
    console.print(f"\n[bold][{backend}][/bold] {', '.join(parts)} of {total} — {_fmt_duration(elapsed)}")
    return 1 if (failed and not extracted) else 0


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
    parser.add_argument("--quiet", "-q", action="store_true", help="Minimal output (no progress bar).")
    parser.add_argument(
        "--debug",
        action="store_true",
        help="Show backend/framework logs and warnings (disables built-in log suppression).",
    )

    args = parser.parse_args(argv)

    if args.debug and not _DEBUG:
        print("warning: --debug was not detected during early startup; some early logs may still be suppressed", file=sys.stderr)

    if args.backend == "auto":
        backend = detect_backend()
    else:
        backend = args.backend
        if backend == "marker" and not has_marker():
            print("error: marker not found", file=sys.stderr)
            return 1
        if backend == "pdftotext" and not has_pdftotext():
            print("error: pdftotext not found on PATH", file=sys.stderr)
            return 1

    pdfs = collect_pdfs(args.paths)
    if not pdfs:
        print("no PDFs found", file=sys.stderr)
        return 1

    # Early banner — write directly to fd to bypass all buffering (mamba run, etc.).
    os.write(2, f"[{backend}] found {len(pdfs)} PDF(s)…\n".encode())

    if args.quiet:
        return _run_quiet(pdfs, backend, args.force)
    return _run_rich(pdfs, backend, args.force)


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
