# Customer Experience Analytics Platform — Dashboard Build Guide

**Tool:** Tableau Desktop / Power BI Desktop (both covered below)
**Audience:** Operations, Marketing, CX, Finance teams
**Data sources:** Outputs from notebooks in `data/processed/` + live AWS Lambda endpoint
**Last updated:** March 2026

---

## Overview

Four dashboards are specified — one per platform module. Each is designed for a specific the retail operator team and follows the same design principles:
- Business question first, always visible at the top
- Single key metric prominently displayed (big number)
- Supporting context visuals below
- Filter panel on the left for centre, date range, segment
- brand colours: Primary blue #2E75B6, accent green #70AD47, alert red #FF7043

---

## Dashboard 1 — Visitor Segment Intelligence (Module 1)

**File:** `outputs/processed/rfm_segments.csv`, `outputs/processed/clv_predictions.csv`
**Primary audience:** Marketing Director, CRM team
**Refresh frequency:** Monthly (after loyalty data refresh)

### Layout

```
┌─────────────────────────────────────────────────────────────────────┐
│  CX VISITOR SEGMENT INTELLIGENCE                                     │
│  "Which customers need our attention this month?"                   │
├───────────┬─────────────────────────────────────────────────────────┤
│  FILTERS  │  KPI STRIP: [Total Visitors] [At-Risk CLV] [Champions%] │
│           ├───────────────────┬─────────────────────────────────────┤
│ Centre    │  SEGMENT DONUT    │  MEAN CLV BY SEGMENT (bar chart)    │
│ Date range│  (% of visitors)  │  Champions ████████████ $847        │
│ Segment   │                   │  Loyalists ███████      $412        │
│ Country   │                   │  Potential ████         $186        │
│           │                   │  At-Risk   █████        $268 ⚠️     │
│           │                   │  Dormant   █            $41         │
│           ├───────────────────┴─────────────────────────────────────┤
│           │  SEGMENT PROFILE TABLE                                   │
│           │  (Segment | Count | % | Avg Recency | Avg Frequency |   │
│           │   Avg Monetary | Predicted CLV | Recommended Action)     │
│           ├─────────────────────────────────────────────────────────┤
│           │  AT-RISK ALERT PANEL (conditional on At-Risk count > 0) │
│           │  ⚠️ $2.1M in recoverable CLV | Launch reactivation now  │
└───────────┴─────────────────────────────────────────────────────────┘
```

### Tableau Build Steps

1. **Connect to data:** File → Connect → Text File → `data/processed/rfm_segments.csv`
2. **Calculated field — CLV Alert:** `IF [Segment] = "At-Risk" AND [Predicted CLV] > 200 THEN "⚠️ HIGH VALUE AT-RISK" ELSE "" END`
3. **Segment donut:** Drag Segment to Rows, Customer ID to Columns (Count), Mark type = Pie. Duplicate for donut effect.
4. **CLV bar chart:** Drag Segment to Rows, Predicted CLV to Columns (AVG). Sort descending. Colour by Segment using custom colour palette.
5. **Profile table:** Sheet → Drag Segment, Count(Customer ID), AVG(Recency), AVG(Frequency), AVG(Monetary), AVG(Predicted CLV) to Text mark. Format as table.
6. **At-Risk alert:** Create a parameter-driven KPI card using `{FIXED [Segment]: SUM([Predicted CLV])}` filtered to "At-Risk".
7. **Dashboard assembly:** New Dashboard → drag 4 sheets. Add filter actions (click segment → highlight all sheets).

### Power BI Build Steps

1. **Get Data → Text/CSV → rfm_segments.csv**
2. **Card visual:** Drag `Predicted CLV` to Values, filter to At-Risk. Display as "At-Risk Recoverable CLV: $2.1M"
3. **Donut chart:** Values = Customer ID (count), Legend = Segment, custom colour scheme
4. **Clustered bar:** Y-axis = Segment, X-axis = Predicted CLV (Average). Sorted descending.
5. **Table:** Add Segment, Count of Customer ID, Average Recency, Average Frequency, Average Monetary, Average Predicted CLV
6. **Alert box:** Use DAX `AT_RISK_CLV = CALCULATE(SUM([Predicted CLV]), [Segment] = "At-Risk")` → Conditional formatting: orange background if > 1,000,000

---

