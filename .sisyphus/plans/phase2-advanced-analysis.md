# Phase 2: 고급 재무지표 및 기술적 분석 구현 계획

> **목표**: "싸고 튼튼한 기업"을 찾는 가치투자 중심의 고급 스크리닝 + 매수 타이밍 분석  
> **기간**: 2-3주 (Wave 방식)  
> **핵심 가치**: 저평가(싸고) + 고수익성(튼튼) + 적정 타이밍

---

## 📊 현재 상태 분석 (Phase 1 기반)

### 데이터 스키마 (현재)
| 필드 | 상태 | 비고 |
|------|------|------|
| ticker, name | ✅ | 정상 수집 |
| open, high, low, close, volume | ✅ | OHLCV 일일 데이터 |
| per, pbr, eps, bps, market_cap | ⚠️ | 많은 종목이 null |
| ROE | ❌ | 미수집 |
| 3개월 수익률 | ❌ | 미수집 (mock 사용) |
| EPS 성장률 | ❌ | 미계산 |
| 부채비율 | ❌ | 미수집 |

### 추천 알고리즘 (현재)
```
가치(40%) - PER/PBR 기반 ✅ 작동
성장(25%) - EPS만 사용 ⚠️ 부분 작동  
수익성(20%) - ROE 미수집 ❌ 미작동
모멘텀(15%) - 3개월 미수집 ❌ 미작동
```

### 차트 (현재)
- lightweight-charts 사용 ✅
- **Mock 데이터 사용** ❌ 실제 데이터 필요
- 거래량 미표시
- 기술적 지표 없음

---

## 🌊 Wave 1: 고급 재무지표 (1주)

### 1.1 데이터 수집 개선

#### 신규 지표 수집
```python
# backend/batch/collect_data.py 확장

# 1. ROE (자기자본이익률)
# 데이터 소스: pykrx 또는 FSS OpenAPI
# 공식: 당기순이익 / 자기자본 * 100
# target: 15% 이상이 양호

# 2. 부채비율 (Debt Ratio)
# 데이터 소스: pykrx 재무제표 또는 FSS OpenAPI
# 공식: 총부채 / 자기자본 * 100
# target: 200% 이하 권장

# 3. Forward P/E
# 공식: 현재 주가 / (EPS * (1 + 성장률))
# 또는 컨센서스 EPS 활용 (데이터 소스 확인 필요)

# 4. EPS YoY 성장률
# 공식: (현재 EPS - 작년 EPS) / 작년 EPS * 100
# 데이터: pykrx에서 최소 2년치 EPS 필요

# 5. 업종/섹터 정보
# 데이터 소스: pykrx 또는 KRX 산업분류
```

#### 데이터 품질 개선
```python
# backend/app/services/data_loader.py 개선

# 1. null 값 처리
- PER/PBR이 null인 종목 필터링 옵션
- 대체 값 계산 (예: 업종 평균)

# 2. 이상치 탐지
- PER < 0 (적자기업) 처리
- PER > 100 (고PER) 플래그
- ROE > 100% 또는 < -100% 검증

# 3. 데이터 검증
- 최소 필수 필드 체크
- 데이터 신선도 확인 (최대 1일)
```

### 1.2 Pydantic 스키마 확장

```python
# backend/app/schemas/stock.py

class StockDetail(BaseModel):
    # 기존 필드
    ticker: str
    name: str
    current_price: float
    change_rate: float
    per: Optional[float] = None
    pbr: Optional[float] = None
    market_cap: Optional[float] = None
    eps: Optional[float] = None
    bps: Optional[float] = None
    
    # 신규 필드 (Wave 1)
    forward_pe: Optional[float] = None  # 선행 PER
    roe: Optional[float] = None  # 자기자본이익률 (%)
    debt_ratio: Optional[float] = None  # 부채비율 (%)
    eps_growth_yoy: Optional[float] = None  # EPS YoY 성장률 (%)
    sector: Optional[str] = None  # 업종
    industry: Optional[str] = None  # 세부산업
```

### 1.3 추천 알고리즘 개선

