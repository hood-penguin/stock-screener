"""Debt-to-Equity financial health criterion."""

import logging
from decimal import Decimal

from app.core.screening.criteria.base import BaseCriteria, CriteriaResult

logger = logging.getLogger(__name__)


class DebtToEquityCriteria(BaseCriteria):
    """Evaluate financial leverage based on Debt-to-Equity ratio."""

    criteria_id = "financial_health.debt_to_equity"
    category = "financial_health"
    name = "Debt-to-Equity Ratio"
    description = "Leverage ratio showing financial risk. Lower is better."
    default_weight = Decimal("1.0")

    async def evaluate(
        self,
        stock_id: int,
        market: str,
        financial_metric,
        sector_benchmark,
        db_session,
    ) -> CriteriaResult:
        """Evaluate debt-to-equity ratio.

        Lower D/E ratio = safer capital structure.
        """
        debt_to_equity = financial_metric.debt_to_equity
        benchmark_de = (
            sector_benchmark.median_debt_eq if sector_benchmark else None
        )

        # Validate data
        if debt_to_equity is None:
            raise ValueError(f"Stock {stock_id} missing debt_to_equity")

        if benchmark_de is None:
            logger.warning(
                f"No benchmark D/E for stock {stock_id} market {market}"
            )
            benchmark_de = Decimal("1.0")

        # Normalize: compare to sector median
        # Lower than median = safer (0.8)
        # Equal to median = average (0.5)
        # Higher than median = riskier (0.2)

        if benchmark_de <= 0:
            benchmark_de = Decimal("1.0")

        # Inverse ratio: higher D/E is bad
        ratio = debt_to_equity / benchmark_de

        if ratio <= 0.5:
            score = Decimal("0.9")
            is_healthy = True
        elif ratio <= 0.8:
            score = Decimal("0.7")
            is_healthy = True
        elif ratio <= 1.2:
            score = Decimal("0.5")
            is_healthy = False
        elif ratio <= 1.5:
            score = Decimal("0.3")
            is_healthy = False
        else:
            score = Decimal("0.1")
            is_healthy = False

        reason = (
            f"D/E ratio {debt_to_equity:.2f} is "
            f"{('below' if debt_to_equity < benchmark_de else 'above')} "
            f"sector median {benchmark_de:.2f}"
        )

        return CriteriaResult(
            criteria_id=self.criteria_id,
            score=score,
            raw_value=debt_to_equity,
            benchmark_value=benchmark_de,
            is_undervalued=is_healthy,
            reason=reason,
        )
