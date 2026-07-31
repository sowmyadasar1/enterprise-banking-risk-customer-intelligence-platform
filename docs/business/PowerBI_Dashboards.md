# Power BI Dashboard Platform

The Power BI Platform (Phase 8) provides enterprise-grade business intelligence visualizations.

## Dashboard Specifications

### 1. Executive Dashboard
- **Audience**: C-Suite, VP of Finance
- **KPIs**: Total Revenue, YTD Growth, Active Customers, Fraud Loss Rate
- **Visuals**: KPI cards, revenue trend line, regional heatmap

### 2. Risk & Compliance Dashboard
- **Audience**: Chief Risk Officer, Compliance Team
- **KPIs**: Fraud Detection Rate, Non-Performing Loan Ratio, Average Credit Score
- **Visuals**: Fraud cases over time, loan default distribution, risk score histogram

### 3. Customer Intelligence Dashboard
- **Audience**: VP of Marketing, Customer Experience Team
- **KPIs**: Customer Lifetime Value, Segment Distribution, Churn Rate
- **Visuals**: Persona pie chart, CLV by segment bar chart, acquisition funnel

### 4. Operational Dashboard
- **Audience**: Branch Managers, Operations Team
- **KPIs**: Transaction Volume, Branch Performance, Support Ticket Resolution
- **Visuals**: Daily transaction heatmap, branch ranking table

## DAX Measures

### Core KPIs
```dax
Total Revenue = SUM(fact_transactions[amount])
Active Customers = DISTINCTCOUNT(dim_customers[customer_id])
Fraud Rate = DIVIDE([Fraud Cases], [Total Transactions], 0)
```

### Time Intelligence
```dax
Revenue YTD = TOTALYTD([Total Revenue], dim_calendar[full_date])
Revenue MoM Growth = DIVIDE([Total Revenue] - [Revenue PM], [Revenue PM], 0)
Revenue YoY Growth = DIVIDE([Total Revenue] - [Revenue PY], [Revenue PY], 0)
```

## Row-Level Security (RLS)
Branch managers are restricted to viewing only their branch's data via RLS roles defined on `dim_branches[branch_id]`.

## Enterprise Theme
A custom JSON theme (`enterprise_theme.json`) enforces consistent branding:
- **Primary**: `#1B3A5C` (Navy)
- **Secondary**: `#2E86AB` (Blue)
- **Accent**: `#F18F01` (Gold)
- **Font**: Segoe UI

## KPI Validation
A Python script (`validate_kpis.py`) confirmed **100% parity** between DAX measures and SQL Warehouse logic, ensuring dashboard accuracy.
