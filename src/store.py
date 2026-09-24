"""Persist chunk embeddings in a local Chroma collection."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import chromadb

from src.chunking import Chunk, chunk_directory
from src.embed import embed_chunks

ROOT = Path(__file__).resolve().parents[1]
CHROMA_DIR = ROOT / ".chroma"
COLLECTION = "policy_chunks"


def _metadata(chunk: Chunk) -> dict[str, Any]:
    return {
        "filename": chunk.filename,
        "version": chunk.version,
        "document_id": chunk.document_id,
        "section_name": chunk.section_name or chunk.section_title,
        "section_id": chunk.section_id,
        "chunkid": chunk.chunkid,
        "tokens": chunk.tokens,
        "table": chunk.table,
        "start_span": chunk.start_span,
        "end_span": chunk.end_span,
    }


def get_collection(persist_dir: Path = CHROMA_DIR) -> chromadb.Collection:
    client = chromadb.PersistentClient(path=str(persist_dir))
    return client.get_or_create_collection(
        name=COLLECTION,
        metadata={"hnsw:space": "cosine"},
    )


def reset_collection(persist_dir: Path = CHROMA_DIR) -> chromadb.Collection:
    """Drop and recreate the collection so a new embedding size can be stored."""
    client = chromadb.PersistentClient(path=str(persist_dir))
    try:
        client.delete_collection(COLLECTION)
    except Exception:
        pass
    return client.get_or_create_collection(
        name=COLLECTION,
        metadata={"hnsw:space": "cosine"},
    )


def index_chunks(persist_dir: Path = CHROMA_DIR, replace: bool = True) -> int:
    """Embed every policy chunk and upsert it into Chroma."""
    chunks = chunk_directory()
    embedded = embed_chunks(chunks)
    collection = reset_collection(persist_dir) if replace else get_collection(persist_dir)
    collection.upsert(
        ids=[item.chunk.chunkid for item in embedded],
        documents=[item.chunk.text for item in embedded],
        embeddings=[list(item.vector) for item in embedded],
        metadatas=[_metadata(item.chunk) for item in embedded],
    )
    return len(embedded)


def query_collection(
    question: str,
    n_results: int = 5,
    persist_dir: Path = CHROMA_DIR,
) -> dict[str, Any]:
    """Embed the question with the same model and return nearest chunks."""
    from src.embed import embed_texts

    collection = get_collection(persist_dir)
    vector = embed_texts([question])[0]
    return collection.query(
        query_embeddings=[list(vector)],
        n_results=n_results,
        include=["documents", "metadatas", "distances"],
    )
