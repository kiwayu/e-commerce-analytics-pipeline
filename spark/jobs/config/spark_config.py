"""
PySpark configuration and session management for incremental file ingestion.
"""

import os
import logging
from typing import Dict, Any, Optional
from pyspark.sql import SparkSession
from pyspark.conf import SparkConf
from dataclasses import dataclass

logger = logging.getLogger(__name__)


@dataclass
class SparkJobConfig:
    """Configuration for PySpark incremental file ingestion jobs."""
    
    # Application settings
    app_name: str = "ecommerce-incremental-file-ingestion"
    master: str = "local[*]"
    
    # Performance settings
    driver_memory: str = "2g"
    executor_memory: str = "2g"
    executor_cores: int = 2
    max_result_size: str = "1g"
    
    # SQL settings
    adaptive_query_execution: bool = True
    adaptive_coalescing: bool = True
    
    # Serialization
    serializer: str = "org.apache.spark.serializer.KryoSerializer"
    
    # Checkpointing
    checkpoint_dir: str = "./spark/data/checkpoint"
    
    # File processing
    input_dir: str = "./spark/data/input"
    processed_dir: str = "./spark/data/processed"
    archive_dir: str = "./spark/data/archive"
    
    # Database settings
    postgres_driver: str = "org.postgresql.Driver"
    postgres_url: str = "jdbc:postgresql://localhost:5432/ecommerce"
    postgres_user: str = "ecommerce_user"
    postgres_password: str = "ecommerce123"
    
    # Job settings
    batch_size: int = 10000
    max_files_per_batch: int = 100
    file_retention_days: int = 30
    
    @classmethod
    def from_environment(cls) -> 'SparkJobConfig':
        """Create configuration from environment variables."""
        return cls(
            app_name=os.getenv('SPARK_APP_NAME', 'ecommerce-incremental-file-ingestion'),
            master=os.getenv('SPARK_MASTER_URL', 'local[*]'),
            driver_memory=os.getenv('SPARK_DRIVER_MEMORY', '2g'),
            executor_memory=os.getenv('SPARK_EXECUTOR_MEMORY', '2g'),
            executor_cores=int(os.getenv('SPARK_EXECUTOR_CORES', '2')),
            checkpoint_dir=os.getenv('SPARK_CHECKPOINT_DIR', './spark/data/checkpoint'),
            input_dir=os.getenv('INPUT_DIR', './spark/data/input'),
            processed_dir=os.getenv('PROCESSED_DIR', './spark/data/processed'),
            archive_dir=os.getenv('ARCHIVE_DIR', './spark/data/archive'),
            postgres_url=os.getenv('POSTGRES_JDBC_URL', 'jdbc:postgresql://localhost:5432/ecommerce'),
            postgres_user=os.getenv('DWH_POSTGRES_USER', 'ecommerce_user'),
            postgres_password=os.getenv('DWH_POSTGRES_PASSWORD', 'ecommerce123'),
            batch_size=int(os.getenv('BATCH_SIZE', '10000')),
            max_files_per_batch=int(os.getenv('MAX_FILES_PER_BATCH', '100')),
            file_retention_days=int(os.getenv('FILE_RETENTION_DAYS', '30'))
        )


