"""
Orders ingestion module for fetching data from external APIs and storing in PostgreSQL.
"""

import os
import logging
import json
import uuid
from datetime import datetime, timezone
from typing import Dict, Any, List, Optional, Tuple
from dataclasses import dataclass
from contextlib import contextmanager

from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError, IntegrityError
from sqlalchemy import func

from ..config.database import get_database_session, test_database_connection
from ..models.raw_models import RawOrders
from .api_client import APIClient, RateLimitConfig, RetryConfig

logger = logging.getLogger(__name__)


@dataclass
class IngestionConfig:
    """Configuration for orders ingestion."""
    
    # API Configuration
    api_base_url: str = "https://my.api.mockaroo.com"
    api_key: Optional[str] = None
    
    # Mockaroo specific settings
    mockaroo_schema_name: str = "ecommerce_orders"
    mockaroo_api_key: Optional[str] = None
    
    # JSONPlaceholder fallback
    jsonplaceholder_url: str = "https://jsonplaceholder.typicode.com"
    
    # Pagination settings
    page_size: int = 100
    max_pages: Optional[int] = None
    
    # Rate limiting
    requests_per_second: float = 5.0
    requests_per_minute: int = 200
    
    # Retry configuration
    max_retries: int = 5
    base_delay: float = 1.0
    max_delay: float = 300.0
    
    # Database settings
    batch_size: int = 1000
    commit_frequency: int = 100
    
    # Data quality
    validate_records: bool = True
    skip_invalid_records: bool = True
    
    @classmethod
    def from_environment(cls) -> 'IngestionConfig':
        """Create configuration from environment variables."""
        return cls(
            api_base_url=os.getenv('API_BASE_URL', 'https://my.api.mockaroo.com'),
            api_key=os.getenv('API_KEY'),
            mockaroo_schema_name=os.getenv('MOCKAROO_SCHEMA', 'ecommerce_orders'),
            mockaroo_api_key=os.getenv('MOCKAROO_API_KEY'),
            page_size=int(os.getenv('API_PAGE_SIZE', '100')),
            max_pages=int(os.getenv('API_MAX_PAGES', '0')) or None,
            requests_per_second=float(os.getenv('API_RATE_LIMIT_RPS', '5.0')),
            requests_per_minute=int(os.getenv('API_RATE_LIMIT_RPM', '200')),
            max_retries=int(os.getenv('API_MAX_RETRIES', '5')),
            batch_size=int(os.getenv('DB_BATCH_SIZE', '1000')),
            validate_records=os.getenv('VALIDATE_RECORDS', 'true').lower() == 'true',
            skip_invalid_records=os.getenv('SKIP_INVALID_RECORDS', 'true').lower() == 'true'
        )


class MockarooAPIClient:
    """Specialized client for Mockaroo API."""
    
    def __init__(self, config: IngestionConfig):
        self.config = config
        self.base_url = "https://my.api.mockaroo.com"
        
        rate_limit_config = RateLimitConfig(
            requests_per_second=config.requests_per_second,
            requests_per_minute=config.requests_per_minute
        )
        
        retry_config = RetryConfig(
            max_retries=config.max_retries,
            base_delay=config.base_delay,
            max_delay=config.max_delay
        )
        
        headers = {}
        if config.mockaroo_api_key:
            headers['X-API-Key'] = config.mockaroo_api_key
        
        self.client = APIClient(
            base_url=self.base_url,
            rate_limit_config=rate_limit_config,
            retry_config=retry_config,
            headers=headers
        )
    
    def fetch_orders(self, count: int = 100) -> List[Dict[str, Any]]:
        """Fetch orders from Mockaroo API."""
        endpoint = f"{self.config.mockaroo_schema_name}.json"
        params = {'count': count}
        
        if self.config.mockaroo_api_key:
            params['key'] = self.config.mockaroo_api_key
        
        try:
            response = self.client.get(endpoint, params=params)
            data = response.json()
            
            # Ensure we have a list
            if not isinstance(data, list):
                logger.warning("Mockaroo returned non-list data, wrapping in list")
                data = [data] if data else []
            
            logger.info(f"Fetched {len(data)} orders from Mockaroo")
            return data
            
        except Exception as e:
            logger.error(f"Error fetching from Mockaroo: {e}")
            raise
    
    def fetch_paginated_orders(self) -> List[Dict[str, Any]]:
        """Fetch all orders with pagination."""
        all_orders = []
        page = 1
        
        while True:
            if self.config.max_pages and page > self.config.max_pages:
                break
            
            try:
                orders = self.fetch_orders(count=self.config.page_size)
                
                if not orders:
                    logger.info("No more orders available")
                    break
                
                all_orders.extend(orders)
                logger.info(f"Page {page}: fetched {len(orders)} orders (total: {len(all_orders)})")
                
                # If we get fewer than page_size, we've reached the end
                if len(orders) < self.config.page_size:
                    break
                
                page += 1
                
            except Exception as e:
                logger.error(f"Error fetching page {page}: {e}")
                break
        
        return all_orders


