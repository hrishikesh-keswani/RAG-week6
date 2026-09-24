"""Chunk data_md/*.md and write data_md/chunks.json."""

import json
import sys
from dataclasses import asdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from src.chunking import chunk_directory  # noqa: E402

OUT = ROOT / "data_md" / "chunks.json"


def main() -> None:
    chunks = chunk_directory()
    payload = {"chunk_count": len(chunks), "chunks": [asdict(c) for c in chunks]}
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    for c in chunks:
        print(
            f"{c.filename:28} v={c.version} | {c.section_title[:36]:36} | "
            f"{c.chunkid[-24:]:24} | {c.tokens:4} tok"
        )
    print(f"\nTotal chunks: {len(chunks)}")
    print(f"Wrote {OUT.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
