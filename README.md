# Investment Operations Reporting Toolkit

An automated data reconciliation and exception-handling engine built in Python and SQL. This toolkit simulates core fund administration and back-office operations workflows by auditing internal ledger balances (**Investment Book of Record / IBOR**) against external banking and custodian statements (**Custody Book of Record / CBOR**) using synthetic, structured multi-asset datasets.

## Project Scope & Operational Impact

In institutional asset management, multi-ledger data discrepancies are a structural inevitability — driven by timing differences, mismatched trade bookings, and settlement drops. Left unchecked, unresolved breaks propagate into net asset value (NAV) updates and daily pricing runs, exposing funds to mispriced investor entry/exit points and regulatory reporting failures.

This repository models the automated control layer that intercepts and classifies ledger deviations before they compromise downstream accounting systems.

## Core Technical Features

- **Risk-focused data ingestion** — outer-join mapping ensures positions omitted from either ledger are preserved and flagged, never silently dropped.
- **Operational exception matrix** — vectorized conditional logic auto-classifies breaks into structural risk categories (cash breaks, quantity shortfalls, valuation discrepancies).
- **Dual-stream reconciliation** — separates outputs into cash reconciliation and securities holdings reconciliation, mirroring how live institutional teams split these workflows (different root causes, different resolution paths).
- **Corporate actions handling** — models real edge cases including dividend reinvestment plan (DRP) timing lags, FX valuation mismatches, and unlisted/illiquid asset valuation lag (using an unlisted infrastructure asset as a test case).
- **Audit-ready output** — formats results into structured, executive-style Excel exception reports with conditional formatting and KPI summary blocks.
- **SQL risk reporting** — syncs reconciliation results to a SQLite warehouse and runs aggregation queries for concentration risk and capital-at-risk reporting.

## System Architecture

- **`data/`** — synthetic portfolio and warehouse data
- **`output/`** — generated exception reports and dashboards
- **`scripts/`** — SQL warehouse queries and reporting scripts
- **`reconciliation_engine.py`** — core pandas/openpyxl reconciliation logic
- **`run_toolkit.sh`** — orchestrates the full pipeline end-to-end

## Execution Guide

**Prerequisites:** Python 3.x with `pandas`, `openpyxl`, and `numpy` installed.

Run the full pipeline from the project root:

```bash
./run_toolkit.sh
```

This will:
1. Run the pandas/openpyxl reconciliation engine and produce a formatted Excel exception report
2. Sync results to the SQLite warehouse
3. Run SQL aggregation queries and produce a management risk summary

Output files land in `/output`.

## Sample Output

![Daily Operations MIS Dashboard](https://github.com/cohen-pikari/investment-reporting-toolkit/raw/main/output/daily_ops_mis_dashboard.png)

---
*Maintained by Cohen Pikari ([github.com/cohen-pikari](https://github.com/cohen-pikari))*
