<!-- FILE: docs/decisions/README.md -->
# Testero ADR Index

**Last updated:** 2025-12-25  
**Audience:** AI engineers + AI assistants

This folder contains the **deduplicated, canonical ADR set** for Testero.
Each ADR includes traceability back to the extracted ADR artifacts and (where applicable) steering updates made on **2025-12-24**.

## ADRs (canonical)

- ADR-0001 — PMLE-first launch scope
- ADR-0002 — Core stack + deployment posture
- ADR-0003 — Auth + billing entitlements (Stripe webhooks)
- ADR-0004 — Pricing & packaging (single $15/mo plan; free boundary)
- ADR-0005 — No auto-publish: human review gate for content
- ADR-0006 — Only serve questions that are ACTIVE + GOOD
- ADR-0007 — Diagnostic sessions snapshot questions for immutability
- ADR-0008 — Quality routing: automated validation + human review rubric
- ADR-0009 — Analytics: PostHog as primary event tracking
- ADR-0010 — Vectors/embeddings: future enhancement (not production-wired)
- ADR-0011 — “Pass-or-Extend”: direction accepted, spec/copy TBD

## Status meanings

- **active** — authoritative unless superseded
- **superseded** — kept for history; do not implement as current behavior
- **draft** — proposed but not yet confirmed end-to-end

---

<!-- Notes:
Sources are referenced inline in each ADR as:
  - extracted ADR file path(s)
  - steering updates (date)
-->



<!-- FILE: docs/decisions/ADR-0001-pmle-first-scope.md -->
# ADR-0001: PMLE-first launch scope

**Status:** active  
**Date:** 2025-12-05 (extracted), reaffirmed 2025-12-24 (steering)  
**Topic:** scope

## Context
Testero is a certification-readiness product. Early conversations included broader scope (multiple certification providers), but launch focus must be narrow enough to ship a credible loop with high-quality content.

## Decision
Launch with **Google Professional Machine Learning Engineer (PMLE)** as the **only** exam scope, and avoid expanding to additional exams until there is a traction signal.

## Rationale
- Concentrates limited build + content bandwidth into one cohesive experience.
- Reduces complexity in content pipeline, evaluation, and messaging.
- Improves odds of delivering a “trustworthy” product rather than a shallow multi-exam shell.

## Consequences
- All product and content decisions should assume **PMLE-first**.
- Other exams/providers remain explicitly deferred until traction.

## Sources
- Extracted ADR: `69335397-c5f4-832a-a049-8fd3cfcbf588/ADR-0002-scope.md`
- Related (historical broader scope): `6803d6a2-9950-8005-ad25-816de069e880/ADR-0001-content.md` (superseded for launch scope)



<!-- FILE: docs/decisions/ADR-0002-core-stack-and-deployment.md -->
# ADR-0002: Core stack + deployment posture

**Status:** active  
**Date:** 2025-04-28 (extracted), reaffirmed 2025-12-24 (steering)  
**Topic:** architecture

## Context
Testero must ship quickly as a solo-built product, with a path to scale later without forcing premature platform complexity.

## Decision
Adopt the following core posture:
- **Next.js** for the web app (TypeScript)
- **Supabase** as the primary database + platform layer (including auth)
- Deploy initially on a **DigitalOcean droplet** (or equivalent simple hosting), with a **future migration path** to more scalable infra if needed
- Treat advanced components (multi-service orchestration, heavy infra) as optional until traction

## Rationale
- Maximizes iteration speed and reduces ops overhead.
- Supabase provides primitives that remove bespoke backend work early.
- Keeps infra decisions reversible.

## Consequences
- Architecture docs and implementation should assume Supabase as the system-of-record.
- Any additional services should be justified by measurable bottlenecks (cost, performance, reliability).

## Sources
- Extracted ADR (stack posture): `68101dc2-9f24-8005-9eb0-25b048e5db84/ADR-0003-architecture.md`



<!-- FILE: docs/decisions/ADR-0003-auth-and-billing-entitlements.md -->
# ADR-0003: Supabase Auth + Stripe billing with webhook-driven entitlements

**Status:** active  
**Date:** 2025-11-01 (extracted)  
**Topic:** architecture / billing

## Context
Testero needs reliable access control for Free vs Paid features, with minimal custom payment surface area and strong security posture.

## Decision
- Use **Supabase Auth** for authentication.
- Use **Stripe** for billing.
- Grant/revoke paid access via **webhook-driven entitlements** stored in the database.
- Gate paid features based on server-trusted entitlements (not client-side assumptions).

## Rationale
- Stripe is the standard for subscription management.
- Webhook-driven entitlements are the most robust way to keep access control consistent.
- Avoids fragile client-side state.

## Consequences
- Must implement Stripe webhook handling and idempotent updates.
- Route guards must check entitlements consistently.
- Support states like `cancel_at_period_end` without prematurely removing access.

