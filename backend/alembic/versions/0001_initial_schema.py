"""Initial schema creation with all tables.

Revision ID: 0001_initial_schema
Revises:
Create Date: 2026-05-17 19:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision: str = "0001_initial_schema"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Create stocks table
    op.create_table(
        "stocks",
        sa.Column("id", sa.BigInteger(), nullable=False),
        sa.Column("ticker", sa.VARCHAR(length=20), nullable=False),
        sa.Column("market", sa.VARCHAR(length=4), nullable=False),
        sa.Column("exchange", sa.VARCHAR(length=20), nullable=False),
        sa.Column("company_name", sa.VARCHAR(length=200), nullable=False),
        sa.Column("company_name_en", sa.VARCHAR(length=200), nullable=True),
        sa.Column("sector", sa.VARCHAR(length=100), nullable=True),
        sa.Column("industry", sa.VARCHAR(length=100), nullable=True),
        sa.Column("currency", sa.VARCHAR(length=4), nullable=False),
        sa.Column("is_active", sa.Boolean(), nullable=False),
        sa.Column("listed_at", sa.Date(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("ticker", "market", name="uq_stock_ticker_market"),
    )
    op.create_index("idx_stocks_active", "stocks", ["is_active"], postgresql_where=sa.text("is_active = TRUE"))
    op.create_index("idx_stocks_market_sector", "stocks", ["market", "sector"])

    # Create raw_financials table
    op.create_table(
        "raw_financials",
        sa.Column("id", sa.BigInteger(), nullable=False),
        sa.Column("stock_id", sa.BigInteger(), nullable=False),
        sa.Column("source", sa.VARCHAR(length=50), nullable=False),
        sa.Column("fiscal_period", sa.VARCHAR(length=10), nullable=True),
        sa.Column("raw_json", postgresql.JSON(astext_type=sa.Text()), nullable=False),
        sa.Column("fetched_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("data_as_of", sa.Date(), nullable=False),
        sa.ForeignKeyConstraint(["stock_id"], ["stocks.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("idx_raw_financials_stock_date", "raw_financials", ["stock_id", "data_as_of"])

    # Create financial_metrics table
    op.create_table(
        "financial_metrics",
        sa.Column("id", sa.BigInteger(), nullable=False),
        sa.Column("stock_id", sa.BigInteger(), nullable=False),
        sa.Column("price", sa.NUMERIC(precision=18, scale=4), nullable=True),
        sa.Column("market_cap", sa.NUMERIC(precision=24, scale=2), nullable=True),
        sa.Column("pe_ratio", sa.NUMERIC(precision=10, scale=4), nullable=True),
        sa.Column("pb_ratio", sa.NUMERIC(precision=10, scale=4), nullable=True),
        sa.Column("ps_ratio", sa.NUMERIC(precision=10, scale=4), nullable=True),
        sa.Column("ev_ebitda", sa.NUMERIC(precision=10, scale=4), nullable=True),
        sa.Column("peg_ratio", sa.NUMERIC(precision=10, scale=4), nullable=True),
        sa.Column("price_to_fcf", sa.NUMERIC(precision=10, scale=4), nullable=True),
        sa.Column("roe", sa.NUMERIC(precision=8, scale=4), nullable=True),
        sa.Column("roa", sa.NUMERIC(precision=8, scale=4), nullable=True),
        sa.Column("gross_margin", sa.NUMERIC(precision=8, scale=4), nullable=True),
        sa.Column("operating_margin", sa.NUMERIC(precision=8, scale=4), nullable=True),
        sa.Column("net_margin", sa.NUMERIC(precision=8, scale=4), nullable=True),
        sa.Column("revenue_growth_yoy", sa.NUMERIC(precision=8, scale=4), nullable=True),
        sa.Column("eps_growth_yoy", sa.NUMERIC(precision=8, scale=4), nullable=True),
        sa.Column("debt_to_equity", sa.NUMERIC(precision=10, scale=4), nullable=True),
        sa.Column("current_ratio", sa.NUMERIC(precision=8, scale=4), nullable=True),
        sa.Column("quick_ratio", sa.NUMERIC(precision=8, scale=4), nullable=True),
        sa.Column("interest_coverage", sa.NUMERIC(precision=10, scale=4), nullable=True),
        sa.Column("rsi_14", sa.NUMERIC(precision=6, scale=2), nullable=True),
        sa.Column("data_as_of", sa.Date(), nullable=False),
        sa.Column("calculated_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["stock_id"], ["stocks.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("stock_id", "data_as_of", name="uq_metrics_stock_date"),
    )
    op.create_index("idx_metrics_recent", "financial_metrics", ["data_as_of"])
    op.create_index("idx_metrics_stock_date", "financial_metrics", ["stock_id", "data_as_of"])

    # Create sector_benchmarks table
    op.create_table(
        "sector_benchmarks",
        sa.Column("id", sa.BigInteger(), nullable=False),
        sa.Column("market", sa.VARCHAR(length=4), nullable=False),
        sa.Column("sector", sa.VARCHAR(length=100), nullable=False),
        sa.Column("metric_date", sa.Date(), nullable=False),
        sa.Column("median_pe", sa.NUMERIC(precision=10, scale=4), nullable=True),
        sa.Column("median_pb", sa.NUMERIC(precision=10, scale=4), nullable=True),
        sa.Column("median_ev_ebitda", sa.NUMERIC(precision=10, scale=4), nullable=True),
        sa.Column("median_roe", sa.NUMERIC(precision=8, scale=4), nullable=True),
        sa.Column("median_debt_eq", sa.NUMERIC(precision=10, scale=4), nullable=True),
        sa.Column("stock_count", sa.Integer(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("market", "sector", "metric_date", name="uq_sector_benchmark"),
    )

    # Create users table
    op.create_table(
        "users",
        sa.Column("id", sa.BigInteger(), nullable=False),
        sa.Column("email", sa.VARCHAR(length=255), nullable=False),
        sa.Column("password_hash", sa.VARCHAR(length=255), nullable=False),
        sa.Column("display_name", sa.VARCHAR(length=100), nullable=True),
        sa.Column("tier", sa.VARCHAR(length=20), nullable=False),
        sa.Column("is_active", sa.Boolean(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("email", name="uq_user_email"),
    )

    # Create screening_results table
    op.create_table(
        "screening_results",
        sa.Column("id", sa.BigInteger(), nullable=False),
        sa.Column("stock_id", sa.BigInteger(), nullable=False),
        sa.Column("market", sa.VARCHAR(length=4), nullable=False),
        sa.Column("total_score", sa.NUMERIC(precision=5, scale=2), nullable=False),
        sa.Column("is_undervalued", sa.Boolean(), nullable=False),
        sa.Column("screened_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("metrics_date", sa.Date(), nullable=False),
        sa.ForeignKeyConstraint(["stock_id"], ["stocks.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("idx_screening_date", "screening_results", ["screened_at"])
    op.create_index("idx_screening_market_score", "screening_results", ["market", "total_score"])
    op.create_index("idx_screening_stock", "screening_results", ["stock_id", "screened_at"])

    # Create criteria_scores table
    op.create_table(
        "criteria_scores",
        sa.Column("id", sa.BigInteger(), nullable=False),
        sa.Column("screening_result_id", sa.BigInteger(), nullable=False),
        sa.Column("criteria_id", sa.VARCHAR(length=100), nullable=False),
        sa.Column("score", sa.NUMERIC(precision=5, scale=4), nullable=False),
        sa.Column("raw_value", sa.NUMERIC(precision=18, scale=4), nullable=True),
        sa.Column("benchmark_value", sa.NUMERIC(precision=18, scale=4), nullable=True),
        sa.Column("is_undervalued", sa.Boolean(), nullable=True),
        sa.Column("reason", sa.Text(), nullable=True),
        sa.ForeignKeyConstraint(["screening_result_id"], ["screening_results.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("idx_criteria_result", "criteria_scores", ["screening_result_id"])

    # Create watchlists table
    op.create_table(
        "watchlists",
        sa.Column("id", sa.BigInteger(), nullable=False),
        sa.Column("user_id", sa.BigInteger(), nullable=False),
        sa.Column("stock_id", sa.BigInteger(), nullable=False),
        sa.Column("alert_threshold", sa.NUMERIC(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["stock_id"], ["stocks.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("user_id", "stock_id", name="uq_watchlist_user_stock"),
    )

    # Create user_screening_presets table
    op.create_table(
        "user_screening_presets",
        sa.Column("id", sa.BigInteger(), nullable=False),
        sa.Column("user_id", sa.BigInteger(), nullable=False),
        sa.Column("preset_name", sa.VARCHAR(length=100), nullable=False),
        sa.Column("is_default", sa.Boolean(), nullable=False),
        sa.Column("enabled_criteria", postgresql.JSON(astext_type=sa.Text()), nullable=False),
        sa.Column("weight_overrides", postgresql.JSON(astext_type=sa.Text()), nullable=False),
        sa.Column("min_score", sa.NUMERIC(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("user_id", "preset_name", name="uq_preset_user_name"),
    )


def downgrade() -> None:
    # Drop tables in reverse order of creation
    op.drop_table("user_screening_presets")
    op.drop_table("watchlists")
    op.drop_table("criteria_scores")
    op.drop_table("screening_results")
    op.drop_table("users")
    op.drop_table("sector_benchmarks")
    op.drop_table("financial_metrics")
    op.drop_table("raw_financials")
    op.drop_table("stocks")
