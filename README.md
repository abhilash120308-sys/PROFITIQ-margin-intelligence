# PROFITIQ: Profitability & Margin Intelligence Platform
> *"Turn Revenue Data into Profit Decisions."*

---

## 📌 Executive Summary & Business Context

In enterprise commerce, organizations frequently suffer from a critical strategic flaw:
**"Revenue-focused but profit-blind."**

Sales and marketing teams chase top-line gross transaction volume through heavy discounting, rebates, and special accommodations—often unaware that major customer accounts and high-volume product lines are actively destroying enterprise operating margins.

**PROFITIQ** transforms raw order and transaction data into actionable profitability intelligence. It moves beyond standard dashboards to answer three fundamental executive questions:

```
┌─────────────────┐       ┌─────────────────┐       ┌─────────────────┐
│     WHAT is     │  ───> │     WHY is it   │  ───> │   WHAT ACTION   │
│   happening?    │       │   happening?    │       │  should we take?│
└─────────────────┘       └─────────────────┘       └─────────────────┘
```

---

## 🎯 Key Capabilities & Platform Modules

### 1. 📊 Executive Overview
* **Financial Summary Cards**: Real-time KPI tracking for Total Revenue, Total Direct Cost, Total Net Profit, Operating Margin %, Total Discounts, Total Orders, and Active Accounts with period-over-period delta comparisons.
* **Profitability Health Score (0–100%)**: A transparent, weighted composite index evaluating:
  * Operating Margin Realization (30 pts)
  * Profitable Customer Breadth (25 pts)
  * Profitable Product Breadth (20 pts)
  * Discount Discipline & Guardrails (15 pts)
  * Loss Containment (10 pts)
* **Automated Risk & Value Alerts**: Instant triggers highlighting negative-margin accounts (🔴 Loss Alert), high-revenue low-margin traps (🟠 Margin Alert), excessive discounting (🟡 Discount Alert), and high-margin expansion targets (🟢 Opportunity).
* **Interactive Visualizations**: Time-series revenue vs. profit trend, category margin distributions, regional performance bars, and top profit drivers.

### 2. 👥 Customer Intelligence & 4-Quadrant Analysis
* **Statistical Quadrant Matrix**: Segmenting accounts using median revenue and profit thresholds:
  * ⭐ **High Revenue / High Profit (Stars)**: Enterprise anchors to protect and nurture.
  * ⚠️ **High Revenue / Low Profit (Margin Traps)**: The primary business hazard—heavy sales volume masked by razor-thin or negative margins.
  * 💎 **Low Revenue / High Profit (Niche Gems)**: High willingness-to-pay accounts ready for wallet-share expansion.
  * 🛑 **Low Revenue / Low Profit (Laggards)**: Operational drains requiring pricing restructuring or minimum order tiers.
* **Customer Deep-Dive Diagnostics**: Interactive account selector providing root-cause diagnostic explanations and tailored contract renegotiation playbooks.

### 3. 📦 Product Intelligence
* **SKU Margin Realization**: Diverging positive vs. negative margin spectrum across the catalog.
* **Leaderboards & Laggards**: Instant breakdown of top profit drivers vs. loss-making items where direct unit COGS exceeds discounted realized revenue.
* **Automated SKU Diagnostics**: Identifies margin-squeeze items needing bill-of-materials renegotiation or promotional discount caps.

### 4. 🏷️ Discount Intelligence & Margin Erosion Engine
* **Discount Tier Diagnostics**: Evaluates realized margin decay across discount brackets (`0-5%`, `5-15%`, `15-25%`, `>25%`).
* **Margin Erosion Warnings**: Detects accounts receiving above-average discounts that return below-average profitability.
* **Discount vs. Profit Correlation**: Quantifies the direct dollar impact of price concessions.

