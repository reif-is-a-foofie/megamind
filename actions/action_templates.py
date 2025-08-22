"""
Action Templates - Reusable templates for common actions.

Provides template system for replies, forwards, and other actions
with variable substitution and customization capabilities.
"""

import json
import os
from typing import Dict, List, Optional, Any
from datetime import datetime
from dataclasses import dataclass
import re


@dataclass
class ActionTemplate:
    """Represents an action template."""
    name: str
    description: str
    template_type: str  # reply, forward, schedule, etc.
    content: str
    variables: List[str]
    category: str
    created_at: datetime
    updated_at: datetime
    usage_count: int = 0
    metadata: Optional[Dict] = None


class ActionTemplates:
    """Manages action templates with variable substitution and customization."""
    
    def __init__(self, templates_file: str = "actions/templates.json"):
        self.templates_file = templates_file
        self.templates: Dict[str, ActionTemplate] = {}
        self._load_templates()
        self._create_default_templates()
    
    def _load_templates(self):
        """Load templates from file."""
        try:
            if os.path.exists(self.templates_file):
                with open(self.templates_file, 'r') as f:
                    data = json.load(f)
                
                for template_data in data.get("templates", []):
                    template = ActionTemplate(
                        name=template_data["name"],
                        description=template_data["description"],
                        template_type=template_data["template_type"],
                        content=template_data["content"],
                        variables=template_data["variables"],
                        category=template_data["category"],
                        created_at=datetime.fromisoformat(template_data["created_at"]),
                        updated_at=datetime.fromisoformat(template_data["updated_at"]),
                        usage_count=template_data.get("usage_count", 0),
                        metadata=template_data.get("metadata", {})
                    )
                    self.templates[template.name] = template
        except Exception as e:
            print(f"Error loading templates: {e}")
    
    def _save_templates(self):
        """Save templates to file."""
        try:
            os.makedirs(os.path.dirname(self.templates_file), exist_ok=True)
            
            data = {
                "templates": [
                    {
                        "name": template.name,
                        "description": template.description,
                        "template_type": template.template_type,
                        "content": template.content,
                        "variables": template.variables,
                        "category": template.category,
                        "created_at": template.created_at.isoformat(),
                        "updated_at": template.updated_at.isoformat(),
                        "usage_count": template.usage_count,
                        "metadata": template.metadata or {}
                    }
                    for template in self.templates.values()
                ]
            }
            
            with open(self.templates_file, 'w') as f:
                json.dump(data, f, indent=2)
        except Exception as e:
            print(f"Error saving templates: {e}")
    
    def _create_default_templates(self):
        """Create default templates if none exist."""
        if not self.templates:
            default_templates = [
                {
                    "name": "quick_acknowledgment",
                    "description": "Quick acknowledgment reply",
                    "template_type": "reply",
                    "content": "Thanks for your message. I'll get back to you soon.",
                    "variables": [],
                    "category": "communication"
                },
                {
                    "name": "detailed_response",
                    "description": "Detailed response template",
                    "template_type": "reply",
                    "content": "Thank you for reaching out about {topic}. Here's what I can tell you:\n\n{response}\n\nLet me know if you need any clarification.",
                    "variables": ["topic", "response"],
                    "category": "communication"
                },
                {
                    "name": "meeting_confirmation",
                    "description": "Meeting confirmation template",
                    "template_type": "reply",
                    "content": "I confirm our meeting on {date} at {time}. I'll be prepared to discuss {agenda}.",
                    "variables": ["date", "time", "agenda"],
                    "category": "meetings"
                },
                {
                    "name": "task_delegation",
                    "description": "Task delegation template",
                    "template_type": "forward",
                    "content": "Hi {recipient},\n\nI'm forwarding this task to you as it aligns with your expertise. Please let me know if you need any additional context.\n\n{original_message}",
                    "variables": ["recipient", "original_message"],
                    "category": "workflow"
                },
                {
                    "name": "follow_up_reminder",
                    "description": "Follow-up reminder template",
                    "template_type": "schedule",
                    "content": "Follow up on {topic} with {contact} regarding {action_item}",
                    "variables": ["topic", "contact", "action_item"],
                    "category": "reminders"
                },
                {
                    "name": "urgent_response",
                    "description": "Urgent response template",
                    "template_type": "reply",
                    "content": "I understand this is urgent. I'm prioritizing this and will address it immediately. I'll update you within {timeframe}.",
                    "variables": ["timeframe"],
                    "category": "urgent"
                }
            ]
            
            for template_data in default_templates:
                template = ActionTemplate(
                    name=template_data["name"],
                    description=template_data["description"],
                    template_type=template_data["template_type"],
                    content=template_data["content"],
                    variables=template_data["variables"],
                    category=template_data["category"],
                    created_at=datetime.now(),
                    updated_at=datetime.now(),
                    usage_count=0
                )
                self.templates[template.name] = template
            
            self._save_templates()
    
    def get_template(self, name: str) -> Optional[ActionTemplate]:
        """Get a template by name."""
        return self.templates.get(name)
    
    def get_templates_by_type(self, template_type: str) -> List[ActionTemplate]:
        """Get all templates of a specific type."""
        return [t for t in self.templates.values() if t.template_type == template_type]
    
    def get_templates_by_category(self, category: str) -> List[ActionTemplate]:
        """Get all templates in a specific category."""
        return [t for t in self.templates.values() if t.category == category]
    
    def create_template(self, name: str, description: str, template_type: str, 
                       content: str, variables: List[str], category: str) -> ActionTemplate:
        """Create a new template."""
        if name in self.templates:
            raise ValueError(f"Template '{name}' already exists")
        
        template = ActionTemplate(
            name=name,
            description=description,
            template_type=template_type,
            content=content,
            variables=variables,
            category=category,
            created_at=datetime.now(),
            updated_at=datetime.now(),
            usage_count=0
        )
        
        self.templates[name] = template
        self._save_templates()
        return template
    
    def update_template(self, name: str, **kwargs) -> ActionTemplate:
        """Update an existing template."""
        if name not in self.templates:
            raise ValueError(f"Template '{name}' not found")
        
        template = self.templates[name]
        
        # Update allowed fields
        allowed_fields = ["description", "content", "variables", "category", "metadata"]
        for field, value in kwargs.items():
            if field in allowed_fields:
                setattr(template, field, value)
        
        template.updated_at = datetime.now()
        self._save_templates()
        return template
    
    def delete_template(self, name: str) -> bool:
        """Delete a template."""
        if name in self.templates:
            del self.templates[name]
            self._save_templates()
            return True
        return False
    
    def apply_template(self, template_name: str, variables: Dict[str, str]) -> str:
        """Apply a template with variable substitution."""
        template = self.get_template(template_name)
        if not template:
            raise ValueError(f"Template '{template_name}' not found")
        
        # Increment usage count
        template.usage_count += 1
        self._save_templates()
        
        # Apply variable substitution
        result = template.content
        
        for var_name, var_value in variables.items():
            placeholder = f"{{{var_name}}}"
            result = result.replace(placeholder, str(var_value))
        
        return result
    
    def get_template_variables(self, template_name: str) -> List[str]:
        """Get the variables required by a template."""
        template = self.get_template(template_name)
        if not template:
            return []
        return template.variables.copy()
    
    def search_templates(self, query: str, template_type: Optional[str] = None) -> List[ActionTemplate]:
        """Search templates by name, description, or content."""
        results = []
        query_lower = query.lower()
        
        for template in self.templates.values():
            if template_type and template.template_type != template_type:
                continue
            
            # Search in name, description, and content
            if (query_lower in template.name.lower() or
                query_lower in template.description.lower() or
                query_lower in template.content.lower()):
                results.append(template)
        
        # Sort by usage count (most used first)
        results.sort(key=lambda t: t.usage_count, reverse=True)
        return results
    
    def get_most_used_templates(self, limit: int = 10) -> List[ActionTemplate]:
        """Get the most frequently used templates."""
        templates = list(self.templates.values())
        templates.sort(key=lambda t: t.usage_count, reverse=True)
        return templates[:limit]
    
    def get_template_statistics(self) -> Dict:
        """Get statistics about template usage."""
        total_templates = len(self.templates)
        total_usage = sum(t.usage_count for t in self.templates.values())
        
        # Group by type
        templates_by_type = {}
        for template in self.templates.values():
            if template.template_type not in templates_by_type:
                templates_by_type[template.template_type] = []
            templates_by_type[template.template_type].append(template)
        
        # Group by category
        templates_by_category = {}
        for template in self.templates.values():
            if template.category not in templates_by_category:
                templates_by_category[template.category] = []
            templates_by_category[template.category].append(template)
        
        return {
            "total_templates": total_templates,
            "total_usage": total_usage,
            "templates_by_type": {k: len(v) for k, v in templates_by_type.items()},
            "templates_by_category": {k: len(v) for k, v in templates_by_category.items()},
            "most_used_templates": [
                {"name": t.name, "usage_count": t.usage_count}
                for t in self.get_most_used_templates(5)
            ],
            "recently_updated": [
                {"name": t.name, "updated_at": t.updated_at.isoformat()}
                for t in sorted(
                    self.templates.values(),
                    key=lambda t: t.updated_at,
                    reverse=True
                )[:5]
            ]
        }
    
    def export_templates(self, format: str = "json") -> str:
        """Export templates in various formats."""
        if format == "json":
            return json.dumps({
                "templates": [
                    {
                        "name": template.name,
                        "description": template.description,
                        "template_type": template.template_type,
                        "content": template.content,
                        "variables": template.variables,
                        "category": template.category,
                        "created_at": template.created_at.isoformat(),
                        "updated_at": template.updated_at.isoformat(),
                        "usage_count": template.usage_count,
                        "metadata": template.metadata or {}
                    }
                    for template in self.templates.values()
                ]
            }, indent=2)
        
        elif format == "text":
            output = []
            output.append("ACTION TEMPLATES")
            output.append("=" * 50)
            
            for template in self.templates.values():
                output.append(f"\n{template.name}")
                output.append(f"Type: {template.template_type}")
                output.append(f"Category: {template.category}")
                output.append(f"Description: {template.description}")
                output.append(f"Usage Count: {template.usage_count}")
                output.append(f"Variables: {', '.join(template.variables)}")
                output.append(f"Content: {template.content}")
                output.append("-" * 30)
            
            return "\n".join(output)
        
        else:
            return f"Unsupported format: {format}"
