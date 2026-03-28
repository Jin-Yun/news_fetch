"""
Tests for text cleaning utilities.
"""

from bs4 import BeautifulSoup
import pytest
from news_fetch.utils.text_cleaner import (
    clean_text,
    clean_html_content,
    remove_bom,
    normalize_spanish_chars,
)


def test_clean_text_removes_extra_whitespace():
    """Test clean_text normalizes whitespace."""
    input_text = "   Hello   world  \n\n   with   multiple   lines   "
    cleaned = clean_text(input_text)
    assert cleaned == "Hello world\n\nwith multiple lines"


def test_clean_text_empty():
    """Test empty input returns empty string."""
    assert clean_text("") == ""
    assert clean_text("   \n\n   ") == ""


def test_remove_bom_removes_bom():
    """Test BOM is removed if present."""
    assert remove_bom("\ufeffHello") == "Hello"
    assert remove_bom("Hello") == "Hello"


def test_normalize_spanish_chars():
    """Test Unicode normalization preserves Spanish characters."""
    # Test with composed and decomposed forms
    import unicodedata
    # Create decomposed (NFD) version of ñ
    decomposed = unicodedata.normalize('NFD', "ñ")
    assert len(decomposed) == 2  # Decomposed into n + combining tilde
    normalized = normalize_spanish_chars(decomposed)
    assert len(normalized) == 1  # Composed back to NFC
    assert normalized == "ñ"


def test_clean_html_content_removes_scripts():
    """Test clean_html_content removes script tags."""
    html = """
    <html>
        <script>alert('bad');</script>
        <p>Hello world</p>
    </html>
    """
    soup = BeautifulSoup(html, 'html.parser')
    cleaned = clean_html_content(soup)
    assert "alert" not in cleaned
    assert "Hello world" in cleaned


def test_clean_html_content_removes_advertisements():
    """Test clean_html_content removes advertisement blocks."""
    html = """
    <article>
        <p>Main content here</p>
        <div class="advertisement">Buy this!</div>
        <p>More content</p>
    </article>
    """
    soup = BeautifulSoup(html, 'html.parser')
    cleaned = clean_html_content(soup)
    assert "Main content here" in cleaned
    assert "More content" in cleaned
    assert "Buy this!" not in cleaned


def test_clean_html_content_removes_related_articles():
    """Test clean_html_content removes related articles section."""
    html = """
    <article>
        <p>Article content</p>
        <div class="related">Read also: something</div>
    </article>
    """
    soup = BeautifulSoup(html, 'html.parser')
    cleaned = clean_html_content(soup)
    assert "Article content" in cleaned
    assert "Read also" not in cleaned
