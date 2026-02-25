# 국내 주식 추천 서비스 개발 플랜

## TL;DR

> **Quick Summary**: KOSPI上市企業 대상 가치투자 추천 웹서비스. PER, PBR, Forward P/E 등 재무지표 기반 scoring 알고리즘으로 저평가 주식을 선별하고 Toss증권 스타일의 모던 UI로 제공

> **Deliverables**:
> - Next.js + FastAPI 웹 애플리케이션
> - 일일 배치 작업 (pykrx 데이터 수집)
> - 대시보드/주식 리스트/검색/상세 페이지
> - TDD 테스트 인프라 (pytest + vitest)

> **Estimated Effort**: 1-2주 (MVP)
> **Parallel Execution**: YES - 3 waves
> **Critical Path**: Backend API → Data Pipeline → Frontend Integration → QA

---

## Context

### Original Request
사용자가 국내 주식 추천 서비스를 개발하고자 함:
- KOSPI 상장 기업 대상
- PER, PBR, Forward P/E 등 지표 기반 추천
- Toss증권 스타일 세련된 F/E
- 일일 배치 작업으로 데이터 최신화
- 로그인 기능은 나중에 구현

### Interview Summary

**기술 스택 결정**:
- Frontend: React + Next.js (App Router)
- Backend: Python FastAPI
- Data Source: pykrx + 금융위원회 API + 크롤링
- Test: TDD (pytest + vitest)

**MVP Scope**:
- 대시보드 (추천 주식 목록)
- 주식 리스트 (필터/정렬)
- 검색 (Autocomplete)
- 상세 페이지 (PER/PBR/현재가)
- 배치 작업 (일일 데이터 수집)

**Research Findings**:
- pykrx: 무료, KOSPI/KOSDAQ 지원, 15분 지연 데이터
- Toss UI: 3단 구조, 빨강=상승/파랑=하락, Pretendard, 4px 스페이싱
- 추천 알고리즘: 가치(40%) + 성장(25%) + 수익성(20%) + 모멘텀(15%)

### Metis Review

**Identified Gaps** (addressed):
- 데이터Freshness: pykrx 지연 데이터 (15분) - MVP에서는 허용
- MVP Feature Lock: 포트폴리오, 알림, 백테스팅 등은 MVP에서 제외
- Disclaimer 필수: 금융 데이터 고지문 추가
- Edge Cases: PER/PBR 마이너스, 거래정지, 시장 공휴일 처리

---

## Work Objectives

### Core Objective
KOSPI 상장 기업 중 저평가 주식을 재무지표 기반으로 추천하는 웹서비스 MVP 개발

### Concrete Deliverables
- `frontend/`: Next.js 15+ 웹 애플리케이션
- `backend/`: FastAPI REST API 서버
- `batch/`: pykrx 기반 일일 데이터 수집 스크립트
- `tests/`: pytest (backend) + vitest (frontend) 테스트

### Definition of Done
- [ ] 로컬 환경에서 `npm run dev` + `uvicorn main:app` 정상 실행
- [ ] http://localhost:3000 접근 시 대시보드 렌더링
- [ ] http://localhost:8000/api/stocks API 응답
- [ ] 배치 스크립트 실행 시 CSV 저장
- [ ] pytest + vitest 테스트 통과

### Must Have
- PER, PBR, Forward P/E 지표 표시
- 시가총액, 현재가, 등락률 표시
- 검색 Autocomplete
- Toss증권 스타일 UI (红色 상승, 青色 하락)
- 금융 고지 Disclaimer

### Must NOT Have (Guardrails)
- ❌ 실제 거래 연동 (매수/매도)
- ❌ 포트폴리오 추적 기능
- ❌ 백테스팅/시뮬레이션
- ❌ 사용자별 맞춤 가중치
- ❌ 알림/알림장
- ❌ 모바일 앱 (Desktop만)

---

## Verification Strategy

### Test Decision
- **Infrastructure exists**: NO (Greenfield)
- **Automated tests**: TDD (pytest + vitest)
- **Framework**: pytest (Python), vitest (JS/TS)

