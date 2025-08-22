"""
Memory System CLI - The Ship's Bridge

Command-line interface for the memory system, providing easy access
to all memory operations, queries, and analytics.
"""

import argparse
import json
import sys
from datetime import datetime
from typing import Optional

from .memory_store import MemoryStore
from .query_engine import QueryEngine


class MemoryCLI:
    """Command-line interface for the memory system."""
    
    def __init__(self, db_path: Optional[str] = None):
        self.memory_store = MemoryStore(db_path or "memory/megamind_memory.db")
        self.query_engine = QueryEngine(self.memory_store)
    
    def add_feed_item(self, source: str, source_id: str, title: str, 
                     content: Optional[str] = None, metadata: Optional[str] = None):
        """Add a new feed item."""
        try:
            metadata_dict = json.loads(metadata) if metadata else None
            item_id = self.memory_store.add_feed_item(source, source_id, title, content, metadata_dict)
            print(f"✅ Added feed item: {item_id} - {title}")
        except Exception as e:
            print(f"❌ Error adding feed item: {e}")
            sys.exit(1)
    
    def record_action(self, feed_item_id: int, action_type: str, metadata: Optional[str] = None):
        """Record a user action."""
        try:
            metadata_dict = json.loads(metadata) if metadata else None
            action = self.memory_store.record_user_action(feed_item_id, action_type, metadata_dict)
            print(f"✅ Recorded action: {action_type} on item {feed_item_id}")
        except Exception as e:
            print(f"❌ Error recording action: {e}")
            sys.exit(1)
    
    def log_event(self, event_type: str, description: str, metadata: Optional[str] = None):
        """Log a system event."""
        try:
            metadata_dict = json.loads(metadata) if metadata else None
            event = self.memory_store.log_system_event(event_type, description, metadata_dict)
            print(f"✅ Logged event: {event_type} - {description}")
        except Exception as e:
            print(f"❌ Error logging event: {e}")
            sys.exit(1)
    
    def query(self, query_text: str, limit: int = 100, export_format: Optional[str] = None):
        """Execute a query."""
        try:
            result = self.query_engine.query(query_text, limit)
            
            print(f"\n🔍 Query Results ({result.total_count} items, {result.query_time_ms:.2f}ms)")
            print(f"Query: {query_text}")
            print(f"Type: {result.query_type}")
            print(f"Filters: {result.filters_applied}")
            print("-" * 80)
            
            for i, item in enumerate(result.items, 1):
                if isinstance(item, dict) and 'title' in item:
                    print(f"{i}. [{item['source']}] {item['title']}")
                    if item.get('content'):
                        print(f"   {item['content'][:100]}...")
                elif hasattr(item, 'action_type'):
                    print(f"{i}. Action: {item.action_type} on item {item.feed_item_id}")
                elif hasattr(item, 'event_type'):
                    print(f"{i}. Event: {item.event_type} - {item.description}")
                print()
            
            if export_format:
                export_file = self.query_engine.export_query_results(result, export_format)
                print(f"📁 Exported results to: {export_file}")
                
        except Exception as e:
            print(f"❌ Error executing query: {e}")
            sys.exit(1)
    
    def search(self, search_term: str, limit: int = 50):
        """Search feed items."""
        try:
            items = self.query_engine.search_items(search_term, limit)
            
            print(f"\n🔍 Search Results for '{search_term}' ({len(items)} items)")
            print("-" * 80)
            
            for i, item in enumerate(items, 1):
                print(f"{i}. [{item['source']}] {item['title']}")
                if item.get('content'):
                    print(f"   {item['content'][:100]}...")
                print()
                
        except Exception as e:
            print(f"❌ Error searching: {e}")
            sys.exit(1)
    
    def analytics(self):
        """Show analytics."""
        try:
            stats = self.query_engine.get_analytics()
            
            print("\n📊 Memory System Analytics")
            print("=" * 50)
            
            print(f"📝 Feed Items: {stats['total_feed_items']}")
            print(f"   Recent (7 days): {stats['recent_items_7_days']}")
            
            if stats['items_by_source']:
                print("   By Source:")
                for source, count in stats['items_by_source'].items():
                    print(f"     {source}: {count}")
            
            print(f"\n🎯 User Actions: {stats['total_user_actions']}")
            if stats['actions_by_type']:
                print("   By Type:")
                for action_type, count in stats['actions_by_type'].items():
                    print(f"     {action_type}: {count}")
            
            print(f"\n⚙️  System Events: {stats['total_system_events']}")
            print(f"   Recent (7 days): {stats['recent_events_7_days']}")
            
            # Performance stats
            perf_stats = self.memory_store.get_stats()
            print(f"\n⚡ Performance Stats:")
            print(f"   Reads: {perf_stats['reads']}")
            print(f"   Writes: {perf_stats['writes']}")
            print(f"   Cache hits: {perf_stats['cache_hits']}")
            print(f"   Cache size: {perf_stats['cache_size']}")
            
        except Exception as e:
            print(f"❌ Error getting analytics: {e}")
            sys.exit(1)
    
    def export_all(self, output_path: str = "memory_export.json"):
        """Export all memory data."""
        try:
            export_file = self.memory_store.export_to_json(output_path)
            print(f"✅ Exported all memory data to: {export_file}")
        except Exception as e:
            print(f"❌ Error exporting data: {e}")
            sys.exit(1)
    
    def backup(self, backup_path: Optional[str] = None):
        """Create a database backup."""
        try:
            backup_file = self.memory_store.backup_database(backup_path)
            print(f"✅ Database backed up to: {backup_file}")
        except Exception as e:
            print(f"❌ Error creating backup: {e}")
            sys.exit(1)
    
    def cleanup(self, days: int = 90):
        """Clean up old data."""
        try:
            self.memory_store.cleanup_old_data(days)
            print(f"✅ Cleaned up data older than {days} days")
        except Exception as e:
            print(f"❌ Error cleaning up data: {e}")
            sys.exit(1)
    
    def status(self):
        """Show system status."""
        try:
            stats = self.memory_store.get_stats()
            
            print("\n🚢 Memory System Status")
            print("=" * 30)
            print(f"Database: {self.memory_store.db_path}")
            print(f"Feed Items: {stats['total_feed_items']}")
            print(f"User Actions: {stats['total_user_actions']}")
            print(f"System Events: {stats['total_system_events']}")
            print(f"Cache Size: {stats['cache_size']}")
            print(f"Total Queries: {stats['reads'] + stats['writes']}")
            print(f"Cache Hit Rate: {stats['cache_hits'] / max(stats['reads'], 1) * 100:.1f}%")
            
        except Exception as e:
            print(f"❌ Error getting status: {e}")
            sys.exit(1)


