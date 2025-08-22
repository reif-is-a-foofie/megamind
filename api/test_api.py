"""
Test suite for Contracts API.

Comprehensive testing of all API endpoints, database operations,
authentication, and error handling.
"""

import sys
import os
import json
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from datetime import datetime

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from api.main import app
from api.database import Base, get_db
from api.models import Contract, ContractLog, ContractStatus, ContractRole


# Test database setup
SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def override_get_db():
    """Override database dependency for testing."""
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db

# Create test client
client = TestClient(app)


@pytest.fixture(scope="function")
def setup_database():
    """Setup test database before each test."""
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)


def test_health_check(setup_database):
    """Test health check endpoint."""
    print("Testing Health Check...")
    
    response = client.get("/health")
    assert response.status_code == 200
    
    data = response.json()
    assert "status" in data
    assert "timestamp" in data
    assert "database" in data
    assert "version" in data
    
    print("✅ Health check validated")


def test_create_contract(setup_database):
    """Test contract creation."""
    print("Testing Contract Creation...")
    
    contract_data = {
        "id": "test.01",
        "title": "Test Contract",
        "description": "A test contract for API validation",
        "allowed_files": ["test/*.py"],
        "completion_criteria": ["Test passes", "Documentation complete"],
        "roles": {
            "captain": {"responsibility": "Assign contract"},
            "worker": {"responsibility": "Implement contract"},
            "tester": {"responsibility": "Validate contract"}
        }
    }
    
    response = client.post("/contracts", json=contract_data)
    assert response.status_code == 201
    
    data = response.json()
    assert data["id"] == "test.01"
    assert data["title"] == "Test Contract"
    assert data["status"] == "pending"
    assert data["progress_percentage"] == 0
    
    print("✅ Contract creation validated")


def test_get_contracts(setup_database):
    """Test getting contracts list."""
    print("Testing Get Contracts...")
    
    # Create test contracts
    contracts_data = [
        {
            "id": "test.01",
            "title": "Test Contract 1",
            "description": "First test contract"
        },
        {
            "id": "test.02",
            "title": "Test Contract 2",
            "description": "Second test contract"
        }
    ]
    
    for contract_data in contracts_data:
        client.post("/contracts", json=contract_data)
    
    # Get contracts
    response = client.get("/contracts")
    assert response.status_code == 200
    
    data = response.json()
    assert "contracts" in data
    assert "total_count" in data
    assert "page" in data
    assert "page_size" in data
    assert "total_pages" in data
    assert len(data["contracts"]) == 2
    
    print("✅ Get contracts validated")


def test_get_contract(setup_database):
    """Test getting a specific contract."""
    print("Testing Get Contract...")
    
    # Create test contract
    contract_data = {
        "id": "test.01",
        "title": "Test Contract",
        "description": "A test contract"
    }
    
    client.post("/contracts", json=contract_data)
    
    # Get specific contract
    response = client.get("/contracts/test.01")
    assert response.status_code == 200
    
    data = response.json()
    assert data["id"] == "test.01"
    assert data["title"] == "Test Contract"
    
    # Test non-existent contract
    response = client.get("/contracts/nonexistent")
    assert response.status_code == 404
    
    print("✅ Get contract validated")


def test_update_contract(setup_database):
    """Test contract updates."""
    print("Testing Update Contract...")
    
    # Create test contract
    contract_data = {
        "id": "test.01",
        "title": "Test Contract",
        "description": "A test contract"
    }
    
    client.post("/contracts", json=contract_data)
    
    # Update contract
    update_data = {
        "title": "Updated Test Contract",
        "description": "An updated test contract",
        "progress_percentage": 50
    }
    
    response = client.put("/contracts/test.01", json=update_data)
    assert response.status_code == 200
    
    data = response.json()
    assert data["title"] == "Updated Test Contract"
    assert data["progress_percentage"] == 50
    
    print("✅ Update contract validated")


def test_update_contract_status(setup_database):
    """Test contract status updates."""
    print("Testing Update Contract Status...")
    
    # Create test contract
    contract_data = {
        "id": "test.01",
        "title": "Test Contract",
        "description": "A test contract"
    }
    
    client.post("/contracts", json=contract_data)
    
    # Update status
    status_data = {
        "status": "in_progress",
        "progress_percentage": 25,
        "notes": "Starting implementation"
    }
    
    response = client.patch("/contracts/test.01/status", json=status_data)
    assert response.status_code == 200
    
    data = response.json()
    assert data["status"] == "in_progress"
    assert data["progress_percentage"] == 25
    
    print("✅ Update contract status validated")


def test_assign_contract(setup_database):
    """Test contract assignment."""
    print("Testing Assign Contract...")
    
    # Create test contract
    contract_data = {
        "id": "test.01",
        "title": "Test Contract",
        "description": "A test contract"
    }
    
    client.post("/contracts", json=contract_data)
    
    # Assign contract
    assignment_data = {
        "assigned_to": "worker_agent",
        "notes": "Assigned to worker for implementation"
    }
    
    response = client.patch("/contracts/test.01/assign", json=assignment_data)
    assert response.status_code == 200
    
    data = response.json()
    assert data["assigned_to"] == "worker_agent"
    
    print("✅ Assign contract validated")


