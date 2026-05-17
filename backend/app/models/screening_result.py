"""Screening results and criteria scores models."""

from datetime import date, datetime
from typing import Optional

from sqlalchemy import DATE, Index, String, Text, VARCHAR
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.types import NUMERIC, DateTime, Boolean

from .base import Base


class ScreeningResult(Base):
    """Results from screening execution."""

    __tablename__ = "screening_results"
    __table_args__ = (
        Index("idx_screening_market_score", "market", "total_score"),
        Index("idx_screening_date", "screened_at"),
        Index("idx_screening_stock", "stock_id", "screened_at"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    stock_id: Mapped[int] = mapped_column(
        nullable=False, foreign_key="stocks.id", ondelete="CASCADE"
    )
    market: Mapped[str] = mapped_column(VARCHAR(4), nullable=False)
    total_score: Mapped[float] = mapped_column(
        NUMERIC(5, 2), nullable=False
    )  # 0-100 score
    is_undervalued: Mapped[bool] = mapped_column(Boolean, nullable=False)
    screened_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(), nullable=False
    )
    metrics_date: Mapped[date] = mapped_column(DATE, nullable=False)

    # Relationships
    stock = relationship("Stock", back_populates="screening_results")
    criteria_scores = relationship(
        "CriteriaScore",
        back_populates="screening_result",
        cascade="all, delete-orphan",
    )

    def __repr__(self) -> str:
        return f"<ScreeningResult stock_id={self.stock_id} score={self.total_score}>"


class CriteriaScore(Base):
    """Score breakdown by individual criteria."""

    __tablename__ = "criteria_scores"
    __table_args__ = (Index("idx_criteria_result", "screening_result_id"),)

    id: Mapped[int] = mapped_column(primary_key=True)
    screening_result_id: Mapped[int] = mapped_column(
        nullable=False, foreign_key="screening_results.id", ondelete="CASCADE"
    )
    criteria_id: Mapped[str] = mapped_column(VARCHAR(100), nullable=False)
    score: Mapped[float] = mapped_column(
        NUMERIC(5, 4), nullable=False
    )  # 0.0-1.0 score
    raw_value: Mapped[Optional[float]] = mapped_column(NUMERIC(18, 4))
    benchmark_value: Mapped[Optional[float]] = mapped_column(NUMERIC(18, 4))
    is_undervalued: Mapped[Optional[bool]] = mapped_column(Boolean)
    reason: Mapped[Optional[str]] = mapped_column(Text)

    # Relationships
    screening_result = relationship("ScreeningResult", back_populates="criteria_scores")

    def __repr__(self) -> str:
        return f"<CriteriaScore criteria_id={self.criteria_id} score={self.score}>"
