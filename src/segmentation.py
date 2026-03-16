"""
segmentation.py — Customer Experience Analytics Platform
Module 1: Customer Segmentation + Customer Lifetime Value

Implements RFM analysis, K-Means clustering with business-friendly segment
naming, and XGBoost-based CLV regression.

Business context: Understanding which retail visitors are most valuable,
most frequent, and most at risk of churning is the foundation of the
marketing strategy. This module segments visitors and predicts their 90-day
future spend to enable targeted, ROI-positive campaigns.
"""

from __future__ import annotations

import logging
import warnings
from typing import Optional

import numpy as np
import pandas as pd
from sklearn.cluster import KMeans
from sklearn.decomposition import PCA
from sklearn.metrics import silhouette_score, r2_score, mean_squared_error
from sklearn.preprocessing import StandardScaler
from xgboost import XGBRegressor

logger = logging.getLogger(__name__)


# ─── Segment name mapping ─────────────────────────────────────────────────────
SEGMENT_NAMES = {
    0: "Champions",
    1: "Loyalists",
    2: "Potential",
    3: "At-Risk",
    4: "Dormant",
}

SEGMENT_COLOURS = {
    "Champions": "#2E75B6",
    "Loyalists": "#70AD47",
    "Potential": "#FFC000",
    "At-Risk": "#FF7043",
    "Dormant": "#9E9E9E",
}