## Dashboard 2 — Destination Traffic Command Centre (Module 2)

**File:** `data/processed/weekly_traffic.csv`, `data/processed/forecasts_4w.csv`
**Live data:** AWS Lambda endpoint (REST API connection)
**Primary audience:** Operations Director, Centre Managers
**Refresh frequency:** Weekly (auto on Monday 7am)

### Layout

```
┌─────────────────────────────────────────────────────────────────────┐
│  DESTINATION TRAFFIC COMMAND CENTRE                                  │
│  "What will visitation look like at each centre over the next month?"│
├───────────┬─────────────────────────────────────────────────────────┤
│  FILTERS  │  KPI STRIP: [Portfolio Total Forecast] [#Anomalies] [MAPE]│
│           ├─────────────────────────────────────────────────────────┤
│ Centre    │  4-WEEK FORECAST CHART (line chart)                     │
│ Week      │  — Historical (solid blue)                              │
│ Alert     │  — Forecast (dashed red)                                │
│   threshold│  — 80% Prediction Interval (shaded)                    │
│           │  — Anomaly flags (red ⚠ markers)                        │
│           ├─────────────────────────────────────────────────────────┤
│           │  DESTINATION RANKING TABLE  │  ANOMALY ALERT FEED       │
│           │  (Forecast vs last year)    │  ⚠️ Dest 042: -18% below  │
│           │  ▲ up  ▼ down  ◆ anomaly   │  ⚠️ Dest 017: -14% below  │
│           │                             │  📋 View all alerts        │
└───────────┴─────────────────────────────────────────────────────────┘
```

### Key Tableau Calculations

```
// Forecast vs Actual Variance %
[Variance %] = (SUM([Weekly Sales]) - SUM([Forecast])) / SUM([Forecast])

// Anomaly flag colour
[Anomaly Colour] = IF [Is Anomaly] = 1 THEN "#FF7043" ELSE "#2E75B6" END

// Alert text
[Alert Message] = IF ABS([Variance %]) > 0.15
  THEN "⚠️ " + [Destination Name] + ": " + STR(ROUND([Variance %]*100, 1)) + "% deviation"
  ELSE "" END
```

### Power BI DAX Measures

```dax
Forecast Accuracy =
DIVIDE(
    SUMX('forecasts', ABS([weekly_sales] - [yhat])),
    SUMX('forecasts', [weekly_sales])
)

Portfolio 4-Week Forecast =
CALCULATE(SUM('forecasts'[yhat]), DATESINPERIOD('forecasts'[ds], TODAY(), 4, WEEK))
```

---

## Dashboard 3 — CX Theme Intelligence (Module 3)

**File:** `data/processed/reviews_processed.csv`, `data/processed/cx_priority_matrix.csv`
**Primary audience:** CX Director, Marketing team
**Refresh frequency:** Monthly

### Layout

```
┌─────────────────────────────────────────────────────────────────────┐
│  CX EXPERIENCE INTELLIGENCE                                          │
│  "What are customers saying — and what needs fixing first?"          │
├───────────┬─────────────────────────────────────────────────────────┤
│  FILTERS  │  KPI STRIP: [Total Reviews] [Positive Rate] [Top Issue] │
│           ├─────────────────────────────────────────────────────────┤
│ Centre    │  CX PRIORITY MATRIX (bubble chart)      │ TREND LINE    │
│ Date range│  — X: Review Volume                     │ (quarterly    │
│ Topic     │  — Y: Negative Rate                     │ pos/neg rate) │
│ Sentiment │  — Size: Volume                         │               │
│           │  — Colour: Quadrant                     │               │
│           │  — Labels: Topic name                   │               │
│           ├─────────────────────────────────────────────────────────┤
│           │  TOPIC DRILL-DOWN TABLE                                  │
│           │  (Topic | Volume | +Sent% | -Sent% | Trend | Action)    │
│           ├─────────────────────────────────────────────────────────┤
│           │  SAMPLE REVIEW FEED (filtered by selected topic)        │
└───────────┴─────────────────────────────────────────────────────────┘
```

### Bubble Chart Implementation (Tableau)

