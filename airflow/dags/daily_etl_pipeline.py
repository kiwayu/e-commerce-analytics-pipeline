"""
Daily ETL Pipeline DAG for E-commerce Analytics

This DAG orchestrates the complete daily ETL process including:
- Parallel data ingestion (API, files, database replication)
- dbt transformations
- Data quality validation with Great Expectations
- Monitoring and alerting

Schedule: Daily at 2 AM UTC
SLA: 4 hours total pipeline completion
"""

import os
from datetime import datetime, timedelta
from typing import Dict, Any

from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.operators.bash import BashOperator
from airflow.operators.dummy import DummyOperator
from airflow.operators.email import EmailOperator
from airflow.sensors.filesystem import FileSensor
from airflow.providers.postgres.operators.postgres import PostgresOperator

try:
    from airflow.providers.slack.operators.slack_webhook import SlackWebhookOperator
    SLACK_PROVIDER_AVAILABLE = True
except ImportError:
    SLACK_PROVIDER_AVAILABLE = False
from airflow.utils.task_group import TaskGroup
from airflow.utils.trigger_rule import TriggerRule
from airflow.models import Variable

# Import custom operators
try:
    from operators.incremental_replication_operator import IncrementalReplicationOperator
    from operators.incremental_replication_operator import ReplicationValidationOperator
except ImportError:
    # Fallback for development
    import sys
    sys.path.append('/opt/airflow/plugins')
    from operators.incremental_replication_operator import IncrementalReplicationOperator
    from operators.incremental_replication_operator import ReplicationValidationOperator


# DAG Configuration
DAG_ID = 'daily_etl_pipeline'
SCHEDULE_INTERVAL = '0 2 * * *'  # Daily at 2 AM UTC

# Default arguments with comprehensive error handling
default_args = {
    'owner': 'data-engineering',
    'depends_on_past': False,
    'start_date': datetime(2024, 1, 1),
    'email_on_failure': True,
    'email_on_retry': False,
    'email_on_success': False,
    'retries': 3,
    'retry_delay': timedelta(minutes=5),
    'retry_exponential_backoff': True,
    'max_retry_delay': timedelta(minutes=30),
    'email': ['data-team@company.com', 'on-call@company.com'],
    'sla': timedelta(hours=4),  # 4-hour SLA for entire pipeline
    'execution_timeout': timedelta(hours=6),  # 6-hour hard timeout
}

# Pipeline Configuration
PIPELINE_CONFIG = {
    'ingestion': {
        'api_batch_size': 10000,
        'file_batch_size': 5000,
        'replication_batch_size': 5000,
        'max_parallel_tasks': 3,
    },
    'transformation': {
        'dbt_target': 'prod',
        'dbt_profiles_dir': '/opt/airflow/dbt_profiles',
        'full_refresh': False,
    },
    'validation': {
        'ge_context_name': 'airflow_context',
        'validation_timeout': timedelta(hours=1),
        'critical_expectations': ['orders', 'customers', 'revenue'],
    },
    'monitoring': {
        'slack_webhook_conn_id': 'slack_webhook',
        'success_channel': '#data-pipeline-success',
        'failure_channel': '#data-pipeline-alerts',
        # Requires the Slack provider and a 'slack_webhook' Airflow connection
        'enable_slack': os.environ.get('ENABLE_SLACK_ALERTS', 'false').lower() == 'true',
    }
}


def get_pipeline_context(**context) -> Dict[str, Any]:
    """
    Get pipeline execution context and configuration.
    
    Returns:
        Dictionary with pipeline context information
    """
    execution_date = context['execution_date']
    
    return {
        'pipeline_id': f"etl_{execution_date.strftime('%Y%m%d_%H%M%S')}",
        'execution_date': execution_date.isoformat(),
        'data_date': (execution_date - timedelta(days=1)).strftime('%Y-%m-%d'),
        'pipeline_config': PIPELINE_CONFIG,
        'dag_run_id': context['dag_run'].run_id,
    }


