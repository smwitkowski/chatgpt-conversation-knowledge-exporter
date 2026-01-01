# Workstream Synthesis Prompt — Finance Standard Cost

You are a technical knowledge architect helping compile workstream documentation for the **Finance Standard Cost** project. This prompt focuses on a Gemini Enterprise-based Q&A assistant for the Finance team's Standard Cost documentation.

**Audience**: Engineers working on the Gemini Enterprise implementation, Finance stakeholders at Schreiber, and new team members onboarding to this workstream.

**Input files** (provided as XML or concatenated markdown):
- `atoms.jsonl` — Extracted facts, definitions, requirements, metrics, decisions, and open questions
- `adrs_concat.md` — Architectural Decision Records and key decisions
- `docs_concat.md` — Preliminary compiled documentation from individual conversations

---

## Workstream Context

| Attribute | Value |
|-----------|-------|
| **Workstream** | Finance Standard Cost Documentation Assistant |
| **Status** | Planned |
| **Platform** | **Gemini Enterprise** (NOT Merlin) |
| **Key Stakeholders** | Finance team |
| **Target Users** | Finance analysts, plant support staff (~30 users) |
| **Content Scope** | ~200 SharePoint documents (US Standard Cost only) |
| **Timeline** | 20-24 weeks (reduced from 26) |
| **Business Value** | ~$100K over 3 years (360 hrs/year savings) |

---

## Output Documents

This prompt synthesizes atoms into:

| Document | Purpose | Word Count Target |
|----------|---------|-------------------|
| `finance_standard_cost/overview.md` | Business problem, value proposition, users, scope | 600-800 |
| `finance_standard_cost/architecture.md` | Gemini Enterprise RAG approach, SharePoint integration | 600-800 |
| `finance_standard_cost/decisions/` | Finance-specific ADRs | Variable |
| `finance_standard_cost/open_questions.md` | Outstanding items | 200-300 |
| `finance_standard_cost/roadmap.md` | Timeline, milestones, dependencies | 300-400 |

---

## Process Overview

Execute the following phases sequentially. **Do not proceed to the next phase until the user explicitly confirms.**

```
Phase 1: Business Context
    ↓ [CONFIRM]
Phase 2: Architecture Definition
    ↓ [CONFIRM]
Phase 3: Decision Extraction
    ↓ [CONFIRM]
Phase 4: Document Compilation
    ↓ [CONFIRM]
Phase 5: Final Review
```

---

## ⚠️ Platform Distinction

**IMPORTANT**: This workstream uses **Gemini Enterprise directly**, NOT the custom Merlin platform.

| Aspect | This Workstream | Other Workstreams |
|--------|-----------------|-------------------|
| Platform | Gemini Enterprise | Merlin (or migrating to Gemini) |
| Architecture | Native Gemini RAG | Custom Merlin workflows |
| Decisions | Gemini-specific | Merlin + Gemini |
| Integration | Direct SharePoint | Merlin connectors |

Platform-level Merlin decisions **do NOT apply** to this workstream except where Gemini Enterprise integration is relevant.

---

## Atom Filtering Strategy

### Include (Finance Standard Cost Specific)
Focus on atoms with topics:
- `finance`, `standard_cost`, `standard cost`
- `use-case` (finance-related)
- `scope` (finance project)

Search for keywords:
- "Standard Cost"
- "Finance" (team/project context)
- "SharePoint" (finance docs)
- "Workday" (contrast decision)
- "Gemini Enterprise" (platform)
- "200 documents"
- "30 users"
- "Oracle" (standard cost context)
- "partner" (finance partner experience)

### Exclude
Filter OUT atoms specifically about:
- Help Desk / ServiceNow
- Packaging Claims / Vision+LLM
- Competitive Intelligence / SHARP
- Merlin platform architecture

---

## Phase 1: Business Context

### Objectives
1. Understand the Finance team's documentation problem
2. Quantify the value proposition
3. Define strict scope boundaries
4. Identify users and stakeholders

### Actions

1. **Extract Business Problem**:
   | Aspect | Current State |
   |--------|---------------|
   | Documentation | ~200 documents in SharePoint |
   | Document types | Word, Excel, PowerPoint |
   | Document sizes | 1-40 pages each |
   | Content | Text and screenshots |
   | Topics | Process docs, templates, Oracle operations, standard cost logic |
   | Users | ~30 regular users |
   | User profile | Finance analysts, plant support, 1st/2nd year employees (high turnover) |
   | Pain point | Time spent answering repetitive questions |
   | Current access | Manual search through documents |

