"""
PROFITIQ: Data Cleaner Module
Cleans, standardizes, imputes, and calculates financial metrics.
Prevents NaN, Inf, and type errors across all downstream dashboards.
"""

import numpy as np
import pandas as pd
from src.utils import safe_divide

def clean_numeric_series(series):
    """Clean series containing strings with $, %, commas, or spaces into float."""
    if pd.api.types.is_numeric_dtype(series):
        return pd.to_numeric(series.fillna(0.0), errors='coerce').fillna(0.0)
    
    cleaned = (
        series.astype(str)
        .str.replace("$", "", regex=False)
        .str.replace("₹", "", regex=False)
        .str.replace("€", "", regex=False)
        .str.replace("£", "", regex=False)
        .str.replace("%", "", regex=False)
        .str.replace(",", "", regex=False)
        .str.strip()
    )
    return pd.to_numeric(cleaned, errors='coerce').fillna(0.0)

def standardize_and_clean_data(raw_df, mapping):
    """
    Standardize raw DataFrame using detected canonical mapping and compute financial fields.
    Returns:
        pd.DataFrame: Cleaned canonical DataFrame
        dict: Data quality diagnostics summary
    """
    df = raw_df.copy()
    initial_rows = len(df)
    initial_cols = len(df.columns)
    duplicate_count = int(df.duplicated().sum())

    # 1. Rename columns according to mapping
    inv_mapping = {v: k for k, v in mapping.items()}
    df = df.rename(columns=inv_mapping)

    # 2. Ensure Core Canonical Columns Exist
    canonical_columns = [
        "Order ID", "Order Date", "Customer", "Product", "Category", 
        "Region", "Quantity", "Revenue", "Cost", "Discount", "Profit", "Profit Margin %"
    ]

    # Impute missing string categories
    if "Customer" not in df.columns:
        df["Customer"] = "Unknown Customer"
    else:
        df["Customer"] = df["Customer"].fillna("Unknown Customer").astype(str).str.strip()

    if "Product" not in df.columns:
        df["Product"] = "Standard Product"
    else:
        df["Product"] = df["Product"].fillna("Standard Product").astype(str).str.strip()

    if "Category" not in df.columns:
        df["Category"] = "General Category"
    else:
        df["Category"] = df["Category"].fillna("General Category").astype(str).str.strip()

    if "Region" not in df.columns:
        df["Region"] = "Global Market"
    else:
        df["Region"] = df["Region"].fillna("Global Market").astype(str).str.strip()

    if "Order ID" not in df.columns:
        df["Order ID"] = [f"ORD-{i+1000}" for i in range(len(df))]
    else:
        df["Order ID"] = df["Order ID"].fillna("ORD-UNKNOWN").astype(str)

    # Clean / Convert Numerics
    if "Quantity" in df.columns:
        df["Quantity"] = clean_numeric_series(df["Quantity"]).clip(lower=0)
    else:
        df["Quantity"] = 1

    if "Revenue" in df.columns:
        df["Revenue"] = clean_numeric_series(df["Revenue"])
    else:
        df["Revenue"] = 0.0

    if "Cost" in df.columns:
        df["Cost"] = clean_numeric_series(df["Cost"])
    else:
        df["Cost"] = 0.0

    if "Discount" in df.columns:
        df["Discount"] = clean_numeric_series(df["Discount"])
    else:
        df["Discount"] = 0.0

    if "Profit" in df.columns:
        df["Profit"] = clean_numeric_series(df["Profit"])
    else:
        # Compute Profit = Revenue - Cost
        df["Profit"] = df["Revenue"] - df["Cost"]

    # Reconcile if Cost was missing but Revenue & Profit exist
    if "Cost" not in mapping and "Profit" in mapping:
        df["Cost"] = df["Revenue"] - df["Profit"]

    # Reconcile if Revenue was missing but Cost & Profit exist
    if "Revenue" not in mapping and "Cost" in mapping and "Profit" in mapping:
        df["Revenue"] = df["Cost"] + df["Profit"]

    # Calculate Profit Margin % safely
    # Profit Margin = (Profit / Revenue) * 100
    df["Profit Margin %"] = np.where(
        df["Revenue"] != 0,
        (df["Profit"] / df["Revenue"]) * 100,
        0.0
    )
    df["Profit Margin %"] = df["Profit Margin %"].replace([np.inf, -np.inf], 0.0).fillna(0.0).round(2)

    # Calculate Discount Rate %
    if "Discount Rate" in df.columns:
        df["Discount Rate"] = clean_numeric_series(df["Discount Rate"])
        if df["Discount Rate"].max() > 1.0:  # If recorded as e.g. 25% instead of 0.25
            df["Discount Rate"] = df["Discount Rate"] / 100.0
    else:
        gross_estimated = df["Revenue"] + df["Discount"]
        df["Discount Rate"] = np.where(
            gross_estimated > 0,
            df["Discount"] / gross_estimated,
            0.0
        )
    df["Discount Rate"] = df["Discount Rate"].clip(0.0, 1.0).round(4)

    # Parse Order Date
    if "Order Date" in df.columns:
        df["Order Date"] = pd.to_datetime(df["Order Date"], errors='coerce')
        # If dates couldn't be parsed, create a default date series
        if df["Order Date"].isna().all():
            df["Order Date"] = pd.date_range(end=pd.Timestamp.now(), periods=len(df), freq='D')
        else:
            df["Order Date"] = df["Order Date"].ffill().fillna(pd.Timestamp.now())
        df["YearMonth"] = df["Order Date"].dt.strftime('%Y-%m')
        df["Year"] = df["Order Date"].dt.year
        df["MonthName"] = df["Order Date"].dt.strftime('%b %Y')
    else:
        df["Order Date"] = pd.date_range(end=pd.Timestamp.now(), periods=len(df), freq='D')
        df["YearMonth"] = df["Order Date"].dt.strftime('%Y-%m')
        df["Year"] = df["Order Date"].dt.year
        df["MonthName"] = df["Order Date"].dt.strftime('%b %Y')

    # Data Quality Diagnostic Summary
    quality_summary = {
        "initial_rows": initial_rows,
        "initial_cols": initial_cols,
        "cleaned_rows": len(df),
        "duplicates_detected": duplicate_count,
        "null_counts": int(raw_df.isna().sum().sum()),
        "memory_mb": round(df.memory_usage(deep=True).sum() / (1024 * 1024), 2),
        "date_range": (df["Order Date"].min().strftime("%Y-%m-%d"), df["Order Date"].max().strftime("%Y-%m-%d"))
    }

    return df, quality_summary
