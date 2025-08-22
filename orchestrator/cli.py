"""
CLI Interface for Contract Orchestrator.

Provides command-line tools for testing and managing contracts.
"""

import argparse
import sys
from typing import Optional

from .contract_manager import ContractManager


def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(description="Contract Orchestrator CLI")
    parser.add_argument("--contracts-file", default="agents/contracts.json", help="Path to contracts file")
    
    subparsers = parser.add_subparsers(dest="command", help="Available commands")
    
    # List contracts
    list_parser = subparsers.add_parser("list", help="List all contracts")
    list_parser.add_argument("--status", help="Filter by status")
    list_parser.add_argument("--agent", help="Filter by assigned agent")
    
    # Show contract details
    show_parser = subparsers.add_parser("show", help="Show contract details")
    show_parser.add_argument("contract_id", help="Contract ID to show")
    
    # Assign contract
    assign_parser = subparsers.add_parser("assign", help="Assign contract to agent")
    assign_parser.add_argument("contract_id", help="Contract ID to assign")
    assign_parser.add_argument("agent_role", help="Role of assigning agent")
    assign_parser.add_argument("agent_id", help="ID of assigning agent")
    assign_parser.add_argument("assigned_to", help="Agent to assign to")
    assign_parser.add_argument("--notes", help="Assignment notes")
    
    # Update progress
    progress_parser = subparsers.add_parser("progress", help="Update contract progress")
    progress_parser.add_argument("contract_id", help="Contract ID")
    progress_parser.add_argument("agent_role", help="Role of updating agent")
    progress_parser.add_argument("agent_id", help="ID of updating agent")
    progress_parser.add_argument("percentage", type=int, help="Progress percentage (0-100)")
    progress_parser.add_argument("--notes", help="Progress notes")
    
    # Mark completed
    complete_parser = subparsers.add_parser("complete", help="Mark contract as completed")
    complete_parser.add_argument("contract_id", help="Contract ID")
    complete_parser.add_argument("agent_role", help="Role of completing agent")
    complete_parser.add_argument("agent_id", help="ID of completing agent")
    complete_parser.add_argument("--notes", help="Completion notes")
    
    # Validate contracts
    validate_parser = subparsers.add_parser("validate", help="Validate all contracts")
    
    # Show audit trail
    audit_parser = subparsers.add_parser("audit", help="Show contract audit trail")
    audit_parser.add_argument("contract_id", help="Contract ID")
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return
    
    # Initialize contract manager
    manager = ContractManager(args.contracts_file)
    
    try:
        if args.command == "list":
            contracts = manager.contracts
            if args.status:
                contracts = manager.get_contracts_by_status(args.status)
            elif args.agent:
                contracts = manager.get_contracts_by_agent(args.agent)
            
            for contract in contracts:
                print(f"{contract['id']}: {contract['title']} ({contract['status']}) - {contract.get('progress_percentage', 0)}%")
        
        elif args.command == "show":
            contract = manager.get_contract(args.contract_id)
            if contract:
                print(f"ID: {contract['id']}")
                print(f"Title: {contract['title']}")
                print(f"Status: {contract['status']}")
                print(f"Progress: {contract.get('progress_percentage', 0)}%")
                print(f"Assigned to: {contract.get('assigned_to', 'None')}")
                print(f"Description: {contract['description']}")
            else:
                print(f"Contract {args.contract_id} not found")
                sys.exit(1)
        
        elif args.command == "assign":
            success = manager.assign_contract(
                args.contract_id,
                args.agent_role,
                args.agent_id,
                args.assigned_to,
                args.notes
            )
            if success:
                print(f"Contract {args.contract_id} assigned to {args.assigned_to}")
            else:
                print("Assignment failed")
                sys.exit(1)
        
        elif args.command == "progress":
            success = manager.update_progress(
                args.contract_id,
                args.agent_role,
                args.agent_id,
                args.percentage,
                args.notes
            )
            if success:
                print(f"Progress updated to {args.percentage}%")
            else:
                print("Progress update failed")
                sys.exit(1)
        
        elif args.command == "complete":
            success = manager.mark_completed(
                args.contract_id,
                args.agent_role,
                args.agent_id,
                args.notes
            )
            if success:
                print(f"Contract {args.contract_id} marked as completed")
            else:
                print("Completion failed")
                sys.exit(1)
        
        elif args.command == "validate":
            errors = manager.validate_all_contracts()
            if errors:
                print("Validation errors found:")
                for contract_id, contract_errors in errors.items():
                    print(f"  {contract_id}:")
                    for error in contract_errors:
                        print(f"    - {error}")
                sys.exit(1)
            else:
                print("All contracts are valid")
        
        elif args.command == "audit":
            transitions, actions = manager.get_audit_trail(args.contract_id)
            print(f"Audit trail for contract {args.contract_id}:")
            print("\nState Transitions:")
            for transition in transitions:
                print(f"  {transition.timestamp}: {transition.from_status.value} -> {transition.to_status.value} by {transition.agent_id} ({transition.agent_role})")
                if transition.notes:
                    print(f"    Notes: {transition.notes}")
            
            print("\nActions:")
            for action in actions:
                status = "✓" if action.success else "✗"
                print(f"  {status} {action.timestamp}: {action.action} by {action.agent_id} ({action.agent_role})")
                if action.error_message:
                    print(f"    Error: {action.error_message}")
    
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
