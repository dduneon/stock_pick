# Work Plan: Comprehensive Naver Finance Crawler

## TL;DR

> **Replace the existing Naver Finance crawler** with a comprehensive, extensible version that extracts ALL financial metrics from both the summary page and the 기업실적분석 table (주요재무정보).
>
> **Deliverables**:
> - New `naver_crawler.py` with comprehensive extraction logic
> - Extended Pydantic schemas for new financial metrics
> - Updated batch collection to persist all metrics
> - Comprehensive test suite (unit + integration)
>
> **Estimated Effort**: Medium-Large  
> **Parallel Execution**: YES - 5 waves  
> **Critical Path**: Schema Design → Crawler Implementation → Batch Integration → Testing

---

## Context

### Current State
The project has an existing `naver_crawler.py` that fetches:
- Summary page: price, PER, PBR, EPS, BPS, market cap, dividend
- Financial table: ROE, debt ratio, EPS growth (limited extraction)

### User Requirements (Confirmed)
1. **Replace** existing crawler with improved version using pandas `read_html(match='주요재무정보')` approach
2. **Extract ALL metrics** from 기업실적분석 table:
   - Revenue, Operating Profit, Net Profit
   - All margin ratios (operating, net profit)
   - All balance sheet ratios (debt, current, reserve)
   - Valuation metrics (PER, PBR, EPS, BPS)
   - Dividend metrics (per share, yield, payout ratio)
3. **Comprehensive + Extensible** design for future metric additions
4. **Store persistently** in CSV/JSON via batch job
5. **Comprehensive tests** including unit and integration tests

### Key Technical Decisions
- **Approach**: Replace `_get_financial_data()` with new comprehensive implementation
- **Parsing**: Use pandas `read_html()` with `match='주요재무정보'` for precise targeting
- **Data Structure**: Extend `Stock` schema to include all new fields
- **Backward Compatibility**: Maintain existing `get_stock_quote()` return format

---

## Work Objectives

### Core Objective
Build a unified, comprehensive Naver Finance crawler that extracts all available financial metrics using robust pandas-based HTML parsing, with full test coverage and seamless integration into the existing batch workflow.

### Concrete Deliverables
1. New `naver_crawler.py` with comprehensive `_get_financial_data()`
2. Extended `Stock` schema in `schemas/stock.py`
3. Updated `batch/collect_data.py` to collect all metrics
4. Updated `data_loader.py` to load new fields
5. Comprehensive test suite in `tests/test_naver_crawler.py`

### Definition of Done
- [ ] All 15+ financial metrics extracted and stored
- [ ] Batch job successfully collects data for all KOSPI stocks
- [ ] All tests pass (unit + integration)
- [ ] Existing API endpoints continue to work
- [ ] Rate limiting preserved (1-2s delays)

### Must Have
- Comprehensive metric extraction from 기업실적분석 table
- Proper handling of missing/null values
- Extensible design for future metric additions
- Full backward compatibility
- Comprehensive test coverage

### Must NOT Have (Guardrails)
- NO breaking changes to existing API
- NO removal of existing functionality
- NO hardcoded values or magic numbers
- NO skipping error handling for any extraction step

---

## Verification Strategy

### Test Decision
- **Infrastructure exists**: YES (pytest)
- **Automated tests**: TDD approach - write tests first
- **Framework**: pytest
- **Test Strategy**: 
  1. Unit tests for parsing functions with mock HTML
  2. Integration tests with real Naver Finance (marked with `@pytest.mark.integration`)
  3. Edge case tests for missing data, malformed HTML

### QA Policy
Every task includes agent-executed QA scenarios:
- **Backend**: Bash (pytest) - Run tests, verify output
- **Evidence saved to**: `.sisyphus/evidence/task-{N}-{scenario-slug}.{ext}`

---

## Execution Strategy

### Parallel Execution Waves

```
Wave 1 (Foundation - Independent, can start immediately):
├── Task 1: Analyze current schemas and define new fields
├── Task 2: Design comprehensive data structure
└── Task 3: Create mock HTML test fixtures

Wave 2 (Crawler Implementation - depends on Wave 1):
├── Task 4: Implement new `_get_financial_data()` function
├── Task 5: Add helper functions for metric extraction
├── Task 6: Implement metric extraction for all fields
└── Task 7: Add error handling and null value management

Wave 3 (Schema & Data Updates - depends on Wave 1):
├── Task 8: Extend Stock schema with new fields
├── Task 9: Update batch/collect_data.py for new fields
└── Task 10: Update data_loader.py for new fields

Wave 4 (Testing - depends on Wave 2 & 3):
├── Task 11: Write unit tests for extraction functions
├── Task 12: Write integration tests with mock HTML
├── Task 13: Write edge case tests (missing data, errors)
└── Task 14: Create test fixtures for various stock types

Wave 5 (Final Integration - depends on Wave 4):
├── Task 15: Full batch job test run
├── Task 16: Verify API endpoints still work
├── Task 17: Performance test (rate limiting check)
└── Task 18: Documentation update
```

### Dependency Matrix

| Task | Depends On | Blocks |
|------|-----------|--------|
| 1-3 | — | 4-10 |
| 4-7 | 1-3 | 11-14 |
| 8-10 | 1-3 | 15-18 |
| 11-14 | 4-7, 8-10 | 15-18 |
| 15-18 | 11-14 | Final Verification |

### Critical Path
Task 1 → Task 4 → Task 11 → Task 15 → Final Verification

---

## TODOs

### Wave 1: Foundation

