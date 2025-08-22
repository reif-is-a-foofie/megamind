"""
Contract Manager - Main orchestrator for contract flow enforcement.

Coordinates state machine and role enforcer to provide unified contract operations.
"""

import json
import os
from typing import Dict, List, Optional, Tuple
from pathlib import Path

from .state_machine import ContractStateMachine, ContractStatus
from .role_enforcer import RoleEnforcer


class ContractManager:
    """Main orchestrator for contract flow enforcement."""
    
    def __init__(self, contracts_file: str = "agents/contracts.json"):
        self.contracts_file = contracts_file
        self.state_machine = ContractStateMachine()
        self.role_enforcer = RoleEnforcer()
        self.contracts = self._load_contracts()
    
    def _load_contracts(self) -> List[Dict]:
        """Load contracts from JSON file."""
        try:
            with open(self.contracts_file, 'r') as f:
                contracts = json.load(f)
            
            # Validate all contracts
            for contract in contracts:
                errors = self._validate_contract(contract)
                if errors:
                    print(f"Warning: Contract {contract.get('id', 'unknown')} has validation errors: {errors}")
            
            return contracts
        except FileNotFoundError:
            print(f"Warning: Contracts file {self.contracts_file} not found")
            return []
        except json.JSONDecodeError as e:
            print(f"Error: Invalid JSON in contracts file: {e}")
            return []
    
    def _save_contracts(self) -> bool:
        """Save contracts to JSON file."""
        try:
            # Ensure directory exists
            os.makedirs(os.path.dirname(self.contracts_file), exist_ok=True)
            
            with open(self.contracts_file, 'w') as f:
                json.dump(self.contracts, f, indent=2)
            return True
        except Exception as e:
            print(f"Error saving contracts: {e}")
            return False
    
    def _validate_contract(self, contract: Dict) -> List[str]:
        """Validate a single contract."""
        errors = []
        
        # Basic validation
        errors.extend(self.state_machine.validate_contract_flow(contract))
        errors.extend(self.role_enforcer.validate_contract_roles(contract))
        
        return errors
    
    def get_contract(self, contract_id: str) -> Optional[Dict]:
        """Get a contract by ID."""
        for contract in self.contracts:
            if contract.get("id") == contract_id:
                return contract
        return None
    
    def assign_contract(
        self, 
        contract_id: str, 
        agent_role: str, 
        agent_id: str,
        assigned_to: str,
        notes: Optional[str] = None
    ) -> bool:
        """Assign a contract to an agent (Captain only)."""
        try:
            # Validate action
            self.role_enforcer.validate_action(contract_id, agent_role, agent_id, "assign_contract")
            
            contract = self.get_contract(contract_id)
            if not contract:
                raise ValueError(f"Contract {contract_id} not found")
            
            # Validate state transition
            if not self.state_machine.can_transition(contract["status"], "in_progress", agent_role):
                raise ValueError(f"Cannot assign contract in status: {contract['status']}")
            
            # Execute transition
            self.state_machine.transition(
                contract_id, 
                contract["status"], 
                "in_progress", 
                agent_role, 
                agent_id,
                notes
            )
            
            # Update contract
            contract["status"] = "in_progress"
            contract["assigned_to"] = assigned_to
            if notes:
                contract["captain_notes"] = notes
            
            return self._save_contracts()
            
        except Exception as e:
            print(f"Error assigning contract: {e}")
            return False
    
    def update_progress(
        self, 
        contract_id: str, 
        agent_role: str, 
        agent_id: str,
        progress_percentage: int,
        notes: Optional[str] = None
    ) -> bool:
        """Update contract progress (Worker only)."""
        try:
            # Validate action
            self.role_enforcer.validate_action(contract_id, agent_role, agent_id, "implement")
            
            contract = self.get_contract(contract_id)
            if not contract:
                raise ValueError(f"Contract {contract_id} not found")
            
            # Update progress
            contract["progress_percentage"] = max(0, min(100, progress_percentage))
            
            # Auto-transition to awaiting_review if complete
            if progress_percentage >= 100 and contract["status"] == "in_progress":
                self.state_machine.transition(
                    contract_id,
                    contract["status"],
                    "awaiting_review",
                    agent_role,
                    agent_id,
                    "Progress complete, ready for review"
                )
                contract["status"] = "awaiting_review"
            
            if notes:
                contract["worker_notes"] = notes
            
            return self._save_contracts()
            
        except Exception as e:
            print(f"Error updating progress: {e}")
            return False
    
    def mark_completed(
        self, 
        contract_id: str, 
        agent_role: str, 
        agent_id: str,
        notes: Optional[str] = None
    ) -> bool:
        """Mark contract as completed (Tester only)."""
        try:
            # Validate action
            self.role_enforcer.validate_action(contract_id, agent_role, agent_id, "mark_completed")
            
            contract = self.get_contract(contract_id)
            if not contract:
                raise ValueError(f"Contract {contract_id} not found")
            
            # Validate state transition
            if not self.state_machine.can_transition(contract["status"], "completed", agent_role):
                raise ValueError(f"Cannot complete contract in status: {contract['status']}")
            
            # Execute transition
            self.state_machine.transition(
                contract_id,
                contract["status"],
                "completed",
                agent_role,
                agent_id,
                notes
            )
            
            # Update contract
            contract["status"] = "completed"
            contract["progress_percentage"] = 100
            if notes:
                contract["tester_notes"] = notes
            
            return self._save_contracts()
            
        except Exception as e:
            print(f"Error marking contract completed: {e}")
            return False
    
    def get_contracts_by_status(self, status: str) -> List[Dict]:
        """Get all contracts with a specific status."""
        return [contract for contract in self.contracts if contract.get("status") == status]
    
    def get_contracts_by_agent(self, agent_id: str) -> List[Dict]:
        """Get all contracts assigned to a specific agent."""
        return [contract for contract in self.contracts if contract.get("assigned_to") == agent_id]
    
    def get_audit_trail(self, contract_id: str) -> Tuple[List, List]:
        """Get complete audit trail for a contract."""
        transitions = self.state_machine.get_transition_history(contract_id)
        actions = self.role_enforcer.get_action_history(contract_id)
        return transitions, actions
    
    def validate_all_contracts(self) -> Dict[str, List[str]]:
        """Validate all contracts and return errors."""
        errors = {}
        for contract in self.contracts:
            contract_errors = self._validate_contract(contract)
            if contract_errors:
                errors[contract.get("id", "unknown")] = contract_errors
        return errors
