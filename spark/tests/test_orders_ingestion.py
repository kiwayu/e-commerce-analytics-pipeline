"""
Unit tests for orders ingestion functionality.
"""

import pytest
import json
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime
import responses

from ..ingestion.orders_ingestion import (
    OrdersIngestionService, 
    IngestionConfig,
    MockarooAPIClient,
    JSONPlaceholderClient
)
from ..ingestion.api_client import APIClient, RateLimitConfig, RetryConfig
from ..models.raw_models import RawOrders


class TestIngestionConfig:
    """Test IngestionConfig class."""
    
    def test_default_config(self):
        """Test default configuration values."""
        config = IngestionConfig()
        
        assert config.api_base_url == "https://my.api.mockaroo.com"
        assert config.page_size == 100
        assert config.requests_per_second == 5.0
        assert config.max_retries == 5
        assert config.validate_records is True
    
    @patch.dict('os.environ', {
        'API_BASE_URL': 'https://test.api.com',
        'API_PAGE_SIZE': '50',
        'API_RATE_LIMIT_RPS': '10.0',
        'VALIDATE_RECORDS': 'false'
    })
    def test_from_environment(self):
        """Test configuration from environment variables."""
        config = IngestionConfig.from_environment()
        
        assert config.api_base_url == "https://test.api.com"
        assert config.page_size == 50
        assert config.requests_per_second == 10.0
        assert config.validate_records is False


class TestAPIClient:
    """Test APIClient functionality."""
    
    def test_rate_limit_config(self):
        """Test rate limiting configuration."""
        config = RateLimitConfig(
            requests_per_second=2.0,
            requests_per_minute=60
        )
        
        assert config.requests_per_second == 2.0
        assert config.min_interval == 0.5
    
    def test_retry_config(self):
        """Test retry configuration."""
        config = RetryConfig(
            max_retries=3,
            base_delay=1.0,
            exponential_base=2.0
        )
        
        # Test delay calculation
        assert config.calculate_delay(1) >= 1.0
        assert config.calculate_delay(2) >= 2.0
        assert config.calculate_delay(3) >= 4.0
    
    @responses.activate
    def test_successful_request(self):
        """Test successful API request."""
        responses.add(
            responses.GET,
            'https://api.test.com/orders',
            json={'data': [{'id': 1, 'total': 100}]},
            status=200
        )
        
        client = APIClient('https://api.test.com')
        response = client.get('orders')
        
        assert response.status_code == 200
        assert response.json()['data'][0]['id'] == 1
    
    @responses.activate 
    def test_retry_on_failure(self):
        """Test retry logic on API failures."""
        # First request fails, second succeeds
        responses.add(
            responses.GET,
            'https://api.test.com/orders',
            status=500
        )
        responses.add(
            responses.GET,
            'https://api.test.com/orders',
            json={'success': True},
            status=200
        )
        
        config = RetryConfig(max_retries=2, base_delay=0.1)
        client = APIClient('https://api.test.com', retry_config=config)
        
        response = client.get('orders')
        assert response.status_code == 200
        assert len(responses.calls) == 2


class TestMockarooAPIClient:
    """Test Mockaroo API client."""
    
    @responses.activate
    def test_fetch_orders(self):
        """Test fetching orders from Mockaroo."""
        mock_orders = [
            {
                'id': 'ORD-001',
                'customer_id': 'CUST-001',
                'total': 150.00,
                'currency': 'USD'
            },
            {
                'id': 'ORD-002', 
                'customer_id': 'CUST-002',
                'total': 75.50,
                'currency': 'EUR'
            }
        ]
        
        responses.add(
            responses.GET,
            'https://my.api.mockaroo.com/ecommerce_orders.json',
            json=mock_orders,
            status=200
        )
        
        config = IngestionConfig(mockaroo_api_key='test-key')
        client = MockarooAPIClient(config)
        
        orders = client.fetch_orders(count=2)
        
        assert len(orders) == 2
        assert orders[0]['id'] == 'ORD-001'
        assert orders[1]['total'] == 75.50


