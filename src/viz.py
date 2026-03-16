"""
viz.py — Customer Experience Analytics Platform
Brand-styled chart styling and reusable visualisation functions.

Applies a consistent visual identity across all notebooks:
- Primary blue: #2E75B6 (the retail operator/the retail operator brand)
- Secondary colours: professional, accessible palette
- Typography: clean, stakeholder-presentable
- Every chart has a title + subtitle stating the key insight
"""

from __future__ import annotations

from typing import Optional, Union

import matplotlib.pyplot as plt
import matplotlib as mpl
import numpy as np
import pandas as pd
import seaborn as sns

# ─── Brand Colour Palette ──────────────────────────────────────────────────
BRAND_BLUE = "#2E75B6"
BRAND_DARK_BLUE = "#1A4D8F"
BRAND_LIGHT_BLUE = "#D5E8F0"
BRAND_GREEN = "#70AD47"
BRAND_AMBER = "#FFC000"
BRAND_RED = "#FF7043"
BRAND_GREY = "#9E9E9E"
BRAND_DARK = "#212121"
BRAND_LIGHT_GREY = "#F5F5F5"

SEGMENT_PALETTE = {
    "Champions": BRAND_BLUE,
    "Loyalists": BRAND_GREEN,
    "Potential": BRAND_AMBER,
    "At-Risk": BRAND_RED,
    "Dormant": BRAND_GREY,
}

BRAND_PALETTE = [BRAND_BLUE, BRAND_GREEN, BRAND_AMBER, BRAND_RED, BRAND_GREY, BRAND_DARK_BLUE]


def set_brand_style() -> None:
    """
    Apply brand styling to all matplotlib/seaborn figures.
    Call once at the start of each notebook.
    """
    mpl.rcParams.update({
        "figure.facecolor": "white",
        "axes.facecolor": "white",
        "axes.edgecolor": "#E0E0E0",
        "axes.grid": True,
        "axes.grid.axis": "y",
        "grid.color": "#F0F0F0",
        "grid.linewidth": 0.8,
        "axes.spines.top": False,
        "axes.spines.right": False,
        "axes.spines.left": False,
        "axes.labelcolor": BRAND_DARK,
        "axes.labelsize": 11,
        "axes.titlesize": 13,
        "axes.titleweight": "bold",
        "xtick.color": "#757575",
        "ytick.color": "#757575",
        "xtick.labelsize": 10,
        "ytick.labelsize": 10,
        "legend.frameon": True,
        "legend.framealpha": 0.9,
        "legend.edgecolor": "#E0E0E0",
        "legend.fontsize": 10,
        "font.family": "sans-serif",
        "font.sans-serif": ["Arial", "Helvetica", "DejaVu Sans"],
        "figure.dpi": 120,
        "savefig.dpi": 150,
        "savefig.bbox": "tight",
    })
    sns.set_palette(BRAND_PALETTE)


def add_subtitle(ax: plt.Axes, subtitle: str, fontsize: int = 9) -> None:
    """Add a grey subtitle below the chart title."""
    ax.set_title(
        ax.get_title() + f"\n{subtitle}",
        fontsize=fontsize,
        color="#757575",
        fontweight="normal",
        pad=10,
    )


def format_title(ax: plt.Axes, title: str, subtitle: str = "") -> None:
    """Set a bold title + optional subtitle on an Axes."""
    ax.set_title(title, fontsize=13, fontweight="bold", color=BRAND_DARK, pad=8)
    if subtitle:
        # Add subtitle as secondary text below
        ax.text(
            0.0, 1.02, subtitle,
            transform=ax.transAxes,
            fontsize=9, color="#757575",
            va="bottom", ha="left"
        )


