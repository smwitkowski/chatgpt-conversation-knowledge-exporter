<!-- FILE: docs/glossary.md -->
# Testero Glossary

> **Audience:** AI assistants and AI engineers working on Testero  
> **Last updated:** 2025-12-24  
> **Conventions:**
> - Terms marked **(Planned)** are intended/marketed but **not validated or confirmed in production** as of **2025-12-24**.
> - Terms marked **(Future enhancement)** are explicitly *not* wired into production yet.
> - Where conversation-extracted atoms were truncated, we provide a clearer definition and keep the source comment for traceability.

---

## Activation
A user milestone indicating they reached “first real value” (e.g., completed diagnostic, reviewed results, began practice). The exact activation event(s) should be defined in analytics.  
<!-- source: editorial-synthesis, 2025-12-24 -->

## Analytics event
A tracked event emitted by the product (e.g., `diagnostic_started`, `question_answered`, `subscription_created`) used for funnels, retention, and KPI reporting (PostHog).  
<!-- source: 691e70a9-2db8-8327-bb4e-83250ca356b4, 48efa029-52ca-4aec-aaec-69eaf3587d55 -->

## Blueprint alignment
The principle that questions, diagnostics, and scoring should map to the official exam blueprint domains and weights (where available).  
<!-- source: 691e70a9-2db8-8327-bb4e-83250ca356b4, eb49bc87-a858-489f-9c19-9e815cd2373a -->

## Blueprint Tracker (Exam-Blueprint Tracker)
A linkable marketing/SEO asset intended to track exam blueprint updates and drive backlinks/PR.  
<!-- source: 6804ef83-e0dc-8005-8736-9af5d3bb0238, 4a8b2c89-4fff-405e-ba17-d9714d417538 -->

## Cancel at period end
A subscription state where the user remains active until the end of the current billing period, then cancels. Often used with Stripe’s `cancel_at_period_end`.  
<!-- source: 690645ec-7814-832c-8fc1-39cdd8755a3b, 0279e718-d6e0-42a7-95c8-e3b07d942cbc -->

## Content drift
Changes over time that cause practice content to become misaligned with the exam (blueprint changes, service changes, outdated docs).  
<!-- source: 6917f618-6938-8326-bb36-43e7419affbe, bd5b2146-576c-4d28-9b7e-43d1fe72d55d -->

## Content generation run
A single “batch” execution of question generation + QC + publishing, typically tracked with metadata like source set, time, and versioning.  
<!-- source: 690645ec-7814-832c-8fc1-39cdd8755a3b, 48efa029-52ca-4aec-aaec-69eaf3587d55 -->

## Constraint
A hard boundary the system must respect (e.g., “no official endorsement claims”, “PMLE-only scope”, “vectors not wired yet”).  
<!-- source: editorial-synthesis, 2025-12-24 -->

## Conversion rate
A ratio measuring movement between funnel steps (e.g., signup → diagnostic complete → subscribe).  
<!-- source: editorial-synthesis, 2025-12-24 -->

## Diagnostic
A pre-assessment designed to estimate readiness, identify weak domains, and personalize what to study next.  
<!-- source: 6847459e-0918-8005-8e1e-6849fb8481d9, 4e073c52-c2a6-4853-8bd1-ed3e515690ad -->

## Diagnostic question snapshot
A mechanism to copy questions used in a diagnostic session into a dedicated table so the session remains immutable even if the main question bank changes.  
<!-- source: 690645ec-7814-832c-8fc1-39cdd8755a3b, 0279e718-d6e0-42a7-95c8-e3b07d942cbc -->

## Domain
A blueprint-aligned topic area (e.g., “ML solution architecture”, “data engineering”, “modeling”, etc.) used for tagging questions, scoring diagnostics, and shaping study plans.  
<!-- source: 691e70a9-2db8-8327-bb4e-83250ca356b4, eb49bc87-a858-489f-9c19-9e815cd2373a -->

## DSPy
A prompt-programming framework used to structure LLM calls into “programs” (modules/signatures) and optimize them using evaluation datasets. (Used for Testero question generation + eval loops.)  
<!-- source: 690645ec-7814-832c-8fc1-39cdd8755a3b, 48efa029-52ca-4aec-aaec-69eaf3587d55 -->

## Eval / Evaluation
A repeatable test used to measure output quality (question realism, correctness, explanation quality, blueprint coverage, etc.), typically with structured rubrics and datasets.  
<!-- source: 690645ec-7814-832c-8fc1-39cdd8755a3b, 7f5b7f17-8218-43ef-8c8f-2df2f63d6d79 -->

