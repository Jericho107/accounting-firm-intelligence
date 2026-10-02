from __future__ import annotations

import sqlite3
from collections.abc import Iterable
from dataclasses import asdict, dataclass
from datetime import date
from pathlib import Path

from .core import analyse


@dataclass(frozen=True)
class Client:
    client_id: str
    client_name: str
    sector: str
    manager: str


@dataclass(frozen=True)
class TimeEntry:
    entry_id: str
    client_id: str
    service_line: str
    employee_id: str
    work_date: date
    hours: float
    cost_rate: float


@dataclass(frozen=True)
class Invoice:
    invoice_id: str
    client_id: str
    service_line: str
    invoice_date: date
    due_date: date
    amount: float
    paid_amount: float


@dataclass(frozen=True)
class Obligation:
    obligation_id: str
    client_id: str
    service_line: str
    due_date: date
    completion_pct: float


@dataclass(frozen=True)
class Capacity:
    employee_id: str
    manager: str
    available_hours: float


@dataclass(frozen=True)
class PracticeData:
    clients: tuple[Client, ...]
    time_entries: tuple[TimeEntry, ...]
    invoices: tuple[Invoice, ...]
    obligations: tuple[Obligation, ...]
    capacity: tuple[Capacity, ...]


def sample_practice() -> PracticeData:
    return PracticeData(
        clients=(
            Client("C001", "Atlas Retail", "retail", "M01"),
            Client("C002", "Northstar Labs", "technology", "M02"),
            Client("C003", "Riviera Foods", "hospitality", "M01"),
        ),
        time_entries=(
            TimeEntry("T001", "C001", "accounts", "E01", date(2026, 9, 3), 40, 70),
            TimeEntry("T002", "C001", "accounts", "E02", date(2026, 9, 12), 25, 96),
            TimeEntry("T003", "C002", "tax", "E03", date(2026, 9, 8), 42, 85),
            TimeEntry("T004", "C002", "tax", "E04", date(2026, 9, 21), 40, 88.25),
            TimeEntry("T005", "C003", "advisory", "E01", date(2026, 9, 14), 35, 90),
            TimeEntry("T006", "C003", "advisory", "E02", date(2026, 9, 25), 40, 91.25),
        ),
        invoices=(
            Invoice("I001", "C001", "accounts", date(2026, 8, 15), date(2026, 9, 14), 9000, 6000),
            Invoice("I002", "C002", "tax", date(2026, 6, 20), date(2026, 7, 20), 6500, 300),
            Invoice("I003", "C003", "advisory", date(2026, 9, 15), date(2026, 10, 15), 15000, 15000),
        ),
        obligations=(
            Obligation("O001", "C001", "accounts", date(2026, 10, 20), 0.85),
            Obligation("O002", "C002", "tax", date(2026, 10, 8), 0.52),
            Obligation("O003", "C003", "advisory", date(2026, 11, 5), 0.90),
        ),
        capacity=(
            Capacity("E01", "M01", 90),
            Capacity("E02", "M01", 90),
            Capacity("E03", "M02", 50),
            Capacity("E04", "M02", 50),
        ),
    )


def _unique(rows: Iterable[object], field: str) -> None:
    values = [getattr(row, field) for row in rows]
    if len(values) != len(set(values)):
        raise ValueError(f"duplicate {field}")


def validate_practice(data: PracticeData) -> None:
    _unique(data.clients, "client_id")
    _unique(data.time_entries, "entry_id")
    _unique(data.invoices, "invoice_id")
    _unique(data.obligations, "obligation_id")
    _unique(data.capacity, "employee_id")
    clients = {row.client_id for row in data.clients}
    for row in data.time_entries:
        if row.client_id not in clients or row.hours <= 0 or row.cost_rate < 0:
            raise ValueError("invalid time entry")
    for row in data.invoices:
        if row.client_id not in clients or row.amount < 0 or not 0 <= row.paid_amount <= row.amount:
            raise ValueError("invalid invoice")
    for row in data.obligations:
        if row.client_id not in clients or not 0 <= row.completion_pct <= 1:
            raise ValueError("invalid obligation")
    if any(row.available_hours <= 0 for row in data.capacity):
        raise ValueError("invalid capacity")


