#!/usr/bin/env python3
"""
Self-Healing System Demo

Demonstrates the comprehensive self-healing capabilities of the Megamind system,
including health monitoring, failure diagnosis, and automatic recovery.
"""

import time
import threading
from datetime import datetime, timedelta

from self_healing_system import SelfHealingSystem, SelfHealingConfig
from health_monitor import HealthMonitor, HealthStatus
from diagnostic_engine import DiagnosticEngine, FailureType, Severity
from recovery_manager import RecoveryManager, RecoveryType


def demo_health_monitoring():
    """Demonstrate health monitoring capabilities."""
    print("🔍 HEALTH MONITORING DEMO")
    print("=" * 50)
    
    # Initialize health monitor
    health_monitor = HealthMonitor()
    
    print("\n📊 Running Health Checks:")
    print("-" * 30)
    
    # Run health checks
    checks = health_monitor.run_health_checks()
    
    for check in checks:
        status_icon = {
            "healthy": "✅",
            "warning": "⚠️",
            "critical": "🚨",
            "unknown": "❓"
        }.get(check.status.value, "❓")
        
        print(f"{status_icon} {check.component.upper()}: {check.message}")
        print(f"   Response time: {check.response_time:.3f}s")
        print(f"   Details: {check.details}")
        print()
    
    # Get system health
    system_health = health_monitor.get_system_health()
    print(f"📈 Overall System Health: {system_health.overall_status.value.upper()}")
    print(f"   Components: {system_health.component_count}")
    print(f"   Healthy: {system_health.healthy_components}")
    print(f"   Warnings: {system_health.warning_components}")
    print(f"   Critical: {system_health.critical_components}")
    print()


def demo_failure_diagnosis():
    """Demonstrate failure diagnosis capabilities."""
    print("🔬 FAILURE DIAGNOSIS DEMO")
    print("=" * 50)
    
    # Initialize diagnostic engine
    diagnostic_engine = DiagnosticEngine()
    
    print("\n🧠 Available Failure Patterns:")
    print("-" * 35)
    
    for pattern_id, pattern in diagnostic_engine.failure_patterns.items():
        print(f"📋 {pattern_id.replace('_', ' ').title()}")
        print(f"   Type: {pattern.failure_type.value}")
        print(f"   Severity: {pattern.severity.value}")
        print(f"   Confidence: {pattern.confidence:.2f}")
        print(f"   Symptoms: {', '.join(pattern.symptoms[:2])}...")
        print()
    
    # Simulate some health checks for diagnosis
    print("🔍 Diagnosing Failures:")
    print("-" * 25)
    
    from health_monitor import HealthCheck, ComponentType
    
    # Simulate a critical API failure
    api_failure = HealthCheck(
        component="api",
        component_type=ComponentType.API,
        status=HealthStatus.CRITICAL,
        message="API service unavailable",
        timestamp=datetime.now(),
        response_time=5.0
    )
    
    diagnosis = diagnostic_engine.diagnose_failure(api_failure)
    if diagnosis:
        print(f"🚨 API Failure Diagnosis:")
        print(f"   Root Cause: {diagnosis.root_cause}")
        print(f"   Confidence: {diagnosis.confidence:.2f}")
        print(f"   Severity: {diagnosis.severity.value}")
        print(f"   Recovery Plan: {', '.join(diagnosis.recovery_plan[:2])}...")
        print()
    
    # Get failure statistics
    stats = diagnostic_engine.get_failure_statistics(hours=24)
    print(f"📊 Failure Statistics (24h):")
    print(f"   Total Failures: {stats['total_failures']}")
    print(f"   By Type: {stats['by_type']}")
    print(f"   By Severity: {stats['by_severity']}")
    print()


