"""
Custom sensors for monitoring data availability and pipeline prerequisites.
"""

import logging
from datetime import datetime, timedelta
from typing import Dict, Any, Optional

from airflow.sdk.bases.sensor import BaseSensorOperator
from airflow.sdk import Context
from airflow.exceptions import AirflowException
from airflow.providers.postgres.hooks.postgres import PostgresHook

logger = logging.getLogger(__name__)


class DataAvailabilitySensor(BaseSensorOperator):
    """
    Sensor that checks for data availability before starting ETL pipeline.
    
    Monitors source systems for new data based on configurable criteria
    such as row counts, timestamps, or file presence.
    """
    
    template_fields = ['sql_query', 'target_date']
    
    def __init__(
        self,
        sql_query: str,
        postgres_conn_id: str = 'postgres_source',
        target_date: Optional[str] = None,
        min_row_count: int = 1,
        max_age_hours: int = 25,  # Data should be less than 25 hours old
        **kwargs
    ):
        """
        Initialize data availability sensor.
        
        Args:
            sql_query: SQL query to check data availability
            postgres_conn_id: Airflow connection ID for source database
            target_date: Date to check for data (defaults to yesterday)
            min_row_count: Minimum number of rows expected
            max_age_hours: Maximum age of data in hours
        """
        super().__init__(**kwargs)
        self.sql_query = sql_query
        self.postgres_conn_id = postgres_conn_id
        self.target_date = target_date
        self.min_row_count = min_row_count
        self.max_age_hours = max_age_hours
    
    def poke(self, context: Context) -> bool:
        """
        Check if data is available and meets criteria.
        
        Args:
            context: Airflow task context
            
        Returns:
            True if data is available, False otherwise
        """
        hook = PostgresHook(postgres_conn_id=self.postgres_conn_id)
        
        try:
            # Use yesterday's date if target_date not specified
            if not self.target_date:
                logical_date = context["logical_date"]
                target_date = (logical_date - timedelta(days=1)).strftime('%Y-%m-%d')
            else:
                target_date = self.target_date
            
            # Format SQL query with target date
            formatted_query = self.sql_query.format(target_date=target_date)
            
            logger.info(f"Checking data availability with query: {formatted_query}")
            
            # Execute query and get results
            result = hook.get_first(formatted_query)
            
            if not result:
                logger.warning("No data returned from availability query")
                return False
            
            # Extract metrics from result
            row_count = result[0] if len(result) > 0 else 0
            latest_timestamp = result[1] if len(result) > 1 else None
            
            logger.info(f"Data availability check - Rows: {row_count}, Latest: {latest_timestamp}")
            
            # Check row count criteria
            if row_count < self.min_row_count:
                logger.info(f"Insufficient data: {row_count} rows (minimum: {self.min_row_count})")
                return False
            
            # Check data freshness if timestamp available
            if latest_timestamp:
                if isinstance(latest_timestamp, str):
                    latest_timestamp = datetime.fromisoformat(latest_timestamp.replace('Z', '+00:00'))
                
                age_hours = (datetime.now() - latest_timestamp.replace(tzinfo=None)).total_seconds() / 3600
                
                if age_hours > self.max_age_hours:
                    logger.info(f"Data too old: {age_hours:.1f} hours (maximum: {self.max_age_hours})")
                    return False
                
                logger.info(f"Data freshness OK: {age_hours:.1f} hours old")
            
            logger.info(f"Data availability criteria met: {row_count} rows available")
            return True
            
        except Exception as e:
            logger.error(f"Error checking data availability: {e}")
            return False


