# Frontend Improvements - Toss UI + Enhanced Detail Page

## TL;DR

> **Quick Summary**: Toss UI 스타일의 shadcn/ui를 적용하고, 종목 상세 페이지를 API의 전체 데이터로 개선하며, dark mode와 skeleton loading을 추가합니다.
> 
> **Deliverables**:
> - shadcn/ui 설치 및 Toss 디자인 토큰 적용
> - 상세 페이지: 재무제표, valuation 지표, 섹터 데이터 표시
> - Dark mode 및 skeleton loading 추가
> - 빈 값 정렬 검증 (기존 구현 확인)
> 
> **Estimated Effort**: Large
> **Parallel Execution**: YES - 3 waves
> **Critical Path**: shadcn/ui 설치 → Tailwind config → 상세 페이지 개선

---

## Context

### Original Request
- Toss UI 스타일 적용 (shadcn/ui 사용)
- 종목 상세 페이지 개선 (API 데이터 연결 + 더 많은 콘텐츠)
- Dark mode, skeleton loading 등 modern UI 추가
- 빈 값 정렬 수정

### Interview Summary
**Key Discussions**:
- UI 스타일: shadcn/ui 컴포넌트库 설치 (Toss 디자인 적용)
- 상세 페이지: 재무제표 + valuation 지표 + 섹터 비교 데이터
- Modern UI: dark mode, skeleton loading
- 빈 값 정렬: 이미 구현됨 → 검증만 진행

**Research Findings**:
- Backend API: StockDetail schema에 모든 재무 데이터 포함 (revenue, operating_profit, net_profit, dividend_yield, operating_margin, net_margin, current_ratio, reserve_ratio 등)
- Toss 디자인 토큰: grey900=#191f28, blue500=#3182f6, green500=#31b653, red500=#f45452
- 기존 상세 페이지: PER, PBR, EPS, BPS만 표시 → 나머지 필드 미연결

### Metis Review
**Identified Gaps** (addressed):
- 빈 값 정렬: 이미 구현됨 → 검증 태스크로 변경
- shadcn/ui 설치 복잡도 → 단계별로 진행
- 상세 페이지 필드 과多 → 우선순위 8-10개 지표만 선별

---

## Work Objectives

### Core Objective
 Toss-inspired modern UI로 개선 + 상세 페이지에 API의 전체 데이터 연결

### Concrete Deliverables
- Toss 디자인 토큰이 적용된 shadcn/ui 컴포넌트
- 재무제표/valuation 데이터가 표시되는 개선된 상세 페이지
- Dark mode 지원
- Skeleton loading 상태

### Definition of Done
- [ ] shadcn/ui 설치 완료 및 Toss 색상 적용
- [ ] 상세 페이지에서 10+ 재무 지표 확인 가능
- [ ] Dark mode 토글 작동 확인
- [ ]Skeleton loading 표시 확인
- [ ] 빈 값 정렬 동작 검증

### Must Have
- shadcn/ui Button, Card, Table, Badge, Skeleton, Toggle 컴포넌트
- Toss 색상 테마 (grey900, blue500, green500, red500)
- 상세 페이지에 표시할 핵심 지표 8-10개

### Must NOT Have (Guardrails)
- ❌ Backend API 변경 (이미 완성됨)
- ❌ 새로운 페이지 라우트 추가
- ❌ 새로운 API 엔드포인트 생성
- ❌ 데이터베이스 변경
- ❌ 인증 관련 수정

---

## Verification Strategy (MANDATORY)

> **ZERO HUMAN INTERVENTION** — ALL verification is agent-executed.
> Acceptance criteria requiring "user manually tests/confirms" are FORBIDDEN.

### Test Decision
- **Infrastructure exists**: YES
- **Automated tests**: Existing Playwright e2e tests + Agent-Executed QA
- **Framework**: Playwright
- **Agent-Executed QA**: Every task includes specific QA scenarios

### QA Policy
Every task includes agent-executed QA scenarios:
- Frontend verification via Playwright (navigate, screenshot, assert DOM)
- API verification via curl (fetch data, assert fields)
- Evidence saved to `.sisyphus/evidence/`

---

## Execution Strategy

### Parallel Execution Waves

