"""
PROFITIQ: Data Loader Module
Handles multi-format ingestion (CSV, XLSX), schema detection, flexible column synonym mapping,
and comprehensive validation error reporting.
"""

import os
import pandas as pd
import streamlit as st

# Canonical Schema Mapping Definitions
COLUMN_SYNONYMS = {
    "Revenue": [
        "revenue", "sales", "gross sales", "net sales", "total sales", 
        "order value", "turnover", "net revenue", "amount", "total amount", "invoiced amount"
    ],
    "Cost": [
        "cost", "cogs", "total cost", "cost of goods sold", "product cost", 
        "unit cost", "expense", "total expense", "direct cost"
    ],
    "Profit": [
        "profit", "net profit", "gross profit", "operating profit", 
        "margin amount", "earnings", "net income", "contribution margin"
    ],
    "Discount": [
        "discount", "discount amount", "discount rate", "discount %", 
        "discount pct", "rebate", "allowance", "markdown"
    ],
    "Customer": [
        "customer", "customer name", "client", "account", "account name", 
        "buyer", "company", "client name", "customer id"
    ],
    "Product": [
        "product", "product name", "item", "item name", "sku", 
        "part number", "offering", "service", "material"
    ],
    "Category": [
        "category", "product category", "product line", "sub-category", 
        "department", "group", "family", "segment"
    ],
    "Region": [
        "region", "market", "territory", "zone", "country", 
        "geography", "location", "state", "area"
    ],
    "Order Date": [
        "order date", "date", "transaction date", "invoice date", 
        "sale date", "posting date", "period"
    ],
    "Order ID": [
        "order id", "order number", "transaction id", "invoice id", 
        "reference", "trans id", "order no", "document id"
    ],
    "Quantity": [
        "quantity", "qty", "units", "volume", "order qty", "count"
    ]
}

def normalize_string(s):
    """Clean and lower string for comparison."""
    if not isinstance(s, str):
        s = str(s)
    return s.strip().lower().replace("_", " ").replace("-", " ")

def detect_column_mappings(df_columns):
    """
    Intelligently map raw DataFrame columns to canonical PROFITIQ fields.
    Returns:
        dict: {canonical_field: detected_raw_col}
        list: missing_required_fields
    """
    detected_mapping = {}
    normalized_raw = {col: normalize_string(col) for col in df_columns}
    
    for canonical, synonyms in COLUMN_SYNONYMS.items():
        matched_col = None
        # 1. Exact match with canonical
        for raw_col, norm_col in normalized_raw.items():
            if norm_col == canonical.lower():
                matched_col = raw_col
                break
        
        # 2. Check synonyms
        if not matched_col:
            for syn in synonyms:
                for raw_col, norm_col in normalized_raw.items():
                    if norm_col == syn:
                        matched_col = raw_col
                        break
                if matched_col:
                    break
                    
        # 3. Substring match if still not found
        if not matched_col:
            for syn in synonyms:
                for raw_col, norm_col in normalized_raw.items():
                    if syn in norm_col or norm_col in syn:
                        matched_col = raw_col
                        break
                if matched_col:
                    break
                    
        if matched_col:
            detected_mapping[canonical] = matched_col

    # Essential minimum fields to run profitability intelligence:
    # Need either (Revenue + Cost) OR (Revenue + Profit) OR (Cost + Profit)
    has_revenue = "Revenue" in detected_mapping
    has_cost = "Cost" in detected_mapping
    has_profit = "Profit" in detected_mapping
    
    missing_critical = []
    if not (has_revenue or (has_cost and has_profit)):
        missing_critical.append("Revenue (or Sales/Amount)")
    if not (has_profit or (has_revenue and has_cost)):
        missing_critical.append("Profit or Cost")
    if "Customer" not in detected_mapping:
        missing_critical.append("Customer (or Client/Account)")
    if "Product" not in detected_mapping:
        missing_critical.append("Product (or Item/SKU)")
        
    return detected_mapping, missing_critical

@st.cache_data(show_spinner=False)
def load_data_from_file(file_bytes, file_name):
    """Read CSV or Excel buffer into DataFrame with robust encoding fallback."""
    try:
        lower_name = file_name.lower()
        if lower_name.endswith(('.xlsx', '.xls')):
            df = pd.read_excel(file_bytes, engine='openpyxl')
        else:
            try:
                df = pd.read_csv(file_bytes, encoding='utf-8')
            except UnicodeDecodeError:
                file_bytes.seek(0)
                df = pd.read_csv(file_bytes, encoding='latin1')
        return df, None
    except Exception as e:
        return None, str(e)

@st.cache_data(show_spinner=False)
def load_sample_dataset():
    """Load default benchmark demo dataset."""
    sample_csv_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data", "sample_data.csv")
    if os.path.exists(sample_csv_path):
        return pd.read_csv(sample_csv_path), "DEMO DATA"
    
    # Fallback inline generation if file not on disk
    from src.data_generator import generate_sample_dataset
    df = generate_sample_dataset(1200)
    return df, "DEMO DATA (Generated)"
