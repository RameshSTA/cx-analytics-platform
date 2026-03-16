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
[![Assumptions](https://img.shields.io/badge/Assumptions-3A567A?style=flat-square)](modeling_assumptions.md)&nbsp;
![Deployment](https://img.shields.io/badge/Deployment-1A4D8F?style=flat-square)&nbsp;
[![Data Sources](https://img.shields.io/badge/Data_Sources-3A567A?style=flat-square)](data_sources.md)

</div>

---

# Deployment Plan

## Production Readiness Assessment

| Module | Production-Ready? | Status | Next Steps to Production |
|:---|:---:|:---|:---|
| M1 — Segmentation | ⚠️ Partial | Scoring pipeline built; no automated retraining | Add weekly scoring Lambda + S3 output |
| M2 — Forecasting | ✅ **Deployed** | Lambda endpoint live; model in S3 | Add CloudWatch alerting on MAPE drift |
| M3 — NLP | ⚠️ Partial | Batch pipeline built; no real-time endpoint | Add SQS trigger for new review batches |
| M4 — A/B Testing | 📊 Analysis | One-time causal analysis; not a real-time service | Codify as repeatable framework for future campaigns |

---

## Module 2 — Live Forecast Endpoint

### Current Deployment

```
Endpoint:  https://{api-id}.execute-api.ap-southeast-2.amazonaws.com/prod/forecast
Method:    POST
Auth:      API Key (x-api-key header)
Region:    ap-southeast-2 (Sydney)
Runtime:   Python 3.11 on Lambda
Memory:    512 MB
Timeout:   30 seconds
```

### Request Format
```json
{
  "store_id": 85,
  "horizon_weeks": 4,
  "include_anomaly_flags": true
}
```

### Response Format
```json
{
  "store_id": 85,
  "generated_at": "2026-03-16T09:00:00+11:00",
  "horizon_weeks": 4,
  "forecast": [
    {"week": "2026-W12", "predicted_sales": 18420, "lower_80": 16800, "upper_80": 20040},
    {"week": "2026-W13", "predicted_sales": 19100, "lower_80": 17400, "upper_80": 20800},
    {"week": "2026-W14", "predicted_sales": 17600, "lower_80": 15900, "upper_80": 19300},
    {"week": "2026-W15", "predicted_sales": 20300, "lower_80": 18500, "upper_80": 22100}
  ],
  "anomaly_flags": [
    {"week": "2026-W14", "flagged": true, "reason": "2.1 SD below 8-week rolling mean"}
  ],
  "model_version": "lgbm_v1.0.0",
  "mape_benchmark": 0.068
}
```

### Infrastructure

```
cloud/
├── lambda_handler.py       ← Main Lambda function
└── deployment_notes.md     ← Step-by-step setup instructions

S3 bucket: retail-cx-platform/
├── models/
│   └── lgbm_forecast_v1.pkl   (serialised LightGBM model, ~2.8 MB)
└── outputs/
    └── forecasts/
        └── store_{id}_{date}.json
```

---

## Monitoring & Retraining Triggers

### Performance Monitoring

| Metric | Threshold | Action |
|:---|:---|:---|
| Rolling 4-week MAPE | > 10% | Alert on-call data scientist |
| Rolling 4-week MAPE | > 15% | Auto-disable endpoint; rollback to previous model |
| Anomaly flag rate | > 20% of stores in any week | Investigate data pipeline upstream |
| API error rate | > 1% | PagerDuty alert; escalate to engineering |
| Prediction latency | > 5 seconds | Auto-scale Lambda concurrency |

### Retraining Schedule

| Trigger | Action |
|:---|:---|
| Weekly (every Monday 2am AEST) | Append latest week's data; retrain LightGBM on rolling 2-year window |
| MAPE alert crossed | Emergency retrain with extended feature engineering review |
| Major structural event (new centre, tenant departure) | Manual retrain with event indicator features added |
| Post-campaign period | Retrain to capture campaign effect in baseline |

---

## Module 1 — Segmentation Deployment Roadmap

### Phase 1 (Now — Portfolio Demo)
- Batch scoring notebook runs monthly
- Output: `outputs/reports/segment_marketing_brief.md`
- Consumer: Marketing team receives CSV of segment assignments + CLV scores

### Phase 2 (Recommended — Production)
```
EventBridge (monthly trigger)
    → Lambda: run_segmentation_pipeline
        → reads latest transaction export from S3
        → applies RetailDataCleaner + RFMCalculator + CLVModel
        → writes segment_scores.parquet to S3
        → triggers SNS notification to CRM system
        → CRM updates customer profiles with segment tag + CLV score
```

### Phase 3 (Advanced)
- Real-time segment update on each transaction event (Kinesis → Lambda → DynamoDB)
- Segment change detection with automatic campaign trigger

---

## Module 3 — NLP Deployment Roadmap

### Phase 1 (Now — Portfolio Demo)
- Batch pipeline processes review exports weekly
- Output: Topic distribution + CX Priority Matrix updated in dashboard

### Phase 2 (Recommended — Production)
```
SQS Queue: new-retail-reviews
    → Lambda: run_nlp_pipeline
        → DistilBERT sentiment inference (batch)
        → BERTopic topic assignment
        → Update dashboard metrics
        → Flag reviews with sentiment_score < 0.3 for human review queue
```

**Inference cost estimate:** DistilBERT on CPU at 300K reviews/year = ~$45/year on Lambda
**Inference cost on GPU (SageMaker):** ~$180/year — not warranted at this volume

---

## Data Quality Gates

Before any model runs in production, the following gates must pass:

| Gate | Condition | Action if Failed |
|:---|:---|:---|
| Row count check | > 80% of expected rows | Alert + hold scoring |
| Schema validation | All required columns present, correct dtype | Alert + hold scoring |
| Null rate | < 5% nulls in key columns | Impute if < 2%; alert if > 5% |
| Date range | No future-dated records; no records > 3 years old | Flag for review |
| Revenue range | No individual transactions > $50,000 (outlier filter) | Winsorise to $50K |

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
