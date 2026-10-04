from __future__ import annotations

from html import escape
from pathlib import Path

from .warehouse import evidence_pack


def _table(headers: list[str], rows: list[list[object]]) -> str:
    head = "".join(f"<th>{escape(str(value))}</th>" for value in headers)
    body = "".join(
        "<tr>" + "".join(f"<td>{escape(str(value))}</td>" for value in row) + "</tr>"
        for row in rows
    )
    return f"<table><thead><tr>{head}</tr></thead><tbody>{body}</tbody></table>"


def executive_report_html() -> str:
    evidence = evidence_pack()
    marts = evidence["marts"]
    profitability = marts["profitability"]
    receivables = marts["receivables"]
    deadlines = marts["deadlines"]
    capacity = marts["capacity"]

    urgent_clients = sorted(
        {
            row["client_id"]
            for row in profitability
            if row["contribution"] < 0
        }
        | {
            row["client_id"]
            for row in receivables
            if row["ar_90_plus"] > 0
        }
        | {
            row["client_id"]
            for row in deadlines
            if row["days_to_due"] <= 7 and row["completion_pct"] < 0.8
        }
    )

    return f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<title>Accounting Firm Intelligence</title>
<style>
body {{ font-family: Arial, sans-serif; max-width: 1180px; margin: 40px auto; line-height: 1.45; }}
h1, h2 {{ margin-bottom: .35rem; }}
.metric {{ display: inline-block; margin: .3rem 1rem .8rem 0; padding: .6rem .8rem; border: 1px solid #bbb; }}
table {{ border-collapse: collapse; width: 100%; margin: 1rem 0 2rem; }}
th, td {{ border: 1px solid #ddd; padding: .55rem; text-align: right; }}
th:first-child, td:first-child {{ text-align: left; }}
small {{ color: #555; }}
</style>
</head>
<body>
<h1>Accounting Firm Intelligence</h1>
<p>Decision surface for profitability, receivables, filing risk and manager capacity.</p>
<div class="metric"><strong>Priority clients</strong><br>{escape(", ".join(urgent_clients) or "None")}</div>
<div class="metric"><strong>Warehouse reconciliation</strong><br>{escape(evidence["reconciliation"]["status"])}</div>

<h2>Client profitability</h2>
{_table(
    ["Client", "Manager", "Service", "Fees", "Hours", "Labour cost", "Contribution"],
    [[r["client_id"], r["manager"], r["service_line"], r["fees"], r["hours"], r["labour_cost"], r["contribution"]] for r in profitability],
)}

<h2>Receivables</h2>
{_table(
    ["Client", "Outstanding", "90+ days"],
    [[r["client_id"], r["outstanding"], r["ar_90_plus"]] for r in receivables],
)}

<h2>Upcoming obligations</h2>
{_table(
    ["Client", "Service", "Due date", "Completion", "Days to due"],
    [[r["client_id"], r["service_line"], r["due_date"], r["completion_pct"], r["days_to_due"]] for r in deadlines],
)}

<h2>Manager capacity</h2>
{_table(
    ["Manager", "Available hours", "Worked hours", "Utilisation"],
    [[r["manager"], r["available_hours"], r["worked_hours"], f'{r["utilisation_pct"]:.1%}'] for r in capacity],
)}

<small>Synthetic demonstration data. Thresholds require calibration before operational use.</small>
</body>
</html>"""


def write_executive_report(path: str | Path) -> Path:
    output = Path(path)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(executive_report_html(), encoding="utf-8")
    return output
