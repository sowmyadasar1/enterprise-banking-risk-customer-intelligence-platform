"""Report generation for forecasting outputs."""
import os
from . import config

def generate_reports(analysis_results, eval_results, scenarios):
    print("\n" + "="*70)
    print("  STEP 9: REPORT GENERATION")
    print("="*70)

    # 1. Executive Summary
    summary_path = os.path.join(config.REPORTS_DIR, 'executive_summary.md')
    with open(summary_path, 'w') as f:
        f.write("# Forecasting Platform — Executive Summary\n\n")
        f.write("## 90-Day Outlook (Base Case)\n")
        for target, scen_dict in scenarios.items():
            f.write(f"- **{target.replace('_', ' ').title()}**: {scen_dict['Base Case'].sum():,.2f}\n")
            
        f.write("\n## Scenario Planning\n")
        for target, scen_dict in scenarios.items():
            f.write(f"### {target.replace('_', ' ').title()}\n")
            f.write(f"- Optimistic: {scen_dict['Optimistic'].sum():,.2f}\n")
            f.write(f"- Base Case: {scen_dict['Base Case'].sum():,.2f}\n")
            f.write(f"- Conservative: {scen_dict['Conservative'].sum():,.2f}\n")
            f.write(f"- Severe Slowdown: {scen_dict['Severe Slowdown'].sum():,.2f}\n\n")

    # 2. Model Evaluation Report
    eval_path = os.path.join(config.REPORTS_DIR, 'model_evaluation.md')
    with open(eval_path, 'w') as f:
        f.write("# Forecasting Model Evaluation\n\n")
        for target, res in eval_results.items():
            f.write(f"## {target.replace('_', ' ').title()}\n")
            f.write("| Model | MAE | RMSE | MAPE |\n")
            f.write("|---|---|---|---|\n")
            for m, metrics in res.items():
                f.write(f"| {m.upper()} | {metrics['mae']:.2f} | {metrics['rmse']:.2f} | {metrics['mape']:.2f}% |\n")
            f.write("\n")

    # 3. Statistical Analysis Report
    stat_path = os.path.join(config.REPORTS_DIR, 'statistical_analysis.md')
    with open(stat_path, 'w') as f:
        f.write("# Time Series Statistical Analysis\n\n")
        for target, res in analysis_results.items():
            f.write(f"## {target.replace('_', ' ').title()}\n")
            f.write(f"- **Stationary (ADF)**: {res['is_stationary']} (p-value: {res['adf_p_value']:.4f})\n")
            f.write(f"- **Trend Strength**: {res['trend_strength']:.1%}\n")
            f.write(f"- **Seasonal Strength**: {res['seasonal_strength']:.1%}\n")
            f.write(f"- **Autocorrelation (Lag 7)**: {res['lag_7_acf']:.4f}\n\n")

    print("  Saved: 3 Markdown reports")
