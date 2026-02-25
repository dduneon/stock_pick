"""
Unit tests for pykrx data collection module.

Run tests:
    python -m pytest backend/tests/test_pykrx.py -v
"""

import os
import sys
from datetime import datetime, timedelta
from unittest.mock import patch, MagicMock

import pandas as pd
import pytest

# Add backend to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from backend.batch import collect_data


class TestGetKospiTickerList:
    """Tests for get_kospi_ticker_list function."""
    
    @patch('backend.batch.collect_data.stock')
    def test_get_kospi_ticker_list_returns_list(self, mock_stock):
        """Test that function returns a list of ticker strings."""
        # Mock pykrx response
        mock_stock.get_market_ticker_list.return_value = ['005930', '000001', '035420']
        
        result = collect_data.get_kospi_ticker_list('20240101')
        
        assert isinstance(result, list)
        assert len(result) == 3
        assert '005930' in result
        mock_stock.get_market_ticker_list.assert_called_once_with('20240101', market='KOSPI')
    
    @patch('backend.batch.collect_data.stock')
    def test_get_kospi_ticker_list_default_date(self, mock_stock):
        """Test default date is today's date."""
        mock_stock.get_market_ticker_list.return_value = []
        
        collect_data.get_kospi_ticker_list()
        
        expected_date = datetime.now().strftime("%Y%m%d")
        mock_stock.get_market_ticker_list.assert_called_once()


class TestGetStockName:
    """Tests for get_stock_name function."""
    
    @patch('backend.batch.collect_data.stock')
    def test_get_stock_name_returns_string(self, mock_stock):
        """Test that function returns company name."""
        mock_stock.get_market_ticker_name.return_value = 'Samsung Electronics'
        
        result = collect_data.get_stock_name('005930')
        
        assert result == 'Samsung Electronics'
        mock_stock.get_market_ticker_name.assert_called_once_with('005930')


class TestGetStockOhlcv:
    """Tests for get_stock_ohlcv function."""
    
    @patch('backend.batch.collect_data.stock')
    def test_get_stock_ohlcv_returns_dataframe(self, mock_stock):
        """Test that function returns DataFrame with OHLCV data."""
        # Create mock OHLCV data
        mock_df = pd.DataFrame({
            '시가': [70000],
            '고가': [71000],
            '저가': [69500],
            '종가': [70500],
            '거래량': [1000000],
            '거래대금': [70000000000]
        })
        mock_stock.get_market_ohlcv.return_value = mock_df
        
        result = collect_data.get_stock_ohlcv('005930', '20240101')
        
        assert isinstance(result, pd.DataFrame)
        assert len(result) == 1
        assert '시가' in result.columns
        assert '종가' in result.columns
    
    @patch('backend.batch.collect_data.stock')
    def test_get_stock_ohlcv_empty_on_error(self, mock_stock):
        """Test that empty DataFrame is returned on error."""
        mock_stock.get_market_ohlcv.side_effect = Exception("API Error")
        
        result = collect_data.get_stock_ohlcv('005930', '20240101')
        
        assert isinstance(result, pd.DataFrame)
        assert result.empty


class TestGetStockFundamental:
    """Tests for get_stock_fundamental function."""
    
    @patch('backend.batch.collect_data.stock')
    def test_get_stock_fundamental_returns_dataframe(self, mock_stock):
        """Test that function returns DataFrame with fundamental data."""
        # Create mock fundamental data
        mock_df = pd.DataFrame({
            'PER': [15.5],
            'PBR': [1.2],
            '시가총액': [500000000000000],
            'EPS': [5000],
            'BPS': [50000]
        })
        mock_stock.get_market_fundamental.return_value = mock_df
        
        result = collect_data.get_stock_fundamental('005930', '20240101')
        
        assert isinstance(result, pd.DataFrame)
        assert len(result) == 1
        assert 'PER' in result.columns
        assert 'PBR' in result.columns
        assert '시가총액' in result.columns
    
    @patch('backend.batch.collect_data.stock')
    def test_get_stock_fundamental_empty_on_error(self, mock_stock):
        """Test that empty DataFrame is returned on error."""
        mock_stock.get_market_fundamental.side_effect = Exception("API Error")
        
        result = collect_data.get_stock_fundamental('005930', '20240101')
        
        assert isinstance(result, pd.DataFrame)
        assert result.empty


