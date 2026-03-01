import time
import random
import re
from typing import Optional, Dict, Any, List, Tuple
from datetime import datetime

import requests
import pandas as pd
import numpy as np
from bs4 import BeautifulSoup


USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:121.0) Gecko/20100101 Firefox/121.0",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.1 Safari/605.1.15",
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


def _get_all_tickers() -> List[str]:
    url = "https://finance.naver.com/sise/sitemap_xml.naver"
    tickers = []
    
    try:
        _rate_limit()
        response = requests.get(url, headers=_get_headers(), timeout=15)
        response.raise_for_status()
        response.encoding = 'euc-kr'
        
        soup = BeautifulSoup(response.text, 'xml')
        stock_items = soup.find_all('stockitem')
        
        for item in stock_items:
            ticker_elem = item.find('symbol')
            if ticker_elem and ticker_elem.text:
                ticker = ticker_elem.text.strip()
                if len(ticker) == 6 and ticker.isdigit():
                    tickers.append(ticker)
    except Exception as e:
        print(f"Sitemap fetch failed: {e}")
    
    if not tickers:
        try:
            _rate_limit()
            url = "https://finance.naver.com/sise/"
            response = requests.get(url, headers=_get_headers(), timeout=15)
            response.raise_for_status()
            response.encoding = 'euc-kr'
            
            soup = BeautifulSoup(response.text, 'html.parser')
            stock_links = soup.select('a.tltle')
            
            for link in stock_links:
                href = link.get('href', '')
                if 'code=' in href:
                    ticker = href.split('code=')[1].strip()
                    if len(ticker) == 6 and ticker.isdigit() and ticker not in tickers:
                        tickers.append(ticker)
        except Exception as e:
            print(f"Main page fetch failed: {e}")
    
    if not tickers:
        tickers = _get_popular_tickers()
    
    print(f"Found {len(tickers)} KOSPI stocks from Naver Finance")
    return tickers


def _get_popular_tickers() -> List[str]:
    return [
        "005930", "000660", "035420", "051910", "005380", "005490", "068270",
        "035720", "012330", "000270", "096770", "066570", "105560", "055550",
        "086790", "032830", "032750", "138040", "003670", "004020", "207940",
        "028260", "034730", "018260", "251270", "000070", "006400", "030200",
        "057050", "095570", "017670", "021240", "058470", "036570", "026960",
    ]


_ticker_cache: Optional[List[str]] = None
_ticker_cache_time: Optional[float] = None
TICKER_CACHE_TTL = 3600


def get_all_tickers(limit: Optional[int] = None, use_cache: bool = True) -> List[str]:
    global _ticker_cache, _ticker_cache_time
    
    current_time = time.time()
    
    if use_cache and _ticker_cache is not None:
        if _ticker_cache_time and (current_time - _ticker_cache_time) < TICKER_CACHE_TTL:
            tickers = _ticker_cache
        else:
            tickers = _get_all_tickers()
            _ticker_cache = tickers
            _ticker_cache_time = current_time
    else:
        tickers = _get_all_tickers()
        _ticker_cache = tickers
        _ticker_cache_time = current_time
    
    if limit and limit > 0:
        return tickers[:limit]
    
    return tickers


def _get_latest_valid_data(series: pd.Series) -> Tuple[Optional[float], Optional[str]]:
    """Get the latest non-null value from a series."""
    cleaned = pd.to_numeric(series.replace('-', np.nan), errors='coerce').dropna()
    if not cleaned.empty:
        return cleaned.iloc[-1], str(cleaned.index[-1])
    return None, None


def _find_row(df: pd.DataFrame, keyword: str) -> Optional[pd.Series]:
    """Find a row by keyword (partial match)."""
    for idx in df.index:
        if keyword in str(idx):
            return df.loc[idx]
    return None


def _parse_numeric(value: Any) -> Optional[float]:
    """Parse numeric value, handling Korean formats."""
    if pd.isna(value) or value == '-' or value == '':
        return None
    if isinstance(value, (int, float)):
        return float(value)
    # Handle comma separators and em tags
    cleaned = str(value).replace(',', '').replace('<em class="f_up">', '').replace('</em>', '').strip()
    try:
        return float(cleaned)
    except (ValueError, TypeError):
        return None


def _get_empty_financial_data() -> Dict[str, Any]:
    """Return empty financial data structure."""
    return {
        'revenue': None,
        'operating_profit': None,
        'net_profit': None,
        'operating_margin': None,
        'net_margin': None,
        'roe': None,
        'debt_ratio': None,
        'current_ratio': None,
        'reserve_ratio': None,
        'eps': None,
        'bps': None,
        'per': None,
        'pbr': None,
        'dividend_per_share': None,
        'dividend_yield': None,
        'dividend_payout_ratio': None,
        'eps_growth_yoy': None,
        'fiscal_year': None,
    }


