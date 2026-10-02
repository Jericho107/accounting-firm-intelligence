from dataclasses import replace
from datetime import date

import pytest

from accounting_intel.warehouse import (
    PracticeData,
    build_warehouse,
    decision_marts,
    reconciliation,
    sample_practice,
    validate_practice,
)


def test_source_to_warehouse_reconciles_all_material_totals():
    data = sample_practice()
    connection = build_warehouse(data)
    result = reconciliation(connection, data)
    assert result["status"] == "PASS"
    assert result["source"] == result["target"]


def test_invoice_and_time_grains_do_not_multiply_each_other():
    connection = build_warehouse(sample_practice())
    marts = decision_marts(connection, date(2026, 10, 2))
    c001 = next(row for row in marts["profitability"] if row["client_id"] == "C001")
    assert c001["fees"] == 9000
    assert c001["hours"] == 65
    assert c001["labour_cost"] == 5200


def test_receivables_ageing_is_invoice_grain():
    connection = build_warehouse(sample_practice())
    marts = decision_marts(connection, date(2026, 10, 20))
    c002 = next(row for row in marts["receivables"] if row["client_id"] == "C002")
    assert c002["outstanding"] == 6200
    assert c002["ar_90_plus"] == 6200


def test_capacity_reconciles_employee_hours_without_client_join_duplication():
    connection = build_warehouse(sample_practice())
    marts = decision_marts(connection, date(2026, 10, 2))
    m01 = next(row for row in marts["capacity"] if row["manager"] == "M01")
    assert m01["available_hours"] == 180
    assert m01["worked_hours"] == 140
    assert m01["utilisation_pct"] == pytest.approx(140 / 180)


def test_duplicate_invoice_is_rejected_before_loading():
    data = sample_practice()
    corrupt = PracticeData(
        data.clients,
        data.time_entries,
        data.invoices + (data.invoices[0],),
        data.obligations,
        data.capacity,
    )
    with pytest.raises(ValueError, match="duplicate invoice_id"):
        validate_practice(corrupt)


def test_paid_amount_above_invoice_is_rejected():
    data = sample_practice()
    bad_invoice = replace(data.invoices[0], paid_amount=data.invoices[0].amount + 1)
    corrupt = PracticeData(
        data.clients,
        data.time_entries,
        (bad_invoice,) + data.invoices[1:],
        data.obligations,
        data.capacity,
    )
    with pytest.raises(ValueError, match="invalid invoice"):
        validate_practice(corrupt)


def test_target_mutation_breaks_reconciliation():
    data = sample_practice()
    connection = build_warehouse(data)
    connection.execute("UPDATE fact_invoice SET amount = amount + 100 WHERE invoice_id = 'I001'")
    assert reconciliation(connection, data)["status"] == "FAIL"
