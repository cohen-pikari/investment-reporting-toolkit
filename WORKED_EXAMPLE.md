# Worked Example: Tracing a Single Exception

This walks through one real exception from this repo's synthetic dataset, end to end, showing exactly how the engine reasons about it.

## The Case: AAPL, FX Valuation Break

**Raw data:** `data/internal_ledger.csv` shows Apple Inc. (US_EQ_AAPL) at a market value of $3,155,407.47. The custodian statement (`data/custodian_statement.csv`) shows $3,137,888.44, a variance of -$17,519.03.

**Why this isn't a real error:** AAPL is a USD-denominated holding. The variance represents roughly 0.55% of market value, within the engine's defined FX tolerance band (0.8%), consistent with a timing difference in spot-rate conversion between the internal book and custodian feed, not a genuine pricing error.

**How the engine classifies it:** see `reconciliation_engine.py`, the `is_fx_candidate` logic. It checks currency ≠ AUD, an existing PRICING_BREAK flag, and whether the variance sits inside the tolerance band, before reclassifying it as `FX_VALUATION_BREAK` rather than escalating it as a hard break.

**Try it yourself:** open `data/custodian_statement.csv`, change AAPL's market value to something outside the 0.8% band (e.g. a 5% difference), re-run `python3 reconciliation_engine.py`, and see it reclassify as a genuine `PRICING_BREAK` instead.

---
*Maintained by Cohen Pikari ([github.com/cohen-pikari](https://github.com/cohen-pikari))*