class SparkSessionManager:
    """Manages PySpark session lifecycle and configuration."""
    
    def __init__(self, config: Optional[SparkJobConfig] = None):
        self.config = config or SparkJobConfig.from_environment()
        self._session: Optional[SparkSession] = None
    
    def create_session(self) -> SparkSession:
        """Create and configure Spark session."""
        if self._session is not None:
            return self._session
        
        logger.info(f"Creating Spark session: {self.config.app_name}")
        
        # Build Spark configuration
        conf = SparkConf()
        
        # Application settings
        conf.setAppName(self.config.app_name)
        conf.setMaster(self.config.master)
        
        # Memory and performance settings
        conf.set("spark.driver.memory", self.config.driver_memory)
        conf.set("spark.executor.memory", self.config.executor_memory)
        conf.set("spark.executor.cores", str(self.config.executor_cores))
        conf.set("spark.driver.maxResultSize", self.config.max_result_size)
        
        # SQL and optimization settings
        conf.set("spark.sql.adaptive.enabled", str(self.config.adaptive_query_execution))
        conf.set("spark.sql.adaptive.coalescePartitions.enabled", str(self.config.adaptive_coalescing))
        conf.set("spark.sql.adaptive.skewJoin.enabled", "true")
        conf.set("spark.sql.adaptive.localShuffleReader.enabled", "true")
        
        # Serialization
        conf.set("spark.serializer", self.config.serializer)
        conf.set("spark.sql.execution.arrow.pyspark.enabled", "true")
        
        # File format optimizations
        conf.set("spark.sql.parquet.enableVectorizedReader", "true")
        conf.set("spark.sql.parquet.mergeSchema", "false")
        conf.set("spark.sql.parquet.filterPushdown", "true")
        
        # CSV settings
        conf.set("spark.sql.csv.filterPushdown.enabled", "true")
        
        # Checkpointing
        conf.set("spark.sql.streaming.checkpointLocation", self.config.checkpoint_dir)
        
        # Database connectivity
        conf.set("spark.driver.extraClassPath", self._get_postgres_jar_path())
        
        # Create session
        self._session = SparkSession.builder.config(conf=conf).getOrCreate()
        
        # Set checkpoint directory
        self._session.sparkContext.setCheckpointDir(self.config.checkpoint_dir)
        
        # Set log level
        self._session.sparkContext.setLogLevel("WARN")
        
        logger.info(f"Spark session created successfully")
        logger.info(f"Spark version: {self._session.version}")
        logger.info(f"Checkpoint directory: {self.config.checkpoint_dir}")
        
        return self._session
    
    def _get_postgres_jar_path(self) -> str:
        """Get PostgreSQL JDBC driver path."""
        # In production, this would point to the actual JAR file
        # For now, assume it's available in the classpath
        return "/opt/spark/jars/postgresql-42.6.0.jar"
    
    @property
    def session(self) -> SparkSession:
        """Get the current Spark session."""
        if self._session is None:
            self._session = self.create_session()
        return self._session
    
    def stop_session(self):
        """Stop the Spark session."""
        if self._session is not None:
            logger.info("Stopping Spark session")
            self._session.stop()
            self._session = None
    
    def get_session_info(self) -> Dict[str, Any]:
        """Get information about the current Spark session."""
        if self._session is None:
            return {"status": "not_created"}
        
        sc = self._session.sparkContext
        return {
            "status": "active",
            "app_name": sc.appName,
            "app_id": sc.applicationId,
            "master": sc.master,
            "version": self._session.version,
            "default_parallelism": sc.defaultParallelism,
            "checkpoint_dir": self.config.checkpoint_dir,
            "driver_memory": self.config.driver_memory,
            "executor_memory": self.config.executor_memory
        }
    
    def __enter__(self):
        """Context manager entry."""
        return self.create_session()
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.stop_session()


def create_spark_session(config: Optional[SparkJobConfig] = None) -> SparkSession:
    """
    Convenience function to create a Spark session.
    
    Args:
        config: Optional Spark job configuration
        
    Returns:
        Configured Spark session
    """
    manager = SparkSessionManager(config)
    return manager.create_session()


def get_database_properties(config: SparkJobConfig) -> Dict[str, str]:
    """
    Get database connection properties for Spark JDBC operations.
    
    Args:
        config: Spark job configuration
        
    Returns:
        Dictionary of JDBC properties
    """
    return {
        "user": config.postgres_user,
        "password": config.postgres_password,
        "driver": config.postgres_driver,
        "stringtype": "unspecified",
        "rewriteBatchedStatements": "true",
        "batchsize": str(config.batch_size),
        "isolationLevel": "READ_COMMITTED"
    }


def optimize_spark_for_csv_processing(spark: SparkSession, config: SparkJobConfig):
    """
    Apply CSV-specific optimizations to Spark session.
    
    Args:
        spark: Spark session to optimize
        config: Job configuration
    """
    # Set dynamic partition pruning
    spark.conf.set("spark.sql.optimizer.dynamicPartitionPruning.enabled", "true")
    
    # Optimize for CSV reading
    spark.conf.set("spark.sql.csv.filterPushdown.enabled", "true")
    spark.conf.set("spark.sql.execution.arrow.maxRecordsPerBatch", str(config.batch_size))
    
    # Set broadcast threshold for small files
    spark.conf.set("spark.sql.autoBroadcastJoinThreshold", "10MB")
    
    # Optimize shuffle partitions for incremental loads
    spark.conf.set("spark.sql.shuffle.partitions", "200")
    
    logger.info("Applied CSV processing optimizations to Spark session")


# Global session manager for convenience
_global_session_manager = None


def get_or_create_global_session(config: Optional[SparkJobConfig] = None) -> SparkSession:
    """Get or create a global Spark session."""
    global _global_session_manager
    
    if _global_session_manager is None:
        _global_session_manager = SparkSessionManager(config)
    
    return _global_session_manager.session


def stop_global_session():
    """Stop the global Spark session."""
    global _global_session_manager
    
    if _global_session_manager is not None:
        _global_session_manager.stop_session()
        _global_session_manager = None
