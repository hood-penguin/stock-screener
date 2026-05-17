# Stock Screener — 개발 가이드

## 프로젝트 개요

Stock Screener는 미국과 한국 주식 시장의 저평가 종목을 자동으로 탐색하는 풀스택 서비스입니다. 머신러닝 없이 재무 지표 기반 스크리닝 알고리즘으로 투자 기회를 찾아냅니다.

## 기술 스택

- **백엔드**: FastAPI + Celery + PostgreSQL + Redis
- **프론트엔드**: Next.js 15 (TypeScript, Tailwind CSS, React Query)
- **인프라**: Docker Compose
- **데이터**: yfinance (Yahoo Finance), Mock 데이터

## 빠른 시작

### 1. 저장소 클론 및 환경 설정

```bash
cd /root/project/stock-screener

# 환경변수 생성
cp .env.example .env

# .env 파일에서 SECRET_KEY 변경
# SECRET_KEY=your-random-32-character-string-here
```

### 2. Docker Compose로 서비스 시작

```bash
docker compose up -d

# 데이터베이스 마이그레이션
docker compose exec backend alembic upgrade head
```

### 3. 초기 데이터 수집 (선택사항)

```bash
# US 시장 데이터 수집
docker compose exec backend celery -A app.tasks.celery_app call app.tasks.data_fetch.fetch_us_market

# KR 시장 데이터 수집 (Mock 데이터)
docker compose exec backend celery -A app.tasks.celery_app call app.tasks.data_fetch.fetch_kr_market
```

## 개발 환경 접근

- **백엔드 API**: http://localhost:8000
- **API 문서 (Swagger)**: http://localhost:8000/docs
- **프론트엔드**: http://localhost:3000

## 프로젝트 구조

```
stock-screener/
├── backend/
│   ├── app/
│   │   ├── api/v1/                 # API 엔드포인트
│   │   │   ├── auth.py             # 인증 (회원가입, 로그인)
│   │   │   ├── stocks.py           # 주식 API
│   │   │   └── screening.py        # 스크리닝 결과 API
│   │   ├── core/
│   │   │   ├── security.py         # JWT, bcrypt
│   │   │   └── screening/          # 스크리닝 엔진
│   │   │       ├── criteria/       # 12개 평가 기준 (플러그인식)
│   │   │       ├── engine.py       # 스크리닝 엔진
│   │   │       └── registry.py     # 기준 자동 탐색
│   │   ├── data/
│   │   │   └── providers/          # 데이터 소스 어댑터
│   │   │       ├── base.py         # 기본 클래스
│   │   │       └── yahoo_finance.py # Yahoo Finance 프로바이더
│   │   ├── models/                 # SQLAlchemy 모델
│   │   ├── schemas/                # Pydantic 스키마
│   │   ├── tasks/                  # Celery 태스크
│   │   │   ├── celery_app.py
│   │   │   ├── data_fetch.py       # 데이터 수집
│   │   │   ├── screening_run.py    # 스크리닝 실행
│   │   │   └── schedules.py        # Celery Beat 스케줄
│   │   ├── config.py               # 설정 (환경변수)
│   │   ├── database.py             # DB 및 Redis 연결
│   │   └── main.py                 # FastAPI 엔트리포인트
│   └── tests/                      # 테스트
│
├── frontend/
│   └── apps/web/
│       ├── app/
│       │   ├── layout.tsx          # 루트 레이아웃
│       │   ├── page.tsx            # 홈 (스크리너로 리다이렉트)
│       │   ├── screener/
│       │   │   ├── page.tsx        # 스크리너 메인 페이지
│       │   │   └── [ticker]/page.tsx # 종목 상세 페이지
│       │   └── globals.css         # 전역 CSS
│       ├── components/             # React 컴포넌트
│       │   ├── FilterPanel.tsx     # 필터 패널
│       │   ├── StockCard.tsx       # 종목 카드
│       │   ├── ScoreGauge.tsx      # 점수 게이지
│       │   └── CriteriaBreakdown.tsx # 기준별 분석
│       ├── lib/
│       │   ├── api.ts              # API 클라이언트
│       │   └── types.ts            # TypeScript 타입
│       └── package.json            # 의존성
│
├── docker-compose.yml              # 서비스 오케스트레이션
├── .env.example                    # 환경변수 템플릿
└── CLAUDE.md                       # 이 파일
```

