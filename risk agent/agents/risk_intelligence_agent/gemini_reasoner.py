"""Gemini LLM reasoning component for Risk Intelligence Agent.

This module uses Google's Gemini 2.5 Flash to generate human-readable explanations
and recommendations for credit officers based on ML predictions and policy/fraud checks.

**Validates Requirements**: 7.1, 7.2, 7.3, 7.4, 7.5, 7.6, 7.7, 7.8, 14.3
"""

import asyncio
import json
import os
from typing import Optional

from .schemas import (
    RiskPrediction,
    SHAPExplanation,
    PolicyReport,
    FraudReport,
    GeminiReasoning,
    Recommendation
)
from . import prompts
from .shap_explainer import explain_to_text


async def reason(
    prediction: RiskPrediction,
    shap_explanation: SHAPExplanation,
    policy_report: PolicyReport,
    fraud_report: FraudReport,
    timeout: float = 3.0
) -> GeminiReasoning:
    """Generate human-readable explanation using Gemini LLM.
    
    Calls Google Generative AI API with structured JSON prompt and parses response
    into GeminiReasoning model. Falls back to SHAP explanation if Gemini fails.
    
    Args:
        prediction: Risk prediction from ML model
        shap_explanation: SHAP feature importance explanation
        policy_report: Policy rule evaluation results
        fraud_report: Fraud detection results
        timeout: Timeout in seconds (default 3.0)
        
    Returns:
        GeminiReasoning with recommendation, explanation, factors, and alerts
    """
    try:
        # Try to call Gemini API with timeout
        result = await asyncio.wait_for(
            _call_gemini_api(prediction, shap_explanation, policy_report, fraud_report),
            timeout=timeout
        )
        return result
        
    except asyncio.TimeoutError:
        # Timeout - return fallback
        print(f"Warning: Gemini API timed out after {timeout}s, using SHAP fallback")
        return _create_fallback_reasoning(prediction, shap_explanation, policy_report, fraud_report)
        
    except Exception as e:
        # Any other error - return fallback
        print(f"Warning: Gemini API failed: {str(e)}, using SHAP fallback")
        return _create_fallback_reasoning(prediction, shap_explanation, policy_report, fraud_report)


