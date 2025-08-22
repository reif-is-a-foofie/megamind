"""
Action Manager - Orchestrates advanced actions for feed items.

Manages action execution, templates, shortcuts, and integration with
memory and UI systems for seamless workflow automation.
"""

import json
import sqlite3
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
from dataclasses import dataclass
from enum import Enum
import os

from .action_templates import ActionTemplates
from .action_executor import ActionExecutor
from .action_history import ActionHistory


class ActionType(Enum):
    """Types of actions that can be performed on feed items."""
    REPLY = "reply"
    ARCHIVE = "archive"
    SCHEDULE = "schedule"
    FORWARD = "forward"
    DELETE = "delete"
    MARK_DONE = "mark_done"
    SNOOZE = "snooze"
    CATEGORIZE = "categorize"
    PRIORITIZE = "prioritize"
    CUSTOM = "custom"


@dataclass
class ActionRequest:
    """Represents a request to perform an action."""
    action_id: str
    action_type: ActionType
    feed_item_id: str
    parameters: Dict[str, Any]
    user_id: str
    timestamp: datetime
    priority: str = "normal"  # low, normal, high, urgent
    metadata: Optional[Dict] = None


@dataclass
class ActionResult:
    """Represents the result of an action execution."""
    action_id: str
    success: bool
    result_data: Dict[str, Any]
    execution_time: float
    error_message: Optional[str] = None
    metadata: Optional[Dict] = None


