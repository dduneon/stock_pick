"""
Stock Data Loader
=================

Loads stock data from:
- CSV/JSON files (backward compatibility)
- Naver Finance (all data: valuation, financials, OHLCV)

Provides unified get_stock_data(ticker) function with caching.
"""

import os
import glob
import time
from typing import List, Optional, Dict, Any
from datetime import datetime

import pandas as pd

DATA_DIR = os.environ.get("DATA_DIR", os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))), "data"))
DAILY_DATA_DIR = os.path.join(DATA_DIR, "daily")
QUARTERLY_DATA_DIR = os.path.join(DATA_DIR, "quarterly")

CACHE_TTL_DAILY = int(os.environ.get("CACHE_TTL_DAILY", 3600))
CACHE_TTL_QUARTERLY = int(os.environ.get("CACHE_TTL_QUARTERLY", 86400 * 90))

from app.services import naver_crawler

_valuation_cache: Dict[str, Dict[str, Any]] = {}
_price_cache: Dict[str, Dict[str, Any]] = {}
_fundamentals_cache: Dict[str, Dict[str, Any]] = {}


def _get_cached_data(cache: Dict[str, Dict[str, Any]], ticker: str, ttl: int) -> Optional[Dict[str, Any]]:
    if ticker in cache:
        cached = cache[ticker]
        if time.time() - cached["timestamp"] < ttl:
            return cached["data"]
    return None


def _set_cached_data(cache: Dict[str, Dict[str, Any]], ticker: str, data: Dict[str, Any]) -> None:
    cache[ticker] = {"data": data, "timestamp": time.time()}


def get_latest_data_file(pattern: str = "stocks_*.csv", use_new_structure: bool = True) -> Optional[str]:
    search_dirs = []
    
    if use_new_structure:
        if "fundamentals" in pattern:
            search_dirs = [QUARTERLY_DATA_DIR, DATA_DIR]
        elif "stocks_advanced" in pattern:
            search_dirs = [DATA_DIR]
        else:
            search_dirs = [DAILY_DATA_DIR, DATA_DIR]
    else:
        search_dirs = [DATA_DIR]
    
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
    daily_file = get_latest_data_file("stocks_*.csv", use_new_structure=True)
    quarterly_file = get_latest_data_file("fundamentals_*.csv", use_new_structure=True)
    
    if not daily_file:
        daily_file = get_latest_data_file("stocks_*.csv", use_new_structure=False)
        quarterly_file = get_latest_data_file("stocks_advanced_*.csv", use_new_structure=False)
    
    if not daily_file or not os.path.exists(daily_file):
        return pd.DataFrame()
    
    if daily_file.endswith(".csv"):
        basic_df = pd.read_csv(daily_file, encoding="utf-8-sig")
    elif daily_file.endswith(".json"):
        basic_df = pd.read_json(daily_file, orient="records")
    else:
        return pd.DataFrame()
    
    if 'ticker' in basic_df.columns:
        basic_df['ticker'] = basic_df['ticker'].astype(str).str.zfill(6)
    
    if quarterly_file and os.path.exists(quarterly_file) and quarterly_file != daily_file:
        try:
            if quarterly_file.endswith(".csv"):
                quarterly_df = pd.read_csv(quarterly_file, encoding="utf-8-sig")
            elif quarterly_file.endswith(".json"):
                quarterly_df = pd.read_json(quarterly_file, orient="records")
            else:
                quarterly_df = pd.DataFrame()
            
            if 'ticker' in quarterly_df.columns:
                quarterly_df['ticker'] = quarterly_df['ticker'].astype(str).str.zfill(6)
            
            if not quarterly_df.empty and 'ticker' in quarterly_df.columns:
                merge_columns = ['roe', 'debt_ratio', 'forward_pe', 'eps_growth_yoy', 'sector',
                                 'revenue', 'operating_profit', 'net_profit', 'operating_margin',
                                 'net_margin', 'current_ratio', 'reserve_ratio',
                                 'dividend_per_share', 'dividend_yield', 'dividend_payout_ratio',
                                 'fiscal_year']
                existing_cols = [col for col in merge_columns if col in quarterly_df.columns]
                
                if existing_cols:
                    merge_df = quarterly_df[['ticker'] + existing_cols].copy()
                    basic_df = basic_df.merge(merge_df, on='ticker', how='left', suffixes=('', '_qtr'))
                    
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


def get_all_stocks(limit: Optional[int] = None) -> List[Dict[str, Any]]:
    df = load_stocks_data()
    
    if df.empty:
        return []
    
    result = []
    for _, row in df.iterrows():
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
            "fiscal_year": str(row["fiscal_year"]) if pd.notna(row.get("fiscal_year")) else None,
            "dividend_payout_ratio": float(row["dividend_payout_ratio"]) if pd.notna(row.get("dividend_payout_ratio")) else None,
            "dividend_yield": float(row["dividend_yield"]) if pd.notna(row.get("dividend_yield")) else None,
            "dividend_per_share": float(row["dividend_per_share"]) if pd.notna(row.get("dividend_per_share")) else None,
            "reserve_ratio": float(row["reserve_ratio"]) if pd.notna(row.get("reserve_ratio")) else None,
            "current_ratio": float(row["current_ratio"]) if pd.notna(row.get("current_ratio")) else None,
            "net_margin": float(row["net_margin"]) if pd.notna(row.get("net_margin")) else None,
            "operating_margin": float(row["operating_margin"]) if pd.notna(row.get("operating_margin")) else None,
            "net_profit": float(row["net_profit"]) if pd.notna(row.get("net_profit")) else None,
            "operating_profit": float(row["operating_profit"]) if pd.notna(row.get("operating_profit")) else None,
            "revenue": float(row["revenue"]) if pd.notna(row.get("revenue")) else None,
        }
        result.append(stock)
    
    if limit:
        result = result[:limit]
    
    return result


