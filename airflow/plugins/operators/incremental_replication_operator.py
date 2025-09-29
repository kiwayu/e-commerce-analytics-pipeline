"""
Airflow operator for incremental database replication using high-water mark strategy.
"""

import logging
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta

from airflow.models import BaseOperator
from airflow.utils.decorators import apply_defaults
from airflow.exceptions import AirflowException, AirflowSkipException
from airflow.utils.context import Context

from hooks.postgres_replication_hook import PostgreSQLReplicationHook

logger = logging.getLogger(__name__)


class IncrementalReplicationOperator(BaseOperator):
    """
    Airflow operator for incremental PostgreSQL table replication.
    
    Performs incremental replication from source to target PostgreSQL tables
    using high-water mark strategy with automatic watermark management.
    
    Features:
    - High-water mark based incremental extraction
    - Automatic watermark management via Airflow Variables
    - Configurable replication modes (insert, upsert)
    - Comprehensive error handling and monitoring
    - Data validation and quality checks
    """
    
    template_fields = [
        'source_table', 'target_table', 'watermark_column',
        'additional_filters', 'replication_mode'
    ]
    
    ui_color = '#4A90E2'
    ui_fgcolor = '#FFFFFF'
    
    @apply_defaults
    def __init__(
        self,
        source_table: str,
        target_table: str,
        source_conn_id: str = "postgres_source",
        target_conn_id: str = "postgres_dwh",
        watermark_column: str = "updated_at",
        primary_key_columns: Optional[List[str]] = None,
        replication_mode: str = "insert",
        batch_size: int = 10000,
        max_records_per_run: Optional[int] = None,
        additional_filters: Optional[str] = None,
        validate_before_replication: bool = True,
        skip_if_no_data: bool = True,
        watermark_lag_tolerance: Optional[timedelta] = None,
        quality_checks: Optional[Dict[str, Any]] = None,
        *args,
        **kwargs
    ):
        """
        Initialize incremental replication operator.
        
        Args:
            source_table: Source table name (schema.table format)
            target_table: Target table name (schema.table format)
            source_conn_id: Airflow connection ID for source database
            target_conn_id: Airflow connection ID for target database
            watermark_column: Column name for watermark (default: updated_at)
            primary_key_columns: List of primary key columns for upsert mode
            replication_mode: Replication mode ('insert' or 'upsert')
            batch_size: Number of records per batch for insertion
            max_records_per_run: Maximum records to process in single run
            additional_filters: Additional WHERE conditions for source query
            validate_before_replication: Whether to validate setup before replication
            skip_if_no_data: Whether to skip task if no new data found
            watermark_lag_tolerance: Maximum acceptable lag before raising error
            quality_checks: Dictionary of quality checks to perform
        """
        super().__init__(*args, **kwargs)
        
        self.source_table = source_table
        self.target_table = target_table
        self.source_conn_id = source_conn_id
        self.target_conn_id = target_conn_id
        self.watermark_column = watermark_column
        self.primary_key_columns = primary_key_columns or []
        self.replication_mode = replication_mode.lower()
        self.batch_size = batch_size
        self.max_records_per_run = max_records_per_run
        self.additional_filters = additional_filters
        self.validate_before_replication = validate_before_replication
        self.skip_if_no_data = skip_if_no_data
        self.watermark_lag_tolerance = watermark_lag_tolerance
        self.quality_checks = quality_checks or {}
        
        # Validate replication mode
        if self.replication_mode not in ['insert', 'upsert']:
            raise ValueError(f"Invalid replication_mode: {self.replication_mode}")
        
        # Validate upsert requirements
        if self.replication_mode == 'upsert' and not self.primary_key_columns:
            raise ValueError("primary_key_columns required for upsert mode")
    
    def execute(self, context: Context) -> Dict[str, Any]:
        """
        Execute incremental replication.
        
        Args:
            context: Airflow task context
            
        Returns:
            Dictionary with replication statistics
        """
        logger.info(f"Starting incremental replication: {self.source_table} -> {self.target_table}")
        
        # Initialize hook
        hook = PostgreSQLReplicationHook(
            source_conn_id=self.source_conn_id,
            target_conn_id=self.target_conn_id
        )
        
        # Store start time
        start_time = datetime.now()
        
        try:
            # Validation phase
            if self.validate_before_replication:
                self._validate_replication_setup(hook)
            
            # Get current watermark
            table_name = self.source_table.split('.')[-1]
            current_watermark = hook.get_watermark(table_name, self.watermark_column)
            
            logger.info(f"Current watermark: {current_watermark}")
            
            # Check for lag if tolerance is specified
            if self.watermark_lag_tolerance:
                self._check_watermark_lag(hook, current_watermark)
            
            # Extract incremental data
            df, record_count, new_watermark = hook.get_incremental_data(
                table_name=self.source_table,
                watermark_column=self.watermark_column,
                last_watermark=current_watermark,
                limit=self.max_records_per_run,
                additional_filters=self.additional_filters
            )
            
            # Handle no data case
            if record_count == 0:
                logger.info("No new data found for replication")
                
                if self.skip_if_no_data:
                    raise AirflowSkipException("No new data found, skipping task")
                
                return self._create_result_summary(
                    start_time=start_time,
                    records_extracted=0,
                    records_loaded=0,
                    watermark_updated=False,
                    current_watermark=current_watermark,
                    new_watermark=current_watermark
                )
            
            # Quality checks on extracted data
            if self.quality_checks:
                self._perform_quality_checks(df)
            
            # Load data to target
            if self.replication_mode == 'insert':
                records_loaded = hook.insert_data(
                    df=df,
                    target_table=self.target_table,
                    if_exists='append',
                    chunk_size=self.batch_size
                )
                upsert_stats = None
                
            elif self.replication_mode == 'upsert':
                upsert_stats = hook.upsert_data(
                    df=df,
                    target_table=self.target_table,
                    primary_key_columns=self.primary_key_columns,
                    chunk_size=self.batch_size
                )
                records_loaded = upsert_stats['inserted'] + upsert_stats['updated']
            
            # Update watermark
            if new_watermark and records_loaded > 0:
                hook.set_watermark(table_name, new_watermark, self.watermark_column)
                watermark_updated = True
            else:
                watermark_updated = False
            
            # Create execution summary
            result = self._create_result_summary(
                start_time=start_time,
                records_extracted=record_count,
                records_loaded=records_loaded,
                watermark_updated=watermark_updated,
                current_watermark=current_watermark,
                new_watermark=new_watermark,
                upsert_stats=upsert_stats
            )
            
            logger.info(f"Replication completed successfully: {result}")
            
            # Store result in XCom for downstream tasks
            context['task_instance'].xcom_push(key='replication_result', value=result)
            
            return result
            
        except AirflowSkipException:
            raise
            
        except Exception as e:
            logger.error(f"Replication failed: {e}")
            
            # Store error in XCom
            error_info = {
                'error': str(e),
                'task_id': self.task_id,
                'source_table': self.source_table,
                'target_table': self.target_table,
                'timestamp': datetime.now().isoformat()
            }
            context['task_instance'].xcom_push(key='replication_error', value=error_info)
            
            raise AirflowException(f"Incremental replication failed: {e}")
    
    def _validate_replication_setup(self, hook: PostgreSQLReplicationHook):
        """
        Validate replication setup before executing.
        
        Args:
            hook: Replication hook instance
        """
        logger.info("Validating replication setup...")
        
        validation_result = hook.validate_replication_setup(
            source_table=self.source_table,
            target_table=self.target_table,
            watermark_column=self.watermark_column
        )
        
        if not validation_result['is_valid']:
            errors = validation_result.get('errors', [])
            error_msg = f"Replication setup validation failed: {'; '.join(errors)}"
            logger.error(error_msg)
            raise AirflowException(error_msg)
        
        logger.info("Replication setup validation passed")
        logger.info(f"Source table rows: {validation_result.get('source_count', 0)}")
        logger.info(f"Target table rows: {validation_result.get('target_count', 0)}")
        
        if validation_result.get('watermark_range'):
            wr = validation_result['watermark_range']
            logger.info(f"Watermark range: {wr['min']} to {wr['max']}")
    
    def _check_watermark_lag(
        self, 
        hook: PostgreSQLReplicationHook, 
        current_watermark: Optional[datetime]
    ):
        """
        Check if watermark lag exceeds tolerance.
        
        Args:
            hook: Replication hook instance
            current_watermark: Current watermark value
        """
        if not current_watermark:
            return  # No watermark to check
        
        # Get max watermark from source
        max_source_watermark = hook.get_max_watermark_from_source(
            self.source_table, self.watermark_column
        )
        
        if not max_source_watermark:
            return  # No data in source
        
        # Calculate lag
        lag = max_source_watermark - current_watermark
        
        if lag > self.watermark_lag_tolerance:
            error_msg = (
                f"Watermark lag ({lag}) exceeds tolerance ({self.watermark_lag_tolerance}). "
                f"Current: {current_watermark}, Source max: {max_source_watermark}"
            )
            logger.error(error_msg)
            raise AirflowException(error_msg)
        
        logger.info(f"Watermark lag check passed: {lag}")
    
    def _perform_quality_checks(self, df):
        """
        Perform data quality checks on extracted data.
        
        Args:
            df: DataFrame to validate
        """
        logger.info("Performing data quality checks...")
        
        for check_name, check_config in self.quality_checks.items():
            try:
                if check_name == 'null_check':
                    self._check_null_values(df, check_config)
                elif check_name == 'duplicate_check':
                    self._check_duplicates(df, check_config)
                elif check_name == 'value_range_check':
                    self._check_value_ranges(df, check_config)
                elif check_name == 'record_count_check':
                    self._check_record_count(df, check_config)
                else:
                    logger.warning(f"Unknown quality check: {check_name}")
                    
            except Exception as e:
                error_msg = f"Quality check '{check_name}' failed: {e}"
                
                if check_config.get('fail_on_error', True):
                    logger.error(error_msg)
                    raise AirflowException(error_msg)
                else:
                    logger.warning(error_msg)
        
        logger.info("Data quality checks completed")
    
    def _check_null_values(self, df, config):
        """Check for null values in specified columns."""
        columns = config.get('columns', [])
        
        for column in columns:
            if column not in df.columns:
                continue
                
            null_count = df[column].isnull().sum()
            total_count = len(df)
            null_percentage = (null_count / total_count) * 100 if total_count > 0 else 0
            
            max_null_percentage = config.get('max_null_percentage', 0)
            
            if null_percentage > max_null_percentage:
                raise ValueError(
                    f"Column '{column}' has {null_percentage:.2f}% null values, "
                    f"exceeds limit of {max_null_percentage}%"
                )
    
    def _check_duplicates(self, df, config):
        """Check for duplicate records."""
        columns = config.get('columns', [])
        
        if not columns:
            return
        
        # Check if specified columns exist
        existing_columns = [col for col in columns if col in df.columns]
        
        if not existing_columns:
            return
        
        duplicate_count = df.duplicated(subset=existing_columns).sum()
        max_duplicates = config.get('max_duplicates', 0)
        
        if duplicate_count > max_duplicates:
            raise ValueError(
                f"Found {duplicate_count} duplicate records, "
                f"exceeds limit of {max_duplicates}"
            )
    
    def _check_value_ranges(self, df, config):
        """Check if values are within specified ranges."""
        for column, range_config in config.items():
            if column not in df.columns:
                continue
            
            min_value = range_config.get('min')
            max_value = range_config.get('max')
            
            if min_value is not None:
                invalid_count = (df[column] < min_value).sum()
                if invalid_count > 0:
                    raise ValueError(
                        f"Column '{column}' has {invalid_count} values below minimum {min_value}"
                    )
            
            if max_value is not None:
                invalid_count = (df[column] > max_value).sum()
                if invalid_count > 0:
                    raise ValueError(
                        f"Column '{column}' has {invalid_count} values above maximum {max_value}"
                    )
    
    def _check_record_count(self, df, config):
        """Check if record count is within expected range."""
        record_count = len(df)
        min_records = config.get('min_records', 0)
        max_records = config.get('max_records', float('inf'))
        
        if record_count < min_records:
            raise ValueError(
                f"Record count {record_count} is below minimum {min_records}"
            )
        
        if record_count > max_records:
            raise ValueError(
                f"Record count {record_count} exceeds maximum {max_records}"
            )
    
    def _create_result_summary(
        self,
        start_time: datetime,
        records_extracted: int,
        records_loaded: int,
        watermark_updated: bool,
        current_watermark: Optional[datetime],
        new_watermark: Optional[datetime],
        upsert_stats: Optional[Dict[str, int]] = None
    ) -> Dict[str, Any]:
        """
        Create execution result summary.
        
        Args:
            start_time: Execution start time
            records_extracted: Number of records extracted
            records_loaded: Number of records loaded
            watermark_updated: Whether watermark was updated
            current_watermark: Previous watermark value
            new_watermark: New watermark value
            upsert_stats: Upsert statistics if applicable
            
        Returns:
            Dictionary with execution summary
        """
        end_time = datetime.now()
        duration = (end_time - start_time).total_seconds()
        
        result = {
            'task_id': self.task_id,
            'source_table': self.source_table,
            'target_table': self.target_table,
            'replication_mode': self.replication_mode,
            'start_time': start_time.isoformat(),
            'end_time': end_time.isoformat(),
            'duration_seconds': duration,
            'records_extracted': records_extracted,
            'records_loaded': records_loaded,
            'watermark_updated': watermark_updated,
            'previous_watermark': current_watermark.isoformat() if current_watermark else None,
            'new_watermark': new_watermark.isoformat() if new_watermark else None,
            'success': True
        }
        
        # Add upsert statistics if available
        if upsert_stats:
            result['upsert_stats'] = upsert_stats
        
        # Calculate throughput
        if duration > 0:
            result['records_per_second'] = records_loaded / duration
        else:
            result['records_per_second'] = 0
        
        return result


