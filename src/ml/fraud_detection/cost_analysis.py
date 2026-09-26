"""Business cost analysis: estimate financial impact of model decisions."""

import numpy as np
import pandas as pd
from . import config


def run_cost_analysis(comparison_df, trained_models, X_test, y_test):
    """Estimate business costs for each model's predictions."""
    print("\n" + "=" * 70)
    print("  STEP 8: BUSINESS COST ANALYSIS")
    print("=" * 70)
    print(f"  Assumptions:")
    print(f"    Avg fraud loss (FN cost):  ${config.AVG_FRAUD_LOSS:,}")
    print(f"    Review cost (FP cost):     ${config.REVIEW_COST:,}")

    cost_rows = []
    for _, row in comparison_df.iterrows():
        name = row["model"]
        tp, fp, tn, fn = int(row["tp"]), int(row["fp"]), int(row["tn"]), int(row["fn"])

        fn_cost = fn * config.AVG_FRAUD_LOSS
        fp_cost = fp * config.REVIEW_COST
        total_cost = fn_cost + fp_cost
        fraud_prevented = tp * config.AVG_FRAUD_LOSS
        net_savings = fraud_prevented - total_cost

        cost_rows.append(
            {
                "model": name,
                "true_positives": tp,
                "false_positives": fp,
                "false_negatives": fn,
                "fraud_losses_prevented": fraud_prevented,
                "missed_fraud_cost": fn_cost,
                "false_alarm_cost": fp_cost,
                "total_cost": total_cost,
                "net_savings": net_savings,
                "review_workload": fp + tp,
            }
        )

    cost_df = pd.DataFrame(cost_rows).sort_values("net_savings", ascending=False)

    print("\n  === COST COMPARISON ===")
    for _, row in cost_df.iterrows():
        print(f"\n  {row['model']}:")
        print(f"    Fraud prevented:   ${row['fraud_losses_prevented']:>12,.0f}")
        print(f"    Missed fraud cost: ${row['missed_fraud_cost']:>12,.0f}")
        print(f"    False alarm cost:  ${row['false_alarm_cost']:>12,.0f}")
        print(f"    Net savings:       ${row['net_savings']:>12,.0f}")
        print(f"    Review workload:   {row['review_workload']:>6} cases")

    best = cost_df.iloc[0]
    print(f"\n  >>> RECOMMENDED MODEL (business): {best['model']}")
    print(f"      Net savings: ${best['net_savings']:,.0f}")

    return cost_df
