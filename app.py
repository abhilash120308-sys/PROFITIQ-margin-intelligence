"""
PROFITIQ: Profitability & Margin Intelligence Platform
"Turn Revenue Data into Profit Decisions."

Main Application Entry Point
"""

import datetime
import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go

# Page configuration
st.set_page_config(
    page_title="PROFITIQ | Margin Intelligence",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Core imports
from src.utils import (
    format_currency, format_percent, format_number, safe_divide,
    get_enterprise_css, render_metric_card, render_alert, render_insight_card,
    clean_html, export_df_to_excel, export_df_to_csv
)
from src.data_loader import (
    load_data_from_file, load_sample_dataset, detect_column_mappings
)
from src.data_cleaner import standardize_and_clean_data
from src.metrics import (
    calculate_executive_kpis, calculate_profitability_health_score, generate_automated_alerts
)
from src.customer_analysis import (
    get_customer_summary_table, get_customer_deep_dive
)
from src.product_analysis import (
    get_product_summary_table, get_product_leaderboards, generate_product_observations
)
from src.discount_analysis import (
    get_discount_metrics, get_discount_tier_analysis, get_margin_erosion_alerts
)
from src.market_analysis import (
    get_region_summary_table, get_category_summary_table,
    get_market_diagnostics, get_region_category_heatmap
)
from src.insight_engine import (
    generate_executive_insights, generate_comprehensive_business_findings
)
from src.recommendation_engine import generate_strategic_recommendations
from src.visualizations import (
    plot_revenue_profit_trend, plot_revenue_profit_by_category, plot_margin_by_region,
    plot_top_entities, plot_discount_vs_profit_scatter, plot_customer_quadrants,
    plot_product_margins_diverging, plot_discount_vs_product_margin,
    plot_discount_tier_margin_realization, plot_market_matrix,
    plot_region_category_heatmap_chart
)
from src.ai_assistant import answer_analytical_query

# Inject enterprise stylesheet
st.markdown(get_enterprise_css(), unsafe_allow_html=True)

# -------------------------------------------------------------
# SESSION STATE INITIALIZATION
# -------------------------------------------------------------
if "current_page" not in st.session_state:
    st.session_state["current_page"] = "Executive Overview"

if "raw_df" not in st.session_state:
    sample_df, source_label = load_sample_dataset()
    st.session_state["raw_df"] = sample_df
    st.session_state["source_label"] = "DEMO DATA"
    st.session_state["last_loaded"] = datetime.datetime.now().strftime("%H:%M")

if "filter_customers" not in st.session_state:
    st.session_state["filter_customers"] = []
if "filter_categories" not in st.session_state:
    st.session_state["filter_categories"] = []
if "filter_regions" not in st.session_state:
    st.session_state["filter_regions"] = []
if "filter_products" not in st.session_state:
    st.session_state["filter_products"] = []
if "chat_history" not in st.session_state:
    st.session_state["chat_history"] = []

# -------------------------------------------------------------
# SIDEBAR CONTROLS & STATEFUL BUTTON NAVIGATION (ZERO RADIO BUTTONS)
# -------------------------------------------------------------
with st.sidebar:
    # 1. Branding Header
    brand_side_html = clean_html("""
    <div class="sidebar-brand-container">
        <div class="sidebar-brand-top">
            <div class="sidebar-brand-logo">PQ</div>
            <div>
                <div class="sidebar-brand-title">PROFITIQ</div>
                <div class="sidebar-brand-tag">MARGIN INTELLIGENCE</div>
            </div>
        </div>
        <div class="sidebar-badge-pill">👑 ENTERPRISE EDITION</div>
    </div>
    """)
    st.markdown(brand_side_html, unsafe_allow_html=True)

    # 2. Navigation Section (Buttons with Active State)
    st.markdown('<div class="sidebar-section-title">🧭 NAVIGATION</div>', unsafe_allow_html=True)

    nav_items = [
        ("Executive Overview", "🏠 Executive Overview"),
        ("Customer Intelligence", "👥 Customer Intelligence"),
        ("Product Intelligence", "📦 Product Intelligence"),
        ("Discount Intelligence", "% Discount Intelligence"),
        ("Market & Category Analysis", "🌐 Market & Category Analysis"),
        ("Business Insights", "💡 Business Insights"),
        ("Data Explorer & Export", "🗄️ Data Explorer & Export")
    ]

    for page_key, display_label in nav_items:
        is_active = (st.session_state["current_page"] == page_key)
        # Format label with right arrow
        btn_text = f"{display_label}  ›" if is_active else f"{display_label}  ›"
        if st.button(
            btn_text,
            key=f"nav_btn_{page_key.replace(' ', '_')}",
            type="primary" if is_active else "secondary",
            use_container_width=True
        ):
            if st.session_state["current_page"] != page_key:
                st.session_state["current_page"] = page_key
                st.rerun()

    st.markdown("<hr style='margin: 14px 0; border: none; border-top: 1px solid #e2e8f0;'>", unsafe_allow_html=True)

    # 3. Data Ingestion Section
    st.markdown('<div class="sidebar-section-title">📊 DATA INGESTION</div>', unsafe_allow_html=True)
    st.markdown('<div class="sidebar-section-sub">Load your sales and order data to get insights.</div>', unsafe_allow_html=True)

    uploaded_file = st.file_uploader(
        "Upload Dataset (.csv, .xlsx)",
        type=["csv", "xlsx", "xls"],
        help="Upload CSV or Excel transactions ledger"
    )
    if uploaded_file is not None:
        raw_df, err = load_data_from_file(uploaded_file, uploaded_file.name)
        if err:
            st.error(f"Upload failed: {err}")
        else:
            st.session_state["raw_df"] = raw_df
            st.session_state["source_label"] = uploaded_file.name
            st.session_state["last_loaded"] = datetime.datetime.now().strftime("%H:%M")
            st.success(f"✓ Loaded {len(raw_df):,} rows")

    st.markdown("<div style='text-align: center; color: #94a3b8; font-size: 11px; margin: 6px 0;'>──────── OR ────────</div>", unsafe_allow_html=True)

    if st.button("📄 Use Sample Benchmark Dataset", use_container_width=True, help="Load benchmark enterprise dataset"):
        sample_df, source_label = load_sample_dataset()
        st.session_state["raw_df"] = sample_df
        st.session_state["source_label"] = "DEMO DATA"
        st.session_state["last_loaded"] = datetime.datetime.now().strftime("%H:%M")
        st.rerun()

    if st.button("↻ Reset to Demo Data", use_container_width=True, help="Reset to original demo data"):
        sample_df, source_label = load_sample_dataset()
        st.session_state["raw_df"] = sample_df
        st.session_state["source_label"] = "DEMO DATA"
        st.session_state["last_loaded"] = datetime.datetime.now().strftime("%H:%M")
        st.session_state["filter_customers"] = []
        st.session_state["filter_categories"] = []
        st.session_state["filter_regions"] = []
        st.session_state["filter_products"] = []
        st.rerun()

    # 4. Data Status Card
    status_card_html = clean_html(f"""
    <div class="sidebar-status-card">
        <div class="sidebar-status-indicator">
            <span class="sidebar-status-dot"></span>
            <span>● Data Loaded Successfully</span>
        </div>
        <div class="sidebar-status-row">
            <span>Active Source:</span>
            <span class="sidebar-status-val">{st.session_state.get('source_label', 'DEMO DATA')}</span>
        </div>
        <div class="sidebar-status-row">
            <span>Total Raw Records:</span>
            <span class="sidebar-status-val">{len(st.session_state['raw_df']):,}</span>
        </div>
        <div class="sidebar-status-row">
            <span>Last Loaded:</span>
            <span class="sidebar-status-val">Today, {st.session_state.get('last_loaded', '19:40')}</span>
        </div>
    </div>
    """)
    st.markdown(status_card_html, unsafe_allow_html=True)

    st.markdown("<hr style='margin: 14px 0; border: none; border-top: 1px solid #e2e8f0;'>", unsafe_allow_html=True)

# -------------------------------------------------------------
# DATA VALIDATION & STANDARDIZATION PIPELINE
# -------------------------------------------------------------
raw_df = st.session_state["raw_df"]
mapping, missing_critical = detect_column_mappings(raw_df.columns)

if missing_critical:
    st.error("### ⚠️ Dataset Incomplete — Missing Critical Financial Columns")
    st.markdown(f"""
    PROFITIQ requires essential financial fields to run margin diagnostics.
    
    **Missing Required Columns:**
    - {", ".join(missing_critical)}
    
    **Detected Columns in your file:**
    - `{", ".join(raw_df.columns)}`
    
    *Please upload a dataset containing Revenue/Sales, Cost/COGS (or Profit), Customer, and Product.*
    """)
    st.stop()

# Clean & standardize
clean_df, quality_info = standardize_and_clean_data(raw_df, mapping)

# -------------------------------------------------------------
# GLOBAL FILTERS (SIDEBAR)
# -------------------------------------------------------------
with st.sidebar:
    st.markdown('<div class="sidebar-section-title">🔎 GLOBAL FILTERS</div>', unsafe_allow_html=True)

    with st.expander("Filter Controls", expanded=True):
        # Date Filter
        if "Order Date" in clean_df.columns and not clean_df["Order Date"].isna().all():
            min_date = clean_df["Order Date"].min().date()
            max_date = clean_df["Order Date"].max().date()
            if min_date < max_date:
                date_range = st.date_input(
                    "📅 Date Range",
                    value=(min_date, max_date),
                    min_value=min_date,
                    max_value=max_date
                )
            else:
                date_range = (min_date, max_date)
        else:
            date_range = None

        # Customer Filter
        all_customers = sorted(clean_df["Customer"].unique())
        selected_customers = st.multiselect(
            "👥 Customer",
            all_customers,
            default=st.session_state.get("filter_customers", []),
            key="sb_cust"
        )

        # Product Filter
        all_products = sorted(clean_df["Product"].unique())
        selected_products = st.multiselect(
            "📦 Product",
            all_products,
            default=st.session_state.get("filter_products", []),
            key="sb_prod"
        )

        # Category Filter
        all_categories = sorted(clean_df["Category"].unique())
        selected_categories = st.multiselect(
            "🏷️ Category",
            all_categories,
            default=st.session_state.get("filter_categories", []),
            key="sb_cat"
        )

        # Region Filter
        all_regions = sorted(clean_df["Region"].unique())
        selected_regions = st.multiselect(
            "🌐 Region / Market",
            all_regions,
            default=st.session_state.get("filter_regions", []),
            key="sb_reg"
        )

    # Filter Action Buttons
    fb_col1, fb_col2 = st.columns(2)
    with fb_col1:
        if st.button("🔎 APPLY FILTERS", use_container_width=True, type="primary"):
            st.session_state["filter_customers"] = selected_customers
            st.session_state["filter_products"] = selected_products
            st.session_state["filter_categories"] = selected_categories
            st.session_state["filter_regions"] = selected_regions
            st.rerun()
    with fb_col2:
        if st.button("↻ CLEAR ALL", use_container_width=True):
            st.session_state["filter_customers"] = []
            st.session_state["filter_products"] = []
            st.session_state["filter_categories"] = []
            st.session_state["filter_regions"] = []
            st.rerun()

# Apply filters
filtered_df = clean_df.copy()

if date_range and len(date_range) == 2:
    start_d, end_d = date_range
    filtered_df = filtered_df[
        (filtered_df["Order Date"].dt.date >= start_d) &
        (filtered_df["Order Date"].dt.date <= end_d)
    ]

if selected_customers:
    filtered_df = filtered_df[filtered_df["Customer"].isin(selected_customers)]

if selected_categories:
    filtered_df = filtered_df[filtered_df["Category"].isin(selected_categories)]

if selected_regions:
    filtered_df = filtered_df[filtered_df["Region"].isin(selected_regions)]

if selected_products:
    filtered_df = filtered_df[filtered_df["Product"].isin(selected_products)]

if filtered_df.empty:
    st.warning("⚠️ No records match the selected filter combination. Please broaden your filter criteria in the sidebar.")
    st.stop()

# -------------------------------------------------------------
# TOP EXECUTIVE BRAND HEADER
# -------------------------------------------------------------
header_html = clean_html(f"""
<div class="brand-header-box">
    <div>
        <div class="brand-title">
            <span>PROFITIQ</span>
            <span class="brand-badge">Enterprise Edition</span>
        </div>
        <div class="brand-subtitle">Profitability & Margin Intelligence Platform &nbsp;•&nbsp; <i>"Turn Revenue Data into Profit Decisions."</i></div>
    </div>
    <div style="text-align: right; color: #cbd5e1; font-size: 12px;">
        <span style="background: rgba(255,255,255,0.1); padding: 6px 12px; border-radius: 8px; border-1px solid rgba(255,255,255,0.15);">
            📊 <b>{len(filtered_df):,}</b> Filtered Records &nbsp;|&nbsp; 🏢 <b>{filtered_df['Customer'].nunique()}</b> Accounts
        </span>
    </div>
</div>
""")
st.markdown(header_html, unsafe_allow_html=True)

# Compute core executive metrics
kpis = calculate_executive_kpis(filtered_df)
health_score, health_breakdown, health_status = calculate_profitability_health_score(filtered_df)
alerts = generate_automated_alerts(filtered_df)

current_page = st.session_state.get("current_page", "Executive Overview")

# =============================================================
# PAGE 1: EXECUTIVE OVERVIEW
# =============================================================
if current_page == "Executive Overview":
    st.markdown('<div class="section-header">📊 Executive Financial Summary</div>', unsafe_allow_html=True)

    # 7 Primary KPI Cards
    col1, col2, col3, col4, col5, col6, col7 = st.columns(7)
    with col1:
        rev_delta = kpis["deltas"].get("revenue", None)
        st.markdown(render_metric_card("Total Revenue", format_currency(kpis["total_revenue"]), delta=rev_delta, delta_type="positive" if rev_delta and "+" in rev_delta else "neutral", sublabel="Gross Invoiced", icon="💵"), unsafe_allow_html=True)
    with col2:
        st.markdown(render_metric_card("Total Cost", format_currency(kpis["total_cost"]), sublabel="Direct COGS", icon="📦"), unsafe_allow_html=True)
    with col3:
        prof_delta = kpis["deltas"].get("profit", None)
        prof_type = "positive" if kpis["total_profit"] > 0 else "negative"
        st.markdown(render_metric_card("Total Profit", format_currency(kpis["total_profit"]), delta=prof_delta, delta_type=prof_type, sublabel="Operating Profit", icon="📈"), unsafe_allow_html=True)
    with col4:
        margin_delta = kpis["deltas"].get("margin", None)
        margin_type = "positive" if kpis["profit_margin_pct"] >= 20 else ("negative" if kpis["profit_margin_pct"] < 10 else "neutral")
        st.markdown(render_metric_card("Profit Margin", format_percent(kpis["profit_margin_pct"]), delta=margin_delta, delta_type=margin_type, sublabel="Realized Margin %", icon="🎯"), unsafe_allow_html=True)
    with col5:
        st.markdown(render_metric_card("Total Discount", format_currency(kpis["total_discount"]), sublabel=f"{safe_divide(kpis['total_discount'], kpis['total_revenue'])*100:.1f}% of Rev", icon="🏷️"), unsafe_allow_html=True)
    with col6:
        st.markdown(render_metric_card("Total Orders", format_number(kpis["order_count"]), sublabel=f"Avg {format_currency(kpis['avg_order_value'])}/ord", icon="🛒"), unsafe_allow_html=True)
    with col7:
        st.markdown(render_metric_card("Active Clients", format_number(kpis["customer_count"]), sublabel=f"Avg {format_currency(safe_divide(kpis['total_profit'], kpis['customer_count']))}/cli", icon="🏢"), unsafe_allow_html=True)

    # Health Score & Executive Alerts Section
    st.markdown("<div style='margin-top: 15px;'></div>", unsafe_allow_html=True)
    h_col1, h_col2 = st.columns([1.2, 2.8])

    with h_col1:
        health_box_html = clean_html(f"""
        <div class="health-score-container">
            <div style="display: flex; justify-content: space-between; align-items: center;">
                <span style="font-weight: 700; font-size: 13.5px; color: #0f172a;">PROFITABILITY HEALTH</span>
                <span style="background: {health_breakdown.get('status_color', '#2563eb')}; color: white; padding: 2px 8px; border-radius: 12px; font-size: 11px; font-weight: 700;">{health_status.upper()}</span>
            </div>
            <div style="font-size: 32px; font-weight: 800; color: #0f172a; margin-top: 6px;">{health_score}<span style="font-size: 18px; color: #94a3b8;">/100</span></div>
            <div class="health-score-bar-bg">
                <div class="health-score-bar-fill" style="width: {health_score}%; background: {health_breakdown.get('status_color', '#2563eb')};"></div>
            </div>
            <div style="font-size: 11.5px; color: #64748b; line-height: 1.5; margin-top: 8px;">
                • Margin Target: <b>{health_breakdown['overall_margin_pts'][0]}/{health_breakdown['overall_margin_pts'][1]} pts</b><br>
                • Profitable Accounts ({health_breakdown['prof_cust_pct']}%): <b>{health_breakdown['customer_breadth_pts'][0]}/{health_breakdown['customer_breadth_pts'][1]} pts</b><br>
                • Profitable Products ({health_breakdown['prof_prod_pct']}%): <b>{health_breakdown['product_breadth_pts'][0]}/{health_breakdown['product_breadth_pts'][1]} pts</b><br>
                • Discount Discipline (Avg {health_breakdown['avg_discount_pct']}%): <b>{health_breakdown['discount_discipline_pts'][0]}/{health_breakdown['discount_discipline_pts'][1]} pts</b>
            </div>
        </div>
        """)
        st.markdown(health_box_html, unsafe_allow_html=True)

    with h_col2:
        alerts_header_html = clean_html("""
        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px;">
            <span style="font-weight: 700; font-size: 14px; color: #0f172a;">⚡ AUTOMATED VALUE & RISK ALERTS</span>
            <span style="font-size: 12px; color: #64748b;">Real-time trigger diagnostics</span>
        </div>
        """)
        st.markdown(alerts_header_html, unsafe_allow_html=True)
        if alerts:
            for alert in alerts[:3]:
                st.markdown(render_alert(alert["type"], alert["title"], alert["description"]), unsafe_allow_html=True)
        else:
            st.success("✓ All accounts and product lines operating above minimum profitability thresholds.")

    # Executive Insights Strip (3 dynamic takeaways)
    st.markdown('<div class="section-header">💡 Automated Executive Insights</div>', unsafe_allow_html=True)
    overview_insights = generate_executive_insights(filtered_df)
    
    ins_cols = st.columns(len(overview_insights[:3]))
    for i, ins_text in enumerate(overview_insights[:3]):
        with ins_cols[i]:
            parts = ins_text.split(":", 1)
            title = parts[0] if len(parts) > 1 else "Key Takeaway"
            desc = parts[1] if len(parts) > 1 else ins_text
            st.markdown(render_insight_card(title, desc), unsafe_allow_html=True)

    # 6 Interactive Executive Charts
    st.markdown('<div class="section-header">📈 Core Profitability Diagnostics</div>', unsafe_allow_html=True)

    c_row1_col1, c_row1_col2 = st.columns(2)
    with c_row1_col1:
        st.plotly_chart(plot_revenue_profit_trend(filtered_df), use_container_width=True)
    with c_row1_col2:
        st.plotly_chart(plot_revenue_profit_by_category(filtered_df), use_container_width=True)

    c_row2_col1, c_row2_col2 = st.columns(2)
    with c_row2_col1:
        st.plotly_chart(plot_margin_by_region(filtered_df), use_container_width=True)
    with c_row2_col2:
        st.plotly_chart(plot_discount_vs_profit_scatter(filtered_df), use_container_width=True)

    c_row3_col1, c_row3_col2 = st.columns(2)
    with c_row3_col1:
        st.plotly_chart(plot_top_entities(filtered_df, "Customer", top_n=8, metric="Profit", title="Top 8 Profitable Customers"), use_container_width=True)
    with c_row3_col2:
        st.plotly_chart(plot_top_entities(filtered_df, "Product", top_n=8, metric="Profit", title="Top 8 Profitable Products"), use_container_width=True)

# =============================================================
# PAGE 2: CUSTOMER INTELLIGENCE
# =============================================================
elif current_page == "Customer Intelligence":
    st.markdown('<div class="section-header">👥 Customer Profitability & Quadrant Intelligence</div>', unsafe_allow_html=True)

    cust_table, med_rev, med_profit = get_customer_summary_table(filtered_df)

    # Customer Summary Metrics
    c_m1, c_m2, c_m3, c_m4 = st.columns(4)
    with c_m1:
        st.markdown(render_metric_card("Total Accounts", format_number(len(cust_table)), sublabel="Active in selection", icon="🏢"), unsafe_allow_html=True)
    with c_m2:
        st.markdown(render_metric_card("Avg Customer Revenue", format_currency(cust_table['Revenue'].mean()), sublabel=f"Median: {format_currency(med_rev)}", icon="💵"), unsafe_allow_html=True)
    with c_m3:
        st.markdown(render_metric_card("Avg Customer Profit", format_currency(cust_table['Profit'].mean()), sublabel=f"Median: {format_currency(med_profit)}", icon="📈"), unsafe_allow_html=True)
    with c_m4:
        avg_cust_margin = safe_divide(cust_table['Profit'].sum(), cust_table['Revenue'].sum()) * 100
        st.markdown(render_metric_card("Avg Customer Margin", format_percent(avg_cust_margin), sublabel=f"{(cust_table['Profit'] > 0).sum()} profitable accounts", icon="🎯"), unsafe_allow_html=True)

    st.markdown("<div style='margin-top: 15px;'></div>", unsafe_allow_html=True)

    # Customer Quadrant Chart
    st.plotly_chart(plot_customer_quadrants(cust_table, med_rev, med_profit), use_container_width=True)

    rule_note_html = clean_html("""
    <div style="background: #f8fafc; border-left: 4px solid #f59e0b; padding: 12px 16px; border-radius: 0 8px 8px 0; margin-bottom: 20px; font-size: 13px; color: #334155;">
        <b>⚠️ Quadrant Diagnostic Rule:</b> Accounts in the lower-right quadrant (<b>High Revenue / Low Profit</b>) generate high sales volume but erode margins through excessive discounting or heavy service costs. These represent top commercial renegotiation priorities.
    </div>
    """)
    st.markdown(rule_note_html, unsafe_allow_html=True)

    # Customer Table with Segment Filter
    st.markdown("### 📋 Customer Profitability Ledger")
    segment_filter = st.multiselect("Filter by Value Segment", options=sorted(cust_table["Value Segment"].unique()), default=[])
    
    display_cust_df = cust_table if not segment_filter else cust_table[cust_table["Value Segment"].isin(segment_filter)]

    formatted_table = display_cust_df.copy()
    formatted_table["Revenue"] = formatted_table["Revenue"].apply(format_currency)
    formatted_table["Cost"] = formatted_table["Cost"].apply(format_currency)
    formatted_table["Discount"] = formatted_table["Discount"].apply(format_currency)
    formatted_table["Profit"] = formatted_table["Profit"].apply(format_currency)
    formatted_table["Profit Margin %"] = formatted_table["Profit Margin %"].apply(lambda x: f"{x:.1f}%")
    formatted_table["Avg Order Value"] = formatted_table["Avg Order Value"].apply(format_currency)
    if "Avg_Discount_Rate" in formatted_table.columns:
        formatted_table["Avg Discount %"] = (formatted_table["Avg_Discount_Rate"] * 100).apply(lambda x: f"{x:.1f}%")
        formatted_table = formatted_table.drop(columns=["Avg_Discount_Rate"])

    st.dataframe(formatted_table, use_container_width=True, hide_index=True)

    # Customer Deep Dive Drilldown
    st.markdown("---")
    st.markdown("### 🔍 Customer Account Deep-Dive Diagnostic")
    selected_customer_name = st.selectbox("Select Customer to Inspect Root-Cause & Action Plan", options=sorted(cust_table["Customer"].unique()))
    
    if selected_customer_name:
        dive = get_customer_deep_dive(filtered_df, selected_customer_name)
        if dive:
            d_col1, d_col2 = st.columns([1.5, 2.5])
            with d_col1:
                dive_card_html = clean_html(f"""
                <div style="background: #ffffff; border: 1px solid #e2e8f0; border-radius: 12px; padding: 20px; box-shadow: 0 1px 3px rgba(0,0,0,0.05);">
                    <div style="font-size: 18px; font-weight: 800; color: #0f172a; margin-bottom: 4px;">{dive['customer']}</div>
                    <div style="margin-bottom: 12px;">{dive['status_badge']}</div>
                    <div style="font-size: 12.5px; color: #475569; line-height: 1.6;">
                        • <b>Total Revenue:</b> {format_currency(dive['revenue'])}<br>
                        • <b>Total Net Profit:</b> {format_currency(dive['profit'])}<br>
                        • <b>Profit Margin:</b> {dive['margin']:.1f}%<br>
                        • <b>Total Discount Received:</b> {format_currency(dive['discount'])}<br>
                        • <b>Average Discount Rate:</b> {dive['avg_discount_rate']:.1f}%<br>
                        • <b>Order Volume:</b> {dive['orders']} orders
                    </div>
                </div>
                """)
                st.markdown(dive_card_html, unsafe_allow_html=True)
                st.markdown("<div style='margin-top: 10px;'></div>", unsafe_allow_html=True)
                dive_action_html = clean_html(f"""
                <div class="insight-card" style="border-left-color: #2563eb;">
                    <div class="insight-title">🔬 Root-Cause Diagnostic</div>
                    <div class="insight-why">{dive['diagnosis']}</div>
                    <div class="insight-action">🚀 Action: {dive['recommended_action']}</div>
                </div>
                """)
                st.markdown(dive_action_html, unsafe_allow_html=True)

            with d_col2:
                if not dive["monthly_trend"].empty:
                    fig_trend = px.bar(dive["monthly_trend"], x="YearMonth", y=["Revenue", "Profit"], barmode="group",
                                       title=f"Monthly Revenue & Profit: {dive['customer']}",
                                       color_discrete_sequence=["#94a3b8", "#2563eb"])
                    fig_trend.update_layout(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", height=320)
                    st.plotly_chart(fig_trend, use_container_width=True)

# =============================================================
# PAGE 3: PRODUCT INTELLIGENCE
# =============================================================
elif current_page == "Product Intelligence":
    st.markdown('<div class="section-header">📦 Product Portfolio Profitability Diagnostics</div>', unsafe_allow_html=True)

    prod_table = get_product_summary_table(filtered_df)
    top_prof, worst_loss, high_marg, low_marg = get_product_leaderboards(prod_table, top_n=5)
    prod_obs = generate_product_observations(prod_table)

    # Product KPIs
    p_k1, p_k2, p_k3, p_k4 = st.columns(4)
    with p_k1:
        st.markdown(render_metric_card("Total Products", format_number(len(prod_table)), sublabel="Analyzed SKUs", icon="📦"), unsafe_allow_html=True)
    with p_k2:
        prof_pct = safe_divide((prod_table['Profit'] > 0).sum(), len(prod_table)) * 100
        st.markdown(render_metric_card("Profitable SKUs", f"{prof_pct:.1f}%", sublabel=f"{(prod_table['Profit'] > 0).sum()} of {len(prod_table)}", icon="✅"), unsafe_allow_html=True)
    with p_k3:
        loss_sku_count = (prod_table['Profit'] < 0).sum()
        st.markdown(render_metric_card("Loss-Making SKUs", format_number(loss_sku_count), delta_type="negative" if loss_sku_count > 0 else "positive", sublabel="Immediate review required", icon="🛑"), unsafe_allow_html=True)
    with p_k4:
        top_sku = prod_table.iloc[0]['Product'] if not prod_table.empty else "N/A"
        st.markdown(render_metric_card("Top Profit Driver", top_sku[:18] + "...", sublabel=format_currency(prod_table.iloc[0]['Profit']) if not prod_table.empty else "$0", icon="⭐"), unsafe_allow_html=True)

    # Automated Product Observations
    if prod_obs:
        st.markdown("<div style='margin-top: 15px;'></div>", unsafe_allow_html=True)
        obs_cols = st.columns(len(prod_obs))
        for i, obs in enumerate(prod_obs):
            with obs_cols[i]:
                alert_badge = "🔴 LOSS RISK" if obs["type"] == "loss" else ("🟠 MARGIN SQUEEZE" if obs["type"] == "margin" else "🟢 MARGIN LEADER")
                st.markdown(render_alert(obs["type"], alert_badge, obs["text"]), unsafe_allow_html=True)

    st.markdown("<div style='margin-top: 15px;'></div>", unsafe_allow_html=True)

    # Charts: Diverging Margins & Discount vs Margin
    p_c1, p_c2 = st.columns([1.2, 1.8])
    with p_c1:
        st.plotly_chart(plot_product_margins_diverging(prod_table), use_container_width=True)
    with p_c2:
        st.plotly_chart(plot_discount_vs_product_margin(prod_table), use_container_width=True)

    # Leaderboards vs Laggards
    st.markdown("### 🏆 Product Performance Polarities")
    l_col1, l_col2 = st.columns(2)
    with l_col1:
        st.markdown("#### ⭐ Top 5 Profitable Products")
        st.dataframe(
            top_prof[["Product", "Category", "Revenue", "Profit", "Profit Margin %"]].assign(
                Revenue=lambda x: x["Revenue"].apply(format_currency),
                Profit=lambda x: x["Profit"].apply(format_currency),
                **{"Profit Margin %": lambda x: x["Profit Margin %"].apply(lambda v: f"{v:.1f}%")}
            ),
            use_container_width=True, hide_index=True
        )
    with l_col2:
        st.markdown("#### 🛑 Worst 5 Loss-Making / Lowest Margin Products")
        st.dataframe(
            worst_loss[["Product", "Category", "Revenue", "Profit", "Profit Margin %"]].assign(
                Revenue=lambda x: x["Revenue"].apply(format_currency),
                Profit=lambda x: x["Profit"].apply(format_currency),
                **{"Profit Margin %": lambda x: x["Profit Margin %"].apply(lambda v: f"{v:.1f}%")}
            ),
            use_container_width=True, hide_index=True
        )

    # Complete Product Profitability Table
    st.markdown("### 📋 Complete SKU Profitability Ledger")
    formatted_prod = prod_table.copy()
    formatted_prod["Revenue"] = formatted_prod["Revenue"].apply(format_currency)
    formatted_prod["Cost"] = formatted_prod["Cost"].apply(format_currency)
    formatted_prod["Discount"] = formatted_prod["Discount"].apply(format_currency)
    formatted_prod["Profit"] = formatted_prod["Profit"].apply(format_currency)
    formatted_prod["Profit Margin %"] = formatted_prod["Profit Margin %"].apply(lambda x: f"{x:.1f}%")
    if "Avg_Discount_Rate" in formatted_prod.columns:
        formatted_prod["Avg Discount %"] = (formatted_prod["Avg_Discount_Rate"] * 100).apply(lambda x: f"{x:.1f}%")
        formatted_prod = formatted_prod.drop(columns=["Avg_Discount_Rate"])

    st.dataframe(formatted_prod, use_container_width=True, hide_index=True)

# =============================================================
# PAGE 4: DISCOUNT INTELLIGENCE
# =============================================================
elif current_page == "Discount Intelligence":
    st.markdown('<div class="section-header">🏷️ Discount Intelligence & Margin Erosion Diagnostics</div>', unsafe_allow_html=True)

    disc_metrics = get_discount_metrics(filtered_df)
    tier_df = get_discount_tier_analysis(filtered_df)
    erosion_alerts = get_margin_erosion_alerts(filtered_df)

    # Discount KPI Cards
    d_k1, d_k2, d_k3, d_k4 = st.columns(4)
    with d_k1:
        st.markdown(render_metric_card("Total Discount Given", format_currency(disc_metrics["total_discount"]), sublabel="Cumulative reductions", icon="🏷️"), unsafe_allow_html=True)
    with d_k2:
        st.markdown(render_metric_card("Average Discount Rate", f"{disc_metrics['avg_discount_rate']:.1f}%", sublabel="Across all orders", icon="📉"), unsafe_allow_html=True)
    with d_k3:
        st.markdown(render_metric_card("Discount % of Revenue", f"{disc_metrics['discount_to_revenue_pct']:.1f}%", sublabel="Relative to invoiced", icon="⚖️"), unsafe_allow_html=True)
    with d_k4:
        st.markdown(render_metric_card("Discount Loss Impact", format_currency(disc_metrics["loss_making_discount_val"]), delta_type="negative", sublabel=f"{disc_metrics['loss_making_discount_orders']} loss orders", icon="🛑"), unsafe_allow_html=True)

    st.markdown("<div style='margin-top: 15px;'></div>", unsafe_allow_html=True)

    # Margin Erosion Alerts
    st.markdown("### ⚠️ Margin Erosion Warnings (High Discount → Low Realized Margin)")
    if erosion_alerts:
        e_cols = st.columns(min(len(erosion_alerts), 3))
        for i, alert in enumerate(erosion_alerts[:3]):
            with e_cols[i]:
                st.markdown(render_alert(
                    "discount",
                    f"{alert['type']}: {alert['target']}",
                    f"{alert['explanation']} (Revenue: {format_currency(alert['revenue'])})"
                ), unsafe_allow_html=True)
    else:
        st.info("No acute discount margin erosion anomalies detected under current filters.")

    # Charts: Discount Tiers & Scatter Correlation
    st.markdown("<div style='margin-top: 15px;'></div>", unsafe_allow_html=True)
    d_c1, d_c2 = st.columns(2)
    with d_c1:
        st.plotly_chart(plot_discount_tier_margin_realization(tier_df), use_container_width=True)
    with d_c2:
        st.plotly_chart(plot_discount_vs_profit_scatter(filtered_df), use_container_width=True)

    # Discount Tier Breakdown Table
    st.markdown("### 📊 Margin Realization Across Discount Brackets")
    if not tier_df.empty:
        formatted_tier = tier_df.copy()
        formatted_tier["Total_Revenue"] = formatted_tier["Total_Revenue"].apply(format_currency)
        formatted_tier["Total_Cost"] = formatted_tier["Total_Cost"].apply(format_currency)
        formatted_tier["Total_Discount"] = formatted_tier["Total_Discount"].apply(format_currency)
        formatted_tier["Total_Profit"] = formatted_tier["Total_Profit"].apply(format_currency)
        formatted_tier["Realized Margin %"] = formatted_tier["Realized Margin %"].apply(lambda x: f"{x:.1f}%")
        formatted_tier["Avg_Margin"] = formatted_tier["Avg_Margin"].apply(lambda x: f"{x:.1f}%")
        formatted_tier["Revenue Share %"] = formatted_tier["Revenue Share %"].apply(lambda x: f"{x:.1f}%")
        st.dataframe(formatted_tier, use_container_width=True, hide_index=True)

# =============================================================
# PAGE 5: MARKET & CATEGORY ANALYSIS
# =============================================================
elif current_page == "Market & Category Analysis":
    st.markdown('<div class="section-header">🌍 Regional Market & Product Category Diagnostics</div>', unsafe_allow_html=True)

    reg_df = get_region_summary_table(filtered_df)
    cat_df = get_category_summary_table(filtered_df)
    market_diag = get_market_diagnostics(reg_df, cat_df)
    heatmap_df = get_region_category_heatmap(filtered_df)

    # Market Benchmark Diagnostic Cards
    m_k1, m_k2, m_k3, m_k4 = st.columns(4)
    with m_k1:
        st.markdown(render_metric_card("Top Profit Region", market_diag.get("top_profit_region", "N/A"), sublabel=format_currency(market_diag.get("top_profit_region_val", 0)), icon="🏆"), unsafe_allow_html=True)
    with m_k2:
        st.markdown(render_metric_card("Lowest Margin Region", market_diag.get("lowest_margin_region", "N/A"), sublabel=f"{market_diag.get('lowest_margin_region_val', 0):.1f}% margin", delta_type="negative", icon="⚠️"), unsafe_allow_html=True)
    with m_k3:
        st.markdown(render_metric_card("Top Margin Category", market_diag.get("highest_margin_cat", "N/A"), sublabel=f"{market_diag.get('highest_margin_cat_val', 0):.1f}% margin", icon="💎"), unsafe_allow_html=True)
    with m_k4:
        st.markdown(render_metric_card("Lowest Margin Category", market_diag.get("lowest_margin_cat", "N/A"), sublabel=f"{market_diag.get('lowest_margin_cat_val', 0):.1f}% margin", icon="📉"), unsafe_allow_html=True)

    st.markdown("<div style='margin-top: 15px;'></div>", unsafe_allow_html=True)

    # Regional & Category Charts
    m_c1, m_c2 = st.columns(2)
    with m_c1:
        st.plotly_chart(plot_market_matrix(reg_df), use_container_width=True)
    with m_c2:
        st.plotly_chart(plot_region_category_heatmap_chart(heatmap_df), use_container_width=True)

    # Regional & Category Comparison Tables
    st.markdown("### 📋 Segment Comparison Ledgers")
    t_c1, t_c2 = st.columns(2)
    with t_c1:
        st.markdown("#### 🌍 Market / Regional Profitability")
        if not reg_df.empty:
            f_reg = reg_df.copy()
            f_reg["Revenue"] = f_reg["Revenue"].apply(format_currency)
            f_reg["Profit"] = f_reg["Profit"].apply(format_currency)
            f_reg["Profit Margin %"] = f_reg["Profit Margin %"].apply(lambda x: f"{x:.1f}%")
            f_reg["Revenue Share %"] = f_reg["Revenue Share %"].apply(lambda x: f"{x:.1f}%")
            f_reg["Profit Share %"] = f_reg["Profit Share %"].apply(lambda x: f"{x:.1f}%")
            st.dataframe(f_reg[["Region", "Revenue", "Profit", "Profit Margin %", "Revenue Share %", "Profit Share %", "Profit-to-Revenue Ratio"]], use_container_width=True, hide_index=True)

    with t_c2:
        st.markdown("#### 📂 Product Category Profitability")
        if not cat_df.empty:
            f_cat = cat_df.copy()
            f_cat["Revenue"] = f_cat["Revenue"].apply(format_currency)
            f_cat["Profit"] = f_cat["Profit"].apply(format_currency)
            f_cat["Profit Margin %"] = f_cat["Profit Margin %"].apply(lambda x: f"{x:.1f}%")
            f_cat["Revenue Share %"] = f_cat["Revenue Share %"].apply(lambda x: f"{x:.1f}%")
            f_cat["Profit Share %"] = f_cat["Profit Share %"].apply(lambda x: f"{x:.1f}%")
            st.dataframe(f_cat[["Category", "Revenue", "Profit", "Profit Margin %", "Revenue Share %", "Profit Share %"]], use_container_width=True, hide_index=True)

# =============================================================
# PAGE 6: BUSINESS INSIGHTS & STRATEGIC RECOMMENDATIONS
# =============================================================
elif current_page == "Business Insights":
    st.markdown('<div class="section-header">🧠 Business Intelligence Center & Strategic Action Plan</div>', unsafe_allow_html=True)

    findings = generate_comprehensive_business_findings(filtered_df)
    recommendations = generate_strategic_recommendations(filtered_df)

    # 1. Executive Summary
    exec_summary_html = clean_html(f"""
    <div style="background: #ffffff; border: 1px solid #e2e8f0; border-radius: 12px; padding: 20px; box-shadow: 0 1px 3px rgba(0,0,0,0.05); margin-bottom: 20px;">
        <div style="font-weight: 800; font-size: 15px; color: #0f172a; margin-bottom: 6px; text-transform: uppercase; letter-spacing: 0.5px;">Executive Summary</div>
        <div style="font-size: 14px; color: #334155; line-height: 1.6;">{findings['summary']}</div>
    </div>
    """)
    st.markdown(exec_summary_html, unsafe_allow_html=True)

    # 2. Key Findings
    st.markdown("### 🔍 Key Analytical Findings")
    k_cols = st.columns(len(findings["key_findings"]))
    for i, finding in enumerate(findings["key_findings"]):
        with k_cols[i]:
            st.markdown(render_insight_card(f"📌 {finding['title']}", finding['detail']), unsafe_allow_html=True)

    # 3. Risks & Opportunities
    st.markdown("<div style='margin-top: 15px;'></div>", unsafe_allow_html=True)
    r_col1, r_col2 = st.columns(2)
    with r_col1:
        st.markdown("### 🛑 Profitability Risks & Value Leaks")
        for risk in findings["risks"]:
            st.markdown(render_alert("loss", risk["title"], risk["impact"]), unsafe_allow_html=True)

    with r_col2:
        st.markdown("### 💎 Strategic Growth Opportunities")
        for opp in findings["opportunities"]:
            st.markdown(render_alert("opportunity", opp["title"], opp["action"]), unsafe_allow_html=True)

    # 4. Actionable Recommendations (INSIGHT -> WHY IT MATTERS -> RECOMMENDED ACTION)
    st.markdown("---")
    st.markdown("### 🚀 Prioritized Executive Action Plan")
    st.markdown("<p style='font-size: 13px; color: #64748b; margin-top: -10px;'>Structured business playbooks answering <b>WHAT</b> is happening, <b>WHY</b> it is happening, and <b>WHAT ACTION</b> to execute.</p>", unsafe_allow_html=True)

    for rec in recommendations:
        priority_color = "#dc2626" if rec["priority"] == "CRITICAL" else ("#ea580c" if rec["priority"] == "HIGH" else "#2563eb")
        rec_card_html = clean_html(f"""
        <div style="background: #ffffff; border: 1px solid #e2e8f0; border-radius: 12px; padding: 18px 22px; margin-bottom: 16px; box-shadow: 0 1px 3px rgba(0,0,0,0.04);">
            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px;">
                <span style="font-weight: 700; font-size: 14px; color: #0f172a;">{rec['pillar']}</span>
                <span style="background-color: {priority_color}; color: white; font-size: 11px; font-weight: 700; padding: 2px 8px; border-radius: 6px;">{rec['priority']} PRIORITY</span>
            </div>
            <div style="margin-bottom: 8px;">
                <span style="font-weight: 700; color: #1e293b; font-size: 13px;">INSIGHT:</span>
                <span style="font-size: 13.5px; color: #334155;"> {rec['insight']}</span>
            </div>
            <div style="margin-bottom: 12px; background: #f8fafc; padding: 10px 14px; border-radius: 8px; border-left: 3px solid #cbd5e1;">
                <span style="font-weight: 700; color: #475569; font-size: 12.5px;">WHY IT MATTERS:</span>
                <span style="font-size: 13px; color: #475569;"> {rec['why_it_matters']}</span>
            </div>
            <div style="background: #eff6ff; padding: 10px 14px; border-radius: 8px; border-left: 3px solid #2563eb;">
                <span style="font-weight: 700; color: #1d4ed8; font-size: 13px;">RECOMMENDED ACTION:</span>
                <span style="font-size: 13px; font-weight: 600; color: #1e40af;"> {rec['recommended_action']}</span>
            </div>
        </div>
        """)
        st.markdown(rec_card_html, unsafe_allow_html=True)

    # 5. Interactive "Ask PROFITIQ" AI Assistant
    st.markdown("---")
    st.markdown("### 💬 Ask PROFITIQ (Business Analytics Assistant)")
    st.markdown("<p style='font-size: 13px; color: #64748b; margin-top: -10px;'>Ask any natural language question about current customers, products, discounts, or margins.</p>", unsafe_allow_html=True)

    quick_prompts = [
        "Which customer is most profitable?",
        "Which customers have high revenue but low profit?",
        "Which products have poor margins?",
        "Which region should we investigate?",
        "How much margin is lost to discounting?"
    ]
    
    qp_cols = st.columns(len(quick_prompts))
    for i, qp in enumerate(quick_prompts):
        with qp_cols[i]:
            if st.button(qp, key=f"qp_{i}", use_container_width=True):
                ans = answer_analytical_query(qp, filtered_df)
                st.session_state["chat_history"].append({"q": qp, "a": ans})

    user_query = st.text_input("Or enter your custom question:", placeholder="e.g. Which customer is losing money?")
    if st.button("Submit Question", type="primary"):
        if user_query.strip():
            ans = answer_analytical_query(user_query, filtered_df)
            st.session_state["chat_history"].append({"q": user_query, "a": ans})

    if st.session_state["chat_history"]:
        st.markdown("<div style='margin-top: 15px;'></div>", unsafe_allow_html=True)
        for item in reversed(st.session_state["chat_history"]):
            with st.chat_message("user"):
                st.write(item["q"])
            with st.chat_message("assistant", avatar="📈"):
                st.markdown(item["a"])

# =============================================================
# PAGE 7: DATA EXPLORER & EXPORT
# =============================================================
elif current_page == "Data Explorer & Export":
    st.markdown('<div class="section-header">🔍 Data Explorer, Audit Quality & Export Center</div>', unsafe_allow_html=True)

    # Data Quality Cards
    q_c1, q_c2, q_c3, q_c4 = st.columns(4)
    with q_c1:
        st.markdown(render_metric_card("Filtered Records", format_number(len(filtered_df)), sublabel=f"Out of {quality_info['initial_rows']:,} raw", icon="📑"), unsafe_allow_html=True)
    with q_c2:
        st.markdown(render_metric_card("Total Columns", format_number(len(filtered_df.columns)), sublabel="Standardized schema", icon="📊"), unsafe_allow_html=True)
    with q_c3:
        st.markdown(render_metric_card("Duplicates in Source", format_number(quality_info["duplicates_detected"]), sublabel="Detected & handled", icon="🔄"), unsafe_allow_html=True)
    with q_c4:
        st.markdown(render_metric_card("Memory Footprint", f"{quality_info['memory_mb']} MB", sublabel="In-memory cache", icon="💾"), unsafe_allow_html=True)

    st.markdown("<div style='margin-top: 20px;'></div>", unsafe_allow_html=True)

    # Data Export Section
    st.markdown("### 📥 Export Analytical Reports")
    cust_table, _, _ = get_customer_summary_table(filtered_df)
    prod_table = get_product_summary_table(filtered_df)
    reg_df = get_region_summary_table(filtered_df)

    export_dict = {
        "Executive Filtered Data": filtered_df,
        "Customer Profitability": cust_table,
        "Product Profitability": prod_table,
        "Regional Diagnostics": reg_df
    }
    
    excel_bytes = export_df_to_excel(export_dict)
    csv_bytes = export_df_to_csv(filtered_df)

    exp_col1, exp_col2 = st.columns(2)
    with exp_col1:
        st.download_button(
            label="📊 Download Full Multi-Tab Excel Report (.xlsx)",
            data=excel_bytes,
            file_name=f"PROFITIQ_Intelligence_Report_{datetime.datetime.now().strftime('%Y%m%d_%H%M')}.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            use_container_width=True
        )
    with exp_col2:
        st.download_button(
            label="📑 Download Filtered Transaction CSV (.csv)",
            data=csv_bytes,
            file_name=f"PROFITIQ_Filtered_Transactions_{datetime.datetime.now().strftime('%Y%m%d_%H%M')}.csv",
            mime="text/csv",
            use_container_width=True
        )

    st.markdown("<div style='margin-top: 20px;'></div>", unsafe_allow_html=True)

    # Interactive Table Explorer with Search
    st.markdown("### 🔎 Interactive Dataset Viewer")
    st.dataframe(filtered_df, use_container_width=True)

    # Summary Statistics
    with st.expander("📈 View Descriptive Statistical Summary"):
        st.dataframe(filtered_df.describe().round(2), use_container_width=True)

# -------------------------------------------------------------
# FOOTER
# -------------------------------------------------------------
footer_html = clean_html("""
<div style="margin-top: 50px; text-align: center; border-top: 1px solid #e2e8f0; padding-top: 20px; color: #94a3b8; font-size: 12px;">
    PROFITIQ • Enterprise Profitability & Margin Intelligence Platform &nbsp;|&nbsp; Built with Streamlit, Pandas & Plotly
</div>
""")
st.markdown(footer_html, unsafe_allow_html=True)
