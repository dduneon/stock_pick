"""
Naver Finance crawler for extracting stock valuation data.

Crawls Naver Finance to extract PER, PBR, Forward PER, EPS, BPS, 
시가총액, 배당수익률, ROE, 부채비율, EPS growth and 현재가 for Korean stocks.

Usage:
    from app.services.naver_crawler import get_stock_quote
    
    quote = get_stock_quote('005930')
    print(quote['per'], quote['pbr'], quote['current_price'])
"""

import time
import random
import re
from typing import Optional, Dict, Any, List
from datetime import datetime

import requests
import pandas as pd
from bs4 import BeautifulSoup


USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:121.0) Gecko/20100101 Firefox/121.0",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.1 Safari/605.1.15",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
]

MIN_DELAY = 1.0
MAX_DELAY = 2.0


def _get_headers() -> Dict[str, str]:
    return {
        "User-Agent": random.choice(USER_AGENTS),
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
        "Accept-Language": "ko-KR,ko;q=0.9,en-US;q=0.8,en;q=0.7",
        "Accept-Encoding": "gzip, deflate, br",
        "Connection": "keep-alive",
        "Upgrade-Insecure-Requests": "1",
    }


def _rate_limit():
    delay = random.uniform(MIN_DELAY, MAX_DELAY)
    time.sleep(delay)


def _parse_number(text: Optional[str]) -> Optional[float]:
    if not text:
        return None
    cleaned = re.sub(r'[^\d.\-]', '', text.replace(',', ''))
    try:
        return float(cleaned) if '.' in cleaned else float(cleaned)
    except (ValueError, TypeError):
        return None


def _parse_market_cap(text: Optional[str]) -> Optional[float]:
    if not text:
        return None
    text = text.strip().replace(',', '')
    亿_match = re.search(r'([\d.]+)\s*억', text)
    if 亿_match:
        return float(亿_match.group(1)) * 1e8
    조_match = re.search(r'([\d.]+)\s*조', text)
    if 조_match:
        return float(조_match.group(1)) * 1e12
    만원_match = re.search(r'([\d,]+)\s*만원', text)
    if 만원_match:
        return float(만원_match.group(1).replace(',', '')) * 10000
    return _parse_number(text)


