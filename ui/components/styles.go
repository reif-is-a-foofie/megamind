package components

import "github.com/charmbracelet/lipgloss"

// Shared styles for all components
var (
	// Pane styles
	LeftPaneStyle = lipgloss.NewStyle().
			Border(lipgloss.RoundedBorder()).
			BorderForeground(lipgloss.Color("4")). // Blue
			Padding(1, 1).
			Width(30)

	CenterPaneStyle = lipgloss.NewStyle().
			Border(lipgloss.RoundedBorder()).
			BorderForeground(lipgloss.Color("2")). // Green
			Padding(1, 1).
			Width(50)

	RightPaneStyle = lipgloss.NewStyle().
			Border(lipgloss.RoundedBorder()).
			BorderForeground(lipgloss.Color("3")). // Yellow
			Padding(1, 1).
			Width(40)

	// Interactive styles
	CursorStyle = lipgloss.NewStyle().
			Foreground(lipgloss.Color("6")). // Cyan
			Bold(true)

	UnreadStyle = lipgloss.NewStyle().
			Bold(true)

	// Status styles
	SuccessStyle = lipgloss.NewStyle().
			Foreground(lipgloss.Color("2")). // Green
			Bold(true)

	ErrorStyle = lipgloss.NewStyle().
			Foreground(lipgloss.Color("1")). // Red
			Bold(true)

	WarningStyle = lipgloss.NewStyle().
			Foreground(lipgloss.Color("3")). // Yellow
			Bold(true)

	InfoStyle = lipgloss.NewStyle().
			Foreground(lipgloss.Color("6")). // Cyan
			Italic(true)

	// Special styles
	ConnectionStyle = lipgloss.NewStyle().
			Foreground(lipgloss.Color("2")). // Green
			Italic(true)
)
