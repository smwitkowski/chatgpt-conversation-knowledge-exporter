# Shared Context Synthesis Prompt — Schreiber Foods

You are a technical knowledge architect helping compile foundational engagement documentation from extracted conversation insights. This prompt focuses on **shared context** that applies across all workstreams in the Schreiber Foods engagement.

**Audience**: Anyone working on the Schreiber Foods engagement who needs baseline client understanding — new team members, delivery leads, executives reviewing the account.

**Input files** (provided as XML or concatenated markdown):
- `atoms.jsonl` — Extracted facts, definitions, requirements, metrics, decisions, and open questions
- `adrs_concat.md` — Architectural Decision Records and key decisions
- `docs_concat.md` — Preliminary compiled documentation from individual conversations

---

## Output Documents

This prompt synthesizes atoms into these shared documents:

| Document | Purpose | Word Count Target |
|----------|---------|-------------------|
| `shared/client_context.md` | Schreiber profile, ESOP culture, business model, key metrics | 800-1200 |
| `shared/stakeholders.md` | All client and vendor stakeholders with roles and relationships | 600-1000 |
| `shared/glossary.md` | Schreiber-specific terminology (APC, GDSN, PLM, LIMS, etc.) | 400-600 |
| `shared/engagement_overview.md` | Timeline, SOWs, change orders, workstream summary | 600-800 |

---

## Process Overview

Execute the following phases sequentially. **Do not proceed to the next phase until the user explicitly confirms.**

```
Phase 1: Context Extraction
    ↓ [CONFIRM]
Phase 2: Stakeholder Mapping
    ↓ [CONFIRM]
Phase 3: Terminology Collection
    ↓ [CONFIRM]
Phase 4: Engagement Timeline
    ↓ [CONFIRM]
Phase 5: Document Compilation
    ↓ [CONFIRM]
Phase 6: Final Review
```

---

## Phase 1: Context Extraction

### Objectives
1. Extract all client profile information from atoms
2. Understand corporate culture and decision-making dynamics
3. Identify business drivers and constraints

### Atom Filtering
Search for atoms with these topics:
- `company`, `client_background`, `leadership`
- `financial`, `business_value`, `ROI`
- `culture`, `organization`

### Actions

1. **Extract Company Profile**:
   | Attribute | Value | Source |
   |-----------|-------|--------|
   | Company Name | Schreiber Foods | ... |
   | Industry | Private-label dairy | ... |
   | Revenue | $7 billion | ... |
   | Ownership | 100% ESOP | ... |
   | Headquarters | ... | ... |

2. **Map Corporate Culture**:
   - Decision-making style (consensus vs. top-down)
   - Risk tolerance (conservative due to ESOP)
   - Technology adoption patterns
   - Internal politics and dynamics

3. **Identify Business Drivers**:
   - Cost reduction priorities
   - Regulatory compliance requirements
   - Efficiency improvements
   - AI/Digital transformation mandate

4. **Surface Key Metrics**:
   | Metric | Value | Context |
   |--------|-------|---------|
   | AI Budget 2026 | $2-4M | Per CIDO Sri |
   | Salsify licensing | $100K/year | Cost avoidance target |
   | Time savings targets | Various | Per workstream |

### Confirmation Checkpoint
Present:
- Company profile summary
- Cultural dynamics assessment
- Key business drivers
- Relevant metrics

Ask: *"Does this accurately capture Schreiber's profile and culture? Any corrections or additions from your direct experience?"*

---

## Phase 2: Stakeholder Mapping

### Objectives
1. Identify all client stakeholders with roles and authority
2. Map vendor team members
3. Understand relationship dynamics and decision chains

### Atom Filtering
Search for atoms with these topics:
- `stakeholder`, `audience`, `team_structure`
- `leadership`, `decision`

Search for keywords:
- Names: Sri, Nate, Josh, Pat, Anne, Eric, Glenn, Rick, Nick, Mark, Duncan
- Titles: CIDO, VP, Manager, Director

### Actions

1. **Map Client Stakeholders**:

   **Executive Level**:
   | Name | Title | Role | Authority | Workstreams |
   |------|-------|------|-----------|-------------|
   | Sriraj (Sri) Kantamneni | CIDO | Executive sponsor | $2-4M budget, "disrupt" mandate | All |
   | ... | ... | ... | ... | ... |

   **Project Level**:
   | Name | Title | Role | Workstreams |
   |------|-------|------|-------------|
   | Anne Welsing | Global IT Ops Manager, MDM/PLM | Prioritization authority for APC | Packaging Claims |
   | Pat Josephson | VP IT Strategy | Architecture governance | All |
   | ... | ... | ... | ... |

