#!/usr/bin/env python3

from __future__ import annotations

import argparse
import dataclasses
import html
import os
import re
import subprocess
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path

import pandas as pd


@dataclasses.dataclass(frozen=True)
class ScanResults:
    arxiv_ids: set[str]
    openreview_ids: set[str]
    pdf_urls: set[str]


USER_AGENT = "agentic-security-sync/0.1 (+https://github.com/)"

ARXIV_NEW_ID_RE = re.compile(r"\b(?P<id>\d{4}\.\d{5})(?:v\d+)?\b")
ARXIV_CONTEXT_RE = re.compile(
    r"(?i)(?:arxiv\s*[: ]\s*|arxiv\.org/(?:abs|pdf)/|alphaxiv\.org/abs/)(?P<id>\d{4}\.\d{5})(?:v\d+)?"
)
OPENREVIEW_ID_RE = re.compile(r"https?://openreview\.net/(?:forum|pdf)\?id=(?P<id>[A-Za-z0-9]+)")
PDF_URL_RE = re.compile(r"https?://[^\s\)\]\">]+\.pdf")


def repo_root() -> Path:
    return Path(__file__).resolve().parents[1]


def iter_scan_files(root: Path) -> list[Path]:
    scan_paths: list[Path] = []

    # Keep scans constrained to “source docs” to avoid recursively pulling refs out of extracted PDFs.
    candidates = [
        root / "analysis",
        root / "datasets",
        root / "shisad" / "docs",
    ]
    for c in candidates:
        if c.exists():
            scan_paths.append(c)

    # Root-level markdown (e.g., README.md).
    scan_paths.extend([p for p in root.glob("*.md") if p.is_file()])

    files: list[Path] = []
    for p in scan_paths:
        if p.is_file():
            files.append(p)
            continue
        for f in p.rglob("*"):
            if not f.is_file():
                continue
            if f.suffix.lower() in {".md", ".csv", ".txt"}:
                files.append(f)
            elif f.suffix.lower() in {".xlsx"}:
                files.append(f)
    return sorted(set(files))


def scan_text(text: str) -> ScanResults:
    arxiv_ids = set()
    openreview_ids = set()
    pdf_urls = set()

    pdf_urls.update(PDF_URL_RE.findall(text))

    for m in OPENREVIEW_ID_RE.finditer(text):
        openreview_ids.add(m.group("id"))

    # Prefer context-driven extraction, but allow “bare” IDs (common in tables/CSVs).
    for m in ARXIV_CONTEXT_RE.finditer(text):
        arxiv_ids.add(m.group("id"))
    for m in ARXIV_NEW_ID_RE.finditer(text):
        arxiv_ids.add(m.group("id"))

    return ScanResults(arxiv_ids=arxiv_ids, openreview_ids=openreview_ids, pdf_urls=pdf_urls)


def scan_xlsx(path: Path) -> ScanResults:
    arxiv_ids: set[str] = set()
    openreview_ids: set[str] = set()
    pdf_urls: set[str] = set()

    sheets = pd.read_excel(path, sheet_name=None)
    for _, df in sheets.items():
        for val in df.astype(str).to_numpy().ravel():
            if not val or val == "nan":
                continue
            s = str(val)
            pdf_urls.update(PDF_URL_RE.findall(s))
            for m in OPENREVIEW_ID_RE.finditer(s):
                openreview_ids.add(m.group("id"))
            for m in ARXIV_CONTEXT_RE.finditer(s):
                arxiv_ids.add(m.group("id"))
            for m in ARXIV_NEW_ID_RE.finditer(s):
                arxiv_ids.add(m.group("id"))

    return ScanResults(arxiv_ids=arxiv_ids, openreview_ids=openreview_ids, pdf_urls=pdf_urls)


def scan_repo_for_refs(root: Path) -> ScanResults:
    arxiv_ids: set[str] = set()
    openreview_ids: set[str] = set()
    pdf_urls: set[str] = set()

    for f in iter_scan_files(root):
        if f.suffix.lower() == ".xlsx":
            r = scan_xlsx(f)
        else:
            try:
                text = f.read_text(encoding="utf-8", errors="ignore")
            except Exception:
                continue
            r = scan_text(text)
        arxiv_ids.update(r.arxiv_ids)
        openreview_ids.update(r.openreview_ids)
        pdf_urls.update(r.pdf_urls)

    return ScanResults(arxiv_ids=arxiv_ids, openreview_ids=openreview_ids, pdf_urls=pdf_urls)


