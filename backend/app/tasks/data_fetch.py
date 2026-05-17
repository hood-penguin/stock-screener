import logging
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from datetime import datetime

from app.tasks.celery_app import celery_app
from app.database import AsyncSessionLocal
from app.models.stock import Stock, RawStockData, FinancialMetrics
from app.data.providers.yahoo_finance import YahooFinanceProvider
from app.core.screening.market import get_market_engine

logger = logging.getLogger(__name__)


async def _fetch_and_save_us_market():
    """US 시장 데이터 수집 및 저장 (async 버전)"""
    provider = YahooFinanceProvider()
    session: AsyncSession = AsyncSessionLocal()

    try:
        async for raw_data in provider.fetch_all_stocks():
            try:
                # 기존 Stock 확인
                result = await session.execute(
                    select(Stock).where(Stock.ticker == raw_data.ticker)
                )
                stock = result.scalars().first()

                if not stock:
                    stock = Stock(
                        ticker=raw_data.ticker,
                        market="US",
                        company_name=raw_data.company_name,
                        sector=raw_data.sector,
                    )
                    session.add(stock)
                    await session.flush()

                # RawStockData 저장
                raw_record = RawStockData(
                    stock_id=stock.id,
                    current_price=raw_data.current_price,
                    pe_ratio=raw_data.pe_ratio,
                    pb_ratio=raw_data.pb_ratio,
                    ps_ratio=raw_data.ps_ratio,
                    revenue=raw_data.revenue,
                    operating_income=raw_data.operating_income,
                    net_income=raw_data.net_income,
                    ebitda=raw_data.ebitda,
                    total_assets=raw_data.total_assets,
                    total_liabilities=raw_data.total_liabilities,
                    total_equity=raw_data.total_equity,
                    current_assets=raw_data.current_assets,
                    current_liabilities=raw_data.current_liabilities,
                    cash=raw_data.cash,
                    eps=raw_data.eps,
                    book_value_per_share=raw_data.book_value_per_share,
                    fetched_at=datetime.utcnow(),
                )
                session.add(raw_record)

                # FinancialMetrics 계산 및 저장
                if raw_data.net_income and raw_data.total_equity:
                    roe = (raw_data.net_income / raw_data.total_equity) * 100
                else:
                    roe = None

                if raw_data.net_income and raw_data.revenue:
                    net_margin = (raw_data.net_income / raw_data.revenue) * 100
                else:
                    net_margin = None

                if raw_data.revenue and raw_data.total_assets:
                    roa = (raw_data.net_income / raw_data.total_assets) * 100 \
                        if raw_data.net_income else None
                else:
                    roa = None

                metrics = FinancialMetrics(
                    stock_id=stock.id,
                    roe=roe,
                    roa=roa,
                    net_margin=net_margin,
                    current_ratio=raw_data.current_assets / raw_data.current_liabilities
                    if raw_data.current_assets and raw_data.current_liabilities else None,
                    quick_ratio=(raw_data.current_assets - (raw_data.current_assets * 0.33))
                    / raw_data.current_liabilities
                    if raw_data.current_assets and raw_data.current_liabilities else None,
                    debt_to_equity=raw_data.total_liabilities / raw_data.total_equity
                    if raw_data.total_liabilities and raw_data.total_equity else None,
                    interest_coverage=raw_data.operating_income / 0.01
                    if raw_data.operating_income else None,
                    calculated_at=datetime.utcnow(),
                )
                session.add(metrics)

                await session.commit()
                logger.info(f"Saved data for {raw_data.ticker}")

            except Exception as e:
                await session.rollback()
                logger.error(f"Error processing {raw_data.ticker}: {str(e)}")
                continue

    finally:
        await session.close()


async def _fetch_and_save_kr_market():
    """KR 시장 데이터 수집 및 저장 (async 버전)"""
    session: AsyncSession = AsyncSessionLocal()

    try:
        # 주요 KR 종목
        kr_tickers = [
            ("005930", "삼성전자"),
            ("000660", "SK하이닉스"),
            ("207940", "삼성바이오로직스"),
            ("051910", "LG화학"),
            ("096770", "SK이노베이션"),
        ]

        for ticker, company_name in kr_tickers:
            try:
                # 기존 Stock 확인
                result = await session.execute(
                    select(Stock).where(Stock.ticker == ticker)
                )
                stock = result.scalars().first()

                if not stock:
                    stock = Stock(
                        ticker=ticker,
                        market="KR",
                        company_name=company_name,
                        sector="Manufacturing",
                    )
                    session.add(stock)
                    await session.flush()

                # Mock 데이터 저장 (실제 API 없음)
                raw_record = RawStockData(
                    stock_id=stock.id,
                    current_price=50000.0,  # Mock
                    pe_ratio=15.0,
                    pb_ratio=1.2,
                    ps_ratio=0.8,
                    revenue=100000000000.0,
                    operating_income=15000000000.0,
                    net_income=12000000000.0,
                    ebitda=20000000000.0,
                    total_assets=500000000000.0,
                    total_liabilities=200000000000.0,
                    total_equity=300000000000.0,
                    current_assets=150000000000.0,
                    current_liabilities=100000000000.0,
                    cash=50000000000.0,
                    fetched_at=datetime.utcnow(),
                )
                session.add(raw_record)

                metrics = FinancialMetrics(
                    stock_id=stock.id,
                    roe=4.0,
                    roa=2.4,
                    net_margin=12.0,
                    current_ratio=1.5,
                    quick_ratio=1.2,
                    debt_to_equity=0.667,
                    interest_coverage=15.0,
                    calculated_at=datetime.utcnow(),
                )
                session.add(metrics)

                await session.commit()
                logger.info(f"Saved mock data for {ticker}")

            except Exception as e:
                await session.rollback()
                logger.error(f"Error processing {ticker}: {str(e)}")
                continue

    finally:
        await session.close()


@celery_app.task(bind=True, max_retries=3, default_retry_delay=300)
def fetch_us_market(self):
    """US 시장 데이터 수집 Celery 태스크"""
    try:
        import asyncio
        asyncio.run(_fetch_and_save_us_market())
        logger.info("US market fetch completed")
    except Exception as e:
        logger.error(f"Error in fetch_us_market: {str(e)}")
        raise self.retry(exc=e)


@celery_app.task(bind=True, max_retries=3, default_retry_delay=300)
def fetch_kr_market(self):
    """KR 시장 데이터 수집 Celery 태스크"""
    try:
        import asyncio
        asyncio.run(_fetch_and_save_kr_market())
        logger.info("KR market fetch completed")
    except Exception as e:
        logger.error(f"Error in fetch_kr_market: {str(e)}")
        raise self.retry(exc=e)
