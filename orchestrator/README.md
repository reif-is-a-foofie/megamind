# Contract Orchestrator

The keel of our galleon - enforces Captain-Worker-Tester contract flow with role-based permissions and state transition validation to prevent spec-gaming.

## Overview

The orchestrator ensures all contracts follow the proper flow:
- **Captain** assigns contracts and sequences work
- **Worker** implements and submits progress
- **Tester** validates and marks completed

## Architecture

### Core Components

1. **ContractStateMachine** (`state_machine.py`)
   - Enforces valid state transitions: `pending` → `in_progress` → `awaiting_review` → `completed`
   - Maintains audit trail of all transitions
   - Validates contract structure

2. **RoleEnforcer** (`role_enforcer.py`)
   - Validates agent permissions for specific actions
   - Records all agent actions with success/failure status
   - Enforces role-based restrictions

3. **ContractManager** (`contract_manager.py`)
   - Main orchestrator that coordinates state machine and role enforcer
   - Provides unified interface for contract operations
   - Handles JSON persistence and validation

### State Transitions

```
pending ──[Captain]──→ in_progress ──[Worker]──→ awaiting_review ──[Tester]──→ completed
```

### Role Permissions

| Action | Captain | Worker | Tester |
|--------|---------|--------|--------|
| assign_contract | ✅ | ❌ | ❌ |
| update_progress | ❌ | ✅ | ❌ |
| mark_completed | ❌ | ❌ | ✅ |
| add_notes | ✅ | ✅ | ✅ |

## Usage

### Python API

```python
from orchestrator import ContractManager

# Initialize manager
manager = ContractManager("agents/contracts.json")

# Captain assigns contract
success = manager.assign_contract(
    "contract.id",
    "captain",
    "captain_agent",
    "worker_agent",
    "Assignment notes"
)

# Worker updates progress
success = manager.update_progress(
    "contract.id",
    "worker", 
    "worker_agent",
    75,
    "Progress notes"
)

# Tester marks completed
success = manager.mark_completed(
    "contract.id",
    "tester",
    "tester_agent", 
    "Completion notes"
)
```

### CLI Interface

```bash
# List all contracts
python3 -m orchestrator.cli list

# List contracts by status
python3 -m orchestrator.cli list --status pending

# Show contract details
python3 -m orchestrator.cli show contract.id

# Assign contract (Captain only)
python3 -m orchestrator.cli assign contract.id captain captain_agent worker_agent --notes "Assignment"

# Update progress (Worker only)
python3 -m orchestrator.cli progress contract.id worker worker_agent 75 --notes "Progress"

# Mark completed (Tester only)
python3 -m orchestrator.cli complete contract.id tester tester_agent --notes "Validated"

# Validate all contracts
python3 -m orchestrator.cli validate

# Show audit trail
python3 -m orchestrator.cli audit contract.id
```

## Testing

Run the comprehensive test suite:

```bash
python3 orchestrator/test_orchestrator.py
```

Tests validate:
- ✅ State machine transitions
- ✅ Role-based permissions
- ✅ Contract flow enforcement
- ✅ Unauthorized action blocking
- ✅ Audit trail functionality

## Security Features

1. **Role Validation**: Every action is validated against agent role
2. **State Enforcement**: Invalid state transitions are blocked
3. **Audit Trail**: Complete history of all actions and transitions
4. **Permission Checks**: Explicit restrictions prevent unauthorized actions

## Contract Structure

Each contract must have:
- `id`: Unique identifier
- `status`: Current state (pending/in_progress/awaiting_review/completed)
- `roles`: Role definitions with responsibilities and restrictions
- `completion_criteria`: List of requirements for completion

## Mission Integration

This orchestrator is the foundation that ensures:
- No spec-gaming or unauthorized contract modifications
- Proper separation of concerns between Captain, Worker, and Tester
- Complete audit trail for mission accountability
- Consistent contract flow across all modules

The keel is solid - the galleon is ready to sail! 🏴‍☠️
