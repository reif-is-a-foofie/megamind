"""
Test script for Advanced Action System.

Validates the action system functionality and demonstrates
action execution, templates, and history tracking.
"""

import sys
import os
from datetime import datetime, timedelta

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from actions.action_manager import ActionManager, ActionRequest, ActionType
from actions.action_templates import ActionTemplates
from actions.action_executor import ActionExecutor
from actions.action_history import ActionHistory


def test_action_templates():
    """Test action templates functionality."""
    print("Testing Action Templates...")
    
    templates = ActionTemplates()
    
    # Test template creation
    template = templates.create_template(
        name="test_template",
        description="Test template for validation",
        template_type="reply",
        content="Thank you for your message about {topic}. I'll respond within {timeframe}.",
        variables=["topic", "timeframe"],
        category="test"
    )
    
    assert template.name == "test_template", "Should create template with correct name"
    assert len(template.variables) == 2, "Should have correct number of variables"
    
    # Test template application
    result = templates.apply_template("test_template", {
        "topic": "Project Beta",
        "timeframe": "24 hours"
    })
    
    assert "Project Beta" in result, "Should substitute variables correctly"
    assert "24 hours" in result, "Should substitute all variables"
    
    # Test template search
    search_results = templates.search_templates("test")
    assert len(search_results) > 0, "Should find templates by search"
    
    # Test template statistics
    stats = templates.get_template_statistics()
    assert "total_templates" in stats, "Should return template statistics"
    
    print("✓ Action Templates validated")


def test_action_executor():
    """Test action executor functionality."""
    print("Testing Action Executor...")
    
    executor = ActionExecutor()
    
    # Test reply action
    result = executor.send_reply(
        feed_item_id="test_item_1",
        message="Test reply message",
        user_id="test_user"
    )
    
    assert result["success"] == True, "Should successfully send reply"
    assert "reply_id" in result, "Should return reply ID"
    
    # Test archive action
    result = executor.archive_item(
        feed_item_id="test_item_2",
        category="test_category",
        tags=["test", "validation"],
        user_id="test_user"
    )
    
    assert result["success"] == True, "Should successfully archive item"
    assert "archive_id" in result, "Should return archive ID"
    
    # Test schedule action
    scheduled_time = (datetime.now() + timedelta(hours=1)).isoformat()
    result = executor.schedule_item(
        feed_item_id="test_item_3",
        scheduled_time=scheduled_time,
        reminder_type="notification",
        description="Test scheduled item",
        user_id="test_user"
    )
    
    assert result["success"] == True, "Should successfully schedule item"
    assert "schedule_id" in result, "Should return schedule ID"
    
    # Test action results retrieval
    results = executor.get_action_results(limit=10)
    assert isinstance(results, list), "Should return action results list"
    
    print("✓ Action Executor validated")


def test_action_history():
    """Test action history functionality."""
    print("Testing Action History...")
    
    history = ActionHistory()
    
    # Test action history retrieval
    history_data = history.get_action_history(limit=10)
    assert isinstance(history_data, list), "Should return action history list"
    
    # Test action statistics
    stats = history.get_action_statistics()
    assert "total_actions" in stats, "Should return action statistics"
    assert "success_rate" in stats, "Should return success rate"
    
    # Test action trends
    trends = history.get_action_trends(days=7)
    assert "daily_counts" in trends, "Should return daily action counts"
    assert "action_type_trends" in trends, "Should return action type trends"
    
    # Test user action summary
    summary = history.get_user_action_summary("test_user", days=30)
    assert "user_id" in summary, "Should return user action summary"
    assert "total_actions" in summary, "Should return total actions"
    
    # Test action search
    search_results = history.search_actions("test", limit=10)
    assert isinstance(search_results, list), "Should return search results"
    
    print("✓ Action History validated")


def test_action_manager():
    """Test action manager functionality."""
    print("Testing Action Manager...")
    
    manager = ActionManager()
    
    # Test available actions
    actions = manager.get_available_actions("email")
    assert isinstance(actions, list), "Should return available actions"
    assert len(actions) > 0, "Should have available actions for email type"
    
    # Test action execution
    request = ActionRequest(
        action_id="test_action_1",
        action_type=ActionType.REPLY,
        feed_item_id="test_item_1",
        parameters={"message": "Test reply from manager"},
        user_id="test_user",
        timestamp=datetime.now()
    )
    
    result = manager.execute_action(request)
    assert result.success == True, "Should successfully execute action"
    assert "action" in result.result_data, "Should return action result data"
    
    # Test action history
    history = manager.get_action_history(limit=10)
    assert isinstance(history, list), "Should return action history"
    
    # Test action statistics
    stats = manager.get_action_statistics()
    assert isinstance(stats, dict), "Should return action statistics"
    
    print("✓ Action Manager validated")


def test_integration():
    """Test integration between all action components."""
    print("Testing Action System Integration...")
    
    # Create all components
    manager = ActionManager()
    templates = ActionTemplates()
    executor = ActionExecutor()
    history = ActionHistory()
    
    # Test end-to-end workflow
    # 1. Create template
    template = templates.create_template(
        name="integration_test",
        description="Integration test template",
        template_type="reply",
        content="Automated response: {message}",
        variables=["message"],
        category="integration"
    )
    
    # 2. Apply template
    message = templates.apply_template("integration_test", {"message": "Integration successful"})
    
    # 3. Execute action
    request = ActionRequest(
        action_id="integration_action",
        action_type=ActionType.REPLY,
        feed_item_id="integration_item",
        parameters={"message": message, "template": "integration_test"},
        user_id="integration_user",
        timestamp=datetime.now()
    )
    
    result = manager.execute_action(request)
    
    # 4. Verify history
    history_data = history.get_action_history(limit=5)
    
    # Verify all components work together
    assert template.name == "integration_test", "Should create template"
    assert "Integration successful" in message, "Should apply template"
    assert result.success == True, "Should execute action"
    assert isinstance(history_data, list), "Should track history"
    
    print("✓ Action System Integration validated")


def main():
    """Run all action system tests."""
    print("🧪 Testing Advanced Action System...\n")
    
    try:
        test_action_templates()
        test_action_executor()
        test_action_history()
        test_action_manager()
        test_integration()
        
        print("\n🎉 All action system tests passed!")
        print("✅ Advanced Action System is ready for mission.")
        
    except Exception as e:
        print(f"\n❌ Action system test failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
