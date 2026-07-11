-- ==============================================================================
-- INVESTMENT OPERATIONS DATA WAREHOUSE AUDIT PIPELINE
-- Workflow: Reconcile Internal Ledger (IBOR) vs Custodian Statements (CBOR)
-- Target Lane: Identify Cash and Position Exception Breaks across Holdings
-- ==============================================================================

-- 📊 AUDIT QUERY 1: CORE RECONCILIATION MATCHING ENGINE
-- Joins the ledgers via an operational UNION set to isolate every discrepancy.
SELECT 
    i.security_id AS [Security ID], 
    i.ticker AS [Ticker], 
    i.quantity AS [Qty (Internal)], 
    COALESCE(c.quantity, 0) AS [Qty (Custodian)],
    (i.quantity - COALESCE(c.quantity, 0)) AS [Qty Variance], 
    i.market_value AS [MV (Internal)],
    COALESCE(c.market_value, 0) AS [MV (Custodian)], 
    (i.market_value - COALESCE(c.market_value, 0)) AS [MV Variance],
    'PORTFOLIO LEDGER MATCH' AS [Audit Lane]
FROM internal_ledger i
LEFT JOIN custodian_statement c ON i.security_id = c.security_id
WHERE i.quantity != COALESCE(c.quantity, 0) OR i.market_value != COALESCE(c.market_value, 0)

UNION

SELECT 
    c.security_id AS [Security ID], 
    c.ticker AS [Ticker], 
    0 AS [Qty (Internal)], 
    c.quantity AS [Qty (Custodian)],
    (0 - c.quantity) AS [Qty Variance], 
    0 AS [MV (Internal)],
    c.market_value AS [MV (Custodian)], 
    (0 - c.market_value) AS [MV Variance],
    'CUSTODIAN STATEMENT UNMATCHED' AS [Audit Lane]
FROM custodian_statement c
LEFT JOIN internal_ledger i ON c.security_id = i.security_id
WHERE i.security_id IS NULL;


-- 💰 AUDIT QUERY 2: TOTAL PORTFOLIO EXPOSURE AT RISK (MANAGEMENT REPORTING)
-- Calculates the total financial impact of all valuation breaks currently outstanding.
-- Uses ABS() so positive and negative variances do not cancel each other out.
SELECT 
    SUM(ABS(i.market_value - COALESCE(c.market_value, 0))) AS [Total Portfolio Capital At Risk],
    COUNT(*) AS [Total Line-Item Breaches]
FROM internal_ledger i
LEFT JOIN custodian_statement c ON i.security_id = c.security_id
WHERE i.quantity != COALESCE(c.quantity, 0) OR i.market_value != COALESCE(c.market_value, 0);


-- 🔎 AUDIT QUERY 3: SYSTEMIC FAILURE CONCENTRATION ANALYSIS
-- Aggregates data to pinpoint exactly which asset ticker drives the highest risk volume.
SELECT 
    i.ticker AS [Ticker Focus],
    COUNT(*) AS [Total Incidents],
    SUM(ABS(i.market_value - COALESCE(c.market_value, 0))) AS [Concentrated Variance Exposure]
FROM internal_ledger i
LEFT JOIN custodian_statement c ON i.security_id = c.security_id
WHERE i.quantity != COALESCE(c.quantity, 0) OR i.market_value != COALESCE(c.market_value, 0)
GROUP BY i.ticker
ORDER BY [Concentrated Variance Exposure] DESC;
