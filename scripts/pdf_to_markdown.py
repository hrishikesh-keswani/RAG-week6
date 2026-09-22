"""Convert policy PDFs in documents/ to markdown via pymupdf4llm."""

import json
import re
from pathlib import Path

import pymupdf4llm

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "documents"
OUT = ROOT / "data" / "markdown"


def pdf_to_markdown(pdf: Path) -> str:
    pages = pymupdf4llm.to_markdown(str(pdf), page_chunks=True)
    parts: list[str] = []
    for i, page in enumerate(pages, start=1):
        text = (page.get("text") or "").strip()
        parts.append(f"--- page: {i} ---\n\n{text}")
    md = "\n\n".join(parts).strip() + "\n"
    sidecar = pdf.with_name(f"{pdf.stem}.meta.json")
    if sidecar.exists():
        try:
            version = str(json.loads(sidecar.read_text(encoding="utf-8")).get("version") or "")
        except json.JSONDecodeError:
            version = ""
        if version and not re.search(r"(?i)\bversion\s*[:=]", md[:2000]):
            md = re.sub(
                r"(--- page: 1 ---\n\n)",
                rf"\1**Version {version}**\n\n",
                md,
                count=1,
            )
    return md


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    pdfs = sorted(SRC.glob("*.pdf"))
    if not pdfs:
        raise SystemExit(f"No PDFs found in {SRC}")

    for pdf in pdfs:
        md = pdf_to_markdown(pdf)
        dest = OUT / f"{pdf.stem}.md"
        dest.write_text(md, encoding="utf-8")
        print(f"Wrote {dest.relative_to(ROOT)} ({len(md)} chars)")


if __name__ == "__main__":
    main()
