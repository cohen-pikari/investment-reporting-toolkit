import sqlite3
import pandas as pd
import yfinance as yf
from datetime import datetime

def fetch_live_market_prices(tickers):
    print(f"📡 Ingesting live market feeds for: {', '.join(tickers)}...")
    price_map = {}
    for ticker in tickers:
        try:
            security = yf.Ticker(ticker)
            history = security.history(period="5d")
            if not history.empty:
                latest_close = history['Close'].iloc[-1]
                price_map[ticker] = round(float(latest_close), 2)
            else:
                price_map[ticker] = None
        except Exception as e:
            print(f"⚠️ Market data ingestion failed for {ticker}: {str(e)}")
            price_map[ticker] = None
    return price_map

def run_live_reconciliation():
    conn = sqlite3.connect(':memory:') 
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE internal_ledger (
            ticker TEXT,
            security_name TEXT,
            internal_quantity REAL,
            internal_unit_cost REAL,
            internal_market_value REAL
        )
    ''')
    sample_holdings = [
        ('AAPL', 'Apple Inc.', 1000, 180.00, 180000.00),
        ('BHP.AX', 'BHP Group Limited', 5000, 42.50, 212500.00),
        ('ALT-VC-PRV', 'Collins St Private Equity Fund', 1, 500000.00, 500000.00)
    ]
    cursor.executemany('INSERT INTO internal_ledger VALUES (?,?,?,?,?)', sample_holdings)
    conn.commit()
    
    df_internal = pd.read_sql_query("SELECT * FROM internal_ledger", conn)
    tracked_tickers = ['AAPL', 'BHP.AX']
    live_prices = fetch_live_market_prices(tracked_tickers)
    
    custodian_records = []
    today_str = datetime.today().strftime('%Y-%m-%d')
    
    for _, row in df_internal.iterrows():
        ticker = row['ticker']
        qty = row['internal_quantity']
        if ticker in live_prices and live_prices[ticker] is not None:
            cust_price = live_prices[ticker]
            cust_mv = round(qty * cust_price, 2)
        else:
            cust_price = row['internal_unit_cost'] * 0.95
            cust_mv = round(qty * cust_price, 2)
            
        custodian_records.append({
            'ticker': ticker,
            'custodian_price': cust_price,
            'custodian_market_value': cust_mv
        })
        
    df_custodian = pd.DataFrame(custodian_records)
    recon_matrix = pd.merge(df_internal, df_custodian, on='ticker', how='left')
    recon_matrix['mv_variance'] = recon_matrix['custodian_market_value'] - recon_matrix['internal_market_value']
    
    exceptions = []
    for _, row in recon_matrix.iterrows():
        if abs(row['mv_variance']) > 0.01:
            exception_type = "PRICING_BREAK"
            resolution_protocol = "Verify internal data management corporate actions logs against external exchange feeds."
            if "ALT" in row['ticker']:
                exception_type = "ALTERNATIVES_VALUATION_LAG"
                resolution_protocol = "Flag to Private Markets division; verify capital call notice/latest NAV statement timeline."
                
            exceptions.append({
                'Ticker': row['ticker'],
                'Security Name': row['security_name'],
                'MV Variance': row['mv_variance'],
                'Exception Type': exception_type,
                'Resolution Protocol': resolution_protocol
            })
            
    df_exceptions = pd.DataFrame(exceptions)
    print("\n📊 --- INVESTMENT OPERATIONS EXCEPTION REPORT --- 📊")
    print(f"Timestamp: {today_str} | Variance Filter: Absolute > $0.01")
    print("=" * 85)
    if not df_exceptions.empty:
        print(df_exceptions[['Ticker', 'MV Variance', 'Exception Type', 'Resolution Protocol']].to_string(index=False))
    else:
        print("✅ Straight-Through Processing (STP) Success: Zero exceptions identified across portfolio balance.")
    print("=" * 85)
    conn.close()

if __name__ == "__main__":
    run_live_reconciliation()
