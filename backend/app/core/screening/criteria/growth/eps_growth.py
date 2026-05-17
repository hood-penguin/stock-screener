"""EPS Growth YoY growth criterion."""

import logging
from decimal import Decimal

from app.core.screening.criteria.base import BaseCriteria, CriteriaResult

logger = logging.getLogger(__name__)


class EPSGrowthCriteria(BaseCriteria):
    """Evaluate earnings growth based on Year-over-Year EPS growth."""

    criteria_id = "growth.eps_growth_yoy"
    category = "growth"
    name = "EPS Growth (YoY)"
    description = "Year-over-year earnings per share growth. Higher is better."
    default_weight = Decimal("1.0")

    async def evaluate(
        self,
        stock_id: int,
        market: str,
        financial_metric,
        sector_benchmark,
        db_session,
    ) -> CriteriaResult:
        """Evaluate EPS growth.

        Higher YoY EPS growth = better earnings quality.
        """
        eps_growth = financial_metric.eps_growth_yoy

        # Validate data
        if eps_growth is None:
            raise ValueError(f"Stock {stock_id} missing eps_growth_yoy")

        # EPS growth thresholds (even more important than revenue growth)
        # > 25%: exceptional
        # 12-25%: strong
        # 5-12%: healthy
        # 0-5%: slow
        # < 0%: declining

        if eps_growth >= 25:
            score = Decimal("0.95")
            is_growing = True
        elif eps_growth >= 12:
            score = Decimal("0.8")
            is_growing = True
        elif eps_growth >= 5:
            score = Decimal("0.6")
            is_growing = True
        elif eps_growth >= 0:
            score = Decimal("0.3")
            is_growing = False
        else:
            score = Decimal("0.1")
            is_growing = False

        reason = (
            f"EPS growth {eps_growth:.2f}% YoY is "
            f"{'strong' if is_growing else 'weak'}"
        )

        return CriteriaResult(
            criteria_id=self.criteria_id,
            score=score,
            raw_value=eps_growth,
            benchmark_value=Decimal("8"),  # 8% growth as benchmark
            is_undervalued=is_growing,
            reason=reason,
        )
