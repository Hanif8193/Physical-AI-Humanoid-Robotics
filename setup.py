from setuptools import setup, find_packages

setup(
    name="physical-ai-backend",
    version="1.0.0",
    description="Physical AI & Humanoid Robotics Textbook Backend",
    packages=find_packages(),
    python_requires=">=3.11",
    install_requires=[
        "fastapi==0.115.0",
        "uvicorn[standard]==0.30.6",
        "asyncpg==0.29.0",
        "sqlalchemy[asyncio]==2.0.35",
        "groq==0.11.0",
        "qdrant-client==1.11.0",
        "sentence-transformers==3.3.1",
        "python-dotenv==1.0.1",
        "pydantic==2.9.0",
        "pydantic-settings==2.5.0",
        "httpx==0.27.2",
        "python-multipart==0.0.12",
        "torch==2.1.0",
    ],
)
