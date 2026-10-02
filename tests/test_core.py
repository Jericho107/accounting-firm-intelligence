from datetime import date

import pytest

from accounting_intel.core import Engagement, analyse, sample, validate


def test_risky_client_is_prioritised() -> None:
    signals = analyse(sample(), date(2026, 10, 2))
    client = next(item for item in signals if item.client_id == "C002")
    assert client.priority == "high"
    assert client.contribution < 0
    assert client.collection_risk == "high"


def test_duplicate_engagement_fails() -> None:
    rows = sample()
    with pytest.raises(ValueError, match="duplicate engagement"):
        validate(rows + [rows[0]])


def test_completion_bound_fails() -> None:
    bad = Engagement(
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
    with pytest.raises(ValueError, match="completion"):
        validate([bad])
