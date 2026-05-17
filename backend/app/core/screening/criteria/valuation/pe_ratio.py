"""P/E Ratio valuation criterion."""

import logging
from decimal import Decimal
from typing import Optional

from app.core.screening.criteria.base import BaseCriteria, CriteriaResult

logger = logging.getLogger(__name__)


class PERatioCriteria(BaseCriteria):
    """Evaluate stock undervaluation based on P/E ratio vs sector median."""

    criteria_id = "valuation.pe_ratio"
    category = "valuation"
    name = "P/E Ratio"
    description = "Price-to-Earnings ratio compared to sector median. Lower is better."
    default_weight = Decimal("1.0")

    async def evaluate(
        self,
        stock_id: int,
        market: str,
        financial_metric,
        sector_benchmark,
        db_session,
    ) -> CriteriaResult:
        """Evaluate P/E ratio.

        Lower P/E ratio relative to sector = undervalued.
        """
        pe_ratio = financial_metric.pe_ratio
        benchmark_pe = sector_benchmark.median_pe if sector_benchmark else None

        # Validate data
        if pe_ratio is None:
            raise ValueError(f"Stock {stock_id} missing pe_ratio")

        if benchmark_pe is None:
            logger.warning(
                f"No benchmark P/E for stock {stock_id} market {market}"
            )
            benchmark_pe = Decimal("25")  # Use reasonable default

        # Normalize: stock PE close to sector median = neutral (0.5)
        # Much lower than median = good (closer to 1.0)
        # Much higher than median = bad (closer to 0.0)

        # Avoid division by zero
        if benchmark_pe <= 0:
            benchmark_pe = Decimal("25")

        ratio = pe_ratio / benchmark_pe

        # Score: inverse relationship
        # ratio 0.5 (half of median) → 0.8 (good)
        # ratio 1.0 (equal to median) → 0.5 (neutral)
        # ratio 2.0 (double median) → 0.2 (bad)

        if ratio <= 0.5:
            score = Decimal("0.9")
            is_undervalued = True
        elif ratio <= 0.75:
            score = Decimal("0.7")
            is_undervalued = True
        elif ratio <= 1.0:
            score = Decimal("0.5")
            is_undervalued = False
        elif ratio <= 1.5:
            score = Decimal("0.3")
            is_undervalued = False
        else:
            score = Decimal("0.1")
            is_undervalued = False

        reason = (
            f"P/E ratio {pe_ratio:.2f} is "
            f"{('below' if pe_ratio < benchmark_pe else 'above')} "
            f"sector median {benchmark_pe:.2f}"
        )

        return CriteriaResult(
            criteria_id=self.criteria_id,
            score=score,
            raw_value=pe_ratio,
            benchmark_value=benchmark_pe,
            is_undervalued=is_undervalued,
            reason=reason,
        )
