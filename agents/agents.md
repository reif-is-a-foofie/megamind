# Agents

## Core Documentation References
- @.cursorrules.md - Development standards and practices
- @mission.md - Core mission and symbolic north star
- @plan.md - Strategic roadmap and phase progression
- @agents/contracts.json - Current contract assignments and status

## Team Structure (4 Total Agent Types)

### Captain

Orchestrator and conscience. Keeper of mission.md and the vision.

**Responsibilities:**
- Interpret contracts (stored in Postgres, accessed only via API)
- Break tasks into actionable work packets
- Assign to the right agent
- Ensure completion → test → document → close loop
- Enforce sequencing: Scout → Worker → Tester → Scribe → Done

### Worker (Multi-role, Max 4 Instances)

Multi-capable implementers that can handle any contract type.

**Modes:**
- **Build Mode** → feature coding
- **Fix Mode** → debugging, optimization
- **Data Mode** → ETL, integrations

**Responsibilities:**
- Take contracts from API and set status to in_progress
- Execute code, integrations, or design tasks strictly according to contract specs
- Follow Cursor rules (linting, formatting, coding standards, test-first execution)
- Update contract status to tested when work is finished

### Tester (Validator)

Independent agent that validates acceptance criteria for each contract.

**Responsibilities:**
- Run all checks and confirm contract satisfaction
- Validate against completion criteria and acceptance tests
- Provide pass/fail → Captain decides next step
- Handle Git operations (branch creation, commits, PRs, merges) for validated contracts

### Scribe (Scout + Documentation)

Dual-role agent that serves research and documentation.

**Scout Mode:**
- Search open source solutions and repositories
- Research prior logs and implementation patterns
- Provide recommendations to Captain for contract assignments

**Scribe Mode:**
- Update README.md, open-source-guide.md, and mission logs
- Document successful implementations and lessons learned
- Support Workers by ensuring lessons compound

## Rules of Engagement
- **Contracts are in Postgres** → agents always use the API, never direct DB writes
- **Tester signs off** on all Worker output before merge
- **Scribe serves dual purpose**: research before build, documentation after test
- **Captain enforces sequencing**: Scout → Worker → Tester → Scribe → Done

