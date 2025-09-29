"""
Utility functions for database replication operations.
"""

import logging
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime, timedelta
import pandas as pd

from airflow.models import Variable
from airflow.exceptions import AirflowException

logger = logging.getLogger(__name__)


class WatermarkManager:
    """
    Centralized watermark management for replication processes.
    """
    
    @staticmethod
    def get_watermark_variable_key(table_name: str, column_name: str) -> str:
        """
        Generate standardized watermark variable key.
        
        Args:
            table_name: Table name (without schema)
            column_name: Watermark column name
            
        Returns:
            Standardized variable key
        """
        # Remove schema prefix if present
        clean_table_name = table_name.split('.')[-1]
        return f"replication_watermark_{clean_table_name}_{column_name}"
    
    @staticmethod
    def get_watermark(table_name: str, column_name: str = "updated_at") -> Optional[datetime]:
        """
        Get watermark from Airflow Variables with error handling.
        
        Args:
            table_name: Table name
            column_name: Watermark column name
            
        Returns:
            Watermark datetime or None if not found
        """
        variable_key = WatermarkManager.get_watermark_variable_key(table_name, column_name)
        
        try:
            watermark_str = Variable.get(variable_key, default_var=None)
            
            if watermark_str is None:
                logger.info(f"No existing watermark found for {table_name}.{column_name}")
                return None
            
            # Parse ISO format timestamp
            watermark = datetime.fromisoformat(watermark_str.replace('Z', '+00:00'))
            logger.info(f"Retrieved watermark for {table_name}.{column_name}: {watermark}")
            
            return watermark
            
        except Exception as e:
            logger.error(f"Error retrieving watermark for {table_name}: {e}")
            return None
    
    @staticmethod
    def set_watermark(table_name: str, watermark_value: datetime, column_name: str = "updated_at") -> bool:
        """
        Set watermark in Airflow Variables with error handling.
        
        Args:
            table_name: Table name
            watermark_value: Watermark value to set
            column_name: Watermark column name
            
        Returns:
            True if successful, False otherwise
        """
        variable_key = WatermarkManager.get_watermark_variable_key(table_name, column_name)
        
        try:
            # Ensure timezone awareness
            if watermark_value.tzinfo is None:
                watermark_value = watermark_value.replace(tzinfo=datetime.now().astimezone().tzinfo)
            
            watermark_str = watermark_value.isoformat()
            Variable.set(variable_key, watermark_str)
            
            logger.info(f"Set watermark for {table_name}.{column_name}: {watermark_str}")
            return True
            
        except Exception as e:
            logger.error(f"Error setting watermark for {table_name}: {e}")
            return False
    
    @staticmethod
    def backup_watermark(table_name: str, column_name: str = "updated_at") -> bool:
        """
        Create backup of current watermark.
        
        Args:
            table_name: Table name
            column_name: Watermark column name
            
        Returns:
            True if backup created successfully
        """
        try:
            current_watermark = WatermarkManager.get_watermark(table_name, column_name)
            
            if current_watermark is None:
                logger.info(f"No watermark to backup for {table_name}.{column_name}")
                return True
            
            backup_key = f"backup_{WatermarkManager.get_watermark_variable_key(table_name, column_name)}"
            backup_value = {
                'watermark': current_watermark.isoformat(),
                'backup_timestamp': datetime.now().isoformat(),
                'table_name': table_name,
                'column_name': column_name
            }
            
            Variable.set(backup_key, str(backup_value))
            logger.info(f"Backed up watermark for {table_name}.{column_name}")
            
            return True
            
        except Exception as e:
            logger.error(f"Error backing up watermark for {table_name}: {e}")
            return False
    
    @staticmethod
    def restore_watermark(table_name: str, column_name: str = "updated_at") -> bool:
        """
        Restore watermark from backup.
        
        Args:
            table_name: Table name
            column_name: Watermark column name
            
        Returns:
            True if restore successful
        """
        try:
            backup_key = f"backup_{WatermarkManager.get_watermark_variable_key(table_name, column_name)}"
            backup_str = Variable.get(backup_key, default_var=None)
            
            if backup_str is None:
                logger.error(f"No backup found for {table_name}.{column_name}")
                return False
            
            backup_data = eval(backup_str)  # In production, use json.loads
            watermark_str = backup_data['watermark']
            watermark = datetime.fromisoformat(watermark_str)
            
            return WatermarkManager.set_watermark(table_name, watermark, column_name)
            
        except Exception as e:
            logger.error(f"Error restoring watermark for {table_name}: {e}")
            return False
    
    @staticmethod
    def list_all_watermarks() -> Dict[str, Dict[str, Any]]:
        """
        List all replication watermarks.
        
        Returns:
            Dictionary of all watermarks with metadata
        """
        try:
            # Get all variables with replication_watermark prefix
            all_variables = Variable.get_all()
            watermarks = {}
            
            for key, value in all_variables.items():
                if key.startswith('replication_watermark_'):
                    try:
                        parts = key.replace('replication_watermark_', '').split('_')
                        table_name = '_'.join(parts[:-1])
                        column_name = parts[-1]
                        
                        watermark = datetime.fromisoformat(value.replace('Z', '+00:00'))
                        
                        watermarks[key] = {
                            'table_name': table_name,
                            'column_name': column_name,
                            'watermark': watermark,
                            'watermark_str': value,
                            'age_hours': (datetime.now() - watermark.replace(tzinfo=None)).total_seconds() / 3600
                        }
                        
                    except Exception as e:
                        logger.warning(f"Error parsing watermark {key}: {e}")
                        continue
            
            return watermarks
            
        except Exception as e:
            logger.error(f"Error listing watermarks: {e}")
            return {}


