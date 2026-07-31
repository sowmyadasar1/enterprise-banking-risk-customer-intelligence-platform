"""Master orchestrator for the Forecasting Platform."""
from .data_preparation import extract_daily_series
from .time_series_analysis import run_analysis
from .feature_engineering import engineer_features
from .models import train_and_forecast_all
from .evaluation import run_evaluation
from .scenarios import generate_scenarios
from .recommendations import generate_recommendations
from .visualizations import generate_all_visualizations
from .reporting import generate_reports
from .tests import run_tests

def run_full_pipeline():
    print("\n" + "="*70)
    print("  ENTERPRISE REVENUE & TRANSACTION FORECASTING PLATFORM")
    print("="*70)

    # 1. Data Preparation
    df = extract_daily_series()

    # 2. Time Series Analysis
    analysis_results = run_analysis(df)

    # 3. Feature Engineering
    features_df = engineer_features(df)

    # 4. Model Evaluation (80/20 Split)
    eval_results = run_evaluation(df)

    # 5. Full Model Training & Multi-Horizon Forecasting
    all_forecasts = train_and_forecast_all(df)

    # 6. Business Scenarios (90-day Outlook)
    scenarios = generate_scenarios(all_forecasts, horizon=90)

    # 7. Business Recommendations
    generate_recommendations(scenarios)

    # 8. Visualizations
    generate_all_visualizations(df, all_forecasts, analysis_results)

    # 9. Reporting
    generate_reports(analysis_results, eval_results, scenarios)

    # 10. Tests
    run_tests()

    print("\n" + "="*70)
    print("  FORECASTING PLATFORM — PIPELINE COMPLETE")
    print("="*70)

if __name__ == "__main__":
    run_full_pipeline()
