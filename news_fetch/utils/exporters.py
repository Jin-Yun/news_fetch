"""
Export utilities for converting results to the standardized JSON format.
Follows the exact output structure specified in requirements.
"""

import json
from datetime import datetime
from typing import Any, Dict, List
from ..models.article import Article


def convert_result_to_dict(
    keywords: List[str],
    start_date: str,
    end_date: str,
    media_sites: List[str],
    articles: List[Article],
    start_time: datetime,
    status: str = "success",
    error_message: str = "",
) -> Dict[str, Any]:
    """
    Convert crawl result to the standardized dictionary format.

    Args:
        keywords: List of search keywords
        start_date: Start date string (YYYY-MM-DD)
        end_date: End date string (YYYY-MM-DD)
        media_sites: List of media site identifiers that were crawled
        articles: List of crawled articles
        start_time: When the crawl started
        status: Status of the crawl ("success" or "error: message")
        error_message: Error message if status is error

    Returns:
        Dictionary matching the required JSON schema
    """
    crawl_time = datetime.now() - start_time
    total_seconds = round(crawl_time.total_seconds(), 2)

    if status == "success" and error_message:
        status = f"partial: {error_message}"

    result = {
        "crawl_params": {
            "keywords": keywords,
            "start_date": start_date,
            "end_date": end_date,
            "media_sites": media_sites,
        },
        "crawl_info": {
            "total_news": len(articles),
            "crawl_time_seconds": total_seconds,
            "crawl_finished_at": datetime.now().isoformat(),
            "status": status,
        },
        "news_data": [article.model_dump() for article in articles],
    }

    return result


def export_to_json(
    output_path: str,
    keywords: List[str],
    start_date: str,
    end_date: str,
    media_sites: List[str],
    articles: List[Article],
    start_time: datetime,
    status: str = "success",
    error_message: str = "",
) -> None:
    """
    Export crawl results to a JSON file.

    Args:
        output_path: Path to save the JSON file
        keywords: List of search keywords
        start_date: Start date string (YYYY-MM-DD)
        end_date: End date string (YYYY-MM-DD)
        media_sites: List of media site identifiers that were crawled
        articles: List of crawled articles
        start_time: When the crawl started
        status: Status of the crawl
        error_message: Error message if any
    """
    result_dict = convert_result_to_dict(
        keywords,
        start_date,
        end_date,
        media_sites,
        articles,
        start_time,
        status,
        error_message,
    )

    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(result_dict, f, ensure_ascii=False, indent=2, default=str)
