"""ROA (Return on Assets) profitability criterion."""

import logging
from decimal import Decimal

from app.core.screening.criteria.base import BaseCriteria, CriteriaResult

logger = logging.getLogger(__name__)


class ROACriteria(BaseCriteria):
    """Evaluate operational efficiency based on Return on Assets."""

    criteria_id = "profitability.roa"
    category = "profitability"
    name = "Return on Assets (ROA)"
    description = "How efficiently assets generate profit. Higher is better."
    default_weight = Decimal("0.8")

    async def evaluate(
        self,
        stock_id: int,
        market: str,
        financial_metric,
        sector_benchmark,
        db_session,
    ) -> CriteriaResult:
        """Evaluate ROA.

        Higher ROA = better operational efficiency.
        """
        roa = financial_metric.roa

        # Validate data
        if roa is None:
            raise ValueError(f"Stock {stock_id} missing roa")

        # ROA thresholds (absolute)
        # > 10%: excellent
        # 5-10%: good
        # 2-5%: average
        # < 2%: weak

        if roa >= 10:
            score = Decimal("0.9")
            is_healthy = True
        elif roa >= 5:
            score = Decimal("0.7")
            is_healthy = True
        elif roa >= 2:
            score = Decimal("0.5")
            is_healthy = False
        elif roa >= 0:
            score = Decimal("0.3")
            is_healthy = False
        else:
            score = Decimal("0.1")
            is_healthy = False

        reason = f"ROA {roa:.2f}% indicates {'strong' if is_healthy else 'weak'} asset efficiency"

        return CriteriaResult(
            criteria_id=self.criteria_id,
            score=score,
            raw_value=roa,
            benchmark_value=Decimal("5"),  # Industry average
            is_undervalued=is_healthy,
            reason=reason,
        )