```python
# backend/app/services/recommendation.py

# 새로운 가중치 구조
def calculate_total_score(stock_data):
    scores = {
        'value': calculate_value_score(per, pbr, forward_pe),  # 35%
        'growth': calculate_growth_score(eps_growth_yoy),  # 25%
        'profitability': calculate_profitability_score(roe),  # 20%
        'momentum': calculate_momentum_score(price_change_3m),  # 15%
        'stability': calculate_stability_score(debt_ratio),  # 5%
    }
    
    # 재무건전성 가중치 (신규)
    # debt_ratio < 100%: +5점
    # 100% <= debt_ratio < 200%: 0점
    # 200% <= debt_ratio < 300%: -5점
    # debt_ratio >= 300%: -10점 (Value Trap 의심)
    
    return weighted_sum(scores)
```

### 1.4 TypeScript 타입 확장

```typescript
// frontend/types/index.ts

export interface StockDetail extends Stock {
  // 기존 필드
  per?: number;
  pbr?: number;
  market_cap?: number;
  eps?: number;
  bps?: number;
  
  // 신규 필드 (Wave 1)
  forward_pe?: number;  // 선행 PER
  roe?: number;  // 자기자본이익률 (%)
  debt_ratio?: number;  // 부채비율 (%)
  eps_growth_yoy?: number;  // EPS YoY (%)
  sector?: string;  // 업종
  industry?: string;  // 세부산업
}
```

---

## 🌊 Wave 2: 기술적 분석 (1주)

### 2.1 OHLCV 히스토리컬 데이터 수집

```python
# backend/batch/collect_history.py (신규)

# pykrx에서 과거 데이터 수집
# stock.get_market_ohlcv_by_date() 활용

# 수집 대상: 최소 120일 (MA 120 계산용)
# 필드: date, open, high, low, close, volume
# 저장: data/history/{ticker}.csv 또는 SQLite
```

### 2.2 기술적 지표 계산

```python
# backend/app/services/technical_analysis.py (신규)

import pandas as pd
import pandas_ta as ta  # 또는 ta-lib

class TechnicalAnalyzer:
    def calculate_ma(self, df: pd.DataFrame) -> dict:
        """이동평균선 계산"""
        return {
            'ma_5': df['close'].rolling(window=5).mean().iloc[-1],
            'ma_20': df['close'].rolling(window=20).mean().iloc[-1],
            'ma_60': df['close'].rolling(window=60).mean().iloc[-1],
            'ma_120': df['close'].rolling(window=120).mean().iloc[-1],
        }
    
    def calculate_rsi(self, df: pd.DataFrame, period: int = 14) -> float:
        """RSI 계산"""
        return ta.rsi(df['close'], length=period).iloc[-1]
    
    def calculate_volume_ma(self, df: pd.DataFrame) -> dict:
        """거래량 이동평균"""
        return {
            'vma_5': df['volume'].rolling(window=5).mean().iloc[-1],
            'vma_20': df['volume'].rolling(window=20).mean().iloc[-1],
        }
    
    def detect_volume_spike(self, df: pd.DataFrame) -> bool:
        """거래량 급등 감지 (VMA 20 대비 200% 이상)"""
        current_volume = df['volume'].iloc[-1]
        vma_20 = df['volume'].rolling(window=20).mean().iloc[-1]
        return current_volume > vma_20 * 2.0
```

### 2.3 API 엔드포인트 추가

```python
# backend/app/routers/stocks.py

@router.get("/stocks/{ticker}/technical")
def get_technical_indicators(ticker: str):
    """
    Get technical indicators for a stock.
    
    Returns:
    - moving_averages: {ma_5, ma_20, ma_60, ma_120}
    - rsi: 14-day RSI
    - volume_analysis: {current, vma_5, vma_20, spike_detected}
    - trend: "uptrend" | "downtrend" | "sideways"
    """
    pass

@router.get("/stocks/{ticker}/chart")
def get_chart_data(ticker: str, period: str = "3m"):
    """
    Get OHLCV data for chart rendering.
    
    period: "1m" | "3m" | "6m" | "1y"
    Returns: List of {date, open, high, low, close, volume}
    """
    pass
```

