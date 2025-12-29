<!-- FILE: docs/product_prd.md -->

# Testero Product Requirements Document (PRD)

**Last updated:** 2025-12-24
**Status:** Canonical (living doc)
**Audience:** AI engineers + AI assistants contributing to Testero

## 1. Purpose

This PRD defines the **v1 product requirements** for Testero: scope, user journeys, functional requirements, monetization, analytics, and open questions.

## 2. Product definition

**Testero** is an **AI-powered exam-prep platform**. <!-- source: 6803d6a2-9950-8005-ad25-816de069e880, de01a96f-8f29-44c7-8b80-17d7306bad4d -->
More specifically: it is a **certification readiness platform** that helps users understand **how prepared they are** and **what to focus on next**. <!-- source: 6917f4c6-69d4-8005-a651-979d1420ff30, 811b0d51-2246-409b-a6c7-266f60caa29d -->

Testero’s core idea includes **AI-generated practice questions**, **personalized study plans** based on performance, and **continuous updates when exam blueprints change**. <!-- source: 6917f4c6-69d4-8005-a651-979d1420ff30, fce1d4b1-88d0-4207-ae22-e2b7cf2f8640 -->

## 3. Problem statement

Testero targets candidate pain such as:

* Excessive time spent on outdated or fragmented resources
* Low confidence that practice questions match the real exam
* Limited feedback loops on readiness and next steps <!-- source: 68101dc2-9f24-8005-9eb0-25b048e5db84, ffaf9d96-9b80-4bc5-8622-9f1fe8c14fe0 -->

## 4. Scope (v1)

### In scope

* **PMLE-only wedge** (Google Professional Machine Learning Engineer) as the initial exam offering. <!-- source: 693c3ff6-2fa0-800f-89a2-fe6a2468e3e7, 2f0986b4-4515-4737-8b17-524c7cc6cbaa --> <!-- source: 693c3ff6-2fa0-800f-89a2-fe6a2468e3e7, 28454b23-fc03-40c1-991d-dd85129747dc -->
* Web app experience (desktop + mobile responsive). <!-- source: 6803d6a2-9950-8005-ad25-816de069e880, 0a19ae9f-edf6-41d5-989a-d940b99ab9be -->
* Post-session review + study planning (no “live advantage” framing). <!-- source: 6847459e-0918-8005-8e1e-6849fb8481d9, b6f7aa29-16a4-4eff-9350-6ce25ccf0a8f -->

### Explicitly out of scope (v1)

* Enterprise features (RBAC, SSO, org dashboards) are future-facing. <!-- source: 68288f55-f6dc-8005-b4b3-d4c47ca9e4b4, 9c02652d-539d-4215-beee-7858491f326b -->
* Native iOS/Android apps and Slack/Teams integrations are **ideas** unless explicitly scheduled. <!-- source: 691e70a9-2db8-8327-bb4e-83250ca356b4, 0a19ae9f-edf6-41d5-989a-d940b99ab9be -->

## 5. Current state (implemented vs planned)

> **Note:** Several items below are **recommended** rather than validated/confirmed as of **2025-12-24** (see §13).

### Implemented (based on extracted status)

* Marketing landing + waitlist exists with PostHog tracking. <!-- source: 680a717d-949c-800d-b702-2c595e535062, 49c4b2c3-e217-49c0-8660-8ba0147ebfcc -->
* Stripe billing/account plumbing exists (env vars + webhooks). <!-- source: 6910be7c-8c04-8005-b79f-2b182b7dd8e9, 5d39d442-347c-4ac0-bf93-b56d35b78f1a -->
* PostHog pageview tracking is implemented via a provider component; event tracking is instrumented across pages. <!-- source: 6847459e-0918-8005-8e1e-6849fb8481d9, 18b0ea04-8745-49a0-90ad-643af8205256 -->
* Practice Test page behaves closer to exam mode: no correctness feedback during the test; explanations appear on results. <!-- source: 69235600-e4a8-832c-976d-eb2ca13eafcc, 8a169087-8fff-4015-a711-48ec1515370f -->

### Not implemented / gaps

* No implemented in-prod pipeline to generate new practice questions; app assumes existing questions in Supabase. <!-- source: 6910be7c-8c04-8005-b79f-2b182b7dd8e9, 5d39d442-347c-4ac0-bf93-b56d35b78f1a -->
* Vector search / embedding retrieval is experimental and not wired up. <!-- source: 6848152d-0370-8005-8163-09cf445fc601, ed459401-546e-4d06-9645-35aefb31c713 -->

