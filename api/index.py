"""Root endpoint for Vercel"""
from http.server import BaseHTTPRequestHandler
import json


class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header('Content-Type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()

        response = {
            "status": "ok",
            "message": "🎉 Backend is running on Vercel! 🎉",
            "version": "2.0.0",
            "endpoints": [
                "/health",
                "/chat",
                "/chat/chapter/{slug}",
                "/translate/query",
                "/translate/message"
            ]
        }

        self.wfile.write(json.dumps(response).encode())
        return
