from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Optional, AsyncIterator


@dataclass
class RawStockData:
    """원본 주식 재무 데이터"""
    ticker: str
    market: str  # "US" or "KR"
    company_name: str
    sector: str

    # 가격 정보
    current_price: Optional[float] = None
    pe_ratio: Optional[float] = None
    pb_ratio: Optional[float] = None
    ps_ratio: Optional[float] = None

    # 재무 지표 (매출, 영업이익, 순이익 등)
    revenue: Optional[float] = None
    operating_income: Optional[float] = None
    net_income: Optional[float] = None
    ebitda: Optional[float] = None

    # 재무상태표 (자산, 부채, 자본)
    total_assets: Optional[float] = None
    total_liabilities: Optional[float] = None
    total_equity: Optional[float] = None
    current_assets: Optional[float] = None
    current_liabilities: Optional[float] = None
    cash: Optional[float] = None

    # 주당 지표
    eps: Optional[float] = None
    book_value_per_share: Optional[float] = None


class BaseDataProvider(ABC):
    """데이터 소스 기본 추상 클래스"""

    @abstractmethod
    async def fetch_all_stocks(self) -> AsyncIterator[RawStockData]:
        """모든 종목 데이터 수집"""
        pass

    @abstractmethod
    async def fetch_stock(self, ticker: str) -> Optional[RawStockData]:
        """특정 종목 데이터 수집"""
        pass
