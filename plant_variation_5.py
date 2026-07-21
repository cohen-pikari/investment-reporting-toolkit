import pathlib

v5_internal = """trade_date,security_id,ticker,quantity,market_value,currency
2026-07-14,US31162V1044,AAPL,1000,185000.00,USD
2026-07-14,US5949181045,MSFT,512,215040.00,USD
2026-07-14,US88160R1014,TSLA,300,75000.00,USD
2026-07-14,CASH001,USD,50000,50000.00,USD
"""

v5_custodian = """statement_date,security_id,ticker,quantity,market_value,currency
2026-07-14,US31162V1044,AAPL,1000,185000.00,USD
2026-07-14,US5949181045,MSFT,500,210000.00,USD
2026-07-14,CASH001,USD,48500,48500.00,USD
"""

pathlib.Path('data/internal_ledger.csv').write_text(v5_internal)
pathlib.Path('data/custodian_statement.csv').write_text(v5_custodian)
print('[COMPLETE] Data Variation 5 (DRP Processing Lag) planted.')
