import argparse
import logging
import random
from typing import Dict
import pandas as pd
import numpy as np

from src.data_generation.utils import save_dataset, generate_metadata

# Assume generator modules exist in src.data_generation
# If they are placeholders, these will mock them
try:
    from src.data_generation.reference_data import generate_regions, generate_branches
except ImportError:

    def generate_regions(size: int, seed: int, **kwargs) -> pd.DataFrame:
        return pd.DataFrame(
            {
                "region_id": range(size),
                "region_name": [f"Region_{i}" for i in range(size)],
            }
        )

    def generate_branches(
        size: int, seed: int, regions_df: pd.DataFrame, **kwargs
    ) -> pd.DataFrame:
        region_ids = (
            regions_df["region_id"].tolist() if not regions_df.empty else range(size)
        )
        return pd.DataFrame(
            {"branch_id": range(size), "region_id": np.random.choice(region_ids, size)}
        )


try:
    from src.data_generation.customers import generate_customers
    from src.data_generation.accounts import generate_accounts
except ImportError:

    def generate_customers(
        size: int, seed: int, branches_df: pd.DataFrame = None, **kwargs
    ) -> pd.DataFrame:
        return pd.DataFrame(
            {"customer_id": range(size), "name": [f"Cust_{i}" for i in range(size)]}
        )

    def generate_accounts(
        size: int, seed: int, customers_df: pd.DataFrame, **kwargs
    ) -> pd.DataFrame:
        customer_ids = (
            customers_df["customer_id"].tolist()
            if not customers_df.empty
            else range(size)
        )
        return pd.DataFrame(
            {
                "account_id": range(size),
                "customer_id": np.random.choice(customer_ids, size),
            }
        )


try:
    from src.data_generation.transactions import generate_transactions
except ImportError:

    def generate_transactions(
        size: int, seed: int, accounts_df: pd.DataFrame, **kwargs
    ) -> pd.DataFrame:
        account_ids = (
            accounts_df["account_id"].tolist() if not accounts_df.empty else range(size)
        )
        return pd.DataFrame(
            {
                "transaction_id": range(size),
                "account_id": np.random.choice(account_ids, size),
                "amount": np.random.rand(size) * 1000,
            }
        )


try:
    from src.data_generation.finance import (
        generate_gl_accounts,
        generate_journal_entries,
    )
except ImportError:

    def generate_gl_accounts(size: int, seed: int, **kwargs) -> pd.DataFrame:
        return pd.DataFrame({"gl_id": range(size)})

    def generate_journal_entries(
        size: int,
        seed: int,
        gl_df: pd.DataFrame,
        transactions_df: pd.DataFrame = None,
        **kwargs,
    ) -> pd.DataFrame:
        return pd.DataFrame({"je_id": range(size)})


try:
    from src.data_generation.risk import (
        generate_credit_scores,
        generate_loan_applications,
    )
except ImportError:

    def generate_credit_scores(
        size: int, seed: int, customers_df: pd.DataFrame, **kwargs
    ) -> pd.DataFrame:
        return pd.DataFrame({"score_id": range(size)})

    def generate_loan_applications(
        size: int, seed: int, customers_df: pd.DataFrame, **kwargs
    ) -> pd.DataFrame:
        return pd.DataFrame({"app_id": range(size)})


try:
    from src.data_generation.fraud import generate_fraud_alerts, generate_watchlists
except ImportError:

    def generate_fraud_alerts(
        size: int,
        seed: int,
        transactions_df: pd.DataFrame,
        watchlists_df: pd.DataFrame = None,
        **kwargs,
    ) -> pd.DataFrame:
        return pd.DataFrame({"alert_id": range(size)})

    def generate_watchlists(size: int, seed: int, **kwargs) -> pd.DataFrame:
        return pd.DataFrame({"watchlist_id": range(size)})


try:
    from src.data_generation.marketing import generate_campaigns, generate_interactions