### QA Policy
모든 task는 agent-executed QA scenarios 포함:
- **Backend API**: curl로 엔드포인트 검증
- **Frontend**: Playwright로 브라우저 렌더링 검증
- **Batch**: Python 스크립트 실행 후 CSV/JSON 검증

---

## Execution Strategy

### Parallel Execution Waves

```
Wave 1 (Foundation - 모든 작업의 기반):
├── Task 1: 프로젝트 세팅 (Next.js + FastAPI + 디렉토리 구조)
├── Task 2: Backend API 스캐폴딩 (FastAPI routes)
├── Task 3: Frontend 세팅 (Next.js + Tailwind + Shadcn/ui)
├── Task 4: pykrx 데이터 수집 스크립트 (단위 테스트 포함)
└── Task 5: TypeScript types/schema 정의

Wave 2 (Core Features - 최대 병렬):
├── Task 6: 추천 알고리즘 구현 (scoring 로직 + 테스트)
├── Task 7: REST API endpoints (/stocks, /recommendations, /search)
├── Task 8: 대시보드 페이지 (추천 주식 목록)
├── Task 9: 주식 리스트 페이지 (필터/정렬)
└── Task 10: 검색 기능 (Autocomplete)

Wave 3 (Integration + Polish):
├── Task 11: 상세 페이지 (PER/PBR/현재가)
├── Task 12: Toss UI 스타일 적용 (색상, 타이포그래피)
├── Task 13: 에러 처리 (Error Boundary, Empty State)
├── Task 14: 배치 작업 ( scheduler or cron)
└── Task 15: Disclaimer 고지문 추가

Wave FINAL (Verification):
├── Task F1: End-to-End QA (Playwright)
├── Task F2: Batch job verification
└── Task F3: Plan compliance audit
```

### Dependency Matrix
- **1-5**: — (독립 실행 가능)
- **6**: 4 (데이터 필요)
- **7**: 2, 5 (API + Schema)
- **8**: 6, 7 (추천 + API)
- **9**: 7 (API)
- **10**: 7 (API)
- **11**: 8, 9, 10 (통합)
- **12**: 8 (대시보드 스타일)
- **13**: 11 (상세 페이지 에러 처리)
- **14**: 4 (pykrx)
- **15**: 8 (대시보드 고지)

---

## TODOs

- [ ] 1. 프로젝트 세팅 (Next.js + FastAPI + 디렉토리 구조)

  **What to do**:
  - Next.js 15 프로젝트 생성 (App Router, TypeScript)
  - FastAPI 프로젝트 생성
  - 디렉토리 구조 설계 (frontend/, backend/, batch/, tests/)
  - Git 초기화 및 .gitignore 설정

  **Must NOT do**:
  - 불필요한 테스트 파일 생성 (Task 4에서一起)

  **Recommended Agent Profile**:
  - **Category**: `quick`
  - **Skills**: [`git-master`]

  **Parallelization**:
  - **Can Run In Parallel**: YES
  - **Parallel Group**: Wave 1
  - **Blocks**: All subsequent tasks
  - **Blocked By**: None

  **References**:
  - Official docs: `https://nextjs.org/docs/app` - Next.js 15 App Router
  - Official docs: `https://fastapi.tiangolo.com/` - FastAPI Getting Started

  **Acceptance Criteria**:
  - [ ] `frontend/` 디렉토리에서 `npm run dev` 성공
  - [ ] `backend/` 디렉토리에서 `uvicorn main:app --reload` 성공
  - [ ] http://localhost:3000 접근 시 Next.js 페이지 렌더링
  - [ ] http://localhost:8000/docs 접근 시 Swagger UI 렌더링

  **QA Scenarios**:
  ```
  Scenario: Frontend 서버 실행 확인
    Tool: Bash
    Preconditions: frontend 디렉토리
    Steps:
      1. cd frontend && npm run dev &
      2. sleep 10
      3. curl -s http://localhost:3000 | head -20
    Expected Result: HTML 페이지 반환 (200 OK)
    Evidence: .sisyphus/evidence/task-1-frontend-startup.txt

  Scenario: Backend 서버 실행 확인
    Tool: Bash
    Preconditions: backend 디렉토리
    Steps:
      1. cd backend && uvicorn main:app --reload &
      2. sleep 5
      3. curl -s http://localhost:8000/docs | head -20
    Expected Result: Swagger HTML 반환
    Evidence: .sisyphus/evidence/task-1-backend-startup.txt
  ```

  **Commit**: YES
  - Message: `chore: initialize project structure`
  - Files: `frontend/`, `backend/`

