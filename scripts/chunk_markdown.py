"""Chunk every Markdown file in data/markdown/ and write data/chunks.json."""

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from src.chunking import chunk_directory  # noqa: E402

OUT = ROOT / "data" / "chunks.json"


def main() -> None:
    markdown_dir = ROOT / "data" / "markdown"
    chunks = chunk_directory(markdown_dir)
    payload = {
        "chunk_count": len(chunks),
        "chunks": [c.to_dict() for c in chunks],
    }
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")

    for c in chunks:
        section = c.section[:42]
        print(
            f"{c.document_name:28} | {section:42} | "
            f"child {c.child_index} next={c.next_id or '-':<8} | "
            f"{c.word_count:4} words"
        )
    print(f"\nTotal chunks: {len(chunks)}")
    print(f"Wrote {OUT.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