- [x] **1. Analyze Current Schemas and Data Flow**

  **What to do**:
  - Read `backend/app/schemas/stock.py` - document all current fields
  - Read `backend/app/services/data_loader.py` - understand loading patterns
  - Read `backend/batch/collect_data.py` - understand collection flow
  - Identify which metrics are currently used vs. which need to be added
  
  **Must NOT do**:
  - Don't modify any files yet
  - Don't skip any field documentation
  
  **Recommended Agent Profile**:
  - **Category**: `deep` (thorough analysis)
  - **Skills**: None needed
  
  **Parallelization**:
  - **Can Run In Parallel**: YES (Wave 1)
  - **Blocked By**: None
  
  **References**:
  - `backend/app/schemas/stock.py` - Current Stock schema
  - `backend/app/services/data_loader.py` - Data loading patterns
  - `backend/batch/collect_data.py` - Collection flow
  
  **Acceptance Criteria**:
  - [ ] Document all current fields in Stock schema
  - [ ] List all metrics to be added (from HTML table)
  - [ ] Create mapping: HTML row name → field name → data type
  
  **QA Scenarios**:
  ```
  Scenario: Verify schema analysis completeness
    Tool: Bash (grep/read)
    Steps:
      1. Read stock.py and count fields
      2. Read data_loader.py and find field usage
      3. Verify all 15+ new metrics are documented
    Expected: Complete field mapping document exists
    Evidence: .sisyphus/evidence/task-1-schema-analysis.md
  ```
  
  **Commit**: NO (part of Wave 1 group)

- [x] **2. Design Comprehensive Data Structure**

  **What to do**:
  - Design new data structure for comprehensive financial data
  - Group metrics logically (profitability, balance sheet, valuation, dividend)
  - Use Optional[float] for all numeric fields (handle missing data)
  - Include metadata fields (year, currency, etc.)
  
  **Design Example**:
  ```python
  class FinancialMetrics(BaseModel):
      # Profitability
      revenue: Optional[float] = None  # 매출액
      operating_profit: Optional[float] = None  # 영업이익
      net_profit: Optional[float] = None  # 당기순이익
      operating_margin: Optional[float] = None  # 영업이익률
      net_margin: Optional[float] = None  # 순이익률
      roe: Optional[float] = None  # ROE
      
      # Balance Sheet
      debt_ratio: Optional[float] = None  # 부채비율
      current_ratio: Optional[float] = None  # 당좌비율
      reserve_ratio: Optional[float] = None  # 유보율
      
      # Valuation
      per: Optional[float] = None
      pbr: Optional[float] = None
      eps: Optional[float] = None
      bps: Optional[float] = None
      
      # Dividend
      dividend_per_share: Optional[float] = None  # 주당배당금
      dividend_yield: Optional[float] = None  # 시가배당률
      dividend_payout_ratio: Optional[float] = None  # 배당성향
      
      # Metadata
      fiscal_year: Optional[str] = None  # e.g., "2024.12"
  ```
  
  **Must NOT do**:
  - Don't use non-Optional types (data can be missing)
  - Don't use Korean field names in code
  
  **Recommended Agent Profile**:
  - **Category**: `deep` (data modeling)
  
  **Acceptance Criteria**:
  - [ ] Complete data structure design document
  - [ ] All 15+ metrics mapped with types
  - [ ] Grouping rationale documented
  
  **QA Scenarios**:
  ```
  Scenario: Verify data structure design
    Tool: Bash (file check)
    Steps:
      1. Check design document exists
      2. Verify all HTML metrics are covered
      3. Check type annotations are Optional[float]
    Expected: Complete design document
    Evidence: .sisyphus/evidence/task-2-design-doc.md
  ```
  
  **Commit**: NO (part of Wave 1 group)

- [x] **3. Create Mock HTML Test Fixtures**

  **What to do**:
  - Create sample HTML files mimicking Naver Finance structure
  - Include various scenarios: normal data, missing data, edge cases
  - Save to `backend/tests/fixtures/naver_finance/`
  
  **Fixtures needed**:
  1. `sk_hynix_full.html` - Complete data (all metrics present)
  2. `samsung_missing_roe.html` - Missing ROE data
  3. `startup_negative_profit.html` - Negative operating profit
  4. `minimal_data.html` - Only basic metrics available
  
  **Must NOT do**:
  - Don't use real HTML (copyright issues)
  - Don't create overly simplified fixtures (must match real structure)
  
  **Recommended Agent Profile**:
  - **Category**: `quick` (file creation)
  
  **Acceptance Criteria**:
  - [ ] 4+ HTML fixtures created
  - [ ] Fixtures cover edge cases
  - [ ] Fixtures match real Naver Finance HTML structure
  
  **QA Scenarios**:
  ```
  Scenario: Verify fixtures are valid HTML
    Tool: Bash (file + python)
    Steps:
      1. Check files exist in tests/fixtures/
      2. Parse with BeautifulSoup - no errors
      3. Verify table structure matches Naver format
    Expected: All fixtures parseable
    Evidence: .sisyphus/evidence/task-3-fixtures-valid.txt
  ```
  
  **Commit**: YES - "test: Add Naver Finance HTML test fixtures"

---

## Final Verification Wave

- [x] **F1. Plan Compliance Audit** — `oracle`
  Read the plan end-to-end. For each "Must Have": verify implementation exists. For each "Must NOT Have": search codebase for forbidden patterns. Check evidence files exist.
  Output: `Must Have [N/N] | Must NOT Have [N/N] | VERDICT`

- [x] **F2. Code Quality Review** — `unspecified-high`
  Run `pytest backend/tests/test_naver_crawler.py -v`. Check for `as any`, bare `except`, magic numbers. Review type hints coverage.
  Output: `Tests [PASS/FAIL] | Quality [PASS/FAIL] | Coverage [%]`

- [x] **F3. Real Integration Test** — `unspecified-high`
  Run batch collection for 5 test stocks. Verify CSV/JSON files contain all new fields with correct values.
  Output: `Collection [PASS/FAIL] | Fields [N/N] | Data Valid [YES/NO]`

- [x] **F4. API Compatibility Check** — `deep`
  Test existing API endpoints (`/api/stocks`, `/api/recommendations`) still work with new crawler.
  Output: `Endpoints [N/N working] | Backward Compatible [YES/NO]`

---

## Commit Strategy

- **Wave 1**: `docs: Add comprehensive Naver crawler design and fixtures`
- **Wave 2**: `feat: Implement comprehensive financial data extraction`
- **Wave 3**: `feat: Extend schemas and data pipeline for new metrics`
- **Wave 4**: `test: Add comprehensive crawler test suite`
- **Wave 5**: `refactor: Integrate new crawler into batch workflow`

