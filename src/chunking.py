"""Header-aware Markdown chunking.

Works for any similarly structured Markdown (ATX headings and/or a short
standalone bold title line). Not tied to a specific document set.

Blocks (paragraphs, lists, tables) under the same heading are packed
together. Tables are never split mid-table.

Limits (words):
  TARGET_MAX  preferred packed size
  HARD_MAX    do not exceed unless a single block is already larger
  MIN_SIZE    do not emit a leftover smaller than this; fold it instead

No stored overlap. A heading is the parent; packed blocks under it are
children. At query time, retrieve a child then expand to its siblings
via expand_section_children().
"""

from __future__ import annotations

import json
import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Iterator, Optional

ROOT = Path(__file__).resolve().parents[1]

TARGET_MAX = 300
HARD_MAX = 400
MIN_SIZE = 100

HEADING_ATX = re.compile(r"^(#{1,6})\s+(.+?)\s*$")
HEADING_BOLD = re.compile(r"^\*{2}([^*]+)\*{2}\s*$")
TABLE_ROW = re.compile(r"^\s*\|.*\|\s*$")
PAGE_MARK = re.compile(r"^---\s*page:\s*(\d+)\s*---\s*$", re.I)
PAGE_FOOTER = re.compile(
    r"(?i)^\s*(page\s+\d+|[-–—]\s*\d+\s+of\s+\d+\s*[-–—]?)\s*$"
)
COPYRIGHT = re.compile(r"(?i)^\s*(©|\(c\)|copyright)\b")
TOC_DOTS = re.compile(r"\.{4,}\s*\d+\s*$")
VERSION_PATTERNS = (
    re.compile(r"(?i)\bversion\s*[:=]\s*v?(\d+(?:\.\d+)*)"),
    re.compile(r"\(v(\d+(?:\.\d+)*)\b"),
    re.compile(r"(?i)\bv(\d+\.\d+)\b"),
)


@dataclass
class Block:
    kind: str
    text: str
    start: int
    end: int
    page: int


@dataclass
class Chunk:
    text: str
    document_name: str
    section: str
    chunk_index: int
    parent_id: str = ""
    child_index: int = 0
    next_id: Optional[str] = None
    start_span: int = 0
    end_span: int = 0
    pagenumber: int = -1
    metadata: dict = field(default_factory=dict)

    @property
    def id(self) -> str:
        return f"{self.parent_id}::{self.child_index}"

    @property
    def word_count(self) -> int:
        return _word_count(self.text)

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "parent_id": self.parent_id,
            "child_index": self.child_index,
            "next_id": self.next_id,
            "text": self.text,
            "document_name": self.document_name,
            "section": self.section,
            "chunk_index": self.chunk_index,
            "word_count": self.word_count,
            "metadata": self.metadata,
        }


def _word_count(text: str) -> int:
    return len(re.findall(r"\S+", text))


