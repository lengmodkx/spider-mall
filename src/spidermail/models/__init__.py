"""
Database models for SpiderMail
"""

from .product import Product, PriceHistory
from .review import Review
from .crawl_task import CrawlTask

__all__ = ["Product", "Review", "PriceHistory", "CrawlTask", "Base"]

from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()