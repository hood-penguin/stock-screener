"""EV/EBITDA valuation criterion."""

import logging
from decimal import Decimal

from app.core.screening.criteria.base import BaseCriteria, CriteriaResult

logger = logging.getLogger(__name__)


class EVEBITDACriteria(BaseCriteria):
    """Evaluate valuation based on EV/EBITDA multiple."""

    criteria_id = "valuation.ev_ebitda"
    category = "valuation"
    name = "EV/EBITDA Multiple"
    description = "Enterprise Value to EBITDA ratio. Lower is better."
    default_weight = Decimal("1.0")

    async def evaluate(
        self,
        stock_id: int,
        market: str,
        financial_metric,
        sector_benchmark,
        db_session,
    ) -> CriteriaResult:
        """Evaluate EV/EBITDA ratio.

        Lower EV/EBITDA relative to sector = undervalued.
        """
        ev_ebitda = financial_metric.ev_ebitda
        benchmark_ev = (
            sector_benchmark.median_ev_ebitda if sector_benchmark else None
        )

        # Validate data
        if ev_ebitda is None:
            raise ValueError(f"Stock {stock_id} missing ev_ebitda")

        if benchmark_ev is None:
            logger.warning(
                f"No benchmark EV/EBITDA for stock {stock_id} market {market}"
            )
            benchmark_ev = Decimal("12")  # Industry average

        # Normalize
        if benchmark_ev <= 0:
            benchmark_ev = Decimal("12")

        ratio = ev_ebitda / benchmark_ev

        # Lower EV/EBITDA is better
        if ratio <= 0.6:
            score = Decimal("0.9")
            is_undervalued = True
        elif ratio <= 0.85:
            score = Decimal("0.7")
            is_undervalued = True
        elif ratio <= 1.15:
            score = Decimal("0.5")
            is_undervalued = False
        elif ratio <= 1.4:
            score = Decimal("0.3")
            is_undervalued = False
        else:
            score = Decimal("0.1")
            is_undervalued = False

        reason = (
            f"EV/EBITDA {ev_ebitda:.2f}x is "
            f"{('below' if ev_ebitda < benchmark_ev else 'above')} "
            f"sector median {benchmark_ev:.2f}x"
        )

        return CriteriaResult(
            criteria_id=self.criteria_id,
            score=score,
            raw_value=ev_ebitda,
            benchmark_value=benchmark_ev,
            is_undervalued=is_undervalued,
            reason=reason,
        )
