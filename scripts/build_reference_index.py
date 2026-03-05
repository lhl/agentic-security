#!/usr/bin/env python3

from __future__ import annotations

import argparse
import csv
import datetime as dt
import html
import re
from collections import defaultdict
from dataclasses import dataclass
from pathlib import Path


SUMMARY_MAX_CHARS = 220

CATEGORY_THREAT = "Threat Model & Benchmarks"
CATEGORY_ARCH = "Secure Architectures by Construction"
CATEGORY_ACCESS = "Access Control & Governance"
CATEGORY_RUNTIME = "Runtime Verification & Policy Enforcement"
CATEGORY_DETECTION = "Detection, Filtering & Firewalls"
CATEGORY_MODEL = "Model-Level Hardening"
CATEGORY_BOUNDARY = "Boundary Marking & Cryptographic Provenance"
CATEGORY_FORMAL = "Formal Methods & Semantics"
CATEGORY_VENDOR = "Vendor System Cards & Policy Docs"
CATEGORY_WEB = "Web Articles & Commentary"
CATEGORY_OTHER = "Additional Related Work"

CATEGORY_ORDER = [
    CATEGORY_THREAT,
    CATEGORY_ARCH,
    CATEGORY_ACCESS,
    CATEGORY_RUNTIME,
    CATEGORY_DETECTION,
    CATEGORY_MODEL,
    CATEGORY_BOUNDARY,
    CATEGORY_FORMAL,
    CATEGORY_VENDOR,
    CATEGORY_WEB,
    CATEGORY_OTHER,
]

MANUAL_CATEGORY_OVERRIDES = {
    # Additional related work should mostly hold non-security / general capability papers.
    "2510.27246": CATEGORY_OTHER,  # Beyond a Million Tokens (memory benchmark)
    "2410.10813": CATEGORY_OTHER,  # LongMemEval (memory benchmark)
    "2406.11230": CATEGORY_OTHER,  # MMNeedle (multimodal long-context benchmark)
    "2210.03629": CATEGORY_OTHER,  # ReAct (general agent reasoning/acting method)
    # Security papers from the former "Additional" bucket.
    "2602.22724": CATEGORY_RUNTIME,  # AgentSentry
    "2502.01822": CATEGORY_DETECTION,  # Firewalls to Secure Dynamic LLM Agentic Networks
    "2509.10540": CATEGORY_THREAT,  # EchoLeak case study
    "2505.22852": CATEGORY_ARCH,  # Operationalizing CaMeL
    "2511.10720": CATEGORY_DETECTION,  # PISanitizer
    "2502.08966": CATEGORY_ACCESS,  # RTBAS
    "2505.23643": CATEGORY_FORMAL,  # FIDES / IFC formal model
    "2408.02373": CATEGORY_ACCESS,  # Operationalizing Contextual Integrity
    # Non-arXiv PDFs keyed by stem.
    "iclr2025-5750f91d8fb9d5c02bd8ad2c3b44456b-Paper-Conference": CATEGORY_THREAT,
}

MANUAL_TITLE_OVERRIDES = {
    # Normalize conference PDF title so it deduplicates with arXiv ASB.
    "iclr2025-5750f91d8fb9d5c02bd8ad2c3b44456b-Paper-Conference": "Agent Security Bench (ASB): Formalizing and Benchmarking Attacks and Defenses in LLM-based Agents",
}

DATASET_CATEGORY_MAP = {
    "Threat model & foundational attacks": CATEGORY_THREAT,
    "Secure architectures by construction": CATEGORY_ARCH,
    "Runtime verification & policy enforcement": CATEGORY_RUNTIME,
    "Detection, filtering & firewalls": CATEGORY_DETECTION,
    "Model-level hardening": CATEGORY_MODEL,
    "Boundary marking / cryptographic provenance": CATEGORY_BOUNDARY,
    "Position / operationalization": CATEGORY_OTHER,
}

