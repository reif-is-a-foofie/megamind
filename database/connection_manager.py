"""
Database Connection Manager - The Ship's Anchor

Manages database connections, connection pooling, and configuration
for the Megamind system.
"""

import os
import logging
from typing import Optional, Dict, Any
from contextlib import contextmanager
from sqlalchemy import create_engine, event, text
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import QueuePool
from sqlalchemy.exc import SQLAlchemyError

logger = logging.getLogger(__name__)


class ConnectionManager:
    """
    Manages database connections and configuration.
    
    Features:
    - Connection pooling for performance
    - Environment-based configuration
    - Connection health monitoring
    - Automatic reconnection
    - Connection encryption support
    """
    
    def __init__(self, database_url: Optional[str] = None):
        self.database_url = database_url or self._get_database_url()
        self.engine = None
        self.SessionLocal = None
        self._initialize_engine()
    
    def _get_database_url(self) -> str:
        """Get database URL from environment or default to SQLite."""
        # Check for PostgreSQL environment variables
        db_host = os.getenv("DB_HOST", "localhost")
        db_port = os.getenv("DB_PORT", "5432")
        db_name = os.getenv("DB_NAME", "megamind")
        db_user = os.getenv("DB_USER", "megamind")
        db_password = os.getenv("DB_PASSWORD", "")
        
        if db_password:
            # Use PostgreSQL
            return f"postgresql://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}"
        else:
            # Use SQLite for development
            return "sqlite:///database/megamind.db"
    
    def _initialize_engine(self):
        """Initialize the SQLAlchemy engine with proper configuration."""
        try:
            if self.database_url.startswith("postgresql"):
                # PostgreSQL configuration
                self.engine = create_engine(
                    self.database_url,
                    poolclass=QueuePool,
                    pool_size=10,
                    max_overflow=20,
                    pool_pre_ping=True,
                    pool_recycle=3600,
                    echo=False  # Set to True for SQL debugging
                )
            else:
                # SQLite configuration
                self.engine = create_engine(
                    self.database_url,
                    poolclass=QueuePool,
                    pool_size=10,
                    max_overflow=20,
                    connect_args={"check_same_thread": False},
                    echo=False
                )
            
            # Create session factory
            self.SessionLocal = sessionmaker(
                autocommit=False,
                autoflush=False,
                bind=self.engine
            )
            
            # Enable foreign key constraints for SQLite
            if self.database_url.startswith("sqlite"):
                def _enable_foreign_keys(dbapi_connection, connection_record):
                    cursor = dbapi_connection.cursor()
                    cursor.execute("PRAGMA foreign_keys=ON")
                    cursor.close()
                
                event.listen(self.engine, "connect", _enable_foreign_keys)
            
            logger.info(f"Database engine initialized: {self.database_url}")
            
        except Exception as e:
            logger.error(f"Failed to initialize database engine: {e}")
            raise
    
    @contextmanager
    def get_session(self) -> Session:
        """Thread-safe database session context manager."""
        session = self.SessionLocal()
        try:
            yield session
            session.commit()
        except Exception as e:
            session.rollback()
            logger.error(f"Database session error: {e}")
            raise
        finally:
            session.close()
    
    def test_connection(self) -> bool:
        """Test database connection."""
        try:
            with self.get_session() as session:
                session.execute(text("SELECT 1"))
            logger.info("Database connection test successful")
            return True
        except Exception as e:
            logger.error(f"Database connection test failed: {e}")
            return False
    
    def get_connection_info(self) -> Dict[str, Any]:
        """Get database connection information."""
        return {
            "database_url": self.database_url,
            "pool_size": self.engine.pool.size(),
            "checked_in": self.engine.pool.checkedin(),
            "checked_out": self.engine.pool.checkedout(),
            "overflow": self.engine.pool.overflow()
        }
    
    def close_connections(self):
        """Close all database connections."""
        if self.engine:
            self.engine.dispose()
            logger.info("Database connections closed")
    
    def __repr__(self):
        return f"<ConnectionManager(database_url='{self.database_url}')>"
