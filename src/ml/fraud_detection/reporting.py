"""Report generation: markdown reports for all fraud detection outputs."""

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
    print("  STEP 12: REPORT GENERATION")
    print("=" * 70)

    # --- Model Comparison Report ---
    report = "# Fraud Detection — Model Comparison Report\n\n"
    report += "## Model Performance Summary\n\n"
    report += (
        "| Model | Accuracy | Precision | Recall | F1 | ROC-AUC | PR-AUC | MCC |\n"
    )
    report += (
        "|-------|----------|-----------|--------|----|---------|---------|----- |\n"
    )
    for _, row in comparison_df.iterrows():
        report += (
            f"| {row['model']} | {row['accuracy']:.4f} | {row['precision']:.4f} | "
            f"{row['recall']:.4f} | {row['f1']:.4f} | {row['roc_auc']:.4f} | "
            f"{row['pr_auc']:.4f} | {row['mcc']:.4f} |\n"
        )
    report += f"\n**Best Model (by F1):** {comparison_df.iloc[0]['model']}\n"
    report += f"\n**Production Model:** {best_model_name}\n"

    with open(os.path.join(config.REPORTS_DIR, "model_comparison.md"), "w") as f:
        f.write(report)
    print("  Saved: model_comparison.md")

    # --- Business Impact Report ---
    biz = "# Fraud Detection — Business Impact Report\n\n"
    biz += f"## Cost Assumptions\n- Avg fraud loss per missed case (FN): ${config.AVG_FRAUD_LOSS:,}\n"
    biz += (
        f"- Operational review cost per false alarm (FP): ${config.REVIEW_COST:,}\n\n"
    )
    biz += "## Cost Analysis by Model\n\n"
    biz += "| Model | Fraud Prevented | Missed Fraud Cost | False Alarm Cost | Net Savings | Review Workload |\n"
    biz += "|-------|-----------------|-------------------|------------------|-------------|------------------|\n"
    for _, row in cost_df.iterrows():
        biz += (
            f"| {row['model']} | ${row['fraud_losses_prevented']:,.0f} | "
            f"${row['missed_fraud_cost']:,.0f} | ${row['false_alarm_cost']:,.0f} | "
            f"${row['net_savings']:,.0f} | {row['review_workload']} |\n"
        )
    biz += f"\n**Recommended Production Model:** {cost_df.iloc[0]['model']}\n"
    biz += f"**Estimated Annual Net Savings:** ${cost_df.iloc[0]['net_savings']:,.0f}\n"

    with open(os.path.join(config.REPORTS_DIR, "business_impact.md"), "w") as f:
        f.write(biz)
    print("  Saved: business_impact.md")

    # --- Feature Importance Report ---
    feat = "# Fraud Detection — Feature Importance Report\n\n"
    if shap_results and "feature_importance" in shap_results:
        feat += "## SHAP Global Feature Importance\n\n"
        feat += "| Rank | Feature | Mean |SHAP| |\n"
        feat += "|------|---------|---------------|\n"
        for i, (fname, val) in enumerate(
            shap_results["feature_importance"].head(20).items(), 1
        ):
            feat += f"| {i} | {fname} | {val:.4f} |\n"

    if feature_selection_results:
        feat += "\n## Mutual Information Scores\n\n"
        if "mi_scores" in feature_selection_results:
            feat += "| Feature | MI Score |\n|---------|----------|\n"
            for fname, val in feature_selection_results["mi_scores"].head(15).items():
                feat += f"| {fname} | {val:.4f} |\n"

    with open(os.path.join(config.REPORTS_DIR, "feature_importance.md"), "w") as f:
        f.write(feat)
    print("  Saved: feature_importance.md")

    # --- Threshold & Risk Scoring Guide ---
    guide = "# Fraud Detection — Risk Scoring Guide\n\n"
    guide += "## Threshold Configuration\n"
    if threshold_results:
        guide += f"- **Optimal Threshold (Max F1):** {threshold_results['best_threshold']:.4f}\n"
        guide += f"- **High-Recall Threshold:** {threshold_results['high_recall_threshold']:.4f}\n\n"
    guide += "## Risk Bands\n\n"
    guide += "| Score Range | Risk Band | Recommended Action |\n"
    guide += "|-------------|-----------|--------------------|\n"
    guide += "| 0 - 24 | Low Risk | Approve Transaction |\n"
    guide += "| 25 - 49 | Medium Risk | Manual Investigation |\n"
    guide += "| 50 - 74 | High Risk | Temporary Hold |\n"
    guide += "| 75 - 100 | Critical Risk | Block / Escalate |\n"

    with open(os.path.join(config.REPORTS_DIR, "risk_scoring_guide.md"), "w") as f:
        f.write(guide)
    print("  Saved: risk_scoring_guide.md")

    # --- Executive Summary ---
    ex = "# Fraud Detection Platform — Executive Summary\n\n"
    ex += f"## Overview\nThe Enterprise Fraud Detection Platform evaluated **{len(comparison_df)} models** "
    ex += f"on the banking customer dataset of **10,000 customers**.\n\n"
    ex += f"## Key Results\n"
    best = comparison_df.iloc[0]
    ex += f"- **Best Model:** {best['model']}\n"
    ex += f"- **F1 Score:** {best['f1']:.4f}\n"
    ex += f"- **ROC-AUC:** {best['roc_auc']:.4f}\n"
    ex += f"- **Precision:** {best['precision']:.4f} | **Recall:** {best['recall']:.4f}\n\n"
    if len(cost_df) > 0:
        best_cost = cost_df.iloc[0]
        ex += f"## Business Impact\n"
        ex += f"- **Net Savings:** ${best_cost['net_savings']:,.0f}\n"
        ex += f"- **Fraud Prevented:** ${best_cost['fraud_losses_prevented']:,.0f}\n"
        ex += f"- **Review Workload:** {best_cost['review_workload']} cases\n\n"
    ex += "## Recommendations\n"
    ex += f"1. Deploy **{best['model']}** as the production fraud detection model.\n"
    ex += "2. Use the optimized threshold for decision-making.\n"
    ex += "3. Monitor model drift monthly and retrain quarterly.\n"
    ex += "4. Integrate SHAP explanations into analyst dashboards.\n"

    with open(os.path.join(config.REPORTS_DIR, "executive_summary.md"), "w") as f:
        f.write(ex)
    print("  Saved: executive_summary.md")

    print(f"\n  Total reports generated: 5")
