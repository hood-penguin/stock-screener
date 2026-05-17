import asyncio
import logging
from typing import Optional, AsyncIterator
import yfinance as yf

from .base import BaseDataProvider, RawStockData

logger = logging.getLogger(__name__)

SP500_TICKERS = [
    "AAPL", "MSFT", "GOOGL", "AMZN", "NVDA",
    "META", "BRK-B", "LLY", "AVGO", "JPM",
    "UNH", "XOM", "TSLA", "PG", "MA",
    "JNJ", "COST", "HD", "MRK", "ABBV",
    "CVX", "BAC", "KO", "PEP", "WMT"
]


class YahooFinanceProvider(BaseDataProvider):
    """Yahoo Finance를 통한 S&P 500 데이터 수집"""

    def __init__(self):
        self.loop = asyncio.get_event_loop()

    async def fetch_all_stocks(self) -> AsyncIterator[RawStockData]:
        """S&P 500 주요 종목 데이터 수집"""
        for ticker in SP500_TICKERS:
            data = await self.fetch_stock(ticker)
            if data:
                yield data

    async def fetch_stock(self, ticker: str) -> Optional[RawStockData]:
        """yfinance를 이용한 단일 종목 데이터 수집"""
        try:
            # sync 함수를 executor에서 실행
            ticker_obj = await self.loop.run_in_executor(
                None, lambda: yf.Ticker(ticker)
            )
            info = await self.loop.run_in_executor(None, lambda: ticker_obj.info)

            if not info:
                logger.warning(f"No data for {ticker}")
                return None

            # 재무 데이터 추출
            financials = await self.loop.run_in_executor(
                None, lambda: ticker_obj.financials
            )
            balance_sheet = await self.loop.run_in_executor(
                None, lambda: ticker_obj.balance_sheet
            )

            # 최신 데이터 추출 (첫 번째 열)
            revenue = None
            net_income = None
            operating_income = None
            ebitda = None

            if financials is not None and not financials.empty:
                revenue = float(financials.loc["Total Revenue"].iloc[0]) \
                    if "Total Revenue" in financials.index else None
                net_income = float(financials.loc["Net Income"].iloc[0]) \
                    if "Net Income" in financials.index else None
                operating_income = float(financials.loc["Operating Income"].iloc[0]) \
                    if "Operating Income" in financials.index else None
                ebitda = float(financials.loc["EBITDA"].iloc[0]) \
                    if "EBITDA" in financials.index else None

            total_assets = None
            total_liabilities = None
            total_equity = None
            current_assets = None
            current_liabilities = None
            cash = None

            if balance_sheet is not None and not balance_sheet.empty:
                total_assets = float(balance_sheet.loc["Total Assets"].iloc[0]) \
                    if "Total Assets" in balance_sheet.index else None
                total_liabilities = float(balance_sheet.loc["Total Liab"].iloc[0]) \
                    if "Total Liab" in balance_sheet.index else None
                total_equity = float(balance_sheet.loc["Total Stockholder Equity"].iloc[0]) \
                    if "Total Stockholder Equity" in balance_sheet.index else None
                current_assets = float(balance_sheet.loc["Current Assets"].iloc[0]) \
                    if "Current Assets" in balance_sheet.index else None
                current_liabilities = float(balance_sheet.loc["Current Liabilities"].iloc[0]) \
                    if "Current Liabilities" in balance_sheet.index else None
                cash = float(balance_sheet.loc["Cash"].iloc[0]) \
                    if "Cash" in balance_sheet.index else None

            return RawStockData(
                ticker=ticker,
                market="US",
                company_name=info.get("longName", ticker),
                sector=info.get("sector", "Unknown"),
                current_price=float(info.get("currentPrice", 0)) \
                    if info.get("currentPrice") else None,
                pe_ratio=float(info.get("trailingPE", 0)) \
                    if info.get("trailingPE") else None,
                pb_ratio=float(info.get("priceToBook", 0)) \
                    if info.get("priceToBook") else None,
                ps_ratio=float(info.get("priceToSalesTrailing12Months", 0)) \
                    if info.get("priceToSalesTrailing12Months") else None,
                revenue=revenue,
                operating_income=operating_income,
                net_income=net_income,
                ebitda=ebitda,
                total_assets=total_assets,
                total_liabilities=total_liabilities,
                total_equity=total_equity,
                current_assets=current_assets,
                current_liabilities=current_liabilities,
                cash=cash,
                eps=float(info.get("trailingEps", 0)) \
                    if info.get("trailingEps") else None,
                book_value_per_share=float(info.get("bookValue", 0)) \
                    if info.get("bookValue") else None,
            )

        except Exception as e:
            logger.error(f"Error fetching data for {ticker}: {str(e)}")
            return None
