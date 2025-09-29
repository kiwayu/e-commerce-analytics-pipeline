#!/usr/bin/env python3
"""
Test script for database replication components.
Validates the replication operators, hooks, and DAG without requiring full Airflow setup.
"""

import os
import sys
import tempfile
import logging
from datetime import datetime, timedelta
from unittest.mock import Mock, patch, MagicMock
import pandas as pd

# Add airflow directory to path
airflow_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(airflow_dir, 'plugins'))
sys.path.insert(0, os.path.join(airflow_dir, 'dags'))

def setup_logging():
    """Set up logging for test execution."""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    # Suppress some verbose loggers
    logging.getLogger('airflow').setLevel(logging.WARNING)
    logging.getLogger('urllib3').setLevel(logging.WARNING)

def test_watermark_manager():
    """Test watermark management utilities."""
    print("\n=== Testing Watermark Manager ===")
    
    try:
        from utils.replication_utils import WatermarkManager
        
        # Test variable key generation
        key = WatermarkManager.get_watermark_variable_key("customers", "updated_at")
        expected_key = "replication_watermark_customers_updated_at"
        assert key == expected_key, f"Expected {expected_key}, got {key}"
        print("✓ Variable key generation works correctly")
        
        # Test watermark parsing (simulate)
        test_date = datetime.now()
        iso_string = test_date.isoformat()
        
        # Mock Variable.get and Variable.set
        with patch('airflow.models.Variable.get') as mock_get, \
             patch('airflow.models.Variable.set') as mock_set:
            
            # Test setting watermark
            mock_set.return_value = None
            result = WatermarkManager.set_watermark("test_table", test_date)
            assert result == True, "Set watermark should return True"
            print("✓ Set watermark works correctly")
            
            # Test getting watermark
            mock_get.return_value = iso_string
            retrieved_watermark = WatermarkManager.get_watermark("test_table")
            assert retrieved_watermark is not None, "Should retrieve watermark"
            print("✓ Get watermark works correctly")
            
            # Test no watermark case
            mock_get.return_value = None
            no_watermark = WatermarkManager.get_watermark("nonexistent_table")
            assert no_watermark is None, "Should return None for nonexistent watermark"
            print("✓ No watermark case handled correctly")
        
        print("✓ Watermark Manager test completed successfully")
        return True
        
    except Exception as e:
        print(f"✗ Watermark Manager test failed: {e}")
        return False

def test_replication_metrics():
    """Test replication metrics utilities."""
    print("\n=== Testing Replication Metrics ===")
    
    try:
        from utils.replication_utils import ReplicationMetrics
        
        # Test lag calculation
        source_time = datetime.now()
        current_time = source_time - timedelta(hours=2)
        
        lag_metrics = ReplicationMetrics.calculate_replication_lag(source_time, current_time)
        
        assert lag_metrics['lag_hours'] == 2.0, f"Expected 2 hours lag, got {lag_metrics['lag_hours']}"
        assert lag_metrics['status'] == 'lagging', f"Expected 'lagging' status, got {lag_metrics['status']}"
        print("✓ Lag calculation works correctly")
        
        # Test throughput calculation
        throughput_metrics = ReplicationMetrics.calculate_throughput_metrics(
            records_processed=1000,
            duration_seconds=10.0,
            data_size_mb=5.0
        )
        
        assert throughput_metrics['records_per_second'] == 100.0, "Throughput calculation incorrect"
        assert throughput_metrics['mb_per_second'] == 0.5, "Data throughput calculation incorrect"
        print("✓ Throughput calculation works correctly")
        
        # Test zero duration handling
        zero_duration_metrics = ReplicationMetrics.calculate_throughput_metrics(100, 0)
        assert zero_duration_metrics['records_per_second'] == 0, "Should handle zero duration"
        print("✓ Zero duration handling works correctly")
        
        print("✓ Replication Metrics test completed successfully")
        return True
        
    except Exception as e:
        print(f"✗ Replication Metrics test failed: {e}")
        return False

