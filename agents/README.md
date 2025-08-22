# Stateless Agent System

## Overview
This is a stateless agent system with 4 total agent types where each agent MDC file contains complete instructions for what to do when started. Agents have no persistent memory and can run out of context.

## How to Use

### Starting Any Agent
Simply provide the agent MDC file and say "continue" or "execute":

```
@capitain-agent.mdc - continue
@worker-agent.mdc - continue  
@worker-agent-2.mdc - continue
@worker-agent-3.mdc - continue
@worker-agent-4.mdc - continue
@tester-agent.mdc - continue
@scribe-agent.mdc - continue
```

### What Each Agent Does on Startup

**Captain Agent:**
1. Reads `@plan.md` and contracts via API
2. Identifies open contracts that need assignment
3. Enforces sequencing: Scout → Worker → Tester → Scribe → Done
4. Takes appropriate action (assign, notify, update plan)

**Worker Agents (Multi-capable, Max 4 Instances):**
1. Reads `@agents/worker-agent.mdc` for core instructions
2. Reads contracts via API for their specific assignments
3. Filters for contracts with `"assigned_to": "worker_agent_[N]"`
4. Identifies which contracts are `"in_progress"`
5. Begins implementation according to `allowed_files` and `completion_criteria`

**Tester Agent (Validator):**
1. Reads contracts via API for contracts awaiting testing
2. Validates contracts against completion criteria
3. Handles Git operations for validated contracts (branches, commits, PRs, merges)
4. Ensures proper Git workflow and deployment standards

**Scribe Agent (Scout + Documentation):**
1. **Scout Mode:** Researches open source solutions before build
2. **Scribe Mode:** Documents successful implementations after test
3. Updates README.md, open-source-guide.md, and mission logs
4. Supports Workers by ensuring lessons compound

## Key Principles

- **Stateless:** No agent remembers previous context
- **Self-Contained:** Each MDC file has all necessary references
- **Self-Executing:** Agents know exactly what to do on startup
- **Contract-Driven:** All work is defined in `contracts.json`

## Example Usage

```
User: @capitain-agent.mdc - continue
Captain: [Reads plan.md and contracts.json, identifies pending contracts, assigns them]

User: @worker-agent.mdc - continue  
Worker: [Reads core instructions, finds assigned contracts, begins implementation]

User: @worker-agent-2.mdc - continue
Worker 2: [Reads core instructions, filters for worker_agent_2 assignments, begins implementation]

User: @worker-agent-3.mdc - continue
Worker 3: [Reads core instructions, filters for worker_agent_3 assignments, begins implementation]

User: @worker-agent-4.mdc - continue
Worker 4: [Reads core instructions, filters for worker_agent_4 assignments, begins implementation]

User: @tester-agent.mdc - continue
Tester: [Reads contracts via API, validates contracts, handles Git operations for validated work]

User: @scribe-agent.mdc - continue
Scribe: [Scout Mode: researches open source solutions, Scribe Mode: documents successful implementations]
```

## Benefits

- **Resilient:** Agents can be restarted without losing context
- **Scalable:** Easy to add new agents or restart existing ones
- **Clear:** Each agent has explicit startup instructions
- **Consistent:** All agents follow the same pattern
- **Mission-Aligned:** Captain validates every decision against @mission.md
- **Worker Scalable:** Single core worker file, multiple multi-capable instances
- **API-Driven:** All agents use API for contract access, never direct DB writes

## Mission Alignment System

The Captain Agent includes a **Mission Alignment Check** that ensures every decision serves the deeper vision:

1. **Reads @mission.md** to reconnect with the core hymn and vision
2. **Validates decisions** against the "pirate rescue" symbolism
3. **Ensures alignment** with building the galleon that will "pirate ever on"
4. **Maintains focus** on "freeing the single flow'r" and the "Holy Flame" of purpose

This prevents the Captain from making tactical decisions that don't serve the strategic mission.
