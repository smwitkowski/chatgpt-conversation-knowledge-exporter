# Schreiber Knowledge Synthesis Prompts

This directory contains comprehensive prompts for synthesizing extracted knowledge atoms into canonical project documentation for the Schreiber Foods engagement.

## Directory Structure

```
prompts/
├── README.md                              # This file
├── schreiber_knowledge_synthesis.md       # Original combined prompt (reference)
│
├── shared/                                # Cross-cutting shared context
│   ├── client_context_prompt.md           # Client profile, stakeholders, glossary, timeline
│   └── platform_prompt.md                 # Merlin core platform architecture
│
└── workstreams/                           # Individual workstream prompts
    ├── helpdesk_mvp_prompt.md             # Help Desk MVP (ServiceNow → Gemini)
    ├── packaging_claims_prompt.md         # Packaging Claims (MDM/APC) — Vision+LLM
    ├── competitive_intelligence_prompt.md # Competitive Intelligence (SHARP)
    └── finance_standard_cost_prompt.md    # Finance Standard Cost (Gemini Enterprise)
```

## Prompt Structure

Each prompt follows a consistent, comprehensive structure:

### Common Elements

| Section | Purpose |
|---------|---------|
| **Workstream Context** | Key attributes, status, stakeholders, platform |
| **Output Documents** | Target files with word count targets |
| **Process Overview** | Phased execution with confirmation checkpoints |
| **Atom Filtering Strategy** | Topics and keywords to include/exclude |
| **Phase-by-Phase Actions** | Detailed extraction and synthesis steps |
| **Document Templates** | Full markdown templates for each output file |
| **Validation Prompts** | Edge case handling guidance |
| **Pre-loaded Context** | Known facts from atoms to seed the synthesis |
| **Output Format** | File markers for direct creation |

### Confirmation Checkpoints

All prompts use explicit confirmation gates:
```
Phase 1 → [CONFIRM] → Phase 2 → [CONFIRM] → ... → Final Review
```

## Recommended Execution Order

### 1. Shared Context (Run First)

| Prompt | Outputs | Purpose |
|--------|---------|---------|
| `shared/client_context_prompt.md` | `shared/client_context.md`, `stakeholders.md`, `glossary.md`, `engagement_overview.md` | Foundation for all workstreams |
| `shared/platform_prompt.md` | `platform/overview.md`, `architecture.md`, `integrations.md`, `decisions/` | Core Merlin platform docs |

### 2. Workstreams (Run Independently)

| Prompt | Outputs | Platform |
|--------|---------|----------|
| `workstreams/helpdesk_mvp_prompt.md` | `helpdesk_mvp/overview.md`, `architecture.md`, `decisions/`, `open_questions.md`, `roadmap.md` | Merlin → Gemini Enterprise |
| `workstreams/packaging_claims_prompt.md` | `packaging_claims/overview.md`, `architecture.md`, `data_model.md`, `decisions/`, `open_questions.md`, `roadmap.md` | Merlin + Databricks |
| `workstreams/competitive_intelligence_prompt.md` | `competitive_intelligence/overview.md`, `architecture.md`, `data_model.md`, `decisions/`, `open_questions.md`, `roadmap.md` | Standalone + Merlin/Gemini |
| `workstreams/finance_standard_cost_prompt.md` | `finance_standard_cost/overview.md`, `architecture.md`, `decisions/`, `open_questions.md`, `roadmap.md` | Gemini Enterprise only |

## Final Output Structure

