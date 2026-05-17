"""API v1 routers."""

from fastapi import APIRouter

from .stocks import router as stocks_router
from .screening import router as screening_router

api_router = APIRouter(prefix="/v1", tags=["v1"])

api_router.include_router(stocks_router)
api_router.include_router(screening_router)

__all__ = ["api_router"]
