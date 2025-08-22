package components

import (
	"fmt"
	"strings"

	tea "github.com/charmbracelet/bubbletea"
)

// LeftPane represents the left pane with file explorer and knowledge graph
type LeftPane struct {
	width     int
	height    int
	viewMode  string // "files" or "knowledge"
	cursor    int
	items     []string
	knowledge []KnowledgeItem
}

// KnowledgeItem represents a knowledge graph item
type KnowledgeItem struct {
	Entity      string
	Type        string
	Connections []string
}

// NewLeftPane creates a new left pane
func NewLeftPane() *LeftPane {
	return &LeftPane{
		viewMode: "files",
		items: []string{
			"📁 agents/",
			"📁 api/",
			"📁 database/",
			"📁 finance/",
			"📁 knowledge/",
			"📁 memory/",
			"📁 orchestrator/",
			"📁 ui/",
		},
		knowledge: []KnowledgeItem{
			{Entity: "Megamind System", Type: "System", Connections: []string{"Memory", "Finance", "Knowledge"}},
			{Entity: "Memory Store", Type: "Component", Connections: []string{"Feed", "Actions", "API"}},
			{Entity: "Finance Manager", Type: "Component", Connections: []string{"Banking", "Crypto", "Analytics"}},
			{Entity: "Knowledge Graph", Type: "Component", Connections: []string{"Patterns", "Insights", "Queries"}},
			{Entity: "Butler Interface", Type: "UI", Connections: []string{"Three-pane", "Navigation", "Theme"}},
			{Entity: "Contract System", Type: "Orchestration", Connections: []string{"Captain", "Worker", "Tester"}},
		},
	}
}

// Init initializes the left pane
func (lp *LeftPane) Init() tea.Cmd {
	return nil
}

// Update handles updates for the left pane
func (lp *LeftPane) Update(msg tea.Msg) (*LeftPane, tea.Cmd) {
	switch msg := msg.(type) {
	case tea.KeyMsg:
		switch msg.String() {
		case "up":
			if lp.cursor > 0 {
				lp.cursor--
			}
		case "down":
			if lp.viewMode == "files" && lp.cursor < len(lp.items)-1 {
				lp.cursor++
			} else if lp.viewMode == "knowledge" && lp.cursor < len(lp.knowledge)-1 {
				lp.cursor++
			}
		case "tab":
			lp.toggleViewMode()
		}
	}
	return lp, nil
}

// View renders the left pane
func (lp *LeftPane) View() string {
	var content string

	if lp.viewMode == "files" {
		content = lp.renderFileExplorer()
	} else {
		content = lp.renderKnowledgeGraph()
	}

	title := "🗂️ Files & Knowledge"
	subtitle := fmt.Sprintf("Mode: %s", strings.Title(lp.viewMode))

	return LeftPaneStyle.Render(fmt.Sprintf("%s\n%s\n\n%s", title, subtitle, content))
}

// SetSize sets the pane size
func (lp *LeftPane) SetSize(width, height int) {
	lp.width = width
	lp.height = height
}

// toggleViewMode switches between file explorer and knowledge graph
func (lp *LeftPane) toggleViewMode() {
	if lp.viewMode == "files" {
		lp.viewMode = "knowledge"
		lp.cursor = 0
	} else {
		lp.viewMode = "files"
		lp.cursor = 0
	}
}

// renderFileExplorer renders the file explorer view
func (lp *LeftPane) renderFileExplorer() string {
	var lines []string

	for i, item := range lp.items {
		if i == lp.cursor {
			lines = append(lines, CursorStyle.Render("> "+item))
		} else {
			lines = append(lines, "  "+item)
		}
	}

	return strings.Join(lines, "\n")
}

// renderKnowledgeGraph renders the knowledge graph view
func (lp *LeftPane) renderKnowledgeGraph() string {
	var lines []string

	for i, item := range lp.knowledge {
		line := fmt.Sprintf("%s (%s)", item.Entity, item.Type)
		if i == lp.cursor {
			lines = append(lines, CursorStyle.Render("> "+line))
		} else {
			lines = append(lines, "  "+line)
		}

		// Add connections
		connections := strings.Join(item.Connections, ", ")
		if i == lp.cursor {
			lines = append(lines, "    "+ConnectionStyle.Render(connections))
		} else {
			lines = append(lines, "    "+connections)
		}
		lines = append(lines, "")
	}

	return strings.Join(lines, "\n")
}
