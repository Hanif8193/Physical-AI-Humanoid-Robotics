"""
Chapter Ingestion Pipeline
Reads all 6 MDX chapters -> strips frontmatter -> chunks -> embeds -> upserts to Qdrant.
Uses sentence-transformers (local, free) for embeddings.

Usage: python scripts/ingest_chapters.py --docs ../frontend/docs/
"""
import argparse
import hashlib
import re
from pathlib import Path
from typing import Generator

from sentence_transformers import SentenceTransformer
from qdrant_client import QdrantClient
from qdrant_client.models import PointStruct, VectorParams, Distance
from dotenv import load_dotenv
import os

load_dotenv()

# Config
CHUNK_SIZE = 512  # tokens (approximate via character count * 0.75)
CHUNK_OVERLAP = 64
COLLECTION = "textbook_chunks"
EMBEDDING_MODEL = "all-MiniLM-L6-v2"
CHAPTER_SLUGS = [
    "ch01-intro-physical-ai",
    "ch02-ros2-fundamentals",
    "ch03-digital-twin",
    "ch04-isaac-platform",
    "ch05-vla",
    "ch06-capstone",
]


def strip_frontmatter(content: str) -> tuple:
    """Remove YAML frontmatter and return (metadata, body)."""
    if not content.startswith("---"):
        return {}, content

    end = content.find("---", 3)
    if end == -1:
        return {}, content

    frontmatter_text = content[3:end].strip()
    body = content[end + 3:].strip()

    metadata = {}
    for line in frontmatter_text.splitlines():
        if ":" in line:
            key, _, value = line.partition(":")
            metadata[key.strip()] = value.strip().strip('"')

    return metadata, body


def clean_mdx(text: str) -> str:
    """Remove MDX-specific syntax for embedding."""
    text = re.sub(r"^import .+$", "", text, flags=re.MULTILINE)
    text = re.sub(r"<\w+[^>]*/?>", "", text)
    text = re.sub(r"</\w+>", "", text)
    text = re.sub(r"```\w*\n(.*?)```", r"[Code: \1]", text, flags=re.DOTALL)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()


def chunk_text(text: str, section_hint: str = "") -> Generator[dict, None, None]:
    """Split text into ~512-token chunks with overlap."""
    max_chars = CHUNK_SIZE * 4
    overlap_chars = CHUNK_OVERLAP * 4

    sections = re.split(r"\n(#{1,3} .+)\n", text)

    current_section = section_hint
    buffer = ""
    chunk_idx = 0

    for part in sections:
        if part.startswith("#"):
            current_section = part.strip("# ").strip()
            continue

        buffer += part

        while len(buffer) > max_chars:
            yield {
                "text": buffer[:max_chars],
                "section": current_section,
                "chunk_index": chunk_idx,
            }
            chunk_idx += 1
            buffer = buffer[max_chars - overlap_chars:]

    if buffer.strip():
        yield {
            "text": buffer.strip(),
            "section": current_section,
            "chunk_index": chunk_idx,
        }


def make_deterministic_id(slug: str, chunk_index: int) -> str:
    """Generate a stable UUID from chapter slug + chunk index to prevent duplicates on re-ingest."""
    key = f"{slug}:{chunk_index}"
    return str(hashlib.md5(key.encode()).hexdigest())


def ingest_chapters(docs_path: str):
    print(f"Loading embedding model: {EMBEDDING_MODEL}")
    model = SentenceTransformer(EMBEDDING_MODEL)
    print("Embedding model loaded.")

    qdrant_client = QdrantClient(
        url=os.getenv("QDRANT_URL"),
        api_key=os.getenv("QDRANT_API_KEY"),
    )

    # Ensure collection exists
    existing = [c.name for c in qdrant_client.get_collections().collections]
    if COLLECTION not in existing:
        qdrant_client.create_collection(
            collection_name=COLLECTION,
            vectors_config=VectorParams(size=384, distance=Distance.COSINE),
        )
        print(f"Created collection: {COLLECTION}")

    docs_dir = Path(docs_path)
    total_chunks = 0

    for slug in CHAPTER_SLUGS:
        mdx_file = docs_dir / f"{slug}.mdx"
        if not mdx_file.exists():
            print(f"WARNING: Missing: {mdx_file}")
            continue

        content = mdx_file.read_text(encoding="utf-8")
        metadata, body = strip_frontmatter(content)
        body = clean_mdx(body)

        module = metadata.get("module", "unknown")
        chapter_title = metadata.get("title", slug)

        print(f"\nIngesting: {chapter_title}")

        chunks = list(chunk_text(body, chapter_title))
        print(f"  {len(chunks)} chunks")

        if not chunks:
            continue

        # Embed all chunks at once (sentence-transformers handles batching)
        texts = [c["text"] for c in chunks]
        embeddings = model.encode(texts, show_progress_bar=True)

        points = []
        for i, (chunk, embedding) in enumerate(zip(chunks, embeddings)):
            points.append(
                PointStruct(
                    id=make_deterministic_id(slug, chunk["chunk_index"]),
                    vector=embedding.tolist(),
                    payload={
                        "chapter_slug": slug,
                        "module": module,
                        "section": chunk["section"],
                        "text": chunk["text"],
                        "chunk_index": chunk["chunk_index"],
                    },
                )
            )

        qdrant_client.upsert(collection_name=COLLECTION, points=points)
        total_chunks += len(points)
        print(f"  Upserted {len(points)} vectors")

    print(f"\nIngestion complete! Total chunks: {total_chunks}")

    info = qdrant_client.get_collection(COLLECTION)
    count = info.points_count if hasattr(info, 'points_count') else total_chunks
    print(f"Qdrant collection size: {count} vectors")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Ingest chapters into Qdrant")
    parser.add_argument("--docs", default="../frontend/docs/", help="Path to docs directory")
    args = parser.parse_args()
    ingest_chapters(args.docs)
