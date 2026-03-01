# Stock Data Collection Architecture Plan

## TL;DR

> **Goal**: Replace yfinance with Naver Finance crawling + FinanceDataReader + DART API for stock data
>
> **Data Sources**:
> - Daily: Naver Finance (PER, PBR, Forward PER, 시가총액, 배당수익률)
> - Daily: FinanceDataReader (OHLCV, 기술적 지표)
> - Quarterly: DART API (부채비율, ROE, EPS, BPS)
>
> **Estimated Effort**: Medium
> **Execution**: Sequential (dependencies between data sources)

---

## Context

### Current State
- Existing `data_loader.py` loads from CSV/JSON files
- Files in `data/` directory: `stocks_*.csv`, `stocks_advanced_*.csv`
- Current data sourced from yfinance (unreliable for fundamentals)

### User Requirements
- **Remove yfinance completely**
- Use Naver Finance for valuation metrics (PER, PBR, Forward PER)
- Use FinanceDataReader for price/chart data
- Keep DART API for financial fundamentals

### Metis Review Findings
- FDR is unstable as primary source, use as backup
- Naver crawling needs rate limiting (3-5 sec, rotate User-Agent)
- DART: 10,000 calls/day limit, parse XBRL (heavy)
- Recommended: layered storage (daily/quarterly/metadata)

---

## Work Objectives

### Core Objective
Build a robust data collection pipeline that:
1. Crawls Naver Finance daily for valuation metrics
2. Fetches OHLCV from FinanceDataReader
3. Collects DART fundamentals quarterly
4. Stores data in layered format for API consumption

### Concrete Deliverables
- [x] New `naver_crawler.py` module for valuation data
- [x] Modified `data_loader.py` to support multiple data sources
- [x] Updated batch collector with proper scheduling
- [x] Data storage structure (daily/quarterly)

### Must Have
- Rate limiting for Naver (avoid IP ban)
- Graceful fallback when sources fail
- Configurable scheduling

### Must NOT Have
- No yfinance dependencies
- No hardcoded credentials
- No blocking calls in API responses

---

## Execution Strategy

### Phase 1: Naver Finance Crawler
- Create `backend/app/services/naver_crawler.py`
- Implement rate limiting (1-2 sec delay)
- Extract: PER, PBR, Forward PER, EPS, 시가총액, 배당수익률

### Phase 2: FinanceDataReader Integration
- Add FDR calls for OHLCV data
- Integrate pandas-ta for technical indicators
- Cache recent data

### Phase 3: DART API Integration
- Leverage existing `dart_api.py`
- Schedule quarterly collection

### Phase 4: Data Loader Updates
- Modify `data_loader.py` to merge all sources
- Add caching layer
- Ensure backward compatibility

---

## Verification Strategy

### Test Scenarios
1. Naver crawler returns correct data for sample tickers
2. FDR returns OHLCV without errors
3. Combined data matches expected schema
4. Rate limiting prevents IP ban (test with 10+ requests)

---

## Commit Strategy

- `feat(data): add naver finance crawler module`
- `feat(data): integrate finance data reader`
- `refactor(data): update data loader for multi-source`
- `chore(data): update batch scheduler`

---

## Success Criteria

### Verification Commands
```bash
# Test Naver crawler
python -c "from app.services.naver_crawler import get_stock_quote; print(get_stock_quote('005930'))"

# Test FDR integration
python -c "from app.services.fdr_client import get_ohlcv; print(get_ohlcv('005930'))"
```