def _extract_metric(annual_df: pd.DataFrame, keywords: List[str]) -> Optional[float]:
    """Extract a single metric by trying multiple keywords."""
    for keyword in keywords:
        row = _find_row(annual_df, keyword)
        if row is not None:
            value, _ = _get_latest_valid_data(row)
            return value
    return None


def _extract_all_metrics(annual_df: pd.DataFrame) -> Dict[str, Any]:
    """Extract all financial metrics from the annual data."""
    result = {
        # Profitability
        'revenue': _extract_metric(annual_df, ['매출액']),
        'operating_profit': _extract_metric(annual_df, ['영업이익']),
        'net_profit': _extract_metric(annual_df, ['당기순이익']),
        'operating_margin': _extract_metric(annual_df, ['영업이익률']),
        'net_margin': _extract_metric(annual_df, ['순이익률']),
        'roe': _extract_metric(annual_df, ['ROE', 'ROE(지배주주)']),
        
        # Balance Sheet
        'debt_ratio': _extract_metric(annual_df, ['부채비율']),
        'current_ratio': _extract_metric(annual_df, ['당좌비율']),
        'reserve_ratio': _extract_metric(annual_df, ['유보율']),
        
        # Valuation
        'eps': _extract_metric(annual_df, ['EPS', 'EPS(원)']),
        'bps': _extract_metric(annual_df, ['BPS', 'BPS(원)']),
        'per': _extract_metric(annual_df, ['PER', 'PER(배)']),
        'pbr': _extract_metric(annual_df, ['PBR', 'PBR(배)']),
        
        # Dividend
        'dividend_per_share': _extract_metric(annual_df, ['주당배당금']),
        'dividend_yield': _extract_metric(annual_df, ['배당수익률']),
        'dividend_payout_ratio': _extract_metric(annual_df, ['배당성향']),
    }
    
    # Extract fiscal year from column headers
    if not annual_df.columns.empty:
        result['fiscal_year'] = str(annual_df.columns[-1])
    else:
        result['fiscal_year'] = None
    
    # Calculate EPS growth YoY
    eps_row = _find_row(annual_df, 'EPS')
    if eps_row is not None:
        eps_series = pd.to_numeric(eps_row.replace('-', np.nan), errors='coerce').dropna()
        if len(eps_series) >= 2:
            recent_eps = eps_series.iloc[-1]
            prev_eps = eps_series.iloc[-2]
            if prev_eps != 0:
                eps_growth = ((recent_eps - prev_eps) / abs(prev_eps)) * 100
                result['eps_growth_yoy'] = round(eps_growth, 2)
    
    # Round all numeric values to 2 decimal places
    for key, value in result.items():
        if isinstance(value, (int, float)) and key != 'fiscal_year':
            result[key] = round(float(value), 2)
    
    return result


def _get_financial_data(ticker: str) -> Dict[str, Any]:
    """Extract comprehensive financial data from Naver Finance."""
    url = f"https://finance.naver.com/item/main.naver?code={ticker}"

    try:
        _rate_limit()
        response = requests.get(url, headers=_get_headers(), timeout=10)
        response.raise_for_status()
        response.encoding = 'euc-kr'

        # Use match for precise targeting
        dfs = pd.read_html(response.text, match='주요재무정보', encoding='euc-kr')
        if not dfs:
            return _get_empty_financial_data()

        df = dfs[0]

        # Set first column as index
        df.set_index(df.columns[0], inplace=True)

        # Extract annual performance data - handle both multi-index and single-level columns
        annual_df = None
        if isinstance(df.columns, pd.MultiIndex):
            # Multi-index columns from real Naver Finance HTML
            try:
                annual_df = df.xs('최근 연간 실적', axis=1, level=0)
                if hasattr(annual_df.columns, 'droplevel'):
                    try:
                        annual_df.columns = annual_df.columns.droplevel(1)
                    except (IndexError, ValueError):
                        pass
            except KeyError:
                # If '최근 연간 실적' not found, use first section
                level0_values = df.columns.get_level_values(0).unique().tolist()
                if level0_values:
                    annual_df = df.xs(level0_values[0], axis=1, level=0)
                    if hasattr(annual_df.columns, 'droplevel'):
                        try:
                            annual_df.columns = annual_df.columns.droplevel(1)
                        except (IndexError, ValueError):
                            pass
        else:
            # Single-level columns (e.g., from test fixtures)
            # Assume first 4 columns are annual data
            annual_cols = [c for c in df.columns if '분기' not in str(c) and 'E' not in str(c)][:4]
            if len(annual_cols) == 0:
                annual_cols = df.columns[:4]
            annual_df = df[annual_cols]

        if annual_df is None or annual_df.empty:
            return _get_empty_financial_data()

        # Extract all metrics
        result = _extract_all_metrics(annual_df)
        return result

    except Exception as e:
        print(f"Financial data extraction failed for {ticker}: {e}")
        return _get_empty_financial_data()


