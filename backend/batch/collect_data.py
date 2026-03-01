import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

"""
KOSPI Stock Data Collection Script using Naver Finance
=======================================================

This module collects KOSPI stock data from Naver Finance:
- Current Price, PER, PBR, Forward PER
- EPS, BPS, Market Capitalization, Dividend Yield
- ROE, Debt Ratio, EPS Growth YoY (from 기업실적분석)
- OHLCV (from historical data page)

Usage:
    python -m backend.batch.collect_data
    
    # Test mode (10 stocks)
    python -m backend.batch.collect_data --test
    
    # Limit to N stocks
    python -m backend.batch.collect_data --limit 50
"""

import os
import time
import random
import argparse
from datetime import datetime
from typing import Optional, List, Dict, Any

import pandas as pd
import requests
from bs4 import BeautifulSoup

from app.services import naver_crawler

MIN_DELAY = 1.0
MAX_DELAY = 2.0


def get_naver_ticker_list(limit: Optional[int] = None) -> List[str]:
    return naver_crawler.get_all_tickers(limit=limit)


def collect_kospi_data(
    limit: Optional[int] = None,
    test_mode: bool = False
) -> pd.DataFrame:
    print(f"Collecting KOSPI data from Naver Finance...")
    
    tickers = get_naver_ticker_list(limit=limit)
    
    if test_mode:
        limit = 10
        tickers = tickers[:limit]
        print(f"Test mode: limiting to {limit} stocks")
    elif limit:
        tickers = tickers[:limit]
        print(f"Limited to {limit} stocks")
    
    print(f"Processing {len(tickers)} stocks...")
    
    all_data = []
    
    for i, ticker in enumerate(tickers):
        try:
            if i > 0:
                delay = random.uniform(MIN_DELAY, MAX_DELAY)
                time.sleep(delay)
            
            quote = naver_crawler.get_stock_quote(ticker)
            
            if not quote:
                print(f"  Warning: No data for {ticker}")
                continue
            
            row = {
                'ticker': quote.get('ticker'),
                'name': quote.get('name'),
                'date': datetime.now().strftime("%Y-%m-%d"),
                'current_price': quote.get('current_price'),
                'per': quote.get('per'),
                'pbr': quote.get('pbr'),
                'forward_pe': quote.get('forward_per'),
                'eps': quote.get('eps'),
                'bps': quote.get('bps'),
                'market_cap': quote.get('market_cap'),
                'dividend_yield': quote.get('dividend_yield'),
                'roe': quote.get('roe'),
                'roe_year': quote.get('roe_year'),
                'debt_ratio': quote.get('debt_ratio'),
                'debt_ratio_year': quote.get('debt_ratio_year'),
                'eps_growth_yoy': quote.get('eps_growth_yoy'),
                'open': quote.get('open'),
                'high': quote.get('high'),
                'low': quote.get('low'),
                'close': quote.get('close'),
                'volume': quote.get('volume'),
                # New comprehensive financial metrics (Wave 3)
                'revenue': quote.get('revenue'),
                'operating_profit': quote.get('operating_profit'),
                'net_profit': quote.get('net_profit'),
                'operating_margin': quote.get('operating_margin'),
                'net_margin': quote.get('net_margin'),
                'current_ratio': quote.get('current_ratio'),
                'reserve_ratio': quote.get('reserve_ratio'),
                'dividend_per_share': quote.get('dividend_per_share'),
                'dividend_payout_ratio': quote.get('dividend_payout_ratio'),
                'fiscal_year': quote.get('fiscal_year'),
            }
            
            all_data.append(row)
            
            if (i + 1) % 50 == 0:
                print(f"  Processed {i + 1}/{len(tickers)} stocks...")
                
        except Exception as e:
            print(f"  Error processing {ticker}: {e}")
            continue
    
    df = pd.DataFrame(all_data)
    
    print(f"Successfully collected {len(df)} stocks")
    
    return df


def save_to_csv(df: pd.DataFrame, output_dir: str = "data") -> str:
    date_str = datetime.now().strftime("%Y%m%d")
    
    os.makedirs(output_dir, exist_ok=True)
    
    filename = f"stocks_{date_str}.csv"
    filepath = os.path.join(output_dir, filename)
    
    df.to_csv(filepath, index=False, encoding='utf-8-sig')
    
    print(f"Saved to {filepath}")
    
    return filepath


def save_to_json(df: pd.DataFrame, output_dir: str = "data") -> str:
    date_str = datetime.now().strftime("%Y%m%d")
    
    os.makedirs(output_dir, exist_ok=True)
    
    filename = f"stocks_{date_str}.json"
    filepath = os.path.join(output_dir, filename)
    
    df.to_json(filepath, orient='records', force_ascii=False, indent=2)
    
    print(f"Saved to {filepath}")
    
    return filepath


def main():
    parser = argparse.ArgumentParser(description='Collect KOSPI stock data from Naver Finance')
    parser.add_argument('--limit', type=int, default=None, help='Limit number of stocks to collect')
    parser.add_argument('--test', action='store_true', help='Test mode: collect 10 stocks')
    parser.add_argument('--output', type=str, default='data', help='Output directory')
    
    args = parser.parse_args()
    
    test_mode = args.test
    limit = args.limit
    
    df = collect_kospi_data(limit=limit, test_mode=test_mode)
    
    if not df.empty:
        save_to_csv(df, args.output)
        save_to_json(df, args.output)
        
        print("\nData collection completed!")
        print(f"Total stocks: {len(df)}")
        print("\nSample data:")
        print(df.head())
        
        print("\nData summary:")
        print(f"  Fields: {list(df.columns)}")
        print(f"  Non-null counts:")
        for col in df.columns:
            non_null = df[col].notna().sum()
            print(f"    {col}: {non_null}/{len(df)}")
    else:
        print("No data collected")


if __name__ == "__main__":
    main()