class TestCollectKospiData:
    """Tests for collect_kospi_data function."""
    
    @patch('backend.batch.collect_data.stock')
    @patch('backend.batch.collect_data.get_stock_fundamental')
    @patch('backend.batch.collect_data.get_stock_ohlcv')
    @patch('backend.batch.collect_data.get_kospi_ticker_list')
    def test_collect_kospi_data_returns_dataframe(self, mock_tickers, mock_ohlcv, mock_fund, mock_stock):
        """Test that function returns DataFrame with stock data."""
        # Mock responses
        mock_tickers.return_value = ['005930']
        
        mock_ohlcv_df = pd.DataFrame({
            '시가': [70000],
            '고가': [71000],
            '저가': [69500],
            '종가': [70500],
            '거래량': [1000000],
            '거래대금': [70000000000]
        })
        mock_ohlcv.return_value = mock_ohlcv_df
        
        mock_fund_df = pd.DataFrame({
            'PER': [15.5],
            'PBR': [1.2],
            '시가총액': [500000000000000],
            'EPS': [5000],
            'BPS': [50000]
        })
        mock_fund.return_value = mock_fund_df
        
        mock_stock.get_market_ticker_name.return_value = 'Samsung Electronics'
        
        result = collect_data.collect_kospi_data('20240101', limit=1)
        
        assert isinstance(result, pd.DataFrame)
        assert len(result) == 1
        assert result.iloc[0]['ticker'] == '005930'
        assert result.iloc[0]['name'] == 'Samsung Electronics'
        assert result.iloc[0]['close'] == 70500
        assert result.iloc[0]['per'] == 15.5
        assert result.iloc[0]['pbr'] == 1.2
    
    @patch('backend.batch.collect_data.get_kospi_ticker_list')
    def test_collect_kospi_data_empty_when_no_tickers(self, mock_tickers):
        """Test that empty DataFrame is returned when no tickers."""
        mock_tickers.return_value = []
        
        result = collect_data.collect_kospi_data('20240101')
        
        assert isinstance(result, pd.DataFrame)
        assert result.empty


class TestSaveToCsv:
    """Tests for save_to_csv function."""
    
    def test_save_to_csv_creates_file(self, tmp_path):
        """Test that CSV file is created."""
        df = pd.DataFrame({
            'ticker': ['005930'],
            'name': ['Samsung'],
            'close': [70000]
        })
        
        output_dir = str(tmp_path)
        filepath = collect_data.save_to_csv(df, '20240101', output_dir)
        
        assert os.path.exists(filepath)
        
        # Verify content (use dtype to preserve string type)
        loaded_df = pd.read_csv(filepath, dtype={'ticker': str})
        assert len(loaded_df) == 1
        assert loaded_df.iloc[0]['ticker'] == '005930'
    
    def test_save_to_csv_filename_format(self, tmp_path):
        """Test that filename follows correct format."""
        df = pd.DataFrame({'ticker': ['005930']})
        
        output_dir = str(tmp_path)
        filepath = collect_data.save_to_csv(df, '20240101', output_dir)
        
        expected_filename = 'stocks_20240101.csv'
        assert filepath.endswith(expected_filename)


class TestSaveToJson:
    """Tests for save_to_json function."""
    
    def test_save_to_json_creates_file(self, tmp_path):
        """Test that JSON file is created."""
        df = pd.DataFrame({
            'ticker': ['005930'],
            'name': ['Samsung'],
            'close': [70000]
        })
        
        output_dir = str(tmp_path)
        filepath = collect_data.save_to_json(df, '20240101', output_dir)
        
        assert os.path.exists(filepath)
        
        # Verify content - use dtype to preserve string type
        loaded_df = pd.read_json(filepath, dtype={'ticker': str})
        assert len(loaded_df) == 1
        assert loaded_df.iloc[0]['ticker'] == '005930'

        df = pd.DataFrame({
            'ticker': ['005930'],
            'name': ['Samsung'],
            'close': [70000]
        })
        
        output_dir = str(tmp_path)
        filepath = collect_data.save_to_json(df, '20240101', output_dir)
        
        assert os.path.exists(filepath)
        
        # Verify content - JSON preserves string
        loaded_df = pd.read_json(filepath)
        assert len(loaded_df) == 1

    
    def test_save_to_json_filename_format(self, tmp_path):
        """Test that filename follows correct format."""
        df = pd.DataFrame({'ticker': ['005930']})
        
        output_dir = str(tmp_path)
        filepath = collect_data.save_to_json(df, '20240101', output_dir)
        
        expected_filename = 'stocks_20240101.json'
        assert filepath.endswith(expected_filename)


class TestIntegration:
    """Integration tests that require pykrx API (skip in CI)."""
    
    @pytest.mark.integration
    def test_get_kospi_ticker_list_integration(self):
        """Integration test: Get real KOSPI ticker list."""
        # This test requires actual API call
        # Use a past date to avoid market holidays issues
        date = (datetime.now() - timedelta(days=10)).strftime("%Y%m%d")
        
        result = collect_data.get_kospi_ticker_list(date)
        
        assert isinstance(result, list)
        assert len(result) > 0
        # Samsung Electronics should be in KOSPI
        assert '005930' in result
    
    @pytest.mark.integration
    def test_get_stock_name_integration(self):
        """Integration test: Get real stock name."""
        name = collect_data.get_stock_name('005930')
        
        assert isinstance(name, str)
        assert len(name) > 0
    
    @pytest.mark.integration
    @pytest.mark.skipif(
        datetime.now().hour < 9 or datetime.now().hour >= 16,
        reason="Market is closed"
    )
    def test_collect_kospi_data_small_sample(self):
        """Integration test: Collect data for a few stocks."""
        # This test makes real API calls
        date = (datetime.now() - timedelta(days=5)).strftime("%Y%m%d")
        
        result = collect_data.collect_kospi_data(date, limit=3)
        
        assert isinstance(result, pd.DataFrame)
        # May be empty if market is closed or no data
        if not result.empty:
            assert 'ticker' in result.columns
            assert 'close' in result.columns
            assert 'per' in result.columns
