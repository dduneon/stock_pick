"""
Technical analysis module using TA-Lib.
Calculates MA, RSI, and volume indicators.
"""

import pandas as pd
import talib
from typing import Dict, Optional, List
from datetime import datetime


class TechnicalAnalyzer:
    """Calculate technical indicators for stock data."""
    
    def __init__(self, ohlcv_df: pd.DataFrame):
        """
        Initialize with OHLCV DataFrame.
        
        Args:
            ohlcv_df: DataFrame with columns: open, high, low, close, volume
        """
        self.df = ohlcv_df.copy()
        
    def calculate_all(self) -> pd.DataFrame:
        """Calculate all technical indicators."""
        self.calculate_moving_averages()
        self.calculate_rsi()
        self.calculate_volume_indicators()
        return self.df
    
    def calculate_moving_averages(self) -> pd.DataFrame:
        """
        Calculate Simple Moving Averages.
        Periods: 5, 20, 60, 120 days
        """
        # Using TA-Lib
        self.df['SMA_5'] = talib.SMA(self.df['close'], timeperiod=5)
        self.df['SMA_20'] = talib.SMA(self.df['close'], timeperiod=20)
        self.df['SMA_60'] = talib.SMA(self.df['close'], timeperiod=60)
        self.df['SMA_120'] = talib.SMA(self.df['close'], timeperiod=120)
        
        return self.df
    
    def calculate_rsi(self, period: int = 14) -> pd.DataFrame:
        """
        Calculate Relative Strength Index (RSI).
        
        Standard period: 14 days
        Overbought: > 70
        Oversold: < 30
        """
        self.df['RSI_14'] = talib.RSI(self.df['close'], timeperiod=period)
        return self.df
    
    def calculate_volume_indicators(self) -> pd.DataFrame:
        """
        Calculate volume-based indicators.
        - Volume Moving Average (20-day)
        - Volume Spike detection
        """
        # Volume SMA
        self.df['SMA_20Volume'] = talib.SMA(self.df['volume'].astype(float), timeperiod=20)
        
        # Volume spike (current volume > 2x average)
        self.df['volume_spike'] = self.df['volume'] > (self.df['SMA_20Volume'] * 2)
        
        return self.df
    
    def get_latest_indicators(self) -> Dict:
        """Get the most recent values for all indicators."""
        if self.df.empty:
            return {}
        
        latest = self.df.iloc[-1]
        
        return {
            # Price
            'open': float(latest.get('open')) if pd.notna(latest.get('open')) else None,
            'high': float(latest.get('high')) if pd.notna(latest.get('high')) else None,
            'low': float(latest.get('low')) if pd.notna(latest.get('low')) else None,
            'close': float(latest.get('close')) if pd.notna(latest.get('close')) else None,
            'volume': int(latest.get('volume')) if pd.notna(latest.get('volume')) else None,
            
            # Moving Averages
            'ma_5': float(latest.get('SMA_5')) if pd.notna(latest.get('SMA_5')) else None,
            'ma_20': float(latest.get('SMA_20')) if pd.notna(latest.get('SMA_20')) else None,
            'ma_60': float(latest.get('SMA_60')) if pd.notna(latest.get('SMA_60')) else None,
            'ma_120': float(latest.get('SMA_120')) if pd.notna(latest.get('SMA_120')) else None,
            
            # RSI
            'rsi_14': float(latest.get('RSI_14')) if pd.notna(latest.get('RSI_14')) else None,
            'rsi_signal': self._get_rsi_signal(latest.get('RSI_14')),
            
            # Volume
            'volume_ma_20': float(latest.get('SMA_20Volume')) if pd.notna(latest.get('SMA_20Volume')) else None,
            'volume_spike': bool(latest.get('volume_spike', False)),
            
            # Trend
            'trend': self._determine_trend(),
        }
    
    def _get_rsi_signal(self, rsi: Optional[float]) -> str:
        """Determine RSI signal."""
        if rsi is None or pd.isna(rsi):
            return 'neutral'
        if rsi > 70:
            return 'overbought'
        elif rsi < 30:
            return 'oversold'
        else:
            return 'neutral'
    
    def _determine_trend(self) -> str:
        """Determine price trend based on MAs."""
        if len(self.df) < 20:
            return 'unknown'
        
        latest = self.df.iloc[-1]
        
        ma_5 = latest.get('SMA_5')
        ma_20 = latest.get('SMA_20')
        ma_60 = latest.get('SMA_60')
        
        if pd.isna(ma_5) or pd.isna(ma_20):
            return 'unknown'
        
        # Golden cross / Death cross logic
        if ma_5 > ma_20 > ma_60:
            return 'strong_uptrend'
        elif ma_5 > ma_20:
            return 'uptrend'
        elif ma_5 < ma_20 < ma_60:
            return 'strong_downtrend'
        elif ma_5 < ma_20:
            return 'downtrend'
        else:
            return 'sideways'
    
    def get_chart_data(self) -> List[Dict]:
        """
        Get data formatted for chart rendering.
        Returns list of OHLCV + indicators.
        """
        result = []
        
        for idx, row in self.df.iterrows():
            # Handle both datetime index and string index
            if isinstance(idx, datetime):
                date_str = idx.strftime('%Y-%m-%d')
            elif hasattr(idx, 'strftime'):
                date_str = idx.strftime('%Y-%m-%d')
            else:
                date_str = str(idx)
            
            data_point = {
                'date': date_str,
                'open': float(row.get('open')) if pd.notna(row.get('open')) else None,
                'high': float(row.get('high')) if pd.notna(row.get('high')) else None,
                'low': float(row.get('low')) if pd.notna(row.get('low')) else None,
                'close': float(row.get('close')) if pd.notna(row.get('close')) else None,
                'volume': int(row.get('volume')) if pd.notna(row.get('volume')) else None,
            }
            
            # Add indicators if available
            if 'SMA_5' in row and pd.notna(row['SMA_5']):
                data_point['ma_5'] = float(row['SMA_5'])
            if 'SMA_20' in row and pd.notna(row['SMA_20']):
                data_point['ma_20'] = float(row['SMA_20'])
            if 'SMA_60' in row and pd.notna(row['SMA_60']):
                data_point['ma_60'] = float(row['SMA_60'])
            if 'SMA_120' in row and pd.notna(row['SMA_120']):
                data_point['ma_120'] = float(row['SMA_120'])
            if 'RSI_14' in row and pd.notna(row['RSI_14']):
                data_point['rsi'] = float(row['RSI_14'])
            if 'SMA_20Volume' in row and pd.notna(row['SMA_20Volume']):
                data_point['volume_ma_20'] = float(row['SMA_20Volume'])
            
            result.append(data_point)
        
        return result


# Convenience functions for API usage

def analyze_stock(ticker: str, days: int = 120) -> Dict:
    """
    Complete technical analysis for a stock.
    
    Args:
        ticker: Stock ticker code
        days: Number of days of history
    
    Returns:
        Dictionary with all technical indicators
    """
    import sys
    import os
    sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../..'))
    
    from batch.collect_history import collect_historical_ohlcv
    
    # Collect data
    df = collect_historical_ohlcv(ticker, days)
    
    if df.empty:
        return {'error': 'No data available'}
    
    # Calculate indicators
    analyzer = TechnicalAnalyzer(df)
    analyzer.calculate_all()
    
    return {
        'ticker': ticker,
        'indicators': analyzer.get_latest_indicators(),
        'chart_data': analyzer.get_chart_data(),
    }