1. X-axis: `SUM([Review Count])` per topic
2. Y-axis: `AVG([Negative Rate])` per topic — calculate as `COUNTD(IF [BERT Label] = "NEGATIVE" THEN [Review ID] END) / COUNTD([Review ID])`
3. Size: `SUM([Review Count])`
4. Colour: Custom calculated field for quadrant (Fix Immediately = red, Monitor = blue, Quick Win = orange, Low Priority = grey)
5. Label: `[Topic Name]`
6. Reference lines: median X and median Y → creates quadrant dividers

### Sentiment Trend (Tableau)

1. Connect date field, truncate to Month
2. Dual-axis: Area chart (positive rate) + Line chart (negative rate)
3. Add band annotation for COVID period (2020–2021) and Christmas peaks

---

## Dashboard 4 — Campaign Effectiveness Tracker (Module 4)

**File:** `data/processed/ab_test_results.csv`
**Primary audience:** Marketing Director, CFO
**Refresh frequency:** Per campaign (not ongoing)

### Layout

```
┌─────────────────────────────────────────────────────────────────────┐
│  CAMPAIGN EFFECTIVENESS DASHBOARD                                    │
│  "Did the promotion work — and by how much?"                         │
├───────────┬─────────────────────────────────────────────────────────┤
│  FILTERS  │  VERDICT PANEL                                          │
│           │  ┌─────────────────────────────────────────────────────┐│
│ Campaign  │  │  CAMPAIGN LIFT: +11.3%  ✅ STATISTICALLY CONFIRMED  ││
│ Date range│  │  90% Confidence Interval: 8.1% — 14.6%              ││
│ Dest type │  │  Probability lift is real: 97.8%                    ││
│           │  │  Estimated revenue impact: $890K (pilot) / $4.7M    ││
│           │  └─────────────────────────────────────────────────────┘│
│           ├─────────────────────────────────────────────────────────┤
│           │  BEFORE/AFTER COMPARISON     │  TREATMENT vs CONTROL   │
│           │  (bar chart: avg weekly      │  (dual line: weekly     │
│           │  sales pre vs post)          │  sales over time)       │
│           ├─────────────────────────────────────────────────────────┤
│           │  DESTINATION-LEVEL RESULTS TABLE                        │
│           │  (Destination | Pre-avg | Post-avg | Lift % | Status)  │
└───────────┴─────────────────────────────────────────────────────────┘
```

---

## Design System Reference

### Colour Palette (Both Tools)

| Name | Hex | Use |
|------|-----|-----|
| the retail operator Blue | #2E75B6 | Primary data series, headers |
| the retail operator Dark Blue | #1A4D8F | Backgrounds, emphasis |
| the retail operator Green | #70AD47 | Positive sentiment, growth indicators |
| the retail operator Amber | #FFC000 | Warning, moderate |
| the retail operator Red | #FF7043 | Negative sentiment, alerts, anomalies |
| Dark Grey | #212121 | Text, axes |
| Mid Grey | #9E9E9E | Secondary labels |
| Light Grey | #F5F5F5 | Background fill |

### Typography

- **Tableau:** Tableau Book for body, Tableau Bold for KPI numbers
- **Power BI:** Segoe UI for body, Segoe UI Semibold for headers and KPI values

### Standard KPI Card Format

```
┌─────────────────────┐
│  $2.1M              │  ← KPI value (large, bold, brand colour)
│  At-Risk Recoverable│  ← Label (small, grey)
│  CLV                │
│  ▲ +18% vs last qtr │  ← Trend indicator (green up / red down)
└─────────────────────┘
```

### Tooltip Standard

Every chart should include a tooltip showing:
- Destination name / Segment / Topic name
- Exact value
- Comparison vs period average
- Recommended action (for CX topics and segments)

---

## Publishing & Access

### Tableau Server
1. Publish to Tableau Server: Server → Publish Workbook
2. Set data refresh schedule: Daily at 6am AEST
3. Share with groups: Operations (Dashboard 2), Marketing (Dashboards 1 + 4), CX Team (Dashboard 3)
4. Embed in the corporate intranet via embedded URL

### Power BI Service
1. Publish to Power BI Workspace: "Retail Analytics"
2. Set scheduled refresh: Power BI Service → Datasets → Schedule Refresh
3. Share dashboard via Power BI app (available on iOS/Android for centre managers)
4. Set row-level security: Centre Managers see only their assigned destinations

---

*For questions about data sources or methodology, contact the Data & Analytics team. For dashboard design changes, consult the brand guidelines before modifying colours or typography.*
