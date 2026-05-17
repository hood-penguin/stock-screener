"""Composite scoring engine for stock screening."""

import logging
from decimal import Decimal
from typing import Optional

from .criteria.base import CriteriaResult
from .registry import CriteriaRegistry

logger = logging.getLogger(__name__)


class ScreeningEngine:
    """Evaluates stocks against multiple screening criteria and produces composite scores."""

    def __init__(self):
        """Initialize the screening engine."""
        self.registry = CriteriaRegistry()

    async def evaluate_stock(
        self,
        stock_id: int,
        market: str,
        financial_metric,
        sector_benchmark,
        db_session,
        enabled_criteria: Optional[dict[str, bool]] = None,
        weight_overrides: Optional[dict[str, Decimal]] = None,
    ) -> tuple[Decimal, list[CriteriaResult]]:
        """Evaluate a stock against all applicable criteria.

        Args:
            stock_id: ID of the stock to evaluate
            market: Market code ('US' or 'KR')
            financial_metric: FinancialMetric object with normalized metrics
            sector_benchmark: SectorBenchmark object for comparison
            db_session: AsyncSession for database access
            enabled_criteria: Dict of criteria_id -> bool to control which criteria to use
            weight_overrides: Dict of criteria_id -> Decimal to override default weights

        Returns:
            Tuple of (total_score, list of CriteriaResult objects)

        Raises:
            ValueError: If required financial data is missing
        """
        if enabled_criteria is None:
            enabled_criteria = {}
        if weight_overrides is None:
            weight_overrides = {}

        # Get all criteria applicable to this market
        market_criteria = self.registry.get_by_market(market)

        # Filter by enabled_criteria if specified
        criteria_to_evaluate = {
            cid: c
            for cid, c in market_criteria.items()
            if enabled_criteria.get(cid, True)  # Default to enabled
        }

        if not criteria_to_evaluate:
            logger.warning(f"No criteria available for market {market}")
            return Decimal("0"), []

        # Evaluate each criterion
        results: list[CriteriaResult] = []
        total_weighted_score = Decimal("0")
        total_weight = Decimal("0")

        for criteria_id, criteria in criteria_to_evaluate.items():
            try:
                result = await criteria.evaluate(
                    stock_id=stock_id,
                    market=market,
                    financial_metric=financial_metric,
                    sector_benchmark=sector_benchmark,
                    db_session=db_session,
                )

                # Apply weight override if specified
                weight = weight_overrides.get(criteria_id, criteria.default_weight)
                weight = Decimal(str(weight))  # Ensure Decimal

                # Accumulate weighted score
                total_weighted_score += result.score * weight
                total_weight += weight

                results.append(result)
                logger.debug(f"Evaluated {criteria_id}: score={result.score}")

            except Exception as e:
                logger.error(
                    f"Error evaluating criteria {criteria_id} for stock {stock_id}: {e}",
                    exc_info=True,
                )
                # Continue with other criteria even if one fails

        # Calculate final composite score (normalized by total weight)
        if total_weight > 0:
            total_score = total_weighted_score / total_weight
        else:
            total_score = Decimal("0")

        # Clamp to [0, 1]
        total_score = max(Decimal("0"), min(Decimal("1"), total_score))

        return total_score, results

    def get_undervalued_stocks(
        self,
        results: list[CriteriaResult],
        undervalued_threshold: Decimal = Decimal("0.7"),
    ) -> bool:
        """Determine if stock is undervalued based on criteria results.

        A stock is considered undervalued if:
        1. The majority of criteria indicate undervaluation (>50%)
        2. The composite score exceeds the threshold

        Args:
            results: List of CriteriaResult objects from evaluate_stock
            undervalued_threshold: Score threshold (0-1) for undervaluation

        Returns:
            True if stock is undervalued, False otherwise
        """
        if not results:
            return False

        # Count how many criteria indicate undervaluation
        undervalued_count = sum(
            1 for r in results if r.is_undervalued is True
        )
        total_count = len(results)

        # Simple majority rule: >50% of criteria must indicate undervaluation
        majority_undervalued = undervalued_count > (total_count / 2)

        # If not clear majority, no undervaluation
        if not majority_undervalued:
            return False

        # Additionally, check if average score supports undervaluation
        avg_score = (
            sum(r.score for r in results) / len(results)
            if results
            else Decimal("0")
        )

        return avg_score >= undervalued_threshold

    def get_category_scores(
        self, results: list[CriteriaResult]
    ) -> dict[str, Decimal]:
        """Calculate average score per category.

        Args:
            results: List of CriteriaResult objects

        Returns:
            Dict of category -> average_score
        """
        categories: dict[str, list[Decimal]] = {}

        for result in results:
            criteria = self.registry.get(result.criteria_id)
            category = criteria.category

            if category not in categories:
                categories[category] = []

            categories[category].append(result.score)

        # Calculate averages
        return {
            cat: (sum(scores) / len(scores))
            for cat, scores in categories.items()
        }

    def score_to_percentage(self, score: Decimal) -> Decimal:
        """Convert score (0-1) to percentage (0-100).

        Args:
            score: Score in range [0, 1]

        Returns:
            Percentage (0-100) with 2 decimal places
        """
        percentage = score * Decimal("100")
        return percentage.quantize(Decimal("0.01"))
