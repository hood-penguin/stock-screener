import pytest
from app.core.screening.engine import ScreeningEngine
from app.core.screening.registry import CriteriaRegistry


class TestCriteriaRegistry:
    """CriteriaRegistry 자동 탐색 테스트"""

    def test_criteria_auto_discovery(self):
        """기준 자동 탐색 테스트"""
        registry = CriteriaRegistry()
        registry.discover()

        assert len(registry.criteria) > 0
        assert "PERatioCriteria" in registry.criteria or \
               any("PE" in name for name in registry.criteria.keys())

    def test_get_criteria(self):
        """기준 조회 테스트"""
        registry = CriteriaRegistry()
        registry.discover()

        # 첫 번째 기준 가져오기
        if registry.criteria:
            first_name = list(registry.criteria.keys())[0]
            criteria = registry.get(first_name)
            assert criteria is not None


class TestScreeningEngine:
    """ScreeningEngine 테스트"""

    def test_engine_initialization(self):
        """엔진 초기화 테스트"""
        engine = ScreeningEngine()
        assert engine is not None
        assert len(engine.registry.criteria) > 0

    def test_run_screening(self):
        """스크리닝 실행 테스트"""
        engine = ScreeningEngine()

        metrics = {
            "pe_ratio": 15.0,
            "pb_ratio": 1.5,
            "roe": 15.0,
            "roa": 8.0,
            "net_margin": 12.0,
            "current_ratio": 1.8,
            "quick_ratio": 1.5,
            "debt_to_equity": 0.6,
            "interest_coverage": 10.0,
        }

        score, criteria_results = engine.run(
            ticker="TEST",
            company_name="Test Company",
            sector="Technology",
            market="US",
            metrics=metrics,
        )

        assert isinstance(score, (int, float))
        assert 0 <= score <= 100
        assert isinstance(criteria_results, dict)
        assert len(criteria_results) > 0

    def test_scoring_results_sorted(self):
        """결과 정렬 테스트"""
        engine = ScreeningEngine()

        # 테스트 케이스 1: 저평가
        metrics_undervalued = {
            "pe_ratio": 8.0,  # 저평가
            "pb_ratio": 1.0,
            "roe": 20.0,  # 높은 수익성
            "roa": 12.0,
            "net_margin": 15.0,
            "current_ratio": 2.0,  # 좋은 유동성
            "quick_ratio": 1.8,
            "debt_to_equity": 0.3,  # 낮은 부채
            "interest_coverage": 15.0,
        }

        # 테스트 케이스 2: 고평가
        metrics_overvalued = {
            "pe_ratio": 50.0,  # 고평가
            "pb_ratio": 5.0,
            "roe": 5.0,  # 낮은 수익성
            "roa": 2.0,
            "net_margin": 3.0,
            "current_ratio": 0.9,  # 낮은 유동성
            "quick_ratio": 0.7,
            "debt_to_equity": 2.0,  # 높은 부채
            "interest_coverage": 2.0,
        }

        score_undervalued, _ = engine.run(
            ticker="UNDER",
            company_name="Undervalued Co",
            sector="Technology",
            market="US",
            metrics=metrics_undervalued,
        )

        score_overvalued, _ = engine.run(
            ticker="OVER",
            company_name="Overvalued Co",
            sector="Technology",
            market="US",
            metrics=metrics_overvalued,
        )

        # 저평가 종목이 더 높은 점수를 받아야 함
        assert score_undervalued > score_overvalued