class ReplicationValidationOperator(BaseOperator):
    """
    Operator for validating replication setup and monitoring replication health.
    """
    
    template_fields = ['source_table', 'target_table']
    ui_color = '#FF9500'
    ui_fgcolor = '#FFFFFF'
    
    @apply_defaults
    def __init__(
        self,
        source_table: str,
        target_table: str,
        source_conn_id: str = "postgres_source",
        target_conn_id: str = "postgres_dwh",
        watermark_column: str = "updated_at",
        max_lag_hours: Optional[float] = None,
        *args,
        **kwargs
    ):
        """
        Initialize replication validation operator.
        
        Args:
            source_table: Source table name
            target_table: Target table name
            source_conn_id: Source connection ID
            target_conn_id: Target connection ID
            watermark_column: Watermark column name
            max_lag_hours: Maximum acceptable lag in hours
        """
        super().__init__(*args, **kwargs)
        
        self.source_table = source_table
        self.target_table = target_table
        self.source_conn_id = source_conn_id
        self.target_conn_id = target_conn_id
        self.watermark_column = watermark_column
        self.max_lag_hours = max_lag_hours
    
    def execute(self, context: Context) -> Dict[str, Any]:
        """
        Execute replication validation.
        
        Args:
            context: Airflow task context
            
        Returns:
            Dictionary with validation results
        """
        logger.info(f"Validating replication for {self.source_table} -> {self.target_table}")
        
        hook = PostgreSQLReplicationHook(
            source_conn_id=self.source_conn_id,
            target_conn_id=self.target_conn_id
        )
        
        try:
            # Get replication statistics
            stats = hook.get_replication_stats(
                source_table=self.source_table,
                target_table=self.target_table,
                watermark_column=self.watermark_column
            )
            
            # Validate lag if specified
            if self.max_lag_hours and stats.get('lag_seconds'):
                max_lag_seconds = self.max_lag_hours * 3600
                
                if stats['lag_seconds'] > max_lag_seconds:
                    raise AirflowException(
                        f"Replication lag ({stats['lag_seconds']/3600:.2f} hours) "
                        f"exceeds maximum ({self.max_lag_hours} hours)"
                    )
            
            # Add validation timestamp
            stats['validation_timestamp'] = datetime.now().isoformat()
            stats['validation_passed'] = True
            
            logger.info(f"Replication validation passed: {stats}")
            
            return stats
            
        except Exception as e:
            logger.error(f"Replication validation failed: {e}")
            raise AirflowException(f"Replication validation failed: {e}")
