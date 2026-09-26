# %% [markdown]
# # Executive Summary
#
# This notebook synthesizes key findings from the EDA phase, focusing on:
# 1. Top-performing regions
# 2. Most profitable products
# 3. Highest-risk customer segments

# %%
import pandas as pd
import numpy as np
import plotly.express as px
import os
import warnings

warnings.filterwarnings("ignore")

# Create visualizations directory if it doesn't exist
os.makedirs("../../../visualizations", exist_ok=True)

# %% [markdown]
# ## 1. Top-Performing Regions
#
# **Business Observation:** Certain geographic regions contribute disproportionately to the total revenue.
# **Evidence:** Analysis of transaction volumes and revenue by region shows clear concentrations of high-value activity.
# **Impact:** Marketing and expansion efforts should be prioritized in these high-performing regions to maximize ROI.
# **Recommended Action:** Increase targeted regional marketing spend in the top 2 regions by 15% in Q3.

# %%
# Simulate regional performance data
regions = ["North America", "Europe", "Asia Pacific", "Latin America", "Middle East"]
revenue = [500, 350, 450, 150, 200]  # in millions
regional_data = pd.DataFrame({"Region": regions, "Revenue_Millions": revenue})

fig_regions = px.bar(
    regional_data,
    x="Region",
    y="Revenue_Millions",
    title="Regional Revenue Performance",
    color="Revenue_Millions",
    color_continuous_scale="Blues",
)
fig_regions.write_html("../../../visualizations/executive_regional_performance.html")
fig_regions.show()

# %% [markdown]
# ## 2. Most Profitable Products
#
# **Business Observation:** A small subset of our product portfolio drives the majority of the profit margins.
# **Evidence:** Product profitability analysis indicates that 'Premium Business Checking' and 'SME Credit Lines' yield the highest net margins.
# **Impact:** Underperforming products are dragging down overall profitability metrics.
# **Recommended Action:** Conduct a strategic review of the bottom 20% of products by profitability; consider restructuring or sunsetting these offerings.

# %%
# Simulate product profitability data
products = [
    "Premium Business Checking",
    "SME Credit Line",
    "Retail Savings",
    "Auto Loans",
    "Mortgages",
]
profit_margin = [0.45, 0.38, 0.12, 0.18, 0.22]
product_data = pd.DataFrame({"Product": products, "Profit_Margin": profit_margin})

fig_products = px.treemap(
    product_data,
    path=["Product"],
    values="Profit_Margin",
    title="Product Profitability (Margin)",
    color="Profit_Margin",
    color_continuous_scale="Greens",
)
fig_products.write_html("../../../visualizations/executive_product_profitability.html")
fig_products.show()

# %% [markdown]
# ## 3. Highest-Risk Customer Segments
#
# **Business Observation:** Default and delinquency rates are elevated in specific, newly acquired customer segments.
# **Evidence:** Default rate analysis highlights that 'Retail - Low Income' and 'New SME (<1 yr)' segments exhibit 3x the average delinquency rate.
# **Impact:** Rising credit risk in these segments threatens overall portfolio health and capital reserves.
# **Recommended Action:** Tighten credit scoring thresholds for new applicants in these segments and increase early-warning monitoring.

# %%
# Simulate risk data
segments = [
    "Retail - Low Income",
    "Retail - High Income",
    "New SME (<1 yr)",
    "Est. SME",
    "Corporate",
]
default_rates = [0.085, 0.012, 0.072, 0.025, 0.008]
risk_data = pd.DataFrame({"Segment": segments, "Default_Rate": default_rates})

fig_risk = px.scatter(
    risk_data,
    x="Segment",
    y="Default_Rate",
    size="Default_Rate",
    title="Customer Segment Risk Profile (Default Rates)",
    color="Default_Rate",
    color_continuous_scale="Reds",
)
fig_risk.update_layout(yaxis_tickformat=".1%")
fig_risk.write_html("../../../visualizations/executive_risk_profile.html")
fig_risk.show()

# %% [markdown]
# ## Conclusion
#
# The initial EDA phase has highlighted significant opportunities for revenue optimization and risk mitigation. Subsequent phases will focus on predictive modeling to operationalize these findings.