---

## Success Criteria

### Verification Commands
```bash
# Run all crawler tests
cd backend && pytest tests/test_naver_crawler.py -v

# Test batch collection (5 stocks)
python -m backend.batch.collect_data --limit 5

# Verify data files contain new fields
head -1 data/stocks_*.csv | grep -E "revenue|operating_profit|net_profit|current_ratio|reserve_ratio"

# Run existing API tests to verify backward compatibility
pytest backend/tests/ -k "test_get_recommendations or test_get_stock_detail" -v
```

### Final Checklist
- [ ] All 15+ financial metrics extracted correctly
- [ ] Batch job runs successfully for all KOSPI stocks
- [ ] All unit tests pass (>90% coverage)
- [ ] Integration tests pass with real Naver data
- [ ] API endpoints remain backward compatible
- [ ] Rate limiting (1-2s) preserved
- [ ] No breaking changes to existing functionality
- [ ] Documentation updated (AGENTS.md, docstrings)



### Wave 2: Crawler Implementation

- [x] **4. Implement New `_get_financial_data()` Function**

  **What to do**:
  - Rewrite `_get_financial_data()` in `naver_crawler.py` using user's pandas approach
  - Use `pd.read_html(response.text, match='주요재무정보', encoding='euc-kr')` for precise targeting
  - Extract `최근 연간 실적` using `.xs()` method
  - Clean column headers with `.droplevel(1)`
  
  **Implementation Template**:
  ```python
  def _get_financial_data(ticker: str) -> Dict[str, Any]:
      """Extract comprehensive financial data from Naver Finance."""
      url = f"https://finance.naver.com/item/main.naver?code={ticker}"
      
      try:
          _rate_limit()
          response = requests.get(url, headers=_get_headers(), timeout=10)
          response.raise_for_status()
          response.encoding = 'euc-kr'
          
          # Use match for precise targeting
          dfs = pd.read_html(response.text, match='주요재무정보', encoding='euc-kr')
          if not dfs:
              return _get_empty_financial_data()
              
          df = dfs[0]
          
          # Set first column as index
          df.set_index(df.columns[0], inplace=True)
          
          # Extract annual performance data
          annual_df = df.xs('최근 연간 실적', axis=1, level=0)
          annual_df.columns = annual_df.columns.droplevel(1)
          
          # Extract all metrics
          result = _extract_all_metrics(annual_df)
          return result
          
      except Exception as e:
          print(f"Financial data extraction failed for {ticker}: {e}")
          return _get_empty_financial_data()
  ```
  
  **Must NOT do**:
  - Don't remove existing `get_stock_quote()` function
  - Don't break existing return format compatibility
  - Don't skip rate limiting
  
  **Recommended Agent Profile**:
  - **Category**: `deep` (complex parsing logic)
  - **Skills**: None
  
  **Parallelization**:
  - **Can Run In Parallel**: YES (Wave 2)
  - **Blocked By**: Task 1-3
  - **Blocks**: Task 11-14
  
  **References**:
  - User's pandas analysis code (provided in prompt)
  - Current `naver_crawler.py:153-243` - Current implementation for reference
  
  **Acceptance Criteria**:
  - [ ] New function uses `match='주요재무정보'`
  - [ ] Function handles missing data gracefully
  - [ ] Returns consistent dictionary structure
  
  **QA Scenarios**:
  ```
  Scenario: Test extraction with mock HTML
    Tool: Bash (pytest)
    Steps:
      1. Run test with sk_hynix_full.html fixture
      2. Verify all expected fields are extracted
      3. Check data types are correct
    Expected: All metrics extracted with correct types
    Evidence: .sisyphus/evidence/task-4-extraction-test.log
  ```
  
  **Commit**: NO (part of Wave 2 group)

- [x] **5. Add Helper Functions for Metric Extraction**

  **What to do**:
  - Create `_get_latest_valid_data(series)` - handles missing values, returns latest non-null
  - Create `_find_row(df, keyword)` - finds row by partial match (Korean/English)
  - Create `_parse_numeric(value)` - converts Korean number format to float
  - Create `_get_empty_financial_data()` - returns default empty structure
  
  **Implementation**:
  ```python
  def _get_latest_valid_data(series: pd.Series) -> Tuple[Optional[float], Optional[str]]:
      """Get the latest non-null value from a series."""
      cleaned = pd.to_numeric(series.replace('-', np.nan), errors='coerce').dropna()
      if not cleaned.empty:
          return cleaned.iloc[-1], str(cleaned.index[-1])
      return None, None
  
  def _find_row(df: pd.DataFrame, keyword: str) -> Optional[pd.Series]:
      """Find a row by keyword (partial match)."""
      for idx in df.index:
          if keyword in str(idx):
              return df.loc[idx]
      return None
  
  def _parse_numeric(value: Any) -> Optional[float]:
      """Parse numeric value, handling Korean formats."""
      if pd.isna(value) or value == '-' or value == '':
          return None
      if isinstance(value, (int, float)):
          return float(value)
      # Handle comma separators and em tags
      cleaned = str(value).replace(',', '').replace('<em class="f_up">', '').replace('</em>', '').strip()
      try:
          return float(cleaned)
      except (ValueError, TypeError):
          return None
  ```
  
  **Must NOT do**:
  - Don't duplicate existing `_parse_number()` function logic
  - Don't create functions that are too specific (keep reusable)
  
  **Recommended Agent Profile**:
  - **Category**: `quick`
  
  **Acceptance Criteria**:
  - [ ] All helper functions implemented
  - [ ] Functions handle edge cases (missing data, malformed values)
  - [ ] Unit tests for each helper function
  
  **QA Scenarios**:
  ```
  Scenario: Test helper functions with edge cases
    Tool: Bash (pytest)
    Steps:
      1. Test _get_latest_valid_data with all nulls
      2. Test _parse_numeric with Korean formats
      3. Test _find_row with partial matches
    Expected: All edge cases handled correctly
    Evidence: .sisyphus/evidence/task-5-helpers-test.log
  ```
  
  **Commit**: NO (part of Wave 2 group)

