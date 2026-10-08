"""
PROFITIQ: Discount Intelligence & Margin Erosion Engine
Analyzes discount-driven margin decay, segments discount tiers,
and identifies customers and products leaking profitability through uncontrolled discounting.
"""

import numpy as np
import pandas as pd
from src.utils import safe_divide

def get_discount_metrics(df):
    """
    Calculate high-level discount leakage metrics and estimated profit impact.
    """
    if df.empty:
        return {
            "total_discount": 0.0, "avg_discount_rate": 0.0,
            "discount_to_revenue_pct": 0.0, "eroded_profit_estimate": 0.0,
            "loss_making_discount_orders": 0, "loss_making_discount_val": 0.0
        }

    total_discount = float(df["Discount"].sum())
    total_rev = float(df["Revenue"].sum())
    gross_sales = total_rev + total_discount
    
    avg_discount_rate = float(df["Discount Rate"].mean() * 100) if "Discount Rate" in df.columns else 0.0
    discount_to_revenue_pct = safe_divide(total_discount, total_rev) * 100
    
    # Identify loss orders associated with discounting
    disc_orders = df[df["Discount"] > 0]
    loss_orders = disc_orders[disc_orders["Profit"] < 0]
    
    loss_count = len(loss_orders)
    loss_val = abs(float(loss_orders["Profit"].sum()))

    # Calculate correlation between discount rate and profit margin
    if len(df) > 5 and "Discount Rate" in df.columns and "Profit Margin %" in df.columns:
        corr = df["Discount Rate"].corr(df["Profit Margin %"])
    else:
        corr = 0.0

    return {
        "total_discount": total_discount,
        "avg_discount_rate": avg_discount_rate,
        "discount_to_revenue_pct": discount_to_revenue_pct,
        "eroded_profit_estimate": total_discount * 0.75, # Estimated profit recovery if 75% of discounts were rationalized
        "loss_making_discount_orders": loss_count,
        "loss_making_discount_val": loss_val,
        "correlation": corr
    }

def get_discount_tier_analysis(df):
    """
    Group transactions into standardized discount brackets to evaluate margin decay per tier.
    """
    if df.empty or "Discount Rate" not in df.columns:
        return pd.DataFrame()

    def get_tier(rate):
        if rate <= 0.05:
            return "1. Low (0% - 5%)"
        elif rate <= 0.15:
            return "2. Moderate (5% - 15%)"
        elif rate <= 0.25:
            return "3. High (15% - 25%)"
        else:
            return "4. Deep Discount (> 25%)"

    temp = df.copy()
    temp["Discount Tier"] = temp["Discount Rate"].apply(get_tier)

    tier_df = temp.groupby("Discount Tier").agg(
        Orders=("Revenue", "count"),
        Total_Revenue=("Revenue", "sum"),
        Total_Cost=("Cost", "sum"),
        Total_Discount=("Discount", "sum"),
        Total_Profit=("Profit", "sum"),
        Avg_Margin=("Profit Margin %", "mean")
    ).reset_index()

    tier_df["Realized Margin %"] = np.where(
        tier_df["Total_Revenue"] > 0,
        (tier_df["Total_Profit"] / tier_df["Total_Revenue"]) * 100,
        0.0
    ).round(2)

    tier_df["Revenue Share %"] = (tier_df["Total_Revenue"] / tier_df["Total_Revenue"].sum() * 100).round(1)
    tier_df = tier_df.sort_values("Discount Tier").reset_index(drop=True)
    return tier_df

def get_margin_erosion_alerts(df):
    """
    Detect accounts and products with above-average discounts and below-average margins.
    """
    alerts = []
    if df.empty:
        return alerts

    avg_disc = df["Discount Rate"].mean() if "Discount Rate" in df.columns else 0.0
    overall_margin = safe_divide(df["Profit"].sum(), df["Revenue"].sum()) * 100

    # Customer erosion
    cust_agg = df.groupby("Customer").agg(
        Revenue=("Revenue", "sum"),
        Profit=("Profit", "sum"),
        Avg_Discount=("Discount Rate", "mean") if "Discount Rate" in df.columns else ("Revenue", lambda x: 0.0)
    ).reset_index()
    cust_agg["Margin %"] = (cust_agg["Profit"] / cust_agg["Revenue"] * 100).round(2)

    eroding_custs = cust_agg[
        (cust_agg["Avg_Discount"] > avg_disc * 1.2) & 
        (cust_agg["Margin %"] < overall_margin * 0.6)
    ].sort_values("Revenue", ascending=False)

    for _, row in eroding_custs.head(4).iterrows():
        alerts.append({
            "target": row["Customer"],
            "type": "Customer",
            "revenue": row["Revenue"],
            "discount_rate": row["Avg_Discount"] * 100,
            "margin": row["Margin %"],
            "explanation": f"Receives an average discount of {row['Avg_Discount']*100:.1f}% (above average) while delivering only {row['Margin %']:.1f}% profit margin."
        })

    # Product erosion
    prod_agg = df.groupby("Product").agg(
        Revenue=("Revenue", "sum"),
        Profit=("Profit", "sum"),
        Avg_Discount=("Discount Rate", "mean") if "Discount Rate" in df.columns else ("Revenue", lambda x: 0.0)
    ).reset_index()
    prod_agg["Margin %"] = (prod_agg["Profit"] / prod_agg["Revenue"] * 100).round(2)

    eroding_prods = prod_agg[
        (prod_agg["Avg_Discount"] > avg_disc * 1.2) & 
        (prod_agg["Margin %"] < overall_margin * 0.6)
    ].sort_values("Revenue", ascending=False)

    for _, row in eroding_prods.head(3).iterrows():
        alerts.append({
            "target": row["Product"],
            "type": "Product",
            "revenue": row["Revenue"],
            "discount_rate": row["Avg_Discount"] * 100,
            "margin": row["Margin %"],
            "explanation": f"Average discount is {row['Avg_Discount']*100:.1f}%, compressing product margin down to {row['Margin %']:.1f}%."
        })

    return alerts
