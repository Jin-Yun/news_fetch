"""
Tests for the Spanish date parser.
Critical functionality since all sites use different date formats in Spanish.
"""

from datetime import date
import pytest
from news_fetch.utils.date_parser import parse_spanish_date, normalize_date, is_date_in_range, SPANISH_MONTHS


def test_spanish_month_mapping_complete():
    """Test all 12 months are mapped."""
    assert len(SPANISH_MONTHS) >= 12
    assert SPANISH_MONTHS["enero"] == 1
    assert SPANISH_MONTHS["diciembre"] == 12
    assert SPANISH_MONTHS["sep"] == 9
    assert SPANISH_MONTHS["oct"] == 10


def test_parse_iso_format():
    """Test parsing ISO format YYYY-MM-DD."""
    parsed = parse_spanish_date("2025-01-15")
    assert parsed == date(2025, 1, 15)


def test_parse_ddmmyyyy_slash():
    """Test parsing DD/MM/YYYY format."""
    parsed = parse_spanish_date("15/01/2025")
    assert parsed == date(2025, 1, 15)


def test_parse_ddmmyyyy_dash():
    """Test parsing DD-MM-YYYY format."""
    parsed = parse_spanish_date("15-01-2025")
    assert parsed == date(2025, 1, 15)


def test_parse_d_de_m_de_y():
    """Test parsing "15 de enero de 2025" - most common Spanish format."""
    parsed = parse_spanish_date("15 de enero de 2025")
    assert parsed == date(2025, 1, 15)


def test_parse_d_m_de_y():
    """Test parsing without "de"."""
    parsed = parse_spanish_date("15 enero 2025")
    assert parsed == date(2025, 1, 15)


def test_parse_monthname_d_y():
    """Test parsing "enero 15 de 2025"."""
    parsed = parse_spanish_date("enero 15 de 2025")
    assert parsed == date(2025, 1, 15)


def test_parse_abbreviated_month():
    """Test parsing with abbreviated month name."""
    parsed = parse_spanish_date("15 ene 2025")
    assert parsed == date(2025, 1, 15)


def test_parse_from_url():
    """Test extracting date from URL pattern."""
    parsed = parse_spanish_date("https://elpais.com/internacional/2025/01/15/article.html")
    assert parsed == date(2025, 1, 15)


def test_parse_month_year_only():
    """Test parsing when only month and year are available."""
    parsed = parse_spanish_date("enero de 2025")
    assert parsed == date(2025, 1, 1)


def test_normalize_date():
    """Test date normalizes to YYYY-MM-DD string."""
    d = date(2025, 1, 5)
    assert normalize_date(d) == "2025-01-05"


def test_is_date_in_range():
    """Test date range check."""
    start = date(2025, 1, 1)
    end = date(2025, 1, 31)

    assert is_date_in_range(date(2025, 1, 15), start, end) is True
    assert is_date_in_range(date(2025, 1, 1), start, end) is True
    assert is_date_in_range(date(2025, 1, 31), start, end) is True
    assert is_date_in_range(date(2024, 12, 31), start, end) is False
    assert is_date_in_range(date(2025, 2, 1), start, end) is False


def test_invalid_date_returns_none():
    """Test invalid input returns None."""
    assert parse_spanish_date("") is None
    assert parse_spanish_date("not a date") is None
    assert parse_spanish_date("32 enero 2025") is None  # Invalid day