---

- [ ] 2. Backend API 스캐폴딩 (FastAPI)

  **What to do**:
  - FastAPI 앱 생성 (main.py)
  - CORS 설정
  - Health check endpoint (`/api/health`)
  - Stocks router 생성

  **Must NOT do**:
  - 실제 데이터 연동 (Task 4에서)

  **Recommended Agent Profile**:
  - **Category**: `quick`
  - **Skills**: []

  **Parallelization**:
  - **Can Run In Parallel**: YES
  - **Parallel Group**: Wave 1
  - **Blocks**: Task 7
  - **Blocked By**: None

  **References**:
  - `backend/main.py` - FastAPI app initialization pattern

  **Acceptance Criteria**:
  - [ ] GET /api/health → {"status": "ok"}
  - [ ] GET /api/stocks → 200 OK (empty array initially)

  **QA Scenarios**:
  ```
  Scenario: Health check endpoint
    Tool: Bash
    Steps:
      1. curl -s http://localhost:8000/api/health
    Expected Result: {"status":"ok","timestamp":"..."}
    Evidence: .sisyphus/evidence/task-2-health-check.json

  Scenario: Stocks endpoint returns 200
    Tool: Bash
    Steps:
      1. curl -s -o /dev/null -w "%{http_code}" http://localhost:8000/api/stocks
    Expected Result: 200
    Evidence: .sisyphus/evidence/task-2-stocks-endpoint.txt
  ```

  **Commit**: YES
  - Message: `feat: add FastAPI scaffolding with health check`
  - Files: `backend/main.py`, `backend/app/`

---

- [ ] 3. Frontend 세팅 (Next.js + Tailwind + Shadcn/ui)

  **What to do**:
  - Tailwind CSS 설정
  - Shadcn/ui 초기화
  - Toss 스타일 색상 설정 (빨강=상승, 파랑=하락)
  - Pretendard 폰트 설정

  **Must NOT do**:
  - 페이지 라우팅 설정 (Task 8에서)

  **Recommended Agent Profile**:
  - **Category**: `visual-engineering`
  - **Skills**: [`frontend-ui-ux`]

  **Parallelization**:
  - **Can Run In Parallel**: YES
  - **Parallel Group**: Wave 1
  - **Blocks**: Task 8, 9, 10, 11, 12
  - **Blocked By**: None

  **References**:
  - Toss UI: Primary #0045F6, 상승 #E5493A, 하락 #2972FF
  - Spacing: 4px baseline
  - Font: Pretendard

  **Acceptance Criteria**:
  - [ ] Tailwind CSS 빌드 성공
  - [ ] Shadcn/ui 컴포넌트 사용 가능
  - [ ] Pretendard 폰트 렌더링

  **QA Scenarios**:
  ```
  Scenario: Tailwind 빌드 확인
    Tool: Bash
    Preconditions: frontend 디렉토리
    Steps:
      1. npm run build 2>&1 | tail -20
    Expected Result: Build successful (no errors)
    Evidence: .sisyphus/evidence/task-3-tailwind-build.txt
  ```

  **Commit**: YES
  - Message: `feat: setup Tailwind CSS and Shadcn/ui`
  - Files: `frontend/`

---

