#!/usr/bin/env python3
"""
Test script to validate the daily ETL pipeline DAG structure and configuration.
"""

import sys
import os
from datetime import datetime, timedelta
from unittest.mock import patch, MagicMock

# Add airflow directory to path
airflow_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(airflow_dir, 'dags'))
sys.path.insert(0, os.path.join(airflow_dir, 'plugins'))


def test_dag_import():
    """Test that the DAG can be imported without errors."""
    print("=== Testing DAG Import ===")
    
    try:
        # Mock Airflow components to avoid import errors
        with patch('airflow.models.Variable'), \
             patch('airflow.operators.python.PythonOperator'), \
             patch('airflow.operators.bash.BashOperator'), \
             patch('airflow.operators.dummy.DummyOperator'), \
             patch('airflow.providers.slack.operators.slack_webhook.SlackWebhookOperator'), \
             patch('airflow.providers.postgres.operators.postgres.PostgresOperator'), \
             patch('operators.incremental_replication_operator.IncrementalReplicationOperator'), \
             patch('operators.incremental_replication_operator.ReplicationValidationOperator'):
            
            # Import the DAG
            import daily_etl_pipeline
            
            dag = daily_etl_pipeline.dag
            
            print(f"✓ DAG imported successfully: {dag.dag_id}")
            print(f"✓ Schedule interval: {dag.schedule_interval}")
            print(f"✓ Max active runs: {dag.max_active_runs}")
            print(f"✓ Catchup: {dag.catchup}")
            
            return True
            
    except Exception as e:
        print(f"✗ DAG import failed: {e}")
        return False


def test_dag_structure():
    """Test DAG structure and task organization."""
    print("\n=== Testing DAG Structure ===")
    
    try:
        with patch('airflow.models.Variable'), \
             patch('airflow.operators.python.PythonOperator'), \
             patch('airflow.operators.bash.BashOperator'), \
             patch('airflow.operators.dummy.DummyOperator'), \
             patch('airflow.providers.slack.operators.slack_webhook.SlackWebhookOperator'), \
             patch('airflow.providers.postgres.operators.postgres.PostgresOperator'), \
             patch('operators.incremental_replication_operator.IncrementalReplicationOperator'), \
             patch('operators.incremental_replication_operator.ReplicationValidationOperator'):
            
            import daily_etl_pipeline
            dag = daily_etl_pipeline.dag
            
            # Get all task IDs
            task_ids = [task.task_id for task in dag.tasks]
            print(f"✓ Total tasks: {len(task_ids)}")
            
            # Check for expected tasks
            expected_tasks = [
                'start_pipeline',
                'validate_prerequisites',
                'ingestion_complete',
                'success_notification',
                'slack_success_alert',
                'failure_notification'
            ]
            
            for expected_task in expected_tasks:
                if expected_task in task_ids:
                    print(f"✓ Found expected task: {expected_task}")
                else:
                    print(f"✗ Missing expected task: {expected_task}")
                    return False
            
            # Check for TaskGroups
            task_group_tasks = [tid for tid in task_ids if '.' in tid]
            print(f"✓ TaskGroup tasks found: {len(task_group_tasks)}")
            
            # Expected TaskGroup patterns
            expected_patterns = [
                'ingestion.',
                'transformation.',
                'validation.'
            ]
            
            for pattern in expected_patterns:
                matching_tasks = [tid for tid in task_ids if tid.startswith(pattern)]
                if matching_tasks:
                    print(f"✓ Found TaskGroup '{pattern[:-1]}' with {len(matching_tasks)} tasks")
                else:
                    print(f"✗ Missing TaskGroup: {pattern[:-1]}")
                    return False
            
            return True
            
    except Exception as e:
        print(f"✗ DAG structure test failed: {e}")
        return False


def test_dag_configuration():
    """Test DAG configuration and default arguments."""
    print("\n=== Testing DAG Configuration ===")
    
    try:
        with patch('airflow.models.Variable'), \
             patch('airflow.operators.python.PythonOperator'), \
             patch('airflow.operators.bash.BashOperator'), \
             patch('airflow.operators.dummy.DummyOperator'), \
             patch('airflow.providers.slack.operators.slack_webhook.SlackWebhookOperator'), \
             patch('airflow.providers.postgres.operators.postgres.PostgresOperator'), \
             patch('operators.incremental_replication_operator.IncrementalReplicationOperator'), \
             patch('operators.incremental_replication_operator.ReplicationValidationOperator'):
            
            import daily_etl_pipeline
            dag = daily_etl_pipeline.dag
            
            # Check default arguments
            default_args = dag.default_args
            
            required_defaults = [
                'owner',
                'retries',
                'retry_delay',
                'email_on_failure',
                'sla'
            ]
            
            for required_arg in required_defaults:
                if required_arg in default_args:
                    print(f"✓ Default arg present: {required_arg} = {default_args[required_arg]}")
                else:
                    print(f"✗ Missing default arg: {required_arg}")
                    return False
            
            # Check schedule
            if dag.schedule_interval == '0 2 * * *':
                print("✓ Schedule interval correct: Daily at 2 AM UTC")
            else:
                print(f"✗ Incorrect schedule interval: {dag.schedule_interval}")
                return False
            
            # Check SLA
            expected_sla = timedelta(hours=4)
            if default_args.get('sla') == expected_sla:
                print("✓ SLA configured correctly: 4 hours")
            else:
                print(f"✗ Incorrect SLA: {default_args.get('sla')}")
                return False
            
            # Check retries
            if default_args.get('retries') == 3:
                print("✓ Retries configured correctly: 3")
            else:
                print(f"✗ Incorrect retry count: {default_args.get('retries')}")
                return False
            
            return True
            
    except Exception as e:
        print(f"✗ DAG configuration test failed: {e}")
        return False


