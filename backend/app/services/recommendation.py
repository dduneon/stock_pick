"""
Stock Recommendation Service

Scoring algorithm for stock recommendations:
- Value (40%): PER, PBR based (lower is better)
- Growth (25%): EPS growth rate
- Profitability (20%): ROE
- Momentum (15%): 3-month return

Usage:
    from backend.app.services.recommendation import (
        calculate_value_score,
        calculate_growth_score,
        calculate_profitability_score,
        calculate_momentum_score,
        calculate_total_score,
        get_top_recommendations,
    )
"""

from typing import List, Optional, Dict, Any
import numpy as np
import pandas as pd
from pydantic import BaseModel


# Weight configuration
VALUE_WEIGHT = 0.40
GROWTH_WEIGHT = 0.25
PROFITABILITY_WEIGHT = 0.20
MOMENTUM_WEIGHT = 0.15

# Score bounds for normalization
MIN_VALID_PER = 0.1
MAX_VALID_PER = 100.0
MIN_VALID_PBR = 0.1
MAX_VALID_PBR = 10.0
MIN_VALID_EPS = -10000
MAX_VALID_EPS = 100000
MIN_VALID_ROE = -50
MAX_VALID_ROE = 50
MIN_VALID_MOMENTUM = -50
MAX_VALID_MOMENTUM = 50


class StockData(BaseModel):
    """Stock data model for recommendation calculation."""
    ticker: str
    name: str
    current_price: float
    change_rate: float
    per: Optional[float] = None
    pbr: Optional[float] = None
    market_cap: Optional[float] = None
    eps: Optional[float] = None
    bps: Optional[float] = None
    eps_growth: Optional[float] = None  # EPS growth rate (%)
    roe: Optional[float] = None  # Return on Equity (%)
    price_change_3m: Optional[float] = None  # 3-month price change (%)


def calculate_value_score(per: Optional[float], pbr: Optional[float]) -> Optional[float]:
    """
    Calculate value score based on PER and PBR.
    
    Lower PER and PBR are better (undervalued).
    Score range: 0-100 (100 is best, i.e., most undervalued).
    
    Args:
        per: Price-to-Earnings Ratio
        pbr: Price-to-Book Ratio
    
    Returns:
        Value score (0-100) or None if data insufficient
    """
    if per is None or pbr is None:
        return None
    
    # Validate inputs
    if per <= 0 or pbr <= 0:
        return None
    
    # Clamp values to reasonable range
    per_clamped = max(MIN_VALID_PER, min(MAX_VALID_PER, per))
    pbr_clamped = max(MIN_VALID_PBR, min(MAX_VALID_PBR, pbr))
    
    # Normalize to 0-100 (lower is better -> invert)
    # PER: lower is better (0-100)
    per_score = 100 * (1 - (per_clamped - MIN_VALID_PER) / (MAX_VALID_PER - MIN_VALID_PER))
    
    # PBR: lower is better (0-100)
    pbr_score = 100 * (1 - (pbr_clamped - MIN_VALID_PBR) / (MAX_VALID_PBR - MIN_VALID_PBR))
    
    # Average of PER and PBR scores (equal weight)
    value_score = (per_score + pbr_score) / 2
    
    # Clamp to 0-100 range
    return max(0.0, min(100.0, value_score))


def calculate_growth_score(eps: Optional[float], eps_growth: Optional[float]) -> Optional[float]:
    """
    Calculate growth score based on EPS and EPS growth rate.
    
    Higher EPS and positive growth are better.
    Score range: 0-100 (100 is best).
    
    Args:
        eps: Earnings per Share
        eps_growth: EPS growth rate (%)
    
    Returns:
        Growth score (0-100) or None if data insufficient
    """
    if eps is None or eps_growth is None:
        # If only EPS available, use as indicator (higher EPS = more profitable)
        if eps is not None:
            eps_clamped = max(MIN_VALID_EPS, min(MAX_VALID_EPS, eps))
            eps_score = 100 * (eps_clamped - MIN_VALID_EPS) / (MAX_VALID_EPS - MIN_VALID_EPS)
            return max(0.0, min(100.0, eps_score))
        return None
    
    # Normalize EPS (higher is better)
    eps_clamped = max(MIN_VALID_EPS, min(MAX_VALID_EPS, eps))
    eps_score = 100 * (eps_clamped - MIN_VALID_EPS) / (MAX_VALID_EPS - MIN_VALID_EPS)
    
    # Normalize growth rate (higher is better, can be negative)
    # Map -100% to 0, 0% to 50, +100% to 100
    growth_clamped = max(-100.0, min(100.0, eps_growth))
    growth_score = 50 + (growth_clamped / 2)  # -100 -> 0, 0 -> 50, 100 -> 100
    
    # Weighted average: 40% absolute EPS, 60% growth rate
    growth_score_final = eps_score * 0.4 + growth_score * 0.6
    
    return max(0.0, min(100.0, growth_score_final))


def calculate_profitability_score(roe: Optional[float]) -> Optional[float]:
    """
    Calculate profitability score based on ROE.
    
    Higher ROE is better.
    Score range: 0-100 (100 is best).
    
    Args:
        roe: Return on Equity (%)
    
    Returns:
        Profitability score (0-100) or None if data insufficient
    """
    if roe is None:
        return None
    
    # Clamp to reasonable range
    roe_clamped = max(MIN_VALID_ROE, min(MAX_VALID_ROE, roe))
    
    # Normalize: 0% ROE -> 0, 20% ROE -> 100
    # ROE above 20% is excellent (capped at 100)
    profitability_score = 100 * roe_clamped / 20.0
    
    return max(0.0, min(100.0, profitability_score))


