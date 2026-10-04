SELECT
    i.client_id,
    c.client_name,
    c.manager,
    SUM(i.amount - i.paid_amount) AS outstanding_ar,
    SUM(
        CASE
            WHEN julianday(:as_of_date) - julianday(i.due_date) >= 90
            THEN i.amount - i.paid_amount
            ELSE 0
        END
    ) AS ar_90_plus,
    SUM(
        CASE
            WHEN julianday(:as_of_date) - julianday(i.due_date) BETWEEN 60 AND 89
            THEN i.amount - i.paid_amount
            ELSE 0
        END
    ) AS ar_60_89,
    SUM(
        CASE
            WHEN julianday(:as_of_date) - julianday(i.due_date) BETWEEN 30 AND 59
            THEN i.amount - i.paid_amount
            ELSE 0
        END
    ) AS ar_30_59
FROM fact_invoice i
JOIN dim_client c USING (client_id)
GROUP BY i.client_id, c.client_name, c.manager
ORDER BY ar_90_plus DESC, outstanding_ar DESC;
