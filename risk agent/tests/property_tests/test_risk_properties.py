"""Property-based tests for XGBoost Model using Hypothesis.

Validates Property 1: Risk Score Bounds and Property 2: Risk Category Consistency
Requirements: 5.2, 5.3, 5.4, 5.5, 5.7
"""

import pytest
import sys
from pathlib import Path
from hypothesis import given, strategies as st, settings, HealthCheck
import numpy as np

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from agents.risk_intelligence_agent.xgboost_model import XGBoostRiskModel
from agents.risk_intelligence_agent.schemas import RiskCategory


@st.composite
def feature_array_strategy(draw):
    """Generate an 8-element feature array of floats in [-1.0, 1.0]."""
    # Features can range from -1.0 (null) to 1.0 (normalized maximum)
    values = [
        draw(st.floats(min_value=-1.0, max_value=1.0, allow_nan=False, allow_infinity=False))
        for _ in range(8)
    ]
    return np.array(values)


@given(features=feature_array_strategy())
@settings(max_examples=100, deadline=None)
def test_property_risk_score_bounds(features):
    """**Validates: Requirements 5.2, 5.7**
    
    Property 1: Risk Score Bounds
    - probability_of_default is in [0, 1]
    - risk_score is in [0, 100]
    - risk_score = (1 - probability_of_default) * 100 holds exactly
    """
    model = XGBoostRiskModel()
    result = model.predict(features)
    
    # 1. Bounds checks
    assert 0.0 <= result.probability_of_default <= 1.0
    assert 0.0 <= result.risk_score <= 100.0
    
    # 2. Formula consistency check (using float tolerance)
    expected_score = (1.0 - result.probability_of_default) * 100.0
    assert pytest.approx(result.risk_score) == expected_score


@given(features=feature_array_strategy())
@settings(max_examples=100, deadline=None)
def test_property_risk_category_consistency(features):
    """**Validates: Requirements 5.3, 5.4, 5.5**
    
    Property 2: Risk Category Consistency
    - LOW risk category iff risk_score > 70
    - HIGH risk category iff risk_score < 40
    - MEDIUM risk category iff 40 <= risk_score <= 70
    """
    model = XGBoostRiskModel()
    result = model.predict(features)
    
    score = result.risk_score
    category = result.risk_category
    
    if score > 70.0:
        assert category == RiskCategory.LOW
    elif score < 40.0:
        assert category == RiskCategory.HIGH
    else:
        assert category == RiskCategory.MEDIUM
