"""
Spider modules for SpiderMail
"""

from .base import BaseSpider
from .taobao_spider import TaobaoSpider
from .jd_spider import JDSpider

__all__ = ["BaseSpider", "TaobaoSpider", "JDSpider"]