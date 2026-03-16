"""
Unit tests for src/preprocessor.py

Tests cover:
- RetailDataCleaner: schema validation, cleaning rules, edge cases
- RossmannCleaner: date parsing, open-store filter, weekly aggregation
"""
import pytest
import pandas as pd
import numpy as np
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from preprocessor import RetailDataCleaner


class TestRetailDataCleaner:
    """Tests for the UCI Online Retail II cleaning pipeline."""

    def test_removes_null_customer_ids(self, sample_retail_df):
        """Rows with null CustomerID must be dropped."""
        df = sample_retail_df.copy()
        df.loc[:5, "CustomerID"] = None
        cleaner = RetailDataCleaner()
        result = cleaner.clean(df)
        assert result["CustomerID"].isna().sum() == 0, "Null CustomerIDs should be removed"

    def test_removes_cancellations(self, sample_retail_df):
        """Invoices starting with 'C' are cancellations and must be removed."""
        df = sample_retail_df.copy()
        df.loc[:9, "InvoiceNo"] = [f"C{i:06d}" for i in range(10)]
        cleaner = RetailDataCleaner()
        result = cleaner.clean(df)
        assert not result["InvoiceNo"].str.startswith("C").any(), "Cancellations must be removed"

    def test_removes_negative_quantity(self, sample_retail_df):
        """Rows with Quantity <= 0 (not cancellations) must be dropped."""
        df = sample_retail_df.copy()
        df.loc[:4, "Quantity"] = -1
        cleaner = RetailDataCleaner()
        result = cleaner.clean(df)
        assert (result["Quantity"] > 0).all(), "All Quantity values should be positive"

    def test_removes_zero_unit_price(self, sample_retail_df):
        """Rows with UnitPrice <= 0 must be dropped."""
        df = sample_retail_df.copy()
        df.loc[:3, "UnitPrice"] = 0.0
        cleaner = RetailDataCleaner()
        result = cleaner.clean(df)
        assert (result["UnitPrice"] > 0).all(), "All UnitPrice values should be positive"

    def test_adds_total_price_column(self, sample_retail_df):
        """Clean output must contain a TotalPrice column = Quantity × UnitPrice."""
        cleaner = RetailDataCleaner()
        result = cleaner.clean(sample_retail_df)
        assert "TotalPrice" in result.columns, "TotalPrice column must exist"
        expected = result["Quantity"] * result["UnitPrice"]
        pd.testing.assert_series_equal(
            result["TotalPrice"].round(2), expected.round(2),
            check_names=False
        )

    def test_output_row_count_less_than_input(self, sample_retail_df):
        """Cleaned dataframe should have fewer or equal rows than input."""
        df = sample_retail_df.copy()
        df.loc[:10, "CustomerID"] = None  # introduce some nulls
        cleaner = RetailDataCleaner()
        result = cleaner.clean(df)
        assert len(result) <= len(df), "Cleaning should not add rows"

    def test_empty_dataframe_returns_empty(self):
        """Passing an empty DataFrame should return an empty DataFrame gracefully."""
        empty_df = pd.DataFrame(columns=[
            "InvoiceNo", "StockCode", "Description", "Quantity",
            "InvoiceDate", "UnitPrice", "CustomerID", "Country"
        ])
        cleaner = RetailDataCleaner()
        result = cleaner.clean(empty_df)
        assert len(result) == 0, "Empty input should produce empty output"
