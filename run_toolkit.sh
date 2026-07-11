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

# 4. Run Advanced SQL Executive Risk Analytics Queries
echo 'Step 3: Running Production SQL Risk Management Dashboard...'
python3 -c "
import sqlite3, pandas as pd
conn = sqlite3.connect('data/portfolio_warehouse.db')
q2 = 'SELECT SUM(ABS(i.market_value - COALESCE(c.market_value, 0))) AS Total_Capital_At_Risk, COUNT(*) AS Total_Breaches FROM internal_ledger i LEFT JOIN custodian_statement c ON i.security_id = c.security_id WHERE i.quantity != COALESCE(c.quantity, 0) OR i.market_value != COALESCE(c.market_value, 0);'
q3 = 'SELECT i.ticker AS Ticker, COUNT(*) AS Total_Incidents, SUM(ABS(i.market_value - COALESCE(c.market_value, 0))) AS Concentrated_Risk FROM internal_ledger i LEFT JOIN custodian_statement c ON i.security_id = c.security_id WHERE i.quantity != COALESCE(c.quantity, 0) OR i.market_value != COALESCE(c.market_value, 0) GROUP BY i.ticker ORDER BY Concentrated_Risk DESC;'
print(pd.read_sql_query(q2, conn).to_string(index=False))
print(pd.read_sql_query(q3, conn).to_string(index=False))
conn.close()
"

echo '===================================================='
echo '✅ PIPELINE RUN COMPLETE - AUDIT SHEETS READY IN /output'
echo '===================================================='
