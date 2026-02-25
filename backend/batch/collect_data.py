"""
KOSPI Stock Data Collection Script using pykrx

This module collects KOSPI stock data including:
- OHLCV (Open, High, Low, Close, Volume)
- PER (Price-to-Earnings Ratio)
- PBR (Price-to-Book Ratio)
- Market Capitalization (시가총액)

Usage:
    python -m backend.batch.collect_data
"""

from datetime import datetime, timedelta
from typing import Optional
import os

import pandas as pd
from pykrx import stock


def get_kospi_ticker_list(date: Optional[str] = None) -> list[str]:
    """
    Get list of KOSPI ticker codes.
    
    Args:
        date: Date in YYYYMMDD format. Defaults to today.
    
    Returns:
        List of ticker codes (e.g., ['005930', '000001', ...])
    """
    if date is None:
        date = datetime.now().strftime("%Y%m%d")
    
    tickers = stock.get_market_ticker_list(date, market="KOSPI")
    return tickers


def get_stock_ohlcv(ticker: str, date: str) -> pd.DataFrame:
    """
    Get OHLCV data for a specific stock.
    
    Args:
        ticker: Stock ticker code (e.g., '005930')
        date: Date in YYYYMMDD format
    
    Returns:
        DataFrame with columns: ['시가', '고가', '저가', '종가', '거래량', '거래대금']
    """
    try:
        # Get last 1 day (today)
        end_date = datetime.strptime(date, "%Y%m%d")
        start_date = end_date - timedelta(days=5)  # Buffer for weekends
        
        df = stock.get_market_ohlcv(
            start_date.strftime("%Y%m%d"),
            end_date.strftime("%Y%m%d"),
            ticker
        )
        
        if df.empty:
            return pd.DataFrame()
        
        # Get the last row (most recent)
        return df.iloc[-1:]
    except Exception:
        return pd.DataFrame()
    """
    Get OHLCV data for a specific stock.
    
    Args:
        ticker: Stock ticker code (e.g., '005930')
        date: Date in YYYYMMDD format
    
    Returns:
        DataFrame with columns: ['시가', '고가', '저가', '종가', '거래량', '거래대금']
    """
    # Get last 1 day (today)
    end_date = datetime.strptime(date, "%Y%m%d")
    start_date = end_date - timedelta(days=5)  # Buffer for weekends
    
    df = stock.get_market_ohlcv(
        start_date.strftime("%Y%m%d"),
        end_date.strftime("%Y%m%d"),
        ticker
    )
    
    if df.empty:
        return pd.DataFrame()
    
    # Get the last row (most recent)
    return df.iloc[-1:]


def get_stock_fundamental(ticker: str, date: str) -> pd.DataFrame:
    """
    Get fundamental data (PER, PBR, 시가총액) for a specific stock.
    
    Args:
        ticker: Stock ticker code (e.g., '005930')
        date: Date in YYYYMMDD format
    
    Returns:
        DataFrame with columns: ['PER', 'PBR', '시가총액', 'EPS', 'BPS']
    """
    try:
        df = stock.get_market_fundamental(date, date, ticker)
        
        if df.empty:
            return pd.DataFrame()
        
        # Get the last row (most recent)
        return df.iloc[-1:]
    except Exception:
        return pd.DataFrame()
    """
    Get fundamental data (PER, PBR, 시가총액) for a specific stock.
    
    Args:
        ticker: Stock ticker code (e.g., '005930')
        date: Date in YYYYMMDD format
    
    Returns:
        DataFrame with columns: ['PER', 'PBR', '시가총액', 'EPS', 'BPS']
    """
    df = stock.get_market_fundamental(date, date, ticker)
    
    if df.empty:
        return pd.DataFrame()
    
    # Get the last row (most recent)
    return df.iloc[-1:]


def get_stock_name(ticker: str) -> str:
    """
    Get company name for a ticker code.
    
    Args:
        ticker: Stock ticker code
    
    Returns:
        Company name
    """
    return stock.get_market_ticker_name(ticker)


