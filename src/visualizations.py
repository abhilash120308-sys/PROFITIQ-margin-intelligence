"""
PROFITIQ: Visualization Engine
High-fidelity Plotly charts styled to match executive enterprise analytics (PowerBI, Tableau, Looker).
"""

import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from src.utils import format_currency

# Enterprise Color Palette
NAVY = "#0f172a"
BLUE_PRIMARY = "#2563eb"
BLUE_LIGHT = "#60a5fa"
EMERALD = "#10b981"
RED_LOSS = "#ef4444"
AMBER_WARN = "#f59e0b"
PURPLE = "#8b5cf6"
SLATE_GRID = "#f1f5f9"
TEXT_COLOR = "#334155"

def apply_enterprise_theme(fig, title_text=""):
    """Apply unified enterprise dashboard layout styling to any Plotly figure."""
    fig.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(family="Plus Jakarta Sans, sans-serif", color=TEXT_COLOR, size=12),
        margin=dict(l=20, r=20, t=45, b=20),
        hoverlabel=dict(bgcolor="#ffffff", font_size=12, font_family="Plus Jakarta Sans"),
        title=dict(text=title_text, font=dict(size=14, color=NAVY, weight=700)) if title_text else None
    )
    fig.update_xaxes(gridcolor=SLATE_GRID, zerolinecolor="#e2e8f0", showline=False)
    fig.update_yaxes(gridcolor=SLATE_GRID, zerolinecolor="#e2e8f0", showline=False)
    return fig

# -------------------------------------------------------------
# 1. EXECUTIVE OVERVIEW CHARTS
# -------------------------------------------------------------

def plot_revenue_profit_trend(df):
    """Monthly Revenue vs Profit Trend line & area chart."""
    if df.empty or "Order Date" not in df.columns:
        return go.Figure()

    trend = df.groupby("YearMonth").agg(
        Revenue=("Revenue", "sum"),
        Profit=("Profit", "sum")
    ).reset_index().sort_values("YearMonth")

    fig = go.Figure()
    fig.add_trace(go.Bar(
        x=trend["YearMonth"],
        y=trend["Revenue"],
        name="Revenue",
        marker_color="#93c5fd",
        opacity=0.75,
        hovertemplate="<b>%{x}</b><br>Revenue: $%{y:,.0f}<extra></extra>"
    ))
    fig.add_trace(go.Scatter(
        x=trend["YearMonth"],
        y=trend["Profit"],
        name="Net Profit",
        mode="lines+markers",
        line=dict(color=BLUE_PRIMARY, width=3),
        marker=dict(size=7, color=BLUE_PRIMARY),
        hovertemplate="<b>%{x}</b><br>Profit: $%{y:,.0f}<extra></extra>"
    ))

    apply_enterprise_theme(fig, "Revenue vs Net Profit Trend")
    fig.update_layout(
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        barmode="overlay"
    )
    return fig

def plot_revenue_profit_by_category(df):
    """Category comparison grouped horizontal bar."""
    if df.empty:
        return go.Figure()

    cat_df = df.groupby("Category").agg(
        Revenue=("Revenue", "sum"),
        Profit=("Profit", "sum")
    ).reset_index().sort_values("Revenue", ascending=True)

    fig = go.Figure()
    fig.add_trace(go.Bar(
        y=cat_df["Category"],
        x=cat_df["Revenue"],
        name="Revenue",
        orientation="h",
        marker_color="#94a3b8",
        hovertemplate="<b>%{y}</b><br>Revenue: $%{x:,.0f}<extra></extra>"
    ))
    fig.add_trace(go.Bar(
        y=cat_df["Category"],
        x=cat_df["Profit"],
        name="Profit",
        orientation="h",
        marker_color=BLUE_PRIMARY,
        hovertemplate="<b>%{y}</b><br>Profit: $%{x:,.0f}<extra></extra>"
    ))

    apply_enterprise_theme(fig, "Revenue & Profit by Category")
    fig.update_layout(
        barmode="group",
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
    )
    return fig

