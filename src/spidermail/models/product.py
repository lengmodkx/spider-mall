"""
Product models
"""

from datetime import datetime
from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean, Numeric, ARRAY, JSON
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.sql import func

Base = declarative_base()


class Product(Base):
    """Product information model"""
    __tablename__ = "products"

    id = Column(Integer, primary_key=True, index=True)
    product_id = Column(String(100), unique=True, nullable=False, index=True)
    platform = Column(String(20), nullable=False, index=True)
    title = Column(Text, nullable=False)
    brand = Column(String(100), index=True)
    price = Column(Numeric(10, 2))
    original_price = Column(Numeric(10, 2))
    discount_rate = Column(Numeric(5, 2))
    sales_count = Column(Integer, default=0)
    review_count = Column(Integer, default=0)
    rating = Column(Numeric(3, 2))
    category = Column(String(100), index=True)
    subcategory = Column(String(100))
    image_urls = Column(ARRAY(String))
    description = Column(Text)
    specifications = Column(JSON)
    shop_name = Column(String(200))
    shop_url = Column(String(500))
    location = Column(String(100))
    shipping_info = Column(Text)
    tags = Column(ARRAY(String))
    status = Column(String(20), default="active")
    source_url = Column(String(1000))
    created_at = Column(DateTime, default=func.now(), index=True)
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())

    def __repr__(self):
        return f"<Product(id={self.id}, product_id={self.product_id}, platform={self.platform})>"


class PriceHistory(Base):
    """Price history model"""
    __tablename__ = "price_history"

    id = Column(Integer, primary_key=True, index=True)
    product_id = Column(String(100), nullable=False, index=True)
    platform = Column(String(20), nullable=False)
    price = Column(Numeric(10, 2), nullable=False)
    original_price = Column(Numeric(10, 2))
    discount_rate = Column(Numeric(5, 2))
    recorded_at = Column(DateTime, default=func.now())

    def __repr__(self):
        return f"<PriceHistory(id={self.id}, product_id={self.product_id}, price={self.price})>"