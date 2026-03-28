"""
Date parsing utilities for Spanish date formats.
Handles Spanish month names and various date format conventions used by Spanish media.
"""

import re
from datetime import date, datetime
from typing import Optional

# Spanish month names mapping
SPANISH_MONTHS = {
    "enero": 1,
    "ene": 1,
    "febrero": 2,
    "feb": 2,
    "marzo": 3,
    "mar": 3,
    "abril": 4,
    "abr": 4,
    "mayo": 5,
    "junio": 6,
    "jun": 6,
    "julio": 7,
    "jul": 7,
    "agosto": 8,
    "ago": 8,
    "septiembre": 9,
    "sep": 9,
    "setiembre": 9,
    "octubre": 10,
    "oct": 10,
    "noviembre": 11,
    "nov": 11,
    "diciembre": 12,
    "dic": 12,
}

# Common relative date patterns in Spanish
RELATIVE_PATTERNS = {
    r"hace\s+(\d+)\s+hora|horas": lambda m: None,  # Today, keep current date
    r"hace\s+(\d+)\s+día|días": lambda m: None,  # N days ago
    r"hace\s+(\d+)\s+semana|semanas": lambda m: None,
    r"ayer": lambda m: None,
    r"hoy": lambda m: None,
}


def parse_spanish_date(date_text: str) -> Optional[date]:
    """
    Parse a date string that contains Spanish month names.

    Args:
        date_text: Date string in Spanish (e.g., "15 de enero de 2025", "enero 15, 2025")

    Returns:
        Parsed date object or None if parsing fails
    """
    # Clean input
    date_text = date_text.lower().strip()
    date_text = re.sub(r'\s+', ' ', date_text)

    # Try ISO format first (YYYY-MM-DD) which many sites use
    try:
        return datetime.strptime(date_text, "%Y-%m-%d").date()
    except ValueError:
        pass

    # Try DD/MM/YYYY format
    try:
        return datetime.strptime(date_text, "%d/%m/%Y").date()
    except ValueError:
        pass

    # Try DD-MM-YYYY format
    try:
        return datetime.strptime(date_text, "%d-%m-%Y").date()
    except ValueError:
        pass

    # Try "15 de enero de 2025" format (most common in Spanish)
    match = re.search(
        r'(\d{1,2})\s+(?:de\s+)?([a-zá-ú]+)\s+(?:de\s+)?(\d{4})',
        date_text
    )
    if match:
        day = int(match.group(1))
        month_name = match.group(2)
        year = int(match.group(3))
        month = SPANISH_MONTHS.get(month_name)
        if month is not None:
            try:
                return date(year, month, day)
            except ValueError:
                pass

    # Try "enero 15 de 2025" format
    match = re.search(
        r'([a-zá-ú]+)\s+(\d{1,2})\s+(?:de\s+)?(\d{4})',
        date_text
    )
    if match:
        month_name = match.group(1)
        day = int(match.group(2))
        year = int(match.group(3))
        month = SPANISH_MONTHS.get(month_name)
        if month is not None:
            try:
                return date(year, month, day)
            except ValueError:
                pass

    # Try "15 ene 2025" format
    match = re.search(
        r'(\d{1,2})\s+([a-z]{3})\s+(\d{4})',
        date_text
    )
    if match:
        day = int(match.group(1))
        month_name = match.group(2)
        year = int(match.group(3))
        month = SPANISH_MONTHS.get(month_name)
        if month is not None:
            try:
                return date(year, month, day)
            except ValueError:
                pass

    # Try extracting year-month from URL patterns commonly found in Spanish media
    # e.g., /2025/01/15/ or /2025-01-15/
    url_date_match = re.search(r'(\d{4})[/-](\d{2})[/-](\d{2})', date_text)
    if url_date_match:
        year = int(url_date_match.group(1))
        month = int(url_date_match.group(2))
        day = int(url_date_match.group(3))
        try:
            return date(year, month, day)
        except ValueError:
            pass

    # Just extract year and month if that's all we can get
    match = re.search(r'([a-zá-ú]+)\s+de\s+(\d{4})', date_text)
    if match:
        month_name = match.group(1)
        year = int(match.group(2))
        month = SPANISH_MONTHS.get(month_name)
        if month is not None:
            return date(year, month, 1)

    return None


def normalize_date(input_date: date) -> str:
    """
    Normalize a date object to the standard string format (YYYY-MM-DD).

    Args:
        input_date: Date object to normalize

    Returns:
        Formatted date string
    """
    return input_date.strftime("%Y-%m-%d")


def is_date_in_range(
    publish_date: date,
    start_date: date,
    end_date: date
) -> bool:
    """
    Check if a publication date falls within the specified range.

    Args:
        publish_date: The date to check
        start_date: Start of range (inclusive)
        end_date: End of range (inclusive)

    Returns:
        True if date is in range, False otherwise
    """
    return start_date <= publish_date <= end_date
