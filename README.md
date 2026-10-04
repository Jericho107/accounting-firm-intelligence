<div align="center">

# Accounting Firm Intelligence

### Profitability · WIP · Receivables · Filing Risk · Capacity

**Python · SQLite · Analytical Modelling · Data Quality · CI**

**Pretoria BI — Data · Intelligence · Performance**

</div>

---

## Management question

> **Which client engagements consume capacity, weaken contribution, create collection exposure or risk missing a filing deadline — and who should act first?**

This repository implements a synthetic accounting-practice decision system. It separates the operational grains that are commonly mixed in reporting — clients, time entries, invoices, obligations and employee capacity — then reconciles them into decision marts without double counting.

**All entities and values are synthetic. No client result or realised ROI is claimed.**

## Decision surface

The project produces an executable HTML management report covering:

- client/service-line profitability;
- outstanding and 90+ day receivables;
- upcoming filing obligations and completion;
- manager capacity and utilisation;
- priority clients requiring intervention.

Generate it with:

```bash
python -m accounting_intel.cli report
```

Output: `output/accounting_executive_report.html`.

## Architecture

```text
CLIENTS ────────────────┐
TIME ENTRIES ──────────┤
INVOICES ──────────────┤
OBLIGATIONS ───────────┼→ CONTRACTS → SQLITE WAREHOUSE → RECONCILIATION
EMPLOYEE CAPACITY ─────┘                         ↓
                                         DECISION MARTS
                                  ┌─────────┼──────────┐
                           PROFITABILITY    AR      CAPACITY
                                  └─────────┼──────────┘
                                      ACTION PRIORITY
```

### Natural grains

| Domain | Grain | Key |
|---|---|---|
| Client | one row per client | `client_id` |
| Time | one row per time entry | `entry_id` |
| Invoice | one row per invoice | `invoice_id` |
| Obligation | one row per filing/obligation | `obligation_id` |
| Capacity | one row per employee | `employee_id` |

Facts are aggregated independently before combination. This prevents invoice × time-entry joins from fabricating fees, hours, labour cost or capacity.

## Controls and validation

The implementation checks:

- unique business keys at every source grain;
- client referential integrity;
- valid completion percentages;
- valid invoice/payment relationships;
- source-to-warehouse row counts;
- total hours and labour cost;
- billed and paid amounts;
- invoice-grain AR ageing;
- employee-grain capacity;
- warehouse financial mutation.

The CI deliberately corrupts controlled states through the reverse-test CLI and must reject them.

## Run locally

```bash
python -m pip install -e ".[dev]"
ruff check .
pytest -q
python -m accounting_intel.cli smoke
python -m accounting_intel.cli report
python -m accounting_intel.cli reverse-test
```

## What a reviewer can verify

A technical reviewer can inspect the grain contracts, warehouse SQL, reconciliation and tests. A manager can open the generated report and see the same model expressed as business decisions.

See:

- `docs/data_contracts.md`
- `docs/controls_matrix.md`
- `docs/proof_matrix.md`
- `docs/limitations.md`

## Scope

This is a synthetic analytical implementation, not an accounting/audit product and not a regulatory opinion. Thresholds require calibration against the operating model of a real practice.

---

<div align="center">

**Pretoria BI**  
**Understand · Decide · Act · Measure**

</div>