### 5. 🌍 Market & Category Analysis
* **Regional Value Diagnostics**: Identifies geographic disparities in pricing discipline and gross-to-net realization.
* **Category Contribution Matrix**: Compares Revenue Share % against Profit Share % to detect volume-heavy but margin-dilutive segments.
* **Region × Category Heatmap**: 2D cross-tabulation matrix of realized operating margins.

### 6. 🧠 Business Intelligence Center & Action Playbooks
* **Executive Findings & Risk Ledger**: Concise, data-grounded summaries of value concentration (Pareto principle) and leakage points.
* **Actionable Recommendations**: Standardized triplets answering:
  * **INSIGHT**: The statistical finding.
  * **WHY IT MATTERS**: Commercial and financial impact.
  * **RECOMMENDED ACTION**: Concrete operational playbook for sales, finance, and operations leadership.
* **💬 "Ask PROFITIQ" AI Assistant**: Natural-language conversational analytics engine grounded in calculated dataset aggregates with zero hallucination.

### 7. 🔍 Data Explorer & Multi-Format Export Center
* **Data Quality & Audit Cards**: Track row counts, duplicates, missing values, memory usage, and date coverage.
* **Multi-Tab Excel Report Export (`.xlsx`)**: One-click download containing Executive Data, Customer Ledger, Product Ledger, and Regional Diagnostics across dedicated sheets.
* **Filtered CSV Export (`.csv`)**: Instant extract of active filtered records.

---

## 🏗️ Project Architecture

```
unified-mentor-p1/
├── app.py                          # Streamlit main entry point & navigation router
├── requirements.txt                # Production dependencies
├── README.md                       # Platform documentation
├── .streamlit/
│   └── config.toml                 # Enterprise theme & styling configuration
├── src/
│   ├── __init__.py                 # Package initializer
│   ├── utils.py                    # Formats, CSS design system, metric cards, export helpers
│   ├── data_loader.py              # Multi-format ingestion & flexible column synonym mapping
│   ├── data_cleaner.py             # Data standardizer, type safety & metric derivations
│   ├── metrics.py                  # Executive KPIs, Health Score, and alert rules
│   ├── customer_analysis.py        # Customer aggregation, quadrant logic & deep dive
│   ├── product_analysis.py         # Product leaderboard, SKU margins & observations
│   ├── discount_analysis.py        # Discount tiers, decay curves & erosion alerts
│   ├── market_analysis.py          # Regional & category analysis, contribution matrices & heatmaps
│   ├── insight_engine.py           # Automated analytical insight generator
│   ├── recommendation_engine.py    # Structured action playbooks (Insight -> Why -> Action)
│   ├── visualizations.py           # Interactive Plotly enterprise chart suite
│   ├── ai_assistant.py             # Deterministic & grounded natural language assistant
│   └── data_generator.py           # Realistic enterprise benchmark dataset generator
├── data/
│   ├── sample_data.csv             # Benchmark CSV dataset (1,500 enterprise transactions)
│   └── sample_data.xlsx            # Benchmark Excel dataset
└── tests/
    └── test_pipeline.py            # Comprehensive 12-stage integration & unit test suite
```

---

## 🛠️ Technology Stack

| Layer | Technology |
|---|---|
| **Application & UI** | Streamlit 1.35+ |
| **Data Processing** | Pandas 2.0+, NumPy |
| **Interactive Visualizations** | Plotly Express & Graph Objects |
| **Machine Learning / Stats** | Scikit-Learn |
| **Excel & Report Generation** | OpenPyXL, XlsxWriter |
| **Language** | Python 3.10+ / 3.14 |

---

## 📥 Ingestion & Column Mapping Engine

PROFITIQ automatically recognizes and standardizes flexible schema naming conventions:

