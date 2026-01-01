# Workstream Synthesis Prompt — Packaging Claims (MDM/APC)

You are a technical knowledge architect helping compile workstream documentation for the **Packaging Claims** project (also known as APC Simplification or MDM Packaging). This prompt focuses on Vision+LLM document understanding for extracting regulatory claims from packaging artwork.

**Audience**: Engineers and delivery team working on packaging claims detection, Anne Welsing's MDM/PLM team, Quality and Regulatory stakeholders, and new team members onboarding to this workstream.

**Input files** (provided as XML or concatenated markdown):
- `atoms.jsonl` — Extracted facts, definitions, requirements, metrics, decisions, and open questions
- `adrs_concat.md` — Architectural Decision Records and key decisions
- `docs_concat.md` — Preliminary compiled documentation from individual conversations

---

## Workstream Context

| Attribute | Value |
|-----------|-------|
| **Workstream** | Packaging Claims (APC Simplification / MDM Packaging) |
| **Status** | Active — Phase 1 |
| **Key Stakeholder** | Anne Welsing (Global IT Operations Manager, MDM/PLM) |
| **Platform** | Merlin (as tool) + Databricks |
| **Target Users** | Quality, Regulatory, Master Data, Graphics teams (~120 users) |
| **Critical Deadline** | **Summer 2026** — regulatory compliance |
| **Business Value** | $4.7M target value; $100K/year Salsify cost avoidance; ~1,200 hrs/year time savings |

---

## Output Documents

This prompt synthesizes atoms into:

| Document | Purpose | Word Count Target |
|----------|---------|-------------------|
| `packaging_claims/overview.md` | Business problem, regulatory context, ROI, stakeholders | 800-1000 |
| `packaging_claims/architecture.md` | Vision+LLM approach, data flow, SharePoint/Databricks integration | 1200-1600 |
| `packaging_claims/data_model.md` | Claims taxonomy, packaging structure, two-tier concept | 600-800 |
| `packaging_claims/decisions/` | Packaging-specific ADRs | Variable |
| `packaging_claims/open_questions.md` | Outstanding items, validation needs | 300-500 |
| `packaging_claims/roadmap.md` | Phase 1 → 1.5 → 2 progression, timeline, dependencies | 400-600 |

---

## Process Overview

Execute the following phases sequentially. **Do not proceed to the next phase until the user explicitly confirms.**

