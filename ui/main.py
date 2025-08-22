#!/usr/bin/env python3
"""
Megamind Butler Interface - Main Entry Point

Three-pane terminal interface with pirate/butler aesthetic:
- Left: File explorer + knowledge graph
- Center: Agent chat interface
- Right: Logs, alerts, XP overlay
"""

import sys
import os
from pathlib import Path
from typing import Optional, Dict, Any

from rich.console import Console
from rich.layout import Layout
from rich.panel import Panel
from rich.text import Text
from rich.table import Table
from rich.live import Live
from rich.prompt import Prompt
from rich.align import Align
from rich.columns import Columns
from rich.rule import Rule

# Add parent directory to path for imports
sys.path.append(str(Path(__file__).parent.parent))

from ui.components.layout_manager import LayoutManager
from ui.components.left_pane import LeftPane
from ui.components.center_pane import CenterPane
from ui.components.right_pane import RightPane
from ui.styles.theme import ButlerTheme
from ui.integrations.memory import MemoryConnector
from ui.integrations.feed import FeedConnector
from ui.integrations.api import APIConnector


class ButlerInterface:
    """Main three-pane butler interface with pirate aesthetic."""
    
    def __init__(self):
        self.console = Console()
        self.theme = ButlerTheme()
        self.layout_manager = LayoutManager()
        
        # Initialize connectors
        self.memory_connector = MemoryConnector()
        self.feed_connector = FeedConnector()
        self.api_connector = APIConnector()
        
        # Initialize panes
        self.left_pane = LeftPane(self.memory_connector)
        self.center_pane = CenterPane(self.feed_connector)
        self.right_pane = RightPane(self.api_connector)
        
        # Setup layout
        self.layout = self._create_layout()
        
    def _create_layout(self) -> Layout:
        """Create the three-pane layout."""
        layout = Layout()
        
        # Split into three columns
        layout.split_column(
            Layout(name="header", size=3),
            Layout(name="main", ratio=1)
        )
        
        # Split main area into three panes
        layout["main"].split_row(
            Layout(name="left", ratio=1),
            Layout(name="center", ratio=2),
            Layout(name="right", ratio=1)
        )
        
        return layout
    
    def _render_header(self) -> Panel:
        """Render the header with pirate/butler aesthetic."""
        title = Text("⚓ MEGAMIND BUTLER INTERFACE ⚓", style="bold gold")
        subtitle = Text("Your Life, Unified in One Stream", style="italic cyan")
        
        header_content = Align.center(
            title + "\n" + subtitle,
            vertical="middle"
        )
        
        return Panel(
            header_content,
            style="bold blue",
            border_style="gold"
        )
    
    def _update_panes(self):
        """Update all panes with current data."""
        # Update header
        self.layout["header"].update(self._render_header())
        
        # Update panes
        self.layout["left"].update(self.left_pane.render())
        self.layout["center"].update(self.center_pane.render())
        self.layout["right"].update(self.right_pane.render())
    
    def run(self):
        """Run the butler interface."""
        try:
            # Clear screen and show welcome
            self.console.clear()
            self.console.print(
                Panel(
                    Align.center(
                        Text("⚓ Welcome to Megamind Butler ⚓\n\n"
                             "Navigating the seas of your digital life...", 
                             style="bold gold"),
                        vertical="middle"
                    ),
                    style="bold blue",
                    border_style="gold"
                )
            )
            
            # Start live display
            with Live(self.layout, refresh_per_second=4, screen=True) as live:
                while True:
                    self._update_panes()
                    live.update(self.layout)
                    
                    # Handle user input (simplified for demo)
                    try:
                        # Non-blocking input check
                        if self.console.input_timeout(timeout=0.25):
                            break
                    except:
                        pass
                        
        except KeyboardInterrupt:
            self.console.print("\n[bold red]Shutting down butler interface...[/bold red]")
        except Exception as e:
            self.console.print(f"[bold red]Error: {e}[/bold red]")
            raise


def main():
    """Main entry point."""
    try:
        butler = ButlerInterface()
        butler.run()
    except Exception as e:
        console = Console()
        console.print(f"[bold red]Failed to start butler interface: {e}[/bold red]")
        sys.exit(1)


if __name__ == "__main__":
    main()
