# Comprehensive Financial Data Structure Design

**Task**: Task 2 - Design Comprehensive Data Structure  
**Plan**: naver-crawler-comprehensive  
**Date**: 2026-03-01  
**Author**: Sisyphus-Junior  

---

## Overview

This document defines the comprehensive data structure for extracting financial metrics from Naver Finance's 기업실적분석 table (주요재무정보). The design supports 15+ financial metrics organized into logical groups for clarity and extensibility.

## Design Principles

1. **Optional Fields**: All numeric fields use `Optional[float]` to handle missing data gracefully
2. **Logical Grouping**: Metrics organized by financial category (profitability, balance sheet, valuation, dividend)
3. **Extensibility**: Clear pattern for adding new metrics in the future
4. **Metadata Support**: Includes fiscal year and other metadata fields
5. **Consistency**: All field names use snake_case English, descriptions include Korean for context

---

## Metric Groupings and Rationale

### 1. Profitability Group

**Rationale**: These metrics measure the company's ability to generate profits from its operations. They are fundamental indicators of business health and operational efficiency.

| Field Name | Type | Korean Label | Description |
|------------|------|--------------|-------------|
| `revenue` | `Optional[float]` | 매출액 | Annual revenue in millions/billions KRW |
| `operating_profit` | `Optional[float]` | 영업이익 | Operating profit (core business earnings) |
| `net_profit` | `Optional[float]` | 당기순이익 | Net profit (bottom line earnings) |
| `operating_margin` | `Optional[float]` | 영업이익률 | Operating margin percentage |
| `net_margin` | `Optional[float]` | 순이익률 | Net margin percentage |
| `roe` | `Optional[float]` | ROE | Return on Equity percentage |

**Why group together**: These metrics tell the complete profitability story - from top-line revenue through to bottom-line profit, with efficiency ratios to understand how well the company converts revenue to profit.

### 2. Balance Sheet Group

**Rationale**: These metrics assess the company's financial stability, liquidity, and capital structure. They indicate how well the company manages its assets and liabilities.

| Field Name | Type | Korean Label | Description |
|------------|------|--------------|-------------|
| `debt_ratio` | `Optional[float]` | 부채비율 | Debt ratio percentage (total liabilities / total equity) |
| `current_ratio` | `Optional[float]` | 당좌비율 | Current ratio percentage (current assets / current liabilities) |
| `reserve_ratio` | `Optional[float]` | 유보율 | Reserve ratio percentage (retained earnings / capital) |

**Why group together**: These are all balance sheet-derived metrics that measure different aspects of financial health: leverage (debt_ratio), short-term liquidity (current_ratio), and accumulated wealth (reserve_ratio).

### 3. Valuation Group

**Rationale**: These metrics help investors understand how the market values the company relative to its earnings and book value. Essential for investment decisions.

| Field Name | Type | Korean Label | Description |
|------------|------|--------------|-------------|
| `per` | `Optional[float]` | PER | Price-to-Earnings ratio |
| `pbr` | `Optional[float]` | PBR | Price-to-Book ratio |
| `eps` | `Optional[float]` | EPS | Earnings per Share |
| `bps` | `Optional[float]` | BPS | Book value per Share |

**Why group together**: These are the core valuation multiples and per-share metrics that investors use to compare companies and assess relative value.

### 4. Dividend Group

**Rationale**: These metrics indicate the company's dividend policy and yield, important for income-focused investors.

| Field Name | Type | Korean Label | Description |
|------------|------|--------------|-------------|
| `dividend_per_share` | `Optional[float]` | 주당배당금 | Dividend per share (annual) |
| `dividend_yield` | `Optional[float]` | 시가배당률 | Dividend yield percentage |
| `dividend_payout_ratio` | `Optional[float]` | 배당성향 | Dividend payout ratio percentage |

**Why group together**: These three metrics provide a complete picture of dividend policy: absolute amount, yield relative to price, and sustainability (payout ratio).

### 5. Growth Group

**Rationale**: Growth metrics show how the company is expanding over time. Currently includes EPS growth as a key indicator.

| Field Name | Type | Korean Label | Description |
|------------|------|--------------|-------------|
| `eps_growth_yoy` | `Optional[float]` | EPS증가율 | EPS year-over-year growth percentage |

**Why group together**: Growth metrics are calculated rather than directly extracted. They provide trend analysis capability.

### 6. Metadata Group

