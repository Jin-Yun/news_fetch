"""
Main search orchestration engine.
Coordinates crawling across multiple media sites and produces the final output.
This is the main entry point for the entire system.
"""

from datetime import datetime, date
from typing import List, Dict, Any, Optional, Union
from dateutil.parser import parse as parse_date

from ..models.article import Article
from ..crawlers.base_crawler import BaseCrawler
from ..crawlers.el_pais import ElPaisCrawler
from ..crawlers.el_mundo import ElMundoCrawler
from ..crawlers.abc_es import ABCCrawler
from ..crawlers.efe import EFECrawler
from ..utils.exporters import convert_result_to_dict, export_to_json


class SpanishNewsCrawler:
    """
    Main entry point for crawling Spanish news.

    Example usage:
    ```python
    from news_fetch import SpanishNewsCrawler

    crawler = SpanishNewsCrawler(
        keywords="China Asia",
        start_date="2025-01-01",
        end_date="2025-03-28",
        media_sites=["elpais", "efe"]
    )

    result = crawler.run()
    # Access results: result["news_data"] contains all articles
    # Save to file: crawler.save_to_json("output.json")
    ```
    """

    # Mapping of media identifiers to crawler classes
    MEDIA_CRAWLERS = {
        "elpais": ElPaisCrawler,
        "elmundo": ElMundoCrawler,
        "abc": ABCCrawler,
        "efe": EFECrawler,
    }

    def __init__(
        self,
        keywords: Union[str, List[str]],
        start_date: str,
        end_date: str,
        media_sites: Optional[List[str]] = None,
        delay_seconds: float = 3.0,
        max_retries: int = 3,
        deduplicate: bool = True,
    ):
        """
        Initialize the crawler with search parameters.

        Args:
            keywords: Search keywords - string with space separation or list of strings
            start_date: Start date in YYYY-MM-DD format
            end_date: End date in YYYY-MM-DD format
            media_sites: List of media sites to crawl. Available: ["elpais", "elmundo", "abc", "efe"]
                         If None, crawls all supported sites.
            delay_seconds: Delay between requests (default 3.0 seconds for respectful crawling)
            max_retries: Maximum number of retries for failed requests (default 3)
            deduplicate: Remove duplicate articles by URL (default True)
        """
        # Process keywords
        self.keywords = self._parse_keywords(keywords)

        # Parse dates
        self.start_date_str = start_date
        self.end_date_str = end_date
        self.start_date = parse_date(start_date).date()
        self.end_date = parse_date(end_date).date()

        # Process media sites - if None, use all
        if media_sites is None:
            self.media_sites = list(self.MEDIA_CRAWLERS.keys())
        else:
            # Validate media sites
            valid_sites = []
            for site in media_sites:
                if site in self.MEDIA_CRAWLERS:
                    valid_sites.append(site)
                else:
                    print(f"Warning: Unknown media site '{site}' - skipping.")
            self.media_sites = valid_sites

        # Configuration
        self.delay_seconds = delay_seconds
        self.max_retries = max_retries
        self.deduplicate = deduplicate

        # Initialize crawlers
        self.crawlers: List[BaseCrawler] = self._init_crawlers()

        # Store results after run
        self._results: Optional[Dict[str, Any]] = None
        self._articles: List[Article] = []
        self._start_time: Optional[datetime] = None
        # Deduplication: avoid crawling same URL multiple times
        self._seen_urls: set = set()

    def run(self) -> Dict[str, Any]:
        """
        Execute the crawl across all selected media sites.

        Returns:
            Dictionary in the standardized output format with all results
        """
        self._start_time = datetime.now()
        start_time = self._start_time
        all_articles: List[Article] = []
        status = "success"
        error_message = ""

        # Reset seen URLs for each run
        self._seen_urls.clear()

        try:
            for crawler in self.crawlers:
                try:
                    articles = crawler.search(self.keywords, self.start_date, self.end_date)
                    # Deduplicate by URL
                    for article in articles:
                        if not self.deduplicate or article.url not in self._seen_urls:
                            self._seen_urls.add(article.url)
                            all_articles.append(article)
                except Exception as e:
                    error_msg = f"Error crawling {crawler.media_id}: {str(e)}"
                    print(error_msg)
                    if error_message:
                        error_message += "; " + error_msg
                    else:
                        error_message = error_msg
                    status = "partial" if status == "success" else status

        except Exception as e:
            status = f"error: {str(e)}"
            error_message = str(e)

        self._articles = all_articles

        result = convert_result_to_dict(
            keywords=self.keywords,
            start_date=self.start_date_str,
            end_date=self.end_date_str,
            media_sites=self.media_sites,
            articles=all_articles,
            start_time=start_time,
            status=status,
            error_message=error_message,
        )

        self._results = result
        return result

    def save_to_json(self, output_path: str) -> None:
        """
        Save the crawl results to a JSON file.
        Must call run() first.

        Args:
            output_path: Path to save the JSON file
        """
        if self._results is None:
            # If not yet run, run first
            self.run()

        assert self._results is not None
        assert self._start_time is not None

        export_to_json(
            output_path=output_path,
            keywords=self.keywords,
            start_date=self.start_date_str,
            end_date=self.end_date_str,
            media_sites=self.media_sites,
            articles=self._articles,
            start_time=self._start_time,
            status=self._results.get("crawl_info", {}).get("status", "success"),
            error_message=self._results.get("crawl_info", {}).get("status", "").replace("error: ", ""),
        )

    def get_articles(self) -> List[Article]:
        """
        Get the list of crawled articles as Article objects.
        Must call run() first.

        Returns:
            List of Article objects
        """
        return self._articles

    def _parse_keywords(self, keywords: Union[str, List[str]]) -> List[str]:
        """Parse keywords from input string or list."""
        if isinstance(keywords, list):
            return [k.strip() for k in keywords if k.strip()]
        if isinstance(keywords, str):
            return [k.strip() for k in keywords.split() if k.strip()]
        return []

    def _init_crawlers(self) -> List[BaseCrawler]:
        """Initialize crawler instances for selected media sites."""
        crawlers: List[BaseCrawler] = []
        for site in self.media_sites:
            crawler_class = self.MEDIA_CRAWLERS.get(site)
            if crawler_class:
                crawler = crawler_class(
                    delay_seconds=self.delay_seconds,
                    max_retries=self.max_retries,
                )
                crawlers.append(crawler)
        return crawlers

    @classmethod
    def available_media_sites(cls) -> List[str]:
        """
        Get list of available media sites.

        Returns:
            List of media site identifiers
        """
        return list(cls.MEDIA_CRAWLERS.keys())
