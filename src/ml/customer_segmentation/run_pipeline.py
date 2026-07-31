"""Master orchestration script for Customer Segmentation & Intelligence Platform."""
from . import config
from .data_preparation import load_and_validate, prepare_features
from .customer_analytics import compute_customer_analytics
from .clustering import run_clustering
from .dimensionality import run_pca
from .personas import generate_personas
from .recommendations import generate_recommendations
from .visualizations import generate_all_visualizations
from .reporting import generate_reports
from .tests import run_tests


def run_full_pipeline():
    print("\n" + "="*70)
    print("  ENTERPRISE CUSTOMER SEGMENTATION & INTELLIGENCE PLATFORM")
    print("="*70)

    # 1. Data Preparation
    df = load_and_validate()
    X_scaled, X_unscaled, customer_ids = prepare_features(df)

    # 2. Customer Analytics (RFM & CLV)
    analytics_df = compute_customer_analytics(df)

    # 3. Clustering
    labels, best_k, comparison_df, kmeans_results = run_clustering(X_scaled)

    # 4. Dimensionality Reduction (PCA)
    X_2d, X_3d, pca_model = run_pca(X_scaled, labels)

    # 5. Persona Generation
    profile_df, assigned, persona_profiles = generate_personas(df, labels, X_unscaled)

    # 6. Business Recommendations
    all_recs = generate_recommendations(persona_profiles)

    # 7. Segment Profiling (embedded in Personas + Reporting)
    print("\n" + "="*70)
    print("  STEP 7: SEGMENT PROFILING")
    print("="*70)
    for persona, profile in persona_profiles.items():
        cnt = profile.get('customer_count', 0)
        metrics = profile.get('avg_metrics', {})
        print(f"\n  {persona} ({cnt} customers):")
        for m, v in metrics.items():
            print(f"    {m}: {v:,.2f}")

    # 8. Visualizations
    generate_all_visualizations(profile_df, analytics_df, assigned)

    # 9. Reports
    generate_reports(analytics_df, profile_df, assigned, persona_profiles,
                     comparison_df, all_recs)

    # 10. Tests
    print("\n")
    run_tests()

    print("\n" + "="*70)
    print("  CUSTOMER SEGMENTATION PLATFORM — PIPELINE COMPLETE")
    print("="*70)


if __name__ == "__main__":
    run_full_pipeline()
