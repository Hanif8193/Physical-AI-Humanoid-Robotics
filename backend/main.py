"""
Physical AI & Humanoid Robotics Textbook — FastAPI Backend
Provides RAG chat, translation, personalization, and auth endpoints.
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from src.config import settings
from src.api import chat, translate, personalize, auth, profile
from src.middleware.rate_limit import RateLimitMiddleware


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application startup and shutdown."""
    print(f"Physical AI Textbook API starting on {settings.BETTER_AUTH_URL}")
    yield
    print("API shutting down")


app = FastAPI(
    title="Physical AI & Humanoid Robotics — API",
    description="RAG chatbot, translation, personalization, and auth for the AI-native textbook.",
    version="1.0.0",
    lifespan=lifespan,
)

# CORS for Docusaurus frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.add_middleware(RateLimitMiddleware)

# API routes
app.include_router(chat.router, prefix="/v1/chat", tags=["RAG Chat"])
app.include_router(translate.router, prefix="/v1", tags=["Translation"])
app.include_router(personalize.router, prefix="/v1", tags=["Personalization"])
app.include_router(auth.router, prefix="/v1/auth", tags=["Authentication"])
app.include_router(profile.router, prefix="/v1", tags=["User Profile"])


@app.get("/")
async def root():
    return {"name": "Physical AI & Humanoid Robotics API", "version": "1.0.0", "docs": "/docs"}


@app.get("/health")
async def health():
    return {"status": "ok", "version": "1.0.0"}
