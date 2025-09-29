# 🚀 ETL Pipeline Orchestration with Airflow

A production-ready Airflow DAG orchestrating the complete daily ETL pipeline for e-commerce analytics. This comprehensive solution includes parallel data ingestion, dbt transformations, data quality validation, and intelligent monitoring with alerting.

## 🎯 Pipeline Overview

### Architecture

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐    ┌──────────────────┐
│  Prerequisites │───▶│  Parallel        │───▶│  Sequential     │───▶│  Validation &    │
│  Validation     │    │  Ingestion       │    │  Transformation │    │  Monitoring      │
└─────────────────┘    └──────────────────┘    └─────────────────┘    └──────────────────┘
                            │        │                   │                        │
                        ┌───▼───┐ ┌──▼──┐           ┌────▼────┐            ┌─────▼─────┐
                        │ API   │ │File │           │   dbt   │            │Great      │
                        │Ingest │ │Ingest│           │ Models  │            │Expect.    │
                        └───────┘ └─────┘           └─────────┘            └───────────┘
                        ┌──────────────┐
                        │ DB           │
                        │ Replication  │
                        └──────────────┘
```

### Schedule & Configuration

- **Schedule**: Daily at 2:00 AM UTC (`0 2 * * *`)
- **SLA**: 4-hour total pipeline completion
- **Retries**: 3 attempts with exponential backoff
- **Timeout**: 6-hour hard timeout per task
- **Concurrency**: Controlled via Airflow pools

## 📋 DAG Structure

### Task Groups

**1. Ingestion Group** (Parallel Execution)
```python
ingestion/
├── api_ingestion          # API data ingestion
├── file_ingestion         # PySpark file processing  
└── database_replication   # Incremental DB replication
```

**2. Transformation Group** (Sequential Execution)
```python
transformation/
├── dbt_run_staging       # Clean and standardize
├── dbt_run_intermediate  # Business logic
├── dbt_run_marts        # Analytics models
└── dbt_test             # Data quality tests
```

**3. Validation Group** (Parallel Execution)
```python
validation/
├── data_quality_validation    # Great Expectations
└── business_metrics_validation # SQL-based checks
```

### Monitoring & Alerting
```python
monitoring/
├── success_notification     # Pipeline success summary
├── slack_success_alert      # Slack success notification
└── failure_notification    # Slack failure alerts
```

## 🔧 Configuration

### Default Arguments

```python
default_args = {
    'owner': 'data-engineering',
    'retries': 3,
    'retry_delay': timedelta(minutes=5),
    'retry_exponential_backoff': True,
    'max_retry_delay': timedelta(minutes=30),
    'sla': timedelta(hours=4),
    'execution_timeout': timedelta(hours=6),
    'email_on_failure': True,
    'email': ['data-team@company.com']
}
```

### Pipeline Configuration

```python
PIPELINE_CONFIG = {
    'ingestion': {
        'api_batch_size': 10000,
        'file_batch_size': 5000,
        'replication_batch_size': 5000,
        'max_parallel_tasks': 3
    },
    'transformation': {
        'dbt_target': 'prod',
        'dbt_profiles_dir': '/opt/airflow/dbt_profiles',
        'full_refresh': False
    },
    'validation': {
        'ge_context_name': 'airflow_context',
        'validation_timeout': timedelta(hours=1),
        'critical_expectations': ['orders', 'customers', 'revenue']
    },
    'monitoring': {
        'slack_webhook_conn_id': 'slack_webhook',
        'success_channel': '#data-pipeline-success',
        'failure_channel': '#data-pipeline-alerts'
    }
}
```

## ⚡ Task Details

### Ingestion Tasks (Parallel)

**API Ingestion**
- **Function**: `run_api_ingestion()`
- **Pool**: `ingestion_pool`
- **SLA**: 1 hour
- **Purpose**: Fetch orders from external APIs
- **Output**: Records ingested count and execution metrics

**File Ingestion**
- **Function**: `run_file_ingestion()`
- **Pool**: `ingestion_pool` 
- **SLA**: 1 hour
- **Purpose**: Process CSV files with PySpark
- **Output**: Files processed and records loaded

**Database Replication**
- **Operator**: `IncrementalReplicationOperator`
- **Pool**: `ingestion_pool`
- **SLA**: 1 hour
- **Purpose**: Incremental replication with watermarks
- **Output**: Replication statistics and watermark updates

### Transformation Tasks (Sequential)

**dbt Staging**
```bash
dbt run --select staging --target prod
```
- **SLA**: 30 minutes
- **Purpose**: Clean and standardize raw data

**dbt Intermediate**
```bash
dbt run --select intermediate --target prod
```
- **SLA**: 45 minutes
- **Purpose**: Apply business logic transformations

**dbt Marts**
```bash
dbt run --select marts --target prod
```
- **SLA**: 1 hour
- **Purpose**: Create analytics-ready dimensional models

**dbt Tests**
```bash
dbt test --target prod
```
- **SLA**: 30 minutes
- **Purpose**: Validate data quality and business rules

### Validation Tasks

**Great Expectations Validation**
- **Function**: `run_great_expectations_validation()`
- **Pool**: `validation_pool`
- **SLA**: 30 minutes
- **Checkpoints**: orders_data_quality, customers_data_quality, revenue_data_quality

**Business Metrics Validation**
- **Operator**: `PostgresOperator`
- **Pool**: `validation_pool`
- **SLA**: 15 minutes
- **Purpose**: Validate key business metrics with SQL

## 🎛️ Resource Management

### Airflow Pools

```python
pools = {
    'ingestion_pool': {
        'slots': 3,
        'description': 'Parallel data ingestion tasks'
    },
    'transformation_pool': {
        'slots': 2, 
        'description': 'dbt transformation tasks'
    },
    'validation_pool': {
        'slots': 2,
        'description': 'Data quality validation tasks'
    }
}
```

### Pool Configuration Script

```bash
# Setup pools
python /opt/airflow/dags/etl/pool_configuration.py

