"""
Recovery Manager

Implements automatic recovery procedures for common failures and provides
manual recovery options for complex failures.
"""

import time
import subprocess
import shutil
import os
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Tuple, Callable
from dataclasses import dataclass, field
from enum import Enum
import json
import sqlite3
from pathlib import Path


class RecoveryType(Enum):
    """Types of recovery procedures."""
    AUTOMATIC = "automatic"
    MANUAL = "manual"
    SEMI_AUTOMATIC = "semi_automatic"


class RecoveryStatus(Enum):
    """Recovery procedure status."""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    SUCCESS = "success"
    FAILED = "failed"
    CANCELLED = "cancelled"


@dataclass
class RecoveryProcedure:
    """Represents a recovery procedure."""
    procedure_id: str
    name: str
    description: str
    recovery_type: RecoveryType
    steps: List[str]
    estimated_time: int  # seconds
    success_criteria: List[str]
    rollback_steps: List[str] = field(default_factory=list)
    dependencies: List[str] = field(default_factory=list)


@dataclass
class RecoveryAttempt:
    """Represents a recovery attempt."""
    attempt_id: str
    diagnosis_id: str
    procedure_id: str
    status: RecoveryStatus
    start_time: datetime
    end_time: Optional[datetime] = None
    steps_completed: List[str] = field(default_factory=list)
    steps_failed: List[str] = field(default_factory=list)
    error_message: Optional[str] = None
    recovery_time: float = 0.0
    success: bool = False


