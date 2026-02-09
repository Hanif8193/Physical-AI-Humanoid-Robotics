"""Health check endpoint for Vercel"""
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
            "status": "healthy",
            "platform": "vercel"
        })
    }