class JSONPlaceholderClient:
    """Fallback client for JSONPlaceholder API."""
    
    def __init__(self, config: IngestionConfig):
        self.config = config
        
        rate_limit_config = RateLimitConfig(
            requests_per_second=config.requests_per_second,
            requests_per_minute=config.requests_per_minute
        )
        
        retry_config = RetryConfig(
            max_retries=config.max_retries,
            base_delay=config.base_delay,
            max_delay=config.max_delay
        )
        
        self.client = APIClient(
            base_url=config.jsonplaceholder_url,
            rate_limit_config=rate_limit_config,
            retry_config=retry_config
        )
    
    def fetch_orders(self) -> List[Dict[str, Any]]:
        """Fetch and transform JSONPlaceholder posts as orders."""
        try:
            response = self.client.get("posts")
            posts = response.json()
            
            # Transform posts into order-like data
            orders = []
            for post in posts:
                order = self._transform_post_to_order(post)
                orders.append(order)
            
            logger.info(f"Fetched and transformed {len(orders)} orders from JSONPlaceholder")
            return orders
            
        except Exception as e:
            logger.error(f"Error fetching from JSONPlaceholder: {e}")
            raise
    
    def _transform_post_to_order(self, post: Dict[str, Any]) -> Dict[str, Any]:
        """Transform JSONPlaceholder post into order-like data."""
        import random
        from datetime import datetime, timedelta
        
        # Generate realistic order data from post
        order_id = f"ORD-{post['id']:06d}"
        customer_id = f"CUST-{post['userId']:04d}"
        
        # Random order details
        items = [
            {
                "product_id": f"PROD-{random.randint(1, 1000):04d}",
                "name": post['title'][:50],
                "quantity": random.randint(1, 5),
                "price": round(random.uniform(10.0, 500.0), 2)
            }
        ]
        
        total_amount = sum(item['price'] * item['quantity'] for item in items)
        
        # Random order date within last 30 days
        days_ago = random.randint(0, 30)
        order_date = datetime.now(timezone.utc) - timedelta(days=days_ago)
        
        return {
            "id": order_id,
            "customer_id": customer_id,
            "order_date": order_date.isoformat(),
            "status": random.choice(["pending", "processing", "shipped", "delivered", "cancelled"]),
            "total": total_amount,
            "currency": "USD",
            "payment_method": random.choice(["credit_card", "debit_card", "paypal", "bank_transfer"]),
            "items": items,
            "shipping_address": {
                "street": f"{random.randint(1, 9999)} {post['title'][:20]} St",
                "city": "Sample City",
                "state": "ST",
                "postal_code": f"{random.randint(10000, 99999)}",
                "country": "US"
            },
            "notes": post['body'][:100]
        }