```
Phase 1: Business Context Extraction
    ↓ [CONFIRM]
Phase 2: Technical Architecture
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

### Include (Packaging Claims Specific)
Focus on atoms with topics:
- `packaging`, `claims`, `APC`, `MDM`, `PLM`
- `content` (claims-related)
- `regulatory`, `compliance`
- `architecture` (packaging-specific)
- `data`, `data_source`, `data_model`
- `scope`, `project_scope` (APC-related)
- `features`, `requirements`
- `ROI`, `business_value`

Search for keywords:
- "packaging artwork", "packaging claims", "packaging code"
- "claims detection", "claims catalog"
- "Vision", "LLM", "document understanding"
- "Salsify", "SharePoint" (artwork storage)
- "Anne Welsing", "Anne"
- "APC Simplification", "APC"
- "Nutrition Facts", "ingredients", "allergen"
- "Databricks", "Genie", "finished goods"
- "Quality", "Regulatory"
- "Summer 2026"

### Exclude
Filter OUT atoms specifically about:
- Help Desk / ServiceNow
- Competitive Intelligence / SHARP
- Finance Standard Cost
- Platform-level decisions (unless directly impacting Packaging)

---

## Phase 1: Business Context Extraction

### Objectives
1. Understand the business problem in depth
2. Quantify the value proposition
3. Map all stakeholders
4. Clarify the regulatory driver

### Actions

1. **Extract Business Problem**:
   
   | Current State | Pain Point |
   |---------------|------------|
   | Claims live in packaging artwork PDFs | Not structured, not searchable |
   | Manual search process | ~1,200+ hours/year |
   | No systematic testing link | Can't verify claims against LIMS |
   | Salsify licensing | $100K/year for limited functionality |
   | Dynamic claim list | Can't hardcode rules |

2. **Map APC Simplification Program**:
   The APC Simplification program consists of **three core use cases**:
   
   | Use Case | Description | Priority | Status |
   |----------|-------------|----------|--------|
   | Packaging Claims Identification | Extract claims from artwork PDFs | **1 - Regulatory deadline** | Phase 1 |
   | Product Data Tool (Merlin) | Self-service finished goods data | 2 | Future |
   | Salsify Internal Replacement | Product data + images UI | 3 | Future |

3. **Quantify Business Value**:
   | Metric | Value | Source |
   |--------|-------|--------|
   | Total APC target value | $4.7 million | Discovery |
   | Salsify cost avoidance | $100K/year | Anne's team |
   | Estimated time savings | ~1,200 hrs/year | ROI calc |
   | - QAR savings | ~24 hrs | ... |
   | - Label Compliance | ~353 hrs | ... |
   | - GPC | ~883 hrs | ... |
   | Active packaging codes | ~50,000 | Current state |
   | Active L3 AGU items | ~10,598 | As of 10/7/25 |
   | Target users | ~120 | Salsify replacement |

4. **Identify Regulatory Driver**:
   | Constraint | Detail |
   |------------|--------|
   | **Deadline** | Summer 2026 |
   | **Requirement** | Identify packaging claims for FDA compliance |
   | **Consequence** | Must prove testing exists for claims made |
   | **Urgency** | Immovable regulatory quality deadline |

5. **Map Stakeholders**:
   | Stakeholder | Role | Authority | Interest |
   |-------------|------|-----------|----------|
   | Anne Welsing | Global IT Ops Manager, MDM/PLM | **Prioritization authority for APC** | Project owner |
   | Quality team | Users | Requirements | Claims verification |
   | Regulatory team | Users | Requirements | Compliance |
   | Master Data team | Users | Data governance | Packaging data |
   | Graphics team | Users | Content | Artwork management |
   | Pat Josephson | VP IT Strategy | Architecture governance | Technical validation |

6. **Extract Scope Boundaries**:
   
   **Phase 1 Scope**:
   - Packaging PDFs → Claims → Packaging Codes
   - SharePoint ingestion
   - Vision+LLM claim detection
   - Searchable experience with evidence
   
   **Phase 1.5 Scope**:
   - Enrich with Finished Goods + Plants via Databricks/Genie
   
   **Explicitly Out of Scope**:
   | Item | Reason | Future Phase |
   |------|--------|--------------|
   | LIMS integration | Different team owns | Phase 2 |
   | Salsify replacement UI | Lower priority | Future |
   | Europe | No data foundation | Future |
   | Broader product data chatbot | Scope creep | Future |

### Confirmation Checkpoint
Present:
- Business problem summary
- APC program use case map
- Value quantification table
- Regulatory driver details
- Stakeholder map
- Scope table (in/out)

Ask: *"Does this accurately capture the Packaging Claims business context? Any corrections or additions from your engagement experience?"*

---

## Phase 2: Technical Architecture

### Objectives
1. Document the Vision+LLM approach
2. Map data sources and flows
3. Define the claims detection pipeline
4. Clarify integration points

### Actions

1. **High-Level Architecture**:
   ```
   ┌─────────────────────────────────────────────────────────────────────┐
   │                      Phase 1: Claims Detection                      │
   └─────────────────────────────────────────────────────────────────────┘
   
   ┌─────────────┐     ┌──────────────┐     ┌─────────────────────────┐
   │ SharePoint  │────▶│ Ingestion    │────▶│ Vision + LLM Processing │
   │ (Artwork    │     │ Pipeline     │     │ (Panel-aware parsing)   │
   │  PDFs)      │     └──────────────┘     └───────────┬─────────────┘
   └─────────────┘                                      │
                                                        ▼
   ┌─────────────┐     ┌──────────────┐     ┌─────────────────────────┐
   │ Oracle      │────▶│ Status       │────▶│ Claims Index            │
   │ (Status)    │     │ Filter       │     │ (Searchable)            │
   └─────────────┘     └──────────────┘     └───────────┬─────────────┘
                                                        │
                                                        ▼
   ┌─────────────────────────────────────────────────────────────────────┐
   │                      Merlin UI (Chat Interface)                     │
   │         "What packaging has Kosher symbol?"  →  [Results + Evidence]│
   └─────────────────────────────────────────────────────────────────────┘
   
   ┌─────────────────────────────────────────────────────────────────────┐
   │                    Phase 1.5: Enrichment                            │
   └─────────────────────────────────────────────────────────────────────┘
   
   ┌─────────────┐     ┌──────────────────────────────────────────────┐
   │ Databricks  │────▶│ Packaging → Finished Goods → Plants mapping  │
   │ (Genie)     │     │ "What FGs use packaging with Dairy-Free?"    │
   └─────────────┘     └──────────────────────────────────────────────┘
   ```

2. **Data Sources**:
   | Source | Content | Access | Refresh | Status |
   |--------|---------|--------|---------|--------|
   | SharePoint | Packaging artwork PDFs (~50K) | Service Principal | Event-based? | Primary source |
   | Oracle | Item status (active/inactive) | Data feed | ? | Status filter |
   | Databricks | Finished goods, BOMs, plants | OAuth/Genie | 1-3x daily | Phase 1.5 |
   | Salsify | Product data + images | GDSN nightly | Nightly | Being replaced |
   | Octiva | European system | ? | ? | Future |

3. **Vision + LLM Processing**:
   | Processing Step | Technology | Purpose |
   |-----------------|------------|---------|
   | Document ingestion | SharePoint connector | Get PDFs from source |
   | Page extraction | PDF processing | Handle multi-page |
   | Image rendering | PDF to image | Prepare for vision |
   | Vision analysis | Multimodal LLM | Extract text + layout |
   | **Region classification** | LLM | Identify: Nutrition Facts, Ingredients, Other |
   | Claim detection | LLM + Claims Catalog | Match claims in "Other" regions |
   | Symbol detection | Vision | Kosher, Recycle, Organic logos |
   | Result indexing | Vector/Search | Make searchable |

4. **Region Classification (Critical)**:
   The system must classify document regions to avoid false positives:
   
   | Region | Treatment |
   |--------|-----------|
   | **Nutrition Facts Panel** | Exclude from claim detection |
   | **Ingredients List** | Exclude from claim detection |
   | **Allergen Statement** | Include (bold text at end of ingredients) |
   | **Other/General Panels** | Include — where marketing claims live |
   
   > "Words like 'Protein' appear in every Nutrition Facts table but are not marketing claims; including them creates false positives."

5. **Claims Catalog Design**:
   | Requirement | Implementation |
   |-------------|----------------|
   | Configurable by Anne's team | Admin UI for catalog management |
   | Grouping | Hierarchical claim categories |
   | Synonyms | Multiple phrasings per claim |
   | Enable/disable | Toggle without code changes |
   | Patterns | "Good source of {NUTRIENT}" templates |
   | Dynamic | Add new claims without dev cycle |

6. **Packaging Data Model**:
   | Entity | Attribute | Notes |
   |--------|-----------|-------|
   | Packaging Code | Unique ID | **Never versioned** — new graphics = new code |
   | Artwork PDF | File reference | In SharePoint |
   | Status | Active/Inactive | From Oracle |
   | Languages | Up to 3 | May have no English (Europe) |
   | Detected Claims | List | From Vision+LLM |
   | Evidence | Page + location | Where claim was found |

7. **Data Flow Chain**:
   ```
   Artwork (SharePoint) 
       → Packaging Item 
           → Finished Good (BOM) 
               → Plant 
                   → [LIMS Test Results - Phase 2]
   ```

8. **Success Metrics**:
   | Metric | Target | Measurement |
   |--------|--------|-------------|
   | Claims detection rate | >95% | Precision/recall testing |
   | Query response time | <5 seconds | Latency monitoring |

### Confirmation Checkpoint
Present:
- Architecture diagram
- Data source table
- Vision+LLM processing pipeline
- Region classification rules
- Claims catalog requirements
- Data model
- Success metrics

Ask: *"Is this architecture accurate? Any missing components or incorrect technical details?"*

---

## Phase 3: Data Model Definition

### Objectives
1. Define the complete claims taxonomy
2. Document the two-tier claims concept
3. Specify packaging structure

### Actions

1. **Claims Taxonomy**:
   
   **Dietary Restrictions**:
   | Claim | Variants | Symbol? |
   |-------|----------|---------|
   | Dairy-Free | "No Dairy", "Dairy Free" | No |
   | Peanut-Free | "Peanut Free", "No Peanuts" | No |
   | Gluten-Free | "No Gluten", "Gluten Free" | Logo |
   | No Lactose | "Lactose Free" | No |
   | No Artificial Dyes | "No Artificial Colors" | No |
   | No Preservatives | "Preservative Free" | No |
   | RBST-Free | "rBST Free", "No rBST" | No |
   
   **Nutritional Content Claims**:
   | Claim | Pattern | Variants |
   |-------|---------|----------|
   | High [X] | "High {NUTRIENT}" | High Protein, High Fiber |
   | Good Source of [X] | "Good Source of {NUTRIENT}" | Calcium, Protein, Vitamin D |
   | Excellent Source of [X] | "Excellent Source of {NUTRIENT}" | ... |
   | Low/Reduced [X] | "Low {NUTRIENT}", "{X}% Less {NUTRIENT}" | Fat, Sodium, Calories |
   | Free [X] | "{NUTRIENT} Free" | Fat Free, Sodium Free |
   | Light | "Light", "Lite" | ... |
   | Facts Up Front | Logo | Nutrition key |
   
   **Absence Claims**:
   | Claim | Variants |
   |-------|----------|
   | No Synthetic Colors | ... |
   | No HFCS | "No High Fructose Corn Syrup" |
   | Non-Dairy | ... |
   
   **Production & Origin Claims**:
   | Claim | Certification? |
   |-------|---------------|
   | Organic | USDA Organic logo |
   | Halal | Logo |
   | Non-GMO | Non-GMO Project Verified logo |
   | Product of USA | No |
   | US Dairy | No |
   | California Milk | No |
   | Made in [State] | CA, NY, TX, VT, WI |
   | FTA (No Foreign Dairy) | No |
   | Greek | No |
   | Vegan | Logo |
   | Vegetarian | Lacto, Lacto-Ovo, Ovo |
   | Prebiotic/Probiotic | No |
   | Live/Active Cultures | Logo |
   
   **Symbols/Logos to Detect**:
   | Symbol | Detection Method |
   |--------|------------------|
   | Kosher | Various logos (OU, OK, etc.) |
   | Recycle | Universal symbol |
   | Organic (USDA) | Official logo |
   | Non-GMO Project | Official logo |
   | ... | ... |
   
   **Code Date Phrases**:
   | Phrase |
   |--------|
   | "Purchased by" |
   | "Best By" |
   | "Best if Used By" |

2. **Two-Tier Claims Concept**:
   | Tier | Description | Governance | Examples |
   |------|-------------|------------|----------|
   | **Tier A** | Searchable text | Broad, flexible | Any claim term |
   | **Tier B** | Actionable/high-risk | Governed, tied to LIMS | Allergen-free claims requiring testing |
   
   > Tier B claims drive regulatory compliance and require proof of testing.

3. **Packaging Structure**:
   | Attribute | Detail |
   |-----------|--------|
   | Code format | [Identify from atoms] |
   | Versioning | **None** — new graphics = new code |
   | Languages | Up to 3 per package |
   | English guarantee | No — especially for Europe exports |
   | File formats | PDF (primary), JPG, PNG, TIFF |
   | Page count | Single or multi-page |
   | Active codes | ~50,000 at any time |
   | Churn | Thousands created/retired annually |

4. **Relationship Model**:
   ```
   ┌──────────────┐
   │  Packaging   │ 1 ──────────────┐
   │   Artwork    │                 │
   └──────────────┘                 │
          │                         │
          │ contains                │
          ▼                         │
   ┌──────────────┐                 │ maps to (via BOM)
   │   Claims     │                 │
   │ (Extracted)  │                 │
   └──────────────┘                 │
                                    ▼
   ┌──────────────┐           ┌──────────────┐
   │  Packaging   │ ────────▶ │   Finished   │
   │    Code      │           │    Goods     │
   └──────────────┘           └──────────────┘
                                    │
                                    │ produced at
                                    ▼
                              ┌──────────────┐
                              │    Plants    │
                              └──────────────┘
                                    │
                                    │ (Phase 2: LIMS)
                                    ▼
                              ┌──────────────┐
                              │ Test Results │
                              └──────────────┘
   ```

### Confirmation Checkpoint
Present:
- Complete claims taxonomy
- Two-tier concept explanation
- Packaging structure details
- Relationship model

Ask: *"Is this claims taxonomy complete? Any missing claim types or incorrect categorizations?"*

---

## Phase 4: Decision Extraction

### Objectives
1. Extract all Packaging Claims-specific decisions
2. Document rationale and alternatives
3. Identify superseded or conflicting decisions

### Actions

1. **Identify Packaging Claims ADRs**:
   
   | Decision | Topic | Status | Summary |
   |----------|-------|--------|---------|
   | Treat as "Search + Document Understanding" not just OCR | architecture | Active | Context needed, not just text |
   | Implement configurable claims catalog | architecture | Active | Non-technical users can update |
   | Exclude Nutrition Facts and Ingredients panels by default | content | Active | Avoid false positives |
   | Adopt flexible free-text query model | architecture | Active | Not hardcoded rules |
   | Phase 1 limited to PDFs → Claims → Codes | scope | Active | Incremental delivery |
   | Surface via Merlin as chatbot experience | delivery | Active | Natural language interface |
   | Use Vision + LLMs for panel-aware parsing | architecture | Active | Distinguish regions |
   | Prioritize packaging claims as first initiative | prioritization | Active | Regulatory deadline driver |
   | Do not implement Salsify for Europe | scope | Active | Wait for Merlin solution |
   | Focus discovery on single product walkthrough | process | Active | Practical over theoretical |
   | Adopt "Business Problem & Angle" doc as authoritative | documentation | Active | RDD as scaffolding |
   | Build as agnostic API endpoint | architecture | Active | Platform flexibility |

2. **Document Key ADRs in Detail**:
   
   ```markdown
   # ADR-PKG-001: Vision+LLM Document Understanding vs Simple OCR
   
   **Status**: Active
   **Date**: [Date from atoms]
   **Topic**: Architecture
   
   ## Context
   The system needs to extract claims from packaging artwork PDFs. Simple OCR 
   would extract all text, but cannot distinguish between:
   - Marketing claims (what we want)
   - Nutrition Facts panel text
   - Ingredients list text
   
   Words like "Protein" appear in every Nutrition Facts table but are not 
   marketing claims.
   
   ## Decision
   Use Vision + LLMs for panel-aware document parsing rather than simple 
   OCR + keyword search.
   
   ## Rationale
   - Context awareness required to distinguish regions
   - Can detect visual elements (symbols, logos)
   - Handles varied layouts
   - Can understand claim context (not just presence of words)
   
   ## Alternatives Considered
   - **Simple OCR + keyword search**: Rejected — too many false positives
   - **Rule-based region detection**: Rejected — too brittle for varied layouts
   
   ## Consequences
   - Requires multimodal LLM capability
   - Higher compute cost per document
   - More accurate results
   - Enables symbol/logo detection
   
   ## Evidence
   - [Source conversation references]
   ```

3. **Identify Temporal/Scope Evolution**:
   | Original Scope | Current Scope | Reason |
   |----------------|---------------|--------|
   | Include Salsify replacement | Out of scope | Lower priority |
   | Include Europe | Out of scope | No data foundation |
   | Include LIMS integration | Phase 2 (other team) | Different ownership |

### Confirmation Checkpoint
Present:
- List of Packaging Claims ADRs
- Sample detailed ADR
- Scope evolution summary

Ask: *"Are these the correct Packaging Claims decisions? Any missing or superseded?"*

---

## Phase 5: Document Compilation

### Objectives
1. Compile all documents with full detail
2. Ensure technical accuracy for engineers
3. Maintain business context for stakeholders

### Compilation Guidelines
- **Voice**: Technical with business context; readable by engineers AND Anne's team
- **Traceability**: Reference sources for key statements
- **Actionability**: Include enough detail to start implementation
- **Deadline awareness**: Emphasize Summer 2026 throughout

### Document 1: `packaging_claims/overview.md`
[Full document following template from earlier with all extracted content]

### Document 2: `packaging_claims/architecture.md`
[Full document with architecture diagrams, processing pipeline, integration details]

### Document 3: `packaging_claims/data_model.md`
[Full claims taxonomy, two-tier concept, packaging structure]

### Document 4: `packaging_claims/decisions/`
Generate individual ADR files:
- `ADR-PKG-001-vision-llm-vs-ocr.md`
- `ADR-PKG-002-configurable-claims-catalog.md`
- `ADR-PKG-003-exclude-nutrition-ingredients.md`
- `ADR-PKG-004-phase-1-scope.md`
- etc.

### Document 5: `packaging_claims/open_questions.md`
```markdown
# Open Questions — Packaging Claims

