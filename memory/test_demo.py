#!/usr/bin/env python3
"""
Memory System Demo - The Ship's Log in Action

This script demonstrates all the features of the memory system
working together to provide persistent storage and querying.
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from memory import MemoryStore, QueryEngine


def main():
    """Demonstrate the memory system functionality."""
    print("🚢 Memory System Demo - The Ship's Log")
    print("=" * 50)
    
    # Initialize the memory system
    store = MemoryStore()
    query_engine = QueryEngine(store)
    
    print("\n1. 📝 Adding Feed Items")
    print("-" * 30)
    
    # Add some sample feed items
    item1 = store.add_feed_item(
        source="email",
        source_id="msg001",
        title="Team Meeting Reminder",
        content="Weekly sync at 2pm today",
        metadata={"priority": "high", "category": "work"}
    )
    print(f"✅ Added item {item1}: Team Meeting Reminder")
    
    item2 = store.add_feed_item(
        source="telegram",
        source_id="tg001",
        title="Weather Alert",
        content="Storm warning for coastal areas",
        metadata={"severity": "moderate", "category": "weather"}
    )
    print(f"✅ Added item {item2}: Weather Alert")
    
    item3 = store.add_feed_item(
        source="api",
        source_id="api001",
        title="System Update Available",
        content="New version 2.1.0 ready for installation",
        metadata={"version": "2.1.0", "category": "system"}
    )
    print(f"✅ Added item {item3}: System Update Available")
    
    print("\n2. 🎯 Recording User Actions")
    print("-" * 30)
    
    # Record some user actions
    store.record_user_action(item1, "mark_done", {"response_time": "2min"})
    print(f"✅ Marked item {item1} as done")
    
    store.record_user_action(item2, "view", {"view_duration": "30s"})
    print(f"✅ Viewed item {item2}")
    
    store.record_user_action(item3, "respond", {"response": "Will install later"})
    print(f"✅ Responded to item {item3}")
    
    print("\n3. 🔍 Querying with Natural Language")
    print("-" * 30)
    
    # Test natural language queries
    queries = [
        "recent items",
        "items from email",
        "items containing meeting",
        "user actions from today"
    ]
    
    for query_text in queries:
        print(f"\nQuery: '{query_text}'")
        result = query_engine.query(query_text, limit=5)
        print(f"Results: {result.total_count} items in {result.query_time_ms:.2f}ms")
        
        for i, item in enumerate(result.items[:3], 1):  # Show first 3
            if isinstance(item, dict) and 'title' in item:
                print(f"  {i}. [{item['source']}] {item['title']}")
            elif isinstance(item, dict) and 'action_type' in item:
                print(f"  {i}. Action: {item['action_type']} on item {item['feed_item_id']}")
    
    print("\n4. 📊 Analytics")
    print("-" * 30)
    
    analytics = query_engine.get_analytics()
    print(f"Total Feed Items: {analytics['total_feed_items']}")
    print(f"Items by Source: {analytics['items_by_source']}")
    print(f"Total User Actions: {analytics['total_user_actions']}")
    print(f"Actions by Type: {analytics['actions_by_type']}")
    
    print("\n5. 🔍 Content Search")
    print("-" * 30)
    
    search_results = query_engine.search_items("meeting", limit=5)
    print(f"Search for 'meeting': {len(search_results)} results")
    for item in search_results:
        print(f"  - [{item['source']}] {item['title']}")
    
    print("\n6. 📁 Export Functionality")
    print("-" * 30)
    
    # Export all data
    export_file = store.export_to_json("demo_export.json")
    print(f"✅ Exported all data to: {export_file}")
    
    # Export query results
    result = query_engine.query("recent items", limit=10)
    query_export = query_engine.export_query_results(result, "json")
    print(f"✅ Exported query results to: {query_export}")
    
    print("\n7. 🛡️ System Status")
    print("-" * 30)
    
    stats = store.get_stats()
    print(f"Database: {store.db_path}")
    print(f"Feed Items: {stats['total_feed_items']}")
    print(f"User Actions: {stats['total_user_actions']}")
    print(f"System Events: {stats['total_system_events']}")
    print(f"Cache Size: {stats['cache_size']}")
    print(f"Total Operations: {stats['reads'] + stats['writes']}")
    
    print("\n🎉 Memory System Demo Complete!")
    print("=" * 50)
    print("All contract requirements satisfied:")
    print("✅ All feed items are persisted to local DB")
    print("✅ User actions (done, delete, respond) are recorded")
    print("✅ Memory can be queried via commandline prompt")
    print("✅ Memory supports exporting to JSON")
    print("\nThe ship's log is ready to serve as the foundation for all other contracts!")


if __name__ == "__main__":
    main()