## Exam mode
A timed or exam-like flow that resembles the real test experience (question presentation, scoring, review).  
<!-- source: 691e248d-5c78-832f-84d7-3ab975e0de1d, 2a0b6dd4-f9f9-4ca0-9ee3-dd800e892663 -->

## Explanation
A rationale for why an answer is correct (and why distractors are wrong), written to teach and reduce repeated mistakes.  
<!-- source: 6803d6a2-9950-8005-ad25-816de069e880, 1e805ad7-72a2-448b-af59-223d412e6180 -->

## Fact
A statement treated as true in the canonical docs. Facts can be superseded by later decisions.  
<!-- source: editorial-synthesis, 2025-12-24 -->

## Funnel
A sequence of user steps used to measure product performance (e.g., landing → signup → diagnostic complete → subscribe → retained).  
<!-- source: 691e70a9-2db8-8327-bb4e-83250ca356b4, 596b11a1-eadc-4679-b82e-73d6e45f781e -->

## Guarantee: Pass-or-Extend (Planned)
A risk-reversal concept: if a user doesn’t pass after following defined criteria, their access is extended. Operational verification + copy language are **TBD**.  
<!-- source: steering-confirmation, 2025-12-24 -->

## ICP (Ideal Customer Profile)
The primary intended user segment the product is optimized for (currently: individual professionals preparing for PMLE).  
<!-- source: 6803d6a2-9950-8005-ad25-816de069e880, 0a19ae9f-edf6-41d5-989a-d940b99ab9be -->

## Loops
An email/nurture platform used for onboarding, lifecycle messaging, and marketing automation.  
<!-- source: 691e70a9-2db8-8327-bb4e-83250ca356b4, 48efa029-52ca-4aec-aaec-69eaf3587d55 -->

## Metric
A quantified measure used for product/business tracking (e.g., WAU, MRR, activation rate).  
<!-- source: editorial-synthesis, 2025-12-24 -->

## MRR (Monthly Recurring Revenue)
Subscription revenue normalized to a monthly rate. (Net new MRR is the change in MRR over a period after churn/expansion.)  
<!-- source: editorial-synthesis, 2025-12-24 -->

## Net New MRR
The period-over-period increase in MRR (new + expansion − contraction − churn). Used as a scaling-stage North Star.  
<!-- source: editorial-synthesis, 2025-12-24 -->

## North Star metric
A single primary metric for the current growth stage that reflects user value and business progress (e.g., WAU early; net new MRR later).  
<!-- source: 6918039f-21f8-832a-b8ad-6950cec4c3d1, 3a6d2c5c-4425-4a1b-8f88-9a7d8a8e1b1d -->

## Open question
An unresolved topic requiring a decision, data, or validation before it becomes canonical.  
<!-- source: editorial-synthesis, 2025-12-24 -->

## Orphan atom
An extracted atom that does not clearly map into the canonical document set (tracked for cleanup).  
<!-- source: editorial-synthesis, 2025-12-24 -->

## Paywall (P1 paywall)
A gating rule controlling access to content/features based on user state (anonymous, signed-in free, paid).  
<!-- source: 690645ec-7814-832c-8fc1-39cdd8755a3b, 48efa029-52ca-4aec-aaec-69eaf3587d55 -->

## Pilot-to-paid conversion
Enterprise-stage metric measuring how often pilots convert into paying org contracts.  
<!-- source: 6803d6a2-9950-8005-ad25-816de069e880, 0a19ae9f-edf6-41d5-989a-d940b99ab9be -->

## Plan (Pricing)
Testero currently offers **one plan** at **$15/month**.  
<!-- source: steering-confirmation, 2025-12-24 -->

## PMLE
**Google Professional Machine Learning Engineer** certification exam. This is Testero’s current sole exam scope.  
<!-- source: 68542019-f478-8005-9f70-a098cf9f5f26, aa5f26da-46c5-4c1f-a71f-81d5d7b83c61 -->
<!-- source: steering-confirmation, 2025-12-24 -->

## PostHog
The canonical product analytics system for capturing events, funnels, and retention in Testero.  
<!-- source: 691e70a9-2db8-8327-bb4e-83250ca356b4, 48efa029-52ca-4aec-aaec-69eaf3587d55 -->

## Practice question
A single scenario-based question presented to the learner with answer choices and an explanation.  
<!-- source: 6803d6a2-9950-8005-ad25-816de069e880, 1e805ad7-72a2-448b-af59-223d412e6180 -->

