"""
Configuration settings for SpiderMail
"""

import os
from typing import Optional
from pydantic import BaseModel, Field


class DatabaseSettings(BaseModel):
    """Database configuration"""
    host: str = Field(default_factory=lambda: os.getenv("DB_HOST", "localhost"))
    port: int = Field(default_factory=lambda: int(os.getenv("DB_PORT", "5432")))
    database: str = Field(default_factory=lambda: os.getenv("DB_NAME", "spidermail"))
    username: str = Field(default_factory=lambda: os.getenv("DB_USER", "postgres"))
    password: str = Field(default_factory=lambda: os.getenv("DB_PASSWORD", ""))
    pool_size: int = Field(default_factory=lambda: int(os.getenv("DB_POOL_SIZE", "10")))
    max_overflow: int = Field(default_factory=lambda: int(os.getenv("DB_MAX_OVERFLOW", "20")))

    @property
    def url(self) -> str:
        """Get database connection URL"""
        return f"postgresql://{self.username}:{self.password}@{self.host}:{self.port}/{self.database}"


class SpiderSettings(BaseModel):
    """Spider configuration"""
    request_delay: float = Field(default_factory=lambda: float(os.getenv("REQUEST_DELAY", "1.0")))
    max_retries: int = Field(default_factory=lambda: int(os.getenv("MAX_RETRIES", "3")))
    timeout: int = Field(default_factory=lambda: int(os.getenv("REQUEST_TIMEOUT", "30")))
    concurrent_requests: int = Field(default_factory=lambda: int(os.getenv("CONCURRENT_REQUESTS", "5")))
    user_agent_rotation: bool = Field(default_factory=lambda: os.getenv("USER_AGENT_ROTATION", "true").lower() == "true")
    proxy_enabled: bool = Field(default_factory=lambda: os.getenv("PROXY_ENABLED", "false").lower() == "true")
    proxy_list: Optional[str] = Field(default_factory=lambda: os.getenv("PROXY_LIST"))


class PlatformSettings(BaseModel):
    """Platform-specific settings"""
    taobao_base_url: str = Field(default_factory=lambda: os.getenv("TAOBAO_BASE_URL", "https://s.taobao.com"))
    jd_base_url: str = Field(default_factory=lambda: os.getenv("JD_BASE_URL", "https://search.jd.com"))
    mobile_category: str = Field(default_factory=lambda: os.getenv("MOBILE_CATEGORY", "手机"))
    max_products_per_page: int = Field(default_factory=lambda: int(os.getenv("MAX_PRODUCTS_PER_PAGE", "100")))
    max_reviews_per_product: int = Field(default_factory=lambda: int(os.getenv("MAX_REVIEWS_PER_PRODUCT", "1000")))


class ScheduleSettings(BaseModel):
    """Task scheduling configuration"""
    enabled: bool = Field(default_factory=lambda: os.getenv("SCHEDULE_ENABLED", "true").lower() == "true")
    crawl_time: str = Field(default_factory=lambda: os.getenv("CRAWL_TIME", "02:00"))  # Daily crawl time
    timezone: str = Field(default_factory=lambda: os.getenv("TIMEZONE", "Asia/Shanghai"))
    retry_on_failure: bool = Field(default_factory=lambda: os.getenv("RETRY_ON_FAILURE", "true").lower() == "true")
    max_retry_attempts: int = Field(default_factory=lambda: int(os.getenv("MAX_RETRY_ATTEMPTS", "3")))


class LoggingSettings(BaseModel):
    """Logging configuration"""
    level: str = Field(default_factory=lambda: os.getenv("LOG_LEVEL", "INFO"))
    format: str = Field(
        default="{time:YYYY-MM-DD HH:mm:ss} | {level} | {name}:{function}:{line} | {message}"
    )
    file_path: str = Field(default_factory=lambda: os.getenv("LOG_FILE_PATH", "logs/spidermail.log"))
    max_file_size: str = Field(default_factory=lambda: os.getenv("LOG_MAX_FILE_SIZE", "100 MB"))
    backup_count: int = Field(default_factory=lambda: int(os.getenv("LOG_BACKUP_COUNT", "5")))


class Settings(BaseModel):
    """Main settings class"""
    database: DatabaseSettings = DatabaseSettings()
    spider: SpiderSettings = SpiderSettings()
    platform: PlatformSettings = PlatformSettings()
    schedule: ScheduleSettings = ScheduleSettings()
    logging: LoggingSettings = LoggingSettings()


# Global settings instance
settings = Settings()