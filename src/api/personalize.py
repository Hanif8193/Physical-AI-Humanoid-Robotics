"""Chapter Personalization API endpoint."""
from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from groq import AsyncGroq
from ..config import settings

router = APIRouter()

PERSONALIZATION_SYSTEM_PROMPT = """You are an expert robotics educator adapting textbook content for a specific learner.

Learner profile:
- Software background: {software_background}
- Hardware background: {hardware_background}
- Experience level: {experience_level}

Adapt the following textbook chapter content based on this profile:

1. For BEGINNERS: Simplify jargon, add more analogies, slow down pacing
2. For INTERMEDIATE: Add practical tips, link to real-world use cases
3. For EXPERT: Add advanced insights, edge cases, performance tips
4. If learner has NO GPU: Emphasize cloud alternatives for all GPU labs
5. If learner has RTX: Emphasize local simulation labs
6. If learner knows Python: Include more code examples
7. Preserve the overall structure but adapt language and depth

Output ONLY the adapted chapter content in the same format."""


class PersonalizeRequest(BaseModel):
    chapter_slug: str
    user_id: str
    content: str  # Original chapter content


class PersonalizeResponse(BaseModel):
    chapter_slug: str
    personalized_content: str
    adaptations_applied: list[str]


# Mock user profile lookup (replace with DB query)
MOCK_PROFILES = {
    "default": {
        "software_background": "Python developer",
        "hardware_background": "No GPU available",
        "experience_level": "beginner",
    }
}


@router.post("/personalize", response_model=PersonalizeResponse)
async def personalize_chapter(request: PersonalizeRequest):
    """Adapt chapter content based on authenticated user's profile."""
    # TODO: Replace with actual DB lookup via user_id
    profile = MOCK_PROFILES.get(request.user_id, MOCK_PROFILES["default"])

    if not profile:
        raise HTTPException(
            status_code=422,
            detail="User profile incomplete. Please complete your profile before personalizing.",
        )

    client = AsyncGroq(api_key=settings.GROQ_API_KEY)

    system_prompt = PERSONALIZATION_SYSTEM_PROMPT.format(**profile)

    response = await client.chat.completions.create(
        model=settings.CHAT_MODEL,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": request.content},
        ],
        max_tokens=4000,
    )

    adapted_content = response.choices[0].message.content

    # Determine what adaptations were applied
    adaptations = []
    if profile["experience_level"] == "beginner":
        adaptations.append("Simplified for beginner level")
    elif profile["experience_level"] == "expert":
        adaptations.append("Enhanced with expert insights")
    if "no gpu" in profile["hardware_background"].lower():
        adaptations.append("Emphasized cloud alternatives for GPU labs")
    if "python" in profile["software_background"].lower():
        adaptations.append("Added Python-focused examples")

    return PersonalizeResponse(
        chapter_slug=request.chapter_slug,
        personalized_content=adapted_content,
        adaptations_applied=adaptations or ["General adaptation applied"],
    )
