import os
import re

base_dir = "/Users/sowmyadasari/Downloads/Enterprise Banking Risk & Customer Intelligence Platform/sql/analytics"

replacements = {
    "01_customer_analytics/01_high_value_customers.sql": [
        ("c.customer_segment", "c.customer_type"),
        ("customer_segment", "customer_type"),
        ("WHERE a.is_active = true", "WHERE a.account_status = 'Active'")
    ],
    "01_customer_analytics/02_churn_risk_analysis.sql": [
        ("a.is_active", "a.account_status"),
        ("a.closed_date", "a.close_date"),
        ("is_active = false", "account_status = 'Closed'"),
        ("closed_date", "close_date")
    ],
    "01_customer_analytics/03_segment_revenue.sql": [
        ("c.customer_segment", "c.customer_type"),
        ("customer_segment", "customer_type"),
        ("f.fee_amount", "0 AS fee_amount"),
        ("fee_amount", "0"),
        ("f.date_id = d.date_id", "f.transaction_date = d.full_date"),
        ("f.is_successful = true", "f.status = 'Success'"),
        ("f.transaction_amount", "f.amount"),
        ("transaction_amount", "amount")
    ],
    "02_transaction_analytics/01_monthly_trends_moving_avg.sql": [
        ("d.year_month", "d.year || '-' || printf('%02d', d.month)"),
        ("year_month", "d.year || '-' || printf('%02d', d.month)"),
        ("f.transaction_amount", "f.amount"),
        ("transaction_amount", "amount")
    ],
    "02_transaction_analytics/02_peak_hours.sql": [
        ("EXTRACT(HOUR FROM f.transaction_timestamp)", "CAST(strftime('%H', f.transaction_timestamp) AS INTEGER)"),
        ("f.transaction_amount", "f.amount"),
        ("transaction_amount", "amount"),
        ("f.is_successful = true", "f.status = 'Success'")
    ],
    "02_transaction_analytics/03_merchant_performance.sql": [
        ("f.transaction_amount", "f.amount"),
        ("transaction_amount", "amount"),
        ("f.is_successful = true", "f.status = 'Success'"),
        ("is_successful", "status = 'Success'")
    ],
    "03_revenue_analytics/01_revenue_growth.sql": [
        ("d.year_month", "d.year || '-' || printf('%02d', d.month)"),
        ("year_month", "d.year || '-' || printf('%02d', d.month)"),
        ("f.fee_amount", "0"),
        ("fee_amount", "0")
    ],
    "03_revenue_analytics/02_revenue_by_branch.sql": [
        ("b.region", "b.region_id"),
        ("f.fee_amount", "0"),
        ("fee_amount", "0")
    ],
    "04_loan_analytics/01_portfolio_analysis.sql": [
        ("f.outstanding_balance", "f.loan_amount"),
        ("outstanding_balance", "loan_amount"),
        ("f.loan_key", "f.loan_id"),
        ("loan_key", "loan_id")
    ],
    "04_loan_analytics/02_late_payments.sql": [
        ("f.loan_key", "f.loan_id"),
        ("loan_key", "loan_id"),
        ("f.due_date", "f.end_date"),
        ("due_date", "end_date")
    ],
    "05_fraud_analytics/01_fraud_patterns.sql": [
        ("EXTRACT(EPOCH FROM (transaction_timestamp - prev_transaction_time))/60", "(strftime('%s', transaction_timestamp) - strftime('%s', prev_transaction_time)) / 60"),
        ("transaction_amount", "amount"),
        ("account_key", "account_id")
    ],
    "05_fraud_analytics/02_fraud_by_dimension.sql": [
        ("m.merchant_region", "m.country"),
        ("f.is_fraud = true", "f.transaction_id IN (SELECT transaction_id FROM fact_fraud)"),
        ("f.is_fraud", "(f.transaction_id IN (SELECT transaction_id FROM fact_fraud))")
    ],
    "06_marketing_analytics/01_campaign_roi.sql": [
        ("c.campaign_cost", "c.budget"),
        ("campaign_cost", "budget"),
        ("c.channel", "r.channel"),
        ("dim_campaign.channel", "fact_marketing_responses.channel")
    ],
    "06_marketing_analytics/02_segment_performance.sql": [
        ("c.customer_segment", "c.customer_type"),
        ("customer_segment", "customer_type"),
        ("r.risk_rating", "c.risk_rating")
    ],
    "07_branch_analytics/01_branch_ranking.sql": [
        ("CURRENT_DATE - INTERVAL '1 year'", "date('now', '-1 year')"),
        ("b.region", "b.region_id")
    ],
    "08_risk_analytics/01_risk_distribution.sql": [
        ("r.risk_score_band", "r.risk_category"),
        ("c.risk_id", "c.risk_rating"),
        ("risk_id", "risk_rating")
    ],
    "09_operations/01_ticket_resolution.sql": [
        ("EXTRACT(EPOCH FROM (t.resolved_at - t.created_at))/3600", "(strftime('%s', t.resolved_at) - strftime('%s', t.created_at)) / 3600.0"),
        ("JOIN\n    dim_employee e ON t.employee_id = e.employee_id", ""),
        ("e.employee_name,", ""),
        ("e.department,", ""),
        ("e.employee_name", ""),
        ("e.department", ""),
        ("e.employee_id", "t.employee_id")
    ],
    "10_executive_kpis/01_executive_scorecard.sql": [
        (r"DATE_TRUNC\('month',\s*([a-zA-Z0-9_.]+)\)", r"strftime('%Y-%m', \1)"),
        ("is_fraud", "(transaction_id IN (SELECT transaction_id FROM fact_fraud))"),
        ("transaction_amount", "amount")
    ],
    "10_executive_kpis/kpi_views.sql": [
        (r"CREATE OR REPLACE VIEW", "DROP VIEW IF EXISTS {view_name};\nCREATE VIEW {view_name} AS"),
        ("EXTRACT(EPOCH FROM (MAX(t.transaction_date) - MIN(t.transaction_date))) / 86400", "(julianday(MAX(t.transaction_date)) - julianday(MIN(t.transaction_date)))"),
        ("DATE_TRUNC('month', t.transaction_date)", "strftime('%Y-%m', t.transaction_date)"),
        ("DATE_TRUNC('month', c.created_date)", "strftime('%Y-%m', c.join_date)"),
        ("DATE_TRUNC('month', m.campaign_date)", "strftime('%Y-%m', m.start_date)"),
        ("DATE_TRUNC('month', transaction_date)", "strftime('%Y-%m', transaction_date)"),
        ("INTERVAL '1 month'", "'+1 month'"),
        ("c.segment", "c.customer_type"),
        ("fact_marketing_campaigns", "dim_campaign"),
        ("m.campaign_spend", "m.budget"),
        ("c.created_date", "c.join_date"),
        ("m.campaign_date", "m.start_date"),
        ("t.transaction_amount", "t.amount"),
        ("transaction_amount", "amount")
    ]
}

def process_files():
    for rel_path, rules in replacements.items():
        file_path = os.path.join(base_dir, rel_path)
        if not os.path.exists(file_path):
            print(f"Not found: {file_path}")
            continue
            
        with open(file_path, 'r') as f:
            content = f.read()
            
        for rule in rules:
            if rel_path == "10_executive_kpis/kpi_views.sql" and rule[0] == r"CREATE OR REPLACE VIEW":
                content = re.sub(r'CREATE OR REPLACE VIEW\s+([a-zA-Z0-9_]+)\s+AS', r'DROP VIEW IF EXISTS \1;\nCREATE VIEW \1 AS', content, flags=re.IGNORECASE)
            elif "DATE_TRUNC" in rule[0]:
                content = re.sub(rule[0], rule[1], content)
            else:
                content = content.replace(rule[0], rule[1])
                
        with open(file_path, 'w') as f:
            f.write(content)
        print(f"Processed: {rel_path}")

if __name__ == '__main__':
    process_files()
