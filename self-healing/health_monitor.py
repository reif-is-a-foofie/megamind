"""
Health Monitor

Monitors all system components for failures and anomalies, providing
real-time health status and alerting capabilities.
"""

import time
import threading
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Callable
from dataclasses import dataclass, field
from enum import Enum
import json
import sqlite3
from pathlib import Path


class HealthStatus(Enum):
    """Health status enumeration."""
    HEALTHY = "healthy"
    WARNING = "warning"
    CRITICAL = "critical"
    UNKNOWN = "unknown"


class ComponentType(Enum):
    """System component types."""
    API = "api"
    MEMORY = "memory"
    FEED = "feed"
    UI = "ui"
    DATABASE = "database"
    ORCHESTRATOR = "orchestrator"
    AUTONOMY = "autonomy"
    JOURNAL = "journal"
    RAIDS = "raids"
    KNOWLEDGE = "knowledge"
    ACTIONS = "actions"


@dataclass
class HealthCheck:
    """Represents a health check result."""
    component: str
    component_type: ComponentType
    status: HealthStatus
    message: str
    timestamp: datetime
    response_time: float
    details: Dict[str, Any] = field(default_factory=dict)


@dataclass
class SystemHealth:
    """Overall system health status."""
    overall_status: HealthStatus
    component_count: int
    healthy_components: int
    warning_components: int
    critical_components: int
    last_check: datetime
    uptime: timedelta
    checks: List[HealthCheck] = field(default_factory=list)


