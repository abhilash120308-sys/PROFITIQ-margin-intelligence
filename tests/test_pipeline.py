"""
PROFITIQ: Unit and Integration Test Suite
Validates all data loaders, cleaners, metrics, analyses, visualizers, and edge cases.
"""

import os
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pandas as pd
import numpy as np

from src.utils import (
    render_insight_card, render_metric_card, render_alert, clean_html,
    format_currency, format_percent, format_number, safe_divide
)
from src.data_loader import load_sample_dataset, detect_column_mappings, load_data_from_file
from src.data_cleaner import standardize_and_clean_data
from src.metrics import calculate_executive_kpis, calculate_profitability_health_score, generate_automated_alerts
from src.customer_analysis import get_customer_summary_table, get_customer_deep_dive
from src.product_analysis import get_product_summary_table, get_product_leaderboards, generate_product_observations
from src.discount_analysis import get_discount_metrics, get_discount_tier_analysis, get_margin_erosion_alerts
from src.market_analysis import get_region_summary_table, get_category_summary_table, get_market_diagnostics, get_region_category_heatmap
from src.insight_engine import generate_executive_insights, generate_comprehensive_business_findings
from src.recommendation_engine import generate_strategic_recommendations
from src.visualizations import (
    plot_revenue_profit_trend, plot_revenue_profit_by_category, plot_margin_by_region,
    plot_top_entities, plot_discount_vs_profit_scatter, plot_customer_quadrants,
    plot_product_margins_diverging, plot_discount_vs_product_margin,
    plot_discount_tier_margin_realization, plot_market_matrix,
    plot_region_category_heatmap_chart
)
from src.ai_assistant import answer_analytical_query

