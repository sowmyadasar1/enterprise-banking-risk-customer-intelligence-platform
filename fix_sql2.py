import os
import re

base_dir = "/Users/sowmyadasari/Downloads/Enterprise Banking Risk & Customer Intelligence Platform/sql/analytics"

# Dictionary mapping file paths to a list of (search_pattern, replacement)
replacements = {
    "01_customer_analytics/01_high_value_customers.sql": [
        (r"c\.customer_segment", r"c.customer_type"),
        (r"(?<!\.)customer_segment", r"customer_type"),
        (r"a\.is_active = true", r"a.account_status = 'Active'"),
    ],
    "01_customer_analytics/02_churn_risk_analysis.sql": [
        (r"a\.is_active", r"a.account_status"),
        (r"is_active = false", r"account_status != 'Active'"),
        (r"a\.closed_date", r"a.close_date"),
        (r"MAX\(closed_date\)", r"MAX(close_date)"),
    ],
    "01_customer_analytics/03_segment_revenue.sql": [
        (r"c\.customer_segment", r"c.customer_type"),
        (r"(?<!\.)customer_segment", r"customer_type"),
        (r"f\.transaction_amount", r"f.amount"),
        (r"SUM\(transaction_amount\)", r"SUM(amount)"),
        (r"f\.fee_amount", r"0 AS fee_amount"),
        (r"f\.date_id = d\.date_id", r"f.transaction_date = d.full_date"),
        (r"f\.is_successful = true", r"f.status = 'Success'"),
    ],
    "02_transaction_analytics/01_monthly_trends_moving_avg.sql": [
        (r"d\.year_month", r"d.year || '-' || printf('%02d', d.month)"),
        (r"f\.transaction_amount", r"f.amount"),
        (r"SUM\(transaction_amount\)", r"SUM(amount)"),
        (r"f\.is_successful = true", r"f.status = 'Success'"),
    ],
    "02_transaction_analytics/02_peak_hours.sql": [
        (
            r"EXTRACT\(HOUR FROM f\.transaction_timestamp\)",
            r"CAST(strftime('%H', f.transaction_timestamp) AS INTEGER)",
        ),
        (r",\s+FROM", r"\n    FROM"),  # Fix trailing comma
        (r"f\.transaction_type", r"f.transaction_type_id"),
        (r"(?<!\.)transaction_type", r"transaction_type_id"),
        (r"f\.transaction_amount", r"f.amount"),
        (r"SUM\(transaction_amount\)", r"SUM(amount)"),
        (r"f\.is_successful = true", r"f.status = 'Success'"),
    ],
    "02_transaction_analytics/03_merchant_performance.sql": [
        (r"f\.transaction_amount", r"f.amount"),
        (r"SUM\(transaction_amount\)", r"SUM(amount)"),
        (r"f\.is_successful = true", r"f.status = 'Success'"),
    ],
    "03_revenue_analytics/01_revenue_growth.sql": [
        (r"d\.year_month", r"d.year || '-' || printf('%02d', d.month)"),
        (r"f\.fee_amount", r"0 AS fee_amount"),
        (r"f\.is_successful = true", r"f.status = 'Success'"),
    ],
    "03_revenue_analytics/02_revenue_by_branch.sql": [
        (r"b\.region\b", r"b.region_id"),
        (r"f\.fee_amount", r"0 AS fee_amount"),
    ],
    "04_loan_analytics/01_portfolio_analysis.sql": [
        (r"f\.outstanding_balance", r"f.loan_amount"),
        (r"SUM\(outstanding_balance\)", r"SUM(loan_amount)"),
        (r"f\.loan_key", r"f.loan_id"),
    ],
    "04_loan_analytics/02_late_payments.sql": [
        (r"f\.loan_key", r"f.loan_id"),
        (r"f\.due_date", r"f.end_date"),
    ],
    "05_fraud_analytics/01_fraud_patterns.sql": [
        (
            r"EXTRACT\(EPOCH FROM \(transaction_timestamp - prev_transaction_time\)\)/60",
            r"(strftime('%s', transaction_timestamp) - strftime('%s', prev_transaction_time)) / 60",
        ),
        (r"transaction_amount", r"amount"),
        (r"account_key", r"account_id"),
        (r",\s+FROM", r"\n    FROM"),  # Trailing comma
    ],
    "05_fraud_analytics/02_fraud_by_dimension.sql": [
        (r"m\.merchant_region", r"m.country"),
        (
            r"f\.is_fraud = true",
            r"f.transaction_id IN (SELECT transaction_id FROM fact_fraud)",
        ),
        (r"t\.transaction_amount", r"t.amount"),  # If alias is t
    ],
    "06_marketing_analytics/01_campaign_roi.sql": [
        (r"c\.campaign_cost", r"c.budget"),
        (r"c\.channel", r"r.channel"),
        (
            r"r\.revenue_generated",
            r"(CAST(r.converted AS INTEGER) * 100)",
        ),  # mock revenue
        (r"campaign_key", r"campaign_id"),  # fix join key just in case
    ],
    "06_marketing_analytics/02_segment_performance.sql": [
        (r"c\.customer_segment", r"c.customer_type"),
        (r"(?<!\.)customer_segment", r"customer_type"),
        (r"r\.risk_rating", r"c.risk_rating"),
        (r"m\.offer_accepted = true", r"m.converted = 1"),
    ],
    "07_branch_analytics/01_branch_ranking.sql": [
        (r"CURRENT_DATE - INTERVAL '1 year'", r"date('now', '-1 year')"),
        (r"b\.region", r"b.region_id"),
        (r"t\.transaction_amount", r"t.amount"),
    ],
    "08_risk_analytics/01_risk_distribution.sql": [
        (r"r\.risk_score_band", r"r.risk_category"),
        (r"r\.risk_rating", r"c.risk_rating"),
        (r"c\.risk_id", r"c.risk_rating"),  # Depends on how it was originally
    ],
    "09_operations/01_ticket_resolution.sql": [
        (
            r"AVG\(EXTRACT\(EPOCH FROM \(t\.resolved_at - t\.created_at\)\)/3600\)",
            r"AVG((strftime('%s', t.resolved_at) - strftime('%s', t.created_at)) / 3600.0)",
        ),
        (
            r"MIN\(EXTRACT\(EPOCH FROM \(t\.resolved_at - t\.created_at\)\)/3600\)",
            r"MIN((strftime('%s', t.resolved_at) - strftime('%s', t.created_at)) / 3600.0)",
        ),
        (
            r"MAX\(EXTRACT\(EPOCH FROM \(t\.resolved_at - t\.created_at\)\)/3600\)",
            r"MAX((strftime('%s', t.resolved_at) - strftime('%s', t.created_at)) / 3600.0)",
        ),
        (r"JOIN\s+dim_employee\s+e\s+ON\s+t\.employee_id\s+=\s+e\.employee_id", r""),
        (r"e\.employee_name,", r""),
        (r"e\.department,", r""),
        (r"e\.employee_id", r"t.employee_id"),
        (
            r"GROUP BY\n\s+t\.employee_id,\n\s+e\.employee_name,\n\s+e\.department",
            r"GROUP BY t.employee_id",
        ),  # Better GROUP BY replace
    ],
    "10_executive_kpis/01_executive_scorecard.sql": [
        (r"DATE_TRUNC\('month',\s*([a-zA-Z0-9_.]+)\)", r"strftime('%Y-%m', \1)"),
        (
            r"is_fraud\s*=\s*TRUE",
            r"transaction_id IN (SELECT transaction_id FROM fact_fraud)",
        ),
        (
            r"\(transaction_id IN \(SELECT transaction_id FROM fact_fraud\)\) = TRUE",
            r"transaction_id IN (SELECT transaction_id FROM fact_fraud)",
        ),
        (r"default_date", r"end_date"),
        (
            r"transaction_type = 'Deposit'",
            r"transaction_type_id = 1",
        ),  # assuming Deposit is an ID or it was already correct?
    ],
    "10_executive_kpis/kpi_views.sql": [
        (
            r"CREATE OR REPLACE VIEW\s+([a-zA-Z0-9_]+)\s+AS",
            r"DROP VIEW IF EXISTS \1;\nCREATE VIEW \1 AS",
        ),
        (
            r"EXTRACT\(EPOCH FROM \(MAX\(t\.transaction_date\) - MIN\(t\.transaction_date\)\)\) / 86400",
            r"(julianday(MAX(t.transaction_date)) - julianday(MIN(t.transaction_date)))",
        ),
        (r"DATE_TRUNC\('month',\s*([a-zA-Z0-9_.]+)\)", r"strftime('%Y-%m', \1)"),
        (r"INTERVAL '1 month'", r"'+1 month'"),
        (r"c\.segment", r"c.customer_type"),
        (r"fact_marketing_campaigns", r"dim_campaign"),
        (r"m\.campaign_spend", r"m.budget"),
        (r"c\.created_date", r"c.join_date"),
        (r"m\.campaign_date", r"m.start_date"),
        (r"t\.transaction_amount", r"t.amount"),
    ],
}


def process_files():
    for rel_path, rules in replacements.items():
        file_path = os.path.join(base_dir, rel_path)
        if not os.path.exists(file_path):
            print(f"Not found: {file_path}")
            continue

        with open(file_path, "r") as f:
            content = f.read()

        for rule in rules:
            content = re.sub(rule[0], rule[1], content, flags=re.IGNORECASE)

        with open(file_path, "w") as f:
            f.write(content)
        print(f"Processed: {rel_path}")


if __name__ == "__main__":
    process_files()