def plot_segment_distribution(
    rfm_segmented: pd.DataFrame,
    save_path: Optional[str] = None,
    figsize: tuple = (12, 5),
) -> tuple:
    """
    Bar chart of visitor counts per segment with revenue breakdown.
    """
    fig, axes = plt.subplots(1, 2, figsize=figsize)

    # Count chart
    segment_counts = rfm_segmented["segment"].value_counts()
    order = ["Champions", "Loyalists", "Potential", "At-Risk", "Dormant"]
    counts = [segment_counts.get(s, 0) for s in order]
    colours = [SEGMENT_PALETTE[s] for s in order]

    axes[0].bar(order, counts, color=colours, edgecolor="white", linewidth=0.5)
    axes[0].set_title("Visitor Count by Segment", fontweight="bold")
    axes[0].set_ylabel("Number of Retail Visitors")
    axes[0].set_xlabel("")
    for i, (seg, count) in enumerate(zip(order, counts)):
        axes[0].text(i, count + max(counts) * 0.01, f"{count:,}", ha="center", fontsize=9, color=BRAND_DARK)

    # Revenue share pie
    rev_by_seg = rfm_segmented.groupby("segment")["monetary"].sum()
    rev_values = [rev_by_seg.get(s, 0) for s in order]
    wedges, texts, autotexts = axes[1].pie(
        rev_values,
        labels=order,
        colors=colours,
        autopct="%1.1f%%",
        pctdistance=0.75,
        startangle=140,
    )
    for at in autotexts:
        at.set_fontsize(9)
    axes[1].set_title("Revenue Share by Segment", fontweight="bold")

    fig.suptitle(
        "Retail Visitor Segmentation Overview",
        fontsize=14, fontweight="bold", y=1.02
    )
    plt.tight_layout()

    if save_path:
        plt.savefig(save_path)
    return fig, axes


def plot_rfm_scatter(
    rfm_segmented: pd.DataFrame,
    save_path: Optional[str] = None,
    figsize: tuple = (10, 7),
) -> tuple:
    """
    2D PCA scatter plot of visitor segments.
    """
    fig, ax = plt.subplots(figsize=figsize)

    for segment in rfm_segmented["segment"].unique():
        mask = rfm_segmented["segment"] == segment
        ax.scatter(
            rfm_segmented.loc[mask, "pca_x"],
            rfm_segmented.loc[mask, "pca_y"],
            c=SEGMENT_PALETTE.get(segment, BRAND_GREY),
            label=segment,
            alpha=0.5,
            s=15,
            edgecolors="none",
        )

    ax.set_title("Visitor Segment Clusters (PCA Reduced)", fontweight="bold")
    ax.set_xlabel("Principal Component 1")
    ax.set_ylabel("Principal Component 2")
    ax.legend(title="Segment", framealpha=0.9)

    plt.tight_layout()
    if save_path:
        plt.savefig(save_path)
    return fig, ax


def plot_elbow(elbow_df: pd.DataFrame, save_path: Optional[str] = None) -> tuple:
    """
    Elbow method + silhouette score dual-axis plot.
    """
    fig, ax1 = plt.subplots(figsize=(9, 5))
    ax2 = ax1.twinx()

    ax1.plot(elbow_df["k"], elbow_df["inertia"], "o-", color=BRAND_BLUE, linewidth=2, markersize=6, label="Inertia")
    ax2.plot(elbow_df["k"], elbow_df["silhouette"], "s--", color=BRAND_RED, linewidth=2, markersize=6, label="Silhouette")

    ax1.set_xlabel("Number of Clusters (K)")
    ax1.set_ylabel("Inertia (Within-cluster variance)", color=BRAND_BLUE)
    ax2.set_ylabel("Silhouette Score", color=BRAND_RED)
    ax1.set_title("K-Means Cluster Selection: Elbow + Silhouette Analysis", fontweight="bold")

    lines1, labels1 = ax1.get_legend_handles_labels()
    lines2, labels2 = ax2.get_legend_handles_labels()
    ax1.legend(lines1 + lines2, labels1 + labels2, loc="center right")

    plt.tight_layout()
    if save_path:
        plt.savefig(save_path)
    return fig, (ax1, ax2)


