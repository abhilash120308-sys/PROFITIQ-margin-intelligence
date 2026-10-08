"""
PROFITIQ: Recommendation Engine
Translates analytical findings into executive action plans with structured
'INSIGHT -> WHY IT MATTERS -> RECOMMENDED ACTION' triplets.
"""

import pandas as pd
from src.utils import safe_divide, format_currency

def generate_strategic_recommendations(df):
    """
    Generate structured, high-priority executive recommendations based on dataset metrics.
    """
    recommendations = []
    if df.empty:
        return recommendations

    total_rev = df["Revenue"].sum()
    total_prof = df["Profit"].sum()
    overall_margin = safe_divide(total_prof, total_rev) * 100
    avg_disc_rate = (df["Discount Rate"].mean() * 100) if "Discount Rate" in df.columns else 0.0

    cust_agg = df.groupby("Customer").agg(
        Revenue=("Revenue", "sum"),
        Profit=("Profit", "sum"),
        Discount=("Discount", "sum"),
        Orders=("Order ID", "nunique") if "Order ID" in df.columns else ("Revenue", "count"),
        Avg_Disc=("Discount Rate", "mean") if "Discount Rate" in df.columns else ("Revenue", lambda x: 0.0)
    ).reset_index()
    cust_agg["Margin %"] = (cust_agg["Profit"] / cust_agg["Revenue"] * 100).round(1)

    med_rev = cust_agg["Revenue"].median()

    # 1. Recommendation for High-Revenue / Low-Margin Customers (The Core Problem)
    traps = cust_agg[(cust_agg["Revenue"] >= med_rev) & (cust_agg["Margin %"] < overall_margin * 0.7)]
    if not traps.empty:
        worst_trap = traps.sort_values("Revenue", ascending=False).iloc[0]
        recommendations.append({
            "pillar": "Pricing & Discount Governance",
            "priority": "HIGH",
            "insight": f"High revenue does not translate into profitability for account '{worst_trap['Customer']}'.",
            "why_it_matters": f"This account generates {format_currency(worst_trap['Revenue'])} in gross revenue, but realizes an operating margin of only {worst_trap['Margin %']}%, significantly below the company benchmark of {overall_margin:.1f}%. High discount rates ({worst_trap['Avg_Disc']*100:.1f}%) are eroding bottom-line margin.",
            "recommended_action": f"Establish strict discount caps (max 10%) for '{worst_trap['Customer']}' upon contract renewal. Transition sales compensation from gross order volume to gross margin contribution to eliminate volume-chasing incentives."
        })

    # 2. Recommendation for Loss-Making Accounts
    loss_makers = cust_agg[cust_agg["Profit"] < 0].sort_values("Profit")
    if not loss_makers.empty:
        worst_loss = loss_makers.iloc[0]
        total_loss_val = abs(loss_makers["Profit"].sum())
        recommendations.append({
            "pillar": "Customer Portfolio Rationalization",
            "priority": "CRITICAL",
            "insight": f"{len(loss_makers)} customer accounts are actively destroying enterprise value.",
            "why_it_matters": f"Cumulative loss across these accounts is -{format_currency(total_loss_val)}. For instance, '{worst_loss['Customer']}' generated -{format_currency(abs(worst_loss['Profit']))} in net margin due to heavy discounting and high cost-of-service.",
            "recommended_action": f"Issue an immediate pricing moratorium for negative-margin accounts. Restructure pricing to achieve a minimum 15% contribution margin, introduce minimum order sizes, or offboard persistent loss-makers to free operational capacity."
        })

    # 3. Recommendation for Product Portfolio Optimization
    prod_agg = df.groupby(["Product", "Category"]).agg(
        Revenue=("Revenue", "sum"),
        Profit=("Profit", "sum"),
        Orders=("Order ID", "nunique") if "Order ID" in df.columns else ("Revenue", "count")
    ).reset_index()
    prod_agg["Margin %"] = (prod_agg["Profit"] / prod_agg["Revenue"] * 100).round(1)

    loss_prods = prod_agg[prod_agg["Profit"] < 0].sort_values("Profit")
    if not loss_prods.empty:
        worst_p = loss_prods.iloc[0]
        recommendations.append({
            "pillar": "Product Portfolio Optimization",
            "priority": "HIGH",
            "insight": f"Product '{worst_p['Product']}' in '{worst_p['Category']}' is operating at a net loss.",
            "why_it_matters": f"Generated -{format_currency(abs(worst_p['Profit']))} across {worst_p['Orders']} transactions. Current list pricing does not cover direct unit COGS and freight/fulfillment expenses.",
            "recommended_action": f"Audit bill-of-materials and supplier contracts for '{worst_p['Product']}'. Immediately implement a 12% price increase or discontinue discounted promotion tiers on this SKU."
        })

    # 4. Recommendation for High-Margin Growth Acceleration
    stars = cust_agg[(cust_agg["Margin %"] > overall_margin * 1.3) & (cust_agg["Profit"] > 0)].sort_values("Profit", ascending=False)
    if not stars.empty:
        star_c = stars.iloc[0]
        recommendations.append({
            "pillar": "Strategic Account Growth",
            "priority": "MEDIUM",
            "insight": f"High-margin customer '{star_c['Customer']}' represents prime expansion potential.",
            "why_it_matters": f"Achieves a stellar {star_c['Margin %']}% profit margin and {format_currency(star_c['Profit'])} net profit, proving high willingness-to-pay and strong product-market fit.",
            "recommended_action": f"Assign a dedicated enterprise success manager to '{star_c['Customer']}'. Develop tailored cross-sell campaigns for premium product lines to expand wallet share."
        })

    # 5. Recommendation for Regional Pricing Discipline
    if "Region" in df.columns:
        reg_agg = df.groupby("Region").agg(
            Revenue=("Revenue", "sum"),
            Profit=("Profit", "sum"),
            Avg_Disc=("Discount Rate", "mean") if "Discount Rate" in df.columns else ("Revenue", lambda x: 0.0)
        ).reset_index()
        reg_agg["Margin %"] = (reg_agg["Profit"] / reg_agg["Revenue"] * 100).round(1)
        low_reg = reg_agg.sort_values("Margin %").iloc[0]
        high_reg = reg_agg.sort_values("Margin %", ascending=False).iloc[0]
        
        if high_reg["Margin %"] - low_reg["Margin %"] > 10:
            recommendations.append({
                "pillar": "Regional Pricing Harmonization",
                "priority": "MEDIUM",
                "insight": f"Significant regional margin variance between '{high_reg['Region']}' ({high_reg['Margin %']}%) and '{low_reg['Region']}' ({low_reg['Margin %']}%).",
                "why_it_matters": f"Region '{low_reg['Region']}' suffers from excessive discounting ({low_reg['Avg_Disc']*100:.1f}% avg) and inconsistent pricing guardrails relative to '{high_reg['Region']}'.",
                "recommended_action": f"Standardize regional pricing approval thresholds. Require regional VP approval for any quote exceeding 12% discount in '{low_reg['Region']}'."
            })

    return recommendations