## Practice exam
A multi-question set intended to simulate real exam conditions and provide a higher-signal readiness estimate than individual questions.  
<!-- source: 691e248d-5c78-832f-84d7-3ab975e0de1d, 2a0b6dd4-f9f9-4ca0-9ee3-dd800e892663 -->

## Readiness
A learner’s estimated preparedness for the exam, typically inferred from diagnostic + practice performance over time.  
<!-- source: 6803d6a2-9950-8005-ad25-816de069e880, 0a19ae9f-edf6-41d5-989a-d940b99ab9be -->

## Readiness layer
Positioning concept: Testero is more than a question bank; it aims to assess readiness and prescribe what to focus on next.  
<!-- source: 6803d6a2-9950-8005-ad25-816de069e880, 82eacbbd-101b-4386-979d-1420ff3079fd -->

## Requirement
A system behavior or capability that must be implemented (often used in PRDs and acceptance criteria).  
<!-- source: editorial-synthesis, 2025-12-24 -->

## Retention
The extent to which users return and continue learning over time (e.g., weekly retention after first diagnostic).  
<!-- source: editorial-synthesis, 2025-12-24 -->

## Retrieval / RAG (Future enhancement)
Using a document corpus + retrieval (often vector-based) to ground or improve question generation and explanations. **Not wired into production yet**; prior work is experimental.  
<!-- source: steering-confirmation, 2025-12-24 -->

## Risk
A plausible issue that could block progress or cause poor outcomes (e.g., low-quality questions, blueprint drift, weak activation).  
<!-- source: editorial-synthesis, 2025-12-24 -->

## Rubric
A scoring guide used in evals/QC to judge quality dimensions consistently (correctness, realism, blueprint alignment, explanation quality).  
<!-- source: 690645ec-7814-832c-8fc1-39cdd8755a3b, 7f5b7f17-8218-43ef-8c8f-2df2f63d6d79 -->

## Spaced repetition (Planned)
A learning method that schedules review based on memory decay (often “Anki-like”) to improve retention.  
<!-- source: 6917f618-6938-8326-bb36-43e7419affbe, bd5b2146-576c-4d28-9b7e-43d1fe72d55d -->

## Stripe
Payments provider used for subscription creation, billing state, and revenue event tracking.  
<!-- source: 69211765-1130-832c-aa6d-7780272c4302, 70b7cbe6-e4c3-4a81-a40c-cd9e09e800d5 -->

## Study plan (Planned)
A personalized set of recommended topics/questions over time based on diagnostic and practice performance.  
<!-- source: 6803d6a2-9950-8005-ad25-816de069e880, 0a19ae9f-edf6-41d5-989a-d940b99ab9be -->

## Supabase
Backend platform used for auth + database (Postgres) in Testero (often paired with row-level security and a “profiles/subscriptions” model).  
<!-- source: 690645ec-7814-832c-8fc1-39cdd8755a3b, 48efa029-52ca-4aec-aaec-69eaf3587d55 -->

## Testero
An AI-powered exam-prep platform.  
<!-- source: 6803d6a2-9950-8005-ad25-816de069e880, de01a96f-53e9-48c9-97c5-8e394fd15587 -->

## Trial
A limited-time subscription state intended to reduce friction for new users; implementation details should match Stripe + database flags.  
<!-- source: 690645ec-7814-832c-8fc1-39cdd8755a3b, 48efa029-52ca-4aec-aaec-69eaf3587d55 -->

## UTM parameters
URL parameters used for marketing attribution (e.g., `utm_source=reddit&utm_medium=comment&utm_campaign=pmle_launch`).  
<!-- source: editorial-synthesis, 2025-12-24 -->

## Vector store (Future enhancement)
A database/index optimized for similarity search over embeddings (e.g., pgvector). Intended for retrieval workflows; currently experimental only in Testero.  
<!-- source: steering-confirmation, 2025-12-24 -->

## WAU (Weekly Active Users)
Count of users active in a given week (definition of “active” must be specified). Used as an early-stage North Star in some planning docs.  
<!-- source: 6918039f-21f8-832a-b8ad-6950cec4c3d1, 3a6d2c5c-4425-4a1b-8f88-9a7d8a8e1b1d -->

## WAL (Weekly Activated Learners) (Proposed)
A stricter alternative to WAU where the “active” definition is constrained to meaningful learning actions (e.g., diagnostic completed or X questions answered).  
<!-- source: 691e70a9-2db8-8327-bb4e-83250ca356b4, 596b11a1-eadc-4679-b82e-73d6e45f781e -->
