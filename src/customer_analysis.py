"""
PROFITIQ: Customer Intelligence & Quadrant Analysis
Analyzes customer profitability, computes statistical quadrant classifications,
identifies margin-destroying accounts, and builds customer diagnostic drilldowns.
"""

import numpy as np
import pandas as pd
from src.utils import safe_divide

def get_customer_summary_table(df):
    """
    Aggregate transactional data to customer level and classify into Value Segments & Quadrants.
    """
    if df.empty:
        return pd.DataFrame(), 0.0, 0.0

    cust_df = df.groupby("Customer").agg(
        Revenue=("Revenue", "sum"),
        Cost=("Cost", "sum"),
        Discount=("Discount", "sum"),
        Profit=("Profit", "sum"),
        Orders=("Order ID", "nunique") if "Order ID" in df.columns else ("Revenue", "count"),
        Avg_Discount_Rate=("Discount Rate", "mean") if "Discount Rate" in df.columns else ("Revenue", lambda x: 0.0)
    ).reset_index()

    # Calculate Profit Margin %
    cust_df["Profit Margin %"] = np.where(
        cust_df["Revenue"] > 0,
        (cust_df["Profit"] / cust_df["Revenue"]) * 100,
        0.0
    ).round(2)

    cust_df["Avg Order Value"] = (cust_df["Revenue"] / cust_df["Orders"]).round(2)

    # Statistical Thresholds (Medians for robust distribution separation)
    median_rev = float(cust_df["Revenue"].median())
    median_profit = float(cust_df["Profit"].median())

    # 1. Assign Quadrants
    def assign_quadrant(row):
        rev_high = row["Revenue"] >= median_rev
        prof_high = row["Profit"] >= median_profit
        
        if rev_high and prof_high:
            return "High Revenue / High Profit (Stars)"
        elif rev_high and not prof_high:
            return "High Revenue / Low Profit (Margin Traps)"
        elif not rev_high and prof_high:
            return "Low Revenue / High Profit (Niche Gems)"
        else:
            return "Low Revenue / Low Profit (Laggards)"

    cust_df["Quadrant"] = cust_df.apply(assign_quadrant, axis=1)

    # 2. Assign Value Segments (Executive Classification)
    overall_avg_margin = safe_divide(df["Profit"].sum(), df["Revenue"].sum()) * 100

    def assign_value_segment(row):
        if row["Profit"] < 0:
            return "Loss Making"
        elif row["Revenue"] >= median_rev and row["Profit Margin %"] >= overall_avg_margin:
            return "High Value"
        elif row["Revenue"] >= median_rev and row["Profit Margin %"] < overall_avg_margin:
            return "At Risk (Margin Trap)"
        elif row["Revenue"] < median_rev and row["Profit Margin %"] >= overall_avg_margin:
            return "Growth Opportunity"
        else:
            return "Low Value"

    cust_df["Value Segment"] = cust_df.apply(assign_value_segment, axis=1)
    cust_df = cust_df.sort_values("Profit", ascending=False).reset_index(drop=True)

    return cust_df, median_rev, median_profit

def get_customer_deep_dive(df, customer_name):
    """
    Generate deep diagnostic profile and recommended action plan for a specific customer.
    """
    cust_data = df[df["Customer"] == customer_name]
    if cust_data.empty:
        return None

    rev = cust_data["Revenue"].sum()
    cost = cust_data["Cost"].sum()
    profit = cust_data["Profit"].sum()
    disc = cust_data["Discount"].sum()
    margin = safe_divide(profit, rev) * 100
    orders = cust_data["Order ID"].nunique() if "Order ID" in cust_data.columns else len(cust_data)
    avg_disc_rate = (cust_data["Discount Rate"].mean() * 100) if "Discount Rate" in cust_data.columns else 0.0

    # Trend by month
    monthly_trend = cust_data.groupby("YearMonth").agg(
        Revenue=("Revenue", "sum"),
        Profit=("Profit", "sum")
    ).reset_index()

    # Category breakdown
    cat_breakdown = cust_data.groupby("Category").agg(
        Revenue=("Revenue", "sum"),
        Profit=("Profit", "sum")
    ).reset_index()
    cat_breakdown["Margin %"] = (cat_breakdown["Profit"] / cat_breakdown["Revenue"] * 100).round(2)

    # Root Cause & Recommended Action Logic
    if profit < 0:
        diagnosis = "Negative Profitability: This account is eroding company margin. The combination of discounts and high product fulfillment costs is exceeding net revenue."
        action = "Immediate Contract Renegotiation: Cap discounts at 10%, restructure payment terms, or adjust minimum order quantities to restore positive unit economics."
        status_badge = "🔴 Critical Loss Maker"
    elif margin < 10 and avg_disc_rate > 20:
        diagnosis = f"Discount Leakage Trap: High revenue (${rev:,.0f}) is masked by aggressive discounting ({avg_disc_rate:.1f}% avg discount), resulting in razor-thin {margin:.1f}% margin."
        action = "Discount Guardrails: Shift sales incentives away from gross volume to gross margin. Implement stepped discounting tied to volume commitments."
        status_badge = "🟠 Margin Destroyer"
    elif margin >= 30:
        diagnosis = f"High-Value Star: Exceptionally profitable account generating {margin:.1f}% margin with disciplined discounting."
        action = "Account Expansion: Assign senior executive sponsor, explore multi-year agreements, and cross-sell higher tier product offerings."
        status_badge = "🟢 Strategic Anchor"
    else:
        diagnosis = f"Standard Account: Generates stable revenue with moderate margin realization ({margin:.1f}%)."
        action = "Continuous Optimization: Review product mix toward higher-margin categories to improve profitability."
        status_badge = "🔵 Balanced Account"

    return {
        "customer": customer_name,
        "revenue": rev,
        "cost": cost,
        "profit": profit,
        "discount": disc,
        "margin": margin,
        "orders": orders,
        "avg_discount_rate": avg_disc_rate,
        "status_badge": status_badge,
        "diagnosis": diagnosis,
        "recommended_action": action,
        "monthly_trend": monthly_trend,
        "cat_breakdown": cat_breakdown
    }