```
docs/
├── shared/
│   ├── client_context.md         # Schreiber profile, ESOP culture
│   ├── stakeholders.md           # All client/vendor stakeholders
│   ├── glossary.md               # Terminology (APC, GDSN, PLM, etc.)
│   └── engagement_overview.md    # Timeline, SOWs, workstream summary
│
├── platform/
│   ├── overview.md               # What Merlin is, Gemini migration
│   ├── architecture.md           # Core Merlin architecture
│   ├── integrations.md           # Databricks, SharePoint, GCP
│   └── decisions/                # Platform-level ADRs
│
├── helpdesk_mvp/
│   ├── overview.md               # Project summary, business value
│   ├── architecture.md           # ServiceNow integration, migration
│   ├── decisions/                # Help Desk ADRs
│   ├── open_questions.md         # Outstanding items
│   └── roadmap.md                # Phases, milestones
│
├── packaging_claims/
│   ├── overview.md               # Business problem, regulatory deadline
│   ├── architecture.md           # Vision+LLM pipeline, data flow
│   ├── data_model.md             # Claims taxonomy, two-tier concept
│   ├── decisions/                # Packaging ADRs
│   ├── open_questions.md         # Outstanding items
│   └── roadmap.md                # Phase 1 → 1.5 → 2
│
├── competitive_intelligence/
│   ├── overview.md               # SHARP vision, current state
│   ├── architecture.md           # Ingestion, knowledge graph, UI
│   ├── data_model.md             # Competitor schema, battle cards
│   ├── decisions/                # CI ADRs
│   ├── open_questions.md         # Outstanding items
│   └── roadmap.md                # Sequential rollout
│
└── finance_standard_cost/
    ├── overview.md               # Business problem, value
    ├── architecture.md           # Gemini Enterprise RAG
    ├── decisions/                # Finance ADRs
    ├── open_questions.md         # Outstanding items
    └── roadmap.md                # 20-24 week timeline
```

## Workstream Summary

| Workstream | Platform | Status | Key Deadline | Key Stakeholder |
|------------|----------|--------|--------------|-----------------|
| **Help Desk MVP** | Merlin → Gemini | Active (90%) | End of June | Kaspar |
| **Packaging Claims** | Merlin + Databricks | Active | **Summer 2026** | Anne Welsing |
| **Competitive Intelligence** | Standalone + Merlin | Design/Pilot | Sequential | Pat, Mark |
| **Finance Standard Cost** | Gemini Enterprise | Planned | 20-24 weeks | Finance team |

## Platform Boundaries

| Workstream | Uses Merlin Core? | Platform-Specific Decisions |
|------------|-------------------|----------------------------|
| Help Desk MVP | Yes → migrating | Gemini Enterprise migration |
| Packaging Claims | Yes (as tool) | Vision+LLM, claims catalog |
| Competitive Intelligence | Integration only | SHARP standalone, knowledge graph |
| Finance Standard Cost | **No** | Pure Gemini Enterprise |

**Important**: Finance Standard Cost uses Gemini Enterprise directly. Merlin platform decisions do NOT apply.

## Excluded Workstreams

These are **not** included (historical or superseded):
- Agentspace Pilot (now Gemini Enterprise)
- Blue Slips
- Sparq Integration

## Input Files

Each prompt expects these input files from the knowledge extractor:
- `atoms.jsonl` — Extracted facts, decisions, open questions (2,622 atoms)
- `adrs_concat.md` — Architectural Decision Records (591 decisions)
- `docs_concat.md` — Preliminary compiled documentation

## Usage Tips

1. **Run shared context first** — Provides foundation for all workstreams
2. **Use atom filtering** — Each prompt specifies topics/keywords to filter
3. **Respect confirmation checkpoints** — Don't skip ahead
4. **Check platform boundaries** — Don't apply Merlin decisions to Finance
5. **Update as you learn** — Prompts can be refined based on synthesis results

## Key Pre-loaded Context

### Client Profile
- **Schreiber Foods**: $7B global private-label dairy, 100% ESOP
- **Culture**: Risk-averse, cost-conscious, consensus-driven
- **AI Budget**: $2-4M for 2026 (per CIDO Sri)

### Key Stakeholders
- **Sri (Sriraj Kantamneni)**: CIDO, budget authority
- **Anne Welsing**: MDM/PLM, Packaging Claims authority
- **Pat Josephson**: VP IT Strategy, architecture governance
- **Pat, Mark**: Competitive Intelligence governance

### Key Decisions
- Migrate to Gemini Enterprise (memory, mobile)
- Build workstream features as agnostic API endpoints
- Packaging Claims: Summer 2026 deadline is immovable
- Competitive Intelligence: Proceed sequentially, not all at once

## Version History

| Date | Change |
|------|--------|
| 2025-12-31 | Initial comprehensive prompts created |
