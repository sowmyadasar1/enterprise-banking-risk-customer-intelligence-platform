"""
Enterprise Data Warehouse Builder
Creates and populates the star-schema warehouse from Gold layer Parquet files.
Uses SQLite for local execution.
"""
import sqlite3
import pandas as pd
import os
import logging
from typing import Dict, List, Optional
from datetime import datetime

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class WarehouseBuilder:
    def __init__(self, db_path='data/warehouse/enterprise_dw.db', gold_dir='data/gold'):
        self.db_path = db_path
        self.gold_dir = gold_dir
        
        # Ensure directories exist
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
        
    def _get_conn(self):
        return sqlite3.connect(self.db_path)

    def build(self):
        logger.info(f"Building data warehouse at {self.db_path}")
        with self._get_conn() as conn:
            self._create_dimension_tables(conn)
            self._create_fact_tables(conn)
            self._create_indexes(conn)
            
            self._load_all_dimensions(conn)
            self._load_all_facts(conn)
            
            self._create_views(conn)
            
        logger.info("Data warehouse build complete.")
            
    def rebuild(self):
        logger.info(f"Rebuilding data warehouse at {self.db_path}")
        if os.path.exists(self.db_path):
            os.remove(self.db_path)
        self.build()

    def _create_dimension_tables(self, conn: sqlite3.Connection):
        logger.info("Creating dimension tables...")
        cursor = conn.cursor()
        
        # dim_date
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS dim_date (
            date_key INTEGER PRIMARY KEY,
            full_date TEXT,
            year INTEGER,
            month INTEGER,
            day INTEGER,
            quarter INTEGER,
            day_of_week INTEGER,
            day_name TEXT,
            is_weekend BOOLEAN,
            is_holiday BOOLEAN
        )
        ''')
        
        # dim_customer
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS dim_customer (
            customer_id TEXT PRIMARY KEY,
            first_name TEXT,
            last_name TEXT,
            full_name TEXT,
            date_of_birth TEXT,
            gender TEXT,
            email TEXT,
            phone_number TEXT,
            join_date TEXT,
            customer_type TEXT,
            risk_rating TEXT,
            is_active BOOLEAN,
            tenure_days INTEGER,
            tenure_years REAL,
            is_long_tenured BOOLEAN
        )
        ''')

        # dim_branch
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS dim_branch (
            branch_id TEXT PRIMARY KEY,
            branch_name TEXT,
            branch_code TEXT,
            region_id TEXT,
            address TEXT,
            city TEXT,
            state TEXT,
            zip_code TEXT,
            manager_id TEXT,
            open_date TEXT
        )
        ''')

        # dim_region
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS dim_region (
            region_id TEXT PRIMARY KEY,
            region_name TEXT,
            region_manager_id TEXT
        )
        ''')
        
        # dim_product
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS dim_product (
            product_id TEXT PRIMARY KEY,
            product_name TEXT,
            product_category TEXT,
            product_type TEXT,
            launch_date TEXT,
            interest_rate REAL,
            fee_amount REAL,
            is_active BOOLEAN
        )
        ''')
        
        # dim_merchant
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS dim_merchant (
            merchant_id TEXT PRIMARY KEY,
            merchant_name TEXT,
            merchant_category TEXT,
            merchant_mcc TEXT,
            country TEXT,
            is_online BOOLEAN
        )
        ''')

        # dim_account
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS dim_account (
            account_id TEXT PRIMARY KEY,
            customer_id TEXT,
            branch_id TEXT,
            product_id TEXT,
            account_type TEXT,
            account_status TEXT,
            open_date TEXT,
            close_date TEXT,
            current_balance REAL
        )
        ''')

        # dim_loan
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS dim_loan (
            loan_id TEXT PRIMARY KEY,
            account_id TEXT,
            customer_id TEXT,
            loan_type TEXT,
            loan_amount REAL,
            interest_rate REAL,
            term_months INTEGER,
            start_date TEXT,
            end_date TEXT,
            status TEXT
        )
        ''')

        # dim_risk
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS dim_risk (
            risk_id TEXT PRIMARY KEY,
            customer_id TEXT,
            risk_score INTEGER,
            risk_category TEXT,
            assessment_date TEXT,
            credit_score INTEGER
        )
        ''')

        # dim_campaign
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS dim_campaign (
            campaign_id TEXT PRIMARY KEY,
            campaign_name TEXT,
            campaign_type TEXT,
            start_date TEXT,
            end_date TEXT,
            budget REAL,
            target_audience TEXT
        )
        ''')

        # dim_employee
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS dim_employee (
            employee_id TEXT PRIMARY KEY,
            first_name TEXT,
            last_name TEXT,
            job_title TEXT,
            department TEXT,
            branch_id TEXT,
            hire_date TEXT
        )
        ''')
        
        conn.commit()

    def _create_fact_tables(self, conn: sqlite3.Connection):
        logger.info("Creating fact tables...")
        cursor = conn.cursor()
        
        # fact_transactions
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS fact_transactions (
            transaction_id TEXT PRIMARY KEY,
            account_id TEXT,
            merchant_id TEXT,
            transaction_type_id TEXT,
            amount REAL,
            currency TEXT,
            transaction_timestamp TEXT,
            transaction_date TEXT,
            channel TEXT,
            status TEXT,
            transaction_hour INTEGER,
            transaction_day_of_week INTEGER,
            transaction_month INTEGER,
            transaction_quarter INTEGER,
            is_weekend BOOLEAN,
            is_night_transaction BOOLEAN,
            amount_abs REAL,
            is_large_transaction BOOLEAN
        )
        ''')

        # fact_loans
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS fact_loans (
            loan_id TEXT PRIMARY KEY,
            account_id TEXT,
            customer_id TEXT,
            loan_amount REAL,
            interest_rate REAL,
            term_months INTEGER,
            start_date TEXT,
            end_date TEXT,
            status TEXT
        )
        ''')

        # fact_fraud
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS fact_fraud (
            fraud_case_id TEXT PRIMARY KEY,
            transaction_id TEXT,
            customer_id TEXT,
            fraud_type TEXT,
            reported_date TEXT,
            investigation_status TEXT,
            financial_loss REAL
        )
        ''')

        # fact_loan_payments
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS fact_loan_payments (
            payment_id TEXT PRIMARY KEY,
            loan_id TEXT,
            payment_date TEXT,
            amount_paid REAL,
            principal_amount REAL,
            interest_amount REAL,
            payment_status TEXT
        )
        ''')

        # fact_marketing_responses
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS fact_marketing_responses (
            response_id TEXT PRIMARY KEY,
            campaign_id TEXT,
            customer_id TEXT,
            response_date TEXT,
            response_type TEXT,
            channel TEXT,
            converted BOOLEAN
        )
        ''')

        # fact_support_tickets
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS fact_support_tickets (
            ticket_id TEXT PRIMARY KEY,
            customer_id TEXT,
            employee_id TEXT,
            issue_category TEXT,
            created_at TEXT,
            resolved_at TEXT,
            status TEXT,
            resolution_hours REAL
        )
        ''')

        # fact_customer_activity
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS fact_customer_activity (
            activity_id TEXT PRIMARY KEY,
            customer_id TEXT,
            activity_date TEXT,
            activity_type TEXT,
            channel TEXT,
            duration_seconds INTEGER
        )
        ''')
        
        conn.commit()

    def _create_indexes(self, conn: sqlite3.Connection):
        logger.info("Creating indexes...")
        cursor = conn.cursor()
        
        # Dimensions indexes
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_dim_account_cust ON dim_account(customer_id)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_dim_loan_cust ON dim_loan(customer_id)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_dim_risk_cust ON dim_risk(customer_id)')
        
        # Facts indexes
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_fact_txn_acc ON fact_transactions(account_id)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_fact_txn_merch ON fact_transactions(merchant_id)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_fact_txn_date ON fact_transactions(transaction_date)')
        
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_fact_fraud_txn ON fact_fraud(transaction_id)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_fact_fraud_cust ON fact_fraud(customer_id)')
        
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_fact_loan_pay_loan ON fact_loan_payments(loan_id)')
        
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_fact_mkt_camp ON fact_marketing_responses(campaign_id)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_fact_mkt_cust ON fact_marketing_responses(customer_id)')
        
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_fact_supp_cust ON fact_support_tickets(customer_id)')
        
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_fact_act_cust ON fact_customer_activity(customer_id)')
        
        conn.commit()

    def _load_dimension(self, conn: sqlite3.Connection, table_name: str, gold_path: str, column_mapping: Optional[Dict] = None):
        if not os.path.exists(gold_path):
            logger.warning(f"Gold path {gold_path} does not exist. Skipping load for {table_name}.")
            return
            
        logger.info(f"Loading {table_name} from {gold_path}")
        try:
            df = pd.read_parquet(gold_path)
            
            if column_mapping:
                df = df.rename(columns=column_mapping)
                
            # Derivations for specific dimensions
            if table_name == 'dim_customer':
                if 'first_name' in df.columns and 'last_name' in df.columns:
                    df['full_name'] = df['first_name'] + ' ' + df['last_name']
                    
            cursor = conn.cursor()
            cursor.execute(f"PRAGMA table_info({table_name})")
            table_columns = [row[1] for row in cursor.fetchall()]
            valid_columns = [col for col in df.columns if col in table_columns]
            df = df[valid_columns]
                    
            df.to_sql(table_name, conn, if_exists='append', index=False)
        except Exception as e:
            logger.error(f"Error loading {table_name}: {e}")

    def _load_fact(self, conn: sqlite3.Connection, table_name: str, gold_path: str, column_mapping: Optional[Dict] = None):
        if not os.path.exists(gold_path):
            logger.warning(f"Gold path {gold_path} does not exist. Skipping load for {table_name}.")
            return
            
        logger.info(f"Loading {table_name} from {gold_path}")
        try:
            df = pd.read_parquet(gold_path)
            
            if column_mapping:
                df = df.rename(columns=column_mapping)
                
            # Derivations for specific facts
            if table_name == 'fact_transactions':
                if 'transaction_timestamp' in df.columns:
                    # Convert to datetime and extract date
                    df['transaction_timestamp'] = pd.to_datetime(df['transaction_timestamp'])
                    df['transaction_date'] = df['transaction_timestamp'].dt.date.astype(str)
                    df['transaction_timestamp'] = df['transaction_timestamp'].astype(str)
            elif table_name == 'fact_support_tickets':
                if 'created_at' in df.columns and 'resolved_at' in df.columns:
                    created = pd.to_datetime(df['created_at'])
                    resolved = pd.to_datetime(df['resolved_at'])
                    df['resolution_hours'] = (resolved - created).dt.total_seconds() / 3600.0
                    df['created_at'] = df['created_at'].astype(str)
                    df['resolved_at'] = df['resolved_at'].astype(str)
                    
            cursor = conn.cursor()
            cursor.execute(f"PRAGMA table_info({table_name})")
            table_columns = [row[1] for row in cursor.fetchall()]
            valid_columns = [col for col in df.columns if col in table_columns]
            df = df[valid_columns]
                    
            df.to_sql(table_name, conn, if_exists='append', index=False)
        except Exception as e:
            logger.error(f"Error loading {table_name}: {e}")

    def _load_all_dimensions(self, conn: sqlite3.Connection):
        logger.info("Loading all dimensions...")
        self._load_dimension(conn, 'dim_date', os.path.join(self.gold_dir, 'reference/calendar.parquet'), {'date_id': 'date_key'})
        self._load_dimension(conn, 'dim_customer', os.path.join(self.gold_dir, 'customers/customers.parquet'))
        self._load_dimension(conn, 'dim_branch', os.path.join(self.gold_dir, 'reference/branches.parquet'))
        self._load_dimension(conn, 'dim_region', os.path.join(self.gold_dir, 'reference/regions.parquet'))
        self._load_dimension(conn, 'dim_product', os.path.join(self.gold_dir, 'reference/products.parquet'))
        self._load_dimension(conn, 'dim_merchant', os.path.join(self.gold_dir, 'finance/merchants.parquet'))
        self._load_dimension(conn, 'dim_account', os.path.join(self.gold_dir, 'finance/accounts.parquet'))
        self._load_dimension(conn, 'dim_loan', os.path.join(self.gold_dir, 'finance/loans.parquet'))
        self._load_dimension(conn, 'dim_risk', os.path.join(self.gold_dir, 'finance/customer_risk_scores.parquet'))
        self._load_dimension(conn, 'dim_campaign', os.path.join(self.gold_dir, 'customers/marketing_campaigns.parquet'))
        self._load_dimension(conn, 'dim_employee', os.path.join(self.gold_dir, 'reference/employees.parquet'))

    def _load_all_facts(self, conn: sqlite3.Connection):
        logger.info("Loading all facts...")
        self._load_fact(conn, 'fact_transactions', os.path.join(self.gold_dir, 'finance/transactions.parquet'), {'timestamp': 'transaction_timestamp'})
        self._load_fact(conn, 'fact_loans', os.path.join(self.gold_dir, 'finance/loans.parquet'))
        self._load_fact(conn, 'fact_fraud', os.path.join(self.gold_dir, 'finance/fraud_cases.parquet'))
        self._load_fact(conn, 'fact_loan_payments', os.path.join(self.gold_dir, 'finance/loan_payments.parquet'))
        self._load_fact(conn, 'fact_marketing_responses', os.path.join(self.gold_dir, 'customers/campaign_responses.parquet'))
        self._load_fact(conn, 'fact_support_tickets', os.path.join(self.gold_dir, 'customers/support_tickets.parquet'))
        self._load_fact(conn, 'fact_customer_activity', os.path.join(self.gold_dir, 'customers/login_history.parquet'))

    def _create_views(self, conn: sqlite3.Connection):
        logger.info("Creating business views...")
        cursor = conn.cursor()
        
        # vw_customer_overview
        cursor.execute('''
        CREATE VIEW IF NOT EXISTS vw_customer_overview AS
        SELECT 
            c.customer_id, c.full_name, c.customer_type, c.risk_rating,
            COUNT(DISTINCT a.account_id) AS total_accounts,
            SUM(a.current_balance) AS total_balance
        FROM dim_customer c
        LEFT JOIN dim_account a ON c.customer_id = a.customer_id
        GROUP BY c.customer_id, c.full_name, c.customer_type, c.risk_rating;
        ''')
        
        # vw_executive_kpi
        cursor.execute('''
        CREATE VIEW IF NOT EXISTS vw_executive_kpi AS
        SELECT 
            COUNT(DISTINCT c.customer_id) AS total_customers,
            SUM(a.current_balance) AS total_deposits,
            SUM(l.loan_amount) AS total_loans
        FROM dim_customer c
        LEFT JOIN dim_account a ON c.customer_id = a.customer_id
        LEFT JOIN dim_loan l ON c.customer_id = l.customer_id;
        ''')
        
        # vw_revenue_summary
        cursor.execute('''
        CREATE VIEW IF NOT EXISTS vw_revenue_summary AS
        SELECT 
            b.branch_name,
            SUM(t.amount) AS total_transaction_volume
        FROM fact_transactions t
        JOIN dim_account a ON t.account_id = a.account_id
        JOIN dim_branch b ON a.branch_id = b.branch_id
        GROUP BY b.branch_name;
        ''')

        # vw_fraud_summary
        cursor.execute('''
        CREATE VIEW IF NOT EXISTS vw_fraud_summary AS
        SELECT 
            f.fraud_type,
            COUNT(f.fraud_case_id) AS total_cases,
            SUM(f.financial_loss) AS total_loss
        FROM fact_fraud f
        GROUP BY f.fraud_type;
        ''')

        # vw_loan_portfolio
        cursor.execute('''
        CREATE VIEW IF NOT EXISTS vw_loan_portfolio AS
        SELECT 
            status,
            COUNT(loan_id) AS total_loans,
            SUM(loan_amount) AS total_principal
        FROM fact_loans
        GROUP BY status;
        ''')

        # vw_branch_performance
        cursor.execute('''
        CREATE VIEW IF NOT EXISTS vw_branch_performance AS
        SELECT 
            b.branch_name,
            COUNT(DISTINCT a.customer_id) AS total_customers,
            COUNT(DISTINCT a.account_id) AS total_accounts
        FROM dim_branch b
        LEFT JOIN dim_account a ON b.branch_id = a.branch_id
        GROUP BY b.branch_name;
        ''')

        # vw_risk_overview
        cursor.execute('''
        CREATE VIEW IF NOT EXISTS vw_risk_overview AS
        SELECT 
            risk_category,
            COUNT(customer_id) AS total_customers,
            AVG(credit_score) AS avg_credit_score
        FROM dim_risk
        GROUP BY risk_category;
        ''')

        conn.commit()

    def get_stats(self, conn: sqlite3.Connection) -> Dict[str, int]:
        cursor = conn.cursor()
        tables = [
            'dim_date', 'dim_customer', 'dim_branch', 'dim_region', 'dim_product', 
            'dim_merchant', 'dim_account', 'dim_loan', 'dim_risk', 'dim_campaign', 'dim_employee',
            'fact_transactions', 'fact_loans', 'fact_fraud', 'fact_loan_payments', 
            'fact_marketing_responses', 'fact_support_tickets', 'fact_customer_activity'
        ]
        
        stats = {}
        for table in tables:
            try:
                cursor.execute(f'SELECT COUNT(*) FROM {table}')
                stats[table] = cursor.fetchone()[0]
            except sqlite3.OperationalError:
                stats[table] = 0
                
        return stats