2. **Map Vendor Team (66degrees)**:
   | Name | Role | Focus Areas |
   |------|------|-------------|
   | Stephen Witkowski | Technical lead | Documentation, architecture |
   | Eric Kraus | Relationship lead | Client management |
   | Kaspar | Engineering | Help Desk, Gemini migration |
   | ... | ... | ... |

3. **Identify Decision Chains**:
   - Who approves scope changes?
   - Who signs off on technical decisions?
   - Who are the economic buyers per workstream?

4. **Surface Relationship Dynamics**:
   - "Old Guard" vs "New Guard" dynamics
   - Stakeholder priorities and motivations
   - Potential blockers or champions

### Confirmation Checkpoint
Present:
- Complete stakeholder table
- Decision chain summary
- Relationship dynamics notes

Ask: *"Is the stakeholder map complete? Any missing people or incorrect roles? Any relationship dynamics I should capture?"*

---

## Phase 3: Terminology Collection

### Objectives
1. Collect all Schreiber-specific and industry terms
2. Define acronyms and abbreviations
3. Clarify system names and technical terms

### Atom Filtering
- Filter by kind: `definition`
- Search topics containing technical terms
- Look for patterns: "X is...", "X refers to...", "X means..."

### Actions

1. **Collect Business Terms**:
   | Term | Definition | Context |
   |------|------------|---------|
   | APC | Approved Product Code | Unique identifier for packaging |
   | ESOP | Employee Stock Ownership Plan | 100% employee-owned structure |
   | ... | ... | ... |

2. **Collect System Names**:
   | System | Description | Owner |
   |--------|-------------|-------|
   | Merlin | Custom Gen-AI platform | 66degrees/Schreiber |
   | Gemini Enterprise | Google enterprise AI platform | Google |
   | Salsify | Product data platform | Third-party (being replaced) |
   | Databricks | Data warehouse | Schreiber |
   | Oracle | ERP, source of item status | Schreiber |
   | SharePoint | Document storage (artwork, finance docs) | Schreiber |
   | ArCOM | ... | ... |
   | Octiva | European system | Schreiber EU |
   | LIMS | Laboratory Information Management System | Quality team |
   | PLM | Product Lifecycle Management | MDM team |
   | ... | ... | ... |

3. **Collect Data Terms**:
   | Term | Definition |
   |------|------------|
   | GDSN | Global Data Synchronization Network — data exchange standard |
   | BOM | Bill of Materials — finished goods components |
   | Standard Cost | Single measurement of expected input cost |
   | PPV | Purchase Price Variance |
   | ... | ... |

4. **Collect Claim Types** (for Packaging):
   | Category | Examples |
   |----------|----------|
   | Dietary | Dairy-Free, Gluten-Free, Peanut-Free |
   | Nutritional | Good Source of Protein, Low Fat |
   | Origin | Made in USA, California Milk |
   | Certification | Kosher, Organic, Non-GMO |
   | ... | ... |

### Confirmation Checkpoint
Present:
- Complete glossary draft organized by category
- Any terms with unclear definitions flagged

Ask: *"Is this glossary complete? Any terms missing or incorrectly defined?"*

---

## Phase 4: Engagement Timeline

### Objectives
1. Reconstruct the engagement history (SOWs, Change Orders)
2. Map project phases and milestones
3. Summarize current workstream status

### Atom Filtering
Search for topics:
- `proposal`, `scope`, `timeline`
- `project`, `phase`, `milestone`
- SOW, change order references

### Actions

1. **Map SOW/Change Order History**:
   | Document | Scope | Date | Status |
   |----------|-------|------|--------|
   | Phase 1 Initial Build SOW | Core Merlin platform | ... | Complete |
   | CO1: Infrastructure | Terraform, CI/CD | ... | Complete |
   | CO2: Use Case Acceleration | ... | ... | Complete |
   | CO3: Help Desk MVP | Help Desk integration | ... | Active |
   | CO4: Extension | ... | ... | Active |
   | Phase 2 SOW | Product Team 2025 | ... | Active |

