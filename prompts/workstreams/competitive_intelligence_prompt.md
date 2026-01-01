# Workstream Synthesis Prompt — Competitive Intelligence (SHARP)

You are a technical knowledge architect helping compile workstream documentation for the **Competitive Intelligence** project, codenamed **SHARP** (Schreiber Hub for Automated Research). This prompt focuses on building a competitor knowledge platform for the cheese and cultured dairy industry.

**Audience**: Engineers and delivery team working on the CI platform, Product Strategy stakeholders at Schreiber, and new team members onboarding to this workstream.

**Input files** (provided as XML or concatenated markdown):
- `atoms.jsonl` — Extracted facts, definitions, requirements, metrics, decisions, and open questions
- `adrs_concat.md` — Architectural Decision Records and key decisions
- `docs_concat.md` — Preliminary compiled documentation from individual conversations

---

## Workstream Context

| Attribute | Value |
|-----------|-------|
| **Workstream** | Competitive Intelligence (SHARP) |
| **Full Name** | Schreiber Hub for Automated Research |
| **Status** | Active — Design/Pilot phase (Tier 2 prototype) |
| **Key Stakeholders** | Product Strategy team, Pat, Mark |
| **Platform** | Standalone platform + Merlin/Gemini Enterprise integration |
| **Target Users** | Executive staff, Finance, Sales, Risk Management, Product Strategy |
| **Scope** | ~90 competitors in cheese and cultured dairy |
| **Governance Note** | Pat and Mark are adamant about NOT trying to do everything at once |

---

## Output Documents

This prompt synthesizes atoms into:

| Document | Purpose | Word Count Target |
|----------|---------|-------------------|
| `competitive_intelligence/overview.md` | SHARP vision, business problem, current state, value proposition | 800-1000 |
| `competitive_intelligence/architecture.md` | Ingestion pipelines, knowledge graph, UI, integrations | 1000-1400 |
| `competitive_intelligence/data_model.md` | Competitor schema, fact model, validation flow, battle cards | 700-900 |
| `competitive_intelligence/decisions/` | CI-specific ADRs | Variable |
| `competitive_intelligence/open_questions.md` | Outstanding items | 300-500 |
| `competitive_intelligence/roadmap.md` | Phased approach, sequential rollout | 400-600 |

---

## Process Overview

Execute the following phases sequentially. **Do not proceed to the next phase until the user explicitly confirms.**

```
Phase 1: Business Context & Vision
    ↓ [CONFIRM]
Phase 2: Architecture Design
    ↓ [CONFIRM]
Phase 3: Data Model Definition
    ↓ [CONFIRM]
Phase 4: Decision Extraction
    ↓ [CONFIRM]
Phase 5: Document Compilation
    ↓ [CONFIRM]
Phase 6: Final Review
```

---

## Atom Filtering Strategy

### Include (Competitive Intelligence Specific)
Focus on atoms with topics:
- `competitive-intelligence`, `competitive_intelligence`, `comp-intel`
- `SHARP`, `competitors`
- `knowledge_graph`, `knowledge_hub`
- `battle_cards`, `battlecards`
- `product_strategy`

Search for keywords:
- "competitive intelligence"
- "SHARP"
- "competitors", "competition"
- "Product Strategy"
- "battle cards"
- "RSS", "web crawling", "ingestion"
- "knowledge graph", "knowledge hub"
- "Pat", "Mark" (governance)
- "cheese", "dairy" (industry context)
- "90 competitors"

### Exclude
Filter OUT atoms specifically about:
- Help Desk / ServiceNow
- Packaging Claims / Vision+LLM / claims detection
- Finance Standard Cost
- Platform-level decisions (unless directly impacting CI)

---

## Phase 1: Business Context & Vision

### Objectives
1. Understand the current competitive intelligence problem
2. Articulate the SHARP vision
3. Identify stakeholders and users
4. Define explicit boundaries

### Actions

