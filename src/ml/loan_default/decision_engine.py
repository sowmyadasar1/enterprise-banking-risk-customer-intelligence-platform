"""Decision engine: map credit risk scores to business actions."""
import pandas as pd
import os
from . import config


def build_decision_engine(risk_df, thresholds):
    """Map risk probabilities to loan approval decisions."""
    print("\n" + "="*70)
    print("  STEP 9: LOAN DECISION ENGINE")
    print("="*70)
    
    auto_app_th = thresholds.get('auto_approve_thresh', 0.2)
    auto_rej_th = thresholds.get('auto_reject_thresh', 0.8)

    def get_action(row):
        prob = row['default_probability']
        
        if prob < auto_app_th:
            return 'Approve Loan', 'Auto-Approve', f"Probability of default ({prob:.3f}) is below Auto-Approve threshold ({auto_app_th:.3f})."
        elif prob >= auto_rej_th:
            return 'Reject Loan', 'Auto-Reject', f"Probability of default ({prob:.3f}) exceeds Auto-Reject threshold ({auto_rej_th:.3f})."
        elif prob < (auto_app_th + auto_rej_th)/2:
            return 'Approve with Conditions', 'Manual Review', f"Moderate risk ({prob:.3f}). Route to underwriter for standard review. Consider higher interest rate."
        else:
            return 'Request Additional Documents', 'Manual Review', f"Elevated risk ({prob:.3f}). Route to senior underwriter. Require collateral verification."

    actions = risk_df.apply(get_action, axis=1, result_type='expand')
    risk_df = risk_df.copy()
    risk_df['recommended_action'] = actions[0]
    risk_df['decision_tier'] = actions[1]
    risk_df['explanation'] = actions[2]

    # Summary
    print("\n  Loan Decision Tiers:")
    tier_counts = risk_df['decision_tier'].value_counts()
    for tier, cnt in tier_counts.items():
        print(f"    {tier:20s}: {cnt:>6} ({cnt/len(risk_df)*100:.1f}%)")
        
    print("\n  Detailed Actions:")
    action_counts = risk_df['recommended_action'].value_counts()
    for action, cnt in action_counts.items():
        print(f"    {action:30s}: {cnt:>6} ({cnt/len(risk_df)*100:.1f}%)")

    # Save
    decisions_path = os.path.join(config.DATA_DIR, 'loan_decisions.csv')
    risk_df.to_csv(decisions_path, index=False)

    return risk_df
