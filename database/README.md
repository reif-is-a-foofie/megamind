# Database System - The Ship's Foundation

> *"Our keel is solid"* - The database system provides the foundation for all contract management, data persistence, and system operations.

## Overview

The Database System is the foundational infrastructure that manages all contract data, provides data persistence, and enables the API layer to function properly. It includes comprehensive migration capabilities, data integrity verification, and backup/recovery procedures.

## Features

### 🏗️ Database Infrastructure
- **Multi-Database Support**: PostgreSQL and SQLite support with automatic fallback
- **Connection Pooling**: Efficient connection management with configurable pools
- **Environment Configuration**: Flexible database configuration via environment variables
- **Session Management**: Thread-safe database sessions with automatic cleanup

### 📊 Schema Management
- **Contract Tables**: Comprehensive contract storage with all metadata
- **Logging System**: Complete audit trail for all contract operations
- **System Configuration**: Centralized system settings management
- **Performance Indexes**: Optimized queries with proper indexing

### 🔄 Migration System
- **JSON to Database Migration**: Seamless migration from existing contracts.json
- **Data Validation**: Comprehensive validation of contract data
- **Integrity Verification**: Post-migration data integrity checks
- **Backup and Recovery**: Automatic backup creation and restoration

### 🔐 Data Security
- **Encrypted Configuration**: Secure storage of sensitive configuration
- **Audit Logging**: Complete audit trail for all operations
- **Data Integrity**: Foreign key constraints and validation
- **Access Control**: Session-based access management

## Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   PostgreSQL    │    │     SQLite      │    │  Environment    │
│   (Production)  │    │  (Development)  │    │  Configuration  │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │
         ▼                       ▼                       ▼
┌─────────────────────────────────────────────────────────────────┐
│                    Connection Manager                           │
│              (Database URL Resolution & Pooling)               │
└─────────────────────────────────────────────────────────────────┘
                                 │
                                 ▼
┌─────────────────────────────────────────────────────────────────┐
│                    Database Manager                             │
│              (Main Orchestrator & Business Logic)              │
└─────────────────────────────────────────────────────────────────┘
                                 │
                                 ▼
┌─────────────────────────────────────────────────────────────────┐
│                  Migration Manager                              │
│              (Schema & Data Migration)                         │
└─────────────────────────────────────────────────────────────────┘
                                 │
                                 ▼
┌─────────────────────────────────────────────────────────────────┐
│                      Models                                     │
│              (SQLAlchemy ORM Definitions)                      │
└─────────────────────────────────────────────────────────────────┘
```

## Installation

1. **Install Dependencies**:
   ```bash
   pip install -r database/requirements.txt
   ```

2. **Set Environment Variables** (optional):
   ```bash
   export DB_HOST=localhost
   export DB_PORT=5432
   export DB_NAME=megamind
   export DB_USER=megamind
   export DB_PASSWORD=your_password
   ```

3. **Initialize Database**:
   ```bash
   python database/simple_demo.py
   ```

## Quick Start

### 1. Initialize Database
```python
from database import DatabaseManager

# Initialize database manager
db_manager = DatabaseManager()

# Initialize database schema
success = db_manager.initialize_database()
if success:
    print("Database initialized successfully")
```

### 2. Migrate Contracts
```python
# Migrate contracts from JSON file
success = db_manager.migrate_from_json("agents/contracts.json")
if success:
    print("Contracts migrated successfully")

# Verify migration
verification = db_manager.verify_migration()
print(f"Migration verification: {verification}")
```

### 3. Manage Contracts
```python
# Get all contracts
contracts = db_manager.get_contracts()

# Get contract by ID
contract = db_manager.get_contract("api.02")

# Update contract
updates = {
    "progress_percentage": 75,
    "worker_notes": "Implementation in progress"
}
success = db_manager.update_contract("api.02", updates, actor="worker_agent")
```

### 4. View Logs and Statistics
```python
# Get contract logs
logs = db_manager.get_contract_logs("api.02", limit=10)

