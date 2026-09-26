"""Report generation: markdown reports for loan default predictions."""

import os
import pandas as pd
from . import config


def generate_reports(
    comparison_df,
    cost_df,
    threshold_results,
    shap_results,
    risk_df,
    feature_selection_results,
    best_model_name,
):
    """Generate comprehensive markdown reports."""
    print("\n" + "=" * 70)
    print("  STEP 11: REPORT GENERATION")
    print("=" * 70)

    # --- Model Comparison Report ---
    report = "# Loan Default Prediction — Model Comparison Report\n\n"
    report += "## Performance & Calibration Summary\n\n"
    report += "| Model | F1 Score | ROC-AUC | PR-AUC | Brier Score (Calibration) |\n"
    report += "|-------|----------|---------|--------|-------------|\n"
    for _, row in comparison_df.iterrows():
        report += (
            f"| {row['model']} | {row['f1']:.4f} | {row['roc_auc']:.4f} | "
            f"{row['pr_auc']:.4f} | {row['brier_score']:.4f} |\n"
        )
    report += f"\n**Best Model (by PR-AUC):** {best_model_name}\n"

    with open(os.path.join(config.REPORTS_DIR, "model_comparison.md"), "w") as f:
        f.write(report)

    # --- Business Impact Report ---
    biz = "# Loan Default Prediction — Portfolio Impact Report\n\n"
    biz += f"## Portfolio Assumptions\n- Avg Loan Value: ${config.AVG_LOAN_AMOUNT:,}\n"
    biz += f"- Profit Margin (Good Loan): {config.PROFIT_MARGIN*100}%\n"
    biz += f"- Recovery Rate (Default): {config.RECOVERY_RATE*100}%\n"
    biz += f"- Manual Review Cost: ${config.REVIEW_COST:,}\n\n"
    biz += "## Impact by Model (Test Set Simulation)\n\n"
    biz += "| Model | Auto-Approve | Manual Review | Auto-Reject | Review Cost | Value Added vs Baseline |\n"
    biz += "|-------|--------------|---------------|-------------|-------------|-------------------------|\n"
    for _, row in cost_df.iterrows():
        biz += (
            f"| {row['model']} | {row['auto_approve_rate']*100:.1f}% | "
            f"{row['review_rate']*100:.1f}% | {row['auto_reject_rate']*100:.1f}% | "
            f"${row['review_costs']:,.0f} | ${row['value_added_vs_baseline']:,.0f} |\n"
        )

    with open(os.path.join(config.REPORTS_DIR, "business_impact.md"), "w") as f:
        f.write(biz)

    # --- Threshold & Risk Scoring Guide ---
    guide = "# Loan Default — Risk Scoring & Threshold Guide\n\n"
    guide += "## Decision Thresholds (Probabilities)\n"
    if threshold_results:
        guide += f"- **Auto-Approve Threshold:** < {threshold_results['auto_approve_thresh']:.4f} \n"
        guide += f"- **Auto-Reject Threshold:** >= {threshold_results['auto_reject_thresh']:.4f}\n"
        guide += f"- **Manual Review Range:** {threshold_results['auto_approve_thresh']:.4f} to {threshold_results['auto_reject_thresh']:.4f}\n\n"

    guide += "## Credit Risk Categories\n\n"
    guide += "| Risk Score (0-100) | Risk Category | Interpretation |\n"
    guide += "|--------------------|---------------|----------------|\n"
    guide += "| 0 - 9 | Very Low Risk | Prime borrower, low default likelihood |\n"
    guide += "| 10 - 24 | Low Risk | Standard borrower, acceptable risk |\n"
    guide += "| 25 - 49 | Medium Risk | Sub-prime, requires underwriting review |\n"
    guide += "| 50 - 79 | High Risk | High likelihood of default, strict conditions |\n"
    guide += "| 80 - 100 | Very High Risk | Critical default risk, decline |\n"

    with open(os.path.join(config.REPORTS_DIR, "risk_scoring_guide.md"), "w") as f:
        f.write(guide)

    # --- Executive Summary ---
    ex = "# Enterprise Loan Default Platform — Executive Summary\n\n"
    ex += f"## Overview\nThe platform evaluated **{len(comparison_df)} calibrated models** "
    ex += f"on a loan applicant dataset to predict default probabilities.\n\n"
    ex += f"## Technical Results\n"
    best = comparison_df.iloc[0]
    ex += f"- **Production Model:** {best['model']}\n"
    ex += f"- **PR-AUC:** {best['pr_auc']:.4f}\n"
    ex += f"- **ROC-AUC:** {best['roc_auc']:.4f}\n"
    ex += f"- **Brier Score (Calibration Error):** {best['brier_score']:.4f}\n\n"
    if len(cost_df) > 0:
        best_cost = cost_df.iloc[0]
        ex += f"## Business Impact\n"
        ex += f"- **Value Added (vs Approve-All Baseline):** ${best_cost['value_added_vs_baseline']:,.0f}\n"
        ex += f"- **Automation Rate:** {100 - best_cost['review_rate']*100:.1f}% (Auto-Approve + Auto-Reject)\n"
        ex += f"- **Manual Review Rate:** {best_cost['review_rate']*100:.1f}%\n\n"
    ex += "## Recommendations\n"
    ex += f"1. Deploy **{best['model']}** with probability calibration for credit scoring.\n"
    ex += "2. Implement multi-tier threshold routing to reduce underwriter workload.\n"
    ex += "3. Use SHAP global importance insights to update credit policies.\n"

    with open(os.path.join(config.REPORTS_DIR, "executive_summary.md"), "w") as f:
        f.write(ex)

    print(f"  Saved: 4 Markdown reports")
