# Data Collection Architecture - Notepad

## Inherited Wisdom
- `naver_crawler.py` - COMPLETE (exists, extracts PER, PBR, Forward PER, EPS, BPS, 시가총액, 배당수익률 with rate limiting)
- `fdr_client.py` - COMPLETE (exists, fetches OHLCV data)
- `dart_api.py` - COMPLETE (exists, calculates ROE, debt ratio, EPS, BPS)
- `collect_data.py` - USES YFINANCE (needs to be replaced with new sources)

## Key Decisions
- Rate limiting: 1-2 seconds delay between Naver requests
- FDR as backup, Naver as primary for valuation
- DART for quarterly fundamentals
- Layered storage: daily (price/valuation) + quarterly (fundamentals)

## Gotchas
- yfinance is unreliable for Korean stocks
- Naver Finance requires rate limiting to avoid IP ban
- DART API has 10,000 calls/day limit

## Implementation Details (Task 2)
- Modified `data_loader.py` to support multi-source data loading
- Added `get_naver_valuation(ticker)`: fetches PER, PBR, Forward PER, EPS, BPS, market_cap, dividend_yield with daily cache (1 hour TTL)
- Added `get_fdr_price_data(ticker)`: fetches OHLCV with daily cache (1 hour TTL)
- Added `get_dart_fundamentals(ticker)`: fetches ROE, debt_ratio with quarterly cache (90 days TTL)
- Added `get_stock_data(ticker)`: unified function that merges all sources with data source tracking
- Added `get_stock_chart_data(ticker, days)`: wrapper for fdr_client.get_chart_data()
- Added `clear_cache(ticker)`: clears cache for specific ticker or all
- Added `get_cache_status()`: returns cache statistics
- Cache TTL configurable via environment variables: CACHE_TTL_DAILY, CACHE_TTL_QUARTERLY
- Falls back to CSV/JSON file data when external APIs fail
- All existing functions (get_stock_by_ticker, load_stocks_data, etc.) preserved for backward compatibility

## Implementation Details (Task 3 & 4)
- Replaced yfinance in `batch/collect_data.py` with Naver + FDR
- Added imports: `naver_crawler`, `fdr_client`, removed `yfinance`
- `get_stock_info(ticker)` now uses:
  - Naver: PER, PBR, Forward PER, EPS, BPS, market_cap, dividend_yield, current_price, name
  - FDR: OHLCV (open, high, low, close, volume)
- Rate limiting: naver_crawler's built-in 1-2 sec + safety delay every 10 stocks
- DART enrichment preserved: ROE, debt_ratio
- Created layered storage structure:
  - `data/daily/stocks_YYYYMMDD.csv` - daily price + valuation
  - `data/quarterly/fundamentals_YYYYQQ.csv` - quarterly fundamentals
  - `data/metadata.json` - tracking file with collection times
- Modified data_loader to read new structure with backward compatibility

## Final Status
- Task 1 (naver_crawler.py): COMPLETE
- Task 2 (data_loader.py): COMPLETE
- Task 3 (batch collector): COMPLETE
- Task 4 (data storage): COMPLETE

## All Tasks Complete - 4/4
- Task 1 (naver_crawler.py): COMPLETE
- Task 2 (data_loader.py): COMPLETE
- Task 3 (batch collector): PENDING
- Task 4 (data storage): PENDING