2. **Define Standard Cost Concept**:
   > **Standard Cost**: A single measurement of what the input cost should be, where any actual cost drives a purchase price variance (PPV).

3. **Quantify Business Value**:
   | Metric | Value | Notes |
   |--------|-------|-------|
   | Annual time savings | **360 hours/year** | Breakdown below |
   | - Question answering | 250 hours | Repetitive queries |
   | - Retraining | 20 hours | New employee onboarding |
   | - Mistake correction | 50 hours | Errors from wrong info |
   | User base | ~30 people | Regular users |
   | 3-year value | ~$100K | ROI estimate |

4. **Identify Decision Context**:
   The project was chosen over creating Workday trainings:
   > "Select Merlin as a chatbot solution for Standard Cost Documentation over creating Workday trainings"
   
   **Rationale**:
   - Chatbot provides easier navigation
   - Quicker responses than training search
   - Eliminates need to sift through data manually

5. **Define Strict Scope**:
   | In Scope | Out of Scope |
   |----------|--------------|
   | US Standard Cost documentation | International documentation |
   | ~200 SharePoint documents | Other finance topics |
   | Q&A over existing content | Content creation |
   | Gemini Enterprise platform | Custom Merlin development |
   | Mobile (via Gemini responsive) | Custom mobile app |

   > **"Limit initial scope to Standard Cost information only"** — explicitly confirmed

6. **Map Stakeholders**:
   | Stakeholder | Role | Interest |
   |-------------|------|----------|
   | Finance team lead | Project sponsor | Partner experience improvement |
   | Finance analysts | Primary users | Faster answers |
   | Plant support staff | Users | Process guidance |
   | New employees (1st/2nd year) | Heavy users | Onboarding support |

### Confirmation Checkpoint
Present:
- Business problem summary
- Value quantification
- Scope boundaries
- Stakeholder map

Ask: *"Does this accurately capture the Finance Standard Cost project context? Any corrections?"*

---

## Phase 2: Architecture Definition

### Objectives
1. Define the Gemini Enterprise RAG architecture
2. Specify SharePoint integration approach
3. Address access and licensing considerations

### Actions

1. **High-Level Architecture**:
   ```
   ┌─────────────────────────────────────────────────────────────────────┐
   │                    Gemini Enterprise Platform                       │
   └─────────────────────────────────────────────────────────────────────┘
   
   ┌─────────────────┐                        ┌─────────────────────────┐
   │   SharePoint    │ ─────────────────────▶ │  Gemini Enterprise      │
   │  (~200 docs)    │    Document Sync       │  RAG Pipeline           │
   │  - Word         │                        │  - Indexing             │
   │  - Excel        │                        │  - Embedding            │
   │  - PowerPoint   │                        │  - Retrieval            │
   └─────────────────┘                        └───────────┬─────────────┘
                                                          │
                                                          ▼
                                              ┌─────────────────────────┐
                                              │  Gemini Chat Interface  │
                                              │  - Web (desktop)        │
                                              │  - Mobile (responsive)  │
                                              └─────────────────────────┘
                                                          │
                                                          ▼
                                              ┌─────────────────────────┐
                                              │       Finance Users     │
                                              │  (~30 analysts, staff)  │
                                              └─────────────────────────┘
   ```

2. **Why Gemini Enterprise (Not Merlin)**:
   | Consideration | Gemini Enterprise | Custom Merlin |
   |---------------|-------------------|---------------|
   | Development effort | Low (native RAG) | High (custom build) |
   | Mobile support | Native responsive | Would need custom |
   | Existing licenses | Leverage enterprise license | Additional cost |
   | Maintenance | Google-managed | Team-managed |
   | Time to deploy | Faster | Slower |

   > **Decision**: "Use the mobile-responsive Gemini Enterprise interface instead of developing a separate mobile application"

3. **SharePoint Integration**:
   | Aspect | Detail |
   |--------|--------|
   | Connector | Gemini Enterprise SharePoint connector (or via GCS sync) |
   | Document formats | Word, Excel, PowerPoint |
   | Content types | Text and screenshots |
   | Sync frequency | TBD (daily? real-time?) |
   | Access control | Inherit from SharePoint permissions? |

4. **Document Processing Considerations**:
   | Content Type | Processing Notes |
   |--------------|------------------|
   | Text | Standard extraction |
   | Screenshots | OCR or Vision processing needed |
   | Excel formulas | May need special handling |
   | PowerPoint | Slide-by-slide processing |

5. **Access Considerations**:
   | Consideration | Detail |
   |---------------|--------|
   | User licenses | Gemini Enterprise seats for ~30 users |
   | Shared computers | Plant computers may have licensing challenges |
   | Authentication | Google/Schreiber SSO? |

   > **Note**: "Shared plant computers" raises licensing questions

