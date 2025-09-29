"""
Airflow DAG for incremental database replication with high-water mark strategy.

This DAG performs incremental replication of customer data from source PostgreSQL
to data warehouse using watermark-based change detection.
"""

from datetime import datetime, timedelta
from typing import Dict, Any

from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.operators.email import EmailOperator
from airflow.sensors.sql import SqlSensor
from airflow.utils.trigger_rule import TriggerRule

# Import custom operators (assuming they're in plugins)
try:
    from operators.incremental_replication_operator import (
        IncrementalReplicationOperator,
        ReplicationValidationOperator
    )
except ImportError:
    # Fallback for development/testing
    import sys
    import os
    sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'plugins'))
    from operators.incremental_replication_operator import (
        IncrementalReplicationOperator,
        ReplicationValidationOperator
    )


# DAG Configuration
DAG_ID = 'incremental_customer_replication'

# Default arguments for all tasks
default_args = {
    'owner': 'data-engineering',
    'depends_on_past': False,
    'start_date': datetime(2024, 1, 1),
    'email_on_failure': True,
    'email_on_retry': False,
    'retries': 2,
    'retry_delay': timedelta(minutes=5),
    'email': ['data-team@company.com'],
    'sla': timedelta(hours=2),  # SLA of 2 hours
}

# Replication configuration
REPLICATION_CONFIG = {
    'source_table': 'raw.raw_customers',
    'target_table': 'staging.customers',
    'source_conn_id': 'postgres_source',
    'target_conn_id': 'postgres_dwh',
    'watermark_column': 'updated_at',
    'primary_key_columns': ['customer_id'],
    'replication_mode': 'upsert',  # Use upsert for customers (handles updates)
    'batch_size': 5000,
    'max_records_per_run': 50000,
    'watermark_lag_tolerance': timedelta(hours=6),  # Allow up to 6 hours lag
}

# Quality checks configuration
QUALITY_CHECKS = {
    'null_check': {
        'columns': ['customer_id', 'email'],
        'max_null_percentage': 0,  # No nulls allowed in key fields
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
        }
    },
    'record_count_check': {
        'min_records': 0,
        'max_records': 100000,  # Sanity check
        'fail_on_error': False
    }
}


def check_replication_prerequisites(**context) -> Dict[str, Any]:
    """
    Check prerequisites before starting replication.
    
    Returns:
        Dictionary with prerequisite check results
    """
    from hooks.postgres_replication_hook import PostgreSQLReplicationHook
    
    hook = PostgreSQLReplicationHook(
        source_conn_id=REPLICATION_CONFIG['source_conn_id'],
        target_conn_id=REPLICATION_CONFIG['target_conn_id']
    )
    
    # Validate setup
    validation_result = hook.validate_replication_setup(
        source_table=REPLICATION_CONFIG['source_table'],
        target_table=REPLICATION_CONFIG['target_table'],
        watermark_column=REPLICATION_CONFIG['watermark_column']
    )
    
    if not validation_result['is_valid']:
        raise Exception(f"Prerequisites check failed: {validation_result['errors']}")
    
    # Get current statistics
    stats = hook.get_replication_stats(
        source_table=REPLICATION_CONFIG['source_table'],
        target_table=REPLICATION_CONFIG['target_table'],
        watermark_column=REPLICATION_CONFIG['watermark_column']
    )
    
    result = {
        'validation_result': validation_result,
        'replication_stats': stats,
        'check_timestamp': datetime.now().isoformat()
    }
    
    print(f"Prerequisites check completed: {result}")
    return result


