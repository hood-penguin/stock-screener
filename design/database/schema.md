# 데이터베이스 스키마

## ERD 개요

```
stocks ──────< raw_financials
  │                │
  │                └──> financial_metrics (정규화된 계산값)
  │
  ├──────< screening_results
  │              │
  │              └──< criteria_scores
  │
  ├──────< sector_benchmarks
  │
users ──────< watchlists >──── stocks
  │
  └──────< user_screening_presets
```

## 테이블 정의

### stocks (종목 마스터)

```sql
CREATE TABLE stocks (
    id              BIGSERIAL PRIMARY KEY,
    ticker          VARCHAR(20)  NOT NULL,
    market          VARCHAR(4)   NOT NULL CHECK (market IN ('US', 'KR')),
    exchange        VARCHAR(20)  NOT NULL,  -- 'NYSE', 'NASDAQ', 'KOSPI', 'KOSDAQ'
    company_name    VARCHAR(200) NOT NULL,
    company_name_en VARCHAR(200),
    sector          VARCHAR(100),
    industry        VARCHAR(100),
    currency        VARCHAR(4)   NOT NULL DEFAULT 'USD',
    is_active       BOOLEAN      NOT NULL DEFAULT TRUE,
    listed_at       DATE,
    created_at      TIMESTAMPTZ  NOT NULL DEFAULT NOW(),
    updated_at      TIMESTAMPTZ  NOT NULL DEFAULT NOW(),
    UNIQUE (ticker, market)
);

CREATE INDEX idx_stocks_market_sector ON stocks (market, sector);
CREATE INDEX idx_stocks_active ON stocks (is_active) WHERE is_active = TRUE;
```

### raw_financials (원시 재무 데이터 — 변경 불가 이력 보존)

```sql
CREATE TABLE raw_financials (
    id              BIGSERIAL PRIMARY KEY,
    stock_id        BIGINT       NOT NULL REFERENCES stocks(id),
    source          VARCHAR(50)  NOT NULL,  -- 'polygon', 'kis_api', 'dart', ...
    fiscal_period   VARCHAR(10),            -- '2024Q3', '2024A'
    raw_json        JSONB        NOT NULL,  -- 소스 원본 데이터 그대로
    fetched_at      TIMESTAMPTZ  NOT NULL DEFAULT NOW(),
    data_as_of      DATE         NOT NULL
);

CREATE INDEX idx_raw_financials_stock_date ON raw_financials (stock_id, data_as_of DESC);
```

### financial_metrics (정규화·계산된 재무 지표)

```sql
CREATE TABLE financial_metrics (
    id                   BIGSERIAL PRIMARY KEY,
    stock_id             BIGINT       NOT NULL REFERENCES stocks(id),
    -- 가격 데이터
    price                NUMERIC(18,4),
    market_cap           NUMERIC(24,2),
    -- 밸류에이션
    pe_ratio             NUMERIC(10,4),
    pb_ratio             NUMERIC(10,4),
    ps_ratio             NUMERIC(10,4),
    ev_ebitda            NUMERIC(10,4),
    peg_ratio            NUMERIC(10,4),
    price_to_fcf         NUMERIC(10,4),
    -- 수익성
    roe                  NUMERIC(8,4),
    roa                  NUMERIC(8,4),
    gross_margin         NUMERIC(8,4),
    operating_margin     NUMERIC(8,4),
    net_margin           NUMERIC(8,4),
    -- 성장성
    revenue_growth_yoy   NUMERIC(8,4),
    eps_growth_yoy       NUMERIC(8,4),
    -- 재무건전성
    debt_to_equity       NUMERIC(10,4),
    current_ratio        NUMERIC(8,4),
    quick_ratio          NUMERIC(8,4),
    interest_coverage    NUMERIC(10,4),
    -- 기술적 지표 (확장 시 사용)
    rsi_14               NUMERIC(6,2),
    -- 메타
    data_as_of           DATE         NOT NULL,
    calculated_at        TIMESTAMPTZ  NOT NULL DEFAULT NOW(),
    UNIQUE (stock_id, data_as_of)
);

CREATE INDEX idx_metrics_stock_date ON financial_metrics (stock_id, data_as_of DESC);
CREATE INDEX idx_metrics_recent ON financial_metrics (data_as_of DESC);
```

### sector_benchmarks (섹터 집계 지표)

