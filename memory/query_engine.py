"""
Query Engine - The Ship's Navigator

Provides powerful querying capabilities for the memory system,
including natural language queries and structured data analysis.
"""

import re
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional, Union
from dataclasses import dataclass
import logging

from .memory_store import MemoryStore
from .models import FeedItem, UserAction, SystemEvent

logger = logging.getLogger(__name__)


@dataclass
class QueryResult:
    """Container for query results with metadata."""
    items: List[Any]
    total_count: int
    query_time_ms: float
    query_type: str
    filters_applied: Dict[str, Any]


class QueryEngine:
    """
    Advanced query engine for memory system.
    
    Features:
    - Natural language query parsing
    - Structured filtering and sorting
    - Performance analytics
    - Export capabilities
    """
    
    def __init__(self, memory_store: MemoryStore):
        self.memory_store = memory_store
        
        # Query patterns for natural language parsing
        self._query_patterns = {
            "recent_items": r"(recent|latest|new|today|yesterday)",
            "source_filter": r"(from|in)\s+(\w+)",
            "action_filter": r"(done|deleted|responded|viewed)",
            "time_filter": r"(last|past|previous)\s+(\d+)\s+(day|week|month|hour)s?",
            "search_content": r"(containing|with|about)\s+(.+)"
        }
    
    def query(self, query_text: str, limit: int = 100) -> QueryResult:
        """
        Execute a natural language or structured query.
        
        Examples:
        - "recent items from email"
        - "items done in the last 3 days"
        - "all items containing meeting"
        """
        import time
        start_time = time.time()
        
        # Parse query
        filters = self._parse_query(query_text)
        
        # Execute query based on type
        if filters.get("query_type") == "feed_items":
            items = self._query_feed_items(filters, limit)
        elif filters.get("query_type") == "user_actions":
            items = self._query_user_actions(filters, limit)
        elif filters.get("query_type") == "system_events":
            items = self._query_system_events(filters, limit)
        else:
            # Default to feed items
            items = self._query_feed_items(filters, limit)
        
        query_time = (time.time() - start_time) * 1000
        
        return QueryResult(
            items=items,
            total_count=len(items),
            query_time_ms=query_time,
            query_type=filters.get("query_type", "feed_items"),
            filters_applied=filters
        )
    
    def _parse_query(self, query_text: str) -> Dict[str, Any]:
        """Parse natural language query into structured filters."""
        query_lower = query_text.lower()
        filters = {"query_type": "feed_items"}
        
        # Check for recent items
        if re.search(self._query_patterns["recent_items"], query_lower):
            filters["recent"] = True
            filters["time_range"] = "recent"
        
        # Check for source filter
        source_match = re.search(self._query_patterns["source_filter"], query_lower)
        if source_match:
            filters["source"] = source_match.group(2)
        
        # Check for action filter
        action_match = re.search(self._query_patterns["action_filter"], query_lower)
        if action_match:
            action = action_match.group(1)
            if action == "done":
                filters["action_type"] = "mark_done"
            elif action == "deleted":
                filters["action_type"] = "delete"
            elif action == "responded":
                filters["action_type"] = "respond"
            elif action == "viewed":
                filters["action_type"] = "view"
        
        # Check for time range
        time_match = re.search(self._query_patterns["time_filter"], query_lower)
        if time_match:
            amount = int(time_match.group(2))
            unit = time_match.group(3)
            filters["time_range"] = {"amount": amount, "unit": unit}
        
        # Check for content search
        content_match = re.search(self._query_patterns["search_content"], query_lower)
        if content_match:
            filters["search_term"] = content_match.group(2)
        
        # Determine query type based on keywords
        if any(word in query_lower for word in ["action", "done", "deleted", "responded"]):
            filters["query_type"] = "user_actions"
        elif any(word in query_lower for word in ["event", "system", "log"]):
            filters["query_type"] = "system_events"
        
        return filters
    
    def _query_feed_items(self, filters: Dict[str, Any], limit: int) -> List[Dict[str, Any]]:
        """Query feed items with filters."""
        with self.memory_store.get_session() as session:
            query = session.query(FeedItem)
            
            # Apply source filter
            if "source" in filters:
                query = query.filter(FeedItem.source == filters["source"])
            
            # Apply time range filter
            if "time_range" in filters:
                if filters["time_range"] == "recent":
                    # Last 24 hours
                    cutoff = datetime.utcnow() - timedelta(days=1)
                    query = query.filter(FeedItem.created_at >= cutoff)
                elif isinstance(filters["time_range"], dict):
                    amount = filters["time_range"]["amount"]
                    unit = filters["time_range"]["unit"]
                    
                    if unit == "day":
                        cutoff = datetime.utcnow() - timedelta(days=amount)
                    elif unit == "week":
                        cutoff = datetime.utcnow() - timedelta(weeks=amount)
                    elif unit == "month":
                        cutoff = datetime.utcnow() - timedelta(days=amount * 30)
                    elif unit == "hour":
                        cutoff = datetime.utcnow() - timedelta(hours=amount)
                    
                    query = query.filter(FeedItem.created_at >= cutoff)
            
            # Apply content search
            if "search_term" in filters:
                search_term = f"%{filters['search_term']}%"
                query = query.filter(
                    (FeedItem.title.contains(search_term)) |
                    (FeedItem.content.contains(search_term))
                )
            
            items = query.order_by(FeedItem.created_at.desc()).limit(limit).all()
            
            # Convert to dictionaries to avoid session binding issues
            return [
                {
                    "id": item.id,
                    "source": item.source,
                    "source_id": item.source_id,
                    "title": item.title,
                    "content": item.content,
                    "item_metadata": item.item_metadata,
                    "created_at": item.created_at,
                    "updated_at": item.updated_at
                }
                for item in items
            ]
    
    def _query_user_actions(self, filters: Dict[str, Any], limit: int) -> List[Dict[str, Any]]:
        """Query user actions with filters."""
        with self.memory_store.get_session() as session:
            query = session.query(UserAction)
            
            # Apply action type filter
            if "action_type" in filters:
                query = query.filter(UserAction.action_type == filters["action_type"])
            
            # Apply time range filter
            if "time_range" in filters:
                if filters["time_range"] == "recent":
                    cutoff = datetime.utcnow() - timedelta(days=1)
                    query = query.filter(UserAction.timestamp >= cutoff)
                elif isinstance(filters["time_range"], dict):
                    amount = filters["time_range"]["amount"]
                    unit = filters["time_range"]["unit"]
                    
                    if unit == "day":
                        cutoff = datetime.utcnow() - timedelta(days=amount)
                    elif unit == "week":
                        cutoff = datetime.utcnow() - timedelta(weeks=amount)
                    elif unit == "month":
                        cutoff = datetime.utcnow() - timedelta(days=amount * 30)
                    elif unit == "hour":
                        cutoff = datetime.utcnow() - timedelta(hours=amount)
                    
                    query = query.filter(UserAction.timestamp >= cutoff)
            
            actions = query.order_by(UserAction.timestamp.desc()).limit(limit).all()
            
            # Convert to dictionaries to avoid session binding issues
            return [
                {
                    "id": action.id,
                    "feed_item_id": action.feed_item_id,
                    "action_type": action.action_type,
                    "action_metadata": action.action_metadata,
                    "timestamp": action.timestamp
                }
                for action in actions
            ]
    
    def _query_system_events(self, filters: Dict[str, Any], limit: int) -> List[SystemEvent]:
        """Query system events with filters."""
        with self.memory_store.get_session() as session:
            query = session.query(SystemEvent)
            
            # Apply time range filter
            if "time_range" in filters:
                if filters["time_range"] == "recent":
                    cutoff = datetime.utcnow() - timedelta(days=1)
                    query = query.filter(SystemEvent.timestamp >= cutoff)
                elif isinstance(filters["time_range"], dict):
                    amount = filters["time_range"]["amount"]
                    unit = filters["time_range"]["unit"]
                    
                    if unit == "day":
                        cutoff = datetime.utcnow() - timedelta(days=amount)
                    elif unit == "week":
                        cutoff = datetime.utcnow() - timedelta(weeks=amount)
                    elif unit == "month":
                        cutoff = datetime.utcnow() - timedelta(days=amount * 30)
                    elif unit == "hour":
                        cutoff = datetime.utcnow() - timedelta(hours=amount)
                    
                    query = query.filter(SystemEvent.timestamp >= cutoff)
            
            return query.order_by(SystemEvent.timestamp.desc()).limit(limit).all()
    
    def get_analytics(self) -> Dict[str, Any]:
        """Get analytics and insights from memory data."""
        with self.memory_store.get_session() as session:
            analytics = {}
            
            # Feed item analytics
            total_items = session.query(FeedItem).count()
            analytics["total_feed_items"] = total_items
            
            # Items by source
            source_counts = session.query(FeedItem.source, session.query(FeedItem).filter(
                FeedItem.source == FeedItem.source
            ).count()).group_by(FeedItem.source).all()
            analytics["items_by_source"] = dict(source_counts)
            
            # Recent activity (last 7 days)
            week_ago = datetime.utcnow() - timedelta(days=7)
            recent_items = session.query(FeedItem).filter(
                FeedItem.created_at >= week_ago
            ).count()
            analytics["recent_items_7_days"] = recent_items
            
            # User action analytics
            total_actions = session.query(UserAction).count()
            analytics["total_user_actions"] = total_actions
            
            # Actions by type
            action_counts = session.query(UserAction.action_type, session.query(UserAction).filter(
                UserAction.action_type == UserAction.action_type
            ).count()).group_by(UserAction.action_type).all()
            analytics["actions_by_type"] = dict(action_counts)
            
            # System event analytics
            total_events = session.query(SystemEvent).count()
            analytics["total_system_events"] = total_events
            
            # Recent system events
            recent_events = session.query(SystemEvent).filter(
                SystemEvent.timestamp >= week_ago
            ).count()
            analytics["recent_events_7_days"] = recent_events
            
            return analytics
    
    def search_items(self, search_term: str, limit: int = 50) -> List[Dict[str, Any]]:
        """Search feed items by title and content."""
        with self.memory_store.get_session() as session:
            search_pattern = f"%{search_term}%"
            items = session.query(FeedItem).filter(
                (FeedItem.title.contains(search_pattern)) |
                (FeedItem.content.contains(search_pattern))
            ).order_by(FeedItem.created_at.desc()).limit(limit).all()
            
            # Convert to dictionaries to avoid session binding issues
            return [
                {
                    "id": item.id,
                    "source": item.source,
                    "source_id": item.source_id,
                    "title": item.title,
                    "content": item.content,
                    "item_metadata": item.item_metadata,
                    "created_at": item.created_at,
                    "updated_at": item.updated_at
                }
                for item in items
            ]
    
    def get_items_by_source(self, source: str, limit: int = 100) -> List[FeedItem]:
        """Get all items from a specific source."""
        return self.memory_store.get_feed_items(source=source, limit=limit)
    
    def get_recent_actions(self, hours: int = 24, limit: int = 100) -> List[UserAction]:
        """Get recent user actions."""
        cutoff = datetime.utcnow() - timedelta(hours=hours)
        
        with self.memory_store.get_session() as session:
            return session.query(UserAction).filter(
                UserAction.timestamp >= cutoff
            ).order_by(UserAction.timestamp.desc()).limit(limit).all()
    
    def export_query_results(self, query_result: QueryResult, format: str = "json") -> str:
        """Export query results to various formats."""
        if format == "json":
            return self._export_to_json(query_result)
        elif format == "csv":
            return self._export_to_csv(query_result)
        else:
            raise ValueError(f"Unsupported export format: {format}")
    
    def _export_to_json(self, query_result: QueryResult) -> str:
        """Export query results to JSON."""
        import json
        from datetime import datetime
        
        export_data = {
            "query_info": {
                "query_type": query_result.query_type,
                "total_count": query_result.total_count,
                "query_time_ms": query_result.query_time_ms,
                "filters_applied": query_result.filters_applied,
                "export_timestamp": datetime.utcnow().isoformat()
            },
            "results": []
        }
        
        for item in query_result.items:
            if isinstance(item, FeedItem):
                export_data["results"].append({
                    "type": "feed_item",
                    "id": item.id,
                    "source": item.source,
                    "title": item.title,
                    "content": item.content,
                    "created_at": item.created_at.isoformat()
                })
            elif isinstance(item, UserAction):
                export_data["results"].append({
                    "type": "user_action",
                    "id": item.id,
                    "feed_item_id": item.feed_item_id,
                    "action_type": item.action_type,
                    "timestamp": item.timestamp.isoformat()
                })
            elif isinstance(item, SystemEvent):
                export_data["results"].append({
                    "type": "system_event",
                    "id": item.id,
                    "event_type": item.event_type,
                    "description": item.description,
                    "timestamp": item.timestamp.isoformat()
                })
        
        filename = f"query_export_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}.json"
        with open(filename, 'w') as f:
            json.dump(export_data, f, indent=2)
        
        return filename
    
    def _export_to_csv(self, query_result: QueryResult) -> str:
        """Export query results to CSV."""
        import csv
        from datetime import datetime
        
        filename = f"query_export_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}.csv"
        
        with open(filename, 'w', newline='') as csvfile:
            if query_result.items:
                # Determine fieldnames based on first item
                first_item = query_result.items[0]
                if isinstance(first_item, FeedItem):
                    fieldnames = ['id', 'source', 'title', 'content', 'created_at']
                elif isinstance(first_item, UserAction):
                    fieldnames = ['id', 'feed_item_id', 'action_type', 'timestamp']
                elif isinstance(first_item, SystemEvent):
                    fieldnames = ['id', 'event_type', 'description', 'timestamp']
                else:
                    fieldnames = []
                
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                writer.writeheader()
                
                for item in query_result.items:
                    if isinstance(item, FeedItem):
                        writer.writerow({
                            'id': item.id,
                            'source': item.source,
                            'title': item.title,
                            'content': item.content or '',
                            'created_at': item.created_at.isoformat()
                        })
                    elif isinstance(item, UserAction):
                        writer.writerow({
                            'id': item.id,
                            'feed_item_id': item.feed_item_id,
                            'action_type': item.action_type,
                            'timestamp': item.timestamp.isoformat()
                        })
                    elif isinstance(item, SystemEvent):
                        writer.writerow({
                            'id': item.id,
                            'event_type': item.event_type,
                            'description': item.description,
                            'timestamp': item.timestamp.isoformat()
                        })
        
        return filename
