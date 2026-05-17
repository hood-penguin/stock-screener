# 저평가 주식 탐색 서비스 (Stock Screener)

> 미국·한국 주식 시장에서 저평가 종목을 자동 발굴하는 풀스택 서비스

## 기술 스택

- **Backend**: FastAPI (Python 3.12) + SQLAlchemy + Celery + Redis
- **Frontend**: Next.js 15 (TypeScript) + TanStack Query + Zustand
- **Database**: PostgreSQL 16
- **Cache/Queue**: Redis 7
- **Infrastructure**: Docker Compose (개발), AWS ECS Fargate (운영)

## 빠른 시작 (로컬 개발)

### 요구사항
- Docker & Docker Compose
- Git

### 1단계: 프로젝트 클론 및 설정

```bash
git clone https://github.com/yschoi/stock-screener.git
cd stock-screener

# 환경 설정
cp .env.example .env
# .env 파일 수정 (필요시)
```

### 2단계: Docker Compose로 실행

```bash
docker-compose up --build
```

### 3단계: 데이터베이스 초기화

```bash
# 별도 터미널에서
docker-compose exec backend alembic upgrade head
docker-compose exec backend python -m app.scripts.seed_data
```

### 4단계: 서비스 접속

- **API Server**: http://localhost:8000
- **API Docs**: http://localhost:8000/docs
- **Frontend**: http://localhost:3000
- **Redis Commander**: http://localhost:8081

## 프로젝트 구조

```
stock-screener/
├── backend/                     # FastAPI 백엔드
│   ├── app/
│   │   ├── main.py             # FastAPI 앱 진입점
│   │   ├── config.py           # 환경 설정
│   │   ├── dependencies.py     # 의존성 주입
│   │   ├── api/v1/             # REST API 라우터
│   │   ├── core/
│   │   │   ├── screening/      # 스크리닝 엔진 (핵심)
│   │   │   └── security/       # JWT, 보안
│   │   ├── data/               # 데이터 프로바이더
│   │   ├── models/             # SQLAlchemy ORM
│   │   ├── schemas/            # Pydantic 스키마
│   │   └── tasks/              # Celery 태스크
│   ├── alembic/                # DB 마이그레이션
│   ├── tests/                  # 단위 테스트
│   └── pyproject.toml          # 의존성
│
├── frontend/                    # Next.js 프론트엔드
│   ├── apps/web/
│   │   ├── app/                # Next.js App Router
│   │   ├── components/         # 리액트 컴포넌트
│   │   ├── lib/                # 유틸, API 클라이언트
│   │   └── package.json
│   └── packages/shared-ui/     # 공유 UI 컴포넌트
│
├── design/                      # 설계 문서
│   ├── architecture/
│   ├── api/
│   ├── database/
│   ├── screening/
│   └── infrastructure/
│
├── docker-compose.yml           # 로컬 개발 환경
└── README.md
```

## 주요 기능

### 1. 저평가 주식 스크리닝
- **12개 기준**: PE ratio, PB ratio, EV/EBITDA, PEG, ROE, ROA, 성장률, 재무건전성
- **플러그인 아키텍처**: 코드 변경 없이 기준 추가 가능
- **시장별 벤치마크**: 섹터 평균과 비교해 저평가 판단

### 2. 다중 시장 지원
- **미국 (US)**: S&P 500 (yfinance)
- **한국 (KR)**: KOSPI/KOSDAQ (DART API)
- 시장별 자동 데이터 수집 및 정규화

### 3. 사용자 맞춤 설정
- 스크리닝 기준 선택
- 스크리닝 결과 필터링 (섹터, 최소 점수)
- 관심 종목 (Watchlist) 관리
- 커스텀 프리셋 저장

### 4. 자동 스케줄링
- Celery Beat로 매일 자동 스크리닝 실행
- 미국: UTC 22:00 (ET 16:30), 한국: UTC 07:00 (KST 15:40)