- [x] **6. Implement Metric Extraction for All Fields**

  **What to do**:
  - Create `_extract_all_metrics(annual_df)` function
  - Extract all 15+ metrics using row keywords
  - Handle both Korean and English row names where applicable
  
  **Metrics to Extract** (from HTML table):
  ```python
  def _extract_all_metrics(annual_df: pd.DataFrame) -> Dict[str, Any]:
      result = {
          # Profitability
          'revenue': _extract_metric(annual_df, ['매출액', 'Revenue']),
          'operating_profit': _extract_metric(annual_df, ['영업이익', 'Operating Profit']),
          'net_profit': _extract_metric(annual_df, ['당기순이익', 'Net Profit']),
          'operating_margin': _extract_metric(annual_df, ['영업이익률', 'Operating Margin']),
          'net_margin': _extract_metric(annual_df, ['순이익률', 'Net Margin']),
          'roe': _extract_metric(annual_df, ['ROE', 'ROE(지배주주)']),
          
          # Balance Sheet
          'debt_ratio': _extract_metric(annual_df, ['부채비율', 'Debt Ratio']),
          'current_ratio': _extract_metric(annual_df, ['당좌비율', 'Current Ratio']),
          'reserve_ratio': _extract_metric(annual_df, ['유보율', 'Reserve Ratio']),
          
          # Valuation
          'eps': _extract_metric(annual_df, ['EPS', 'EPS(원)']),
          'bps': _extract_metric(annual_df, ['BPS', 'BPS(원)']),
          'per': _extract_metric(annual_df, ['PER', 'PER(배)']),
          'pbr': _extract_metric(annual_df, ['PBR', 'PBR(배)']),
          
          # Dividend
          'dividend_per_share': _extract_metric(annual_df, ['주당배당금', 'Dividend per Share']),
          'dividend_yield': _extract_metric(annual_df, ['시가배당률', 'Dividend Yield']),
          'dividend_payout_ratio': _extract_metric(annual_df, ['배당성향', 'Payout Ratio']),
          
          # EPS Growth (calculated)
          'eps_growth_yoy': _calculate_eps_growth(annual_df),
          'fiscal_year': _get_latest_fiscal_year(annual_df),
      }
      return result
  ```
  
  **Must NOT do**:
  - Don't skip any metrics from the list
  - Don't hardcode row indices (use keyword matching)
  
  **Recommended Agent Profile**:
  - **Category**: `deep`
  
  **Acceptance Criteria**:
  - [ ] All 15+ metrics extracted
  - [ ] EPS growth calculated correctly (YoY)
  - [ ] Fiscal year captured
  
  **QA Scenarios**:
  ```
  Scenario: Verify all metrics extracted
    Tool: Bash (pytest)
    Steps:
      1. Run extraction on full fixture
      2. Assert all expected keys present in result
      3. Verify EPS growth calculation formula
    Expected: All 15+ metrics present with correct values
    Evidence: .sisyphus/evidence/task-6-metrics-extracted.json
  ```
  
  **Commit**: NO (part of Wave 2 group)

- [x] **7. Add Error Handling and Null Value Management**

  **What to do**:
  - Ensure all extraction functions handle missing rows gracefully
  - Return None for missing metrics (not 0 or empty string)
  - Add comprehensive error logging
  - Handle edge cases: empty table, malformed HTML, network errors
  
  **Must NOT do**:
  - Don't use bare `except:` clauses
  - Don't mask errors with silent failures
  - Don't return incorrect default values
  
  **Recommended Agent Profile**:
  - **Category**: `unspecified-high` (error handling is important)
  
  **Acceptance Criteria**:
  - [ ] All extraction wrapped in try/except
  - [ ] Missing data returns None (not 0)
  - [ ] Errors logged with stock code for debugging
  
  **QA Scenarios**:
  ```
  Scenario: Test error handling with broken fixtures
    Tool: Bash (pytest)
    Steps:
      1. Test with empty HTML
      2. Test with missing table
      3. Test with malformed numeric values
    Expected: Graceful handling, returns empty structure, no crashes
    Evidence: .sisyphus/evidence/task-7-error-handling.log
  ```
  
  **Commit**: YES - "feat: Implement comprehensive financial data extraction with error handling"

---


### Wave 3: Schema & Data Updates

- [x] **8. Extend Stock Schema with New Fields**

  **What to do**:
  - Update `backend/app/schemas/stock.py` to add new fields to Stock schema
  - Add `FinancialMetrics` nested model (optional, for organization)
  - Update field descriptions
  - Ensure all new fields are Optional (can be missing)
  
  **Changes to `stock.py`**:
  ```python
  class Stock(BaseModel):
      # Existing fields...
      ticker: str
      name: str
      current_price: Optional[float] = None
      per: Optional[float] = None
      pbr: Optional[float] = None
      eps: Optional[float] = None
      bps: Optional[float] = None
      
      # New comprehensive financial metrics
      revenue: Optional[float] = Field(None, description="Annual revenue (매출액)")
      operating_profit: Optional[float] = Field(None, description="Operating profit (영업이익)")
      net_profit: Optional[float] = Field(None, description="Net profit (당기순이익)")
      operating_margin: Optional[float] = Field(None, description="Operating margin %% (영업이익률)")
      net_margin: Optional[float] = Field(None, description="Net margin %% (순이익률)")
      roe: Optional[float] = Field(None, description="Return on Equity %%")
      debt_ratio: Optional[float] = Field(None, description="Debt ratio %% (부채비율)")
      current_ratio: Optional[float] = Field(None, description="Current ratio %% (당좌비율)")
      reserve_ratio: Optional[float] = Field(None, description="Reserve ratio %% (유보율)")
      dividend_per_share: Optional[float] = Field(None, description="Dividend per share (주당배당금)")
      dividend_payout_ratio: Optional[float] = Field(None, description="Dividend payout ratio %% (배당성향)")
      eps_growth_yoy: Optional[float] = Field(None, description="EPS year-over-year growth %%")
      fiscal_year: Optional[str] = Field(None, description="Fiscal year of data (e.g., '2024.12')")
  ```
  
  **Must NOT do**:
  - Don't remove existing fields
  - Don't make new fields required (use Optional)
  - Don't forget Field descriptions
  
  **Recommended Agent Profile**:
  - **Category**: `quick`
  
  **Parallelization**:
  - **Can Run In Parallel**: YES (Wave 3)
  - **Blocked By**: Task 1-3
  - **Blocks**: Task 15-18
  
  **References**:
  - `backend/app/schemas/stock.py` - Current Stock model
  - Design document from Task 2
  
  **Acceptance Criteria**:
  - [ ] All 15+ new fields added to Stock schema
  - [ ] All fields are Optional with proper types
  - [ ] Field descriptions added
  - [ ] Pydantic model validates without errors
  
  **QA Scenarios**:
  ```
  Scenario: Verify schema validation
    Tool: Bash (python)
    Steps:
      1. Import Stock from schemas.stock
      2. Create Stock instance with new fields
      3. Verify validation passes
    Expected: Model validates correctly
    Evidence: .sisyphus/evidence/task-8-schema-validation.log
  ```
  
  **Commit**: NO (part of Wave 3 group)

