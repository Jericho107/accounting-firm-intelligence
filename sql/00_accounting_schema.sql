PRAGMA foreign_keys = ON;

CREATE TABLE IF NOT EXISTS dim_client (
    client_id TEXT PRIMARY KEY,
    client_name TEXT NOT NULL,
    sector TEXT NOT NULL,
    manager TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS fact_time (
    entry_id TEXT PRIMARY KEY,
    client_id TEXT NOT NULL,
    service_line TEXT NOT NULL,
    employee_id TEXT NOT NULL,
    work_date TEXT NOT NULL,
    hours REAL NOT NULL CHECK(hours > 0),
    labour_cost REAL NOT NULL CHECK(labour_cost >= 0),
    FOREIGN KEY(client_id) REFERENCES dim_client(client_id)
);

CREATE TABLE IF NOT EXISTS fact_invoice (
    invoice_id TEXT PRIMARY KEY,
    client_id TEXT NOT NULL,
    service_line TEXT NOT NULL,
    invoice_date TEXT NOT NULL,
    due_date TEXT NOT NULL,
    amount REAL NOT NULL CHECK(amount >= 0),
    paid_amount REAL NOT NULL CHECK(paid_amount >= 0 AND paid_amount <= amount),
    FOREIGN KEY(client_id) REFERENCES dim_client(client_id)
);

CREATE TABLE IF NOT EXISTS fact_obligation (
    obligation_id TEXT PRIMARY KEY,
    client_id TEXT NOT NULL,
    service_line TEXT NOT NULL,
    due_date TEXT NOT NULL,
    completion_pct REAL NOT NULL CHECK(completion_pct BETWEEN 0 AND 1),
    FOREIGN KEY(client_id) REFERENCES dim_client(client_id)
);

CREATE TABLE IF NOT EXISTS fact_capacity (
    employee_id TEXT PRIMARY KEY,
    manager TEXT NOT NULL,
    available_hours REAL NOT NULL CHECK(available_hours > 0)
);