## API 문서

FastAPI 자동 문서:
- **OpenAPI (Swagger)**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

주요 엔드포인트:

```
# 인증
POST   /v1/auth/register          등록
POST   /v1/auth/login             로그인
POST   /v1/auth/refresh           토큰 갱신

# 스크리닝
GET    /v1/screener/results       저평가 종목 목록
GET    /v1/screener/results/{ticker}  결과 상세

# 종목
GET    /v1/stocks                 모든 종목
GET    /v1/stocks/{ticker}        종목 상세
GET    /v1/sectors                사용 가능 섹터

# 관심 종목
GET    /v1/watchlist              내 관심 종목
POST   /v1/watchlist              추가
DELETE /v1/watchlist/{stock_id}   제거

# 설정
GET    /v1/presets                내 프리셋
POST   /v1/presets                생성
PUT    /v1/presets/{preset_id}    수정
DELETE /v1/presets/{preset_id}    삭제
```

## 개발 가이드

### 스크리닝 기준 추가

새 기준을 추가하려면 파일 하나만 생성하면 됩니다:

```python
# backend/app/core/screening/criteria/valuation/momentum_indicator.py

from ..base import BaseCriteria, CriteriaCategory, CriteriaResult
from typing import Optional

class MomentumIndicatorCriteria(BaseCriteria):
    @property
    def criteria_id(self) -> str:
        return "momentum_indicator"
    
    @property
    def name(self) -> str:
        return "모멘텀 지표"
    
    @property
    def category(self) -> CriteriaCategory:
        return CriteriaCategory.GROWTH
    
    def evaluate(
        self, 
        stock_data: dict, 
        sector_benchmarks: Optional[dict] = None
    ) -> Optional[CriteriaResult]:
        # Your implementation here
        pass
```

파일 추가 후 자동으로 스크리닝 엔진에 등록됩니다!

### 테스트 실행

```bash
# 모든 테스트
docker-compose exec backend pytest

# 특정 테스트 파일
docker-compose exec backend pytest tests/test_screening_engine.py

# 커버리지 포함
docker-compose exec backend pytest --cov=app tests/
```

### 로그 보기

```bash
# 전체 로그
docker-compose logs -f

# 특정 서비스만
docker-compose logs -f backend
docker-compose logs -f worker
docker-compose logs -f beat
```

## 배포

### 스테이징 (AWS ECS)

```bash
# 스테이징 배포
./scripts/deploy.sh staging

# 환경 변수 설정
export AWS_PROFILE=your-profile
export DOCKER_REGISTRY=your-registry
```

### 프로덕션

```bash
# 프로덕션 배포
./scripts/deploy.sh production
```

## 문제 해결

### 데이터베이스 연결 오류

```bash
# 데이터베이스 로그 확인
docker-compose logs db

# 데이터베이스 재설정
docker-compose down -v
docker-compose up -d db
docker-compose exec backend alembic upgrade head
```

### Celery 작업이 실행되지 않음

```bash
# Worker 로그 확인
docker-compose logs worker

# Redis 연결 확인
docker-compose exec redis redis-cli ping
```

## 성능 최적화

- **데이터베이스 인덱싱**: 자동 생성 (마이그레이션 포함)
- **API 캐싱**: Redis 캐시 (5분 TTL)
- **스크리닝 병렬화**: Celery로 종목별 병렬 평가
- **프론트엔드**: Next.js SSR, 이미지 최적화

## 기여 가이드

1. Feature branch 생성: `git checkout -b feat/new-feature`
2. Conventional Commits 형식으로 커밋
3. Pull Request 생성
4. 코드 리뷰 + 테스트 통과 후 merge

## 라이선스

MIT License

## 저자

yschoi (yschoi@ssrinc.co.kr)

## 지원

이슈 또는 질문: https://github.com/yschoi/stock-screener/issues
