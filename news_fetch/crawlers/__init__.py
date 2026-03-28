"""Crawler implementations for each media site."""
from .base_crawler import BaseCrawler
from .el_pais import ElPaisCrawler
from .el_mundo import ElMundoCrawler
from .abc_es import ABCCrawler
from .efe import EFECrawler

__all__ = [
    "BaseCrawler",
    "ElPaisCrawler",
    "ElMundoCrawler",
    "ABCCrawler",
    "EFECrawler",
]
