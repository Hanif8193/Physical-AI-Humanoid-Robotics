"""Urdu Translation API endpoint."""
from fastapi import APIRouter, HTTPException, Request
from pydantic import BaseModel
from groq import AsyncGroq
from ..config import settings

router = APIRouter()

TRANSLATION_SYSTEM_PROMPT = """You are a technical translator specializing in robotics and AI content.
Translate the following text to Urdu, following these rules:

1. Preserve ALL technical terms in English with Urdu transliteration in parentheses:
   - ROS 2 → ROS 2 (روس ٹو)
   - SLAM → SLAM (سلام)
   - LiDAR → LiDAR (لیڈار)
   - URDF → URDF
   - Isaac → Isaac
   - Gazebo → Gazebo
   - Nav2 → Nav2
   - Python → Python
   - ROS → ROS

2. Keep code blocks unchanged (do not translate code).
3. Keep markdown formatting (##, **, etc.) intact.
4. Use formal academic Urdu style.
5. Output ONLY the translated text, nothing else."""


class TranslateRequest(BaseModel):
    chapter_slug: str
    target_language: str = "ur"
    content: str  # Chapter HTML/MDX content to translate


class ChatTranslateRequest(BaseModel):
    text: str


class ChatTranslateResponse(BaseModel):
    translated: str


class TranslateResponse(BaseModel):
    chapter_slug: str
    target_language: str
    translated_content: str
    preserved_terms: list[str]


@router.post("/translate", response_model=TranslateResponse)
async def translate_chapter(request: TranslateRequest):
    """Translate a chapter to Urdu with technical term preservation."""
    if request.target_language != "ur":
        raise HTTPException(status_code=400, detail="Only Urdu (ur) translation is supported")

    if not request.content.strip():
        raise HTTPException(status_code=400, detail="Content cannot be empty")

    client = AsyncGroq(api_key=settings.GROQ_API_KEY)

    response = await client.chat.completions.create(
        model=settings.CHAT_MODEL,
        messages=[
            {"role": "system", "content": TRANSLATION_SYSTEM_PROMPT},
            {"role": "user", "content": request.content},
        ],
        max_tokens=4000,
    )

    translated = response.choices[0].message.content

    # Extract preserved technical terms (simple heuristic)
    preserved = [
        term for term in [
            "ROS 2", "SLAM", "LiDAR", "URDF", "Isaac", "Gazebo",
            "Nav2", "Python", "GPU", "IMU", "VSLAM", "VLA"
        ]
        if term in translated
    ]

    return TranslateResponse(
        chapter_slug=request.chapter_slug,
        target_language="ur",
        translated_content=translated,
        preserved_terms=preserved,
    )


class QueryTranslateRequest(BaseModel):
    text: str


class QueryTranslateResponse(BaseModel):
    translated: str
    was_urdu: bool


@router.post("/translate/query", response_model=QueryTranslateResponse)
async def translate_query_to_english(request: QueryTranslateRequest):
    """Detect Urdu input and translate to English for RAG embedding."""
    # Check if text contains Urdu/Arabic characters
    has_urdu = bool(__import__('re').search(r'[\u0600-\u06FF]', request.text))

    if not has_urdu:
        return QueryTranslateResponse(translated=request.text, was_urdu=False)

    client = AsyncGroq(api_key=settings.GROQ_API_KEY)
    response = await client.chat.completions.create(
        model=settings.CHAT_MODEL,
        messages=[
            {"role": "system", "content": "Translate the following Urdu question to English. Output ONLY the English translation, nothing else."},
            {"role": "user", "content": request.text},
        ],
        max_tokens=200,
    )
    return QueryTranslateResponse(translated=response.choices[0].message.content.strip(), was_urdu=True)


CHAT_TRANSLATION_PROMPT = """You are a technical Urdu translator for an AI & Robotics textbook chatbot.
Translate the English text to clear, natural Urdu (Nastaliq script) for students.

Rules:
1. Translate faithfully — do NOT summarize or add information.
2. Keep technical terms in English: AI, Physical AI, ROS 2, LiDAR, SLAM, IMU, GPU, VLA, URDF, Nav2, MoveIt2, Gazebo, Isaac.
3. Keep citations unchanged: [Chapter X, Section Y.Z]
4. Preserve structure: bullet points, headings, numbered lists.
5. Do NOT translate code blocks or file names.
6. Output ONLY the Urdu translation."""


@router.post("/translate/message", response_model=ChatTranslateResponse)
async def translate_chat_message(request: ChatTranslateRequest):
    """Translate a chat response to Urdu for display."""
    if not request.text.strip():
        raise HTTPException(status_code=400, detail="Text cannot be empty")

    client = AsyncGroq(api_key=settings.GROQ_API_KEY)
    response = await client.chat.completions.create(
        model=settings.CHAT_MODEL,
        messages=[
            {"role": "system", "content": CHAT_TRANSLATION_PROMPT},
            {"role": "user", "content": request.text},
        ],
        max_tokens=2000,
    )
    return ChatTranslateResponse(translated=response.choices[0].message.content)
