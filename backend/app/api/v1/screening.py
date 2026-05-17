"""API endpoints for stock screening."""

from datetime import datetime
from decimal import Decimal

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select, desc, and_, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db_session
from app.models import ScreeningResult, CriteriaScore, Stock
from app.schemas import (
    ScreeningResultResponse,
    ScreeningListResponse,
    ScreeningRequest,
    CriteriaScoreResponse,
)
from app.core.screening import ScreeningEngine, CriteriaRegistry

router = APIRouter(prefix="/screening", tags=["screening"])


@router.get("/results", response_model=ScreeningListResponse)
async def list_screening_results(
    db: AsyncSession = Depends(get_db_session),
    market: str = Query("US", description="Filter by market"),
    min_score: Decimal = Query(0, ge=0, le=1),
    undervalued_only: bool = Query(False),
    limit: int = Query(100, ge=1, le=1000),
    offset: int = Query(0, ge=0),
) -> ScreeningListResponse:
    """List latest screening results.

    - **market**: Filter by market (US, KR)
    - **min_score**: Minimum composite score
    - **undervalued_only**: Only undervalued stocks
    - **limit**: Maximum results
    - **offset**: Pagination offset
    """
    query = select(ScreeningResult).where(ScreeningResult.market == market.upper())

    if min_score > 0:
        query = query.where(ScreeningResult.total_score >= min_score)

    if undervalued_only:
        query = query.where(ScreeningResult.is_undervalued == True)

    # Order by score descending
    query = query.order_by(desc(ScreeningResult.total_score))

    # Get total count
    count_query = select(ScreeningResult).where(ScreeningResult.market == market.upper())
    if min_score > 0:
        count_query = count_query.where(ScreeningResult.total_score >= min_score)
    if undervalued_only:
        count_query = count_query.where(ScreeningResult.is_undervalued == True)

    count_result = await db.execute(select(func.count()).select_from(ScreeningResult).where(*count_query.whereclause.clauses))
    total = count_result.scalar() or 0

    # Fetch results
    result = await db.execute(query.offset(offset).limit(limit))
    results = result.scalars().all()

    # Populate criteria scores
    items = []
    for screening_result in results:
        # Fetch criteria scores
        criteria_result = await db.execute(
            select(CriteriaScore).where(
                CriteriaScore.screening_result_id == screening_result.id
            )
        )
        criteria_scores = criteria_result.scalars().all()

        # Convert to response
        sr_response = ScreeningResultResponse.model_validate(screening_result)
        sr_response.criteria_scores = [
            CriteriaScoreResponse.model_validate(cs) for cs in criteria_scores
        ]
        items.append(sr_response)

    return ScreeningListResponse(
        items=items,
        total=total,
        limit=limit,
        offset=offset,
        timestamp=datetime.utcnow(),
    )


@router.get("/results/{screening_id}", response_model=ScreeningResultResponse)
async def get_screening_result(
    screening_id: int,
    db: AsyncSession = Depends(get_db_session),
) -> ScreeningResultResponse:
    """Get a specific screening result with all criterion scores."""
    result = await db.execute(
        select(ScreeningResult).where(ScreeningResult.id == screening_id)
    )
    screening = result.scalars().first()

    if not screening:
        raise HTTPException(status_code=404, detail="Screening result not found")

    # Fetch criteria scores
    criteria_result = await db.execute(
        select(CriteriaScore).where(
            CriteriaScore.screening_result_id == screening_id
        )
    )
    criteria_scores = criteria_result.scalars().all()

    response = ScreeningResultResponse.model_validate(screening)
    response.criteria_scores = [
        CriteriaScoreResponse.model_validate(cs) for cs in criteria_scores
    ]

    return response


@router.get("/stock/{stock_id}/latest", response_model=ScreeningResultResponse | None)
async def get_stock_latest_screening(
    stock_id: int,
    db: AsyncSession = Depends(get_db_session),
) -> ScreeningResultResponse | None:
    """Get the latest screening result for a specific stock."""
    result = await db.execute(
        select(ScreeningResult)
        .where(ScreeningResult.stock_id == stock_id)
        .order_by(desc(ScreeningResult.screened_at))
        .limit(1)
    )
    screening = result.scalars().first()

    if not screening:
        return None

    # Fetch criteria scores
    criteria_result = await db.execute(
        select(CriteriaScore).where(
            CriteriaScore.screening_result_id == screening.id
        )
    )
    criteria_scores = criteria_result.scalars().all()

    response = ScreeningResultResponse.model_validate(screening)
    response.criteria_scores = [
        CriteriaScoreResponse.model_validate(cs) for cs in criteria_scores
    ]

    return response


@router.get("/criteria", response_model=dict)
async def list_criteria() -> dict:
    """List all available screening criteria."""
    registry = CriteriaRegistry()
    all_criteria = registry.get_all()

    criteria_by_category = {}
    for criteria_id, criteria in all_criteria.items():
        if criteria.category not in criteria_by_category:
            criteria_by_category[criteria.category] = []

        criteria_by_category[criteria.category].append({
            "criteria_id": criteria_id,
            "name": criteria.name,
            "description": criteria.description,
            "default_weight": float(criteria.default_weight),
            "category": criteria.category,
        })

    return {
        "total": len(all_criteria),
        "categories": criteria_by_category,
    }
