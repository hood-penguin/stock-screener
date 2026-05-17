"""Base class and data structures for screening criteria."""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Optional

from decimal import Decimal


@dataclass
class CriteriaResult:
    """Result of evaluating a single screening criterion."""

    criteria_id: str
    """Unique identifier for the criteria (e.g., 'valuation.pe_ratio')."""

    score: Decimal
    """Score from 0 to 1, where 1 is best (undervalued/healthy)."""

    raw_value: Optional[Decimal] = None
    """The actual metric value used in calculation."""

    benchmark_value: Optional[Decimal] = None
    """The benchmark or threshold value for comparison."""

    is_undervalued: Optional[bool] = None
    """Whether the stock is undervalued by this criterion."""

    reason: Optional[str] = None
    """Human-readable explanation of the score."""


class BaseCriteria(ABC):
    """Abstract base class for all screening criteria.

    Criteria plugins must inherit from this class and implement evaluate().
    The screening engine discovers and loads criteria automatically.
    """

    # Criteria metadata (must be set in subclass)
    criteria_id: str = ""
    """Unique identifier (e.g., 'valuation.pe_ratio')."""

    category: str = ""
    """Category: valuation, profitability, growth, or financial_health."""

    name: str = ""
    """Human-readable name (e.g., 'P/E Ratio')."""

    description: str = ""
    """Detailed description of what this criterion measures."""

    default_weight: Decimal = Decimal("1.0")
    """Default weight in composite scoring (0-1)."""

    markets: set[str] = None
    """Markets this criterion applies to (e.g., {'US', 'KR'})."""

    def __init__(self):
        """Initialize criteria with default markets if not specified."""
        if self.markets is None:
            self.markets = {"US", "KR"}

    @abstractmethod
    async def evaluate(
        self,
        stock_id: int,
        market: str,
        financial_metric,
        sector_benchmark,
        db_session,
    ) -> CriteriaResult:
        """Evaluate this criterion for a specific stock.

        Args:
            stock_id: ID of the stock to evaluate
            market: Market code ('US' or 'KR')
            financial_metric: FinancialMetric object with normalized metrics
            sector_benchmark: SectorBenchmark object for market/sector averages
            db_session: AsyncSession for database access if needed

        Returns:
            CriteriaResult with score (0-1), raw_value, benchmark_value, reason

        Raises:
            ValueError: If required data is missing or invalid
        """
        pass

    def validate_config(self) -> None:
        """Validate that this criteria instance is properly configured.

        Raises:
            ValueError: If configuration is invalid
        """
        if not self.criteria_id:
            raise ValueError(f"{self.__class__.__name__} must define criteria_id")
        if not self.category:
            raise ValueError(f"{self.__class__.__name__} must define category")
        if not self.name:
            raise ValueError(f"{self.__class__.__name__} must define name")

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(criteria_id={self.criteria_id})"