def plot_margin_by_region(df):
    """Regional profit margin % bar chart."""
    if df.empty:
        return go.Figure()

    reg = df.groupby("Region").agg(
        Revenue=("Revenue", "sum"),
        Profit=("Profit", "sum")
    ).reset_index()
    reg["Margin %"] = (reg["Profit"] / reg["Revenue"] * 100).round(1)
    reg = reg.sort_values("Margin %", ascending=False)

    colors = [EMERALD if m >= 20 else (AMBER_WARN if m >= 10 else RED_LOSS) for m in reg["Margin %"]]

    fig = go.Figure(go.Bar(
        x=reg["Region"],
        y=reg["Margin %"],
        marker_color=colors,
        text=reg["Margin %"].apply(lambda x: f"{x:.1f}%"),
        textposition="outside",
        hovertemplate="<b>%{x}</b><br>Margin: %{y:.1f}%<extra></extra>"
    ))

    apply_enterprise_theme(fig, "Operating Profit Margin % by Region")
    fig.update_yaxes(title="Margin %")
    return fig

def plot_top_entities(df, entity_col, top_n=10, metric="Profit", title=None):
    """Horizontal bar chart for top entities."""
    if df.empty or entity_col not in df.columns:
        return go.Figure()

    top_df = df.groupby(entity_col).agg(
        Revenue=("Revenue", "sum"),
        Profit=("Profit", "sum")
    ).reset_index().nlargest(top_n, metric).sort_values(metric, ascending=True)

    colors = [EMERALD if p > 0 else RED_LOSS for p in top_df[metric]]

    fig = go.Figure(go.Bar(
        y=top_df[entity_col],
        x=top_df[metric],
        orientation="h",
        marker_color=colors,
        text=top_df[metric].apply(lambda x: format_currency(x)),
        textposition="outside",
        hovertemplate=f"<b>%{{y}}</b><br>{metric}: $%{{x:,.0f}}<extra></extra>"
    ))

    chart_title = title if title else f"Top {top_n} {entity_col}s by {metric}"
    apply_enterprise_theme(fig, chart_title)
    fig.update_xaxes(title=metric)
    return fig

def plot_discount_vs_profit_scatter(df):
    """Scatter plot of Discount Rate vs Net Profit."""
    if df.empty or "Discount Rate" not in df.columns:
        return go.Figure()

    sample = df.sample(min(500, len(df)), random_state=42) if len(df) > 500 else df
    colors = [EMERALD if p >= 0 else RED_LOSS for p in sample["Profit"]]

    fig = go.Figure(go.Scatter(
        x=sample["Discount Rate"] * 100,
        y=sample["Profit"],
        mode="markers",
        marker=dict(size=8, color=colors, opacity=0.7, line=dict(width=1, color="#ffffff")),
        text=sample["Customer"] if "Customer" in sample.columns else None,
        customdata=np.stack((sample["Revenue"], sample["Category"]), axis=-1) if "Category" in sample.columns else None,
        hovertemplate="<b>Customer: %{text}</b><br>Discount: %{x:.1f}%<br>Profit: $%{y:,.0f}<br>Revenue: $%{customdata[0]:,.0f}<br>Category: %{customdata[1]}<extra></extra>"
    ))

    apply_enterprise_theme(fig, "Transaction Discount Rate vs Net Profit ($)")
    fig.add_hline(y=0, line_dash="dash", line_color="#94a3b8", line_width=1.5)
    fig.update_xaxes(title="Discount Rate (%)")
    fig.update_yaxes(title="Net Profit ($)")
    return fig

# -------------------------------------------------------------
# 2. CUSTOMER INTELLIGENCE CHARTS (QUADRANT ANALYSIS)
# -------------------------------------------------------------

