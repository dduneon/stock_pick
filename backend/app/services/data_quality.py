"""
Data quality checks and validation for financial indicators.

This module provides validation, cleaning, and outlier detection 
for stock financial data to ensure data quality before analysis.

Usage:
    from app.services.data_quality import DataQualityChecker
    
    checker = DataQualityChecker()
    is_valid = checker.validate_per(15.5)
    cleaned_df = checker.clean_dataframe(df)
"""

from typing import Dict, List, Optional, Tuple
import pandas as pd
import numpy as np


class DataQualityChecker:
    """Validate and clean financial data."""
    
    # Validation thresholds
    PER_MIN = 0.1
    PER_MAX = 100.0  # PER > 100 might be suspicious (extreme overvaluation)
    PER_EXTREME_MAX = 500.0  # Hard cutoff for outliers
    
    PBR_MIN = 0.1
    PBR_MAX = 10.0
    PBR_EXTREME_MAX = 50.0
    
    ROE_MIN = -50.0  # ROE can be negative (losses)
    ROE_MAX = 100.0  # Extremely high ROE might indicate data error
    ROE_EXTREME_MAX = 200.0
    
    DEBT_RATIO_MIN = 0.0
    DEBT_RATIO_MAX = 1000.0  # 1000% is very high but possible
    DEBT_RATIO_EXTREME_MAX = 5000.0
    
    EPS_GROWTH_MIN = -100.0  # -100% means complete loss
    EPS_GROWTH_MAX = 200.0  # More than 200% growth is suspicious
    EPS_GROWTH_EXTREME_MAX = 1000.0
    
    FORWARD_PE_MIN = 0.1
    FORWARD_PE_MAX = 100.0
    
    # Z-score threshold for outlier detection
    Z_SCORE_THRESHOLD = 3.0
    
    @staticmethod
    def validate_per(per: Optional[float]) -> bool:
        """
        Validate PER (Price-to-Earnings Ratio) value.
        
        PER should be positive (negative means losses).
        Extremely high PER (>100) might indicate data error or extreme overvaluation.
        
        Args:
            per: PER value to validate
        
        Returns:
            True if valid, False otherwise
        """
        if per is None:
            return False
        return DataQualityChecker.PER_MIN <= per <= DataQualityChecker.PER_EXTREME_MAX
    
    @staticmethod
    def validate_pbr(pbr: Optional[float]) -> bool:
        """
        Validate PBR (Price-to-Book Ratio) value.
        
        Args:
            pbr: PBR value to validate
        
        Returns:
            True if valid, False otherwise
        """
        if pbr is None:
            return False
        return DataQualityChecker.PBR_MIN <= pbr <= DataQualityChecker.PBR_EXTREME_MAX
    
    @staticmethod
    def validate_roe(roe: Optional[float]) -> bool:
        """
        Validate ROE (Return on Equity) value.
        
        ROE can be negative (losses) but extreme values are suspicious.
        
        Args:
            roe: ROE value to validate (in percentage, e.g., 15 for 15%)
        
        Returns:
            True if valid, False otherwise
        """
        if roe is None:
            return False
        return DataQualityChecker.ROE_MIN <= roe <= DataQualityChecker.ROE_EXTREME_MAX
    
    @staticmethod
    def validate_debt_ratio(debt_ratio: Optional[float]) -> bool:
        """
        Validate Debt Ratio value.
        
        Debt ratio should be positive. Very high values might indicate data error.
        
        Args:
            debt_ratio: Debt ratio to validate (in percentage)
        
        Returns:
            True if valid, False otherwise
        """
        if debt_ratio is None:
            return False
        return DataQualityChecker.DEBT_RATIO_MIN <= debt_ratio <= DataQualityChecker.DEBT_RATIO_EXTREME_MAX
    
    @staticmethod
    def validate_eps_growth(eps_growth: Optional[float]) -> bool:
        """
        Validate EPS growth rate.
        
        Args:
            eps_growth: EPS growth rate to validate (in percentage)
        
        Returns:
            True if valid, False otherwise
        """
        if eps_growth is None:
            return False
        return DataQualityChecker.EPS_GROWTH_MIN <= eps_growth <= DataQualityChecker.EPS_GROWTH_EXTREME_MAX
    
    @staticmethod
    def validate_forward_pe(forward_pe: Optional[float]) -> bool:
        """
        Validate Forward P/E ratio.
        
        Args:
            forward_pe: Forward P/E value to validate
        
        Returns:
            True if valid, False otherwise
        """
        if forward_pe is None:
            return False
        return DataQualityChecker.FORWARD_PE_MIN <= forward_pe <= DataQualityChecker.FORWARD_PE_MAX
    
    @staticmethod
    def detect_outliers(
        df: pd.DataFrame, 
        column: str, 
        method: str = 'zscore',
        threshold: float = 3.0
    ) -> pd.Series:
        """
        Detect outliers in a DataFrame column.
        
        Args:
            df: DataFrame containing the data
            column: Column name to check for outliers
            method: Detection method ('zscore' or 'iqr')
            threshold: Threshold for outlier detection
        
        Returns:
            Boolean Series indicating outliers (True = outlier)
        """
        if column not in df.columns:
            return pd.Series(False, index=df.index)
        
        data = df[column].dropna()
        if len(data) < 3:
            return pd.Series(False, index=df.index)
        
        if method == 'zscore':
            # Z-score method
            z_scores = np.abs((data - data.mean()) / data.std())
            outliers = z_scores > threshold
        elif method == 'iqr':
            # IQR method
            Q1 = data.quantile(0.25)
            Q3 = data.quantile(0.75)
            IQR = Q3 - Q1
            lower_bound = Q1 - threshold * IQR
            upper_bound = Q3 + threshold * IQR
            outliers = (data < lower_bound) | (data > upper_bound)
        else:
            raise ValueError(f"Unknown outlier detection method: {method}")
        
        # Map back to original DataFrame index
        return df[column].isin(data[outliers])
    
    @staticmethod
    def fill_missing_with_industry_avg(
        df: pd.DataFrame, 
        column: str, 
        sector_column: str = 'sector'
    ) -> pd.DataFrame:
        """
        Fill missing values with industry average.
        
        Args:
            df: DataFrame with stock data
            column: Column to fill
            sector_column: Column containing sector/industry information
        
        Returns:
            DataFrame with missing values filled
        """
        if column not in df.columns:
            return df
        
        if sector_column in df.columns:
            # Fill by sector
            df[column] = df.groupby(sector_column)[column].transform(
                lambda x: x.fillna(x.mean())
            )
        
        # Fill remaining with overall average
        df[column] = df[column].fillna(df[column].mean())
        
        return df
    
    @staticmethod
    def clamp_value(value: Optional[float], min_val: float, max_val: float) -> Optional[float]:
        """
        Clamp a value to a valid range.
        
        Args:
            value: Value to clamp
            min_val: Minimum allowed value
            max_val: Maximum allowed value
        
        Returns:
            Clamped value or None if input is None
        """
        if value is None:
            return None
        return max(min_val, min(max_val, value))
    
    @classmethod
    def clean_per(cls, per: Optional[float]) -> Optional[float]:
        """Clean and validate PER value."""
        if not cls.validate_per(per):
            return None
        return cls.clamp_value(per, cls.PER_MIN, cls.PER_MAX)
    
    @classmethod
    def clean_pbr(cls, pbr: Optional[float]) -> Optional[float]:
        """Clean and validate PBR value."""
        if not cls.validate_pbr(pbr):
            return None
        return cls.clamp_value(pbr, cls.PBR_MIN, cls.PBR_MAX)
    
    @classmethod
    def clean_roe(cls, roe: Optional[float]) -> Optional[float]:
        """Clean and validate ROE value."""
        if not cls.validate_roe(roe):
            return None
        return cls.clamp_value(roe, cls.ROE_MIN, cls.ROE_MAX)
    
    @classmethod
    def clean_debt_ratio(cls, debt_ratio: Optional[float]) -> Optional[float]:
        """Clean and validate debt ratio value."""
        if not cls.validate_debt_ratio(debt_ratio):
            return None
        return cls.clamp_value(debt_ratio, cls.DEBT_RATIO_MIN, cls.DEBT_RATIO_MAX)
    
    @classmethod
    def clean_eps_growth(cls, eps_growth: Optional[float]) -> Optional[float]:
        """Clean and validate EPS growth rate."""
        if not cls.validate_eps_growth(eps_growth):
            return None
        return cls.clamp_value(eps_growth, cls.EPS_GROWTH_MIN, cls.EPS_GROWTH_MAX)
    
    @classmethod
    def clean_dataframe(cls, df: pd.DataFrame) -> pd.DataFrame:
        """
        Clean all financial indicators in a DataFrame.
        
        Applies validation and clamping to all known financial indicator columns.
        
        Args:
            df: DataFrame with stock data
        
        Returns:
            Cleaned DataFrame
        """
        df = df.copy()
        
        # Clean PER
        if 'per' in df.columns:
            df['per'] = df['per'].apply(cls.clean_per)
        
        # Clean PBR
        if 'pbr' in df.columns:
            df['pbr'] = df['pbr'].apply(cls.clean_pbr)
        
        # Clean ROE
        if 'roe' in df.columns:
            df['roe'] = df['roe'].apply(cls.clean_roe)
        
        # Clean Debt Ratio
        if 'debt_ratio' in df.columns:
            df['debt_ratio'] = df['debt_ratio'].apply(cls.clean_debt_ratio)
        
        # Clean EPS Growth
        if 'eps_growth_yoy' in df.columns:
            df['eps_growth_yoy'] = df['eps_growth_yoy'].apply(cls.clean_eps_growth)
        
        # Clean Forward PE
        if 'forward_pe' in df.columns:
            df['forward_pe'] = df['forward_pe'].apply(
                lambda x: cls.clamp_value(x, cls.FORWARD_PE_MIN, cls.FORWARD_PE_MAX) 
                if cls.validate_forward_pe(x) else None
            )
        
        return df
    
    @staticmethod
    def get_data_quality_report(df: pd.DataFrame) -> Dict[str, any]:
        """
        Generate a data quality report for a DataFrame.
        
        Args:
            df: DataFrame with stock data
        
        Returns:
            Dictionary with data quality statistics
        """
        report = {
            'total_stocks': len(df),
            'columns': {}
        }
        
        financial_columns = ['per', 'pbr', 'roe', 'debt_ratio', 'eps_growth_yoy', 'forward_pe']
        
        for col in financial_columns:
            if col in df.columns:
                data = df[col].dropna()
                report['columns'][col] = {
                    'count': len(data),
                    'missing': len(df) - len(data),
                    'missing_pct': round((len(df) - len(data)) / len(df) * 100, 2) if len(df) > 0 else 0,
                    'min': data.min() if len(data) > 0 else None,
                    'max': data.max() if len(data) > 0 else None,
                    'mean': data.mean() if len(data) > 0 else None,
                    'median': data.median() if len(data) > 0 else None,
                }
        
        return report
    
    @staticmethod
    def remove_outliers(
        df: pd.DataFrame, 
        columns: List[str],
        method: str = 'zscore',
        threshold: float = 3.0
    ) -> pd.DataFrame:
        """
        Remove outliers from specified columns.
        
        Args:
            df: DataFrame with stock data
            columns: List of columns to check for outliers
            method: Outlier detection method ('zscore' or 'iqr')
            threshold: Threshold for outlier detection
        
        Returns:
            DataFrame with outliers removed (set to None)
        """
        df = df.copy()
        
        for col in columns:
            if col in df.columns:
                outliers = DataQualityChecker.detect_outliers(df, col, method, threshold)
                df.loc[outliers, col] = None
        
        return df
