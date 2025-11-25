"""
Data cleaning and validation utilities
"""

import re
import hashlib
from typing import Dict, Any, List, Optional, Union
from datetime import datetime, date
from pydantic import BaseModel, validator, Field
from loguru import logger


class ProductData(BaseModel):
    """Product data validation model"""
    product_id: str = Field(..., min_length=1, max_length=100)
    platform: str = Field(..., regex=r'^(taobao|jd)$')
    title: str = Field(..., min_length=1, max_length=1000)
    brand: Optional[str] = Field(None, max_length=100)
    price: Optional[float] = Field(None, ge=0)
    original_price: Optional[float] = Field(None, ge=0)
    discount_rate: Optional[float] = Field(None, ge=0, le=100)
    sales_count: Optional[int] = Field(0, ge=0)
    review_count: Optional[int] = Field(0, ge=0)
    rating: Optional[float] = Field(None, ge=0, le=5)
    category: Optional[str] = Field(None, max_length=100)
    subcategory: Optional[str] = Field(None, max_length=100)
    image_urls: List[str] = []
    description: Optional[str] = None
    specifications: Optional[Dict[str, Any]] = None
    shop_name: Optional[str] = Field(None, max_length=200)
    shop_url: Optional[str] = Field(None, max_length=500)
    location: Optional[str] = Field(None, max_length=100)
    shipping_info: Optional[str] = None
    tags: List[str] = []
    status: str = Field(default="active", regex=r'^(active|inactive|deleted)$')
    source_url: Optional[str] = Field(None, max_length=1000)

    @validator('discount_rate')
    def calculate_discount_rate(cls, v, values):
        """Auto calculate discount rate if not provided"""
        if v is None and 'price' in values and 'original_price' in values:
            price = values['price']
            original_price = values['original_price']
            if price and original_price and original_price > price:
                return round((1 - price / original_price) * 100, 2)
        return v

    @validator('image_urls', pre=True)
    def filter_image_urls(cls, v):
        """Filter and validate image URLs"""
        if not v:
            return []
        if isinstance(v, str):
            v = [v]
        return [url for url in v if url and cls.is_valid_url(url)]

    @staticmethod
    def is_valid_url(url: str) -> bool:
        """Check if URL is valid"""
        url_pattern = re.compile(
            r'^https?://'  # http:// or https://
            r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+[A-Z]{2,6}\.?|'  # domain...
            r'localhost|'  # localhost...
            r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})'  # ...or ip
            r'(?::\d+)?'  # optional port
            r'(?:/?|[/?]\S+)$', re.IGNORECASE)
        return url_pattern.match(url) is not None


class ReviewData(BaseModel):
    """Review data validation model"""
    review_id: str = Field(..., min_length=1, max_length=100)
    product_id: str = Field(..., min_length=1, max_length=100)
    platform: str = Field(..., regex=r'^(taobao|jd)$')
    user_name: Optional[str] = Field(None, max_length=100)
    user_level: Optional[str] = Field(None, max_length=50)
    rating: int = Field(..., ge=1, le=5)
    content: Optional[str] = None
    pros: Optional[str] = None
    cons: Optional[str] = None
    images: List[str] = []
    helpful_count: Optional[int] = Field(0, ge=0)
    reply_count: Optional[int] = Field(0, ge=0)
    purchase_time: Optional[datetime] = None
    review_time: Optional[datetime] = None
    specifications: Optional[Dict[str, Any]] = None
    verified_purchase: bool = False
    is_top_review: bool = False
    sentiment_score: Optional[float] = Field(None, ge=-1, le=1)
    keywords: List[str] = []
    source_url: Optional[str] = Field(None, max_length=1000)

    @validator('review_time', pre=True)
    def parse_review_time(cls, v):
        """Parse various time formats"""
        if v is None:
            return None
        if isinstance(v, datetime):
            return v
        if isinstance(v, str):
            try:
                # Try common date formats
                for fmt in ['%Y-%m-%d %H:%M:%S', '%Y-%m-%d', '%Y/%m/%d']:
                    try:
                        return datetime.strptime(v, fmt)
                    except ValueError:
                        continue
            except Exception:
                logger.warning(f"Could not parse review time: {v}")
        return None

    @validator('purchase_time', pre=True)
    def parse_purchase_time(cls, v):
        """Parse purchase time"""
        return cls.parse_review_time(v)

    @validator('images', pre=True)
    def filter_review_images(cls, v):
        """Filter and validate review image URLs"""
        if not v:
            return []
        if isinstance(v, str):
            v = [v]
        return [url for url in v if url and ProductData.is_valid_url(url)]

    @validator('content', pre=True)
    def clean_content(cls, v):
        """Clean review content"""
        if not v:
            return ""
        # Remove excessive whitespace
        v = re.sub(r'\s+', ' ', str(v).strip())
        # Remove HTML tags
        v = re.sub(r'<[^>]+>', '', v)
        # Remove special characters that might cause issues
        v = re.sub(r'[^\w\s\u4e00-\u9fa5.,!?()（）。，！？]', '', v)
        return v[:2000]  # Limit content length

    @validator('user_name', pre=True)
    def anonymize_user_name(cls, v):
        """Anonymize user name for privacy"""
        if not v or v == 'Anonymous':
            return 'Anonymous'
        # Keep only first 2-3 characters
        if len(v) > 3:
            return v[:2] + '**'
        return v[:1] + '**'