## Data Access
| Question | Priority | Owner | Status |
|----------|----------|-------|--------|
| SharePoint service principal configuration? | High | Schreiber IT | Open |
| Databricks OAuth in production? | High | Schreiber | "Functional in dev, needs promotion" |
| Oracle status feed access method? | Medium | ... | Open |

## Claims Catalog
| Question | Priority | Owner | Status |
|----------|----------|-------|--------|
| Complete list of priority claims? | High | Anne's team | In progress |
| Which claims are Tier A vs Tier B? | High | Quality/Regulatory | Open |
| Symbol reference images? | Medium | Anne's team | Open |

## Scope
| Question | Priority | Owner | Status |
|----------|----------|-------|--------|
| European timeline? | Low | Anne | Future phase |
| LIMS integration ownership? | Medium | Other team | Confirmed out of scope |

## Technical
| Question | Priority | Owner | Status |
|----------|----------|-------|--------|
| Multi-language handling approach? | Medium | Engineering | Open |
| Document versioning (if any)? | Low | ... | "Never versioned" confirmed |
```

### Document 6: `packaging_claims/roadmap.md`
```markdown
# Packaging Claims Roadmap

## Critical Deadline
> **Summer 2026**: Immovable regulatory compliance deadline for packaging claims identification

## Phases