class HealthMonitor:
    """Monitors system health and provides status reporting."""
    
    def __init__(self, db_path: str = "self_healing.db"):
        self.db_path = db_path
        self._init_database()
        self.health_checks: Dict[str, Callable] = {}
        self.alert_handlers: List[Callable] = []
        self.monitoring_active = False
        self.monitor_thread = None
        self.check_interval = 30  # seconds
        
    def _init_database(self):
        """Initialize the health monitoring database."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS health_checks (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                component TEXT NOT NULL,
                component_type TEXT NOT NULL,
                status TEXT NOT NULL,
                message TEXT NOT NULL,
                timestamp TEXT NOT NULL,
                response_time REAL NOT NULL,
                details TEXT
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS health_alerts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                component TEXT NOT NULL,
                alert_type TEXT NOT NULL,
                message TEXT NOT NULL,
                severity TEXT NOT NULL,
                timestamp TEXT NOT NULL,
                resolved BOOLEAN DEFAULT FALSE,
                resolved_at TEXT
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS system_uptime (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                start_time TEXT NOT NULL,
                end_time TEXT,
                status TEXT NOT NULL,
                duration_seconds REAL
            )
        ''')
        
        conn.commit()
        conn.close()
    
    def register_health_check(self, component: str, check_func: Callable):
        """Register a health check function for a component."""
        self.health_checks[component] = check_func
    
    def add_alert_handler(self, handler: Callable):
        """Add an alert handler function."""
        self.alert_handlers.append(handler)
    
    def check_api_health(self) -> HealthCheck:
        """Check API system health."""
        start_time = time.time()
        try:
            # Simulate API health check
            time.sleep(0.1)  # Simulate API call
            response_time = time.time() - start_time
            
            # Simulate different health states
            import random
            if random.random() > 0.9:  # 10% chance of warning
                status = HealthStatus.WARNING
                message = "API response time elevated"
            elif random.random() > 0.95:  # 5% chance of critical
                status = HealthStatus.CRITICAL
                message = "API service unavailable"
            else:
                status = HealthStatus.HEALTHY
                message = "API service healthy"
            
            return HealthCheck(
                component="api",
                component_type=ComponentType.API,
                status=status,
                message=message,
                timestamp=datetime.now(),
                response_time=response_time,
                details={"endpoint": "/health", "version": "1.0.0"}
            )
        except Exception as e:
            return HealthCheck(
                component="api",
                component_type=ComponentType.API,
                status=HealthStatus.CRITICAL,
                message=f"API health check failed: {str(e)}",
                timestamp=datetime.now(),
                response_time=time.time() - start_time
            )
    
    def check_memory_health(self) -> HealthCheck:
        """Check memory system health."""
        start_time = time.time()
        try:
            # Simulate memory health check
            time.sleep(0.05)
            response_time = time.time() - start_time
            
            # Check if memory database exists and is accessible
            memory_db = Path("memory.db")
            if not memory_db.exists():
                status = HealthStatus.WARNING
                message = "Memory database not found"
            else:
                status = HealthStatus.HEALTHY
                message = "Memory system healthy"
            
            return HealthCheck(
                component="memory",
                component_type=ComponentType.MEMORY,
                status=status,
                message=message,
                timestamp=datetime.now(),
                response_time=response_time,
                details={"db_size": memory_db.stat().st_size if memory_db.exists() else 0}
            )
        except Exception as e:
            return HealthCheck(
                component="memory",
                component_type=ComponentType.MEMORY,
                status=HealthStatus.CRITICAL,
                message=f"Memory health check failed: {str(e)}",
                timestamp=datetime.now(),
                response_time=time.time() - start_time
            )
    
    def check_database_health(self) -> HealthCheck:
        """Check database system health."""
        start_time = time.time()
        try:
            # Simulate database health check
            time.sleep(0.1)
            response_time = time.time() - start_time
            
            # Check if contracts database exists
            contracts_db = Path("agents/contracts.json")
            if not contracts_db.exists():
                status = HealthStatus.CRITICAL
                message = "Contracts database not found"
            else:
                status = HealthStatus.HEALTHY
                message = "Database system healthy"
            
            return HealthCheck(
                component="database",
                component_type=ComponentType.DATABASE,
                status=status,
                message=message,
                timestamp=datetime.now(),
                response_time=response_time,
                details={"contracts_count": 15}  # Simulated count
            )
        except Exception as e:
            return HealthCheck(
                component="database",
                component_type=ComponentType.DATABASE,
                status=HealthStatus.CRITICAL,
                message=f"Database health check failed: {str(e)}",
                timestamp=datetime.now(),
                response_time=time.time() - start_time
            )
    
    def check_ui_health(self) -> HealthCheck:
        """Check UI system health."""
        start_time = time.time()
        try:
            # Simulate UI health check
            time.sleep(0.05)
            response_time = time.time() - start_time
            
            # Check if UI files exist
            ui_main = Path("ui/main.go")
            if not ui_main.exists():
                status = HealthStatus.WARNING
                message = "UI main file not found"
            else:
                status = HealthStatus.HEALTHY
                message = "UI system healthy"
            
            return HealthCheck(
                component="ui",
                component_type=ComponentType.UI,
                status=status,
                message=message,
                timestamp=datetime.now(),
                response_time=response_time,
                details={"ui_type": "crush", "components": 3}
            )
        except Exception as e:
            return HealthCheck(
                component="ui",
                component_type=ComponentType.UI,
                status=HealthStatus.CRITICAL,
                message=f"UI health check failed: {str(e)}",
                timestamp=datetime.now(),
                response_time=time.time() - start_time
            )
    
    def run_health_checks(self) -> List[HealthCheck]:
        """Run all registered health checks."""
        checks = []
        
        # Run built-in health checks
        checks.extend([
            self.check_api_health(),
            self.check_memory_health(),
            self.check_database_health(),
            self.check_ui_health()
        ])
        
        # Run custom health checks
        for component, check_func in self.health_checks.items():
            try:
                check = check_func()
                checks.append(check)
            except Exception as e:
                checks.append(HealthCheck(
                    component=component,
                    component_type=ComponentType.UNKNOWN,
                    status=HealthStatus.CRITICAL,
                    message=f"Health check failed: {str(e)}",
                    timestamp=datetime.now(),
                    response_time=0.0
                ))
        
        # Store health checks in database
        self._store_health_checks(checks)
        
        # Trigger alerts for critical issues
        self._check_alerts(checks)
        
        return checks
    
    def get_system_health(self) -> SystemHealth:
        """Get overall system health status."""
        checks = self.run_health_checks()
        
        # Calculate overall status
        critical_count = sum(1 for c in checks if c.status == HealthStatus.CRITICAL)
        warning_count = sum(1 for c in checks if c.status == HealthStatus.WARNING)
        healthy_count = sum(1 for c in checks if c.status == HealthStatus.HEALTHY)
        
        if critical_count > 0:
            overall_status = HealthStatus.CRITICAL
        elif warning_count > 0:
            overall_status = HealthStatus.WARNING
        else:
            overall_status = HealthStatus.HEALTHY
        
        return SystemHealth(
            overall_status=overall_status,
            component_count=len(checks),
            healthy_components=healthy_count,
            warning_components=warning_count,
            critical_components=critical_count,
            last_check=datetime.now(),
            uptime=timedelta(hours=24),  # Simulated uptime
            checks=checks
        )
    
    def _store_health_checks(self, checks: List[HealthCheck]):
        """Store health checks in database."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        for check in checks:
            cursor.execute('''
                INSERT INTO health_checks 
                (component, component_type, status, message, timestamp, response_time, details)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (
                check.component,
                check.component_type.value,
                check.status.value,
                check.message,
                check.timestamp.isoformat(),
                check.response_time,
                json.dumps(check.details)
            ))
        
        conn.commit()
        conn.close()
    
    def _check_alerts(self, checks: List[HealthCheck]):
        """Check for alerts and trigger handlers."""
        for check in checks:
            if check.status in [HealthStatus.CRITICAL, HealthStatus.WARNING]:
                alert = {
                    "component": check.component,
                    "alert_type": "health_check",
                    "message": check.message,
                    "severity": check.status.value,
                    "timestamp": check.timestamp
                }
                
                # Store alert in database
                self._store_alert(alert)
                
                # Trigger alert handlers
                for handler in self.alert_handlers:
                    try:
                        handler(alert)
                    except Exception as e:
                        print(f"Alert handler failed: {e}")
    
    def _store_alert(self, alert: Dict[str, Any]):
        """Store alert in database."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO health_alerts 
            (component, alert_type, message, severity, timestamp)
            VALUES (?, ?, ?, ?, ?)
        ''', (
            alert["component"],
            alert["alert_type"],
            alert["message"],
            alert["severity"],
            alert["timestamp"].isoformat()
        ))
        
        conn.commit()
        conn.close()
    
    def start_monitoring(self):
        """Start continuous health monitoring."""
        if self.monitoring_active:
            return
        
        self.monitoring_active = True
        self.monitor_thread = threading.Thread(target=self._monitor_loop)
        self.monitor_thread.daemon = True
        self.monitor_thread.start()
    
    def stop_monitoring(self):
        """Stop continuous health monitoring."""
        self.monitoring_active = False
        if self.monitor_thread:
            self.monitor_thread.join()
    
    def _monitor_loop(self):
        """Main monitoring loop."""
        while self.monitoring_active:
            try:
                self.run_health_checks()
                time.sleep(self.check_interval)
            except Exception as e:
                print(f"Health monitoring error: {e}")
                time.sleep(self.check_interval)
    
    def get_health_history(self, component: str = None, hours: int = 24) -> List[HealthCheck]:
        """Get health check history."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        since = datetime.now() - timedelta(hours=hours)
        
        if component:
            cursor.execute('''
                SELECT component, component_type, status, message, timestamp, response_time, details
                FROM health_checks
                WHERE component = ? AND timestamp > ?
                ORDER BY timestamp DESC
            ''', (component, since.isoformat()))
        else:
            cursor.execute('''
                SELECT component, component_type, status, message, timestamp, response_time, details
                FROM health_checks
                WHERE timestamp > ?
                ORDER BY timestamp DESC
            ''', (since.isoformat(),))
        
        checks = []
        for row in cursor.fetchall():
            checks.append(HealthCheck(
                component=row[0],
                component_type=ComponentType(row[1]),
                status=HealthStatus(row[2]),
                message=row[3],
                timestamp=datetime.fromisoformat(row[4]),
                response_time=row[5],
                details=json.loads(row[6]) if row[6] else {}
            ))
        
        conn.close()
        return checks
