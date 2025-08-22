"""
Butler Theme - Pirate/Butler Aesthetic

Defines the visual theme and styling for the Megamind Butler Interface.
"""

from typing import Dict, Any
from rich.theme import Theme
from rich.color import Color


class ButlerTheme:
    """Pirate/Butler aesthetic theme for the Megamind interface."""
    
    def __init__(self):
        self.colors = {
            "primary": "gold",
            "secondary": "cyan", 
            "accent": "blue",
            "success": "green",
            "warning": "yellow",
            "error": "red",
            "info": "white",
            "background": "black",
            "text": "white"
        }
        
        self.symbols = {
            "ship": "⚓",
            "treasure": "💰",
            "storm": "🌪️",
            "compass": "🧭",
            "map": "🗺️",
            "sword": "⚔️",
            "shield": "🛡️",
            "crown": "👑",
            "star": "⭐",
            "anchor": "⚓"
        }
        
        self.titles = {
            "captain": "Captain",
            "navigator": "Navigator", 
            "quartermaster": "Quartermaster",
            "boatswain": "Boatswain",
            "carpenter": "Carpenter",
            "gunner": "Gunner",
            "surgeon": "Surgeon",
            "cook": "Cook",
            "swabbie": "Swabbie"
        }
        
    def get_theme(self) -> Theme:
        """Get the Rich theme configuration."""
        return Theme({
            "primary": self.colors["primary"],
            "secondary": self.colors["secondary"],
            "accent": self.colors["accent"],
            "success": self.colors["success"],
            "warning": self.colors["warning"],
            "error": self.colors["error"],
            "info": self.colors["info"],
            "background": self.colors["background"],
            "text": self.colors["text"]
        })
    
    def get_title(self, level: int) -> str:
        """Get pirate title based on level."""
        if level >= 20:
            return self.titles["captain"]
        elif level >= 15:
            return self.titles["navigator"]
        elif level >= 10:
            return self.titles["quartermaster"]
        elif level >= 5:
            return self.titles["boatswain"]
        elif level >= 3:
            return self.titles["carpenter"]
        elif level >= 1:
            return self.titles["swabbie"]
        else:
            return "Landlubber"
    
    def get_border_style(self, pane_type: str) -> str:
        """Get border style for different pane types."""
        border_styles = {
            "left": "blue",
            "center": "green", 
            "right": "yellow",
            "header": "gold",
            "footer": "cyan"
        }
        return border_styles.get(pane_type, "white")
    
    def get_pane_title(self, pane_type: str) -> str:
        """Get pane title with pirate symbols."""
        titles = {
            "left": f"{self.symbols['map']} Files & Knowledge",
            "center": f"{self.symbols['compass']} Agent Chat & Feed",
            "right": f"{self.symbols['treasure']} Logs & XP"
        }
        return titles.get(pane_type, "Unknown Pane")
    
    def get_welcome_message(self) -> str:
        """Get welcome message with pirate theme."""
        return f"{self.symbols['ship']} Welcome to Megamind Butler {self.symbols['ship']}"
    
    def get_farewell_message(self) -> str:
        """Get farewell message with pirate theme."""
        return f"{self.symbols['anchor']} Fair winds and following seas! {self.symbols['anchor']}"
    
    def get_progress_bar_style(self, percentage: float) -> str:
        """Get progress bar style based on completion percentage."""
        if percentage >= 80:
            return "green"
        elif percentage >= 60:
            return "yellow"
        elif percentage >= 40:
            return "cyan"
        else:
            return "red"
    
    def get_alert_style(self, alert_type: str) -> str:
        """Get alert style based on type."""
        alert_styles = {
            "info": "cyan",
            "warning": "yellow",
            "error": "red",
            "success": "green"
        }
        return alert_styles.get(alert_type, "white")