# Monitor utilization
airflow pools list
```

## 📊 Monitoring & Alerting

### Success Notifications

**Slack Success Message**
```
✅ ETL Pipeline Completed Successfully

Pipeline: daily_etl_pipeline
Execution Date: 2024-01-15
Duration: 2h 15m

📊 Ingestion Summary:
• API Ingestion: 15,000 records
• File Ingestion: 8,500 records
• DB Replication: 2,300 records
• Total Records: 25,800

✅ Data Quality:
• Validations Passed: 12
• Validations Failed: 0

Dashboard: https://company.looker.com/dashboards/etl-pipeline
```

### Failure Alerts

**Critical Failure Notification**
```
🚨 CRITICAL PIPELINE ALERT 🚨

DAG: daily_etl_pipeline
Execution Date: 2024-01-15
Status: failed

Issues:
• Pipeline execution failed
• 2 tasks failed
• SLA compliance below threshold: 75%

Summary:
• Total Tasks: 15
• Success Rate: 86.67%
• Duration: 3h 45m
• Performance Score: 72.5/100
```

### Monitoring Features

- **Real-time pipeline metrics tracking**
- **SLA compliance monitoring**
- **Performance score calculation**
- **Error pattern analysis**
- **Resource utilization tracking**

## 🔍 Data Quality Validation

### Great Expectations Checkpoints

**Orders Data Quality**
```python
expectations = [
    'expect_table_row_count_to_be_between',
    'expect_column_values_to_not_be_null',
    'expect_column_values_to_be_unique',
    'expect_column_values_to_be_in_set',
    'expect_column_values_to_be_between'
]
```

**Customers Data Quality**
```python
expectations = [
    'expect_column_values_to_be_unique',
    'expect_column_values_to_match_regex',
    'expect_column_values_to_be_between'
]
```

**Revenue Data Quality**
```python
expectations = [
    'expect_table_row_count_to_equal',
    'expect_column_values_to_be_between'
]
```

### Business Metrics Validation

```sql
-- Daily orders validation
SELECT 
    'daily_orders' as check_name,
    COUNT(*) as actual_value,
    100 as min_expected,
    50000 as max_expected,
    CASE WHEN COUNT(*) BETWEEN 100 AND 50000 THEN TRUE ELSE FALSE END as passed
FROM marts.fact_orders 
WHERE DATE(order_date) = CURRENT_DATE - INTERVAL '1 day'
```

## 🛠️ Setup & Deployment

### Prerequisites

1. **Airflow Installation**
```bash
pip install apache-airflow[postgres,redis,slack]==2.7.3
```

2. **Database Setup**
```bash
# Initialize Airflow database
airflow db init

# Create admin user
airflow users create \
    --username admin \
    --firstname Admin \
    --lastname User \
    --role Admin \
    --email admin@company.com
```

3. **Connections Setup**
```bash
# PostgreSQL connections
airflow connections add postgres_source \
    --conn-type postgres \
    --conn-host source-db.company.com \
    --conn-login readonly_user \
    --conn-password secret123

airflow connections add postgres_dwh \
    --conn-type postgres \
    --conn-host dwh.company.com \
    --conn-login dwh_user \
    --conn-password secret456

# Slack webhook
airflow connections add slack_webhook \
    --conn-type http \
    --conn-host hooks.slack.com \
    --conn-password webhook_url_here