class ReplicationMetrics:
    """
    Collect and manage replication metrics.
    """
    
    @staticmethod
    def calculate_replication_lag(
        source_max_watermark: datetime,
        current_watermark: Optional[datetime]
    ) -> Dict[str, Any]:
        """
        Calculate replication lag metrics.
        
        Args:
            source_max_watermark: Maximum watermark in source
            current_watermark: Current processed watermark
            
        Returns:
            Dictionary with lag metrics
        """
        if current_watermark is None:
            return {
                'lag_seconds': None,
                'lag_hours': None,
                'lag_days': None,
                'status': 'no_watermark'
            }
        
        # Ensure both timestamps are timezone-aware for comparison
        if source_max_watermark.tzinfo is None:
            source_max_watermark = source_max_watermark.replace(tzinfo=datetime.now().astimezone().tzinfo)
        
        if current_watermark.tzinfo is None:
            current_watermark = current_watermark.replace(tzinfo=datetime.now().astimezone().tzinfo)
        
        lag_timedelta = source_max_watermark - current_watermark
        lag_seconds = max(0, lag_timedelta.total_seconds())
        
        return {
            'lag_seconds': lag_seconds,
            'lag_hours': lag_seconds / 3600,
            'lag_days': lag_seconds / 86400,
            'lag_timedelta': str(lag_timedelta),
            'status': 'lagging' if lag_seconds > 3600 else 'current',
            'source_max_watermark': source_max_watermark.isoformat(),
            'current_watermark': current_watermark.isoformat()
        }
    
    @staticmethod
    def calculate_throughput_metrics(
        records_processed: int,
        duration_seconds: float,
        data_size_mb: Optional[float] = None
    ) -> Dict[str, Any]:
        """
        Calculate throughput metrics for replication.
        
        Args:
            records_processed: Number of records processed
            duration_seconds: Processing duration in seconds
            data_size_mb: Optional data size in MB
            
        Returns:
            Dictionary with throughput metrics
        """
        if duration_seconds <= 0:
            return {
                'records_per_second': 0,
                'records_per_minute': 0,
                'records_per_hour': 0,
                'mb_per_second': 0,
                'duration_seconds': duration_seconds
            }
        
        records_per_second = records_processed / duration_seconds
        
        metrics = {
            'records_per_second': round(records_per_second, 2),
            'records_per_minute': round(records_per_second * 60, 2),
            'records_per_hour': round(records_per_second * 3600, 2),
            'duration_seconds': round(duration_seconds, 2),
            'total_records': records_processed
        }
        
        if data_size_mb is not None:
            metrics['mb_per_second'] = round(data_size_mb / duration_seconds, 2)
            metrics['total_size_mb'] = data_size_mb
        
        return metrics


