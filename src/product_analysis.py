"""
PROFITIQ: Product Intelligence Engine
Analyzes product-level profitability, identifies margin-eroding SKUs,
evaluates category mix, and generates automated product diagnostics.
"""

import numpy as np
import pandas as pd
from src.utils import safe_divide

def get_product_summary_table(df):
    """
    Aggregate transactional data to product level with category and margin metrics.
    """
    if df.empty:
        return pd.DataFrame()

    prod_df = df.groupby(["Product", "Category"]).agg(
        Revenue=("Revenue", "sum"),
        Cost=("Cost", "sum"),
        Discount=("Discount", "sum"),
        Profit=("Profit", "sum"),
        Quantity=("Quantity", "sum") if "Quantity" in df.columns else ("Revenue", "count"),
        Orders=("Order ID", "nunique") if "Order ID" in df.columns else ("Revenue", "count"),
        Avg_Discount_Rate=("Discount Rate", "mean") if "Discount Rate" in df.columns else ("Revenue", lambda x: 0.0)
    ).reset_index()

    prod_df["Profit Margin %"] = np.where(
        prod_df["Revenue"] > 0,
        (prod_df["Profit"] / prod_df["Revenue"]) * 100,
        0.0
    ).round(2)

    prod_df["Avg Unit Price"] = np.where(
        prod_df["Quantity"] > 0,
        prod_df["Revenue"] / prod_df["Quantity"],
        0.0
    ).round(2)

    prod_df["Avg Unit Cost"] = np.where(
        prod_df["Quantity"] > 0,
        prod_df["Cost"] / prod_df["Quantity"],
        0.0
    ).round(2)

    prod_df = prod_df.sort_values("Profit", ascending=False).reset_index(drop=True)
    return prod_df

def get_product_leaderboards(prod_df, top_n=5):
    """
    Extract top profitable, worst loss-making, highest margin, and lowest margin products.
    """
    if prod_df.empty:
        return {}, {}, {}, {}

    top_profitable = prod_df.nlargest(top_n, "Profit")
    worst_loss = prod_df.nsmallest(top_n, "Profit")
    highest_margin = prod_df[prod_df["Revenue"] > 1000].nlargest(top_n, "Profit Margin %")
    lowest_margin = prod_df[prod_df["Revenue"] > 1000].nsmallest(top_n, "Profit Margin %")

    return top_profitable, worst_loss, highest_margin, lowest_margin

def generate_product_observations(prod_df):
    """
    Generate automated diagnostic observations regarding product profitability.
    """
    observations = []
    if prod_df.empty:
        return observations

    loss_products = prod_df[prod_df["Profit"] < 0]
    if not loss_products.empty:
        worst = loss_products.iloc[0]
        observations.append({
            "type": "loss",
            "text": f"Product '{worst['Product']}' in '{worst['Category']}' is generating a net loss of -${abs(worst['Profit']):,.0f} across {worst['Orders']} orders due to COGS exceeding discounted price."
        })

    # High Revenue, Low Margin SKUs
    med_rev = prod_df["Revenue"].median()
    avg_margin = safe_divide(prod_df["Profit"].sum(), prod_df["Revenue"].sum()) * 100
    dilutive = prod_df[(prod_df["Revenue"] >= med_rev) & (prod_df["Profit Margin %"] < 10) & (prod_df["Profit"] > 0)]
    if not dilutive.empty:
        item = dilutive.iloc[0]
        observations.append({
            "type": "margin",
            "text": f"Product '{item['Product']}' drives heavy revenue (${item['Revenue']:,.0f}) but operates at a slim {item['Profit Margin %']:.1f}% margin (vs {avg_margin:.1f}% benchmark). Re-evaluate supplier costs."
        })

    # High Margin Stars
    high_margin_stars = prod_df[(prod_df["Profit Margin %"] > 40) & (prod_df["Profit"] > 0)].sort_values("Profit", ascending=False)
    if not high_margin_stars.empty:
        star = high_margin_stars.iloc[0]
        observations.append({
            "type": "opportunity",
            "text": f"Product '{star['Product']}' demonstrates strong pricing power with {star['Profit Margin %']:.1f}% margin, generating ${star['Profit']:,.0f} profit."
        })

    return observations
