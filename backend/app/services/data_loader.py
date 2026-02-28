"""
Stock Data Loader
=================

Loads stock data from multiple sources:
- CSV/JSON files (backward compatibility)
- Naver Finance (valuation metrics: PER, PBR, Forward PER, EPS, BPS, market_cap, dividend_yield)
- FinanceDataReader (OHLCV price data)
- DART API (quarterly fundamentals: ROE, debt_ratio)

Provides unified get_stock_data(ticker) function that merges all sources with caching.
"""

import os
import glob
import time
from typing import List, Optional, Dict, Any
from datetime import datetime

import pandas as pd

# Use DATA_DIR env var, fallback to project root data directory
DATA_DIR = os.environ.get("DATA_DIR", os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))), "data"))
DAILY_DATA_DIR = os.path.join(DATA_DIR, "daily")
QUARTERLY_DATA_DIR = os.path.join(DATA_DIR, "quarterly")
DATA_DIR = os.environ.get("DATA_DIR", os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))), "data"))

# Cache configuration via environment variables
CACHE_TTL_DAILY = int(os.environ.get("CACHE_TTL_DAILY", 3600))  # 1 hour default
CACHE_TTL_QUARTERLY = int(os.environ.get("CACHE_TTL_QUARTERLY", 86400 * 90))  # 90 days default

# Import external data sources
from app.services import naver_crawler
from app.services import fdr_client
from app.services.dart_api import DartAPIClient


# In-memory cache for API data
# Structure: {ticker: {"data": ..., "timestamp": ...}}
_valuation_cache: Dict[str, Dict[str, Any]] = {}
_price_cache: Dict[str, Dict[str, Any]] = {}
_fundamentals_cache: Dict[str, Dict[str, Any]] = {}


def _get_cached_data(cache: Dict[str, Dict[str, Any]], ticker: str, ttl: int) -> Optional[Dict[str, Any]]:
    """Get data from cache if still valid."""
    if ticker in cache:
        cached = cache[ticker]
        if time.time() - cached["timestamp"] < ttl:
            return cached["data"]
    return None


def _set_cached_data(cache: Dict[str, Dict[str, Any]], ticker: str, data: Dict[str, Any]) -> None:
    """Set data in cache with current timestamp."""
    cache[ticker] = {"data": data, "timestamp": time.time()}


# =============================================================================
# CSV/JSON File Loading (New Layered Structure + Backward Compatibility)
# =============================================================================


def get_latest_data_file(pattern: str = "stocks_*.csv", use_new_structure: bool = True) -> Optional[str]:
    """Get the most recent stock data file matching pattern.
    
    Args:
        pattern: Glob pattern to match (e.g., "stocks_*.csv", "fundamentals_*.csv")
        use_new_structure: If True, first search new directories (daily/, quarterly/), then fall back to old location
    
    Returns:
        Path to the latest matching file, or None if not found
    """
    search_dirs = []
    
    if use_new_structure:
        # Determine which new directory to search based on pattern
        if "fundamentals" in pattern:
            search_dirs = [QUARTERLY_DATA_DIR, DATA_DIR]  # Try new structure first, then backward compat
        elif "stocks_advanced" in pattern:
            search_dirs = [DATA_DIR]  # Backward compat only
        else:
            # Default: stocks_*.csv - try daily first, then backward compat
            search_dirs = [DAILY_DATA_DIR, DATA_DIR]
    else:
        search_dirs = [DATA_DIR]
    
    # Try CSV first, then JSON
    for ext in ["csv", "json"]:
        for search_dir in search_dirs:
            if not os.path.exists(search_dir):
                continue
            file_pattern = os.path.join(search_dir, pattern.replace("*.csv", f"*.{ext}").replace("*.json", f"*.{ext}"))
            files = glob.glob(file_pattern)
            if files:
                return max(files, key=os.path.getmtime)
    return None


