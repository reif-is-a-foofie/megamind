"""
Pydantic schemas for API request/response validation.

Defines data models for API endpoints with validation, documentation,
and type safety for the Contracts API.
"""

from pydantic import BaseModel, Field, validator
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum


class ContractStatusEnum(str, Enum):
    """Contract status enumeration for API."""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    AWAITING_REVIEW = "awaiting_review"
    COMPLETED = "completed"


class ContractRoleEnum(str, Enum):
    """Contract role enumeration for API."""
    CAPTAIN = "captain"
    WORKER = "worker"
    TESTER = "tester"


class ContractBase(BaseModel):
    """Base contract schema with common fields."""
    
    title: str = Field(..., min_length=1, max_length=200, description="Contract title")
    description: str = Field(..., min_length=1, description="Contract description")
    allowed_files: Optional[List[str]] = Field(None, description="List of allowed file patterns")
    completion_criteria: Optional[List[str]] = Field(None, description="List of completion criteria")
    roles: Optional[Dict[str, Any]] = Field(None, description="Role definitions and restrictions")
    dependencies: Optional[List[str]] = Field(None, description="List of dependency contract IDs")
    coordination_notes: Optional[str] = Field(None, description="Coordination notes")


class ContractCreate(ContractBase):
    """Schema for creating a new contract."""
    
    id: str = Field(..., min_length=1, max_length=50, description="Unique contract identifier")
    
    @validator('id')
    def validate_id_format(cls, v):
        """Validate contract ID format."""
        if not v.replace('.', '').replace('_', '').isalnum():
            raise ValueError('Contract ID must contain only alphanumeric characters, dots, and underscores')
        return v


class ContractUpdate(BaseModel):
    """Schema for updating an existing contract."""
    
    title: Optional[str] = Field(None, min_length=1, max_length=200)
    description: Optional[str] = Field(None, min_length=1)
    allowed_files: Optional[List[str]] = None
    completion_criteria: Optional[List[str]] = None
    roles: Optional[Dict[str, Any]] = None
    status: Optional[ContractStatusEnum] = None
    progress_percentage: Optional[int] = Field(None, ge=0, le=100)
    assigned_to: Optional[str] = Field(None, max_length=100)
    dependencies: Optional[List[str]] = None
    captain_notes: Optional[str] = None
    worker_notes: Optional[str] = None
    tester_notes: Optional[str] = None
    coordination_notes: Optional[str] = None


class ContractResponse(ContractBase):
    """Schema for contract response."""
    
    id: str
    status: ContractStatusEnum
    progress_percentage: int = Field(..., ge=0, le=100)
    assigned_to: Optional[str] = None
    captain_notes: Optional[str] = None
    worker_notes: Optional[str] = None
    tester_notes: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    
    class Config:
        orm_mode = True


class ContractLogBase(BaseModel):
    """Base contract log schema."""
    
    action: str = Field(..., min_length=1, max_length=100, description="Action performed")
    agent_role: ContractRoleEnum
    agent_id: str = Field(..., min_length=1, max_length=100, description="Agent identifier")
    notes: Optional[str] = Field(None, description="Additional notes")


class ContractLogCreate(ContractLogBase):
    """Schema for creating a contract log entry."""
    
    contract_id: str = Field(..., min_length=1, max_length=50)
    old_values: Optional[Dict[str, Any]] = None
    new_values: Optional[Dict[str, Any]] = None


class ContractLogResponse(ContractLogBase):
    """Schema for contract log response."""
    
    id: int
    contract_id: str
    old_values: Optional[Dict[str, Any]] = None
    new_values: Optional[Dict[str, Any]] = None
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None
    created_at: datetime
    
    class Config:
        orm_mode = True


class StatusUpdateRequest(BaseModel):
    """Schema for status update requests."""
    
    status: ContractStatusEnum
    progress_percentage: Optional[int] = Field(None, ge=0, le=100)
    notes: Optional[str] = None


class AssignmentRequest(BaseModel):
    """Schema for contract assignment requests."""
    
    assigned_to: str = Field(..., min_length=1, max_length=100)
    notes: Optional[str] = None


class ProgressUpdateRequest(BaseModel):
    """Schema for progress update requests."""
    
    progress_percentage: int = Field(..., ge=0, le=100)
    notes: Optional[str] = None


class ContractListResponse(BaseModel):
    """Schema for contract list response."""
    
    contracts: List[ContractResponse]
    total_count: int
    page: int
    page_size: int
    total_pages: int


class ContractLogListResponse(BaseModel):
    """Schema for contract log list response."""
    
    logs: List[ContractLogResponse]
    total_count: int
    page: int
    page_size: int
    total_pages: int


class HealthCheckResponse(BaseModel):
    """Schema for health check response."""
    
    status: str
    timestamp: datetime
    database: Dict[str, Any]
    version: str = "1.0.0"


class ErrorResponse(BaseModel):
    """Schema for error responses."""
    
    error: str
    detail: Optional[str] = None
    timestamp: datetime = Field(default_factory=datetime.now)


class PaginationParams(BaseModel):
    """Schema for pagination parameters."""
    
    page: int = Field(1, ge=1, description="Page number")
    page_size: int = Field(50, ge=1, le=100, description="Items per page")


class ContractFilterParams(BaseModel):
    """Schema for contract filtering parameters."""
    
    status: Optional[ContractStatusEnum] = None
    assigned_to: Optional[str] = None
    search: Optional[str] = Field(None, description="Search in title and description")
    created_after: Optional[datetime] = None
    created_before: Optional[datetime] = None


class APIAuditLogResponse(BaseModel):
    """Schema for API audit log response."""
    
    id: int
    endpoint: str
    method: str
    status_code: int
    agent_id: Optional[str] = None
    agent_role: Optional[ContractRoleEnum] = None
    response_time_ms: Optional[int] = None
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None
    created_at: datetime
    
    class Config:
        orm_mode = True
