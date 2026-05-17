"""User models - authentication and preferences."""

from datetime import datetime
from typing import Optional

from sqlalchemy import Boolean, String, UniqueConstraint, VARCHAR, JSON
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.types import DateTime

from .base import Base


class User(Base):
    """User account for authentication."""

    __tablename__ = "users"
    __table_args__ = (UniqueConstraint("email", name="uq_user_email"),)

    id: Mapped[int] = mapped_column(primary_key=True)
    email: Mapped[str] = mapped_column(VARCHAR(255), nullable=False)
    password_hash: Mapped[str] = mapped_column(VARCHAR(255), nullable=False)
    display_name: Mapped[Optional[str]] = mapped_column(VARCHAR(100))
    tier: Mapped[str] = mapped_column(VARCHAR(20), default="free", nullable=False)  # free, premium
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(), nullable=False
    )

    # Relationships
    watchlists = relationship(
        "Watchlist", back_populates="user", cascade="all, delete-orphan"
    )
    screening_presets = relationship(
        "UserScreeningPreset", back_populates="user", cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:
        return f"<User {self.email}>"


class Watchlist(Base):
    """User's watchlist - stocks they're interested in."""

    __tablename__ = "watchlists"
    __table_args__ = (UniqueConstraint("user_id", "stock_id", name="uq_watchlist_user_stock"),)

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(
        nullable=False, foreign_key="users.id", ondelete="CASCADE"
    )
    stock_id: Mapped[int] = mapped_column(
        nullable=False, foreign_key="stocks.id", ondelete="CASCADE"
    )
    alert_threshold: Mapped[Optional[float]] = mapped_column()  # Alert if score >= threshold
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(), nullable=False
    )

    # Relationships
    user = relationship("User", back_populates="watchlists")
    stock = relationship("Stock", back_populates="watchlist_items")

    def __repr__(self) -> str:
        return f"<Watchlist user_id={self.user_id} stock_id={self.stock_id}>"


class UserScreeningPreset(Base):
    """User's custom screening preset with criteria selection and weights."""

    __tablename__ = "user_screening_presets"
    __table_args__ = (
        UniqueConstraint("user_id", "preset_name", name="uq_preset_user_name"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(
        nullable=False, foreign_key="users.id", ondelete="CASCADE"
    )
    preset_name: Mapped[str] = mapped_column(VARCHAR(100), nullable=False)
    is_default: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    enabled_criteria: Mapped[dict[str, bool]] = mapped_column(
        JSON, nullable=False, default={}
    )  # {"criteria_id": true/false}
    weight_overrides: Mapped[dict[str, float]] = mapped_column(
        JSON, nullable=False, default={}
    )  # {"criteria_id": weight}
    min_score: Mapped[Optional[float]] = mapped_column(default=0)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(), nullable=False
    )

    # Relationships
    user = relationship("User", back_populates="screening_presets")

    def __repr__(self) -> str:
        return f"<UserScreeningPreset user_id={self.user_id} name={self.preset_name}>"
