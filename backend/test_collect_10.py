"""
Test: Collect 10 stocks and save to data directory
"""
import sys
sys.path.insert(0, 'backend')

from batch.collect_data import collect, save
from datetime import datetime

# Collect 10 stocks
print("Collecting 10 stocks...")
df = collect(limit=10)

if not df.empty:
    # Save with today's date
    today = datetime.now().strftime("%Y%m%d")
    save(df, today)
    
    print(f"\n=== SUCCESS: Collected {len(df)} stocks ===")
    print(df[['ticker', 'name', 'current_price', 'per', 'pbr', 'forward_per', 'dividend_yield']].to_string())
    
    # Verify file was created
    import os
    csv_path = f"data/daily/stocks_{today}.csv"
    if os.path.exists(csv_path):
        print(f"\n✓ Saved to: {csv_path}")
        print(f"  File size: {os.path.getsize(csv_path)} bytes")
else:
    print("ERROR: No data collected")
