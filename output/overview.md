<!-- FILE: docs/overview.md -->
# Testero Overview

> **Audience:** AI assistants and AI engineers working on Testero  
> **Last updated:** 2025-12-24

## Canonical snapshot (current truth)

- **Exam scope:** **Google Professional Machine Learning Engineer (PMLE)** only.  
  <!-- source: steering-confirmation, 2025-12-24 -->
- **Offer:** **One plan** — **$15/month**.  
  <!-- source: steering-confirmation, 2025-12-24 -->
- **Risk reversal:** **Pass-or-Extend** (operational workflow + copy language are **TBD**).  
  <!-- source: steering-confirmation, 2025-12-24 -->
- **Retrieval / vectors:** **Not production-wired**; prior work is **experimental only** and considered a **future enhancement**.  
  <!-- source: steering-confirmation, 2025-12-24 -->
- **Analytics:** **PostHog** is the canonical product analytics system.  
  <!-- source: steering-confirmation, 2025-12-24 -->

> Note: Earlier extracted decisions mention broader exam scope (PMLE + ACE) and higher price anchors ($39/$40). Those are **superseded** by the canonical snapshot above.  
> <!-- source: steering-confirmation, 2025-12-24 -->

## What Testero is

Testero is an AI-powered exam prep product focused on helping learners become “exam ready” through:

- **Scenario-based practice questions**  
  <!-- source: 6803d6a2-9950-8005-ad25-816de069e880, de01a96f-53e9-48c9-97c5-8e394fd15587 -->
- **High-quality explanations** that teach, not just score  
  <!-- source: 6803d6a2-9950-8005-ad25-816de069e880, 1e805ad7-72a2-448b-af59-223d412e6180 -->
- **Adaptive study planning** based on user performance  
  <!-- source: 6803d6a2-9950-8005-ad25-816de069e880, 0a19ae9f-edf6-41d5-989a-d940b99ab9be -->

The current product scope provides a diagnostic and practice workflow for the **Google PMLE** exam.  
<!-- source: 68914ecd-2234-8330-ba6e-f98886c44bf4, 6c49171f-9746-4fa7-8493-3a2e4196f35f -->

## Who it’s for (and not for)

### Primary ICP (now)
**Individual professionals** preparing for certification exams, typically paying out-of-pocket.  
<!-- source: 6803d6a2-9950-8005-ad25-816de069e880, 0a19ae9f-edf6-41d5-989a-d940b99ab9be -->

### Secondary ICP (later)
**Teams / consulting orgs** that want upskilling + progress tracking.  
<!-- source: 6803d6a2-9950-8005-ad25-816de069e880, 0a19ae9f-edf6-41d5-989a-d940b99ab9be -->

### Not-for-now
- “Official” or provider-endorsed positioning (do **not** imply endorsement).  
  <!-- source: 693c3ff6-2c18-832e-a7d6-d48ce7fd5164, 67f0c06a-a10b-4e44-a2ee-9226a6c23c18 -->
- Real-time assistance / anything that resembles cheating automation (Testero is practice + review).  
  <!-- source: 6803d6a2-9950-8005-ad25-816de069e880, 0a19ae9f-edf6-41d5-989a-d940b99ab9be -->

## Core product loop (conceptual)

1. **Diagnostic** (baseline readiness + gaps)  
2. **Study plan** (prioritized topics / spacing)  
3. **Practice** (questions + full practice exams)  
4. **Review** (mistakes → explanations → next recommended work)  
5. Repeat until confidence and performance stabilize

This loop is the “center of gravity” for PRD, architecture, content pipeline, and analytics.  
<!-- source: 6803d6a2-9950-8005-ad25-816de069e880, 0a19ae9f-edf6-41d5-989a-d940b99ab9be -->

## Product principles (guardrails)

- **Quality > quantity:** realistic questions + strong explanations beat a massive static bank.  
  <!-- source: 6803d6a2-9950-8005-ad25-816de069e880, 1e805ad7-72a2-448b-af59-223d412e6180 -->
- **Blueprint alignment:** content should map to exam blueprint areas and stay current.  
  <!-- source: 6803d6a2-9950-8005-ad25-816de069e880, 0a19ae9f-edf6-41d5-989a-d940b99ab9be -->