**Rationale**: Contextual information about when the data was reported and its validity period.

| Field Name | Type | Description |
|------------|------|-------------|
| `fiscal_year` | `Optional[str]` | Fiscal year of data (e.g., '2024.12', '2025.12(E)') |

**Why group together**: Metadata fields provide context for interpreting the financial metrics and help track data freshness.

---

## Complete Pydantic Schema Design

### Option 1: Flat Structure (Recommended for Simplicity)

```python
from pydantic import BaseModel, Field
from typing import Optional


class StockFinancialMetrics(BaseModel):
    """
    Comprehensive financial metrics for a stock.
    
    Extracted from Naver Finance 기업실적분석 table (주요재무정보).
    All numeric fields are Optional[float] to handle missing data gracefully.
    """
    
    # =========================================================================
    # Profitability Metrics
    # =========================================================================
    revenue: Optional[float] = Field(
        None, 
        description="Annual revenue (매출액) in millions/billions KRW"
    )
    operating_profit: Optional[float] = Field(
        None, 
        description="Operating profit (영업이익) - core business earnings"
    )
    net_profit: Optional[float] = Field(
        None, 
        description="Net profit (당기순이익) - bottom line earnings"
    )
    operating_margin: Optional[float] = Field(
        None, 
        description="Operating margin %% (영업이익률) - operating profit / revenue"
    )
    net_margin: Optional[float] = Field(
        None, 
        description="Net margin %% (순이익률) - net profit / revenue"
    )
    roe: Optional[float] = Field(
        None, 
        description="Return on Equity %% (자기자본이익률) - net profit / equity"
    )
    
    # =========================================================================
    # Balance Sheet Metrics
    # =========================================================================
    debt_ratio: Optional[float] = Field(
        None, 
        description="Debt ratio %% (부채비율) - total liabilities / equity"
    )
    current_ratio: Optional[float] = Field(
        None, 
        description="Current ratio %% (당좌비율) - current assets / current liabilities"
    )
    reserve_ratio: Optional[float] = Field(
        None, 
        description="Reserve ratio %% (유보율) - retained earnings / capital"
    )
    
    # =========================================================================
    # Valuation Metrics
    # =========================================================================
    per: Optional[float] = Field(
        None, 
        description="Price-to-Earnings ratio (PER) - price / EPS"
    )
    pbr: Optional[float] = Field(
        None, 
        description="Price-to-Book ratio (PBR) - price / BPS"
    )
    eps: Optional[float] = Field(
        None, 
        description="Earnings per Share (EPS) - net profit / shares outstanding"
    )
    bps: Optional[float] = Field(
        None, 
        description="Book value per Share (BPS) - equity / shares outstanding"
    )
    
    # =========================================================================
    # Dividend Metrics
    # =========================================================================
    dividend_per_share: Optional[float] = Field(
        None, 
        description="Dividend per share (주당배당금) - annual dividend amount"
    )
    dividend_yield: Optional[float] = Field(
        None, 
        description="Dividend yield %% (시가배당률) - dividend / price"
    )
    dividend_payout_ratio: Optional[float] = Field(
        None, 
        description="Dividend payout ratio %% (배당성향) - dividend / EPS"
    )
    
    # =========================================================================
    # Growth Metrics
    # =========================================================================
    eps_growth_yoy: Optional[float] = Field(
        None, 
        description="EPS year-over-year growth %% (EPS증가율)"
    )
    
    # =========================================================================
    # Metadata
    # =========================================================================
    fiscal_year: Optional[str] = Field(
        None, 
        description="Fiscal year of data (e.g., '2024.12', '2025.12(E)')"
    )
    
    class Config:
        from_attributes = True
```

### Option 2: Nested Group Structure (For Future Extensibility)

