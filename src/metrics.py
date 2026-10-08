"""
PROFITIQ: Metrics & KPI Engine
Calculates executive KPIs, period-over-period comparisons,
transparent Profitability Health Score, and automated business alert triggers.
"""

import numpy as np
import pandas as pd
from src.utils import safe_divide

def calculate_executive_kpis(df):
    """
    Calculate high-level financial summary KPIs and period-over-period deltas.
    Returns:
        dict: Comprehensive KPI metrics dictionary
    """
    if df.empty:
        return {
            "total_revenue": 0.0, "total_cost": 0.0, "total_profit": 0.0,
            "profit_margin_pct": 0.0, "total_discount": 0.0, "order_count": 0,
            "customer_count": 0, "product_count": 0, "avg_order_value": 0.0,
            "avg_profit_per_order": 0.0, "deltas": {}
        }

    total_revenue = float(df["Revenue"].sum())
    total_cost = float(df["Cost"].sum())
    total_profit = float(df["Profit"].sum())
    profit_margin_pct = safe_divide(total_profit, total_revenue) * 100.0
    total_discount = float(df["Discount"].sum())
    order_count = int(df["Order ID"].nunique()) if "Order ID" in df.columns else len(df)
    customer_count = int(df["Customer"].nunique())
    product_count = int(df["Product"].nunique())
    
    avg_order_value = safe_divide(total_revenue, order_count)
    avg_profit_per_order = safe_divide(total_profit, order_count)

    # Compute Period-over-Period Delta if multiple periods exist
    deltas = {}
    if "Order Date" in df.columns and len(df) > 10:
        sorted_df = df.sort_values("Order Date")
        midpoint = len(sorted_df) // 2
        p1 = sorted_df.iloc[:midpoint]
        p2 = sorted_df.iloc[midpoint:]
        
        p1_rev = p1["Revenue"].sum()
        p2_rev = p2["Revenue"].sum()
        if p1_rev > 0:
            rev_change = ((p2_rev - p1_rev) / p1_rev) * 100
            deltas["revenue"] = f"{'+' if rev_change >= 0 else ''}{rev_change:.1f}% vs H1"
            
        p1_prof = p1["Profit"].sum()
        p2_prof = p2["Profit"].sum()
        if abs(p1_prof) > 0:
            prof_change = ((p2_prof - p1_prof) / abs(p1_prof)) * 100
            deltas["profit"] = f"{'+' if prof_change >= 0 else ''}{prof_change:.1f}% vs H1"
            
        p1_margin = safe_divide(p1_prof, p1_rev) * 100
        p2_margin = safe_divide(p2_prof, p2_rev) * 100
        margin_change = p2_margin - p1_margin
        deltas["margin"] = f"{'+' if margin_change >= 0 else ''}{margin_change:.1f} pts"

    return {
        "total_revenue": total_revenue,
        "total_cost": total_cost,
        "total_profit": total_profit,
        "profit_margin_pct": profit_margin_pct,
        "total_discount": total_discount,
        "order_count": order_count,
        "customer_count": customer_count,
        "product_count": product_count,
        "avg_order_value": avg_order_value,
        "avg_profit_per_order": avg_profit_per_order,
        "deltas": deltas
    }

def calculate_profitability_health_score(df):
    """
    Calculate an executive 0-100% Profitability Health Score with transparent business logic.
    Components:
    1. Operating Margin realization (30 pts max)
    2. Profitable Customer breadth (25 pts max)
    3. Profitable Product portfolio (20 pts max)
    4. Discount discipline (15 pts max)
    5. Loss containment (10 pts max)
    """
    if df.empty:
        return 0, {}, "Poor"

    total_revenue = df["Revenue"].sum()
    total_profit = df["Profit"].sum()
    overall_margin = safe_divide(total_profit, total_revenue) * 100

    # 1. Margin Component (30 pts) - Target 25% margin = full 30 pts
    margin_score = min(30.0, max(0.0, (overall_margin / 25.0) * 30.0))

    # 2. Profitable Customer Breadth (25 pts)
    cust_profit = df.groupby("Customer")["Profit"].sum()
    prof_cust_ratio = safe_divide((cust_profit > 0).sum(), len(cust_profit))
    cust_score = prof_cust_ratio * 25.0

    # 3. Profitable Product Portfolio (20 pts)
    prod_profit = df.groupby("Product")["Profit"].sum()
    prof_prod_ratio = safe_divide((prod_profit > 0).sum(), len(prod_profit))
    prod_score = prof_prod_ratio * 20.0

    # 4. Discount Discipline (15 pts) - Penalize avg discounts > 15%
    avg_discount_rate = df["Discount Rate"].mean() if "Discount Rate" in df.columns else 0.0
    discount_score = max(0.0, min(15.0, 15.0 - (avg_discount_rate * 50.0)))

    # 5. Loss Containment (10 pts) - Ratio of revenue that does NOT belong to loss-making orders
    loss_orders_rev = df[df["Profit"] < 0]["Revenue"].sum()
    loss_rev_ratio = safe_divide(loss_orders_rev, total_revenue)
    loss_score = max(0.0, (1.0 - (loss_rev_ratio * 2.0)) * 10.0)

    total_score = round(min(100.0, max(0.0, margin_score + cust_score + prod_score + discount_score + loss_score)), 1)

    if total_score >= 80:
        status_label = "Optimal"
        status_color = "#10b981"
    elif total_score >= 65:
        status_label = "Healthy"
        status_color = "#2563eb"
    elif total_score >= 50:
        status_label = "Moderate Risk"
        status_color = "#f59e0b"
    else:
        status_label = "Critical Margin Erosion"
        status_color = "#ef4444"

    breakdown = {
        "overall_margin_pts": (round(margin_score, 1), 30),
        "customer_breadth_pts": (round(cust_score, 1), 25),
        "product_breadth_pts": (round(prod_score, 1), 20),
        "discount_discipline_pts": (round(discount_score, 1), 15),
        "loss_containment_pts": (round(loss_score, 1), 10),
        "status_label": status_label,
        "status_color": status_color,
        "prof_cust_pct": round(prof_cust_ratio * 100, 1),
        "prof_prod_pct": round(prof_prod_ratio * 100, 1),
        "avg_discount_pct": round(avg_discount_rate * 100, 1)
    }

    return total_score, breakdown, status_label

