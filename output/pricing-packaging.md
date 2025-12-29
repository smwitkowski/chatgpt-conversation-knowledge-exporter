<!-- FILE: docs/pricing_packaging.md -->
# Testero Pricing & Packaging

**Last updated:** 2025-12-25  
**As-of validity anchor:** 2025-12-24 (items marked “Recommended / Not validated” are not confirmed end-to-end as of this date)  
**Audience:** AI engineers + AI assistants contributing to Testero  
**Status:** Canonical (with explicit superseded history)

> This document defines the *current* pricing and packaging, the entitlements model that enforces it, and the historical decisions that were explored and then superseded.

---

## 1) Canonical pricing (current)

### 1.1 One plan, one price (canonical)
**Current canonical plan:** **$15/month** (single plan).  
<!-- source: steering-confirmation, 2025-12-24 -->

**Scope:** PMLE-focused offering for the initial wedge.  
<!-- source: 693c3ff6-2fa0-800f-89a2-fe6a2468e3e7, 2f0986b4-4515-4737-8b17-524c7cc6cbaa -->

### 1.2 What “$15/mo” buys (canonical intent)
Paid users should receive:
- full access to practice questions and practice exams
- high-quality explanations
- study plan / targeted practice based on performance  
<!-- source: 6917f4c6-69d4-8005-a651-979d1420ff30, fce1d4b1-88d0-4207-ae22-e2b7cf2f8640 -->

> Note: Exact feature boundaries are enforced via entitlements (see §3) and should be reflected consistently in marketing copy.

---

## 2) Packaging: Free vs Paid access

### 2.1 Free tier boundary (canonical per ADR)
Free tier is designed to allow a user to experience value quickly without “giving away the whole product”:
- **Free:** ~30 questions + **1 Readiness Snapshot**
- **Paid:** the rest is gated behind the paywall  
<!-- source: 690678ff-6f48-8327-8071-1a446a8b5b87, ffbeb313-626e-498e-84cd-94fd5ae76234 -->

**Why:** Drive activation + conversion through a clearly bounded free experience.  
<!-- source: 690678ff-6f48-8327-8071-1a446a8b5b87, ffbeb313-626e-498e-84cd-94fd5ae76234 -->

### 2.2 Trial (recommended / not validated as of 2025-12-24)
There are atoms indicating a **trial flow** exists (e.g., 14-day free trial endpoints and behavior).  
<!-- source: 690679e6-f9fc-8331-8cd3-7a010a51731f, 8a42f473-4cf9-4acd-81d7-f6af7509ae12 -->

**Recommended posture:** Treat trial as an *optional experiment*—do not make it canonical unless it is intentionally enabled and supported (billing + copy + support).  
<!-- source: 691e70a9-2db8-8327-bb4e-83250ca356b4, ba22aa0c-3e00-4f17-9532-3847525dcc2c -->

**Open question:** whether the $15/mo plan includes a trial at launch (see §7).

---

## 3) Entitlements & paywall enforcement (implementation-facing)

### 3.1 Stripe-hosted checkout and portal (canonical)
Use Stripe-hosted Checkout + Stripe Customer Portal (avoid custom payment UIs).  
<!-- source: 690679e6-f9fc-8331-8cd3-7a010a51731f, 8a42f473-4cf9-4acd-81d7-f6af7509ae12 -->

Entitlements are updated **webhook-first** (do not trust client-side state).  
<!-- source: 690678ff-6f48-8327-8071-1a446a8b5b87, ffbeb313-626e-498e-84cd-94fd5ae76234 -->

### 3.2 Paywall levels (canonical internal model)
A defined paywall model exists (P1 “blanket paywall” described in billing definitions), including:
- blanket gating behind entitlements
- special-case handling like `cancel_at_period_end` grace until current period ends  
<!-- source: 690679e6-f9fc-8331-8cd3-7a010a51731f, 023bde68-940c-4b45-bf7a-b066a6e76915 -->

### 3.3 Reducing “post-purchase friction” (canonical direction)
Implement a short-lived “grace cookie” after successful checkout so users don’t get stuck behind the paywall while Stripe webhooks propagate.  
<!-- source: 691e70a9-2db8-8327-bb4e-83250ca356b4, 8afdeac2-95db-4704-bc5b-37ca41088a7e -->

---

## 4) Pricing page & copy rules (marketing-facing)

### 4.1 Keep the pricing page “one decision”
At launch, reduce choice overload by exposing **one clear plan** rather than multiple generic tiers.  
<!-- source: 691e70a9-2db8-8327-bb4e-83250ca356b4, f7a19d33-2083-434c-b8a2-8629db12b46d -->