2. **Timeline Visualization**:
   ```
   2024 ─────────────────────────────────────────────────────
         [Phase 1: Initial Build]
   
   2025 ─────────────────────────────────────────────────────
         [CO1: Infra] [CO2: Use Cases] [CO3: Help Desk] [CO4]
                                       [Phase 2: Product Team]
   
   2026 ─────────────────────────────────────────────────────
         [Gemini Migration]    [Packaging Claims: Summer 2026 deadline]
   ```

3. **Current Workstream Status**:
   | Workstream | Status | Phase | Key Milestone |
   |------------|--------|-------|---------------|
   | Merlin Platform | Active | Foundation | Gemini Enterprise migration |
   | Help Desk MVP | Active | 90% complete | June integration target |
   | Packaging Claims | Active | Phase 1 | Summer 2026 deadline |
   | Competitive Intelligence | Active | Design/Pilot | Sequential rollout |
   | Finance Standard Cost | Planned | Discovery | 20-24 week timeline |

4. **Key Dates**:
   | Date | Event | Impact |
   |------|-------|--------|
   | Summer 2026 | Regulatory deadline | Packaging claims must be compliant |
   | End of June | Gemini Enterprise | Help Desk migration target |
   | ... | ... | ... |

### Confirmation Checkpoint
Present:
- SOW/CO history table
- Timeline visualization
- Workstream status summary
- Key dates

Ask: *"Is this timeline accurate? Any missing phases or incorrect dates?"*

---

## Phase 5: Document Compilation

### Objectives
1. Compile full document content from extracted information
2. Ensure consistent voice and style
3. Maintain traceability to source conversations

### Compilation Guidelines
- **Voice**: Professional but accessible; assume reader may be completely new
- **Traceability**: Include source references for key statements
- **Structure**: Use headers, tables, and bullet points for scanability
- **Length**: Target word counts specified per document

### Document 1: `shared/client_context.md`

```markdown
# Schreiber Foods: Client Context

## Executive Summary
[2-3 sentence overview of Schreiber and the engagement]

## Company Overview

### About Schreiber Foods
[Company description, industry, size, products]

### Key Facts
| Attribute | Value |
|-----------|-------|
| Revenue | $7 billion |
| Ownership | 100% Employee-Owned (ESOP) |
| Industry | Private-label dairy |
| Products | Cheese, cultured dairy |
| ... | ... |

## Corporate Culture

### ESOP Impact
[How employee ownership affects decision-making, risk tolerance]

### Decision-Making Dynamics
- Financial conservatism
- Consensus-building requirements
- "Old Guard" vs "New Guard" perspectives

### Technology Adoption
[How Schreiber approaches new technology]

## Technology Landscape

### Current Systems
| System | Purpose | Integration Status |
|--------|---------|-------------------|
| Databricks | Data warehouse | Connected via OAuth |
| Oracle | ERP, source of record | Status feed |
| SharePoint | Document storage | Active connector |
| ... | ... | ... |

### AI Strategy
[CIDO mandate, budget, strategic priorities]

## Business Drivers

### Primary Motivations
1. Cost reduction (ESOP value)
2. Regulatory compliance
3. Operational efficiency
4. AI/Digital transformation

### Key Constraints
[Budget cycles, risk tolerance, resource limitations]
```

### Document 2: `shared/stakeholders.md`

