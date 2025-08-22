"""
Database Manager - The Ship's Foundation

Main orchestrator for database operations, providing a unified interface
for contract management, migrations, and data access.
"""

import logging
from typing import List, Dict, Any, Optional
from datetime import datetime

from .connection_manager import ConnectionManager
from .migration_manager import MigrationManager
from .models import Contract, ContractLog, ContractStatus, ContractPriority, SystemConfig

logger = logging.getLogger(__name__)


class DatabaseManager:
    """
    Main database manager for the Megamind system.
    
    Features:
    - Contract management operations
    - Database migration and setup
    - Connection management
    - Data integrity and backup
    - System configuration management
    """
    
    def __init__(self, database_url: Optional[str] = None):
        self.connection_manager = ConnectionManager(database_url)
        self.migration_manager = MigrationManager(self.connection_manager)
        
        logger.info("Database manager initialized")
    
    def initialize_database(self) -> bool:
        """Initialize database schema and perform initial setup."""
        try:
            # Create schema
            if not self.migration_manager.create_schema():
                logger.error("Failed to create database schema")
                return False
            
            # Test connection
            if not self.connection_manager.test_connection():
                logger.error("Database connection test failed")
                return False
            
            # Initialize system configuration
            self._initialize_system_config()
            
            logger.info("Database initialized successfully")
            return True
            
        except Exception as e:
            logger.error(f"Failed to initialize database: {e}")
            return False
    
    def _initialize_system_config(self):
        """Initialize system configuration."""
        try:
            with self.connection_manager.get_session() as session:
                # Check if system config already exists
                if session.query(SystemConfig).count() > 0:
                    return
                
                # Create default system configuration
                default_configs = [
                    {
                        "key": "database_version",
                        "value": "1.0.0",
                        "value_type": "string",
                        "description": "Current database schema version"
                    },
                    {
                        "key": "migration_timestamp",
                        "value": datetime.utcnow().isoformat(),
                        "value_type": "string",
                        "description": "Timestamp of last migration"
                    },
                    {
                        "key": "backup_enabled",
                        "value": "true",
                        "value_type": "bool",
                        "description": "Enable automatic database backups"
                    },
                    {
                        "key": "backup_interval_hours",
                        "value": "24",
                        "value_type": "int",
                        "description": "Backup interval in hours"
                    }
                ]
                
                for config_data in default_configs:
                    config = SystemConfig(**config_data)
                    session.add(config)
                
                logger.info("System configuration initialized")
                
        except Exception as e:
            logger.error(f"Failed to initialize system configuration: {e}")
    
    def migrate_from_json(self, json_file_path: str = "agents/contracts.json") -> bool:
        """Migrate contracts from JSON file to database."""
        return self.migration_manager.migrate_contracts_from_json(json_file_path)
    
    def verify_migration(self) -> Dict[str, Any]:
        """Verify migration integrity."""
        return self.migration_manager.verify_migration()
    
    def get_contract(self, contract_id: str) -> Optional[Dict[str, Any]]:
        """Get contract by ID."""
        try:
            with self.connection_manager.get_session() as session:
                contract = session.query(Contract).filter(
                    Contract.contract_id == contract_id
                ).first()
                if contract:
                    return contract.to_dict()
                return None
        except Exception as e:
            logger.error(f"Failed to get contract {contract_id}: {e}")
            return None
    
    def get_contracts(self, 
                     status: Optional[ContractStatus] = None,
                     assigned_to: Optional[str] = None,
                     priority: Optional[ContractPriority] = None) -> List[Contract]:
        """Get contracts with optional filtering."""
        try:
            with self.connection_manager.get_session() as session:
                query = session.query(Contract)
                
                if status:
                    query = query.filter(Contract.status == status)
                
                if assigned_to:
                    query = query.filter(Contract.assigned_to == assigned_to)
                
                if priority:
                    query = query.filter(Contract.priority == priority)
                
                return query.all()
                
        except Exception as e:
            logger.error(f"Failed to get contracts: {e}")
            return []
    
    def update_contract(self, contract_id: str, updates: Dict[str, Any], actor: str = "system") -> bool:
        """Update contract with logging."""
        try:
            with self.connection_manager.get_session() as session:
                contract = session.query(Contract).filter(
                    Contract.contract_id == contract_id
                ).first()
                
                if not contract:
                    logger.error(f"Contract {contract_id} not found")
                    return False
                
                # Store old values for logging
                old_values = contract.to_dict()
                
                # Apply updates
                for key, value in updates.items():
                    if hasattr(contract, key):
                        if key == "status" and isinstance(value, str):
                            value = self.migration_manager._map_status(value)
                        elif key == "priority" and isinstance(value, str):
                            value = self.migration_manager._map_priority(value)
                        
                        setattr(contract, key, value)
                
                # Update timestamp
                contract.updated_at = datetime.utcnow()
                
                # Create log entry
                log_entry = ContractLog(
                    contract_id=contract.id,
                    action="contract_updated",
                    actor=actor,
                    message=f"Contract updated by {actor}",
                    old_values=old_values,
                    new_values=contract.to_dict(),
                    log_metadata={
                        "update_timestamp": datetime.utcnow().isoformat(),
                        "updated_fields": list(updates.keys())
                    }
                )
                
                session.add(log_entry)
                logger.info(f"Updated contract {contract_id}")
                return True
                
        except Exception as e:
            logger.error(f"Failed to update contract {contract_id}: {e}")
            return False
    
    def create_contract(self, contract_data: Dict[str, Any], actor: str = "system") -> Optional[Contract]:
        """Create new contract with logging."""
        try:
            with self.connection_manager.get_session() as session:
                # Create contract
                contract = Contract(
                    contract_id=contract_data["id"],
                    title=contract_data.get("title", ""),
                    description=contract_data.get("description", ""),
                    allowed_files=contract_data.get("allowed_files", []),
                    completion_criteria=contract_data.get("completion_criteria", []),
                    dependencies=contract_data.get("dependencies", []),
                    status=self.migration_manager._map_status(contract_data.get("status", "pending")),
                    progress_percentage=contract_data.get("progress_percentage", 0),
                    assigned_to=contract_data.get("assigned_to"),
                    priority=self.migration_manager._map_priority(contract_data.get("priority", "medium")),
                    captain_notes=contract_data.get("captain_notes"),
                    worker_notes=contract_data.get("worker_notes"),
                    tester_notes=contract_data.get("tester_notes"),
                    coordination_notes=contract_data.get("coordination_notes"),
                    contract_metadata=contract_data.get("metadata", {})
                )
                
                session.add(contract)
                session.flush()  # Get the contract ID
                
                # Create log entry
                log_entry = ContractLog(
                    contract_id=contract.id,
                    action="contract_created",
                    actor=actor,
                    message=f"Contract created by {actor}",
                    new_values=contract.to_dict(),
                    log_metadata={
                        "creation_timestamp": datetime.utcnow().isoformat()
                    }
                )
                
                session.add(log_entry)
                logger.info(f"Created contract {contract.contract_id}")
                return contract
                
        except Exception as e:
            logger.error(f"Failed to create contract: {e}")
            return None
    
    def get_contract_logs(self, contract_id: str, limit: int = 50) -> List[Dict[str, Any]]:
        """Get contract logs."""
        try:
            with self.connection_manager.get_session() as session:
                contract = session.query(Contract).filter(
                    Contract.contract_id == contract_id
                ).first()
                
                if not contract:
                    return []
                
                logs = session.query(ContractLog).filter(
                    ContractLog.contract_id == contract.id
                ).order_by(ContractLog.timestamp.desc()).limit(limit).all()
                
                return [log.to_dict() for log in logs]
                
        except Exception as e:
            logger.error(f"Failed to get contract logs for {contract_id}: {e}")
            return []
    
    def get_system_stats(self) -> Dict[str, Any]:
        """Get system statistics."""
        try:
            with self.connection_manager.get_session() as session:
                total_contracts = session.query(Contract).count()
                total_logs = session.query(ContractLog).count()
                
                # Status distribution
                status_distribution = {}
                for status in ContractStatus:
                    count = session.query(Contract).filter(Contract.status == status).count()
                    status_distribution[status.value] = count
                
                # Priority distribution
                priority_distribution = {}
                for priority in ContractPriority:
                    count = session.query(Contract).filter(Contract.priority == priority).count()
                    priority_distribution[priority.value] = count
                
                # Recent activity
                recent_logs = session.query(ContractLog).order_by(
                    ContractLog.timestamp.desc()
                ).limit(10).all()
                
                stats = {
                    "total_contracts": total_contracts,
                    "total_log_entries": total_logs,
                    "status_distribution": status_distribution,
                    "priority_distribution": priority_distribution,
                    "recent_activity": [
                        {
                            "contract_id": log.contract.contract_id,
                            "action": log.action,
                            "actor": log.actor,
                            "timestamp": log.timestamp.isoformat()
                        }
                        for log in recent_logs
                    ],
                    "connection_info": self.connection_manager.get_connection_info(),
                    "generated_at": datetime.utcnow().isoformat()
                }
                
                return stats
                
        except Exception as e:
            logger.error(f"Failed to get system stats: {e}")
            return {"error": str(e)}
    
    def backup_database(self, backup_file: str = None) -> bool:
        """Create database backup."""
        return self.migration_manager.backup_database(backup_file)
    
    def export_to_json(self, output_file: str = "database/exported_contracts.json") -> bool:
        """Export contracts to JSON format."""
        return self.migration_manager.export_to_json(output_file)
    
    def get_system_config(self, key: str) -> Optional[str]:
        """Get system configuration value."""
        try:
            with self.connection_manager.get_session() as session:
                config = session.query(SystemConfig).filter(SystemConfig.key == key).first()
                return config.value if config else None
        except Exception as e:
            logger.error(f"Failed to get system config {key}: {e}")
            return None
    
    def set_system_config(self, key: str, value: str, value_type: str = "string", description: str = None) -> bool:
        """Set system configuration value."""
        try:
            with self.connection_manager.get_session() as session:
                config = session.query(SystemConfig).filter(SystemConfig.key == key).first()
                
                if config:
                    config.value = value
                    config.updated_at = datetime.utcnow()
                else:
                    config = SystemConfig(
                        key=key,
                        value=value,
                        value_type=value_type,
                        description=description
                    )
                    session.add(config)
                
                logger.info(f"Set system config {key} = {value}")
                return True
                
        except Exception as e:
            logger.error(f"Failed to set system config {key}: {e}")
            return False
    
    def close(self):
        """Close database connections."""
        self.connection_manager.close_connections()
        logger.info("Database manager closed")
    
    def __repr__(self):
        return f"<DatabaseManager(connection_manager={self.connection_manager})>"
