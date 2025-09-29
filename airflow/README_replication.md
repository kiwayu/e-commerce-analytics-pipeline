# 🔄 Airflow Database Replication System

A comprehensive, production-ready Airflow solution for incremental database replication using high-water mark strategy with automatic watermark management.

## 🎯 Overview

This system provides enterprise-grade incremental replication from source PostgreSQL tables to data warehouse tables using:

- **High-Water Mark Strategy**: Tracks last processed timestamp using `updated_at` columns
- **Airflow Variables**: Persistent watermark storage with backup/recovery
- **Custom Operators**: Purpose-built for replication workflows
- **Data Quality Validation**: Comprehensive quality checks and business rules
- **Error Recovery**: Robust error handling with automatic retry logic
- **Monitoring & Alerting**: Real-time health checks and lag monitoring

## 🏗️ Architecture

### Component Structure
```
airflow/
├── plugins/
│   ├── hooks/
│   │   ├── postgres_replication_hook.py    # Database connectivity & operations
│   │   └── __init__.py
│   ├── operators/
│   │   ├── incremental_replication_operator.py  # Main replication logic
│   │   └── __init__.py
│   └── __init__.py                         # Plugin registration
├── dags/
│   ├── incremental_replication_dag.py     # Production replication DAG
│   └── utils/
│       └── replication_utils.py           # Utility functions
├── test_replication.py                    # Validation tests
└── README_replication.md                  # This documentation
```

### Data Flow
```
Source DB → Watermark Check → Incremental Extract → Quality Validation → Target DB → Watermark Update
    ↓              ↓                 ↓                    ↓               ↓            ↓
PostgreSQL    Airflow Vars    Custom Hook        Data Validator    PostgreSQL   Airflow Vars
```

## 🚀 Quick Start

### 1. Setup Airflow Connections

```bash
# Source database connection
airflow connections add postgres_source \
    --conn-type postgres \
    --conn-host source-db.company.com \
    --conn-login readonly_user \
    --conn-password secret123 \
    --conn-schema production

# Target data warehouse connection  
airflow connections add postgres_dwh \
    --conn-type postgres \
    --conn-host dwh.company.com \
    --conn-login dwh_user \
    --conn-password secret456 \
    --conn-schema warehouse
```

### 2. Deploy Components

```bash
# Copy to Airflow directories
cp -r airflow/plugins/* $AIRFLOW_HOME/plugins/
cp -r airflow/dags/* $AIRFLOW_HOME/dags/

# Restart Airflow services
systemctl restart airflow-webserver airflow-scheduler
```

### 3. Enable DAGs

```bash
# Enable the replication DAG
airflow dags unpause incremental_customer_replication

# Enable monitoring DAG
airflow dags unpause replication_health_monitoring
```

### 4. Monitor Execution

- **Airflow UI**: View DAG runs and task logs
- **Watermarks**: Check `Admin > Variables` for watermark values
- **Logs**: Monitor task execution details

## 📊 Key Features

### 🔧 **IncrementalReplicationOperator**

Production-ready operator for incremental replication:

```python
from operators.incremental_replication_operator import IncrementalReplicationOperator

replicate_customers = IncrementalReplicationOperator(
    task_id='replicate_customers',
    source_table='raw.raw_customers',
    target_table='staging.customers',
    source_conn_id='postgres_source',
    target_conn_id='postgres_dwh',
    watermark_column='updated_at',
    primary_key_columns=['customer_id'],
    replication_mode='upsert',  # or 'insert'
    batch_size=5000,
    max_records_per_run=50000,
    quality_checks={
        'null_check': {
            'columns': ['customer_id', 'email'],
            'max_null_percentage': 0
        },
        'duplicate_check': {
            'columns': ['customer_id'],
            'max_duplicates': 0
        }
    },
    watermark_lag_tolerance=timedelta(hours=6),
    skip_if_no_data=True
)
```

### 💧 **Watermark Management**

Automatic watermark tracking with Airflow Variables:

```python
from utils.replication_utils import WatermarkManager

# Get current watermark
watermark = WatermarkManager.get_watermark('customers', 'updated_at')

# Set new watermark
WatermarkManager.set_watermark('customers', datetime.now())

# Backup before risky operations
WatermarkManager.backup_watermark('customers')

# Restore from backup
WatermarkManager.restore_watermark('customers')

# List all watermarks
all_watermarks = WatermarkManager.list_all_watermarks()
```

