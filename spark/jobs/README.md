# PySpark Incremental File Ingestion

This module provides a production-ready PySpark job for incremental file ingestion with comprehensive change detection, checkpointing, and error handling capabilities.

## Overview

The incremental file ingestion job monitors a directory for CSV files, detects new and changed files using modification timestamps and file hashes, and loads only the changed data into the `raw_shipments` PostgreSQL table. It includes robust checkpointing logic to prevent reprocessing and enable recovery from failures.

## Features

### 🔄 **Incremental Processing**
- **File Change Detection**: Uses modification timestamps and MD5 hashes
- **Checkpoint Management**: Persistent state tracking with JSON storage
- **Resume Capability**: Recovers from failures without reprocessing
- **Deduplication**: Prevents duplicate processing of unchanged files

### 📊 **CSV Processing**
- **Flexible Schema Handling**: Primary schema with fallback to inference
- **Data Validation**: Comprehensive validation with error tracking
- **Type Conversion**: Automatic conversion to target schema
- **JSON Field Mapping**: Handles nested address and dimension data

### 🚀 **PySpark Optimization**
- **Adaptive Query Execution**: Automatic optimization for varying data sizes
- **Connection Pooling**: Efficient database connectivity
- **Batch Processing**: Configurable batch sizes for optimal performance
- **Memory Management**: Optimized for large file processing

### 🛡️ **Reliability & Monitoring**
- **Error Recovery**: Graceful handling of processing failures
- **File Archiving**: Automatic archiving of processed files
- **Comprehensive Logging**: Detailed execution logging
- **Statistics Tracking**: Complete job and file-level metrics

## Quick Start

### 1. Environment Setup

```bash
# Set environment variables
export SPARK_MASTER_URL=local[*]
export INPUT_DIR=./spark/data/input
export DWH_POSTGRES_HOST=localhost
export DWH_POSTGRES_USER=ecommerce_user
export DWH_POSTGRES_PASSWORD=ecommerce123
```

### 2. Create Sample Data

```bash
cd spark/jobs/incremental
python incremental_loader.py --create-sample-data
```

### 3. Run Incremental Job

```bash
python incremental_loader.py
```

## Architecture

### Component Structure

```
spark/jobs/
├── config/
│   ├── spark_config.py          # Spark session configuration
│   └── __init__.py
├── utils/
│   ├── checkpoint_manager.py    # Checkpoint persistence and management
│   ├── file_monitor.py          # File monitoring and change detection
│   ├── csv_processor.py         # CSV processing and validation
│   └── __init__.py
├── incremental/
│   ├── incremental_loader.py    # Main incremental loader job
│   └── __init__.py
└── README.md
```

### Data Flow

```
Input Directory → File Monitor → Checkpoint Check → CSV Processor → Validation → PostgreSQL
      ↓              ↓              ↓               ↓            ↓          ↓
  CSV Files    Change Detection  Skip Processed  Schema Mapping  Quality   raw_shipments
                                                                Scoring
```

## Configuration

### SparkJobConfig Parameters

| Parameter | Default | Description |
|-----------|---------|-------------|
| `app_name` | incremental-file-ingestion | Spark application name |
| `master` | local[*] | Spark master URL |
| `driver_memory` | 2g | Driver memory allocation |
| `executor_memory` | 2g | Executor memory allocation |
| `checkpoint_dir` | ./spark/data/checkpoint | Checkpoint storage directory |
| `input_dir` | ./spark/data/input | Input files directory |
| `batch_size` | 10000 | Database batch size |
| `max_files_per_batch` | 100 | Maximum files per processing batch |

### Environment Variables