def plot_customer_quadrants(cust_df, median_rev, median_profit):
    """
    Four-Quadrant Customer Scatter Plot:
    X: Revenue, Y: Profit.
    Clearly identifies High Revenue / Low Profit Margin Traps.
    """
    if cust_df.empty:
        return go.Figure()

    color_map = {
        "High Value": EMERALD,
        "Growth Opportunity": BLUE_PRIMARY,
        "At Risk (Margin Trap)": AMBER_WARN,
        "Low Value": "#94a3b8",
        "Loss Making": RED_LOSS
    }

    fig = go.Figure()

    for segment, color in color_map.items():
        sub = cust_df[cust_df["Value Segment"] == segment]
        if not sub.empty:
            fig.add_trace(go.Scatter(
                x=sub["Revenue"],
                y=sub["Profit"],
                mode="markers+text",
                name=segment,
                marker=dict(size=12, color=color, opacity=0.85, line=dict(width=1.5, color="#ffffff")),
                text=sub["Customer"],
                textposition="top center",
                textfont=dict(size=9, color=NAVY),
                customdata=np.stack((sub["Profit Margin %"], sub["Orders"], sub["Discount"]), axis=-1),
                hovertemplate="<b>%{text}</b><br>Segment: " + segment + "<br>Revenue: $%{x:,.0f}<br>Profit: $%{y:,.0f}<br>Margin: %{customdata[0]:.1f}%<br>Orders: %{customdata[1]}<br>Total Discount: $%{customdata[2]:,.0f}<extra></extra>"
            ))

    # Median Quadrant Threshold Lines
    fig.add_vline(x=median_rev, line_dash="dash", line_color="#cbd5e1", line_width=1.5)
    fig.add_hline(y=median_profit, line_dash="dash", line_color="#cbd5e1", line_width=1.5)

    # Quadrant Labels
    max_rev = cust_df["Revenue"].max() * 1.05
    max_prof = cust_df["Profit"].max() * 1.05
    min_prof = cust_df["Profit"].min() * 1.05

    fig.add_annotation(x=max_rev*0.8, y=max_prof*0.9, text="⭐ HIGH REVENUE / HIGH PROFIT<br><b>(STARS)</b>", showarrow=False, font=dict(color=EMERALD, size=10, weight="bold"), align="center", bgcolor="rgba(255,255,255,0.8)")
    fig.add_annotation(x=max_rev*0.8, y=min_prof*0.8, text="⚠️ HIGH REVENUE / LOW PROFIT<br><b>(MARGIN TRAPS)</b>", showarrow=False, font=dict(color="#b45309", size=10, weight="bold"), align="center", bgcolor="rgba(255,255,255,0.8)")
    fig.add_annotation(x=median_rev*0.3, y=max_prof*0.9, text="💎 LOW REVENUE / HIGH PROFIT<br><b>(NICHE GEMS)</b>", showarrow=False, font=dict(color=BLUE_PRIMARY, size=10, weight="bold"), align="center", bgcolor="rgba(255,255,255,0.8)")
    fig.add_annotation(x=median_rev*0.3, y=min_prof*0.8, text="🛑 LOW REVENUE / LOW PROFIT<br><b>(LAGGARDS)</b>", showarrow=False, font=dict(color=RED_LOSS, size=10, weight="bold"), align="center", bgcolor="rgba(255,255,255,0.8)")

    apply_enterprise_theme(fig, "Customer Profitability Quadrant Matrix")
    fig.update_layout(legend=dict(orientation="h", yanchor="bottom", y=-0.25, xanchor="center", x=0.5))
    fig.update_xaxes(title="Customer Total Revenue ($)")
    fig.update_yaxes(title="Customer Total Net Profit ($)")
    return fig

# -------------------------------------------------------------
# 3. PRODUCT INTELLIGENCE CHARTS
# -------------------------------------------------------------

def plot_product_margins_diverging(prod_df):
    """Diverging bar chart showing positive vs negative margin products."""
    if prod_df.empty:
        return go.Figure()

    df_sorted = prod_df.sort_values("Profit Margin %", ascending=True)
    colors = [EMERALD if m >= 0 else RED_LOSS for m in df_sorted["Profit Margin %"]]

    fig = go.Figure(go.Bar(
        y=df_sorted["Product"],
        x=df_sorted["Profit Margin %"],
        orientation="h",
        marker_color=colors,
        text=df_sorted["Profit Margin %"].apply(lambda x: f"{x:.1f}%"),
        textposition="outside",
        customdata=np.stack((df_sorted["Revenue"], df_sorted["Profit"], df_sorted["Category"]), axis=-1),
        hovertemplate="<b>%{y}</b> (%{customdata[2]})<br>Margin: %{x:.1f}%<br>Revenue: $%{customdata[0]:,.0f}<br>Profit: $%{customdata[1]:,.0f}<extra></extra>"
    ))

    apply_enterprise_theme(fig, "Product Margin Realization (%) — Profitable vs Loss-Making")
    fig.update_layout(height=max(400, len(df_sorted) * 26))
    fig.update_xaxes(title="Profit Margin %", zerolinecolor="#475569", zerolinewidth=1.5)
    return fig

