# Stock Screener

저평가 주식을 자동으로 탐색하는 풀스택 웹 애플리케이션입니다. 미국 및 한국 주식 시장의 재무 지표를 분석하여 투자 기회를 발굴합니다.

## 주요 특징

- **12가지 재무 지표**: 저평가, 수익성, 성장성, 재무 건강도 기반 평가
- **자동 데이터 수집**: Celery를 통한 정기적인 시장 데이터 업데이트
- **실시간 스크리닝**: 조건에 맞는 저평가 종목 즉시 조회
- **필터링**: 시장, 섹터, 점수 범위로 결과 필터링
- **상세 분석**: 종목별 종합 점수 및 기준별 상세 분석
- **반응형 디자인**: 모든 장치에서 최적화된 UI

## 기술 스택

- **백엔드**: FastAPI, SQLAlchemy, Celery, Redis
- **프론트엔드**: Next.js 15, React 18, TailwindCSS, React Query
- **데이터베이스**: PostgreSQL 16
- **캐싱**: Redis 7
- **메시지 브로커**: Redis
- **데이터 소스**: yfinance (Yahoo Finance)

## 빠른 시작

### 사전 요구사항

- Docker & Docker Compose
- Python 3.12+ (로컬 개발)
- Node.js 20+ (로컬 개발)

### 환경 설정

```bash
# 저장소 클론
git clone <repository-url>
cd stock-screener

# 환경 파일 생성
cp .env.example .env

# .env에서 SECRET_KEY 변경
nano .env
```

### Docker로 실행 (권장)

```bash
# 모든 서비스 시작
docker compose up -d

# 데이터베이스 마이그레이션
docker compose exec backend alembic upgrade head

# 접속
# 프론트엔드: http://localhost:3000
# API: http://localhost:8000
# API Docs: http://localhost:8000/docs
```

### 로컬 개발 (Docker 없이)

```bash
# 백엔드 설정
cd backend
python -m venv venv
source venv/bin/activate
pip install -e ".[dev]"

export DATABASE_URL=postgresql://user:pass@localhost/stockscreener
export REDIS_URL=redis://localhost:6379/0

# 마이그레이션
alembic upgrade head

# 서버 실행
uvicorn app.main:app --reload

# 프론트엔드 설정 (별도 터미널)
cd frontend/apps/web
pnpm install
pnpm dev
```

## API 엔드포인트

### 인증
- `POST /v1/auth/register` - 회원가입
- `POST /v1/auth/login` - 로그인
- `GET /v1/auth/me` - 현재 사용자 정보

### 스크리닝
- `GET /v1/screener/results` - 스크리닝 결과 조회
- `GET /v1/screener/results/{ticker}` - 종목 상세 정보

### 주식
- `GET /v1/stocks/{ticker}` - 주식 정보 조회
- `GET /v1/stocks` - 종목 검색

## 평가 기준 (12개)

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

## 자동 스케줄

Celery Beat를 통한 정기적인 데이터 수집 및 스크리닝:

- **KR 시장 데이터 수집**: 매일 06:40 UTC
- **US 시장 데이터 수집**: 매일 21:30 UTC
- **KR 시장 스크리닝**: 매일 07:00 UTC
- **US 시장 스크리닝**: 매일 22:00 UTC

## 프로젝트 구조

```
stock-screener/
├── backend/
│   ├── app/
│   │   ├── api/v1/              # API 라우터
│   │   ├── core/                # 스크리닝 엔진
│   │   ├── data/                # 데이터 프로바이더
│   │   ├── models/              # DB 모델
│   │   ├── tasks/               # Celery 태스크
│   │   └── ...
│   └── tests/                   # 테스트
├── frontend/
│   └── apps/web/                # Next.js 앱
│       ├── app/                 # 페이지
│       ├── components/          # React 컴포넌트
│       ├── lib/                 # 유틸리티
│       └── ...
├── docker-compose.yml           # 서비스 구성
└── README.md                    # 이 파일
```

## 개발 가이드

### 새로운 스크리닝 기준 추가

`/backend/app/core/screening/criteria/` 디렉터리에 새 파일을 생성하고 `BaseCriteria`를 상속받아 구현하면 자동으로 등록됩니다 (플러그인 아키텍처).

### 테스트 실행

```bash
cd backend
pytest                           # 모든 테스트
pytest tests/test_screening/     # 특정 디렉터리
pytest --cov=app                # 커버리지 포함
```

### 마이그레이션

```bash
cd backend
alembic revision --autogenerate -m "description"
alembic upgrade head
alembic downgrade -1
```

## 트러블슈팅

### 포트 충돌
```bash
# 포트 사용 확인
lsof -i :8000
lsof -i :3000
lsof -i :5432
lsof -i :6379
```

### 데이터베이스 초기화
```bash
docker compose down -v
docker compose up -d
docker compose exec backend alembic upgrade head
```

### Celery 태스크 문제
```bash
docker compose logs worker
docker compose logs beat
docker compose exec backend celery -A app.tasks.celery_app call app.tasks.data_fetch.fetch_us_market
```

## 배포

### Docker를 이용한 배포

```bash
# 이미지 빌드
docker compose build

# 환경 설정
cp .env.example .env
# .env 파일 수정 (SECRET_KEY, DEBUG=False, ENVIRONMENT=production)

# 배포
docker compose -f docker-compose.yml up -d
```

### 환경 변수 체크리스트

- [ ] `SECRET_KEY` 변경 (32자 이상의 랜덤 문자열)
- [ ] `DEBUG=False` 설정
- [ ] `ENVIRONMENT=production` 설정
- [ ] `DATABASE_URL` 프로덕션 데이터베이스 URL
- [ ] `REDIS_URL` 프로덕션 Redis URL
- [ ] HTTPS 및 CORS 설정 확인

## 라이센스

MIT

## 기여

pull request와 이슈 제출을 환영합니다!

## 문의

개발 관련 질문이나 버그 리포트는 이슈 또는 discussions을 사용해주세요.

---

**상태**: Phase 10 완료 (모든 기능 구현)
**마지막 업데이트**: 2026-05-17

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
