"""
Article data model using Pydantic for validation.
Represents a single news article from a Spanish media site.
"""

from datetime import date, datetime
from typing import Optional
from pydantic import BaseModel, Field


class Article(BaseModel):
    """A news article scraped from a Spanish media site."""

    media: str = Field(description="Source media identifier (elpais, elmundo, abc, efe)")
    title: str = Field(description="Article title in original Spanish")
    subtitle: Optional[str] = Field(default=None, description="Subtitle or abstract/summary")
    content: str = Field(description="Full article content text")
    author: Optional[str] = Field(default=None, description="Author name(s)")
    publish_time: str = Field(description="Publication date in YYYY-MM-DD format")
    url: str = Field(description="Original URL of the article")
    category: Optional[str] = Field(default=None, description="News category/section")
    crawl_time: datetime = Field(description="When this article was crawled")

    model_config = {
        "json_schema_extra": {
            "example": {
                "media": "elpais",
                "title": "China refuerza sus lazos económicos con España",
                "subtitle": "El comercio bilateral alcanza niveles históricos en 2024",
                "content": "El contenido completo del artículo...",
                "author": "Juan García",
                "publish_time": "2025-01-15",
                "url": "https://elpais.com/internacional/2025-01-15/...",
                "category": "internacional",
                "crawl_time": "2026-03-28T10:30:00",
            }
        }
    }
