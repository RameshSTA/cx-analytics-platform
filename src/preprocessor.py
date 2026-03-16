"""
preprocessor.py — Customer Experience Analytics Platform
Reusable data cleaning and preprocessing utilities.

All transformations are documented with the business reason behind each decision.
"""

from __future__ import annotations

import logging
import re
from pathlib import Path
from typing import Optional

import numpy as np
import pandas as pd

logger = logging.getLogger(__name__)


class RetailDataCleaner:
    """
    Cleans and validates the UCI Online Retail II dataset for use in
    customer segmentation and CLV modelling.

    Business context: Raw transaction data from retail partners
    contains cancellations, data entry errors, and anonymous sessions that
    would distort customer value calculations. This class applies a principled
    cleaning pipeline before any analysis.

    Parameters
    ----------
    min_quantity : int
        Minimum acceptable quantity per line item. Negatives are cancellations.
    min_price : float
        Minimum acceptable unit price. Zero-price records are typically
        internal transfers or test transactions, not real sales.
    remove_cancellations : bool
        Whether to drop invoices starting with 'C' (cancellation flag).
    verbose : bool
        Whether to log a cleaning report after transformation.
    """

    def __init__(
        self,
        min_quantity: int = 1,
        min_price: float = 0.01,
        remove_cancellations: bool = True,
        verbose: bool = True,
    ) -> None:
        self.min_quantity = min_quantity
        self.min_price = min_price
        self.remove_cancellations = remove_cancellations
        self.verbose = verbose
        self._cleaning_log: list[dict] = []

    def fit_transform(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Apply the full cleaning pipeline.

        Parameters
        ----------
        df : pd.DataFrame
            Raw UCI Online Retail II data as loaded from Excel.

        Returns
        -------
        pd.DataFrame
            Cleaned transaction DataFrame with an added 'revenue' column.
        """
        original_rows = len(df)
        original_customers = df["Customer ID"].nunique()
        df = df.copy()

        # Step 1: Drop rows with no Customer ID.
        # Business reason: We cannot assign RFM scores to anonymous sessions.
        before = len(df)
        df = df.dropna(subset=["Customer ID"])
        self._log("Drop null Customer ID", before, len(df), "Cannot segment anonymous visitors")

        # Step 2: Remove cancellation invoices (prefix 'C').
        # Business reason: Cancellations inflate recency and depress monetary
        # values, making churned customers appear more recent than they are.
        if self.remove_cancellations:
            before = len(df)
            df = df[~df["Invoice"].astype(str).str.startswith("C")]
            self._log("Remove cancellations", before, len(df), "Cancellations distort RFM monetary")

        # Step 3: Remove non-positive quantities.
        # Business reason: Returns and adjustments are not genuine purchase events.
        before = len(df)
        df = df[df["Quantity"] >= self.min_quantity]
        self._log("Remove non-positive Quantity", before, len(df), "Returns are not centre visits")

        # Step 4: Remove zero/negative prices.
        # Business reason: Free samples and internal SKUs are not customer revenue.
        before = len(df)
        df = df[df["Price"] >= self.min_price]
        self._log("Remove zero/negative Price", before, len(df), "Internal SKUs excluded from revenue")

        # Step 5: Remove rows with null Description (bad data).
        before = len(df)
        df = df.dropna(subset=["Description"])
        self._log("Drop null Description", before, len(df), "Unidentifiable items excluded")

        # Step 6: Ensure InvoiceDate is datetime.
        df["InvoiceDate"] = pd.to_datetime(df["InvoiceDate"])

        # Step 7: Compute revenue per line item.
        df["revenue"] = df["Quantity"] * df["Price"]

        # Step 8: Cast Customer ID to integer for clean joins.
        df["Customer ID"] = df["Customer ID"].astype(int)

        if self.verbose:
            self._print_cleaning_report(original_rows, original_customers, df)

        return df

    def _log(self, step: str, before: int, after: int, reason: str) -> None:
        removed = before - after
        pct = removed / before * 100 if before > 0 else 0
        self._cleaning_log.append(
            {"step": step, "removed": removed, "pct_removed": round(pct, 2), "reason": reason}
        )

    def _print_cleaning_report(
        self, original_rows: int, original_customers: int, df: pd.DataFrame
    ) -> None:
        print("\n" + "=" * 65)
        print("  CX ANALYTICS PLATFORM — DATA CLEANING REPORT")
        print("=" * 65)
        print(f"  Original rows     : {original_rows:>10,}")
        print(f"  Final rows        : {len(df):>10,}")
        print(f"  Rows removed      : {original_rows - len(df):>10,}  ({(original_rows - len(df)) / original_rows * 100:.1f}%)")
        print(f"  Final customers   : {df['Customer ID'].nunique():>10,}")
        print(f"  Date range        : {df['InvoiceDate'].min().date()} → {df['InvoiceDate'].max().date()}")
        print(f"  Total revenue     : £{df['revenue'].sum():>12,.2f}")
        print("-" * 65)
        print(f"  {'Step':<35} {'Removed':>8} {'%':>6}")
        print("-" * 65)
        for entry in self._cleaning_log:
            print(f"  {entry['step']:<35} {entry['removed']:>8,} {entry['pct_removed']:>5.1f}%")
        print("=" * 65 + "\n")

    def get_cleaning_log(self) -> pd.DataFrame:
        """Return the cleaning log as a DataFrame for reporting."""
        return pd.DataFrame(self._cleaning_log)


class RossmannCleaner:
    """
    Cleans and merges Rossmann Store Sales data for foot traffic forecasting
    and A/B testing modules.

    Business context: The Rossmann dataset is used as a proxy for the retail operator
    destination-level foot traffic. Stores = destinations, Sales = visitation
    index. Closed days must be excluded from training to avoid misleading the
    forecasting model with structural zeroes.

    Parameters
    ----------
    open_only : bool
        If True, drop all rows where Open == 0 (closed days).
    fill_competition : bool
        If True, fill missing competition distance with dataset max (far away).
    """

    def __init__(self, open_only: bool = True, fill_competition: bool = True) -> None:
        self.open_only = open_only
        self.fill_competition = fill_competition

    def fit_transform(
        self, train_df: pd.DataFrame, store_df: pd.DataFrame
    ) -> pd.DataFrame:
        """
        Merge train and store files, apply cleaning, return analysis-ready DataFrame.

        Parameters
        ----------
        train_df : pd.DataFrame
            Loaded rossmann_train.csv
        store_df : pd.DataFrame
            Loaded rossmann_store.csv

        Returns
        -------
        pd.DataFrame
            Merged and cleaned DataFrame.
        """
        df = train_df.merge(store_df, on="Store", how="left")
        df["Date"] = pd.to_datetime(df["Date"])

        if self.open_only:
            before = len(df)
            df = df[df["Open"] == 1]
            logger.info(f"Removed {before - len(df):,} closed-day rows")

        if self.fill_competition:
            max_dist = df["CompetitionDistance"].max()
            df["CompetitionDistance"] = df["CompetitionDistance"].fillna(max_dist)

        # Fill ordinal store attributes
        df["CompetitionOpenSinceMonth"] = df["CompetitionOpenSinceMonth"].fillna(0)
        df["CompetitionOpenSinceYear"] = df["CompetitionOpenSinceYear"].fillna(0)
        df["Promo2SinceWeek"] = df["Promo2SinceWeek"].fillna(0)
        df["Promo2SinceYear"] = df["Promo2SinceYear"].fillna(0)

        # Encode categoricals
        df["StoreType"] = df["StoreType"].map({"a": 0, "b": 1, "c": 2, "d": 3})
        df["Assortment"] = df["Assortment"].map({"a": 0, "b": 1, "c": 2})

        logger.info(
            f"Cleaned Rossmann data: {len(df):,} rows, "
            f"{df['Store'].nunique()} stores, "
            f"{df['Date'].min().date()} → {df['Date'].max().date()}"
        )
        return df

    def aggregate_weekly(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Aggregate daily sales to weekly per store.

        Returns a DataFrame with columns: Store, year_week, week_start,
        weekly_sales, weekly_customers, promo_flag.
        """
        df = df.copy()
        df["year_week"] = df["Date"].dt.isocalendar().year.astype(str) + "-W" + \
                          df["Date"].dt.isocalendar().week.astype(str).str.zfill(2)
        df["week_start"] = df["Date"] - pd.to_timedelta(df["Date"].dt.dayofweek, unit="d")

        weekly = (
            df.groupby(["Store", "year_week", "week_start"])
            .agg(
                weekly_sales=("Sales", "sum"),
                weekly_customers=("Customers", "sum"),
                promo_flag=("Promo", "max"),
                school_holiday=("SchoolHoliday", "max"),
                state_holiday=("StateHoliday", lambda x: (x != "0").any().astype(int)),
                store_type=("StoreType", "first"),
                assortment=("Assortment", "first"),
            )
            .reset_index()
            .sort_values(["Store", "week_start"])
        )
        return weekly
