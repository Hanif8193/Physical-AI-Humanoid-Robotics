"""
Translate query endpoint for Vercel - Urdu to English translation for RAG embedding
Uses Groq to translate Urdu queries to English before embedding
"""
from http.server import BaseHTTPRequestHandler
import json
import os
import urllib.request
import urllib.error


def translate_with_groq(text: str, groq_key: str, source_lang: str = "Urdu", target_lang: str = "English") -> str:
    """Translate text using Groq API"""
    # Detect if text contains Urdu characters
    urdu_chars = any('\u0600' <= char <= '\u06FF' for char in text)

    if not urdu_chars and source_lang == "Urdu":
        return text

    prompt = f"Translate the following {source_lang} text to {target_lang}. Provide ONLY the translation, no explanations:\n\n{text}"

    payload = {
        "model": "llama-3.3-70b-versatile",
        "messages": [
            {"role": "system", "content": f"You are a professional translator. Translate {source_lang} to {target_lang} accurately."},
            {"role": "user", "content": prompt}
        ],
        "max_tokens": 500
    }

    req = urllib.request.Request(
        "https://api.groq.com/openai/v1/chat/completions",
        data=json.dumps(payload).encode('utf-8'),
        headers={
            "Authorization": f"Bearer {groq_key}",
            "Content-Type": "application/json"
        }
    )

    try:
        with urllib.request.urlopen(req, timeout=15) as response:
            result = json.loads(response.read().decode('utf-8'))
            return result["choices"][0]["message"]["content"].strip()
    except Exception as e:
        print(f"Translation error: {e}")
        return text


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
            content_length = int(self.headers.get('Content-Length', 0))
            body = self.rfile.read(content_length).decode('utf-8')
            data = json.loads(body) if body else {}

            text = data.get('text', '')

            if not text:
                self.send_response(400)
                self.send_header('Content-Type', 'application/json')
                self.send_header('Access-Control-Allow-Origin', '*')
                self.end_headers()
                self.wfile.write(json.dumps({"error": "Text cannot be empty"}).encode())
                return

            groq_key = os.getenv("GROQ_API_KEY")
            if not groq_key:
                self.send_response(500)
                self.send_header('Content-Type', 'application/json')
                self.send_header('Access-Control-Allow-Origin', '*')
                self.end_headers()
                self.wfile.write(json.dumps({"error": "GROQ_API_KEY not configured"}).encode())
                return

            translated = translate_with_groq(text, groq_key, source_lang="Urdu", target_lang="English")

            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            self.wfile.write(json.dumps({"translated": translated}).encode())

        except Exception as e:
            print(f"Error: {e}")
            self.send_response(500)
            self.send_header('Content-Type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            self.wfile.write(json.dumps({
                "translated": data.get('text', ''),
                "error": str(e)
            }).encode())