## 스크리닝 기준 (12개)

### 저평가 지표 (4개)
- PER Ratio (주가수익비율)
- PB Ratio (주가순자산비율)
- PS Ratio (주가판매비)
- PEG Ratio (주가순이익성장비율)

### 수익성 지표 (5개)
- ROE (자기자본이익률)
- ROA (총자산이익률)
- Net Margin (순이익률)
- Gross Margin (매출총이익률)
- Operating Margin (영업이익률)

### 성장성 지표 (2개)
- Revenue Growth (매출 성장)
- EPS Growth (주당이익 성장)

### 재무 건강도 (4개)
- Debt-to-Equity (부채비율)
- Current Ratio (유동비율)
- Quick Ratio (당좌비율)
- Interest Coverage (이자보상배수)

## Celery 스케줄

```
KR 시장 데이터 수집:   매일 06:40 UTC
US 시장 데이터 수집:   매일 21:30 UTC
KR 시장 스크리닝:     매일 07:00 UTC
US 시장 스크리닝:     매일 22:00 UTC
```

변경: `/backend/app/tasks/schedules.py` 에서 `CELERY_BEAT_SCHEDULE` 수정

## 주요 명령어

### 데이터베이스 마이그레이션

```bash
cd backend

# 마이그레이션 생성
alembic revision --autogenerate -m "설명"

# 마이그레이션 적용
alembic upgrade head

# 이전 버전으로 롤백
alembic downgrade -1
```

### 테스트 실행

```bash
cd backend

# 모든 테스트
pytest

# 특정 테스트 실행
pytest tests/test_screening/test_criteria.py

# 커버리지 포함
pytest --cov=app
```

### 백엔드 로컬 개발 (Docker 없이)

```bash
cd backend

# 가상환경 활성화
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 의존성 설치
pip install -e ".[dev]"

# PostgreSQL 및 Redis 필요
export DATABASE_URL=postgresql://user:pass@localhost/dbname
export REDIS_URL=redis://localhost:6379/0

# 서버 시작
uvicorn app.main:app --reload

# Celery Worker (별도 터미널)
celery -A app.tasks.celery_app worker --loglevel=info

# Celery Beat (별도 터미널)
celery -A app.tasks.celery_app beat --loglevel=info
```

### 프론트엔드 로컬 개발

```bash
cd frontend/apps/web

# 의존성 설치
pnpm install

# 개발 서버
pnpm dev

# 빌드
pnpm build

# 프로덕션 서버
pnpm start
```

## 새로운 스크리닝 기준 추가

1. `/backend/app/core/screening/criteria/` 하위에 새 파일 생성:

```python
# example: revenue_growth.py
from app.core.screening.criteria.base import BaseCriteria

class RevenueGrowthCriteria(BaseCriteria):
    name = "Revenue Growth"
    category = "growth"
    
    def evaluate(self, metrics, sector_avg):
        if not metrics.get("revenue_growth"):
            return None
        
        growth = metrics["revenue_growth"]
        sector_growth = sector_avg.get("revenue_growth", 5.0)
        
        score = min(100, (growth / sector_growth) * 50 + 50)
        reason = f"수익 성장률: {growth:.1f}% (섹터 평균: {sector_growth:.1f}%)"
        
        return {"score": score, "reason": reason}
```

2. 엔진이 자동으로 탐색하고 등록합니다 (플러그인 아키텍처)

## 트러블슈팅

### 데이터베이스 연결 오류
```bash
docker compose logs db
lsof -i :5432
```

### Redis 연결 오류
```bash
redis-cli ping
docker compose logs redis
```

### Celery 태스크 미실행
```bash
docker compose logs worker
docker compose logs beat
docker compose exec backend celery -A app.tasks.celery_app call app.tasks.data_fetch.fetch_us_market
```

