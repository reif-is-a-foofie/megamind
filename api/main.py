"""
Main FastAPI application for Contracts API.

Provides RESTful endpoints for contract management with authentication,
rate limiting, comprehensive logging, and error handling.
"""

from fastapi import FastAPI, Depends, HTTPException, status, Request, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, desc, func
import time
import logging
from typing import List, Optional
from datetime import datetime, timedelta

from .database import get_db, init_db, check_db_connection, get_db_info
from .models import Contract, ContractLog, APIAuditLog, ContractStatus, ContractRole
from .schemas import (
    ContractCreate, ContractUpdate, ContractResponse, ContractListResponse,
    ContractLogCreate, ContractLogResponse, ContractLogListResponse,
    StatusUpdateRequest, AssignmentRequest, ProgressUpdateRequest,
    HealthCheckResponse, ErrorResponse, PaginationParams, ContractFilterParams,
    APIAuditLogResponse
)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(
    title="Contracts API",
    description="RESTful API for intelligent contract management with agent integration",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Add middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.add_middleware(
    TrustedHostMiddleware,
    allowed_hosts=["*"]  # Configure appropriately for production
)


# Rate limiting storage (in production, use Redis)
rate_limit_storage = {}


def check_rate_limit(request: Request, agent_id: str):
    """Simple rate limiting implementation."""
    current_time = time.time()
    key = f"{agent_id}:{request.client.host}"
    
    if key in rate_limit_storage:
        last_request, count = rate_limit_storage[key]
        if current_time - last_request < 60:  # 1 minute window
            if count >= 100:  # 100 requests per minute
                raise HTTPException(
                    status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                    detail="Rate limit exceeded"
                )
            rate_limit_storage[key] = (last_request, count + 1)
        else:
            rate_limit_storage[key] = (current_time, 1)
    else:
        rate_limit_storage[key] = (current_time, 1)


def log_api_request(request: Request, response, agent_id: str = None, agent_role: str = None):
    """Log API request for audit purposes."""
    try:
        db = next(get_db())
        audit_log = APIAuditLog(
            endpoint=str(request.url.path),
            method=request.method,
            status_code=response.status_code,
            agent_id=agent_id,
            agent_role=ContractRole(agent_role) if agent_role else None,
            ip_address=request.client.host,
            user_agent=request.headers.get("user-agent"),
            response_time_ms=int((time.time() - request.state.start_time) * 1000)
        )
        db.add(audit_log)
        db.commit()
    except Exception as e:
        logger.error(f"Error logging API request: {e}")


@app.middleware("http")
async def add_process_time_header(request: Request, call_next):
    """Add processing time header and log requests."""
    request.state.start_time = time.time()
    
    # Extract agent info from headers
    agent_id = request.headers.get("X-Agent-ID")
    agent_role = request.headers.get("X-Agent-Role")
    
    # Check rate limit
    if agent_id:
        check_rate_limit(request, agent_id)
    
    response = await call_next(request)
    
    # Log request
    log_api_request(request, response, agent_id, agent_role)
    
    return response


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Global exception handler."""
    logger.error(f"Unhandled exception: {exc}")
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "error": "Internal server error",
            "detail": str(exc),
            "timestamp": datetime.now().isoformat()
        }
    )


# Health check endpoint
@app.get("/health", response_model=HealthCheckResponse)
async def health_check():
    """Health check endpoint."""
    db_status = check_db_connection()
    db_info = get_db_info()
    
    return HealthCheckResponse(
        status="healthy" if db_status else "unhealthy",
        timestamp=datetime.now(),
        database=db_info
    )


# Contract endpoints
@app.get("/contracts", response_model=ContractListResponse)
async def get_contracts(
    page: int = 1,
    page_size: int = 50,
    status: Optional[ContractStatus] = None,
    assigned_to: Optional[str] = None,
    search: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """Get contracts with filtering and pagination."""
    query = db.query(Contract)
    
    # Apply filters
    if status:
        query = query.filter(Contract.status == status)
    if assigned_to:
        query = query.filter(Contract.assigned_to == assigned_to)
    if search:
        search_filter = or_(
            Contract.title.ilike(f"%{search}%"),
            Contract.description.ilike(f"%{search}%")
        )
        query = query.filter(search_filter)
    
    # Get total count
    total_count = query.count()
    
    # Apply pagination
    offset = (page - 1) * page_size
    contracts = query.offset(offset).limit(page_size).all()
    
    # Convert to response models
    contract_responses = [ContractResponse.from_orm(contract) for contract in contracts]
    
    return ContractListResponse(
        contracts=contract_responses,
        total_count=total_count,
        page=page,
        page_size=page_size,
        total_pages=(total_count + page_size - 1) // page_size
    )


@app.get("/contracts/{contract_id}", response_model=ContractResponse)
async def get_contract(contract_id: str, db: Session = Depends(get_db)):
    """Get a specific contract by ID."""
    contract = db.query(Contract).filter(Contract.id == contract_id).first()
    if not contract:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Contract {contract_id} not found"
        )
    return ContractResponse.from_orm(contract)


@app.post("/contracts", response_model=ContractResponse, status_code=status.HTTP_201_CREATED)
async def create_contract(
    contract: ContractCreate,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    """Create a new contract."""
    # Check if contract already exists
    existing = db.query(Contract).filter(Contract.id == contract.id).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Contract {contract.id} already exists"
        )
    
    # Create contract
    db_contract = Contract(**contract.dict())
    db.add(db_contract)
    
    # Create log entry
    log_entry = ContractLog(
        contract_id=contract.id,
        action="contract_created",
        agent_role=ContractRole.CAPTAIN,  # Default to captain for creation
        agent_id="system",
        notes="Contract created via API"
    )
    db.add(log_entry)
    
    db.commit()
    db.refresh(db_contract)
    
    return ContractResponse.from_orm(db_contract)


@app.put("/contracts/{contract_id}", response_model=ContractResponse)
async def update_contract(
    contract_id: str,
    contract_update: ContractUpdate,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    """Update an existing contract."""
    db_contract = db.query(Contract).filter(Contract.id == contract_id).first()
    if not db_contract:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Contract {contract_id} not found"
        )
    
    # Store old values for logging
    old_values = db_contract.to_dict()
    
    # Update contract
    update_data = contract_update.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_contract, field, value)
    
    # Create log entry
    log_entry = ContractLog(
        contract_id=contract_id,
        action="contract_updated",
        agent_role=ContractRole.CAPTAIN,  # Default to captain for updates
        agent_id="system",
        old_values=old_values,
        new_values=db_contract.to_dict(),
        notes="Contract updated via API"
    )
    db.add(log_entry)
    
    db.commit()
    db.refresh(db_contract)
    
    return ContractResponse.from_orm(db_contract)


@app.delete("/contracts/{contract_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_contract(
    contract_id: str,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    """Delete a contract."""
    db_contract = db.query(Contract).filter(Contract.id == contract_id).first()
    if not db_contract:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Contract {contract_id} not found"
        )
    
    # Create log entry before deletion
    log_entry = ContractLog(
        contract_id=contract_id,
        action="contract_deleted",
        agent_role=ContractRole.CAPTAIN,
        agent_id="system",
        notes="Contract deleted via API"
    )
    db.add(log_entry)
    
    db.delete(db_contract)
    db.commit()


# Status update endpoint
@app.patch("/contracts/{contract_id}/status", response_model=ContractResponse)
async def update_contract_status(
    contract_id: str,
    status_update: StatusUpdateRequest,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    """Update contract status and progress."""
    db_contract = db.query(Contract).filter(Contract.id == contract_id).first()
    if not db_contract:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Contract {contract_id} not found"
        )
    
    # Store old values
    old_values = {
        "status": db_contract.status.value,
        "progress_percentage": db_contract.progress_percentage
    }
    
    # Update status and progress
    db_contract.status = status_update.status
    if status_update.progress_percentage is not None:
        db_contract.progress_percentage = status_update.progress_percentage
    
    # Create log entry
    log_entry = ContractLog(
        contract_id=contract_id,
        action="status_update",
        agent_role=ContractRole.WORKER,  # Default to worker for status updates
        agent_id="system",
        old_values=old_values,
        new_values={
            "status": status_update.status.value,
            "progress_percentage": status_update.progress_percentage
        },
        notes=status_update.notes
    )
    db.add(log_entry)
    
    db.commit()
    db.refresh(db_contract)
    
    return ContractResponse.from_orm(db_contract)


# Assignment endpoint
@app.patch("/contracts/{contract_id}/assign", response_model=ContractResponse)
async def assign_contract(
    contract_id: str,
    assignment: AssignmentRequest,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    """Assign a contract to an agent."""
    db_contract = db.query(Contract).filter(Contract.id == contract_id).first()
    if not db_contract:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Contract {contract_id} not found"
        )
    
    # Store old value
    old_assigned_to = db_contract.assigned_to
    
    # Update assignment
    db_contract.assigned_to = assignment.assigned_to
    
    # Create log entry
    log_entry = ContractLog(
        contract_id=contract_id,
        action="contract_assigned",
        agent_role=ContractRole.CAPTAIN,
        agent_id="system",
        old_values={"assigned_to": old_assigned_to},
        new_values={"assigned_to": assignment.assigned_to},
        notes=assignment.notes
    )
    db.add(log_entry)
    
    db.commit()
    db.refresh(db_contract)
    
    return ContractResponse.from_orm(db_contract)


# Contract logs endpoints
@app.get("/contracts/{contract_id}/logs", response_model=ContractLogListResponse)
async def get_contract_logs(
    contract_id: str,
    page: int = 1,
    page_size: int = 50,
    db: Session = Depends(get_db)
):
    """Get logs for a specific contract."""
    # Verify contract exists
    contract = db.query(Contract).filter(Contract.id == contract_id).first()
    if not contract:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Contract {contract_id} not found"
        )
    
    # Get logs
    query = db.query(ContractLog).filter(ContractLog.contract_id == contract_id)
    total_count = query.count()
    
    # Apply pagination
    offset = (page - 1) * page_size
    logs = query.order_by(desc(ContractLog.created_at)).offset(offset).limit(page_size).all()
    
    # Convert to response models
    log_responses = [ContractLogResponse.from_orm(log) for log in logs]
    
    return ContractLogListResponse(
        logs=log_responses,
        total_count=total_count,
        page=page,
        page_size=page_size,
        total_pages=(total_count + page_size - 1) // page_size
    )


@app.post("/contracts/{contract_id}/logs", response_model=ContractLogResponse)
async def create_contract_log(
    contract_id: str,
    log_entry: ContractLogCreate,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    """Create a log entry for a contract."""
    # Verify contract exists
    contract = db.query(Contract).filter(Contract.id == contract_id).first()
    if not contract:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Contract {contract_id} not found"
        )
    
    # Create log entry
    db_log = ContractLog(**log_entry.dict())
    db.add(db_log)
    db.commit()
    db.refresh(db_log)
    
    return ContractLogResponse.from_orm(db_log)


# Statistics endpoints
@app.get("/statistics/contracts")
async def get_contract_statistics(db: Session = Depends(get_db)):
    """Get contract statistics."""
    total_contracts = db.query(Contract).count()
    
    # Status distribution
    status_counts = db.query(
        Contract.status,
        func.count(Contract.id)
    ).group_by(Contract.status).all()
    
    # Recent activity
    week_ago = datetime.now() - timedelta(days=7)
    recent_logs = db.query(ContractLog).filter(
        ContractLog.created_at >= week_ago
    ).count()
    
    return {
        "total_contracts": total_contracts,
        "status_distribution": {status.value: count for status, count in status_counts},
        "recent_activity": recent_logs,
        "last_updated": datetime.now().isoformat()
    }


@app.get("/statistics/agents")
async def get_agent_statistics(db: Session = Depends(get_db)):
    """Get agent activity statistics."""
    # Agent assignment counts
    agent_counts = db.query(
        Contract.assigned_to,
        func.count(Contract.id)
    ).filter(Contract.assigned_to.isnot(None)).group_by(Contract.assigned_to).all()
    
    # Agent activity in logs
    agent_activity = db.query(
        ContractLog.agent_id,
        ContractLog.agent_role,
        func.count(ContractLog.id)
    ).group_by(ContractLog.agent_id, ContractLog.agent_role).all()
    
    return {
        "agent_assignments": {agent: count for agent, count in agent_counts},
        "agent_activity": [
            {
                "agent_id": agent_id,
                "role": role.value,
                "action_count": count
            }
            for agent_id, role, count in agent_activity
        ],
        "last_updated": datetime.now().isoformat()
    }


# Initialize database on startup
@app.on_event("startup")
async def startup_event():
    """Initialize database on startup."""
    try:
        init_db()
        logger.info("Database initialized successfully")
    except Exception as e:
        logger.error(f"Error initializing database: {e}")
        raise