def demo_recovery_procedures():
    """Demonstrate recovery procedure capabilities."""
    print("🛠️ RECOVERY PROCEDURES DEMO")
    print("=" * 50)
    
    # Initialize recovery manager
    recovery_manager = RecoveryManager()
    
    print("\n📋 Available Recovery Procedures:")
    print("-" * 35)
    
    for procedure_id, procedure in recovery_manager.recovery_procedures.items():
        type_icon = {
            "automatic": "🤖",
            "manual": "👤",
            "semi_automatic": "🤝"
        }.get(procedure.recovery_type.value, "❓")
        
        print(f"{type_icon} {procedure.name}")
        print(f"   Type: {procedure.recovery_type.value}")
        print(f"   Estimated Time: {procedure.estimated_time}s")
        print(f"   Steps: {len(procedure.steps)}")
        print(f"   Description: {procedure.description}")
        print()
    
    # Simulate a recovery attempt
    print("🔄 Simulating Recovery Attempt:")
    print("-" * 30)
    
    from diagnostic_engine import Diagnosis
    
    # Create a simulated diagnosis
    test_diagnosis = Diagnosis(
        diagnosis_id="test_diag_001",
        component="api",
        failure_type=FailureType.CONNECTION,
        severity=Severity.HIGH,
        root_cause="Network connectivity issues",
        confidence=0.85,
        symptoms=["API service unavailable"],
        recovery_plan=["Restart API service"],
        timestamp=datetime.now()
    )
    
    # Attempt automatic recovery
    recovery_attempt = recovery_manager.attempt_automatic_recovery(test_diagnosis)
    
    print(f"🛠️ Recovery Attempt Results:")
    print(f"   Status: {recovery_attempt.status.value}")
    print(f"   Success: {recovery_attempt.success}")
    print(f"   Recovery Time: {recovery_attempt.recovery_time:.2f}s")
    print(f"   Steps Completed: {len(recovery_attempt.steps_completed)}")
    print(f"   Steps Failed: {len(recovery_attempt.steps_failed)}")
    
    if recovery_attempt.steps_completed:
        print(f"   Completed Steps: {', '.join(recovery_attempt.steps_completed)}")
    
    if recovery_attempt.error_message:
        print(f"   Error: {recovery_attempt.error_message}")
    print()
    
    # Get recovery statistics
    stats = recovery_manager.get_recovery_statistics(hours=24)
    print(f"📊 Recovery Statistics (24h):")
    print(f"   Total Attempts: {stats['total_attempts']}")
    print(f"   Success Rate: {stats['success_rate']:.2%}")
    print(f"   Average Recovery Time: {stats['avg_recovery_time']:.2f}s")
    print()


def demo_self_healing_system():
    """Demonstrate the complete self-healing system."""
    print("🏴‍☠️ SELF-HEALING SYSTEM DEMO")
    print("=" * 50)
    
    # Initialize self-healing system with custom config
    config = SelfHealingConfig(
        monitoring_interval=10,  # Faster for demo
        auto_recovery_enabled=True,
        alert_notifications=True,
        max_recovery_attempts=2,
        recovery_cooldown=60,  # Shorter for demo
        health_threshold=0.8
    )
    
    self_healing = SelfHealingSystem(config)
    
    print("\n🚀 Starting Self-Healing System...")
    self_healing.start()
    
    # Let it run for a bit to collect data
    print("⏳ Running health monitoring for 15 seconds...")
    time.sleep(15)
    
    # Get system status
    print("\n📊 System Status:")
    print("-" * 20)
    status = self_healing.get_system_status()
    
    print(f"Active: {status.is_active}")
    print(f"Monitoring: {status.monitoring_active}")
    print(f"Health Score: {status.system_health_score:.2%}")
    print(f"Total Recoveries: {status.total_recoveries}")
    print(f"Successful: {status.successful_recoveries}")
    print(f"Failed: {status.failed_recoveries}")
    
    if status.current_issues:
        print(f"Current Issues: {', '.join(status.current_issues)}")
    else:
        print("Current Issues: None")
    print()
    
    # Get health dashboard
    print("📈 Health Dashboard:")
    print("-" * 20)
    dashboard = self_healing.get_health_dashboard()
    
    health = dashboard["system_health"]
    print(f"Overall Status: {health['overall_status']}")
    print(f"Health Score: {health['health_score']:.2%}")
    print(f"Components: {health['healthy_components']}/{health['component_count']} healthy")
    
    if health['warning_components'] > 0:
        print(f"Warnings: {health['warning_components']}")
    if health['critical_components'] > 0:
        print(f"Critical: {health['critical_components']}")
    print()
    
    # Show component details
    print("🔍 Component Details:")
    print("-" * 20)
    for component in dashboard["components"]:
        status_icon = {
            "healthy": "✅",
            "warning": "⚠️",
            "critical": "🚨"
        }.get(component["status"], "❓")
        
        print(f"{status_icon} {component['component'].upper()}: {component['message']}")
        print(f"   Response Time: {component['response_time']:.3f}s")
    print()
    
    # Stop the system
    print("🛑 Stopping Self-Healing System...")
    self_healing.stop()
    print("✅ Self-Healing System stopped")


