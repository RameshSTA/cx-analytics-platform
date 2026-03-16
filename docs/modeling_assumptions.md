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
[![Business Impact](https://img.shields.io/badge/Business_Impact-3A567A?style=flat-square)](business_impact_and_roi.md)&nbsp;
![Assumptions](https://img.shields.io/badge/Assumptions-1A4D8F?style=flat-square)&nbsp;
[![Deployment](https://img.shields.io/badge/Deployment-3A567A?style=flat-square)](deployment_plan.md)&nbsp;
[![Data Sources](https://img.shields.io/badge/Data_Sources-3A567A?style=flat-square)](data_sources.md)

</div>

---

# Modelling Assumptions, Risks & Limitations

## Module 1 — Segmentation & CLV

### Key Assumptions

| Assumption | Value / Description | Sensitivity |
|:---|:---|:---|
| RFM lookback window | 12 months from observation cutoff | Shorter windows increase churn signal; longer windows smooth it |
| K-Means cluster count | k=5 (elbow + silhouette validation) | k=4 produces broader segments; k=6 splits At-Risk into two sub-groups |
| CLV forecast horizon | 12 months forward | Accuracy degrades beyond 18 months for volatile spenders |
| XGBoost train/test split | 80/20 temporal (not random) | Random split would inflate R² by ~0.06 via data leakage |
| Currency | GBP (UCI dataset) | Converted to AUD in business impact calculations at 1.92 exchange rate |

### Known Risks
- **Survivorship bias:** The UCI dataset excludes customers who churned before the observation period. CLV predictions are therefore optimistic for newly acquired customers.
- **Stationarity assumption:** RFM patterns are assumed stable. A major external shock (pandemic, economic recession) would invalidate segment boundaries until the model is retrained.
- **Proxy dataset:** UCI Online Retail II is a UK e-commerce dataset. the retail operator is a physical retail operator. Direct metric translation requires validation against the retail operator's own transaction data.

---

## Module 2 — Forecasting

### Key Assumptions

| Assumption | Value / Description | Sensitivity |
|:---|:---|:---|
| Weekly aggregation unit | ISO week (Mon–Sun) | Daily models would require more features and are noisier |
| SARIMA seasonality period | 52 weeks (annual) | Assumes stable annual cycle; fails during holiday timing shifts |
| Prophet changepoint prior scale | 0.05 (default) | Higher values allow more flexible trend; tested 0.01–0.20 |
| LightGBM lag features | Weeks 1, 2, 4, 8, 52 | Empirically selected via permutation importance |
| Isolation Forest contamination | 5% | Flagged based on domain knowledge of typical anomaly frequency |

### Known Risks
- **Dataset proxy:** Rossmann is a German pharmacy/drugstore chain. The seasonal pattern (Christmas dominates) is structurally different from Australian retail, where summer holidays and back-to-school drive different peaks. production models would use the retail operator's own footfall data.
- **Store heterogeneity:** A single LightGBM model is fitted across all 1,115 stores. Store-specific models or a hierarchical approach may improve MAPE for unusual stores (airport retail, outlet centres).
- **External regressors not fully modelled:** Weather, competitor openings, and major events are not in the Rossmann dataset and are not included.

---

## Module 3 — NLP

### Key Assumptions

| Assumption | Value / Description | Sensitivity |
|:---|:---|:---|
| Dataset proxy | Yelp Shopping category reviews | Approximates retail-style feedback; not identical to CX survey data |
| DistilBERT base model | `distilbert-base-uncased` | Larger models (BERT-base, RoBERTa) would improve F1 by ~1–2 pts at 2× inference cost |
| Sentiment labels | Binary (positive / negative) | A 3-class model (positive / neutral / negative) better captures mixed reviews |
| BERTopic topic count | Auto-selected (8 topics) | Forced k would allow domain-aligned topic names but risks under/over-segmenting |
| Review sampling | Up to 50K reviews (synthetic: 1K) | Full Yelp dataset (6.7M) would improve topic coherence significantly |

### Known Risks
- **Domain shift:** Yelp reviews are voluntary and skew negative (unhappy customers are more motivated to write). post-visit customer surveys are solicited post-visit and may have different sentiment distributions.
- **Irony and sarcasm:** DistilBERT occasionally misclassifies heavily ironic reviews. A custom fine-tuning pass on domain-specific language would reduce this error.
- **Topic drift:** BERTopic topics are static post-training. Emerging themes (e.g., new queue management technology complaints) will not appear until the model is retrained.

---

## Module 4 — Causal Inference

### Key Assumptions

| Assumption | Value / Description | How It Is Tested |
|:---|:---|:---|
| Parallel trends | Treatment and control stores trend identically pre-campaign | Visual inspection of H1 2013 weekly sales; balance test p=0.871 |
| No spillover (SUTVA) | Promo2 in one store does not affect control store sales | Stores in the same geographic market are partially excluded from the matched control pool |
| No anticipation effects | Stores did not change behaviour in anticipation of the campaign | Pre-period is H1 2013; campaign starts H2 2013 |
| Nearest-neighbour matching | Matching on pre-period mean weekly sales only | A richer matching (on store size, store type, competition) would reduce residual confounding |
| Campaign period | H2 2013 (weeks 27–52) | Promo2SinceYear=2013, Promo2SinceWeek≥27 used to identify treated stores |

### Known Risks
- **Selection into treatment:** Rossmann may have selected stores for Promo2 based on characteristics that predict future sales growth. Nearest-neighbour matching on pre-period sales partially addresses this but cannot rule out unobserved confounders.
- **Hawthorne effect:** Store managers who know they are in a promotional programme may increase effort independent of the programme itself.
- **Short post-period:** The post-period is one half-year (26 weeks). Longer-run effects (positive or negative through fatigue) are not measured.
- **External validity:** The Rossmann result is specific to the German pharmacy retail context and the Promo2 mechanism. the operator's campaign mechanisms are different.

---

## Cross-Module Risks

| Risk | Modules Affected | Mitigation |
|:---|:---|:---|
| Proxy dataset limitation | All | Documented in every notebook; synthetic fallbacks validate pipeline without real data |
| Random seed sensitivity | M1, M3 | All seeds fixed at 42; notebooks are deterministically reproducible |
| Feature leakage | M1, M2 | Temporal splits enforced in both modules; no future-date features in training windows |
| Production drift | M2, M3 | Monitoring thresholds documented in `deployment_plan.md`; retraining triggers specified |

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