1. **Extract Current State**:
   | Aspect | Current State | Pain Point |
   |--------|---------------|------------|
   | Process | Semi-data driven | Relies on gut instinct, hearsay |
   | Research | Manual Google searches, bespoke inquiries | No systematic approach |
   | System of Record | None | Fragmented sources |
   | Sources | Press releases, social media, paywalled newspapers | Hard to access, not centralized |
   | Team | One product manager per category | Focus on day-to-day, not deep CI |
   | Intellectual Assets | No automated ingestion or updating | Stale, incomplete |

2. **Extract SHARP Vision**:
   > A living Competitive Intelligence Knowledge Hub that:
   > - Continuously ingests external signals and internal artifacts
   > - Extracts facts into a structured model
   > - Detects deltas (changes over time)
   > - Exposes knowledge via Merlin Q&A and battle cards

3. **Identify Stakeholders**:
   | Stakeholder | Role | Primary Use Case |
   |-------------|------|------------------|
   | Executive staff | Strategic decisions | Market trends, competitor moves |
   | Finance | M&A, risk assessment | Competitor financials |
   | Sales | Competitive positioning | Battle cards, objection handling |
   | Risk Management | Threat monitoring | Facility changes, market shifts |
   | Product Strategy | Category insights | Product launches, innovations |

4. **Define Scope**:
   
   **In Scope**:
   | Item | Details |
   |------|---------|
   | Competitor count | ~90 competitors |
   | Categories | Cheese, cultured dairy |
   | Public sources | RSS, web crawling, press releases, social media (public) |
   | Internal sources | Customer intel, internal documents |
   | Manual ingestion | Email, link, PDF submission |
   | UI | Admin views, user views, Merlin/Gemini integration |
   
   **Explicitly Out of Scope**:
   | Item | Reason |
   |------|--------|
   | **Paywall content** | Legal/access constraints |
   | **Satellite imagery** | Not needed for this use case |
   | **CRM replacement** | Different system |
   | **Autonomous decision-making** | Human-in-the-loop required |

5. **Extract Governance Mandate**:
   > **"Pat and Mark are adamant about NOT trying to do everything all at once"**
   > - Proceed sequentially
   > - Build incrementally
   > - Validate each phase before expanding

6. **Client Background**:
   | Attribute | Detail |
   |-----------|--------|
   | Industry position | Cheese and product processor |
   | CI team location | Within Product Strategy |
   | Stakeholder groups | Executive, Finance, Sales, Risk |

### Confirmation Checkpoint
Present:
- Current state pain points
- SHARP vision statement
- Stakeholder map with use cases
- Scope table (in/out)
- Governance mandate

Ask: *"Does this accurately capture the Competitive Intelligence vision and scope? Any corrections or additions?"*

---

## Phase 2: Architecture Design

### Objectives
1. Design the data ingestion architecture
2. Define the knowledge repository structure
3. Specify user interfaces and integrations
4. Map the validation flow

### Actions

1. **High-Level Architecture**:
   ```
   ┌─────────────────────────────────────────────────────────────────────┐
   │                         Data Ingestion                              │
   └─────────────────────────────────────────────────────────────────────┘
   
   ┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐
   │  Public Sources │     │ Internal Sources│     │  Manual Funnel  │
   │  - RSS feeds    │     │ - Customer intel│     │  - Email        │
   │  - Web crawling │     │ - Internal docs │     │  - Link submit  │
   │  - Press releases│    │                 │     │  - PDF upload   │
   │  - Social media │     │                 │     │                 │
   └────────┬────────┘     └────────┬────────┘     └────────┬────────┘
            │                       │                       │
            └───────────────────────┼───────────────────────┘
                                    │
                                    ▼
   ┌─────────────────────────────────────────────────────────────────────┐
   │                    Fact Extraction Pipeline                         │
   │         (NLP/LLM processing → Structured facts → Delta detection)   │
   └─────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
   ┌─────────────────────────────────────────────────────────────────────┐
   │                  Human Validation Queue                             │
   │            (Review, conflict resolution, approval)                  │
   └─────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
   ┌─────────────────────────────────────────────────────────────────────┐
   │                    Knowledge Repository                             │
   │        (Structured repository — knowledge graph or similar)         │
   └─────────────────────────────────────────────────────────────────────┘
                                    │
            ┌───────────────────────┼───────────────────────┐
            ▼                       ▼                       ▼
   ┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐
   │  SHARP Web UI   │     │ Merlin/Gemini   │     │  Battle Cards   │
   │  - Admin views  │     │  Integration    │     │  - Per competitor│
   │  - User views   │     │  (Q&A endpoint) │     │  - Auto-generated│
   │  - Audit trail  │     │                 │     │                 │
   └─────────────────┘     └─────────────────┘     └─────────────────┘
   ```

