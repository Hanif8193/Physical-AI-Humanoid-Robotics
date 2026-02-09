"""Chat endpoint for Vercel"""
import json
import os
import urllib.request
import urllib.error

def handler(request):
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
        # Parse request body
        body = request.get('body', '{}')
        if isinstance(body, bytes):
            body = body.decode('utf-8')
        data = json.loads(body)

        query = data.get('query', '').strip()
        if not query:
            return {
                'statusCode': 400,
                'headers': {
                    'Content-Type': 'application/json',
                    'Access-Control-Allow-Origin': '*',
                },
                'body': json.dumps({"error": "Query cannot be empty"})
            }

        # Call Groq API
        groq_api_key = os.getenv("GROQ_API_KEY")
        if not groq_api_key:
            return {
                'statusCode': 500,
                'headers': {
                    'Content-Type': 'application/json',
                    'Access-Control-Allow-Origin': '*',
                },
                'body': json.dumps({"error": "API key not configured"})
            }

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

        return {
            'statusCode': 200,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*',
            },
            'body': json.dumps({
                "response": response_text,
                "citations": []
            })
        }

    except Exception as e:
        return {
            'statusCode': 500,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*',
            },
            'body': json.dumps({
                "response": "I encountered an error processing your request. Please try again.",
                "citations": [],
                "error": str(e)
            })
        }
