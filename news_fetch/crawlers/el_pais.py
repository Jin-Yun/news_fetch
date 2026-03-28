"""
El País (elpais.com) crawler.
El País is Spain's largest general-interest daily newspaper.
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


class ElPaisCrawler(BaseCrawler):
    """El País (elpais.com) crawler implementation."""

    BASE_SEARCH_URL = "https://elpais.com/buscar/{keyword}/"
    BASE_DOMAIN = "https://elpais.com"

    def __init__(self, delay_seconds: float = 3.0, max_retries: int = 3):
        super().__init__(media_id="elpais", delay_seconds=delay_seconds, max_retries=max_retries)
        self.http_client = RespectfulHttpClient(delay_seconds=delay_seconds, max_retries=max_retries)

    def search(
        self,
        keywords: List[str],
        start_date: date,
        end_date: date,
    ) -> List[Article]:
        """
        Search for articles in El País matching keywords and date range.

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
                url = self._build_search_url(keyword, start_date, end_date, page)
                html = self.http_client.get(url)
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
                        # Check date range
                        pub_date = parse_spanish_date(article.publish_time)
                        if pub_date and is_date_in_range(pub_date, start_date, end_date):
                            articles.append(article)

                # Check if there's a next page
                if not self._has_next_page(soup):
                    break

                page += 1

        return articles

    def extract_article(self, url: str, keyword: str) -> Optional[Article]:
        """
        Extract article content from El País article URL.

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

        # Check for paywall
        if self._is_paywalled(soup):
            # We can still extract what metadata is available
            return self._extract_paywalled_article(soup, url, keyword)

        # Extract basic metadata
        title = self._extract_title(soup)
        if not title:
            return None

        subtitle = self._extract_subtitle(soup)
        content = self._extract_content(soup)
        author = self._extract_author(soup)
        publish_time = self._extract_publish_date(soup)
        category = self._extract_category(soup)

        return Article(
            media="elpais",
            title=clean_text(title),
            subtitle=clean_text(subtitle) if subtitle else None,
            content=clean_text(content),
            author=clean_text(author) if author else None,
            publish_time=publish_time,
            url=url,
            category=clean_text(category) if category else None,
            crawl_time=datetime.now(),
        )

    def _build_search_url(
        self,
        keyword: str,
        start_date: date,
        end_date: date,
        page: int,
    ) -> str:
        """Build the search URL with date filters."""
        keyword_encoded = keyword.replace(' ', '+')
        url = self.BASE_SEARCH_URL.format(keyword=keyword_encoded)
        # Add date range parameters
        if page > 1:
            url += f"?page={page}"
        url += f"&from={start_date:%Y-%m-%d}&to={end_date:%Y-%m-%d}"
        return url

    def _extract_article_links(self, soup: BeautifulSoup) -> List[str]:
        """Extract article URLs from search results page."""
        links: List[str] = []

        # Look for article links in search results
        article_elements = soup.select('article a[href]')
        for element in article_elements:
            href = element.get('href')
            if href and isinstance(href, str):
                # Filter out non-article links
                if self._is_article_link(href):
                    links.append(href)

        return list(dict.fromkeys(links))  # Remove duplicates

    def _is_article_link(self, href: str) -> bool:
        """Check if the link is likely an article."""
        # El País article URLs have date pattern /YYYY/MM/DD/
        if re.search(r'/\d{4}/\d{2}/\d{2}/', href):
            return True
        return False

    def _normalize_url(self, url: str) -> str:
        """Normalize URL to absolute URL."""
        if url.startswith('//'):
            return f"https:{url}"
        if url.startswith('/'):
            return f"{self.BASE_DOMAIN}{url}"
        return url

    def _has_next_page(self, soup: BeautifulSoup) -> bool:
        """Check if there's a next page of search results."""
        next_link = soup.select_one('.pagination .next a')
        return next_link is not None

    def _extract_title(self, soup: BeautifulSoup) -> Optional[str]:
        """Extract article title."""
        # Try JSON-LD first
        json_ld = self._extract_json_ld(soup)
        if json_ld and 'headline' in json_ld:
            return json_ld['headline']

        # Try common selectors
        title_tag = soup.select_one('h1')
        if title_tag:
            return title_tag.get_text()

        title_tag = soup.select_one('title')
        if title_tag:
            text = title_tag.get_text()
            # Remove site name
            return text.rsplit('|', 1)[0].strip()

        return None

    def _extract_subtitle(self, soup: BeautifulSoup) -> Optional[str]:
        """Extract article subtitle."""
        subtitle_tag = soup.select_one('.subtitle')
        if subtitle_tag:
            return subtitle_tag.get_text()
        subtitle_tag = soup.select_one('.lead')
        if subtitle_tag:
            return subtitle_tag.get_text()
        return None

    def _extract_content(self, soup: BeautifulSoup) -> str:
        """Extract article content."""
        # Find the article body
        article_body = soup.select_one('article')
        if article_body:
            return clean_html_content(article_body)

        content_div = soup.select_one('.articulo-contenido')
        if content_div:
            return clean_html_content(content_div)

        content_div = soup.select_one('.content')
        if content_div:
            return clean_html_content(content_div)

        return ""

    def _extract_author(self, soup: BeautifulSoup) -> Optional[str]:
        """Extract author name."""
        json_ld = self._extract_json_ld(soup)
        if json_ld and 'author' in json_ld:
            author_data = json_ld['author']
            if isinstance(author_data, dict) and 'name' in author_data:
                return author_data['name']
            if isinstance(author_data, list) and author_data:
                names = [a.get('name', '') for a in author_data if a.get('name')]
                return ', '.join(names)

        author_tag = soup.select_one('.autor')
        if author_tag:
            return author_tag.get_text().strip()

        author_tag = soup.select_one('.author')
        if author_tag:
            return author_tag.get_text().strip()

        byline = soup.select_one('.byline')
        if byline:
            return byline.get_text().strip()

        return None

    def _extract_publish_date(self, soup: BeautifulSoup) -> str:
        """Extract and normalize publication date."""
        # Try JSON-LD first
        json_ld = self._extract_json_ld(soup)
        if json_ld and 'datePublished' in json_ld:
            date_str = json_ld['datePublished']
            # Already ISO format, just take the date part
            if 'T' in date_str:
                date_str = date_str.split('T')[0]
            return date_str

        # Try meta tags
        meta_date = soup.select_one('meta[property="article:published_time"]')
        if meta_date and meta_date.get('content'):
            date_str = meta_date.get('content')
            if 'T' in date_str:
                date_str = date_str.split('T')[0]
            return date_str

        # Look for date in text
        date_tag = soup.select_one('.fecha')
        if date_tag:
            date_text = date_tag.get_text()
            parsed = parse_spanish_date(date_text)
            if parsed:
                return normalize_date(parsed)

        # Try to extract from URL
        url_match = re.search(r'/(\d{4})/(\d{2})/(\d{2})/', str(soup))
        if url_match:
            return f"{url_match.group(1)}-{url_match.group(2)}-{url_match.group(3)}"

        return normalize_date(date.today())

    def _extract_category(self, soup: BeautifulSoup) -> Optional[str]:
        """Extract article category/section."""
        # Look for breadcrumb
        breadcrumb = soup.select_one('.breadcrumb a')
        if breadcrumb:
            return breadcrumb.get_text().strip()

        # Extract from URL
        url_path = str(soup.find('link[rel="canonical"]')).split('href="')[1].split('"')[0]
        if '/' in url_path:
            parts = [p for p in url_path.split('/') if p]
            if parts and not parts[0].isdigit():
                return parts[0]

        return None

    def _is_paywalled(self, soup: BeautifulSoup) -> bool:
        """Check if article is behind paywall."""
        paywall_text = soup.find(string=lambda text: text and "suscripción" in text.lower())
        if paywall_text:
            return True
        paywall_text = soup.find(string=lambda text: text and "subscribe" in text.lower())
        if paywall_text:
            return True
        return False

    def _extract_paywalled_article(self, soup: BeautifulSoup, url: str, keyword: str) -> Optional[Article]:
        """Extract what metadata we can from a paywalled article."""
        title = self._extract_title(soup)
        if not title:
            return None

        subtitle = self._extract_subtitle(soup)
        author = self._extract_author(soup)
        publish_time = self._extract_publish_date(soup)
        category = self._extract_category(soup)

        # Content is limited, indicate that
        content = "[Article behind paywall - only metadata available]"

        return Article(
            media="elpais",
            title=clean_text(title),
            subtitle=clean_text(subtitle) if subtitle else None,
            content=content,
            author=clean_text(author) if author else None,
            publish_time=publish_time,
            url=url,
            category=clean_text(category) if category else None,
            crawl_time=datetime.now(),
        )

    def _extract_json_ld(self, soup: BeautifulSoup) -> Optional[dict]:
        """Extract JSON-LD metadata from article."""
        script_tag = soup.select_one('script[type="application/ld+json"]')
        if not script_tag:
            return None

        try:
            import json
            data = json.loads(script_tag.get_text())
            # Sometimes it's an array
            if isinstance(data, list):
                for item in data:
                    if isinstance(item, dict) and '@type' in item:
                        if item['@type'] in ['Article', 'NewsArticle']:
                            return item
                return data[0] if data else None
            return data if isinstance(data, dict) else None
        except Exception:
            return None
