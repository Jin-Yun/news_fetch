"""
Abstract base class for all news crawlers.
Defines the common interface that all crawler implementations must follow.
"""

from abc import ABC, abstractmethod
from datetime import date
from typing import List, Optional
from ..models.article import Article


class BaseCrawler(ABC):
    """Abstract base class for all news site crawlers."""

    def __init__(self, media_id: str, delay_seconds: float = 3.0, max_retries: int = 3):
        """
        Initialize the crawler.

        Args:
            media_id: Unique identifier for this media site
            delay_seconds: Delay between requests to respect server load
            max_retries: Maximum number of retries for failed requests
        """
        self.media_id = media_id
        self.delay_seconds = delay_seconds
        self.max_retries = max_retries

    @abstractmethod
    def search(
        self,
        keywords: List[str],
        start_date: date,
        end_date: date,
    ) -> List[Article]:
        """
        Search for articles matching keywords within the date range.

        Args:
            keywords: List of keywords to search for
            start_date: Start of date range (inclusive)
            end_date: End of date range (inclusive)

        Returns:
            List of Article objects matching the search criteria
        """
        pass

    @abstractmethod
    def extract_article(self, url: str, keyword: str) -> Optional[Article]:
        """
        Extract full article content from a given URL.

        Args:
            url: Article URL to extract
            keyword: The search keyword that found this article

        Returns:
            Article object if extraction successful, None otherwise
        """
        pass
