# 백엔드 설계

## 프로젝트 구조

```
backend/
├── app/
│   ├── main.py                    # FastAPI 앱 진입점
│   ├── config.py                  # 환경 설정
│   ├── dependencies.py            # DI 컨테이너
│   │
│   ├── api/                       # API 라우터
│   │   ├── v1/
│   │   │   ├── stocks.py          # 종목 조회
│   │   │   ├── screener.py        # 스크리닝 결과
│   │   │   ├── watchlist.py       # 관심 종목
│   │   │   └── auth.py            # 인증
│   │   └── deps.py                # API 공통 의존성
│   │
│   ├── core/
│   │   ├── screening/             # 스크리닝 엔진 (핵심)
│   │   │   ├── engine.py          # 엔진 오케스트레이터
│   │   │   ├── registry.py        # 기준 플러그인 레지스트리
│   │   │   ├── scorer.py          # 종합 점수 계산기
│   │   │   └── criteria/          # 스크리닝 기준 플러그인들
│   │   │       ├── base.py        # 기준 인터페이스 (ABC)
│   │   │       ├── valuation/
│   │   │       │   ├── pe_ratio.py
│   │   │       │   ├── pb_ratio.py
│   │   │       │   ├── ev_ebitda.py
│   │   │       │   └── peg_ratio.py
│   │   │       ├── profitability/
│   │   │       │   ├── roe.py
│   │   │       │   ├── roa.py
│   │   │       │   └── gross_margin.py
│   │   │       ├── growth/
│   │   │       │   ├── revenue_growth.py
│   │   │       │   └── eps_growth.py
│   │   │       └── financial_health/
│   │   │           ├── debt_ratio.py
│   │   │           └── current_ratio.py
│   │   │
│   │   └── market/                # 시장 어댑터
│   │       ├── base.py            # MarketAdapter 인터페이스
│   │       ├── us_market.py       # 미국 시장
│   │       └── kr_market.py       # 한국 시장
│   │
│   ├── data/                      # 데이터 수집 레이어
│   │   ├── providers/
│   │   │   ├── base.py            # DataProvider 인터페이스
│   │   │   ├── polygon.py         # Polygon.io (US)
│   │   │   ├── yahoo_finance.py   # Yahoo Finance (US 보조)
│   │   │   ├── kis_api.py         # 한국투자증권 (KR)
│   │   │   └── dart.py            # DART 전자공시 (KR)
│   │   └── normalizer.py          # 시장별 데이터 정규화
│   │
│   ├── models/                    # SQLAlchemy ORM 모델
│   │   ├── stock.py
│   │   ├── financial.py
│   │   ├── screening_result.py
│   │   └── user.py
│   │
│   ├── schemas/                   # Pydantic 스키마
│   │   ├── stock.py
│   │   ├── screening.py
│   │   └── user.py
│   │
│   └── tasks/                     # Celery 태스크
│       ├── data_fetch.py          # 데이터 수집 태스크
│       ├── screening_run.py       # 스크리닝 실행 태스크
│       └── schedules.py           # Celery Beat 스케줄
│
├── tests/
├── alembic/                       # DB 마이그레이션
├── pyproject.toml
└── Dockerfile
```

## 스크리닝 기준 플러그인 인터페이스

```python
# core/screening/criteria/base.py

from abc import ABC, abstractmethod
from dataclasses import dataclass
from enum import Enum
from typing import Optional

class CriteriaCategory(Enum):
    VALUATION = "valuation"
    PROFITABILITY = "profitability"
    GROWTH = "growth"
    FINANCIAL_HEALTH = "financial_health"
    MOMENTUM = "momentum"  # 나중에 추가 가능

@dataclass
class CriteriaResult:
    criteria_id: str
    score: float          # 0.0 ~ 1.0 (1.0이 최고 저평가)
    raw_value: float      # 실제 지표 값 (예: PER = 8.5)
    benchmark: float      # 비교 기준 값 (예: 섹터 평균 PER)
    is_undervalued: bool
    reason: str           # 사람이 읽을 수 있는 설명

class BaseCriteria(ABC):
    """모든 스크리닝 기준이 구현해야 하는 인터페이스"""

    @property
    @abstractmethod
    def criteria_id(self) -> str:
        """유일한 기준 식별자 (예: 'pe_ratio_vs_sector')"""
        ...

    @property
    @abstractmethod
    def name(self) -> str:
        """사람이 읽을 수 있는 이름"""
        ...

    @property
    @abstractmethod
    def category(self) -> CriteriaCategory:
        ...

    @property
    def weight(self) -> float:
        """종합 점수에서 이 기준의 가중치 (기본 1.0)"""
        return 1.0

    @property
    def required_fields(self) -> list[str]:
        """평가에 필요한 재무 데이터 필드명 목록"""
        return []

    @abstractmethod
    def evaluate(
        self,
        stock_data: dict,
        sector_benchmarks: Optional[dict] = None,
    ) -> Optional[CriteriaResult]:
        """
        Returns None if required data is unavailable.
        """
        ...
```

