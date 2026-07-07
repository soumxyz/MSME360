"""Property-based tests for financial health and confidence scoring.

Validates Property 10: Financial Health Score Additivity and Property 9: Confidence Score Bounds.
Requirements: 9.5, 9.6, 9.7, 10.4, 10.6
"""

import pytest
import sys
from pathlib import Path
from hypothesis import given, strategies as st, settings
import numpy as np

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from agents.risk_intelligence_agent.financial_health import compute_financial_health_score
from agents.risk_intelligence_agent.confidence import compute_confidence
from agents.risk_intelligence_agent.schemas import FeatureVector, RiskPrediction, RiskCategory


@st.composite
def feature_vector_strategy(draw):
    """Generate random FeatureVector where values are either -1.0 (null) or in [0.0, 1.0]."""
    values = []
    for _ in range(8):
        is_null = draw(st.booleans())
        if is_null:
            values.append(-1.0)
        else:
            values.append(draw(st.floats(min_value=0.0, max_value=1.0, allow_nan=False, allow_infinity=False)))
            
    return FeatureVector(
        values=values,
        feature_names=[
            'revenue_growth_percentage',
            'average_monthly_balance',
            'cash_flow_ratio',
            'upi_transaction_frequency',
            'employee_growth_percentage',
            'emi_to_revenue_ratio',
            'business_age_months',
            'digital_payment_ratio'
        ],
        null_flags=[v == -1.0 for v in values]
    )


@st.composite
def risk_prediction_strategy(draw):
    """Generate random RiskPrediction."""
    prob = draw(st.floats(min_value=0.0, max_value=1.0, allow_nan=False, allow_infinity=False))
    score = (1.0 - prob) * 100.0
    
    if score > 70.0:
        cat = RiskCategory.LOW
    elif score < 40.0:
        cat = RiskCategory.HIGH
    else:
        cat = RiskCategory.MEDIUM
        
    return RiskPrediction(
        probability_of_default=prob,
        risk_score=score,
        risk_category=cat
    )


@st.composite
def data_sources_strategy(draw):
    """Generate random subsets of data sources."""
    sources = ["GST", "UPI", "AA", "EPFO", "BANK"]
    return draw(st.lists(st.sampled_from(sources), unique=True))


@given(features=feature_vector_strategy())
@settings(max_examples=100, deadline=None)
def test_property_financial_health_score_additivity(features):
    """**Validates: Requirements 9.5, 9.6, 9.7**
    
    Property 10: Financial Health Score Additivity
    - Verify overall_score = liquidity * 0.30 + growth * 0.25 + digital * 0.20 + debt * 0.25
    - Verify all scores are in [0, 100]
    """
    result = compute_financial_health_score(features)
    
    # Check bounds
    assert 0.0 <= result.liquidity_score <= 100.0
    assert 0.0 <= result.growth_score <= 100.0
    assert 0.0 <= result.digital_adoption_score <= 100.0
    assert 0.0 <= result.debt_management_score <= 100.0
    assert 0.0 <= result.overall_score <= 100.0
    
    # Check weighted sum formula
    expected_overall = (
        result.liquidity_score * 0.30 +
        result.growth_score * 0.25 +
        result.digital_adoption_score * 0.20 +
        result.debt_management_score * 0.25
    )
    
    assert pytest.approx(result.overall_score) == expected_overall


@given(
    data_sources=data_sources_strategy(),
    prediction=risk_prediction_strategy(),
    features=feature_vector_strategy()
)
@settings(max_examples=100, deadline=None)
def test_property_confidence_bounds(data_sources, prediction, features):
    """**Validates: Requirements 10.4, 10.6**
    
    Property 9: Confidence Score Bounds
    - Verify all component scores are in [0, 100]
    - Verify overall_confidence is in [0, 100]
    - Verify weighted formula produces values within bounds
    - Verify manual review flag is set if confidence < 60%
    """
    result = compute_confidence(data_sources, prediction, features)
    
    # Check bounds
    assert 0.0 <= result.data_completeness_score <= 100.0
    assert 0.0 <= result.model_confidence <= 100.0
    assert 0.0 <= result.feature_stability_score <= 100.0
    assert 0.0 <= result.overall_confidence <= 100.0
    
    # Check weighted formula
    expected_confidence = (
        result.data_completeness_score * 0.40 +
        result.model_confidence * 0.40 +
        result.feature_stability_score * 0.20
    )
    
    assert pytest.approx(result.overall_confidence) == expected_confidence
    
    # Verify manual review flag implication (Requirement 10.5)
    if result.overall_confidence < 60.0:
        assert result.requires_manual_review is True
    else:
        assert result.requires_manual_review is False
