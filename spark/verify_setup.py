#!/usr/bin/env python3
"""
Verification script for the API ingestion module setup.
This script tests all components without requiring external dependencies.
"""

import os
import sys
import logging
from typing import Dict, Any

# Add current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_imports():
    """Test that all modules can be imported successfully."""
    print("Testing module imports...")
    
    try:
        # Test config imports
        from config.database import DatabaseConfig, DatabaseManager
        print("[OK] Database configuration imports successful")
        
        # Test model imports
        from models.raw_models import RawOrders, RawCustomers, RawShipments
        print("[OK] SQLAlchemy model imports successful")
        
        # Test ingestion imports
        from ingestion.api_client import APIClient, RateLimitConfig, RetryConfig
        from ingestion.orders_ingestion import OrdersIngestionService, IngestionConfig
        print("[OK] API ingestion imports successful")
        
        return True
        
    except ImportError as e:
        print(f"[ERROR] Import failed: {e}")
        return False


def test_configuration():
    """Test configuration classes."""
    print("\nTesting configuration...")
    
    try:
        from config.database import DatabaseConfig
        from ingestion.orders_ingestion import IngestionConfig
        
        # Test database config
        db_config = DatabaseConfig()
        assert hasattr(db_config, 'connection_string')
        assert hasattr(db_config, 'connection_params')
        print("[OK] Database configuration working")
        
        # Test ingestion config
        ing_config = IngestionConfig()
        assert ing_config.page_size == 100
        assert ing_config.requests_per_second == 5.0
        print("[OK] Ingestion configuration working")
        
        # Test environment config
        env_config = IngestionConfig.from_environment()
        assert env_config.api_base_url is not None
        print("[OK] Environment configuration working")
        
        return True
        
    except Exception as e:
        print(f"[ERROR] Configuration test failed: {e}")
        return False


def test_api_client():
    """Test API client functionality."""
    print("\nTesting API client...")
    
    try:
        from ingestion.api_client import APIClient, RateLimitConfig, RetryConfig
        
        # Test rate limit config
        rate_config = RateLimitConfig(requests_per_second=2.0)
        assert rate_config.min_interval == 0.5
        print("[OK] Rate limiting configuration working")
        
        # Test retry config
        retry_config = RetryConfig(max_retries=3)
        delay = retry_config.calculate_delay(1)
        assert delay >= 1.0
        print("[OK] Retry configuration working")
        
        # Test API client creation
        client = APIClient('https://httpbin.org', rate_limit_config=rate_config)
        assert client.base_url == 'https://httpbin.org'
        stats = client.get_stats()
        assert 'total_requests' in stats
        print("[OK] API client creation working")
        
        return True
        
    except Exception as e:
        print(f"❌ API client test failed: {e}")
        return False


def test_data_models():
    """Test SQLAlchemy data models."""
    print("\nTesting data models...")
    
    try:
        from models.raw_models import RawOrders
        
        # Test model creation from API data
        api_data = {
            'id': 'TEST-001',
            'customer_id': 'CUST-001',
            'order_date': '2024-01-15T10:30:00Z',
            'status': 'pending',
            'total': 99.99,
            'currency': 'USD',
            'items': [{'product_id': 'PROD-1', 'quantity': 1}]
        }
        
        raw_order = RawOrders.from_api_response(
            api_data=api_data,
            source_system='test',
            batch_id='test-batch'
        )
        
        assert raw_order.order_id == 'TEST-001'
        assert raw_order.customer_id == 'CUST-001'
        assert raw_order.source_system == 'test'
        assert raw_order.record_hash is not None
        assert len(raw_order.record_hash) == 64  # SHA-256
        print("✅ RawOrders model working")
        
        # Test datetime parsing
        parsed_date = RawOrders._parse_datetime('2024-01-15T10:30:00Z')
        assert parsed_date is not None
        assert parsed_date.year == 2024
        print("✅ Datetime parsing working")
        
        return True
        
    except Exception as e:
        print(f"❌ Data model test failed: {e}")
        return False