def test_contract_logs(setup_database):
    """Test contract logs functionality."""
    print("Testing Contract Logs...")
    
    # Create test contract
    contract_data = {
        "id": "test.01",
        "title": "Test Contract",
        "description": "A test contract"
    }
    
    client.post("/contracts", json=contract_data)
    
    # Create log entry
    log_data = {
        "action": "test_action",
        "agent_role": "worker",
        "agent_id": "test_agent",
        "notes": "Test log entry"
    }
    
    response = client.post("/contracts/test.01/logs", json=log_data)
    assert response.status_code == 200
    
    data = response.json()
    assert data["action"] == "test_action"
    assert data["agent_role"] == "worker"
    assert data["agent_id"] == "test_agent"
    
    # Get logs
    response = client.get("/contracts/test.01/logs")
    assert response.status_code == 200
    
    data = response.json()
    assert "logs" in data
    assert len(data["logs"]) > 0
    
    print("✅ Contract logs validated")


def test_contract_statistics(setup_database):
    """Test contract statistics endpoint."""
    print("Testing Contract Statistics...")
    
    # Create test contracts with different statuses
    contracts_data = [
        {
            "id": "test.01",
            "title": "Test Contract 1",
            "description": "Pending contract"
        },
        {
            "id": "test.02",
            "title": "Test Contract 2",
            "description": "In progress contract"
        }
    ]
    
    for contract_data in contracts_data:
        client.post("/contracts", json=contract_data)
    
    # Update one contract to in_progress
    status_data = {"status": "in_progress", "progress_percentage": 50}
    client.patch("/contracts/test.02/status", json=status_data)
    
    # Get statistics
    response = client.get("/statistics/contracts")
    assert response.status_code == 200
    
    data = response.json()
    assert "total_contracts" in data
    assert "status_distribution" in data
    assert "recent_activity" in data
    assert data["total_contracts"] == 2
    
    print("✅ Contract statistics validated")


def test_agent_statistics(setup_database):
    """Test agent statistics endpoint."""
    print("Testing Agent Statistics...")
    
    # Create test contract
    contract_data = {
        "id": "test.01",
        "title": "Test Contract",
        "description": "A test contract"
    }
    
    client.post("/contracts", json=contract_data)
    
    # Assign contract
    assignment_data = {"assigned_to": "worker_agent"}
    client.patch("/contracts/test.01/assign", json=assignment_data)
    
    # Get agent statistics
    response = client.get("/statistics/agents")
    assert response.status_code == 200
    
    data = response.json()
    assert "agent_assignments" in data
    assert "agent_activity" in data
    assert "worker_agent" in data["agent_assignments"]
    
    print("✅ Agent statistics validated")


def test_error_handling(setup_database):
    """Test error handling."""
    print("Testing Error Handling...")
    
    # Test non-existent contract
    response = client.get("/contracts/nonexistent")
    assert response.status_code == 404
    
    # Test invalid contract creation
    invalid_data = {
        "id": "test.01",
        "title": "",  # Invalid empty title
        "description": "A test contract"
    }
    
    response = client.post("/contracts", json=invalid_data)
    assert response.status_code == 422  # Validation error
    
    # Test duplicate contract creation
    contract_data = {
        "id": "test.01",
        "title": "Test Contract",
        "description": "A test contract"
    }
    
    client.post("/contracts", json=contract_data)
    
    # Try to create duplicate
    response = client.post("/contracts", json=contract_data)
    assert response.status_code == 409  # Conflict
    
    print("✅ Error handling validated")


def test_pagination(setup_database):
    """Test pagination functionality."""
    print("Testing Pagination...")
    
    # Create multiple test contracts
    for i in range(15):
        contract_data = {
            "id": f"test.{i:02d}",
            "title": f"Test Contract {i}",
            "description": f"Test contract {i}"
        }
        client.post("/contracts", json=contract_data)
    
    # Test pagination
    response = client.get("/contracts?page=1&page_size=10")
    assert response.status_code == 200
    
    data = response.json()
    assert len(data["contracts"]) == 10
    assert data["page"] == 1
    assert data["page_size"] == 10
    assert data["total_pages"] == 2
    
    # Test second page
    response = client.get("/contracts?page=2&page_size=10")
    assert response.status_code == 200
    
    data = response.json()
    assert len(data["contracts"]) == 5  # Remaining contracts
    assert data["page"] == 2
    
    print("✅ Pagination validated")


def test_filtering(setup_database):
    """Test contract filtering."""
    print("Testing Filtering...")
    
    # Create test contracts with different statuses
    contracts_data = [
        {
            "id": "test.01",
            "title": "Pending Contract",
            "description": "A pending contract"
        },
        {
            "id": "test.02",
            "title": "In Progress Contract",
            "description": "An in progress contract"
        }
    ]
    
    for contract_data in contracts_data:
        client.post("/contracts", json=contract_data)
    
    # Update second contract to in_progress
    status_data = {"status": "in_progress", "progress_percentage": 50}
    client.patch("/contracts/test.02/status", json=status_data)
    
    # Test status filtering
    response = client.get("/contracts?status=pending")
    assert response.status_code == 200
    
    data = response.json()
    assert len(data["contracts"]) == 1
    assert data["contracts"][0]["status"] == "pending"
    
    # Test search filtering
    response = client.get("/contracts?search=Progress")
    assert response.status_code == 200
    
    data = response.json()
    assert len(data["contracts"]) == 1
    assert "Progress" in data["contracts"][0]["title"]
    
    print("✅ Filtering validated")


def main():
    """Run all API tests."""
    print("🧪 Testing Contracts API...\n")
    
    # Import pytest and run tests
    try:
        import pytest
        pytest.main([__file__, "-v"])
        print("\n🎉 All API tests completed!")
        return True
    except ImportError:
        print("❌ pytest not available. Install with: pip install pytest")
        return False
    except Exception as e:
        print(f"❌ Test execution failed: {e}")
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
