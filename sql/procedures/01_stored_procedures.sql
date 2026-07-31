CREATE SCHEMA IF NOT EXISTS rpt;

-- Procedure: Daily Warehouse Refresh
CREATE OR REPLACE PROCEDURE rpt.sp_daily_refresh()
LANGUAGE plpgsql AS $$
BEGIN
    -- Refresh materialized views
    -- Log completion
    RAISE NOTICE 'Daily refresh completed at %', CURRENT_TIMESTAMP;
EXCEPTION
    WHEN OTHERS THEN
        RAISE EXCEPTION 'Daily refresh failed: %', SQLERRM;
END;
$$;

-- Procedure: Monthly KPI Refresh
CREATE OR REPLACE PROCEDURE rpt.sp_monthly_kpi_refresh()
LANGUAGE plpgsql AS $$
BEGIN
    -- Refresh KPI tables
    RAISE NOTICE 'Monthly KPI refresh completed at %', CURRENT_TIMESTAMP;
EXCEPTION
    WHEN OTHERS THEN
        RAISE EXCEPTION 'Monthly KPI refresh failed: %', SQLERRM;
END;
$$;

-- Procedure: Revenue Summary Calculator
CREATE OR REPLACE PROCEDURE rpt.sp_revenue_summary_calculator(
    p_start_date DATE,
    p_end_date DATE,
    p_branch_id INT DEFAULT NULL
)
LANGUAGE plpgsql AS $$
BEGIN
    -- Dummy logic for generating summary
    RAISE NOTICE 'Revenue Summary Calculator completed for % to % at %', p_start_date, p_end_date, CURRENT_TIMESTAMP;
EXCEPTION
    WHEN OTHERS THEN
        RAISE EXCEPTION 'Revenue Summary Calculator failed: %', SQLERRM;
END;
$$;

-- Procedure: Fraud Summary Calculator
CREATE OR REPLACE PROCEDURE rpt.sp_fraud_summary_calculator(
    p_start_date DATE,
    p_end_date DATE
)
LANGUAGE plpgsql AS $$
BEGIN
    RAISE NOTICE 'Fraud Summary Calculator completed for % to % at %', p_start_date, p_end_date, CURRENT_TIMESTAMP;
EXCEPTION
    WHEN OTHERS THEN
        RAISE EXCEPTION 'Fraud Summary Calculator failed: %', SQLERRM;
END;
$$;

-- Procedure: Customer Metrics Calculator
CREATE OR REPLACE PROCEDURE rpt.sp_customer_metrics_calculator()
LANGUAGE plpgsql AS $$
BEGIN
    RAISE NOTICE 'Customer Metrics Calculator completed at %', CURRENT_TIMESTAMP;
EXCEPTION
    WHEN OTHERS THEN
        RAISE EXCEPTION 'Customer Metrics Calculator failed: %', SQLERRM;
END;
$$;

-- Procedure: Loan Metrics Calculator
CREATE OR REPLACE PROCEDURE rpt.sp_loan_metrics_calculator()
LANGUAGE plpgsql AS $$
BEGIN
    RAISE NOTICE 'Loan Metrics Calculator completed at %', CURRENT_TIMESTAMP;
EXCEPTION
    WHEN OTHERS THEN
        RAISE EXCEPTION 'Loan Metrics Calculator failed: %', SQLERRM;
END;
$$;

-- Procedure: Branch Metrics Calculator
CREATE OR REPLACE PROCEDURE rpt.sp_branch_metrics_calculator(
    p_branch_id INT DEFAULT NULL
)
LANGUAGE plpgsql AS $$
BEGIN
    RAISE NOTICE 'Branch Metrics Calculator completed for branch % at %', p_branch_id, CURRENT_TIMESTAMP;
EXCEPTION
    WHEN OTHERS THEN
        RAISE EXCEPTION 'Branch Metrics Calculator failed: %', SQLERRM;
END;
$$;