class UpstreamSystemHealthSensor(BaseSensorOperator):
    """
    Sensor that monitors health of upstream systems before starting ETL.
    
    Checks database connectivity, API availability, and system status.
    """
    
    def __init__(
        self,
        systems_to_check: Dict[str, Dict[str, Any]],
        **kwargs
    ):
        """
        Initialize upstream system health sensor.
        
        Args:
            systems_to_check: Dictionary of systems and their health check configs
        """
        super().__init__(**kwargs)
        self.systems_to_check = systems_to_check
    
    def poke(self, context: Context) -> bool:
        """
        Check health of all upstream systems.
        
        Args:
            context: Airflow task context
            
        Returns:
            True if all systems are healthy, False otherwise
        """
        all_systems_healthy = True
        health_results = {}
        
        for system_name, config in self.systems_to_check.items():
            try:
                system_healthy = self._check_system_health(system_name, config)
                health_results[system_name] = {
                    'healthy': system_healthy,
                    'checked_at': datetime.now().isoformat()
                }
                
                if not system_healthy:
                    all_systems_healthy = False
                    logger.warning(f"System {system_name} is not healthy")
                else:
                    logger.info(f"System {system_name} is healthy")
                    
            except Exception as e:
                logger.error(f"Error checking {system_name}: {e}")
                health_results[system_name] = {
                    'healthy': False,
                    'error': str(e),
                    'checked_at': datetime.now().isoformat()
                }
                all_systems_healthy = False
        
        # Store health check results in XCom
        context['task_instance'].xcom_push(
            key='system_health_results',
            value=health_results
        )
        
        return all_systems_healthy
    
    def _check_system_health(self, system_name: str, config: Dict[str, Any]) -> bool:
        """
        Check health of a specific system.
        
        Args:
            system_name: Name of the system to check
            config: Health check configuration
            
        Returns:
            True if system is healthy, False otherwise
        """
        check_type = config.get('type', 'database')
        
        if check_type == 'database':
            return self._check_database_health(config)
        elif check_type == 'api':
            return self._check_api_health(config)
        elif check_type == 'file_system':
            return self._check_file_system_health(config)
        else:
            logger.warning(f"Unknown health check type: {check_type}")
            return False
    
    def _check_database_health(self, config: Dict[str, Any]) -> bool:
        """Check database connectivity and performance."""
        try:
            conn_id = config.get('conn_id')
            test_query = config.get('test_query', 'SELECT 1')
            timeout_seconds = config.get('timeout_seconds', 30)
            
            hook = PostgresHook(postgres_conn_id=conn_id)
            
            # Test basic connectivity
            result = hook.get_first(test_query)
            
            if result:
                logger.info(f"Database health check passed for {conn_id}")
                return True
            else:
                logger.warning(f"Database health check failed for {conn_id}")
                return False
                
        except Exception as e:
            logger.error(f"Database health check error: {e}")
            return False
    
    def _check_api_health(self, config: Dict[str, Any]) -> bool:
        """Check API availability and response time."""
        try:
            import requests
            
            url = config.get('url')
            timeout = config.get('timeout_seconds', 30)
            expected_status = config.get('expected_status', 200)
            
            response = requests.get(url, timeout=timeout)
            
            if response.status_code == expected_status:
                logger.info(f"API health check passed for {url}")
                return True
            else:
                logger.warning(f"API health check failed for {url}: {response.status_code}")
                return False
                
        except Exception as e:
            logger.error(f"API health check error: {e}")
            return False
    
    def _check_file_system_health(self, config: Dict[str, Any]) -> bool:
        """Check file system availability and space."""
        try:
            import os
            import shutil
            
            path = config.get('path')
            min_free_gb = config.get('min_free_gb', 1)
            
            # Check if path exists and is accessible
            if not os.path.exists(path):
                logger.warning(f"File system path does not exist: {path}")
                return False
            
            # Check available disk space
            disk_usage = shutil.disk_usage(path)
            free_gb = disk_usage.free / (1024**3)
            
            if free_gb < min_free_gb:
                logger.warning(f"Insufficient disk space: {free_gb:.1f}GB (minimum: {min_free_gb}GB)")
                return False
            
            logger.info(f"File system health check passed for {path}: {free_gb:.1f}GB free")
            return True
            
        except Exception as e:
            logger.error(f"File system health check error: {e}")
            return False


