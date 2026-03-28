"""
Respectful HTTP client with rate limiting, retries, and proper headers.
Follows respectful crawling practices for academic research.
"""

import time
from typing import Optional, Dict, Any
import requests
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type


class RespectfulHttpClient:
    """
    HTTP client wrapper that implements:
    - Rate limiting with configurable delay between requests
    - Exponential backoff retries for failed requests
    - Proper browser-like headers
    - UTF-8 encoding for Spanish character support
    """

    # Default browser-like headers
    DEFAULT_HEADERS = {
        "User-Agent": (
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/120.0.0.0 Safari/537.36"
        ),
        "Accept-Language": "es-ES,es;q=0.9,en;q=0.8",
        "Accept": (
            "text/html,application/xhtml+xml,application/xml;"
            "q=0.9,image/webp,*/*;q=0.8"
        ),
    }

    def __init__(
        self,
        delay_seconds: float = 3.0,
        max_retries: int = 3,
        headers: Optional[Dict[str, str]] = None,
    ):
        """
        Initialize the respectful HTTP client.

        Args:
            delay_seconds: Minimum delay between consecutive requests
            max_retries: Maximum number of retries for failed requests
            headers: Custom headers to use (uses defaults if None)
        """
        self.delay_seconds = delay_seconds
        self.max_retries = max_retries
        self.headers = headers or self.DEFAULT_HEADERS
        self._last_request_time: Optional[float] = None

    def _respect_delay(self) -> None:
        """Enforce delay between requests to avoid overwhelming the server."""
        if self._last_request_time is not None:
            elapsed = time.time() - self._last_request_time
            if elapsed < self.delay_seconds:
                time.sleep(self.delay_seconds - elapsed)
        self._last_request_time = time.time()

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10),
        retry=retry_if_exception_type((requests.exceptions.RequestException,)),
    )
    def get(self, url: str, params: Optional[Dict[str, Any]] = None) -> Optional[str]:
        """
        Make a respectful GET request.

        Args:
            url: URL to request
            params: Optional query parameters

        Returns:
            Response text if successful, None otherwise
        """
        self._respect_delay()

        try:
            response = requests.get(
                url,
                params=params,
                headers=self.headers,
                timeout=30,
            )
            response.raise_for_status()
            # Ensure UTF-8 encoding for Spanish characters
            response.encoding = "utf-8"
            return response.text
        except requests.exceptions.RequestException:
            return None