def http_get(url: str, *, timeout_s: int = 30) -> bytes:
    req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    with urllib.request.urlopen(req, timeout=timeout_s) as resp:  # noqa: S310
        return resp.read()


def download(url: str, dest: Path, *, retries: int = 3) -> None:
    dest.parent.mkdir(parents=True, exist_ok=True)
    if dest.exists() and dest.stat().st_size > 0:
        return

    tmp = dest.with_suffix(dest.suffix + ".tmp")
    if tmp.exists():
        tmp.unlink()

    last_err: Exception | None = None
    for attempt in range(1, retries + 1):
        try:
            data = http_get(url, timeout_s=60)
            tmp.write_bytes(data)
            if tmp.stat().st_size == 0:
                raise RuntimeError("downloaded 0 bytes")
            tmp.replace(dest)
            return
        except Exception as e:  # noqa: BLE001
            last_err = e
            if tmp.exists():
                tmp.unlink()
            if attempt < retries:
                time.sleep(1.0 * attempt)

    raise RuntimeError(f"failed to download {url}: {last_err}")


def sanitize_filename(s: str) -> str:
    s = s.replace(os.sep, "_")
    s = re.sub(r"[^A-Za-z0-9._-]+", "_", s)
    return s.strip("_")


def arxiv_pdf_dest(papers_dir: Path, arxiv_id: str) -> Path:
    safe_id = arxiv_id.replace("/", "_")
    return papers_dir / f"arxiv-{safe_id}.pdf"


def openreview_pdf_dest(papers_dir: Path, openreview_id: str) -> Path:
    return papers_dir / f"openreview-{openreview_id}.pdf"


def classify_pdf_url(url: str, papers_dir: Path, vendor_dir: Path) -> Path:
    parsed = urllib.parse.urlparse(url)
    host = parsed.netloc.lower()
    basename = Path(parsed.path).name or "download.pdf"

    if host == "proceedings.iclr.cc":
        m = re.search(r"/paper_files/paper/(?P<year>\d{4})/file/", parsed.path)
        prefix = f"iclr{m.group('year')}-" if m else "iclr-"
        return papers_dir / f"{prefix}{sanitize_filename(basename)}"

    if host.endswith("anthropic.com"):
        return vendor_dir / f"anthropic-{sanitize_filename(basename)}"

    host_part = sanitize_filename(host.replace(".", "_"))
    return vendor_dir / f"{host_part}-{sanitize_filename(basename)}"


def run_extract(dirs: list[Path], *, force: bool) -> None:
    """Delegate text extraction to extract_pdf.py."""
    script = Path(__file__).resolve().parent / "extract_pdf.py"
    cmd = [sys.executable, str(script), "--quiet"]
    if force:
        cmd.append("--force")
    cmd.extend(str(d) for d in dirs if d.exists())
    subprocess.run(cmd, check=True)


def pdf_title(pdf: Path) -> str | None:
    try:
        out = subprocess.check_output(["pdfinfo", str(pdf)], text=True, stderr=subprocess.DEVNULL)
    except Exception:
        return None
    for line in out.splitlines():
        if line.startswith("Title:"):
            title = line.split(":", 1)[1].strip()
            return title or None
    return None


def html_title_and_canonical(html_path: Path) -> tuple[str | None, str | None]:
    try:
        text = html_path.read_text(encoding="utf-8", errors="ignore")
    except Exception:
        return None, None

    title = None
    m = re.search(r"(?is)<title[^>]*>(.*?)</title>", text)
    if m:
        title = html.unescape(re.sub(r"\s+", " ", m.group(1)).strip())

    canonical = None
    m = re.search(r'(?is)<link[^>]+rel="canonical"[^>]+href="([^"]+)"', text)
    if m:
        canonical = html.unescape(m.group(1)).strip()

    return title, canonical


def bib_escape(s: str) -> str:
    return (
        s.replace("\\", "\\\\")
        .replace("{", "\\{")
        .replace("}", "\\}")
        .replace("\n", " ")
        .replace("\r", " ")
    )