- [ ] 4. pykrx 데이터 수집 스크립트 (단위 테스트 포함)

  **What to do**:
  - pykrx 설치 (`pip install pykrx`)
  - KOSPI 전종목 시세 수집 함수
  - PER, PBR, 시가총액 등 핵심 지표 추출
  - CSV/JSON으로 저장
  - pytest 테스트 작성

  **Must NOT do**:
  - 복잡한 전처리 (MVP에서는 단순 저장)

  **Recommended Agent Profile**:
  - **Category**: `deep`
  - **Skills**: []

  **Parallelization**:
  - **Can Run In Parallel**: YES
  - **Parallel Group**: Wave 1
  - **Blocks**: Task 6, 14
  - **Blocked By**: None

  **References**:
  - pykrx docs: `https://github.com/ sharesenj pykrx`
  - Sample: `from pykrx import stock`

  **Acceptance Criteria**:
  - [ ] pykrx 설치 성공
  - [ ] KOSPI 전종목 데이터 CSV 저장 (최소 100개)
  - [ ] pytest tests/test_pykrx.py → PASS

  **QA Scenarios**:
  ```
  Scenario: pykrx 데이터 수집
    Tool: Bash
    Preconditions: backend 디렉토리
    Steps:
      1. pip install pykrx pandas
      2. python -c "from pykrx import stock; print(stock.get_market_ticker_list())" | head -5
    Expected Result: 티커 목록 출력
    Evidence: .sisyphus/evidence/task-4-pykrx-install.txt

  Scenario: 데이터 CSV 저장
    Tool: Bash
    Preconditions: backend 디렉토리
    Steps:
      1. python batch/collect_data.py
      2. ls -la data/
    Expected Result: stocks.csv 파일 생성
    Evidence: .sisyphus/evidence/task-4-csv-save.txt
  ```

  **Commit**: YES
  - Message: `feat: add pykrx data collection script`
  - Files: `backend/batch/collect_data.py`, `tests/test_pykrx.py`

---

- [ ] 5. TypeScript types/schema 정의

  **What to do**:
  - Backend: Pydantic models (Stock, Recommendation)
  - Frontend: TypeScript interfaces
  - 공통 schema 정의

  **Must NOT do**:
  - 실제 데이터 매핑 (Task 6에서)

  **Recommended Agent Profile**:
  - **Category**: `quick`
  - **Skills**: []

  **Parallelization**:
  - **Can Run In Parallel**: YES
  - **Parallel Group**: Wave 1
  - **Blocks**: Task 6, 7
  - **Blocked By**: None

  **References**:
  - `backend/app/schemas/` - Pydantic model patterns

  **Acceptance Criteria**:
  - [ ] Stock interface 정의 완료
  - [ ] Recommendation interface 정의 완료

  **QA Scenarios**:
  ```
  Scenario: Type check
    Tool: Bash
    Preconditions: frontend 디렉토리
    Steps:
      1. npx tsc --noEmit
    Expected Result: No errors
    Evidence: .sisyphus/evidence/task-5-types.txt
  ```

  **Commit**: YES
  - Message: `types: define TypeScript and Pydantic schemas`
  - Files: `frontend/types/`, `backend/app/schemas/`

---

- [ ] 6. 추천 알고리즘 구현 (scoring 로직 + 테스트)

  **What to do**:
  - 가치 지표: PER, PBR 점수화 (낮을수록 高점)
  - 성장 지표: EPS 성장률
  - 수익성: ROE
  - 모멘텀: 3개월 수익률
  - 가중치: 가치 40% + 성장 25% + 수익성 20% + 모멘텀 15%
  - pytest 테스트 작성

  **Must NOT do**:
  - 복잡한 산업별 BENCHMARK (MVP에서는 단순 순위)

  **Recommended Agent Profile**:
  - **Category**: `deep`
  - **Skills**: []

  **Parallelization**:
  - **Can Run In Parallel**: NO
  - **Parallel Group**: Wave 2
  - **Blocks**: Task 8
  - **Blocked By**: Task 4, 5

  **References**:
  - Backend: `backend/app/services/recommendation.py`
  - Algorithm:価値 40% + 성장 25% + 수익성 20% + 모멘텀 15%

  **Acceptance Criteria**:
  - [ ] 추천 점수 계산 함수 구현
  - [ ] Top 20 추천 목록 반환
  - [ ] pytest tests/test_recommendation.py → PASS

  **QA Scenarios**:
  ```
  Scenario: 추천 알고리즘 테스트
    Tool: Bash
    Preconditions: backend 디렉토리
    Steps:
      1. python -m pytest tests/test_recommendation.py -v
    Expected Result: All tests PASS
    Evidence: .sisyphus/evidence/task-6-algo-test.txt

  Scenario: 추천 결과 검증
    Tool: Bash
    Preconditions: backend 실행 중
    Steps:
      1. curl -s http://localhost:8000/api/recommendations | python -m json.tool | head -30
    Expected Result: JSON array, 최소 10개 항목
    Evidence: .sisyphus/evidence/task-6-recommendations.json
  ```

  **Commit**: YES
  - Message: `feat: implement stock recommendation algorithm`
  - Files: `backend/app/services/recommendation.py`, `tests/test_recommendation.py`