```sql
CREATE TABLE sector_benchmarks (
    id              BIGSERIAL PRIMARY KEY,
    market          VARCHAR(4)   NOT NULL,
    sector          VARCHAR(100) NOT NULL,
    metric_date     DATE         NOT NULL,
    -- 각 지표의 중앙값 (median)
    median_pe       NUMERIC(10,4),
    median_pb       NUMERIC(10,4),
    median_ev_ebitda NUMERIC(10,4),
    median_roe      NUMERIC(8,4),
    median_debt_eq  NUMERIC(10,4),
    stock_count     INTEGER      NOT NULL,
    UNIQUE (market, sector, metric_date)
);
```

### screening_results (스크리닝 실행 결과)

```sql
CREATE TABLE screening_results (
    id              BIGSERIAL PRIMARY KEY,
    stock_id        BIGINT       NOT NULL REFERENCES stocks(id),
    market          VARCHAR(4)   NOT NULL,
    total_score     NUMERIC(5,2) NOT NULL CHECK (total_score BETWEEN 0 AND 100),
    is_undervalued  BOOLEAN      NOT NULL,
    screened_at     TIMESTAMPTZ  NOT NULL DEFAULT NOW(),
    metrics_date    DATE         NOT NULL  -- 기반이 된 재무 데이터 날짜
);

CREATE INDEX idx_screening_market_score ON screening_results (market, total_score DESC);
CREATE INDEX idx_screening_date ON screening_results (screened_at DESC);
CREATE INDEX idx_screening_stock ON screening_results (stock_id, screened_at DESC);
```

### criteria_scores (기준별 세부 점수)

```sql
CREATE TABLE criteria_scores (
    id                BIGSERIAL PRIMARY KEY,
    screening_result_id BIGINT    NOT NULL REFERENCES screening_results(id) ON DELETE CASCADE,
    criteria_id       VARCHAR(100) NOT NULL,
    score             NUMERIC(5,4) NOT NULL CHECK (score BETWEEN 0 AND 1),
    raw_value         NUMERIC(18,4),
    benchmark_value   NUMERIC(18,4),
    is_undervalued    BOOLEAN,
    reason            TEXT
);

CREATE INDEX idx_criteria_result ON criteria_scores (screening_result_id);
```

### users

```sql
CREATE TABLE users (
    id              BIGSERIAL PRIMARY KEY,
    email           VARCHAR(255) NOT NULL UNIQUE,
    password_hash   VARCHAR(255) NOT NULL,
    display_name    VARCHAR(100),
    tier            VARCHAR(20)  NOT NULL DEFAULT 'free' CHECK (tier IN ('free', 'premium')),
    is_active       BOOLEAN      NOT NULL DEFAULT TRUE,
    created_at      TIMESTAMPTZ  NOT NULL DEFAULT NOW()
);
```

### watchlists (관심 종목)

```sql
CREATE TABLE watchlists (
    id              BIGSERIAL PRIMARY KEY,
    user_id         BIGINT       NOT NULL REFERENCES users(id),
    stock_id        BIGINT       NOT NULL REFERENCES stocks(id),
    alert_threshold NUMERIC(5,2),  -- 이 점수 이상이면 알림
    created_at      TIMESTAMPTZ  NOT NULL DEFAULT NOW(),
    UNIQUE (user_id, stock_id)
);
```

### user_screening_presets (사용자 맞춤 스크리닝 설정)

```sql
CREATE TABLE user_screening_presets (
    id               BIGSERIAL PRIMARY KEY,
    user_id          BIGINT       NOT NULL REFERENCES users(id),
    preset_name      VARCHAR(100) NOT NULL,
    is_default       BOOLEAN      NOT NULL DEFAULT FALSE,
    enabled_criteria JSONB        NOT NULL DEFAULT '[]',  -- 활성 기준 ID 목록
    weight_overrides JSONB        NOT NULL DEFAULT '{}',  -- {"criteria_id": weight}
    min_score        NUMERIC(5,2) DEFAULT 0,
    created_at       TIMESTAMPTZ  NOT NULL DEFAULT NOW(),
    UNIQUE (user_id, preset_name)
);
```

## 인덱스 전략 요약

| 쿼리 패턴 | 인덱스 |
|---|---|
| 시장별 최신 스크리닝 결과 조회 | `(market, total_score DESC)` |
| 특정 종목의 최신 재무 지표 | `(stock_id, data_as_of DESC)` |
| 섹터 필터 + 점수 정렬 | `(market, sector)` + `(total_score DESC)` |
| 사용자 관심 종목 | `(user_id, stock_id)` UNIQUE |

## 파티셔닝 전략

`screening_results`와 `raw_financials`는 데이터가 쌓이면 월별 파티셔닝 적용:

```sql
-- 예시 (데이터 누적 후 적용)
CREATE TABLE screening_results_2025_01 PARTITION OF screening_results
    FOR VALUES FROM ('2025-01-01') TO ('2025-02-01');
```
