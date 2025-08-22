"""
Memory System Data Models

Defines the core data structures for persistent memory storage.
Uses SQLAlchemy ORM for clean database operations and type safety.
"""

from datetime import datetime
from enum import Enum
from typing import Optional, Dict, Any
from sqlalchemy import Column, Integer, String, Text, DateTime, JSON, Index, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

Base = declarative_base()


class ActionType(Enum):
    """Types of user actions that can be performed on feed items."""
    MARK_DONE = "mark_done"
    DELETE = "delete"
    RESPOND = "respond"
    VIEW = "view"


class FeedItem(Base):
    """Represents a single item in the unified feed."""
    __tablename__ = "feed_items"
    
    id = Column(Integer, primary_key=True)
    source = Column(String(100), nullable=False, index=True)  # email, telegram, api, etc.
    source_id = Column(String(255), nullable=False)  # Original ID from source
    title = Column(String(500), nullable=False)
    content = Column(Text, nullable=True)
    item_metadata = Column(JSON, nullable=True)  # Flexible storage for source-specific data
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    actions = relationship("UserAction", back_populates="feed_item", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<FeedItem(id={self.id}, source='{self.source}', title='{self.title[:50]}...')>"


class UserAction(Base):
    """Records user interactions with feed items."""
    __tablename__ = "user_actions"
    
    id = Column(Integer, primary_key=True)
    feed_item_id = Column(Integer, ForeignKey("feed_items.id"), nullable=False, index=True)
    action_type = Column(String(50), nullable=False, index=True)
    timestamp = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)
    action_metadata = Column(JSON, nullable=True)  # Additional action data (response text, etc.)
    
    # Relationships
    feed_item = relationship("FeedItem", back_populates="actions")
    
    def __repr__(self):
        return f"<UserAction(id={self.id}, action='{self.action_type}', item_id={self.feed_item_id})>"


class SystemEvent(Base):
    """Records system-level events and state changes."""
    __tablename__ = "system_events"
    
    id = Column(Integer, primary_key=True)
    event_type = Column(String(100), nullable=False, index=True)
    description = Column(Text, nullable=False)
    event_metadata = Column(JSON, nullable=True)
    timestamp = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)
    
    def __repr__(self):
        return f"<SystemEvent(id={self.id}, type='{self.event_type}', desc='{self.description[:50]}...')>"


# Performance indexes
Index("idx_feed_items_source_created", FeedItem.source, FeedItem.created_at)
Index("idx_user_actions_type_timestamp", UserAction.action_type, UserAction.timestamp)
Index("idx_system_events_type_timestamp", SystemEvent.event_type, SystemEvent.timestamp)