def validate_prerequisites(**context) -> Dict[str, Any]:
    """
    Validate pipeline prerequisites before execution.
    
    Returns:
        Dictionary with validation results
    """
    from hooks.postgres_replication_hook import PostgreSQLReplicationHook
    
    pipeline_context = get_pipeline_context(**context)
    
    validation_results = {
        'pipeline_id': pipeline_context['pipeline_id'],
        'prerequisites_passed': True,
        'checks_performed': [],
        'issues': []
    }
    
    try:
        # Check database connectivity
        hook = PostgreSQLReplicationHook(
            source_conn_id='postgres_source',
            target_conn_id='postgres_dwh'
        )
        
        # Validate source connectivity
        try:
            source_test = hook.source_hook.get_first("SELECT 1 as test")
            if source_test:
                validation_results['checks_performed'].append('source_db_connectivity')
            else:
                validation_results['issues'].append('Source database connectivity failed')
                validation_results['prerequisites_passed'] = False
        except Exception as e:
            validation_results['issues'].append(f'Source database error: {str(e)}')
            validation_results['prerequisites_passed'] = False
        
        # Validate target connectivity
        try:
            target_test = hook.target_hook.get_first("SELECT 1 as test")
            if target_test:
                validation_results['checks_performed'].append('target_db_connectivity')
            else:
                validation_results['issues'].append('Target database connectivity failed')
                validation_results['prerequisites_passed'] = False
        except Exception as e:
            validation_results['issues'].append(f'Target database error: {str(e)}')
            validation_results['prerequisites_passed'] = False
        
        # Check disk space (simplified)
        import shutil
        disk_usage = shutil.disk_usage('/opt/airflow/data')
        free_gb = disk_usage.free / (1024**3)
        
        if free_gb < 10:  # Less than 10GB free
            validation_results['issues'].append(f'Low disk space: {free_gb:.1f}GB free')
            validation_results['prerequisites_passed'] = False
        else:
            validation_results['checks_performed'].append('disk_space_check')
        
        # Check required Airflow Variables
        required_variables = [
            'dbt_profiles_dir',
            'ge_config_path', 
            'slack_webhook_url'
        ]
        
        for var_name in required_variables:
            try:
                Variable.get(var_name)
                validation_results['checks_performed'].append(f'variable_{var_name}')
            except Exception:
                validation_results['issues'].append(f'Missing Airflow Variable: {var_name}')
                validation_results['prerequisites_passed'] = False
        
        return validation_results
        
    except Exception as e:
        validation_results['prerequisites_passed'] = False
        validation_results['issues'].append(f'Prerequisites validation error: {str(e)}')
        return validation_results


def run_api_ingestion(**context) -> Dict[str, Any]:
    """
    Execute API ingestion task.
    
    Returns:
        Dictionary with ingestion results
    """
    import sys
    sys.path.append('/opt/spark/jobs')
    
    from ingestion.orders_ingestion import ingest_orders
    
    pipeline_context = get_pipeline_context(**context)
    
    try:
        # Run API ingestion
        ingestion_config = {
            'batch_size': PIPELINE_CONFIG['ingestion']['api_batch_size'],
            'max_records': 100000,
            'timeout_seconds': 3600,
        }
        
        result = ingest_orders(config=ingestion_config)
        
        # Store result in XCom
        context['task_instance'].xcom_push(
            key='api_ingestion_result',
            value=result
        )
        
        return {
            'task': 'api_ingestion',
            'pipeline_id': pipeline_context['pipeline_id'],
            'status': 'success',
            'records_ingested': result.get('records_processed', 0),
            'execution_time': result.get('execution_time_seconds', 0)
        }
        
    except Exception as e:
        error_result = {
            'task': 'api_ingestion',
            'pipeline_id': pipeline_context['pipeline_id'],
            'status': 'failed',
            'error': str(e),
            'records_ingested': 0
        }
        
        context['task_instance'].xcom_push(
            key='api_ingestion_error',
            value=error_result
        )
        
        raise


