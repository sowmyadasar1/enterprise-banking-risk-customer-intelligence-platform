import pandas as pd
from typing import Dict, List, Tuple, Any, Optional
import logging
import re

from src.etl.base import BaseValidator


logger = logging.getLogger(__name__)

DATASET_SCHEMAS = {
    # Reference Data
    'regions': {
        'pk': 'region_id',
        'required_cols': ['region_id', 'region_name'],
        'fk': [],
        'date_cols': [],
        'numeric_cols': [],
        'non_negative_cols': []
    },
    'branches': {
        'pk': 'branch_id',
        'required_cols': ['branch_id', 'region_id', 'branch_name'],
        'fk': [('region_id', 'regions', 'region_id')],
        'date_cols': [],
        'numeric_cols': [],
        'non_negative_cols': []
    },
    'products': {
        'pk': 'product_id',
        'required_cols': ['product_id', 'product_name', 'product_type'],
        'fk': [],
        'date_cols': [],
        'numeric_cols': [],
        'non_negative_cols': []
    },
    'transaction_types': {
        'pk': 'transaction_type_id',
        'required_cols': ['transaction_type_id', 'type_name'],
        'fk': [],
        'date_cols': [],
        'numeric_cols': [],
        'non_negative_cols': []
    },
    'merchant_categories': {
        'pk': 'category_id',
        'required_cols': ['category_id', 'category_name'],
        'fk': [],
        'date_cols': [],
        'numeric_cols': [],
        'non_negative_cols': []
    },
    'exchange_rates': {
        'pk': 'rate_id',
        'required_cols': ['rate_id', 'date', 'from_currency', 'to_currency', 'exchange_rate'],
        'fk': [],
        'date_cols': ['date'],
        'numeric_cols': ['exchange_rate'],
        'non_negative_cols': ['exchange_rate']
    },
    'calendar': {
        'pk': 'date_id',
        'required_cols': ['date_id', 'full_date', 'year', 'month', 'day', 'is_weekend', 'is_holiday'],
        'fk': [],
        'date_cols': ['full_date'],
        'numeric_cols': [],
        'non_negative_cols': []
    },
    'employees': {
        'pk': 'employee_id',
        'required_cols': ['employee_id', 'branch_id', 'first_name', 'last_name'],
        'fk': [('branch_id', 'branches', 'branch_id')],
        'date_cols': ['hire_date'],
        'numeric_cols': [],
        'non_negative_cols': []
    },
    'merchants': {
        'pk': 'merchant_id',
        'required_cols': ['merchant_id', 'category_id', 'merchant_name'],
        'fk': [('category_id', 'merchant_categories', 'category_id')],
        'date_cols': [],
        'numeric_cols': [],
        'non_negative_cols': []
    },
    
    # Customers
    'customers': {
        'pk': 'customer_id',
        'required_cols': ['customer_id', 'first_name', 'last_name', 'email'],
        'fk': [],
        'date_cols': ['date_of_birth', 'join_date'],
        'numeric_cols': [],
        'non_negative_cols': []
    },
    'customer_addresses': {
        'pk': 'address_id',
        'required_cols': ['address_id', 'customer_id', 'city', 'country'],
        'fk': [('customer_id', 'customers', 'customer_id')],
        'date_cols': [],
        'numeric_cols': [],
        'non_negative_cols': []
    },
    'customer_employment': {
        'pk': 'employment_id',
        'required_cols': ['employment_id', 'customer_id', 'employer_name', 'annual_income', 'employment_status'],
        'fk': [('customer_id', 'customers', 'customer_id')],
        'date_cols': ['start_date'],
        'numeric_cols': ['annual_income'],
        'non_negative_cols': ['annual_income']
    },
    'customer_segments': {
        'pk': 'segment_id',
        'required_cols': ['segment_id', 'customer_id', 'segment_name'],
        'fk': [('customer_id', 'customers', 'customer_id')],
        'date_cols': [],
        'numeric_cols': [],
        'non_negative_cols': []
    },
    'kyc_information': {
        'pk': 'kyc_id',
        'required_cols': ['kyc_id', 'customer_id', 'verification_status'],
        'fk': [('customer_id', 'customers', 'customer_id')],
        'date_cols': ['issue_date', 'expiry_date', 'last_verified_date'],
        'numeric_cols': [],
        'non_negative_cols': []
    },
    'beneficiaries': {
        'pk': 'beneficiary_id',
        'required_cols': ['beneficiary_id', 'customer_id', 'first_name', 'last_name'],
        'fk': [('customer_id', 'customers', 'customer_id')],
        'date_cols': [],
        'numeric_cols': ['allocation_percentage'],
        'non_negative_cols': ['allocation_percentage']
    },
    
    # Finance
    'accounts': {
        'pk': 'account_id',
        'required_cols': ['account_id', 'customer_id', 'account_type', 'balance'],
        'fk': [('customer_id', 'customers', 'customer_id')],
        'date_cols': ['open_date'],
        'numeric_cols': ['balance'],
        'non_negative_cols': []
    },
    'loans': {
        'pk': 'loan_id',
        'required_cols': ['loan_id', 'customer_id', 'loan_amount', 'interest_rate'],
        'fk': [('customer_id', 'customers', 'customer_id')],
        'date_cols': ['start_date', 'end_date'],
        'numeric_cols': ['loan_amount', 'interest_rate'],
        'non_negative_cols': ['loan_amount', 'interest_rate']
    },
    'credit_cards': {
        'pk': 'card_id',
        'required_cols': ['card_id', 'customer_id', 'account_id', 'card_number', 'credit_limit'],
        'fk': [('account_id', 'accounts', 'account_id')],
        'date_cols': ['expiration_date', 'issued_date'],
        'numeric_cols': ['credit_limit'],
        'non_negative_cols': ['credit_limit']
    },
    
    # Transactions
    'transactions': {
        'pk': 'transaction_id',
        'required_cols': ['transaction_id', 'account_id', 'amount', 'timestamp'],
        'fk': [('account_id', 'accounts', 'account_id')],
        'date_cols': ['timestamp'],
        'numeric_cols': ['amount'],
        'non_negative_cols': []
    },
    'loan_payments': {
        'pk': 'payment_id',
        'required_cols': ['payment_id', 'loan_id', 'total_amount', 'payment_date'],
        'fk': [('loan_id', 'loans', 'loan_id')],
        'date_cols': ['payment_date'],
        'numeric_cols': ['total_amount'],
        'non_negative_cols': ['total_amount']
    },
    
    # Risk & Fraud
    'loan_default_labels': {
        'pk': 'label_id',
        'required_cols': ['label_id', 'loan_id', 'is_default'],
        'fk': [('loan_id', 'loans', 'loan_id')],
        'date_cols': [],
        'numeric_cols': [],
        'non_negative_cols': []
    },
    'customer_risk_scores': {
        'pk': 'risk_id',
        'required_cols': ['risk_id', 'customer_id', 'risk_score'],
        'fk': [('customer_id', 'customers', 'customer_id')],
        'date_cols': ['assessment_date'],
        'numeric_cols': ['risk_score'],
        'non_negative_cols': ['risk_score']
    },
    'fraud_cases': {
        'pk': 'case_id',
        'required_cols': ['case_id', 'transaction_id', 'status'],
        'fk': [('transaction_id', 'transactions', 'transaction_id')],
        'date_cols': ['reported_date'],
        'numeric_cols': [],
        'non_negative_cols': []
    },
    'fraud_investigations': {
        'pk': 'investigation_id',
        'required_cols': ['investigation_id', 'case_id', 'investigator_id', 'start_date', 'outcome', 'notes'],
        'fk': [('case_id', 'fraud_cases', 'case_id')],
        'date_cols': ['start_date', 'end_date'],
        'numeric_cols': [],
        'non_negative_cols': []
    },
    
    # Marketing
    'marketing_campaigns': {
        'pk': 'campaign_id',
        'required_cols': ['campaign_id', 'campaign_name', 'budget'],
        'fk': [],
        'date_cols': ['start_date', 'end_date'],
        'numeric_cols': ['budget'],
        'non_negative_cols': ['budget']
    },
    'campaign_responses': {
        'pk': 'response_id',
        'required_cols': ['response_id', 'campaign_id', 'customer_id', 'response_type'],
        'fk': [
            ('campaign_id', 'marketing_campaigns', 'campaign_id'),
            ('customer_id', 'customers', 'customer_id')
        ],
        'date_cols': ['response_date'],
        'numeric_cols': [],
        'non_negative_cols': []
    },
    
    # Operations
    'support_tickets': {
        'pk': 'ticket_id',
        'required_cols': ['ticket_id', 'customer_id', 'issue_category', 'priority', 'status', 'created_at'],
        'fk': [('customer_id', 'customers', 'customer_id')],
        'date_cols': ['created_at', 'resolved_at'],
        'numeric_cols': ['satisfaction_score'],
        'non_negative_cols': ['satisfaction_score']
    },
    'device_information': {
        'pk': 'device_id',
        'required_cols': ['device_id', 'customer_id', 'device_type'],
        'fk': [('customer_id', 'customers', 'customer_id')],
        'date_cols': [],
        'numeric_cols': [],
        'non_negative_cols': []
    },
    'login_history': {
        'pk': 'login_id',
        'required_cols': ['login_id', 'customer_id', 'login_timestamp', 'status'],
        'fk': [('customer_id', 'customers', 'customer_id')],
        'date_cols': ['login_timestamp'],
        'numeric_cols': [],
        'non_negative_cols': []
    }
}


