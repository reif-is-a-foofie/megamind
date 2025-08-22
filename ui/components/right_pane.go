package components

import (
	"fmt"
	"strings"
	"time"

	tea "github.com/charmbracelet/bubbletea"
)

// Alert represents a system alert
type Alert struct {
	Icon    string
	Message string
	Level   string // "info", "warning", "error"
}

// LogEntry represents a system log entry
type LogEntry struct {
	Time    time.Time
	Level   string
	Message string
}

// RightPane represents the right pane with logs, alerts, and XP overlay
type RightPane struct {
	width  int
	height int
	xpData map[string]interface{}
	alerts []Alert
	logs   []LogEntry
}

// NewRightPane creates a new right pane
func NewRightPane() *RightPane {
	return &RightPane{
		xpData: map[string]interface{}{
			"level":           5,
			"xp":              1250,
			"xp_to_next":      250,
			"title":           "Navigator",
			"completed_today": 12,
		},
		alerts: []Alert{
			{Icon: "⚠️", Message: "High priority contract ui.01 needs attention", Level: "warning"},
			{Icon: "💰", Message: "Gold price alert: Significant movement detected", Level: "info"},
			{Icon: "🌪️", Message: "Weather alert: Hurricane approaching coastal areas", Level: "warning"},
			{Icon: "📧", Message: "3 unread items require attention", Level: "info"},
		},
		logs: []LogEntry{
			{Time: time.Now(), Level: "INFO", Message: "Worker agent started ui.01 implementation"},
			{Time: time.Now(), Level: "INFO", Message: "Three-pane layout initialized"},
			{Time: time.Now(), Level: "INFO", Message: "Memory connector established"},
			{Time: time.Now(), Level: "INFO", Message: "Feed connector connected"},
			{Time: time.Now(), Level: "INFO", Message: "API connector ready"},
			{Time: time.Now(), Level: "SUCCESS", Message: "Butler interface ready for interaction"},
		},
	}
}

// Init initializes the right pane
func (rp *RightPane) Init() tea.Cmd {
	return nil
}

// Update handles updates for the right pane
func (rp *RightPane) Update(msg tea.Msg) (*RightPane, tea.Cmd) {
	// Right pane is mostly read-only for now
	return rp, nil
}

// View renders the right pane
func (rp *RightPane) View() string {
	xpSection := rp.renderXPOverlay()
	alertsSection := rp.renderAlerts()
	logsSection := rp.renderLogs()

	content := fmt.Sprintf("%s\n\n%s\n\n%s", xpSection, alertsSection, logsSection)

	title := "📊 Logs & XP"
	subtitle := "System Status"

	return RightPaneStyle.Render(fmt.Sprintf("%s\n%s\n\n%s", title, subtitle, content))
}

// SetSize sets the pane size
func (rp *RightPane) SetSize(width, height int) {
	rp.width = width
	rp.height = height
}

// renderXPOverlay renders the XP and gamification overlay
func (rp *RightPane) renderXPOverlay() string {
	var lines []string
	lines = append(lines, "🏴‍☠️ Pirate Progress")
	lines = append(lines, strings.Repeat("=", 20))

	level := rp.xpData["level"].(int)
	title := rp.xpData["title"].(string)
	xp := rp.xpData["xp"].(int)
	xpToNext := rp.xpData["xp_to_next"].(int)
	completedToday := rp.xpData["completed_today"].(int)

	lines = append(lines, fmt.Sprintf("Level: %d - %s", level, title))
	lines = append(lines, fmt.Sprintf("XP: %d / %d", xp, xp+xpToNext))
	lines = append(lines, fmt.Sprintf("Progress: %d XP to next level", xpToNext))
	lines = append(lines, fmt.Sprintf("Today: %d items completed", completedToday))

	return strings.Join(lines, "\n")
}

// renderAlerts renders the alerts section
func (rp *RightPane) renderAlerts() string {
	var lines []string
	lines = append(lines, "🚨 Active Alerts")
	lines = append(lines, strings.Repeat("=", 30))

	for _, alert := range rp.alerts {
		line := fmt.Sprintf("%s %s", alert.Icon, alert.Message)
		switch alert.Level {
		case "warning":
			line = WarningStyle.Render(line)
		case "error":
			line = ErrorStyle.Render(line)
		default:
			line = InfoStyle.Render(line)
		}
		lines = append(lines, line)
	}

	return strings.Join(lines, "\n")
}

// renderLogs renders the system logs
func (rp *RightPane) renderLogs() string {
	var lines []string
	lines = append(lines, "📝 System Logs")
	lines = append(lines, strings.Repeat("=", 30))

	for _, log := range rp.logs {
		timeStr := log.Time.Format("15:04:05")
		line := fmt.Sprintf("%s %s: %s", timeStr, log.Level, log.Message)

		switch log.Level {
		case "SUCCESS":
			line = SuccessStyle.Render(line)
		case "ERROR":
			line = ErrorStyle.Render(line)
		case "WARNING":
			line = WarningStyle.Render(line)
		default:
			line = InfoStyle.Render(line)
		}

		lines = append(lines, line)
	}

	return strings.Join(lines, "\n")
}
