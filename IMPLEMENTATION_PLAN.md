# Stock Screener Service - Implementation Plan

**Status**: Planning Phase  
**Start Date**: 2026-05-17  
**Target Completion**: 2026-05-24 (7 days)  
**Priority**: MVP with complete architecture

## Execution Strategy

This is a large-scale full-stack project requiring systematic, phase-based execution:

1. **Phase 1: Project Foundation** (Git + Structure)
2. **Phase 2: Backend Foundation** (Models + Migrations)
3. **Phase 3: Backend Core** (Screening Engine)
4. **Phase 4: Backend API** (REST Endpoints)
5. **Phase 5: Backend Tasks** (Celery Jobs)
6. **Phase 6: Frontend Foundation** (Next.js Setup)
7. **Phase 7: Frontend UI** (Pages & Components)
8. **Phase 8: Infrastructure** (Docker Compose)
9. **Phase 9: Testing & Documentation**
10. **Phase 10: GitHub & Deployment**

## Phase 1: Project Foundation (Est. 30 min)

### Deliverables
- [ ] Git repository initialized
- [ ] User config set (yschoi@ssrinc.co.kr / yschoi)
- [ ] `.gitignore` created (Python + Node.js)
- [ ] Directory structure created
- [ ] `.env.example` created
- [ ] `CLAUDE.md` created with project overview
- [ ] Initial commit

### Tasks
```bash
# 1. Git init
git init
git config user.email "yschoi@ssrinc.co.kr"
git config user.name "yschoi"

# 2. Create .gitignore
# See below for full content

# 3. Create directory structure
mkdir -p backend/app/{api/v1,core/screening/criteria/{valuation,profitability,growth,financial_health},data/providers,models,schemas,tasks} backend/alembic/versions backend/tests
mkdir -p frontend/apps/web/{app,components,lib} frontend/packages/shared-ui
mkdir -p docker

# 4. Create .env.example
# See below for full content

# 5. Create README.md, CLAUDE.md

# 6. Initial commit
git add .
git commit -m "chore: 초기 프로젝트 설정 및 디렉터리 구조 생성"
```

## Phase 2: Backend Foundation (Est. 2 hours)

### Deliverables
- [ ] `pyproject.toml` with all dependencies
- [ ] `app/config.py` (Pydantic settings)
- [ ] `app/main.py` (FastAPI entry point)
- [ ] SQLAlchemy ORM models (8 tables)
- [ ] Pydantic request/response schemas
- [ ] Alembic migration (initial schema)
- [ ] Database initialization script
- [ ] Commits: 5-7 atomic commits

### Dependencies
```toml
fastapi = "^0.109.0"
uvicorn = "^0.27.0"
sqlalchemy = "^2.0"
pydantic = "^2.0"
pydantic-settings = "^2.0"
alembic = "^1.13.0"
psycopg2-binary = "^2.9"
redis = "^5.0"
celery = "^5.3"
yfinance = "^0.2"
python-jose = "^3.3"
passlib = "^1.7"
python-dotenv = "^1.0"
pytest = "^7.4"
httpx = "^0.25"
```

## Phase 3: Backend Core - Screening Engine (Est. 2.5 hours)

### Deliverables
- [ ] Criteria base class (`criteria/base.py`)
- [ ] Criteria registry (`registry.py`) with auto-discovery
- [ ] Scoring engine (`scorer.py`)
- [ ] 12 screening criteria implementations:
  - Valuation: PE ratio, PB ratio, EV/EBITDA, PEG, Price/FCF
  - Profitability: ROE, ROA, Gross Margin, Operating Margin
  - Growth: Revenue growth, EPS growth
  - Financial Health: Debt ratio, Current ratio
- [ ] Market adapters (US & KR)
- [ ] Commits: 8-10 atomic commits

