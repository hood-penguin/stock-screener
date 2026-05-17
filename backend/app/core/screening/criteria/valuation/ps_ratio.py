"""P/S Ratio valuation criterion."""

import logging
from decimal import Decimal

from app.core.screening.criteria.base import BaseCriteria, CriteriaResult

logger = logging.getLogger(__name__)


class PSRatioCriteria(BaseCriteria):
    """Evaluate stock undervaluation based on P/S ratio."""

    criteria_id = "valuation.ps_ratio"
    category = "valuation"
    name = "P/S Ratio"
    description = "Price-to-Sales ratio. Lower is better."
    default_weight = Decimal("0.7")

    async def evaluate(
        self,
        stock_id: int,
        market: str,
        financial_metric,
        sector_benchmark,
        db_session,
    ) -> CriteriaResult:
        """Evaluate P/S ratio.

        Lower P/S ratio = undervalued.
        """
        ps_ratio = financial_metric.ps_ratio

        # Validate data
        if ps_ratio is None:
            raise ValueError(f"Stock {stock_id} missing ps_ratio")

        # P/S ratio thresholds (absolute, less dependent on sector variation)
        # Less than 1.0 is generally considered undervalued
        # Less than 2.0 is reasonable
        # Greater than 3.0 is expensive

        if ps_ratio <= 0.5:
            score = Decimal("0.95")
            is_undervalued = True
        elif ps_ratio <= 1.0:
            score = Decimal("0.8")
            is_undervalued = True
        elif ps_ratio <= 2.0:
            score = Decimal("0.5")
            is_undervalued = False
        elif ps_ratio <= 3.0:
            score = Decimal("0.3")
            is_undervalued = False
        else:
            score = Decimal("0.1")
            is_undervalued = False

        reason = f"P/S ratio {ps_ratio:.2f} indicates stock is {'undervalued' if is_undervalued else 'fairly valued or overvalued'}"

        return CriteriaResult(
            criteria_id=self.criteria_id,
            score=score,
            raw_value=ps_ratio,
            benchmark_value=Decimal("2.0"),  # Industry average
            is_undervalued=is_undervalued,
            reason=reason,
        )
