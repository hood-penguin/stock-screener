"""Quick Ratio financial health criterion."""

import logging
from decimal import Decimal

from app.core.screening.criteria.base import BaseCriteria, CriteriaResult

logger = logging.getLogger(__name__)


class QuickRatioCriteria(BaseCriteria):
    """Evaluate immediate liquidity based on Quick Ratio (Acid Test)."""

    criteria_id = "financial_health.quick_ratio"
    category = "financial_health"
    name = "Quick Ratio"
    description = (
        "Liquid assets to current liabilities (stricter than current ratio). Higher is better."
    )
    default_weight = Decimal("0.8")

    async def evaluate(
        self,
        stock_id: int,
        market: str,
        financial_metric,
        sector_benchmark,
        db_session,
    ) -> CriteriaResult:
        """Evaluate quick ratio.

        Higher quick ratio = better immediate liquidity without relying on inventory.
        """
        quick_ratio = financial_metric.quick_ratio

        # Validate data
        if quick_ratio is None:
            raise ValueError(f"Stock {stock_id} missing quick_ratio")

        # Quick ratio thresholds
        # > 1.5: excellent liquidity
        # 1.0-1.5: healthy
        # 0.6-1.0: adequate
        # < 0.6: liquidity risk

        if quick_ratio >= 1.5:
            score = Decimal("0.9")
            is_healthy = True
        elif quick_ratio >= 1.0:
            score = Decimal("0.75")
            is_healthy = True
        elif quick_ratio >= 0.6:
            score = Decimal("0.4")
            is_healthy = False
        else:
            score = Decimal("0.1")
            is_healthy = False

        reason = (
            f"Quick ratio {quick_ratio:.2f} indicates "
            f"{'strong' if is_healthy else 'weak'} immediate liquidity"
        )

        return CriteriaResult(
            criteria_id=self.criteria_id,
            score=score,
            raw_value=quick_ratio,
            benchmark_value=Decimal("1.0"),  # Break-even liquidity
            is_undervalued=is_healthy,
            reason=reason,
        )
