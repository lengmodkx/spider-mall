"""
JD.com spider implementation
"""

import json
import re
from typing import List, Dict, Any, Optional
from urllib.parse import urljoin, quote
from bs4 import BeautifulSoup
from loguru import logger

from .base import BaseSpider
from ..config.settings import settings


class JDSpider(BaseSpider):
    """JD.com spider for extracting product and review data"""

    def __init__(self):
        super().__init__("jd")
        self.base_url = settings.platform.jd_base_url
        self.search_url = "https://search.jd.com/Search"
        self.item_url = "https://item.jd.com"
        self.price_url = "https://p.3.cn/prices/mgets"
        self.review_url = "https://club.jd.com/comment/productCommentSummaries.action"
        self.review_list_url = "https://club.jd.com/comment/productPageComments.action"

    def search_products(self, category: str = "手机", page: int = 1, **kwargs) -> List[Dict[str, Any]]:
        """Search JD products by category"""
        try:
            params = {
                'keyword': category,
                'page': page,
                'psort': 3,  # Sort by sales volume
                'click': 0,
                's': (page - 1) * 30 + 1,  # 30 products per page, starting position
                'scrolling': 'y'
            }

            logger.info(f"Searching JD products: {category}, page: {page}")
            response = self.make_request(self.search_url, params=params)

            products = []
            soup = BeautifulSoup(response.text, 'lxml')

            # Find product items
            product_items = soup.find_all('li', class_='gl-item')
            for item in product_items:
                product_data = self.parse_search_item(item)
                if product_data:
                    # Get real-time price
                    if product_data.get('product_id'):
                        product_data['price'] = self.get_product_price(product_data['product_id'])
                    products.append(product_data)

            logger.info(f"Found {len(products)} products on page {page}")
            return products

        except Exception as e:
            logger.error(f"Error searching JD products: {e}")
            return []

    def parse_search_item(self, item_elem) -> Optional[Dict[str, Any]]:
        """Parse individual item from search results"""
        try:
            # Extract product ID
            sku_elem = item_elem.get('data-sku', '')
            product_id = sku_elem if sku_elem else ''

            # Extract title
            title_elem = item_elem.find('div', class_='p-name')
            title = ''
            if title_elem:
                title_link = title_elem.find('a')
                if title_link:
                    title = self.clean_text(title_link.get('title', '') or title_link.get_text())

            # Extract brand
            brand = ''
            brand_elem = item_elem.find('div', class_='p-name')
            if brand_elem:
                brand_text = brand_elem.get_text()
                brand_match = re.search(r'^([A-Za-z\u4e00-\u9fa5]+)', brand_text)
                if brand_match:
                    brand = brand_match.group(1)

            # Extract shop name
            shop_elem = item_elem.find('div', class_='p-shop')
            shop_name = ''
            if shop_elem:
                shop_link = shop_elem.find('a')
                if shop_link:
                    shop_name = self.clean_text(shop_link.get_text())

            # Extract image URL
            img_elem = item_elem.find('div', class_='p-img')
            image_url = ''
            if img_elem:
                img_tag = img_elem.find('img')
                if img_tag:
                    # Convert thumbnail to full size image
                    img_src = img_tag.get('src') or img_tag.get('data-lazy-img', '')
                    if img_src:
                        image_url = img_src.replace('/n9/', '/n1/').replace('jfs/t1/', 'jfs/t1/')

            product = {
                'platform': 'jd',
                'product_id': product_id,
                'title': title,
                'brand': brand,
                'shop_name': shop_name,
                'image_url': image_url,
                'category': settings.platform.mobile_category,
                'source_url': f"{self.item_url}/{product_id}.html" if product_id else '',
                'tags': []
            }

            return product

        except Exception as e:
            logger.warning(f"Error parsing JD search item: {e}")
            return None

    def get_product_price(self, product_id: str) -> Optional[float]:
        """Get real-time product price"""
        try:
            params = {
                'skuIds': f'J_{product_id}',
                'type': 1
            }

            response = self.make_request(self.price_url, params=params)
            price_data = response.json()

            if price_data and len(price_data) > 0:
                price = price_data[0].get('p', '')
                return self.extract_price(price)

        except Exception as e:
            logger.warning(f"Error getting price for product {product_id}: {e}")

        return None

    def get_product_details(self, product_url: str) -> Dict[str, Any]:
        """Get detailed product information from JD product page"""
        try:
            logger.info(f"Getting JD product details: {product_url}")
            soup = self.get_page_content(product_url)

            details = {}

            # Extract product title
            title_elem = soup.find('div', class_='sku-name')
            if title_elem:
                details['title'] = self.clean_text(title_elem.get_text())

            # Extract brand
            brand_elem = soup.find('ul', {'id': 'parameter-brand'})
            if brand_elem:
                brand_link = brand_elem.find('a')
                if brand_link:
                    details['brand'] = self.clean_text(brand_link.get_text())

            # Extract shop information
            shop_elem = soup.find('div', class_='J-hove-wrap')
            if shop_elem:
                shop_name_elem = shop_elem.find('div', class_='name')
                if shop_name_elem:
                    details['shop_name'] = self.clean_text(shop_name_elem.get_text())

            # Extract product images
            images = []
            img_list = soup.find('ul', {'id': 'spec-list'})
            if img_list:
                img_items = img_list.find_all('img')
                for img in img_items:
                    img_url = img.get('src') or img.get('data-origin', '')
                    if img_url:
                        # Convert to full size image
                        full_img_url = img_url.replace('/n5/', '/n1/')
                        images.append(urljoin(product_url, full_img_url))
            details['image_urls'] = images

            # Extract specifications
            specs = {}
            param_elems = soup.find_all('li', class_='parameter')
            for param_elem in param_elems:
                param_text = param_elem.get_text()
                if ':' in param_text:
                    key, value = param_text.split(':', 1)
                    specs[self.clean_text(key)] = self.clean_text(value)

            # Additional specifications from Ptable table
            ptable = soup.find('table', class_='Ptable')
            if ptable:
                rows = ptable.find_all('tr')
                for row in rows:
                    cells = row.find_all(['th', 'td'])
                    if len(cells) >= 2:
                        key = self.clean_text(cells[0].get_text())
                        value = self.clean_text(cells[1].get_text())
                        if key and value:
                            specs[key] = value

            details['specifications'] = specs

            # Get comment count and average rating
            product_id = product_url.split('/')[-1].replace('.html', '')
            comment_data = self.get_product_summary(product_id)
            if comment_data:
                details['review_count'] = comment_data.get('comment_count', 0)
                details['rating'] = comment_data.get('average_score', 0)
                details['sales_count'] = comment_data.get('good_rate', 0) * details.get('review_count', 0) / 100 if details.get('review_count') else 0

            return details

        except Exception as e:
            logger.error(f"Error getting JD product details from {product_url}: {e}")
            return {}

    def get_product_summary(self, product_id: str) -> Optional[Dict[str, Any]]:
        """Get product summary including comment statistics"""
        try:
            params = {
                'referenceIds': product_id,
                'referenceType': 0,
                'callback': 'jQuery1234567890'  # JSONP callback
            }

            response = self.make_request(self.review_url, params=params)

            # Parse JSONP response
            jsonp_text = response.text
            json_start = jsonp_text.find('(') + 1
            json_end = jsonp_text.rfind(')')
            json_text = jsonp_text[json_start:json_end]

            data = json.loads(json_text)
            comments = data.get('CommentsCount', [])

            if comments and len(comments) > 0:
                comment_info = comments[0]
                return {
                    'comment_count': int(comment_info.get('CommentCount', 0)),
                    'good_rate': float(comment_info.get('GoodRate', 0)),
                    'average_score': float(comment_info.get('AverageScore', 0)),
                    'default_good_count': int(comment_info.get('DefaultGoodCount', 0)),
                    'good_count': int(comment_info.get('GoodCount', 0)),
                    'after_count': int(comment_info.get('AfterCount', 0))
                }

        except Exception as e:
            logger.warning(f"Error getting product summary for {product_id}: {e}")

        return None

    def get_product_reviews(self, product_id: str, page: int = 0) -> List[Dict[str, Any]]:
        """Get product reviews from JD"""
        try:
            logger.info(f"Getting JD reviews for product {product_id}, page {page}")

            params = {
                'productId': product_id,
                'score': 0,  # 0: all reviews, 1: good, 2: medium, 3: bad
                'sortType': 5,  # Sort by time
                'page': page,
                'pageSize': 10,
                'callback': 'fetchJSON_comment98'
            }

            response = self.make_request(self.review_list_url, params=params)

            # Parse JSONP response
            jsonp_text = response.text
            json_start = jsonp_text.find('(') + 1
            json_end = jsonp_text.rfind(')')
            json_text = jsonp_text[json_start:json_end]

            data = json.loads(json_text)
            reviews = []

            comments = data.get('comments', [])
            for comment_data in comments:
                review = self.parse_review_item(comment_data, product_id)
                if review:
                    reviews.append(review)

            logger.info(f"Found {len(reviews)} reviews on page {page}")
            return reviews

        except Exception as e:
            logger.error(f"Error getting JD reviews for product {product_id}: {e}")
            return []

    def parse_review_item(self, review_data: Dict, product_id: str) -> Optional[Dict[str, Any]]:
        """Parse individual JD review item"""
        try:
            review = {
                'platform': 'jd',
                'product_id': product_id,
                'review_id': str(review_data.get('id', '')),
                'user_name': self.clean_text(review_data.get('nickname', 'Anonymous')),
                'user_level': review_data.get('userLevelName', ''),
                'rating': int(review_data.get('score', 0)),
                'content': self.clean_text(review_data.get('content', '')),
                'pros': self.clean_text(review_data.get('good', '')),
                'cons': self.clean_text(review_data.get('bad', '')),
                'helpful_count': int(review_data.get('usefulVoteCount', 0)),
                'reply_count': int(review_data.get('replyCount', 0)),
                'review_time': self.parse_review_time(review_data.get('creationTime', '')),
                'verified_purchase': review_data.get('isMobile', False),
                'is_top_review': review_data.get('isTop', False),
                'images': [],
                'specifications': self.parse_review_specs(review_data.get('productColor', ''), review_data.get('productSize', '')),
                'source_url': f"{self.item_url}/{product_id}.html#comment"
            }

            # Extract review images
            if 'images' in review_data and review_data['images']:
                review['images'] = [img.get('imgUrl', '') for img in review_data['images'] if img.get('imgUrl')]

            # Extract purchase time if available
            if 'referenceTime' in review_data:
                review['purchase_time'] = self.parse_review_time(review_data['referenceTime'])

            return review

        except Exception as e:
            logger.warning(f"Error parsing JD review item: {e}")
            return None

    def parse_review_specs(self, color: str, size: str) -> str:
        """Parse product specifications from review"""
        specs = []
        if color:
            specs.append(f"颜色: {color}")
        if size:
            specs.append(f"尺码: {size}")
        return '; '.join(specs)

    def parse_review_time(self, time_str: str) -> Optional[str]:
        """Parse JD review time format"""
        if not time_str:
            return None

        try:
            # JD format like "2024-01-15 10:30:45"
            if ' ' in time_str:
                return time_str.split(' ')[0]
            return time_str
        except Exception:
            return time_str