"""ROE (Return on Equity) profitability criterion."""

import logging
from decimal import Decimal

from app.core.screening.criteria.base import BaseCriteria, CriteriaResult

logger = logging.getLogger(__name__)


class ROECriteria(BaseCriteria):
    """Evaluate stock quality based on Return on Equity."""

    criteria_id = "profitability.roe"
    category = "profitability"
    name = "Return on Equity (ROE)"
    description = "How efficiently the company uses shareholder capital. Higher is better."
    default_weight = Decimal("1.0")

    async def evaluate(
        self,
        stock_id: int,
        market: str,
        financial_metric,
        sector_benchmark,
        db_session,
    ) -> CriteriaResult:
        """Evaluate ROE.

        Higher ROE relative to sector = better quality investment.
        """
        roe = financial_metric.roe
        benchmark_roe = sector_benchmark.median_roe if sector_benchmark else None

        # Validate data
        if roe is None:
            raise ValueError(f"Stock {stock_id} missing roe")

        if benchmark_roe is None:
            logger.warning(
                f"No benchmark ROE for stock {stock_id} market {market}"
            )
            benchmark_roe = Decimal("15")  # Reasonable default

        # Normalize: stock ROE compared to sector median
        # Much higher than median = good (0.9)
        # Equal to median = neutral (0.5)
        # Much lower than median = bad (0.1)

        if benchmark_roe <= 0:
            benchmark_roe = Decimal("15")

        ratio = roe / benchmark_roe

        if ratio >= 1.5:
            score = Decimal("0.9")
            is_healthy = True
        elif ratio >= 1.2:
            score = Decimal("0.7")
            is_healthy = True
        elif ratio >= 0.8:
            score = Decimal("0.5")
            is_healthy = False
        elif ratio >= 0.5:
            score = Decimal("0.3")
            is_healthy = False
        else:
            score = Decimal("0.1")
            is_healthy = False

        reason = (
            f"ROE {roe:.2f}% is "
            f"{('above' if roe > benchmark_roe else 'below')} "
            f"sector median {benchmark_roe:.2f}%"
        )

        return CriteriaResult(
            criteria_id=self.criteria_id,
            score=score,
            raw_value=roe,
            benchmark_value=benchmark_roe,
            is_undervalued=is_healthy,
            reason=reason,
        )
