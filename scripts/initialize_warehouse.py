import sqlite3
import os

def build_data_warehouse():
    db_path = "data/portfolio_warehouse.db"
    
    # Ensure data directory exists cleanly
    os.makedirs("data", exist_ok=True)
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Create production schema layout with explicit constraints
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS internal_ledger (
            ticker TEXT PRIMARY KEY,
            security_name TEXT NOT NULL,
            quantity REAL NOT NULL,
            unit_cost REAL NOT NULL,
            market_value REAL NOT NULL
        )
    ''')
    
    # Seed data arrays matching your thesis positions & watchlist
    sample_holdings = [
        ('AAPL', 'Apple Inc.', 1000, 180.00, 180000.00),
        ('BHP.AX', 'BHP Group Limited', 5000, 42.50, 212500.00),
        ('ALT-VC-PRV', 'Collins St Private Equity Fund', 1, 500000.00, 500000.00)
    ]
    
    cursor.executemany('INSERT OR REPLACE INTO internal_ledger VALUES (?,?,?,?,?)', sample_holdings)
    conn.commit()
    conn.close()
    print(f"🗄️ SQL Warehouse Layer successfully initialized at: {db_path}")

if __name__ == "__main__":
    build_data_warehouse()