```bash
# Spark Configuration
SPARK_APP_NAME=ecommerce-incremental-file-ingestion
SPARK_MASTER_URL=local[*]
SPARK_DRIVER_MEMORY=4g
SPARK_EXECUTOR_MEMORY=4g
SPARK_EXECUTOR_CORES=4

# Directory Configuration
INPUT_DIR=./spark/data/input
PROCESSED_DIR=./spark/data/processed
ARCHIVE_DIR=./spark/data/archive
SPARK_CHECKPOINT_DIR=./spark/data/checkpoint

# Database Configuration
POSTGRES_JDBC_URL=jdbc:postgresql://localhost:5432/ecommerce
DWH_POSTGRES_USER=ecommerce_user
DWH_POSTGRES_PASSWORD=ecommerce123

# Processing Configuration
BATCH_SIZE=10000
MAX_FILES_PER_BATCH=50
FILE_RETENTION_DAYS=30
```

## File Processing

### CSV Schema

Expected CSV columns for shipments data:

| Column | Type | Required | Description |
|--------|------|----------|-------------|
| `shipment_id` | String | Yes | Unique shipment identifier |
| `order_id` | String | Yes | Associated order identifier |
| `tracking_number` | String | No | Carrier tracking number |
| `carrier` | String | No | Shipping carrier name |
| `shipment_status` | String | No | Current shipment status |
| `shipped_date` | String | No | Date shipment was sent |
| `destination_*` | String | No | Destination address fields |
| `shipping_cost` | String | No | Cost of shipping |

### Sample CSV Format

```csv
shipment_id,order_id,tracking_number,carrier,shipment_status,shipped_date,destination_city,shipping_cost
SHP-000001,ORD-000123,1Z999AA1234567890,UPS,shipped,2024-01-15 10:30:00,New York,15.99
SHP-000002,ORD-000124,9405511899223456789012,USPS,delivered,2024-01-14 09:15:00,Los Angeles,8.50
```

## Checkpointing

### Checkpoint Storage

Checkpoints are stored as JSON files in the configured checkpoint directory:

```json
{
  "job_name": "incremental_shipments",
  "last_updated": "2024-01-15T10:30:00Z",
  "checkpoints": {
    "/path/to/file.csv": {
      "file_path": "/path/to/file.csv",
      "file_size": 1024,
      "modification_time": 1705312200.0,
      "processing_time": 1705312300.0,
      "file_hash": "abc123def456",
      "record_count": 100,
      "status": "processed",
      "batch_id": "batch-uuid"
    }
  }
}
```

### Checkpoint States

- **`processing`**: File is currently being processed
- **`processed`**: File was successfully processed
- **`failed`**: File processing failed with error

### Recovery Logic

1. **File Discovery**: Scan input directory for CSV files
2. **Change Detection**: Compare file metadata with checkpoints
3. **Status Check**: Skip files already processed successfully
4. **Retry Logic**: Retry failed files automatically
5. **Stale Detection**: Reset stale processing states (>1 hour)

## Error Handling

### File-Level Errors

- **Schema Mismatch**: Fallback to flexible schema inference
- **Validation Failures**: Log errors but continue processing valid records
- **Access Errors**: Skip inaccessible files with warnings
- **Format Errors**: Handle malformed CSV data gracefully

### Job-Level Recovery

- **Database Connection**: Retry logic with exponential backoff
- **Checkpoint Corruption**: Automatic backup and recovery
- **Resource Exhaustion**: Graceful degradation and cleanup
- **Partial Failures**: Continue processing remaining files

### Error Reporting

```python
{
  "processing_errors": [
    {
      "file_path": "/path/to/problematic_file.csv",
      "error": "Validation failed: missing required columns"
    }
  ],
  "validation_errors": [
    {
      "file_path": "/path/to/file.csv",
      "warning": "Used flexible schema due to column mismatch"
    }
  ]
}
```

## Monitoring

### Job Statistics

```python
{
  "batch_id": "uuid-string",
  "duration_seconds": 120.5,
  "files_processed": 5,
  "files_failed": 1,
  "total_records_read": 10000,
  "total_records_written": 9950,
  "file_success_rate": 0.83,
  "record_success_rate": 0.995,
  "checkpoint_stats": {
    "total_files": 20,
    "processed_files": 18,
    "failed_files": 2
  }
}
```

### Performance Metrics

