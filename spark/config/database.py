"""
Database configuration and connection management for the ETL pipeline.
"""

import os
from typing import Optional, Dict, Any
from sqlalchemy import create_engine, text
from sqlalchemy.engine import Engine
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import QueuePool
import logging

logger = logging.getLogger(__name__)


class DatabaseConfig:
    """Database configuration management."""
    
    def __init__(self):
        self.host = os.getenv('DWH_POSTGRES_HOST', 'localhost')
        self.port = int(os.getenv('DWH_POSTGRES_PORT', '5432'))
        self.database = os.getenv('DWH_POSTGRES_DB', 'ecommerce')
        self.username = os.getenv('DWH_POSTGRES_USER', 'ecommerce_user')
        self.password = os.getenv('DWH_POSTGRES_PASSWORD', 'ecommerce123')
        self.schema = os.getenv('DWH_POSTGRES_SCHEMA', 'public')
        
        # Connection pool settings
        self.pool_size = int(os.getenv('DB_POOL_SIZE', '10'))
        self.max_overflow = int(os.getenv('DB_MAX_OVERFLOW', '20'))
        self.pool_timeout = int(os.getenv('DB_POOL_TIMEOUT', '30'))
        self.pool_recycle = int(os.getenv('DB_POOL_RECYCLE', '3600'))
        
    @property
    def connection_string(self) -> str:
        """Get PostgreSQL connection string."""
        return (
            f"postgresql://{self.username}:{self.password}@"
            f"{self.host}:{self.port}/{self.database}"
        )
    
    @property
    def connection_params(self) -> Dict[str, Any]:
        """Get connection parameters for SQLAlchemy engine."""
        return {
            'poolclass': QueuePool,
            'pool_size': self.pool_size,
            'max_overflow': self.max_overflow,
            'pool_timeout': self.pool_timeout,
            'pool_recycle': self.pool_recycle,
            'pool_pre_ping': True,  # Verify connections before use
            'echo': os.getenv('SQL_ECHO', 'false').lower() == 'true',
            'connect_args': {
                'connect_timeout': 10,
                'application_name': 'ecommerce_etl_pipeline'
            }
        }


class DatabaseManager:
    """Database connection and session management."""
    
    def __init__(self, config: Optional[DatabaseConfig] = None):
        self.config = config or DatabaseConfig()
        self._engine: Optional[Engine] = None
        self._session_factory: Optional[sessionmaker] = None
        
    @property
    def engine(self) -> Engine:
        """Get or create SQLAlchemy engine."""
        if self._engine is None:
            self._engine = create_engine(
                self.config.connection_string,
                **self.config.connection_params
            )
            logger.info(f"Created database engine for {self.config.host}:{self.config.port}")
        return self._engine
    
    @property
    def session_factory(self) -> sessionmaker:
        """Get or create session factory."""
        if self._session_factory is None:
            self._session_factory = sessionmaker(
                bind=self.engine,
                autoflush=False,
                autocommit=False
            )
        return self._session_factory
    
    def get_session(self) -> Session:
        """Create a new database session."""
        return self.session_factory()
    
    def test_connection(self) -> bool:
        """Test database connection."""
        try:
            with self.engine.connect() as conn:
                conn.execute(text("SELECT 1"))
            logger.info("Database connection test successful")
            return True
        except Exception as e:
            logger.error(f"Database connection test failed: {e}")
            return False
    
    def close(self):
        """Close database connections."""
        if self._engine:
            self._engine.dispose()
            logger.info("Database engine disposed")


# Global database manager instance
db_manager = DatabaseManager()


def get_database_session() -> Session:
    """Get a database session (convenience function)."""
    return db_manager.get_session()


def test_database_connection() -> bool:
    """Test database connection (convenience function)."""
    return db_manager.test_connection()