## API 키 설정

### Yahoo Finance (yfinance)
- 무료, 특별한 키 불필요

### Polygon.io (선택)
```bash
POLYGON_API_KEY=pk_...
```

### 한국 DART API (선택)
```bash
DART_API_KEY=...
```

### 1. 스크리닝 엔진 (플러그인 아키텍처)

**원칙**: 새 기준 추가 = 파일 하나 추가 (코드 변경 없음)

```python
# 1. BaseCriteria 인터페이스 구현
class MyNewCriteria(BaseCriteria):
    @property
    def criteria_id(self) -> str:
        return "unique_id"
    
    def evaluate(self, stock_data: dict, sector_benchmarks: dict) -> CriteriaResult:
        # 계산 로직
        return CriteriaResult(...)

# 2. 파일을 criteria/ 하위에 저장
# 3. CriteriaRegistry.auto_discover()가 자동 등록 (초기화 시)
# 4. ScreeningEngine에 자동으로 포함됨
```

**설계 문서**: `/root/project/stock-screener/design/screening/screening-engine.md`

### 2. 데이터 정규화 (원시 데이터 → 계산값)

```
외부 API (yfinance, DART)
    ↓
raw_financials (원시 JSON 저장 - 변경 불가)
    ↓
financial_metrics (정규화된 계산값 - 스크리닝에 사용)
    ↓
screening_results + criteria_scores (스크리닝 결과)
```

**핵심**: 원시 데이터 보존으로 언제든 재계산 가능

### 3. 마이그레이션 관리 (Alembic)

```bash
# 스키마 변경할 때
# 1. models/*.py 수정
# 2. 마이그레이션 파일 생성
docker-compose exec backend alembic revision --autogenerate -m "설명"

# 3. 확인 후 마이그레이션 적용
docker-compose exec backend alembic upgrade head

# 4. 커밋
git add backend/alembic/
git commit -m "feat(database): 설명"
```

### 4. Celery 태스크 스케줄

**Beat Schedule** (`app/tasks/schedules.py`):

```yaml
KR Market:
  - 데이터 수집: 매일 06:40 UTC (15:40 KST)
  - 스크리닝: 매일 07:00 UTC (16:00 KST)

US Market:
  - 데이터 수집: 매일 21:30 UTC (16:30 ET)
  - 스크리닝: 매일 22:00 UTC (17:00 ET)
```

**로그 보기**:
```bash
docker-compose logs -f beat     # 스케줄 실행 로그
docker-compose logs -f worker   # 태스크 실행 로그
```

## 개발 워크플로우

### API 엔드포인트 추가

1. **스키마 정의** (`app/schemas/`)
   ```python
   from pydantic import BaseModel
   
   class MyRequestSchema(BaseModel):
       field: str
   ```

2. **라우터 구현** (`app/api/v1/`)
   ```python
   from fastapi import APIRouter
   
   router = APIRouter()
   
   @router.get("/my-endpoint")
   async def my_endpoint():
       return {"status": "ok"}
   ```

3. **메인 앱 등록** (`app/main.py`)
   ```python
   from app.api.v1.my_endpoint import router
   app.include_router(router, prefix="/v1")
   ```

### 스크리닝 기준 추가 (3단계 예시)

**Step 1**: 파일 생성

```python
# backend/app/core/screening/criteria/valuation/new_metric.py

from ..base import BaseCriteria, CriteriaCategory, CriteriaResult
from typing import Optional

class NewMetricCriteria(BaseCriteria):
    @property
    def criteria_id(self) -> str:
        return "new_metric"
    
    @property
    def name(self) -> str:
        return "새로운 지표"
    
    @property
    def category(self) -> CriteriaCategory:
        return CriteriaCategory.VALUATION
    
    @property
    def weight(self) -> float:
        return 1.0
    
    @property
    def required_fields(self) -> list[str]:
        return ["field1", "field2"]
    
    def evaluate(
        self,
        stock_data: dict,
        sector_benchmarks: Optional[dict] = None,
    ) -> Optional[CriteriaResult]:
        value = stock_data.get("field1")
        if value is None:
            return None
        
        # 계산 로직
        score = min(1.0, max(0.0, value / 100))
        
        return CriteriaResult(
            criteria_id=self.criteria_id,
            score=score,
            raw_value=value,
            benchmark=50.0,
            is_undervalued=(value < 50),
            reason=f"값: {value}"
        )
```

