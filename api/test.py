"""Test endpoint to debug Groq API calls"""
from http.server import BaseHTTPRequestHandler
import json
import os
import urllib.request
import ssl


class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        try:
            groq_key = os.getenv("GROQ_API_KEY")

            if not groq_key:
                raise Exception("No GROQ_API_KEY found")

            # Test Groq API call with SSL context
            payload = {
                "model": "llama-3.3-70b-versatile",
                "messages": [{"role": "user", "content": "Hello"}],
                "max_tokens": 50
            }

            req = urllib.request.Request(
                "https://api.groq.com/openai/v1/chat/completions",
                data=json.dumps(payload).encode('utf-8'),
                headers={
                    "Authorization": f"Bearer {groq_key}",
                    "Content-Type": "application/json"
                }
            )

            # Create SSL context that doesn't verify certificates (for debugging)
            context = ssl._create_unverified_context()

            with urllib.request.urlopen(req, timeout=30, context=context) as response:
                result = json.loads(response.read().decode('utf-8'))
                message = result["choices"][0]["message"]["content"]

            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            self.wfile.write(json.dumps({
                "status": "success",
                "message": message,
                "groq_key_present": bool(groq_key),
                "groq_key_prefix": groq_key[:10] if groq_key else None
            }).encode())

        except Exception as e:
            import traceback
            self.send_response(500)
            self.send_header('Content-Type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            self.wfile.write(json.dumps({
                "status": "error",
                "error": str(e),
                "error_type": type(e).__name__,
                "traceback": traceback.format_exc(),
                "groq_key_present": bool(os.getenv("GROQ_API_KEY")),
                "groq_key_length": len(os.getenv("GROQ_API_KEY", ""))
            }).encode())
