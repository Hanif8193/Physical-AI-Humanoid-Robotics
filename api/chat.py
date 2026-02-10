"""
RAG Chat endpoint for Vercel - Lightweight version using OpenAI embeddings API
No PyTorch dependency - uses cloud embeddings instead of local sentence-transformers
"""
from http.server import BaseHTTPRequestHandler
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
    """Get response from Groq with citations"""
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
        "stream": False,
        "max_tokens": 800
    }

    req = urllib.request.Request(
        "https://api.groq.com/openai/v1/chat/completions",
        data=json.dumps(payload).encode('utf-8'),
        headers={
            "Authorization": f"Bearer {groq_key}",
            "Content-Type": "application/json",
            "User-Agent": "Mozilla/5.0 (compatible; Physical-AI-Bot/1.0)"
        }
    )

    with urllib.request.urlopen(req, timeout=30) as response:
        result = json.loads(response.read().decode('utf-8'))
        return result["choices"][0]["message"]["content"]


class handler(BaseHTTPRequestHandler):
    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', '*')
        self.end_headers()
        return

    def do_POST(self):
        try:
            # Read request body
            content_length = int(self.headers.get('Content-Length', 0))
            body = self.rfile.read(content_length).decode('utf-8')
            data = json.loads(body) if body else {}

            query = data.get('query', '').strip()
            selected_context = data.get('selected_context', '')

            # Extract chapter slug from path if present
            chapter_slug = None
            if '/chapter/' in self.path:
                parts = self.path.split('/chapter/')
                if len(parts) > 1:
                    chapter_slug = parts[1].strip('/')

            if not query:
                self.send_response(400)
                self.send_header('Content-Type', 'application/json')
                self.send_header('Access-Control-Allow-Origin', '*')
                self.end_headers()
                self.wfile.write(json.dumps({"error": "Query cannot be empty"}).encode())
                return

            # Get environment variables
            groq_key = os.getenv("GROQ_API_KEY")
            openai_key = os.getenv("OPENAI_API_KEY")
            qdrant_url = os.getenv("QDRANT_URL", "")
            qdrant_key = os.getenv("QDRANT_API_KEY", "")

            if not groq_key:
                self.send_response(500)
                self.send_header('Content-Type', 'application/json')
                self.send_header('Access-Control-Allow-Origin', '*')
                self.end_headers()
                self.wfile.write(json.dumps({"error": "GROQ_API_KEY not configured"}).encode())
                return

            # Build query text with context if provided
            query_text = query
            if selected_context:
                query_text = f"Context: {selected_context}\n\nQuestion: {query}"

            # Get embedding and search
            response_text = ""
            citations = []

            if openai_key and qdrant_url:
                try:
                    query_vector = get_openai_embedding(query_text, openai_key)
                    results = search_qdrant(query_vector, chapter_slug, qdrant_url, qdrant_key, limit=5)

                    if not results:
                        response_text = "I cannot find relevant information in this textbook. The chapters may not be ingested yet."
                    else:
                        # Build context from results
                        context_parts = []
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
                        response_text = stream_groq_response(context, query, groq_key)

                        # Add citation footer if response doesn't have citations
                        if not any(f"[Chapter" in response_text or f"[{i+1}]" in response_text for i in range(len(citations))):
                            footer = "\n\n*Sources: " + ", ".join(
                                f"[{c['chapter_slug']}, {c['section']}]" for c in citations[:3]
                            ) + "*"
                            response_text += footer

                except Exception as e:
                    print(f"RAG error: {e}")
                    response_text = stream_groq_response("", query, groq_key)
            else:
                # No OpenAI/Qdrant - fallback to basic chat
                response_text = stream_groq_response("", query, groq_key)

            # Return NDJSON format
            events = [
                json.dumps({"type": "chunk", "content": response_text, "citations": []}),
                json.dumps({"type": "citation", "content": "", "citations": citations}),
                json.dumps({"type": "done", "content": "", "citations": citations})
            ]

            self.send_response(200)
            self.send_header('Content-Type', 'application/x-ndjson')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            self.wfile.write(("\n".join(events) + "\n").encode())

        except Exception as e:
            print(f"Error: {e}")
            error_events = [
                json.dumps({"type": "chunk", "content": "I encountered an error processing your request. Please try again.", "citations": []}),
                json.dumps({"type": "done", "content": "", "citations": []})
            ]

            self.send_response(200)
            self.send_header('Content-Type', 'application/x-ndjson')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            self.wfile.write(("\n".join(error_events) + "\n").encode())