ACCESS_RE = re.compile(
    r"\b(access control|authorization|authorized|policy|governance|governing|privilege|"
    r"mcp|agentbound|seagent|csagent|saga|progent|mandatory access control|abac|rbac)\b",
    flags=re.IGNORECASE,
)
FORMAL_RE = re.compile(
    r"\b(formal|calculus|noninterference|semantics|information flow|ifc|proof|verified)\b",
    flags=re.IGNORECASE,
)
BOUNDARY_RE = re.compile(
    r"\b(signed|signature|cryptographic|encrypted|fencing|authentication|provenance)\b",
    flags=re.IGNORECASE,
)
MODEL_RE = re.compile(
    r"\b(secalign|struq|foundation model|representation editing|instruction hierarchy|fine-?tuning)\b",
    flags=re.IGNORECASE,
)
DETECTION_RE = re.compile(
    r"\b(detect|detector|detection|firewall|filter|filtering|sanitiz|guard|shield|parsing)\b",
    flags=re.IGNORECASE,
)
RUNTIME_RE = re.compile(
    r"\b(runtime|verify|verification|enforcement|trace|trajectory|task shield|vigil|agentspec|toolsafe|drift)\b",
    flags=re.IGNORECASE,
)
THREAT_RE = re.compile(
    r"\b(benchmark|attack|attacks|red team|redteam|adversarial|threat|agentdojo|asb|agentdyn|injecagent|poison)\b",
    flags=re.IGNORECASE,
)
ARCH_RE = re.compile(
    r"\b(architecture|isolation|dual llm|control flow|data flow|design patterns|camel|airgap)\b",
    flags=re.IGNORECASE,
)

LINK_RE = re.compile(r"\[([^\]]+)\]\([^)]+\)")
TAG_RE = re.compile(r"<[^>]+>")
INLINE_ABSTRACT_RE = re.compile(
    r"(?is)(?:^|\n)\s*(?:#+\s*)?(?:\*+)?abstract(?:\*+)?\s*[\-:\u2014]\s*(.+?)(?:\n\s*\n|$)"
)
SUMMARY_VERB_RE = re.compile(
    r"\b(is|are|was|were|introduce|introduces|propose|proposes|present|presents|show|shows|"
    r"demonstrate|demonstrates|provide|provides|address|addresses|focus|focuses|evaluate|evaluates)\b",
    flags=re.IGNORECASE,
)


@dataclass(frozen=True)
class MatrixMeta:
    title: str
    category: str
    note: str


@dataclass(frozen=True)
class RefEntry:
    title: str
    summary: str
    category: str
    year: int | None
    source_label: str
    source_url: str | None
    links: tuple[tuple[str, str], ...]


def repo_root() -> Path:
    return Path(__file__).resolve().parents[1]


def parse_bib(path: Path) -> dict[str, dict[str, str]]:
    entries: dict[str, dict[str, str]] = {}
    if not path.exists():
        return entries

    current_key: str | None = None
    current_fields: dict[str, str] = {}

    for raw_line in path.read_text(encoding="utf-8", errors="ignore").splitlines():
        line = raw_line.rstrip()
        if not line.strip():
            continue

        if line.lstrip().startswith("@"):
            if current_key is not None:
                entries[current_key] = current_fields
            m = re.match(r"\s*@\w+\s*\{([^,]+),\s*$", line)
            if not m:
                current_key = None
                current_fields = {}
                continue
            current_key = m.group(1).strip()
            current_fields = {}
            continue

        if current_key is None:
            continue

        if line.strip() == "}":
            entries[current_key] = current_fields
            current_key = None
            current_fields = {}
            continue

        m = re.match(r'\s*([A-Za-z][A-Za-z0-9_-]*)\s*=\s*[{"](.+)[}"]\s*,?\s*$', line)
        if not m:
            continue
        field = m.group(1).lower().strip()
        value = clean_bib_value(m.group(2))
        current_fields[field] = value

    if current_key is not None:
        entries[current_key] = current_fields
    return entries


def clean_bib_value(value: str) -> str:
    value = value.replace("\\&", "&")
    value = value.replace("\\_", "_")
    value = re.sub(r"[{}]", "", value)
    value = re.sub(r"\s+", " ", value).strip()
    return value


def load_matrix(path: Path) -> dict[str, MatrixMeta]:
    mapping: dict[str, MatrixMeta] = {}
    if not path.exists():
        return mapping

    with path.open("r", encoding="utf-8", newline="") as f:
        reader = csv.DictReader(f)
        for row in reader:
            raw_id = (row.get("id") or "").strip()
            if not raw_id:
                continue
            mapping[raw_id] = MatrixMeta(
                title=(row.get("title") or "").strip(),
                category=(row.get("category") or "").strip(),
                note=(row.get("note") or "").strip(),
            )
    return mapping


def normalize_line(line: str) -> str:
    line = line.strip()
    if not line:
        return ""
    line = TAG_RE.sub(" ", line)
    line = LINK_RE.sub(r"\1", line)
    line = line.replace("**", "").replace("*", "").replace("`", "")
    line = re.sub(r"\s+", " ", line).strip()
    return line


