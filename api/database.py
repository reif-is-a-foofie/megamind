"""
Database configuration and connection management.

Provides SQLAlchemy setup, connection pooling, and database utilities
for the Contracts API with Postgres backend.
"""

import os
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Database configuration
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://user:password@localhost/contracts_db")

# For development/testing, use SQLite if Postgres not available
if DATABASE_URL.startswith("postgresql://") and "localhost" in DATABASE_URL:
    try:
        # Test Postgres connection
        engine = create_engine(DATABASE_URL, pool_pre_ping=True)
        with engine.connect() as conn:
            conn.execute("SELECT 1")
        logger.info("PostgreSQL connection successful")
    except Exception as e:
        logger.warning(f"PostgreSQL connection failed: {e}. Falling back to SQLite.")
        DATABASE_URL = "sqlite:///./contracts.db"
        engine = create_engine(
            DATABASE_URL,
            connect_args={"check_same_thread": False},
            poolclass=StaticPool
        )
else:
    engine = create_engine(DATABASE_URL, pool_pre_ping=True)

# Session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base class for models
Base = declarative_base()


def get_db():
    """Get database session with automatic cleanup."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db():
    """Initialize database tables."""
    try:
        Base.metadata.create_all(bind=engine)
        logger.info("Database tables created successfully")
    except Exception as e:
        logger.error(f"Error creating database tables: {e}")
        raise


def check_db_connection():
    """Check database connection health."""
    try:
        with engine.connect() as conn:
            conn.execute("SELECT 1")
        return True
    except Exception as e:
        logger.error(f"Database connection check failed: {e}")
        return False


def get_db_info():
    """Get database information."""
    try:
        with engine.connect() as conn:
            # Get database name
            if DATABASE_URL.startswith("postgresql://"):
                result = conn.execute("SELECT current_database()")
                db_name = result.scalar()
            else:
                db_name = "SQLite"
            
            # Get table count
            result = conn.execute("SELECT COUNT(*) FROM information_schema.tables WHERE table_schema = 'public'")
            table_count = result.scalar()
            
            return {
                "database_type": "PostgreSQL" if DATABASE_URL.startswith("postgresql://") else "SQLite",
                "database_name": db_name,
                "table_count": table_count,
                "connection_status": "healthy"
            }
    except Exception as e:
        logger.error(f"Error getting database info: {e}")
        return {
            "database_type": "Unknown",
            "database_name": "Unknown",
            "table_count": 0,
            "connection_status": "error",
            "error": str(e)
        }
