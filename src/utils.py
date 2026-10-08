"""
PROFITIQ: Utility Functions
Provides formatting, enterprise CSS styling, export helpers, and zero-leak UI card builders.
"""

import io
import textwrap
import pandas as pd
import streamlit as st

def format_currency(val, symbol="$"):
    """Format numeric value into clean enterprise currency string ($1.2M, $450.5K, etc.)."""
    if val is None or pd.isna(val):
        return f"{symbol}0.00"
    
    is_neg = val < 0
    abs_val = abs(val)
    
    if abs_val >= 1_000_000_000:
        formatted = f"{symbol}{abs_val / 1_000_000_000:.2f}B"
    elif abs_val >= 1_000_000:
        formatted = f"{symbol}{abs_val / 1_000_000:.2f}M"
    elif abs_val >= 1_000:
        formatted = f"{symbol}{abs_val / 1_000:.1f}K"
    else:
        formatted = f"{symbol}{abs_val:,.2f}"
        
    return f"-{formatted}" if is_neg else formatted

def format_percent(val):
    """Format numeric value into percentage string."""
    if val is None or pd.isna(val):
        return "0.0%"
    return f"{val:.1f}%"

def format_number(val):
    """Format integer or float with commas."""
    if val is None or pd.isna(val):
        return "0"
    if isinstance(val, (int, float)):
        if abs(val) >= 1_000_000:
            return f"{val / 1_000_000:.1f}M"
        if abs(val) >= 1_000:
            return f"{val / 1_000:.1f}K"
        return f"{val:,.0f}"
    return str(val)

def safe_divide(numerator, denominator, default=0.0):
    """Safely divide two numbers handling zero and NaN."""
    try:
        if denominator == 0 or pd.isna(denominator) or pd.isna(numerator):
            return default
        return numerator / denominator
    except Exception:
        return default

def clean_html(html_str):
    """Dedent and strip HTML strings to prevent Markdown from interpreting leading whitespace as code blocks."""
    return textwrap.dedent(html_str).strip()

def get_enterprise_css():
    """Return custom CSS for enterprise look (Power BI / Tableau / Modern SaaS aesthetics)."""
    css = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&family=JetBrains+Mono:wght@400;500&display=swap');

html, body, [class*="css"] {
    font-family: 'Plus Jakarta Sans', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
    color: #0f172a;
}

.block-container {
    padding-top: 1.5rem;
    padding-bottom: 3rem;
    padding-left: 2rem;
    padding-right: 2rem;
    max-width: 1440px;
}

/* -------------------------------------------------------------
   SIDEBAR ENTERPRISE STYLING & WIDTH
------------------------------------------------------------- */
section[data-testid="stSidebar"] {
    background-color: #f8fafc !important;
    border-right: 1px solid #e2e8f0 !important;
    min-width: 325px !important;
    max-width: 340px !important;
}
section[data-testid="stSidebar"] .block-container {
    padding-top: 1.2rem !important;
    padding-left: 1.1rem !important;
    padding-right: 1.1rem !important;
}