def normalize_block(text: str) -> str:
    text = TAG_RE.sub(" ", text)
    text = LINK_RE.sub(r"\1", text)
    text = text.replace("**", "").replace("*", "").replace("`", "")
    text = re.sub(r"\s+", " ", text).strip()
    return text


def is_noise_line(line: str) -> bool:
    stripped = line.strip()
    if not stripped:
        return False
    if stripped.startswith("![]("):
        return True
    if stripped.startswith("|"):
        return True
    if stripped.startswith("```"):
        return True
    if stripped.startswith("Figure "):
        return True
    if stripped.startswith("Table "):
        return True
    if stripped.startswith("Algorithm "):
        return True
    return False


def first_paragraph(lines: list[str], start_idx: int) -> str | None:
    i = start_idx
    while i < len(lines):
        line = normalize_line(lines[i])
        if not line:
            i += 1
            continue
        if is_noise_line(line):
            i += 1
            continue
        if line.startswith("#"):
            i += 1
            continue

        para: list[str] = [line]
        i += 1
        while i < len(lines):
            nxt = normalize_line(lines[i])
            if not nxt:
                break
            if nxt.startswith("#"):
                break
            if is_noise_line(nxt):
                i += 1
                continue
            para.append(nxt)
            i += 1
        joined = " ".join(para).strip()
        if len(joined) >= 80 and not is_unusable_summary(joined):
            return joined
        i += 1
    return None


def is_unusable_summary(text: str) -> bool:
    low = text.lower()
    if low.startswith(("table of contents", "contents", "abstract |", "algorithm ")):
        return True

    comma_count = text.count(",")
    has_verb = SUMMARY_VERB_RE.search(text) is not None
    looks_authory = comma_count >= 3 and not has_verb
    has_affiliation_words = any(word in low for word in ("university", "institute", "laboratory", "school"))
    if looks_authory and has_affiliation_words:
        return True
    if looks_authory and " et al" in low:
        return True
    if looks_authory and re.search(r"\b[A-Z][a-z]+(?:\s+[A-Z][a-z]+){2,}\b", text):
        return True

    if re.search(r"\b\d+\s*,\s*\w+\b", text) and not has_verb:
        return True

    return False


def summarize_markdown(md_path: Path) -> str | None:
    if not md_path.exists():
        return None

    text = md_path.read_text(encoding="utf-8", errors="ignore")
    text = re.sub(r"<!--.*?-->", " ", text, flags=re.DOTALL)

    m = INLINE_ABSTRACT_RE.search(text)
    if m:
        abstract = normalize_block(m.group(1))
        if abstract and not is_unusable_summary(abstract):
            return shorten(abstract)

    lines = text.splitlines()

    for idx, raw in enumerate(lines):
        line = normalize_line(raw)
        normalized_heading = line.lstrip("#").strip().lower()
        if normalized_heading == "abstract":
            abstract = first_paragraph(lines, idx + 1)
            if abstract:
                return shorten(abstract)

    paragraph = first_paragraph(lines, 0)
    if paragraph:
        return shorten(paragraph)
    return None


def summarize_html(html_path: Path) -> str | None:
    if not html_path.exists():
        return None
    text = html_path.read_text(encoding="utf-8", errors="ignore")

    m = re.search(r'(?is)<meta[^>]+name=["\']description["\'][^>]+content=["\']([^"\']+)', text)
    if m:
        desc = html.unescape(m.group(1)).strip()
        desc = re.sub(r"\s+", " ", desc)
        if desc:
            return shorten(desc)

    m = re.search(r"(?is)<p[^>]*>(.*?)</p>", text)
    if m:
        para = html.unescape(TAG_RE.sub(" ", m.group(1))).strip()
        para = re.sub(r"\s+", " ", para)
        if len(para) >= 40:
            return shorten(para)
    return None


def shorten(text: str, max_chars: int = SUMMARY_MAX_CHARS) -> str:
    text = re.sub(r"\s+", " ", text).strip()
    if len(text) <= max_chars:
        return text

    window = text[: max_chars + 1]
    sentence_idx = max(window.rfind(". "), window.rfind("; "), window.rfind(": "))
    if sentence_idx >= int(max_chars * 0.6):
        return window[: sentence_idx + 1].strip()

    comma_idx = window.rfind(", ")
    if comma_idx >= int(max_chars * 0.6):
        return window[:comma_idx].strip() + "..."

    return window[:max_chars].rstrip(" ,;:") + "..."