def run_file_ingestion(**context) -> Dict[str, Any]:
    """
    Execute PySpark file ingestion task.
    
    Returns:
        Dictionary with ingestion results
    """
    import sys
    sys.path.append('/opt/spark/jobs')
    
    from incremental.incremental_loader import IncrementalFileLoader
    from config.spark_config import SparkJobConfig
    
    pipeline_context = get_pipeline_context(**context)
    
    try:
        # Configure Spark job
        spark_config = SparkJobConfig(
            app_name=f"file_ingestion_{pipeline_context['pipeline_id']}",
            batch_size=PIPELINE_CONFIG['ingestion']['file_batch_size'],
            input_dir='/opt/airflow/data/input',
            checkpoint_dir='/opt/airflow/data/checkpoint'
        )
        
        # Run file ingestion
        loader = IncrementalFileLoader(spark_config)
        result = loader.run()
        
        # Store result in XCom
        context['task_instance'].xcom_push(
            key='file_ingestion_result',
            value=result
        )
        
        return {
            'task': 'file_ingestion',
            'pipeline_id': pipeline_context['pipeline_id'],
            'status': 'success',
            'files_processed': result.get('files_processed', 0),
            'records_ingested': result.get('total_records_written', 0),
            'execution_time': result.get('duration_seconds', 0)
        }
        
    except Exception as e:
        error_result = {
            'task': 'file_ingestion',
            'pipeline_id': pipeline_context['pipeline_id'],
            'status': 'failed',
            'error': str(e),
            'files_processed': 0,
            'records_ingested': 0
        }
        
        context['task_instance'].xcom_push(
            key='file_ingestion_error',
            value=error_result
        )
        
        raise


def run_great_expectations_validation(**context) -> Dict[str, Any]:
    """
    Execute Great Expectations data validation.
    
    Returns:
        Dictionary with validation results
    """
    try:
        import great_expectations as ge
        from great_expectations.core.batch import RuntimeBatchRequest
    except ImportError:
        raise ImportError("Great Expectations not installed. Run: pip install great_expectations")
    
    pipeline_context = get_pipeline_context(**context)
    
    try:
        # Initialize Great Expectations context
        ge_config_path = Variable.get('ge_config_path', '/opt/airflow/great_expectations')
        context_ge = ge.get_context(context_root_dir=ge_config_path)
        
        validation_results = {
            'pipeline_id': pipeline_context['pipeline_id'],
            'validations_run': [],
            'validations_passed': 0,
            'validations_failed': 0,
            'critical_failures': [],
            'overall_status': 'passed'
        }
        
        # Define critical data validation checkpoints
        critical_checkpoints = [
            {
                'name': 'orders_data_quality',
                'table': 'marts.fact_orders',
                'expectations': [
                    'expect_table_row_count_to_be_between',
                    'expect_column_values_to_not_be_null',
                    'expect_column_values_to_be_unique'
                ]
            },
            {
                'name': 'customers_data_quality', 
                'table': 'marts.dim_customers',
                'expectations': [
                    'expect_table_row_count_to_be_between',
                    'expect_column_values_to_not_be_null',
                    'expect_column_values_to_match_regex'
                ]
            },
            {
                'name': 'revenue_data_quality',
                'table': 'marts.revenue_daily',
                'expectations': [
                    'expect_table_row_count_to_be_between',
                    'expect_column_values_to_be_between'
                ]
            }
        ]
        
        # Run validation checkpoints
        for checkpoint_config in critical_checkpoints:
            try:
                checkpoint = context_ge.get_checkpoint(checkpoint_config['name'])
                result = checkpoint.run()
                
                validation_info = {
                    'checkpoint': checkpoint_config['name'],
                    'table': checkpoint_config['table'],
                    'success': result.success,
                    'statistics': result.statistics if hasattr(result, 'statistics') else {}
                }
                
                validation_results['validations_run'].append(validation_info)
                
                if result.success:
                    validation_results['validations_passed'] += 1
                else:
                    validation_results['validations_failed'] += 1
                    if checkpoint_config['name'] in PIPELINE_CONFIG['validation']['critical_expectations']:
                        validation_results['critical_failures'].append(checkpoint_config['name'])
                        validation_results['overall_status'] = 'failed'
                
            except Exception as e:
                validation_info = {
                    'checkpoint': checkpoint_config['name'],
                    'table': checkpoint_config['table'],
                    'success': False,
                    'error': str(e)
                }
                
                validation_results['validations_run'].append(validation_info)
                validation_results['validations_failed'] += 1
                validation_results['critical_failures'].append(f"{checkpoint_config['name']}: {str(e)}")
                validation_results['overall_status'] = 'failed'
        
        # Store results in XCom
        context['task_instance'].xcom_push(
            key='validation_results',
            value=validation_results
        )
        
        # Raise exception if critical validations failed
        if validation_results['overall_status'] == 'failed':
            raise Exception(f"Critical data validations failed: {validation_results['critical_failures']}")
        
        return validation_results
        
    except Exception as e:
        error_result = {
            'pipeline_id': pipeline_context['pipeline_id'],
            'overall_status': 'error',
            'error': str(e),
            'validations_run': [],
            'critical_failures': [str(e)]
        }
        
        context['task_instance'].xcom_push(
            key='validation_error',
            value=error_result
        )
        
        raise