def calculate_momentum_score(price_change_3m: Optional[float]) -> Optional[float]:
    """
    Calculate momentum score based on 3-month price change.
    
    Positive momentum is better, but extreme may indicate risk.
    Score range: 0-100 (100 is best).
    
    Args:
        price_change_3m: 3-month price change (%)
    
    Returns:
        Momentum score (0-100) or None if data insufficient
    """
    if price_change_3m is None:
        return None
    
    # Clamp to reasonable range
    momentum_clamped = max(MIN_VALID_MOMENTUM, min(MAX_VALID_MOMENTUM, price_change_3m))
    
    # Normalize: -50% -> 0, 0% -> 50, +50% -> 100
    momentum_score = 50 + momentum_clamped
    
    return max(0.0, min(100.0, momentum_score))


def calculate_total_score(
    per: Optional[float] = None,
    pbr: Optional[float] = None,
    eps: Optional[float] = None,
    eps_growth: Optional[float] = None,
    roe: Optional[float] = None,
    price_change_3m: Optional[float] = None,
) -> Optional[float]:
    """
    Calculate total recommendation score with weighted average.
    
    Weights:
    - Value (PER, PBR): 40%
    - Growth (EPS, EPS growth): 25%
    - Profitability (ROE): 20%
    - Momentum (3-month return): 15%
    
    Args:
        per: Price-to-Earnings Ratio
        pbr: Price-to-Book Ratio
        eps: Earnings per Share
        eps_growth: EPS growth rate (%)
        roe: Return on Equity (%)
        price_change_3m: 3-month price change (%)
    
    Returns:
        Total score (0-100) or None if insufficient data
    """
    value_score = calculate_value_score(per, pbr)
    growth_score = calculate_growth_score(eps, eps_growth)
    profitability_score = calculate_profitability_score(roe)
    momentum_score = calculate_momentum_score(price_change_3m)
    
    # Collect available scores with their weights
    scores_with_weights = []
    
    if value_score is not None:
        scores_with_weights.append((value_score, VALUE_WEIGHT))
    if growth_score is not None:
        scores_with_weights.append((growth_score, GROWTH_WEIGHT))
    if profitability_score is not None:
        scores_with_weights.append((profitability_score, PROFITABILITY_WEIGHT))
    if momentum_score is not None:
        scores_with_weights.append((momentum_score, MOMENTUM_WEIGHT))
    
    if not scores_with_weights:
        return None
    
    # Calculate weighted average
    total_score = sum(score * weight for score, weight in scores_with_weights)
    total_weight = sum(weight for _, weight in scores_with_weights)
    
    # Normalize by actual weight used
    normalized_score = (total_score / total_weight) * total_weight if total_weight > 0 else 0
    
    return max(0.0, min(100.0, normalized_score))


def get_top_recommendations(
    stocks: List[StockData],
    n: int = 20,
    min_score_threshold: float = 0.0,
) -> List[Dict[str, Any]]:
    """
    Get top N stock recommendations based on total score.
    
    Args:
        stocks: List of stock data
        n: Number of recommendations to return
        min_score_threshold: Minimum score to include (default: 0)
    
    Returns:
        List of stock recommendations sorted by score (descending)
    """
    recommendations = []
    
    for stock in stocks:
        # Calculate score for each stock
        score = calculate_total_score(
            per=stock.per,
            pbr=stock.pbr,
            eps=stock.eps,
            eps_growth=stock.eps_growth,
            roe=stock.roe,
            price_change_3m=stock.price_change_3m,
        )
        
        if score is None or score < min_score_threshold:
            continue
        
        recommendations.append({
            'ticker': stock.ticker,
            'name': stock.name,
            'current_price': stock.current_price,
            'change_rate': stock.change_rate,
            'per': stock.per,
            'pbr': stock.pbr,
            'eps': stock.eps,
            'eps_growth': stock.eps_growth,
            'roe': stock.roe,
            'price_change_3m': stock.price_change_3m,
            'recommendation_score': round(score, 2),
            'value_score': calculate_value_score(stock.per, stock.pbr),
            'growth_score': calculate_growth_score(stock.eps, stock.eps_growth),
            'profitability_score': calculate_profitability_score(stock.roe),
            'momentum_score': calculate_momentum_score(stock.price_change_3m),
        })
    
    # Sort by score descending
    recommendations.sort(key=lambda x: x['recommendation_score'], reverse=True)
    
    return recommendations[:n]


def get_top_recommendations_from_df(
    df: pd.DataFrame,
    n: int = 20,
    min_score_threshold: float = 0.0,
) -> pd.DataFrame:
    """
    Get top N stock recommendations from DataFrame.
    
    Args:
        df: DataFrame with stock data columns
        n: Number of recommendations to return
        min_score_threshold: Minimum score to include
    
    Returns:
        DataFrame with top recommendations
    """
    # Convert DataFrame to list of StockData
    stocks = []
    for _, row in df.iterrows():
        stock = StockData(
            ticker=str(row.get('ticker', '')),
            name=str(row.get('name', '')),
            current_price=float(row.get('close', 0)) if pd.notna(row.get('close')) else 0.0,
            change_rate=float(row.get('change_rate', 0)) if pd.notna(row.get('change_rate')) else 0.0,
            per=float(row['per']) if pd.notna(row.get('per')) else None,
            pbr=float(row['pbr']) if pd.notna(row.get('pbr')) else None,
            market_cap=float(row['market_cap']) if pd.notna(row.get('market_cap')) else None,
            eps=float(row['eps']) if pd.notna(row.get('eps')) else None,
            bps=float(row['bps']) if pd.notna(row.get('bps')) else None,
        )
        stocks.append(stock)
    
    recommendations = get_top_recommendations(stocks, n, min_score_threshold)
    
    if not recommendations:
        return pd.DataFrame()
    
    return pd.DataFrame(recommendations)
