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
[![Deployment](https://img.shields.io/badge/Deployment-3A567A?style=flat-square)](deployment_plan.md)&nbsp;
![Data Sources](https://img.shields.io/badge/Data_Sources-1A4D8F?style=flat-square)

</div>

---

# Data Sources & Quality

## Overview

The platform uses three real-world, publicly available datasets. Each was selected because it closely mirrors the type of data the operator's Data & Insights team works with: transaction records, operational time series, and unstructured customer feedback at scale.

---

## Dataset 1 — UCI Online Retail II

**Used by:** Module 1 (Customer Segmentation & CLV)

| Property | Value |
|:---|:---|
| Source | UCI Machine Learning Repository |
| URL | https://archive.ics.uci.edu/dataset/502/online+retail+ii |
| File | `data/raw/online_retail_II.xlsx` |
| Size | ~47 MB, 541,909 rows (2 sheets: 2009–2010, 2010–2011) |
| Rows after cleaning | ~398,000 |
| Unique customers | 4,338 |
| Time span | 01 Dec 2009 – 09 Dec 2011 |
| Geography | UK-based retailer, international customers |
| Currency | GBP (£) |

### Schema

| Column | Type | Description |
|:---|:---|:---|
| `InvoiceNo` | String | 6-digit invoice number; 'C' prefix = cancellation |
| `StockCode` | String | Product/item code |
| `Description` | String | Product name (free text; some nulls) |
| `Quantity` | Integer | Units purchased; negative = return/cancellation |
| `InvoiceDate` | Datetime | Date and time of invoice |
| `UnitPrice` | Float | Price per unit in GBP |
| `CustomerID` | Float | Unique customer identifier (nullable) |
| `Country` | String | Country of customer |

### Cleaning Rules Applied

| Rule | Rows Removed | Rationale |
|:---|:---:|:---|
| Remove rows with null CustomerID | ~24,000 | Cannot attribute to a customer for RFM |
| Remove cancellations (InvoiceNo starts with 'C') | ~9,200 | Not a purchase event |
| Remove negative Quantity (non-cancellation returns) | ~2,100 | Data entry errors |
| Remove UnitPrice ≤ 0 | ~400 | Free samples / data errors |
| Remove Quantity > 10,000 (bulk B2B outliers) | ~150 | Non-representative for retail CX |
| Remove non-UK customers for CLV analysis | ~35,000 | Focus on primary market |

### Business Alignment with the retail operator
<p align="justify">
While UCI Online Retail II is a UK e-commerce dataset, its transaction structure (customer ID, product, date, quantity, price) is identical to the transaction feeds that the retail operator receives from its retail partners. The RFM segmentation logic, CLV modelling approach, and segment profiling methodology are directly transferable to the operator's CommBank iQ transaction data.
</p>

---

## Dataset 2 — Rossmann Store Sales

**Used by:** Module 2 (Forecasting) + Module 4 (A/B Testing)

| Property | Value |
|:---|:---|
| Source | Kaggle / Rossmann Pharmaceuticals |
| URL | https://www.kaggle.com/competitions/rossmann-store-sales/data |
| Files | `data/raw/rossmann_train.csv`, `data/raw/rossmann_store.csv` |
| Size | ~38 MB (train) + ~50 KB (store) |
| Rows | 1,017,209 daily store-level rows |
| Stores | 1,115 stores |
| Time span | 01 Jan 2013 – 31 Jul 2015 |
| Geography | Germany |
| Currency | EUR (€) |

### Schema — `rossmann_train.csv`

| Column | Type | Description |
|:---|:---|:---|
| `Store` | Integer | Store ID (1–1,115) |
| `DayOfWeek` | Integer | 1 = Monday, 7 = Sunday |
| `Date` | Date | Observation date |
| `Sales` | Integer | Daily sales in EUR |
| `Customers` | Integer | Number of customers that day |
| `Open` | Binary | 0 = store closed |
| `Promo` | Binary | 1 = company-wide promo active that day |
| `StateHoliday` | String | a=public, b=Easter, c=Christmas, 0=none |
| `SchoolHoliday` | Binary | 1 = school holiday |

### Schema — `rossmann_store.csv`

| Column | Type | Description |
|:---|:---|:---|
| `Store` | Integer | Store ID |
| `StoreType` | String | a/b/c/d — store format category |
| `Assortment` | String | a=basic, b=extra, c=extended |
| `CompetitionDistance` | Float | Distance (m) to nearest competitor |
| `Promo2` | Binary | 1 = store participates in sustained Promo2 loyalty programme |
| `Promo2SinceYear` | Integer | Year Promo2 participation began |
| `Promo2SinceWeek` | Integer | Week of year Promo2 participation began |
| `PromoInterval` | String | Months Promo2 is active (e.g., "Jan,Apr,Jul,Oct") |

### Important Dataset Note for A/B Testing
<p align="justify">
The daily <code>Promo</code> column is <strong>identical across all 1,115 stores on any given day</strong> — it is a company-wide promotional signal, not a per-store treatment variable. This was discovered during Module 4 development and is a key finding: it means <code>Promo</code> cannot be used as a treatment variable for A/B testing. The per-store treatment used in Module 4 is <code>Promo2</code> from <code>store.csv</code>, which varies at the store level based on when each store joined the sustained loyalty programme.
</p>

---

## Dataset 3 — Yelp Open Dataset (Shopping Reviews)

**Used by:** Module 3 (NLP Sentiment Pipeline)

| Property | Value |
|:---|:---|
| Source | Yelp Dataset Challenge |
| URL | https://www.yelp.com/dataset |
| Files | `data/raw/yelp_review.json`, `data/raw/yelp_business.json` |
| Size | ~5.3 GB (review JSON) + ~120 MB (business JSON) |
| Total reviews | 6.9 million |
| Shopping-category reviews | ~850,000 (after business filter) |
| Time span | 2004 – 2022 |
| Geography | USA, Canada |
| Language | English (primary) |

### Schema — `yelp_review.json` (one record per line)

| Field | Type | Description |
|:---|:---|:---|
| `review_id` | String | Unique review identifier |
| `user_id` | String | Reviewer's user ID |
| `business_id` | String | Business being reviewed |
| `stars` | Integer | Rating 1–5 |
| `date` | String | Review date |
| `text` | String | Full review text |
| `useful` | Integer | Community "useful" votes |
| `funny` | Integer | Community "funny" votes |
| `cool` | Integer | Community "cool" votes |

### Sentiment Label Creation
| Stars | Label | Rationale |
|:---:|:---:|:---|
| 1–2 | Negative (0) | Explicit dissatisfaction |
| 3 | Excluded | Ambiguous signal; improves classifier quality |
| 4–5 | Positive (1) | Satisfaction and advocacy |

### Business Alignment with the retail operator
<p align="justify">
Yelp shopping reviews (malls, shopping centres, retail stores) closely replicate the themes present in customer feedback: parking, food court, staff behaviour, cleanliness, amenities, and variety of stores. The sentiment classification and topic modelling methodology would be directly applicable to the operator's own CX survey verbatim data, NPS open-text responses, and Google Reviews data.
</p>

---

## Data Quality Summary

| Dataset | Missing Values | Outliers Handled | Synthetic Fallback |
|:---|:---:|:---:|:---:|
| UCI Online Retail II | 24K nulls in CustomerID (removed) | Quantity, UnitPrice winsorised | ✅ 500-customer synthetic retail dataset |
| Rossmann | Minimal (<0.1%) | Sales=0 on closed days (filtered) | ✅ 50-store synthetic weekly sales |
| Yelp | None in key fields | Star rating extremes included | ✅ 200-review synthetic corpus |

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
