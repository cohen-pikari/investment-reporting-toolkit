"""
SQLite Warehouse Initializer
------------------------------
Loads the full reconciliation matrix (output of reconciliation_engine.py)
into a relational SQLite warehouse, enabling downstream SQL-based risk
aggregation and reporting independent of the pandas layer.
"""

import os
import sqlite3
import pandas as pd


def build_warehouse(db_path="data/portfolio_warehouse.db",
                     recon_csv="output/full_reconciliation_matrix.csv"):
    os.makedirs("data", exist_ok=True)

    if not os.path.exists(recon_csv):
        print(f"Error: {recon_csv} not found. Run reconciliation_engine.py first.")
        return

    df = pd.read_csv(recon_csv)

    conn = sqlite3.connect(db_path)
    df.to_sql("reconciliation_matrix", conn, if_exists="replace", index=False)

    conn.execute("""
        CREATE INDEX IF NOT EXISTS idx_exception_type
        ON reconciliation_matrix (exception_type)
    """)
    conn.execute("""
        CREATE INDEX IF NOT EXISTS idx_asset_class
        ON reconciliation_matrix (asset_class)
    """)
    conn.commit()
    conn.close()

    print(f"Warehouse initialized: {db_path} ({len(df)} rows loaded into "
          f"'reconciliation_matrix' table)")


if __name__ == "__main__":
    build_warehouse()
