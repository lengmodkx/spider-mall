#!/usr/bin/env python3
"""
Example usage of SpiderMail
"""

import os
import sys

# Add src to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from spidermail.spiders.taobao_spider import TaobaoSpider
from spidermail.spiders.jd_spider import JDSpider
from spidermail.utils.data_cleaner import DataCleaner
from spidermail.utils.logger import setup_logger


def main():
    """Example usage"""
    setup_logger()

    print("🕷️ SpiderMail Example")
    print("=" * 30)

    # Test Taobao spider
    print("\n📱 Testing Taobao Spider...")
    try:
        taobao = TaobaoSpider()
        products = taobao.search_products("手机", page=1)
        print(f"Found {len(products)} products from Taobao")

        # Show first product
        if products:
            product = products[0]
            print(f"Sample product: {product.get('title', 'No title')}")
            print(f"Price: {product.get('price', 'No price')}")
            print(f"Shop: {product.get('shop_name', 'No shop')}")

    except Exception as e:
        print(f"Taobao spider error: {e}")

    # Test JD spider
    print("\n📱 Testing JD Spider...")
    try:
        jd = JDSpider()
        products = jd.search_products("手机", page=1)
        print(f"Found {len(products)} products from JD")

        # Show first product
        if products:
            product = products[0]
            print(f"Sample product: {product.get('title', 'No title')}")
            print(f"Price: {product.get('price', 'No price')}")
            print(f"Shop: {product.get('shop_name', 'No shop')}")

    except Exception as e:
        print(f"JD spider error: {e}")

    # Test data cleaning
    print("\n🧹 Testing Data Cleaning...")
    try:
        sample_product = {
            'platform': 'taobao',
            'title': 'Apple iPhone 15 Pro Max 256GB 蓝色',
            'price': '¥9999.00',
            'original_price': '¥10999.00',
            'sales_count': '月销1000+',
            'shop_name': 'Apple官方旗舰店'
        }

        cleaned = DataCleaner.clean_product_data(sample_product)
        if cleaned:
            print(f"Cleaned product: {cleaned.title}")
            print(f"Price: {cleaned.price}")
            print(f"Discount rate: {cleaned.discount_rate}%")

    except Exception as e:
        print(f"Data cleaning error: {e}")

    print("\n✅ Example completed!")


if __name__ == '__main__':
    main()