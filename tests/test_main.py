"""
Basic smoke tests for the main crawler class.
"""

from datetime import date
import pytest
from news_fetch import SpanishNewsCrawler
from news_fetch.utils.date_parser import parse_spanish_date


def test_crawler_initialization_string_keywords():
    """Test crawler initializes with string keywords."""
    crawler = SpanishNewsCrawler(
        keywords="China Asia",
        start_date="2025-01-01",
        end_date="2025-03-28",
        media_sites=["efe"],
    )
    assert crawler.keywords == ["China", "Asia"]
    assert crawler.start_date == date(2025, 1, 1)
    assert crawler.end_date == date(2025, 3, 28)
    assert crawler.media_sites == ["efe"]


def test_crawler_initialization_list_keywords():
    """Test crawler initializes with list keywords."""
    crawler = SpanishNewsCrawler(
        keywords=["China", "Asia"],
        start_date="2025-01-01",
        end_date="2025-03-28",
    )
    assert crawler.keywords == ["China", "Asia"]
    # Defaults to all sites
    assert set(crawler.media_sites) == {"elpais", "elmundo", "abc", "efe"}


def test_crawler_rejects_unknown_media_sites(capsys):
    """Test crawler warns about unknown media sites and ignores them."""
    crawler = SpanishNewsCrawler(
        keywords="China",
        start_date="2025-01-01",
        end_date="2025-03-28",
        media_sites=["efe", "unknown_site"],
    )
    assert "unknown_site" not in crawler.media_sites
    assert "efe" in crawler.media_sites
    # Check warning printed
    captured = capsys.readouterr()
    assert "Warning: Unknown media site" in captured.out


def test_available_media_sites():
    """Test available_media_sites returns all supported sites."""
    sites = SpanishNewsCrawler.available_media_sites()
    assert len(sites) == 4
    assert "elpais" in sites
    assert "elmundo" in sites
    assert "abc" in sites
    assert "efe" in sites


def test_result_structure():
    """Test that empty result has correct structure."""
    crawler = SpanishNewsCrawler(
        keywords="ThisKeywordShouldNotMatchAnything",
        start_date="2025-01-01",
        end_date="2025-01-02",
        media_sites=["efe"],
    )
    result = crawler.run()

    # Check structure matches specification
    assert "crawl_params" in result
    assert "crawl_info" in result
    assert "news_data" in result

    assert "keywords" in result["crawl_params"]
    assert "start_date" in result["crawl_params"]
    assert "end_date" in result["crawl_params"]
    assert "media_sites" in result["crawl_params"]

    assert "total_news" in result["crawl_info"]
    assert "crawl_time_seconds" in result["crawl_info"]
    assert "crawl_finished_at" in result["crawl_info"]
    assert "status" in result["crawl_info"]


def test_empty_keywords():
    """Test crawler handles empty keywords gracefully."""
    crawler = SpanishNewsCrawler(
        keywords="",
        start_date="2025-01-01",
        end_date="2025-01-02",
    )
    assert crawler.keywords == []
    result = crawler.run()
    assert result["crawl_info"]["total_news"] == 0


def test_deduplicate_default_enabled():
    """Test deduplication is enabled by default."""
    crawler = SpanishNewsCrawler(
        keywords="China",
        start_date="2025-01-01",
        end_date="2025-01-02",
    )
    assert crawler.deduplicate is True


def test_deduplicate_can_be_disabled():
    """Test deduplication can be disabled."""
    crawler = SpanishNewsCrawler(
        keywords="China",
        start_date="2025-01-01",
        end_date="2025-01-02",
        deduplicate=False,
    )
    assert crawler.deduplicate is False


def test_get_articles_before_run():
    """Test get_articles returns empty list before run."""
    crawler = SpanishNewsCrawler(
        keywords="China",
        start_date="2025-01-01",
        end_date="2025-01-02",
    )
    assert crawler.get_articles() == []