```
Wave 1 (Foundation - shadcn/ui setup):
├── Task 1: Initialize shadcn/ui configuration
├── Task 2: Update Tailwind config with Toss design tokens
├── Task 3: Install core shadcn/ui components
├── Task 4: Configure dark mode in Tailwind + Next.js
└── Task 5: Create reusable Skeleton component

Wave 2 (Detail Page Enhancement):
├── Task 6: Map all StockDetail API fields
├── Task 7: Add profitability metrics section
├── Task 8: Add dividend data section
├── Task 9: Add stability/liquidity metrics section
├── Task 10: Add fiscal year info section
└── Task 11: Create sector comparison section (if API supports)

Wave 3 (Modernization + Verification):
├── Task 12: Replace spinners with skeleton loading
├── Task 13: Add dark mode toggle UI
├── Task 14: Apply Toss colors to existing components
├── Task 15: Verify empty value sorting (existing code)
└── Task 16: Run e2e tests and verify
```

---

## TODOs

- [x] 1. Initialize shadcn/ui configuration

  **What to do**:
  - Run `npx shadcn@latest init` in frontend directory
  - Configure with Tailwind CSS, CSS variables, React Server Components support
  - Set base path to `@/components`
  - Select default options for color scheme

  **Must NOT do**:
  - Don't modify existing component files yet

  **Recommended Agent Profile**:
  - **Category**: `unspecified-high`
    - Reason: Requires CLI setup and configuration decisions
  - **Skills**: []

  **Parallelization**:
  - **Can Run In Parallel**: YES
  - **Parallel Group**: Wave 1 (with Tasks 2, 3)
  - **Blocks**: Tasks 2, 3, 4, 5
  - **Blocked By**: None

  **References**:
  - shadcn/ui docs: `https://ui.shadcn.com/docs/installation/next.js`
  - Current tailwind.config.js: `frontend/tailwind.config.js`
  - Current globals.css: `frontend/app/globals.css`

  **Acceptance Criteria**:
  - [ ] shadcn.json created in frontend root
  - [ ] components.json created
  - [ ] tailwind.config.js updated with shadcn paths

  **QA Scenarios**:
  ```
  Scenario: Verify shadcn initialization
    Tool: Bash
    Preconditions: In frontend directory
    Steps:
      1. Run ls -la to check config files exist
      2. Check package.json for new dependencies
    Expected Result: shadcn.json and components.json present
    Evidence: .sisyphus/evidence/task-1-shadcn-init.{ext}
  ```

- [x] 2. Update Tailwind config with Toss design tokens

  **What to do**:
  - Add Toss-inspired color palette to tailwind.config.js:
    - grey-900: #191f28 (primary text)
    - grey-800: #333d4b
    - grey-700: #4e5968
    - grey-500: #8b95a1
    - grey-300: #d1d6db
    - grey-100: #f2f4f6
    - blue-500: #3182f6 (primary brand)
    - green-500: #31b653 (gain)
    - red-500: #f45452 (loss)
  - Keep existing #0045F6, #E5493A, #2972FF for backward compatibility initially

  **Must NOT do**:
  - Don't remove existing color tokens completely (for gradual migration)

  **Recommended Agent Profile**:
  - **Category**: `quick`
    - Reason: Configuration file edit only
  - **Skills**: []

  **Parallelization**:
  - **Can Run In Parallel**: YES
  - **Parallel Group**: Wave 1 (with Tasks 1, 3, 4, 5)
  - **Blocks**: Task 14
  - **Blocked By**: Task 1

  **References**:
  - Current tailwind.config.js: `frontend/tailwind.config.js`
  - shadcn theming: `https://ui.shadcn.com/docs/theming`

  **Acceptance Criteria**:
  - [ ] New Toss colors added to tailwind.config.js
  - [ ] Colors accessible via className (e.g., text-grey-900)

  **QA Scenarios**:
  ```
  Scenario: Verify Toss colors available
    Tool: Bash
    Preconditions: Build complete
    Steps:
      1. grep "grey-900" frontend/tailwind.config.js
    Expected Result: Color token present
    Evidence: .sisyphus/evidence/task-2-colors.{ext}
  ```

