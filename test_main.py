"""
Minimal FastAPI app for testing Koyeb deployment
"""
from fastapi import FastAPI

app = FastAPI()

@app.get("/")
def root():
    return {"status": "ok", "message": "Minimal test app running"}

@app.get("/health")
def health():
    return {"status": "healthy"}