def get_ohlcv_naver(ticker: str, days: int = 30) -> Optional[Dict[str, Any]]:
    url = f"https://finance.naver.com/item/sise_day.naver?code={ticker}&page=1"
    
    try:
        _rate_limit()
        response = requests.get(url, headers=_get_headers(), timeout=10)
        response.raise_for_status()
        response.encoding = 'euc-kr'
        
        tables = pd.read_html(response.text, encoding='euc-kr')
        
        for df in tables:
            if df.shape[0] > 5 and df.shape[1] >= 6:
                first_col = df.iloc[:, 0].astype(str)
                if first_col.str.contains(r'\d{4}\.\d{2}\.\d{2}').any():
                    df.columns = ['date', 'close', 'change', 'open', 'high', 'low', 'volume']
                    df = df.dropna(subset=['date'])
                    
                    if not df.empty:
                        latest = df.iloc[0]
                        return {
                            'date': str(latest['date']),
                            'open': float(latest['open']) if pd.notna(latest.get('open')) else None,
                            'high': float(latest['high']) if pd.notna(latest.get('high')) else None,
                            'low': float(latest['low']) if pd.notna(latest.get('low')) else None,
                            'close': float(latest['close']) if pd.notna(latest.get('close')) else None,
                            'volume': int(latest['volume']) if pd.notna(latest.get('volume')) else None,
                        }
    except Exception as e:
        print(f"OHLCV fetch failed for {ticker}: {e}")
    
    return None


def get_stock_quote(ticker: str) -> Optional[Dict[str, Any]]:
    ticker = str(ticker).zfill(6)
    url = f"https://finance.naver.com/item/main.naver?code={ticker}"
    
    try:
        _rate_limit()
        response = requests.get(url, headers=_get_headers(), timeout=10)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.text, 'html.parser')
        
        name = None
        name_elem = soup.select_one('.h_company h2')
        if name_elem:
            name = name_elem.get_text(strip=True)
        if not name:
            name_elem = soup.select_one('.company_info a')
            if name_elem:
                name = name_elem.get_text(strip=True)
        
        current_price = None
        price_elem = soup.select_one('.no_today .blind')
        if price_elem:
            price_text = price_elem.get_text(strip=True).replace('포인트', '').strip()
            current_price = _parse_number(price_text)
        if not current_price:
            price_elem = soup.select_one('.new_total .blind')
            if price_elem:
                price_text = price_elem.get_text(strip=True).replace('포인트', '').strip()
                current_price = _parse_number(price_text)
        
        per_elem = soup.select_one('#_per')
        per = _parse_number(per_elem.get_text(strip=True)) if per_elem else None
        
        pbr_elem = soup.select_one('#_pbr')
        pbr = _parse_number(pbr_elem.get_text(strip=True)) if pbr_elem else None
        
        forward_per_elem = soup.select_one('#_cns_per')
        forward_per = _parse_number(forward_per_elem.get_text(strip=True)) if forward_per_elem else None
        
        eps_elem = soup.select_one('#_eps')
        eps = _parse_number(eps_elem.get_text(strip=True)) if eps_elem else None
        
        bps_elem = soup.select_one('#_bps')
        bps = _parse_number(bps_elem.get_text(strip=True)) if bps_elem else None
        if not bps and pbr and current_price and pbr != 0:
            bps = current_price / pbr
        
        market_cap_elem = soup.select_one('#_market_sum')
        market_cap = _parse_market_cap(market_cap_elem.get_text(strip=True)) if market_cap_elem else None
        
        dividend_elem = soup.select_one('#_dvr')
        dividend_yield = _parse_number(dividend_elem.get_text(strip=True).replace('%', '')) if dividend_elem else None
        
        financial_data = _get_financial_data(ticker)
        
        ohlcv = get_ohlcv_naver(ticker)
        
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
            # Financial metrics from comprehensive extraction
            'revenue': financial_data.get('revenue'),
            'operating_profit': financial_data.get('operating_profit'),
            'net_profit': financial_data.get('net_profit'),
            'operating_margin': financial_data.get('operating_margin'),
            'net_margin': financial_data.get('net_margin'),
            'roe': financial_data.get('roe'),
            'debt_ratio': financial_data.get('debt_ratio'),
            'current_ratio': financial_data.get('current_ratio'),
            'reserve_ratio': financial_data.get('reserve_ratio'),
            'eps_growth_yoy': financial_data.get('eps_growth_yoy'),
            'dividend_per_share': financial_data.get('dividend_per_share'),
            'dividend_payout_ratio': financial_data.get('dividend_payout_ratio'),
            'fiscal_year': financial_data.get('fiscal_year'),
            'open': ohlcv.get('open') if ohlcv else None,
            'high': ohlcv.get('high') if ohlcv else None,
            'low': ohlcv.get('low') if ohlcv else None,
            'close': ohlcv.get('close') if ohlcv else None,
            'volume': ohlcv.get('volume') if ohlcv else None,
            'ohlcv_date': ohlcv.get('date') if ohlcv else None,
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
        if quote:
            results.append(quote)
    return results


def get_kospi_tickers() -> List[str]:
    return get_all_tickers()
