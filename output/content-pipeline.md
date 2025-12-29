````markdown
<!-- FILE: docs/content_pipeline.md -->
# Testero Content Pipeline

**Last updated:** 2025-12-25  
**Audience:** AI engineers + AI assistants contributing to Testero  
**Status:** Canonical (living doc)

> This document describes how Testero sources, generates, validates, reviews, and publishes practice questions.  
> Any section explicitly marked **Recommended / Not validated** reflects proposed direction and has **not** been confirmed end-to-end in production as of **2025-12-24**.

---

## 1) Purpose & scope

Testero’s differentiation depends on **credible, always-fresh practice content** built from a **repeatable pipeline** with **human review** (not “firehose auto-generation”).  
<!-- source: 690678ff-6f48-8327-8071-1a446a8b5b87, ffbeb313-626e-498e-84cd-94fd5ae76234 -->

This doc covers:
- doc discovery + ingestion
- chunking/normalization
- question generation (DSPy/programmatic)
- automated validation + scoring + routing
- human review workflow in Admin UI
- publication + learner visibility rules
- drift monitoring + refresh cadence

---

## 2) Pipeline overview

### 2.1 High-level lifecycle (canonical)

```mermaid
flowchart TD
  A[Source discovery<br/>(doc search, allowlist)] --> B[Ingest + normalize<br/>(scrape → markdown)]
  B --> C[Chunk + annotate<br/>(domain/difficulty metadata)]
  C --> D[Generate candidate questions<br/>(DSPy program)]
  D --> E[Automated validation + scoring<br/>(validators, factuality checks)]
  E --> F[Dedupe<br/>(lexical, optional semantic)]
  F --> G[Insert as DRAFT + UNREVIEWED]
  G --> H[Admin review workflow]
  H --> I{Approve?}
  I -- yes --> J[Promote to ACTIVE + GOOD]
  I -- no --> K[Revise / Reseed / Retire]
  J --> L[Learner-visible selection]
````

Key governance decision: **never auto-publish generated questions**. All generated items must land as **DRAFT + UNREVIEWED** and require human promotion before learners can see them.

<!-- source: 691e70a9-2db8-8327-bb4e-83250ca356b4, e73af14d-a283-48a3-b9a6-c3732cd83672 -->

### 2.2 Minimal generation pipeline (P1 / v0.5)

The minimal PMLE generation pipeline:

* takes doc-grounded chunks as input
* outputs: question stem, 4 options (exactly one correct), explanation/rationale
* stores metadata including **doc URLs used** + attributes like domain/difficulty and a `source_run_id`.

<!-- source: 691e70a9-2db8-8327-bb4e-83250ca356b4, e73af14d-a283-48a3-b9a6-c3732cd83672 -->

---

## 3) Inputs & sourcing

### 3.1 Authoritative sources (canonical posture)

* Primary grounding sources are official documentation (e.g., Google Cloud docs for PMLE).
* Content must be traceable: store citations/URLs for what a question is grounded in.

<!-- source: 690678ff-6f48-8327-8071-1a446a8b5b87, ffbeb313-626e-498e-84cd-94fd5ae76234 -->

### 3.2 Doc discovery + scraping (implemented in experimentation)

Doc retrieval approach:

* Use a doc search module to find relevant Google Cloud docs (restricted to `docs.cloud.google.com`), then scrape the page content into markdown (rather than extracting full content via search results directly).

<!-- source: 69388fc5-f5a8-8325-92b4-cb90096da1c7, 0604f5d6-7b90-4455-84fb-ec2aaf5d1e38 -->

Scraping details:

* Firecrawl extraction targets the article body via selector `**.devsite-article-body`.

<!-- source: 69388fc5-f5a8-8325-92b4-cb90096da1c7, 0604f5d6-7b90-4455-84fb-ec2aaf5d1e38 -->

Governance requirement:

* Crawlers must respect `robots.txt`, rate limits, and content licenses; avoid storing proprietary content directly—store pointers/metadata and citations with link-outs.

<!-- source: 690645ec-7814-832c-8fc1-39cdd8755a3b, 977927b0-ca86-46b9-9d1f-c3f44451d838 -->

---

## 4) Question generation architecture

### 4.1 DSPy program structure (canonical direction)

A DSPy program exists (e.g., `PMLEQuestionProgram`) that performs:

* search/retrieval → gap analysis → generation → validation loop
* then dedupe + factual evaluation

<!-- source: 69388fc5-f5a8-8325-92b4-cb90096da1c7, 0604f5d6-7b90-4455-84fb-ec2aaf5d1e38 -->

### 4.2 Separation of generator vs validator (recommended / consistent with ADR posture)

Use separate generator and validator components so the system can:

* propose candidates quickly,
* evaluate them consistently,
* route them based on quality signals, and
* keep “review gates” explicit.

<!-- source: 690645ec-7814-832c-8fc1-39cdd8755a3b, ed4e4493-9d79-4cec-9476-c184cb9ae805 -->

> **Recommended / Not validated as of 2025-12-24:** Full multi-service split (Next.js + Node API + Python microservices) for generator/validator/crawler is a direction, not a hard dependency for v1.

---

## 5) Automated quality control & routing

### 5.1 Human-in-the-loop is required (canonical)

Testero uses **human-in-the-loop SME review** plus **automated validation** for question QC.

<!-- source: 68101dc2-9f24-8005-9eb0-25b048e5db84, ffaf9d96-9b80-4bc5-8622-9f1fe8c14fe0 -->

### 5.2 Quality scoring + routing thresholds (canonical decision)

Route candidates based on `quality_score` thresholds (e.g., approve / human-review / reseed-rework), with thresholds configurable by environment.

<!-- source: 690645ec-7814-832c-8fc1-39cdd8755a3b, ed4e4493-9d79-4cec-9476-c184cb9ae805 -->

Example threshold concept (illustrative, adjustable):

* `>= 0.90` → ready for human approval queue (fast path)
* `0.60–0.89` → needs review + edits
* `< 0.60` → reseed/rework

<!-- source: 690645ec-7814-832c-8fc1-39cdd8755a3b, ed4e4493-9d79-4cec-9476-c184cb9ae805 -->

---

## 6) Dedupe strategy

### 6.1 Canonical posture

The system includes deduplication utilities combining:

* **lexical** duplicate detection (e.g., normalized stems + token overlap/Jaccard)
* **semantic** duplicate detection via cosine similarity on embeddings

<!-- source: 69388fc5-f5a8-8325-92b4-cb90096da1c7, 0604f5d6-7b90-4455-84fb-ec2aaf5d1e38 -->

### 6.2 Operational addendum (steering)

**Semantic/embedding-based dedupe should be treated as a future enhancement** until embeddings are explicitly wired into the production pipeline and validated.
(Approved steering addendum from this thread.)

> Practical guidance: keep lexical dedupe always-on; enable semantic dedupe behind a flag once embeddings are productionized.

---

## 7) Review workflow & publication rules

### 7.1 Status vs review workflow (canonical decision)

Separate **delivery status** from **review status**:

* `status`: delivery lifecycle (e.g., ACTIVE, etc.)
* `review_status`: audit workflow (e.g., UNREVIEWED / GOOD / NEEDS_ANSWER_FIX / NEEDS_EXPLANATION_FIX / RETIRED)

<!-- source: 6930b629-35bc-832f-8635-55284b1ecc2f, 46a5498c-7a33-4d7f-ac2b-022c89ea3c79 -->

### 7.2 Learner-visible selection (canonical decision)

Diagnostic/practice question selection must be restricted to:

* `status = 'ACTIVE'` AND `review_status = 'GOOD'`

<!-- source: 6930b629-35bc-832f-8635-55284b1ecc2f, 46a5498c-7a33-4d7f-ac2b-022c89ea3c79 -->

### 7.3 Admin UI is the control plane (canonical decision)

The **Admin UI** is the primary interface for:

* reviewing generated questions
* editing/reseeding candidates
* promoting questions to learner-visible states

<!-- source: 6930b629-35bc-832f-8635-55284b1ecc2f, f2c8fe85-26a6-416e-aacd-4d7b795e1c55 -->

---

## 8) Data model expectations (pipeline-facing)

Minimum metadata the pipeline should persist per generated candidate (canonical expectation):

* stem/options/correct/explanation
* doc URLs used (citations)
* domain + difficulty
* `source_run_id` (for batch traceability)
* validator outputs + `quality_score`
* review workflow fields (review_status, notes, approver metadata)

<!-- source: 691e70a9-2db8-8327-bb4e-83250ca356b4, e73af14d-a283-48a3-b9a6-c3732cd83672 -->

<!-- source: 690645ec-7814-832c-8fc1-39cdd8755a3b, ed4e4493-9d79-4cec-9476-c184cb9ae805 -->

> See also: `docs/evaluation_quality.md` for validator composition and metrics, and `docs/architecture.md` for database + service boundaries.

---

## 9) Drift monitoring & refresh cadence

### 9.1 Exam drift risk (canonical risk + mitigation direction)

Risk: certification exams drift, causing outdated content.
Mitigation direction includes a **weekly delta scan crawler on allow-listed docs** and flagging blueprint diffs.

<!-- source: 690678ff-6f48-8327-8071-1a446a8b5b87, ffbeb313-626e-498e-84cd-94fd5ae76234 -->

### 9.2 Blueprint tracking (recommended / not implemented)

An “Exam Blueprint Tracker” is a marketing/content concept and can also support drift monitoring, but **it is not implemented** as of now.

<!-- source: 6918d983-3e50-832c-bf02-2e79553dc5cf, fcef8adc-09bc-4f91-bd3d-e1e48d96a2ad -->

**Recommended / Not validated as of 2025-12-24:**

* monthly blueprint refresh job (diff + alerts)
* generate “coverage gaps” report by domain/difficulty and trigger generation runs

---

## 10) Experimental components & future enhancements (explicitly non-canonical)

### 10.1 Embeddings (experimental)

An embeddings module exists that generates embeddings using OpenAI `text-embedding-3-small` (1536-d).

<!-- source: 69388fc5-f5a8-8325-92b4-cb90096da1c7, 0604f5d6-7b90-4455-84fb-ec2aaf5d1e38 -->

**Steering note:** embeddings/vectors are a **future enhancement** until wired into production (retrieval, semantic dedupe, clustering, etc.). (Approved steering addendum from this thread.)

### 10.2 Retrieval augmentation (recommended)

* Use doc-grounded retrieval for factuality checks and citations
* enforce domain allowlists for sources

<!-- source: 69388fc5-f5a8-8325-92b4-cb90096da1c7, 0604f5d6-7b90-4455-84fb-ec2aaf5d1e38 -->

---

## 11) Open questions

* What is the minimum “Admin review” UX to make approvals fast but auditable (bulk actions, diff views, validator summaries)?
* What are the canonical validator set + weights that drive `quality_score`?
* What is the operational definition of “Pass or Extend” as it impacts content cadence and content guarantees? (Decision exists, operational/copy TBD.)
* What is the definitive storage posture for scraped content (full text vs snippets vs pointers) under licensing constraints?