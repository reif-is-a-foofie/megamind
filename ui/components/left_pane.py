"""
Left Pane - File Explorer + Knowledge Graph

Displays file system navigation and knowledge graph relationships.
"""

from typing import List, Dict, Any, Optional
from pathlib import Path
from rich.panel import Panel
from rich.tree import Tree
from rich.text import Text
from rich.table import Table
from rich.columns import Columns


class LeftPane:
    """Left pane showing file explorer and knowledge graph."""
    
    def __init__(self, memory_connector):
        self.memory_connector = memory_connector
        self.current_path = Path.cwd()
        self.selected_item = None
        self.view_mode = "files"  # "files" or "knowledge"
        
    def render(self) -> Panel:
        """Render the left pane content."""
        if self.view_mode == "files":
            content = self._render_file_explorer()
        else:
            content = self._render_knowledge_graph()
            
        return Panel(
            content,
            title="🗂️ Files & Knowledge",
            border_style="blue",
            subtitle=f"Mode: {self.view_mode.title()}"
        )
    
    def _render_file_explorer(self) -> Tree:
        """Render the file explorer tree."""
        tree = Tree("📁 Project Root", style="bold blue")
        
        # Add main directories
        project_root = Path.cwd()
        main_dirs = [
            "agents", "api", "database", "finance", 
            "knowledge", "memory", "orchestrator", "ui"
        ]
        
        for dir_name in main_dirs:
            dir_path = project_root / dir_name
            if dir_path.exists():
                dir_node = tree.add(f"📁 {dir_name}", style="cyan")
                
                # Add some key files in each directory
                if dir_name == "agents":
                    dir_node.add("📄 contracts.json", style="green")
                    dir_node.add("📄 agents.md", style="green")
                elif dir_name == "ui":
                    dir_node.add("🐍 main.py", style="yellow")
                    dir_node.add("📄 requirements.txt", style="yellow")
                elif dir_name == "memory":
                    dir_node.add("🗄️ memory_store.py", style="green")
                    dir_node.add("📊 megamind_memory.db", style="green")
                elif dir_name == "finance":
                    dir_node.add("💰 finance_manager.py", style="green")
                    dir_node.add("📈 finance_data.db", style="green")
        
        return tree
    
    def _render_knowledge_graph(self) -> Table:
        """Render the knowledge graph relationships."""
        table = Table(title="🧠 Knowledge Graph", show_header=True)
        table.add_column("Entity", style="cyan", no_wrap=True)
        table.add_column("Type", style="magenta")
        table.add_column("Connections", style="green")
        
        # Sample knowledge graph data
        knowledge_data = [
            ("Megamind System", "System", "Memory, Finance, Knowledge"),
            ("Memory Store", "Component", "Feed, Actions, API"),
            ("Finance Manager", "Component", "Banking, Crypto, Analytics"),
            ("Knowledge Graph", "Component", "Patterns, Insights, Queries"),
            ("Butler Interface", "UI", "Three-pane, Navigation, Theme"),
            ("Contract System", "Orchestration", "Captain, Worker, Tester"),
        ]
        
        for entity, entity_type, connections in knowledge_data:
            table.add_row(entity, entity_type, connections)
            
        return table
    
    def toggle_view_mode(self):
        """Toggle between file explorer and knowledge graph views."""
        self.view_mode = "knowledge" if self.view_mode == "files" else "files"
    
    def navigate_to(self, path: str):
        """Navigate to a specific path in file explorer."""
        new_path = Path(path)
        if new_path.exists():
            self.current_path = new_path
    
    def select_item(self, item: str):
        """Select an item in the current view."""
        self.selected_item = item
