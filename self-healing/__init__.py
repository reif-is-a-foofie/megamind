"""
Self-Healing System

A comprehensive system for monitoring, diagnosing, and automatically recovering
from failures across the entire Megamind system.

This system embodies the mission's resilience - ensuring the galleon can
'pirate ever on' even when storms damage our systems.
"""

from health_monitor import HealthMonitor
from diagnostic_engine import DiagnosticEngine
from recovery_manager import RecoveryManager
from self_healing_system import SelfHealingSystem

__version__ = "1.0.0"
__all__ = [
    "HealthMonitor",
    "DiagnosticEngine", 
    "RecoveryManager",
    "SelfHealingSystem"
]
