"""
PROFITIQ: Insight Engine
Automated, data-grounded analytical engine. Inspects filtered transactional metrics
and computes rigorous business conclusions answering WHAT, WHY, and WHAT ACTION.
"""

import numpy as np
import pandas as pd
from src.utils import safe_divide, format_currency

def generate_executive_insights(df):
    """
    Generate 3-6 concise, data-driven executive takeaways for the overview dashboard.
    """
    insights = []
    if df.empty or len(df) < 5:
        return ["Insufficient data to generate automated executive insights."]

    total_rev = df["Revenue"].sum()
    total_prof = df["Profit"].sum()
    overall_margin = safe_divide(total_prof, total_rev) * 100

    # 1. Customer Revenue vs Profit Divergence Insight
    cust_agg = df.groupby("Customer").agg(
        Revenue=("Revenue", "sum"),
        Profit=("Profit", "sum")
    ).reset_index()
    cust_agg["Margin %"] = (cust_agg["Profit"] / cust_agg["Revenue"] * 100).round(1)
    
    top_rev_cust = cust_agg.sort_values("Revenue", ascending=False).iloc[0]
    top_prof_cust = cust_agg.sort_values("Profit", ascending=False).iloc[0]

    if top_rev_cust["Customer"] != top_prof_cust["Customer"]:
        insights.append(
            f"Revenue vs Profit Divergence: Top revenue generator '{top_rev_cust['Customer']}' ({format_currency(top_rev_cust['Revenue'])}, {top_rev_cust['Margin %']}% margin) is NOT the top profit creator. '{top_prof_cust['Customer']}' generates higher net profit ({format_currency(top_prof_cust['Profit'])})."
        )
    else:
        insights.append(
            f"Anchor Account: '{top_rev_cust['Customer']}' leads both top-line revenue ({format_currency(top_rev_cust['Revenue'])}) and net profit contribution ({format_currency(top_prof_cust['Profit'])})."
        )

    # 2. Regional Driver Insight
    if "Region" in df.columns:
        reg_agg = df.groupby("Region").agg(
            Profit=("Profit", "sum"),
            Revenue=("Revenue", "sum")
        ).reset_index()
        reg_agg["Margin %"] = (reg_agg["Profit"] / reg_agg["Revenue"] * 100).round(1)
        top_reg = reg_agg.sort_values("Profit", ascending=False).iloc[0]
        insights.append(
            f"Regional Value Engine: Region '{top_reg['Region']}' delivers the largest profit share ({format_currency(top_reg['Profit'])}, {top_reg['Margin %']}% operating margin)."
        )

    # 3. Category Margin Differential Insight
    if "Category" in df.columns:
        cat_agg = df.groupby("Category").agg(
            Revenue=("Revenue", "sum"),
            Profit=("Profit", "sum")
        ).reset_index()
        cat_agg["Margin %"] = (cat_agg["Profit"] / cat_agg["Revenue"] * 100).round(1)
        highest_margin_cat = cat_agg.sort_values("Margin %", ascending=False).iloc[0]
        lowest_margin_cat = cat_agg.sort_values("Margin %", ascending=True).iloc[0]
        
        insights.append(
            f"Category Spread: '{highest_margin_cat['Category']}' achieves the strongest profitability ({highest_margin_cat['Margin %']}% margin), while '{lowest_margin_cat['Category']}' operates at the lowest margin ({lowest_margin_cat['Margin %']}%)."
        )

    # 4. Discount Impact Insight
    if "Discount Rate" in df.columns:
        avg_disc = df["Discount Rate"].mean() * 100
        disc_corr = df["Discount Rate"].corr(df["Profit Margin %"]) if len(df) > 10 else 0
        if disc_corr < -0.3:
            insights.append(
                f"Discount Erosion Warning: Strong inverse correlation ({disc_corr:.2f}) between discounts and profit margins. Transactions with discounts above {avg_disc:.1f}% show acute margin compression."
            )
        else:
            insights.append(
                f"Discount Discipline: Average discount rate across current filters is {avg_disc:.1f}% with total discount allowance of {format_currency(df['Discount'].sum())}."
            )

    # 5. Loss Making Segment Check
    loss_orders = df[df["Profit"] < 0]
    if len(loss_orders) > 0:
        loss_val = abs(loss_orders["Profit"].sum())
        insights.append(
            f"Margin Leakage: {len(loss_orders)} loss-making transactions identified, draining {format_currency(loss_val)} in net operating profit."
        )

    return insights