### 🛡️ **Data Quality Validation**

Comprehensive quality checks:

```python
quality_checks = {
    'null_check': {
        'columns': ['customer_id', 'email', 'registration_date'],
        'max_null_percentage': 0,  # No nulls allowed
        'fail_on_error': True
    },
    'duplicate_check': {
        'columns': ['customer_id'],
        'max_duplicates': 0,
        'fail_on_error': True
    },
    'value_range_check': {
        'registration_date': {
            'min': datetime(2020, 1, 1),
            'max': datetime.now() + timedelta(days=1)
        },
        'age': {
            'min': 0,
            'max': 150
        }
    },
    'record_count_check': {
        'min_records': 0,
        'max_records': 100000,
        'fail_on_error': False  # Warning only
    }
}
```

### 📈 **Monitoring & Health Checks**

Real-time monitoring with `ReplicationValidationOperator`:

```python
from operators.incremental_replication_operator import ReplicationValidationOperator

health_check = ReplicationValidationOperator(
    task_id='check_replication_health',
    source_table='raw.raw_customers',
    target_table='staging.customers',
    max_lag_hours=2,  # Alert if lag > 2 hours
    source_conn_id='postgres_source',
    target_conn_id='postgres_dwh'
)
```

## 🔍 Replication Modes

### **Insert Mode**
- Appends new records to target table
- Suitable for append-only scenarios
- Faster performance for large datasets

### **Upsert Mode** 
- INSERT with ON CONFLICT DO UPDATE
- Handles both new and updated records
- Requires primary key columns specification
- Ideal for slowly changing dimensions

## 📊 DAG Configuration

### Main Replication DAG

**Schedule**: Every 30 minutes
**SLA**: 2 hours
**Retries**: 2 with 5-minute delay

**Task Flow**:
1. `check_source_data_availability` - SQL sensor for new data
2. `check_prerequisites` - Validate setup and connections
3. `pre_replication_validation` - Health check before replication
4. `replicate_customers` - Main replication task
5. `post_replication_validation` - Data validation after load
6. `final_validation` - Final health check
7. `send_success_notification` - Success email notification

**Error Handling**:
- `send_failure_notification` - Failure alerts (runs on ANY failure)

### Health Monitoring DAG

**Schedule**: Every hour
**Purpose**: Continuous health monitoring

**Tasks**:
- `check_replication_health` - Monitor lag and data consistency
- `send_health_alert` - Alert on health issues

## 🔧 Configuration Examples

### Basic Customer Replication

```python
# Simple append-only replication
customer_replication = IncrementalReplicationOperator(
    task_id='replicate_customers',
    source_table='raw.raw_customers',
    target_table='staging.customers',
    replication_mode='insert',
    watermark_column='created_at',
    batch_size=10000
)
```

### Advanced Order Replication with Quality Checks

```python
# Complex upsert with extensive validation
order_replication = IncrementalReplicationOperator(
    task_id='replicate_orders',
    source_table='raw.raw_orders',
    target_table='staging.orders',
    primary_key_columns=['order_id'],
    replication_mode='upsert',
    watermark_column='updated_at',
    additional_filters="status != 'cancelled'",
    quality_checks={
        'null_check': {
            'columns': ['order_id', 'customer_id', 'total_amount'],
            'max_null_percentage': 0
        },
        'value_range_check': {
            'total_amount': {'min': 0, 'max': 100000},
            'order_date': {
                'min': datetime(2020, 1, 1),
                'max': datetime.now()
            }
        }
    },
    watermark_lag_tolerance=timedelta(hours=1),
    max_records_per_run=25000
)
```

## 📊 Monitoring & Metrics

### Airflow Variables Tracking

The system automatically tracks watermarks in Airflow Variables:

```
Variable Key: replication_watermark_customers_updated_at
Value: 2024-01-15T10:30:00.123456+00:00

Variable Key: replication_watermark_orders_updated_at  
Value: 2024-01-15T10:25:00.654321+00:00
```

### XCom Results

Each replication task stores detailed results in XCom:

```json
{
  "task_id": "replicate_customers",
  "source_table": "raw.raw_customers",
  "target_table": "staging.customers",
  "replication_mode": "upsert",
  "start_time": "2024-01-15T10:30:00",
  "end_time": "2024-01-15T10:32:30",
  "duration_seconds": 150.5,
  "records_extracted": 5000,
  "records_loaded": 4995,
  "watermark_updated": true,
  "previous_watermark": "2024-01-15T08:00:00+00:00",
  "new_watermark": "2024-01-15T10:30:00+00:00",
  "records_per_second": 33.2,
  "success": true,
  "upsert_stats": {
    "inserted": 4500,
    "updated": 495
  }
}
```

### Health Metrics

```json
{
  "source": {
    "total_rows": 1000000,
    "rows_with_watermark": 999950,
    "min_watermark": "2020-01-01T00:00:00+00:00",
    "max_watermark": "2024-01-15T10:30:00+00:00"
  },
  "target": {
    "total_rows": 995000
  },
  "current_watermark": "2024-01-15T10:25:00+00:00",
  "lag_seconds": 300,
  "lag_hours": 0.083,
  "is_lagging": false
}
```

## 🚨 Error Handling

### Automatic Recovery

- **Connection Failures**: Automatic retry with exponential backoff
- **Data Quality Issues**: Configurable fail/warn behavior
- **Watermark Corruption**: Automatic backup and recovery
- **Partial Failures**: Continue processing remaining batches

### Error Notifications

```python
# Failure notification includes:
{
  'dag_id': 'incremental_customer_replication',
  'task_id': 'replicate_customers', 
  'execution_date': '2024-01-15T10:30:00+00:00',
  'error_info': {
    'error': 'Connection timeout to source database',
    'task_id': 'replicate_customers',
    'source_table': 'raw.raw_customers',
    'target_table': 'staging.customers'
  },
  'log_url': 'http://airflow.company.com/log?...'
}
```

### Manual Recovery Procedures

```bash
# Reset watermark to specific timestamp
airflow variables set replication_watermark_customers_updated_at "2024-01-15T09:00:00+00:00"

# Clear failed task instance
airflow tasks clear incremental_customer_replication replicate_customers -s 2024-01-15T10:30:00

# Backup current watermarks
python -c "
from utils.replication_utils import WatermarkManager
WatermarkManager.backup_watermark('customers')
"
```

## 🔒 Security & Best Practices

### Database Permissions

**Source Database (Read-Only)**:
```sql
-- Create read-only user
CREATE USER replication_reader WITH PASSWORD 'secure_password';
GRANT CONNECT ON DATABASE production TO replication_reader;
GRANT USAGE ON SCHEMA raw TO replication_reader;
GRANT SELECT ON ALL TABLES IN SCHEMA raw TO replication_reader;
GRANT SELECT ON ALL SEQUENCES IN SCHEMA raw TO replication_reader;

-- Grant future table access
ALTER DEFAULT PRIVILEGES IN SCHEMA raw GRANT SELECT ON TABLES TO replication_reader;
```

**Target Database (Write Access)**:
```sql
-- Create ETL user
CREATE USER dwh_writer WITH PASSWORD 'secure_password';
GRANT CONNECT ON DATABASE warehouse TO dwh_writer;
GRANT USAGE ON SCHEMA staging TO dwh_writer;
GRANT INSERT, UPDATE, DELETE ON ALL TABLES IN SCHEMA staging TO dwh_writer;
GRANT USAGE ON ALL SEQUENCES IN SCHEMA staging TO dwh_writer;
```

### Connection Security

- Use Airflow's encrypted connection storage
- Rotate passwords regularly
- Use connection pooling to limit concurrent connections
- Implement network-level security (VPC, firewalls)

### Monitoring Security

- Log all replication activities
- Monitor for unusual data patterns
- Alert on failed authentication attempts
- Track watermark changes for audit trails

## 🚀 Performance Optimization

### Batch Size Tuning

```python
# For large tables (>1M rows)
batch_size=20000
max_records_per_run=100000

# For small tables (<100K rows)  
batch_size=5000
max_records_per_run=50000

# For high-frequency changes
batch_size=1000
max_records_per_run=10000
```

### Database Optimization

