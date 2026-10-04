WITH available AS (
    SELECT
        manager,
        SUM(available_hours) AS available_hours
    FROM fact_capacity
    GROUP BY manager
),
worked AS (
    SELECT
        c.manager,
        SUM(t.hours) AS worked_hours
    FROM fact_capacity c
    LEFT JOIN fact_time t
        ON t.employee_id = c.employee_id
    GROUP BY c.manager
)
SELECT
    a.manager,
    a.available_hours,
    COALESCE(w.worked_hours, 0) AS worked_hours,
    CASE
        WHEN a.available_hours = 0 THEN NULL
        ELSE COALESCE(w.worked_hours, 0) / a.available_hours
    END AS utilisation_pct
FROM available a
LEFT JOIN worked w USING (manager)
ORDER BY utilisation_pct DESC;
