# Memory System - The Ship's Log

The Memory System is the foundational component of the Megamind project, providing persistent storage for all feed history, user actions, and system events. It's designed as a hybrid system combining SQLite persistence with in-memory caching for optimal performance and reliability.

## 🚢 Mission Context

> "We commission galleons whose berth we'll never meet; They shall pirate ever on, those blistered, wretched seas."

The Memory System is our galleon's log - the reliable foundation that records every voyage through the data seas. All other contracts build upon this persistent memory.

## 🏗️ Architecture

### Hybrid Memory Design
- **SQLite Database**: Reliable persistence with ACID compliance
- **In-Memory Cache**: Fast access to recent items (1-hour TTL)
- **Thread-Safe Operations**: Concurrent access support
- **Performance Monitoring**: Built-in query statistics

### Core Components
- `MemoryStore`: Main storage engine with hybrid architecture
- `QueryEngine`: Natural language and structured querying
- `CLI`: Command-line interface for all operations
- `Models`: SQLAlchemy ORM models for type safety

## 📦 Installation

```bash
# Install dependencies
pip install -r memory/requirements.txt

# Initialize database (automatic on first use)
python -m memory.cli status
```

## 🚀 Quick Start

### Basic Operations

```python
from memory import MemoryStore, QueryEngine

# Initialize
store = MemoryStore()
query_engine = QueryEngine(store)

# Add a feed item
item = store.add_feed_item(
    source="email",
    source_id="msg123",
    title="Meeting reminder",
    content="Team sync at 3pm"
)

# Record user action
store.record_user_action(item.id, "mark_done")

# Query with natural language
results = query_engine.query("recent items from email")
```

### Command Line Interface

```bash
# Add a feed item
python -m memory.cli add-item email msg123 "Meeting reminder" "Team sync at 3pm"

# Record an action
python -m memory.cli record-action 1 mark_done

# Query recent items
python -m memory.cli query "recent items from email"

# Show analytics
python -m memory.cli analytics

# Export all data
python -m memory.cli export-all
```

## 🔍 Query Capabilities

### Natural Language Queries
- `"recent items from email"`
- `"items done in the last 3 days"`
- `"all items containing meeting"`
- `"user actions from yesterday"`
- `"system events in the past week"`

### Structured Queries
```python
# Get items by source
items = query_engine.get_items_by_source("email", limit=50)

# Search content
results = query_engine.search_items("meeting", limit=25)

# Get recent actions
actions = query_engine.get_recent_actions(hours=24)
```

## 📊 Analytics

The system provides comprehensive analytics:

```python
analytics = query_engine.get_analytics()
print(f"Total items: {analytics['total_feed_items']}")
print(f"Items by source: {analytics['items_by_source']}")
print(f"Actions by type: {analytics['actions_by_type']}")
```

## 💾 Data Models

### FeedItem
- `id`: Primary key
- `source`: Source name (email, telegram, api, etc.)
- `source_id`: Original ID from source
- `title`: Item title
- `content`: Item content (optional)
- `metadata`: Flexible JSON storage
- `created_at`: Creation timestamp
- `updated_at`: Last update timestamp

### UserAction
- `id`: Primary key
- `feed_item_id`: Reference to feed item
- `action_type`: Type of action (mark_done, delete, respond, view)
- `timestamp`: Action timestamp
- `metadata`: Additional action data

### SystemEvent
- `id`: Primary key
- `event_type`: Event type
- `description`: Event description
- `metadata`: Event data
- `timestamp`: Event timestamp

## 🔧 Performance Features

### Caching Strategy
- **In-Memory Cache**: Recent items cached for 1 hour
- **Cache Hit Rate**: Monitored and reported
- **Automatic Expiration**: Stale cache entries removed

### Database Optimization
- **Indexed Queries**: Performance indexes on common fields
- **Connection Pooling**: Efficient database connections
- **Batch Operations**: Optimized for bulk operations

### Monitoring
```python
stats = store.get_stats()
print(f"Cache hit rate: {stats['cache_hits'] / stats['reads'] * 100:.1f}%")
print(f"Total operations: {stats['reads'] + stats['writes']}")
```

## 🛡️ Reliability Features

### Backup & Recovery
```bash
# Create backup
python -m memory.cli backup

# Automatic backup with timestamp
python -m memory.cli backup --path memory/backup/custom_backup.db
```

### Data Export
```bash
# Export all data to JSON
python -m memory.cli export-all

# Export query results
python -m memory.cli query "recent items" --export json
python -m memory.cli query "user actions" --export csv
```

### Data Cleanup
```bash
# Clean up old data (default: 90 days)
python -m memory.cli cleanup

# Custom retention period
python -m memory.cli cleanup --days 30
```

## 🔮 Future Scaling

The system is designed for future expansion:

### Database Migration
- Easy migration from SQLite to PostgreSQL
- Connection string configuration
- Schema compatibility

### Advanced Caching
- Redis integration for distributed caching
- Cache invalidation strategies
- Multi-node support

### Analytics Enhancement
- Pandas integration for advanced analytics
- Time-series analysis
- Predictive modeling

## 🧪 Testing

```bash
# Run memory system tests
python -m pytest tests/test_memory.py

# Test CLI functionality
python -m memory.cli status
python -m memory.cli analytics
```

## 📋 Contract Compliance

This implementation satisfies all `memory.01` contract requirements:

✅ **All feed items are persisted to local DB**  
✅ **User actions (done, delete, respond) are recorded**  
✅ **Memory can be queried via commandline prompt**  
✅ **Memory supports exporting to JSON**  

## 🎯 Integration Points

The Memory System integrates with other contracts:

- **Feed Aggregator**: Stores incoming feed items
- **UI Framework**: Provides data for display
- **Notification System**: Logs meeting alerts and actions
- **Gamification**: Tracks user progress and XP events

## 🚨 Error Handling

The system includes comprehensive error handling:

- **Database Connection Errors**: Automatic retry with backoff
- **Invalid Data**: Validation and graceful degradation
- **File System Errors**: Backup and recovery procedures
- **Memory Errors**: Cache cleanup and database fallback

## 📞 Support

For issues or questions about the Memory System:

1. Check the logs: `python -m memory.cli status`
2. Review analytics: `python -m memory.cli analytics`
3. Export data for debugging: `python -m memory.cli export-all`

---

*"Our abacus is quiet-kept, we're absent honor's roll; we dive, we drown, we reif as one — we ransom for the Pearl."*

The Memory System is our quiet abacus, keeping the ship's log with precision and reliability.
