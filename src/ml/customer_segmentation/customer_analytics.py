"""Customer Analytics: RFM Analysis, CLV Calculation, and baseline profiling."""
import pandas as pd
import numpy as np
from . import config


def compute_rfm(df):
    """Compute RFM scores from the Feature Store."""
    print("\n" + "="*70)
    print("  STEP 2: CUSTOMER ANALYTICS — RFM & CLV")
    print("="*70)

    rfm = pd.DataFrame({'customer_id': df[config.ID_COL].values})

    # Recency: days since last transaction (lower = more recent = better)
    if config.RFM_RECENCY_COL in df.columns:
        rfm['recency'] = df[config.RFM_RECENCY_COL].values
    else:
        rfm['recency'] = 0

    # Frequency: average monthly transaction count (higher = better)
    if config.RFM_FREQUENCY_COL in df.columns:
        rfm['frequency'] = df[config.RFM_FREQUENCY_COL].values
    else:
        rfm['frequency'] = 0

    # Monetary: average balance (higher = better)
    if config.RFM_MONETARY_COL in df.columns:
        rfm['monetary'] = df[config.RFM_MONETARY_COL].values
    else:
        rfm['monetary'] = 0

    # RFM Scoring (quintile-based 1-5 scoring)
    # For Recency: lower is better, so reverse scoring
    try:
        rfm['R_score'] = pd.qcut(rfm['recency'].rank(method='first'), q=5, labels=[5, 4, 3, 2, 1]).astype(float)
    except ValueError:
        rfm['R_score'] = 3.0  # fallback

    try:
        rfm['F_score'] = pd.qcut(rfm['frequency'].rank(method='first'), q=5, labels=[1, 2, 3, 4, 5]).astype(float)
    except ValueError:
        rfm['F_score'] = 3.0

    try:
        rfm['M_score'] = pd.qcut(rfm['monetary'].rank(method='first'), q=5, labels=[1, 2, 3, 4, 5]).astype(float)
    except ValueError:
        rfm['M_score'] = 3.0

    rfm['RFM_score'] = rfm['R_score'] + rfm['F_score'] + rfm['M_score']

    # RFM Segment Labels
    def rfm_segment(row):
        if row['RFM_score'] >= 13:
            return 'Champions'
        elif row['RFM_score'] >= 10:
            return 'Loyal Customers'
        elif row['RFM_score'] >= 8:
            return 'Potential Loyalists'
        elif row['RFM_score'] >= 6:
            return 'At Risk'
        elif row['RFM_score'] >= 4:
            return 'Needs Attention'
        else:
            return 'Hibernating'

    rfm['rfm_segment'] = rfm.apply(rfm_segment, axis=1)

    print("\n  [RFM Score Distribution]")
    print(f"    Min: {rfm['RFM_score'].min():.0f}  Max: {rfm['RFM_score'].max():.0f}  Mean: {rfm['RFM_score'].mean():.1f}")
    print(f"\n  [RFM Segments]")
    for seg, cnt in rfm['rfm_segment'].value_counts().items():
        print(f"    {seg:25s}: {cnt:>5} ({cnt/len(rfm)*100:.1f}%)")

    return rfm


def compute_clv(df, rfm):
    """Compute simplified Customer Lifetime Value."""
    clv = pd.DataFrame({'customer_id': df[config.ID_COL].values})

    # CLV = tenure_months * avg_monthly_revenue_proxy
    # Using avg_balance as a proxy for revenue contribution
    tenure_col = 'tenure_months' if 'tenure_months' in df.columns else None
    balance_col = 'avg_balance' if 'avg_balance' in df.columns else None

    if tenure_col and balance_col:
        tenure = pd.to_numeric(df[tenure_col], errors='coerce').fillna(1)
        balance = pd.to_numeric(df[balance_col], errors='coerce').fillna(0)
        # Simplified CLV model: tenure * monthly_profit_proxy
        # Assuming 0.5% monthly return on average balance
        clv['estimated_clv'] = (tenure * balance * 0.005).round(2)
    else:
        clv['estimated_clv'] = 0

    # CLV tiers
    clv['clv_tier'] = pd.qcut(clv['estimated_clv'].rank(method='first'), q=5,
                               labels=['Very Low', 'Low', 'Medium', 'High', 'Very High'],
                               duplicates='drop')

    print(f"\n  [Customer Lifetime Value]")
    print(f"    Min CLV:  ${clv['estimated_clv'].min():,.2f}")
    print(f"    Max CLV:  ${clv['estimated_clv'].max():,.2f}")
    print(f"    Mean CLV: ${clv['estimated_clv'].mean():,.2f}")
    print(f"\n  [CLV Tiers]")
    for tier, cnt in clv['clv_tier'].value_counts().sort_index().items():
        print(f"    {tier:10s}: {cnt:>5} ({cnt/len(clv)*100:.1f}%)")

    return clv


def compute_customer_analytics(df):
    """Run full customer analytics suite."""
    rfm = compute_rfm(df)
    clv = compute_clv(df, rfm)

    # Merge RFM + CLV
    analytics = rfm.merge(clv, on='customer_id')

    # Additional analytics
    if 'products_owned' in df.columns:
        analytics['products_owned'] = df['products_owned'].values
    if 'account_count' in df.columns:
        analytics['account_count'] = df['account_count'].values
    if 'risk_score' in df.columns:
        analytics['risk_score'] = df['risk_score'].values

    analytics.to_csv(os.path.join(config.DATA_DIR, 'customer_analytics.csv'), index=False)
    print(f"\n  Saved: customer_analytics.csv ({len(analytics)} customers)")

    return analytics


import os
