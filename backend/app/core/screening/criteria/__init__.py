"""Screening criteria module."""

from .base import BaseCriteria, CriteriaResult
from .valuation import (
    PERatioCriteria,
    PBRatioCriteria,
    PSRatioCriteria,
    PEGRatioCriteria,
    EVEBITDACriteria,
    PriceToFCFCriteria,
)
from .profitability import (
    ROECriteria,
    ROACriteria,
    NetMarginCriteria,
    GrossMarginCriteria,
    OperatingMarginCriteria,
)
from .growth import (
    RevenueGrowthCriteria,
    EPSGrowthCriteria,
)
from .financial_health import (
    DebtToEquityCriteria,
    CurrentRatioCriteria,
    QuickRatioCriteria,
    InterestCoverageCriteria,
)

__all__ = [
    "BaseCriteria",
    "CriteriaResult",
    "PERatioCriteria",
    "PBRatioCriteria",
    "PSRatioCriteria",
    "PEGRatioCriteria",
    "EVEBITDACriteria",
    "PriceToFCFCriteria",
    "ROECriteria",
    "ROACriteria",
    "NetMarginCriteria",
    "GrossMarginCriteria",
    "OperatingMarginCriteria",
    "RevenueGrowthCriteria",
    "EPSGrowthCriteria",
    "DebtToEquityCriteria",
    "CurrentRatioCriteria",
    "QuickRatioCriteria",
    "InterestCoverageCriteria",
]
