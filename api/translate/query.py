"""
Translate query endpoint for Vercel - Urdu to English translation for RAG embedding
Uses Groq to translate Urdu queries to English before embedding
"""
import json
import os
import urllib.request
import urllib.error


def translate_with_groq(text: str, groq_key: str, source_lang: str = "Urdu", target_lang: str = "English") -> str:
    """Translate text using Groq API"""
    # Detect if text contains Urdu characters
    urdu_chars = any('\u0600' <= char <= '\u06FF' for char in text)

    if not urdu_chars and source_lang == "Urdu":
        # No Urdu detected, return as-is
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
        return text  # Fallback to original text


def handler(request):
    """Translate Urdu query to English for RAG embedding"""
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

        text = data.get('text', '')

        if not text:
            return {
                'statusCode': 400,
                'headers': {
                    'Content-Type': 'application/json',
                    'Access-Control-Allow-Origin': '*',
                },
                'body': json.dumps({"error": "Text cannot be empty"})
            }

        groq_key = os.getenv("GROQ_API_KEY")
        if not groq_key:
            return {
                'statusCode': 500,
                'headers': {
                    'Content-Type': 'application/json',
                    'Access-Control-Allow-Origin': '*',
                },
                'body': json.dumps({"error": "GROQ_API_KEY not configured"})
            }

        translated = translate_with_groq(text, groq_key, source_lang="Urdu", target_lang="English")

        return {
            'statusCode': 200,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*',
            },
            'body': json.dumps({"translated": translated})
        }

    except Exception as e:
        print(f"Error: {e}")
        return {
            'statusCode': 500,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*',
            },
            'body': json.dumps({
                "translated": text,  # Fallback to original
                "error": str(e)
            })
        }
