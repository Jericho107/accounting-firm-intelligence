WITH fees AS (
    SELECT
        client_id,
        service_line,
        SUM(amount) AS billed_fees
    FROM fact_invoice
    GROUP BY client_id, service_line
),
labour AS (
    SELECT
        client_id,
        service_line,
        SUM(hours) AS hours_worked,
        SUM(labour_cost) AS labour_cost
    FROM fact_time
    GROUP BY client_id, service_line
)
SELECT
    c.client_id,
    c.client_name,
    c.manager,
    f.service_line,
    f.billed_fees,
    COALESCE(l.hours_worked, 0) AS hours_worked,
    COALESCE(l.labour_cost, 0) AS labour_cost,
    f.billed_fees - COALESCE(l.labour_cost, 0) AS contribution,
    CASE
        WHEN f.billed_fees = 0 THEN NULL
        ELSE (f.billed_fees - COALESCE(l.labour_cost, 0)) / f.billed_fees
    END AS contribution_margin_pct,
    CASE
        WHEN COALESCE(l.hours_worked, 0) = 0 THEN NULL
        ELSE f.billed_fees / l.hours_worked
    END AS effective_hourly_rate
FROM fees f
JOIN dim_client c USING (client_id)
LEFT JOIN labour l USING (client_id, service_line)
ORDER BY contribution ASC, c.client_id;