def get_stock_by_ticker(ticker: str) -> Optional[Dict[str, Any]]:
    df = load_stocks_data()
    
    if df.empty:
        return None
    
    ticker_str = str(ticker).zfill(6)
    matches = df[df["ticker"].astype(str) == ticker_str]
    
    if matches.empty:
        return None
    
    row = matches.iloc[0]
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
        "revenue": float(row["revenue"]) if pd.notna(row.get("revenue")) else None,
        "operating_profit": float(row["operating_profit"]) if pd.notna(row.get("operating_profit")) else None,
        "net_profit": float(row["net_profit"]) if pd.notna(row.get("net_profit")) else None,
        "operating_margin": float(row["operating_margin"]) if pd.notna(row.get("operating_margin")) else None,
        "net_margin": float(row["net_margin"]) if pd.notna(row.get("net_margin")) else None,
        "current_ratio": float(row["current_ratio"]) if pd.notna(row.get("current_ratio")) else None,
        "reserve_ratio": float(row["reserve_ratio"]) if pd.notna(row.get("reserve_ratio")) else None,
        "dividend_per_share": float(row["dividend_per_share"]) if pd.notna(row.get("dividend_per_share")) else None,
        "dividend_yield": float(row["dividend_yield"]) if pd.notna(row.get("dividend_yield")) else None,
        "dividend_payout_ratio": float(row["dividend_payout_ratio"]) if pd.notna(row.get("dividend_payout_ratio")) else None,
        "fiscal_year": str(row["fiscal_year"]) if pd.notna(row.get("fiscal_year")) else None,
        "open": float(row["open"]) if pd.notna(row.get("open")) else None,
        "high": float(row["high"]) if pd.notna(row.get("high")) else None,
        "low": float(row["low"]) if pd.notna(row.get("low")) else None,
        "volume": int(row["volume"]) if pd.notna(row.get("volume")) else None,
    }



def search_stocks(query: str) -> List[Dict[str, Any]]:
    df = load_stocks_data()
    
    if df.empty:
        return []
    
    query_lower = query.lower()
    matches = df[df["name"].astype(str).str.lower().str.contains(query_lower, na=False)]
    
    result = []
    for _, row in matches.iterrows():
        price = row.get("current_price") if pd.notna(row.get("current_price")) else row.get("close")
        stock = {
            "ticker": str(row.get("ticker", "")),
            "name": str(row.get("name", "")),
            "current_price": float(price) if pd.notna(price) else 0.0,
            "change_rate": float(row.get("change_rate", 0)) if pd.notna(row.get("change_rate")) else 0.0,
        }
        result.append(stock)
    
    return result


def get_naver_valuation(ticker: str) -> Optional[Dict[str, Any]]:
    ticker = str(ticker).zfill(6)
    
    cached = _get_cached_data(_valuation_cache, ticker, CACHE_TTL_DAILY)
    if cached is not None:
        return cached
    
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


def get_stock_data(ticker: str, use_cache: bool = True) -> Dict[str, Any]:
    ticker = str(ticker).zfill(6)
    
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
        "roe_year": None,
        "debt_ratio": None,
        "debt_ratio_year": None,
        "eps_growth_yoy": None,
        "open": None,
        "high": None,
        "low": None,
        "close": None,
        "volume": None,
        "source": "unknown",
    }
    
    data_sources: Dict[str, str] = {}
    
    try:
        naver_data = None
        if use_cache:
            naver_data = _get_cached_data(_valuation_cache, ticker, CACHE_TTL_DAILY)
        if naver_data is None:
            naver_data = naver_crawler.get_stock_quote(ticker)
        
        if naver_data:
            for key in ["name", "current_price", "per", "pbr", "forward_per", 
                       "eps", "bps", "market_cap", "dividend_yield"]:
                if naver_data.get(key) is not None:
                    result[key] = naver_data[key]
                    data_sources[key] = "naver"
            
            for key in ["roe", "roe_year", "debt_ratio", "debt_ratio_year", "eps_growth_yoy"]:
                if naver_data.get(key) is not None:
                    result[key] = naver_data[key]
                    data_sources[key] = "naver"
            
            for key in ["open", "high", "low", "close", "volume"]:
                if naver_data.get(key) is not None:
                    result[key] = naver_data[key]
                    data_sources[key] = "naver"
            
            if result.get("current_price") is None and naver_data.get("close") is not None:
                result["current_price"] = naver_data["close"]
                data_sources["current_price"] = "naver"
    except Exception as e:
        print(f"Warning: Naver data fetch failed for {ticker}: {e}")
    
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
    
    result["_data_sources"] = data_sources
    
    return result


def get_stock_chart_data(ticker: str, days: int = 30) -> List[Dict[str, Any]]:
    ticker = str(ticker).zfill(6)
    
    try:
        ohlcv = naver_crawler.get_ohlcv_naver(ticker, days)
        if ohlcv:
            return [ohlcv]
    except Exception as e:
        print(f"Error fetching chart data for {ticker}: {e}")
    
    return []


def clear_cache(ticker: Optional[str] = None) -> None:
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
