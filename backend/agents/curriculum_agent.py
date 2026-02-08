"""
CurriculumAgent — Validates chapter coverage across all 6 chapters.
Single responsibility: ensure no critical topic is missing from the textbook.

Reusable via: from agents.curriculum_agent import CurriculumAgent
"""
from openai import OpenAI
import json
from pathlib import Path


class CurriculumAgent:
    """
    Validates chapter coverage and suggests content gaps.

    Input: Path to docs/ directory with 6 MDX chapters
    Output: Coverage report with gap analysis
    """

    REQUIRED_TOPICS = {
        "foundations": ["embodied intelligence", "sense-plan-act", "physical AI"],
        "ros2": ["nodes", "topics", "services", "rclpy", "URDF"],
        "simulation": ["Gazebo", "digital twin", "sensor simulation", "LiDAR"],
        "isaac": ["Isaac Sim", "Isaac ROS", "VSLAM", "Nav2", "sim-to-real"],
        "vla": ["Whisper", "LLM planning", "VLA model", "action execution"],
        "capstone": ["full pipeline", "voice command", "navigation", "manipulation"],
    }

    def __init__(self):
        self.client = OpenAI()

    def validate_coverage(self, docs_path: str) -> dict:
        """
        Check all 6 chapters for required topic coverage.

        Returns: {
            "status": "pass" | "fail",
            "coverage": {module: {topic: bool}},
            "gaps": [str],
            "recommendations": [str]
        }
        """
        docs_dir = Path(docs_path)
        coverage = {}
        gaps = []

        for module, topics in self.REQUIRED_TOPICS.items():
            coverage[module] = {}
            # Find the chapter file for this module
            for mdx_file in docs_dir.glob("*.mdx"):
                content = mdx_file.read_text(encoding="utf-8").lower()
                if module in content or f"module: \"{module}\"" in content:
                    for topic in topics:
                        found = topic.lower() in content
                        coverage[module][topic] = found
                        if not found:
                            gaps.append(f"{module}: missing '{topic}'")
                    break
            else:
                for topic in topics:
                    coverage[module][topic] = False
                    gaps.append(f"{module}: chapter not found for topic '{topic}'")

        status = "pass" if not gaps else "fail"

        # Use GPT-4o for recommendations
        recommendations = []
        if gaps:
            response = self.client.chat.completions.create(
                model="gpt-4o",
                messages=[{
                    "role": "user",
                    "content": f"These topics are missing from a Physical AI textbook: {gaps}. "
                               "Suggest concise fixes (one sentence each).",
                }],
            )
            recommendations = response.choices[0].message.content.split("\n")

        return {
            "status": status,
            "coverage": coverage,
            "gaps": gaps,
            "recommendations": recommendations,
        }