- **Personalization is the differentiator:** adapt what’s served based on performance.  
  <!-- source: 6803d6a2-9950-8005-ad25-816de069e880, 0a19ae9f-edf6-41d5-989a-d940b99ab9be -->
- **No unverified proof points:** avoid fabricated pass rates / ratings / confidence deltas.  
  <!-- source: 693c3ff6-2c18-832e-a7d6-d48ce7fd5164, 67f0c06a-a10b-4e44-a2ee-9226a6c23c18 -->

## Pricing & guarantee (current)

### Pricing
Testero is currently sold as a **single plan** priced at **$15/month**.  
<!-- source: steering-confirmation, 2025-12-24 -->

### Guarantee: Pass-or-Extend
The product intends to offer a **Pass-or-Extend** risk reversal. Specific conditions, verification, and operational workflow are **TBD** and must be defined before finalizing copy.  
<!-- source: steering-confirmation, 2025-12-24 -->

> Implementation note: this likely implies we need a minimal way to record an exam attempt window + user-reported outcome, plus a support/admin process.  
> <!-- source: editorial-inference, 2025-12-24 -->

## What’s “future enhancement” (explicitly)

- **Vectors / retrieval / RAG grounding:** research exists, but not wired into production. Treat as a later architecture milestone, not a current dependency.  
  <!-- source: steering-confirmation, 2025-12-24 -->
- Additional certifications beyond PMLE (ACE, AWS, Azure, PMP, etc.).  
  <!-- source: steering-confirmation, 2025-12-24 -->

## Success metrics (high level)

North Star metrics by growth stage:

- **Launch → PMF:** **Weekly Active Users (WAU)**  
  <!-- source: 6918039f-21f8-832a-b8ad-6950cec4c3d1, 3a6d2c5c-4425-4a1b-8f88-9a7d8a8e1b1d -->
- **Scaling B2C:** **Net New MRR**  
  <!-- source: 6918039f-21f8-832a-b8ad-6950cec4c3d1, 3a6d2c5c-4425-4a1b-8f88-9a7d8a8e1b1d -->
- **Enterprise expansion:** **Pilot-to-paid conversion**  
  <!-- source: 6918039f-21f8-832a-b8ad-6950cec4c3d1, 3a6d2c5c-4425-4a1b-8f88-9a7d8a8e1b1d -->

Supporting funnel (conceptual): signup → diagnostic start → diagnostic complete → first practice → repeat usage → subscription/retention.  
<!-- source: 6918039f-21f8-832a-b8ad-6950cec4c3d1, 3a6d2c5c-4425-4a1b-8f88-9a7d8a8e1b1d -->

## Where to look next (doc map)

- Definitions and canonical terms: [`docs/glossary.md`](./glossary.md)
- Ideal customer profile and positioning boundaries: [`docs/icp.md`](./icp.md)
- Product requirements and flows: [`docs/product_prd.md`](./product_prd.md)
- System design and integrations: [`docs/architecture.md`](./architecture.md)
- Content sourcing → generation → QC → updates: [`docs/content_pipeline.md`](./content_pipeline.md)
- Quality framework + evals: [`docs/evaluation_quality.md`](./evaluation_quality.md)
- Instrumentation + KPIs: [`docs/analytics_metrics.md`](./analytics_metrics.md)
- Pricing, entitlements, and guarantee mechanics: [`docs/pricing_packaging.md`](./pricing_packaging.md)
- Growth channels, SEO, email: [`docs/marketing_growth.md`](./marketing_growth.md)
- Phased plan and milestones: [`docs/roadmap.md`](./roadmap.md)
- Security/privacy posture: [`docs/security_privacy.md`](./security_privacy.md)

## Decision records (ADRs)

Canonical decisions live in `decisions/` (deduplicated ADR set). Earlier extracted ADRs referencing broader exam scope exist and should be marked **superseded** where they conflict with the canonical snapshot.  
<!-- source: 68101dc2-9f24-8005-9eb0-25b048e5db84, ffaf9d96-9b80-4bc5-8622-9f1fe8c14fe0 -->
