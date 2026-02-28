"""
Tests for DART API integration and advanced financial indicators.

Run tests with:
    cd backend && python -m pytest tests/test_dart_api.py -v
"""

import os
import sys
import pytest
from datetime import datetime

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from app.services.dart_api import (
    calculate_forward_pe,
    calculate_eps_growth_yoy,
)
from app.services.data_quality import DataQualityChecker


class TestForwardPECalculation:
    """Test Forward P/E calculation."""
    
    def test_calculate_forward_pe_basic(self):
        """Test basic forward PE calculation."""
        # PER = 15, EPS = 1000, growth = 10%
        # Current Price = 15 * 1000 = 15000
        # Forward EPS = 1000 * 1.1 = 1100
        # Forward PE = 15000 / 1100 = 13.64
        result = calculate_forward_pe(15.0, 1000.0, 0.10)
        assert result is not None
        assert abs(result - 13.64) < 0.1
    
    def test_calculate_forward_pe_zero_eps(self):
        """Test forward PE with zero EPS."""
        result = calculate_forward_pe(15.0, 0.0, 0.10)
        assert result is None
    
    def test_calculate_forward_pe_negative_eps(self):
        """Test forward PE with negative EPS."""
        result = calculate_forward_pe(15.0, -100.0, 0.10)
        assert result is None
    
    def test_calculate_forward_pe_none_input(self):
        """Test forward PE with None input."""
        result = calculate_forward_pe(None, 1000.0, 0.10)
        assert result is None
        
        result = calculate_forward_pe(15.0, None, 0.10)
        assert result is None
    
    def test_calculate_forward_pe_different_growth_rates(self):
        """Test forward PE with different growth rates."""
        # PER = 20, EPS = 500
        # 0% growth: Forward PE = Current PE = 20
        result_0 = calculate_forward_pe(20.0, 500.0, 0.0)
        assert result_0 == 20.0
        
        # 20% growth: Forward PE should be lower
        result_20 = calculate_forward_pe(20.0, 500.0, 0.20)
        assert result_20 is not None
        assert result_20 < result_0
        
        # 50% growth: Even lower
        result_50 = calculate_forward_pe(20.0, 500.0, 0.50)
        assert result_50 is not None
        assert result_50 < result_20


class TestEPSGrowthCalculation:
    """Test EPS YoY growth calculation."""
    
    def test_calculate_eps_growth_positive(self):
        """Test positive EPS growth."""
        # Current = 1100, Previous = 1000
        # Growth = (1100 - 1000) / 1000 * 100 = 10%
        result = calculate_eps_growth_yoy(1100.0, 1000.0)
        assert result is not None
        assert abs(result - 10.0) < 0.1
    
    def test_calculate_eps_growth_negative(self):
        """Test negative EPS growth (decline)."""
        # Current = 800, Previous = 1000
        # Growth = (800 - 1000) / 1000 * 100 = -20%
        result = calculate_eps_growth_yoy(800.0, 1000.0)
        assert result is not None
        assert abs(result - (-20.0)) < 0.1
    
    def test_calculate_eps_growth_zero_previous(self):
        """Test EPS growth with zero previous EPS."""
        # Current = 1000, Previous = 0
        result = calculate_eps_growth_yoy(1000.0, 0.0)
        assert result == 100.0
        
        # Current = 0, Previous = 0
        result = calculate_eps_growth_yoy(0.0, 0.0)
        assert result == 0.0
    
    def test_calculate_eps_growth_none_input(self):
        """Test EPS growth with None input."""
        result = calculate_eps_growth_yoy(None, 1000.0)
        assert result is None
        
        result = calculate_eps_growth_yoy(1000.0, None)
        assert result is None


class TestDataQualityValidation:
    """Test data quality validation functions."""
    
    def test_validate_per_valid(self):
        """Test valid PER values."""
        assert DataQualityChecker.validate_per(10.0) is True
        assert DataQualityChecker.validate_per(0.5) is True
        assert DataQualityChecker.validate_per(100.0) is True
    
    def test_validate_per_invalid(self):
        """Test invalid PER values."""
        assert DataQualityChecker.validate_per(None) is False
        assert DataQualityChecker.validate_per(-5.0) is False
        assert DataQualityChecker.validate_per(0.0) is False
        assert DataQualityChecker.validate_per(1000.0) is False  # Too high
    
    def test_validate_roe_valid(self):
        """Test valid ROE values."""
        assert DataQualityChecker.validate_roe(15.0) is True
        assert DataQualityChecker.validate_roe(-10.0) is True  # Loss is valid
        assert DataQualityChecker.validate_roe(50.0) is True
    
    def test_validate_roe_invalid(self):
        """Test invalid ROE values."""
        assert DataQualityChecker.validate_roe(None) is False
        assert DataQualityChecker.validate_roe(-100.0) is False  # Too low
        assert DataQualityChecker.validate_roe(500.0) is False  # Too high
    
    def test_validate_debt_ratio_valid(self):
        """Test valid debt ratio values."""
        assert DataQualityChecker.validate_debt_ratio(50.0) is True
        assert DataQualityChecker.validate_debt_ratio(0.0) is True
        assert DataQualityChecker.validate_debt_ratio(1000.0) is True
    
    def test_validate_debt_ratio_invalid(self):
        """Test invalid debt ratio values."""
        assert DataQualityChecker.validate_debt_ratio(None) is False
        assert DataQualityChecker.validate_debt_ratio(-10.0) is False
        assert DataQualityChecker.validate_debt_ratio(10000.0) is False  # Too high
    
    def test_clean_per(self):
        """Test PER cleaning."""
        assert DataQualityChecker.clean_per(10.0) == 10.0
        assert DataQualityChecker.clean_per(200.0) == 100.0  # Clamped to max
        assert DataQualityChecker.clean_per(-5.0) is None
        assert DataQualityChecker.clean_per(None) is None
    
    def test_clean_roe(self):
        """Test ROE cleaning."""
        assert DataQualityChecker.clean_roe(15.0) == 15.0
        assert DataQualityChecker.clean_roe(150.0) == 100.0  # Clamped to max
        assert DataQualityChecker.clean_roe(-100.0) is None