- [x] 3. Install core shadcn/ui components

  **What to do**:
  - Install essential components:
    - npx shadcn@latest add button
    - npx shadcn@latest add card
    - npx shadcn@latest add badge
    - npx shadcn@latest add skeleton
    - npx shadcn@latest add toggle
    - npx shadcn@latest add select
  - Components go to frontend/components/ui/

  **Must NOT do**:
  - Don't replace existing components yet (migration later)

  **Recommended Agent Profile**:
  - **Category**: `unspecified-high`
    - Reason: Multiple CLI commands, file generation
  - **Skills**: []

  **Parallelization**:
  - **Can Run In Parallel**: YES
  - **Parallel Group**: Wave 1 (with Tasks 1, 2, 4, 5)
  - **Blocks**: Tasks 14
  - **Blocked By**: Tasks 1, 2

  **References**:
  - shadcn components: `https://ui.shadcn.com/docs/components`
  - Current Header.tsx: `frontend/components/Header.tsx`
  - Current EmptyState.tsx: `frontend/components/EmptyState.tsx`

  **Acceptance Criteria**:
  - [ ] Button, Card, Badge, Skeleton, Toggle, Select in components/ui/
  - [ ] All components render without errors

  **QA Scenarios**:
  ```
  Scenario: Verify components installed
    Tool: Bash
    Preconditions: Components added
    Steps:
      1. ls frontend/components/ui/ | wc -l
      2. Check each component file exists
    Expected Result: 6+ component files present
    Evidence: .sisyphus/evidence/task-3-components.{ext}
  ```

- [x] 4. Configure dark mode in Tailwind + Next.js

  **What to do**:
  - Enable dark mode strategy in tailwind.config.js: "class"
  - Add dark mode CSS variables to globals.css
  - Add darkMode provider to layout.tsx
  - Test toggle functionality

  **Must NOT do**:
  - Don't implement toggle UI yet (Task 13)

  **Recommended Agent Profile**:
  - **Category**: `unspecified-high`
    - Reason: Requires configuration + CSS + React context
  - **Skills**: []

  **Parallelization**:
  - **Can Run In Parallel**: YES
  - **Parallel Group**: Wave 1 (with Tasks 1, 2, 3, 5)
  - **Blocks**: Tasks 12, 13, 14
  - **Blocked By**: Tasks 1, 2

  **References**:
  - shadcn dark mode: `https://ui.shadcn.com/docs/theming#dark-mode`
  - Current layout.tsx: `frontend/app/layout.tsx`
  - Current globals.css: `frontend/app/globals.css`

  **Acceptance Criteria**:
  - [ ] darkMode: "class" in tailwind.config.js
  - [ ] Dark mode CSS variables in globals.css
  - [ ] Toggle works when html has "dark" class

  **QA Scenarios**:
  ```
  Scenario: Verify dark mode CSS variables
    Tool: Bash
    Preconditions: Files modified
    Steps:
      1. grep "dark:" frontend/app/globals.css | head -10
    Expected Result: Dark mode styles present
    Evidence: .sisyphus/evidence/task-4-darkmode.{ext}
  ```

- [x] 5. Create reusable Skeleton component

  **What to do**:
  - Use shadcn Skeleton as base
  - Create stock-specific skeleton variants:
    - StockCardSkeleton (for grid display)
    - StockTableRowSkeleton (for table rows)
    - StockDetailSkeleton (for detail page)
  - Ensure animations match Toss aesthetic

  **Must NOT do**:
  - Don't replace loading spinners yet (Task 12)

  **Recommended Agent Profile**:
  - **Category**: `quick`
    - Reason: Component creation with clear patterns
  - **Skills**: []

  **Parallelization**:
  - **Can Run In Parallel**: YES
  - **Parallel Group**: Wave 1 (with Tasks 1, 2, 3, 4)
  - **Blocks**: Task 12
  - **Blocked By**: Task 3

  **References**:
  - shadcn Skeleton: `https://ui.shadcn.com/components/skeleton`
  - Current loading states: `frontend/app/stocks/page.tsx` (spinner pattern)

  **Acceptance Criteria**:
  - [ ] StockCardSkeleton component created
  - [ ] StockDetailSkeleton component created
  - [ ] Animations working (pulse effect)

  **QA Scenarios**:
  ```
  Scenario: Verify skeleton components work
    Tool: Playwright
    Preconditions: Dev server running
    Steps:
      1. Navigate to /stocks
      2. Take screenshot before data loads
      3. Verify skeleton animation visible
    Expected Result: Skeleton displays with pulse animation
    Evidence: .sisyphus/evidence/task-5-skeleton.{ext}
  ```

