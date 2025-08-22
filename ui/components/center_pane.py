"""
Center Pane - Agent Chat Interface

Displays agent interactions and feed items with action capabilities.
"""

from typing import List, Dict, Any, Optional
from datetime import datetime
from rich.panel import Panel
from rich.text import Text
from rich.table import Table
from rich.columns import Columns
from rich.console import Group


class CenterPane:
    """Center pane showing agent chat interface and feed items."""
    
    def __init__(self, feed_connector):
        self.feed_connector = feed_connector
        self.messages = []
        self.selected_item = None
        self.input_buffer = ""
        
        # Initialize with some sample data
        self._load_sample_data()
        
    def render(self) -> Panel:
        """Render the center pane content."""
        content = Group(
            self._render_feed_items(),
            self._render_chat_interface()
        )
        
        return Panel(
            content,
            title="💬 Agent Chat & Feed",
            border_style="green",
            subtitle="Press Enter to interact"
        )
    
    def _render_feed_items(self) -> Table:
        """Render the feed items table."""
        table = Table(title="📰 Unified Feed", show_header=True)
        table.add_column("Time", style="cyan", no_wrap=True)
        table.add_column("Source", style="magenta")
        table.add_column("Content", style="white")
        table.add_column("Status", style="yellow")
        
        # Sample feed items
        feed_items = [
            ("09:15", "📧 Email", "Meeting reminder: Team sync at 10:00", "⏰ Pending"),
            ("09:30", "💰 Finance", "Gold price: $2,150/oz (+2.3%)", "📈 Alert"),
            ("09:45", "🌪️ Weather", "Hurricane warning: Category 2 approaching", "⚠️ Alert"),
            ("10:00", "📅 Calendar", "Team sync meeting starting now", "🎯 Active"),
            ("10:15", "📧 Email", "Project update from client", "📋 New"),
        ]
        
        for time, source, content, status in feed_items:
            table.add_row(time, source, content, status)
            
        return table
    
    def _render_chat_interface(self) -> Text:
        """Render the agent chat interface."""
        chat_text = Text()
        chat_text.append("🤖 Agent Chat\n", style="bold green")
        chat_text.append("=" * 40 + "\n", style="blue")
        
        # Sample chat messages
        chat_messages = [
            ("Captain", "Worker agent, status report on ui.01 contract?"),
            ("Worker", "Implementing three-pane terminal interface with Rich library. Progress: 60%"),
            ("Captain", "Excellent. Focus on core functionality first."),
            ("Worker", "Acknowledged. Will complete layout and basic navigation."),
        ]
        
        for sender, message in chat_messages:
            chat_text.append(f"{sender}: ", style="bold cyan")
            chat_text.append(f"{message}\n", style="white")
        
        chat_text.append("\n" + "=" * 40 + "\n", style="blue")
        chat_text.append("Type your message: ", style="bold yellow")
        chat_text.append(self.input_buffer, style="white")
        
        return chat_text
    
    def _load_sample_data(self):
        """Load sample data for demonstration."""
        self.messages = [
            {
                "timestamp": datetime.now(),
                "sender": "Captain",
                "content": "Worker agent, begin implementation of ui.01 contract.",
                "type": "command"
            },
            {
                "timestamp": datetime.now(),
                "sender": "Worker",
                "content": "Acknowledged. Starting three-pane terminal interface implementation.",
                "type": "response"
            }
        ]
    
    def add_message(self, sender: str, content: str, msg_type: str = "message"):
        """Add a new message to the chat."""
        self.messages.append({
            "timestamp": datetime.now(),
            "sender": sender,
            "content": content,
            "type": msg_type
        })
    
    def select_feed_item(self, index: int):
        """Select a feed item for action."""
        self.selected_item = index
    
    def mark_item_done(self, index: int):
        """Mark a feed item as done."""
        if 0 <= index < len(self.messages):
            # In a real implementation, this would update the feed connector
            pass
    
    def delete_item(self, index: int):
        """Delete a feed item."""
        if 0 <= index < len(self.messages):
            # In a real implementation, this would update the feed connector
            pass
    
    def set_input_buffer(self, text: str):
        """Set the input buffer text."""
        self.input_buffer = text