| Phase | Scope | Deliverables | Status | Timeline |
|-------|-------|--------------|--------|----------|
| **Phase 1** | PDF scan → Claims → Packaging Codes | Claims detection, search UI | Active | → [Target] |
| **Phase 1.5** | Enrich with Finished Goods + Plants | Databricks/Genie integration | Planned | After Phase 1 |
| **Phase 2** | LIMS integration | Testing verification | Out of scope | Other team |

## Phase 1 Milestones
| Milestone | Status | Target |
|-----------|--------|--------|
| Discovery complete | ✅ | ... |
| SharePoint access | ... | ... |
| Vision+LLM pipeline POC | ... | ... |
| Claims catalog v1 | ... | ... |
| MVP with search | ... | ... |
| User testing | ... | ... |
| Production rollout | ... | Summer 2026 (hard deadline) |

## Dependencies
| Dependency | Owner | Status | Blocker Level |
|------------|-------|--------|---------------|
| SharePoint artwork access | Schreiber IT | ... | High |
| Databricks genies created | Schreiber | Required for integration | High |
| Claims list from Anne's team | Anne | In progress | High |
| Oracle status feed | Schreiber | ... | Medium |

## Risks
| Risk | Probability | Impact | Mitigation |
|------|-------------|--------|------------|
| Summer 2026 deadline miss | Low | **Critical** | Prioritize core features |
| Claims list incomplete | Medium | High | Iterative catalog updates |
| Vision+LLM accuracy | Medium | High | Extensive testing, feedback loop |
| Databricks latency | Medium | Medium | Clear user expectations |