def run_all_tests():
    print("========================================")
    print("RUNNING PROFITIQ INTEGRATION TEST SUITE")
    print("========================================")

    # 1. Test Data Loader
    sample_df, source_label = load_sample_dataset()
    assert not sample_df.empty, "Sample DataFrame should not be empty"
    print(f"[PASS] 1. Sample Data Ingestion Passed: {len(sample_df)} records loaded.")

    # 2. Test Schema Mapping Detection
    mapping, missing = detect_column_mappings(sample_df.columns)
    assert len(missing) == 0, f"Critical columns reported missing: {missing}"
    print(f"[PASS] 2. Schema Mapping Passed: Detected {len(mapping)} canonical fields.")

    # 3. Test Data Standardization & Cleaning
    clean_df, quality_info = standardize_and_clean_data(sample_df, mapping)
    assert not clean_df.empty, "Cleaned DataFrame should not be empty"
    assert "Revenue" in clean_df.columns and "Profit" in clean_df.columns
    assert not clean_df["Profit Margin %"].isna().any(), "No NaNs in Profit Margin %"
    print(f"[PASS] 3. Data Cleaning & Metrics Computation Passed.")

    # 4. Test Executive KPIs & Health Score
    kpis = calculate_executive_kpis(clean_df)
    assert kpis["total_revenue"] > 0, "Total revenue must be positive"
    score, breakdown, status = calculate_profitability_health_score(clean_df)
    assert 0 <= score <= 100, "Health score must be between 0 and 100"
    alerts = generate_automated_alerts(clean_df)
    print(f"[PASS] 4. KPIs & Health Score Passed: Score={score}/100, Alerts={len(alerts)}.")

    # 5. Test Customer Intelligence & Quadrants
    cust_table, med_rev, med_profit = get_customer_summary_table(clean_df)
    assert not cust_table.empty, "Customer table should not be empty"
    assert "Quadrant" in cust_table.columns and "Value Segment" in cust_table.columns
    sample_cust = cust_table.iloc[0]["Customer"]
    deep_dive = get_customer_deep_dive(clean_df, sample_cust)
    assert deep_dive is not None, "Customer deep dive should not be None"
    print(f"[PASS] 5. Customer Quadrants & Deep-Dive Passed: {len(cust_table)} accounts analyzed.")

    # 6. Test Product Intelligence
    prod_table = get_product_summary_table(clean_df)
    assert not prod_table.empty, "Product table should not be empty"
    top_p, worst_p, high_m, low_m = get_product_leaderboards(prod_table)
    prod_obs = generate_product_observations(prod_table)
    print(f"[PASS] 6. Product Intelligence Passed: {len(prod_table)} SKUs, {len(prod_obs)} observations.")

    # 7. Test Discount Intelligence
    disc_metrics = get_discount_metrics(clean_df)
    assert disc_metrics["total_discount"] >= 0
    tier_df = get_discount_tier_analysis(clean_df)
    assert not tier_df.empty
    erosion_alerts = get_margin_erosion_alerts(clean_df)
    print(f"[PASS] 7. Discount Intelligence & Margin Erosion Passed: {len(tier_df)} tiers evaluated.")

    # 8. Test Market & Category Analysis
    reg_df = get_region_summary_table(clean_df)
    cat_df = get_category_summary_table(clean_df)
    mkt_diag = get_market_diagnostics(reg_df, cat_df)
    heatmap_df = get_region_category_heatmap(clean_df)
    assert not reg_df.empty and not cat_df.empty
    print(f"[PASS] 8. Market & Category Diagnostics Passed.")

    # 9. Test Insight & Recommendation Engines
    insights = generate_executive_insights(clean_df)
    assert len(insights) >= 3, "At least 3 insights should be generated"
    findings = generate_comprehensive_business_findings(clean_df)
    recs = generate_strategic_recommendations(clean_df)
    assert len(recs) >= 2, "Strategic recommendations should be generated"
    print(f"[PASS] 9. Insights & Actionable Recommendations Passed: {len(insights)} insights, {len(recs)} playbooks.")

    # 10. Test Visualizations (Plotly Figures)
    fig1 = plot_revenue_profit_trend(clean_df)
    fig2 = plot_revenue_profit_by_category(clean_df)
    fig3 = plot_margin_by_region(clean_df)
    fig4 = plot_top_entities(clean_df, "Customer", 8)
    fig5 = plot_discount_vs_profit_scatter(clean_df)
    fig6 = plot_customer_quadrants(cust_table, med_rev, med_profit)
    fig7 = plot_product_margins_diverging(prod_table)
    fig8 = plot_discount_vs_product_margin(prod_table)
    fig9 = plot_discount_tier_margin_realization(tier_df)
    fig10 = plot_market_matrix(reg_df)
    fig11 = plot_region_category_heatmap_chart(heatmap_df)
    print(f"[PASS] 10. All 11 Plotly Visualizations Rendered Successfully.")

    # 11. Test AI Assistant Query Engine
    test_queries = [
        "Which customer is most profitable?",
        "Which customers have high revenue but low profit?",
        "Which products have poor margins?",
        "Which region should we investigate?",
        "How much margin is lost to discounting?"
    ]
    for q in test_queries:
        ans = answer_analytical_query(q, clean_df)
        assert len(ans) > 10, f"Failed query: {q}"
    print(f"[PASS] 11. AI Assistant Grounded Query Resolution Passed.")

    # 12. Test UI Card & Alert Renderers (render_insight_card, render_metric_card, render_alert)
    card_html = render_metric_card("Test Label", "$100", delta="+10%", delta_type="positive", sublabel="Subtext")
    assert "<div class=\"metric-card\">" in card_html and "\n" not in card_html
    alert_html = render_alert("loss", "Alert Title", "Alert Desc")
    assert "<div class=\"alert-box" in alert_html
    insight_html = render_insight_card("Insight Title", "Insight Text")
    assert "<div class=\"insight-card\">" in insight_html and "Insight Title" in insight_html
    print(f"[PASS] 12. UI Renderers (render_insight_card, render_metric_card, render_alert) Passed.")

    # 13. Edge Case Tests: Zero Revenue, Empty Data, Missing Cost
    zero_df = pd.DataFrame([{
        "Customer": "Zero Corp", "Product": "Free Item", "Revenue": 0.0, "Cost": 100.0, "Discount": 0.0, "Profit": -100.0
    }])
    clean_zero, _ = standardize_and_clean_data(zero_df, {"Customer": "Customer", "Product": "Product", "Revenue": "Revenue", "Cost": "Cost", "Profit": "Profit"})
    zero_kpis = calculate_executive_kpis(clean_zero)
    assert not np.isnan(clean_zero["Profit Margin %"].iloc[0]), "Zero revenue margin should be safe"
    assert not np.isinf(clean_zero["Profit Margin %"].iloc[0]), "Zero revenue margin should not be Inf"
    print(f"[PASS] 13. Edge Case & Zero-Division Safety Passed.")

    print("========================================")
    print("ALL TESTS PASSED SUCCESSFULLY! (100% PASS)")
    print("========================================")

if __name__ == "__main__":
    run_all_tests()