```python
from pydantic import BaseModel, Field
from typing import Optional


class ProfitabilityMetrics(BaseModel):
    """Profitability and income statement metrics."""
    revenue: Optional[float] = Field(None, description="Annual revenue (매출액)")
    operating_profit: Optional[float] = Field(None, description="Operating profit (영업이익)")
    net_profit: Optional[float] = Field(None, description="Net profit (당기순이익)")
    operating_margin: Optional[float] = Field(None, description="Operating margin %% (영업이익률)")
    net_margin: Optional[float] = Field(None, description="Net margin %% (순이익률)")
    roe: Optional[float] = Field(None, description="Return on Equity %%")


class BalanceSheetMetrics(BaseModel):
    """Balance sheet health metrics."""
    debt_ratio: Optional[float] = Field(None, description="Debt ratio %% (부채비율)")
    current_ratio: Optional[float] = Field(None, description="Current ratio %% (당좌비율)")
    reserve_ratio: Optional[float] = Field(None, description="Reserve ratio %% (유보율)")


class ValuationMetrics(BaseModel):
    """Market valuation metrics."""
    per: Optional[float] = Field(None, description="Price-to-Earnings ratio")
    pbr: Optional[float] = Field(None, description="Price-to-Book ratio")
    eps: Optional[float] = Field(None, description="Earnings per Share")
    bps: Optional[float] = Field(None, description="Book value per Share")


class DividendMetrics(BaseModel):
    """Dividend policy metrics."""
    dividend_per_share: Optional[float] = Field(None, description="Dividend per share (주당배당금)")
    dividend_yield: Optional[float] = Field(None, description="Dividend yield %% (시가배당률)")
    dividend_payout_ratio: Optional[float] = Field(None, description="Dividend payout ratio %% (배당성향)")


class GrowthMetrics(BaseModel):
    """Growth and trend metrics."""
    eps_growth_yoy: Optional[float] = Field(None, description="EPS year-over-year growth %%")


class FinancialMetadata(BaseModel):
    """Metadata about the financial data."""
    fiscal_year: Optional[str] = Field(None, description="Fiscal year (e.g., '2024.12')")


class ComprehensiveFinancialData(BaseModel):
    """
    Complete financial data structure with nested groups.
    
    Use this structure for API responses where grouping aids clarity.
    """
    profitability: ProfitabilityMetrics = Field(default_factory=ProfitabilityMetrics)
    balance_sheet: BalanceSheetMetrics = Field(default_factory=BalanceSheetMetrics)
    valuation: ValuationMetrics = Field(default_factory=ValuationMetrics)
    dividend: DividendMetrics = Field(default_factory=DividendMetrics)
    growth: GrowthMetrics = Field(default_factory=GrowthMetrics)
    metadata: FinancialMetadata = Field(default_factory=FinancialMetadata)
```

---

## Field Extraction Mapping

This table maps HTML table row names to the schema fields:

| HTML Row Name (Korean) | Schema Field | Extraction Strategy |
|------------------------|--------------|---------------------|
| 매출액 | `revenue` | Latest annual value |
| 영업이익 | `operating_profit` | Latest annual value |
| 당기순이익 | `net_profit` | Latest annual value |
| 영업이익률 | `operating_margin` | Latest annual value |
| 순이익률 | `net_margin` | Latest annual value |
| ROE / ROE(지배주주) | `roe` | Latest annual value |
| 부채비율 | `debt_ratio` | Latest annual value |
| 당좌비율 | `current_ratio` | Latest annual value |
| 유보율 | `reserve_ratio` | Latest annual value |
| PER / PER(배) | `per` | Latest annual value |
| PBR / PBR(배) | `pbr` | Latest annual value |
| EPS / EPS(원) | `eps` | Latest annual value |
| BPS / BPS(원) | `bps` | Latest annual value |
| 주당배당금 | `dividend_per_share` | Latest annual value |
| 시가배당률 | `dividend_yield` | Latest annual value |
| 배당성향 | `dividend_payout_ratio` | Latest annual value |
| *Calculated* | `eps_growth_yoy` | `(EPS_current - EPS_previous) / EPS_previous * 100` |
| Column header | `fiscal_year` | Extract from column header (e.g., '2024.12') |

---

## Data Quality Considerations

### Missing Data Handling
- Naver Finance shows `'-'` or empty cells for missing values
- All fields are `Optional[float]` to represent missing data as `None`
- Extraction functions must handle `'-'`, empty strings, and malformed values

### Numeric Parsing
- Revenue values may include commas (e.g., '1,234,567')
- Some values may have HTML tags (e.g., `<em class="f_up">-77,303</em>`)
- Percentage values are stored as numbers (e.g., 15.5 for 15.5%), not strings
- Very large numbers (trillions) must be handled correctly

### Fiscal Year Formats
- Standard: `'2024.12'` (December year-end)
- Estimates: `'2025.12(E)'` (estimated values)
- Must be stored as string to preserve the '(E)' indicator