except ImportError:

    def generate_campaigns(size: int, seed: int, **kwargs) -> pd.DataFrame:
        return pd.DataFrame({"campaign_id": range(size)})

    def generate_interactions(
        size: int,
        seed: int,
        customers_df: pd.DataFrame,
        campaigns_df: pd.DataFrame,
        **kwargs,
    ) -> pd.DataFrame:
        return pd.DataFrame({"interaction_id": range(size)})


try:
    from src.data_generation.operations import generate_tickets, generate_employees
except ImportError:

    def generate_tickets(
        size: int,
        seed: int,
        customers_df: pd.DataFrame,
        employees_df: pd.DataFrame = None,
        **kwargs,
    ) -> pd.DataFrame:
        return pd.DataFrame({"ticket_id": range(size)})

    def generate_employees(
        size: int, seed: int, branches_df: pd.DataFrame, **kwargs
    ) -> pd.DataFrame:
        return pd.DataFrame({"employee_id": range(size)})


logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


class DataGenerator:
    """
    Main orchestrator for synthetic data generation pipeline.
    Coordinates generation of all datasets in the correct dependency order.
    """

    def __init__(self, scale_factor: float = 1.0, seed: int = 42):
        self.scale_factor = scale_factor
        self.seed = seed
        self.dataframes: Dict[str, pd.DataFrame] = {}

        # Base sizes for scale_factor = 1.0
        self.base_sizes = {
            "regions": 5,
            "branches": 50,
            "gl_accounts": 200,
            "watchlists": 1000,
            "campaigns": 20,
            "employees": 1000,
            "customers": 10000,
            "accounts": 15000,
            "transactions": 500000,
            "journal_entries": 100000,
            "credit_scores": 10000,
            "loan_applications": 2000,
            "fraud_alerts": 5000,
            "interactions": 50000,
            "tickets": 10000,
        }

        # Set seeds
        random.seed(self.seed)
        np.random.seed(self.seed)

    def _get_size(self, entity: str) -> int:
        return max(1, int(self.base_sizes.get(entity, 1000) * self.scale_factor))

    def _process_and_save(
        self, df: pd.DataFrame, category: str, name: str, description: str = ""
    ):
        self.dataframes[name] = df
        save_dataset(df, category, name, formats=["csv", "parquet", "json"])
        generate_metadata(df, category, name, description)

    def generate_all(self):
        """
        Run the generation pipeline in topological order of dependencies.
        Order:
        1. Reference Data (Regions, Branches)
        2. Independent Data (GL Accounts, Watchlists, Campaigns)
        3. Employees (depends on Branches)
        4. Customers (depends on Branches)
        5. Accounts (depends on Customers)
        6. Transactions (depends on Accounts)
        7. Journal Entries (depends on GL Accounts, Transactions)
        8. Risk & Loan (depends on Customers)
        9. Fraud (depends on Transactions, Watchlists)
        10. Marketing Interactions (depends on Customers, Campaigns)
        11. Operations Tickets (depends on Customers, Employees)
        """
        logger.info(
            f"Starting data generation with scale factor {self.scale_factor} and seed {self.seed}"
        )

        # Level 1: Reference Data
        logger.info("Generating Reference Data...")
        regions_df = generate_regions(size=self._get_size("regions"), seed=self.seed)
        self._process_and_save(
            regions_df, "reference_data", "regions", "Geographic regions"
        )

        branches_df = generate_branches(
            size=self._get_size("branches"), seed=self.seed, regions_df=regions_df
        )
        self._process_and_save(
            branches_df, "reference_data", "branches", "Bank branches"
        )

        gl_accounts_df = generate_gl_accounts(
            size=self._get_size("gl_accounts"), seed=self.seed
        )
        self._process_and_save(
            gl_accounts_df, "finance", "gl_accounts", "General Ledger accounts"
        )

        watchlists_df = generate_watchlists(
            size=self._get_size("watchlists"), seed=self.seed
        )
        self._process_and_save(
            watchlists_df, "fraud", "watchlists", "AML and sanction watchlists"
        )

        campaigns_df = generate_campaigns(
            size=self._get_size("campaigns"), seed=self.seed
        )
        self._process_and_save(
            campaigns_df, "marketing", "campaigns", "Marketing campaigns"
        )

        # Level 2: Operations (Employees)
        logger.info("Generating Employees...")
        employees_df = generate_employees(
            size=self._get_size("employees"), seed=self.seed, branches_df=branches_df
        )
        self._process_and_save(
            employees_df, "operations", "employees", "Bank employees"
        )

        # Level 3: Customers & Accounts
        logger.info("Generating Customers and Accounts...")
        customers_df = generate_customers(
            size=self._get_size("customers"), seed=self.seed, branches_df=branches_df
        )
        self._process_and_save(
            customers_df, "customers", "customers", "Customer profiles"
        )

        accounts_df = generate_accounts(
            size=self._get_size("accounts"), seed=self.seed, customers_df=customers_df
        )
        self._process_and_save(
            accounts_df, "customers", "accounts", "Customer accounts"
        )

        # Level 4: Transactions
        logger.info("Generating Transactions...")
        transactions_df = generate_transactions(
            size=self._get_size("transactions"), seed=self.seed, accounts_df=accounts_df
        )
        self._process_and_save(
            transactions_df, "transactions", "transactions", "Financial transactions"
        )

        # Level 5: Downstream Finance, Risk, Fraud, Marketing, Operations
        logger.info("Generating Downstream Entity Data...")
        journal_entries_df = generate_journal_entries(
            size=self._get_size("journal_entries"),
            seed=self.seed,
            gl_df=gl_accounts_df,
            transactions_df=transactions_df,
        )
        self._process_and_save(
            journal_entries_df,
            "finance",
            "journal_entries",
            "Accounting journal entries",
        )

        credit_scores_df = generate_credit_scores(
            size=self._get_size("credit_scores"),
            seed=self.seed,
            customers_df=customers_df,
        )
        self._process_and_save(
            credit_scores_df, "risk", "credit_scores", "Customer credit scores"
        )

        loan_applications_df = generate_loan_applications(
            size=self._get_size("loan_applications"),
            seed=self.seed,
            customers_df=customers_df,
        )
        self._process_and_save(
            loan_applications_df, "risk", "loan_applications", "Loan applications"
        )

        fraud_alerts_df = generate_fraud_alerts(
            size=self._get_size("fraud_alerts"),
            seed=self.seed,
            transactions_df=transactions_df,
            watchlists_df=watchlists_df,
        )
        self._process_and_save(
            fraud_alerts_df, "fraud", "fraud_alerts", "Fraud alerts and cases"
        )

        interactions_df = generate_interactions(
            size=self._get_size("interactions"),
            seed=self.seed,
            customers_df=customers_df,
            campaigns_df=campaigns_df,
        )
        self._process_and_save(
            interactions_df,
            "marketing",
            "interactions",
            "Customer marketing interactions",
        )

        tickets_df = generate_tickets(
            size=self._get_size("tickets"),
            seed=self.seed,
            customers_df=customers_df,
            employees_df=employees_df,
        )
        self._process_and_save(
            tickets_df, "operations", "tickets", "Customer support tickets"
        )

        logger.info("Data generation completed successfully!")
        return self.dataframes


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Synthetic Data Generation Pipeline Orchestrator"
    )
    parser.add_argument(
        "--scale_factor",
        type=float,
        default=1.0,
        help="Multiplier for the number of records to generate",
    )
    parser.add_argument(
        "--seed", type=int, default=42, help="Random seed for reproducibility"
    )

    args = parser.parse_args()

    generator = DataGenerator(scale_factor=args.scale_factor, seed=args.seed)
    generator.generate_all()
