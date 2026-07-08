"""
PostgreSQL replication hook for incremental data transfer with high-water mark strategy.
"""

import logging
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime, timezone
import pandas as pd
from contextlib import contextmanager

from airflow.hooks.postgres_hook import PostgresHook
from airflow.exceptions import AirflowException
from airflow.models import Variable

logger = logging.getLogger(__name__)


class PostgreSQLReplicationHook(PostgresHook):
    """
    Extended PostgreSQL hook for incremental replication operations.
    
    Provides high-water mark based incremental replication with automatic
    watermark management and comprehensive error handling.
    """
    
    def __init__(
        self,
        source_conn_id: str = "postgres_source",
        target_conn_id: str = "postgres_dwh", 
        *args, **kwargs
    ):
        """
        Initialize replication hook.
        
        Args:
            source_conn_id: Airflow connection ID for source database
            target_conn_id: Airflow connection ID for target database
        """
        super().__init__(postgres_conn_id=source_conn_id, *args, **kwargs)
        self.source_conn_id = source_conn_id
        self.target_conn_id = target_conn_id
        self._source_hook = None
        self._target_hook = None
    
    @property
    def source_hook(self) -> PostgresHook:
        """Get source database hook."""
        if self._source_hook is None:
            self._source_hook = PostgresHook(postgres_conn_id=self.source_conn_id)
        return self._source_hook
    
    @property
    def target_hook(self) -> PostgresHook:
        """Get target database hook."""
        if self._target_hook is None:
            self._target_hook = PostgresHook(postgres_conn_id=self.target_conn_id)
        return self._target_hook
    
    def get_watermark(self, table_name: str, watermark_column: str = "updated_at") -> Optional[datetime]:
        """
        Get current watermark value from Airflow Variables.
        
        Args:
            table_name: Name of the table being replicated
            watermark_column: Name of the watermark column
            
        Returns:
            Current watermark value or None if not set
        """
        variable_key = f"replication_watermark_{table_name}_{watermark_column}"
        
        try:
            watermark_str = Variable.get(variable_key, default_var=None)
            
            if watermark_str is None:
                logger.info(f"No existing watermark found for {table_name}.{watermark_column}")
                return None
            
            # Parse ISO format timestamp
            watermark = datetime.fromisoformat(watermark_str.replace('Z', '+00:00'))
            logger.info(f"Retrieved watermark for {table_name}.{watermark_column}: {watermark}")
            
            return watermark
            
        except Exception as e:
            logger.error(f"Error retrieving watermark for {table_name}: {e}")
            raise AirflowException(f"Failed to retrieve watermark: {e}")
    
    def set_watermark(
        self, 
        table_name: str, 
        watermark_value: datetime, 
        watermark_column: str = "updated_at"
    ):
        """
        Set watermark value in Airflow Variables.
        
        Args:
            table_name: Name of the table being replicated
            watermark_value: New watermark value
            watermark_column: Name of the watermark column
        """
        variable_key = f"replication_watermark_{table_name}_{watermark_column}"
        
        try:
            # Convert to ISO format string with timezone
            if watermark_value.tzinfo is None:
                watermark_value = watermark_value.replace(tzinfo=timezone.utc)
            
            watermark_str = watermark_value.isoformat()
            
            Variable.set(variable_key, watermark_str)
            logger.info(f"Set watermark for {table_name}.{watermark_column}: {watermark_str}")
            
        except Exception as e:
            logger.error(f"Error setting watermark for {table_name}: {e}")
            raise AirflowException(f"Failed to set watermark: {e}")
    
    def get_max_watermark_from_source(
        self, 
        table_name: str, 
        watermark_column: str = "updated_at"
    ) -> Optional[datetime]:
        """
        Get maximum watermark value from source table.
        
        Args:
            table_name: Source table name
            watermark_column: Watermark column name
            
        Returns:
            Maximum watermark value or None if table is empty
        """
        try:
            sql = f"""
                SELECT MAX({watermark_column}) as max_watermark
                FROM {table_name}
                WHERE {watermark_column} IS NOT NULL
            """
            
            result = self.source_hook.get_first(sql)
            
            if result and result[0]:
                max_watermark = result[0]
                
                # Ensure timezone awareness
                if isinstance(max_watermark, datetime) and max_watermark.tzinfo is None:
                    max_watermark = max_watermark.replace(tzinfo=timezone.utc)
                
                logger.info(f"Max watermark in {table_name}.{watermark_column}: {max_watermark}")
                return max_watermark
            
            logger.info(f"No data found in {table_name}.{watermark_column}")
            return None
            
        except Exception as e:
            logger.error(f"Error getting max watermark from {table_name}: {e}")
            raise AirflowException(f"Failed to get max watermark: {e}")
    
    def get_incremental_data(
        self,
        table_name: str,
        watermark_column: str = "updated_at",
        last_watermark: Optional[datetime] = None,
        limit: Optional[int] = None,
        additional_filters: Optional[str] = None
    ) -> Tuple[pd.DataFrame, int, Optional[datetime]]:
        """
        Extract incremental data from source table.
        
        Args:
            table_name: Source table name
            watermark_column: Watermark column name
            last_watermark: Last processed watermark value
            limit: Maximum number of records to fetch
            additional_filters: Additional WHERE conditions
            
        Returns:
            Tuple of (DataFrame, record_count, new_watermark)
        """
        try:
            # Build WHERE clause
            where_conditions = []
            
            if last_watermark:
                # Format timestamp for SQL
                if last_watermark.tzinfo is None:
                    last_watermark = last_watermark.replace(tzinfo=timezone.utc)
                
                timestamp_str = last_watermark.strftime('%Y-%m-%d %H:%M:%S.%f')
                where_conditions.append(f"{watermark_column} > '{timestamp_str}'::timestamp with time zone")
            
            if additional_filters:
                where_conditions.append(additional_filters)
            
            where_clause = " AND ".join(where_conditions) if where_conditions else "1=1"
            
            # Build SQL query
            sql = f"""
                SELECT *
                FROM {table_name}
                WHERE {where_clause}
                ORDER BY {watermark_column} ASC
            """
            
            if limit:
                sql += f" LIMIT {limit}"
            
            logger.info(f"Executing incremental query: {sql}")
            
            # Execute query and get data
            df = self.source_hook.get_pandas_df(sql)
            record_count = len(df)
            
            # Get new watermark from the data
            new_watermark = None
            if record_count > 0 and watermark_column in df.columns:
                new_watermark = df[watermark_column].max()
                
                # Ensure timezone awareness
                if isinstance(new_watermark, datetime) and new_watermark.tzinfo is None:
                    new_watermark = new_watermark.replace(tzinfo=timezone.utc)
            
            logger.info(f"Extracted {record_count} records from {table_name}")
            logger.info(f"New watermark: {new_watermark}")
            
            return df, record_count, new_watermark
            
        except Exception as e:
            logger.error(f"Error extracting incremental data from {table_name}: {e}")
            raise AirflowException(f"Failed to extract incremental data: {e}")
    
    def insert_data(
        self,
        df: pd.DataFrame,
        target_table: str,
        if_exists: str = "append",
        chunk_size: int = 10000
    ) -> int:
        """
        Insert data into target table.
        
        Args:
            df: DataFrame to insert
            target_table: Target table name
            if_exists: How to behave if table exists ('append', 'replace', 'fail')
            chunk_size: Number of records per batch
            
        Returns:
            Number of records inserted
        """
        try:
            if df.empty:
                logger.info("No data to insert")
                return 0
            
            # Get target database engine
            engine = self.target_hook.get_sqlalchemy_engine()
            
            # Insert data in chunks
            total_inserted = 0
            
            for i in range(0, len(df), chunk_size):
                chunk = df.iloc[i:i + chunk_size]
                
                # Insert chunk
                chunk.to_sql(
                    target_table,
                    engine,
                    if_exists=if_exists if i == 0 else "append",
                    index=False,
                    method='multi'
                )
                
                total_inserted += len(chunk)
                logger.info(f"Inserted chunk {i//chunk_size + 1}: {len(chunk)} records")
            
            logger.info(f"Successfully inserted {total_inserted} records into {target_table}")
            return total_inserted
            
        except Exception as e:
            logger.error(f"Error inserting data into {target_table}: {e}")
            raise AirflowException(f"Failed to insert data: {e}")
    
    def upsert_data(
        self,
        df: pd.DataFrame,
        target_table: str,
        primary_key_columns: List[str],
        chunk_size: int = 10000
    ) -> Dict[str, int]:
        """
        Upsert data into target table using INSERT ... ON CONFLICT.
        
        Args:
            df: DataFrame to upsert
            target_table: Target table name
            primary_key_columns: List of primary key column names
            chunk_size: Number of records per batch
            
        Returns:
            Dictionary with insert and update counts
        """
        try:
            if df.empty:
                logger.info("No data to upsert")
                return {"inserted": 0, "updated": 0}
            
            total_inserted = 0
            total_updated = 0
            
            # Process in chunks
            for i in range(0, len(df), chunk_size):
                chunk = df.iloc[i:i + chunk_size]
                
                # Generate column lists
                columns = list(chunk.columns)
                column_list = ", ".join(columns)
                
                # Generate values placeholders
                values_list = []
                for _, row in chunk.iterrows():
                    values = []
                    for col in columns:
                        value = row[col]
                        if pd.isna(value):
                            values.append("NULL")
                        elif isinstance(value, str):
                            escaped_value = value.replace("'", "''")
                            values.append(f"'{escaped_value}'")
                        elif isinstance(value, datetime):
                            values.append(f"'{value.isoformat()}'")
                        else:
                            values.append(str(value))
                    values_list.append(f"({', '.join(values)})")
                
                values_clause = ",\n".join(values_list)
                
                # Generate update clause
                update_columns = [col for col in columns if col not in primary_key_columns]
                update_clause = ", ".join([f"{col} = EXCLUDED.{col}" for col in update_columns])
                
                # Generate conflict clause
                conflict_columns = ", ".join(primary_key_columns)
                
                # Build upsert SQL
                sql = f"""
                    INSERT INTO {target_table} ({column_list})
                    VALUES {values_clause}
                    ON CONFLICT ({conflict_columns})
                    DO UPDATE SET
                        {update_clause},
                        updated_at = CURRENT_TIMESTAMP
                """
                
                # Execute upsert
                self.target_hook.run(sql)
                
                # Get affected row counts (simplified)
                chunk_size_actual = len(chunk)
                total_inserted += chunk_size_actual  # Approximation
                
                logger.info(f"Upserted chunk {i//chunk_size + 1}: {chunk_size_actual} records")
            
            result = {"inserted": total_inserted, "updated": total_updated}
            logger.info(f"Upsert completed: {result}")
            
            return result
            
        except Exception as e:
            logger.error(f"Error upserting data into {target_table}: {e}")
            raise AirflowException(f"Failed to upsert data: {e}")
    
    @contextmanager
    def transaction(self, connection_id: str):
        """
        Context manager for database transactions.
        
        Args:
            connection_id: Connection ID to use for transaction
        """
        hook = PostgresHook(postgres_conn_id=connection_id)
        conn = hook.get_conn()
        
        try:
            conn.autocommit = False
            yield conn
            conn.commit()
            logger.info("Transaction committed successfully")
            
        except Exception as e:
            conn.rollback()
            logger.error(f"Transaction rolled back due to error: {e}")
            raise
            
        finally:
            conn.close()
    
    def validate_replication_setup(
        self, 
        source_table: str, 
        target_table: str,
        watermark_column: str = "updated_at"
    ) -> Dict[str, Any]:
        """
        Validate replication setup and return diagnostic information.
        
        Args:
            source_table: Source table name
            target_table: Target table name
            watermark_column: Watermark column name
            
        Returns:
            Dictionary with validation results
        """
        validation_results = {
            "source_exists": False,
            "target_exists": False,
            "watermark_column_exists": False,
            "source_count": 0,
            "target_count": 0,
            "watermark_range": None,
            "errors": []
        }
        
        try:
            # Check source table
            try:
                source_count_sql = f"SELECT COUNT(*) FROM {source_table}"
                source_count = self.source_hook.get_first(source_count_sql)[0]
                validation_results["source_exists"] = True
                validation_results["source_count"] = source_count
                
                # Check watermark column
                watermark_check_sql = f"""
                    SELECT column_name 
                    FROM information_schema.columns 
                    WHERE table_name = '{source_table.split('.')[-1]}' 
                    AND column_name = '{watermark_column}'
                """
                watermark_exists = self.source_hook.get_first(watermark_check_sql)
                validation_results["watermark_column_exists"] = watermark_exists is not None
                
                if validation_results["watermark_column_exists"]:
                    # Get watermark range
                    range_sql = f"""
                        SELECT 
                            MIN({watermark_column}) as min_watermark,
                            MAX({watermark_column}) as max_watermark
                        FROM {source_table}
                        WHERE {watermark_column} IS NOT NULL
                    """
                    range_result = self.source_hook.get_first(range_sql)
                    if range_result:
                        validation_results["watermark_range"] = {
                            "min": range_result[0],
                            "max": range_result[1]
                        }
                
            except Exception as e:
                validation_results["errors"].append(f"Source table error: {e}")
            
            # Check target table
            try:
                target_count_sql = f"SELECT COUNT(*) FROM {target_table}"
                target_count = self.target_hook.get_first(target_count_sql)[0]
                validation_results["target_exists"] = True
                validation_results["target_count"] = target_count
                
            except Exception as e:
                validation_results["errors"].append(f"Target table error: {e}")
            
            # Overall validation status
            validation_results["is_valid"] = (
                validation_results["source_exists"] and
                validation_results["target_exists"] and
                validation_results["watermark_column_exists"] and
                len(validation_results["errors"]) == 0
            )
            
            return validation_results
            
        except Exception as e:
            validation_results["errors"].append(f"Validation error: {e}")
            validation_results["is_valid"] = False
            return validation_results
    
    def get_replication_stats(
        self,
        source_table: str,
        target_table: str,
        watermark_column: str = "updated_at"
    ) -> Dict[str, Any]:
        """
        Get comprehensive replication statistics.
        
        Args:
            source_table: Source table name
            target_table: Target table name
            watermark_column: Watermark column name
            
        Returns:
            Dictionary with replication statistics
        """
        try:
            stats = {}
            
            # Source statistics
            source_stats_sql = f"""
                SELECT 
                    COUNT(*) as total_rows,
                    COUNT({watermark_column}) as rows_with_watermark,
                    MIN({watermark_column}) as min_watermark,
                    MAX({watermark_column}) as max_watermark,
                    AVG(EXTRACT(EPOCH FROM (CURRENT_TIMESTAMP - {watermark_column}))) as avg_age_seconds
                FROM {source_table}
            """
            
            source_result = self.source_hook.get_first(source_stats_sql)
            stats["source"] = {
                "total_rows": source_result[0] if source_result else 0,
                "rows_with_watermark": source_result[1] if source_result else 0,
                "min_watermark": source_result[2] if source_result else None,
                "max_watermark": source_result[3] if source_result else None,
                "avg_age_seconds": source_result[4] if source_result else None
            }
            
            # Target statistics
            target_stats_sql = f"SELECT COUNT(*) FROM {target_table}"
            target_result = self.target_hook.get_first(target_stats_sql)
            stats["target"] = {
                "total_rows": target_result[0] if target_result else 0
            }
            
            # Current watermark
            current_watermark = self.get_watermark(source_table.split('.')[-1], watermark_column)
            stats["current_watermark"] = current_watermark
            
            # Lag analysis
            if stats["source"]["max_watermark"] and current_watermark:
                lag_seconds = (stats["source"]["max_watermark"] - current_watermark).total_seconds()
                stats["lag_seconds"] = max(0, lag_seconds)
                stats["is_lagging"] = lag_seconds > 3600  # More than 1 hour behind
            else:
                stats["lag_seconds"] = None
                stats["is_lagging"] = False
            
            return stats
            
        except Exception as e:
            logger.error(f"Error getting replication stats: {e}")
            raise AirflowException(f"Failed to get replication stats: {e}")
