"""
Configuration settings for SpiderMail
"""

import os
from typing import Optional
from pydantic import BaseModel, Field


class DatabaseSettings(BaseModel):
    """Database configuration"""
    host: str = Field(default="localhost")
    port: int = Field(default=5432)
    database: str = Field(default="spidermail")
    username: str = Field(default="postgres")
    password: str = Field(default="")
    pool_size: int = Field(default=10)
    max_overflow: int = Field(default=20)

    @property
    def url(self) -> str:
        """Get database connection URL"""
        return f"postgresql://{self.username}:{self.password}@{self.host}:{self.port}/{self.database}"


class SpiderSettings(BaseModel):
    """Spider configuration"""
    request_delay: float = Field(default=1.0)
    max_retries: int = Field(default=3)
    timeout: int = Field(default=30)
    concurrent_requests: int = Field(default=5)
    user_agent_rotation: bool = Field(default=True)
    proxy_enabled: bool = Field(default=False)
    proxy_list: Optional[str] = Field(default=None)


class PlatformSettings(BaseModel):
    """Platform-specific settings"""
    taobao_base_url: str = Field(default="https://s.taobao.com")
    jd_base_url: str = Field(default="https://search.jd.com")
    mobile_category: str = Field(default="手机")
    max_products_per_page: int = Field(default=100)
    max_reviews_per_product: int = Field(default=1000)


class ScheduleSettings(BaseModel):
    """Task scheduling configuration"""
    enabled: bool = Field(default=True)
    crawl_time: str = Field(default="02:00")  # Daily crawl time
    timezone: str = Field(default="Asia/Shanghai")
    retry_on_failure: bool = Field(default=True)
    max_retry_attempts: int = Field(default=3)


class LoggingSettings(BaseModel):
    """Logging configuration"""
    level: str = Field(default="INFO")
    format: str = Field(
        default="{time:YYYY-MM-DD HH:mm:ss} | {level} | {name}:{function}:{line} | {message}"
    )
    file_path: str = Field(default="logs/spidermail.log")
    max_file_size: str = Field(default="100 MB")
    backup_count: int = Field(default=5)


class Settings(BaseModel):
    """Main settings class"""
    database: DatabaseSettings = DatabaseSettings()
    spider: SpiderSettings = SpiderSettings()
    platform: PlatformSettings = PlatformSettings()
    schedule: ScheduleSettings = ScheduleSettings()
    logging: LoggingSettings = LoggingSettings()


# Global settings instance
settings = Settings()