---

- [ ] 7. REST API endpoints (/stocks, /recommendations, /search)

  **What to do**:
  - GET /api/stocks - 전종목 목록
  - GET /api/stocks/{ticker} - 개별 종목 상세
  - GET /api/recommendations - 추천 목록
  - GET /api/search?q={query} - 검색

  **Must NOT do**:
  - Pagination (MVP에서는 Limit만)

  **Recommended Agent Profile**:
  - **Category**: `unspecified-high`
  - **Skills**: []

  **Parallelization**:
  - **Can Run In Parallel**: NO
  - **Parallel Group**: Wave 2
  - **Blocks**: Task 8, 9, 10
  - **Blocked By**: Task 2, 5

  **References**:
  - FastAPI router patterns
  - http://localhost:8000/docs - API 문서

  **Acceptance Criteria**:
  - [ ] GET /api/stocks → 200 OK (배열 반환)
  - [ ] GET /api/stocks/005930 → 200 OK (개별 종목)
  - [ ] GET /api/recommendations → 200 OK
  - [ ] GET /api/search?q=삼성 → 200 OK

  **QA Scenarios**:
  ```
  Scenario: All API endpoints
    Tool: Bash
    Preconditions: backend 실행 중
    Steps:
      1. curl -s http://localhost:8000/api/stocks | python -m json.tool | wc -l
      2. curl -s http://localhost:8000/api/stocks/005930 | python -m json.tool | head -20
      3. curl -s http://localhost:8000/api/recommendations | python -m json.tool | head -20
      4. curl -s "http://localhost:8000/api/search?q=삼성" | python -m json.tool | head -20
    Expected Result: All return 200 OK with valid JSON
    Evidence: .sisyphus/evidence/task-7-apis.txt
  ```

  **Commit**: YES
  - Message: `feat: implement REST API endpoints`
  - Files: `backend/app/routers/`

---

- [ ] 8. 대시보드 페이지 (추천 주식 목록)

  **What to do**:
  - / 페이지 (대시보드)
  - 추천 주식 카드 그리드
  - Toss 스타일 적용 (색상, 간격)
  - Disclaimer 고지문

  **Must NOT do**:
  - 복잡한 차트 (Task 11에서 basic만)

  **Recommended Agent Profile**:
  - **Category**: `visual-engineering`
  - **Skills**: [`frontend-ui-ux`]

  **Parallelization**:
  - **Can Run In Parallel**: NO
  - **Parallel Group**: Wave 2
  - **Blocks**: Task 12, 15
  - **Blocked By**: Task 3, 6, 7

  **References**:
  - Toss UI: 빨강=상승 #E5493A, 파랑=하락 #2972FF
  - Layout: 3단 구조 (헤더+사이드바+본문)

  **Acceptance Criteria**:
  - [ ] http://localhost:3000 접근 시 대시보드 렌더링
  - [ ] 추천 주식 목록 (최소 10개) 표시
  - [ ] 각 카드에 PER, PBR, 현재가 표시

  **QA Scenarios**:
  ```
  Scenario: 대시보드 렌더링
    Tool: Playwright
    Preconditions: frontend + backend 실행 중
    Steps:
      1. npx playwright test --reporter=line
      2. 或: browser.goto("http://localhost:3000")
      3. screenshot()
    Expected Result: 추천 목록 렌더링 확인
    Evidence: .sisyphus/evidence/task-8-dashboard.png
  ```

  **Commit**: YES
  - Message: `feat: implement dashboard page`
  - Files: `frontend/app/page.tsx`