class DataCleaner:
    """Data cleaning and processing utilities"""

    @staticmethod
    def clean_product_data(raw_data: Dict[str, Any]) -> Optional[ProductData]:
        """Clean and validate product data"""
        try:
            # Generate product ID if not provided
            if not raw_data.get('product_id'):
                raw_data['product_id'] = DataCleaner.generate_product_id(raw_data)

            # Clean and normalize data
            cleaned_data = DataCleaner.normalize_data(raw_data)

            # Validate with Pydantic model
            product = ProductData(**cleaned_data)
            return product

        except Exception as e:
            logger.error(f"Error cleaning product data: {e}, data: {raw_data}")
            return None

    @staticmethod
    def clean_review_data(raw_data: Dict[str, Any]) -> Optional[ReviewData]:
        """Clean and validate review data"""
        try:
            # Generate review ID if not provided
            if not raw_data.get('review_id'):
                raw_data['review_id'] = DataCleaner.generate_review_id(raw_data)

            # Clean and normalize data
            cleaned_data = DataCleaner.normalize_data(raw_data)

            # Add sentiment analysis
            if cleaned_data.get('content'):
                cleaned_data['sentiment_score'] = DataCleaner.analyze_sentiment(cleaned_data['content'])

            # Extract keywords
            if cleaned_data.get('content'):
                cleaned_data['keywords'] = DataCleaner.extract_keywords(cleaned_data['content'])

            # Validate with Pydantic model
            review = ReviewData(**cleaned_data)
            return review

        except Exception as e:
            logger.error(f"Error cleaning review data: {e}, data: {raw_data}")
            return None

    @staticmethod
    def normalize_data(data: Dict[str, Any]) -> Dict[str, Any]:
        """Normalize data types and formats"""
        normalized = {}

        for key, value in data.items():
            if value is None or value == '':
                continue

            # Handle different data types
            if isinstance(value, str):
                # Clean text fields
                value = ' '.join(value.strip().split())
                if value.lower() == 'null' or value.lower() == 'none':
                    continue
            elif isinstance(value, (list, tuple)):
                # Filter out empty values from lists
                value = [v for v in value if v is not None and v != '']
                if not value:
                    continue
            elif isinstance(value, dict):
                # Filter out empty values from dictionaries
                value = {k: v for k, v in value.items() if v is not None and v != ''}

            normalized[key] = value

        return normalized

    @staticmethod
    def generate_product_id(data: Dict[str, Any]) -> str:
        """Generate unique product ID from data"""
        content = f"{data.get('platform', '')}_{data.get('title', '')}_{data.get('price', 0)}"
        return hashlib.md5(content.encode()).hexdigest()[:16]

    @staticmethod
    def generate_review_id(data: Dict[str, Any]) -> str:
        """Generate unique review ID from data"""
        content = f"{data.get('product_id', '')}_{data.get('user_name', '')}_{data.get('review_time', '')}"
        return hashlib.md5(content.encode()).hexdigest()[:16]

    @staticmethod
    def analyze_sentiment(text: str) -> float:
        """Simple sentiment analysis (returns -1 to 1)"""
        if not text:
            return 0.0

        # Simple keyword-based sentiment analysis
        positive_words = [
            '好', '棒', '不错', '满意', '推荐', '值得', '优质', '完美', '优秀',
            'good', 'great', 'excellent', 'amazing', 'perfect', 'love', 'recommend'
        ]
        negative_words = [
            '差', '糟糕', '失望', '不好', '垃圾', '问题', '故障', '缺陷',
            'bad', 'terrible', 'awful', 'disappointed', 'hate', 'worst', 'problem'
        ]

        text_lower = text.lower()
        positive_count = sum(1 for word in positive_words if word in text_lower)
        negative_count = sum(1 for word in negative_words if word in text_lower)

        total_words = positive_count + negative_count
        if total_words == 0:
            return 0.0

        return (positive_count - negative_count) / total_words

    @staticmethod
    def extract_keywords(text: str, max_keywords: int = 10) -> List[str]:
        """Extract keywords from text"""
        if not text:
            return []

        # Simple keyword extraction based on common product features
        product_keywords = [
            '电池', '屏幕', '摄像头', '性能', '价格', '质量', '外观', '手感', '系统',
            '充电', '耐用', '清晰', '流畅', '速度快', '发热', '音质', '拍照',
            'battery', 'screen', 'camera', 'performance', 'price', 'quality', 'design'
        ]

        text_lower = text.lower()
        found_keywords = []

        for keyword in product_keywords:
            if keyword in text_lower:
                found_keywords.append(keyword)

        return found_keywords[:max_keywords]

    @staticmethod
    def validate_data_consistency(product: ProductData, review: ReviewData) -> bool:
        """Validate data consistency between product and review"""
        # Check platform consistency
        if product.platform != review.platform:
            logger.warning(f"Platform mismatch: product={product.platform}, review={review.platform}")
            return False

        # Check product ID consistency
        if product.product_id != review.product_id:
            logger.warning(f"Product ID mismatch: product={product.product_id}, review={review.product_id}")
            return False

        return True

    @staticmethod
    def deduplicate_data(data_list: List[Dict[str, Any]], key_field: str) -> List[Dict[str, Any]]:
        """Remove duplicate data based on key field"""
        seen = set()
        unique_data = []

        for item in data_list:
            key_value = item.get(key_field)
            if key_value and key_value not in seen:
                seen.add(key_value)
                unique_data.append(item)

        return unique_data