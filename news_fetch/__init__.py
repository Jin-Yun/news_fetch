"""
Spanish News Crawler - Crawl Chinese/Asia related news from Spanish mainstream media.

Main entry point: SpanishNewsCrawler
"""

__version__ = "1.0.0"

from .search.search_engine import SpanishNewsCrawler

__all__ = ["SpanishNewsCrawler"]
