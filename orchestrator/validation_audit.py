#!/usr/bin/env python3
"""
Comprehensive Orchestrator Validation Audit

Validates the Captain-Worker-Tester flow enforcement system and traces
actual contract flow history to identify any systemic issues.
"""

import json
import os
import sys
from typing import Dict, List, Set
from datetime import datetime

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from orchestrator.contract_manager import ContractManager
from orchestrator.state_machine import ContractStatus
from orchestrator.role_enforcer import RoleEnforcer


class OrchestratorAuditor:
    """Comprehensive auditor for the orchestrator system."""
    
    def __init__(self):
        self.manager = ContractManager()
        self.contracts = self.manager.contracts
        self.issues = []
        self.warnings = []
        
    def audit_contract_flow(self) -> Dict[str, List[str]]:
        """Audit the flow of all contracts through the system."""
        print("🔍 Auditing Contract Flow...")
        
        flow_issues = {}
        
        for contract in self.contracts:
            contract_id = contract.get("id", "unknown")
            issues = []
            
            # Check if contract has proper flow
            if not self._validate_contract_flow(contract):
                issues.append("Invalid flow pattern")
            
            # Check role discipline
            role_issues = self._check_role_discipline(contract)
            issues.extend(role_issues)
            
            # Check for missing implementation evidence
            if contract.get("status") == "completed":
                if not self._has_implementation_evidence(contract):
                    issues.append("No implementation evidence found")
            
            if issues:
                flow_issues[contract_id] = issues
        
        return flow_issues
    
    def _validate_contract_flow(self, contract: Dict) -> bool:
        """Validate that a contract follows proper state transitions."""
        status = contract.get("status")
        
        # Check if status is valid
        try:
            ContractStatus(status)
        except ValueError:
            return False
        
        # Check if completed contracts have all required notes
        if status == "completed":
            required_notes = ["captain_notes", "worker_notes", "tester_notes"]
            for note in required_notes:
                if not contract.get(note):
                    return False
        
        return True
    
    def _check_role_discipline(self, contract: Dict) -> List[str]:
        """Check if roles were properly followed."""
        issues = []
        
        # Check if all completed contracts have captain assignment
        if contract.get("status") == "completed":
            if not contract.get("captain_notes"):
                issues.append("Missing captain assignment")
            
            if not contract.get("worker_notes"):
                issues.append("Missing worker implementation")
            
            if not contract.get("tester_notes"):
                issues.append("Missing tester validation")
        
        return issues
    
    def _has_implementation_evidence(self, contract: Dict) -> bool:
        """Check if there's evidence of actual implementation."""
        contract_id = contract.get("id", "")
        
        # Check for implementation directories based on contract type
        implementation_mapping = {
            "ui.01": ["ui"],
            "feed.01": ["feed"],
            "notify.01": ["notify"],
            "game.01": ["game"],
            "memory.01": ["memory"],
            "orchestrator.01": ["orchestrator"],
            "finance.01": ["finance"],
            "crypto.01": ["crypto"],
            "knowledge.01": ["knowledge"],
            "actions.01": ["actions"],
            "raids.01": ["raids"],
            "api.01": ["api"],
            "api.02": ["database", "migrations"]
        }
        
        # Check specific mapping first
        if contract_id in implementation_mapping:
            for dir_name in implementation_mapping[contract_id]:
                if os.path.exists(dir_name):
                    return True
        
        # Check for test files
        test_file = f"tests/test_{contract_id.replace('.', '_')}.py"
        if os.path.exists(test_file):
            return True
        
        # Check for any Python files in the project that might be related
        if contract_id.startswith("ui"):
            return os.path.exists("ui") or any("ui" in f for f in os.listdir(".") if os.path.isdir(f))
        elif contract_id.startswith("feed"):
            return os.path.exists("feed") or any("feed" in f for f in os.listdir(".") if os.path.isdir(f))
        elif contract_id.startswith("notify"):
            return os.path.exists("notify") or any("notify" in f for f in os.listdir(".") if os.path.isdir(f))
        elif contract_id.startswith("game"):
            return os.path.exists("game") or any("game" in f for f in os.listdir(".") if os.path.isdir(f))
        
        return False
    
    def audit_role_permissions(self) -> Dict[str, List[str]]:
        """Audit role-based permissions enforcement."""
        print("🔐 Auditing Role Permissions...")
        
        permission_issues = {}
        enforcer = RoleEnforcer()
        
        # Test all role-action combinations
        roles = ["captain", "worker", "tester"]
        actions = ["assign_contract", "implement", "mark_completed", "test"]
        
        for role in roles:
            for action in actions:
                can_perform = enforcer.can_perform_action(role, action)
                
                # Log any unexpected permissions
                if action == "assign_contract" and role != "captain" and can_perform:
                    permission_issues[f"{role}_assign"] = [f"{role} should not be able to assign contracts"]
                elif action == "mark_completed" and role != "tester" and can_perform:
                    permission_issues[f"{role}_complete"] = [f"{role} should not be able to mark contracts completed"]
                elif action == "implement" and role != "worker" and can_perform:
                    permission_issues[f"{role}_implement"] = [f"{role} should not be able to implement"]
        
        return permission_issues
    
    def audit_state_transitions(self) -> Dict[str, List[str]]:
        """Audit state machine transitions."""
        print("🔄 Auditing State Transitions...")
        
        transition_issues = {}
        state_machine = self.manager.state_machine
        
        # Test all possible transitions
        test_cases = [
            ("pending", "in_progress", "captain", True),
            ("pending", "in_progress", "worker", False),
            ("pending", "completed", "tester", False),
            ("in_progress", "awaiting_review", "worker", True),
            ("in_progress", "awaiting_review", "captain", False),
            ("awaiting_review", "completed", "tester", True),
            ("awaiting_review", "completed", "worker", False),
        ]
        
        for from_status, to_status, role, should_allow in test_cases:
            can_transition = state_machine.can_transition(from_status, to_status, role)
            if can_transition != should_allow:
                key = f"{from_status}_to_{to_status}_{role}"
                transition_issues[key] = [
                    f"Transition {from_status} -> {to_status} by {role} should be {should_allow}, got {can_transition}"
                ]
        
        return transition_issues
    
    def audit_completed_contracts(self) -> Dict[str, List[str]]:
        """Audit all completed contracts for proper flow."""
        print("✅ Auditing Completed Contracts...")
        
        completed_issues = {}
        
        for contract in self.contracts:
            if contract.get("status") == "completed":
                contract_id = contract.get("id", "unknown")
                issues = []
                
                # Check if contract was properly assigned
                if not contract.get("assigned_to"):
                    issues.append("No assignment recorded")
                
                # Check if all required notes are present
                required_notes = ["captain_notes", "worker_notes", "tester_notes"]
                for note in required_notes:
                    if not contract.get(note):
                        issues.append(f"Missing {note}")
                
                # Check if progress is 100%
                if contract.get("progress_percentage", 0) != 100:
                    issues.append("Progress not 100%")
                
                if issues:
                    completed_issues[contract_id] = issues
        
        return completed_issues
    
    def generate_audit_report(self) -> str:
        """Generate comprehensive audit report."""
        print("📊 Generating Audit Report...")
        
        report = []
        report.append("# Orchestrator Validation Audit Report")
        report.append(f"Generated: {datetime.utcnow().isoformat()}")
        report.append("")
        
        # Contract flow audit
        flow_issues = self.audit_contract_flow()
        report.append("## Contract Flow Audit")
        if flow_issues:
            report.append("❌ Issues Found:")
            for contract_id, issues in flow_issues.items():
                report.append(f"  - {contract_id}: {', '.join(issues)}")
        else:
            report.append("✅ All contracts follow proper flow")
        report.append("")
        
        # Role permissions audit
        permission_issues = self.audit_role_permissions()
        report.append("## Role Permissions Audit")
        if permission_issues:
            report.append("❌ Issues Found:")
            for issue_key, issues in permission_issues.items():
                report.append(f"  - {issue_key}: {', '.join(issues)}")
        else:
            report.append("✅ All role permissions properly enforced")
        report.append("")
        
        # State transitions audit
        transition_issues = self.audit_state_transitions()
        report.append("## State Transitions Audit")
        if transition_issues:
            report.append("❌ Issues Found:")
            for issue_key, issues in transition_issues.items():
                report.append(f"  - {issue_key}: {', '.join(issues)}")
        else:
            report.append("✅ All state transitions properly enforced")
        report.append("")
        
        # Completed contracts audit
        completed_issues = self.audit_completed_contracts()
        report.append("## Completed Contracts Audit")
        if completed_issues:
            report.append("❌ Issues Found:")
            for contract_id, issues in completed_issues.items():
                report.append(f"  - {contract_id}: {', '.join(issues)}")
        else:
            report.append("✅ All completed contracts properly validated")
        report.append("")
        
        # Summary
        total_issues = len(flow_issues) + len(permission_issues) + len(transition_issues) + len(completed_issues)
        report.append("## Summary")
        if total_issues == 0:
            report.append("🎉 **VALIDATION PASSED** - Orchestrator system is properly enforcing Captain-Worker-Tester flow")
        else:
            report.append(f"⚠️ **VALIDATION FAILED** - {total_issues} issues found in orchestrator system")
        
        return "\n".join(report)


def main():
    """Run comprehensive orchestrator audit."""
    print("🔍 Starting Comprehensive Orchestrator Validation Audit...\n")
    
    auditor = OrchestratorAuditor()
    report = auditor.generate_audit_report()
    
    print(report)
    
    # Save report to file
    with open("orchestrator_audit_report.md", "w") as f:
        f.write(report)
    
    print("\n📄 Audit report saved to: orchestrator_audit_report.md")
    
    # Exit with appropriate code
    if "VALIDATION FAILED" in report:
        sys.exit(1)
    else:
        sys.exit(0)


if __name__ == "__main__":
    main()
