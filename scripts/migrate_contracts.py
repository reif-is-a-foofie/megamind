#!/usr/bin/env python3
"""
Contract Migration Script - The Ship's Navigator

Migrates contracts from JSON files to the database with proper
validation, error handling, and rollback capabilities.
"""

import sys
import os
import json
import logging
from datetime import datetime
from typing import Dict, Any, List

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database import DatabaseManager

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('database/migration.log'),
        logging.StreamHandler(sys.stdout)
    ]
)

logger = logging.getLogger(__name__)


def validate_contract_data(contract_data: Dict[str, Any]) -> bool:
    """Validate contract data structure."""
    required_fields = ["id", "title"]
    
    for field in required_fields:
        if field not in contract_data:
            logger.error(f"Missing required field: {field}")
            return False
    
    # Validate contract ID format
    contract_id = contract_data["id"]
    if not isinstance(contract_id, str) or "." not in contract_id:
        logger.error(f"Invalid contract ID format: {contract_id}")
        return False
    
    # Validate status
    valid_statuses = ["pending", "in_progress", "awaiting_review", "completed", "cancelled", "failed"]
    status = contract_data.get("status", "pending")
    if status not in valid_statuses:
        logger.error(f"Invalid status: {status}")
        return False
    
    # Validate priority
    valid_priorities = ["low", "medium", "high", "immediate"]
    priority = contract_data.get("priority", "medium")
    if priority not in valid_priorities:
        logger.error(f"Invalid priority: {priority}")
        return False
    
    # Validate progress percentage
    progress = contract_data.get("progress_percentage", 0)
    if not isinstance(progress, int) or progress < 0 or progress > 100:
        logger.error(f"Invalid progress percentage: {progress}")
        return False
    
    return True


def backup_json_file(json_file_path: str) -> str:
    """Create backup of JSON file before migration."""
    try:
        timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
        backup_path = f"{json_file_path}.backup_{timestamp}"
        
        with open(json_file_path, 'r') as source:
            with open(backup_path, 'w') as backup:
                backup.write(source.read())
        
        logger.info(f"Created backup: {backup_path}")
        return backup_path
        
    except Exception as e:
        logger.error(f"Failed to create backup: {e}")
        return ""


def load_contracts_from_json(json_file_path: str) -> List[Dict[str, Any]]:
    """Load contracts from JSON file with validation."""
    try:
        if not os.path.exists(json_file_path):
            logger.error(f"JSON file not found: {json_file_path}")
            return []
        
        with open(json_file_path, 'r') as f:
            contracts_data = json.load(f)
        
        if not isinstance(contracts_data, list):
            logger.error("Invalid JSON format: expected list of contracts")
            return []
        
        # Validate each contract
        valid_contracts = []
        for i, contract_data in enumerate(contracts_data):
            if validate_contract_data(contract_data):
                valid_contracts.append(contract_data)
            else:
                logger.error(f"Invalid contract at index {i}: {contract_data.get('id', 'unknown')}")
        
        logger.info(f"Loaded {len(valid_contracts)} valid contracts from {len(contracts_data)} total")
        return valid_contracts
        
    except json.JSONDecodeError as e:
        logger.error(f"JSON decode error: {e}")
        return []
    except Exception as e:
        logger.error(f"Failed to load contracts from JSON: {e}")
        return []


def migrate_contracts(json_file_path: str = "agents/contracts.json", 
                     database_url: str = None) -> bool:
    """Main migration function."""
    logger.info("Starting contract migration process")
    
    # Create backup
    backup_path = backup_json_file(json_file_path)
    if not backup_path:
        logger.warning("Failed to create backup, but continuing with migration")
    
    # Load contracts from JSON
    contracts_data = load_contracts_from_json(json_file_path)
    if not contracts_data:
        logger.error("No valid contracts to migrate")
        return False
    
    # Initialize database manager
    try:
        db_manager = DatabaseManager(database_url)
        
        # Initialize database
        if not db_manager.initialize_database():
            logger.error("Failed to initialize database")
            return False
        
        # Perform migration
        if not db_manager.migrate_from_json(json_file_path):
            logger.error("Failed to migrate contracts")
            return False
        
        # Verify migration
        verification = db_manager.verify_migration()
        if not verification.get("migration_successful", False):
            logger.error("Migration verification failed")
            logger.error(f"Verification details: {verification}")
            return False
        
        # Log success
        logger.info("Contract migration completed successfully")
        logger.info(f"Migration summary: {verification}")
        
        # Create backup of migrated data
        db_manager.backup_database()
        
        return True
        
    except Exception as e:
        logger.error(f"Migration failed: {e}")
        return False
    finally:
        if 'db_manager' in locals():
            db_manager.close()


def main():
    """Main entry point."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Migrate contracts from JSON to database")
    parser.add_argument("--json-file", default="agents/contracts.json", 
                       help="Path to contracts JSON file")
    parser.add_argument("--database-url", help="Database connection URL")
    parser.add_argument("--dry-run", action="store_true", 
                       help="Validate JSON without migrating")
    
    args = parser.parse_args()
    
    if args.dry_run:
        logger.info("Running in dry-run mode (validation only)")
        contracts_data = load_contracts_from_json(args.json_file)
        if contracts_data:
            logger.info(f"Validation successful: {len(contracts_data)} contracts are valid")
            return True
        else:
            logger.error("Validation failed")
            return False
    
    # Perform migration
    success = migrate_contracts(args.json_file, args.database_url)
    
    if success:
        logger.info("Migration completed successfully")
        sys.exit(0)
    else:
        logger.error("Migration failed")
        sys.exit(1)


if __name__ == "__main__":
    main()
