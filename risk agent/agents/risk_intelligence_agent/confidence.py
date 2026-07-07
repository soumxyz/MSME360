"""Confidence level calculation for Risk Intelligence Agent.

This module computes confidence in the risk assessment based on data completeness,
model confidence, and feature stability.

**Validates Requirements**: 10.1, 10.2, 10.3, 10.4, 10.5, 10.6
"""

import numpy as np
from typing import List
from .schemas import RiskPrediction, FeatureVector, ConfidenceBreakdown


def compute_confidence(
    data_sources: List[str],
    prediction: RiskPrediction,
    features: FeatureVector
) -> ConfidenceBreakdown:
    """Compute confidence breakdown for risk assessment.
    
    Calculates 3 component scores and combines them into overall confidence:
    - Data Completeness (40%): Percentage of available data sources
    - Model Confidence (40%): Distance from decision boundary (0.5)
    - Feature Stability (20%): Inverse of feature variance
    
    Args:
        data_sources: List of available data source names (e.g., ["GST", "UPI", "AA", "EPFO", "BANK"])
        prediction: Risk prediction from ML model
        features: Feature vector used for prediction
        
    Returns:
        ConfidenceBreakdown with component scores and overall confidence
        
    Data Sources:
        - GST: GST data
        - UPI: UPI transaction data
        - AA: Account Aggregator (bank statements)
        - EPFO: Employee Provident Fund data
        - BANK: Existing loan/bank data
    """
    # ========================================================================
    # Component 1: Data Completeness Score (40%)
    # Formula: (available_sources / total_sources) * 100
    # ========================================================================
    total_sources = 5  # GST, UPI, AA, EPFO, BANK
    available_sources = len(data_sources)
    
    data_completeness_score = (available_sources / total_sources) * 100
    data_completeness_score = np.clip(data_completeness_score, 0, 100)
    
    # ========================================================================
    # Component 2: Model Confidence (40%)
    # Formula: |probability_of_default - 0.5| * 200
    # ========================================================================
    # The further from 0.5 (decision boundary), the more confident the model
    # Distance from 0.5 ranges from 0 to 0.5, multiply by 200 to get [0, 100]
    prob_default = prediction.probability_of_default
    distance_from_boundary = abs(prob_default - 0.5)
    model_confidence = distance_from_boundary * 200
    model_confidence = np.clip(model_confidence, 0, 100)
    
    # ========================================================================
    # Component 3: Feature Stability Score (20%)
    # Measure based on feature availability and consistency
    # ========================================================================
    # Count non-null features
    feature_values = np.array(features.values)
    non_null_features = feature_values[feature_values != -1.0]
    
    if len(non_null_features) > 0:
        # Calculate variance of non-null features
        feature_variance = np.var(non_null_features)
        
        # Lower variance = more stable = higher score
        # Assuming normalized features in [0, 1], variance ranges from 0 to 0.25
        # Convert to stability score: high variance = low stability
        # Use exponential decay: score = 100 * exp(-4 * variance)
        feature_stability_score = 100 * np.exp(-4 * feature_variance)
        feature_stability_score = np.clip(feature_stability_score, 0, 100)
    else:
        # No valid features, very low confidence
        feature_stability_score = 0.0
    
    # ========================================================================
    # Overall Confidence: Weighted Average
    # completeness * 0.40 + model_conf * 0.40 + stability * 0.20
    # ========================================================================
    overall_confidence = (
        data_completeness_score * 0.40 +
        model_confidence * 0.40 +
        feature_stability_score * 0.20
    )
    
    overall_confidence = np.clip(overall_confidence, 0, 100)
    
    # ========================================================================
    # Determine if manual review is required
    # Requirement 10.5: overall_confidence < 60% → requires_manual_review = TRUE
    # ========================================================================
    requires_manual_review = overall_confidence < 60.0
    
    return ConfidenceBreakdown(
        data_completeness_score=float(data_completeness_score),
        model_confidence=float(model_confidence),
        feature_stability_score=float(feature_stability_score),
        overall_confidence=float(overall_confidence),
        requires_manual_review=requires_manual_review
    )


def compute_confidence_simple(
    num_data_sources: int,
    probability_of_default: float,
    num_valid_features: int
) -> float:
    """Simplified confidence calculation for quick estimation.
    
    Args:
        num_data_sources: Number of available data sources (0-5)
        probability_of_default: Probability of default (0-1)
        num_valid_features: Number of non-null features (0-8)
        
    Returns:
        Overall confidence score (0-100)
    """
    # Data completeness
    data_score = (num_data_sources / 5) * 100
    
    # Model confidence
    model_score = abs(probability_of_default - 0.5) * 200
    
    # Feature completeness (simple proxy for stability)
    feature_score = (num_valid_features / 8) * 100
    
    # Weighted average
    confidence = data_score * 0.40 + model_score * 0.40 + feature_score * 0.20
    
    return np.clip(confidence, 0, 100)