# Get system statistics
stats = db_manager.get_system_stats()
print(f"Total contracts: {stats['total_contracts']}")
```

## Data Models

### Contract
- **id**: Primary key
- **contract_id**: Unique contract identifier (e.g., "api.02")
- **title**: Contract title
- **description**: Contract description
- **allowed_files**: List of allowed file patterns
- **completion_criteria**: List of completion criteria
- **dependencies**: List of dependency contract IDs
- **status**: Contract status (pending, in_progress, awaiting_review, completed, cancelled, failed)
- **progress_percentage**: Progress percentage (0-100)
- **assigned_to**: Assigned agent
- **priority**: Contract priority (low, medium, high, immediate)
- **timestamps**: created_at, updated_at, started_at, completed_at
- **notes**: captain_notes, worker_notes, tester_notes, coordination_notes
- **contract_metadata**: Additional contract data

### ContractLog
- **id**: Primary key
- **contract_id**: Reference to contract
- **action**: Action performed (contract_created, contract_updated, etc.)
- **actor**: Actor performing the action
- **message**: Action message
- **old_values**: Previous values (for updates)
- **new_values**: New values (for updates)
- **timestamp**: Action timestamp
- **log_metadata**: Additional log data

### SystemConfig
- **id**: Primary key
- **key**: Configuration key
- **value**: Configuration value
- **value_type**: Value type (string, int, float, bool, json)
- **description**: Configuration description
- **is_encrypted**: Whether value is encrypted
- **timestamps**: created_at, updated_at

## API Reference

### DatabaseManager

#### Core Methods
- `initialize_database()`: Initialize database schema and configuration
- `migrate_from_json(json_file_path)`: Migrate contracts from JSON file
- `verify_migration()`: Verify migration integrity
- `get_contract(contract_id)`: Get contract by ID
- `get_contracts(status, assigned_to, priority)`: Get contracts with filtering
- `update_contract(contract_id, updates, actor)`: Update contract with logging
- `create_contract(contract_data, actor)`: Create new contract
- `get_contract_logs(contract_id, limit)`: Get contract logs
- `get_system_stats()`: Get system statistics
- `backup_database(backup_file)`: Create database backup
- `export_to_json(output_file)`: Export contracts to JSON

#### Configuration Methods
- `get_system_config(key)`: Get system configuration value
- `set_system_config(key, value, value_type, description)`: Set system configuration

### ConnectionManager

#### Connection Methods
- `get_session()`: Get thread-safe database session
- `test_connection()`: Test database connection
- `get_connection_info()`: Get connection pool information
- `close_connections()`: Close all database connections

### MigrationManager

#### Migration Methods
- `create_schema()`: Create database schema
- `drop_schema()`: Drop database schema
- `migrate_contracts_from_json(json_file_path)`: Migrate contracts from JSON
- `verify_migration()`: Verify migration integrity
- `export_to_json(output_file)`: Export contracts to JSON
- `backup_database(backup_file)`: Create database backup

## Database Schema

### PostgreSQL Schema
```sql
-- Create enum types
CREATE TYPE contract_status AS ENUM (
    'pending', 'in_progress', 'awaiting_review', 
    'completed', 'cancelled', 'failed'
);

CREATE TYPE contract_priority AS ENUM (
    'low', 'medium', 'high', 'immediate'
);

-- Create contracts table
CREATE TABLE contracts (
    id SERIAL PRIMARY KEY,
    contract_id VARCHAR(50) UNIQUE NOT NULL,
    title VARCHAR(200) NOT NULL,
    description TEXT,
    allowed_files JSONB,
    completion_criteria JSONB,
    dependencies JSONB,
    status contract_status DEFAULT 'pending' NOT NULL,
    progress_percentage INTEGER DEFAULT 0 NOT NULL,
    assigned_to VARCHAR(100),
    priority contract_priority DEFAULT 'medium' NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP NOT NULL,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP NOT NULL,
    started_at TIMESTAMP WITH TIME ZONE,
    completed_at TIMESTAMP WITH TIME ZONE,
    captain_notes TEXT,
    worker_notes TEXT,
    tester_notes TEXT,
    coordination_notes TEXT,
    contract_metadata JSONB
);

-- Create contract_logs table
CREATE TABLE contract_logs (
    id SERIAL PRIMARY KEY,
    contract_id INTEGER NOT NULL REFERENCES contracts(id) ON DELETE CASCADE,
    action VARCHAR(100) NOT NULL,
    actor VARCHAR(100) NOT NULL,
    message TEXT,
    old_values JSONB,
    new_values JSONB,
    timestamp TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP NOT NULL,
    log_metadata JSONB
);

-- Create system_config table
CREATE TABLE system_config (
    id SERIAL PRIMARY KEY,
    key VARCHAR(100) UNIQUE NOT NULL,
    value TEXT,
    value_type VARCHAR(50) DEFAULT 'string' NOT NULL,
    description TEXT,
    is_encrypted BOOLEAN DEFAULT FALSE NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP NOT NULL,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP NOT NULL
);
```

## Migration Process

### 1. Pre-Migration Validation
```bash
# Validate JSON file without migrating
python scripts/migrate_contracts.py --dry-run
```

### 2. Migration Execution
```bash
# Perform full migration
python scripts/migrate_contracts.py
```

### 3. Post-Migration Verification
```python
# Verify migration integrity
verification = db_manager.verify_migration()
if verification['migration_successful']:
    print("Migration successful")