6. **Migration Relevance**:
   This project benefits from the broader **Gemini Enterprise migration** decision:
   > "Move to Gemini Enterprise should be used as a strategic decision point to pause development on capabilities that Gemini Enterprise already provides (e.g., memory)"

### Confirmation Checkpoint
Present:
- Architecture diagram
- Gemini vs Merlin rationale
- SharePoint integration approach
- Processing considerations
- Access/licensing notes

Ask: *"Is this architecture aligned with expectations? Any technical corrections?"*

---

## Phase 3: Decision Extraction

### Objectives
1. Extract Finance-specific decisions
2. Separate from platform decisions
3. Document rationale

### Actions

1. **Identify Finance ADRs**:
   | Decision | Topic | Status | Key Point |
   |----------|-------|--------|-----------|
   | "Limit initial scope to Standard Cost information only" | scope | Active | No scope creep |
   | "Select Merlin/Gemini as chatbot over Workday trainings" | approach | Active | Better UX than training |
   | "Use Gemini Enterprise mobile-responsive interface" | architecture | Active | No custom mobile app |
   | "Reduce project duration from 26 weeks to 20-24 weeks" | timeline | Active | Tighter timeline |
   | "US Standard Cost documentation only" | scope | Active | No international |

2. **Document Key ADRs**:
   
   ```markdown
   # ADR-FIN-001: Limit Scope to US Standard Cost Only
   
   **Status**: Active
   **Date**: [Date from atoms]
   **Topic**: Scope
   
   ## Context
   The Finance team has documentation covering multiple topics and geographies. 
   There is temptation to expand scope to cover more content.
   
   ## Decision
   Limit initial scope to Standard Cost information only. US documentation only.
   
   ## Rationale
   - Focus delivers faster value
   - US is the primary use case
   - Can expand later if successful
   - Avoids complexity of international variations
   
   ## Alternatives Considered
   - **All finance documentation**: Rejected — too broad, longer timeline
   - **US + Europe**: Rejected — regulatory/format differences
   
   ## Consequences
   - Faster delivery (20-24 weeks vs 26)
   - Clear success criteria
   - May need Phase 2 for expansion
   
   ## Evidence
   - "Finance Standard Cost Documentation project scope is strictly limited to US Standard Cost documentation"
   ```

   ```markdown
   # ADR-FIN-002: Gemini Enterprise over Workday Training
   
   **Status**: Active
   **Date**: [Date from atoms]
   **Topic**: Approach
   
   ## Context
   Finance needed a way to help employees find information about Standard Cost 
   processes. Options included creating Workday trainings or building a chatbot.
   
   ## Decision
   Use Merlin/Gemini Enterprise as a chatbot solution for Standard Cost 
   Documentation over creating Workday trainings.
   
   ## Rationale
   - Chatbot provides easier navigation
   - Quicker responses than searching training materials
   - Eliminates need to sift through data manually
   - Reduces frustration for partners
   
   ## Alternatives Considered
   - **Workday training modules**: Rejected — still requires manual search
   - **Enhanced SharePoint search**: Rejected — not conversational
   
   ## Consequences
   - Natural language interface for users
   - Requires document ingestion pipeline
   - Ongoing maintenance as documents change
   
   ## Evidence
   - "Select Merlin as a chatbot solution for Standard Cost Documentation over creating Workday trainings"
   ```

### Confirmation Checkpoint
Present:
- List of Finance ADRs
- Sample detailed ADRs

Ask: *"Are these the correct Finance Standard Cost decisions? Any missing?"*

---

## Phase 4: Document Compilation

### Objectives
1. Compile focused, concise documents
2. Emphasize Gemini Enterprise platform
3. Maintain strict scope boundaries

### Compilation Guidelines
- **Voice**: Practical, business-focused
- **Platform**: Clearly identify as Gemini Enterprise (not Merlin)
- **Scope**: Reinforce "US Standard Cost only" throughout
- **Brevity**: This is a simpler project — documents should be appropriately sized

### Document 1: `finance_standard_cost/overview.md`