**Step 2**: __init__.py에 명시적 임포트 (선택사항, auto-discovery가 할 것)

**Step 3**: 테스트 작성 및 커밋

```bash
git add backend/app/core/screening/criteria/
git commit -m "feat(screening): 새로운 지표 추가"
```

### 프론트엔드 페이지 추가

**Step 1**: 페이지 파일 생성

```typescript
// frontend/apps/web/app/my-page/page.tsx

export default function MyPage() {
  return <div>My Content</div>;
}
```

**Step 2**: 필요시 컴포넌트 분리

```typescript
// frontend/apps/web/components/MyComponent.tsx

export function MyComponent() {
  return <div>Component</div>;
}
```

**Step 3**: Next.js App Router가 자동 라우팅

## 데이터베이스 스키마

**주요 테이블**:

| 테이블 | 용도 |
|--------|------|
| `stocks` | 종목 마스터 |
| `raw_financials` | 원시 재무 데이터 (JSON) |
| `financial_metrics` | 정규화된 지표 |
| `screening_results` | 스크리닝 실행 결과 |
| `criteria_scores` | 기준별 점수 상세 |
| `sector_benchmarks` | 섹터 평균값 |
| `users` | 사용자 |
| `watchlists` | 관심 종목 |
| `user_screening_presets` | 사용자 맞춤 설정 |

**상세 스키마**: `/root/project/stock-screener/design/database/schema.md`

## 코드 스타일 & 규칙

### Python (Backend)

- **Type Hints**: 모든 함수에 타입 힌트 필수
- **Pydantic v2**: request/response 스키마
- **SQLAlchemy 2.0**: async ORM 사용
- **Docstrings**: Google style 사용

```python
def calculate_score(value: float, benchmark: float) -> float:
    """
    Calculate a normalized score.
    
    Args:
        value: Current value
        benchmark: Comparison benchmark
    
    Returns:
        Normalized score between 0.0 and 1.0
    """
    return min(1.0, value / benchmark)
```

### TypeScript (Frontend)

- **Strict Mode**: TypeScript strict 모드 활성화
- **No `any`**: any 타입 금지
- **Functional Components**: React 함수형 컴포넌트만 사용
- **Custom Hooks**: 로직 재사용 시 훅으로 추상화

```typescript
// ✅ Good
function MyComponent(): React.ReactNode {
  const data = useFetchData();
  return <div>{data}</div>;
}

// ❌ Bad
function MyComponent(): any {
  const data: any = fetchData();
  return <div>{data}</div>;
}
```

## 테스트

### 백엔드 테스트

```bash
# 모든 테스트 실행
docker-compose exec backend pytest

# 특정 파일
docker-compose exec backend pytest tests/test_screening_engine.py::test_engine_evaluation

# 커버리지 포함
docker-compose exec backend pytest --cov=app --cov-report=html
```

**테스트 작성 예시**:

```python
# tests/test_screening_engine.py

import pytest
from app.core.screening.engine import ScreeningEngine
from app.core.screening.registry import CriteriaRegistry

@pytest.fixture
def engine():
    return ScreeningEngine(CriteriaRegistry())

def test_engine_scores_high_on_undervalued_stock(engine):
    stock_data = {"pe_ratio": 8.5, "sector": "Tech"}
    results = engine.run([stock_data])
    
    assert len(results) == 1
    assert results[0].total_score > 70
```

### 프론트엔드 테스트

```bash
cd frontend/apps/web
npm run test
```

## 디버깅 팁

### 데이터베이스 쿼리 확인