def year_from_fields(fields: dict[str, str], fallback_id: str | None = None) -> int | None:
    raw_year = (fields.get("year") or "").strip()
    if raw_year.isdigit():
        return int(raw_year)
    if fallback_id and re.match(r"^\d{4}\.\d{5}$", fallback_id):
        yy = int(fallback_id[:2])
        return 2000 + yy
    return None


def classify_category(
    *,
    ref_type: str,
    title: str,
    summary: str,
    dataset_category: str | None,
) -> str:
    if ref_type == "vendor":
        return CATEGORY_VENDOR
    if ref_type == "web":
        return CATEGORY_WEB

    if dataset_category:
        mapped = DATASET_CATEGORY_MAP.get(dataset_category, CATEGORY_OTHER)
        if mapped == CATEGORY_ARCH:
            combined = f"{title} {summary}"
            if ACCESS_RE.search(combined):
                return CATEGORY_ACCESS
            if FORMAL_RE.search(combined):
                return CATEGORY_FORMAL
        return mapped

    combined = f"{title} {summary}"
    if BOUNDARY_RE.search(combined):
        return CATEGORY_BOUNDARY
    if MODEL_RE.search(combined):
        return CATEGORY_MODEL
    if DETECTION_RE.search(combined):
        return CATEGORY_DETECTION
    if RUNTIME_RE.search(combined):
        return CATEGORY_RUNTIME
    if THREAT_RE.search(combined):
        return CATEGORY_THREAT
    if ACCESS_RE.search(combined):
        return CATEGORY_ACCESS
    if FORMAL_RE.search(combined):
        return CATEGORY_FORMAL
    if ARCH_RE.search(combined):
        return CATEGORY_ARCH
    return CATEGORY_OTHER


def fallback_summary(title: str, ref_type: str) -> str:
    if ref_type == "web":
        return "Saved web snapshot cited in this repository's analysis."
    if ref_type == "vendor":
        return "Vendor/system documentation snapshot used as a primary reference."
    return f"Research reference on {title.lower()}."


