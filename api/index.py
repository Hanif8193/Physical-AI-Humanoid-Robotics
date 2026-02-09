"""
Vercel-compatible FastAPI backend (simplified)
No PyTorch - uses external APIs instead
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import os

app = FastAPI(title="Physical AI Backend")

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def root():
    return {
        "status": "ok",
        "message": "Physical AI Backend - Vercel Deployment",
        "version": "1.0.0"
    }

@app.get("/health")
def health():
    return {"status": "healthy", "platform": "vercel"}

@app.get("/v1/info")
def info():
    return {
        "service": "Physical AI Backend",
        "deployment": "Vercel Serverless",
        "note": "Lightweight version - ML features use external APIs"
    }

# Vercel serverless handler
from mangum import Mangum
handler = Mangum(app)
