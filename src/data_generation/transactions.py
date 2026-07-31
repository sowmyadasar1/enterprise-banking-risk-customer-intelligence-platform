import pandas as pd
from faker import Faker
import numpy as np

def generate_transactions(n: int, seed: int = 42, **dependencies) -> pd.DataFrame:
    """
    Generate synthetic data for transactions.
    
    Args:
        n (int): Number of records to generate.
        seed (int): Random seed for reproducibility.
        **dependencies: Dictionary of dependent DataFrames.
        
    Returns:
        pd.DataFrame: Generated transactions data.
    """
    fake = Faker()
    Faker.seed(seed)
    np.random.seed(seed)
    
    accounts_df = dependencies.get('accounts')
    merchants_df = dependencies.get('merchants')
    transaction_types_df = dependencies.get('transaction_types')
    
    account_ids = accounts_df['account_id'].tolist() if accounts_df is not None and not accounts_df.empty else [fake.uuid4() for _ in range(n)]
    merchant_ids = merchants_df['merchant_id'].tolist() if merchants_df is not None and not merchants_df.empty else [fake.uuid4() for _ in range(n)]
    type_ids = transaction_types_df['transaction_type_id'].tolist() if transaction_types_df is not None and not transaction_types_df.empty else [fake.uuid4() for _ in range(n)]
    
    channels = ['ONLINE', 'IN_BRANCH', 'ATM', 'MOBILE_APP', 'POS']
    statuses = ['COMPLETED', 'PENDING', 'FAILED', 'REVERSED']
    
    data = {
        'transaction_id': [fake.uuid4() for _ in range(n)],
        'account_id': np.random.choice(account_ids, size=n),
        'merchant_id': np.random.choice(merchant_ids, size=n),
        'transaction_type_id': np.random.choice(type_ids, size=n),
        'amount': np.round(np.random.lognormal(mean=4, sigma=1.2, size=n), 2),
        'currency': 'USD',
        'timestamp': [fake.date_time_between(start_date='-1y', end_date='now') for _ in range(n)],
        'channel': np.random.choice(channels, size=n),
        'status': np.random.choice(statuses, size=n, p=[0.9, 0.05, 0.04, 0.01])
    }
    
    return pd.DataFrame(data)
