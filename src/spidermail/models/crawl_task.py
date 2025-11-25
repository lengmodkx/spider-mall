"""
Crawl task models
"""

from datetime import datetime
from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean, ARRAY, JSON
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.sql import func

Base = declarative_base()


class CrawlTask(Base):
    """Crawl task tracking model"""
    __tablename__ = "crawl_tasks"

    id = Column(Integer, primary_key=True, index=True)
    task_name = Column(String(100), nullable=False)
    platform = Column(String(20), nullable=False, index=True)
    category = Column(String(100))
    status = Column(String(20), default="running", index=True)  # running, completed, failed
    products_found = Column(Integer, default=0)
    reviews_found = Column(Integer, default=0)
    errors_count = Column(Integer, default=0)
    error_messages = Column(ARRAY(Text))
    start_time = Column(DateTime, nullable=False)
    end_time = Column(DateTime)
    duration_seconds = Column(Integer)
    created_at = Column(DateTime, default=func.now())

    def __repr__(self):
        return f"<CrawlTask(id={self.id}, name={self.task_name}, platform={self.platform}, status={self.status})>"