class TestJSONPlaceholderClient:
    """Test JSONPlaceholder API client."""
    
    @responses.activate
    def test_fetch_orders(self):
        """Test fetching and transforming posts to orders."""
        mock_posts = [
            {
                'id': 1,
                'userId': 1,
                'title': 'Test Product Title',
                'body': 'Product description here'
            },
            {
                'id': 2,
                'userId': 2, 
                'title': 'Another Product',
                'body': 'Another description'
            }
        ]
        
        responses.add(
            responses.GET,
            'https://jsonplaceholder.typicode.com/posts',
            json=mock_posts,
            status=200
        )
        
        config = IngestionConfig()
        client = JSONPlaceholderClient(config)
        
        orders = client.fetch_orders()
        
        assert len(orders) == 2
        assert orders[0]['id'] == 'ORD-000001'
        assert orders[0]['customer_id'] == 'CUST-0001'
        assert 'items' in orders[0]
        assert 'total' in orders[0]


class TestRawOrdersModel:
    """Test RawOrders SQLAlchemy model."""
    
    def test_from_api_response(self):
        """Test creating RawOrders from API response."""
        api_data = {
            'id': 'ORD-123',
            'customer_id': 'CUST-456',
            'order_date': '2024-01-15T10:30:00Z',
            'status': 'pending',
            'total': 99.99,
            'currency': 'USD',
            'items': [
                {'product_id': 'PROD-1', 'quantity': 2, 'price': 49.99}
            ]
        }
        
        raw_order = RawOrders.from_api_response(
            api_data=api_data,
            source_system='test_api',
            batch_id='batch-123'
        )
        
        assert raw_order.order_id == 'ORD-123'
        assert raw_order.customer_id == 'CUST-456'
        assert raw_order.total_amount == '99.99'
        assert raw_order.currency == 'USD'
        assert raw_order.source_system == 'test_api'
        assert raw_order.batch_id == 'batch-123'
        assert raw_order.record_hash is not None
        assert len(raw_order.record_hash) == 64  # SHA-256 hex
    
    def test_datetime_parsing(self):
        """Test datetime parsing with various formats."""
        # Test ISO format
        result = RawOrders._parse_datetime('2024-01-15T10:30:00Z')
        assert result is not None
        assert result.year == 2024
        
        # Test date only
        result = RawOrders._parse_datetime('2024-01-15')
        assert result is not None
        assert result.year == 2024
        
        # Test invalid format
        result = RawOrders._parse_datetime('invalid-date')
        assert result is None