## Sources
- Extracted ADR: `690678ff-6f48-8327-8071-1a446a8b5b87/ADR-0008-architecture.md`
- Supporting billing details (checkout/portal, etc.): `690679e6-f9fc-8331-8cd3-7a010a51731f/ADR-0008-billing.md` (and related billing ADRs)



<!-- FILE: docs/decisions/ADR-0004-pricing-and-packaging.md -->
# ADR-0004: Pricing & packaging — single $15/mo plan + bounded free entry

**Status:** active  
**Date:** 2025-12-24 (steering update; supersedes earlier pricing ADRs)  
**Topic:** pricing

## Context
Earlier pricing experiments included multi-tier and different anchor points. Steering updated the canonical direction to a simpler launch posture.

## Decision
- Offer **one paid plan** at **$15/month**.
- Maintain a clearly bounded free experience:
  - **~30 questions + 1 Readiness Snapshot** (current posture)
- Avoid “AI credits” messaging unless usage is truly enforced and legible.

## Rationale
- Single-plan pricing reduces choice friction at go-live.
- A bounded free entry lets users experience value while preserving conversion incentives.
- Credits-style messaging tends to confuse users unless the product is *actually* metered.

## Consequences
- UI, Stripe product configuration, and entitlement checks should assume **one plan**.
- Any trial behavior is optional and should not be treated as canonical unless explicitly enabled (copy + support + billing behavior aligned).

## Supersedes (historical)
- Prior per-exam subscription hypothesis (e.g., $12/mo, annual $79) and other pricing options explored earlier.
- Any copy or code paths that imply multiple paid tiers without explicit intent.

## Sources
- Extracted “free boundary” ADR: `690678ff-6f48-8327-8071-1a446a8b5b87/ADR-0005-pricing.md`
- Extracted “fewer plans” ADR: `693c3ff6-2c18-832e-a7d6-d48ce7fd5164/ADR-0061-pricing.md`
- Steering decision (chat): canonical price set to **$15/mo**, one plan (2025-12-24)



<!-- FILE: docs/decisions/ADR-0005-human-review-gate-no-auto-publish.md -->
# ADR-0005: Do not auto-publish generated questions (human review gate)

**Status:** active  
**Date:** 2025-11-29 (extracted)  
**Topic:** content_pipeline

## Context
AI-generated questions can hallucinate or be subtly incorrect. Testero’s trust and outcomes depend on preventing low-quality content from reaching learners.

## Decision
Generated questions must **never** be auto-published.
- Insert all generated questions as **DRAFT** and **review_status=UNREVIEWED**
- Require **human review + promotion** before learner visibility

## Rationale
- Prevents “silent correctness failures” from damaging trust.
- Keeps quality consistent while the pipeline and evals mature.

## Consequences
- Adds operational overhead (review queue).
- Slows time-to-live for new content, but improves reliability.

## Sources
- Extracted ADR: `693c3ff6-2c18-832e-a7d6-d48ce7fd5164/ADR-0040-content_pipeline.md`



<!-- FILE: docs/decisions/ADR-0006-only-serve-active-good.md -->
# ADR-0006: Only serve questions that are ACTIVE + GOOD

**Status:** active  
**Date:** 2025-11-27 (extracted)  
**Topic:** quality

## Context
If unreviewed or “needs fix” questions are served in the core practice loop, user trust and learning outcomes degrade quickly.

## Decision
Diagnostics and practice flows must only serve questions where:
- `status = ACTIVE` AND
- `review_status = GOOD`

## Rationale
- Ensures the learner experience is consistently high-quality.
- Avoids “beta-feeling” content during critical learning moments.

## Consequences
- May constrain question availability early; requires graceful handling (fallback domains, smaller pools, or prompting admin review to increase coverage).

## Sources
- Extracted ADR: `691e70a9-2db8-8327-bb4e-83250ca356b4/ADR-0042-quality.md`



<!-- FILE: docs/decisions/ADR-0007-diagnostic-snapshots.md -->
# ADR-0007: Diagnostic sessions snapshot questions for immutability

**Status:** active  
**Date:** 2025-11-19 (extracted)  
**Topic:** architecture / product_flow

## Context
Question content can change over time (fixes, edits, retirements). Diagnostics must remain consistent once a user starts a session.

## Decision
Diagnostic sessions should **snapshot selected questions** into a session-owned structure (rather than reading live from source questions during the session).

## Rationale
- Session immutability: user answers map to the exact question/options shown.
- Avoids correctness drift if the underlying question bank changes mid-session.

## Consequences
- Requires storing enough data in the diagnostic session to evaluate correctness and display review results (not just IDs).
- Allows future edits to source questions without corrupting prior sessions.

## Sources
- Extracted ADR (multiple duplicates): `691e70a9-2db8-8327-bb4e-83250ca356b4/ADR-0011-architecture.md` (and duplicate ADR-0011 variants)