2. **Data Ingestion Components**:
   | Source Type | Technology | Frequency | Notes |
   |-------------|------------|-----------|-------|
   | RSS feeds | RSS parser | Real-time/hourly | Public sources |
   | Web crawling | Web crawler service | Scheduled | Respect robots.txt |
   | Press releases | Feed/scrape | Event-based | Company announcements |
   | Social media | API (public) | Scheduled | Twitter, LinkedIn public |
   | Customer intel | Manual funnel | On-demand | Internal submissions |
   | Internal docs | Document ingestion | On-demand | PDF, Word, etc. |
   | Manual links | URL submission | On-demand | Employee-submitted |

3. **Knowledge Repository**:
   > "Backend storage will be a structured repository (knowledge graph or similar) with specific architecture design left to the delivery team"
   
   | Option | Pros | Cons |
   |--------|------|------|
   | Knowledge Graph (Neo4j, etc.) | Rich relationships, query flexibility | Complexity |
   | Vector DB + Structured DB | Semantic search + structured data | Two systems |
   | Unified Platform (Vertex AI?) | Integration with GCP | Vendor lock-in |
   
   **Decision**: Architecture left to delivery team

4. **User Interfaces**:
   
   **Admin Views**:
   | View | Purpose |
   |------|---------|
   | Review Queue | Pending facts for validation |
   | Conflict Resolution | Contradictory facts |
   | Audit Trail | Change history |
   | Source Management | Configure feeds/crawlers |
   
   **User Views**:
   | View | Purpose |
   |------|---------|
   | Competitor Profiles | Per-competitor detail pages |
   | Battle Cards | Sales-ready competitor summaries |
   | Change Digest | Recent changes, alerts |
   | Search | Full-text search across facts |

5. **Merlin/Gemini Integration**:
   | Aspect | Detail |
   |--------|--------|
   | Integration Type | Custom agent/endpoint built by 66degrees |
   | Query Endpoint | For validated competitive intel |
   | Platform | Merlin now, Gemini Enterprise future |
   | Access | Internal Schreiber users only |

6. **Validation Flow**:
   ```
   Raw Source → Extraction → Pending Queue → Human Review → Validated Fact
                                                  ↓
                                          Conflict? → Resolution
                                                  ↓
                                          Approved → Knowledge Base
   ```
   
   > Facts must be validated before becoming authoritative. Not autonomous decision-making.

7. **Monitoring Requirements**:
   > "Competitive Intelligence monitoring requirements are lighter touch as the tool is internal and not customer-facing"

### Confirmation Checkpoint
Present:
- Architecture diagram
- Ingestion components table
- Knowledge repository options
- UI views (admin/user)
- Integration approach
- Validation flow

Ask: *"Is this architecture aligned with expectations? Any components missing or over-specified?"*

---

## Phase 3: Data Model Definition

### Objectives
1. Define entity types for competitors and related objects
2. Specify the fact model
3. Design battle card structure
4. Clarify data dimensions

### Actions