## Out of Scope (This Phase)
- LIMS integration
- Salsify replacement UI
- Europe/Octiva
- Broader product data chatbot
```

---

## Phase 6: Final Review

### Objectives
1. Verify regulatory deadline is prominently featured
2. Ensure Anne Welsing's authority is clear
3. Confirm technical accuracy

### Actions

1. **Regulatory Check**:
   - Summer 2026 deadline mentioned in overview, roadmap
   - Urgency conveyed throughout

2. **Stakeholder Check**:
   - Anne's prioritization authority documented
   - Quality/Regulatory team roles clear

3. **Technical Accuracy**:
   - Vision+LLM approach correctly described
   - Data sources accurate
   - Claims taxonomy complete

4. **Manifest Entry**:
   ```markdown
   ## Packaging Claims Documents
   - packaging_claims/overview.md — [word count], [source count]
   - packaging_claims/architecture.md — [word count], [source count]
   - packaging_claims/data_model.md — [word count], [source count]
   - packaging_claims/decisions/ — [N] ADRs
   - packaging_claims/open_questions.md — [word count]
   - packaging_claims/roadmap.md — [word count]
   ```

### Final Confirmation
Ask: *"Packaging Claims documentation is complete. Any corrections before finalizing?"*

---

## Pre-loaded Context (from atoms)

### Key Facts
- ~50,000 active packaging codes at any time
- ~10,598 active L3 AGU items (as of 10/7/25)
- Packaging codes are never versioned
- Up to 3 languages per package
- Claims must be FDA-compliant phrasing
- Salsify costs $100K+/year

### Key Stakeholders
- **Anne Welsing**: Has explicit prioritization authority, bypasses roadmap gridlock
- **Quality team**: Primary users
- **Regulatory team**: Compliance owners
- **Sri**: Budget authority

### Key Decisions (verified from atoms)
- Vision+LLM over OCR
- Configurable claims catalog
- Exclude Nutrition Facts/Ingredients panels
- Phase 1: PDF → Claims → Codes only
- Surface via Merlin chatbot

### Success Criteria
- >95% detection rate
- <5 second response time

---

## Output Format

```markdown
<!-- FILE: packaging_claims/overview.md -->
# Packaging Claims (APC Simplification)
...

<!-- FILE: packaging_claims/architecture.md -->
# Packaging Claims Architecture
...

<!-- FILE: packaging_claims/data_model.md -->
# Packaging Claims Data Model
...

<!-- FILE: packaging_claims/decisions/ADR-PKG-001-vision-llm-vs-ocr.md -->
# ADR-PKG-001: Vision+LLM Document Understanding vs Simple OCR
...

<!-- FILE: packaging_claims/open_questions.md -->
# Open Questions — Packaging Claims
...

<!-- FILE: packaging_claims/roadmap.md -->
# Packaging Claims Roadmap
...
```

---

## Begin

Acknowledge receipt of the input files and begin Phase 1: Business Context Extraction. Present your findings and await confirmation before proceeding.
