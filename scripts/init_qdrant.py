"""
Initialize Qdrant Cloud collection for textbook chunks.
Run once before ingestion: python scripts/init_qdrant.py
"""
import asyncio
from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams, PayloadSchemaType
from dotenv import load_dotenv
import os

load_dotenv()


def init_collection():
    client = QdrantClient(
        url=os.getenv("QDRANT_URL"),
        api_key=os.getenv("QDRANT_API_KEY"),
    )

    collection_name = "textbook_chunks"

    # Check if collection already exists
    collections = client.get_collections().collections
    if any(c.name == collection_name for c in collections):
        print(f"✓ Collection '{collection_name}' already exists")
        info = client.get_collection(collection_name)
        print(f"  Vectors count: {info.vectors_count}")
        return

    # Create collection with 384-dim vectors (all-MiniLM-L6-v2)
    client.create_collection(
        collection_name=collection_name,
        vectors_config=VectorParams(
            size=384,
            distance=Distance.COSINE,
        ),
    )

    # Create payload indexes for efficient filtering
    client.create_payload_index(collection_name, "chapter_slug", PayloadSchemaType.KEYWORD)
    client.create_payload_index(collection_name, "module", PayloadSchemaType.KEYWORD)

    print(f"Created collection '{collection_name}' with 384-dim cosine vectors")
    print("   Payload indexes: chapter_slug, module")


if __name__ == "__main__":
    init_collection()
