# Retail Customer Shopping Behavior Analysis 🛒📊

![Python](https://img.shields.io/badge/python-3670A0?style=for-the-badge&logo=python&logoColor=ffdd54)
![PostgreSQL](https://img.shields.io/badge/postgresql-4169e1?style=for-the-badge&logo=postgresql&logoColor=white)
![Power BI](https://img.shields.io/badge/power_bi-F2C811?style=for-the-badge&logo=powerbi&logoColor=black)
![License](https://img.shields.io/badge/License-MIT-green.svg?style=for-the-badge)

An end-to-end, enterprise-grade data engineering and analytics portfolio project designed to uncover actionable insights into retail customer shopping behavior. This project features an automated Python ETL pipeline, performance-tuned PostgreSQL analytics, and a specification for a strategic Power BI executive dashboard.

---

## 🎯 Project Objective

To analyze transactional retail data to drive **customer retention**, increase **purchase frequency**, and optimize **revenue growth**. By engineering a robust data pipeline and modeling the data, this project identifies high-value customer cohorts (the top 10%) and surfaces critical insights into category performance.

## 🏗️ Architecture & Pipeline

The data flows through a modern analytics stack:

```mermaid
graph LR
    A[(Raw Data / Mock Data)] -->|Pandas ETL| B(Data Cleaning & Imputation)
    B -->|Feature Engineering| C(Age, Frequency, CLV Proxy)
    C -->|SQLAlchemy| D[(PostgreSQL Data Warehouse)]
    C -->|CSV Export| E[Processed CSV File]
    D -->|SQL Analytics| F[Insights & Aggregations]
    D -->|Direct Query| G[Power BI Semantic Model]
```

## 📂 Repository Structure

```text
retail-shopping-analysis/
│
├── data/
│   ├── raw/                  # Raw, uncleaned CSV files (ignored in git)
│   └── processed/            # Cleaned data ready for BI consumption
│
├── src/
│   └── data_pipeline.py      # Python ETL script (Cleaning, Imputation, Engineering)
│
├── sql/
│   └── analysis_queries.sql  # PostgreSQL DDL and Analytical Queries (CTEs, Window Functions)
│
├── docs/
│   ├── powerbi_specs.md      # Star schema design and DAX measure formulas
│   └── EXECUTIVE_REPORT.md   # Synthesized business findings and strategic recommendations
│
├── requirements.txt          # Python dependencies
└── README.md                 # Project documentation
```

## 🚀 Reproduction Instructions

Follow these steps to run the project locally.

### 1. Environment Setup

Clone the repository and set up a virtual environment:

```bash
git clone https://github.com/yourusername/retail-shopping-analysis.git
cd retail-shopping-analysis

# Create and activate virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Database Configuration

Ensure PostgreSQL is installed and running. By default, the script connects to a local database named `retail_db`. 
Set your connection string via an environment variable if it differs:

```bash
export DB_CONNECTION_STRING="postgresql://username:password@localhost:5432/retail_db"
```
*(On Windows PowerShell use `$env:DB_CONNECTION_STRING="..."`)*

### 3. Run the Data Pipeline

Execute the ETL script. If no raw data is provided, the script will automatically generate 1,000 rows of statistically sound mock data for demonstration purposes.

```bash
python src/data_pipeline.py
```

**What this does:**
- Standardizes column names to `snake_case`.
- Imputes missing numerical values using grouped medians.
- Engineers `age_group`, `purchase_frequency_score`, and `clv_proxy`.
- Saves to `data/processed/clean_customer_shopping.csv`.
- Loads the data into the PostgreSQL `retail_db`.

### 4. Execute Analytics Queries

Open `sql/analysis_queries.sql` in pgAdmin, DBeaver, or via `psql` to view the schema definitions and execute the analytical queries.

## 📈 Metric Highlights & Business Impact

Based on the execution of the SQL analytics and Power BI modeling, key deliverables include:

- **Revenue Analysis**: Cross-tabulation of AOV by Gender and Age Group to pinpoint highest-margin demographics.
- **Top 10% Identification**: A robust CTE isolating the highest-spending customers, enabling targeted VIP retention marketing.
- **Category Ranking**: Implementation of `DENSE_RANK()` window functions to isolate the top 3 revenue-generating transactions per product category.

For a full breakdown of the business findings and recommendations, please read the [Executive Report](docs/EXECUTIVE_REPORT.md).

---
*Developed by a Principal Data Engineer & Senior Analytics Architect.*
