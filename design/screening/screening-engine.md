# 스크리닝 엔진 설계

## 핵심 설계 원칙

**새 기준 추가 = 파일 하나 추가** (코드 변경 없음)

## 현재 지원 기준 목록

### 밸류에이션 (Valuation)

| 기준 ID | 이름 | 설명 | 가중치 |
|---|---|---|---|
| `pe_ratio_vs_sector` | PER vs 섹터 평균 | 주가수익비율이 섹터 평균 대비 낮을수록 점수 높음 | 1.5 |
| `pb_ratio_vs_sector` | PBR vs 섹터 평균 | 주가순자산비율이 섹터 평균 대비 낮을수록 | 1.2 |
| `ev_ebitda_vs_sector` | EV/EBITDA vs 섹터 평균 | 기업가치/EBITDA 비율 | 1.3 |
| `peg_ratio` | PEG 비율 | PER ÷ EPS성장률 (1 미만이면 저평가) | 1.2 |
| `price_to_fcf` | 주가/잉여현금흐름 | 현금창출 대비 주가 | 1.1 |

### 수익성 (Profitability)

| 기준 ID | 이름 | 설명 | 가중치 |
|---|---|---|---|
| `roe_vs_sector` | ROE vs 섹터 평균 | 자기자본이익률 | 1.2 |
| `roa_vs_sector` | ROA vs 섹터 평균 | 총자산이익률 | 1.0 |
| `gross_margin` | 매출총이익률 | 매출 대비 이익률 | 0.8 |
| `operating_margin` | 영업이익률 | 영업 효율성 | 1.0 |

### 성장성 (Growth)

| 기준 ID | 이름 | 설명 | 가중치 |
|---|---|---|---|
| `revenue_growth_yoy` | 매출 성장률 (YoY) | 전년 대비 매출 성장 | 1.0 |
| `eps_growth_yoy` | EPS 성장률 (YoY) | 주당순이익 성장 | 1.1 |

### 재무건전성 (Financial Health)

| 기준 ID | 이름 | 설명 | 가중치 |
|---|---|---|---|
| `debt_ratio` | 부채비율 | 낮을수록 좋음 | 1.0 |
| `current_ratio` | 유동비율 | 1.5 이상이면 양호 | 0.9 |
| `interest_coverage` | 이자보상배율 | 영업이익/이자비용 | 0.9 |

## 새 기준 추가 방법 (Step-by-Step)

### 1단계: 파일 생성

```python
# backend/app/core/screening/criteria/momentum/rsi_criterion.py

from ..base import BaseCriteria, CriteriaCategory, CriteriaResult
from typing import Optional

class RSICriteria(BaseCriteria):
    """RSI 30 이하 (과매도 구간) 종목 탐색"""

    @property
    def criteria_id(self) -> str:
        return "rsi_oversold"

    @property
    def name(self) -> str:
        return "RSI 과매도"

    @property
    def category(self) -> CriteriaCategory:
        return CriteriaCategory.MOMENTUM

    @property
    def weight(self) -> float:
        return 0.8  # 기술적 지표는 낮은 가중치

    @property
    def required_fields(self) -> list[str]:
        return ["rsi_14"]

    def evaluate(
        self,
        stock_data: dict,
        sector_benchmarks: Optional[dict] = None,
    ) -> Optional[CriteriaResult]:
        rsi = stock_data.get("rsi_14")
        if rsi is None:
            return None

        # RSI 30 이하: 과매도, 30~50: 중립, 50 이상: 과매수
        if rsi <= 30:
            score = (30 - rsi) / 30  # 0에 가까울수록 1.0
        elif rsi <= 50:
            score = (50 - rsi) / 20 * 0.5
        else:
            score = 0.0

        return CriteriaResult(
            criteria_id=self.criteria_id,
            score=score,
            raw_value=rsi,
            benchmark=30.0,
            is_undervalued=(rsi <= 30),
            reason=f"RSI {rsi:.1f} → {'과매도 구간' if rsi <= 30 else '일반 구간'}",
        )
```

### 2단계: 완료

파일을 `criteria/momentum/` 디렉터리에 저장하면 **자동으로 등록**됩니다.
레지스트리가 서버 시작 시 `criteria/` 하위를 재귀 탐색하여 자동 로드합니다.

## 종합 점수 계산 로직

```
최종 저평가 점수 = Σ(기준_점수 × 가중치) / Σ(가중치)

각 기준 점수: 0.0 ~ 1.0
최종 점수 표시: 0 ~ 100점 (×100)
```

### 예시

```
AAPL 스크리닝 결과:
  PER vs 섹터     점수 0.85 × 가중치 1.5 = 1.275
  PBR vs 섹터     점수 0.62 × 가중치 1.2 = 0.744
  EV/EBITDA      점수 0.80 × 가중치 1.3 = 1.040
  ROE vs 섹터     점수 0.92 × 가중치 1.2 = 1.104
  영업이익률       점수 0.80 × 가중치 1.0 = 0.800
  부채비율        점수 0.72 × 가중치 1.0 = 0.720

  합계: 5.683 / 7.2 = 0.789 → 79점
```

## 사용자 맞춤 설정

사용자는 다음을 커스터마이징 가능:

```json
{
  "preset_name": "가치투자 중심",
  "enabled_criteria": [
    "pe_ratio_vs_sector",
    "pb_ratio_vs_sector",
    "ev_ebitda_vs_sector",
    "roe_vs_sector",
    "debt_ratio"
  ],
  "weight_overrides": {
    "pe_ratio_vs_sector": 2.0,
    "roe_vs_sector": 1.5
  },
  "min_score_threshold": 60
}
```

## 섹터 벤치마크 계산

```
섹터 평균 = 해당 섹터 전체 종목의 중앙값 (평균 아닌 중앙값 사용)
이유: 극단적인 아웃라이어(적자 기업 등)의 영향 최소화
```

## 스크리닝 결과 캐싱 전략

```
스크리닝 실행 → DB 저장 → Redis 캐시 (TTL 1시간)
                              ↓
              API 요청 시 캐시 먼저 확인
              캐시 미스 시 DB 조회 후 캐시 갱신
```