/* Sidebar Brand Block */
.sidebar-brand-card, .sidebar-brand-container {
    background: #ffffff;
    border: 1px solid #e2e8f0;
    border-radius: 12px;
    padding: 14px 16px;
    margin-bottom: 16px;
    box-shadow: 0 2px 6px rgba(15, 23, 42, 0.04);
}
.sidebar-brand-row, .sidebar-brand-top {
    display: flex;
    align-items: center;
    gap: 12px;
}
.sidebar-brand-logo {
    background: linear-gradient(135deg, #2563eb 0%, #1d4ed8 100%);
    width: 48px;
    height: 48px;
    min-width: 48px;
    border-radius: 10px;
    display: flex;
    align-items: center;
    justify-content: center;
    color: #ffffff;
    font-weight: 800;
    font-size: 20px;
    letter-spacing: -0.5px;
    box-shadow: 0 4px 10px rgba(37, 99, 235, 0.35);
}
.sidebar-brand-name, .sidebar-brand-title {
    font-size: 20px;
    font-weight: 800;
    color: #0f172a;
    letter-spacing: -0.5px;
    line-height: 1.1;
    margin-bottom: 2px;
}
.sidebar-brand-subtitle, .sidebar-brand-tag {
    font-size: 9.5px;
    font-weight: 700;
    color: #2563eb;
    text-transform: uppercase;
    letter-spacing: 0.9px;
}
.sidebar-enterprise-pill, .sidebar-badge-pill {
    display: inline-flex;
    align-items: center;
    gap: 4px;
    background: #eff6ff;
    border: 1px solid #bfdbfe;
    color: #1d4ed8;
    font-size: 10px;
    font-weight: 700;
    padding: 3px 10px;
    border-radius: 20px;
    margin-top: 10px;
    text-transform: uppercase;
    letter-spacing: 0.6px;
}

/* Sidebar Section Headers */
.sidebar-section-title {
    font-size: 11.5px;
    font-weight: 800;
    text-transform: uppercase;
    letter-spacing: 0.7px;
    color: #475569;
    margin-top: 14px;
    margin-bottom: 6px;
    display: flex;
    align-items: center;
    gap: 6px;
}
.sidebar-section-sub {
    font-size: 11px;
    color: #64748b;
    margin-bottom: 10px;
    line-height: 1.35;
}

/* Navigation Button Styling */
section[data-testid="stSidebar"] .stButton > button {
    border-radius: 8px !important;
    padding: 9px 14px !important;
    font-size: 13px !important;
    font-weight: 600 !important;
    transition: all 0.15s ease-in-out !important;
    display: flex !important;
    justify-content: space-between !important;
    align-items: center !important;
    text-align: left !important;
    width: 100% !important;
    margin-bottom: 3px !important;
}

/* Primary (Active) Nav Button */
section[data-testid="stSidebar"] .stButton > button[kind="primary"] {
    background: linear-gradient(135deg, #2563eb 0%, #1d4ed8 100%) !important;
    color: #ffffff !important;
    border: 1px solid #1e40af !important;
    box-shadow: 0 2px 6px rgba(37, 99, 235, 0.25) !important;
    font-weight: 700 !important;
}

/* Secondary (Inactive) Nav Button */
section[data-testid="stSidebar"] .stButton > button[kind="secondary"] {
    background: #ffffff !important;
    color: #334155 !important;
    border: 1px solid #e2e8f0 !important;
    box-shadow: 0 1px 2px rgba(0, 0, 0, 0.02) !important;
}
section[data-testid="stSidebar"] .stButton > button[kind="secondary"]:hover {
    background: #f1f5f9 !important;
    color: #0f172a !important;
    border-color: #cbd5e1 !important;
    transform: translateX(2px) !important;
}

/* Active Data Status Card */
.sidebar-status-card {
    background: #ffffff;
    border: 1px solid #e2e8f0;
    border-radius: 9px;
    padding: 12px 14px;
    margin-top: 10px;
    margin-bottom: 12px;
    box-shadow: 0 1px 3px rgba(0,0,0,0.03);
}
.sidebar-status-indicator {
    display: flex;
    align-items: center;
    gap: 6px;
    font-size: 11.5px;
    font-weight: 700;
    color: #059669;
    margin-bottom: 8px;
    padding-bottom: 6px;
    border-bottom: 1px solid #f1f5f9;
}
.sidebar-status-dot {
    width: 8px;
    height: 8px;
    background-color: #10b981;
    border-radius: 50%;
    box-shadow: 0 0 0 2px rgba(16, 185, 129, 0.2);
}
.sidebar-status-row {
    display: flex;
    justify-content: space-between;
    font-size: 11px;
    color: #64748b;
    margin-bottom: 3px;
}
.sidebar-status-val {
    font-weight: 700;
    color: #0f172a;
}

/* Main Dashboard Top Header */
.brand-header-box {
    background: linear-gradient(135deg, #0f172a 0%, #1e293b 50%, #1e3a8a 100%);
    border-radius: 12px;
    padding: 20px 24px;
    margin-bottom: 20px;
    box-shadow: 0 4px 12px rgba(15, 23, 42, 0.12);
    display: flex;
    justify-content: space-between;
    align-items: center;
    border: 1px solid rgba(255, 255, 255, 0.1);
}
.brand-title {
    color: #ffffff;
    font-size: 24px;
    font-weight: 800;
    letter-spacing: -0.5px;
    margin: 0;
    display: flex;
    align-items: center;
    gap: 10px;
}
.brand-badge {
    background: linear-gradient(135deg, #2563eb, #38bdf8);
    color: #ffffff;
    font-size: 11px;
    font-weight: 700;
    padding: 3px 9px;
    border-radius: 20px;
    text-transform: uppercase;
    letter-spacing: 0.8px;
}
.brand-subtitle {
    color: #94a3b8;
    font-size: 13px;
    font-weight: 500;
    margin-top: 4px;
    margin-bottom: 0;
}

/* Metric Cards */
.metric-card {
    background: #ffffff;
    border-radius: 10px;
    padding: 14px 16px;
    border: 1px solid #e2e8f0;
    box-shadow: 0 1px 3px rgba(0, 0, 0, 0.04);
    min-height: 118px;
    height: 100%;
    box-sizing: border-box;
    display: flex;
    flex-direction: column;
    justify-content: space-between;
    transition: transform 0.15s ease, box-shadow 0.15s ease, border-color 0.15s ease;
}
.metric-card:hover {
    transform: translateY(-2px);
    box-shadow: 0 6px 12px rgba(0, 0, 0, 0.06);
    border-color: #cbd5e1;
}
.metric-header {
    display: flex;
    align-items: center;
    justify-content: space-between;
    margin-bottom: 4px;
}
.metric-label {
    font-size: 11px;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 0.5px;
    color: #64748b;
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
}
.metric-value {
    font-size: 20px;
    font-weight: 800;
    color: #0f172a;
    letter-spacing: -0.4px;
    margin-top: 2px;
    margin-bottom: 2px;
    font-feature-settings: "tnum";
}
.metric-subtext {
    font-size: 10.5px;
    color: #94a3b8;
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
    margin-top: 2px;
}
.metric-delta {
    font-size: 10px;
    font-weight: 700;
    display: inline-flex;
    align-items: center;
    padding: 1px 5px;
    border-radius: 4px;
    line-height: 1.3;
}
.metric-delta.positive {
    color: #059669;
    background-color: #ecfdf5;
}
.metric-delta.negative {
    color: #dc2626;
    background-color: #fef2f2;
}
.metric-delta.neutral {
    color: #2563eb;
    background-color: #eff6ff;
}

.health-score-container {
    background: #ffffff;
    border: 1px solid #e2e8f0;
    border-radius: 10px;
    padding: 18px 20px;
    box-shadow: 0 1px 3px rgba(0,0,0,0.03);
    min-height: 185px;
}
.health-score-bar-bg {
    background-color: #e2e8f0;
    border-radius: 9999px;
    height: 10px;
    width: 100%;
    overflow: hidden;
    margin-top: 8px;
    margin-bottom: 8px;
}
.health-score-bar-fill {
    height: 100%;
    border-radius: 9999px;
    transition: width 0.8s ease-in-out;
}

.alert-box {
    border-radius: 8px;
    padding: 12px 16px;
    margin-bottom: 10px;
    display: flex;
    align-items: flex-start;
    gap: 10px;
    font-size: 13px;
    line-height: 1.4;
}
.alert-loss {
    background-color: #fef2f2;
    border: 1px solid #fecaca;
    color: #991b1b;
}
.alert-margin {
    background-color: #fffbeb;
    border: 1px solid #fde68a;
    color: #92400e;
}
.alert-discount {
    background-color: #fefce8;
    border: 1px solid #fef08a;
    color: #854d0e;
}
.alert-opportunity {
    background-color: #f0fdf4;
    border: 1px solid #bbf7d0;
    color: #166534;
}

.insight-card {
    background: #ffffff;
    border-left: 4px solid #2563eb;
    border-radius: 0 8px 8px 0;
    padding: 14px 16px;
    margin-bottom: 12px;
    box-shadow: 0 1px 3px rgba(0,0,0,0.04);
    border-top: 1px solid #f1f5f9;
    border-right: 1px solid #f1f5f9;
    border-bottom: 1px solid #f1f5f9;
    height: 100%;
    box-sizing: border-box;
}
.insight-title {
    font-size: 13.5px;
    font-weight: 700;
    color: #0f172a;
    margin-bottom: 4px;
}
.insight-why {
    font-size: 12.5px;
    color: #475569;
    line-height: 1.45;
}
.insight-action {
    font-size: 12.5px;
    font-weight: 600;
    color: #1d4ed8;
    background-color: #eff6ff;
    padding: 4px 10px;
    border-radius: 5px;
    display: inline-block;
    margin-top: 6px;
}

.section-header {
    font-size: 17px;
    font-weight: 700;
    color: #0f172a;
    margin-top: 20px;
    margin-bottom: 14px;
    display: flex;
    align-items: center;
    gap: 8px;
    border-bottom: 2px solid #f1f5f9;
    padding-bottom: 6px;
}

div[data-testid="stSidebarNav"] {display: none;}
</style>
"""
    return clean_html(css)

def render_metric_card(label, value, delta=None, delta_type="neutral", sublabel="", icon=""):
    """
    Generate clean, dedented HTML for an executive metric card.
    Guaranteed to have zero leading whitespace on any line.
    """
    delta_html = ""
    if delta:
        delta_html = f'<span class="metric-delta {delta_type}">{delta}</span>'
        
    sublabel_html = f'<div class="metric-subtext">{sublabel}</div>' if sublabel else '<div class="metric-subtext">&nbsp;</div>'
    
    html = f"""<div class="metric-card"><div><div class="metric-header"><div class="metric-label">{icon} {label}</div>{delta_html}</div><div class="metric-value">{value}</div></div>{sublabel_html}</div>"""
    return html

def render_alert(alert_type, title, description, badge=""):
    """Generate clean HTML for standardized alert box without code block artifacts."""
    type_class_map = {
        "loss": ("alert-loss", "🔴 LOSS ALERT"),
        "margin": ("alert-margin", "🟠 MARGIN ALERT"),
        "discount": ("alert-discount", "🟡 DISCOUNT ALERT"),
        "opportunity": ("alert-opportunity", "🟢 OPPORTUNITY")
    }
    css_class, default_badge = type_class_map.get(alert_type.lower(), ("alert-margin", "⚠️ ALERT"))
    badge_text = badge if badge else default_badge
    
    html = f"""<div class="alert-box {css_class}"><div style="flex: 1;"><div style="font-weight: 700; font-size: 11.5px; margin-bottom: 2px; letter-spacing: 0.5px;">{badge_text}</div><div style="font-weight: 600; margin-bottom: 2px;">{title}</div><div style="font-size: 12.5px; opacity: 0.95;">{description}</div></div></div>"""
    return html

def render_insight_card(title, text):
    """Generate clean HTML for an insight takeaway card."""
    html = f"""<div class="insight-card"><div class="insight-title">{title}</div><div class="insight-why">{text}</div></div>"""
    return html

def export_df_to_excel(df_dict):
    """Export multiple DataFrames to multi-tab Excel bytes."""
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        for sheet_name, df in df_dict.items():
            clean_name = sheet_name[:31]
            df.to_excel(writer, sheet_name=clean_name, index=False)
    output.seek(0)
    return output.getvalue()

def export_df_to_csv(df):
    """Export DataFrame to CSV bytes."""
    return df.to_csv(index=False).encode('utf-8')
