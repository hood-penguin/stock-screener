"""Profitability criteria module."""

from .roe import ROECriteria
from .roa import ROACriteria
from .net_margin import NetMarginCriteria
from .gross_margin import GrossMarginCriteria
from .operating_margin import OperatingMarginCriteria

__all__ = [
    "ROECriteria",
    "ROACriteria",
    "NetMarginCriteria",
    "GrossMarginCriteria",
    "OperatingMarginCriteria",
]