def plot_discount_vs_product_margin(prod_df):
    """Scatter of Avg Discount % vs Realized Product Margin %."""
    if prod_df.empty or "Avg_Discount_Rate" not in prod_df.columns:
        return go.Figure()

    fig = px.scatter(
        prod_df,
        x=prod_df["Avg_Discount_Rate"] * 100,
        y="Profit Margin %",
        size="Revenue",
        color="Category",
        hover_name="Product",
        title="Product Discount Rate vs Realized Margin (Bubble Size = Revenue)",
        labels={"x": "Average Discount Rate (%)", "Profit Margin %": "Realized Margin %"},
        color_discrete_sequence=[BLUE_PRIMARY, EMERALD, PURPLE, AMBER_WARN]
    )
    apply_enterprise_theme(fig, "Product Discount Rate vs Realized Margin (Bubble Size = Revenue)")
    fig.add_hline(y=0, line_dash="dash", line_color=RED_LOSS)
    return fig

# -------------------------------------------------------------
# 4. DISCOUNT INTELLIGENCE CHARTS
# -------------------------------------------------------------

def plot_discount_tier_margin_realization(tier_df):
    """Bar chart of realized margin across discount tiers."""
    if tier_df.empty:
        return go.Figure()

    fig = go.Figure()
    fig.add_trace(go.Bar(
        x=tier_df["Discount Tier"],
        y=tier_df["Realized Margin %"],
        name="Realized Margin %",
        marker_color=[EMERALD if m > 20 else (AMBER_WARN if m > 5 else RED_LOSS) for m in tier_df["Realized Margin %"]],
        text=tier_df["Realized Margin %"].apply(lambda x: f"{x:.1f}%"),
        textposition="outside",
        hovertemplate="<b>%{x}</b><br>Realized Margin: %{y:.1f}%<br>Total Revenue: $%{customdata:,.0f}<extra></extra>",
        customdata=tier_df["Total_Revenue"]
    ))

    apply_enterprise_theme(fig, "Margin Realization (%) by Discount Tier Bracket")
    fig.update_yaxes(title="Realized Margin %")
    return fig

# -------------------------------------------------------------
# 5. MARKET & CATEGORY CHARTS
# -------------------------------------------------------------

def plot_market_matrix(reg_df):
    """Scatter matrix of Revenue Share % vs Profit Share % by Region."""
    if reg_df.empty:
        return go.Figure()

    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=reg_df["Revenue Share %"],
        y=reg_df["Profit Share %"],
        mode="markers+text",
        text=reg_df["Region"],
        textposition="top center",
        marker=dict(size=reg_df["Revenue"] / reg_df["Revenue"].max() * 35 + 10, color=BLUE_PRIMARY, opacity=0.8),
        customdata=np.stack((reg_df["Revenue"], reg_df["Profit"], reg_df["Profit Margin %"]), axis=-1),
        hovertemplate="<b>%{text}</b><br>Revenue Share: %{x:.1f}%<br>Profit Share: %{y:.1f}%<br>Total Revenue: $%{customdata[0]:,.0f}<br>Total Profit: $%{customdata[1]:,.0f}<br>Margin: %{customdata[2]:.1f}%<extra></extra>"
    ))

    max_val = max(reg_df["Revenue Share %"].max(), reg_df["Profit Share %"].max()) * 1.15
    fig.add_trace(go.Scatter(
        x=[0, max_val], y=[0, max_val],
        mode="lines",
        line=dict(color="#cbd5e1", dash="dash"),
        name="Parity Line (Rev Share = Profit Share)",
        showlegend=True
    ))

    apply_enterprise_theme(fig, "Market Value Diagnostic: Revenue Share vs Profit Share")
    fig.update_layout(legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1))
    fig.update_xaxes(title="Revenue Share (%)")
    fig.update_yaxes(title="Profit Share (%)")
    return fig

def plot_region_category_heatmap_chart(heatmap_df):
    """Heatmap visualization of Profit Margin % across Region x Category."""
    if heatmap_df.empty:
        return go.Figure()

    fig = go.Figure(data=go.Heatmap(
        z=heatmap_df.values,
        x=heatmap_df.columns.tolist(),
        y=heatmap_df.index.tolist(),
        colorscale="Blues",
        text=np.vectorize(lambda x: f"{x:.1f}%")(heatmap_df.values),
        texttemplate="%{text}",
        textfont={"size": 11, "family": "Plus Jakarta Sans"},
        colorbar=dict(title="Margin %"),
        hovertemplate="<b>Region: %{y}</b><br>Category: %{x}<br>Margin: %{z:.1f}%<extra></extra>"
    ))

    apply_enterprise_theme(fig, "Profit Margin % Matrix (Region × Category)")
    fig.update_xaxes(title="Category")
    fig.update_yaxes(title="Region")
    return fig
