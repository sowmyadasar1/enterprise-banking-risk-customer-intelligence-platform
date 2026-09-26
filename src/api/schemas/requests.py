"""
Pydantic Request Schemas — Strict input validation for all prediction endpoints.
"""

from pydantic import BaseModel, ConfigDict, Field
from typing import List, Optional


# ─── Fraud Detection ────────────────────────────────────────────────
class FraudPredictionRequest(BaseModel):
    """Input for a single fraud prediction. Fields match the Feature Store output."""

    transaction_amount: float = Field(
        ..., ge=0, description="Transaction amount in USD"
    )
    merchant_category: str = Field(..., description="Merchant category code or name")
    transaction_hour: int = Field(
        ..., ge=0, le=23, description="Hour of transaction (0-23)"
    )
    transaction_day_of_week: int = Field(
        ..., ge=0, le=6, description="Day of week (0=Mon, 6=Sun)"
    )
    is_international: int = Field(
        0, ge=0, le=1, description="1 if international, 0 domestic"
    )
    is_weekend: int = Field(0, ge=0, le=1, description="1 if weekend, 0 weekday")
    customer_age: int = Field(..., ge=18, le=120, description="Customer age")
    account_age_days: int = Field(
        ..., ge=0, description="Days since account was opened"
    )
    avg_transaction_amount: float = Field(
        0.0, ge=0, description="Customer's historical avg txn"
    )
    transaction_count_30d: int = Field(
        0, ge=0, description="Transactions in last 30 days"
    )
    amount_std_30d: float = Field(
        0.0, ge=0, description="Std dev of amounts in last 30 days"
    )
    distance_from_home: float = Field(
        0.0, ge=0, description="Distance from home address (km)"
    )

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "transaction_amount": 4500.00,
                "merchant_category": "electronics",
                "transaction_hour": 2,
                "transaction_day_of_week": 5,
                "is_international": 1,
                "is_weekend": 1,
                "customer_age": 34,
                "account_age_days": 180,
                "avg_transaction_amount": 250.00,
                "transaction_count_30d": 12,
                "amount_std_30d": 350.00,
                "distance_from_home": 850.5,
            }
        }
    )


class FraudBatchRequest(BaseModel):
    """Batch fraud prediction request."""

    transactions: List[FraudPredictionRequest] = Field(
        ..., min_length=1, max_length=1000, description="List of transactions to score"
    )


# ─── Loan Default ───────────────────────────────────────────────────
class LoanDefaultRequest(BaseModel):
    """Input for a single loan default prediction."""

    loan_amount: float = Field(..., gt=0, description="Requested loan amount")
    interest_rate: float = Field(
        ..., gt=0, le=100, description="Annual interest rate (%)"
    )
    loan_term_months: int = Field(..., gt=0, le=600, description="Loan term in months")
    customer_age: int = Field(..., ge=18, le=120)
    annual_income: float = Field(..., gt=0, description="Applicant's annual income")
    credit_score: int = Field(..., ge=300, le=900, description="Credit score")
    debt_to_income_ratio: float = Field(0.0, ge=0, description="DTI ratio")
    employment_length_years: float = Field(0.0, ge=0)
    number_of_accounts: int = Field(1, ge=0)
    previous_defaults: int = Field(0, ge=0)

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "loan_amount": 25000.00,
                "interest_rate": 7.5,
                "loan_term_months": 60,
                "customer_age": 42,
                "annual_income": 85000.00,
                "credit_score": 720,
                "debt_to_income_ratio": 0.35,
                "employment_length_years": 8.0,
                "number_of_accounts": 5,
                "previous_defaults": 0,
            }
        }
    )


# ─── Customer Segmentation ──────────────────────────────────────────
class SegmentationRequest(BaseModel):
    """Input for customer segmentation assignment."""

    avg_balance: float = Field(..., description="Average account balance")
    total_transactions: int = Field(
        ..., ge=0, description="Total lifetime transactions"
    )
    avg_transaction_amount: float = Field(0.0, ge=0)
    tenure_days: int = Field(..., ge=0, description="Customer tenure in days")
    num_products: int = Field(1, ge=1, le=20, description="Number of products owned")
    credit_score: int = Field(650, ge=300, le=900)

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "avg_balance": 45000.00,
                "total_transactions": 320,
                "avg_transaction_amount": 512.75,
                "tenure_days": 1825,
                "num_products": 4,
                "credit_score": 760,
            }
        }
    )


# ─── Forecasting ────────────────────────────────────────────────────
class ForecastRequest(BaseModel):
    """Parameters for a forecast query."""

    target_metric: str = Field(
        ...,
        description="Metric to forecast",
        pattern="^(transaction_volume|revenue|loan_demand|new_customers)$",
    )
    horizon_days: int = Field(30, ge=1, le=365, description="Forecast horizon in days")

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "target_metric": "revenue",
                "horizon_days": 90,
            }
        }
    )
