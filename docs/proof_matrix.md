# Validation Matrix

| Claim | Executable evidence | Failure path | Status |
|---|---|---|---|
| Engagement grain is unique | `core.validate` | duplicate client/service engagement | implemented |
| Multi-grain practice data are valid before load | `warehouse.validate_practice` | duplicate invoice, invalid payment, orphan/invalid fact | implemented |
| Warehouse preserves material source totals | `warehouse.reconciliation` | mutate target invoice amount | implemented |
| Invoice and time facts do not multiply each other | independently aggregated marts | cross-grain double-count test | implemented |
| AR ageing remains invoice-grain | receivables mart | 90+ day ageing test | implemented |
| Capacity remains employee-grain | capacity mart | employee/time join-duplication test | implemented |
| Manager portfolio reconciles to engagements | `manager_portfolio` | aggregation test | implemented |
| Management output is generated from governed marts | `reporting.executive_report_html` | report-content test | implemented |
| CI validates clean and corrupted states | GitHub Actions + reverse-test CLI | controlled input and warehouse corruptions | implemented |
| Real accounting-firm ROI or audit assurance | no production evidence | not applicable | not claimed |

## Review principle

A management metric is accepted only when its natural grain, source measure and reconciliation path are visible.