- [x] **9. Update Batch Collection for New Fields**

  **What to do**:
  - Update `backend/batch/collect_data.py` to include new fields in data collection
  - Modify the row dictionary to include all extracted metrics
  - Ensure CSV/JSON output includes new columns
  
  **Changes to `collect_data.py`**:
  ```python
  # In collect_kospi_data() function
  row = {
      # Existing fields...
      'ticker': ticker,
      'name': quote.get('name'),
      'current_price': quote.get('current_price'),
      
      # New comprehensive financial metrics
      'revenue': quote.get('revenue'),
      'operating_profit': quote.get('operating_profit'),
      'net_profit': quote.get('net_profit'),
      'operating_margin': quote.get('operating_margin'),
      'net_margin': quote.get('net_margin'),
      'roe': quote.get('roe'),
      'debt_ratio': quote.get('debt_ratio'),
      'current_ratio': quote.get('current_ratio'),
      'reserve_ratio': quote.get('reserve_ratio'),
      'dividend_per_share': quote.get('dividend_per_share'),
      'dividend_payout_ratio': quote.get('dividend_payout_ratio'),
      'eps_growth_yoy': quote.get('eps_growth_yoy'),
      'fiscal_year': quote.get('fiscal_year'),
  }
  ```
  
  **Must NOT do**:
  - Don't break existing column order unnecessarily
  - Don't skip any new fields
  - Don't change the file output format
  
  **Recommended Agent Profile**:
  - **Category**: `quick`
  
  **Acceptance Criteria**:
  - [ ] All new fields included in row dictionary
  - [ ] CSV output includes new columns
  - [ ] JSON output includes new fields
  
  **QA Scenarios**:
  ```
  Scenario: Test batch collection output
    Tool: Bash (python + file check)
    Steps:
      1. Run collect_data with --limit 1
      2. Check CSV file has new columns
      3. Check JSON file has new fields
    Expected: Output files contain all new fields
    Evidence: .sisyphus/evidence/task-9-batch-output.txt
  ```
  
  **Commit**: NO (part of Wave 3 group)

- [x] **10. Update Data Loader for New Fields**

  **What to do**:
  - Update `backend/app/services/data_loader.py` to load new fields
  - Update `create_stock_from_row()` function
  - Ensure cache includes new fields
  
  **Changes to `data_loader.py`**:
  ```python
  def create_stock_from_row(row: Dict[str, Any]) -> Stock:
      return Stock(
          # Existing fields...
          ticker=row['ticker'],
          name=row.get('name'),
          current_price=parse_float(row.get('current_price')),
          
          # New fields
          revenue=parse_float(row.get('revenue')),
          operating_profit=parse_float(row.get('operating_profit')),
          net_profit=parse_float(row.get('net_profit')),
          operating_margin=parse_float(row.get('operating_margin')),
          net_margin=parse_float(row.get('net_margin')),
          roe=parse_float(row.get('roe')),
          debt_ratio=parse_float(row.get('debt_ratio')),
          current_ratio=parse_float(row.get('current_ratio')),
          reserve_ratio=parse_float(row.get('reserve_ratio')),
          dividend_per_share=parse_float(row.get('dividend_per_share')),
          dividend_payout_ratio=parse_float(row.get('dividend_payout_ratio')),
          eps_growth_yoy=parse_float(row.get('eps_growth_yoy')),
          fiscal_year=row.get('fiscal_year'),
      )
  ```
  
  **Must NOT do**:
  - Don't forget to handle None/NaN values
  - Don't break existing stock loading
  
  **Recommended Agent Profile**:
  - **Category**: `quick`
  
  **Acceptance Criteria**:
  - [ ] Data loader loads all new fields
  - [ ] Stock objects created with new fields
  - [ ] Cache includes new data
  
  **QA Scenarios**:
  ```
  Scenario: Test data loading
    Tool: Bash (pytest)
    Steps:
      1. Load test CSV with new fields
      2. Verify Stock objects have all fields
      3. Check cache contains new data
    Expected: All fields loaded correctly
    Evidence: .sisyphus/evidence/task-10-data-loader.log
  ```
  
  **Commit**: YES - "feat: Extend data pipeline for comprehensive financial metrics"

---


### Wave 4: Testing

