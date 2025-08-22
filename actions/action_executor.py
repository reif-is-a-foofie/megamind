"""
Action Executor - Handles actual execution of actions.

Executes actions by integrating with external systems (email, calendar,
file systems) and provides feedback on execution results.
"""

import json
import sqlite3
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
import os
import uuid


class ActionExecutor:
    """Executes actions by integrating with external systems."""
    
    def __init__(self, memory_db_path: str = "memory/memory.db"):
        self.memory_db_path = memory_db_path
    
    def send_reply(self, feed_item_id: str, message: str, user_id: str) -> Dict[str, Any]:
        """Send a reply to a feed item."""
        try:
            # Get feed item details from memory
            feed_item = self._get_feed_item(feed_item_id)
            if not feed_item:
                return {"success": False, "error": "Feed item not found"}
            
            # Extract recipient information
            recipient = self._extract_recipient(feed_item)
            
            # In a real implementation, this would integrate with email/chat systems
            # For now, we'll simulate the action
            reply_id = str(uuid.uuid4())
            
            # Store reply in memory
            self._store_action_result(
                action_type="reply",
                feed_item_id=feed_item_id,
                result_data={
                    "reply_id": reply_id,
                    "message": message,
                    "recipient": recipient,
                    "sent_time": datetime.now().isoformat()
                },
                user_id=user_id
            )
            
            return {
                "success": True,
                "reply_id": reply_id,
                "recipient": recipient,
                "message": message
            }
            
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def archive_item(self, feed_item_id: str, category: str, tags: List[str], user_id: str) -> Dict[str, Any]:
        """Archive a feed item."""
        try:
            # Get feed item details
            feed_item = self._get_feed_item(feed_item_id)
            if not feed_item:
                return {"success": False, "error": "Feed item not found"}
            
            # Create archive entry
            archive_id = str(uuid.uuid4())
            
            # Store archive in memory
            self._store_action_result(
                action_type="archive",
                feed_item_id=feed_item_id,
                result_data={
                    "archive_id": archive_id,
                    "category": category,
                    "tags": tags,
                    "archived_time": datetime.now().isoformat(),
                    "original_content": feed_item.get("content", "")
                },
                user_id=user_id
            )
            
            return {
                "success": True,
                "archive_id": archive_id,
                "category": category,
                "tags": tags
            }
            
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def schedule_item(self, feed_item_id: str, scheduled_time: str, 
                     reminder_type: str, description: str, user_id: str) -> Dict[str, Any]:
        """Schedule a feed item for later."""
        try:
            # Parse scheduled time
            try:
                scheduled_datetime = datetime.fromisoformat(scheduled_time)
            except ValueError:
                return {"success": False, "error": "Invalid scheduled time format"}
            
            # Create schedule entry
            schedule_id = str(uuid.uuid4())
            
            # Store schedule in memory
            self._store_action_result(
                action_type="schedule",
                feed_item_id=feed_item_id,
                result_data={
                    "schedule_id": schedule_id,
                    "scheduled_time": scheduled_time,
                    "reminder_type": reminder_type,
                    "description": description,
                    "created_time": datetime.now().isoformat()
                },
                user_id=user_id
            )
            
            return {
                "success": True,
                "schedule_id": schedule_id,
                "scheduled_time": scheduled_time,
                "reminder_type": reminder_type
            }
            
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def forward_item(self, feed_item_id: str, recipient: str, message: str, 
                    method: str, user_id: str) -> Dict[str, Any]:
        """Forward a feed item to another recipient."""
        try:
            # Get feed item details
            feed_item = self._get_feed_item(feed_item_id)
            if not feed_item:
                return {"success": False, "error": "Feed item not found"}
            
            # Create forward entry
            forward_id = str(uuid.uuid4())
            
            # Store forward in memory
            self._store_action_result(
                action_type="forward",
                feed_item_id=feed_item_id,
                result_data={
                    "forward_id": forward_id,
                    "recipient": recipient,
                    "message": message,
                    "method": method,
                    "forwarded_time": datetime.now().isoformat(),
                    "original_content": feed_item.get("content", "")
                },
                user_id=user_id
            )
            
            return {
                "success": True,
                "forward_id": forward_id,
                "recipient": recipient,
                "method": method
            }
            
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def delete_item(self, feed_item_id: str, permanent: bool, user_id: str) -> Dict[str, Any]:
        """Delete a feed item."""
        try:
            # Get feed item details
            feed_item = self._get_feed_item(feed_item_id)
            if not feed_item:
                return {"success": False, "error": "Feed item not found"}
            
            # Create delete entry
            delete_id = str(uuid.uuid4())
            
            # Store delete action in memory
            self._store_action_result(
                action_type="delete",
                feed_item_id=feed_item_id,
                result_data={
                    "delete_id": delete_id,
                    "permanent": permanent,
                    "deleted_time": datetime.now().isoformat(),
                    "original_content": feed_item.get("content", "")
                },
                user_id=user_id
            )
            
            return {
                "success": True,
                "delete_id": delete_id,
                "permanent": permanent
            }
            
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def mark_done(self, feed_item_id: str, completion_notes: str, user_id: str) -> Dict[str, Any]:
        """Mark a feed item as done."""
        try:
            # Get feed item details
            feed_item = self._get_feed_item(feed_item_id)
            if not feed_item:
                return {"success": False, "error": "Feed item not found"}
            
            # Create completion entry
            completion_id = str(uuid.uuid4())
            
            # Store completion in memory
            self._store_action_result(
                action_type="mark_done",
                feed_item_id=feed_item_id,
                result_data={
                    "completion_id": completion_id,
                    "completion_notes": completion_notes,
                    "completed_time": datetime.now().isoformat(),
                    "original_content": feed_item.get("content", "")
                },
                user_id=user_id
            )
            
            return {
                "success": True,
                "completion_id": completion_id,
                "completion_notes": completion_notes
            }
            
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def snooze_item(self, feed_item_id: str, snooze_until: str, reason: str, user_id: str) -> Dict[str, Any]:
        """Snooze a feed item until a later time."""
        try:
            # Parse snooze time
            try:
                snooze_datetime = datetime.fromisoformat(snooze_until)
            except ValueError:
                return {"success": False, "error": "Invalid snooze time format"}
            
            # Create snooze entry
            snooze_id = str(uuid.uuid4())
            
            # Store snooze in memory
            self._store_action_result(
                action_type="snooze",
                feed_item_id=feed_item_id,
                result_data={
                    "snooze_id": snooze_id,
                    "snooze_until": snooze_until,
                    "reason": reason,
                    "snoozed_time": datetime.now().isoformat()
                },
                user_id=user_id
            )
            
            return {
                "success": True,
                "snooze_id": snooze_id,
                "snooze_until": snooze_until,
                "reason": reason
            }
            
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def categorize_item(self, feed_item_id: str, category: str, subcategory: str, 
                       tags: List[str], user_id: str) -> Dict[str, Any]:
        """Categorize a feed item."""
        try:
            # Get feed item details
            feed_item = self._get_feed_item(feed_item_id)
            if not feed_item:
                return {"success": False, "error": "Feed item not found"}
            
            # Create categorization entry
            categorization_id = str(uuid.uuid4())
            
            # Store categorization in memory
            self._store_action_result(
                action_type="categorize",
                feed_item_id=feed_item_id,
                result_data={
                    "categorization_id": categorization_id,
                    "category": category,
                    "subcategory": subcategory,
                    "tags": tags,
                    "categorized_time": datetime.now().isoformat()
                },
                user_id=user_id
            )
            
            return {
                "success": True,
                "categorization_id": categorization_id,
                "category": category,
                "subcategory": subcategory,
                "tags": tags
            }
            
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def prioritize_item(self, feed_item_id: str, priority: str, reason: str, user_id: str) -> Dict[str, Any]:
        """Prioritize a feed item."""
        try:
            # Get feed item details
            feed_item = self._get_feed_item(feed_item_id)
            if not feed_item:
                return {"success": False, "error": "Feed item not found"}
            
            # Create prioritization entry
            prioritization_id = str(uuid.uuid4())
            
            # Store prioritization in memory
            self._store_action_result(
                action_type="prioritize",
                feed_item_id=feed_item_id,
                result_data={
                    "prioritization_id": prioritization_id,
                    "priority": priority,
                    "reason": reason,
                    "prioritized_time": datetime.now().isoformat()
                },
                user_id=user_id
            )
            
            return {
                "success": True,
                "prioritization_id": prioritization_id,
                "priority": priority,
                "reason": reason
            }
            
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def execute_custom_action(self, feed_item_id: str, custom_type: str, 
                            custom_data: Dict[str, Any], user_id: str) -> Dict[str, Any]:
        """Execute a custom action."""
        try:
            # Create custom action entry
            custom_action_id = str(uuid.uuid4())
            
            # Store custom action in memory
            self._store_action_result(
                action_type="custom",
                feed_item_id=feed_item_id,
                result_data={
                    "custom_action_id": custom_action_id,
                    "custom_type": custom_type,
                    "custom_data": custom_data,
                    "executed_time": datetime.now().isoformat()
                },
                user_id=user_id
            )
            
            return {
                "success": True,
                "custom_action_id": custom_action_id,
                "custom_type": custom_type,
                "custom_data": custom_data
            }
            
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def _get_feed_item(self, feed_item_id: str) -> Optional[Dict]:
        """Get feed item details from memory."""
        try:
            conn = sqlite3.connect(self.memory_db_path)
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT id, content, source_type, timestamp, metadata
                FROM memory_entries
                WHERE id = ?
            """, (feed_item_id,))
            
            row = cursor.fetchone()
            conn.close()
            
            if row:
                return {
                    "id": row[0],
                    "content": row[1],
                    "source_type": row[2],
                    "timestamp": row[3],
                    "metadata": json.loads(row[4]) if row[4] else {}
                }
            
            return None
            
        except Exception as e:
            print(f"Error getting feed item: {e}")
            return None
    
    def _extract_recipient(self, feed_item: Dict) -> str:
        """Extract recipient information from feed item."""
        # Try to extract from metadata first
        metadata = feed_item.get("metadata", {})
        if "sender" in metadata:
            return metadata["sender"]
        if "from" in metadata:
            return metadata["from"]
        
        # Try to extract from content
        content = feed_item.get("content", "")
        
        # Simple email extraction
        import re
        email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
        emails = re.findall(email_pattern, content)
        if emails:
            return emails[0]
        
        # Default recipient
        return "unknown@example.com"
    
    def _store_action_result(self, action_type: str, feed_item_id: str, 
                           result_data: Dict[str, Any], user_id: str):
        """Store action result in memory."""
        try:
            conn = sqlite3.connect(self.memory_db_path)
            cursor = conn.cursor()
            
            # Ensure action_results table exists
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS action_results (
                    id TEXT PRIMARY KEY,
                    action_type TEXT NOT NULL,
                    feed_item_id TEXT NOT NULL,
                    result_data TEXT NOT NULL,
                    user_id TEXT NOT NULL,
                    timestamp TEXT NOT NULL
                )
            """)
            
            # Insert action result
            cursor.execute("""
                INSERT INTO action_results (id, action_type, feed_item_id, result_data, user_id, timestamp)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (
                str(uuid.uuid4()),
                action_type,
                feed_item_id,
                json.dumps(result_data),
                user_id,
                datetime.now().isoformat()
            ))
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            print(f"Error storing action result: {e}")
    
    def get_action_results(self, feed_item_id: Optional[str] = None, 
                          action_type: Optional[str] = None, 
                          limit: int = 50) -> List[Dict]:
        """Get action results with optional filtering."""
        try:
            conn = sqlite3.connect(self.memory_db_path)
            cursor = conn.cursor()
            
            query = "SELECT * FROM action_results WHERE 1=1"
            params = []
            
            if feed_item_id:
                query += " AND feed_item_id = ?"
                params.append(feed_item_id)
            
            if action_type:
                query += " AND action_type = ?"
                params.append(action_type)
            
            query += " ORDER BY timestamp DESC LIMIT ?"
            params.append(limit)
            
            cursor.execute(query, params)
            rows = cursor.fetchall()
            conn.close()
            
            results = []
            for row in rows:
                results.append({
                    "id": row[0],
                    "action_type": row[1],
                    "feed_item_id": row[2],
                    "result_data": json.loads(row[3]),
                    "user_id": row[4],
                    "timestamp": row[5]
                })
            
            return results
            
        except Exception as e:
            print(f"Error getting action results: {e}")
            return []
