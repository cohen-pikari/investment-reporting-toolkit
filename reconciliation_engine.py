"""
Investment Operations Reconciliation Engine
--------------------------------------------
Core reconciliation logic for the toolkit. Ingests the fund's Investment
Book of Record (IBOR) and the custodian's independent Custody Book of
Record (CBOR), performs a full outer-join match on security identifier,
and classifies every discrepancy into a structured exception taxonomy.

Design principles:
  - Outer join preserves positions missing from either side (never
    silently dropped).
  - Vectorised classification (np.select) — no row-by-row Python loops —
    so the same logic scales cleanly from a handful of positions to a
    full institutional multi-asset portfolio.
  - Exception types are assigned based on *which fields* disagree
    (quantity / cash / valuation) and cross-referenced against known
    asset-class behaviour (e.g. unlisted assets reprice periodically,
    not daily), mirroring how a real reconciliation control distinguishes
    an expected timing lag from a genuine break.

All data processed here is synthetic and illustrative.
"""

import os
import pandas as pd
import numpy as np


def load_ledgers(internal_path="data/internal_ledger.csv", custodian_path="data/custodian_statement.csv"):
    df_internal = pd.read_csv(internal_path)
    df_custodian = pd.read_csv(custodian_path)
    return df_internal, df_custodian


def reconcile(df_internal: pd.DataFrame, df_custodian: pd.DataFrame) -> pd.DataFrame:
    """Full outer-join reconciliation with vectorised exception classification."""

    merged = pd.merge(
        df_internal, df_custodian,
        on="security_id", how="outer",
        suffixes=("_internal", "_custodian"),
    )

    # Backfill descriptive fields from whichever side has them
    for col in ["ticker", "security_name", "asset_class", "currency"]:
        merged[col] = merged[f"{col}_internal"].fillna(merged[f"{col}_custodian"])
        merged.drop(columns=[f"{col}_internal", f"{col}_custodian"], inplace=True)

    numeric_cols = ["quantity_internal", "quantity_custodian",
                    "market_value_internal", "market_value_custodian"]
    for c in numeric_cols:
        merged[c] = merged[c].fillna(0)

    merged["qty_variance"] = merged["quantity_internal"] - merged["quantity_custodian"]
    merged["mv_variance"] = merged["market_value_internal"] - merged["market_value_custodian"]

    is_cash = merged["security_id"].str.startswith("CASH")
    is_unlisted = merged["asset_class"] == "Unlisted/Alternatives"
    is_fixed_income = merged["asset_class"] == "Fixed Income"
    missing_from_custodian = (merged["quantity_custodian"] == 0) & (merged["quantity_internal"] != 0)
    missing_from_internal = (merged["quantity_internal"] == 0) & (merged["quantity_custodian"] != 0)
    qty_break = (merged["qty_variance"] != 0) & ~missing_from_custodian & ~missing_from_internal
    mv_only_break = (merged["qty_variance"] == 0) & (merged["mv_variance"].abs() > 0.01)

    conditions = [
        is_cash & (merged["qty_variance"] != 0),
        missing_from_custodian,
        missing_from_internal,
        is_unlisted & mv_only_break,
        is_fixed_income & mv_only_break,
        qty_break & (merged["market_value_internal"].round(2) != merged["market_value_custodian"].round(2)) & (merged["qty_variance"].abs() < merged["quantity_internal"] * 0.05),
        qty_break,
        mv_only_break,
    ]
    choices = [
        "CASH_BALANCE_BREAK",
        "UNRECORDED_AT_CUSTODIAN",
        "UNBOOKED_INTERNAL_TRADE",
        "UNLISTED_VALUATION_LAG",
        "COUPON_TIMING_LAG",
        "CA_DRP_TIMING_LAG",
        "QUANTITY_BREAK",
        "PRICING_BREAK",
    ]
    merged["exception_type"] = np.select(conditions, choices, default="MATCHED")

    # FX mismatch overlay: small MV-only variance on a non-AUD holding within a tight
    # tolerance band is reclassified as an FX timing difference rather than a hard break.
    fx_band = merged["mv_variance"].abs() / merged["market_value_internal"].replace(0, np.nan)
    is_fx_candidate = (merged["currency"] != "AUD") & (merged["exception_type"] == "PRICING_BREAK") & (fx_band < 0.008)
    merged.loc[is_fx_candidate, "exception_type"] = "FX_VALUATION_BREAK"

    return merged


def classify_summary(recon_df: pd.DataFrame) -> pd.DataFrame:
    exceptions = recon_df[recon_df["exception_type"] != "MATCHED"].copy()
    return exceptions


def run():
    df_internal, df_custodian = load_ledgers()
    recon_df = reconcile(df_internal, df_custodian)
    exceptions = classify_summary(recon_df)

    os.makedirs("output", exist_ok=True)
    recon_df.to_csv("output/full_reconciliation_matrix.csv", index=False)
    exceptions.to_csv("output/exceptions_only.csv", index=False)

    print(f"Reconciliation complete: {len(recon_df)} positions processed, "
          f"{len(exceptions)} exceptions identified.")
    print(exceptions["exception_type"].value_counts().to_string())

    return recon_df, exceptions


if __name__ == "__main__":
    run()
