"""
Migration script to import contracts from JSON to database.

Imports existing contracts from agents/contracts.json into the
Postgres/SQLite database for the Contracts API.
"""

import json
import os
import sys
from datetime import datetime
from sqlalchemy.orm import Session

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from api.database import SessionLocal, init_db
from api.models import Contract, ContractLog, ContractStatus, ContractRole


def load_contracts_from_json(file_path: str = "agents/contracts.json"):
    """Load contracts from JSON file."""
    try:
        with open(file_path, 'r') as f:
            data = json.load(f)
        return data
    except FileNotFoundError:
        print(f"Error: Contracts file not found at {file_path}")
        return []
    except json.JSONDecodeError as e:
        print(f"Error: Invalid JSON in contracts file: {e}")
        return []


def migrate_contracts():
    """Migrate contracts from JSON to database."""
    print("🔄 Starting contract migration...")
    
    # Initialize database
    try:
        init_db()
        print("✅ Database initialized")
    except Exception as e:
        print(f"❌ Error initializing database: {e}")
        return False
    
    # Load contracts from JSON
    contracts_data = load_contracts_from_json()
    if not contracts_data:
        print("❌ No contracts found to migrate")
        return False
    
    print(f"📋 Found {len(contracts_data)} contracts to migrate")
    
    # Create database session
    db = SessionLocal()
    
    try:
        migrated_count = 0
        skipped_count = 0
        
        for contract_data in contracts_data:
            contract_id = contract_data.get("id")
            
            # Check if contract already exists
            existing = db.query(Contract).filter(Contract.id == contract_id).first()
            if existing:
                print(f"⏭️  Skipping existing contract: {contract_id}")
                skipped_count += 1
                continue
            
            # Create contract
            contract = Contract(
                id=contract_id,
                title=contract_data.get("title", ""),
                description=contract_data.get("description", ""),
                allowed_files=contract_data.get("allowed_files"),
                completion_criteria=contract_data.get("completion_criteria"),
                roles=contract_data.get("roles"),
                status=ContractStatus(contract_data.get("status", "pending")),
                progress_percentage=contract_data.get("progress_percentage", 0),
                assigned_to=contract_data.get("assigned_to"),
                dependencies=contract_data.get("dependencies"),
                captain_notes=contract_data.get("captain_notes"),
                worker_notes=contract_data.get("worker_notes"),
                tester_notes=contract_data.get("tester_notes"),
                coordination_notes=contract_data.get("coordination_notes")
            )
            
            db.add(contract)
            
            # Create initial log entry
            log_entry = ContractLog(
                contract_id=contract_id,
                action="contract_migrated",
                agent_role=ContractRole.CAPTAIN,
                agent_id="migration_script",
                notes=f"Contract migrated from JSON on {datetime.now().isoformat()}"
            )
            db.add(log_entry)
            
            migrated_count += 1
            print(f"✅ Migrated contract: {contract_id}")
        
        # Commit all changes
        db.commit()
        
        print(f"\n🎉 Migration completed successfully!")
        print(f"📊 Statistics:")
        print(f"   - Migrated: {migrated_count}")
        print(f"   - Skipped: {skipped_count}")
        print(f"   - Total: {migrated_count + skipped_count}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error during migration: {e}")
        db.rollback()
        return False
    
    finally:
        db.close()


def verify_migration():
    """Verify that migration was successful."""
    print("\n🔍 Verifying migration...")
    
    db = SessionLocal()
    
    try:
        # Count contracts in database
        contract_count = db.query(Contract).count()
        print(f"📋 Contracts in database: {contract_count}")
        
        # Count log entries
        log_count = db.query(ContractLog).count()
        print(f"📝 Log entries in database: {log_count}")
        
        # Show sample contracts
        sample_contracts = db.query(Contract).limit(3).all()
        print(f"\n📋 Sample contracts:")
        for contract in sample_contracts:
            print(f"   - {contract.id}: {contract.title} ({contract.status.value})")
        
        return contract_count > 0
        
    except Exception as e:
        print(f"❌ Error verifying migration: {e}")
        return False
    
    finally:
        db.close()


def main():
    """Main migration function."""
    print("🚀 Contracts API Migration Tool")
    print("=" * 50)
    
    # Check if contracts.json exists
    if not os.path.exists("agents/contracts.json"):
        print("❌ Error: agents/contracts.json not found")
        print("   Please ensure you're running this from the project root directory")
        return False
    
    # Run migration
    success = migrate_contracts()
    
    if success:
        # Verify migration
        verify_migration()
        
        print("\n✅ Migration completed successfully!")
        print("🌐 You can now start the API server with:")
        print("   uvicorn api.main:app --reload")
        print("\n📚 API documentation will be available at:")
        print("   http://localhost:8000/docs")
        
        return True
    else:
        print("\n❌ Migration failed!")
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
