<div align="center">
  <img src="../assets/header_banner.svg" width="100%" alt="Customer Experience Analytics Platform"/>
</div>

<div align="center">

[![README](https://img.shields.io/badge/README-3A567A?style=flat-square)](../README.md)&nbsp;
[![Business Problem](https://img.shields.io/badge/Business_Problem-3A567A?style=flat-square)](business_problem.md)&nbsp;
[![Architecture](https://img.shields.io/badge/Architecture-3A567A?style=flat-square)](architecture_overview.md)&nbsp;
![Model Card](https://img.shields.io/badge/Model_Card-1A4D8F?style=flat-square)&nbsp;
[![Feature Engineering](https://img.shields.io/badge/Feature_Engineering-3A567A?style=flat-square)](feature_engineering.md)&nbsp;
[![Evaluation](https://img.shields.io/badge/Evaluation-3A567A?style=flat-square)](evaluation_strategy.md)&nbsp;
[![Statistical Methods](https://img.shields.io/badge/Statistical_Methods-3A567A?style=flat-square)](statistical_methods.md)&nbsp;
[![Business Impact](https://img.shields.io/badge/Business_Impact-3A567A?style=flat-square)](business_impact_and_roi.md)&nbsp;
[![Assumptions](https://img.shields.io/badge/Assumptions-3A567A?style=flat-square)](modeling_assumptions.md)&nbsp;
[![Deployment](https://img.shields.io/badge/Deployment-3A567A?style=flat-square)](deployment_plan.md)&nbsp;
[![Data Sources](https://img.shields.io/badge/Data_Sources-3A567A?style=flat-square)](data_sources.md)

</div>

---

# Model Card

## Platform Overview

This document provides a concise model card for each ML model deployed in the Customer Experience Analytics Platform, following the Model Cards for Model Reporting standard (Mitchell et al., 2019).

---

## Model 1 — XGBoost Customer Lifetime Value Regressor

| Property | Value |
|:---|:---|
| **Model type** | Gradient-boosted decision tree (XGBoost regression) |
| **Framework** | XGBoost 2.0+ |
| **Task** | Predict 12-month forward CLV per customer (continuous, GBP) |
| **Training data** | UCI Online Retail II — first 80% of transaction history (temporal split) |
| **Holdout evaluation** | Last 20% of transaction history (2011) |
| **Primary metric** | R² = 0.74 (holdout); Top-decile lift = 4.8× |
| **Hyperparameters** | n_estimators=400, max_depth=5, learning_rate=0.05, subsample=0.8 |
| **Input features** | 7 RFM features + 6 engineered features (see feature_engineering.md) |
| **Output** | Predicted CLV in £ per customer |
| **Intended use** | Rank customers by predicted future value for retention targeting |
| **Not intended for** | Real-time transaction approval; individual loan/credit decisions |

### Fairness Considerations
The model is trained on purchase behaviour, not demographic attributes. CustomerID is a pseudonymous identifier — no gender, age, or location data is used in modelling. However, purchase behaviour may correlate with demographic attributes, and the model should not be used to make decisions that disadvantage protected groups.

### Monitoring
- Retrain monthly on rolling 24-month transaction window
- Alert threshold: R² drops below 0.65 on 90-day rolling validation

---

## Model 2 — LightGBM Multi-Step Sales Forecaster

| Property | Value |
|:---|:---|
| **Model type** | Gradient-boosted decision tree (LightGBM regression) |
| **Framework** | LightGBM 4.0+ |
| **Task** | Recursive 4-week-ahead weekly sales forecast per store |
| **Training data** | Rossmann stores 2013–2015 (weeks 1–104 per store) |
| **Holdout evaluation** | Final 4 weeks per store (2015) |
| **Primary metric** | MAPE = 6.8% (holdout); MAE = £1,780/week |
| **Hyperparameters** | n_estimators=500, num_leaves=63, learning_rate=0.05, min_data_in_leaf=20 |
| **Input features** | 13 features including sales lags (1,2,4,8,52), rolling stats, holidays, store metadata |
| **Output** | Predicted weekly sales in £; anomaly flag (binary) per week |
| **Intended use** | Centre manager staffing decisions, vendor replenishment, promotional planning |
| **Not intended for** | Intraday sales forecasting; individual transaction prediction |
| **Deployment** | AWS Lambda endpoint (ap-southeast-2) |

### Monitoring
- Weekly automated validation: compute MAPE on latest week actuals
- Alert threshold: 4-week rolling MAPE > 10%
- Retraining trigger: MAPE > 15% for 2 consecutive weeks

---

## Model 3a — DistilBERT Sentiment Classifier

| Property | Value |
|:---|:---|
| **Model type** | Transformer (DistilBERT fine-tuned for binary sentiment) |
| **Framework** | HuggingFace Transformers 4.x |
| **Base model** | `distilbert-base-uncased` |
| **Task** | Binary sentiment classification: positive (1) / negative (0) |
| **Training data** | Yelp Shopping reviews — stars 1–2 = negative, 4–5 = positive (3-star excluded) |
| **Train/test split** | 80/20 stratified random split |
| **Primary metric** | F1 (weighted) = 0.91 |
| **Other metrics** | Precision = 0.90, Recall = 0.92, ROC-AUC = 0.96 |
| **Max sequence length** | 128 tokens (truncated; adequate for 95% of reviews) |
| **Training epochs** | 3 |
| **Intended use** | Classify incoming customer reviews; power NPS risk dashboard |
| **Not intended for** | Medical text; legal documents; languages other than English |

### Limitations
- Irony and sarcasm detection is imperfect (~8% misclassification rate on sarcastic reviews)
- Reviews longer than 128 tokens are truncated — the tail content is unanalysed
- The model may inherit biases present in Yelp's self-selected reviewer population

---

## Model 3b — BERTopic Topic Modeller

| Property | Value |
|:---|:---|
| **Model type** | Neural topic model (UMAP + HDBSCAN + c-TF-IDF) |
| **Framework** | BERTopic 0.16+ |
| **Sentence encoder** | `all-MiniLM-L6-v2` (384-dimensional embeddings) |
| **Task** | Unsupervised extraction of recurring review themes |
| **Topics discovered** | 8 (auto-selected) |
| **Coherence (c_v)** | 0.54 |
| **Coverage** | 87% of reviews assigned to a named topic |
| **Intended use** | Identify CX pain points; power the CX Action Priority Matrix |
| **Not intended for** | Real-time classification of individual reviews (batch use only) |

---

## Model 4 — Bayesian A/B Model (Beta-Binomial)

| Property | Value |
|:---|:---|
| **Model type** | Bayesian Beta-Binomial with PyMC |
| **Framework** | PyMC 5.x, ArviZ |
| **Task** | Estimate posterior probability that treatment group conversion > control |
| **Prior** | Beta(1,1) — uninformative, equivalent to uniform over [0,1] |
| **Likelihood** | Binomial(n, p) |
| **Posterior summary** | P(treatment > control) = 95.8% |
| **Intended use** | Provide probabilistic decision support for campaign scaling |
| **Not intended for** | Sequential (multi-armed bandit) testing; continuous outcomes |

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
