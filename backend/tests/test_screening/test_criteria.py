import pytest
from app.core.screening.criteria.valuation.pe_ratio import PERatioCriteria
from app.core.screening.criteria.profitability.roe import ROECriteria


class TestPERatioCriteria:
    """PERatioCriteria 단위 테스트"""

    def test_undervalued_case(self):
        """저평가 케이스 테스트"""
        criteria = PERatioCriteria()

        # 종목 PE: 10, 섹터 평균: 20
        metrics = {
            "pe_ratio": 10.0,
        }
        sector_avg = {
            "pe_ratio": 20.0,
        }

        result = criteria.evaluate(metrics, sector_avg)

        assert result is not None
        assert result["score"] > 50  # 저평가이므로 높은 점수
        assert "reason" in result
        assert "PE" in result["reason"]

    def test_overvalued_case(self):
        """고평가 케이스 테스트"""
        criteria = PERatioCriteria()

        # 종목 PE: 40, 섹터 평균: 20
        metrics = {
            "pe_ratio": 40.0,
        }
        sector_avg = {
            "pe_ratio": 20.0,
        }

        result = criteria.evaluate(metrics, sector_avg)

        assert result is not None
        assert result["score"] < 50  # 고평가이므로 낮은 점수
        assert "reason" in result

    def test_missing_data(self):
        """데이터 없는 케이스 테스트"""
        criteria = PERatioCriteria()

        metrics = {
            "pe_ratio": None,
        }
        sector_avg = {
            "pe_ratio": 20.0,
        }

        result = criteria.evaluate(metrics, sector_avg)

        assert result is None  # 데이터 없으면 None 반환


class TestROECriteria:
    """ROECriteria 단위 테스트"""

    def test_high_roe(self):
        """높은 ROE 케이스"""
        criteria = ROECriteria()

        metrics = {
            "roe": 20.0,  # 높은 ROE
        }
        sector_avg = {
            "roe": 10.0,
        }

        result = criteria.evaluate(metrics, sector_avg)

        assert result is not None
        assert result["score"] > 50  # 높은 ROE는 좋은 신호
        assert "reason" in result

    def test_low_roe(self):
        """낮은 ROE 케이스"""
        criteria = ROECriteria()

        metrics = {
            "roe": 3.0,  # 낮은 ROE
        }
        sector_avg = {
            "roe": 10.0,
        }

        result = criteria.evaluate(metrics, sector_avg)

        assert result is not None
        assert result["score"] < 50  # 낮은 ROE는 좋지 않음
        assert "reason" in result

    def test_zero_roe(self):
        """0 ROE 케이스"""
        criteria = ROECriteria()

        metrics = {
            "roe": 0.0,
        }
        sector_avg = {
            "roe": 10.0,
        }

        result = criteria.evaluate(metrics, sector_avg)

        assert result is None  # 0 이하면 None