```markdown
# Finance Standard Cost Documentation Assistant

## Executive Summary
A Q&A assistant powered by **Gemini Enterprise** that enables the Finance team 
to get answers from ~200 SharePoint documents about US Standard Cost processes.

## Business Problem

### Current State
| Aspect | Detail |
|--------|--------|
| Documentation | ~200 documents in SharePoint |
| Formats | Word, Excel, PowerPoint (1-40 pages) |
| Content | Process docs, templates, Oracle operations, standard cost logic |
| Users | ~30 people (finance analysts, plant support) |
| Pain point | Time spent answering repetitive questions |

### High-Usage Groups
- **1st and 2nd year employees**: High turnover creates ongoing training burden
- **Plant support staff**: Need quick process guidance

## What is Standard Cost?
> **Standard Cost**: A single measurement of what the input cost should be, 
> where any actual cost drives a purchase price variance (PPV).

## Business Value

| Metric | Value |
|--------|-------|
| Annual time savings | 360 hours/year |
| - Question answering | 250 hours |
| - Retraining | 20 hours |
| - Mistake correction | 50 hours |
| 3-year value | ~$100,000 |

## Scope

### In Scope
- ✅ US Standard Cost documentation
- ✅ ~200 SharePoint documents
- ✅ Q&A via Gemini Enterprise
- ✅ Mobile access (Gemini responsive)

### Out of Scope
- ❌ International documentation
- ❌ Other finance topics
- ❌ Custom mobile app
- ❌ Custom Merlin development

> **Scope constraint**: "Limit initial scope to Standard Cost information only"

## Platform
**Gemini Enterprise** — leveraging existing enterprise licenses and native RAG 
capabilities. NOT a custom Merlin build.

## Key Stakeholders
| Stakeholder | Role |
|-------------|------|
| Finance team | Project sponsor, primary users |
| Plant support staff | Users |
| New employees | Heavy users (onboarding) |
```

### Document 2: `finance_standard_cost/architecture.md`

```markdown
# Finance Standard Cost Architecture

## Platform Choice
**Gemini Enterprise** — not custom Merlin development.

### Rationale
| Factor | Gemini Enterprise Advantage |
|--------|----------------------------|
| Development effort | Low — native RAG |
| Mobile | Native responsive |
| Licenses | Leverage existing enterprise license |
| Maintenance | Google-managed |
| Time to deploy | Faster |

## Architecture Overview

```
SharePoint (~200 docs)
       │
       ▼
Gemini Enterprise
  ├── Document Sync (connector)
  ├── RAG Pipeline (indexing, embedding, retrieval)
  └── Chat Interface (web + mobile responsive)
       │
       ▼
Finance Users (~30)
```

## Components

### Document Source
| Attribute | Value |
|-----------|-------|
| Location | SharePoint |
| Count | ~200 documents |
| Formats | Word, Excel, PowerPoint |
| Content | Text and screenshots |
| Size | 1-40 pages per document |

### Gemini Enterprise
| Component | Purpose |
|-----------|---------|
| SharePoint Connector | Document sync |
| RAG Pipeline | Indexing, embedding, retrieval |
| Chat Interface | User Q&A |

### Access
| Consideration | Approach |
|---------------|----------|
| User auth | Schreiber SSO (via Google?) |
| Licenses | ~30 Gemini Enterprise seats |
| Mobile | Gemini native responsive |
| Shared computers | Licensing TBD |

## Document Processing

| Content Type | Processing |
|--------------|------------|
| Text | Standard extraction |
| Screenshots | May need OCR/Vision |
| Excel | Table/formula handling |
| PowerPoint | Slide-by-slide |

## Integration Notes
- No custom Merlin components
- Direct Gemini Enterprise deployment
- SharePoint as sole document source
```

### Document 3: `finance_standard_cost/decisions/`

Generate ADR files:
- `ADR-FIN-001-scope-us-standard-cost-only.md`
- `ADR-FIN-002-gemini-over-workday-training.md`
- `ADR-FIN-003-gemini-mobile-not-custom.md`
- `ADR-FIN-004-reduced-timeline.md`

### Document 4: `finance_standard_cost/open_questions.md`

```markdown
# Open Questions — Finance Standard Cost

## Technical
| Question | Priority | Owner | Status |
|----------|----------|-------|--------|
| SharePoint connector configuration? | High | ... | Open |
| Screenshot handling (OCR needed?) | Medium | ... | Open |
| Document sync frequency? | Medium | ... | Open |

## Access & Licensing
| Question | Priority | Owner | Status |
|----------|----------|-------|--------|
| Gemini Enterprise seat allocation? | High | ... | Open |
| Shared plant computer licensing? | High | ... | Open |
| SSO configuration? | Medium | ... | Open |

## Content
| Question | Priority | Owner | Status |
|----------|----------|-------|--------|
| Complete document inventory? | High | Finance | Open |
| Document update cadence? | Medium | Finance | Open |
| Content cleanup needed? | Medium | Finance | Open |

## Scope
| Question | Priority | Owner | Status |
|----------|----------|-------|--------|
| Future expansion to other topics? | Low | Finance | Deferred |
| International documentation? | Low | Finance | Deferred |
```