def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description="Memory System CLI - The Ship's Log",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Add a feed item
  python -m memory.cli add-item email msg123 "Meeting reminder" "Team sync at 3pm"
  
  # Record an action
  python -m memory.cli record-action 1 mark_done
  
  # Query recent items
  python -m memory.cli query "recent items from email"
  
  # Search for content
  python -m memory.cli search "meeting"
  
  # Show analytics
  python -m memory.cli analytics
  
  # Export all data
  python -m memory.cli export-all
        """
    )
    
    parser.add_argument("--db-path", help="Database path")
    
    subparsers = parser.add_subparsers(dest="command", help="Available commands")
    
    # Add feed item
    add_parser = subparsers.add_parser("add-item", help="Add a feed item")
    add_parser.add_argument("source", help="Source name (email, telegram, etc.)")
    add_parser.add_argument("source_id", help="Original ID from source")
    add_parser.add_argument("title", help="Item title")
    add_parser.add_argument("--content", help="Item content")
    add_parser.add_argument("--metadata", help="JSON metadata")
    
    # Record action
    action_parser = subparsers.add_parser("record-action", help="Record a user action")
    action_parser.add_argument("feed_item_id", type=int, help="Feed item ID")
    action_parser.add_argument("action_type", help="Action type (mark_done, delete, respond, view)")
    action_parser.add_argument("--metadata", help="JSON metadata")
    
    # Log event
    event_parser = subparsers.add_parser("log-event", help="Log a system event")
    event_parser.add_argument("event_type", help="Event type")
    event_parser.add_argument("description", help="Event description")
    event_parser.add_argument("--metadata", help="JSON metadata")
    
    # Query
    query_parser = subparsers.add_parser("query", help="Execute a query")
    query_parser.add_argument("query_text", help="Query text (natural language)")
    query_parser.add_argument("--limit", type=int, default=100, help="Result limit")
    query_parser.add_argument("--export", choices=["json", "csv"], help="Export format")
    
    # Search
    search_parser = subparsers.add_parser("search", help="Search feed items")
    search_parser.add_argument("search_term", help="Search term")
    search_parser.add_argument("--limit", type=int, default=50, help="Result limit")
    
    # Analytics
    subparsers.add_parser("analytics", help="Show analytics")
    
    # Export
    export_parser = subparsers.add_parser("export-all", help="Export all data")
    export_parser.add_argument("--output", default="memory_export.json", help="Output file")
    
    # Backup
    backup_parser = subparsers.add_parser("backup", help="Create database backup")
    backup_parser.add_argument("--path", help="Backup path")
    
    # Cleanup
    cleanup_parser = subparsers.add_parser("cleanup", help="Clean up old data")
    cleanup_parser.add_argument("--days", type=int, default=90, help="Days to keep")
    
    # Status
    subparsers.add_parser("status", help="Show system status")
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return
    
    cli = MemoryCLI(args.db_path)
    
    # Execute command
    if args.command == "add-item":
        cli.add_feed_item(args.source, args.source_id, args.title, args.content, args.metadata)
    elif args.command == "record-action":
        cli.record_action(args.feed_item_id, args.action_type, args.metadata)
    elif args.command == "log-event":
        cli.log_event(args.event_type, args.description, args.metadata)
    elif args.command == "query":
        cli.query(args.query_text, args.limit, args.export)
    elif args.command == "search":
        cli.search(args.search_term, args.limit)
    elif args.command == "analytics":
        cli.analytics()
    elif args.command == "export-all":
        cli.export_all(args.output)
    elif args.command == "backup":
        cli.backup(args.path)
    elif args.command == "cleanup":
        cli.cleanup(args.days)
    elif args.command == "status":
        cli.status()


if __name__ == "__main__":
    main()
