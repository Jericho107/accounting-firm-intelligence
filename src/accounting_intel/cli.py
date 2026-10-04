from __future__ import annotations

import json
import sys
from dataclasses import replace
from datetime import date

from .core import Engagement, sample, serialise_sample, validate
from .reporting import write_executive_report
from .warehouse import PracticeData, build_warehouse, evidence_pack, reconciliation, sample_practice


def smoke() -> int:
    payload = serialise_sample()
    payload["warehouse"] = evidence_pack()
    print(json.dumps(payload, indent=2, sort_keys=True))
    return 0


def report() -> int:
    path = write_executive_report("output/accounting_executive_report.html")
    print(path.as_posix())
    return 0


def reverse_test() -> int:
    cases: list[dict[str, str]] = []

    try:
        rows = sample()
        validate(rows + [rows[0]])
    except ValueError as exc:
        cases.append({"case": "duplicate-engagement-grain", "status": "PASS", "error": str(exc)})
    else:
        cases.append({"case": "duplicate-engagement-grain", "status": "FAIL", "error": "corruption accepted"})

    try:
        validate(
            [
                Engagement(
                    "X",
                    "tax",
                    "M",
                    100,
                    1,
                    1,
                    0,
                    0,
                    0,
                    date(2026, 10, 3),
                    1.2,
                )
            ]
        )
    except ValueError as exc:
        cases.append({"case": "invalid-completion", "status": "PASS", "error": str(exc)})
    else:
        cases.append({"case": "invalid-completion", "status": "FAIL", "error": "corruption accepted"})

    data = sample_practice()
    bad_invoice = replace(data.invoices[0], paid_amount=data.invoices[0].amount + 1)
    corrupt = PracticeData(
        data.clients,
        data.time_entries,
        (bad_invoice,) + data.invoices[1:],
        data.obligations,
        data.capacity,
    )
    try:
        build_warehouse(corrupt)
    except ValueError as exc:
        cases.append({"case": "invalid-invoice-contract", "status": "PASS", "error": str(exc)})
    else:
        cases.append({"case": "invalid-invoice-contract", "status": "FAIL", "error": "corruption accepted"})

    connection = build_warehouse(data)
    connection.execute("UPDATE fact_invoice SET amount = amount + 100 WHERE invoice_id = 'I001'")
    warehouse_status = reconciliation(connection, data)["status"]
    cases.append(
        {
            "case": "warehouse-financial-drift",
            "status": "PASS" if warehouse_status == "FAIL" else "FAIL",
            "error": "drift detected" if warehouse_status == "FAIL" else "drift accepted",
        }
    )

    print(json.dumps(cases, indent=2, sort_keys=True))
    return 0 if all(case["status"] == "PASS" for case in cases) else 1


def main() -> int:
    command = sys.argv[1] if len(sys.argv) > 1 else "smoke"
    if command == "smoke":
        return smoke()
    if command == "report":
        return report()
    if command == "reverse-test":
        return reverse_test()
    print(
        "usage: python -m accounting_intel.cli [smoke|report|reverse-test]",
        file=sys.stderr,
    )
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
