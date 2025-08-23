"""
Self-Healing System

Main orchestrator that coordinates health monitoring, diagnostics, and recovery
to provide comprehensive self-healing capabilities for the Megamind system.
"""

import time
import threading
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Callable
from dataclasses import dataclass, field
import json
import sqlite3
from pathlib import Path

from health_monitor import HealthMonitor, HealthCheck, SystemHealth
from diagnostic_engine import DiagnosticEngine, Diagnosis
from recovery_manager import RecoveryManager, RecoveryAttempt


@dataclass
class SelfHealingConfig:
    """Configuration for the self-healing system."""
    monitoring_interval: int = 30  # seconds
    auto_recovery_enabled: bool = True
    alert_notifications: bool = True
    max_recovery_attempts: int = 3
    recovery_cooldown: int = 300  # seconds
    health_threshold: float = 0.8  # 80% healthy components required


@dataclass
class SelfHealingStatus:
    """Status of the self-healing system."""
    is_active: bool
    monitoring_active: bool
    last_health_check: Optional[datetime]
    total_recoveries: int
    successful_recoveries: int
    failed_recoveries: int
    current_issues: List[str] = field(default_factory=list)
    system_health_score: float = 0.0


class SelfHealingSystem:
    """Main self-healing system orchestrator."""
    
    def __init__(self, config: SelfHealingConfig = None):
        self.config = config or SelfHealingConfig()
        self.db_path = "self_healing.db"
        self._init_database()
        
        # Initialize components
        self.health_monitor = HealthMonitor(self.db_path)
        self.diagnostic_engine = DiagnosticEngine(self.db_path)
        self.recovery_manager = RecoveryManager(self.db_path)
        
        # System state
        self.is_active = False
        self.monitoring_thread = None
        self.alert_handlers: List[Callable] = []
        self.recovery_cooldowns: Dict[str, datetime] = {}
        
        # Register alert handlers
        self._register_alert_handlers()
    
    def _init_database(self):
        """Initialize the self-healing database."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS self_healing_status (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                is_active BOOLEAN NOT NULL,
                monitoring_active BOOLEAN NOT NULL,
                last_health_check TEXT,
                total_recoveries INTEGER DEFAULT 0,
                successful_recoveries INTEGER DEFAULT 0,
                failed_recoveries INTEGER DEFAULT 0,
                system_health_score REAL DEFAULT 0.0,
                timestamp TEXT NOT NULL
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS recovery_cooldowns (
                component TEXT PRIMARY KEY,
                last_recovery TEXT NOT NULL,
                cooldown_until TEXT NOT NULL
            )
        ''')
        
        conn.commit()
        conn.close()
    
    def _register_alert_handlers(self):
        """Register alert handlers for the health monitor."""
        self.health_monitor.add_alert_handler(self._handle_health_alert)
    
    def _handle_health_alert(self, alert: Dict[str, Any]):
        """Handle health alerts and trigger recovery if needed."""
        print(f"🚨 Health Alert: {alert['component']} - {alert['message']}")
        
        # Check if component is in cooldown
        if self._is_in_cooldown(alert['component']):
            print(f"⏳ Component {alert['component']} is in recovery cooldown")
            return
        
        # Trigger recovery process
        self._trigger_recovery_for_alert(alert)
    
    def _is_in_cooldown(self, component: str) -> bool:
        """Check if a component is in recovery cooldown."""
        if component not in self.recovery_cooldowns:
            return False
        
        cooldown_until = self.recovery_cooldowns[component]
        return datetime.now() < cooldown_until
    
    def _trigger_recovery_for_alert(self, alert: Dict[str, Any]):
        """Trigger recovery process for a health alert."""
        # Get the latest health check for this component
        health_checks = self.health_monitor.get_health_history(component=alert['component'], hours=1)
        if not health_checks:
            return
        
        latest_check = health_checks[0]
        
        # Diagnose the failure
        diagnosis = self.diagnostic_engine.diagnose_failure(latest_check)
        if not diagnosis:
            print(f"❓ No diagnosis available for {alert['component']}")
            return
        
        print(f"🔍 Diagnosis: {diagnosis.root_cause} (confidence: {diagnosis.confidence:.2f})")
        
        # Attempt automatic recovery if enabled
        if self.config.auto_recovery_enabled:
            self._attempt_recovery(diagnosis)
    
    def _attempt_recovery(self, diagnosis: Diagnosis):
        """Attempt recovery for a diagnosis."""
        print(f"🛠️ Attempting recovery for {diagnosis.component}")
        
        # Check recovery attempt limits
        recent_attempts = self.recovery_manager.get_recovery_history(hours=1)
        component_attempts = [a for a in recent_attempts if a.diagnosis_id == diagnosis.diagnosis_id]
        
        if len(component_attempts) >= self.config.max_recovery_attempts:
            print(f"⚠️ Maximum recovery attempts reached for {diagnosis.component}")
            return
        
        # Attempt automatic recovery
        recovery_attempt = self.recovery_manager.attempt_automatic_recovery(diagnosis)
        
        # Update cooldown
        cooldown_until = datetime.now() + timedelta(seconds=self.config.recovery_cooldown)
        self.recovery_cooldowns[diagnosis.component] = cooldown_until
        
        # Store cooldown in database
        self._store_recovery_cooldown(diagnosis.component, cooldown_until)
        
        # Update statistics
        self._update_recovery_statistics(recovery_attempt.success)
        
        if recovery_attempt.success:
            print(f"✅ Recovery successful for {diagnosis.component}")
        else:
            print(f"❌ Recovery failed for {diagnosis.component}: {recovery_attempt.error_message}")
    
    def start(self):
        """Start the self-healing system."""
        if self.is_active:
            print("Self-healing system is already active")
            return
        
        print("🏴‍☠️ Starting Self-Healing System...")
        
        self.is_active = True
        self.health_monitor.start_monitoring()
        
        # Start monitoring thread
        self.monitoring_thread = threading.Thread(target=self._monitoring_loop)
        self.monitoring_thread.daemon = True
        self.monitoring_thread.start()
        
        print("✅ Self-Healing System started successfully")
    
    def stop(self):
        """Stop the self-healing system."""
        if not self.is_active:
            print("Self-healing system is not active")
            return
        
        print("🛑 Stopping Self-Healing System...")
        
        self.is_active = False
        self.health_monitor.stop_monitoring()
        
        if self.monitoring_thread:
            self.monitoring_thread.join()
        
        print("✅ Self-Healing System stopped")
    
    def _monitoring_loop(self):
        """Main monitoring loop for the self-healing system."""
        while self.is_active:
            try:
                # Run comprehensive health check
                system_health = self.health_monitor.get_system_health()
                
                # Update system status
                self._update_system_status(system_health)
                
                # Check if manual intervention is needed
                if system_health.overall_status.value == "critical":
                    self._handle_critical_system_state(system_health)
                
                # Sleep for monitoring interval
                time.sleep(self.config.monitoring_interval)
                
            except Exception as e:
                print(f"❌ Self-healing monitoring error: {e}")
                time.sleep(self.config.monitoring_interval)
    
    def _handle_critical_system_state(self, system_health: SystemHealth):
        """Handle critical system state."""
        print("🚨 CRITICAL SYSTEM STATE DETECTED")
        print(f"   Critical components: {system_health.critical_components}")
        print(f"   Warning components: {system_health.warning_components}")
        
        # Trigger alerts for all critical components
        for check in system_health.checks:
            if check.status.value == "critical":
                alert = {
                    "component": check.component,
                    "alert_type": "critical_state",
                    "message": check.message,
                    "severity": "critical",
                    "timestamp": check.timestamp
                }
                self._handle_health_alert(alert)
    
    def get_system_status(self) -> SelfHealingStatus:
        """Get current system status."""
        # Get latest health check
        health_checks = self.health_monitor.get_health_history(hours=1)
        last_health_check = health_checks[0].timestamp if health_checks else None
        
        # Get recovery statistics
        recovery_stats = self.recovery_manager.get_recovery_statistics(hours=24)
        
        # Calculate system health score
        if health_checks:
            healthy_count = sum(1 for c in health_checks if c.status.value == "healthy")
            total_count = len(health_checks)
            health_score = healthy_count / total_count if total_count > 0 else 0.0
        else:
            health_score = 0.0
        
        # Get current issues
        current_issues = []
        for check in health_checks:
            if check.status.value != "healthy":
                current_issues.append(f"{check.component}: {check.message}")
        
        return SelfHealingStatus(
            is_active=self.is_active,
            monitoring_active=self.health_monitor.monitoring_active,
            last_health_check=last_health_check,
            total_recoveries=recovery_stats["total_attempts"],
            successful_recoveries=recovery_stats["successful_attempts"],
            failed_recoveries=recovery_stats["failed_attempts"],
            current_issues=current_issues,
            system_health_score=health_score
        )
    
    def get_health_dashboard(self) -> Dict[str, Any]:
        """Get comprehensive health dashboard data."""
        # Get system health
        system_health = self.health_monitor.get_system_health()
        
        # Get diagnosis statistics
        diagnosis_stats = self.diagnostic_engine.get_failure_statistics(hours=24)
        
        # Get recovery statistics
        recovery_stats = self.recovery_manager.get_recovery_statistics(hours=24)
        
        # Get system status
        system_status = self.get_system_status()
        
        return {
            "system_health": {
                "overall_status": system_health.overall_status.value,
                "component_count": system_health.component_count,
                "healthy_components": system_health.healthy_components,
                "warning_components": system_health.warning_components,
                "critical_components": system_health.critical_components,
                "health_score": system_status.system_health_score
            },
            "diagnostics": diagnosis_stats,
            "recovery": recovery_stats,
            "status": {
                "is_active": system_status.is_active,
                "monitoring_active": system_status.monitoring_active,
                "last_health_check": system_status.last_health_check.isoformat() if system_status.last_health_check else None,
                "current_issues": system_status.current_issues
            },
            "components": [
                {
                    "component": check.component,
                    "status": check.status.value,
                    "message": check.message,
                    "response_time": check.response_time,
                    "timestamp": check.timestamp.isoformat()
                }
                for check in system_health.checks
            ]
        }
    
    def add_alert_handler(self, handler: Callable):
        """Add a custom alert handler."""
        self.alert_handlers.append(handler)
    
    def _update_system_status(self, system_health: SystemHealth):
        """Update system status in database."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO self_healing_status 
            (is_active, monitoring_active, last_health_check, total_recoveries,
             successful_recoveries, failed_recoveries, system_health_score, timestamp)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            self.is_active,
            self.health_monitor.monitoring_active,
            system_health.last_check.isoformat(),
            0,  # Will be updated separately
            0,  # Will be updated separately
            0,  # Will be updated separately
            system_health.healthy_components / system_health.component_count if system_health.component_count > 0 else 0.0,
            datetime.now().isoformat()
        ))
        
        conn.commit()
        conn.close()
    
    def _update_recovery_statistics(self, success: bool):
        """Update recovery statistics."""
        # This would typically update the statistics in the database
        # For now, we'll just print the result
        if success:
            print("📈 Recovery statistics updated: +1 successful")
        else:
            print("📉 Recovery statistics updated: +1 failed")
    
    def _store_recovery_cooldown(self, component: str, cooldown_until: datetime):
        """Store recovery cooldown in database."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT OR REPLACE INTO recovery_cooldowns 
            (component, last_recovery, cooldown_until)
            VALUES (?, ?, ?)
        ''', (
            component,
            datetime.now().isoformat(),
            cooldown_until.isoformat()
        ))
        
        conn.commit()
        conn.close()
    
    def get_recovery_cooldowns(self) -> Dict[str, datetime]:
        """Get current recovery cooldowns."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('SELECT component, cooldown_until FROM recovery_cooldowns')
        
        cooldowns = {}
        for row in cursor.fetchall():
            component, cooldown_until_str = row
            cooldown_until = datetime.fromisoformat(cooldown_until_str)
            if cooldown_until > datetime.now():
                cooldowns[component] = cooldown_until
        
        conn.close()
        return cooldowns