```python
# config.py에서 설정
SQLALCHEMY_ECHO = True  # SQL 쿼리 출력
```

### API 응답 검증

```bash
# 직접 API 호출
curl -X GET "http://localhost:8000/v1/stocks" \
  -H "Authorization: Bearer your_token"

# 또는 API Docs 사용
# http://localhost:8000/docs
```

### Celery 태스크 디버깅

```bash
# Worker를 포그라운드에서 실행
docker-compose run --rm worker celery -A app.tasks worker --loglevel=debug

# 특정 태스크만 실행
docker-compose exec backend celery -A app.tasks inspect active
```

## 배포 체크리스트

배포 전 확인사항:

- [ ] 모든 테스트 통과 (pytest)
- [ ] 타입 체크 통과 (mypy, TypeScript strict)
- [ ] 린트 규칙 준수 (black, eslint)
- [ ] 보안 스캔 통과
- [ ] DB 마이그레이션 검증
- [ ] 환경 변수 설정 확인
- [ ] API 문서 최신화
- [ ] git 커밋 로그 정리

## 주요 문서 링크

| 문서 | 설명 |
|------|------|
| [시스템 아키텍처](./design/architecture/system-overview.md) | 전체 시스템 구성도 |
| [백엔드 설계](./design/architecture/backend-design.md) | 프로젝트 구조, 스크리닝 엔진 |
| [API 명세](./design/api/api-spec.md) | REST API 엔드포인트 전체 |
| [DB 스키마](./design/database/schema.md) | 데이터베이스 설계 |
| [스크리닝 엔진](./design/screening/screening-engine.md) | 기준 추가 방법 |
| [인프라](./design/infrastructure/infra.md) | Docker, 배포 설정 |

## Conventional Commits 규칙

**형식**: `type(scope): 한글 설명`

**Types**:
- `feat`: 새 기능
- `fix`: 버그 수정
- `chore`: 빌드/설정 (의존성, CI/CD)
- `refactor`: 동작 변경 없는 개선
- `docs`: 문서 변경
- `test`: 테스트 추가/변경
- `style`: 포맷팅, 스타일
- `perf`: 성능 개선

**예시**:

```bash
git commit -m "feat(screening): PE ratio 기준 추가"
git commit -m "fix(api): 스크리닝 결과 필터링 버그 수정"
git commit -m "docs: API 문서 업데이트"
git commit -m "chore: 의존성 업그레이드"
```

## 트러블슈팅

### "Connection refused" 에러

```bash
# Docker 컨테이너 상태 확인
docker-compose ps

# 재시작
docker-compose restart

# 로그 확인
docker-compose logs db
```

### 마이그레이션 충돌

```bash
# 최신 마이그레이션 확인
docker-compose exec backend alembic current

# 특정 버전으로 롤백
docker-compose exec backend alembic downgrade -1

# 다시 진행
docker-compose exec backend alembic upgrade head
```

### Celery 작업 정체

```bash
# Redis 상태 확인
docker-compose exec redis redis-cli info

# 큐 비우기
docker-compose exec backend celery -A app.tasks purge

# Worker 재시작
docker-compose restart worker
```

## 성능 모니터링

### 데이터베이스 슬로우 쿼리

```sql
-- PostgreSQL slow query log 확인
SELECT * FROM pg_stat_statements 
WHERE mean_time > 100 
ORDER BY mean_time DESC;
```

### API 응답 시간

```bash
# 응답 시간 측정
time curl http://localhost:8000/v1/screener/results
```

### Celery 작업 처리 시간

```bash
docker-compose logs worker | grep "Task took"
```

## 다음 학습 자료

- FastAPI 공식 문서: https://fastapi.tiangolo.com
- SQLAlchemy ORM: https://docs.sqlalchemy.org/20
- Celery Task Queue: https://docs.celeryproject.io
- Next.js App Router: https://nextjs.org/docs/app
- PostgreSQL 문서: https://www.postgresql.org/docs/16

---

**Last Updated**: 2026-05-17  
**Maintainer**: yschoi@ssrinc.co.kr