### File Structure
```
app/core/screening/
├── criteria/
│   ├── base.py (BaseCriteria, CriteriaResult, CriteriaCategory)
│   ├── valuation/
│   │   ├── __init__.py
│   │   ├── pe_ratio.py
│   │   ├── pb_ratio.py
│   │   ├── ev_ebitda.py
│   │   ├── peg_ratio.py
│   │   └── price_to_fcf.py
│   ├── profitability/
│   │   ├── __init__.py
│   │   ├── roe.py
│   │   ├── roa.py
│   │   ├── gross_margin.py
│   │   └── operating_margin.py
│   ├── growth/
│   │   ├── __init__.py
│   │   ├── revenue_growth.py
│   │   └── eps_growth.py
│   └── financial_health/
│       ├── __init__.py
│       ├── debt_ratio.py
│       └── current_ratio.py
├── registry.py (CriteriaRegistry with auto-discovery)
├── scorer.py (ScreeningEngine, composite scoring)
├── engine.py (Main orchestrator)
└── __init__.py
```

## Phase 4: Backend API - Endpoints (Est. 2 hours)

### Deliverables
- [ ] JWT authentication (register, login, refresh)
- [ ] Stock endpoints (list, detail, sectors)
- [ ] Screener endpoints (results with filtering)
- [ ] Watchlist CRUD
- [ ] User presets CRUD
- [ ] Error handlers & response schemas
- [ ] CORS middleware
- [ ] Rate limiting setup
- [ ] Commits: 5-7 atomic commits

### Endpoints
```
POST   /v1/auth/register          → User registration
POST   /v1/auth/login             → User login
POST   /v1/auth/refresh           → Token refresh

GET    /v1/stocks                 → List all stocks
GET    /v1/stocks/{ticker}        → Stock details
GET    /v1/sectors                → Available sectors

GET    /v1/screener/results       → Screening results (filtered)
GET    /v1/screener/results/{ticker} → Result details
POST   /v1/screener/run           → Trigger screening job

GET    /v1/watchlist              → User's watchlist
POST   /v1/watchlist              → Add to watchlist
DELETE /v1/watchlist/{stock_id}   → Remove from watchlist

GET    /v1/presets                → User's screening presets
POST   /v1/presets                → Create preset
PUT    /v1/presets/{preset_id}    → Update preset
DELETE /v1/presets/{preset_id}    → Delete preset
```

## Phase 5: Backend Tasks - Celery (Est. 1 hour)

### Deliverables
- [ ] Celery app setup
- [ ] Data fetch tasks (US & KR markets)
- [ ] Screening execution task
- [ ] Beat schedule configuration
- [ ] Error handling & retry logic
- [ ] Commits: 3-4 atomic commits

### Tasks
```
fetch_us_market (yfinance)     → Daily after US market close
fetch_kr_market (placeholder)  → Daily after KR market close
run_screening                  → After data fetch completes
```

## Phase 6: Frontend Foundation - Next.js Setup (Est. 1 hour)

### Deliverables
- [ ] Next.js 15 project initialized
- [ ] TypeScript configuration
- [ ] TailwindCSS setup
- [ ] pnpm monorepo configuration
- [ ] API client library (axios/fetch wrapper)
- [ ] Type definitions from backend schemas
- [ ] Environment configuration
- [ ] Commits: 2-3 atomic commits

### Structure
```
frontend/
├── package.json (pnpm workspaces)
├── apps/web/ (Next.js 15 App Router)
│   ├── app/
│   │   ├── layout.tsx
│   │   ├── page.tsx (redirects to /screener)
│   │   ├── (auth)/
│   │   │   ├── login/page.tsx
│   │   │   └── register/page.tsx
│   │   ├── dashboard/page.tsx
│   │   ├── screener/
│   │   │   ├── page.tsx (list)
│   │   │   └── [ticker]/page.tsx (detail)
│   │   └── watchlist/page.tsx
│   ├── components/ (reusable UI)
│   ├── lib/ (utilities, API client, types)
│   ├── package.json
│   └── next.config.ts
└── packages/shared-ui/ (shared components)
```

