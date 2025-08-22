"""
Layout Manager for Three-Pane Butler Interface

Manages the layout, navigation, and pane interactions.
"""

from typing import Dict, Any, Optional
from rich.layout import Layout
from rich.panel import Panel
from rich.text import Text


class LayoutManager:
    """Manages the three-pane layout and navigation."""
    
    def __init__(self):
        self.active_pane = "center"  # Default to center pane
        self.pane_weights = {
            "left": 1,
            "center": 2, 
            "right": 1
        }
        self.navigation_history = []
        
    def get_layout(self) -> Layout:
        """Get the current layout configuration."""
        layout = Layout()
        
        # Split into header and main area
        layout.split_column(
            Layout(name="header", size=3),
            Layout(name="main", ratio=1)
        )
        
        # Split main area into three panes
        layout["main"].split_row(
            Layout(name="left", ratio=self.pane_weights["left"]),
            Layout(name="center", ratio=self.pane_weights["center"]),
            Layout(name="right", ratio=self.pane_weights["right"])
        )
        
        return layout
    
    def switch_pane(self, pane_name: str) -> bool:
        """Switch to a different pane."""
        if pane_name in ["left", "center", "right"]:
            self.navigation_history.append(self.active_pane)
            self.active_pane = pane_name
            return True
        return False
    
    def resize_pane(self, pane_name: str, new_weight: int) -> bool:
        """Resize a pane by adjusting its weight."""
        if pane_name in self.pane_weights and new_weight > 0:
            self.pane_weights[pane_name] = new_weight
            return True
        return False
    
    def get_navigation_help(self) -> Panel:
        """Get navigation help text."""
        help_text = Text()
        help_text.append("Navigation: ", style="bold gold")
        help_text.append("← → (arrow keys) to switch panes\n", style="white")
        help_text.append("Actions: ", style="bold gold")
        help_text.append("Enter to select, Esc to cancel\n", style="white")
        help_text.append("Resize: ", style="bold gold")
        help_text.append("Ctrl+← → to resize panes", style="white")
        
        return Panel(
            help_text,
            title="Navigation Help",
            border_style="gold"
        )
    
    def get_status_bar(self) -> Panel:
        """Get the status bar showing current pane and system status."""
        status_text = Text()
        status_text.append(f"Active: {self.active_pane.upper()}", style="bold cyan")
        status_text.append(" | ", style="white")
        status_text.append("Ready", style="green")
        
        return Panel(
            status_text,
            border_style="blue"
        )