def _sidecar_version(filename: str) -> str:
    if not filename:
        return ""
    sidecar = ROOT / "documents" / f"{Path(filename).stem}.meta.json"
    if not sidecar.exists():
        return ""
    try:
        data = json.loads(sidecar.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return ""
    return str(data.get("version") or "").strip()


def _extract_version(markdown: str, filename: str = "") -> str:
    """Two labels only: '1' = superseded/old, '2' = current."""
    head = markdown[:4000]
    if re.search(r"(?i)\bsuperseded\b", head):
        return "1"
    sidecar = _sidecar_version(filename)
    if sidecar:
        return sidecar.split(".")[0]
    for pattern in VERSION_PATTERNS:
        match = pattern.search(head)
        if match:
            return match.group(1).split(".")[0]
    return "2"


def _is_boilerplate(line: str) -> bool:
    stripped = line.strip()
    if not stripped:
        return False
    if PAGE_FOOTER.match(stripped) or COPYRIGHT.match(stripped):
        return True
    if TOC_DOTS.search(stripped):
        return True
    return False


def _normalize_heading(raw: str) -> str:
    text = raw.replace("**", " ").replace("__", " ")
    text = re.sub(r"\s+", " ", text).strip(" -:").strip()
    return text


def _is_heading(line: str) -> Optional[str]:
    """Return heading text if this line starts a new section."""
    atx = HEADING_ATX.match(line.strip())
    if atx:
        title = _normalize_heading(atx.group(2))
        return title or None
    bold = HEADING_BOLD.match(line.strip())
    if bold:
        title = _normalize_heading(bold.group(1))
        if line.strip().endswith(":"):
            return None
        if 3 <= _word_count(title) <= 12:
            return title
    return None


def iter_blocks(markdown: str) -> Iterator[Block]:
    """Yield content blocks with source spans and page numbers."""
    lines = markdown.replace("\r\n", "\n").split("\n")
    offset = 0
    buf: list[tuple[str, int, int]] = []
    kind = "text"
    page = -1

    def flush() -> Iterator[Block]:
        nonlocal buf, kind
        if not buf:
            kind = "text"
            return
        text = "\n".join(item[0] for item in buf).strip()
        start = buf[0][1]
        end = buf[-1][2]
        buf = []
        if text:
            yield Block(kind=kind, text=text, start=start, end=end, page=page)
        kind = "text"

    for line in lines:
        line_start = offset
        line_end = offset + len(line)
        offset = line_end + 1

        marked = PAGE_MARK.match(line.strip())
        if marked:
            yield from flush()
            page = int(marked.group(1))
            continue

        if _is_boilerplate(line):
            continue

        heading = _is_heading(line)
        if heading:
            yield from flush()
            yield Block(
                kind="heading",
                text=heading,
                start=line_start,
                end=line_end,
                page=page,
            )
            continue

        if TABLE_ROW.match(line):
            if kind != "table":
                yield from flush()
                kind = "table"
            buf.append((line, line_start, line_end))
            continue

        if not line.strip():
            if buf:
                yield from flush()
            continue

        if kind == "table":
            yield from flush()
        kind = "text"
        buf.append((line, line_start, line_end))

    yield from flush()


def _format_chunk(parts: list[str], document_name: str, section: str) -> str:
    body = "\n\n".join(p for p in parts if p.strip()).strip()
    header = f"{document_name} > {section}" if section else document_name
    return f"[{header}]\n{body}".strip()


def _union_span(chunks_or_blocks: list) -> tuple[int, int, int]:
    starts = [x.start_span if hasattr(x, "start_span") else x.start for x in chunks_or_blocks]
    ends = [x.end_span if hasattr(x, "end_span") else x.end for x in chunks_or_blocks]
    pages = [
        x.pagenumber if hasattr(x, "pagenumber") else x.page for x in chunks_or_blocks
    ]
    pages = [p for p in pages if p != -1]
    return min(starts), max(ends), (pages[0] if pages else -1)


def chunk_markdown(
    markdown: str,
    document_name: str,
    filename: str = "",
) -> list[Chunk]:
    """Chunk a markdown string. Safe for any similarly structured doc."""
    section = "Introduction"
    packed: list[Block] = []
    packed_words = 0
    chunks: list[Chunk] = []
    filename = filename or f"{document_name}.md"
    version = _extract_version(markdown, filename=filename)

    def reset_pack() -> None:
        nonlocal packed, packed_words
        packed, packed_words = [], 0

    def emit_from_blocks(blocks: list[Block]) -> Chunk:
        start, end, page = _union_span(blocks)
        text = _format_chunk([b.text for b in blocks], document_name, section)
        return Chunk(
            text=text,
            document_name=document_name,
            section=section or "Introduction",
            chunk_index=len(chunks),
            start_span=start,
            end_span=end,
            pagenumber=page,
        )

    def fold_or_emit(force: bool) -> None:
        if not packed:
            return
        wc = _word_count(" ".join(b.text for b in packed))
        if (
            not force
            and wc < MIN_SIZE
            and chunks
            and chunks[-1].section == section
        ):
            extra = "\n\n".join(b.text for b in packed)
            last = chunks[-1]
            last.text = f"{last.text}\n\n{extra}"
            start, end, page = _union_span([last, *packed])
            last.start_span = start
            last.end_span = end
            if last.pagenumber == -1:
                last.pagenumber = page
            reset_pack()
            return

        chunks.append(emit_from_blocks(packed))
        reset_pack()

    def start_new_section(title: str) -> None:
        nonlocal section
        fold_or_emit(force=False)
        section = title

    def accept_block(block: Block) -> None:
        nonlocal packed_words
        n = _word_count(block.text)

        if n > HARD_MAX and not packed:
            packed.append(block)
            packed_words = n
            fold_or_emit(force=True)
            return

        projected = packed_words + n
        if packed and projected > TARGET_MAX:
            leftover = n
            if leftover < MIN_SIZE and projected <= HARD_MAX:
                packed.append(block)
                packed_words = projected
                return
            fold_or_emit(force=True)

        packed.append(block)
        packed_words += n
        if packed_words >= TARGET_MAX:
            fold_or_emit(force=True)

    for block in iter_blocks(markdown):
        if block.kind == "heading":
            start_new_section(block.text)
            continue
        accept_block(block)

    fold_or_emit(force=False)
    if packed:
        fold_or_emit(force=True)
    merged = _assign_lineage(_merge_undersized(chunks))
    return _attach_metadata(merged, filename=filename, version=version)


def _merge_undersized(chunks: list[Chunk]) -> list[Chunk]:
    """Merge leftover chunks below MIN_SIZE into a neighbor in the same doc."""
    if not chunks:
        return chunks
    merged: list[Chunk] = []
    for chunk in chunks:
        if (
            merged
            and chunk.document_name == merged[-1].document_name
            and chunk.word_count < MIN_SIZE
        ):
            prev = merged[-1]
            prev.text = f"{prev.text}\n\n{chunk.text}"
            start, end, page = _union_span([prev, chunk])
            prev.start_span = start
            prev.end_span = end
            if prev.pagenumber == -1:
                prev.pagenumber = page
            continue
        merged.append(chunk)

    i = 0
    while i < len(merged) - 1:
        cur, nxt = merged[i], merged[i + 1]
        if cur.document_name == nxt.document_name and cur.word_count < MIN_SIZE:
            nxt.text = f"{cur.text}\n\n{nxt.text}"
            start, end, page = _union_span([cur, nxt])
            nxt.start_span = start
            nxt.end_span = end
            if nxt.pagenumber == -1:
                nxt.pagenumber = page
            nxt.section = f"{cur.section} / {nxt.section}"
            merged.pop(i)
            continue
        i += 1

    for idx, chunk in enumerate(merged):
        chunk.chunk_index = idx
    return merged


def _parent_id(document_name: str, section: str) -> str:
    return f"{document_name}::{section}"


def _assign_lineage(chunks: list[Chunk]) -> list[Chunk]:
    """Mark parent section + ordered children. Enables expand-on-retrieve."""
    counts: dict[str, int] = {}
    for chunk in chunks:
        pid = _parent_id(chunk.document_name, chunk.section)
        chunk.parent_id = pid
        chunk.child_index = counts.get(pid, 0)
        counts[pid] = chunk.child_index + 1

    by_parent: dict[str, list[Chunk]] = {}
    for chunk in chunks:
        by_parent.setdefault(chunk.parent_id, []).append(chunk)
    for siblings in by_parent.values():
        siblings.sort(key=lambda c: c.child_index)
        for i, chunk in enumerate(siblings):
            chunk.next_id = siblings[i + 1].id if i + 1 < len(siblings) else None
    return chunks


def _attach_metadata(
    chunks: list[Chunk],
    filename: str,
    version: str,
) -> list[Chunk]:
    for chunk in chunks:
        chunk.metadata = {
            "filename": filename,
            "pagenumber": chunk.pagenumber,
            "section_name": chunk.section,
            "chunkid": chunk.id,
            "start_span": chunk.start_span,
            "end_span": chunk.end_span,
            "version": version,
        }
    return chunks


def expand_section_children(
    hit_ids: list[str],
    chunks: list[Chunk],
) -> list[Chunk]:
    """Retrieve hit → return all children of those parents, in document order."""
    by_id = {chunk.id: chunk for chunk in chunks}
    parent_order: list[str] = []
    seen: set[str] = set()
    for hit_id in hit_ids:
        chunk = by_id.get(hit_id)
        if chunk is None or chunk.parent_id in seen:
            continue
        seen.add(chunk.parent_id)
        parent_order.append(chunk.parent_id)

    expanded: list[Chunk] = []
    for parent_id in parent_order:
        kids = [c for c in chunks if c.parent_id == parent_id]
        kids.sort(key=lambda c: c.child_index)
        expanded.extend(kids)
    return expanded


def chunk_file(path: Path) -> list[Chunk]:
    return chunk_markdown(
        path.read_text(encoding="utf-8"),
        document_name=path.stem,
        filename=path.name,
    )


def chunk_directory(markdown_dir: Path) -> list[Chunk]:
    all_chunks: list[Chunk] = []
    for path in sorted(markdown_dir.glob("*.md")):
        all_chunks.extend(chunk_file(path))
    return all_chunks
