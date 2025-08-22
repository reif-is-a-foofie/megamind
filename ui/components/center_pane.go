package components

import (
	"fmt"
	"strings"
	"time"

	tea "github.com/charmbracelet/bubbletea"
)

// FeedItem represents a feed item
type FeedItem struct {
	ID      int
	Time    time.Time
	Source  string
	Content string
	Status  string
	Read    bool
}

// ChatMessage represents a chat message
type ChatMessage struct {
	Sender  string
	Content string
	Time    time.Time
}

// CenterPane represents the center pane with agent chat and feed
type CenterPane struct {
	width        int
	height       int
	cursor       int
	feedItems    []FeedItem
	chatMessages []ChatMessage
	inputBuffer  string
}

// NewCenterPane creates a new center pane
func NewCenterPane() *CenterPane {
	return &CenterPane{
		feedItems: []FeedItem{
			{ID: 1, Time: time.Now(), Source: "📧 Email", Content: "Meeting reminder: Team sync at 10:00", Status: "⏰ Pending", Read: false},
			{ID: 2, Time: time.Now(), Source: "💰 Finance", Content: "Gold price: $2,150/oz (+2.3%)", Status: "📈 Alert", Read: false},
			{ID: 3, Time: time.Now(), Source: "🌪️ Weather", Content: "Hurricane warning: Category 2 approaching", Status: "⚠️ Alert", Read: false},
			{ID: 4, Time: time.Now(), Source: "📅 Calendar", Content: "Team sync meeting starting now", Status: "🎯 Active", Read: true},
			{ID: 5, Time: time.Now(), Source: "📧 Email", Content: "Project update from client", Status: "📋 New", Read: false},
		},
		chatMessages: []ChatMessage{
			{Sender: "Captain", Content: "Worker agent, status report on ui.01 contract?", Time: time.Now()},
			{Sender: "Worker", Content: "Implementing three-pane terminal interface with Crush framework. Progress: 60%", Time: time.Now()},
			{Sender: "Captain", Content: "Excellent. Focus on core functionality first.", Time: time.Now()},
			{Sender: "Worker", Content: "Acknowledged. Will complete layout and basic navigation.", Time: time.Now()},
		},
	}
}

// Init initializes the center pane
func (cp *CenterPane) Init() tea.Cmd {
	return nil
}

// Update handles updates for the center pane
func (cp *CenterPane) Update(msg tea.Msg) (*CenterPane, tea.Cmd) {
	switch msg := msg.(type) {
	case tea.KeyMsg:
		switch msg.String() {
		case "up":
			if cp.cursor > 0 {
				cp.cursor--
			}
		case "down":
			if cp.cursor < len(cp.feedItems)-1 {
				cp.cursor++
			}
		case "enter":
			cp.markAsRead(cp.cursor)
		case "d":
			cp.markAsDone(cp.cursor)
		case "backspace":
			if len(cp.inputBuffer) > 0 {
				cp.inputBuffer = cp.inputBuffer[:len(cp.inputBuffer)-1]
			}
		default:
			if len(msg.String()) == 1 {
				cp.inputBuffer += msg.String()
			}
		}
	}
	return cp, nil
}

// View renders the center pane
func (cp *CenterPane) View() string {
	feedSection := cp.renderFeedItems()
	chatSection := cp.renderChatInterface()

	content := fmt.Sprintf("%s\n\n%s", feedSection, chatSection)

	title := "💬 Agent Chat & Feed"
	subtitle := "Press Enter to interact"

	return CenterPaneStyle.Render(fmt.Sprintf("%s\n%s\n\n%s", title, subtitle, content))
}

// SetSize sets the pane size
func (cp *CenterPane) SetSize(width, height int) {
	cp.width = width
	cp.height = height
}

// markAsRead marks a feed item as read
func (cp *CenterPane) markAsRead(index int) {
	if index >= 0 && index < len(cp.feedItems) {
		cp.feedItems[index].Read = true
	}
}

// markAsDone marks a feed item as done
func (cp *CenterPane) markAsDone(index int) {
	if index >= 0 && index < len(cp.feedItems) {
		cp.feedItems[index].Status = "✅ Done"
	}
}

// renderFeedItems renders the feed items section
func (cp *CenterPane) renderFeedItems() string {
	var lines []string
	lines = append(lines, "📰 Unified Feed")
	lines = append(lines, strings.Repeat("=", 30))
	lines = append(lines, "Time    Source    Content                    Status")
	lines = append(lines, strings.Repeat("-", 30))

	for i, item := range cp.feedItems {
		timeStr := item.Time.Format("15:04")
		line := fmt.Sprintf("%s  %s  %s  %s", timeStr, item.Source, item.Content, item.Status)

		if i == cp.cursor {
			line = CursorStyle.Render("> " + line)
		} else {
			line = "  " + line
		}

		if !item.Read {
			line = UnreadStyle.Render(line)
		}

		lines = append(lines, line)
	}

	return strings.Join(lines, "\n")
}

// renderChatInterface renders the chat interface section
func (cp *CenterPane) renderChatInterface() string {
	var lines []string
	lines = append(lines, "🤖 Agent Chat")
	lines = append(lines, strings.Repeat("=", 40))

	for _, msg := range cp.chatMessages {
		line := fmt.Sprintf("%s: %s", msg.Sender, msg.Content)
		lines = append(lines, line)
	}

	lines = append(lines, strings.Repeat("=", 40))
	lines = append(lines, fmt.Sprintf("Type your message: %s", cp.inputBuffer))

	return strings.Join(lines, "\n")
}
