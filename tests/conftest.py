"""
Shared fixtures for Customer Experience Analytics Platform test suite.
"""
import sys
import os
import pytest
import pandas as pd
import numpy as np

# Ensure src/ is on the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))


@pytest.fixture
def sample_retail_df():
    """Minimal synthetic retail transactions for unit testing."""
    np.random.seed(42)
    n = 200
    customers = [f"C{i:04d}" for i in range(1, 21)]
    dates = pd.date_range("2021-01-01", "2021-12-31", periods=n)
    return pd.DataFrame({
        "InvoiceNo": [f"INV{i:06d}" for i in range(n)],
        "StockCode": np.random.choice(["PROD01", "PROD02", "PROD03", "PROD04"], n),
        "Description": np.random.choice(["Widget A", "Widget B", "Widget C"], n),
        "Quantity": np.random.randint(1, 20, n),
        "InvoiceDate": dates,
        "UnitPrice": np.random.uniform(2.0, 50.0, n).round(2),
        "CustomerID": np.random.choice(customers, n),
        "Country": "United Kingdom",
    })


@pytest.fixture
def sample_rossmann_df():
    """Minimal synthetic Rossmann-style store sales data."""
    np.random.seed(42)
    stores = list(range(1, 11))
    dates = pd.date_range("2013-01-01", "2013-12-31", freq="D")
    rows = []
    for store in stores:
        for date in dates:
            rows.append({
                "Store": store,
                "Date": date,
                "Sales": int(np.random.normal(15000, 3000)),
                "Customers": int(np.random.normal(600, 100)),
                "Open": 1,
                "Promo": int(date.week % 2),
                "StateHoliday": "0",
                "SchoolHoliday": 0,
                "DayOfWeek": date.dayofweek + 1,
            })
    return pd.DataFrame(rows)


@pytest.fixture
def sample_rfm_df():
    """Pre-computed RFM scores for testing segmentation logic."""
    np.random.seed(42)
    n = 100
    return pd.DataFrame({
        "CustomerID": [f"C{i:04d}" for i in range(n)],
        "recency_days": np.random.randint(1, 365, n),
        "frequency": np.random.randint(1, 50, n),
        "monetary_value": np.random.uniform(50, 5000, n).round(2),
        "recency_rank": np.random.randint(1, 6, n),
        "frequency_rank": np.random.randint(1, 6, n),
        "monetary_rank": np.random.randint(1, 6, n),
    })