1. **Entity Types**:
   
   **Competitor**:
   | Attribute | Type | Description |
   |-----------|------|-------------|
   | id | String | Unique identifier |
   | name | String | Company name |
   | category | Enum | Cheese, Cultured Dairy, Both |
   | status | Enum | Active, Inactive, Acquired |
   | headquarters | String | Location |
   | website | URL | Primary website |
   | ... | ... | ... |
   
   **Product**:
   | Attribute | Type | Description |
   |-----------|------|-------------|
   | id | String | Unique identifier |
   | competitor_id | Reference | Parent competitor |
   | name | String | Product name |
   | category | String | Product category |
   | launch_date | Date | When launched |
   | ... | ... | ... |
   
   **Facility**:
   | Attribute | Type | Description |
   |-----------|------|-------------|
   | id | String | Unique identifier |
   | competitor_id | Reference | Parent competitor |
   | location | String | City, State/Country |
   | type | Enum | Manufacturing, Distribution, HQ |
   | capacity | String | If known |
   | ... | ... | ... |
   
   **Leadership**:
   | Attribute | Type | Description |
   |-----------|------|-------------|
   | id | String | Unique identifier |
   | competitor_id | Reference | Parent competitor |
   | name | String | Person name |
   | title | String | Current role |
   | start_date | Date | When started |
   | ... | ... | ... |

2. **Fact Model**:
   | Attribute | Type | Description |
   |-----------|------|-------------|
   | id | String | Unique identifier |
   | statement | String | The fact statement |
   | entity_type | Enum | Competitor, Product, Facility, Leadership |
   | entity_id | Reference | Related entity |
   | source_url | URL | Where fact was found |
   | source_type | Enum | RSS, Web, Internal, Manual |
   | extracted_at | Timestamp | When extracted |
   | validated_at | Timestamp | When approved |
   | validated_by | String | Approver |
   | confidence | Float | Extraction confidence |
   | status | Enum | Pending, Validated, Rejected, Superseded |

3. **Data Dimensions** (from atoms):
   | Level | Rigidity | Examples |
   |-------|----------|----------|
   | **Top-Level (Rigid)** | Stable | Competitors, Products, Facilities, Leadership |
   | **Lower-Level (Evolving)** | Dynamic | News, events, market moves, product changes |

4. **Battle Card Structure**:
   ```markdown
   # [Competitor Name] — Battle Card
   
   ## Quick Facts
   - **Founded**: [Year]
   - **Headquarters**: [Location]
   - **Revenue**: [If known]
   - **Key Products**: [List]
   
   ## Strengths
   - [Strength 1]
   - [Strength 2]
   
   ## Weaknesses
   - [Weakness 1]
   - [Weakness 2]
   
   ## Key Products
   | Product | Category | Positioning |
   |---------|----------|-------------|
   | ... | ... | ... |
   
   ## Recent News
   - [Date]: [Headline]
   - ...
   
   ## Talking Points
   - How we win against them: [Points]
   - Common objections: [Objections]
   
   ## Facilities
   | Location | Type | Notes |
   |----------|------|-------|
   | ... | ... | ... |
   
   ---
   *Last updated: [Timestamp]*
   *Sources: [Count] validated facts*
   ```

5. **Conflict Resolution Model**:
   | Scenario | Resolution Approach |
   |----------|---------------------|
   | Contradictory facts | Human review, choose authoritative |
   | Outdated fact | Mark superseded, keep history |
   | Source disagreement | Weight by source reliability |
   | Ambiguous entity | Manual entity resolution |

### Confirmation Checkpoint
Present:
- Entity type definitions
- Fact model structure
- Data dimensions (rigid vs evolving)
- Battle card template
- Conflict resolution approach

Ask: *"Is this data model appropriate? Any missing entities or attributes?"*

---

## Phase 4: Decision Extraction

### Objectives
1. Extract CI-specific decisions
2. Highlight governance decisions
3. Document integration decisions

### Actions

1. **Identify CI ADRs**:
   | Decision | Topic | Status | Key Point |
   |----------|-------|--------|-----------|
   | "Use Merlin as primary UI for querying CI database" | ui_ux | Active | Chatbot interface |
   | "Do not attempt all CI use cases at once; proceed sequentially" | scope | **Active** | Pat/Mark mandate |
   | "Build CI as agnostic API endpoint" | architecture | Active | Platform flexibility |
   | "Structured repository (knowledge graph or similar)" | architecture | Active | Flexible implementation |
   | "Lighter touch monitoring (internal tool)" | operations | Active | Lower SLA than customer-facing |
   | "Human validation before facts become authoritative" | process | Active | Not autonomous |
   | "Paywall content explicitly out of scope" | scope | Active | Legal/access |
   | "CRM replacement out of scope" | scope | Active | Different system |

