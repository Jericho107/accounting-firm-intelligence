from pathlib import Path

from accounting_intel.warehouse import build_warehouse, sample_practice

ROOT = Path(__file__).resolve().parents[1]


def _sql(name: str) -> str:
    return (ROOT / "sql" / name).read_text(encoding="utf-8")


def test_profitability_sql_executes_against_warehouse():
    connection = build_warehouse(sample_practice())
    rows = connection.execute(_sql("10_client_profitability.sql")).fetchall()
    assert len(rows) == 3
    assert rows[0][0] == "C002"


def test_ar_aging_sql_surfaces_90_plus_exposure():
    connection = build_warehouse(sample_practice())
    rows = connection.execute(
        _sql("20_ar_aging.sql"),
        {"as_of_date": "2026-10-20"},
    ).fetchall()
    c002 = next(row for row in rows if row[0] == "C002")
    assert c002[4] == 6200


def test_capacity_sql_preserves_employee_grain():
    connection = build_warehouse(sample_practice())
    rows = connection.execute(_sql("30_capacity_utilisation.sql")).fetchall()
    m01 = next(row for row in rows if row[0] == "M01")
    assert m01[1] == 180
    assert m01[2] == 140


def test_deadline_risk_sql_executes():
    connection = build_warehouse(sample_practice())
    rows = connection.execute(
        _sql("40_deadline_risk.sql"),
        {"as_of_date": "2026-10-02"},
    ).fetchall()
    assert rows
    assert rows[0][-1] in {"high", "medium", "low"}