<!-- FILE: docs/decisions/ADR-0008-quality-routing-validation-plus-review.md -->
# ADR-0008: Quality routing via automated validation + human rubric

**Status:** active  
**Date:** 2025-11-01 (extracted), reaffirmed 2025-12-24 (steering)  
**Topic:** evaluation / quality

## Context
We want scalable content creation without sacrificing correctness. Automated validators can catch many issues, but not all; human review remains the final gate.

## Decision
Adopt a two-stage quality system:
1. **Automated validation + scoring** (structure checks, grounded factuality checks, duplication checks where applicable)
2. **Human review** using a consistent rubric before promotion to learner-visible states

## Rationale
- Automated checks reduce reviewer burden and keep standards consistent.
- Human review blocks subtle errors and improves explanations.

## Consequences
- Requires validator outputs to be stored and visible in Admin review UX.
- Requires a consistent rubric definition and reviewer workflow.

## Sources
- Validator routing / scoring direction: `690645ec-7814-832c-8fc1-39cdd8755a3b/ADR-0006-evaluation.md`
- Human-in-loop posture referenced broadly in quality atoms and docs (see `docs/evaluation_quality.md`)



<!-- FILE: docs/decisions/ADR-0009-analytics-posthog.md -->
# ADR-0009: Use PostHog for event tracking (activation + pricing funnels)

**Status:** active  
**Date:** 2025-12-09 (extracted)  
**Topic:** analytics

## Context
Testero needs lightweight, reliable instrumentation to measure activation, retention, and conversion—especially during early launch iterations.

## Decision
Use **PostHog** as the primary event tracking system for:
- onboarding / activation funnel events
- pricing funnel events (pricing view → checkout → purchase → entitlement grant)
- paywall hits (what feature was blocked)

## Rationale
- Enables fast iteration and funnel debugging.
- Keeps analytics centralized and queryable without heavy data engineering.

## Consequences
- Must maintain an event dictionary and consistent naming.
- Must ensure Stripe/webhook-derived “entitlement granted” is tracked server-side.

## Sources
- Extracted ADR: `691e70a9-2db8-8327-bb4e-83250ca356b4/ADR-0051-analytics.md`
- Related onboarding tracking ADR: `6847459e-0918-8005-8e1e-6849fb8481d9/ADR-0004-onboarding.md`



<!-- FILE: docs/decisions/ADR-0010-vectors-future-enhancement.md -->
# ADR-0010: Vectors/embeddings are a future enhancement (not production-wired)

**Status:** active  
**Date:** 2025-12-24 (steering addendum)  
**Topic:** architecture / search

## Context
There have been experiments and design directions involving embeddings (semantic dedupe, retrieval, vector search). Steering clarified that this is not yet part of the production-wired system.

## Decision
Treat vectors/embeddings as a **future enhancement** until:
- a production pipeline is explicitly wired (indexing, retrieval, evals)
- quality + relevance are validated with real usage
- operational costs and failure modes are understood

## Rationale
- Prevents accidental complexity and “half-integrations.”
- Keeps the v1 system grounded in reliable, auditable mechanisms.

## Consequences
- Lexical dedupe can be used now.
- Semantic dedupe, semantic retrieval, and vector-powered adaptivity remain behind flags or are deferred.

## Sources
- Implied vector store considerations appear in architecture ADR alternatives (pgvector mentioned): `68101dc2-9f24-8005-9eb0-25b048e5db84/ADR-0003-architecture.md`
- Steering addendum: vectors should be placed as a future enhancement (2025-12-24)



<!-- FILE: docs/decisions/ADR-0011-pass-or-extend-tbd.md -->
# ADR-0011: “Pass-or-Extend” direction accepted; operational spec & copy TBD

**Status:** draft  
**Date:** 2025-12-24 (steering)  
**Topic:** pricing / policy

## Context
A “Pass-or-Extend” promise was discussed as a trust and conversion lever (if a learner fails, they get additional access). Steering accepted the direction but explicitly noted operational and copy details are not finalized.

## Decision
Proceed with “Pass-or-Extend” as a **direction**, but treat it as **TBD** until:
- operational definition is agreed
- abuse prevention is defined
- support workflow is defined
- customer-facing copy is finalized and consistent with reality

## Rationale
- Can increase trust, but only if it is enforceable and honest.
- Avoids over-claiming before the program is operationally true.

## Consequences
- Do not present as a hard guarantee in marketing copy until spec exists.
- Engineering should not implement automated enforcement until policy details are confirmed.

## Open questions (required to activate)
- What qualifies as “fail”? (self-attestation vs evidence)
- What is the extension length?
- What time window applies?
- What anti-abuse constraints apply?
- How is it requested/fulfilled?

## Sources
- Steering decision: accepted direction; operational and copy language TBD (2025-12-24)
