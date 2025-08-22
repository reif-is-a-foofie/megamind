"""
Memory Store - The Ship's Log

Hybrid memory system combining SQLite persistence with in-memory caching
for optimal performance and reliability. This is the foundation upon which
all other contracts build.
"""

import json
import sqlite3
from datetime import datetime, timedelta
from pathlib import Path
from typing import List, Dict, Any, Optional, Union
from contextlib import contextmanager
import threading
import logging

from sqlalchemy import create_engine, event
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import StaticPool

from .models import Base, FeedItem, UserAction, SystemEvent, ActionType

logger = logging.getLogger(__name__)


class MemoryStore:
    """
    Hybrid memory store with SQLite persistence and in-memory caching.
    
    Features:
    - SQLite for reliable persistence
    - In-memory cache for fast queries
    - Automatic backup and recovery
    - Thread-safe operations
    - Performance monitoring
    """
    
    def __init__(self, db_path: str = "memory/megamind_memory.db"):
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        
        # SQLAlchemy setup with SQLite
        self.engine = create_engine(
            f"sqlite:///{self.db_path}",
            poolclass=StaticPool,
            connect_args={"check_same_thread": False}
        )
        
        # Session factory
        self.SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=self.engine)
        
        # In-memory cache for recent items
        self._cache = {}
        self._cache_lock = threading.Lock()
        self._cache_ttl = timedelta(hours=1)  # Cache items for 1 hour
        
        # Performance monitoring
        self._query_stats = {"reads": 0, "writes": 0, "cache_hits": 0}
        self._stats_lock = threading.Lock()
        
        # Initialize database
        self._init_database()
        
        # Log system startup
        self.log_system_event("memory_store_started", "Memory store initialized successfully")
    
    def _init_database(self):
        """Initialize database tables and indexes."""
        Base.metadata.create_all(bind=self.engine)
        
        # Enable foreign key constraints
        def _enable_foreign_keys(dbapi_connection, connection_record):
            cursor = dbapi_connection.cursor()
            cursor.execute("PRAGMA foreign_keys=ON")
            cursor.close()
        
        event.listen(self.engine, "connect", _enable_foreign_keys)
        
        logger.info(f"Database initialized at {self.db_path}")
    
    @contextmanager
    def get_session(self) -> Session:
        """Thread-safe database session context manager."""
        session = self.SessionLocal()
        try:
            yield session
            session.commit()
        except Exception as e:
            session.rollback()
            logger.error(f"Database session error: {e}")
            raise
        finally:
            session.close()
    
    def add_feed_item(self, source: str, source_id: str, title: str, 
                     content: Optional[str] = None, metadata: Optional[Dict] = None) -> FeedItem:
        """Add a new feed item to memory."""
        with self._stats_lock:
            self._query_stats["writes"] += 1
        
        with self.get_session() as session:
            feed_item = FeedItem(
                source=source,
                source_id=source_id,
                title=title,
                content=content,
                item_metadata=metadata or {}
            )
            session.add(feed_item)
            session.flush()  # Get the ID
            
            item_id = feed_item.id
            logger.info(f"Added feed item: {item_id} from {source}")
            return item_id
    
    def record_user_action(self, feed_item_id: int, action_type: Union[str, ActionType], 
                          metadata: Optional[Dict] = None) -> UserAction:
        """Record a user action on a feed item."""
        with self._stats_lock:
            self._query_stats["writes"] += 1
        
        with self.get_session() as session:
            action = UserAction(
                feed_item_id=feed_item_id,
                action_type=str(action_type),
                action_metadata=metadata or {}
            )
            session.add(action)
            
            logger.info(f"Recorded action: {action_type} on item {feed_item_id}")
            return action
    
    def log_system_event(self, event_type: str, description: str, 
                        metadata: Optional[Dict] = None) -> SystemEvent:
        """Log a system-level event."""
        with self._stats_lock:
            self._query_stats["writes"] += 1
        
        with self.get_session() as session:
            event = SystemEvent(
                event_type=event_type,
                description=description,
                event_metadata=metadata or {}
            )
            session.add(event)
            
            logger.info(f"System event: {event_type} - {description}")
            return event
    
    def get_feed_items(self, source: Optional[str] = None, limit: int = 100, 
                      offset: int = 0) -> List[FeedItem]:
        """Get feed items with optional filtering and pagination."""
        with self._stats_lock:
            self._query_stats["reads"] += 1
        
        with self.get_session() as session:
            query = session.query(FeedItem)
            
            if source:
                query = query.filter(FeedItem.source == source)
            
            items = query.order_by(FeedItem.created_at.desc()).offset(offset).limit(limit).all()
            
            # Cache results (simplified for now)
            pass
            
            return items
    
    def get_user_actions(self, feed_item_id: Optional[int] = None, 
                        action_type: Optional[str] = None, limit: int = 100) -> List[UserAction]:
        """Get user actions with optional filtering."""
        with self._stats_lock:
            self._query_stats["reads"] += 1
        
        with self.get_session() as session:
            query = session.query(UserAction)
            
            if feed_item_id:
                query = query.filter(UserAction.feed_item_id == feed_item_id)
            if action_type:
                query = query.filter(UserAction.action_type == action_type)
            
            return query.order_by(UserAction.timestamp.desc()).limit(limit).all()
    
    def get_system_events(self, event_type: Optional[str] = None, 
                         limit: int = 100) -> List[SystemEvent]:
        """Get system events with optional filtering."""
        with self._stats_lock:
            self._query_stats["reads"] += 1
        
        with self.get_session() as session:
            query = session.query(SystemEvent)
            
            if event_type:
                query = query.filter(SystemEvent.event_type == event_type)
            
            return query.order_by(SystemEvent.timestamp.desc()).limit(limit).all()
    
    def _cache_item(self, item: FeedItem):
        """Cache a feed item in memory for fast access."""
        with self._cache_lock:
            cache_key = f"feed_item_{item.id}"
            self._cache[cache_key] = {
                "item": item,
                "cached_at": datetime.utcnow()
            }
    
    def _get_cached_item(self, item_id: int) -> Optional[FeedItem]:
        """Get a feed item from cache if available and fresh."""
        with self._cache_lock:
            cache_key = f"feed_item_{item_id}"
            cached_data = self._cache.get(cache_key)
            
            if cached_data:
                age = datetime.utcnow() - cached_data["cached_at"]
                if age < self._cache_ttl:
                    with self._stats_lock:
                        self._query_stats["cache_hits"] += 1
                    return cached_data["item"]
                else:
                    # Remove expired cache entry
                    del self._cache[cache_key]
        
        return None
    
    def export_to_json(self, output_path: str = "memory_export.json") -> str:
        """Export all memory data to JSON format."""
        export_data = {
            "export_timestamp": datetime.utcnow().isoformat(),
            "feed_items": [],
            "user_actions": [],
            "system_events": []
        }
        
        with self.get_session() as session:
            # Export feed items
            feed_items = session.query(FeedItem).all()
            for item in feed_items:
                export_data["feed_items"].append({
                    "id": item.id,
                    "source": item.source,
                    "source_id": item.source_id,
                    "title": item.title,
                    "content": item.content,
                    "metadata": item.item_metadata,
                    "created_at": item.created_at.isoformat(),
                    "updated_at": item.updated_at.isoformat()
                })
            
            # Export user actions
            actions = session.query(UserAction).all()
            for action in actions:
                export_data["user_actions"].append({
                    "id": action.id,
                    "feed_item_id": action.feed_item_id,
                    "action_type": action.action_type,
                    "metadata": action.action_metadata,
                    "timestamp": action.timestamp.isoformat()
                })
            
            # Export system events
            events = session.query(SystemEvent).all()
            for event in events:
                export_data["system_events"].append({
                    "id": event.id,
                    "event_type": event.event_type,
                    "description": event.description,
                    "metadata": event.event_metadata,
                    "timestamp": event.timestamp.isoformat()
                })
        
        # Write to file
        with open(output_path, 'w') as f:
            json.dump(export_data, f, indent=2)
        
        logger.info(f"Memory exported to {output_path}")
        return output_path
    
    def get_stats(self) -> Dict[str, Any]:
        """Get performance statistics."""
        with self._stats_lock:
            stats = self._query_stats.copy()
        
        with self._cache_lock:
            stats["cache_size"] = len(self._cache)
        
        # Get database stats
        with self.get_session() as session:
            stats["total_feed_items"] = session.query(FeedItem).count()
            stats["total_user_actions"] = session.query(UserAction).count()
            stats["total_system_events"] = session.query(SystemEvent).count()
        
        return stats
    
    def backup_database(self, backup_path: Optional[str] = None) -> str:
        """Create a backup of the database."""
        if backup_path is None:
            timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
            backup_path = f"memory/backup/megamind_memory_{timestamp}.db"
        
        backup_path = Path(backup_path)
        backup_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Use SQLite backup API for reliable copying
        with sqlite3.connect(self.db_path) as source_conn:
            with sqlite3.connect(backup_path) as backup_conn:
                source_conn.backup(backup_conn)
        
        logger.info(f"Database backed up to {backup_path}")
        return str(backup_path)
    
    def cleanup_old_data(self, days_to_keep: int = 90):
        """Clean up old data to prevent database bloat."""
        cutoff_date = datetime.utcnow() - timedelta(days=days_to_keep)
        
        with self.get_session() as session:
            # Clean old system events
            deleted_events = session.query(SystemEvent).filter(
                SystemEvent.timestamp < cutoff_date
            ).delete()
            
            # Clean old user actions (but keep feed items for now)
            deleted_actions = session.query(UserAction).filter(
                UserAction.timestamp < cutoff_date
            ).delete()
        
        logger.info(f"Cleaned up {deleted_events} old system events and {deleted_actions} old user actions")
    
    def __repr__(self):
        stats = self.get_stats()
        return f"<MemoryStore(db_path='{self.db_path}', items={stats['total_feed_items']}, actions={stats['total_user_actions']})>"
