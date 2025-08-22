"""
Contract State Machine - Enforces valid state transitions.

The keel of our galleon - ensures contracts follow the proper flow:
pending -> in_progress -> awaiting_review -> completed
"""

from enum import Enum
from typing import Dict, List, Optional
from dataclasses import dataclass
from datetime import datetime
import json


class ContractStatus(Enum):
    """Valid contract statuses with enforced transitions."""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    AWAITING_REVIEW = "awaiting_review"
    COMPLETED = "completed"


@dataclass
class StateTransition:
    """Records a state transition with audit trail."""
    from_status: ContractStatus
    to_status: ContractStatus
    agent_role: str
    agent_id: str
    timestamp: datetime
    notes: Optional[str] = None


class ContractStateMachine:
    """Enforces valid contract state transitions with role-based permissions."""
    
    # Valid transitions: (from_status, to_status, required_role)
    VALID_TRANSITIONS = [
        (ContractStatus.PENDING, ContractStatus.IN_PROGRESS, "captain"),
        (ContractStatus.IN_PROGRESS, ContractStatus.AWAITING_REVIEW, "worker"),
        (ContractStatus.AWAITING_REVIEW, ContractStatus.COMPLETED, "tester"),
    ]
    
    def __init__(self):
        self.transition_history: Dict[str, List[StateTransition]] = {}
    
    def can_transition(
        self, 
        from_status: str, 
        to_status: str, 
        agent_role: str
    ) -> bool:
        """Check if a state transition is valid for the given role."""
        try:
            from_enum = ContractStatus(from_status)
            to_enum = ContractStatus(to_status)
        except ValueError:
            return False
        
        return (from_enum, to_enum, agent_role) in self.VALID_TRANSITIONS
    
    def transition(
        self, 
        contract_id: str, 
        from_status: str, 
        to_status: str, 
        agent_role: str, 
        agent_id: str,
        notes: Optional[str] = None
    ) -> StateTransition:
        """Execute a state transition with audit trail."""
        if not self.can_transition(from_status, to_status, agent_role):
            raise ValueError(
                f"Invalid transition: {from_status} -> {to_status} by {agent_role}"
            )
        
        transition = StateTransition(
            from_status=ContractStatus(from_status),
            to_status=ContractStatus(to_status),
            agent_role=agent_role,
            agent_id=agent_id,
            timestamp=datetime.utcnow(),
            notes=notes
        )
        
        if contract_id not in self.transition_history:
            self.transition_history[contract_id] = []
        
        self.transition_history[contract_id].append(transition)
        return transition
    
    def get_transition_history(self, contract_id: str) -> List[StateTransition]:
        """Get audit trail for a contract."""
        return self.transition_history.get(contract_id, [])
    
    def validate_contract_flow(self, contract: Dict) -> List[str]:
        """Validate that a contract follows proper flow rules."""
        errors = []
        
        # Check required fields
        required_fields = ["id", "status", "roles"]
        for field in required_fields:
            if field not in contract:
                errors.append(f"Missing required field: {field}")
        
        if "status" in contract:
            try:
                ContractStatus(contract["status"])
            except ValueError:
                errors.append(f"Invalid status: {contract['status']}")
        
        # Check roles structure
        if "roles" in contract:
            required_roles = ["captain", "worker", "tester"]
            for role in required_roles:
                if role not in contract["roles"]:
                    errors.append(f"Missing role definition: {role}")
        
        return errors