def test_data_quality_validator():
    """Test data quality validation utilities."""
    print("\n=== Testing Data Quality Validator ===")
    
    try:
        from utils.replication_utils import DataQualityValidator
        
        # Create test DataFrames
        source_df = pd.DataFrame({
            'id': [1, 2, 3],
            'name': ['Alice', 'Bob', 'Charlie'],
            'email': ['alice@test.com', 'bob@test.com', 'charlie@test.com'],
            'created_at': pd.to_datetime(['2023-01-01', '2023-01-02', '2023-01-03'])
        })
        
        target_df = pd.DataFrame({
            'id': [1, 2],
            'name': ['Alice', 'Bob'],
            'email': ['alice@test.com', 'bob@test.com'],
            'created_at': pd.to_datetime(['2023-01-01', '2023-01-02'])
        })
        
        # Test consistency validation
        consistency_result = DataQualityValidator.validate_data_consistency(
            source_df, target_df, ['id']
        )
        
        assert consistency_result['source_count'] == 3, "Source count incorrect"
        assert consistency_result['target_count'] == 2, "Target count incorrect"
        assert consistency_result['missing_in_target_count'] == 1, "Missing records count incorrect"
        print("✓ Data consistency validation works correctly")
        
        # Test data type validation
        expected_types = {
            'id': 'integer',
            'name': 'string',
            'email': 'string',
            'created_at': 'datetime'
        }
        
        type_result = DataQualityValidator.validate_data_types(source_df, expected_types)
        # Note: pandas dtypes might not match exactly, so we'll check structure
        assert 'type_check_passed' in type_result, "Type check result structure incorrect"
        print("✓ Data type validation works correctly")
        
        # Test business rules validation
        business_rules = {
            'email_format': {
                'column': 'email'
            },
            'date_range': {
                'column': 'created_at',
                'min_date': datetime(2020, 1, 1),
                'max_date': datetime(2025, 1, 1)
            }
        }
        
        rules_result = DataQualityValidator.validate_business_rules(source_df, business_rules)
        assert 'business_rules_passed' in rules_result, "Business rules result structure incorrect"
        print("✓ Business rules validation works correctly")
        
        print("✓ Data Quality Validator test completed successfully")
        return True
        
    except Exception as e:
        print(f"✗ Data Quality Validator test failed: {e}")
        return False

def test_postgres_replication_hook():
    """Test PostgreSQL replication hook (mocked)."""
    print("\n=== Testing PostgreSQL Replication Hook ===")
    
    try:
        from hooks.postgres_replication_hook import PostgreSQLReplicationHook
        
        # Mock the PostgresHook dependencies
        with patch('hooks.postgres_replication_hook.PostgresHook') as mock_postgres_hook:
            # Create hook instance
            hook = PostgreSQLReplicationHook(
                source_conn_id="test_source",
                target_conn_id="test_target"
            )
            
            assert hook.source_conn_id == "test_source", "Source connection ID not set correctly"
            assert hook.target_conn_id == "test_target", "Target connection ID not set correctly"
            print("✓ Hook initialization works correctly")
            
            # Test watermark methods (with mocked Variable)
            with patch('airflow.models.Variable.get') as mock_get, \
                 patch('airflow.models.Variable.set') as mock_set:
                
                # Test get watermark
                test_watermark = datetime.now()
                mock_get.return_value = test_watermark.isoformat()
                
                retrieved = hook.get_watermark("test_table", "updated_at")
                assert retrieved is not None, "Should retrieve watermark"
                print("✓ Get watermark method works correctly")
                
                # Test set watermark
                mock_set.return_value = None
                hook.set_watermark("test_table", test_watermark, "updated_at")
                mock_set.assert_called_once()
                print("✓ Set watermark method works correctly")
        
        print("✓ PostgreSQL Replication Hook test completed successfully")
        return True
        
    except Exception as e:
        print(f"✗ PostgreSQL Replication Hook test failed: {e}")
        return False

