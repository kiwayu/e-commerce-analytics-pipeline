# API Ingestion Module

This module provides a production-ready solution for ingesting orders data from external APIs into PostgreSQL using SQLAlchemy. It includes advanced features like rate limiting, exponential backoff retry logic, pagination handling, and comprehensive error management.

## Features

### 🚀 **Core Functionality**
- **Paginated API Fetching**: Automatically handles API pagination with configurable page sizes
- **Multiple API Sources**: Supports Mockaroo API and JSONPlaceholder with automatic fallback
- **SQLAlchemy Integration**: Full ORM support with PostgreSQL-specific features (JSONB, UUID, etc.)
- **Raw Data Storage**: Stores complete API responses in `raw.raw_orders` table with metadata

### ⚡ **Advanced API Client**
- **Rate Limiting**: Multi-tier rate limiting (per-second, per-minute, per-hour)
- **Exponential Backoff**: Intelligent retry logic with jitter to prevent thundering herd
- **Connection Pooling**: HTTP connection reuse for improved performance
- **Request Statistics**: Built-in metrics tracking for monitoring

### 🛡️ **Resilience & Quality**
- **Comprehensive Error Handling**: Graceful handling of network, API, and database errors
- **Data Validation**: Built-in validation with configurable quality scoring
- **Deduplication**: SHA-256 hashing for duplicate detection
- **Transaction Management**: Proper database transaction handling with rollback support

### 📊 **Monitoring & Observability**
- **Detailed Logging**: Structured logging with configurable levels
- **Batch Tracking**: Unique batch IDs for data lineage
- **Performance Metrics**: Success rates, validation rates, timing statistics
- **Quality Scoring**: Automated data quality assessment

## Quick Start

### 1. Installation

```bash
pip install -r requirements.txt
```

### 2. Environment Setup

Create a `.env` file:
```bash
# Database Configuration
DWH_POSTGRES_HOST=localhost
DWH_POSTGRES_PORT=5432
DWH_POSTGRES_DB=ecommerce
DWH_POSTGRES_USER=ecommerce_user
DWH_POSTGRES_PASSWORD=ecommerce123

# API Configuration (optional)
MOCKAROO_API_KEY=your_mockaroo_api_key
API_PAGE_SIZE=100
API_RATE_LIMIT_RPS=5.0
```

### 3. Basic Usage

```python
from spark.ingestion import ingest_orders

# Run ingestion with default settings
stats = ingest_orders()

print(f"Fetched: {stats['fetched']} orders")
print(f"Inserted: {stats['inserted']} orders")
print(f"Success rate: {stats['success_rate']:.2%}")
```

### 4. Custom Configuration

```python
from spark.ingestion import ingest_orders, IngestionConfig

config = IngestionConfig(
    page_size=50,
    max_pages=10,
    requests_per_second=2.0,
    validate_records=True,
    skip_invalid_records=True
)

stats = ingest_orders(config)
```

## API Sources

### Mockaroo API (Primary)

Mockaroo provides realistic e-commerce test data. Set up a schema with these fields:

```json
{
  "id": "Row Number",
  "customer_id": "Custom List",
  "order_date": "Datetime",
  "status": "Custom List [pending,processing,shipped,delivered]",
  "total": "Money",
  "currency": "Currency Code",
  "payment_method": "Custom List [credit_card,debit_card,paypal]",
  "items": "JSON Array",
  "shipping_address": "JSON Object"
}
```

### JSONPlaceholder (Fallback)

Automatically transforms JSONPlaceholder posts into order-like data when Mockaroo is unavailable.

## Configuration Options

