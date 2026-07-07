"""Unit tests for SHAP Explainability.

Validates: Requirements 6.1, 6.2, 6.4, 14.4
"""

import pytest
import numpy as np
from unittest.mock import MagicMock

from agents.risk_intelligence_agent.shap_explainer import explain, explain_to_text
from agents.risk_intelligence_agent.xgboost_model import XGBoostRiskModel
from agents.risk_intelligence_agent.schemas import SHAPExplanation, FeatureContribution


def test_shap_explanation_ranking_and_impact():
    """Test that SHAP features are ranked by absolute value descending and impact direction matches sign."""
    # We use a mock model to ensure the mock path is taken or shap handles it.
    model = XGBoostRiskModel()  # Without loaded model booster, it uses mock SHAP
    features = np.array([0.9, 0.1, 0.8, 0.2, 0.7, 0.3, 0.6, 0.4])
    
    explanation = explain(model, features)
    
    assert isinstance(explanation, SHAPExplanation)
    assert len(explanation.top_5_features) <= 5
    
    # Verify descending sort order by absolute value
    abs_shap_values = [abs(f.shap_value) for f in explanation.top_5_features]
    for i in range(len(abs_shap_values) - 1):
        assert abs_shap_values[i] >= abs_shap_values[i + 1]
        
    # Verify impact direction matches sign of SHAP value
    for f in explanation.top_5_features:
        if f.shap_value > 0:
            assert f.impact_direction == "positive"
        else:
            assert f.impact_direction == "negative"


def test_shap_values_bounds():
    """Test that all SHAP values correspond to the 8 input features."""
    model = XGBoostRiskModel()
    features = np.array([0.5] * 8)
    explanation = explain(model, features)
    
    assert len(explanation.all_shap_values) == 8


def test_graceful_degradation_on_failure():
    """Test that the SHAP explainer falls back gracefully if computation fails."""
    # Mock model that raises Exception when accessed
    mock_model = MagicMock()
    # Mocking standard behavior to fail during shap tree explainer or fallback
    # But wait, explain() catches all exceptions and falls back to mock shap!
    # So if we raise Exception in model.model booster but also make _compute_mock_shap fail,
    # wait: the code is:
    # try:
    #    import shap
    #    ...
    # except Exception as e:
    #    # SHAP computation failed, use mock values
    #    shap_values_array, base_value = _compute_mock_shap(features)
    #
    # If we pass an invalid numpy array, wait, that raises ValueError.
    # What if shap throws exception but mock shap succeeds? It falls back.
    # What if we verify that explain() returns a valid explanation even when shap isn't installed or model is invalid.
    explanation = explain(mock_model, np.array([0.5] * 8))
    assert isinstance(explanation, SHAPExplanation)
    assert len(explanation.all_shap_values) == 8


def test_explain_to_text_format():
    """Test text explanation formatting works properly."""
    model = XGBoostRiskModel()
    features = np.array([0.5] * 8)
    explanation = explain(model, features)
    
    text = explain_to_text(explanation)
    assert "SHAP Feature Importance Analysis" in text
    assert "Base Value" in text
    assert "Top 5 Contributing Features" in text
