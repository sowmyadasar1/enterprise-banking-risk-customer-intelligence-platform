"""Persona Generation: Map cluster profiles to business personas."""
import pandas as pd
import numpy as np
import json
import os
from . import config


PERSONA_DEFINITIONS = {
    'VIP Customers': {
        'description': 'Top-tier customers with highest balances, frequent transactions, and long tenure. '
                       'They represent the bank\'s most valuable relationships.',
        'priority': 'Platinum',
        'color': '#FFD700'
    },
    'High Net Worth': {
        'description': 'Customers with very high account balances and significant loan portfolios. '
                       'They may not transact frequently but hold substantial assets.',
        'priority': 'Gold',
        'color': '#C0C0C0'
    },
    'Loyal Customers': {
        'description': 'Long-tenured customers with consistent transaction patterns and moderate balances. '
                       'They form the stable base of the bank\'s customer portfolio.',
        'priority': 'Gold',
        'color': '#2ecc71'
    },
    'Growth Customers': {
        'description': 'Relatively new customers showing increasing engagement, moderate balances, '
                       'and potential for cross-sell. They represent future revenue growth.',
        'priority': 'Silver',
        'color': '#3498db'
    },
    'Young Digital Customers': {
        'description': 'Tech-savvy customers with high digital channel usage, frequent but small transactions. '
                       'They prefer mobile/online banking over branch visits.',
        'priority': 'Silver',
        'color': '#9b59b6'
    },
    'Budget-Conscious Customers': {
        'description': 'Price-sensitive customers with low balances and minimal product ownership. '
                       'They respond well to fee waivers and value propositions.',
        'priority': 'Bronze',
        'color': '#e67e22'
    },
    'Dormant Customers': {
        'description': 'Inactive customers with very low recent transaction activity. '
                       'They are at high risk of attrition and require re-engagement campaigns.',
        'priority': 'At-Risk',
        'color': '#95a5a6'
    },
    'At-Risk Customers': {
        'description': 'Customers showing declining engagement, increasing support tickets, '
                       'or elevated risk scores. Immediate retention efforts are needed.',
        'priority': 'At-Risk',
        'color': '#e74c3c'
    },
}


def generate_personas(df_original, labels, X_unscaled):
    """Map clusters to business personas based on profile analysis."""
    print("\n" + "="*70)
    print("  STEP 5: CUSTOMER PERSONA GENERATION")
    print("="*70)

    profile_df = X_unscaled.copy()
    profile_df['cluster'] = labels
    profile_df['customer_id'] = df_original[config.ID_COL].values

    # Compute cluster profiles (mean of each feature per cluster)
    cluster_profiles = profile_df.groupby('cluster').mean(numeric_only=True)
    n_clusters = len(cluster_profiles)
    print(f"  Clusters to label: {n_clusters}")

    # Rank clusters on key dimensions
    dims = {}
    for col in ['avg_balance', 'avg_monthly_txn_count', 'days_since_last_transaction',
                'products_owned', 'risk_score', 'total_loan_amount', 'tenure_months',
                'rolling_30d_spend', 'account_count']:
        if col in cluster_profiles.columns:
            dims[col] = cluster_profiles[col]

    # Assign personas by scoring each cluster on dimensions
    persona_names = list(PERSONA_DEFINITIONS.keys())
    assigned = {}

    # Sort clusters by avg_balance descending
    if 'avg_balance' in dims:
        ranked_by_balance = dims['avg_balance'].sort_values(ascending=False).index.tolist()
    else:
        ranked_by_balance = list(range(n_clusters))

    # Simple heuristic assignment based on cluster ranking
    available_personas = persona_names.copy()
    for i, cluster_id in enumerate(ranked_by_balance):
        if i == 0 and 'VIP Customers' in available_personas:
            assigned[cluster_id] = 'VIP Customers'
        elif i == 1 and 'High Net Worth' in available_personas:
            assigned[cluster_id] = 'High Net Worth'
        elif i == 2 and 'Loyal Customers' in available_personas:
            assigned[cluster_id] = 'Loyal Customers'
        elif i == 3 and 'Growth Customers' in available_personas:
            assigned[cluster_id] = 'Growth Customers'
        elif i == 4 and 'Young Digital Customers' in available_personas:
            assigned[cluster_id] = 'Young Digital Customers'
        elif i == 5 and 'Budget-Conscious Customers' in available_personas:
            assigned[cluster_id] = 'Budget-Conscious Customers'
        else:
            # Handle additional clusters
            remaining = [p for p in available_personas if p not in assigned.values()]
            if remaining:
                assigned[cluster_id] = remaining[0]
            else:
                assigned[cluster_id] = f'Segment {cluster_id}'

    # Check for dormant (highest recency)
    if 'days_since_last_transaction' in dims:
        dormant_cluster = dims['days_since_last_transaction'].idxmax()
        if dormant_cluster in assigned:
            assigned[dormant_cluster] = 'Dormant Customers'

    # Check for at-risk (highest risk_score)
    if 'risk_score' in dims:
        risk_cluster = dims['risk_score'].idxmax()
        if risk_cluster in assigned and risk_cluster != dormant_cluster if 'days_since_last_transaction' in dims else True:
            assigned[risk_cluster] = 'At-Risk Customers'

    # Map labels
    profile_df['persona'] = profile_df['cluster'].map(assigned)
    profile_df['persona'] = profile_df['persona'].fillna('General Customer')

    print("\n  [Persona Assignment]")
    for cluster_id, persona in sorted(assigned.items()):
        cnt = sum(labels == cluster_id)
        print(f"    Cluster {cluster_id} → {persona:30s} ({cnt:>5} customers)")

    # Save persona profiles
    persona_profiles = {}
    for cluster_id, persona_name in assigned.items():
        cluster_data = profile_df[profile_df['cluster'] == cluster_id]
        profile = {
            'persona': persona_name,
            'cluster_id': int(cluster_id),
            'customer_count': int(len(cluster_data)),
            'description': PERSONA_DEFINITIONS.get(persona_name, {}).get('description', ''),
            'priority': PERSONA_DEFINITIONS.get(persona_name, {}).get('priority', 'Standard'),
            'avg_metrics': {}
        }
        for col in ['avg_balance', 'avg_monthly_txn_count', 'products_owned',
                     'risk_score', 'total_loan_amount', 'rolling_30d_spend']:
            if col in cluster_data.columns:
                profile['avg_metrics'][col] = round(float(cluster_data[col].mean()), 2)
        persona_profiles[persona_name] = profile

    # Save to JSON
    with open(os.path.join(config.PERSONAS_DIR, 'persona_profiles.json'), 'w') as f:
        json.dump(persona_profiles, f, indent=2)

    # Save customer-persona mapping
    mapping = profile_df[['customer_id', 'cluster', 'persona']].copy()
    mapping.to_csv(os.path.join(config.DATA_DIR, 'customer_personas.csv'), index=False)

    return profile_df, assigned, persona_profiles
