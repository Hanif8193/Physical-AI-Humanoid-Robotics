"""
RAG Chat endpoint for Vercel - Reads chapter content from chapters.json
No external dependencies - uses local chapter database
"""
from http.server import BaseHTTPRequestHandler
import json
import os
import urllib.request
import urllib.error
from typing import Optional


def load_chapters():
    """Load chapter content from chapters.json"""
    try:
        json_path = os.path.join(os.path.dirname(__file__), 'chapters.json')
        with open(json_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
            return data.get('chapters', [])
    except Exception as e:
        print(f"Error loading chapters: {e}")
        return []


def search_chapters(query: str, chapter_slug: Optional[str] = None) -> dict:
    """Search chapters for relevant information"""
    chapters = load_chapters()

    if not chapters:
        return {
            "found": False,
            "message": "Chapter data not available",
            "citations": []
        }

    query_lower = query.lower()

    # Check for chapter-specific queries
    if chapter_slug:
        chapter = next((c for c in chapters if c['slug'] == chapter_slug), None)
        if chapter:
            return {
                "found": True,
                "content": f"Chapter {chapter['number']}: {chapter['title']}\n\n{chapter['summary']}\n\nKey concepts:\n" +
                          "\n".join(f"• {concept}" for concept in chapter['key_concepts']),
                "citations": [{
                    "chapter_slug": chapter['slug'],
                    "section": "Overview",
                    "excerpt": chapter['summary'][:200]
                }]
            }

    # Check for general queries about chapters
    if 'how many chapter' in query_lower or 'number of chapter' in query_lower:
        return {
            "found": True,
            "content": f"This textbook contains {len(chapters)} chapters on Physical AI & Humanoid Robotics:\n\n" +
                      "\n".join(f"{i+1}. {ch['title']}" for i, ch in enumerate(chapters)),
            "citations": [{
                "chapter_slug": "metadata",
                "section": "Table of Contents",
                "excerpt": "6 chapters total"
            }]
        }

    # Check for summary requests
    if 'summary' in query_lower or 'summarize' in query_lower:
        # Extract chapter number if present
        chapter_num = None
        for i in range(1, 7):
            if f'chapter {i}' in query_lower or f'ch{i}' in query_lower or f'ch0{i}' in query_lower:
                chapter_num = i
                break

        if chapter_num:
            chapter = chapters[chapter_num - 1]
            return {
                "found": True,
                "content": f"Chapter {chapter['number']}: {chapter['title']}\n\n{chapter['summary']}",
                "citations": [{
                    "chapter_slug": chapter['slug'],
                    "section": "Summary",
                    "excerpt": chapter['summary'][:200]
                }]
            }

    # Search through all chapters for relevant keywords
    results = []
    for chapter in chapters:
        score = 0
        matches = []

        # Search in title
        if any(word in chapter['title'].lower() for word in query_lower.split()):
            score += 10
            matches.append(('title', chapter['title']))

        # Search in summary
        if any(word in chapter['summary'].lower() for word in query_lower.split()):
            score += 5
            matches.append(('summary', chapter['summary']))

        # Search in key concepts
        for concept in chapter['key_concepts']:
            if any(word in concept.lower() for word in query_lower.split()):
                score += 3
                matches.append(('concept', concept))

        if score > 0:
            results.append({
                'chapter': chapter,
                'score': score,
                'matches': matches
            })

    # Sort by score
    results.sort(key=lambda x: x['score'], reverse=True)

    if results:
        best = results[0]
        chapter = best['chapter']

        # Build response from matches
        content = f"[Chapter {chapter['number']}, {chapter['title']}]\n\n"

        if any(m[0] == 'summary' for m in best['matches']):
            content += chapter['summary'] + "\n\n"

        if any(m[0] == 'concept' for m in best['matches']):
            relevant_concepts = [m[1] for m in best['matches'] if m[0] == 'concept']
            if relevant_concepts:
                content += "Key concepts:\n" + "\n".join(f"• {c}" for c in relevant_concepts[:3])

        return {
            "found": True,
            "content": content,
            "citations": [{
                "chapter_slug": chapter['slug'],
                "section": "Content",
                "excerpt": chapter['summary'][:200]
            }]
        }

    return {
        "found": False,
        "message": "I cannot find specific information about that in this textbook. Try asking about specific chapters (1-6) or topics like 'Physical AI', 'ROS 2', 'simulation', 'Isaac platform', 'VLA', or the capstone project.",
        "citations": []
    }


def groq_response(context: str, query: str, groq_key: str):
    """Get response from Groq with context"""
    system_prompt = f"""You are an expert assistant for the "Physical AI & Humanoid Robotics" textbook.

CRITICAL RULES:
1. Base your answer on the context below
2. Include chapter references from the context
3. Be concise and technical
4. If the context is insufficient, acknowledge it

Context:
{context}"""

    payload = {
        "model": "llama-3.3-70b-versatile",
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": query}
        ],
        "stream": False,
        "max_tokens": 500
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

    try:
        with urllib.request.urlopen(req, timeout=30) as response:
            result = json.loads(response.read().decode('utf-8'))
            return result["choices"][0]["message"]["content"]
    except Exception as e:
        print(f"Groq API error: {e}")
        # Fallback to context if Groq fails
        return context


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

            # Get GROQ API key
            groq_key = (os.getenv("GROQ_API_KEY") or '').strip()
            if not groq_key:
                self.send_response(500)
                self.send_header('Content-Type', 'application/json')
                self.send_header('Access-Control-Allow-Origin', '*')
                self.end_headers()
                self.wfile.write(json.dumps({"error": "GROQ_API_KEY not configured"}).encode())
                return

            # Search chapters for relevant content
            search_result = search_chapters(query, chapter_slug)

            if search_result['found']:
                # Generate response using Groq with chapter context
                context = search_result['content']
                if selected_context:
                    context = f"Selected text: {selected_context}\n\n{context}"

                response_text = groq_response(context, query, groq_key)
                citations = search_result.get('citations', [])
            else:
                # No relevant chapter content found
                response_text = search_result.get('message',
                    "I cannot find information about that in this textbook. Try asking about chapters 1-6 or topics like Physical AI, ROS 2, simulation, Isaac platform, or VLA.")
                citations = []

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
