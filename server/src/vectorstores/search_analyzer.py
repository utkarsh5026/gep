from langchain_core.documents import Document
from pydantic import BaseModel, Field
from typing import Any


class ScoreInterpretation(BaseModel):
    """Interpretation of a score on a 0-100 scale."""

    normalized_score: float = Field(
        description="The normalized score on a 0-100 scale where higher is better")
    percentage: str = Field(
        description="The percentage of the score on a 0-100 scale")
    relevance: str = Field(
        description="The relevance of the score on a 0-100 scale")
    confidence: str = Field(
        description="The confidence of the score on a 0-100 scale")
    color: str = Field(description="The color of the score on a 0-100 scale")
    stars: float = Field(
        description="The number of stars for the score on a 0-100 scale")
    star_display: str = Field(
        description="The display of the stars for the score on a 0-100 scale")


class SearchAnalyzer:
    def __init__(self, search_results: list[tuple[Document, float]]):
        self.search_results = search_results

    def analyze(self) -> list[tuple[Document, ScoreInterpretation]]:
        """
        Analyze search results to provide insights about relevance distribution.

        Args:
            results: List of search results with score information

        Returns:
            Dictionary with analysis information
        """
        results = []
        for doc, score in self.search_results:
            interpretation = self.interpret_score(score)
            results.append((doc, interpretation))
        return results

    @classmethod
    def interpret_score(cls, normalized_score: float) -> ScoreInterpretation:
        """
            Interpret a normalized score with human-friendly descriptions.

            Args:
                normalized_score: Score on 0-100 scale

        Returns:
            Dictionary with interpretation data
        """
        if normalized_score >= 90:
            relevance = "Extremely relevant"
            confidence = "Very high confidence"
            color = "green"
        elif normalized_score >= 75:
            relevance = "Highly relevant"
            confidence = "High confidence"
            color = "light green"
        elif normalized_score >= 60:
            relevance = "Moderately relevant"
            confidence = "Moderate confidence"
            color = "yellow"
        elif normalized_score >= 40:
            relevance = "Somewhat relevant"
            confidence = "Low confidence"
            color = "orange"
        else:
            relevance = "Low relevance"
            confidence = "Very low confidence"
            color = "red"

        stars = normalized_score / 20

        return ScoreInterpretation(
            normalized_score=round(normalized_score, 1),
            percentage=f"{round(normalized_score, 1)}%",
            relevance=relevance,
            confidence=confidence,
            color=color,
            stars=stars,
            star_display=cls._format_stars(stars)
        )

    @classmethod
    def _format_stars(cls, stars: float) -> str:
        """Format a star rating as a string."""
        full_stars = int(stars)
        half_star = stars - full_stars >= 0.5

        star_display = "★" * full_stars
        star_display += "½" if half_star else ""
        star_display += "☆" * (5 - full_stars - (1 if half_star else 0))

        return star_display