- [x] **11. Write Unit Tests for Extraction Functions**

  **What to do**:
  - Create `backend/tests/test_naver_crawler.py`
  - Write unit tests for `_get_latest_valid_data()`
  - Write unit tests for `_find_row()`
  - Write unit tests for `_parse_numeric()`
  - Write unit tests for `_extract_all_metrics()` with mock fixtures
  
  **Test Structure**:
  ```python
  import pytest
  import pandas as pd
  from backend.app.services.naver_crawler import (
      _get_latest_valid_data,
      _find_row,
      _parse_numeric,
      _extract_all_metrics,
  )
  
  class TestGetLatestValidData:
      def test_returns_latest_non_null(self):
          series = pd.Series([1.0, 2.0, None, 4.0], index=['2022', '2023', '2024', '2025'])
          value, year = _get_latest_valid_data(series)
          assert value == 4.0
          assert year == '2025'
      
      def test_handles_all_nulls(self):
          series = pd.Series([None, None, None])
          value, year = _get_latest_valid_data(series)
          assert value is None
          assert year is None
      
      def test_handles_dash_values(self):
          series = pd.Series(['-', '-', '10.5'])
          value, year = _get_latest_valid_data(series)
          assert value == 10.5
  
  class TestFindRow:
      def test_finds_row_by_keyword(self):
          df = pd.DataFrame({'A': [1, 2, 3]}, index=['ROE(%)', 'EPS', 'PER'])
          result = _find_row(df, 'ROE')
          assert result is not None
          assert result['A'] == 1
      
      def test_returns_none_if_not_found(self):
          df = pd.DataFrame({'A': [1, 2]}, index=['EPS', 'PER'])
          result = _find_row(df, 'ROE')
          assert result is None
  
  class TestParseNumeric:
      def test_parses_float(self):
          assert _parse_numeric('123.45') == 123.45
      
      def test_parses_with_comma(self):
          assert _parse_numeric('1,234,567') == 1234567
      
      def test_handles_em_tags(self):
          assert _parse_numeric('<em class="f_up">-77,303</em>') == -77303
      
      def test_returns_none_for_dash(self):
          assert _parse_numeric('-') is None
      
      def test_returns_none_for_empty(self):
          assert _parse_numeric('') is None
  
  class TestExtractAllMetrics:
      def test_extracts_all_metrics_from_fixture(self, load_sk_hynix_fixture):
          result = _extract_all_metrics(load_sk_hynix_fixture)
          assert 'revenue' in result
          assert 'operating_profit' in result
          assert 'roe' in result
          assert 'debt_ratio' in result
          # ... verify all expected keys
  ```
  
  **Must NOT do**:
  - Don't skip edge cases
  - Don't write tests that depend on real network calls
  
  **Recommended Agent Profile**:
  - **Category**: `deep` (test logic)
  
  **Parallelization**:
  - **Can Run In Parallel**: YES (Wave 4)
  - **Blocked By**: Task 4-7
  - **Blocks**: Task 15-18
  
  **References**:
  - Test fixtures from Task 3
  - Implementation from Task 4-7
  
  **Acceptance Criteria**:
  - [ ] Unit tests for all helper functions
  - [ ] Tests cover edge cases (nulls, dashes, missing rows)
  - [ ] Tests use mock fixtures (no network calls)
  
  **QA Scenarios**:
  ```
  Scenario: Run unit tests
    Tool: Bash (pytest)
    Steps:
      1. Run pytest tests/test_naver_crawler.py::TestGetLatestValidData -v
      2. Run pytest tests/test_naver_crawler.py::TestParseNumeric -v
      3. Verify all tests pass
    Expected: 100% unit test pass rate
    Evidence: .sisyphus/evidence/task-11-unit-tests.log
  ```
  
  **Commit**: NO (part of Wave 4 group)

- [x] **12. Write Integration Tests with Mock HTML**

  **What to do**:
  - Write integration tests for `_get_financial_data()`
  - Test with different fixtures (full data, missing data, edge cases)
  - Verify complete extraction pipeline works end-to-end
  
  **Test Structure**:
  ```python
  class TestFinancialDataIntegration:
      def test_extracts_full_data(self, sk_hynix_html):
          # Mock requests.get to return sk_hynix_html
          result = _get_financial_data('000660')
          assert result['revenue'] is not None
          assert result['roe'] is not None
          assert result['debt_ratio'] is not None
          assert result['eps_growth_yoy'] is not None
      
      def test_handles_missing_data_gracefully(self, missing_data_html):
          result = _get_financial_data('000001')
          # Should return empty structure without crashing
          assert result['revenue'] is None
          assert result['roe'] is None
      
      def test_handles_malformed_html(self, malformed_html):
          result = _get_financial_data('999999')
          # Should handle gracefully, return empty structure
          assert isinstance(result, dict)
  ```
  
  **Must NOT do**:
  - Don't make real HTTP calls in tests
  - Don't skip error case testing
  
  **Recommended Agent Profile**:
  - **Category**: `deep`
  
  **Acceptance Criteria**:
  - [ ] Integration tests with all fixtures
  - [ ] Mock HTTP responses (no real calls)
  - [ ] Error cases covered
  
  **QA Scenarios**:
  ```
  Scenario: Run integration tests
    Tool: Bash (pytest)
    Steps:
      1. Run pytest tests/test_naver_crawler.py::TestFinancialDataIntegration -v
      2. Verify all fixture scenarios pass
    Expected: All integration tests pass
    Evidence: .sisyphus/evidence/task-12-integration-tests.log
  ```
  
  **Commit**: NO (part of Wave 4 group)

- [x] **13. Write Edge Case Tests**

  **What to do**:
  - Test with completely empty table
  - Test with HTML missing the target table
  - Test with network timeout
  - Test with negative values (e.g., operating loss)
  - Test with zero values
  - Test with extremely large numbers
  
  **Edge Cases to Cover**:
  1. Empty HTML response
  2. Table exists but has no data rows
  3. All metrics are missing (all '-')
  4. Network timeout
  5. HTTP error (404, 500)
  6. Negative operating profit (loss)
  7. Zero EPS (avoid division by zero in growth calc)
  8. Very large revenue numbers (trillions)
  
  **Must NOT do**:
  - Don't skip network error cases
  - Don't assume data is always present
  
  **Recommended Agent Profile**:
  - **Category**: `deep`
  
  **Acceptance Criteria**:
  - [ ] Edge cases documented
  - [ ] Tests for each edge case
  - [ ] No unhandled exceptions
  
  **QA Scenarios**:
  ```
  Scenario: Test edge cases
    Tool: Bash (pytest)
    Steps:
      1. Run edge case tests
      2. Verify no exceptions raised
      3. Check graceful degradation
    Expected: All edge cases handled gracefully
    Evidence: .sisyphus/evidence/task-13-edge-cases.log
  ```
  
  **Commit**: NO (part of Wave 4 group)

