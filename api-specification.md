# Contracts API Specification

## Overview
The Contracts API serves as the central coordination layer for the 4-agent system, providing contract management, agent monitoring, and stateless resilience capabilities.

## Base URL
```
http://contracts.api/
```

## Authentication
All endpoints require Bearer token authentication:
```
Authorization: Bearer <token>
```

## Core Contract Endpoints

### GET /contracts
Retrieve all contracts with optional filtering.

**Query Parameters:**
- `status` - Filter by contract status (open, in_progress, awaiting_review, completed)
- `assigned_to` - Filter by assigned agent
- `phase` - Filter by mission phase

**Response:**
```json
{
  "contracts": [
    {
      "id": "api.01",
      "title": "Contracts API Implementation",
      "status": "in_progress",
      "assigned_to": "worker_agent",
      "progress_percentage": 75
    }
  ]
}
```

### GET /contracts/{id}
Retrieve specific contract details.

### PUT /contracts/{id}
Update contract status and progress.

### POST /contracts
Create new contract.

## Agent Resilience Endpoints

### POST /contracts/{id}/snapshot
Save agent progress snapshot for stateless recovery.

**Request Body:**
```json
{
  "agent": "worker_agent",
  "mode": "build",
  "tokens_processed": 1000,
  "snapshot": {
    "files_changed": ["contracts_api.py", "models.py"],
    "diff": "...",
    "notes": "API scaffolding complete, implementing routes",
    "progress_percentage": 75
  }
}
```

**Response:**
```json
{
  "snapshot_id": 123,
  "contract_id": "api.01",
  "created_at": "2025-08-22T15:30:00Z"
}
```

### POST /contracts/{id}/heartbeat
Send agent heartbeat for health monitoring.

**Request Body:**
```json
{
  "agent": "worker_agent",
  "tokens_processed": 100,
  "status": "still building routes"
}
```

**Response:**
```json
{
  "heartbeat_id": 456,
  "contract_id": "api.01",
  "created_at": "2025-08-22T15:30:00Z"
}
```

### GET /contracts/{id}/snapshot?latest=true
Retrieve latest snapshot for contract recovery.

**Response:**
```json
{
  "snapshot_id": 123,
  "agent": "worker_agent",
  "mode": "build",
  "tokens_processed": 1000,
  "snapshot": {
    "files_changed": ["contracts_api.py"],
    "notes": "API scaffolding complete"
  },
  "created_at": "2025-08-22T15:30:00Z"
}
```

### GET /contracts/{id}/heartbeat?latest=true
Retrieve latest heartbeat for health monitoring.

**Response:**
```json
{
  "heartbeat_id": 456,
  "agent": "worker_agent",
  "tokens_processed": 100,
  "status": "still building routes",
  "created_at": "2025-08-22T15:30:00Z"
}
```

## Captain Monitoring Endpoints

### GET /agents/health
Monitor all agent health status.

**Response:**
```json
{
  "agents": [
    {
      "agent": "worker_agent",
      "contract_id": "api.01",
      "last_heartbeat": "2025-08-22T15:30:00Z",
      "status": "active",
      "tokens_processed": 1000
    }
  ],
  "stale_agents": [
    {
      "agent": "worker_agent_2",
      "contract_id": "api.02",
      "last_heartbeat": "2025-08-22T15:00:00Z",
      "status": "stale"
    }
  ]
}
```

### GET /contracts/{id}/progress
Get detailed progress for specific contract.

**Response:**
```json
{
  "contract_id": "api.01",
  "current_agent": "worker_agent",
  "progress_percentage": 75,
  "latest_snapshot": {
    "snapshot_id": 123,
    "notes": "API scaffolding complete"
  },
  "latest_heartbeat": {
    "heartbeat_id": 456,
    "status": "still building routes"
  },
  "activity_history": [
    {
      "type": "snapshot",
      "created_at": "2025-08-22T15:30:00Z",
      "tokens_processed": 1000
    }
  ]
}
```

## Database Schema

### contracts Table
```sql
CREATE TABLE contracts (
    id VARCHAR(50) PRIMARY KEY,
    title VARCHAR(255) NOT NULL,
    description TEXT,
    status VARCHAR(20) NOT NULL,
    progress_percentage INT DEFAULT 0,
    assigned_to VARCHAR(50),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

### contract_logs Table
```sql
CREATE TABLE contract_logs (
    id SERIAL PRIMARY KEY,
    contract_id VARCHAR(50) REFERENCES contracts(id),
    agent VARCHAR(50) NOT NULL,
    action VARCHAR(50) NOT NULL,
    details JSONB,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

### agent_snapshots Table
```sql
CREATE TABLE agent_snapshots (
    id SERIAL PRIMARY KEY,
    contract_id VARCHAR(50) REFERENCES contracts(id) ON DELETE CASCADE,
    agent VARCHAR(50) NOT NULL,
    mode VARCHAR(20),
    tokens_processed INT,
    snapshot JSONB,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

### agent_heartbeats Table
```sql
CREATE TABLE agent_heartbeats (
    id SERIAL PRIMARY KEY,
    contract_id VARCHAR(50) REFERENCES contracts(id) ON DELETE CASCADE,
    agent VARCHAR(50) NOT NULL,
    tokens_processed INT,
    status TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

## Indexes
```sql
CREATE INDEX idx_contracts_status ON contracts(status);
CREATE INDEX idx_contracts_assigned_to ON contracts(assigned_to);
CREATE INDEX idx_snapshots_contract_id ON agent_snapshots(contract_id);
CREATE INDEX idx_heartbeats_contract_id ON agent_heartbeats(contract_id);
CREATE INDEX idx_heartbeats_created_at ON agent_heartbeats(created_at);
```

## Agent Integration Guidelines

### Worker Agents
- Send heartbeat every ~100 tokens processed
- Send snapshot every ~1000 tokens processed
- Include progress percentage in snapshots
- Use snapshots for context recovery on restart

### Captain Agent
- Monitor heartbeats for agent health
- Respawn agents with stale heartbeats (>30s)
- Use snapshots for agent recovery
- Track overall system health

### Tester Agent
- Validate contracts against completion criteria
- Update contract status via API
- Log validation results in contract_logs

### Scribe Agent
- Document completed contracts
- Research requirements for new contracts
- Update plan.md based on progress

## Error Handling
- 401 Unauthorized: Invalid or missing authentication
- 404 Not Found: Contract or resource not found
- 422 Validation Error: Invalid request body
- 500 Internal Server Error: Server-side error

## Rate Limiting
- 100 requests per minute per agent
- 1000 requests per hour per agent
- Heartbeat and snapshot endpoints have higher limits
