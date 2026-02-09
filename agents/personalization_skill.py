"""
PersonalizationSkill — Reusable profile-aware chapter rewrite.
Single responsibility: adapt chapter content to learner profile.

Callable from any agent: from agents.personalization_skill import PersonalizationSkill
"""
from openai import OpenAI
from dataclasses import dataclass


@dataclass
class LearnerProfile:
    software_background: str
    hardware_background: str
    experience_level: str  # beginner | intermediate | expert
    preferred_language: str = "en"


class PersonalizationSkill:
    """
    Adapts textbook content to a learner's profile.

    Input: content (str), profile (LearnerProfile)
    Output: {"adapted": str, "changes": list[str]}
    """

    SYSTEM_PROMPT = """You are an expert robotics educator adapting content for a specific learner.

Learner profile:
- Software: {software}
- Hardware: {hardware}
- Level: {level}

Adaptation rules:
- Beginner: simplify, more analogies, slower pacing
- Intermediate: practical tips, real-world connections
- Expert: advanced insights, edge cases, optimizations
- No GPU: emphasize cloud alternatives
- Has Python: more code examples
Preserve structure. Output adapted content only."""

    def __init__(self):
        self.client = OpenAI()

    def adapt(self, content: str, profile: LearnerProfile) -> dict:
        """
        Adapt content to learner profile.

        Returns: {"adapted": str, "changes": list[str]}
        """
        system_prompt = self.SYSTEM_PROMPT.format(
            software=profile.software_background,
            hardware=profile.hardware_background,
            level=profile.experience_level,
        )

        response = self.client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": content},
            ],
            max_tokens=4000,
        )

        adapted = response.choices[0].message.content
        changes = []

        if profile.experience_level == "beginner":
            changes.append("Simplified for beginner level")
        elif profile.experience_level == "expert":
            changes.append("Enhanced with expert insights")
        if "no gpu" in profile.hardware_background.lower():
            changes.append("Cloud alternatives emphasized")
        if "python" in profile.software_background.lower():
            changes.append("Python examples added")

        return {"adapted": adapted, "changes": changes or ["General adaptation"]}
