<div align="center">
  <img src="../assets/header_banner.svg" width="100%" alt="Customer Experience Analytics Platform"/>
</div>

<div align="center">

[![README](https://img.shields.io/badge/README-3A567A?style=flat-square)](../README.md)&nbsp;
[![Business Problem](https://img.shields.io/badge/Business_Problem-3A567A?style=flat-square)](business_problem.md)&nbsp;
[![Architecture](https://img.shields.io/badge/Architecture-3A567A?style=flat-square)](architecture_overview.md)&nbsp;
[![Model Card](https://img.shields.io/badge/Model_Card-3A567A?style=flat-square)](model_card.md)&nbsp;
[![Feature Engineering](https://img.shields.io/badge/Feature_Engineering-3A567A?style=flat-square)](feature_engineering.md)&nbsp;
![Evaluation](https://img.shields.io/badge/Evaluation-1A4D8F?style=flat-square)&nbsp;
[![Statistical Methods](https://img.shields.io/badge/Statistical_Methods-3A567A?style=flat-square)](statistical_methods.md)&nbsp;
[![Business Impact](https://img.shields.io/badge/Business_Impact-3A567A?style=flat-square)](business_impact_and_roi.md)&nbsp;
[![Assumptions](https://img.shields.io/badge/Assumptions-3A567A?style=flat-square)](modeling_assumptions.md)&nbsp;
[![Deployment](https://img.shields.io/badge/Deployment-3A567A?style=flat-square)](deployment_plan.md)&nbsp;
[![Data Sources](https://img.shields.io/badge/Data_Sources-3A567A?style=flat-square)](data_sources.md)

</div>

---

# Evaluation Strategy

## Guiding Principle

<p align="justify">
Every model in this platform is evaluated on held-out data it has never seen during training, using metrics that are directly interpretable by a non-technical business stakeholder. The evaluation strategy is designed to answer not just "is the model accurate?" but "is this model accurate enough to make the business decision it is being asked to support?" Each module has a defined success threshold, and if the threshold is not met, the module documents why and what the implications are for the downstream decision.
</p>

---

## Module 1 — Segmentation & CLV Evaluation

### Clustering Evaluation (K-Means)
| Metric | Value | Interpretation |
|:---|:---:|:---|
| Silhouette score (k=5) | **0.62** | Strong cluster separation — segments are distinct in RFM space |
| Elbow method (inertia) | Elbow at k=5 | Marginal within-cluster variance gain drops sharply after k=5 |
| Business interpretability | ✅ Pass | All 5 clusters receive interpretable names (Champion, Loyal, At-Risk, Promising, Churned) |

### CLV Model Evaluation (XGBoost Regression)
| Metric | Value | Split | Interpretation |
|:---|:---:|:---|:---|
| R² | **0.74** | 80/20 temporal | Model explains 74% of CLV variance out-of-sample |
| RMSE | £186 | Holdout | Typical CLV prediction error ≈ £186 per customer |
| MAE | £112 | Holdout | Median absolute error; less sensitive to high-CLV outliers |
| Top-decile lift | **4.8×** | Holdout | Top 10% predicted CLV customers have 4.8× actual revenue vs. mean |

**Temporal split rationale:** A random 80/20 split would leak future information into training. The 80% training window uses transactions up to the cutoff date; the 20% test window evaluates predictions on customers whose holdout-period revenue is unknown to the model. This mirrors the operational use case — predict forward CLV from historical RFM features.

---

## Module 2 — Forecasting Evaluation

### Model Comparison (out-of-sample, 4-week hold-out)
| Model | MAPE | MAE (£/week) | RMSE | Training Time |
|:---|:---:|:---:|:---:|:---|
| Naïve (last-year same-week) | 14.1% | £3,820 | £5,210 | — |
| SARIMA(1,1,1)(1,1,1,52) | 11.2% | £2,940 | £4,180 | ~8 min |
| Prophet + AU holidays | 8.4% | £2,210 | £3,120 | ~4 min |
| **LightGBM (production)** | **6.8%** | **£1,780** | **£2,540** | ~12 min |

**Why MAPE is the primary metric:** MAPE (Mean Absolute Percentage Error) is preferred over absolute error metrics because it is scale-invariant — a £500 error on a £1,000-revenue week is very different from a £500 error on a £50,000-revenue week. Centre managers think in percentage terms ("we were off by 7%") not in absolute £ terms.

**4-week horizon justification:** Staffing decisions require 3–4 weeks' notice for casual workforce scheduling. Vendor inventory replenishment requires 2–3 weeks. The 4-week horizon is the minimum needed to make operationally actionable forecasts.

### Anomaly Detection Evaluation
| Metric | Value |
|:---|:---|
| Isolation Forest contamination | 5% |
| Precision@flagged (synthetic labelling) | 0.82 |
| Recall@true-anomaly (synthetic) | 0.79 |

---

## Module 3 — NLP Evaluation

### DistilBERT Sentiment Classifier
| Metric | Score |
|:---|:---:|
| **F1 (weighted)** | **0.91** |
| Precision | 0.90 |
| Recall | 0.92 |
| ROC-AUC | 0.96 |
| Accuracy | 0.91 |

**Why F1 over accuracy:** The sentiment dataset has natural class imbalance (more negative reviews than positive in the shopping category). Accuracy would be misleadingly inflated by predicting the majority class. F1 balances precision and recall and is the standard metric for production text classifiers.

### VADER Baseline Comparison
| Model | F1 | Notes |
|:---|:---:|:---|
| VADER (lexicon, no training) | 0.74 | Strong baseline; struggles with irony and negation |
| DistilBERT (fine-tuned) | **0.91** | +17 F1 points over VADER; captures nuanced domain language |

### BERTopic Coherence
| Metric | Value |
|:---|:---|
| Number of topics | 8 (auto-selected) |
| Topic coherence (c_v) | 0.54 |
| Coverage (% reviews assigned to a topic) | 87% |

---

## Module 4 — Causal Inference Evaluation

### Experimental Design Quality
| Check | Result | Implication |
|:---|:---:|:---|
| Balance test (Welch t on pre-period sales) | p = 0.871 | ✅ PASS — treatment and control groups are statistically indistinguishable in pre-period |
| Parallel trends visual inspection | ✅ Confirmed | Pre-period trends are parallel (H1 2013); DiD assumption holds |
| Matched-pair sample size | 54 vs 54 | Sufficient power for detecting ±5% lift at α=0.10 |
| Cluster-robust SE | Applied | Accounts for within-store serial correlation across weeks |

### Test Results Summary
| Test | Statistic | p-value | Interpretation |
|:---|:---:|:---:|:---|
| Welch t-test (post-period means) | t = 0.37 | 0.710 | Not significant — expected for matched design with small effect size |
| Mann-Whitney U | U = 1,286 | 0.68 | Consistent with t-test |
| **Difference-in-Differences (DiD)** | β = +£848/wk | **0.080** | Marginally significant causal lift at α=0.10 |
| Bayesian P(lift > 0) | — | **95.8%** | Strong posterior evidence for positive effect |

**Why DiD is the primary causal estimate:** Simple post-period comparisons confound treatment effects with pre-existing differences between stores. DiD controls for store fixed effects (entity demeaning) and time trends (post indicator), isolating the causal effect of the Promo2 campaign. Cluster-robust standard errors at the store level account for the autocorrelated nature of weekly sales data.

---

## Cross-Module Consistency Checks

| Check | Status |
|:---|:---|
| Segmentation CLV values match M4 revenue impact calculations | ✅ Consistent |
| Forecast MAPE benchmark used in DiD sample size calculation | ✅ Documented |
| NLP topic labels align with operational CX categories in reports | ✅ Aligned |
| All random seeds fixed (42) and documented | ✅ Reproducible |
| Synthetic data fallback produces structurally identical outputs | ✅ Verified |

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
