"""
Role Enforcer - Validates agent permissions and prevents unauthorized actions.

Ensures only authorized agents can perform specific actions on contracts.
"""

from typing import Dict, List, Optional
from dataclasses import dataclass
from datetime import datetime


@dataclass
class AgentAction:
    """Records an agent action with validation."""
    contract_id: str
    agent_role: str
    agent_id: str
    action: str
    timestamp: datetime
    success: bool
    error_message: Optional[str] = None


class RoleEnforcer:
    """Enforces role-based permissions for contract actions."""
    
    # Role-based action permissions
    ROLE_PERMISSIONS = {
        "captain": {
            "assign_contract": True,
            "update_priority": True,
            "add_notes": True,
            "implement": False,
            "test": False,
            "mark_completed": False,
        },
        "worker": {
            "assign_contract": False,
            "update_priority": False,
            "add_notes": True,
            "implement": True,
            "test": False,
            "mark_completed": False,
        },
        "tester": {
            "assign_contract": False,
            "update_priority": False,
            "add_notes": True,
            "implement": False,
            "test": True,
            "mark_completed": True,
        }
    }
    
    def __init__(self):
        self.action_history: List[AgentAction] = []
    
    def can_perform_action(self, agent_role: str, action: str) -> bool:
        """Check if an agent role can perform a specific action."""
        if agent_role not in self.ROLE_PERMISSIONS:
            return False
        
        return self.ROLE_PERMISSIONS[agent_role].get(action, False)
    
    def validate_action(
        self, 
        contract_id: str, 
        agent_role: str, 
        agent_id: str, 
        action: str
    ) -> AgentAction:
        """Validate and record an agent action."""
        can_perform = self.can_perform_action(agent_role, action)
        
        agent_action = AgentAction(
            contract_id=contract_id,
            agent_role=agent_role,
            agent_id=agent_id,
            action=action,
            timestamp=datetime.utcnow(),
            success=can_perform,
            error_message=None if can_perform else f"{agent_role} cannot perform {action}"
        )
        
        self.action_history.append(agent_action)
        
        if not can_perform:
            raise PermissionError(
                f"Agent {agent_id} ({agent_role}) cannot perform action: {action}"
            )
        
        return agent_action
    
    def get_action_history(
        self, 
        contract_id: Optional[str] = None, 
        agent_role: Optional[str] = None
    ) -> List[AgentAction]:
        """Get action history with optional filtering."""
        history = self.action_history
        
        if contract_id:
            history = [action for action in history if action.contract_id == contract_id]
        
        if agent_role:
            history = [action for action in history if action.agent_role == agent_role]
        
        return history
    
    def validate_contract_roles(self, contract: Dict) -> List[str]:
        """Validate that a contract has proper role definitions."""
        errors = []
        
        if "roles" not in contract:
            errors.append("Contract missing roles definition")
            return errors
        
        required_roles = ["captain", "worker", "tester"]
        for role in required_roles:
            if role not in contract["roles"]:
                errors.append(f"Missing required role: {role}")
            else:
                role_def = contract["roles"][role]
                if "responsibility" not in role_def:
                    errors.append(f"Role {role} missing responsibility")
                if "restrictions" not in role_def:
                    errors.append(f"Role {role} missing restrictions")
        
        return errors
    
    def check_role_restrictions(self, agent_role: str, action: str, contract: Dict) -> bool:
        """Check if an action violates role restrictions in a specific contract."""
        if "roles" not in contract or agent_role not in contract["roles"]:
            return False
        
        restrictions = contract["roles"][agent_role].get("restrictions", [])
        
        # Check if action is explicitly forbidden
        for restriction in restrictions:
            if restriction.upper() == f"MUST NOT {action.upper()}":
                return False
            if restriction.upper() == f"ONLY {agent_role.upper()} MAY {action.upper()}":
                return True
        
        # Default to role permissions if no specific restrictions
        return self.can_perform_action(agent_role, action)
