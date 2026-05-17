"""Interest Coverage financial health criterion."""

import logging
from decimal import Decimal

from app.core.screening.criteria.base import BaseCriteria, CriteriaResult

logger = logging.getLogger(__name__)


class InterestCoverageCriteria(BaseCriteria):
    """Evaluate debt servicing ability based on Interest Coverage Ratio."""

    criteria_id = "financial_health.interest_coverage"
    category = "financial_health"
    name = "Interest Coverage Ratio"
    description = "How many times EBITDA covers interest expense. Higher is better."
    default_weight = Decimal("0.8")

    async def evaluate(
        self,
        stock_id: int,
        market: str,
        financial_metric,
        sector_benchmark,
        db_session,
    ) -> CriteriaResult:
        """Evaluate interest coverage ratio.

        Higher interest coverage = better ability to service debt.
        """
        interest_coverage = financial_metric.interest_coverage

        # Validate data
        if interest_coverage is None:
            raise ValueError(f"Stock {stock_id} missing interest_coverage")

        # Interest coverage thresholds
        # > 10: excellent
        # 5-10: strong
        # 2.5-5: adequate
        # 1.5-2.5: weak
        # < 1.5: distress

        if interest_coverage >= 10:
            score = Decimal("0.95")
            is_healthy = True
        elif interest_coverage >= 5:
            score = Decimal("0.8")
            is_healthy = True
        elif interest_coverage >= 2.5:
            score = Decimal("0.6")
            is_healthy = True
        elif interest_coverage >= 1.5:
            score = Decimal("0.3")
            is_healthy = False
        else:
            score = Decimal("0.1")
            is_healthy = False

        reason = (
            f"Interest coverage {interest_coverage:.2f}x indicates "
            f"{'strong' if is_healthy else 'weak'} debt servicing ability"
        )

        return CriteriaResult(
            criteria_id=self.criteria_id,
            score=score,
            raw_value=interest_coverage,
            benchmark_value=Decimal("5"),  # 5x is healthy benchmark
            is_undervalued=is_healthy,
            reason=reason,
        )
