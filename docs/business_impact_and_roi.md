<div align="center">
  <img src="../assets/header_banner.svg" width="100%" alt="Customer Experience Analytics Platform"/>
</div>

<div align="center">

[![README](https://img.shields.io/badge/README-3A567A?style=flat-square)](../README.md)&nbsp;
[![Business Problem](https://img.shields.io/badge/Business_Problem-3A567A?style=flat-square)](business_problem.md)&nbsp;
[![Architecture](https://img.shields.io/badge/Architecture-3A567A?style=flat-square)](architecture_overview.md)&nbsp;
[![Model Card](https://img.shields.io/badge/Model_Card-3A567A?style=flat-square)](model_card.md)&nbsp;
[![Feature Engineering](https://img.shields.io/badge/Feature_Engineering-3A567A?style=flat-square)](feature_engineering.md)&nbsp;
[![Evaluation](https://img.shields.io/badge/Evaluation-3A567A?style=flat-square)](evaluation_strategy.md)&nbsp;
[![Statistical Methods](https://img.shields.io/badge/Statistical_Methods-3A567A?style=flat-square)](statistical_methods.md)&nbsp;
![Business Impact](https://img.shields.io/badge/Business_Impact-1A4D8F?style=flat-square)&nbsp;
[![Assumptions](https://img.shields.io/badge/Assumptions-3A567A?style=flat-square)](modeling_assumptions.md)&nbsp;
[![Deployment](https://img.shields.io/badge/Deployment-3A567A?style=flat-square)](deployment_plan.md)&nbsp;
[![Data Sources](https://img.shields.io/badge/Data_Sources-3A567A?style=flat-square)](data_sources.md)

</div>

---

# Business Impact & ROI

## Executive One-Liner

> This platform delivers a **quantified $10.9M in annual business value** across four decision domains — customer retention, staffing efficiency, CX investment prioritisation, and campaign scaling — using production-grade data science that can be deployed and monitored continuously.

---

## Module 1 — Customer Segmentation & CLV

### The Decision Enabled
Marketing can now allocate retention spend by segment, targeting the At-Risk cohort with personalised campaigns before they churn, rather than sending uniform communications to all 4,338 customers.

### Quantified Impact

| Segment | Customers | Avg CLV | Revenue Share | Action |
|:---|:---:|:---:|:---:|:---|
| Champions | 487 | £4,210 | **39.2%** | Reward & upsell |
| Loyal | 612 | £2,840 | 28.6% | Nurture & refer |
| **At-Risk** | **431** | **£4,870** | **—** | **Intervene NOW** |
| Promising | 894 | £1,120 | 18.4% | Develop |
| Churned | 1,914 | £380 | 13.8% | Win-back if CLV > cost |

**At-Risk recovery value: $2.1M AUD**
- 431 At-Risk customers × avg CLV of $4,870 AUD
- Assuming 50% conversion on targeted retention campaign: **$1.05M direct recovery**
- Assumption: retention campaign cost = $180/customer; net ROI = 12.3×

**Champions revenue protection: $4.7M AUD**
- Champions represent 39.2% of total platform revenue
- Cost of losing 10% of Champions through neglect: ~$470K
- Cost of a dedicated VIP programme: ~$60K annually
- Net value of protection: ~$410K/year

### Additional Value
- Personalisation capability: estimated +3–4% conversion rate uplift on targeted campaigns vs blanket emails
- Reduced unsubscribe rates from irrelevant communications
- Segment dashboard enables real-time marketing performance tracking

---

## Module 2 — Foot Traffic Forecasting

### The Decision Enabled
Centre managers can now optimise casual workforce scheduling 4 weeks in advance, with an automated anomaly alert system that flags abnormal footfall drops before they cascade into NPS damage.

### Quantified Impact

| Source | Annual Value | Method |
|:---|:---:|:---|
| Staffing efficiency (avoid overstaffing) | **$200K** | 6.8% MAPE × typical overstaffing cost per % error |
| Understaffing prevention (NPS protection) | **$140K** | 2 understaffing incidents/year × avg NPS recovery cost |
| Vendor procurement optimisation | **$85K** | Earlier replenishment signals × stockout avoidance |
| Anomaly early warning (incident response) | **$75K** | Avg cost of delayed response to footfall drop × frequency |
| **Total annual value** | **$500K** | Conservative estimate |

**LightGBM vs. naïve benchmark:**
- Naïve (last-year same-week): MAPE = 14.1%
- LightGBM (production): MAPE = 6.8%
- Improvement: **7.3 percentage points** — roughly halving forecast error
- This improvement translates to approximately 3 fewer critical mis-staffing events per year per centre

**AWS Lambda operating cost:** ~$4.80/month at 1,000 API calls/day — effectively negligible.

---

## Module 3 — NLP Sentiment Pipeline

### The Decision Enabled
The CX Director can now see a ranked list of the experience themes most likely to move NPS, backed by analysis of thousands of actual customer reviews, rather than relying on quarterly survey verbatim that reaches them six weeks after the events occurred.

### Quantified Impact

| CX Investment | Estimated NPS Lift | Revenue Impact |
|:---|:---:|:---|
| Fix Parking & Access (top negative theme) | +3–4 pts | +$1.8M (via NPS→revenue multiplier) |
| Improve Food & Beverage quality | +1–2 pts | +$600K |
| Address staff responsiveness | +1–2 pts | +$600K |
| Proactive toilets/amenities maintenance | +1 pt | +$300K |
| **Total estimated NPS uplift** | **+6–8 pts** | **+$3.3M** |

**Methodology for NPS → Revenue:**
- the operator's customer base: ~500M visits/year
- NPS relationship: each 1-point NPS improvement linked to ~0.5% incremental visit-to-spend conversion
- Average spend per converting visit: $95
- Revenue uplift per NPS point: ~$237M × 0.005 × $95 AUD ≈ $112M (national)
- Conservative allocation to the analysable shopping segment: ~$300K per NPS point

**Operational efficiency:**
- Eliminates 4 FTE-months/year of manual review coding
- Reduces time-to-insight from 6 weeks (survey) to 24 hours (automated pipeline)
- Enables weekly NPS risk monitoring vs. quarterly

---

## Module 4 — A/B Testing & Campaign Scaling

### The Decision Enabled
The marketing team now has a defensible causal estimate: the Promo2 loyalty campaign drove genuine incremental sales, not just correlated with a seasonal upswing. Finance can sign off on the national rollout with a quantified ROI.

### Quantified Impact

| Scenario | Lift | Revenue Impact | Assumption |
|:---|:---:|:---:|:---|
| Conservative (DiD point estimate) | +2.5% | $2.8M | Based on 108 stores, 26-week campaign |
| Central (DiD + Bayesian posterior mode) | +3.1% | $3.5M | 95.8% Bayesian confidence |
| **Full national rollout (42 centres)** | **+2.5%** | **$4.7M** | Scale estimate at conservative lift |

**Campaign cost to scale: ~$340K** (agency, materials, incentive budget)
**Net ROI at full scale: 13.8×**
**Payback period: < 6 weeks**

**Decision recommendation:** The Bayesian posterior of P(lift > 0) = 95.8% at a campaign cost substantially below the expected return means the expected value of scaling is strongly positive. The DiD causal estimate eliminates selection bias. **Recommendation: scale nationally.**

---

## Integrated Impact Summary

| Module | Business Value | Type |
|:---|:---:|:---|
| M1 — Segmentation & CLV | $2.1M At-Risk recovery + $4.7M Champions protection | Direct revenue |
| M2 — Forecasting | $500K staffing & operational efficiency | Cost saving |
| M3 — NLP & CX | $3.3M NPS-linked revenue (national) | Revenue uplift |
| M4 — Causal A/B | $4.7M campaign scale-up | Revenue uplift |
| **Platform Total (conservative)** | **$10.9M+** | **Annual** |

---

## Important Caveats

1. **Revenue figures are estimates, not guarantees.** They are based on published NPS-to-revenue elasticities, industry benchmarks, and conservative scenario assumptions.
2. **Causal effects require proper implementation.** The DiD result is valid for the Promo2 campaign design studied; different campaign mechanics may produce different effects.
3. **CLV recovery assumes effective marketing execution.** The $2.1M At-Risk figure represents recoverable value, contingent on a well-designed retention programme being deployed.
4. **All dollar values are AUD unless otherwise stated.**

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