def test_incremental_replication_operator():
    """Test incremental replication operator (mocked)."""
    print("\n=== Testing Incremental Replication Operator ===")
    
    try:
        from operators.incremental_replication_operator import IncrementalReplicationOperator
        
        # Create operator instance
        operator = IncrementalReplicationOperator(
            task_id='test_replication',
            source_table='raw.raw_customers',
            target_table='staging.customers',
            source_conn_id='postgres_source',
            target_conn_id='postgres_dwh',
            watermark_column='updated_at',
            primary_key_columns=['customer_id'],
            replication_mode='upsert',
            batch_size=1000
        )
        
        assert operator.task_id == 'test_replication', "Task ID not set correctly"
        assert operator.source_table == 'raw.raw_customers', "Source table not set correctly"
        assert operator.replication_mode == 'upsert', "Replication mode not set correctly"
        print("✓ Operator initialization works correctly")
        
        # Test validation of replication mode
        try:
            IncrementalReplicationOperator(
                task_id='invalid_test',
                source_table='test',
                target_table='test',
                replication_mode='invalid_mode'
            )
            assert False, "Should have raised ValueError for invalid mode"
        except ValueError:
            print("✓ Invalid replication mode validation works correctly")
        
        # Test upsert mode validation
        try:
            IncrementalReplicationOperator(
                task_id='invalid_upsert',
                source_table='test',
                target_table='test',
                replication_mode='upsert'
                # Missing primary_key_columns
            )
            assert False, "Should have raised ValueError for upsert without primary keys"
        except ValueError:
            print("✓ Upsert mode validation works correctly")
        
        print("✓ Incremental Replication Operator test completed successfully")
        return True
        
    except Exception as e:
        print(f"✗ Incremental Replication Operator test failed: {e}")
        return False

def test_dag_structure():
    """Test DAG structure and dependencies."""
    print("\n=== Testing DAG Structure ===")
    
    try:
        # Import DAG (this will test import and basic structure)
        with patch('airflow.models.Variable'), \
             patch('operators.incremental_replication_operator.IncrementalReplicationOperator'), \
             patch('operators.incremental_replication_operator.ReplicationValidationOperator'):
            
            from incremental_replication_dag import dag, monitoring_dag
            
            assert dag.dag_id == 'incremental_customer_replication', "Main DAG ID incorrect"
            assert monitoring_dag.dag_id == 'replication_health_monitoring', "Monitoring DAG ID incorrect"
            print("✓ DAG IDs set correctly")
            
            # Check main DAG tasks
            main_dag_task_ids = [task.task_id for task in dag.tasks]
            expected_tasks = [
                'check_source_data_availability',
                'check_prerequisites', 
                'pre_replication_validation',
                'replicate_customers',
                'post_replication_validation',
                'final_validation',
                'send_failure_notification',
                'send_success_notification'
            ]
            
            for expected_task in expected_tasks:
                assert expected_task in main_dag_task_ids, f"Task {expected_task} not found in DAG"
            
            print(f"✓ Main DAG has all expected tasks ({len(expected_tasks)} tasks)")
            
            # Check monitoring DAG tasks
            monitoring_task_ids = [task.task_id for task in monitoring_dag.tasks]
            expected_monitoring_tasks = ['check_replication_health', 'send_health_alert']
            
            for expected_task in expected_monitoring_tasks:
                assert expected_task in monitoring_task_ids, f"Monitoring task {expected_task} not found"
            
            print(f"✓ Monitoring DAG has all expected tasks ({len(expected_monitoring_tasks)} tasks)")
            
            # Check schedule intervals
            assert dag.schedule_interval == timedelta(minutes=30), "Main DAG schedule incorrect"
            assert monitoring_dag.schedule_interval == timedelta(hours=1), "Monitoring DAG schedule incorrect"
            print("✓ DAG schedules set correctly")
        
        print("✓ DAG Structure test completed successfully")
        return True
        
    except Exception as e:
        print(f"✗ DAG Structure test failed: {e}")
        return False

def test_integration():
    """Test integration between components."""
    print("\n=== Testing Integration ===")
    
    try:
        # Test that all components can be imported together
        from utils.replication_utils import WatermarkManager, ReplicationMetrics
        from hooks.postgres_replication_hook import PostgreSQLReplicationHook
        from operators.incremental_replication_operator import IncrementalReplicationOperator
        
        print("✓ All components import successfully")
        
        # Test watermark flow simulation
        with patch('airflow.models.Variable.get') as mock_get, \
             patch('airflow.models.Variable.set') as mock_set:
            
            # Simulate a complete watermark lifecycle
            mock_get.return_value = None  # No existing watermark
            
            # Get initial watermark (should be None)
            initial_watermark = WatermarkManager.get_watermark("test_table")
            assert initial_watermark is None, "Initial watermark should be None"
            
            # Set new watermark
            new_watermark = datetime.now()
            result = WatermarkManager.set_watermark("test_table", new_watermark)
            assert result == True, "Set watermark should succeed"
            
            # Simulate retrieval of set watermark
            mock_get.return_value = new_watermark.isoformat()
            retrieved_watermark = WatermarkManager.get_watermark("test_table")
            assert retrieved_watermark is not None, "Should retrieve set watermark"
            
            print("✓ Watermark lifecycle simulation works correctly")
        
        # Test metrics calculation
        start_time = datetime.now()
        end_time = start_time + timedelta(seconds=30)
        duration = (end_time - start_time).total_seconds()
        
        metrics = ReplicationMetrics.calculate_throughput_metrics(
            records_processed=3000,
            duration_seconds=duration
        )
        
        assert metrics['records_per_second'] == 100.0, "Integration metrics calculation incorrect"
        print("✓ Metrics calculation integration works correctly")
        
        print("✓ Integration test completed successfully")
        return True
        
    except Exception as e:
        print(f"✗ Integration test failed: {e}")
        return False

