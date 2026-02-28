"""
Collect historical OHLCV data for technical analysis.
Stores 120+ days of data for MA/RSI calculations.
"""

from pykrx import stock
import pandas as pd
from datetime import datetime, timedelta
from typing import List, Optional
import os


def collect_historical_ohlcv(
    ticker: str,
    days: int = 120
) -> pd.DataFrame:
    """
    Collect historical OHLCV data for a single stock.
    
    Args:
        ticker: Stock ticker code (e.g., '005930')
        days: Number of days to collect (default: 120 for MA120)
    
    Returns:
        DataFrame with columns: date, open, high, low, close, volume
    """
    end_date = datetime.now()
    start_date = end_date - timedelta(days=days + 30)  # Buffer for weekends/holidays
    
    df = stock.get_market_ohlcv(
        start_date.strftime("%Y%m%d"),
        end_date.strftime("%Y%m%d"),
        ticker
    )
    
    if df.empty:
        return pd.DataFrame()
    
    # Rename columns to English
    df = df.rename(columns={
        '시가': 'open',
        '고가': 'high',
        '저가': 'low',
        '종가': 'close',
        '거래량': 'volume',
        '거래대금': 'amount'
    })
    
    # Keep only last N days
    df = df.tail(days)
    
    return df


def save_historical_data(ticker: str, df: pd.DataFrame, output_dir: str = "data/history"):
    """Save historical data to CSV."""
    os.makedirs(output_dir, exist_ok=True)
    filepath = os.path.join(output_dir, f"{ticker}.csv")
    df.to_csv(filepath)
    return filepath


def load_historical_data(ticker: str, input_dir: str = "data/history") -> pd.DataFrame:
    """Load historical data from CSV if it exists."""
    filepath = os.path.join(input_dir, f"{ticker}.csv")
    if os.path.exists(filepath):
        df = pd.read_csv(filepath, index_col=0, parse_dates=True)
        return df
    return pd.DataFrame()


def collect_and_save_all_kospi_history(days: int = 120, limit: Optional[int] = None):
    """
    Collect historical data for all KOSPI stocks.
    
    Args:
        days: Number of days of history to collect
        limit: Optional limit for number of stocks (for testing)
    """
    from backend.batch.collect_data import get_kospi_ticker_list
    
    date = datetime.now().strftime("%Y%m%d")
    tickers = get_kospi_ticker_list(date)
    
    if limit:
        tickers = tickers[:limit]
    
    print(f"Collecting {days} days of historical data for {len(tickers)} stocks...")
    
    success_count = 0
    error_count = 0
    
    for i, ticker in enumerate(tickers):
        try:
            df = collect_historical_ohlcv(ticker, days)
            if not df.empty:
                save_historical_data(ticker, df)
                success_count += 1
            else:
                error_count += 1
            
            if (i + 1) % 50 == 0:
                print(f"  Progress: {i + 1}/{len(tickers)} stocks processed")
                
        except Exception as e:
            print(f"  Error collecting {ticker}: {e}")
            error_count += 1
    
    print(f"\nCollection complete:")
    print(f"  Success: {success_count}")
    print(f"  Errors: {error_count}")


if __name__ == "__main__":
    # Test with Samsung Electronics
    print("Testing data collection for Samsung Electronics (005930)...")
    df = collect_historical_ohlcv('005930', days=120)
    print(f"Collected {len(df)} days of data")
    print(df.tail())
    
    # Save test data
    filepath = save_historical_data('005930', df)
    print(f"\nSaved to: {filepath}")
