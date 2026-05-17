"""Net Profit Margin profitability criterion."""

import logging
from decimal import Decimal

from app.core.screening.criteria.base import BaseCriteria, CriteriaResult

logger = logging.getLogger(__name__)


class NetMarginCriteria(BaseCriteria):
    """Evaluate profitability based on Net Profit Margin."""

    criteria_id = "profitability.net_margin"
    category = "profitability"
    name = "Net Profit Margin"
    description = (
        "Percentage of revenue that becomes profit. Higher is better."
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
        """Evaluate Net Profit Margin.

        Higher net margin = better profitability.
        """
        net_margin = financial_metric.net_margin
        benchmark_margin = (
            sector_benchmark.median_net_margin if sector_benchmark else None
        )

        # Validate data
        if net_margin is None:
            raise ValueError(f"Stock {stock_id} missing net_margin")

        if benchmark_margin is None:
            logger.warning(
                f"No benchmark net margin for stock {stock_id} market {market}"
            )
            benchmark_margin = Decimal("10")

        # Normalize: compare to sector median
        if benchmark_margin <= 0:
            benchmark_margin = Decimal("10")

        ratio = net_margin / benchmark_margin

        if ratio >= 1.5:
            score = Decimal("0.9")
            is_healthy = True
        elif ratio >= 1.1:
            score = Decimal("0.7")
            is_healthy = True
        elif ratio >= 0.9:
            score = Decimal("0.5")
            is_healthy = False
        elif ratio >= 0.7:
            score = Decimal("0.3")
            is_healthy = False
        else:
            score = Decimal("0.1")
            is_healthy = False

        reason = (
            f"Net margin {net_margin:.2f}% is "
            f"{('above' if net_margin > benchmark_margin else 'below')} "
            f"sector median {benchmark_margin:.2f}%"
        )

        return CriteriaResult(
            criteria_id=self.criteria_id,
            score=score,
            raw_value=net_margin,
            benchmark_value=benchmark_margin,
            is_undervalued=is_healthy,
            reason=reason,
        )
