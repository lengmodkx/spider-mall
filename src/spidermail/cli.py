"""
Command Line Interface for SpiderMail
"""

import click
import sys
from pathlib import Path
from loguru import logger

from .database.connection import db_manager
from .scheduler import scheduler
from .config.settings import settings
from .utils.logger import setup_logger
from .utils.exceptions import SpiderMailException


@click.group()
@click.option('--config', '-c', type=click.Path(exists=True), help='Configuration file path')
@click.option('--verbose', '-v', is_flag=True, help='Enable verbose logging')
def cli(config, verbose):
    """SpiderMail - E-commerce data spider for Taobao and JD"""
    setup_logger()

    if verbose:
        logger.remove()
        logger.add(sys.stdout, level="DEBUG")


@cli.command()
@click.option('--host', default='localhost', help='Database host')
@click.option('--port', default=5432, help='Database port')
@click.option('--database', default='spidermail', help='Database name')
@click.option('--username', default='postgres', help='Database username')
@click.option('--password', prompt=True, hide_input=True, help='Database password')
def init_db(host, port, database, username, password):
    """Initialize database with tables"""
    try:
        # Update database settings
        settings.database.host = host
        settings.database.port = port
        settings.database.database = database
        settings.database.username = username
        settings.database.password = password

        # Create tables
        db_manager.create_tables()
        click.echo("✅ Database tables created successfully!")
        logger.info("Database initialized successfully")

    except Exception as e:
        click.echo(f"❌ Database initialization failed: {e}", err=True)
        logger.error(f"Database initialization failed: {e}")
        sys.exit(1)


@cli.command()
def start_scheduler():
    """Start the automated crawling scheduler"""
    try:
        click.echo("🚀 Starting SpiderMail scheduler...")
        scheduler.start()

        click.echo("✅ Scheduler started successfully!")
        click.echo(f"📅 Scheduled daily crawl at: {settings.schedule.crawl_time}")

        # Keep the process running
        try:
            while True:
                import time
                time.sleep(1)
        except KeyboardInterrupt:
            click.echo("\n🛑 Stopping scheduler...")
            scheduler.stop()
            click.echo("✅ Scheduler stopped")

    except Exception as e:
        click.echo(f"❌ Failed to start scheduler: {e}", err=True)
        logger.error(f"Scheduler start failed: {e}")
        sys.exit(1)


@cli.command()
@click.option('--platform', type=click.Choice(['taobao', 'jd', 'all']), default='all', help='Platform to crawl')
@click.option('--category', default='手机', help='Product category to crawl')
@click.option('--pages', default=3, help='Number of pages to crawl')
def crawl(platform, category, pages):
    """Run manual crawling task"""
    try:
        click.echo(f"🕷️  Starting manual crawl...")
        click.echo(f"Platform: {platform}")
        click.echo(f"Category: {category}")
        click.echo(f"Pages: {pages}")

        if platform == 'all':
            # Crawl both platforms
            for p in ['taobao', 'jd']:
                result = scheduler.run_manual_crawl(p, category, pages)
                click.echo(f"📊 {p.title()}: {result['products']} products, {result['reviews']} reviews")
        else:
            # Crawl specific platform
            result = scheduler.run_manual_crawl(platform, category, pages)
            if result['status'] == 'success':
                click.echo(f"✅ {platform.title()}: {result['products']} products, {result['reviews']} reviews")
            else:
                click.echo(f"❌ Failed: {result['error']}", err=True)

    except Exception as e:
        click.echo(f"❌ Manual crawl failed: {e}", err=True)
        logger.error(f"Manual crawl failed: {e}")
        sys.exit(1)