### 2.4 차트 개선 (Frontend)

```typescript
// frontend/app/stock/[ticker]/page.tsx

// 1. 캔들차트 + 거래량 서브차트
// 2. 이동평균선 오버레이 (MA5, MA20, MA60)
// 3. RSI 패널 추가 (하단에 게이지 또는 라인)
// 4. 거래량 급등 마커

// lightweight-charts 설정
const chartOptions = {
  layout: {
    background: { color: '#ffffff' },
    textColor: '#333',
  },
  grid: {
    vertLines: { color: '#f0f0f0' },
    horzLines: { color: '#f0f0f0' },
  },
  crosshair: {
    mode: CrosshairMode.Normal,
  },
  rightPriceScale: {
    borderColor: '#cccccc',
  },
  timeScale: {
    borderColor: '#cccccc',
  },
};

// 캔들스틱 시리즈
const candlestickSeries = chart.addCandlestickSeries({
  upColor: '#E5493A',
  downColor: '#2972FF',
  borderVisible: false,
  wickUpColor: '#E5493A',
  wickDownColor: '#2972FF',
});

// 이동평균선 시리즈 (오버레이)
const ma5Series = chart.addLineSeries({ color: '#FF6B6B', lineWidth: 1 });
const ma20Series = chart.addLineSeries({ color: '#4ECDC4', lineWidth: 1 });
const ma60Series = chart.addLineSeries({ color: '#45B7D1', lineWidth: 1 });

// 거래량 차트 (하단 서브차트)
const volumeSeries = chart.addHistogramSeries({
  color: '#26a69a',
  priceFormat: { type: 'volume' },
  priceScaleId: '', // 별도 스케일
});
```

---

## 🌊 Wave 3: UI/UX 고도화 (1주)

### 3.1 필터/정렬 확장

```typescript
// frontend/app/stocks/page.tsx

// 신규 필터 옵션
interface FilterState {
  // 기존
  perMin: string;
  perMax: string;
  marketCapMin: string;
  
  // 신규 (Wave 3)
  pbrMin: string;
  pbrMax: string;
  roeMin: string;  // ROE 최소
  debtRatioMax: string;  // 부채비율 최대
  forwardPeMax: string;  // Forward P/E 최대
  sector: string;  // 업종 필터
  rsiRange: 'oversold' | 'neutral' | 'overbought';  // RSI 상태
}

// 신규 정렬 옵션
const sortOptions = [
  { field: 'market_cap', label: '시가총액' },
  { field: 'per', label: 'PER' },
  { field: 'pbr', label: 'PBR' },
  { field: 'change_rate', label: '등락률' },
  // 신규
  { field: 'roe', label: 'ROE' },
  { field: 'forward_pe', label: 'Forward P/E' },
  { field: 'debt_ratio', label: '부채비율' },
  { field: 'recommendation_score', label: '추천점수' },
];
```

### 3.2 상세 페이지 개선

```
┌─────────────────────────────────────────────────────────┐
│  [삼성전자] [72,500원] [▲ 1.2%]  [전자/반도체]          │
├─────────────────────────────────────────────────────────┤
│                                                         │
│  [캔들차트 + MA5/20/60 + 거래량]                        │
│                                                         │
├─────────────────────────────────────────────────────────┤
│  RSI(14)          [====○====] 45.2 (중립)              │
├──────────────────────┬──────────────────────────────────┤
│  펀더멘털            │  투자 지표                        │
├──────────────────────┼──────────────────────────────────┤
│  PER:        8.5배   │  추천점수: 85점 (매수)           │
│  Forward P/E: 7.2배  │  가치: 90점 (저평가)             │
│  PBR:        0.9배   │  수익성: 88점 (ROE 18%)          │
│  ROE:        18.5% ⭐│  재무건전성: 95점                │
│  부채비율:   120%    │  모멘텀: 65점                    │
│  EPS성장:    +25%    │                                  │
├──────────────────────┴──────────────────────────────────┤
│  ⚠️ 투자고지: 본 정보는 참고용이며 투자권유가 아닙니다    │
└─────────────────────────────────────────────────────────┘
```