def build_warehouse(data: PracticeData, path: str | Path = ":memory:") -> sqlite3.Connection:
    validate_practice(data)
    connection = sqlite3.connect(path)
    connection.executescript(
        """
        CREATE TABLE dim_client (
            client_id TEXT PRIMARY KEY, client_name TEXT NOT NULL, sector TEXT NOT NULL, manager TEXT NOT NULL
        );
        CREATE TABLE fact_time (
            entry_id TEXT PRIMARY KEY, client_id TEXT NOT NULL, service_line TEXT NOT NULL,
            employee_id TEXT NOT NULL, work_date TEXT NOT NULL, hours REAL NOT NULL, labour_cost REAL NOT NULL,
            FOREIGN KEY(client_id) REFERENCES dim_client(client_id)
        );
        CREATE TABLE fact_invoice (
            invoice_id TEXT PRIMARY KEY, client_id TEXT NOT NULL, service_line TEXT NOT NULL,
            invoice_date TEXT NOT NULL, due_date TEXT NOT NULL, amount REAL NOT NULL, paid_amount REAL NOT NULL,
            FOREIGN KEY(client_id) REFERENCES dim_client(client_id)
        );
        CREATE TABLE fact_obligation (
            obligation_id TEXT PRIMARY KEY, client_id TEXT NOT NULL, service_line TEXT NOT NULL,
            due_date TEXT NOT NULL, completion_pct REAL NOT NULL,
            FOREIGN KEY(client_id) REFERENCES dim_client(client_id)
        );
        CREATE TABLE fact_capacity (
            employee_id TEXT PRIMARY KEY, manager TEXT NOT NULL, available_hours REAL NOT NULL
        );
        """
    )
    connection.execute("PRAGMA foreign_keys = ON")
    connection.executemany(
        "INSERT INTO dim_client VALUES (?, ?, ?, ?)",
        [(r.client_id, r.client_name, r.sector, r.manager) for r in data.clients],
    )
    connection.executemany(
        "INSERT INTO fact_time VALUES (?, ?, ?, ?, ?, ?, ?)",
        [
            (r.entry_id, r.client_id, r.service_line, r.employee_id, r.work_date.isoformat(), r.hours, r.hours * r.cost_rate)
            for r in data.time_entries
        ],
    )
    connection.executemany(
        "INSERT INTO fact_invoice VALUES (?, ?, ?, ?, ?, ?, ?)",
        [
            (r.invoice_id, r.client_id, r.service_line, r.invoice_date.isoformat(), r.due_date.isoformat(), r.amount, r.paid_amount)
            for r in data.invoices
        ],
    )
    connection.executemany(
        "INSERT INTO fact_obligation VALUES (?, ?, ?, ?, ?)",
        [(r.obligation_id, r.client_id, r.service_line, r.due_date.isoformat(), r.completion_pct) for r in data.obligations],
    )
    connection.executemany(
        "INSERT INTO fact_capacity VALUES (?, ?, ?)",
        [(r.employee_id, r.manager, r.available_hours) for r in data.capacity],
    )
    connection.commit()
    return connection


def reconciliation(connection: sqlite3.Connection, data: PracticeData) -> dict[str, object]:
    source = {
        "clients": len(data.clients),
        "time_entries": len(data.time_entries),
        "invoices": len(data.invoices),
        "obligations": len(data.obligations),
        "capacity": len(data.capacity),
        "hours": round(sum(r.hours for r in data.time_entries), 2),
        "labour_cost": round(sum(r.hours * r.cost_rate for r in data.time_entries), 2),
        "billed": round(sum(r.amount for r in data.invoices), 2),
        "paid": round(sum(r.paid_amount for r in data.invoices), 2),
    }
    target = {
        "clients": connection.execute("SELECT COUNT(*) FROM dim_client").fetchone()[0],
        "time_entries": connection.execute("SELECT COUNT(*) FROM fact_time").fetchone()[0],
        "invoices": connection.execute("SELECT COUNT(*) FROM fact_invoice").fetchone()[0],
        "obligations": connection.execute("SELECT COUNT(*) FROM fact_obligation").fetchone()[0],
        "capacity": connection.execute("SELECT COUNT(*) FROM fact_capacity").fetchone()[0],
        "hours": round(connection.execute("SELECT COALESCE(SUM(hours), 0) FROM fact_time").fetchone()[0], 2),
        "labour_cost": round(connection.execute("SELECT COALESCE(SUM(labour_cost), 0) FROM fact_time").fetchone()[0], 2),
        "billed": round(connection.execute("SELECT COALESCE(SUM(amount), 0) FROM fact_invoice").fetchone()[0], 2),
        "paid": round(connection.execute("SELECT COALESCE(SUM(paid_amount), 0) FROM fact_invoice").fetchone()[0], 2),
    }
    return {"source": source, "target": target, "status": "PASS" if source == target else "FAIL"}


