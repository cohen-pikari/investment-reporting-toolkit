#!/bin/bash

# Define corporate layout colors
BLUE='\033[0;34m'
GREEN='\033[0;32m'
CYAN='\033[0;36m'
CLEAR='\033[0m'

echo -e "${BLUE}====================================================================${CLEAR}"
echo -e "${BLUE}🚀 INITIALIZING INTEGRATED INVESTMENT OPERATIONS REPORTING TOOLKIT ${CLEAR}"
echo -e "${BLUE}====================================================================${CLEAR}"

echo -e "\n${CYAN}[STEP 1/4] Initializing Production SQL Warehouse Layer...${CLEAR}"
python3 scripts/initialize_warehouse.py

echo -e "\n${CYAN}[STEP 2/4] Executing Live Market Data Ingestion & Pricing Reconciliation Engine...${CLEAR}"
python3 scripts/reconcile_live_feeds.py

echo -e "\n${CYAN}[STEP 3/4] Generating Executive MIS Operations Dashboard Visuals...${CLEAR}"
python3 scripts/generate_ops_dashboard.py

echo -e "\n${CYAN}[STEP 4/4] Compiling Formatted Corporate Audit Spreadsheet Ledger...${CLEAR}"
python3 scripts/generate_excel_sheets.py

echo -e "\n${GREEN}====================================================================${CLEAR}"
echo -e "${GREEN}✅ PIPELINE INTEGRATION RUN COMPLETE - ALL ARTIFACTS READY IN /output ${CLEAR}"
echo -e "${GREEN}====================================================================${CLEAR}"

