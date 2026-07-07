"""Financial health composite scoring for Risk Intelligence Agent.

This module computes a multi-dimensional financial health score based on
liquidity, growth, digital adoption, and debt management.

**Validates Requirements**: 9.1, 9.2, 9.3, 9.4, 9.5, 9.6, 9.7
"""

import numpy as np
from .schemas import FeatureVector, FinancialHealthScore


def compute_financial_health_score(features: FeatureVector) -> FinancialHealthScore:
    """Compute composite financial health score from feature vector.
    
    Calculates 4 component scores and combines them into overall score:
    - Liquidity (30%): Cash reserves and cash flow health
    - Growth (25%): Revenue and employee growth trends
    - Digital Adoption (20%): Digital payment usage
    - Debt Management (25%): EMI burden and debt serviceability
    
    Args:
        features: 8-element feature vector with normalized values
        
    Returns:
        FinancialHealthScore with component scores and overall score
        
    Feature Vector Index Mapping:
        0: revenue_growth_percentage
        1: average_monthly_balance
        2: cash_flow_ratio
        3: upi_transaction_frequency
        4: employee_growth_percentage
        5: emi_to_revenue_ratio
        6: business_age_months
        7: digital_payment_ratio
    """
    # Extract feature values (remember: -1 means NULL)
    revenue_growth = features.values[0]
    avg_monthly_balance = features.values[1]
    cash_flow_ratio = features.values[2]
    upi_transaction_freq = features.values[3]
    employee_growth = features.values[4]
    emi_to_revenue = features.values[5]
    business_age = features.values[6]
    digital_payment_ratio = features.values[7]
    
    # ========================================================================
    # Component 1: Liquidity Score (30%)
    # Measures: average_monthly_balance + cash_flow_ratio
    # ========================================================================
    liquidity_components = []
    
    if avg_monthly_balance != -1.0:
        # Higher balance = better liquidity
        # Normalized value already in [0, 1], scale to [0, 100]
        liquidity_components.append(avg_monthly_balance * 100)
    
    if cash_flow_ratio != -1.0:
        # Positive cash flow = good, normalize to [0, 100]
        # Cash flow ratio can be negative, so we need to scale appropriately
        # Assuming normalized value is in [-1, 1] after normalization
        cash_flow_score = ((cash_flow_ratio + 1) / 2) * 100
        liquidity_components.append(np.clip(cash_flow_score, 0, 100))
    
    if liquidity_components:
        liquidity_score = np.mean(liquidity_components)
    else:
        # No data available, use neutral score
        liquidity_score = 50.0
    
    # ========================================================================
    # Component 2: Growth Score (25%)
    # Measures: revenue_growth_percentage + employee_growth_percentage
    # ========================================================================
    growth_components = []
    
    if revenue_growth != -1.0:
        # Normalized growth, convert to [0, 100]
        growth_components.append(revenue_growth * 100)
    
    if employee_growth != -1.0:
        # Normalized employee growth
        growth_components.append(employee_growth * 100)
    
    if growth_components:
        growth_score = np.mean(growth_components)
    else:
        growth_score = 50.0
    
    # ========================================================================
    # Component 3: Digital Adoption Score (20%)
    # Measures: digital_payment_ratio + upi_transaction_frequency
    # ========================================================================
    digital_components = []
    
    if digital_payment_ratio != -1.0:
        digital_components.append(digital_payment_ratio * 100)
    
    if upi_transaction_freq != -1.0:
        digital_components.append(upi_transaction_freq * 100)
    
    if digital_components:
        digital_adoption_score = np.mean(digital_components)
    else:
        digital_adoption_score = 50.0
    
    # ========================================================================
    # Component 4: Debt Management Score (25%)
    # Measures: emi_to_revenue_ratio (inverse - lower is better)
    # ========================================================================
    if emi_to_revenue != -1.0:
        # Lower EMI ratio is better, so we invert it
        # Normalized value in [0, 1], where high value = high EMI burden
        # Score: 100 - (normalized_value * 100) gives higher score for lower EMI
        debt_management_score = 100 - (emi_to_revenue * 100)
        debt_management_score = np.clip(debt_management_score, 0, 100)
    else:
        debt_management_score = 50.0
    
    # ========================================================================
    # Overall Score: Weighted Average
    # liquidity * 0.30 + growth * 0.25 + digital * 0.20 + debt * 0.25
    # ========================================================================
    overall_score = (
        liquidity_score * 0.30 +
        growth_score * 0.25 +
        digital_adoption_score * 0.20 +
        debt_management_score * 0.25
    )
    
    # Ensure all scores are in [0, 100] range
    liquidity_score = np.clip(liquidity_score, 0, 100)
    growth_score = np.clip(growth_score, 0, 100)
    digital_adoption_score = np.clip(digital_adoption_score, 0, 100)
    debt_management_score = np.clip(debt_management_score, 0, 100)
    overall_score = np.clip(overall_score, 0, 100)
    
    return FinancialHealthScore(
        liquidity_score=float(liquidity_score),
        growth_score=float(growth_score),
        digital_adoption_score=float(digital_adoption_score),
        debt_management_score=float(debt_management_score),
        overall_score=float(overall_score)
    )
