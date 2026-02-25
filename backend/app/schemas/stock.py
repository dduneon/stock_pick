from pydantic import BaseModel, Field
from typing import Optional


class StockBase(BaseModel):
    """Base stock schema with common fields"""
    ticker: str = Field(..., description="Stock ticker symbol")
    name: str = Field(..., description="Company name")


class Stock(StockBase):
    """Stock schema for list responses"""
    current_price: float = Field(..., description="Current stock price")
    change_rate: float = Field(..., description="Price change rate (%)")
    
    class Config:
        from_attributes = True


class StockDetail(Stock):
    """Detailed stock schema with financial metrics"""
    per: Optional[float] = Field(None, description="Price-to-Earnings Ratio")
    pbr: Optional[float] = Field(None, description="Price-to-Book Ratio")
    market_cap: Optional[float] = Field(None, description="Market capitalization")
    eps: Optional[float] = Field(None, description="Earnings per Share")
    bps: Optional[float] = Field(None, description="Book value per Share")
    
    class Config:
        from_attributes = True


class Recommendation(BaseModel):
    """Stock recommendation schema"""
    ticker: str = Field(..., description="Stock ticker symbol")
    name: str = Field(..., description="Company name")
    current_price: float = Field(..., description="Current stock price")
    change_rate: float = Field(..., description="Price change rate (%)")
    per: Optional[float] = Field(None, description="Price-to-Earnings Ratio")
    pbr: Optional[float] = Field(None, description="Price-to-Book Ratio")
    market_cap: Optional[float] = Field(None, description="Market capitalization")
    eps: Optional[float] = Field(None, description="Earnings per Share")
    bps: Optional[float] = Field(None, description="Book value per Share")
    recommendation_score: Optional[float] = Field(None, description="Recommendation score")
    
    class Config:
        from_attributes = True
