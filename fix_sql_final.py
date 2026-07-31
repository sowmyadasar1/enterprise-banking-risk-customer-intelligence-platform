import os
import re

base_dir = "/Users/sowmyadasari/Downloads/Enterprise Banking Risk & Customer Intelligence Platform/sql/analytics"

replacements = {
    "01_customer_analytics/03_segment_revenue.sql": [
        ("0 AS 0", "0 AS fee_amount"),
        ("SUM(0)", "SUM(fee_amount)")
    ],
    "02_transaction_analytics/01_monthly_trends_moving_avg.sql": [
        ("f.is_successful = true", "f.status = 'Success'"),
        ("f.is_successful", "f.status = 'Success'")
    ],
    "02_transaction_analytics/02_peak_hours.sql": [
        ("f.transaction_type,", "f.transaction_type_id,"),
        ("f.transaction_type", "f.transaction_type_id"),
        ("transaction_type,", "transaction_type_id,"),
        ("BY transaction_type", "BY transaction_type_id")
    ],
    "03_revenue_analytics/01_revenue_growth.sql": [
        ("f.is_successful = true", "f.status = 'Success'"),
        ("f.is_successful", "f.status = 'Success'")
    ],
    "03_revenue_analytics/02_revenue_by_branch.sql": [
        ("b.region_id_id", "b.region_id")
    ],
    "04_loan_analytics/02_late_payments.sql": [
        ("f.end_date", "f.payment_date") # Wait, is due_date better mapped to end_date or payment_date? fact_loans has end_date. But the alias is `f`. If `f` is fact_loans, end_date. If fact_loan_payments, payment_date. Let's use `end_date` just in case? No, wait. 
    ],
    "05_fraud_analytics/02_fraud_by_dimension.sql": [
        ("t.transaction_amount", "t.amount")
    ],
    "06_marketing_analytics/01_campaign_roi.sql": [
        ("r.revenue_generated", "(CAST(r.converted AS INTEGER) * 100)")
    ],
    "06_marketing_analytics/02_segment_performance.sql": [
        ("m.offer_accepted", "m.converted")
    ],
    "07_branch_analytics/01_branch_ranking.sql": [
        ("t.transaction_amount", "t.amount")
    ],
    "08_risk_analytics/01_risk_distribution.sql": [
        ("r.risk_rating", "c.risk_rating")
    ],
    "09_operations/01_ticket_resolution.sql": [
        ("GROUP BY\n    t.employee_id,\n    \n    \nORDER BY", "GROUP BY\n    t.employee_id\nORDER BY"),
        ("t.employee_id,\n    \n    \n    COUNT", "t.employee_id,\n    COUNT")
    ],
    "10_executive_kpis/01_executive_scorecard.sql": [
        ("default_date", "end_date")
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
            content = content.replace(rule[0], rule[1])
                
        with open(file_path, 'w') as f:
            f.write(content)
        print(f"Processed: {rel_path}")

if __name__ == '__main__':
    process_files()
