from typing import List, Optional
from fastapi import APIRouter, Query, HTTPException

from app.schemas.stock import Stock, StockDetail, Recommendation
from app.services import data_loader
from app.services.recommendation import (
    get_top_recommendations_from_df,
    get_top_recommendations,
    StockData,
    calculate_total_score,
)

router = APIRouter(prefix="/api", tags=["stocks"])


@router.get("/stocks", response_model=List[StockDetail])
def get_stocks(limit: Optional[int] = Query(None, description="Maximum number of results")):
    """
    Get list of all stocks.
    
    - **limit**: Optional limit for number of results (for MVP, no pagination)
    """
    stocks = data_loader.get_all_stocks(limit=limit)
    return stocks


@router.get("/stocks/{ticker}", response_model=StockDetail)
def get_stock_detail(ticker: str):
    """
    Get detailed stock information by ticker.
    
    - **ticker**: Stock ticker code (e.g., '005930')
    """
    stock = data_loader.get_stock_by_ticker(ticker)
    
    if not stock:
        raise HTTPException(status_code=404, detail=f"Stock with ticker '{ticker}' not found")
    
    return stock


@router.get("/recommendations", response_model=List[Recommendation])
def get_recommendations(
    limit: Optional[int] = Query(20, description="Maximum number of recommendations"),
    min_score: Optional[float] = Query(0.0, description="Minimum recommendation score"),
):
    """
    Get top stock recommendations based on scoring algorithm.
    
    - **limit**: Maximum number of recommendations to return (default: 20)
    - **min_score**: Minimum recommendation score threshold (default: 0)
    
    Scoring is based on:
    - Value (40%): PER, PBR based (lower is better)
    - Growth (25%): EPS growth rate
    - Profitability (20%): ROE
    - Momentum (15%): 3-month return
    """
    # Load all stock data
    import pandas as pd
    df = data_loader.load_stocks_data()
    
    if df.empty:
        return []
    
    # Get recommendations using the recommendation service
    recommendations_df = get_top_recommendations_from_df(
        df,
        n=limit,
        min_score_threshold=min_score,
    )
    
    if recommendations_df.empty:
        return []
    
    # Convert to list of dicts
    result = []
    for _, row in recommendations_df.iterrows():
        rec = {
            "ticker": str(row.get("ticker", "")),
            "name": str(row.get("name", "")),
            "current_price": float(row.get("current_price", 0)),
            "change_rate": float(row.get("change_rate", 0)),
            "per": row.get("per"),
            "pbr": row.get("pbr"),
            "market_cap": row.get("market_cap"),
            "eps": row.get("eps"),
            "bps": row.get("bps"),
            "recommendation_score": row.get("recommendation_score"),
        }
        result.append(rec)
    
    return result


@router.get("/search", response_model=List[Stock])
def search_stocks(q: str = Query(..., description="Search query (company name)")):
    """
    Search stocks by company name.
    
    - **q**: Search query string (partial match supported)
    """
    if not q or len(q.strip()) < 1:
        return []
    
    stocks = data_loader.search_stocks(q.strip())
    return stocks


@router.get("/stocks/{ticker}/technical")
def get_technical_indicators(ticker: str):
    """
    Get technical indicators for a stock.
    
    Returns:
    - moving_averages: {ma_5, ma_20, ma_60, ma_120}
    - rsi: {value, signal}
    - volume: {current, ma_20, spike_detected}
    - trend: uptrend/downtrend/sideways
    """
    from app.services.technical_analysis import analyze_stock
    
    result = analyze_stock(ticker)
    
    if 'error' in result:
        raise HTTPException(status_code=404, detail=result['error'])
    
    return result['indicators']


@router.get("/stocks/{ticker}/chart")
def get_chart_data(ticker: str, period: str = "3m"):
    """
    Get OHLCV + indicators data for chart rendering.
    
    period: "1m" | "3m" | "6m" | "1y"
    """
    from app.services.technical_analysis import analyze_stock
    
    days_map = {
        "1m": 30,
        "3m": 90,
        "6m": 180,
        "1y": 365
    }
    days = days_map.get(period, 90)
    
    result = analyze_stock(ticker, days)
    
    if 'error' in result:
        raise HTTPException(status_code=404, detail=result['error'])
    
    return {
        'ticker': ticker,
        'period': period,
        'data': result['chart_data']
    }
