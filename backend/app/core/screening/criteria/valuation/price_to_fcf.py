"""Price-to-FCF (Free Cash Flow) valuation criterion."""

import logging
from decimal import Decimal

from app.core.screening.criteria.base import BaseCriteria, CriteriaResult

logger = logging.getLogger(__name__)


class PriceToFCFCriteria(BaseCriteria):
    """Evaluate valuation based on Price-to-FCF ratio."""

    criteria_id = "valuation.price_to_fcf"
    category = "valuation"
    name = "Price-to-FCF Ratio"
    description = (
        "Price per dollar of free cash flow. Lower is better."
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
        """Evaluate Price-to-FCF ratio.

        Lower P/FCF = stock trades at discount to cash generation capability.
        """
        price_to_fcf = financial_metric.price_to_fcf

        # Validate data
        if price_to_fcf is None:
            raise ValueError(f"Stock {stock_id} missing price_to_fcf")

        # P/FCF thresholds
        # < 10: very undervalued
        # 10-15: undervalued
        # 15-25: fairly valued
        # 25-40: overvalued
        # > 40: very overvalued

        if price_to_fcf < 10:
            score = Decimal("0.95")
            is_undervalued = True
        elif price_to_fcf < 15:
            score = Decimal("0.75")
            is_undervalued = True
        elif price_to_fcf < 25:
            score = Decimal("0.5")
            is_undervalued = False
        elif price_to_fcf < 40:
            score = Decimal("0.3")
            is_undervalued = False
        else:
            score = Decimal("0.1")
            is_undervalued = False

        reason = f"P/FCF ratio {price_to_fcf:.2f} indicates {'attractive' if is_undervalued else 'expensive'} valuation"

        return CriteriaResult(
            criteria_id=self.criteria_id,
            score=score,
            raw_value=price_to_fcf,
            benchmark_value=Decimal("20"),  # 20 is fair value
            is_undervalued=is_undervalued,
            reason=reason,
        )
