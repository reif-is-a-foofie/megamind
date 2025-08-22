"""
Action History - Tracks and manages action history.

Provides comprehensive tracking of all actions performed on feed items
with memory integration and historical analysis capabilities.
"""

import json
import sqlite3
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
from collections import defaultdict, Counter
import uuid


class ActionHistory:
    """Manages action history with memory integration."""
    
    def __init__(self, memory_db_path: str = "memory/memory.db"):
        self.memory_db_path = memory_db_path
        self._ensure_tables_exist()
    
    def _ensure_tables_exist(self):
        """Ensure required tables exist in the database."""
        try:
            conn = sqlite3.connect(self.memory_db_path)
            cursor = conn.cursor()
            
            # Create action_history table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS action_history (
                    id TEXT PRIMARY KEY,
                    action_id TEXT NOT NULL,
                    action_type TEXT NOT NULL,
                    feed_item_id TEXT NOT NULL,
                    user_id TEXT NOT NULL,
                    parameters TEXT NOT NULL,
                    result_data TEXT NOT NULL,
                    execution_time REAL NOT NULL,
                    timestamp TEXT NOT NULL,
                    success BOOLEAN NOT NULL,
                    error_message TEXT
                )
            """)
            
            # Create action_statistics table for caching
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS action_statistics (
                    id TEXT PRIMARY KEY,
                    stat_type TEXT NOT NULL,
                    stat_key TEXT NOT NULL,
                    stat_value TEXT NOT NULL,
                    timestamp TEXT NOT NULL
                )
            """)
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            print(f"Error ensuring tables exist: {e}")
    
    def record_action(self, action_request, result_data: Dict[str, Any], execution_time: float):
        """Record an action in the history."""
        try:
            conn = sqlite3.connect(self.memory_db_path)
            cursor = conn.cursor()
            
            cursor.execute("""
                INSERT INTO action_history (
                    id, action_id, action_type, feed_item_id, user_id, 
                    parameters, result_data, execution_time, timestamp, 
                    success, error_message
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                str(uuid.uuid4()),
                action_request.action_id,
                action_request.action_type.value,
                action_request.feed_item_id,
                action_request.user_id,
                json.dumps(action_request.parameters),
                json.dumps(result_data),
                execution_time,
                action_request.timestamp.isoformat(),
                result_data.get("success", True),
                result_data.get("error_message")
            ))
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            print(f"Error recording action: {e}")
    
    def get_action_history(self, feed_item_id: Optional[str] = None, 
                          user_id: Optional[str] = None, 
                          limit: int = 50) -> List[Dict]:
        """Get action history with optional filtering."""
        try:
            conn = sqlite3.connect(self.memory_db_path)
            cursor = conn.cursor()
            
            query = "SELECT * FROM action_history WHERE 1=1"
            params = []
            
            if feed_item_id:
                query += " AND feed_item_id = ?"
                params.append(feed_item_id)
            
            if user_id:
                query += " AND user_id = ?"
                params.append(user_id)
            
            query += " ORDER BY timestamp DESC LIMIT ?"
            params.append(limit)
            
            cursor.execute(query, params)
            rows = cursor.fetchall()
            conn.close()
            
            history = []
            for row in rows:
                history.append({
                    "id": row[0],
                    "action_id": row[1],
                    "action_type": row[2],
                    "feed_item_id": row[3],
                    "user_id": row[4],
                    "parameters": json.loads(row[5]),
                    "result_data": json.loads(row[6]),
                    "execution_time": row[7],
                    "timestamp": row[8],
                    "success": bool(row[9]),
                    "error_message": row[10]
                })
            
            return history
            
        except Exception as e:
            print(f"Error getting action history: {e}")
            return []
    
    def get_action_statistics(self) -> Dict:
        """Get comprehensive statistics about action usage."""
        try:
            conn = sqlite3.connect(self.memory_db_path)
            cursor = conn.cursor()
            
            # Get basic statistics
            cursor.execute("SELECT COUNT(*) FROM action_history")
            total_actions = cursor.fetchone()[0]
            
            cursor.execute("SELECT COUNT(*) FROM action_history WHERE success = 1")
            successful_actions = cursor.fetchone()[0]
            
            cursor.execute("SELECT COUNT(*) FROM action_history WHERE success = 0")
            failed_actions = cursor.fetchone()[0]
            
            # Get action type distribution
            cursor.execute("SELECT action_type, COUNT(*) FROM action_history GROUP BY action_type")
            action_type_counts = dict(cursor.fetchall())
            
            # Get user distribution
            cursor.execute("SELECT user_id, COUNT(*) FROM action_history GROUP BY user_id")
            user_counts = dict(cursor.fetchall())
            
            # Get average execution time by action type
            cursor.execute("""
                SELECT action_type, AVG(execution_time) 
                FROM action_history 
                WHERE success = 1 
                GROUP BY action_type
            """)
            avg_execution_times = dict(cursor.fetchall())
            
            # Get recent activity (last 7 days)
            week_ago = (datetime.now() - timedelta(days=7)).isoformat()
            cursor.execute("""
                SELECT COUNT(*) 
                FROM action_history 
                WHERE timestamp >= ?
            """, (week_ago,))
            recent_actions = cursor.fetchone()[0]
            
            # Get most active feed items
            cursor.execute("""
                SELECT feed_item_id, COUNT(*) 
                FROM action_history 
                GROUP BY feed_item_id 
                ORDER BY COUNT(*) DESC 
                LIMIT 10
            """)
            most_active_items = dict(cursor.fetchall())
            
            conn.close()
            
            return {
                "total_actions": total_actions,
                "successful_actions": successful_actions,
                "failed_actions": failed_actions,
                "success_rate": successful_actions / total_actions if total_actions > 0 else 0,
                "action_type_distribution": action_type_counts,
                "user_distribution": user_counts,
                "avg_execution_times": avg_execution_times,
                "recent_activity": recent_actions,
                "most_active_items": most_active_items
            }
            
        except Exception as e:
            print(f"Error getting action statistics: {e}")
            return {}
    
    def get_action_trends(self, days: int = 30) -> Dict:
        """Get action trends over time."""
        try:
            conn = sqlite3.connect(self.memory_db_path)
            cursor = conn.cursor()
            
            start_date = (datetime.now() - timedelta(days=days)).isoformat()
            
            # Get daily action counts
            cursor.execute("""
                SELECT DATE(timestamp) as date, COUNT(*) as count
                FROM action_history
                WHERE timestamp >= ?
                GROUP BY DATE(timestamp)
                ORDER BY date
            """, (start_date,))
            
            daily_counts = dict(cursor.fetchall())
            
            # Get action type trends
            cursor.execute("""
                SELECT DATE(timestamp) as date, action_type, COUNT(*) as count
                FROM action_history
                WHERE timestamp >= ?
                GROUP BY DATE(timestamp), action_type
                ORDER BY date
            """, (start_date,))
            
            action_type_trends = defaultdict(dict)
            for row in cursor.fetchall():
                date, action_type, count = row
                action_type_trends[action_type][date] = count
            
            # Get user activity trends
            cursor.execute("""
                SELECT DATE(timestamp) as date, user_id, COUNT(*) as count
                FROM action_history
                WHERE timestamp >= ?
                GROUP BY DATE(timestamp), user_id
                ORDER BY date
            """, (start_date,))
            
            user_trends = defaultdict(dict)
            for row in cursor.fetchall():
                date, user_id, count = row
                user_trends[user_id][date] = count
            
            conn.close()
            
            return {
                "daily_counts": dict(daily_counts),
                "action_type_trends": dict(action_type_trends),
                "user_trends": dict(user_trends),
                "period_days": days
            }
            
        except Exception as e:
            print(f"Error getting action trends: {e}")
            return {}
    
    def get_user_action_summary(self, user_id: str, days: int = 30) -> Dict:
        """Get action summary for a specific user."""
        try:
            conn = sqlite3.connect(self.memory_db_path)
            cursor = conn.cursor()
            
            start_date = (datetime.now() - timedelta(days=days)).isoformat()
            
            # Get user's action counts
            cursor.execute("""
                SELECT action_type, COUNT(*) 
                FROM action_history 
                WHERE user_id = ? AND timestamp >= ?
                GROUP BY action_type
            """, (user_id, start_date))
            
            action_counts = dict(cursor.fetchall())
            
            # Get user's success rate
            cursor.execute("""
                SELECT COUNT(*) 
                FROM action_history 
                WHERE user_id = ? AND timestamp >= ? AND success = 1
            """, (user_id, start_date))
            
            successful_actions = cursor.fetchone()[0]
            
            cursor.execute("""
                SELECT COUNT(*) 
                FROM action_history 
                WHERE user_id = ? AND timestamp >= ?
            """, (user_id, start_date))
            
            total_actions = cursor.fetchone()[0]
            
            # Get user's average execution time
            cursor.execute("""
                SELECT AVG(execution_time) 
                FROM action_history 
                WHERE user_id = ? AND timestamp >= ? AND success = 1
            """, (user_id, start_date))
            
            avg_execution_time = cursor.fetchone()[0] or 0
            
            # Get user's most used action types
            cursor.execute("""
                SELECT action_type, COUNT(*) 
                FROM action_history 
                WHERE user_id = ? AND timestamp >= ?
                GROUP BY action_type 
                ORDER BY COUNT(*) DESC 
                LIMIT 5
            """, (user_id, start_date))
            
            most_used_actions = dict(cursor.fetchall())
            
            conn.close()
            
            return {
                "user_id": user_id,
                "period_days": days,
                "total_actions": total_actions,
                "successful_actions": successful_actions,
                "success_rate": successful_actions / total_actions if total_actions > 0 else 0,
                "avg_execution_time": avg_execution_time,
                "action_counts": action_counts,
                "most_used_actions": most_used_actions
            }
            
        except Exception as e:
            print(f"Error getting user action summary: {e}")
            return {}
    
    def search_actions(self, query: str, limit: int = 50) -> List[Dict]:
        """Search actions by various criteria."""
        try:
            conn = sqlite3.connect(self.memory_db_path)
            cursor = conn.cursor()
            
            # Search in action types, user IDs, and feed item IDs
            cursor.execute("""
                SELECT * FROM action_history 
                WHERE action_type LIKE ? 
                   OR user_id LIKE ? 
                   OR feed_item_id LIKE ?
                ORDER BY timestamp DESC 
                LIMIT ?
            """, (f"%{query}%", f"%{query}%", f"%{query}%", limit))
            
            rows = cursor.fetchall()
            conn.close()
            
            results = []
            for row in rows:
                results.append({
                    "id": row[0],
                    "action_id": row[1],
                    "action_type": row[2],
                    "feed_item_id": row[3],
                    "user_id": row[4],
                    "parameters": json.loads(row[5]),
                    "result_data": json.loads(row[6]),
                    "execution_time": row[7],
                    "timestamp": row[8],
                    "success": bool(row[9]),
                    "error_message": row[10]
                })
            
            return results
            
        except Exception as e:
            print(f"Error searching actions: {e}")
            return []
    
    def export_action_history(self, format: str = "json", 
                            feed_item_id: Optional[str] = None,
                            user_id: Optional[str] = None,
                            limit: int = 1000) -> str:
        """Export action history in various formats."""
        history = self.get_action_history(feed_item_id, user_id, limit)
        
        if format == "json":
            return json.dumps(history, indent=2)
        
        elif format == "csv":
            import csv
            import io
            
            output = io.StringIO()
            writer = csv.writer(output)
            
            # Write header
            writer.writerow([
                "ID", "Action ID", "Action Type", "Feed Item ID", "User ID",
                "Parameters", "Result Data", "Execution Time", "Timestamp",
                "Success", "Error Message"
            ])
            
            # Write data
            for action in history:
                writer.writerow([
                    action["id"],
                    action["action_id"],
                    action["action_type"],
                    action["feed_item_id"],
                    action["user_id"],
                    json.dumps(action["parameters"]),
                    json.dumps(action["result_data"]),
                    action["execution_time"],
                    action["timestamp"],
                    action["success"],
                    action["error_message"] or ""
                ])
            
            return output.getvalue()
        
        else:
            return f"Unsupported format: {format}"
    
    def cleanup_old_actions(self, days_to_keep: int = 90) -> int:
        """Clean up old action history entries."""
        try:
            conn = sqlite3.connect(self.memory_db_path)
            cursor = conn.cursor()
            
            cutoff_date = (datetime.now() - timedelta(days=days_to_keep)).isoformat()
            
            cursor.execute("""
                DELETE FROM action_history 
                WHERE timestamp < ?
            """, (cutoff_date,))
            
            deleted_count = cursor.rowcount
            conn.commit()
            conn.close()
            
            return deleted_count
            
        except Exception as e:
            print(f"Error cleaning up old actions: {e}")
            return 0
