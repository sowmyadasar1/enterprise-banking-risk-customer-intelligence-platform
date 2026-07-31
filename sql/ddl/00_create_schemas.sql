-- Enterprise Banking Data Warehouse Schemas
CREATE SCHEMA IF NOT EXISTS staging;    -- Temporary landing from Gold layer
CREATE SCHEMA IF NOT EXISTS dim;        -- Dimension tables
CREATE SCHEMA IF NOT EXISTS fact;       -- Fact tables
CREATE SCHEMA IF NOT EXISTS mart;       -- Data mart views
CREATE SCHEMA IF NOT EXISTS rpt;        -- Reporting views
CREATE SCHEMA IF NOT EXISTS sec;        -- Security & audit