### IngestionConfig Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `api_base_url` | str | mockaroo URL | Base API URL |
| `mockaroo_api_key` | str | None | Mockaroo API key |
| `page_size` | int | 100 | Records per API request |
| `max_pages` | int | None | Maximum pages to fetch |
| `requests_per_second` | float | 5.0 | Rate limit (RPS) |
| `requests_per_minute` | int | 200 | Rate limit (RPM) |
| `max_retries` | int | 5 | Maximum retry attempts |
| `base_delay` | float | 1.0 | Initial retry delay |
| `max_delay` | float | 300.0 | Maximum retry delay |
| `validate_records` | bool | True | Enable data validation |
| `skip_invalid_records` | bool | True | Skip invalid records |
| `batch_size` | int | 1000 | Database batch size |
| `commit_frequency` | int | 100 | Commit every N records |

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `DWH_POSTGRES_HOST` | Database host | localhost |
| `DWH_POSTGRES_PORT` | Database port | 5432 |
| `DWH_POSTGRES_DB` | Database name | ecommerce |
| `DWH_POSTGRES_USER` | Database user | ecommerce_user |
| `DWH_POSTGRES_PASSWORD` | Database password | ecommerce123 |
| `MOCKAROO_API_KEY` | Mockaroo API key | None |
| `API_PAGE_SIZE` | Records per page | 100 |
| `API_RATE_LIMIT_RPS` | Requests per second | 5.0 |
| `VALIDATE_RECORDS` | Enable validation | true |

## Rate Limiting

The module implements sophisticated rate limiting:

### Multi-Tier Limits
- **Per-second**: Prevents overwhelming API servers
- **Per-minute**: Respects API quotas  
- **Per-hour**: Long-term usage limits
- **Burst protection**: Prevents sudden spikes

### Adaptive Backoff
- **Exponential delays**: 1s, 2s, 4s, 8s, etc.
- **Jitter**: Random variation to prevent synchronization
- **Respect server headers**: Honors `Retry-After` headers
- **Circuit breaker**: Automatic fallback on repeated failures

## Data Validation

### Built-in Validations
- **Required fields**: Order ID validation
- **Data types**: Numeric amount validation  
- **Format checks**: Email and currency format
- **Business rules**: Logical consistency checks

### Quality Scoring
```python
# Automatic quality score calculation
score = calculate_quality_score(
    total_fields=10,
    null_fields=2,      # -30% impact
    invalid_fields=1,   # -50% impact  
    duplicate_fields=0  # -20% impact
)
# Returns: 0.85 (85% quality)
```

### Error Tracking
```json
{
  "validation_errors": [
    "Missing required field: id",
    "Invalid email format", 
    "Invalid currency code"
  ]
}
```

## Database Schema

### Raw Orders Table (`raw.raw_orders`)

```sql
CREATE TABLE raw.raw_orders (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    order_id VARCHAR(100) NOT NULL,
    customer_id VARCHAR(100),
    order_date TIMESTAMP WITH TIME ZONE,
    order_status VARCHAR(50),
    total_amount VARCHAR(20),  -- Stored as string for validation
    currency VARCHAR(3),
    payment_method VARCHAR(50),
    
    -- JSONB fields for flexible data
    shipping_address JSONB,
    billing_address JSONB, 
    order_items JSONB,
    
    -- Metadata
    source_system VARCHAR(50) NOT NULL,
    ingestion_timestamp TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    batch_id VARCHAR(100),
    record_hash VARCHAR(64),
    
    -- Data quality
    is_valid BOOLEAN DEFAULT TRUE,
    validation_errors JSONB
);
```

### Key Features
- **UUID Primary Keys**: Ensures uniqueness across systems
- **JSONB Support**: Flexible storage for complex nested data
- **Metadata Tracking**: Complete audit trail with batch IDs
- **Quality Flags**: Built-in validation status tracking
- **Indexes**: Optimized for common query patterns

## Error Handling

### Network Errors
- **Connection timeouts**: Automatic retry with backoff
- **DNS failures**: Exponential backoff with jitter
- **SSL errors**: Comprehensive error logging

### API Errors  
- **HTTP 429**: Respect `Retry-After` headers
- **HTTP 5xx**: Automatic retry with exponential backoff
- **Invalid JSON**: Graceful error handling and logging
- **Empty responses**: Proper validation and error reporting

