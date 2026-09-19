/*
=============================================================================
Phase 2: PostgreSQL Analytics & Schema 
Description: Standard, performance-tuned PostgreSQL scripts for the 
             Retail Customer Shopping Behavior Analysis project.
=============================================================================
*/

-- ============================================================================
-- 1. Schema Definition (DDL)
-- ============================================================================
-- Define the core fact table structure. 
-- Data from the Python pipeline is initially loaded into 'clean_customer_shopping'
-- We will create a robust, indexed 'fact_purchases' table to house this data.

DROP TABLE IF EXISTS fact_purchases CASCADE;

CREATE TABLE fact_purchases (
    customer_id INT PRIMARY KEY,
    age INT CHECK (age >= 18 AND age <= 120),
    gender VARCHAR(20),
    category VARCHAR(50),
    purchase_amount NUMERIC(10, 2) CHECK (purchase_amount >= 0),
    review_rating NUMERIC(3, 2) CHECK (review_rating >= 1.0 AND review_rating <= 5.0),
    historical_purchases INT DEFAULT 0,
    age_group VARCHAR(20),
    purchase_frequency_score VARCHAR(20),
    clv_proxy NUMERIC(12, 2)
);

-- Note: Normally you would use an INSERT INTO ... SELECT FROM statement here 
-- to migrate data from the pandas staging table to the production schema.
-- INSERT INTO fact_purchases SELECT * FROM clean_customer_shopping;

-- Create indexes on frequently filtered/grouped columns for performance
CREATE INDEX idx_fact_purchases_category ON fact_purchases(category);
CREATE INDEX idx_fact_purchases_gender_age ON fact_purchases(gender, age_group);


-- ============================================================================
-- 2. Analysis Queries
-- ============================================================================

-- ----------------------------------------------------------------------------
-- A. Revenue Analysis
-- Description: Calculate total revenue, customer count, and average order 
--              value (AOV) grouped by gender and age_group.
-- ----------------------------------------------------------------------------
SELECT 
    gender,
    age_group,
    COUNT(customer_id) AS total_customers,
    SUM(purchase_amount) AS total_revenue,
    ROUND(AVG(purchase_amount), 2) AS average_order_value
FROM 
    fact_purchases
GROUP BY 
    gender, 
    age_group
ORDER BY 
    total_revenue DESC;


-- ----------------------------------------------------------------------------
-- B. High-Spenders Subquery (Top 10%)
-- Description: Extract customers whose total spend exceeds the 90th percentile 
--              of overall customer spend.
-- ----------------------------------------------------------------------------
WITH SpendPercentiles AS (
    SELECT 
        PERCENTILE_CONT(0.90) WITHIN GROUP (ORDER BY clv_proxy) AS p90_spend
    FROM 
        fact_purchases
)
SELECT 
    customer_id,
    gender,
    age_group,
    purchase_frequency_score,
    clv_proxy AS total_spend
FROM 
    fact_purchases
WHERE 
    clv_proxy > (SELECT p90_spend FROM SpendPercentiles)
ORDER BY 
    clv_proxy DESC;


-- ----------------------------------------------------------------------------
-- C. Top 3 Products by Category (Window Function)
-- Description: Isolate the top 3 revenue-generating "items" (here simulated by 
--              customers' individual high-value purchases within categories) 
--              using DENSE_RANK().
-- Note: In a pure star schema, 'product_id' would exist. Here we rank transactions.
-- ----------------------------------------------------------------------------
WITH CategoryRankings AS (
    SELECT 
        customer_id,
        category,
        purchase_amount,
        DENSE_RANK() OVER (PARTITION BY category ORDER BY purchase_amount DESC) AS revenue_rank
    FROM 
        fact_purchases
)
SELECT 
    category,
    customer_id AS top_transaction_customer,
    purchase_amount,
    revenue_rank
FROM 
    CategoryRankings
WHERE 
    revenue_rank <= 3
ORDER BY 
    category ASC, 
    revenue_rank ASC;
