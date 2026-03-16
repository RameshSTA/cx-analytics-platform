# Data Dictionary — Customer Experience Analytics Platform

All datasets are publicly available proxies. They are framed in the retail operator/the retail operator terminology throughout the project.

---

## Module 1 — UCI Online Retail II
**Source:** https://archive.ics.uci.edu/dataset/502/online+retail+ii
**File:** `data/raw/online_retail_II.xlsx`
**Rows:** ~1,067,371 transactions | **Period:** 2009-12-01 to 2011-12-09
**Business framing:** Each transaction = a visitor purchase at a retail partner

| Column | Type | Description | Platform Mapping |
|--------|------|-------------|-------------------|
| `Invoice` | string | Unique invoice number. Prefix 'C' = cancellation | Transaction ID |
| `StockCode` | string | Product/item code | SKU at retail partner |
| `Description` | string | Product name | Item purchased |
| `Quantity` | integer | Units purchased (negative = return/cancellation) | Units per visit |
| `InvoiceDate` | datetime | Date and time of transaction | Visit timestamp |
| `Price` | float | Unit price in GBP | Unit spend (AUD equivalent) |
| `Customer ID` | float | Unique customer identifier (nullable) | retail visitor ID |
| `Country` | string | Customer's country | Destination country |

**Derived RFM Features:**

| Feature | Formula | Business Meaning |
|---------|---------|-----------------|
| `recency` | (ref_date - max InvoiceDate).days | Days since last centre visit |
| `frequency` | count(unique Invoice) per customer | Number of centre visits |
| `monetary` | sum(Quantity × Price) per customer | Total lifetime spend at the retail operator |
| `revenue` | Quantity × Price | Revenue per line item |

---

## Modules 2 & 4 — Rossmann Store Sales
**Source:** https://www.kaggle.com/competitions/rossmann-store-sales/data
**Files:** `data/raw/rossmann_train.csv`, `data/raw/rossmann_store.csv`
**Rows:** 1,017,209 (train.csv) + 1,115 stores
**Business framing:** Each store = a retail destination; Sales = weekly visitation index

### rossmann_train.csv

| Column | Type | Description | Platform Mapping |
|--------|------|-------------|-------------------|
| `Store` | integer | Unique store identifier (1–1115) | retail destination ID |
| `DayOfWeek` | integer | Day of week (1=Mon, 7=Sun) | Day of visit |
| `Date` | date | Transaction date | Visit date |
| `Sales` | integer | Daily turnover in EUR | Daily visitation proxy |
| `Customers` | integer | Number of customers that day | Daily footfall |
| `Open` | binary | 0=closed, 1=open | Destination operating status |
| `Promo` | binary | 1=promotion running that day | Campaign active flag |
| `StateHoliday` | string | a=public, b=Easter, c=Christmas, 0=none | Holiday type |
| `SchoolHoliday` | binary | 1=school holiday | School holiday flag |

### rossmann_store.csv

| Column | Type | Description | Platform Mapping |
|--------|------|-------------|-------------------|
| `Store` | integer | Store identifier | Destination ID |
| `StoreType` | string | Store format (a, b, c, d) | Centre format/tier |
| `Assortment` | string | Assortment level (a=basic, b=extra, c=extended) | Tenancy mix tier |
| `CompetitionDistance` | float | Distance to nearest competitor (metres) | Competitive radius |
| `CompetitionOpenSinceMonth` | float | Month competitor opened | Competitor tenure |
| `CompetitionOpenSinceYear` | float | Year competitor opened | Competitor entry year |
| `Promo2` | binary | 1=participating in ongoing promo | Loyalty program flag |
| `Promo2SinceWeek` | float | Week Promo2 started | Campaign start week |
| `Promo2SinceYear` | float | Year Promo2 started | Campaign start year |
| `PromoInterval` | string | Months Promo2 restarts (e.g. 'Jan,Apr,Jul,Oct') | Campaign cycle |

**Derived Features (Module 2):**

| Feature | Formula | Business Meaning |
|---------|---------|-----------------|
| `lag_1w` | Sales shifted 1 week | Last week's visitation |
| `lag_4w` | Sales shifted 4 weeks | Same period last month |
| `lag_52w` | Sales shifted 52 weeks | Same week last year |
| `roll_4w` | 4-week rolling mean | Short-term trend |
| `roll_12w` | 12-week rolling mean | Quarterly trend |
| `is_christmas_period` | Date in Dec 15 – Jan 5 | Christmas trading window |
| `is_easter_period` | Date within 2 weeks of Easter | Easter trading window |
| `weekly_sales` | sum(Sales) per Store per ISO week | Weekly visitation index |

---

## Module 3 — Yelp Open Dataset
**Source:** https://www.yelp.com/dataset
**Files:** `data/raw/yelp_review.json`, `data/raw/yelp_business.json`
**Target rows:** ~50,000–100,000 (after filtering to Shopping category)
**Business framing:** Each review = a retail visitor feedback response

### yelp_business.json (relevant fields)

| Field | Type | Description | Platform Mapping |
|-------|------|-------------|-------------------|
| `business_id` | string | Unique business identifier | Retail partner / destination ID |
| `name` | string | Business name | Retail partner name |
| `city` | string | City | Destination city |
| `state` | string | State/province | Destination state |
| `stars` | float | Average star rating | Average satisfaction score |
| `review_count` | integer | Total number of reviews | Feedback volume |
| `categories` | string | Comma-separated category tags | Used to filter: 'Shopping', 'Department Stores' |

### yelp_review.json (relevant fields)

| Field | Type | Description | Platform Mapping |
|-------|------|-------------|-------------------|
| `review_id` | string | Unique review identifier | Feedback response ID |
| `user_id` | string | Reviewer identifier | Anonymised visitor ID |
| `business_id` | string | Business reviewed | Destination / retailer ID |
| `stars` | integer | Star rating (1–5) | Satisfaction rating |
| `date` | date | Review date | Feedback submission date |
| `text` | string | Full review text | Customer verbatim feedback |
| `useful` | integer | Helpful votes | Engagement signal |

**Derived NLP Features:**

| Feature | Source | Description |
|---------|--------|-------------|
| `cleaned_text` | `text` | Preprocessed, lemmatised text |
| `vader_compound` | `cleaned_text` | VADER compound sentiment score (-1 to +1) |
| `bert_label` | `cleaned_text` | DistilBERT binary label (POSITIVE/NEGATIVE) |
| `bert_score` | `cleaned_text` | DistilBERT confidence score (0–1) |
| `topic_id` | `cleaned_text` | BERTopic topic assignment (integer) |
| `topic_name` | `topic_id` | Human-readable topic label |

---

## Processed Outputs

| File | Generated By | Description |
|------|-------------|-------------|
| `data/processed/rfm_segments.csv` | 01_segmentation.ipynb | Customer RFM scores + segment labels |
| `data/processed/clv_predictions.csv` | 01_segmentation.ipynb | 90-day CLV predictions per customer |
| `data/processed/weekly_traffic.csv` | 02_forecasting.ipynb | Weekly visitation index per destination |
| `data/processed/forecasts_4w.csv` | 02_forecasting.ipynb | 4-week ahead forecasts per destination |
| `data/processed/reviews_processed.csv` | 03_nlp_pipeline.ipynb | Preprocessed reviews with sentiment + topic |
| `data/processed/cx_priority_matrix.csv` | 03_nlp_pipeline.ipynb | Topic × sentiment × volume summary |
| `data/processed/ab_test_results.csv` | 04_ab_testing.ipynb | Treatment/control groups with outcomes |
