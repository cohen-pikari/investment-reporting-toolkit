#!/bin/bash
BLUE='\033[0;34m'
GREEN='\033[0;32m'
CYAN='\033[0;36m'
CLEAR='\033[0m'

echo -e "${BLUE}====================================================================${CLEAR}"
echo -e "${BLUE} INVESTMENT OPERATIONS REPORTING TOOLKIT — FULL PIPELINE RUN ${CLEAR}"
echo -e "${BLUE}====================================================================${CLEAR}"

echo -e "\n${CYAN}[STEP 1/5] Generating synthetic multi-asset portfolio dataset...${CLEAR}"
python3 scripts/generate_synthetic_data.py

echo -e "\n${CYAN}[STEP 2/5] Running core reconciliation engine (IBOR vs CBOR)...${CLEAR}"
python3 reconciliation_engine.py

echo -e "\n${CYAN}[STEP 3/5] Loading results into SQLite warehouse...${CLEAR}"
python3 scripts/initialize_warehouse.py

echo -e "\n${CYAN}[STEP 4/5] Generating executive MIS dashboard and Excel exception report...${CLEAR}"
python3 scripts/generate_ops_dashboard.py
python3 scripts/generate_excel_sheets.py

echo -e "\n${CYAN}[STEP 5/5] Compiling SQL-driven management summary report...${CLEAR}"
python3 scripts/generate_sql_summary.py

echo -e "\n${GREEN}====================================================================${CLEAR}"
echo -e "${GREEN} PIPELINE COMPLETE — all artifacts ready in /output ${CLEAR}"
echo -e "${GREEN}====================================================================${CLEAR}"
