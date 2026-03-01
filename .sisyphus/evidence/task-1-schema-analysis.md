# Schema Analysis Report - Wave 1 Naver Crawler Implementation

**Date:** 2026-03-01  
**Scope:** Backend schemas, data loading, and collection flow analysis  
**Files Analyzed:**
- `backend/app/schemas/stock.py`
- `backend/app/services/data_loader.py`
- `backend/batch/collect_data.py`
- `backend/app/services/naver_crawler.py`

---

## 1. Current Stock Schema Fields

### StockBase (Line 5-8)
| Field | Type | Description |
|-------|------|-------------|
| ticker | str | Stock ticker symbol (6 digits) |
| name | str | Company name |

### Stock (Line 11-17) - Inherits from StockBase
| Field | Type | Description |
|-------|------|-------------|
| ticker | str | Stock ticker symbol |
| name | str | Company name |
| current_price | float | Current stock price |
| change_rate | float | Price change rate (%) |

### StockDetail (Line 20-37) - Inherits from Stock
| Field | Type | Description | Status |
|-------|------|-------------|--------|
| ticker | str | Stock ticker symbol | Existing |
| name | str | Company name | Existing |
| current_price | float | Current stock price | Existing |
| change_rate | float | Price change rate (%) | Existing |
| per | Optional[float] | Price-to-Earnings Ratio | Existing |
| pbr | Optional[float] | Price-to-Book Ratio | Existing |
| market_cap | Optional[float] | Market capitalization | Existing |
| eps | Optional[float] | Earnings per Share | Existing |
| bps | Optional[float] | Book value per Share | Existing |
| **forward_pe** | **Optional[float]** | Forward P/E ratio (선행 PER) | **NEW in Wave 1** |
| **roe** | **Optional[float]** | Return on Equity (ROE) % | **NEW in Wave 1** |
| **debt_ratio** | **Optional[float]** | Debt Ratio (부채비율) % | **NEW in Wave 1** |
| **eps_growth_yoy** | **Optional[float]** | EPS YoY growth rate % | **NEW in Wave 1** |
| **sector** | **Optional[str]** | Industry sector (업종) | **NEW in Wave 1** |

### Recommendation Schema (Line 40-64)
Same fields as StockDetail plus:
| Field | Type | Description |
|-------|------|-------------|
| recommendation_score | Optional[float] | Calculated recommendation score |

---

## 2. Current Data Collection Flow

### 2.1 Data Source: Naver Finance

**Primary Function:** `naver_crawler.get_stock_quote(ticker)` (Line 280-370)
- URL: `https://finance.naver.com/item/main.naver?code={ticker}`
- Extracts basic quote data + calls `_get_financial_data()` for additional metrics

**Secondary Function:** `naver_crawler._get_financial_data(ticker)` (Line 153-243)
- Parses HTML tables from main page
- Uses `pd.read_html()` to extract financial tables
- Currently extracts: ROE, Debt Ratio, EPS Growth YoY

**OHLCV Function:** `naver_crawler.get_ohlcv_naver(ticker)` (Line 246-277)
- URL: `https://finance.naver.com/item/sise_day.naver?code={ticker}`
- Extracts: open, high, low, close, volume

### 2.2 Current Data Fields Collected (collect_data.py, Lines 79-101)

```python
{
    'ticker': quote.get('ticker'),              # str
    'name': quote.get('name'),                  # str
    'date': datetime.now().strftime("%Y-%m-%d"), # str
    'current_price': quote.get('current_price'), # float
    'per': quote.get('per'),                    # float
    'pbr': quote.get('pbr'),                    # float
    'forward_pe': quote.get('forward_per'),     # float
    'eps': quote.get('eps'),                    # float
    'bps': quote.get('bps'),                    # float
    'market_cap': quote.get('market_cap'),      # float
    'dividend_yield': quote.get('dividend_yield'), # float
    'roe': quote.get('roe'),                    # float (%)
    'roe_year': quote.get('roe_year'),          # str (year label)
    'debt_ratio': quote.get('debt_ratio'),      # float (%)
    'debt_ratio_year': quote.get('debt_ratio_year'), # str (year label)
    'eps_growth_yoy': quote.get('eps_growth_yoy'), # float (%)
    'open': quote.get('open'),                  # float
    'high': quote.get('high'),                  # float
    'low': quote.get('low'),                    # float
    'close': quote.get('close'),                # float
    'volume': quote.get('volume'),              # int
}
```