- **Throughput**: Records processed per second
- **Success Rates**: File and record level success percentages
- **Resource Usage**: Memory and CPU utilization
- **Error Rates**: Validation and processing error frequencies

### Logging

```python
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

# Job execution logs
2024-01-15 10:30:00 - incremental_loader - INFO - Starting incremental file loading job
2024-01-15 10:30:01 - file_monitor - INFO - Found 3 files to process
2024-01-15 10:30:02 - csv_processor - INFO - Read 1000 records from shipments_01.csv
2024-01-15 10:30:03 - incremental_loader - INFO - Successfully wrote 995 records to raw_shipments
```

## Integration

### Airflow Integration

```python
from airflow import DAG
from airflow.operators.bash import BashOperator
from datetime import datetime, timedelta

dag = DAG(
    'incremental_shipments_ingestion',
    default_args={
        'owner': 'data-team',
        'retries': 2,
        'retry_delay': timedelta(minutes=5)
    },
    description='Incremental shipments file ingestion',
    schedule_interval=timedelta(hours=1),
    start_date=datetime(2024, 1, 1),
    catchup=False
)

incremental_task = BashOperator(
    task_id='ingest_shipments',
    bash_command='cd /opt/spark/jobs && python incremental/incremental_loader.py',
    dag=dag
)
```

### Docker Integration

```dockerfile
FROM apache/spark:3.4.1-python3

# Install dependencies
COPY requirements.txt .
RUN pip install -r requirements.txt

# Copy job files
COPY spark/jobs/ ./jobs/

# Set working directory
WORKDIR /opt/spark

# Default command
CMD ["python", "jobs/incremental/incremental_loader.py"]
```

## Performance Tuning

### Spark Configuration

```python
# For large files (>100MB each)
config = SparkJobConfig(
    driver_memory="4g",
    executor_memory="6g",
    executor_cores=4,
    batch_size=20000
)

# For many small files (<10MB each)
config = SparkJobConfig(
    driver_memory="2g",
    executor_memory="2g",
    executor_cores=2,
    batch_size=5000,
    max_files_per_batch=200
)
```

### Database Optimization

```python
# JDBC settings for high throughput
db_properties = {
    "batchsize": "20000",
    "rewriteBatchedStatements": "true",
    "isolationLevel": "READ_COMMITTED"
}
```

### File System Optimization

- **File Sizes**: Optimal range 10MB-100MB per CSV file
- **Partitioning**: Organize files by date/source for better performance
- **Compression**: Use gzip compression for archived files
- **Cleanup**: Regular cleanup of processed and archived files

## Troubleshooting

### Common Issues

1. **OutOfMemory Errors**
   ```bash
   # Increase driver and executor memory
   export SPARK_DRIVER_MEMORY=4g
   export SPARK_EXECUTOR_MEMORY=4g
   ```

2. **Checkpoint Corruption**
   ```bash
   # Reset checkpoints (will reprocess all files)
   rm -rf ./spark/data/checkpoint/*
   ```

3. **Database Connection Issues**
   ```bash
   # Test connectivity
   psql -h localhost -U ecommerce_user -d ecommerce -c "SELECT 1"
   ```

4. **File Permission Errors**
   ```bash
   # Fix permissions
   chmod -R 755 ./spark/data/
   ```

### Debug Mode

```bash
# Enable debug logging
export SPARK_LOG_LEVEL=DEBUG
export PYTHONPATH=$PYTHONPATH:$(pwd)

# Run with verbose output
python jobs/incremental/incremental_loader.py --verbose
```

### Performance Diagnostics

```python
# Check Spark UI for job metrics
http://localhost:4040

# Monitor checkpoint file sizes
ls -la ./spark/data/checkpoint/

# Check database table statistics
SELECT COUNT(*) FROM raw.raw_shipments;
SELECT source_file, COUNT(*) FROM raw.raw_shipments GROUP BY source_file;
```

---

This incremental file ingestion solution provides enterprise-grade reliability and performance for processing CSV files at scale with comprehensive change detection and error recovery capabilities.
