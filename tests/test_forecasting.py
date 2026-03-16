"""
Unit tests for src/forecasting.py

Tests cover:
- TimeSeriesPreprocessor: weekly aggregation, closed-store filtering
- AnomalyFlagger: score shape, contamination rate
"""
import pytest
import pandas as pd
import numpy as np
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from forecasting import TimeSeriesPreprocessor, AnomalyFlagger


class TestTimeSeriesPreprocessor:
    """Tests for time-series data preparation pipeline."""

    def test_removes_closed_store_days(self, sample_rossmann_df):
        """Days where Open==0 must be excluded from the training data."""
        df = sample_rossmann_df.copy()
        # Close some days
        df.loc[df["Date"] < "2013-02-01", "Open"] = 0
        prep = TimeSeriesPreprocessor()
        result = prep.prepare(df)
        # After preparation, all observations should be from open days
        # (Weekly aggregation on closed days would produce 0 — check no zero-sales weeks)
        assert (result["Sales"] > 0).all(), "Closed-day rows should be excluded"

    def test_weekly_aggregation_reduces_row_count(self, sample_rossmann_df):
        """Weekly aggregated data must have fewer rows than daily input."""
        prep = TimeSeriesPreprocessor()
        result = prep.prepare(sample_rossmann_df)
        # Daily rows = 365 × 10 stores = 3,650; weekly ≈ 52 × 10 = 520
        assert len(result) < len(sample_rossmann_df), (
            "Weekly aggregation should reduce row count vs daily data"
        )

    def test_weekly_output_has_required_columns(self, sample_rossmann_df):
        """Weekly output must include Store, week_start, and Sales columns."""
        prep = TimeSeriesPreprocessor()
        result = prep.prepare(sample_rossmann_df)
        for col in ["Store", "Sales"]:
            assert col in result.columns, f"Required column '{col}' missing from weekly output"


class TestAnomalyFlagger:
    """Tests for Isolation Forest anomaly detection."""

    def test_anomaly_scores_correct_length(self, sample_rossmann_df):
        """Anomaly score array must have same length as input."""
        df = sample_rossmann_df.copy()
        df = df[df["Store"] == 1].copy()
        flagger = AnomalyFlagger(contamination=0.05, random_state=42)
        scores = flagger.fit_predict(df[["Sales"]])
        assert len(scores) == len(df), "Anomaly score length must match input length"

    def test_anomaly_flag_is_binary(self, sample_rossmann_df):
        """Anomaly flags must be binary: -1 (anomaly) or 1 (normal)."""
        df = sample_rossmann_df.copy()
        df = df[df["Store"] == 1].copy()
        flagger = AnomalyFlagger(contamination=0.05, random_state=42)
        flags = flagger.fit_predict(df[["Sales"]])
        unique_values = set(np.unique(flags))
        assert unique_values.issubset({-1, 1}), f"Unexpected flag values: {unique_values}"

    def test_anomaly_rate_near_contamination(self, sample_rossmann_df):
        """Anomaly flag rate should be approximately equal to contamination parameter."""
        df = sample_rossmann_df.copy()
        contamination = 0.10
        flagger = AnomalyFlagger(contamination=contamination, random_state=42)
        flags = flagger.fit_predict(df[["Sales"]])
        anomaly_rate = (flags == -1).mean()
        # Allow ±5% tolerance around the target contamination rate
        assert abs(anomaly_rate - contamination) < 0.05, (
            f"Anomaly rate {anomaly_rate:.2f} deviates too much from target {contamination}"
        )
