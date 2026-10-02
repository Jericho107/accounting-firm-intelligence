from __future__ import annotations

from collections.abc import Iterable
from dataclasses import asdict, dataclass
from datetime import date


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
    for row in rows:
        key = (row.client_id, row.service_line)
        if key in seen:
            raise ValueError(f"duplicate engagement grain: {key}")
        seen.add(key)
        if not row.client_id or not row.service_line or not row.manager:
            raise ValueError("business keys and manager are required")
        if min(
            row.fees_billed,
            row.hours_worked,
            row.labour_cost,
            row.wip_value,
            row.ar_balance,
        ) < 0:
            raise ValueError("negative operational value")
        if row.oldest_invoice_days < 0:
            raise ValueError("invoice age cannot be negative")
        if not 0 <= row.completion_pct <= 1:
            raise ValueError("completion must be in [0, 1]")


def analyse(rows: Iterable[Engagement], as_of: date) -> list[ClientSignal]:
    items = list(rows)
    validate(items)
    output: list[ClientSignal] = []
    for row in items:
        contribution = row.fees_billed - row.labour_cost
        margin = contribution / row.fees_billed if row.fees_billed else 0.0
        rate = row.fees_billed / row.hours_worked if row.hours_worked else 0.0
        wip_ratio = row.wip_value / row.fees_billed if row.fees_billed else 0.0
        collection = (
            "high"
            if row.oldest_invoice_days >= 90
            else "medium"
            if row.oldest_invoice_days >= 60
            else "normal"
        )
        days_to_due = (row.filing_due - as_of).days
        deadline = (
            "high"
            if days_to_due <= 7 and row.completion_pct < 0.80
            else "medium"
            if days_to_due <= 14 and row.completion_pct < 0.70
            else "normal"
        )
        flags = sum(
            (
                margin < 0.10,
                collection == "high",
                deadline == "high",
                wip_ratio > 0.40,
            )
        )
        priority = "high" if flags >= 2 else "medium" if flags == 1 else "monitor"
        output.append(
            ClientSignal(
                row.client_id,
                row.service_line,
                contribution,
                margin,
                rate,
                collection,
                deadline,
                wip_ratio,
                priority,
            )
        )
    return output


def manager_portfolio(
    engagements: Iterable[Engagement],
    as_of: date,
) -> list[dict[str, object]]:
    rows = list(engagements)
    signals = analyse(rows, as_of)
    by_key = {(row.client_id, row.service_line): row for row in signals}
    managers = sorted({row.manager for row in rows})
    output: list[dict[str, object]] = []
    for manager in managers:
        owned = [row for row in rows if row.manager == manager]
        owned_signals = [by_key[(row.client_id, row.service_line)] for row in owned]
        output.append(
            {
                "manager": manager,
                "hours": sum(row.hours_worked for row in owned),
                "wip": round(sum(row.wip_value for row in owned), 2),
                "ar": round(sum(row.ar_balance for row in owned), 2),
                "high_priority_engagements": sum(
                    signal.priority == "high" for signal in owned_signals
                ),
                "contribution": round(
                    sum(signal.contribution for signal in owned_signals), 2
                ),
            }
        )
    return output


def portfolio_summary(signals: Iterable[ClientSignal]) -> dict[str, object]:
    rows = list(signals)
    return {
        "engagements": len(rows),
        "high_priority_clients": sorted(
            {row.client_id for row in rows if row.priority == "high"}
        ),
        "negative_contribution_clients": sorted(
            {row.client_id for row in rows if row.contribution < 0}
        ),
        "total_contribution": round(sum(row.contribution for row in rows), 2),
    }


def sample() -> list[Engagement]:
    return [
        Engagement(
            "C001", "accounts", "M01", 9000, 65, 5200, 1800, 3000, 32,
            date(2026, 10, 20), 0.85,
        ),
        Engagement(
            "C002", "tax", "M02", 6500, 82, 7100, 3100, 6200, 104,
            date(2026, 10, 8), 0.52,
        ),
        Engagement(
            "C003", "advisory", "M01", 15000, 75, 6800, 1200, 0, 0,
            date(2026, 11, 5), 0.90,
        ),
    ]


def serialise_sample(as_of: date = date(2026, 10, 2)) -> dict[str, object]:
    signals = analyse(sample(), as_of)
    return {
        "signals": [asdict(item) for item in signals],
        "manager_portfolio": manager_portfolio(sample(), as_of),
        "summary": portfolio_summary(signals),
    }