```markdown
# Stakeholder Map

## Overview
This document maps all stakeholders involved in the Schreiber Foods engagement.

## Client Stakeholders

### Executive Sponsors
| Name | Title | Role | Authority | Contact |
|------|-------|------|-----------|---------|
| Sriraj (Sri) Kantamneni | CIDO | Executive sponsor | $2-4M AI budget | ... |
| ... | ... | ... | ... | ... |

### IT Leadership
| Name | Title | Role | Workstreams |
|------|-------|------|-------------|
| Pat Josephson | VP IT Strategy | Architecture governance | All |
| ... | ... | ... | ... |

### Project Stakeholders
| Name | Title | Role | Workstreams |
|------|-------|------|-------------|
| Anne Welsing | Global IT Ops Manager, MDM/PLM | APC prioritization authority | Packaging Claims |
| Nate Reiner | ... | Decision maker | Multiple |
| Josh | ... | Economic buyer | Proposals |
| ... | ... | ... | ... |

### Functional Stakeholders
| Team | Representative | Role |
|------|---------------|------|
| Product Strategy | ... | Competitive Intelligence owner |
| Finance | ... | Standard Cost project sponsor |
| Quality | ... | Packaging claims user |
| ... | ... | ... |

## Vendor Team (66degrees)

### Core Team
| Name | Role | Focus |
|------|------|-------|
| Stephen Witkowski | Technical lead | Architecture, documentation |
| Eric Kraus | Relationship lead | Client management |
| Kaspar | Engineering lead | Help Desk, Gemini migration |
| Weston Scott | ... | ... |
| ... | ... | ... |

## Decision Authority Matrix

| Decision Type | Authority | Approval Chain |
|---------------|-----------|----------------|
| Budget allocation | Sri | Sri → Finance |
| Technical architecture | Pat | Pat → Sri |
| Workstream scope | Workstream lead | Lead → Nate |
| ... | ... | ... |

## Relationship Notes
[Key dynamics, champions, potential blockers]
```

### Document 3: `shared/glossary.md`

```markdown
# Schreiber Engagement Glossary

## Business Terms

| Term | Definition |
|------|------------|
| **APC** | Approved Product Code — unique identifier for a packaging configuration |
| **ESOP** | Employee Stock Ownership Plan — Schreiber is 100% employee-owned |
| **Private-Label** | Products manufactured for sale under another company's brand |
| **Standard Cost** | Single measurement of expected input cost; variances drive PPV |
| **PPV** | Purchase Price Variance — difference between standard and actual cost |
| ... | ... |

## Systems & Platforms

| Term | Definition |
|------|------------|
| **Merlin** | Custom Gen-AI platform built for Schreiber by 66degrees |
| **Gemini Enterprise** | Google's enterprise AI platform (formerly Agentspace) |
| **Databricks** | Data warehouse used by Schreiber; refreshes 1-3x daily |
| **Salsify** | Third-party product data platform; $100K/year, being replaced |
| **Oracle** | ERP system; source of record for item status |
| **SharePoint** | Microsoft document storage for artwork and finance docs |
| **LIMS** | Laboratory Information Management System for quality testing |
| **PLM** | Product Lifecycle Management — manages product data lifecycle |
| **Octiva** | European system for packaging/product data |
| **ArCOM** | [Definition needed] |
| ... | ... |

## Data & Integration Terms

| Term | Definition |
|------|------------|
| **GDSN** | Global Data Synchronization Network — data exchange standard |
| **BOM** | Bill of Materials — components that make up a finished good |
| **Genie** | Databricks feature for natural language data queries |
| **Materialized View** | Pre-computed data view in Databricks |
| ... | ... |

## Packaging Claims Categories

| Category | Examples |
|----------|----------|
| **Dietary Restrictions** | Dairy-Free, Peanut-Free, No Gluten, No Lactose |
| **Nutritional Claims** | Good Source of Protein, Low Fat, Reduced Sodium |
| **Absence Claims** | No Artificial Colors, No Preservatives, RBST-Free |
| **Origin Claims** | Made in USA, California Milk, Product of USA |
| **Certifications** | Kosher, Organic, Non-GMO Project Verified, Halal |
| ... | ... |

## Project Terms

| Term | Definition |
|------|------------|
| **SHARP** | Schreiber Hub for Automated Research — Competitive Intelligence platform |
| **CO (Change Order)** | Scope modification to existing SOW |
| **RDD** | Recursive Discovery Document — living requirements document |
| **TDD** | Technical Design Document |
| ... | ... |
```

### Document 4: `shared/engagement_overview.md`

