"""
SQLAlchemy models for contracts and contract logs.

Defines database schema with proper relationships, constraints,
and validation for the Contracts API.
"""

from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean, JSON, ForeignKey, Enum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from datetime import datetime
import enum

from .database import Base


class ContractStatus(enum.Enum):
    """Contract status enumeration."""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    AWAITING_REVIEW = "awaiting_review"
    COMPLETED = "completed"


class ContractRole(enum.Enum):
    """Contract role enumeration."""
    CAPTAIN = "captain"
    WORKER = "worker"
    TESTER = "tester"


class Contract(Base):
    """Contract model representing a contract in the system."""
    
    __tablename__ = "contracts"
    
    # Primary key
    id = Column(String(50), primary_key=True, index=True)
    
    # Basic contract information
    title = Column(String(200), nullable=False, index=True)
    description = Column(Text, nullable=False)
    
    # File and completion criteria
    allowed_files = Column(JSON, nullable=True)  # List of allowed file patterns
    completion_criteria = Column(JSON, nullable=True)  # List of completion criteria
    
    # Roles and responsibilities
    roles = Column(JSON, nullable=True)  # Role definitions and restrictions
    
    # Status and progress
    status = Column(Enum(ContractStatus), default=ContractStatus.PENDING, nullable=False, index=True)
    progress_percentage = Column(Integer, default=0, nullable=False)
    
    # Assignment and tracking
    assigned_to = Column(String(100), nullable=True, index=True)
    dependencies = Column(JSON, nullable=True)  # List of dependency contract IDs
    
    # Notes and coordination
    captain_notes = Column(Text, nullable=True)
    worker_notes = Column(Text, nullable=True)
    tester_notes = Column(Text, nullable=True)
    coordination_notes = Column(Text, nullable=True)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    
    # Relationships
    logs = relationship("ContractLog", back_populates="contract", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Contract(id='{self.id}', title='{self.title}', status='{self.status}')>"
    
    def to_dict(self):
        """Convert contract to dictionary for JSON serialization."""
        return {
            "id": self.id,
            "title": self.title,
            "description": self.description,
            "allowed_files": self.allowed_files,
            "completion_criteria": self.completion_criteria,
            "roles": self.roles,
            "status": self.status.value,
            "progress_percentage": self.progress_percentage,
            "assigned_to": self.assigned_to,
            "dependencies": self.dependencies,
            "captain_notes": self.captain_notes,
            "worker_notes": self.worker_notes,
            "tester_notes": self.tester_notes,
            "coordination_notes": self.coordination_notes,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None
        }


class ContractLog(Base):
    """Contract log model for tracking contract changes and actions."""
    
    __tablename__ = "contract_logs"
    
    # Primary key
    id = Column(Integer, primary_key=True, index=True)
    
    # Foreign key to contract
    contract_id = Column(String(50), ForeignKey("contracts.id"), nullable=False, index=True)
    
    # Log information
    action = Column(String(100), nullable=False, index=True)  # e.g., "status_change", "assignment", "progress_update"
    agent_role = Column(Enum(ContractRole), nullable=False, index=True)
    agent_id = Column(String(100), nullable=False, index=True)
    
    # Change details
    old_values = Column(JSON, nullable=True)  # Previous values
    new_values = Column(JSON, nullable=True)  # New values
    notes = Column(Text, nullable=True)
    
    # Metadata
    ip_address = Column(String(45), nullable=True)  # IPv4 or IPv6
    user_agent = Column(String(500), nullable=True)
    
    # Timestamp
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False, index=True)
    
    # Relationships
    contract = relationship("Contract", back_populates="logs")
    
    def __repr__(self):
        return f"<ContractLog(id={self.id}, contract_id='{self.contract_id}', action='{self.action}')>"
    
    def to_dict(self):
        """Convert log entry to dictionary for JSON serialization."""
        return {
            "id": self.id,
            "contract_id": self.contract_id,
            "action": self.action,
            "agent_role": self.agent_role.value,
            "agent_id": self.agent_id,
            "old_values": self.old_values,
            "new_values": self.new_values,
            "notes": self.notes,
            "ip_address": self.ip_address,
            "user_agent": self.user_agent,
            "created_at": self.created_at.isoformat() if self.created_at else None
        }


class APIAuditLog(Base):
    """API audit log for tracking API usage and security."""
    
    __tablename__ = "api_audit_logs"
    
    # Primary key
    id = Column(Integer, primary_key=True, index=True)
    
    # Request information
    endpoint = Column(String(200), nullable=False, index=True)
    method = Column(String(10), nullable=False, index=True)
    status_code = Column(Integer, nullable=False, index=True)
    
    # Authentication
    agent_id = Column(String(100), nullable=True, index=True)
    agent_role = Column(Enum(ContractRole), nullable=True, index=True)
    
    # Request details
    request_data = Column(JSON, nullable=True)
    response_data = Column(JSON, nullable=True)
    
    # Performance
    response_time_ms = Column(Integer, nullable=True)
    
    # Metadata
    ip_address = Column(String(45), nullable=True)
    user_agent = Column(String(500), nullable=True)
    
    # Timestamp
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False, index=True)
    
    def __repr__(self):
        return f"<APIAuditLog(id={self.id}, endpoint='{self.endpoint}', method='{self.method}')>"
    
    def to_dict(self):
        """Convert audit log to dictionary for JSON serialization."""
        return {
            "id": self.id,
            "endpoint": self.endpoint,
            "method": self.method,
            "status_code": self.status_code,
            "agent_id": self.agent_id,
            "agent_role": self.agent_role.value if self.agent_role else None,
            "request_data": self.request_data,
            "response_data": self.response_data,
            "response_time_ms": self.response_time_ms,
            "ip_address": self.ip_address,
            "user_agent": self.user_agent,
            "created_at": self.created_at.isoformat() if self.created_at else None
        }