### 3.3 업종별 분석 페이지 (신규)

```typescript
// frontend/app/sectors/page.tsx (신규)

// 업종별 평균 지표 비교
// - 반도체: 평균 PER 15.2, ROE 12%
// - 은행: 평균 PER 5.8, ROE 8%
// - 자동차: 평균 PER 8.1, ROE 10%

// 업종 내 상대적 순위 표시
// "이 종목은 반도체 업종에서 PER 기준 상위 10%"
```

---

## 📋 데이터 소스 전략

### Tier 1: pykrx (무료, 15분 지연)
- ✅ OHLCV 일일 데이터
- ✅ PER, PBR, EPS, BPS
- ⚠️ ROE (제한적)
- ❌ 부채비율 (재무제표 필요)

### Tier 2: FSS OpenAPI (금융위원회, 무료)
- ✅ 상세 재무제표
- ✅ ROE, 부채비율
- ✅ 업종 정보
- ⚠️ API 신청 및 Rate Limit

### Tier 3: 한국거래소/KRX (상업용)
- ✅ 실시간 데이터
- ❌ 유료

### 권장 전략
```
MVP: pykrx만 사용
Phase 2: pykrx + FSS OpenAPI 병행
Phase 3: 실시간 데이터 고려
```

---

## 🎯 성공 기준 (Definition of Done)

### Wave 1 완료 기준
- [ ] ROE, Forward P/E, 부채비율, EPS 성장률 수집
- [ ] 추천 알고리즘에 재무건전성 가중치 추가
- [ ] 데이터 품질 개선 (null 처리, 이상치 필터링)

### Wave 2 완료 기준
- [ ] 120일 OHLCV 히스토리 데이터 수집
- [ ] MA(5/20/60/120), RSI(14), VMA 계산 API
- [ ] 캔들차트 + 거래량 + 이동평균선 표시
- [ ] RSI 게이지 또는 서브차트 추가

### Wave 3 완료 기준
- [ ] 필터에 ROE, 부채비율, Forward P/E, 업종 추가
- [ ] 정렬에 신규 지표 추가
- [ ] 상세 페이지 재무 테이블 개선
- [ ] 업종별 분석 페이지 (Optional)

---

## 🚨 위험 요소 및 대응

| 위험 | 가능성 | 대응책 |
|------|--------|--------|
| FSS OpenAPI 복잡도 | 중 | pykrx 우선, 필요시 FSS 추가 |
| pykrx 데이터 한계 | 중 | 업종/섹터는 수동 매핑 또는 대체 데이터 |
| 계산 성능 | 낮 | 캐싱 전략 (Redis 또는 파일 캐시) |
| UI 복잡도 | 중 | Progressive Disclosure (단계적 공개) |

---

## 📅 예상 일정

| 주차 | Wave | 주요 작업 | 산출물 |
|------|------|-----------|--------|
| 1주차 | Wave 1 | 데이터 수집 개선, ROE/부채비율 | collect_data.py 확장, DB 스키마 변경 |
| 2주차 | Wave 2 | 기술적 분석, 차트 개선 | technical_analysis.py, 차트 컴포넌트 |
| 3주차 | Wave 3 | UI/UX 고도화, 필터 확장 | stocks/page.tsx 개선, 상세 페이지 개선 |

---

## 📝 결론

이 계획은 "싸고 튼튼한 기업"을 찾는 가치투자 철학을 구현합니다:

1. **저평가 확인**: PER, PBR, Forward P/E
2. **수익성 검증**: ROE
3. **재무건전성**: 부채비율
4. **적정 타이밍**: RSI, 이동평균선, 거래량

MVP에서 실제로 작동하던 것은 "가치(40%)"뿐이었지만,  
Phase 2 완료 후에는 모든 가중치가 실제 데이터 기반으로 작동하게 됩니다.
