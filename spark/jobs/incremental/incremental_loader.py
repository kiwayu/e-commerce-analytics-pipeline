"""
PySpark incremental file ingestion job for loading CSV files into raw_shipments table.
"""

import os
import sys
import logging
import uuid
from datetime import datetime, timezone
from typing import Dict, Any, List, Optional
from pathlib import Path

# Add project root to path for imports
project_root = Path(__file__).parent.parent.parent
sys.path.append(str(project_root))

from pyspark.sql import SparkSession, DataFrame
from pyspark.sql.functions import col, lit

from jobs.config.spark_config import SparkJobConfig, SparkSessionManager, get_database_properties
from jobs.utils.checkpoint_manager import CheckpointManager
from jobs.utils.file_monitor import IncrementalFileProcessor
from jobs.utils.csv_processor import CSVProcessor

logger = logging.getLogger(__name__)


class IncrementalFileLoader:
    """
    Main class for incremental file loading with PySpark.
    
    Handles the complete pipeline:
    1. File discovery and change detection
    2. CSV processing and validation
    3. Data loading to PostgreSQL
    4. Checkpoint management
    5. Error handling and recovery
    """
    
    def __init__(self, config: Optional[SparkJobConfig] = None):
        """
        Initialize the incremental file loader.
        
        Args:
            config: Optional Spark job configuration
        """
        self.config = config or SparkJobConfig.from_environment()
        self.batch_id = str(uuid.uuid4())
        
        # Initialize components
        self.session_manager = SparkSessionManager(self.config)
        self.checkpoint_manager = CheckpointManager(
            self.config.checkpoint_dir,
            job_name="incremental_shipments"
        )
        
        # Statistics tracking
        self.job_stats = {
            'batch_id': self.batch_id,
            'start_time': datetime.now(timezone.utc).isoformat(),
            'end_time': None,
            'files_processed': 0,
            'files_failed': 0,
            'total_records_read': 0,
            'total_records_written': 0,
            'validation_errors': [],
            'processing_errors': []
        }
        
        # Ensure directories exist
        self._ensure_directories()
    
    def _ensure_directories(self):
        """Ensure required directories exist."""
        directories = [
            self.config.input_dir,
            self.config.processed_dir,
            self.config.archive_dir,
            self.config.checkpoint_dir
        ]
        
        for directory in directories:
            Path(directory).mkdir(parents=True, exist_ok=True)
            logger.debug(f"Ensured directory exists: {directory}")
    
    def run(self) -> Dict[str, Any]:
        """
        Run the complete incremental file loading process.
        
        Returns:
            Dictionary containing job execution statistics
        """
        logger.info(f"Starting incremental file loading job (batch_id: {self.batch_id})")
        
        try:
            # Create Spark session
            spark = self.session_manager.create_session()
            
            # Initialize file processor
            file_processor = IncrementalFileProcessor(
                input_directory=self.config.input_dir,
                checkpoint_manager=self.checkpoint_manager,
                file_patterns=['*.csv'],
                processing_config={
                    'max_files_per_batch': self.config.max_files_per_batch,
                    'priority_mode': 'oldest_first'
                }
            )
            
            # Get files to process
            files_to_process = file_processor.get_files_to_process()
            
            if not files_to_process:
                logger.info("No files to process")
                return self._finalize_stats()
            
            logger.info(f"Found {len(files_to_process)} files to process")
            
            # Process each file
            csv_processor = CSVProcessor(spark)
            
            for file_path in files_to_process:
                try:
                    self._process_single_file(file_path, csv_processor, spark)
                except Exception as e:
                    logger.error(f"Failed to process file {file_path}: {e}")
                    self.job_stats['files_failed'] += 1
                    self.job_stats['processing_errors'].append({
                        'file_path': file_path,
                        'error': str(e)
                    })
                    
                    # Mark file as failed in checkpoint
                    self.checkpoint_manager.mark_file_failed(
                        file_path, str(e), self.batch_id
                    )
            
            # Cleanup old checkpoints
            self.checkpoint_manager.cleanup_old_checkpoints(
                self.config.file_retention_days
            )
            
            return self._finalize_stats()
            
        except Exception as e:
            logger.error(f"Job failed: {e}")
            self.job_stats['processing_errors'].append({
                'error': f"Job-level error: {str(e)}"
            })
            return self._finalize_stats()
        
        finally:
            # Clean up Spark session
            self.session_manager.stop_session()
    
    def _process_single_file(
        self,
        file_path: str,
        csv_processor: CSVProcessor,
        spark: SparkSession
    ):
        """
        Process a single CSV file.
        
        Args:
            file_path: Path to the file to process
            csv_processor: CSV processor instance
            spark: Spark session
        """
        logger.info(f"Processing file: {file_path}")
        
        # Mark file as processing in checkpoint
        self.checkpoint_manager.mark_file_processing(file_path, self.batch_id)
        
        try:
            # Validate file before processing
            file_processor = IncrementalFileProcessor(
                self.config.input_dir,
                self.checkpoint_manager
            )
            
            is_valid, error_msg = file_processor.validate_file_for_processing(file_path)
            if not is_valid:
                raise ValueError(f"File validation failed: {error_msg}")
            
            # Read CSV with fallback schema handling
            df, warnings = csv_processor.read_csv_with_fallback(
                file_path,
                primary_schema=csv_processor.schema_manager.get_shipments_schema(),
                fallback_to_flexible=True
            )
            
            if warnings:
                self.job_stats['validation_errors'].extend([
                    {'file_path': file_path, 'warning': warning}
                    for warning in warnings
                ])
            
            original_count = df.count()
            self.job_stats['total_records_read'] += original_count
            
            logger.info(f"Read {original_count} records from {file_path}")
            
            # Validate and clean data
            cleaned_df, validation_stats = csv_processor.validate_shipments_data(df)
            
            # Add metadata columns
            enhanced_df = csv_processor.add_metadata_columns(
                cleaned_df,
                file_path=file_path,
                batch_id=self.batch_id,
                source_system="csv_file_ingestion"
            )
            
            # Convert to target schema
            target_df = csv_processor.convert_to_target_schema(enhanced_df)
            
            # Filter only valid records for writing
            valid_df = target_df.filter(col('is_valid') == True)
            valid_count = valid_df.count()
            
            if valid_count == 0:
                logger.warning(f"No valid records found in {file_path}")
                self.checkpoint_manager.mark_file_processed(file_path, 0, self.batch_id)
                return
            
            # Write to database
            self._write_to_database(valid_df, spark)
            
            self.job_stats['total_records_written'] += valid_count
            self.job_stats['files_processed'] += 1
            
            # Mark file as successfully processed
            self.checkpoint_manager.mark_file_processed(
                file_path, valid_count, self.batch_id
            )
            
            # Move file to processed directory (optional)
            self._archive_processed_file(file_path)
            
            # Log processing summary
            summary = csv_processor.get_processing_summary(
                original_count, valid_count, validation_stats, file_path
            )
            
            logger.info(
                f"Successfully processed {file_path}: "
                f"{summary['processed_rows']}/{summary['original_rows']} records "
                f"({summary['processing_rate']:.2%} success rate)"
            )
            
        except Exception as e:
            logger.error(f"Error processing file {file_path}: {e}")
            raise
    
    def _write_to_database(self, df: DataFrame, spark: SparkSession):
        """
        Write DataFrame to PostgreSQL raw_shipments table.
        
        Args:
            df: DataFrame to write
            spark: Spark session
        """
        logger.info("Writing data to PostgreSQL...")
        
        try:
            # Get database properties
            db_properties = get_database_properties(self.config)
            
            # Write to PostgreSQL
            df.write \
                .format("jdbc") \
                .option("url", self.config.postgres_url) \
                .option("dbtable", "raw.raw_shipments") \
                .option("user", self.config.postgres_user) \
                .option("password", self.config.postgres_password) \
                .option("driver", self.config.postgres_driver) \
                .option("batchsize", str(self.config.batch_size)) \
                .option("isolationLevel", "READ_COMMITTED") \
                .option("stringtype", "unspecified") \
                .mode("append") \
                .save()
            
            logger.info(f"Successfully wrote {df.count()} records to raw_shipments")
            
        except Exception as e:
            logger.error(f"Error writing to database: {e}")
            raise
    
    def _archive_processed_file(self, file_path: str):
        """
        Move processed file to archive directory.
        
        Args:
            file_path: Path to the processed file
        """
        try:
            source_path = Path(file_path)
            if not source_path.exists():
                logger.warning(f"File no longer exists for archiving: {file_path}")
                return
            
            # Create archive path with timestamp
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            archive_filename = f"{timestamp}_{source_path.name}"
            archive_path = Path(self.config.archive_dir) / archive_filename
            
            # Move file to archive
            source_path.rename(archive_path)
            logger.debug(f"Archived file: {file_path} -> {archive_path}")
            
        except Exception as e:
            logger.warning(f"Could not archive file {file_path}: {e}")
            # Don't fail the job if archiving fails
    
    def _finalize_stats(self) -> Dict[str, Any]:
        """Finalize and return job statistics."""
        self.job_stats['end_time'] = datetime.now(timezone.utc).isoformat()
        
        # Calculate duration
        start_time = datetime.fromisoformat(self.job_stats['start_time'].replace('Z', '+00:00'))
        end_time = datetime.fromisoformat(self.job_stats['end_time'].replace('Z', '+00:00'))
        duration = (end_time - start_time).total_seconds()
        
        self.job_stats['duration_seconds'] = duration
        self.job_stats['success'] = self.job_stats['files_failed'] == 0
        
        # Add checkpoint statistics
        checkpoint_stats = self.checkpoint_manager.get_checkpoint_stats()
        self.job_stats['checkpoint_stats'] = checkpoint_stats
        
        # Calculate rates
        total_files = self.job_stats['files_processed'] + self.job_stats['files_failed']
        if total_files > 0:
            self.job_stats['file_success_rate'] = self.job_stats['files_processed'] / total_files
        else:
            self.job_stats['file_success_rate'] = 1.0
        
        if self.job_stats['total_records_read'] > 0:
            self.job_stats['record_success_rate'] = (
                self.job_stats['total_records_written'] / 
                self.job_stats['total_records_read']
            )
        else:
            self.job_stats['record_success_rate'] = 1.0
        
        return self.job_stats


