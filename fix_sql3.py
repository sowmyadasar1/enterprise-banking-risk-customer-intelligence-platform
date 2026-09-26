import os

base_dir = "/Users/sowmyadasari/Downloads/Enterprise Banking Risk & Customer Intelligence Platform/sql/analytics"

replacements = {
    "02_transaction_analytics/01_monthly_trends_moving_avg.sql": [
        ("f.date_id = d.date_id", "f.transaction_date = d.full_date"),
        ("f.date_id", "f.transaction_date"),
    ],
    "02_transaction_analytics/02_peak_hours.sql": [
        ("transaction_type_id_id", "transaction_type_id")
    ],
    "03_revenue_analytics/01_revenue_growth.sql": [
        ("f.date_id = d.date_id", "f.transaction_date = d.full_date"),
        ("f.date_id", "f.transaction_date"),
    ],
    "03_revenue_analytics/02_revenue_by_branch.sql": [
        ("f.is_successful", "f.status = 'Success'")
    ],
    "04_loan_analytics/02_late_payments.sql": [
        ("f.payment_amount", "f.amount_paid"),
        ("payment_amount", "amount_paid"),
    ],
    "05_fraud_analytics/02_fraud_by_dimension.sql": [
        ("t.transaction_key", "t.transaction_id"),
        ("transaction_key", "transaction_id"),
    ],
    "06_marketing_analytics/01_campaign_roi.sql": [
        ("r.campaign_key", "r.campaign_id"),
        ("campaign_key", "campaign_id"),
    ],
    "06_marketing_analytics/02_segment_performance.sql": [
        ("m.revenue_generated", "(CAST(m.converted AS INTEGER) * 100)")
    ],
    "07_branch_analytics/01_branch_ranking.sql": [
        ("region", "region_id"),
        ("region_id_id", "region_id"),
    ],
    "10_executive_kpis/01_executive_scorecard.sql": [
        ("transaction_type", "transaction_type_id")
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
            content = content.replace(rule[0], rule[1])

        with open(file_path, "w") as f:
            f.write(content)
        print(f"Processed: {rel_path}")


if __name__ == "__main__":
    process_files()