def send_success_notification(**context) -> None:
    """
    Send success notification with pipeline summary.
    """
    pipeline_context = get_pipeline_context(**context)
    
    # Collect results from all tasks
    api_result = context['task_instance'].xcom_pull(
        task_ids='ingestion.api_ingestion',
        key='api_ingestion_result'
    ) or {}
    
    file_result = context['task_instance'].xcom_pull(
        task_ids='ingestion.file_ingestion', 
        key='file_ingestion_result'
    ) or {}
    
    db_result = context['task_instance'].xcom_pull(
        task_ids='ingestion.database_replication',
        key='replication_result'
    ) or {}
    
    validation_result = context['task_instance'].xcom_pull(
        task_ids='validation.data_quality_validation',
        key='validation_results'
    ) or {}
    
    # Calculate totals
    total_records = (
        api_result.get('records_ingested', 0) +
        file_result.get('records_ingested', 0) +
        db_result.get('records_loaded', 0)
    )
    
    summary_message = f"""
🎉 **ETL Pipeline Success** 🎉

**Pipeline ID:** {pipeline_context['pipeline_id']}
**Execution Date:** {pipeline_context['execution_date']}
**Data Date:** {pipeline_context['data_date']}

**📊 Ingestion Summary:**
• API Ingestion: {api_result.get('records_ingested', 0):,} records
• File Ingestion: {file_result.get('records_ingested', 0):,} records  
• DB Replication: {db_result.get('records_loaded', 0):,} records
• **Total Records:** {total_records:,}

**✅ Data Quality:**
• Validations Passed: {validation_result.get('validations_passed', 0)}
• Validations Failed: {validation_result.get('validations_failed', 0)}

**⏱️ Performance:**
• Pipeline Duration: {context['dag_run'].duration}
• Status: Completed Successfully

Dashboard: https://company.looker.com/dashboards/etl-pipeline
    """
    
    print(f"SUCCESS NOTIFICATION: {summary_message}")


# Create the DAG
dag = DAG(
    DAG_ID,
    default_args=default_args,
    description='Daily ETL Pipeline for E-commerce Analytics',
    schedule_interval=SCHEDULE_INTERVAL,
    max_active_runs=1,  # Prevent overlapping runs
    catchup=False,  # Don't backfill
    tags=['etl', 'daily', 'production', 'analytics'],
    doc_md=__doc__
)

# =============================================================================
# TASK DEFINITIONS
# =============================================================================

# Start task
start_pipeline = DummyOperator(
    task_id='start_pipeline',
    dag=dag
)

# Prerequisites validation
validate_prerequisites_task = PythonOperator(
    task_id='validate_prerequisites',
    python_callable=validate_prerequisites,
    dag=dag,
    sla=timedelta(minutes=10)
)

