"""
PROFITIQ: Market & Category Intelligence Engine
Analyzes geography and product category profitability, identifies regional margin variance,
and detects value-dilutive regional/product combinations.
"""

import numpy as np
import pandas as pd
from src.utils import safe_divide

def get_region_summary_table(df):
    """
    Aggregate transactional data by Region/Market.
    """
    if df.empty:
        return pd.DataFrame()

    reg_df = df.groupby("Region").agg(
        Revenue=("Revenue", "sum"),
        Cost=("Cost", "sum"),
        Discount=("Discount", "sum"),
        Profit=("Profit", "sum"),
        Orders=("Order ID", "nunique") if "Order ID" in df.columns else ("Revenue", "count"),
        Avg_Discount_Rate=("Discount Rate", "mean") if "Discount Rate" in df.columns else ("Revenue", lambda x: 0.0)
    ).reset_index()

    reg_df["Profit Margin %"] = np.where(
        reg_df["Revenue"] > 0,
        (reg_df["Profit"] / reg_df["Revenue"]) * 100,
        0.0
    ).round(2)

    total_rev = reg_df["Revenue"].sum()
    total_prof = reg_df["Profit"].sum()

    reg_df["Revenue Share %"] = (reg_df["Revenue"] / total_rev * 100).round(1) if total_rev > 0 else 0.0
    reg_df["Profit Share %"] = (reg_df["Profit"] / total_prof * 100).round(1) if total_prof > 0 else 0.0
    reg_df["Profit-to-Revenue Ratio"] = (reg_df["Profit Share %"] / reg_df["Revenue Share %"]).round(2) if total_rev > 0 else 1.0

    return reg_df.sort_values("Profit", ascending=False).reset_index(drop=True)

def get_category_summary_table(df):
    """
    Aggregate transactional data by Category.
    """
    if df.empty:
        return pd.DataFrame()

    cat_df = df.groupby("Category").agg(
        Revenue=("Revenue", "sum"),
        Cost=("Cost", "sum"),
        Discount=("Discount", "sum"),
        Profit=("Profit", "sum"),
        Orders=("Order ID", "nunique") if "Order ID" in df.columns else ("Revenue", "count"),
        Avg_Discount_Rate=("Discount Rate", "mean") if "Discount Rate" in df.columns else ("Revenue", lambda x: 0.0)
    ).reset_index()

    cat_df["Profit Margin %"] = np.where(
        cat_df["Revenue"] > 0,
        (cat_df["Profit"] / cat_df["Revenue"]) * 100,
        0.0
    ).round(2)

    total_rev = cat_df["Revenue"].sum()
    total_prof = cat_df["Profit"].sum()

    cat_df["Revenue Share %"] = (cat_df["Revenue"] / total_rev * 100).round(1) if total_rev > 0 else 0.0
    cat_df["Profit Share %"] = (cat_df["Profit"] / total_prof * 100).round(1) if total_prof > 0 else 0.0

    return cat_df.sort_values("Profit", ascending=False).reset_index(drop=True)

def get_market_diagnostics(reg_df, cat_df):
    """
    Identify extreme market benchmarks: top/bottom profit regions, top/bottom margin categories.
    """
    diagnostics = {}
    if not reg_df.empty:
        diagnostics["top_profit_region"] = reg_df.iloc[0]["Region"]
        diagnostics["top_profit_region_val"] = reg_df.iloc[0]["Profit"]
        diagnostics["lowest_profit_region"] = reg_df.iloc[-1]["Region"]
        diagnostics["lowest_profit_region_val"] = reg_df.iloc[-1]["Profit"]
        diagnostics["lowest_margin_region"] = reg_df.sort_values("Profit Margin %").iloc[0]["Region"]
        diagnostics["lowest_margin_region_val"] = reg_df.sort_values("Profit Margin %").iloc[0]["Profit Margin %"]
    
    if not cat_df.empty:
        top_cat = cat_df.sort_values("Profit Margin %", ascending=False).iloc[0]
        low_cat = cat_df.sort_values("Profit Margin %", ascending=True).iloc[0]
        diagnostics["highest_margin_cat"] = top_cat["Category"]
        diagnostics["highest_margin_cat_val"] = top_cat["Profit Margin %"]
        diagnostics["lowest_margin_cat"] = low_cat["Category"]
        diagnostics["lowest_margin_cat_val"] = low_cat["Profit Margin %"]

    return diagnostics

def get_region_category_heatmap(df):
    """
    Generate a 2D Pivot Table of Profit Margin % across Region x Category.
    """
    if df.empty:
        return pd.DataFrame()

    pivot = df.pivot_table(
        index="Region",
        columns="Category",
        values=["Revenue", "Profit"],
        aggfunc="sum"
    ).fillna(0)

    # Compute margin % for each cell
    rev_df = pivot["Revenue"]
    prof_df = pivot["Profit"]
    
    margin_df = (prof_df / rev_df.replace(0, np.nan) * 100).fillna(0.0).round(1)
    return margin_df