def generate_comprehensive_business_findings(df):
    """
    Generate in-depth findings grouped into Executive Summary, Key Findings,
    Profitability Risks, and Opportunities for the Business Insights center.
    """
    if df.empty:
        return {
            "summary": "No data available.",
            "key_findings": [],
            "risks": [],
            "opportunities": []
        }

    total_rev = df["Revenue"].sum()
    total_prof = df["Profit"].sum()
    overall_margin = safe_divide(total_prof, total_rev) * 100
    total_disc = df["Discount"].sum()

    # Executive Summary Paragraph
    summary = (
        f"Across the analyzed dataset, total net revenue reached {format_currency(total_rev)} with cumulative profit of "
        f"{format_currency(total_prof)}, delivering an overall operating margin of {overall_margin:.1f}%. "
        f"A total of {format_currency(total_disc)} was distributed in customer discounts. "
    )

    # Key Findings
    key_findings = []
    
    # 1. Pareto Concentration
    cust_rev = df.groupby("Customer")["Revenue"].sum().sort_values(ascending=False)
    cust_prof = df.groupby("Customer")["Profit"].sum().sort_values(ascending=False)
    top_20_pct_count = max(1, int(len(cust_rev) * 0.2))
    top_rev_share = (cust_rev.head(top_20_pct_count).sum() / total_rev * 100) if total_rev > 0 else 0
    top_prof_share = (cust_prof.head(top_20_pct_count).sum() / total_prof * 100) if total_prof > 0 else 0
    
    key_findings.append({
        "title": "Value Concentration (Pareto Principle)",
        "detail": f"The top {top_20_pct_count} customers ({top_20_pct_count/len(cust_rev)*100:.0f}% of client base) generate {top_rev_share:.1f}% of total revenue and {top_prof_share:.1f}% of total profit."
    })

    # 2. Quadrant Distribution
    med_rev = cust_rev.median()
    med_prof = cust_prof.median()
    trap_custs = df.groupby("Customer").agg({"Revenue": "sum", "Profit": "sum"}).reset_index()
    traps = trap_custs[(trap_custs["Revenue"] >= med_rev) & (trap_custs["Profit"] < med_prof)]
    
    key_findings.append({
        "title": "Margin Trap Account Prevalence",
        "detail": f"Identified {len(traps)} major accounts in the 'High Revenue / Low Profit' quadrant, representing significant commercial revenue that fails to flow through to bottom-line profit."
    })

    # Risks
    risks = []
    # Chronic loss makers
    loss_custs = trap_custs[trap_custs["Profit"] < 0]
    if not loss_custs.empty:
        worst_c = loss_custs.sort_values("Profit").iloc[0]
        risks.append({
            "title": f"Negative Customer Profitability ({len(loss_custs)} Accounts)",
            "impact": f"Worst account '{worst_c['Customer']}' generated a net loss of -${abs(worst_c['Profit']):,.0f}. Total loss across negative accounts: -${abs(loss_custs['Profit'].sum()):,.0f}."
        })

    # Uncontrolled discount erosion
    if "Discount Rate" in df.columns:
        deep_disc = df[df["Discount Rate"] > 0.25]
        if not deep_disc.empty:
            deep_margin = safe_divide(deep_disc["Profit"].sum(), deep_disc["Revenue"].sum()) * 100
            risks.append({
                "title": "Deep Discount Margin Compression",
                "impact": f"{len(deep_disc)} orders received discounts > 25%, resulting in a compressed margin of {deep_margin:.1f}% compared to company baseline of {overall_margin:.1f}%."
            })

    # Opportunities
    opportunities = []
    # High margin niche accounts
    gems = trap_custs[(trap_custs["Revenue"] < med_rev) & (trap_custs["Profit"] / trap_custs["Revenue"] * 100 > overall_margin * 1.5)]
    if not gems.empty:
        opportunities.append({
            "title": f"Expand High-Margin Niche Accounts ({len(gems)} Identified)",
            "action": f"Accounts such as '{gems.iloc[0]['Customer']}' deliver premium margins (>{overall_margin*1.5:.0f}%). Increasing share-of-wallet with these accounts offers low-risk profit expansion."
        })

    # High margin product cross-sell
    prod_agg = df.groupby(["Product", "Category"]).agg({"Revenue": "sum", "Profit": "sum"}).reset_index()
    prod_agg["Margin %"] = (prod_agg["Profit"] / prod_agg["Revenue"] * 100).round(1)
    star_prods = prod_agg[prod_agg["Margin %"] > 35].sort_values("Profit", ascending=False)
    if not star_prods.empty:
        star_p = star_prods.iloc[0]
        opportunities.append({
            "title": f"Cross-Sell Margin Leader: '{star_p['Product']}'",
            "action": f"Product delivers {star_p['Margin %']}% margin. Bundle this offering with lower-margin products to lift overall basket profitability."
        })

    return {
        "summary": summary,
        "key_findings": key_findings,
        "risks": risks,
        "opportunities": opportunities
    }
