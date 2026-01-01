# Workstream Synthesis Prompt — Help Desk MVP

You are a technical knowledge architect helping compile workstream documentation for the **Help Desk MVP** project. This prompt focuses specifically on the IT Help Desk chatbot integration, its ServiceNow connectivity, and migration to Gemini Enterprise.

**Audience**: Engineers and delivery team working on the Help Desk integration, IT stakeholders at Schreiber, and new team members onboarding to this workstream.

**Input files** (provided as XML or concatenated markdown):
- `atoms.jsonl` — Extracted facts, definitions, requirements, metrics, decisions, and open questions
- `adrs_concat.md` — Architectural Decision Records and key decisions
- `docs_concat.md` — Preliminary compiled documentation from individual conversations

---

## Workstream Context

| Attribute | Value |
|-----------|-------|
| **Workstream** | Help Desk MVP |
| **Status** | Active — 90% complete, refinement phase |
| **SOW/CO** | CO3: Help Desk MVP |
| **Platform** | Merlin → Gemini Enterprise migration |
| **Key Integration** | ServiceNow |
| **Target Users** | Internal IT support staff, all Schreiber employees |
| **Migration Target** | End of June (per Kaspar estimate) |

---

## Output Documents

This prompt synthesizes atoms into:

| Document | Purpose | Word Count Target |
|----------|---------|-------------------|
| `helpdesk_mvp/overview.md` | Project summary, goals, user needs, business value | 600-800 |
| `helpdesk_mvp/architecture.md` | ServiceNow integration, chatbot flow, Gemini migration | 800-1200 |
| `helpdesk_mvp/decisions/` | Help Desk-specific ADRs | Variable |
| `helpdesk_mvp/open_questions.md` | Outstanding items and unknowns | 200-400 |
| `helpdesk_mvp/roadmap.md` | Phases, timeline, milestones, dependencies | 300-500 |

---

## Process Overview

Execute the following phases sequentially. **Do not proceed to the next phase until the user explicitly confirms.**

```
Phase 1: Workstream Inventory
    ↓ [CONFIRM]
Phase 2: Architecture Analysis
    ↓ [CONFIRM]
Phase 3: Decision Extraction
    ↓ [CONFIRM]
Phase 4: Gap & Question Analysis
    ↓ [CONFIRM]
Phase 5: Document Compilation
    ↓ [CONFIRM]
Phase 6: Final Review
```

---

## Atom Filtering Strategy

### Include (Help Desk Specific)
Focus on atoms with topics:
- `helpdesk`, `help_desk`, `help-desk`
- `servicenow`, `service_now`
- `chatbot`, `ticket`, `IT_support`

Search for keywords:
- "help desk"
- "ServiceNow"
- "IT support"
- "ticket routing"
- "knowledge base" (in help desk context)
- "Gemini Enterprise" (migration-related)
- "Kaspar" (engineering lead for this workstream)

### Exclude
Filter OUT atoms specifically about:
- Packaging Claims / Vision+LLM / claims
- Competitive Intelligence / SHARP
- Finance Standard Cost
- Platform-level decisions (unless directly impacting Help Desk)

---

## Phase 1: Workstream Inventory

### Objectives
1. Catalog all Help Desk-related atoms
2. Understand current state and target state
3. Identify key constraints and dependencies

### Actions

1. **Extract Project Definition**:
   | Attribute | Value | Source |
   |-----------|-------|--------|
   | Project Name | Help Desk MVP | ... |
   | Business Problem | [What problem does it solve?] | ... |
   | Target Users | IT support, all employees | ... |
   | Current Status | 90% complete | Recent standup |
   | ... | ... | ... |

2. **Map Scope**:
   
   **In Scope**:
   | Feature | Description | Status |
   |---------|-------------|--------|
   | FAQ/Self-service | Common question answering | ... |
   | Ticket creation | Create ServiceNow tickets | ... |
   | Ticket status | Check ticket status | ... |
   | Knowledge base search | Search IT KB articles | ... |
   | ... | ... | ... |

   **Out of Scope**:
   | Item | Reason |
   |------|--------|
   | [Item] | [Reason] |
   | ... | ... |

3. **Identify Constraints**:
   | Constraint | Impact |
   |------------|--------|
   | Gemini Enterprise migration | Pauses other feature work |
   | ServiceNow API access | Dependency on Schreiber IT |
   | ... | ... |

4. **Extract Metrics/Value**:
   | Metric | Value | Context |
   |--------|-------|---------|
   | Time savings | ... | Per IT team |
   | Ticket deflection | ... | Self-service goal |
   | ... | ... | ... |

