#!/bin/bash

# ==============================================================================
# MASTER OPERATIONS PIPELINE CONTROLLER - INVESTMENT REPORTING TOOLKIT
# ==============================================================================

echo '===================================================='
echo '🚀 INITIALIZING AUTOMATED INVESTMENT REPORTING TOOLKIT'
echo '===================================================='

# 1. Ensure virtual environment is active
if [ -d 'venv' ]; then
    source venv/bin/activate
fi

# 2. Execute primary Python reconciliation and excel spreadsheet generation
echo 'Step 1: Running Python pandas/openpyxl Reconciliation Pipeline...'
python3 scripts/reconcile.py

# 3. Synchronize local relational SQL database warehouse tables
echo 'Step 2: Syncing Variation Data to SQLite Warehouse...'
python3 -c "
import os, sqlite3, pandas as pd
conn = sqlite3.connect('data/portfolio_warehouse.db')
pd.read_csv('data/internal_ledger.csv').to_sql('internal_ledger', conn, if_exists='replace', index=False)
pd.read_csv('data/custodian_statement.csv').to_sql('custodian_statement', conn, if_exists='replace', index=False)
conn.close()
"
echo '[SUCCESS] Relational SQLite tables fully refreshed.'

# 4. Run Advanced SQL Executive Risk Analytics and Generate Management Sheet
echo 'Step 3: Compiling Relational Database Warehouse Risk Reports...'
python3 scripts/query_db.py

echo '===================================================='
echo '✅ PIPELINE RUN COMPLETE - ALL AUDIT REPORTS GENERATED IN /output'
echo '===================================================='
