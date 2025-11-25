"""
Database models for SpiderMail
"""

from .product import Product, PriceHistory, Base
from .review import Review
from .crawl_task import CrawlTask

__all__ = ["Product", "Review", "PriceHistory", "CrawlTask", "Base"]