# =============================================================================
# INGESTION TASK GROUP
# =============================================================================
with TaskGroup('ingestion', dag=dag) as ingestion_group:
    
    # API Ingestion Task
    api_ingestion = PythonOperator(
        task_id='api_ingestion',
        python_callable=run_api_ingestion,
        sla=timedelta(hours=1),
        pool='ingestion_pool',
        priority_weight=10,
        dag=dag
    )

    # File Ingestion Task
    file_ingestion = PythonOperator(
        task_id='file_ingestion',
        python_callable=run_file_ingestion,
        sla=timedelta(hours=1),
        pool='ingestion_pool',
        priority_weight=10,
        dag=dag
    )
    
    # Database Replication Task
    database_replication = IncrementalReplicationOperator(
        task_id='database_replication',
        source_table='raw.raw_customers',
        target_table='staging.customers',
        source_conn_id='postgres_source',
        target_conn_id='postgres_dwh',
        watermark_column='updated_at',
        primary_key_columns=['customer_id'],
        replication_mode='upsert',
        batch_size=PIPELINE_CONFIG['ingestion']['replication_batch_size'],
        sla=timedelta(hours=1),
        pool='ingestion_pool',
        priority_weight=10,
        dag=dag
    )

# Ingestion completion gate
ingestion_complete = DummyOperator(
    task_id='ingestion_complete',
    trigger_rule=TriggerRule.ALL_SUCCESS,
    dag=dag
)

# =============================================================================
# TRANSFORMATION TASK GROUP  
# =============================================================================
with TaskGroup('transformation', dag=dag) as transformation_group:
    
    # dbt staging layer
    dbt_staging = BashOperator(
        task_id='dbt_run_staging',
        bash_command=f"""
        cd /opt/airflow/dbt && \
        dbt run --select staging --target {PIPELINE_CONFIG['transformation']['dbt_target']} \
            --profiles-dir {PIPELINE_CONFIG['transformation']['dbt_profiles_dir']}
        """,
        sla=timedelta(minutes=30),
        pool='transformation_pool',
        dag=dag
    )

    # dbt intermediate layer
    dbt_intermediate = BashOperator(
        task_id='dbt_run_intermediate',
        bash_command=f"""
        cd /opt/airflow/dbt && \
        dbt run --select intermediate --target {PIPELINE_CONFIG['transformation']['dbt_target']} \
            --profiles-dir {PIPELINE_CONFIG['transformation']['dbt_profiles_dir']}
        """,
        sla=timedelta(minutes=45),
        pool='transformation_pool',
        dag=dag
    )
    
    # dbt marts layer
    dbt_marts = BashOperator(
        task_id='dbt_run_marts',
        bash_command=f"""
        cd /opt/airflow/dbt && \
        dbt run --select marts --target {PIPELINE_CONFIG['transformation']['dbt_target']} \
            --profiles-dir {PIPELINE_CONFIG['transformation']['dbt_profiles_dir']}
        """,
        sla=timedelta(hours=1),
        pool='transformation_pool',
        dag=dag
    )
    
    # dbt tests
    dbt_test = BashOperator(
        task_id='dbt_test',
        bash_command=f"""
        cd /opt/airflow/dbt && \
        dbt test --target {PIPELINE_CONFIG['transformation']['dbt_target']} \
            --profiles-dir {PIPELINE_CONFIG['transformation']['dbt_profiles_dir']}
        """,
        sla=timedelta(minutes=30),
        pool='transformation_pool',
        dag=dag
    )
    
    # Set transformation dependencies
    dbt_staging >> dbt_intermediate >> dbt_marts >> dbt_test

