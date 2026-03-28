"""
Tests for other utility modules: http_client and exporters.
"""

from datetime import datetime, date
import pytest
from news_fetch.models.article import Article
from news_fetch.utils.http_client import RespectfulHttpClient
from news_fetch.utils.exporters import convert_result_to_dict, export_to_json
import tempfile
import json


class TestRespectfulHttpClient:
    """Tests for RespectfulHttpClient."""

    def test_default_headers_contain_accept_language(self):
        """Test default headers include Spanish language preference."""
        client = RespectfulHttpClient()
        assert "Accept-Language" in client.headers
        assert "es-ES" in client.headers["Accept-Language"]

    def test_custom_headers_can_be_provided(self):
        """Test custom headers override defaults."""
        custom_headers = {"X-Custom": "test"}
        client = RespectfulHttpClient(headers=custom_headers)
        assert client.headers["X-Custom"] == "test"

    def test_delay_is_enforced(self):
        """Test delay is enforced between requests - this is a basic check."""
        client = RespectfulHttpClient(delay_seconds=0.1)
        # First request doesn't wait
        client._respect_delay()
        # After first request, we expect it to track last request time
        assert client._last_request_time is not None


class TestExporters:
    """Tests for exporters module."""

    def test_convert_result_to_dict_structure(self):
        """Test converted result has the correct structure."""
        articles = []
        start_time = datetime.now()

        result = convert_result_to_dict(
            keywords=["China", "Asia"],
            start_date="2025-01-01",
            end_date="2025-03-28",
            media_sites=["elpais", "efe"],
            articles=articles,
            start_time=start_time,
            status="success",
        )

        # Check top level keys
        assert "crawl_params" in result
        assert "crawl_info" in result
        assert "news_data" in result

        # Check crawl_params content
        assert result["crawl_params"]["keywords"] == ["China", "Asia"]
        assert result["crawl_params"]["start_date"] == "2025-01-01"
        assert result["crawl_params"]["end_date"] == "2025-03-28"
        assert result["crawl_params"]["media_sites"] == ["elpais", "efe"]

        # Check crawl_info content
        assert "total_news" in result["crawl_info"]
        assert "crawl_time_seconds" in result["crawl_info"]
        assert "crawl_finished_at" in result["crawl_info"]
        assert result["crawl_info"]["status"] == "success"
        assert result["crawl_info"]["total_news"] == 0

    def test_convert_result_to_dict_with_articles(self):
        """Test conversion with actual articles."""
        article = Article(
            media="elpais",
            title="Título en español",
            content="Contenido",
            publish_time="2025-01-15",
            url="https://example.com/article",
            crawl_time=datetime.now(),
        )

        start_time = datetime.now()
        result = convert_result_to_dict(
            keywords=["China"],
            start_date="2025-01-01",
            end_date="2025-01-31",
            media_sites=["elpais"],
            articles=[article],
            start_time=start_time,
        )

        assert result["crawl_info"]["total_news"] == 1
        assert len(result["news_data"]) == 1
        assert result["news_data"][0]["media"] == "elpais"
        assert result["news_data"][0]["title"] == "Título en español"

    def test_export_to_json_saves_file(self):
        """Test export_to_json correctly writes file."""
        article = Article(
            media="efe",
            title="Noticia EFE",
            content="Contenido EFE",
            publish_time="2025-01-10",
            url="https://efe.com/article",
            crawl_time=datetime.now(),
        )

        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            pass

        try:
            export_to_json(
                output_path=f.name,
                keywords=["Asia"],
                start_date="2025-01-01",
                end_date="2025-01-31",
                media_sites=["efe"],
                articles=[article],
                start_time=datetime.now(),
            )

            # Read back and verify
            with open(f.name, 'r', encoding='utf-8') as f_read:
                data = json.load(f_read)

            assert data["crawl_info"]["total_news"] == 1
            assert data["news_data"][0]["title"] == "Noticia EFE"
        finally:
            import os
            os.unlink(f.name)

    def test_convert_result_handles_partial_error(self):
        """Test partial error is correctly recorded."""
        start_time = datetime.now()
        result = convert_result_to_dict(
            keywords=["China"],
            start_date="2025-01-01",
            end_date="2025-01-31",
            media_sites=["elpais", "efe"],
            articles=[],
            start_time=start_time,
            status="success",
            error_message="elpais failed",
        )

        assert "partial" in result["crawl_info"]["status"]
        assert "elpais failed" in result["crawl_info"]["status"]
