"""
Base spider class with common functionality
"""

import time
import random
from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional
from urllib.parse import urljoin, urlparse
import requests
from bs4 import BeautifulSoup
from fake_useragent import UserAgent
from retrying import retry
from loguru import logger

from ..config.settings import settings


class BaseSpider(ABC):
    """Base spider class with common functionality"""

    def __init__(self, platform: str):
        self.platform = platform
        self.session = requests.Session()
        self.ua = UserAgent()
        self.setup_session()

    def setup_session(self):
        """Setup requests session with headers and proxies"""
        # Set random user agent
        if settings.spider.user_agent_rotation:
            self.session.headers.update({
                'User-Agent': self.ua.random,
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
                'Accept-Encoding': 'gzip, deflate',
                'Connection': 'keep-alive',
                'Upgrade-Insecure-Requests': '1',
            })
        else:
            self.session.headers.update({
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
                'Accept-Encoding': 'gzip, deflate',
                'Connection': 'keep-alive',
                'Upgrade-Insecure-Requests': '1',
            })

    @retry(stop_max_attempt_number=settings.spider.max_retries, wait_fixed=2000)
    def make_request(self, url: str, params: Optional[Dict] = None, **kwargs) -> requests.Response:
        """Make HTTP request with retry logic"""
        try:
            # Random delay to avoid being blocked
            time.sleep(settings.spider.request_delay + random.uniform(0, 1))

            response = self.session.get(
                url,
                params=params,
                timeout=settings.spider.timeout,
                **kwargs
            )
            response.raise_for_status()
            return response
        except requests.RequestException as e:
            logger.error(f"Request failed for URL {url}: {e}")
            raise

    def get_page_content(self, url: str, **kwargs) -> BeautifulSoup:
        """Get page content and parse with BeautifulSoup"""
        response = self.make_request(url, **kwargs)
        return BeautifulSoup(response.text, 'lxml')

    def clean_text(self, text: str) -> str:
        """Clean and normalize text content"""
        if not text:
            return ""
        return ' '.join(text.strip().split())

    def extract_price(self, price_text: str) -> Optional[float]:
        """Extract numeric price from text"""
        import re
        if not price_text:
            return None

        # Remove currency symbols and extract numbers
        price_match = re.search(r'[\d,]+\.?\d*', price_text.replace('¥', '').replace('￥', ''))
        if price_match:
            try:
                return float(price_match.group().replace(',', ''))
            except ValueError:
                return None
        return None

    def generate_product_id(self, product_data: Dict[str, Any]) -> str:
        """Generate unique product ID"""
        import hashlib
        content = f"{self.platform}_{product_data.get('title', '')}_{product_data.get('price', 0)}"
        return hashlib.md5(content.encode()).hexdigest()[:16]

    @abstractmethod
    def search_products(self, category: str, page: int = 1, **kwargs) -> List[Dict[str, Any]]:
        """Search products by category"""
        pass

    @abstractmethod
    def get_product_details(self, product_url: str) -> Dict[str, Any]:
        """Get detailed product information"""
        pass

    @abstractmethod
    def get_product_reviews(self, product_id: str, page: int = 1) -> List[Dict[str, Any]]:
        """Get product reviews"""
        pass