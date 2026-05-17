"""Registry system for auto-discovering and managing screening criteria."""

import importlib
import logging
import pkgutil
from pathlib import Path
from typing import Dict, Type

from .criteria.base import BaseCriteria

logger = logging.getLogger(__name__)


class CriteriaRegistry:
    """Auto-discovers and manages all screening criteria plugins."""

    _instance = None
    _criteria_classes: Dict[str, Type[BaseCriteria]] = {}
    _criteria_instances: Dict[str, BaseCriteria] = {}

    def __new__(cls):
        """Implement singleton pattern."""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    @classmethod
    def discover(cls) -> None:
        """Auto-discover all criteria classes from subdirectories.

        Recursively imports all modules in the criteria directory and
        registers any classes that inherit from BaseCriteria.

        This is called once at application startup.
        """
        registry = cls()

        # Get the criteria directory path
        criteria_dir = Path(__file__).parent / "criteria"

        logger.info(f"Discovering criteria in {criteria_dir}")

        # Walk through all subdirectories and modules
        for importer, modname, ispkg in pkgutil.walk_packages(
            path=[str(criteria_dir)],
            prefix="app.core.screening.criteria.",
            onerror=lambda x: logger.warning(f"Error importing {x}"),
        ):
            try:
                module = importlib.import_module(modname)

                # Find all BaseCriteria subclasses in this module
                for item_name in dir(module):
                    item = getattr(module, item_name)

                    # Check if it's a class and subclass of BaseCriteria (but not BaseCriteria itself)
                    if (
                        isinstance(item, type)
                        and issubclass(item, BaseCriteria)
                        and item is not BaseCriteria
                    ):
                        # Instantiate and register the criteria
                        try:
                            instance = item()
                            instance.validate_config()
                            registry.register(instance)
                            logger.info(
                                f"Registered criteria: {instance.criteria_id} "
                                f"from {modname}.{item_name}"
                            )
                        except Exception as e:
                            logger.error(
                                f"Failed to instantiate {item_name} from {modname}: {e}"
                            )

            except Exception as e:
                logger.error(f"Error importing module {modname}: {e}")

        logger.info(
            f"Criteria discovery complete. Registered {len(registry._criteria_instances)} criteria"
        )

    @classmethod
    def register(cls, criteria: BaseCriteria) -> None:
        """Register a criteria instance.

        Args:
            criteria: Instance of a BaseCriteria subclass

        Raises:
            ValueError: If criteria_id is already registered or invalid
        """
        registry = cls()

        if not criteria.criteria_id:
            raise ValueError("Criteria must have a criteria_id")

        if criteria.criteria_id in registry._criteria_instances:
            raise ValueError(
                f"Criteria '{criteria.criteria_id}' is already registered"
            )

        criteria.validate_config()
        registry._criteria_instances[criteria.criteria_id] = criteria
        logger.debug(f"Registered criteria: {criteria.criteria_id}")

    @classmethod
    def get(cls, criteria_id: str) -> BaseCriteria:
        """Get a criteria instance by ID.

        Args:
            criteria_id: The criteria identifier

        Returns:
            The criteria instance

        Raises:
            KeyError: If criteria_id is not registered
        """
        registry = cls()
        if criteria_id not in registry._criteria_instances:
            raise KeyError(f"Criteria '{criteria_id}' not found in registry")
        return registry._criteria_instances[criteria_id]

    @classmethod
    def get_all(cls) -> Dict[str, BaseCriteria]:
        """Get all registered criteria.

        Returns:
            Dictionary mapping criteria_id to criteria instances
        """
        registry = cls()
        return registry._criteria_instances.copy()

    @classmethod
    def get_by_category(cls, category: str) -> Dict[str, BaseCriteria]:
        """Get all criteria in a specific category.

        Args:
            category: The category name (valuation, profitability, growth, financial_health)

        Returns:
            Dictionary mapping criteria_id to criteria instances in that category
        """
        registry = cls()
        return {
            cid: c
            for cid, c in registry._criteria_instances.items()
            if c.category == category
        }

    @classmethod
    def get_by_market(cls, market: str) -> Dict[str, BaseCriteria]:
        """Get all criteria applicable to a specific market.

        Args:
            market: Market code ('US' or 'KR')

        Returns:
            Dictionary mapping criteria_id to criteria instances for that market
        """
        registry = cls()
        return {
            cid: c
            for cid, c in registry._criteria_instances.items()
            if market in c.markets
        }

    @classmethod
    def list_criteria(cls) -> list[str]:
        """Get list of all registered criteria IDs.

        Returns:
            Sorted list of criteria IDs
        """
        registry = cls()
        return sorted(registry._criteria_instances.keys())

    @classmethod
    def count(cls) -> int:
        """Get count of registered criteria.

        Returns:
            Number of registered criteria
        """
        registry = cls()
        return len(registry._criteria_instances)

    @classmethod
    def reset(cls) -> None:
        """Reset the registry (used mainly in testing)."""
        registry = cls()
        registry._criteria_instances.clear()
