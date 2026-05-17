# API 명세

Base URL: `https://api.stockscreener.app/v1`

## 인증

모든 API는 JWT Bearer 토큰 필요 (공개 조회 제외)

```
Authorization: Bearer <token>
```

---

## 인증 API

### POST /auth/register
회원 가입

**Request**
```json
{
  "email": "user@example.com",
  "password": "string",
  "displayName": "홍길동"
}
```

**Response 201**
```json
{
  "userId": 1,
  "email": "user@example.com",
  "token": "eyJ..."
}
```

### POST /auth/login
로그인

**Response 200**
```json
{
  "token": "eyJ...",
  "refreshToken": "eyJ...",
  "expiresIn": 3600
}
```

---

## 스크리닝 API

### GET /screener/results
저평가 종목 목록 조회 (스크리닝 결과)

**Query Parameters**

| 파라미터 | 타입 | 기본값 | 설명 |
|---|---|---|---|
| `market` | `US\|KR\|ALL` | `ALL` | 시장 필터 |
| `sector` | `string[]` | - | 섹터 필터 (복수 선택) |
| `minScore` | `number` | `0` | 최소 저평가 점수 (0~100) |
| `sortBy` | `string` | `totalScore` | 정렬 기준 |
| `sortOrder` | `asc\|desc` | `desc` | 정렬 방향 |
| `page` | `number` | `1` | 페이지 번호 |
| `pageSize` | `20\|50\|100` | `20` | 페이지 크기 |
| `presetId` | `number` | - | 사용자 맞춤 프리셋 ID |

**Response 200**
```json
{
  "data": [
    {
      "ticker": "AAPL",
      "market": "US",
      "companyName": "Apple Inc.",
      "sector": "Technology",
      "exchange": "NASDAQ",
      "currency": "USD",
      "price": 185.20,
      "marketCap": 2870000000000,
      "totalScore": 82.4,
      "isUndervalued": true,
      "topCriteria": [
        {
          "criteriaId": "pe_ratio_vs_sector",
          "name": "PER vs 섹터",
          "score": 85.0,
          "reason": "PER 14.2 = 섹터 평균(24.1)의 59%"
        }
      ],
      "screenedAt": "2025-01-15T22:00:00Z"
    }
  ],
  "pagination": {
    "total": 342,
    "page": 1,
    "pageSize": 20,
    "totalPages": 18
  },
  "meta": {
    "lastScreenedAt": "2025-01-15T22:00:00Z",
    "totalStocksEvaluated": 5847
  }
}
```

### GET /screener/results/{ticker}
특정 종목의 상세 스크리닝 결과

**Path Parameters**: `ticker` (예: `AAPL`, `005930.KR`)

**Response 200**
```json
{
  "ticker": "AAPL",
  "market": "US",
  "companyName": "Apple Inc.",
  "totalScore": 82.4,
  "isUndervalued": true,
  "criteriaDetails": [
    {
      "criteriaId": "pe_ratio_vs_sector",
      "name": "PER vs 섹터 평균",
      "category": "valuation",
      "score": 85.0,
      "rawValue": 14.2,
      "benchmark": 24.1,
      "isUndervalued": true,
      "reason": "PER 14.2 = 섹터 평균(24.1)의 59%"
    },
    {
      "criteriaId": "roe_vs_sector",
      "name": "ROE vs 섹터 평균",
      "category": "profitability",
      "score": 92.0,
      "rawValue": 28.4,
      "benchmark": 15.2,
      "isUndervalued": false,
      "reason": "ROE 28.4%로 섹터 평균(15.2%)보다 높음"
    }
  ],
  "financialSummary": {
    "price": 185.20,
    "marketCap": 2870000000000,
    "peRatio": 14.2,
    "pbRatio": 2.1,
    "evEbitda": 8.2,
    "roe": 28.4,
    "debtToEquity": 1.45
  },
  "screenedAt": "2025-01-15T22:00:00Z"
}
```

---

## 종목 API

### GET /stocks
종목 목록 조회 (검색용)

**Query Parameters**: `query`, `market`, `page`, `pageSize`

### GET /stocks/{ticker}
종목 기본 정보 및 최신 재무 데이터

### GET /stocks/{ticker}/history
과거 스크리닝 점수 이력

**Response 200**
```json
{
  "ticker": "AAPL",
  "history": [
    { "date": "2025-01-15", "totalScore": 82.4, "price": 185.20 },
    { "date": "2025-01-14", "totalScore": 79.1, "price": 183.50 }
  ]
}
```

---

## 기준(Criteria) API

### GET /criteria
사용 가능한 모든 스크리닝 기준 목록

**Response 200**
```json
{
  "criteria": [
    {
      "criteriaId": "pe_ratio_vs_sector",
      "name": "PER vs 섹터 평균",
      "category": "valuation",
      "description": "주가수익비율(PER)을 동일 섹터 중앙값과 비교",
      "weight": 1.5,
      "requiredFields": ["pe_ratio", "sector"]
    }
  ],
  "categories": ["valuation", "profitability", "growth", "financial_health"]
}
```

---

## 관심 종목 API

### GET /watchlist
사용자 관심 종목 목록 (인증 필요)

### POST /watchlist
관심 종목 추가
```json
{ "ticker": "AAPL", "market": "US", "alertThreshold": 75 }
```

### DELETE /watchlist/{ticker}
관심 종목 제거

---

## 사용자 프리셋 API

### GET /presets
사용자의 스크리닝 프리셋 목록

### POST /presets
새 프리셋 생성
```json
{
  "presetName": "가치투자 중심",
  "enabledCriteria": ["pe_ratio_vs_sector", "pb_ratio_vs_sector"],
  "weightOverrides": { "pe_ratio_vs_sector": 2.0 },
  "minScore": 60
}
```

### PUT /presets/{presetId}
프리셋 수정

### DELETE /presets/{presetId}
프리셋 삭제

---

## 섹터 API

### GET /sectors
시장별 섹터 목록 및 벤치마크

**Query Parameters**: `market`

**Response 200**
```json
{
  "market": "US",
  "sectors": [
    {
      "sector": "Technology",
      "stockCount": 523,
      "benchmarks": {
        "medianPe": 24.1,
        "medianPb": 4.8,
        "medianRoe": 15.2
      }
    }
  ]
}
```

---

## 에러 응답 형식

```json
{
  "error": {
    "code": "STOCK_NOT_FOUND",
    "message": "종목을 찾을 수 없습니다: INVALID",
    "statusCode": 404
  }
}
```

## 에러 코드

| 코드 | HTTP | 설명 |
|---|---|---|
| `UNAUTHORIZED` | 401 | 인증 토큰 없음/만료 |
| `FORBIDDEN` | 403 | 권한 없음 (프리미엄 기능) |
| `STOCK_NOT_FOUND` | 404 | 종목 미존재 |
| `RATE_LIMIT_EXCEEDED` | 429 | 요청 한도 초과 |
| `SCREENING_NOT_READY` | 503 | 스크리닝 진행 중 |
