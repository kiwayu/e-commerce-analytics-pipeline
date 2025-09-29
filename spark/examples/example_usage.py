"""
Example usage of the API ingestion module.
"""

import os
import logging
import sys
from dotenv import load_dotenv

# Add the parent directory to the path so we can import our modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from spark.ingestion import ingest_orders, IngestionConfig
from spark.config import test_database_connection

# Load environment variables
load_dotenv()

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)


def example_basic_ingestion():
    """Example of basic orders ingestion."""
    logger.info("Starting basic orders ingestion example")
    
    # Test database connection first
    if not test_database_connection():
        logger.error("Database connection failed. Please check your configuration.")
        return
    
    # Run ingestion with default configuration
    try:
        stats = ingest_orders()
        
        logger.info("Ingestion completed successfully!")
        logger.info(f"Records fetched: {stats['fetched']}")
        logger.info(f"Records inserted: {stats['inserted']}")
        logger.info(f"Success rate: {stats['success_rate']:.2%}")
        
    except Exception as e:
        logger.error(f"Ingestion failed: {e}")


def example_custom_configuration():
    """Example with custom configuration."""
    logger.info("Starting custom configuration ingestion example")
    
    # Create custom configuration
    config = IngestionConfig(
        page_size=50,                    # Smaller page size
        max_pages=2,                     # Limit to 2 pages
        requests_per_second=2.0,         # More conservative rate limiting
        validate_records=True,           # Enable validation
        skip_invalid_records=True,       # Skip invalid records
        commit_frequency=25               # Commit more frequently
    )
    
    try:
        stats = ingest_orders(config)
        
        logger.info("Custom ingestion completed!")
        logger.info(f"Validation rate: {stats['validation_rate']:.2%}")
        logger.info(f"Duration: {stats['duration_seconds']:.2f} seconds")
        
    except Exception as e:
        logger.error(f"Custom ingestion failed: {e}")


def example_mockaroo_ingestion():
    """Example using Mockaroo API (requires API key)."""
    logger.info("Starting Mockaroo API ingestion example")
    
    # Check if Mockaroo API key is available
    mockaroo_key = os.getenv('MOCKAROO_API_KEY')
    if not mockaroo_key:
        logger.warning("MOCKAROO_API_KEY not found. This example will fall back to JSONPlaceholder.")
    
    config = IngestionConfig(
        mockaroo_api_key=mockaroo_key,
        mockaroo_schema_name='ecommerce_orders',  # Your Mockaroo schema name
        page_size=100,
        max_pages=5
    )
    
    try:
        stats = ingest_orders(config)
        
        logger.info("Mockaroo ingestion completed!")
        logger.info(f"Batch ID: {stats['batch_id']}")
        logger.info(f"Records processed: {stats['fetched']}")
        
    except Exception as e:
        logger.error(f"Mockaroo ingestion failed: {e}")


def example_with_monitoring():
    """Example with detailed monitoring and error handling."""
    logger.info("Starting monitored ingestion example")
    
    config = IngestionConfig(
        page_size=20,
        max_pages=3,
        validate_records=True,
        skip_invalid_records=False  # Don't skip invalid records to see errors
    )
    
    try:
        stats = ingest_orders(config)
        
        # Detailed reporting
        print("\n" + "="*60)
        print("DETAILED INGESTION REPORT")
        print("="*60)
        print(f"Batch ID: {stats['batch_id']}")
        print(f"Start Time: {stats['start_time']}")
        print(f"End Time: {stats['end_time']}")
        print(f"Duration: {stats['duration_seconds']:.2f} seconds")
        print(f"Success: {stats['success']}")
        
        print(f"\nRECORD STATISTICS:")
        print(f"  Fetched: {stats['fetched']}")
        print(f"  Valid: {stats['valid']}")
        print(f"  Invalid: {stats['invalid']}")
        print(f"  Inserted: {stats['inserted']}")
        print(f"  Failed: {stats['failed']}")
        print(f"  Skipped: {stats['skipped']}")
        
        print(f"\nQUALITY METRICS:")
        print(f"  Success Rate: {stats['success_rate']:.2%}")
        print(f"  Validation Rate: {stats['validation_rate']:.2%}")
        
        if stats['error']:
            print(f"\nERROR: {stats['error']}")
        
        print("="*60)
        
    except Exception as e:
        logger.error(f"Monitored ingestion failed: {e}")


if __name__ == "__main__":
    print("E-commerce ETL Pipeline - API Ingestion Examples")
    print("="*50)
    
    # Run examples
    print("\n1. Basic Ingestion Example")
    print("-" * 30)
    example_basic_ingestion()
    
    print("\n2. Custom Configuration Example") 
    print("-" * 30)
    example_custom_configuration()
    
    print("\n3. Mockaroo API Example")
    print("-" * 30)
    example_mockaroo_ingestion()
    
    print("\n4. Monitoring Example")
    print("-" * 30)
    example_with_monitoring()
    
    print("\n" + "="*50)
    print("Examples completed!")


# Environment configuration example
def setup_environment():
    """Example of setting up environment variables."""
    env_example = """
# API Configuration
MOCKAROO_API_KEY=your_mockaroo_api_key_here
API_BASE_URL=https://my.api.mockaroo.com
API_PAGE_SIZE=100
API_MAX_PAGES=10
API_RATE_LIMIT_RPS=5.0
API_RATE_LIMIT_RPM=200
API_MAX_RETRIES=5

# Database Configuration
DWH_POSTGRES_HOST=localhost
DWH_POSTGRES_PORT=5432
DWH_POSTGRES_DB=ecommerce
DWH_POSTGRES_USER=ecommerce_user
DWH_POSTGRES_PASSWORD=ecommerce123

# Ingestion Configuration
VALIDATE_RECORDS=true
SKIP_INVALID_RECORDS=true
DB_BATCH_SIZE=1000

# Logging
SQL_ECHO=false
"""
    
    print("\nTo use this module, create a .env file with the following variables:")
    print(env_example)
