<div align="center">
  <img src="../assets/header_banner.svg" width="100%" alt="Customer Experience Analytics Platform"/>
</div>

<div align="center">

[![README](https://img.shields.io/badge/README-3A567A?style=flat-square)](../README.md)&nbsp;
[![Business Problem](https://img.shields.io/badge/Business_Problem-3A567A?style=flat-square)](business_problem.md)&nbsp;
![Architecture](https://img.shields.io/badge/Architecture-1A4D8F?style=flat-square)&nbsp;
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

# Architecture Overview

## System Design Philosophy

<p align="justify">
The platform is designed around three principles. First, <strong>modularity</strong>: each analytical module (segmentation, forecasting, NLP, A/B testing) is fully self-contained — it can be developed, tested, and deployed independently. Second, <strong>reproducibility</strong>: every notebook is deterministically reproducible from raw data, with pinned dependencies, fixed random seeds, and synthetic data fallbacks so reviewers can run the full pipeline without needing proprietary datasets. Third, <strong>production readiness</strong>: the platform is not a research artifact — Module 2's LightGBM model is deployed as a live AWS Lambda endpoint, and the src/ library is structured as a proper Python package with typed interfaces and docstrings throughout.
</p>

---

## Data Flow

```
┌─────────────────────────────────────────────────────────────────────────┐
│                         RAW DATA SOURCES                                │
│   UCI Online Retail II    Rossmann Store Sales     Yelp Open Dataset    │
│   (541,909 transactions)  (1,017,209 rows)         (6.7M reviews)       │
└───────────────┬─────────────────────┬──────────────────┬───────────────┘
                │                     │                  │
                ▼                     ▼                  ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                       00_EDA.ipynb (Exploration)                        │
│         Schema validation · Distributions · Missing value audit         │
│         Correlation maps · Business hypothesis generation               │
└───────────────┬─────────────────────┬──────────────────┬───────────────┘
                │                     │                  │
        ┌───────▼──────┐     ┌────────▼──────┐  ┌───────▼──────────────┐
        │ M1            │     │ M2 + M4       │  │ M3                   │
        │ 01_segment.   │     │ 02_forecast.  │  │ 03_nlp_pipeline.     │
        │ ipynb         │     │ ipynb         │  │ ipynb                │
        └───────┬──────┘     └────────┬──────┘  └───────┬──────────────┘
                │                     │                  │
        ┌───────▼──────┐     ┌────────▼──────┐  ┌───────▼──────────────┐
        │ RFM Engine   │     │ SARIMA        │  │ TextPreprocessor      │
        │ K-Means (k=5)│     │ Prophet       │  │ VADER baseline        │
        │ XGBoost CLV  │     │ LightGBM      │  │ DistilBERT classifier │
        │              │     │ IsolationForest│ │ BERTopic modeller     │
        └───────┬──────┘     └────────┬──────┘  └───────┬──────────────┘
                │                     │                  │
                └─────────────────────┼──────────────────┘
                                      │
                              ┌───────▼───────┐
                              │    OUTPUTS    │
                              │  charts/      │
                              │  reports/     │
                              └───────┬───────┘
                                      │
                              ┌───────▼───────┐
                              │  04_ab_test.  │
                              │  ipynb        │
                              │  (uses M2     │
                              │   data)       │
                              └───────┬───────┘
                                      │
                              ┌───────▼───────┐
                              │ AWS Lambda    │
                              │ LightGBM      │
                              │ Forecast API  │
                              └───────────────┘
```

---

## Module Responsibilities

### Module 0 — EDA (`00_EDA.ipynb`)
- Ingests all three raw datasets
- Produces schema reports, distribution charts, and correlation analyses
- Documents anomalies and cleaning decisions for downstream modules
- Outputs: `eda_retail_overview.png`, `eda_rossmann_*.png`, `eda_yelp_overview.png`

### Module 1 — Customer Segmentation + CLV (`01_segmentation.ipynb`)
- **Input:** UCI Online Retail II (541,909 transactions, 4,338 unique customers)
- **Pipeline:** Transaction cleaning → RFM computation → K-Means (k=5, selected by elbow + silhouette) → segment profiling → XGBoost CLV regression with 80/20 temporal split
- **Outputs:** 5 named segments with CLV attached, At-Risk recovery brief, 5 charts
- **src/ classes used:** `RetailDataCleaner`, `RFMCalculator`, `CustomerSegmenter`, `CLVModel`

### Module 2 — Forecasting (`02_forecasting.ipynb`)
- **Input:** Rossmann Store Sales (1,115 stores, 1,017,209 rows, 2013–2015)
- **Pipeline:** Weekly aggregation → SARIMA baseline → Prophet with Australian holidays → LightGBM multi-step with lag features → 4-week ahead forecast → Isolation Forest anomaly flags
- **Outputs:** MAPE comparison table, 4-week forecast chart, feature importance, 7 charts
- **src/ classes used:** `TimeSeriesPreprocessor`, `ProphetForecaster`, `LGBMForecaster`, `AnomalyFlagger`
- **Cloud:** LightGBM model serialised and deployed via `cloud/lambda_handler.py`

### Module 3 — NLP Sentiment (`03_nlp_pipeline.ipynb`)
- **Input:** Yelp Open Dataset — Shopping category reviews (up to 1M reviews)
- **Pipeline:** spaCy tokenisation + NLTK cleaning → VADER lexicon baseline → DistilBERT fine-tuning (binary sentiment) → BERTopic unsupervised topic extraction → CX Action Priority Matrix (impact × prevalence × fix-ease)
- **Outputs:** Topic heatmap, sentiment trend, priority matrix, F1 report, 5 charts
- **src/ classes used:** `TextPreprocessor`, `SentimentClassifier`, `TopicModeller`, `CXActionMatrix`

### Module 4 — A/B Testing & Causal Inference (`04_ab_testing.ipynb`)
- **Input:** Rossmann Store Sales + Store metadata (Promo2 treatment assignment)
- **Pipeline:** Matched-pair design (54 H2-2013 Promo2 starters vs 54 nearest-neighbour controls) → balance validation (Welch t, p=0.871) → Welch t-test → Mann-Whitney U → Bayesian A/B (PyMC Beta-Binomial) → Difference-in-Differences (entity-demeaned OLS, clustered SE) → revenue impact model
- **Outputs:** Descriptive stats, Bayesian posterior, parallel trends chart, 3 charts

---

## Source Library Structure

```
src/
├── preprocessor.py     # RetailDataCleaner, RossmannCleaner
│                        — validation, outlier removal, type casting
├── segmentation.py     # RFMCalculator, CustomerSegmenter, CLVModel
│                        — RFM scoring, K-Means wrapper, XGBoost CLV
├── forecasting.py      # TimeSeriesPreprocessor, ProphetForecaster,
│                        LGBMForecaster, AnomalyFlagger
├── nlp_pipeline.py     # TextPreprocessor, SentimentClassifier,
│                        TopicModeller, CXActionMatrix
└── viz.py              # set_brand_style(), WF_PALETTE dict,
                         plot_rfm_scatter(), plot_forecast_comparison()
```

All classes follow a `fit() / transform()` / `predict()` interface consistent with scikit-learn conventions. Every public method carries a Google-style docstring with Args, Returns, and Raises sections.

---

## Cloud Architecture

```
Centre Manager / Data Team
          │
          │  HTTP POST
          │  {"store_id": 85, "horizon_weeks": 4}
          ▼
    API Gateway (AWS)
          │
          ▼
    Lambda Function (Python 3.11)
    lambda_handler.py
    ├── loads pre-trained LightGBM model from S3
    ├── constructs lag + holiday + store features
    ├── runs multi-step recursive forecast
    └── returns JSON: {"store": 85, "forecast": [...], "anomaly_flags": [...]}
          │
          ▼
    S3 bucket
    retail-cx-forecasts/
    ├── models/lgbm_forecast_v1.pkl
    └── outputs/store_{id}_forecast_{date}.json
```

**Cold start:** ~1.8 seconds (model loaded from S3 on first invocation)
**Warm latency:** ~180ms per request
**Cost at 1,000 requests/day:** ~$0.40/month (well within Lambda free tier)

---

## Technology Decisions

| Decision | Chosen | Alternatives Considered | Rationale |
|:---|:---|:---|:---|
| Segmentation algorithm | K-Means (k=5) | DBSCAN, GMM, Hierarchical | Interpretable, scalable, business-friendly cluster count |
| CLV model | XGBoost regression | BG/NBD + Gamma-Gamma, Ridge | Better handles non-linear RFM interactions; no distributional assumptions |
| Forecast baseline | SARIMA | Exponential Smoothing, Naïve | Standard benchmark; interpretable AR/MA structure |
| Production forecast | LightGBM | Prophet, LSTM, N-BEATS | Best MAPE; fast inference; easy Lambda packaging |
| Sentiment model | DistilBERT | VADER-only, BERT-base, RoBERTa | 97% of BERT accuracy at 60% size; fine-tunable on retail reviews |
| Topic model | BERTopic | LDA, NMF, Top2Vec | Coherent topics without fixed k; leverages sentence embeddings |
| Causal method | DiD + Bayesian | Propensity Score Matching, IV | DiD handles selection bias with panel data; Bayesian adds probabilistic decision layer |
| Cloud runtime | AWS Lambda | AWS SageMaker, GCP Vertex | Serverless; zero idle cost; right-sized for a 4-week forecast endpoint |

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
