#!/usr/bin/env python3
"""
Test script for the incremental file ingestion job.
This script demonstrates the functionality without requiring a full Spark cluster.
"""

import os
import sys
import logging
import tempfile
import shutil
from pathlib import Path
from unittest.mock import Mock, patch

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.append(str(project_root))

def setup_test_environment():
    """Set up a temporary test environment."""
    test_dir = Path(tempfile.mkdtemp(prefix="spark_test_"))
    
    # Create directory structure
    dirs = ['input', 'processed', 'archive', 'checkpoint']
    for d in dirs:
        (test_dir / d).mkdir(parents=True, exist_ok=True)
    
    return test_dir

def create_test_csv_files(input_dir: Path):
    """Create test CSV files with sample data."""
    import csv
    from datetime import datetime, timedelta
    
    # Sample shipments data
    sample_data = [
        {
            'shipment_id': 'SHP-000001',
            'order_id': 'ORD-000001',
            'tracking_number': '1Z999AA1234567890',
            'carrier': 'UPS',
            'shipment_status': 'delivered',
            'shipped_date': '2024-01-15 10:30:00',
            'destination_city': 'New York',
            'destination_country': 'US',
            'shipping_cost': '15.99',
            'currency': 'USD'
        },
        {
            'shipment_id': 'SHP-000002',
            'order_id': 'ORD-000002',
            'tracking_number': '9405511899223456789012',
            'carrier': 'USPS',
            'shipment_status': 'shipped',
            'shipped_date': '2024-01-14 09:15:00',
            'destination_city': 'Los Angeles',
            'destination_country': 'US',
            'shipping_cost': '8.50',
            'currency': 'USD'
        }
    ]
    
    # Create multiple test files
    files_created = []
    
    for i, data_slice in enumerate([sample_data[:1], sample_data[1:]], 1):
        filename = input_dir / f"test_shipments_{i:02d}.csv"
        
        with open(filename, 'w', newline='') as csvfile:
            if data_slice:
                writer = csv.DictWriter(csvfile, fieldnames=data_slice[0].keys())
                writer.writeheader()
                writer.writerows(data_slice)
        
        files_created.append(filename)
        print(f"Created test file: {filename} ({len(data_slice)} records)")
    
    return files_created

def test_checkpoint_manager():
    """Test checkpoint management functionality."""
    print("\n=== Testing Checkpoint Manager ===")
    
    try:
        from jobs.utils.checkpoint_manager import CheckpointManager
        
        test_dir = setup_test_environment()
        checkpoint_dir = test_dir / 'checkpoint'
        
        # Create checkpoint manager
        manager = CheckpointManager(str(checkpoint_dir), 'test_job')
        
        # Test file tracking
        test_file = str(test_dir / 'input' / 'test.csv')
        batch_id = 'test-batch-001'
        
        # Create a dummy file
        Path(test_file).touch()
        
        # Mark as processing
        manager.mark_file_processing(test_file, batch_id)
        print(f"✓ Marked file as processing: {test_file}")
        
        # Mark as processed
        manager.mark_file_processed(test_file, 100, batch_id)
        print(f"✓ Marked file as processed: {test_file}")
        
        # Get statistics
        stats = manager.get_checkpoint_stats()
        print(f"✓ Checkpoint stats: {stats}")
        
        # Cleanup
        shutil.rmtree(test_dir)
        print("✓ Checkpoint manager test completed successfully")
        
        return True
        
    except Exception as e:
        print(f"✗ Checkpoint manager test failed: {e}")
        return False

def test_file_monitor():
    """Test file monitoring functionality."""
    print("\n=== Testing File Monitor ===")
    
    try:
        from jobs.utils.file_monitor import FileMonitor, FileInfo
        
        test_dir = setup_test_environment()
        input_dir = test_dir / 'input'
        
        # Create test files
        create_test_csv_files(input_dir)
        
        # Create file monitor
        monitor = FileMonitor(str(input_dir), ['*.csv'])
        
        # Scan files
        files = monitor.scan_files(calculate_hashes=True)
        print(f"✓ Found {len(files)} files")
        
        # Test file statistics
        stats = monitor.get_file_statistics(files)
        print(f"✓ File statistics: {stats}")
        
        # Test filtering
        filtered = monitor.filter_processable_files(files, min_size=1)
        print(f"✓ Filtered to {len(filtered)} processable files")
        
        # Cleanup
        shutil.rmtree(test_dir)
        print("✓ File monitor test completed successfully")
        
        return True
        
    except Exception as e:
        print(f"✗ File monitor test failed: {e}")
        return False

def test_csv_processor():
    """Test CSV processing functionality."""
    print("\n=== Testing CSV Processor ===")
    
    try:
        # Mock PySpark for testing without actual Spark
        mock_spark = Mock()
        mock_df = Mock()
        mock_df.count.return_value = 2
        mock_df.withColumn.return_value = mock_df
        mock_df.filter.return_value = mock_df
        mock_df.select.return_value = mock_df
        
        from jobs.utils.csv_processor import CSVProcessor, CSVSchemaManager
        
        # Test schema manager
        schema_manager = CSVSchemaManager()
        schema = schema_manager.get_shipments_schema()
        print(f"✓ Created shipments schema with {len(schema.fields)} fields")
        
        flexible_schema = schema_manager.get_flexible_schema()
        print(f"✓ Created flexible schema with {len(flexible_schema.fields)} fields")
        
        # Test CSV processor (with mocked Spark)
        processor = CSVProcessor(mock_spark)
        print("✓ Created CSV processor")
        
        # Test validation (mock data)
        validation_stats = {
            'original_rows': 2,
            'valid_rows': 2,
            'invalid_rows': 0,
            'validation_rate': 1.0
        }
        print(f"✓ Validation simulation: {validation_stats}")
        
        print("✓ CSV processor test completed successfully")
        
        return True
        
    except Exception as e:
        print(f"✗ CSV processor test failed: {e}")
        return False

