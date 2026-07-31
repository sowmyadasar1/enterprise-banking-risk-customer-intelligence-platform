# Revenue & Transaction Forecasting Pipeline

Revenue Forecasting (Phase 7D) provides multi-day time-series predictions using classical ARIMA models.

## Business Context
Banks must anticipate cash flow to manage liquidity, schedule branch staffing, and plan marketing spend. Rather than relying on simple year-over-year assumptions, ARIMA captures seasonal trends, autocorrelation, and momentum shifts in real-time transaction data.

## Target Metrics
We trained individual ARIMA models for four critical business metrics:

| Metric | Business Use |
|--------|-------------|
| `revenue` | Net interest income and fee forecasting |
| `transaction_volume` | ATM/branch staffing optimization |
| `loan_demand` | Capital reserve planning |
| `new_customers` | Marketing campaign ROI projection |

## ARIMA Methodology
- **Model Selection**: Auto-ARIMA was used to search the optimal `(p, d, q)` order for each time series.
- **Stationarity**: The Augmented Dickey-Fuller (ADF) test was applied. Non-stationary series were differenced.
- **Evaluation**: Mean Absolute Error (MAE) and Mean Absolute Percentage Error (MAPE) on a held-out test window.
- **Confidence Intervals**: Each forecast point includes a 95% confidence band (upper and lower bounds).

## Forecast Output
```json
{
  "target_metric": "revenue",
  "horizon_days": 30,
  "forecast": [
    { "day": 1, "mean": 42500.50, "lower_bound": 38200.10, "upper_bound": 46800.90 },
    { "day": 2, "mean": 43100.25, "lower_bound": 37900.00, "upper_bound": 48300.50 }
  ],
  "cumulative_total": 1275015.00
}
```

## API Endpoint
`GET /api/v1/forecast/{metric}?horizon=30` — Returns daily forecasts with confidence intervals.
