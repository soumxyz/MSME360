"""Unit tests for Gemini Reasoner Component.

Validates: Requirements 7.1, 7.5, 14.3
"""

import pytest
import asyncio
from unittest.mock import patch, MagicMock

from agents.risk_intelligence_agent.gemini_reasoner import reason, _create_fallback_reasoning
from agents.risk_intelligence_agent.schemas import (
    RiskPrediction,
    RiskCategory,
    SHAPExplanation,
    FeatureContribution,
    PolicyReport,
    FraudReport,
    FraudFlag,
    Recommendation,
    GeminiReasoning
)


@pytest.fixture
def mock_inputs():
    """Mock inputs for reasoning tests."""
    prediction = RiskPrediction(
        probability_of_default=0.25,
        risk_score=75.0,
        risk_category=RiskCategory.LOW
    )
    
    top_features = [
        FeatureContribution(
            feature_name="cash_flow_ratio",
            feature_value=0.8,
            shap_value=0.15,
            impact_direction="positive"
        ),
        FeatureContribution(
            feature_name="business_age_months",
            feature_value=36.0,
            shap_value=0.10,
            impact_direction="positive"
        ),
        FeatureContribution(
            feature_name="emi_to_revenue_ratio",
            feature_value=0.2,
            shap_value=-0.05,
            impact_direction="negative"
        )
    ]
    
    shap_explanation = SHAPExplanation(
        base_value=0.5,
        top_5_features=top_features,
        all_shap_values=[0.15, 0.10, -0.05] + [0.0] * 5
    )
    
    policy_report = PolicyReport(
        eligibility=True,
        eligibility_score=100,
        violations=[],
        applied_rules=["POL-001", "POL-003"]
    )
    
    fraud_flags = [
        FraudFlag(flag_name="gst_bank_mismatch", status=False, description="GST-Bank"),
        FraudFlag(flag_name="circular_transactions", status=True, description="Circular transactions detected")
    ]
    
    fraud_report = FraudReport(
        gst_bank_mismatch=False,
        circular_transactions=True,
        requires_manual_review=True,
        flags=fraud_flags
    )
    
    return prediction, shap_explanation, policy_report, fraud_report


def test_fallback_creation(mock_inputs):
    """Test fallback reasoning construction when Gemini API fails/is missing."""
    prediction, shap_explanation, policy_report, fraud_report = mock_inputs
    
    res = _create_fallback_reasoning(prediction, shap_explanation, policy_report, fraud_report)
    
    assert isinstance(res, GeminiReasoning)
    assert res.is_fallback is True
    assert res.recommendation == Recommendation.MANUAL_REVIEW  # Because fraud_report.requires_manual_review is True
    assert len(res.positive_factors) == 3
    assert len(res.negative_factors) == 3
    assert "Circular transactions detected" in res.fraud_alerts


def test_reason_timeout_enforcement(mock_inputs):
    """Test that timeout is enforced and falls back to fallback reasoning."""
    prediction, shap_explanation, policy_report, fraud_report = mock_inputs
    
    async def slow_mock_api(*args, **kwargs):
        await asyncio.sleep(2.0)
        return GeminiReasoning(
            recommendation=Recommendation.APPROVE,
            explanation="Approved",
            positive_factors=["A", "B", "C"],
            negative_factors=["D", "E", "F"]
        )
        
    with patch('agents.risk_intelligence_agent.gemini_reasoner._call_gemini_api', side_effect=slow_mock_api):
        # Setting timeout to 0.1 seconds to trigger TimeoutError
        res = asyncio.run(reason(prediction, shap_explanation, policy_report, fraud_report, timeout=0.1))
        assert res.is_fallback is True
        assert res.recommendation == Recommendation.MANUAL_REVIEW


def test_reason_exception_fallback(mock_inputs):
    """Test that any exceptions during API call trigger fallback reasoning."""
    prediction, shap_explanation, policy_report, fraud_report = mock_inputs
    
    with patch('agents.risk_intelligence_agent.gemini_reasoner._call_gemini_api', side_effect=Exception("API failure")):
        res = asyncio.run(reason(prediction, shap_explanation, policy_report, fraud_report))
        assert res.is_fallback is True
        assert res.recommendation == Recommendation.MANUAL_REVIEW
