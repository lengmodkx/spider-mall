"""
Taobao spider implementation
"""

import json
import re
from typing import List, Dict, Any, Optional
from urllib.parse import urljoin, quote
from bs4 import BeautifulSoup
from loguru import logger

from .base import BaseSpider
from ..config.settings import settings


class TaobaoSpider(BaseSpider):
    """Taobao spider for extracting product and review data"""

    def __init__(self):
        super().__init__("taobao")
        self.base_url = settings.platform.taobao_base_url
        self.search_url = "https://s.taobao.com/search"
        self.item_url = "https://detail.tmall.com/item.htm"
        self.review_url = "https://rate.tmall.com/list_detail_rate.htm"

    def search_products(self, category: str = "手机", page: int = 1, **kwargs) -> List[Dict[str, Any]]:
        """Search Taobao products by category"""
        try:
            params = {
                'q': category,
                's': (page - 1) * 44,  # 44 products per page
                'sort': 'sale-desc',    # Sort by sales volume
                'style': 'grid',
                'js': '1',
                'stats_click': 'search_radio_all%3A1',
                'initiative_id': 'staobaoz_20241125',
                'ie': 'utf8'
            }

            logger.info(f"Searching Taobao products: {category}, page: {page}")
            response = self.make_request(self.search_url, params=params)

            # Extract JSON data from HTML
            products = []
            soup = BeautifulSoup(response.text, 'lxml')

            # Try to find g_page_config JSON data
            scripts = soup.find_all('script')
            for script in scripts:
                if script.string and 'g_page_config' in script.string:
                    try:
                        # Extract JSON data
                        match = re.search(r'g_page_config = ({.+?});', script.string)
                        if match:
                            page_config = json.loads(match.group(1))
                            items = page_config.get('mods', {}).get('itemlist', {}).get('data', {}).get('auctions', [])

                            for item in items:
                                product_data = self.parse_search_item(item)
                                if product_data:
                                    products.append(product_data)

                    except (json.JSONDecodeError, KeyError) as e:
                        logger.warning(f"Failed to parse Taobao search data: {e}")
                        continue

            logger.info(f"Found {len(products)} products on page {page}")
            return products

        except Exception as e:
            logger.error(f"Error searching Taobao products: {e}")
            return []

    def parse_search_item(self, item_data: Dict) -> Optional[Dict[str, Any]]:
        """Parse individual item from search results"""
        try:
            product = {
                'platform': 'taobao',
                'product_id': item_data.get('nid', ''),
                'title': self.clean_text(item_data.get('raw_title', '')),
                'price': self.extract_price(item_data.get('view_price', '')),
                'original_price': self.extract_price(item_data.get('view_fee', '')),
                'sales_count': self.extract_sales_count(item_data.get('view_sales', '')),
                'review_count': int(item_data.get('comment_count', 0)),
                'shop_name': self.clean_text(item_data.get('nick', '')),
                'location': self.clean_text(item_data.get('item_loc', '')),
                'image_url': item_data.get('pic_url', ''),
                'category': settings.platform.mobile_category,
                'source_url': f"https://item.taobao.com/item.htm?id={item_data.get('nid', '')}",
                'tags': []
            }

            # Extract discount rate
            if product['original_price'] and product['price'] and product['original_price'] > product['price']:
                product['discount_rate'] = round((1 - product['price'] / product['original_price']) * 100, 2)

            return product

        except Exception as e:
            logger.warning(f"Error parsing search item: {e}")
            return None

    def get_product_details(self, product_url: str) -> Dict[str, Any]:
        """Get detailed product information from product page"""
        try:
            logger.info(f"Getting product details: {product_url}")
            soup = self.get_page_content(product_url)

            details = {}

            # Extract product title
            title_elem = soup.find('div', class_='tb-detail-hd')
            if title_elem:
                details['title'] = self.clean_text(title_elem.get_text())

            # Extract price
            price_elem = soup.find('em', class_='tb-rmb-num')
            if price_elem:
                details['price'] = self.extract_price(price_elem.get_text())

            # Extract brand
            brand_elem = soup.find('li', {'data-property': '品牌名'})
            if brand_elem:
                details['brand'] = self.clean_text(brand_elem.find('div', class_='tb-property-cont').get_text())

            # Extract shop information
            shop_elem = soup.find('div', class_='tb-shop-name')
            if shop_elem:
                details['shop_name'] = self.clean_text(shop_elem.get_text())

            # Extract product images
            images = []
            img_elems = soup.find_all('img', {'id': re.compile(r'J_ImgBooth')})
            for img in img_elems:
                if img.get('src'):
                    images.append(urljoin(product_url, img['src']))
            details['image_urls'] = images

            # Extract specifications
            specs = {}
            spec_elems = soup.find_all('ul', class_='tb-prop-list')
            for spec_elem in spec_elems:
                prop_name = spec_elem.find('span', class_='tb-property-type')
                prop_value = spec_elem.find('span', class_='tb-property-cont')
                if prop_name and prop_value:
                    specs[self.clean_text(prop_name.get_text())] = self.clean_text(prop_value.get_text())
            details['specifications'] = specs

            return details

        except Exception as e:
            logger.error(f"Error getting product details from {product_url}: {e}")
            return {}

    def get_product_reviews(self, product_id: str, page: int = 1) -> List[Dict[str, Any]]:
        """Get product reviews from Taobao/Tmall"""
        try:
            logger.info(f"Getting reviews for product {product_id}, page {page}")

            params = {
                'itemId': product_id,
                'currentPage': page,
                'pageSize': 20,
                'rateType': '',
                'sortType': 3,  # Sort by time
                'attribute': '',
                'spm': 'a1z09.1.0.0'
            }

            response = self.make_request(self.review_url, params=params)

            # Parse JSON response
            try:
                review_data = response.json()
                reviews = []

                rate_detail = review_data.get('rateDetail', {})
                rate_list = rate_detail.get('rateList', [])

                for review_item in rate_list:
                    review = self.parse_review_item(review_item, product_id)
                    if review:
                        reviews.append(review)

                logger.info(f"Found {len(reviews)} reviews on page {page}")
                return reviews

            except (json.JSONDecodeError, AttributeError) as e:
                logger.warning(f"Failed to parse review data: {e}")
                return []

        except Exception as e:
            logger.error(f"Error getting reviews for product {product_id}: {e}")
            return []

    def parse_review_item(self, review_data: Dict, product_id: str) -> Optional[Dict[str, Any]]:
        """Parse individual review item"""
        try:
            review = {
                'platform': 'taobao',
                'product_id': product_id,
                'review_id': review_data.get('id', ''),
                'user_name': self.clean_text(review_data.get('displayUserNick', 'Anonymous')),
                'rating': int(review_data.get('rate', 0)),
                'content': self.clean_text(review_data.get('rateContent', '')),
                'helpful_count': int(review_data.get('useful', 0)),
                'review_time': self.parse_review_time(review_data.get('rateDate', '')),
                'verified_purchase': review_data.get('goldUser', False),
                'images': [],
                'specifications': review_data.get('auctionSku', ''),
                'is_top_review': review_data.get('tamllSweetLevel', 0) > 0,
                'source_url': f"https://detail.tmall.com/item.htm?id={product_id}"
            }

            # Extract review images
            if 'pics' in review_data and review_data['pics']:
                review['images'] = [pic.get('picUrl', '') for pic in review_data['pics'] if pic.get('picUrl')]

            # Extract pros and cons if available
            if 'appendComment' in review_data:
                review['pros'] = self.clean_text(review_data['appendComment'].get('content', ''))
                review['cons'] = ''

            return review

        except Exception as e:
            logger.warning(f"Error parsing review item: {e}")
            return None

    def extract_sales_count(self, sales_text: str) -> int:
        """Extract sales count from text like '月销1000+'"""
        if not sales_text:
            return 0

        try:
            # Remove non-digit characters and convert to int
            import re
            match = re.search(r'(\d+)', sales_text.replace(',', ''))
            if match:
                return int(match.group(1))
        except (ValueError, AttributeError):
            pass

        return 0

    def parse_review_time(self, time_text: str) -> Optional[str]:
        """Parse review time from text"""
        if not time_text:
            return None

        try:
            # Handle different time formats
            if '年' in time_text and '月' in time_text and '日' in time_text:
                # Format like "2024年01月15日"
                time_text = time_text.replace('年', '-').replace('月', '-').replace('日', '')
                return time_text
            elif '-' in time_text:
                # Format like "2024-01-15"
                return time_text
            else:
                # Default format
                return time_text
        except Exception:
            return time_text