## Phase 7: Frontend UI - Pages & Components (Est. 2.5 hours)

### Deliverables
- [ ] Authentication pages (login, register)
- [ ] Dashboard page (overview stats)
- [ ] Screener page (results list with filters)
- [ ] Stock detail page (score breakdown)
- [ ] Watchlist page
- [ ] Core components:
  - StockCard (summary view)
  - ScoreGauge (visual score display)
  - CriteriaBreakdown (criteria details)
  - FilterPanel (screening filters)
  - MarketBadge (market indicator)
- [ ] TanStack Query integration
- [ ] Zustand store for filters
- [ ] Commits: 6-8 atomic commits

### Key Features
- Real-time filtering with URL params
- Score visualization
- Responsive design (mobile-first)
- Dark mode support (Tailwind)
- Loading states & error handling

## Phase 8: Infrastructure - Docker Compose (Est. 1 hour)

### Deliverables
- [ ] `docker-compose.yml` (6 services)
- [ ] Backend `Dockerfile`
- [ ] Frontend build setup
- [ ] Startup scripts
- [ ] Health checks
- [ ] Volume management
- [ ] Network configuration
- [ ] Commits: 2-3 atomic commits

### Services
```yaml
db:      postgres:16-alpine
redis:   redis:7-alpine
backend: FastAPI (8000)
worker:  Celery worker
beat:    Celery beat scheduler
web:     Next.js (3000)
```

## Phase 9: Testing & Documentation (Est. 1.5 hours)

### Deliverables
- [ ] Unit tests for screening engine
- [ ] Integration tests for API endpoints
- [ ] Database seeding for development
- [ ] API documentation (OpenAPI/Swagger)
- [ ] CLAUDE.md project guide
- [ ] Development setup guide
- [ ] Commits: 3-4 atomic commits

### Test Coverage
- Screening criteria accuracy
- API endpoint validation
- Database migrations
- Authentication flow

## Phase 10: GitHub & Final Setup (Est. 30 min)

### Deliverables
- [ ] GitHub repository created
- [ ] All commits pushed
- [ ] README with setup instructions
- [ ] GitHub Actions (optional, CI/CD)
- [ ] Commits: 1 final commit

---

## Commit Message Convention

**Format**: `type(scope): 한글 설명`

Examples:
```
chore: 초기 프로젝트 설정 및 .gitignore 추가
feat(backend): SQLAlchemy 모델 및 Alembic 마이그레이션 추가
feat(backend): 스크리닝 엔진 플러그인 아키텍처 구현
feat(backend): FastAPI v1 엔드포인트 및 인증 구현
feat(backend): Celery 태스크 및 Beat 스케줄 추가
feat(frontend): Next.js 초기 설정 및 TailwindCSS 통합
feat(frontend): 스크리너 페이지 및 UI 컴포넌트 구현
chore: Docker Compose 및 환경 설정 추가
test: 스크리닝 엔진 단위 테스트 추가
docs: 프로젝트 CLAUDE.md 작성
```

## Risk & Mitigation

| Risk | Mitigation |
|------|-----------|
| Large scope | Phase-based execution with clear milestones |
| Database complexity | Use Alembic for version control, test migrations early |
| Plugin architecture | Implement registry early with auto-discovery tests |
| Frontend data sync | Use TanStack Query with proper caching strategy |
| Docker networking | Test each service independently first |

## Success Criteria

✅ All tests passing  
✅ Screening engine can evaluate 50+ stocks  
✅ API endpoints respond correctly  
✅ Frontend displays results with filtering  
✅ Docker Compose runs all services  
✅ GitHub repository with clean commit history  
✅ CLAUDE.md documents architecture and patterns

---

## Next Steps

1. Execute Phase 1 immediately (30 min)
2. Review plan, adjust if needed
3. Execute Phases 2-5 sequentially (backend)
4. Execute Phases 6-7 in parallel (frontend)
5. Execute Phases 8-10 after core features complete

**Estimated Total Time**: 14-16 hours of focused work
