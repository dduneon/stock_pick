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
    # Basic financial indicators
    per: Optional[float] = Field(None, description="Price-to-Earnings Ratio")
    pbr: Optional[float] = Field(None, description="Price-to-Book Ratio")
    market_cap: Optional[float] = Field(None, description="Market capitalization")
    eps: Optional[float] = Field(None, description="Earnings per Share")
    bps: Optional[float] = Field(None, description="Book value per Share")
    
    # New fields (Wave 1 - Advanced Financial Indicators)
    forward_pe: Optional[float] = Field(None, description="Forward P/E ratio (선행 PER)")
    roe: Optional[float] = Field(None, description="Return on Equity (자기자본이익률) %")
    debt_ratio: Optional[float] = Field(None, description="Debt Ratio (부채비율) %")
    eps_growth_yoy: Optional[float] = Field(None, description="EPS Year-over-Year growth rate %")
    sector: Optional[str] = Field(None, description="Industry sector (업종)")
    
    class Config:
        from_attributes = True


class Recommendation(BaseModel):
    """Stock recommendation schema"""
    ticker: str = Field(..., description="Stock ticker symbol")
    name: str = Field(..., description="Company name")
    current_price: float = Field(..., description="Current stock price")
    change_rate: float = Field(..., description="Price change rate (%)")
    
    # Basic financial indicators
    per: Optional[float] = Field(None, description="Price-to-Earnings Ratio")
    pbr: Optional[float] = Field(None, description="Price-to-Book Ratio")
    market_cap: Optional[float] = Field(None, description="Market capitalization")
    eps: Optional[float] = Field(None, description="Earnings per Share")
    bps: Optional[float] = Field(None, description="Book value per Share")
    
    # New fields (Wave 1 - Advanced Financial Indicators)
    forward_pe: Optional[float] = Field(None, description="Forward P/E ratio (선행 PER)")
    roe: Optional[float] = Field(None, description="Return on Equity (자기자본이익률) %")
    debt_ratio: Optional[float] = Field(None, description="Debt Ratio (부채비율) %")
    eps_growth_yoy: Optional[float] = Field(None, description="EPS Year-over-Year growth rate %")
    sector: Optional[str] = Field(None, description="Industry sector (업종)")
    
    recommendation_score: Optional[float] = Field(None, description="Recommendation score")
    
    class Config:
        from_attributes = True
