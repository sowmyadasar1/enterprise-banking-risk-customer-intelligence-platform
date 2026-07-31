"""Decision engine: convert predictions to business actions with explanations."""
import pandas as pd
import os
from . import config


def build_decision_engine(risk_df):
    """Map risk scores to actionable business decisions."""
    print("\n" + "="*70)
    print("  STEP 11: DECISION ENGINE")
    print("="*70)

    def get_action(row):
        score = row['risk_score']
        band = row['risk_band']

        if score < 10:
            return 'Approve Transaction', f"Risk score {score:.0f} is well below threshold. No action needed."
        elif score < 25:
            return 'Approve with Monitoring', f"Risk score {score:.0f} is low but warrants standard monitoring."
        elif score < 50:
            return 'Manual Investigation', f"Risk score {score:.0f} is elevated. Route to L1 analyst for review within 24h."
        elif score < 75:
            return 'Temporary Hold', f"Risk score {score:.0f} is high. Place temporary hold and escalate to L2 fraud team within 4h."
        elif score < 90:
            return 'Block Transaction', f"Risk score {score:.0f} is very high. Block transaction and contact customer for verification."
        else:
            return 'Escalate to Fraud Team', f"Risk score {score:.0f} is critical. Immediately escalate to senior fraud investigators. Freeze account."

    actions = risk_df.apply(get_action, axis=1, result_type='expand')
    risk_df = risk_df.copy()
    risk_df['recommended_action'] = actions[0]
    risk_df['explanation'] = actions[1]

    # Summary
    print("\n  Action Distribution:")
    action_counts = risk_df['recommended_action'].value_counts()
    for action, cnt in action_counts.items():
        print(f"    {action:30s}: {cnt:>6} ({cnt/len(risk_df)*100:.1f}%)")

    # Save
    decisions_path = os.path.join(config.DATA_DIR, 'decisions.csv')
    risk_df.to_csv(decisions_path, index=False)
    print(f"\n  Saved: {decisions_path}")

    # Print sample decisions
    print("\n  Sample Decisions:")
    samples = risk_df.nlargest(5, 'risk_score')
    for _, row in samples.iterrows():
        print(f"    Customer {row['customer_id'][:8]}... | Score: {row['risk_score']:.0f} | "
              f"Action: {row['recommended_action']}")
        print(f"      → {row['explanation']}")

    return risk_df
