"""
Vercel-compatible FastAPI backend with RAG
Uses Groq + Qdrant APIs (no PyTorch needed)
"""
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, List
import os
import httpx
from qdrant_client import QdrantClient
from qdrant_client.models import Filter, FieldCondition, MatchValue

app = FastAPI(title="Physical AI Backend")

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize clients
groq_api_key = os.getenv("GROQ_API_KEY")
qdrant_url = os.getenv("QDRANT_URL")
qdrant_api_key = os.getenv("QDRANT_API_KEY")
qdrant_collection = os.getenv("QDRANT_COLLECTION", "textbook_chunks")

qdrant_client = QdrantClient(url=qdrant_url, api_key=qdrant_api_key) if qdrant_url else None


class ChatRequest(BaseModel):
    query: str
    selected_context: Optional[str] = None
    session_id: Optional[str] = None


@app.get("/")
def root():
    return {
        "status": "ok",
        "message": "RAG Chatbot API is running",
        "version": "1.0.0"
    }


@app.get("/health")
def health():
    return {"status": "healthy", "platform": "vercel"}


@app.post("/chat")
@app.post("/chat/chapter/{chapter_slug}")
async def chat(request: ChatRequest, chapter_slug: Optional[str] = None):
    """
    RAG chat endpoint with Groq + Qdrant
    """
    try:
        if not request.query.strip():
            raise HTTPException(status_code=400, detail="Query cannot be empty")

        # For basic response without Qdrant search
        if not qdrant_client:
            # Fallback: Direct Groq call without RAG
            async with httpx.AsyncClient() as client:
                groq_response = await client.post(
                    "https://api.groq.com/openai/v1/chat/completions",
                    headers={
                        "Authorization": f"Bearer {groq_api_key}",
                        "Content-Type": "application/json"
                    },
                    json={
                        "model": "llama-3.3-70b-versatile",
                        "messages": [
                            {"role": "system", "content": "You are an expert on Physical AI and Humanoid Robotics. Provide helpful, technical answers."},
                            {"role": "user", "content": request.query}
                        ],
                        "max_tokens": 500
                    },
                    timeout=30.0
                )

                if groq_response.status_code == 200:
                    result = groq_response.json()
                    response_text = result["choices"][0]["message"]["content"]
                    return {
                        "response": response_text,
                        "citations": []
                    }
                else:
                    return {
                        "response": "I'm having trouble processing your request. Please try again.",
                        "citations": []
                    }

        # With Qdrant: Do RAG
        # TODO: Implement full RAG with proper embeddings
        # For now, fallback to direct Groq
        async with httpx.AsyncClient() as client:
            groq_response = await client.post(
                "https://api.groq.com/openai/v1/chat/completions",
                headers={
                    "Authorization": f"Bearer {groq_api_key}",
                    "Content-Type": "application/json"
                },
                json={
                    "model": "llama-3.3-70b-versatile",
                    "messages": [
                        {"role": "system", "content": "You are an expert on Physical AI and Humanoid Robotics from the textbook. Provide helpful, technical answers based on the course material."},
                        {"role": "user", "content": request.query}
                    ],
                    "max_tokens": 500
                },
                timeout=30.0
            )

            if groq_response.status_code == 200:
                result = groq_response.json()
                response_text = result["choices"][0]["message"]["content"]
                return {
                    "response": response_text,
                    "citations": []
                }
    except Exception as e:
        print(f"Error in chat: {str(e)}")
        return {
            "response": "I encountered an error processing your request. Please try again.",
            "citations": []
        }


# Vercel serverless handler
from mangum import Mangum
handler = Mangum(app)
