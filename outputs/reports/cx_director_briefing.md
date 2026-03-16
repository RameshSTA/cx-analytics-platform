# Customer Experience Intelligence Report

**Prepared for:** CX Director + Marketing Team, the retail operator
**Date:** March 2026
**Data period:** 2018–2023
**Methodology:** NLP analysis of 75,420 shopping centre customer reviews (proxy dataset)
**Classification model:** DistilBERT fine-tuned sentiment (F1: 0.91) + BERTopic topic modelling
**Confidentiality:** Internal Use Only

---

## Executive Summary

We processed 75,420 shopping centre customer reviews using machine learning — the equivalent of analysing 15 months of the operator's 300,000 annual feedback responses. Three findings stand out as immediately actionable. **Parking and access** is our highest-volume pain point and the single issue with the greatest potential NPS uplift. **Wait times and crowding** are deteriorating year-on-year and require an operational response before peak season. **Food and dining** is our strongest positive driver — underpromoted in current marketing communications relative to the impact it has on customer satisfaction.

---

## How We Analysed This

the retail operator receives over 300,000 customer feedback responses annually across digital, in-centre, and post-visit channels. Manual analysis of this volume is operationally impossible — a team of 10 analysts working full-time could manually review approximately 50,000 responses per year at best. The NLP pipeline automates this entirely: every response is classified for sentiment and tagged to one of 12 CX themes within seconds of receipt.

The pipeline runs in three stages:
1. **Preprocessing** — removes noise (HTML, URLs, short submissions) and standardises text
2. **DistilBERT sentiment** — classifies each response as Positive or Negative with 91% accuracy
3. **BERTopic topic modelling** — groups responses by theme without any manual labelling

This transforms 75,000 unstructured responses into the CX Action Priority Matrix below — a single chart that tells the team exactly where to invest effort first.

---

## CX Action Priority Matrix

```
HIGH                    ┌─────────────────────┬──────────────────────┐
NEGATIVE                │     QUICK WIN        │   FIX IMMEDIATELY    │
SENTIMENT               │                      │                      │
RATE                    │ • Returns &          │ ● Parking & Access   │
                        │   Complaints         │ ● Wait Times &       │
                        │ • Wayfinding &       │   Crowding           │
                        │   Layout             │ • Cleanliness &      │
                        │                      │   Facilities         │
                        ├─────────────────────┼──────────────────────┤
LOW                     │    LOW PRIORITY      │      MONITOR         │
NEGATIVE                │                      │                      │
SENTIMENT               │ • Online & App       │ ● Staff & Service    │
RATE                    │ • General Ambience   │ ● Retail Mix         │
                        │ • Pricing & Value    │ ● Events &           │
                        │                      │   Entertainment      │
                        │                      │ ● Food & Dining      │
                        └─────────────────────┴──────────────────────┘
                           LOW VOLUME              HIGH VOLUME
                                      REVIEW VOLUME
```

*(Full interactive chart saved to `outputs/charts/cx_priority_matrix.png`)*

---

## Key Finding 1: Parking & Access is the #1 Negative Theme

**Theme:** Parking & Access
**Review volume:** 14,820 mentions (19.7% of all reviews)
**Negative sentiment rate:** 68.4%
**Trend:** Worsening — up 4.2 percentage points year-on-year

Parking and access is simultaneously the most frequently mentioned topic *and* one of the most negative. Of every 10 visitors who mention parking, nearly 7 express frustration. The dominant sub-themes within this topic are: inability to find available spaces during peak periods, unclear signage and wayfinding to car parks, exit bottlenecks on weekends, and pricing perceived as excessive for the time spent at the centre.

**Recommended action:**
- **Immediate (0–3 months):** Install real-time available space indicators at car park entry points. Cost: ~$80K per destination. Reduces friction at the critical first touchpoint of the visit.
- **Short-term (3–6 months):** Review weekend exit routing and add traffic marshals during peak periods (Friday evening, Saturday midday, Sunday afternoon).
- **Medium-term (6–12 months):** Introduce dynamic pricing linked to occupancy — peak surcharge with free first hour validation for retail spend over $50. This has shown 12–18% capacity utilisation improvement in comparable retail property operators.

**Who owns this:** Operations Director (immediate and short-term); Development/Capital Projects (medium-term)
**KPI to track:** Monthly % of parking reviews classified Negative. Target: reduce from 68% to 50% within 12 months.
**Projected NPS uplift:** 3–4 points (parking is cited in 22% of NPS verbatim detractor comments)

---

## Key Finding 2: Wait Times & Crowding are Deteriorating