## 6. Primary user personas

### Persona A — Individual candidate (primary)

Busy professional paying out-of-pocket who wants:

* A fast readiness signal
* A focused study plan
* High-quality explanations <!-- source: 6917f4c6-69d4-8005-a651-979d1420ff30, 3f670fe4-acde-4c44-97a9-223d08040fc3 -->

### Persona B — Team / org (future)

Engineering L&D / consulting org tracking readiness and pass rates. <!-- source: 6917f4c6-69d4-8005-a651-979d1420ff30, 3f670fe4-acde-4c44-97a9-223d08040fc3 -->

## 7. User journeys

### Journey 1 — Activation (“aha moment”)

1. Landing → diagnostic CTA. <!-- source: 690679e6-9ac8-8005-86b6-bdfe2d65e4bf, 234bd1a4-a7b4-4b5c-aa5a-3a5788a8e806 -->
2. Diagnostic (anonymous allowed) → answer PMLE-aligned questions. <!-- source: 6906c5d0-acde-8005-98d3-2c5ea35ba439, ec93e8fc-61c4-4a71-9714-cc080bb08c78 -->
3. Results summary → domain breakdown + recommended next steps. <!-- source: 6906c5d0-acde-8005-98d3-2c5ea35ba439, e75347a6-acde-4fdf-bfe8-acde2cbc8504 -->
4. Practice sessions targeting weak domains → review explanations. <!-- source: 691e70a9-2db8-8327-bb4e-83250ca356b4, d62e86ab-2524-4292-b174-acde633afc7b -->

### Journey 2 — Convert to paid

1. User hits a value boundary (e.g., deeper explanations, unlimited practice, study plan). <!-- source: 691e70a9-2db8-8327-bb4e-83250ca356b4, 9c02652d-539d-4215-beee-7858491f326b -->
2. Paywall explains benefits + pricing; backend enforces entitlements. <!-- source: 690679e6-9ac8-8005-86b6-bdfe2d65e4bf, 234bd1a4-a7b4-4b5c-aa5a-3a5788a8e806 -->
3. Stripe checkout → unlock. <!-- source: 690679e6-9ac8-8005-86b6-bdfe2d65e4bf, 234bd1a4-a7b4-4b5c-aa5a-3a5788a8e806 -->

### Journey 3 — Ongoing learning

1. Return for targeted practice sessions and periodic diagnostics. <!-- source: 691e70a9-2db8-8327-bb4e-83250ca356b4, bc9cf6b7-49c6-47c5-8f63-9f0f0908f38c -->
2. Study plan evolves based on performance. <!-- source: 6917f4c6-69d4-8005-a651-979d1420ff30, fce1d4b1-88d0-4207-ae22-e2b7cf2f8640 -->

## 8. Functional requirements (v1)

### 8.1 Authentication & accounts

* Provide a secure, rate-limited API path for Supabase auth flows with clean JSON success/error semantics. <!-- source: 6847459e-0918-8005-8e1e-6849fb8481d9, 8cc313e0-acde-4b44-a45e-acde23c852c0 -->
* Support anonymous diagnostic sessions (v1) that can be resumed. <!-- source: 6906c5d0-acde-8005-98d3-2c5ea35ba439, 6420a08d-acde-4141-9490-acde1f23a27e -->

### 8.2 Diagnostic

* Diagnostic uses canonical question schema (or a constrained snapshot of it) and stays “v1-solid”. <!-- source: 6906c5d0-acde-8005-98d3-2c5ea35ba439, ec93e8fc-61c4-4a71-9714-cc080bb08c78 -->
* Diagnostic and diagnostic/practice selection must be restricted to the **PMLE blueprint**. <!-- source: 6906c5d0-acde-8005-98d3-2c5ea35ba439, b41df5b3-acde-47f1-8b1c-acde1c6dff33 -->
* Create results summary route: `/diagnostic/[id]/summary`. <!-- source: 6906c5d0-acde-8005-98d3-2c5ea35ba439, e75347a6-acde-4fdf-bfe8-acde2cbc8504 -->
* On completion, clear local storage session ID used for resuming anon sessions. <!-- source: 6906c5d0-acde-8005-98d3-2c5ea35ba439, 4c0a7f19-acde-4a15-8342-acde0ad89462 -->

**Data model requirement**

* Snapshot diagnostic questions with domain metadata so domain stats remain stable even as canonical questions evolve. <!-- source: 6930b629-acde-8005-ac66-69d507eae7d7, 09bd46ea-acde-4aa1-9c2c-acde975fc0ed -->

