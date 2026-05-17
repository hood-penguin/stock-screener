# 저평가 주식 탐색 서비스 (Stock Screener) — 설계 문서

> 미국·한국 주식 시장에서 저평가 종목을 자동 발굴하는 풀스택 서비스

## 목차

| 문서 | 설명 |
|---|---|
| [시스템 아키텍처](./architecture/system-overview.md) | 전체 시스템 구성도, 컴포넌트 관계 |
| [백엔드 설계](./architecture/backend-design.md) | API 서버, 스크리닝 엔진, 데이터 파이프라인 |
| [프론트엔드 설계](./architecture/frontend-design.md) | 웹/앱 공통 컴포넌트, 화면 구조 |
| [데이터 파이프라인](./architecture/data-pipeline.md) | 시장 데이터 수집·정제 흐름 |
| [API 명세](./api/api-spec.md) | REST API 엔드포인트 전체 정의 |
| [DB 스키마](./database/schema.md) | 테이블 구조 및 인덱스 전략 |
| [스크리닝 엔진](./screening/screening-engine.md) | 플러그인 아키텍처, 기준 추가 가이드 |
| [인프라](./infrastructure/infra.md) | 배포 구성, 컨테이너, 환경 분리 |

## 핵심 설계 원칙

1. **확장성 우선**: 스크리닝 기준을 코드 변경 없이 플러그인으로 추가
2. **멀티마켓 추상화**: US/KR 시장을 동일 인터페이스로 처리
3. **Web + App 코드 공유**: React Native + Next.js 모노레포
4. **데이터 무결성**: 원시 데이터 보존 → 계산값 분리 저장

## 빠른 기술 스택 요약

```
Backend   : FastAPI (Python 3.12) + Celery + Redis
Database  : PostgreSQL 16 + Redis (캐시/큐)
Web       : Next.js 15 (TypeScript)
App       : React Native 0.74 (Expo)
공통 UI   : 모노레포 내 shared-ui 패키지
Data (US) : Polygon.io / Yahoo Finance
Data (KR) : 한국투자증권 OpenAPI / DART 전자공시
Infra     : Docker Compose (개발) / AWS ECS Fargate (운영)
```