def load_reference_entries(root: Path) -> list[RefEntry]:
    refs: list[RefEntry] = []

    papers_dir = root / "references" / "papers"
    vendor_dir = root / "references" / "vendor"
    web_dir = root / "references" / "web"
    matrix_path = root / "datasets" / "ai_agent_security_paper_matrix.csv"
    matrix = load_matrix(matrix_path)

    arxiv_bib = parse_bib(root / "references" / "bib" / "arxiv.bib")
    openreview_bib = parse_bib(root / "references" / "bib" / "openreview.bib")
    misc_bib = parse_bib(root / "references" / "bib" / "misc.bib")

    arxiv_by_id: dict[str, dict[str, str]] = {}
    for fields in arxiv_bib.values():
        arxiv_id = (fields.get("eprint") or "").strip()
        if not arxiv_id:
            continue
        arxiv_by_id[arxiv_id] = fields
        arxiv_by_id[arxiv_id.replace("/", "_")] = fields

    openreview_by_id: dict[str, dict[str, str]] = {}
    for key, fields in openreview_bib.items():
        if key.startswith("openreview"):
            openreview_id = key.removeprefix("openreview")
            openreview_by_id[openreview_id] = fields
        openreview_by_id[key] = fields

    misc_by_key = {k.lower(): v for k, v in misc_bib.items()}

    for pdf in sorted(papers_dir.glob("arxiv-*.pdf")):
        arxiv_id = pdf.stem.removeprefix("arxiv-")
        matrix_meta = matrix.get(arxiv_id)
        fields = arxiv_by_id.get(arxiv_id, {})
        md = pdf.with_suffix(".md")

        title = (
            (matrix_meta.title if matrix_meta and matrix_meta.title else "")
            or fields.get("title", "")
            or pdf.stem
        ).strip()
        summary = (
            (matrix_meta.note if matrix_meta and matrix_meta.note else "")
            or summarize_markdown(md)
            or fallback_summary(title, "paper")
        )
        category = classify_category(
            ref_type="paper",
            title=title,
            summary=summary,
            dataset_category=matrix_meta.category if matrix_meta else None,
        )
        category = MANUAL_CATEGORY_OVERRIDES.get(arxiv_id, category)
        year = year_from_fields(fields, fallback_id=arxiv_id.replace("_", "/"))
        url = fields.get("url") or f"https://arxiv.org/abs/{arxiv_id.replace('_', '/')}"

        links: list[tuple[str, str]] = [("pdf", f"papers/{pdf.name}")]
        if md.exists():
            links.append(("text", f"papers/{md.name}"))

        refs.append(
            RefEntry(
                title=title,
                summary=summary,
                category=category,
                year=year,
                source_label=f"arXiv:{arxiv_id.replace('_', '/')}",
                source_url=url,
                links=tuple(links),
            )
        )

    for pdf in sorted(papers_dir.glob("openreview-*.pdf")):
        oid = pdf.stem.removeprefix("openreview-")
        fields = openreview_by_id.get(oid, {})
        md = pdf.with_suffix(".md")

        title = fields.get("title") or pdf.stem
        summary = summarize_markdown(md) or fallback_summary(title, "paper")
        category = classify_category(
            ref_type="paper",
            title=title,
            summary=summary,
            dataset_category=None,
        )
        category = MANUAL_CATEGORY_OVERRIDES.get(oid, category)
        year = year_from_fields(fields)
        url = fields.get("url") or f"https://openreview.net/forum?id={oid}"

        links: list[tuple[str, str]] = [("pdf", f"papers/{pdf.name}")]
        if md.exists():
            links.append(("text", f"papers/{md.name}"))

        refs.append(
            RefEntry(
                title=title,
                summary=summary,
                category=category,
                year=year,
                source_label=f"OpenReview:{oid}",
                source_url=url,
                links=tuple(links),
            )
        )

    for pdf in sorted(papers_dir.glob("*.pdf")):
        if pdf.name.startswith(("arxiv-", "openreview-")):
            continue
        md = pdf.with_suffix(".md")
        stem = pdf.stem
        key = stem.lower()
        fields = misc_by_key.get(key, {})

        title = MANUAL_TITLE_OVERRIDES.get(stem) or fields.get("title") or pdf.stem
        summary = summarize_markdown(md) or fallback_summary(title, "paper")
        category = classify_category(
            ref_type="paper",
            title=title,
            summary=summary,
            dataset_category=None,
        )
        category = MANUAL_CATEGORY_OVERRIDES.get(stem, category)
        year = year_from_fields(fields)
        url = fields.get("url")

        links: list[tuple[str, str]] = [("pdf", f"papers/{pdf.name}")]
        if md.exists():
            links.append(("text", f"papers/{md.name}"))

        refs.append(
            RefEntry(
                title=title,
                summary=summary,
                category=category,
                year=year,
                source_label="PDF",
                source_url=url,
                links=tuple(links),
            )
        )

    for pdf in sorted(vendor_dir.glob("*.pdf")):
        md = pdf.with_suffix(".md")
        key = pdf.stem.lower()
        fields = misc_by_key.get(key, {})

        title = fields.get("title") or pdf.stem
        summary = summarize_markdown(md) or fallback_summary(title, "vendor")
        year = year_from_fields(fields)
        url = fields.get("url")

        links: list[tuple[str, str]] = [("pdf", f"vendor/{pdf.name}")]
        if md.exists():
            links.append(("text", f"vendor/{md.name}"))

        refs.append(
            RefEntry(
                title=title,
                summary=summary,
                category=CATEGORY_VENDOR,
                year=year,
                source_label="Vendor",
                source_url=url,
                links=tuple(links),
            )
        )

    for html_file in sorted(web_dir.glob("*.html")):
        key = html_file.stem.lower()
        fields = misc_by_key.get(key, {})
        title = fields.get("title") or html_file.stem
        summary = summarize_html(html_file) or fallback_summary(title, "web")
        year = year_from_fields(fields)
        url = fields.get("url")

        refs.append(
            RefEntry(
                title=title,
                summary=summary,
                category=CATEGORY_WEB,
                year=year,
                source_label="Web",
                source_url=url,
                links=(("snapshot", f"web/{html_file.name}"),),
            )
        )

    return refs


def normalize_title_for_merge(title: str) -> str:
    t = title.lower().strip()
    t = re.sub(r"[^a-z0-9]+", " ", t)
    t = re.sub(r"\s+", " ", t).strip()
    return t


def category_rank(category: str) -> int:
    if category in CATEGORY_ORDER:
        return CATEGORY_ORDER.index(category)
    return len(CATEGORY_ORDER) + 1


def summary_quality(summary: str) -> tuple[int, int]:
    low = summary.lower()
    generic = 0
    if low.startswith("saved web snapshot cited"):
        generic = 1
    if low.startswith("vendor/system documentation snapshot"):
        generic = 1
    if low.startswith("research reference on "):
        generic = 1
    return (generic, -len(summary))


