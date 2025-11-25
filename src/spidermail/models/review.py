"""
Review models
"""

from datetime import datetime
from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean, Numeric, ARRAY, JSON, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.sql import func

Base = declarative_base()


class Review(Base):
    """Review information model"""
    __tablename__ = "reviews"

    id = Column(Integer, primary_key=True, index=True)
    review_id = Column(String(100), unique=True, nullable=False)
    product_id = Column(String(100), nullable=False, index=True)
    platform = Column(String(20), nullable=False, index=True)
    user_name = Column(String(100))
    user_level = Column(String(50))
    rating = Column(Integer, nullable=False, index=True)  # 1-5 stars
    content = Column(Text)
    pros = Column(Text)
    cons = Column(Text)
    images = Column(ARRAY(String))
    helpful_count = Column(Integer, default=0)
    reply_count = Column(Integer, default=0)
    purchase_time = Column(DateTime)
    review_time = Column(DateTime, nullable=False, index=True)
    specifications = Column(JSON)
    verified_purchase = Column(Boolean, default=False)
    is_top_review = Column(Boolean, default=False)
    sentiment_score = Column(Numeric(3, 2))
    keywords = Column(ARRAY(String))
    source_url = Column(String(1000))
    created_at = Column(DateTime, default=func.now())

    def __repr__(self):
        return f"<Review(id={self.id}, product_id={self.product_id}, rating={self.rating})>"