"""Operating Profit Margin profitability criterion."""

import logging
from decimal import Decimal

from app.core.screening.criteria.base import BaseCriteria, CriteriaResult

logger = logging.getLogger(__name__)


class OperatingMarginCriteria(BaseCriteria):
    """Evaluate operational efficiency based on Operating Profit Margin."""

    criteria_id = "profitability.operating_margin"
    category = "profitability"
    name = "Operating Profit Margin"
    description = "Operating profit as percentage of revenue. Higher is better."
    default_weight = Decimal("0.8")

    async def evaluate(
        self,
        stock_id: int,
        market: str,
        financial_metric,
        sector_benchmark,
        db_session,
    ) -> CriteriaResult:
        """Evaluate Operating Profit Margin.

        Higher operating margin indicates efficient operations.
        """
        operating_margin = financial_metric.operating_margin
        benchmark_margin = (
            sector_benchmark.median_operating_margin
            if sector_benchmark
            else None
        )

        # Validate data
        if operating_margin is None:
            raise ValueError(f"Stock {stock_id} missing operating_margin")

        if benchmark_margin is None:
            logger.warning(
                f"No benchmark operating margin for stock {stock_id} market {market}"
            )
            benchmark_margin = Decimal("15")

        # Normalize
        if benchmark_margin <= 0:
            benchmark_margin = Decimal("15")

        ratio = operating_margin / benchmark_margin

        if ratio >= 1.3:
            score = Decimal("0.9")
            is_strong = True
        elif ratio >= 1.1:
            score = Decimal("0.7")
            is_strong = True
        elif ratio >= 0.9:
            score = Decimal("0.5")
            is_strong = False
        elif ratio >= 0.7:
            score = Decimal("0.3")
            is_strong = False
        else:
            score = Decimal("0.1")
            is_strong = False

        reason = (
            f"Operating margin {operating_margin:.2f}% is "
            f"{('above' if operating_margin > benchmark_margin else 'below')} "
            f"sector median {benchmark_margin:.2f}%"
        )

        return CriteriaResult(
            criteria_id=self.criteria_id,
            score=score,
            raw_value=operating_margin,
            benchmark_value=benchmark_margin,
            is_undervalued=is_strong,
            reason=reason,
        )