- [x] 6. Map all StockDetail API fields to frontend types

  **What to do**:
  - Update frontend/types/index.ts to match backend StockDetail schema:
    - Add missing fields: revenue, operating_profit, net_profit, operating_margin, net_margin, current_ratio, reserve_ratio, dividend_per_share, dividend_yield, dividend_payout_ratio, fiscal_year
  - Create proper TypeScript interfaces

  **Must NOT do**:
  - Don't add fields not in backend schema

  **Recommended Agent Profile**:
  - **Category**: `quick`
    - Reason: Type definition only
  - **Skills**: []

  **Parallelization**:
  - **Can Run In Parallel**: YES
  - **Parallel Group**: Wave 2 (with Tasks 7, 8, 9, 10, 11)
  - **Blocks**: Tasks 7, 8, 9, 10, 11
  - **Blocked By**: Wave 1

  **References**:
  - Backend schema: `backend/app/schemas/stock.py` (StockDetail class)
  - Current types: `frontend/types/index.ts`

  **Acceptance Criteria**:
  - [ ] All StockDetail fields in TypeScript
  - [ ] No TypeScript errors when importing

  **QA Scenarios**:
  ```
  Scenario: Verify types match API
    Tool: Bash
    Preconditions: Types updated
    Steps:
      1. cd frontend && npx tsc --noEmit 2>&1 | head -20
    Expected Result: No type errors
    Evidence: .sisyphus/evidence/task-6-types.{ext}
  ```

