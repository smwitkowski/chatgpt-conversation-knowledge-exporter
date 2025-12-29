<!-- FILE: docs/evaluation_quality.md -->
# Testero Evaluation & Quality Framework

**Last updated:** 2025-12-25  
**As-of validity anchor:** 2025-12-24 (recommended items may not be validated/confirmed end-to-end as of this date)  
**Audience:** AI engineers + AI assistants contributing to Testero  
**Status:** Canonical + explicitly-marked recommendations

> This document defines how Testero measures and enforces question quality (structure, correctness, grounding, and duplication), and how results flow into the human review pipeline.

---

## 1) Goals

1. Prevent low-quality or incorrect questions from reaching learners.
2. Keep quality enforcement **repeatable, measurable, and auditable**.
3. Enable iteration: validators + evals improve generation quality over time (DSPy optimization loop).
4. Maintain a clear “quality gate” separation: **generation ≠ publication**.  
<!-- source: 691e70a9-2db8-8327-bb4e-83250ca356b4, e73af14d-a283-48a3-b9a6-c3732cd83672 -->

---

## 2) Governance: what is allowed to reach learners

### 2.1 Human-in-the-loop is required (canonical)
Testero uses a **human-in-the-loop SME review process** plus automated validation for question quality control.  
<!-- source: 68101dc2-9f24-8005-9eb0-25b048e5db84, ffaf9d96-9b80-4bc5-8622-9f1fe8c14fe0 -->

### 2.2 No auto-publish (canonical)
Generated questions are inserted into the canonical schema as **DRAFT + review_status=UNREVIEWED** and enter a human review queue; the pipeline **does not auto-publish**.  
<!-- source: 691e70a9-2db8-8327-bb4e-83250ca356b4, e73af14d-a283-48a3-b9a6-c3732cd83672 -->

### 2.3 Eligibility filter (canonical)
Learner-facing selection must be restricted to:
- `status = 'ACTIVE'` **and**
- `review_status = 'GOOD'`  
<!-- source: 691e70a9-2db8-8327-bb4e-83250ca356b4, 28f3acd6-d97b-4008-baf5-95ad579fa540 -->

---

## 3) Status model: separating “delivery state” from “review state”

Keep two orthogonal fields:
- `status`: delivery lifecycle (e.g., DRAFT/ACTIVE/RETIRED)
- `review_status`: audit workflow (e.g., UNREVIEWED/GOOD/NEEDS_ANSWER_FIX/NEEDS_EXPLANATION_FIX/RETIRED)  
<!-- source: 691e70a9-2db8-8327-bb4e-83250ca356b4, 46a5498c-7a33-4d7f-ac2b-022c89ea3c79 -->

This prevents accidental learner exposure due to “published” items that are not quality-cleared.

---

## 4) Validator layers

### 4.1 Layer 0: hard structural validator (canonical requirement)
A hard validator should enforce schema constraints such as:
- exactly 4 options
- exactly 1 correct answer
- length bounds
- basic style checks  
<!-- source: 691e70a9-2db8-8327-bb4e-83250ca356b4, e73af14d-a283-48a3-b9a6-c3732cd83672 -->

> Note: Some extracted requirements mention duplication checks “via embeddings.” Treat semantic/vector checks as a **future enhancement** until vectors are wired into production and validated (see §7.2). (Approved steering addendum.)

### 4.2 Layer 1: grounded factuality validator (canonical direction)
Validator verification flow:
1. Extract **atomic claims** from the question + explanation
2. Retrieve supporting evidence from allow-listed docs
3. Classify each claim as support / contradict / neutral with confidence
4. Aggregate to a final verdict or score  
<!-- source: 690645ec-7814-832c-8fc1-39cdd8755a3b, 977927b0-ca86-46b9-9d1f-c3f44451d838 -->

### 4.3 Layer 2: routing by validator scores (canonical direction)
Use score thresholds on validator outputs to route candidates:
- approve queue if above a high threshold
- fix/reseed if below a low threshold
- thresholds are tunable per environment  
<!-- source: 690645ec-7814-832c-8fc1-39cdd8755a3b, c7ceb316-4139-4086-af23-073f888df968 -->

---

## 5) Review rubric (human QA gate)

Use a **5-point review rubric**; approve if overall score is at least **4** and the item is correct/clear; otherwise Fix or Reject.  
<!-- source: 690678ff-6f48-8327-8071-1a446a8b5b87, ffbeb313-626e-498e-84cd-94fd5ae76234 -->

Recommended rubric dimensions (not yet validated end-to-end as of 2025-12-24):
- Correctness (answer + explanation)
- Realism (scenario plausibility)
- Blueprint alignment (tag matches the concept tested)
- Clarity (no ambiguity, no trick wording)
- Usefulness of explanation (teaches, not just states)

