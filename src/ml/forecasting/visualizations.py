"""Visualization module for the Forecasting Platform."""
import os
import matplotlib.pyplot as plt
import pandas as pd
from . import config

def plot_historical_and_forecast(df: pd.DataFrame, all_forecasts: dict, horizon: int = 90):
    print("\n" + "="*70)
    print("  STEP 8: VISUALIZATIONS")
    print("="*70)
    
    for target, h_dict in all_forecasts.items():
        if horizon not in h_dict:
            continue
            
        f_data = h_dict[horizon]
        if 'arima' in f_data:
            model = 'arima'
        else:
            model = 'moving_average'
            
        mean = f_data[model]['mean']
        lower = f_data[model]['lower']
        upper = f_data[model]['upper']
        
        # Historical data (last 180 days for context)
        hist = df[target].tail(180)
        
        # Forecast dates
        last_date = df.index[-1]
        fc_dates = pd.date_range(start=last_date + pd.Timedelta(days=1), periods=horizon, freq='D')
        
        plt.figure(figsize=(12, 6))
        plt.plot(hist.index, hist.values, label='Historical', color='#1f77b4')
        plt.plot(fc_dates, mean, label=f'Forecast ({model.upper()})', color='#ff7f0e')
        plt.fill_between(fc_dates, lower, upper, color='#ff7f0e', alpha=0.2, label='95% Confidence Interval')
        
        plt.title(f'{target.replace("_", " ").title()} — 90 Day Forecast')
        plt.xlabel('Date')
        plt.ylabel('Value')
        plt.legend()
        plt.grid(True, alpha=0.3)
        plt.tight_layout()
        
        out_path = os.path.join(config.VIS_DIR, f'{target}_forecast.png')
        plt.savefig(out_path, dpi=150)
        plt.close()
        print(f"  Saved: {target}_forecast.png")

def plot_decomposition(analysis_results: dict):
    for col, res in analysis_results.items():
        decomp = res.get('decomposition')
        if decomp is not None:
            fig, (ax1, ax2, ax3) = plt.subplots(3, 1, figsize=(10, 8), sharex=True)
            
            ax1.plot(decomp['trend'])
            ax1.set_title(f'{col.replace("_", " ").title()} — Trend')
            ax1.grid(True, alpha=0.3)
            
            ax2.plot(decomp['seasonal'])
            ax2.set_title('Seasonality')
            ax2.grid(True, alpha=0.3)
            
            ax3.plot(decomp['resid'])
            ax3.set_title('Residuals')
            ax3.grid(True, alpha=0.3)
            
            plt.tight_layout()
            out_path = os.path.join(config.VIS_DIR, f'{col}_decomposition.png')
            plt.savefig(out_path, dpi=150)
            plt.close()
            print(f"  Saved: {col}_decomposition.png")

def generate_all_visualizations(df, all_forecasts, analysis_results):
    plot_historical_and_forecast(df, all_forecasts)
    plot_decomposition(analysis_results)