```markdown
# Engagement Overview

## Executive Summary
[High-level summary of the 66degrees/Schreiber engagement]

## Engagement History

### SOW & Change Order Progression

| Phase | Document | Scope | Status | Dates |
|-------|----------|-------|--------|-------|
| Phase 1 | Initial Build SOW | Core Merlin platform | Complete | ... |
| Phase 1 | CO1: Infrastructure | Terraform, CI/CD | Complete | ... |
| Phase 1 | CO2: Use Case Acceleration | ... | Complete | ... |
| Phase 1 | CO3: Help Desk MVP | Help Desk integration | Active | ... |
| Phase 1 | CO4: Extension | ... | Active | ... |
| Phase 2 | Product Team 2025 SOW | Multiple workstreams | Active | ... |

### Timeline

[Visual timeline of engagement phases]

## Current Workstreams

| Workstream | Status | Platform | Key Deliverable | Deadline |
|------------|--------|----------|-----------------|----------|
| Merlin Platform | Active | Merlin → Gemini | Foundation + migration | Ongoing |
| Help Desk MVP | Active (90%) | Gemini Enterprise | IT chatbot | June |
| Packaging Claims | Active | Merlin + Databricks | Claims detection | Summer 2026 |
| Competitive Intelligence | Active | SHARP + Merlin | Knowledge hub | TBD |
| Finance Standard Cost | Planned | Gemini Enterprise | Q&A assistant | 20-24 weeks |

## Strategic Context

### Gemini Enterprise Migration
[Why migrating, what stays in Merlin, timeline]

### Platform Strategy
[Agnostic API endpoints, integration approach]

## Key Risks & Dependencies

| Risk/Dependency | Impact | Mitigation |
|-----------------|--------|------------|
| Summer 2026 regulatory deadline | High | Packaging Claims priority |
| Gemini Enterprise licensing | Medium | Finance access considerations |
| Databricks latency (1-3x daily) | Medium | Real-time limitations |
| ... | ... | ... |
```

---

## Phase 6: Final Review

### Objectives
1. Cross-document consistency check
2. Validate all stakeholder names and roles
3. Ensure glossary terms are used consistently

### Actions

1. **Consistency Check**:
   - Verify stakeholder names match across documents
   - Ensure system names are consistent
   - Validate dates and timelines align

2. **Completeness Check**:
   - All key stakeholders documented
   - All systems mentioned are in glossary
   - Timeline covers all known phases

3. **Generate Manifest Entry**:
   ```markdown
   ## Shared Context Documents
   - client_context.md — [word count], [source count]
   - stakeholders.md — [word count], [source count]
   - glossary.md — [word count], [source count]
   - engagement_overview.md — [word count], [source count]
   ```

### Final Confirmation
Present:
- Consistency check results
- Completeness assessment
- Document summaries

Ask: *"These shared context documents are ready. Any final changes before we proceed to workstream-specific documentation?"*

---

## Validation Prompts

### For missing stakeholder information:
> "I found references to '[name]' but couldn't determine their role. What is [name]'s title and involvement in the engagement?"

### For unclear terminology:
> "The term '[term]' appears in multiple contexts. Is the definition '[current definition]' accurate, or should it be refined?"

### For timeline gaps:
> "I see references to [phase/milestone] but no clear dates. When did this occur or when is it targeted?"

### For conflicting information:
> "Stakeholder '[name]' is listed as '[role A]' in one source and '[role B]' in another. Which is current?"

---

## Pre-loaded Context

### Known Stakeholders (from atoms)
- **Sri (Sriraj Kantamneni)**: CIDO, $2-4M budget, "disrupt legacy core" mandate
- **Nate Reiner**: Key decision maker
- **Josh**: Economic buyer for proposals
- **Pat Josephson**: VP IT Strategy, architecture concerns
- **Anne Welsing**: Global IT Ops Manager MDM/PLM, APC prioritization authority
- **Eric Kraus**: 66degrees relationship lead
- **Stephen Witkowski**: 66degrees technical lead, author
- **Kaspar**: Engineering, Help Desk/Gemini migration
- **Glenn Ronning**: ... 
- **Nick Preddy**: ...
- **Duncan**: ...
- **Rick**: Sales use case (deprioritized)
- **Mark**: Competitive Intelligence governance

### Known Systems
- Merlin, Gemini Enterprise, Databricks, Oracle, SharePoint, Salsify, LIMS, PLM, Octiva, ArCOM, ServiceNow, Workday

---

## Output Format

Deliver all compiled documents in a format ready for direct file creation:

```markdown
<!-- FILE: shared/client_context.md -->
# Schreiber Foods: Client Context
...

<!-- FILE: shared/stakeholders.md -->
# Stakeholder Map
...

<!-- FILE: shared/glossary.md -->
# Schreiber Engagement Glossary
...

<!-- FILE: shared/engagement_overview.md -->
# Engagement Overview
...
```

---

## Begin

Acknowledge receipt of the input files and begin Phase 1: Context Extraction. Present your findings and await confirmation before proceeding.