**Source Database**:
```sql
-- Index on watermark column
CREATE INDEX CONCURRENTLY idx_customers_updated_at ON raw_customers(updated_at);

-- Partial index for active records
CREATE INDEX CONCURRENTLY idx_customers_updated_at_active 
ON raw_customers(updated_at) WHERE status = 'active';
```

**Target Database**:
```sql
-- Unique constraint for upsert operations
ALTER TABLE staging.customers ADD CONSTRAINT uk_customers_id UNIQUE (customer_id);

-- Index for efficient lookups
CREATE INDEX CONCURRENTLY idx_staging_customers_updated_at ON staging.customers(updated_at);
```

### Network Optimization

- Use connection pooling (pgbouncer)
- Enable compression for large datasets
- Consider read replicas for source database
- Implement connection timeout and retry logic

## 📋 Troubleshooting Guide

### Common Issues

**1. Watermark Not Updating**
```bash
# Check Airflow Variables
airflow variables list | grep replication_watermark

# Verify task completion
airflow tasks state incremental_customer_replication replicate_customers 2024-01-15T10:30:00

# Manual watermark update
airflow variables set replication_watermark_customers_updated_at "2024-01-15T10:30:00+00:00"
```

**2. High Replication Lag**
```sql
-- Check source data growth
SELECT 
    COUNT(*) as total_records,
    MAX(updated_at) as max_watermark,
    MIN(updated_at) as min_watermark
FROM raw.raw_customers;

-- Check target table status
SELECT COUNT(*) FROM staging.customers;
```

**3. Quality Check Failures**
```python
# Disable quality checks temporarily
replicate_task = IncrementalReplicationOperator(
    # ... other params ...
    quality_checks={},  # Disable all checks
    skip_if_no_data=False
)
```

**4. Connection Timeouts**
```python
# Increase timeout in connection
# Edit connection in Airflow UI:
# Extra: {"connect_timeout": 30, "command_timeout": 300}
```

### Debug Mode

```bash
# Enable debug logging
export AIRFLOW__LOGGING__LOGGING_LEVEL=DEBUG

# Run single task
airflow tasks run incremental_customer_replication replicate_customers 2024-01-15T10:30:00

# Check task logs
airflow tasks log incremental_customer_replication replicate_customers 2024-01-15T10:30:00
```

## 🧪 Testing

### Unit Tests

```bash
# Run all tests
python airflow/test_replication.py

# Test specific component
python -c "
from airflow.test_replication import test_watermark_manager
test_watermark_manager()
"
```

### Integration Tests

```bash
# Test with actual database connections
airflow dags test incremental_customer_replication 2024-01-15T10:30:00

# Test single task
airflow tasks test incremental_customer_replication replicate_customers 2024-01-15T10:30:00
```

### Data Validation

```sql
-- Compare source vs target counts
SELECT 
    (SELECT COUNT(*) FROM raw.raw_customers) as source_count,
    (SELECT COUNT(*) FROM staging.customers) as target_count;

-- Check for recent changes
SELECT COUNT(*) FROM raw.raw_customers 
WHERE updated_at > '2024-01-15T10:00:00';
```

## 📈 Production Deployment Checklist

### Pre-Deployment

- [ ] Database connections configured and tested
- [ ] Source table has watermark column with index
- [ ] Target table schema matches source
- [ ] Appropriate database permissions granted
- [ ] Network connectivity verified
- [ ] Airflow plugins directory accessible
- [ ] DAG files copied to dags directory

### Post-Deployment

- [ ] DAGs appear in Airflow UI
- [ ] Test DAG run completed successfully
- [ ] Watermarks stored in Airflow Variables
- [ ] Email notifications working
- [ ] Monitoring DAG enabled
- [ ] Log aggregation configured
- [ ] Alerting rules set up

### Production Monitoring

- [ ] Dashboard for replication metrics
- [ ] Alerts for replication lag > threshold
- [ ] Alerts for consecutive failures
- [ ] Regular watermark backup schedule
- [ ] Capacity monitoring for target database
- [ ] Performance monitoring enabled

---

This comprehensive database replication system provides enterprise-grade reliability, monitoring, and error recovery for incremental data replication workflows in Airflow. The modular design allows for easy customization and extension to support various replication scenarios and data sources.
