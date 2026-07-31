"""Automated Business Recommendations based on Forecast Scenarios."""
import json
import os
from . import config

def generate_recommendations(scenarios: dict):
    print("\n" + "="*70)
    print("  STEP 7: BUSINESS RECOMMENDATIONS")
    print("="*70)

    recommendations = {}

    # Logic: compare Optimistic vs Base vs Conservative
    for target, scen_dict in scenarios.items():
        base = scen_dict['Base Case'].sum()
        optimistic = scen_dict['Optimistic'].sum()
        conservative = scen_dict['Conservative'].sum()
        
        recs = []
        
        if target == 'transaction_volume':
            vol_growth = (optimistic / (base + 1e-5)) - 1
            if vol_growth > 0.20:
                recs.append("High Transaction Volume Risk: Increase server capacity and database IOPS to handle potential 20%+ spikes.")
            recs.append("Capacity Planning: Ensure core banking APIs are horizontally scaled for the next 90 days.")
            
        elif target == 'revenue':
            rev_drop = 1 - (conservative / (base + 1e-5))
            if rev_drop > 0.15:
                recs.append("Revenue Risk: Prepare contingency budgets; conservative forecast implies a 15%+ drop vs expected base.")
            recs.append("Revenue Planning: Align marketing spend with the Optimistic baseline to capture potential upside.")
            
        elif target == 'loan_demand':
            recs.append("Capital Allocation: Ensure sufficient liquidity is reserved for the 90-day base case loan originations.")
            recs.append("Risk Planning: Tighten credit scoring slightly if the Conservative scenario trends downwards (indicating market contraction).")
            
        elif target == 'new_customers':
            recs.append("Branch Planning: Allocate additional customer support staff in key branches if new customer acquisition trends toward the Optimistic bound.")
            recs.append("Marketing Planning: Maintain CAC efficiency campaigns to ensure the baseline acquisition target is met.")
            
        recommendations[target] = recs
        print(f"  [{target.upper()}]")
        for r in recs:
            print(f"    - {r}")

    # Save to JSON
    with open(os.path.join(config.REPORTS_DIR, 'recommendations.json'), 'w') as f:
        json.dump(recommendations, f, indent=4)
        
    return recommendations
