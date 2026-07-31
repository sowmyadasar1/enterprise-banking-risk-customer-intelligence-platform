"""Business Recommendations: cross-sell, upsell, retention per persona."""
import json
import os
from . import config


RECOMMENDATIONS = {
    'VIP Customers': {
        'marketing_strategy': 'Exclusive invitation-only events, personalized wealth management offers, priority customer service.',
        'retention_strategy': 'Assign dedicated relationship manager, quarterly portfolio reviews, premium loyalty rewards.',
        'cross_sell': ['Private banking services', 'Investment portfolio management', 'Insurance products'],
        'upsell': ['Platinum credit cards', 'Premium mortgage products', 'International banking'],
        'product_recommendations': ['Wealth management', 'Trust services', 'Brokerage accounts'],
        'relationship_management': 'White-glove concierge service with dedicated team.',
        'campaign_suggestions': ['Exclusive investment webinars', 'VIP appreciation dinners', 'Early access to new products'],
        'business_priority': 'Critical — Protect and grow highest-value relationships.',
        'expected_impact': 'Retention of top 5% revenue contributors, potential 15-20% AUM growth.'
    },
    'High Net Worth': {
        'marketing_strategy': 'Targeted wealth advisory communications, tax optimization seminars, estate planning.',
        'retention_strategy': 'Proactive outreach from senior advisors, competitive rate matching, fee waivers.',
        'cross_sell': ['Tax-advantaged investment accounts', 'Estate planning', 'Insurance bundles'],
        'upsell': ['Premium savings accounts', 'High-yield CDs', 'Commercial lending'],
        'product_recommendations': ['Fixed income products', 'Real estate investment trusts', 'Structured deposits'],
        'relationship_management': 'Senior relationship manager with quarterly touchpoints.',
        'campaign_suggestions': ['Wealth preservation workshops', 'Charitable giving programs', 'Referral bonuses'],
        'business_priority': 'High — Maximize asset retention and fee income.',
        'expected_impact': 'Increase share-of-wallet by 10-15%, reduce attrition to under 3%.'
    },
    'Loyal Customers': {
        'marketing_strategy': 'Loyalty rewards enhancement, milestone celebrations, referral programs.',
        'retention_strategy': 'Tenure-based rate discounts, loyalty bonus points, anniversary gifts.',
        'cross_sell': ['Home equity loans', 'Auto loans', 'Credit card upgrades'],
        'upsell': ['Premium checking accounts', 'Investment advisory', 'Insurance add-ons'],
        'product_recommendations': ['Retirement savings', 'Education savings plans', 'Travel rewards cards'],
        'relationship_management': 'Regular digital check-ins, annual in-person review.',
        'campaign_suggestions': ['Referral reward campaigns', 'Product bundle discounts', 'Loyalty tier upgrades'],
        'business_priority': 'High — Deepen engagement and maximize lifetime value.',
        'expected_impact': 'Increase products per customer from 3 to 5, boosting revenue 20%.'
    },
    'Growth Customers': {
        'marketing_strategy': 'Onboarding journey optimization, product discovery campaigns, financial literacy content.',
        'retention_strategy': 'Welcome bonuses, first-year fee waivers, personalized financial tips.',
        'cross_sell': ['Savings accounts', 'Personal loans', 'Basic investment products'],
        'upsell': ['Rewards credit cards', 'Premium checking', 'Mobile payment solutions'],
        'product_recommendations': ['Emergency fund savings', 'Short-term CDs', 'Budgeting tools'],
        'relationship_management': 'Digital-first engagement with periodic human touchpoints.',
        'campaign_suggestions': ['Financial wellness webinars', 'First investment bonus', 'Product trial offers'],
        'business_priority': 'Medium-High — Nurture to become Loyal/VIP customers.',
        'expected_impact': 'Convert 30% to Loyal segment within 18 months.'
    },
    'Young Digital Customers': {
        'marketing_strategy': 'Social media engagement, gamified savings challenges, mobile-first experiences.',
        'retention_strategy': 'In-app rewards, seamless digital experience, peer comparison features.',
        'cross_sell': ['Micro-investment platforms', 'Student loan refinancing', 'Peer-to-peer payments'],
        'upsell': ['Premium mobile features', 'Cashback credit cards', 'Crypto trading access'],
        'product_recommendations': ['Round-up savings', 'No-fee checking', 'Digital wallets'],
        'relationship_management': 'AI chatbot + periodic in-app engagement.',
        'campaign_suggestions': ['Social media contests', 'Referral challenges', 'Financial literacy modules'],
        'business_priority': 'Medium — Build long-term digital banking relationships.',
        'expected_impact': 'Increase digital adoption 40%, reduce branch costs 15%.'
    },
    'Budget-Conscious Customers': {
        'marketing_strategy': 'Value-focused messaging, low-fee product promotions, financial planning tools.',
        'retention_strategy': 'Fee waiver programs, overdraft protection, budgeting assistance.',
        'cross_sell': ['Basic savings accounts', 'Secured credit cards', 'Bill pay services'],
        'upsell': ['Fee-free checking upgrades', 'Cash-back debit cards', 'Financial coaching'],
        'product_recommendations': ['No-minimum-balance savings', 'Prepaid cards', 'Automatic savings'],
        'relationship_management': 'Self-service digital with proactive financial tips.',
        'campaign_suggestions': ['Fee reduction promotions', 'Savings goal challenges', 'Financial education'],
        'business_priority': 'Medium — Reduce cost-to-serve while maintaining engagement.',
        'expected_impact': 'Reduce attrition 10%, increase average balance 25%.'
    },
    'Dormant Customers': {
        'marketing_strategy': 'Win-back campaigns with incentives, re-engagement emails, dormancy alerts.',
        'retention_strategy': 'Account reactivation bonuses, personalized "we miss you" outreach, fee forgiveness.',
        'cross_sell': ['Simple savings products', 'Mobile banking activation', 'Automatic transfers'],
        'upsell': ['Active checking account incentives', 'Cashback offers on reactivation'],
        'product_recommendations': ['High-yield savings', 'Round-up features', 'Goal-based saving'],
        'relationship_management': 'Outbound call center campaign with special offers.',
        'campaign_suggestions': ['Reactivation bonus campaigns', 'Win-back email series', 'SMS nudges'],
        'business_priority': 'High — Prevent full attrition and recover dormant balances.',
        'expected_impact': 'Reactivate 15-20% of dormant accounts, recover $2M+ in deposits.'
    },
    'At-Risk Customers': {
        'marketing_strategy': 'Proactive retention offers, service recovery, complaint resolution.',
        'retention_strategy': 'Immediate outreach, rate matching, dedicated problem resolution team.',
        'cross_sell': ['Consolidation loans', 'Debt management programs', 'Insurance products'],
        'upsell': ['Financial advisory services', 'Credit improvement programs'],
        'product_recommendations': ['Debt consolidation', 'Credit counseling', 'Hardship programs'],
        'relationship_management': 'Immediate assignment to retention specialist.',
        'campaign_suggestions': ['Service recovery calls', 'Rate reduction offers', 'Loyalty reinstatement'],
        'business_priority': 'Critical — Immediate intervention to prevent churn.',
        'expected_impact': 'Reduce churn rate by 25%, save $500K+ in lost revenue.'
    },
}


