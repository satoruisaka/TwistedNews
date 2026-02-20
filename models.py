"""
Data models for TwistedNews application.
"""

from dataclasses import dataclass, field
from typing import List, Dict
from datetime import datetime


@dataclass
class NewsArticle:
    """Represents a single news article."""
    filepath: str
    filename: str
    date: str  # YYYYMMDD from filename
    time: str  # HHMMSS from filename
    title: str  # Original language title from filename
    language: str  # Detected language (chinese, russian, hebrew, arabic, spanish)
    content: str  # Full markdown content
    

@dataclass
class LanguageGroup:
    """Represents articles grouped by language."""
    language: str  # chinese, russian, hebrew, arabic, spanish
    language_code: str  # CN, RU, HE, AR, SP
    date: str  # YYYYMMDD
    articles: List[NewsArticle] = field(default_factory=list)
    commentary: str = ""  # Generated commentary from TwistedPair
    
    def get_combined_content(self) -> str:
        """Combine all article contents for processing."""
        combined = []
        for article in self.articles:
            combined.append(f"## Article: {article.title}\n")
            combined.append(article.content)
            combined.append("\n---\n")
        return "\n".join(combined)
    
    def get_article_count(self) -> int:
        """Return number of articles in this group."""
        return len(self.articles)


@dataclass
class CommentaryResult:
    """Result from TwistedPair commentary generation."""
    language: str
    language_code: str
    date: str
    article_count: int
    commentary: str
    output_file: str
    mode: str
    tone: str
    gain: int
    timestamp: str