def demo_failure_simulation():
    """Demonstrate failure simulation and recovery."""
    print("🎭 FAILURE SIMULATION DEMO")
    print("=" * 50)
    
    # Initialize self-healing system
    config = SelfHealingConfig(
        monitoring_interval=5,  # Very fast for demo
        auto_recovery_enabled=True,
        max_recovery_attempts=1,
        recovery_cooldown=30
    )
    
    self_healing = SelfHealingSystem(config)
    
    print("\n🚀 Starting Self-Healing System...")
    self_healing.start()
    
    # Let it run for a bit
    print("⏳ Running for 10 seconds to establish baseline...")
    time.sleep(10)
    
    # Simulate a failure by creating a corrupted health check
    print("\n🎭 Simulating API Failure...")
    
    # This would normally be triggered by the health monitor
    # For demo purposes, we'll simulate it directly
    from health_monitor import HealthCheck, ComponentType, HealthStatus
    
    # Create a critical health check
    critical_check = HealthCheck(
        component="api",
        component_type=ComponentType.API,
        status=HealthStatus.CRITICAL,
        message="API service unavailable - connection timeout",
        timestamp=datetime.now(),
        response_time=10.0,
        details={"endpoint": "/health", "error": "connection_timeout"}
    )
    
    # Trigger diagnosis and recovery
    diagnosis = self_healing.diagnostic_engine.diagnose_failure(critical_check)
    if diagnosis:
        print(f"🔍 Diagnosis: {diagnosis.root_cause}")
        print(f"   Confidence: {diagnosis.confidence:.2f}")
        print(f"   Severity: {diagnosis.severity.value}")
        
        # Attempt recovery
        recovery_attempt = self_healing.recovery_manager.attempt_automatic_recovery(diagnosis)
        print(f"🛠️ Recovery Result: {'✅ Success' if recovery_attempt.success else '❌ Failed'}")
        print(f"   Time: {recovery_attempt.recovery_time:.2f}s")
        print(f"   Steps: {len(recovery_attempt.steps_completed)} completed")
    
    # Let it run a bit more
    print("\n⏳ Running for 10 more seconds to observe recovery...")
    time.sleep(10)
    
    # Get final status
    final_status = self_healing.get_system_status()
    print(f"\n📊 Final Status:")
    print(f"   Health Score: {final_status.system_health_score:.2%}")
    print(f"   Total Recoveries: {final_status.total_recoveries}")
    print(f"   Successful: {final_status.successful_recoveries}")
    
    # Stop the system
    print("\n🛑 Stopping Self-Healing System...")
    self_healing.stop()
    print("✅ Self-Healing System stopped")


def main():
    """Run the complete self-healing demo."""
    print("🏴‍☠️ MEGAMIND SELF-HEALING SYSTEM DEMO")
    print("=" * 60)
    print("This demo showcases the comprehensive self-healing capabilities")
    print("that ensure the galleon can 'pirate ever on' even when storms")
    print("damage our systems.")
    print("=" * 60)
    print()
    
    try:
        # Run individual demos
        demo_health_monitoring()
        demo_failure_diagnosis()
        demo_recovery_procedures()
        demo_self_healing_system()
        demo_failure_simulation()
        
        print("=" * 60)
        print("🏴‍☠️ DEMO COMPLETE - Self-Healing System")
        print("The system embodies the mission's resilience:")
        print("• MONITOR: Continuous health monitoring of all components")
        print("• DIAGNOSE: Automatic failure pattern recognition and root cause analysis")
        print("• RECOVER: Automatic and manual recovery procedures")
        print("• PROTECT: Cooldown periods and attempt limits prevent system overload")
        print("• LEARN: Recovery history and success metrics for continuous improvement")
        print("=" * 60)
        
    except Exception as e:
        print(f"❌ Demo failed: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
