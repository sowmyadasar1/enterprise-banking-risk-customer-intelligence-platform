"""Test suite for forecasting pipeline."""
import os
import pandas as pd
from . import config

def run_tests():
    print("\n" + "="*70)
    print("  FORECASTING PLATFORM — TEST SUITE")
    print("="*70)
    
    passed = 0
    total = 0
    
    def check(condition, desc):
        nonlocal passed, total
        total += 1
        if condition:
            print(f"  ✓ {desc}")
            passed += 1
        else:
            print(f"  ✗ {desc}")
            
    # 1. Check data generated
    df_path = os.path.join(config.DATA_DIR, 'daily_time_series.csv')
    has_data = os.path.exists(df_path)
    check(has_data, "Time series aggregated data exists")
    
    if has_data:
        df = pd.read_csv(df_path)
        check(len(df) > 0, "Time series has rows")
        check(not df.isnull().values.any(), "No nulls in prepared time series")
    else:
        check(False, "Time series has rows")
        check(False, "No nulls in prepared time series")
        
    # 2. Check models saved
    models = [f for f in os.listdir(config.MODELS_DIR) if f.endswith('.pkl')]
    check(len(models) > 0, "ARIMA models saved and loadable")
    
    # 3. Check reports
    reports = ['executive_summary.md', 'model_evaluation.md', 'statistical_analysis.md', 'recommendations.json']
    all_reports = all(os.path.exists(os.path.join(config.REPORTS_DIR, r)) for r in reports)
    check(all_reports, "All reports generated successfully")
    
    # 4. Check visualizations
    vis_files = os.listdir(config.VIS_DIR)
    check(len(vis_files) > 0, "Visualizations generated successfully")
    
    print(f"\n  Results: {passed} passed, {total - passed} failed out of {total} tests")