class TestDataQualityDataFrame:
    """Test data quality with DataFrames."""
    
    def test_detect_outliers_zscore(self):
        """Test outlier detection with z-score method runs without error."""
        import pandas as pd
        
        df = pd.DataFrame({
            'per': [10.0, 12.0, 11.0, 10.5, 11.5, 10.8, 500.0]
        })
        
        outliers = DataQualityChecker.detect_outliers(df, 'per', method='zscore')
        
        # Should return a boolean series of same length
        assert len(outliers) == len(df)
        assert outliers.dtype == bool
    
    def test_detect_outliers_iqr(self):
        """Test outlier detection with IQR method runs without error."""
        import pandas as pd
        
        df = pd.DataFrame({
            'roe': [10.0, 12.0, 11.0, 10.5, 11.5, 10.8, 500.0]
        })
        
        outliers = DataQualityChecker.detect_outliers(df, 'roe', method='iqr')
        
        # Should return a boolean series of same length
        assert len(outliers) == len(df)
        assert outliers.dtype == bool
    
    def test_get_data_quality_report(self):
        """Test data quality report generation."""
        import pandas as pd
        import numpy as np
        
        df = pd.DataFrame({
            'ticker': ['005930', '000001', '002000'],
            'per': [15.0, 20.0, None],
            'roe': [10.0, None, 15.0],
        })
        
        report = DataQualityChecker.get_data_quality_report(df)
        
        assert report['total_stocks'] == 3
        assert 'columns' in report
        assert 'per' in report['columns']
        assert report['columns']['per']['count'] == 2
        assert report['columns']['per']['missing'] == 1
    
    def test_clean_dataframe(self):
        """Test full DataFrame cleaning."""
        import pandas as pd
        import numpy as np
        
        df = pd.DataFrame({
            'ticker': ['005930', '000001'],
            'per': [15.0, 200.0],  # 200 should be clamped
            'roe': [10.0, -100.0],  # -100 should be invalid
        })
        
        cleaned = DataQualityChecker.clean_dataframe(df)
        
        assert cleaned['per'].iloc[1] == 100.0  # Clamped
        assert pd.isna(cleaned['roe'].iloc[1])  # Invalid, set to NaN


class TestDartAPIClient:
    """Test DART API Client (requires API key)."""
    
    @pytest.mark.skipif(
        not os.getenv('DART_API_KEY'),
        reason="DART_API_KEY not set"
    )
    def test_dart_client_initialization(self):
        """Test DART client initialization with valid API key."""
        from app.services.dart_api import DartAPIClient
        
        client = DartAPIClient()
        assert client is not None
        assert client.api_key is not None
    
    @pytest.mark.skipif(
        not os.getenv('DART_API_KEY'),
        reason="DART_API_KEY not set"
    )
    def test_get_corp_code_samsung(self):
        """Test getting corp code for Samsung Electronics."""
        from app.services.dart_api import DartAPIClient
        
        client = DartAPIClient()
        corp_code = client.get_corp_code('005930')  # Samsung
        
        # Corp code should be found (might be None if API unavailable)
        # but should not raise an exception
        assert corp_code is None or isinstance(corp_code, str)
    
    def test_dart_client_no_api_key(self):
        """Test DART client without API key."""
        from app.services.dart_api import DartAPIClient
        
        # Clear any existing API key
        original_key = os.getenv('DART_API_KEY')
        if original_key:
            del os.environ['DART_API_KEY']
        
        try:
            with pytest.raises(ValueError) as exc_info:
                DartAPIClient()
            
            assert "DART_API_KEY is required" in str(exc_info.value)
        finally:
            # Restore original key
            if original_key:
                os.environ['DART_API_KEY'] = original_key


class TestStockSchema:
    """Test Stock schema with new fields."""
    
    def test_stock_detail_with_new_fields(self):
        """Test StockDetail schema includes new fields."""
        from app.schemas.stock import StockDetail
        
        stock = StockDetail(
            ticker='005930',
            name='Samsung Electronics',
            current_price=70000.0,
            change_rate=1.5,
            per=15.0,
            pbr=1.5,
            eps=4666.0,
            bps=46666.0,
            market_cap=450000000000000.0,
            # New fields
            forward_pe=13.5,
            roe=12.5,
            debt_ratio=45.0,
            eps_growth_yoy=10.0,
            sector='Electronics'
        )
        
        assert stock.ticker == '005930'
        assert stock.forward_pe == 13.5
        assert stock.roe == 12.5
        assert stock.debt_ratio == 45.0
        assert stock.eps_growth_yoy == 10.0
        assert stock.sector == 'Electronics'
    
    def test_stock_detail_optional_fields(self):
        """Test StockDetail with optional fields as None."""
        from app.schemas.stock import StockDetail
        
        stock = StockDetail(
            ticker='005930',
            name='Samsung Electronics',
            current_price=70000.0,
            change_rate=1.5,
        )
        
        assert stock.per is None
        assert stock.roe is None
        assert stock.forward_pe is None


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
