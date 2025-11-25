#!/usr/bin/env python3
"""
Test script to verify SpiderMail functionality
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from spidermail.database.connection import db_manager
from spidermail.config.settings import settings
from spidermail.models import Product, Review, CrawlTask
from sqlalchemy import text

def test_database_connection():
    """Test database connection"""
    print("=== Testing Database Connection ===")
    try:
        engine = db_manager.engine
        with engine.connect() as conn:
            result = conn.execute(text('SELECT version()'))
            version = result.fetchone()[0]
            print(f"Database: PostgreSQL {version[:60]}...")
            return True
    except Exception as e:
        print(f"Database connection failed: {e}")
        return False

def test_database_tables():
    """Test database tables"""
    print("\n=== Testing Database Tables ===")
    try:
        with db_manager.get_session() as session:
            product_count = session.query(Product).count()
            review_count = session.query(Review).count()
            task_count = session.query(CrawlTask).count()

            print(f"Products: {product_count}")
            print(f"Reviews: {review_count}")
            print(f"Tasks: {task_count}")
            return True
    except Exception as e:
        print(f"Database table query failed: {e}")
        return False

def test_configuration():
    """Test configuration"""
    print("\n=== Testing Configuration ===")
    try:
        print(f"Database Host: {settings.database.host}")
        print(f"Database Name: {settings.database.database}")
        print(f"Database User: {settings.database.username}")
        print(f"Request Delay: {settings.spider.request_delay}s")
        print(f"Max Retries: {settings.spider.max_retries}")
        print(f"Taobao URL: {settings.platform.taobao_base_url}")
        print(f"JD URL: {settings.platform.jd_base_url}")
        print(f"Schedule Enabled: {settings.schedule.enabled}")
        print(f"Crawl Time: {settings.schedule.crawl_time}")
        return True
    except Exception as e:
        print(f"Configuration test failed: {e}")
        return False

def main():
    """Main test function"""
    print("SpiderMail System Test")
    print("=" * 40)

    tests = [
        ("Database Connection", test_database_connection),
        ("Database Tables", test_database_tables),
        ("Configuration", test_configuration),
    ]

    passed = 0
    total = len(tests)

    for test_name, test_func in tests:
        if test_func():
            passed += 1
            print(f"[PASS] {test_name}")
        else:
            print(f"[FAIL] {test_name}")

    print(f"\n=== Test Results ===")
    print(f"Passed: {passed}/{total}")

    if passed == total:
        print("All tests passed! SpiderMail is ready to use.")
        return 0
    else:
        print("Some tests failed. Please check the errors above.")
        return 1

if __name__ == "__main__":
    sys.exit(main())