"""Financial data models - raw and normalized."""

from datetime import date, datetime
from typing import Any, Optional

from sqlalchemy import DATE, JSON, ForeignKey, Index, String, UniqueConstraint, VARCHAR, DateTime
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.types import NUMERIC

from .base import Base, TimestampMixin


class RawFinancial(Base):
    """Raw financial data as returned from external APIs."""

    __tablename__ = "raw_financials"
    __table_args__ = (
        Index("idx_raw_financials_stock_date", "stock_id", "data_as_of"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    stock_id: Mapped[int] = mapped_column(
        ForeignKey("stocks.id", ondelete="CASCADE"), nullable=False
    )
    source: Mapped[str] = mapped_column(VARCHAR(50), nullable=False)  # polygon, kis_api, dart, etc
    fiscal_period: Mapped[Optional[str]] = mapped_column(VARCHAR(10))  # 2024Q3, 2024A
    raw_json: Mapped[dict[str, Any]] = mapped_column(JSON, nullable=False)
    fetched_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(), nullable=False
    )
    data_as_of: Mapped[date] = mapped_column(DATE, nullable=False)

    # Relationships
    stock = relationship("Stock", back_populates="raw_financials")

    def __repr__(self) -> str:
        return f"<RawFinancial stock_id={self.stock_id} source={self.source}>"


class FinancialMetric(Base):
    """Normalized and calculated financial metrics."""

    __tablename__ = "financial_metrics"
    __table_args__ = (
        UniqueConstraint("stock_id", "data_as_of", name="uq_metrics_stock_date"),
        Index("idx_metrics_stock_date", "stock_id", "data_as_of"),
        Index("idx_metrics_recent", "data_as_of"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    stock_id: Mapped[int] = mapped_column(
        ForeignKey("stocks.id", ondelete="CASCADE"), nullable=False
    )

    # Price Data
    price: Mapped[Optional[float]] = mapped_column(NUMERIC(18, 4))
    market_cap: Mapped[Optional[float]] = mapped_column(NUMERIC(24, 2))

    # Valuation Metrics
    pe_ratio: Mapped[Optional[float]] = mapped_column(NUMERIC(10, 4))
    pb_ratio: Mapped[Optional[float]] = mapped_column(NUMERIC(10, 4))
    ps_ratio: Mapped[Optional[float]] = mapped_column(NUMERIC(10, 4))
    ev_ebitda: Mapped[Optional[float]] = mapped_column(NUMERIC(10, 4))
    peg_ratio: Mapped[Optional[float]] = mapped_column(NUMERIC(10, 4))
    price_to_fcf: Mapped[Optional[float]] = mapped_column(NUMERIC(10, 4))

    # Profitability Metrics
    roe: Mapped[Optional[float]] = mapped_column(NUMERIC(8, 4))
    roa: Mapped[Optional[float]] = mapped_column(NUMERIC(8, 4))
    gross_margin: Mapped[Optional[float]] = mapped_column(NUMERIC(8, 4))
    operating_margin: Mapped[Optional[float]] = mapped_column(NUMERIC(8, 4))
    net_margin: Mapped[Optional[float]] = mapped_column(NUMERIC(8, 4))

    # Growth Metrics
    revenue_growth_yoy: Mapped[Optional[float]] = mapped_column(NUMERIC(8, 4))
    eps_growth_yoy: Mapped[Optional[float]] = mapped_column(NUMERIC(8, 4))

    # Financial Health Metrics
    debt_to_equity: Mapped[Optional[float]] = mapped_column(NUMERIC(10, 4))
    current_ratio: Mapped[Optional[float]] = mapped_column(NUMERIC(8, 4))
    quick_ratio: Mapped[Optional[float]] = mapped_column(NUMERIC(8, 4))
    interest_coverage: Mapped[Optional[float]] = mapped_column(NUMERIC(10, 4))

    # Technical Indicators
    rsi_14: Mapped[Optional[float]] = mapped_column(NUMERIC(6, 2))

    # Metadata
    data_as_of: Mapped[date] = mapped_column(DATE, nullable=False)
    calculated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(), nullable=False
    )

    # Relationships
    stock = relationship("Stock", back_populates="financial_metrics")

    def __repr__(self) -> str:
        return f"<FinancialMetric stock_id={self.stock_id} as_of={self.data_as_of}>"


class SectorBenchmark(Base):
    """Aggregated metrics by sector for benchmark comparisons."""

    __tablename__ = "sector_benchmarks"
    __table_args__ = (
        UniqueConstraint("market", "sector", "metric_date", name="uq_sector_benchmark"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    market: Mapped[str] = mapped_column(VARCHAR(4), nullable=False)
    sector: Mapped[str] = mapped_column(VARCHAR(100), nullable=False)
    metric_date: Mapped[date] = mapped_column(DATE, nullable=False)

    # Median values for benchmarking
    median_pe: Mapped[Optional[float]] = mapped_column(NUMERIC(10, 4))
    median_pb: Mapped[Optional[float]] = mapped_column(NUMERIC(10, 4))
    median_ev_ebitda: Mapped[Optional[float]] = mapped_column(NUMERIC(10, 4))
    median_roe: Mapped[Optional[float]] = mapped_column(NUMERIC(8, 4))
    median_debt_eq: Mapped[Optional[float]] = mapped_column(NUMERIC(10, 4))
    stock_count: Mapped[int] = mapped_column(nullable=False, default=0)

    def __repr__(self) -> str:
        return f"<SectorBenchmark {self.market}/{self.sector} {self.metric_date}>"
