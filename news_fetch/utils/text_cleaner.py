"""
Text cleaning utilities for scraping Spanish news content.
Removes unwanted boilerplate, ads, navigation, and normalizes whitespace.
"""

import re
from typing import List, Union
from bs4 import BeautifulSoup, NavigableString, Tag


def clean_text(text: str) -> str:
    """
    Clean raw text: normalize whitespace, fix spacing around punctuation.

    Args:
        text: Raw text to clean

    Returns:
        Cleaned text
    """
    if not text:
        return ""

    # Replace multiple newlines with single
    text = re.sub(r'\n\s*\n', '\n\n', text)
    # Replace multiple spaces with single
    text = re.sub(r'[ \t]+', ' ', text)
    # Strip whitespace from each line
    lines = [line.strip() for line in text.split('\n')]
    # Remove empty lines at start/end
    while lines and not lines[0]:
        lines.pop(0)
    while lines and not lines[-1]:
        lines.pop()

    return '\n'.join(lines).strip()


def clean_html_content(soup: BeautifulSoup) -> str:
    """
    Clean HTML content by removing common unwanted elements.

    Args:
        soup: BeautifulSoup object of the article HTML

    Returns:
        Cleaned text content
    """
    # Make a copy to avoid modifying original
    soup_copy = BeautifulSoup(str(soup), 'html.parser')

    # Remove common unwanted elements
    unwanted_selectors = [
        'script', 'style', 'noscript', 'iframe', 'svg',
        'header', 'footer', 'nav', 'navigation',
        '.social', '.share', '.sharing', '.social-links',
        '.advertisement', '.ad', '.ads', '.banner',
        '.related', 'related-articles', '.more-news',
        '.comments', '#comments',
        '.footer', '.header', '.navigation',
        '[role="complementary"]',
        '.author-bio', '.sidebar',
        '.promo', '.promotion',
    ]

    for selector in unwanted_selectors:
        try:
            for element in soup_copy.select(selector):
                element.decompose()
        except Exception:
            continue

    # Extract text with proper spacing
    text = extract_text_from_html(soup_copy)
    return clean_text(text)


def extract_text_from_html(soup: BeautifulSoup) -> str:
    """
    Extract text from HTML with proper spacing between block elements.

    Args:
        soup: BeautifulSoup object

    Returns:
        Extracted text
    """
    text_parts: List[str] = []

    def extract_recursive(element: Union[Tag, NavigableString]) -> None:
        if isinstance(element, NavigableString):
            if element.strip():
                text_parts.append(str(element))
            return

        # Block elements get newlines
        is_block = element.name in [
            'p', 'div', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6',
            'ul', 'ol', 'li', 'br', 'blockquote', 'article', 'section'
        ]

        for child in element.contents:
            extract_recursive(child)

        if is_block:
            text_parts.append('\n')

    extract_recursive(soup)
    return ''.join(text_parts)


def remove_bom(text: str) -> str:
    """
    Remove Unicode BOM (Byte Order Mark) if present.

    Args:
        text: Text that might contain BOM

    Returns:
        Text without BOM
    """
    if text.startswith('\ufeff'):
        return text[1:]
    return text


def normalize_spanish_chars(text: str) -> str:
    """
    Normalize Spanish characters (currently just ensures NFC normalization).

    Args:
        text: Text to normalize

    Returns:
        Normalized text
    """
    import unicodedata
    return unicodedata.normalize('NFC', text)
