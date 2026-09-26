"""Report generation: markdown reports for segmentation platform."""

import os
import json
import pandas as pd
from . import config


def generate_reports(
    analytics_df, profile_df, assigned, persona_profiles, comparison_df, all_recs
):
    """Generate all markdown reports."""
    print("\n" + "=" * 70)
    print("  STEP 9: REPORT GENERATION")
    print("=" * 70)

    # --- Segmentation Report ---
    seg = "# Customer Segmentation Report\n\n"
    seg += "## Clustering Results\n\n"
    seg += "| Method | K | Silhouette | Davies-Bouldin | Calinski-Harabasz |\n"
    seg += "|--------|---|------------|----------------|-------------------|\n"
    for _, row in comparison_df.iterrows():
        seg += (
            f"| {row['method']} | {row['k']:.0f} | {row['silhouette']:.4f} | "
            f"{row['davies_bouldin']:.4f} | {row['calinski_harabasz']:.1f} |\n"
        )
    seg += f"\n**Best Method:** {comparison_df.iloc[0]['method']} "
    seg += f"(Silhouette={comparison_df.iloc[0]['silhouette']:.4f})\n\n"
    seg += "## Segment Sizes\n\n"
    seg += "| Persona | Customers | % of Total |\n"
    seg += "|---------|-----------|------------|\n"
    for persona, cnt in profile_df["persona"].value_counts().items():
        seg += f"| {persona} | {cnt:,} | {cnt/len(profile_df)*100:.1f}% |\n"

    with open(os.path.join(config.REPORTS_DIR, "segmentation_report.md"), "w") as f:
        f.write(seg)

    # --- Customer Intelligence Report ---
    intel = "# Customer Intelligence Report\n\n"
    intel += "## RFM Analysis Summary\n\n"
    intel += "| RFM Segment | Count | % |\n"
    intel += "|-------------|-------|---|\n"
    for seg_name, cnt in analytics_df["rfm_segment"].value_counts().items():
        intel += f"| {seg_name} | {cnt:,} | {cnt/len(analytics_df)*100:.1f}% |\n"
    intel += f"\n## CLV Summary\n"
    intel += f"- Mean CLV: ${analytics_df['estimated_clv'].mean():,.2f}\n"
    intel += f"- Median CLV: ${analytics_df['estimated_clv'].median():,.2f}\n"
    intel += f"- Max CLV: ${analytics_df['estimated_clv'].max():,.2f}\n"

    with open(os.path.join(config.REPORTS_DIR, "customer_intelligence.md"), "w") as f:
        f.write(intel)

    # --- Persona Guide ---
    guide = "# Customer Persona Guide\n\n"
    for name, profile in persona_profiles.items():
        guide += f"## {name}\n\n"
        guide += f"**Priority:** {profile.get('priority', 'Standard')} | "
        guide += f"**Customers:** {profile.get('customer_count', 0):,}\n\n"
        guide += f"{profile.get('description', '')}\n\n"
        if "avg_metrics" in profile:
            guide += "### Key Metrics\n"
            for metric, val in profile["avg_metrics"].items():
                guide += f"- {metric}: {val:,.2f}\n"
        guide += "\n---\n\n"

    with open(os.path.join(config.REPORTS_DIR, "persona_guide.md"), "w") as f:
        f.write(guide)

    # --- Executive Summary ---
    exe = "# Enterprise Customer Segmentation — Executive Summary\n\n"
    exe += f"## Overview\n"
    exe += f"The platform segmented **{len(profile_df):,} customers** into "
    exe += f"**{len(assigned)} distinct personas** using unsupervised machine learning.\n\n"
    exe += f"## Key Findings\n"
    top = (
        profile_df.groupby("persona")["avg_balance"].mean().sort_values(ascending=False)
    )
    if len(top) > 0:
        exe += f"- **Highest Value Segment:** {top.index[0]} (Avg Balance: ${top.iloc[0]:,.2f})\n"
    if len(top) > 1:
        exe += f"- **Lowest Value Segment:** {top.index[-1]} (Avg Balance: ${top.iloc[-1]:,.2f})\n"
    exe += f"- **RFM Champions:** {sum(analytics_df['rfm_segment'] == 'Champions'):,} customers\n"
    exe += f"- **At-Risk/Dormant:** {sum(analytics_df['rfm_segment'].isin(['At Risk', 'Needs Attention', 'Hibernating'])):,} customers\n"
    exe += f"\n## Recommendations\n"
    exe += "1. Prioritize retention for VIP and At-Risk segments.\n"
    exe += "2. Launch reactivation campaigns for Dormant customers.\n"
    exe += "3. Invest in digital capabilities for Young Digital segment.\n"
    exe += "4. Cross-sell wealth products to High Net Worth customers.\n"

    with open(os.path.join(config.REPORTS_DIR, "executive_summary.md"), "w") as f:
        f.write(exe)

    print(f"  Saved: 4 Markdown reports")
