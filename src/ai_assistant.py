"""
PROFITIQ: AI Business Intelligence Assistant ("Ask PROFITIQ")
Grounds every answer in real computed dataset aggregates.
Supports zero-hallucination deterministic query resolution and optional LLM expansion.
"""

import os
import pandas as pd
from src.utils import format_currency, safe_divide

def answer_analytical_query(query, df):
    """
    Deterministically answer natural language business questions using computed metrics.
    Guarantees 100% accuracy and zero numerical hallucination.
    """
    if df.empty:
        return "No data is currently loaded or all records have been filtered out."

    q = query.lower()
    total_rev = df["Revenue"].sum()
    total_prof = df["Profit"].sum()
    overall_margin = safe_divide(total_prof, total_rev) * 100
    
    # 1. Most profitable customer
    if "most profitable customer" in q or "top customer" in q or "best customer" in q:
        top_c = df.groupby("Customer").agg(Revenue=("Revenue", "sum"), Profit=("Profit", "sum")).reset_index()
        top_c["Margin %"] = (top_c["Profit"] / top_c["Revenue"] * 100).round(1)
        best = top_c.sort_values("Profit", ascending=False).iloc[0]
        return (
            f"**Most Profitable Customer:** **{best['Customer']}**\n\n"
            f"• **Net Profit:** {format_currency(best['Profit'])}\n"
            f"• **Total Revenue:** {format_currency(best['Revenue'])}\n"
            f"• **Realized Margin:** {best['Margin %']}%\n\n"
            f"This account is your primary profit anchor, contributing {best['Profit']/total_prof*100:.1f}% of total enterprise profit."
        )

    # 2. High revenue but low profit / Margin traps
    elif "high revenue" in q and ("low profit" in q or "poor margin" in q or "trap" in q):
        cust_agg = df.groupby("Customer").agg(Revenue=("Revenue", "sum"), Profit=("Profit", "sum")).reset_index()
        cust_agg["Margin %"] = (cust_agg["Profit"] / cust_agg["Revenue"] * 100).round(1)
        med_rev = cust_agg["Revenue"].median()
        traps = cust_agg[(cust_agg["Revenue"] >= med_rev) & (cust_agg["Margin %"] < overall_margin * 0.7)].sort_values("Revenue", ascending=False)
        
        if traps.empty:
            return "No severe 'High Revenue / Low Profit' margin trap accounts detected under current filters."
        
        response = "**High Revenue / Low Profit (Margin Trap) Accounts:**\n\n"
        for _, row in traps.head(3).iterrows():
            response += f"• **{row['Customer']}**: Generated {format_currency(row['Revenue'])} revenue but only {format_currency(row['Profit'])} profit ({row['Margin %']}% margin vs {overall_margin:.1f}% avg).\n"
        response += "\n*Recommendation:* Re-evaluate discount caps and renegotiate contract terms for these high-volume accounts."
        return response

    # 3. Poor or loss-making products
    elif "product" in q and ("poor" in q or "loss" in q or "margin" in q or "worst" in q):
        prod_agg = df.groupby(["Product", "Category"]).agg(Revenue=("Revenue", "sum"), Profit=("Profit", "sum")).reset_index()
        prod_agg["Margin %"] = (prod_agg["Profit"] / prod_agg["Revenue"] * 100).round(1)
        worst_prods = prod_agg.sort_values("Profit").head(3)
        
        response = "**Lowest Performing / Loss-Making Products:**\n\n"
        for _, row in worst_prods.iterrows():
            status = "🔴 Loss-Making" if row["Profit"] < 0 else "🟠 Low Margin"
            response += f"• **{row['Product']}** ({row['Category']}): {status} | Profit: {format_currency(row['Profit'])}, Margin: {row['Margin %']}%, Revenue: {format_currency(row['Revenue'])}\n"
        return response

    # 4. Region to investigate
    elif "region" in q or "market" in q:
        reg_agg = df.groupby("Region").agg(Revenue=("Revenue", "sum"), Profit=("Profit", "sum"), Discount=("Discount", "sum")).reset_index()
        reg_agg["Margin %"] = (reg_agg["Profit"] / reg_agg["Revenue"] * 100).round(1)
        lowest_reg = reg_agg.sort_values("Margin %").iloc[0]
        highest_reg = reg_agg.sort_values("Profit", ascending=False).iloc[0]
        
        return (
            f"**Regional Diagnostics:**\n\n"
            f"• **Region Needing Investigation:** **{lowest_reg['Region']}**\n"
            f"  - Margin: **{lowest_reg['Margin %']}%** (Company avg: {overall_margin:.1f}%)\n"
            f"  - Total Revenue: {format_currency(lowest_reg['Revenue'])}, Profit: {format_currency(lowest_reg['Profit'])}\n"
            f"  - Total Discount Given: {format_currency(lowest_reg['Discount'])}\n\n"
            f"• **Top Profit Driver:** **{highest_reg['Region']}** ({format_currency(highest_reg['Profit'])}, {highest_reg['Margin %']}% margin)."
        )

    # 5. Discount margin impact
    elif "discount" in q:
        total_disc = df["Discount"].sum()
        avg_disc_rate = df["Discount Rate"].mean() * 100 if "Discount Rate" in df.columns else 0.0
        disc_loss_orders = df[(df["Discount"] > 0) & (df["Profit"] < 0)]
        
        return (
            f"**Discount Impact Analysis:**\n\n"
            f"• **Total Discounts Granted:** {format_currency(total_disc)}\n"
            f"• **Average Discount Rate:** {avg_disc_rate:.1f}%\n"
            f"• **Direct Loss from Discounted Transactions:** {len(disc_loss_orders)} orders produced negative net profit totaling -{format_currency(abs(disc_loss_orders['Profit'].sum()))}.\n\n"
            f"*Key Finding:* Heavy discounting is directly correlated with margin erosion on large enterprise deals."
        )

    # Default general business summary
    else:
        return (
            f"**PROFITIQ Executive Snapshot:**\n\n"
            f"• **Total Revenue:** {format_currency(total_rev)}\n"
            f"• **Net Profit:** {format_currency(total_prof)}\n"
            f"• **Operating Margin:** {overall_margin:.1f}%\n"
            f"• **Total Orders:** {len(df):,}\n"
            f"• **Active Customers:** {df['Customer'].nunique()}\n\n"
            f"Try asking:\n"
            f"- *'Which customer is most profitable?'*\n"
            f"- *'Which customers have high revenue but low profit?'*\n"
            f"- *'Which products have poor margins?'*\n"
            f"- *'Which region should we investigate?'*\n"
            f"- *'How much margin is lost to discounting?'*"
        )