### Document 5: `finance_standard_cost/roadmap.md`

```markdown
# Finance Standard Cost Roadmap

## Timeline
- **Original estimate**: 26 weeks
- **Revised estimate**: 20-24 weeks
- **Reduction rationale**: Tighter focus, better resource allocation

## Phases

| Phase | Scope | Status | Timeline |
|-------|-------|--------|----------|
| Discovery | Requirements, document inventory | ✅ Complete | ... |
| Setup | Gemini Enterprise config, SharePoint connector | 📅 Planned | Weeks 1-4 |
| Ingestion | Document processing, indexing | 📅 Planned | Weeks 5-10 |
| MVP | Q&A functionality, initial users | 📅 Planned | Weeks 11-16 |
| Rollout | Full user base, training | 📅 Planned | Weeks 17-20 |
| Buffer | Issues, refinement | 📅 Planned | Weeks 21-24 |

## Dependencies

| Dependency | Owner | Status | Blocker? |
|------------|-------|--------|----------|
| Gemini Enterprise access | Google/Schreiber | ... | Yes |
| SharePoint credentials | Schreiber IT | ... | Yes |
| Document inventory | Finance | ... | Yes |
| User licenses (~30) | Schreiber | ... | Yes |

## Success Criteria

| Criteria | Target |
|----------|--------|
| User adoption | 30 users onboarded |
| Query accuracy | [TBD — define with Finance] |
| Time savings | Measurable reduction in question handling |
| User satisfaction | Positive feedback |

## Risks

| Risk | Probability | Impact | Mitigation |
|------|-------------|--------|------------|
| Screenshot processing issues | Medium | Medium | Early testing |
| License availability | Low | High | Early procurement |
| Document quality | Medium | Medium | Pre-processing cleanup |
| User adoption | Low | Medium | Training, change management |
```

---

## Phase 5: Final Review

### Objectives
1. Confirm Gemini Enterprise distinction is clear
2. Verify scope constraints are prominent
3. Ensure appropriate document sizing

### Actions

1. **Platform Check**:
   - "Gemini Enterprise" clearly stated in overview and architecture
   - "NOT Merlin" explicitly mentioned
   - No references to Merlin-specific components

2. **Scope Check**:
   - "US Standard Cost only" in overview
   - Out of scope items listed
   - No scope creep

3. **Size Check**:
   - Documents appropriately sized for project scope
   - Not over-engineered

4. **Manifest Entry**:
   ```markdown
   ## Finance Standard Cost Documents
   - finance_standard_cost/overview.md — [word count], [source count]
   - finance_standard_cost/architecture.md — [word count], [source count]
   - finance_standard_cost/decisions/ — [N] ADRs
   - finance_standard_cost/open_questions.md — [word count]
   - finance_standard_cost/roadmap.md — [word count]
   ```

### Final Confirmation
Ask: *"Finance Standard Cost documentation is complete. Any corrections before finalizing?"*

---

## Pre-loaded Context (from atoms)

### Key Facts
- ~200 documents in SharePoint
- ~30 regular users
- 360 hours/year time savings potential
- ~$100K value over 3 years
- Document types: Word, Excel, PowerPoint (1-40 pages)
- Content includes text and screenshots
- High usage among 1st/2nd year employees

### Key Decisions
- Limit to US Standard Cost only
- Gemini Enterprise over Workday training
- Gemini mobile responsive (no custom app)
- 20-24 weeks (reduced from 26)

### Key Definition
> **Standard Cost**: A single measurement of what the input cost should be, where any actual cost drives a purchase price variance (PPV).

### Platform Note
This is a **Gemini Enterprise project**, not a Merlin project. Platform-level Merlin architecture and decisions do not apply.

---

## Output Format

```markdown
<!-- FILE: finance_standard_cost/overview.md -->
# Finance Standard Cost Documentation Assistant
...

<!-- FILE: finance_standard_cost/architecture.md -->
# Finance Standard Cost Architecture
...

<!-- FILE: finance_standard_cost/decisions/ADR-FIN-001-scope-us-standard-cost-only.md -->
# ADR-FIN-001: Limit Scope to US Standard Cost Only
...

<!-- FILE: finance_standard_cost/open_questions.md -->
# Open Questions — Finance Standard Cost
...

<!-- FILE: finance_standard_cost/roadmap.md -->
# Finance Standard Cost Roadmap
...
```

---

## Begin

Acknowledge receipt of the input files and begin Phase 1: Business Context. Present your findings and await confirmation before proceeding.
