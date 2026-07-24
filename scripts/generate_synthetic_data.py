"""
Synthetic Multi-Asset Portfolio Data Generator
------------------------------------------------
Generates two independent, synthetic datasets representing:
  - internal_ledger.csv   (Investment Book of Record / IBOR)
  - custodian_statement.csv (Custody Book of Record / CBOR)

Both datasets start from an identical "clean" base portfolio across four
asset classes (AU Equities, US Equities, Fixed Income, Unlisted/Private),
plus cash. A controlled set of deliberate discrepancies is then injected
into the CBOR copy to simulate realistic institutional reconciliation
exceptions: quantity breaks, cash breaks, pricing breaks, FX mismatches,
corporate action (DRP) timing lags, and unlisted asset valuation lags.

All data is entirely fictional / illustrative. No real institutional,
client, or employer data is used or represented.
"""

import pandas as pd
import numpy as np
import os

np.random.seed(42)

STATEMENT_DATE = "2026-07-22"

# ---------------------------------------------------------------------------
# 1. BASE PORTFOLIO CONSTRUCTION
# ---------------------------------------------------------------------------

au_equities = [
    ("AU_EQ_BHP", "BHP", "BHP Group Ltd", "AUD"),
    ("AU_EQ_CBA", "CBA", "Commonwealth Bank of Australia", "AUD"),
    ("AU_EQ_CSL", "CSL", "CSL Limited", "AUD"),
    ("AU_EQ_NAB", "NAB", "National Australia Bank", "AUD"),
    ("AU_EQ_WES", "WES", "Wesfarmers Ltd", "AUD"),
    ("AU_EQ_WOW", "WOW", "Woolworths Group", "AUD"),
    ("AU_EQ_TLS", "TLS", "Telstra Group", "AUD"),
    ("AU_EQ_RIO", "RIO", "Rio Tinto Ltd", "AUD"),
    ("AU_EQ_MQG", "MQG", "Macquarie Group", "AUD"),
    ("AU_EQ_XRO", "XRO", "Xero Limited", "AUD"),
    ("AU_EQ_A200", "A200", "Betashares Australia 200 ETF", "AUD"),
    ("AU_EQ_VAS", "VAS", "Vanguard Australian Shares ETF", "AUD"),
]

us_equities = [
    ("US_EQ_AAPL", "AAPL", "Apple Inc.", "USD"),
    ("US_EQ_MSFT", "MSFT", "Microsoft Corp.", "USD"),
    ("US_EQ_NVDA", "NVDA", "NVIDIA Corp.", "USD"),
    ("US_EQ_AMZN", "AMZN", "Amazon.com Inc.", "USD"),
    ("US_EQ_GOOGL", "GOOGL", "Alphabet Inc.", "USD"),
    ("US_EQ_META", "META", "Meta Platforms Inc.", "USD"),
    ("US_EQ_JPM", "JPM", "JPMorgan Chase & Co.", "USD"),
    ("US_EQ_VTS", "VTS", "Vanguard US Total Market ETF", "USD"),
    ("US_EQ_VGS", "VGS", "Vanguard International Shares ETF", "USD"),
    ("US_EQ_SPCX", "SPCX", "Space Exploration Technologies Corp.", "USD"),
]

fixed_income = [
    ("FI_AGB_2031", "AGB31", "Australian Govt Bond 2031", "AUD"),
    ("FI_AGB_2028", "AGB28", "Australian Govt Bond 2028", "AUD"),
    ("FI_UST_2030", "UST30", "US Treasury Note 2030", "USD"),
    ("FI_CORP_TLS", "CTLS28", "Telstra Corporate Bond 2028", "AUD"),
    ("FI_CORP_CBA", "CCBA29", "CBA Tier 2 Subordinated Note 2029", "AUD"),
    ("FI_SEMI_QLD", "QTC30", "Queensland Treasury Corp Bond 2030", "AUD"),
]

unlisted = [
    ("ALT_INF_MEL", "MEL_AIRPORT", "Melbourne Airport Infrastructure Fund", "AUD"),
    ("ALT_PE_COLLINS", "COLLINS_PE", "Collins St Private Equity Fund III", "AUD"),
    ("ALT_INF_WIND", "WINDFARM_02", "Southern Ranges Windfarm Trust", "AUD"),
    ("ALT_PROP_LOG", "LOGISTICS_HUB", "National Logistics Property Trust", "AUD"),
]

cash = [
    ("CASH_AUD", "CASH_AUD", "Cash - Australian Dollar", "AUD"),
    ("CASH_USD", "CASH_USD", "Cash - US Dollar", "USD"),
]

all_positions = au_equities + us_equities + fixed_income + unlisted + cash