def collect_kospi_data(date: Optional[str] = None, limit: Optional[int] = None) -> pd.DataFrame:
    """
    Collect all KOSPI stock data for a given date.
    
    Args:
        date: Date in YYYYMMDD format. Defaults to today.
        limit: Optional limit for number of stocks to collect (for testing)
    
    Returns:
        DataFrame with all collected stock data
    """
    if date is None:
        date = datetime.now().strftime("%Y%m%d")
    
    print(f"Collecting KOSPI data for {date}...")
    
    # Get ticker list
    tickers = get_kospi_ticker_list(date)
    print(f"Found {len(tickers)} KOSPI stocks")
    
    if limit:
        tickers = tickers[:limit]
        print(f"Limited to {limit} stocks (for testing)")
    
    all_data = []
    
    for i, ticker in enumerate(tickers):
        try:
            # Get OHLCV
            ohlcv = get_stock_ohlcv(ticker, date)
            
            # Get fundamental data
            fundamental = get_stock_fundamental(ticker, date)
            
            # Get company name
            name = get_stock_name(ticker)
            
            # Combine data
            if not ohlcv.empty:
                row = {
                    'ticker': ticker,
                    'name': name,
                    'date': date,
                }
                
                # Add OHLCV columns
                if not ohlcv.empty:
                    row['open'] = ohlcv['시가'].values[0] if '시가' in ohlcv.columns else None
                    row['high'] = ohlcv['고가'].values[0] if '고가' in ohlcv.columns else None
                    row['low'] = ohlcv['저가'].values[0] if '저가' in ohlcv.columns else None
                    row['close'] = ohlcv['종가'].values[0] if '종가' in ohlcv.columns else None
                    row['volume'] = ohlcv['거래량'].values[0] if '거래량' in ohlcv.columns else None
                    row['amount'] = ohlcv['거래대금'].values[0] if '거래대금' in ohlcv.columns else None
                
                # Add fundamental columns
                if not fundamental.empty:
                    row['per'] = fundamental['PER'].values[0] if 'PER' in fundamental.columns else None
                    row['pbr'] = fundamental['PBR'].values[0] if 'PBR' in fundamental.columns else None
                    row['market_cap'] = fundamental['시가총액'].values[0] if '시가총액' in fundamental.columns else None
                    row['eps'] = fundamental['EPS'].values[0] if 'EPS' in fundamental.columns else None
                    row['bps'] = fundamental['BPS'].values[0] if 'BPS' in fundamental.columns else None
                else:
                    row['per'] = None
                    row['pbr'] = None
                    row['market_cap'] = None
                    row['eps'] = None
                    row['bps'] = None
                
                all_data.append(row)
            
            # Progress indicator
            if (i + 1) % 100 == 0:
                print(f"  Processed {i + 1}/{len(tickers)} stocks...")
                
        except Exception as e:
            print(f"  Error processing {ticker}: {e}")
            continue
    
    # Create DataFrame
    df = pd.DataFrame(all_data)
    
    print(f"Successfully collected {len(df)} stocks")
    
    return df


def save_to_csv(df: pd.DataFrame, date: Optional[str] = None, output_dir: str = "data") -> str:
    """
    Save DataFrame to CSV file.
    
    Args:
        df: DataFrame to save
        date: Date string for filename (YYYYMMDD). Defaults to today.
        output_dir: Output directory path
    
    Returns:
        Path to saved file
    """
    if date is None:
        date = datetime.now().strftime("%Y%m%d")
    
    # Create output directory if not exists
    os.makedirs(output_dir, exist_ok=True)
    
    filename = f"stocks_{date}.csv"
    filepath = os.path.join(output_dir, filename)
    
    df.to_csv(filepath, index=False, encoding='utf-8-sig')
    
    print(f"Saved to {filepath}")
    
    return filepath


def save_to_json(df: pd.DataFrame, date: Optional[str] = None, output_dir: str = "data") -> str:
    """
    Save DataFrame to JSON file.
    
    Args:
        df: DataFrame to save
        date: Date string for filename (YYYYMMDD). Defaults to today.
        output_dir: Output directory path
    
    Returns:
        Path to saved file
    """
    if date is None:
        date = datetime.now().strftime("%Y%m%d")
    
    # Create output directory if not exists
    os.makedirs(output_dir, exist_ok=True)
    
    filename = f"stocks_{date}.json"
    filepath = os.path.join(output_dir, filename)
    
    df.to_json(filepath, orient='records', force_ascii=False, indent=2)
    
    print(f"Saved to {filepath}")
    
    return filepath


def main():
    """Main entry point for data collection."""
    date = datetime.now().strftime("%Y%m%d")
    
    # Collect data
    df = collect_kospi_data(date)
    
    if not df.empty:
        # Save to CSV
        save_to_csv(df, date)
        
        # Also save to JSON
        save_to_json(df, date)
        
        print("\nData collection completed!")
        print(f"Total stocks: {len(df)}")
        print("\nSample data:")
        print(df.head())
    else:
        print("No data collected")


if __name__ == "__main__":
    main()