async def _call_gemini_api(
    prediction: RiskPrediction,
    shap_explanation: SHAPExplanation,
    policy_report: PolicyReport,
    fraud_report: FraudReport
) -> GeminiReasoning:
    """Call Google Generative AI API to generate explanation.
    
    Args:
        prediction: Risk prediction
        shap_explanation: SHAP explanation
        policy_report: Policy report
        fraud_report: Fraud report
        
    Returns:
        GeminiReasoning from Gemini API
        
    Raises:
        ImportError: If google-generativeai package not installed
        Exception: If API call fails
    """
    try:
        import google.generativeai as genai
    except ImportError:
        raise ImportError("google-generativeai package not installed. Install with: pip install google-generativeai")
    
    # Get API key from environment
    api_key = os.getenv('GEMINI_API_KEY')
    if not api_key:
        raise ValueError("GEMINI_API_KEY environment variable not set")
    
    # Configure Gemini API
    genai.configure(api_key=api_key)
    
    # Use Gemini 2.5 Flash model
    model = genai.GenerativeModel('gemini-2.0-flash-exp')
    
    # Build prompt from data
    fraud_flags = {
        'gst_bank_mismatch': fraud_report.gst_bank_mismatch,
        'suspicious_revenue_spike': fraud_report.suspicious_revenue_spike,
        'circular_transactions': fraud_report.circular_transactions,
        'duplicate_account': fraud_report.duplicate_account,
        'fake_invoices': fraud_report.fake_invoices,
        'suspicious_upi_behavior': fraud_report.suspicious_upi_behavior
    }
    
    # Convert top features to dict format
    top_features_dict = [
        {
            'feature_name': f.feature_name,
            'feature_value': f.feature_value,
            'shap_value': f.shap_value,
            'impact_direction': f.impact_direction
        }
        for f in shap_explanation.top_5_features
    ]
    
    user_prompt = prompts.build_user_prompt(
        risk_score=prediction.risk_score,
        risk_category=prediction.risk_category.value,
        probability_of_default=prediction.probability_of_default,
        top_features=top_features_dict,
        policy_violations=policy_report.violations,
        fraud_flags=fraud_flags,
        eligibility=policy_report.eligibility
    )
    
    # Call Gemini API
    response = await asyncio.to_thread(
        model.generate_content,
        [prompts.SYSTEM_PROMPT, user_prompt]
    )
    
    # Parse response
    response_text = response.text.strip()
    
    # Try to parse as JSON first
    try:
        response_data = json.loads(response_text)
    except json.JSONDecodeError:
        # Response not JSON, try to extract structured data from text
        response_data = _parse_text_response(response_text)
    
    # Extract fields from response
    recommendation_str = response_data.get('recommendation', 'MANUAL_REVIEW')
    explanation = response_data.get('explanation', response_text)
    positive_factors = response_data.get('positive_factors', [])
    negative_factors = response_data.get('negative_factors', [])
    fraud_alerts = response_data.get('fraud_alerts', [])
    
    # Validate recommendation
    try:
        recommendation = Recommendation(recommendation_str)
    except ValueError:
        recommendation = Recommendation.MANUAL_REVIEW
    
    # Ensure we have exactly 3 positive and negative factors
    if len(positive_factors) < 3:
        positive_factors.extend(['Additional analysis needed'] * (3 - len(positive_factors)))
    positive_factors = positive_factors[:3]
    
    if len(negative_factors) < 3:
        negative_factors.extend(['Additional analysis needed'] * (3 - len(negative_factors)))
    negative_factors = negative_factors[:3]
    
    return GeminiReasoning(
        recommendation=recommendation,
        explanation=explanation,
        positive_factors=positive_factors,
        negative_factors=negative_factors,
        fraud_alerts=fraud_alerts,
        is_fallback=False
    )


def _parse_text_response(text: str) -> dict:
    """Parse semi-structured text response from Gemini.
    
    Attempts to extract recommendation, explanation, and factors from text
    when JSON parsing fails.
    
    Args:
        text: Response text from Gemini
        
    Returns:
        Dictionary with parsed fields
    """
    result = {
        'recommendation': 'MANUAL_REVIEW',
        'explanation': '',
        'positive_factors': [],
        'negative_factors': [],
        'fraud_alerts': []
    }
    
    lines = text.split('\n')
    
    current_section = None
    
    for line in lines:
        line = line.strip()
        
        if not line:
            continue
        
        # Detect sections
        if 'recommendation' in line.lower() and ':' in line:
            rec_text = line.split(':', 1)[1].strip().upper()
            for rec in ['APPROVE', 'REJECT', 'MANUAL_REVIEW', 'APPROVE_WITH_CONDITIONS']:
                if rec in rec_text:
                    result['recommendation'] = rec
                    break
                    
        elif 'explanation' in line.lower() and ':' in line:
            result['explanation'] = line.split(':', 1)[1].strip()
            current_section = 'explanation'
            
        elif 'positive' in line.lower() and 'factor' in line.lower():
            current_section = 'positive'
            
        elif 'negative' in line.lower() and 'factor' in line.lower():
            current_section = 'negative'
            
        elif 'fraud' in line.lower() and 'alert' in line.lower():
            current_section = 'fraud'
            
        elif current_section == 'positive' and (line.startswith('-') or line.startswith('•') or line.startswith('*') or line[0].isdigit()):
            factor = line.lstrip('-•*0123456789. ').strip()
            if factor:
                result['positive_factors'].append(factor)
                
        elif current_section == 'negative' and (line.startswith('-') or line.startswith('•') or line.startswith('*') or line[0].isdigit()):
            factor = line.lstrip('-•*0123456789. ').strip()
            if factor:
                result['negative_factors'].append(factor)
                
        elif current_section == 'fraud' and (line.startswith('-') or line.startswith('•') or line.startswith('*')):
            alert = line.lstrip('-•* ').strip()
            if alert and alert.lower() != 'none':
                result['fraud_alerts'].append(alert)
                
        elif current_section == 'explanation':
            result['explanation'] += ' ' + line
    
    # If explanation is empty, use first substantial paragraph
    if not result['explanation']:
        for line in lines:
            if len(line.strip()) > 50:
                result['explanation'] = line.strip()
                break
    
    return result


