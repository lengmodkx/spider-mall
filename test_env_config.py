#!/usr/bin/env python3
"""
Test environment variable configuration
"""

import os
import sys
sys.path.insert(0, 'src')

def test_env_config():
    """Test that environment variables are properly loaded"""

    # Set test environment variables
    os.environ['DB_HOST'] = 'test_host'
    os.environ['DB_PORT'] = '9999'
    os.environ['DB_NAME'] = 'test_db'
    os.environ['DB_USER'] = 'test_user'
    os.environ['DB_PASSWORD'] = 'test_password'
    os.environ['REQUEST_DELAY'] = '2.5'
    os.environ['LOG_LEVEL'] = 'DEBUG'

    # Import and test settings
    from spidermail.config.settings import settings

    print("=== Environment Variable Configuration Test ===")
    print(f"Database Host: {settings.database.host}")
    print(f"Database Port: {settings.database.port}")
    print(f"Database Name: {settings.database.database}")
    print(f"Database User: {settings.database.username}")
    print(f"Database Password: {'*' * len(settings.database.password)}")
    print(f"Request Delay: {settings.spider.request_delay}")
    print(f"Log Level: {settings.logging.level}")

    # Test that environment variables are working
    success = (
        settings.database.host == 'test_host' and
        settings.database.port == 9999 and
        settings.database.database == 'test_db' and
        settings.database.username == 'test_user' and
        settings.database.password == 'test_password' and
        settings.spider.request_delay == 2.5 and
        settings.logging.level == 'DEBUG'
    )

    print(f"\nEnvironment variables working: {'✓' if success else '✗'}")
    return success

if __name__ == "__main__":
    test_env_config()