records = []
for sec_id, ticker, name, ccy in all_positions:
    if sec_id.startswith("CASH"):
        qty = np.random.randint(200_000, 900_000)
        price = 1.00
    elif sec_id.startswith("ALT_"):
        qty = np.random.randint(1, 5)
        price = np.random.randint(400_000, 1_500_000)
    elif sec_id.startswith("FI_"):
        qty = np.random.randint(500_000, 3_000_000)
        price = round(np.random.uniform(95.0, 104.0), 2)
    else:
        qty = np.random.randint(500, 15_000)
        price = round(np.random.uniform(15.0, 550.0), 2)

    market_value = round(qty * price, 2)
    records.append({
        "security_id": sec_id,
        "ticker": ticker,
        "security_name": name,
        "asset_class": (
            "Cash" if sec_id.startswith("CASH") else
            "Unlisted/Alternatives" if sec_id.startswith("ALT_") else
            "Fixed Income" if sec_id.startswith("FI_") else
            "AU Equities" if sec_id.startswith("AU_") else
            "US Equities"
        ),
        "currency": ccy,
        "quantity": qty,
        "unit_price": price,
        "market_value": market_value,
    })

base_df = pd.DataFrame(records)

# ---------------------------------------------------------------------------
# 2. BUILD IBOR (internal ledger) — the clean baseline
# ---------------------------------------------------------------------------

internal_df = base_df.copy()
internal_df.insert(0, "trade_date", STATEMENT_DATE)

# ---------------------------------------------------------------------------
# 3. BUILD CBOR (custodian statement) — clean baseline, then inject breaks
# ---------------------------------------------------------------------------

custodian_df = base_df.copy()
custodian_df.insert(0, "statement_date", STATEMENT_DATE)

n = len(custodian_df)
idx = custodian_df.set_index("security_id")

# --- Exception 1: Quantity break (pending settlement) — 2 AU equities ---
qty_break_ids = ["AU_EQ_WES", "AU_EQ_TLS"]
for sid in qty_break_ids:
    idx.loc[sid, "quantity"] = idx.loc[sid, "quantity"] - np.random.randint(200, 800)
    idx.loc[sid, "market_value"] = round(idx.loc[sid, "quantity"] * idx.loc[sid, "unit_price"], 2)

# --- Exception 2: Pricing/valuation break — 2 US equities (custodian stale price feed) ---
pricing_break_ids = ["US_EQ_META", "US_EQ_JPM"]
for sid in pricing_break_ids:
    stale_price = round(idx.loc[sid, "unit_price"] * np.random.uniform(0.96, 0.99), 2)
    idx.loc[sid, "unit_price"] = stale_price
    idx.loc[sid, "market_value"] = round(idx.loc[sid, "quantity"] * stale_price, 2)

# --- Exception 3: Cash balance break — AUD cash account (unexplained shortfall) ---
idx.loc["CASH_AUD", "quantity"] = idx.loc["CASH_AUD", "quantity"] - 48_500
idx.loc["CASH_AUD", "market_value"] = idx.loc["CASH_AUD", "quantity"]

# --- Exception 4: FX valuation mismatch — 2 USD-denominated holdings ---
fx_mismatch_ids = ["US_EQ_AAPL", "US_EQ_NVDA"]
for sid in fx_mismatch_ids:
    fx_drift = np.random.uniform(-0.006, 0.006)
    idx.loc[sid, "market_value"] = round(idx.loc[sid, "market_value"] * (1 + fx_drift), 2)

# --- Exception 5: Corporate action / DRP timing lag — 1 AU equity ---
idx.loc["AU_EQ_CBA", "quantity"] = idx.loc["AU_EQ_CBA", "quantity"] - 45
idx.loc["AU_EQ_CBA", "market_value"] = round(idx.loc["AU_EQ_CBA", "quantity"] * idx.loc["AU_EQ_CBA", "unit_price"], 2)

# --- Exception 6: Unlisted / illiquid asset valuation lag — 2 alternatives ---
unlisted_lag_ids = ["ALT_INF_MEL", "ALT_PE_COLLINS"]
for sid in unlisted_lag_ids:
    stale_factor = np.random.uniform(0.90, 0.95)
    idx.loc[sid, "market_value"] = round(idx.loc[sid, "market_value"] * stale_factor, 2)

# --- Exception 7: Bond coupon timing lag — 1 fixed income holding ---
idx.loc["FI_CORP_TLS", "market_value"] = round(idx.loc["FI_CORP_TLS", "market_value"] * 0.998, 2)

custodian_df = idx.reset_index()
custodian_df = custodian_df[["statement_date", "security_id", "ticker", "security_name",
                              "asset_class", "currency", "quantity", "unit_price", "market_value"]]

internal_df = internal_df[["trade_date", "security_id", "ticker", "security_name",
                            "asset_class", "currency", "quantity", "unit_price", "market_value"]]

# ---------------------------------------------------------------------------
# 4. WRITE OUTPUT
# ---------------------------------------------------------------------------

os.makedirs("data", exist_ok=True)
internal_df.to_csv("data/internal_ledger.csv", index=False)
custodian_df.to_csv("data/custodian_statement.csv", index=False)

print(f"Generated synthetic portfolio: {len(internal_df)} positions across "
      f"{internal_df['asset_class'].nunique()} asset classes.")
print("Injected exception categories: Quantity Break, Pricing Break, Cash Break, "
      "FX Mismatch, DRP Timing Lag, Unlisted Valuation Lag, Coupon Timing Lag.")
print("Files written: data/internal_ledger.csv, data/custodian_statement.csv")
