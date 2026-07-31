"""Business Scenario generation based on forecasting models."""
import numpy as np

def generate_scenarios(all_forecasts: dict, horizon: int = 90):
    """
    Generates three scenarios for the chosen horizon:
    1. Base Case (ARIMA mean)
    2. Optimistic (ARIMA upper bound + 5%)
    3. Conservative (ARIMA lower bound - 5%)
    4. Revenue Slowdown (Base Case - 15%)
    """
    print("\n" + "="*70)
    print("  STEP 6: BUSINESS SCENARIOS")
    print("="*70)

    scenarios = {}
    
    for target, h_dict in all_forecasts.items():
        if horizon not in h_dict:
            continue
            
        if 'arima' in h_dict[horizon]:
            base_mean = h_dict[horizon]['arima']['mean']
            upper = h_dict[horizon]['arima']['upper']
            lower = h_dict[horizon]['arima']['lower']
        else:
            # Fallback to moving average if ARIMA failed
            base_mean = h_dict[horizon]['moving_average']['mean']
            upper = h_dict[horizon]['moving_average']['upper']
            lower = h_dict[horizon]['moving_average']['lower']
            
        # Guarantee non-negative forecasts
        base_mean = np.maximum(base_mean, 0)
        upper = np.maximum(upper, 0)
        lower = np.maximum(lower, 0)
        
        scenarios[target] = {
            'Base Case': base_mean,
            'Optimistic': upper * 1.05,
            'Conservative': lower * 0.95,
            'Severe Slowdown': base_mean * 0.85
        }
        
        print(f"  [{target.upper()}] 90-Day Accumulations:")
        print(f"    Base Case:       {scenarios[target]['Base Case'].sum():,.2f}")
        print(f"    Optimistic:      {scenarios[target]['Optimistic'].sum():,.2f}")
        print(f"    Conservative:    {scenarios[target]['Conservative'].sum():,.2f}")
        print(f"    Severe Slowdown: {scenarios[target]['Severe Slowdown'].sum():,.2f}\n")
        
    return scenarios
