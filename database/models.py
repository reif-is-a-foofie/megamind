"""
Database Models - Contract Management Schema

Defines the SQLAlchemy models for contract management, including
contracts, contract logs, and related entities.
"""

from datetime import datetime
from typing import Optional, Dict, Any, List
from sqlalchemy import Column, Integer, String, Text, DateTime, JSON, Index, ForeignKey, Boolean, Enum
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
import enum

Base = declarative_base()


class ContractStatus(enum.Enum):
    """Contract status enumeration."""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    AWAITING_REVIEW = "awaiting_review"
    COMPLETED = "completed"
    CANCELLED = "cancelled"
    FAILED = "failed"


class ContractPriority(enum.Enum):
    """Contract priority enumeration."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    IMMEDIATE = "immediate"


class Contract(Base):
    """Represents a contract in the system."""
    __tablename__ = "contracts"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    contract_id = Column(String(50), unique=True, nullable=False, index=True)  # e.g., "memory.01"
    title = Column(String(200), nullable=False)
    description = Column(Text, nullable=True)
    
    # Contract metadata
    allowed_files = Column(JSON, nullable=True)  # List of allowed file patterns
    completion_criteria = Column(JSON, nullable=True)  # List of completion criteria
    dependencies = Column(JSON, nullable=True)  # List of dependency contract IDs
    
    # Status and assignment
    status = Column(Enum(ContractStatus), default=ContractStatus.PENDING, nullable=False, index=True)
    progress_percentage = Column(Integer, default=0, nullable=False)
    assigned_to = Column(String(100), nullable=True, index=True)
    priority = Column(Enum(ContractPriority), default=ContractPriority.MEDIUM, nullable=False, index=True)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    started_at = Column(DateTime, nullable=True)
    completed_at = Column(DateTime, nullable=True)
    
    # Notes and coordination
    captain_notes = Column(Text, nullable=True)
    worker_notes = Column(Text, nullable=True)
    tester_notes = Column(Text, nullable=True)
    coordination_notes = Column(Text, nullable=True)
    
    # Additional metadata
    contract_metadata = Column(JSON, nullable=True)  # Additional contract data
    
    # Relationships
    logs = relationship("ContractLog", back_populates="contract", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Contract(id={self.id}, contract_id='{self.contract_id}', title='{self.title}', status='{self.status.value}')>"
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert contract to dictionary format."""
        return {
            "id": self.contract_id,
            "title": self.title,
            "description": self.description,
            "allowed_files": self.allowed_files,
            "completion_criteria": self.completion_criteria,
            "dependencies": self.dependencies,
            "status": self.status.value,
            "progress_percentage": self.progress_percentage,
            "assigned_to": self.assigned_to,
            "priority": self.priority.value,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
            "started_at": self.started_at.isoformat() if self.started_at else None,
            "completed_at": self.completed_at.isoformat() if self.completed_at else None,
            "captain_notes": self.captain_notes,
            "worker_notes": self.worker_notes,
            "tester_notes": self.tester_notes,
            "coordination_notes": self.coordination_notes,
            "metadata": self.contract_metadata
        }


class ContractLog(Base):
    """Represents a log entry for contract activities."""
    __tablename__ = "contract_logs"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    contract_id = Column(Integer, ForeignKey("contracts.id"), nullable=False, index=True)
    
    # Log entry details
    action = Column(String(100), nullable=False, index=True)  # e.g., "status_change", "assignment", "progress_update"
    actor = Column(String(100), nullable=False, index=True)  # e.g., "captain", "worker", "tester", "system"
    message = Column(Text, nullable=True)
    
    # Data changes
    old_values = Column(JSON, nullable=True)  # Previous values
    new_values = Column(JSON, nullable=True)  # New values
    
    # Timestamp
    timestamp = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)
    
    # Additional context
    log_metadata = Column(JSON, nullable=True)  # Additional log data
    
    # Relationships
    contract = relationship("Contract", back_populates="logs")
    
    def __repr__(self):
        return f"<ContractLog(id={self.id}, contract_id={self.contract_id}, action='{self.action}', actor='{self.actor}')>"
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert log entry to dictionary format."""
        return {
            "id": self.id,
            "contract_id": self.contract_id,
            "action": self.action,
            "actor": self.actor,
            "message": self.message,
            "old_values": self.old_values,
            "new_values": self.new_values,
            "timestamp": self.timestamp.isoformat() if self.timestamp else None,
            "metadata": self.log_metadata
        }


class SystemConfig(Base):
    """Represents system configuration settings."""
    __tablename__ = "system_config"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    key = Column(String(100), unique=True, nullable=False, index=True)
    value = Column(Text, nullable=True)
    value_type = Column(String(50), nullable=False, default="string")  # string, int, float, bool, json
    description = Column(Text, nullable=True)
    is_encrypted = Column(Boolean, default=False, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    def __repr__(self):
        return f"<SystemConfig(id={self.id}, key='{self.key}', value_type='{self.value_type}')>"


# Performance indexes
Index("idx_contracts_status_priority", Contract.status, Contract.priority)
Index("idx_contracts_assigned_status", Contract.assigned_to, Contract.status)
Index("idx_contracts_created_updated", Contract.created_at, Contract.updated_at)
Index("idx_contract_logs_contract_timestamp", ContractLog.contract_id, ContractLog.timestamp)
Index("idx_contract_logs_action_actor", ContractLog.action, ContractLog.actor)
