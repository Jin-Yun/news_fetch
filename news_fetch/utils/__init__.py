"""Utility modules for the crawler."""
from .date_parser import parse_spanish_date, normalize_date
from .http_client import RespectfulHttpClient
from .text_cleaner import clean_text, clean_html_content
from .exporters import export_to_json, convert_result_to_dict

__all__ = [
    "parse_spanish_date",
    "normalize_date",
    "RespectfulHttpClient",
    "clean_text",
    "clean_html_content",
    "export_to_json",
    "convert_result_to_dict",
]
