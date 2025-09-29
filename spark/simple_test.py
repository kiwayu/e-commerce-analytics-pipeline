"""
Simple test script for API ingestion module functionality.
"""

def test_basic_functionality():
    """Test basic functionality without external dependencies."""
    print("Testing API ingestion module...")
    
    try:
        # Test imports
        print("1. Testing imports...")
        from ingestion.api_client import APIClient, RateLimitConfig, RetryConfig
        from models.raw_models import RawOrders
        from config.database import DatabaseConfig
        print("   [OK] All imports successful")
        
        # Test configuration
        print("2. Testing configuration...")
        rate_config = RateLimitConfig(requests_per_second=2.0)
        assert rate_config.min_interval == 0.5
        print("   [OK] Rate limiting configuration working")
        
        # Test data model
        print("3. Testing data model...")
        api_data = {
            'id': 'TEST-001',
            'total': 99.99,
            'currency': 'USD'
        }
        raw_order = RawOrders.from_api_response(api_data, 'test')
        assert raw_order.order_id == 'TEST-001'
        assert raw_order.record_hash is not None
        print("   [OK] Data model creation working")
        
        # Test validation
        print("4. Testing validation...")
        from ingestion.orders_ingestion import OrdersIngestionService, IngestionConfig
        config = IngestionConfig()
        service = OrdersIngestionService(config)
        
        valid_order = {'id': 'ORD-123', 'total': 99.99, 'currency': 'USD'}
        is_valid, errors = service.validate_order_data(valid_order)
        assert is_valid is True
        print("   [OK] Data validation working")
        
        print("\nAll tests passed! The module is ready for use.")
        return True
        
    except Exception as e:
        print(f"   [ERROR] Test failed: {e}")
        return False


if __name__ == "__main__":
    success = test_basic_functionality()
    
    if success:
        print("\nModule verification successful!")
        print("\nNext steps:")
        print("1. Set up your .env file with database credentials")
        print("2. Install dependencies: pip install -r requirements.txt")
        print("3. Run: python -c \"from ingestion import ingest_orders; print(ingest_orders())\"")
    else:
        print("\nModule verification failed. Please check the errors above.")
