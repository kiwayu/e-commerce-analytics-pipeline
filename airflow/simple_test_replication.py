#!/usr/bin/env python3
"""
Simplified test script for database replication components.
Tests basic functionality without requiring external dependencies like pandas.
"""

import os
import sys
import tempfile
import logging
from datetime import datetime, timedelta
from unittest.mock import Mock, patch

# Add airflow directory to path
airflow_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(airflow_dir, 'plugins'))
sys.path.insert(0, os.path.join(airflow_dir, 'dags'))

def test_imports():
    """Test that all components can be imported."""
    print("\n=== Testing Imports ===")
    
    try:
        # Test utility imports
        from utils.replication_utils import WatermarkManager, ReplicationMetrics
        print("✓ Utility modules imported successfully")
        
        # Test hook imports
        from hooks.postgres_replication_hook import PostgreSQLReplicationHook
        print("✓ PostgreSQL replication hook imported successfully")
        
        # Test operator imports
        from operators.incremental_replication_operator import (
            IncrementalReplicationOperator,
            ReplicationValidationOperator
        )
        print("✓ Replication operators imported successfully")
        
        print("✓ All imports successful")
        return True
        
    except ImportError as e:
        print(f"✗ Import failed: {e}")
        return False
    except Exception as e:
        print(f"✗ Unexpected error during import: {e}")
        return False

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
        
        # Test schema prefix removal
        key_with_schema = WatermarkManager.get_watermark_variable_key("raw.customers", "updated_at")
        assert key_with_schema == expected_key, "Schema prefix should be removed"
        print("✓ Schema prefix removal works correctly")
        
        # Test watermark operations with mocked Airflow Variables
        with patch('airflow.models.Variable.get') as mock_get, \
             patch('airflow.models.Variable.set') as mock_set:
            
            # Test setting watermark
            test_date = datetime.now()
            mock_set.return_value = None
            result = WatermarkManager.set_watermark("test_table", test_date)
            assert result == True, "Set watermark should return True"
            mock_set.assert_called_once()
            print("✓ Set watermark functionality works")
            
            # Test getting watermark when exists
            mock_get.return_value = test_date.isoformat()
            retrieved_watermark = WatermarkManager.get_watermark("test_table")
            assert retrieved_watermark is not None, "Should retrieve watermark"
            print("✓ Get watermark functionality works")
            
            # Test getting watermark when doesn't exist
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
    """Test replication metrics calculations."""
    print("\n=== Testing Replication Metrics ===")
    
    try:
        from utils.replication_utils import ReplicationMetrics
        
        # Test lag calculation
        source_time = datetime.now()
        current_time = source_time - timedelta(hours=2)
        
        lag_metrics = ReplicationMetrics.calculate_replication_lag(source_time, current_time)
        
        # Check that we got the expected structure
        expected_keys = ['lag_seconds', 'lag_hours', 'lag_days', 'status']
        for key in expected_keys:
            assert key in lag_metrics, f"Missing key: {key}"
        
        assert lag_metrics['lag_hours'] == 2.0, f"Expected 2 hours lag, got {lag_metrics['lag_hours']}"
        assert lag_metrics['status'] == 'lagging', f"Expected 'lagging' status, got {lag_metrics['status']}"
        print("✓ Lag calculation works correctly")
        
        # Test throughput calculation
        throughput_metrics = ReplicationMetrics.calculate_throughput_metrics(
            records_processed=1000,
            duration_seconds=10.0,
            data_size_mb=5.0
        )
        
        expected_throughput_keys = ['records_per_second', 'records_per_minute', 'duration_seconds']
        for key in expected_throughput_keys:
            assert key in throughput_metrics, f"Missing throughput key: {key}"
        
        assert throughput_metrics['records_per_second'] == 100.0, "Throughput calculation incorrect"
        assert throughput_metrics['mb_per_second'] == 0.5, "Data throughput calculation incorrect"
        print("✓ Throughput calculation works correctly")
        
        # Test zero duration handling
        zero_duration_metrics = ReplicationMetrics.calculate_throughput_metrics(100, 0)
        assert zero_duration_metrics['records_per_second'] == 0, "Should handle zero duration"
        print("✓ Zero duration handling works correctly")
        
        # Test no watermark case
        no_watermark_lag = ReplicationMetrics.calculate_replication_lag(source_time, None)
        assert no_watermark_lag['status'] == 'no_watermark', "Should handle no watermark case"
        print("✓ No watermark case handled correctly")
        
        print("✓ Replication Metrics test completed successfully")
        return True
        
    except Exception as e:
        print(f"✗ Replication Metrics test failed: {e}")
        return False

