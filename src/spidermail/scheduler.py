"""
Task scheduler for automated crawling
"""

import schedule
import time
import threading
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Callable
from contextlib import contextmanager
from loguru import logger

from .spiders.taobao_spider import TaobaoSpider
from .spiders.jd_spider import JDSpider
from .database.connection import db_manager
from .models import Product, Review, CrawlTask, PriceHistory
from .utils.data_cleaner import DataCleaner
from .config.settings import settings


class TaskScheduler:
    """Task scheduler for running crawling jobs"""

    def __init__(self):
        self.taobao_spider = TaobaoSpider()
        self.jd_spider = JDSpider()
        self.is_running = False
        self.scheduler_thread = None

    def start(self):
        """Start the scheduler"""
        if settings.schedule.enabled:
            logger.info("Starting task scheduler")
            self.is_running = True

            # Schedule daily crawling tasks
            schedule.every().day.at(settings.schedule.crawl_time).do(
                self.run_daily_crawl, category=settings.platform.mobile_category
            )

            # Schedule hourly data validation and cleanup
            schedule.every().hour.do(self.run_data_maintenance)

            # Start scheduler in separate thread
            self.scheduler_thread = threading.Thread(target=self._run_scheduler, daemon=True)
            self.scheduler_thread.start()
        else:
            logger.info("Scheduler is disabled")

    def stop(self):
        """Stop the scheduler"""
        logger.info("Stopping task scheduler")
        self.is_running = False
        schedule.clear()

    def _run_scheduler(self):
        """Run the scheduler loop"""
        while self.is_running:
            schedule.run_pending()
            time.sleep(60)  # Check every minute

    def run_daily_crawl(self, category: str = "手机"):
        """Run daily crawling task"""
        logger.info(f"Starting daily crawl for category: {category}")

        # Create crawl task record
        task = self._create_crawl_task("daily_crawl", "all", category)

        try:
            # Crawl both platforms
            total_products = 0
            total_reviews = 0

            # Crawl Taobao
            taobao_results = self.crawl_platform_data("taobao", category, task)
            total_products += taobao_results['products']
            total_reviews += taobao_results['reviews']

            # Crawl JD
            jd_results = self.crawl_platform_data("jd", category, task)
            total_products += jd_results['products']
            total_reviews += jd_results['reviews']

            # Update task record
            self._update_crawl_task(task, "completed", total_products, total_reviews)

            logger.info(f"Daily crawl completed: {total_products} products, {total_reviews} reviews")

        except Exception as e:
            logger.error(f"Daily crawl failed: {e}")
            self._update_crawl_task(task, "failed", 0, 0, error_message=str(e))

            # Retry if configured
            if settings.schedule.retry_on_failure:
                self._retry_failed_task(task, category)

    def crawl_platform_data(self, platform: str, category: str, task: CrawlTask) -> Dict[str, int]:
        """Crawl data for a specific platform"""
        if platform == "taobao":
            spider = self.taobao_spider
        elif platform == "jd":
            spider = self.jd_spider
        else:
            raise ValueError(f"Unknown platform: {platform}")

        logger.info(f"Crawling {platform} data for category: {category}")

        products_count = 0
        reviews_count = 0
        max_pages = 5  # Limit pages to avoid overwhelming

        try:
            # Search products
            for page in range(1, max_pages + 1):
                logger.info(f"Crawling {platform} page {page}")

                products = spider.search_products(category, page)
                if not products:
                    logger.info(f"No more products found on {platform} page {page}")
                    break

                # Process each product
                for product_data in products:
                    try:
                        # Clean and save product
                        cleaned_product = DataCleaner.clean_product_data(product_data)
                        if cleaned_product:
                            self._save_product(cleaned_product.dict())
                            products_count += 1

                            # Get product reviews
                            if settings.platform.max_reviews_per_product > 0:
                                self._crawl_product_reviews(spider, cleaned_product.product_id, platform)
                                reviews_count += 1

                    except Exception as e:
                        logger.error(f"Error processing product {product_data.get('product_id')}: {e}")
                        continue

                # Add delay between pages
                time.sleep(settings.spider.request_delay)

        except Exception as e:
            logger.error(f"Error crawling {platform} data: {e}")
            raise

        return {"products": products_count, "reviews": reviews_count}

    def _crawl_product_reviews(self, spider, product_id: str, platform: str):
        """Crawl reviews for a specific product"""
        max_review_pages = 3  # Limit review pages

        for page in range(max_review_pages):
            try:
                reviews = spider.get_product_reviews(product_id, page)
                if not reviews:
                    break

                for review_data in reviews:
                    try:
                        cleaned_review = DataCleaner.clean_review_data(review_data)
                        if cleaned_review:
                            self._save_review(cleaned_review.dict())
                    except Exception as e:
                        logger.error(f"Error saving review: {e}")
                        continue

                time.sleep(settings.spider.request_delay)

            except Exception as e:
                logger.error(f"Error crawling reviews for product {product_id}: {e}")
                break

    def _save_product(self, product_data: Dict):
        """Save product data to database"""
        with db_manager.get_session() as session:
            try:
                # Check if product already exists
                existing_product = session.query(Product).filter(
                    Product.product_id == product_data['product_id']
                ).first()

                if existing_product:
                    # Update existing product
                    for key, value in product_data.items():
                        if hasattr(existing_product, key):
                            setattr(existing_product, key, value)

                    # Add price history if price changed
                    if 'price' in product_data and product_data['price']:
                        price_history = PriceHistory(
                            product_id=product_data['product_id'],
                            platform=product_data['platform'],
                            price=product_data['price'],
                            original_price=product_data.get('original_price'),
                            discount_rate=product_data.get('discount_rate')
                        )
                        session.add(price_history)
                else:
                    # Create new product
                    product = Product(**product_data)
                    session.add(product)

                session.commit()
                logger.debug(f"Saved product: {product_data['product_id']}")

            except Exception as e:
                session.rollback()
                logger.error(f"Error saving product {product_data.get('product_id')}: {e}")
                raise

    def _save_review(self, review_data: Dict):
        """Save review data to database"""
        with db_manager.get_session() as session:
            try:
                # Check if review already exists
                existing_review = session.query(Review).filter(
                    Review.review_id == review_data['review_id']
                ).first()

                if not existing_review:
                    review = Review(**review_data)
                    session.add(review)
                    session.commit()
                    logger.debug(f"Saved review: {review_data['review_id']}")

            except Exception as e:
                session.rollback()
                logger.error(f"Error saving review {review_data.get('review_id')}: {e}")
                raise

    def _create_crawl_task(self, task_name: str, platform: str, category: str) -> CrawlTask:
        """Create a crawl task record"""
        with db_manager.get_session() as session:
            task = CrawlTask(
                task_name=task_name,
                platform=platform,
                category=category,
                status="running",
                start_time=datetime.now()
            )
            session.add(task)
            session.commit()
            session.refresh(task)
            return task

    def _update_crawl_task(self, task: CrawlTask, status: str, products_count: int,
                          reviews_count: int, error_message: str = None):
        """Update crawl task record"""
        with db_manager.get_session() as session:
            try:
                task.status = status
                task.products_found = products_count
                task.reviews_found = reviews_count
                task.end_time = datetime.now()

                if task.start_time:
                    task.duration_seconds = int((task.end_time - task.start_time).total_seconds())

                if error_message:
                    if not task.error_messages:
                        task.error_messages = []
                    task.error_messages.append(error_message)
                    task.errors_count = len(task.error_messages)

                session.commit()
            except Exception as e:
                logger.error(f"Error updating crawl task: {e}")

    def _retry_failed_task(self, task: CrawlTask, category: str):
        """Retry a failed task"""
        logger.info(f"Retrying failed task: {task.task_name}")

        retry_count = 0
        while retry_count < settings.schedule.max_retry_attempts:
            try:
                retry_count += 1
                logger.info(f"Retry attempt {retry_count}/{settings.schedule.max_retry_attempts}")

                # Update task status
                task.status = "running"
                self._update_crawl_task(task, "running", 0, 0)

                # Retry the crawl
                self.run_daily_crawl(category)
                break

            except Exception as e:
                logger.error(f"Retry {retry_count} failed: {e}")
                if retry_count >= settings.schedule.max_retry_attempts:
                    task.status = "failed"
                    self._update_crawl_task(task, "failed", 0, 0, error_message=f"Max retries exceeded: {e}")
                else:
                    time.sleep(60 * retry_count)  # Exponential backoff

    def run_data_maintenance(self):
        """Run data maintenance tasks"""
        logger.info("Running data maintenance")

        try:
            # Clean up old crawl task records (keep last 30 days)
            cutoff_date = datetime.now() - timedelta(days=30)

            with db_manager.get_session() as session:
                deleted_count = session.query(CrawlTask).filter(
                    CrawlTask.created_at < cutoff_date
                ).delete()
                session.commit()

                if deleted_count > 0:
                    logger.info(f"Cleaned up {deleted_count} old crawl task records")

            # Optimize database (if needed)
            self._optimize_database()

        except Exception as e:
            logger.error(f"Data maintenance failed: {e}")

    def _optimize_database(self):
        """Perform database optimization"""
        try:
            with db_manager.get_session() as session:
                # Update statistics
                session.execute("ANALYZE products;")
                session.execute("ANALYZE reviews;")
                session.commit()

        except Exception as e:
            logger.warning(f"Database optimization failed: {e}")

    def run_manual_crawl(self, platform: str, category: str, pages: int = 3):
        """Run manual crawl for testing or immediate data collection"""
        logger.info(f"Starting manual crawl: {platform}, category: {category}, pages: {pages}")

        task = self._create_crawl_task("manual_crawl", platform, category)

        try:
            # Override max_pages for manual crawl
            original_max_pages = 5
            results = self.crawl_platform_data(platform, category, task)

            self._update_crawl_task(task, "completed", results['products'], results['reviews'])

            return {
                "status": "success",
                "products": results['products'],
                "reviews": results['reviews']
            }

        except Exception as e:
            logger.error(f"Manual crawl failed: {e}")
            self._update_crawl_task(task, "failed", 0, 0, error_message=str(e))
            return {
                "status": "failed",
                "error": str(e)
            }


# Global scheduler instance
scheduler = TaskScheduler()