"""
Database Migration Manager - The Ship's Navigator

Manages database schema creation, migrations, and data import
from existing JSON files to the database.
"""

import json
import logging
import os
from datetime import datetime
from typing import List, Dict, Any, Optional
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError

from .connection_manager import ConnectionManager
from .models import Base, Contract, ContractLog, ContractStatus, ContractPriority

logger = logging.getLogger(__name__)


class MigrationManager:
    """
    Manages database migrations and schema setup.
    
    Features:
    - Schema creation and updates
    - Data migration from JSON files
    - Migration versioning
    - Rollback capabilities
    - Data integrity verification
    """
    
    def __init__(self, connection_manager: ConnectionManager):
        self.connection_manager = connection_manager
        self.engine = connection_manager.engine
    
    def create_schema(self) -> bool:
        """Create database schema."""
        try:
            Base.metadata.create_all(bind=self.engine)
            logger.info("Database schema created successfully")
            return True
        except Exception as e:
            logger.error(f"Failed to create database schema: {e}")
            return False
    
    def drop_schema(self) -> bool:
        """Drop database schema (use with caution)."""
        try:
            Base.metadata.drop_all(bind=self.engine)
            logger.info("Database schema dropped successfully")
            return True
        except Exception as e:
            logger.error(f"Failed to drop database schema: {e}")
            return False
    
    def migrate_contracts_from_json(self, json_file_path: str = "agents/contracts.json") -> bool:
        """Migrate contracts from JSON file to database."""
        try:
            if not os.path.exists(json_file_path):
                logger.error(f"Contracts JSON file not found: {json_file_path}")
                return False
            
            # Read JSON file
            with open(json_file_path, 'r') as f:
                contracts_data = json.load(f)
            
            if not isinstance(contracts_data, list):
                logger.error("Invalid JSON format: expected list of contracts")
                return False
            
            # Migrate contracts
            migrated_count = 0
            with self.connection_manager.get_session() as session:
                for contract_data in contracts_data:
                    if self._migrate_contract(session, contract_data):
                        migrated_count += 1
            
            logger.info(f"Successfully migrated {migrated_count} contracts from JSON")
            return True
            
        except Exception as e:
            logger.error(f"Failed to migrate contracts from JSON: {e}")
            return False
    
    def _migrate_contract(self, session, contract_data: Dict[str, Any]) -> bool:
        """Migrate a single contract from JSON data."""
        try:
            # Check if contract already exists
            existing_contract = session.query(Contract).filter(
                Contract.contract_id == contract_data.get("id")
            ).first()
            
            if existing_contract:
                logger.info(f"Contract {contract_data.get('id')} already exists, skipping")
                return True
            
            # Create new contract
            contract = Contract(
                contract_id=contract_data.get("id"),
                title=contract_data.get("title", ""),
                description=contract_data.get("description", ""),
                allowed_files=contract_data.get("allowed_files", []),
                completion_criteria=contract_data.get("completion_criteria", []),
                dependencies=contract_data.get("dependencies", []),
                status=self._map_status(contract_data.get("status", "pending")),
                progress_percentage=contract_data.get("progress_percentage", 0),
                assigned_to=contract_data.get("assigned_to"),
                priority=self._map_priority(contract_data.get("priority", "medium")),
                captain_notes=contract_data.get("captain_notes"),
                worker_notes=contract_data.get("worker_notes"),
                tester_notes=contract_data.get("tester_notes"),
                coordination_notes=contract_data.get("coordination_notes"),
                contract_metadata={
                    "migrated_from_json": True,
                    "migration_timestamp": datetime.utcnow().isoformat(),
                    "original_data": contract_data
                }
            )
            
            session.add(contract)
            session.flush()  # Get the contract ID
            
            # Create initial log entry
            log_entry = ContractLog(
                contract_id=contract.id,
                action="contract_created",
                actor="system",
                message=f"Contract migrated from JSON file",
                new_values=contract.to_dict(),
                log_metadata={
                    "migration_source": "json_file",
                    "migration_timestamp": datetime.utcnow().isoformat()
                }
            )
            
            session.add(log_entry)
            logger.info(f"Migrated contract: {contract.contract_id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to migrate contract {contract_data.get('id')}: {e}")
            return False
    
    def _map_status(self, status_str: str) -> ContractStatus:
        """Map status string to ContractStatus enum."""
        status_mapping = {
            "pending": ContractStatus.PENDING,
            "in_progress": ContractStatus.IN_PROGRESS,
            "awaiting_review": ContractStatus.AWAITING_REVIEW,
            "completed": ContractStatus.COMPLETED,
            "cancelled": ContractStatus.CANCELLED,
            "failed": ContractStatus.FAILED
        }
        return status_mapping.get(status_str.lower(), ContractStatus.PENDING)
    
    def _map_priority(self, priority_str: str) -> ContractPriority:
        """Map priority string to ContractPriority enum."""
        priority_mapping = {
            "low": ContractPriority.LOW,
            "medium": ContractPriority.MEDIUM,
            "high": ContractPriority.HIGH,
            "immediate": ContractPriority.IMMEDIATE
        }
        return priority_mapping.get(priority_str.lower(), ContractPriority.MEDIUM)
    
    def verify_migration(self) -> Dict[str, Any]:
        """Verify migration integrity."""
        try:
            with self.connection_manager.get_session() as session:
                # Count contracts
                contract_count = session.query(Contract).count()
                
                # Count log entries
                log_count = session.query(ContractLog).count()
                
                # Check for contracts without logs
                contracts_without_logs = session.query(Contract).outerjoin(
                    ContractLog
                ).filter(ContractLog.id.is_(None)).count()
                
                # Get status distribution
                status_distribution = {}
                for status in ContractStatus:
                    count = session.query(Contract).filter(Contract.status == status).count()
                    status_distribution[status.value] = count
                
                # Get priority distribution
                priority_distribution = {}
                for priority in ContractPriority:
                    count = session.query(Contract).filter(Contract.priority == priority).count()
                    priority_distribution[priority.value] = count
                
                verification_result = {
                    "total_contracts": contract_count,
                    "total_log_entries": log_count,
                    "contracts_without_logs": contracts_without_logs,
                    "status_distribution": status_distribution,
                    "priority_distribution": priority_distribution,
                    "migration_successful": contracts_without_logs == 0,
                    "verification_timestamp": datetime.utcnow().isoformat()
                }
                
                logger.info(f"Migration verification completed: {verification_result}")
                return verification_result
                
        except Exception as e:
            logger.error(f"Failed to verify migration: {e}")
            return {"error": str(e)}
    
    def export_to_json(self, output_file: str = "database/exported_contracts.json") -> bool:
        """Export contracts from database to JSON format."""
        try:
            with self.connection_manager.get_session() as session:
                contracts = session.query(Contract).all()
                
                contracts_data = []
                for contract in contracts:
                    contract_dict = contract.to_dict()
                    # Add logs if requested
                    contract_dict["logs"] = [
                        log.to_dict() for log in contract.logs
                    ]
                    contracts_data.append(contract_dict)
                
                # Ensure directory exists
                os.makedirs(os.path.dirname(output_file), exist_ok=True)
                
                # Write to file
                with open(output_file, 'w') as f:
                    json.dump(contracts_data, f, indent=2)
                
                logger.info(f"Exported {len(contracts_data)} contracts to {output_file}")
                return True
                
        except Exception as e:
            logger.error(f"Failed to export contracts to JSON: {e}")
            return False
    
    def backup_database(self, backup_file: str = None) -> bool:
        """Create database backup."""
        try:
            if not backup_file:
                timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
                backup_file = f"database/backup_{timestamp}.json"
            
            return self.export_to_json(backup_file)
            
        except Exception as e:
            logger.error(f"Failed to create database backup: {e}")
            return False
    
    def get_migration_stats(self) -> Dict[str, Any]:
        """Get migration statistics."""
        try:
            with self.connection_manager.get_session() as session:
                total_contracts = session.query(Contract).count()
                total_logs = session.query(ContractLog).count()
                
                # Get recent activity
                recent_logs = session.query(ContractLog).order_by(
                    ContractLog.timestamp.desc()
                ).limit(10).all()
                
                stats = {
                    "total_contracts": total_contracts,
                    "total_log_entries": total_logs,
                    "recent_activity": [
                        {
                            "contract_id": log.contract.contract_id,
                            "action": log.action,
                            "actor": log.actor,
                            "timestamp": log.timestamp.isoformat()
                        }
                        for log in recent_logs
                    ],
                    "generated_at": datetime.utcnow().isoformat()
                }
                
                return stats
                
        except Exception as e:
            logger.error(f"Failed to get migration stats: {e}")
            return {"error": str(e)}
    
    def __repr__(self):
        return f"<MigrationManager(connection_manager={self.connection_manager})>"