### 4.2 Avoid unverified claims (canonical)
If claims are not verified (e.g., “SME reviewed”, “pass rate”), they must be:
- omitted, or
- explicitly labeled as aspirational / in-progress  
<!-- source: 6803dab6-3548-8005-bad8-b6d803cc1e12, 4ef1702c-00ad-4e81-9d0d-38757ce7cb78 -->

### 4.3 “Pass-or-Extend” promise (decision accepted; operational/copy TBD)
There is a “Pass-or-Extend” concept: if the learner fails, they receive additional access.  
<!-- source: 6803d6a2-9950-8005-ad25-816de069e880, 0a19ae9f-edf6-41d5-989a-d940b99ab9be -->
<!-- source: steering-confirmation, 2025-12-24 -->

**Canonical stance:** We will use “Pass-or-Extend” as a direction, but the operational rules and customer-facing language are TBD.  
(Do not implement or market as a hard guarantee until §7 is resolved.)

---

## 5) Historical pricing decisions (superseded)

> These are maintained for context. They are **not** canonical after the 2025-12-24 steering decisions.

### 5.1 Prior subscription anchors (superseded)
- Pro $12/month + annual $79/year anchor (ADR states “active” historically).  
  **Superseded by:** one plan at **$15/month**.  
  <!-- source: 690678ff-6f48-8327-8071-1a446a8b5b87, ffbeb313-626e-498e-84cd-94fd5ae76234 -->

### 5.2 “Exam pass” one-time offer exposure (superseded / deferred)
A one-time “exam pass” offer existed as an idea/experiment, with a decision not to expose it on day one.  
With one-plan $15/mo, this remains deferred unless explicitly reintroduced as an experiment.  
<!-- source: 691e70a9-2db8-8327-bb4e-83250ca356b4, f7a19d33-2083-434c-b8a2-8629db12b46d -->

### 5.3 Early cohort pricing at $40 (historical)
Testero had an early paying customer at **$40**, and a decision was made **not** to retroactively discount unless explicitly requested.  
<!-- source: 693c3fd0-2fa0-832f-948f-653ce50f5a7e, a5738493-feb3-4466-86c9-db5d17692b12 -->

There was also a later decision to avoid lowering price “due to nerves” and instead run structured experiments for future cohorts.  
This is **superseded** by the canonical $15/month plan but remains relevant as a lesson: pricing changes should be intentional, not reactive.  
<!-- source: 693c3ff6-2c18-832e-a7d6-d48ce7fd5164, 5578ea7d-aed0-42e4-b2ea-a79ca4852327 -->

---

## 6) Analytics & instrumentation (pricing funnel)

**Core funnel events** to instrument (canonical direction):
- pricing page view
- click “upgrade”
- checkout started (Stripe session created)
- checkout completed
- entitlement granted (webhook processed)
- paywall shown / blocked action (with feature key)  
<!-- source: 690679e6-f9fc-8331-8cd3-7a010a51731f, 0b855209-bb33-4bb9-a145-d75db6c09f43 -->

> UTM tracking: ensure upgrades from Reddit/SEO/community posts use UTMs so pricing conversion can be attributed at least at landing+signup level. (Implementation detail lives in analytics docs.)

---

## 7) Open questions (must resolve to fully “lock” pricing + packaging)

1. **Trial policy:** Is there a trial for the $15 plan at launch? If yes, exact duration + cancellation behavior + copy.
2. **Pass-or-Extend operational spec:**  
   - What qualifies as “fail”? (self-attestation vs evidence)  
   - What timeframe?  
   - What extension length?  
   - Anti-abuse constraints?  
   - Support workflow?  
3. **Free tier boundary confirmation:** Is “30 questions + 1 Readiness Snapshot” still the intended free experience under the $15 plan, or should the free tier be simplified (e.g., “1 diagnostic + limited practice”)?
4. **Legacy customer policy:** For any existing $40 customers, do we keep them grandfathered, offer voluntary migration, or proactively migrate them?

---

## 8) Implementation checklist (engineering)

- [ ] Single Stripe product/price configured for **$15/month**
- [ ] Remove or hide superseded prices/tier SKUs in UI (and in Stripe if not needed)
- [ ] Entitlement enforcement centralized (server-side) with consistent `PAYWALL` error handling
- [ ] Grace cookie implemented post-checkout
- [ ] Paywall instrumentation + conversion funnel events implemented
- [ ] Pricing page copy aligned with:
  - one-plan positioning
  - no unverified claims
  - Pass-or-Extend marked as “terms TBD” until spec exists