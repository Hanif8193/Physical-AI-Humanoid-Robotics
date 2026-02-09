"""
Minimal FastAPI app for testing Koyeb deployment
No dependencies on external services - just works!
"""
import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="Physical AI Backend - Test")

# Simple CORS
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
        "message": "Backend is running!",
        "version": "1.0.0-test"
    }

@app.get("/health")
def health():
    return {"status": "healthy", "port": os.getenv("PORT", "8000")}

@app.get("/test")
def test():
    return {
        "message": "If you see this, Koyeb deployment works!",
        "env_vars_present": {
            "PORT": os.getenv("PORT") is not None,
            "GROQ_API_KEY": os.getenv("GROQ_API_KEY") is not None,
            "DATABASE_URL": os.getenv("DATABASE_URL") is not None,
        }
    }