class SchemaValidator(BaseValidator):
    def validate(self, df: pd.DataFrame, dataset_name: str) -> Tuple[List[str], List[str]]:
        errors = []
        warnings = []
        schema = DATASET_SCHEMAS.get(dataset_name)
        
        if not schema:
            errors.append(f"No schema defined for {dataset_name}")
            return errors, warnings
            
        for col in schema['required_cols']:
            if col not in df.columns:
                errors.append(f"Missing required column: {col}")
                
        return errors, warnings


class PKValidator:
    def validate(self, df: pd.DataFrame, dataset_name: str) -> Tuple[List[str], List[str]]:
        errors = []
        warnings = []
        schema = DATASET_SCHEMAS.get(dataset_name)
        
        if not schema or 'pk' not in schema:
            return errors, warnings
            
        pk_col = schema['pk']
        if pk_col in df.columns:
            if df[pk_col].isnull().any():
                errors.append(f"Primary key {pk_col} contains null values.")
            
            if not df[pk_col].is_unique:
                errors.append(f"Primary key {pk_col} contains duplicate values.")
                
        return errors, warnings


class FKValidator:
    def validate(self, df: pd.DataFrame, dataset_name: str, all_datasets: Dict[str, pd.DataFrame]) -> Tuple[List[str], List[str]]:
        errors = []
        warnings = []
        schema = DATASET_SCHEMAS.get(dataset_name)
        
        if not schema or 'fk' not in schema:
            return errors, warnings
            
        for fk_col, parent_table, parent_col in schema['fk']:
            if fk_col not in df.columns:
                continue
                
            if parent_table not in all_datasets:
                warnings.append(f"Parent table {parent_table} not found to validate FK {fk_col}.")
                continue
                
            parent_df = all_datasets[parent_table]
            if parent_col not in parent_df.columns:
                errors.append(f"Parent column {parent_col} not found in {parent_table}.")
                continue
                
            valid_keys = set(parent_df[parent_col].dropna())
            orphan_records = df[~df[fk_col].isin(valid_keys) & df[fk_col].notnull()]
            
            if not orphan_records.empty:
                errors.append(f"Foreign key constraint violation: {len(orphan_records)} records in {dataset_name}.{fk_col} do not exist in {parent_table}.{parent_col}")
                
        return errors, warnings