### Database Errors
- **Connection failures**: Connection pool retry logic  
- **Constraint violations**: Duplicate detection and handling
- **Transaction failures**: Automatic rollback and error logging
- **Deadlocks**: Retry logic for concurrent operations

## Monitoring

### Request Statistics
```python
client = APIClient('https://api.example.com')
stats = client.get_stats()

print(f"Total requests: {stats['total_requests']}")
print(f"Success rate: {stats['success_rate']:.2%}")
print(f"Retry rate: {stats['retry_rate']:.2%}")
```

### Ingestion Metrics
```python
stats = ingest_orders()

{
  'batch_id': 'uuid-string',
  'fetched': 1000,
  'valid': 950, 
  'invalid': 50,
  'inserted': 945,
  'failed': 5,
  'skipped': 50,
  'success_rate': 0.945,
  'validation_rate': 0.95,
  'duration_seconds': 45.2
}
```

### Logging
```python
import logging

# Structured logging with correlation IDs
logger = logging.getLogger('spark.ingestion')
logger.info(
    "Processing batch",
    extra={
        'batch_id': batch_id,
        'page': 1,
        'records': 100
    }
)
```

## Testing

### Running Tests
```bash
# Run all tests
pytest spark/tests/

# Run with coverage
pytest --cov=spark spark/tests/

# Run specific test categories
pytest spark/tests/test_orders_ingestion.py::TestAPIClient
```

### Test Categories
- **Unit Tests**: Individual component testing
- **Integration Tests**: End-to-end data flow
- **Mock Tests**: API response simulation
- **Database Tests**: SQLAlchemy model validation

## Performance Considerations

### Optimization Strategies
- **Connection Pooling**: Reuse HTTP connections
- **Batch Processing**: Commit records in batches
- **Parallel Processing**: Multiple worker processes (future)
- **Memory Management**: Stream processing for large datasets

### Scaling Guidelines
- **Single Process**: Up to 10,000 records/hour
- **Rate Limits**: Respect API provider limits
- **Database Load**: Monitor connection pool usage
- **Memory Usage**: ~1MB per 1000 records

## Production Deployment

### Docker Integration
```dockerfile
FROM python:3.9-slim

WORKDIR /app
COPY spark/ ./spark/
COPY requirements.txt .

RUN pip install -r requirements.txt

CMD ["python", "-m", "spark.ingestion.orders_ingestion"]
```

### Airflow Integration
```python
from airflow import DAG
from airflow.operators.python import PythonOperator
from spark.ingestion import ingest_orders

def ingest_orders_task():
    stats = ingest_orders()
    return stats

dag = DAG('orders_ingestion', schedule='@hourly')

PythonOperator(
    task_id='ingest_orders',
    python_callable=ingest_orders_task,
    dag=dag
)
```

### Monitoring Setup
- **Health Checks**: Database connectivity validation
- **Alerts**: Failed ingestion notifications  
- **Metrics**: Success rates, performance tracking
- **Logging**: Centralized log aggregation

## Troubleshooting

### Common Issues

1. **Database Connection Failures**
   ```bash
   # Check connectivity
   python -c "from spark.config import test_database_connection; print(test_database_connection())"
   ```

2. **API Rate Limiting**
   ```python
   # Reduce rate limits
   config = IngestionConfig(requests_per_second=1.0)
   ```

3. **Memory Issues**
   ```python
   # Reduce batch size
   config = IngestionConfig(batch_size=100, commit_frequency=50)
   ```

4. **Data Quality Issues**
   ```python
   # Enable validation
   config = IngestionConfig(validate_records=True, skip_invalid_records=False)
   ```

### Debug Mode
```python
import logging
logging.getLogger('spark').setLevel(logging.DEBUG)

# Enable SQL echo
os.environ['SQL_ECHO'] = 'true'
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Add tests for new functionality  
4. Run the test suite
5. Submit a pull request

### Code Style
- Follow PEP 8 conventions
- Use type hints where possible
- Write comprehensive docstrings
- Include unit tests for new features

---

This module provides a robust foundation for API data ingestion with enterprise-grade reliability, monitoring, and error handling capabilities.