def _create_fallback_reasoning(
    prediction: RiskPrediction,
    shap_explanation: SHAPExplanation,
    policy_report: PolicyReport,
    fraud_report: FraudReport
) -> GeminiReasoning:
    """Create fallback reasoning when Gemini API fails.
    
    Uses SHAP explanation text and rule-based logic to generate explanation.
    
    Args:
        prediction: Risk prediction
        shap_explanation: SHAP explanation
        policy_report: Policy report
        fraud_report: Fraud report
        
    Returns:
        GeminiReasoning with is_fallback=True
    """
    # Generate text explanation from SHAP
    shap_text = explain_to_text(shap_explanation)
    
    # Determine recommendation based on rules
    if not policy_report.eligibility:
        recommendation = Recommendation.REJECT
    elif fraud_report.requires_manual_review:
        recommendation = Recommendation.MANUAL_REVIEW
    elif prediction.risk_category.value == 'LOW':
        recommendation = Recommendation.APPROVE
    elif prediction.risk_category.value == 'HIGH':
        recommendation = Recommendation.REJECT
    else:
        recommendation = Recommendation.APPROVE_WITH_CONDITIONS
    
    # Extract positive and negative factors from SHAP
    positive_factors = []
    negative_factors = []
    
    for feature in shap_explanation.top_5_features[:3]:
        if feature.impact_direction == 'positive':
            positive_factors.append(
                f"{feature.feature_name}: {feature.feature_value:.2f} (positive impact)"
            )
        else:
            negative_factors.append(
                f"{feature.feature_name}: {feature.feature_value:.2f} (negative impact)"
            )
    
    # Pad to exactly 3 each
    while len(positive_factors) < 3:
        positive_factors.append("Additional factors require manual review")
    while len(negative_factors) < 3:
        negative_factors.append("Additional factors require manual review")
    
    # Extract fraud alerts
    fraud_alerts = [
        flag.description for flag in fraud_report.flags 
        if flag.status is True
    ]
    
    # Build explanation
    fraud_flags = {
        'gst_bank_mismatch': fraud_report.gst_bank_mismatch,
        'suspicious_revenue_spike': fraud_report.suspicious_revenue_spike,
        'circular_transactions': fraud_report.circular_transactions,
        'duplicate_account': fraud_report.duplicate_account,
        'fake_invoices': fraud_report.fake_invoices,
        'suspicious_upi_behavior': fraud_report.suspicious_upi_behavior
    }
    
    top_features_dict = [
        {
            'feature_name': f.feature_name,
            'feature_value': f.feature_value,
            'shap_value': f.shap_value,
            'impact_direction': f.impact_direction
        }
        for f in shap_explanation.top_5_features
    ]
    
    explanation = prompts.build_fallback_explanation(
        risk_score=prediction.risk_score,
        risk_category=prediction.risk_category.value,
        top_features=top_features_dict,
        policy_violations=policy_report.violations,
        fraud_flags=fraud_flags,
        eligibility=policy_report.eligibility
    )
    
    return GeminiReasoning(
        recommendation=recommendation,
        explanation=explanation,
        positive_factors=positive_factors[:3],
        negative_factors=negative_factors[:3],
        fraud_alerts=fraud_alerts,
        is_fallback=True
    )
