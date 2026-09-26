"""Risk scoring: generate fraud risk scores and risk bands."""

import numpy as np
import pandas as pd
import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import os
from . import config


def generate_risk_scores(model, X_data, customer_ids, threshold=0.5):
    """Generate fraud risk scores and assign risk bands."""
    print("\n" + "=" * 70)
    print("  STEP 10: RISK SCORING")
    print("=" * 70)

    try:
        probas = model.predict_proba(X_data.fillna(0))[:, 1]
    except Exception:
        probas = np.zeros(len(X_data))

    # Scale to 0-100
    risk_scores = (probas * 100).round(2)

    # Risk bands
    def assign_band(score):
        if score < 25:
            return "Low Risk"
        elif score < 50:
            return "Medium Risk"
        elif score < 75:
            return "High Risk"
        else:
            return "Critical Risk"

    risk_df = pd.DataFrame(
        {
            "customer_id": customer_ids,
            "fraud_probability": probas.round(4),
            "risk_score": risk_scores,
            "risk_band": [assign_band(s) for s in risk_scores],
            "predicted_fraud": (probas >= threshold).astype(int),
        }
    )

    # Summary
    print(f"\n  Risk Band Distribution:")
    band_counts = risk_df["risk_band"].value_counts()
    for band in ["Low Risk", "Medium Risk", "High Risk", "Critical Risk"]:
        cnt = band_counts.get(band, 0)
        print(f"    {band:15s}: {cnt:>6} ({cnt/len(risk_df)*100:.1f}%)")

    # Plot risk distribution
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 5))

    ax1.hist(risk_scores, bins=50, color="steelblue", edgecolor="white", alpha=0.8)
    ax1.set_xlabel("Risk Score (0-100)")
    ax1.set_ylabel("Count")
    ax1.set_title("Fraud Risk Score Distribution")
    ax1.axvline(25, color="green", linestyle="--", alpha=0.7, label="Low/Med")
    ax1.axvline(50, color="orange", linestyle="--", alpha=0.7, label="Med/High")
    ax1.axvline(75, color="red", linestyle="--", alpha=0.7, label="High/Critical")
    ax1.legend()

    colors = {
        "Low Risk": "#2ecc71",
        "Medium Risk": "#f39c12",
        "High Risk": "#e74c3c",
        "Critical Risk": "#8e44ad",
    }
    bands = ["Low Risk", "Medium Risk", "High Risk", "Critical Risk"]
    vals = [band_counts.get(b, 0) for b in bands]
    ax2.bar(bands, vals, color=[colors[b] for b in bands])
    ax2.set_ylabel("Count")
    ax2.set_title("Risk Band Distribution")

    plt.tight_layout()
    plt.savefig(os.path.join(config.VIS_DIR, "risk_distribution.png"), dpi=150)
    plt.close()
    print("  Saved: risk_distribution.png")

    # Save risk scores
    risk_path = os.path.join(config.DATA_DIR, "risk_scores.csv")
    risk_df.to_csv(risk_path, index=False)
    print(f"  Saved: {risk_path}")

    return risk_df
