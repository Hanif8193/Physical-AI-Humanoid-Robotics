"""Application configuration from environment variables."""
from pydantic_settings import BaseSettings
from typing import List


class Settings(BaseSettings):
    DATABASE_URL: str = "postgresql://localhost/textbook"
    QDRANT_URL: str = "http://localhost:6333"
    QDRANT_API_KEY: str = ""
    GROQ_API_KEY: str = ""
    BETTER_AUTH_SECRET: str = "change-me-in-production"
    BETTER_AUTH_URL: str = "http://localhost:8000"
    ADMIN_API_KEY: str = "admin-key"
    ALLOWED_ORIGINS: List[str] = ["http://localhost:3000"]
    QDRANT_COLLECTION: str = "textbook_chunks"
    EMBEDDING_MODEL: str = "all-MiniLM-L6-v2"
    EMBEDDING_DIMS: int = 384
    CHAT_MODEL: str = "llama-3.3-70b-versatile"

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


settings = Settings()
