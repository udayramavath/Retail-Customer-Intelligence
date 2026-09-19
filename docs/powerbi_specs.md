# Power BI Semantic Model & DAX Specifications

This document outlines the data model architecture and the analytical measures required to build the Executive Retail Dashboard in Power BI.

## 1. Data Model (Star Schema)

To ensure optimal performance and intuitive drag-and-drop report authoring, the data should be structured in a Star Schema format. 

### Fact Table
*   **`fact_purchases`**: The central table containing granular transaction/customer data.
    *   *Columns*: `customer_id`, `purchase_amount`, `review_rating`, `historical_purchases`, `clv_proxy`, `DateKey`, `ProductKey` (if expanded).

### Dimension Tables
*   **`dim_customer`**: Contains customer demographics.
    *   *Columns*: `customer_id` (PK), `age`, `age_group`, `gender`, `purchase_frequency_score`.
*   **`dim_product`**: Contains product hierarchy details.
    *   *Columns*: `product_id` (PK), `category`, `product_name`.
*   **`dim_date`**: A standard calendar table for time intelligence.
    *   *Columns*: `DateKey` (PK), `Date`, `Year`, `Quarter`, `Month`, `MonthName`, `DayOfWeek`.

**Relationships**:
*   `fact_purchases[customer_id]` -> `dim_customer[customer_id]` (Many-to-One, Single direction)
*   *(Future expansion)* `fact_purchases[product_id]` -> `dim_product[product_id]` (Many-to-One, Single direction)
*   *(Future expansion)* `fact_purchases[DateKey]` -> `dim_date[DateKey]` (Many-to-One, Single direction)

---

## 2. DAX Measures

Below are the explicit DAX formulas required for the core business logic. Create a dedicated `_KeyMeasures` table in Power BI to organize these.

### Core Financials
```dax
Total Revenue = SUM(fact_purchases[purchase_amount])
```

```dax
Total Transactions = COUNTROWS(fact_purchases)
```

```dax
AOV = DIVIDE([Total Revenue], [Total Transactions], 0)
```

### Customer Segmentation & Retention
```dax
High Value Customer % = 
VAR TotalCustomers = DISTINCTCOUNT(fact_purchases[customer_id])
VAR HighValueCustomers = 
    CALCULATE(
        DISTINCTCOUNT(fact_purchases[customer_id]), 
        dim_customer[purchase_frequency_score] = "High"
    )
RETURN DIVIDE(HighValueCustomers, TotalCustomers, 0)
```

```dax
Repeat Purchase Rate = 
VAR CustomersWithMultiplePurchases = 
    CALCULATE(
        DISTINCTCOUNT(fact_purchases[customer_id]),
        fact_purchases[historical_purchases] > 1
    )
VAR TotalCustomers = DISTINCTCOUNT(fact_purchases[customer_id])
RETURN DIVIDE(CustomersWithMultiplePurchases, TotalCustomers, 0)
```

---

## 3. Dashboard Blueprint

The report will consist of a 3-tab layout tailored for executive and managerial stakeholders.

### Tab 1: Executive KPI Overview
*   **Target Audience**: C-Suite, VP of Sales.
*   **Top Banner**: KPI Cards displaying `Total Revenue`, `AOV`, `Total Transactions`, and `Repeat Purchase Rate`.
*   **Visual 1 (Line Chart)**: Revenue Trend over time (requires `dim_date`).
*   **Visual 2 (Donut Chart)**: Revenue by `gender`.
*   **Visual 3 (Clustered Column Chart)**: Total Customers and Revenue by `age_group`.

### Tab 2: Category & Product Deep Dive
*   **Target Audience**: Inventory & Merchandising Teams.
*   **Top Banner**: Slicers for `Category` and `Date Range`.
*   **Visual 1 (Pareto Chart)**: Bar chart of Revenue by Category, with a cumulative % line (80/20 rule analysis).
*   **Visual 2 (Matrix Table)**: Top performing items/categories showing `Total Revenue`, `AOV`, and average `review_rating`. Conditional formatting (data bars) on Revenue.
*   **Visual 3 (Scatter Plot)**: `Total Revenue` (X-axis) vs `Average Review Rating` (Y-axis) by Category, to identify high-revenue/low-rated risks.

### Tab 3: Customer Segmentation & Retention
*   **Target Audience**: Marketing & CRM Teams.
*   **Top Banner**: Slicers for `age_group` and `gender`.
*   **Visual 1 (100% Stacked Bar)**: Proportion of `purchase_frequency_score` (Low, Medium, High) across different `age_groups`.
*   **Visual 2 (Gauge or KPI Card)**: `High Value Customer %` against a target threshold (e.g., 25%).
*   **Visual 3 (Scatter/Bubble Chart)**: RFM/Frequency Matrix. `historical_purchases` (X) vs `clv_proxy` (Y), bubble size by `Total Revenue`.