def post_replication_validation(**context) -> Dict[str, Any]:
    """
    Perform post-replication validation and data quality checks.
    
    Returns:
        Dictionary with validation results
    """
    from hooks.postgres_replication_hook import PostgreSQLReplicationHook
    
    # Get replication result from upstream task
    replication_result = context['task_instance'].xcom_pull(
        task_ids='replicate_customers',
        key='replication_result'
    )
    
    if not replication_result:
        raise Exception("No replication result found in XCom")
    
    hook = PostgreSQLReplicationHook(
        source_conn_id=REPLICATION_CONFIG['source_conn_id'],
        target_conn_id=REPLICATION_CONFIG['target_conn_id']
    )
    
    # Get updated statistics
    post_stats = hook.get_replication_stats(
        source_table=REPLICATION_CONFIG['source_table'],
        target_table=REPLICATION_CONFIG['target_table'],
        watermark_column=REPLICATION_CONFIG['watermark_column']
    )
    
    # Validate record counts
    expected_records = replication_result.get('records_loaded', 0)
    
    if expected_records > 0:
        # Simple validation: check if target table has data
        if post_stats['target']['total_rows'] == 0:
            raise Exception("Target table is empty after replication")
    
    validation_result = {
        'replication_result': replication_result,
        'post_replication_stats': post_stats,
        'validation_passed': True,
        'validation_timestamp': datetime.now().isoformat()
    }
    
    print(f"Post-replication validation completed: {validation_result}")
    return validation_result


def send_failure_notification(**context) -> None:
    """
    Send detailed failure notification.
    """
    task_instance = context['task_instance']
    dag_run = context['dag_run']
    
    # Get error details from XCom if available
    error_info = task_instance.xcom_pull(
        task_ids='replicate_customers',
        key='replication_error'
    ) or {}
    
    failure_info = {
        'dag_id': dag_run.dag_id,
        'run_id': dag_run.run_id,
        'task_id': task_instance.task_id,
        'execution_date': context['execution_date'].isoformat(),
        'error_info': error_info,
        'log_url': task_instance.log_url
    }
    
    print(f"Replication failure notification: {failure_info}")
    
    # In production, this would send notifications to monitoring systems
    # For now, just log the failure details


# Create DAG
dag = DAG(
    DAG_ID,
    default_args=default_args,
    description='Incremental replication of customer data using high-water mark',
    schedule_interval=timedelta(minutes=30),  # Run every 30 minutes
    max_active_runs=1,  # Prevent overlapping runs
    catchup=False,  # Don't backfill
    tags=['replication', 'incremental', 'customers', 'postgres'],
    doc_md=__doc__
)

# Task 1: Source data availability sensor
source_data_sensor = SqlSensor(
    task_id='check_source_data_availability',
    conn_id=REPLICATION_CONFIG['source_conn_id'],
    sql=f"""
        SELECT COUNT(*) as record_count
        FROM {REPLICATION_CONFIG['source_table']}
        WHERE {REPLICATION_CONFIG['watermark_column']} > 
              COALESCE((
                  SELECT MAX({REPLICATION_CONFIG['watermark_column']})
                  FROM {REPLICATION_CONFIG['target_table']}
              ), '1900-01-01'::timestamp)
    """,
    poke_interval=60,  # Check every minute
    timeout=300,  # Timeout after 5 minutes
    mode='poke',
    dag=dag
)

# Task 2: Prerequisites check
prerequisites_check = PythonOperator(
    task_id='check_prerequisites',
    python_callable=check_replication_prerequisites,
    dag=dag
)

# Task 3: Pre-replication validation
pre_validation = ReplicationValidationOperator(
    task_id='pre_replication_validation',
    source_table=REPLICATION_CONFIG['source_table'],
    target_table=REPLICATION_CONFIG['target_table'],
    source_conn_id=REPLICATION_CONFIG['source_conn_id'],
    target_conn_id=REPLICATION_CONFIG['target_conn_id'],
    watermark_column=REPLICATION_CONFIG['watermark_column'],
    max_lag_hours=24,  # Alert if more than 24 hours behind
    dag=dag
)

# Task 4: Main replication task
replicate_customers = IncrementalReplicationOperator(
    task_id='replicate_customers',
    source_table=REPLICATION_CONFIG['source_table'],
    target_table=REPLICATION_CONFIG['target_table'],
    source_conn_id=REPLICATION_CONFIG['source_conn_id'],
    target_conn_id=REPLICATION_CONFIG['target_conn_id'],
    watermark_column=REPLICATION_CONFIG['watermark_column'],
    primary_key_columns=REPLICATION_CONFIG['primary_key_columns'],
    replication_mode=REPLICATION_CONFIG['replication_mode'],
    batch_size=REPLICATION_CONFIG['batch_size'],
    max_records_per_run=REPLICATION_CONFIG['max_records_per_run'],
    watermark_lag_tolerance=REPLICATION_CONFIG['watermark_lag_tolerance'],
    quality_checks=QUALITY_CHECKS,
    skip_if_no_data=True,
    dag=dag
)