def _get_financial_data(ticker: str) -> Dict[str, Optional[float]]:
    """
    Extract financial data from Naver Finance main page "기업실적분석" section.
    
    Returns:
        Dict with 'roe', 'debt_ratio', 'eps_growth_yoy' keys
    """
    result = {
        'roe': None,
        'debt_ratio': None,
        'eps_growth_yoy': None,
    }
    
    # Naver Finance main page has annual financial data
    url = f"https://finance.naver.com/item/main.naver?code={ticker}"
    
    try:
        _rate_limit()
        
        response = requests.get(url, headers=_get_headers(), timeout=10)
        response.raise_for_status()
        response.encoding = 'euc-kr'
        
        # Parse tables - look for annual financial data table with year columns
        tables = pd.read_html(response.text, encoding='euc-kr')
        
        # Find the table with annual financial data (has year columns like '2024.12')
        for df in tables:
            if df.shape[0] > 10 and df.shape[1] > 3:
                # Check if this table has year columns (look for pattern like 2024.12)
                # Columns are multi-index: (section, year, standard)
                has_year_cols = False
                for col in df.columns[:6]:
                    col_str = str(col)
                    if '202' in col_str and ('12' in col_str or '09' in col_str):
                        has_year_cols = True
                        break
                
                if has_year_cols:
                    # Table structure:
                    # Row 5: ROE (index 5)
                    # Row 6: 부채비율 (index 6) 
                    # Row 9: EPS (index 9)
                    # Column indices: 0=metric name, 1=2022.12, 2=2023.12, 3=2024.12, 4=2025.12(E), 5=2024.09
                    
                    # Get ROE - row index 5
                    # Try column 4 first (2025.12E forecast), then column 3 (2024.12), then column 2 (2023.12)
                    if df.shape[0] > 5:
                        # Try column 4 (2025.12E - forecast)
                        if df.shape[1] > 4:
                            roe_val = df.iloc[5, 4]
                            if pd.notna(roe_val):
                                result['roe'] = float(roe_val)
                        # Try column 3 (2024.12 - most recent complete year)
                        if result['roe'] is None and df.shape[1] > 3:
                            roe_val = df.iloc[5, 3]
                            if pd.notna(roe_val):
                                result['roe'] = float(roe_val)
                        # Try column 2 (2023.12)
                        if result['roe'] is None and df.shape[1] > 2:
                            roe_val = df.iloc[5, 2]
                            if pd.notna(roe_val):
                                result['roe'] = float(roe_val)
                    
                    # Get debt ratio - row index 6
                    # Try column 4 first (2025.12E), then column 3 (2024.12), then column 2 (2023.12)
                    if df.shape[0] > 6:
                        if df.shape[1] > 4:
                            debt_val = df.iloc[6, 4]
                            if pd.notna(debt_val):
                                result['debt_ratio'] = float(debt_val)
                        if result['debt_ratio'] is None and df.shape[1] > 3:
                            debt_val = df.iloc[6, 3]
                            if pd.notna(debt_val):
                                result['debt_ratio'] = float(debt_val)
                        if result['debt_ratio'] is None and df.shape[1] > 2:
                            debt_val = df.iloc[6, 2]
                            if pd.notna(debt_val):
                                result['debt_ratio'] = float(debt_val)
                    
                    # Get EPS for YoY calculation - row index 9
                    # Calculate from most recent annual (col 4 or 3) vs previous year (col 3 or 2)
                    if df.shape[0] > 9 and df.shape[1] > 4:
                        eps_current = df.iloc[9, 4]  # 2025.12E or use col 3 for 2024.12
                        eps_prev = df.iloc[9, 3]     # 2024.12
                        
                        if pd.notna(eps_current) and pd.notna(eps_prev):
                            eps_current = float(eps_current)
                            eps_prev = float(eps_prev)
                            if eps_prev != 0:
                                result['eps_growth_yoy'] = round(((eps_current - eps_prev) / abs(eps_prev)) * 100, 2)
                        # Fallback: use 2024.12 vs 2023.12
                        elif df.shape[1] > 3:
                            eps_current = df.iloc[9, 3]  # 2024.12
                            eps_prev = df.iloc[9, 2]     # 2023.12
                            if pd.notna(eps_current) and pd.notna(eps_prev):
                                eps_current = float(eps_current)
                                eps_prev = float(eps_prev)
                                if eps_prev != 0:
                                    result['eps_growth_yoy'] = round(((eps_current - eps_prev) / abs(eps_prev)) * 100, 2)
                    
                    # If we found data, break
                    if result['roe'] is not None or result['debt_ratio'] is not None:
                        break
        
    except Exception as e:
        print(f"Error fetching financial data for {ticker}: {e}")
    
    return result


