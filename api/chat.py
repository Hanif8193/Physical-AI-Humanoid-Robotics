"""
RAG Chat endpoint for Vercel - Lightweight version using OpenAI embeddings API
No PyTorch dependency - uses cloud embeddings instead of local sentence-transformers
"""
import json
import os
import urllib.request
import urllib.error
from typing import Optional


def get_openai_embedding(text: str, api_key: str) -> list:
    """Get embedding from OpenAI API"""
    payload = {
        "input": text,
        "model": "text-embedding-3-small"
    }

    req = urllib.request.Request(
        "https://api.openai.com/v1/embeddings",
        data=json.dumps(payload).encode('utf-8'),
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
    )

    with urllib.request.urlopen(req, timeout=10) as response:
        result = json.loads(response.read().decode('utf-8'))
        return result["data"][0]["embedding"]


def search_qdrant(query_vector: list, chapter_slug: Optional[str] = None,
                  qdrant_url: str = "", qdrant_key: str = "", limit: int = 5) -> list:
    """Search Qdrant vector database"""
    payload = {
        "vector": query_vector,
        "limit": limit,
        "with_payload": True
    }

    if chapter_slug:
        payload["filter"] = {
            "must": [
                {
                    "key": "chapter_slug",
                    "match": {"value": chapter_slug}
                }
            ]
        }

    headers = {
        "Content-Type": "application/json"
    }
    if qdrant_key:
        headers["api-key"] = qdrant_key

    req = urllib.request.Request(
        f"{qdrant_url}/collections/textbook_chunks/points/query",
        data=json.dumps(payload).encode('utf-8'),
        headers=headers
    )

    try:
        with urllib.request.urlopen(req, timeout=10) as response:
            result = json.loads(response.read().decode('utf-8'))
            return result.get("result", {}).get("points", [])
    except Exception as e:
        print(f"Qdrant error: {e}")
        return []


def stream_groq_response(context: str, query: str, groq_key: str):
    """Stream response from Groq with citations"""
    system_prompt = f"""You are an expert assistant for the "Physical AI & Humanoid Robotics" textbook.

CRITICAL RULES:
1. You MUST base every answer on the retrieved context below.
2. You MUST include at least one citation in the format [Chapter X, Section Y].
3. If you cannot find relevant context, respond: "I cannot find information about that in this textbook."
4. NEVER make up information not present in the retrieved context.
5. Keep answers focused and technical.

Retrieved context:
{context}"""

    payload = {
        "model": "llama-3.3-70b-versatile",
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": query}
        ],
        "stream": False,  # Vercel serverless doesn't support streaming well
        "max_tokens": 800
    }

    req = urllib.request.Request(
        "https://api.groq.com/openai/v1/chat/completions",
        data=json.dumps(payload).encode('utf-8'),
        headers={
            "Authorization": f"Bearer {groq_key}",
            "Content-Type": "application/json"
        }
    )

    with urllib.request.urlopen(req, timeout=30) as response:
        result = json.loads(response.read().decode('utf-8'))
        return result["choices"][0]["message"]["content"]


