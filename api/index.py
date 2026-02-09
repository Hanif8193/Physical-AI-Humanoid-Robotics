"""Root endpoint for Vercel"""
import json

def handler(request):
    return {
        'statusCode': 200,
        'headers': {
            'Content-Type': 'application/json',
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Methods': 'GET, POST, OPTIONS',
            'Access-Control-Allow-Headers': '*',
        },
        'body': json.dumps({
            "status": "ok",
            "message": "RAG Chatbot API is running",
            "version": "2.0.0"
        })
    }
