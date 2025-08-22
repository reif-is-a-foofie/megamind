#!/bin/bash

echo "⚓ MEGAMIND BUTLER INTERFACE DEMO ⚓"
echo "=================================="
echo ""
echo "This demo showcases the Crush-based three-pane terminal interface:"
echo ""
echo "• Left Pane: File explorer + Knowledge graph (Tab to toggle)"
echo "• Center Pane: Agent chat + Unified feed (Arrow keys to navigate)"
echo "• Right Pane: Logs, alerts, XP overlay"
echo ""
echo "Controls:"
echo "• Tab/Shift+Tab: Switch between panes"
echo "• Arrow keys: Navigate within focused pane"
echo "• Enter: Mark feed item as read"
echo "• 'd': Mark feed item as done"
echo "• Ctrl+C or 'q': Quit"
echo ""
echo "Press Enter to launch the interface..."
read

# Run the Crush-based UI
go run main.go