class ActionManager:
    """Manages advanced actions for feed items with intelligent routing."""
    
    def __init__(self, memory_db_path: str = "memory/memory.db"):
        self.memory_db_path = memory_db_path
        self.templates = ActionTemplates()
        self.executor = ActionExecutor()
        self.history = ActionHistory(memory_db_path)
        self.action_handlers = self._register_action_handlers()
    
    def _register_action_handlers(self) -> Dict[ActionType, callable]:
        """Register handlers for different action types."""
        return {
            ActionType.REPLY: self._handle_reply,
            ActionType.ARCHIVE: self._handle_archive,
            ActionType.SCHEDULE: self._handle_schedule,
            ActionType.FORWARD: self._handle_forward,
            ActionType.DELETE: self._handle_delete,
            ActionType.MARK_DONE: self._handle_mark_done,
            ActionType.SNOOZE: self._handle_snooze,
            ActionType.CATEGORIZE: self._handle_categorize,
            ActionType.PRIORITIZE: self._handle_prioritize,
            ActionType.CUSTOM: self._handle_custom
        }
    
    def execute_action(self, request: ActionRequest) -> ActionResult:
        """Execute an action based on the request."""
        import time
        start_time = time.time()
        
        try:
            # Validate action request
            if not self._validate_action_request(request):
                return ActionResult(
                    action_id=request.action_id,
                    success=False,
                    result_data={},
                    execution_time=time.time() - start_time,
                    error_message="Invalid action request"
                )
            
            # Get handler for action type
            handler = self.action_handlers.get(request.action_type)
            if not handler:
                return ActionResult(
                    action_id=request.action_id,
                    success=False,
                    result_data={},
                    execution_time=time.time() - start_time,
                    error_message=f"Unknown action type: {request.action_type}"
                )
            
            # Execute action
            result_data = handler(request)
            
            # Record action in history
            self.history.record_action(request, result_data, time.time() - start_time)
            
            return ActionResult(
                action_id=request.action_id,
                success=True,
                result_data=result_data,
                execution_time=time.time() - start_time
            )
            
        except Exception as e:
            execution_time = time.time() - start_time
            return ActionResult(
                action_id=request.action_id,
                success=False,
                result_data={},
                execution_time=execution_time,
                error_message=str(e)
            )
    
    def _validate_action_request(self, request: ActionRequest) -> bool:
        """Validate an action request."""
        if not request.action_id or not request.feed_item_id or not request.user_id:
            return False
        
        if request.action_type not in ActionType:
            return False
        
        # Validate required parameters for specific action types
        if request.action_type == ActionType.REPLY:
            if "message" not in request.parameters:
                return False
        elif request.action_type == ActionType.SCHEDULE:
            if "scheduled_time" not in request.parameters:
                return False
        elif request.action_type == ActionType.FORWARD:
            if "recipient" not in request.parameters:
                return False
        
        return True
    
    def _handle_reply(self, request: ActionRequest) -> Dict[str, Any]:
        """Handle reply action."""
        message = request.parameters.get("message", "")
        template_name = request.parameters.get("template", None)
        
        # Apply template if specified
        if template_name:
            template = self.templates.get_template(template_name)
            if template:
                message = template.apply(message, request.parameters)
        
        # Execute reply
        result = self.executor.send_reply(
            feed_item_id=request.feed_item_id,
            message=message,
            user_id=request.user_id
        )
        
        return {
            "action": "reply",
            "message": message,
            "template_used": template_name,
            "recipient": result.get("recipient"),
            "sent_time": datetime.now().isoformat()
        }
    
    def _handle_archive(self, request: ActionRequest) -> Dict[str, Any]:
        """Handle archive action."""
        category = request.parameters.get("category", "general")
        tags = request.parameters.get("tags", [])
        
        result = self.executor.archive_item(
            feed_item_id=request.feed_item_id,
            category=category,
            tags=tags,
            user_id=request.user_id
        )
        
        return {
            "action": "archive",
            "category": category,
            "tags": tags,
            "archived_time": datetime.now().isoformat(),
            "archive_id": result.get("archive_id")
        }
    
    def _handle_schedule(self, request: ActionRequest) -> Dict[str, Any]:
        """Handle schedule action."""
        scheduled_time = request.parameters.get("scheduled_time")
        reminder_type = request.parameters.get("reminder_type", "notification")
        description = request.parameters.get("description", "")
        
        result = self.executor.schedule_item(
            feed_item_id=request.feed_item_id,
            scheduled_time=scheduled_time,
            reminder_type=reminder_type,
            description=description,
            user_id=request.user_id
        )
        
        return {
            "action": "schedule",
            "scheduled_time": scheduled_time,
            "reminder_type": reminder_type,
            "description": description,
            "schedule_id": result.get("schedule_id")
        }
    
    def _handle_forward(self, request: ActionRequest) -> Dict[str, Any]:
        """Handle forward action."""
        recipient = request.parameters.get("recipient")
        message = request.parameters.get("message", "")
        method = request.parameters.get("method", "email")
        
        result = self.executor.forward_item(
            feed_item_id=request.feed_item_id,
            recipient=recipient,
            message=message,
            method=method,
            user_id=request.user_id
        )
        
        return {
            "action": "forward",
            "recipient": recipient,
            "method": method,
            "message": message,
            "forward_id": result.get("forward_id")
        }
    
    def _handle_delete(self, request: ActionRequest) -> Dict[str, Any]:
        """Handle delete action."""
        permanent = request.parameters.get("permanent", False)
        
        result = self.executor.delete_item(
            feed_item_id=request.feed_item_id,
            permanent=permanent,
            user_id=request.user_id
        )
        
        return {
            "action": "delete",
            "permanent": permanent,
            "deleted_time": datetime.now().isoformat()
        }
    
    def _handle_mark_done(self, request: ActionRequest) -> Dict[str, Any]:
        """Handle mark done action."""
        completion_notes = request.parameters.get("completion_notes", "")
        
        result = self.executor.mark_done(
            feed_item_id=request.feed_item_id,
            completion_notes=completion_notes,
            user_id=request.user_id
        )
        
        return {
            "action": "mark_done",
            "completion_notes": completion_notes,
            "completed_time": datetime.now().isoformat()
        }
    
    def _handle_snooze(self, request: ActionRequest) -> Dict[str, Any]:
        """Handle snooze action."""
        snooze_until = request.parameters.get("snooze_until")
        reason = request.parameters.get("reason", "")
        
        result = self.executor.snooze_item(
            feed_item_id=request.feed_item_id,
            snooze_until=snooze_until,
            reason=reason,
            user_id=request.user_id
        )
        
        return {
            "action": "snooze",
            "snooze_until": snooze_until,
            "reason": reason,
            "snooze_id": result.get("snooze_id")
        }
    
    def _handle_categorize(self, request: ActionRequest) -> Dict[str, Any]:
        """Handle categorize action."""
        category = request.parameters.get("category")
        subcategory = request.parameters.get("subcategory")
        tags = request.parameters.get("tags", [])
        
        result = self.executor.categorize_item(
            feed_item_id=request.feed_item_id,
            category=category,
            subcategory=subcategory,
            tags=tags,
            user_id=request.user_id
        )
        
        return {
            "action": "categorize",
            "category": category,
            "subcategory": subcategory,
            "tags": tags,
            "categorized_time": datetime.now().isoformat()
        }
    
    def _handle_prioritize(self, request: ActionRequest) -> Dict[str, Any]:
        """Handle prioritize action."""
        priority = request.parameters.get("priority", "normal")
        reason = request.parameters.get("reason", "")
        
        result = self.executor.prioritize_item(
            feed_item_id=request.feed_item_id,
            priority=priority,
            reason=reason,
            user_id=request.user_id
        )
        
        return {
            "action": "prioritize",
            "priority": priority,
            "reason": reason,
            "prioritized_time": datetime.now().isoformat()
        }
    
    def _handle_custom(self, request: ActionRequest) -> Dict[str, Any]:
        """Handle custom action."""
        custom_type = request.parameters.get("custom_type")
        custom_data = request.parameters.get("custom_data", {})
        
        result = self.executor.execute_custom_action(
            feed_item_id=request.feed_item_id,
            custom_type=custom_type,
            custom_data=custom_data,
            user_id=request.user_id
        )
        
        return {
            "action": "custom",
            "custom_type": custom_type,
            "custom_data": custom_data,
            "executed_time": datetime.now().isoformat(),
            "result": result
        }
    
    def get_available_actions(self, feed_item_type: str) -> List[Dict]:
        """Get available actions for a specific feed item type."""
        actions = []
        
        # Base actions available for all items
        base_actions = [
            ActionType.MARK_DONE,
            ActionType.DELETE,
            ActionType.SNOOZE,
            ActionType.CATEGORIZE,
            ActionType.PRIORITIZE
        ]
        
        for action_type in base_actions:
            actions.append({
                "type": action_type.value,
                "name": action_type.value.replace("_", " ").title(),
                "description": f"{action_type.value.replace('_', ' ').title()} this item",
                "shortcut": self._get_action_shortcut(action_type),
                "parameters": self._get_action_parameters(action_type)
            })
        
        # Type-specific actions
        if feed_item_type in ["email", "message"]:
            actions.extend([
                {
                    "type": ActionType.REPLY.value,
                    "name": "Reply",
                    "description": "Reply to this message",
                    "shortcut": "r",
                    "parameters": ["message", "template"]
                },
                {
                    "type": ActionType.FORWARD.value,
                    "name": "Forward",
                    "description": "Forward this message",
                    "shortcut": "f",
                    "parameters": ["recipient", "message", "method"]
                }
            ])
        
        if feed_item_type in ["task", "reminder", "meeting"]:
            actions.append({
                "type": ActionType.SCHEDULE.value,
                "name": "Schedule",
                "description": "Schedule this item",
                "shortcut": "s",
                "parameters": ["scheduled_time", "reminder_type", "description"]
            })
        
        if feed_item_type in ["document", "file"]:
            actions.append({
                "type": ActionType.ARCHIVE.value,
                "name": "Archive",
                "description": "Archive this item",
                "shortcut": "a",
                "parameters": ["category", "tags"]
            })
        
        return actions
    
    def _get_action_shortcut(self, action_type: ActionType) -> str:
        """Get keyboard shortcut for an action."""
        shortcuts = {
            ActionType.REPLY: "r",
            ActionType.ARCHIVE: "a",
            ActionType.SCHEDULE: "s",
            ActionType.FORWARD: "f",
            ActionType.DELETE: "d",
            ActionType.MARK_DONE: "m",
            ActionType.SNOOZE: "z",
            ActionType.CATEGORIZE: "c",
            ActionType.PRIORITIZE: "p"
        }
        return shortcuts.get(action_type, "")
    
    def _get_action_parameters(self, action_type: ActionType) -> List[str]:
        """Get required parameters for an action."""
        parameters = {
            ActionType.REPLY: ["message"],
            ActionType.ARCHIVE: ["category"],
            ActionType.SCHEDULE: ["scheduled_time"],
            ActionType.FORWARD: ["recipient"],
            ActionType.DELETE: [],
            ActionType.MARK_DONE: [],
            ActionType.SNOOZE: ["snooze_until"],
            ActionType.CATEGORIZE: ["category"],
            ActionType.PRIORITIZE: ["priority"]
        }
        return parameters.get(action_type, [])
    
    def get_action_history(self, feed_item_id: Optional[str] = None, 
                          user_id: Optional[str] = None, 
                          limit: int = 50) -> List[Dict]:
        """Get action history with optional filtering."""
        return self.history.get_action_history(feed_item_id, user_id, limit)
    
    def get_action_statistics(self) -> Dict:
        """Get statistics about action usage."""
        return self.history.get_action_statistics()
