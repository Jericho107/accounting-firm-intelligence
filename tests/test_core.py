from datetime import date
import pytest
from accounting_intel.core import Engagement, analyse, sample, validate

def test_risky_client_is_prioritised():
    signals = analyse(sample(), date(2026, 10, 2))
    c2 = next(x for x in signals if x.client_id == "C002")
    assert c2.priority == "high"
    assert c2.contribution < 0
    assert c2.collection_risk == "high"

def test_duplicate_engagement_fails():
    rows = sample()
    with pytest.raises(ValueError, match="duplicate engagement"):
        validate(rows + [rows[0]])

def test_completion_bound_fails():
    bad = Engagement("X","tax","M",100,1,1,0,0,0,date(2026,10,3),1.2)
    with pytest.raises(ValueError, match="completion"):
        validate([bad])
