"""Business cost analysis: financial impact and portfolio risk estimation."""

import numpy as np
import pandas as pd
from . import config


def run_cost_analysis(comparison_df, trained_models, X_test, y_test, thresholds):
    """Estimate portfolio financial impact based on decision thresholds."""
    print("\n" + "=" * 70)
    print("  STEP 7: BUSINESS COST ANALYSIS")
    print("=" * 70)

    avg_loan = config.AVG_LOAN_AMOUNT
    profit = avg_loan * config.PROFIT_MARGIN
    loss = avg_loan * (1 - config.RECOVERY_RATE)
    rev_cost = config.REVIEW_COST

    print(f"  Assumptions:")
    print(f"    Avg Loan Value:    ${avg_loan:,.0f}")
    print(f"    Profit per Good:   ${profit:,.0f} ({config.PROFIT_MARGIN*100:.0f}%)")
    print(f"    Loss per Default:  ${loss:,.0f} ({100-config.RECOVERY_RATE*100:.0f}%)")
    print(f"    Manual Review Cost:${rev_cost:,.0f}")

    auto_app_th = thresholds.get("auto_approve_thresh", 0.5)
    auto_rej_th = thresholds.get("auto_reject_thresh", 0.5)

    cost_rows = []
    for _, row in comparison_df.iterrows():
        name = row["model"]
        model = trained_models[name]
        try:
            y_proba = model.predict_proba(X_test.fillna(0))[:, 1]
        except:
            continue

        # Simulate decisions
        auto_app = y_proba < auto_app_th
        auto_rej = y_proba >= auto_rej_th
        review = ~auto_app & ~auto_rej

        # Assume Manual Reviews are perfectly accurate for now to estimate max value,
        # but realistically they reject bad and approve good at the cost of the review fee.
        # Let's say review correctly identifies truth.

        # Financials from Auto-Approve (We get profit for true negatives, loss for false negatives)
        aa_profit = sum((auto_app) & (y_test == 0)) * profit
        aa_loss = sum((auto_app) & (y_test == 1)) * loss

        # Financials from Auto-Reject (We avoid loss, but miss profit from false positives)
        missed_profit = sum((auto_rej) & (y_test == 0)) * profit
        avoided_loss = sum((auto_rej) & (y_test == 1)) * loss

        # Financials from Review
        review_cost_total = sum(review) * rev_cost
        rev_profit = sum((review) & (y_test == 0)) * profit
        rev_avoided_loss = sum((review) & (y_test == 1)) * loss  # We avoid this loss

        net_value = (aa_profit - aa_loss) + rev_profit - review_cost_total

        # Baseline: Approve everyone
        baseline_profit = sum(y_test == 0) * profit
        baseline_loss = sum(y_test == 1) * loss
        baseline_net = baseline_profit - baseline_loss

        value_added = net_value - baseline_net

        cost_rows.append(
            {
                "model": name,
                "auto_approve_rate": sum(auto_app) / len(y_test),
                "auto_reject_rate": sum(auto_rej) / len(y_test),
                "review_rate": sum(review) / len(y_test),
                "net_portfolio_value": net_value,
                "value_added_vs_baseline": value_added,
                "review_costs": review_cost_total,
                "missed_good_loans_cost": missed_profit,
            }
        )

    cost_df = pd.DataFrame(cost_rows).sort_values(
        "net_portfolio_value", ascending=False
    )

    print("\n  === PORTFOLIO IMPACT (1,500 test applicants) ===")
    for _, row in cost_df.iterrows():
        print(f"\n  {row['model']}:")
        print(f"    Auto-Approve Rate: {row['auto_approve_rate']*100:.1f}%")
        print(f"    Review Rate:       {row['review_rate']*100:.1f}%")
        print(f"    Auto-Reject Rate:  {row['auto_reject_rate']*100:.1f}%")
        print(f"    Review Costs:      ${row['review_costs']:,.0f}")
        print(f"    Net Value:         ${row['net_portfolio_value']:,.0f}")
        print(f"    Value Added:       ${row['value_added_vs_baseline']:,.0f}")

    best = cost_df.iloc[0]
    print(f"\n  >>> RECOMMENDED MODEL (business): {best['model']}")
    print(f"      Net Portfolio Value: ${best['net_portfolio_value']:,.0f}")

    return cost_df
