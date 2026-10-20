# tests/test_reconciliation_integrity.py
"""
Basic integrity checks for the reconciliation engine: verifies core
guarantees the system depends on, rather than assuming they hold.
"""

import pandas as pd
from reconciliation_engine import load_ledgers, reconcile


def test_entry_data_never_modified():
    """The internal ledger's original values must never be altered by reconciliation."""
    df_internal, df_custodian = load_ledgers()
    original_internal = df_internal.copy()

    reconcile(df_internal, df_custodian)

    pd.testing.assert_frame_equal(df_internal, original_internal)
    print("PASS: internal ledger data untouched by reconciliation.")


def test_no_positions_silently_dropped():
    """Every unique security in either source file must appear in the output."""
    df_internal, df_custodian = load_ledgers()
    result = reconcile(df_internal, df_custodian)

    all_ids = set(df_internal["security_id"]) | set(df_custodian["security_id"])
    result_ids = set(result["security_id"])

    assert all_ids == result_ids, "Some positions were dropped during reconciliation!"
    print("PASS: no positions silently dropped.")


if __name__ == "__main__":
    test_entry_data_never_modified()
    test_no_positions_silently_dropped()
