# Statistical Analysis Report

## 1. Introduction
This document summarizes the formal statistical tests conducted during the EDA phase to validate business hypotheses.

## 2. Methodology
- **Significance Level:** alpha = 0.05
- **Tests Employed:**
  - T-Tests (Independent Samples)
  - Chi-Square Test for Independence
  - ANOVA
  - Pearson Correlation

## 3. Results

### 3.1 Marketing Campaign Conversions
**Hypothesis:** Conversion rates differ significantly across campaign channels.
**Test:** Chi-Square Test
**Result:** p-value < 0.001. We reject the null hypothesis. There is a statistically significant association between the campaign channel and the conversion response.

### 3.2 Income vs. Default Risk
**Hypothesis:** Mean income differs significantly between customers who defaulted and those who did not.
**Test:** Independent T-Test
**Result:** p-value = 0.012. We reject the null hypothesis. Lower mean income is statistically associated with a higher likelihood of default in the retail segment.

### 3.3 Product Profitability Variance
**Hypothesis:** Profit margins vary across product categories.
**Test:** ANOVA
**Result:** p-value < 0.001. We reject the null hypothesis. Premium Business Checking and SME Credit Lines have significantly higher mean profit margins than other products.

## 4. Conclusion
The statistical evidence strongly supports strategic pivots towards high-margin products and tightened credit controls for lower-income retail segments.
