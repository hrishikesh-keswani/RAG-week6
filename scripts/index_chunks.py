"""Embed policy chunks into Chroma and run one sample query."""

import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

os.environ.setdefault("OLLAMA_BASE_URL", "http://127.0.0.1:11434")
os.environ.setdefault("EMBED_MODEL", "mxbai-embed-large")

from src.store import index_chunks, query_collection  # noqa: E402


def main() -> None:
    count = index_chunks()
    print(f"Indexed {count} chunks into .chroma/ collection policy_chunks")

    question = "What year is Coforge committed to achieve Net Zero?"
    result = query_collection(question, n_results=5)
    print(f"\nQuery: {question}\n")
    ids = result.get("ids", [[]])[0]
    metas = result.get("metadatas", [[]])[0]
    dists = result.get("distances", [[]])[0]
    docs = result.get("documents", [[]])[0]
    for rank, (chunk_id, meta, dist, doc) in enumerate(zip(ids, metas, dists, docs), start=1):
        preview = " ".join(doc.split())[:160]
        print(
            f"{rank}. v{meta.get('version')} {meta.get('filename')} | "
            f"{meta.get('section_name')} | dist={dist:.4f}\n"
            f"   {preview}...\n"
        )


if __name__ == "__main__":
    main()
