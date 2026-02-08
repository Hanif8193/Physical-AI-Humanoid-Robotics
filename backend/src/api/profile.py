"""User Profile API endpoint."""
from fastapi import APIRouter, HTTPException, Header
from pydantic import BaseModel
from typing import Optional

router = APIRouter()

# In-memory store (replace with Neon Postgres)
_profiles: dict[str, dict] = {}


class ProfileRequest(BaseModel):
    software_background: str = ""
    hardware_background: str = ""
    experience_level: str = "beginner"
    preferred_language: str = "en"


class ProfileResponse(BaseModel):
    user_id: str
    updated_at: str


@router.put("/profile", response_model=ProfileResponse)
async def update_profile(
    request: ProfileRequest,
    authorization: Optional[str] = Header(None),
):
    """Create or update user profile for personalization."""
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Authentication required")

    # Validate experience level
    if request.experience_level not in ("beginner", "intermediate", "expert"):
        raise HTTPException(
            status_code=422,
            detail="experience_level must be beginner, intermediate, or expert",
        )

    # Extract user_id from token (simplified)
    token = authorization.replace("Bearer ", "")
    from .auth import _sessions
    session = _sessions.get(token)
    if not session:
        raise HTTPException(status_code=401, detail="Invalid or expired session")

    from datetime import datetime
    user_id = session["user_id"]
    _profiles[user_id] = {
        **request.model_dump(),
        "updated_at": datetime.utcnow().isoformat(),
    }

    return ProfileResponse(
        user_id=user_id,
        updated_at=_profiles[user_id]["updated_at"],
    )
