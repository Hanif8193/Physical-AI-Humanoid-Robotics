"""Chat endpoint for Vercel"""
from http.server import BaseHTTPRequestHandler
import json
import os
import urllib.request
import urllib.error

class handler(BaseHTTPRequestHandler):
    def do_POST(self):
        try:
            # Read request body
            content_length = int(self.headers.get('Content-Length', 0))
            body = self.rfile.read(content_length).decode('utf-8')
            data = json.loads(body) if body else {}

            query = data.get('query', '').strip()
            if not query:
                self.send_error_response(400, "Query cannot be empty")
                return

            # Call Groq API
            groq_api_key = os.getenv("GROQ_API_KEY")
            if not groq_api_key:
                self.send_error_response(500, "API key not configured")
                return

            groq_payload = {
                "model": "llama-3.3-70b-versatile",
                "messages": [
                    {"role": "system", "content": "You are an expert on Physical AI and Humanoid Robotics. Provide helpful, technical answers."},
                    {"role": "user", "content": query}
                ],
                "max_tokens": 500
            }

            req = urllib.request.Request(
                "https://api.groq.com/openai/v1/chat/completions",
                data=json.dumps(groq_payload).encode('utf-8'),
                headers={
                    "Authorization": f"Bearer {groq_api_key}",
                    "Content-Type": "application/json"
                }
            )

            with urllib.request.urlopen(req, timeout=30) as response:
                result = json.loads(response.read().decode('utf-8'))
                response_text = result["choices"][0]["message"]["content"]

            # Send success response
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
            self.send_header('Access-Control-Allow-Headers', '*')
            self.end_headers()

            response_data = {
                "response": response_text,
                "citations": []
            }
            self.wfile.write(json.dumps(response_data).encode())

        except Exception as e:
            print(f"Error in chat: {str(e)}")
            self.send_error_response(500, f"Error: {str(e)}")

    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', '*')
        self.end_headers()

    def send_error_response(self, code, message):
        self.send_response(code)
        self.send_header('Content-type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        self.wfile.write(json.dumps({"error": message}).encode())
