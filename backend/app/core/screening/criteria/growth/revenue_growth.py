"""Revenue Growth YoY growth criterion."""

import logging
from decimal import Decimal

from app.core.screening.criteria.base import BaseCriteria, CriteriaResult

logger = logging.getLogger(__name__)


class RevenueGrowthCriteria(BaseCriteria):
    """Evaluate growth potential based on Year-over-Year revenue growth."""

    criteria_id = "growth.revenue_growth_yoy"
    category = "growth"
    name = "Revenue Growth (YoY)"
    description = "Year-over-year revenue growth rate. Higher is better."
    default_weight = Decimal("1.0")

    async def evaluate(
        self,
        stock_id: int,
        market: str,
        financial_metric,
        sector_benchmark,
        db_session,
    ) -> CriteriaResult:
        """Evaluate revenue growth.

        Higher YoY revenue growth = better growth prospects.
        """
        revenue_growth = financial_metric.revenue_growth_yoy

        # Validate data
        if revenue_growth is None:
            raise ValueError(f"Stock {stock_id} missing revenue_growth_yoy")

        # Revenue growth thresholds
        # > 30%: exceptional
        # 15-30%: strong
        # 5-15%: healthy
        # 0-5%: slow
        # < 0%: declining

        if revenue_growth >= 30:
            score = Decimal("0.95")
            is_growing = True
        elif revenue_growth >= 15:
            score = Decimal("0.8")
            is_growing = True
        elif revenue_growth >= 5:
            score = Decimal("0.6")
            is_growing = True
        elif revenue_growth >= 0:
            score = Decimal("0.3")
            is_growing = False
        else:
            score = Decimal("0.1")
            is_growing = False

        reason = (
            f"Revenue growth {revenue_growth:.2f}% YoY is "
            f"{'strong' if is_growing else 'weak'}"
        )

        return CriteriaResult(
            criteria_id=self.criteria_id,
            score=score,
            raw_value=revenue_growth,
            benchmark_value=Decimal("10"),  # 10% growth as benchmark
            is_undervalued=is_growing,
            reason=reason,
        )
