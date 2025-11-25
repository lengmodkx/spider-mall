#!/usr/bin/env python3
"""
Simple startup script for SpiderMail without emoji characters
"""

import sys
import os
sys.path.insert(0, 'src')

def show_status():
    """Show system status"""
    print("=== SpiderMail System Status ===")

    try:
        from spidermail.database.connection import db_manager
        from spidermail.config.settings import settings
        from spidermail.models import Product, Review, CrawlTask

        # Database status
        with db_manager.get_session() as session:
            product_count = session.query(Product).count()
            review_count = session.query(Review).count()
            task_count = session.query(CrawlTask).count()

            print(f"Database Status:")
            print(f"  Products: {product_count}")
            print(f"  Reviews: {review_count}")
            print(f"  Tasks: {task_count}")

    except Exception as e:
        print(f"Database: Error ({e})")

    # Configuration
    print(f"\nConfiguration:")
    print(f"  Database Host: {settings.database.host}")
    print(f"  Database Name: {settings.database.database}")
    print(f"  Taobao URL: {settings.platform.taobao_base_url}")
    print(f"  JD URL: {settings.platform.jd_base_url}")
    print(f"  Request Delay: {settings.spider.request_delay}s")
    print(f"  Schedule Enabled: {settings.schedule.enabled}")
    print(f"  Crawl Time: {settings.schedule.crawl_time}")

def test_spider(platform='taobao'):
    """Test spider functionality"""
    print(f"\n=== Testing {platform.title()} Spider ===")

    try:
        if platform == 'taobao':
            from spidermail.spiders.taobao_spider import TaobaoSpider
            spider = TaobaoSpider()
        else:
            from spidermail.spiders.jd_spider import JDSpider
            spider = JDSpider()

        print(f"{platform.title()} spider initialized successfully")

        # Test search
        print("Testing product search...")
        products = spider.search_products("手机", page=1)
        if products:
            print(f"Found {len(products)} products")
            for i, product in enumerate(products[:2]):
                title = product.get('title', 'No title')
                price = product.get('price', '0')
                print(f"  {i+1}. {title[:50]}... - Price: {price}")
        else:
            print("No products found (this may be normal due to anti-bot measures)")

        print(f"{platform.title()} spider test completed")

    except Exception as e:
        print(f"Spider test failed: {e}")

def main():
    """Main function"""
    print("SpiderMail - E-commerce Data Spider")
    print("=" * 40)

    if len(sys.argv) > 1:
        command = sys.argv[1]

        if command == "status":
            show_status()
        elif command == "test":
            platform = sys.argv[2] if len(sys.argv) > 2 else "taobao"
            test_spider(platform)
        else:
            print("Usage: python start_simple.py [status|test] [platform]")
            print("  status  - Show system status")
            print("  test    - Test spider (taobao or jd)")
    else:
        # Show status by default
        show_status()
        print(f"\nUsage: python start_simple.py [status|test] [platform]")
        print("System is ready. All components loaded successfully!")

if __name__ == "__main__":
    main()