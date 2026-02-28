"""FinanceDataReader client for OHLCV and chart data."""

from datetime import datetime, date, timedelta
from typing import Optional, Dict, Any, List

import pandas as pd
import FinanceDataReader as fdr


def get_ohlcv(
    ticker: str,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None
) -> pd.DataFrame:
    """
    Get OHLCV (Open, High, Low, Close, Volume) data for a stock.
    
    Args:
        ticker: Stock ticker code (e.g., '005930' for Samsung Electronics)
        start_date: Start date in 'YYYY-MM-DD' format. Defaults to 30 days ago.
        end_date: End date in 'YYYY-MM-DD' format. Defaults to today.
    
    Returns:
        DataFrame with columns: Date, Open, High, Low, Close, Volume, Change
        Returns empty DataFrame on error.
    """
    try:
        # Ensure ticker is 6-digit format for Korean stocks
        ticker = str(ticker).zfill(6)
        
        # Set default dates if not provided
        if not end_date:
            end_date = datetime.now().strftime('%Y-%m-%d')
        if not start_date:
            # Default to 30 days ago
            start_date_dt = datetime.now().replace(day=1)  # First of month
            if start_date_dt > datetime.now():
                # Handle month overflow
                if start_date_dt.month == 12:
                    start_date_dt = start_date_dt.replace(year=start_date_dt.year + 1, month=1)
                else:
                    start_date_dt = start_date_dt.replace(month=start_date_dt.month + 1)
            start_date = start_date_dt.strftime('%Y-%m-%d')
        
        # Fetch data using FinanceDataReader
        df = fdr.DataReader(ticker, start_date, end_date)
        
        if df is None or df.empty:
            return pd.DataFrame()
        
        # Reset index to make Date a column
        if 'Date' not in df.columns and df.index.name == 'Date':
            df = df.reset_index()
        
        # Ensure required columns exist
        required_cols = ['Open', 'High', 'Low', 'Close', 'Volume']
        missing_cols = [col for col in required_cols if col not in df.columns]
        if missing_cols:
            return pd.DataFrame()
        
        # Select and order columns
        result_cols = ['Date', 'Open', 'High', 'Low', 'Close', 'Volume']
        if 'Change' in df.columns:
            result_cols.append('Change')
        
        df = df[result_cols].copy()
        
        # Convert Date to string for JSON serialization
        if 'Date' in df.columns:
            df['Date'] = pd.to_datetime(df['Date']).dt.strftime('%Y-%m-%d')
        
        return df
        
    except Exception as e:
        print(f"Error fetching OHLCV data for {ticker}: {e}")
        return pd.DataFrame()


def get_latest_price(ticker: str) -> Optional[Dict[str, Any]]:
    """
    Get the latest price data for a stock.
    
    Args:
        ticker: Stock ticker code (e.g., '005930' for Samsung Electronics)
    
    Returns:
        Dictionary with latest price data (Date, Open, High, Low, Close, Volume)
        Returns None on error.
    """
    try:
        # Ensure ticker is 6-digit format for Korean stocks
        ticker = str(ticker).zfill(6)
        
        # Get last 2 days of data to ensure we have the latest
        df = get_ohlcv(ticker, start_date=None, end_date=None)
        
        if df is None or df.empty:
            return None
        
        # Get the last row (most recent data)
        latest = df.iloc[-1]
        
        return {
            "date": latest.get("Date"),
            "open": float(latest.get("Open", 0)) if pd.notna(latest.get("Open")) else None,
            "high": float(latest.get("High", 0)) if pd.notna(latest.get("High")) else None,
            "low": float(latest.get("Low", 0)) if pd.notna(latest.get("Low")) else None,
            "close": float(latest.get("Close", 0)) if pd.notna(latest.get("Close")) else None,
            "volume": int(latest.get("Volume", 0)) if pd.notna(latest.get("Volume")) else None,
            "change": float(latest.get("Change", 0)) if "Change" in latest.index and pd.notna(latest.get("Change")) else None,
        }
        
    except Exception as e:
        print(f"Error fetching latest price for {ticker}: {e}")
        return None


def get_chart_data(
    ticker: str,
    days: int = 30
) -> List[Dict[str, Any]]:
    """
    Get chart data for a stock (formatted for charting libraries).
    
    Args:
        ticker: Stock ticker code
        days: Number of days to fetch (default 30)
    
    Returns:
        List of dictionaries with chart data
    """
    try:
        # Calculate start date
        end_date = datetime.now().strftime('%Y-%m-%d')
        start_date_dt = datetime.now() - timedelta(days=days)
        start_date = start_date_dt.strftime('%Y-%m-%d')
        
        df = get_ohlcv(ticker, start_date, end_date)
        
        if df.empty:
            return []
        
        # Convert to list of dicts for charting
        result = []
        for _, row in df.iterrows():
            result.append({
                "date": row.get("Date"),
                "open": float(row.get("Open", 0)) if pd.notna(row.get("Open")) else None,
                "high": float(row.get("High", 0)) if pd.notna(row.get("High")) else None,
                "low": float(row.get("Low", 0)) if pd.notna(row.get("Low")) else None,
                "close": float(row.get("Close", 0)) if pd.notna(row.get("Close")) else None,
                "volume": int(row.get("Volume", 0)) if pd.notna(row.get("Volume")) else None,
            })
        
        return result
        
    except Exception as e:
        print(f"Error fetching chart data for {ticker}: {e}")
        return []
