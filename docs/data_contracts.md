# Data contracts and grains

This case separates operational domains before aggregation. That separation is deliberate: joining invoice and time-entry facts directly can multiply rows and fabricate fees, hours or labour cost.

| Domain | Natural grain | Primary key | Material measures |
|---|---|---|---|
| Client | one row per client | client_id | none |
| Time | one row per time entry | entry_id | hours, labour cost |
| Invoice | one row per invoice | invoice_id | billed, paid, outstanding |
| Obligation | one row per filing/obligation | obligation_id | completion |
| Capacity | one row per employee | employee_id | available hours |

Decision marts aggregate each fact independently before combining measures. Tests explicitly prove that invoice and time grains do not multiply each other.