else:
    print("Migration failed")
```

## Configuration

### Environment Variables
- **DB_HOST**: Database host (default: localhost)
- **DB_PORT**: Database port (default: 5432)
- **DB_NAME**: Database name (default: megamind)
- **DB_USER**: Database user (default: megamind)
- **DB_PASSWORD**: Database password (default: empty, uses SQLite)

### Database URLs
- **PostgreSQL**: `postgresql://user:password@host:port/database`
- **SQLite**: `sqlite:///database/megamind.db`

## Performance

### Indexing Strategy
- **Primary Keys**: All tables have auto-incrementing primary keys
- **Foreign Keys**: Contract logs reference contracts with CASCADE delete
- **Composite Indexes**: Status + priority, assigned_to + status
- **Timestamp Indexes**: Created/updated timestamps for efficient queries

### Connection Pooling
- **Pool Size**: 10 connections (configurable)
- **Max Overflow**: 20 connections (configurable)
- **Pool Recycle**: 1 hour (configurable)
- **Pre-ping**: Enabled for connection health checks

### Query Optimization
- **Eager Loading**: Relationships loaded efficiently
- **Batch Operations**: Bulk insert/update operations
- **Session Management**: Automatic session cleanup
- **Connection Reuse**: Efficient connection pooling

## Security

### Data Protection
- **Encrypted Configuration**: Sensitive config values can be encrypted
- **Session Isolation**: Thread-safe session management
- **SQL Injection Prevention**: Parameterized queries
- **Access Control**: Session-based access management

### Audit Trail
- **Complete Logging**: All contract operations logged
- **Change Tracking**: Old and new values stored for updates
- **Actor Attribution**: All actions attributed to specific actors
- **Timestamp Tracking**: Precise timing of all operations

## Monitoring

### Health Checks
```python
# Test database connection
if db_manager.connection_manager.test_connection():
    print("Database healthy")
else:
    print("Database connection failed")

# Get connection pool stats
conn_info = db_manager.connection_manager.get_connection_info()
print(f"Pool size: {conn_info['pool_size']}")
print(f"Checked out: {conn_info['checked_out']}")
```

### Performance Monitoring
```python
# Get system statistics
stats = db_manager.get_system_stats()
print(f"Total contracts: {stats['total_contracts']}")
print(f"Total logs: {stats['total_log_entries']}")
print(f"Status distribution: {stats['status_distribution']}")
```

## Backup and Recovery

### Automatic Backups
```python
# Create backup
success = db_manager.backup_database()
if success:
    print("Backup created successfully")

# Export to JSON
success = db_manager.export_to_json("backup.json")
if success:
    print("Export completed")
```

### Recovery Process
```python
# Restore from backup
db_manager = DatabaseManager()
db_manager.initialize_database()
db_manager.migrate_from_json("backup.json")
```

## Troubleshooting

### Common Issues

1. **Connection Errors**
   - Verify database is running
   - Check connection credentials
   - Ensure network connectivity

2. **Migration Failures**
   - Validate JSON file format
   - Check file permissions
   - Review error logs

3. **Performance Issues**
   - Monitor connection pool usage
   - Check query performance
   - Review indexing strategy

### Debug Mode
```python
import logging
logging.basicConfig(level=logging.DEBUG)

# Enable SQL logging
db_manager.connection_manager.engine.echo = True
```

## Future Enhancements

### Planned Features
- **Alembic Migrations**: Version-controlled schema migrations
- **Async Support**: Async database operations
- **Replication**: Database replication for high availability
- **Sharding**: Horizontal scaling with database sharding

### Scalability Improvements
- **Connection Pooling**: Advanced connection management
- **Query Optimization**: Advanced query optimization
- **Caching**: Multi-level caching strategy
- **Monitoring**: Advanced monitoring and alerting

## Contributing

### Development Setup
1. Clone the repository
2. Install dependencies: `pip install -r database/requirements.txt`
3. Set up development database
4. Run tests: `python -m pytest database/tests/`

### Code Standards
- Follow PEP 8 style guidelines
- Add comprehensive docstrings
- Include unit tests for new features
- Update documentation for API changes

## License

This project is part of the Megamind system and follows the same licensing terms.

---

*"The ship's foundation is now solid and ready!"* 🚢🏗️
