package main

import (
	"fmt"
	"os"

	"megamind/ui/components"

	tea "github.com/charmbracelet/bubbletea"
	"github.com/charmbracelet/lipgloss"
)

// Main application model
type ButlerModel struct {
	leftPane   *components.LeftPane
	centerPane *components.CenterPane
	rightPane  *components.RightPane
	width      int
	height     int
	focused    int // 0=left, 1=center, 2=right
}

// Initialize the main model
func initialModel() ButlerModel {
	return ButlerModel{
		leftPane:   components.NewLeftPane(),
		centerPane: components.NewCenterPane(),
		rightPane:  components.NewRightPane(),
		focused:    1, // Start with center pane focused
	}
}

// Init function for Bubble Tea
func (m ButlerModel) Init() tea.Cmd {
	return tea.Batch(
		m.leftPane.Init(),
		m.centerPane.Init(),
		m.rightPane.Init(),
	)
}

// Update function for Bubble Tea
func (m ButlerModel) Update(msg tea.Msg) (tea.Model, tea.Cmd) {
	var cmd tea.Cmd

	switch msg := msg.(type) {
	case tea.WindowSizeMsg:
		m.width = msg.Width
		m.height = msg.Height
		// Update panes with new dimensions
		m.leftPane.SetSize(msg.Width/3, msg.Height-2)
		m.centerPane.SetSize(msg.Width/3, msg.Height-2)
		m.rightPane.SetSize(msg.Width/3, msg.Height-2)

	case tea.KeyMsg:
		switch msg.String() {
		case "tab":
			m.focused = (m.focused + 1) % 3
		case "shift+tab":
			m.focused = (m.focused + 2) % 3
		case "ctrl+c", "q":
			return m, tea.Quit
		}
	}

	// Update focused pane
	switch m.focused {
	case 0:
		m.leftPane, cmd = m.leftPane.Update(msg)
	case 1:
		m.centerPane, cmd = m.centerPane.Update(msg)
	case 2:
		m.rightPane, cmd = m.rightPane.Update(msg)
	}

	return m, cmd
}

// View function for Bubble Tea
func (m ButlerModel) View() string {
	// Create header
	header := m.renderHeader()

	// Create panes
	leftView := m.leftPane.View()
	centerView := m.centerPane.View()
	rightView := m.rightPane.View()

	// Apply focus styling
	if m.focused == 0 {
		leftView = focusedStyle.Render(leftView)
	} else {
		leftView = unfocusedStyle.Render(leftView)
	}

	if m.focused == 1 {
		centerView = focusedStyle.Render(centerView)
	} else {
		centerView = unfocusedStyle.Render(centerView)
	}

	if m.focused == 2 {
		rightView = focusedStyle.Render(rightView)
	} else {
		rightView = unfocusedStyle.Render(rightView)
	}

	// Combine panes horizontally
	panes := lipgloss.JoinHorizontal(
		lipgloss.Top,
		leftView,
		centerView,
		rightView,
	)

	// Combine header and panes
	return lipgloss.JoinVertical(lipgloss.Left, header, panes)
}

// Render the header with pirate/butler aesthetic
func (m ButlerModel) renderHeader() string {
	title := "⚓ MEGAMIND BUTLER INTERFACE ⚓"
	subtitle := "Your Life, Unified in One Stream"

	header := lipgloss.NewStyle().
		Bold(true).
		Foreground(lipgloss.Color("11")). // Yellow
		Align(lipgloss.Center).
		Width(m.width).
		Render(title + "\n" + subtitle)

	return headerStyle.Render(header)
}

// Styles
var (
	headerStyle = lipgloss.NewStyle().
			Border(lipgloss.RoundedBorder()).
			BorderForeground(lipgloss.Color("11")). // Yellow
			Padding(0, 1).
			Margin(0, 0, 1, 0)

	focusedStyle = lipgloss.NewStyle().
			Border(lipgloss.RoundedBorder()).
			BorderForeground(lipgloss.Color("6")). // Cyan
			BorderStyle(lipgloss.ThickBorder())

	unfocusedStyle = lipgloss.NewStyle().
			Border(lipgloss.RoundedBorder()).
			BorderForeground(lipgloss.Color("8")). // Gray
			BorderStyle(lipgloss.NormalBorder())
)

// Main function
func main() {
	p := tea.NewProgram(
		initialModel(),
		tea.WithAltScreen(),
		tea.WithMouseCellMotion(),
	)

	if _, err := p.Run(); err != nil {
		fmt.Printf("Error running butler interface: %v", err)
		os.Exit(1)
	}
}