- [x] **14. Create Test Fixtures for Various Stock Types**

  **What to do**:
  - Create fixtures for different stock types:
    - Large cap (SK hynix, Samsung) - full data
    - Mid cap - some missing data
    - Small cap - minimal data
    - Loss-making company - negative profits
    - Newly listed - limited history
  
  **Fixtures**:
  1. `fixtures/large_cap_full.html` - Complete data set
  2. `fixtures/mid_cap_partial.html` - Some missing metrics
  3. `fixtures/small_cap_minimal.html` - Only basic metrics
  4. `fixtures/loss_making.html` - Negative operating profit
  5. `fixtures/newly_listed.html` - Limited fiscal years
  
  **Must NOT do**:
  - Don't use real copyrighted HTML
  - Create representative test data manually
  
  **Recommended Agent Profile**:
  - **Category**: `quick`
  
  **Acceptance Criteria**:
  - [ ] 5+ different fixture types
  - [ ] Fixtures cover major scenarios
  - [ ] All fixtures parseable by BeautifulSoup
  
  **QA Scenarios**:
  ```
  Scenario: Verify fixtures
    Tool: Bash (python)
    Steps:
      1. Load each fixture with BeautifulSoup
      2. Verify table structure is valid
      3. Check data variety
    Expected: All fixtures valid and diverse
    Evidence: .sisyphus/evidence/task-14-fixtures-verified.txt
  ```
  
  **Commit**: YES - "test: Add comprehensive test suite for Naver crawler"

---


### Wave 5: Final Integration

- [x] **15. Full Batch Job Test Run**

  **What to do**:
  - Run `python -m backend.batch.collect_data --limit 10` (test mode)
  - Verify CSV file created with all new columns
  - Verify JSON file created with all new fields
  - Check that data is correct for all 10 stocks
  - Verify rate limiting is working (should take ~20 seconds for 10 stocks)
  
  **Validation Steps**:
  ```bash
  # Run batch collection
  cd /home/dduneon/stock
  python -m backend.batch.collect_data --limit 10
  
  # Check output files
  ls -la data/stocks_*.csv data/stocks_*.json
  
  # Verify new columns exist
  head -1 data/stocks_*.csv | tr ',' '\n' | grep -E 'revenue|operating_profit|roe|debt_ratio'
  
  # Check JSON structure
  python -c "import json; data = json.load(open('data/stocks_*.json')); print(list(data[0].keys()))"
  ```
  
  **Must NOT do**:
  - Don't run full collection during testing (takes too long)
  - Don't skip verification of data types
  
  **Recommended Agent Profile**:
  - **Category**: `unspecified-high`
  
  **Parallelization**:
  - **Can Run In Parallel**: YES (Wave 5)
  - **Blocked By**: Task 11-14
  - **Blocks**: None
  
  **References**:
  - `backend/batch/collect_data.py`
  - Test fixtures from Task 3, 14
  
  **Acceptance Criteria**:
  - [ ] Batch job runs without errors
  - [ ] CSV has all new columns
  - [ ] JSON has all new fields
  - [ ] Data types are correct
  - [ ] Rate limiting preserved
  
  **QA Scenarios**:
  ```
  Scenario: Full batch test run
    Tool: Bash (timing + validation)
    Steps:
      1. Run collect_data --limit 10
      2. Measure time (should be ~20s with rate limiting)
      3. Verify output files
      4. Check data integrity
    Expected: Successful collection with all fields
    Evidence: .sisyphus/evidence/task-15-batch-run.log
  ```
  
  **Commit**: NO (part of Wave 5 group)

- [x] **16. Verify API Endpoints Still Work**

  **What to do**:
  - Start backend server
  - Test `/api/stocks` endpoint
  - Test `/api/stocks/{ticker}` endpoint
  - Test `/api/recommendations` endpoint
  - Verify responses include new fields
  - Ensure backward compatibility (old fields still present)
  
  **Test Commands**:
  ```bash
  # Start backend
  cd backend && uvicorn main:app --reload &
  
  # Test endpoints
  curl http://localhost:8000/api/stocks | jq '.[0] | keys'
  curl http://localhost:8000/api/stocks/005930 | jq '.revenue, .roe, .operating_profit'
  curl http://localhost:8000/api/recommendations | jq '.[0] | keys'
  ```
  
  **Must NOT do**:
  - Don't break existing API contracts
  - Don't remove existing response fields
  
  **Recommended Agent Profile**:
  - **Category**: `unspecified-high`
  
  **Acceptance Criteria**:
  - [ ] All endpoints return 200
  - [ ] Responses include new fields
  - [ ] Old fields still present
  - [ ] No breaking changes
  
  **QA Scenarios**:
  ```
  Scenario: Test API endpoints
    Tool: Bash (curl)
    Steps:
      1. Start backend server
      2. Call /api/stocks
      3. Verify response contains new fields
      4. Test individual stock endpoint
    Expected: All endpoints working with new data
    Evidence: .sisyphus/evidence/task-16-api-test.log
  ```
  
  **Commit**: NO (part of Wave 5 group)

