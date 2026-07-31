# Dashboard Layout Specifications

The Enterprise Banking BI Platform comprises 7 highly interactive pages. Navigation is handled via a persistent left-hand collapsible menu (using bookmarks and buttons).

## 1. Executive Dashboard (Landing Page)
**Target Audience**: C-Suite, VPs
**Visuals**:
- **Top Ribbon (Cards)**: Total Revenue, Total Customers, Total Fraud Loss, Overall Risk Score.
- **Top Left (Line Chart)**: Revenue Trends (Actual vs. Forecast).
- **Top Right (Decomposition Tree)**: Root Cause Analysis of Revenue by Region -> Branch -> Product.
- **Bottom Left (Map)**: Geographic heatmap of branch performance (Revenue vs Target).
- **Bottom Right (Matrix)**: Executive KPI Summary table with sparklines.

## 2. Fraud Dashboard
**Target Audience**: Fraud Investigators, Risk Managers
**Visuals**:
- **Cards**: Fraud Rate, Total Suspicious Transactions, YTD Financial Loss.
- **Top Left (Area Chart)**: Fraud volume trend over time.
- **Top Right (Donut Chart)**: Fraud by Type (e.g., Identity Theft, Card Skimming).
- **Bottom (Table with Drill-through)**: Suspicious Transactions log. 
  - *Drill-through*: Right-click a transaction to view "Transaction Detail Page".

## 3. Loan Dashboard
**Target Audience**: Credit Risk Team, Loan Officers
**Visuals**:
- **Cards**: Total Outstanding Loans, Approval Rate, Default Rate.
- **Top Left (Funnel Chart)**: Loan Approval Pipeline (Application -> Review -> Approved -> Funded).
- **Top Right (Clustered Column Chart)**: Default Rate by Risk Category and Loan Type.
- **Bottom (Scatter Plot)**: Loan Size vs Interest Rate (Color coded by Default Status).

## 4. Customer Dashboard
**Target Audience**: Marketing Team, Product Managers
**Visuals**:
- **Cards**: Customer Lifetime Value, Retention Rate, Churn Rate.
- **Top Left (Treemap)**: Customer Segments distribution (driven by ML Phase 7C).
- **Top Right (Gauge Chart)**: Net Promoter Score (NPS) or Customer Satisfaction.
- **Bottom (Ribbon Chart)**: Product ownership transitions over time.

## 5. Revenue Dashboard
**Target Audience**: Finance Team
**Visuals**:
- **Cards**: MTD Revenue, YoY Growth %, Profit Margin.
- **Top Left (Waterfall Chart)**: Revenue variance (YoY Growth breakdown by Region).
- **Top Right (Line & Clustered Column)**: Monthly Revenue vs Rolling 12-Month Average.
- **Bottom (Matrix)**: Detailed branch-level P&L statement with drill-down to Account level.

## 6. Risk Dashboard
**Target Audience**: Chief Risk Officer, Compliance
**Visuals**:
- **Cards**: High-Risk Customers count, Average Credit Score, Portfolio Value at Risk.
- **Top (Heatmap/Matrix)**: Risk distribution by Region and Customer Persona.
- **Bottom Left (Line Chart)**: Trend of average risk scores over the last 36 months.
- **Bottom Right (Bar Chart)**: Count of customers in each credit score band.

## 7. Marketing & Operations Dashboard
**Target Audience**: Campaign Managers, Customer Support Leads
**Visuals**:
- **Cards**: Campaign Conversion Rate, Avg Support Resolution Time, Open Tickets.
- **Top Left (Scatter Plot)**: Marketing Spend vs Conversion Rate (by Campaign).
- **Top Right (Line Chart)**: Daily Support Ticket inflow vs Resolution rate.
- **Bottom (Table)**: Cross-sell opportunities identified by the ML Recommendation engine.
