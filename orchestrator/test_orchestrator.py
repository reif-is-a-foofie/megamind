"""
Test script for Contract Orchestrator.

Validates the orchestrator functionality and demonstrates contract flow enforcement.
"""

import sys
import os
from typing import Dict

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from orchestrator.contract_manager import ContractManager
from orchestrator.state_machine import ContractStatus
from orchestrator.role_enforcer import RoleEnforcer


def test_state_machine():
    """Test state machine transitions."""
    print("Testing State Machine...")
    
    from orchestrator.state_machine import ContractStateMachine
    
    sm = ContractStateMachine()
    
    # Test valid transitions
    assert sm.can_transition("pending", "in_progress", "captain")
    assert sm.can_transition("in_progress", "awaiting_review", "worker")
    assert sm.can_transition("awaiting_review", "completed", "tester")
    
    # Test invalid transitions
    assert not sm.can_transition("pending", "completed", "worker")
    assert not sm.can_transition("in_progress", "completed", "captain")
    assert not sm.can_transition("pending", "in_progress", "worker")
    
    print("✓ State machine transitions validated")


def test_role_enforcer():
    """Test role-based permissions."""
    print("Testing Role Enforcer...")
    
    enforcer = RoleEnforcer()
    
    # Test valid permissions
    assert enforcer.can_perform_action("captain", "assign_contract")
    assert enforcer.can_perform_action("worker", "implement")
    assert enforcer.can_perform_action("tester", "mark_completed")
    
    # Test invalid permissions
    assert not enforcer.can_perform_action("captain", "implement")
    assert not enforcer.can_perform_action("worker", "mark_completed")
    assert not enforcer.can_perform_action("tester", "assign_contract")
    
    print("✓ Role permissions validated")


def test_contract_flow():
    """Test contract flow functionality."""
    print("Testing Contract Flow...")
    
    manager = ContractManager()
    
    # Test that we can get contracts
    contract = manager.get_contract("orchestrator.01")
    assert contract is not None, "Should be able to get contract"
    assert contract["id"] == "orchestrator.01", "Should get correct contract"
    
    # Test progress update on existing in_progress contract
    success = manager.update_progress(
        "memory.01",
        "worker",
        "worker_agent",
        75,
        "Memory system progress update"
    )
    assert success, "Progress update failed"
    
    # Verify progress was updated
    contract = manager.get_contract("memory.01")
    assert contract["progress_percentage"] == 75, "Progress should be updated"
    
    print("✓ Contract flow functionality validated")


def test_unauthorized_actions():
    """Test that unauthorized actions are properly blocked."""
    print("Testing Unauthorized Actions...")
    
    manager = ContractManager()
    
    # Test worker trying to assign contract
    success = manager.assign_contract(
        "notify.01",
        "worker",
        "worker_agent",
        "another_worker",
        "This should fail"
    )
    assert not success, "Worker should not be able to assign contracts"
    
    # Test captain trying to mark contract completed
    success = manager.mark_completed(
        "notify.01",
        "captain",
        "captain_agent",
        "This should fail"
    )
    assert not success, "Captain should not be able to mark contracts completed"
    
    # Test invalid state transition
    success = manager.mark_completed(
        "notify.01",
        "tester",
        "tester_agent",
        "This should fail - contract not in awaiting_review"
    )
    assert not success, "Should not be able to complete contract not in awaiting_review"
    
    print("✓ Unauthorized actions properly blocked")


def test_audit_trail():
    """Test audit trail functionality."""
    print("Testing Audit Trail...")
    
    manager = ContractManager()
    
    # Test audit trail functionality with existing data
    transitions, actions = manager.get_audit_trail("orchestrator.01")
    
    # Verify we can get audit trail (even if empty)
    assert isinstance(transitions, list), "Should return list of transitions"
    assert isinstance(actions, list), "Should return list of actions"
    
    # Test that we can get action history by role
    captain_actions = manager.role_enforcer.get_action_history(agent_role="captain")
    assert isinstance(captain_actions, list), "Should return list of captain actions"
    
    print("✓ Audit trail functionality validated")


def main():
    """Run all tests."""
    print("🧪 Testing Contract Orchestrator...\n")
    
    try:
        test_state_machine()
        test_role_enforcer()
        test_contract_flow()
        test_unauthorized_actions()
        test_audit_trail()
        
        print("\n🎉 All tests passed! Orchestrator is ready for mission.")
        
        # Show final contract status
        manager = ContractManager()
        contract = manager.get_contract("orchestrator.01")
        if contract:
            print(f"\n📋 orchestrator.01 Status: {contract['status']} ({contract['progress_percentage']}%)")
        
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
