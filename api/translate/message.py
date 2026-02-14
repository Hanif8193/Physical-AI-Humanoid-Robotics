"""
Translate message endpoint for Vercel - English to Urdu translation for responses
Uses Groq to translate RAG responses to Urdu for display
"""
from http.server import BaseHTTPRequestHandler
import json
import os
import urllib.request
import urllib.error


def translate_with_groq(text: str, groq_key: str, source_lang: str = "English", target_lang: str = "Urdu") -> str:
    """Translate text using Groq API"""
    prompt = f"Translate the following {source_lang} text to {target_lang}. Maintain any citations in square brackets as-is. Provide ONLY the translation:\n\n{text}"

    payload = {
        "model": "llama-3.3-70b-versatile",
        "messages": [
            {"role": "system", "content": f"You are a professional translator. Translate {source_lang} to {target_lang} accurately while preserving technical terms and citations."},
            {"role": "user", "content": prompt}
        ],
        "max_tokens": 1000
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
        with urllib.request.urlopen(req, timeout=20) as response:
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

            groq_key = (os.getenv("GROQ_API_KEY") or '').strip()
            if not groq_key:
                self.send_response(500)
                self.send_header('Content-Type', 'application/json')
                self.send_header('Access-Control-Allow-Origin', '*')
                self.end_headers()
                self.wfile.write(json.dumps({"error": "GROQ_API_KEY not configured"}).encode())
                return

            translated = translate_with_groq(text, groq_key, source_lang="English", target_lang="Urdu")

            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            self.wfile.write(json.dumps({"translated": translated}, ensure_ascii=False).encode('utf-8'))

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
