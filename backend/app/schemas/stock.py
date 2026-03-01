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
    
    # New fields (Wave 3 - Comprehensive Financial Metrics)
    revenue: Optional[float] = Field(None, description="Annual revenue (매출액)")
    operating_profit: Optional[float] = Field(None, description="Operating profit (영업이익)")
    net_profit: Optional[float] = Field(None, description="Net profit (당기순이익)")
    operating_margin: Optional[float] = Field(None, description="Operating margin % (영업이익률)")
    net_margin: Optional[float] = Field(None, description="Net margin % (순이익률)")
    current_ratio: Optional[float] = Field(None, description="Current ratio % (당좌비율)")
    reserve_ratio: Optional[float] = Field(None, description="Reserve ratio % (유보율)")
    dividend_per_share: Optional[float] = Field(None, description="Dividend per share (주당배당금)")
    dividend_yield: Optional[float] = Field(None, description="Dividend yield % (시가배당률)")
    dividend_payout_ratio: Optional[float] = Field(None, description="Dividend payout ratio % (배당성향)")
    fiscal_year: Optional[str] = Field(None, description="Fiscal year of data (e.g., '2024.12')")
    
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
    
    # New fields (Wave 3 - Comprehensive Financial Metrics)
    revenue: Optional[float] = Field(None, description="Annual revenue (매출액)")
    operating_profit: Optional[float] = Field(None, description="Operating profit (영업이익)")
    net_profit: Optional[float] = Field(None, description="Net profit (당기순이익)")
    operating_margin: Optional[float] = Field(None, description="Operating margin % (영업이익률)")
    net_margin: Optional[float] = Field(None, description="Net margin % (순이익률)")
    current_ratio: Optional[float] = Field(None, description="Current ratio % (당좌비율)")
    reserve_ratio: Optional[float] = Field(None, description="Reserve ratio % (유보율)")
    dividend_per_share: Optional[float] = Field(None, description="Dividend per share (주당배당금)")
    dividend_yield: Optional[float] = Field(None, description="Dividend yield % (시가배당률)")
    dividend_payout_ratio: Optional[float] = Field(None, description="Dividend payout ratio % (배당성향)")
    fiscal_year: Optional[str] = Field(None, description="Fiscal year of data (e.g., '2024.12')")
    
    recommendation_score: Optional[float] = Field(None, description="Recommendation score")
    
    class Config:
        from_attributes = True