def decision_marts(connection: sqlite3.Connection, as_of: date) -> dict[str, object]:
    profitability = connection.execute(
        """
        WITH fees AS (
            SELECT client_id, service_line, SUM(amount) billed
            FROM fact_invoice GROUP BY client_id, service_line
        ), cost AS (
            SELECT client_id, service_line, SUM(hours) hours, SUM(labour_cost) labour_cost
            FROM fact_time GROUP BY client_id, service_line
        )
        SELECT c.client_id, c.manager, f.service_line, f.billed, COALESCE(x.hours, 0),
               COALESCE(x.labour_cost, 0), f.billed - COALESCE(x.labour_cost, 0)
        FROM fees f JOIN dim_client c USING(client_id)
        LEFT JOIN cost x USING(client_id, service_line)
        ORDER BY c.client_id
        """
    ).fetchall()
    receivables = connection.execute(
        """
        SELECT client_id, SUM(amount - paid_amount) outstanding,
               SUM(CASE WHEN julianday(?) - julianday(due_date) >= 90 THEN amount - paid_amount ELSE 0 END) ar_90_plus
        FROM fact_invoice GROUP BY client_id ORDER BY client_id
        """,
        (as_of.isoformat(),),
    ).fetchall()
    deadlines = connection.execute(
        """
        SELECT client_id, service_line, due_date, completion_pct,
               CAST(julianday(due_date) - julianday(?) AS INTEGER) days_to_due
        FROM fact_obligation ORDER BY due_date
        """,
        (as_of.isoformat(),),
    ).fetchall()
    capacity = connection.execute(
        """
        SELECT c.manager, SUM(c.available_hours) available, COALESCE(SUM(t.hours), 0) worked
        FROM fact_capacity c
        LEFT JOIN fact_time t ON t.employee_id = c.employee_id
        GROUP BY c.manager ORDER BY c.manager
        """
    ).fetchall()
    return {
        "profitability": [
            {
                "client_id": r[0], "manager": r[1], "service_line": r[2], "fees": r[3],
                "hours": r[4], "labour_cost": r[5], "contribution": r[6],
            }
            for r in profitability
        ],
        "receivables": [
            {"client_id": r[0], "outstanding": r[1], "ar_90_plus": r[2]} for r in receivables
        ],
        "deadlines": [
            {
                "client_id": r[0], "service_line": r[1], "due_date": r[2],
                "completion_pct": r[3], "days_to_due": r[4],
            }
            for r in deadlines
        ],
        "capacity": [
            {
                "manager": r[0], "available_hours": r[1], "worked_hours": r[2],
                "utilisation_pct": r[2] / r[1] if r[1] else 0,
            }
            for r in capacity
        ],
    }


def evidence_pack(as_of: date = date(2026, 10, 2)) -> dict[str, object]:
    data = sample_practice()
    connection = build_warehouse(data)
    recon = reconciliation(connection, data)
    marts = decision_marts(connection, as_of)
    return {
        "contracts": {
            "clients": "one row per client",
            "time": "one row per time entry",
            "invoices": "one row per invoice",
            "obligations": "one row per obligation",
            "capacity": "one row per employee",
        },
        "reconciliation": recon,
        "marts": marts,
        "legacy_signal_check": [asdict(row) for row in analyse(__import__("accounting_intel.core", fromlist=["sample"]).sample(), as_of)],
    }