def create_sample_data():
    """Create sample CSV files for testing."""
    import csv
    import random
    from datetime import datetime, timedelta
    
    # Create input directory
    input_dir = Path("./spark/data/input")
    input_dir.mkdir(parents=True, exist_ok=True)
    
    # Sample data for shipments
    sample_data = []
    
    carriers = ['UPS', 'FedEx', 'DHL', 'USPS', 'Amazon Logistics']
    statuses = ['pending', 'shipped', 'in_transit', 'delivered', 'exception']
    countries = ['US', 'CA', 'GB', 'DE', 'FR']
    
    for i in range(1000):
        shipped_date = datetime.now() - timedelta(days=random.randint(0, 30))
        delivery_date = shipped_date + timedelta(days=random.randint(1, 7))
        
        record = {
            'shipment_id': f'SHP-{i+1:06d}',
            'order_id': f'ORD-{random.randint(1, 500):06d}',
            'tracking_number': f'1Z{random.randint(100000000000, 999999999999)}',
            'carrier': random.choice(carriers),
            'shipping_method': random.choice(['Standard', 'Express', 'Overnight', 'Ground']),
            'shipment_status': random.choice(statuses),
            'shipped_date': shipped_date.strftime('%Y-%m-%d %H:%M:%S'),
            'estimated_delivery_date': delivery_date.strftime('%Y-%m-%d'),
            'actual_delivery_date': delivery_date.strftime('%Y-%m-%d') if random.random() > 0.3 else '',
            'package_count': random.randint(1, 5),
            'total_weight': round(random.uniform(0.5, 25.0), 2),
            'weight_unit': 'kg',
            'shipping_cost': round(random.uniform(5.0, 50.0), 2),
            'currency': 'USD',
            'destination_street': f'{random.randint(1, 999)} Main St',
            'destination_city': f'City{random.randint(1, 100)}',
            'destination_state': f'ST{random.randint(1, 50)}',
            'destination_postal_code': f'{random.randint(10000, 99999)}',
            'destination_country': random.choice(countries),
            'signature_required': random.choice(['true', 'false']),
            'is_return': random.choice(['false', 'false', 'false', 'true'])  # 25% returns
        }
        sample_data.append(record)
    
    # Write to CSV files (split into multiple files)
    files_to_create = 3
    records_per_file = len(sample_data) // files_to_create
    
    for file_num in range(files_to_create):
        start_idx = file_num * records_per_file
        end_idx = start_idx + records_per_file if file_num < files_to_create - 1 else len(sample_data)
        
        file_data = sample_data[start_idx:end_idx]
        filename = input_dir / f"shipments_{file_num + 1:02d}.csv"
        
        with open(filename, 'w', newline='') as csvfile:
            if file_data:
                writer = csv.DictWriter(csvfile, fieldnames=file_data[0].keys())
                writer.writeheader()
                writer.writerows(file_data)
        
        print(f"Created sample file: {filename} ({len(file_data)} records)")