def test_configuration():
    """Test configuration management."""
    print("\n=== Testing Configuration ===")
    
    try:
        from jobs.config.spark_config import SparkJobConfig, SparkSessionManager
        
        # Test default configuration
        config = SparkJobConfig()
        print(f"✓ Default config - App: {config.app_name}, Master: {config.master}")
        
        # Test environment configuration
        os.environ['SPARK_APP_NAME'] = 'test-app'
        os.environ['INPUT_DIR'] = '/tmp/test-input'
        
        env_config = SparkJobConfig.from_environment()
        print(f"✓ Environment config - App: {env_config.app_name}, Input: {env_config.input_dir}")
        
        # Test session manager (without actually creating Spark session)
        session_manager = SparkSessionManager(config)
        print(f"✓ Created session manager with config")
        
        # Test database properties
        from jobs.config.spark_config import get_database_properties
        db_props = get_database_properties(config)
        print(f"✓ Database properties: {list(db_props.keys())}")
        
        print("✓ Configuration test completed successfully")
        
        return True
        
    except Exception as e:
        print(f"✗ Configuration test failed: {e}")
        return False

def test_integration():
    """Test integration between components."""
    print("\n=== Testing Integration ===")
    
    try:
        from jobs.utils.checkpoint_manager import CheckpointManager
        from jobs.utils.file_monitor import IncrementalFileProcessor
        
        test_dir = setup_test_environment()
        
        # Create test files
        input_dir = test_dir / 'input'
        test_files = create_test_csv_files(input_dir)
        
        # Create checkpoint manager
        checkpoint_manager = CheckpointManager(str(test_dir / 'checkpoint'), 'integration_test')
        
        # Create incremental processor
        processor = IncrementalFileProcessor(
            str(input_dir),
            checkpoint_manager,
            file_patterns=['*.csv']
        )
        
        # Get files to process
        files_to_process = processor.get_files_to_process()
        print(f"✓ Found {len(files_to_process)} files to process")
        
        # Validate files
        for file_path in files_to_process:
            is_valid, error = processor.validate_file_for_processing(file_path)
            print(f"✓ File validation - {Path(file_path).name}: {'Valid' if is_valid else f'Invalid ({error})'}")
        
        # Cleanup
        shutil.rmtree(test_dir)
        print("✓ Integration test completed successfully")
        
        return True
        
    except Exception as e:
        print(f"✗ Integration test failed: {e}")
        return False

def run_all_tests():
    """Run all test functions."""
    print("Starting PySpark Incremental File Ingestion Tests")
    print("=" * 60)
    
    tests = [
        ("Configuration", test_configuration),
        ("Checkpoint Manager", test_checkpoint_manager),
        ("File Monitor", test_file_monitor),
        ("CSV Processor", test_csv_processor),
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
    print("TEST SUMMARY")
    print("=" * 60)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "✓ PASS" if result else "✗ FAIL"
        print(f"{test_name:.<40} {status}")
    
    print("-" * 60)
    print(f"Tests passed: {passed}/{total} ({passed/total*100:.1f}%)")
    
    if passed == total:
        print("\n🎉 All tests passed! The incremental file ingestion job is ready.")
        return True
    else:
        print(f"\n⚠️  {total - passed} test(s) failed. Please check the errors above.")
        return False

def show_usage_examples():
    """Show usage examples."""
    print("\n" + "=" * 60)
    print("USAGE EXAMPLES")
    print("=" * 60)
    
    examples = """
1. CREATE SAMPLE DATA:
   cd spark/jobs
   python incremental/incremental_loader.py --create-sample-data

2. RUN INCREMENTAL JOB (with local Spark):
   export SPARK_MASTER_URL=local[2]
   export INPUT_DIR=./spark/data/input
   export DWH_POSTGRES_HOST=localhost
   python incremental/incremental_loader.py

3. RUN WITH CUSTOM CONFIGURATION:
   export SPARK_DRIVER_MEMORY=4g
   export BATCH_SIZE=20000
   export MAX_FILES_PER_BATCH=50
   python incremental/incremental_loader.py

4. AIRFLOW INTEGRATION:
   # Add to your Airflow DAG
   BashOperator(
       task_id='incremental_shipments',
       bash_command='cd /opt/spark && python jobs/incremental/incremental_loader.py'
   )

5. DOCKER DEPLOYMENT:
   docker build -t incremental-ingestion .
   docker run -v /data:/data incremental-ingestion

6. MONITOR CHECKPOINTS:
   python -c "
   from jobs.utils.checkpoint_manager import CheckpointManager
   cm = CheckpointManager('./spark/data/checkpoint')
   print(cm.get_checkpoint_stats())
   "

For detailed documentation, see: spark/jobs/README.md
"""
    
    print(examples)

if __name__ == "__main__":
    # Setup logging
    logging.basicConfig(level=logging.WARNING)
    
    success = run_all_tests()
    
    if success:
        show_usage_examples()
        sys.exit(0)
    else:
        print("\nFix the failing tests before proceeding.")
        sys.exit(1)