def write_text(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def generate_arxiv_bib(root: Path, bib_dir: Path, *, force: bool) -> Path:
    cache_dir = bib_dir / "arxiv"
    arxiv_pdfs = sorted((root / "references" / "papers").glob("arxiv-*.pdf"))
    ids = []
    for p in arxiv_pdfs:
        ids.append(p.stem.removeprefix("arxiv-").replace("_", "/"))
    ids = sorted(set(ids))

    for arxiv_id in ids:
        cache_path = cache_dir / f"{sanitize_filename(arxiv_id)}.bib"
        if cache_path.exists() and not force:
            continue
        bib = http_get(f"https://arxiv.org/bibtex/{arxiv_id}").decode("utf-8", errors="ignore").strip()
        write_text(cache_path, bib + "\n")

    combined = "\n".join((cache_dir / f"{sanitize_filename(i)}.bib").read_text(encoding="utf-8") for i in ids)
    out_path = bib_dir / "arxiv.bib"
    write_text(out_path, combined.strip() + "\n")
    return out_path


def openreview_meta(openreview_id: str) -> dict[str, str | list[str] | None]:
    html_bytes = http_get(f"https://openreview.net/forum?id={openreview_id}")
    text = html_bytes.decode("utf-8", errors="ignore")

    # OpenReview pages include `meta name="citation_*"` tags we can use.
    def meta_all(name: str) -> list[str]:
        return [
            html.unescape(m.group(1)).strip()
            for m in re.finditer(rf'(?is)<meta[^>]+name="{re.escape(name)}"[^>]+content="([^"]*)"', text)
        ]

    title = meta_all("citation_title")
    authors = meta_all("citation_author")
    date = meta_all("citation_online_date")
    pdf_url = meta_all("citation_pdf_url")
    conf = meta_all("citation_conference_title")

    return {
        "title": title[0] if title else None,
        "authors": authors or None,
        "online_date": date[0] if date else None,
        "pdf_url": pdf_url[0] if pdf_url else None,
        "conference": conf[0] if conf else None,
        "forum_url": f"https://openreview.net/forum?id={openreview_id}",
    }


def generate_openreview_bib(root: Path, bib_dir: Path, *, force: bool) -> Path:
    cache_dir = bib_dir / "openreview"
    openreview_pdfs = sorted((root / "references" / "papers").glob("openreview-*.pdf"))
    ids = sorted({p.stem.removeprefix("openreview-") for p in openreview_pdfs})

    entries: list[str] = []
    for oid in ids:
        cache_path = cache_dir / f"{oid}.bib"
        if cache_path.exists() and not force:
            entries.append(cache_path.read_text(encoding="utf-8"))
            continue

        meta = openreview_meta(oid)
        title = meta.get("title") or f"OpenReview {oid}"
        authors = meta.get("authors") or []
        if isinstance(authors, list):
            authors_str = " and ".join(authors)
        else:
            authors_str = str(authors)

        year = None
        online_date = meta.get("online_date")
        if isinstance(online_date, str) and online_date[:4].isdigit():
            year = online_date[:4]

        booktitle = meta.get("conference")
        url = meta.get("forum_url")
        pdf_url = meta.get("pdf_url")

        key = f"openreview{oid}"
        fields = {
            "title": title,
            "author": authors_str,
            "year": year,
            "booktitle": booktitle,
            "url": url,
            "pdf": pdf_url,
        }
        # Drop empty fields.
        fields = {k: v for k, v in fields.items() if v}

        entry_type = "inproceedings" if "booktitle" in fields else "misc"
        lines = [f"@{entry_type}{{{key},"] + [f"  {k}={{{bib_escape(str(v))}}}," for k, v in fields.items()] + ["}"]
        bib = "\n".join(lines) + "\n"
        write_text(cache_path, bib)
        entries.append(bib)

    out_path = bib_dir / "openreview.bib"
    write_text(out_path, "\n".join(e.strip() for e in entries if e.strip()) + "\n")
    return out_path


def generate_misc_bib(root: Path, bib_dir: Path, pdf_url_to_path: dict[str, Path]) -> Path:
    entries: list[tuple[str, str]] = []

    # Saved HTML pages.
    for html_path in sorted((root / "references" / "web").glob("*.html")):
        title, canonical = html_title_and_canonical(html_path)
        if not title:
            continue
        key = sanitize_filename(html_path.stem).lower()
        fields = {
            "title": title,
            "url": canonical,
            "howpublished": "Web page",
        }
        lines = [f"@misc{{{key},"] + [f"  {k}={{{bib_escape(str(v))}}}," for k, v in fields.items() if v] + ["}"]
        entries.append((key, "\n".join(lines) + "\n"))

    # Vendor PDFs (best-effort title from pdfinfo).
    for pdf in sorted((root / "references" / "vendor").glob("*.pdf")):
        title = pdf_title(pdf) or pdf.stem
        key = sanitize_filename(pdf.stem).lower()
        url = None
        for u, p in pdf_url_to_path.items():
            if p == pdf:
                url = u
                break
        fields = {
            "title": title,
            "url": url,
            "howpublished": "PDF",
        }
        lines = [f"@misc{{{key},"] + [f"  {k}={{{bib_escape(str(v))}}}," for k, v in fields.items() if v] + ["}"]
        entries.append((key, "\n".join(lines) + "\n"))

    # Other non-arXiv/OpenReview PDFs we downloaded (e.g., proceedings).
    for u, p in sorted(pdf_url_to_path.items()):
        if p.suffix.lower() != ".pdf":
            continue
        if p.name.startswith(("arxiv-", "openreview-")):
            continue
        if p.parent.name not in {"papers", "vendor"}:
            continue
        key = sanitize_filename(p.stem).lower()
        if any(k == key for k, _ in entries):
            continue
        fields = {
            "title": p.stem,
            "url": u,
            "howpublished": "PDF",
        }
        lines = [f"@misc{{{key},"] + [f"  {k}={{{bib_escape(str(v))}}}," for k, v in fields.items() if v] + ["}"]
        entries.append((key, "\n".join(lines) + "\n"))

    out_path = bib_dir / "misc.bib"
    content = "\n".join(v.strip() for _, v in sorted(entries, key=lambda kv: kv[0])) + "\n"
    write_text(out_path, content)
    return out_path


def main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(description="Sync reference PDFs + text snapshots + BibTeX for agentic-security.")
    parser.add_argument("--download", action="store_true", help="Download missing references.")
    parser.add_argument("--extract", action="store_true", help="Generate text snapshots (*.md) next to PDFs via extract_pdf.py.")
    parser.add_argument("--bibtex", action="store_true", help="Generate BibTeX under references/bib/.")
    parser.add_argument("--all", action="store_true", help="Equivalent to --download --extract --bibtex.")
    parser.add_argument("--force", action="store_true", help="Overwrite cached BibTeX and extracted snapshots.")

    args = parser.parse_args(argv)
    if args.all:
        args.download = True
        args.extract = True
        args.bibtex = True

    root = repo_root()
    papers_dir = root / "references" / "papers"
    web_dir = root / "references" / "web"
    vendor_dir = root / "references" / "vendor"
    bib_dir = root / "references" / "bib"

    refs = scan_repo_for_refs(root)

    pdf_url_to_path: dict[str, Path] = {}

    if args.download:
        for arxiv_id in sorted(refs.arxiv_ids):
            dest = arxiv_pdf_dest(papers_dir, arxiv_id)
            url = f"https://arxiv.org/pdf/{arxiv_id}.pdf"
            if not dest.exists() or dest.stat().st_size == 0:
                print(f"[get ] arXiv:{arxiv_id}")
            download(url, dest)

        for oid in sorted(refs.openreview_ids):
            dest = openreview_pdf_dest(papers_dir, oid)
            url = f"https://openreview.net/pdf?id={oid}"
            if not dest.exists() or dest.stat().st_size == 0:
                print(f"[get ] OpenReview:{oid}")
            download(url, dest)

        for url in sorted(refs.pdf_urls):
            # Skip if already covered by arXiv/OpenReview.
            if "arxiv.org/" in url:
                continue
            if "openreview.net/" in url:
                continue

            dest = classify_pdf_url(url, papers_dir, vendor_dir)
            pdf_url_to_path[url] = dest
            if not dest.exists() or dest.stat().st_size == 0:
                print(f"[get ] {url}")
            download(url, dest)

    # Even if we didn't download this run, try to map known PDF URLs to existing files
    # so `misc.bib` can include URLs for vendor docs.
    for url in sorted(refs.pdf_urls):
        if "arxiv.org/" in url or "openreview.net/" in url:
            continue
        dest = classify_pdf_url(url, papers_dir, vendor_dir)
        if dest.exists():
            pdf_url_to_path[url] = dest

    if args.extract:
        run_extract([papers_dir, vendor_dir], force=args.force)

    if args.bibtex:
        bib_dir.mkdir(parents=True, exist_ok=True)
        generate_arxiv_bib(root, bib_dir, force=args.force)
        generate_openreview_bib(root, bib_dir, force=args.force)
        generate_misc_bib(root, bib_dir, pdf_url_to_path)

    # Best-effort: keep these dirs around even if empty.
    for d in (papers_dir, web_dir, vendor_dir, bib_dir):
        d.mkdir(parents=True, exist_ok=True)

    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))