class DataQualityValidator:
    """
    Data quality validation utilities for replication.
    """
    
    @staticmethod
    def validate_data_consistency(
        source_df: pd.DataFrame,
        target_df: pd.DataFrame,
        key_columns: List[str]
    ) -> Dict[str, Any]:
        """
        Validate data consistency between source and target.
        
        Args:
            source_df: Source DataFrame
            target_df: Target DataFrame
            key_columns: Key columns for comparison
            
        Returns:
            Dictionary with validation results
        """
        try:
            validation_results = {
                'source_count': len(source_df),
                'target_count': len(target_df),
                'consistency_check_passed': True,
                'issues': []
            }
            
            # Check if key columns exist
            missing_source_cols = [col for col in key_columns if col not in source_df.columns]
            missing_target_cols = [col for col in key_columns if col not in target_df.columns]
            
            if missing_source_cols:
                validation_results['issues'].append(f"Missing columns in source: {missing_source_cols}")
                validation_results['consistency_check_passed'] = False
            
            if missing_target_cols:
                validation_results['issues'].append(f"Missing columns in target: {missing_target_cols}")
                validation_results['consistency_check_passed'] = False
            
            if not validation_results['consistency_check_passed']:
                return validation_results
            
            # Check for missing records in target
            source_keys = set(source_df[key_columns].apply(tuple, axis=1))
            target_keys = set(target_df[key_columns].apply(tuple, axis=1))
            
            missing_in_target = source_keys - target_keys
            extra_in_target = target_keys - source_keys
            
            if missing_in_target:
                validation_results['issues'].append(f"Records missing in target: {len(missing_in_target)}")
                validation_results['consistency_check_passed'] = False
            
            if extra_in_target:
                validation_results['issues'].append(f"Extra records in target: {len(extra_in_target)}")
                # This might be expected in incremental scenarios
            
            validation_results['missing_in_target_count'] = len(missing_in_target)
            validation_results['extra_in_target_count'] = len(extra_in_target)
            validation_results['matching_records'] = len(source_keys & target_keys)
            
            return validation_results
            
        except Exception as e:
            return {
                'consistency_check_passed': False,
                'error': str(e),
                'issues': [f"Validation error: {e}"]
            }
    
    @staticmethod
    def validate_data_types(df: pd.DataFrame, expected_types: Dict[str, str]) -> Dict[str, Any]:
        """
        Validate data types in DataFrame.
        
        Args:
            df: DataFrame to validate
            expected_types: Dictionary of column -> expected type
            
        Returns:
            Dictionary with validation results
        """
        validation_results = {
            'type_check_passed': True,
            'type_issues': []
        }
        
        for column, expected_type in expected_types.items():
            if column not in df.columns:
                validation_results['type_issues'].append(f"Column {column} not found")
                validation_results['type_check_passed'] = False
                continue
            
            actual_type = str(df[column].dtype)
            
            # Simple type mapping
            type_mapping = {
                'string': ['object', 'string'],
                'integer': ['int64', 'int32', 'int'],
                'float': ['float64', 'float32', 'float'],
                'datetime': ['datetime64[ns]', 'datetime'],
                'boolean': ['bool', 'boolean']
            }
            
            expected_types_list = type_mapping.get(expected_type, [expected_type])
            
            if actual_type not in expected_types_list:
                validation_results['type_issues'].append(
                    f"Column {column}: expected {expected_type}, got {actual_type}"
                )
                validation_results['type_check_passed'] = False
        
        return validation_results
    
    @staticmethod
    def validate_business_rules(df: pd.DataFrame, rules: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validate business rules on DataFrame.
        
        Args:
            df: DataFrame to validate
            rules: Dictionary of business rules
            
        Returns:
            Dictionary with validation results
        """
        validation_results = {
            'business_rules_passed': True,
            'rule_violations': []
        }
        
        for rule_name, rule_config in rules.items():
            try:
                if rule_name == 'email_format':
                    column = rule_config['column']
                    if column in df.columns:
                        # Simple email validation
                        invalid_emails = df[~df[column].str.contains('@', na=False)]
                        if len(invalid_emails) > 0:
                            validation_results['rule_violations'].append(
                                f"Invalid email format in {column}: {len(invalid_emails)} records"
                            )
                            validation_results['business_rules_passed'] = False
                
                elif rule_name == 'date_range':
                    column = rule_config['column']
                    min_date = rule_config.get('min_date')
                    max_date = rule_config.get('max_date')
                    
                    if column in df.columns:
                        if min_date:
                            invalid_min = df[df[column] < min_date]
                            if len(invalid_min) > 0:
                                validation_results['rule_violations'].append(
                                    f"Dates before {min_date} in {column}: {len(invalid_min)} records"
                                )
                                validation_results['business_rules_passed'] = False
                        
                        if max_date:
                            invalid_max = df[df[column] > max_date]
                            if len(invalid_max) > 0:
                                validation_results['rule_violations'].append(
                                    f"Dates after {max_date} in {column}: {len(invalid_max)} records"
                                )
                                validation_results['business_rules_passed'] = False
                
                elif rule_name == 'referential_integrity':
                    # Check if referenced values exist
                    child_column = rule_config['child_column']
                    parent_values = set(rule_config['parent_values'])
                    
                    if child_column in df.columns:
                        invalid_refs = df[~df[child_column].isin(parent_values)]
                        if len(invalid_refs) > 0:
                            validation_results['rule_violations'].append(
                                f"Invalid references in {child_column}: {len(invalid_refs)} records"
                            )
                            validation_results['business_rules_passed'] = False
                
            except Exception as e:
                validation_results['rule_violations'].append(f"Error validating rule {rule_name}: {e}")
                validation_results['business_rules_passed'] = False
        
        return validation_results


def create_replication_summary(
    task_id: str,
    source_table: str,
    target_table: str,
    replication_stats: Dict[str, Any],
    validation_results: Optional[Dict[str, Any]] = None
) -> str:
    """
    Create formatted replication summary for notifications.
    
    Args:
        task_id: Airflow task ID
        source_table: Source table name
        target_table: Target table name
        replication_stats: Replication statistics
        validation_results: Optional validation results
        
    Returns:
        Formatted summary string
    """
    summary = f"""
📊 REPLICATION SUMMARY
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

🔄 Task: {task_id}
📋 Source: {source_table}
📋 Target: {target_table}

📈 STATISTICS:
   • Records Extracted: {replication_stats.get('records_extracted', 0):,}
   • Records Loaded: {replication_stats.get('records_loaded', 0):,}
   • Duration: {replication_stats.get('duration_seconds', 0):.2f} seconds
   • Throughput: {replication_stats.get('records_per_second', 0):.2f} records/sec
   • Success Rate: {replication_stats.get('success', False)}

💧 WATERMARK:
   • Previous: {replication_stats.get('previous_watermark', 'None')}
   • New: {replication_stats.get('new_watermark', 'None')}
   • Updated: {replication_stats.get('watermark_updated', False)}
"""
    
    if validation_results:
        summary += f"""
✅ VALIDATION:
   • Data Quality: {'PASSED' if validation_results.get('validation_passed', False) else 'FAILED'}
   • Issues: {len(validation_results.get('issues', []))}
"""
        
        if validation_results.get('issues'):
            summary += "   • Details: " + "; ".join(validation_results['issues'][:3])
    
    summary += "\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    
    return summary
