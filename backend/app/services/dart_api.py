"""
DART (전자공시시스템) API integration for financial statements.
Provides ROE, Debt Ratio, and other fundamental indicators.

Usage:
    from app.services.dart_api import DartAPIClient
    
    client = DartAPIClient()
    roe = client.calculate_roe('005930')
    debt_ratio = client.calculate_debt_ratio('005930')
"""

import os
from typing import Optional, Dict, Any
from datetime import datetime, timedelta
import time
import pandas as pd

# Try to import OpenDartReader - may not be available in all environments
try:
    import OpenDartReader
    DART_AVAILABLE = True
except ImportError:
    DART_AVAILABLE = False
    OpenDartReader = None


class DartAPIClient:
    """DART API client for fetching financial statements and calculating ratios."""
    
    # Rate limiting configuration
    RATE_LIMIT_DELAY = 0.5  # seconds between requests
    MAX_RETRIES = 3
    
    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize DART API client.
        
        Args:
            api_key: DART API key. If not provided, reads from DART_API_KEY env var.
        
        Raises:
            ValueError: If API key is not provided and not in environment.
            ImportError: If OpenDartReader is not installed.
        """
        if not DART_AVAILABLE:
            raise ImportError(
                "OpenDartReader is not installed. "
                "Install with: pip install opendartreader"
            )
        
        self.api_key = api_key or os.getenv('DART_API_KEY')
        if not self.api_key:
            raise ValueError(
                "DART_API_KEY is required. "
                "Get your key from: https://opendart.fss.or.kr/ "
                "Set it as environment variable or pass to constructor."
            )
        
        self.dart = OpenDartReader(self.api_key)
        self._last_request_time = 0
        self._corp_code_cache: Dict[str, Optional[str]] = {}
    
    def _rate_limit(self):
        """Apply rate limiting between requests."""
        elapsed = time.time() - self._last_request_time
        if elapsed < self.RATE_LIMIT_DELAY:
            time.sleep(self.RATE_LIMIT_DELAY - elapsed)
        self._last_request_time = time.time()
    
    def _retry_with_backoff(self, func, *args, **kwargs):
        """Execute function with retry logic and exponential backoff."""
        for attempt in range(self.MAX_RETRIES):
            try:
                self._rate_limit()
                return func(*args, **kwargs)
            except Exception as e:
                if attempt == self.MAX_RETRIES - 1:
                    raise e
                # Exponential backoff: 1s, 2s, 4s
                time.sleep(2 ** attempt)
        return None
    
    def get_corp_code(self, ticker: str) -> Optional[str]:
        """
        Get corporation code from ticker symbol.
        
        Args:
            ticker: Stock ticker code (e.g., '005930')
        
        Returns:
            Corporation code for DART API, or None if not found.
        """
        # Check cache first
        if ticker in self._corp_code_cache:
            return self._corp_code_cache[ticker]
        
        try:
            corp_list = self.dart.corp_codes
            match = corp_list[corp_list['stock_code'] == ticker]
            if not match.empty:
                corp_code = match.iloc[0]['corp_code']
                self._corp_code_cache[ticker] = corp_code
                return corp_code
        except Exception as e:
            print(f"Error looking up corp code for {ticker}: {e}")
        
        self._corp_code_cache[ticker] = None
        return None
    
    def get_financial_statement(
        self, 
        ticker: str, 
        year: int,
        report_code: str = '11011'  # 사업보고서
    ) -> Optional[pd.DataFrame]:
        """
        Get financial statement (재무상태표) for a company.
        
        Args:
            ticker: Stock ticker code (e.g., '005930')
            year: Fiscal year (e.g., 2023)
            report_code: Report type code (11011=사업보고서, 11012=반기보고서, 11013=분기보고서, 11014=1분기보고서)
        
        Returns:
            DataFrame with financial statement data, or None if not available.
        """
        corp_code = self.get_corp_code(ticker)
        if not corp_code:
            return None
        
        try:
            def fetch():
                return self.dart.finstate(corp_code, year, report_code)
            
            fs = self._retry_with_backoff(fetch)
            return fs
        except Exception as e:
            print(f"Error fetching financial statement for {ticker}: {e}")
            return None
    
    def get_income_statement(
        self, 
        ticker: str, 
        year: int,
        report_code: str = '11011'
    ) -> Optional[pd.DataFrame]:
        """
        Get income statement (손익계산서) for a company.
        
        Args:
            ticker: Stock ticker code (e.g., '005930')
            year: Fiscal year
            report_code: Report type code
        
        Returns:
            DataFrame with income statement data, or None if not available.
        """
        corp_code = self.get_corp_code(ticker)
        if not corp_code:
            return None
        
        try:
            def fetch():
                return self.dart.finstate(corp_code, year, report_code)
            
            return self._retry_with_backoff(fetch)
        except Exception as e:
            print(f"Error fetching income statement for {ticker}: {e}")
            return None
    
    def calculate_roe(self, ticker: str) -> Optional[float]:
        """
        Calculate ROE (Return on Equity, 자기자본이익률).
        
        Formula: Net Income / Shareholders' Equity * 100
        
        Args:
            ticker: Stock ticker code (e.g., '005930')
        
        Returns:
            ROE percentage (e.g., 15.5 for 15.5%), or None if data unavailable.
        """
        # Get most recent complete fiscal year
        year = datetime.now().year - 1
        
        # Try current and previous year (some companies may not have filed yet)
        for y in [year, year - 1]:
            try:
                # Get financial statement (contains both BS and IS data)
                fs_df = self.get_financial_statement(ticker, y)
                if fs_df is None or fs_df.empty:
                    continue
                
                # Extract values from the same finstate data
                net_income = self._extract_net_income(fs_df)
                equity = self._extract_shareholders_equity(fs_df)
                
                if net_income is not None and equity is not None and equity > 0:
                    roe = (net_income / equity) * 100
                    return round(roe, 2)
                    
            except Exception as e:
                print(f"Error calculating ROE for {ticker} (year {y}): {e}")
                continue
        
        return None
    
    def calculate_debt_ratio(self, ticker: str) -> Optional[float]:
        """
        Calculate Debt Ratio (부채비율).
        
        Formula: Total Liabilities / Shareholders' Equity * 100
        
        Args:
            ticker: Stock ticker code (e.g., '005930')
        
        Returns:
            Debt ratio percentage (e.g., 150.5 for 150.5%), or None if data unavailable.
        """
        year = datetime.now().year - 1
        
        for y in [year, year - 1]:
            try:
                fs_df = self.get_financial_statement(ticker, y)
                if fs_df is None or fs_df.empty:
                    continue
                
                liabilities = self._extract_total_liabilities(fs_df)
                equity = self._extract_shareholders_equity(fs_df)
                
                if liabilities is not None and equity is not None and equity > 0:
                    debt_ratio = (liabilities / equity) * 100
                    return round(debt_ratio, 2)
                
            except Exception as e:
                print(f"Error calculating debt ratio for {ticker} (year {y}): {e}")
                continue
        
        return None
    

    
    def _extract_shareholders_equity(self, fs_df: pd.DataFrame) -> Optional[float]:
        """Extract shareholders' equity from financial statement."""
        if fs_df is None or fs_df.empty:
            return None
        
        try:
            # Find rows where sj_div = 'BS' (Balance Sheet)
            bs_df = fs_df[fs_df['sj_div'] == 'BS']
            
            # Find capital total (자본총계)
            equity_rows = bs_df[bs_df['account_nm'] == '자본총계']
            if equity_rows.empty:
                # Try alternative names
                equity_rows = bs_df[bs_df['account_nm'].str.contains('자본', na=False)]
            
            if not equity_rows.empty:
                amount_str = equity_rows.iloc[0]['thstrm_amount']
                # Parse string with commas to float
                return float(amount_str.replace(',', ''))
        except Exception as e:
            print(f"Error extracting equity: {e}")
        
        return None
    
    def _extract_total_liabilities(self, fs_df: pd.DataFrame) -> Optional[float]:
        """Extract total liabilities from financial statement."""
        if fs_df is None or fs_df.empty:
            return None
        
        try:
            bs_df = fs_df[fs_df['sj_div'] == 'BS']
            
            # Find liabilities total (부채총계)
            liability_rows = bs_df[bs_df['account_nm'] == '부채총계']
            if liability_rows.empty:
                liability_rows = bs_df[bs_df['account_nm'].str.contains('부채', na=False)]
            
            if not liability_rows.empty:
                amount_str = liability_rows.iloc[0]['thstrm_amount']
                return float(amount_str.replace(',', ''))
        except Exception as e:
            print(f"Error extracting liabilities: {e}")
        
        return None
    
    def _extract_net_income(self, fs_df: pd.DataFrame) -> Optional[float]:
        """Extract net income from income statement."""
        if fs_df is None or fs_df.empty:
            return None
        
        try:
            # Find rows where sj_div = 'IS' (Income Statement)
            is_df = fs_df[fs_df['sj_div'] == 'IS']
            
            # Find net income (당기순이익)
            income_rows = is_df[is_df['account_nm'] == '당기순이익']
            if income_rows.empty:
                income_rows = is_df[is_df['account_nm'].str.contains('순이익', na=False)]
            
            if not income_rows.empty:
                amount_str = income_rows.iloc[0]['thstrm_amount']
                return float(amount_str.replace(',', ''))
        except Exception as e:
            print(f"Error extracting net income: {e}")
        
        return None


    def _extract_outstanding_shares(self, fs_df: pd.DataFrame) -> Optional[int]:
        """Extract outstanding shares (발행주식수) from financial statement."""
        if fs_df is None or fs_df.empty:
            return None
        
        try:
            # Look for shares in the statement
            bs_df = fs_df[fs_df['sj_div'] == 'BS']
            
            # Try to find 발행주식수 or 자본금 related rows
            shares_rows = bs_df[bs_df['account_nm'].str.contains('발행주식수', na=False)]
            if not shares_rows.empty:
                amount_str = shares_rows.iloc[0]['thstrm_amount']
                return int(float(amount_str.replace(',', '')))
            
            # Alternative: Calculate from 자본금 (Capital Stock)
            capital_rows = bs_df[bs_df['account_nm'] == '자본금']
            if not capital_rows.empty:
                # Get capital amount and divide by face value (usually 100 or 5000)
                # This is approximate
                capital = float(capital_rows.iloc[0]['thstrm_amount'].replace(',', ''))
                # Face value is typically 100 or 5000 for KOSPI stocks
                # Try to determine from the company
                face_value = self._get_face_value(fs_df)
                if face_value and face_value > 0:
                    return int(capital / face_value)
                    
        except Exception as e:
            print(f"Error extracting outstanding shares: {e}")
        
        return None
    
    def _get_face_value(self, fs_df: pd.DataFrame) -> Optional[int]:
        """Get face value (액면가) from financial statement."""
        try:
            bs_df = fs_df[fs_df['sj_div'] == 'BS']
            
            # Look for 액면가 or 주당액면금액
            face_rows = bs_df[bs_df['account_nm'].str.contains('액면가', na=False)]
            if not face_rows.empty:
                amount_str = face_rows.iloc[0]['thstrm_amount']
                return int(float(amount_str.replace(',', '')))
            
            # Default face values
            return 100  # Most KOSPI stocks have 100 won face value
            
        except:
            return 100  # Default assumption
    
    def calculate_eps(self, ticker: str) -> Optional[float]:
        """
        Calculate EPS (Earnings Per Share, 주당순이익).
        
        Formula: Net Income / Outstanding Shares
        
        Args:
            ticker: Stock ticker code (e.g., '005930')
        
        Returns:
            EPS value, or None if data unavailable.
        """
        year = datetime.now().year - 1
        
        for y in [year, year - 1]:
            try:
                fs_df = self.get_financial_statement(ticker, y)
                if fs_df is None or fs_df.empty:
                    continue
                
                net_income = self._extract_net_income(fs_df)
                shares = self._extract_outstanding_shares(fs_df)
                
                if net_income is not None and shares is not None and shares > 0:
                    eps = net_income / shares
                    return round(eps, 2)
                    
            except Exception as e:
                print(f"Error calculating EPS for {ticker} (year {y}): {e}")
                continue
        
        return None
    
    def calculate_bps(self, ticker: str) -> Optional[float]:
        """
        Calculate BPS (Book Value Per Share, 주당순자산).
        
        Formula: Shareholders' Equity / Outstanding Shares
        
        Args:
            ticker: Stock ticker code (e.g., '005930')
        
        Returns:
            BPS value, or None if data unavailable.
        """
        year = datetime.now().year - 1
        
        for y in [year, year - 1]:
            try:
                fs_df = self.get_financial_statement(ticker, y)
                if fs_df is None or fs_df.empty:
                    continue
                
                equity = self._extract_shareholders_equity(fs_df)
                shares = self._extract_outstanding_shares(fs_df)
                
                if equity is not None and shares is not None and shares > 0:
                    bps = equity / shares
                    return round(bps, 2)
                    
            except Exception as e:
                print(f"Error calculating BPS for {ticker} (year {y}): {e}")
                continue
        
        return None
    
    def calculate_per(self, ticker: str, current_price: float) -> Optional[float]:
        """
        Calculate PER (Price-to-Earnings Ratio, 주가수익비율).
        
        Formula: Current Price / EPS
        
        Args:
            ticker: Stock ticker code (e.g., '005930')
            current_price: Current stock price
        
        Returns:
            PER value, or None if data unavailable.
        """
        eps = self.calculate_eps(ticker)
        
        if eps is not None and eps > 0 and current_price > 0:
            per = current_price / eps
            return round(per, 2)
        
        return None
    
    def calculate_pbr(self, ticker: str, current_price: float) -> Optional[float]:
        """
        Calculate PBR (Price-to-Book Ratio, 주가순자산비율).
        
        Formula: Current Price / BPS
        
        Args:
            ticker: Stock ticker code (e.g., '005930')
            current_price: Current stock price
        
        Returns:
            PBR value, or None if data unavailable.
        """
        bps = self.calculate_bps(ticker)
        
        if bps is not None and bps > 0 and current_price > 0:
            pbr = current_price / bps
            return round(pbr, 2)
        
        return None
    

    
    def get_company_info(self, ticker: str) -> Optional[Dict[str, Any]]:
        """
        Get company basic information.
        
        Args:
            ticker: Stock ticker code (e.g., '005930')
        
        Returns:
            Dictionary with company info, or None if not found.
        """
        corp_code = self.get_corp_code(ticker)
        if not corp_code:
            return None
        
        try:
            def fetch():
                return self.dart.company(corp_code)
            
            return self._retry_with_backoff(fetch)
        except Exception as e:
            print(f"Error fetching company info for {ticker}: {e}")
            return None


