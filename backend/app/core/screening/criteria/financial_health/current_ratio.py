"""Current Ratio financial health criterion."""

import logging
from decimal import Decimal

from app.core.screening.criteria.base import BaseCriteria, CriteriaResult

logger = logging.getLogger(__name__)


class CurrentRatioCriteria(BaseCriteria):
    """Evaluate short-term liquidity based on Current Ratio."""

    criteria_id = "financial_health.current_ratio"
    category = "financial_health"
    name = "Current Ratio"
    description = (
        "Current assets to current liabilities. Higher is better (1.5-3.0 is healthy)."
    )
    default_weight = Decimal("0.9")

    async def evaluate(
        self,
        stock_id: int,
        market: str,
        financial_metric,
        sector_benchmark,
        db_session,
    ) -> CriteriaResult:
        """Evaluate current ratio.

        Higher current ratio = better liquidity and less financial distress risk.
        """
        current_ratio = financial_metric.current_ratio

        # Validate data
        if current_ratio is None:
            raise ValueError(f"Stock {stock_id} missing current_ratio")

        # Current ratio thresholds
        # > 3.0: over-capitalized (slightly inefficient)
        # 1.5-3.0: healthy
        # 1.0-1.5: adequate but tight
        # < 1.0: liquidity crisis risk

        if current_ratio >= 1.5 and current_ratio <= 3.0:
            score = Decimal("0.9")
            is_healthy = True
        elif current_ratio > 1.0:
            score = Decimal("0.7")
            is_healthy = True
        elif current_ratio >= 0.8:
            score = Decimal("0.4")
            is_healthy = False
        else:
            score = Decimal("0.1")
            is_healthy = False

        if current_ratio >= 3.0:
            reason = f"Current ratio {current_ratio:.2f} shows over-capitalization"
        else:
            reason = (
                f"Current ratio {current_ratio:.2f} indicates "
                f"{'strong' if is_healthy else 'weak'} liquidity"
            )

        return CriteriaResult(
            criteria_id=self.criteria_id,
            score=score,
            raw_value=current_ratio,
            benchmark_value=Decimal("2.0"),  # Healthy benchmark
            is_undervalued=is_healthy,
            reason=reason,
        )