### Edge Cases
1. **Newly listed companies**: May have only 1-2 years of data
2. **Loss-making companies**: Negative operating profit or net profit
3. **Zero EPS**: Avoid division by zero in growth calculations
4. **Missing entire rows**: Some companies lack certain metrics entirely

---

## Extensibility Guide

### Adding New Metrics

To add a new metric in the future:

1. **Add to schema**:
   ```python
   new_metric: Optional[float] = Field(
       None, 
       description="New metric description (Korean label)"
   )
   ```

2. **Add to extraction mapping**:
   ```python
   'new_metric': ['Korean Label', 'Alternative Label'],
   ```

3. **Add to crawler**:
   ```python
   result['new_metric'] = _extract_metric(annual_df, ['Korean Label'])
   ```

4. **Add to batch collection**:
   ```python
   'new_metric': quote.get('new_metric'),
   ```

5. **Add to data loader**:
   ```python
   new_metric=parse_float(row.get('new_metric')),
   ```

### New Metric Categories

If adding a new category (e.g., Cash Flow metrics):

1. Create a new group in the design document
2. Add fields to the appropriate schema section
3. Document the grouping rationale
4. Update extraction mapping

---

## Integration with Existing Code

### Current Schema (StockDetail)
The existing `StockDetail` schema already includes:
- `per`, `pbr`, `eps`, `bps`, `market_cap`
- `forward_pe`, `roe`, `debt_ratio`, `eps_growth_yoy`, `sector`

### Migration Plan
The new comprehensive metrics will be **added** to the existing schema (no removal):

```python
class StockDetail(Stock):
    """Detailed stock schema with comprehensive financial metrics."""
    
    # Existing fields (keep all)
    per: Optional[float] = Field(None, description="Price-to-Earnings Ratio")
    pbr: Optional[float] = Field(None, description="Price-to-Book Ratio")
    market_cap: Optional[float] = Field(None, description="Market capitalization")
    eps: Optional[float] = Field(None, description="Earnings per Share")
    bps: Optional[float] = Field(None, description="Book value per Share")
    forward_pe: Optional[float] = Field(None, description="Forward P/E ratio")
    roe: Optional[float] = Field(None, description="Return on Equity")
    debt_ratio: Optional[float] = Field(None, description="Debt Ratio")
    eps_growth_yoy: Optional[float] = Field(None, description="EPS growth rate")
    sector: Optional[str] = Field(None, description="Industry sector")
    
    # New comprehensive metrics
    revenue: Optional[float] = Field(None, description="Annual revenue (매출액)")
    operating_profit: Optional[float] = Field(None, description="Operating profit (영업이익)")
    net_profit: Optional[float] = Field(None, description="Net profit (당기순이익)")
    operating_margin: Optional[float] = Field(None, description="Operating margin %%")
    net_margin: Optional[float] = Field(None, description="Net margin %%")
    current_ratio: Optional[float] = Field(None, description="Current ratio %% (당좌비율)")
    reserve_ratio: Optional[float] = Field(None, description="Reserve ratio %% (유보율)")
    dividend_per_share: Optional[float] = Field(None, description="Dividend per share")
    dividend_yield: Optional[float] = Field(None, description="Dividend yield %%")
    dividend_payout_ratio: Optional[float] = Field(None, description="Dividend payout ratio %%")
    fiscal_year: Optional[str] = Field(None, description="Fiscal year (e.g., '2024.12')")
```

---

## Validation Checklist

- [x] All 15+ metrics mapped with types
- [x] Grouping rationale documented
- [x] All numeric fields use `Optional[float]`
- [x] Metadata fields included (`fiscal_year`)
- [x] Pydantic `Field()` with descriptions
- [x] HTML-to-field mapping documented
- [x] Data quality considerations documented
- [x] Extensibility guide provided
- [x] Integration plan with existing schema
- [x] Korean labels included in descriptions

---

## Summary

This design provides a comprehensive, extensible data structure for Naver Finance financial metrics. The flat structure (Option 1) is recommended for initial implementation due to its simplicity and compatibility with the existing codebase. The nested structure (Option 2) can be considered for future API versions where grouped responses are preferred.

**Total Metrics**: 18 fields (15 financial + 3 existing retained)
**Type Safety**: All numeric fields are `Optional[float]`
**Data Source**: Naver Finance 기업실적분석 table (주요재무정보)
**Extraction Method**: pandas `read_html(match='주요재무정보')`