class OrdersIngestionService:
    """Main service for ingesting orders from APIs."""
    
    def __init__(self, config: Optional[IngestionConfig] = None):
        self.config = config or IngestionConfig.from_environment()
        self.batch_id = str(uuid.uuid4())
        self.stats = {
            'fetched': 0,
            'valid': 0,
            'invalid': 0,
            'inserted': 0,
            'failed': 0,
            'skipped': 0
        }
    
    @contextmanager
    def get_db_session(self):
        """Get database session with proper cleanup."""
        session = get_database_session()
        try:
            yield session
            session.commit()
        except Exception as e:
            session.rollback()
            logger.error(f"Database session error: {e}")
            raise
        finally:
            session.close()
    
    def validate_order_data(self, order_data: Dict[str, Any]) -> Tuple[bool, List[str]]:
        """Validate order data and return validation status and errors."""
        if not self.config.validate_records:
            return True, []
        
        errors = []
        
        # Required fields validation
        required_fields = ['id']
        for field in required_fields:
            if not order_data.get(field):
                errors.append(f"Missing required field: {field}")
        
        # Data type validation
        if order_data.get('total'):
            try:
                float(order_data['total'])
            except (ValueError, TypeError):
                errors.append("Invalid total amount format")
        
        # Email validation if present
        if order_data.get('customer_email'):
            email = order_data['customer_email']
            if '@' not in email or '.' not in email:
                errors.append("Invalid email format")
        
        # Currency validation
        if order_data.get('currency'):
            currency = order_data['currency']
            if len(currency) != 3 or not currency.isalpha():
                errors.append("Invalid currency code")
        
        return len(errors) == 0, errors
    
    def fetch_orders_from_api(self) -> List[Dict[str, Any]]:
        """Fetch orders from the configured API source."""
        logger.info(f"Starting orders fetch with batch_id: {self.batch_id}")
        
        # Try Mockaroo first if API key is available
        if self.config.mockaroo_api_key:
            logger.info("Fetching orders from Mockaroo API")
            try:
                client = MockarooAPIClient(self.config)
                orders = client.fetch_paginated_orders()
                logger.info(f"Successfully fetched {len(orders)} orders from Mockaroo")
                return orders
            except Exception as e:
                logger.warning(f"Mockaroo API failed: {e}. Falling back to JSONPlaceholder")
        
        # Fallback to JSONPlaceholder
        logger.info("Fetching orders from JSONPlaceholder API")
        try:
            client = JSONPlaceholderClient(self.config)
            orders = client.fetch_orders()
            logger.info(f"Successfully fetched {len(orders)} orders from JSONPlaceholder")
            return orders
        except Exception as e:
            logger.error(f"All API sources failed: {e}")
            raise
    
    def store_orders_in_database(self, orders: List[Dict[str, Any]]) -> None:
        """Store orders in the raw_orders table."""
        if not orders:
            logger.warning("No orders to store")
            return
        
        logger.info(f"Storing {len(orders)} orders in database")
        
        with self.get_db_session() as session:
            batch_count = 0
            
            for i, order_data in enumerate(orders):
                try:
                    # Validate order data
                    is_valid, validation_errors = self.validate_order_data(order_data)
                    
                    if not is_valid and self.config.skip_invalid_records:
                        logger.warning(f"Skipping invalid order {order_data.get('id', 'unknown')}: {validation_errors}")
                        self.stats['invalid'] += 1
                        self.stats['skipped'] += 1
                        continue
                    
                    # Create RawOrders instance
                    raw_order = RawOrders.from_api_response(
                        api_data=order_data,
                        source_system='api',
                        batch_id=self.batch_id
                    )
                    
                    # Set validation info
                    if not is_valid:
                        raw_order.is_valid = False
                        raw_order.validation_errors = validation_errors
                        self.stats['invalid'] += 1
                    else:
                        self.stats['valid'] += 1
                    
                    # Add to session
                    session.add(raw_order)
                    batch_count += 1
                    
                    # Commit in batches
                    if batch_count >= self.config.commit_frequency:
                        session.commit()
                        self.stats['inserted'] += batch_count
                        logger.debug(f"Committed batch of {batch_count} orders")
                        batch_count = 0
                
                except IntegrityError as e:
                    session.rollback()
                    logger.warning(f"Duplicate order {order_data.get('id', 'unknown')}: {e}")
                    self.stats['skipped'] += 1
                    batch_count = 0
                
                except Exception as e:
                    session.rollback()
                    logger.error(f"Error storing order {order_data.get('id', 'unknown')}: {e}")
                    self.stats['failed'] += 1
                    batch_count = 0
            
            # Commit remaining orders
            if batch_count > 0:
                session.commit()
                self.stats['inserted'] += batch_count
                logger.debug(f"Committed final batch of {batch_count} orders")
    
    def run_ingestion(self) -> Dict[str, Any]:
        """
        Run the complete ingestion process.
        
        Returns:
            Dictionary containing ingestion statistics
        """
        start_time = datetime.now(timezone.utc)
        
        try:
            # Test database connection
            if not test_database_connection():
                raise RuntimeError("Database connection test failed")
            
            # Fetch orders from API
            logger.info("Starting orders ingestion process")
            orders = self.fetch_orders_from_api()
            self.stats['fetched'] = len(orders)
            
            if not orders:
                logger.warning("No orders fetched from API")
                return self._get_final_stats(start_time)
            
            # Store orders in database
            self.store_orders_in_database(orders)
            
            # Log final statistics
            end_time = datetime.now(timezone.utc)
            duration = (end_time - start_time).total_seconds()
            
            logger.info(
                f"Ingestion completed in {duration:.2f}s. "
                f"Fetched: {self.stats['fetched']}, "
                f"Valid: {self.stats['valid']}, "
                f"Invalid: {self.stats['invalid']}, "
                f"Inserted: {self.stats['inserted']}, "
                f"Failed: {self.stats['failed']}, "
                f"Skipped: {self.stats['skipped']}"
            )
            
            return self._get_final_stats(start_time)
        
        except Exception as e:
            logger.error(f"Ingestion process failed: {e}")
            return self._get_final_stats(start_time, error=str(e))
    
    def _get_final_stats(self, start_time: datetime, error: Optional[str] = None) -> Dict[str, Any]:
        """Get final ingestion statistics."""
        end_time = datetime.now(timezone.utc)
        duration = (end_time - start_time).total_seconds()
        
        stats = self.stats.copy()
        stats.update({
            'batch_id': self.batch_id,
            'start_time': start_time.isoformat(),
            'end_time': end_time.isoformat(),
            'duration_seconds': duration,
            'success': error is None,
            'error': error
        })
        
        if stats['fetched'] > 0:
            stats['success_rate'] = stats['inserted'] / stats['fetched']
            stats['validation_rate'] = stats['valid'] / stats['fetched']
        else:
            stats['success_rate'] = 0.0
            stats['validation_rate'] = 0.0
        
        return stats