---

## 3. Data Loading Patterns (data_loader.py)

### 3.1 File Structure
- **Daily data:** `data/daily/stocks_YYYYMMDD.csv`
- **Quarterly data:** `data/quarterly/fundamentals_YYYYMMDD.csv`
- **Legacy:** `data/stocks_YYYYMMDD.csv`

### 3.2 Data Loading Flow

1. `load_stocks_data()` (Line 70-121)
   - Loads daily CSV/JSON
   - Loads quarterly CSV/JSON if available
   - Merges quarterly fields: `['roe', 'debt_ratio', 'forward_pe', 'eps_growth_yoy', 'sector']`

2. `get_all_stocks()` (Line 124-154)
   - Returns list of stock dicts with standardized fields

3. `get_stock_by_ticker()` (Line 157-190)
   - Returns single stock dict including OHLCV data

4. `get_stock_data()` (Line 248-321)
   - Unified fetch with caching
   - Falls back to Naver crawler then file data
   - Returns dict with 20+ fields including data source tracking

### 3.3 Cache System
- `_valuation_cache`: TTL = 3600 seconds (1 hour)
- `_price_cache`: TTL = 3600 seconds (1 hour)
- `_fundamentals_cache`: TTL = 7776000 seconds (90 days)

---

## 4. Naver Finance HTML Table Analysis

### 4.1 Target Table: 기업실적분석 (Corporate Performance Analysis)

The table contains these financial metric rows:

| Korean Label (HTML) | English Name | Current Field | Needs Addition |
|---------------------|--------------|---------------|----------------|
| 매출액 | Revenue | ❌ None | **YES** |
| 영업이익 | Operating Profit | ❌ None | **YES** |
| 당기순이익 | Net Profit | ❌ None | **YES** |
| 영업이익률 | Operating Margin (%) | ❌ None | **YES** |
| 순이익률 | Net Margin (%) | ❌ None | **YES** |
| ROE(지배주주) | ROE (Controlling Shareholder) | ✅ `roe` | No |
| 부채비율 | Debt Ratio (%) | ✅ `debt_ratio` | No |
| 당좌비율 | Current Ratio (%) | ❌ None | **YES** |
| 유보율 | Reserve Ratio (%) | ❌ None | **YES** |
| EPS(원) | EPS (Won) | ✅ `eps` | No |
| PER(배) | PER (Multiple) | ✅ `per` | No |
| BPS(원) | BPS (Won) | ✅ `bps` | No |
| PBR(배) | PBR (Multiple) | ✅ `pbr` | No |
| 주당배당금 | Dividend per Share | ❌ None | **YES** |
| 시가배당률 | Dividend Yield (%) | ⚠️ `dividend_yield` | Partial* |
| 배당성향 | Dividend Payout Ratio (%) | ❌ None | **YES** |

*Note: `dividend_yield` is collected from main quote page, not from 기업실적분석 table

### 4.2 Complete Field Mapping: Naver HTML → Python Schema

| HTML Korean Name | Python Field Name | Data Type | Collection Source |
|------------------|-------------------|-----------|-------------------|
| 매출액 | `revenue` | `Optional[float]` | 기업실적분석 table |
| 영업이익 | `operating_profit` | `Optional[float]` | 기업실적분석 table |
| 당기순이익 | `net_profit` | `Optional[float]` | 기업실적분석 table |
| 영업이익률 | `operating_margin` | `Optional[float]` | 기업실적분석 table |
| 순이익률 | `net_margin` | `Optional[float]` | 기업실적분석 table |
| ROE(지배주주) | `roe` | `Optional[float]` | 기업실적분석 table |
| 부채비율 | `debt_ratio` | `Optional[float]` | 기업실적분석 table |
| 당좌비율 | `current_ratio` | `Optional[float]` | 기업실적분석 table |
| 유보율 | `reserve_ratio` | `Optional[float]` | 기업실적분석 table |
| EPS(원) | `eps` | `Optional[float]` | Main quote page |
| BPS(원) | `bps` | `Optional[float]` | Main quote page |
| PER(배) | `per` | `Optional[float]` | Main quote page |
| PBR(배) | `pbr` | `Optional[float]` | Main quote page |
| 주당배당금 | `dividend_per_share` | `Optional[float]` | 기업실적분석 table |
| 시가배당률 | `dividend_yield` | `Optional[float]` | Main quote page |
| 배당성향 | `dividend_payout_ratio` | `Optional[float]` | 기업실적분석 table |
| - | `eps_growth_yoy` | `Optional[float]` | Calculated from EPS history |
| 선행PER | `forward_pe` | `Optional[float]` | Main quote page |