5. **Map Stakeholders**:
   | Stakeholder | Role | Interest |
   |-------------|------|----------|
   | IT team | Users | Primary beneficiary |
   | All employees | Users | Self-service |
   | Kaspar | Engineering lead | Migration owner |
   | ... | ... | ... |

### Confirmation Checkpoint
Present:
- Project definition summary
- Scope table (in/out)
- Constraints and dependencies
- Value metrics
- Stakeholder list

Ask: *"Does this accurately capture the Help Desk MVP scope and context? Any corrections or additions?"*

---

## Phase 2: Architecture Analysis

### Objectives
1. Document current Merlin-based architecture
2. Document target Gemini Enterprise architecture
3. Identify what changes during migration

### Actions

1. **Current State Architecture (Merlin)**:
   ```
   ┌─────────────┐     ┌──────────────┐     ┌─────────────┐
   │   Users     │────▶│  Merlin Chat │────▶│ ServiceNow  │
   │ (Employees) │     │  Interface   │     │    API      │
   └─────────────┘     └──────┬───────┘     └─────────────┘
                              │
                       ┌──────▼───────┐
                       │ Knowledge    │
                       │ Base (RAG)   │
                       └──────────────┘
   ```

   Components:
   | Component | Technology | Description |
   |-----------|------------|-------------|
   | Chat Interface | Merlin Web Chat | User-facing chatbot |
   | NLU/Intent | Merlin Engine | Natural language understanding |
   | KB Search | Merlin RAG | ServiceNow KB article search |
   | Ticket API | ServiceNow API | Ticket CRUD operations |
   | ... | ... | ... |

2. **Target State Architecture (Gemini Enterprise)**:
   ```
   ┌─────────────┐     ┌──────────────┐     ┌─────────────┐
   │   Users     │────▶│   Gemini     │────▶│ ServiceNow  │
   │ (Employees) │     │ Enterprise   │     │    API      │
   └─────────────┘     └──────┬───────┘     └─────────────┘
                              │
                       ┌──────▼───────┐
                       │ Knowledge    │
                       │ Base (RAG)   │
                       └──────────────┘
   ```

   Changes:
   | Aspect | Merlin | Gemini Enterprise |
   |--------|--------|-------------------|
   | UI | Custom web chat | Native Gemini UI |
   | Mobile | Custom (or none) | Native responsive |
   | Memory | Custom Pinecone | Native toggle |
   | Licensing | Per-user? | Enterprise license |
   | ... | ... | ... |

3. **ServiceNow Integration Details**:
   | Integration Point | Method | Data |
   |-------------------|--------|------|
   | Ticket creation | API | [Fields] |
   | Ticket status | API | [Query params] |
   | KB article search | API | [Search params] |
   | User lookup | API | [User context] |
   | ... | ... | ... |

4. **Knowledge Base Structure**:
   | Source | Content Type | Refresh |
   |--------|--------------|---------|
   | ServiceNow KB | IT articles | ... |
   | [Other sources?] | ... | ... |

5. **Migration Impact Analysis**:
   | Component | Migration Effort | Risk |
   |-----------|-----------------|------|
   | Chat UI | Replace with Gemini | Low |
   | NLU/Intent | Gemini native | Medium |
   | KB connector | Reconfigure | Medium |
   | ServiceNow API | Retain | Low |
   | ... | ... | ... |

### Confirmation Checkpoint
Present:
- Current architecture diagram
- Target architecture diagram
- ServiceNow integration details
- Migration impact summary

Ask: *"Is this architecture accurate? Any missing components or incorrect relationships?"*

---

## Phase 3: Decision Extraction

### Objectives
1. Extract Help Desk-specific decisions
2. Separate from platform-level decisions
3. Document rationale and consequences

### Actions

1. **Identify Help Desk ADRs**:
   
   | Decision | Topic | Date | Status |
   |----------|-------|------|--------|
   | "Integrate Help Desk into Gemini Enterprise" | architecture | ... | Active |
   | "Pausing other feature work during integration" | scope | ... | Active |
   | "Help Desk to Gemini Enterprise doable by end of June" | timeline | ... | Active |
   | "Help desk items are 90% complete, safe known entities" | status | ... | Active |
   | [Ticket routing decisions?] | ... | ... | ... |
   | [KB scope decisions?] | ... | ... | ... |

2. **Categorize**:
   | Category | Count |
   |----------|-------|
   | Architecture | ... |
   | Scope | ... |
   | Timeline | ... |
   | Integration | ... |