def load_stocks_data() -> pd.DataFrame:
    """
    Load stock data from the latest available data file.
    
    Priority:
    1. Try new structure: data/daily/stocks_*.csv + data/quarterly/fundamentals_*.csv
    2. Fallback: data/stocks_*.csv + data/stocks_advanced_*.csv (backward compat)
    
    Returns:
        DataFrame with stock data, or empty DataFrame if no data found
    """
    # Try new structure first
    daily_file = get_latest_data_file("stocks_*.csv", use_new_structure=True)
    quarterly_file = get_latest_data_file("fundamentals_*.csv", use_new_structure=True)
    
    # If no new structure files, fall back to old structure
    if not daily_file:
        daily_file = get_latest_data_file("stocks_*.csv", use_new_structure=False)
        quarterly_file = get_latest_data_file("stocks_advanced_*.csv", use_new_structure=False)
    
    if not daily_file or not os.path.exists(daily_file):
        return pd.DataFrame()
    
    # Load daily/basic data
    if daily_file.endswith(".csv"):
        basic_df = pd.read_csv(daily_file, encoding="utf-8-sig")
    elif daily_file.endswith(".json"):
        basic_df = pd.read_json(daily_file, orient="records")
    else:
        return pd.DataFrame()
    
    # Ensure ticker column is string type with leading zeros preserved
    if 'ticker' in basic_df.columns:
        basic_df['ticker'] = basic_df['ticker'].astype(str).str.zfill(6)
    
    # Load quarterly/fundamentals data if available
    if quarterly_file and os.path.exists(quarterly_file) and quarterly_file != daily_file:
        try:
            if quarterly_file.endswith(".csv"):
                quarterly_df = pd.read_csv(quarterly_file, encoding="utf-8-sig")
            elif quarterly_file.endswith(".json"):
                quarterly_df = pd.read_json(quarterly_file, orient="records")
            else:
                quarterly_df = pd.DataFrame()
            
            # Ensure ticker column is string type
            if 'ticker' in quarterly_df.columns:
                quarterly_df['ticker'] = quarterly_df['ticker'].astype(str).str.zfill(6)
            
            # Merge quarterly data into basic data
            if not quarterly_df.empty and 'ticker' in quarterly_df.columns:
                # Columns to merge from quarterly data
                merge_columns = ['roe', 'debt_ratio', 'forward_pe', 'eps_growth_yoy', 'sector']
                existing_cols = [col for col in merge_columns if col in quarterly_df.columns]
                
                if existing_cols:
                    # Create merge subset
                    merge_df = quarterly_df[['ticker'] + existing_cols].copy()
                    
                    # Merge on ticker
                    basic_df = basic_df.merge(merge_df, on='ticker', how='left', suffixes=('', '_qtr'))
                    
                    # Use quarterly values where basic is null
                    for col in existing_cols:
                        if col in basic_df.columns and f"{col}_qtr" in basic_df.columns:
                            basic_df[col] = basic_df[col].fillna(basic_df[f"{col}_qtr"])
                            basic_df = basic_df.drop(columns=[f"{col}_qtr"])
                        elif f"{col}_qtr" in basic_df.columns:
                            basic_df[col] = basic_df[f"{col}_qtr"]
                            basic_df = basic_df.drop(columns=[f"{col}_qtr"])
        except Exception as e:
            print(f"Warning: Could not merge quarterly data: {e}")
    
    return basic_df
# CSV/JSON File Loading (Backward Compatibility)
# =============================================================================

def get_latest_data_file(pattern: str = "stocks_*.csv") -> Optional[str]:
    """Get the most recent stock data file matching pattern."""
    # Try CSV first, then JSON
    for ext in ["csv", "json"]:
        file_pattern = os.path.join(DATA_DIR, pattern.replace("*.csv", f"*.{ext}").replace("*.json", f"*.{ext}"))
        files = glob.glob(file_pattern)
        if files:
            return max(files, key=os.path.getmtime)
    return None