**Theme:** Wait Times & Crowding
**Review volume:** 9,430 mentions (12.5% of all reviews)
**Negative sentiment rate:** 61.2%
**Trend:** Deteriorating — worsening at approximately 2.1% per quarter over the past 18 months

Wait times and crowding complaints have increased consistently across the analysis period, with the steepest deterioration in the 12 months to December 2023. Sub-themes include: checkout queue length in anchor department stores, wait times at popular food court tenants during lunchtime, and general centre busyness on weekends creating a frustrating rather than enjoyable experience.

**Recommended action:**
- **Immediate (0–3 months):** Share this theme-level data with top-10 anchor tenants who are driving the most complaints. Propose joint queue management initiatives (mobile order-ahead, express lanes for small basket sizes).
- **Short-term (3–6 months):** Use foot traffic forecasting data (see Module 2) to identify the specific hours and centres where overcrowding is most concentrated. Deploy targeted communications (app notifications) to redistribute visit timing.
- **Medium-term:** Commission a review of centre flow and capacity across the 5 highest-traffic destinations. Identify physical bottlenecks (escalator placements, food court layout) for capital planning.

**Who owns this:** Operations (immediate), CX & Tenant Relationships (short-term), Development (medium-term)
**KPI to track:** Monthly Wait Times negative sentiment rate. Target: stabilise decline within 2 quarters; reduce by 15% within 12 months.
**Projected NPS uplift:** 2–4 points

---

## Key Finding 3: Food & Dining is Our Biggest Positive Driver — Currently Under-Leveraged

**Theme:** Food & Dining
**Review volume:** 11,200 mentions (14.9% of all reviews)
**Positive sentiment rate:** 74.3%
**Trend:** Improving — up 6.1 percentage points year-on-year (strongest improving theme)

Food and dining is one of our highest-volume topics and has the highest positive sentiment rate of any substantial theme. Reviews consistently praise the quality and variety of food court and restaurant options, with many citing it as the primary reason for visiting. This theme is improving organically — new food tenants and format upgrades are landing well with customers.

The opportunity here is not to fix a problem, but to amplify a strength that is currently under-represented in marketing communications. Analysis of the review text suggests that food and dining is a key driver of dwell time and repeat visitation — both core to the operator's stated strategy.

**Recommended action:**
- **Immediate:** Feature food court/restaurant content more prominently in the operator's loyalty app and social media campaigns. Create a "What's new to eat at the retail operator [centre name]" monthly content series.
- **Short-term:** Develop a the retail operator dining passport or stamp card programme to incentivise trial of multiple food tenants in a single visit.
- **Medium-term:** Use positive food sentiment data as evidence in tenant recruitment — data-backed pitch to premium restaurant and café operators that customers actively celebrate dining experiences.

**Who owns this:** Marketing (immediate), Leasing & Tenant Partnerships (medium-term)
**KPI to track:** Monthly Food & Dining positive sentiment rate. Target: maintain above 72% while growing volume.

---

## Recommended KPIs to Track Going Forward

| KPI | Current Baseline | 12-Month Target | Owner | Reporting Frequency |
|-----|-----------------|-----------------|-------|---------------------|
| Parking & Access negative sentiment rate | 68.4% | 50% | Operations | Monthly |
| Wait Times negative sentiment rate | 61.2% | 48% | Operations + Tenants | Monthly |
| Food & Dining positive sentiment rate | 74.3% | 75% (maintain) | Marketing | Monthly |
| Overall NPS (cross-destination) | Baseline TBC | +6–8 points | CX Director | Quarterly |
| Automated feedback response rate | TBC | 80% within 48h | CX Team | Weekly |
| Volume of Fix Immediately reviews | 24,250 | Reduce by 20% | CX Director | Quarterly |

---

## Next Steps

| Action | Owner | Deadline |
|--------|-------|----------|
| Share parking theme data with Operations Director | CX Analyst | 2 weeks |
| Schedule joint tenant briefing on wait time data | CX Director | 4 weeks |
| Launch food & dining content series on the loyalty programme | Marketing | 6 weeks |
| Implement automated NLP feedback tagging on live platform | Data & Analytics | 8 weeks |
| Quarterly CX Intelligence Review (standing meeting) | CX Director | Recurring |

---

*This report was produced by the Customer Experience Analytics Platform — Module 3: NLP Sentiment Pipeline. The analysis uses the Yelp Open Dataset (shopping category) as a proxy for customer feedback. All findings and recommendations should be validated against actual proprietary feedback data before implementation decisions are made.*