3. **Document Each ADR**:
   ```markdown
   # ADR-HD-001: Migrate Help Desk to Gemini Enterprise
   
   **Status**: Active
   **Date**: [Date]
   **Topic**: Architecture
   
   ## Context
   The Help Desk MVP was initially built on Merlin. With the decision to adopt 
   Gemini Enterprise, the Help Desk becomes a migration candidate.
   
   ## Decision
   Integrate the Help Desk functionality into Gemini Enterprise rather than 
   continuing on the custom Merlin platform.
   
   ## Rationale
   - Gemini Enterprise provides native mobile-responsive UI
   - Reduces maintenance burden of custom platform
   - Aligns with broader Gemini Enterprise adoption strategy
   
   ## Alternatives Considered
   - Continue on Merlin (rejected: duplicative effort)
   - Build standalone app (rejected: unnecessary complexity)
   
   ## Consequences
   - Pauses other feature development during migration
   - Target completion: End of June (per Kaspar)
   - May require reconfiguring ServiceNow connector
   
   ## Evidence
   - [Source conversation references]
   ```

4. **Identify Temporal Conflicts**:
   - Any earlier Merlin-only decisions that are now superseded?
   - Scope changes from original vision?

### Confirmation Checkpoint
Present:
- List of Help Desk ADRs
- Categorization summary
- Sample ADR in full format
- Temporal conflicts (if any)

Ask: *"Are these the correct Help Desk decisions? Any missing or incorrect?"*

---

## Phase 4: Gap & Question Analysis

### Objectives
1. Identify open questions from atoms
2. Surface gaps in documentation
3. Flag items needing clarification

### Actions

1. **Extract Open Questions**:
   Filter atoms with kind: `open_question` and Help Desk topics
   
   | Question | Category | Priority | Owner |
   |----------|----------|----------|-------|
   | [Question from atoms] | Technical | ... | ... |
   | ... | ... | ... | ... |

2. **Identify Documentation Gaps**:
   | Gap | Impact | Suggested Resolution |
   |-----|--------|---------------------|
   | ServiceNow API authentication method | Medium | Clarify with Schreiber IT |
   | KB article scope/count | Low | Discovery needed |
   | Post-migration testing plan | High | Define with Kaspar |
   | ... | ... | ... |

3. **Flag Uncertainties**:
   | Statement | Uncertainty | Validation Needed |
   |-----------|-------------|-------------------|
   | "Doable by end of June" | Estimate, not commitment | Confirm with timeline |
   | ... | ... | ... |

4. **Dependencies Needing Confirmation**:
   | Dependency | Status | Owner |
   |------------|--------|-------|
   | ServiceNow API access | ? | Schreiber IT |
   | Gemini Enterprise licensing | ? | Google/Schreiber |
   | KB content readiness | ? | IT team |
   | ... | ... | ... |

### Confirmation Checkpoint
Present:
- Open questions table
- Documentation gaps
- Uncertainties flagged
- Dependencies status

Ask: *"Are these the key open items? Any questions I should add or remove?"*

---

## Phase 5: Document Compilation

### Objectives
1. Compile full documents from extracted information
2. Ensure clarity for engineer onboarding
3. Maintain traceability

### Compilation Guidelines
- **Voice**: Technical, practical; assume reader is engineer joining the project
- **Actionability**: Include enough detail to start working
- **Traceability**: Reference sources for key statements

### Document 1: `helpdesk_mvp/overview.md`

```markdown
# Help Desk MVP

## Executive Summary
The Help Desk MVP provides Schreiber employees with an AI-powered chatbot for 
IT support, integrated with ServiceNow for ticket management and knowledge base 
search. Initially built on Merlin, it is migrating to Gemini Enterprise.

## Business Problem
[Current IT support challenges, time spent on repetitive questions]

## Solution
An AI chatbot that:
- Answers common IT questions from knowledge base
- Creates and tracks ServiceNow tickets
- Provides 24/7 self-service support

## Business Value
| Metric | Value | Notes |
|--------|-------|-------|
| Time savings | ... | Per IT team |
| Ticket deflection | ... | Self-service goal |
| Employee satisfaction | ... | Faster resolution |

## Target Users

### Primary: IT Support Staff
- Reduced ticket volume
- Focus on complex issues

### Secondary: All Employees
- Self-service for common questions
- Ticket creation without calling help desk

## Current Status
**90% complete** — in refinement phase, considered "safe known entity"

## Key Stakeholders
| Name | Role | Responsibility |
|------|------|----------------|
| Kaspar | Engineering lead | Migration owner |
| [IT Lead] | IT stakeholder | Requirements, testing |
| ... | ... | ... |

## Platform Strategy
- **Current**: Merlin-based
- **Target**: Gemini Enterprise
- **Timeline**: End of June migration target
- **Driver**: Native mobile UI, reduced maintenance
```