class TestOrdersIngestionService:
    """Test OrdersIngestionService class."""
    
    def setup_method(self):
        """Setup test fixtures."""
        self.config = IngestionConfig(
            page_size=10,
            max_pages=1,
            validate_records=True,
            skip_invalid_records=True
        )
        self.service = OrdersIngestionService(self.config)
    
    def test_validate_order_data_valid(self):
        """Test validation of valid order data."""
        valid_order = {
            'id': 'ORD-123',
            'total': 99.99,
            'currency': 'USD',
            'customer_email': 'test@example.com'
        }
        
        is_valid, errors = self.service.validate_order_data(valid_order)
        
        assert is_valid is True
        assert len(errors) == 0
    
    def test_validate_order_data_invalid(self):
        """Test validation of invalid order data."""
        invalid_order = {
            # Missing 'id' field
            'total': 'invalid_amount',
            'currency': 'INVALID',  # Wrong format
            'customer_email': 'invalid_email'
        }
        
        is_valid, errors = self.service.validate_order_data(invalid_order)
        
        assert is_valid is False
        assert len(errors) > 0
        assert any('Missing required field: id' in error for error in errors)
        assert any('Invalid total amount format' in error for error in errors)
        assert any('Invalid currency code' in error for error in errors)
        assert any('Invalid email format' in error for error in errors)
    
    @patch('spark.ingestion.orders_ingestion.get_database_session')
    def test_store_orders_in_database(self, mock_get_session):
        """Test storing orders in database."""
        # Mock database session
        mock_session = MagicMock()
        mock_get_session.return_value.__enter__.return_value = mock_session
        
        orders = [
            {
                'id': 'ORD-001',
                'total': 100.00,
                'currency': 'USD'
            },
            {
                'id': 'ORD-002',
                'total': 200.00,
                'currency': 'EUR'
            }
        ]
        
        self.service.store_orders_in_database(orders)
        
        # Verify session operations
        assert mock_session.add.call_count == 2
        assert mock_session.commit.call_count >= 1
    
    @patch('spark.config.database.test_database_connection')
    @patch.object(OrdersIngestionService, 'fetch_orders_from_api')
    @patch.object(OrdersIngestionService, 'store_orders_in_database')
    def test_run_ingestion_success(self, mock_store, mock_fetch, mock_test_db):
        """Test successful ingestion run."""
        # Setup mocks
        mock_test_db.return_value = True
        mock_fetch.return_value = [
            {'id': 'ORD-001', 'total': 100},
            {'id': 'ORD-002', 'total': 200}
        ]
        mock_store.return_value = None
        
        # Run ingestion
        result = self.service.run_ingestion()
        
        # Verify results
        assert result['success'] is True
        assert result['fetched'] == 2
        assert 'batch_id' in result
        assert 'duration_seconds' in result
        assert result['error'] is None
    
    @patch('spark.config.database.test_database_connection')
    def test_run_ingestion_db_connection_failure(self, mock_test_db):
        """Test ingestion failure due to database connection."""
        mock_test_db.return_value = False
        
        result = self.service.run_ingestion()
        
        assert result['success'] is False
        assert 'Database connection test failed' in result['error']


# Integration test fixtures
@pytest.fixture
def sample_order_data():
    """Sample order data for testing."""
    return {
        'id': 'ORD-TEST-001',
        'customer_id': 'CUST-TEST-001',
        'order_date': '2024-01-15T10:30:00Z',
        'status': 'pending',
        'total': 150.75,
        'currency': 'USD',
        'payment_method': 'credit_card',
        'items': [
            {
                'product_id': 'PROD-001',
                'name': 'Test Product',
                'quantity': 2,
                'price': 75.37
            }
        ],
        'shipping_address': {
            'street': '123 Test St',
            'city': 'Test City',
            'state': 'TS',
            'postal_code': '12345',
            'country': 'US'
        }
    }


class TestIngestionIntegration:
    """Integration tests for the complete ingestion process."""
    
    def test_end_to_end_data_flow(self, sample_order_data):
        """Test complete data flow from API response to database model."""
        # Create RawOrders from API response
        raw_order = RawOrders.from_api_response(
            api_data=sample_order_data,
            source_system='test_integration',
            batch_id='integration-test-batch'
        )
        
        # Verify all fields are properly mapped
        assert raw_order.order_id == 'ORD-TEST-001'
        assert raw_order.customer_id == 'CUST-TEST-001'
        assert raw_order.total_amount == '150.75'
        assert raw_order.currency == 'USD'
        assert raw_order.payment_method == 'credit_card'
        assert raw_order.source_system == 'test_integration'
        assert raw_order.batch_id == 'integration-test-batch'
        
        # Verify JSONB fields
        assert raw_order.order_items is not None
        assert len(raw_order.order_items) == 1
        assert raw_order.order_items[0]['product_id'] == 'PROD-001'
        
        assert raw_order.shipping_address is not None
        assert raw_order.shipping_address['city'] == 'Test City'
        
        # Verify metadata
        assert raw_order.record_hash is not None
        assert raw_order.ingestion_timestamp is not None
        assert raw_order.is_valid is True
