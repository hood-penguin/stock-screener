import logging
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from datetime import datetime

from app.tasks.celery_app import celery_app
from app.database import AsyncSessionLocal, redis_client
from app.models.stock import Stock, FinancialMetrics
from app.models.screening_result import ScreeningResult, CriteriaScore
from app.core.screening.engine import ScreeningEngine

logger = logging.getLogger(__name__)


async def _run_screening_for_market(market: str):
    """특정 시장에 대한 스크리닝 실행"""
    session: AsyncSession = AsyncSessionLocal()

    try:
        # 해당 시장의 모든 종목 로드
        result = await session.execute(
            select(Stock).where(Stock.market == market)
        )
        stocks = result.scalars().all()

        if not stocks:
            logger.warning(f"No stocks found for market {market}")
            return

        # 스크리닝 엔진 초기화
        engine = ScreeningEngine()

        # 각 종목 스크리닝
        screening_results = []

        for stock in stocks:
            try:
                # 최신 재무 지표 로드
                metrics_result = await session.execute(
                    select(FinancialMetrics)
                    .where(FinancialMetrics.stock_id == stock.id)
                    .order_by(FinancialMetrics.calculated_at.desc())
                    .limit(1)
                )
                metrics = metrics_result.scalars().first()

                if not metrics:
                    logger.warning(f"No metrics for {stock.ticker}")
                    continue

                # 스크리닝 실행
                score, criteria_results = engine.run(
                    ticker=stock.ticker,
                    company_name=stock.company_name,
                    sector=stock.sector,
                    market=stock.market,
                    metrics={
                        "pe_ratio": None,  # metrics에서 추출 필요
                        "pb_ratio": None,
                        "roe": metrics.roe,
                        "roa": metrics.roa,
                        "net_margin": metrics.net_margin,
                        "current_ratio": metrics.current_ratio,
                        "quick_ratio": metrics.quick_ratio,
                        "debt_to_equity": metrics.debt_to_equity,
                        "interest_coverage": metrics.interest_coverage,
                    },
                )

                # ScreeningResult 생성
                screening_record = ScreeningResult(
                    stock_id=stock.id,
                    market=market,
                    overall_score=score,
                    screened_at=datetime.utcnow(),
                )
                session.add(screening_record)
                await session.flush()

                # CriteriaScore 저장
                for criterion_name, criterion_data in criteria_results.items():
                    criterion_score = CriteriaScore(
                        screening_result_id=screening_record.id,
                        criterion_name=criterion_name,
                        score=criterion_data.get("score"),
                        reason=criterion_data.get("reason"),
                    )
                    session.add(criterion_score)

                screening_results.append(
                    {
                        "ticker": stock.ticker,
                        "score": score,
                    }
                )

                await session.commit()
                logger.info(f"Screened {stock.ticker}: score={score}")

            except Exception as e:
                await session.rollback()
                logger.error(f"Error screening {stock.ticker}: {str(e)}")
                continue

        # Redis 캐시 갱신
        if redis_client:
            cache_key = f"screening_results:{market}"
            # 점수 순으로 정렬
            screening_results.sort(key=lambda x: x["score"], reverse=True)
            try:
                import json
                await redis_client.setex(
                    cache_key,
                    3600,  # 1시간 TTL
                    json.dumps(screening_results),
                )
                logger.info(f"Updated cache for {market}")
            except Exception as e:
                logger.error(f"Error updating cache: {str(e)}")

    finally:
        await session.close()


@celery_app.task(bind=True, max_retries=3)
def run_screening(self, market: str):
    """스크리닝 실행 Celery 태스크"""
    try:
        import asyncio
        asyncio.run(_run_screening_for_market(market))
        logger.info(f"Screening completed for {market}")
    except Exception as e:
        logger.error(f"Error in run_screening: {str(e)}")
        raise self.retry(exc=e)