```

### Deployment Steps

1. **Copy DAG Files**
```bash
cp airflow/dags/daily_etl_pipeline.py $AIRFLOW_HOME/dags/
cp -r airflow/plugins/* $AIRFLOW_HOME/plugins/
cp -r airflow/dags/validation $AIRFLOW_HOME/dags/
cp -r airflow/dags/etl $AIRFLOW_HOME/dags/
```

2. **Setup Pools**
```bash
python $AIRFLOW_HOME/dags/etl/pool_configuration.py
```

3. **Configure Variables**
```bash
airflow variables set dbt_profiles_dir /opt/airflow/dbt_profiles
airflow variables set ge_config_path /opt/airflow/great_expectations
airflow variables set slack_webhook_url https://hooks.slack.com/services/...
```

4. **Start Services**
```bash
# Start webserver
airflow webserver --port 8080 --daemon

# Start scheduler  
airflow scheduler --daemon

# Start worker (if using CeleryExecutor)
airflow celery worker --daemon
```

### Environment Variables

```bash
# Core Airflow settings
export AIRFLOW_HOME=/opt/airflow
export AIRFLOW__CORE__DAGS_FOLDER=/opt/airflow/dags
export AIRFLOW__CORE__EXECUTOR=LocalExecutor

# Database connection
export AIRFLOW__DATABASE__SQL_ALCHEMY_CONN=postgresql+psycopg2://airflow:password@localhost:5432/airflow_db

# Email settings
export AIRFLOW__SMTP__SMTP_HOST=smtp.company.com
export AIRFLOW__SMTP__SMTP_USER=airflow@company.com
export AIRFLOW__SMTP__SMTP_PASSWORD=email_password

# dbt settings
export DBT_PROFILES_DIR=/opt/airflow/dbt_profiles
export DBT_PROJECT_DIR=/opt/airflow/dbt
```

## 🔧 Customization

### Adding New Ingestion Sources

```python
# Add to ingestion TaskGroup
with TaskGroup('ingestion', dag=dag) as ingestion_group:
    
    new_source_ingestion = PythonOperator(
        task_id='new_source_ingestion',
        python_callable=run_new_source_ingestion,
        pool='ingestion_pool',
        sla=timedelta(hours=1)
    )
```

### Custom Validation Rules

```python
# Add to validation TaskGroup
custom_validation = PostgresOperator(
    task_id='custom_business_validation',
    postgres_conn_id='postgres_dwh',
    sql="""
    -- Your custom validation SQL
    SELECT validation_rule, passed, error_message
    FROM custom_validation_function()
    """,
    pool='validation_pool'
)
```

### Alert Customization

```python
# Custom alert conditions
def custom_alert_logic(**context):
    metrics = get_pipeline_metrics(context['execution_date'])
    
    # Your custom alerting logic
    if custom_condition_met(metrics):
        send_custom_alert(metrics)
```

## 📈 Performance Optimization

### Best Practices

1. **Pool Sizing**
   - Ingestion: 3 slots (API + File + DB parallel)
   - Transformation: 2 slots (sequential dbt stages)
   - Validation: 2 slots (GE + SQL parallel)

2. **SLA Management**
   - Total pipeline: 4 hours
   - Individual tasks: 15 minutes to 1 hour
   - Critical path optimization

3. **Resource Allocation**
   - Memory: 4GB per transformation task
   - CPU: 2 cores per ingestion task
   - Disk: 50GB temp space for file processing

4. **Monitoring Optimization**
   - Real-time metrics collection
   - Proactive alerting thresholds
   - Performance trend analysis

### Scaling Considerations

**Horizontal Scaling**
- Use CeleryExecutor with Redis/RabbitMQ
- Add worker nodes for increased throughput
- Implement task partitioning for large datasets

**Vertical Scaling**
- Increase pool slots for parallel execution
- Optimize dbt model materialization
- Tune database connection pooling

## 🚨 Troubleshooting

### Common Issues

**1. Task Timeouts**
```bash
# Increase task timeout
execution_timeout=timedelta(hours=8)

# Check resource utilization
airflow tasks state dag_id task_id execution_date
```

**2. Pool Exhaustion**
```bash
# Monitor pool utilization
python /opt/airflow/dags/etl/pool_configuration.py

# Increase pool slots
airflow pools set pool_name 5 "Increased capacity"
```

**3. dbt Failures**
```bash
# Debug dbt issues
cd /opt/airflow/dbt
dbt debug --profiles-dir /opt/airflow/dbt_profiles

# Check specific model
dbt run --select failing_model --target prod
```

**4. Connection Issues**
```bash
# Test connections
airflow connections test postgres_dwh
airflow connections test slack_webhook

# Update connection
airflow connections delete postgres_dwh
airflow connections add postgres_dwh --conn-type postgres ...
```

### Debug Commands

```bash
# Check DAG structure
airflow dags show daily_etl_pipeline

# Test specific task
airflow tasks test daily_etl_pipeline task_id 2024-01-15

# View task logs
airflow tasks log daily_etl_pipeline task_id 2024-01-15 1

# Clear task state
airflow tasks clear daily_etl_pipeline --start-date 2024-01-15 --end-date 2024-01-15
```

---

This Airflow ETL pipeline provides enterprise-grade orchestration with comprehensive monitoring, intelligent alerting, and robust error handling. The modular design allows for easy customization and scaling to meet evolving data processing requirements.
