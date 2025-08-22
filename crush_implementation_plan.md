# Captain's Crush-Based Implementation Plan

**Reference Base:** [Charmbracelet Crush](https://github.com/charmbracelet/crush)

## 🎯 Mission Translation: Crush Primitives → Butler System

### Core Crush Concepts for Butler Integration

| Crush Primitive | Butler Translation | Contract Mapping |
|----------------|-------------------|------------------|
| **Sessions** | Multi-context support (work, personal, finance) | `ui.01` - Three-pane layout |
| **LSP Backends** | Feed connectors (email, gold, weather) | `feed.01` - MCP-compatible connectors |
| **MCP Extensions** | Life integrations (finance, crypto, notify) | `finance.01`, `crypto.01`, `notify.01` |
| **Multi-Model** | Agent voices (OpenAI, local models) | `knowledge.01` - Model switching |
| **Bubble-Tea UI** | Three-pane dashboard | `ui.01` - Pane layout |
| **Persistence** | SQLite + cache integration | `memory.01` - Already complete |
| **Overlays** | Gamification + quests | `game.01` - XP system |

## 🚀 Implementation Sequence

### Phase 1: Foundation (CRITICAL - Missing Implementation)

#### 1. **feed.01 - Crush MCP Feed Connectors** ⚡ IMMEDIATE
**Crush Integration**: Replace LSP backends with MCP-compatible connectors
- **Email Connector**: MCP-compatible email integration
- **Gold Price API**: Real-time gold price via MCP
- **Hurricane Alerts**: Weather alerts via MCP
- **Crush Integration**: Must conform to Model Context Protocol

**Implementation Path**:
```go
feed/
├── main.go              # MCP server entry point
├── connectors/
│   ├── email.go         # Email MCP connector
│   ├── gold.go          # Gold price MCP connector
│   ├── weather.go       # Hurricane alerts MCP connector
│   └── base.go          # Base MCP connector interface
└── mcp/
    ├── protocol.go      # MCP protocol implementation
    └── handlers.go      # MCP message handlers
```

#### 2. **ui.01 - Crush Three-Pane Butler Interface** ⚡ IMMEDIATE
**Crush Integration**: Extend Bubble-Tea UI with three-pane layout
- **Left Pane**: File explorer + knowledge graph (Crush Session integration)
- **Center Pane**: Agent chat interface (Crush Multi-Model integration)
- **Right Pane**: Logs, alerts, XP overlay (Crush MCP integration)

**Implementation Path**:
```go
ui/
├── main.go              # Crush UI entry point
├── components/
│   ├── layout.go        # Three-pane layout manager
│   ├── left_pane.go     # File explorer + knowledge graph
│   ├── center_pane.go   # Agent chat interface
│   ├── right_pane.go    # Logs, alerts, XP overlay
│   └── navigation.go    # Crush keybindings
├── styles/
│   ├── theme.go         # Pirate/butler aesthetic
│   └── colors.go        # Color scheme
└── integrations/
    ├── memory.go        # Memory system connector
    ├── feed.go          # Feed MCP connector
    └── api.go           # Contracts API integration
```

### Phase 2: Life Integrations (MCP Extensions)

#### 3. **finance.01 - Financial MCP Connector**
**Crush Integration**: MCP-compatible financial data connector
- **Banking APIs**: Account balances, transactions
- **Investment Data**: Portfolio tracking
- **Crush Integration**: MCP protocol for financial data

#### 4. **crypto.01 - Cryptocurrency MCP Connector**
**Crush Integration**: MCP-compatible crypto data connector
- **Price Feeds**: Real-time crypto prices
- **Portfolio Tracking**: Crypto holdings
- **Crush Integration**: MCP protocol for crypto data

#### 5. **notify.01 - Meeting Alerts MCP Connector**
**Crush Integration**: MCP-compatible calendar connector
- **Calendar APIs**: Google, iCloud integration
- **Meeting Alerts**: Real-time notifications
- **Join Actions**: One-keystroke meeting joining

### Phase 3: Intelligence Layer

#### 6. **knowledge.01 - Advanced Knowledge Graph** ✅ COMPLETED
**Crush Integration**: Extend with model switching capabilities
- **Multi-Model Support**: Switch between OpenAI, local models
- **Agent Voices**: Different "personalities" per model
- **Context Persistence**: Maintain context across model switches

#### 7. **actions.01 - Advanced Action System** ✅ COMPLETED
**Crush Integration**: MCP-compatible action system
- **Action Templates**: Reusable action patterns
- **External Integration**: Email, calendar, file systems
- **Crush Integration**: MCP protocol for actions

### Phase 4: Gamification & Autonomy

#### 8. **game.01 - Gamified XP & Pirate Aesthetic**
**Crush Integration**: UI overlay on Crush interface
- **XP System**: Experience points for actions
- **Quest System**: Pirate-themed quests
- **UI Overlay**: XP display, quest popups, raid triggers

#### 9. **autonomy.01 - Autonomous Butler Actions**
**Crush Integration**: Autonomous decision making
- **Smart Responses**: Automatic email replies
- **Meeting Scheduling**: Intelligent calendar management
- **Crush Integration**: MCP protocol for autonomous actions

## 🔧 Technical Implementation Strategy

### Crush Integration Patterns

#### 1. **MCP Protocol Compliance**
```go
// All connectors must implement MCP interface
type MCPConnector interface {
    Initialize() error
    HandleRequest(req MCPRequest) (MCPResponse, error)
    Shutdown() error
}
```

#### 2. **Session Integration**
```go
// Multi-context session management
type ButlerSession struct {
    Context    string // work, personal, finance
    Model      string // OpenAI, local, etc.
    Memory     *MemorySystem
    Feed       *FeedConnector
}
```

#### 3. **UI Component Architecture**
```go
// Three-pane layout with Crush integration
type ButlerUI struct {
    LeftPane   *FileExplorerPane
    CenterPane *ChatPane
    RightPane  *LogsPane
    Session    *ButlerSession
}
```

### Development Workflow

#### 1. **Foundation First**
- Start with `feed.01` - MCP connectors
- Then `ui.01` - Three-pane interface
- Ensure Crush integration at each step

#### 2. **Integration Testing**
- Test MCP protocol compliance
- Validate Crush keybindings
- Verify session persistence

#### 3. **Progressive Enhancement**
- Core functionality first
- Aesthetics and polish second
- Advanced features last

## 📋 Captain's Assignment Checklist

### Immediate Actions (Phase 1)
- [ ] **Reassign feed.01** to worker with Crush MCP focus
- [ ] **Reassign ui.01** to worker with Crush UI focus
- [ ] **Validate memory.01** integration with Crush persistence
- [ ] **Test orchestrator.01** with Crush session management

### Validation Criteria
- [ ] **MCP Compliance**: All connectors follow Crush MCP protocol
- [ ] **Session Integration**: Multi-context switching works
- [ ] **UI Responsiveness**: Three-pane layout functions
- [ ] **Keybinding Support**: Crush shortcuts work
- [ ] **Memory Persistence**: Data persists across sessions

### Success Metrics
- [ ] **Zero Greenfield Code**: All systems extend Crush primitives
- [ ] **Seamless Integration**: No reinvention of Crush concepts
- [ ] **Performance**: Maintains Crush's responsiveness
- [ ] **Usability**: Follows Crush's interaction patterns

## 🎯 Mission Impact

This Crush-based approach provides:
- **Foundation Stability**: Built on proven Crush primitives
- **Rapid Development**: Extend existing concepts, don't reinvent
- **Consistent UX**: Follows established Crush patterns
- **Scalable Architecture**: MCP protocol enables easy extensions
- **Future-Proof**: Aligned with Charmbracelet ecosystem

The galleon now has a solid keel (Crush foundation) that supports all other systems with precision and consistency! 🚀⚡

**READY FOR CAPTAIN'S ORDERS** - Standing by to execute Crush-based implementation! 🏴‍☠️
