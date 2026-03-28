"""
EFE (efe.com) crawler.
Agencia EFE is Spain's national news agency.
Very clean semantic HTML, excellent source for China/Asia coverage.
"""

from datetime import date, datetime
from typing import List, Optional
from bs4 import BeautifulSoup
import re

from ..models.article import Article
from ..crawlers.base_crawler import BaseCrawler
from ..utils.http_client import RespectfulHttpClient
from ..utils.date_parser import parse_spanish_date, is_date_in_range, normalize_date
from ..utils.text_cleaner import clean_text, clean_html_content


class EFECrawler(BaseCrawler):
    """EFE (efe.com) crawler implementation."""

    BASE_SEARCH_URL = "https://www.efe.com/busqueda"
    BASE_DOMAIN = "https://www.efe.com"

    def __init__(self, delay_seconds: float = 3.0, max_retries: int = 3):
        super().__init__(media_id="efe", delay_seconds=delay_seconds, max_retries=max_retries)
        self.http_client = RespectfulHttpClient(delay_seconds=delay_seconds, max_retries=max_retries)

    def search(
        self,
        keywords: List[str],
        start_date: date,
        end_date: date,
    ) -> List[Article]:
        """
        Search for articles in EFE matching keywords and date range.

        Args:
            keywords: List of keywords to search for
            start_date: Start of date range
            end_date: End of date range

        Returns:
            List of Article objects
        """
        articles: List[Article] = []

        for keyword in keywords:
            page = 1
            while True:
                params = {
                    "palabra": keyword,
                    "desde": f"{start_date:%d-%m-%Y}",
                    "hasta": f"{end_date:%d-%m-%Y}",
                    "pagina": page,
                }

                html = self.http_client.get(self.BASE_SEARCH_URL, params=params)
                if not html:
                    break

                soup = BeautifulSoup(html, 'lxml')
                article_links = self._extract_article_links(soup)

                if not article_links:
                    break

                for link in article_links:
                    full_url = self._normalize_url(link)
                    article = self.extract_article(full_url, keyword)
                    if article:
                        pub_date = parse_spanish_date(article.publish_time)
                        if pub_date and is_date_in_range(pub_date, start_date, end_date):
                            articles.append(article)

                if not self._has_next_page(soup, page):
                    break

                page += 1

        return articles

    def extract_article(self, url: str, keyword: str) -> Optional[Article]:
        """
        Extract article content from EFE article URL.

        Args:
            url: Article URL
            keyword: The search keyword that found this article

        Returns:
            Article object if successful, None otherwise
        """
        html = self.http_client.get(url)
        if not html:
            return None

        soup = BeautifulSoup(html, 'lxml')

        title = self._extract_title(soup)
        if not title:
            return None

        subtitle = self._extract_subtitle(soup)
        content = self._extract_content(soup)
        author = self._extract_author(soup)
        publish_time = self._extract_publish_date(soup)
        category = self._extract_category(soup)

        return Article(
            media="efe",
            title=clean_text(title),
            subtitle=clean_text(subtitle) if subtitle else None,
            content=clean_text(content),
            author=clean_text(author) if author else None,
            publish_time=publish_time,
            url=url,
            category=clean_text(category) if category else None,
            crawl_time=datetime.now(),
        )

    def _extract_article_links(self, soup: BeautifulSoup) -> List[str]:
        """Extract article URLs from search results page."""
        links: List[str] = []

        # EFE search results are in nice semantic blocks
        result_items = soup.select('.resultado a')
        if not result_items:
            result_items = soup.select('h3 a')

        for item in result_items:
            href = item.get('href')
            if href and isinstance(href, str) and '/efe/' in href:
                links.append(href)

        return list(dict.fromkeys(links))

    def _normalize_url(self, url: str) -> str:
        """Normalize URL to absolute URL."""
        if url.startswith('//'):
            return f"https:{url}"
        if url.startswith('/'):
            return f"{self.BASE_DOMAIN}{url}"
        return url

    def _has_next_page(self, soup: BeautifulSoup, current_page: int) -> bool:
        """Check if there's a next page."""
        pagination = soup.select_one('.paginacion')
        if pagination:
            next_link = pagination.select_one(f'a[href*="pagina={current_page + 1}"]')
            return next_link is not None
        return False

    def _extract_title(self, soup: BeautifulSoup) -> Optional[str]:
        """Extract article title."""
        h1_tag = soup.select_one('h1')
        if h1_tag:
            return h1_tag.get_text()

        title_tag = soup.select_one('title')
        if title_tag:
            text = title_tag.get_text()
            return text.rsplit('|', 1)[0].strip()

        return None

    def _extract_subtitle(self, soup: BeautifulSoup) -> Optional[str]:
        """Extract article subtitle."""
        subtitle_tag = soup.select_one('.subtitulo')
        if subtitle_tag:
            return subtitle_tag.get_text()
        lead_tag = soup.select_one('.lead')
        if lead_tag:
            return lead_tag.get_text()
        return None

    def _extract_content(self, soup: BeautifulSoup) -> str:
        """Extract and clean article content."""
        # EFE has very clean article markup
        article_body = soup.select_one('article')
        if article_body:
            return clean_html_content(article_body)

        content_div = soup.select_one('.cuerpo-noticia')
        if content_div:
            return clean_html_content(content_div)

        content_div = soup.select_one('.content')
        if content_div:
            return clean_html_content(content_div)

        return ""

    def _extract_author(self, soup: BeautifulSoup) -> Optional[str]:
        """Extract author name."""
        author_tag = soup.select_one('.autor')
        if author_tag:
            return author_tag.get_text().strip()

        firma_tag = soup.select_one('.firma')
        if firma_tag:
            return firma_tag.get_text().strip()

        # EFE articles often just say "EFE" as the author
        byline = soup.select_one('.byline')
        if byline:
            return byline.get_text().strip()

        return "EFE"

    def _extract_publish_date(self, soup: BeautifulSoup) -> str:
        """Extract and normalize publication date."""
        meta_date = soup.select_one('meta[property="article:published_time"]')
        if meta_date and meta_date.get('content'):
            date_str = meta_date.get('content')
            if isinstance(date_str, str) and 'T' in date_str:
                date_str = date_str.split('T')[0]
            return date_str

        date_tag = soup.select_one('.fecha')
        if date_tag:
            date_text = date_tag.get_text()
            parsed = parse_spanish_date(date_text)
            if parsed:
                return normalize_date(parsed)

        # Extract from URL
        url_match = re.search(r'/(\d{4})/(\d{2})/(\d{2})/', str(soup))
        if url_match:
            return f"{url_match.group(1)}-{url_match.group(2)}-{url_match.group(3)}"

        return normalize_date(date.today())

    def _extract_category(self, soup: BeautifulSoup) -> Optional[str]:
        """Extract article category/section."""
        breadcrumb = soup.select_one('.breadcrumb a')
        if breadcrumb:
            return breadcrumb.get_text().strip()

        # Extract from URL
        url_parts = url.split('/')
        for part in url_parts:
            if part in ['internacional', 'america', 'asia', 'economia', 'deportes', 'cultura']:
                return part

        return None
