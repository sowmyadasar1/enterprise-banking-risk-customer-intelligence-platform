"""Visualizations: segment charts, RFM distribution, radar charts, heatmaps."""
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import os
from . import config


def plot_segment_sizes(profile_df, assigned):
    """Bar chart of segment sizes."""
    counts = profile_df['persona'].value_counts()
    colors = plt.cm.Set2(np.linspace(0, 1, len(counts)))

    plt.figure(figsize=(12, 6))
    bars = plt.barh(counts.index, counts.values, color=colors, edgecolor='white')
    for bar, val in zip(bars, counts.values):
        plt.text(bar.get_width() + 20, bar.get_y() + bar.get_height()/2,
                 f'{val:,} ({val/len(profile_df)*100:.1f}%)', va='center')
    plt.xlabel('Number of Customers')
    plt.title('Customer Segment Sizes')
    plt.tight_layout()
    plt.savefig(os.path.join(config.VIS_DIR, 'segment_sizes.png'), dpi=150)
    plt.close()


def plot_rfm_distribution(analytics_df):
    """Plot RFM score distribution."""
    fig, axes = plt.subplots(1, 3, figsize=(18, 5))

    axes[0].hist(analytics_df['recency'], bins=30, color='#3498db', edgecolor='white', alpha=0.8)
    axes[0].set_title('Recency Distribution')
    axes[0].set_xlabel('Days Since Last Transaction')

    axes[1].hist(analytics_df['frequency'], bins=30, color='#2ecc71', edgecolor='white', alpha=0.8)
    axes[1].set_title('Frequency Distribution')
    axes[1].set_xlabel('Avg Monthly Transaction Count')

    axes[2].hist(analytics_df['monetary'], bins=30, color='#e74c3c', edgecolor='white', alpha=0.8)
    axes[2].set_title('Monetary Distribution')
    axes[2].set_xlabel('Average Balance')

    plt.suptitle('RFM Distribution Analysis', fontsize=14, y=1.02)
    plt.tight_layout()
    plt.savefig(os.path.join(config.VIS_DIR, 'rfm_distribution.png'), dpi=150)
    plt.close()


def plot_revenue_by_segment(profile_df):
    """Revenue contribution by segment."""
    if 'avg_balance' not in profile_df.columns:
        return

    segment_revenue = profile_df.groupby('persona')['avg_balance'].agg(['mean', 'sum']).sort_values('sum', ascending=False)

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 6))

    colors = plt.cm.Set2(np.linspace(0, 1, len(segment_revenue)))
    ax1.bar(range(len(segment_revenue)), segment_revenue['mean'], color=colors, edgecolor='white')
    ax1.set_xticks(range(len(segment_revenue)))
    ax1.set_xticklabels(segment_revenue.index, rotation=45, ha='right')
    ax1.set_ylabel('Average Balance ($)')
    ax1.set_title('Average Balance by Segment')

    if segment_revenue['sum'].sum() > 0:
        ax2.pie(segment_revenue['sum'], labels=segment_revenue.index, autopct='%1.1f%%',
                colors=colors, startangle=90)
        ax2.set_title('Total Balance Share by Segment')
    else:
        ax2.text(0.5, 0.5, "No Balance Data Available", ha='center', va='center', fontsize=12)
        ax2.axis('off')

    plt.tight_layout()
    plt.savefig(os.path.join(config.VIS_DIR, 'revenue_by_segment.png'), dpi=150)
    plt.close()


def plot_radar_chart(profile_df):
    """Radar chart comparing segments across dimensions."""
    dims = ['avg_balance', 'avg_monthly_txn_count', 'products_owned',
            'risk_score', 'rolling_30d_spend']
    available = [d for d in dims if d in profile_df.columns]
    if len(available) < 3:
        print("  [WARN] Not enough dimensions for radar chart")
        return

    segment_means = profile_df.groupby('persona')[available].mean()
    # Normalize to 0-1 for radar
    normed = (segment_means - segment_means.min()) / (segment_means.max() - segment_means.min() + 1e-10)

    angles = np.linspace(0, 2 * np.pi, len(available), endpoint=False).tolist()
    angles += angles[:1]

    fig, ax = plt.subplots(figsize=(10, 10), subplot_kw=dict(polar=True))
    colors = plt.cm.Set1(np.linspace(0, 1, len(normed)))

    for i, (persona, row) in enumerate(normed.iterrows()):
        values = row.tolist()
        values += values[:1]
        ax.plot(angles, values, 'o-', linewidth=2, label=persona, color=colors[i])
        ax.fill(angles, values, alpha=0.1, color=colors[i])

    ax.set_xticks(angles[:-1])
    ax.set_xticklabels(available, size=9)
    ax.set_title('Customer Segment Radar Chart', size=14, y=1.08)
    ax.legend(loc='upper right', bbox_to_anchor=(1.3, 1.1), fontsize=8)
    plt.tight_layout()
    plt.savefig(os.path.join(config.VIS_DIR, 'segment_radar.png'), dpi=150, bbox_inches='tight')
    plt.close()


def plot_heatmap(profile_df):
    """Feature heatmap across segments."""
    dims = ['avg_balance', 'avg_monthly_txn_count', 'products_owned',
            'risk_score', 'rolling_30d_spend', 'total_loan_amount',
            'days_since_last_transaction', 'account_count']
    available = [d for d in dims if d in profile_df.columns]

    segment_means = profile_df.groupby('persona')[available].mean()
    # Normalize
    normed = (segment_means - segment_means.min()) / (segment_means.max() - segment_means.min() + 1e-10)

    plt.figure(figsize=(14, 8))
    plt.imshow(normed.values, cmap='YlOrRd', aspect='auto')
    plt.colorbar(label='Normalized Value')
    plt.xticks(range(len(available)), available, rotation=45, ha='right')
    plt.yticks(range(len(normed)), normed.index)
    plt.title('Customer Segment Feature Heatmap')

    # Add text
    for i in range(len(normed)):
        for j in range(len(available)):
            plt.text(j, i, f'{normed.values[i, j]:.2f}', ha='center', va='center', fontsize=8)

    plt.tight_layout()
    plt.savefig(os.path.join(config.VIS_DIR, 'segment_heatmap.png'), dpi=150)
    plt.close()


def generate_all_visualizations(profile_df, analytics_df, assigned):
    """Generate all visualizations."""
    print("\n" + "="*70)
    print("  STEP 8: VISUALIZATIONS")
    print("="*70)

    plot_segment_sizes(profile_df, assigned)
    print("  Saved: segment_sizes.png")

    plot_rfm_distribution(analytics_df)
    print("  Saved: rfm_distribution.png")

    plot_revenue_by_segment(profile_df)
    print("  Saved: revenue_by_segment.png")

    plot_radar_chart(profile_df)
    print("  Saved: segment_radar.png")

    plot_heatmap(profile_df)
    print("  Saved: segment_heatmap.png")

    print(f"  Total visualizations: 5+ charts generated")