def plot_forecast(
    actual: pd.DataFrame,
    forecast: pd.DataFrame,
    store_id: int,
    save_path: Optional[str] = None,
    figsize: tuple = (13, 5),
) -> tuple:
    """
    Time series chart: historical traffic + 4-week ahead forecast with
    80% prediction interval. Retail Operations-ready format.
    """
    fig, ax = plt.subplots(figsize=figsize)

    ax.plot(actual["week_start"], actual["weekly_sales"], color=BRAND_BLUE, linewidth=1.5, label="Actual Visitation")
    ax.plot(forecast["ds"], forecast["yhat"], color=BRAND_RED, linewidth=2, linestyle="--", label="Forecast")

    if "yhat_lower" in forecast.columns and "yhat_upper" in forecast.columns:
        ax.fill_between(
            forecast["ds"],
            forecast["yhat_lower"],
            forecast["yhat_upper"],
            alpha=0.2, color=BRAND_RED, label="80% Prediction Interval"
        )

    ax.axvline(actual["week_start"].max(), color="#BDBDBD", linewidth=1, linestyle=":")
    ax.text(actual["week_start"].max(), ax.get_ylim()[1] * 0.95, " Forecast →", color="#757575", fontsize=9)

    ax.set_title(f"Retail Destination {store_id:03d} — Weekly Visitation Forecast", fontweight="bold")
    ax.set_xlabel("Week")
    ax.set_ylabel("Weekly Visitation Index")
    ax.legend()

    plt.tight_layout()
    if save_path:
        plt.savefig(save_path)
    return fig, ax


def plot_sentiment_trend(
    reviews_df: pd.DataFrame,
    date_col: str = "date",
    sentiment_col: str = "bert_label",
    save_path: Optional[str] = None,
    figsize: tuple = (13, 5),
) -> tuple:
    """
    Monthly positive sentiment rate over time with COVID and Christmas overlays.
    """
    df = reviews_df.copy()
    df[date_col] = pd.to_datetime(df[date_col])
    df["month"] = df[date_col].dt.to_period("M")

    monthly = (
        df.groupby("month")
        .apply(lambda x: (x[sentiment_col] == "POSITIVE").mean())
        .reset_index()
        .rename(columns={0: "positive_rate"})
    )
    monthly["month_dt"] = monthly["month"].dt.to_timestamp()

    fig, ax = plt.subplots(figsize=figsize)
    ax.plot(monthly["month_dt"], monthly["positive_rate"], color=BRAND_BLUE, linewidth=2)
    ax.fill_between(monthly["month_dt"], monthly["positive_rate"], alpha=0.1, color=BRAND_BLUE)

    ax.axhline(monthly["positive_rate"].mean(), color=BRAND_GREY, linewidth=1, linestyle="--", label="Average")
    ax.set_ylim(0, 1)
    ax.yaxis.set_major_formatter(mpl.ticker.PercentFormatter(1.0))

    ax.set_title("the retail operator Customer Sentiment Over Time", fontweight="bold")
    ax.set_xlabel("Month")
    ax.set_ylabel("Positive Sentiment Rate")
    ax.legend()

    plt.tight_layout()
    if save_path:
        plt.savefig(save_path)
    return fig, ax


def plot_clv_by_segment(
    rfm_with_clv: pd.DataFrame,
    save_path: Optional[str] = None,
    figsize: tuple = (10, 5),
) -> tuple:
    """
    Horizontal bar chart of mean 90-day CLV per segment.
    """
    order = ["Champions", "Loyalists", "Potential", "At-Risk", "Dormant"]
    mean_clv = rfm_with_clv.groupby("segment")["predicted_clv"].mean().reindex(order)

    fig, ax = plt.subplots(figsize=figsize)
    colours = [SEGMENT_PALETTE[s] for s in order]
    bars = ax.barh(order, mean_clv.values, color=colours, edgecolor="white")

    for bar, val in zip(bars, mean_clv.values):
        ax.text(val + 0.5, bar.get_y() + bar.get_height() / 2, f"£{val:.0f}", va="center", fontsize=10)

    ax.set_xlabel("Mean Predicted 90-day CLV (£)")
    ax.set_title("Predicted 90-Day Customer Lifetime Value by Segment", fontweight="bold")
    ax.invert_yaxis()

    plt.tight_layout()
    if save_path:
        plt.savefig(save_path)
    return fig, ax
