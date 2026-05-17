import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_screener_results_basic(async_client: AsyncClient):
    """스크리너 기본 호출 테스트"""
    response = await async_client.get("/v1/screener/results")

    assert response.status_code == 200
    data = response.json()
    assert "results" in data
    assert "total" in data
    assert "page" in data


@pytest.mark.asyncio
async def test_screener_market_filter_us(async_client: AsyncClient):
    """US 시장 필터 테스트"""
    response = await async_client.get("/v1/screener/results", params={"market": "US"})

    assert response.status_code == 200
    data = response.json()
    assert "results" in data

    # 결과의 모든 항목이 US 시장이어야 함
    for result in data["results"]:
        assert result.get("market") == "US"


@pytest.mark.asyncio
async def test_screener_market_filter_kr(async_client: AsyncClient):
    """KR 시장 필터 테스트"""
    response = await async_client.get("/v1/screener/results", params={"market": "KR"})

    assert response.status_code == 200
    data = response.json()
    assert "results" in data

    # 결과의 모든 항목이 KR 시장이어야 함
    for result in data["results"]:
        assert result.get("market") == "KR"


@pytest.mark.asyncio
async def test_screener_pagination(async_client: AsyncClient):
    """페이지네이션 테스트"""
    # 첫 페이지
    response1 = await async_client.get(
        "/v1/screener/results",
        params={"page": 1, "page_size": 5}
    )
    assert response1.status_code == 200
    data1 = response1.json()
    assert len(data1["results"]) <= 5
    assert data1["page"] == 1

    # 두 번째 페이지 (있으면)
    if data1["total_pages"] > 1:
        response2 = await async_client.get(
            "/v1/screener/results",
            params={"page": 2, "page_size": 5}
        )
        assert response2.status_code == 200
        data2 = response2.json()
        assert data2["page"] == 2


@pytest.mark.asyncio
async def test_screener_min_score_filter(async_client: AsyncClient):
    """최소 점수 필터 테스트"""
    response = await async_client.get(
        "/v1/screener/results",
        params={"min_score": 70}
    )

    assert response.status_code == 200
    data = response.json()
    assert "results" in data

    # 결과의 모든 항목이 최소 점수 이상이어야 함
    for result in data["results"]:
        assert result.get("overall_score", 0) >= 70