def handler(request):
    """Main handler for Vercel serverless function"""
    # Handle CORS preflight
    if request.get('method') == 'OPTIONS':
        return {
            'statusCode': 200,
            'headers': {
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Methods': 'GET, POST, OPTIONS',
                'Access-Control-Allow-Headers': '*',
            },
            'body': ''
        }

    try:
        # Parse request
        body = request.get('body', '{}')
        if isinstance(body, bytes):
            body = body.decode('utf-8')
        data = json.loads(body)

        query = data.get('query', '').strip()
        selected_context = data.get('selected_context', '')

        # Get path to extract chapter slug if this is /chat/chapter/{slug}
        path = request.get('path', '')
        chapter_slug = None
        if '/chapter/' in path:
            parts = path.split('/chapter/')
            if len(parts) > 1:
                chapter_slug = parts[1].strip('/')

        if not query:
            return {
                'statusCode': 400,
                'headers': {
                    'Content-Type': 'application/json',
                    'Access-Control-Allow-Origin': '*',
                },
                'body': json.dumps({"error": "Query cannot be empty"})
            }

        # Get environment variables
        openai_key = os.getenv("OPENAI_API_KEY")
        groq_key = os.getenv("GROQ_API_KEY")
        qdrant_url = os.getenv("QDRANT_URL", "")
        qdrant_key = os.getenv("QDRANT_API_KEY", "")

        if not groq_key:
            return {
                'statusCode': 500,
                'headers': {
                    'Content-Type': 'application/json',
                    'Access-Control-Allow-Origin': '*',
                },
                'body': json.dumps({"error": "GROQ_API_KEY not configured"})
            }

        # Build query text with context if provided
        query_text = query
        if selected_context:
            query_text = f"Context: {selected_context}\n\nQuestion: {query}"

        # Get embedding
        if openai_key and qdrant_url:
            try:
                query_vector = get_openai_embedding(query_text, openai_key)

                # Search Qdrant
                results = search_qdrant(query_vector, chapter_slug, qdrant_url, qdrant_key, limit=5)

                if not results:
                    response_text = "I cannot find relevant information in this textbook. The chapters may not be ingested yet."
                    citations = []
                else:
                    # Build context from results
                    context_parts = []
                    citations = []

                    for i, hit in enumerate(results):
                        payload = hit.get("payload", {})
                        chapter = payload.get("chapter_slug", "unknown")
                        section = payload.get("section", "unknown")
                        text = payload.get("text", "")

                        context_parts.append(f"[{i+1}] Chapter: {chapter}, Section: {section}\n{text}")
                        citations.append({
                            "chapter_slug": chapter,
                            "section": section,
                            "excerpt": text[:200] + "..." if len(text) > 200 else text
                        })

                    context = "\n\n---\n\n".join(context_parts)

                    # Generate response
                    response_text = stream_groq_response(context, query, groq_key)

                    # Add citation footer if response doesn't have citations
                    if not any(f"[Chapter" in response_text or f"[{i+1}]" in response_text for i in range(len(citations))):
                        footer = "\n\n*Sources: " + ", ".join(
                            f"[{c['chapter_slug']}, {c['section']}]" for c in citations[:3]
                        ) + "*"
                        response_text += footer

            except Exception as e:
                # Fallback to basic chat if RAG fails
                print(f"RAG error: {e}")
                response_text = stream_groq_response("", query, groq_key)
                citations = []
        else:
            # No OpenAI key or Qdrant - fallback to basic chat
            response_text = stream_groq_response("", query, groq_key)
            citations = []

        # Return NDJSON format expected by frontend (streaming-like)
        events = []

        # Send response as chunk event
        events.append(json.dumps({"type": "chunk", "content": response_text, "citations": []}))

        # Send citations event
        events.append(json.dumps({"type": "citation", "content": "", "citations": citations}))

        # Send done event
        events.append(json.dumps({"type": "done", "content": "", "citations": citations}))

        # Join with newlines to create NDJSON
        ndjson_body = "\n".join(events) + "\n"

        return {
            'statusCode': 200,
            'headers': {
                'Content-Type': 'application/x-ndjson',
                'Access-Control-Allow-Origin': '*',
            },
            'body': ndjson_body
        }

    except Exception as e:
        print(f"Error: {e}")
        # Return error in NDJSON format
        error_msg = "I encountered an error processing your request. Please try again."
        events = [
            json.dumps({"type": "chunk", "content": error_msg, "citations": []}),
            json.dumps({"type": "done", "content": "", "citations": []})
        ]
        return {
            'statusCode': 200,  # Still 200 so frontend can parse the error message
            'headers': {
                'Content-Type': 'application/x-ndjson',
                'Access-Control-Allow-Origin': '*',
            },
            'body': "\n".join(events) + "\n"
        }
