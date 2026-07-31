import pandas as pd
from faker import Faker
import numpy as np
from datetime import timedelta, date

def generate_exchange_rates(n: int, seed: int = 42, **dependencies) -> pd.DataFrame:
    """
    Generate synthetic data for exchange rates.
    
    Args:
        n (int): Number of records to generate.
        seed (int): Random seed for reproducibility.
        **dependencies: Dictionary of dependent DataFrames.
        
    Returns:
        pd.DataFrame: Generated exchange rates data.
    """
    fake = Faker()
    Faker.seed(seed)
    np.random.seed(seed)
    
    currencies = ['EUR', 'GBP', 'JPY', 'CAD', 'AUD', 'CHF', 'CNY', 'INR']
    base_rates = {'EUR': 0.9, 'GBP': 0.75, 'JPY': 110, 'CAD': 1.25, 'AUD': 1.3, 'CHF': 0.95, 'CNY': 6.5, 'INR': 75}
    
    data = []
    start_date = date.today() - timedelta(days=n)
    
    for i in range(n):
        current_date = start_date + timedelta(days=i)
        for cur in currencies:
            noise = np.random.normal(0, 0.01 * base_rates[cur])
            rate = base_rates[cur] + noise
            data.append({
                'rate_id': fake.uuid4(),
                'date': current_date,
                'from_currency': 'USD',
                'to_currency': cur,
                'exchange_rate': round(rate, 4)
            })
            base_rates[cur] = rate # Random walk
            
    df = pd.DataFrame(data)
    if len(df) > n:
        df = df.sample(n).reset_index(drop=True)
    return df