### 8.3 Practice questions & sessions

* Support ad-hoc practice questions (one-by-one), with explanations and review UX. <!-- source: 691e70a9-2db8-8327-bb4e-83250ca356b4, d62e86ab-2524-4292-b174-acde633afc7b -->
* Diagnostic summary CTAs route into practice/session flows. <!-- source: 691e70a9-2db8-8327-bb4e-83250ca356b4, 93906c7a-acde-42a0-99b8-acde92931650 -->
* Dashboard handles empty states (no diagnostics yet) with clear next actions. <!-- source: 690679e6-9ac8-8005-86b6-bdfe2d65e4bf, 72edb28c-acde-4b9c-ac1a-acde49149fa7 -->

### 8.4 Practice exam (“exam mode”)

* Practice Test page behaves closer to exam mode: no correctness feedback during the test; explanations appear on results. <!-- source: 69235600-e4a8-832c-976d-eb2ca13eafcc, 8a169087-8fff-4015-a711-48ec1515370f -->
* Exam mode results should align with diagnostic/practice domain tracking (schema compatibility). <!-- source: 6930b629-acde-8005-ac66-69d507eae7d7, 09bd46ea-acde-4aa1-9c2c-acde975fc0ed -->

### 8.5 Study plan

* Diagnostic summary: disable “Start Study Plan” if one already exists for that diagnostic. <!-- source: 68914d16-acde-8005-8c77-7231783b3e65, d3b67ce4-acde-4b00-a97f-acde751c4f09 -->
* Provide internal endpoint to prefill a study plan from diagnostic results (`diagnosticId`) returning domain performance + recommended focus areas. <!-- source: 68914d16-acde-8005-8c77-7231783b3e65, dbd25a31-acde-4f1e-9d19-acde342f3990 -->

### 8.6 Feedback & iteration loop (v1-lightweight)

* System should improve via user feedback (e.g., flag confusing questions) and admin fixes. <!-- source: 68101dc2-9f24-8005-9eb0-25b048e5db84, ffaf9d96-9b80-4bc5-8622-9f1fe8c14fe0 -->

### 8.7 Billing, paywall, and entitlements

**Canonical packaging (as of 2025-12-24)**

* **One plan:** **$15/month**.

  <!-- source: steering-confirmation, 2025-12-24 -->

  Earlier discussions treated $15 as a candidate price point. <!-- source: 693c3fd0-2fa0-800f-a4ba-15a53168da33, e730f543-d94a-467c-8d56-ecb1c17063a8 -->

**Paywall behavior**

* When blocked, show paywall UI with upgrade CTA + benefits + pricing; API routes return `403` with JSON code `PAYWALL`. <!-- source: 690679e6-9ac8-8005-86b6-bdfe2d65e4bf, 234bd1a4-a7b4-4b5c-aa5a-3a5788a8e806 -->

**Billing data model**

* Supabase billing schema exists with core tables, RLS, indexes, and FK relationships to `auth.users`. <!-- source: 6910be7c-8c04-8005-b79f-2b182b7dd8e9, 138b8665-acde-4dfe-acde-bccc244f9f17 -->

### 8.8 Analytics & instrumentation

* Instrument the funnel: Landing → diagnostic → summary → upgrade → Stripe checkout. <!-- source: 690679e6-9ac8-8005-86b6-bdfe2d65e4bf, 234bd1a4-a7b4-4b5c-aa5a-3a5788a8e806 -->
* Add PostHog events for the diagnostic loop (start/resume/summary view). <!-- source: 6847459e-0918-8005-8e1e-6849fb8481d9, 66315078-b1f3-4f06-9150-e728dc60777d -->

## 9. Non-functional requirements

### 9.1 Performance & UX clarity

* Keep “time-to-first-question” low and avoid overwhelming users during the first session. (Derived from activation focus.) <!-- source: 690679e6-9ac8-8005-86b6-bdfe2d65e4bf, 234bd1a4-a7b4-4b5c-aa5a-3a5788a8e806 -->

### 9.2 Security, compliance, and truthfulness

* Do not claim “official endorsement” or similar compliance/certification claims without evidence. <!-- source: 6847459e-0918-8005-8e1e-6849fb8481d9, b6f7aa29-16a4-4eff-9350-6ce25ccf0a8f -->
* Do not publish unverified proof metrics/testimonials as facts; treat as placeholders until verified. <!-- source: 691e70a9-2db8-8327-bb4e-83250ca356b4, 279a724a-acde-4e62-acde-d3f864a5b0b4 --> <!-- source: 691e70a9-2db8-8327-bb4e-83250ca356b4, 279a724a-acde-4e62-acde-d3f864a5b0b4 -->

