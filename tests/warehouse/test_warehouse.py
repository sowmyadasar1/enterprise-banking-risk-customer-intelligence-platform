import os
import sqlite3
import pytest
import pandas as pd
from src.warehouse.warehouse_builder import WarehouseBuilder

@pytest.fixture(scope="module")
def warehouse_builder(tmp_path_factory):
    # Setup temporary directories for gold data and warehouse
    temp_dir = tmp_path_factory.mktemp("dw_test")
    db_path = os.path.join(temp_dir, "test_dw.db")
    gold_dir = os.path.join(temp_dir, "gold")
    
    # Create mock gold data
    os.makedirs(os.path.join(gold_dir, 'reference'), exist_ok=True)
    os.makedirs(os.path.join(gold_dir, 'customers'), exist_ok=True)
    os.makedirs(os.path.join(gold_dir, 'finance'), exist_ok=True)
    
    # dim_date
    pd.DataFrame({'date_key': [1, 2], 'full_date': ['2023-01-01', '2023-01-02']}).to_parquet(os.path.join(gold_dir, 'reference/calendar.parquet'))
    # dim_customer
    pd.DataFrame({'customer_id': ['C1', 'C2'], 'first_name': ['John', 'Jane'], 'last_name': ['Doe', 'Smith']}).to_parquet(os.path.join(gold_dir, 'customers/customers.parquet'))
    # dim_account
    pd.DataFrame({'account_id': ['A1', 'A2'], 'customer_id': ['C1', 'C2'], 'current_balance': [100.0, 200.0], 'branch_id': ['B1', 'B2']}).to_parquet(os.path.join(gold_dir, 'finance/accounts.parquet'))
    # dim_branch
    pd.DataFrame({'branch_id': ['B1', 'B2'], 'branch_name': ['North', 'South']}).to_parquet(os.path.join(gold_dir, 'reference/branches.parquet'))
    # dim_region
    pd.DataFrame({'region_id': ['R1'], 'region_name': ['West']}).to_parquet(os.path.join(gold_dir, 'reference/regions.parquet'))
    # dim_product
    pd.DataFrame({'product_id': ['P1']}).to_parquet(os.path.join(gold_dir, 'reference/products.parquet'))
    # dim_merchant
    pd.DataFrame({'merchant_id': ['M1']}).to_parquet(os.path.join(gold_dir, 'finance/merchants.parquet'))
    # dim_loan
    pd.DataFrame({'loan_id': ['L1'], 'customer_id': ['C1'], 'loan_amount': [1000.0], 'status': ['Active']}).to_parquet(os.path.join(gold_dir, 'finance/loans.parquet'))
    # dim_risk
    pd.DataFrame({'risk_id': ['RK1'], 'customer_id': ['C1'], 'risk_category': ['Low'], 'credit_score': [800]}).to_parquet(os.path.join(gold_dir, 'finance/customer_risk_scores.parquet'))
    # dim_campaign
    pd.DataFrame({'campaign_id': ['CAMP1']}).to_parquet(os.path.join(gold_dir, 'customers/marketing_campaigns.parquet'))
    # dim_employee
    pd.DataFrame({'employee_id': ['E1']}).to_parquet(os.path.join(gold_dir, 'reference/employees.parquet'))
    
    # facts
    pd.DataFrame({'transaction_id': ['T1'], 'account_id': ['A1'], 'amount': [50.0], 'timestamp': ['2023-01-01 10:00:00']}).to_parquet(os.path.join(gold_dir, 'finance/transactions.parquet'))
    pd.DataFrame({'fraud_case_id': ['F1'], 'transaction_id': ['T1'], 'customer_id': ['C1'], 'fraud_type': ['Phishing'], 'financial_loss': [100.0]}).to_parquet(os.path.join(gold_dir, 'finance/fraud_cases.parquet'))
    pd.DataFrame({'payment_id': ['PAY1'], 'loan_id': ['L1']}).to_parquet(os.path.join(gold_dir, 'finance/loan_payments.parquet'))
    pd.DataFrame({'response_id': ['RES1']}).to_parquet(os.path.join(gold_dir, 'customers/campaign_responses.parquet'))
    pd.DataFrame({'ticket_id': ['TIC1'], 'created_at': ['2023-01-01 10:00:00'], 'resolved_at': ['2023-01-01 12:00:00']}).to_parquet(os.path.join(gold_dir, 'customers/support_tickets.parquet'))
    pd.DataFrame({'activity_id': ['ACT1']}).to_parquet(os.path.join(gold_dir, 'customers/login_history.parquet'))
    
    builder = WarehouseBuilder(db_path=db_path, gold_dir=gold_dir)
    builder.build()
    
    yield builder
    
