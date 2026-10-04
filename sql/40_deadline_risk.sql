SELECT
    o.client_id,
    c.client_name,
    c.manager,
    o.service_line,
    o.due_date,
    o.completion_pct,
    CAST(julianday(o.due_date) - julianday(:as_of_date) AS INTEGER) AS days_to_due,
    CASE
        WHEN julianday(o.due_date) - julianday(:as_of_date) <= 7
             AND o.completion_pct < 0.80
        THEN 'high'
        WHEN julianday(o.due_date) - julianday(:as_of_date) <= 14
             AND o.completion_pct < 0.70
        THEN 'medium'
        ELSE 'low'
    END AS deadline_risk
FROM fact_obligation o
JOIN dim_client c USING (client_id)
ORDER BY
    CASE deadline_risk WHEN 'high' THEN 1 WHEN 'medium' THEN 2 ELSE 3 END,
    days_to_due;
