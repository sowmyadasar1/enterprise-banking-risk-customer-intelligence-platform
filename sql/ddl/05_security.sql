-- Read-only analytics role
CREATE ROLE analytics_readonly;
GRANT USAGE ON SCHEMA dim, fact, rpt, mart TO analytics_readonly;
GRANT SELECT ON ALL TABLES IN SCHEMA dim, fact, rpt, mart TO analytics_readonly;

-- Admin role
CREATE ROLE warehouse_admin;
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA dim, fact, rpt, mart, staging, sec TO warehouse_admin;

-- Least privilege application role
CREATE ROLE app_service;
GRANT USAGE ON SCHEMA dim, fact, rpt TO app_service;
GRANT SELECT ON ALL TABLES IN SCHEMA dim, fact, rpt TO app_service;
