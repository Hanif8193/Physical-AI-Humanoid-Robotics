"""Authentication endpoints (Better-Auth compatible)."""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, EmailStr
import hashlib
import secrets
from datetime import datetime, timedelta

router = APIRouter()

# In-memory store for demo (replace with Neon Postgres in production)
_users: dict[str, dict] = {}
_sessions: dict[str, dict] = {}


def hash_password(password: str) -> str:
    """Simple password hash (use bcrypt in production)."""
    return hashlib.sha256(password.encode()).hexdigest()


class RegisterRequest(BaseModel):
    email: EmailStr
    password: str
    name: str | None = None


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class AuthResponse(BaseModel):
    user_id: str
    email: str
    session_token: str
    expires_at: str


@router.post("/register", response_model=AuthResponse, status_code=201)
async def register(request: RegisterRequest):
    """Register a new user."""
    if len(request.password) < 8:
        raise HTTPException(status_code=422, detail="Password must be at least 8 characters")

    if request.email in _users:
        raise HTTPException(status_code=409, detail="Email already registered")

    user_id = secrets.token_hex(16)
    _users[request.email] = {
        "id": user_id,
        "email": request.email,
        "name": request.name,
        "password_hash": hash_password(request.password),
        "created_at": datetime.utcnow().isoformat(),
    }

    # Create session
    token = secrets.token_urlsafe(32)
    expires_at = datetime.utcnow() + timedelta(days=7)
    _sessions[token] = {"user_id": user_id, "expires_at": expires_at}

    return AuthResponse(
        user_id=user_id,
        email=request.email,
        session_token=token,
        expires_at=expires_at.isoformat(),
    )


@router.post("/login", response_model=AuthResponse)
async def login(request: LoginRequest):
    """Login with email and password."""
    user = _users.get(request.email)
    if not user or user["password_hash"] != hash_password(request.password):
        raise HTTPException(status_code=401, detail="Invalid email or password")

    # Create new session
    token = secrets.token_urlsafe(32)
    expires_at = datetime.utcnow() + timedelta(days=7)
    _sessions[token] = {"user_id": user["id"], "expires_at": expires_at}

    return AuthResponse(
        user_id=user["id"],
        email=request.email,
        session_token=token,
        expires_at=expires_at.isoformat(),
    )