def ingest_orders(config: Optional[IngestionConfig] = None) -> Dict[str, Any]:
    """
    Main function to ingest orders from API into PostgreSQL.
    
    Args:
        config: Optional ingestion configuration
        
    Returns:
        Dictionary containing ingestion statistics
    """
    service = OrdersIngestionService(config)
    return service.run_ingestion()


# Example usage and testing
if __name__ == "__main__":
    import sys
    
    # Setup logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(sys.stdout),
            logging.FileHandler('orders_ingestion.log')
        ]
    )
    
    # Run ingestion
    try:
        config = IngestionConfig.from_environment()
        stats = ingest_orders(config)
        
        print("\n" + "="*50)
        print("INGESTION SUMMARY")
        print("="*50)
        print(f"Batch ID: {stats['batch_id']}")
        print(f"Duration: {stats['duration_seconds']:.2f}s")
        print(f"Records Fetched: {stats['fetched']}")
        print(f"Valid Records: {stats['valid']}")
        print(f"Invalid Records: {stats['invalid']}")
        print(f"Records Inserted: {stats['inserted']}")
        print(f"Records Failed: {stats['failed']}")
        print(f"Records Skipped: {stats['skipped']}")
        print(f"Success Rate: {stats['success_rate']:.2%}")
        print(f"Validation Rate: {stats['validation_rate']:.2%}")
        
        if stats['error']:
            print(f"Error: {stats['error']}")
            sys.exit(1)
        else:
            print("✅ Ingestion completed successfully!")
        
    except Exception as e:
        logger.error(f"Ingestion failed: {e}")
        print(f"❌ Ingestion failed: {e}")
        sys.exit(1)
