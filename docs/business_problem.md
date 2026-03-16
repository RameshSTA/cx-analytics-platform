<div align="center">
  <img src="../assets/header_banner.svg" width="100%" alt="Customer Experience Analytics Platform"/>
</div>

<div align="center">

[![README](https://img.shields.io/badge/README-3A567A?style=flat-square)](../README.md)&nbsp;
![Business Problem](https://img.shields.io/badge/Business_Problem-1A4D8F?style=flat-square)&nbsp;
[![Architecture](https://img.shields.io/badge/Architecture-3A567A?style=flat-square)](architecture_overview.md)&nbsp;
[![Model Card](https://img.shields.io/badge/Model_Card-3A567A?style=flat-square)](model_card.md)&nbsp;
[![Feature Engineering](https://img.shields.io/badge/Feature_Engineering-3A567A?style=flat-square)](feature_engineering.md)&nbsp;
[![Evaluation](https://img.shields.io/badge/Evaluation-3A567A?style=flat-square)](evaluation_strategy.md)&nbsp;
[![Statistical Methods](https://img.shields.io/badge/Statistical_Methods-3A567A?style=flat-square)](statistical_methods.md)&nbsp;
[![Business Impact](https://img.shields.io/badge/Business_Impact-3A567A?style=flat-square)](business_impact_and_roi.md)&nbsp;
[![Assumptions](https://img.shields.io/badge/Assumptions-3A567A?style=flat-square)](modeling_assumptions.md)&nbsp;
[![Deployment](https://img.shields.io/badge/Deployment-3A567A?style=flat-square)](deployment_plan.md)&nbsp;
[![Data Sources](https://img.shields.io/badge/Data_Sources-3A567A?style=flat-square)](data_sources.md)

</div>

---

# Business Problem

## Stakeholder Context

the retail operator owns and operates **42 shopping centres** across Australia and New Zealand — collectively hosting approximately 12,000 retail partners and receiving more than **500 million customer visits per year**. The Data & Insights team processes over 300,000 customer feedback responses annually using machine learning, partners with CommBank iQ on transaction-level analytics, and runs multi-channel attribution studies linking physical visits to downstream online purchases.

Despite this scale, the team faces four persistent, high-stakes questions that this platform directly addresses.

---

## Problem 1 — Customer Segmentation & Lifetime Value

**Who are our most valuable visitors, and which are silently churning before we notice?**

<p align="justify">
the operator's visitor base is highly heterogeneous. A small fraction of visitors — Champions and Loyal customers — accounts for a disproportionate share of spend and advocacy. Yet without a formal segmentation framework grounded in Recency, Frequency, and Monetary behaviour, these distinctions remain invisible to the marketing team. Campaigns are broadcast uniformly. Retention budgets are allocated by intuition rather than by predicted lifetime value. By the time a high-value visitor churns, the opportunity cost has already been incurred.
</p>

**What fails without this module:**
- Retention spend is wasted on customers who were never at risk
- High-value At-Risk customers receive no targeted intervention
- No economic framework exists to prioritise which segment to act on first
- Campaign ROI cannot be attributed at the segment level

**Success criteria:** A named segmentation with economic value (CLV) attached to each group, enabling the marketing team to direct the $2.1M At-Risk recovery budget to the right customers at the right time.

---

## Problem 2 — Foot Traffic Forecasting

**Can we predict weekly centre visitation four weeks in advance, with sufficient accuracy to drive staffing and vendor commitments?**

<p align="justify">
the retail operator centres operate under variable demand. Weekly footfall fluctuates with school holidays, public holidays, weather, promotions, and macroeconomic signals. Staffing decisions, casual roster build-up, and vendor-managed inventory replenishment all require a reliable forward view. Currently, planners rely on same-week comparisons from the prior year — a method that fails after structural shocks (post-COVID recovery, centre renovations, major tenant exits) and cannot distinguish signal from noise in the short-range window where operational decisions are made.
</p>

**What fails without this module:**
- Overstaffing on low-traffic weeks incurs unnecessary labour cost
- Understaffing on peak weeks damages NPS through poor experience
- No automated early-warning system for abnormal footfall drops
- Centre managers make promotion decisions without a demand baseline

**Success criteria:** A production-grade model achieving sub-8% MAPE on 4-week-ahead forecasts, with an Isolation Forest anomaly flag for unusual drops, served via an AWS Lambda endpoint that centre managers can query in real time.

---

## Problem 3 — NLP Sentiment & CX Intelligence

**With 300,000+ reviews annually, which experience themes are actually driving negative sentiment — and which, if fixed, would move NPS the most?**

<p align="justify">
the retail operator collects structured survey responses and unstructured text reviews at scale. The volume makes manual reading impossible: a human analyst team reading 8 hours a day would take 18 months to read a single year's reviews. Existing approaches apply coarse keyword filters (e.g., "parking" mentions = parking problem), which conflate neutral mentions with negative experiences, miss compound issues ("the parking is fine but signage is terrible"), and produce no prioritisation signal — everything looks equally important.
</p>

**What fails without this module:**
- CX investment decisions are made on anecdote rather than signal
- The highest-impact friction points remain hidden in the review corpus
- No early-warning system for emerging NPS risks (e.g., a new queue management problem)
- The same themes get re-raised in quarterly reviews without resolution because no one knows which to fix first

**Success criteria:** A DistilBERT sentiment classifier (F1 ≥ 0.90), topic extraction with BERTopic, and a CX Action Priority Matrix that ranks themes by impact × prevalence × ease-of-fix — giving the CX Director a clear, defensible investment roadmap.

---

## Problem 4 — Campaign Causal Inference

**Did the promotional campaign actually increase visitation — or did it just coincide with a period that was already trending up?**

<p align="justify">
the retail operator runs promotional programmes — loyalty events, Promo2 sustained campaigns, seasonal activations — and needs to know whether they work causally, not just correlationally. Without causal inference, all "lift" estimates are confounded: centres that received the campaign may have been on an upward trajectory anyway, or may have been different from control centres in ways that matter. Spending $4.7M to scale a campaign that showed spurious correlation would be a costly mistake. Conversely, abandoning an effective campaign because a naive t-test was underpowered is equally costly.
</p>

**What fails without this module:**
- Marketing claims "the campaign worked" based on unadjusted before/after comparisons
- Finance cannot sign off on a $4.7M scale-up without a causal estimate and confidence interval
- A/B testing framework is not codified — every new campaign starts from scratch
- No systematic approach to covariate balance or parallel-trend validation

**Success criteria:** A statistically rigorous matched-pair Difference-in-Differences design with Bayesian bootstrap, demonstrating genuine causal lift at 95.8% posterior probability, with a quantified revenue impact and a documented decision framework for future campaigns.

---

## Why These Four Problems, Together

<p align="justify">
These four modules are not independent. The CLV segmentation (M1) informs which customer cohorts to prioritise in A/B testing (M4). The traffic forecast (M2) provides the demand baseline against which causal lift (M4) is measured. The NLP pipeline (M3) surfaces the experience friction points that, once resolved, directly improve the conversion from visit to purchase — the outcome that CLV (M1) tracks. Together they form a closed-loop CX intelligence system: understand your customers, forecast their behaviour, hear their voice, and measure whether your interventions actually worked.
</p>

---

*Document version 1.0 · March 2026 · Ramesh Shrestha*

---

<div align="center">

*Customer Experience Analytics Platform — Documentation*

*[Back to README](../README.md) · Copyright © 2026 Ramesh Shrestha · All rights reserved*

</div>

<div align="center">
  <img src="../assets/footer_banner.svg" width="100%" alt="Ramesh Shrestha — Data Scientist · Sydney, Australia"/>
</div>