## 스크리닝 기준 구현 예시 (PER)

```python
# core/screening/criteria/valuation/pe_ratio.py

from ..base import BaseCriteria, CriteriaCategory, CriteriaResult
from typing import Optional
import math

class PERatioCriteria(BaseCriteria):
    criteria_id = "pe_ratio_vs_sector"
    name = "PER (섹터 대비)"
    category = CriteriaCategory.VALUATION
    weight = 1.5          # 밸류에이션 핵심 지표로 가중치 높임
    required_fields = ["pe_ratio", "sector"]

    def evaluate(self, stock_data: dict, sector_benchmarks: Optional[dict] = None) -> Optional[CriteriaResult]:
        pe = stock_data.get("pe_ratio")
        sector = stock_data.get("sector")

        if pe is None or pe <= 0:
            return None

        # 섹터 평균 PER (없으면 시장 전체 평균 사용)
        sector_avg_pe = (
            sector_benchmarks.get(sector, {}).get("avg_pe")
            if sector_benchmarks
            else None
        ) or 20.0  # 기본 시장 평균

        ratio = pe / sector_avg_pe
        # ratio < 1이면 섹터 평균보다 저평가
        score = max(0.0, min(1.0, 1.0 - (ratio - 0.3) / 1.4))

        return CriteriaResult(
            criteria_id=self.criteria_id,
            score=score,
            raw_value=pe,
            benchmark=sector_avg_pe,
            is_undervalued=(ratio < 0.8),
            reason=f"PER {pe:.1f} = 섹터 평균({sector_avg_pe:.1f})의 {ratio*100:.0f}%",
        )
```

## 스크리닝 엔진 오케스트레이터

```python
# core/screening/engine.py

class ScreeningEngine:
    def __init__(self, registry: CriteriaRegistry):
        self.registry = registry

    def run(
        self,
        stocks: list[dict],
        enabled_criteria: list[str] | None = None,   # None = 전체 활성화
        market: str = "US",
        sector_benchmarks: dict | None = None,
    ) -> list[ScreeningResult]:
        criteria_list = self.registry.get_enabled(enabled_criteria)
        results = []

        for stock in stocks:
            criteria_scores = []
            for criteria in criteria_list:
                result = criteria.evaluate(stock, sector_benchmarks)
                if result:
                    criteria_scores.append((criteria, result))

            if criteria_scores:
                total_score = self._composite_score(criteria_scores)
                results.append(ScreeningResult(
                    ticker=stock["ticker"],
                    market=market,
                    total_score=total_score,
                    criteria_details=criteria_scores,
                    screened_at=datetime.utcnow(),
                ))

        return sorted(results, key=lambda r: r.total_score, reverse=True)

    def _composite_score(self, scored: list) -> float:
        total_weight = sum(c.weight for c, _ in scored)
        weighted_sum = sum(c.weight * r.score for c, r in scored)
        return weighted_sum / total_weight if total_weight else 0.0
```

## 플러그인 레지스트리 (자동 등록)

```python
# core/screening/registry.py
# criteria/ 디렉터리를 스캔해 BaseCriteria 구현체를 자동 등록
# → 파일만 추가하면 자동으로 스크리닝에 포함됨

class CriteriaRegistry:
    def __init__(self):
        self._criteria: dict[str, BaseCriteria] = {}
        self._auto_discover()

    def _auto_discover(self):
        """criteria/ 하위 패키지를 재귀 탐색해 BaseCriteria 구현체 자동 등록"""
        import pkgutil, importlib, inspect
        from . import criteria as pkg

        for _, module_name, _ in pkgutil.walk_packages(
            path=pkg.__path__, prefix=pkg.__name__ + "."
        ):
            module = importlib.import_module(module_name)
            for _, cls in inspect.getmembers(module, inspect.isclass):
                if issubclass(cls, BaseCriteria) and cls is not BaseCriteria:
                    instance = cls()
                    self._criteria[instance.criteria_id] = instance
```

## Celery 스케줄

```python
# tasks/schedules.py

CELERYBEAT_SCHEDULE = {
    # KR 장 마감 후 (15:40 KST = 06:40 UTC)
    "kr-data-fetch": {
        "task": "tasks.data_fetch.fetch_kr_market",
        "schedule": crontab(hour=6, minute=40),
    },
    # US 장 마감 후 (16:30 ET = 21:30 UTC)
    "us-data-fetch": {
        "task": "tasks.data_fetch.fetch_us_market",
        "schedule": crontab(hour=21, minute=30),
    },
    # 데이터 수집 완료 후 스크리닝 실행 (KR: 07:00, US: 22:00 UTC)
    "kr-screening": {
        "task": "tasks.screening_run.run_screening",
        "schedule": crontab(hour=7, minute=0),
        "kwargs": {"market": "KR"},
    },
    "us-screening": {
        "task": "tasks.screening_run.run_screening",
        "schedule": crontab(hour=22, minute=0),
        "kwargs": {"market": "US"},
    },
}
```
