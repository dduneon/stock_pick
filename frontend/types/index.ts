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
}

export interface StockDetail extends Stock {
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
