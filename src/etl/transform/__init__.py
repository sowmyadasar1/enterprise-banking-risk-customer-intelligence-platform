"""
ETL Transformation Layer — Derives engineered columns for Silver and Gold layers.
All transformations are documented with business purpose.
"""

import logging
from typing import Tuple, Any

import pandas as pd
import numpy as np

from src.etl.base import BaseTransformer, PipelineResult

logger = logging.getLogger(__name__)

class DataTransformer(BaseTransformer):
    """
    Transforms clean data by deriving new features and computing aggregations.
    """

    def transform(self, df: pd.DataFrame, dataset_name: str, **context: Any) -> Tuple[pd.DataFrame, PipelineResult]:
        """
        Routes the DataFrame to the appropriate dataset-specific transformation method.
        
        Args:
            df (pd.DataFrame): The clean DataFrame to transform.
            dataset_name (str): The dataset name to determine routing.
            **context: Additional context arguments (like other dataframes for Gold layer).
            
        Returns:
            Tuple[pd.DataFrame, PipelineResult]: Transformed DataFrame and result metadata.
        """
        logger.info(f"Starting transformation for dataset: {dataset_name}")
        
        route_map = {
            'customers': self._transform_customers,
            'accounts': self._transform_accounts,
            'transactions': self._transform_transactions,
            'loans': self._transform_loans,
            'customers_risk': self._transform_customers_risk
        }
        
        transformer_func = route_map.get(dataset_name, self._transform_passthrough)
        
        try:
            transformed_df = transformer_func(df, **context)
            success = True
            errors = []
        except Exception as e:
            logger.error(f"Transformation failed for {dataset_name}: {e}")
            transformed_df = df
            success = False
            errors = [str(e)]
            
        result = PipelineResult(
            success=success,
            records_in=len(df),
            records_out=len(transformed_df),
            records_rejected=0,
            errors=errors,
            stage="transform"
        )
        logger.info(f"Finished transformation for {dataset_name}. Success: {success}")
        return transformed_df, result

    def _transform_customers(self, df: pd.DataFrame, **ctx: Any) -> pd.DataFrame:
        """Add customer related metrics like age, tenure, age group."""
        df = df.copy()
        today = pd.Timestamp.now(tz='UTC')
        
        if 'birth_year' in df.columns:
            df['age'] = today.year - df['birth_year']
            df['age'] = df['age'].fillna(0).astype(int)
            
            bins = [0, 17, 25, 35, 50, 65, float('inf')]
            labels = ['<18', '18-25', '26-35', '36-50', '51-65', '65+']
            df['age_group'] = pd.cut(df['age'], bins=bins, labels=labels, right=True)
            df['age_group'] = df['age_group'].astype(str).replace('nan', 'Unknown')
            
        if 'join_date' in df.columns:
            join_dates = pd.to_datetime(df['join_date'], utc=True)
            df['tenure_days'] = (today - join_dates).dt.days
            df['tenure_years'] = df['tenure_days'] / 365.25
            df['is_long_tenured'] = df['tenure_years'] > 5
            
        return df

    def _transform_accounts(self, df: pd.DataFrame, **ctx: Any) -> pd.DataFrame:
        """Add account related metrics like account age, utilization, and overdrawn status."""
        df = df.copy()
        today = pd.Timestamp.now(tz='UTC')
        
        if 'opened_date' in df.columns:
            opened_dates = pd.to_datetime(df['opened_date'], utc=True)
            df['account_age_days'] = (today - opened_dates).dt.days
            
        if 'balance' in df.columns and 'credit_limit' in df.columns:
            df['utilization_rate'] = np.where(
                df['credit_limit'] > 0,
                df['balance'] / df['credit_limit'],
                np.nan
            )
            
        if 'balance' in df.columns:
            df['is_overdrawn'] = df['balance'] < 0
            
        return df

    def _transform_transactions(self, df: pd.DataFrame, **ctx: Any) -> pd.DataFrame:
        """Add transaction related time boundaries and sizing."""
        df = df.copy()
        
        time_col = 'transaction_time' if 'transaction_time' in df.columns else ('timestamp' if 'timestamp' in df.columns else None)
        
        if time_col:
            dt_series = pd.to_datetime(df[time_col], utc=True)
            df['transaction_hour'] = dt_series.dt.hour
            df['transaction_day_of_week'] = dt_series.dt.dayofweek
            df['transaction_month'] = dt_series.dt.month
            df['transaction_quarter'] = dt_series.dt.quarter
            df['is_weekend'] = df['transaction_day_of_week'] >= 5
            df['is_night_transaction'] = df['transaction_hour'].isin([22, 23, 0, 1, 2, 3])
            
        if 'amount' in df.columns:
            df['amount_abs'] = df['amount'].abs()
            df['is_large_transaction'] = df['amount_abs'] > 5000
            
        return df

    def _transform_loans(self, df: pd.DataFrame, **ctx: Any) -> pd.DataFrame:
        """Add loan metrics like loan age, utilization, overdue status."""
        df = df.copy()
        today = pd.Timestamp.now(tz='UTC')
        
        if 'origination_date' in df.columns:
            origination_dates = pd.to_datetime(df['origination_date'], utc=True)
            df['loan_age_days'] = (today - origination_dates).dt.days
            
            if 'term_months' in df.columns:
                df['remaining_term_months'] = df['term_months'] - (df['loan_age_days'] // 30)
                df['remaining_term_months'] = df['remaining_term_months'].clip(lower=0)
                
        if 'outstanding_balance' in df.columns and 'principal_amount' in df.columns:
            df['loan_utilization'] = np.where(
                df['principal_amount'] > 0,
                df['outstanding_balance'] / df['principal_amount'],
                np.nan
            )
            
        if 'loan_status' in df.columns:
            df['is_overdue'] = df['loan_status'].isin(['Delinquent', 'Default'])
            
        return df

    def _transform_customers_risk(self, df: pd.DataFrame, **ctx: Any) -> pd.DataFrame:
        """Compute aggregated risk metrics for the Gold layer."""
        customers_df = ctx.get('customers_df', df)
        loans_df = ctx.get('loans_df', None)
        transactions_df = ctx.get('transactions_df', None)
        
        result_df = customers_df.copy()
        customer_id_col = 'customer_id' if 'customer_id' in result_df.columns else 'id'
        
        if loans_df is not None and not loans_df.empty and customer_id_col in loans_df.columns and 'outstanding_balance' in loans_df.columns:
            loan_totals = loans_df.groupby(customer_id_col)['outstanding_balance'].sum().reset_index()
            loan_totals = loan_totals.rename(columns={'outstanding_balance': 'total_loan_balance'})
            result_df = pd.merge(result_df, loan_totals, on=customer_id_col, how='left')
            result_df['total_loan_balance'] = result_df['total_loan_balance'].fillna(0)
            
            if 'monthly_payment' in loans_df.columns:
                loan_pmts = loans_df.groupby(customer_id_col)['monthly_payment'].sum().reset_index()
                loan_pmts = loan_pmts.rename(columns={'monthly_payment': 'total_loan_monthly_payment'})
                result_df = pd.merge(result_df, loan_pmts, on=customer_id_col, how='left')
                result_df['total_loan_monthly_payment'] = result_df['total_loan_monthly_payment'].fillna(0)
        else:
            result_df['total_loan_balance'] = 0.0
            result_df['total_loan_monthly_payment'] = 0.0
            
        if transactions_df is not None and not transactions_df.empty and customer_id_col in transactions_df.columns:
            time_col = 'transaction_time' if 'transaction_time' in transactions_df.columns else ('timestamp' if 'timestamp' in transactions_df.columns else None)
            
            tx_df = transactions_df.copy()
            
            if time_col:
                tx_df[time_col] = pd.to_datetime(tx_df[time_col], utc=True)
                today = pd.Timestamp.now(tz='UTC')
                thirty_days_ago = today - pd.Timedelta(days=30)
                recent_tx = tx_df[tx_df[time_col] >= thirty_days_ago]
                
                recent_counts = recent_tx.groupby(customer_id_col).size().reset_index(name='total_transactions_30d')
                result_df = pd.merge(result_df, recent_counts, on=customer_id_col, how='left')
                result_df['total_transactions_30d'] = result_df['total_transactions_30d'].fillna(0).astype(int)
            else:
                result_df['total_transactions_30d'] = 0
                
            if 'amount' in tx_df.columns:
                amt_stats = tx_df.groupby(customer_id_col).agg(
                    avg_transaction_amount=('amount', 'mean'),
                    max_transaction_amount=('amount', 'max')
                ).reset_index()
                result_df = pd.merge(result_df, amt_stats, on=customer_id_col, how='left')
                result_df['avg_transaction_amount'] = result_df['avg_transaction_amount'].fillna(0.0)
                result_df['max_transaction_amount'] = result_df['max_transaction_amount'].fillna(0.0)
        else:
            result_df['total_transactions_30d'] = 0
            result_df['avg_transaction_amount'] = 0.0
            result_df['max_transaction_amount'] = 0.0

        if 'avg_monthly_income' in result_df.columns and 'total_loan_monthly_payment' in result_df.columns:
            result_df['dti_proxy'] = np.where(
                result_df['avg_monthly_income'] > 0,
                result_df['total_loan_monthly_payment'] / result_df['avg_monthly_income'],
                np.nan
            )
        else:
            result_df['dti_proxy'] = np.nan
            
        return result_df

    def _transform_passthrough(self, df: pd.DataFrame, **ctx: Any) -> pd.DataFrame:
        """Returns df unchanged (for reference tables)."""
        return df.copy()
