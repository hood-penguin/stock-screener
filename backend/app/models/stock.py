"""Stock model - master data for stocks."""

from datetime import date
from typing import Optional

from sqlalchemy import Boolean, Index, String, UniqueConstraint, VARCHAR
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base, TimestampMixin


class Stock(Base, TimestampMixin):
    """Stock master data."""

    __tablename__ = "stocks"
    __table_args__ = (
        UniqueConstraint("ticker", "market", name="uq_stock_ticker_market"),
        Index("idx_stocks_market_sector", "market", "sector"),
        Index("idx_stocks_active", "is_active", postgresql_where="is_active = TRUE"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    ticker: Mapped[str] = mapped_column(VARCHAR(20), nullable=False)
    market: Mapped[str] = mapped_column(VARCHAR(4), nullable=False)  # 'US' or 'KR'
    exchange: Mapped[str] = mapped_column(VARCHAR(20), nullable=False)  # NYSE, NASDAQ, KOSPI, etc
    company_name: Mapped[str] = mapped_column(VARCHAR(200), nullable=False)
    company_name_en: Mapped[Optional[str]] = mapped_column(VARCHAR(200))
    sector: Mapped[Optional[str]] = mapped_column(VARCHAR(100))
    industry: Mapped[Optional[str]] = mapped_column(VARCHAR(100))
    currency: Mapped[str] = mapped_column(VARCHAR(4), default="USD", nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    listed_at: Mapped[Optional[date]] = mapped_column()

    # Relationships
    raw_financials = relationship(
        "RawFinancial", back_populates="stock", cascade="all, delete-orphan"
    )
    financial_metrics = relationship(
        "FinancialMetric", back_populates="stock", cascade="all, delete-orphan"
    )
    screening_results = relationship(
        "ScreeningResult", back_populates="stock", cascade="all, delete-orphan"
    )
    watchlist_items = relationship(
        "Watchlist", back_populates="stock", cascade="all, delete-orphan"
    )
    sector_benchmarks = relationship(
        "SectorBenchmark", back_populates="stocks", foreign_keys="SectorBenchmark.sector"
    )

    def __repr__(self) -> str:
        return f"<Stock {self.ticker} ({self.market})>"
