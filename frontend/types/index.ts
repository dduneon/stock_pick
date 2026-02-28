/**
 * Stock-related TypeScript interfaces
 * Matches backend Pydantic schemas
 */

export interface Stock {
  /** Stock ticker symbol */
  ticker: string;
  /** Company name */
  name: string;
  /** Current stock price */
  current_price: number;
  /** Price change rate (%) */
  change_rate: number;
  /** Price-to-Earnings Ratio */
  per?: number;
  /** Price-to-Book Ratio */
  pbr?: number;
  /** Market capitalization */
  market_cap?: number;
  /** Earnings per Share */
  eps?: number;
  /** Book value per Share */
  bps?: number;
  
  // New fields (from Wave 1)
  /** Forward Price-to-Earnings Ratio (estimated) */
  forward_pe?: number;
  /** Return on Equity (%) */
  roe?: number;
  /** Debt ratio (%) */
  debt_ratio?: number;
  /** EPS growth year-over-year (%) */
  eps_growth_yoy?: number;
  /** Industry sector */
  sector?: string;
  
  // New fields (from Wave 2)
  /** Relative Strength Index (14-day) */
  rsi_14?: number;
  /** 5-day Moving Average */
  ma_5?: number;
  /** 20-day Moving Average */
  ma_20?: number;
  /** Price trend */
  trend?: 'uptrend' | 'downtrend' | 'sideways';
  /** Volume spike flag */
  volume_spike?: boolean;
  
  // Calculated
  /** Overall recommendation score */
  recommendation_score?: number;
}

export interface StockDetail extends Stock {
  // StockDetail inherits all fields from Stock
}

export interface Recommendation {
  /** Stock ticker symbol */
  ticker: string;
  /** Company name */
  name: string;
  /** Current stock price */
  current_price: number;
  /** Price change rate (%) */
  change_rate: number;
  /** Price-to-Earnings Ratio */
  per?: number;
  /** Price-to-Book Ratio */
  pbr?: number;
  /** Market capitalization */
  market_cap?: number;
  /** Earnings per Share */
  eps?: number;
  /** Book value per Share */
  bps?: number;
  /** Recommendation score */
  recommendation_score?: number;
}
