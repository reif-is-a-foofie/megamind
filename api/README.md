# Contracts API

FastAPI service for intelligent contract management with Postgres backend, authentication, rate limiting, and seamless agent integration.

## Overview

The Contracts API provides a RESTful interface for managing contracts, tracking changes, and enabling agent interactions. It replaces static JSON files with a dynamic, scalable database-backed system.

## Features

### Core Functionality
- **Contract Management**: CRUD operations for contracts
- **Status Tracking**: Real-time status and progress updates
- **Agent Integration**: Role-based access and assignment
- **Audit Logging**: Comprehensive change tracking
- **Statistics**: Contract and agent analytics

### Advanced Features
- **Rate Limiting**: Request throttling per agent
- **Authentication**: Agent-based access control
- **Pagination**: Efficient data retrieval
- **Filtering**: Advanced search and filtering
- **Real-time Updates**: Live contract status changes

## Architecture

### Database Schema
- **contracts**: Main contract data with relationships
- **contract_logs**: Change tracking and audit trail
- **api_audit_logs**: API usage and security monitoring

### API Endpoints
- **GET /health**: System health check
- **GET /contracts**: List contracts with filtering
- **POST /contracts**: Create new contract
- **GET /contracts/{id}**: Get specific contract
- **PUT /contracts/{id}**: Update contract
- **DELETE /contracts/{id}**: Delete contract
- **PATCH /contracts/{id}/status**: Update status
- **PATCH /contracts/{id}/assign**: Assign contract
- **GET /contracts/{id}/logs**: Get contract logs
- **POST /contracts/{id}/logs**: Create log entry
- **GET /statistics/contracts**: Contract statistics
- **GET /statistics/agents**: Agent activity statistics

## Installation

### Prerequisites
- Python 3.8+
- PostgreSQL (optional, falls back to SQLite)
- pip

### Setup

1. **Install dependencies**:
```bash
pip install fastapi uvicorn sqlalchemy psycopg2-binary pydantic
```

2. **Configure database** (optional):
```bash
export DATABASE_URL="postgresql://user:password@localhost/contracts_db"
```

3. **Run migration**:
```bash
python3 api/migrate_contracts.py
```

4. **Start the server**:
```bash
uvicorn api.main:app --reload --host 0.0.0.0 --port 8000
```

## Usage

### Basic API Calls

#### Get All Contracts
```bash
curl -X GET "http://localhost:8000/contracts" \
  -H "X-Agent-ID: worker_agent" \
  -H "X-Agent-Role: worker"
```

#### Create Contract
```bash
curl -X POST "http://localhost:8000/contracts" \
  -H "Content-Type: application/json" \
  -H "X-Agent-ID: captain_agent" \
  -H "X-Agent-Role: captain" \
  -d '{
    "id": "new.01",
    "title": "New Contract",
    "description": "A new contract for testing",
    "allowed_files": ["new/*.py"],
    "completion_criteria": ["Tests pass", "Documentation complete"]
  }'
```

#### Update Contract Status
```bash
curl -X PATCH "http://localhost:8000/contracts/new.01/status" \
  -H "Content-Type: application/json" \
  -H "X-Agent-ID: worker_agent" \
  -H "X-Agent-Role: worker" \
  -d '{
    "status": "in_progress",
    "progress_percentage": 50,
    "notes": "Implementation started"
  }'
```

#### Assign Contract
```bash
curl -X PATCH "http://localhost:8000/contracts/new.01/assign" \
  -H "Content-Type: application/json" \
  -H "X-Agent-ID: captain_agent" \
  -H "X-Agent-Role: captain" \
  -d '{
    "assigned_to": "worker_agent",
    "notes": "Assigned for implementation"
  }'
```

### Python Client Example

```python
import requests

class ContractsAPIClient:
    def __init__(self, base_url="http://localhost:8000", agent_id=None, agent_role=None):
        self.base_url = base_url
        self.headers = {
            "Content-Type": "application/json",
            "X-Agent-ID": agent_id,
            "X-Agent-Role": agent_role
        }
    
    def get_contracts(self, status=None, assigned_to=None, search=None):
        params = {}
        if status:
            params["status"] = status
        if assigned_to:
            params["assigned_to"] = assigned_to
        if search:
            params["search"] = search
        
        response = requests.get(f"{self.base_url}/contracts", headers=self.headers, params=params)
        return response.json()
    
    def get_contract(self, contract_id):
        response = requests.get(f"{self.base_url}/contracts/{contract_id}", headers=self.headers)
        return response.json()
    
    def update_status(self, contract_id, status, progress_percentage, notes=None):
        data = {
            "status": status,
            "progress_percentage": progress_percentage
        }
        if notes:
            data["notes"] = notes
        
        response = requests.patch(
            f"{self.base_url}/contracts/{contract_id}/status",
            headers=self.headers,
            json=data
        )
        return response.json()

# Usage
client = ContractsAPIClient(agent_id="worker_agent", agent_role="worker")

# Get pending contracts
pending_contracts = client.get_contracts(status="pending")

# Update contract status
client.update_status("test.01", "in_progress", 75, "Implementation complete")
```

