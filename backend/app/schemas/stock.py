"""Pydantic schemas for stock-related API responses."""

from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, Field


class StockBase(BaseModel):
    """Base stock information."""

    ticker: str = Field(..., min_length=1, max_length=20, description="Stock ticker symbol")
    market: str = Field(..., min_length=2, max_length=4, description="Market code (US, KR)")
    exchange: str = Field(..., description="Exchange name")
    company_name: str = Field(..., description="Company name in local language")
    company_name_en: str | None = Field(None, description="Company name in English")
    sector: str | None = Field(None, description="Industry sector")
    industry: str | None = Field(None, description="Industry classification")
    currency: str = Field(..., description="Currency code (USD, KRW)")
    is_active: bool = Field(True, description="Whether stock is actively traded")
    listed_at: datetime | None = Field(None, description="IPO date")


class StockResponse(StockBase):
    """Stock response from API."""

    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class StockListResponse(BaseModel):
    """List of stocks with pagination."""

    items: list[StockResponse]
    total: int
    limit: int
    offset: int


class FinancialMetricResponse(BaseModel):
    """Financial metrics for a stock."""

    id: int
    stock_id: int
    price: Decimal | None
    market_cap: Decimal | None
    pe_ratio: Decimal | None
    pb_ratio: Decimal | None
    ps_ratio: Decimal | None
    ev_ebitda: Decimal | None
    peg_ratio: Decimal | None
    price_to_fcf: Decimal | None
    roe: Decimal | None
    roa: Decimal | None
    gross_margin: Decimal | None
    operating_margin: Decimal | None
    net_margin: Decimal | None
    revenue_growth_yoy: Decimal | None
    eps_growth_yoy: Decimal | None
    debt_to_equity: Decimal | None
    current_ratio: Decimal | None
    quick_ratio: Decimal | None
    interest_coverage: Decimal | None
    rsi_14: Decimal | None
    data_as_of: datetime
    calculated_at: datetime

    class Config:
        from_attributes = True