# =============================================================================
# VALIDATION TASK GROUP
# =============================================================================
with TaskGroup('validation', dag=dag) as validation_group:
    
    # Data quality validation
    data_quality_validation = PythonOperator(
        task_id='data_quality_validation',
        python_callable=run_great_expectations_validation,
        sla=timedelta(minutes=30),
        pool='validation_pool',
        dag=dag
    )
    
    # Business metrics validation
    business_metrics_validation = PostgresOperator(
        task_id='business_metrics_validation',
        postgres_conn_id='postgres_dwh',
        sql="""
        -- Validate key business metrics
        WITH validation_checks AS (
            SELECT 
                'daily_orders' as check_name,
                COUNT(*) as actual_value,
                100 as min_expected,
                50000 as max_expected,
                CASE WHEN COUNT(*) BETWEEN 100 AND 50000 THEN TRUE ELSE FALSE END as passed
            FROM marts.fact_orders 
            WHERE DATE(order_date) = CURRENT_DATE - INTERVAL '1 day'
            
            UNION ALL
            
            SELECT 
                'daily_revenue' as check_name,
                SUM(total_amount) as actual_value,
                1000 as min_expected,
                10000000 as max_expected,
                CASE WHEN SUM(total_amount) BETWEEN 1000 AND 10000000 THEN TRUE ELSE FALSE END as passed
            FROM marts.fact_orders 
            WHERE DATE(order_date) = CURRENT_DATE - INTERVAL '1 day'
        )
        SELECT 
            check_name,
            actual_value,
            min_expected,
            max_expected,
            passed,
            CASE WHEN NOT passed THEN 'CRITICAL: ' || check_name || ' validation failed' END as error_message
        FROM validation_checks;
        """,
        sla=timedelta(minutes=15),
        pool='validation_pool',
        dag=dag
    )

# =============================================================================
# MONITORING AND ALERTING
# =============================================================================

# Success notification
success_notification = PythonOperator(
    task_id='success_notification',
    python_callable=send_success_notification,
    trigger_rule=TriggerRule.ALL_SUCCESS,
    dag=dag
)

# Slack alerts are optional: they require the Slack provider and a configured
# webhook connection. Without them, fall back to log-only notification tasks
# so the DAG still parses and runs in a bare local environment.
if PIPELINE_CONFIG['monitoring']['enable_slack'] and SLACK_PROVIDER_AVAILABLE:
    slack_success_alert = SlackWebhookOperator(
        task_id='slack_success_alert',
        slack_webhook_conn_id=PIPELINE_CONFIG['monitoring']['slack_webhook_conn_id'],
        message="""
        ✅ **ETL Pipeline Completed Successfully**

        Pipeline: {{ dag.dag_id }}
        Execution Date: {{ ds }}
        Duration: {{ dag_run.duration }}
        """,
        channel=PIPELINE_CONFIG['monitoring']['success_channel'],
        trigger_rule=TriggerRule.ALL_SUCCESS,
        dag=dag
    )

    failure_notification = SlackWebhookOperator(
        task_id='failure_notification',
        slack_webhook_conn_id=PIPELINE_CONFIG['monitoring']['slack_webhook_conn_id'],
        message="""
        🚨 **ETL Pipeline Failed**

        Pipeline: {{ dag.dag_id }}
        Execution Date: {{ ds }}
        Failed Task: {{ ti.task_id }}

        Please check logs: {{ ti.log_url }}
        """,
        channel=PIPELINE_CONFIG['monitoring']['failure_channel'],
        trigger_rule=TriggerRule.ONE_FAILED,
        dag=dag
    )
else:
    slack_success_alert = PythonOperator(
        task_id='slack_success_alert',
        python_callable=lambda **context: print(
            f"Pipeline {context['dag'].dag_id} completed successfully "
            f"(Slack alerting disabled)"
        ),
        trigger_rule=TriggerRule.ALL_SUCCESS,
        dag=dag
    )

    failure_notification = PythonOperator(
        task_id='failure_notification',
        python_callable=lambda **context: print(
            f"Pipeline {context['dag'].dag_id} failed "
            f"(Slack alerting disabled)"
        ),
        trigger_rule=TriggerRule.ONE_FAILED,
        dag=dag
    )

# =============================================================================
# TASK DEPENDENCIES
# =============================================================================

# Main pipeline flow
start_pipeline >> validate_prerequisites_task >> ingestion_group >> ingestion_complete

# Transformation flow (sequential after ingestion)
ingestion_complete >> transformation_group

# Validation flow (after transformation)
transformation_group >> validation_group

# Success notifications (after all tasks complete successfully)
validation_group >> [success_notification, slack_success_alert]

# Failure notifications (on any task failure)
[
    validate_prerequisites_task,
    ingestion_group,
    transformation_group, 
    validation_group
] >> failure_notification
