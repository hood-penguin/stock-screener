"""Frontend-facing screener API — includes stock info and uses frontend-compatible shapes."""

from datetime import datetime
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel
from sqlalchemy import select, desc, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db_session
from app.models import ScreeningResult, CriteriaScore, Stock

router = APIRouter(prefix="/screener", tags=["screener"])


class ScreenerResultItem(BaseModel):
    id: int
    stock_id: int
    ticker: str
    company_name: str
    sector: str | None
    market: str
    overall_score: float
    screened_at: datetime


class ScreenerListResponse(BaseModel):
    results: list[ScreenerResultItem]
    total: int
    page: int
    page_size: int
    total_pages: int


class CriteriaScoreDetail(BaseModel):
    id: int
    screening_result_id: int
    criterion_name: str
    score: float | None
    reason: str | None


class ScreenerDetailResponse(ScreenerResultItem):
    criteria_scores: list[CriteriaScoreDetail] = []


@router.get("/results", response_model=ScreenerListResponse)
async def get_screener_results(
    db: AsyncSession = Depends(get_db_session),
    market: Optional[str] = Query(None, description="Market to filter (US, KR); omit or ALL for all markets"),
    sector: Optional[str] = Query(None, description="Sector to filter (e.g. Technology, Financial Services)"),
    min_score: float = Query(0.0, ge=0, le=100),
    undervalued_only: bool = Query(False),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=200),
) -> ScreenerListResponse:
    """List latest screening results per stock with stock info included.

    market=ALL (or omitted) returns all markets.
    """
    # Subquery: latest screened_at per (stock_id, market) to deduplicate
    latest_sub = (
        select(
            ScreeningResult.stock_id,
            ScreeningResult.market,
            func.max(ScreeningResult.screened_at).label("max_screened_at"),
        )
        .group_by(ScreeningResult.stock_id, ScreeningResult.market)
        .subquery()
    )

    base_cond = [
        ScreeningResult.stock_id == latest_sub.c.stock_id,
        ScreeningResult.market == latest_sub.c.market,
        ScreeningResult.screened_at == latest_sub.c.max_screened_at,
    ]

    market_upper = (market or "ALL").upper()
    if market_upper not in ("ALL", ""):
        base_cond.append(ScreeningResult.market == market_upper)

    if sector:
        base_cond.append(Stock.sector == sector)

    if min_score > 0:
        base_cond.append(ScreeningResult.total_score >= min_score)
    if undervalued_only:
        base_cond.append(ScreeningResult.is_undervalued == True)  # noqa: E712

    count_stmt = (
        select(func.count(ScreeningResult.id))
        .join(latest_sub, (ScreeningResult.stock_id == latest_sub.c.stock_id) &
              (ScreeningResult.market == latest_sub.c.market) &
              (ScreeningResult.screened_at == latest_sub.c.max_screened_at))
        .join(Stock, Stock.id == ScreeningResult.stock_id)
        .where(*base_cond)
    )
    total = (await db.execute(count_stmt)).scalar() or 0

    offset = (page - 1) * page_size
    stmt = (
        select(ScreeningResult, Stock)
        .join(latest_sub, (ScreeningResult.stock_id == latest_sub.c.stock_id) &
              (ScreeningResult.market == latest_sub.c.market) &
              (ScreeningResult.screened_at == latest_sub.c.max_screened_at))
        .join(Stock, Stock.id == ScreeningResult.stock_id)
        .where(*base_cond)
        .order_by(desc(ScreeningResult.total_score))
        .offset(offset)
        .limit(page_size)
    )
    rows = (await db.execute(stmt)).all()

    results = [
        ScreenerResultItem(
            id=sr.id,
            stock_id=sr.stock_id,
            ticker=stock.ticker,
            company_name=stock.company_name,
            sector=stock.sector,
            market=sr.market,
            overall_score=float(sr.total_score),
            screened_at=sr.screened_at,
        )
        for sr, stock in rows
    ]

    total_pages = max(1, (total + page_size - 1) // page_size)

    return ScreenerListResponse(
        results=results,
        total=total,
        page=page,
        page_size=page_size,
        total_pages=total_pages,
    )


@router.get("/results/{ticker}", response_model=ScreenerDetailResponse)
async def get_screener_result_by_ticker(
    ticker: str,
    db: AsyncSession = Depends(get_db_session),
) -> ScreenerDetailResponse:
    """Get latest screening result for a stock by ticker."""
    stock_result = await db.execute(
        select(Stock).where(Stock.ticker == ticker.upper())
    )
    stock = stock_result.scalars().first()
    if not stock:
        raise HTTPException(status_code=404, detail=f"Stock {ticker} not found")

    sr_result = await db.execute(
        select(ScreeningResult)
        .where(ScreeningResult.stock_id == stock.id)
        .order_by(desc(ScreeningResult.screened_at))
        .limit(1)
    )
    sr = sr_result.scalars().first()
    if not sr:
        raise HTTPException(status_code=404, detail=f"No screening result for {ticker}")

    cs_result = await db.execute(
        select(CriteriaScore).where(CriteriaScore.screening_result_id == sr.id)
    )
    criteria_scores = [
        CriteriaScoreDetail(
            id=cs.id,
            screening_result_id=cs.screening_result_id,
            criterion_name=cs.criteria_id,
            score=round(float(cs.score) * 100, 1) if cs.score is not None else None,
            reason=cs.reason,
        )
        for cs in cs_result.scalars().all()
    ]

    return ScreenerDetailResponse(
        id=sr.id,
        stock_id=sr.stock_id,
        ticker=stock.ticker,
        company_name=stock.company_name,
        sector=stock.sector,
        market=sr.market,
        overall_score=float(sr.total_score),
        screened_at=sr.screened_at,
        criteria_scores=criteria_scores,
    )