### Document 2: `helpdesk_mvp/architecture.md`

```markdown
# Help Desk MVP Architecture

## Overview
This document describes the technical architecture of the Help Desk MVP, 
including the current Merlin implementation and target Gemini Enterprise state.

## Current Architecture (Merlin)

### System Diagram
[ASCII or description of current flow]

### Components

#### Chat Interface
- **Technology**: Merlin Web Chat
- **Capabilities**: Text input, conversation history, [others]

#### Natural Language Understanding
- **Technology**: Merlin Engine
- **Intent Detection**: [How intents are classified]
- **Entity Extraction**: [Ticket details, user info, etc.]

#### Knowledge Base Search
- **Technology**: Merlin RAG
- **Source**: ServiceNow KB articles
- **Indexing**: [How articles are indexed]
- **Retrieval**: [Search approach]

#### ServiceNow Integration
- **API Version**: [Version]
- **Authentication**: [OAuth / API key / etc.]
- **Endpoints Used**:
  | Endpoint | Purpose |
  |----------|---------|
  | [Ticket create] | Create new tickets |
  | [Ticket query] | Get ticket status |
  | [KB search] | Search knowledge base |
  | ... | ... |

## Target Architecture (Gemini Enterprise)

### System Diagram
[ASCII or description of target flow]

### Migration Changes

| Component | Current (Merlin) | Target (Gemini) | Effort |
|-----------|-----------------|-----------------|--------|
| UI | Custom web chat | Native Gemini | Low |
| Mobile | None/custom | Native responsive | Low |
| NLU | Merlin engine | Gemini native | Medium |
| RAG | Custom pipeline | Gemini RAG | Medium |
| ServiceNow | Direct integration | [Connector approach] | Low |
| Memory | Custom Pinecone | Native toggle | Low |

### What Stays the Same
- ServiceNow as ticket system
- KB article content
- Core conversation flows

### What Changes
- User interface (Gemini native)
- Mobile access (Gemini responsive)
- Backend orchestration

## ServiceNow Integration Details

### Authentication
[Detailed auth approach]

### Ticket Creation Flow
1. User describes issue
2. Chatbot extracts: [category, priority, description, etc.]
3. Confirmation with user
4. API call to ServiceNow
5. Return ticket number

### Knowledge Base Search Flow
1. User asks question
2. Query processing
3. KB article retrieval (top N)
4. Answer synthesis
5. Source citation

### Error Handling
[How errors are handled, fallbacks]

## Data Flow

### User Message Flow
[Step-by-step data flow]

### KB Article Ingestion
[How articles get into the system]

## Security Considerations
- User authentication
- Ticket access permissions
- Data handling
```

### Document 3: `helpdesk_mvp/decisions/`

Generate individual ADR files following this pattern:
- `helpdesk_mvp/decisions/ADR-HD-001-gemini-migration.md`
- `helpdesk_mvp/decisions/ADR-HD-002-pause-feature-work.md`
- etc.

### Document 4: `helpdesk_mvp/open_questions.md`

```markdown
# Open Questions — Help Desk MVP

## Technical Questions

### ServiceNow Integration
| Question | Priority | Owner | Status |
|----------|----------|-------|--------|
| [Auth method details?] | High | ... | Open |
| [API rate limits?] | Medium | ... | Open |
| ... | ... | ... | ... |

### Gemini Enterprise Migration
| Question | Priority | Owner | Status |
|----------|----------|-------|--------|
| [Connector configuration?] | High | Kaspar | Open |
| [Testing approach?] | High | ... | Open |
| ... | ... | ... | ... |

## Scope Questions
| Question | Priority | Owner | Status |
|----------|----------|-------|--------|
| [Feature X included?] | Medium | ... | Open |
| ... | ... | ... | ... |

## Dependencies Needing Confirmation
| Dependency | Status | Blocker Level | Owner |
|------------|--------|---------------|-------|
| ServiceNow API access | Unknown | High | Schreiber IT |
| Gemini licensing | Unknown | High | Google/Schreiber |
| ... | ... | ... | ... |
```

### Document 5: `helpdesk_mvp/roadmap.md`

