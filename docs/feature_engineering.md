<div align="center">
  <img src="../assets/header_banner.svg" width="100%" alt="Customer Experience Analytics Platform"/>
</div>

<div align="center">

[![README](https://img.shields.io/badge/README-3A567A?style=flat-square)](../README.md)&nbsp;
[![Business Problem](https://img.shields.io/badge/Business_Problem-3A567A?style=flat-square)](business_problem.md)&nbsp;
[![Architecture](https://img.shields.io/badge/Architecture-3A567A?style=flat-square)](architecture_overview.md)&nbsp;
[![Model Card](https://img.shields.io/badge/Model_Card-3A567A?style=flat-square)](model_card.md)&nbsp;
![Feature Engineering](https://img.shields.io/badge/Feature_Engineering-1A4D8F?style=flat-square)&nbsp;
[![Evaluation](https://img.shields.io/badge/Evaluation-3A567A?style=flat-square)](evaluation_strategy.md)&nbsp;
[![Statistical Methods](https://img.shields.io/badge/Statistical_Methods-3A567A?style=flat-square)](statistical_methods.md)&nbsp;
[![Business Impact](https://img.shields.io/badge/Business_Impact-3A567A?style=flat-square)](business_impact_and_roi.md)&nbsp;
[![Assumptions](https://img.shields.io/badge/Assumptions-3A567A?style=flat-square)](modeling_assumptions.md)&nbsp;
[![Deployment](https://img.shields.io/badge/Deployment-3A567A?style=flat-square)](deployment_plan.md)&nbsp;
[![Data Sources](https://img.shields.io/badge/Data_Sources-3A567A?style=flat-square)](data_sources.md)

</div>

---

# Feature Engineering

## Design Principles

<p align="justify">
All features in this platform are designed with three constraints: (1) <strong>leakage-free</strong> — no feature uses information from the evaluation period during training; (2) <strong>interpretable</strong> — every feature has a clear business meaning that a non-technical stakeholder can understand; (3) <strong>computationally stable</strong> — features are robust to missing values, outliers, and schema changes in the upstream data.
</p>

---

## Module 1 — RFM + CLV Features

### RFM Core Features

| Feature | Formula | Business Meaning | Notes |
|:---|:---|:---|:---|
| `recency_days` | Days since last purchase | How recently did this customer buy? | Lower = more engaged |
| `frequency` | Count of unique invoice dates | How often do they buy? | Excludes cancellations |
| `monetary_value` | Sum of (Quantity × UnitPrice) | How much have they spent? | Winsorised at 99th pct |
| `recency_rank` | Percentile rank of recency (inverted) | Recency score 1–5 | 5 = most recent |
| `frequency_rank` | Percentile rank of frequency | Frequency score 1–5 | 5 = most frequent |
| `monetary_rank` | Percentile rank of monetary value | Monetary score 1–5 | 5 = highest value |
| `rfm_combined` | R + F + M rank average | Overall engagement index | Used for segment labelling |

### CLV Regression Features (additional)

| Feature | Description | Leakage Check |
|:---|:---|:---|
| `avg_order_value` | Mean spend per invoice | ✅ Computed from training window only |
| `order_interval_std` | Std dev of days between orders | ✅ Training window only |
| `unique_products` | Count of unique StockCodes purchased | ✅ Training window only |
| `return_rate` | Proportion of invoices with negative quantity | ✅ Training window only |
| `weekday_preference` | Modal purchase weekday (0=Mon, 6=Sun) | ✅ Training window only |
| `months_active` | Months between first and last purchase | ✅ Training window only |

---

## Module 2 — Time Series Features

### Temporal Features (LightGBM)

| Feature | Description | Importance Rank |
|:---|:---|:---:|
| `sales_lag_1` | Weekly sales, 1 week prior | 1st |
| `sales_lag_52` | Weekly sales, same week last year | 2nd |
| `sales_lag_4` | Weekly sales, 4 weeks prior | 3rd |
| `sales_lag_2` | Weekly sales, 2 weeks prior | 4th |
| `sales_lag_8` | Weekly sales, 8 weeks prior | 5th |
| `rolling_mean_4w` | 4-week rolling average | 6th |
| `rolling_std_4w` | 4-week rolling std (volatility) | 7th |
| `week_of_year` | ISO week number (1–52) | 8th |
| `is_school_holiday` | Binary: Australian school holiday week | 9th |
| `is_state_event` | Binary: major state public holiday | 10th |
| `promo_flag` | Weekly Promo flag from dataset | 11th |
| `store_type` | Store category (A/B/C/D) one-hot | 12th |
| `competition_distance` | Distance to nearest competitor (km) | 13th |

### SARIMA + Prophet Regressors

| Feature | Model | Treatment |
|:---|:---|:---|
| Trend | Both | Estimated from data (SARIMA differencing; Prophet piecewise linear) |
| Seasonality (annual) | Both | SARIMA: seasonal order (1,1,1,52); Prophet: yearly_seasonality=True |
| Seasonality (weekly) | Prophet | weekly_seasonality=True (Mon–Sun pattern) |
| Holiday effects | Prophet | Australian public holidays via `workalendar` package |
| Changepoints | Prophet | Auto-detected (up to 25 changepoints, prior_scale=0.05) |

---

## Module 3 — NLP Features

### Text Preprocessing Pipeline

| Step | Action | Rationale |
|:---|:---|:---|
| Lowercasing | Convert to lowercase | Normalise case variation |
| HTML stripping | Remove `<br>`, `&amp;`, etc. | Yelp reviews contain HTML fragments |
| URL removal | Regex `https?://\S+` → `""` | URLs add noise, no semantic value |
| Punctuation | Retain sentence-ending `.!?`; strip others | Preserve sentiment signals |
| Negation handling | `n't`, `not`, `never` preserved | Critical for sentiment accuracy |
| Stopword removal | NLTK English stopwords (NLP tasks only) | Sentiment: retained; Topic: removed |
| Lemmatisation | spaCy `en_core_web_sm` | Reduces vocabulary size for BERTopic |
| Token length filter | Remove tokens < 2 or > 30 chars | Remove noise tokens |

### DistilBERT Input Features

| Feature | Description |
|:---|:---|
| `input_ids` | Tokenised text, max_length=128, truncated |
| `attention_mask` | 1 for real tokens, 0 for padding |
| `label` | Binary: 1 = positive, 0 = negative |

### BERTopic Embeddings

| Component | Setting |
|:---|:---|
| Sentence encoder | `all-MiniLM-L6-v2` (384-dim) |
| Dimensionality reduction | UMAP (n_neighbors=15, n_components=5) |
| Clustering | HDBSCAN (min_cluster_size=50) |
| Representation | c-TF-IDF with MMR for diverse keywords |

---

## Module 4 — Experimental Features

### Store-Level Features for Matching

| Feature | Description | Use |
|:---|:---|:---|
| `pre_mean_sales` | Mean weekly sales H1 2013 | Primary matching variable |
| `store_type` | A/B/C/D categorical | Balance check |
| `assortment` | a/b/c categorical | Balance check |
| `competition_distance` | Distance to nearest competitor | Balance check |
| `promo2` | Binary Promo2 participant | Treatment assignment |
| `promo2_since_week` | Week Promo2 started | Treatment timing |
| `promo2_since_year` | Year Promo2 started | Treatment cohort |

### DiD Panel Features

| Feature | Description |
|:---|:---|
| `treat` | 1 if store is in treatment group, 0 if control |
| `post` | 1 if week is in H2 2013 (campaign period), 0 if H1 2013 |
| `treat_post` | Interaction term (treat × post) — the DiD estimand |
| `y_dm` | Store-demeaned weekly sales (entity fixed effects) |
| `post_dm` | Store-demeaned post indicator |
| `tp_dm` | Store-demeaned treat_post interaction |

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
