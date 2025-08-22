# Advanced Action System

Sophisticated action handling for feed items with templates, shortcuts, and seamless workflow automation.

## Overview

The Advanced Action System provides intelligent action execution, template management, and comprehensive history tracking. It transforms basic feed interactions into powerful workflow automation with memory integration and UI connectivity.

## Architecture

### Core Components

1. **ActionManager** (`action_manager.py`)
   - Intelligent action routing and validation
   - Role-based permission enforcement
   - Action request processing and execution
   - Integration with templates and history

2. **ActionTemplates** (`action_templates.py`)
   - Reusable action templates with variable substitution
   - Template categorization and search
   - Usage tracking and statistics
   - Custom template creation and management

3. **ActionExecutor** (`action_executor.py`)
   - External system integration (email, calendar, file systems)
   - Action execution with error handling
   - Result tracking and feedback
   - Memory persistence for action results

4. **ActionHistory** (`action_history.py`)
   - Comprehensive action tracking
   - Statistical analysis and trends
   - User activity summaries
   - Export capabilities and cleanup

## Features

### Action Types
- **Reply**: Send responses to feed items
- **Archive**: Categorize and store items
- **Schedule**: Set reminders and follow-ups
- **Forward**: Share items with others
- **Delete**: Remove items (permanent/temporary)
- **Mark Done**: Complete tasks with notes
- **Snooze**: Defer items until later
- **Categorize**: Organize with tags and categories
- **Prioritize**: Set importance levels
- **Custom**: Extensible custom actions

### Template System
- **Variable Substitution**: Dynamic content generation
- **Category Organization**: Template classification
- **Usage Tracking**: Template popularity metrics
- **Search Capabilities**: Find templates by content
- **Custom Creation**: User-defined templates

### Advanced Features
- **Keyboard Shortcuts**: Quick action access
- **Batch Operations**: Multiple item processing
- **Smart Routing**: Context-aware action selection
- **Error Handling**: Graceful failure management
- **Performance Tracking**: Execution time monitoring

## Usage

### Basic Action Execution

```python
from actions import ActionManager, ActionRequest, ActionType
from datetime import datetime

manager = ActionManager()

# Create action request
request = ActionRequest(
    action_id="reply_001",
    action_type=ActionType.REPLY,
    feed_item_id="email_123",
    parameters={"message": "Thank you for your message"},
    user_id="user_001",
    timestamp=datetime.now()
)

# Execute action
result = manager.execute_action(request)
print(f"Action successful: {result.success}")
```

### Template Usage

```python
from actions import ActionTemplates

templates = ActionTemplates()

# Apply template with variables
message = templates.apply_template("quick_acknowledgment", {})
print(message)  # "Thanks for your message. I'll get back to you soon."

# Create custom template
template = templates.create_template(
    name="meeting_response",
    description="Meeting confirmation template",
    template_type="reply",
    content="I confirm our meeting on {date} at {time}.",
    variables=["date", "time"],
    category="meetings"
)
```

### Action History Analysis

```python
from actions import ActionHistory

history = ActionHistory()

# Get action statistics
stats = history.get_action_statistics()
print(f"Total actions: {stats['total_actions']}")
print(f"Success rate: {stats['success_rate']:.2%}")

# Get user summary
summary = history.get_user_action_summary("user_001", days=30)
print(f"User actions: {summary['total_actions']}")

# Get action trends
trends = history.get_action_trends(days=7)
print(f"Daily activity: {trends['daily_counts']}")
```

### Available Actions by Type

```python
# Get available actions for email items
actions = manager.get_available_actions("email")
for action in actions:
    print(f"{action['name']}: {action['description']}")
    print(f"  Shortcut: {action['shortcut']}")
    print(f"  Parameters: {action['parameters']}")
```

## Integration

### Memory System Integration
- Automatic action result storage
- Historical analysis and trends
- User behavior tracking
- Performance metrics collection

### UI Integration
- Keyboard shortcut support
- Action menu integration
- Real-time status updates
- Template selection interface

### External Systems
- Email system integration
- Calendar API connectivity
- File system operations
- Notification services

## Action Templates

### Default Templates

1. **quick_acknowledgment**
   - Type: Reply
   - Content: "Thanks for your message. I'll get back to you soon."
   - Variables: None

2. **detailed_response**
   - Type: Reply
   - Content: "Thank you for reaching out about {topic}. Here's what I can tell you:\n\n{response}\n\nLet me know if you need any clarification."
   - Variables: topic, response

3. **meeting_confirmation**
   - Type: Reply
   - Content: "I confirm our meeting on {date} at {time}. I'll be prepared to discuss {agenda}."
   - Variables: date, time, agenda

4. **task_delegation**
   - Type: Forward
   - Content: "Hi {recipient},\n\nI'm forwarding this task to you as it aligns with your expertise. Please let me know if you need any additional context.\n\n{original_message}"
   - Variables: recipient, original_message

5. **follow_up_reminder**
   - Type: Schedule
   - Content: "Follow up on {topic} with {contact} regarding {action_item}"
   - Variables: topic, contact, action_item

6. **urgent_response**
   - Type: Reply
   - Content: "I understand this is urgent. I'm prioritizing this and will address it immediately. I'll update you within {timeframe}."
   - Variables: timeframe

### Creating Custom Templates

```python
# Create a custom template
template = templates.create_template(
    name="project_update",
    description="Project status update template",
    template_type="reply",
    content="Project {project_name} is currently {status}. Key updates:\n{updates}\nNext milestone: {next_milestone}",
    variables=["project_name", "status", "updates", "next_milestone"],
    category="project_management"
)

# Apply the template
message = templates.apply_template("project_update", {
    "project_name": "Alpha",
    "status": "on track",
    "updates": "Phase 1 completed, Phase 2 starting",
    "next_milestone": "Beta release in 2 weeks"
})
```

## Performance

### Optimization Features
- **Caching**: Template and action caching
- **Batch Processing**: Efficient bulk operations
- **Async Support**: Non-blocking action execution
- **Memory Management**: Optimized resource usage

### Monitoring
- **Execution Time**: Action performance tracking
- **Success Rates**: Action reliability metrics
- **Usage Patterns**: User behavior analysis
- **System Health**: Error rate monitoring

## Testing

Run comprehensive tests:

```bash
python3 actions/test_action_system.py
```

Tests validate:
- ✅ Template creation and application
- ✅ Action execution and validation
- ✅ History tracking and analysis
- ✅ Manager integration and routing
- ✅ System integration stability
- ✅ Error handling and recovery

## Configuration

### Action Shortcuts
Customize keyboard shortcuts in `action_manager.py`:

```python
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
```

### Template Settings
Configure template behavior:

```python
# Template file location
templates_file = "actions/templates.json"

# Default template categories
categories = ["communication", "meetings", "workflow", "reminders", "urgent"]
```

## Mission Integration

This action system provides:
- **Workflow Automation**: Streamlined task processing
- **Template Efficiency**: Reusable action patterns
- **Historical Intelligence**: Action pattern analysis
- **User Experience**: Intuitive action interfaces
- **System Integration**: Seamless external connectivity

The system transforms basic interactions into powerful workflows, enabling the galleon to operate with precision and efficiency! ⚡🔄