def test_operator_initialization():
    """Test operator initialization and validation."""
    print("\n=== Testing Operator Initialization ===")
    
    try:
        from operators.incremental_replication_operator import (
            IncrementalReplicationOperator,
            ReplicationValidationOperator
        )
        
        # Test valid initialization
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
        assert operator.primary_key_columns == ['customer_id'], "Primary key columns not set correctly"
        print("✓ Valid operator initialization works")
        
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
            print("✓ Invalid replication mode validation works")
        
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
            print("✓ Upsert mode validation works")
        
        # Test validation operator
        validation_operator = ReplicationValidationOperator(
            task_id='test_validation',
            source_table='raw.raw_customers',
            target_table='staging.customers',
            max_lag_hours=2
        )
        
        assert validation_operator.task_id == 'test_validation', "Validation operator task ID incorrect"
        assert validation_operator.max_lag_hours == 2, "Max lag hours not set correctly"
        print("✓ Validation operator initialization works")
        
        print("✓ Operator Initialization test completed successfully")
        return True
        
    except Exception as e:
        print(f"✗ Operator Initialization test failed: {e}")
        return False

def test_hook_initialization():
    """Test hook initialization."""
    print("\n=== Testing Hook Initialization ===")
    
    try:
        # Mock the PostgresHook since we don't have actual connections
        with patch('hooks.postgres_replication_hook.PostgresHook'):
            from hooks.postgres_replication_hook import PostgreSQLReplicationHook
            
            # Test hook creation
            hook = PostgreSQLReplicationHook(
                source_conn_id="test_source",
                target_conn_id="test_target"
            )
            
            assert hook.source_conn_id == "test_source", "Source connection ID not set"
            assert hook.target_conn_id == "test_target", "Target connection ID not set"
            print("✓ Hook initialization works correctly")
            
            # Test watermark methods with mocked Variable
            with patch('airflow.models.Variable.get') as mock_get, \
                 patch('airflow.models.Variable.set') as mock_set:
                
                # Test get watermark
                test_watermark = datetime.now()
                mock_get.return_value = test_watermark.isoformat()
                
                retrieved = hook.get_watermark("test_table", "updated_at")
                assert retrieved is not None, "Should retrieve watermark"
                print("✓ Hook get watermark method works")
                
                # Test set watermark
                mock_set.return_value = None
                hook.set_watermark("test_table", test_watermark, "updated_at")
                mock_set.assert_called_once()
                print("✓ Hook set watermark method works")
        
        print("✓ Hook Initialization test completed successfully")
        return True
        
    except Exception as e:
        print(f"✗ Hook Initialization test failed: {e}")
        return False

def test_dag_structure():
    """Test DAG structure and basic configuration."""
    print("\n=== Testing DAG Structure ===")
    
    try:
        # Mock all the dependencies to test DAG structure
        with patch('airflow.models.Variable'), \
             patch('operators.incremental_replication_operator.IncrementalReplicationOperator'), \
             patch('operators.incremental_replication_operator.ReplicationValidationOperator'), \
             patch('airflow.operators.python.PythonOperator'), \
             patch('airflow.operators.email.EmailOperator'), \
             patch('airflow.sensors.sql.SqlSensor'):
            
            # Import DAGs
            import incremental_replication_dag as dag_module
            
            # Test main DAG
            main_dag = dag_module.dag
            assert main_dag.dag_id == 'incremental_customer_replication', "Main DAG ID incorrect"
            print("✓ Main DAG ID set correctly")
            
            # Test monitoring DAG
            monitoring_dag = dag_module.monitoring_dag
            assert monitoring_dag.dag_id == 'replication_health_monitoring', "Monitoring DAG ID incorrect"
            print("✓ Monitoring DAG ID set correctly")
            
            # Test schedule intervals
            assert main_dag.schedule_interval == timedelta(minutes=30), "Main DAG schedule incorrect"
            assert monitoring_dag.schedule_interval == timedelta(hours=1), "Monitoring DAG schedule incorrect"
            print("✓ DAG schedules set correctly")
            
            # Test DAG configuration
            assert main_dag.max_active_runs == 1, "Main DAG max active runs should be 1"
            assert main_dag.catchup == False, "Main DAG catchup should be False"
            print("✓ DAG configuration set correctly")
            
            # Test replication config
            replication_config = dag_module.REPLICATION_CONFIG
            expected_config_keys = ['source_table', 'target_table', 'watermark_column', 'replication_mode']
            for key in expected_config_keys:
                assert key in replication_config, f"Missing config key: {key}"
            print("✓ Replication configuration structure correct")
        
        print("✓ DAG Structure test completed successfully")
        return True
        
    except Exception as e:
        print(f"✗ DAG Structure test failed: {e}")
        return False

