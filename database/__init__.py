"""
Database Package - The Ship's Foundation

This package provides the database infrastructure for the Megamind system,
including schema management, migrations, and data access layers.
"""

from .database_manager import DatabaseManager
from .models import Contract, ContractLog, Base
from .migration_manager import MigrationManager
from .connection_manager import ConnectionManager

__all__ = ["DatabaseManager", "Contract", "ContractLog", "Base", 
           "MigrationManager", "ConnectionManager"]
