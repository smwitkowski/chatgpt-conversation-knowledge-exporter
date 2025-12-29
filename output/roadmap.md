<!-- FILE: docs/roadmap.md -->
# Testero Roadmap

**Last updated:** 2025-12-25  
**As-of validity anchor:** 2025-12-24 (items marked “Recommended / Not validated” are not confirmed end-to-end as of this date)  
**Audience:** AI engineers + AI assistants contributing to Testero  
**Status:** Canonical (living doc)

> This roadmap is optimized for a solo builder: ship value, learn fast, and keep the content/quality system credible.

---

## 1) Roadmap principles (how we choose work)

1. **Ship the core learning loop first**: readiness → targeted practice → review → repeat.  
2. **Quality gates before scale**: do not grow a low-quality question bank.  
3. **Establish a workable content pipeline before “Priority 2” expansion.**  
   <!-- source: 6930b629-35bc-832f-8635-55284b1ecc2f, 9fd0f61a-67f3-4583-a2f6-aa2494ca3942 -->
4. **Keep experiments isolated**: vectors/embeddings are future enhancement until production-wired and validated.  
5. **Avoid big rewrites**: iterate the existing Next.js + Supabase + Stripe foundation.

---

## 2) Workstreams

### A) Learner product loop (core)
- Diagnostic (readiness snapshot)
- Practice (targeted questions)
- Practice exam (exam mode)
- Review (explanations + mistakes)
- Study plan (actionable next steps)

### B) Content + quality loop (core)
- Source grounding + ingestion
- Candidate generation
- Automated validation + routing
- Human review in Admin UI
- Publish only `ACTIVE + GOOD`

### C) Monetization + activation
- One plan at **$15/month** (canonical)
- Paywall + entitlements
- “Pass-or-Extend” direction (ops/copy TBD)

### D) Growth (post-foundation)
- SEO + content strategy
- Community distribution (Reddit, etc.)
- Email onboarding + lifecycle nudges

---

## 3) 4-week execution sequence (near-term plan)

> This is the canonical short-horizon execution plan extracted from prior planning decisions and refined to match the current product shape.  
> It is deliberately “boring”: ship the foundation, then the loop, then gating, then acquisition.

### Week 1 — Data foundation + schema hardening
**Objective:** Make the question/diagnostic data model reliable so everything else stacks cleanly.  
<!-- source: 691e248d-5c78-832f-84d7-3ab975e0de1d, 019d0627-599e-45d9-8863-5ca9d5752a50 -->

**Deliverables**
- Clean Supabase schema for questions/answers + diagnostics
- Stable question selection + storage (diagnostic snapshots)
- Minimal “question quality + explanation wiring” complete enough to support review flows  
<!-- source: 691e248d-5c78-832f-84d7-3ab975e0de1d, 019d0627-599e-45d9-8863-5ca9d5752a50 -->

**Exit criteria**
- A diagnostic run can be created, completed, and reviewed without schema hacks
- Diagnostic “domain breakdown” can be computed consistently

---

### Week 2 — Diagnostic + readiness UX (core loop entry)
**Objective:** Make readiness feel real and actionable (not just a quiz).  
**Deliverables**
- Diagnostic UX polished enough for first-time users (start/resume/complete)
- Summary page that:
  - shows domain breakdown
  - recommends next practice focus
  - routes into practice session creation
- Basic empty-states in dashboard

**Exit criteria**
- A new user can go: landing → diagnostic → summary → “what next” in <10 minutes
- PostHog captures the funnel events for this loop

---

### Week 3 — Practice exam mode + analytics reliability
**Objective:** Support “exam-like” experience and meaningful progress tracking.  
**Deliverables**
- Practice test (“exam mode”) behavior:
  - no correctness feedback mid-test
  - explanations appear on results
- Better review UX for missed questions (explanations + rationale)
- Analytics hardening (event dictionary sanity, key funnels stable)

**Exit criteria**
- A user can do a full session and understand performance gaps without confusion
- PostHog funnels for “activation loop” are queryable and stable

---

### Week 4 — Free-vs-paid gating + acquisition loop
**Objective:** Convert users reliably and start controlled growth.  
<!-- source: 6917f618-6938-8326-bb36-43e7419affbe, 8a863bcf-6c6e-419f-b8e6-b3e96a8e7f66 -->
<!-- source: 6930b629-35bc-832f-8635-55284b1ecc2f, 4bed2477-b5f3-4994-ae1d-db122804c7a0 -->

**Deliverables**
- Paywall enforcement + entitlements (Stripe webhooks → Supabase)
- Pricing page aligned to one-plan **$15/mo**
- Acquisition loop starter kit:
  - UTM’d links for community posts
  - basic email onboarding triggers (if enabled)
  - 1–2 “evergreen” landing pages for PMLE intent

**Exit criteria**
- A user can upgrade without friction and immediately see paid value
- Growth activity is measurable (UTM + funnel)

---

## 4) Priority gates (what must be true before expanding scope)

### Gate 1 — “Workable content pipeline” established (required before Priority 2)
Proceed to Priority 2 only after a workable content pipeline exists.  
<!-- source: 6930b629-35bc-832f-8635-55284b1ecc2f, 9fd0f61a-67f3-4583-a2f6-aa2494ca3942 -->

**Minimum definition (v1)**
- Questions have review states (`UNREVIEWED`, `GOOD`, fix states)
- Learner-visible questions are restricted to `ACTIVE + GOOD`
- Admin review workflow exists (even if minimal)
- Ability to add/repair content without destabilizing production

### Gate 2 — “Reliable conversion funnel”
- Pricing → checkout → entitlement grant → paid experience is stable and instrumented

---

## 5) Priority 2 (post-foundation expansion)

> Only begin once Gate 1 is satisfied.

### 5.1 Content engine scale-up (still PMLE-only)
- Improve generation throughput with consistent QC
- Batch-level reports: dedupe, validator fail rates, approval latency
- Expand PMLE domain coverage systematically (coverage gaps report)

### 5.2 Growth scale-up
- SEO program: “PMLE readiness,” “PMLE practice exam,” blueprint-focused pages
- Community: repeatable posting playbook + UTM links
- Email: onboarding sequence and “review mistakes” nudges

### 5.3 Product experience upgrades
- Stronger study plan with spaced repetition cues (Anki-like direction)
- Better progress dashboards (domain trends, weak areas)

---

## 6) Future enhancements (explicitly not wired/validated as of 2025-12-24)

These are valid directions but **not production-wired** yet:
- Vector search / embedding retrieval powering content selection or semantic dedupe
- Sophisticated “adaptive practice” driven by embeddings
- Enterprise / team dashboards and org reporting

---

## 7) Open questions (blockers / high-leverage clarifications)

1. **Pass-or-Extend operational spec** (decision direction accepted; terms/copy TBD)
2. **Trial policy** (if any) for the $15/mo plan
3. **Canonical free boundary** under the one-plan approach:
   - keep “~30 questions + 1 Readiness Snapshot” vs simplify to “1 diagnostic + limited practice”

---

## 8) Next-step implementation format (how to turn this into tickets)

Roadmap items should be converted into Linear issues with:
- single owner
- explicit exit criteria (definition of done)
- dependencies called out (schema, entitlements, analytics)
- “scope guardrails” to prevent overbuilding  
<!-- source: 6930b629-35bc-832f-8635-55284b1ecc2f, df9afbd5-ce0a-4e3c-a968-106e0d6c4e6e -->
