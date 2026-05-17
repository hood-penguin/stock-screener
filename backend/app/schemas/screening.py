"""Pydantic schemas for screening-related API responses."""

from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, Field


class CriteriaScoreResponse(BaseModel):
    """Score for a single screening criterion."""

    criteria_id: str
    score: Decimal = Field(..., ge=0, le=1, description="Score from 0 to 1")
    raw_value: Decimal | None = Field(None, description="Actual metric value")
    benchmark_value: Decimal | None = Field(None, description="Benchmark or sector median")
    is_undervalued: bool | None = Field(None, description="Whether undervalued by this criterion")
    reason: str | None = Field(None, description="Explanation of the score")

    class Config:
        from_attributes = True


class ScreeningResultResponse(BaseModel):
    """Complete screening result for a stock."""

    id: int
    stock_id: int
    market: str
    total_score: Decimal = Field(..., ge=0, le=1, description="Composite score from 0 to 1")
    is_undervalued: bool = Field(..., description="Whether stock is undervalued overall")
    metrics_date: datetime
    screened_at: datetime
    criteria_scores: list[CriteriaScoreResponse] = Field(default_factory=list)

    class Config:
        from_attributes = True


class ScreeningRequest(BaseModel):
    """Request to screen stocks."""

    market: str = Field("US", description="Market to screen (US, KR)")
    enabled_criteria: dict[str, bool] = Field(
        default_factory=dict,
        description="Override which criteria to use (criteria_id -> bool)"
    )
    weight_overrides: dict[str, Decimal] = Field(
        default_factory=dict,
        description="Override criterion weights (criteria_id -> weight)"
    )
    limit: int = Field(100, ge=1, le=1000, description="Max results to return")
    offset: int = Field(0, ge=0, description="Pagination offset")
    min_score: Decimal | None = Field(None, ge=0, le=1, description="Minimum total score")


class ScreeningListResponse(BaseModel):
    """List of screening results with pagination."""

    items: list[ScreeningResultResponse]
    total: int
    limit: int
    offset: int
    timestamp: datetime
