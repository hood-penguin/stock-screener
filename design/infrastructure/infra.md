# 인프라 설계

## 환경 구성

| 환경 | 목적 | 구성 |
|---|---|---|
| `local` | 개발자 로컬 | Docker Compose |
| `staging` | QA 및 통합 테스트 | AWS ECS (단일 태스크) |
| `production` | 서비스 운영 | AWS ECS Fargate (오토스케일링) |

## 로컬 개발 환경 (Docker Compose)

```yaml
# docker-compose.yml

services:
  db:
    image: postgres:16-alpine
    environment:
      POSTGRES_DB: stockscreener
      POSTGRES_PASSWORD: localpassword
    ports: ["5432:5432"]
    volumes: ["pgdata:/var/lib/postgresql/data"]

  redis:
    image: redis:7-alpine
    ports: ["6379:6379"]

  backend:
    build: ./backend
    ports: ["8000:8000"]
    environment:
      DATABASE_URL: postgresql://postgres:localpassword@db/stockscreener
      REDIS_URL: redis://redis:6379/0
    depends_on: [db, redis]
    volumes: ["./backend:/app"]
    command: uvicorn app.main:app --reload --host 0.0.0.0

  worker:
    build: ./backend
    environment:
      DATABASE_URL: postgresql://postgres:localpassword@db/stockscreener
      REDIS_URL: redis://redis:6379/0
    depends_on: [db, redis]
    command: celery -A app.tasks worker --loglevel=info

  beat:
    build: ./backend
    environment:
      REDIS_URL: redis://redis:6379/0
    depends_on: [redis]
    command: celery -A app.tasks beat --loglevel=info

  web:
    build: ./frontend/apps/web
    ports: ["3000:3000"]
    environment:
      NEXT_PUBLIC_API_URL: http://localhost:8000/v1

volumes:
  pgdata:
```

## 프로덕션 아키텍처 (AWS)

```
┌─────────────────────────────────────────────────────────┐
│                      AWS VPC                             │
│                                                         │
│  ┌─────────────────────────────────────────────────┐   │
│  │               Public Subnet                      │   │
│  │                                                 │   │
│  │   Route 53 → CloudFront → ALB                   │   │
│  │                              │                  │   │
│  └──────────────────────────────┼──────────────────┘   │
│                                 │                       │
│  ┌──────────────────────────────┼──────────────────┐   │
│  │               Private Subnet                     │   │
│  │                              │                  │   │
│  │   ECS Fargate ←──────────────┘                   │   │
│  │   ┌──────────────┐  ┌──────────────┐            │   │
│  │   │ API Tasks    │  │ Worker Tasks │            │   │
│  │   │ (FastAPI)    │  │ (Celery)     │            │   │
│  │   │ 2~10 인스턴스 │  │ 2~6 인스턴스 │            │   │
│  │   └──────┬───────┘  └──────┬───────┘            │   │
│  │          │                 │                    │   │
│  │   ┌──────▼─────────────────▼───────┐            │   │
│  │   │         ElastiCache (Redis)    │            │   │
│  │   │         RDS PostgreSQL         │            │   │
│  │   └───────────────────────────────┘            │   │
│  └────────────────────────────────────────────────┘   │
│                                                         │
└─────────────────────────────────────────────────────────┘

  Vercel/Next.js ─── CDN ─── 사용자 (Web)
  Expo EAS ────────────────── 사용자 (App)
```

## 컨테이너 이미지 구성

```dockerfile
# backend/Dockerfile

FROM python:3.12-slim AS base
WORKDIR /app
COPY pyproject.toml .
RUN pip install --no-cache-dir .

FROM base AS production
COPY app/ app/
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "4"]
```

## 환경 변수

```bash
# 공통
DATABASE_URL=postgresql://user:pass@host/db
REDIS_URL=redis://host:6379/0
SECRET_KEY=<32자 이상 랜덤>
ENVIRONMENT=production

# 데이터 소스 API 키
POLYGON_API_KEY=<key>
KIS_APP_KEY=<key>
KIS_APP_SECRET=<key>
DART_API_KEY=<key>

# 알림
EXPO_ACCESS_TOKEN=<key>   # 모바일 푸시
SMTP_HOST=<smtp host>
SMTP_PORT=587
SMTP_USER=<email>
SMTP_PASSWORD=<password>
```

## 스케일링 전략

| 컴포넌트 | 스케일링 트리거 | 최소/최대 |
|---|---|---|
| API Server | CPU > 70% 또는 요청 대기 > 100 | 2 / 10 |
| Celery Worker | 큐 길이 > 50 | 2 / 6 |
| RDS | 읽기: Read Replica, 쓰기: 단일 Primary | - |
| ElastiCache | 메모리 > 80% | 단일 노드 → 클러스터 |

## CI/CD 파이프라인

```
GitHub Push → GitHub Actions
                    │
          ┌─────────┴──────────┐
          ▼                    ▼
    pytest 실행          ESLint/TypeCheck
    (백엔드 테스트)       (프론트엔드 검사)
          │                    │
          └─────────┬──────────┘
                    ▼
           Docker 이미지 빌드
                    │
            ┌───────┴───────┐
            ▼               ▼
        staging 배포    (main 브랜치)
            │           production 배포
            ▼
        통합 테스트 실행
```

## 모니터링

| 항목 | 도구 |
|---|---|
| 애플리케이션 메트릭 | AWS CloudWatch |
| 에러 추적 | Sentry |
| 로그 집계 | CloudWatch Logs |
| 스크리닝 실행 현황 | 내부 대시보드 (Celery Flower) |
| 업타임 모니터링 | AWS Route 53 Health Check |
