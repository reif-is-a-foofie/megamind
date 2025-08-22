"""
Contracts API - FastAPI service for intelligent contract management.

Provides RESTful API endpoints for contract operations with Postgres backend,
authentication, rate limiting, and seamless agent integration.
"""

from .main import app
from .models import Contract, ContractLog, ContractStatus, ContractRole
from .database import get_db, engine
from .schemas import ContractCreate, ContractUpdate, ContractResponse

__all__ = ["app", "Contract", "ContractLog", "ContractStatus", "ContractRole", "get_db", "engine", "ContractCreate", "ContractUpdate", "ContractResponse"]