def generate_automated_alerts(df):
    """
    Generate live, data-grounded executive alerts (Loss, Margin, Discount, Opportunity).
    """
    alerts = []
    if df.empty:
        return alerts

    # 1. Loss Alerts 🔴
    cust_agg = df.groupby("Customer").agg({"Revenue": "sum", "Profit": "sum"}).reset_index()
    loss_customers = cust_agg[cust_agg["Profit"] < 0].sort_values("Profit")
    if not loss_customers.empty:
        worst_cust = loss_customers.iloc[0]
        alerts.append({
            "type": "loss",
            "title": f"Negative Margin Customer: {worst_cust['Customer']}",
            "description": f"Generated negative cumulative profit of -${abs(worst_cust['Profit']):,.0f} on ${worst_cust['Revenue']:,.0f} in revenue. Immediate pricing review required."
        })

    prod_agg = df.groupby("Product").agg({"Revenue": "sum", "Profit": "sum"}).reset_index()
    loss_prods = prod_agg[prod_agg["Profit"] < 0].sort_values("Profit")
    if not loss_prods.empty:
        worst_prod = loss_prods.iloc[0]
        alerts.append({
            "type": "loss",
            "title": f"Loss-Making Product: {worst_prod['Product']}",
            "description": f"Has generated -${abs(worst_prod['Profit']):,.0f} in net profit. Cost structure or discount limits must be re-evaluated."
        })

    # 2. Margin Erosion Alert 🟠 (High Revenue, Subpar Margin)
    med_rev = cust_agg["Revenue"].median()
    avg_margin = safe_divide(df["Profit"].sum(), df["Revenue"].sum()) * 100
    high_rev_low_margin = cust_agg[
        (cust_agg["Revenue"] >= med_rev) & 
        ((cust_agg["Profit"] / cust_agg["Revenue"] * 100) < (avg_margin * 0.5)) &
        (cust_agg["Profit"] > 0)
    ].sort_values("Revenue", ascending=False)
    
    if not high_rev_low_margin.empty:
        target = high_rev_low_margin.iloc[0]
        margin_pct = (target["Profit"] / target["Revenue"]) * 100
        alerts.append({
            "type": "margin",
            "title": f"High Revenue / Low Margin: {target['Customer']}",
            "description": f"Contributes significant revenue (${target['Revenue']:,.0f}) but only {margin_pct:.1f}% profit margin (vs {avg_margin:.1f}% average). Profit-blind strategy risk."
        })

    # 3. Discount Alert 🟡
    if "Discount Rate" in df.columns:
        high_disc_orders = df[df["Discount Rate"] > 0.25]
        if len(high_disc_orders) > 0:
            disc_loss = high_disc_orders[high_disc_orders["Profit"] < 0]
            if len(disc_loss) > 0:
                alerts.append({
                    "type": "discount",
                    "title": f"Discount-Driven Margin Erosion Detected",
                    "description": f"{len(disc_loss)} transactions with discounts over 25% resulted in net negative profit, draining ${abs(disc_loss['Profit'].sum()):,.0f}."
                })

    # 4. Opportunity 🟢
    high_margin_customers = cust_agg[
        (cust_agg["Profit"] / cust_agg["Revenue"] * 100 > 35) & 
        (cust_agg["Revenue"] < med_rev)
    ].sort_values("Profit", ascending=False)
    if not high_margin_customers.empty:
        gem = high_margin_customers.iloc[0]
        gem_margin = (gem["Profit"] / gem["Revenue"]) * 100
        alerts.append({
            "type": "opportunity",
            "title": f"High-Margin Growth Candidate: {gem['Customer']}",
            "description": f"Delivers an exceptional {gem_margin:.1f}% profit margin. Consider prioritizing account expansion and wallet-share capture."
        })

    return alerts