---

- [ ] 9. 주식 리스트 페이지 (필터/정렬)

  **What to do**:
  - /stocks 페이지
  - 전종목 테이블视图
  - 정렬: 시가총액, PER, PBR, 등락률
  - 필터: PER 범위, 시가총액 최소

  **Must NOT do**:
  - 무한 스크롤 (MVP에서는 pagination)

  **Recommended Agent Profile**:
  - **Category**: `visual-engineering`
  - **Skills**: [`frontend-ui-ux`]

  **Parallelization**:
  - **Can Run In Parallel**: NO
  - **Parallel Group**: Wave 2
  - **Blocks**: None
  - **Blocked By**: Task 7

  **References**:
  - Toss: 테이블 행 40-48px, 호버 강조
  - Shadcn/ui: Table 컴포넌트

  **Acceptance Criteria**:
  - [ ] /stocks 접근 시 전종목 테이블 표시
  - [ ] PER 클릭 시 오름차순 정렬
  - [ ] 시가총액 필터 작동

  **QA Scenarios**:
  ```
  Scenario: 주식 리스트 필터
    Tool: Playwright
    Preconditions: frontend 실행 중
    Steps:
      1. goto("http://localhost:3000/stocks")
      2. click("[data-testid=sort-per]")
      3. screenshot()
    Expected Result: PER 순 정렬 확인
    Evidence: .sisyphus/evidence/task-9-stock-list.png
  ```

  **Commit**: YES
  - Message: `feat: implement stock list page with filters`
  - Files: `frontend/app/stocks/page.tsx`

---

- [ ] 10. 검색 기능 (Autocomplete)

  **What to do**:
  - 헤더 검색 입력창
  - Autocomplete 드롭다운
  - 검색 결과 페이지 (/search?q=...)
  - Toss 스타일 검색 UI

  **Must NOT**:
  - Debounce 과도하게 긴 지연 (300ms 권장)

  **Recommended Agent Profile**:
  - **Category**: `visual-engineering`
  - **Skills**: [`frontend-ui-ux`]

  **Parallelization**:
  - **Can Run In Parallel**: NO
  - **Parallel Group**: Wave 2
  - **Blocks**: None
  - **Blocked By**: Task 7

  **References**:
  - Toss: 검색창 Always-visible, 실시간 제안

  **Acceptance Criteria**:
  - [ ] 검색창 입력 시 자동완성 드롭다운
  - [ ] "삼성" 입력 시 삼성전자 등 결과 표시
  - [ ] 검색 결과 페이지 작동

  **QA Scenarios**:
  ```
  Scenario: 검색 Autocomplete
    Tool: Playwright
    Preconditions: frontend 실행 중
    Steps:
      1. goto("http://localhost:3000")
      2. fill("[data-testid=search-input]", "삼성")
      3. wait(500)
      4. screenshot()
    Expected Result: 자동완성 드롭다운 표시
    Evidence: .sisyphus/evidence/task-10-search.png
  ```

  **Commit**: YES
  - Message: `feat: implement search with autocomplete`
  - Files: `frontend/components/Search.tsx`

---

- [ ] 11. 상세 페이지 (PER/PBR/현재가)

  **What to do**:
  - /stock/[ticker] 페이지
  - 기업 기본 정보
  - PER, PBR, Forward P/E 표시
  - 현재가, 등락률, 시가총액
  - basic 차트 (Lightweight Charts)

  **Must NOT**:
  - 복잡한 기술적 지표 (이동평균선, RSI 등)

  **Recommended Agent Profile**:
  - **Category**: `visual-engineering`
  - **Skills**: [`frontend-ui-ux`]

  **Parallelization**:
  - **Can Run In Parallel**: NO
  - **Parallel Group**: Wave 3
  - **Blocks**: None
  - **Blocked By**: Task 8, 9, 10

  **References**:
  - Lightweight Charts: `https://tradingview.github.io/lightweight-charts/`
  - Toss: 차트 패널 시스템

  **Acceptance Criteria**:
  - [ ] /stock/005930 접근 시 삼성전자 상세 정보
  - [ ] PER, PBR, Forward P/E 표시
  - [ ] 차트 렌더링

  **QA Scenarios**:
  ```
  Scenario: 상세 페이지
    Tool: Playwright
    Preconditions: frontend 실행 중
    Steps:
      1. goto("http://localhost:3000/stock/005930")
      2. screenshot()
    Expected Result: 상세 정보 + 차트 렌더링
    Evidence: .sisyphus/evidence/task-11-detail.png
  ```

  **Commit**: YES
  - Message: `feat: implement stock detail page`
  - Files: `frontend/app/stock/[ticker]/page.tsx`

