"""Prompt templates for Gemini LLM in Risk Intelligence Agent.

This module defines the prompt structure for Gemini 2.5 Flash to generate
human-readable credit assessment explanations for IDBI Bank credit officers.
"""

from typing import Dict, Any, List, Optional


# System context for Gemini LLM
SYSTEM_PROMPT = """You are a senior credit analyst assistant at IDBI Bank. You evaluate MSME loan applications based on alternate data. Be objective, concise, and use financial language appropriate for a credit officer."""


def build_user_prompt(
    risk_score: float,
    risk_category: str,
    probability_of_default: float,
    top_features: List[Dict[str, Any]],
    policy_violations: List[str],
    fraud_flags: Dict[str, Optional[bool]],
    eligibility: bool,
    financial_health_score: Optional[float] = None,
    confidence_level: Optional[float] = None
) -> str:
    """Build structured JSON prompt for Gemini.
    
    Args:
        risk_score: Risk score (0-100, higher is better)
        risk_category: Risk category (LOW, MEDIUM, HIGH)
        probability_of_default: Probability of default (0-1)
        top_features: List of top SHAP features with name, value, shap_value, impact_direction
        policy_violations: List of policy violation descriptions
        fraud_flags: Dictionary of fraud flag names to status (True/False/None)
        eligibility: Loan eligibility status
        financial_health_score: Optional composite financial health score
        confidence_level: Optional overall confidence percentage
        
    Returns:
        JSON-formatted string prompt for Gemini
    """
    # Build fraud flags section - only include TRUE flags
    active_fraud_flags = [
        flag_name for flag_name, status in fraud_flags.items() 
        if status is True
    ]
    
    # Build features section with impact direction
    features_summary = []
    for feature in top_features[:5]:  # Top 5 features
        features_summary.append({
            "feature_name": feature.get("feature_name", "unknown"),
            "feature_value": round(feature.get("feature_value", 0), 2),
            "shap_value": round(feature.get("shap_value", 0), 4),
            "impact": feature.get("impact_direction", "neutral")
        })
    
    # Construct the structured input JSON
    prompt_data = {
        "risk_assessment": {
            "risk_score": round(risk_score, 2),
            "risk_category": risk_category,
            "probability_of_default": round(probability_of_default, 4)
        },
        "top_features": features_summary,
        "policy": {
            "eligibility": eligibility,
            "violations": policy_violations if policy_violations else []
        },
        "fraud": {
            "active_flags": active_fraud_flags,
            "requires_review": len(active_fraud_flags) > 0
        }
    }
    
    # Add optional fields if available
    if financial_health_score is not None:
        prompt_data["financial_health_score"] = round(financial_health_score, 2)
    
    if confidence_level is not None:
        prompt_data["confidence_level"] = round(confidence_level, 2)
    
    # Build the final prompt text
    user_prompt = f"""Analyze the following MSME credit application and provide a recommendation:

INPUT DATA:
{prompt_data}

Provide your assessment in the following structured format:
- Recommendation: One of [APPROVE, APPROVE_WITH_CONDITIONS, REJECT, MANUAL_REVIEW]
- Explanation: A concise paragraph (2-3 sentences) explaining the decision
- Positive Factors: Exactly 3 factors supporting creditworthiness
- Negative Factors: Exactly 3 factors indicating credit risk
- Fraud Alerts: List any fraud concerns (empty if none)

Be specific, reference actual feature values, and justify your recommendation based on the data provided."""
    
    return user_prompt


# Output schema specification for Gemini
OUTPUT_SCHEMA = {
    "type": "object",
    "properties": {
        "recommendation": {
            "type": "string",
            "enum": ["APPROVE", "APPROVE_WITH_CONDITIONS", "REJECT", "MANUAL_REVIEW"],
            "description": "Final credit recommendation"
        },
        "explanation": {
            "type": "string",
            "description": "Concise explanation of the decision (2-3 sentences)"
        },
        "positive_factors": {
            "type": "array",
            "items": {"type": "string"},
            "minItems": 3,
            "maxItems": 3,
            "description": "Exactly 3 factors supporting creditworthiness"
        },
        "negative_factors": {
            "type": "array",
            "items": {"type": "string"},
            "minItems": 3,
            "maxItems": 3,
            "description": "Exactly 3 factors indicating credit risk"
        },
        "fraud_alerts": {
            "type": "array",
            "items": {"type": "string"},
            "description": "List of fraud concerns (empty array if none)"
        }
    },
    "required": ["recommendation", "explanation", "positive_factors", "negative_factors", "fraud_alerts"]
}


# Template for fallback explanation when Gemini fails
FALLBACK_EXPLANATION_TEMPLATE = """Risk Assessment: {risk_category} risk with score {risk_score}/100.

Key Contributing Factors:
{top_features_text}

Policy Status: {eligibility_text}
{policy_violations_text}

{fraud_text}

This assessment is based on ML prediction with SHAP explainability. Manual review recommended due to LLM generation failure."""


def build_fallback_explanation(
    risk_score: float,
    risk_category: str,
    top_features: List[Dict[str, Any]],
    policy_violations: List[str],
    fraud_flags: Dict[str, Optional[bool]],
    eligibility: bool
) -> str:
    """Build a fallback explanation when Gemini fails.
    
    Args:
        risk_score: Risk score (0-100)
        risk_category: Risk category
        top_features: Top SHAP features
        policy_violations: Policy violations
        fraud_flags: Fraud flags
        eligibility: Eligibility status
        
    Returns:
        Fallback explanation text
    """
    # Format top features
    features_lines = []
    for i, feature in enumerate(top_features[:5], 1):
        name = feature.get("feature_name", "unknown")
        value = feature.get("feature_value", 0)
        impact = feature.get("impact_direction", "neutral")
        features_lines.append(f"{i}. {name} = {value:.2f} ({impact} impact)")
    
    top_features_text = "\n".join(features_lines) if features_lines else "No feature data available"
    
    # Format policy violations
    if policy_violations:
        violations_text = "Violations: " + ", ".join(policy_violations)
    else:
        violations_text = "No policy violations"
    
    policy_violations_text = violations_text
    
    # Format fraud flags
    active_fraud = [name for name, status in fraud_flags.items() if status is True]
    if active_fraud:
        fraud_text = f"Fraud Alerts: {', '.join(active_fraud)}"
    else:
        fraud_text = "No fraud alerts"
    
    return FALLBACK_EXPLANATION_TEMPLATE.format(
        risk_category=risk_category,
        risk_score=risk_score,
        top_features_text=top_features_text,
        eligibility_text="Eligible" if eligibility else "Not Eligible",
        policy_violations_text=policy_violations_text,
        fraud_text=fraud_text
    )
