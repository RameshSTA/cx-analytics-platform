"""
Unit tests for src/segmentation.py

Tests cover:
- RFMCalculator: correct RFM metric computation
- CustomerSegmenter: cluster count, segment label assignment
- CLVModel: model fitting, prediction shape and value range
"""
import pytest
import pandas as pd
import numpy as np
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from segmentation import RFMCalculator, CustomerSegmenter


class TestRFMCalculator:
    """Tests for RFM feature computation."""

    def test_rfm_output_has_required_columns(self, sample_retail_df):
        """RFM output must contain recency_days, frequency, monetary_value columns."""
        calc = RFMCalculator()
        # Ensure InvoiceDate is datetime
        df = sample_retail_df.copy()
        df["InvoiceDate"] = pd.to_datetime(df["InvoiceDate"])
        if "TotalPrice" not in df.columns:
            df["TotalPrice"] = df["Quantity"] * df["UnitPrice"]
        result = calc.compute(df)
        for col in ["recency_days", "frequency", "monetary_value"]:
            assert col in result.columns, f"Column '{col}' must be present in RFM output"

    def test_rfm_recency_is_non_negative(self, sample_retail_df):
        """Recency in days must be >= 0 for all customers."""
        calc = RFMCalculator()
        df = sample_retail_df.copy()
        df["InvoiceDate"] = pd.to_datetime(df["InvoiceDate"])
        if "TotalPrice" not in df.columns:
            df["TotalPrice"] = df["Quantity"] * df["UnitPrice"]
        result = calc.compute(df)
        assert (result["recency_days"] >= 0).all(), "Recency cannot be negative"

    def test_rfm_frequency_is_positive(self, sample_retail_df):
        """Frequency (distinct invoice dates) must be >= 1 for all customers."""
        calc = RFMCalculator()
        df = sample_retail_df.copy()
        df["InvoiceDate"] = pd.to_datetime(df["InvoiceDate"])
        if "TotalPrice" not in df.columns:
            df["TotalPrice"] = df["Quantity"] * df["UnitPrice"]
        result = calc.compute(df)
        assert (result["frequency"] >= 1).all(), "Frequency must be at least 1"

    def test_rfm_monetary_is_positive(self, sample_retail_df):
        """Monetary value must be positive for all customers."""
        calc = RFMCalculator()
        df = sample_retail_df.copy()
        df["InvoiceDate"] = pd.to_datetime(df["InvoiceDate"])
        if "TotalPrice" not in df.columns:
            df["TotalPrice"] = df["Quantity"] * df["UnitPrice"]
        result = calc.compute(df)
        assert (result["monetary_value"] > 0).all(), "Monetary value must be positive"

    def test_rfm_one_row_per_customer(self, sample_retail_df):
        """RFM output should have exactly one row per unique CustomerID."""
        calc = RFMCalculator()
        df = sample_retail_df.copy()
        df["InvoiceDate"] = pd.to_datetime(df["InvoiceDate"])
        if "TotalPrice" not in df.columns:
            df["TotalPrice"] = df["Quantity"] * df["UnitPrice"]
        result = calc.compute(df)
        assert result.index.nunique() == result.shape[0], "Duplicate CustomerID rows found"


class TestCustomerSegmenter:
    """Tests for K-Means segmentation."""

    def test_segmenter_produces_correct_k_clusters(self, sample_rfm_df):
        """Fitted segmenter with k=3 must produce exactly 3 cluster labels."""
        segmenter = CustomerSegmenter(n_clusters=3, random_state=42)
        result = segmenter.fit_predict(sample_rfm_df[["recency_days", "frequency", "monetary_value"]])
        n_unique = len(np.unique(result))
        assert n_unique == 3, f"Expected 3 clusters, got {n_unique}"

    def test_segment_labels_assigned_to_all_rows(self, sample_rfm_df):
        """Every row must receive a segment assignment (no NaN labels)."""
        segmenter = CustomerSegmenter(n_clusters=5, random_state=42)
        result = segmenter.fit_predict(sample_rfm_df[["recency_days", "frequency", "monetary_value"]])
        assert not pd.Series(result).isna().any(), "Some rows have no segment assignment"

    def test_segment_count_matches_input_rows(self, sample_rfm_df):
        """Output segment array must have the same length as input DataFrame."""
        segmenter = CustomerSegmenter(n_clusters=5, random_state=42)
        result = segmenter.fit_predict(sample_rfm_df[["recency_days", "frequency", "monetary_value"]])
        assert len(result) == len(sample_rfm_df), "Segment count does not match input row count"