@pytest.fixture
def conn(warehouse_builder):
    with sqlite3.connect(warehouse_builder.db_path) as c:
        yield c

def test_dimension_tables_exist(conn):
    cursor = conn.cursor()
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name LIKE 'dim_%';")
    tables = [row[0] for row in cursor.fetchall()]
    assert len(tables) == 11
    assert 'dim_customer' in tables
    assert 'dim_date' in tables

def test_fact_tables_exist(conn):
    cursor = conn.cursor()
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name LIKE 'fact_%';")
    tables = [row[0] for row in cursor.fetchall()]
    assert len(tables) == 7
    assert 'fact_transactions' in tables
    assert 'fact_fraud' in tables

def test_dimensions_populated(conn, warehouse_builder):
    stats = warehouse_builder.get_stats(conn)
    assert stats['dim_customer'] == 2
    assert stats['dim_date'] == 2
    assert stats['dim_account'] == 2

def test_facts_populated(conn, warehouse_builder):
    stats = warehouse_builder.get_stats(conn)
    assert stats['fact_transactions'] == 1
    assert stats['fact_fraud'] == 1

def test_views_execute_without_error(conn):
    cursor = conn.cursor()
    views = [
        'vw_customer_overview', 'vw_executive_kpi', 'vw_revenue_summary',
        'vw_fraud_summary', 'vw_loan_portfolio', 'vw_branch_performance',
        'vw_risk_overview'
    ]
    for view in views:
        cursor.execute(f"SELECT * FROM {view} LIMIT 1")
        # Should not raise exception

def test_no_orphan_records_fact_transactions(conn):
    cursor = conn.cursor()
    cursor.execute('''
        SELECT COUNT(*) 
        FROM fact_transactions f 
        LEFT JOIN dim_account d ON f.account_id = d.account_id 
        WHERE d.account_id IS NULL
    ''')
    count = cursor.fetchone()[0]
    assert count == 0

def test_no_orphan_records_fact_fraud(conn):
    cursor = conn.cursor()
    cursor.execute('''
        SELECT COUNT(*) 
        FROM fact_fraud f 
        LEFT JOIN dim_customer d ON f.customer_id = d.customer_id 
        WHERE d.customer_id IS NULL
    ''')
    count = cursor.fetchone()[0]
    assert count == 0

def test_indexes_exist(conn):
    cursor = conn.cursor()
    cursor.execute("SELECT name FROM sqlite_master WHERE type='index' AND name='idx_fact_txn_acc'")
    assert cursor.fetchone() is not None

def test_derived_columns_fact_transactions(conn):
    cursor = conn.cursor()
    cursor.execute("SELECT transaction_date FROM fact_transactions LIMIT 1")
    date_val = cursor.fetchone()[0]
    assert date_val == '2023-01-01'

def test_derived_columns_dim_customer(conn):
    cursor = conn.cursor()
    cursor.execute("SELECT full_name FROM dim_customer WHERE customer_id='C1'")
    full_name = cursor.fetchone()[0]
    assert full_name == 'John Doe'