def generate_recommendations(persona_profiles):
    """Generate and save business recommendations for each persona."""
    print("\n" + "="*70)
    print("  STEP 6: BUSINESS RECOMMENDATIONS")
    print("="*70)

    all_recs = {}
    for persona_name, profile in persona_profiles.items():
        recs = RECOMMENDATIONS.get(persona_name, {
            'marketing_strategy': 'Standard marketing communications.',
            'retention_strategy': 'Monitor engagement and intervene if declining.',
            'cross_sell': ['General product offerings'],
            'upsell': ['Standard product upgrades'],
            'product_recommendations': ['Core banking products'],
            'relationship_management': 'Standard digital engagement.',
            'campaign_suggestions': ['Seasonal promotions'],
            'business_priority': 'Standard',
            'expected_impact': 'Maintain current relationship.'
        })

        all_recs[persona_name] = {
            'persona': persona_name,
            'customer_count': profile.get('customer_count', 0),
            'priority': profile.get('priority', 'Standard'),
            **recs
        }

        print(f"\n  {persona_name} ({profile.get('customer_count', 0)} customers):")
        print(f"    Priority: {profile.get('priority', 'Standard')}")
        print(f"    Marketing: {recs.get('marketing_strategy', 'N/A')[:80]}...")
        print(f"    Retention: {recs.get('retention_strategy', 'N/A')[:80]}...")

    # Save recommendations
    with open(os.path.join(config.RECS_DIR, 'recommendations.json'), 'w') as f:
        json.dump(all_recs, f, indent=2)

    # Save as markdown
    md = "# Customer Segment Recommendations\n\n"
    for persona, rec in all_recs.items():
        md += f"## {persona}\n\n"
        md += f"**Priority:** {rec.get('priority', 'Standard')} | "
        md += f"**Customers:** {rec.get('customer_count', 0):,}\n\n"
        md += f"### Marketing Strategy\n{rec.get('marketing_strategy', 'N/A')}\n\n"
        md += f"### Retention Strategy\n{rec.get('retention_strategy', 'N/A')}\n\n"
        md += f"### Cross-Sell Opportunities\n"
        for item in rec.get('cross_sell', []):
            md += f"- {item}\n"
        md += f"\n### Upsell Opportunities\n"
        for item in rec.get('upsell', []):
            md += f"- {item}\n"
        md += f"\n### Expected Impact\n{rec.get('expected_impact', 'N/A')}\n\n---\n\n"

    with open(os.path.join(config.RECS_DIR, 'recommendations.md'), 'w') as f:
        f.write(md)

    print(f"\n  Saved: recommendations.json + recommendations.md")
    return all_recs
