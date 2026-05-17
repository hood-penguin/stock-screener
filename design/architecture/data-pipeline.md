# 데이터 파이프라인 설계

## 데이터 수집 흐름

```
┌──────────────────────────────────────────────────────────┐
│                    수집 스케줄                             │
│                                                          │
│   KR 장 마감 (15:30 KST)     US 장 마감 (16:00 ET)       │
│         │                           │                    │
│         ▼ 06:40 UTC                 ▼ 21:30 UTC          │
│   ┌──────────────┐           ┌──────────────┐            │
│   │ fetch_kr_    │           │ fetch_us_    │            │
│   │ market()     │           │ market()     │            │
│   └──────┬───────┘           └──────┬───────┘            │
└──────────┼───────────────────────────┼───────────────────┘
           │                           │
           ▼                           ▼
┌──────────────────────────────────────────────────────────┐
│                   데이터 수집 레이어                        │
│                                                          │
│  ┌─────────────────────────┐  ┌─────────────────────┐   │
│  │ KR 수집기                │  │ US 수집기            │   │
│  │                         │  │                     │   │
│  │ 1. 한투 OpenAPI          │  │ 1. Polygon.io       │   │
│  │    - 주가/거래량          │  │    - 주가/재무       │   │
│  │    - 재무제표             │  │    - 섹터 정보       │   │
│  │                         │  │                     │   │
│  │ 2. DART 전자공시          │  │ 2. Yahoo Finance   │   │
│  │    - 분기/연간 재무       │  │    (보조 소스)       │   │
│  │    - 기업 기본 정보       │  │                     │   │
│  │                         │  │ 3. SEC EDGAR        │   │
│  │ 3. KRX 데이터             │  │    - 10-K/10-Q      │   │
│  │    - 섹터 분류            │  │                     │   │
│  └──────────┬──────────────┘  └──────────┬──────────┘   │
└─────────────┼──────────────────────────────┼────────────┘
              │                              │
              ▼                              ▼
┌──────────────────────────────────────────────────────────┐
│                    정규화 레이어                            │
│                                                          │
│   KR 원시 데이터          US 원시 데이터                    │
│        │                       │                         │
│        ▼                       ▼                         │
│   ┌─────────────────────────────────────────┐            │
│   │           Normalizer                    │            │
│   │                                         │            │
│   │  - 통화 통일 (KRW→USD 또는 현지 통화 유지)│            │
│   │  - 필드명 표준화 (pe_ratio, pb_ratio...)  │            │
│   │  - 날짜 형식 통일 (UTC ISO 8601)          │            │
│   │  - 결측값 처리 전략                       │            │
│   └────────────────────┬────────────────────┘            │
└────────────────────────┼─────────────────────────────────┘
                         │
                         ▼
┌──────────────────────────────────────────────────────────┐
│                     PostgreSQL                            │
│                                                          │
│  raw_financials (원시 보존)   stocks (종목 마스터)          │
│  financial_metrics (계산값)   sector_benchmarks (섹터 집계)│
└──────────────────────────────────────────────────────────┘
                         │
                         ▼ (데이터 수집 완료 후 트리거)
┌──────────────────────────────────────────────────────────┐
│                  스크리닝 엔진 실행                         │
│  (별도 문서: screening-engine.md 참고)                     │
└──────────────────────────────────────────────────────────┘
```

## 데이터 소스별 세부 사항

### 미국 시장 (US)

| 소스 | 제공 데이터 | 업데이트 주기 | 비용 |
|---|---|---|---|
| **Polygon.io** | 주가, 재무제표, 종목 정보 | 실시간/일별 | 유료 (월 $29~) |
| **Yahoo Finance (yfinance)** | 주가, 기본 재무, 섹터 | 일별 | 무료 (비공식) |
| **SEC EDGAR** | 10-K/10-Q 원문 재무제표 | 분기별 | 무료 |
| **FRED** | 무위험이자율 (DCF 할인율용) | 주간 | 무료 |

### 한국 시장 (KR)

| 소스 | 제공 데이터 | 업데이트 주기 | 비용 |
|---|---|---|---|
| **한국투자증권 OpenAPI** | 주가, 호가, 종목 기본 | 실시간/일별 | 무료 (계좌 필요) |
| **DART 전자공시 API** | 사업보고서, 분기보고서 | 공시 즉시 | 무료 |
| **KRX (정보데이터시스템)** | 섹터 분류, 지수 | 일별 | 무료 |
| **금융감독원 XBRL** | 표준 재무제표 데이터 | 분기별 | 무료 |

## 데이터 어댑터 인터페이스

```python
# data/providers/base.py

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import AsyncIterator

@dataclass
class RawStockData:
    ticker: str
    market: str                 # "US" | "KR"
    company_name: str
    sector: str | None
    exchange: str               # "NYSE", "NASDAQ", "KOSPI", "KOSDAQ"
    currency: str               # "USD", "KRW"
    # 가격 데이터
    price: float
    market_cap: float | None
    # 재무 데이터 (없으면 None)
    pe_ratio: float | None
    pb_ratio: float | None
    ev_ebitda: float | None
    roe: float | None
    roa: float | None
    debt_to_equity: float | None
    current_ratio: float | None
    gross_margin: float | None
    operating_margin: float | None
    revenue_growth_yoy: float | None
    eps_growth_yoy: float | None
    # 메타
    fiscal_year_end: str | None
    data_as_of: str             # ISO 8601

class BaseDataProvider(ABC):
    @abstractmethod
    async def fetch_all_stocks(self) -> AsyncIterator[RawStockData]:
        """해당 시장의 모든 종목 데이터를 스트리밍으로 반환"""
        ...

    @abstractmethod
    async def fetch_stock(self, ticker: str) -> RawStockData | None:
        """특정 종목 데이터 조회"""
        ...

    @abstractmethod
    async def fetch_sector_benchmarks(self) -> dict[str, dict]:
        """섹터별 평균 지표 반환 {'Technology': {'avg_pe': 25.3, ...}}"""
        ...
```

## 결측값 처리 전략

```
재무 데이터 결측 시 처리 우선순위:

1. 동일 종목 최신 연간 데이터 사용 (분기 데이터 없으면)
2. TTM(Trailing 12 Month) 계산
3. 섹터 중앙값으로 대체 (점수 계산 제외, 표시만)
4. 데이터 없음으로 표시 (해당 기준 평가 Skip)
```

## 데이터 신선도 관리

```python
# 데이터 유효성 검사 규칙
FRESHNESS_RULES = {
    "price": timedelta(hours=24),          # 주가: 1일 이내
    "financial_statements": timedelta(days=120),  # 재무제표: 4개월 이내
    "sector_benchmarks": timedelta(days=7),       # 섹터 평균: 1주일 이내
}
```

## 오류 처리 및 재시도

```python
# tasks/data_fetch.py (Celery)

@celery_app.task(
    bind=True,
    max_retries=3,
    default_retry_delay=300,  # 5분 후 재시도
    autoretry_for=(NetworkError, RateLimitError),
)
async def fetch_us_market(self):
    try:
        async for stock_data in polygon_provider.fetch_all_stocks():
            await normalizer.process_and_save(stock_data)
    except DataProviderError as e:
        # 주요 소스 실패 시 Yahoo Finance 폴백
        logger.warning(f"Polygon failed, falling back to Yahoo: {e}")
        async for stock_data in yahoo_provider.fetch_all_stocks():
            await normalizer.process_and_save(stock_data)
```
