"""
RAGAgent — Wraps ingestion pipeline for re-indexing on chapter update.
Single responsibility: keep Qdrant in sync with chapter content.

Reusable via: from agents.rag_agent import RAGAgent
"""
from pathlib import Path
import subprocess
import sys


class RAGAgent:
    """
    Re-ingests chapters into Qdrant when content changes.

    Input: chapter_slug (optional) or "all"
    Output: ingestion report
    """

    CHAPTER_SLUGS = [
        "ch01-intro-physical-ai",
        "ch02-ros2-fundamentals",
        "ch03-digital-twin",
        "ch04-isaac-platform",
        "ch05-vla",
        "ch06-capstone",
    ]

    def __init__(self, docs_path: str = "../frontend/docs/"):
        self.docs_path = docs_path

    def reingest(self, chapter_slug: str = "all") -> dict:
        """
        Re-run ingestion pipeline for one or all chapters.

        Returns: {"status": "success"|"error", "chapters_processed": int, "message": str}
        """
        if chapter_slug != "all" and chapter_slug not in self.CHAPTER_SLUGS:
            return {
                "status": "error",
                "chapters_processed": 0,
                "message": f"Unknown chapter: {chapter_slug}",
            }

        try:
            result = subprocess.run(
                [sys.executable, "scripts/ingest_chapters.py", "--docs", self.docs_path],
                capture_output=True,
                text=True,
                cwd=Path(__file__).parent.parent,
            )

            if result.returncode == 0:
                return {
                    "status": "success",
                    "chapters_processed": len(self.CHAPTER_SLUGS),
                    "message": result.stdout,
                }
            else:
                return {
                    "status": "error",
                    "chapters_processed": 0,
                    "message": result.stderr,
                }
        except Exception as e:
            return {"status": "error", "chapters_processed": 0, "message": str(e)}