def test_quality_checks_structure():
    """Test quality checks configuration structure."""
    print("\n=== Testing Quality Checks Structure ===")
    
    try:
        # Import quality checks from DAG
        with patch('airflow.models.Variable'), \
             patch('operators.incremental_replication_operator.IncrementalReplicationOperator'):
            
            import incremental_replication_dag as dag_module
            
            quality_checks = dag_module.QUALITY_CHECKS
            
            # Check structure
            expected_check_types = ['null_check', 'duplicate_check', 'value_range_check', 'record_count_check']
            for check_type in expected_check_types:
                assert check_type in quality_checks, f"Missing quality check type: {check_type}"
            
            # Check null_check structure
            null_check = quality_checks['null_check']
            assert 'columns' in null_check, "null_check should have columns"
            assert 'max_null_percentage' in null_check, "null_check should have max_null_percentage"
            assert isinstance(null_check['columns'], list), "columns should be a list"
            print("✓ Null check configuration correct")
            
            # Check duplicate_check structure
            duplicate_check = quality_checks['duplicate_check']
            assert 'columns' in duplicate_check, "duplicate_check should have columns"
            assert 'max_duplicates' in duplicate_check, "duplicate_check should have max_duplicates"
            print("✓ Duplicate check configuration correct")
            
            # Check value_range_check structure
            value_range_check = quality_checks['value_range_check']
            assert isinstance(value_range_check, dict), "value_range_check should be a dict"
            print("✓ Value range check configuration correct")
            
            # Check record_count_check structure
            record_count_check = quality_checks['record_count_check']
            assert 'min_records' in record_count_check, "record_count_check should have min_records"
            assert 'max_records' in record_count_check, "record_count_check should have max_records"
            print("✓ Record count check configuration correct")
        
        print("✓ Quality Checks Structure test completed successfully")
        return True
        
    except Exception as e:
        print(f"✗ Quality Checks Structure test failed: {e}")
        return False

def run_all_tests():
    """Run all test functions."""
    print("STARTING SIMPLIFIED DATABASE REPLICATION TESTS")
    print("=" * 65)
    
    # Setup basic logging
    logging.basicConfig(level=logging.WARNING)
    
    tests = [
        ("Component Imports", test_imports),
        ("Watermark Manager", test_watermark_manager),
        ("Replication Metrics", test_replication_metrics),
        ("Operator Initialization", test_operator_initialization),
        ("Hook Initialization", test_hook_initialization),
        ("DAG Structure", test_dag_structure),
        ("Quality Checks Structure", test_quality_checks_structure),
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
    print("\n" + "=" * 65)
    print("TEST SUMMARY")
    print("=" * 65)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "PASS" if result else "FAIL"
        print(f"{test_name:.<40} {status}")
    
    print("-" * 65)
    print(f"Tests passed: {passed}/{total} ({passed/total*100:.1f}%)")
    
    if passed == total:
        print("\nAll tests passed! The database replication system is ready.")
        print("\nNext Steps:")
        print("1. Set up Airflow connections (postgres_source, postgres_dwh)")
        print("2. Copy plugins and DAGs to Airflow directories")
        print("3. Enable the replication DAGs in Airflow UI")
        print("4. Monitor the first replication run")
        print("\nSee README_replication.md for detailed documentation")
        return True
    else:
        print(f"\n{total - passed} test(s) failed. Please check the errors above.")
        return False

if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
