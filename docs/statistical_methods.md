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
![Statistical Methods](https://img.shields.io/badge/Statistical_Methods-1A4D8F?style=flat-square)&nbsp;
[![Business Impact](https://img.shields.io/badge/Business_Impact-3A567A?style=flat-square)](business_impact_and_roi.md)&nbsp;
[![Assumptions](https://img.shields.io/badge/Assumptions-3A567A?style=flat-square)](modeling_assumptions.md)&nbsp;
[![Deployment](https://img.shields.io/badge/Deployment-3A567A?style=flat-square)](deployment_plan.md)&nbsp;
[![Data Sources](https://img.shields.io/badge/Data_Sources-3A567A?style=flat-square)](data_sources.md)

</div>

---

# Statistical Methods Reference

## Module 1 — Segmentation & CLV

### RFM Analysis
<p align="justify">
RFM (Recency, Frequency, Monetary) is a customer segmentation framework first formalised by Hughes (1994) and widely used in retail analytics. Each customer receives three scores: Recency (days since last purchase — lower is better), Frequency (number of distinct purchase dates), and Monetary value (total spend). Scores are computed as percentile ranks (1–5) and combined into a composite engagement index. The RFM framework is used here as a feature space for K-Means clustering, not as a rule-based labelling system — which allows the data to determine segment boundaries rather than imposing arbitrary thresholds.
</p>

### K-Means Clustering
**Objective function:**
```
argmin Σᵢ Σₓ∈Cᵢ ||x - μᵢ||²
```
Where `Cᵢ` is cluster i and `μᵢ` is its centroid. K-Means minimises total within-cluster variance.

**k selection:** The elbow method plots inertia (total within-cluster sum of squares) against k. The optimal k is the "elbow" — where marginal inertia reduction drops sharply. Validated by Silhouette Score = (b - a) / max(a, b), where a = mean intra-cluster distance, b = mean distance to nearest other cluster. Score range: [-1, 1]; values > 0.5 indicate well-separated clusters.

**Result:** k=5, Silhouette = 0.62 (strong separation)

### XGBoost CLV Regression
<p align="justify">
XGBoost (Chen & Guestrin, 2016) builds an ensemble of decision trees additively, where each tree corrects the residuals of the previous ensemble. The final prediction is the sum of all tree outputs plus a base score. Regularisation (L1 and L2 on leaf weights) prevents overfitting. The temporal train/test split prevents data leakage: all features are computed exclusively from the training window, and evaluation uses held-out customers' actual future spend.
</p>

---

## Module 2 — Forecasting

### SARIMA
SARIMA(p,d,q)(P,D,Q,s) — Seasonal AutoRegressive Integrated Moving Average:
```
Φ(Bˢ) φ(B) ∇ᴰₛ ∇ᵈ yₜ = Θ(Bˢ) θ(B) εₜ
```
Where B is the backshift operator, ∇ is the differencing operator, and (p,d,q)(P,D,Q,52) are the non-seasonal and seasonal orders respectively. Parameters estimated by maximum likelihood. Model order selected by AIC minimisation.

**Fitted model:** SARIMA(1,1,1)(1,1,1,52) — AIC = 8,214

### Facebook Prophet
Prophet (Taylor & Letham, 2018) decomposes time series as:
```
y(t) = g(t) + s(t) + h(t) + ε(t)
```
Where g(t) is the piecewise-linear trend, s(t) is Fourier-series seasonality, h(t) captures holiday effects (Australian public holidays via `workalendar`), and ε(t) is error. Changepoints are automatically detected and given a Laplace prior to prevent overfitting.

### LightGBM Multi-Step Forecasting
Multi-step forecasting is implemented recursively: the model is trained to predict 1 step ahead, then used iteratively to produce the 4-week forecast. At each step, the previous prediction is used as the lag-1 feature. This introduces compounding error but is more robust to distribution shifts than a direct 4-step model.

Feature importance is measured by gain (total reduction in squared loss attributable to splits on that feature).

### Isolation Forest Anomaly Detection
<p align="justify">
Isolation Forest (Liu et al., 2008) isolates anomalies by randomly partitioning the feature space. Anomalous points are isolated in fewer splits than normal points, yielding a shorter average path length. The anomaly score is: score(x, n) = 2^(-E(h(x)) / c(n)), where E(h(x)) is the expected path length and c(n) is the average path length for n samples. Points with score > 0.6 are flagged as anomalous (contamination = 5%).
</p>

---

## Module 3 — NLP

### VADER Sentiment Analysis
VADER (Valence Aware Dictionary and sEntiment Reasoner, Hutto & Gilbert, 2014) is a lexicon and rule-based sentiment tool. It computes a compound score in [-1, +1] by summing valence scores for recognised words, then applying grammatical rules for negation (e.g., "not good"), intensifiers ("very"), and punctuation emphasis. Threshold: compound ≥ 0.05 = positive; ≤ -0.05 = negative.

### DistilBERT
DistilBERT (Sanh et al., 2019) is a distilled version of BERT — 40% smaller, 60% faster, retaining 97% of BERT's performance on NLP benchmarks. Fine-tuning replaces the classification head with a binary output layer and trains for 3 epochs using AdamW optimiser (lr=2e-5), binary cross-entropy loss. The [CLS] token embedding from the last encoder layer is used as the document representation.

### BERTopic
BERTopic (Grootendorst, 2022) uses sentence embeddings (MiniLM), UMAP for dimensionality reduction, and HDBSCAN for density-based clustering to form topics. Topic representation uses class-based TF-IDF (c-TF-IDF): `W_{t,c} = tf_{t,c} × log(1 + A / tf_t)`, where A is the total number of words across all topics. Maximal Marginal Relevance (MMR) diversifies the keyword representation to avoid redundant terms.

---

## Module 4 — Causal Inference

### Matched-Pair Design
<p align="justify">
Nearest-neighbour matching pairs each treatment store to the most similar control store based on pre-period (H1 2013) mean weekly sales. This creates a balanced comparison group without relying on randomisation. Balance is validated by a Welch t-test on pre-period means: p = 0.871 (strongly non-significant) confirms that matched groups are statistically indistinguishable.
</p>

### Welch t-Test
The Welch (unequal variance) t-test does not assume equal population variances:
```
t = (x̄₁ - x̄₂) / √(s₁²/n₁ + s₂²/n₂)
```
Degrees of freedom estimated by the Welch-Satterthwaite equation. Used for post-period comparison of treatment vs control group means.

### Mann-Whitney U Test
Non-parametric alternative to the t-test. Tests whether the distributions of treatment and control have the same location without assuming normality. Appropriate for skewed sales distributions with outliers.

### Bayesian A/B Test (Beta-Binomial)
Each group's conversion probability is modelled as Beta-distributed:
```
p_treatment ~ Beta(α_T + successes_T, β_T + failures_T)
p_control   ~ Beta(α_C + successes_C, β_C + failures_C)
```
With uninformative prior Beta(1,1). Posterior samples from PyMC. P(treatment > control) estimated as the proportion of MCMC samples where p_treatment > p_control = **95.8%**.

### Difference-in-Differences (DiD)
The DiD estimator controls for unobserved store-level time-invariant confounders via entity demeaning (equivalent to including store fixed effects):
```
y_dm_{it} = δ · post_dm_{it} + τ · (treat × post)_dm_{it} + ε_{it}
```
Where `_dm` denotes store-demeaned variables, δ captures common time trends, and **τ is the causal treatment effect** (DiD estimate). Standard errors are clustered at the store level to account for autocorrelation.

**Result:** τ = +$848/week per store (p = 0.080, cluster-robust SE)
**Interpretation:** The Promo2 loyalty programme caused an estimated +2.5% increase in weekly sales, above and beyond any common time trend or pre-existing store differences.

---

## References

- Chen, T., & Guestrin, C. (2016). XGBoost: A scalable tree boosting system. *KDD 2016*.
- Grootendorst, M. (2022). BERTopic: Neural topic modeling with a class-based TF-IDF procedure. *arXiv:2203.05794*.
- Hughes, A. M. (1994). Strategic Database Marketing. Probus Publishing.
- Hutto, C., & Gilbert, E. (2014). VADER: A parsimonious rule-based model for sentiment analysis of social media text. *ICWSM 2014*.
- Liu, F. T., Ting, K. M., & Zhou, Z. H. (2008). Isolation forest. *ICDM 2008*.
- Mitchell, M., et al. (2019). Model cards for model reporting. *FAccT 2019*.
- Sanh, V., et al. (2019). DistilBERT, a distilled version of BERT. *NeurIPS EMC² Workshop*.
- Taylor, S. J., & Letham, B. (2018). Forecasting at scale. *The American Statistician, 72*(1), 37–45.

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
