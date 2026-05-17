"""P/B Ratio valuation criterion."""

import logging
from decimal import Decimal

from app.core.screening.criteria.base import BaseCriteria, CriteriaResult

logger = logging.getLogger(__name__)


class PBRatioCriteria(BaseCriteria):
    """Evaluate stock undervaluation based on P/B ratio vs sector median."""

    criteria_id = "valuation.pb_ratio"
    category = "valuation"
    name = "P/B Ratio"
    description = "Price-to-Book ratio compared to sector median. Lower is better."
    default_weight = Decimal("0.8")

    async def evaluate(
        self,
        stock_id: int,
        market: str,
        financial_metric,
        sector_benchmark,
        db_session,
    ) -> CriteriaResult:
        """Evaluate P/B ratio.

        Lower P/B ratio relative to sector = undervalued.
        """
        pb_ratio = financial_metric.pb_ratio
        benchmark_pb = sector_benchmark.median_pb if sector_benchmark else None

        # Validate data
        if pb_ratio is None:
            raise ValueError(f"Stock {stock_id} missing pb_ratio")

        if benchmark_pb is None:
            logger.warning(
                f"No benchmark P/B for stock {stock_id} market {market}"
            )
            benchmark_pb = Decimal("2.0")

        # Normalize
        if benchmark_pb <= 0:
            benchmark_pb = Decimal("2.0")

        ratio = pb_ratio / benchmark_pb

        # Score calculation similar to P/E
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
            f"P/B ratio {pb_ratio:.2f} is "
            f"{('below' if pb_ratio < benchmark_pb else 'above')} "
            f"sector median {benchmark_pb:.2f}"
        )

        return CriteriaResult(
            criteria_id=self.criteria_id,
            score=score,
            raw_value=pb_ratio,
            benchmark_value=benchmark_pb,
            is_undervalued=is_undervalued,
            reason=reason,
        )