---

## 5. New Metrics to Add (11 Fields)

### 5.1 Financial Performance Metrics
1. **`revenue`** - Revenue (매출액)
2. **`operating_profit`** - Operating Profit (영업이익)
3. **`net_profit`** - Net Profit (당기순이익)
4. **`operating_margin`** - Operating Margin % (영업이익률)
5. **`net_margin`** - Net Margin % (순이익률)

### 5.2 Financial Health Metrics
6. **`current_ratio`** - Current Ratio % (당좌비율)
7. **`reserve_ratio`** - Reserve Ratio % (유보율)

### 5.3 Dividend Metrics
8. **`dividend_per_share`** - Dividend per Share (주당배당금)
9. **`dividend_payout_ratio`** - Dividend Payout Ratio % (배당성향)

### 5.4 Already Exists (5 Fields)
- `per`, `pbr`, `eps`, `bps`, `roe`, `debt_ratio`, `forward_pe`, `eps_growth_yoy`

---

## 6. Summary: Current vs. Required

### Currently Implemented (11 fields):
| Field | Type | Source |
|-------|------|--------|
| ticker | str | Base |
| name | str | Base |
| current_price | float | Quote |
| change_rate | float | Quote |
| per | float | Main page |
| pbr | float | Main page |
| market_cap | float | Main page |
| eps | float | Main page |
| bps | float | Main page |
| forward_pe | float | Main page |
| roe | float | Financial table |
| debt_ratio | float | Financial table |
| eps_growth_yoy | float | Calculated |
| sector | str | Financial table |

### To Be Added (9 new metrics from table):
1. `revenue` (Optional[float])
2. `operating_profit` (Optional[float])
3. `net_profit` (Optional[float])
4. `operating_margin` (Optional[float])
5. `net_margin` (Optional[float])
6. `current_ratio` (Optional[float])
7. `reserve_ratio` (Optional[float])
8. `dividend_per_share` (Optional[float])
9. `dividend_payout_ratio` (Optional[float])

---

## 7. Technical Implementation Notes

### 7.1 Parsing Pattern (from naver_crawler.py)
```python
# Current pattern for extracting financial data:
1. Use pd.read_html() to parse all tables
2. Find target table by shape (>10 rows, >3 columns) and content
3. Set first column as index (contains metric names in Korean)
4. Use df.xs() to get annual data section
5. Search row by keyword in index (e.g., 'ROE', '부채비율')
6. Extract latest non-null value
```

### 7.2 Korean Keywords to Match (for new fields)
- Revenue: `'매출액'`
- Operating Profit: `'영업이익'`
- Net Profit: `'당기순이익'` or `'순이익'`
- Operating Margin: `'영업이익률'`
- Net Margin: `'순이익률'`
- Current Ratio: `'당좌비율'`
- Reserve Ratio: `'유보율'`
- Dividend per Share: `'주당배당금'`
- Dividend Payout Ratio: `'배당성향'`

### 7.3 Data Types
All new metrics should be `Optional[float]` to handle missing data gracefully.

### 7.4 Storage Pattern
New fields should follow existing pattern:
- Add to `StockDetail` schema
- Add to `Recommendation` schema
- Add to `collect_data.py` row dict
- Add to `data_loader.py` merge columns list
- Add to `naver_crawler.py` `_get_financial_data()` return dict

---

## 8. Files Requiring Updates

Based on this analysis, the following files will need modification to add the new metrics:

1. `backend/app/schemas/stock.py` - Add new Optional[float] fields to StockDetail and Recommendation
2. `backend/app/services/naver_crawler.py` - Extend `_get_financial_data()` to extract new metrics
3. `backend/batch/collect_data.py` - Add new fields to the row dictionary
4. `backend/app/services/data_loader.py` - Add new fields to merge columns and result dicts

---

*End of Schema Analysis Report*