# Convenience functions for direct usage
def calculate_forward_pe(current_per: float, eps: float, growth_rate: float = 0.1) -> Optional[float]:
    """
    Calculate Forward P/E ratio.
    
    Forward P/E = Current Price / Forward EPS
    
    If no analyst consensus available, uses conservative estimate with default growth rate.
    
    Args:
        current_per: Current Price-to-Earnings ratio
        eps: Current Earnings per Share
        growth_rate: Expected EPS growth rate (default: 10% = 0.1)
    
    Returns:
        Forward P/E ratio, or None if input data is invalid.
    """
    if not current_per or not eps or eps <= 0:
        return None
    
    # Calculate current price from PER
    current_price = current_per * eps
    
    # Calculate forward EPS with growth assumption
    forward_eps = eps * (1 + growth_rate)
    
    if forward_eps <= 0:
        return None
    
    forward_pe = current_price / forward_eps
    return round(forward_pe, 2)


def calculate_eps_growth_yoy(current_eps: float, previous_eps: float) -> Optional[float]:
    """
    Calculate EPS Year-over-Year growth rate.
    
    Formula: ((Current EPS - Previous EPS) / |Previous EPS|) * 100
    
    Args:
        current_eps: Current year EPS
        previous_eps: Previous year EPS
    
    Returns:
        EPS YoY growth rate in percentage, or None if data invalid.
    """
    if current_eps is None or previous_eps is None:
        return None
    
    if previous_eps == 0:
        # If previous EPS was 0, treat any positive current EPS as 100% growth
        return 100.0 if current_eps > 0 else 0.0
    
    growth_rate = ((current_eps - previous_eps) / abs(previous_eps)) * 100
    return round(growth_rate, 2)
