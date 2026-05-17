# 프론트엔드 설계

## 모노레포 구조

```
frontend/
├── apps/
│   ├── web/               # Next.js 15 웹 앱
│   │   ├── app/           # App Router
│   │   │   ├── (auth)/
│   │   │   │   ├── login/
│   │   │   │   └── register/
│   │   │   ├── dashboard/
│   │   │   ├── screener/
│   │   │   │   ├── page.tsx          # 스크리너 메인
│   │   │   │   └── [ticker]/
│   │   │   │       └── page.tsx      # 종목 상세
│   │   │   └── watchlist/
│   │   ├── lib/
│   │   └── next.config.ts
│   │
│   └── mobile/            # React Native (Expo)
│       ├── app/           # Expo Router
│       │   ├── (tabs)/
│       │   │   ├── index.tsx         # 대시보드
│       │   │   ├── screener.tsx      # 스크리너
│       │   │   └── watchlist.tsx     # 관심 종목
│       │   └── stock/[ticker].tsx    # 종목 상세
│       └── app.json
│
└── packages/
    ├── ui/                # 공통 UI 컴포넌트 (웹/앱 모두 사용)
    │   ├── components/
    │   │   ├── StockCard/
    │   │   ├── ScoreGauge/
    │   │   ├── CriteriaBreakdown/
    │   │   ├── MarketBadge/
    │   │   └── FilterPanel/
    │   └── package.json
    │
    ├── api-client/        # 공통 API 클라이언트 (타입 공유)
    │   ├── client.ts
    │   ├── types/
    │   │   ├── stock.ts
    │   │   └── screening.ts
    │   └── package.json
    │
    └── utils/             # 공통 유틸
        ├── formatters.ts  # 숫자/통화 포맷
        ├── market.ts      # 시장 관련 헬퍼
        └── package.json
```

## 주요 화면 구성

### 1. 스크리너 메인 페이지

```
┌─────────────────────────────────────────────────────────┐
│  Stock Screener                         [KR] [US]        │
├─────────────────────────────────────────────────────────┤
│  필터 패널                                               │
│  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐   │
│  │ 섹터 전체 │ │ 시총 전체 │ │ PER 기준 │ │ 정렬 기준│   │
│  └──────────┘ └──────────┘ └──────────┘ └──────────┘   │
├─────────────────────────────────────────────────────────┤
│  종목 목록 (저평가 점수 내림차순)                          │
│                                                          │
│  ┌─────────────────────────────────────────────────┐    │
│  │ ● AAPL  Apple Inc.                [US] [Tech]   │    │
│  │   저평가 점수: ████████░░ 82점                   │    │
│  │   PER 14.2 (섹터 평균 24.1 대비 41% 저평가)      │    │
│  │   PBR 2.1  ROE 28%  부채비율 45%                 │    │
│  └─────────────────────────────────────────────────┘    │
│  ┌─────────────────────────────────────────────────┐    │
│  │ ● 005930  삼성전자           [KR] [반도체]        │    │
│  │   저평가 점수: ███████░░░ 71점                   │    │
│  │   PER 10.2 (섹터 평균 18.5 대비 45% 저평가)      │    │
│  └─────────────────────────────────────────────────┘    │
│  ...                                                     │
└─────────────────────────────────────────────────────────┘
```

### 2. 종목 상세 페이지

```
┌─────────────────────────────────────────────────────────┐
│  ← AAPL — Apple Inc.                      [관심종목 +]   │
├────────────────────────┬────────────────────────────────┤
│  저평가 종합 점수       │  가격 정보                       │
│                        │                                 │
│      82 / 100          │  $185.20  ▲ +1.2%              │
│   ████████░░           │  시총: $2.87T                   │
│   매우 저평가           │  52주: $124 ~ $199              │
├────────────────────────┴────────────────────────────────┤
│  기준별 분석                                             │
│                                                          │
│  [밸류에이션]                                             │
│  • PER vs 섹터    ████████░░  85점  PER 14.2 (섹터 24.1)│
│  • PBR vs 섹터    ██████░░░░  62점  PBR 2.1 (섹터 4.8)  │
│  • EV/EBITDA      ████████░░  80점  8.2 (섹터 15.3)     │
│                                                          │
│  [수익성]                                                │
│  • ROE            █████████░  92점  28.4%               │
│  • 영업이익률      ████████░░  80점  30.1%               │
│                                                          │
│  [재무건전성]                                             │
│  • 부채비율        ███████░░░  72점  45%                 │
│  • 유동비율        ████████░░  82점  1.5                 │
├─────────────────────────────────────────────────────────┤
│  재무 추이 (5년)          주가 차트                       │
└─────────────────────────────────────────────────────────┘
```

## 상태 관리

```typescript
// packages/api-client/types/screening.ts

export interface ScreeningResult {
  ticker: string;
  market: "US" | "KR";
  companyName: string;
  sector: string;
  totalScore: number;           // 0~100
  isUndervalued: boolean;
  criteriaDetails: CriteriaDetail[];
  screenedAt: string;           // ISO 8601
}

export interface CriteriaDetail {
  criteriaId: string;
  name: string;
  category: CriteriaCategory;
  score: number;                // 0~100
  rawValue: number;
  benchmark: number;
  isUndervalued: boolean;
  reason: string;
}

export type CriteriaCategory =
  | "valuation"
  | "profitability"
  | "growth"
  | "financial_health"
  | "momentum";
```

### 상태 관리 전략

| 상태 유형 | 도구 | 이유 |
|---|---|---|
| 서버 데이터 (스크리닝 결과 등) | TanStack Query | 캐싱·재검증 자동화 |
| UI 상태 (필터, 모달 등) | Zustand (웹) / Jotai (앱) | 경량, 보일러플레이트 없음 |
| 인증 상태 | Zustand + localStorage | 영속성 필요 |

## 필터 패널 설계

필터는 URL 쿼리 파라미터로 직렬화 → 공유 가능한 URL 생성

```typescript
interface ScreenerFilters {
  market: "US" | "KR" | "ALL";
  sector?: string[];
  marketCapMin?: number;
  marketCapMax?: number;
  minScore?: number;             // 최소 저평가 점수
  enabledCriteria?: string[];   // 활성화할 기준 ID 목록
  sortBy: "totalScore" | "pe" | "pb" | "roe";
  sortOrder: "asc" | "desc";
  page: number;
  pageSize: 20 | 50 | 100;
}
```

## 모바일 앱 특화 기능

- **푸시 알림**: 관심 종목이 특정 점수 이상이 되면 알림
- **위젯**: iOS/Android 홈 화면 위젯으로 Top 3 저평가 종목 표시
- **오프라인**: 마지막 스크리닝 결과 로컬 캐시 (SQLite via MMKV)

## 성능 전략

| 항목 | 전략 |
|---|---|
| 초기 로딩 | Next.js SSR + ISR (스크리닝 결과 1시간 캐시) |
| 목록 렌더링 | 가상 스크롤 (react-virtual) |
| API 요청 | TanStack Query staleTime 5분 |
| 이미지 | Next.js Image 컴포넌트 자동 최적화 |