def main():
    """Main entry point for the incremental file loader."""
    
    # Setup logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(),
            logging.FileHandler('incremental_loader.log')
        ]
    )
    
    logger.info("Starting incremental file loading job")
    
    try:
        # Check if sample data should be created
        if '--create-sample-data' in sys.argv:
            logger.info("Creating sample data...")
            create_sample_data()
            logger.info("Sample data created successfully")
            return
        
        # Create and run the loader
        config = SparkJobConfig.from_environment()
        loader = IncrementalFileLoader(config)
        
        # Run the job
        stats = loader.run()
        
        # Print summary
        print("\n" + "="*60)
        print("INCREMENTAL FILE LOADING SUMMARY")
        print("="*60)
        print(f"Batch ID: {stats['batch_id']}")
        print(f"Duration: {stats.get('duration_seconds', 0):.2f} seconds")
        print(f"Files Processed: {stats['files_processed']}")
        print(f"Files Failed: {stats['files_failed']}")
        print(f"Records Read: {stats['total_records_read']}")
        print(f"Records Written: {stats['total_records_written']}")
        print(f"File Success Rate: {stats.get('file_success_rate', 0):.2%}")
        print(f"Record Success Rate: {stats.get('record_success_rate', 0):.2%}")
        print(f"Overall Success: {'✓' if stats['success'] else '✗'}")
        
        if stats['processing_errors']:
            print(f"\nErrors ({len(stats['processing_errors'])}):")
            for error in stats['processing_errors']:
                print(f"  - {error}")
        
        if stats['validation_errors']:
            print(f"\nValidation Warnings ({len(stats['validation_errors'])}):")
            for warning in stats['validation_errors'][:5]:  # Show first 5
                print(f"  - {warning}")
            if len(stats['validation_errors']) > 5:
                print(f"  ... and {len(stats['validation_errors']) - 5} more")
        
        print("="*60)
        
        # Exit with appropriate code
        exit_code = 0 if stats['success'] else 1
        sys.exit(exit_code)
        
    except Exception as e:
        logger.error(f"Job failed with exception: {e}")
        print(f"Job failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
