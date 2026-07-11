-- ==============================================================================
-- INVESTMENT OPERATIONS DATA WAREHOUSE AUDIT PIPELINE
-- Workflow: Reconcile Internal Ledger (IBOR) vs Custodian Statements (CBOR)
-- Target Lane: Identify Cash and Position Exception Breaks across Holdings
-- ==============================================================================

-- PART A: INTERROGATING CASH LINE-ITEM VARIANCE (CASH RECONCILIATION)
SELECT 
    security_id AS [Security ID],
    ticker AS [Ticker],
    quantity AS [Qty (Internal)],
    market_value AS [MV (Internal)]
FROM internal_ledger
WHERE security_id = 'CASH001';


-- PART B: COMPREHENSIVE RECONCILIATION AUDIT (SECURITIES MATCHING MATRIX)
-- Uses a structural UNION set to perfectly simulate a FULL OUTER JOIN across 
-- internal portfolio accounting engines and external custodian bank feeds.
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