- [x] **17. Performance Test (Rate Limiting Check)**

  **What to do**:
  - Verify rate limiting is still working (1-2 second delays)
  - Test with 5 stocks and measure time
  - Should take ~7-12 seconds (5 stocks × 1-2s delay + processing)
  - Check that no rate limit errors from Naver
  
  **Test Script**:
  ```python
  import time
  from backend.app.services.naver_crawler import get_stock_quote
  
  tickers = ['005930', '000660', '035420', '051910', '005380']
  start = time.time()
  
  for ticker in tickers:
      result = get_stock_quote(ticker)
      print(f"{ticker}: {result.get('name')}")
  
  elapsed = time.time() - start
  print(f"Total time: {elapsed:.2f}s")
  assert 5 <= elapsed <= 15, f"Rate limiting may be broken: {elapsed}s"
  ```
  
  **Must NOT do**:
  - Don't disable rate limiting for speed
  - Don't hammer Naver servers
  
  **Recommended Agent Profile**:
  - **Category**: `quick`
  
  **Acceptance Criteria**:
  - [ ] Rate limiting preserved (1-2s delays)
  - [ ] No 429/403 errors from Naver
  - [ ] Reasonable total time for test set
  
  **QA Scenarios**:
  ```
  Scenario: Verify rate limiting
    Tool: Bash (python)
    Steps:
      1. Run performance test with 5 stocks
      2. Measure total time
      3. Check for rate limit errors
    Expected: 5-15 seconds total, no errors
    Evidence: .sisyphus/evidence/task-17-performance.log
  ```
  
  **Commit**: NO (part of Wave 5 group)

- [x] **18. Documentation Update**

  **What to do**:
  - Update `backend/app/services/AGENTS.md` with new crawler details
  - Add docstrings to all new functions
  - Update main project README if needed
  - Document new fields in Stock schema
  
  **Documentation to Update**:
  1. `backend/app/services/AGENTS.md` - Add section on comprehensive crawler
  2. Function docstrings in `naver_crawler.py`
  3. Schema field descriptions in `stock.py`
  4. Add example of new fields to API documentation
  
  **Example Docstring**:
  ```python
  def _get_financial_data(ticker: str) -> Dict[str, Any]:
      """
      Extract comprehensive financial data from Naver Finance.
      
      Fetches the 주요재무정보 table and extracts all available metrics
      including revenue, profits, ratios, and valuation metrics.
      
      Args:
          ticker: 6-digit Korean stock code (e.g., '005930')
          
      Returns:
          Dictionary containing financial metrics:
          - revenue: Annual revenue
          - operating_profit: Operating profit
          - net_profit: Net profit
          - operating_margin: Operating margin (%)
          - net_margin: Net margin (%)
          - roe: Return on equity (%)
          - debt_ratio: Debt ratio (%)
          - current_ratio: Current ratio (%)
          - reserve_ratio: Reserve ratio (%)
          - per: Price-to-earnings ratio
          - pbr: Price-to-book ratio
          - eps: Earnings per share
          - bps: Book value per share
          - dividend_per_share: Dividend per share
          - dividend_yield: Dividend yield (%)
          - dividend_payout_ratio: Dividend payout ratio (%)
          - eps_growth_yoy: EPS year-over-year growth (%)
          - fiscal_year: Fiscal year of data (e.g., '2024.12')
          
      Returns empty dict with None values if extraction fails.
      """
  ```
  
  **Must NOT do**:
  - Don't skip docstrings
  - Don't leave undocumented public functions
  
  **Recommended Agent Profile**:
  - **Category**: `writing`
  
  **Acceptance Criteria**:
  - [ ] All functions have docstrings
  - [ ] AGENTS.md updated
  - [ ] New fields documented
  
  **QA Scenarios**:
  ```
  Scenario: Verify documentation
    Tool: Bash (grep/find)
    Steps:
      1. Check all new functions have docstrings
      2. Verify AGENTS.md has crawler section
      3. Check README if updated
    Expected: Documentation complete
    Evidence: .sisyphus/evidence/task-18-documentation.txt
  ```
  
  **Commit**: YES - "docs: Add comprehensive documentation for Naver crawler"

---

## Success Criteria

### Verification Commands

```bash
# Run all crawler tests
cd /home/dduneon/stock/backend && pytest tests/test_naver_crawler.py -v

# Run batch collection (10 stocks test)
cd /home/dduneon/stock && python -m backend.batch.collect_data --limit 10

# Verify data files contain new fields
head -1 data/stocks_*.csv | tr ',' '\n' | sort | uniq

# Check specific new fields exist
head -1 data/stocks_*.csv | grep -E "revenue|operating_profit|net_profit|current_ratio|reserve_ratio|dividend_per_share"

# Run existing API tests to verify backward compatibility
cd /home/dduneon/stock/backend && pytest tests/ -k "test_get_recommendations or test_get_stock_detail" -v

# Start backend and test API manually
cd /home/dduneon/stock/backend && uvicorn main:app --reload &
curl -s http://localhost:8000/api/stocks/005930 | jq '.revenue, .roe, .operating_profit'

# Check test coverage
cd /home/dduneon/stock/backend && pytest tests/test_naver_crawler.py --cov=app.services.naver_crawler --cov-report=term-missing
```

### Final Checklist

- [ ] All 15+ financial metrics extracted correctly from Naver Finance
- [ ] Batch job runs successfully for test set (10 stocks)
- [ ] CSV output contains all new columns with correct data
- [ ] JSON output contains all new fields with correct data
- [ ] All unit tests pass (>90% coverage for crawler module)
- [ ] All integration tests pass with mock fixtures
- [ ] All edge case tests pass (empty data, errors, etc.)
- [ ] API endpoints remain backward compatible
- [ ] Rate limiting preserved (1-2s delays between requests)
- [ ] No breaking changes to existing functionality
- [ ] Documentation updated (AGENTS.md, docstrings, README if needed)
- [ ] Test fixtures created for various scenarios
- [ ] Performance acceptable (no degradation)

### Definition of Success

The project successfully replaces the existing Naver Finance crawler with a comprehensive, extensible version that:

1. **Extracts all metrics** from the 기업실적분석 table using robust pandas parsing
2. **Integrates seamlessly** with existing batch workflow and data pipeline
3. **Maintains backward compatibility** - all existing APIs work unchanged
4. **Has comprehensive test coverage** - unit, integration, and edge case tests
5. **Preserves rate limiting** - respects Naver's servers with 1-2s delays
6. **Is well-documented** - clear docstrings and updated AGENTS.md

The new crawler serves as a foundation for future financial data enhancements.