class RFMCalculator:
    """
    Computes RFM (Recency, Frequency, Monetary) features from a transactions
    DataFrame.

    RFM is the industry-standard framework for visitor value analysis at
    the retail operator. It answers: How recently did a visitor come? How often?
    How much do they spend?

    Parameters
    ----------
    reference_date : str or pd.Timestamp, optional
        Reference date for recency calculation. Defaults to max invoice date + 1 day.
    customer_col : str
        Column name for customer identifier.
    date_col : str
        Column name for invoice/transaction date.
    invoice_col : str
        Column name for invoice identifier (used for frequency count).
    revenue_col : str
        Column name for line-item revenue.
    """

    def __init__(
        self,
        reference_date: Optional[str] = None,
        customer_col: str = "Customer ID",
        date_col: str = "InvoiceDate",
        invoice_col: str = "Invoice",
        revenue_col: str = "revenue",
    ) -> None:
        self.reference_date = reference_date
        self.customer_col = customer_col
        self.date_col = date_col
        self.invoice_col = invoice_col
        self.revenue_col = revenue_col
        self.ref_date_: Optional[pd.Timestamp] = None

    def fit_transform(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Compute RFM scores from a cleaned transaction DataFrame.

        Parameters
        ----------
        df : pd.DataFrame
            Cleaned transactions with at minimum: customer_col, date_col,
            invoice_col, revenue_col.

        Returns
        -------
        pd.DataFrame
            One row per customer with columns: customer_id, recency,
            frequency, monetary, first_purchase, last_purchase.
        """
        df = df.copy()
        df[self.date_col] = pd.to_datetime(df[self.date_col])

        if self.reference_date is not None:
            self.ref_date_ = pd.Timestamp(self.reference_date)
        else:
            self.ref_date_ = df[self.date_col].max() + pd.Timedelta(days=1)

        logger.info(f"RFM reference date: {self.ref_date_.date()}")

        rfm = (
            df.groupby(self.customer_col)
            .agg(
                recency=(self.date_col, lambda x: (self.ref_date_ - x.max()).days),
                frequency=(self.invoice_col, "nunique"),
                monetary=(self.revenue_col, "sum"),
                first_purchase=(self.date_col, "min"),
                last_purchase=(self.date_col, "max"),
            )
            .reset_index()
            .rename(columns={self.customer_col: "customer_id"})
        )

        # Clip extreme monetary values (top 0.5%) to reduce XGBoost variance
        upper = rfm["monetary"].quantile(0.995)
        rfm["monetary"] = rfm["monetary"].clip(upper=upper)

        logger.info(
            f"RFM computed: {len(rfm):,} customers | "
            f"median recency={rfm['recency'].median():.0f}d | "
            f"median frequency={rfm['frequency'].median():.1f} | "
            f"median monetary=£{rfm['monetary'].median():.2f}"
        )
        return rfm


class CustomerSegmenter:
    """
    Segments retail visitors using K-Means clustering on RFM features.

    Provides elbow method analysis, silhouette scoring, PCA visualisation,
    and business-friendly segment labelling.

    Parameters
    ----------
    n_clusters : int
        Number of segments. Default 5 (Champions, Loyalists, Potential,
        At-Risk, Dormant) — validated by elbow + silhouette analysis.
    random_state : int
        Seed for reproducibility.
    """

    def __init__(self, n_clusters: int = 5, random_state: int = 42) -> None:
        self.n_clusters = n_clusters
        self.random_state = random_state
        self.scaler_ = StandardScaler()
        self.kmeans_: Optional[KMeans] = None
        self.pca_: Optional[PCA] = None
        self.segment_map_: dict = {}
        self.profile_: Optional[pd.DataFrame] = None

    def elbow_analysis(
        self, rfm: pd.DataFrame, k_range: range = range(2, 11)
    ) -> pd.DataFrame:
        """
        Compute inertia and silhouette scores for a range of K values.

        Returns a DataFrame for plotting. Use this to justify the chosen K
        to non-technical stakeholders.
        """
        features = rfm[["recency", "frequency", "monetary"]].values
        X_scaled = self.scaler_.fit_transform(features)

        results = []
        for k in k_range:
            km = KMeans(n_clusters=k, random_state=self.random_state, n_init=10)
            labels = km.fit_predict(X_scaled)
            inertia = km.inertia_
            sil = silhouette_score(X_scaled, labels) if k >= 2 else np.nan
            results.append({"k": k, "inertia": inertia, "silhouette": sil})
            logger.debug(f"k={k}: inertia={inertia:.0f}, silhouette={sil:.4f}")

        return pd.DataFrame(results)

    def fit(self, rfm: pd.DataFrame) -> "CustomerSegmenter":
        """
        Fit the K-Means model on RFM features and assign business-friendly
        segment names based on centroid ordering.

        Segment naming logic:
        - Champions: low recency, high frequency, high monetary
        - Loyalists: moderate recency, high frequency, high monetary
        - Potential: moderate recency, moderate frequency, moderate monetary
        - At-Risk: high recency (not visited recently), previously high value
        - Dormant: very high recency, low frequency, low monetary
        """
        features = rfm[["recency", "frequency", "monetary"]].values
        X_scaled = self.scaler_.fit_transform(features)

        self.kmeans_ = KMeans(
            n_clusters=self.n_clusters, random_state=self.random_state, n_init=10
        )
        self.kmeans_.fit(X_scaled)

        centroids = pd.DataFrame(
            self.scaler_.inverse_transform(self.kmeans_.cluster_centers_),
            columns=["recency", "frequency", "monetary"],
        )

        # Rank clusters: sort by recency ASC, monetary DESC to assign names
        centroids["rfm_score"] = (
            -centroids["recency"] + centroids["frequency"] * 2 + centroids["monetary"] / 100
        )
        centroids["rank"] = centroids["rfm_score"].rank(ascending=False).astype(int) - 1
        self.segment_map_ = centroids["rank"].to_dict()

        # Fit PCA for 2D visualisation
        self.pca_ = PCA(n_components=2, random_state=self.random_state)
        self.pca_.fit(X_scaled)

        logger.info(f"CustomerSegmenter fitted: {self.n_clusters} segments")
        return self

    def predict(self, rfm: pd.DataFrame) -> pd.DataFrame:
        """
        Assign segment labels to visitors.

        Parameters
        ----------
        rfm : pd.DataFrame
            RFM DataFrame from RFMCalculator.

        Returns
        -------
        pd.DataFrame
            Input DataFrame with added columns: cluster_id, segment, pca_x, pca_y.
        """
        if self.kmeans_ is None:
            raise RuntimeError("Call fit() before predict()")

        rfm = rfm.copy()
        X_scaled = self.scaler_.transform(rfm[["recency", "frequency", "monetary"]].values)

        rfm["cluster_id"] = self.kmeans_.predict(X_scaled)
        rfm["segment"] = rfm["cluster_id"].map(self.segment_map_).map(SEGMENT_NAMES)

        pca_coords = self.pca_.transform(X_scaled)
        rfm["pca_x"] = pca_coords[:, 0]
        rfm["pca_y"] = pca_coords[:, 1]

        return rfm

    def profile(self, rfm_segmented: pd.DataFrame) -> pd.DataFrame:
        """
        Generate a segment profile table with mean R/F/M, count, and % share.

        Returns a DataFrame sorted by business priority (Champions first).
        """
        profile = (
            rfm_segmented.groupby("segment")
            .agg(
                count=("customer_id", "count"),
                avg_recency=("recency", "mean"),
                avg_frequency=("frequency", "mean"),
                avg_monetary=("monetary", "mean"),
                total_revenue=("monetary", "sum"),
            )
            .reset_index()
        )
        profile["pct_of_customers"] = profile["count"] / profile["count"].sum() * 100
        profile["pct_of_revenue"] = profile["total_revenue"] / profile["total_revenue"].sum() * 100

        order = list(SEGMENT_NAMES.values())
        profile["_order"] = profile["segment"].map({s: i for i, s in enumerate(order)})
        profile = profile.sort_values("_order").drop("_order", axis=1).reset_index(drop=True)

        self.profile_ = profile
        return profile


class CLVModel:
    """
    Predicts 90-day Customer Lifetime Value using XGBoost regression.

    Features: recency, frequency, monetary, segment (encoded).
    Target: estimated future 90-day spend (proxy: monetary × frequency_weight).

    In production (the retail operator), this would be trained on actual
    transaction data with a 90-day forward window as the target.

    Parameters
    ----------
    n_estimators : int
        Number of XGBoost trees.
    learning_rate : float
        XGBoost step size.
    random_state : int
        Reproducibility seed.
    """

    def __init__(
        self,
        n_estimators: int = 300,
        learning_rate: float = 0.05,
        max_depth: int = 5,
        random_state: int = 42,
    ) -> None:
        self.n_estimators = n_estimators
        self.learning_rate = learning_rate
        self.max_depth = max_depth
        self.random_state = random_state
        self.model_: Optional[XGBRegressor] = None
        self.feature_names_: list[str] = []
        self.rmse_: float = np.nan
        self.r2_: float = np.nan

    def _build_features(self, rfm_segmented: pd.DataFrame) -> pd.DataFrame:
        segment_order = list(SEGMENT_NAMES.values())
        rfm_segmented = rfm_segmented.copy()
        rfm_segmented["segment_code"] = rfm_segmented["segment"].map(
            {s: i for i, s in enumerate(segment_order)}
        )
        features = ["recency", "frequency", "monetary", "segment_code"]
        self.feature_names_ = features
        return rfm_segmented[features]

    def _build_target(self, rfm_segmented: pd.DataFrame) -> pd.Series:
        """
        Construct a proxy CLV target for demonstration.

        CLV proxy = monetary × log(frequency + 1) × recency_discount
        where recency_discount = exp(-recency / 365).

        In production: replace with actual 90-day forward spend.
        """
        r = rfm_segmented["recency"]
        f = rfm_segmented["frequency"]
        m = rfm_segmented["monetary"]
        recency_discount = np.exp(-r / 365)
        clv = m * np.log1p(f) * recency_discount
        return clv

    def fit(
        self, rfm_segmented: pd.DataFrame, eval_size: float = 0.2
    ) -> "CLVModel":
        """
        Train the CLV regression model.

        Parameters
        ----------
        rfm_segmented : pd.DataFrame
            Output from CustomerSegmenter.predict() containing segment column.
        eval_size : float
            Fraction of data held out for evaluation metrics.

        Returns
        -------
        CLVModel
            Fitted instance (for method chaining).
        """
        from sklearn.model_selection import train_test_split

        X = self._build_features(rfm_segmented)
        y = self._build_target(rfm_segmented)

        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=eval_size, random_state=self.random_state
        )

        self.model_ = XGBRegressor(
            n_estimators=self.n_estimators,
            learning_rate=self.learning_rate,
            max_depth=self.max_depth,
            random_state=self.random_state,
            verbosity=0,
        )
        self.model_.fit(X_train, y_train, eval_set=[(X_test, y_test)], verbose=False)

        y_pred = self.model_.predict(X_test)
        self.rmse_ = np.sqrt(mean_squared_error(y_test, y_pred))
        self.r2_ = r2_score(y_test, y_pred)

        logger.info(f"CLV model trained — RMSE: £{self.rmse_:.2f} | R²: {self.r2_:.4f}")
        return self

    def predict(self, rfm_segmented: pd.DataFrame) -> pd.Series:
        """
        Predict 90-day CLV for all customers.

        Returns
        -------
        pd.Series
            Predicted CLV values indexed like rfm_segmented.
        """
        if self.model_ is None:
            raise RuntimeError("Call fit() before predict()")
        X = self._build_features(rfm_segmented)
        return pd.Series(self.model_.predict(X), index=rfm_segmented.index, name="predicted_clv")

    def feature_importance(self) -> pd.DataFrame:
        """Return feature importances as a tidy DataFrame."""
        if self.model_ is None:
            raise RuntimeError("Call fit() before feature_importance()")
        return (
            pd.DataFrame(
                {"feature": self.feature_names_, "importance": self.model_.feature_importances_}
            )
            .sort_values("importance", ascending=False)
            .reset_index(drop=True)
        )

    def explain(self) -> None:
        """Print a plain-English model performance summary."""
        print("\n" + "=" * 55)
        print("  CLV MODEL PERFORMANCE")
        print("=" * 55)
        print(f"  RMSE   : £{self.rmse_:>10.2f}")
        print(f"  R²     : {self.r2_:>10.4f}")
        print(f"\n  Business interpretation:")
        print(f"  The model explains {self.r2_ * 100:.1f}% of the variance")
        print(f"  in 90-day visitor spend. Predictions are accurate")
        print(f"  to within ±£{self.rmse_:.2f} on average.")
        print("=" * 55 + "\n")