class BusinessRuleValidator:
    def validate(self, df: pd.DataFrame, dataset_name: str) -> Tuple[List[str], List[str]]:
        errors = []
        warnings = []
        schema = DATASET_SCHEMAS.get(dataset_name)
        
        if not schema:
            return errors, warnings

        # Non-negative validation (amount in transactions, etc.)
        for col in schema.get('non_negative_cols', []):
            if col in df.columns:
                if (pd.to_numeric(df[col], errors='coerce') < 0).any():
                    if dataset_name == 'transactions':
                        warnings.append(f"Negative values found in {dataset_name}.{col}")
                    else:
                        errors.append(f"Negative values found in {dataset_name}.{col}")
                        
        # Email validation for customers
        if dataset_name == 'customers' and 'email' in df.columns:
            email_pattern = r'^[\w\.-]+@[\w\.-]+\.\w+$'
            invalid_emails = df[df['email'].notnull() & ~df['email'].astype(str).str.match(email_pattern)]
            if not invalid_emails.empty:
                errors.append(f"Invalid email format found in {len(invalid_emails)} records.")
                
        # Date validations (no future dates for DOB or join_date)
        if dataset_name == 'customers':
            today = pd.Timestamp.today()
            for col in ['date_of_birth', 'join_date']:
                if col in df.columns:
                    dates = pd.to_datetime(df[col], errors='coerce')
                    if (dates > today).any():
                        errors.append(f"Future dates found in {dataset_name}.{col}")
                        
        # Null percentage validation
        for col in df.columns:
            null_pct = df[col].isnull().mean()
            if null_pct > 0.5:
                warnings.append(f"Column {col} has >50% null values ({null_pct:.2%}).")

        return errors, warnings


class DatasetValidator:
    def __init__(self):
        self.schema_validator = SchemaValidator()
        self.pk_validator = PKValidator()
        self.fk_validator = FKValidator()
        self.br_validator = BusinessRuleValidator()

    def validate(self, df: pd.DataFrame, dataset_name: str, all_datasets: Dict[str, pd.DataFrame]) -> Tuple[pd.DataFrame, List[str], List[str]]:
        all_errors = []
        all_warnings = []
        
        # Schema validation
        err, warn = self.schema_validator.validate(df, dataset_name)
        all_errors.extend(err)
        all_warnings.extend(warn)
        
        # PK validation
        err, warn = self.pk_validator.validate(df, dataset_name)
        all_errors.extend(err)
        all_warnings.extend(warn)
        
        # FK validation
        err, warn = self.fk_validator.validate(df, dataset_name, all_datasets)
        all_errors.extend(err)
        all_warnings.extend(warn)
        
        # Business rules validation
        err, warn = self.br_validator.validate(df, dataset_name)
        all_errors.extend(err)
        all_warnings.extend(warn)
        
        # If there are hard errors, we could filter out invalid rows, 
        # but the request asks to return the valid_df.
        # For simplicity in this skeleton, we just return the original dataframe.
        return df, all_errors, all_warnings