def test_ingestion_service():
    """Test ingestion service functionality."""
    print("\nTesting ingestion service...")
    
    try:
        from ingestion.orders_ingestion import OrdersIngestionService, IngestionConfig
        
        # Test service creation
        config = IngestionConfig(validate_records=True)
        service = OrdersIngestionService(config)
        assert service.config.validate_records is True
        print("✅ Ingestion service creation working")
        
        # Test data validation
        valid_order = {
            'id': 'ORD-123',
            'total': 99.99,
            'currency': 'USD',
            'customer_email': 'test@example.com'
        }
        
        is_valid, errors = service.validate_order_data(valid_order)
        assert is_valid is True
        assert len(errors) == 0
        print("✅ Data validation working")
        
        # Test invalid data
        invalid_order = {
            'total': 'invalid',
            'currency': 'INVALID',
            'customer_email': 'invalid_email'
        }
        
        is_valid, errors = service.validate_order_data(invalid_order)
        assert is_valid is False
        assert len(errors) > 0
        print("✅ Invalid data detection working")
        
        return True
        
    except Exception as e:
        print(f"❌ Ingestion service test failed: {e}")
        return False


def test_example_files():
    """Test that example files are present and valid."""
    print("\nTesting example files...")
    
    try:
        # Check if example file exists and is readable
        example_path = os.path.join(os.path.dirname(__file__), 'examples', 'example_usage.py')
        
        if os.path.exists(example_path):
            with open(example_path, 'r') as f:
                content = f.read()
                assert 'ingest_orders' in content
                assert 'IngestionConfig' in content
            print("✅ Example usage file present and valid")
        else:
            print("⚠️  Example usage file not found")
        
        # Check README
        readme_path = os.path.join(os.path.dirname(__file__), 'README.md')
        if os.path.exists(readme_path):
            with open(readme_path, 'r') as f:
                content = f.read()
                assert 'API Ingestion Module' in content
                assert 'Quick Start' in content
            print("✅ README file present and valid")
        else:
            print("⚠️  README file not found")
        
        return True
        
    except Exception as e:
        print(f"❌ Example files test failed: {e}")
        return False


def run_verification():
    """Run complete verification suite."""
    print("=" * 60)
    print("API INGESTION MODULE VERIFICATION")
    print("=" * 60)
    
    tests = [
        ("Module Imports", test_imports),
        ("Configuration", test_configuration),
        ("API Client", test_api_client),
        ("Data Models", test_data_models),
        ("Ingestion Service", test_ingestion_service),
        ("Example Files", test_example_files),
    ]
    
    results = []
    
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"❌ {test_name} failed with exception: {e}")
            results.append((test_name, False))
    
    # Summary
    print("\n" + "=" * 60)
    print("VERIFICATION SUMMARY")
    print("=" * 60)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{test_name:.<40} {status}")
    
    print("-" * 60)
    print(f"Tests passed: {passed}/{total} ({passed/total*100:.1f}%)")
    
    if passed == total:
        print("\n🎉 All verification tests passed!")
        print("The API ingestion module is ready for use.")
        return True
    else:
        print(f"\n⚠️  {total - passed} test(s) failed.")
        print("Please check the errors above and fix any issues.")
        return False


def show_usage_instructions():
    """Show usage instructions."""
    print("\n" + "=" * 60)
    print("USAGE INSTRUCTIONS")
    print("=" * 60)
    
    instructions = """
1. ENVIRONMENT SETUP:
   Create a .env file with your database credentials:
   
   DWH_POSTGRES_HOST=localhost
   DWH_POSTGRES_PORT=5432
   DWH_POSTGRES_DB=ecommerce
   DWH_POSTGRES_USER=ecommerce_user
   DWH_POSTGRES_PASSWORD=ecommerce123
   MOCKAROO_API_KEY=your_api_key_here

2. BASIC USAGE:
   python -c "from spark.ingestion import ingest_orders; print(ingest_orders())"

3. CUSTOM CONFIGURATION:
   from spark.ingestion import ingest_orders, IngestionConfig
   config = IngestionConfig(page_size=50, max_pages=5)
   stats = ingest_orders(config)

4. RUN EXAMPLES:
   cd spark/examples
   python example_usage.py

5. RUN TESTS:
   cd spark
   python -m pytest tests/

For detailed documentation, see: spark/README.md
"""
    
    print(instructions)


if __name__ == "__main__":
    # Setup minimal logging
    logging.basicConfig(level=logging.WARNING)
    
    success = run_verification()
    
    if success:
        show_usage_instructions()
        sys.exit(0)
    else:
        print("\nRun this script again after fixing the issues.")
        sys.exit(1)