2. **Document Key ADRs**:
   
   ```markdown
   # ADR-CI-001: Sequential Rollout, Not All at Once
   
   **Status**: Active
   **Date**: [Date from atoms]
   **Topic**: Scope / Governance
   
   ## Context
   The Competitive Intelligence platform has many potential use cases: competitor 
   monitoring, battle cards, executive briefings, M&A analysis, etc. There is 
   pressure to deliver value quickly.
   
   ## Decision
   Do not attempt to build all Competitive Intelligence use cases at once. 
   Proceed sequentially, validating each phase before expanding.
   
   ## Rationale
   - Pat and Mark are adamant about this approach
   - Reduces risk of scope creep
   - Allows learning and iteration
   - Validates value before major investment
   
   ## Alternatives Considered
   - **Big bang**: Build all features at once — Rejected (too risky, too complex)
   - **Feature prioritization only**: Prioritize but build in parallel — Rejected (still too complex)
   
   ## Consequences
   - Slower initial rollout
   - Clearer success criteria per phase
   - Ability to pivot based on learnings
   - Strong governance alignment
   
   ## Evidence
   - "Pat and Mark are adamant about NOT trying to do everything all at once"
   ```

3. **Governance Decisions**:
   | Decision | Enforced By | Implication |
   |----------|-------------|-------------|
   | Sequential rollout | Pat, Mark | Phase gates required |
   | Human validation | Architecture | No autonomous fact publication |
   | Agnostic API | Architecture | Platform-independent design |

### Confirmation Checkpoint
Present:
- List of CI ADRs
- Governance decisions highlighted
- Sample detailed ADR

Ask: *"Are these the correct Competitive Intelligence decisions? Any missing or incorrect?"*

---

## Phase 5: Document Compilation

### Objectives
1. Compile comprehensive documentation
2. Emphasize governance constraints
3. Provide actionable architecture guidance

### Compilation Guidelines
- **Voice**: Technical with strategic context
- **Governance**: Emphasize Pat/Mark mandate throughout
- **Flexibility**: Note where decisions are left to delivery team
- **Traceability**: Reference sources

### Generate Full Documents:

1. **`competitive_intelligence/overview.md`** — Full business context, vision, stakeholders
2. **`competitive_intelligence/architecture.md`** — Complete architecture with diagrams
3. **`competitive_intelligence/data_model.md`** — Entity definitions, fact model, battle cards
4. **`competitive_intelligence/decisions/`** — All CI-specific ADRs
5. **`competitive_intelligence/open_questions.md`** — Technical and scope questions
6. **`competitive_intelligence/roadmap.md`** — Phased approach with governance gates

### Document 6: `competitive_intelligence/roadmap.md`
```markdown
# Competitive Intelligence Roadmap

## Governance Mandate
> **"Pat and Mark are adamant about NOT trying to do everything all at once"**
> 
> Proceed sequentially. Validate each phase before expanding.

## Phases

| Phase | Scope | Validation Gate | Status |
|-------|-------|-----------------|--------|
| **Discovery** | Requirements, data sources, architecture options | Stakeholder approval | Complete |
| **Pilot** | Core ingestion, subset of competitors, basic UI | MVP demo, user feedback | In Progress |
| **MVP** | Full competitor coverage, battle cards, Merlin integration | Production readiness | Planned |
| **Expansion** | Additional sources, advanced analytics | Value realization | Future |

## Phase 1: Pilot
| Deliverable | Description | Status |
|-------------|-------------|--------|
| Ingestion pipeline | RSS + manual for 10-20 competitors | ... |
| Basic UI | Competitor profiles, fact list | ... |
| Validation workflow | Manual approval queue | ... |

## Phase 2: MVP
| Deliverable | Description | Status |
|-------------|-------------|--------|
| Full competitor coverage | ~90 competitors | ... |
| Battle cards | Auto-generated per competitor | ... |
| Merlin integration | Q&A endpoint | ... |
| Change digest | Recent updates | ... |

## Phase 3: Expansion
| Deliverable | Description | Status |
|-------------|-------------|--------|
| Additional sources | Web crawling expansion | ... |
| Advanced analytics | Trend detection | ... |
| Gemini Enterprise | Migration from Merlin | ... |

## Tier Classification
> Competitive Intelligence platform is a **Tier 2 prototype/pilot project**

## Risks
| Risk | Probability | Impact | Mitigation |
|------|-------------|--------|------------|
| Scope creep | High | High | Strict phase gates, Pat/Mark review |
| Data quality | Medium | High | Human validation, source weighting |
| Adoption | Medium | Medium | Stakeholder engagement, training |
```

