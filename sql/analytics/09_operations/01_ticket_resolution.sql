/*
=============================================================================
Business Question: How efficient is our customer support in resolving tickets?
Business Interpretation: Evaluates support employee performance and identifies bottlenecks in ticket resolution.
Decision Supported: Support staff training, process improvements, and SLA management.
Recommended Business Action: Provide additional training for employees with high resolution times and optimize support workflows.
SQL Techniques Used: Date/Time Functions, Aggregation, JOINs, Group By
=============================================================================
*/

SELECT
    t.employee_id,
    COUNT(t.ticket_id) AS total_tickets_resolved,
    AVG((strftime('%s', t.resolved_at) - strftime('%s', t.created_at)) / 3600.0) AS avg_resolution_hours,
    MIN((strftime('%s', t.resolved_at) - strftime('%s', t.created_at)) / 3600.0) AS min_resolution_hours,
    MAX((strftime('%s', t.resolved_at) - strftime('%s', t.created_at)) / 3600.0) AS max_resolution_hours
FROM
    fact_support_tickets t

WHERE
    t.status = 'Resolved'
GROUP BY
    t.employee_id
ORDER BY
    avg_resolution_hours ASC;