def get_stock_quote(ticker: str) -> Optional[Dict[str, Any]]:
    ticker = str(ticker).zfill(6)
    url = f"https://finance.naver.com/item/main.naver?code={ticker}"
    
    try:
        _rate_limit()
        
        response = requests.get(url, headers=_get_headers(), timeout=10)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.text, 'html.parser')
        
        name = None
        # Naver Finance uses .h_company h2 for company name
        name_elem = soup.select_one('.h_company h2')
        if name_elem:
            name = name_elem.get_text(strip=True)
        
        if not name:
            name_elem = soup.select_one('.company_info a')
            if name_elem:
                name = name_elem.get_text(strip=True)
        
        if not name:
            name_elem = soup.select_one('h2.company_name')
            if name_elem:
                name = name_elem.get_text(strip=True)
        
        current_price = None
        # Naver Finance uses .no_today .blind for current price
        price_elem = soup.select_one('.no_today .blind')
        if price_elem:
            price_text = price_elem.get_text(strip=True)
            price_text = price_text.replace('포인트', '').strip()
            current_price = _parse_number(price_text)
        
        if not current_price:
            price_elem = soup.select_one('.new_total .blind')
            if price_elem:
                price_text = price_elem.get_text(strip=True)
                price_text = price_text.replace('포인트', '').strip()
                current_price = _parse_number(price_text)
        
        if not current_price:
            price_elem = soup.select_one('.price .blind')
            if price_elem:
                current_price = _parse_number(price_elem.get_text())
        
        per = None
        per_elem = soup.select_one('#_per')
        if per_elem:
            per_text = per_elem.get_text(strip=True)
            per = _parse_number(per_text)
        
        pbr = None
        pbr_elem = soup.select_one('#_pbr')
        if pbr_elem:
            pbr_text = pbr_elem.get_text(strip=True)
            pbr = _parse_number(pbr_text)
        
        forward_per = None
        forward_per_elem = soup.select_one('#_cns_per')
        if forward_per_elem:
            forward_per_text = forward_per_elem.get_text(strip=True)
            forward_per = _parse_number(forward_per_text)
        
        eps = None
        eps_elem = soup.select_one('#_eps')
        if eps_elem:
            eps_text = eps_elem.get_text(strip=True)
            eps = _parse_number(eps_text)
        
        bps = None
        # Try to get BPS from element
        bps_elem = soup.select_one('#_bps')
        if bps_elem:
            bps_text = bps_elem.get_text(strip=True)
            bps = _parse_number(bps_text)
        
        # Fallback: Extract BPS from per_table if available
        if not bps:
            per_table = soup.select_one('table.per_table')
            if per_table:
                # Find the row containing PBR/BPS (usually 3rd row with index 2)
                rows = per_table.select('tr')
                if len(rows) >= 3:
                    cells = rows[2].select('td')
                    if len(cells) >= 1:
                        cell_text = cells[0].get_text(separator=' ', strip=True)
                        # Format: "7.33 배 l 144,811 원"
                        parts = cell_text.split('l')
                        if len(parts) >= 2:
                            bps_text = parts[1].replace('원', '').strip()
                            bps = _parse_number(bps_text)
        
        # Final fallback: Calculate BPS from PBR and current price
        if not bps and pbr and pbr != 0 and current_price:
            bps = current_price / pbr
        
        market_cap = None
        market_cap_elem = soup.select_one('#_market_sum')
        if market_cap_elem:
            market_cap_text = market_cap_elem.get_text(strip=True)
            market_cap = _parse_market_cap(market_cap_text)
        
        dividend_yield = None
        dividend_elem = soup.select_one('#_dvr')
        if dividend_elem:
            dividend_text = dividend_elem.get_text(strip=True)
            dividend_text = dividend_text.replace('%', '').strip()
            dividend_yield = _parse_number(dividend_text)
        
        # Get additional financial data from 기업실적분석
        financial_data = _get_financial_data(ticker)
        
        result = {
            'ticker': ticker,
            'name': name,
            'current_price': current_price,
            'per': per,
            'pbr': pbr,
            'forward_per': forward_per,
            'eps': eps,
            'bps': bps,
            'market_cap': market_cap,
            'dividend_yield': dividend_yield,
            'roe': financial_data.get('roe'),
            'debt_ratio': financial_data.get('debt_ratio'),
            'eps_growth_yoy': financial_data.get('eps_growth_yoy'),
            'updated_at': datetime.now().isoformat(),
        }
        
        return result
        
    except requests.RequestException as e:
        print(f"Error fetching quote for {ticker}: {e}")
        return None
    except Exception as e:
        print(f"Error parsing quote for {ticker}: {e}")
        return None


def get_multiple_quotes(tickers: List[str]) -> List[Dict[str, Any]]:
    results = []
    for ticker in tickers:
        quote = get_stock_quote(ticker)
        results.append(quote)
    return results


def get_kospi_tickers() -> List[str]:
    return [
        "005930",
        "000660",
        "035420",
        "051910",
        "005380",
        "005490",
        "068270",
        "035720",
        "012330",
        "000270",
        "096770",
        "066570",
        "105560",
        "055550",
        "086790",
        "032830",
        "032750",
        "138040",
        "003670",
        "004020",
    ]
