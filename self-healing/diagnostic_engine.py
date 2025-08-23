"""
Diagnostic Engine

Automatically diagnoses root causes of failures and provides
detailed analysis for recovery procedures.
"""

import time
import re
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, field
from enum import Enum
import json
import sqlite3
from pathlib import Path


class FailureType(Enum):
    """Types of system failures."""
    CONNECTION = "connection"
    PERMISSION = "permission"
    RESOURCE = "resource"
    CONFIGURATION = "configuration"
    TIMEOUT = "timeout"
    DATA_CORRUPTION = "data_corruption"
    MEMORY_LEAK = "memory_leak"
    THREAD_DEADLOCK = "thread_deadlock"
    UNKNOWN = "unknown"


class Severity(Enum):
    """Failure severity levels."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


@dataclass
class FailurePattern:
    """Represents a failure pattern for diagnosis."""
    pattern_id: str
    failure_type: FailureType
    severity: Severity
    symptoms: List[str]
    root_causes: List[str]
    recovery_steps: List[str]
    prevention_tips: List[str]
    confidence: float = 0.0


@dataclass
class Diagnosis:
    """Represents a failure diagnosis."""
    diagnosis_id: str
    component: str
    failure_type: FailureType
    severity: Severity
    root_cause: str
    confidence: float
    symptoms: List[str]
    recovery_plan: List[str]
    timestamp: datetime
    details: Dict[str, Any] = field(default_factory=dict)


class DiagnosticEngine:
    """Automatically diagnoses root causes of failures."""
    
    def __init__(self, db_path: str = "self_healing.db"):
        self.db_path = db_path
        self._init_database()
        self.failure_patterns: Dict[str, FailurePattern] = {}
        self._load_failure_patterns()
    
    def _init_database(self):
        """Initialize the diagnostic database."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS failure_patterns (
                id TEXT PRIMARY KEY,
                failure_type TEXT NOT NULL,
                severity TEXT NOT NULL,
                symptoms TEXT NOT NULL,
                root_causes TEXT NOT NULL,
                recovery_steps TEXT NOT NULL,
                prevention_tips TEXT NOT NULL,
                confidence REAL DEFAULT 0.0
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS diagnoses (
                id TEXT PRIMARY KEY,
                component TEXT NOT NULL,
                failure_type TEXT NOT NULL,
                severity TEXT NOT NULL,
                root_cause TEXT NOT NULL,
                confidence REAL NOT NULL,
                symptoms TEXT NOT NULL,
                recovery_plan TEXT NOT NULL,
                timestamp TEXT NOT NULL,
                details TEXT
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS diagnostic_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                diagnosis_id TEXT NOT NULL,
                component TEXT NOT NULL,
                success_rate REAL DEFAULT 0.0,
                recovery_time REAL DEFAULT 0.0,
                timestamp TEXT NOT NULL
            )
        ''')
        
        conn.commit()
        conn.close()
    
    def _load_failure_patterns(self):
        """Load predefined failure patterns."""
        patterns = [
            FailurePattern(
                pattern_id="api_connection_timeout",
                failure_type=FailureType.CONNECTION,
                severity=Severity.HIGH,
                symptoms=[
                    "API response time elevated",
                    "API service unavailable",
                    "Connection timeout errors"
                ],
                root_causes=[
                    "Network connectivity issues",
                    "API server overload",
                    "Firewall blocking connections"
                ],
                recovery_steps=[
                    "Check network connectivity",
                    "Restart API service",
                    "Verify firewall settings"
                ],
                prevention_tips=[
                    "Implement connection pooling",
                    "Add retry mechanisms",
                    "Monitor API performance"
                ],
                confidence=0.85
            ),
            FailurePattern(
                pattern_id="database_corruption",
                failure_type=FailureType.DATA_CORRUPTION,
                severity=Severity.CRITICAL,
                symptoms=[
                    "Database access errors",
                    "Data integrity violations",
                    "Corrupted file errors"
                ],
                root_causes=[
                    "Disk space issues",
                    "Hardware failures",
                    "Improper shutdown"
                ],
                recovery_steps=[
                    "Backup current data",
                    "Run database repair tools",
                    "Restore from backup if needed"
                ],
                prevention_tips=[
                    "Regular backups",
                    "Proper shutdown procedures",
                    "Disk health monitoring"
                ],
                confidence=0.90
            ),
            FailurePattern(
                pattern_id="memory_database_missing",
                failure_type=FailureType.RESOURCE,
                severity=Severity.MEDIUM,
                symptoms=[
                    "Memory database not found",
                    "Memory system errors",
                    "Data persistence failures"
                ],
                root_causes=[
                    "Database file deleted",
                    "Permission issues",
                    "Disk space problems"
                ],
                recovery_steps=[
                    "Check file permissions",
                    "Recreate database if needed",
                    "Verify disk space"
                ],
                prevention_tips=[
                    "Regular file backups",
                    "Permission monitoring",
                    "Disk space alerts"
                ],
                confidence=0.80
            ),
            FailurePattern(
                pattern_id="ui_file_missing",
                failure_type=FailureType.RESOURCE,
                severity=Severity.MEDIUM,
                symptoms=[
                    "UI main file not found",
                    "UI system errors",
                    "Interface failures"
                ],
                root_causes=[
                    "File deletion or corruption",
                    "Deployment issues",
                    "Version conflicts"
                ],
                recovery_steps=[
                    "Check file existence",
                    "Reinstall UI components",
                    "Verify deployment"
                ],
                prevention_tips=[
                    "Version control",
                    "Deployment validation",
                    "File integrity checks"
                ],
                confidence=0.75
            ),
            FailurePattern(
                pattern_id="permission_denied",
                failure_type=FailureType.PERMISSION,
                severity=Severity.HIGH,
                symptoms=[
                    "Permission denied errors",
                    "Access control failures",
                    "Authentication issues"
                ],
                root_causes=[
                    "Incorrect file permissions",
                    "User privilege issues",
                    "Security policy violations"
                ],
                recovery_steps=[
                    "Check file permissions",
                    "Verify user privileges",
                    "Review security policies"
                ],
                prevention_tips=[
                    "Regular permission audits",
                    "Principle of least privilege",
                    "Security monitoring"
                ],
                confidence=0.85
            )
        ]
        
        for pattern in patterns:
            self.failure_patterns[pattern.pattern_id] = pattern
    
    def diagnose_failure(self, health_check: 'HealthCheck') -> Optional[Diagnosis]:
        """Diagnose a failure based on health check results."""
        if health_check.status.value == "healthy":
            return None
        
        # Find matching failure patterns
        matching_patterns = self._find_matching_patterns(health_check)
        
        if not matching_patterns:
            return self._create_unknown_diagnosis(health_check)
        
        # Select the best matching pattern
        best_pattern = max(matching_patterns, key=lambda p: p.confidence)
        
        # Create diagnosis
        diagnosis = Diagnosis(
            diagnosis_id=f"diag_{int(time.time())}",
            component=health_check.component,
            failure_type=best_pattern.failure_type,
            severity=best_pattern.severity,
            root_cause=best_pattern.root_causes[0],  # Primary root cause
            confidence=best_pattern.confidence,
            symptoms=best_pattern.symptoms,
            recovery_plan=best_pattern.recovery_steps,
            timestamp=datetime.now(),
            details={
                "pattern_id": best_pattern.pattern_id,
                "all_root_causes": best_pattern.root_causes,
                "prevention_tips": best_pattern.prevention_tips,
                "health_check_details": health_check.details
            }
        )
        
        # Store diagnosis
        self._store_diagnosis(diagnosis)
        
        return diagnosis
    
    def _find_matching_patterns(self, health_check: 'HealthCheck') -> List[FailurePattern]:
        """Find failure patterns that match the health check symptoms."""
        matching_patterns = []
        
        for pattern in self.failure_patterns.values():
            # Check if any symptoms match
            for symptom in pattern.symptoms:
                if self._symptom_matches(symptom, health_check.message):
                    matching_patterns.append(pattern)
                    break
        
        return matching_patterns
    
    def _symptom_matches(self, symptom: str, message: str) -> bool:
        """Check if a symptom matches the health check message."""
        # Convert to lowercase for comparison
        symptom_lower = symptom.lower()
        message_lower = message.lower()
        
        # Check for exact matches or keyword matches
        if symptom_lower in message_lower:
            return True
        
        # Check for keyword matches
        keywords = symptom_lower.split()
        return any(keyword in message_lower for keyword in keywords)
    
    def _create_unknown_diagnosis(self, health_check: 'HealthCheck') -> Diagnosis:
        """Create a diagnosis for unknown failure patterns."""
        return Diagnosis(
            diagnosis_id=f"diag_unknown_{int(time.time())}",
            component=health_check.component,
            failure_type=FailureType.UNKNOWN,
            severity=Severity.MEDIUM,
            root_cause="Unknown failure pattern",
            confidence=0.3,
            symptoms=[health_check.message],
            recovery_plan=[
                "Investigate failure manually",
                "Check system logs",
                "Contact system administrator"
            ],
            timestamp=datetime.now(),
            details={
                "pattern_id": "unknown",
                "health_check_details": health_check.details
            }
        )
    
    def get_diagnosis_history(self, component: str = None, hours: int = 24) -> List[Diagnosis]:
        """Get diagnosis history."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        since = datetime.now() - timedelta(hours=hours)
        
        if component:
            cursor.execute('''
                SELECT id, component, failure_type, severity, root_cause, confidence,
                       symptoms, recovery_plan, timestamp, details
                FROM diagnoses
                WHERE component = ? AND timestamp > ?
                ORDER BY timestamp DESC
            ''', (component, since.isoformat()))
        else:
            cursor.execute('''
                SELECT id, component, failure_type, severity, root_cause, confidence,
                       symptoms, recovery_plan, timestamp, details
                FROM diagnoses
                WHERE timestamp > ?
                ORDER BY timestamp DESC
            ''', (since.isoformat(),))
        
        diagnoses = []
        for row in cursor.fetchall():
            diagnoses.append(Diagnosis(
                diagnosis_id=row[0],
                component=row[1],
                failure_type=FailureType(row[2]),
                severity=Severity(row[3]),
                root_cause=row[4],
                confidence=row[5],
                symptoms=json.loads(row[6]),
                recovery_plan=json.loads(row[7]),
                timestamp=datetime.fromisoformat(row[8]),
                details=json.loads(row[9]) if row[9] else {}
            ))
        
        conn.close()
        return diagnoses
    
    def get_failure_statistics(self, hours: int = 24) -> Dict[str, Any]:
        """Get failure statistics."""
        diagnoses = self.get_diagnosis_history(hours=hours)
        
        stats = {
            "total_failures": len(diagnoses),
            "by_component": {},
            "by_type": {},
            "by_severity": {},
            "most_common_failures": []
        }
        
        for diagnosis in diagnoses:
            # By component
            if diagnosis.component not in stats["by_component"]:
                stats["by_component"][diagnosis.component] = 0
            stats["by_component"][diagnosis.component] += 1
            
            # By type
            failure_type = diagnosis.failure_type.value
            if failure_type not in stats["by_type"]:
                stats["by_type"][failure_type] = 0
            stats["by_type"][failure_type] += 1
            
            # By severity
            severity = diagnosis.severity.value
            if severity not in stats["by_severity"]:
                stats["by_severity"][severity] = 0
            stats["by_severity"][severity] += 1
        
        # Most common failures
        failure_counts = {}
        for diagnosis in diagnoses:
            key = f"{diagnosis.component}:{diagnosis.failure_type.value}"
            if key not in failure_counts:
                failure_counts[key] = 0
            failure_counts[key] += 1
        
        stats["most_common_failures"] = sorted(
            failure_counts.items(),
            key=lambda x: x[1],
            reverse=True
        )[:5]
        
        return stats
    
    def _store_diagnosis(self, diagnosis: Diagnosis):
        """Store diagnosis in database."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO diagnoses 
            (id, component, failure_type, severity, root_cause, confidence,
             symptoms, recovery_plan, timestamp, details)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            diagnosis.diagnosis_id,
            diagnosis.component,
            diagnosis.failure_type.value,
            diagnosis.severity.value,
            diagnosis.root_cause,
            diagnosis.confidence,
            json.dumps(diagnosis.symptoms),
            json.dumps(diagnosis.recovery_plan),
            diagnosis.timestamp.isoformat(),
            json.dumps(diagnosis.details)
        ))
        
        conn.commit()
        conn.close()
    
    def add_failure_pattern(self, pattern: FailurePattern):
        """Add a new failure pattern to the diagnostic engine."""
        self.failure_patterns[pattern.pattern_id] = pattern
        
        # Store in database
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT OR REPLACE INTO failure_patterns 
            (id, failure_type, severity, symptoms, root_causes, recovery_steps, prevention_tips, confidence)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            pattern.pattern_id,
            pattern.failure_type.value,
            pattern.severity.value,
            json.dumps(pattern.symptoms),
            json.dumps(pattern.root_causes),
            json.dumps(pattern.recovery_steps),
            json.dumps(pattern.prevention_tips),
            pattern.confidence
        ))
        
        conn.commit()
        conn.close()
    
    def update_diagnosis_success(self, diagnosis_id: str, success: bool, recovery_time: float = 0.0):
        """Update diagnosis success rate based on recovery results."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Get diagnosis details
        cursor.execute('SELECT component FROM diagnoses WHERE id = ?', (diagnosis_id,))
        result = cursor.fetchone()
        
        if result:
            component = result[0]
            success_rate = 1.0 if success else 0.0
            
            cursor.execute('''
                INSERT INTO diagnostic_history 
                (diagnosis_id, component, success_rate, recovery_time, timestamp)
                VALUES (?, ?, ?, ?, ?)
            ''', (
                diagnosis_id,
                component,
                success_rate,
                recovery_time,
                datetime.now().isoformat()
            ))
        
        conn.commit()
        conn.close()
