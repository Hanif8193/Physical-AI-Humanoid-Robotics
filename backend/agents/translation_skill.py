"""
TranslationSkill — Reusable translation with technical term preservation.
Single responsibility: translate robotics content to Urdu accurately.

Callable from any agent: from agents.translation_skill import TranslationSkill
"""
from openai import OpenAI


class TranslationSkill:
    """
    Translates robotics/AI content to Urdu, preserving technical terms.

    Input: text (str), target_language (str, default "ur")
    Output: {"translated": str, "preserved_terms": list[str]}
    """

    PRESERVED_TERMS = [
        "ROS 2", "SLAM", "LiDAR", "URDF", "Isaac", "Gazebo",
        "Nav2", "Python", "GPU", "IMU", "VSLAM", "VLA",
        "Whisper", "MoveIt2", "Jetson", "Orin",
    ]

    SYSTEM_PROMPT = """Translate the following robotics and AI text to Urdu.
Rules:
1. Keep technical terms in English with Urdu transliteration: term (ترم)
2. Do not translate: code blocks, variable names, command names
3. Use formal academic Urdu
4. Preserve markdown formatting"""

    def __init__(self):
        self.client = OpenAI()

    def translate(self, text: str, target_language: str = "ur") -> dict:
        """
        Translate text to target language.

        Returns: {"translated": str, "preserved_terms": list[str]}
        """
        if target_language != "ur":
            raise ValueError(f"Unsupported language: {target_language}. Only 'ur' supported.")

        response = self.client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": self.SYSTEM_PROMPT},
                {"role": "user", "content": text},
            ],
            max_tokens=4000,
        )

        translated = response.choices[0].message.content
        preserved = [t for t in self.PRESERVED_TERMS if t in translated]

        return {"translated": translated, "preserved_terms": preserved}