---

## Phase 6: Final Review

### Objectives
1. Verify governance mandate is prominent
2. Confirm scope boundaries are clear
3. Ensure architectural flexibility preserved

### Actions

1. **Governance Check**:
   - "Sequential" mandate in overview AND roadmap
   - Pat/Mark referenced as governance owners

2. **Scope Check**:
   - Paywall, CRM, satellite explicitly out of scope
   - ~90 competitors specified

3. **Flexibility Check**:
   - Knowledge graph "or similar" phrasing preserved
   - Delivery team has implementation authority

4. **Manifest Entry**:
   ```markdown
   ## Competitive Intelligence Documents
   - competitive_intelligence/overview.md — [word count], [source count]
   - competitive_intelligence/architecture.md — [word count], [source count]
   - competitive_intelligence/data_model.md — [word count], [source count]
   - competitive_intelligence/decisions/ — [N] ADRs
   - competitive_intelligence/open_questions.md — [word count]
   - competitive_intelligence/roadmap.md — [word count]
   ```

### Final Confirmation
Ask: *"Competitive Intelligence documentation is complete. Any corrections before finalizing?"*

---

## Pre-loaded Context (from atoms)

### Key Vision Statements
- "A living Competitive Intelligence Knowledge Hub that continuously ingests external signals and internal artifacts, extracts facts into a structured model, detects deltas, and exposes knowledge via Merlin Q&A and battle cards"
- "Competitive Intelligence currently lacks a single source of truth"

### Key Governance
- "Pat and Mark are adamant about NOT trying to do everything all at once"
- "Do not attempt to build all Competitive Intelligence use cases at once; proceed sequentially"
- "Tier 2 prototype/pilot project"

### Key Decisions
- Use Merlin as primary UI
- Build as agnostic API endpoint
- Structured repository (knowledge graph or similar)
- Lighter monitoring (internal tool)

### Explicit Out of Scope
- Paywall content
- Satellite imagery
- CRM replacement
- Autonomous decision-making

### Stakeholders
- Product Strategy team (primary users)
- Pat, Mark (governance)
- Executive, Finance, Sales, Risk (consumers)

---

## Output Format

```markdown
<!-- FILE: competitive_intelligence/overview.md -->
# Competitive Intelligence (SHARP)
...

<!-- FILE: competitive_intelligence/architecture.md -->
# Competitive Intelligence Architecture
...

<!-- FILE: competitive_intelligence/data_model.md -->
# Competitive Intelligence Data Model
...

<!-- FILE: competitive_intelligence/decisions/ADR-CI-001-sequential-rollout.md -->
# ADR-CI-001: Sequential Rollout, Not All at Once
...

<!-- FILE: competitive_intelligence/open_questions.md -->
# Open Questions — Competitive Intelligence
...

<!-- FILE: competitive_intelligence/roadmap.md -->
# Competitive Intelligence Roadmap
...
```

---

## Begin

Acknowledge receipt of the input files and begin Phase 1: Business Context & Vision. Present your findings and await confirmation before proceeding.