## 10. Success metrics (recommended targets)

> **Recommended, not validated as of 2025-12-24.** <!-- source: 691e70a9-2db8-8327-bb4e-83250ca356b4, 84549a99-acde-457f-acde-86a5877d38cd -->

* Waitlist → active conversion (definition of “active” TBD). <!-- source: 691e70a9-2db8-8327-bb4e-83250ca356b4, 84549a99-acde-457f-acde-86a5877d38cd -->
* Question quality score ≥ 4.0/5. <!-- source: 691e70a9-2db8-8327-bb4e-83250ca356b4, 84549a99-acde-457f-acde-86a5877d38cd -->
* Exam pass rate ≥ 80% (only once pass-rate data exists). <!-- source: 691e70a9-2db8-8327-bb4e-83250ca356b4, 84549a99-acde-457f-acde-86a5877d38cd -->

## 11. Dependencies & implementation notes

* Frontend stack: Next.js + Supabase auth; UI components via shadcn/ui. <!-- source: 6847459e-0918-8005-8e1e-6849fb8481d9, 0ae31da8-acde-4ac7-acde-f3309bf01b47 -->
* Content pipeline: conceptually defined, but production integration for ongoing generation/validation is not complete. <!-- source: 6910be7c-8c04-8005-b79f-2b182b7dd8e9, 5d39d442-347c-4ac0-bf93-b56d35b78f1a -->
* Vector search / embeddings: **future enhancement only** (experimented; not wired up). <!-- source: 6848152d-0370-8005-8163-09cf445fc601, ed459401-546e-4d06-9645-35aefb31c713 -->

  <!-- source: steering-confirmation, 2025-12-24 -->

## 12. Superseded decisions (record)

These concepts exist in ADR history but are **not canonical** after the 2025-12-24 steering decisions:

* “Exam-cycle / time-boxed packages” positioning (vs subscription). <!-- source: ADR-0066, 2025-12-10 -->
* Multi-option packages ($69/$99/$199) and/or $39/month secondary pricing. <!-- source: ADR-0068, 2025-12-10 -->

Keep ADRs for historical context; do not implement without an explicit re-decision.

## 13. Unvalidated / recommended items as of 2025-12-24

Include for completeness, but treat as **recommended** (not confirmed or externally verifiable):

* “Proof” marketing metrics (confidence uplift, study hour reduction). <!-- source: 691e70a9-2db8-8327-bb4e-83250ca356b4, 279a724a-acde-4e62-acde-d3f864a5b0b4 -->
* Testimonials displayed in marketing. <!-- source: 691e70a9-2db8-8327-bb4e-83250ca356b4, 279a724a-acde-4e62-acde-d3f864a5b0b4 -->
* “Pass-or-Extend” guarantee: direction accepted, but operational terms + copy are TBD. <!-- source: 691e70a9-2db8-8327-bb4e-83250ca356b4, 279a724a-acde-4e62-acde-d3f864a5b0b4 -->

  <!-- source: steering-confirmation, 2025-12-24 -->
* Free trial / cancellation flow specifics (if any) for the $15/month plan. <!-- source: 691e70a9-2db8-8327-bb4e-83250ca356b4, 279a724a-acde-4e62-acde-d3f864a5b0b4 -->

## 14. Open questions (v1)

Top priority:

* What are the exact “Pass-or-Extend” operational rules and customer-facing copy? <!-- source: 691e70a9-2db8-8327-bb4e-83250ca356b4, 279a724a-acde-4e62-acde-d3f864a5b0b4 -->
* Should a free trial exist for the $15/month plan, and what is the cancellation flow? <!-- source: 691e70a9-2db8-8327-bb4e-83250ca356b4, 279a724a-acde-4e62-acde-d3f864a5b0b4 -->
* What are the minimal content quality gates before a question is eligible for diagnostic/practice? <!-- source: 6917f4c6-69d4-8005-a651-979d1420ff30, fce1d4b1-88d0-4207-ae22-e2b7cf2f8640 -->
* Which planned integrations (Slack/Teams, iOS/Android) are roadmap commitments vs backlog ideas? <!-- source: 691e70a9-2db8-8327-bb4e-83250ca356b4, 0a19ae9f-edf6-41d5-989a-d940b99ab9be -->