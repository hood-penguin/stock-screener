import logging
from datetime import datetime, date
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.tasks.celery_app import celery_app
from app.database import AsyncSessionLocal
from app.models.stock import Stock
from app.models.financial import FinancialMetric
from app.models.screening_result import ScreeningResult, CriteriaScore
from app.core.screening.scorer import ScreeningEngine

logger = logging.getLogger(__name__)


async def _run_screening_for_market(market: str):
    """특정 시장에 대한 스크리닝 실행"""
    today = date.today()
    engine = ScreeningEngine()

    async with AsyncSessionLocal() as session:
        result = await session.execute(select(Stock).where(Stock.market == market))
        stocks = result.scalars().all()

        if not stocks:
            logger.warning(f"No stocks found for market {market}")
            return

        for stock in stocks:
            try:
                metrics_result = await session.execute(
                    select(FinancialMetric)
                    .where(FinancialMetric.stock_id == stock.id)
                    .order_by(FinancialMetric.data_as_of.desc())
                    .limit(1)
                )
                metrics = metrics_result.scalars().first()

                if not metrics:
                    logger.warning(f"No metrics for {stock.ticker}")
                    continue

                total_score, criteria_results = await engine.evaluate_stock(
                    stock_id=stock.id,
                    market=market,
                    financial_metric=metrics,
                    sector_benchmark=None,
                    db_session=session,
                )

                is_undervalued = engine.get_undervalued_stocks(criteria_results)
                score_pct = float(engine.score_to_percentage(total_score))

                screening_record = ScreeningResult(
                    stock_id=stock.id,
                    market=market,
                    total_score=score_pct,
                    is_undervalued=is_undervalued,
                    screened_at=datetime.utcnow(),
                    metrics_date=today,
                )
                session.add(screening_record)
                await session.flush()

                for cr in criteria_results:
                    session.add(CriteriaScore(
                        screening_result_id=screening_record.id,
                        criteria_id=cr.criteria_id,
                        score=float(cr.score),
                        raw_value=float(cr.raw_value) if cr.raw_value is not None else None,
                        benchmark_value=float(cr.benchmark_value) if cr.benchmark_value is not None else None,
                        is_undervalued=cr.is_undervalued,
                        reason=cr.reason,
                    ))

                await session.commit()
                logger.info(f"Screened {stock.ticker}: score={score_pct:.1f}")

            except Exception as e:
                await session.rollback()
                logger.error(f"Error screening {stock.ticker}: {e}")


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