---

## 6) Evals harness (question-level)

### 6.1 `eval_accuracy` module (implemented in experimentation)
The `eval_accuracy` module performs LLM-based factual accuracy evaluation and includes DSPy signatures for query refinement and per-option evaluation.  
<!-- source: 69388fc5-f5a8-8325-92b4-cb90096da1c7, 0604f5d6-7b90-4455-84fb-ec2aaf5d1e38 -->

`eval_accuracy.py` performs Exa-based factual checking using retrieved research context and outputs an LLM verdict (correct / incorrect / uncertain).  
<!-- source: 69388fc5-f5a8-8325-92b4-cb90096da1c7, 3ab2c581-bb7f-4f55-b6e3-ff2af6fdca1f -->

### 6.2 `pmle_question_metric` (implemented in experimentation)
`pmle_metric.py` defines `pmle_question_metric(example, pred)` which includes:
- structural validation (`validate_question`)
- factual evaluation
- and a combined score (described as coarse-grained)  
<!-- source: 69388fc5-f5a8-8325-92b4-cb90096da1c7, 3ab2c581-bb7f-4f55-b6e3-ff2af6fdca1f -->

Treat the current metric as “**more hard checks + factual check**” rather than a final, authoritative measure of question quality.  
<!-- source: 69388fc5-f5a8-8325-92b4-cb90096da1c7, 3ab2c581-bb7f-4f55-b6e3-ff2af6fdca1f -->

---

## 7) Duplication control

### 7.1 Lexical duplication (recommended; low risk to adopt)
Lexical duplicate detection uses a default Jaccard similarity threshold of **0.9** (≥90% token overlap).  
<!-- source: 69388fc5-f5a8-8325-92b4-cb90096da1c7, 0604f5d6-7b90-4455-84fb-ec2aaf5d1e38 -->

### 7.2 Semantic duplication (future enhancement)
Semantic duplicate detection uses a default cosine similarity threshold of **0.85** to catch paraphrases.  
<!-- source: 69388fc5-f5a8-8325-92b4-cb90096da1c7, 0604f5d6-7b90-4455-84fb-ec2aaf5d1e38 -->

**Steering addendum:** semantic/vector-based duplication is a **future enhancement** until vectors are production-wired and validated (as of 2025-12-24).

---

## 8) Batch-level reporting (generation run health)

Proposed batch metrics include:
- `unique_question_ratio = unique_count / total_count`
- `avg_nearest_neighbor_sim` to quantify duplication/overlap  
<!-- source: 69388fc5-f5a8-8325-92b4-cb90096da1c7, 3ab2c581-bb7f-4f55-b6e3-ff2af6fdca1f -->

Recommended additional batch diagnostics (not validated as of 2025-12-24):
- % failing hard structural checks
- % failing factuality checks
- % routed to “Fix” vs “Reject”
- median time-to-approval in Admin review queue
- per-domain coverage (ACTIVE+GOOD counts)

---

## 9) Product-level “quality outcomes” metrics (recommended / not validated)

Success metric targets include (illustrative; not confirmed as of 2025-12-24):
- reported real exam pass rate ≥ 80%
- NPS ≥ 45
- question quality score ≥ 4/5  
<!-- source: 68101dc2-9f24-8005-9eb0-25b048e5db84, ffaf9d96-9b80-4bc5-8622-9f1fe8c14fe0 -->

> These are useful as “directional targets” but require real user data and instrumentation to become authoritative.

---

## 10) Risks & mitigations

### 10.1 Hallucinations & incorrect content
Key risk: AI hallucinations causing incorrect answers. Mitigation includes validator checks and keeping a human QA gate until acceptance thresholds are proven.  
<!-- source: 68101dc2-9f24-8005-9eb0-25b048e5db84, ffaf9d96-9b80-4bc5-8622-9f1fe8c14fe0 -->

### 10.2 Over-claiming “SME reviewed”
There is extracted copy-level content stating questions are “peer-reviewed by certified SMEs.”  
<!-- source: 6803dab6-3548-8005-bad8-b6d803cc1e12, 4ef1702c-00ad-4e81-9d0d-38757ce7cb78 -->

**As-of note (2025-12-24):** Treat this as a **marketing/copy claim** that must be validated operationally (process + evidence) before being treated as factual/authoritative in documentation.

---

## 11) Open questions
- What is the canonical “PMLE question quality rubric” definition (dimensions + scoring anchors)?
- Which validators are mandatory for promotion to `GOOD` vs optional warnings?
- What is the operational definition of “UNCERTAIN” verdicts in factuality checks (block promotion vs allow with caution)?
- When vectors are productionized, what is the desired semantic similarity policy (soft warning vs hard block)?