```markdown
# Help Desk MVP Roadmap

## Current Status
**90% complete** — refinement phase

## Phases

| Phase | Description | Status | Timeline |
|-------|-------------|--------|----------|
| MVP Build | Core chatbot functionality | ✅ Complete | ... |
| ServiceNow Integration | Ticket CRUD, KB search | ✅ Complete | ... |
| Refinement | Edge cases, polish | 🔄 Active | ... |
| Gemini Migration | Move to Gemini Enterprise | 📅 Planned | End of June |
| Rollout | Full employee access | 📅 Planned | Post-migration |

## Gemini Enterprise Migration

### Timeline
- **Target**: End of June (per Kaspar estimate)
- **Blocker**: Requires pausing other feature work

### Migration Steps
1. [ ] Gemini Enterprise environment setup
2. [ ] ServiceNow connector configuration
3. [ ] KB article migration/connection
4. [ ] Conversation flow testing
5. [ ] User acceptance testing
6. [ ] Cutover

### Dependencies
| Dependency | Owner | Status |
|------------|-------|--------|
| Gemini Enterprise access | ... | ... |
| ServiceNow API credentials | ... | ... |
| ... | ... | ... |

## Key Milestones
| Milestone | Date | Status |
|-----------|------|--------|
| MVP complete | ... | ✅ |
| Migration start | ... | 📅 |
| Migration complete | End of June | 📅 |
| Full rollout | ... | 📅 |

## Risks
| Risk | Probability | Impact | Mitigation |
|------|-------------|--------|------------|
| Migration delays | Medium | Medium | Buffer in timeline |
| ServiceNow API issues | Low | High | Early testing |
| ... | ... | ... | ... |
```

---

## Phase 6: Final Review

### Objectives
1. Ensure workstream isolation (no platform/other workstream bleed)
2. Verify technical accuracy
3. Confirm completeness

### Actions

1. **Isolation Check**:
   - No Packaging Claims content
   - No Competitive Intelligence content
   - Platform references only where directly relevant

2. **Accuracy Check**:
   - ServiceNow integration details correct
   - Timeline/status current
   - Architecture diagrams accurate

3. **Completeness Check**:
   - All major topics covered
   - Open questions captured
   - Decisions documented

4. **Manifest Entry**:
   ```markdown
   ## Help Desk MVP Documents
   - helpdesk_mvp/overview.md — [word count], [source count]
   - helpdesk_mvp/architecture.md — [word count], [source count]
   - helpdesk_mvp/decisions/ — [N] ADRs
   - helpdesk_mvp/open_questions.md — [word count]
   - helpdesk_mvp/roadmap.md — [word count]
   ```

### Final Confirmation
Ask: *"Help Desk MVP documentation is complete. Any corrections before finalizing?"*

---

## Validation Prompts

### For unclear technical details:
> "The ServiceNow [integration aspect] isn't clear from the atoms. Can you provide details on [specific question]?"

### For timeline uncertainty:
> "The 'end of June' migration target is an estimate from Kaspar. Is this still the current target, or has it changed?"

### For scope ambiguity:
> "Is [feature X] in scope for the Help Desk MVP, or is it planned for a future phase?"

---

## Pre-loaded Context (from atoms)

### Known Facts
- Help desk items are 90% complete, considered safe known entities requiring only refinement
- Integrating Help Desk into Gemini Enterprise requires pausing other feature work
- Kaspar estimates Help Desk to Gemini Enterprise integration is doable by end of June
- Mobile app development is not the team's responsibility; Gemini Enterprise will handle it

### Known Decisions
- Migrate Help Desk to Gemini Enterprise
- Pause feature work during migration
- Use Gemini Enterprise native mobile UI

### Known Stakeholders
- Kaspar: Engineering lead for Help Desk/Gemini migration

---

## Output Format

```markdown
<!-- FILE: helpdesk_mvp/overview.md -->
# Help Desk MVP
...

<!-- FILE: helpdesk_mvp/architecture.md -->
# Help Desk MVP Architecture
...

<!-- FILE: helpdesk_mvp/decisions/ADR-HD-001-gemini-migration.md -->
# ADR-HD-001: Migrate Help Desk to Gemini Enterprise
...

<!-- FILE: helpdesk_mvp/open_questions.md -->
# Open Questions — Help Desk MVP
...

<!-- FILE: helpdesk_mvp/roadmap.md -->
# Help Desk MVP Roadmap
...
```

---

## Begin

Acknowledge receipt of the input files and begin Phase 1: Workstream Inventory. Present your findings and await confirmation before proceeding.