def test_pipeline_config():
    """Test pipeline configuration constants."""
    print("\n=== Testing Pipeline Configuration ===")
    
    try:
        with patch('airflow.models.Variable'), \
             patch('airflow.operators.python.PythonOperator'), \
             patch('airflow.operators.bash.BashOperator'), \
             patch('airflow.operators.dummy.DummyOperator'), \
             patch('airflow.providers.slack.operators.slack_webhook.SlackWebhookOperator'), \
             patch('airflow.providers.postgres.operators.postgres.PostgresOperator'), \
             patch('operators.incremental_replication_operator.IncrementalReplicationOperator'), \
             patch('operators.incremental_replication_operator.ReplicationValidationOperator'):
            
            import daily_etl_pipeline
            
            config = daily_etl_pipeline.PIPELINE_CONFIG
            
            # Check configuration sections
            required_sections = ['ingestion', 'transformation', 'validation', 'monitoring']
            
            for section in required_sections:
                if section in config:
                    print(f"✓ Configuration section present: {section}")
                else:
                    print(f"✗ Missing configuration section: {section}")
                    return False
            
            # Check ingestion config
            ingestion_config = config['ingestion']
            if 'api_batch_size' in ingestion_config and 'file_batch_size' in ingestion_config:
                print("✓ Ingestion configuration complete")
            else:
                print("✗ Incomplete ingestion configuration")
                return False
            
            # Check transformation config
            transformation_config = config['transformation']
            if 'dbt_target' in transformation_config and 'dbt_profiles_dir' in transformation_config:
                print("✓ Transformation configuration complete")
            else:
                print("✗ Incomplete transformation configuration")
                return False
            
            # Check monitoring config
            monitoring_config = config['monitoring']
            if 'slack_webhook_conn_id' in monitoring_config:
                print("✓ Monitoring configuration complete")
            else:
                print("✗ Incomplete monitoring configuration")
                return False
            
            return True
            
    except Exception as e:
        print(f"✗ Pipeline configuration test failed: {e}")
        return False


def test_task_dependencies():
    """Test task dependencies and flow."""
    print("\n=== Testing Task Dependencies ===")
    
    try:
        with patch('airflow.models.Variable'), \
             patch('airflow.operators.python.PythonOperator'), \
             patch('airflow.operators.bash.BashOperator'), \
             patch('airflow.operators.dummy.DummyOperator'), \
             patch('airflow.providers.slack.operators.slack_webhook.SlackWebhookOperator'), \
             patch('airflow.providers.postgres.operators.postgres.PostgresOperator'), \
             patch('operators.incremental_replication_operator.IncrementalReplicationOperator'), \
             patch('operators.incremental_replication_operator.ReplicationValidationOperator'):
            
            import daily_etl_pipeline
            dag = daily_etl_pipeline.dag
            
            # Get task dependencies
            task_dict = {task.task_id: task for task in dag.tasks}
            
            # Check start task has no upstream dependencies
            start_task = task_dict.get('start_pipeline')
            if start_task and len(start_task.upstream_task_ids) == 0:
                print("✓ Start task has no upstream dependencies")
            else:
                print("✗ Start task configuration issue")
                return False
            
            # Check prerequisite validation comes after start
            prereq_task = task_dict.get('validate_prerequisites')
            if prereq_task and 'start_pipeline' in prereq_task.upstream_task_ids:
                print("✓ Prerequisites validation properly connected")
            else:
                print("✗ Prerequisites validation dependency issue")
                return False
            
            # Check that ingestion_complete has TaskGroup dependencies
            ingestion_complete = task_dict.get('ingestion_complete')
            if ingestion_complete:
                # Should have upstream dependencies from ingestion TaskGroup
                upstream_count = len(ingestion_complete.upstream_task_ids)
                print(f"✓ Ingestion complete has {upstream_count} upstream dependencies")
            else:
                print("✗ Missing ingestion_complete task")
                return False
            
            return True
            
    except Exception as e:
        print(f"✗ Task dependencies test failed: {e}")
        return False


def run_all_tests():
    """Run all DAG validation tests."""
    print("STARTING DAG STRUCTURE VALIDATION")
    print("=" * 60)
    
    tests = [
        ("DAG Import", test_dag_import),
        ("DAG Structure", test_dag_structure),
        ("DAG Configuration", test_dag_configuration),
        ("Pipeline Configuration", test_pipeline_config),
        ("Task Dependencies", test_task_dependencies),
    ]
    
    results = []
    
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"✗ {test_name} failed with exception: {e}")
            results.append((test_name, False))
    
    # Summary
    print("\n" + "=" * 60)
    print("TEST SUMMARY")
    print("=" * 60)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "PASS" if result else "FAIL"
        print(f"{test_name:.<35} {status}")
    
    print("-" * 60)
    print(f"Tests passed: {passed}/{total} ({passed/total*100:.1f}%)")
    
    if passed == total:
        print("\nAll tests passed! The ETL pipeline DAG is ready for deployment.")
        print("\nNext Steps:")
        print("1. Set up Airflow connections (postgres_source, postgres_dwh, slack_webhook)")
        print("2. Configure Airflow pools using pool_configuration.py")
        print("3. Set Airflow Variables (dbt_profiles_dir, ge_config_path)")
        print("4. Deploy DAG to Airflow environment")
        print("5. Enable the DAG in Airflow UI")
        print("\nSee README_etl_orchestration.md for detailed setup instructions")
        return True
    else:
        print(f"\n{total - passed} test(s) failed. Please check the errors above.")
        return False


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
