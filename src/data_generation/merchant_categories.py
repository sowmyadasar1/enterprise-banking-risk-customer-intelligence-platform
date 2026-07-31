import pandas as pd
from faker import Faker
import numpy as np

def generate_merchant_categories(n: int, seed: int = 42, **dependencies) -> pd.DataFrame:
    """
    Generate synthetic data for merchant categories.
    
    Args:
        n (int): Number of records to generate.
        seed (int): Random seed for reproducibility.
        **dependencies: Dictionary of dependent DataFrames.
        
    Returns:
        pd.DataFrame: Generated merchant categories data.
    """
    fake = Faker()
    Faker.seed(seed)
    np.random.seed(seed)
    
    categories = [
        'Groceries', 'Dining', 'Travel', 'Entertainment', 'Retail',
        'Utilities', 'Health', 'Automotive', 'Education', 'Services'
    ]
    
    actual_n = min(n, len(categories))
    
    data = {
        'category_id': [fake.uuid4() for _ in range(actual_n)],
        'category_name': categories[:actual_n],
        'description': [f"Category for {cat.lower()}" for cat in categories[:actual_n]],
        'mcc_code': [str(fake.random_int(min=1000, max=9999)) for _ in range(actual_n)]
    }
    
    return pd.DataFrame(data)
