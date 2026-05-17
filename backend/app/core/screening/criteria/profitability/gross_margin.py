"""Gross Profit Margin profitability criterion."""

import logging
from decimal import Decimal

from app.core.screening.criteria.base import BaseCriteria, CriteriaResult

logger = logging.getLogger(__name__)


class GrossMarginCriteria(BaseCriteria):
    """Evaluate pricing power based on Gross Profit Margin."""

    criteria_id = "profitability.gross_margin"
    category = "profitability"
    name = "Gross Profit Margin"
    description = "Gross profit as percentage of revenue. Higher indicates pricing power."
    default_weight = Decimal("0.7")

    async def evaluate(
        self,
        stock_id: int,
        market: str,
        financial_metric,
        sector_benchmark,
        db_session,
    ) -> CriteriaResult:
        """Evaluate Gross Profit Margin.

        Higher gross margin indicates better pricing power and cost control.
        """
        gross_margin = financial_metric.gross_margin
        benchmark_margin = (
            sector_benchmark.median_gross_margin if sector_benchmark else None
        )

        # Validate data
        if gross_margin is None:
            raise ValueError(f"Stock {stock_id} missing gross_margin")

        if benchmark_margin is None:
            logger.warning(
                f"No benchmark gross margin for stock {stock_id} market {market}"
            )
            benchmark_margin = Decimal("40")

        # Normalize
        if benchmark_margin <= 0:
            benchmark_margin = Decimal("40")

        ratio = gross_margin / benchmark_margin

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
            f"Gross margin {gross_margin:.2f}% is "
            f"{('above' if gross_margin > benchmark_margin else 'below')} "
            f"sector median {benchmark_margin:.2f}%"
        )

        return CriteriaResult(
            criteria_id=self.criteria_id,
            score=score,
            raw_value=gross_margin,
            benchmark_value=benchmark_margin,
            is_undervalued=is_strong,
            reason=reason,
        )
