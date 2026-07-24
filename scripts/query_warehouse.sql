-- ==============================================================================
-- INVESTMENT OPERATIONS DATA WAREHOUSE — RISK AGGREGATION QUERIES
-- Source: reconciliation_matrix (SQLite), populated by initialize_warehouse.py
-- ==============================================================================

-- QUERY 1: Total Capital At Risk (all outstanding exceptions)
SELECT
    COUNT(*) AS total_exceptions,
    SUM(ABS(mv_variance)) AS total_capital_at_risk
FROM reconciliation_matrix
WHERE exception_type != 'MATCHED';

-- QUERY 2: Exception Concentration by Type
SELECT
    exception_type,
    COUNT(*) AS incident_count,
    SUM(ABS(mv_variance)) AS concentrated_risk_value
FROM reconciliation_matrix
WHERE exception_type != 'MATCHED'
GROUP BY exception_type
ORDER BY concentrated_risk_value DESC;

-- QUERY 3: Exception Concentration by Asset Class
-- Identifies which part of the portfolio is structurally driving the most breaks —
-- useful for spotting whether a specific asset class needs a process improvement.
SELECT
    asset_class,
    COUNT(*) AS incident_count,
    SUM(ABS(mv_variance)) AS concentrated_risk_value,
    ROUND(100.0 * COUNT(*) / (SELECT COUNT(*) FROM reconciliation_matrix WHERE exception_type != 'MATCHED'), 1) AS pct_of_all_exceptions
FROM reconciliation_matrix
WHERE exception_type != 'MATCHED'
GROUP BY asset_class
ORDER BY concentrated_risk_value DESC;

-- QUERY 4: Straight-Through Processing (STP) Rate
-- The proportion of the portfolio that matched cleanly with zero manual intervention —
-- a standard operational KPI for a reconciliation control function.
SELECT
    COUNT(*) AS total_positions,
    SUM(CASE WHEN exception_type = 'MATCHED' THEN 1 ELSE 0 END) AS matched_positions,
    ROUND(100.0 * SUM(CASE WHEN exception_type = 'MATCHED' THEN 1 ELSE 0 END) / COUNT(*), 1) AS stp_rate_pct
FROM reconciliation_matrix;
