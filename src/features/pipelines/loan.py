"""
Loan Features Pipeline
Generates loan-level features aggregated per customer from dim_loan and fact_loan_payments.
"""
import pandas as pd
import numpy as np


def build_loan_features(conn):
    """Build comprehensive loan features per customer."""
    print("[Loan] Loading loan tables...")

    df_loan = pd.read_sql("SELECT * FROM dim_loan", conn)
    df_pay = pd.read_sql("SELECT * FROM fact_loan_payments", conn)

    # Coerce numerics
    for col in ['loan_amount', 'interest_rate', 'term_months']:
        df_loan[col] = pd.to_numeric(df_loan[col], errors='coerce').fillna(0)
    for col in ['amount_paid', 'principal_amount', 'interest_amount']:
        df_pay[col] = pd.to_numeric(df_pay[col], errors='coerce').fillna(0)

    df_loan['start_date'] = pd.to_datetime(df_loan['start_date'], errors='coerce', utc=True).dt.tz_localize(None)
    df_loan['end_date'] = pd.to_datetime(df_loan['end_date'], errors='coerce', utc=True).dt.tz_localize(None)
    today = pd.Timestamp.now().tz_localize(None)

    # --- Loan-level features ---
    df_loan['loan_age_days'] = (today - df_loan['start_date']).dt.days.fillna(0).astype(int)
    df_loan['expected_monthly_payment'] = np.where(
        df_loan['term_months'] > 0,
        df_loan['loan_amount'] / df_loan['term_months'],
        0
    )

    # --- Payment aggregations per loan ---
    pay_agg = df_pay.groupby('loan_id').agg(
        total_paid=('amount_paid', 'sum'),
        total_principal_paid=('principal_amount', 'sum'),
        total_interest_paid=('interest_amount', 'sum'),
        payment_count=('payment_id', 'count'),
        late_payment_count=('payment_status', lambda x: (x == 'Late').sum()),
        missed_payment_count=('payment_status', lambda x: (x == 'Missed').sum()),
    ).reset_index()

    df_loan = df_loan.merge(pay_agg, on='loan_id', how='left')
    df_loan['total_paid'] = df_loan['total_paid'].fillna(0)
    df_loan['payment_count'] = df_loan['payment_count'].fillna(0).astype(int)
    df_loan['late_payment_count'] = df_loan['late_payment_count'].fillna(0).astype(int)
    df_loan['missed_payment_count'] = df_loan['missed_payment_count'].fillna(0).astype(int)

    # Remaining balance
    df_loan['remaining_balance'] = (df_loan['loan_amount'] - df_loan['total_paid']).clip(lower=0)

    # Repayment rate
    df_loan['repayment_rate'] = np.where(
        df_loan['loan_amount'] > 0,
        df_loan['total_paid'] / df_loan['loan_amount'],
        0
    )

    # Loan utilization (remaining / original)
    df_loan['loan_utilization'] = np.where(
        df_loan['loan_amount'] > 0,
        df_loan['remaining_balance'] / df_loan['loan_amount'],
        0
    )

    # Interest burden
    df_loan['interest_burden'] = np.where(
        df_loan['total_paid'] > 0,
        df_loan['total_interest_paid'] / df_loan['total_paid'],
        0
    )

    # Missed payment ratio
    df_loan['missed_payment_ratio'] = np.where(
        df_loan['payment_count'] > 0,
        df_loan['missed_payment_count'] / df_loan['payment_count'],
        0
    )

    # --- Aggregate to customer level ---
    cust_agg = df_loan.groupby('customer_id').agg(
        total_loan_amount=('loan_amount', 'sum'),
        total_loans=('loan_id', 'nunique'),
        avg_loan_amount=('loan_amount', 'mean'),
        avg_interest_rate=('interest_rate', 'mean'),
        avg_loan_age_days=('loan_age_days', 'mean'),
        total_remaining_balance=('remaining_balance', 'sum'),
        avg_repayment_rate=('repayment_rate', 'mean'),
        avg_loan_utilization=('loan_utilization', 'mean'),
        total_late_payments=('late_payment_count', 'sum'),
        total_missed_payments=('missed_payment_count', 'sum'),
        total_payments=('payment_count', 'sum'),
        avg_interest_burden=('interest_burden', 'mean'),
        avg_missed_payment_ratio=('missed_payment_ratio', 'mean'),
    ).reset_index()

    # Installment ratio: total expected monthly / number of loans
    cust_agg['avg_installment'] = np.where(
        cust_agg['total_loans'] > 0,
        cust_agg['total_loan_amount'] / cust_agg['total_loans'],
        0
    )

    cust_agg = cust_agg.fillna(0).round(4)
    print(f"[Loan] Generated {len(cust_agg)} rows, {len(cust_agg.columns)} features.")
    return cust_agg