@cli.command()
@click.option('--platform', type=click.Choice(['taobao', 'jd']), required=True, help='Platform to test')
@click.option('--test-search', is_flag=True, help='Test product search')
@click.option('--test-reviews', is_flag=True, help='Test review extraction')
def test_spider(platform, test_search, test_reviews):
    """Test spider functionality"""
    try:
        if platform == 'taobao':
            from .spiders.taobao_spider import TaobaoSpider
            spider = TaobaoSpider()
        else:
            from .spiders.jd_spider import JDSpider
            spider = JDSpider()

        click.echo(f"🧪 Testing {platform.title()} spider...")

        if test_search:
            click.echo("📝 Testing product search...")
            products = spider.search_products("手机", page=1)
            if products:
                click.echo(f"✅ Found {len(products)} products")
                for i, product in enumerate(products[:3]):
                    click.echo(f"  {i+1}. {product.get('title', 'No title')[:50]}...")
            else:
                click.echo("⚠️  No products found")

        if test_reviews:
            click.echo("💬 Testing review extraction...")
            # Use a sample product ID for testing
            test_product_id = "123456789"  # This would need to be a real product ID
            reviews = spider.get_product_reviews(test_product_id, page=1)
            if reviews:
                click.echo(f"✅ Found {len(reviews)} reviews")
                for i, review in enumerate(reviews[:2]):
                    click.echo(f"  {i+1}. Rating: {review.get('rating')}, Content: {review.get('content', '')[:50]}...")
            else:
                click.echo("⚠️  No reviews found")

        click.echo("✅ Spider test completed")

    except Exception as e:
        click.echo(f"❌ Spider test failed: {e}", err=True)
        logger.error(f"Spider test failed: {e}")
        sys.exit(1)


@cli.command()
def status():
    """Show system status"""
    try:
        click.echo("📊 SpiderMail System Status")
        click.echo("=" * 30)

        # Database status
        try:
            with db_manager.get_session() as session:
                from .models import Product, Review, CrawlTask
                product_count = session.query(Product).count()
                review_count = session.query(Review).count()
                task_count = session.query(CrawlTask).count()

                click.echo(f"💾 Database Status:")
                click.echo(f"  Products: {product_count}")
                click.echo(f"  Reviews: {review_count}")
                click.echo(f"  Tasks: {task_count}")

        except Exception as e:
            click.echo(f"💾 Database: ❌ Error ({e})")

        # Scheduler status
        click.echo(f"⏰ Scheduler: {'🟢 Running' if scheduler.is_running else '🔴 Stopped'}")
        click.echo(f"📅 Next crawl: {settings.schedule.crawl_time}")

        # Configuration
        click.echo(f"⚙️  Configuration:")
        click.echo(f"  Platform: {settings.platform.taobao_base_url}")
        click.echo(f"  Category: {settings.platform.mobile_category}")
        click.echo(f"  Delay: {settings.spider.request_delay}s")

    except Exception as e:
        click.echo(f"❌ Status check failed: {e}", err=True)
        sys.exit(1)


@cli.command()
def config():
    """Show current configuration"""
    click.echo("⚙️  Current Configuration")
    click.echo("=" * 25)

    click.echo(f"Database:")
    click.echo(f"  Host: {settings.database.host}")
    click.echo(f"  Port: {settings.database.port}")
    click.echo(f"  Database: {settings.database.database}")
    click.echo(f"  Username: {settings.database.username}")

    click.echo(f"Spider:")
    click.echo(f"  Request Delay: {settings.spider.request_delay}s")
    click.echo(f"  Max Retries: {settings.spider.max_retries}")
    click.echo(f"  Timeout: {settings.spider.timeout}s")
    click.echo(f"  Concurrent Requests: {settings.spider.concurrent_requests}")

    click.echo(f"Schedule:")
    click.echo(f"  Enabled: {settings.schedule.enabled}")
    click.echo(f"  Crawl Time: {settings.schedule.crawl_time}")
    click.echo(f"  Timezone: {settings.schedule.timezone}")

    click.echo(f"Logging:")
    click.echo(f"  Level: {settings.logging.level}")
    click.echo(f"  File: {settings.logging.file_path}")


def main():
    """Main entry point"""
    try:
        cli()
    except KeyboardInterrupt:
        click.echo("\n👋 Goodbye!")
    except SpiderMailException as e:
        click.echo(f"❌ SpiderMail error: {e}", err=True)
        sys.exit(1)
    except Exception as e:
        click.echo(f"❌ Unexpected error: {e}", err=True)
        logger.exception("Unexpected error occurred")
        sys.exit(1)


if __name__ == '__main__':
    main()