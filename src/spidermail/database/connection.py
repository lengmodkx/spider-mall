"""
Database connection management
"""

from sqlalchemy import create_engine, MetaData
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import StaticPool
from contextlib import contextmanager
from typing import Generator
import redis

from ..config.settings import settings


class DatabaseManager:
    """Database connection manager"""

    def __init__(self):
        self.engine = create_engine(
            settings.database.url,
            pool_size=settings.database.pool_size,
            max_overflow=settings.database.max_overflow,
            pool_pre_ping=True,
            echo=False
        )
        self.SessionLocal = sessionmaker(
            autocommit=False,
            autoflush=False,
            bind=self.engine
        )
        self.metadata = MetaData()

    def create_tables(self):
        """Create all database tables"""
        from ..models import Base
        Base.metadata.create_all(bind=self.engine)

    def drop_tables(self):
        """Drop all database tables"""
        from ..models import Base
        Base.metadata.drop_all(bind=self.engine)

    @contextmanager
    def get_session(self) -> Generator[Session, None, None]:
        """Get database session with automatic cleanup"""
        session = self.SessionLocal()
        try:
            yield session
            session.commit()
        except Exception:
            session.rollback()
            raise
        finally:
            session.close()

    def get_sync_session(self) -> Session:
        """Get synchronous database session"""
        return self.SessionLocal()


class RedisManager:
    """Redis connection manager for caching and task queue"""

    def __init__(self):
        self.redis_client = redis.Redis(
            host='localhost',
            port=6379,
            db=0,
            decode_responses=True
        )

    def get_client(self) -> redis.Redis:
        """Get Redis client"""
        return self.redis_client

    def ping(self) -> bool:
        """Test Redis connection"""
        try:
            return self.redis_client.ping()
        except redis.ConnectionError:
            return False


# Global database and Redis managers
db_manager = DatabaseManager()
redis_manager = RedisManager()