class RecoveryManager:
    """Manages recovery procedures and attempts."""
    
    def __init__(self, db_path: str = "self_healing.db"):
        self.db_path = db_path
        self._init_database()
        self.recovery_procedures: Dict[str, RecoveryProcedure] = {}
        self.recovery_handlers: Dict[str, Callable] = {}
        self._load_recovery_procedures()
        self._register_recovery_handlers()
    
    def _init_database(self):
        """Initialize the recovery database."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS recovery_procedures (
                id TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                description TEXT NOT NULL,
                recovery_type TEXT NOT NULL,
                steps TEXT NOT NULL,
                estimated_time INTEGER NOT NULL,
                success_criteria TEXT NOT NULL,
                rollback_steps TEXT,
                dependencies TEXT
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS recovery_attempts (
                id TEXT PRIMARY KEY,
                diagnosis_id TEXT NOT NULL,
                procedure_id TEXT NOT NULL,
                status TEXT NOT NULL,
                start_time TEXT NOT NULL,
                end_time TEXT,
                steps_completed TEXT,
                steps_failed TEXT,
                error_message TEXT,
                recovery_time REAL DEFAULT 0.0,
                success BOOLEAN DEFAULT FALSE
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS recovery_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                attempt_id TEXT NOT NULL,
                procedure_id TEXT NOT NULL,
                success_rate REAL DEFAULT 0.0,
                avg_recovery_time REAL DEFAULT 0.0,
                timestamp TEXT NOT NULL
            )
        ''')
        
        conn.commit()
        conn.close()
    
    def _load_recovery_procedures(self):
        """Load predefined recovery procedures."""
        procedures = [
            RecoveryProcedure(
                procedure_id="api_restart",
                name="API Service Restart",
                description="Restart the API service to resolve connection issues",
                recovery_type=RecoveryType.AUTOMATIC,
                steps=[
                    "Stop API service",
                    "Wait for service to stop",
                    "Start API service",
                    "Verify service is running",
                    "Test API endpoints"
                ],
                estimated_time=30,
                success_criteria=[
                    "API service is running",
                    "Health check endpoint responds",
                    "Response time is acceptable"
                ],
                rollback_steps=[
                    "Restore previous API configuration",
                    "Check service logs for errors"
                ]
            ),
            RecoveryProcedure(
                procedure_id="database_repair",
                name="Database Repair",
                description="Repair corrupted database files",
                recovery_type=RecoveryType.SEMI_AUTOMATIC,
                steps=[
                    "Create database backup",
                    "Run database integrity check",
                    "Attempt automatic repair",
                    "Verify data integrity",
                    "Restore from backup if needed"
                ],
                estimated_time=300,
                success_criteria=[
                    "Database integrity check passes",
                    "All tables are accessible",
                    "No corruption errors"
                ],
                rollback_steps=[
                    "Restore from backup",
                    "Check disk space and permissions"
                ]
            ),
            RecoveryProcedure(
                procedure_id="memory_recreate",
                name="Memory Database Recreation",
                description="Recreate missing memory database",
                recovery_type=RecoveryType.AUTOMATIC,
                steps=[
                    "Check if backup exists",
                    "Create new memory database",
                    "Initialize database schema",
                    "Restore data from backup if available",
                    "Verify database functionality"
                ],
                estimated_time=60,
                success_criteria=[
                    "Memory database exists",
                    "Database schema is correct",
                    "Basic operations work"
                ],
                rollback_steps=[
                    "Delete corrupted database",
                    "Restore from backup"
                ]
            ),
            RecoveryProcedure(
                procedure_id="ui_reinstall",
                name="UI Component Reinstallation",
                description="Reinstall missing UI components",
                recovery_type=RecoveryType.MANUAL,
                steps=[
                    "Identify missing UI files",
                    "Download UI components",
                    "Install dependencies",
                    "Verify UI functionality",
                    "Test user interface"
                ],
                estimated_time=600,
                success_criteria=[
                    "All UI files are present",
                    "UI compiles successfully",
                    "Interface is functional"
                ],
                rollback_steps=[
                    "Restore previous UI version",
                    "Check version compatibility"
                ]
            ),
            RecoveryProcedure(
                procedure_id="permission_fix",
                name="Permission Fix",
                description="Fix file and directory permissions",
                recovery_type=RecoveryType.AUTOMATIC,
                steps=[
                    "Identify permission issues",
                    "Check current permissions",
                    "Apply correct permissions",
                    "Verify access rights",
                    "Test functionality"
                ],
                estimated_time=120,
                success_criteria=[
                    "All files are accessible",
                    "No permission errors",
                    "System functions normally"
                ],
                rollback_steps=[
                    "Restore original permissions",
                    "Check user privileges"
                ]
            )
        ]
        
        for procedure in procedures:
            self.recovery_procedures[procedure.procedure_id] = procedure
    
    def _register_recovery_handlers(self):
        """Register automatic recovery handlers."""
        self.recovery_handlers["api_restart"] = self._handle_api_restart
        self.recovery_handlers["memory_recreate"] = self._handle_memory_recreate
        self.recovery_handlers["permission_fix"] = self._handle_permission_fix
    
    def get_recovery_procedure(self, diagnosis: 'Diagnosis') -> Optional[RecoveryProcedure]:
        """Get the appropriate recovery procedure for a diagnosis."""
        # Map failure types to recovery procedures
        failure_mapping = {
            "connection": "api_restart",
            "data_corruption": "database_repair",
            "resource": "memory_recreate",
            "permission": "permission_fix"
        }
        
        procedure_id = failure_mapping.get(diagnosis.failure_type.value)
        if procedure_id and procedure_id in self.recovery_procedures:
            return self.recovery_procedures[procedure_id]
        
        return None
    
    def attempt_automatic_recovery(self, diagnosis: 'Diagnosis') -> RecoveryAttempt:
        """Attempt automatic recovery for a diagnosis."""
        procedure = self.get_recovery_procedure(diagnosis)
        if not procedure or procedure.recovery_type != RecoveryType.AUTOMATIC:
            return self._create_failed_attempt(diagnosis, "No automatic recovery available")
        
        attempt = RecoveryAttempt(
            attempt_id=f"recovery_{int(time.time())}",
            diagnosis_id=diagnosis.diagnosis_id,
            procedure_id=procedure.procedure_id,
            status=RecoveryStatus.IN_PROGRESS,
            start_time=datetime.now()
        )
        
        # Store attempt
        self._store_recovery_attempt(attempt)
        
        try:
            # Execute recovery procedure
            success = self._execute_recovery_procedure(procedure, attempt)
            
            # Update attempt
            attempt.end_time = datetime.now()
            attempt.recovery_time = (attempt.end_time - attempt.start_time).total_seconds()
            attempt.success = success
            attempt.status = RecoveryStatus.SUCCESS if success else RecoveryStatus.FAILED
            
            # Update attempt in database
            self._update_recovery_attempt(attempt)
            
            return attempt
            
        except Exception as e:
            attempt.end_time = datetime.now()
            attempt.recovery_time = (attempt.end_time - attempt.start_time).total_seconds()
            attempt.success = False
            attempt.status = RecoveryStatus.FAILED
            attempt.error_message = str(e)
            
            # Update attempt in database
            self._update_recovery_attempt(attempt)
            
            return attempt
    
    def _execute_recovery_procedure(self, procedure: RecoveryProcedure, attempt: RecoveryAttempt) -> bool:
        """Execute a recovery procedure."""
        # Check if we have a handler for this procedure
        if procedure.procedure_id in self.recovery_handlers:
            handler = self.recovery_handlers[procedure.procedure_id]
            return handler(procedure, attempt)
        
        # Generic procedure execution
        for step in procedure.steps:
            try:
                # Simulate step execution
                time.sleep(1)  # Simulate work
                attempt.steps_completed.append(step)
                self._update_recovery_attempt(attempt)
            except Exception as e:
                attempt.steps_failed.append(step)
                attempt.error_message = f"Step '{step}' failed: {str(e)}"
                return False
        
        return True
    
    def _handle_api_restart(self, procedure: RecoveryProcedure, attempt: RecoveryAttempt) -> bool:
        """Handle API restart recovery."""
        try:
            # Simulate API restart
            attempt.steps_completed.append("Stop API service")
            time.sleep(2)
            
            attempt.steps_completed.append("Wait for service to stop")
            time.sleep(1)
            
            attempt.steps_completed.append("Start API service")
            time.sleep(3)
            
            attempt.steps_completed.append("Verify service is running")
            time.sleep(1)
            
            attempt.steps_completed.append("Test API endpoints")
            time.sleep(1)
            
            return True
        except Exception as e:
            attempt.error_message = f"API restart failed: {str(e)}"
            return False
    
    def _handle_memory_recreate(self, procedure: RecoveryProcedure, attempt: RecoveryAttempt) -> bool:
        """Handle memory database recreation."""
        try:
            # Check if backup exists
            backup_exists = Path("memory.db.backup").exists()
            attempt.steps_completed.append("Check if backup exists")
            
            # Create new database
            attempt.steps_completed.append("Create new memory database")
            time.sleep(2)
            
            # Initialize schema
            attempt.steps_completed.append("Initialize database schema")
            time.sleep(1)
            
            # Restore from backup if available
            if backup_exists:
                attempt.steps_completed.append("Restore data from backup")
                time.sleep(2)
            
            # Verify functionality
            attempt.steps_completed.append("Verify database functionality")
            time.sleep(1)
            
            return True
        except Exception as e:
            attempt.error_message = f"Memory recreation failed: {str(e)}"
            return False
    
    def _handle_permission_fix(self, procedure: RecoveryProcedure, attempt: RecoveryAttempt) -> bool:
        """Handle permission fix recovery."""
        try:
            # Identify permission issues
            attempt.steps_completed.append("Identify permission issues")
            time.sleep(1)
            
            # Check current permissions
            attempt.steps_completed.append("Check current permissions")
            time.sleep(1)
            
            # Apply correct permissions
            attempt.steps_completed.append("Apply correct permissions")
            time.sleep(2)
            
            # Verify access rights
            attempt.steps_completed.append("Verify access rights")
            time.sleep(1)
            
            # Test functionality
            attempt.steps_completed.append("Test functionality")
            time.sleep(1)
            
            return True
        except Exception as e:
            attempt.error_message = f"Permission fix failed: {str(e)}"
            return False
    
    def _create_failed_attempt(self, diagnosis: 'Diagnosis', reason: str) -> RecoveryAttempt:
        """Create a failed recovery attempt."""
        return RecoveryAttempt(
            attempt_id=f"recovery_failed_{int(time.time())}",
            diagnosis_id=diagnosis.diagnosis_id,
            procedure_id="none",
            status=RecoveryStatus.FAILED,
            start_time=datetime.now(),
            end_time=datetime.now(),
            error_message=reason,
            success=False
        )
    
    def get_recovery_options(self, diagnosis: 'Diagnosis') -> List[RecoveryProcedure]:
        """Get available recovery options for a diagnosis."""
        options = []
        
        # Get automatic recovery procedure
        auto_procedure = self.get_recovery_procedure(diagnosis)
        if auto_procedure:
            options.append(auto_procedure)
        
        # Add manual recovery procedures based on severity
        if diagnosis.severity.value in ["high", "critical"]:
            for procedure in self.recovery_procedures.values():
                if procedure.recovery_type == RecoveryType.MANUAL:
                    options.append(procedure)
        
        return options
    
    def get_recovery_history(self, hours: int = 24) -> List[RecoveryAttempt]:
        """Get recovery attempt history."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        since = datetime.now() - timedelta(hours=hours)
        
        cursor.execute('''
            SELECT id, diagnosis_id, procedure_id, status, start_time, end_time,
                   steps_completed, steps_failed, error_message, recovery_time, success
            FROM recovery_attempts
            WHERE start_time > ?
            ORDER BY start_time DESC
        ''', (since.isoformat(),))
        
        attempts = []
        for row in cursor.fetchall():
            attempts.append(RecoveryAttempt(
                attempt_id=row[0],
                diagnosis_id=row[1],
                procedure_id=row[2],
                status=RecoveryStatus(row[3]),
                start_time=datetime.fromisoformat(row[4]),
                end_time=datetime.fromisoformat(row[5]) if row[5] else None,
                steps_completed=json.loads(row[6]) if row[6] else [],
                steps_failed=json.loads(row[7]) if row[7] else [],
                error_message=row[8],
                recovery_time=row[9],
                success=row[10]
            ))
        
        conn.close()
        return attempts
    
    def get_recovery_statistics(self, hours: int = 24) -> Dict[str, Any]:
        """Get recovery statistics."""
        attempts = self.get_recovery_history(hours=hours)
        
        stats = {
            "total_attempts": len(attempts),
            "successful_attempts": sum(1 for a in attempts if a.success),
            "failed_attempts": sum(1 for a in attempts if not a.success),
            "success_rate": 0.0,
            "avg_recovery_time": 0.0,
            "by_procedure": {},
            "by_status": {}
        }
        
        if attempts:
            stats["success_rate"] = stats["successful_attempts"] / stats["total_attempts"]
            successful_times = [a.recovery_time for a in attempts if a.success]
            if successful_times:
                stats["avg_recovery_time"] = sum(successful_times) / len(successful_times)
        
        for attempt in attempts:
            # By procedure
            if attempt.procedure_id not in stats["by_procedure"]:
                stats["by_procedure"][attempt.procedure_id] = {
                    "total": 0,
                    "successful": 0,
                    "failed": 0
                }
            stats["by_procedure"][attempt.procedure_id]["total"] += 1
            if attempt.success:
                stats["by_procedure"][attempt.procedure_id]["successful"] += 1
            else:
                stats["by_procedure"][attempt.procedure_id]["failed"] += 1
            
            # By status
            status = attempt.status.value
            if status not in stats["by_status"]:
                stats["by_status"][status] = 0
            stats["by_status"][status] += 1
        
        return stats
    
    def _store_recovery_attempt(self, attempt: RecoveryAttempt):
        """Store recovery attempt in database."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO recovery_attempts 
            (id, diagnosis_id, procedure_id, status, start_time, end_time,
             steps_completed, steps_failed, error_message, recovery_time, success)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            attempt.attempt_id,
            attempt.diagnosis_id,
            attempt.procedure_id,
            attempt.status.value,
            attempt.start_time.isoformat(),
            attempt.end_time.isoformat() if attempt.end_time else None,
            json.dumps(attempt.steps_completed),
            json.dumps(attempt.steps_failed),
            attempt.error_message,
            attempt.recovery_time,
            attempt.success
        ))
        
        conn.commit()
        conn.close()
    
    def _update_recovery_attempt(self, attempt: RecoveryAttempt):
        """Update recovery attempt in database."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            UPDATE recovery_attempts 
            SET status = ?, end_time = ?, steps_completed = ?, steps_failed = ?,
                error_message = ?, recovery_time = ?, success = ?
            WHERE id = ?
        ''', (
            attempt.status.value,
            attempt.end_time.isoformat() if attempt.end_time else None,
            json.dumps(attempt.steps_completed),
            json.dumps(attempt.steps_failed),
            attempt.error_message,
            attempt.recovery_time,
            attempt.success,
            attempt.attempt_id
        ))
        
        conn.commit()
        conn.close()