## API Documentation

### Authentication Headers
- **X-Agent-ID**: Agent identifier (required for rate limiting)
- **X-Agent-Role**: Agent role (captain, worker, tester)

### Response Formats

#### Contract Response
```json
{
  "id": "contract.01",
  "title": "Contract Title",
  "description": "Contract description",
  "allowed_files": ["path/*.py"],
  "completion_criteria": ["Criteria 1", "Criteria 2"],
  "roles": {
    "captain": {"responsibility": "Assign contract"},
    "worker": {"responsibility": "Implement contract"},
    "tester": {"responsibility": "Validate contract"}
  },
  "status": "pending",
  "progress_percentage": 0,
  "assigned_to": "worker_agent",
  "captain_notes": "Captain's notes",
  "worker_notes": "Worker's notes",
  "tester_notes": "Tester's notes",
  "coordination_notes": "Coordination notes",
  "created_at": "2024-01-01T00:00:00",
  "updated_at": "2024-01-01T00:00:00"
}
```

#### Contract List Response
```json
{
  "contracts": [...],
  "total_count": 10,
  "page": 1,
  "page_size": 50,
  "total_pages": 1
}
```

#### Statistics Response
```json
{
  "total_contracts": 10,
  "status_distribution": {
    "pending": 3,
    "in_progress": 5,
    "awaiting_review": 1,
    "completed": 1
  },
  "recent_activity": 15,
  "last_updated": "2024-01-01T00:00:00"
}
```

## Testing

### Run Tests
```bash
python3 api/test_api.py
```

### Test Coverage
- ✅ Health check endpoint
- ✅ Contract CRUD operations
- ✅ Status updates and assignments
- ✅ Logging and audit trails
- ✅ Statistics and analytics
- ✅ Error handling and validation
- ✅ Pagination and filtering
- ✅ Rate limiting and authentication

## Migration

### From JSON to Database
The migration script imports existing contracts from `agents/contracts.json`:

```bash
python3 api/migrate_contracts.py
```

### Migration Features
- **Data Preservation**: All contract data preserved
- **Log Creation**: Initial log entries for migrated contracts
- **Validation**: Checks for existing contracts
- **Statistics**: Migration progress reporting

## Configuration

### Environment Variables
- **DATABASE_URL**: Database connection string
- **LOG_LEVEL**: Logging level (INFO, DEBUG, etc.)

### Database Options
- **PostgreSQL**: Production-ready with connection pooling
- **SQLite**: Development/testing with automatic fallback

### Rate Limiting
- **Default**: 100 requests per minute per agent
- **Configurable**: Adjustable in main.py
- **Storage**: In-memory (use Redis for production)

## Performance

### Optimization Features
- **Connection Pooling**: Efficient database connections
- **Query Optimization**: Indexed database queries
- **Caching**: Response caching for static data
- **Async Support**: Non-blocking operations

### Monitoring
- **Health Checks**: Database and service monitoring
- **Audit Logging**: Complete API usage tracking
- **Performance Metrics**: Response time monitoring
- **Error Tracking**: Comprehensive error logging

## Security

### Authentication
- **Agent-Based**: Role-based access control
- **Rate Limiting**: Request throttling per agent
- **Input Validation**: Pydantic schema validation
- **SQL Injection Protection**: SQLAlchemy ORM

### Audit Trail
- **Change Tracking**: All modifications logged
- **Agent Attribution**: Action attribution to agents
- **IP Tracking**: Request source tracking
- **User Agent Logging**: Client identification

## Mission Integration

This API provides:
- **Foundation Layer**: Core contract management system
- **Agent Connectivity**: Seamless agent integration
- **Scalable Architecture**: Database-backed operations
- **Real-time Updates**: Live contract status changes
- **Comprehensive Logging**: Full audit trail

The API transforms static contract management into a dynamic, intelligent system enabling the galleon to operate with precision and accountability! 🚀⚡
