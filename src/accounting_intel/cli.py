from __future__ import annotations

import json
import sys
from datetime import date

from .core import Engagement, serialise_sample, sample, validate


def smoke() -> int:
    print(json.dumps(serialise_sample(), indent=2, sort_keys=True))
    return 0


def reverse_test() -> int:
    cases: list[dict[str, str]] = []

    try:
        rows = sample()
        validate(rows + [rows[0]])
    except ValueError as exc:
        cases.append(
            {"case": "duplicate-grain", "status": "PASS", "error": str(exc)}
        )
    else:
        cases.append(
            {"case": "duplicate-grain", "status": "FAIL", "error": "corruption accepted"}
        )

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
        cases.append(
            {"case": "invalid-completion", "status": "PASS", "error": str(exc)}
        )
    else:
        cases.append(
            {
                "case": "invalid-completion",
                "status": "FAIL",
                "error": "corruption accepted",
            }
        )

    print(json.dumps(cases, indent=2, sort_keys=True))
    return 0 if all(case["status"] == "PASS" for case in cases) else 1


def main() -> int:
    command = sys.argv[1] if len(sys.argv) > 1 else "smoke"
    if command == "smoke":
        return smoke()
    if command == "reverse-test":
        return reverse_test()
    print(
        "usage: python -m accounting_intel.cli [smoke|reverse-test]",
        file=sys.stderr,
    )
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
