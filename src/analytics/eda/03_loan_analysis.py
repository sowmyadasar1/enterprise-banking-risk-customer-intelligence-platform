# %% [markdown]
# # Analysis: Loan Default Patterns
# This notebook covers the exploratory data analysis (EDA) of the bank's loan portfolio, 
# focusing on understanding loan default patterns and key relationships.
# We will perform bivariate analysis to understand how customer financial capacity (Total Balance) 
# and Credit Score impact the likelihood of default. We will also test the statistical significance 
# of Loan Type against Default Status using a Chi-Square test.

# %%
import pandas as pd
import sqlite3
import scipy.stats as stats
import matplotlib.pyplot as plt
import seaborn as sns
import os

# Create connection
conn = sqlite3.connect('../../data/warehouse/enterprise_dw.db')
vis_dir = '../../notebooks/eda/visualizations'
os.makedirs(vis_dir, exist_ok=True)

# %% [markdown]
# ## Data Loading
# We will extract loan information joined with customer credit scores and account balances.
# Note: Since 'Income' is not explicitly available, we will use 'Total Balance' across accounts as a proxy for customer financial capacity.

# %%
query = """
SELECT 
    l.loan_id,
    l.loan_type,
    l.loan_amount,
    l.status,
    r.credit_score,
    COALESCE(c_overview.total_balance, 0) as total_balance,
    CASE WHEN l.status IN ('Default', 'Charged Off', 'Late (31-120 days)') THEN 1 ELSE 0 END as is_default
FROM dim_loan l
LEFT JOIN dim_risk r ON l.customer_id = r.customer_id
LEFT JOIN vw_customer_overview c_overview ON l.customer_id = c_overview.customer_id
"""
df_loans = pd.read_sql_query(query, conn)
for col in df_loans.columns:
    if df_loans[col].dtype == 'object':
        try: df_loans[col] = pd.to_numeric(df_loans[col])
        except: pass
df_loans.fillna(0, inplace=True)
df_loans.head()

# %% [markdown]
# ## Bivariate Analysis: Total Balance vs. Loan Amount
# This analysis helps us understand if customers with higher account balances tend to take larger or smaller loans.

# %%
plt.figure(figsize=(10, 6))
sns.scatterplot(data=df_loans, x='total_balance', y='loan_amount', hue='is_default', alpha=0.6)
plt.title('Total Balance vs Loan Amount (colored by Default)')
plt.xlabel('Total Balance (Proxy for Income)')
plt.ylabel('Loan Amount')
plt.savefig(f'{vis_dir}/loan_balance_vs_amount.png', bbox_inches='tight')
plt.show()

# %% [markdown]
# **Business Interpretation:**
# Observing the scatter plot, we can identify patterns indicating whether high loan amounts relative to total balances are more susceptible to default. We can also see the general distribution of our lending relative to customer liquidity.

# %% [markdown]
# ## Bivariate Analysis: Credit Score vs. Default
# We analyze how the customer's credit score correlates with their default status. We expect lower credit scores to have a higher incidence of default.

# %%
plt.figure(figsize=(10, 6))
sns.boxplot(data=df_loans, x='is_default', y='credit_score')
plt.title('Credit Score Distribution by Default Status')
plt.xlabel('Is Default (1=Yes, 0=No)')
plt.ylabel('Credit Score')
plt.savefig(f'{vis_dir}/loan_credit_score_vs_default.png', bbox_inches='tight')
plt.show()

# %% [markdown]
# **Business Interpretation:**
# The boxplot shows the median and spread of credit scores for both default and non-default groups. A significantly lower median credit score in the default group confirms that our credit scoring model aligns with risk. This visual can help in setting credit score thresholds for future loan approvals.

# %% [markdown]
# ## Statistical Testing: Chi-Square Test (Loan Type vs Default Status)
# We perform a Chi-Square test of independence to determine if there's a statistically significant association between the type of loan and the likelihood of default.

# %%
contingency_table = pd.crosstab(df_loans['loan_type'], df_loans['is_default'])
print("Contingency Table (Loan Type vs Default):")
print(contingency_table)

chi2, p_val, dof, expected = stats.chi2_contingency(contingency_table)
print(f"\nChi-Square Statistic: {chi2:.4f}")
print(f"P-value: {p_val:.4e}")

# %% [markdown]
# **Business Interpretation:**
# - **Null Hypothesis (H0):** Loan Type and Default Status are independent.
# - **Alternative Hypothesis (H1):** There is an association between Loan Type and Default Status.
# 
# Given the p-value, if it is less than our significance level (e.g., 0.05), we reject the null hypothesis. This implies that certain loan products might carry inherently higher risks, and the business should potentially adjust interest rates or underwriting criteria for those specific loan types.
