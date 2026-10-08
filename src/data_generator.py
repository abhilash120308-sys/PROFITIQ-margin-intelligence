"""
Sample Data Generator for PROFITIQ Platform
Generates realistic enterprise order & profitability transactions
incorporating real-world business dynamics (Margin erosion, discount leakage, quadrant separation).
"""

import os
import random
import numpy as np
import pandas as pd
from datetime import datetime, timedelta

def generate_sample_dataset(num_records=1200, seed=42):
    np.random.seed(seed)
    random.seed(seed)

    # 1. Master Data Definitions
    regions = ["North America", "Europe", "Asia-Pacific", "Latin America", "Middle East & Africa"]
    
    categories = {
        "Enterprise Software": [
            ("Cloud ERP Suite", 4500, 1200), # (base_price, base_cost)
            ("CyberSecurity Platform", 3200, 950),
            ("Analytics Cloud Pro", 2800, 700),
            ("DevOps Automation Hub", 1900, 600)
        ],
        "Hardware & Infrastructure": [
            ("Edge AI Gateway Server", 6500, 4800),
            ("High-Density Rack Switch", 3800, 3100),
            ("NVMe SAN Storage Array", 8200, 6900),
            ("Industrial IoT Sensor Pack", 1200, 900)
        ],
        "Professional Services": [
            ("Cloud Migration Sprint", 5000, 2800),
            ("Architecture Review & Audit", 3500, 1800),
            ("24/7 Managed SRE Support", 4000, 2400),
            ("Custom Integration Toolkit", 2500, 1400)
        ],
        "Workplace & Office Solutions": [
            ("Ergonomic Smart Desk Suite", 1600, 1350),
            ("Executive Telepresence Unit", 2900, 2450),
            ("Conference Audio Matrix", 1100, 850),
            ("Modular Acoustic Pods", 4200, 3600)
        ]
    }

    # Customers with distinct behavioral archetypes to demonstrate all quadrants & alerts:
    # (Name, Archetype, Preferred Region, Target Discount Range)
    customer_profiles = [
        # High Revenue, High Profit (Star Accounts)
        ("Apex Global Tech", "Star", "North America", (0.02, 0.08)),
        ("Quantum Dynamics", "Star", "Europe", (0.03, 0.10)),
        ("Vanguard Financial Systems", "Star", "North America", (0.01, 0.07)),
        ("Beacon Healthcare", "Star", "Asia-Pacific", (0.04, 0.09)),
        ("Titan Energy Partners", "Star", "Middle East & Africa", (0.02, 0.08)),
        
        # High Revenue, Low Profit / Margin Destroyer (The "Revenue-Focused but Profit-Blind" Trap)
        ("OmniCorp International", "MarginEroder", "Europe", (0.28, 0.45)),
        ("MegaRetail Logistics", "MarginEroder", "North America", (0.30, 0.48)),
        ("Global Wholesale Direct", "MarginEroder", "Asia-Pacific", (0.32, 0.50)),
        ("Apex Horizon Distribution", "MarginEroder", "Latin America", (0.25, 0.42)),
        
        # Low Revenue, High Profit (High Margin Gems / Niche)
        ("Synergy BioLabs", "NicheGem", "Europe", (0.00, 0.05)),
        ("FinTech Innovations", "NicheGem", "North America", (0.01, 0.06)),
        ("Precision Robotics Ltd", "NicheGem", "Asia-Pacific", (0.02, 0.07)),
        ("Summit Capital Advisors", "NicheGem", "North America", (0.00, 0.04)),
        
        # Low Revenue, Low Profit / Chronic Loss Makers
        ("Starlight Media", "LossMaker", "Latin America", (0.35, 0.55)),
        ("Discount Express Corp", "LossMaker", "Middle East & Africa", (0.38, 0.60)),
        ("Budget Office Outlet", "LossMaker", "Europe", (0.30, 0.50)),
        
        # Moderate / Standard accounts
        ("Nexus Telecom", "Standard", "Asia-Pacific", (0.08, 0.18)),
        ("Pinnacle Manufacturing", "Standard", "North America", (0.06, 0.15)),
        ("Sterling & Cross Partners", "Standard", "Europe", (0.05, 0.14)),
        ("Acrobat Logistics Group", "Standard", "Latin America", (0.10, 0.20)),
        ("Horizon Media Network", "Standard", "North America", (0.07, 0.16)),
        ("Helios Solar Tech", "Standard", "Europe", (0.08, 0.17)),
        ("Zenith Biopharma", "Standard", "Asia-Pacific", (0.05, 0.12)),
        ("Cascade Industrial Works", "Standard", "Middle East & Africa", (0.09, 0.19)),
        ("Orion Consumer Goods", "Standard", "Latin America", (0.12, 0.22))
    ]

    # Generate dates across 18 months
    start_date = datetime(2023, 1, 1)
    end_date = datetime(2024, 6, 30)
    total_days = (end_date - start_date).days

    records = []
    
    for i in range(1, num_records + 1):
        order_id = f"ORD-2023-{1000 + i}"
        
        # Pick customer based on weighted probabilities (Stars and MarginEroders place bigger/more frequent orders)
        cust_weights = [
            4 if p[1] in ["Star", "MarginEroder"] else (1 if p[1] in ["NicheGem", "LossMaker"] else 2) 
            for p in customer_profiles
        ]
        total_w = sum(cust_weights)
        norm_weights = [w / total_w for w in cust_weights]
        
        cust_idx = np.random.choice(len(customer_profiles), p=norm_weights)
        cust_name, cust_type, pref_region, (min_disc, max_disc) = customer_profiles[cust_idx]
        
        # Region (80% preferred, 20% random other)
        if random.random() < 0.8:
            region = pref_region
        else:
            region = random.choice(regions)
            
        # Category & Product
        category_name = random.choice(list(categories.keys()))
        product_tuple = random.choice(categories[category_name])
        product_name, list_unit_price, base_unit_cost = product_tuple
        
        # Quantity
        if cust_type == "MarginEroder":
            quantity = random.randint(4, 18)
        elif cust_type == "Star":
            quantity = random.randint(3, 14)
        elif cust_type == "NicheGem":
            quantity = random.randint(1, 4)
        else:
            quantity = random.randint(1, 8)
            
        # Date
        days_offset = random.randint(0, total_days)
        order_date = start_date + timedelta(days=days_offset)
        
        # Discount Calculation
        discount_rate = round(random.uniform(min_disc, max_disc), 3)
        
        # Special case: occasional promotional margin hit for certain product combinations
        if "Hardware" in category_name and region == "Latin America" and random.random() < 0.25:
            discount_rate = min(0.55, discount_rate + 0.15)
            
        gross_sales = list_unit_price * quantity
        discount_amount = round(gross_sales * discount_rate, 2)
        net_revenue = round(gross_sales - discount_amount, 2)
        
        # Cost with slight variance (shipping/handling variations)
        unit_cost = base_unit_cost * random.uniform(0.95, 1.08)
        total_cogs = round(unit_cost * quantity, 2)
        
        # Profit = Net Revenue - Total COGS
        profit = round(net_revenue - total_cogs, 2)
        margin_pct = round((profit / net_revenue) * 100, 2) if net_revenue > 0 else 0.0

        records.append({
            "Order ID": order_id,
            "Order Date": order_date.strftime("%Y-%m-%d"),
            "Customer": cust_name,
            "Customer Segment": "Enterprise" if quantity > 5 else "Mid-Market",
            "Region": region,
            "Category": category_name,
            "Product": product_name,
            "Quantity": quantity,
            "List Price": list_unit_price,
            "Gross Sales": gross_sales,
            "Discount Rate": discount_rate,
            "Discount Amount": discount_amount,
            "Revenue": net_revenue,
            "Cost": total_cogs,
            "Profit": profit,
            "Profit Margin %": margin_pct
        })

    df = pd.DataFrame(records)
    # Sort by date
    df["Order Date"] = pd.to_datetime(df["Order Date"])
    df = df.sort_values("Order Date").reset_index(drop=True)
    df["Order Date"] = df["Order Date"].dt.strftime("%Y-%m-%d")
    return df

if __name__ == "__main__":
    os.makedirs("data", exist_ok=True)
    df = generate_sample_dataset(1500)
    
    csv_path = "data/sample_data.csv"
    xlsx_path = "data/sample_data.xlsx"
    
    df.to_csv(csv_path, index=False)
    df.to_excel(xlsx_path, index=False, engine="openpyxl")
    
    print(f"Generated {len(df)} records in {csv_path} and {xlsx_path}")
    print(f"Total Revenue: ${df['Revenue'].sum():,.2f}")
    print(f"Total Cost: ${df['Cost'].sum():,.2f}")
    print(f"Total Profit: ${df['Profit'].sum():,.2f}")
    print(f"Overall Margin: {(df['Profit'].sum()/df['Revenue'].sum())*100:.2f}%")
