"""
Unit tests for stock recommendation algorithm.

Run tests:
    python -m pytest backend/tests/test_recommendation.py -v
"""

import os
import sys
from typing import Optional

import pandas as pd
import pytest

# Add backend to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from backend.app.services.recommendation import (
    calculate_value_score,
    calculate_growth_score,
    calculate_profitability_score,
    calculate_momentum_score,
    calculate_total_score,
    get_top_recommendations,
    get_top_recommendations_from_df,
    StockData,
    VALUE_WEIGHT,
    GROWTH_WEIGHT,
    PROFITABILITY_WEIGHT,
    MOMENTUM_WEIGHT,
)


class TestCalculateValueScore:
    """Tests for calculate_value_score function."""
    
    def test_value_score_perfect_perfect_pbr(self):
        """Test score for lowest PER and PBR (best value)."""
        score = calculate_value_score(1.0, 0.1)
        assert score is not None
        assert score > 90  # Very high score for excellent value
    
    def test_value_score_high_per_high_pbr(self):
        """Test score for highest PER and PBR (worst value)."""
        score = calculate_value_score(100.0, 10.0)
        assert score is not None
        assert score < 10  # Very low score for poor value
    
    def test_value_score_average(self):
        """Test score for average PER and PBR."""
        score = calculate_value_score(15.0, 1.5)
        assert score is not None
        assert 80 < score < 95  # Middle range
    
    def test_value_score_none_per(self):
        """Test score when PER is None."""
        score = calculate_value_score(None, 1.5)
        assert score is None
    
    def test_value_score_none_pbr(self):
        """Test score when PBR is None."""
        score = calculate_value_score(15.0, None)
        assert score is None
    
    def test_value_score_both_none(self):
        """Test score when both are None."""
        score = calculate_value_score(None, None)
        assert score is None
    
    def test_value_score_negative_per(self):
        """Test score with negative PER (invalid)."""
        score = calculate_value_score(-5.0, 1.5)
        assert score is None
    
    def test_value_score_zero_pbr(self):
        """Test score with zero PBR (invalid)."""
        score = calculate_value_score(15.0, 0.0)
        assert score is None
    
    def test_value_score_clamping(self):
        """Test that extreme values are clamped."""
        # Extreme high values should be clamped to max
        score_high = calculate_value_score(1000.0, 100.0)
        # Extreme low values should be clamped to min
        score_low = calculate_value_score(0.01, 0.01)
        
        assert score_high is not None
        assert score_low is not None
        # Low PER/PBR should give high scores (good value), high PER/PBR low scores
        assert score_high < 10  # High values = bad value = low score
        assert score_low > 90  # Low values = good value = high score


class TestCalculateGrowthScore:
    """Tests for calculate_growth_score function."""
    
    def test_growth_score_positive_growth(self):
        """Test score with positive EPS growth."""
        score = calculate_growth_score(5000, 20.0)
        assert score is not None
        # With EPS=5000 and growth=20%, score should be > 40
        assert score > 40
    
    def test_growth_score_negative_growth(self):
        """Test score with negative EPS growth."""
        score = calculate_growth_score(5000, -20.0)
        assert score is not None
        assert score < 50
    
    def test_growth_score_zero_growth(self):
        """Test score with zero EPS growth."""
        score = calculate_growth_score(5000, 0.0)
        assert score is not None
        # With EPS=5000 and growth=0%, score is below 50 due to EPS weight
        assert 30 < score < 50  # Close to neutral but affected by EPS
    
    def test_growth_score_only_eps(self):
        """Test score when only EPS is available."""
        score = calculate_growth_score(5000, None)
        assert score is not None
        assert 0 <= score <= 100
    
    def test_growth_score_none_eps(self):
        """Test score when EPS is None."""
        score = calculate_growth_score(None, 10.0)
        assert score is None
    
    def test_growth_score_both_none(self):
        """Test score when both are None."""
        score = calculate_growth_score(None, None)
        assert score is None
    
    def test_growth_score_extreme_positive(self):
        """Test score with extreme positive growth."""
        score = calculate_growth_score(100000, 100.0)
        assert score is not None
        assert score > 80
    
    def test_growth_score_extreme_negative(self):
        """Test score with extreme negative growth."""
        score = calculate_growth_score(-10000, -100.0)
        assert score is not None
        assert score < 20


