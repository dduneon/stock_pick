"""
Stock Data Loader

Loads stock data from CSV/JSON files collected via pykrx.
"""

import os
import glob
from typing import List, Optional, Dict, Any
from datetime import datetime

import pandas as pd


DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "data")


def get_latest_data_file() -> Optional[str]:
    """Get the most recent stock data file."""
    # Try CSV first, then JSON
    for ext in ["csv", "json"]:
        pattern = os.path.join(DATA_DIR, f"stocks_*.{ext}")
        files = glob.glob(pattern)
        if files:
            return max(files, key=os.path.getmtime)
    return None


def load_stocks_data() -> pd.DataFrame:
    """
    Load stock data from the latest available data file.
    
    Returns:
        DataFrame with stock data, or empty DataFrame if no data found
    """
    data_file = get_latest_data_file()
    
    if not data_file or not os.path.exists(data_file):
        return pd.DataFrame()
    
    if data_file.endswith(".csv"):
        return pd.read_csv(data_file, encoding="utf-8-sig")
    elif data_file.endswith(".json"):
        return pd.read_json(data_file, orient="records")
    
    return pd.DataFrame()


def get_all_stocks(limit: Optional[int] = None) -> List[Dict[str, Any]]:
    """
    Get list of all stocks.
    
    Args:
        limit: Optional limit for number of results
        
    Returns:
        List of stock dictionaries
    """
    df = load_stocks_data()
    
    if df.empty:
        return []
    
    # Select and rename columns for API response
    result = []
    for _, row in df.iterrows():
        stock = {
            "ticker": str(row.get("ticker", "")),
            "name": str(row.get("name", "")),
            "current_price": float(row.get("close", 0)) if pd.notna(row.get("close")) else 0.0,
            "change_rate": float(row.get("change_rate", 0)) if pd.notna(row.get("change_rate")) else 0.0,
            "per": float(row["per"]) if pd.notna(row.get("per")) else None,
            "pbr": float(row["pbr"]) if pd.notna(row.get("pbr")) else None,
            "market_cap": float(row["market_cap"]) if pd.notna(row.get("market_cap")) else None,
            "eps": float(row["eps"]) if pd.notna(row.get("eps")) else None,
            "bps": float(row["bps"]) if pd.notna(row.get("bps")) else None,
        }
        result.append(stock)
    
    if limit:
        result = result[:limit]
    
    return result


def get_stock_by_ticker(ticker: str) -> Optional[Dict[str, Any]]:
    """
    Get detailed stock information by ticker.
    
    Args:
        ticker: Stock ticker code
        
    Returns:
        Stock dictionary or None if not found
    """
    df = load_stocks_data()
    
    if df.empty:
        return None
    
    # Find matching stock
    matches = df[df["ticker"].astype(str) == ticker]
    
    if matches.empty:
        return None
    
    row = matches.iloc[0]
    return {
        "ticker": str(row.get("ticker", "")),
        "name": str(row.get("name", "")),
        "current_price": float(row.get("close", 0)) if pd.notna(row.get("close")) else 0.0,
        "change_rate": float(row.get("change_rate", 0)) if pd.notna(row.get("change_rate")) else 0.0,
        "per": float(row["per"]) if pd.notna(row.get("per")) else None,
        "pbr": float(row["pbr"]) if pd.notna(row.get("pbr")) else None,
        "market_cap": float(row["market_cap"]) if pd.notna(row.get("market_cap")) else None,
        "eps": float(row["eps"]) if pd.notna(row.get("eps")) else None,
        "bps": float(row["bps"]) if pd.notna(row.get("bps")) else None,
        "open": float(row["open"]) if pd.notna(row.get("open")) else None,
        "high": float(row["high"]) if pd.notna(row.get("high")) else None,
        "low": float(row["low"]) if pd.notna(row.get("low")) else None,
        "volume": int(row["volume"]) if pd.notna(row.get("volume")) else None,
    }


def search_stocks(query: str) -> List[Dict[str, Any]]:
    """
    Search stocks by name.
    
    Args:
        query: Search query string
        
    Returns:
        List of matching stocks
    """
    df = load_stocks_data()
    
    if df.empty:
        return []
    
    # Case-insensitive search
    query_lower = query.lower()
    matches = df[df["name"].astype(str).str.lower().str.contains(query_lower, na=False)]
    
    result = []
    for _, row in matches.iterrows():
        stock = {
            "ticker": str(row.get("ticker", "")),
            "name": str(row.get("name", "")),
            "current_price": float(row.get("close", 0)) if pd.notna(row.get("close")) else 0.0,
            "change_rate": float(row.get("change_rate", 0)) if pd.notna(row.get("change_rate")) else 0.0,
        }
        result.append(stock)
    
    return result