# Task 5: Post-replication validation
post_validation = PythonOperator(
    task_id='post_replication_validation',
    python_callable=post_replication_validation,
    dag=dag
)

# Task 6: Final validation check
final_validation = ReplicationValidationOperator(
    task_id='final_validation',
    source_table=REPLICATION_CONFIG['source_table'],
    target_table=REPLICATION_CONFIG['target_table'],
    source_conn_id=REPLICATION_CONFIG['source_conn_id'],
    target_conn_id=REPLICATION_CONFIG['target_conn_id'],
    watermark_column=REPLICATION_CONFIG['watermark_column'],
    dag=dag
)

# Task 7: Failure notification (runs only on failure)
failure_notification = PythonOperator(
    task_id='send_failure_notification',
    python_callable=send_failure_notification,
    trigger_rule=TriggerRule.ONE_FAILED,
    dag=dag
)

# Task 8: Success email notification
success_notification = EmailOperator(
    task_id='send_success_notification',
    to=['data-team@company.com'],
    subject='✅ Customer Replication Completed Successfully',
    html_content="""
    <h3>Customer Data Replication Completed</h3>
    <p><strong>DAG:</strong> {{ dag.dag_id }}</p>
    <p><strong>Execution Date:</strong> {{ execution_date }}</p>
    <p><strong>Duration:</strong> {{ dag_run.duration }}</p>
    
    <h4>Replication Details:</h4>
    <p>Check the logs for detailed statistics about records processed.</p>
    
    <p><a href="{{ ti.log_url }}">View Logs</a></p>
    """,
    trigger_rule=TriggerRule.ALL_SUCCESS,
    dag=dag
)

# Define task dependencies
source_data_sensor >> prerequisites_check >> pre_validation >> replicate_customers

# Post-replication flow
replicate_customers >> post_validation >> final_validation >> success_notification

# Failure handling
[prerequisites_check, pre_validation, replicate_customers, post_validation, final_validation] >> failure_notification


# Additional DAG for monitoring replication health
monitoring_dag = DAG(
    'replication_health_monitoring',
    default_args={
        **default_args,
        'start_date': datetime(2024, 1, 1),
        'email_on_failure': True,
        'retries': 1,
    },
    description='Monitor replication health and lag',
    schedule_interval=timedelta(hours=1),  # Run every hour
    max_active_runs=1,
    catchup=False,
    tags=['monitoring', 'replication', 'health'],
    doc_md="""
    # Replication Health Monitoring DAG
    
    This DAG monitors the health of incremental replication processes:
    - Checks replication lag
    - Validates data consistency
    - Alerts on issues
    """
)

# Monitoring task
replication_health_check = ReplicationValidationOperator(
    task_id='check_replication_health',
    source_table=REPLICATION_CONFIG['source_table'],
    target_table=REPLICATION_CONFIG['target_table'],
    source_conn_id=REPLICATION_CONFIG['source_conn_id'],
    target_conn_id=REPLICATION_CONFIG['target_conn_id'],
    watermark_column=REPLICATION_CONFIG['watermark_column'],
    max_lag_hours=2,  # Alert if more than 2 hours behind
    dag=monitoring_dag
)

# Health check alert
health_alert = EmailOperator(
    task_id='send_health_alert',
    to=['data-team@company.com', 'on-call@company.com'],
    subject='🚨 Replication Health Alert',
    html_content="""
    <h3>Replication Health Issue Detected</h3>
    <p><strong>Table:</strong> {{ params.source_table }} → {{ params.target_table }}</p>
    <p><strong>Issue:</strong> Replication lag exceeds threshold</p>
    <p><strong>Time:</strong> {{ execution_date }}</p>
    
    <p>Please investigate the replication process immediately.</p>
    
    <p><a href="{{ ti.log_url }}">View Logs</a></p>
    """,
    params={
        'source_table': REPLICATION_CONFIG['source_table'],
        'target_table': REPLICATION_CONFIG['target_table']
    },
    trigger_rule=TriggerRule.ONE_FAILED,
    dag=monitoring_dag
)

replication_health_check >> health_alert