class TestCalculateProfitabilityScore:
    """Tests for calculate_profitability_score function."""
    
    def test_profitability_score_high_roe(self):
        """Test score with high ROE."""
        score = calculate_profitability_score(25.0)
        assert score is not None
        assert score == 100  # Capped at 100
    
    def test_profitability_score_average_roe(self):
        """Test score with average ROE."""
        score = calculate_profitability_score(10.0)
        assert score is not None
        assert score == 50
    
    def test_profitability_score_zero_roe(self):
        """Test score with zero ROE."""
        score = calculate_profitability_score(0.0)
        assert score is not None
        assert score == 0
    
    def test_profitability_score_negative_roe(self):
        """Test score with negative ROE."""
        score = calculate_profitability_score(-10.0)
        assert score is not None
        assert score == 0  # Clamped to 0
    
    def test_profitability_score_none(self):
        """Test score when ROE is None."""
        score = calculate_profitability_score(None)
        assert score is None
    
    def test_profitability_score_clamping(self):
        """Test that extreme values are clamped."""
        score = calculate_profitability_score(100.0)
        assert score is not None
        assert score == 100  # Capped


class TestCalculateMomentumScore:
    """Tests for calculate_momentum_score function."""
    
    def test_momentum_score_positive(self):
        """Test score with positive momentum."""
        score = calculate_momentum_score(30.0)
        assert score is not None
        assert score == 80  # 50 + 30
    
    def test_momentum_score_zero(self):
        """Test score with zero momentum."""
        score = calculate_momentum_score(0.0)
        assert score is not None
        assert score == 50
    
    def test_momentum_score_negative(self):
        """Test score with negative momentum."""
        score = calculate_momentum_score(-30.0)
        assert score is not None
        assert score == 20  # 50 - 30
    
    def test_momentum_score_none(self):
        """Test score when price_change_3m is None."""
        score = calculate_momentum_score(None)
        assert score is None
    
    def test_momentum_score_clamping(self):
        """Test that extreme values are clamped."""
        score_pos = calculate_momentum_score(100.0)
        score_neg = calculate_momentum_score(-100.0)
        
        assert score_pos is not None
        assert score_neg is not None
        assert score_pos == 100  # Capped
        assert score_neg == 0  # Capped


class TestCalculateTotalScore:
    """Tests for calculate_total_score function."""
    
    def test_total_score_all_available(self):
        """Test score with all metrics available."""
        score = calculate_total_score(
            per=10.0,
            pbr=1.0,
            eps=5000,
            eps_growth=15.0,
            roe=15.0,
            price_change_3m=10.0,
        )
        assert score is not None
        assert 0 <= score <= 100
    
    def test_total_score_partial(self):
        """Test score with partial metrics."""
        score = calculate_total_score(
            per=10.0,
            pbr=1.0,
            eps=None,
            eps_growth=None,
            roe=None,
            price_change_3m=None,
        )
        assert score is not None
        assert 0 <= score <= 100
    
    def test_total_score_none(self):
        """Test score with no metrics."""
        score = calculate_total_score()
        assert score is None
    
    def test_total_score_single_metric(self):
        """Test score with only one metric."""
        score = calculate_total_score(
            per=10.0,
            pbr=1.0,
        )
        assert score is not None
        assert 0 <= score <= 100
    
    def test_total_score_weight_sum(self):
        """Test that weights sum correctly."""
        assert VALUE_WEIGHT == 0.40
        assert GROWTH_WEIGHT == 0.25
        assert PROFITABILITY_WEIGHT == 0.20
        assert MOMENTUM_WEIGHT == 0.15
        assert VALUE_WEIGHT + GROWTH_WEIGHT + PROFITABILITY_WEIGHT + MOMENTUM_WEIGHT == 1.0