- [x] 7. Add profitability metrics section to detail page

  **What to do**:
  - Add new section in stock detail page for profitability:
    - ROE (already exists but ensure visible)
    - Operating Margin: operating_margin field
    - Net Margin: net_margin field
    - EPS Growth YoY: eps_growth_yoy field
  - Use Card component with proper Toss styling
  - Color code: green for good (>15%), yellow for moderate (5-15%), red for low (<5%)

  **Must NOT do**:
  - Don't break existing layout

  **Recommended Agent Profile**:
  - **Category**: `visual-engineering`
    - Reason: UI component with data visualization
  - **Skills**: []

  **Parallelization**:
  - **Can Run In Parallel**: YES
  - **Parallel Group**: Wave 2 (with Tasks 6, 8, 9, 10, 11)
  - **Blocks**: Task 16
  - **Blocked By**: Task 6

  **References**:
  - Current detail page metrics: `frontend/app/stock/[ticker]/page.tsx` (lines 640-717)
  - shadcn Card: `https://ui.shadcn.com/components/card`
  - Toss profit indicators: green (#31b653) for positive

  **Acceptance Criteria**:
  - [ ] Operating margin displays correctly
  - [ ] Net margin displays correctly
  - [ ] Color coding matches thresholds
  - [ ] Shows '-' when data is null

  **QA Scenarios**:
  ```
  Scenario: Verify profitability section displays
    Tool: Bash + Playwright
    Preconditions: Dev server running, API has data
    Steps:
      1. curl -s http://localhost:8000/api/stocks/005930 | jq '.operating_margin, .net_margin'
      2. Navigate to /stocks/005930
      3. Screenshot the profitability section
    Expected Result: Values match API, '-' shown if null
    Evidence: .sisyphus/evidence/task-7-profitability.{ext}
  ```

- [x] 8. Add dividend data section to detail page

  **What to do**:
  - Add dividend information section:
    - Dividend Per Share (DPS): dividend_per_share
    - Dividend Yield: dividend_yield
    - Payout Ratio: dividend_payout_ratio
    - Fiscal Year: fiscal_year
  - Format as percentage where appropriate

  **Must NOT do**:
  - Don't duplicate existing data

  **Recommended Agent Profile**:
  - **Category**: `visual-engineering`
    - Reason: UI component with data display
  - **Skills**: []

  **Parallelization**:
  - **Can Run In Parallel**: YES
  - **Parallel Group**: Wave 2 (with Tasks 6, 7, 9, 10, 11)
  - **Blocks**: Task 16
  - **Blocked By**: Task 6

  **References**:
  - Current detail page structure: `frontend/app/stock/[ticker]/page.tsx`
  - shadcn Badge: `https://ui.shadcn.com/components/badge`

  **Acceptance Criteria**:
  - [ ] Dividend yield displays as percentage
  - [ ] Payout ratio displays as percentage
  - [ ] Shows '-' when data is null
  - [ ] Fiscal year displays

  **QA Scenarios**:
  ```
  Scenario: Verify dividend section displays
    Tool: Bash + Playwright
    Preconditions: Dev server running
    Steps:
      1. curl -s http://localhost:8000/api/stocks/005930 | jq '.dividend_yield, .dividend_payout_ratio'
      2. Navigate to /stocks/005930
      3. Verify dividend section visible
    Expected Result: Data matches API
    Evidence: .sisyphus/evidence/task-8-dividend.{ext}
  ```

- [x] 9. Add stability/liquidity metrics section

  **What to do**:
  - Add section for company stability:
    - Current Ratio: current_ratio
    - Reserve Ratio: reserve_ratio
    - Debt Ratio: debt_ratio (already exists, ensure visible)
  - Color code: green for safe, yellow for caution, red for risky

  **Must NOT do**:
  - Don't duplicate debt_ratio (already shown in table)

  **Recommended Agent Profile**:
  - **Category**: `visual-engineering`
    - Reason: UI component with data visualization
  - **Skills**: []

  **Parallelization**:
  - **Can Run In Parallel**: YES
  - **Parallel Group**: Wave 2 (with Tasks 6, 7, 8, 10, 11)
  - **Blocks**: Task 16
  - **Blocked By**: Task 6

  **References**:
  - Current stocks table shows debt_ratio: `frontend/app/stocks/page.tsx`

  **Acceptance Criteria**:
  - [ ] Current ratio displays
  - [ ] Reserve ratio displays
  - [ ] Color coding matches thresholds

  **QA Scenarios**:
  ```
  Scenario: Verify stability metrics
    Tool: Bash + Playwright
    Preconditions: Dev server running
    Steps:
      1. curl -s http://localhost:8000/api/stocks/005930 | jq '.current_ratio, .reserve_ratio'
      2. Navigate to /stocks/005930
      3. Check stability section
    Expected Result: Values match API
    Evidence: .sisyphus/evidence/task-9-stability.{ext}
  ```

- [x] 10. Add fiscal year info section

  **What to do**:
  - Display fiscal year information:
    - fiscal_year field
    - When data was last updated
  - Show as metadata/timestamp format

  **Must NOT do**:
  - Don't make it prominent (secondary info)

  **Recommended Agent Profile**:
  - **Category**: `quick`
    - Reason: Simple display component
  - **Skills**: []

  **Parallelization**:
  - **Can Run In Parallel**: YES
  - **Parallel Group**: Wave 2 (with Tasks 6, 7, 8, 9, 11)
  - **Blocks**: Task 16
  - **Blocked By**: Task 6

  **References**:
  - Current footer pattern: `frontend/app/stock/[ticker]/page.tsx` (disclaimer area)

  **Acceptance Criteria**:
  - [ ] Fiscal year displays
  - [ ] Shows '-' when null

  **QA Scenarios**:
  ```
  Scenario: Verify fiscal year displays
    Tool: Bash + Playwright
    Preconditions: Dev server running
    Steps:
      1. curl -s http://localhost:8000/api/stocks/005930 | jq '.fiscal_year'
      2. Navigate to /stocks/005930
    Expected Result: Shows fiscal year or '-'
    Evidence: .sisyphus/evidence/task-10-fiscal.{ext}
  ```

- [x] 11. Create sector comparison section

  **What to do**:
  - Check if sector data available from API
  - If available, display sector comparison:
    - Show sector name
    - Show how stock compares to sector average
  - Note: Depends on API supporting sector comparison endpoint

  **Must NOT do**:
  - Don't create fake data

  **Recommended Agent Profile**:
  - **Category**: `visual-engineering`
    - Reason: Data comparison visualization
  - **Skills**: []

  **Parallelization**:
  - **Can Run In Parallel**: YES
  - **Parallel Group**: Wave 2 (with Tasks 6, 7, 8, 9, 10)
  - **Blocks**: Task 16
  - **Blocked By**: Task 6

  **References**:
  - sector field in StockDetail: `backend/app/schemas/stock.py`

  **Acceptance Criteria**:
  - [ ] If API has sector data, display it
  - [ ] If not available, show "Sector data unavailable"

  **QA Scenarios**:
  ```
  Scenario: Check sector availability
    Tool: Bash
    Preconditions: API running
    Steps:
      1. curl -s http://localhost:8000/api/stocks/005930 | jq '.sector'
    Expected Result: Sector value or null
    Evidence: .sisyphus/evidence/task-11-sector.{ext}
  ```

- [ ] 12. Replace spinners with skeleton loading

  **What to do**:
  - Replace existing spinner loading with Skeleton components:
    - Home page: Skeleton for stock cards
    - Stocks page: Skeleton for table rows
    - Detail page: Skeleton for all sections
  - Ensure skeletons show expected layout structure

  **Must NOT do**:
  - Don't remove error handling

  **Recommended Agent Profile**:
  - **Category**: `visual-engineering`
    - Reason: UI state management
  - **Skills**: []

  **Parallelization**:
  - **Can Run In Parallel**: YES
  - **Parallel Group**: Wave 3 (with Tasks 13, 14, 15, 16)
  - **Blocks**: Task F3
  - **Blocked By**: Tasks 4, 5

  **References**:
  - Current loading states: `frontend/app/stocks/page.tsx` (lines 416-432)
  - shadcn Skeleton: `https://ui.shadcn.com/components/skeleton`

  **Acceptance Criteria**:
  - [ ] All pages show skeleton during load
  - [ ] Skeleton matches content layout
  - [ ] Animation runs smoothly

  **QA Scenarios**:
  ```
  Scenario: Verify skeleton loading
    Tool: Playwright
    Preconditions: Dev server running
    Steps:
      1. Navigate to /stocks
      2. Immediately screenshot
      3. Verify skeleton visible (not spinner)
    Expected Result: Skeleton with pulse animation
    Evidence: .sisyphus/evidence/task-12-skeleton.{ext}
  ```

- [ ] 13. Add dark mode toggle UI

  **What to do**:
  - Add toggle button to Header component
  - Use shadcn Toggle component
  - Persist preference in localStorage
  - Apply dark class to html element

  **Must NOT do**:
  - Don't break existing navigation

  **Recommended Agent Profile**:
  - **Category**: `visual-engineering`
    - Reason: UI component with state
  - **Skills**: []

  **Parallelization**:
  - **Can Run In Parallel**: YES
  - **Parallel Group**: Wave 3 (with Tasks 12, 14, 15, 16)
  - **Blocks**: Task F3
  - **Blocked By**: Task 4

  **References**:
  - Current Header: `frontend/components/Header.tsx`
  - shadcn Toggle: `https://ui.shadcn.com/components/toggle`

  **Acceptance Criteria**:
  - [ ] Toggle button visible in Header
  - [ ] Clicking toggles dark mode
  - [ ] Preference persists on reload

  **QA Scenarios**:
  ```
  Scenario: Verify dark mode toggle
    Tool: Playwright
    Preconditions: Dev server running
    Steps:
      1. Navigate to home page
      2. Click dark mode toggle
      3. Screenshot to verify dark mode
      4. Reload page
      5. Verify preference persisted
    Evidence: .sisyphus/evidence/task-13-darktoggle.{ext}
  ```

- [ ] 14. Apply Toss colors to existing components

  **What to do**:
  - Migrate existing components to use Toss colors:
    - Header: Use grey-900 for text
    - Stock cards: Use blue-500 for primary, green-500/red-500 for gains/losses
    - Tables: Use grey-300 for borders
  - Update Tailwind classes throughout

  **Must NOT do**:
  - Don't break existing functionality

  **Recommended Agent Profile**:
  - **Category**: `visual-engineering`
    - Reason: Style refactoring across components
  - **Skills**: []

  **Parallelization**:
  - **Can Run In Parallel**: YES
  - **Parallel Group**: Wave 3 (with Tasks 12, 13, 15, 16)
  - **Blocks**: Task F3
  - **Blocked By**: Tasks 2, 3, 4

  **References**:
  - Current colors: grep -r "#0045F6\|#E5493A\|#2972FF" frontend/
  - Toss tokens: grey900=#191f28, blue500=#3182f6

  **Acceptance Criteria**:
  - [ ] Major components use new Toss colors
  - [ ] No broken layouts

  **QA Scenarios**:
  ```
  Scenario: Verify color migration
    Tool: Playwright
    Preconditions: Dev server running
    Steps:
      1. Navigate to home page
      2. Screenshot
      3. Compare with old screenshot (if exists)
    Expected Result: Consistent Toss-style colors
    Evidence: .sisyphus/evidence/task-14-colors.{ext}
  ```

- [ ] 15. Verify empty value sorting behavior

  **What to do**:
  - Verify existing sorting logic in stocks page:
    - Lines 328-330 already handle undefined/null
    - Values with undefined sort to end
  - Run Playwright test to confirm behavior

  **Must NOT do**:
  - Don't modify existing working code

  **Recommended Agent Profile**:
  - **Category**: `quick`
    - Reason: Verification only, no code changes
  - **Skills**: []

  **Parallelization**:
  - **Can Run In Parallel**: YES
  - **Parallel Group**: Wave 3 (with Tasks 12, 13, 14, 16)
  - **Blocks**: Task F3
  - **Blocked By**: Wave 1

  **References**:
  - Current sorting: `frontend/app/stocks/page.tsx` (lines 288-334)

  **Acceptance Criteria**:
  - [ ] Stocks with null values sort to end
  - [ ] Both asc and desc handle nulls correctly

  **QA Scenarios**:
  ```
  Scenario: Verify null sorting
    Tool: Playwright
    Preconditions: Dev server running, stocks page
    Steps:
      1. Click PER sort header
      2. Scroll to see if stocks with '-' are at bottom
      3. Click reverse sort
      4. Verify nulls still at end (or top depending on direction)
    Expected Result: Null/undefined values at end
    Evidence: .sisyphus/evidence/task-15-sort.{ext}
  ```

- [ ] 16. Run e2e tests and verify

  **What to do**:
  - Run full Playwright test suite:
    - cd frontend && playwright test
  - Fix any broken tests
  - Verify all pages load correctly

  **Must NOT do**:
  - Don't skip failing tests

  **Recommended Agent Profile**:
  - **Category**: `unspecified-high`
    - Reason: Test execution and debugging
  - **Skills**: []

  **Parallelization**:
  - **Can Run In Parallel**: NO (final verification)
  - **Parallel Group**: Wave 3 (last task)
  - **Blocks**: Final Verification Wave
  - **Blocked By**: Tasks 6-15

  **References**:
  - E2E tests: `frontend/e2e/`
  - Current tests: stocks.spec.ts, stock-detail.spec.ts

  **Acceptance Criteria**:
  - [ ] All e2e tests pass
  - [ ] No console errors

  **QA Scenarios**:
  ```
  Scenario: Run e2e test suite
    Tool: Bash
    Preconditions: Dev server running
    Steps:
      1. cd frontend && playwright test
    Expected Result: All tests pass
    Evidence: .sisyphus/evidence/task-16-e2e.{ext}
  ```

---

## Final Verification Wave

---

## Final Verification Wave

- [ ] F1. **Plan Compliance Audit** — Verify all must-have items implemented
- [ ] F2. **Code Quality Review** — Check no `as any`, proper types
- [ ] F3. **Visual QA** — Screenshot comparison for UI consistency
- [ ] F4. **E2E Test Verification** — All Playwright tests pass

---

## Commit Strategy

- **1**: `chore(ui): init shadcn/ui with toss theme` — tailwind.config.js, components.json
- **2**: `feat(ui): add toss design tokens` — tailwind.config.js extended
- **3**: `feat(ui): install core shadcn components` — package.json, components/
- **4**: `feat(ui): add dark mode support` — globals.css, layout.tsx
- **5**: `feat(ui): create skeleton components` — components/ui/skeleton.tsx
- **6**: `feat(detail): add profitability metrics` — stock/[ticker]/page.tsx
- **7**: `feat(detail): add dividend data section` — stock/[ticker]/page.tsx
- **8**: `feat(detail): add stability metrics` — stock/[ticker]/page.tsx
- **9**: `feat(detail): add fiscal info` — stock/[ticker]/page.tsx
- **10**: `feat(ui): add skeleton loading states` — page.tsx files
- **11**: `feat(ui): add dark mode toggle` — header.tsx
- **12**: `test: verify empty sorting behavior` — playwright test
- **13**: `test: run full e2e` — playwright

---

## Success Criteria

### Verification Commands
```bash
# Verify shadcn/ui installed
grep -E "@radix-ui|class-variance-authority" frontend/package.json

# Verify dark mode CSS variables
grep "dark:" frontend/app/globals.css | head -5

# Verify detail page API fields
curl -s http://localhost:8000/api/stocks/005930 | jq '.dividend_yield, .operating_margin'

# Run e2e tests
cd frontend && playwright test e2e/
```

### Final Checklist
- [ ] All "Must Have" present
- [ ] All "Must NOT Have" absent
- [ ] All e2e tests pass
- [ ] Visual QA screenshots captured
