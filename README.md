<div align="center">

# Accounting Firm Intelligence

### Client profitability, WIP, receivables, deadline risk and capacity intelligence for accounting practices.

**Pretoria BI — Data · Intelligence · Performance**

</div>

---

## Management question

> **Which client engagements consume capacity, destroy contribution, create collection exposure or risk missing statutory deadlines?**

**All data and entities are synthetic. No client result or realised ROI is claimed.**

---

## Implemented capabilities

- Engagement contribution and margin
- Effective billing rate
- WIP-to-fee exposure
- Accounts-receivable ageing
- Filing deadline risk

The implementation is executable end to end and includes controlled failure cases to verify that material data defects are rejected.

## Decision and control flow

```text
SIGNAL → CONTRACT → VALIDATION → ANALYSIS → DECISION RULE → ACTION OWNER → FOLLOW-UP
```

## Run locally

```bash
python -m pip install -e ".[dev]"
ruff check .
pytest -q
python -m accounting_intel.cli smoke
python -m accounting_intel.cli reverse-test
```

## Repository map

```text
accounting-firm-intelligence/
├── .github/workflows/ci.yml
├── config/
├── docs/
├── sql/
├── src/accounting_intel/
├── tests/
├── Dockerfile
├── Makefile
├── pyproject.toml
└── README.md
```

## Scope and limitations

Implemented evidence is separated from future production claims. See `docs/proof_matrix.md` and `docs/limitations.md`. Thresholds in this synthetic case are examples to demonstrate governance and must be calibrated before real deployment.

---

<div align="center">

**Pretoria BI**  
**Understand · Decide · Act · Measure**

</div>