---

- [ ] 12. Toss UI 스타일 적용 (색상, 타이포그래피)

  **What to do**:
  - Global CSS에 Toss 색상 적용
  - Pretendard 폰트 전체 적용
  - 카드/테이블 스타일统一
  - 다크 모드基礎

  **Must NOT**:
  - 과도한 커스터마이징

  **Recommended Agent Profile**:
  - **Category**: `visual-engineering`
  - **Skills**: [`frontend-ui-ux`]

  **Parallelization**:
  - **Can Run In Parallel**: NO
  - **Parallel Group**: Wave 3
  - **Blocks**: None
  - **Blocked By**: Task 8

  **References**:
  - Toss TDS: Primary #0045F6, 상승 #E5493A, 하락 #2972FF
  - Spacing: 4px baseline

  **Acceptance Criteria**:
  - [ ] 전체 페이지에 Toss 색상 적용
  - [ ] Pretendard 폰트 렌더링
  - [ ] 상승/하락 색상 표시

  **QA Scenarios**:
  ```
  Scenario: Toss 스타일 확인
    Tool: Playwright
    Preconditions: frontend 실행 중
    Steps:
      1. goto("http://localhost:3000")
      2. screenshot()
    Expected Result: Toss 스타일 적용 확인
    Evidence: .sisyphus/evidence/task-12-style.png
  ```

  **Commit**: YES
  - Message: `style: apply Toss UI design system`
  - Files: `frontend/app/globals.css`

---

- [ ] 13. 에러 처리 (Error Boundary, Empty State)

  **What to do**:
  - React Error Boundary
  - API 에러 시 Fallback UI
  - 검색 결과 없을 때 Empty State
  - PER/PBR N/A 처리

  **Must NOT**:
  - 복잡한 에러 복구 로직

  **Recommended Agent Profile**:
  - **Category**: `quick`
  - **Skills**: []

  **Parallelization**:
  - **Can Run In Parallel**: NO
  - **Parallel Group**: Wave 3
  - **Blocks**: None
  - **Blocked By**: Task 11

  **References**:
  - Shadcn/ui: ErrorBoundary 패턴

  **Acceptance Criteria**:
  - [ ] API 실패 시 에러 메시지 표시
  - [ ] 검색 결과 없을 때 Empty State
  - [ ] PER/PBR 마이너스 시 N/A 표시

  **QA Scenarios**:
  ```
  Scenario: Empty State
    Tool: Playwright
    Preconditions: frontend 실행 중
    Steps:
      1. goto("http://localhost:3000/search?q=xyz123nonexistent")
      2. screenshot()
    Expected Result: "검색 결과가 없습니다" 메시지
    Evidence: .sisyphus/evidence/task-13-empty.png
  ```

  **Commit**: YES
  - Message: `fix: add error boundary and empty states`
  - Files: `frontend/components/`

---

- [ ] 14. 배치 작업 (scheduler or cron)

  **What to do**:
  - 일일 데이터 수집 스크립트 scheduler 설정
  - CSV/JSON 저장
  - 실행 로그 기록

  **Must NOT**:
  - 실시간 자동화 (MVP에서는 수동 실행)

  **Recommended Agent Profile**:
  - **Category**: `quick`
  - **Skills**: []

  **Parallelization**:
  - **Can Run In Parallel**: NO
  - **Parallel Group**: Wave 3
  - **Blocks**: None
  - **Blocked By**: Task 4

  **References**:
  - Python: schedule 라이브러리 또는 cron

  **Acceptance Criteria**:
  - [ ] batch/collect_data.py 실행 시 CSV 저장
  - [ ] logs/ 디렉토리에 실행 로그

  **QA Scenarios**:
  ```
  Scenario: Batch 실행
    Tool: Bash
    Preconditions: backend 디렉토리
    Steps:
      1. python batch/collect_data.py
      2. ls -la data/stocks_*.csv
    Expected Result: CSV 파일 생성 (날짜별)
    Evidence: .sisyphus/evidence/task-14-batch.txt
  ```

  **Commit**: YES
  - Message: `feat: add daily batch job script`
  - Files: `backend/batch/`