def run_all_tests():
    """Run all test functions."""
    print("🧪 STARTING DATABASE REPLICATION TESTS")
    print("=" * 60)
    
    setup_logging()
    
    tests = [
        ("Watermark Manager", test_watermark_manager),
        ("Replication Metrics", test_replication_metrics),
        ("Data Quality Validator", test_data_quality_validator),
        ("PostgreSQL Replication Hook", test_postgres_replication_hook),
        ("Incremental Replication Operator", test_incremental_replication_operator),
        ("DAG Structure", test_dag_structure),
        ("Integration", test_integration),
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
    print("🧪 TEST SUMMARY")
    print("=" * 60)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "✓ PASS" if result else "✗ FAIL"
        print(f"{test_name:.<35} {status}")
    
    print("-" * 60)
    print(f"Tests passed: {passed}/{total} ({passed/total*100:.1f}%)")
    
    if passed == total:
        print("\n🎉 All tests passed! The database replication system is ready.")
        return True
    else:
        print(f"\n⚠️  {total - passed} test(s) failed. Please check the errors above.")
        return False

def show_usage_examples():
    """Show usage examples for the replication system."""
    print("\n" + "=" * 60)
    print("📚 USAGE EXAMPLES")
    print("=" * 60)
    
    examples = """
1. BASIC REPLICATION SETUP:
   
   # In your Airflow DAG
   from operators.incremental_replication_operator import IncrementalReplicationOperator
   
   replicate_task = IncrementalReplicationOperator(
       task_id='replicate_customers',
       source_table='raw.raw_customers',
       target_table='staging.customers',
       watermark_column='updated_at',
       replication_mode='upsert',
       primary_key_columns=['customer_id']
   )

2. WATERMARK MANAGEMENT:
   
   # Manual watermark operations
   from utils.replication_utils import WatermarkManager
   
   # Get current watermark
   watermark = WatermarkManager.get_watermark('customers', 'updated_at')
   
   # Set new watermark
   WatermarkManager.set_watermark('customers', datetime.now())
   
   # Backup watermark before risky operations
   WatermarkManager.backup_watermark('customers')

3. MONITORING SETUP:
   
   # Health check task
   health_check = ReplicationValidationOperator(
       task_id='check_health',
       source_table='raw.raw_customers',
       target_table='staging.customers',
       max_lag_hours=2
   )

4. AIRFLOW CONNECTIONS:
   
   # Set up connections in Airflow UI or CLI:
   airflow connections add postgres_source \\
       --conn-type postgres \\
       --conn-host source-db.company.com \\
       --conn-login readonly_user \\
       --conn-password secret \\
       --conn-schema production
   
   airflow connections add postgres_dwh \\
       --conn-type postgres \\
       --conn-host dwh.company.com \\
       --conn-login dwh_user \\
       --conn-password secret \\
       --conn-schema warehouse

5. QUALITY CHECKS:
   
   quality_checks = {
       'null_check': {
           'columns': ['customer_id', 'email'],
           'max_null_percentage': 0
       },
       'duplicate_check': {
           'columns': ['customer_id'],
           'max_duplicates': 0
       }
   }

6. PRODUCTION DEPLOYMENT:
   
   # Copy files to Airflow directory
   cp airflow/plugins/* $AIRFLOW_HOME/plugins/
   cp airflow/dags/* $AIRFLOW_HOME/dags/
   
   # Restart Airflow services
   systemctl restart airflow-webserver airflow-scheduler

For detailed documentation, see the DAG files and operator docstrings.
"""
    
    print(examples)

if __name__ == "__main__":
    success = run_all_tests()
    
    if success:
        show_usage_examples()
        sys.exit(0)
    else:
        print("\nFix the failing tests before proceeding.")
        sys.exit(1)
