import logging
from dataclasses import asdict
from datetime import date, datetime
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.tasks.celery_app import celery_app
from app.database import AsyncSessionLocal
from app.models.stock import Stock
from app.models.financial import RawFinancial, FinancialMetric
from app.data.providers.yahoo_finance import YahooFinanceProvider
from app.data.providers.base import RawStockData

logger = logging.getLogger(__name__)


def _compute_metrics(raw: RawStockData, today: date) -> FinancialMetric:
    """RawStockData로부터 FinancialMetric 계산"""
    roe = (raw.net_income / raw.total_equity * 100) if raw.net_income and raw.total_equity else None
    roa = (raw.net_income / raw.total_assets * 100) if raw.net_income and raw.total_assets else None
    net_margin = (raw.net_income / raw.revenue * 100) if raw.net_income and raw.revenue else None
    gross_margin = None
    operating_margin = (raw.operating_income / raw.revenue * 100) if raw.operating_income and raw.revenue else None
    current_ratio = (raw.current_assets / raw.current_liabilities) if raw.current_assets and raw.current_liabilities else None
    quick_ratio = ((raw.current_assets * 0.67) / raw.current_liabilities) if raw.current_assets and raw.current_liabilities else None
    debt_to_equity = (raw.total_liabilities / raw.total_equity) if raw.total_liabilities and raw.total_equity else None

    return FinancialMetric(
        pe_ratio=raw.pe_ratio,
        pb_ratio=raw.pb_ratio,
        ps_ratio=raw.ps_ratio,
        roe=roe,
        roa=roa,
        net_margin=net_margin,
        gross_margin=gross_margin,
        operating_margin=operating_margin,
        current_ratio=current_ratio,
        quick_ratio=quick_ratio,
        debt_to_equity=debt_to_equity,
        data_as_of=today,
    )


async def _upsert_stock(session: AsyncSession, raw: RawStockData) -> Stock:
    result = await session.execute(
        select(Stock).where(Stock.ticker == raw.ticker, Stock.market == raw.market)
    )
    stock = result.scalars().first()
    if not stock:
        stock = Stock(
            ticker=raw.ticker,
            market=raw.market,
            exchange="NYSE" if raw.market == "US" else "KRX",
            company_name=raw.company_name,
            sector=raw.sector,
            currency="USD" if raw.market == "US" else "KRW",
            is_active=True,
        )
        session.add(stock)
        await session.flush()
    return stock


async def _fetch_and_save_us_market():
    """US 시장 데이터 수집 및 저장"""
    provider = YahooFinanceProvider()
    today = date.today()

    async with AsyncSessionLocal() as session:
        async for raw in provider.fetch_all_stocks():
            try:
                stock = await _upsert_stock(session, raw)

                raw_record = RawFinancial(
                    stock_id=stock.id,
                    source="yfinance",
                    raw_json={k: v for k, v in asdict(raw).items() if v is not None},
                    fetched_at=datetime.utcnow(),
                    data_as_of=today,
                )
                session.add(raw_record)

                metrics = _compute_metrics(raw, today)
                metrics.stock_id = stock.id
                session.add(metrics)

                await session.commit()
                logger.info(f"Saved data for {raw.ticker}")
            except Exception as e:
                await session.rollback()
                logger.error(f"Error processing {raw.ticker}: {e}")


async def _fetch_and_save_kr_market():
    """KR 시장 Mock 데이터 저장"""
    kr_tickers = [
        ("005930", "삼성전자", "Technology"),
        ("000660", "SK하이닉스", "Technology"),
        ("207940", "삼성바이오로직스", "Healthcare"),
        ("051910", "LG화학", "Materials"),
        ("096770", "SK이노베이션", "Energy"),
    ]
    today = date.today()

    async with AsyncSessionLocal() as session:
        for ticker, company_name, sector in kr_tickers:
            try:
                from app.data.providers.base import RawStockData as RS
                raw = RS(
                    ticker=ticker,
                    market="KR",
                    company_name=company_name,
                    sector=sector,
                    current_price=50000.0,
                    pe_ratio=15.0,
                    pb_ratio=1.2,
                    ps_ratio=0.8,
                    revenue=1e11,
                    operating_income=1.5e10,
                    net_income=1.2e10,
                    ebitda=2e10,
                    total_assets=5e11,
                    total_liabilities=2e11,
                    total_equity=3e11,
                    current_assets=1.5e11,
                    current_liabilities=1e11,
                    cash=5e10,
                )
                stock = await _upsert_stock(session, raw)

                raw_record = RawFinancial(
                    stock_id=stock.id,
                    source="mock",
                    raw_json={k: v for k, v in asdict(raw).items() if v is not None},
                    fetched_at=datetime.utcnow(),
                    data_as_of=today,
                )
                session.add(raw_record)

                metrics = _compute_metrics(raw, today)
                metrics.stock_id = stock.id
                session.add(metrics)

                await session.commit()
                logger.info(f"Saved mock data for {ticker}")
            except Exception as e:
                await session.rollback()
                logger.error(f"Error processing {ticker}: {e}")


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
