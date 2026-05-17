"""PEG Ratio valuation criterion."""

import logging
from decimal import Decimal

from app.core.screening.criteria.base import BaseCriteria, CriteriaResult

logger = logging.getLogger(__name__)


class PEGRatioCriteria(BaseCriteria):
    """Evaluate stock undervaluation based on PEG ratio (P/E relative to growth)."""

    criteria_id = "valuation.peg_ratio"
    category = "valuation"
    name = "PEG Ratio"
    description = (
        "P/E to Growth ratio. Lower than 1.0 means stock is undervalued relative to growth."
    )
    default_weight = Decimal("1.0")

    async def evaluate(
        self,
        stock_id: int,
        market: str,
        financial_metric,
        sector_benchmark,
        db_session,
    ) -> CriteriaResult:
        """Evaluate PEG ratio.

        PEG = P/E Ratio / Expected Annual Growth Rate (%)
        Lower PEG = better value relative to growth prospects.
        """
        peg_ratio = financial_metric.peg_ratio
        eps_growth = financial_metric.eps_growth_yoy

        # Validate data
        if peg_ratio is None:
            raise ValueError(f"Stock {stock_id} missing peg_ratio")

        # PEG ratio interpretation:
        # < 0.5: significantly undervalued
        # 0.5-1.0: undervalued
        # 1.0-1.5: fairly valued
        # 1.5-2.0: slightly overvalued
        # > 2.0: overvalued

        if peg_ratio < 0.5:
            score = Decimal("0.95")
            is_undervalued = True
        elif peg_ratio < 1.0:
            score = Decimal("0.75")
            is_undervalued = True
        elif peg_ratio < 1.5:
            score = Decimal("0.5")
            is_undervalued = False
        elif peg_ratio < 2.0:
            score = Decimal("0.3")
            is_undervalued = False
        else:
            score = Decimal("0.1")
            is_undervalued = False

        growth_info = (
            f" with {eps_growth:.2f}% growth"
            if eps_growth and eps_growth > 0
            else ""
        )
        reason = f"PEG ratio {peg_ratio:.2f}{growth_info} indicates {'attractive valuation' if is_undervalued else 'elevated valuation'}"

        return CriteriaResult(
            criteria_id=self.criteria_id,
            score=score,
            raw_value=peg_ratio,
            benchmark_value=Decimal("1.0"),  # Fair value PEG
            is_undervalued=is_undervalued,
            reason=reason,
        )