class TestGetTopRecommendations:
    """Tests for get_top_recommendations function."""
    
    def test_get_top_recommendations_basic(self):
        """Test basic functionality."""
        stocks = [
            StockData(
                ticker='005930',
                name='Samsung Electronics',
                current_price=70000,
                change_rate=1.5,
                per=15.0,
                pbr=1.2,
                eps=5000,
                eps_growth=10.0,
                roe=15.0,
                price_change_3m=5.0,
            ),
            StockData(
                ticker='000001',
                name='SK Hynix',
                current_price=120000,
                change_rate=-0.5,
                per=8.0,
                pbr=0.8,
                eps=8000,
                eps_growth=25.0,
                roe=20.0,
                price_change_3m=15.0,
            ),
        ]
        
        result = get_top_recommendations(stocks, n=2)
        
        assert len(result) == 2
        assert result[0]['ticker'] == '000001'  # Should be higher score
        assert 'recommendation_score' in result[0]
    
    def test_get_top_recommendations_limit(self):
        """Test that result is limited to n."""
        stocks = [
            StockData(
                ticker=f'{i:06d}',
                name=f'Company {i}',
                current_price=10000,
                change_rate=0.0,
                per=10.0,
                pbr=1.0,
                eps=1000,
                eps_growth=5.0,
                roe=10.0,
                price_change_3m=0.0,
            )
            for i in range(50)
        ]
        
        result = get_top_recommendations(stocks, n=10)
        
        assert len(result) == 10
    
    def test_get_top_recommendations_min_threshold(self):
        """Test minimum score threshold."""
        stocks = [
            StockData(
                ticker='005930',
                name='High Score',
                current_price=70000,
                change_rate=1.5,
                per=5.0,
                pbr=0.5,
                eps=10000,
                eps_growth=30.0,
                roe=30.0,
                price_change_3m=20.0,
            ),
            StockData(
                ticker='000001',
                name='Low Score',
                current_price=10000,
                change_rate=-1.0,
                per=50.0,
                pbr=5.0,
                eps=100,
                eps_growth=-10.0,
                roe=1.0,
                price_change_3m=-20.0,
            ),
        ]
        
        result = get_top_recommendations(stocks, n=10, min_score_threshold=50.0)
        
        assert len(result) == 1
        assert result[0]['ticker'] == '005930'
    
    def test_get_top_recommendations_missing_data(self):
        """Test with missing data."""
        stocks = [
            StockData(
                ticker='005930',
                name='No Data',
                current_price=70000,
                change_rate=1.5,
                per=None,
                pbr=None,
                eps=None,
                eps_growth=None,
                roe=None,
                price_change_3m=None,
            ),
            StockData(
                ticker='000001',
                name='Full Data',
                current_price=10000,
                change_rate=0.0,
                per=10.0,
                pbr=1.0,
                eps=5000,
                eps_growth=10.0,
                roe=15.0,
                price_change_3m=5.0,
            ),
        ]
        
        result = get_top_recommendations(stocks, n=10)
        
        # Should only return stock with sufficient data
        assert len(result) == 1
        assert result[0]['ticker'] == '000001'
    
    def test_get_top_recommendations_empty(self):
        """Test with empty list."""
        result = get_top_recommendations([], n=10)
        assert result == []


class TestGetTopRecommendationsFromDf:
    """Tests for get_top_recommendations_from_df function."""
    
    def test_from_df_basic(self):
        """Test basic DataFrame input."""
        df = pd.DataFrame({
            'ticker': ['005930', '000001'],
            'name': ['Samsung', 'SK Hynix'],
            'close': [70000, 120000],
            'change_rate': [1.5, -0.5],
            'per': [15.0, 8.0],
            'pbr': [1.2, 0.8],
            'eps': [5000, 8000],
            'bps': [50000, 60000],
        })
        
        result = get_top_recommendations_from_df(df, n=2)
        
        assert isinstance(result, pd.DataFrame)
        assert len(result) == 2
        assert 'recommendation_score' in result.columns
    
    def test_from_df_empty(self):
        """Test with empty DataFrame."""
        df = pd.DataFrame()
        
        result = get_top_recommendations_from_df(df, n=10)
        
        assert isinstance(result, pd.DataFrame)
        assert len(result) == 0


class TestStockDataModel:
    """Tests for StockData model."""
    
    def test_stock_data_full(self):
        """Test StockData with all fields."""
        stock = StockData(
            ticker='005930',
            name='Samsung',
            current_price=70000,
            change_rate=1.5,
            per=15.0,
            pbr=1.2,
            market_cap=500000000000000,
            eps=5000,
            bps=50000,
            eps_growth=10.0,
            roe=15.0,
            price_change_3m=5.0,
        )
        
        assert stock.ticker == '005930'
        assert stock.per == 15.0
    
    def test_stock_data_minimal(self):
        """Test StockData with minimal fields."""
        stock = StockData(
            ticker='005930',
            name='Samsung',
            current_price=70000,
            change_rate=1.5,
        )
        
        assert stock.ticker == '005930'
        assert stock.per is None
    
    def test_stock_data_optional_fields(self):
        """Test that optional fields default to None."""
        stock = StockData(
            ticker='005930',
            name='Samsung',
            current_price=70000,
            change_rate=1.5,
        )
        
        assert stock.per is None
        assert stock.pbr is None
        assert stock.eps is None
        assert stock.eps_growth is None
        assert stock.roe is None
        assert stock.price_change_3m is None
