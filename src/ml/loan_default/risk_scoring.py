"""Risk scoring: generate credit risk scores and risk categories."""
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import os
from . import config


def generate_risk_scores(model, X_data, customer_ids):
    """Generate credit risk scores and assign risk bands."""
    print("\n" + "="*70)
    print("  STEP 8: CREDIT RISK SCORING")
    print("="*70)

    try:
        probas = model.predict_proba(X_data.fillna(0))[:, 1]
    except Exception:
        probas = np.zeros(len(X_data))

    # Scale to 0-100 (where 100 is highest risk of default)
    risk_scores = (probas * 100).round(2)

    # Risk bands for Credit
    def assign_band(score):
        if score < 10:
            return 'Very Low Risk'
        elif score < 25:
            return 'Low Risk'
        elif score < 50:
            return 'Medium Risk'
        elif score < 80:
            return 'High Risk'
        else:
            return 'Very High Risk'

    risk_df = pd.DataFrame({
        'customer_id': customer_ids,
        'default_probability': probas.round(4),
        'credit_risk_score': risk_scores,
        'risk_category': [assign_band(s) for s in risk_scores]
    })

    # Summary
    print(f"\n  Credit Risk Category Distribution:")
    band_counts = risk_df['risk_category'].value_counts()
    for band in ['Very Low Risk', 'Low Risk', 'Medium Risk', 'High Risk', 'Very High Risk']:
        cnt = band_counts.get(band, 0)
        print(f"    {band:15s}: {cnt:>6} ({cnt/len(risk_df)*100:.1f}%)")

    # Plot risk distribution
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 5))

    ax1.hist(risk_scores, bins=50, color='darkblue', edgecolor='white', alpha=0.8)
    ax1.set_xlabel('Credit Risk Score (0-100)')
    ax1.set_ylabel('Count')
    ax1.set_title('Credit Risk Score Distribution')
    ax1.axvline(10, color='green', linestyle='--', alpha=0.7)
    ax1.axvline(25, color='lightgreen', linestyle='--', alpha=0.7)
    ax1.axvline(50, color='orange', linestyle='--', alpha=0.7)
    ax1.axvline(80, color='red', linestyle='--', alpha=0.7)

    colors = {'Very Low Risk': '#27ae60', 'Low Risk': '#2ecc71', 'Medium Risk': '#f39c12',
              'High Risk': '#e67e22', 'Very High Risk': '#c0392b'}
    bands = ['Very Low Risk', 'Low Risk', 'Medium Risk', 'High Risk', 'Very High Risk']
    vals = [band_counts.get(b, 0) for b in bands]
    ax2.bar(bands, vals, color=[colors[b] for b in bands])
    ax2.set_ylabel('Count')
    ax2.set_title('Risk Category Distribution')

    plt.tight_layout()
    plt.savefig(os.path.join(config.VIS_DIR, 'credit_risk_distribution.png'), dpi=150)
    plt.close()

    # Save risk scores
    risk_path = os.path.join(config.DATA_DIR, 'credit_risk_scores.csv')
    risk_df.to_csv(risk_path, index=False)
    
    return risk_df
