from __future__ import annotations

from dataclasses import asdict, dataclass
from datetime import date
from typing import Iterable


@dataclass(frozen=True)
class Engagement:
    client_id: str
    service_line: str
    manager: str
    fees_billed: float
    hours_worked: float
    labour_cost: float
    wip_value: float
    ar_balance: float
    oldest_invoice_days: int
    filing_due: date
    completion_pct: float


@dataclass(frozen=True)
class ClientSignal:
    client_id: str
    service_line: str
    contribution: float
    contribution_margin_pct: float
    effective_rate: float
    collection_risk: str
    deadline_risk: str
    wip_to_fees_pct: float
    priority: str


def validate(rows: Iterable[Engagement]) -> None:
    seen: set[tuple[str, str]] = set()
    for r in rows:
        key = (r.client_id, r.service_line)
        if key in seen:
            raise ValueError(f"duplicate engagement grain: {key}")
        seen.add(key)
        if not r.client_id or not r.service_line or not r.manager:
            raise ValueError("business keys and manager are required")
        if min(r.fees_billed, r.hours_worked, r.labour_cost, r.wip_value, r.ar_balance) < 0:
            raise ValueError("negative operational value")
        if r.oldest_invoice_days < 0:
            raise ValueError("invoice age cannot be negative")
        if not 0 <= r.completion_pct <= 1:
            raise ValueError("completion must be in [0, 1]")


def analyse(rows: Iterable[Engagement], as_of: date) -> list[ClientSignal]:
    items = list(rows)
    validate(items)
    out: list[ClientSignal] = []
    for r in items:
        contribution = r.fees_billed - r.labour_cost
        margin = contribution / r.fees_billed if r.fees_billed else 0.0
        rate = r.fees_billed / r.hours_worked if r.hours_worked else 0.0
        wip_ratio = r.wip_value / r.fees_billed if r.fees_billed else 0.0
        collection = "high" if r.oldest_invoice_days >= 90 else "medium" if r.oldest_invoice_days >= 60 else "normal"
        days_to_due = (r.filing_due - as_of).days
        deadline = "high" if days_to_due <= 7 and r.completion_pct < 0.80 else "medium" if days_to_due <= 14 and r.completion_pct < 0.70 else "normal"
        flags = sum((margin < 0.10, collection == "high", deadline == "high", wip_ratio > 0.40))
        priority = "high" if flags >= 2 else "medium" if flags == 1 else "monitor"
        out.append(ClientSignal(r.client_id, r.service_line, contribution, margin, rate,
                                collection, deadline, wip_ratio, priority))
    return out


def portfolio_summary(signals: Iterable[ClientSignal]) -> dict[str, object]:
    rows = list(signals)
    return {
        "engagements": len(rows),
        "high_priority_clients": sorted({r.client_id for r in rows if r.priority == "high"}),
        "negative_contribution_clients": sorted({r.client_id for r in rows if r.contribution < 0}),
        "total_contribution": round(sum(r.contribution for r in rows), 2),
    }


def sample() -> list[Engagement]:
    return [
        Engagement("C001", "accounts", "M01", 9000, 65, 5200, 1800, 3000, 32, date(2026, 10, 20), 0.85),
        Engagement("C002", "tax", "M02", 6500, 82, 7100, 3100, 6200, 104, date(2026, 10, 8), 0.52),
        Engagement("C003", "advisory", "M01", 15000, 75, 6800, 1200, 0, 0, date(2026, 11, 5), 0.90),
    ]


def serialise_sample(as_of: date = date(2026, 10, 2)) -> dict[str, object]:
    signals = analyse(sample(), as_of)
    return {"signals": [asdict(x) for x in signals], "summary": portfolio_summary(signals)}
