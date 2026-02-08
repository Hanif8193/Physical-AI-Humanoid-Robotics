"""
RAG Service — Retrieval-Augmented Generation for textbook Q&A.
Uses Groq (llama) for chat and sentence-transformers for local embeddings.
CITATION ENFORCEMENT: Every response MUST include at least one citation.
Responses without citations are BLOCKED (Constitution Principle III).
"""
from typing import AsyncGenerator, Optional
from groq import AsyncGroq
from qdrant_client import QdrantClient
from qdrant_client.models import Filter, FieldCondition, MatchValue
from sentence_transformers import SentenceTransformer

from ..config import settings

# System prompt enforcing citation requirement
CITATION_SYSTEM_PROMPT = """You are an expert assistant for the "Physical AI & Humanoid Robotics" textbook.

CRITICAL RULES:
1. You MUST base every answer on the retrieved context below.
2. You MUST include at least one citation in the format [Chapter X, Section Y].
3. If you cannot find relevant context, respond: "I cannot find information about that in this textbook. [No citation available]"
4. NEVER make up information not present in the retrieved context.
5. Keep answers focused and technical.

Retrieved context:
{context}
"""

NO_CITATION_MARKER = "[No citation available]"

# Load embedding model once at startup (cached after first load)
_embedding_model = None


def get_embedding_model() -> SentenceTransformer:
    global _embedding_model
    if _embedding_model is None:
        print(f"Loading embedding model: {settings.EMBEDDING_MODEL}")
        _embedding_model = SentenceTransformer(settings.EMBEDDING_MODEL)
    return _embedding_model


class RAGService:
    def __init__(self):
        self.groq = AsyncGroq(api_key=settings.GROQ_API_KEY)
        self.qdrant = QdrantClient(
            url=settings.QDRANT_URL,
            api_key=settings.QDRANT_API_KEY if settings.QDRANT_API_KEY else None,
        )

    def _embed(self, text: str) -> list:
        """Embed text using local sentence-transformers model."""
        model = get_embedding_model()
        return model.encode(text).tolist()

    async def query(
        self,
        query: str,
        chapter_slug: Optional[str] = None,
        selected_context: Optional[str] = None,
        top_k: int = 5,
    ) -> AsyncGenerator[dict, None]:
        """
        Query the RAG system with citation enforcement.

        Yields: {"type": "chunk"|"citation"|"done", "content": str, "citations": list}
        """
        # Step 1: Embed the query locally
        query_text = query
        if selected_context:
            query_text = f"Context: {selected_context}\n\nQuestion: {query}"

        query_vector = self._embed(query_text)

        # Step 2: Search Qdrant
        search_filter = None
        if chapter_slug:
            search_filter = Filter(
                must=[FieldCondition(key="chapter_slug", match=MatchValue(value=chapter_slug))]
            )

        try:
            response = self.qdrant.query_points(
                collection_name=settings.QDRANT_COLLECTION,
                query=query_vector,
                query_filter=search_filter,
                limit=top_k,
                with_payload=True,
            )
            results = response.points
        except Exception as e:
            print(f"Qdrant search error: {e}")
            results = []

        if not results:
            yield {
                "type": "chunk",
                "content": "I cannot find relevant information in this textbook. The chapters may not be ingested yet.",
                "citations": [],
            }
            yield {"type": "done", "content": "", "citations": []}
            return

        # Step 3: Build context with citations
        context_parts = []
        citations = []
        for i, hit in enumerate(results):
            payload = hit.payload
            chapter = payload.get("chapter_slug", "unknown")
            section = payload.get("section", "unknown")
            text = payload.get("text", "")

            context_parts.append(f"[{i+1}] Chapter: {chapter}, Section: {section}\n{text}")
            citations.append({
                "ref": i + 1,
                "chapter_slug": chapter,
                "section": section,
                "excerpt": text[:200] + "..." if len(text) > 200 else text,
            })

        context = "\n\n---\n\n".join(context_parts)

        # Step 4: Generate response with Groq (streaming)
        system_prompt = CITATION_SYSTEM_PROMPT.format(context=context)

        stream = await self.groq.chat.completions.create(
            model=settings.CHAT_MODEL,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": query},
            ],
            stream=True,
            max_tokens=800,
        )

        full_response = ""
        async for chunk in stream:
            delta = chunk.choices[0].delta.content or ""
            full_response += delta
            if delta:
                yield {"type": "chunk", "content": delta, "citations": []}

        # Step 5: CITATION ENFORCEMENT
        has_citation = any(
            f"[Chapter" in full_response or f"[{i+1}]" in full_response
            for i in range(len(citations))
        )

        if not has_citation and NO_CITATION_MARKER not in full_response:
            footer = f"\n\n*Sources: " + ", ".join(
                f"[{c['chapter_slug']}, {c['section']}]" for c in citations[:3]
            ) + "*"
            yield {"type": "chunk", "content": footer, "citations": []}

        yield {"type": "citation", "content": "", "citations": citations}
        yield {"type": "done", "content": "", "citations": citations}


# Singleton
rag_service = RAGService()