def load_stocks_data() -> pd.DataFrame:
    """
    Load stock data from the latest available data file.
    Merges basic data (per, pbr, eps, bps) with advanced data (roe, debt_ratio) if available.
    
    Returns:
        DataFrame with stock data, or empty DataFrame if no data found
    """
    # Load basic data file
    basic_file = get_latest_data_file("stocks_*.csv")
    
    if not basic_file or not os.path.exists(basic_file):
        return pd.DataFrame()
    
    if basic_file.endswith(".csv"):
        basic_df = pd.read_csv(basic_file, encoding="utf-8-sig")
    elif basic_file.endswith(".json"):
        basic_df = pd.read_json(basic_file, orient="records")
    else:
        return pd.DataFrame()
    
    # Ensure ticker column is string type with leading zeros preserved
    if 'ticker' in basic_df.columns:
        basic_df['ticker'] = basic_df['ticker'].astype(str).str.zfill(6)
    
    # Load advanced data file if available
    advanced_file = get_latest_data_file("stocks_advanced_*.csv")
    if advanced_file and os.path.exists(advanced_file) and advanced_file != basic_file:
        try:
            if advanced_file.endswith(".csv"):
                advanced_df = pd.read_csv(advanced_file, encoding="utf-8-sig")
            elif advanced_file.endswith(".json"):
                advanced_df = pd.read_json(advanced_file, orient="records")
            else:
                advanced_df = pd.DataFrame()
            
            # Ensure ticker column is string type
            if 'ticker' in advanced_df.columns:
                advanced_df['ticker'] = advanced_df['ticker'].astype(str).str.zfill(6)
            
            # Merge advanced data into basic data
            if not advanced_df.empty and 'ticker' in advanced_df.columns:
                # Columns to merge from advanced data
                merge_columns = ['roe', 'debt_ratio', 'forward_pe', 'eps_growth_yoy', 'sector']
                existing_cols = [col for col in merge_columns if col in advanced_df.columns]
                
                if existing_cols:
                    # Create merge subset
                    merge_df = advanced_df[['ticker'] + existing_cols].copy()
                    
                    # Merge on ticker
                    basic_df = basic_df.merge(merge_df, on='ticker', how='left', suffixes=('', '_adv'))
                    
                    # Use advanced values where basic is null
                    for col in existing_cols:
                        if col in basic_df.columns and f"{col}_adv" in basic_df.columns:
                            basic_df[col] = basic_df[col].fillna(basic_df[f"{col}_adv"])
                            basic_df = basic_df.drop(columns=[f"{col}_adv"])
                        elif f"{col}_adv" in basic_df.columns:
                            basic_df[col] = basic_df[f"{col}_adv"]
                            basic_df = basic_df.drop(columns=[f"{col}_adv"])
        except Exception as e:
            print(f"Warning: Could not merge advanced data: {e}")
    
    return basic_df


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
        # Handle price: use current_price if available, fall back to close
        price = row.get("current_price") if pd.notna(row.get("current_price")) else row.get("close")
        stock = {
            "ticker": str(row.get("ticker", "")),
            "name": str(row.get("name", "")),
            "current_price": float(price) if pd.notna(price) else 0.0,
            "change_rate": float(row.get("change_rate", 0)) if pd.notna(row.get("change_rate")) else 0.0,
            "per": float(row["per"]) if pd.notna(row.get("per")) else None,
            "pbr": float(row["pbr"]) if pd.notna(row.get("pbr")) else None,
            "market_cap": float(row["market_cap"]) if pd.notna(row.get("market_cap")) else None,
            "eps": float(row["eps"]) if pd.notna(row.get("eps")) else None,
            "bps": float(row["bps"]) if pd.notna(row.get("bps")) else None,
            "roe": float(row["roe"]) if pd.notna(row.get("roe")) else None,
            "debt_ratio": float(row["debt_ratio"]) if pd.notna(row.get("debt_ratio")) else None,
            "forward_pe": float(row["forward_pe"]) if pd.notna(row.get("forward_pe")) else None,
            "eps_growth_yoy": float(row["eps_growth_yoy"]) if pd.notna(row.get("eps_growth_yoy")) else None,
            "sector": str(row["sector"]) if pd.notna(row.get("sector")) else None,
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
    
    # Ensure ticker is formatted as 6-digit string
    ticker_str = str(ticker).zfill(6)
    
    # Find matching stock
    matches = df[df["ticker"].astype(str) == ticker_str]
    
    if matches.empty:
        return None
    
    row = matches.iloc[0]
    # Handle price: use current_price if available, fall back to close
    price = row.get("current_price") if pd.notna(row.get("current_price")) else row.get("close")
    return {
        "ticker": str(row.get("ticker", "")),
        "name": str(row.get("name", "")),
        "current_price": float(price) if pd.notna(price) else 0.0,
        "change_rate": float(row.get("change_rate", 0)) if pd.notna(row.get("change_rate")) else 0.0,
        "per": float(row["per"]) if pd.notna(row.get("per")) else None,
        "pbr": float(row["pbr"]) if pd.notna(row.get("pbr")) else None,
        "market_cap": float(row["market_cap"]) if pd.notna(row.get("market_cap")) else None,
        "eps": float(row["eps"]) if pd.notna(row.get("eps")) else None,
        "bps": float(row["bps"]) if pd.notna(row.get("bps")) else None,
        "roe": float(row["roe"]) if pd.notna(row.get("roe")) else None,
        "debt_ratio": float(row["debt_ratio"]) if pd.notna(row.get("debt_ratio")) else None,
        "forward_pe": float(row["forward_pe"]) if pd.notna(row.get("forward_pe")) else None,
        "eps_growth_yoy": float(row["eps_growth_yoy"]) if pd.notna(row.get("eps_growth_yoy")) else None,
        "sector": str(row["sector"]) if pd.notna(row.get("sector")) else None,
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
        # Handle price: use current_price if available, fall back to close
        price = row.get("current_price") if pd.notna(row.get("current_price")) else row.get("close")
        stock = {
            "ticker": str(row.get("ticker", "")),
            "name": str(row.get("name", "")),
            "current_price": float(price) if pd.notna(price) else 0.0,
            "change_rate": float(row.get("change_rate", 0)) if pd.notna(row.get("change_rate")) else 0.0,
        }
        result.append(stock)
    
    return result


# =============================================================================
# External API Data Fetching Functions
# =============================================================================

def get_naver_valuation(ticker: str) -> Optional[Dict[str, Any]]:
    """
    Fetch valuation metrics from Naver Finance.
    
    Fetches: PER, PBR, Forward PER, EPS, BPS, market_cap, dividend_yield
    
    Args:
        ticker: Stock ticker code (6-digit)
    
    Returns:
        Dictionary with valuation metrics, or None if fetch fails.
        Includes cached data if available and not expired.
    """
    ticker = str(ticker).zfill(6)
    
    # Check cache first
    cached = _get_cached_data(_valuation_cache, ticker, CACHE_TTL_DAILY)
    if cached is not None:
        return cached
    
    # Fetch fresh data
    try:
        quote = naver_crawler.get_stock_quote(ticker)
        if quote:
            result = {
                "ticker": ticker,
                "name": quote.get("name"),
                "current_price": quote.get("current_price"),
                "per": quote.get("per"),
                "pbr": quote.get("pbr"),
                "forward_per": quote.get("forward_per"),
                "eps": quote.get("eps"),
                "bps": quote.get("bps"),
                "market_cap": quote.get("market_cap"),
                "dividend_yield": quote.get("dividend_yield"),
                "source": "naver",
                "updated_at": quote.get("updated_at"),
            }
            _set_cached_data(_valuation_cache, ticker, result)
            return result
    except Exception as e:
        print(f"Error fetching Naver valuation for {ticker}: {e}")
    
    return None


def get_fdr_price_data(ticker: str) -> Optional[Dict[str, Any]]:
    """
    Fetch OHLCV price data from FinanceDataReader.
    
    Fetches: Open, High, Low, Close, Volume, Change
    
    Args:
        ticker: Stock ticker code (6-digit)
    
    Returns:
        Dictionary with latest price data, or None if fetch fails.
        Includes cached data if available and not expired.
    """
    ticker = str(ticker).zfill(6)
    
    # Check cache first
    cached = _get_cached_data(_price_cache, ticker, CACHE_TTL_DAILY)
    if cached is not None:
        return cached
    
    # Fetch fresh data
    try:
        price_data = fdr_client.get_latest_price(ticker)
        if price_data:
            result = {
                "ticker": ticker,
                "date": price_data.get("date"),
                "open": price_data.get("open"),
                "high": price_data.get("high"),
                "low": price_data.get("low"),
                "close": price_data.get("close"),
                "volume": price_data.get("volume"),
                "change": price_data.get("change"),
                "source": "fdr",
                "updated_at": datetime.now().isoformat(),
            }
            _set_cached_data(_price_cache, ticker, result)
            return result
    except Exception as e:
        print(f"Error fetching FDR price data for {ticker}: {e}")
    
    return None


def get_dart_fundamentals(ticker: str) -> Optional[Dict[str, Any]]:
    """
    Fetch quarterly fundamentals from DART API.
    
    Fetches: ROE, debt_ratio
    
    Requires DART_API_KEY environment variable to be set.
    
    Args:
        ticker: Stock ticker code (6-digit)
    
    Returns:
        Dictionary with fundamental metrics, or None if fetch fails.
        Includes cached data if available and not expired.
    """
    ticker = str(ticker).zfill(6)
    
    # Check cache first
    cached = _get_cached_data(_fundamentals_cache, ticker, CACHE_TTL_QUARTERLY)
    if cached is not None:
        return cached
    
    # Check for API key
    api_key = os.getenv("DART_API_KEY")
    if not api_key:
        print(f"DART_API_KEY not set, skipping fundamentals for {ticker}")
        return None
    
    # Fetch fresh data
    try:
        client = DartAPIClient(api_key=api_key)
        
        roe = client.calculate_roe(ticker)
        debt_ratio = client.calculate_debt_ratio(ticker)
        
        result = {
            "ticker": ticker,
            "roe": roe,
            "debt_ratio": debt_ratio,
            "source": "dart",
            "updated_at": datetime.now().isoformat(),
        }
        _set_cached_data(_fundamentals_cache, ticker, result)
        return result
    except ImportError:
        print(f"OpenDartReader not installed, skipping fundamentals for {ticker}")
        return None
    except Exception as e:
        print(f"Error fetching DART fundamentals for {ticker}: {e}")
    
    return None


# =============================================================================
# Unified Stock Data Function
# =============================================================================

def get_stock_data(ticker: str, use_cache: bool = True) -> Dict[str, Any]:
    """
    Get comprehensive stock data by merging all available sources.
    
    This function fetches data from multiple sources and merges them into
    a single unified response. Sources are queried in order of freshness needs:
    - Naver Finance: valuation metrics (PER, PBR, etc.)
    - FinanceDataReader: OHLCV price data
    - DART API: quarterly fundamentals (ROE, debt_ratio)
    
    Falls back to CSV/JSON file data if external APIs fail.
    
    Args:
        ticker: Stock ticker code (6-digit)
        use_cache: Whether to use cached data (default: True)
    
    Returns:
        Dictionary with comprehensive stock data from all sources.
        Includes 'data_source' field indicating where each value came from.
    """
    ticker = str(ticker).zfill(6)
    
    # Initialize result with all possible fields
    result: Dict[str, Any] = {
        "ticker": ticker,
        "name": None,
        "current_price": None,
        "change_rate": None,
        "per": None,
        "pbr": None,
        "forward_per": None,
        "eps": None,
        "bps": None,
        "market_cap": None,
        "dividend_yield": None,
        "roe": None,
        "debt_ratio": None,
        "open": None,
        "high": None,
        "low": None,
        "close": None,
        "volume": None,
        "sector": None,
        "source": "unknown",
    }
    
    data_sources: Dict[str, str] = {}
    
    # 1. Fetch from Naver Finance (valuation metrics)
    try:
        naver_data = None
        if use_cache:
            naver_data = _get_cached_data(_valuation_cache, ticker, CACHE_TTL_DAILY)
        if naver_data is None:
            naver_data = get_naver_valuation(ticker)
        
        if naver_data:
            for key in ["name", "current_price", "per", "pbr", "forward_per", 
                       "eps", "bps", "market_cap", "dividend_yield"]:
                if naver_data.get(key) is not None:
                    result[key] = naver_data[key]
                    data_sources[key] = "naver"
    except Exception as e:
        print(f"Warning: Naver data fetch failed for {ticker}: {e}")
    
    # 2. Fetch from FinanceDataReader (OHLCV)
    try:
        fdr_data = None
        if use_cache:
            fdr_data = _get_cached_data(_price_cache, ticker, CACHE_TTL_DAILY)
        if fdr_data is None:
            fdr_data = get_fdr_price_data(ticker)
        
        if fdr_data:
            for key in ["open", "high", "low", "close", "volume", "change"]:
                if fdr_data.get(key) is not None:
                    result[key] = fdr_data[key]
                    data_sources[key] = "fdr"
            # Use close price as current_price if not set
            if result.get("current_price") is None and fdr_data.get("close") is not None:
                result["current_price"] = fdr_data["close"]
                data_sources["current_price"] = "fdr"
    except Exception as e:
        print(f"Warning: FDR data fetch failed for {ticker}: {e}")
    
    # 3. Fetch from DART API (fundamentals)
    try:
        dart_data = None
        if use_cache:
            dart_data = _get_cached_data(_fundamentals_cache, ticker, CACHE_TTL_QUARTERLY)
        if dart_data is None:
            dart_data = get_dart_fundamentals(ticker)
        
        if dart_data:
            for key in ["roe", "debt_ratio"]:
                if dart_data.get(key) is not None:
                    result[key] = dart_data[key]
                    data_sources[key] = "dart"
    except Exception as e:
        print(f"Warning: DART data fetch failed for {ticker}: {e}")
    
    # 4. Fallback to CSV/JSON data if external APIs returned nothing useful
    if all(v is None for v in [result.get("current_price"), result.get("per"), result.get("name")]):
        try:
            file_data = get_stock_by_ticker(ticker)
            if file_data:
                for key, value in file_data.items():
                    if value is not None and result.get(key) is None:
                        result[key] = value
                        data_sources[key] = "file"
        except Exception as e:
            print(f"Warning: File data fallback failed for {ticker}: {e}")
    
    # Set source tracking
    result["_data_sources"] = data_sources
    
    return result


def get_stock_chart_data(ticker: str, days: int = 30) -> List[Dict[str, Any]]:
    """
    Get historical chart data for a stock.
    
    Args:
        ticker: Stock ticker code (6-digit)
        days: Number of days of history to fetch (default: 30)
    
    Returns:
        List of dictionaries with OHLCV data, or empty list if fetch fails.
    """
    ticker = str(ticker).zfill(6)
    
    try:
        return fdr_client.get_chart_data(ticker, days)
    except Exception as e:
        print(f"Error fetching chart data for {ticker}: {e}")
        return []


def clear_cache(ticker: Optional[str] = None) -> None:
    """
    Clear cached data for a specific ticker or all tickers.
    
    Args:
        ticker: Optional ticker to clear cache for. If None, clears all cache.
    """
    global _valuation_cache, _price_cache, _fundamentals_cache
    
    if ticker:
        ticker = str(ticker).zfill(6)
        _valuation_cache.pop(ticker, None)
        _price_cache.pop(ticker, None)
        _fundamentals_cache.pop(ticker, None)
    else:
        _valuation_cache.clear()
        _price_cache.clear()
        _fundamentals_cache.clear()


def get_cache_status() -> Dict[str, Any]:
    """
    Get current cache status information.
    
    Returns:
        Dictionary with cache statistics.
    """
    return {
        "valuation_cache": {
            "count": len(_valuation_cache),
            "ttl_seconds": CACHE_TTL_DAILY,
        },
        "price_cache": {
            "count": len(_price_cache),
            "ttl_seconds": CACHE_TTL_DAILY,
        },
        "fundamentals_cache": {
            "count": len(_fundamentals_cache),
            "ttl_seconds": CACHE_TTL_QUARTERLY,
        },
    }