| Canonical Field | Recognized Synonyms & Aliases |
|---|---|
| **Revenue** | `Revenue`, `Sales`, `Net Sales`, `Order Value`, `Turnover`, `Amount`, `Invoiced Amount` |
| **Cost** | `Cost`, `COGS`, `Total Cost`, `Cost of Goods Sold`, `Expense`, `Unit Cost` |
| **Profit** | `Profit`, `Net Profit`, `Gross Profit`, `Operating Profit`, `Earnings`, `Margin Amount` |
| **Discount** | `Discount`, `Discount Amount`, `Discount Rate`, `Rebate`, `Allowance`, `Markdown` |
| **Customer** | `Customer`, `Customer Name`, `Client`, `Account`, `Company`, `Buyer` |
| **Product** | `Product`, `Product Name`, `SKU`, `Item`, `Offering`, `Part Number` |
| **Category** | `Category`, `Product Line`, `Department`, `Sub-Category`, `Family` |
| **Region** | `Region`, `Market`, `Territory`, `Country`, `Geography`, `State`, `Zone` |
| **Order Date** | `Order Date`, `Date`, `Transaction Date`, `Invoice Date`, `Period` |
| **Quantity** | `Quantity`, `Qty`, `Units`, `Volume`, `Count` |

*If optional financial fields are omitted, the engine automatically reconciles them (e.g., `Profit = Revenue - Cost - Discount`, `Cost = Revenue - Profit`, `Discount = 0.0`).*

---

## 🚀 Quickstart & Installation

### 1. Clone or Open the Repository
```bash
cd "c:\Users\Abhilash\OneDrive\Desktop\unified mentor p1"
```

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

### 3. Run the Automated Test Suite
```bash
python tests/test_pipeline.py
```
*(Confirms 100% pass across all 12 modules, calculations, and visualizations).*

### 4. Launch the Application
```bash
streamlit run app.py
```
*Or via Python module execution:*
```bash
python -m streamlit run app.py
```

Open your browser at `http://localhost:8501`.

---

## 📊 Financial Calculations & Methodology

$$\text{Profit Margin \%} = \left( \frac{\text{Net Operating Profit}}{\text{Net Invoiced Revenue}} \right) \times 100$$

$$\text{Discount Rate} = \frac{\text{Discount Amount}}{\text{Net Revenue} + \text{Discount Amount}}$$

$$\text{Customer Average Order Value} = \frac{\text{Total Customer Revenue}}{\text{Total Order Count}}$$

$$\text{Profit-to-Revenue Ratio} = \frac{\text{Segment Profit Share \%}}{\text{Segment Revenue Share \%}}$$

---

## 📈 Demo Dataset Archetypes

The included benchmark dataset (`data/sample_data.csv`, 1,500 records) realistically simulates:
1. **Star Accounts** (e.g. *Apex Global Tech*, *Quantum Dynamics*): 25–40% margins, disciplined discounting (<8%).
2. **Margin Trap Accounts** (e.g. *OmniCorp International*, *MegaRetail Logistics*): High revenue ($5M+) but razor-thin margins (3–8%) caused by 35–45% aggressive discounting.
3. **Niche Gems** (e.g. *Synergy BioLabs*, *FinTech Innovations*): Low order volume, 40%+ margins.
4. **Loss-Making Accounts** (e.g. *Starlight Media*, *Budget Office Outlet*): Negative margins caused by pricing concessions below direct fulfillment costs.
5. **Product Category Variance**: High-margin Cloud Software vs. low-margin/high-discounting Hardware Infrastructure.

---

## 🛡️ Quality & Design Standard

Built to look and feel like an **executive-grade SaaS analytics suite** (inspired by modern Power BI, Tableau, and Stripe Analytics):
- Clean, crisp light-canvas styling with subtle slate borders and soft drop shadows.
- Distinct color-coding: Emerald (`#10b981`) for profit/positive, Rose (`#ef4444`) for loss/risk, Amber (`#f59e0b`) for warning, Cobalt (`#2563eb`) for neutral.
- Comprehensive zero-division and empty dataset safeguards.
- 100% data-grounded insights and recommendations.