def source_url_rank(url: str | None) -> int:
    if not url:
        return 99
    if "arxiv.org/" in url:
        return 0
    if "openreview.net/" in url:
        return 1
    return 2


def merge_duplicate_entries(refs: list[RefEntry]) -> list[RefEntry]:
    grouped: dict[str, list[RefEntry]] = defaultdict(list)
    for ref in refs:
        key = normalize_title_for_merge(ref.title)
        grouped[key].append(ref)

    merged: list[RefEntry] = []
    for _, items in grouped.items():
        if len(items) == 1:
            merged.append(items[0])
            continue

        title = items[0].title
        summary = sorted((i.summary for i in items), key=summary_quality)[0]
        category = sorted((i.category for i in items), key=category_rank)[0]

        years = [i.year for i in items if i.year is not None]
        year = max(years) if years else None

        source_labels = []
        seen_labels = set()
        for it in items:
            if it.source_label not in seen_labels:
                seen_labels.add(it.source_label)
                source_labels.append(it.source_label)
        source_label = " + ".join(source_labels)

        primary_url = sorted((i.source_url for i in items), key=source_url_rank)[0]

        links: list[tuple[str, str]] = []
        seen_links: set[tuple[str, str]] = set()
        for it in items:
            for link in it.links:
                if link in seen_links:
                    continue
                seen_links.add(link)
                links.append(link)

        # Preserve non-primary external source URLs as explicit links.
        extra_urls = []
        for it in items:
            if it.source_url and it.source_url != primary_url and it.source_url not in extra_urls:
                extra_urls.append(it.source_url)
        for i, url in enumerate(extra_urls, start=1):
            label = f"source-alt-{i}"
            links.append((label, url))

        merged.append(
            RefEntry(
                title=title,
                summary=summary,
                category=category,
                year=year,
                source_label=source_label,
                source_url=primary_url,
                links=tuple(links),
            )
        )

    return merged


def sort_key(ref: RefEntry) -> tuple[int, str]:
    year_sort = ref.year if ref.year is not None else -1
    return (-year_sort, ref.title.lower())


def render_index(refs: list[RefEntry]) -> str:
    grouped: dict[str, list[RefEntry]] = defaultdict(list)
    for ref in refs:
        grouped[ref.category].append(ref)

    for entries in grouped.values():
        entries.sort(key=sort_key)

    today = dt.date.today().isoformat()
    lines: list[str] = []
    lines.append("# Reference Index")
    lines.append("")
    lines.append(
        "Topic-organized index of references under `references/`, including title, short summary, and local/source links."
    )
    lines.append("")
    lines.append(f"- Generated: {today}")
    lines.append(f"- Total references: {len(refs)}")
    lines.append("")

    categories = [c for c in CATEGORY_ORDER if c in grouped]
    extras = sorted(c for c in grouped if c not in CATEGORY_ORDER)
    categories.extend(extras)

    for category in categories:
        entries = grouped.get(category, [])
        if not entries:
            continue
        lines.append(f"## {category} ({len(entries)})")
        lines.append("")
        for ref in entries:
            meta: list[str] = []
            if ref.year is not None:
                meta.append(str(ref.year))
            if ref.source_label:
                meta.append(ref.source_label)
            meta_str = "; ".join(f"`{m}`" for m in meta)

            link_bits = [f"[{label}]({target})" for label, target in ref.links]
            if ref.source_url:
                link_bits.append(f"[source]({ref.source_url})")
            links_str = ", ".join(link_bits)

            entry = f"- **{ref.title}**"
            if meta_str:
                entry += f" ({meta_str})"
            if links_str:
                entry += f" ({links_str})"
            entry += f" - {ref.summary}"
            lines.append(entry)
        lines.append("")

    return "\n".join(lines).rstrip() + "\n"


def main() -> int:
    parser = argparse.ArgumentParser(description="Build references/REFERENCE_INDEX.md grouped by topic category.")
    parser.add_argument(
        "--output",
        default="references/REFERENCE_INDEX.md",
        help="Path to output markdown file (relative to repo root).",
    )
    args = parser.parse_args()

    root = repo_root()
    refs = load_reference_entries(root)
    refs = merge_duplicate_entries(refs)
    refs.sort(key=sort_key)

    output = root / args.output
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(render_index(refs), encoding="utf-8")
    print(f"[ok] wrote {output.relative_to(root)} ({len(refs)} references)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
