"""
Right Pane - Logs, Alerts & XP Overlay

Displays system logs, alerts, and gamified XP information.
"""

from typing import List, Dict, Any, Optional
from datetime import datetime
from rich.panel import Panel
from rich.text import Text
from rich.table import Table
from rich.columns import Columns
from rich.console import Group


class RightPane:
    """Right pane showing logs, alerts, and XP overlay."""
    
    def __init__(self, api_connector):
        self.api_connector = api_connector
        self.logs = []
        self.alerts = []
        self.xp_data = {
            "level": 5,
            "xp": 1250,
            "xp_to_next": 250,
            "title": "Navigator",
            "completed_today": 12
        }
        
        # Initialize with sample data
        self._load_sample_data()
        
    def render(self) -> Panel:
        """Render the right pane content."""
        content = Group(
            self._render_xp_overlay(),
            self._render_alerts(),
            self._render_logs()
        )
        
        return Panel(
            content,
            title="📊 Logs & XP",
            border_style="yellow",
            subtitle="System Status"
        )
    
    def _render_xp_overlay(self) -> Table:
        """Render the XP and gamification overlay."""
        table = Table(title="🏴‍☠️ Pirate Progress", show_header=False)
        table.add_column("Stat", style="cyan", no_wrap=True)
        table.add_column("Value", style="gold")
        
        xp_data = self.xp_data
        table.add_row("Level", f"{xp_data['level']} - {xp_data['title']}")
        table.add_row("XP", f"{xp_data['xp']} / {xp_data['xp'] + xp_data['xp_to_next']}")
        table.add_row("Progress", f"{xp_data['xp_to_next']} XP to next level")
        table.add_row("Today", f"{xp_data['completed_today']} items completed")
        
        return table
    
    def _render_alerts(self) -> Text:
        """Render the alerts section."""
        alert_text = Text()
        alert_text.append("🚨 Active Alerts\n", style="bold red")
        alert_text.append("=" * 30 + "\n", style="red")
        
        # Sample alerts
        alerts = [
            ("⚠️", "High priority contract ui.01 needs attention"),
            ("💰", "Gold price alert: Significant movement detected"),
            ("🌪️", "Weather alert: Hurricane approaching coastal areas"),
            ("📧", "3 unread emails require response"),
        ]
        
        for icon, message in alerts:
            alert_text.append(f"{icon} {message}\n", style="yellow")
        
        return alert_text
    
    def _render_logs(self) -> Text:
        """Render the system logs."""
        log_text = Text()
        log_text.append("📝 System Logs\n", style="bold blue")
        log_text.append("=" * 30 + "\n", style="blue")
        
        # Sample logs
        logs = [
            ("10:15:30", "INFO", "Worker agent started ui.01 implementation"),
            ("10:15:45", "INFO", "Three-pane layout initialized"),
            ("10:16:00", "INFO", "Memory connector established"),
            ("10:16:15", "INFO", "Feed connector connected"),
            ("10:16:30", "INFO", "API connector ready"),
            ("10:16:45", "SUCCESS", "Butler interface ready for interaction"),
        ]
        
        for timestamp, level, message in logs:
            if level == "INFO":
                style = "cyan"
            elif level == "SUCCESS":
                style = "green"
            elif level == "WARNING":
                style = "yellow"
            elif level == "ERROR":
                style = "red"
            else:
                style = "white"
                
            log_text.append(f"{timestamp} [{level}] {message}\n", style=style)
        
        return log_text
    
    def _load_sample_data(self):
        """Load sample data for demonstration."""
        self.logs = [
            {
                "timestamp": datetime.now(),
                "level": "INFO",
                "message": "Butler interface initialized",
                "source": "ui.main"
            },
            {
                "timestamp": datetime.now(),
                "level": "SUCCESS",
                "message": "Three-pane layout created successfully",
                "source": "ui.layout"
            }
        ]
        
        self.alerts = [
            {
                "type": "warning",
                "message": "Contract ui.01 implementation in progress",
                "priority": "high"
            },
            {
                "type": "info",
                "message": "Memory system operational",
                "priority": "low"
            }
        ]
    
    def add_log(self, level: str, message: str, source: str = "system"):
        """Add a new log entry."""
        self.logs.append({
            "timestamp": datetime.now(),
            "level": level,
            "message": message,
            "source": source
        })
    
    def add_alert(self, alert_type: str, message: str, priority: str = "medium"):
        """Add a new alert."""
        self.alerts.append({
            "type": alert_type,
            "message": message,
            "priority": priority
        })
    
    def update_xp(self, xp_gained: int):
        """Update XP and level information."""
        self.xp_data["xp"] += xp_gained
        self.xp_data["completed_today"] += 1
        
        # Simple level progression
        if self.xp_data["xp"] >= self.xp_data["xp"] + self.xp_data["xp_to_next"]:
            self.xp_data["level"] += 1
            self.xp_data["xp_to_next"] = self.xp_data["level"] * 100
    
    def clear_alerts(self):
        """Clear all alerts."""
        self.alerts = []
