"""API endpoints for stocks."""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db_session
from app.models import Stock, FinancialMetric
from app.schemas import StockResponse, StockListResponse, FinancialMetricResponse

router = APIRouter(prefix="/stocks", tags=["stocks"])


@router.get("", response_model=StockListResponse)
async def list_stocks(
    db: AsyncSession = Depends(get_db_session),
    market: str = Query("US", description="Filter by market"),
    sector: str | None = Query(None, description="Filter by sector"),
    active_only: bool = Query(True, description="Only active stocks"),
    limit: int = Query(100, ge=1, le=1000),
    offset: int = Query(0, ge=0),
) -> StockListResponse:
    """List stocks with optional filtering.

    - **market**: Filter by market (US, KR)
    - **sector**: Filter by industry sector
    - **active_only**: Only include actively traded stocks
    - **limit**: Maximum results (max 1000)
    - **offset**: Pagination offset
    """
    # Build base query
    base_query = select(Stock)

    if active_only:
        base_query = base_query.where(Stock.is_active == True)

    if market:
        base_query = base_query.where(Stock.market == market.upper())

    if sector:
        base_query = base_query.where(Stock.sector == sector)

    # Get total count
    count_query = select(func.count()).select_from(Stock)
    if base_query.whereclause is not None:
        count_query = count_query.where(base_query.whereclause)
    count_result = await db.execute(count_query)
    total = count_result.scalar() or 0

    # Execute with pagination
    result = await db.execute(base_query.offset(offset).limit(limit))
    stocks = result.scalars().all()

    return StockListResponse(
        items=[StockResponse.model_validate(s) for s in stocks],
        total=total,
        limit=limit,
        offset=offset,
    )


@router.get("/{stock_id}", response_model=StockResponse)
async def get_stock(
    stock_id: int,
    db: AsyncSession = Depends(get_db_session),
) -> StockResponse:
    """Get a specific stock by ID."""
    result = await db.execute(select(Stock).where(Stock.id == stock_id))
    stock = result.scalars().first()

    if not stock:
        raise HTTPException(status_code=404, detail="Stock not found")

    return StockResponse.model_validate(stock)


@router.get("/{stock_id}/metrics", response_model=FinancialMetricResponse | None)
async def get_stock_metrics(
    stock_id: int,
    db: AsyncSession = Depends(get_db_session),
) -> FinancialMetricResponse | None:
    """Get latest financial metrics for a stock."""
    result = await db.execute(
        select(FinancialMetric)
        .where(FinancialMetric.stock_id == stock_id)
        .order_by(FinancialMetric.data_as_of.desc())
        .limit(1)
    )
    metric = result.scalars().first()

    if not metric:
        return None

    return FinancialMetricResponse.model_validate(metric)


@router.get("/search/{ticker}", response_model=StockListResponse)
async def search_stocks(
    ticker: str,
    db: AsyncSession = Depends(get_db_session),
    market: str | None = Query(None),
) -> StockListResponse:
    """Search stocks by ticker symbol."""
    query = select(Stock).where(Stock.ticker.ilike(f"%{ticker}%"))

    if market:
        query = query.where(Stock.market == market.upper())

    result = await db.execute(query.limit(20))
    stocks = result.scalars().all()

    return StockListResponse(
        items=[StockResponse.model_validate(s) for s in stocks],
        total=len(stocks),
        limit=20,
        offset=0,
    )