---

- [ ] 15. Disclaimer 고지문 추가

  **What to do**:
  - Footer에 금융 고지문 추가
  - "본 서비스는 투자 조언이 아닙니다"
  - 데이터 소스 출처 명시

  **Must NOT**:
  - 복잡한 Legal 텍스트

  **Recommended Agent Profile**:
  - **Category**: `quick`
  - **Skills**: []

  **Parallelization**:
  - **Can Run In Parallel**: NO
  - **Parallel Group**: Wave 3
  - **Blocks**: None
  - **Blocked By**: Task 8

  **References**:
  - Toss: 투자 고지 similar 패턴

  **Acceptance Criteria**:
  - [ ] 모든 페이지 Footer에 고지문 표시
  - [ ] "데이터: pykrx" 출처 명시

  **QA Scenarios**:
  ```
  Scenario: Disclaimer 확인
    Tool: Playwright
    Preconditions: frontend 실행 중
    Steps:
      1. goto("http://localhost:3000")
      2. scroll("bottom")
      3. screenshot()
    Expected Result: Footer 고지문 확인
    Evidence: .sisyphus/evidence/task-15-footer.png
  ```

  **Commit**: YES
  - Message: `docs: add financial disclaimer`
  - Files: `frontend/components/Footer.tsx`

---

## Final Verification Wave

- [ ] F1. **End-to-End QA** — Playwright
  - 모든 페이지 접근 확인
  - 검색, 필터, 정렬 기능 검증
  - 에러 상황 테스트

- [ ] F2. **Batch Job Verification**
  - 데이터 수집 스크립트 실행
  - CSV/JSON 저장 확인
  - 데이터 무결성 검증

- [ ] F3. **Plan Compliance Audit**
  - MVP 범위 준수 확인
  - Guardrails 적용 확인
  - Must Have/Must NOT 확인

---

## Commit Strategy

| Wave | Message | Files |
|------|---------|-------|
| 1 | `chore: initialize project structure` | frontend/, backend/ |
| 1 | `feat: add FastAPI scaffolding` | backend/main.py |
| 1 | `feat: setup Tailwind and Shadcn/ui` | frontend/ |
| 1 | `feat: add pykrx data collection` | backend/batch/ |
| 1 | `types: define schemas` | frontend/types/, backend/app/schemas/ |
| 2 | `feat: implement recommendation algorithm` | backend/app/services/ |
| 2 | `feat: implement REST API` | backend/app/routers/ |
| 2 | `feat: implement dashboard page` | frontend/app/page.tsx |
| 2 | `feat: implement stock list` | frontend/app/stocks/ |
| 2 | `feat: implement search` | frontend/components/ |
| 3 | `feat: implement detail page` | frontend/app/stock/ |
| 3 | `style: apply Toss UI` | frontend/app/globals.css |
| 3 | `fix: add error handling` | frontend/components/ |
| 3 | `feat: add batch job` | backend/batch/ |
| 3 | `docs: add disclaimer` | frontend/components/ |

---

## Success Criteria

### Verification Commands
```bash
# Frontend
cd frontend && npm run dev

# Backend
cd backend && uvicorn main:app --reload

# Batch
cd backend && python batch/collect_data.py

# Tests
cd frontend && npx vitest
cd backend && pytest
```

### Final Checklist
- [ ] 모든 Must Have 기능 구현
- [ ] 모든 Must NOT 항목 미포함
- [ ] pytest 테스트 통과
- [ ] vitest 테스트 통과
- [ ] Disclaimer 표시
- [ ] Toss UI 스타일 적용
